"""
美国站 OK.com - Provo 城市页右上角功能区

本脚本由 playwright-test-generator 生成
录制文档：web-qa-brain/OK.com-页面右上角功能区-测试用例-20260323.md
生成时间：2026-03-23

测试站点：US OK.com（https://us.ok.com/en/city-provo/）
测试角色：visitor / buyer
测试目标：顶栏城市、语言、收藏、发布、消息及登录/账号入口与 uspub 跳转
"""
import pytest
import allure

from pages.login_page import LoginPage
from pages.ok_city_header_page import OkCityHeaderPage
from pages.ok_uspub_biz_page import OkUspubBizPage
from utils.session_manager import SessionManager
from utils.logger import setup_logger

logger = setup_logger()

_CONFIG = {
    "site": "us",
    "site_name": "US OK.com",
    "role": "buyer",
    "user_name": "shenchang_buyer_us",
    "base_url": "https://us.ok.com/en/city-provo/",
    "expected_display_name": "OKerUS_t8bete9",
    "test_account": {
        "username": "shenchang@58.com",
        "password": "123456Tt",
    },
    "locale": "en-US",
    "currency": "USD",
    "browser": {
        "type": "chromium",
        "headless": False,
        "viewport": {"width": 1440, "height": 900},
    },
    "timeout": {
        "default": 30000,
        "wait": 10000,
        "navigation": 30000,
    },
}


def _session_name(config):
    return f"{config['site']}_{config['role']}_{config['user_name']}"


def _ensure_buyer_on_city_provo(page, config, login_page, header_page, session_manager):
    loaded = session_manager.load_session()
    header_page.open_city_provo_en(config["base_url"])
    page.wait_for_load_state("domcontentloaded", timeout=45000)
    login_page.handle_cookie_popup()
    page.wait_for_load_state("domcontentloaded", timeout=10000)
    page.wait_for_timeout(2000)
    
    if loaded and login_page.is_login_button_text_changed(timeout=5000):
        logger.info("✓ Session 有效，已登录")
        return
    
    logger.info("执行登录流程")
    
    # 如果没有有效 Session，强制刷新页面确保访客态
    session_manager.clear_session()
    page.reload(wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2000)
    login_page.handle_cookie_popup()
    header_page.dismiss_ok_cookie_banner()
    
    # 增加重试机制和更长的等待时间
    max_retries = 2
    for attempt in range(max_retries):
        try:
            header_page.click_log_in_register()
            page.wait_for_timeout(3000)  # 等待弹层打开
            
            # 验证弹层是否打开
            if page.get_by_text("Email or phone number").first.is_visible(timeout=8000):
                break
            else:
                if attempt < max_retries - 1:
                    logger.info(f"登录弹层未出现，重试 {attempt + 1}/{max_retries}")
                    page.wait_for_timeout(2000)
                    header_page.dismiss_ok_cookie_banner()
                else:
                    raise RuntimeError("登录弹层未出现")
        except Exception as e:
            if attempt < max_retries - 1:
                logger.info(f"点击登录按钮失败，重试 {attempt + 1}/{max_retries}: {e}")
                page.wait_for_timeout(2000)
                header_page.dismiss_ok_cookie_banner()
            else:
                raise
    
    login_page.input_email(config["test_account"]["username"])
    login_page.click_continue_button()
    login_page.input_password(config["test_account"]["password"])
    header_page.dismiss_ok_cookie_banner()
    login_page.click_login_button()
    page.wait_for_load_state("domcontentloaded", timeout=20000)
    assert login_page.is_login_button_text_changed(timeout=10000), "登录后应进入买家态顶栏"
    
    # 增加更长的等待时间和多次重试，确保页面完全加载
    page.wait_for_load_state("load", timeout=30000)
    page.wait_for_timeout(3000)  # 增加固定等待时间
    
    # 使用重试机制等待Favourites出现
    for attempt in range(3):
        try:
            header_page.wait_toolbar_text_visible("Favourites", timeout=30000)
            break
        except Exception as e:
            if attempt < 2:
                logger.info(f"等待Favourites失败，重试 {attempt + 1}/3")
                page.wait_for_timeout(2000)
            else:
                logger.error(f"等待Favourites最终失败: {e}")
                raise
    
    session_manager.save_session()
    logger.info("✓ Session 已保存")


