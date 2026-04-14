# test_cases/site_selection/conftest.py
"""
地区选择页面测试专用 conftest
优化：module 级别 fixture，一个测试文件只打开一次浏览器

自定义原因：
- 该目录保留 module 级 page，只为无状态批次测试复用浏览器。
- 生命周期逻辑复用 testcase_support，不再复制全局 page 实现。
"""
import pytest
from utils.testcase_support import finish_managed_page, start_managed_page


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
    browser_manager, page = start_managed_page(config)
    
    yield page
    
    finish_managed_page(browser_manager, page)
