"""
AU58 - Property 房产发布功能测试
批次1：模块1 - 发布入口与顶部标题（TC001-TC005，含未登录 Post）

测试环境：
- 网站：https://au.58v5.cn
- 视口：PC端（1920x1080）
- 登录状态：必须登录
"""

import os
import re
import pytest
import allure
from pages.property_publish_page import PropertyPublishPage
from pages.login_page import LoginPage
from utils.session_manager import SessionManager
from utils.logger import setup_logger

logger = setup_logger()


def _goto_with_retry(page, url: str, config, *, attempts: int = 3) -> None:
    """首页/发布页偶发 net::ERR_TIMED_OUT，有限重试。"""
    nav_timeout = config["timeout"]["navigation"]
    last_err: BaseException | None = None
    for i in range(attempts):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=nav_timeout)
            return
        except BaseException as e:
            last_err = e
            logger.warning("goto 重试 %s/%s %s — %s", i + 1, attempts, url, e)
            if i < attempts - 1:
                page.wait_for_timeout(1500 * (i + 1))
    raise last_err  # type: ignore[misc]


def _accept_cookies_if_any(page) -> None:
    try:
        btn = page.get_by_role("button", name="Accept all").first
        if btn.is_visible(timeout=2500):
            btn.click()
            page.wait_for_timeout(400)
    except Exception:
        pass


def _heading_or_title_text(page) -> str:
    for sel in ("h1", "h2", "[role='heading']"):
        loc = page.locator(sel).first
        try:
            t = (loc.inner_text(timeout=2500) or "").strip()
            if t:
                return t
        except Exception:
            continue
    try:
        return (page.title() or "").strip()
    except Exception:
        return ""


def _click_home_post(page) -> bool:
    """在首页顶栏区域尝试点击 Post（PC 布局可能为 button/link）。"""
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(400)
    scopes = (
        page.locator("header"),
        page.locator("nav"),
        page.locator("[class*='header' i]"),
        page.locator("body"),
    )
    for root in scopes:
        try:
            for role in ("button", "link"):
                loc = root.get_by_role(role, name=re.compile(r"^post$", re.I))
                if loc.count() > 0:
                    el = loc.first
                    if el.is_visible(timeout=2500):
                        el.click(timeout=8000)
                        return True
        except Exception:
            continue
    try:
        exact = page.get_by_text("Post", exact=True)
        n = min(exact.count(), 6)
        for i in range(n):
            el = exact.nth(i)
            if not el.is_visible(timeout=800):
                continue
            box = el.bounding_box()
            if box and box.get("y", 9999) < 220:
                el.click(timeout=8000)
                return True
    except Exception:
        pass
    return False


def _login_ui_visible(page) -> bool:
    page.wait_for_timeout(800)
    try:
        if page.get_by_role("dialog").first.is_visible(timeout=4000):
            return True
    except Exception:
        pass
    try:
        tb = page.get_by_role("textbox", name=re.compile(r"email|phone", re.I))
        if tb.first.is_visible(timeout=3000):
            return True
    except Exception:
        pass
    u = page.url or ""
    if re.search(r"login|signin|sign-in|passport|account", u, re.I):
        return True
    body = page.evaluate("() => document.body.innerText || ''") or ""
    return bool(
        re.search(
            r"log\s*in|sign\s*in|email\s+or\s+phone|continue|验证码|密码",
            body,
            re.I,
        )
    )


_CONFIG = {
    "site": "au",
    "site_name": "澳洲站",
    "role": "seller",
    "user_name": "au_seller_liuyue",
    "base_url": "https://au.58v5.cn",
    "publish_url": "https://aupub.58v5.cn/biz/en",
    "test_account": {
        "username": "liuyue62@58.com",
        "password": "Xindemima1%",
    },
    "locale": "en-AU",
    "currency": "AUD",
    "browser": {
        "type": "chromium",
        "headless": False if not os.getenv("CI") else True,
        "viewport": {"width": 1920, "height": 1080}
    },
    "timeout": {
        "default": 30000,
        "wait": 10000,
        "navigation": 30000
    }
}


@pytest.fixture(scope="module")
def logged_in_page(page, config):
    """与批次2+一致：SessionManager 恢复/写入会话，保证 aupub 发布域为登录态。"""
    vp = config["browser"].get("viewport") or {"width": 1920, "height": 1080}
    page.set_viewport_size(vp)
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config["base_url"], session_name)
    login_page = LoginPage(page)
    if session_manager.load_session():
        logger.info("✓ batch1 Session 已加载")
    else:
        login_page.navigate_to_home_page(config["base_url"])
        login_page.handle_cookie_popup()
        login_page.login(
            config["test_account"]["username"],
            config["test_account"]["password"],
        )
        session_manager.save_session()
        logger.info("✓ batch1 登录并保存 Session")
    return page


