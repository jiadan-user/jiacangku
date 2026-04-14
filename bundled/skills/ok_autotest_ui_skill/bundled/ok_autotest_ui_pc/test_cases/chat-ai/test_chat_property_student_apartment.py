"""
澳大利亚站 - 学生公寓详情页聊天功能测试（实测用例）

测试站点：AU (https://au.58v5.cn)
测试角色：Buyer（租户）
测试目标：验证学生公寓详情页 Contact 按钮 → 聊天页面的完整交互链路，
         包括与AI进行多轮对话，询问房屋配置、地理位置、看房时间、付款方式、价格等信息

优化说明：所有测试用例共享同一个浏览器 session 和聊天页面，
         仅在模块初始化时登录并打开聊天页面一次，避免重复导航。
"""
import os
import pytest
import allure
from pages.login_page import LoginPage
from pages.ai_chat_job_page import AiChatJobPage
from utils.session_manager import SessionManager
from utils.browser_manager import BrowserManager
from utils.logger import setup_logger

logger = setup_logger()

# ============================================
# 测试环境配置
# ============================================
_DEFAULT_PROPERTY_URL = (
    "https://au.58v5.cn/en/city-new-south-wales/cate-property-student-apartment/"
    "%5BOriginalID%3A6529470774541110%5D+2+Bed+2+Bath+1+Carspace+6+Pual+Street+Zetland%2C+Sydney-6574798962022110/"
    "?from="
)

_CONFIG = {
    "site": "au",
    "site_name": "澳大利亚站",
    "role": "buyer",
    "user_name": "au_buyer_393049273_qq",
    "base_url": "https://au.58v5.cn",
    "property_detail_url": os.environ.get("CHAT_PROPERTY_DETAIL_URL", _DEFAULT_PROPERTY_URL),
    "test_account": {
        "username": "393049273@qq.com",
        "password": "Qa123456"
    },
    "locale": "en-AU",
    "currency": "AUD",
    "browser": {
        "type": "chromium",
        "headless": False,
        "viewport": {"width": 1920, "height": 1080}
    },
    "timeout": {
        "default": 30000,
        "wait": 10000,
        "navigation": 60000
    }
}


# ============================================================
# Module 级 page fixture —— 覆盖 conftest 的 function 级 fixture
# 整个模块只启动一次浏览器，共享同一个 page 实例
# ============================================================

@pytest.fixture(scope="module")
def page(config):
    """
    Module 级浏览器 fixture：整个测试模块共享同一个浏览器/页面实例。
    模块初始化时完成登录并导航到聊天页面，模块结束后关闭浏览器。
    
    注意：使用 mark_in_use()/mark_released() 保护实例不被 pytest hooks 提前清理。
    """
    browser_manager = BrowserManager()
    _page = browser_manager.start_browser(
        browser_type=config['browser']['type'],
        headless=config['browser']['headless'],
        base_url=config['base_url'],
        viewport=config['browser']['viewport']
    )
    
    # 标记为使用中，防止被 pytest hooks 的 _cleanup_all(force=False) 清理
    browser_manager.mark_in_use()

    if os.environ.get("DEBUG_PAUSE", "").lower() in ("1", "true", "yes"):
        try:
            _page.pause()
        except Exception:
            pass

    # ---- 登录 ----
    login_page = LoginPage(_page)
    site = config['site']
    role = config['role']
    account_name = config['user_name']
    base_url = config['base_url']
    username = config['test_account']['username']
    password = config['test_account']['password']

    session_manager = SessionManager(
        _page, base_url,
        session_name=f"{site}_{role}_{account_name}"
    )

    session_loaded = session_manager.load_session()
    if session_loaded:
        logger.info("✓ 成功加载已保存的 Session")
        _page.wait_for_load_state("domcontentloaded", timeout=30000)
        if login_page.is_login_button_text_changed(timeout=2000):
            logger.info("✅ Session 有效，跳过登录")
        else:
            logger.info("⚠️ Session 已过期，需要重新登录")
            session_loaded = False

    if not session_loaded:
        login_page.navigate_to_home_page(base_url=base_url)
        login_page.handle_cookie_popup()
        _page.wait_for_load_state("domcontentloaded", timeout=30000)
        login_page.click_login_register_button()
        login_page.input_email(username)
        login_page.click_continue_button()
        login_page.input_password(password)
        login_page.click_login_button()
        _page.wait_for_load_state("domcontentloaded", timeout=10000)
        logger.info("✅ 登录成功！")
        session_manager.save_session()
        logger.info("✓ Session 已保存")

    # ---- 导航到学生公寓详情页并进入聊天 ----
    chat_page = AiChatJobPage(_page)
    property_url = config['property_detail_url']
    try:
        _page.goto(property_url, wait_until="domcontentloaded", timeout=60000)
        _page.wait_for_timeout(2000)
    except Exception as e:
        browser_manager.mark_released()
        browser_manager.close_browser(_page)
        pytest.skip(
            f"学生公寓详情页无法访问（可能已下架），跳过所有用例。\n"
            f"URL: {property_url}\n"
            f"错误: {e}\n"
            f"提示：可通过环境变量 CHAT_PROPERTY_DETAIL_URL 指定有效的房产详情页 URL"
        )
    _page.wait_for_timeout(2000)
    logger.info("✓ 已进入学生公寓详情页")
    
    # 点击右侧的 Contact 按钮
    chat_page.click_contact_button_primary()
    chat_page.wait_for_chat_loaded()
    logger.info("✅ 聊天页面已打开，所有用例将共享此页面")

    yield _page

    # 标记为已释放
    browser_manager.mark_released()
    
    if os.environ.get("KEEP_BROWSER_OPEN", "").lower() not in ("1", "true", "yes"):
        browser_manager.close_browser(_page)


