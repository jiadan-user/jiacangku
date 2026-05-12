# test_cases/publish_job/conftest.py
"""
发布职位测试专用配置
- 强制使用无头模式（不弹出浏览器窗口）
- 其他测试模块不受影响
"""
import pytest
import allure
from datetime import datetime
from pathlib import Path
from utils.browser_manager import BrowserManager
from utils.logger import setup_logger

logger = setup_logger()


@pytest.fixture(scope="module")
def config(request):
    """
    读取测试模块内的 _CONFIG
    如果模块没有 _CONFIG，则使用默认配置
    """
    if hasattr(request.module, '_CONFIG'):
        return request.module._CONFIG
    
    # 默认配置（用于没有 _CONFIG 的测试模块）
    return {
        'base_url': 'https://uspub.58v5.cn/biz/en/publish/job?categoryId=4000',
        'browser': {
            'type': 'chromium',
            'headless': True,
            'viewport': {'width': 1920, 'height': 1080}
        },
        'accounts': {
            'weijingjing02': {
                'username': 'weijingjing02@58.com',
                'password': 'Ok123456'
            }
        }
    }


@pytest.fixture(scope="module")
def page(config):
    """
    发布职位测试专用的浏览器页面 fixture
    强制使用无头模式，整个模块共享浏览器实例
    
    注意：使用 mark_in_use()/mark_released() 保护实例不被 pytest hooks 提前清理。
    """
    browser_manager = BrowserManager()
    
    # 强制使用无头模式（覆盖配置文件和环境变量）
    page = browser_manager.start_browser(
        browser_type=config['browser']['type'],
        headless=True,  # 强制无头模式
        base_url=config['base_url'],
        viewport=config['browser']['viewport']
    )
    
    # 标记为使用中，防止被 pytest hooks 的 _cleanup_all(force=False) 清理
    browser_manager.mark_in_use()
    
    logger.info("🚀 发布职位测试：使用无头模式（模块共享浏览器）")
    
    yield page
    
    # 标记为已释放
    browser_manager.mark_released()
    
    # 模块结束后关闭浏览器
    browser_manager.close_browser(page)


@pytest.fixture(autouse=True)
def reset_page_state_after_test(page):
    """每个测试后重置页面状态"""
    yield
    try:
        if page and not page.is_closed():
            page.keyboard.press("Escape")
            page.wait_for_timeout(200)
    except Exception:
        pass


# ========== 失败截图钩子 ==========

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    测试用例失败时自动截图并附加到 Allure 报告
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
                
                # 附加到 Allure 报告
                with open(screenshot_path, 'rb') as f:
                    allure.attach(
                        f.read(),
                        name="失败截图",
                        attachment_type=allure.attachment_type.PNG
                    )
                
                # URL 记录在日志中
                logger.error(f"测试失败 URL: {page.url}")
                
            except Exception as e:
                logger.error(f"截图失败: {e}")