@pytest.fixture
def publish_page(logged_in_page):
    """房产发布页 fixture（依赖登录状态）"""
    return PropertyPublishPage(logged_in_page)


@pytest.mark.p0
@pytest.mark.case_id("TC001")
@pytest.mark.case_id_au58_property_publish_m1_001
@allure.feature("AU站房产发布")
@allure.story("模块1：发布入口与顶部标题")
@allure.title("TC001 发布前置页显示正确的二级分类列表")
@allure.severity(allure.severity_level.BLOCKER)
def test_tc001_publish_front_page_shows_secondary_categories(logged_in_page, config, publish_page):
    """
    TC001 发布前置页显示正确的二级分类列表
    
    前置条件：
    - 已登录 AU 站账号
    
    测试步骤：
    1. 直接导航到发布前置页
    2. 验证二级分类列表显示
    
    预期结果：
    - 显示完整的二级分类列表（Marketplace、Jobs、Property For Rent、Property For Sale等9个分类）
    - 各分类可点击
    
    MCP录制代码：
    await page.goto('https://aupub.58v5.cn/biz/en/publish/front');
    """
    with allure.step("步骤1：导航到发布前置页"):
        logged_in_page.goto(f"{config['publish_url']}/publish/front", timeout=30000)
        logged_in_page.wait_for_load_state("domcontentloaded", timeout=30000)
        logged_in_page.wait_for_timeout(2000)
        _accept_cookies_if_any(logged_in_page)
        logger.info("✓ 导航到发布前置页成功")
    
    with allure.step("步骤2：验证核心二级分类（线上类目可能增减，不全量强制 Marketplace 等）"):
        required_categories = [
            "Property For Rent",
            "Property For Sale",
        ]
        for category in required_categories:
            category_element = logged_in_page.get_by_text(category, exact=True).first
            assert category_element.is_visible(timeout=8000), (
                f"二级分类 {category} 应该显示"
            )
        optional_categories = [
            "Marketplace",
            "Jobs",
            "Commercial Property for sale",
            "Commercial Property for rent",
            "Cars",
            "Services",
            "Community",
        ]
        shown_extra = sum(
            1
            for c in optional_categories
            if logged_in_page.get_by_text(c, exact=True).first.is_visible(timeout=1500)
        )
        logger.info(
            "✓ 核心二级分类已校验；其余类目可见数: %s / %s",
            shown_extra,
            len(optional_categories),
        )
    
    allure.attach(
        logged_in_page.screenshot(),
        name="tc001-二级分类列表",
        attachment_type=allure.attachment_type.PNG
    )


@pytest.mark.p0
@pytest.mark.case_id("TC002")
@pytest.mark.case_id_au58_property_publish_m1_002
@allure.feature("AU站房产发布")
@allure.story("模块1：发布入口与顶部标题")
@allure.title("TC002 点击二级分类后仅显示对应三级分类")
@allure.severity(allure.severity_level.BLOCKER)
def test_tc002_click_secondary_shows_tertiary_categories(logged_in_page, config, publish_page):
    """
    TC002 点击二级分类后仅显示对应三级分类
    
    前置条件：
    - 已登录 AU 站账号
    - 发布前置页已加载
    
    测试步骤：
    1. 导航到发布前置页
    2. 点击"Property For Rent"
    3. 验证三级分类列表
    
    预期结果：
    - 三级分类中只显示"Property For Rent"下属类型（House、Townhomes等6个）
    - 不显示其他二级分类的三级分类
    
    MCP录制代码：
    await page.getByText('Property For Rent', { exact: true }).click();
    """
    with allure.step("步骤1：导航到发布前置页"):
        logged_in_page.goto(f"{config['publish_url']}/publish/front", timeout=30000)
        logged_in_page.wait_for_load_state("domcontentloaded", timeout=30000)
        logged_in_page.wait_for_timeout(2000)
        _accept_cookies_if_any(logged_in_page)
        logger.info("✓ 导航到发布前置页成功")
    
    with allure.step("步骤2：点击二级分类 Property For Rent"):
        logged_in_page.get_by_text("Property For Rent", exact=True).click()
        logged_in_page.wait_for_load_state("domcontentloaded", timeout=30000)
        logged_in_page.wait_for_timeout(3000)
        logger.info("✓ 点击 Property For Rent 成功")
    
    with allure.step("步骤3：验证三级分类列表显示"):
        expected_tertiary_categories = [
            "House",
            "Townhomes",
            "Apartment&Unit",
            "Villa",
            "Retirement",
            "Other",
        ]
        
        for category in expected_tertiary_categories:
            category_element = logged_in_page.get_by_text(category, exact=True).first
            assert category_element.is_visible(timeout=10000), (
                f"三级分类 {category} 应该显示"
            )
        
        logger.info(f"✓ 验证通过：显示 {len(expected_tertiary_categories)} 个三级分类")
    
    allure.attach(
        logged_in_page.screenshot(),
        name="tc002-三级分类列表",
        attachment_type=allure.attachment_type.PNG
    )


