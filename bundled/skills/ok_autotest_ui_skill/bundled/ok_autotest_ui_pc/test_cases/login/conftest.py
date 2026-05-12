# test_cases/login/conftest.py
"""
Login 模块测试的 conftest 配置
优化：减少重复的页面加载，提升执行效率
"""

import pytest
from pages.login_page import LoginPage
from utils.logger import setup_logger

logger = setup_logger()


def _ensure_logged_out_impl(self, base_url=None):
    """
    确保已退出登录状态（为 LoginPage 动态添加的方法）
    
    Args:
        base_url: 基础URL
    """
    try:
        # 清除 cookies 和存储
        self.page.context.clear_cookies()
        self.page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
        logger.debug("✓ 已清除 Cookies 和存储")
        
        # 重新加载页面
        if base_url:
            self.page.goto(base_url, wait_until="domcontentloaded", timeout=10000)
        else:
            self.page.reload(wait_until="domcontentloaded", timeout=10000)
        
        self.page.wait_for_timeout(1000)
        
        # 处理 cookie 弹窗
        self.handle_cookie_popup()
        logger.debug("✓ 已确保退出登录状态")
    except Exception as e:
        logger.warning(f"确保退出登录失败: {e}")


@pytest.fixture(scope="module")
def login_config():
    """
    Login模块专用配置（session级别）
    从任一测试文件读取 _CONFIG，所有login测试共享
    """
    import os
    import importlib.util
    import sys
    from pathlib import Path
    
    # 固定从 test_login_welcome_page_tc001_tc012 读取公共 _CONFIG，避免 glob 顺序不确定
    login_dir = Path(__file__).parent
    test_file = login_dir / "test_login_welcome_page_tc001_tc012.py"
    if not test_file.exists():
        # 降级：取第一个字母序最小的文件，保证跨平台稳定
        test_file = sorted(login_dir.glob("test_*.py"))[0]
    
    spec = importlib.util.spec_from_file_location("_temp_module", test_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    config = module._CONFIG
    
    # 支持环境变量覆盖
    env_headless = os.getenv("HEADLESS")
    if env_headless:
        config['browser']['headless'] = env_headless.lower() in ('true', '1', 'yes')
    
    # 为 LoginPage 类动态添加 ensure_logged_out 方法
    from pages.login_page import LoginPage
    if not hasattr(LoginPage, 'ensure_logged_out'):
        LoginPage.ensure_logged_out = _ensure_logged_out_impl
        logger.debug("✅ 已为 LoginPage 添加 ensure_logged_out 方法")
    
    return config


@pytest.fixture(scope="module")
def page(login_config):
    """
    为 login 模块提供优化的 page fixture（module级别，每个测试文件独立实例）
    
    优化点：
    1. 支持无头模式（通过环境变量 HEADLESS）
    2. 资源拦截（只拦截第三方追踪脚本，保留图片、CSS、JS）
    3. 每个测试文件独立浏览器实例，避免并发竞争
    4. 优化超时时间：将默认 15秒 改为 5秒
    """
    from utils.browser_manager import BrowserManager
    import os
    
    browser_manager = BrowserManager()
    
    # 优化1：支持环境变量控制无头模式
    headless = os.getenv("HEADLESS", "").lower() in ("true", "1", "yes")
    if not headless:
        headless = login_config['browser'].get('headless', False)
    
    page = browser_manager.start_browser(
        browser_type=login_config['browser']['type'],
        headless=headless,
        base_url=login_config['base_url'],
        viewport=login_config['browser']['viewport']
    )
    
    # 优化2：只拦截第三方追踪脚本（保留图片、CSS、JS等所有页面资源）
    def route_handler(route):
        try:
            url = route.request.url
            
            # 只拦截第三方追踪脚本，不拦截图片等页面资源
            if any(tracker in url for tracker in [
                "google-analytics.com",
                "googletagmanager.com", 
                "facebook.com/tr",
                "doubleclick.net",
                "analytics.js"
            ]):
                route.abort()
                return
            
            route.continue_()
        except Exception:
            # 如果拦截失败，继续请求
            try:
                route.continue_()
            except:
                pass
    
    try:
        page.route("**/*", route_handler)
        logger.debug(f"[LOGIN] 已启用资源拦截（只拦截追踪脚本，保留图片，headless={headless}）")
    except Exception as e:
        logger.warning(f"[LOGIN] 资源拦截设置失败: {e}")
    
    # 默认超时 15 秒：页面导航通常需要 8-20s，5s 在弱网下必然超时
    page.set_default_timeout(15000)
    logger.debug("[LOGIN] 已设置默认超时时间为 15 秒")
    
    # 标记为使用中，防止被 pytest hooks 清理
    browser_manager.mark_in_use()
    
    yield page
    
    # 标记为已释放
    browser_manager.mark_released()
    
    # 整个测试会话结束后才关闭浏览器
    if os.environ.get("KEEP_BROWSER_OPEN", "").lower() not in ("1", "true", "yes"):
        try:
            browser_manager.close_browser(page)
            logger.debug(f"[LOGIN] 测试会话结束，关闭浏览器")
        except Exception as e:
            logger.warning(f"[LOGIN] 关闭浏览器失败: {e}")


@pytest.fixture(scope="module")
def preloaded_page(page, login_config):
    """
    预加载的页面，每个测试文件独立实例（module级别）

    优化策略：
    1. 只加载一次页面和 Cookie 处理
    2. 用例间只需要重置登录状态
    3. module-scoped 避免并发时多个文件共用同一个 page 产生竞争
    """
    login_page = LoginPage(page)
    base_url = login_config.get('base_url')
    
    # 首次加载页面
    try:
        login_page.navigate_to_home_page(base_url)
        login_page.handle_cookie_popup()
        logger.debug(f"[LOGIN] 页面预加载完成: {base_url}")
    except Exception as e:
        logger.warning(f"[LOGIN] 页面预加载失败: {e}")
    
    yield page


def _close_login_dialog_if_open(page):
    """
    关闭登录弹窗（如果打开）
    增强版：支持多种关闭方式，并验证弹窗是否真正关闭
    """
    try:
        # 1. 先检测弹窗是否存在
        modal_dialog = page.locator('[role="dialog"][class*="modal show"], [role="dialog"][class*="Modal"]')
        
        if not modal_dialog.is_visible(timeout=200):
            logger.debug("未检测到打开的登录弹窗，无需关闭")
            return False
        
        logger.debug("检测到登录弹窗，准备关闭...")
        
        # 2. 尝试多种关闭方式（优先级从高到低）
        closed = False
        
        # 方式1：点击关闭按钮（X 图标） - 优先级最高
        try:
            # 在弹窗内查找关闭按钮
            close_selectors = [
                # CSS 选择器组合
                '[role="dialog"] button[aria-label*="close" i]',
                '[role="dialog"] button[aria-label*="Close"]',
                '[role="dialog"] [class*="close" i]',
                '[role="dialog"] button:has-text("×")',
                '[role="dialog"] button:has-text("✕")',
                # 常见的关闭按钮 class
                '[role="dialog"] .btn-close',
                '[role="dialog"] .close',
            ]
            
            for selector in close_selectors:
                try:
                    close_btn = page.locator(selector).first
                    if close_btn.is_visible(timeout=500):
                        logger.debug(f"尝试点击关闭按钮: {selector}")
                        close_btn.click(timeout=3000, force=True)
                        page.wait_for_timeout(1000)
                        
                        # 验证弹窗是否关闭
                        if not modal_dialog.is_visible(timeout=1000):
                            closed = True
                            logger.debug(f"✓ 成功通过关闭按钮关闭弹窗: {selector}")
                            break
                except Exception:
                    continue
            
            if closed:
                # 额外等待，确保 DOM 完全稳定
                page.wait_for_timeout(2000)
                try:
                    page.wait_for_load_state("domcontentloaded", timeout=3000)
                except Exception:
                    pass
                logger.debug("✓ 弹窗关闭，页面已稳定")
                return True
        except Exception as e:
            logger.debug(f"方式1（关闭按钮）失败: {e}")
        
        # 方式2：如果在密码页，尝试点击返回按钮
        try:
            back_btn = page.locator('[role="dialog"] button:has-text("Back"), [role="dialog"] [aria-label*="back" i]').first
            if back_btn.is_visible(timeout=500):
                logger.debug("检测到返回按钮，尝试返回到欢迎页...")
                back_btn.click(timeout=2000)
                page.wait_for_timeout(1000)
                
                # 返回后再次尝试关闭
                close_btn = page.locator('[role="dialog"] button[aria-label*="close" i], [role="dialog"] .close').first
                if close_btn.is_visible(timeout=1000):
                    close_btn.click(timeout=2000, force=True)
                    page.wait_for_timeout(1000)
                    
                    if not modal_dialog.is_visible(timeout=1000):
                        closed = True
                        logger.debug("✓ 通过返回后关闭弹窗成功")
        except Exception as e:
            logger.debug(f"方式2（返回按钮）失败: {e}")
        
        # 方式3：按 ESC 键
        if not closed:
            try:
                logger.debug("尝试按 ESC 键关闭弹窗...")
                page.keyboard.press("Escape")
                page.wait_for_timeout(1000)
                
                if not modal_dialog.is_visible(timeout=1000):
                    closed = True
                    logger.debug("✓ 通过 ESC 键关闭弹窗成功")
            except Exception as e:
                logger.debug(f"方式3（ESC 键）失败: {e}")
        
        # 最终验证
        if closed:
            page.wait_for_timeout(2000)
            try:
                page.wait_for_load_state("domcontentloaded", timeout=3000)
            except Exception:
                pass
            logger.debug("✓ 登录弹窗已关闭，页面已稳定")
            return True
        else:
            logger.warning("⚠️  所有关闭方式均失败，弹窗可能仍然打开")
            return False
            
    except Exception as e:
        logger.debug(f"关闭登录弹窗失败: {e}")
        return False


@pytest.fixture(autouse=True)
def smart_reset_for_login_tests(page, login_config, request):
    """
    智能重置策略：只有标记了 needs_logout 的用例需要退登，其他用例只关闭弹窗
    
    策略：
    1. 测试前：检查并关闭可能残留的弹窗，确保干净的起始状态
    2. 测试后：只有标记了 needs_logout 的测试才退登，其他只关闭弹窗
    """
    login_page = LoginPage(page)
    test_name = request.node.name
    
    # 测试前：检查并关闭可能残留的弹窗
    try:
        if _close_login_dialog_if_open(page):
            logger.debug(f"🧹 [{test_name}] 测试前：检测到残留弹窗，已关闭")
    except Exception as e:
        logger.debug(f"测试前关闭弹窗失败: {e}")
    
    yield
    
    # 测试后：根据标记决定是否退登
    try:
        if page and not page.is_closed():
            # 检查是否标记了需要退登
            needs_logout = request.node.get_closest_marker('needs_logout')
            
            if needs_logout:
                # 被标记 needs_logout 的用例：需要退登
                logger.info(f"🔄 [{test_name}] 测试后：需要退登")
                try:
                    # 强制退登，不依赖 _login_success 标志
                    login_page.page.context.clear_cookies()
                    login_page.page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
                    logger.info("✓ Cookies和存储已清除")
                    
                    # 导航回首页（而不是reload），确保完全重新加载
                    try:
                        base_url = login_config.get('base_url')
                        login_page.page.goto(base_url, wait_until="domcontentloaded", timeout=10000)
                        logger.info(f"✓ 已导航回首页: {base_url}")
                        
                        # 处理cookie弹窗
                        login_page.handle_cookie_popup()
                        logger.info("✓ Cookie弹窗已处理")
                    except Exception as e:
                        logger.warning(f"导航首页失败: {e}")
                    
                    # 重置登录标志
                    login_page._login_success = False
                    logger.info(f"✅ [{test_name}] 退登完成")
                except Exception as e:
                    logger.warning(f"退登失败: {e}")
            else:
                # 其他测试：只关闭弹窗
                logger.info(f"🔄 [{test_name}] 测试后：只关闭弹窗")
                try:
                    _close_login_dialog_if_open(page)
                    logger.info(f"✓ [{test_name}] 弹窗关闭完成")
                except Exception as e:
                    logger.debug(f"关闭弹窗失败: {e}")
    except Exception as e:
        logger.debug(f"[LOGIN] 重置失败: {e}")
