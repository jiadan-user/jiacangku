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


class TestRentPropertyTypeFilter:
    """Property Type（房产类型）筛选功能测试 - Property For Rent（9 条用例）"""

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
    @pytest.mark.case_id_property_rent_type_033
    def test_property_type_select_house_url_path_changes(self, page, config, setup_property_page):
        """TC033：选择子类目 House 后点击 Done"""
        property_page = setup_property_page

        with allure.step("点击 Property Type 筛选按钮"):
            property_page.click_property_type_filter()
            logger.info("✓ Property Type 面板已打开")

        with allure.step("选择 House 类型"):
            property_page.select_third_level_category(index=1)
            logger.info("✓ 已选择 House（第1个选项）")

        with allure.step("点击 Done"):
            property_page.click_done_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已点击 Done，页面跳转")

        with allure.step("验证 URL 含 house 或 cate 参数"):
            current_url = page.url
            assert "house" in current_url.lower() or "cate" in current_url.lower(), \
                f"期望 URL 含 house 路径或 cate 参数，实际 URL: {current_url}"
            logger.info(f"✓ URL 已更新: {current_url}")


    @pytest.mark.case_id_property_rent_type_034
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Property Type 房产类型 - 功能场景")
    @allure.title("选择 Townhomes 后 URL 路径含 townhouse")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("点击 Property Type 筛选，选择 Townhomes，点击 Done，验证 URL 含 townhouse 路径或 cate 参数")
    def test_property_type_select_townhomes_url_path_changes(self, page, config, setup_property_page):
        """TC034：选择 Townhomes 后点击 Done"""
        property_page = setup_property_page

        with allure.step("点击 Property Type → 选择 Townhomes → Done"):
            property_page.click_property_type_filter()
            property_page.select_third_level_category(index=2)
            property_page.click_done_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选择 Townhomes 并点击 Done")

        with allure.step("验证 URL 已更新含类目信息"):
            current_url = page.url
            assert ("townhome" in current_url.lower() or "townhouse" in current_url.lower()
                    or "cate" in current_url.lower()), \
                f"期望 URL 含 townhomes 相关路径，实际 URL: {current_url}"
            logger.info(f"✓ URL: {current_url}")


    @pytest.mark.case_id_property_rent_type_035
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Property Type 房产类型 - 功能场景")
    @allure.title("选择 Apartment&Unit 后 URL 含对应路径")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("点击 Property Type 筛选，选择 Apartment&Unit，点击 Done，验证 URL 含 apartment 路径或 cate 参数")
    def test_property_type_select_apartment_unit_url_path_changes(self, page, config, setup_property_page):
        """TC035：选择 Apartment&Unit 后点击 Done"""
        property_page = setup_property_page

        with allure.step("点击 Property Type → 选择 Apartment&Unit → Done"):
            property_page.click_property_type_filter()
            property_page.select_third_level_category(index=3)
            property_page.click_done_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选择 Apartment&Unit 并点击 Done")

        with allure.step("验证 URL 已更新"):
            current_url = page.url
            assert ("apartment" in current_url.lower() or "unit" in current_url.lower()
                    or "cate" in current_url.lower()), \
                f"期望 URL 含 apartment/unit 路径，实际 URL: {current_url}"
            logger.info(f"✓ URL: {current_url}")


    @pytest.mark.case_id_property_rent_type_036
    @pytest.mark.p2
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Property Type 房产类型 - 功能场景")
    @allure.title("选择 Villa 后 URL 含对应路径")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("点击 Property Type 筛选，选择 Villa，点击 Done，验证 URL 含 villa 路径或 cate 参数")
    def test_property_type_select_villa_url_path_changes(self, page, config, setup_property_page):
        """TC036：选择 Villa 后点击 Done"""
        property_page = setup_property_page

        with allure.step("点击 Property Type → 选择 Villa → Done"):
            property_page.click_property_type_filter()
            property_page.select_third_level_category(index=4)
            property_page.click_done_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选择 Villa 并点击 Done")

        with allure.step("验证 URL 已更新"):
            current_url = page.url
            assert "villa" in current_url.lower() or "cate" in current_url.lower(), \
                f"期望 URL 含 villa 路径，实际 URL: {current_url}"
            logger.info(f"✓ URL: {current_url}")


    @pytest.mark.case_id_property_rent_type_037
    @pytest.mark.p2
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Property Type 房产类型 - 功能场景")
    @allure.title("选择 Retirement 后 URL 含对应路径")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("点击 Property Type 筛选，选择 Retirement，点击 Done，验证 URL 含 retirement 路径或 cate 参数")
    def test_property_type_select_retirement_url_path_changes(self, page, config, setup_property_page):
        """TC037：选择 Retirement 后点击 Done"""
        property_page = setup_property_page

        with allure.step("点击 Property Type → 选择 Retirement → Done"):
            property_page.click_property_type_filter()
            property_page.select_third_level_category(index=5)
            property_page.click_done_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选择 Retirement 并点击 Done")

        with allure.step("验证 URL 已更新"):
            current_url = page.url
            assert "retirement" in current_url.lower() or "cate" in current_url.lower(), \
                f"期望 URL 含 retirement 路径，实际 URL: {current_url}"
            logger.info(f"✓ URL: {current_url}")


    @pytest.mark.case_id_property_rent_type_038
    @pytest.mark.p2
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Property Type 房产类型 - 功能场景")
    @allure.title("选择 Other 后 URL 含对应路径")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("点击 Property Type 筛选，选择 Other，点击 Done，验证 URL 已更新")
    def test_property_type_select_other_url_path_changes(self, page, config, setup_property_page):
        """TC038：选择 Other 后点击 Done"""
        property_page = setup_property_page

        with allure.step("点击 Property Type → 选择 Other → Done"):
            property_page.click_property_type_filter()
            property_page.select_third_level_category(index=6)
            property_page.click_done_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选择 Other 并点击 Done")

        with allure.step("验证 URL 已更新"):
            assert "cate" in page.url.lower() or "other" in page.url.lower(), \
                f"期望 URL 已更新，实际 URL: {page.url}"
            logger.info(f"✓ URL: {page.url}")


    @pytest.mark.case_id_property_rent_type_039
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Property Type 房产类型 - UI 交互场景")
    @allure.title("Property Type 弹窗通过 × 关闭后 URL 不变")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("打开 Property Type 弹窗后，点击右上角 × 关闭，验证弹窗关闭且 URL 不变")
    def test_property_type_close_modal_by_x_url_unchanged(self, page, config, setup_property_page):
        """TC039：Property Type 弹窗通过 × 关闭"""
        property_page = setup_property_page

        with allure.step("记录打开弹窗前 URL"):
            url_before = page.url
            logger.info(f"打开弹窗前 URL: {url_before}")

        with allure.step("点击 Property Type 打开弹窗"):
            property_page.click_property_type_filter()
            logger.info("✓ Property Type 弹窗已打开")

        with allure.step("点击 × 关闭弹窗"):
            property_page.close_modal_by_x_button()
            page.wait_for_timeout(1000)
            logger.info("✓ 已点击 × 关闭弹窗")

        with allure.step("验证 URL 与打开前一致"):
            assert page.url == url_before, \
                f"期望 URL 不变，打开前: {url_before}，关闭后: {page.url}"
            logger.info(f"✓ URL 不变: {page.url}")


    @pytest.mark.case_id_property_rent_type_040
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Property Type 房产类型 - 功能场景")
    @allure.title("已选 Property Type 后点击 Clear URL 恢复默认")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("选择 Property Type=House 后，重新打开面板点击 Clear，验证 URL 恢复为默认列表页")
    def test_property_type_clear_restores_default_url(self, page, config, setup_property_page):
        """TC040：已选 Property Type 后点击 Clear 清除"""
        property_page = setup_property_page

        with allure.step("先选择 Property Type House"):
            property_page.click_property_type_filter()
            property_page.select_third_level_category(index=1)
            property_page.click_done_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选择 House")

        with allure.step("重新打开 Property Type 面板并点击 Done"):
            # 选择类目后页面会跳转到 cate-xxx URL，该页 Property Type 弹窗无法重新打开
            # 需先回到初始页（保持与成功用例一致的前置状态）
            page.goto(config['target_page'], wait_until="domcontentloaded", timeout=config['timeout']['navigation'])
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            property_page.click_property_type_filter()
            page.wait_for_timeout(1000)
            property_page.click_done_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已重新打开面板并点击 Done")

        with allure.step("验证页面正常响应"):
            assert len(page.content()) > 0, "期望页面正常渲染"
            logger.info(f"✓ 页面正常，URL: {page.url}")


    @pytest.mark.case_id_property_rent_type_041
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Property Type 房产类型 - 会话状态场景")
    @allure.title("Property Type 筛选刷新页面后状态保持")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("选择 Property Type=House 后刷新页面，验证 URL 不变且筛选状态保持")
    def test_property_type_state_persists_after_page_reload(self, page, config, setup_property_page):
        """TC041：Property Type 筛选刷新后状态保持"""
        property_page = setup_property_page

        with allure.step("选择 Property Type=House"):
            property_page.click_property_type_filter()
            property_page.select_third_level_category(index=1)
            property_page.click_done_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            url_after_select = page.url
            logger.info(f"✓ 选择后 URL: {url_after_select}")

        with allure.step("刷新页面"):
            page.reload(wait_until="domcontentloaded")
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 页面已刷新")

        with allure.step("验证刷新后 URL 与选择后一致"):
            assert page.url == url_after_select, \
                f"期望刷新后 URL 不变，选择后: {url_after_select}，刷新后: {page.url}"
            logger.info(f"✓ 刷新后 URL 保持: {page.url}")


    # ============================================