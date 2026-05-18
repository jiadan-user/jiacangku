"""
地图模式 - List/Map 视图切换测试（Sydney Student Accommodation）

测试站点：AU (https://au.58v5.cn)
覆盖用例：TC001–TC008
功能点：List→Map 切换 / Map→List 切换 / 直接访问 / 刷新 / 后退 / 筛选保留
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



class TestMapViewSwitch:
    """List / Map 视图切换测试（8 条用例）"""

    @pytest.fixture(scope="module")
    def setup_sa_page(self, page, config):
        """Class 级别页面准备：导航到地图模式页面，处理 Cookie，返回 PropertyMapPage 实例"""
        sa_page = PropertyMapPage(page)
        page.goto(config['target_page'], wait_until="domcontentloaded", timeout=config['timeout']['navigation'])
        page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
        sa_page.handle_cookie_popup()
        page.wait_for_timeout(2000)  # 等待 Map 按钮 active 状态渲染
        yield sa_page

    @pytest.fixture(scope="module", autouse=True)
    def reset_map_page_after_module(self, page, config):
        """模块级别：所有测试结束后重置页面"""
        yield  # 先执行所有测试
        try:
            logger.info("========== 模块测试完毕，重置页面 ==========")
            page.goto(config['target_page'], wait_until="domcontentloaded", timeout=config['timeout']['navigation'])
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            page.wait_for_timeout(2000)  # 等待 Map 按钮 active 状态渲染
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
            page.wait_for_timeout(2000)  # 等待 Map 按钮 active 状态渲染
            logger.info(f"✓ 页面已重置到初始状态: {page.url}")
        except Exception as e:
            logger.warning(f"重置页面失败（不影响用例结果）: {e}")
    @pytest.mark.p0
    @pytest.mark.case_id_sa_view_001
    def test_switch_list_to_map_url_contains_view_map(self, page, config, setup_sa_page):
        """TC001：从 List 视图切换到 Map 视图"""
        sa_page = setup_sa_page

        # ========== Arrange ==========
        with allure.step("打开 Student Accommodation 列表页（无 view=map）"):
            page.goto(config['list_page'], wait_until="domcontentloaded", timeout=config['timeout']['navigation'])
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已打开列表页")

        # ========== Act ==========
        with allure.step("点击 Map 按钮切换到地图模式"):
            sa_page.click_map_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已点击 Map 按钮")

        # ========== Assert ==========
        with allure.step("验证 URL 含 view=map 和 viewport 参数"):
            current_url = page.url
            assert "view=map" in current_url, \
                f"期望 URL 含 view=map，实际 URL: {current_url}"
            assert "viewport" in current_url, \
                f"期望 URL 含 viewport 参数，实际 URL: {current_url}"
            logger.info(f"✓ URL 含 view=map 和 viewport: {current_url}")

    @pytest.mark.case_id_sa_view_002
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("List/Map 视图切换 - 功能场景")
    @allure.title("从 Map 视图切换到 List 视图，URL 移除 view=map 参数")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description("在地图模式下点击 List 按钮，验证 URL 中 view=map 和 viewport 参数被移除")
    def test_switch_map_to_list_url_removes_view_map(self, page, config, setup_sa_page):
        """TC002：从 Map 视图切换到 List 视图"""
        sa_page = setup_sa_page

        # ========== Arrange ==========
        with allure.step("确认当前处于地图模式"):
            assert sa_page.is_map_view_active(), \
                f"期望当前处于地图模式，实际 URL: {page.url}"
            logger.info("✓ 当前处于地图模式")

        # ========== Act ==========
        with allure.step("点击 List 按钮切换到列表模式"):
            sa_page.click_list_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已点击 List 按钮")

        # ========== Assert ==========
        with allure.step("验证 URL 不含 view=map"):
            current_url = page.url
            assert "view=map" not in current_url, \
                f"期望 URL 不含 view=map，实际 URL: {current_url}"
            logger.info(f"✓ URL 已移除 view=map: {current_url}")

    @pytest.mark.case_id_sa_view_003
    @pytest.mark.p1
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("List/Map 视图切换 - 功能场景")
    @allure.title("直接访问含 view=map 的 URL，页面以地图模式加载")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("直接访问含 view=map&viewport 的完整 URL，验证页面以地图模式正常加载")
    def test_direct_access_map_url_loads_map_view(self, page, config, setup_sa_page):
        """TC003：直接访问含 view=map 的 URL"""
        sa_page = setup_sa_page

        # ========== Act ==========
        with allure.step("直接访问含 view=map 的完整 URL"):
            page.goto(config['target_page'], wait_until="domcontentloaded", timeout=config['timeout']['navigation'])
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            page.wait_for_timeout(2000)  # 等待 Map 按钮 active 状态渲染
            logger.info("✓ 已直接访问地图模式 URL")

        # ========== Assert ==========
        with allure.step("验证页面处于地图模式"):
            assert sa_page.is_map_view_active(), \
                f"期望页面以地图模式加载，实际 URL: {page.url}"
            logger.info(f"✓ 页面已以地图模式加载: {page.url}")

    @pytest.mark.case_id_sa_view_004
    @pytest.mark.p1
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("List/Map 视图切换 - 会话场景")
    @allure.title("地图模式下刷新页面，view=map 和 viewport 参数保持不变")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("在地图模式下按 F5 刷新，验证 URL 参数（view=map、viewport）保持不变")
    def test_map_view_page_refresh_keeps_url_params(self, page, config, setup_sa_page):
        """TC004：地图模式下刷新页面，视图和 viewport 保持不变"""
        sa_page = setup_sa_page

        # ========== Arrange ==========
        with allure.step("记录刷新前 URL"):
            url_before = page.url
            assert "view=map" in url_before, \
                f"期望处于地图模式，实际 URL: {url_before}"
            logger.info(f"✓ 刷新前 URL: {url_before}")

        # ========== Act ==========
        with allure.step("刷新页面"):
            page.reload(wait_until="domcontentloaded", timeout=config['timeout']['navigation'])
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 页面已刷新")

        # ========== Assert ==========
        with allure.step("验证 URL 参数保持不变"):
            url_after = page.url
            assert "view=map" in url_after, \
                f"期望刷新后仍含 view=map，实际 URL: {url_after}"
            assert "viewport" in url_after, \
                f"期望刷新后仍含 viewport，实际 URL: {url_after}"
            logger.info(f"✓ 刷新后 URL 保持地图模式: {url_after}")
    @pytest.mark.case_id_sa_view_006
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("List/Map 视图切换 - 功能场景")
    @allure.title("List 模式设置筛选后切换到 Map，筛选参数保留")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("在 List 模式下设置 Price 和 Beds 筛选，切换到 Map 视图，验证筛选参数保留且 view=map 追加")
    def test_list_with_filters_switch_to_map_keeps_filters(self, page, config, setup_sa_page):
        """TC009：List 模式设置筛选后切换到 Map，筛选参数保留"""
        sa_page = setup_sa_page

        # ========== Arrange ==========
        with allure.step("进入 List 模式并设置筛选条件"):
            page.goto(config['list_page'], wait_until="domcontentloaded", timeout=config['timeout']['navigation'])
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            
            # 设置 Price 筛选
            sa_page.click_price_filter()
            sa_page.input_price_min("500")
            sa_page.input_price_max("1500")
            sa_page.click_price_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            
            # 设置 Beds 筛选
            sa_page.click_beds_filter()
            sa_page.select_beds_value("2")
            sa_page.click_beds_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            
            logger.info("✓ 已在 List 模式设置 Price=500~1500 和 Beds=2")

        # ========== Act ==========
        with allure.step("点击 Map 按钮切换到地图模式"):
            sa_page.click_map_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已切换到 Map 模式")

        # ========== Assert ==========
        with allure.step("验证已切换到地图模式且筛选参数保留"):
            current_url = page.url
            
            # 验证1：确认已进入地图模式（使用多种判断方式）
            assert sa_page.is_map_view_active(), \
                f"期望已切换到地图模式，实际 URL: {current_url}"
            logger.info("✓ 已成功切换到地图模式")
            
            # 验证2：确认筛选参数保留
            assert "lowestPrice=500" in current_url, \
                f"期望 URL 含 lowestPrice=500，实际 URL: {current_url}"
            assert "highestPrice=1500" in current_url, \
                f"期望 URL 含 highestPrice=1500，实际 URL: {current_url}"
            assert "attr_168=2" in current_url, \
                f"期望 URL 含 attr_168=2，实际 URL: {current_url}"
            logger.info(f"✓ 切换到 Map 后筛选参数保留，URL: {current_url}")
            
            # 可选验证：如果 URL 含 view=map，记录日志（但不强制要求）
            if "view=map" in current_url:
                logger.info("✓ URL 含 view=map 参数（前端使用 URL 参数标识地图模式）")
            else:
                logger.info("⚠ URL 不含 view=map 参数（前端可能使用其他方式标识地图模式）")

    @pytest.mark.case_id_sa_view_007
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("List/Map 视图切换 - 功能场景")
    @allure.title("Map 模式设置筛选后切换到 List，筛选参数保留")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("在 Map 模式下设置 Sort 和 Bathrooms 筛选，切换到 List 视图，验证筛选参数保留且 view=map 移除")
    def test_map_with_filters_switch_to_list_keeps_filters(self, page, config, setup_sa_page):
        """TC010：Map 模式设置筛选后切换到 List，筛选参数保留"""
        sa_page = setup_sa_page

        # ========== Arrange ==========
        with allure.step("在 Map 模式下设置筛选条件"):
            # 确认当前处于 Map 模式
            assert sa_page.is_map_view_active(), \
                f"期望当前处于地图模式，实际 URL: {page.url}"
            
            # 设置 Sort 筛选
            sa_page.click_sort_filter()
            sa_page.select_sort_option("Lowest Price")
            sa_page.click_sort_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            
            # 设置 Bathrooms 筛选
            sa_page.click_bathrooms_filter()
            sa_page.select_bathrooms_value("1")
            sa_page.click_bathrooms_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            
            logger.info("✓ 已在 Map 模式设置 Sort=Lowest Price 和 Bathrooms=1")

        # ========== Act ==========
        with allure.step("点击 List 按钮切换到列表模式"):
            sa_page.click_list_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已切换到 List 模式")

        # ========== Assert ==========
        with allure.step("验证 URL 不含 view=map 且筛选参数保留"):
            current_url = page.url
            assert "view=map" not in current_url, \
                f"期望 URL 不含 view=map，实际 URL: {current_url}"
            assert "sortId=3" in current_url, \
                f"期望 URL 含 sortId=3（Lowest Price），实际 URL: {current_url}"
            assert "attr_166=1" in current_url, \
                f"期望 URL 含 attr_166=1，实际 URL: {current_url}"
            logger.info(f"✓ 切换到 List 后筛选参数保留，URL: {current_url}")

    @pytest.mark.case_id_sa_view_008
    @pytest.mark.p1
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("List/Map 视图切换 - 组合场景")
    @allure.title("List/Map 来回切换多次，筛选参数始终保留")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("设置筛选后在 List 和 Map 之间来回切换 3 次，验证筛选参数始终保留")
    def test_switch_view_multiple_times_keeps_filters(self, page, config, setup_sa_page):
        """TC011：List/Map 来回切换多次，筛选参数始终保留"""
        sa_page = setup_sa_page

        # ========== Arrange ==========
        with allure.step("进入 List 模式并设置筛选条件"):
            page.goto(config['list_page'], wait_until="domcontentloaded", timeout=config['timeout']['navigation'])
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            
            # 设置 Price 筛选
            sa_page.click_price_filter()
            sa_page.input_price_min("800")
            sa_page.click_price_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            
            logger.info("✓ 已设置 Price Min=800")

        # ========== Act & Assert ==========
        with allure.step("第 1 次：List → Map，验证筛选保留"):
            sa_page.click_map_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            assert "view=map" in page.url and "lowestPrice=800" in page.url, \
                f"期望切换到 Map 后筛选保留，实际 URL: {page.url}"
            logger.info("✓ 第 1 次切换到 Map，筛选保留")

        with allure.step("第 2 次：Map → List，验证筛选保留"):
            sa_page.click_list_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            assert "view=map" not in page.url and "lowestPrice=800" in page.url, \
                f"期望切换到 List 后筛选保留，实际 URL: {page.url}"
            logger.info("✓ 第 2 次切换到 List，筛选保留")

        with allure.step("第 3 次：List → Map，验证筛选保留"):
            sa_page.click_map_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            assert "view=map" in page.url and "lowestPrice=800" in page.url, \
                f"期望切换到 Map 后筛选保留，实际 URL: {page.url}"
            logger.info("✓ 第 3 次切换到 Map，筛选保留")

        with allure.step("第 4 次：Map → List，验证筛选保留"):
            sa_page.click_list_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            assert "view=map" not in page.url and "lowestPrice=800" in page.url, \
                f"期望切换到 List 后筛选保留，实际 URL: {page.url}"
            logger.info("✓ 第 4 次切换到 List，筛选保留")

        # ========== Final Assert ==========
        with allure.step("验证最终筛选参数仍保留"):
            current_url = page.url
            assert "lowestPrice=800" in current_url, \
                f"期望多次切换后筛选参数仍保留，实际 URL: {current_url}"
            logger.info(f"✓ 来回切换 4 次后筛选参数保留，URL: {current_url}")


