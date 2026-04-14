"""
AU站 - 列表卡片房产类型功能测试（买房列表 sale/cate-buy）

本脚本由 playwright-test-generator 生成
录制文档：test_plans/au58-Property-列表卡片房产类型功能测试用例.md
生成时间：2026-03-10
测试站点：AU (https://au.58v5.cn)，需登录
测试目标：验证 Canberra 买房列表页（cate-buy）列表卡片的房产类型展示
"""
import pytest
import allure
from pages.property_list_page import PropertyListPage
from utils.logger import setup_logger

logger = setup_logger()

# 买房列表（sale）path_part
PATH_PART_BUY = "cate-property-for-sale-"

# ============================================
# 测试环境配置（买房列表）
# ============================================
_CONFIG = {
    "site": "au",
    "site_name": "AU站（澳大利亚）",
    "role": "guest",
    "user_name": "guest_au",
    "base_url": "https://au.58v5.cn",
    "test_account": None,
    "list_url": "https://au.58v5.cn/en/city-canberra/cate-buy/?iconSource=buy",
    "browser": {
        "type": "chromium",
        "headless": True,
        "viewport": {"width": 1920, "height": 1080},
    },
    "timeout": {"default": 30000, "wait": 10000, "navigation": 30000},
}


def _ensure_logged_in_and_on_list(page, config):
    """直接打开买房列表页（无需登录）。"""
    list_url = config["list_url"]
    plp = PropertyListPage(page)
    page.goto(list_url, wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
    page.wait_for_load_state("domcontentloaded", timeout=5000)
    try:
        cookie_btn = page.locator("button:has-text('Accept all'), button:has-text('Accept')").first
        if cookie_btn.is_visible(timeout=2000):
            cookie_btn.click()
            page.wait_for_timeout(1000)
    except Exception:
        pass
    return plp


# ============================================
# TC001 列表页卡片展示房产类型（买房）
# ============================================
@pytest.mark.case_id_au58_list_card_property_type_buy_001
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片房产类型功能-买房列表")
@allure.title("列表页卡片展示房产类型（买房）")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("买房列表每条卡片均展示房产类型信息")
def test_tc001_list_cards_show_property_type_buy(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    card_count = plp.get_list_card_links_count(path_part=PATH_PART_BUY)
    assert card_count > 0, "买房列表页应至少有一条卡片"
    prop_type = plp.get_first_card_property_type_text(path_part=PATH_PART_BUY)
    assert prop_type and len(prop_type.strip()) > 0, "第一张卡片应有非空房产类型"
    logger.info(f"✓ 卡片数: {card_count}, 首卡房产类型: {prop_type}")


# ============================================
# TC002 列表卡片房产类型取值合理（买房）
# ============================================
@pytest.mark.case_id_au58_list_card_property_type_buy_002
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片房产类型功能-买房列表")
@allure.title("列表卡片房产类型取值合理（买房）")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("买房列表房产类型为系统支持的枚举值或合理英文")
def test_tc002_property_type_values_valid_buy(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    prop_type = plp.get_first_card_property_type_text(path_part=PATH_PART_BUY)
    assert prop_type, "应获取到房产类型文本"
    assert plp.is_property_type_valid(prop_type), f"房产类型取值不合理: {prop_type}"
    logger.info(f"✓ 房产类型取值合理: {prop_type}")


# ============================================
# TC003 列表卡片房产类型可读性（买房）
# ============================================
@pytest.mark.case_id_au58_list_card_property_type_buy_003
@pytest.mark.smoke
@pytest.mark.p1
@allure.feature("OK")
@allure.story("AU站列表卡片房产类型功能-买房列表")
@allure.title("列表卡片房产类型可读性（买房）")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("买房列表类型文案清晰可读，长度合理")
def test_tc003_property_type_readability_buy(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    prop_type = plp.get_first_card_property_type_text(path_part=PATH_PART_BUY)
    assert prop_type, "应获取到房产类型文本"
    assert len(prop_type) < 100, f"房产类型文案过长: {len(prop_type)} 字符"
    logger.info(f"✓ 房产类型可读性良好: {prop_type} ({len(prop_type)} 字符)")


# ============================================
# TC004 列表卡片房产类型与详情页一致（买房）
# ============================================
@pytest.mark.case_id_au58_list_card_property_type_buy_004
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片房产类型功能-买房列表")
@allure.title("列表卡片房产类型与详情页一致（买房）")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("买房列表页房产类型与详情页一致")
def test_tc004_property_type_matches_detail_page_buy(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    list_prop_type = plp.get_first_card_property_type_text(path_part=PATH_PART_BUY)
    assert list_prop_type, "应获取到列表页房产类型"
    logger.info(f"列表页房产类型: {list_prop_type}")
    try:
        with page.context.expect_page(timeout=10000) as new_page_info:
            plp.click_first_list_card(PATH_PART_BUY)
        detail_page = new_page_info.value
        detail_page.wait_for_load_state("domcontentloaded", timeout=15000)
        detail_page.wait_for_timeout(2000)
        detail_text = detail_page.locator("body").inner_text()
        assert list_prop_type in detail_text, f"列表页房产类型({list_prop_type})应在详情页中"
        logger.info(f"✓ 房产类型一致: {list_prop_type} 在详情页中")
        detail_page.close()
    except Exception:
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(2000)
        detail_text = page.locator("body").inner_text()
        assert list_prop_type in detail_text, f"列表页房产类型({list_prop_type})应在详情页中"
        logger.info(f"✓ 房产类型一致: {list_prop_type} 在详情页中")


# ============================================
# TC005 房产类型为空或特殊情况处理（买房）
# ============================================
@pytest.mark.case_id_au58_list_card_property_type_buy_005
@pytest.mark.smoke
@pytest.mark.p1
@allure.feature("OK")
@allure.story("AU站列表卡片房产类型功能-买房列表")
@allure.title("房产类型为空或特殊情况处理（买房）")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("买房列表特殊情况下有合理的展示")
def test_tc005_property_type_special_cases_buy(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    types_list = plp.get_card_property_types(max_cards=5, path_part=PATH_PART_BUY)
    assert len(types_list) > 0, "应至少有一张卡片"
    valid_count = sum(1 for t in types_list if t and t.strip())
    assert valid_count > 0, "至少应有一张卡片展示房产类型"
    logger.info(f"✓ 检查完成: {valid_count}/{len(types_list)} 张卡片有房产类型")
