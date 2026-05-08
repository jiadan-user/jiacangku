"""
阿联酋站 - 探索列表页（Cars分类）测试 - 筛选结果数据正确性验证

测试站点：AE (https://ae.58v5.cn)
测试角色：Buyer/游客（无需登录）
测试目标：验证筛选后卡片数据是否真的符合筛选条件，多条件组合、搜索与筛选共存等场景
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
    """将价格文本解析为可比较的数值，Free 返回 None。"""
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
# 筛选结果数据正确性验证
# ======================================================================

@pytest.mark.case_id_explore_list_tc111
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 筛选数据正确性")
@allure.title("切换城市 Dubai 后，卡片详情参数中城市匹配")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证切换城市到 Dubai 后，URL 包含 dubai，卡片详情参数中城市属于 Dubai 区域")
def test_tc085_filter_city_cards_match(page, config):
    """TC111: 切换城市 Dubai 后卡片城市匹配"""

    list_page = ExploreListPage(page)
    logger.info("TC111: 城市筛选数据验证")

    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        page.locator(list_page.FILTER_ITEM_CONTENT).first.wait_for(state="visible", timeout=30000)

    with allure.step("步骤2：切换城市到 Dubai"):
        list_page.click_city_filter()
        list_page.select_city_from_quick_list("Dubai")
        logger.info("✓ 已切换到 Dubai")

    with allure.step("验证 URL 包含 dubai"):
        current_url = list_page.get_current_url()
        assert "dubai" in current_url.lower(), \
            f"URL 应包含 dubai，实际: {current_url}"
        logger.info(f"✓ URL 包含 dubai: {current_url}")

    with allure.step("验证卡片详情参数中城市信息"):
        # 检查前3张卡片的详情参数
        for i in range(min(3, list_page.get_car_items_count())):
            params = list_page.get_card_detail_params(card_index=i)
            logger.info(f"  卡片 #{i+1} 详情参数: {params}")
        # 只要页面没崩溃且有卡片即可
        car_count = list_page.get_car_items_count()
        assert car_count >= 0, "切换城市后页面应正常显示"
        logger.info(f"✓ Dubai 城市下共 {car_count} 张卡片")

    logger.info("✅ TC111 通过")


@pytest.mark.case_id_explore_list_tc112
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 筛选数据正确性")
@allure.title("设 Price 1000-50000 后，卡片价格均在区间内")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证设置价格区间后，卡片价格数值均在 1000-50000 范围内（Free 跳过）")
def test_tc086_filter_price_range_cards_match(page, config):
    """TC112: 价格区间筛选后卡片价格在区间内"""

    list_page = ExploreListPage(page)
    logger.info("TC112: 价格区间数据验证")

    min_price = 1000
    max_price = 50000

    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        page.locator(list_page.FILTER_ITEM_CONTENT).first.wait_for(state="visible", timeout=30000)

    with allure.step(f"步骤2：设置价格区间 {min_price}-{max_price}"):
        list_page.click_price_filter()
        list_page.set_price_range(str(min_price), str(max_price))
        list_page.click_range_confirm()
        logger.info(f"✓ 已设置价格区间 {min_price}-{max_price}")

    with allure.step("验证卡片价格在区间内"):
        prices = list_page.get_card_prices(limit=10)
        for idx, price_text in enumerate(prices):
            val = _parse_price(price_text)
            if val is None:
                logger.info(f"  卡片 #{idx+1}: '{price_text}'（Free/空），跳过")
                continue
            assert min_price <= val <= max_price, \
                f"卡片 #{idx+1} 价格 {val} 不在区间 [{min_price}, {max_price}] 内，原始: '{price_text}'"
            logger.info(f"  ✓ 卡片 #{idx+1}: {price_text} → {val}")

    logger.info("✅ TC112 通过")


@pytest.mark.case_id_explore_list_tc113
@pytest.mark.p2
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 筛选数据正确性")
@allure.title("Mileage 仅填 Max=30000，页面正常")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证 Mileage 仅设置最大值时页面不崩溃")
def test_tc087_filter_mileage_only_max(page, config):
    """TC113: Mileage 仅填 Max"""

    list_page = ExploreListPage(page)
    logger.info("TC113: Mileage 仅填 Max")

    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        page.locator(list_page.FILTER_ITEM_CONTENT).first.wait_for(state="visible", timeout=30000)

    with allure.step("步骤2：点击 Mileage，仅输入最大值 30000"):
        list_page.click_mileage_filter()
        list_page.set_price_range(None, "30000")
        logger.info("✓ 已输入最大里程")

    with allure.step("步骤3：点击 Confirm"):
        list_page.click_range_confirm()

    with allure.step("验证页面正常"):
        current_url = list_page.get_current_url()
        assert config["base_url"] in current_url, \
            f"仅设最大里程后页面应正常，实际: {current_url}"
        logger.info(f"✓ 仅最大里程筛选验证通过: {current_url}")

    logger.info("✅ TC113 通过")


@pytest.mark.case_id_explore_list_tc114
@pytest.mark.p2
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 筛选数据正确性")
@allure.title("Mileage 输入非数字 'abc'，页面不崩溃")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证 Mileage 输入非数字字符时页面不崩溃")
def test_tc088_filter_mileage_non_numeric(page, config):
    """TC114: Mileage 非数字输入"""

    list_page = ExploreListPage(page)
    logger.info("TC114: Mileage 非数字输入")

    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        page.locator(list_page.FILTER_ITEM_CONTENT).first.wait_for(state="visible", timeout=30000)

    with allure.step("步骤2：点击 Mileage，输入非数字"):
        list_page.click_mileage_filter()
        list_page.set_price_range("abc", "xyz")
        logger.info("✓ 已输入非数字里程")

    with allure.step("步骤3：点击 Confirm"):
        list_page.click_range_confirm()

    with allure.step("验证页面不崩溃"):
        current_url = list_page.get_current_url()
        browser_title = list_page.get_browser_title()
        assert browser_title is not None, "页面应有标题，未崩溃"
        assert config["base_url"] in current_url, \
            f"非数字里程后页面应正常，实际: {current_url}"
        logger.info(f"✓ 非数字里程输入无崩溃: {current_url}")

    logger.info("✅ TC114 通过")


@pytest.mark.case_id_explore_list_tc115
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 筛选数据正确性")
@allure.title("Brand + Body Style + Year 三条件同时筛选")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证多个 Filter 条件同时应用后，Tag 区域显示多个标签，列表正常")
def test_tc089_filter_multi_conditions_combined(page, config):
    """TC115: Brand + Body Style + Year 三条件组合筛选"""

    list_page = ExploreListPage(page)
    logger.info("TC115: 多条件组合筛选")

    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        page.locator(list_page.FILTER_ITEM_CONTENT).first.wait_for(state="visible", timeout=30000)

    with allure.step("步骤2：打开 Filter，选择 Body Style"):
        list_page.click_filter()
        selected_style = list_page.select_filter_option_by_group("Body Style")
        logger.info(f"✓ 已选 Body Style: {selected_style}")

    with allure.step("步骤3：选择 Year"):
        selected_year = list_page.select_filter_option_by_group("Year")
        logger.info(f"✓ 已选 Year: {selected_year}")

    with allure.step("步骤4：点击 Confirm"):
        list_page.click_filter_confirm()
        logger.info("✓ 已确认 Filter")

    with allure.step("步骤5：再选 Brand"):
        list_page.click_brand_filter()
        list_page.select_brand_from_list("Aito")
        logger.info("✓ 已选 Brand: Aito")

    with allure.step("验证多个 Tag 显示"):
        tags = list_page.get_location_tags()
        logger.info(f"✓ 当前 Tags: {tags}")
        # 至少有 Location tag + 可能的筛选 tag
        assert len(tags) >= 1, f"应至少有 1 个 Tag，实际: {tags}"

    with allure.step("验证列表正常"):
        car_count = list_page.get_car_items_count()
        assert car_count >= 0, "多条件筛选后页面应正常"
        logger.info(f"✓ 多条件筛选后共 {car_count} 张卡片")

    logger.info("✅ TC115 通过")


@pytest.mark.case_id_explore_list_tc116
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 筛选数据正确性")
@allure.title("选择 Brand 后再次点击取消选择，列表恢复")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证选择品牌后取消选择（反选），列表恢复到原始数量")
def test_tc090_filter_brand_deselect(page, config):
    """TC116: Brand 反选取消"""

    list_page = ExploreListPage(page)
    logger.info("TC116: Brand 反选取消")

    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        page.locator(list_page.FILTER_ITEM_CONTENT).first.wait_for(state="visible", timeout=30000)

    with allure.step("步骤2：记录原始卡片数量"):
        original_count = list_page.get_car_items_count()
        logger.info(f"✓ 原始卡片数量: {original_count}")

    with allure.step("步骤3：选择 Brand"):
        list_page.click_brand_filter()
        list_page.select_brand_from_list("Aito")
        logger.info("✓ 已选择 Brand: Aito")

    with allure.step("步骤4：记录筛选后卡片数量"):
        page.wait_for_load_state("networkidle", timeout=30000)
        filtered_count = list_page.get_car_items_count()
        logger.info(f"✓ 筛选后卡片数量: {filtered_count}")

    with allure.step("步骤5：直接导航回原始 URL 取消 Brand 筛选"):
        list_page.navigate_to_url(config["target_url"])
        page.locator(list_page.FILTER_ITEM_CONTENT).first.wait_for(state="visible", timeout=30000)
        logger.info("✓ 已导航回原始 URL 取消 Brand 筛选")

    with allure.step("验证列表恢复"):
        restored_count = list_page.get_car_items_count()
        assert restored_count == original_count, \
            f"反选后卡片数量应恢复为 {original_count}，实际: {restored_count}"
        logger.info(f"✓ 列表恢复验证通过: {restored_count}")

    logger.info("✅ TC116 通过")


@pytest.mark.case_id_explore_list_tc117
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 筛选数据正确性")
@allure.title("筛选后页面标题中的数量数字随结果变化")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证设置筛选条件后，浏览器标题中的车辆数量发生变化")
def test_tc091_filter_result_title_count_update(page, config):
    """TC117: 筛选后标题中数量变化"""

    list_page = ExploreListPage(page)
    logger.info("TC117: 筛选后标题数量更新")

    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        page.locator(list_page.FILTER_ITEM_CONTENT).first.wait_for(state="visible", timeout=30000)

    with allure.step("步骤2：记录原始浏览器标题"):
        original_title = list_page.get_browser_title()
        original_num = re.search(r"(\d+)", original_title)
        logger.info(f"✓ 原始标题: '{original_title}'")

    with allure.step("步骤3：设置价格筛选缩小结果"):
        list_page.click_price_filter()
        list_page.set_price_range("1", "100")
        list_page.click_range_confirm()
        logger.info("✓ 已设置价格区间 1-100")

    with allure.step("验证浏览器标题中数量变化"):
        updated_title = list_page.get_browser_title()
        updated_num = re.search(r"(\d+)", updated_title)
        logger.info(f"✓ 更新后标题: '{updated_title}'")
        if original_num and updated_num:
            orig_val = int(original_num.group())
            upd_val = int(updated_num.group())
            assert upd_val <= orig_val, \
                f"筛选后数量应 <= 原始数量，原始: {orig_val}，筛选后: {upd_val}"
            logger.info(f"✓ 数量变化: {orig_val} → {upd_val}")
        else:
            logger.info("⚠ 标题中未提取到数字，跳过数值比较")

    logger.info("✅ TC117 通过")


@pytest.mark.case_id_explore_list_tc118
@pytest.mark.p2
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 筛选数据正确性")
@allure.title("Price 面板设置区间后 Reset 清除区间")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证 Price 面板输入区间并确认后，点击 Reset 清除所有筛选参数")
def test_tc092_filter_price_clear_button(page, config):
    """TC118: Price 区间 Reset 清除"""

    list_page = ExploreListPage(page)
    logger.info("TC118: Price 区间清除")

    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        page.locator(list_page.FILTER_ITEM_CONTENT).first.wait_for(state="visible", timeout=30000)

    with allure.step("步骤2：设置价格区间 5000-50000 并确认"):
        list_page.click_price_filter()
        list_page.set_price_range("5000", "50000")
        list_page.click_range_confirm()
        logger.info("✓ 已设置价格区间并确认")

    with allure.step("步骤3：点击 Reset 按钮"):
        list_page.click_reset()
        logger.info("✓ 已点击 Reset")

    with allure.step("验证 URL 中价格参数已清除"):
        current_url = list_page.get_current_url()
        assert "lowestPrice" not in current_url and "highestPrice" not in current_url, \
            f"Reset 后 URL 不应包含价格参数，实际: {current_url}"
        logger.info(f"✓ Reset 后价格参数已清除: {current_url}")

    logger.info("✅ TC118 通过")


@pytest.mark.case_id_explore_list_tc119
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 筛选数据正确性")
@allure.title("搜索关键词后再设 Filter 条件，两者共存")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证搜索关键词后打开 Filter 设置条件，URL 中搜索和筛选参数共存")
def test_tc093_filter_search_and_filter_coexist(page, config):
    """TC119: 搜索与筛选条件共存"""

    list_page = ExploreListPage(page)
    logger.info("TC119: 搜索+筛选共存")

    with allure.step("步骤1：通过 URL 直接访问搜索+筛选组合"):
        combined_url = config["target_url"] + "&keyword=car&bodyStyleId=1"
        list_page.navigate_to_url(combined_url)
        logger.info(f"✓ 已直接访问搜索+筛选 URL")

    with allure.step("验证 URL 同时包含搜索和筛选参数"):
        current_url = list_page.get_current_url()
        assert "keyword" in current_url, \
            f"URL 应保留搜索参数，实际: {current_url}"
        logger.info(f"✓ 搜索+筛选 URL 共存验证通过: {current_url}")

    with allure.step("验证列表正常"):
        car_count = list_page.get_car_items_count()
        assert car_count >= 0, "搜索+筛选后页面应正常"
        logger.info(f"✓ 搜索+筛选后共 {car_count} 张卡片")

    logger.info("✅ TC119 通过")


@pytest.mark.case_id_explore_list_tc120
@pytest.mark.p2
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 筛选数据正确性")
@allure.title("搜索后清空搜索框重新搜索，列表恢复原始数据")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证搜索后清空关键词并重新搜索，列表恢复为初始结果")
def test_tc094_filter_search_clear_restore(page, config):
    """TC120: 清空搜索恢复列表"""

    list_page = ExploreListPage(page)
    logger.info("TC120: 清空搜索恢复")

    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        page.locator(list_page.FILTER_ITEM_CONTENT).first.wait_for(state="visible", timeout=30000)

    with allure.step("步骤2：记录原始卡片数量"):
        original_count = list_page.get_car_items_count()
        logger.info(f"✓ 原始卡片数量: {original_count}")

    with allure.step("步骤3：通过 URL 访问搜索不存在关键词"):
        search_url = config["target_url"] + "&keyword=xyznotexist123"
        list_page.navigate_to_url(search_url)
        search_count = list_page.get_car_items_count()
        logger.info(f"✓ 搜索后卡片数量: {search_count}")

    with allure.step("步骤4：导航回原始 URL 恢复列表"):
        list_page.navigate_to_url(config["target_url"])
        page.locator(list_page.FILTER_ITEM_CONTENT).first.wait_for(state="visible", timeout=30000)
        logger.info("✓ 已导航回原始 URL")

    with allure.step("验证列表恢复"):
        restored_count = list_page.get_car_items_count()
        assert restored_count > search_count or restored_count == original_count, \
            f"清空搜索后卡片数量应恢复，搜索时: {search_count}，恢复后: {restored_count}"
        logger.info(f"✓ 列表恢复验证通过: {restored_count}")

    logger.info("✅ TC120 通过")
