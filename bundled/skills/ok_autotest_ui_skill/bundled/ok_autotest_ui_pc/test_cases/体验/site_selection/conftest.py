# test_cases/site_selection/conftest.py
"""
地区选择页面测试专用 conftest
优化：module 级别 fixture，一个测试文件只打开一次浏览器
"""
import pytest
import os
from utils.browser_manager import BrowserManager


@pytest.fixture(scope="module")
def page(config):
    """
    浏览器页面 fixture（module 级别）
    一个测试文件（批次）只打开一次浏览器，所有测试用例共享
    
    优势：
    - 提升执行效率（减少浏览器启动次数）
    - 降低资源消耗
    - 适合无状态的页面测试（如地区选择页）
    
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
