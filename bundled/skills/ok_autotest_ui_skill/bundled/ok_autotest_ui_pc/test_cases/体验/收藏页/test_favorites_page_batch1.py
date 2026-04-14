"""
OK.com 收藏页 - 批次1（TC001–TC005 访问控制与登录流程前半段）

由 playwright-test-generator 依据 CLI 录制生成。
用例文档：test_cases/体验/收藏页/OK.com-收藏页-测试用例-20260402.md
"""
import re

import allure
import pytest
from playwright.sync_api import expect

from pages.favorites_page import FavoritesPage
from pages.login_page import LoginPage
from utils.logger import setup_logger

logger = setup_logger()

_CONFIG = {
    "site": "ae",
    "site_name": "阿联酋站 (AE OK.com)",
    "role": "buyer",
    "user_name": "ae_buyer_sc",
    "base_url": "https://aepub.ok.com",
    "test_account": {
        "username": "shenchang@58.com",
        "password": "123456Tt",
    },
    "empty_favorites_account": {
        "username": "shencccccccc@outlook.com",
        "password": "123456Tt",
    },
    "browser": {
        "type": "chromium",
        "headless": False,
        "viewport": {"width": 1920, "height": 1080},
    },
    "timeout": {
        "default": 30000,
        "wait": 10000,
        "navigation": 30000,
    },
}


@pytest.mark.case_id_ae_favorites_001
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.ui
@pytest.mark.ae
@pytest.mark.favorite
@allure.feature("OK.com 收藏页")
@allure.story("访问控制与登录流程")
@allure.title("TC001: 访客访问收藏页被拦截")
@allure.severity(allure.severity_level.BLOCKER)
def test_tc001_visitor_favorites_intercepted(page, config):
    fav = FavoritesPage(page)
    login_page = LoginPage(page)

    with allure.step("步骤1：清除登录态并打开收藏页"):
        fav.reset_to_guest()
        fav.navigate_to_favorites_list(config["base_url"])
        login_page.handle_cookie_popup()
        page.wait_for_load_state("domcontentloaded", timeout=5000)

    with allure.step("步骤2：验证访客引导与无列表"):
        expect(page).to_have_title(re.compile(r"Favourites", re.I))
        expect(page.get_by_text("Log in to view more content")).to_be_visible()
        expect(page.get_by_text("Login").first).to_be_visible()
        expect(page.get_by_text(re.compile(r"Log\s*in\s*/\s*Register", re.I)).first).to_be_visible()
        # 已登录时不会出现访客空态文案；作为「无收藏列表」的可靠判据（页脚等处的 /cate- 链不计入）


@pytest.mark.case_id_ae_favorites_002
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.ui
@pytest.mark.ae
@pytest.mark.favorite
@allure.feature("OK.com 收藏页")
@allure.story("访问控制与登录流程")
@allure.title("TC002: 访客触发登录弹窗（邮箱步骤）")
@allure.severity(allure.severity_level.BLOCKER)
def test_tc002_visitor_login_modal_email_step(page, config):
    fav = FavoritesPage(page)
    login_page = LoginPage(page)

    with allure.step("步骤1：访客打开收藏页并展示登录弹窗"):
        fav.reset_to_guest()
        fav.navigate_to_favorites_list(config["base_url"])
        login_page.handle_cookie_popup()
        fav.ensure_email_step_login_modal(login_page)

    with allure.step("步骤2：校验邮箱步骤 UI"):
        dlg = page.get_by_role("dialog")
        expect(dlg).to_be_visible()
        expect(dlg.get_by_text("Your data is protected")).to_be_visible()
        expect(dlg.get_by_text("Welcome to OK.com")).to_be_visible()
        expect(dlg.get_by_text("AE", exact=True)).to_be_visible()
        expect(dlg.get_by_text("Free to post. Easy to find.")).to_be_visible()
        expect(
            dlg.get_by_role("textbox", name="Email or phone number")
        ).to_be_visible()
        expect(dlg.get_by_role("button", name="Continue")).to_be_disabled()
        expect(dlg.get_by_text("OR", exact=True)).to_be_visible()
        expect(dlg.get_by_role("img", name="google")).to_be_visible()
        expect(dlg.get_by_role("img", name="facebook")).to_be_visible()
        expect(dlg.get_by_role("img", name="apple")).to_be_visible()
        expect(dlg.get_by_text(re.compile(r"Terms of Use", re.I))).to_be_visible()
        expect(dlg.get_by_text(re.compile(r"Privacy Policy", re.I))).to_be_visible()


