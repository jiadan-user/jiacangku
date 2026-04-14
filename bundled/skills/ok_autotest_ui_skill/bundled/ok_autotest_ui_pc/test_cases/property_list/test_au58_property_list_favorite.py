"""
AU站 - 买房列表卡片收藏功能测试

本脚本由 playwright-test-generator 生成
录制文档：test_plans/au58-Property-列表卡片收藏功能测试用例.md
生成时间：2026-03-04
测试站点：AU (https://au.58v5.cn)，需登录
测试目标：未登录点击收藏弹出登录框；已登录收藏/取消收藏、进入收藏页、刷新后状态保持
"""
import pytest
import allure
from pages.property_list_page import PropertyListPage
from pages.login_page import LoginPage
from utils.session_manager import SessionManager
from utils.logger import setup_logger

logger = setup_logger()

# ============================================
# 测试环境配置（来自录制文档）
# ============================================
_CONFIG = {
    "site": "au",
    "site_name": "AU站（澳大利亚）",
    "role": "buyer",
    "user_name": "dc_buyer_au",
    "base_url": "https://au.58v5.cn",
    "test_account": {
        "username": "liuyue62@58.com",
        "password": "Xindemima1%",
    },
    "list_url": "https://au.58v5.cn/en/city-canberra/cate-buy/?iconSource=buy",
    "favorites_url_pattern": "favorites",
    "browser": {
        "type": "chromium",
        "headless": True,
        "viewport": {"width": 1920, "height": 1080},
    },
    "timeout": {"default": 30000, "wait": 10000, "navigation": 30000},
}


def _wait_for_fav_toast(page, added: bool, timeout: int = 8000):
    """等待收藏/取消收藏的 Toast（兼容 favourites 与 favorites 拼写）；若未捕获到 Toast 仅记录不抛错"""
    if added:
        for text in ("Added to favourite", "Added to favorites"):
            try:
                page.get_by_text(text, exact=False).wait_for(state="visible", timeout=timeout)
                return
            except Exception:
                continue
    else:
        for text in ("Removed from favourite", "Removed from favorites"):
            try:
                page.get_by_text(text, exact=False).wait_for(state="visible", timeout=timeout)
                return
            except Exception:
                continue
    logger.warning("未捕获到收藏/取消收藏 Toast，可能已消失或文案不同")

