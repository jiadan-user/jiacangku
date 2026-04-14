# test_cases/ai/ai_publish/conftest.py
"""
AI发布页测试专用配置
- 失败自动重试 3 次（间隔 2 秒）
- 失败自动截图并附加到 Allure 报告

自定义原因：
- 该目录保留独立 conftest，仅为目录级 flaky 策略和失败截图治理。
- config/page 逻辑默认复用全局约定，并通过 testcase_support 统一运行时覆盖。
"""
import os
import pytest
from utils.logger import setup_logger
from utils.testcase_support import (
    attach_failure_screenshot,
    build_runtime_config,
    finish_managed_page,
    resolve_headless_for_current_env,
    start_managed_page,
)


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
    """读取测试模块内的 _CONFIG，并应用 runtime_overrides/env 覆盖。"""
    return build_runtime_config(request.module)


@pytest.fixture(scope="module")
def page(config):
    """
    AI发布页测试专用浏览器页面 fixture。
    每个测试用例独立的浏览器实例。
    """
    browser_manager, page = start_managed_page(
        config,
        force_headless=resolve_headless_for_current_env(config["browser"]["headless"]),
    )

    yield page

    finish_managed_page(browser_manager, page)


# ========== 失败截图钩子 ==========

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试用例失败时自动截图并附加到 Allure 报告。"""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get('page')

        if page:
            try:
                attach_failure_screenshot(item, logger)
            except Exception as e:
                logger.error(f"截图失败: {e}")
