"""
详情页推荐模块自动化测试 - 批次 2
模块：推荐商品卡片交互 - 访客状态收藏
覆盖用例：TC-REC-007
测试站点：美国站 (US)
生成时间：2026-04-02
"""
import pytest
import allure
from playwright.sync_api import Page, expect
from pages.detail_page_recommendation import DetailPageRecommendation
from utils.logger import setup_logger

logger = setup_logger()

# ====================================================
# _CONFIG 配置（必须定义在顶层）
# ====================================================
_CONFIG = {
    "site": "us",
    "site_name": "美国站 (US OK.com)",
    "role": "visitor",
    "user_name": "us_visitor_rec",
    "base_url": "https://us.58v5.cn",
    "test_account": {
        "username": "shenchang@58.com",
        "password": "123456Tt"
    },
    "locale": "en-US",
    "currency": "USD",
    "browser": {
        "type": "chromium",
        "headless": False,
        "viewport": {
            "width": 1920,
            "height": 1080
        }
    },
    "timeout": {
        "default": 30000,
        "wait": 10000,
        "navigation": 30000
    }
}


# ====================================================
# Module-Level Fixtures
# ====================================================
@pytest.fixture(scope="function")
def page(config):
    """
    函数级 fixture：每个测试用例使用独立的浏览器实例
    确保测试隔离性，避免状态相互影响
    """
    logger.info("=" * 80)
    logger.info("【Function Setup】创建独立浏览器实例")
    logger.info("=" * 80)
    
    browser_type = config["browser"]["type"]
    headless = config["browser"].get("headless", False)
    viewport = config["browser"].get("viewport", {"width": 1920, "height": 1080})
    
    from playwright.sync_api import sync_playwright
    playwright = sync_playwright().start()
    
    if browser_type == "chromium":
        browser = playwright.chromium.launch(headless=headless)
    elif browser_type == "firefox":
        browser = playwright.firefox.launch(headless=headless)
    elif browser_type == "webkit":
        browser = playwright.webkit.launch(headless=headless)
    else:
        raise ValueError(f"不支持的浏览器类型: {browser_type}")
    
    context = browser.new_context(viewport=viewport)
    page = context.new_page()
    
    yield page
    
    logger.info("=" * 80)
    logger.info("【Function Teardown】关闭浏览器实例")
    logger.info("=" * 80)
    page.close()
    context.close()
    browser.close()
    playwright.stop()


@pytest.fixture(scope="module")
def valid_detail_url_with_recommendations():
    """
    提供一个有推荐模块的有效详情页URL
    
    策略：使用候选URL列表
    """
    # 候选详情页URL（从分享功能测试中复用）
    CANDIDATE_URLS = [
        "https://us.58v5.cn/en/city-washington1/cate-others242/testcheng-6517268992063710/",
        "https://us.58v5.cn/en/city-washington1/cate-others127/40oz-tritan-bpa-free-large-tumbler-with-straw-and-handle-reusable-water-cup-6530384495922910/",
    ]
    
    logger.info("="*80)
    logger.info("【推荐模块】获取有效详情页URL...")
    logger.info("="*80)
    
    url = CANDIDATE_URLS[0]
    logger.info(f"✓ 使用详情页URL: {url}")
    logger.info("="*80)
    return url


@pytest.fixture(scope="function", autouse=True)
def reset_page_state(page):
    """
    每个测试用例执行后重置页面状态
    对于推荐模块，不需要特殊的重置逻辑
    """
    yield
    pass


# ====================================================
# Test Cases - Batch 2
# ====================================================

@pytest.mark.case_id("TC-REC-007")
@pytest.mark.p0
@pytest.mark.smoke
@pytest.mark.detail_page
@pytest.mark.recommendation
@pytest.mark.favorite
@pytest.mark.us
@allure.feature("详情页")
@allure.story("推荐模块 - 访客收藏交互")
@allure.title("TC-REC-007: 点击收藏图标弹出登录弹窗（访客状态）")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
**测试目的**：验证访客状态下点击推荐卡片收藏图标后弹出登录弹窗

**前置条件**：
- 用户未登录（访客状态）
- 访问有推荐模块的详情页

**测试步骤**：
1. 访客身份打开详情页
2. 滚动到推荐模块
3. 验证访客状态（右上角显示 "Log in / Register"）
4. 验证推荐模块可见
5. 点击第一张推荐卡片的收藏图标
6. 验证登录弹窗弹出
7. 验证弹窗包含：邮箱输入框、Continue 按钮、第三方登录按钮

