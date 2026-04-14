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


class TestRentSort:
    """Sort（排序）筛选功能测试 - Property For Rent（8 条用例）"""

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
    @pytest.mark.p2
    @pytest.mark.case_id_property_rent_sort_001
    def test_sort_default_best_match_no_sort_id_in_url(self, page, config, setup_property_page):
        """TC001：默认排序为 Best Match"""
        property_page = setup_property_page

        # ========== Act ==========
        with allure.step("观察排序按钮初始状态"):
            is_best_match = property_page.verify_default_sort_is_best_match()
            logger.info(f"✓ 验证默认排序是否为 Best Match: {is_best_match}")

        # ========== Assert ==========
        with allure.step("验证排序按钮显示 Best Match"):
            assert is_best_match, "期望排序按钮显示文案为 'Best Match'"
            logger.info("✓ 排序按钮默认显示 Best Match")

        with allure.step("验证 URL 不含 sortId 参数"):
            current_url = page.url
            assert "sortId" not in current_url, \
                f"期望 URL 不含 sortId 参数，实际 URL: {current_url}"
            logger.info(f"✓ URL 不含 sortId: {current_url}")


    @pytest.mark.case_id_property_rent_sort_002
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Sort 排序 - 功能场景")
    @allure.title("选择 Newest First 排序后 URL 含 sortId 且按钮文案更新")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("点击排序按钮，选择 Newest First，点击 Done，验证 URL 含 sortId 且排序按钮文案变为 Newest First")
    def test_sort_select_newest_first_url_contains_sort_id(self, page, config, setup_property_page):
        """TC002：选择 Newest First 排序后点击 Done"""
        property_page = setup_property_page

        # ========== Act ==========
        with allure.step("点击排序按钮展开下拉面板"):
            property_page.click_sort_button()
            logger.info("✓ 排序下拉面板已展开")

        with allure.step("选择 Newest First 选项"):
            property_page.select_sort_option("Newest First")
            logger.info("✓ 已选择 Newest First")

        with allure.step("点击 Done 按钮"):
            property_page.click_done_button_in_sort_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已点击 Done，页面已刷新")

        # ========== Assert ==========
        with allure.step("验证 URL 含 sortId 参数"):
            current_url = page.url
            assert "sortId" in current_url, \
                f"期望 URL 含 sortId 参数，实际 URL: {current_url}"
            logger.info(f"✓ URL 含 sortId: {current_url}")

        with allure.step("验证排序按钮文案为 Newest First"):
            sort_text = property_page.get_current_sort_text()
            assert sort_text == "Newest First", \
                f"期望排序按钮显示 'Newest First'，实际显示: '{sort_text}'"
            logger.info(f"✓ 排序按钮文案: {sort_text}")


    @pytest.mark.case_id_property_rent_sort_003
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Sort 排序 - 功能场景")
    @allure.title("选择 Lowest Price 排序后 URL 含 sortId")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("点击排序按钮，选择 Lowest Price，点击 Done，验证 URL 含 sortId 且按钮显示 Lowest Price")
    def test_sort_select_lowest_price_url_contains_sort_id(self, page, config, setup_property_page):
        """TC003：选择 Lowest Price 排序后点击 Done"""
        property_page = setup_property_page

        with allure.step("点击排序按钮 → 选择 Lowest Price → Done"):
            property_page.click_sort_button()
            property_page.select_sort_option("Lowest Price")
            property_page.click_done_button_in_sort_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选择 Lowest Price 并点击 Done")

        with allure.step("验证 URL 含 sortId"):
            assert "sortId" in page.url, \
                f"期望 URL 含 sortId，实际 URL: {page.url}"
            logger.info(f"✓ URL: {page.url}")

        with allure.step("验证排序按钮文案为 Lowest Price"):
            sort_text = property_page.get_current_sort_text()
            assert sort_text == "Lowest Price", \
                f"期望排序按钮显示 'Lowest Price'，实际: '{sort_text}'"
            logger.info(f"✓ 排序文案: {sort_text}")


    @pytest.mark.case_id_property_rent_sort_004
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Sort 排序 - 功能场景")
    @allure.title("选择 Highest Price 排序后 URL 含 sortId")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("点击排序按钮，选择 Highest Price，点击 Done，验证 URL 含 sortId 且按钮显示 Highest Price")
    def test_sort_select_highest_price_url_contains_sort_id(self, page, config, setup_property_page):
        """TC004：选择 Highest Price 排序后点击 Done"""
        property_page = setup_property_page

        with allure.step("点击排序按钮 → 选择 Highest Price → Done"):
            property_page.click_sort_button()
            property_page.select_sort_option("Highest Price")
            property_page.click_done_button_in_sort_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选择 Highest Price 并点击 Done")

        with allure.step("验证 URL 含 sortId"):
            assert "sortId" in page.url, \
                f"期望 URL 含 sortId，实际 URL: {page.url}"
            logger.info(f"✓ URL: {page.url}")

        with allure.step("验证排序按钮文案为 Highest Price"):
            sort_text = property_page.get_current_sort_text()
            assert sort_text == "Highest Price", \
                f"期望排序按钮显示 'Highest Price'，实际: '{sort_text}'"
            logger.info(f"✓ 排序文案: {sort_text}")


    @pytest.mark.case_id_property_rent_sort_005
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Sort 排序 - 功能场景")
    @allure.title("已选排序后点击 Clear 再 Done URL 恢复无 sortId")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("选择 Newest First 后，重新打开排序面板，点击 Clear 再 Done，验证 URL 不含 sortId")
    def test_sort_clear_resets_to_default_no_sort_id(self, page, config, setup_property_page):
        """TC005：已选排序后点击 Clear 再 Done"""
        property_page = setup_property_page

        with allure.step("先选择 Newest First 排序"):
            property_page.click_sort_button()
            property_page.select_sort_option("Newest First")
            property_page.click_done_button_in_sort_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选择 Newest First")

        with allure.step("重新打开排序面板并点击 Clear"):
            property_page.click_sort_button()
            property_page.click_clear_button_in_sort_modal()
            logger.info("✓ 已点击 Clear")

        with allure.step("点击 Done"):
            property_page.click_done_button_in_sort_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已点击 Done，页面刷新")

        with allure.step("验证 URL 不含 sortId"):
            assert "sortId" not in page.url, \
                f"期望 URL 不含 sortId，实际 URL: {page.url}"
            logger.info(f"✓ URL 不含 sortId: {page.url}")

        with allure.step("验证排序按钮恢复 Best Match"):
            assert property_page.verify_default_sort_is_best_match(), \
                "期望排序按钮恢复显示 'Best Match'"
            logger.info("✓ 排序按钮恢复 Best Match")


    @pytest.mark.case_id_property_rent_sort_006
    @pytest.mark.p2
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Sort 排序 - 边界值场景")
    @allure.title("打开排序下拉不选任何项直接点击 Done 排序不变")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("打开排序下拉面板，不选任何选项直接点击 Done，验证 URL 不变且排序仍为 Best Match")
    def test_sort_open_panel_without_selection_click_done_no_change(self, page, config, setup_property_page):
        """TC006：打开排序下拉不选任何项直接点击 Done"""
        property_page = setup_property_page

        with allure.step("记录打开面板前的 URL"):
            url_before = page.url
            logger.info(f"打开面板前 URL: {url_before}")

        with allure.step("打开排序面板，不选择任何项，直接点击 Done"):
            property_page.click_sort_button()
            property_page.click_done_button_in_sort_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 未选择任何项，已点击 Done")

        with allure.step("验证 URL 不含有效 sortId（sortId=0 等同于默认，允许存在）"):
            import re as _re
            sort_match = _re.search(r'sortId=(\d+)', page.url)
            assert not sort_match or sort_match.group(1) == '0', \
                f"期望 URL 不含非默认 sortId，实际 URL: {page.url}"
            logger.info(f"✓ URL 未含非默认 sortId（当前 URL: {page.url}）")

        with allure.step("验证排序仍为 Best Match"):
            assert property_page.verify_default_sort_is_best_match(), \
                "期望排序按钮仍显示 'Best Match'"
            logger.info("✓ 排序仍为 Best Match")


    @pytest.mark.case_id_property_rent_sort_007
    @pytest.mark.p2
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Sort 排序 - UI 交互场景")
    @allure.title("排序下拉展开后点击面板外区域面板关闭")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("点击排序按钮展开下拉面板，点击面板外空白区域，验证面板关闭且排序不变")
    def test_sort_click_outside_closes_panel(self, page, config, setup_property_page):
        """TC007：排序下拉展开后点击面板外区域关闭"""
        property_page = setup_property_page

        with allure.step("点击排序按钮展开下拉面板"):
            property_page.click_sort_button()
            logger.info("✓ 排序面板已展开")

        with allure.step("点击面板外空白区域"):
            property_page.click_page_blank_area()
            page.wait_for_timeout(1000)
            logger.info("✓ 已点击面板外区域")

        with allure.step("验证 URL 不含 sortId（面板关闭未提交）"):
            assert "sortId" not in page.url, \
                f"期望 URL 不含 sortId，实际 URL: {page.url}"
            logger.info(f"✓ 面板关闭，URL 不变: {page.url}")


    @pytest.mark.case_id_property_rent_sort_008
    @pytest.mark.p2
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Sort 排序 - 组合场景")
    @allure.title("选择排序后翻页排序条件保持")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("选择 Newest First 排序后，点击第二页，验证 URL 仍含 sortId 参数")
    def test_sort_persists_after_pagination(self, page, config, setup_property_page):
        """TC008：选择排序后翻页，排序条件保持"""
        property_page = setup_property_page

        with allure.step("选择 Newest First 排序并提交"):
            property_page.click_sort_button()
            property_page.select_sort_option("Newest First")
            property_page.click_done_button_in_sort_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选择 Newest First")

        with allure.step("点击第二页分页按钮"):
            try:
                page.get_by_role("link", name="2").first.click()
                page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
                logger.info("✓ 已跳转到第二页")
            except Exception:
                page.get_by_text("2").first.click()
                page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
                logger.info("✓ 已跳转到第二页（备选定位器）")

        with allure.step("验证翻页后 URL 仍含 sortId"):
            assert "sortId" in page.url, \
                f"期望翻页后 URL 仍含 sortId，实际 URL: {page.url}"
            logger.info(f"✓ 翻页后 sortId 保持: {page.url}")


    # ============================================