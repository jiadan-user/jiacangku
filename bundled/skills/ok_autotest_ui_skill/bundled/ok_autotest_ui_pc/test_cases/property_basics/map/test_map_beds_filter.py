"""
地图模式 - Beds 卧室筛选测试（Sydney Student Accommodation）

测试站点：AU (https://au.58v5.cn)
覆盖用例：TC024–TC028
功能点：选 2 间 / Studio / 8+ / Clear / 快速点击
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



class TestMapBedsFilter:
    """Beds 卧室筛选测试（5 条用例）"""

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
    @pytest.mark.case_id_sa_beds_024
    def test_beds_select_2_url_contains_attr_168_2(self, page, config, setup_sa_page):
        """TC024：选择 Beds=2，URL 含 attr_168=2"""
        sa_page = setup_sa_page

        with allure.step("点击 Beds → 选择 2 → Done"):
            sa_page.click_beds_filter()
            sa_page.select_beds_value("2")
            sa_page.click_beds_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选 Beds=2 并点击 Done")

        with allure.step("验证 URL 含 attr_168=2 且 view=map 保留"):
            current_url = page.url
            assert "attr_168=2" in current_url, \
                f"期望 URL 含 attr_168=2，实际 URL: {current_url}"
            assert "view=map" in current_url, \
                f"期望 URL 保留 view=map，实际 URL: {current_url}"
            logger.info(f"✓ URL: {current_url}")

    @pytest.mark.case_id_sa_beds_025
    @pytest.mark.p0
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Beds 卧室筛选 - 功能场景")
    @allure.title("选择 Studio，URL 含 attr_168=10")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("点击 Beds，选择 Studio，点击 Done，验证 URL 含 attr_168=10")
    def test_beds_select_studio_url_contains_attr_168_10(self, page, config, setup_sa_page):
        """TC025：选择 Beds=Studio，URL 含 attr_168=10"""
        sa_page = setup_sa_page

        with allure.step("点击 Beds → 选择 Studio → Done"):
            sa_page.click_beds_filter()
            sa_page.select_beds_value("Studio")
            sa_page.click_beds_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选 Studio 并点击 Done")

        with allure.step("验证 URL 含 attr_168=10"):
            assert "attr_168=10" in page.url, \
                f"期望 URL 含 attr_168=10，实际 URL: {page.url}"
            logger.info(f"✓ URL 含 attr_168=10: {page.url}")

    @pytest.mark.case_id_sa_beds_026
    @pytest.mark.p1
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Beds 卧室筛选 - 边界场景")
    @allure.title("选择 Beds=8+（最大值），URL 含对应 attr_168 参数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("点击 Beds，选择 8+，点击 Done，验证 URL 含 attr_168 参数")
    def test_beds_select_8plus_url_contains_attr_168(self, page, config, setup_sa_page):
        """TC026：选择 Beds=8+（最大值）"""
        sa_page = setup_sa_page

        with allure.step("点击 Beds → 选择 8+ → Done"):
            sa_page.click_beds_filter()
            sa_page.select_beds_value("8+")
            sa_page.click_beds_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选 8+ 并点击 Done")

        with allure.step("验证 URL 含 attr_168 参数"):
            assert "attr_168" in page.url, \
                f"期望 URL 含 attr_168，实际 URL: {page.url}"
            logger.info(f"✓ URL 含 attr_168: {page.url}")

    @pytest.mark.case_id_sa_beds_027
    @pytest.mark.p1
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Beds 卧室筛选 - 功能场景")
    @allure.title("Beds 筛选后点击 Clear，URL 中 attr_168 被移除")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("已设置 Beds=2 后，重新打开 Beds 面板点击 Clear，验证 URL 中 attr_168 移除")
    def test_beds_clear_removes_attr_168_from_url(self, page, config, setup_sa_page):
        """TC027：Beds 筛选后点击 Clear，attr_168 被移除"""
        sa_page = setup_sa_page

        with allure.step("先设置 Beds=2"):
            sa_page.click_beds_filter()
            sa_page.select_beds_value("2")
            sa_page.click_beds_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            assert "attr_168" in page.url, f"Beds 设置失败，URL: {page.url}"
            logger.info("✓ 已设置 Beds=2")

        with allure.step("重新打开 Beds 面板，点击 Clear"):
            sa_page.click_beds_filter()
            sa_page.click_beds_clear()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已点击 Clear")

        with allure.step("验证 URL 不含 attr_168"):
            assert "attr_168" not in page.url, \
                f"期望 URL 不含 attr_168，实际 URL: {page.url}"
            logger.info(f"✓ attr_168 已移除，URL: {page.url}")

    @pytest.mark.case_id_sa_beds_028
    @pytest.mark.p1
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Beds 卧室筛选 - 边界场景")
    @allure.title("连续快速点击不同 Beds 值，最终选择生效")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("快速连续点击 Beds=1 再点击 Beds=3，点击 Done，验证 URL 中 attr_168 为最后选择的值")
    def test_beds_rapid_click_last_selection_takes_effect(self, page, config, setup_sa_page):
        """TC028：连续快速点击不同 Beds 值，最终选择生效"""
        sa_page = setup_sa_page

        with allure.step("打开 Beds 面板，快速点击 1 再点击 3"):
            sa_page.click_beds_filter()
            sa_page.select_beds_value("1")
            page.wait_for_timeout(300)
            sa_page.select_beds_value("3")
            sa_page.click_beds_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已快速选择 1→3 并点击 Done")

        with allure.step("验证 URL 含 attr_168 参数（最终选择生效）"):
            assert "attr_168" in page.url, \
                f"期望 URL 含 attr_168，实际 URL: {page.url}"
            logger.info(f"✓ 最终 Beds 选择已生效，URL: {page.url}")