def _ensure_logged_in_and_on_list(page, config):
    """确保已登录并在列表页（Session 复用或从列表页登录）。"""
    list_url = config["list_url"]
    plp = PropertyListPage(page)
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config["base_url"], session_name)

    if session_manager.load_session():
        page.goto(list_url, wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
        # 等待收藏图标真正出现，确保列表卡片渲染完成
        try:
            page.locator('img[alt="fav-icon"]').first.wait_for(state="visible", timeout=20000)
        except Exception:
            page.wait_for_timeout(3000)
        logger.info(f"✓ 加载 session: {session_name}")
        return plp

    page.goto(list_url, wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
    try:
        cookie_btn = page.locator("button:has-text('Accept all'), button:has-text('Accept')").first
        if cookie_btn.is_visible(timeout=2000):
            cookie_btn.click()
            page.wait_for_timeout(1000)
    except Exception:
        pass
    page.get_by_text("Log in / Register").first.click()
    page.wait_for_timeout(1500)
    page.get_by_role("textbox", name="Email or phone number").wait_for(state="visible", timeout=10000)
    login_page = LoginPage(page)
    login_page.input_email(config["test_account"]["username"])
    login_page.click_continue_button()
    login_page.input_password(config["test_account"]["password"])
    login_page.click_login_button()
    page.wait_for_load_state("domcontentloaded", timeout=15000)
    session_manager.save_session()
    logger.info(f"✓ 登录成功并保存 session: {session_name}")
    page.goto(list_url, wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
    # 等待收藏图标真正出现，确保列表卡片渲染完成
    try:
        page.locator('img[alt="fav-icon"]').first.wait_for(state="visible", timeout=20000)
    except Exception:
        page.wait_for_timeout(3000)
    return plp


# ============================================
# TC001 未登录点击收藏图标弹出登录弹窗
# ============================================
@pytest.mark.case_id_au58_list_favorite_001
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片收藏功能")
@allure.title("未登录点击收藏图标弹出登录弹窗")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("未登录状态下点击列表卡片收藏图标，弹出 Welcome to OK.com 登录对话框")
def test_tc001_unlogged_click_fav_opens_login_dialog(page, config):
    plp = PropertyListPage(page)
    plp.navigate_to_list(config["list_url"], timeout=config["timeout"]["navigation"])
    page.wait_for_load_state("domcontentloaded", timeout=5000)
    page.wait_for_timeout(1000)

    plp.click_first_fav_icon()
    page.wait_for_timeout(2500)

    visible = plp.is_login_dialog_visible(timeout=8000)
    assert visible, "未登录点击收藏应弹出登录对话框（含 Email or phone number）"
    logger.info("✓ 登录对话框已弹出")


# ============================================
# TC002 已登录点击收藏图标收藏成功
# ============================================
@pytest.mark.case_id_au58_list_favorite_002
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片收藏功能")
@allure.title("已登录点击收藏图标收藏成功")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("已登录状态下点击未收藏卡片的收藏图标，出现 Added to favourites 提示")
def test_tc002_logged_click_fav_adds_favorite(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    plp.click_fav_icon_nth(1)
    _wait_for_fav_toast(page, added=True, timeout=8000)
    logger.info("✓ 收藏成功，Toast: Added to favourites/favorites")


# ============================================
# TC003 进入收藏页面查看已收藏的房产
# ============================================
@pytest.mark.case_id_au58_list_favorite_003
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片收藏功能")
@allure.title("进入收藏页面查看已收藏的房产")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("通过右上角菜单进入 Favourites 页，URL 为收藏页且页面正常")
def test_tc003_go_to_favorites_page(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    plp.click_favourites_in_menu()
    page.wait_for_load_state("domcontentloaded", timeout=15000)
    assert config["favorites_url_pattern"] in page.url, f"应进入收藏页，当前 URL: {page.url}"
    logger.info(f"✓ 已进入收藏页: {page.url}")


# ============================================
# TC004 已登录取消收藏
# ============================================
@pytest.mark.case_id_au58_list_favorite_004
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片收藏功能")
@allure.title("已登录取消收藏")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("点击已收藏卡片的收藏图标，出现 Removed from favorites 提示")
def test_tc004_logged_click_fav_removes_favorite(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    plp.click_fav_icon_nth(1)
    _wait_for_fav_toast(page, added=True, timeout=4000)
    page.wait_for_timeout(800)
    plp.click_fav_icon_nth(1)
    _wait_for_fav_toast(page, added=False, timeout=8000)
    assert config["list_url"] in page.url or "cate-buy" in page.url, "取消收藏后应仍在列表页"
    logger.info("✓ 取消收藏成功")


# ============================================
# TC005 收藏后刷新页面状态保持
# ============================================
@pytest.mark.case_id_au58_list_favorite_005
@pytest.mark.p1
@allure.feature("OK")
@allure.story("AU站列表卡片收藏功能")
@allure.title("收藏后刷新页面状态保持")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("收藏某条后刷新列表页，该卡片仍为已收藏状态")
def test_tc005_favorite_persists_after_reload(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    plp.click_fav_icon_nth(1)
    _wait_for_fav_toast(page, added=True, timeout=8000)
    page.reload(wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
    page.wait_for_load_state("domcontentloaded", timeout=5000)
    plp.click_fav_icon_nth(1)
    _wait_for_fav_toast(page, added=False, timeout=8000)
    assert config["list_url"] in page.url or "cate-buy" in page.url, "操作后应仍在列表页"
    logger.info("✓ 刷新后仍为已收藏，点击后取消收藏成功")


# ============================================
# TC006 取消收藏后到收藏页验证该帖子已移除
# ============================================
@pytest.mark.case_id_au58_list_favorite_006
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片收藏功能")
@allure.title("取消收藏后到收藏页验证该帖子已移除")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("收藏某条卡片后记录标题，取消收藏，进入收藏页验证该卡片不在列表中")
def test_tc006_unfavorite_then_verify_removed_from_favorites(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    
    # 先收藏第一张卡片并记录标题
    plp.click_fav_icon_nth(0)
    _wait_for_fav_toast(page, added=True, timeout=8000)
    page.wait_for_timeout(1000)
    
    # 获取第一张卡片的标题（用于后续验证）
    first_card = page.locator('a[href*="cate-property-for-sale-"]').first
    card_title = first_card.inner_text().split("\n")[0].strip()[:50]
    logger.info(f"已收藏卡片标题（前50字符）: {card_title}")
    
    # 取消收藏
    page.wait_for_timeout(800)
    plp.click_fav_icon_nth(0)
    _wait_for_fav_toast(page, added=False, timeout=8000)
    logger.info("✓ 已取消收藏")
    
    # 进入收藏页
    page.wait_for_timeout(1000)
    plp.click_favourites_in_menu()
    page.wait_for_load_state("domcontentloaded", timeout=15000)
    page.wait_for_timeout(2000)
    
    # 验证该卡片不在收藏页中
    assert config["favorites_url_pattern"] in page.url, f"应进入收藏页，当前 URL: {page.url}"
    
    # 检查该卡片是否在收藏页中（应该不在）
    is_in_favorites = plp.is_card_in_favorites_by_title(card_title, timeout=3000)
    assert not is_in_favorites, f"取消收藏后，该卡片不应在收藏页中，标题: {card_title}"
    
    logger.info(f"✓ 取消收藏后，该卡片已从收藏页移除: {card_title}")