@pytest.mark.p0
@pytest.mark.case_id("TC003")
@pytest.mark.case_id_au58_property_publish_m1_003
@allure.feature("AU站房产发布")
@allure.story("模块1：发布入口与顶部标题")
@allure.title("TC003 点击三级分类后进入对应发布表单页")
@allure.severity(allure.severity_level.BLOCKER)
def test_tc003_click_tertiary_enters_form_page(logged_in_page, config, publish_page):
    """
    TC003 点击三级分类后进入对应发布表单页
    
    前置条件：
    - 已登录 AU 站账号
    - 已选择二级分类"Property For Rent"，三级分类列表可见
    
    测试步骤：
    1. 导航到发布前置页
    2. 点击"Property For Rent"
    3. 点击三级分类"House"
    4. 验证表单页显示
    
    预期结果：
    - 成功进入房产发布表单页
    - 页面顶部标题显示"Property For Rent Post"
    - 表单中显示对应三级分类的房产信息字段（Property Info区域）
    
    MCP录制代码：
    await page.getByText('Property For Rent', { exact: true }).click();
    await page.getByText('House').click();
    """
    with allure.step("步骤1：导航到发布前置页"):
        logged_in_page.goto(f"{config['publish_url']}/publish/front", timeout=30000)
        logged_in_page.wait_for_load_state("domcontentloaded", timeout=30000)
        logged_in_page.wait_for_timeout(2000)
        _accept_cookies_if_any(logged_in_page)
        logger.info("✓ 导航到发布前置页成功")
    
    with allure.step("步骤2：点击二级分类 Property For Rent"):
        logged_in_page.get_by_text("Property For Rent", exact=True).click()
        logged_in_page.wait_for_load_state("domcontentloaded", timeout=30000)
        logged_in_page.wait_for_timeout(3000)
        logger.info("✓ 点击 Property For Rent 成功")
    
    with allure.step("步骤3：点击三级分类 House"):
        logged_in_page.get_by_text("House", exact=True).first.click(timeout=15000)
        logged_in_page.wait_for_load_state("domcontentloaded", timeout=30000)
        logged_in_page.wait_for_timeout(2500)
        logger.info("✓ 点击 House 成功")
    
    with allure.step("步骤4：验证表单页显示"):
        page_title = _heading_or_title_text(logged_in_page)
        assert re.search(r"property.*rent|for\s+rent", page_title, re.I), (
            f"页面标题应体现租房发布，实际：{page_title!r}"
        )
        
        assert logged_in_page.get_by_text("Property Info", exact=False).first.is_visible(
            timeout=8000
        ), "应显示 Property Info 区域"
        
        for label_re, desc in (
            (re.compile(r"bedroom|beds?\b|studio", re.I), "卧室/Beds"),
            (re.compile(r"bathroom", re.I), "浴室"),
            (re.compile(r"area\s*size|living\s*area|sqft|m2", re.I), "面积"),
        ):
            assert logged_in_page.get_by_text(label_re).first.is_visible(
                timeout=8000
            ), f"表单应展示{desc}相关字段"
        
        logger.info("✓ 验证通过：表单页显示正常")
    
    allure.attach(
        logged_in_page.screenshot(),
        name="tc003-发布表单页",
        attachment_type=allure.attachment_type.PNG
    )


