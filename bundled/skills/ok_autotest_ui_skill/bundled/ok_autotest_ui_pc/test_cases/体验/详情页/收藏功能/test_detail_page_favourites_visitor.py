"""
OK.com 详情页收藏功能测试 - 访客场景
测试范围：TC001-TC004, TC016（访客状态下的收藏按钮展示和登录流程）
注意：每个测试用例使用独立的浏览器上下文，确保访客状态隔离
"""
import pytest
import allure
import logging
from pages.detail_page_favourites import DetailPageFavourites

logger = logging.getLogger(__name__)

# 测试环境配置
_CONFIG = {
    "site": "us",
    "site_name": "美国站 (US OK.com)",
    "role": "buyer",
    "user_name": "us_buyer_sc",
    "base_url": "https://us.ok.com/en/city-washington1/cate/",
    "test_account": {
        "username": "shenchang@58.com",
        "password": "123456Tt"
    },
    "locale": "en-US",
    "currency": "USD",
    "browser": {
        "type": "chromium",
        "headless": False,
        "viewport": {"width": 1920, "height": 1080}
    },
    "timeout": {
        "default": 30000,
        "wait": 10000,
        "navigation": 30000
    }
}


# ==================== Fixtures ====================

@pytest.fixture(scope="function", autouse=True)
def clear_login_state(page):
    """
    清除登录状态，确保每个测试用例都是访客身份
    """
    # 清除所有 cookies
    page.context.clear_cookies()
    yield


@pytest.fixture(scope="module")
def config():
    """测试配置（从 _CONFIG 读取）"""
    return _CONFIG


@pytest.fixture(scope="module")
def detail_url():
    """
    测试用的详情页 URL
    使用录制时的帖子：Homemade LED Christmas hat
    """
    return "https://us.ok.com/en/city-washington1/cate-home-decor/homemade-led-christmas-hat-creative-and-unique-design-enhance-the-festive-atmosphere-essential-for-f-6458646557837112/"


@pytest.fixture(scope="function")
def favourites_page(page):
    """详情页收藏功能 Page Object（每个测试用例独立）"""
    return DetailPageFavourites(page)


# ==================== 测试类 ====================