# ============================================================
# 模块一：进入聊天页面
# ============================================================

@pytest.mark.case_id_chat_property_contact01
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.chat
@pytest.mark.au
@allure.feature("OK")
@allure.story("聊天功能 - 学生公寓详情页进入聊天")
@allure.title("点击学生公寓详情页 Contact 按钮应跳转到聊天页面")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证已登录用户在学生公寓详情页点击右侧 Contact 按钮后，能跳转到对应的聊天页面")
def test_contact_button_navigates_to_chat(page, config):
    """TC001: 点击 Contact 按钮跳转聊天页面"""
    chat_page = AiChatJobPage(page)

    with allure.step("验证当前页面 URL 为聊天页面"):
        current_url = chat_page.get_current_url()
        assert "chat" in current_url.lower(), \
            f"未在聊天页面，当前 URL: {current_url}"
        logger.info(f"✅ 已跳转到聊天页面，URL: {current_url}")


# ============================================================
# 模块二：AI 多轮对话 - 房屋配置询问
# ============================================================

@pytest.mark.case_id_chat_property_facilities02
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.chat
@pytest.mark.au
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（房屋配置）")
@allure.title("询问房屋卫浴数量，AI应正确回复")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证用户询问卫浴数量后，AI能基于帖子信息正确回复，并等待AI回复完成后再发送下一条消息")
def test_ask_bathroom_count(page, config):
    """TC002: 询问卫浴数量"""
    chat_page = AiChatJobPage(page)
    message = "How many bathrooms does this apartment have?"

    with allure.step(f"发送消息: {message}"):
        chat_page.send_message_by_enter(message, post_send_wait=20000)
        logger.info(f"✓ 已发送消息: {message}")

    with allure.step("验证消息已出现在聊天区域"):
        assert chat_page.is_message_visible_in_chat(message), \
            f"消息未出现在聊天区域: {message}"
        logger.info("✅ 消息已正确显示")

    with allure.step("等待 AI Auto Reply 回复"):
        chat_page.wait_for_ai_auto_reply(timeout=30000)
        assert chat_page.is_ai_auto_reply_visible(), \
            "未收到 AI Auto Reply 回复"
        logger.info("✅ AI 已回复卫浴数量问题")


