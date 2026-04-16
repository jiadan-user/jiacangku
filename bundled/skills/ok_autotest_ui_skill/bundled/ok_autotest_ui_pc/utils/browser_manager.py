# utils/browser_manager.py
import os
import sys
import asyncio
import atexit
import weakref
import threading

from utils.logger import setup_logger

logger = setup_logger()

# ══════════════════════════════════════════════════════════════════════════════
# 【正确修复】全局单例 Playwright 实例
# 
# 根据 Playwright 官方文档 (https://github.com/microsoft/playwright-python/issues/1391):
# "Avoid manually calling start, and only use one Python context at a time"
# 
# 问题：每个 BrowserManager 都调用 sync_playwright().start() 会导致第二次调用失败
# 解决：全局只创建一个 sync_playwright() 实例，所有 BrowserManager 共享这个实例
# ══════════════════════════════════════════════════════════════════════════════

_global_playwright_instance = None
_global_playwright_lock = threading.RLock()

def _get_or_create_playwright():
    """
    获取或创建全局单例 Playwright 实例
    
    这是正确的做法：
    1. 全局只创建一个 sync_playwright() 实例
    2. 在这个实例上可以创建多个浏览器
    3. 避免 "Playwright Sync API inside the asyncio loop" 错误
    
    Returns:
        playwright 实例
    """
    global _global_playwright_instance
    
    with _global_playwright_lock:
        if _global_playwright_instance is None:
            logger.info("[PLAYWRIGHT] 创建全局 Playwright 实例（首次）")
            from playwright.sync_api import sync_playwright
            _global_playwright_instance = sync_playwright().start()
            logger.info("[PLAYWRIGHT] ✅ 全局 Playwright 实例创建成功")
        else:
            logger.debug("[PLAYWRIGHT] 复用现有的全局 Playwright 实例")
        
        return _global_playwright_instance

def _cleanup_global_playwright():
    """
    清理全局 Playwright 实例
    
    注意：只在所有 BrowserManager 实例都清理完毕后调用
    """
    global _global_playwright_instance
    
    with _global_playwright_lock:
        if _global_playwright_instance is not None:
            try:
                logger.info("[PLAYWRIGHT] 清理全局 Playwright 实例")
                _global_playwright_instance.stop()
                _global_playwright_instance = None
                logger.info("[PLAYWRIGHT] ✅ 全局 Playwright 实例已清理")
            except Exception as e:
                logger.error(f"[PLAYWRIGHT] ❌ 清理全局 Playwright 实例失败: {e}")
                _global_playwright_instance = None

# ══════════════════════════════════════════════════════════════════════════════
# 【全局 Playwright 实例追踪器】
#
# 问题：当 pytest fixture 在 yield 之前失败时，Playwright 实例不会被清理，
#       导致其内部 asyncio 循环残留，影响后续测试。
#
# 解决方案：
# 1. 使用全局列表追踪所有创建的 BrowserManager 实例
# 2. 注册 atexit 处理器，在进程退出时清理所有实例
# 3. 提供 cleanup_all_instances() 函数供 pytest hook 调用
# ══════════════════════════════════════════════════════════════════════════════

# 全局追踪所有 BrowserManager 实例（使用弱引用避免内存泄漏）
_active_instances = []


def _register_instance(instance):
    """注册一个 BrowserManager 实例到全局追踪列表"""
    _active_instances.append(weakref.ref(instance))


def _unregister_instance(instance):
    """从全局追踪列表中移除一个实例"""
    _active_instances[:] = [ref for ref in _active_instances if ref() is not None and ref() is not instance]


def cleanup_all_playwright_instances(force=False):
    """
    清理未关闭的 Playwright 实例
    
    这个函数会被以下场景调用：
    1. atexit 处理器（进程退出时，force=True）
    2. pytest 的 pytest_runtest_teardown hook（每个测试后，force=False）
    3. pytest 的 pytest_sessionfinish hook（测试会话结束时，force=True）
    
    Args:
        force: 如果为 True，强制清理所有实例（用于 session 结束时）
               如果为 False，只清理 in_use=False 的实例（保护 module 级 fixture）
    
    Returns:
        tuple: (cleaned_count, remaining_count)
    """
    global _active_instances
    cleaned = 0
    remaining = []
    
    for ref in _active_instances[:]:  # 使用切片复制避免迭代时修改
        instance = ref()
        # 【P1 修复】先检查 None，避免在检查后对象被垃圾回收
        if instance is None:
            continue  # 跳过已被回收的实例
        
        # 只清理非使用中的实例，除非 force=True
        if force or not instance.in_use:
            try:
                # 【正确修复】只清理 browser 和 context，不清理 playwright 实例
                # playwright 实例是全局单例，由 _cleanup_global_playwright() 统一清理
                if instance.browser or instance.context:
                    try:
                        if instance.context:
                            instance.context.close()
                        if instance.browser:
                            instance.browser.close()
                        cleaned += 1
                    except (RuntimeError, OSError) as e:
                        # 【P1 修复】只捕获特定异常，记录日志
                        logger.warning(f"[CLEANUP] 清理 Browser/Context 时出错: {e}")
                    finally:
                        instance.browser = None
                        instance.context = None
                        # 注意：不清理 instance.playwright，它指向全局单例
            except Exception as e:
                # 【P1 修复】记录未预期的异常
                logger.error(f"[CLEANUP] 清理实例时发生未预期错误: {e}")
        else:
            # 保留使用中的实例
            remaining.append(ref)
    
    # 更新列表：保留使用中的实例
    _active_instances[:] = remaining
    
    if cleaned > 0:
        logger.debug(f"[CLEANUP] 清理了 {cleaned} 个实例，保留 {len(remaining)} 个使用中的实例")
    
    return cleaned, len(remaining)


