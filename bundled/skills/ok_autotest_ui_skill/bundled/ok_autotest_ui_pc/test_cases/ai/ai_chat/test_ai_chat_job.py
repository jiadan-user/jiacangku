"""
AE站（沙特）- Jobs详情页 Contact会话发送消息 测试脚本

本脚本由 playwright-test-generator 生成
录制文档：test_cases/ai/ai_chat/ai_chat_JobDetail会话页发送消息-测试用例-20260318.md
生成时间：2026-03-19

测试站点：AE (https://ae.58v5.cn)
测试角色：Buyer（求职者）
测试目标：验证从 Jobs 详情页点击 Contact 按钮进入会话页后，
         能够发送文本消息、简历、形象照片、护照图片，
         并触发 AI Auto Reply 自动回复功能

录制发现：
- 聊天页 URL 域名：aepub.58v5.cn（ae 站）
- 点击 Contact → 弹出登录弹窗（非跳转登录页）
- 密码填入后需 Tab 触发 blur 才能激活 Log in 按钮
- 登录成功后直接跳转至聊天页
"""
import os
import sys
import pytest
import allure
from pages.login_page import LoginPage
from pages.ai_chat_job_page import AiChatJobPage
from utils.session_manager import SessionManager
from utils.logger import setup_logger
from test_cases.ai.ai_chat.conftest import _resolve_headless

logger = setup_logger()

