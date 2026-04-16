# test_cases/体验/首页/定位面板/conftest.py
"""
定位面板测试专用 conftest
优化：module 级别 fixture，一个测试文件只打开一次浏览器
"""
import pytest
import os
from utils.browser_manager import BrowserManager
from utils.logger import setup_logger

logger = setup_logger()


@pytest.fixture(scope="module")
def page(config):
    """
    浏览器页面 fixture（module 级别）
    一个测试文件（批次）只打开一次浏览器，所有测试用例共享
    
    优势：
    - 提升执行效率（减少浏览器启动次数）
    - 降低资源消耗
    - 适合无状态的页面测试（如定位面板测试）
    
    注意：
    - 测试用例之间需要保持独立性（每个测试导航到初始页面）
    - 不适用于有登录态或状态保持的测试
    """
    from utils.browser_manager import BrowserManager
    
    browser_manager = BrowserManager()
    page = browser_manager.start_browser(
        browser_type=config['browser']['type'],
        headless=config['browser']['headless'],
        base_url=config['base_url'],
        viewport=config['browser']['viewport']
    )
    
    # 标记为使用中，防止被 pytest hooks 的 _cleanup_all(force=False) 清理
    browser_manager.mark_in_use()

    # 调试开关（默认关闭）
    if os.environ.get("DEBUG_PAUSE", "").lower() in ("1", "true", "yes"):
        try:
            page.pause()
        except Exception:
            pass
    
    yield page
    
    # 标记为已释放
    browser_manager.mark_released()
    
    # 测试批次结束后关闭浏览器
    if os.environ.get("KEEP_BROWSER_OPEN", "").lower() not in ("1", "true", "yes"):
        browser_manager.close_browser(page)


@pytest.fixture(autouse=True)
def setup_method(page):
    """
    在每个测试前自动执行的设置
    关闭可能打开的定位面板，确保测试之间状态独立
    """
    # 在测试开始前，尝试关闭可能打开的定位面板
    try:
        # 检查是否有tooltip打开
        tooltip = page.locator("[role='tooltip']")
        if tooltip.count() > 0 and tooltip.first.is_visible(timeout=1000):
            # 点击页面空白区域关闭tooltip
            page.mouse.click(200, 400)
            page.wait_for_timeout(500)
            logger.debug("✓ 已关闭之前打开的面板")
    except Exception:
        pass  # 没有打开的面板，继续
    
    yield  # 执行测试
    
    # 测试结束后，也尝试关闭面板（清理状态）
    try:
        tooltip = page.locator("[role='tooltip']")
        if tooltip.count() > 0 and tooltip.first.is_visible(timeout=1000):
            page.mouse.click(200, 400)
            page.wait_for_timeout(500)
            logger.debug("✓ 测试后清理：已关闭面板")
    except Exception:
        pass