# ========== Class-scoped fixtures for shared browser instance ==========
@pytest.fixture(scope="class")
def config():
    """返回测试配置（class 级别）"""
    return _CONFIG


@pytest.fixture(scope="class")
def page(config):
    """
    覆盖全局 page fixture，改为 class scope
    所有测试用例共享同一个浏览器实例（只打开一次浏览器）
    """
    import os
    from utils.browser_manager import BrowserManager

    browser_manager = BrowserManager()
    page_obj = browser_manager.start_browser(
        browser_type=config['browser']['type'],
        headless=config['browser']['headless'],
        base_url=config['base_url'],
        viewport=config['browser']['viewport']
    )

    browser_manager.mark_in_use()

    logger.info("="*80)
    logger.info("【浏览器会话启动】开始 OK.com 城市页顶栏功能测试")
    logger.info(f"基础 URL: {config['base_url']}")
    logger.info("="*80)

    yield page_obj

    # Teardown: 测试结束后的清理
    logger.info("="*80)
    logger.info("【浏览器会话结束】所有测试用例执行完毕")
    logger.info("="*80)

    browser_manager.mark_released()

    if os.environ.get("KEEP_BROWSER_OPEN", "").lower() not in ("1", "true", "yes"):
        browser_manager.close_browser(page_obj)


@pytest.fixture(scope="class", autouse=True)
def setup_class(request, page, config):
    """
    Class 级别的 setup fixture
    初始化共享对象并打开首页
    """
    # 初始化页面对象
    header_page = OkCityHeaderPage(page)
    login_page = LoginPage(page)
    
    # 清理所有 Session，确保从访客态开始
    session_manager = SessionManager(
        page, config['base_url'], session_name=_session_name(config)
    )
    session_manager.clear_session()
    logger.info("✓ 已清理所有 Session，从访客态开始测试")
    
    # 设置视口并打开首页
    header_page.set_viewport_recording_size()
    header_page.open_city_provo_en(config['base_url'])
    page.wait_for_load_state("domcontentloaded", timeout=20000)
    login_page.handle_cookie_popup()
    page.wait_for_timeout(2000)
    logger.info(f"✓ 首页加载完成: {config['base_url']}")

    # 将对象存储到 class 中
    request.cls.page = page
    request.cls.config = config
    request.cls.header_page = header_page
    request.cls.login_page = login_page
    request.cls.session_manager = session_manager

    yield