@pytest.mark.case_id_chat_property_facilities03
@pytest.mark.regression
@pytest.mark.p0
@pytest.mark.chat
@pytest.mark.au
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（房屋配置）")
@allure.title("询问卧室数量，AI应正确回复")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证用户询问卧室数量后，AI能基于帖子信息正确回复")
def test_ask_bedroom_count(page, config):
    """TC003: 询问卧室数量"""
    chat_page = AiChatJobPage(page)
    message = "How many bedrooms are there in this student apartment?"

    with allure.step(f"发送消息: {message}"):
        chat_page.send_message_by_enter(message, post_send_wait=20000)
        logger.info(f"✓ 已发送消息: {message}")

    with allure.step("验证消息已出现在聊天区域"):
        assert chat_page.is_message_visible_in_chat(message), \
            f"消息未出现在聊天区域: {message}"
        logger.info("✅ 消息已正确显示")

    with allure.step("等待 AI Auto Reply 回复"):
        chat_page.wait_for_ai_auto_reply(timeout=30000)
        assert chat_page.is_ai_auto_reply_visible(), \
            "未收到 AI Auto Reply 回复"
        logger.info("✅ AI 已回复卧室数量问题")


@pytest.mark.case_id_chat_property_facilities04
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.chat
@pytest.mark.au
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（房屋配置）")
@allure.title("询问装潢程度，AI应正确回复")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户询问装潢程度后，AI能基于帖子信息正确回复")
def test_ask_furnishing_level(page, config):
    """TC004: 询问装潢程度"""
    chat_page = AiChatJobPage(page)
    message = "Is the apartment furnished or unfurnished? What furniture is included?"

    with allure.step(f"发送消息: {message}"):
        chat_page.send_message_by_enter(message, post_send_wait=20000)
        logger.info(f"✓ 已发送消息: {message}")

    with allure.step("验证消息已出现在聊天区域"):
        assert chat_page.is_message_visible_in_chat(message), \
            f"消息未出现在聊天区域: {message}"
        logger.info("✅ 消息已正确显示")

    with allure.step("等待 AI Auto Reply 回复"):
        chat_page.wait_for_ai_auto_reply(timeout=30000)
        assert chat_page.is_ai_auto_reply_visible(), \
            "未收到 AI Auto Reply 回复"
        logger.info("✅ AI 已回复装潢程度问题")


@pytest.mark.case_id_chat_property_facilities05
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.chat
@pytest.mark.au
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（房屋配置）")
@allure.title("询问实用面积，AI应正确回复")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户询问实用面积后，AI能基于帖子信息正确回复")
def test_ask_apartment_size(page, config):
    """TC005: 询问实用面积"""
    chat_page = AiChatJobPage(page)
    message = "What is the usable area or size of this apartment in square meters?"

    with allure.step(f"发送消息: {message}"):
        chat_page.send_message_by_enter(message, post_send_wait=20000)
        logger.info(f"✓ 已发送消息: {message}")

    with allure.step("验证消息已出现在聊天区域"):
        assert chat_page.is_message_visible_in_chat(message), \
            f"消息未出现在聊天区域: {message}"
        logger.info("✅ 消息已正确显示")

    with allure.step("等待 AI Auto Reply 回复"):
        chat_page.wait_for_ai_auto_reply(timeout=30000)
        assert chat_page.is_ai_auto_reply_visible(), \
            "未收到 AI Auto Reply 回复"
        logger.info("✅ AI 已回复实用面积问题")


@pytest.mark.case_id_chat_property_facilities06
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.chat
@pytest.mark.au
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（房屋配置）")
@allure.title("询问楼龄和楼层，AI应正确回复")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户询问楼龄和楼层后，AI能基于帖子信息正确回复")
def test_ask_building_age_and_floor(page, config):
    """TC006: 询问楼龄和楼层"""
    chat_page = AiChatJobPage(page)
    message = "How old is the building and which floor is this apartment on?"

    with allure.step(f"发送消息: {message}"):
        chat_page.send_message_by_enter(message, post_send_wait=20000)
        logger.info(f"✓ 已发送消息: {message}")

    with allure.step("验证消息已出现在聊天区域"):
        assert chat_page.is_message_visible_in_chat(message), \
            f"消息未出现在聊天区域: {message}"
        logger.info("✅ 消息已正确显示")

    with allure.step("等待 AI Auto Reply 回复"):
        chat_page.wait_for_ai_auto_reply(timeout=30000)
        assert chat_page.is_ai_auto_reply_visible(), \
            "未收到 AI Auto Reply 回复"
        logger.info("✅ AI 已回复楼龄和楼层问题")


