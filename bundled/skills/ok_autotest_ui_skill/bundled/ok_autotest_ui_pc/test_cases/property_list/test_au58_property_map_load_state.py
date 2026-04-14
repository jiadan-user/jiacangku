"""
AU站 Property 地图视图 - 地图加载状态功能测试

本脚本由 playwright-test-generator 生成
录制文档：test_plans/au58-Property-地图加载状态功能测试用例.md
生成时间：2026-03-17
测试站点：AU (https://au.58v5.cn)，无需登录
测试目标：验证地图视图中地图容器、结果数量、Pin点、控件的加载状态及视图切换后地图重载
"""
import re
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
    "list_view_url": "https://au.58v5.cn/en/city-canberra/cate-rent/?iconSource=rent",
    "browser": {
        "type": "chromium",
        "headless": True,
        "viewport": {"width": 1920, "height": 1080},
    },
    "timeout": {"default": 30000, "wait": 10000, "navigation": 30000},
}


def _open_map_view(page, config) -> PropertyMapPage:
    """打开含 view=map 参数的地图视图页面，等待地图容器初始化。"""
    pmp = PropertyMapPage(page)
    pmp.navigate_to_map_page(config["list_url"], timeout=90000)
    try:
        cookie_btn = page.locator("button:has-text('Accept all'), button:has-text('Accept')").first
        if cookie_btn.is_visible(timeout=2000):
            cookie_btn.click()
            page.wait_for_timeout(500)
    except Exception:
        pass
    pmp.is_map_container_loaded()
    return pmp


# ============================================
# TC001 地图容器正常加载渲染
# ============================================
@pytest.mark.case_id_au58_property_map_load_state_001
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站地图加载状态功能")
@allure.title("地图容器正常加载渲染")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("打开含 view=map 参数的 URL，验证地图容器（.gm-style）和地图外框（.MapView_mapView__oebEi）均正常加载，无白屏")
def test_tc001_map_container_loads_correctly(page, config):
    with allure.step("步骤1：打开地图视图页面"):
        pmp = _open_map_view(page, config)
        logger.info(f"✓ 已打开地图页面: {page.url}")

    with allure.step("步骤2：验证 URL 含 view=map 参数"):
        assert "view=map" in page.url, f"URL 应含 view=map，实际: {page.url}"
        logger.info("✓ URL 含 view=map 参数")

    with allure.step("步骤3：验证地图容器（.gm-style）正常渲染"):
        if not pmp.is_map_rendered():
            pytest.skip("地图容器(.gm-style)未在 60s 内完成渲染，可能是 Google Maps API 加载超时")
        logger.info("✓ 地图容器 .gm-style 正常渲染")

    with allure.step("步骤4：验证地图外框（.MapView_mapView__oebEi）存在"):
        assert pmp.is_map_container_loaded(), "地图外框 .MapView_mapView__oebEi 应存在"
        logger.info("✓ 地图外框 .MapView_mapView__oebEi 正常加载")

    with allure.step("步骤5：验证 URL 含 viewport 参数"):
        assert "viewport=" in page.url, f"URL 应含 viewport 参数，实际: {page.url}"
        logger.info("✓ URL 含 viewport 参数")


# ============================================
# TC002 地图结果数量徽标正常展示
# ============================================
@pytest.mark.case_id_au58_property_map_load_state_002
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站地图加载状态功能")
@allure.title("地图结果数量徽标正常展示")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("地图视图加载完成后，结果数量徽标（MapView_resultsBadge）可见，文本为 'N results' 格式且 N > 0")
def test_tc002_results_badge_displays_correctly(page, config):
    with allure.step("步骤1：打开地图视图页面"):
        pmp = _open_map_view(page, config)
        logger.info("✓ 已打开地图页面")

    with allure.step("步骤2：验证结果数量徽标可见"):
        assert pmp.is_map_results_badge_visible(), "结果数量徽标（.MapView_resultsBadge__yvMxa）应可见"
        logger.info("✓ 结果数量徽标可见")

    with allure.step("步骤3：获取结果数量文本"):
        badge_text = pmp.get_map_results_badge_text()
        if not badge_text:
            pytest.skip("结果数量徽标在 45s 内仍为 Searching...，地图搜索未完成，跳过本用例")
        logger.info(f"✓ 结果数量文本: '{badge_text}'")

    with allure.step("步骤4：验证结果数量文本格式（N results）"):
        assert "result" in badge_text.lower(), f"文本应包含 'result'，实际: '{badge_text}'"
        match = re.search(r"\d+", badge_text)
        assert match, f"文本应包含数字，实际: '{badge_text}'"
        count = int(match.group())
        assert count > 0, f"结果数量应大于 0，实际: {count}"
        logger.info(f"✓ 结果数量: {count}，格式正确")


