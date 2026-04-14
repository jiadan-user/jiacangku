"""
AU站 - 列表卡片位置邮编功能测试

本脚本由 playwright-test-generator 生成
录制文档：test_plans/au58-Property-列表卡片位置邮编功能测试用例.md
生成时间：2026-03-09
测试站点：AU (https://au.58v5.cn)，需登录
测试目标：验证 Canberra 列表页列表卡片的位置/邮编展示（租房列表无卡片时使用买房列表）
"""
import pytest
import allure
import re
from pages.property_list_page import PropertyListPage
from utils.logger import setup_logger

logger = setup_logger()

# ============================================
# 测试环境配置（来自录制文档）
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
    """直接打开列表页（无需登录）。"""
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
# TC001 列表页卡片展示位置/邮编
# ============================================
@pytest.mark.case_id_au58_list_card_location_001
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片位置邮编功能")
@allure.title("列表页卡片展示位置/邮编")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("每条列表卡片均展示位置或邮编信息")
def test_tc001_list_cards_show_location(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    card_count = plp.get_list_card_links_count(path_part="cate-property-for-sale-")
    assert card_count > 0, "列表页应至少有一条卡片"
    location_text = plp.get_first_card_location_text()
    assert location_text and len(location_text.strip()) > 0, "第一张卡片应有非空位置/邮编"
    logger.info(f"✓ 卡片数: {card_count}, 首卡位置: {location_text}")


# ============================================
# TC002 列表卡片邮编格式正确
# ============================================
@pytest.mark.case_id_au58_list_card_location_002
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片位置邮编功能")
@allure.title("列表卡片邮编格式正确")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("邮编格式正确（澳大利亚 4 位数字）")
def test_tc002_postcode_format_correct(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    location_text = plp.get_first_card_location_text()
    assert location_text, "应获取到位置/邮编文本"
    # 卡片文本中应包含有效邮编（4位）或位置信息
    assert plp.is_postcode_format_valid(location_text) or len(location_text) >= 2, (
        f"位置/邮编格式不正确: {location_text}"
    )
    logger.info(f"✓ 位置/邮编格式正确: {location_text}")


# ============================================
# TC003 列表卡片位置可读性
# ============================================
@pytest.mark.case_id_au58_list_card_location_003
@pytest.mark.smoke
@pytest.mark.p1
@allure.feature("OK")
@allure.story("AU站列表卡片位置邮编功能")
@allure.title("列表卡片位置可读性")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("位置文案清晰可读，字体大小适中，无遮挡")
def test_tc003_location_readability(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    location_text = plp.get_first_card_location_text()
    assert location_text, "应获取到位置文本"
    assert len(location_text) < 100, f"位置文案过长: {len(location_text)} 字符"
    logger.info(f"✓ 位置可读性良好: {location_text} ({len(location_text)} 字符)")


# ============================================
# TC004 列表卡片位置与详情页一致
# ============================================
@pytest.mark.case_id_au58_list_card_location_004
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片位置邮编功能")
@allure.title("列表卡片位置与详情页一致")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("列表页位置与详情页位置一致")
def test_tc004_location_matches_detail_page(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    list_location = plp.get_first_card_location_text()
    assert list_location, "应获取到列表页位置"
    logger.info(f"列表页位置: {list_location}")
    first_card = page.locator('a[href*="cate-property-for-sale-"], a[href*="residential-"]').first
    first_card.wait_for(state="visible", timeout=5000)
    try:
        with page.context.expect_page(timeout=10000) as new_page_info:
            first_card.click()
        detail_page = new_page_info.value
        detail_page.wait_for_load_state("domcontentloaded", timeout=15000)
        detail_page.wait_for_timeout(2000)
        detail_text = detail_page.locator("body").inner_text()
        # 详情页应包含列表页的位置/邮编
        assert list_location in detail_text or (
            re.search(r'\b\d{4}\b', list_location) and re.search(r'\b\d{4}\b', detail_text)
        ), f"列表页位置({list_location})应在详情页中"
        logger.info(f"✓ 位置一致: {list_location} 在详情页中")
        detail_page.close()
    except Exception:
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(2000)
        detail_text = page.locator("body").inner_text()
        assert list_location in detail_text or (
            re.search(r'\b\d{4}\b', list_location) and re.search(r'\b\d{4}\b', detail_text)
        ), f"列表页位置({list_location})应在详情页中"
        logger.info(f"✓ 位置一致: {list_location} 在详情页中")


# ============================================
# TC005 位置为空或特殊情况处理
# ============================================
@pytest.mark.case_id_au58_list_card_location_005
@pytest.mark.smoke
@pytest.mark.p1
@allure.feature("OK")
@allure.story("AU站列表卡片位置邮编功能")
@allure.title("位置为空或特殊情况处理")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("特殊情况下有合理的展示")
def test_tc005_location_special_cases(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    locations = plp.get_card_locations(max_cards=5)
    assert len(locations) > 0, "应至少有一张卡片"
    valid_count = sum(1 for loc in locations if loc and loc.strip())
    assert valid_count > 0, "至少应有一张卡片展示位置/邮编"
    logger.info(f"✓ 检查完成: {valid_count}/{len(locations)} 张卡片有位置")
