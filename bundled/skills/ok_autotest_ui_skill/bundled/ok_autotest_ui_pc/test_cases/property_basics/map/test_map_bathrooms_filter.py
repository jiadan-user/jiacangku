"""
地图模式 - Bathrooms 浴室筛选测试（Sydney Student Accommodation）

测试站点：AU (https://au.58v5.cn)
覆盖用例：TC029–TC033
功能点：选 1 / Shared / 1.5 / 5+ / Clear
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



class TestMapBathroomsFilter:
    """Bathrooms 浴室筛选测试（5 条用例）"""

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
    @pytest.mark.case_id_sa_bath_029
    def test_bathrooms_select_1_url_contains_attr_166_1(self, page, config, setup_sa_page):
        """TC029：选择 Bathrooms=1，URL 含 attr_166=1"""
        sa_page = setup_sa_page

        with allure.step("点击 Bathrooms → 选择 1 → Done"):
            sa_page.click_bathrooms_filter()
            sa_page.select_bathrooms_value("1")
            sa_page.click_bathrooms_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选 Bathrooms=1 并点击 Done")

        with allure.step("验证 URL 含 attr_166=1 且 view=map 保留"):
            current_url = page.url
            assert "attr_166=1" in current_url, \
                f"期望 URL 含 attr_166=1，实际 URL: {current_url}"
            assert "view=map" in current_url, \
                f"期望 URL 保留 view=map，实际 URL: {current_url}"
            logger.info(f"✓ URL: {current_url}")

    @pytest.mark.case_id_sa_bath_030
    @pytest.mark.p0
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Bathrooms 浴室筛选 - 功能场景")
    @allure.title("选择 Shared，URL 含 attr_166=11")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("点击 Bathrooms，选择 Shared，点击 Done，验证 URL 含 attr_166=11")
    def test_bathrooms_select_shared_url_contains_attr_166_11(self, page, config, setup_sa_page):
        """TC030：选择 Bathrooms=Shared，URL 含 attr_166=11"""
        sa_page = setup_sa_page

        with allure.step("点击 Bathrooms → 选择 Shared → Done"):
            sa_page.click_bathrooms_filter()
            sa_page.select_bathrooms_value("Shared")
            sa_page.click_bathrooms_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选 Shared 并点击 Done")

        with allure.step("验证 URL 含 attr_166=11"):
            assert "attr_166=11" in page.url, \
                f"期望 URL 含 attr_166=11，实际 URL: {page.url}"
            logger.info(f"✓ URL 含 attr_166=11: {page.url}")

    @pytest.mark.case_id_sa_bath_031
    @pytest.mark.p1
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Bathrooms 浴室筛选 - 功能场景")
    @allure.title("选择 Bathrooms=1.5（半值），URL 含对应 attr_166 枚举值")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("点击 Bathrooms，选择 1.5，点击 Done，验证 URL 含 attr_166 参数")
    def test_bathrooms_select_1_5_url_contains_attr_166(self, page, config, setup_sa_page):
        """TC031：选择 Bathrooms=1.5（半值）"""
        sa_page = setup_sa_page

        with allure.step("点击 Bathrooms → 选择 1.5 → Done"):
            sa_page.click_bathrooms_filter()
            sa_page.select_bathrooms_value("1.5")
            sa_page.click_bathrooms_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选 1.5 并点击 Done")

        with allure.step("验证 URL 含 attr_166 参数"):
            assert "attr_166" in page.url, \
                f"期望 URL 含 attr_166，实际 URL: {page.url}"
            logger.info(f"✓ URL 含 attr_166: {page.url}")

    @pytest.mark.case_id_sa_bath_032
    @pytest.mark.p1
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Bathrooms 浴室筛选 - 边界场景")
    @allure.title("选择 Bathrooms=5+（最大值），URL 含对应参数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("点击 Bathrooms，选择 5+，点击 Done，验证 URL 含 attr_166 参数")
    def test_bathrooms_select_5plus_url_contains_attr_166(self, page, config, setup_sa_page):
        """TC032：选择 Bathrooms=5+（最大值）"""
        sa_page = setup_sa_page

        with allure.step("点击 Bathrooms → 选择 5+ → Done"):
            sa_page.click_bathrooms_filter()
            sa_page.select_bathrooms_value("5+")
            sa_page.click_bathrooms_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选 5+ 并点击 Done")

        with allure.step("验证 URL 含 attr_166 参数"):
            assert "attr_166" in page.url, \
                f"期望 URL 含 attr_166，实际 URL: {page.url}"
            logger.info(f"✓ URL 含 attr_166: {page.url}")

    @pytest.mark.case_id_sa_bath_033
    @pytest.mark.p1
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Bathrooms 浴室筛选 - 功能场景")
    @allure.title("Bathrooms 筛选后点击 Clear，URL 中 attr_166 被移除")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("已设置 Bathrooms=1 后，重新打开 Bathrooms 面板点击 Clear，验证 URL 中 attr_166 移除")
    def test_bathrooms_clear_removes_attr_166_from_url(self, page, config, setup_sa_page):
        """TC033：Bathrooms 筛选后点击 Clear，attr_166 被移除"""
        sa_page = setup_sa_page

        with allure.step("先设置 Bathrooms=1"):
            sa_page.click_bathrooms_filter()
            sa_page.select_bathrooms_value("1")
            sa_page.click_bathrooms_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            assert "attr_166" in page.url, f"Bathrooms 设置失败，URL: {page.url}"
            logger.info("✓ 已设置 Bathrooms=1")

        with allure.step("重新打开 Bathrooms 面板，点击 Clear"):
            sa_page.click_bathrooms_filter()
            sa_page.click_bathrooms_clear()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已点击 Clear")

        with allure.step("验证 URL 不含 attr_166"):
            assert "attr_166" not in page.url, \
                f"期望 URL 不含 attr_166，实际 URL: {page.url}"
            logger.info(f"✓ attr_166 已移除，URL: {page.url}")


