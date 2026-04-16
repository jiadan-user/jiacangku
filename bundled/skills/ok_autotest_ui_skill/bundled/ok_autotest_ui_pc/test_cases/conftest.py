# test_cases/conftest.py
import pytest
import allure
import os
import re
import sys
import asyncio
from datetime import datetime
from pathlib import Path
from utils.logger import setup_logger

# Playwright 截图前会等待 document.fonts.ready；外链字体慢/被 CSP 拦截时会卡在
# "waiting for fonts to load..." 直至 screenshot 超时。官方 workaround：跳过字体就绪等待。
# Ref: https://github.com/microsoft/playwright/issues/28995
os.environ.setdefault("PW_TEST_SCREENSHOT_NO_FONTS_READY", "1")

logger = setup_logger()


# ══════════════════════════════════════════════════════════════════════════════
# 【关键修复】Playwright Sync API 与 asyncio 事件循环冲突
#
# 问题根因：
#   当 fixture 在 yield 之前失败时（如 KeyError），Playwright 实例不会被关闭，
#   其内部的 asyncio 循环会残留，导致后续测试报错。
#
# 解决方案（针对 module scope 优化）：
#   1. BrowserManager 使用全局实例追踪器，追踪所有创建的实例
#   2. pytest hook 在每个模块的首个用例前清理上一个模块的残留资源
#   3. session 结束时强制清理所有资源
#   4. 移除用例级别的清理逻辑（module scope 下不需要）
# ══════════════════════════════════════════════════════════════════════════════


def _cleanup_all(force=False):
    """
    清理 Playwright 实例和 asyncio 状态
    
    【P1 修复】使用 browser_manager 的新 API，职责分离更清晰
    
    Args:
        force: 如果为 True，强制清理所有实例（用于 session 结束时）
               如果为 False，只清理非使用中的实例（保护 module 级 fixture）
    
    这个函数会：
    1. 清理未正确关闭的 Playwright 实例（根据 force 参数决定是否保护使用中的实例）
    2. 如果没有活跃实例，清理 asyncio 事件循环
    """
    # 1. 清理 Playwright 实例
    try:
        from utils.browser_manager import cleanup_all_playwright_instances, cleanup_asyncio_if_needed
        cleaned, remaining = cleanup_all_playwright_instances(force=force)
        logger.debug(f"[CLEANUP] 清理了 {cleaned} 个实例，剩余 {remaining} 个")
        
        # 2. 如果没有剩余实例，清理 asyncio 状态
        if remaining == 0:
            cleanup_asyncio_if_needed()
    except Exception as e:
        logger.warning(f"[CLEANUP] 清理时出错: {e}")


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """
    pytest hook：在每个测试用例的 setup 阶段开始前执行
    
    优化说明（针对 module scope）：
    - 只在每个模块的首个用例前清理上一个模块可能残留的资源
    - 同一模块内的后续用例跳过清理，避免影响 module-scoped fixture
    - force=False 保护当前模块正在使用的 module 级 fixture
    
    为什么仍需要这个 hook？
    1. 防止上一个模块的 fixture 初始化失败导致资源泄漏
    2. 确保每个模块开始时环境干净
    3. 支持并行执行时的资源隔离
    """
    # 获取或初始化已清理模块的追踪集合
    if not hasattr(pytest_runtest_setup, '_cleaned_modules'):
        pytest_runtest_setup._cleaned_modules = set()
    
    # 只在模块的第一个用例时清理
    if item.module not in pytest_runtest_setup._cleaned_modules:
        _cleanup_all(force=False)
        pytest_runtest_setup._cleaned_modules.add(item.module)
        logger.debug(f"[CLEANUP] 模块 {item.module.__name__} 首个用例前清理完成")


def pytest_sessionfinish(session, exitstatus):
    """
    pytest hook：整个测试会话结束时执行
    
    最终清理，强制清理所有资源，确保没有残留。
    这是必须保留的 hook，确保测试结束后没有任何残留进程。
    """
    _cleanup_all(force=True)
    
    # 清理模块追踪记录
    if hasattr(pytest_runtest_setup, '_cleaned_modules'):
        pytest_runtest_setup._cleaned_modules.clear()
    
    logger.debug("[CLEANUP] Session 结束，所有资源已强制清理")


# ========== 动态注册 case_id_* markers ==========

def pytest_configure(config):
    """
    pytest 配置钩子 - 动态注册 case_id_* markers
    
    这样做的好处：
    1. 避免 pytest.ini 中列出数百个 markers，保持文件简洁
    2. 新增用例时无需手动更新 pytest.ini
    3. 运行时自动扫描并注册所有 case_id_* markers
    """
    # 扫描 test_cases 目录下的所有测试文件，提取 case_id_* markers
    test_cases_dir = Path(__file__).parent
    case_id_pattern = re.compile(r'@pytest\.mark\.(case_id_\w+)')
    
    registered_markers = set()
    
    for test_file in test_cases_dir.rglob('test_*.py'):
        try:
            content = test_file.read_text(encoding='utf-8')
            markers = case_id_pattern.findall(content)
            registered_markers.update(markers)
        except Exception:
            pass  # 忽略读取失败的文件
    
    # 注册所有发现的 case_id_* markers
    for marker in registered_markers:
        config.addinivalue_line("markers", f"{marker}: 自动注册的用例标识")
    
    logger.debug(f"动态注册了 {len(registered_markers)} 个 case_id_* markers")