# 【P1 修复】独立的 asyncio 清理函数（分离职责）
def cleanup_asyncio_if_needed():
    """
    在没有活跃 Playwright 实例时清理全局 Playwright 实例
    
    这个函数应该在 cleanup_all_playwright_instances() 之后调用，
    确保只有在所有 BrowserManager 实例都被清理后才清理全局 Playwright 实例。
    """
    if not _active_instances:
        _cleanup_global_playwright()


# 注册 atexit 处理器（进程退出时强制清理所有实例）
def _atexit_cleanup():
    """进程退出时的清理处理器"""
    cleanup_all_playwright_instances(force=True)
    cleanup_asyncio_if_needed()

atexit.register(_atexit_cleanup)


# ══════════════════════════════════════════════════════════════════════════════
# 【已废弃】不再需要 asyncio 清理逻辑
#
# 原因：使用全局单例 Playwright 实例后，不会再出现多次调用 sync_playwright().start()
# 导致的 asyncio 循环冲突问题。
# ══════════════════════════════════════════════════════════════════════════════

# ── 自动修正 Playwright 浏览器路径 ──────────────────────────────────────────
_BROWSER_PREFIXES = ('chromium', 'firefox', 'webkit')

def _path_has_browsers(path: str) -> bool:
    """判断目录内是否有真实的浏览器可执行目录。"""
    if not os.path.isdir(path):
        return False
    return any(
        entry.startswith(_BROWSER_PREFIXES)
        for entry in os.listdir(path)
        if not entry.startswith('.')
    )

def _fix_playwright_browser_path():
    """修正 Playwright 浏览器路径"""
    env_path = os.environ.get('PLAYWRIGHT_BROWSERS_PATH', '')
    if env_path and not _path_has_browsers(env_path):
        # Linux 服务器路径
        linux_path = os.path.expanduser('~/.cache/ms-playwright')
        # macOS 路径
        mac_path = os.path.expanduser('~/Library/Caches/ms-playwright')
        
        for real_path in [linux_path, mac_path]:
            if _path_has_browsers(real_path):
                os.environ['PLAYWRIGHT_BROWSERS_PATH'] = real_path
                break
# ────────────────────────────────────────────────────────────────────────────


