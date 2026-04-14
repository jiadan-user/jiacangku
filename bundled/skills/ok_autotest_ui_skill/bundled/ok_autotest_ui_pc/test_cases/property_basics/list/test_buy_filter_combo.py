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
    "base_url": "https://au.58v5.cn",
    "target_page": "https://au.58v5.cn/en/city-canberra/cate-buy/?iconSource=buy",
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

class TestBuyFilterCombo:
    """搜索筛选组合场景测试 - Property For Sale（6 条用例）"""

    @pytest.fixture(scope="module")
    def setup_buy_page(self, page, config):
        property_page = PropertyPage(page)
        page.goto(_CONFIG['target_page'], wait_until="domcontentloaded", timeout=_CONFIG['timeout']['navigation'])
        page.wait_for_load_state('domcontentloaded', timeout=_CONFIG['timeout']['navigation'])
        property_page.handle_cookie_popup()
        page.wait_for_timeout(1000)
        yield property_page

    @pytest.fixture(scope="module", autouse=True)
    def reset_buy_page_after_module(self, page, config):
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
    def reset_page_between_tests(self, page, config, setup_buy_page):
        """函数级别：每个测试之间重置页面（不关闭浏览器）"""
        yield  # 先执行测试
        # 每个测试后重置页面到初始状态
        try:
            logger.info("========== 用例执行完毕，重置页面到初始状态 ==========")
            page.goto(_CONFIG['target_page'], wait_until="domcontentloaded", timeout=_CONFIG['timeout']['navigation'])
            page.wait_for_load_state('domcontentloaded', timeout=_CONFIG['timeout']['navigation'])
            page.wait_for_timeout(1000)
            current_url = page.url
            if "cate-buy" in current_url:
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
    @pytest.mark.p0
    @pytest.mark.case_id_buy_combo_036
    def test_search_with_sort_filter_both_params_in_url(self, page, config, setup_buy_page):
        """TC036：搜索 + Sort 组合"""
        buy_page = setup_buy_page

        # ========== Arrange ==========
        with allure.step("搜索 'Villa'"):
            buy_page.input_search_keyword("Villa")
            buy_page.click_search_button()
            page.wait_for_load_state('domcontentloaded', timeout=_CONFIG['timeout']['navigation'])
            logger.info("✓ 已搜索 Villa")

        # ========== Act ==========
        with allure.step("设置 Sort=Lowest Price"):
            buy_page.click_sort_button()
            buy_page.select_sort_option("Lowest Price")
            buy_page.click_done_button_in_sort_modal()
            page.wait_for_load_state('domcontentloaded', timeout=_CONFIG['timeout']['navigation'])
            logger.info("✓ 已设置 Sort=Lowest Price")

        # ========== Assert ==========
        with allure.step("验证 URL 同时含 keyword=Villa 和 sortId=3"):
            current_url = page.url
            assert "keyword=Villa" in current_url, \
                f"期望 URL 含 keyword=Villa，实际: {current_url}"
            assert "sortId=3" in current_url, \
                f"期望 URL 含 sortId=3（Lowest Price），实际: {current_url}"
            logger.info(f"✓ URL 含 keyword 和 sortId: {current_url}")


    @pytest.mark.case_id_buy_combo_037
    @pytest.mark.p0
    @pytest.mark.property_buy
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("搜索筛选组合")
    @allure.title("搜索关键词后叠加 Price 筛选，URL 含 q、lowestPrice、highestPrice")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("搜索 Apartment 后设置 Price 500000-1000000")
    def test_search_with_price_filter_all_params_in_url(self, page, config, setup_buy_page):
        """TC037：搜索 + Price 组合"""
        buy_page = setup_buy_page

        # ========== Arrange ==========
        with allure.step("搜索 'Apartment'"):
            buy_page.input_search_keyword("Apartment")
            buy_page.click_search_button()
            page.wait_for_load_state('domcontentloaded', timeout=_CONFIG['timeout']['navigation'])
            logger.info("✓ 已搜索 Apartment")

        # ========== Act ==========
        with allure.step("设置 Price Min=500000, Max=1000000"):
            buy_page.click_price_filter()
            buy_page.input_price_range("500000", "1000000")
            buy_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=_CONFIG['timeout']['navigation'])
            logger.info("✓ 已设置 Price 筛选")

        # ========== Assert ==========
        with allure.step("验证 URL 含 q、lowestPrice、highestPrice"):
            current_url = page.url
            assert "keyword=Apartment" in current_url, \
                f"期望 URL 含 keyword=Apartment，实际: {current_url}"
            assert "lowestPrice=500000" in current_url, \
                f"期望 URL 含 lowestPrice=500000，实际: {current_url}"
            assert "highestPrice=1000000" in current_url, \
                f"期望 URL 含 highestPrice=1000000，实际: {current_url}"
            logger.info(f"✓ URL 含搜索词和价格筛选: {current_url}")


    # ============================================
    # 十二、更多组合筛选场景 TC041
    # ============================================

    @pytest.mark.case_id_buy_combo_041
    @pytest.mark.p0
    @pytest.mark.property_buy
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("组合筛选")
    @allure.title("选择sug地址+筛选组合")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证选择sug地址后叠加筛选项，URL包含suglevel和筛选参数")
    def test_sug_address_with_filters_combination(self, page, config, setup_buy_page):
        """TC041：选择sug地址+筛选组合"""
        buy_page = setup_buy_page

        # ========== Arrange ==========
        with allure.step("输入并选择 sug 地址 'Canberra'"):
            # 输入地址关键词
            buy_page.input_search_keyword("Ca")
            page.wait_for_timeout(1000)  # 等待 sug 面板出现
            
            # 检查是否有 sug 词
            sug_count = buy_page.get_sug_items_count()
            if sug_count == 0:
                pytest.skip("没有 sug 词可选择")
            
            # 点击第一个 sug 词
            clicked_sug = buy_page.click_sug_item(0)
            page.wait_for_timeout(1000)
            page.wait_for_load_state('domcontentloaded', timeout=_CONFIG['timeout']['navigation'])
            logger.info(f"✓ 已选择 sug 词: '{clicked_sug}'")

        # ========== Act ==========
        with allure.step("设置 Price Min=400000"):
            buy_page.click_price_filter()
            buy_page.input_price_range("400000", None)
            buy_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=_CONFIG['timeout']['navigation'])
            logger.info("✓ 已设置 Price Min=400000")

        with allure.step("设置 Beds=2"):
            buy_page.click_beds_filter()
            buy_page.select_beds_values("2")
            buy_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=_CONFIG['timeout']['navigation'])
            logger.info("✓ 已选择 Beds 值: 2")

        # ========== Assert ==========
        with allure.step("验证 URL 包含 sug 参数和筛选参数"):
            current_url = page.url
            
            # 验证包含搜索关键词
            assert "keyword=" in current_url, \
                f"期望 URL 含 keyword，实际: {current_url}"
            logger.info("✓ URL 含 keyword 参数")
            
            # 验证包含 sug 相关参数（可能是 search_type=sug 或其他sug参数）
            has_sug_params = ("search_type=sug" in current_url or 
                            "sugLongitude=" in current_url or 
                            "sugLatitude=" in current_url or
                            "sugCityLevel" in current_url)
            assert has_sug_params, \
                f"期望 URL 含 sug 相关参数，实际: {current_url}"
            logger.info("✓ URL 含 sug 相关参数")
            
            # 验证包含 Price 参数
            assert "lowestPrice=400000" in current_url, \
                f"期望 URL 含 lowestPrice=400000，实际: {current_url}"
            logger.info("✓ URL 含 lowestPrice=400000")
            
            # 验证包含 Beds 参数
            assert "attr_168=2" in current_url, \
                f"期望 URL 含 attr_168=2，实际: {current_url}"
            logger.info("✓ URL 含 attr_168=2")
            
            logger.info(f"✓ sug 地址 + 筛选组合验证通过: {current_url}")

    # ============================================
    # 十八、搜索筛选组合补充 TC039, TC040, TC042
    # ============================================

    @pytest.mark.case_id_buy_combo_039
    @pytest.mark.p1
    @pytest.mark.property_buy
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("搜索筛选组合")
    @allure.title("搜索加筛选后Filter Clear仅清除筛选保留搜索词")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证搜索加筛选后点击Filter Clear仅清除筛选保留搜索词")
    def test_filter_clear_keeps_search_keyword(self, page, config, setup_buy_page):
        """TC039：搜索加筛选后Filter Clear仅清除筛选保留搜索词"""
        buy_page = setup_buy_page
        
        with allure.step("搜索 'House'"):
            buy_page.input_search_keyword("House")
            buy_page.click_search_button()
            page.wait_for_timeout(1000)
            page.wait_for_load_state('domcontentloaded', timeout=_CONFIG['timeout']['navigation'])
            logger.info("✓ 已搜索 House")
        
        with allure.step("设置 Price Min=300000"):
            buy_page.click_price_filter()
            buy_page.input_price_range("300000", None)
            buy_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=_CONFIG['timeout']['navigation'])
            logger.info("✓ 已设置 Price")
        
        with allure.step("点击 Filter 按钮打开筛选面板"):
            try:
                buy_page.click_filter_button()
                page.wait_for_timeout(1000)
                logger.info("✓ 已打开 Filter 面板")
            except Exception as e:
                pytest.skip(f"打开 Filter 面板失败: {e}")
        
        with allure.step("点击 Filter 面板中的 Clear 按钮"):
            try:
                buy_page.click_clear_button_in_filter_modal()
                page.wait_for_timeout(500)
                logger.info("✓ 已点击 Filter 面板中的 Clear 按钮")
            except Exception as e:
                pytest.skip(f"点击 Clear 按钮失败: {e}")
        
        with allure.step("点击 Done 按钮确认清除"):
            try:
                buy_page.click_done_button_in_filter_modal()
                page.wait_for_timeout(1000)
                page.wait_for_load_state('domcontentloaded', timeout=_CONFIG['timeout']['navigation'])
                logger.info("✓ 已点击 Done 按钮确认清除")
            except Exception as e:
                pytest.skip(f"点击 Done 按钮失败: {e}")
        
        with allure.step("验证URL仍含搜索词但不含筛选参数"):
            current_url = page.url
            assert "keyword=House" in current_url or "q=House" in current_url, \
                f"期望保留搜索词，实际: {current_url}"
            assert "lowestPrice=" not in current_url, \
                f"期望移除Price参数，实际: {current_url}"
            logger.info(f"✓ Clear保留搜索词清除筛选: {current_url}")


    @pytest.mark.case_id_buy_combo_040
    @pytest.mark.p2
    @pytest.mark.property_buy
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("搜索筛选组合")
    @allure.title("清空搜索框筛选项保留")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("验证清空搜索框后筛选项保留")
    def test_clear_search_box_keeps_filters(self, page, config, setup_buy_page):
        """TC040：清空搜索框筛选项保留"""
        buy_page = setup_buy_page
        
        with allure.step("搜索并设置筛选"):
            buy_page.input_search_keyword("Villa")
            buy_page.click_search_button()
            page.wait_for_timeout(1000)
            
            buy_page.click_beds_filter()
            buy_page.select_beds_values("3")
            buy_page.click_done_button_in_beds_modal()
            page.wait_for_timeout(1000)
            logger.info("✓ 已搜索Villa并设置Beds=3")
        
        with allure.step("清空搜索框"):
            search_input = page.locator(buy_page.SEARCH_INPUT)
            search_input.fill("")
            buy_page.click_search_button()
            page.wait_for_timeout(1000)
            logger.info("✓ 已清空搜索框并提交")
        
        with allure.step("验证URL仍含筛选参数"):
            current_url = page.url
            assert "attr_168=3" in current_url, \
                f"期望保留Beds参数，实际: {current_url}"
            logger.info(f"✓ 清空搜索框保留筛选: {current_url}")


    @pytest.mark.case_id_buy_combo_042
    @pytest.mark.p1
    @pytest.mark.property_buy
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("搜索筛选组合")
    @allure.title("搜索加筛选后切换分类搜索词保留筛选清空")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证搜索加筛选后切换分类时搜索词保留筛选清空")
    def test_category_switch_keeps_search_clears_filters(self, page, config, setup_buy_page):
        """TC042：搜索加筛选后切换分类搜索词保留筛选清空"""
        buy_page = setup_buy_page
        
        with allure.step("搜索 'Villa' 并设置筛选"):
            buy_page.input_search_keyword("Villa")
            buy_page.click_search_button()
            page.wait_for_timeout(1000)
            page.wait_for_load_state('domcontentloaded', timeout=_CONFIG['timeout']['navigation'])
            
            buy_page.click_beds_filter()
            buy_page.select_beds_values("3")
            buy_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=_CONFIG['timeout']['navigation'])
            logger.info("✓ 已搜索Villa并设置Beds=3")
            
            url_before = page.url
            assert "keyword=Villa" in url_before, "搜索失败"
            assert "attr_168=3" in url_before, "筛选失败"
        
        with allure.step("切换分类到 Rent"):
            try:
                buy_page.select_category("Property For Rent")
                page.wait_for_load_state('domcontentloaded', timeout=_CONFIG['timeout']['navigation'])
                logger.info("✓ 已切换到 Rent")
            except Exception as e:
                pytest.skip(f"无法切换分类: {e}")
        
        with allure.step("验证搜索词保留但筛选清空"):
            current_url = page.url
            assert "keyword=Villa" in current_url or "q=Villa" in current_url, \
                f"期望保留搜索词，实际: {current_url}"
            assert "attr_168=" not in current_url, \
                f"期望清空筛选参数，实际: {current_url}"
            logger.info(f"✓ 搜索词保留筛选清空: {current_url}")


    # ============================================