# ========== Fixture 定义 ==========

@pytest.fixture(scope="module")
def config(request):
    """
    读取测试模块内的 _CONFIG
    支持通过环境变量 HEADLESS 全局覆盖无头模式设置
    
    新生成的脚本必须在文件顶部定义 _CONFIG 字典
    """
    if not hasattr(request.module, '_CONFIG'):
        raise ValueError(
            f"测试模块 {request.module.__name__} 缺少 _CONFIG 配置。\n"
            f"请确保脚本由 playwright-test-generator 生成，或手动添加 _CONFIG。"
        )
    cfg = request.module._CONFIG
    
    # 检查是否有全局环境变量覆盖
    env_headless = os.getenv("HEADLESS")
    if env_headless is not None:
        cfg['browser']['headless'] = env_headless.lower() in ('true', '1', 't', 'yes', 'y')
    elif not cfg['browser'].get('headless', False):
        # 在无显示器的 Linux 环境（CI 服务器）下自动切换为无头模式
        import sys
        if sys.platform.startswith('linux') and not os.getenv("DISPLAY"):
            cfg['browser']['headless'] = True

    return cfg


@pytest.fixture(scope="module")
def page(config, request):
    """
    浏览器页面 fixture（静默执行）
    整个测试模块共享同一个浏览器实例，提升执行效率 80-90%
    
    注意：
    1. scope="module"：同一模块内的所有测试共享浏览器，模块结束后关闭
    2. 使用 mark_in_use()/mark_released() 保护实例不被 pytest hooks 提前清理
    3. 测试间状态隔离由 reset_page_state_after_test fixture 处理
    4. 认证：优先环境变量 MARKETPLACE_STORAGE_STATE；否则若测试文件同目录存在 auth_state.json 则自动加载（如 marketplace_post）
    """
    from utils.browser_manager import BrowserManager
    
    browser_manager = BrowserManager()
    storage_path = os.environ.get("MARKETPLACE_STORAGE_STATE", "").strip()
    storage_kw = {}
    if storage_path and Path(storage_path).is_file():
        storage_kw["storage_state"] = storage_path
        logger.info("[AUTH] MARKETPLACE_STORAGE_STATE=%s", storage_path)
    else:
        module_dir = Path(request.module.__file__).resolve().parent
        default_auth = module_dir / "auth_state.json"
        if default_auth.is_file():
            storage_kw["storage_state"] = str(default_auth)
            logger.info("[AUTH] 使用模块旁默认 auth_state.json: %s", default_auth)
    page = browser_manager.start_browser(
        browser_type=config['browser']['type'],
        headless=config['browser']['headless'],
        base_url=config['base_url'],
        viewport=config['browser']['viewport'],
        **storage_kw,
    )
    
    # 标记为使用中，防止被 pytest hooks 的 _cleanup_all(force=False) 清理
    browser_manager.mark_in_use()

    # 调试开关（默认关闭，不影响正常跑测）
    # - DEBUG_PAUSE=1: 启动后立刻暂停，打开 Playwright Inspector（用于手动调试）
    # - KEEP_BROWSER_OPEN=1: 用例结束后不自动关闭浏览器（便于观察最终页面/控制台）
    if os.environ.get("DEBUG_PAUSE", "").lower() in ("1", "true", "yes"):
        try:
            page.pause()
        except Exception:
            # 某些环境不支持 pause（例如无 GUI），保持静默
            pass
    
    yield page
    
    # 标记为已释放
    browser_manager.mark_released()
    
    # 模块结束后关闭浏览器（静默执行）
    if os.environ.get("KEEP_BROWSER_OPEN", "").lower() not in ("1", "true", "yes"):
        browser_manager.close_browser(page)


@pytest.fixture(autouse=True)
def reset_page_state_after_test(page, request):
    """
    每个测试后自动重置页面状态，避免测试间污染
    
    这个 fixture 配合 module 级的 page fixture 使用：
    - page fixture 负责浏览器生命周期（模块级）
    - 本 fixture 负责测试间状态隔离（每个测试后执行）
    """
    yield
    
    # 测试结束后重置页面状态
    try:
        if page and not page.is_closed():
            # 关闭可能打开的弹窗/对话框
            page.keyboard.press("Escape")
            # 等待一小段时间确保状态稳定
            page.wait_for_timeout(200)
    except Exception:
        pass  # 静默处理，不影响测试结果


