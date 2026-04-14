"""
阿联酋站 - 二手空调商品详情页聊天功能测试

测试站点：AE (https://ae.58v5.cn)
测试角色：Buyer（买家）
测试目标：验证二手空调商品详情页 Contact 按钮 → 聊天页面的完整交互链路，
         包括与AI进行多轮对话，询问商品图片、成色、规格、价格、配送等信息

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
_DEFAULT_PRODUCT_URL = (
    "https://ae.58v5.cn/en/city-abu-dhabi/cate-air-conditioners/"
    "Hisense+1+Ton+Inverter+Split+Air+Conditioner-2034518880336068608/"
    "?from="
)

_CONFIG = {
    "site": "ae",
    "site_name": "阿联酋站",
    "role": "buyer",
    "user_name": "ae_buyer_393049273_qq",
    "base_url": "https://ae.58v5.cn",
    "product_detail_url": os.environ.get("CHAT_PRODUCT_DETAIL_URL", _DEFAULT_PRODUCT_URL),
    "test_account": {
        "username": "393049273@qq.com",
        "password": "Qa123456"
    },
    "locale": "en-AE",
    "currency": "AED",
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
        _page.wait_for_load_state("domcontentloaded", timeout=30000)
        logger.info("✅ 登录成功！")
        session_manager.save_session()
        logger.info("✓ Session 已保存")

    # ---- 导航到商品详情页 ----
    product_url = config['product_detail_url']
    try:
        _page.goto(product_url, wait_until="domcontentloaded", timeout=60000)
        _page.wait_for_timeout(3000)
        logger.info("✓ 已进入商品详情页")
    except Exception as e:
        pytest.skip(
            f"商品详情页无法访问（可能已下架），跳过所有用例。\n"
            f"URL: {product_url}\n"
            f"错误: {e}\n"
            f"提示：可通过环境变量 CHAT_PRODUCT_DETAIL_URL 指定有效的商品详情页 URL"
        )

    # ---- 点击 Contact 按钮 ----
    chat_page = AiChatJobPage(_page)
    try:
        contact_button = _page.get_by_role("button", name="Contact").first
        contact_button.click()
        _page.wait_for_timeout(3000)
        
        # 等待聊天页面加载
        _page.wait_for_selector(
            "role=textbox[name='Input message']",
            state="visible",
            timeout=15000
        )
        logger.info("✅ 聊天页面已打开，所有用例将共享此页面")
    except Exception as e:
        pytest.skip(f"无法打开聊天页面: {e}")

    yield _page

    # 标记为已释放
    browser_manager.mark_released()
    
    if os.environ.get("KEEP_BROWSER_OPEN", "").lower() not in ("1", "true", "yes"):
        browser_manager.close_browser(_page)


# ============================================================
# 模块一：进入聊天页面
# ============================================================

@pytest.fixture(scope="module")
def config():
    """返回测试配置"""
    return _CONFIG


@pytest.mark.case_id_chat_marketplace_contact01
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.chat
@pytest.mark.ae
@allure.feature("OK")
@allure.story("聊天功能 - 二手空调商品详情页进入聊天")
@allure.title("点击商品详情页 Contact 按钮应跳转到聊天页面")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证已登录用户在二手空调商品详情页点击右侧 Contact 按钮后，能跳转到对应的聊天页面")
def test_contact_button_navigates_to_chat(page, config):
    """TC001: 点击 Contact 按钮跳转聊天页面"""
    chat_page = AiChatJobPage(page)

    with allure.step("验证当前页面 URL 为聊天页面"):
        current_url = chat_page.get_current_url()
        assert "chat" in current_url.lower(), \
            f"未在聊天页面，当前 URL: {current_url}"
        logger.info(f"✅ 已跳转到聊天页面，URL: {current_url}")


# ============================================================
# 模块二：AI 对话 - 回答AI询问（预算、用途等）
# ============================================================

@pytest.mark.case_id_chat_marketplace_budget02
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.chat
@pytest.mark.ae
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（回答AI询问）")
@allure.title("回答预算范围，AI应正确理解")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证用户回答预算范围后，AI能理解并继续引导对话")
def test_answer_budget(page, config):
    """TC002: 回答预算范围"""
    chat_page = AiChatJobPage(page)
    message = "My budget is around 500-800 AED."

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
        logger.info("✅ AI 已回复预算问题")


@pytest.mark.case_id_chat_marketplace_usage03
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.chat
@pytest.mark.ae
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（回答AI询问）")
@allure.title("回答用途需求，AI应正确理解")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户回答使用场所后，AI能理解并继续引导对话")
def test_answer_usage(page, config):
    """TC003: 回答用途需求"""
    chat_page = AiChatJobPage(page)
    message = "I need it for my bedroom, around 15-20 square meters."

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
        logger.info("✅ AI 已回复用途问题")


# ============================================================
# 模块三：提供联系方式
# ============================================================

@pytest.mark.case_id_chat_marketplace_contact_email04
@pytest.mark.regression
@pytest.mark.p0
@pytest.mark.chat
@pytest.mark.ae
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（联系方式交换）")
@allure.title("提供邮箱地址，AI应正确接收")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证用户提供邮箱地址后，AI能正确接收并回复")
def test_provide_email(page, config):
    """TC004: 提供邮箱地址"""
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
        logger.info("✅ AI 已接收邮箱")


@pytest.mark.case_id_chat_marketplace_contact_phone05
@pytest.mark.regression
@pytest.mark.p0
@pytest.mark.chat
@pytest.mark.ae
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（联系方式交换）")
@allure.title("提供电话号码，AI应正确接收")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证用户提供电话号码后，AI能正确接收并回复")
def test_provide_phone(page, config):
    """TC005: 提供电话号码"""
    chat_page = AiChatJobPage(page)
    message = "My phone number is +971 50 123 4567, you can call me anytime."

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
        logger.info("✅ AI 已接收电话号码")


# ============================================================
# 模块四：主动询问商品信息
# ============================================================

@pytest.mark.case_id_chat_marketplace_photos06
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.chat
@pytest.mark.ae
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（商品信息）")
@allure.title("询问商品图片，AI应正确回复")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户询问是否有更多商品图片后，AI能正确回复")
def test_ask_product_photos(page, config):
    """TC006: 询问商品图片"""
    chat_page = AiChatJobPage(page)
    message = "Do you have more photos of the air conditioner? Can I see the back and sides?"

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
        logger.info("✅ AI 已回复商品图片问题")


@pytest.mark.case_id_chat_marketplace_condition07
@pytest.mark.regression
@pytest.mark.p0
@pytest.mark.chat
@pytest.mark.ae
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（商品信息）")
@allure.title("询问物品成色，AI应正确回复")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证用户询问物品成色后，AI能基于商品信息正确回复")
def test_ask_condition(page, config):
    """TC007: 询问物品成色"""
    chat_page = AiChatJobPage(page)
    message = "What is the condition of this air conditioner? Any scratches or damages?"

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
        logger.info("✅ AI 已回复物品成色问题")


@pytest.mark.case_id_chat_marketplace_specs08
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.chat
@pytest.mark.ae
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（商品信息）")
@allure.title("询问规格大小，AI应正确回复")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户询问商品规格大小后，AI能基于商品信息正确回复")
def test_ask_specifications(page, config):
    """TC008: 询问规格大小"""
    chat_page = AiChatJobPage(page)
    message = "What are the exact specifications? Dimensions and cooling capacity?"

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
        logger.info("✅ AI 已回复规格大小问题")


@pytest.mark.case_id_chat_marketplace_quantity09
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.chat
@pytest.mark.ae
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（商品信息）")
@allure.title("询问商品数量，AI应正确回复")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户询问商品数量后，AI能正确回复")
def test_ask_quantity(page, config):
    """TC009: 询问商品数量"""
    chat_page = AiChatJobPage(page)
    message = "How many units do you have available? Can I buy multiple units?"

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
        logger.info("✅ AI 已回复数量问题")


@pytest.mark.case_id_chat_marketplace_working10
@pytest.mark.regression
@pytest.mark.p0
@pytest.mark.chat
@pytest.mark.ae
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（商品信息）")
@allure.title("询问是否可用，AI应正确回复")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证用户询问商品是否可用/是否正常工作后，AI能正确回复")
def test_ask_working_condition(page, config):
    """TC010: 询问是否可用"""
    chat_page = AiChatJobPage(page)
    message = "Is the air conditioner still working properly? Any issues with cooling?"

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
        logger.info("✅ AI 已回复可用性问题")


@pytest.mark.case_id_chat_marketplace_usage_duration11
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.chat
@pytest.mark.ae
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（商品信息）")
@allure.title("询问已使用时长，AI应正确回复")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户询问商品使用时长后，AI能正确回复")
def test_ask_usage_duration(page, config):
    """TC011: 询问已使用时长"""
    chat_page = AiChatJobPage(page)
    message = "How long have you been using this air conditioner? How old is it?"

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
        logger.info("✅ AI 已回复使用时长问题")


@pytest.mark.case_id_chat_marketplace_wholesale12
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.chat
@pytest.mark.ae
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（商品信息）")
@allure.title("询问是否批发/零售，AI应正确回复")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户询问是否支持批发后，AI能正确回复")
def test_ask_wholesale_retail(page, config):
    """TC012: 询问是否批发/零售"""
    chat_page = AiChatJobPage(page)
    message = "Do you offer wholesale pricing? I might need multiple units for my business."

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
        logger.info("✅ AI 已回复批发零售问题")


# ============================================================
# 模块五：价格协商
# ============================================================

@pytest.mark.case_id_chat_marketplace_price13
@pytest.mark.regression
@pytest.mark.p0
@pytest.mark.chat
@pytest.mark.ae
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（价格协商）")
@allure.title("询问价格并尝试砍价，AI应正确回复")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证用户询问价格并提出砍价后，AI能正确回复")
def test_negotiate_price(page, config):
    """TC013: 询问价格并砍价"""
    chat_page = AiChatJobPage(page)
    message = "Can you offer a better price? Maybe 600 AED including delivery?"

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
        logger.info("✅ AI 已回复砍价问题")


@pytest.mark.case_id_chat_marketplace_free_shipping14
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.chat
@pytest.mark.ae
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（价格协商）")
@allure.title("询问是否包邮，AI应正确回复")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户询问是否包邮后，AI能正确回复")
def test_ask_free_shipping(page, config):
    """TC014: 询问是否包邮"""
    chat_page = AiChatJobPage(page)
    message = "Is delivery free? Or how much would shipping cost to my area?"

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
        logger.info("✅ AI 已回复包邮问题")


# ============================================================
# 模块六：交易方式
# ============================================================

@pytest.mark.case_id_chat_marketplace_trade15
@pytest.mark.regression
@pytest.mark.p2
@pytest.mark.chat
@pytest.mark.ae
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（交易方式）")
@allure.title("询问是否可以置换，AI应正确回复")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户询问是否可用旧物置换后，AI能正确回复")
def test_ask_trade_option(page, config):
    """TC015: 询问是否可用洗衣机置换"""
    chat_page = AiChatJobPage(page)
    message = "Would you be interested in a trade? I have a washing machine I could exchange."

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
        logger.info("✅ AI 已回复置换问题")


@pytest.mark.case_id_chat_marketplace_location16
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.chat
@pytest.mark.ae
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（交易方式）")
@allure.title("询问地理位置，AI应正确回复")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户询问商品所在位置后，AI能正确回复")
def test_ask_location(page, config):
    """TC016: 询问地理位置"""
    chat_page = AiChatJobPage(page)
    message = "Where exactly are you located in Abu Dhabi? Which area?"

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


@pytest.mark.case_id_chat_marketplace_viewing17
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.chat
@pytest.mark.ae
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（交易方式）")
@allure.title("询问看货方式，AI应正确回复")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户询问如何查看商品后，AI能正确回复")
def test_ask_viewing_method(page, config):
    """TC017: 询问看货方式"""
    chat_page = AiChatJobPage(page)
    message = "Can I come to see the air conditioner before buying? When is a good time?"

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
        logger.info("✅ AI 已回复看货方式问题")


@pytest.mark.case_id_chat_marketplace_payment18
@pytest.mark.regression
@pytest.mark.p0
@pytest.mark.chat
@pytest.mark.ae
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（交易方式）")
@allure.title("询问付款方式，AI应正确回复")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证用户询问付款方式后，AI能正确回复")
def test_ask_payment_method(page, config):
    """TC018: 询问付款方式"""
    chat_page = AiChatJobPage(page)
    message = "What payment methods do you accept? Cash, bank transfer, or online payment?"

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


@pytest.mark.case_id_chat_marketplace_delivery19
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.chat
@pytest.mark.ae
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（交易方式）")
@allure.title("询问邮寄方式，AI应正确回复")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户询问邮寄/配送方式后，AI能正确回复")
def test_ask_delivery_method(page, config):
    """TC019: 询问邮寄方式"""
    chat_page = AiChatJobPage(page)
    message = "How will you deliver the air conditioner? Do you offer installation?"

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
        logger.info("✅ AI 已回复邮寄方式问题")


# ============================================================
# 模块七：比价和综合
# ============================================================

@pytest.mark.case_id_chat_marketplace_comparison20
@pytest.mark.regression
@pytest.mark.p2
@pytest.mark.chat
@pytest.mark.ae
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（比价）")
@allure.title("进行比价询问，AI应正确回复")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户提出比价问题后，AI能正确回复")
def test_ask_price_comparison(page, config):
    """TC020: 比价询问"""
    chat_page = AiChatJobPage(page)
    message = "I saw similar Hisense 1 ton AC for 650 AED. Why is yours different?"

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
        logger.info("✅ AI 已回复比价问题")


# ============================================================
# 模块八：无关问题测试
# ============================================================

@pytest.mark.case_id_chat_marketplace_irrelevant21
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.chat
@pytest.mark.ae
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（无关问题处理）")
@allure.title("询问敏感无关问题（宗教信仰），AI应合理引导或拒绝")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户询问宗教信仰等敏感无关问题后，AI能识别并做出合理回应（引导回主题或礼貌拒绝）")
def test_ask_irrelevant_religion(page, config):
    """TC021: 询问宗教信仰"""
    chat_page = AiChatJobPage(page)
    message = "What is your religious belief? Are you Muslim or Christian?"

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
# 模块九：结束对话
# ============================================================

@pytest.mark.case_id_chat_marketplace_end22
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.chat
@pytest.mark.ae
@allure.feature("OK")
@allure.story("聊天功能 - AI对话（结束对话）")
@allure.title("告知没有其他问题，AI应礼貌回应")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户表示没有其他问题后，AI能给出礼貌的结束回复")
def test_end_conversation(page, config):
    """TC022: 结束对话"""
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
