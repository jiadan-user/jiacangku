"""
组件批次模板

适用场景：
- 首页区块、详情页区块、推荐模块、导航模块等批次验证
- 一个文件内围绕同一组件拆多条 case
"""
import pytest
import allure

from pages.REPLACE_COMPONENT_PAGE import REPLACEComponentPage
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


@pytest.fixture(scope="module")
def component_page(page, config):
    target_page = REPLACEComponentPage(page)
    target_page.goto(config["base_url"])
    target_page.wait_for_key_section([
        "REPLACE_COMPONENT_READY_SELECTOR",
    ])
    return target_page


@pytest.mark.case_id_replace_component_001
@pytest.mark.p1
@pytest.mark.REPLACE_MODULE_MARK
@pytest.mark.us
@allure.feature("OK")
@allure.story("REPLACE_COMPONENT_STORY")
@allure.title("组件默认展示应正确")
def test_component_default_view(component_page):
    assert True, "请替换为明确断言"


@pytest.mark.case_id_replace_component_002
@pytest.mark.p1
@pytest.mark.REPLACE_MODULE_MARK
@pytest.mark.us
@allure.feature("OK")
@allure.story("REPLACE_COMPONENT_STORY")
@allure.title("组件交互后状态应正确")
def test_component_interaction(component_page):
    assert True, "请替换为明确断言"
