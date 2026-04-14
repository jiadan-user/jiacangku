"""
标准功能流模板

适用场景：
- 单页面或短流程功能验证
- 不需要自定义目录级 conftest
- 直接复用全局 config/page fixture
"""
import pytest
import allure

from pages.REPLACE_PAGE import REPLACEPage
from utils.logger import setup_logger

logger = setup_logger()

_CONFIG = {
    "site": "us",
    "site_name": "OK美国站",
    "base_url": "https://example.com",
    "browser": {
        "type": "chromium",
        "headless": False,
        "viewport": {"width": 1920, "height": 1080},
    },
    "timeout": {
        "default": 30000,
    },
}


@pytest.mark.case_id_replace_001
@pytest.mark.p1
@pytest.mark.REPLACE_MODULE_MARK
@pytest.mark.us
@allure.feature("OK")
@allure.story("REPLACE_STORY")
@allure.title("REPLACE_TITLE")
def test_replace_case(page, config):
    target_page = REPLACEPage(page)

    with allure.step("进入目标页面"):
        target_page.goto(config["base_url"])
        target_page.wait_for_key_section([
            "REPLACE_READY_SELECTOR",
        ])

    with allure.step("执行核心动作"):
        # 不要新增 page.wait_for_timeout(3000/5000)
        # 优先使用 locator wait / expect / BasePage helper
        pass

    with allure.step("验证结果"):
        assert True, "请替换为明确断言"
