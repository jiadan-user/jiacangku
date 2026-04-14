# test_cases/ai/ai_chat/conftest.py
"""
AI Chat 测试专用配置
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


def _resolve_headless(headless: bool) -> bool:
    """兼容历史脚本的导入方式，后续统一改用 testcase_support。"""
    return resolve_headless_for_current_env(headless)


# ========== 失败重试（3次）==========

def pytest_collection_modifyitems(items):
    """为 ai/ai_chat 目录下的所有测试用例自动添加失败重试（3次，间隔2秒）。
    排除含 module 级 page fixture 的文件（RERUN 会重建 module fixture，
    触发 anyio event loop 冲突导致 Playwright Sync API 报错）。
    """
    # 含 module 级自定义 page fixture 的文件不加 flaky，避免 RERUN 触发 asyncio 冲突
    _exclude_files = {"test_ai_chat_job.py"}
    for item in items:
        if "ai/ai_chat" in str(item.fspath):
            if item.fspath.basename not in _exclude_files:
                item.add_marker(pytest.mark.flaky(reruns=3, reruns_delay=2))



# ========== Fixtures ==========

@pytest.fixture(scope="module")
def config(request):
    """读取测试模块内的 _CONFIG，并应用 runtime_overrides/env 覆盖。"""
    return build_runtime_config(request.module)


@pytest.fixture(scope="module")
def page(config):
    """
    AI Chat 测试专用浏览器页面 fixture（module 级，所有用例复用同一浏览器实例）。
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
