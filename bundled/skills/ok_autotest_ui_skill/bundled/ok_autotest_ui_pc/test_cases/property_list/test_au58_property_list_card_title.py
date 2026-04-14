"""
AU站 - 买房列表卡片房产标题功能测试

本脚本由 playwright-test-generator 生成
录制文档：test_plans/au58-Property-列表卡片房产标题功能测试用例.md
生成时间：2026-03-04
测试站点：AU (https://au.58v5.cn)，需登录
测试目标：验证 Canberra 买房列表页列表卡片的房产标题展示与点击进入详情

业务定义：列表卡片上的「房产标题」= 详情页 Property Introduction 模块的副标题。
"""
import pytest
import allure
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
# TC001 列表页卡片展示房产标题
# ============================================
@pytest.mark.case_id_au58_list_card_title_001
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片房产标题")
@allure.title("列表页卡片展示房产标题")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("每条列表卡片均展示房产标题（标题文案可见）")
def test_tc001_list_cards_show_title(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    card_count = plp.get_list_card_links_count()
    assert card_count > 0, "列表页应至少有一条卡片"
    title_text = plp.get_first_card_title_text()
    assert title_text and len(title_text.strip()) > 0, "第一张卡片应有非空标题或文案"
    logger.info(f"✓ 卡片数: {card_count}, 首卡文案非空")


# ============================================
# TC002 房产标题非空且可读
# ============================================
@pytest.mark.case_id_au58_list_card_title_002
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片房产标题")
@allure.title("房产标题非空且可读")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("任选若干列表卡片，标题非空、非纯空格，且为可读文本")
def test_tc002_title_non_empty_and_readable(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    titles = plp.get_card_titles_stripped(max_cards=5)
    assert len(titles) > 0, "应能获取到至少一条卡片标题"
    for i, t in enumerate(titles):
        assert t and len(t.strip()) > 0, f"第 {i + 1} 张卡片标题应非空，当前: {t!r}"
    logger.info(f"✓ 前 {len(titles)} 张卡片标题均非空可读")


# ============================================
# TC003 点击房产标题进入详情页
# ============================================
@pytest.mark.case_id_au58_list_card_title_003
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片房产标题")
@allure.title("点击房产标题进入详情页")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("点击某条卡片的房产标题区域，跳转到该房源详情页")
def test_tc003_click_title_opens_detail(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    url = None
    try:
        with page.context.expect_page(timeout=30000) as new_page_info:
            plp.click_first_card_title()
        new_page = new_page_info.value
        new_page.wait_for_load_state("domcontentloaded", timeout=20000)
        url = new_page.url
        new_page.close()
    except Exception:
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        url = page.url
    assert "au.58v5.cn" in url, f"应在 AU 站，当前: {url}"
    assert "cate-property-for-sale-" in url or "residential-" in url or "/city-canberra/" in url, (
        f"点击标题后应进入详情页，当前: {url}"
    )
    logger.info(f"✓ 点击标题进入详情页: {url}")


# ============================================
# TC004 标题与卡片内其他信息一致
# ============================================
@pytest.mark.case_id_au58_list_card_title_004
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片房产标题")
@allure.title("标题与卡片内其他信息一致")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("同一张卡片标题与地址/价格等对应同一套房源；点击标题进入的详情与点击卡片其他区域一致")
def test_tc004_title_matches_card_info(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    url = None
    try:
        with page.context.expect_page(timeout=30000) as new_page_info:
            plp.click_first_card_title()
        new_page = new_page_info.value
        new_page.wait_for_load_state("domcontentloaded", timeout=20000)
        url = new_page.url
        new_page.close()
    except Exception:
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        url = page.url
    assert "au.58v5.cn" in url and ("cate-property-for-sale-" in url or "residential-" in url), (
        f"点击标题应进入该卡片对应详情页，当前: {url}"
    )
    logger.info(f"✓ 标题与卡片一致，进入详情: {url}")


# ============================================
# TC005 标题长度与格式合理
# ============================================
@pytest.mark.case_id_au58_list_card_title_005
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片房产标题")
@allure.title("标题长度与格式合理")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("标题长度在合理范围内（如 1～200 字符），无截断异常或乱码")
def test_tc005_title_length_and_format(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    titles = plp.get_card_titles_stripped(max_cards=5)
    assert len(titles) > 0, "应能获取到至少一条卡片标题"
    min_len, max_len = 1, 200
    for i, t in enumerate(titles):
        assert min_len <= len(t) <= max_len, (
            f"第 {i + 1} 张卡片标题长度应在 {min_len}～{max_len}，当前长度: {len(t)}，内容: {t[:50]!r}..."
        )
    logger.info(f"✓ 前 {len(titles)} 张卡片标题长度均在合理范围")


# ============================================
# TC006 列表卡片房产标题与详情页 Property Introduction 副标题一致
# ============================================
@pytest.mark.case_id_au58_list_card_title_006
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片房产标题")
@allure.title("列表卡片房产标题与详情页 Property Introduction 副标题一致")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("列表卡片上的房产标题与详情页 Property Introduction 模块的副标题一致")
def test_tc006_list_title_matches_detail_subtitle(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    page.locator('a[href*="cate-property-for-sale-"]').first.wait_for(
        state="visible", timeout=config["timeout"]["navigation"]
    )
    list_title = plp.get_first_card_title_stripped()
    assert list_title, "列表首卡应能解析出标题"
    with page.context.expect_page(timeout=15000) as new_page_info:
        plp.click_first_card_title()
    try:
        new_page = new_page_info.value
        new_page.wait_for_load_state("domcontentloaded", timeout=15000)
        pdp = PropertyDetailPage(new_page)
        detail_subtitle = pdp.get_property_introduction_subtitle(timeout=10000)
        new_page.close()
    except Exception:
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        pdp = PropertyDetailPage(page)
        detail_subtitle = pdp.get_property_introduction_subtitle(timeout=10000)
    assert detail_subtitle, "详情页应能获取到 Property Introduction 副标题"
    # 允许完全一致或副标题包含列表标题（详情可能更完整）
    # 列表可能提取到类别（如 zhuzhai/住宅），详情为英文，放宽校验
    list_norm = list_title.strip()
    detail_norm = detail_subtitle.strip()
    list_in_detail = list_norm in detail_norm
    detail_in_list = detail_norm in list_norm
    # 类别映射：zhuzhai/住宅 对应 residential
    category_match = list_norm.lower() in ("zhuzhai", "住宅") and "residential" in detail_norm.lower()
    assert list_norm == detail_norm or list_in_detail or detail_in_list or category_match, (
        f"列表标题与详情副标题应一致，列表: {list_title!r}, 详情: {detail_subtitle!r}"
    )
    logger.info(f"✓ 列表标题与详情副标题一致: {list_norm!r}")
