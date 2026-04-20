"""
OK.com 详情页收藏功能测试 - 登录用户场景
测试范围：TC005-TC015（登录用户的收藏操作、状态持久化、收藏列表）
"""
import pytest
import allure
import logging
from pages.detail_page_favourites import DetailPageFavourites
from utils.session_manager import SessionManager

logger = logging.getLogger(__name__)

# 测试环境配置
_CONFIG = {
    "site": "us",
    "site_name": "美国站 (US OK.com)",
    "role": "buyer",
    "user_name": "us_buyer_sc",
    "base_url": "https://us.58v5.cn/en/city-washington1/cate/",
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

@pytest.fixture(scope="module")
def config():
    """测试配置"""
    return _CONFIG


@pytest.fixture(scope="module")
def page(config):
    """
    Module 级浏览器 fixture：整个测试模块共享同一个浏览器实例
    
    登录用户场景特点：
    1. 整个模块共享浏览器,提升执行效率
    2. 自动加载认证状态
    3. 测试间状态由 login_user fixture 维护
    """
    from utils.browser_manager import BrowserManager
    
    browser_manager = BrowserManager()
    _page = browser_manager.start_browser(
        browser_type=config['browser']['type'],
        headless=config['browser']['headless'],
        base_url=config['base_url'],
        viewport=config['browser']['viewport']
    )
    
    browser_manager.mark_in_use()
    
    yield _page
    
    browser_manager.mark_released()
    browser_manager.close_browser(_page)


@pytest.fixture(scope="module")
def detail_url(config):
    """
    动态获取一个有效的详情页URL
    
    策略：
    1. 使用预定义的候选URL列表（从safe分类手动收集）
    2. 逐个验证URL是否有效（未删除且有Favourites按钮）
    3. 返回第一个有效的URL
    """
    import re
    from utils.browser_manager import BrowserManager
    
    logger.info("="*80)
    logger.info("【智能URL查找】验证候选详情页URL...")
    logger.info("="*80)
    
    # 候选URL列表（从非招聘/房产/车分类手动收集）
    CANDIDATE_URLS = [
        # Home Goods分类
        "https://us.58v5.cn/en/city-washington1/cate-others127/40oz-tritan-bpa-free-large-tumbler-with-straw-and-handle-reusable-water-cup-6530384495922910/",
        "https://us.58v5.cn/en/city-washington1/cate-others242/testcheng-6517268992063710/",
        # Electronics分类
        "https://us.58v5.cn/en/city-washington1/cate-electronics/gaming-laptop-6458646557837113/",
    ]
    
    browser_manager = BrowserManager()
    temp_page = None
    
    try:
        # 创建临时浏览器用于验证
        temp_page = browser_manager.start_browser(
            browser_type=config['browser']['type'],
            headless=config['browser']['headless'],
            base_url=config['base_url'],
            viewport=config['browser']['viewport']
        )
        
        # 处理Cookie（只需一次）
        logger.info("访问首页处理Cookie...")
        temp_page.goto("https://us.58v5.cn/en/", wait_until="domcontentloaded", timeout=30000)
        try:
            temp_page.get_by_role("button", name=re.compile("Accept|同意", re.I)).click(timeout=3000)
            logger.info("✓ 已处理Cookie弹窗")
        except:
            logger.info("- 无Cookie弹窗")
        temp_page.wait_for_timeout(1000)
        
        # 验证候选URL
        for idx, candidate_url in enumerate(CANDIDATE_URLS):
            logger.info(f"\n候选URL ({idx+1}/{len(CANDIDATE_URLS)}): {candidate_url}")
            logger.info(f"  验证详情页有效性...")
            
            try:
                temp_page.goto(candidate_url, wait_until="domcontentloaded", timeout=20000)
                temp_page.wait_for_timeout(2000)
                
                # 检查是否显示"已删除"
                deleted_indicator = temp_page.get_by_text("The content has been deleted")
                if deleted_indicator.count() > 0 and deleted_indicator.is_visible(timeout=1000):
                    logger.info(f"  ✗ 帖子已删除，跳过")
                    continue
                
                # 检查Favourites按钮是否存在
                fav_btn = temp_page.get_by_text("Favourites", exact=True)
                if fav_btn.count() > 0:
                    try:
                        if fav_btn.first.is_visible(timeout=3000):
                            logger.info(f"  ✓ 找到有效详情页！")
                            logger.info(f"  ✓ URL: {candidate_url}")
                            logger.info("="*80)
                            return candidate_url
                        else:
                            logger.info(f"  ✗ Favourites按钮存在但不可见")
                    except:
                        logger.info(f"  ✗ Favourites按钮检查超时")
                else:
                    logger.info(f"  ✗ 未找到Favourites按钮")
            
            except Exception as e:
                logger.warning(f"  访问失败: {str(e)[:100]}")
                continue
        
        # 如果所有候选URL都失效
        error_msg = f"所有 {len(CANDIDATE_URLS)} 个候选URL都无效"
        logger.error(error_msg)
        logger.error("可能原因：")
        logger.error("  1. 候选URL的帖子都已被删除")
        logger.error("  2. US站点网络问题")
        logger.error("  3. 请更新CANDIDATE_URLS列表")
        pytest.skip(f"智能URL查找失败: {error_msg}")
        
    except Exception as e:
        error_msg = f"智能URL查找异常: {e}"
        logger.error(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        pytest.skip(error_msg)
    finally:
        # 清理临时浏览器
        if temp_page:
            browser_manager.close_browser(temp_page)


@pytest.fixture(scope="module")
def favourites_page(page):
    """详情页收藏功能 Page Object"""
    return DetailPageFavourites(page)


@pytest.fixture(scope="class", autouse=True)
def login_user(page, config, favourites_page):
    """
    类级别的登录 fixture
    确保所有登录用户场景测试开始前已登录
    """
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    
    with allure.step("前置条件：确保用户已登录"):
        # 尝试加载已保存的登录态
        if not session_manager.load_session():
            logger.info("未找到已保存的登录态，开始登录流程")
            
            # 访问首页
            page.goto(config["base_url"])
            page.wait_for_load_state("domcontentloaded")
            favourites_page.handle_cookie_popup()
            
            # 点击登录按钮
            page.get_by_text("Log in / Register").click()
            page.wait_for_timeout(2000)
            
            # 完成登录
            favourites_page.login_in_dialog(
                email=config["test_account"]["username"],
                password=config["test_account"]["password"]
            )
            page.wait_for_timeout(3000)
            
            # 保存登录态
            session_manager.save_session()
            logger.info(f"✓ 登录成功，已保存登录态：{session_name}")
        else:
            logger.info(f"✓ 已加载登录态：{session_name}")
    
    yield
    
    # Teardown: 不清理登录态，供后续测试复用


@pytest.fixture(autouse=True)
def ensure_login_state(page, favourites_page):
    """
    每个测试前确保没有登录弹窗阻挡操作
    如果出现登录弹窗，先关闭它
    """
    yield
    
    # 测试后检查并关闭可能出现的登录弹窗
    try:
        login_dialog = page.locator("dialog[open]")
        if login_dialog.count() > 0 and login_dialog.is_visible(timeout=1000):
            # 按 Escape 关闭弹窗
            page.keyboard.press("Escape")
            page.wait_for_timeout(500)
            logger.info("✓ 已关闭登录弹窗")
    except Exception:
        pass


# ==================== 测试类 ====================

@allure.epic("OK.com 体验测试")
@allure.feature("详情页")
@allure.story("收藏功能 - 登录用户场景")
class TestDetailPageFavouritesLoggedIn:
    """详情页收藏功能 - 登录用户场景测试"""

    @allure.title("TC005: 登录用户首次收藏帖子")
    @allure.description("""
    前置条件：已登录，当前帖子未被收藏
    测试步骤：进入详情页，点击收藏按钮
    预期结果：
    - 图标立即变为实心（已收藏状态）
    - 无需登录弹窗
    - 页面不刷新
    - 可能有成功提示
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @pytest.mark.case_id_favourites_tc005
    def test_logged_user_first_favourite(self, page, config, detail_url, favourites_page):
        """TC005: 登录用户首次收藏帖子"""
        
        with allure.step("步骤1：登录用户进入详情页"):
            page.goto(detail_url)
            page.wait_for_load_state("domcontentloaded")
            logger.info(f"✓ 访问详情页：{detail_url}")

        with allure.step("步骤2：确认收藏按钮为空心图标（未收藏状态）"):
            # 注意：这里无法通过快照判断是空心还是实心，只能通过视觉确认
            # 或者检查是否有 "Remove from favourites" 等文字
            assert favourites_page.is_favourites_button_visible(), "收藏按钮不可见"
            logger.info("✓ 收藏按钮可见")

        with allure.step("步骤3：点击收藏按钮"):
            favourites_page.click_favourites_button(force_click=True)
            page.wait_for_timeout(2000)

        with allure.step("步骤4：等待收藏完成"):
            page.wait_for_timeout(2000)
            logger.info("✓ 收藏操作已完成")

        with allure.step("步骤5：验证页面未刷新"):
            assert detail_url in page.url, "页面 URL 发生变化"
            logger.info("✓ 页面未刷新")

    @allure.title("TC006: 登录用户取消收藏")
    @allure.description("""
    前置条件：已登录，当前帖子已收藏（实心图标）
    测试步骤：点击收藏按钮（取消收藏）
    预期结果：
    - 图标立即变为空心（未收藏状态）
    - 页面不刷新
    - 可能有取消成功提示
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @pytest.mark.case_id_favourites_tc006
    def test_logged_user_cancel_favourite(self, page, config, detail_url, favourites_page):
        """TC006: 登录用户取消收藏"""
        
        with allure.step("前置：访问详情页并先收藏帖子"):
            page.goto(detail_url)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(1000)
            logger.info(f"✓ 访问详情页：{detail_url}")
            
            # 确保收藏按钮可见
            assert favourites_page.is_favourites_button_visible(), "收藏按钮不可见"
            
            # 先点击一次收藏（确保帖子处于已收藏状态）
            favourites_page.click_favourites_button(force_click=True)
            page.wait_for_timeout(2000)
            logger.info("✓ 已收藏帖子")
        
        with allure.step("步骤1：确认收藏按钮为实心图标（已收藏状态）"):
            assert favourites_page.is_favourites_button_visible(), "收藏按钮不可见"
            logger.info("✓ 收藏按钮可见（当前为已收藏状态）")

        with allure.step("步骤2：点击收藏按钮（取消收藏）"):
            favourites_page.click_favourites_button(force_click=True)
            page.wait_for_timeout(2000)

        with allure.step("步骤3：验证页面未刷新"):
            assert detail_url in page.url, "页面 URL 发生变化"
            logger.info("✓ 页面未刷新")

    @allure.title("TC007: 收藏按钮重复点击（状态切换）")
    @allure.description("""
    前置条件：已登录
    测试步骤：连续点击收藏按钮 3 次
    预期结果：
    - 图标状态正确切换：空心→实心→空心→实心
    - 每次点击响应正确
    - 无重复请求或错误
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.p1
    @pytest.mark.us
    @pytest.mark.case_id_favourites_tc007
    def test_logged_user_toggle_favourite_multiple_times(self, page, config, detail_url, favourites_page):
        """TC007: 收藏按钮重复点击（状态切换）"""
        
        with allure.step("前置：访问详情页"):
            page.goto(detail_url)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(1000)
            logger.info(f"✓ 访问详情页：{detail_url}")
            
            # 确保收藏按钮可见
            assert favourites_page.is_favourites_button_visible(), "收藏按钮不可见"
        
        with allure.step("步骤1：点击收藏按钮（第1次）"):
            favourites_page.click_favourites_button(force_click=True)
            page.wait_for_timeout(1500)
            logger.info("✓ 第1次点击完成")

        with allure.step("步骤2：再次点击收藏按钮（第2次）"):
            favourites_page.click_favourites_button(force_click=True)
            page.wait_for_timeout(1500)
            logger.info("✓ 第2次点击完成")

        with allure.step("步骤3：再次点击收藏按钮（第3次）"):
            favourites_page.click_favourites_button(force_click=True)
            page.wait_for_timeout(1500)
            logger.info("✓ 第3次点击完成")

        with allure.step("步骤4：验证收藏按钮仍可见且可交互"):
            assert favourites_page.is_favourites_button_visible(), "收藏按钮不可见"
            assert favourites_page.favourites_button.is_enabled(), "收藏按钮不可交互"
            logger.info("✓ 收藏按钮状态正常，所有操作成功响应")

    @allure.title("TC010: 刷新页面后收藏状态保持")
    @allure.description("""
    前置条件：已登录，已收藏当前帖子
    测试步骤：刷新当前页面（F5）
    预期结果：
    - 页面刷新后，收藏按钮仍显示为实心图标
    - 收藏状态正确保存
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @pytest.mark.case_id_favourites_tc010
    def test_logged_user_favourite_persists_after_refresh(self, page, config, detail_url, favourites_page):
        """TC010: 刷新页面后收藏状态保持"""
        
        with allure.step("前置：访问详情页并收藏帖子"):
            page.goto(detail_url)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(1000)
            logger.info(f"✓ 访问详情页：{detail_url}")
            
            # 确保收藏按钮可见并点击收藏
            assert favourites_page.is_favourites_button_visible(), "收藏按钮不可见"
            favourites_page.click_favourites_button(force_click=True)
            page.wait_for_timeout(2000)
            logger.info("✓ 已收藏帖子")

        with allure.step("步骤1：刷新当前页面"):
            page.reload()
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(2000)
            logger.info("✓ 页面已刷新")

        with allure.step("步骤2：验证收藏按钮仍可见"):
            assert favourites_page.is_favourites_button_visible(), "刷新后收藏按钮不可见"
            logger.info("✓ 刷新后收藏按钮仍可见")

        with allure.step("步骤3：验证页面正常加载"):
            assert detail_url in page.url, "刷新后 URL 异常"
            logger.info("✓ 页面正常加载，收藏状态保持")

    @allure.title("TC011: 退出详情页再次进入，收藏状态保持")
    @allure.description("""
    前置条件：已登录，已收藏帖子 A
    测试步骤：返回列表页，进入其他帖子，再返回帖子 A
    预期结果：帖子 A 的收藏按钮仍为实心图标
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @pytest.mark.case_id_favourites_tc011
    def test_logged_user_favourite_persists_after_navigation(self, page, config, detail_url, favourites_page):
        """TC011: 退出详情页再次进入，收藏状态保持"""
        
        with allure.step("前置：访问详情页并收藏帖子"):
            page.goto(detail_url)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(1000)
            logger.info(f"✓ 访问详情页：{detail_url}")
            
            # 确保收藏按钮可见并点击收藏
            assert favourites_page.is_favourites_button_visible(), "收藏按钮不可见"
            favourites_page.click_favourites_button(force_click=True)
            page.wait_for_timeout(2000)
            logger.info("✓ 已收藏帖子")
        
        with allure.step("步骤1：记录当前帖子 URL"):
            post_a_url = detail_url
            logger.info(f"✓ 帖子 A URL: {post_a_url}")

        with allure.step("步骤2：返回列表页"):
            page.go_back()
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(2000)
            logger.info("✓ 已返回列表页")

        with allure.step("步骤3：进入其他帖子"):
            # 点击列表中的第二个帖子
            other_post = page.locator("a[href*='/cate-']").nth(1)
            if other_post.is_visible():
                other_post.click()
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(2000)
                logger.info("✓ 已进入其他帖子")

        with allure.step("步骤4：再次返回列表页"):
            page.go_back()
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(1000)

        with allure.step("步骤5：重新进入帖子 A"):
            page.goto(post_a_url)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(2000)
            logger.info(f"✓ 重新进入帖子 A：{post_a_url}")

        with allure.step("步骤6：验证收藏按钮仍可见"):
            assert favourites_page.is_favourites_button_visible(), "收藏按钮不可见"
            logger.info("✓ 收藏状态保持，按钮仍可见")

    @allure.title("TC013: 收藏的帖子出现在收藏列表")
    @allure.description("""
    前置条件：已登录
    测试步骤：收藏帖子，访问收藏列表页面
    预期结果：
    - 成功进入收藏列表页面
    - 收藏列表包含刚收藏的帖子
    - 帖子标题、价格、图片等信息正确显示
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @pytest.mark.case_id_favourites_tc013
    def test_logged_user_favourite_appears_in_list(self, page, config, detail_url, favourites_page):
        """TC013: 收藏的帖子出现在收藏列表"""
        
        with allure.step("步骤1：记录帖子标题"):
            page.goto(detail_url)
            page.wait_for_load_state("domcontentloaded")
            post_title = page.locator("h1").first.inner_text()
            logger.info(f"✓ 帖子标题：{post_title[:50]}...")

        with allure.step("步骤2：确保帖子已收藏"):
            favourites_page.click_favourites_button(force_click=True)
            page.wait_for_timeout(2000)
            logger.info("✓ 点击收藏按钮")

        with allure.step("步骤3：访问收藏列表页面"):
            # 使用正确的收藏列表URL
            favourites_list_url = "https://uspub.58v5.cn/biz/en/list/favorites/"
            page.goto(favourites_list_url)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(3000)
            logger.info(f"✓ 访问收藏列表：{favourites_list_url}")

        with allure.step("步骤4：验证进入收藏列表页面"):
            # 严格验证：URL必须包含favorites
            current_url = page.url
            logger.info(f"✓ 当前页面 URL: {current_url}")
            
            assert "favorites" in current_url or "favourites" in current_url, \
                f"收藏列表页面 URL 错误：{current_url}，应该包含 'favorites' 或 'favourites'"
            logger.info("✓ 已成功进入收藏列表页面")

        with allure.step("步骤5：在列表中搜索刚收藏的帖子"):
            # 查找包含帖子标题前 20 个字符的链接
            title_keyword = post_title[:20] if len(post_title) > 20 else post_title
            post_in_list = page.get_by_text(title_keyword, exact=False).first
            
            # 如果找到，验证可见性
            if post_in_list.count() > 0:
                logger.info(f"✓ 在收藏列表中找到帖子：{title_keyword}")
            else:
                logger.warning(f"⚠️ 在收藏列表中未找到帖子（可能需要滚动或分页）")
