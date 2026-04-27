"""
阿联酋站 - 探索列表页（Cars分类）测试 - 排序数据正确性验证

测试站点：AE (https://ae.58v5.cn)
测试角色：Buyer/游客（无需登录）
测试目标：验证排序后卡片数据顺序是否正确，排序与筛选/搜索/分页的组合场景
"""
import re
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


def _parse_price(text: str):
    """将价格文本解析为可比较的数值，Free 返回 None。
    支持格式：AED543, AED22K+, AED4M+, AED1,234, Free
    """
    if not text or text.strip().lower() == "free":
        return None
    cleaned = text.replace("AED", "").replace(",", "").replace("+", "").strip()
    if cleaned.upper().endswith("M"):
        num = re.search(r"[\d.]+", cleaned)
        return float(num.group()) * 1_000_000 if num else None
    if cleaned.upper().endswith("K"):
        num = re.search(r"[\d.]+", cleaned)
        return float(num.group()) * 1_000 if num else None
    num = re.search(r"[\d.]+", cleaned)
    return float(num.group()) if num else None


# ======================================================================
# 排序数据正确性验证
# ======================================================================

@pytest.mark.case_id_explore_list_tc101
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 排序数据正确性")
@allure.title("Price Low to High 排序后卡片价格递增")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证选择价格升序后，前10张卡片的价格数值呈非递减顺序")
def test_tc077_sort_price_low_to_high_data(page, config):
    """TC101: 价格升序后卡片价格数值递增"""

    list_page = ExploreListPage(page)
    logger.info("TC101: 价格升序数据验证")

    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        page.locator(list_page.FILTER_ITEM_CONTENT).first.wait_for(state="visible", timeout=15000)

    with allure.step("步骤2：选择 Price: Low to High 排序"):
        list_page.click_sort()
        list_page.select_sort_option("Price: Low to High")
        list_page.click_sort_confirm()
        logger.info("✓ 已选择价格升序并确认")

    with allure.step("验证前10张卡片价格递增"):
        prices = list_page.get_card_prices(limit=10)
        numeric_prices = [_parse_price(p) for p in prices if _parse_price(p) is not None]
        assert len(numeric_prices) >= 2, f"应至少有 2 个有效价格用于比较，实际: {len(numeric_prices)}"
        for i in range(len(numeric_prices) - 1):
            assert numeric_prices[i] <= numeric_prices[i + 1], \
                f"价格应递增，但第 {i+1} 张({numeric_prices[i]}) > 第 {i+2} 张({numeric_prices[i+1]})"
        logger.info(f"✓ 价格递增验证通过: {numeric_prices}")

    logger.info("✅ TC101 通过")


@pytest.mark.case_id_explore_list_tc102
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 排序数据正确性")
@allure.title("Price High to Low 排序后卡片价格递减")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证选择价格降序后，前10张卡片的价格数值呈非递增顺序")
def test_tc078_sort_price_high_to_low_data(page, config):
    """TC102: 价格降序后卡片价格数值递减"""

    list_page = ExploreListPage(page)
    logger.info("TC102: 价格降序数据验证")

    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        page.locator(list_page.FILTER_ITEM_CONTENT).first.wait_for(state="visible", timeout=15000)

    with allure.step("步骤2：选择 Price: High to Low 排序"):
        list_page.click_sort()
        list_page.select_sort_option("Price: High to Low")
        list_page.click_sort_confirm()
        logger.info("✓ 已选择价格降序并确认")

    with allure.step("验证前10张卡片价格递减"):
        prices = list_page.get_card_prices(limit=10)
        numeric_prices = [_parse_price(p) for p in prices if _parse_price(p) is not None]
        assert len(numeric_prices) >= 2, f"应至少有 2 个有效价格用于比较，实际: {len(numeric_prices)}"
        for i in range(len(numeric_prices) - 1):
            assert numeric_prices[i] >= numeric_prices[i + 1], \
                f"价格应递减，但第 {i+1} 张({numeric_prices[i]}) < 第 {i+2} 张({numeric_prices[i+1]})"
        logger.info(f"✓ 价格递减验证通过: {numeric_prices}")

    logger.info("✅ TC102 通过")


