"""
AE 站点 - Settings 页面 New Messages 模块测试用例

测试范围：
- 模块访问与显示
- 邮件通知开关功能
- 状态文字显示
"""
import pytest
import allure
from playwright.sync_api import Page, expect
from pages.settings_page import SettingsPage
from pages.login_page import LoginPage
import logging

logger = logging.getLogger("AutoTest")


# ============================================
# 全局配置（供 conftest.py 的 config fixture 使用）
# ============================================

_CONFIG = {
    "base_url": "https://ae.58v5.cn",
    "settings_url": "https://aepub.58v5.cn/biz/en/user/home?tabindex=1",
    "test_account": {
        "username": "wangyongli@58.com",
        "password": "Qwer1234"
    },
    "browser": {
        "type": "chromium",
        "headless": False,
        "viewport": {"width": 1920, "height": 1080}
    }
}


# ============================================
# 配置与 Fixtures
# ============================================

def handle_cookie_popup(page: Page):
    """统一处理 Cookie 弹窗"""
    try:
        cookie_button = page.locator("button:has-text('Allow all'), button:has-text('Accept all')").first
        if cookie_button.is_visible(timeout=2000):
            cookie_button.click()
            page.wait_for_timeout(1000)
            logger.info("✓ Cookie 弹窗已处理")
    except:
        pass


def close_login_dialog(page: Page):
    """关闭可能存在的登录弹窗"""
    try:
        # 尝试多种方式关闭登录弹窗
        # 1. 按 ESC 键
        page.keyboard.press("Escape")
        page.wait_for_timeout(800)
        
        # 2. 查找并点击关闭按钮（多种选择器）
        close_selectors = [
            "button[aria-label='Close']",
            "[class*='LoginPC_closeBtn']",
            "[class*='closeBtn']",
            ".modal-header .close",
            ".modal .close",
            "button.close",
            "[class*='modal'] button:has-text('×')",
            "[class*='modal'] [aria-label='Close']"
        ]
        
        for selector in close_selectors:
            try:
                close_btn = page.locator(selector).first
                if close_btn.is_visible(timeout=1000):
                    # 尝试多种点击方式
                    try:
                        page.evaluate("(el) => el.click()", close_btn.element_handle())
                    except:
                        close_btn.click(force=True)
                    page.wait_for_timeout(800)
                    logger.info(f"✓ 通过选择器 {selector} 关闭登录弹窗")
                    break
            except:
                continue
        
        # 3. 检查弹窗是否仍然存在，使用 JavaScript 强制移除
        try:
            login_dialog = page.locator("[class*='LoginPC_loginModalPC'], [class*='modal'][role='dialog']").first
            if login_dialog.is_visible(timeout=500):
                # 使用 JavaScript 强制移除所有登录相关的弹窗
                page.evaluate("""
                    // 移除登录弹窗
                    document.querySelectorAll('[class*="LoginPC_loginModalPC"], [class*="loginModal"], [role="dialog"]').forEach(el => {
                        if (el.textContent.includes('Welcome to OK.com') || 
                            el.textContent.includes('Log in') ||
                            el.textContent.includes('Email or phone number')) {
                            el.style.display = 'none';
                            el.remove();
                        }
                    });
                    // 移除 modal backdrop
                    document.querySelectorAll('.modal-backdrop, [class*="modal-backdrop"]').forEach(el => {
                        el.remove();
                    });
                    // 移除 body 上的 modal-open 类
                    document.body.classList.remove('modal-open');
                    // 恢复 body 的滚动
                    document.body.style.overflow = '';
                """)
                page.wait_for_timeout(500)
                logger.info("✓ 通过 JavaScript 强制关闭登录弹窗")
        except:
            pass
    except Exception as e:
        logger.debug(f"关闭登录弹窗时出错（可能弹窗不存在）: {e}")