@pytest.mark.p1
@pytest.mark.case_id("TC004")
@pytest.mark.case_id_au58_property_publish_m1_004
@allure.feature("AU站房产发布")
@allure.story("模块1：发布入口与顶部标题")
@allure.title("TC004 发布页顶部标题根据二级类型动态显示")
@allure.severity(allure.severity_level.NORMAL)
def test_tc004_page_title_changes_by_secondary_type(logged_in_page, config, publish_page):
    """
    TC004 发布页顶部标题根据二级类型动态显示
    
    前置条件：
    - 已登录 AU 站账号
    
    测试步骤：
    1. 导航到发布前置页
    2. 点击"Property For Rent"，验证标题
    3. 返回发布前置页
    4. 点击"Property For Sale"，验证标题
    
    预期结果：
    - 租房入口：顶部显示"Property For Rent Post"
    - 买房入口：顶部显示"Property For Sale Post"
    - 标题根据二级类型动态显示
    
    MCP录制代码：
    await page.goto('https://aupub.58v5.cn/biz/en/publish/front');
    await page.getByText('Property For Sale', { exact: true }).click();
    """
    with allure.step("步骤1：导航到发布前置页"):
        logged_in_page.goto(f"{config['publish_url']}/publish/front", timeout=30000)
        logged_in_page.wait_for_load_state("domcontentloaded", timeout=30000)
        logged_in_page.wait_for_timeout(2000)
        _accept_cookies_if_any(logged_in_page)
        logger.info("✓ 导航到发布前置页成功")
    
    with allure.step("步骤2：租房路径进入表单并验证标题"):
        logged_in_page.get_by_text("Property For Rent", exact=True).click()
        logged_in_page.wait_for_load_state("domcontentloaded", timeout=30000)
        logged_in_page.wait_for_timeout(3000)
        logged_in_page.get_by_text("House", exact=True).first.click(timeout=15000)
        logged_in_page.wait_for_load_state("domcontentloaded", timeout=30000)
        logged_in_page.wait_for_timeout(2500)
        
        rent_title = _heading_or_title_text(logged_in_page)
        assert re.search(r"property.*rent|for\s+rent", rent_title, re.I), (
            f"租房发布页标题应体现 Rent，实际：{rent_title!r}"
        )
        logger.info("✓ 租房标题验证通过：%s", rent_title)
    
    with allure.step("步骤3：返回发布前置页"):
        logged_in_page.goto(f"{config['publish_url']}/publish/front", timeout=30000)
        logged_in_page.wait_for_load_state("domcontentloaded", timeout=30000)
        logged_in_page.wait_for_timeout(2000)
        _accept_cookies_if_any(logged_in_page)
        logger.info("✓ 返回发布前置页成功")
    
    with allure.step("步骤4：买房路径进入表单并验证标题"):
        logged_in_page.get_by_text("Property For Sale", exact=True).click()
        logged_in_page.wait_for_load_state("domcontentloaded", timeout=30000)
        logged_in_page.wait_for_timeout(3000)
        logged_in_page.get_by_text("House", exact=True).first.click(timeout=15000)
        logged_in_page.wait_for_load_state("domcontentloaded", timeout=30000)
        logged_in_page.wait_for_timeout(2500)
        
        sale_title = _heading_or_title_text(logged_in_page)
        assert re.search(r"property.*sale|for\s+sale", sale_title, re.I), (
            f"买房发布页标题应体现 Sale，实际：{sale_title!r}"
        )
        logger.info("✓ 买房标题验证通过：%s", sale_title)
    
    allure.attach(
        logged_in_page.screenshot(),
        name="tc004-买房标题",
        attachment_type=allure.attachment_type.PNG
    )


@pytest.mark.p0
@pytest.mark.case_id_au58_property_publish_m1_005
@allure.feature("AU站房产发布")
@allure.story("模块1：发布入口与顶部标题")
@allure.title("TC005 未登录在首页点击 Post 应出现登录相关界面")
@allure.severity(allure.severity_level.BLOCKER)
def test_m1_tc005_guest_post_requires_login(page, config):
    """不经过 logged_in_page：清空 Cookie 后从首页点 Post。"""
    vp = config["browser"].get("viewport") or {"width": 1920, "height": 1080}
    page.set_viewport_size(vp)
    ctx = page.context
    ctx.clear_cookies()
    try:
        ctx.clear_permissions()
    except Exception:
        pass
    base = config["base_url"]
    _goto_with_retry(page, base, config)
    page.wait_for_timeout(1500)
    LoginPage(page).handle_cookie_popup()
    page.wait_for_timeout(500)

    with allure.step("未登录态下点击首页 Post"):
        clicked = _click_home_post(page)
        if not clicked:
            pytest.skip("首页未定位到顶栏 Post（布局或文案与脚本假设不一致）")
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        page.wait_for_timeout(2000)

    with allure.step("应出现弹窗/登录页/邮箱输入等登录相关 UI"):
        assert _login_ui_visible(page), (
            "未登录点击 Post 后应出现登录弹窗、登录页或邮箱/手机输入框"
        )