@pytest.mark.case_id_ae_favorites_003
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.ui
@pytest.mark.ae
@pytest.mark.favorite
@allure.feature("OK.com 收藏页")
@allure.story("访问控制与登录流程")
@allure.title("TC003: 输入邮箱后 Continue 启用")
@allure.severity(allure.severity_level.BLOCKER)
def test_tc003_continue_enabled_after_email(page, config):
    fav = FavoritesPage(page)
    login_page = LoginPage(page)
    email = config["test_account"]["username"]

    with allure.step("步骤1：打开登录弹窗并输入邮箱"):
        fav.reset_to_guest()
        fav.navigate_to_favorites_list(config["base_url"])
        login_page.handle_cookie_popup()
        fav.ensure_email_step_login_modal(login_page)
        login_page.input_email(email)

    with allure.step("步骤2：Continue 可点击"):
        btn = page.get_by_role("button", name="Continue")
        expect(btn).to_be_enabled()


@pytest.mark.case_id_ae_favorites_004
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.ui
@pytest.mark.ae
@pytest.mark.favorite
@allure.feature("OK.com 收藏页")
@allure.story("访问控制与登录流程")
@allure.title("TC004: Continue 进入密码步骤")
@allure.severity(allure.severity_level.BLOCKER)
def test_tc004_password_step_after_continue(page, config):
    fav = FavoritesPage(page)
    login_page = LoginPage(page)
    email = config["test_account"]["username"]

    with allure.step("步骤1：邮箱步骤并点击 Continue"):
        fav.reset_to_guest()
        fav.navigate_to_favorites_list(config["base_url"])
        login_page.handle_cookie_popup()
        fav.ensure_email_step_login_modal(login_page)
        login_page.input_email(email)
        login_page.click_continue_button()

    with allure.step("步骤2：密码步骤 UI"):
        expect(page.get_by_text("Welcome back!")).to_be_visible()
        expect(
            page.get_by_text("Enter your password to log in to your account.")
        ).to_be_visible()
        expect(page.get_by_text(email).first).to_be_visible()
        expect(page.get_by_role("textbox", name="Enter password")).to_be_visible()
        expect(page.get_by_text("Forgot your password?")).to_be_visible()
        expect(page.get_by_role("button", name="Log in")).to_be_disabled()


@pytest.mark.case_id_ae_favorites_005
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.ui
@pytest.mark.ae
@pytest.mark.favorite
@allure.feature("OK.com 收藏页")
@allure.story("访问控制与登录流程")
@allure.title("TC005: 输入密码后 Log in 启用且为密码框")
@allure.severity(allure.severity_level.BLOCKER)
def test_tc005_login_enabled_after_password(page, config):
    fav = FavoritesPage(page)
    login_page = LoginPage(page)
    email = config["test_account"]["username"]
    password = config["test_account"]["password"]

    with allure.step("步骤1：进入密码步骤"):
        fav.reset_to_guest()
        fav.navigate_to_favorites_list(config["base_url"])
        login_page.handle_cookie_popup()
        fav.ensure_email_step_login_modal(login_page)
        login_page.input_email(email)
        login_page.click_continue_button()
        expect(page.get_by_text("Welcome back!")).to_be_visible()

    with allure.step("步骤2：输入密码并校验按钮与 input type"):
        pwd = page.get_by_role("textbox", name="Enter password")
        expect(pwd).to_have_attribute("type", "password")
        login_page.input_password(password)
        expect(page.get_by_role("button", name="Log in")).to_be_enabled()
