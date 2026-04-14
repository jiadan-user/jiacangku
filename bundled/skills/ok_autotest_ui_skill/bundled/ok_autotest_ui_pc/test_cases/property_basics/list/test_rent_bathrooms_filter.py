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


class TestRentBathroomsFilter:
    """Bathrooms（卫生间数量）筛选功能测试 - Property For Rent（7 条用例）"""

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
    @pytest.mark.case_id_property_rent_bath_026
    def test_bathrooms_select_2_url_contains_attr_166(self, page, config, setup_property_page):
        """TC026：选择 Bathrooms = 2 后点击 Done"""
        property_page = setup_property_page

        with allure.step("点击 Bathrooms 筛选按钮"):
            property_page.click_bathrooms_filter()
            logger.info("✓ Bathrooms 筛选面板已打开")

        with allure.step("选择 Bathrooms=2"):
            property_page.select_bathrooms_values("2")
            logger.info("✓ 已选择 Bathrooms=2")

        with allure.step("点击 Done"):
            property_page.click_done_button_in_bathrooms_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已点击 Done")

        with allure.step("验证 URL 含 attr_166 参数"):
            assert "attr_166" in page.url, \
                f"期望 URL 含 attr_166 参数，实际 URL: {page.url}"
            logger.info(f"✓ attr_166 在 URL 中: {page.url}")


    @pytest.mark.case_id_property_rent_bath_027
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Bathrooms 卫生间筛选 - 边界值场景")
    @allure.title("选择 Bathrooms=1 最小值后 URL 含 attr_166 参数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("点击 Bathrooms 筛选，选择 1（最小值），点击 Done，验证 URL 含 attr_166 参数")
    def test_bathrooms_select_1_minimum_url_contains_attr_166(self, page, config, setup_property_page):
        """TC027：选择 Bathrooms = 1（最小值）"""
        property_page = setup_property_page

        with allure.step("点击 Bathrooms → 选择 1 → Done"):
            property_page.click_bathrooms_filter()
            property_page.select_bathrooms_values("1")
            property_page.click_done_button_in_bathrooms_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选择 Bathrooms=1 并点击 Done")

        with allure.step("验证 URL 含 attr_166"):
            assert "attr_166" in page.url, \
                f"期望 URL 含 attr_166，实际 URL: {page.url}"
            logger.info(f"✓ URL: {page.url}")


    @pytest.mark.case_id_property_rent_bath_028
    @pytest.mark.p2
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Bathrooms 卫生间筛选 - 边界值场景")
    @allure.title("选择 Bathrooms=1.5 半整数值后 URL 含 attr_166 参数")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("点击 Bathrooms 筛选，选择 1.5，点击 Done，验证 URL 含 attr_166 参数")
    def test_bathrooms_select_1_5_half_value_url_contains_attr_166(self, page, config, setup_property_page):
        """TC028：选择 Bathrooms = 1.5（半整数值）"""
        property_page = setup_property_page

        with allure.step("点击 Bathrooms → 选择 1.5 → Done"):
            property_page.click_bathrooms_filter()
            property_page.select_bathrooms_values("1.5")
            property_page.click_done_button_in_bathrooms_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选择 Bathrooms=1.5 并点击 Done")

        with allure.step("验证 URL 含 attr_166"):
            assert "attr_166" in page.url, \
                f"期望 URL 含 attr_166，实际 URL: {page.url}"
            logger.info(f"✓ URL: {page.url}")


    @pytest.mark.case_id_property_rent_bath_029
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Bathrooms 卫生间筛选 - 边界值场景")
    @allure.title("选择 Bathrooms=5+ 最大开放值后 URL 含 attr_166 参数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("点击 Bathrooms 筛选，选择 5+（最大开放值），点击 Done，验证 URL 含 attr_166 参数")
    def test_bathrooms_select_5plus_maximum_url_contains_attr_166(self, page, config, setup_property_page):
        """TC029：选择 Bathrooms = 5+（最大开放值）"""
        property_page = setup_property_page

        with allure.step("点击 Bathrooms → 选择 5+ → Done"):
            property_page.click_bathrooms_filter()
            property_page.select_bathrooms_values("5+")
            property_page.click_done_button_in_bathrooms_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选择 Bathrooms=5+ 并点击 Done")

        with allure.step("验证 URL 含 attr_166"):
            assert "attr_166" in page.url, \
                f"期望 URL 含 attr_166，实际 URL: {page.url}"
            logger.info(f"✓ URL: {page.url}")


    @pytest.mark.case_id_property_rent_bath_030
    @pytest.mark.p2
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Bathrooms 卫生间筛选 - 功能场景")
    @allure.title("选择 Shared 选项后 URL 含 attr_166 参数")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("点击 Bathrooms 筛选，选择 Shared，点击 Done，验证 URL 含 attr_166 参数")
    def test_bathrooms_select_shared_url_contains_attr_166(self, page, config, setup_property_page):
        """TC030：选择 Shared 选项"""
        property_page = setup_property_page

        with allure.step("点击 Bathrooms → 选择 Shared → Done"):
            property_page.click_bathrooms_filter()
            property_page.select_bathrooms_values("Shared")
            property_page.click_done_button_in_bathrooms_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选择 Shared 并点击 Done")

        with allure.step("验证 URL 含 attr_166"):
            assert "attr_166" in page.url, \
                f"期望 URL 含 attr_166，实际 URL: {page.url}"
            logger.info(f"✓ URL: {page.url}")


    @pytest.mark.case_id_property_rent_bath_031
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Bathrooms 卫生间筛选 - API参数矩阵")
    @allure.title("Bathrooms 枚举选项 URL 参数映射逐一校验")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("逐一选择 Bathrooms 各枚举值，验证每次选择后 URL 均含 attr_166 参数（枚举映射正确）")
    @pytest.mark.parametrize("bath_value", ["1", "1.5", "2", "2.5", "3", "3.5", "4", "4.5", "5", "5+", "Shared"])
    def test_bathrooms_enum_mapping_url_contains_attr_166(self, page, config, setup_property_page, bath_value):
        """TC031：Bathrooms 所有枚举选项 URL 参数映射校验"""
        property_page = setup_property_page

        with allure.step(f"点击 Bathrooms → 选择 {bath_value} → Done"):
            property_page.click_bathrooms_filter()
            property_page.select_bathrooms_values(bath_value)
            property_page.click_done_button_in_bathrooms_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info(f"✓ 已选择 Bathrooms={bath_value} 并点击 Done")

        with allure.step(f"验证选择 {bath_value} 后 URL 含 attr_166"):
            assert "attr_166" in page.url, \
                f"选择 Bathrooms={bath_value} 后期望 URL 含 attr_166，实际 URL: {page.url}"
            logger.info(f"✓ Bathrooms={bath_value} 映射正确，URL: {page.url}")


    @pytest.mark.case_id_property_rent_bath_032
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Bathrooms 卫生间筛选 - 功能场景")
    @allure.title("已选 Bathrooms 后点击 Clear URL 中 attr_166 参数消失")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("设置 Bathrooms=2 后，重新打开面板点击 Clear，验证 URL 中 attr_166 参数消失")
    def test_bathrooms_clear_removes_attr_166_from_url(self, page, config, setup_property_page):
        """TC032：已选 Bathrooms 后点击 Clear 清除"""
        property_page = setup_property_page

        with allure.step("先设置 Bathrooms=2"):
            property_page.click_bathrooms_filter()
            property_page.select_bathrooms_values("2")
            property_page.click_done_button_in_bathrooms_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Bathrooms=2")

        with allure.step("重新打开 Bathrooms 面板并点击 Clear"):
            property_page.click_bathrooms_filter()
            property_page.click_clear_button_in_bathrooms_modal()
            property_page.click_done_button_in_bathrooms_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已点击 Clear 并 Done")

        with allure.step("验证 URL 不含 attr_166"):
            assert "attr_166" not in page.url, \
                f"期望 URL 不含 attr_166，实际 URL: {page.url}"
            logger.info(f"✓ attr_166 已从 URL 清除: {page.url}")


    # ============================================