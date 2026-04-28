"""
阿联酋站 - 探索列表页（Cars分类）测试 - 模块三：Sort 排序功能

本脚本由 playwright-test-generator 生成
录制文档：/Users/a58/Desktop/测试用例/okcom-探索列表页-测试用例-20260303.md
生成时间：2026-03-04

测试站点：AE (https://ae.58v5.cn)
测试角色：Buyer/游客（无需登录）
测试目标：验证 Sort 排序面板的展开、选项选择、Confirm/Clear、关闭、URL 保留等功能
"""
import pytest
import allure
from pages.explore_list_page import ExploreListPage
from utils.logger import setup_logger

logger = setup_logger()

_CONFIG = {
    "site": "ae",
    "site_name": "阿联酋站",
    "role": "buyer",
    "user_name": "guest_ae",
    "base_url": "https://ae.58v5.cn",
    "test_account": None,
    "target_url": "https://ae.58v5.cn/en/city-abu-dhabi/cate-car/?iconSource=car",
    "locale": "en-AE",
    "currency": "AED",
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


@pytest.mark.case_id_explore_list_tc011
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Sort 排序功能")
@allure.title("点击 Sort 展开排序下拉面板，显示 4 个排序选项")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证点击 Sort 按钮后展开含 4 个排序选项的面板及 Clear/Confirm 按钮")
def test_tc010_sort_panel_opens(page, config):
    """TC011: 点击 Sort 展开排序下拉面板"""

    # ========== Arrange ==========
    list_page = ExploreListPage(page)
    logger.info("TC011: Sort 面板展开")

    # ========== Act ==========
    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        logger.info("✓ 已打开探索列表页")

    with allure.step("步骤2：点击 Sort 按钮"):
        list_page.click_sort()
        logger.info("✓ 已点击 Sort")

    # ========== Assert ==========
    with allure.step("验证排序面板展开，4 个选项可见"):
        assert list_page.is_sort_panel_visible(), \
            "Sort 面板应展开，'Price: Low to High' 选项应可见"

        sort_options = [
            "Price: Low to High",
            "Price: High to Low",
            "Most recent",
            "Lowest Mileage"
        ]
        for opt in sort_options:
            is_vis = page.get_by_text(opt).first.is_visible(timeout=3000)
            assert is_vis, f"Sort 选项 '{opt}' 应可见"

        logger.info("✓ 4 个排序选项均可见")

    with allure.step("验证 Clear 和 Confirm 按钮可见"):
        assert page.get_by_text("Clear", exact=True).first.is_visible(timeout=3000), \
            "Sort 面板的 Clear 按钮应可见"
        assert page.get_by_text("Confirm", exact=True).first.is_visible(timeout=3000), \
            "Sort 面板的 Confirm 按钮应可见"
        logger.info("✓ Clear 和 Confirm 按钮均可见")

    logger.info("✅ TC011 通过")


@pytest.mark.case_id_explore_list_tc012
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Sort 排序功能")
@allure.title("选择 'Price: Low to High' 并点击 Confirm，URL 含排序参数")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证选择价格升序并 Confirm 后，URL 包含 sortId=3，面板关闭")
def test_tc011_sort_price_low_to_high(page, config):
    """TC012: 选择 'Price: Low to High' 并点击 Confirm"""

    # ========== Arrange ==========
    list_page = ExploreListPage(page)
    logger.info("TC012: 选择价格升序排序")

    # ========== Act ==========
    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        logger.info("✓ 已打开探索列表页")

    with allure.step("步骤2：点击 Sort 展开面板"):
        list_page.click_sort()
        logger.info("✓ Sort 面板已展开")

    with allure.step("步骤3：选择 'Price: Low to High'"):
        list_page.select_sort_option("Price: Low to High")
        logger.info("✓ 已选择 Price: Low to High")

    with allure.step("步骤4：点击 Confirm"):
        list_page.click_sort_confirm()
        logger.info("✓ 已点击 Confirm")

    # ========== Assert ==========
    with allure.step("验证 URL 包含排序参数 sortId=3"):
        current_url = list_page.get_current_url()
        assert "sortId=3" in current_url, \
            f"URL 应包含 'sortId=3'，实际: {current_url}"
        logger.info(f"✓ URL 包含 sortId=3: {current_url}")

    with allure.step("验证 Sort 面板已关闭"):
        assert not list_page.is_sort_panel_visible(), \
            "点击 Confirm 后 Sort 面板应关闭"
        logger.info("✓ Sort 面板已关闭")

    logger.info("✅ TC012 通过")


@pytest.mark.case_id_explore_list_tc013
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Sort 排序功能")
@allure.title("选择 'Price: High to Low' 排序，URL 含 sortId=4")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证选择价格降序并 Confirm 后，URL 包含 sortId=4")
def test_tc012_sort_price_high_to_low(page, config):
    """TC013: 选择 'Price: High to Low' 排序"""

    # ========== Arrange ==========
    list_page = ExploreListPage(page)
    logger.info("TC013: 选择价格降序排序")

    # ========== Act ==========
    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])

    with allure.step("步骤2：点击 Sort 并选择 Price: High to Low"):
        list_page.click_sort()
        list_page.select_sort_option("Price: High to Low")
        list_page.click_sort_confirm()
        logger.info("✓ 已选择 Price: High to Low 并确认")

    # ========== Assert ==========
    with allure.step("验证 URL 包含 sortId=4"):
        current_url = list_page.get_current_url()
        assert "sortId=4" in current_url, \
            f"URL 应包含 'sortId=4'，实际: {current_url}"
        logger.info(f"✓ URL 包含 sortId=4: {current_url}")

    logger.info("✅ TC013 通过")