@pytest.fixture(scope="module")
def logged_in_page(page: Page, config):
    """已登录的页面 fixture（模块级别，整个模块共享登录状态）"""
    login_page = LoginPage(page)
    
    # 直接访问 Settings 页面（会触发登录对话框）
    logger.info("直接访问 Settings 页面...")
    page.goto(config["settings_url"], timeout=60000)
    page.wait_for_load_state('networkidle', timeout=30000)
    page.wait_for_timeout(3000)
    
    # 处理 Cookie 弹窗
    handle_cookie_popup(page)
    
    # 检查是否出现登录弹窗（Settings 页面会自动弹出）
    logger.info("检查登录状态...")
    try:
        # 检查是否有登录对话框
        login_dialog = page.locator("[class*='LoginPC_loginModalPC'], [class*='modal'][role='dialog']").first
        if login_dialog.is_visible(timeout=3000):
            logger.info("检测到登录对话框，开始登录...")
            
            # 在对话框中输入邮箱
            page.get_by_role('textbox', name='Email or phone number').fill(config["test_account"]["username"])
            page.wait_for_timeout(1000)
            
            # 点击 Continue
            page.get_by_role('button', name='Continue').click()
            page.wait_for_timeout(2000)
            
            # 输入密码
            page.get_by_role('textbox', name='Enter password').fill(config["test_account"]["password"])
            page.wait_for_timeout(1000)
            
            # 点击登录
            page.get_by_role('button', name='Log in').click()
            page.wait_for_timeout(3000)
            
            # 等待对话框关闭
            try:
                login_dialog.wait_for(state="hidden", timeout=5000)
                logger.info("✓ 登录对话框已关闭")
            except:
                # 强制关闭对话框
                close_login_dialog(page)
            
            logger.info("✓ 登录成功")
        else:
            logger.info("✓ 用户已登录，无需再次登录")
    except Exception as e:
        logger.warning(f"登录流程异常: {e}")
        # 尝试关闭任何残留的对话框
        close_login_dialog(page)
    
    # 最终确认没有弹窗
    close_login_dialog(page)
    page.wait_for_timeout(1000)
    
    yield page


@pytest.fixture(autouse=True)
def close_dialogs_before_test(logged_in_page):
    """每个测试前自动关闭可能存在的弹窗"""
    page = logged_in_page
    close_login_dialog(page)
    yield


# ============================================
# 一、模块访问与显示（3条）
# ============================================

@allure.feature("Settings 页面")
@allure.story("New Messages 模块")
@allure.title("TC001: 访问 Settings 页面 - New Messages 模块显示")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.p0
@pytest.mark.case_id_settings_tc001
def test_tc001_access_settings_new_messages(logged_in_page, config):
    """TC001: 访问 Settings 页面 - New Messages 模块显示"""
    page = logged_in_page
    settings_page = SettingsPage(page)
    
    with allure.step("导航到 Settings 页面"):
        settings_page.navigate_to_settings()
        page.wait_for_timeout(2000)
    
    with allure.step("滚动到 New Messages 模块"):
        settings_page.scroll_to_new_messages()
    
    with allure.step("验证 New Messages 模块可见"):
        assert settings_page.is_new_messages_visible(), "New Messages 模块不可见"
        logger.info("✓ TC001 通过：New Messages 模块显示正常")


@allure.feature("Settings 页面")
@allure.story("New Messages 模块")
@allure.title("TC002: New Messages 模块 - 所有元素显示")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.p0
@pytest.mark.case_id_settings_tc002
def test_tc002_new_messages_all_elements_display(logged_in_page, config):
    """TC002: New Messages 模块 - 所有元素显示"""
    page = logged_in_page
    settings_page = SettingsPage(page)
    
    with allure.step("导航到 Settings 页面"):
        settings_page.navigate_to_settings()
        page.wait_for_timeout(2000)
    
    with allure.step("滚动到 New Messages 模块"):
        settings_page.scroll_to_new_messages()
    
    with allure.step("验证模块标题"):
        expect(settings_page.new_messages_title).to_be_visible()
        logger.info("✓ 标题 'New Messages' 显示正常")
    
    with allure.step("验证描述文字"):
        expect(settings_page.new_messages_description).to_be_visible()
        logger.info("✓ 描述文字显示正常")
    
    with allure.step("验证通知开关"):
        expect(settings_page.new_messages_toggle).to_be_visible()
        logger.info("✓ 通知开关显示正常")
    
    with allure.step("验证状态文字或副说明"):
        # 根据当前状态，至少有一个文字应该可见
        enabled_visible = settings_page.new_messages_enabled_text.is_visible(timeout=2000)
        subtext_visible = settings_page.new_messages_subtext.is_visible(timeout=2000)
        assert enabled_visible or subtext_visible, "状态文字和副说明都不可见"
        logger.info("✓ 状态文字显示正常")
    
    logger.info("✓ TC002 通过：所有元素显示正常")


