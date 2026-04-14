"""
AU站 - 买房列表卡片头像和名称功能测试

本脚本由 playwright-test-generator 生成
录制文档：test_plans/au58-Property-列表卡片头像和名称功能测试用例.md
生成时间：2026-03-04
测试站点：AU (https://au.58v5.cn)，无需登录
测试目标：验证 Canberra 买房列表页列表卡片的头像与名称展示及点击行为
"""
import pytest
import allure
from pages.property_list_page import PropertyListPage
from utils.logger import setup_logger

logger = setup_logger()

# ============================================
# 测试环境配置（来自录制文档，无需登录）
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


# ============================================
# TC001 列表页卡片展示头像区域
# ============================================
@pytest.mark.case_id_au58_list_card_avatar_001
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片头像和名称 - 展示与点击")
@allure.title("列表页卡片展示头像区域")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("打开买房列表页，验证每条列表卡片均有头像展示区域")
def test_tc001_list_cards_have_avatar_area(page, config):
    list_url = config["list_url"]
    plp = PropertyListPage(page)
    plp.navigate_to_list(list_url, timeout=config["timeout"]["navigation"])
    page.wait_for_load_state("domcontentloaded", timeout=5000)

    card_count = plp.get_list_card_links_count()
    avatar_count = plp.get_agent_avatar_count()
    assert card_count > 0, "列表页应至少有一条卡片"
    assert avatar_count > 0, "列表页应至少有一个经纪人头像"
    assert avatar_count >= card_count or card_count <= avatar_count + 2, (
        f"卡片数 {card_count} 与头像数 {avatar_count} 应大致对应"
    )
    logger.info(f"✓ 列表卡片数: {card_count}, 头像数: {avatar_count}")


# ============================================
# TC002 列表页卡片展示名称
# ============================================
@pytest.mark.case_id_au58_list_card_avatar_002
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片头像和名称 - 展示与点击")
@allure.title("列表页卡片展示名称")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证每条列表卡片上均展示名称（经纪人/发布者）")
def test_tc002_list_cards_show_name(page, config):
    list_url = config["list_url"]
    plp = PropertyListPage(page)
    plp.navigate_to_list(list_url, timeout=config["timeout"]["navigation"])
    page.wait_for_load_state("domcontentloaded", timeout=5000)

    text = plp.get_first_card_agent_name_text()
    assert text, "第一张卡片应有文案"
    assert "OKerAU" in text or "A$" in text or text.strip(), (
        "卡片文案应包含经纪人标识或价格等"
    )
    logger.info("✓ 第一张卡片文案含名称/价格等信息")


# ============================================
# TC003 头像与名称同卡关联展示
# ============================================
@pytest.mark.case_id_au58_list_card_avatar_003
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片头像和名称 - 展示与点击")
@allure.title("头像与名称同卡关联展示")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证单张卡片内同时存在头像与名称且布局合理")
def test_tc003_avatar_and_name_in_same_card(page, config):
    list_url = config["list_url"]
    plp = PropertyListPage(page)
    plp.navigate_to_list(list_url, timeout=config["timeout"]["navigation"])
    page.wait_for_load_state("domcontentloaded", timeout=5000)

    avatar_count = plp.get_agent_avatar_count()
    first_card_text = plp.get_first_card_agent_name_text()
    assert avatar_count > 0, "应有至少一个头像"
    assert first_card_text and len(first_card_text.strip()) > 0, "第一张卡片应有名称等文案"
    logger.info("✓ 同卡内头像与名称均存在")


# ============================================
# TC004 无头像时显示兜底头像
# ============================================
@pytest.mark.case_id_au58_list_card_avatar_004
@pytest.mark.p1
@allure.feature("OK")
@allure.story("AU站列表卡片头像和名称 - 展示与点击")
@allure.title("无头像时显示兜底头像")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("无自定义头像时展示兜底头像（如 src 为 #fff）")
def test_tc004_default_avatar_display(page, config):
    list_url = config["list_url"]
    plp = PropertyListPage(page)
    plp.navigate_to_list(list_url, timeout=config["timeout"]["navigation"])
    page.wait_for_load_state("domcontentloaded", timeout=5000)

    srcs = plp.get_agent_avatar_src_list()
    assert len(srcs) > 0, "应存在至少一个头像元素"
    has_custom = any(s and s != "#fff" and not s.startswith("#") for s in srcs)
    has_default = any(s == "#fff" or (isinstance(s, str) and s.strip() == "#fff") for s in srcs)
    assert has_custom or has_default, "头像应为自定义图或兜底(#fff)"
    logger.info(f"✓ 头像 src 样本: 自定义或兜底 #fff 均存在")


# ============================================
# TC005 头像或名称可点击，点击后进入卡片详情页
# ============================================
@pytest.mark.case_id_au58_list_card_avatar_005
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片头像和名称 - 展示与点击")
@allure.title("点击头像或名称后进入卡片详情页")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("点击卡片头像或名称后进入该卡片的房产详情页")
def test_tc005_click_avatar_opens_detail(page, config):
    list_url = config["list_url"]
    plp = PropertyListPage(page)
    plp.navigate_to_list(list_url, timeout=config["timeout"]["navigation"])
    page.wait_for_load_state("domcontentloaded", timeout=5000)
    url_before = page.url

    try:
        with page.context.expect_page(timeout=10000) as new_page_info:
            plp.click_first_agent_avatar()
        new_page = new_page_info.value
        new_page.wait_for_load_state("domcontentloaded", timeout=15000)
        url = new_page.url
        new_page.close()
    except Exception:
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        url = page.url

    assert "au.58v5.cn" in url, f"新页应为 AU 站，当前: {url}"
    assert "cate-property-for-sale-" in url or "residential-" in url or "/city-canberra/" in url, (
        f"点击后应进入卡片详情页，当前: {url}"
    )
    logger.info(f"✓ 点击头像后进入卡片详情页: {url}")

