# test_cases/ai/ai_publish/conftest.py
"""
AI发布页测试专用配置
- 失败自动重试 3 次（间隔 2 秒）
- 失败自动截图并附加到 Allure 报告
"""
import os
import sys
import pytest
import allure
from datetime import datetime
from pathlib import Path
from utils.browser_manager import BrowserManager
from utils.logger import setup_logger


def _resolve_headless(headless: bool) -> bool:
    """Linux 无显示服务器时强制 headless，其余环境尊重配置。"""
    if sys.platform.startswith("linux"):
        if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
            return True
    return headless

logger = setup_logger()


# ========== 失败重试（3次）==========

def pytest_collection_modifyitems(items):
    """为 ai_publish 目录下的所有测试用例自动添加失败重试（3次，间隔2秒）。"""
    for item in items:
        if "ai/ai_publish" in str(item.fspath):
            item.add_marker(pytest.mark.flaky(reruns=3, reruns_delay=2))


# ========== Fixtures ==========

@pytest.fixture(scope="module")
def config(request):
    """读取测试模块内的 _CONFIG。"""
    if not hasattr(request.module, '_CONFIG'):
        raise ValueError(
            f"测试模块 {request.module.__name__} 缺少 _CONFIG 配置。"
        )
    return request.module._CONFIG


@pytest.fixture(scope="module")
def page(config):
    """
    AI发布页测试专用浏览器页面 fixture。
    每个测试用例独立的浏览器实例。
    """
    browser_manager = BrowserManager()
    page = browser_manager.start_browser(
        browser_type=config['browser']['type'],
        headless=_resolve_headless(config['browser']['headless']),
        base_url=config['base_url'],
        viewport=config['browser']['viewport']
    )

    browser_manager.mark_in_use()

    yield page

    browser_manager.mark_released()
    browser_manager.close_browser(page)


# ========== 失败截图钩子 ==========

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试用例失败时自动截图并附加到 Allure 报告。"""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get('page')

        if page:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_name = f"FAILED_{item.name}_{timestamp}.png"
            screenshot_dir = Path("reports/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = screenshot_dir / screenshot_name

            try:
                page.screenshot(path=str(screenshot_path, timeout=60000), full_page=True)

                with open(screenshot_path, 'rb') as f:
                    allure.attach(
                        f.read(),
                        name="失败截图",
                        attachment_type=allure.attachment_type.PNG
                    )

                logger.error(f"测试失败 URL: {page.url}")

            except Exception as e:
                logger.error(f"截图失败: {e}")