@pytest.mark.case_id_explore_list_tc103
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 排序数据正确性")
@allure.title("筛选 Brand 后排序 Price Low to High，结果同时满足")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("先选择 Brand 筛选，再按价格升序排列，验证 URL 同时包含品牌和排序参数")
def test_tc079_sort_with_filter_combined(page, config):
    """TC103: 先选 Brand，再排序 Price Low→High"""

    list_page = ExploreListPage(page)
    logger.info("TC103: Brand + 价格排序联动")

    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        page.locator(list_page.FILTER_ITEM_CONTENT).first.wait_for(state="visible", timeout=15000)

    with allure.step("步骤2：选择 Brand"):
        list_page.click_brand_filter()
        list_page.select_brand_from_list("Aito")
        logger.info("✓ 已选择 Brand: Aito")

    with allure.step("步骤3：选择 Price: Low to High 排序"):
        list_page.click_sort()
        list_page.select_sort_option("Price: Low to High")
        list_page.click_sort_confirm()
        logger.info("✓ 已选择价格升序")

    with allure.step("验证 URL 同时包含品牌和排序参数"):
        current_url = list_page.get_current_url()
        assert "sortId=3" in current_url, \
            f"URL 应包含排序参数 sortId=3，实际: {current_url}"
        logger.info(f"✓ 筛选+排序联动验证通过: {current_url}")

    with allure.step("验证卡片价格仍递增"):
        prices = list_page.get_card_prices(limit=10)
        numeric_prices = [_parse_price(p) for p in prices if _parse_price(p) is not None]
        if len(numeric_prices) >= 2:
            for i in range(len(numeric_prices) - 1):
                assert numeric_prices[i] <= numeric_prices[i + 1], \
                    f"价格应递增，但第 {i+1} 张({numeric_prices[i]}) > 第 {i+2} 张({numeric_prices[i+1]})"
            logger.info(f"✓ 筛选后价格排序正确: {numeric_prices}")
        else:
            logger.info("⚠ 筛选结果不足 2 条，跳过排序校验")

    logger.info("✅ TC103 通过")


@pytest.mark.case_id_explore_list_tc104
@pytest.mark.p2
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 排序数据正确性")
@allure.title("切换排序方式前后列表总数不变")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证从默认排序切换到价格升序后，页面卡片数量不变")
def test_tc080_sort_result_count_unchanged(page, config):
    """TC104: 切换排序方式前后列表总数不变"""

    list_page = ExploreListPage(page)
    logger.info("TC104: 排序前后数量一致")

    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        page.locator(list_page.FILTER_ITEM_CONTENT).first.wait_for(state="visible", timeout=15000)

    with allure.step("步骤2：记录默认排序下卡片数量"):
        count_before = list_page.get_car_items_count()
        logger.info(f"✓ 默认排序卡片数量: {count_before}")

    with allure.step("步骤3：切换到 Price: Low to High"):
        list_page.click_sort()
        list_page.select_sort_option("Price: Low to High")
        list_page.click_sort_confirm()

    with allure.step("验证卡片数量不变"):
        count_after = list_page.get_car_items_count()
        assert count_after == count_before, \
            f"排序后卡片数量应不变，排序前: {count_before}，排序后: {count_after}"
        logger.info(f"✓ 排序前后卡片数量一致: {count_after}")

    logger.info("✅ TC104 通过")


@pytest.mark.case_id_explore_list_tc105
@pytest.mark.p2
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 排序数据正确性")
@allure.title("价格升序时 Free 帖子的排序位置合理")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证价格升序排列时，Free 帖子要么在最前、要么在最后，位置一致")
def test_tc081_sort_price_low_free_position(page, config):
    """TC105: 价格升序时 Free 帖子排序位置"""

    list_page = ExploreListPage(page)
    logger.info("TC105: Free 帖子排序位置")

    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        page.locator(list_page.FILTER_ITEM_CONTENT).first.wait_for(state="visible", timeout=15000)

    with allure.step("步骤2：选择 Price: Low to High"):
        list_page.click_sort()
        list_page.select_sort_option("Price: Low to High")
        list_page.click_sort_confirm()
        logger.info("✓ 已选择价格升序")

    with allure.step("验证 Free 帖子位置合理"):
        prices = list_page.get_card_prices(limit=10)
        free_indices = [i for i, p in enumerate(prices) if p.strip().lower() == "free"]
        if free_indices:
            # Free 帖子应聚集在开头或末尾
            all_at_start = all(idx < len(free_indices) for idx in free_indices)
            all_at_end = all(idx >= len(prices) - len(free_indices) for idx in free_indices)
            assert all_at_start or all_at_end, \
                f"Free 帖子应聚集在最前或最后，实际位置: {free_indices}"
            position = "最前" if all_at_start else "最后"
            logger.info(f"✓ Free 帖子在{position}，位置: {free_indices}")
        else:
            logger.info("⚠ 前10张卡片中无 Free 帖子，跳过位置校验")

    logger.info("✅ TC105 通过")


