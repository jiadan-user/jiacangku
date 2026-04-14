"""
地图模式 - Sort 排序筛选测试（Sydney Student Accommodation）

测试站点：AU (https://au.58v5.cn)
覆盖用例：TC009–TC015
功能点：默认 Best Match / Newest First / Lowest Price / Highest Price / Clear / 切换视图保留
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



class TestMapSort:
    """Sort 排序测试（6 条用例）"""

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
    @pytest.mark.case_id_sa_sort_009
    def test_sort_default_best_match_no_sort_id(self, page, config, setup_sa_page):
        """TC009：默认排序为 Best Match，URL 不含 sortId"""
        sa_page = setup_sa_page

        # ========== Act ==========
        with allure.step("观察排序按钮初始状态并检查 URL"):
            is_best_match = sa_page.verify_default_sort_is_best_match()
            current_url = page.url
            logger.info(f"✓ 当前排序文案: {sa_page.get_current_sort_text()}")

        # ========== Assert ==========
        with allure.step("验证排序按钮显示 Best Match"):
            assert is_best_match, "期望排序按钮默认显示 'Best Match'"
            logger.info("✓ 排序按钮默认显示 Best Match")

        with allure.step("验证 URL 不含 sortId"):
            assert "sortId" not in current_url, \
                f"期望 URL 不含 sortId，实际 URL: {current_url}"
            logger.info(f"✓ URL 不含 sortId: {current_url}")

    @pytest.mark.case_id_sa_sort_010
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Sort 排序 - 功能场景")
    @allure.title("选择 Newest First 后点击 Done，URL 含 sortId=1 且地图参数保留")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("点击排序按钮，选择 Newest First，点击 Done，验证 URL 含 sortId=1 且 view=map 保留")
    def test_sort_select_newest_first_url_contains_sort_id_1(self, page, config, setup_sa_page):
        """TC010：选择 Newest First 后点击 Done"""
        sa_page = setup_sa_page

        # ========== Act ==========
        with allure.step("点击排序按钮 → 选择 Newest First → Done"):
            sa_page.click_sort_filter()
            sa_page.select_sort_option("Newest First")
            sa_page.click_sort_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选 Newest First 并点击 Done")

        # ========== Assert ==========
        with allure.step("验证 URL 含 sortId=1"):
            assert "sortId=1" in page.url, \
                f"期望 URL 含 sortId=1，实际 URL: {page.url}"
            logger.info(f"✓ URL 含 sortId=1: {page.url}")

        with allure.step("验证地图参数保留"):
            assert "view=map" in page.url, \
                f"期望 URL 保留 view=map，实际 URL: {page.url}"
            logger.info("✓ view=map 参数已保留")

        with allure.step("验证排序按钮文案为 Newest First"):
            sort_text = sa_page.get_current_sort_text()
            assert sort_text == "Newest First", \
                f"期望排序按钮显示 'Newest First'，实际: '{sort_text}'"
            logger.info(f"✓ 排序按钮文案: {sort_text}")

    @pytest.mark.case_id_sa_sort_011
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Sort 排序 - 功能场景")
    @allure.title("选择 Lowest Price 后点击 Done，URL 含 sortId=3")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("点击排序按钮，选择 Lowest Price，点击 Done，验证 URL 含 sortId=3")
    def test_sort_select_lowest_price_url_contains_sort_id_3(self, page, config, setup_sa_page):
        """TC011：选择 Lowest Price 后点击 Done"""
        sa_page = setup_sa_page

        with allure.step("点击排序按钮 → 选择 Lowest Price → Done"):
            sa_page.click_sort_filter()
            sa_page.select_sort_option("Lowest Price")
            sa_page.click_sort_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选 Lowest Price 并点击 Done")

        with allure.step("验证 URL 含 sortId=3 且 view=map 保留"):
            assert "sortId=3" in page.url, \
                f"期望 URL 含 sortId=3，实际 URL: {page.url}"
            assert "view=map" in page.url, \
                f"期望 URL 保留 view=map，实际 URL: {page.url}"
            logger.info(f"✓ URL: {page.url}")

        with allure.step("验证排序按钮文案为 Lowest Price"):
            sort_text = sa_page.get_current_sort_text()
            assert sort_text == "Lowest Price", \
                f"期望显示 'Lowest Price'，实际: '{sort_text}'"
            logger.info(f"✓ 排序文案: {sort_text}")

    @pytest.mark.case_id_sa_sort_013
    @pytest.mark.p1
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Sort 排序 - 组合场景")
    @allure.title("排序后切换到 List 视图，sortId 参数保留")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("在地图模式下设置排序为 Lowest Price，然后切换到 List 视图，验证 sortId=3 保留")
    def test_sort_after_switch_to_list_sort_id_preserved(self, page, config, setup_sa_page):
        """TC013：排序后切换到 List 视图，sortId 参数保留"""
        sa_page = setup_sa_page

        with allure.step("设置排序为 Lowest Price"):
            sa_page.click_sort_filter()
            sa_page.select_sort_option("Lowest Price")
            sa_page.click_sort_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            assert "sortId=3" in page.url, f"排序设置失败，URL: {page.url}"
            logger.info("✓ 已设置 Lowest Price 排序")

        with allure.step("切换到 List 视图"):
            sa_page.click_list_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已切换到 List 视图")

        with allure.step("验证 sortId=3 保留，view=map 被移除"):
            current_url = page.url
            assert "sortId=3" in current_url, \
                f"期望 sortId=3 保留，实际 URL: {current_url}"
            assert "view=map" not in current_url, \
                f"期望 view=map 被移除，实际 URL: {current_url}"
            logger.info(f"✓ List 视图 URL 含 sortId=3: {current_url}")

    @pytest.mark.case_id_sa_sort_014
    @pytest.mark.p2
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Sort 排序 - 边界场景")
    @allure.title("打开排序面板不选项直接 Done，排序和 URL 不变")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("打开排序面板不选任何选项直接点击 Done，验证 URL 无非默认 sortId（允许 sortId=0）")
    def test_sort_open_panel_no_selection_done_url_unchanged(self, page, config, setup_sa_page):
        """TC014：打开排序面板不选任何项直接 Done，排序不变"""
        sa_page = setup_sa_page

        with allure.step("记录操作前 URL"):
            url_before = page.url
            logger.info(f"✓ 操作前 URL: {url_before}")

        with allure.step("打开排序面板，不选择，直接点击 Done"):
            sa_page.click_sort_filter()
            sa_page.click_sort_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已打开排序面板并直接 Done")

        with allure.step("验证 URL 无非默认 sortId（允许 sortId=0）"):
            current_url = page.url
            sort_match = _re.search(r'sortId=(\d+)', current_url)
            assert not sort_match or sort_match.group(1) == '0', \
                f"期望 URL 无非默认 sortId，实际 URL: {current_url}"
            logger.info(f"✓ URL 验证通过: {current_url}")

        with allure.step("验证排序仍为 Best Match"):
            assert sa_page.verify_default_sort_is_best_match(), \
                "期望排序保持 'Best Match'"
            logger.info("✓ 排序仍为 Best Match")

    @pytest.mark.case_id_sa_sort_015
    @pytest.mark.p1
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Sort 排序 - 功能场景")
    @allure.title("已选排序后重新选择 Best Match，URL 中 sortId 被移除")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("已选 Newest First 后，重新打开排序面板选 Best Match，验证 URL 不含 sortId")
    def test_sort_reselect_best_match_removes_sort_id(self, page, config, setup_sa_page):
        """TC015：已选排序后重新选择 Best Match 恢复默认"""
        sa_page = setup_sa_page

        with allure.step("先选择 Newest First"):
            sa_page.click_sort_filter()
            sa_page.select_sort_option("Newest First")
            sa_page.click_sort_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            assert "sortId=1" in page.url, f"Newest First 设置失败，URL: {page.url}"
            logger.info("✓ 已设置 Newest First")

        with allure.step("重新打开排序面板选 Best Match → Done"):
            sa_page.click_sort_filter()
            sa_page.select_sort_option("Best Match")
            sa_page.click_sort_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已重新选择 Best Match")

        with allure.step("验证 URL 不含非默认 sortId"):
            current_url = page.url
            sort_match = _re.search(r'sortId=(\d+)', current_url)
            assert not sort_match or sort_match.group(1) == '0', \
                f"期望 URL 不含非默认 sortId，实际 URL: {current_url}"
            logger.info(f"✓ URL 不含 sortId: {current_url}")

        with allure.step("验证排序按钮恢复 Best Match"):
            assert sa_page.verify_default_sort_is_best_match(), \
                "期望排序恢复 'Best Match'"
            logger.info("✓ 排序已恢复 Best Match")


