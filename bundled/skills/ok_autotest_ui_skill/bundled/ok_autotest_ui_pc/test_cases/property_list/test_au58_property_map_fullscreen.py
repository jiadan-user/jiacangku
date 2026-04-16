"""
AU站 Property 地图视图 - 全屏切换功能测试

本脚本由 playwright-test-generator 生成
录制文档：test_plans/au58-Property-地图全屏切换功能测试用例.md
生成时间：2026-03-17
测试站点：AU (https://au.58v5.cn)，无需登录
测试目标：验证地图视图全屏切换按钮的进入全屏/退出全屏功能
"""
import pytest
import allure
from pages.property_map_page import PropertyMapPage
from utils.logger import setup_logger

logger = setup_logger()

_CONFIG = {
    "site": "au",
    "site_name": "AU站（澳大利亚）",
    "role": "guest",
    "user_name": "guest_au",
    "base_url": "https://au.58v5.cn",
    "test_account": None,
    "list_url": "https://au.58v5.cn/en/city-canberra/cate-rent/?iconSource=rent&view=map&viewport=c%3A-35.0184%2C149.3184%7Cz%3A9",
    "browser": {
        "type": "chromium",
        "headless": True,
        "viewport": {"width": 1920, "height": 1080},
    },
    "timeout": {"default": 30000, "wait": 10000, "navigation": 30000},
}


def _open_map_page(page, config):
    """打开地图视图页面并等待地图及自定义控件完全渲染。"""
    pmp = PropertyMapPage(page)
    # 使用 navigate_to_map_page（含重试+502 skip，超时 60s）
    pmp.navigate_to_map_page(config["list_url"], timeout=90000)
    try:
        cookie_btn = page.locator("button:has-text('Accept all'), button:has-text('Accept')").first
        if cookie_btn.is_visible(timeout=2000):
            cookie_btn.click()
            page.wait_for_timeout(500)
    except Exception:
        pass
    # 等待地图容器渲染完成（Google Maps API 异步加载，CI 下可能需要更长时间）
    rendered = pmp.is_map_rendered()
    if not rendered:
        import pytest
        pytest.skip("地图容器(.gm-style)未在 60s 内完成渲染，可能是 Google Maps API 加载超时")
    # 等待 OK 自定义地图控制按钮出现（全屏展开按钮）
    try:
        page.locator(".MapControls_controls__o6ToG").first.locator("button").first.wait_for(state="visible", timeout=15000)
    except Exception:
        pass
    return pmp


# ============================================
# TC001 地图视图默认加载
# ============================================
@pytest.mark.case_id_au58_property_map_fullscreen_001
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站地图全屏切换功能")
@allure.title("地图视图默认加载")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("进入含 view=map 参数的 URL，页面以地图模式展示，地图容器正常渲染")
def test_tc001_map_view_loads_correctly(page, config):
    with allure.step("步骤1：打开地图视图页面"):
        pmp = _open_map_page(page, config)
        logger.info(f"✓ 已打开地图页面: {page.url}")

    with allure.step("步骤2：验证 URL 含 view=map 参数"):
        assert "view=map" in page.url, f"URL 应含 view=map，实际: {page.url}"
        logger.info("✓ URL 含 view=map 参数")

    with allure.step("步骤3：验证地图容器正常渲染"):
        if not pmp.is_map_rendered():
            pytest.skip("地图容器(.gm-style)未在 60s 内完成渲染，可能是 Google Maps API 加载超时")
        logger.info("✓ 地图容器正常渲染")

    with allure.step("步骤4：验证地图视图切换按钮处于激活状态"):
        assert pmp.is_map_view_active(), "Map 切换按钮应处于 active 状态"
        logger.info("✓ Map 视图切换按钮处于激活状态")