@pytest.mark.case_id_explore_list_tc014
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Sort 排序功能")
@allure.title("选择 'Most recent' 排序，URL 含 sortId=1")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证选择最新发布排序并 Confirm 后，URL 包含 sortId=1")
def test_tc013_sort_most_recent(page, config):
    """TC014: 选择 'Most recent' 排序"""

    # ========== Arrange ==========
    list_page = ExploreListPage(page)
    logger.info("TC014: 选择最新排序")

    # ========== Act ==========
    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])

    with allure.step("步骤2：点击 Sort 并选择 Most recent"):
        list_page.click_sort()
        list_page.select_sort_option("Most recent")
        list_page.click_sort_confirm()
        logger.info("✓ 已选择 Most recent 并确认")

    # ========== Assert ==========
    with allure.step("验证 URL 包含 sortId=1"):
        current_url = list_page.get_current_url()
        assert "sortId=1" in current_url, \
            f"URL 应包含 'sortId=1'，实际: {current_url}"
        logger.info(f"✓ URL 包含 sortId=1: {current_url}")

    logger.info("✅ TC014 通过")


@pytest.mark.case_id_explore_list_tc015
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Sort 排序功能")
@allure.title("选择 'Lowest Mileage' 排序，URL 含 sortId=5")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证选择最低里程排序并 Confirm 后，URL 包含 sortId=5")
def test_tc014_sort_lowest_mileage(page, config):
    """TC015: 选择 'Lowest Mileage' 排序"""

    # ========== Arrange ==========
    list_page = ExploreListPage(page)
    logger.info("TC015: 选择最低里程排序")

    # ========== Act ==========
    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])

    with allure.step("步骤2：点击 Sort 并选择 Lowest Mileage"):
        list_page.click_sort()
        list_page.select_sort_option("Lowest Mileage")
        list_page.click_sort_confirm()
        logger.info("✓ 已选择 Lowest Mileage 并确认")

    # ========== Assert ==========
    with allure.step("验证 URL 包含 sortId=5"):
        current_url = list_page.get_current_url()
        assert "sortId=5" in current_url, \
            f"URL 应包含 'sortId=5'，实际: {current_url}"
        logger.info(f"✓ URL 包含 sortId=5: {current_url}")

    logger.info("✅ TC015 通过")


@pytest.mark.case_id_explore_list_tc016
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Sort 排序功能")
@allure.title("Sort 面板选择选项后点击 Clear，取消勾选，面板不关闭")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证 Sort 面板点击 Clear 后已选选项取消勾选，面板保持展开")
def test_tc015_sort_clear_button(page, config):
    """TC016: 点击 Sort 面板的 Clear 按钮"""

    # ========== Arrange ==========
    list_page = ExploreListPage(page)
    logger.info("TC016: Sort Clear 按钮")

    # ========== Act ==========
    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])

    with allure.step("步骤2：打开 Sort，选择 Price: Low to High"):
        list_page.click_sort()
        list_page.select_sort_option("Price: Low to High")
        logger.info("✓ 已选择排序选项")

    with allure.step("步骤3：点击 Clear"):
        list_page.click_sort_clear()
        logger.info("✓ 已点击 Clear")

    # ========== Assert ==========
    with allure.step("验证 Sort 面板仍展开（Clear 不关闭面板）"):
        assert list_page.is_sort_panel_visible(), \
            "点击 Clear 后 Sort 面板应保持展开"
        logger.info("✓ Sort 面板保持展开")

    with allure.step("验证 URL 不含排序参数（Clear 不触发排序）"):
        current_url = list_page.get_current_url()
        assert "sortId" not in current_url, \
            f"Clear 后 URL 不应含 sortId，实际: {current_url}"
        logger.info("✓ URL 无 sortId 参数")

    logger.info("✅ TC016 通过")


