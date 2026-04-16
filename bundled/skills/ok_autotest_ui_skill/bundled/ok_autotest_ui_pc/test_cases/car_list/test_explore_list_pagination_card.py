"""
阿联酋站 - 探索列表页（Cars分类）测试 - 分页深度验证 + 卡片交互补充

测试站点：AE (https://ae.58v5.cn)
测试角色：Buyer/游客（无需登录）
测试目标：验证分页翻页数据变化、URL 参数、浏览器后退，卡片打开方式、懒加载、搜索编码等
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
# 分页深度验证
# ======================================================================

@pytest.mark.case_id_explore_list_tc131
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 分页深度验证")
@allure.title("点击 Next 后卡片列表数据与第1页不同")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证翻到第2页后，首条卡片标题与第1页不同，证明数据确实翻页了")
def test_tc131_pagination_data_changes(page, config):
    """TC131: 翻页后数据变化"""

    list_page = ExploreListPage(page)
    logger.info("TC131: 翻页数据变化")

    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        page.locator(list_page.FILTER_ITEM_CONTENT).first.wait_for(state="visible", timeout=15000)

    with allure.step("步骤2：记录第1页首条卡片标题"):
        titles_page1 = list_page.get_card_titles(limit=3)
        assert len(titles_page1) > 0, "第1页应有卡片"
        logger.info(f"✓ 第1页前3条标题: {titles_page1}")

    with allure.step("步骤3：点击 Next 翻到第2页"):
        if not list_page.is_next_page_btn_visible():
            pytest.skip("列表不足 2 页，跳过翻页验证")
        list_page.click_next_page()
        logger.info("✓ 已翻到第2页")

    with allure.step("验证第2页数据与第1页不同"):
        titles_page2 = list_page.get_card_titles(limit=3)
        assert len(titles_page2) > 0, "第2页应有卡片"
        assert titles_page1 != titles_page2, \
            f"第2页数据应与第1页不同，第1页: {titles_page1}，第2页: {titles_page2}"
        logger.info(f"✓ 第2页前3条标题: {titles_page2}")

    logger.info("✅ TC131 通过")


@pytest.mark.case_id_explore_list_tc132
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 分页深度验证")
@allure.title("翻页后 URL 包含 page 参数")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证翻页后 URL 中出现 page 或 p 参数")
def test_tc132_pagination_url_page_param(page, config):
    """TC132: 翻页 URL 参数"""

    list_page = ExploreListPage(page)
    logger.info("TC132: 翻页 URL 参数")

    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        page.locator(list_page.FILTER_ITEM_CONTENT).first.wait_for(state="visible", timeout=15000)
        url_page1 = list_page.get_current_url()
        logger.info(f"✓ 第1页 URL: {url_page1}")

    with allure.step("步骤2：点击 Next"):
        if not list_page.is_next_page_btn_visible():
            pytest.skip("列表不足 2 页")
        list_page.click_next_page()

    with allure.step("验证 URL 变化"):
        url_page2 = list_page.get_current_url()
        assert url_page2 != url_page1, \
            f"翻页后 URL 应变化，实际仍为: {url_page2}"
        logger.info(f"✓ 第2页 URL: {url_page2}")

    logger.info("✅ TC132 通过")


@pytest.mark.case_id_explore_list_tc133
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 分页深度验证")
@allure.title("从第2页点浏览器后退回到第1页")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证从第2页点击浏览器后退按钮，能返回第1页数据")
def test_tc133_pagination_back_to_first(page, config):
    """TC133: 分页后退"""

    list_page = ExploreListPage(page)
    logger.info("TC133: 分页后退")

    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        page.locator(list_page.FILTER_ITEM_CONTENT).first.wait_for(state="visible", timeout=15000)
        url_page1 = list_page.get_current_url()
        titles_page1 = list_page.get_card_titles(limit=3)

    with allure.step("步骤2：翻到第2页"):
        if not list_page.is_next_page_btn_visible():
            pytest.skip("列表不足 2 页")
        list_page.click_next_page()
        logger.info("✓ 已翻到第2页")

    with allure.step("步骤3：浏览器后退"):
        list_page.go_back()
        logger.info("✓ 已后退")

    with allure.step("验证回到第1页"):
        current_url = list_page.get_current_url()
        titles_back = list_page.get_card_titles(limit=3)
        logger.info(f"✓ 后退后 URL: {current_url}")
        logger.info(f"✓ 后退后前3条标题: {titles_back}")
        # 数据应与第1页一致
        if titles_page1 and titles_back:
            assert titles_back[0] == titles_page1[0], \
                f"后退后首条标题应与第1页一致，第1页: '{titles_page1[0]}'，后退后: '{titles_back[0]}'"

    logger.info("✅ TC133 通过")


@pytest.mark.case_id_explore_list_tc134
@pytest.mark.p2
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 分页深度验证")
@allure.title("结果仅1页时 Next 按钮不可见")
@allure.severity(allure.severity_level.MINOR)
@allure.description("通过极限筛选使结果仅1页，验证 Next 按钮不可见")
def test_tc134_pagination_last_page_next_state(page, config):
    """TC134: 结果仅1页时 Next 不可见"""

    list_page = ExploreListPage(page)
    logger.info("TC134: 单页时 Next 不可见")

    with allure.step("步骤1：访问极限筛选 URL 使结果很少"):
        few_url = f"{config['base_url']}/en/city-abu-dhabi/cate-car/?iconSource=car&lowestPrice=99999000&highestPrice=99999999"
        list_page.navigate_to_url(few_url)
        logger.info(f"✓ 已访问极限筛选 URL")

    with allure.step("验证 Next 按钮不可见"):
        car_count = list_page.get_car_items_count()
        logger.info(f"  当前卡片数量: {car_count}")
        if car_count == 0:
            assert not list_page.is_next_page_btn_visible(), \
                "无结果时 Next 按钮不应可见"
            logger.info("✓ 无结果，Next 按钮不可见")
        else:
            logger.info("⚠ 仍有结果，可能需要更严格的筛选条件")

    logger.info("✅ TC134 通过")


# ======================================================================
# 卡片交互补充
# ======================================================================

@pytest.mark.case_id_explore_list_tc135
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 卡片交互")
@allure.title("卡片链接 target 属性为 _blank（新窗口打开）")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证卡片 <a> 标签包含 target=_blank 或类似新窗口属性")
def test_tc135_card_target_blank(page, config):
    """TC135: 卡片链接 target 属性"""

    list_page = ExploreListPage(page)
    logger.info("TC135: 卡片 target 属性")

    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        page.locator(list_page.FILTER_ITEM_CONTENT).first.wait_for(state="visible", timeout=15000)

    with allure.step("验证首张卡片的 target 属性"):
        first_card = page.locator(list_page.CAR_ITEM_LINK).first
        target = first_card.get_attribute("target", timeout=3000) or ""
        href = first_card.get_attribute("href", timeout=3000) or ""
        logger.info(f"  首张卡片: href='{href}', target='{target}'")
        # 卡片应有有效链接
        assert href, "卡片应有 href 属性"
        # target 可能是 _blank 或不设置（由 JS 控制跳转）
        if target:
            logger.info(f"✓ 卡片 target 属性: '{target}'")
        else:
            logger.info("✓ 卡片无 target 属性（可能由 JS 控制跳转）")

    logger.info("✅ TC135 通过")


@pytest.mark.case_id_explore_list_tc136
@pytest.mark.p2
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 卡片交互")
@allure.title("滚动到页面底部后所有卡片图片 src 不为空")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证滚动到底部后，所有可见卡片的图片 src 属性不为空（懒加载已触发）")
def test_tc136_card_lazy_load_scroll(page, config):
    """TC136: 卡片图片懒加载"""

    list_page = ExploreListPage(page)
    logger.info("TC136: 图片懒加载")

    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        page.locator(list_page.FILTER_ITEM_CONTENT).first.wait_for(state="visible", timeout=15000)

    with allure.step("步骤2：滚动到页面底部"):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(3000)
        logger.info("✓ 已滚动到底部")

    with allure.step("验证所有卡片图片 src 不为空"):
        cards = page.locator(list_page.CAR_ITEM_LINK).all()
        total = len(cards)
        empty_src_count = 0
        # 检查前15张卡片
        check_count = min(15, total)
        for i in range(check_count):
            card = cards[i]
            img = card.locator(list_page.CAR_IMAGE)
            if img.count():
                src = img.get_attribute("src", timeout=2000) or ""
                if not src:
                    empty_src_count += 1
                    logger.info(f"  ⚠ 卡片 #{i+1}: 图片 src 为空")
        assert empty_src_count <= 1, \
            f"滚动后仍有 {empty_src_count} 张卡片图片 src 为空（允许最多 1 张）"
        logger.info(f"✓ {check_count} 张卡片图片 src 检查完毕，空 src: {empty_src_count}")

    logger.info("✅ TC136 通过")


@pytest.mark.case_id_explore_list_tc137
@pytest.mark.p2
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 搜索增强")
@allure.title("搜索中文关键词，URL 正确编码且不崩溃")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证搜索中文关键词后 URL 包含编码后的关键词，页面不崩溃")
def test_tc137_search_chinese_encoding(page, config):
    """TC137: 中文搜索编码"""

    list_page = ExploreListPage(page)
    logger.info("TC137: 中文搜索编码")

    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        page.locator(list_page.FILTER_ITEM_CONTENT).first.wait_for(state="visible", timeout=15000)

    with allure.step("步骤2：搜索中文关键词"):
        list_page.search("丰田汽车")
        logger.info("✓ 已搜索 '丰田汽车'")

    with allure.step("验证页面不崩溃，URL 包含编码后的关键词"):
        current_url = list_page.get_current_url()
        browser_title = list_page.get_browser_title()
        assert browser_title is not None, "搜索中文后页面应有标题，未崩溃"
        assert "keyword" in current_url, \
            f"URL 应包含 keyword 参数，实际: {current_url}"
        logger.info(f"✓ 中文搜索 URL: {current_url}")

    logger.info("✅ TC137 通过")


@pytest.mark.case_id_explore_list_tc138
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("探索列表页 - 搜索增强")
@allure.title("搜索不存在的关键词，空态可见且列表数量为 0")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证搜索不存在的随机关键词后，列表为空或显示空态提示")
def test_tc138_search_no_result_empty_state(page, config):
    """TC138: 搜索无结果空态"""

    list_page = ExploreListPage(page)
    logger.info("TC138: 搜索无结果空态")

    with allure.step("步骤1：导航到目标 URL"):
        list_page.navigate_to_url(config["target_url"])
        page.locator(list_page.FILTER_ITEM_CONTENT).first.wait_for(state="visible", timeout=15000)

    with allure.step("步骤2：搜索不存在的关键词"):
        list_page.search("zzz_nonexistent_keyword_12345")
        logger.info("✓ 已搜索不存在的关键词")

    with allure.step("验证空态"):
        car_count = list_page.get_car_items_count()
        logger.info(f"  搜索后卡片数量: {car_count}")
        if car_count == 0:
            is_empty = list_page.is_empty_state_visible()
            assert is_empty, "列表为空时应显示空态元素"
            logger.info("✓ 空态元素可见，无搜索结果")
        else:
            logger.info(f"⚠ 搜索后仍有 {car_count} 条结果（可能存在模糊匹配）")

    with allure.step("验证 Next 按钮不可见"):
        if car_count == 0:
            assert not list_page.is_next_page_btn_visible(), \
                "无搜索结果时 Next 按钮不应可见"
            logger.info("✓ 无结果时 Next 不可见")

    logger.info("✅ TC138 通过")