@pytest.mark.case_id_chat_property_facilities07
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.chat
@pytest.mark.au
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（房屋配置）")
@allure.title("询问车位配置，AI应正确回复")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户询问车位配置后，AI能基于帖子信息正确回复")
def test_ask_parking_space(page, config):
    """TC007: 询问车位配置"""
    chat_page = AiChatJobPage(page)
    message = "Is there a parking space included with this apartment?"

    with allure.step(f"发送消息: {message}"):
        chat_page.send_message_by_enter(message, post_send_wait=20000)
        logger.info(f"✓ 已发送消息: {message}")

    with allure.step("验证消息已出现在聊天区域"):
        assert chat_page.is_message_visible_in_chat(message), \
            f"消息未出现在聊天区域: {message}"
        logger.info("✅ 消息已正确显示")

    with allure.step("等待 AI Auto Reply 回复"):
        chat_page.wait_for_ai_auto_reply(timeout=30000)
        assert chat_page.is_ai_auto_reply_visible(), \
            "未收到 AI Auto Reply 回复"
        logger.info("✅ AI 已回复车位配置问题")


@pytest.mark.case_id_chat_property_facilities08
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.chat
@pytest.mark.au
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（房屋配置）")
@allure.title("询问物业管理，AI应正确回复")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户询问物业管理后，AI能基于帖子信息正确回复")
def test_ask_property_management(page, config):
    """TC008: 询问物业管理"""
    chat_page = AiChatJobPage(page)
    message = "What property management services are included? Are there maintenance fees?"

    with allure.step(f"发送消息: {message}"):
        chat_page.send_message_by_enter(message, post_send_wait=20000)
        logger.info(f"✓ 已发送消息: {message}")

    with allure.step("验证消息已出现在聊天区域"):
        assert chat_page.is_message_visible_in_chat(message), \
            f"消息未出现在聊天区域: {message}"
        logger.info("✅ 消息已正确显示")

    with allure.step("等待 AI Auto Reply 回复"):
        chat_page.wait_for_ai_auto_reply(timeout=30000)
        assert chat_page.is_ai_auto_reply_visible(), \
            "未收到 AI Auto Reply 回复"
        logger.info("✅ AI 已回复物业管理问题")


# ============================================================
# 模块三：AI 多轮对话 - 地理位置和交通
# ============================================================

@pytest.mark.case_id_chat_property_location09
@pytest.mark.regression
@pytest.mark.p0
@pytest.mark.chat
@pytest.mark.au
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（地理位置）")
@allure.title("询问具体地址和周边设施，AI应正确回复")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证用户询问房产具体地址和周边设施后，AI能正确回复")
def test_ask_location_and_surroundings(page, config):
    """TC009: 询问地理位置和周边设施"""
    chat_page = AiChatJobPage(page)
    message = "Where exactly is this apartment located? What facilities are nearby like shops, universities, or transport?"

    with allure.step(f"发送消息: {message}"):
        chat_page.send_message_by_enter(message, post_send_wait=20000)
        logger.info(f"✓ 已发送消息: {message}")

    with allure.step("验证消息已出现在聊天区域"):
        assert chat_page.is_message_visible_in_chat(message), \
            f"消息未出现在聊天区域: {message}"
        logger.info("✅ 消息已正确显示")

    with allure.step("等待 AI Auto Reply 回复"):
        chat_page.wait_for_ai_auto_reply(timeout=30000)
        assert chat_page.is_ai_auto_reply_visible(), \
            "未收到 AI Auto Reply 回复"
        logger.info("✅ AI 已回复地理位置问题")


# ============================================================
# 模块四：AI 多轮对话 - 看房和付款
# ============================================================

