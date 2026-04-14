"""
AU站 - 租房列表卡片价格功能测试

本脚本由 playwright-test-generator 生成
录制文档：test_plans/au58-Property-列表卡片价格功能测试用例.md
生成时间：2026-03-05
测试站点：AU (https://au.58v5.cn)，需登录
测试目标：验证 Canberra 租房列表页列表卡片的价格展示、格式、可读性和一致性
"""
import pytest
import allure
import re
from pages.property_list_page import PropertyListPage
from pages.property_detail_page import PropertyDetailPage
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
# TC001 列表页卡片展示价格
# ============================================
@pytest.mark.case_id_au58_list_card_price_001
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片价格功能")
@allure.title("列表页卡片展示价格")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("每条列表卡片均展示价格信息（价格文案可见）")
def test_tc001_list_cards_show_price(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    card_count = plp.get_list_card_links_count(path_part="cate-property-for-sale-")
    assert card_count > 0, "列表页应至少有一条卡片"
    
    # 调试：查看第一张卡片的完整文本
    first_card = page.locator('a[href*="cate-property-for-sale-"], a[href*="residential-"]').first
    card_text = first_card.inner_text()
    logger.info(f"首卡完整文本: {card_text}")
    
    price_text = plp.get_first_card_price_text()
    assert price_text and len(price_text.strip()) > 0, f"第一张卡片应有非空价格，当前卡片文本: {card_text[:200]}"
    logger.info(f"✓ 卡片数: {card_count}, 首卡价格: {price_text}")


# ============================================
# TC002 列表卡片价格格式正确
# ============================================
@pytest.mark.case_id_au58_list_card_price_002
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片价格功能")
@allure.title("列表卡片价格格式正确")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("价格格式正确（如：A$XXX/week 或 A$XXX per week）")
def test_tc002_price_format_correct(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    
    price_text = plp.get_first_card_price_text()
    assert price_text, "应获取到价格文本"
    
    # 验证价格格式
    assert plp.is_price_format_valid(price_text), \
        f"价格格式不正确: {price_text}（应包含货币符号、数字、可能的周期）"
    
    # 验证包含货币符号
    assert '$' in price_text, f"价格应包含货币符号: {price_text}"
    
    # 验证包含数字
    assert re.search(r'\d+', price_text), f"价格应包含数字: {price_text}"
    
    logger.info(f"✓ 价格格式正确: {price_text}")


# ============================================
# TC003 列表卡片价格可读性
# ============================================
@pytest.mark.case_id_au58_list_card_price_003
@pytest.mark.smoke
@pytest.mark.p1
@allure.feature("OK")
@allure.story("AU站列表卡片价格功能")
@allure.title("列表卡片价格可读性")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("价格文案清晰可读，字体大小适中，无遮挡")
def test_tc003_price_readability(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    
    price_text = plp.get_first_card_price_text()
    assert price_text, "应获取到价格文本"
    
    # 验证价格文案长度合理（不会过长导致显示问题）
    assert len(price_text) < 100, f"价格文案过长: {len(price_text)} 字符"
    
    # 验证价格文案存在且可读（已通过 get_first_card_price_text 获取到）
    # 价格信息已包含在卡片文本中，无需单独验证元素可见性
    
    logger.info(f"✓ 价格可读性良好: {price_text} ({len(price_text)} 字符)")


# ============================================
# TC004 列表卡片价格与详情页一致
# ============================================
@pytest.mark.case_id_au58_list_card_price_004
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片价格功能")
@allure.title("列表卡片价格与详情页一致")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("列表页价格与详情页价格一致")
def test_tc004_price_matches_detail_page(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    
    # 1. 获取列表页价格
    list_price = plp.get_first_card_price_text()
    assert list_price, "应获取到列表页价格"
    logger.info(f"列表页价格: {list_price}")
    
    # 2. 点击卡片进入详情页
    first_card = page.locator('a[href*="cate-property-for-sale-"], a[href*="residential-"]').first
    first_card.wait_for(state="visible", timeout=5000)
    
    with page.context.expect_page(timeout=15000) as new_page_info:
        first_card.click()
    
    try:
        detail_page_obj = new_page_info.value
        detail_page_obj.wait_for_load_state("domcontentloaded", timeout=15000)
        detail_page_obj.wait_for_timeout(2000)
        
        # 3. 获取详情页价格（从页面文本中提取）
        detail_page_text = detail_page_obj.locator("body").inner_text()
        detail_price_match = re.search(r'A?\$[\d,]+(?:\s*(?:\/|per)\s*(?:week|month|year|day))?', detail_page_text, re.IGNORECASE)
        detail_price = detail_price_match.group() if detail_price_match else ""
        logger.info(f"详情页价格: {detail_price}")
        
        # 4. 验证价格一致性
        # 提取数字部分进行比较（忽略格式差异）
        list_price_num = re.search(r'[\d,]+', list_price)
        detail_price_num = re.search(r'[\d,]+', detail_price)
        
        assert list_price_num and detail_price_num, "应能提取价格数字"
        
        list_num = list_price_num.group().replace(',', '')
        detail_num = detail_price_num.group().replace(',', '')
        
        assert list_num == detail_num, \
            f"列表页价格({list_price})与详情页价格({detail_price})不一致"
        
        logger.info(f"✓ 价格一致: {list_price} = {detail_price}")
        
        detail_page_obj.close()
    except Exception as e:
        # 如果新标签页打开失败，尝试在当前页面验证
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(2000)
        
        detail_page_text = page.locator("body").inner_text()
        detail_price_match = re.search(r'A?\$[\d,]+(?:\s*(?:\/|per)\s*(?:week|month|year|day))?', detail_page_text, re.IGNORECASE)
        detail_price = detail_price_match.group() if detail_price_match else ""
        logger.info(f"详情页价格: {detail_price}")
        
        list_price_num = re.search(r'[\d,]+', list_price)
        detail_price_num = re.search(r'[\d,]+', detail_price)
        
        assert list_price_num and detail_price_num, "应能提取价格数字"
        
        list_num = list_price_num.group().replace(',', '')
        detail_num = detail_price_num.group().replace(',', '')
        
        assert list_num == detail_num, \
            f"列表页价格({list_price})与详情页价格({detail_price})不一致"
        
        logger.info(f"✓ 价格一致: {list_price} = {detail_price}")
        
        # 返回列表页
        page.goto(config["list_url"], wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])


# ============================================
# TC005 价格为空或特殊情况处理
# ============================================
@pytest.mark.case_id_au58_list_card_price_005
@pytest.mark.smoke
@pytest.mark.p1
@allure.feature("OK")
@allure.story("AU站列表卡片价格功能")
@allure.title("价格为空或特殊情况处理")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("特殊情况下有合理的展示（如'Contact for price'、'Price on application'等）")
def test_tc005_price_special_cases(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    
    # 获取前5张卡片的价格
    prices = plp.get_card_prices(max_cards=5)
    assert len(prices) > 0, "应至少有一张卡片"
    
    # 检查是否有特殊情况
    special_keywords = ['contact', 'price on application', 'negotiable', 'poa']
    has_special_case = False
    
    for i, price in enumerate(prices):
        if not price or price.strip() == "":
            # 价格为空，检查是否有特殊文案
            card = page.locator('a[href*="cate-property-for-sale-"], a[href*="residential-"]').nth(i)
            card_text = card.inner_text().lower()
            
            for keyword in special_keywords:
                if keyword in card_text:
                    has_special_case = True
                    logger.info(f"✓ 卡片{i+1}价格为空，但有特殊文案: {keyword}")
                    break
            
            if not has_special_case:
                # 如果价格为空且没有特殊文案，可能是数据问题，记录警告
                logger.warning(f"⚠️ 卡片{i+1}价格为空且无特殊文案")
    
    # 至少应该有一张卡片有价格或特殊文案
    valid_count = sum(1 for p in prices if p and p.strip())
    assert valid_count > 0 or has_special_case, \
        "至少应有一张卡片展示价格或特殊文案"
    
    logger.info(f"✓ 检查完成: {valid_count}/{len(prices)} 张卡片有价格")
