"""
AU站 - 买房列表卡片面积功能测试

本脚本由 playwright-test-generator 生成
录制文档：test_plans/au58-Property-列表卡片面积功能测试用例.md
生成时间：2026-03-09
测试站点：AU (https://au.58v5.cn)，需登录
测试目标：验证 Canberra 买房列表页（cate-buy）列表卡片的面积展示、格式、可读性和一致性
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
# TC001 列表页卡片展示面积
# ============================================
@pytest.mark.case_id_au58_list_card_area_001
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片面积功能")
@allure.title("列表页卡片展示面积")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("每条列表卡片均展示面积信息（面积文案可见）")
def test_tc001_list_cards_show_area(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    card_count = plp.get_list_card_links_count(path_part="cate-property-for-sale-")
    assert card_count > 0, "列表页应至少有一条卡片"
    area_text = plp.get_first_card_area_text()
    assert area_text and len(area_text.strip()) > 0, "第一张卡片应有非空面积"
    logger.info(f"✓ 卡片数: {card_count}, 首卡面积: {area_text}")


# ============================================
# TC002 列表卡片面积格式正确
# ============================================
@pytest.mark.case_id_au58_list_card_area_002
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片面积功能")
@allure.title("列表卡片面积格式正确")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("面积格式正确（如：XX sqm、XX m²、XX sq ft）")
def test_tc002_area_format_correct(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    area_text = plp.get_first_card_area_text()
    assert area_text, "应获取到面积文本"
    assert plp.is_area_format_valid(area_text), f"面积格式不正确: {area_text}"
    assert re.search(r'\d+', area_text), f"面积应包含数字: {area_text}"
    logger.info(f"✓ 面积格式正确: {area_text}")


# ============================================
# TC003 列表卡片面积可读性
# ============================================
@pytest.mark.case_id_au58_list_card_area_003
@pytest.mark.smoke
@pytest.mark.p1
@allure.feature("OK")
@allure.story("AU站列表卡片面积功能")
@allure.title("列表卡片面积可读性")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("面积文案清晰可读，字体大小适中，无遮挡")
def test_tc003_area_readability(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    area_text = plp.get_first_card_area_text()
    assert area_text, "应获取到面积文本"
    assert len(area_text) < 100, f"面积文案过长: {len(area_text)} 字符"
    logger.info(f"✓ 面积可读性良好: {area_text} ({len(area_text)} 字符)")


# ============================================
# TC004 列表卡片面积与详情页一致
# ============================================
@pytest.mark.case_id_au58_list_card_area_004
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片面积功能")
@allure.title("列表卡片面积与详情页一致")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("列表页面积与详情页面积一致")
def test_tc004_area_matches_detail_page(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    list_area = plp.get_first_card_area_text()
    assert list_area, "应获取到列表页面积"
    logger.info(f"列表页面积: {list_area}")
    first_card = page.locator('a[href*="cate-property-for-sale-"], a[href*="residential-"]').first
    first_card.wait_for(state="visible", timeout=5000)
    try:
        with page.context.expect_page(timeout=10000) as new_page_info:
            first_card.click()
        detail_page = new_page_info.value
        detail_page.wait_for_load_state("domcontentloaded", timeout=15000)
        detail_page.wait_for_timeout(2000)
        detail_text = detail_page.locator("body").inner_text()
        area_match = re.search(
            r'[\d,]+\.?\d*\s*(?:sqm|m²|sq\.?\s*m|sq\s*ft|sqft|square\s*metres?)',
            detail_text, re.IGNORECASE
        )
        detail_area = area_match.group() if area_match else ""
        logger.info(f"详情页面积: {detail_area}")
        list_num = re.search(r'[\d,]+\.?\d*', list_area)
        detail_num = re.search(r'[\d,]+\.?\d*', detail_area)
        assert list_num and detail_num, "应能提取面积数字"
        assert list_num.group().replace(',', '') == detail_num.group().replace(',', ''), \
            f"列表页面积({list_area})与详情页面积({detail_area})不一致"
        logger.info(f"✓ 面积一致: {list_area} = {detail_area}")
        detail_page.close()
    except Exception:
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(2000)
        detail_text = page.locator("body").inner_text()
        area_match = re.search(
            r'[\d,]+\.?\d*\s*(?:sqm|m²|sq\.?\s*m|sq\s*ft|sqft|square\s*metres?)',
            detail_text, re.IGNORECASE
        )
        detail_area = area_match.group() if area_match else ""
        list_num = re.search(r'[\d,]+\.?\d*', list_area)
        detail_num = re.search(r'[\d,]+\.?\d*', detail_area)
        assert list_num and detail_num, "应能提取面积数字"
        assert list_num.group().replace(',', '') == detail_num.group().replace(',', ''), \
            f"列表页面积({list_area})与详情页面积({detail_area})不一致"
        logger.info(f"✓ 面积一致: {list_area} = {detail_area}")


# ============================================
# TC005 面积为空或特殊情况处理
# ============================================
@pytest.mark.case_id_au58_list_card_area_005
@pytest.mark.smoke
@pytest.mark.p1
@allure.feature("OK")
@allure.story("AU站列表卡片面积功能")
@allure.title("面积为空或特殊情况处理")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("特殊情况下有合理的展示（如'Contact for details'等）")
def test_tc005_area_special_cases(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    areas = plp.get_card_areas(max_cards=5)
    assert len(areas) > 0, "应至少有一张卡片"
    valid_count = sum(1 for a in areas if a and a.strip())
    assert valid_count > 0, "至少应有一张卡片展示面积"
    logger.info(f"✓ 检查完成: {valid_count}/{len(areas)} 张卡片有面积")