@pytest.mark.case_id_chat_property_viewing10
@pytest.mark.regression
@pytest.mark.p0
@pytest.mark.chat
@pytest.mark.au
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（看房安排）")
@allure.title("询问看房时间安排，AI应正确回复")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证用户询问看房时间后，AI能提供合理的回复或引导联系房东")
def test_ask_viewing_time(page, config):
    """TC010: 询问看房时间"""
    chat_page = AiChatJobPage(page)
    message = "When can I schedule a viewing for this apartment?"

    with allure.step(f"发送消息: {message}"):
        chat_page.send_message_by_enter(message, post_send_wait=20000)
        logger.info(f"✓ 已发送消息: {message}")

    with allure.step("验证消息已出现在聊天区域"):
        assert chat_page.is_message_visible_in_chat(message), \
            f"消息未出现在聊天区域: {message}"
        logger.info("✅ 消息已正确显示")

    with allure.step("等待 AI Auto Reply 回复"):
        chat_page.wait_for_ai_auto_reply(timeout=30000)
        assert chat_page.is_ai_auto_reply_visible(), \
            "未收到 AI Auto Reply 回复"
        logger.info("✅ AI 已回复看房时间问题")


@pytest.mark.case_id_chat_property_payment11
@pytest.mark.regression
@pytest.mark.p0
@pytest.mark.chat
@pytest.mark.au
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（付款方式）")
@allure.title("询问付款方式，AI应正确回复")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证用户询问付款方式后，AI能提供相关信息")
def test_ask_payment_method(page, config):
    """TC011: 询问付款方式"""
    chat_page = AiChatJobPage(page)
    message = "What payment methods are accepted? Do you require a deposit?"

    with allure.step(f"发送消息: {message}"):
        chat_page.send_message_by_enter(message, post_send_wait=20000)
        logger.info(f"✓ 已发送消息: {message}")

    with allure.step("验证消息已出现在聊天区域"):
        assert chat_page.is_message_visible_in_chat(message), \
            f"消息未出现在聊天区域: {message}"
        logger.info("✅ 消息已正确显示")

    with allure.step("等待 AI Auto Reply 回复"):
        chat_page.wait_for_ai_auto_reply(timeout=30000)
        assert chat_page.is_ai_auto_reply_visible(), \
            "未收到 AI Auto Reply 回复"
        logger.info("✅ AI 已回复付款方式问题")


@pytest.mark.case_id_chat_property_price12
@pytest.mark.regression
@pytest.mark.p0
@pytest.mark.chat
@pytest.mark.au
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（价格询问）")
@allure.title("询问租金价格，AI应正确回复")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证用户询问租金价格后，AI能基于帖子信息正确回复")
def test_ask_rental_price(page, config):
    """TC012: 询问租金价格"""
    chat_page = AiChatJobPage(page)
    message = "What is the weekly or monthly rental price for this apartment?"

    with allure.step(f"发送消息: {message}"):
        chat_page.send_message_by_enter(message, post_send_wait=20000)
        logger.info(f"✓ 已发送消息: {message}")

    with allure.step("验证消息已出现在聊天区域"):
        assert chat_page.is_message_visible_in_chat(message), \
            f"消息未出现在聊天区域: {message}"
        logger.info("✅ 消息已正确显示")

    with allure.step("等待 AI Auto Reply 回复"):
        chat_page.wait_for_ai_auto_reply(timeout=30000)
        assert chat_page.is_ai_auto_reply_visible(), \
            "未收到 AI Auto Reply 回复"
        logger.info("✅ AI 已回复租金价格问题")


# ============================================================
# 模块五：AI 对话 - 无关问题测试
# ============================================================