class BrowserManager:
    """浏览器管理器（静默执行）"""
    
    def __init__(self, use_global_instance=True):
        """
        初始化 BrowserManager
        
        Args:
            use_global_instance: 是否使用全局单例 Playwright 实例
                                True: 使用全局单例（默认，用于主线程）
                                False: 创建独立实例（用于子线程，符合官方文档要求）
        """
        self.playwright = None
        self.browser = None
        self.context = None
        self._in_use = False  # 标记是否在 fixture 生命周期内（用于保护 module 级 fixture）
        self.use_global_instance = use_global_instance  # 是否使用全局单例
        # 注册到全局追踪列表
        _register_instance(self)
    
    def mark_in_use(self):
        """标记为使用中（fixture yield 前调用）
        
        当 BrowserManager 被标记为 in_use 时，cleanup_all_playwright_instances(force=False)
        不会清理该实例，从而保护 module 级 fixture 在整个模块测试期间保持活跃。
        """
        self._in_use = True
    
    def mark_released(self):
        """标记为已释放（fixture yield 后调用）
        
        当 fixture 的生命周期结束时调用此方法，允许后续的清理操作清理该实例。
        """
        self._in_use = False
    
    @property
    def in_use(self):
        """返回是否在使用中"""
        return self._in_use
    
    def start_browser(
        self,
        browser_type='chromium',
        headless=False,
        base_url=None,
        viewport=None,
        geolocation=None,
        permissions=None,
        storage_state=None,
    ):
        """
        启动浏览器并创建页面（静默执行）
        
        Args:
            browser_type: 浏览器类型 (chromium/firefox/webkit)
            headless: 是否无头模式
            base_url: 基础 URL
            viewport: 视口大小 {"width": 1920, "height": 1080}
            geolocation: 地理位置 {"latitude": -33.8688, "longitude": 151.2093}，
                         None 则使用默认纽约坐标
            permissions: 权限列表 ["geolocation", "notifications"]，
                         None 则默认只授予 ["notifications"]
            storage_state: Storage state文件路径（用于恢复登录状态）

        Returns:
            Page: Playwright 页面对象
        """
        # 直接调用核心逻辑
        return self._start_browser_core(
            browser_type=browser_type,
            headless=headless,
            base_url=base_url,
            viewport=viewport,
            geolocation=geolocation,
            permissions=permissions,
            storage_state=storage_state,
        )

    def _start_browser_core(
        self,
        browser_type='chromium',
        headless=False,
        base_url=None,
        viewport=None,
        geolocation=None,
        permissions=None,
        storage_state=None,
    ):
        """实际启动浏览器的核心逻辑（在当前线程中调用）"""
        try:
            # 修正浏览器路径
            _fix_playwright_browser_path()

            # 【关键修复】根据 use_global_instance 决定使用全局单例还是独立实例
            # 根据 Playwright 官方文档：
            # - 主线程：使用全局单例（避免 asyncio 循环冲突）
            # - 子线程：必须创建独立实例（Playwright 不是线程安全的）
            if self.use_global_instance:
                self.playwright = _get_or_create_playwright()
                logger.debug("[PLAYWRIGHT] 使用全局单例实例")
            else:
                from playwright.sync_api import sync_playwright
                self.playwright = sync_playwright().start()
                logger.info("[PLAYWRIGHT] 创建独立 Playwright 实例（子线程模式）")
            
            # 启动浏览器
            browser_launcher = getattr(self.playwright, browser_type)
            
            # 【关键修复】强制在 CI/沙箱环境中使用无头模式
            # 检查环境变量：HEADLESS=true 或 CI=1
            env_headless = os.environ.get("HEADLESS", "").lower() in ("true", "1", "yes")
            env_ci = os.environ.get("CI", "").lower() in ("true", "1", "yes")
            
            # 如果环境变量指定了无头模式，强制覆盖参数
            if env_headless or env_ci:
                headless = True
                logger.info(f"[ENV] 检测到环境变量 HEADLESS={env_headless} 或 CI={env_ci}，强制使用无头模式")
            
            # 添加启动参数以减少被检测
            launch_options = {
                'headless': headless,
                'timeout': int(os.environ.get("PLAYWRIGHT_BROWSER_LAUNCH_TIMEOUT_MS", "300000")),
                'args': [
                    '--disable-blink-features=AutomationControlled',  # 禁用自动化控制标志
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                ]
            }

            # 调试增强（仅在设置环境变量时生效）
            # - SLOW_MO_MS=500: 每个 Playwright 操作额外延迟 500ms
            # - DEVTOOLS=1: Chromium 打开 DevTools（可辅助排查选择器/请求）
            slow_mo_raw = os.environ.get("SLOW_MO_MS", "").strip()
            if slow_mo_raw:
                try:
                    slow_mo_ms = int(slow_mo_raw)
                    if slow_mo_ms > 0:
                        launch_options["slow_mo"] = slow_mo_ms
                except ValueError:
                    pass

            if os.environ.get("DEVTOOLS", "").lower() in ("1", "true", "yes") and browser_type == "chromium":
                launch_options["devtools"] = True
            
            self.browser = browser_launcher.launch(**launch_options)
            
            # 创建浏览器上下文（不设置 viewport 以便后续最大化）
            context_options = {}
            
            # 如果不是无头模式，不设置 viewport（让浏览器自适应）
            if not headless:
                context_options['viewport'] = None  # 自适应，允许后续最大化
                context_options['no_viewport'] = True  # 不限制视口
            else:
                # 无头模式设置大尺寸视口
                if viewport:
                    context_options['viewport'] = viewport
                else:
                    context_options['viewport'] = {'width': 1920, 'height': 1080}
            
            if base_url:
                context_options['base_url'] = base_url
            
            # 添加反检测措施，使浏览器更像真实用户
            # 设置真实的 User-Agent
            context_options['user_agent'] = (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # 设置语言和时区
            context_options['locale'] = 'en-US'
            context_options['timezone_id'] = 'America/New_York'
            
            # 设置权限（允许通知等，更像真实浏览器）
            # 若调用方传入 permissions，优先使用；否则默认仅授予 notifications
            context_options['permissions'] = permissions if permissions is not None else ['notifications']

            # 设置地理位置
            # 若调用方传入 geolocation，使用调用方坐标；否则默认纽约（反检测）
            context_options['geolocation'] = (
                geolocation if geolocation is not None
                else {'longitude': -74.006, 'latitude': 40.7128}  # New York default
            )
            
            # 设置storage state（如果提供）
            if storage_state:
                context_options['storage_state'] = storage_state
                logger.info(f"[AUTH] 使用storage state: {storage_state}")
            
            self.context = self.browser.new_context(**context_options)
            
            # 添加额外的反检测脚本
            self.context.add_init_script("""
                // 移除 webdriver 标志
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // 覆盖 plugins 属性
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // 覆盖 languages 属性
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                
                // 覆盖 chrome 对象
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                };
                
                // 覆盖 permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // 覆盖 getBattery
                if (navigator.getBattery) {
                    navigator.getBattery = undefined;
                }
                
                // 覆盖 connection
                Object.defineProperty(navigator, 'connection', {
                    get: () => ({
                        effectiveType: '4g',
                        rtt: 50,
                        downlink: 10,
                        saveData: false
                    })
                });
                
                // 覆盖 hardwareConcurrency
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8
                });
                
                // 覆盖 deviceMemory
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => 8
                });
                
                // 覆盖 platform
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'MacIntel'
                });
                
                // 移除自动化相关属性
                delete navigator.__proto__.webdriver;
                
                // 覆盖 toString 方法
                const originalToString = Function.prototype.toString;
                Function.prototype.toString = function() {
                    if (this === navigator.getBattery || 
                        this === navigator.permissions.query) {
                        return 'function () { [native code] }';
                    }
                    return originalToString.apply(this, arguments);
                };
            """)
            
            # 创建新页面
            page = self.context.new_page()
            
            # 非无头模式下，页面创建后立即最大化窗口
            if not headless:
                try:
                    # 使用 CDP 协议设置窗口为最大化
                    session = self.context.new_cdp_session(page)
                    session.send('Browser.setWindowBounds', {
                        'windowId': 1,
                        'bounds': {'windowState': 'maximized'}
                    })
                except Exception:
                    # 如果 CDP 失败，尝试 JavaScript 方式
                    try:
                        page.evaluate("""() => {
                            window.moveTo(0, 0);
                            window.resizeTo(screen.availWidth, screen.availHeight);
                        }""")
                    except Exception:
                        pass  # 静默失败，不影响测试
            
            # 设置默认超时
            page.set_default_timeout(30000)
            page.set_default_navigation_timeout(30000)
            
            return page
            
        except Exception as e:
            logger.error(f"浏览器启动失败: {e}")
            # 【关键】确保在失败时清理已创建的资源，避免 asyncio 循环残留
            self._cleanup_on_failure()
            raise
    
    def _cleanup_on_failure(self):
        """
        在启动失败时清理已创建的资源
        
        这个方法确保即使 start_browser() 中途失败，
        也能正确清理 Playwright 资源，避免 asyncio 循环残留。
        """
        try:
            if self.context:
                try:
                    self.context.close()
                except Exception:
                    pass
                self.context = None
            
            if self.browser:
                try:
                    self.browser.close()
                except Exception:
                    pass
                self.browser = None
            
            if self.playwright:
                try:
                    self.playwright.stop()
                except Exception:
                    pass
                self.playwright = None
            
            logger.debug("[CLEANUP] 已清理失败时的 Playwright 资源")
        except Exception as cleanup_error:
            logger.debug(f"[CLEANUP] 清理失败: {cleanup_error}")
    
    def close_browser(self, page=None):
        """
        关闭浏览器（静默执行）
        
        注意：
        - 如果使用全局单例，不关闭 playwright 实例（由 _cleanup_global_playwright() 统一管理）
        - 如果使用独立实例，需要关闭 playwright 实例
        
        Args:
            page: 页面对象（可选）
        """
        try:
            if page:
                page.close()
            
            if self.context:
                self.context.close()
                self.context = None
            
            if self.browser:
                self.browser.close()
                self.browser = None
            
            # 【关键修复】根据 use_global_instance 决定是否关闭 playwright 实例
            if not self.use_global_instance and self.playwright:
                # 独立实例需要关闭
                self.playwright.stop()
                self.playwright = None
                logger.debug("[PLAYWRIGHT] 已关闭独立 Playwright 实例")
            # 全局单例不关闭，由 _cleanup_global_playwright() 统一管理
            
            # 从全局追踪列表中移除
            _unregister_instance(self)
                
        except Exception as e:
            logger.error(f"关闭浏览器失败: {e}")
            raise
