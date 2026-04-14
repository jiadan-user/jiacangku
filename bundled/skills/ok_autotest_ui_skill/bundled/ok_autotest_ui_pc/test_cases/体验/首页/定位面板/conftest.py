# test_cases/体验/首页/定位面板/conftest.py
"""
定位面板测试专用 conftest
优化：module 级别 fixture，一个测试文件只打开一次浏览器

自定义原因：
- 该目录保留 module 级 page，只为无状态批次测试复用浏览器。
- 生命周期逻辑复用 testcase_support，不再复制全局 page 实现。
"""
import pytest
from utils.logger import setup_logger
from utils.testcase_support import finish_managed_page, start_managed_page

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
    browser_manager, page = start_managed_page(config)
    
    yield page
    
    finish_managed_page(browser_manager, page)


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