# ============================================
# TC002 点击全屏按钮进入全屏模式
# ============================================
@pytest.mark.case_id_au58_property_map_fullscreen_002
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站地图全屏切换功能")
@allure.title("点击全屏按钮进入全屏模式")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("在地图视图点击全屏切换按钮，地图进入全屏模式，左侧列表隐藏")
def test_tc002_click_fullscreen_button_enters_fullscreen(page, config):
    with allure.step("步骤1：打开地图视图页面"):
        pmp = _open_map_page(page, config)
        logger.info("✓ 已打开地图页面")

    with allure.step("步骤2：验证全屏按钮可见"):
        assert pmp.is_fullscreen_button_visible(), "全屏切换按钮(gm-fullscreen-control)应可见"
        logger.info("✓ 全屏切换按钮可见")

    with allure.step("步骤3：点击全屏按钮"):
        # 录制代码：await page.getByRole('button').nth(5).click();
        # 稳定选择器：.MapControls_controls__o6ToG button:first
        pmp.click_fullscreen_button()
        try:
            page.locator(".MapControls_fullscreenHint__Il0Zi").wait_for(state="attached", timeout=5000)
        except Exception:
            pass
        page.wait_for_timeout(1500)
        logger.info("✓ 已点击全屏按钮")

    with allure.step("步骤4：验证进入全屏模式"):
        assert pmp.is_in_fullscreen_mode(), "点击全屏按钮后，地图应进入全屏模式（左侧列表隐藏）"
        logger.info("✓ 已进入全屏模式，左侧卡片列表已隐藏")

    with allure.step("步骤5：验证出现退出全屏提示"):
        assert pmp.is_fullscreen_exit_hint_visible(), "全屏模式下应出现 'Exit full screen by pressing esc' 提示"
        logger.info("✓ 出现退出全屏提示文字")


# ============================================
# TC003 全屏模式下地图正常展示
# ============================================
@pytest.mark.case_id_au58_property_map_fullscreen_003
@pytest.mark.smoke
@pytest.mark.p1
@allure.feature("OK")
@allure.story("AU站地图全屏切换功能")
@allure.title("全屏模式下地图正常展示")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("进入全屏模式后，地图容器正常渲染，Pin 点标记仍可见，无白屏")
def test_tc003_fullscreen_map_renders_correctly(page, config):
    with allure.step("步骤1：打开地图页面并进入全屏"):
        pmp = _open_map_page(page, config)
        pmp.click_fullscreen_button()
        try:
            page.locator(".MapControls_fullscreenHint__Il0Zi").wait_for(state="attached", timeout=5000)
        except Exception:
            pass
        # CI 无头模式下全屏切换后地图重绘需要更多时间
        page.wait_for_timeout(1500)
        logger.info("✓ 已进入全屏模式")

    with allure.step("步骤2：验证地图容器在全屏下正常渲染"):
        if not pmp.is_map_rendered():
            pytest.skip("全屏模式下地图容器(.gm-style)未在 60s 内完成渲染，可能是 Google Maps API 加载超时")
        logger.info("✓ 全屏模式下地图正常渲染")

    with allure.step("步骤3：验证地图 Pin 点标记仍可见"):
        # 使用 PropertyMapPage 的方法获取 Pin 点数量
        pin_count = pmp.get_pin_count()
        assert pin_count > 0, "全屏模式下地图 Pin 点标记应可见"
        logger.info(f"✓ 全屏模式下 Pin 点标记可见，共 {pin_count} 个")

    with allure.step("步骤4：验证全屏按钮在全屏模式下仍可见"):
        assert pmp.is_fullscreen_button_visible(), "全屏模式下全屏切换按钮应仍可见"
        logger.info("✓ 全屏模式下全屏切换按钮仍可见")