@pytest.mark.case_id_explore_list_tc017
@pytest.mark.p2
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Sort 排序功能")
@allure.title("Sort 面板不选任何选项直接 Confirm，URL 不含排序参数")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证 Sort 面板不选任何排序选项直接 Confirm，列表保持默认排序")
def test_tc016_sort_confirm_without_selection(page, config):
    """TC017: Sort 面板不选任何选项直接 Confirm"""

    # ========== Arrange ==========
    list_page = ExploreListPage(page)
    logger.info("TC017: Sort 无选择直接 Confirm")

    # ========== Act ==========
    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])

    with allure.step("步骤2：打开 Sort，不选任何选项直接 Confirm"):
        list_page.click_sort()
        list_page.click_sort_confirm()
        logger.info("✓ 未选任何选项，直接 Confirm")

    # ========== Assert ==========
    with allure.step("验证 URL 不含 sortId 参数"):
        current_url = list_page.get_current_url()
        assert "sortId" not in current_url, \
            f"不选排序选项 Confirm 后，URL 不应含 sortId，实际: {current_url}"
        logger.info(f"✓ URL 无 sortId: {current_url}")

    logger.info("✅ TC017 通过")


@pytest.mark.case_id_explore_list_tc018
@pytest.mark.p2
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Sort 排序功能")
@allure.title("Sort 面板展开后按 Escape 关闭")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证 Sort 面板展开后按 Escape 键可关闭面板")
def test_tc017_sort_close_by_escape(page, config):
    """TC018: 排序后按 ESC 键关闭下拉"""

    # ========== Arrange ==========
    list_page = ExploreListPage(page)
    logger.info("TC018: Sort 面板 ESC 关闭")

    # ========== Act ==========
    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])

    with allure.step("步骤2：打开 Sort 面板"):
        list_page.click_sort()
        assert list_page.is_sort_panel_visible(), "Sort 面板应已展开"
        logger.info("✓ Sort 面板已展开")

    with allure.step("步骤3：按 Escape 关闭面板"):
        list_page.close_sort_panel_by_escape()
        logger.info("✓ 已按 Escape")

    # ========== Assert ==========
    with allure.step("验证 Sort 面板已关闭"):
        assert not list_page.is_sort_panel_visible(), \
            "按 Escape 后 Sort 面板应关闭"
        logger.info("✓ Sort 面板已关闭")

    logger.info("✅ TC018 通过")


@pytest.mark.case_id_explore_list_tc019
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Sort 排序功能")
@allure.title("排序后刷新页面，URL 参数保留排序状态")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证选择排序 Confirm 后刷新页面，URL 仍包含 sortId 参数")
def test_tc018_sort_preserved_after_reload(page, config):
    """TC019: 排序后刷新页面，URL 参数保留排序状态"""

    # ========== Arrange ==========
    list_page = ExploreListPage(page)
    logger.info("TC019: 排序参数刷新保留")

    # ========== Act ==========
    with allure.step("步骤1：导航到目标 URL，选择价格升序并 Confirm"):
        list_page.navigate_to_url(config["target_url"])
        list_page.click_sort()
        list_page.select_sort_option("Price: Low to High")
        list_page.click_sort_confirm()
        logger.info("✓ 已选择排序并确认")

    with allure.step("步骤2：刷新页面"):
        list_page.reload_page()
        logger.info("✓ 已刷新页面")

    # ========== Assert ==========
    with allure.step("验证 URL 刷新后仍含 sortId=3"):
        current_url = list_page.get_current_url()
        assert "sortId=3" in current_url, \
            f"刷新后 URL 应仍含 'sortId=3'，实际: {current_url}"
        logger.info(f"✓ 刷新后排序参数保留: {current_url}")

    logger.info("✅ TC019 通过")


@pytest.mark.case_id_explore_list_tc020
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Sort 排序功能")
@allure.title("Sort 单选验证：切换选项后前一选项自动取消")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证选择 Price: Low to High 后切换 Most recent，前者自动取消，为单选行为")
def test_tc019_sort_single_selection(page, config):
    """TC020: Sort 只能单选，切换时前一选项自动取消"""

    # ========== Arrange ==========
    list_page = ExploreListPage(page)
    logger.info("TC020: Sort 单选验证")

    # ========== Act ==========
    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])

    with allure.step("步骤2：打开 Sort，先选 Price: Low to High"):
        list_page.click_sort()
        list_page.select_sort_option("Price: Low to High")
        logger.info("✓ 已选择 Price: Low to High")

    with allure.step("步骤3：再选 Most recent"):
        list_page.select_sort_option("Most recent")
        logger.info("✓ 已切换为 Most recent")

    with allure.step("步骤4：点击 Confirm"):
        list_page.click_sort_confirm()

    # ========== Assert ==========
    with allure.step("验证 URL 含 sortId=1（Most recent），而不是 sortId=3"):
        current_url = list_page.get_current_url()
        assert "sortId=1" in current_url, \
            f"单选切换后应为 sortId=1，实际: {current_url}"
        assert "sortId=3" not in current_url, \
            f"前一选项 sortId=3 应被取消，实际: {current_url}"
        logger.info(f"✓ 单选验证通过: {current_url}")

    logger.info("✅ TC020 通过")