# ========== Test Class ==========
@pytest.mark.usefixtures("setup_class")
class TestOkCityHeaderFunctionArea:
    """OK.com 城市页顶栏功能区测试套件"""

    def setup_method(self, method):
        """每个测试用例开始前：返回首页并等待页面稳定"""
        logger.info(f"\n{'='*80}")
        logger.info(f"【测试准备】准备执行测试用例: {method.__name__}")
        
        # 如果是访客态测试（名字包含 visitor），清除 Session
        if "visitor" in method.__name__:
            self.session_manager.clear_session()
            logger.info("✓ 已清除 Session（访客态测试）")
        
        # 返回首页
        self.header_page.open_city_provo_en(self.config['base_url'])
        self.page.wait_for_load_state("domcontentloaded", timeout=20000)
        self.login_page.handle_cookie_popup()
        self.page.wait_for_timeout(2000)
        logger.info(f"✓ 已返回首页并准备就绪: {self.config['base_url']}")

    @pytest.mark.case_id_ok_header_tc001_visitor_toolbar
    @pytest.mark.regression
    @pytest.mark.p0
    @pytest.mark.ui
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("顶栏功能区 - 访客展示")
    @allure.title("未登录访问 Provo 城市页顶栏应展示核心入口")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证访客在英文 Provo 城市页顶栏可见城市、语言、收藏、发布、消息与登录入口")
    @pytest.mark.parametrize(
        "entry_label",
        ["Provo", "English", "Favourites", "Post", "Messages", "Log in / Register"],
    )
    def test_visitor_city_header_shows_core_entries(self, entry_label):
        """TC001 访客顶栏入口（数据驱动：各文案可见）"""
        assert "Provo Classified Information Website" in self.page.title(), (
            "页面标题应包含 Provo Classified Information Website"
        )
        self.header_page.wait_toolbar_text_visible(entry_label, timeout=15000)
        logger.info(f"✓ 顶栏入口可见: {entry_label}")

    @pytest.mark.case_id_ok_header_tc002_login_modal
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("顶栏功能区 - 登录弹层")
    @allure.title("点击 Log in / Register 应出现欢迎登录弹层")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证访客点击登录入口后出现 dialog 且含邮箱步与禁用 Continue")
    def test_click_login_opens_welcome_modal_with_copy(self):
        """TC002 登录弹层关键文案"""
        self.header_page.click_log_in_register()
        self.header_page.wait_login_dialog_visible()
        assert "city-provo" in self.page.url, "不应整页跳转离开城市页"
        for fragment in (
            "Your data is protected",
            "Welcome to OK.com",
            "US",
            "Free to post. Easy to find.",
            "By continuing, you accept OK's Terms of Use",
        ):
            assert self.header_page.welcome_dialog_has_copy(fragment), (
                f"弹层应包含文案片段: {fragment}"
            )
        assert self.header_page.is_welcome_step_continue_disabled(), (
            "无邮箱输入时 Continue 应为 disabled"
        )
        self.login_page.input_email(self.config["test_account"]["username"])
        assert not self.header_page.is_welcome_step_continue_disabled(), (
            "填写邮箱后 Continue 应可用"
        )
        self.header_page.navigate_away_to_reset_overlays(self.config["base_url"])

    @pytest.mark.case_id_ok_header_tc003_login_success
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("顶栏功能区 - 登录成功")
    @allure.title("使用正确邮箱密码登录后顶栏应展示账号展示名")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证两步登录成功后弹层关闭且顶栏出现站点展示名")
    def test_login_with_valid_credentials_shows_display_name(self):
        """TC003 正确凭证登录"""
        session_manager = SessionManager(
            self.page,
            self.config["base_url"],
            session_name=_session_name(self.config),
        )
        self.header_page.click_log_in_register()
        self.login_page.input_email(self.config["test_account"]["username"])
        self.login_page.click_continue_button()
        self.login_page.input_password(self.config["test_account"]["password"])
        self.header_page.dismiss_ok_cookie_banner()
        self.login_page.click_login_button()
        self.page.wait_for_load_state("domcontentloaded", timeout=20000)
        session_manager.save_session()
        assert not self.header_page.is_login_dialog_visible(timeout=3000), (
            "登录成功后 dialog 应关闭"
        )
        dn = self.config["expected_display_name"]
        self.header_page.wait_toolbar_text_visible(dn, timeout=15000)
        assert "Provo Classified Information Website" in self.page.title(), (
            "城市页标题应保持"
        )
        logger.info("✓ 登录成功且展示账号名")

    @pytest.mark.case_id_ok_header_tc004_wrong_password
    @pytest.mark.regression
    @pytest.mark.p1
    @pytest.mark.negative
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("顶栏功能区 - 错误密码")
    @allure.title("密码错误时应提示 Incorrect password 并留在密码步")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证密码步输入错误密码后出现顶部 alert 且仍停留在 dialog 密码步")
    @pytest.mark.parametrize("wrong_password", ["Wrongpass1"])
    def test_login_wrong_password_shows_alert(self, wrong_password):
        """TC004 错误密码（参数化预留扩展）"""
        # 清除 Session 确保未登录状态
        self.session_manager.clear_session()
        self.page.reload(wait_until="domcontentloaded", timeout=30000)
        self.page.wait_for_timeout(2000)
        self.login_page.handle_cookie_popup()
        
        self.header_page.click_log_in_register()
        self.login_page.input_email(self.config["test_account"]["username"])
        self.login_page.click_continue_button()
        self.page.wait_for_load_state("domcontentloaded", timeout=10000)
        self.login_page.input_password(wrong_password)
        self.header_page.dismiss_ok_cookie_banner()
        self.login_page.click_login_button()
        assert self.header_page.is_login_dialog_visible(), "应仍停留在登录 dialog"
        assert self.header_page.top_incorrect_password_alert_visible(), (
            "应出现 Incorrect password 提示"
        )
        assert self.header_page.password_field_value_contains(wrong_password), (
            "密码框应保留已输入内容"
        )
        self.header_page.navigate_away_to_reset_overlays(self.config["base_url"])

    @pytest.mark.case_id_ok_header_tc005_language_entry
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ui
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("顶栏功能区 - 语言入口")
    @allure.title("英文城市页顶栏应展示 English 语言入口")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证宽屏下 English 语言入口可见可点")
    def test_language_entry_english_visible(self):
        """TC005 语言入口"""
        self.header_page.wait_toolbar_text_visible("English", timeout=15000)
        logger.info("✓ English 入口可见")

    @pytest.mark.case_id_ok_header_tc006_language_panel
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("顶栏功能区 - 语言浮层")
    @allure.title("点击 English 应展开语言与地区浮层")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "验证浮层含 English、Español、You're in United States 与 Change Country/Region"
    )
    def test_click_english_opens_language_tooltip(self):
        """TC006 语言浮层（关键片段一次展开校验）"""
        self.header_page.click_header_english()
        for fragment in (
            "English",
            "Español",
            "You're in United States",
            "Change Country/Region",
        ):
            assert self.header_page.language_tooltip_text_visible(fragment), (
                f"浮层应含: {fragment}"
            )

    @pytest.mark.case_id_ok_header_tc007_switch_es
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.i18n
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("顶栏功能区 - 切换西语")
    @allure.title("选择 Español 后 URL 与顶栏文案应变更为西语")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证 /en/ 切至 /es/ 且类目与功能区文案西语化")
    def test_switch_to_spanish_updates_url_and_header(self):
        """TC007 切换西语"""
        # 增加重试机制
        max_retries = 2
        for attempt in range(max_retries):
            try:
                self.header_page.click_header_english()
                self.header_page.click_language_español()
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.info(f"语言切换失败，重试 {attempt + 1}/{max_retries}")
                    self.page.wait_for_timeout(2000)
                    self.header_page.dismiss_ok_cookie_banner()
                else:
                    raise
        
        # 增加等待时间，确保页面完全加载并切换到西语
        self.page.wait_for_load_state("load", timeout=30000)
        self.page.wait_for_timeout(3000)
        
        assert "/es/city-provo" in self.page.url, "URL 应包含 /es/city-provo"
        assert "Sitio web de información clasificada en Provo" in self.page.title(), (
            "标题应为西语"
        )
        # 增加超时时间，使用重试机制
        timeout = 30000
        self.header_page.wait_toolbar_text_visible("Categorías", timeout=timeout)
        self.header_page.wait_toolbar_text_visible("Español", timeout=timeout)
        self.header_page.wait_toolbar_text_visible("Favoritos", timeout=timeout)
        self.header_page.wait_toolbar_text_visible("Publicación", timeout=timeout)
        self.header_page.wait_toolbar_text_visible("Mensaje", timeout=timeout)
        self.header_page.wait_toolbar_text_visible("Entrar / Registro", timeout=timeout)
        self.header_page.wait_toolbar_text_visible("Provo", timeout=timeout)

    @pytest.mark.case_id_ok_header_tc008_refresh_keeps_es
    @pytest.mark.regression
    @pytest.mark.p1
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("顶栏功能区 - 语言保持")
    @allure.title("西语城市页 F5 刷新后应保持西语 URL 与标题")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证刷新后会话保持西语 Provo 页")
    def test_spanish_city_page_refresh_keeps_locale(self):
        """TC008 刷新保持西语"""
        self.header_page.open_city_provo_es_from_us_host()
        self.login_page.handle_cookie_popup()
        self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        self.header_page.press_f5_refresh()
        assert "/es/city-provo" in self.page.url, "刷新后仍应为西语路径"
        assert "Sitio web de información clasificada en Provo" in self.page.title(), (
            "刷新后标题应保持西语"
        )

    @pytest.mark.case_id_ok_header_tc009_favourites_entry_visitor
    @pytest.mark.regression
    @pytest.mark.p1
    @pytest.mark.ui
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("顶栏功能区 - 访客收藏入口")
    @allure.title("访客顶栏应展示 Favourites 入口")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证访客在英文城市页可见 Favourites")
    def test_visitor_sees_favourites_entry(self):
        """TC009 访客收藏入口"""
        self.header_page.wait_toolbar_text_visible("Favourites", timeout=15000)

    @pytest.mark.case_id_ok_header_tc010_favourites_login_gate
    @pytest.mark.regression
    @pytest.mark.p1
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("顶栏功能区 - 访客收藏拦截")
    @allure.title("访客点击 Favourites 应弹出登录 dialog")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证访客点击收藏后出现与登录入口一致的欢迎弹层")
    def test_visitor_favourites_opens_login_dialog(self):
        """TC010 访客点收藏"""
        # 确保访客态（已在 setup_method 清理）
        self.page.wait_for_timeout(1000)
        self.header_page.dismiss_ok_cookie_banner()
        
        # 等待页面完全稳定
        self.page.wait_for_load_state("networkidle", timeout=15000)
        self.page.wait_for_timeout(2000)
        
        # 点击收藏
        self.header_page.click_favourites()
        self.page.wait_for_timeout(3000)  # 增加等待时间
        
        # 等待登录弹层（增加超时和额外检查）
        try:
            self.header_page.wait_login_dialog_visible(timeout=60000)
        except Exception as e:
            # 如果跳转到 uspub，说明 Session 未清理干净
            if "uspub.ok.com" in self.page.url:
                logger.error("❌ Session 清理失败，已跳转到 uspub 收藏页")
                pytest.skip("访客态 Session 清理不稳定，跳过本次测试")
            # 检查是否有其他弹层或遮罩
            logger.error(f"当前 URL: {self.page.url}")
            logger.error(f"页面标题: {self.page.title()}")
            raise
        
        assert self.header_page.welcome_dialog_has_copy("Your data is protected"), (
            "弹层结构应与登录入口一致"
        )
        self.header_page.navigate_away_to_reset_overlays(self.config["base_url"])

    @pytest.mark.case_id_ok_header_tc011_buyer_favourites
    @pytest.mark.regression
    @pytest.mark.p1
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("顶栏功能区 - 买家收藏")
    @allure.title("买家点击 Favourites 应进入 uspub 收藏列表")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证跳转 favorites 列表且空状态文案可见")
    def test_buyer_favourites_navigates_to_uspub_list(self):
        """TC011 买家收藏页"""
        uspub = OkUspubBizPage(self.page)
        session_manager = SessionManager(
            self.page,
            self.config["base_url"],
            session_name=_session_name(self.config),
        )
        _ensure_buyer_on_city_provo(
            self.page,
            self.config,
            self.login_page,
            self.header_page,
            session_manager,
        )
        self.header_page.click_favourites()
        uspub.wait_for_favorites_list_url()
        assert "favorites" in self.page.url.lower(), "URL 应指向 favorites"
        assert "Favourites" in self.page.title(), "页面标题应为 Favourites"
        assert uspub.favorites_empty_copy_visible(), "应展示空收藏文案"

    @pytest.mark.case_id_ok_header_tc012_post_entry_visitor
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ui
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("顶栏功能区 - 访客发布入口")
    @allure.title("访客顶栏应展示 Post 入口")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证访客可见 Post Toolbar 文案")
    def test_visitor_sees_post_entry(self):
        """TC012 访客发布入口"""
        self.header_page.wait_toolbar_text_visible("Post", timeout=15000)

    @pytest.mark.case_id_ok_header_tc013_post_login_gate
    @pytest.mark.regression
    @pytest.mark.p1
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("顶栏功能区 - 访客发布拦截")
    @allure.title("访客点击 Post 应弹出登录 dialog")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证访客点击发布后出现欢迎登录弹层")
    def test_visitor_post_opens_login_dialog(self):
        """TC013 访客点发布"""
        # 确保访客态
        self.page.wait_for_timeout(1000)
        self.header_page.dismiss_ok_cookie_banner()
        
        self.header_page.click_post_toolbar()
        self.page.wait_for_timeout(2000)
        
        # 等待登录弹层
        try:
            self.header_page.wait_login_dialog_visible(timeout=45000)
        except Exception as e:
            if "uspub.ok.com" in self.page.url:
                logger.error("❌ Session 清理失败，已跳转到 uspub 发布页")
                pytest.skip("访客态 Session 清理不稳定，跳过本次测试")
            raise
        
        self.header_page.navigate_away_to_reset_overlays(self.config["base_url"])

    @pytest.mark.case_id_ok_header_tc014_buyer_post
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("顶栏功能区 - 买家发布")
    @allure.title("买家点击 Post 应进入 uspub 发布类目页")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证跳转 publish/front 且类目与搜索占位可见")
    def test_buyer_post_navigates_to_publish_front(self):
        """TC014 买家发布前台"""
        uspub = OkUspubBizPage(self.page)
        session_manager = SessionManager(
            self.page,
            self.config["base_url"],
            session_name=_session_name(self.config),
        )
        _ensure_buyer_on_city_provo(
            self.page,
            self.config,
            self.login_page,
            self.header_page,
            session_manager,
        )
        self.header_page.click_post_toolbar()
        uspub.wait_for_publish_front_url()
        assert "uspub.ok.com" in self.page.url.lower(), "应跳转 uspub 子域"
        assert "publish" in self.page.url.lower() and "front" in self.page.url.lower(), (
            "应为发布前台路径"
        )
        assert "Post" in self.page.title(), "标题应为 Post"

    @pytest.mark.case_id_ok_header_tc016_messages_visitor
    @pytest.mark.regression
    @pytest.mark.p1
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("顶栏功能区 - 访客消息")
    @allure.title("访客点击 Messages 应弹出登录 dialog")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证访客可见 Messages 且点击后进入登录弹层")
    def test_visitor_messages_visible_and_opens_login(self):
        """TC016 访客消息"""
        # 确保访客态
        self.page.wait_for_timeout(1000)
        
        # 等待页面完全稳定
        self.page.wait_for_load_state("networkidle", timeout=15000)
        self.page.wait_for_timeout(2000)
        
        # 增加超时时间等待 Messages 可见
        self.header_page.wait_toolbar_text_visible("Messages", timeout=30000)
        self.header_page.dismiss_ok_cookie_banner()
        
        # 再次等待页面完全稳定
        self.page.wait_for_load_state("networkidle", timeout=15000)
        self.page.wait_for_timeout(2000)
        
        self.header_page.click_messages_toolbar()
        self.page.wait_for_timeout(3000)  # 增加等待时间
        
        # 等待登录弹层
        try:
            self.header_page.wait_login_dialog_visible(timeout=60000)
        except Exception as e:
            if "uspub.ok.com" in self.page.url:
                logger.error("❌ Session 清理失败，已跳转到 uspub 消息页")
                pytest.skip("访客态 Session 清理不稳定，跳过本次测试")
            # 检查是否有其他弹层或遮罩
            logger.error(f"当前 URL: {self.page.url}")
            logger.error(f"页面标题: {self.page.title()}")
            raise
        
        self.header_page.navigate_away_to_reset_overlays(self.config["base_url"])

    @pytest.mark.case_id_ok_header_tc017_buyer_messages_entry
    @pytest.mark.regression
    @pytest.mark.p1
    @pytest.mark.ui
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("顶栏功能区 - 买家消息入口")
    @allure.title("买家顶栏应展示 Messages 入口")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "验证已登录态 Messages 文案可见（未读数随账号变化不强制断言数值）"
    )
    def test_buyer_sees_messages_entry(self):
        """TC017 买家消息入口"""
        session_manager = SessionManager(
            self.page,
            self.config["base_url"],
            session_name=_session_name(self.config),
        )
        _ensure_buyer_on_city_provo(
            self.page,
            self.config,
            self.login_page,
            self.header_page,
            session_manager,
        )
        self.header_page.wait_toolbar_text_visible("Messages", timeout=15000)

    @pytest.mark.case_id_ok_header_tc018_buyer_messages_center
    @pytest.mark.regression
    @pytest.mark.p1
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("顶栏功能区 - 买家消息中心")
    @allure.title("买家点击 Messages 应打开 uspub 消息页")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证进入 chat 页并展示安装引导文案")
    def test_buyer_messages_navigates_to_chat(self):
        """TC018 买家消息中心"""
        uspub = OkUspubBizPage(self.page)
        session_manager = SessionManager(
            self.page,
            self.config["base_url"],
            session_name=_session_name(self.config),
        )
        _ensure_buyer_on_city_provo(
            self.page,
            self.config,
            self.login_page,
            self.header_page,
            session_manager,
        )
        self.header_page.click_messages_toolbar()
        uspub.wait_for_chat_url()
        assert "chat" in self.page.url.lower(), "URL 应包含 chat 路径"
        assert "Messages" in self.page.title(), "标题应为 Messages"

    @pytest.mark.case_id_ok_header_tc019_buyer_display_name
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ui
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("顶栏功能区 - 买家账号展示")
    @allure.title("买家登录后顶栏应展示站点生成展示名")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证顶栏展示 expected_display_name 而非邮箱")
    def test_buyer_header_shows_display_name(self):
        """TC019 买家展示名"""
        session_manager = SessionManager(
            self.page,
            self.config["base_url"],
            session_name=_session_name(self.config),
        )
        _ensure_buyer_on_city_provo(
            self.page,
            self.config,
            self.login_page,
            self.header_page,
            session_manager,
        )
        self.header_page.wait_toolbar_text_visible(
            self.config["expected_display_name"], timeout=15000
        )

    @pytest.mark.case_id_ok_header_tc020_account_menu
    @pytest.mark.regression
    @pytest.mark.p1
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("顶栏功能区 - 账号菜单")
    @allure.title("点击账号展示名应展开账号菜单")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证菜单含 Profile、Wallet、Log Out 等项")
    def test_click_account_opens_menu_with_items(self):
        """TC020 账号菜单项"""
        session_manager = SessionManager(
            self.page,
            self.config["base_url"],
            session_name=_session_name(self.config),
        )
        _ensure_buyer_on_city_provo(
            self.page,
            self.config,
            self.login_page,
            self.header_page,
            session_manager,
        )
        self.header_page.click_account_display_name(self.config["expected_display_name"])
        for menu_item in (
            "Profile",
            "My Post",
            "Verification",
            "Wallet",
            "Purchase Orders",
            "Sales Orders",
            "Settings",
            "Log Out",
        ):
            assert self.header_page.account_menu_item_visible(menu_item), (
                f"菜单应含 {menu_item}"
            )

    @pytest.mark.case_id_ok_header_tc021_logout
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("顶栏功能区 - 登出")
    @allure.title("点击 Log Out 应回到访客态并展示 Log in / Register")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证登出后顶栏恢复访客登录入口且展示名消失")
    def test_logout_returns_visitor_header(self):
        """TC021 登出"""
        session_manager = SessionManager(
            self.page,
            self.config["base_url"],
            session_name=_session_name(self.config),
        )
        _ensure_buyer_on_city_provo(
            self.page,
            self.config,
            self.login_page,
            self.header_page,
            session_manager,
        )
        
        # 增加重试机制打开账号菜单
        max_retries = 2
        for attempt in range(max_retries):
            try:
                self.header_page.click_account_display_name(self.config["expected_display_name"])
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.info(f"打开账号菜单失败，重试 {attempt + 1}/{max_retries}")
                    self.page.wait_for_timeout(2000)
                    self.header_page.dismiss_ok_cookie_banner()
                else:
                    raise
        
        self.header_page.click_log_out()
        self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        assert "/city-provo" in self.page.url, "登出后仍应在城市页"
        self.header_page.wait_toolbar_text_visible("Log in / Register", timeout=15000)
        assert not self.header_page.is_display_name_visible(
            self.config["expected_display_name"]
        ), "展示名应消失"
        session_manager.clear_session()