@pytest.fixture(scope="function")
def geolocation_page(request, config):
    """
    带地理位置权限的浏览器页面 fixture（静默执行）

    用于需要模拟 GPS 坐标的测试用例（如地图定位授权）。
    调用方通过 pytest.mark.parametrize 或 request.param 传入配置：
        {
            "geolocation": {"latitude": -33.8688, "longitude": 151.2093},
            "grant_permission": True   # True=授权, False=拒绝(不传geolocation)
        }

    使用示例（测试方法签名）：
        def test_xxx(self, geolocation_page, config):
            page, geo_config = geolocation_page
            ...
    """
    from utils.browser_manager import BrowserManager
    import threading
    import queue as _queue

    # 【根本修复】Playwright Sync API 内部使用 asyncio loop（run_until_complete）。
    # 当 module-scope 的 Playwright 实例运行时，其 asyncio loop 处于 running 状态，
    # 导致同一线程内无法再启动新的 Playwright 实例（asyncio 不允许嵌套 run_until_complete）。
    #
    # 解法：在专用子线程中运行 geolocation browser 的完整生命周期。
    # 子线程没有 running asyncio loop，可以正常启动 Playwright。
    # page 对象通过消息队列在子线程内调用，绝不传回主线程使用。
    # 测试代码通过 run_in_browser(callable) 将操作发送到子线程执行。

    geo_param = getattr(request, "param", {}) or {}
    grant = geo_param.get("grant_permission", True)
    geo_coords = geo_param.get("geolocation", None)

    _res_q = _queue.Queue()   # 子线程 → 主线程：启动结果 / 操作结果
    _cmd_q = _queue.Queue()   # 主线程 → 子线程：callable 指令
    _STOP = object()

    def _browser_thread():
        # 【关键修复】子线程必须使用独立的 Playwright 实例
        # 根据 Playwright 官方文档，sync API 不是线程安全的
        # 参考：https://github.com/microsoft/playwright-python/issues/623
        bm = BrowserManager(use_global_instance=False)
        pg = None
        try:
            if grant and geo_coords:
                pg = bm.start_browser(
                    browser_type=config["browser"]["type"],
                    headless=config["browser"]["headless"],
                    base_url=config["base_url"],
                    viewport=config["browser"]["viewport"],
                    geolocation=geo_coords,
                    permissions=["geolocation", "notifications"],
                )
            else:
                pg = bm.start_browser(
                    browser_type=config["browser"]["type"],
                    headless=config["browser"]["headless"],
                    base_url=config["base_url"],
                    viewport=config["browser"]["viewport"],
                    geolocation=None,
                    permissions=["notifications"],
                )
            _res_q.put(('ready', None))

            # 循环处理主线程发来的 callable
            while True:
                cmd = _cmd_q.get()
                if cmd is _STOP:
                    break
                fn = cmd
                try:
                    result = fn(pg)
                    _res_q.put(('ok', result))
                except Exception as e:
                    _res_q.put(('error', e))
        except Exception as e:
            _res_q.put(('error', e))
            pg = None
        finally:
            if pg is not None:
                try:
                    if os.environ.get("KEEP_BROWSER_OPEN", "").lower() not in ("1", "true", "yes"):
                        bm.close_browser(pg)
                except Exception:
                    pass

    t = threading.Thread(target=_browser_thread, daemon=True)
    t.start()

    status, err = _res_q.get(timeout=120)
    if status == 'error':
        t.join(timeout=5)
        raise err

    def run_in_browser(fn):
        """在持有 page 的子线程中执行 fn(page)，返回结果或抛出异常"""
        _cmd_q.put(fn)
        s, r = _res_q.get(timeout=120)
        if s == 'error':
            raise r
        return r

    logger.debug("[GEO_FIXTURE] 子线程 Playwright 启动成功")

    # yield (geo_param, run_in_browser)：测试通过 run_in_browser(lambda page: ...) 操作 page
    yield geo_param, run_in_browser

    _cmd_q.put(_STOP)
    t.join(timeout=30)
    logger.debug("[GEO_FIXTURE] 子线程已退出")


# ========== 失败截图钩子（自动执行）==========

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    测试用例失败时自动截图并附加到 Allure 报告
    这是唯一允许使用 allure.attach() 的地方
    """
    outcome = yield
    report = outcome.get_result()
    
    # 只在测试执行阶段（call）且失败时截图
    if report.when == "call" and report.failed:
        page = item.funcargs.get('page')
        
        if page:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_name = f"FAILED_{item.name}_{timestamp}.png"
            screenshot_dir = Path("reports/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = screenshot_dir / screenshot_name
            
            try:
                # 截图
                page.screenshot(path=str(screenshot_path), timeout=60000, full_page=True)
                
                # 附加到 Allure 报告（仅保留截图，不附加其他信息）
                with open(screenshot_path, 'rb') as f:
                    allure.attach(
                        f.read(),
                        name="失败截图",
                        attachment_type=allure.attachment_type.PNG
                    )
                
                # URL 记录在日志中，不附加到报告
                logger.error(f"测试失败 URL: {page.url}")
                
            except Exception as e:
                logger.error(f"截图失败: {e}")