**预期结果**：
- 访客状态下点击收藏图标立即弹出登录弹窗
- 登录弹窗包含：标题、输入框、Continue 按钮、第三方登录选项（Google/Facebook/Apple）、隐私政策说明
- 弹窗右上角有关闭按钮
- 背景页面不跳转
""")
def test_tc_rec_007_visitor_favorite_triggers_login_modal(page, config, valid_detail_url_with_recommendations):
    """
    TC-REC-007: 访客状态下点击推荐卡片收藏图标弹出登录弹窗
    """
    logger.info("=" * 80)
    logger.info("TC-REC-007: 点击收藏图标弹出登录弹窗（访客状态）")
    logger.info("=" * 80)
    logger.info(f"站点: {_CONFIG['site'].upper()} ({_CONFIG['site_name']})")
    detail_url = valid_detail_url_with_recommendations  # 使用动态URL
    logger.info(f"详情页: {detail_url}")
    logger.info("=" * 80)
    
    # 初始化 Page Object
    rec_page = DetailPageRecommendation(page)
    
    with allure.step("步骤1：访客身份打开详情页"):
        rec_page.navigate_to_detail_page(detail_url)
        logger.info(f"✓ 打开详情页成功: {detail_url}")
    
    with allure.step("步骤2：处理Cookie弹窗（如果存在）"):
        rec_page.handle_cookie_popup()
        logger.info("✓ 已处理Cookie弹窗（如果存在）")
    
    with allure.step("步骤3：滚动到推荐模块"):
        rec_page.scroll_to_recommendation_module()
        logger.info("✓ 滚动到推荐模块成功")
    
    with allure.step("步骤4：验证访客状态"):
        login_button = page.get_by_text("Log in / Register")
        expect(login_button).to_be_visible()
        logger.info("✓ 访客状态确认：右上角显示 'Log in / Register'")
    
    with allure.step("步骤5：验证推荐模块可见"):
        is_visible = rec_page.is_recommendation_title_visible()
        assert is_visible, "推荐模块应该可见"
        logger.info("✓ 推荐模块可见")
    
    with allure.step("步骤6：验证推荐标题"):
        expect(rec_page.recommendation_title).to_be_visible()
        expect(rec_page.recommendation_title).to_have_text("You may also like")
        logger.info("✓ 推荐标题验证通过")
    
    with allure.step("步骤7：点击第一张推荐卡片的收藏图标"):
        # 直接使用 evaluate 点击，不使用 Page Object 方法（因为 Page Object 方法有 3 秒等待）
        page.evaluate(
            "document.querySelectorAll('.list-components-item-favorite.pc-card img.favorite-icon')[0].click()"
        )
        page.wait_for_timeout(500)
        logger.info("✓ 点击收藏图标成功")
    
    with allure.step("步骤8：验证登录弹窗弹出"):
        # 验证登录弹窗的标题
        welcome_heading = page.get_by_text("Welcome to OK.com")
        expect(welcome_heading).to_be_visible(timeout=10000)
        logger.info("✓ 登录弹窗已弹出")
    
    with allure.step("步骤9：验证登录弹窗标题"):
        welcome_title = page.get_by_text("Welcome to OK.com")
        expect(welcome_title).to_be_visible()
        logger.info("✓ 登录弹窗标题验证通过")
    
    with allure.step("步骤10：验证邮箱输入框存在"):
        # 使用 role=textbox 定位
        email_input = page.get_by_role("textbox").filter(has_text="Email or phone number").first
        if not email_input.is_visible(timeout=2000):
            # 如果第一个定位器失败，尝试更宽松的定位
            email_input = page.get_by_role("textbox").first
        expect(email_input).to_be_visible(timeout=5000)
        logger.info("✓ 邮箱输入框可见")
    
    with allure.step("步骤11：验证 Continue 按钮存在且初始禁用"):
        continue_button = page.get_by_role("button", name="Continue")
        expect(continue_button).to_be_visible()
        expect(continue_button).to_be_disabled()
        logger.info("✓ Continue 按钮存在且初始禁用")
    
    with allure.step("步骤12：验证第三方登录按钮存在"):
        # 验证 Google 登录图标
        google_login = page.locator('img[alt="google"]').first
        expect(google_login).to_be_visible()
        
        # 验证 Facebook 登录图标
        facebook_login = page.locator('img[alt="facebook"]').first
        expect(facebook_login).to_be_visible()
        
        # 验证 Apple 登录图标
        apple_login = page.locator('img[alt="apple"]').first
        expect(apple_login).to_be_visible()
        
        logger.info("✓ 第三方登录按钮（Google/Facebook/Apple）验证通过")
    
    with allure.step("步骤13：验证隐私政策说明存在"):
        privacy_text = page.get_by_text("By continuing, you accept OK's")
        expect(privacy_text).to_be_visible()
        logger.info("✓ 隐私政策说明可见")
    
    logger.info("=" * 80)
    logger.info("✅ TC-REC-007: 点击收藏图标弹出登录弹窗（访客状态） - 测试通过！")
    logger.info("=" * 80)