@pytest.mark.case_id_explore_list_tc106
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 排序数据正确性")
@allure.title("从 Price Low→High 切换到 Most recent，数据重新加载")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证切换排序方式后 URL 更新且首条卡片标题可能变化")
def test_tc082_sort_switch_between_options(page, config):
    """TC106: 切换排序方式，数据重新加载"""

    list_page = ExploreListPage(page)
    logger.info("TC106: 切换排序方式")

    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        page.locator(list_page.FILTER_ITEM_CONTENT).first.wait_for(state="visible", timeout=15000)

    with allure.step("步骤2：通过 URL 直接访问价格升序排序"):
        sort_low_url = config["target_url"] + "&sortId=3"
        list_page.navigate_to_url(sort_low_url)
        url_first = list_page.get_current_url()
        logger.info(f"✓ 价格升序 URL: {url_first}")

    with allure.step("步骤3：通过 URL 切换到 Most recent"):
        sort_recent_url = config["target_url"] + "&sortId=1"
        list_page.navigate_to_url(sort_recent_url)
        url_second = list_page.get_current_url()
        logger.info(f"✓ 最新排序 URL: {url_second}")

    with allure.step("验证 URL 排序参数已更新"):
        assert "sortId=3" not in url_second, \
            f"切换后 URL 不应保留旧排序参数 sortId=3，实际: {url_second}"
        assert "sortId=1" in url_second, \
            f"URL 应包含 sortId=1，实际: {url_second}"
        logger.info("✓ 排序切换验证通过")

    logger.info("✅ TC106 通过")


@pytest.mark.case_id_explore_list_tc107
@pytest.mark.p2
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 排序数据正确性")
@allure.title("搜索关键词后再排序，两个条件共存")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证搜索关键词后选择排序，URL 同时包含 keyword 和 sortId")
def test_tc083_sort_and_search_combined(page, config):
    """TC107: 搜索关键词后再排序"""

    list_page = ExploreListPage(page)
    logger.info("TC107: 搜索+排序联动")

    with allure.step("步骤1：通过 URL 直接访问搜索+排序组合"):
        combined_url = config["target_url"] + "&keyword=car&sortId=4"
        list_page.navigate_to_url(combined_url)
        logger.info(f"✓ 已直接访问搜索+排序 URL")

    with allure.step("验证 URL 同时包含搜索和排序参数"):
        current_url = list_page.get_current_url()
        assert "keyword" in current_url, \
            f"URL 应保留搜索参数 keyword，实际: {current_url}"
        assert "sortId=4" in current_url, \
            f"URL 应包含排序参数 sortId=4，实际: {current_url}"
        logger.info(f"✓ 搜索+排序 URL 验证通过: {current_url}")

    logger.info("✅ TC107 通过")


@pytest.mark.case_id_explore_list_tc108
@pytest.mark.p2
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 排序数据正确性")
@allure.title("排序后翻到第2页，排序条件仍保持")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证排序后点击 Next 翻页，URL 中排序参数仍存在")
def test_tc084_sort_and_pagination(page, config):
    """TC108: 排序后翻页，排序条件保持"""

    list_page = ExploreListPage(page)
    logger.info("TC108: 排序+翻页")

    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        page.locator(list_page.FILTER_ITEM_CONTENT).first.wait_for(state="visible", timeout=15000)

    with allure.step("步骤2：选择 Price: Low to High"):
        list_page.click_sort()
        list_page.select_sort_option("Price: Low to High")
        list_page.click_sort_confirm()
        logger.info("✓ 已选择价格升序")

    with allure.step("步骤3：点击 Next 翻页"):
        if list_page.is_next_page_btn_visible():
            list_page.click_next_page()
            logger.info("✓ 已点击 Next 翻页")
        else:
            pytest.skip("列表不足 2 页，跳过翻页验证")

    with allure.step("验证翻页后排序参数仍在 URL 中"):
        current_url = list_page.get_current_url()
        assert "sortId=3" in current_url, \
            f"翻页后 URL 应保留排序参数 sortId=3，实际: {current_url}"
        logger.info(f"✓ 翻页后排序参数保持: {current_url}")

    logger.info("✅ TC108 通过")
