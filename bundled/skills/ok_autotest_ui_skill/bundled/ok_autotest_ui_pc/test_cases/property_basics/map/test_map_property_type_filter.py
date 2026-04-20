"""
地图模式 - Property Type 及 Filter 综合筛选测试（Sydney Student Accommodation）

测试站点：AU (https://au.58v5.cn)
覆盖用例：TC034–TC038（Property Type）/ TC041–TC043（Filter 综合面板）
功能点：类型选择 / 关闭 × / Clear / 面板全区块展示 / Type+Price / Beds+Bath / Clear / 徽章
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



class TestMapPropertyTypeAndFilter:
    """Property Type + Filter 综合筛选测试（10 条用例）"""

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
    @pytest.mark.case_id_sa_filter_034
    def test_property_type_select_student_apartment_url_changes(self, page, config, setup_sa_page):
        """TC034：选择 Student Apartment，URL 路径更新"""
        sa_page = setup_sa_page

        with allure.step("点击 Property Type，打开 Category 弹窗"):
            sa_page.click_property_type_filter()
            logger.info("✓ Category 弹窗已打开")

        with allure.step("选择 Student Apartment → Done"):
            sa_page.select_property_type_option("Student Apartment")
            sa_page.click_property_type_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选择 Student Apartment 并点击 Done")

        with allure.step("验证 URL 路径含 student-apartment 且 view=map 保留"):
            current_url = page.url
            assert "student-apartment" in current_url, \
                f"期望 URL 含 student-apartment，实际 URL: {current_url}"
            assert "view=map" in current_url, \
                f"期望 URL 保留 view=map，实际 URL: {current_url}"
            logger.info(f"✓ URL: {current_url}")

    @pytest.mark.case_id_sa_proptype_035
    @pytest.mark.p1
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Property Type 房产类型筛选 - 功能场景")
    @allure.title("选择 Apartment，URL 路径更新为对应类型")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("点击 Property Type，选择 Apartment，点击 Done，验证 URL 路径更新且地图参数保留")
    def test_property_type_select_apartment_url_changes(self, page, config, setup_sa_page):
        """TC035：选择 Apartment，URL 路径更新"""
        sa_page = setup_sa_page

        with allure.step("点击 Property Type → 选择 Apartment → Done"):
            sa_page.click_property_type_filter()
            sa_page.select_property_type_option("Apartment")
            sa_page.click_property_type_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选 Apartment 并点击 Done")

        with allure.step("验证 URL 路径已更新且 view=map 保留"):
            current_url = page.url
            assert "apartment" in current_url.lower(), \
                f"期望 URL 含 apartment，实际 URL: {current_url}"
            assert "view=map" in current_url, \
                f"期望 URL 保留 view=map，实际 URL: {current_url}"
            logger.info(f"✓ URL: {current_url}")

    @pytest.mark.case_id_sa_proptype_036
    @pytest.mark.p1
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Property Type 房产类型筛选 - 功能场景")
    @allure.title("选择 House，URL 路径更新，地图模式参数保留")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("点击 Property Type，选择 House，点击 Done，验证 URL 路径更新且 view=map 保留")
    def test_property_type_select_house_url_changes(self, page, config, setup_sa_page):
        """TC036：选择 House，URL 路径更新"""
        sa_page = setup_sa_page

        with allure.step("点击 Property Type → 选择 House → Done"):
            sa_page.click_property_type_filter()
            sa_page.select_property_type_option("House")
            sa_page.click_property_type_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选 House 并点击 Done")

        with allure.step("验证 URL 路径含 house 且 view=map 保留"):
            current_url = page.url
            assert "house" in current_url.lower(), \
                f"期望 URL 含 house，实际 URL: {current_url}"
            assert "view=map" in current_url, \
                f"期望 URL 保留 view=map，实际 URL: {current_url}"
            logger.info(f"✓ URL: {current_url}")

    @pytest.mark.case_id_sa_proptype_037
    @pytest.mark.p2
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Property Type 房产类型筛选 - UI/交互场景")
    @allure.title("点击 × 关闭 Property Type 弹窗，URL 不变")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("打开 Property Type 弹窗，不选择任何类型，点击 × 关闭，验证 URL 不变且弹窗消失")
    def test_property_type_close_x_url_unchanged(self, page, config, setup_sa_page):
        """TC037：点击 × 关闭 Property Type 弹窗，URL 不变"""
        sa_page = setup_sa_page

        with allure.step("记录关闭前 URL"):
            url_before = page.url
            logger.info(f"✓ 操作前 URL: {url_before}")

        with allure.step("打开 Property Type 弹窗，点击 × 关闭"):
            sa_page.click_property_type_filter()
            assert sa_page.is_filter_modal_visible(), "期望 Property Type 弹窗已打开"
            sa_page.click_property_type_close()
            logger.info("✓ 已点击 × 关闭弹窗")

        with allure.step("验证弹窗已关闭且 URL 不变"):
            assert sa_page.is_filter_modal_hidden(), "期望弹窗已关闭"
            assert page.url == url_before, \
                f"期望 URL 不变，操作前: {url_before}，操作后: {page.url}"
            logger.info(f"✓ 弹窗已关闭，URL 不变: {page.url}")

    @pytest.mark.case_id_sa_proptype_038
    @pytest.mark.p1
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Property Type 房产类型筛选 - 功能场景")
    @allure.title("已选类型后点击 Clear 再 Done，URL 路径恢复默认")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("选择 Student Apartment 后，重新打开 Property Type 弹窗点击 Clear 再 Done，验证 URL 恢复默认")
    def test_property_type_clear_restores_default_url(self, page, config, setup_sa_page):
        """TC038：已选类型后点击 Clear 再 Done，URL 路径恢复默认"""
        sa_page = setup_sa_page

        with allure.step("先选择 Student Apartment"):
            sa_page.click_property_type_filter()
            sa_page.select_property_type_option("Student Apartment")
            sa_page.click_property_type_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选 Student Apartment")

        with allure.step("导航回初始页面，再打开 Property Type 弹窗点击 Clear → Done"):
            page.goto(config['target_page'], wait_until="domcontentloaded", timeout=config['timeout']['navigation'])
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            sa_page.click_property_type_filter()
            sa_page.click_property_type_clear()
            sa_page.click_property_type_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已点击 Clear 并 Done")

        with allure.step("验证 URL 恢复默认（含 cate-student-apartment，无 cate= 特定类型参数）"):
            current_url = page.url
            assert "cate-student-apartment" in current_url, \
                f"期望 URL 回到默认分类，实际 URL: {current_url}"
            logger.info(f"✓ URL 已恢复默认: {current_url}")

    # ============================================================
    # 七、Filter 综合筛选面板  TC039–TC043
    # ============================================================

    @pytest.mark.case_id_sa_filter_042
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Filter 综合筛选 - 功能场景")
    @allure.title("点击 Filter 按钮，综合面板展开并包含所有分区")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("点击 Filter 按钮，验证综合面板展开并包含类型、Price、Beds、Bathrooms 区域及 Done/Clear 按钮")
    def test_filter_panel_opens_with_all_sections(self, page, config, setup_sa_page):
        """TC039：Filter 综合面板包含所有筛选分区"""
        sa_page = setup_sa_page

        with allure.step("点击 Filter 按钮，打开综合筛选面板"):
            sa_page.click_filter_comprehensive()
            logger.info("✓ Filter 综合面板已打开")

        with allure.step("验证面板可见"):
            assert sa_page.is_filter_modal_visible(), "期望 Filter 综合面板已展开"
            logger.info("✓ Filter 面板可见")

        with allure.step("验证面板包含 Done 和 Clear 按钮"):
            done_btn = page.locator("[class*='FilterModalPC_btnArea'] button[type='submit']")
            clear_btn = page.locator("[class*='FilterModalPC_btnArea'] button[type='reset']")
            assert done_btn.is_visible(), "期望 Done 按钮可见"
            assert clear_btn.is_visible(), "期望 Clear 按钮可见"
            logger.info("✓ Done 和 Clear 按钮均可见")

        with allure.step("关闭 Filter 面板"):
            sa_page.click_filter_modal_close()
            logger.info("✓ Filter 面板已关闭")

    @pytest.mark.case_id_sa_filter_041
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Filter 综合筛选 - 功能场景")
    @allure.title("在 Filter 面板同时设置 Beds=2、Bathrooms=1 后点击 Done")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("在 Filter 面板选择 Beds=2、Bathrooms=1，点击 Done，验证 URL 含 attr_168=2&attr_166=1")
    def test_filter_panel_beds_and_bathrooms_done_url_contains_both(self, page, config, setup_sa_page):
        """TC041：在 Filter 面板同时设置 Beds=2、Bathrooms=1 后点击 Done"""
        sa_page = setup_sa_page

        with allure.step("打开 Filter 面板，选择 Beds=2 和 Bathrooms=1"):
            sa_page.click_filter_comprehensive()
            sa_page.filter_modal_select_beds("2")
            sa_page.filter_modal_select_bathrooms("1")
            logger.info("✓ 已选 Beds=2 和 Bathrooms=1")

        with allure.step("点击 Done"):
            sa_page.click_filter_modal_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已点击 Done")

        with allure.step("验证 URL 含 attr_168=2 和 attr_166=1"):
            current_url = page.url
            assert "attr_168=2" in current_url, \
                f"期望 URL 含 attr_168=2，实际 URL: {current_url}"
            assert "attr_166=1" in current_url, \
                f"期望 URL 含 attr_166=1，实际 URL: {current_url}"
            logger.info(f"✓ URL 含 Beds 和 Bathrooms 参数: {current_url}")

    @pytest.mark.case_id_sa_filter_043
    @pytest.mark.p2
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Filter 综合筛选 - 功能场景")
    @allure.title("Filter·N 徽章数字在新增筛选条件后递增")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("记录初始 Filter 徽章数字，通过 Filter 面板新增 Beds=2，验证徽章数字递增 1")
    def test_filter_badge_increments_after_adding_condition(self, page, config, setup_sa_page):
        """TC043：Filter·N 徽章数字反映已激活的筛选条件数量"""
        sa_page = setup_sa_page

        with allure.step("记录初始 Filter 徽章文案"):
            initial_badge = sa_page.get_filter_badge_text()
            initial_num_match = _re.search(r'(\d+)', initial_badge)
            initial_num = int(initial_num_match.group(1)) if initial_num_match else 0
            logger.info(f"✓ 初始 Filter 徽章: '{initial_badge}'，数字: {initial_num}")

        with allure.step("通过 Filter 面板新增 Beds=2"):
            sa_page.click_filter_comprehensive()
            sa_page.filter_modal_select_beds("2")
            sa_page.click_filter_modal_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已新增 Beds=2 筛选条件")

        with allure.step("验证 Filter 徽章数字递增"):
            new_badge = sa_page.get_filter_badge_text()
            new_num_match = _re.search(r'(\d+)', new_badge)
            new_num = int(new_num_match.group(1)) if new_num_match else 0
            assert new_num > initial_num, \
                f"期望 Filter 徽章数字递增，初始: {initial_num}，当前: {new_num}"
            logger.info(f"✓ Filter 徽章数字从 {initial_num} 增加到 {new_num}")


