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
         
业务前置：当B端雇主账号在线（状态显示 "Active now"）时，
         系统不会触发 AI 代聊逻辑，此时测试用例会自动跳过

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
    1. 检查雇主状态是否为 Active now → 如果是则跳过所有用例（B端在线不触发AI代聊）
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
    # 业务逻辑：B端账号在线（"Active now"）时不触发AI代聊，因此跳过测试
    try:
        # 使用类名定位雇主状态容器
        employer_status_elem = _page.locator("[class*='AgentCard_detailsCardUserCompany']").first
        if employer_status_elem.is_visible(timeout=5000):
            status_text = employer_status_elem.inner_text().strip()
            logger.info(f"雇主状态: {status_text}")
            
            # 只有 "Active now" 才跳过测试
            if status_text == "Active now":
                logger.warning(f"⚠️ B端账号在线（状态: Active now），不触发AI代聊逻辑，跳过所有用例")
                browser_manager.close_browser()
                pytest.skip("B端账号在线，不触发AI代聊逻辑")
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
    """Jobs详情页 Contact会话发送消息测试
    
    验证逻辑优化（参考 test_ai_chat_send_message_优化总结.md）:
    - 提取公共验证方法 _verify_file_upload_and_ai_reply()
    - 统一截图逻辑 _take_screenshot_with_allure()
    - 减少重复代码，提高可维护性
    """

    @staticmethod
    def _verify_file_upload_and_ai_reply(page, chat_page, initial_count: int, file_type: str, timeout: int = 30000):
        """
        验证文件上传和 AI 自动回复的通用方法（采用M端验证方式：基于消息数量统计）
        
        Args:
            page: Playwright Page 对象
            chat_page: AiChatJobPage 对象
            initial_count: 上传前的初始消息数量
            file_type: 文件类型（用于日志）
            timeout: AI 回复等待超时时间（毫秒，默认 30 秒）
        
        Returns:
            dict: 验证结果 {
                'file_uploaded': bool,      # 文件是否上传成功
                'ai_replied': bool,         # AI 是否回复
                'new_message_count': int,   # 新增消息数量
                'final_count': int,         # 最终消息总数
                'timeout_occurred': bool,   # 是否发生超时
                'failure_reason': str       # 失败原因
            }
        """
        result = {
            'file_uploaded': False,
            'ai_replied': False,
            'new_message_count': 0,
            'final_count': 0,
            'timeout_occurred': False,
            'failure_reason': ''
        }
        
        # 1. 验证文件消息出现
        page.wait_for_timeout(3000)  # 等待上传处理
        
        if chat_page.is_file_message_visible(timeout=15000):
            result['file_uploaded'] = True
            logger.info(f"✓ {file_type}消息已显示在聊天区域")
        else:
            result['failure_reason'] = f"{file_type}消息未显示在聊天区域"
            logger.error(f"❌ {result['failure_reason']}")
            # 失败时输出HTML片段用于调试
            try:
                chat_html = page.locator("[class*='chat'], [class*='message']").first.inner_html()
                logger.error(f"聊天区域HTML（前500字符）: {chat_html[:500]}")
            except Exception:
                pass
            return result
        
        # 2. 验证 AI 自动回复（采用M端方式：消息数量变化 + AI标识）
        try:
            # 使用M端的验证方法：基于消息数量增加 + AI标识判断
            ai_replied = chat_page.verify_ai_replied_by_count(
                initial_message_count=initial_count,
                timeout=timeout
            )
            
            if ai_replied:
                result['ai_replied'] = True
                logger.info("✓ AI Auto Reply 已显示（M端验证方式）")
            else:
                result['timeout_occurred'] = True
                result['failure_reason'] = f"超时 {timeout/1000}秒 内未检测到AI回复（AI自动回复在沙箱环境响应慢，易超时）"
                logger.warning(f"⚠️ {result['failure_reason']}")
                return result
                
        except Exception as e:
            result['failure_reason'] = f"验证 AI 回复时发生异常: {e}"
            logger.error(f"❌ {result['failure_reason']}")
            return result
        
        # 3. 统计新增消息数量（M端验证方式）
        final_count = chat_page.count_messages()
        new_message_count = final_count - initial_count
        result['new_message_count'] = new_message_count
        result['final_count'] = final_count
        
        logger.info(f"✓ 消息统计: 初始={initial_count}, 最终={final_count}, 新增={new_message_count}")
        
        return result
    
    @staticmethod
    def _take_screenshot_with_allure(page, filename: str, allure_name: str = None):
        """
        截图并附加到 Allure 报告的通用方法
        
        Args:
            page: Playwright Page 对象
            filename: 截图文件名
            allure_name: Allure 报告中显示的名称（可选，默认使用 filename）
        """
        try:
            from pathlib import Path
            screenshot_dir = Path("reports/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = screenshot_dir / filename
            
            page.screenshot(path=str(screenshot_path), timeout=60000, full_page=True)
            logger.info(f"📸 已截图保存到: {screenshot_path}")
            
            # 附加到 Allure 报告
            with open(screenshot_path, 'rb') as f:
                allure.attach(
                    f.read(),
                    name=allure_name or filename,
                    attachment_type=allure.attachment_type.PNG
                )
        except Exception as e:
            logger.warning(f"截图失败: {e}")

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

        assert os.path.exists(resume_path), f"简历文件不存在: {resume_path}"

        # ========== Act：上传简历 ==========
        with allure.step("确认聊天页输入框可见"):
            chat_page.wait_for_chat_loaded()
            logger.info("✓ 聊天页已就绪")
        
        # 记录初始消息数量（M端验证方式）
        initial_count = chat_page.count_messages()
        logger.info(f"✓ 上传前消息数量: {initial_count}")

        with allure.step(f"上传简历文件: {config['test_data']['resume']}"):
            chat_page.upload_image_file(resume_path)
            logger.info(f"✓ 已触发简历上传: {resume_path}")

        # ========== Assert：验证文件消息和 AI 回复（M端验证方式）==========
        with allure.step("验证简历上传和 AI 自动回复（M端验证方式）"):
            result = self._verify_file_upload_and_ai_reply(page, chat_page, initial_count, "简历")
            
            # 截图
            self._take_screenshot_with_allure(page, "chat_after_upload_resume.png", "简历上传后截图")
            
            # 断言验证（M端方式：上传成功 + AI回复 + 消息数量增加）
            assert result['file_uploaded'], f"简历上传失败：{result.get('failure_reason', '文件消息未显示在聊天区域')}"
            
            # AI回复断言：如果是超时，给出明确的超时原因
            if not result['ai_replied']:
                failure_msg = result.get('failure_reason', 'AI Auto Reply 未出现')
                if result.get('timeout_occurred'):
                    pytest.fail(f"❌ {failure_msg}")
                else:
                    assert False, failure_msg
            
            assert result['new_message_count'] >= 2, f"新消息数量异常: {result['new_message_count']}（期望 >= 2）"
            
            logger.info(f"✅ 验证完成（M端方式）：上传成功={result['file_uploaded']}, AI回复={result['ai_replied']}, 新增消息={result['new_message_count']}")

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

        assert os.path.exists(photo_path), f"形象照片文件不存在: {photo_path}"

        # ========== Act：上传图片 ==========
        with allure.step("确认聊天页输入框可见"):
            chat_page.wait_for_chat_loaded()
            logger.info("✓ 聊天页已就绪")
        
        # 记录初始消息数量（M端验证方式）
        initial_count = chat_page.count_messages()
        logger.info(f"✓ 上传前消息数量: {initial_count}")

        with allure.step(f"上传形象照片: {config['test_data']['profile_photo']}"):
            chat_page.upload_image_file(photo_path)
            logger.info(f"✓ 已触发图片上传: {photo_path}")

        # ========== Assert：验证图片消息和 AI 回复（M端验证方式）==========
        with allure.step("验证形象照片上传和 AI 自动回复（M端验证方式）"):
            result = self._verify_file_upload_and_ai_reply(page, chat_page, initial_count, "形象照片")
            
            # 截图
            self._take_screenshot_with_allure(page, "chat_after_upload_photo.png", "形象照片上传后截图")
            
            # 断言验证（M端方式：上传成功 + AI回复 + 消息数量增加）
            assert result['file_uploaded'], f"形象照片上传失败：{result.get('failure_reason', '图片消息未显示在聊天区域')}"
            
            # AI回复断言：如果是超时，给出明确的超时原因
            if not result['ai_replied']:
                failure_msg = result.get('failure_reason', 'AI Auto Reply 未出现')
                if result.get('timeout_occurred'):
                    pytest.fail(f"❌ {failure_msg}")
                else:
                    assert False, failure_msg
            
            assert result['new_message_count'] >= 2, f"新消息数量异常: {result['new_message_count']}（期望 >= 2）"
            
            logger.info(f"✅ 验证完成（M端方式）：上传成功={result['file_uploaded']}, AI回复={result['ai_replied']}, 新增消息={result['new_message_count']}")

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

        assert os.path.exists(passport_path), f"护照图片文件不存在: {passport_path}"

        # ========== Act：上传护照图片 ==========
        with allure.step("确认聊天页输入框可见"):
            chat_page.wait_for_chat_loaded()
            logger.info("✓ 聊天页已就绪")
        
        # 记录初始消息数量（M端验证方式）
        initial_count = chat_page.count_messages()
        logger.info(f"✓ 上传前消息数量: {initial_count}")

        with allure.step(f"上传护照图片: {config['test_data']['passport']}"):
            chat_page.upload_image_file(passport_path)
            logger.info(f"✓ 已触发护照图片上传: {passport_path}")

        # ========== Assert：验证图片消息和 AI 回复（M端验证方式）==========
        with allure.step("验证护照图片上传和 AI 自动回复（M端验证方式）"):
            result = self._verify_file_upload_and_ai_reply(page, chat_page, initial_count, "护照图片")
            
            # 截图
            self._take_screenshot_with_allure(page, "chat_after_upload_passport.png", "护照图片上传后截图")
            
            # 断言验证（M端方式：上传成功 + AI回复 + 消息数量增加）
            assert result['file_uploaded'], f"护照图片上传失败：{result.get('failure_reason', '图片消息未显示在聊天区域')}"
            
            # AI回复断言：如果是超时，给出明确的超时原因
            if not result['ai_replied']:
                failure_msg = result.get('failure_reason', 'AI Auto Reply 未出现')
                if result.get('timeout_occurred'):
                    pytest.fail(f"❌ {failure_msg}")
                else:
                    assert False, failure_msg
            
            assert result['new_message_count'] >= 2, f"新消息数量异常: {result['new_message_count']}（期望 >= 2）"
            
            logger.info(f"✅ 验证完成（M端方式）：上传成功={result['file_uploaded']}, AI回复={result['ai_replied']}, 新增消息={result['new_message_count']}")

        logger.info("✅ TC004 通过：护照图片发送成功，AI Auto Reply 响应")
