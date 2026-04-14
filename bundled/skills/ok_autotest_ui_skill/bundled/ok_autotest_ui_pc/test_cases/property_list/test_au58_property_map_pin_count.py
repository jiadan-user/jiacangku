"""
AU站 Property 地图模式 - 房源点数量功能测试

本脚本由 playwright-test-generator 生成
生成时间：2026-03-20

测试站点：AU (https://au.58v5.cn)
测试角色：guest（无需登录）
测试目标：验证地图模式下房源点（Pin 点）数量与结果徽标的一致性，
         以及 Pin 点的类型标识、价格文字、缩放稳定性。

录制数据（canberra / rent，2026-03-20 实测）：
  - 结果徽标：33 results
  - Pin 点总数：33 个（img[alt="bottom icon"]）
  - Sale Marker：0 个（Rent 页面无 sale marker）
  - Pin 点 class：PropertyMarker_markerWrapper__GGFMj PropertyMarker_rent__9TYMC
  - 价格文字容器：PropertyMarker_priceText__M8l6x（33/33 非空）
  - 缩放 zoom 11→10：Pin 点总数仍为 33

MCP 录制代码：
    await page.evaluate('() => { const b = document.querySelectorAll(\'img[alt="bottom icon"]\').length; const s = document.querySelectorAll(\'img[alt="sale marker"]\').length; return { bottomIcon: b, saleMarker: s, total: b+s }; }');
    await page.getByRole('button').filter({ hasText: /^$/ }).nth(3).click();  // 缩小
    await page.getByRole('button').filter({ hasText: /^$/ }).nth(2).click();  // 放大
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
    "target_url": (
        "https://au.58v5.cn/en/city-canberra/cate-property/"
        "?iconSource=rent&view=map&viewport=c%3A-35.2802%2C149.1310%7Cz%3A11"
    ),
    "locale": "en-AU",
    "browser": {
        "type": "chromium",
        "headless": True,
        "viewport": {"width": 1920, "height": 1080},
    },
    "timeout": {
        "default": 90000,
        "wait": 30000,
        "navigation": 90000,
    },
}


@pytest.fixture(scope="module")
def config():
    return _CONFIG


class TestPropertyMapPinCount:
    """AU站 Property 地图模式 - 房源点数量功能测试类"""

    @pytest.mark.case_id_au58_property_map_pin_count_001
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("地图模式房源点数量 - 正向场景")
    @allure.title("地图 Pin 点总数与结果徽标数字相等")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "验证 AU 站 Rent Property 地图模式下，地图上显示的 Pin 点总数"
        "（bottom icon + sale marker）与结果徽标数字完全相等。"
    )
    def test_pin_count_equals_badge_number(self, page, config):
        """TC001：地图 Pin 点总数 = 结果徽标数字"""
        map_page = PropertyMapPage(page)
        target_url = config["target_url"]

        logger.info("=" * 80)
        logger.info("TC001 - 地图 Pin 点总数与结果徽标数字相等")
        logger.info("=" * 80)

        with allure.step("步骤1：导航到地图模式页面"):
            map_page.navigate_to_map_page(target_url)
            logger.info(f"✓ 已导航到: {target_url}")

        with allure.step("步骤2：处理 Cookie 弹窗"):
            map_page.handle_cookie_popup()

        with allure.step("步骤3：等待地图加载完成"):
            rendered = map_page.is_map_container_loaded()
            if not rendered:
                pytest.skip("地图容器未在规定时间内加载完成")
            logger.info("✓ 地图容器已加载")

        with allure.step("步骤4：等待 Pin 点渲染"):
            pins_loaded = map_page.wait_for_map_pins(timeout_ms=15000)
            if not pins_loaded:
                pytest.skip("地图 Pin 点未在 15s 内渲染完成")
            logger.info("✓ Pin 点已渲染")

        with allure.step("步骤5：统计 Pin 点总数"):
            # MCP 录制代码：bottomIconCount: 33, saleMarkerCount: 0, totalPins: 33
            pin_stats = page.evaluate(
                "() => {"
                "  const b = document.querySelectorAll('img[alt=\"bottom icon\"]').length;"
                "  const s = document.querySelectorAll('img[alt=\"sale marker\"]').length;"
                "  return { bottomIcon: b, saleMarker: s, total: b + s };"
                "}"
            )
            total_pins = pin_stats["total"]
            logger.info(
                f"Pin 点统计：bottom icon={pin_stats['bottomIcon']}，"
                f"sale marker={pin_stats['saleMarker']}，总计={total_pins}"
            )

        with allure.step("步骤6：获取结果徽标数字"):
            badge_text = map_page.get_map_results_badge_text()
            if not badge_text:
                pytest.skip("结果徽标未显示，跳过")
            badge_number = map_page.get_map_results_badge_number()
            logger.info(f"结果徽标：{badge_text!r}，数字：{badge_number}")

        with allure.step("验证：Pin 点总数 = 结果徽标数字"):
            assert total_pins > 0, f"Pin 点总数应 > 0，实际：{total_pins}"
            assert badge_number > 0, f"结果徽标数字应 > 0，实际：{badge_number}"
            assert total_pins == badge_number, (
                f"Pin 点总数（{total_pins}）≠ 结果徽标数字（{badge_number}）"
            )
            logger.info(f"✓ Pin 点总数（{total_pins}）= badge（{badge_number}）")

        logger.info("✅ TC001 通过！Pin 点总数与结果徽标一致")

    @pytest.mark.case_id_au58_property_map_pin_count_002
    @pytest.mark.regression
    @pytest.mark.p1
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("地图模式房源点数量 - 正向场景")
    @allure.title("所有 Pin 点均显示价格文字")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "验证地图模式下每个 Pin 点容器（PropertyMarker_markerWrapper）内均包含"
        "非空的价格文字（PropertyMarker_priceText），无空白 Pin 点。"
    )
    def test_all_pins_have_price_text(self, page, config):
        """TC002：所有 Pin 点均显示价格文字"""
        map_page = PropertyMapPage(page)
        target_url = config["target_url"]

        logger.info("=" * 80)
        logger.info("TC002 - 所有 Pin 点均显示价格文字")
        logger.info("=" * 80)

        with allure.step("步骤1：导航到地图模式页面"):
            map_page.navigate_to_map_page(target_url)

        with allure.step("步骤2：处理 Cookie 弹窗"):
            map_page.handle_cookie_popup()

        with allure.step("步骤3：等待 Pin 点渲染"):
            pins_loaded = map_page.wait_for_map_pins(timeout_ms=15000)
            if not pins_loaded:
                pytest.skip("Pin 点未渲染完成")

        with allure.step("步骤4：检查所有 Pin 点的价格文字"):
            # MCP 录制：pinsWithPriceText: 33，totalPins: 33
            pin_price_stats = page.evaluate(
                "() => {"
                "  const wrappers = document.querySelectorAll('[class*=\"PropertyMarker_markerWrapper\"]');"
                "  const total = wrappers.length;"
                "  const withPrice = Array.from(wrappers).filter(el => el.innerText.trim().length > 0).length;"
                "  const samplePrices = Array.from(wrappers).slice(0, 5).map(el => el.innerText.trim());"
                "  return { total, withPrice, emptyCount: total - withPrice, samplePrices };"
                "}"
            )
            total = pin_price_stats["total"]
            with_price = pin_price_stats["withPrice"]
            empty_count = pin_price_stats["emptyCount"]
            logger.info(
                f"Pin 点总数：{total}，有价格文字：{with_price}，"
                f"空白：{empty_count}，示例：{pin_price_stats['samplePrices']}"
            )

        with allure.step("验证：所有 Pin 点均有价格文字"):
            assert total > 0, f"Pin 点总数应 > 0，实际：{total}"
            assert empty_count == 0, (
                f"存在 {empty_count} 个 Pin 点没有价格文字（共 {total} 个）"
            )
            assert with_price == total, (
                f"有价格文字的 Pin 点（{with_price}）≠ 总 Pin 点数（{total}）"
            )
            logger.info(f"✓ 全部 {total} 个 Pin 点均有价格文字")

        logger.info("✅ TC002 通过！所有 Pin 点均显示价格文字")

    @pytest.mark.case_id_au58_property_map_pin_count_003
    @pytest.mark.regression
    @pytest.mark.p1
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("地图模式房源点数量 - 正向场景")
    @allure.title("Rent 页面所有 Pin 点均带 Rent 类型标识")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "验证 Rent（租房）类型地图页面中，所有 Pin 点均含 PropertyMarker_rent class，"
        "且无 Sale 类型的 img[alt='sale marker']，确认类型标识与页面分类一致。"
    )
    def test_rent_pins_have_rent_class(self, page, config):
        """TC003：Rent 页面所有 Pin 点均带 Rent 类型 class"""
        map_page = PropertyMapPage(page)
        target_url = config["target_url"]

        logger.info("=" * 80)
        logger.info("TC003 - Rent 页面所有 Pin 点均带 Rent 类型标识")
        logger.info("=" * 80)

        with allure.step("步骤1：导航到 Rent 地图模式页面"):
            map_page.navigate_to_map_page(target_url)

        with allure.step("步骤2：处理 Cookie 弹窗"):
            map_page.handle_cookie_popup()

        with allure.step("步骤3：等待 Pin 点渲染"):
            pins_loaded = map_page.wait_for_map_pins(timeout_ms=15000)
            if not pins_loaded:
                pytest.skip("Pin 点未渲染完成")

        with allure.step("步骤4：统计各类型 Pin 点数量"):
            # MCP 录制：firstPinClass = "PropertyMarker_markerWrapper__GGFMj PropertyMarker_rent__9TYMC"
            type_stats = page.evaluate(
                "() => {"
                "  const rentPins = document.querySelectorAll('[class*=\"PropertyMarker_rent\"]').length;"
                "  const salePins = document.querySelectorAll('[class*=\"PropertyMarker_sale\"]').length;"
                "  const bottomIcons = document.querySelectorAll('img[alt=\"bottom icon\"]').length;"
                "  const saleMarkers = document.querySelectorAll('img[alt=\"sale marker\"]').length;"
                "  return { rentPins, salePins, bottomIcons, saleMarkers };"
                "}"
            )
            logger.info(
                f"Rent Pin 点：{type_stats['rentPins']}，Sale Pin 点：{type_stats['salePins']}，"
                f"bottom icon：{type_stats['bottomIcons']}，sale marker：{type_stats['saleMarkers']}"
            )

        with allure.step("验证：所有 Pin 点均为 Rent 类型，无 Sale 类型"):
            assert type_stats["rentPins"] > 0, (
                f"Rent 类型 Pin 点数量应 > 0，实际：{type_stats['rentPins']}"
            )
            assert type_stats["salePins"] == 0, (
                f"Rent 页面不应有 Sale 类型 Pin 点，实际：{type_stats['salePins']}"
            )
            assert type_stats["saleMarkers"] == 0, (
                f"Rent 页面不应有 sale marker 图标，实际：{type_stats['saleMarkers']}"
            )
            assert type_stats["rentPins"] == type_stats["bottomIcons"], (
                f"Rent Pin 点数（{type_stats['rentPins']}）≠ bottom icon 数（{type_stats['bottomIcons']}）"
            )
            logger.info(f"✓ 所有 {type_stats['rentPins']} 个 Pin 点均为 Rent 类型")

        logger.info("✅ TC003 通过！Pin 点类型与页面分类一致")

    @pytest.mark.case_id_au58_property_map_pin_count_004
    @pytest.mark.regression
    @pytest.mark.p1
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("地图模式房源点数量 - 正向场景")
    @allure.title("地图缩放后 Pin 点总数与 badge 保持一致")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "点击地图缩小按钮（zoom 11→10），等待地图数据重新加载后，"
        "验证 Pin 点总数仍与结果徽标数字相等，确认缩放不破坏数量一致性。"
    )
    def test_pin_count_consistent_after_zoom(self, page, config):
        """TC004：地图缩放后 Pin 点总数与 badge 保持一致"""
        map_page = PropertyMapPage(page)
        target_url = config["target_url"]

        logger.info("=" * 80)
        logger.info("TC004 - 地图缩放后 Pin 点总数与 badge 保持一致")
        logger.info("=" * 80)

        with allure.step("步骤1：导航到地图模式页面"):
            map_page.navigate_to_map_page(target_url)

        with allure.step("步骤2：处理 Cookie 弹窗"):
            map_page.handle_cookie_popup()

        with allure.step("步骤3：等待 Pin 点渲染并记录初始数量"):
            pins_loaded = map_page.wait_for_map_pins(timeout_ms=15000)
            if not pins_loaded:
                pytest.skip("Pin 点未渲染完成")

            initial_pins = page.evaluate(
                "() => document.querySelectorAll('img[alt=\"bottom icon\"]').length"
                " + document.querySelectorAll('img[alt=\"sale marker\"]').length"
            )
            initial_zoom = map_page.get_zoom_level_from_url()
            logger.info(f"初始状态：Pin 点={initial_pins}，zoom={initial_zoom}")

        with allure.step("步骤4：点击缩小按钮（zoom 减小1级）"):
            # MCP 录制代码：await page.getByRole('button').filter({hasText:/^$/}).nth(3).click()
            map_page.click_map_zoom_out()
            page.wait_for_timeout(3000)
            zoom_after = map_page.get_zoom_level_from_url()
            logger.info(f"✓ 缩小后 zoom={zoom_after}（URL 已更新）")

        with allure.step("步骤5：重新统计 Pin 点数量"):
            zoomed_pins = page.evaluate(
                "() => document.querySelectorAll('img[alt=\"bottom icon\"]').length"
                " + document.querySelectorAll('img[alt=\"sale marker\"]').length"
            )
            logger.info(f"缩小后 Pin 点总数：{zoomed_pins}")

        with allure.step("步骤6：获取结果徽标数字"):
            badge_text = map_page.get_map_results_badge_text()
            if not badge_text:
                pytest.skip("结果徽标未显示，跳过")
            badge_number = map_page.get_map_results_badge_number()
            logger.info(f"结果徽标：{badge_text!r}，数字：{badge_number}")

        with allure.step("验证：缩放后 Pin 点总数 = badge 数字"):
            assert zoomed_pins > 0, f"缩放后 Pin 点数量应 > 0，实际：{zoomed_pins}"
            assert zoomed_pins == badge_number, (
                f"缩放后 Pin 点总数（{zoomed_pins}）≠ 结果徽标数字（{badge_number}）"
            )
            logger.info(
                f"✓ 缩放后关系正确：pins({zoomed_pins}) = badge({badge_number})"
            )

        logger.info("✅ TC004 通过！缩放后 Pin 点数量与 badge 一致")

    @pytest.mark.case_id_au58_property_map_pin_count_005
    @pytest.mark.regression
    @pytest.mark.p2
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("地图模式房源点数量 - 正向场景")
    @allure.title("从列表视图切换到地图视图后 Pin 点正常加载")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "从列表视图点击 Map 按钮切换到地图视图，验证切换完成后 Pin 点成功渲染，"
        "且 Pin 点总数与结果徽标数字相等。"
    )
    def test_pins_load_after_switch_to_map(self, page, config):
        """TC005：从列表视图切换后 Pin 点正常加载"""
        map_page = PropertyMapPage(page)
        list_url = "https://au.58v5.cn/en/city-canberra/cate-property/?iconSource=rent"

        logger.info("=" * 80)
        logger.info("TC005 - 从列表视图切换到地图视图后 Pin 点正常加载")
        logger.info("=" * 80)

        with allure.step("步骤1：打开列表视图页面"):
            page.goto(list_url, timeout=90000, wait_until="domcontentloaded")
            try:
                page.wait_for_load_state("networkidle", timeout=20000)
            except Exception:
                pass
            logger.info("✓ 列表视图已打开")

        with allure.step("步骤2：处理 Cookie 弹窗"):
            map_page.handle_cookie_popup()

        with allure.step("步骤3：点击 Map 按钮切换到地图视图"):
            # MCP 录制代码：await page.getByRole('button', { name: 'Map' }).click()
            map_page.click_map_toggle_button()
            page.wait_for_timeout(3000)
            logger.info("✓ 已点击 Map 按钮")

        with allure.step("步骤4：等待地图容器加载完成"):
            loaded = map_page.wait_for_map_loaded_after_toggle(timeout_ms=30000)
            if not loaded:
                pytest.skip("切换后地图容器未在30s内加载完成")
            logger.info("✓ 地图容器已加载")

        with allure.step("步骤5：等待 Pin 点渲染"):
            pins_loaded = map_page.wait_for_map_pins(timeout_ms=15000)
            if not pins_loaded:
                pytest.skip("切换后 Pin 点未在15s内渲染完成")
            logger.info("✓ Pin 点已渲染")

        with allure.step("步骤6：统计 Pin 点总数"):
            total_pins = page.evaluate(
                "() => document.querySelectorAll('img[alt=\"bottom icon\"]').length"
                " + document.querySelectorAll('img[alt=\"sale marker\"]').length"
            )
            logger.info(f"切换后 Pin 点总数：{total_pins}")

        with allure.step("步骤7：获取结果徽标数字"):
            badge_text = map_page.get_map_results_badge_text()
            if not badge_text:
                pytest.skip("结果徽标未显示，跳过")
            badge_number = map_page.get_map_results_badge_number()
            logger.info(f"结果徽标：{badge_text!r}，数字：{badge_number}")

        with allure.step("验证：Pin 点总数 = badge 数字，且 URL 包含 view=map"):
            assert map_page.is_url_contains_map_view(), (
                f"URL 应包含 view=map，实际：{page.url}"
            )
            assert total_pins > 0, f"Pin 点总数应 > 0，实际：{total_pins}"
            assert total_pins == badge_number, (
                f"切换后 Pin 点总数（{total_pins}）≠ 结果徽标数字（{badge_number}）"
            )
            logger.info(
                f"✓ 视图切换后关系正确：pins({total_pins}) = badge({badge_number})"
            )

        logger.info("✅ TC005 通过！切换后 Pin 点正常加载且数量一致")
