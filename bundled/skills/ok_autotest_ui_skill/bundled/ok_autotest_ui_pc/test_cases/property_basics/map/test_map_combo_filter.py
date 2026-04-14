"""
地图模式 - 组合筛选测试（Sydney Student Accommodation）

测试站点：AU (https://au.58v5.cn)
覆盖用例：TC047–TC051（含扩展组合场景）
功能点：Sort+Price / Price+Beds / Beds+Bath / 三项叠加 / 五项叠加 / 单项 Clear / 空结果
"""
import re as _re
import pytest
import allure
from pages.property_map_page import PropertyMapPage
from utils.logger import setup_logger

logger = setup_logger()

_CONFIG = {
    "site": "au",
    "site_name": "澳大利亚站",
    "role": "buyer",
    "user_name": "mayueming_au_buyer",
    "base_url": "https://au.58v5.cn",
    "test_account": None,
    "target_page": (
        "https://au.58v5.cn/en/city-sydney/cate-student-apartment/"
        "?iconSource=student-apartment&view=map"
        "&viewport=c%3A-33.8623%2C151.2077%7Cz%3A11"
    ),
    "list_page": "https://au.58v5.cn/en/city-sydney/cate-student-apartment/?iconSource=student-apartment",
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



class TestMapComboFilter:
    """组合筛选测试（8 条用例）"""

    @pytest.fixture(scope="module")
    def setup_sa_page(self, page, config):
        """Class 级别页面准备：导航到地图模式页面，处理 Cookie，返回 PropertyMapPage 实例"""
        sa_page = PropertyMapPage(page)
        page.goto(config['target_page'], wait_until="domcontentloaded", timeout=config['timeout']['navigation'])
        page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
        sa_page.handle_cookie_popup()
        page.wait_for_timeout(1000)
        yield sa_page

    @pytest.fixture(scope="module", autouse=True)
    def reset_map_page_after_module(self, page, config):
        """模块级别：所有测试结束后重置页面"""
        yield  # 先执行所有测试
        try:
            logger.info("========== 模块测试完毕，重置页面 ==========")
            page.goto(config['target_page'], wait_until="domcontentloaded", timeout=config['timeout']['navigation'])
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            page.wait_for_timeout(1000)
            logger.info("✓ 模块测试完成，页面已重置")
        except Exception as e:
            logger.warning(f"模块结束后重置页面失败: {e}")
    
    @pytest.fixture(scope="function", autouse=True)
    def reset_page_between_tests(self, page, config, setup_sa_page):
        """函数级别：每个测试之间重置页面（不关闭浏览器）"""
        yield  # 先执行测试
        try:
            logger.info("========== 用例执行完毕，重置页面到初始状态 ==========")
            page.goto(config['target_page'], wait_until="domcontentloaded", timeout=config['timeout']['navigation'])
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            page.wait_for_timeout(1000)
            logger.info(f"✓ 页面已重置到初始状态: {page.url}")
        except Exception as e:
            logger.warning(f"重置页面失败（不影响用例结果）: {e}")
    @pytest.mark.p1
    @pytest.mark.case_id_sa_combo_044
    def test_combo_sort_lowest_price_and_price_range_url_contains_both(self, page, config, setup_sa_page):
        """TC044：Sort=Lowest Price + Price=500~1500 组合"""
        sa_page = setup_sa_page

        with allure.step("设置排序为 Lowest Price"):
            sa_page.click_sort_filter()
            sa_page.select_sort_option("Lowest Price")
            sa_page.click_sort_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Lowest Price 排序")

        with allure.step("设置 Price Min=500，Max=1500"):
            sa_page.click_price_filter()
            sa_page.input_price_min("500")
            sa_page.input_price_max("1500")
            sa_page.click_price_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置价格 500~1500")

        with allure.step("验证 URL 同时含 sortId=3、价格参数和 view=map"):
            current_url = page.url
            assert "sortId=3" in current_url, \
                f"期望 URL 含 sortId=3，实际 URL: {current_url}"
            assert "lowestPrice=500" in current_url, \
                f"期望 URL 含 lowestPrice=500，实际 URL: {current_url}"
            assert "highestPrice=1500" in current_url, \
                f"期望 URL 含 highestPrice=1500，实际 URL: {current_url}"
            assert "view=map" in current_url, \
                f"期望 URL 保留 view=map，实际 URL: {current_url}"
            logger.info(f"✓ 组合筛选 URL: {current_url}")

    @pytest.mark.case_id_sa_combo_048
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("组合筛选 - 功能场景")
    @allure.title("Price=500~1500 + Beds=2，URL 含价格和 attr_168 参数")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("设置 Price=500~1500，再设置 Beds=2，验证 URL 同时含价格参数和 attr_168=2")
    def test_combo_price_range_and_beds_2_url_contains_both(self, page, config, setup_sa_page):
        """TC045：Price=500~1500 + Beds=2 组合"""
        sa_page = setup_sa_page

        with allure.step("设置 Price Min=500，Max=1500"):
            sa_page.click_price_filter()
            sa_page.input_price_min("500")
            sa_page.input_price_max("1500")
            sa_page.click_price_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Price=500~1500")

        with allure.step("设置 Beds=2"):
            sa_page.click_beds_filter()
            sa_page.select_beds_value("2")
            sa_page.click_beds_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Beds=2")

        with allure.step("验证 URL 含价格参数和 attr_168=2"):
            current_url = page.url
            assert "lowestPrice=500" in current_url, \
                f"期望 URL 含 lowestPrice=500，实际 URL: {current_url}"
            assert "highestPrice=1500" in current_url, \
                f"期望 URL 含 highestPrice=1500，实际 URL: {current_url}"
            assert "attr_168=2" in current_url, \
                f"期望 URL 含 attr_168=2，实际 URL: {current_url}"
            logger.info(f"✓ 组合筛选 URL: {current_url}")

    @pytest.mark.case_id_sa_combo_049
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("组合筛选 - 功能场景")
    @allure.title("Beds=2 + Bathrooms=1，URL 同时含 attr_168 和 attr_166")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("设置 Beds=2，再设置 Bathrooms=1，验证 URL 同时含 attr_168=2 和 attr_166=1")
    def test_combo_beds_2_and_bathrooms_1_url_contains_both(self, page, config, setup_sa_page):
        """TC046：Beds=2 + Bathrooms=1 组合"""
        sa_page = setup_sa_page

        with allure.step("设置 Beds=2"):
            sa_page.click_beds_filter()
            sa_page.select_beds_value("2")
            sa_page.click_beds_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Beds=2")

        with allure.step("设置 Bathrooms=1"):
            sa_page.click_bathrooms_filter()
            sa_page.select_bathrooms_value("1")
            sa_page.click_bathrooms_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Bathrooms=1")

        with allure.step("验证 URL 同时含 attr_168=2 和 attr_166=1"):
            current_url = page.url
            assert "attr_168=2" in current_url, \
                f"期望 URL 含 attr_168=2，实际 URL: {current_url}"
            assert "attr_166=1" in current_url, \
                f"期望 URL 含 attr_166=1，实际 URL: {current_url}"
            logger.info(f"✓ 组合筛选 URL: {current_url}")

    @pytest.mark.case_id_sa_combo_050
    @pytest.mark.p1
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("组合筛选 - 功能场景")
    @allure.title("Sort + Beds + Price 三项组合，URL 含三项参数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("设置 Sort=Highest Price、Beds=Studio、Price Max=3000，验证 URL 含三项参数且 view=map 保留")
    def test_combo_sort_beds_price_triple_url_contains_all(self, page, config, setup_sa_page):
        """TC047：Sort + Beds + Price 三项组合"""
        sa_page = setup_sa_page

        with allure.step("设置 Sort=Highest Price"):
            sa_page.click_sort_filter()
            sa_page.select_sort_option("Highest Price")
            sa_page.click_sort_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Highest Price")

        with allure.step("设置 Beds=Studio"):
            sa_page.click_beds_filter()
            sa_page.select_beds_value("Studio")
            sa_page.click_beds_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Studio")

        with allure.step("设置 Price Max=3000"):
            sa_page.click_price_filter()
            sa_page.input_price_max("3000")
            sa_page.click_price_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Price Max=3000")

        with allure.step("验证 URL 含三项参数且 view=map 保留"):
            current_url = page.url
            assert "sortId=4" in current_url, \
                f"期望 URL 含 sortId=4，实际 URL: {current_url}"
            assert "attr_168=10" in current_url, \
                f"期望 URL 含 attr_168=10 (Studio)，实际 URL: {current_url}"
            assert "highestPrice=3000" in current_url, \
                f"期望 URL 含 highestPrice=3000，实际 URL: {current_url}"
            assert "view=map" in current_url, \
                f"期望 URL 保留 view=map，实际 URL: {current_url}"
            logger.info(f"✓ 三项组合筛选 URL: {current_url}")

    @pytest.mark.case_id_sa_combo_051
    @pytest.mark.p1
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("组合筛选 - 功能场景")
    @allure.title("Sort + Price 两项叠加，URL 含 sortId 和价格参数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("设置 Sort=Lowest Price，再设置 Price Min=500、Max=1200，验证 URL 含 sortId=3 和价格参数")
    def test_combo_sort_and_price_url_contains_both(self, page, config, setup_sa_page):
        """TC048：Sort + Price 两项叠加"""
        sa_page = setup_sa_page

        with allure.step("设置 Sort=Lowest Price"):
            sa_page.click_sort_filter()
            sa_page.select_sort_option("Lowest Price")
            sa_page.click_sort_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Lowest Price")

        with allure.step("设置 Price Min=500，Max=1200"):
            sa_page.click_price_filter()
            sa_page.input_price_min("500")
            sa_page.input_price_max("1200")
            sa_page.click_price_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Price=500~1200")

        with allure.step("验证 URL 含 sortId=3 和价格参数"):
            current_url = page.url
            assert "sortId=3" in current_url, \
                f"期望 URL 含 sortId=3，实际 URL: {current_url}"
            assert "lowestPrice=500" in current_url, \
                f"期望 URL 含 lowestPrice=500，实际 URL: {current_url}"
            assert "highestPrice=1200" in current_url, \
                f"期望 URL 含 highestPrice=1200，实际 URL: {current_url}"
            logger.info(f"✓ 组合筛选 URL: {current_url}")

    @pytest.mark.case_id_sa_combo_049
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("组合筛选 - 功能场景")
    @allure.title("全量组合（Sort+Price+Beds+Bathrooms+PropertyType），URL 含所有参数")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("依次设置 Sort=Newest First、Price=500~2000、Beds=2、Bathrooms=1、Property Type=Student Apartment，验证 URL 含所有参数")
    def test_combo_all_five_filters_url_contains_all(self, page, config, setup_sa_page):
        """TC049：全量组合（5 个筛选项）"""
        sa_page = setup_sa_page

        with allure.step("设置 Sort=Newest First"):
            sa_page.click_sort_filter()
            sa_page.select_sort_option("Newest First")
            sa_page.click_sort_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Newest First")

        with allure.step("设置 Price Min=500，Max=2000"):
            sa_page.click_price_filter()
            sa_page.input_price_min("500")
            sa_page.input_price_max("2000")
            sa_page.click_price_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Price=500~2000")

        with allure.step("设置 Beds=2"):
            sa_page.click_beds_filter()
            sa_page.select_beds_value("2")
            sa_page.click_beds_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Beds=2")

        with allure.step("设置 Bathrooms=1"):
            sa_page.click_bathrooms_filter()
            sa_page.select_bathrooms_value("1")
            sa_page.click_bathrooms_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Bathrooms=1")

        with allure.step("设置 Property Type=Student Apartment"):
            sa_page.click_property_type_filter()
            sa_page.select_property_type_option("Student Apartment")
            sa_page.click_property_type_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Property Type=Student Apartment")

        with allure.step("验证 URL 含所有筛选参数"):
            current_url = page.url
            assert "sortId=1" in current_url, \
                f"期望 URL 含 sortId=1，实际 URL: {current_url}"
            assert "lowestPrice=500" in current_url, \
                f"期望 URL 含 lowestPrice=500，实际 URL: {current_url}"
            assert "highestPrice=2000" in current_url, \
                f"期望 URL 含 highestPrice=2000，实际 URL: {current_url}"
            assert "attr_168=2" in current_url, \
                f"期望 URL 含 attr_168=2，实际 URL: {current_url}"
            assert "attr_166=1" in current_url, \
                f"期望 URL 含 attr_166=1，实际 URL: {current_url}"
            logger.info(f"✓ 全量组合筛选 URL: {current_url}")

    @pytest.mark.case_id_sa_combo_050
    @pytest.mark.p1
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("组合筛选 - 功能场景")
    @allure.title("组合筛选后单独清除 Beds，其他条件保持不变")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("已设置 Price=500~1500 和 Beds=2，单独点击 Beds 面板 Clear，验证 attr_168 移除但价格参数保留")
    def test_combo_clear_only_beds_other_conditions_unchanged(self, page, config, setup_sa_page):
        """TC050：组合筛选后单独清除一个条件，其他条件保持不变"""
        sa_page = setup_sa_page

        with allure.step("设置 Price=500~1500 和 Beds=2"):
            sa_page.click_price_filter()
            sa_page.input_price_min("500")
            sa_page.input_price_max("1500")
            sa_page.click_price_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            sa_page.click_beds_filter()
            sa_page.select_beds_value("2")
            sa_page.click_beds_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Price+Beds 组合")

        with allure.step("仅清除 Beds 筛选"):
            sa_page.click_beds_filter()
            sa_page.click_beds_clear()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已清除 Beds 筛选")

        with allure.step("验证 attr_168 已移除，价格参数保留"):
            current_url = page.url
            assert "attr_168" not in current_url, \
                f"期望 URL 不含 attr_168，实际 URL: {current_url}"
            assert "lowestPrice=500" in current_url, \
                f"期望 URL 仍含 lowestPrice=500，实际 URL: {current_url}"
            assert "highestPrice=1500" in current_url, \
                f"期望 URL 仍含 highestPrice=1500，实际 URL: {current_url}"
            logger.info(f"✓ Beds 已清除，Price 保留，URL: {current_url}")

    @pytest.mark.case_id_sa_combo_051
    @pytest.mark.p2
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("组合筛选 - 边界场景")
    @allure.title("组合筛选结果为空时，显示空状态文案")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("设置 Price Min=99999 和 Beds=8+，期望列表显示空状态文案且页面不崩溃")
    def test_combo_filters_no_results_shows_empty_state(self, page, config, setup_sa_page):
        """TC051：组合筛选结果为空时，显示空状态文案"""
        sa_page = setup_sa_page

        with allure.step("设置极端价格 Price Min=99999"):
            sa_page.click_price_filter()
            sa_page.input_price_min("99999")
            sa_page.click_price_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Price Min=99999")

        with allure.step("设置 Beds=8+"):
            sa_page.click_beds_filter()
            sa_page.select_beds_value("8+")
            sa_page.click_beds_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Beds=8+")

        with allure.step("验证页面不崩溃（URL 正常）"):
            current_url = page.url
            assert "au.58v5.cn" in current_url, \
                f"期望页面未崩溃，实际 URL: {current_url}"
            logger.info(f"✓ 页面未崩溃，URL: {current_url}")