# ============================================================
# 测试环境配置（来自录制文档「测试环境配置」）
# ============================================================
_CONFIG = {
    "site": "ae",
    "site_name": "AE站（沙特）",
    "role": "buyer",
    "user_name": "OKerAE_569ervr",
    "base_url": "https://ae.58v5.cn",
    "job_detail_url": (
        "https://ae.58v5.cn/en/city/cate-aerospace-engineering"
        "/software-architect-2034165619510861824/"
    ),
    "chat_url_pattern": "aepub.58v5.cn/biz/en/chat",
    "chat_post_id": "2034165619510861824",
    "chat_shop_id": "796393013895583552",
    "chat_shop_name": "二羊",
    "chat_post_name": "Software Architect",
    "test_account": {
        "username": "emily930920@163.com",
        "password": "Qa123456",
    },
    "test_data": {
        "resume": "test_data/images/jianli.jpg",
        "profile_photo": "test_data/images/xingxiangzhao.jpg",
        "passport": "test_data/images/huzhao.jpg",
        "text_message": "Hello, I am interested in the Software Architect position.",
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


# ============================================================
# Module 级 page fixture（整个脚本共享同一浏览器 + 登录状态）
# ============================================================

@pytest.fixture(scope="module")
def page(config):
    """
    Module 级浏览器 fixture：整个测试脚本共享同一个已登录的浏览器实例。

    登录策略（录制确认）：
    1. 先访问 Jobs 详情页，尝试加载 Session
    2. Session 有效 → 直接点击 Contact 进入聊天页
    3. Session 无效 → 点击 Contact 触发登录弹窗 → 输入邮箱/密码 → 登录后直接跳转至聊天页
    
    类前置检查（在登录前执行）：
    1. 检查雇主状态是否为 Active now → 如果是则跳过所有用例
    2. 检查当前登录用户是否为 OKerAE_569ervr → 如果不是则重新登录
    """
    from utils.browser_manager import BrowserManager

    logger.info("=" * 80)
    logger.info("【Module Setup】创建共享浏览器实例 + 类前置检查 + 登录")
    logger.info("=" * 80)

    browser_manager = BrowserManager()
    _page = browser_manager.start_browser(
        browser_type=config["browser"]["type"],
        headless=_resolve_headless(config["browser"]["headless"]),
        base_url=config["base_url"],
        viewport=config["browser"]["viewport"],
    )
    browser_manager.mark_in_use()

    login_page = LoginPage(_page)
    chat_page_setup = AiChatJobPage(_page)
    session_manager = SessionManager(
        _page,
        config["base_url"],
        session_name=f"{config['site']}_{config['role']}_{config['user_name']}",
    )

    # ========== 类前置检查 ==========
    logger.info("=" * 80)
    logger.info("【类前置检查】验证雇主状态和登录用户")
    logger.info("=" * 80)

    # ---- 访问 Jobs 详情页 ----
    with allure.step("访问 Jobs 详情页"):
        _page.goto(
            config["job_detail_url"],
            wait_until="domcontentloaded",
            timeout=config["timeout"]["navigation"],
        )
        # 尽量等待 Contact 按钮可见（JS 渲染），超时则继续（按钮可能已在 DOM 中）
        try:
            _page.wait_for_selector(
                "role=button[name='Contact']",
                state="visible",
                timeout=20000,
            )
            _page.wait_for_timeout(500)
        except Exception:
            logger.info("⚠️ Contact 按钮等待超时，继续执行（按钮可能已存在于 DOM）")
        logger.info(f"✓ 已加载 Jobs 详情页: {config['job_detail_url']}")

    # Step 1: 检查雇主状态
    # 只有雇主状态为 "Active now" 时才跳过测试
    try:
        # 使用类名定位雇主状态容器
        employer_status_elem = _page.locator("[class*='AgentCard_detailsCardUserCompany']").first
        if employer_status_elem.is_visible(timeout=5000):
            status_text = employer_status_elem.inner_text().strip()
            logger.info(f"雇主状态: {status_text}")
            
            # 只有 "Active now" 才跳过测试
            if status_text == "Active now":
                logger.warning(f"⚠️ 雇主状态为 'Active now'，跳过所有用例")
                browser_manager.close_browser()
                pytest.skip("雇主状态为 'Active now'，跳过测试")
            else:
                logger.info(f"✓ 雇主状态为 '{status_text}'，继续执行")
        else:
            logger.info("✓ 未检测到雇主状态元素，继续执行")
    except Exception as e:
        logger.info(f"✓ 雇主状态检查异常（继续执行）: {e}")

    # Step 2: 检查当前登录用户
    expected_username = "OKerAE_569ervr"
    current_username = None
    need_relogin = False

    # 先尝试加载 session
    session_loaded = session_manager.load_session()
    if session_loaded:
        _page.reload(wait_until="domcontentloaded")
        _page.wait_for_timeout(2000)
        
        # 检查用户名
        try:
            # 尝试多种可能的用户名元素选择器
            username_selectors = [
                "[class*='username']",
                "[class*='user-name']",
                "[data-testid='username']",
                "[class*='profile'] >> text=/OKer/",
                "text=/OKer\\w+/",
            ]
            for selector in username_selectors:
                try:
                    username_elem = _page.locator(selector).first
                    if username_elem.is_visible(timeout=2000):
                        current_username = username_elem.inner_text().strip()
                        logger.info(f"✓ 当前登录用户: {current_username}")
                        break
                except Exception:
                    continue
        except Exception as e:
            logger.info(f"⚠️ 无法获取当前用户名: {e}")
        
        # 判断用户名是否匹配
        if current_username and current_username != expected_username:
            logger.warning(f"⚠️ 当前用户 '{current_username}' 不是预期用户 '{expected_username}'，需要重新登录")
            need_relogin = True
            
            # 退出当前登录
            try:
                # 点击用户头像或设置
                avatar_selectors = ["[class*='avatar']", "[class*='user-icon']", "[class*='profile-icon']"]
                for selector in avatar_selectors:
                    try:
                        _page.locator(selector).first.click(timeout=3000)
                        _page.wait_for_timeout(1000)
                        break
                    except Exception:
                        continue
                
                # 点击 Logout
                _page.get_by_text("Logout", exact=False).first.click(timeout=3000)
                _page.wait_for_timeout(2000)
                logger.info("✓ 已退出当前登录")
                session_loaded = False
            except Exception as e:
                logger.info(f"⚠️ 退出登录失败，清除 session 后重新登录: {e}")
                session_loaded = False
        elif current_username == expected_username:
            logger.info(f"✅ 当前登录用户匹配 '{expected_username}'")
        else:
            logger.info("⚠️ 无法确认当前用户，将尝试登录")
            session_loaded = False

    logger.info("=" * 80)
    logger.info("【类前置检查完成】开始登录流程")
    logger.info("=" * 80)

    # ========== 正常登录流程（session 无效或需要重新登录）==========
    if not session_loaded:
        logger.info("Session 无效，开始登录流程（通过 Contact 触发登录弹窗）")

        # 录制确认：点击 Contact → 弹出登录弹窗（输入邮箱/密码）
        with allure.step("点击 Contact 触发登录弹窗"):
            # 重试点击，确保弹窗弹出（网络延迟情况下第一次点击可能未响应）
            for _attempt in range(3):
                _page.get_by_role("button", name="Contact").first.click()
                try:
                    _page.wait_for_selector(
                        "role=textbox[name='Email or phone number']",
                        state="visible",
                        timeout=10000,
                    )
                    break
                except Exception:
                    if _attempt == 2:
                        raise
                    logger.info(f"⚠️ 登录弹窗未出现，第{_attempt + 1}次重试")
                    _page.wait_for_timeout(2000)
            logger.info("✓ 登录弹窗已弹出")

        with allure.step(f"输入邮箱 {config['test_account']['username']}"):
            _page.get_by_role("textbox", name="Email or phone number").fill(
                config["test_account"]["username"]
            )
            _page.get_by_role("button", name="Continue").click()
            _page.wait_for_selector(
                "role=textbox[name='Enter password']",
                state="visible",
                timeout=15000,
            )
            logger.info("✓ 已输入邮箱并点击 Continue")

        with allure.step("输入密码并登录"):
            _page.get_by_role("textbox", name="Enter password").fill(
                config["test_account"]["password"]
            )
            # 录制确认：Tab 触发 blur，激活 Log in 按钮
            _page.keyboard.press("Tab")
            # 等待 Log in 按钮可点击（非 disabled）
            _page.wait_for_selector(
                "button:not([disabled])",
                state="visible",
                timeout=8000,
            )
            _page.get_by_role("button", name="Log in").click()
            # 等待聊天页输入框出现（跳过 wait_for_url，因为 SPA 导航不总触发 domcontentloaded）
            _page.wait_for_selector(
                "role=textbox[name='Input message']",
                state="visible",
                timeout=30000,
            )
            logger.info("✅ 登录成功，已直接进入聊天页")

        with allure.step("保存 Session"):
            session_manager.save_session()
            logger.info("✓ Session 已保存")

    else:
        # Session 有效，手动点击 Contact 进入聊天页
        with allure.step("点击 Contact 进入聊天页"):
            chat_page_setup.click_contact_button_primary()
            logger.info(f"✅ 已进入聊天页：{_page.url}")

    logger.info(f"✅ 聊天页就绪：{_page.url}")

    yield _page

    browser_manager.mark_released()
    logger.info("=" * 80)
    logger.info("【Module Teardown】关闭共享浏览器实例")
    logger.info("=" * 80)
    browser_manager.close_browser(_page)


@pytest.fixture(autouse=True)
def reset_to_chat_page(page, config):
    """每个用例执行后回到聊天页（确保下一个用例从干净状态开始）"""
    yield
    try:
        current_url = page.url
        if config["chat_url_pattern"] not in current_url:
            page.go_back(wait_until="domcontentloaded", timeout=10000)
    except Exception:
        pass


# ============================================================
# 测试类
# ============================================================

class TestJobDetailSendMessage:
    """Jobs详情页 Contact会话发送消息测试"""

    # ----------------------------------------------------------
    # TC001：从 Jobs 详情页点击 Contact 按钮进入会话页并发送文本消息
    # ----------------------------------------------------------
    @pytest.mark.case_id_ai_chat_ae_job_detail_send_01
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_chat
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("Jobs详情页会话 - 发送消息")
    @allure.title("从 Jobs 详情页点击 Contact 进入会话页并发送文本消息应成功")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description("验证已登录用户在 Jobs 详情页点击 Contact 后跳转到会话页，输入文本消息点击 Send 后消息发送成功，AI Auto Reply 自动回复。")
    def test_contact_enter_chat_and_send_text_message(self, page, config):
        """TC001: 从 Jobs 详情页进入会话页并发送文本消息"""

        # ========== Arrange ==========
        chat_page = AiChatJobPage(page)
        text_message = config["test_data"]["text_message"]

        logger.info("=" * 80)
        logger.info("TC001: 从 Jobs 详情页点击 Contact 进入会话页并发送文本消息")
        logger.info("=" * 80)

        # ========== Assert 阶段1：验证已在聊天页 ==========
        with allure.step("验证当前 URL 包含聊天页域名"):
            current_url = chat_page.get_current_url()
            assert config["chat_url_pattern"] in current_url, \
                f"未跳转到聊天页，当前 URL: {current_url}"
            logger.info(f"✓ 聊天页 URL 验证通过: {current_url}")

        with allure.step("验证 Send 按钮初始为 disabled"):
            # 确保聊天页输入框已加载
            chat_page.wait_for_chat_loaded()
            assert chat_page.is_send_button_disabled(), \
                "初始状态 Send 按钮应为 disabled，但当前可用"
            logger.info("✓ Send 按钮初始为 disabled")

        # ========== Act 阶段2：填入消息并发送 ==========
        with allure.step(f"在输入框填入文本: {text_message}"):
            chat_page.fill_message_input(text_message)
            logger.info(f"✓ 已填入消息: {text_message}")

        with allure.step("验证 Send 按钮变为可用"):
            assert chat_page.is_send_button_enabled(), \
                "填入文本后 Send 按钮仍为 disabled"
            logger.info("✓ Send 按钮已可用")

        with allure.step("点击 Send 按钮发送消息"):
            chat_page.click_send_button()
            logger.info("✓ 已点击 Send 按钮")

        # ========== Assert 阶段2：验证消息发送成功 ==========
        with allure.step("验证消息出现在聊天区域"):
            assert chat_page.is_message_visible_in_chat(text_message), \
                f"发送后消息文本未显示在聊天区域: {text_message}"
            logger.info("✓ 消息已显示在聊天区域")

        with allure.step("验证输入框已清空"):
            assert chat_page.is_input_cleared(), \
                "发送后输入框未清空"
            logger.info("✓ 输入框已清空")

        with allure.step("等待并验证 AI Auto Reply 出现"):
            chat_page.wait_for_ai_auto_reply(timeout=100000)
            assert chat_page.is_ai_auto_reply_visible(), \
                "AI Auto Reply 标签未在聊天区域出现"
            logger.info("✓ AI Auto Reply 出现")
        
        with allure.step("验证 AI Auto Reply 时间在发送时间之后"):
            assert chat_page.verify_ai_reply_after_send(), \
                "AI Auto Reply 时间未在发送消息时间之后"
            logger.info("✓ AI Auto Reply 时间验证通过")

        logger.info("✅ TC001 通过：文本消息发送成功，AI Auto Reply 响应")

    # ----------------------------------------------------------
    # TC002：在会话页发送简历（文件上传）
    # ----------------------------------------------------------
    @pytest.mark.case_id_ai_chat_ae_job_detail_send_02
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_chat
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("Jobs详情页会话 - 发送消息")
    @allure.title("在会话页上传简历文件应成功显示并触发 AI Auto Reply")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证在会话页通过隐藏文件 input 上传简历（jianli.jpg），文件消息出现在聊天区域，AI 自动回复。")
    def test_send_resume_file_in_chat(self, page, config):
        """TC002: 在会话页发送简历文件"""

        # ========== Arrange ==========
        chat_page = AiChatJobPage(page)
        resume_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            ),
            config["test_data"]["resume"],
        )

        logger.info("=" * 80)
        logger.info("TC002: 在会话页发送简历文件")
        logger.info("=" * 80)
        logger.info(f"简历路径: {resume_path}")

        assert os.path.exists(resume_path), \
            f"简历文件不存在: {resume_path}"

        # ========== Act：上传简历 ==========
        with allure.step("确认聊天页输入框可见"):
            chat_page.wait_for_chat_loaded()
            logger.info("✓ 聊天页已就绪")

        with allure.step(f"上传简历文件: {config['test_data']['resume']}"):
            chat_page.upload_image_file(resume_path)
            logger.info(f"✓ 已触发简历上传: {resume_path}")

        # ========== Assert：验证文件消息和 AI 回复 ==========
        with allure.step("验证文件消息出现在聊天区域"):
            # 等待文件上传处理（给服务端时间）
            page.wait_for_timeout(3000)
            
            # 截图用于调试
            try:
                screenshot_path = "reports/chat_after_upload_resume.png"
                page.screenshot(path=screenshot_path, timeout=60000)
                logger.info(f"📸 已截图保存到: {screenshot_path}")
            except Exception as e:
                logger.warning(f"截图失败: {e}")
            
            # 检查文件消息是否出现
            if not chat_page.is_file_message_visible(timeout=15000):
                # 失败时输出页面HTML片段用于调试
                try:
                    chat_html = page.locator("[class*='chat'], [class*='message']").first.inner_html()
                    logger.error(f"聊天区域HTML（前500字符）: {chat_html[:500]}")
                except Exception:
                    pass
                
                assert False, "上传简历后，文件消息未显示在聊天区域"
            
            logger.info("✓ 文件消息已显示在聊天区域")

        with allure.step("等待并验证 AI Auto Reply 出现"):
            chat_page.wait_for_ai_auto_reply(timeout=100000)
            assert chat_page.is_ai_auto_reply_visible(), \
                "AI Auto Reply 标签未在聊天区域出现"
            logger.info("✓ AI Auto Reply 出现")
        
        with allure.step("验证 AI Auto Reply 时间在发送时间之后"):
            assert chat_page.verify_ai_reply_after_send(), \
                "AI Auto Reply 时间未在发送消息时间之后"
            logger.info("✓ AI Auto Reply 时间验证通过")

        logger.info("✅ TC002 通过：简历发送成功，AI Auto Reply 响应")

    # ----------------------------------------------------------
    # TC003：在会话页发送形象照片（图片上传）
    # ----------------------------------------------------------
    @pytest.mark.case_id_ai_chat_ae_job_detail_send_03
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_chat
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("Jobs详情页会话 - 发送消息")
    @allure.title("在会话页上传形象照片应成功显示并触发 AI Auto Reply")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证在会话页通过隐藏 image input 上传形象照片（xingxiangzhao.jpg），图片消息以缩略图形式出现，AI 自动回复。")
    def test_send_profile_photo_in_chat(self, page, config):
        """TC003: 在会话页发送形象照片"""

        # ========== Arrange ==========
        chat_page = AiChatJobPage(page)
        photo_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            ),
            config["test_data"]["profile_photo"],
        )

        logger.info("=" * 80)
        logger.info("TC003: 在会话页发送形象照片")
        logger.info("=" * 80)
        logger.info(f"照片路径: {photo_path}")

        assert os.path.exists(photo_path), \
            f"形象照片文件不存在: {photo_path}"

        # ========== Act：上传图片 ==========
        with allure.step("确认聊天页输入框可见"):
            chat_page.wait_for_chat_loaded()
            logger.info("✓ 聊天页已就绪")

        with allure.step(f"上传形象照片: {config['test_data']['profile_photo']}"):
            chat_page.upload_image_file(photo_path)
            logger.info(f"✓ 已触发图片上传: {photo_path}")

        # ========== Assert：验证图片消息和 AI 回复 ==========
        with allure.step("验证图片消息出现在聊天区域"):
            # 等待图片上传处理
            page.wait_for_timeout(3000)
            
            # 截图用于调试
            try:
                screenshot_path = "reports/chat_after_upload_photo.png"
                page.screenshot(path=screenshot_path, timeout=60000)
                logger.info(f"📸 已截图保存到: {screenshot_path}")
            except Exception as e:
                logger.warning(f"截图失败: {e}")
            
            # 检查图片消息是否出现
            if not chat_page.is_file_message_visible(timeout=15000):
                # 失败时输出页面HTML片段
                try:
                    chat_html = page.locator("[class*='chat'], [class*='message']").first.inner_html()
                    logger.error(f"聊天区域HTML（前500字符）: {chat_html[:500]}")
                except Exception:
                    pass
                
                assert False, "上传形象照片后，图片消息未显示在聊天区域"
            
            logger.info("✓ 图片消息已显示在聊天区域")

        with allure.step("等待并验证 AI Auto Reply 出现"):
            chat_page.wait_for_ai_auto_reply(timeout=100000)
            assert chat_page.is_ai_auto_reply_visible(), \
                "AI Auto Reply 标签未在聊天区域出现"
            logger.info("✓ AI Auto Reply 出现")
        
        with allure.step("验证 AI Auto Reply 时间在发送时间之后"):
            assert chat_page.verify_ai_reply_after_send(), \
                "AI Auto Reply 时间未在发送消息时间之后"
            logger.info("✓ AI Auto Reply 时间验证通过")

        logger.info("✅ TC003 通过：形象照片发送成功，AI Auto Reply 响应")

    # ----------------------------------------------------------
    # TC004：在会话页发送护照图片（图片上传）
    # ----------------------------------------------------------
    @pytest.mark.case_id_ai_chat_ae_job_detail_send_04
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_chat
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("Jobs详情页会话 - 发送消息")
    @allure.title("在会话页上传护照图片应成功显示并触发 AI Auto Reply")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证在会话页通过隐藏 image input 上传护照图片（huzhao.jpg），图片消息以缩略图形式出现，AI 自动回复。")
    def test_send_passport_photo_in_chat(self, page, config):
        """TC004: 在会话页发送护照图片"""

        # ========== Arrange ==========
        chat_page = AiChatJobPage(page)
        passport_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            ),
            config["test_data"]["passport"],
        )

        logger.info("=" * 80)
        logger.info("TC004: 在会话页发送护照图片")
        logger.info("=" * 80)
        logger.info(f"护照图片路径: {passport_path}")

        assert os.path.exists(passport_path), \
            f"护照图片文件不存在: {passport_path}"

        # ========== Act：上传护照图片 ==========
        with allure.step("确认聊天页输入框可见"):
            chat_page.wait_for_chat_loaded()
            logger.info("✓ 聊天页已就绪")

        with allure.step(f"上传护照图片: {config['test_data']['passport']}"):
            chat_page.upload_image_file(passport_path)
            logger.info(f"✓ 已触发护照图片上传: {passport_path}")

        # ========== Assert：验证图片消息和 AI 回复 ==========
        with allure.step("验证图片消息出现在聊天区域"):
            # 等待图片上传处理
            page.wait_for_timeout(3000)
            
            # 截图用于调试
            try:
                screenshot_path = "reports/chat_after_upload_passport.png"
                page.screenshot(path=screenshot_path, timeout=60000)
                logger.info(f"📸 已截图保存到: {screenshot_path}")
            except Exception as e:
                logger.warning(f"截图失败: {e}")
            
            # 检查图片消息是否出现
            if not chat_page.is_file_message_visible(timeout=15000):
                # 失败时输出页面HTML片段
                try:
                    chat_html = page.locator("[class*='chat'], [class*='message']").first.inner_html()
                    logger.error(f"聊天区域HTML（前500字符）: {chat_html[:500]}")
                except Exception:
                    pass
                
                assert False, "上传护照图片后，图片消息未显示在聊天区域"
            
            logger.info("✓ 图片消息已显示在聊天区域")

        with allure.step("等待并验证 AI Auto Reply 出现"):
            chat_page.wait_for_ai_auto_reply(timeout=100000)
            assert chat_page.is_ai_auto_reply_visible(), \
                "AI Auto Reply 标签未在聊天区域出现"
            logger.info("✓ AI Auto Reply 出现")
        
        with allure.step("验证 AI Auto Reply 时间在发送时间之后"):
            assert chat_page.verify_ai_reply_after_send(), \
                "AI Auto Reply 时间未在发送消息时间之后"
            logger.info("✓ AI Auto Reply 时间验证通过")

        logger.info("✅ TC004 通过：护照图片发送成功，AI Auto Reply 响应")
