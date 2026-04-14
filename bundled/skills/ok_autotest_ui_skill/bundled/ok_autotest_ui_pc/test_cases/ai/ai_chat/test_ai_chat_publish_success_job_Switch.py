"""
AE站 - Job发布成功页 EasyChat AI开关 测试脚本

本脚本由 playwright-test-generator 生成
录制文档：test_cases/ai/ai_chat/ai_chat_发布成功页 开关.md
生成时间：2026-03-18

测试站点：AE (https://aepub.58v5.cn)
测试角色：Seller (卖家)
测试目标：验证 Job 发布成功页中 EasyChat AI 自动回复开关的展示、切换、持久化行为
"""
import os
import sys
import pytest
import allure
from pages.login_page import LoginPage
from pages.ai_publish_job_success_page import AiPublishJobSuccessPage
from utils.session_manager import SessionManager
from utils.logger import setup_logger

# Linux 无 X Server 时自动 headless；也可通过 HEADLESS=true 强制开启
_IS_HEADLESS = (
    os.environ.get("HEADLESS", "").lower() == "true"
    or (sys.platform.startswith("linux") and not os.environ.get("DISPLAY"))
)

logger = setup_logger()

# ============================================================
# 测试环境配置（来自录制文档）
# ============================================================
_CONFIG = {
    "site": "ae",
    "site_name": "AE站",
    "role": "seller",
    "user_name": "ae_seller_yangyang",
    "base_url": "https://aepub.58v5.cn",
    "test_account": {
        "username": "yangyang100@58.com",
        "password": "Qa123456",
    },
    "publish_job_url": "https://aepub.58v5.cn/biz/en/publish/job?categoryId=3000",
    "locale": "en-US",
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

# 供 TC002~TC012 复用：发布成功后的 Job ID（由 TC001 写入）
_SHARED = {"success_url": ""}


# ============================================================
# Fixture：登录 + 发布 Job（module 级，仅执行一次）
# ============================================================

@pytest.fixture(scope="module")
def published_success_url(page, config):
    """
    Module 级前置：登录 → 发布一个 Job → 返回发布成功页 URL。
    TC002~TC012 均依赖此 fixture 直接导航到成功页。
    """
    login_page = LoginPage(page)
    success_page = AiPublishJobSuccessPage(page)

    site = config["site"]
    role = config["role"]
    account_name = config["user_name"]
    base_url = config["base_url"]
    username = config["test_account"]["username"]
    password = config["test_account"]["password"]

    logger.info("=" * 80)
    logger.info("Module Setup：登录 + 发布 Job → 到达发布成功页")
    logger.info("=" * 80)

    # ---- Session 复用 ----
    session_manager = SessionManager(
        page, base_url, session_name=f"{site}_{role}_{account_name}"
    )

    with allure.step("访问发布首页"):
        page.goto(f"{base_url}/biz/en/publish/front", timeout=30000, wait_until="domcontentloaded")
        page.wait_for_load_state("domcontentloaded", timeout=15000)

    session_loaded = False
    with allure.step("尝试加载已保存 Session"):
        session_loaded = session_manager.load_session()
        if session_loaded:
            page.reload()
            page.wait_for_load_state("domcontentloaded", timeout=10000)
            page.wait_for_timeout(2000)
            if not login_page.is_login_button_text_changed(timeout=2000):
                session_loaded = False

    if not session_loaded:
        with allure.step("处理 Cookie 弹窗"):
            login_page.handle_cookie_popup()
            page.wait_for_timeout(1000)

        with allure.step(f"登录账号 {username}"):
            login_page.click_login_register_button()
            login_page.input_email(username)
            login_page.click_continue_button()
            login_page.input_password(password)
            login_page.click_login_button()
            page.wait_for_load_state("domcontentloaded", timeout=10000)
            assert login_page.is_login_button_text_changed(timeout=5000), \
                "登录失败，右上角仍显示 Log in / Register"
            logger.info("✅ 登录成功")

        with allure.step("保存 Session"):
            session_manager.save_session()

    # ---- 发布 Job ----
    with allure.step("导航到 Job 发布页"):
        page.goto(config["publish_job_url"], timeout=30000, wait_until="domcontentloaded")
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(5000)
        # 等待 Job Title 输入框可见，确认进入了 Job 发布页
        page.wait_for_selector("#title", state="visible", timeout=30000)

    with allure.step("填写 Job Basics 并 Continue"):
        success_page.fill_job_basics_and_continue()

    with allure.step("填写 Job Description 并 Continue"):
        success_page.fill_job_description_and_continue(
            "We are looking for an experienced Software Architect to design "
            "and implement scalable software solutions."
        )

    with allure.step("点击 Post 发布，等待跳转成功页"):
        success_page.click_post_button()
        current_url = page.url
        assert "/publish/success" in current_url, f"未跳转到发布成功页，当前 URL: {current_url}"
        _SHARED["success_url"] = current_url
        logger.info(f"✅ 发布成功，URL: {current_url}")

    yield current_url

    logger.info("Module Teardown: 测试模块执行完成")


# ============================================================
# 测试类
# ============================================================

@pytest.mark.usefixtures("published_success_url")
class TestAiChatJobSuccessSwitch:
    """Job发布成功页 EasyChat AI开关测试"""

    # ----------------------------------------------------------
    # TC001：完整 Job 发布流程后跳转到发布成功页
    # ----------------------------------------------------------
    @pytest.mark.case_id_ai_chat_success_switch_01
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_chat
    @pytest.mark.ai_chat_job
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("Job发布成功页 - EasyChat AI开关")
    @allure.title("Job发布完成后应跳转到发布成功页并显示 EasyChat 卡片")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description(
        "验证完整 Job 发布流程（填写3步表单 → 点击 Post）后页面跳转到 /publish/success，"
        "且 EasyChat AI 开关卡片默认为 ON 状态。"
    )
    def test_job_publish_redirects_to_success_page_with_easychat_on(
        self, page, config, published_success_url
    ):
        """TC001: Job发布成功后跳转到发布成功页"""
        success_page = AiPublishJobSuccessPage(page)

        with allure.step("验证当前 URL 包含 /publish/success"):
            current_url = page.url
            assert "/publish/success" in current_url, \
                f"未跳转到发布成功页，当前 URL: {current_url}"
            logger.info(f"✓ 当前 URL: {current_url}")

        with allure.step("验证页面标题为 'Submitted successfully'"):
            heading = success_page.get_heading_text()
            assert "Submitted successfully" in heading, \
                f"页面标题不符，期望含 'Submitted successfully'，实际: '{heading}'"
            logger.info(f"✓ 页面标题: {heading}")

        with allure.step("验证 EasyChat 卡片可见"):
            assert success_page.is_card_visible(), "EasyChat 卡片不可见"
            logger.info("✓ EasyChat 卡片可见")

        with allure.step("验证 EasyChat 开关默认为 ON（蓝色）"):
            assert success_page.is_switch_on(), \
                f"开关默认状态不是 ON，当前 src: {success_page.get_switch_src()}"
            logger.info("✓ EasyChat 开关默认 ON")

    # ----------------------------------------------------------
    # TC002：发布成功页展示 EasyChat AI 开关卡片
    # ----------------------------------------------------------
    @pytest.mark.case_id_ai_chat_success_switch_02
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_chat
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("Job发布成功页 - EasyChat AI开关")
    @allure.title("发布成功页应完整展示 EasyChat AI 开关卡片内容")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "验证发布成功页中 EasyChat 卡片的标题、描述文案和开关初始状态均符合预期。"
    )
    def test_success_page_displays_easychat_card(self, page, config, published_success_url):
        """TC002: 发布成功页展示 EasyChat AI 开关卡片"""
        success_page = AiPublishJobSuccessPage(page)

        with allure.step("导航到发布成功页"):
            success_page.navigate_to_success_page(config["base_url"],
                                                   published_success_url.split("id=")[-1])

        with allure.step("验证 EasyChat 卡片可见"):
            assert success_page.is_card_visible(), "EasyChat 卡片不可见"
            logger.info("✓ EasyChat 卡片可见")

        with allure.step("验证卡片标题为 'EasyChat'"):
            title_text = success_page.get_card_title_text()
            assert "EasyChat" in title_text, \
                f"卡片标题不符，期望含 'EasyChat'，实际: '{title_text}'"
            logger.info(f"✓ 卡片标题: {title_text}")

        with allure.step("验证卡片描述文案"):
            desc_text = success_page.get_card_description_text()
            expected_desc = "AI Auto-Reply takes care of your conversations"
            assert expected_desc in desc_text, \
                f"描述文案不符，期望含 '{expected_desc}'，实际: '{desc_text}'"
            logger.info(f"✓ 卡片描述: {desc_text}")

        with allure.step("验证开关默认为 ON（蓝色）"):
            assert success_page.is_switch_on(), \
                f"开关默认状态不是 ON，当前 src: {success_page.get_switch_src()}"
            logger.info("✓ 开关默认 ON")

    # ----------------------------------------------------------
    # TC003：点击开关关闭 EasyChat
    # ----------------------------------------------------------
    @pytest.mark.case_id_ai_chat_success_switch_03
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_chat
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("Job发布成功页 - EasyChat AI开关")
    @allure.title("点击 EasyChat 开关应将其关闭（OFF）")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "验证在 EasyChat 开关处于 ON 状态时，点击开关后状态切换为 OFF（灰色），页面无跳转。"
    )
    def test_click_switch_turns_easychat_off(self, page, config, published_success_url):
        """TC003: 点击 EasyChat 开关关闭 AI 自动回复"""
        success_page = AiPublishJobSuccessPage(page)

        with allure.step("导航到发布成功页"):
            success_page.navigate_to_success_page(config["base_url"],
                                                   published_success_url.split("id=")[-1])

        with allure.step("确认开关当前为 ON"):
            assert success_page.is_switch_on(), \
                f"前置条件不满足：开关不是 ON，当前 src: {success_page.get_switch_src()}"

        with allure.step("点击开关关闭 EasyChat"):
            success_page.click_switch()
            success_page.wait_for_switch_off()

        with allure.step("验证开关状态变为 OFF（灰色）"):
            assert success_page.is_switch_off(), \
                f"开关未切换为 OFF，当前 src: {success_page.get_switch_src()}"
            logger.info("✓ 开关切换为 OFF")

        with allure.step("验证页面未跳转，仍在发布成功页"):
            assert success_page.is_success_page(), \
                f"页面发生跳转，当前 URL: {page.url}"
            logger.info("✓ 页面未跳转")

    # ----------------------------------------------------------
    # TC004：点击开关重新开启 EasyChat
    # ----------------------------------------------------------
    @pytest.mark.case_id_ai_chat_success_switch_04
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_chat
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("Job发布成功页 - EasyChat AI开关")
    @allure.title("在 EasyChat 关闭状态下点击开关应重新开启（ON）")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "验证在 EasyChat 开关处于 OFF 状态时，再次点击开关后状态切换回 ON（蓝色），页面无跳转。"
    )
    def test_click_switch_turns_easychat_on(self, page, config, published_success_url):
        """TC004: 点击 EasyChat 开关重新开启 AI 自动回复"""
        success_page = AiPublishJobSuccessPage(page)

        with allure.step("导航到发布成功页"):
            success_page.navigate_to_success_page(config["base_url"],
                                                   published_success_url.split("id=")[-1])

        with allure.step("先将开关设为 OFF"):
            if success_page.is_switch_on():
                success_page.click_switch()
                success_page.wait_for_switch_off()

        with allure.step("再次点击开关开启 EasyChat"):
            success_page.click_switch()
            success_page.wait_for_switch_on()

        with allure.step("验证开关状态变为 ON（蓝色）"):
            assert success_page.is_switch_on(), \
                f"开关未切换为 ON，当前 src: {success_page.get_switch_src()}"
            logger.info("✓ 开关切换为 ON")

        with allure.step("验证页面未跳转，仍在发布成功页"):
            assert success_page.is_success_page(), \
                f"页面发生跳转，当前 URL: {page.url}"
            logger.info("✓ 页面未跳转")

    # ----------------------------------------------------------
    # TC005：刷新后 EasyChat ON 状态持久化
    # ----------------------------------------------------------
    @pytest.mark.case_id_ai_chat_success_switch_05
    @pytest.mark.p1
    @pytest.mark.ai
    @pytest.mark.ai_chat
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("Job发布成功页 - EasyChat AI开关")
    @allure.title("刷新页面后 EasyChat ON 状态应持久化")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "验证将 EasyChat 开关设为 ON 后刷新页面，开关状态仍为 ON，"
        "说明状态已持久化到后端。"
    )
    def test_switch_on_state_persists_after_refresh(self, page, config, published_success_url):
        """TC005: 刷新发布成功页后 EasyChat ON 状态持久化"""
        success_page = AiPublishJobSuccessPage(page)

        with allure.step("导航到发布成功页"):
            success_page.navigate_to_success_page(config["base_url"],
                                                   published_success_url.split("id=")[-1])

        with allure.step("确保开关为 ON"):
            if not success_page.is_switch_on():
                success_page.click_switch()
                success_page.wait_for_switch_on()

        with allure.step("刷新页面"):
            success_page.refresh_page()

        with allure.step("验证刷新后开关仍为 ON"):
            assert success_page.is_switch_on(), \
                f"刷新后开关状态未持久化，当前 src: {success_page.get_switch_src()}"
            logger.info("✓ 刷新后 ON 状态持久化")

    # ----------------------------------------------------------
    # TC008：EasyChat 关闭状态下刷新后 OFF 持久化
    # ----------------------------------------------------------
    @pytest.mark.case_id_ai_chat_success_switch_06
    @pytest.mark.p1
    @pytest.mark.ai
    @pytest.mark.ai_chat
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("Job发布成功页 - EasyChat AI开关")
    @allure.title("刷新页面后 EasyChat OFF 状态应持久化")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "验证将 EasyChat 开关设为 OFF 后刷新页面，开关状态仍为 OFF，"
        "说明关闭状态已持久化到后端。"
    )
    def test_switch_off_state_persists_after_refresh(self, page, config, published_success_url):
        """TC008: EasyChat 关闭状态下刷新页面后状态持久化"""
        success_page = AiPublishJobSuccessPage(page)

        with allure.step("导航到发布成功页"):
            success_page.navigate_to_success_page(config["base_url"],
                                                   published_success_url.split("id=")[-1])

        with allure.step("将开关设为 OFF"):
            if success_page.is_switch_on():
                success_page.click_switch()
                success_page.wait_for_switch_off()
            assert success_page.is_switch_off(), "前置条件不满足：开关不是 OFF"

        with allure.step("刷新页面"):
            success_page.refresh_page()

        with allure.step("验证刷新后开关仍为 OFF"):
            assert success_page.is_switch_off(), \
                f"刷新后开关状态未持久化（期望 OFF），当前 src: {success_page.get_switch_src()}"
            logger.info("✓ 刷新后 OFF 状态持久化")

        with allure.step("恢复开关为 ON（清理）"):
            success_page.click_switch()
            success_page.wait_for_switch_on()
            logger.info("✓ 恢复开关为 ON")

    # ----------------------------------------------------------
    # TC010：发布成功页整体布局验证
    # ----------------------------------------------------------
    @pytest.mark.case_id_ai_chat_success_switch_08
    @pytest.mark.p1
    @pytest.mark.ui
    @pytest.mark.ai_chat
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("Job发布成功页 - EasyChat AI开关")
    @allure.title("发布成功页整体布局应符合设计规范")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description(
        "验证发布成功页各元素（标题、文案、按钮、EasyChat 卡片）均可见且无水平溢出。"
    )
    def test_success_page_layout(self, page, config, published_success_url):
        """TC010: 发布成功页整体布局验证"""
        success_page = AiPublishJobSuccessPage(page)

        with allure.step("导航到发布成功页"):
            success_page.navigate_to_success_page(config["base_url"],
                                                   published_success_url.split("id=")[-1])

        with allure.step("验证标题 'Submitted successfully' 可见"):
            assert success_page.is_visible("h1"), "页面 h1 不可见"
            assert "Submitted successfully" in success_page.get_heading_text()
            logger.info("✓ 标题可见")

        with allure.step("验证描述文案1可见"):
            assert page.locator("p", has_text="Thank you for your post").is_visible(), \
                "描述文案1不可见"
            logger.info("✓ 描述文案1可见")

        with allure.step("验证描述文案2可见"):
            assert page.get_by_text("You can view your posts in 'My Post'").is_visible(), \
                "描述文案2不可见"
            logger.info("✓ 描述文案2可见")

        with allure.step("验证 'Make another post' 按钮可见"):
            assert page.get_by_role("button", name="Make another post").is_visible(), \
                "'Make another post' 按钮不可见"
            logger.info("✓ Make another post 按钮可见")

        with allure.step("验证 'View my post' 按钮可见"):
            assert page.get_by_role("button", name="View my post").is_visible(), \
                "'View my post' 按钮不可见"
            logger.info("✓ View my post 按钮可见")

        with allure.step("验证 EasyChat 卡片可见"):
            assert success_page.is_card_visible(), "EasyChat 卡片不可见"
            logger.info("✓ EasyChat 卡片可见")

        with allure.step("验证页面无水平滚动条"):
            has_hscroll = page.evaluate(
                "() => document.documentElement.scrollWidth > document.documentElement.clientWidth"
            )
            assert not has_hscroll, "页面存在水平滚动条"
            logger.info("✓ 无水平滚动条")

    # ----------------------------------------------------------
    # TC011：EasyChat 开关 ON 状态视觉验证
    # ----------------------------------------------------------
    @pytest.mark.case_id_ai_chat_success_switch_09
    @pytest.mark.p1
    @pytest.mark.ui
    @pytest.mark.ai_chat
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("Job发布成功页 - EasyChat AI开关")
    @allure.title("EasyChat 开关 ON 状态下应显示蓝色勾选图标")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description(
        "验证 EasyChat 开关处于 ON 状态时，开关图标 src 中包含 checked 标识（蓝色勾选）。"
    )
    def test_switch_on_visual(self, page, config, published_success_url):
        """TC011: EasyChat 开关 ON 状态视觉验证"""
        success_page = AiPublishJobSuccessPage(page)

        with allure.step("导航到发布成功页"):
            success_page.navigate_to_success_page(config["base_url"],
                                                   published_success_url.split("id=")[-1])

        with allure.step("确保开关为 ON"):
            if not success_page.is_switch_on():
                success_page.click_switch()
                success_page.wait_for_switch_on()

        with allure.step("验证开关图标包含 'checked' 标识（蓝色）"):
            src = success_page.get_switch_src()
            assert "icon_switch_checked" in src, \
                f"ON 状态开关图标不含 'checked'，实际 src: {src}"
            logger.info(f"✓ ON 状态图标 src: {src}")

        with allure.step("验证 EasyChat 卡片内容仍完整可见"):
            assert success_page.is_card_visible(), "EasyChat 卡片不可见"
            logger.info("✓ 卡片内容完整可见")

    # ----------------------------------------------------------
    # TC012：EasyChat 开关 OFF 状态视觉验证
    # ----------------------------------------------------------
    @pytest.mark.case_id_ai_chat_success_switch_10
    @pytest.mark.p1
    @pytest.mark.ui
    @pytest.mark.ai_chat
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("Job发布成功页 - EasyChat AI开关")
    @allure.title("EasyChat 开关 OFF 状态下应显示灰色图标，卡片内容仍可见")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description(
        "验证 EasyChat 开关处于 OFF 状态时，开关图标为灰色，"
        "且卡片的标题与描述文案仍然可见（不消失）。"
    )
    def test_switch_off_visual(self, page, config, published_success_url):
        """TC012: EasyChat 开关 OFF 状态视觉验证"""
        success_page = AiPublishJobSuccessPage(page)

        with allure.step("导航到发布成功页"):
            success_page.navigate_to_success_page(config["base_url"],
                                                   published_success_url.split("id=")[-1])

        with allure.step("将开关设为 OFF"):
            if success_page.is_switch_on():
                success_page.click_switch()
                success_page.wait_for_switch_off()

        with allure.step("验证开关图标不含 'checked' 标识（灰色）"):
            src = success_page.get_switch_src()
            assert "icon_switch_checked" not in src, \
                f"OFF 状态开关图标仍含 'checked'，实际 src: {src}"
            assert "icon_switch" in src, \
                f"OFF 状态开关图标不含 'icon_switch'，实际 src: {src}"
            logger.info(f"✓ OFF 状态图标 src: {src}")

        with allure.step("验证 EasyChat 卡片标题仍可见"):
            assert page.get_by_text("EasyChat").is_visible(), \
                "OFF 状态下 EasyChat 标题消失"
            logger.info("✓ 卡片标题可见")

        with allure.step("验证 EasyChat 卡片描述文案仍可见"):
            assert success_page.is_visible(".ChatAiSwitch_description__cNDzd"), \
                "OFF 状态下描述文案消失"
            logger.info("✓ 卡片描述文案可见")

        with allure.step("恢复开关为 ON（清理）"):
            success_page.click_switch()
            success_page.wait_for_switch_on()
            logger.info("✓ 恢复开关为 ON")