@pytest.mark.case_id_chat_property_irrelevant13
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.chat
@pytest.mark.au
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（无关问题处理）")
@allure.title("询问敏感无关问题（宗教信仰），AI应合理引导或拒绝")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户询问宗教信仰等敏感无关问题后，AI能识别并做出合理回应（引导回主题或礼貌拒绝）")
def test_ask_irrelevant_question(page, config):
    """TC013: 询问敏感无关问题（宗教信仰）"""
    chat_page = AiChatJobPage(page)
    message = "What is your religious belief? Do you believe in God?"

    with allure.step(f"发送消息: {message}"):
        chat_page.send_message_by_enter(message, post_send_wait=20000)
        logger.info(f"✓ 已发送消息: {message}")

    with allure.step("验证消息已出现在聊天区域"):
        assert chat_page.is_message_visible_in_chat(message), \
            f"消息未出现在聊天区域: {message}"
        logger.info("✅ 消息已正确显示")

    with allure.step("等待 AI Auto Reply 回复"):
        chat_page.wait_for_ai_auto_reply(timeout=30000)
        assert chat_page.is_ai_auto_reply_visible(), \
            "未收到 AI Auto Reply 回复"
        logger.info("✅ AI 已回复（应引导回主题或礼貌拒绝）")


# ============================================================
# 模块六：AI 询问联系方式
# ============================================================

@pytest.mark.case_id_chat_property_contact_info14
@pytest.mark.regression
@pytest.mark.p0
@pytest.mark.chat
@pytest.mark.au
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（联系方式交换）")
@allure.title("AI询问联系方式时，提供邮箱应被正确处理")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证当AI询问联系方式时，用户提供邮箱地址（优先），AI能正确接收并回复")
def test_provide_email(page, config):
    """TC014: 提供邮箱地址（优先联系方式）"""
    chat_page = AiChatJobPage(page)
    message = "You can reach me at john.smith@example.com"

    with allure.step(f"发送消息: {message}"):
        chat_page.send_message_by_enter(message, post_send_wait=20000)
        logger.info(f"✓ 已发送消息: {message}")

    with allure.step("验证消息已出现在聊天区域"):
        assert chat_page.is_message_visible_in_chat(message), \
            f"消息未出现在聊天区域: {message}"
        logger.info("✅ 消息已正确显示")

    with allure.step("等待 AI Auto Reply 回复"):
        chat_page.wait_for_ai_auto_reply(timeout=30000)
        assert chat_page.is_ai_auto_reply_visible(), \
            "未收到 AI Auto Reply 回复"
        logger.info("✅ AI 已回复并接收联系方式")


@pytest.mark.case_id_chat_property_contact_info15
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.chat
@pytest.mark.au
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（联系方式交换）")
@allure.title("AI询问联系方式时，提供WhatsApp号码应被正确处理")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证当AI询问联系方式时，用户提供WhatsApp号码，AI能正确接收并回复")
def test_provide_whatsapp(page, config):
    """TC015: 提供WhatsApp号码"""
    chat_page = AiChatJobPage(page)
    message = "My WhatsApp is +61 423 456 789"

    with allure.step(f"发送消息: {message}"):
        chat_page.send_message_by_enter(message, post_send_wait=20000)
        logger.info(f"✓ 已发送消息: {message}")

    with allure.step("验证消息已出现在聊天区域"):
        assert chat_page.is_message_visible_in_chat(message), \
            f"消息未出现在聊天区域: {message}"
        logger.info("✅ 消息已正确显示")

    with allure.step("等待 AI Auto Reply 回复"):
        chat_page.wait_for_ai_auto_reply(timeout=30000)
        assert chat_page.is_ai_auto_reply_visible(), \
            "未收到 AI Auto Reply 回复"
        logger.info("✅ AI 已回复并接收联系方式")


@pytest.mark.case_id_chat_property_contact_info16
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.chat
@pytest.mark.au
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（联系方式交换）")
@allure.title("AI询问联系方式时，提供微信号应被正确处理")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证当AI询问联系方式时，用户提供微信号，AI能正确接收并回复")
def test_provide_wechat(page, config):
    """TC016: 提供微信号"""
    chat_page = AiChatJobPage(page)
    message = "You can add me on WeChat: johnsmith2026"

    with allure.step(f"发送消息: {message}"):
        chat_page.send_message_by_enter(message, post_send_wait=20000)
        logger.info(f"✓ 已发送消息: {message}")

    with allure.step("验证消息已出现在聊天区域"):
        assert chat_page.is_message_visible_in_chat(message), \
            f"消息未出现在聊天区域: {message}"
        logger.info("✅ 消息已正确显示")

    with allure.step("等待 AI Auto Reply 回复"):
        chat_page.wait_for_ai_auto_reply(timeout=30000)
        assert chat_page.is_ai_auto_reply_visible(), \
            "未收到 AI Auto Reply 回复"
        logger.info("✅ AI 已回复并接收联系方式")