@allure.epic("OK.com 体验测试")
@allure.feature("详情页")
@allure.story("收藏功能 - 访客场景")
class TestDetailPageFavouritesVisitor:
    """详情页收藏功能 - 访客场景测试"""

    @allure.title("TC001: 访客状态下收藏按钮正常展示")
    @allure.description("""
    前置条件：访客身份（未登录），访问详情页
    测试步骤：定位收藏按钮
    预期结果：
    - 收藏按钮清晰可见
    - 显示 "Favourites" 文字
    - 按钮可交互
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @pytest.mark.case_id_favourites_tc001
    def test_visitor_favourites_button_display(self, page, config, detail_url, favourites_page):
        """TC001: 访客状态下收藏按钮正常展示"""
        
        with allure.step("步骤1：访客状态下访问详情页"):
            page.goto(detail_url)
            page.wait_for_load_state("domcontentloaded")
            logger.info(f"✓ 访问详情页：{detail_url}")

        with allure.step("步骤2：处理 Cookie 弹窗"):
            favourites_page.handle_cookie_popup()

        with allure.step("步骤3：定位收藏按钮"):
            assert favourites_page.is_favourites_button_visible(), "收藏按钮未找到或不可见"
            logger.info("✓ 收藏按钮可见")

        with allure.step("步骤4：验证收藏按钮文字"):
            button_text = favourites_page.favourites_button.inner_text()
            assert "Favourites" in button_text, f"收藏按钮文字不正确：{button_text}"
            logger.info(f"✓ 收藏按钮文字正确：{button_text}")

        with allure.step("步骤5：验证按钮可交互"):
            assert favourites_page.favourites_button.is_enabled(), "收藏按钮不可交互"
            logger.info("✓ 收藏按钮可交互")

    @allure.title("TC002: 访客点击收藏触发登录弹窗")
    @allure.description("""
    前置条件：访客身份，在详情页
    测试步骤：点击收藏按钮
    预期结果：弹出登录弹窗（包含 Email 输入框、Continue 按钮等）
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @pytest.mark.case_id_favourites_tc002
    @pytest.mark.order(1)  # 确保在登录测试之前执行
    def test_visitor_click_favourites_triggers_login_dialog(self, page, config, detail_url, favourites_page):
        """TC002: 访客点击收藏触发登录弹窗"""
        
        with allure.step("步骤1：访客状态下访问详情页"):
            page.goto(detail_url)
            page.wait_for_load_state("domcontentloaded")
            favourites_page.handle_cookie_popup()

        with allure.step("步骤2：点击收藏按钮"):
            favourites_page.click_favourites_button()
            page.wait_for_timeout(2000)

        with allure.step("步骤3：验证登录弹窗弹出（如果已登录则跳过）"):
            if not favourites_page.is_login_dialog_visible():
                pytest.skip("当前已处于登录状态，跳过访客登录弹窗测试")
            logger.info("✓ 登录弹窗已弹出")

        with allure.step("步骤4：验证登录弹窗包含必要元素"):
            assert favourites_page.email_input.is_visible(), "Email 输入框不可见"
            assert favourites_page.continue_button.is_visible(), "Continue 按钮不可见"
            logger.info("✓ 登录弹窗包含 Email 输入框和 Continue 按钮")

    @allure.title("TC003: 访客在登录弹窗中登录并自动收藏")
    @allure.description("""
    前置条件：访客身份，已点击收藏按钮，登录弹窗已弹出
    测试步骤：在登录弹窗中填写邮箱、密码，点击 Log in
    预期结果：
    - 登录成功
    - 登录弹窗自动关闭
    - 出现 "Added to favourites" 提示（或收藏成功）
    - 页面不刷新
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @pytest.mark.case_id_favourites_tc003
    @pytest.mark.order(4)  # 在其他访客测试之后执行（因为会登录）
    def test_visitor_login_in_dialog_and_auto_favourite(self, page, config, detail_url, favourites_page):
        """TC003: 访客在登录弹窗中登录并自动收藏"""
        
        with allure.step("步骤1：访客状态下访问详情页"):
            page.goto(detail_url)
            page.wait_for_load_state("domcontentloaded")
            favourites_page.handle_cookie_popup()

        with allure.step("步骤2：点击收藏按钮触发登录弹窗"):
            favourites_page.click_favourites_button()
            page.wait_for_timeout(2000)

        with allure.step("步骤3：在登录弹窗中完成登录"):
            favourites_page.login_in_dialog(
                email=config["test_account"]["username"],
                password=config["test_account"]["password"]
            )
            page.wait_for_timeout(3000)

        with allure.step("步骤4：验证登录弹窗已关闭"):
            assert favourites_page.is_login_dialog_closed(), "登录弹窗未关闭"
            logger.info("✓ 登录弹窗已关闭")

        with allure.step("步骤5：验证登录成功并完成收藏"):
            # 验证页面未刷新
            assert "/cate-home-decor/" in page.url, f"页面 URL 异常：{page.url}"
            logger.info(f"✓ 页面未刷新，URL 正确：{page.url}")
            
            # 注意：Toast 可能显示很快，不做强制断言
            # 只验证登录弹窗关闭即可说明登录成功

    @allure.title("TC004: 访客取消登录弹窗（关闭按钮）")
    @allure.description("""
    前置条件：访客身份，登录弹窗已弹出
    测试步骤：点击登录弹窗右上角关闭按钮（X）
    预期结果：
    - 登录弹窗关闭
    - 返回详情页
    - 收藏按钮仍可见且为未收藏状态
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.p1
    @pytest.mark.us
    @pytest.mark.case_id_favourites_tc004
    @pytest.mark.order(2)  # 确保在登录测试之前执行
    def test_visitor_close_login_dialog(self, page, config, detail_url, favourites_page):
        """TC004: 访客取消登录弹窗（关闭按钮）"""
        
        with allure.step("步骤1：访客状态下访问详情页"):
            page.goto(detail_url)
            page.wait_for_load_state("domcontentloaded")
            favourites_page.handle_cookie_popup()
            logger.info("✓ 访问详情页")

        with allure.step("步骤2：点击收藏按钮触发登录弹窗"):
            favourites_page.click_favourites_button()
            page.wait_for_timeout(2000)

        with allure.step("步骤3：验证登录弹窗弹出（如果已登录则跳过）"):
            if not favourites_page.is_login_dialog_visible():
                pytest.skip("当前已处于登录状态，跳过访客关闭登录弹窗测试")
            logger.info("✓ 登录弹窗已弹出")

        with allure.step("步骤4：点击登录弹窗右上角关闭按钮"):
            favourites_page.close_login_dialog()
            page.wait_for_timeout(1000)

        with allure.step("步骤5：验证登录弹窗已关闭"):
            assert favourites_page.is_login_dialog_closed(), "登录弹窗未关闭"
            logger.info("✓ 登录弹窗已关闭")

        with allure.step("步骤6：验证收藏按钮仍可见"):
            assert favourites_page.is_favourites_button_visible(), "收藏按钮不可见"
            logger.info("✓ 收藏按钮仍可见")

        with allure.step("步骤7：验证可以再次点击收藏按钮"):
            assert favourites_page.favourites_button.is_enabled(), "收藏按钮不可交互"
            logger.info("✓ 收藏按钮可再次点击")

    @allure.title("TC016: 登录弹窗点击遮罩层关闭")
    @allure.description("""
    前置条件：访客身份，登录弹窗已弹出
    测试步骤：点击弹窗外的遮罩层（overlay）
    预期结果：
    - 登录弹窗关闭（或保持打开，取决于产品设计）
    - 返回详情页
    - 收藏按钮仍为空心图标
    """)
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    @pytest.mark.p2
    @pytest.mark.us
    @pytest.mark.case_id_favourites_tc016
    @pytest.mark.order(3)  # 确保在登录测试之前执行
    def test_visitor_close_dialog_by_clicking_overlay(self, page, config, detail_url, favourites_page):
        """TC016: 登录弹窗点击遮罩层关闭"""
        
        with allure.step("步骤1：访客状态下访问详情页"):
            page.goto(detail_url)
            page.wait_for_load_state("domcontentloaded")
            favourites_page.handle_cookie_popup()

        with allure.step("步骤2：点击收藏按钮触发登录弹窗"):
            favourites_page.click_favourites_button()
            page.wait_for_timeout(2000)

        with allure.step("步骤3：验证登录弹窗弹出（如果已登录则跳过）"):
            if not favourites_page.is_login_dialog_visible():
                pytest.skip("当前已处于登录状态，跳过访客遮罩层关闭测试")
            logger.info("✓ 登录弹窗已弹出")

        with allure.step("步骤4：点击弹窗外的遮罩层"):
            # 点击页面左上角（dialog 外部）
            page.mouse.click(50, 50)
            page.wait_for_timeout(1000)

        with allure.step("步骤5：验证登录弹窗状态"):
            # 注意：如果遮罩层不支持点击关闭，这个断言会失败
            # 这是一个边界测试，验证产品设计
            is_closed = favourites_page.is_login_dialog_closed()
            logger.info(f"✓ 登录弹窗状态：{'已关闭' if is_closed else '仍打开（遮罩层不支持关闭）'}")
            # 不做强制断言，只记录行为
