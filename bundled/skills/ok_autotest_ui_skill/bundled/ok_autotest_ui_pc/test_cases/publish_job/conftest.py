# test_cases/publish_job/conftest.py
"""
发布职位测试专用配置
- 强制使用无头模式（不弹出浏览器窗口）
- 其他测试模块不受影响

自定义原因：
- 该目录下有 9 个历史文件没有声明 _CONFIG，需要目录级默认配置兜底。
- page fixture 需要强制无头，避免本地/CI 执行时弹出窗口干扰。
"""
import pytest
from utils.logger import setup_logger
from utils.testcase_support import (
    attach_failure_screenshot,
    build_runtime_config,
    finish_managed_page,
    start_managed_page,
)

logger = setup_logger()


@pytest.fixture(scope="module")
def config(request):
    """
    读取测试模块内的 _CONFIG
    如果模块没有 _CONFIG，则使用默认配置
    """
    default_config = {
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
    return build_runtime_config(
        request.module,
        default_config=default_config,
        require_module_config=False,
    )


@pytest.fixture(scope="module")
def page(config):
    """
    发布职位测试专用的浏览器页面 fixture
    强制使用无头模式，整个模块共享浏览器实例
    
    注意：使用 mark_in_use()/mark_released() 保护实例不被 pytest hooks 提前清理。
    """
    browser_manager, page = start_managed_page(
        config,
        force_headless=True,
    )
    
    logger.info("🚀 发布职位测试：使用无头模式（模块共享浏览器）")
    
    yield page
    
    finish_managed_page(browser_manager, page)


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
            try:
                attach_failure_screenshot(item, logger)
            except Exception as e:
                logger.error(f"截图失败: {e}")