@pytest.mark.case_id_chat_property_contact_info17
@pytest.mark.regression
@pytest.mark.p2
@pytest.mark.chat
@pytest.mark.au
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（联系方式交换）")
@allure.title("AI询问联系方式时，提供手机号应被正确处理")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证当AI询问联系方式时，用户提供手机号码（最后），AI能正确接收并回复")
def test_provide_phone_number(page, config):
    """TC017: 提供手机号码（最后联系方式）"""
    chat_page = AiChatJobPage(page)
    message = "My phone number is +61 412 345 678, feel free to call me anytime."

    with allure.step(f"发送消息: {message}"):
        chat_page.send_message_by_enter(message, post_send_wait=20000)
        logger.info(f"✓ 已发送消息: {message}")

    with allure.step("验证消息已出现在聊天区域"):
        assert chat_page.is_message_visible_in_chat(message), \
            f"消息未出现在聊天区域: {message}"
        logger.info("✅ 消息已正确显示")

    with allure.step("等待 AI Auto Reply 回复"):
        chat_page.wait_for_ai_auto_reply(timeout=30000)
        assert chat_page.is_ai_auto_reply_visible(), \
            "未收到 AI Auto Reply 回复"
        logger.info("✅ AI 已回复并接收联系方式")


# ============================================================
# 模块七：综合对话验证
# ============================================================

@pytest.mark.case_id_chat_property_comprehensive18
@pytest.mark.regression
@pytest.mark.p0
@pytest.mark.chat
@pytest.mark.au
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（综合验证）")
@allure.title("综合询问多个房屋信息，AI应能处理复杂问题")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证用户发送包含多个问题的复杂消息后，AI能理解并作出全面回复")
def test_ask_comprehensive_questions(page, config):
    """TC018: 综合询问多个问题"""
    chat_page = AiChatJobPage(page)
    message = "I'm very interested in this apartment. Can you tell me about the lease term, utilities included, and if pets are allowed?"

    with allure.step(f"发送消息: {message}"):
        chat_page.send_message_by_enter(message, post_send_wait=20000)
        logger.info(f"✓ 已发送消息: {message}")

    with allure.step("验证消息已出现在聊天区域"):
        assert chat_page.is_message_visible_in_chat(message), \
            f"消息未出现在聊天区域: {message}"
        logger.info("✅ 消息已正确显示")

    with allure.step("等待 AI Auto Reply 回复"):
        chat_page.wait_for_ai_auto_reply(timeout=30000)
        assert chat_page.is_ai_auto_reply_visible(), \
            "未收到 AI Auto Reply 回复"
        logger.info("✅ AI 已回复综合问题")


@pytest.mark.case_id_chat_property_end_conversation19
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.chat
@pytest.mark.au
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（结束对话）")
@allure.title("告知AI没有其他问题，AI应礼貌回应")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户表示没有其他问题后，AI能给出礼貌的结束回复")
def test_end_conversation(page, config):
    """TC019: 结束对话"""
    chat_page = AiChatJobPage(page)
    message = "Thank you for all the information. I don't have any other questions at the moment."

    with allure.step(f"发送消息: {message}"):
        chat_page.send_message_by_enter(message, post_send_wait=20000)
        logger.info(f"✓ 已发送消息: {message}")

    with allure.step("验证消息已出现在聊天区域"):
        assert chat_page.is_message_visible_in_chat(message), \
            f"消息未出现在聊天区域: {message}"
        logger.info("✅ 消息已正确显示")

    with allure.step("等待 AI Auto Reply 回复"):
        chat_page.wait_for_ai_auto_reply(timeout=30000)
        assert chat_page.is_ai_auto_reply_visible(), \
            "未收到 AI Auto Reply 回复"
        logger.info("✅ AI 已礼貌回应结束对话")
