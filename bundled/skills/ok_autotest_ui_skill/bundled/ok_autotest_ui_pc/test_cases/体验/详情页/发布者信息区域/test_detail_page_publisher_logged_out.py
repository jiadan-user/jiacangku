"""
OK.com 详情页发布者信息区域 — 退出登录后场景（TC-PUB-012A & TC-PUB-012B）

测试基于联系历史状态的Contact交互规则：
- TC-PUB-012A：登录后点击过Contact → 退出登录 → 再次点击Contact → 引导登录
- TC-PUB-012B：登录后未点击Contact → 退出登录 → 点击Contact → 进入访客微聊

playwright-test-generator 生成 | 用例文档：OK.com-详情页发布者信息区域-测试用例-20260409.md v2.2
"""
import re

import allure
import pytest
from playwright.sync_api import expect

from pages.detail_page_publisher import DetailPagePublisher
from pages.login_page import LoginPage
from utils.logger import setup_logger
from utils.session_manager import SessionManager

logger = setup_logger()

_CONFIG = {
    "site": "ae",
    "site_name": "阿联酋站 (AE OK.com)",
    "role": "buyer",
    "user_name": "qa_buyer_ae_logout_test",
    "base_url": "https://ae.58v5.cn",
    "detail_url": (
        "https://ae.58v5.cn/en/city-abu-dhabi/cate-other-business-industrial/google-pixel-6-pro-128gb-excellent-condition-for-sale-2053750384618487810/"
    ),
    "test_account": {
        "username": "shenchang@58.com",
        "password": "123456Tt",
    },
    "test_account_012b": {  # TC-PUB-012B专用账号，避免连续登录冲突
        "username": "mamengmeng02@58.com",
        "password": "Qwer1234",
    },
    "locale": "en-US",
    "currency": "AED",
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


@allure.epic("OK.com 体验测试")
@allure.feature("详情页")
@allure.story("发布者信息区域（退出登录后）")
class TestDetailPagePublisherLoggedOut:
    @pytest.mark.case_id_pub_012a
    @pytest.mark.p0
    @pytest.mark.detail_page
    @pytest.mark.ae
    @allure.title("TC-PUB-012A: 登录后点击过Contact，退出登录后再次点击Contact引导登录")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_tc_pub_012a_clicked_contact_then_logout(self, page, config):
        login_page = LoginPage(page)
        pub = DetailPagePublisher(page)
        session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
        session_manager = SessionManager(page, config["base_url"], session_name)

        with allure.step("导航到详情页"):
            pub.goto_detail(config["detail_url"])
            login_page.handle_cookie_popup()
            # 等待页面完全稳定,避免DOM元素在hydration时被替换
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(1500)
            logger.info("✓ 已导航到详情页")

        with allure.step("在详情页上登录"):
            login_page.click_login_register_button()
            login_page.input_email(config["test_account"]["username"])
            login_page.click_continue_button()
            login_page.input_password(config["test_account"]["password"])
            login_page.click_login_button()
            page.locator("text=/OKer/").first.wait_for(state="visible", timeout=20000)
            logger.info("✓ 在详情页上登录成功")

        with allure.step("【关键】点击Contact按钮（建立联系记录）"):
            c = pub.contact_button
            c.wait_for(state="visible", timeout=15000)
            c.click()
            page.wait_for_timeout(2000)
            
            # 验证进入了微聊页面（可能是已登录微聊或chat-guest with needLogin）
            current_url_after_contact = page.url
            is_chat_page = "chat" in current_url_after_contact.lower()
            assert is_chat_page, f"点击Contact后应进入微聊页面，当前URL: {current_url_after_contact}"
            logger.info(f"✓ 已点击Contact并进入微聊页面: {current_url_after_contact}")
            
            # 返回详情页
            page.go_back()
            page.wait_for_timeout(2000)
            # 验证返回到详情页（使用Contact按钮，需要用role=button避免匹配到页脚的Contact Us）
            expect(page.get_by_role("button", name=re.compile(r"^Contact$", re.I))).to_be_visible(timeout=10000)
            logger.info("✓ 已返回详情页")

        with allure.step("在详情页上执行退出登录"):
            # 点击用户菜单
            user_menu = page.locator("text=/OKer/").first
            user_menu.click()
            page.wait_for_timeout(1000)
            
            # 点击退出登录（Sign out / Log out）
            logout_button = page.get_by_text(re.compile(r"Sign\s*out|Log\s*out", re.I))
            logout_button.wait_for(state="visible", timeout=10000)
            logout_button.click()
            
            # 等待退出完成，验证已显示 "Log in / Register"
            page.wait_for_timeout(2000)
            expect(page.get_by_text(re.compile(r"Log\s*in\s*/\s*Register", re.I))).to_be_visible(
                timeout=15000
            )
            
            # 调试：打印退出登录后的Cookie和Storage状态
            cookies = page.context.cookies()
            logger.info(f"退出登录后Cookie数量: {len(cookies)}")
            for cookie in cookies:
                logger.info(f"  Cookie: {cookie['name']} = {cookie['value'][:50] if len(cookie['value']) > 50 else cookie['value']}")
            
            # 获取localStorage和sessionStorage的详细内容
            local_storage_items = page.evaluate("() => Object.keys(localStorage)")
            session_storage_items = page.evaluate("() => Object.keys(sessionStorage)")
            logger.info(f"退出登录后localStorage项数: {len(local_storage_items)}, keys: {local_storage_items}")
            logger.info(f"退出登录后sessionStorage项数: {len(session_storage_items)}, keys: {session_storage_items}")
            
            # 特别关注是否有登录态相关的token/session
            for key in local_storage_items:
                value = page.evaluate(f"() => localStorage.getItem('{key}')")
                if any(kw in key.lower() for kw in ['token', 'session', 'auth', 'user', 'login']):
                    logger.info(f"  localStorage[{key}] = {value[:100] if isinstance(value, str) and len(value) > 100 else value}")
            
            # 验证当前仍在详情页
            current_url = page.url
            assert config["detail_url"] in current_url, f"退出登录后应仍在详情页，当前URL: {current_url}"
            logger.info(f"✓ 已在详情页上退出登录，当前为访客态，URL: {current_url}")

        with allure.step("再次点击Contact（此时应引导登录，因为曾建立过联系）"):
            c = pub.contact_button
            c.wait_for(state="visible", timeout=15000)
            c.click()

        with allure.step("验证出现登录引导（区别于从未登录或登录后未点Contact的访客）"):
            page.wait_for_timeout(3000)
            
            current_url = page.url
            logger.info(f"登录后点击过Contact，退出登录后再次点击Contact，当前URL: {current_url}")
            
            # 验证登录引导：必须是明确的登录引导，不能进入访客微聊
            # 1. 检查是否有needLogin参数（可能在chat-guest URL中）
            has_need_login_param = "needLogin=true" in current_url or "needlogin=true" in current_url.lower()
            
            # 2. 检查是否有登录弹层
            has_login_dialog = page.locator('[role="dialog"]').filter(
                has_text=re.compile(r"Welcome|Login|Sign\s*in", re.I)
            ).count() > 0
            
            # 3. 检查是否跳转到登录页面
            has_login_page = "login" in current_url.lower() or "signin" in current_url.lower()
            
            # 4. 检查是否有明确的登录表单
            has_login_form = page.get_by_role("textbox", name=re.compile("Email|Username", re.I)).count() > 0
            
            # 断言：必须有登录引导（弹层、登录页、登录表单或needLogin参数）
            has_login_guidance = has_need_login_param or has_login_dialog or has_login_page or has_login_form
            assert has_login_guidance, \
                f"应出现登录引导！登录后点击过Contact，退出登录后再次点击应引导登录。当前URL: {current_url}"
            
            logger.info(f"✓ 已验证：登录后点击过Contact，退出登录后再次点击Contact出现登录引导")
            logger.info(f"  - needLogin参数: {has_need_login_param}")
            logger.info(f"  - 登录弹层: {has_login_dialog}")
            logger.info(f"  - 登录页面: {has_login_page}")
            logger.info(f"  - 登录表单: {has_login_form}")

    @pytest.mark.case_id_pub_012b
    @pytest.mark.p1
    @pytest.mark.detail_page
    @pytest.mark.ae
    @allure.title("TC-PUB-012B: 登录后未点击Contact，退出登录后点击Contact进入访客微聊")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_tc_pub_012b_not_clicked_contact_then_logout(self, page, config):
        # 使用专用测试账号 mamengmeng02@58.com，避免与TC-PUB-012A的账号冲突
        login_page = LoginPage(page)
        pub = DetailPagePublisher(page)
        session_name = f"{config['site']}_{config['role']}_012b_mamengmeng"
        session_manager = SessionManager(page, config["base_url"], session_name)
        
        logger.info(f"👤 TC-PUB-012B 使用专用测试账号: {config['test_account_012b']['username']}")

        with allure.step("【关键】清除所有Cookie和Storage，模拟全新匿名访客"):
            # 如果在TC-PUB-012A之后执行，会继承"匿名状态下曾联系过"的Cookie标记
            # 必须清空，确保本测试是一个"从未联系过"的全新匿名访客
            page.context.clear_cookies()
            page.evaluate("() => localStorage.clear()")
            page.evaluate("() => sessionStorage.clear()")
            logger.info("✓ 已清除所有Cookie和Storage，确保是全新匿名访客状态（从未联系过）")

        with allure.step("导航到详情页"):
            pub.goto_detail(config["detail_url"])
            login_page.handle_cookie_popup()
            logger.info("✓ 已导航到详情页")

        with allure.step("在详情页上登录（使用专用账号mamengmeng02）"):
            login_page.click_login_register_button()
            login_page.input_email(config["test_account_012b"]["username"])
            login_page.click_continue_button()
            login_page.input_password(config["test_account_012b"]["password"])
            login_page.click_login_button()
            page.locator("text=/OKer/").first.wait_for(state="visible", timeout=20000)
            logger.info("✓ 在详情页上登录成功（使用专用账号mamengmeng02）")

        with allure.step("【关键】不点击Contact按钮（未建立联系记录）"):
            # 验证Contact按钮可见，但故意不点击
            c = pub.contact_button
            c.wait_for(state="visible", timeout=15000)
            logger.info("✓ Contact按钮可见，但未点击（保持无联系记录状态）")

        with allure.step("在详情页上执行退出登录"):
            user_menu = page.locator("text=/OKer/").first
            user_menu.click()
            page.wait_for_timeout(1000)
            
            logout_button = page.get_by_text(re.compile(r"Sign\s*out|Log\s*out", re.I))
            logout_button.wait_for(state="visible", timeout=10000)
            logout_button.click()
            
            page.wait_for_timeout(2000)
            expect(page.get_by_text(re.compile(r"Log\s*in\s*/\s*Register", re.I))).to_be_visible(
                timeout=15000
            )
            
            current_url = page.url
            assert config["detail_url"] in current_url, f"退出登录后应仍在详情页，当前URL: {current_url}"
            logger.info(f"✓ 已在详情页上退出登录，未点击过Contact，当前为访客态")

        with allure.step("点击Contact（此时应进入访客微聊，因为未建立过联系）"):
            c = pub.contact_button
            c.wait_for(state="visible", timeout=15000)
            
            # 记录点击前的URL
            url_before_click = page.url
            logger.info(f"点击Contact前URL: {url_before_click}")
            
            c.click()
            
            # 等待URL变化或弹窗出现
            page.wait_for_timeout(3000)

        with allure.step("验证进入访客微聊页（与纯访客行为一致）"):
            current_url = page.url
            logger.info(f"登录后未点击Contact，退出登录后点击Contact，当前URL: {current_url}")
            
            # 检查是否URL未变化（可能点击未生效或出现了弹窗）
            if current_url == url_before_click:
                logger.warning(f"⚠️ URL未发生变化，检查是否有登录弹窗或其他阻塞")
                
                # 检查是否出现登录引导
                has_login_dialog = page.locator('[role="dialog"]').filter(
                    has_text=re.compile(r"Welcome|Login|Sign\s*in", re.I)
                ).count() > 0
                
                has_login_form = page.get_by_role("textbox", name=re.compile("Email|Username", re.I)).count() > 0
                
                if has_login_dialog or has_login_form:
                    logger.error(f"❌ 账号 {config['test_account_012b']['username']} 历史上可能点击过Contact，出现了登录引导而非访客微聊！")
                    logger.error("建议更换一个从未使用过的测试账号，或清理该账号的历史联系记录")
                    pytest.fail(f"账号存在历史联系记录，无法验证'未点击Contact'场景。需要更换测试账号或清理历史数据。")
                else:
                    logger.error(f"❌ Contact按钮点击后URL未变化，且未检测到登录引导。可能是页面交互问题。")
                    pytest.fail(f"Contact按钮点击未生效，URL保持不变: {current_url}")
            
            # 验证进入访客微聊
            is_guest_chat = "chat-guest" in current_url.lower()
            
            # 如果不是访客微聊，检查是否是登录引导（说明账号有历史记录）
            if not is_guest_chat:
                has_need_login_param = "needLogin=true" in current_url or "needlogin=true" in current_url.lower()
                has_login_page = "login" in current_url.lower() or "signin" in current_url.lower()
                
                if has_need_login_param or has_login_page:
                    logger.error(f"❌ 账号 {config['test_account_012b']['username']} 历史上点击过Contact，出现了登录引导！")
                    logger.error("建议更换一个从未使用过的测试账号")
                    pytest.fail(f"测试账号存在历史联系记录，无法验证'未点击Contact'场景。当前URL: {current_url}")
            
            assert is_guest_chat, \
                f"应进入访客微聊页！登录后未点击Contact，退出登录后按纯访客处理。当前URL: {current_url}"
            
            # 验证页面显示访客微聊界面
            chat_interface_visible = (
                page.locator('[placeholder*="message"], [placeholder*="Message"]').count() > 0 or
                page.locator('textarea, input[type="text"]').count() > 0
            )
            assert chat_interface_visible, "应显示微聊输入界面"
            
            logger.info("✓ 已验证：登录后未点击Contact，退出登录后点击Contact进入访客微聊（与纯访客一致）")