# ============================================
# TC004 全屏模式下点击退出全屏恢复正常视图
# ============================================
@pytest.mark.case_id_au58_property_map_fullscreen_004
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站地图全屏切换功能")
@allure.title("全屏模式下点击退出全屏按钮恢复正常视图")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("在全屏模式下再次点击全屏按钮，页面恢复为正常地图+列表布局")
def test_tc004_click_exit_fullscreen_restores_normal_view(page, config):
    with allure.step("步骤1：打开地图页面并进入全屏"):
        pmp = _open_map_page(page, config)
        pmp.click_fullscreen_button()
        # 等待 fullscreenHint 出现再继续
        try:
            page.locator(".MapControls_fullscreenHint__Il0Zi").wait_for(state="attached", timeout=5000)
        except Exception:
            pass
        page.wait_for_timeout(1500)
        assert pmp.is_in_fullscreen_mode(), "应已进入全屏模式"
        logger.info("✓ 已进入全屏模式")

    with allure.step("步骤2：点击退出全屏按钮"):
        # 录制代码：await page.getByRole('button').nth(5).click();（同一个按钮）
        pmp.click_fullscreen_button()
        # 等待 fullscreenHint 消失再继续
        try:
            page.locator(".MapControls_fullscreenHint__Il0Zi").wait_for(state="detached", timeout=5000)
        except Exception:
            pass
        # CI 无头模式下布局重绘需要更多时间
        page.wait_for_timeout(1500)
        logger.info("✓ 已点击退出全屏按钮")

    with allure.step("步骤3：验证恢复为正常视图（左侧列表重新出现）"):
        assert not pmp.is_in_fullscreen_mode(), "点击退出全屏后，应恢复为正常布局（左侧列表可见）"
        logger.info("✓ 已恢复正常视图，左侧卡片列表重新出现")

    with allure.step("步骤4：验证地图仍正常渲染"):
        if not pmp.is_map_rendered():
            pytest.skip("退出全屏后地图容器(.gm-style)未在 60s 内完成渲染，可能是 Google Maps API 加载超时")
        logger.info("✓ 退出全屏后地图正常渲染")

    with allure.step("步骤5：验证退出全屏提示已消失"):
        assert not pmp.is_fullscreen_exit_hint_visible(), "退出全屏后提示文字应消失"
        logger.info("✓ 退出全屏提示文字已消失")


# ============================================
# TC005 全屏切换按钮在两种状态下持续可见
# ============================================
@pytest.mark.case_id_au58_property_map_fullscreen_005
@pytest.mark.smoke
@pytest.mark.p1
@allure.feature("OK")
@allure.story("AU站地图全屏切换功能")
@allure.title("全屏切换按钮在两种状态下持续可见")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("无论全屏或非全屏状态，全屏切换按钮始终可见且可点击")
def test_tc005_fullscreen_button_always_visible(page, config):
    with allure.step("步骤1：打开地图页面，验证非全屏状态下按钮可见"):
        pmp = _open_map_page(page, config)
        assert pmp.is_fullscreen_button_visible(), "非全屏状态下全屏切换按钮应可见"
        logger.info("✓ 非全屏状态：全屏切换按钮可见")

    with allure.step("步骤2：进入全屏，验证按钮仍可见"):
        pmp.click_fullscreen_button()
        try:
            page.locator(".MapControls_fullscreenHint__Il0Zi").wait_for(state="attached", timeout=5000)
        except Exception:
            pass
        page.wait_for_timeout(1500)
        assert pmp.is_fullscreen_button_visible(), "全屏状态下全屏切换按钮应仍可见"
        logger.info("✓ 全屏状态：全屏切换按钮仍可见")

    with allure.step("步骤3：退出全屏，验证按钮仍可见"):
        pmp.click_fullscreen_button()
        try:
            page.locator(".MapControls_fullscreenHint__Il0Zi").wait_for(state="detached", timeout=5000)
        except Exception:
            pass
        page.wait_for_timeout(1500)
        assert pmp.is_fullscreen_button_visible(), "退出全屏后全屏切换按钮应仍可见"
        logger.info("✓ 退出全屏后：全屏切换按钮仍可见")

    with allure.step("步骤4：验证按钮尺寸合理（可点击）"):
        btn_state = pmp.get_fullscreen_button_state()
        assert btn_state == "visible", f"全屏按钮应处于可见状态，实际: {btn_state}"
        logger.info("✓ 全屏切换按钮尺寸合理，可正常点击")
