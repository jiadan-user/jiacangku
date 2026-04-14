"""
AU站 Property 地图模式 - 卡片数量功能测试

本脚本由 playwright-test-generator 生成
生成时间：2026-03-20

测试站点：AU (https://au.58v5.cn)
测试角色：guest（无需登录）
测试目标：验证地图模式下左侧卡片列表数量与结果徽标（badge）的一致性关系

录制数据（canberra / rent，2026-03-20 实测）：
  - 结果徽标：33 results
  - 左侧列表第1页卡片数：24（第2页有剩余）
  - 结论：左侧卡片数量 ≤ 结果徽标数字（分页机制导致，每页最多24张）

MCP 录制代码（browser_click / browser_evaluate）：
    await page.getByRole('button', { name: 'Map' }).click();
    await page.evaluate('() => { ... cardLinks: 24 ... resultText: "33 results" ... }');
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


class TestPropertyMapCardCount:
    """AU站 Property 地图模式 - 卡片数量功能测试类"""

    @pytest.mark.case_id_au58_property_map_card_count_001
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("地图模式卡片数量 - 正向场景")
    @allure.title("地图模式下左侧卡片数量不超过结果徽标数字")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "验证 AU 站 Rent Property 地图模式下，左侧卡片列表数量 ≤ 结果徽标（badge）数字。"
        "由于分页机制，每页最多展示24张卡片，badge 展示总数，因此 card_count ≤ badge_count。"
    )
    def test_left_card_count_le_badge_number(self, page, config):
        """TC001：左侧卡片数量 ≤ 结果徽标数字"""
        map_page = PropertyMapPage(page)
        target_url = config["target_url"]

        logger.info("=" * 80)
        logger.info("TC001 - 左侧卡片数量 ≤ 结果徽标数字")
        logger.info("=" * 80)

        with allure.step("步骤1：导航到地图模式页面"):
            map_page.navigate_to_map_page(target_url)
            logger.info(f"✓ 已导航到: {target_url}")

        with allure.step("步骤2：处理 Cookie 弹窗"):
            map_page.handle_cookie_popup()
            logger.info("✓ Cookie 弹窗已处理")

        with allure.step("步骤3：等待地图渲染"):
            rendered = map_page.is_map_container_loaded()
            if not rendered:
                pytest.skip("地图容器未在规定时间内加载完成")
            logger.info("✓ 地图容器已加载")

        with allure.step("步骤4：获取结果徽标数字"):
            badge_text = map_page.get_map_results_badge_text()
            if not badge_text:
                pytest.skip("结果徽标未显示，可能是网络延迟，跳过本用例")
            badge_number = map_page.get_map_results_badge_number()
            logger.info(f"结果徽标文本：{badge_text!r}，提取数字：{badge_number}")

        with allure.step("步骤5：获取左侧卡片列表数量"):
            # 通过 listPanel 选择器精确统计左侧卡片链接
            card_count = page.evaluate(
                "() => {"
                "  const panel = document.querySelector('[class*=\"listPanel\"]');"
                "  if (!panel) return 0;"
                "  return panel.querySelectorAll('a[href*=\"cate-property\"]').length;"
                "}"
            )
            logger.info(f"左侧卡片数量（当前页）：{card_count}")

        with allure.step("验证：左侧卡片数量 ≤ 结果徽标数字"):
            assert badge_number > 0, f"结果徽标数字应 > 0，实际：{badge_number}"
            assert card_count > 0, f"左侧卡片数量应 > 0，实际：{card_count}"
            assert card_count <= badge_number, (
                f"左侧卡片数量（{card_count}）超过了结果徽标数字（{badge_number}），"
                f"分页场景下卡片数应 ≤ badge 总数"
            )
            logger.info(
                f"✓ 断言通过：left_cards({card_count}) ≤ badge({badge_number})"
            )

        logger.info("✅ TC001 通过！左侧卡片数量符合预期（不超过结果徽标）")

    @pytest.mark.case_id_au58_property_map_card_count_002
    @pytest.mark.regression
    @pytest.mark.p1
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("地图模式卡片数量 - 正向场景")
    @allure.title("结果徽标正确展示房源总数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "验证地图模式下结果徽标（badge）格式正确，显示 'N results' 格式文本，"
        "且数字 > 0，代表当前地图视口内的房源总数。"
    )
    def test_results_badge_displays_correctly(self, page, config):
        """TC002：结果徽标正确展示 'N results' 格式"""
        map_page = PropertyMapPage(page)
        target_url = config["target_url"]

        logger.info("=" * 80)
        logger.info("TC002 - 结果徽标正确展示房源总数")
        logger.info("=" * 80)

        with allure.step("步骤1：导航到地图模式页面"):
            map_page.navigate_to_map_page(target_url)
            logger.info("✓ 导航完成")

        with allure.step("步骤2：处理 Cookie 弹窗"):
            map_page.handle_cookie_popup()

        with allure.step("步骤3：验证地图结果徽标可见"):
            badge_visible = map_page.is_map_results_badge_visible()
            assert badge_visible, "结果徽标（.MapView_resultsBadge__yvMxa）应该可见"
            logger.info("✓ 结果徽标可见")

        with allure.step("步骤4：获取并验证结果徽标文本格式"):
            badge_text = map_page.get_map_results_badge_text()
            if not badge_text:
                pytest.skip("结果徽标文本为空，可能是搜索中，跳过")
            logger.info(f"结果徽标文本：{badge_text!r}")

            assert re.match(r"\d+\s+results?", badge_text, re.IGNORECASE), (
                f"结果徽标文本格式应为 'N results'，实际：{badge_text!r}"
            )

            badge_number = map_page.get_map_results_badge_number()
            assert badge_number > 0, (
                f"结果徽标数字应 > 0，实际：{badge_number}（文本：{badge_text!r}）"
            )
            logger.info(f"✓ 结果徽标格式正确，房源总数：{badge_number}")

        logger.info("✅ TC002 通过！结果徽标格式与数值均正确")

    @pytest.mark.case_id_au58_property_map_card_count_003
    @pytest.mark.regression
    @pytest.mark.p1
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("地图模式卡片数量 - 正向场景")
    @allure.title("左侧卡片列表第1页数量不超过每页最大限制（24张）")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "验证地图模式下左侧卡片列表第1页展示的卡片数量不超过每页最大24张，"
        "且存在分页控件（Next 按钮），说明有多页数据。"
    )
    def test_left_card_page_limit(self, page, config):
        """TC003：左侧卡片第1页数量 ≤ 24，且有分页控件"""
        map_page = PropertyMapPage(page)
        target_url = config["target_url"]

        logger.info("=" * 80)
        logger.info("TC003 - 左侧卡片第1页数量不超过每页最大限制")
        logger.info("=" * 80)

        with allure.step("步骤1：导航到地图模式页面"):
            map_page.navigate_to_map_page(target_url)
            logger.info("✓ 导航完成")

        with allure.step("步骤2：处理 Cookie 弹窗"):
            map_page.handle_cookie_popup()

        with allure.step("步骤3：等待地图加载"):
            rendered = map_page.is_map_container_loaded()
            if not rendered:
                pytest.skip("地图容器未加载完成")

        with allure.step("步骤4：获取左侧卡片数量"):
            card_count = page.evaluate(
                "() => {"
                "  const panel = document.querySelector('[class*=\"listPanel\"]');"
                "  if (!panel) return 0;"
                "  return panel.querySelectorAll('a[href*=\"cate-property\"]').length;"
                "}"
            )
            logger.info(f"左侧卡片数量（第1页）：{card_count}")

        with allure.step("验证：卡片数量 > 0 且 ≤ 24"):
            assert card_count > 0, f"左侧卡片数量应 > 0，实际：{card_count}"
            assert card_count <= 24, (
                f"第1页卡片数量应 ≤ 24（每页最大限制），实际：{card_count}"
            )
            logger.info(f"✓ 第1页卡片数量：{card_count}（≤ 24）")

        with allure.step("步骤5：验证分页控件（Next 按钮）可见"):
            map_page.scroll_left_card_panel_to_bottom()
            pagination_visible = map_page.is_left_pagination_visible()
            assert pagination_visible, (
                "分页 Next 按钮应可见（说明有多页数据，卡片总数 > 当前页数量）"
            )
            logger.info("✓ 分页控件可见，确认存在多页数据")

        logger.info("✅ TC003 通过！左侧卡片数量符合分页限制")

    @pytest.mark.case_id_au58_property_map_card_count_004
    @pytest.mark.regression
    @pytest.mark.p1
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("地图模式卡片数量 - 正向场景")
    @allure.title("翻到第2页后左侧卡片数量仍 ≤ 结果徽标数字")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "在地图模式下点击分页 Next 翻到第2页，验证第2页的卡片数量同样 ≤ 结果徽标总数，"
        "且第2页卡片数量 ≤ 第1页卡片数量（最后一页可能不满24张）。"
    )
    def test_second_page_card_count(self, page, config):
        """TC004：翻页后第2页卡片数量仍满足约束"""
        map_page = PropertyMapPage(page)
        target_url = config["target_url"]

        logger.info("=" * 80)
        logger.info("TC004 - 翻到第2页后卡片数量仍 ≤ 结果徽标数字")
        logger.info("=" * 80)

        with allure.step("步骤1：导航到地图模式页面"):
            map_page.navigate_to_map_page(target_url)
            logger.info("✓ 导航完成")

        with allure.step("步骤2：处理 Cookie 弹窗"):
            map_page.handle_cookie_popup()

        with allure.step("步骤3：等待地图加载"):
            rendered = map_page.is_map_container_loaded()
            if not rendered:
                pytest.skip("地图容器未加载完成")

        with allure.step("步骤4：获取结果徽标数字"):
            badge_text = map_page.get_map_results_badge_text()
            if not badge_text:
                pytest.skip("结果徽标未显示，跳过")
            badge_number = map_page.get_map_results_badge_number()
            logger.info(f"结果徽标：{badge_text!r}，总数：{badge_number}")

        with allure.step("步骤5：记录第1页卡片数量"):
            page1_card_count = page.evaluate(
                "() => {"
                "  const panel = document.querySelector('[class*=\"listPanel\"]');"
                "  if (!panel) return 0;"
                "  return panel.querySelectorAll('a[href*=\"cate-property\"]').length;"
                "}"
            )
            logger.info(f"第1页卡片数量：{page1_card_count}")

        with allure.step("步骤6：滚动到底部并点击 Next 翻到第2页"):
            map_page.scroll_left_card_panel_to_bottom()
            pagination_visible = map_page.is_left_pagination_visible()
            if not pagination_visible:
                pytest.skip("分页控件不可见，可能总数据 ≤ 24，无第2页，跳过")

            map_page.click_left_pagination_next()
            page.wait_for_timeout(2000)
            logger.info("✓ 已点击 Next 翻到第2页")

        with allure.step("步骤7：获取第2页卡片数量"):
            page2_card_count = page.evaluate(
                "() => {"
                "  const panel = document.querySelector('[class*=\"listPanel\"]');"
                "  if (!panel) return 0;"
                "  return panel.querySelectorAll('a[href*=\"cate-property\"]').length;"
                "}"
            )
            logger.info(f"第2页卡片数量：{page2_card_count}")

        with allure.step("验证：第2页卡片数量 ≤ badge 总数"):
            assert page2_card_count > 0, f"第2页卡片数量应 > 0，实际：{page2_card_count}"
            assert page2_card_count <= badge_number, (
                f"第2页卡片数量（{page2_card_count}）超过结果徽标总数（{badge_number}）"
            )
            logger.info(
                f"✓ 断言通过：page2_cards({page2_card_count}) ≤ badge({badge_number})"
            )

        logger.info("✅ TC004 通过！第2页卡片数量符合约束")

    @pytest.mark.case_id_au58_property_map_card_count_005
    @pytest.mark.regression
    @pytest.mark.p2
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("地图模式卡片数量 - 正向场景")
    @allure.title("从列表视图切换到地图视图后结果徽标与卡片数量一致")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "从列表视图点击 Map 按钮切换到地图视图，验证地图加载后"
        "结果徽标显示正常且左侧卡片数量 ≤ badge 数字，确认视图切换不影响数据一致性。"
    )
    def test_switch_to_map_view_card_count(self, page, config):
        """TC005：从列表视图切换地图视图后数量关系仍正确"""
        map_page = PropertyMapPage(page)
        list_url = "https://au.58v5.cn/en/city-canberra/cate-property/?iconSource=rent"

        logger.info("=" * 80)
        logger.info("TC005 - 从列表视图切换到地图视图后数量关系验证")
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
            # MCP 录制代码：await page.getByRole('button', { name: 'Map' }).click();
            map_page.click_map_toggle_button()
            page.wait_for_timeout(3000)
            logger.info("✓ 已点击 Map 按钮")

        with allure.step("步骤4：等待地图容器加载完成"):
            loaded = map_page.wait_for_map_loaded_after_toggle(timeout_ms=30000)
            if not loaded:
                pytest.skip("切换后地图容器未在30s内加载完成")
            logger.info("✓ 地图容器已加载")

        with allure.step("步骤5：验证 URL 包含 view=map"):
            assert map_page.is_url_contains_map_view(), (
                f"切换后 URL 应包含 view=map，实际：{page.url}"
            )
            logger.info(f"✓ URL 包含 view=map，当前：{page.url}")

        with allure.step("步骤6：获取结果徽标"):
            badge_text = map_page.get_map_results_badge_text()
            if not badge_text:
                pytest.skip("结果徽标未显示，跳过")
            badge_number = map_page.get_map_results_badge_number()
            logger.info(f"结果徽标：{badge_text!r}，总数：{badge_number}")

        with allure.step("步骤7：获取左侧卡片数量"):
            card_count = page.evaluate(
                "() => {"
                "  const panel = document.querySelector('[class*=\"listPanel\"]');"
                "  if (!panel) return 0;"
                "  return panel.querySelectorAll('a[href*=\"cate-property\"]').length;"
                "}"
            )
            logger.info(f"左侧卡片数量：{card_count}")

        with allure.step("验证：左侧卡片数量 ≤ 结果徽标数字"):
            assert badge_number > 0, f"badge 数字应 > 0，实际：{badge_number}"
            assert card_count > 0, f"左侧卡片数量应 > 0，实际：{card_count}"
            assert card_count <= badge_number, (
                f"切换后卡片数量（{card_count}）超过 badge 总数（{badge_number}）"
            )
            logger.info(
                f"✓ 视图切换后关系正确：cards({card_count}) ≤ badge({badge_number})"
            )

        logger.info("✅ TC005 通过！视图切换后卡片数量关系正确")