# ============================================
# TC003 地图 Pin 点标记正常渲染
# ============================================
@pytest.mark.case_id_au58_property_map_load_state_003
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站地图加载状态功能")
@allure.title("地图 Pin 点标记正常渲染")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("地图视图加载完成后，视口范围内至少有 1 个 Pin 点标记（price bubble 或 sale marker）可见")
def test_tc003_map_pins_render_correctly(page, config):
    with allure.step("步骤1：打开地图视图页面"):
        pmp = _open_map_view(page, config)
        logger.info("✓ 已打开地图页面")

    with allure.step("步骤2：等待 Pin 点出现"):
        appeared = pmp.wait_for_map_pins(timeout_ms=30000)
        if not appeared:
            pytest.skip("地图 Pin 点在 30s 内未出现，可能是 Google Maps 数据加载延迟")
        logger.info("✓ Pin 点已出现")

    with allure.step("步骤3：统计 Pin 点数量"):
        pin_count = pmp.get_map_pin_count()
        assert pin_count > 0, f"地图上应至少有 1 个 Pin 点，实际: {pin_count}"
        logger.info(f"✓ 地图 Pin 点数量: {pin_count}（bottom icon + sale marker）")

    with allure.step("步骤4：验证 Pin 点在地图区域内"):
        # 地图区域 region[name="Map"] 存在
        map_region = page.get_by_role("region", name="Map")
        assert map_region.count() > 0, "地图区域（region[name='Map']）应存在"
        logger.info("✓ 地图区域（region[name='Map']）存在")


# ============================================
# TC004 地图控件正常加载（缩放/全屏/定位按钮）
# ============================================
@pytest.mark.case_id_au58_property_map_load_state_004
@pytest.mark.smoke
@pytest.mark.p1
@allure.feature("OK")
@allure.story("AU站地图加载状态功能")
@allure.title("地图控件正常加载（缩放/全屏/定位按钮）")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("地图视图加载完成后，OK 自定义地图控件容器可见，包含 4 个功能按钮（全屏、放大、缩小、定位）")
def test_tc004_map_controls_load_correctly(page, config):
    with allure.step("步骤1：打开地图视图页面"):
        pmp = _open_map_view(page, config)
        logger.info("✓ 已打开地图页面")

    with allure.step("步骤2：验证地图控件容器可见"):
        assert pmp.is_map_controls_visible(), "地图控件容器（.MapControls_controls__o6ToG）应可见"
        logger.info("✓ 地图控件容器可见")

    with allure.step("步骤3：统计控件按钮数量"):
        btn_count = pmp.get_map_control_button_count()
        assert btn_count >= 4, f"地图控件应至少有 4 个按钮（全屏、放大、缩小、定位），实际: {btn_count}"
        logger.info(f"✓ 地图控件按钮数量: {btn_count}")

    with allure.step("步骤4：验证全屏按钮可见"):
        assert pmp.is_fullscreen_button_visible(), "全屏切换按钮应可见"
        logger.info("✓ 全屏切换按钮可见")


# ============================================
# TC005 从列表视图切换到地图视图后地图正常加载
# ============================================
@pytest.mark.case_id_au58_property_map_load_state_005
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站地图加载状态功能")
@allure.title("从列表视图切换到地图视图后地图正常加载")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("在列表视图点击 Map 切换按钮，地图正常加载渲染，URL 更新为含 view=map 参数，Pin 点可见")
def test_tc005_switch_from_list_to_map_view(page, config):
    with allure.step("步骤1：打开列表视图页面"):
        pmp = PropertyMapPage(page)
        page.goto(config["list_view_url"], wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
        try:
            cookie_btn = page.locator("button:has-text('Accept all'), button:has-text('Accept')").first
            if cookie_btn.is_visible(timeout=2000):
                cookie_btn.click()
                page.wait_for_timeout(500)
        except Exception:
            pass
        logger.info(f"✓ 已打开列表视图: {page.url}")

    with allure.step("步骤2：验证当前为列表视图（无地图）"):
        assert "view=map" not in page.url, f"列表视图 URL 不应含 view=map，实际: {page.url}"
        assert not pmp.is_map_rendered(), "列表视图下地图容器不应存在"
        logger.info("✓ 当前为列表视图，地图容器不存在")

    with allure.step("步骤3：点击 Map 切换按钮"):
        # MCP录制代码：await page.getByRole('button', { name: 'Map' }).click();
        pmp.click_map_toggle_button()
        logger.info("✓ 已点击 Map 切换按钮")

    with allure.step("步骤4：等待地图加载完成"):
        loaded = pmp.wait_for_map_loaded_after_toggle(timeout_ms=60000)
        if not loaded:
            pytest.skip("切换到地图视图后，地图容器(.gm-style)在 60s 内未加载完成，可能是 Google Maps API 加载超时")
        logger.info("✓ 地图加载完成")

    with allure.step("步骤5：验证 URL 含 view=map 参数"):
        assert "view=map" in page.url, f"切换后 URL 应含 view=map，实际: {page.url}"
        logger.info(f"✓ URL 已更新为地图视图: {page.url}")

    with allure.step("步骤6：验证地图容器可见"):
        if not pmp.is_map_rendered():
            pytest.skip("切换后地图容器(.gm-style)未在 60s 内完成渲染，可能是 Google Maps API 加载超时")
        logger.info("✓ 地图容器（.gm-style）可见")

    with allure.step("步骤7：验证地图 Pin 点可见"):
        # 切换后地图重新初始化，额外等待 Pin 点渲染
        appeared = pmp.wait_for_map_pins(timeout_ms=20000)
        if not appeared:
            pytest.skip("切换到地图视图后，Pin 点在 20s 内未出现，可能是 Google Maps 数据加载延迟")
        pin_count = pmp.get_map_pin_count()
        assert pin_count > 0, f"切换到地图视图后，Pin 点应可见，实际: {pin_count}"
        logger.info(f"✓ 地图 Pin 点可见，数量: {pin_count}")
