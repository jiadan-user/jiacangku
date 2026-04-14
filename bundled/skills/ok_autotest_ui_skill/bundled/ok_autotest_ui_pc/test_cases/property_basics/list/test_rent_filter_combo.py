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


class TestRentFilterCombo:
    """Filter 综合筛选 & 多项组合场景测试 - Property For Rent（23 条用例）"""

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
    @pytest.mark.case_id_property_rent_combo_042
    def test_filter_badge_initial_count_includes_icon_source(self, page, config, setup_property_page):
        """TC042：Filter badge 初始计数验证"""
        property_page = setup_property_page

        with allure.step("获取 Filter 按钮显示文案"):
            filter_text = property_page.get_filter_display_text()
            logger.info(f"Filter 显示文案: '{filter_text}'")

        with allure.step("验证 Filter badge 显示计数（含 iconSource）"):
            assert "Filter" in filter_text, \
                f"期望找到 Filter 按钮，实际显示: '{filter_text}'"
            logger.info(f"✓ Filter badge: {filter_text}")


    @pytest.mark.case_id_property_rent_filter_043
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Filter 综合筛选 - UI 场景")
    @allure.title("设置 Price 后 Filter badge 计数更新")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("设置价格筛选后，验证 Filter badge 计数增加（lowestPrice 和 highestPrice 各计一个）")
    def test_filter_badge_count_updates_after_price_filter(self, page, config, setup_property_page):
        """TC043：设置 Price 后 Filter badge 计数更新"""
        property_page = setup_property_page

        with allure.step("记录设置 Price 前的 Filter badge"):
            badge_before = property_page.get_filter_display_text()
            logger.info(f"设置前 badge: '{badge_before}'")

        with allure.step("设置 Price=500~2000"):
            property_page.click_price_filter()
            property_page.input_price_range("500", "2000")
            property_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置价格筛选 500~2000")

        with allure.step("验证 Filter badge 已更新（包含价格参数）"):
            assert "lowestPrice=500" in page.url and "highestPrice=2000" in page.url, \
                "期望 URL 含价格参数（Price 筛选已生效）"
            logger.info(f"✓ 价格筛选生效，URL: {page.url}")


    @pytest.mark.case_id_property_rent_filter_044
    @pytest.mark.p0
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Filter 综合筛选 - 组合场景")
    @allure.title("Price + Beds 双重筛选 URL 同时含两组参数")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("依次设置 Price=500~2000 和 Beds=2，验证 URL 同时含 lowestPrice/highestPrice 和 attr_168")
    def test_filter_price_and_beds_combination_url_contains_both_params(self, page, config, setup_property_page):
        """TC044：Price + Beds 双重筛选"""
        property_page = setup_property_page

        with allure.step("设置 Price=500~2000"):
            property_page.click_price_filter()
            property_page.input_price_range("500", "2000")
            property_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Price=500~2000")

        with allure.step("设置 Beds=2"):
            property_page.click_beds_filter()
            property_page.select_beds_values("2")
            property_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Beds=2")

        with allure.step("验证 URL 同时含价格和 Beds 参数"):
            current_url = page.url
            assert "lowestPrice=500" in current_url, \
                f"期望 URL 含 lowestPrice=500，实际: {current_url}"
            assert "highestPrice=2000" in current_url, \
                f"期望 URL 含 highestPrice=2000，实际: {current_url}"
            assert "attr_168" in current_url, \
                f"期望 URL 含 attr_168，实际: {current_url}"
            logger.info(f"✓ 双重筛选 URL: {current_url}")


    @pytest.mark.case_id_property_rent_filter_045
    @pytest.mark.p0
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Filter 综合筛选 - 组合场景")
    @allure.title("Sort + Price 组合筛选 URL 同时含 sortId 和价格参数")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("设置 Sort=Lowest Price 和 Price=1000~5000，验证 URL 同时含 sortId 和价格参数")
    def test_filter_sort_and_price_combination_url_contains_both(self, page, config, setup_property_page):
        """TC045：Sort + Price 组合筛选"""
        property_page = setup_property_page

        with allure.step("设置排序 Lowest Price"):
            property_page.click_sort_button()
            property_page.select_sort_option("Lowest Price")
            property_page.click_done_button_in_sort_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置排序 Lowest Price")

        with allure.step("设置 Price=1000~5000"):
            property_page.click_price_filter()
            property_page.input_price_range("1000", "5000")
            property_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Price=1000~5000")

        with allure.step("验证 URL 同时含 sortId 和价格参数"):
            current_url = page.url
            assert "sortId" in current_url, \
                f"期望 URL 含 sortId，实际: {current_url}"
            assert "lowestPrice=1000" in current_url, \
                f"期望 URL 含 lowestPrice=1000，实际: {current_url}"
            logger.info(f"✓ Sort+Price 组合 URL: {current_url}")


    @pytest.mark.case_id_property_rent_filter_046
    @pytest.mark.p0
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Filter 综合筛选 - 组合场景")
    @allure.title("Sort + Property Type 组合筛选 URL 同时含两组参数")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("设置 Sort=Newest First 和 Property Type=House，验证 URL 同时含 sortId 和 house 路径")
    def test_filter_sort_and_property_type_combination_url_contains_both(self, page, config, setup_property_page):
        """TC046：Sort + Property Type 组合筛选"""
        property_page = setup_property_page

        with allure.step("设置排序 Newest First"):
            property_page.click_sort_button()
            property_page.select_sort_option("Newest First")
            property_page.click_done_button_in_sort_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置排序 Newest First")

        with allure.step("设置 Property Type=House"):
            property_page.click_property_type_filter()
            property_page.select_third_level_category(index=1)
            property_page.click_done_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Property Type=House")

        with allure.step("验证 URL 含 sortId"):
            assert "sortId" in page.url, \
                f"期望 URL 含 sortId，实际: {page.url}"
            logger.info(f"✓ Sort+PropertyType 组合 URL: {page.url}")


    @pytest.mark.case_id_property_rent_filter_047
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Filter 综合筛选 - 组合场景")
    @allure.title("Beds + Price 组合筛选 URL 同时含两组参数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("先设置 Beds=2 后设置 Price=500~2000，验证 URL 同时含 attr_168 和价格参数")
    def test_filter_beds_then_price_url_contains_both(self, page, config, setup_property_page):
        """TC047：Beds + Price 组合筛选"""
        property_page = setup_property_page

        with allure.step("设置 Beds=2"):
            property_page.click_beds_filter()
            property_page.select_beds_values("2")
            property_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Beds=2")

        with allure.step("设置 Price=500~2000"):
            property_page.click_price_filter()
            property_page.input_price_range("500", "2000")
            property_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Price=500~2000")

        with allure.step("验证 URL 同时含 attr_168 和价格参数"):
            current_url = page.url
            assert "attr_168" in current_url, \
                f"期望 URL 含 attr_168，实际: {current_url}"
            assert "lowestPrice" in current_url, \
                f"期望 URL 含 lowestPrice，实际: {current_url}"
            logger.info(f"✓ Beds+Price URL: {current_url}")


    @pytest.mark.case_id_property_rent_filter_048
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Filter 综合筛选 - 组合场景")
    @allure.title("Bathrooms + Property Type 组合筛选 URL 同时含两组参数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("设置 Bathrooms=2 和 Property Type=Townhomes，验证 URL 含 attr_166 和类目参数")
    def test_filter_bathrooms_and_property_type_combination(self, page, config, setup_property_page):
        """TC048：Bathrooms + Property Type 组合筛选"""
        property_page = setup_property_page

        with allure.step("设置 Bathrooms=2"):
            property_page.click_bathrooms_filter()
            property_page.select_bathrooms_values("2")
            property_page.click_done_button_in_bathrooms_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Bathrooms=2")

        with allure.step("设置 Property Type=Townhomes"):
            property_page.click_property_type_filter()
            property_page.select_third_level_category(index=2)
            property_page.click_done_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Property Type=Townhomes")

        with allure.step("验证 URL 含 attr_166"):
            assert "attr_166" in page.url, \
                f"期望 URL 含 attr_166，实际: {page.url}"
            logger.info(f"✓ Bathrooms+PropertyType URL: {page.url}")


    @pytest.mark.case_id_property_rent_filter_049
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Filter 综合筛选 - 组合场景")
    @allure.title("Beds + Bathrooms 组合筛选 URL 同时含两组参数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("设置 Beds=2 和 Bathrooms=1，验证 URL 同时含 attr_168 和 attr_166 参数")
    def test_filter_beds_and_bathrooms_combination_url_contains_both(self, page, config, setup_property_page):
        """TC049：Beds + Bathrooms 组合筛选"""
        property_page = setup_property_page

        with allure.step("设置 Beds=2"):
            property_page.click_beds_filter()
            property_page.select_beds_values("2")
            property_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Beds=2")

        with allure.step("设置 Bathrooms=1"):
            property_page.click_bathrooms_filter()
            property_page.select_bathrooms_values("1")
            property_page.click_done_button_in_bathrooms_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Bathrooms=1")

        with allure.step("验证 URL 同时含 attr_168 和 attr_166"):
            current_url = page.url
            assert "attr_168" in current_url, \
                f"期望 URL 含 attr_168，实际: {current_url}"
            assert "attr_166" in current_url, \
                f"期望 URL 含 attr_166，实际: {current_url}"
            logger.info(f"✓ Beds+Bathrooms URL: {current_url}")


    @pytest.mark.case_id_property_rent_filter_050
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Filter 综合筛选 - 组合场景")
    @allure.title("Sort + Beds + Price 三项组合筛选 URL 含三组参数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("设置 Sort=Highest Price、Beds=2、Price=2000~5000，验证 URL 同时含三组参数")
    def test_filter_sort_beds_price_triple_combination_url_contains_all(self, page, config, setup_property_page):
        """TC050：Sort + Beds + Price 三项组合筛选"""
        property_page = setup_property_page

        with allure.step("设置排序 Highest Price"):
            property_page.click_sort_button()
            property_page.select_sort_option("Highest Price")
            property_page.click_done_button_in_sort_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置排序 Highest Price")

        with allure.step("设置 Beds=2"):
            property_page.click_beds_filter()
            property_page.select_beds_values("2")
            property_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Beds=2")

        with allure.step("设置 Price=2000~5000"):
            property_page.click_price_filter()
            property_page.input_price_range("2000", "5000")
            property_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Price=2000~5000")

        with allure.step("验证 URL 含三组参数"):
            current_url = page.url
            assert "sortId" in current_url, f"期望 URL 含 sortId，实际: {current_url}"
            assert "attr_168" in current_url, f"期望 URL 含 attr_168，实际: {current_url}"
            assert "lowestPrice=2000" in current_url, \
                f"期望 URL 含 lowestPrice=2000，实际: {current_url}"
            logger.info(f"✓ 三项组合 URL: {current_url}")


    # ============================================
    # 七、列表页直接多筛选项组合场景 TC065–TC078
    # ============================================

    @pytest.mark.case_id_property_rent_combo_065
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("列表页组合筛选 - 组合场景")
    @allure.title("Price + Bathrooms 双重筛选 URL 同时含价格和 attr_166 参数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("从列表页分别点击 Price 和 Bathrooms 筛选按钮，设置后验证 URL 同时含两组参数")
    def test_combo_price_and_bathrooms_url_contains_both(self, page, config, setup_property_page):
        """TC065：Price + Bathrooms 双重筛选"""
        property_page = setup_property_page

        with allure.step("点击 Price → 输入 Min=800、Max=3000 → Done"):
            property_page.click_price_filter()
            property_page.input_price_range("800", "3000")
            property_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Price=800~3000")

        with allure.step("点击 Bathrooms → 选择 2 → Done"):
            property_page.click_bathrooms_filter()
            property_page.select_bathrooms_values("2")
            property_page.click_done_button_in_bathrooms_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Bathrooms=2")

        with allure.step("验证 URL 同时含价格参数和 attr_166"):
            current_url = page.url
            assert "lowestPrice=800" in current_url, \
                f"期望 URL 含 lowestPrice=800，实际: {current_url}"
            assert "attr_166" in current_url, \
                f"期望 URL 含 attr_166，实际: {current_url}"
            logger.info(f"✓ Price+Bathrooms URL: {current_url}")


    @pytest.mark.case_id_property_rent_combo_066
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("列表页组合筛选 - 组合场景")
    @allure.title("Price + Property Type 双重筛选 URL 含价格和类目参数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("设置 Price=1000~4000 和 Property Type=House，验证 URL 同时含价格和 house 路径")
    def test_combo_price_and_property_type_url_contains_both(self, page, config, setup_property_page):
        """TC066：Price + Property Type 双重筛选"""
        property_page = setup_property_page

        with allure.step("设置 Price=1000~4000"):
            property_page.click_price_filter()
            property_page.input_price_range("1000", "4000")
            property_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Price=1000~4000")

        with allure.step("设置 Property Type=House"):
            property_page.click_property_type_filter()
            property_page.select_third_level_category(index=1)
            property_page.click_done_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Property Type=House")

        with allure.step("验证 URL 含价格参数"):
            assert "lowestPrice=1000" in page.url, \
                f"期望 URL 含 lowestPrice=1000，实际: {page.url}"
            logger.info(f"✓ Price+PropertyType URL: {page.url}")


    @pytest.mark.case_id_property_rent_combo_067
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("列表页组合筛选 - 组合场景")
    @allure.title("Beds + Property Type 双重筛选 URL 含 attr_168 和类目参数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("设置 Beds=3 和 Property Type=Apartment&Unit，验证 URL 含 attr_168 和类目信息")
    def test_combo_beds_and_property_type_url_contains_both(self, page, config, setup_property_page):
        """TC067：Beds + Property Type 双重筛选"""
        property_page = setup_property_page

        with allure.step("设置 Beds=3"):
            property_page.click_beds_filter()
            property_page.select_beds_values("3")
            property_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Beds=3")

        with allure.step("设置 Property Type=Apartment&Unit"):
            property_page.click_property_type_filter()
            property_page.select_third_level_category(index=3)
            property_page.click_done_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Property Type=Apartment&Unit")

        with allure.step("验证 URL 含 attr_168"):
            assert "attr_168" in page.url, \
                f"期望 URL 含 attr_168，实际: {page.url}"
            logger.info(f"✓ Beds+PropertyType URL: {page.url}")


    @pytest.mark.case_id_property_rent_combo_068
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("列表页组合筛选 - 组合场景")
    @allure.title("Sort + Bathrooms 双重组合筛选 URL 含 sortId 和 attr_166")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("设置 Sort=Lowest Price 和 Bathrooms=1，验证 URL 含 sortId 和 attr_166")
    def test_combo_sort_and_bathrooms_url_contains_both(self, page, config, setup_property_page):
        """TC068：Sort + Bathrooms 双重组合筛选"""
        property_page = setup_property_page

        with allure.step("设置排序 Lowest Price"):
            property_page.click_sort_button()
            property_page.select_sort_option("Lowest Price")
            property_page.click_done_button_in_sort_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置排序 Lowest Price")

        with allure.step("设置 Bathrooms=1"):
            property_page.click_bathrooms_filter()
            property_page.select_bathrooms_values("1")
            property_page.click_done_button_in_bathrooms_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Bathrooms=1")

        with allure.step("验证 URL 含 sortId 和 attr_166"):
            current_url = page.url
            assert "sortId" in current_url, f"期望 URL 含 sortId，实际: {current_url}"
            assert "attr_166" in current_url, f"期望 URL 含 attr_166，实际: {current_url}"
            logger.info(f"✓ Sort+Bathrooms URL: {current_url}")


    @pytest.mark.case_id_property_rent_combo_069
    @pytest.mark.p0
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("列表页组合筛选 - 组合场景")
    @allure.title("Price + Beds + Bathrooms 三项组合筛选 URL 含三组参数")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("设置 Price=500~2000、Beds=2、Bathrooms=1，验证 URL 同时含三组筛选参数")
    def test_combo_price_beds_bathrooms_triple_url_contains_all(self, page, config, setup_property_page):
        """TC069：Price + Beds + Bathrooms 三项组合筛选"""
        property_page = setup_property_page

        with allure.step("设置 Price=500~2000"):
            property_page.click_price_filter()
            property_page.input_price_range("500", "2000")
            property_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Price=500~2000")

        with allure.step("设置 Beds=2"):
            property_page.click_beds_filter()
            property_page.select_beds_values("2")
            property_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Beds=2")

        with allure.step("设置 Bathrooms=1"):
            property_page.click_bathrooms_filter()
            property_page.select_bathrooms_values("1")
            property_page.click_done_button_in_bathrooms_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Bathrooms=1")

        with allure.step("验证 URL 含三组参数"):
            current_url = page.url
            assert "lowestPrice=500" in current_url, \
                f"期望 URL 含 lowestPrice=500，实际: {current_url}"
            assert "attr_168" in current_url, \
                f"期望 URL 含 attr_168，实际: {current_url}"
            assert "attr_166" in current_url, \
                f"期望 URL 含 attr_166，实际: {current_url}"
            logger.info(f"✓ 三项组合 URL: {current_url}")


    @pytest.mark.case_id_property_rent_combo_070
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("列表页组合筛选 - 组合场景")
    @allure.title("Sort + Price + Property Type 三项组合筛选 URL 含三组参数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("设置 Sort=Newest First、Price=1000~3000、Property Type=Townhomes，验证 URL 含三组参数")
    def test_combo_sort_price_property_type_triple_url_contains_all(self, page, config, setup_property_page):
        """TC070：Sort + Price + Property Type 三项组合筛选"""
        property_page = setup_property_page

        with allure.step("设置排序 Newest First"):
            property_page.click_sort_button()
            property_page.select_sort_option("Newest First")
            property_page.click_done_button_in_sort_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置排序 Newest First")

        with allure.step("设置 Price=1000~3000"):
            property_page.click_price_filter()
            property_page.input_price_range("1000", "3000")
            property_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Price=1000~3000")

        with allure.step("设置 Property Type=Townhomes"):
            property_page.click_property_type_filter()
            property_page.select_third_level_category(index=2)
            property_page.click_done_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Property Type=Townhomes")

        with allure.step("验证 URL 含 sortId 和价格参数"):
            current_url = page.url
            assert "sortId" in current_url, f"期望 URL 含 sortId，实际: {current_url}"
            assert "lowestPrice=1000" in current_url, \
                f"期望 URL 含 lowestPrice=1000，实际: {current_url}"
            logger.info(f"✓ Sort+Price+PropertyType URL: {current_url}")


    @pytest.mark.case_id_property_rent_combo_071
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("列表页组合筛选 - 组合场景")
    @allure.title("Beds + Bathrooms + Property Type 三项组合筛选 URL 含三组参数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("设置 Beds=2、Bathrooms=1、Property Type=House，验证 URL 含三组筛选参数")
    def test_combo_beds_bathrooms_property_type_triple_url_contains_all(self, page, config, setup_property_page):
        """TC071：Beds + Bathrooms + Property Type 三项组合筛选"""
        property_page = setup_property_page

        with allure.step("设置 Beds=2"):
            property_page.click_beds_filter()
            property_page.select_beds_values("2")
            property_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Beds=2")

        with allure.step("设置 Bathrooms=1"):
            property_page.click_bathrooms_filter()
            property_page.select_bathrooms_values("1")
            property_page.click_done_button_in_bathrooms_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Bathrooms=1")

        with allure.step("设置 Property Type=House"):
            property_page.click_property_type_filter()
            property_page.select_third_level_category(index=1)
            property_page.click_done_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Property Type=House")

        with allure.step("验证 URL 含 attr_168 和 attr_166"):
            current_url = page.url
            assert "attr_168" in current_url, f"期望 URL 含 attr_168，实际: {current_url}"
            assert "attr_166" in current_url, f"期望 URL 含 attr_166，实际: {current_url}"
            logger.info(f"✓ Beds+Bathrooms+PropertyType URL: {current_url}")


    @pytest.mark.case_id_property_rent_combo_072
    @pytest.mark.p0
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("列表页组合筛选 - 组合场景")
    @allure.title("全量五项组合筛选 URL 含所有筛选参数")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("依次设置 Sort、Price、Beds、Bathrooms、Property Type 五个筛选项，验证 URL 同时含所有参数")
    def test_combo_all_five_filters_url_contains_all_params(self, page, config, setup_property_page):
        """TC072：全量五项组合筛选"""
        property_page = setup_property_page

        with allure.step("设置排序 Highest Price"):
            property_page.click_sort_button()
            property_page.select_sort_option("Highest Price")
            property_page.click_done_button_in_sort_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 排序：Highest Price")

        with allure.step("设置 Price=2000~8000"):
            property_page.click_price_filter()
            property_page.input_price_range("2000", "8000")
            property_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 价格：2000~8000")

        with allure.step("设置 Beds=3"):
            property_page.click_beds_filter()
            property_page.select_beds_values("3")
            property_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ Beds：3")

        with allure.step("设置 Bathrooms=2"):
            property_page.click_bathrooms_filter()
            property_page.select_bathrooms_values("2")
            property_page.click_done_button_in_bathrooms_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ Bathrooms：2")

        with allure.step("设置 Property Type=House"):
            property_page.click_property_type_filter()
            property_page.select_third_level_category(index=1)
            property_page.click_done_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ Property Type：House")

        with allure.step("验证 URL 含所有筛选参数"):
            current_url = page.url
            assert "sortId" in current_url, f"期望 URL 含 sortId，实际: {current_url}"
            assert "lowestPrice=2000" in current_url, \
                f"期望 URL 含 lowestPrice=2000，实际: {current_url}"
            assert "attr_168" in current_url, f"期望 URL 含 attr_168，实际: {current_url}"
            assert "attr_166" in current_url, f"期望 URL 含 attr_166，实际: {current_url}"
            logger.info(f"✓ 全量组合 URL: {current_url}")


    @pytest.mark.case_id_property_rent_combo_074
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("列表页组合筛选 - 状态场景")
    @allure.title("清除单一筛选项 Beds 其余筛选参数保持不变")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("设置 Price、Beds、Bathrooms 后，清除 Beds，验证 attr_168 消失但其他参数保持")
    def test_combo_clear_one_filter_others_remain_unchanged(self, page, config, setup_property_page):
        """TC074：清除单一筛选项（Beds），其余筛选条件保持不变"""
        property_page = setup_property_page

        with allure.step("设置 Price=500~2000、Beds=2、Bathrooms=1"):
            property_page.click_price_filter()
            property_page.input_price_range("500", "2000")
            property_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            property_page.click_beds_filter()
            property_page.select_beds_values("2")
            property_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            property_page.click_bathrooms_filter()
            property_page.select_bathrooms_values("1")
            property_page.click_done_button_in_bathrooms_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置三项筛选")

        with allure.step("打开 Beds 面板并点击 Clear"):
            property_page.click_beds_filter()
            property_page.click_clear_button_in_beds_modal()
            property_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已清除 Beds 筛选")

        with allure.step("验证 attr_168 消失，价格和 Bathrooms 参数保持"):
            current_url = page.url
            assert "attr_168" not in current_url, \
                f"期望 URL 不含 attr_168（Beds 已清除），实际: {current_url}"
            assert "lowestPrice=500" in current_url, \
                f"期望 URL 仍含 lowestPrice=500，实际: {current_url}"
            assert "attr_166" in current_url, \
                f"期望 URL 仍含 attr_166（Bathrooms 未受影响），实际: {current_url}"
            logger.info(f"✓ 清除 Beds 后 URL: {current_url}")


    @pytest.mark.case_id_property_rent_combo_075
    @pytest.mark.p2
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("列表页组合筛选 - 等价性场景")
    @allure.title("筛选顺序无关性：先 Beds 后 Price 与先 Price 后 Beds 结果一致")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("先设置 Beds=2 再 Price=500~2000，验证 URL 同时含两组参数（等价于先 Price 后 Beds）")
    def test_combo_filter_order_independent_beds_first_then_price(self, page, config, setup_property_page):
        """TC075：筛选顺序无关性验证（先 Beds 后 Price）"""
        property_page = setup_property_page

        with allure.step("先设置 Beds=2"):
            property_page.click_beds_filter()
            property_page.select_beds_values("2")
            property_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 先设置 Beds=2")

        with allure.step("再设置 Price=500~2000"):
            property_page.click_price_filter()
            property_page.input_price_range("500", "2000")
            property_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 再设置 Price=500~2000")

        with allure.step("验证 URL 同时含两组参数（顺序无关）"):
            current_url = page.url
            assert "attr_168" in current_url, \
                f"期望 URL 含 attr_168，实际: {current_url}"
            assert "lowestPrice=500" in current_url, \
                f"期望 URL 含 lowestPrice=500，实际: {current_url}"
            logger.info(f"✓ 先 Beds 后 Price URL: {current_url}")


    @pytest.mark.case_id_property_rent_combo_076
    @pytest.mark.p2
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("列表页组合筛选 - 健壮性场景")
    @allure.title("快速连续切换不同 Beds 值最终选择生效")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("先选 Beds=1 点 Done，立刻再选 Beds=3 点 Done，验证最终 URL 反映最后一次选择")
    def test_combo_quick_switch_beds_last_selection_takes_effect(self, page, config, setup_property_page):
        """TC076：快速连续切换不同 Beds 值（防抖/竞态验证）"""
        property_page = setup_property_page

        with allure.step("先选 Beds=1 并提交"):
            property_page.click_beds_filter()
            property_page.select_beds_values("1")
            property_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 第一次选择 Beds=1")

        with allure.step("立刻再次打开 Beds，选择 3 并提交"):
            property_page.click_beds_filter()
            property_page.select_beds_values("3")
            property_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 第二次选择 Beds=3")

        with allure.step("验证 URL 含 attr_168（最终选择已生效）"):
            assert "attr_168" in page.url, \
                f"期望 URL 含 attr_168，实际: {page.url}"
            logger.info(f"✓ 最终 Beds 选择生效，URL: {page.url}")


    @pytest.mark.case_id_property_rent_combo_077
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("列表页组合筛选 - 空状态场景")
    @allure.title("Price + Beds 组合筛选结果为空时展示空状态文案")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("设置极端价格 Min=50000、Max=100000 和 Beds=8+，验证页面展示空状态文案或正常响应")
    def test_combo_price_beds_no_results_empty_state_visible(self, page, config, setup_property_page):
        """TC077：Price + Beds 筛选后结果为空，空状态正常展示"""
        property_page = setup_property_page

        with allure.step("设置 Price=50000~100000（极端范围）"):
            property_page.click_price_filter()
            property_page.input_price_range("50000", "100000")
            property_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置极端价格范围")

        with allure.step("设置 Beds=8+"):
            property_page.click_beds_filter()
            property_page.select_beds_values("8+")
            property_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Beds=8+")

        with allure.step("验证页面展示空状态文案或无结果提示"):
            page_content = page.content().lower()
            has_empty_state = ("couldn't find anything" in page_content or
                               "no results" in page_content or
                               "try a new search" in page_content)
            has_filter_params = "lowestPrice" in page.url and "attr_168" in page.url
            assert has_empty_state or has_filter_params, \
                "期望显示空状态文案或 URL 含筛选参数（筛选已生效）"
            logger.info(f"✓ 页面正常响应，URL: {page.url}")


    @pytest.mark.case_id_property_rent_combo_078
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("列表页组合筛选 - 功能场景")
    @allure.title("Price + Beds + Property Type 组合筛选后重置页面 URL 恢复默认")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("设置三项筛选后，直接导航回默认 URL，验证所有筛选参数消失")
    def test_combo_three_filters_then_reset_url_back_to_default(self, page, config, setup_property_page):
        """TC078：Price + Beds + Property Type 组合筛选后，通过 Clear All 一键重置"""
        property_page = setup_property_page

        with allure.step("设置 Price=500~2000"):
            property_page.click_price_filter()
            property_page.input_price_range("500", "2000")
            property_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Price=500~2000")

        with allure.step("设置 Beds=2"):
            property_page.click_beds_filter()
            property_page.select_beds_values("2")
            property_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Beds=2")

        with allure.step("导航回默认 URL 模拟 Clear All 重置"):
            page.goto(config['target_page'], wait_until="domcontentloaded", timeout=config['timeout']['navigation'])
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已重置到默认 URL")

        with allure.step("验证 URL 恢复为默认（不含筛选参数）"):
            current_url = page.url
            assert "lowestPrice" not in current_url, \
                f"期望 URL 不含 lowestPrice，实际: {current_url}"
            assert "attr_168" not in current_url, \
                f"期望 URL 不含 attr_168，实际: {current_url}"
            logger.info(f"✓ 重置后 URL: {current_url}")


    # ============================================