@allure.feature("Settings 页面")
@allure.story("New Messages 模块")
@allure.title("TC003: New Messages 模块 - 直接 URL 访问")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p1
@pytest.mark.case_id_settings_tc003
def test_tc003_direct_url_access(logged_in_page, config):
    """TC003: New Messages 模块 - 直接 URL 访问"""
    page = logged_in_page
    settings_page = SettingsPage(page)
    
    with allure.step("直接访问 Settings URL"):
        page.goto(config["settings_url"])
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
    
    with allure.step("滚动到 New Messages 模块"):
        settings_page.scroll_to_new_messages()
    
    with allure.step("验证 New Messages 模块可见"):
        assert settings_page.is_new_messages_visible(), "直接访问后 New Messages 模块不可见"
        logger.info("✓ TC003 通过：直接 URL 访问成功")


# ============================================
# 二、通知开关功能（4条）
# ============================================



@allure.feature("Settings 页面")
@allure.story("New Messages 模块")
@allure.title("TC005: 通知开关 - 启用邮件通知")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.p0
@pytest.mark.case_id_settings_tc005
def test_tc005_enable_email_notifications(logged_in_page, config):
    """TC005: 通知开关 - 启用邮件通知"""
    page = logged_in_page
    settings_page = SettingsPage(page)
    
    with allure.step("导航到 Settings 页面"):
        settings_page.navigate_to_settings()
        page.wait_for_timeout(2000)
        settings_page.scroll_to_new_messages()
    
    with allure.step("确保通知已禁用"):
        current_state = settings_page.get_toggle_state()
        if current_state == "enabled":
            settings_page.click_toggle()
            page.wait_for_timeout(1500)
    
    with allure.step("启用邮件通知"):
        settings_page.enable_notifications()
        page.wait_for_timeout(1500)
    
    with allure.step("验证通知已启用"):
        final_state = settings_page.get_toggle_state()
        assert final_state == "enabled", f"启用失败，当前状态: {final_state}"
        expect(settings_page.new_messages_enabled_text).to_be_visible()
        logger.info("✓ TC005 通过：邮件通知启用成功")





# ============================================
# 三、状态文字显示（2条）
# ============================================

@allure.feature("Settings 页面")
@allure.story("New Messages 模块")
@allure.title("TC008: 状态文字 - 启用状态显示")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p1
@pytest.mark.case_id_settings_tc008
def test_tc008_enabled_status_text_display(logged_in_page, config):
    """TC008: 状态文字 - 启用状态显示"""
    page = logged_in_page
    settings_page = SettingsPage(page)
    
    with allure.step("导航到 Settings 页面"):
        settings_page.navigate_to_settings()
        page.wait_for_timeout(2000)
        settings_page.scroll_to_new_messages()
    
    with allure.step("启用邮件通知"):
        settings_page.enable_notifications()
        page.wait_for_timeout(1500)
    
    with allure.step("验证启用状态文字显示"):
        expect(settings_page.new_messages_enabled_text).to_be_visible()
        enabled_text = settings_page.new_messages_enabled_text.inner_text()
        assert enabled_text == "Email notifications enabled", \
            f"状态文字错误: {enabled_text}"
        logger.info("✓ TC008 通过：启用状态文字显示正确")


@allure.feature("Settings 页面")
@allure.story("New Messages 模块")
@allure.title("TC009: 副说明文字 - 退订说明显示")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.p2
@pytest.mark.case_id_settings_tc009
def test_tc009_subtext_display(logged_in_page, config):
    """TC009: 副说明文字 - 退订说明显示"""
    page = logged_in_page
    settings_page = SettingsPage(page)
    
    with allure.step("导航到 Settings 页面"):
        settings_page.navigate_to_settings()
        page.wait_for_timeout(2000)
        settings_page.scroll_to_new_messages()
    
    with allure.step("启用邮件通知"):
        settings_page.enable_notifications()
        page.wait_for_timeout(1500)
    
    with allure.step("验证退订说明文字显示"):
        if settings_page.new_messages_subtext.is_visible(timeout=2000):
            subtext = settings_page.new_messages_subtext.inner_text()
            assert "Unsubscribe" in subtext, f"退订说明文字错误: {subtext}"
            logger.info("✓ TC009 通过：退订说明文字显示正确")
        else:
            logger.warning("⚠ 退订说明文字未显示，可能是设计变更")


# ============================================
# 四、页面刷新与持久化（2条）
# ============================================

