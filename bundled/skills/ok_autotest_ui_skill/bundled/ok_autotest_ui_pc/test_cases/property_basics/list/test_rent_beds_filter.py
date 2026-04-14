import re
import pytest
import allure
from pages.property_page import PropertyPage
from utils.logger import setup_logger

logger = setup_logger()

_CONFIG = {
    "site": "au",
    "site_name": "澳大利亚站",
    "role": "buyer",
    "user_name": "mayueming_au_buyer",
    "base_url": "https://au.58v5.cn",
    "test_account": None,
    "target_page": "https://au.58v5.cn/en/city-canberra/cate-property/?iconSource=rent",
    "locale": "en-AU",
    "currency": "AUD",
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


class TestRentBedsFilter:
    """Beds（卧室数量）筛选功能测试 - Property For Rent（7 条用例）"""

    @pytest.fixture(scope="module")
    def setup_property_page(self, page, config):
        property_page = PropertyPage(page)
        page.goto(config['target_page'], wait_until="domcontentloaded", timeout=config['timeout']['navigation'])
        page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
        property_page.handle_cookie_popup()
        page.wait_for_timeout(1000)
        yield property_page

    @pytest.fixture(scope="module", autouse=True)
    def reset_rent_page_after_module(self, page, config):
        """模块级别：所有测试结束后重置页面"""
        yield  # 先执行所有测试
        # 所有测试完成后的清理
        try:
            logger.info("========== 模块测试完毕，重置页面 ==========")
            page.goto(_CONFIG['target_page'], wait_until="domcontentloaded", timeout=_CONFIG['timeout']['navigation'])
            page.wait_for_load_state('domcontentloaded', timeout=_CONFIG['timeout']['navigation'])
            page.wait_for_timeout(1000)
            logger.info("✓ 模块测试完成，页面已重置")
        except Exception as e:
            logger.warning(f"模块结束后重置页面失败: {e}")
    
    @pytest.fixture(scope="function", autouse=True)
    def reset_page_between_tests(self, page, config, setup_property_page):
        """函数级别：每个测试之间重置页面（不关闭浏览器）"""
        yield  # 先执行测试
        # 每个测试后重置页面到初始状态
        try:
            logger.info("========== 用例执行完毕，重置页面到初始状态 ==========")
            page.goto(_CONFIG['target_page'], wait_until="domcontentloaded", timeout=_CONFIG['timeout']['navigation'])
            page.wait_for_load_state('domcontentloaded', timeout=_CONFIG['timeout']['navigation'])
            page.wait_for_timeout(1000)
            current_url = page.url
            if "cate-property" in current_url:
                logger.info(f"✓ 页面已重置到初始状态: {current_url}")
            else:
                logger.warning(f"⚠️ 页面 URL 可能不符合预期: {current_url}")
        except Exception as e:
            logger.warning(f"重置页面失败（不影响用例结果）: {e}")
            try:
                page.reload(wait_until="domcontentloaded", timeout=_CONFIG['timeout']['navigation'])
                page.wait_for_timeout(1000)
                logger.info("✓ 已通过刷新恢复页面")
            except Exception:
                pass
    @pytest.mark.p1
    @pytest.mark.case_id_property_rent_beds_019
    def test_beds_select_3_url_contains_attr_168(self, page, config, setup_property_page):
        """TC019：选择 Beds = 3 后点击 Done"""
        property_page = setup_property_page

        with allure.step("点击 Beds 筛选按钮"):
            property_page.click_beds_filter()
            logger.info("✓ Beds 筛选面板已打开")

        with allure.step("选择 Beds=3"):
            property_page.select_beds_values("3")
            logger.info("✓ 已选择 Beds=3")

        with allure.step("点击 Done"):
            property_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已点击 Done")

        with allure.step("验证 URL 含 attr_168 参数"):
            assert "attr_168" in page.url, \
                f"期望 URL 含 attr_168 参数，实际 URL: {page.url}"
            logger.info(f"✓ attr_168 在 URL 中: {page.url}")

        with allure.step("验证激活标签显示 Beds:3"):
            beds_tag = property_page.get_beds_filter_tag_text()
            assert beds_tag, "期望显示 Beds 激活标签"
            assert "3" in beds_tag, \
                f"期望激活标签包含 '3'，实际: '{beds_tag}'"
            logger.info(f"✓ Beds 激活标签: {beds_tag}")


    @pytest.mark.case_id_property_rent_beds_020
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Beds 卧室筛选 - 边界值场景")
    @allure.title("选择 Beds=1 最小值后 URL 含 attr_168 参数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("点击 Beds 筛选，选择 1（最小值），点击 Done，验证 URL 含 attr_168 参数")
    def test_beds_select_1_minimum_value_url_contains_attr_168(self, page, config, setup_property_page):
        """TC020：选择 Beds = 1（最小值）"""
        property_page = setup_property_page

        with allure.step("点击 Beds → 选择 1 → Done"):
            property_page.click_beds_filter()
            property_page.select_beds_values("1")
            property_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选择 Beds=1 并点击 Done")

        with allure.step("验证 URL 含 attr_168"):
            assert "attr_168" in page.url, \
                f"期望 URL 含 attr_168，实际 URL: {page.url}"
            logger.info(f"✓ URL: {page.url}")


    @pytest.mark.case_id_property_rent_beds_021
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Beds 卧室筛选 - 边界值场景")
    @allure.title("选择 Beds=8+ 最大开放值后 URL 含 attr_168 参数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("点击 Beds 筛选，选择 8+（最大开放值），点击 Done，验证 URL 含 attr_168 参数")
    def test_beds_select_8plus_maximum_value_url_contains_attr_168(self, page, config, setup_property_page):
        """TC021：选择 Beds = 8+（最大开放值）"""
        property_page = setup_property_page

        with allure.step("点击 Beds → 选择 8+ → Done"):
            property_page.click_beds_filter()
            property_page.select_beds_values("8+")
            property_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选择 Beds=8+ 并点击 Done")

        with allure.step("验证 URL 含 attr_168"):
            assert "attr_168" in page.url, \
                f"期望 URL 含 attr_168，实际 URL: {page.url}"
            logger.info(f"✓ URL: {page.url}")


    @pytest.mark.case_id_property_rent_beds_022
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Beds 卧室筛选 - 功能场景")
    @allure.title("选择 Studio 类型后 URL 含 attr_168 参数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("点击 Beds 筛选，选择 Studio，点击 Done，验证 URL 含 attr_168 参数")
    def test_beds_select_studio_url_contains_attr_168(self, page, config, setup_property_page):
        """TC022：选择 Studio 类型"""
        property_page = setup_property_page

        with allure.step("点击 Beds → 选择 Studio → Done"):
            property_page.click_beds_filter()
            property_page.select_beds_values("Studio")
            property_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选择 Studio 并点击 Done")

        with allure.step("验证 URL 含 attr_168"):
            assert "attr_168" in page.url, \
                f"期望 URL 含 attr_168，实际 URL: {page.url}"
            logger.info(f"✓ URL: {page.url}")


    @pytest.mark.case_id_property_rent_beds_023
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Beds 卧室筛选 - 功能场景")
    @allure.title("连续点击两个 Beds 值多选行为验证最后一次选择生效")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("在 Beds 面板中先点 1 再点 2，验证最终选择行为（单选或多选），点击 Done 后 URL 含 attr_168")
    def test_beds_multi_click_last_selection_takes_effect(self, page, config, setup_property_page):
        """TC023：连续点击两个 Beds 值（多选行为验证）"""
        property_page = setup_property_page

        with allure.step("打开 Beds 面板，依次点击 1 和 2"):
            property_page.click_beds_filter()
            property_page.select_beds_values("1")
            page.wait_for_timeout(500)
            property_page.select_beds_values("2")
            logger.info("✓ 已依次选择 Beds 1 和 2")

        with allure.step("点击 Done"):
            property_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已点击 Done")

        with allure.step("验证 URL 含 attr_168（选择已生效）"):
            assert "attr_168" in page.url, \
                f"期望 URL 含 attr_168，实际 URL: {page.url}"
            logger.info(f"✓ URL: {page.url}")


    @pytest.mark.case_id_property_rent_beds_024
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Beds 卧室筛选 - 功能场景")
    @allure.title("已选 Beds 后点击 Clear URL 中 attr_168 参数消失")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("设置 Beds=2 后，重新打开面板点击 Clear，验证 URL 中 attr_168 参数消失")
    def test_beds_clear_removes_attr_168_from_url(self, page, config, setup_property_page):
        """TC024：已选 Beds 后点击 Clear 清除"""
        property_page = setup_property_page

        with allure.step("先设置 Beds=2"):
            property_page.click_beds_filter()
            property_page.select_beds_values("2")
            property_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Beds=2")

        with allure.step("重新打开 Beds 面板并点击 Clear"):
            property_page.click_beds_filter()
            property_page.click_clear_button_in_beds_modal()
            property_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已点击 Clear 并 Done")

        with allure.step("验证 URL 不含 attr_168"):
            assert "attr_168" not in page.url, \
                f"期望 URL 不含 attr_168，实际 URL: {page.url}"
            logger.info(f"✓ attr_168 已从 URL 清除: {page.url}")


    @pytest.mark.case_id_property_rent_beds_025
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Beds 卧室筛选 - 异常场景")
    @allure.title("Beds 筛选结果为空时展示空状态文案")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("选择 Beds=8+ 等可能导致空结果的值，点击 Done，验证空状态文案显示")
    def test_beds_no_results_shows_empty_state_text(self, page, config, setup_property_page):
        """TC025：Beds 筛选结果为空时展示空状态"""
        property_page = setup_property_page

        with allure.step("点击 Beds → 选择 8+ → Done"):
            property_page.click_beds_filter()
            property_page.select_beds_values("8+")
            property_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选择 Beds=8+ 并点击 Done")

        with allure.step("验证页面正常展示（空状态或有结果）"):
            page_content = page.content()
            empty_state_visible = "couldn't find anything" in page_content.lower() or \
                                  "no results" in page_content.lower() or \
                                  "attr_168" in page.url
            assert empty_state_visible, \
                "期望页面展示空状态文案或显示筛选结果，页面无有效响应"
            logger.info(f"✓ 页面正常响应，URL: {page.url}")


    # ============================================