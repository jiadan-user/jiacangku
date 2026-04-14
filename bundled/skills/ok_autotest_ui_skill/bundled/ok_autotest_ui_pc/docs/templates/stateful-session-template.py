"""
状态型用例模板

适用场景：
- 需要登录态、Session、数据准备
- 允许定义显式 helper / fixture
- 默认仍复用全局 page，不新增目录级 page/config
"""
import pytest
import allure

from pages.login_page import LoginPage
from pages.REPLACE_PAGE import REPLACEPage
from utils.logger import setup_logger
from utils.session_manager import SessionManager

logger = setup_logger()

_CONFIG = {
    "site": "ae",
    "site_name": "阿联酋站",
    "role": "seller",
    "user_name": "replace_user",
    "base_url": "https://example.com",
    "test_account": {
        "username": "replace@example.com",
        "password": "replace-password",
    },
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
def prepared_page(page, config):
    """显式表达状态准备，不把登录流程散落到测试函数主体。"""
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config["base_url"], session_name)
    login_page = LoginPage(page)

    if not session_manager.load_session():
        login_page.navigate_to_home_page(base_url=config["base_url"])
        login_page.login(config["test_account"]["username"], config["test_account"]["password"])
        session_manager.save_session()

    yield page


@pytest.mark.case_id_replace_state_001
@pytest.mark.p1
@pytest.mark.REPLACE_MODULE_MARK
@pytest.mark.ae
@allure.feature("OK")
@allure.story("REPLACE_STATEFUL_STORY")
@allure.title("REPLACE_STATEFUL_TITLE")
def test_replace_stateful_case(prepared_page, config):
    target_page = REPLACEPage(prepared_page)

    with allure.step("进入目标状态页"):
        target_page.goto(config["base_url"])
        target_page.wait_for_key_section([
            "REPLACE_READY_SELECTOR",
        ])

    with allure.step("执行状态型动作"):
        # 如果必须保留极短等待，必须写明原因，且默认不超过 300ms。
        pass

    with allure.step("验证结果"):
        assert True, "请替换为明确断言"
