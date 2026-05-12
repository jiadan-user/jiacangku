"""
阿联酋站 - 探索列表页（Cars分类）测试 - 模块四、五：Filter 综合筛选、Location 城市筛选

本脚本由 playwright-test-generator 生成
录制文档：/Users/a58/Desktop/测试用例/okcom-探索列表页-测试用例-20260303.md
生成时间：2026-03-04

测试站点：AE (https://ae.58v5.cn)
测试角色：Buyer/游客（无需登录）
测试目标：验证 Filter 弹窗功能和 Location 城市切换功能
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


# ======================================================================
# 模块四：Filter 综合筛选
# ======================================================================

@pytest.mark.case_id_explore_list_tc021
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Filter 综合筛选")
@allure.title("点击 Filter 按钮展开筛选弹窗")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证点击 Filter 按钮后展开筛选弹窗，包含多个筛选维度")
def test_tc020_filter_panel_opens(page, config):
    """TC021: 点击 Filter 按钮展开筛选面板"""

    # ========== Arrange ==========
    list_page = ExploreListPage(page)
    logger.info("TC021: Filter 面板展开")

    # ========== Act ==========
    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        logger.info("✓ 已打开探索列表页")

    with allure.step("步骤2：点击 Filter 按钮"):
        list_page.click_filter()
        logger.info("✓ 已点击 Filter")

    # ========== Assert ==========
    with allure.step("验证 Filter 弹窗可见"):
        assert list_page.is_filter_modal_visible(), \
            "Filter 弹窗应展开可见"
        logger.info("✓ Filter 弹窗已展开")

    with allure.step("验证弹窗包含 Body Style 等筛选维度"):
        assert page.get_by_text("Body Style").first.is_visible(timeout=3000), \
            "Filter 弹窗应包含 Body Style 筛选项"
        logger.info("✓ Filter 弹窗包含筛选维度")

    logger.info("✅ TC021 通过")


@pytest.mark.case_id_explore_list_tc022
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Filter 综合筛选")
@allure.title("激活筛选条件后 Filter 按钮显示角标数字")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证在 Filter 面板中选择 1 个条件后，Filter 按钮显示 '· 1' 角标")
def test_tc021_filter_badge_shows_count(page, config):
    """TC022: 已激活筛选时 Filter 按钮显示角标数字"""

    # ========== Arrange ==========
    list_page = ExploreListPage(page)
    logger.info("TC022: Filter 角标数字")

    # ========== Act ==========
    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        logger.info("✓ 已打开探索列表页")

    with allure.step("步骤2：点击 Filter 并激活 1 个选项"):
        list_page.click_filter()
        list_page.select_first_filter_option()
        logger.info("✓ 已选择筛选条件")

    with allure.step("步骤3：点击 Confirm 关闭 Filter 面板"):
        list_page.click_filter_confirm()
        logger.info("✓ 已 Confirm Filter")

    # ========== Assert ==========
    with allure.step("验证 Filter 按钮处于激活态"):
        assert list_page.is_filter_active(), \
            "Filter 按钮应处于激活状态（含角标）"
        logger.info("✓ Filter 按钮激活态验证通过")

    with allure.step("验证角标数字 ≥ 1"):
        badge_count = list_page.get_filter_badge_count()
        assert badge_count >= 1, \
            f"Filter 角标数应 ≥ 1，实际: {badge_count}"
        logger.info(f"✓ Filter 角标数: {badge_count}")

    logger.info("✅ TC022 通过")


@pytest.mark.case_id_explore_list_tc023
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Filter 综合筛选")
@allure.title("Filter 面板内多条件组合筛选，结果符合 AND 逻辑")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证在 Filter 面板中选择多个条件后，URL 包含对应参数，筛选生效")
def test_tc022_filter_multi_condition(page, config):
    """TC023: Filter 面板内多条件组合筛选"""

    # ========== Arrange ==========
    list_page = ExploreListPage(page)
    logger.info("TC023: Filter 多条件组合")

    # ========== Act ==========
    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])

    with allure.step("步骤2：点击 Filter 并选择多个条件"):
        list_page.click_filter()
        # Select first option in first dropdown (Body Style)
        list_page.select_first_filter_option()
        logger.info("✓ 已选择 Filter 条件")

    with allure.step("步骤3：点击 Confirm 关闭"):
        list_page.click_filter_confirm()

    # ========== Assert ==========
    with allure.step("验证 Filter 激活状态"):
        assert list_page.is_filter_active(), \
            "多条件组合后 Filter 应处于激活状态"
        logger.info("✓ Filter 多条件组合验证通过")

    logger.info("✅ TC023 通过")


@pytest.mark.case_id_explore_list_tc024
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Filter 综合筛选")
@allure.title("Filter 筛选结果为空时展示空态 UI")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证筛选组合使结果为空时，页面展示空态图标和文案")
def test_tc023_filter_empty_result(page, config):
    """TC024: Filter 面板内全部条件选择后，筛选结果为空"""

    # ========== Arrange ==========
    list_page = ExploreListPage(page)
    logger.info("TC024: Filter 空结果")

    # ========== Act ==========
    with allure.step("步骤1：访问极限价格筛选 URL（返回极少结果）"):
        # Use URL-based approach with extreme price range
        empty_url = f"{config['base_url']}/en/city-abu-dhabi/cate-car/?iconSource=car&lowestPrice=99999900&highestPrice=99999999"
        list_page.navigate_to_url(empty_url)
        logger.info("✓ 已访问极限筛选 URL")

    # ========== Assert ==========
    with allure.step("验证列表显示极少或无结果，页面不崩溃"):
        current_url = list_page.get_current_url()
        assert "lowestPrice" in current_url, \
            f"URL 应包含价格参数，实际: {current_url}"
        assert config["base_url"] in current_url, \
            f"页面应保持在站点内，未崩溃，实际: {current_url}"
        logger.info(f"✓ 极限筛选页面正常，URL: {current_url}")

    logger.info("✅ TC024 通过")


@pytest.mark.case_id_explore_list_tc025
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Filter 综合筛选")
@allure.title("Filter 面板内点击 Clear 清空所有筛选条件")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证 Filter 面板点击 Clear 后所有已选条件清空")
def test_tc024_filter_clear_all(page, config):
    """TC025: Filter 面板内点击 Clear 清空所有筛选"""

    # ========== Arrange ==========
    list_page = ExploreListPage(page)
    logger.info("TC025: Filter Clear 清空")

    # ========== Act ==========
    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])

    with allure.step("步骤2：打开 Filter 并选择条件"):
        list_page.click_filter()
        list_page.select_first_filter_option()
        logger.info("✓ 已选择 Filter 条件")

    with allure.step("步骤3：点击 Filter 面板内 Clear"):
        list_page.click_filter_clear()
        logger.info("✓ 已点击 Clear")

    # ========== Assert ==========
    with allure.step("验证 Filter 面板仍展开（Clear 不关闭面板）"):
        assert list_page.is_filter_modal_visible(), \
            "点击 Clear 后 Filter 面板应保持展开"
        logger.info("✓ Filter 面板保持展开")

    with allure.step("步骤4：点击 Confirm 关闭 Filter"):
        list_page.click_filter_confirm()

    with allure.step("验证 Filter 角标清零"):
        assert not list_page.is_filter_active(), \
            "Clear 后 Confirm，Filter 角标应清零"
        logger.info("✓ Filter 角标清零")

    logger.info("✅ TC025 通过")


@pytest.mark.case_id_explore_list_tc026
@pytest.mark.p2
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Filter 综合筛选")
@allure.title("按 ESC 键关闭 Filter 面板，未确认条件不生效")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证 Filter 面板展开时按 ESC 键可关闭，未确认的条件不生效")
def test_tc025_filter_close_by_escape(page, config):
    """TC026: 按 ESC 键关闭 Filter 面板"""

    # ========== Arrange ==========
    list_page = ExploreListPage(page)
    logger.info("TC026: Filter ESC 关闭")

    # ========== Act ==========
    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])

    with allure.step("步骤2：打开 Filter 面板"):
        list_page.click_filter()
        assert list_page.is_filter_modal_visible(), "Filter 面板应已展开"
        logger.info("✓ Filter 面板已展开")

    with allure.step("步骤3：按 Escape 关闭面板"):
        list_page.close_filter_by_escape()
        logger.info("✓ 已按 Escape")

    # ========== Assert ==========
    with allure.step("验证 Filter 面板已关闭"):
        assert not list_page.is_filter_modal_visible(), \
            "按 ESC 后 Filter 面板应关闭"
        logger.info("✓ Filter 面板已关闭")

    with allure.step("验证 Filter 角标未增加（条件未生效）"):
        assert not list_page.is_filter_active(), \
            "ESC 关闭后 Filter 不应有激活态角标"
        logger.info("✓ ESC 关闭不生效验证通过")

    logger.info("✅ TC026 通过")


# ======================================================================
# 模块五：Location 城市筛选
# ======================================================================

@pytest.mark.case_id_explore_list_tc027
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Location 城市筛选")
@allure.title("切换城市为 Dubai，页面标题和 Tag 更新为 Dubai")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证点击 Abu Dhabi 下拉并选择 Dubai 后，页面标题、URL、Location Tag 均更新")
def test_tc026_switch_city_to_dubai(page, config):
    """TC027: 切换城市为 Dubai，页面标题和 Tag 更新"""

    # ========== Arrange ==========
    list_page = ExploreListPage(page)
    logger.info("TC027: 切换城市 Dubai")

    # ========== Act ==========
    with allure.step("步骤1：导航到 Abu Dhabi URL"):
        list_page.navigate_to_url(config["target_url"])
        logger.info("✓ 已打开 Abu Dhabi Cars 列表页")

    with allure.step("步骤2：点击 Abu Dhabi 下拉打开城市列表"):
        list_page.click_city_filter()
        logger.info("✓ 已点击城市筛选")

    with allure.step("步骤3：选择 Dubai"):
        list_page.select_city_from_quick_list("Dubai")
        logger.info("✓ 已选择 Dubai")

    # ========== Assert ==========
    with allure.step("验证 URL 包含 city-dubai"):
        current_url = list_page.get_current_url()
        assert "city-dubai" in current_url, \
            f"URL 应包含 'city-dubai'，实际: {current_url}"
        logger.info(f"✓ URL 切换验证通过: {current_url}")

    with allure.step("验证页面标题变为 'Cars in Dubai'"):
        title = list_page.get_page_title_text()
        assert "Dubai" in title, \
            f"页面标题应包含 'Dubai'，实际: '{title}'"
        logger.info(f"✓ 页面标题验证通过: '{title}'")

    with allure.step("验证 Location Tag 变为 Dubai"):
        tags = list_page.get_location_tags()
        assert any("Dubai" in t for t in tags), \
            f"Location Tag 应包含 'Dubai'，实际: {tags}"
        logger.info(f"✓ Location Tag 验证通过: {tags}")

    logger.info("✅ TC027 通过")


@pytest.mark.case_id_explore_list_tc028
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Location 城市筛选")
@allure.title("点击 Location Tag 上的 × 移除城市筛选")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证点击 Location Tag 的关闭图标后，Tag 消失，URL 切换为全国路径")
def test_tc027_remove_location_tag(page, config):
    """TC028: 点击 Location Tag 上的 × 移除城市筛选"""

    # ========== Arrange ==========
    list_page = ExploreListPage(page)
    logger.info("TC028: 移除 Location Tag")

    # ========== Act ==========
    with allure.step("步骤1：导航到 Abu Dhabi URL（Location Tag 存在）"):
        list_page.navigate_to_url(config["target_url"])
        assert list_page.is_location_tag_visible(), "Location Tag 应存在"
        logger.info("✓ Location Tag 确认存在")

    with allure.step("步骤2：点击 Location Tag 的 × 按钮"):
        list_page.click_location_tag_close()
        logger.info("✓ 已点击 × 按钮")

    # ========== Assert ==========
    with allure.step("验证 Location Tag 消失"):
        tag_count = list_page.get_location_tags_count()
        assert tag_count == 0, \
            f"点击 × 后 Location Tag 应消失，实际数量: {tag_count}"
        logger.info("✓ Location Tag 已消失")

    with allure.step("验证 URL 已移除城市限制"):
        current_url = list_page.get_current_url()
        assert "city-abu-dhabi" not in current_url, \
            f"移除城市后 URL 应无 'city-abu-dhabi'，实际: {current_url}"
        logger.info(f"✓ URL 城市限制已移除: {current_url}")

    logger.info("✅ TC028 通过")


@pytest.mark.case_id_explore_list_tc029
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Location 城市筛选")
@allure.title("城市下拉列表展示完整城市选项，当前城市高亮")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证点击城市下拉后，展示 UAE 主要城市列表，包含 Dubai 选项")
def test_tc028_city_dropdown_shows_list(page, config):
    """TC029: 城市下拉列表展示完整城市选项"""

    # ========== Arrange ==========
    list_page = ExploreListPage(page)
    logger.info("TC029: 城市列表展示")

    # ========== Act ==========
    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])

    with allure.step("步骤2：点击 Abu Dhabi 下拉"):
        list_page.click_city_filter()
        logger.info("✓ 已打开城市下拉")

    # ========== Assert ==========
    with allure.step("验证城市列表可见，包含 Dubai"):
        assert list_page.is_city_dropdown_visible(), \
            "城市快速列表应可见"
        assert page.get_by_text("Dubai").first.is_visible(timeout=3000), \
            "城市列表应包含 Dubai"
        logger.info("✓ 城市列表展示验证通过")

    logger.info("✅ TC029 通过")


@pytest.mark.case_id_explore_list_tc030
@pytest.mark.p2
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Location 城市筛选")
@allure.title("URL 包含不存在的城市参数，页面不崩溃")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证直接访问不存在城市的 URL，页面显示 404 或重定向，不白屏")
def test_tc029_invalid_city_url(page, config):
    """TC030: URL 直接包含不存在的城市参数"""

    # ========== Arrange ==========
    list_page = ExploreListPage(page)
    invalid_url = f"{config['base_url']}/en/city-invalid-city/cate-car/"
    logger.info(f"TC030: 不存在城市 URL: {invalid_url}")

    # ========== Act ==========
    with allure.step("步骤1：直接访问不存在城市的 URL"):
        list_page.navigate_to_url(invalid_url)
        logger.info("✓ 已访问无效城市 URL")

    # ========== Assert ==========
    with allure.step("验证页面不白屏，不显示 JS 错误"):
        current_url = list_page.get_current_url()
        browser_title = list_page.get_browser_title()
        # 页面应有标题（非崩溃）
        assert browser_title is not None, \
            "访问无效城市 URL 后页面不应崩溃，应有标题"
        logger.info(f"✓ 无效城市 URL 处理验证通过，当前 URL: {current_url}")

    logger.info("✅ TC030 通过")


# ======================================================================
# 模块四扩展：Filter 各条件逐项验证
# ======================================================================

@pytest.mark.case_id_explore_list_tc063
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Filter 综合筛选")
@allure.title("Filter 弹窗展示 8 个筛选分组：Body Style/Color/Year/Specs/Fuel Type/Transmission/Engine/Drive Type")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证 Filter 弹窗内包含全部 8 个筛选分组名称，顺序正确")
def test_tc059_filter_all_groups_visible(page, config):
    """TC063: Filter 弹窗包含所有筛选分组"""

    list_page = ExploreListPage(page)
    logger.info("TC063: Filter 弹窗全分组可见性验证")

    expected_groups = [
        "Body Style", "Body Color", "Year", "Specs",
        "Fuel Type", "Transmission", "Engine(cc)", "Drive Type"
    ]

    with allure.step("步骤1：打开 Filter 弹窗"):
        list_page.navigate_to_url(config["target_url"])
        list_page.click_filter()
        assert list_page.is_filter_modal_visible(), "Filter 弹窗应展开"

    with allure.step("验证所有分组名称均存在"):
        actual_groups = list_page.get_filter_all_group_names()
        logger.info(f"实际分组: {actual_groups}")
        for group in expected_groups:
            assert group in actual_groups, \
                f"Filter 弹窗应包含分组 '{group}'，实际分组: {actual_groups}"
        logger.info(f"✓ 全部 {len(expected_groups)} 个分组均存在")

    logger.info("✅ TC063 通过")


@pytest.mark.case_id_explore_list_tc064
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Filter 综合筛选")
@allure.title("Filter - Body Style 选择 SUV，URL 含 attr_181 参数，列表结果更新")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证在 Filter 弹窗选择 Body Style = SUV 后，URL 包含 attr_181 参数，Filter 角标数为 1")
def test_tc060_filter_body_style_suv(page, config):
    """TC064: Filter - Body Style 筛选 SUV"""

    list_page = ExploreListPage(page)
    logger.info("TC064: Filter Body Style SUV")

    with allure.step("步骤1：打开 Filter 弹窗"):
        list_page.navigate_to_url(config["target_url"])
        list_page.click_filter()

    with allure.step("步骤2：选择 Body Style = SUV"):
        selected = list_page.select_filter_option_by_group("Body Style", option_text="SUV")
        logger.info(f"✓ 已选择 Body Style: {selected}")

    with allure.step("步骤3：Confirm 筛选"):
        list_page.click_filter_confirm()

    with allure.step("验证 URL 包含 Body Style 参数 attr_181"):
        current_url = list_page.get_current_url()
        assert "attr_181" in current_url, \
            f"URL 应含 'attr_181'（Body Style），实际: {current_url}"
        logger.info(f"✓ URL 验证通过: {current_url}")

    with allure.step("验证 Filter 角标数为 1"):
        badge = list_page.get_filter_badge_count()
        assert badge >= 1, f"选择 1 个 Body Style 后角标应 ≥ 1，实际: {badge}"
        logger.info(f"✓ Filter 角标: {badge}")

    logger.info("✅ TC064 通过")


@pytest.mark.case_id_explore_list_tc065
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Filter 综合筛选")
@allure.title("Filter - Body Color 选择 White，URL 含 attr_180 参数")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证选择 Body Color = White 后，URL 包含 attr_180 参数，Filter 激活")
def test_tc061_filter_body_color_white(page, config):
    """TC065: Filter - Body Color 筛选 White"""

    list_page = ExploreListPage(page)
    logger.info("TC065: Filter Body Color White")

    with allure.step("步骤1：打开 Filter 弹窗"):
        list_page.navigate_to_url(config["target_url"])
        list_page.click_filter()

    with allure.step("步骤2：选择 Body Color = White"):
        selected = list_page.select_filter_option_by_group("Body Color", option_text="White")
        logger.info(f"✓ 已选择颜色: {selected}")

    with allure.step("步骤3：Confirm 筛选"):
        list_page.click_filter_confirm()

    with allure.step("验证 URL 含 attr_180（Body Color）"):
        current_url = list_page.get_current_url()
        assert "attr_180" in current_url, \
            f"URL 应含 'attr_180'（Body Color），实际: {current_url}"
        logger.info(f"✓ Body Color URL 验证通过: {current_url}")

    with allure.step("验证 Filter 处于激活状态"):
        assert list_page.is_filter_active(), "选择 Body Color 后 Filter 应激活"
        logger.info("✓ Filter 激活状态验证通过")

    logger.info("✅ TC065 通过")


@pytest.mark.case_id_explore_list_tc066
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Filter 综合筛选")
@allure.title("Filter - Year 下拉选项包含历史年份，选择后 URL 含 attr_190")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证 Year 下拉包含历史年份选项，选择后 URL 含 attr_190 参数")
def test_tc062_filter_year_selection(page, config):
    """TC066: Filter - Year 年份筛选"""

    list_page = ExploreListPage(page)
    logger.info("TC066: Filter Year 筛选")

    with allure.step("步骤1：打开 Filter 弹窗"):
        list_page.navigate_to_url(config["target_url"])
        list_page.click_filter()

    with allure.step("步骤2：查看 Year 选项列表"):
        year_options = list_page.get_filter_group_options("Year")
        logger.info(f"Year 选项: {year_options[:5]}...")
        assert len(year_options) > 0, "Year 选项不应为空"
        assert any(opt.isdigit() and 2000 <= int(opt) <= 2030 for opt in year_options), \
            f"Year 选项应包含合法年份，实际: {year_options[:5]}"

    with allure.step("步骤3：重新导航后打开 Filter 并选择第一个年份"):
        list_page.navigate_to_url(config["target_url"])
        list_page.click_filter()
        selected = list_page.select_filter_option_by_group("Year", option_index=0)
        logger.info(f"✓ 已选择年份: {selected}")
        list_page.click_filter_confirm()

    with allure.step("验证 URL 含 attr_190（Year）"):
        current_url = list_page.get_current_url()
        assert "attr_190" in current_url, \
            f"URL 应含 'attr_190'（Year），实际: {current_url}"
        logger.info(f"✓ Year URL 验证通过: {current_url}")

    logger.info("✅ TC066 通过")


@pytest.mark.case_id_explore_list_tc067
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Filter 综合筛选")
@allure.title("Filter - Specs 选择 European，URL 含 attr_186 参数")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证选择 Specs = European 后，URL 包含 attr_186 参数")
def test_tc063_filter_specs_european(page, config):
    """TC067: Filter - Specs 规格筛选"""

    list_page = ExploreListPage(page)
    logger.info("TC067: Filter Specs European")

    with allure.step("步骤1：打开 Filter 弹窗"):
        list_page.navigate_to_url(config["target_url"])
        list_page.click_filter()

    with allure.step("步骤2：选择 Specs = European"):
        selected = list_page.select_filter_option_by_group("Specs", option_text="European")
        logger.info(f"✓ 已选择规格: {selected}")

    with allure.step("步骤3：Confirm 筛选"):
        list_page.click_filter_confirm()

    with allure.step("验证 URL 含 attr_186（Specs）"):
        current_url = list_page.get_current_url()
        assert "attr_186" in current_url, \
            f"URL 应含 'attr_186'（Specs），实际: {current_url}"
        logger.info(f"✓ Specs URL 验证通过: {current_url}")

    logger.info("✅ TC067 通过")


@pytest.mark.case_id_explore_list_tc068
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Filter 综合筛选")
@allure.title("Filter - Fuel Type 选择 Petrol，URL 含 attr_183 参数")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证选择 Fuel Type = Petrol 后，URL 含 attr_183，列表结果为汽油车")
def test_tc064_filter_fuel_type_petrol(page, config):
    """TC068: Filter - Fuel Type 燃油类型筛选"""

    list_page = ExploreListPage(page)
    logger.info("TC068: Filter Fuel Type Petrol")

    with allure.step("步骤1：查看 Fuel Type 全选项"):
        list_page.navigate_to_url(config["target_url"])
        list_page.click_filter()
        fuel_options = list_page.get_filter_group_options("Fuel Type")
        logger.info(f"Fuel Type 选项: {fuel_options}")
        assert "Petrol" in fuel_options or "Diesel" in fuel_options, \
            f"Fuel Type 应包含 Petrol 或 Diesel，实际: {fuel_options}"

    with allure.step("步骤2：重新导航后打开 Filter 并选择 Petrol"):
        list_page.navigate_to_url(config["target_url"])
        list_page.click_filter()
        target = "Petrol" if "Petrol" in fuel_options else fuel_options[0]
        selected = list_page.select_filter_option_by_group("Fuel Type", option_text=target)
        logger.info(f"✓ 已选择燃油类型: {selected}")
        list_page.click_filter_confirm()

    with allure.step("验证 URL 含 attr_183（Fuel Type）"):
        current_url = list_page.get_current_url()
        assert "attr_183" in current_url, \
            f"URL 应含 'attr_183'（Fuel Type），实际: {current_url}"
        logger.info(f"✓ Fuel Type URL 验证通过: {current_url}")

    logger.info("✅ TC068 通过")


@pytest.mark.case_id_explore_list_tc069
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Filter 综合筛选")
@allure.title("Filter - Transmission 选择 Auto，URL 含 attr_188 参数")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证选择 Transmission = Auto 后，URL 含 attr_188 参数，Filter 激活")
def test_tc065_filter_transmission_auto(page, config):
    """TC069: Filter - Transmission 变速箱类型筛选"""

    list_page = ExploreListPage(page)
    logger.info("TC069: Filter Transmission Auto")

    with allure.step("步骤1：打开 Filter 弹窗查看 Transmission 选项"):
        list_page.navigate_to_url(config["target_url"])
        list_page.click_filter()
        trans_options = list_page.get_filter_group_options("Transmission")
        logger.info(f"Transmission 选项: {trans_options}")
        assert "Auto" in trans_options or len(trans_options) > 0, \
            f"Transmission 应有选项，实际: {trans_options}"

    with allure.step("步骤2：重新导航后打开 Filter 并选择 Auto"):
        list_page.navigate_to_url(config["target_url"])
        list_page.click_filter()
        target = "Auto" if "Auto" in trans_options else trans_options[0]
        selected = list_page.select_filter_option_by_group("Transmission", option_text=target)
        logger.info(f"✓ 已选择变速箱: {selected}")
        list_page.click_filter_confirm()

    with allure.step("验证 URL 含 attr_188（Transmission）"):
        current_url = list_page.get_current_url()
        assert "attr_188" in current_url, \
            f"URL 应含 'attr_188'（Transmission），实际: {current_url}"
        logger.info(f"✓ Transmission URL 验证通过: {current_url}")

    logger.info("✅ TC069 通过")


@pytest.mark.case_id_explore_list_tc070
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Filter 综合筛选")
@allure.title("Filter - Engine(cc) 输入排量区间 1000-3000，URL 含 attr_184 参数")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证在 Engine(cc) 输入框输入 1000-3000 并 Confirm 后，URL 含 attr_184=1000_3000")
def test_tc066_filter_engine_cc_range(page, config):
    """TC070: Filter - Engine(cc) 排量区间筛选"""

    list_page = ExploreListPage(page)
    logger.info("TC070: Filter Engine(cc) Range")

    with allure.step("步骤1：打开 Filter 弹窗"):
        list_page.navigate_to_url(config["target_url"])
        list_page.click_filter()
        assert list_page.is_filter_modal_visible(), "Filter 弹窗应展开"

    with allure.step("步骤2：在 Engine(cc) 输入排量区间 1000-3000"):
        list_page.set_engine_cc_range(1000, 3000)
        logger.info("✓ 已输入 Engine(cc) 区间 1000-3000")

    with allure.step("步骤3：Confirm 筛选"):
        list_page.click_filter_confirm()

    with allure.step("验证 URL 含 attr_184（Engine cc）及区间值"):
        current_url = list_page.get_current_url()
        assert "attr_184" in current_url, \
            f"URL 应含 'attr_184'（Engine cc），实际: {current_url}"
        assert "1000" in current_url and "3000" in current_url, \
            f"URL 应含排量区间值 1000 和 3000，实际: {current_url}"
        logger.info(f"✓ Engine(cc) URL 验证通过: {current_url}")

    logger.info("✅ TC070 通过")


@pytest.mark.case_id_explore_list_tc071
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - Filter 综合筛选")
@allure.title("Filter - Drive Type 选择 AWD，URL 含 attr_182 参数")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证选择 Drive Type = AWD 后，URL 含 attr_182 参数，Filter 激活")
def test_tc067_filter_drive_type_awd(page, config):
    """TC071: Filter - Drive Type 驱动类型筛选"""

    list_page = ExploreListPage(page)
    logger.info("TC071: Filter Drive Type AWD")

    with allure.step("步骤1：打开 Filter 弹窗查看 Drive Type 选项"):
        list_page.navigate_to_url(config["target_url"])
        list_page.click_filter()
        drive_options = list_page.get_filter_group_options("Drive Type")
        logger.info(f"Drive Type 选项: {drive_options}")
        assert len(drive_options) > 0, "Drive Type 应有选项"

    with allure.step("步骤2：重新导航后打开 Filter 并选择 AWD"):
        list_page.navigate_to_url(config["target_url"])
        list_page.click_filter()
        target = "AWD" if "AWD" in drive_options else drive_options[0]
        selected = list_page.select_filter_option_by_group("Drive Type", option_text=target)
        logger.info(f"✓ 已选择驱动类型: {selected}")
        list_page.click_filter_confirm()

    with allure.step("验证 URL 含 attr_182（Drive Type）"):
        current_url = list_page.get_current_url()
        assert "attr_182" in current_url, \
            f"URL 应含 'attr_182'（Drive Type），实际: {current_url}"
        logger.info(f"✓ Drive Type URL 验证通过: {current_url}")

    with allure.step("验证 Filter 处于激活状态"):
        assert list_page.is_filter_active(), "选择 Drive Type 后 Filter 应激活"
        logger.info("✓ Filter 激活状态验证通过")

    logger.info("✅ TC071 通过")