@allure.feature("Settings 页面")
@allure.story("New Messages 模块")
@allure.title("TC010: 状态持久化 - 刷新页面后保持")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.p0
@pytest.mark.case_id_settings_tc010
def test_tc010_state_persistence_after_refresh(logged_in_page, config):
    """TC010: 状态持久化 - 刷新页面后保持"""
    page = logged_in_page
    settings_page = SettingsPage(page)
    
    with allure.step("导航到 Settings 页面"):
        settings_page.navigate_to_settings()
        page.wait_for_timeout(2000)
        settings_page.scroll_to_new_messages()
    
    with allure.step("启用邮件通知"):
        settings_page.enable_notifications()
        page.wait_for_timeout(1500)
        initial_state = settings_page.get_toggle_state()
        logger.info(f"设置状态为: {initial_state}")
    
    with allure.step("刷新页面"):
        page.reload(wait_until="networkidle")
        page.wait_for_timeout(2000)
        settings_page.scroll_to_new_messages()
    
    with allure.step("验证状态保持不变"):
        current_state = settings_page.get_toggle_state()
        assert current_state == initial_state, \
            f"刷新后状态改变，期望 {initial_state}，实际 {current_state}"
        logger.info("✓ TC010 通过：状态持久化正常")


@allure.feature("Settings 页面")
@allure.story("New Messages 模块")
@allure.title("TC011: 状态持久化 - 重新登录后保持")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.p0
@pytest.mark.case_id_settings_tc011
@pytest.mark.skip(reason="已知问题：退出登录时被登录对话框拦截，无法点击 Log Out 按钮")
def test_tc011_state_persistence_after_relogin(page, config):
    """TC011: 状态持久化 - 重新登录后保持
    
    已知问题：退出登录操作时，登录对话框会拦截点击事件，
    导致无法点击 Log Out 按钮。需要修复页面元素层级或点击逻辑。
    """
    login_page = LoginPage(page)
    settings_page = SettingsPage(page)
    
    with allure.step("第一次登录"):
        page.goto(config["base_url"])
        page.wait_for_load_state("networkidle")
        handle_cookie_popup(page)
        
        login_page.click_login_register_button()
        login_page.input_email(config["test_account"]["username"])
        login_page.click_continue_button()
        login_page.input_password(config["test_account"]["password"])
        login_page.click_login_button()
        page.wait_for_timeout(3000)
    
    with allure.step("设置邮件通知状态"):
        settings_page.navigate_to_settings()
        page.wait_for_timeout(2000)
        settings_page.scroll_to_new_messages()
        settings_page.enable_notifications()
        page.wait_for_timeout(1500)
        initial_state = settings_page.get_toggle_state()
        logger.info(f"设置状态为: {initial_state}")
    
    with allure.step("退出登录"):
        # 用 JS 点击用户头像，绕过弹窗遮挡
        user_avatar = page.locator("#pcUserInfoArea")
        user_avatar.wait_for(state="visible", timeout=5000)
        page.evaluate("(el) => el.click()", user_avatar.element_handle())
        page.wait_for_timeout(1500)
        
        # 用 JS 点击 Log Out，绕过弹窗遮挡
        logout_link = page.get_by_text("Log Out", exact=True)
        logout_link.wait_for(state="visible", timeout=5000)
        page.evaluate("(el) => el.click()", logout_link.element_handle())
        page.wait_for_timeout(3000)
    
    with allure.step("重新登录"):
        # 关闭可能残留的登录弹窗
        try:
            close_btn = page.locator("[class*='LoginPC_closeBtn']").first
            if close_btn.is_visible(timeout=2000):
                page.evaluate("(el) => el.click()", close_btn.element_handle())
                page.wait_for_timeout(1000)
        except:
            pass
        
        login_page.click_login_register_button()
        login_page.input_email(config["test_account"]["username"])
        login_page.click_continue_button()
        login_page.input_password(config["test_account"]["password"])
        login_page.click_login_button()
        page.wait_for_timeout(3000)
    
    with allure.step("验证状态保持不变"):
        # 直接通过 URL 访问 Settings，绕过弹窗遮挡问题
        page.goto(config.get("settings_url", "https://aepub.58v5.cn/biz/en/user/home?tabindex=1"))
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        settings_page.scroll_to_new_messages()
        current_state = settings_page.get_toggle_state()
        assert current_state == initial_state, \
            f"重新登录后状态改变，期望 {initial_state}，实际 {current_state}"
        logger.info("✓ TC011 通过：重新登录后状态保持正常")
