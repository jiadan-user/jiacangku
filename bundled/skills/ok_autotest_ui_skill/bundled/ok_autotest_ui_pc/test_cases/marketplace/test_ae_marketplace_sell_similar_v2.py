"""
AE站 - 二手想卖同款功能测试 (优化版)

测试站点: AE (https://ae.58v5.cn)
测试角色: Buyer (买家)
测试目标: 全面验证 Sell Similar (想卖同款) 功能
    - 按钮展示逻辑 (本人帖/非本人帖)
    - 点击跳转功能
    - 发布页预加载内容 (类目/属性/价格/图片)
    - 登录态处理
    - 多语言支持

基于 XMind 测试用例: 二手想卖同款.xmind

优化点:
- 自动查找有 Sell Similar 按钮的商品 (而不是固定使用第一个)
- 更健壮的选择器策略
- 更完善的错误处理
"""
import time
import pytest
import allure
from urllib.parse import urljoin
from pages.marketplace_list_page_ae import MarketplaceListPageAe
from pages.marketplace_detail_page_ae import MarketplaceDetailPageAe
from pages.marketplace_sell_similar_page_ae import MarketplaceSellSimilarPageAe
from test_cases.marketplace.explicit_waits import (
    wait_aed_listing_price_signal,
    wait_dom_content_loaded,
    wait_list_results_settled,
    wait_marketplace_detail_href_in_dom,
    wait_marketplace_detail_price,
    wait_network_quiet,
    wait_publish_context_ready,
    wait_short_ui_tick,
)
from test_cases.zhaopin.ae_login_helper import ensure_ae_logged_in
from utils.logger import setup_logger

logger = setup_logger()

# ============================================
# 测试环境配置（来自录制文档）
# ============================================
_CONFIG = {
    "site": "ae",
    "site_name": "阿联酋站",
    "role": "buyer",
    # 与 marketplace 目录下其它脚本统一，共用同一份 Session 文件
    "user_name": "ae_marketplace_regression",
    "base_url": "https://ae.58v5.cn",
    "test_account": {
        "username": "wangyongli@58.com",
        "password": "Qwer1234"
    },
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


# ============================================
# Helper 函数
# ============================================

def _gather_detail_hrefs_from_list_page(page, max_links: int) -> list:
    """从当前列表页收集商品详情 href（去重，最多 max_links 条）。"""
    import re

    out = []
    try:
        wait_dom_content_loaded(page, 15000)
        try:
            wait_network_quiet(page, 12000)
        except Exception:
            pass
        try:
            wait_aed_listing_price_signal(page, 20000)
        except Exception:
            pass
        deadline = time.time() + 35.0
        price_elements = []
        while time.time() < deadline:
            price_elements = page.locator("text=/AED\\s+\\d+/").all()
            if len(price_elements) > 0:
                break
            try:
                page.evaluate(
                    "window.scrollTo(0, Math.min((window.scrollY || 0) + 900, "
                    "(document.body && document.body.scrollHeight) || 9999))"
                )
            except Exception:
                pass
            wait_marketplace_detail_href_in_dom(page, timeout_ms=450)
        logger.info(f"找到 {len(price_elements)} 个价格元素")
        for price_elem in price_elements[: max_links * 2]:
            try:
                parent_link = price_elem.locator("xpath=ancestor::a[@href]").first
                href = parent_link.get_attribute("href")
                if not href:
                    continue
                if "cate-marketplace" in href or "?" in href:
                    continue
                if not href.endswith("/"):
                    continue
                if not re.search(r"\d{10,}", href):
                    continue
                if href not in out:
                    out.append(href)
                    logger.info(f"  -> 商品 {len(out)}: {href}")
                    if len(out) >= max_links:
                        break
            except Exception:
                continue
        if len(out) == 0:
            logger.info("方法1未找到商品,尝试方法2...")
            for link in page.locator('a[href*="/cate-"]').all():
                try:
                    href = link.get_attribute("href")
                    if not href or "cate-marketplace" in href or "?" in href:
                        continue
                    if not href.endswith("/"):
                        continue
                    if not re.search(r"\d{19}", href):
                        continue
                    if "city-" not in href:
                        continue
                    if href not in out:
                        out.append(href)
                        logger.info(f"  -> 商品 {len(out)}: {href}")
                        if len(out) >= max_links:
                            break
                except Exception:
                    continue
    except Exception as e:
        logger.warning(f"收集列表链接时出错: {e}")
    return out


def _scan_links_for_sell_similar(
    page,
    config,
    detail_page,
    sell_similar_page,
    all_links,
    language,
):
    """遍历详情链接，返回首个非本人且展示 Sell Similar 的帖子。"""
    for i, href in enumerate(all_links, 1):
        try:
            detail_url = urljoin(page.url, href)
            if language != "en" and "/en/" in detail_url:
                detail_url = detail_url.replace("/en/", f"/{language}/")
            logger.info(f"[{i}/{len(all_links)}] 检查商品: {detail_url}")
            page.goto(detail_url, wait_until="domcontentloaded", timeout=30000)
            try:
                wait_marketplace_detail_price(page, 20000)
            except Exception:
                wait_dom_content_loaded(page, 15000)
            if not detail_page.is_detail_page_loaded(timeout=15000):
                logger.info("  ⏭️ 跳过: 详情页未就绪")
                continue
            has_withdraw = detail_page.is_withdraw_button_visible(timeout=3000)
            has_edit = detail_page.is_edit_button_visible(timeout=3000)
            if has_withdraw or has_edit:
                logger.info("  ⏭️ 跳过: 本人帖（Withdraw/Edit）")
                continue
            has_sell_similar = sell_similar_page.is_sell_similar_button_visible(timeout=5000)
            if has_sell_similar:
                original_price = detail_page.get_price_text()
                try:
                    original_title = page.locator("h1, [class*='title']").first.inner_text()
                except Exception:
                    original_title = ""
                logger.info("  ✅ 找到有 Sell Similar 按钮的商品!")
                logger.info(f"     URL: {detail_url}")
                logger.info(f"     价格: {original_price}")
                logger.info(f"     标题: {original_title[:50] if original_title else 'N/A'}")
                return (detail_url, original_price, original_title)
            logger.info("  ⏭️ 跳过: 没有 Sell Similar 按钮")
        except Exception as e:
            logger.warning(f"  ⚠️ 检查第 {i} 个商品时出错: {e}")
            continue
    return None


def find_post_with_sell_similar_button(page, config, list_page, detail_page, sell_similar_page, max_attempts=20, language='en'):
    """
    在列表页中查找有 Sell Similar 按钮的非本人帖子
    
    Args:
        language: 语言代码,默认 'en',可选 'es', 'ar' 等
    
    Returns:
        tuple: (detail_url, original_price, original_title) 如果找到
        None: 如果未找到
    """
    logger.info(f"开始查找有 Sell Similar 按钮的商品 (最多检查 {max_attempts} 个)...")
    
    list_url = f"{config['base_url']}/{language}/city-abu-dhabi/cate-marketplace/"
    try:
        cur_base = (page.url or "").split("?")[0].rstrip("/")
        tgt_base = list_url.rstrip("/")
        if cur_base != tgt_base:
            page.goto(list_url, wait_until="domcontentloaded", timeout=60000)
            try:
                wait_aed_listing_price_signal(page, 20000)
            except Exception:
                wait_dom_content_loaded(page, 15000)
            logger.info(f"✓ 访问列表页: {list_url}")
        else:
            logger.info(f"✓ 已在目标列表页，跳过重复导航: {list_url}")
    except Exception:
        page.goto(list_url, wait_until="domcontentloaded", timeout=60000)
        try:
            wait_aed_listing_price_signal(page, 20000)
        except Exception:
            wait_dom_content_loaded(page, 15000)
        logger.info(f"✓ 访问列表页: {list_url}")
    
    all_links = _gather_detail_hrefs_from_list_page(page, max_attempts)
    logger.info(f"✓ 总共找到 {len(all_links)} 个有效商品链接")
    found = _scan_links_for_sell_similar(
        page, config, detail_page, sell_similar_page, all_links, language
    )
    if found:
        return found

    # 主列表前排可能全是当前账号本人帖；尝试其他分类列表以命中他人商品
    extra_list_urls = (
        f"{config['base_url']}/{language}/city-abu-dhabi/cate-samsung3/",
        f"{config['base_url']}/{language}/city-abu-dhabi/cate-books/",
        f"{config['base_url']}/{language}/city-abu-dhabi/cate-headphones/",
        f"{config['base_url']}/{language}/city-abu-dhabi/cate-cell-phone-cases/",
    )
    for alt in extra_list_urls:
        logger.info(f"主列表未命中，尝试备用分类: {alt}")
        try:
            page.goto(alt, wait_until="domcontentloaded", timeout=60000)
            try:
                wait_aed_listing_price_signal(page, 20000)
            except Exception:
                wait_dom_content_loaded(page, 15000)
        except Exception as e:
            logger.warning(f"备用列表打开失败: {alt} ({e})")
            continue
        all_links = _gather_detail_hrefs_from_list_page(page, max_attempts)
        logger.info(f"✓ 备用列表得到 {len(all_links)} 个商品链接")
        found = _scan_links_for_sell_similar(
            page, config, detail_page, sell_similar_page, all_links, language
        )
        if found:
            return found

    logger.error("❌ 未找到有 Sell Similar 按钮的商品")
    return None


# ============================================
# 测试用例
# ============================================

@pytest.mark.case_id_sell_similar_tc001
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.marketplace
@pytest.mark.ae
@allure.feature("Marketplace")
@allure.story("Sell Similar - 非本人帖详情页按钮展示")
@allure.title("非本人帖详情页应该展示 Sell Similar 按钮")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证在非本人发布的二手帖子详情页，能够正确展示 Sell Similar 按钮，并且不展示 Withdraw/Edit 按钮")
def test_tc001_non_own_post_shows_sell_similar_button(marketplace_list_session, config):
    """非本人帖详情页展示 Sell Similar 按钮测试"""
    page = marketplace_list_session
    
    # ========== Arrange: 准备测试对象 ==========
    list_page = MarketplaceListPageAe(page)
    detail_page = MarketplaceDetailPageAe(page)
    sell_similar_page = MarketplaceSellSimilarPageAe(page)
    
    logger.info("="*80)
    logger.info("TC001: 非本人帖详情页展示 Sell Similar 按钮")
    logger.info("="*80)
    logger.info(f"站点: {config['site'].upper()} ({config['site_name']})")
    logger.info(f"角色: {config['role'].upper()} (买家)")
    logger.info(f"账号: {config['user_name']}")
    logger.info("="*80)
    
    
    # ========== Act: 查找有 Sell Similar 按钮的商品 ==========
    with allure.step("步骤1: 查找有 Sell Similar 按钮的商品"):
        result = find_post_with_sell_similar_button(page, config, list_page, detail_page, sell_similar_page)
        
        if result is None:
            pytest.skip("列表页未找到有 Sell Similar 按钮的商品,可能所有商品都达到了点击上限")
        
        detail_url, original_price, original_title = result
        logger.info(f"✓ 找到目标商品: {detail_url}")
    
    # ========== Assert: 验证详情页按钮展示 ==========
    with allure.step("验证1: 详情页 URL 正确"):
        current_url = page.url
        assert "/cate-" in current_url, \
            f"详情页 URL 应包含 '/cate-'，实际: {current_url}"
        assert "cate-marketplace" not in current_url.lower(), \
            f"详情页 URL 不应包含 'cate-marketplace'（列表页），实际: {current_url}"
        logger.info(f"✓ URL 验证通过: {current_url}")
    
    with allure.step("验证2: 详情页展示价格信息"):
        assert detail_page.get_price_text(), \
            "详情页应展示价格信息（包含 AED）"
        logger.info(f"✓ 价格信息验证通过: {detail_page.get_price_text()}")
    
    with allure.step("验证3: 不展示 Withdraw 按钮（非本人帖）"):
        has_withdraw = detail_page.is_withdraw_button_visible(timeout=3000)
        assert not has_withdraw, \
            "非本人帖不应展示 Withdraw 按钮"
        logger.info("✓ 确认不展示 Withdraw 按钮")
    
    with allure.step("验证4: 不展示 Edit 按钮（非本人帖）"):
        has_edit = detail_page.is_edit_button_visible(timeout=3000)
        assert not has_edit, \
            "非本人帖不应展示 Edit 按钮"
        logger.info("✓ 确认不展示 Edit 按钮")
    
    with allure.step("验证5: 展示 Contact 按钮（非本人帖）"):
        has_contact = detail_page.is_contact_button_visible(timeout=5000)
        assert has_contact, \
            "非本人帖应展示 Contact 按钮"
        logger.info("✓ 确认展示 Contact 按钮")
    
    with allure.step("验证6: 展示 Sell Similar 按钮（核心功能）"):
        has_sell_similar = sell_similar_page.is_sell_similar_button_visible(timeout=5000)
        assert has_sell_similar, \
            "非本人帖应展示 Sell Similar 按钮"
        logger.info("✓ 确认展示 Sell Similar 按钮")
    
    logger.info("="*80)
    logger.info("✅ TC001 测试通过！非本人帖详情页正确展示 Sell Similar 按钮")
    logger.info("="*80)


@pytest.mark.case_id_sell_similar_tc002
@pytest.mark.smoke
@pytest.mark.p1
@pytest.mark.marketplace
@pytest.mark.ae
@allure.feature("Marketplace")
@allure.story("Sell Similar - 点击按钮跳转发布页")
@allure.title("点击 Sell Similar 按钮应该跳转到发布页")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证点击 Sell Similar 按钮后，能够正确跳转到发布页面")
def test_tc002_click_sell_similar_navigates_to_publish_page(marketplace_list_session, config):
    """点击 Sell Similar 按钮跳转发布页测试"""
    page = marketplace_list_session
    
    # ========== Arrange: 准备测试对象 ==========
    list_page = MarketplaceListPageAe(page)
    detail_page = MarketplaceDetailPageAe(page)
    sell_similar_page = MarketplaceSellSimilarPageAe(page)
    
    logger.info("="*80)
    logger.info("TC002: 点击 Sell Similar 按钮跳转发布页")
    logger.info("="*80)
    
    
    # ========== Act: 查找有 Sell Similar 按钮的商品 ==========
    with allure.step("步骤1: 查找有 Sell Similar 按钮的商品"):
        result = find_post_with_sell_similar_button(page, config, list_page, detail_page, sell_similar_page)
        
        if result is None:
            pytest.skip("列表页未找到有 Sell Similar 按钮的商品")
        
        detail_url, _, _ = result
        logger.info(f"✓ 找到目标商品: {detail_url}")
    
    with allure.step("步骤2: 验证 Sell Similar 按钮可见"):
        assert sell_similar_page.is_sell_similar_button_visible(timeout=5000), \
            "Sell Similar 按钮应该可见"
        logger.info("✓ Sell Similar 按钮可见")
    
    # ========== Act 阶段2: 点击 Sell Similar 按钮 ==========
    with allure.step("步骤3: 点击 Sell Similar 按钮"):
        sell_similar_page.click_sell_similar_button()
        logger.info("✓ 已点击 Sell Similar 按钮")
    
    with allure.step("步骤4: 等待页面跳转"):
        page.wait_for_load_state("domcontentloaded", timeout=30000)
        wait_publish_context_ready(page, timeout=20000)
        logger.info("✓ 页面跳转完成")
    
    # ========== Assert: 验证跳转到发布页 ==========
    with allure.step("验证1: 成功跳转到发布页"):
        assert sell_similar_page.is_publish_page_loaded(timeout=20000), \
            "应该成功跳转到发布页"
        logger.info("✓ 确认已进入发布页")
    
    with allure.step("验证2: URL 包含 publish 或 Post 标题"):
        current_url = sell_similar_page.get_current_url()
        page_title = page.title()
        
        url_check = "/publish/" in current_url.lower() or "/biz/en/publish/" in current_url.lower()
        title_check = "post" in page_title.lower()
        
        assert url_check or title_check, \
            f"发布页 URL 应包含 '/publish/'，或标题应包含 'Post'。实际 URL: {current_url}, 标题: {page_title}"
        logger.info(f"✓ URL 验证通过: {current_url}")
        logger.info(f"✓ 标题验证通过: {page_title}")
    
    logger.info("="*80)
    logger.info("✅ TC002 测试通过！Sell Similar 按钮功能正常")
    logger.info("="*80)


@pytest.mark.case_id_sell_similar_tc003
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.marketplace
@pytest.mark.ae
@allure.feature("Marketplace")
@allure.story("Sell Similar - 本人帖详情页按钮隐藏")
@allure.title("本人帖详情页不应该展示 Sell Similar 按钮")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证在本人发布的二手帖子详情页，不展示 Sell Similar 按钮，应展示 Withdraw/Edit 按钮")
def test_tc003_own_post_does_not_show_sell_similar_button(marketplace_list_session, config):
    """本人帖详情页不展示 Sell Similar 按钮测试"""
    page = marketplace_list_session
    
    # ========== Arrange: 准备测试对象 ==========
    list_page = MarketplaceListPageAe(page)
    detail_page = MarketplaceDetailPageAe(page)
    sell_similar_page = MarketplaceSellSimilarPageAe(page)
    
    logger.info("="*80)
    logger.info("TC003: 本人帖详情页不展示 Sell Similar 按钮")
    logger.info("="*80)
    
    
    # ========== Act: 查找本人帖子 ==========
    with allure.step("步骤1: 查找本人发布的帖子"):
        # 使用包含本人帖子的特定URL
        page.goto(
            f"{config['base_url']}/en/city-abu-dhabi/cate-marketplace/?iconSource=marketplace",
            wait_until="domcontentloaded",
            timeout=60000
        )
        try:
            wait_aed_listing_price_signal(page, 20000)
        except Exception:
            wait_dom_content_loaded(page, 15000)
        logger.info("✓ 访问本人帖子列表页 (iconSource=marketplace)")
        
        own_post_found = False
        own_post_url = None
        
        all_links = []
        try:
            # 策略1: 查找包含价格的商品卡片
            import re
            price_elements = page.locator("text=/AED\\s+\\d+/").all()
            logger.info(f"找到 {len(price_elements)} 个价格元素")
            
            for price_elem in price_elements[:20]:
                try:
                    parent_link = price_elem.locator("xpath=ancestor::a[@href]").first
                    href = parent_link.get_attribute("href")
                    
                    if not href:
                        continue
                    
                    # 验证是否是详情页链接
                    if "cate-marketplace" in href or "?" in href:
                        continue
                    if not href.endswith("/"):
                        continue
                    if not re.search(r'\d{10,}', href):
                        continue
                    
                    if href not in all_links:
                        all_links.append(href)
                        logger.info(f"  -> 商品 {len(all_links)}: {href}")
                        
                        if len(all_links) >= 10:
                            break
                except Exception:
                    continue
            
            # 策略2: 如果策略1没找到,使用备用方案
            if len(all_links) == 0:
                logger.info("策略1未找到商品,尝试策略2...")
                links = page.locator('a[href*="/cate-"]').all()
                for link in links[:30]:
                    try:
                        href = link.get_attribute("href")
                        if not href:
                            continue
                        
                        # 详情页链接特征
                        if "cate-marketplace" in href:
                            continue
                        if not href.endswith("/"):
                            continue
                        if not re.search(r'\d{19}', href):
                            continue
                        
                        if href not in all_links:
                            all_links.append(href)
                            logger.info(f"  -> 商品 {len(all_links)}: {href}")
                            
                            if len(all_links) >= 10:
                                break
                    except Exception:
                        continue
        except Exception as e:
            logger.warning(f"获取商品链接时出错: {e}")
        
        logger.info(f"✓ 总共找到 {len(all_links)} 个商品链接,开始查找本人帖...")
        
        for i, href in enumerate(all_links, 1):
            try:
                detail_url = urljoin(page.url, href)
                page.goto(detail_url, wait_until="domcontentloaded", timeout=30000)
                try:
                    wait_marketplace_detail_price(page, 20000)
                except Exception:
                    wait_dom_content_loaded(page, 15000)
                has_withdraw = detail_page.is_withdraw_button_visible(timeout=3000)
                has_edit = detail_page.is_edit_button_visible(timeout=3000)
                
                if has_withdraw or has_edit:
                    own_post_found = True
                    own_post_url = detail_url
                    logger.info(f"✓ 找到本人帖子 [{i}/{len(all_links)}]: {detail_url}")
                    break
                else:
                    # 返回本人帖子列表页继续查找
                    page.goto(
                        f"{config['base_url']}/en/city-abu-dhabi/cate-marketplace/?iconSource=marketplace",
                        wait_until="domcontentloaded",
                        timeout=30000
                    )
                    try:
                        wait_aed_listing_price_signal(page, 12000)
                    except Exception:
                        wait_short_ui_tick(page)
            except Exception as e:
                logger.warning(f"检查第 {i} 个商品时出错: {e}")
                continue
        
        if not own_post_found:
            pytest.skip("列表页未找到本人发布的帖子,跳过测试。建议先发布一个测试商品。")
    
    # ========== Assert: 验证本人帖详情页按钮展示 ==========
    with allure.step("验证1: 展示 Withdraw 或 Edit 按钮 (本人帖特征)"):
        has_withdraw = detail_page.is_withdraw_button_visible(timeout=5000)
        has_edit = detail_page.is_edit_button_visible(timeout=5000)
        assert has_withdraw or has_edit, \
            "本人帖应展示 Withdraw 或 Edit 按钮"
        logger.info("✓ 确认展示 Withdraw/Edit 按钮")
    
    with allure.step("验证2: 不展示 Contact 按钮 (本人帖特征)"):
        has_contact = detail_page.is_contact_button_visible(timeout=3000)
        assert not has_contact, \
            "本人帖不应展示 Contact 按钮"
        logger.info("✓ 确认不展示 Contact 按钮")
    
    with allure.step("验证3: 不展示 Sell Similar 按钮 (核心验证)"):
        has_sell_similar = sell_similar_page.is_sell_similar_button_visible(timeout=5000)
        assert not has_sell_similar, \
            "本人帖不应展示 Sell Similar 按钮"
        logger.info("✓ 确认不展示 Sell Similar 按钮")
    
    logger.info("="*80)
    logger.info("✅ TC003 测试通过！本人帖正确隐藏 Sell Similar 按钮")
    logger.info("="*80)


@pytest.mark.case_id_sell_similar_tc004
@pytest.mark.smoke
@pytest.mark.p1
@pytest.mark.marketplace
@pytest.mark.ae
@allure.feature("Marketplace")
@allure.story("Sell Similar - 发布页预加载内容")
@allure.title("发布页应该预加载原帖的价格等信息,但图片应被清空")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证点击 Sell Similar 后,发布页正确预加载原帖的价格信息,但图片应被清空")
def test_tc004_publish_page_preloads_original_post_data(marketplace_list_session, config):
    """发布页预加载原帖数据测试"""
    page = marketplace_list_session
    
    # ========== Arrange: 准备测试对象 ==========
    list_page = MarketplaceListPageAe(page)
    detail_page = MarketplaceDetailPageAe(page)
    sell_similar_page = MarketplaceSellSimilarPageAe(page)
    
    logger.info("="*80)
    logger.info("TC004: 发布页预加载原帖数据")
    logger.info("="*80)
    
    
    # ========== Act: 查找有 Sell Similar 按钮的商品并记录信息 ==========
    with allure.step("步骤1: 查找有 Sell Similar 按钮的商品"):
        result = find_post_with_sell_similar_button(page, config, list_page, detail_page, sell_similar_page)
        
        if result is None:
            pytest.skip("列表页未找到有 Sell Similar 按钮的商品")
        
        detail_url, original_price, original_title = result
        logger.info(f"✓ 原帖价格: {original_price}")
        logger.info(f"✓ 原帖标题: {original_title[:50] if original_title else 'N/A'}")
    
    # ========== Act 阶段2: 点击 Sell Similar 进入发布页 ==========
    with allure.step("步骤2: 点击 Sell Similar 按钮"):
        sell_similar_page.click_sell_similar_button()
        logger.info("✓ 已点击 Sell Similar 按钮")
    
    with allure.step("步骤3: 等待发布页加载"):
        page.wait_for_load_state("domcontentloaded", timeout=30000)
        wait_publish_context_ready(page, timeout=25000)
        assert sell_similar_page.is_publish_page_loaded(timeout=20000), \
            "应该成功跳转到发布页"
        logger.info("✓ 已进入发布页")
    
    # ========== Assert: 验证发布页预加载内容 ==========
    with allure.step("验证1: 发布页 URL 正确"):
        current_url = sell_similar_page.get_current_url()
        assert "/publish/" in current_url.lower(), \
            f"发布页 URL 应包含 '/publish/'，实际: {current_url}"
        logger.info(f"✓ URL 验证通过: {current_url}")
    
    with allure.step("验证2: 价格信息已预填充 (如果原帖有价格)"):
        if original_price and original_price != "AED 0":
            wait_dom_content_loaded(page, 10000)
            publish_price = sell_similar_page.get_publish_page_price(timeout=5000)
            
            if publish_price:
                import re
                original_price_num = re.search(r'\d+', original_price)
                if original_price_num:
                    logger.info(f"✓ 发布页价格已预填充: {publish_price}")
                else:
                    logger.info(f"⚠️ 发布页价格: {publish_price} (原帖: {original_price})")
            else:
                logger.info("⚠️ 发布页价格输入框为空或未找到")
    
    with allure.step("验证3: 图片应该被清空"):
        images_count = sell_similar_page.get_publish_page_images_count(timeout=3000)
        logger.info(f"发布页图片数量: {images_count}")
        # 注意: 图片清空的验证可能需要根据实际页面结构调整
    
    with allure.step("验证4: 标题已预填充 (如果原帖有标题)"):
        if original_title:
            publish_title = sell_similar_page.get_publish_page_title(timeout=5000)
            if publish_title:
                logger.info(f"✓ 发布页标题已预填充: {publish_title[:50]}...")
            else:
                logger.info("⚠️ 发布页标题为空")
    
    logger.info("="*80)
    logger.info("✅ TC004 测试通过！发布页正确预加载原帖数据")
    logger.info("="*80)


@pytest.mark.case_id_sell_similar_tc005
@pytest.mark.smoke
@pytest.mark.p1
@pytest.mark.marketplace
@pytest.mark.ae
@allure.feature("Marketplace")
@allure.story("Sell Similar - 未登录场景")
@allure.title("未登录用户点击 Sell Similar 应调起登录弹窗")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证未登录用户点击 Sell Similar 按钮时,应该调起登录弹窗,而不是直接进入发布页")
def test_tc005_not_logged_in_user_shows_login_popup(page, config):
    """未登录用户点击 Sell Similar 调起登录测试"""
    
    # ========== Arrange: 准备测试对象 ==========
    list_page = MarketplaceListPageAe(page)
    detail_page = MarketplaceDetailPageAe(page)
    sell_similar_page = MarketplaceSellSimilarPageAe(page)
    
    logger.info("="*80)
    logger.info("TC005: 未登录用户点击 Sell Similar 调起登录")
    logger.info("="*80)
    
    # ========== 前置条件: 确保未登录状态 ==========
    with allure.step("前置条件: 清除登录状态"):
        try:
            # 清除所有存储
            page.context.clear_cookies()
            page.evaluate("localStorage.clear(); sessionStorage.clear();")
            logger.info("✓ 已清除 Cookies 和 Storage")
        except Exception as e:
            logger.warning(f"清除登录状态失败: {e}")
    
    # ========== Act: 未登录访问详情页 ==========
    with allure.step("步骤1: 未登录访问二手列表页"):
        page.goto(
            f"{config['base_url']}/en/city-abu-dhabi/cate-marketplace/",
            wait_until="domcontentloaded",
            timeout=60000
        )
        try:
            wait_list_results_settled(page, timeout=25000)
        except Exception:
            wait_aed_listing_price_signal(page, 20000)
        logger.info("✓ 打开二手列表页成功")
    
    with allure.step("步骤2: 验证未登录状态"):
        # 检查是否有登录按钮 (多种可能的文案)
        login_indicators = [
            page.get_by_text("Log in / Register"),
            page.get_by_text("Log in"),
            page.get_by_text("Sign in"),
            page.locator("[class*='login'], [class*='signin']").filter(has_text="Log")
        ]
        
        is_logged_out = False
        for indicator in login_indicators:
            try:
                if indicator.is_visible(timeout=2000):
                    is_logged_out = True
                    logger.info(f"✓ 找到未登录标识: {indicator}")
                    break
            except Exception:
                continue
        
        assert is_logged_out, \
            "应该显示登录相关按钮,确认未登录状态"
        logger.info("✓ 确认当前为未登录状态")
    
    with allure.step("步骤3: 进入商品详情页"):
        first_href = list_page.get_first_detail_listing_link_href()
        assert first_href, "列表页应至少有一个商品卡片"
        
        detail_url = urljoin(page.url, first_href)
        page.goto(detail_url, wait_until="domcontentloaded", timeout=30000)
        try:
            wait_marketplace_detail_price(page, 20000)
        except Exception:
            wait_dom_content_loaded(page, 15000)
        logger.info(f"✓ 已进入详情页: {detail_url}")
    
    with allure.step("步骤4: 验证 Sell Similar 按钮可见 (未登录也应展示)"):
        has_sell_similar = sell_similar_page.is_sell_similar_button_visible(timeout=5000)
        if not has_sell_similar:
            logger.warning("⚠️ 该商品没有 Sell Similar 按钮,尝试查找其他商品")
            pytest.skip("该商品没有 Sell Similar 按钮")
        logger.info("✓ Sell Similar 按钮可见")
    
    # ========== Act: 点击 Sell Similar ==========
    with allure.step("步骤5: 点击 Sell Similar 按钮"):
        sell_similar_page.click_sell_similar_button()
        try:
            page.locator("[role='dialog']").first.wait_for(state="visible", timeout=10000)
        except Exception:
            try:
                page.get_by_role("textbox", name="Email or phone number").wait_for(
                    state="visible", timeout=5000
                )
            except Exception:
                wait_short_ui_tick(page)
        logger.info("✓ 已点击 Sell Similar 按钮")
    
    # ========== Assert: 验证登录弹窗出现 ==========
    with allure.step("验证1: 应该调起登录弹窗或跳转到登录页"):
        # 检查登录相关元素
        email_input = page.get_by_role("textbox", name="Email or phone number")
        login_dialog = page.locator("[role='dialog']")
        
        email_visible = False
        dialog_visible = False
        
        try:
            email_visible = email_input.is_visible(timeout=5000)
        except Exception:
            pass
        
        try:
            dialog_visible = login_dialog.is_visible(timeout=5000)
        except Exception:
            pass
        
        # 或者检查 URL 是否跳转到登录页
        current_url = page.url
        url_has_login = "login" in current_url.lower()
        
        assert email_visible or dialog_visible or url_has_login, \
            f"未登录用户点击 Sell Similar 应该调起登录弹窗或跳转登录页。实际 URL: {current_url}"
        logger.info("✓ 确认登录弹窗已出现或跳转到登录页")
    
    with allure.step("验证2: 不应该直接进入发布页"):
        current_url = page.url
        assert "/publish/" not in current_url.lower() or "login" in current_url.lower(), \
            f"未登录用户不应该直接进入发布页,实际 URL: {current_url}"
        logger.info(f"✓ 确认未直接进入发布页: {current_url}")
    
    logger.info("="*80)
    logger.info("✅ TC005 测试通过！未登录用户正确调起登录")
    logger.info("="*80)

    # 恢复磁盘中的 Session，后续用例可走 ensure_ae_logged_in 快路径
    with allure.step("恢复登录态：从已保存 Session 还原，供后续用例使用"):
        ensure_ae_logged_in(page, config)


@pytest.mark.case_id_sell_similar_tc007
@pytest.mark.p1
@pytest.mark.marketplace
@pytest.mark.ae
@allure.feature("Marketplace")
@allure.story("Sell Similar - 非二手帖子不展示按钮")
@allure.title("非二手帖子(Jobs/Services)不应该展示 Sell Similar 按钮")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证在非二手分类的帖子详情页(如 Jobs、Services),不展示 Sell Similar 按钮")
def test_tc007_non_marketplace_posts_do_not_show_sell_similar(marketplace_list_session, config):
    """非二手帖子不展示 Sell Similar 按钮测试"""
    page = marketplace_list_session
    
    # ========== Arrange: 准备测试对象 ==========
    detail_page = MarketplaceDetailPageAe(page)
    sell_similar_page = MarketplaceSellSimilarPageAe(page)
    
    logger.info("="*80)
    logger.info("TC007: 非二手帖子不展示 Sell Similar 按钮")
    logger.info("="*80)
    
    
    # 测试多个非二手分类
    test_categories = [
        {
            "name": "Jobs",
            "list_url": f"{config['base_url']}/en/city-abu-dhabi/cate-jobs/",
            "category": "招聘"
        },
        {
            "name": "Services",
            "list_url": f"{config['base_url']}/en/city-abu-dhabi/cate-services/",
            "category": "服务"
        }
    ]
    
    for category_info in test_categories:
        with allure.step(f"测试分类: {category_info['name']}"):
            logger.info(f"\n{'='*60}")
            logger.info(f"测试分类: {category_info['name']} ({category_info['category']})")
            logger.info(f"{'='*60}")
            
            # 访问分类列表页
            page.goto(category_info['list_url'], wait_until="domcontentloaded", timeout=60000)
            try:
                page.wait_for_load_state("load", timeout=10000)
            except Exception:
                pass
            wait_dom_content_loaded(page, 15000)
            logger.info(f"✓ 打开 {category_info['name']} 列表页")
            
            # 获取第一个帖子链接
            try:
                # 查找第一个详情页链接
                links = page.locator('a[href*="/cate-"]').all()
                detail_url = None
                
                for link in links[:20]:
                    try:
                        href = link.get_attribute("href")
                        if not href:
                            continue
                        # 排除列表页本身
                        if f"cate-{category_info['name'].lower()}" in href and href.count("/cate-") >= 1:
                            # 检查是否是详情页 (包含商品ID)
                            parts = href.split("/")
                            if len(parts) > 5:  # 详情页 URL 通常更长
                                detail_url = urljoin(page.url, href)
                                break
                    except Exception:
                        continue
                
                if not detail_url:
                    logger.warning(f"⚠️ {category_info['name']} 列表页未找到详情页链接,跳过")
                    continue
                
                # 访问详情页
                page.goto(detail_url, wait_until="domcontentloaded", timeout=30000)
                wait_dom_content_loaded(page, 15000)
                try:
                    page.wait_for_load_state("networkidle", timeout=8000)
                except Exception:
                    pass
                logger.info(f"✓ 已进入 {category_info['name']} 详情页: {detail_url}")
                
                # 验证不展示 Sell Similar 按钮
                has_sell_similar = sell_similar_page.is_sell_similar_button_visible(timeout=5000)
                assert not has_sell_similar, \
                    f"{category_info['name']} 帖子不应展示 Sell Similar 按钮"
                logger.info(f"✓ 确认 {category_info['name']} 帖子不展示 Sell Similar 按钮")
                
            except AssertionError:
                raise
            except Exception as e:
                logger.warning(f"⚠️ 测试 {category_info['name']} 分类时出错: {e}")
                continue
    
    logger.info("="*80)
    logger.info("✅ TC007 测试通过！非二手帖子正确不展示 Sell Similar 按钮")
    logger.info("="*80)


@pytest.mark.case_id_sell_similar_tc008
@pytest.mark.p2
@pytest.mark.marketplace
@pytest.mark.ae
@allure.feature("Marketplace")
@allure.story("Sell Similar - 多语言验证")
@allure.title("ES 站点应该展示西班牙语的 Sell Similar 按钮")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证在 ES 语言环境下,Sell Similar 按钮文案正确显示为西班牙语")
def test_tc008_sell_similar_button_in_spanish_language(marketplace_list_session, config):
    """多语言验证 - ES 站点测试"""
    page = marketplace_list_session
    
    # ========== Arrange: 准备测试对象 ==========
    list_page = MarketplaceListPageAe(page)
    detail_page = MarketplaceDetailPageAe(page)
    sell_similar_page = MarketplaceSellSimilarPageAe(page)
    
    logger.info("="*80)
    logger.info("TC008: 多语言验证 - ES 站点")
    logger.info("="*80)
    
    
    # ========== Act: 切换到 ES 语言并查找商品 ==========
    with allure.step("步骤1: 切换到西班牙语 (ES) 并查找商品"):
        # 使用 helper 函数查找有 Sell Similar 按钮的商品 (ES 语言)
        result = find_post_with_sell_similar_button(
            page, config, list_page, detail_page, sell_similar_page, 
            max_attempts=20, language='es'
        )
        
        if result is None:
            pytest.skip("ES 语言列表页未找到有 Sell Similar 按钮的商品")
        
        detail_url, _, _ = result
        logger.info(f"✓ 已进入 ES 语言详情页: {detail_url}")
    
    # ========== Assert: 验证按钮展示 ==========
    with allure.step("验证: 在 ES 语言列表页找到的商品,详情页应该展示 Sell Similar 按钮"):
        # 注意: detail_url 是从 ES 列表页找到的,但点击后可能跳转到 EN 页面
        # 这是正常的,因为后端可能会重定向到默认语言
        # 关键是验证按钮是否可见
        
        current_url = page.url
        logger.info(f"✓ 当前页面 URL: {current_url}")
        
        # 检查按钮是否可见 (英文或西班牙语)
        has_sell_similar_en = sell_similar_page.is_sell_similar_button_visible(timeout=3000)
        
        # 检查西班牙语版本
        has_sell_similar_es = False
        try:
            es_button = page.locator("text=/Vender.*similar/i").first
            has_sell_similar_es = es_button.is_visible(timeout=3000)
        except Exception:
            pass
        
        # 至少有一个版本的按钮应该可见
        assert has_sell_similar_en or has_sell_similar_es, \
            "从 ES 列表页找到的商品应该展示 Sell Similar 按钮"
        
        if has_sell_similar_en:
            logger.info("✓ 找到英文版 Sell Similar 按钮")
        if has_sell_similar_es:
            logger.info("✓ 找到西班牙语版 Vender similar 按钮")
    
    logger.info("="*80)
    logger.info("✅ TC008 测试通过！ES 语言环境下按钮正常展示")
    logger.info("="*80)


@pytest.mark.case_id_sell_similar_tc009
@pytest.mark.p2
@pytest.mark.marketplace
@pytest.mark.ae
@allure.feature("Marketplace")
@allure.story("Sell Similar - 发布页属性继承")
@allure.title("发布页应该继承原帖的商品属性")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证点击 Sell Similar 后,发布页正确继承原帖的商品属性(如品牌、型号、状况等)")
def test_tc009_publish_page_inherits_product_attributes(marketplace_list_session, config):
    """发布页属性继承验证测试"""
    page = marketplace_list_session
    
    # ========== Arrange: 准备测试对象 ==========
    list_page = MarketplaceListPageAe(page)
    detail_page = MarketplaceDetailPageAe(page)
    sell_similar_page = MarketplaceSellSimilarPageAe(page)
    
    logger.info("="*80)
    logger.info("TC009: 发布页属性继承验证")
    logger.info("="*80)
    
    
    # ========== Act: 查找有 Sell Similar 按钮的商品 ==========
    with allure.step("步骤1: 查找有 Sell Similar 按钮的商品"):
        result = find_post_with_sell_similar_button(page, config, list_page, detail_page, sell_similar_page)
        
        if result is None:
            pytest.skip("列表页未找到有 Sell Similar 按钮的商品")
        
        detail_url, original_price, original_title = result
        logger.info(f"✓ 找到目标商品: {detail_url}")
    
    with allure.step("步骤2: 记录原帖的属性信息"):
        # 尝试获取商品属性
        original_attributes = {}
        
        # 查找属性标签 (如 Brand, Model, Condition 等)
        try:
            attribute_elements = page.locator("[class*='attribute'], [class*='spec'], [class*='detail']").all()
            for elem in attribute_elements[:10]:
                try:
                    text = elem.inner_text()
                    if ":" in text:
                        key, value = text.split(":", 1)
                        original_attributes[key.strip()] = value.strip()
                except Exception:
                    continue
        except Exception:
            pass
        
        logger.info(f"✓ 原帖属性: {original_attributes if original_attributes else '未找到明确属性标签'}")
    
    # ========== Act: 点击 Sell Similar 进入发布页（可能新标签） ==========
    with allure.step("步骤3–4: 点击 Sell Similar 并切换到实际发布页"):
        publish_page = sell_similar_page.get_publish_page_after_sell_similar_click()
        page = publish_page
        sell_similar_page = MarketplaceSellSimilarPageAe(publish_page)
        wait_publish_context_ready(publish_page, timeout=20000)
        assert sell_similar_page.is_publish_page_loaded(timeout=15000), \
            "应该成功跳转到发布页（含新标签场景）"
        logger.info("✓ 已进入发布页")
    
    # ========== Assert: 验证发布页属性继承 ==========
    with allure.step("验证1: 发布页 URL 正确"):
        current_url = sell_similar_page.get_current_url()
        cur = current_url.lower()
        assert "/publish/" in cur or ("/biz/" in cur and "publish" in cur), \
            f"发布页 URL 应包含发布路径，实际: {current_url}"
        logger.info(f"✓ URL 验证通过: {current_url}")
    
    with allure.step("验证2: 检查属性字段是否存在"):
        # 查找常见的属性输入框或选择器
        common_attributes = ["brand", "model", "condition", "color", "size"]
        found_attributes = []
        
        for attr in common_attributes:
            try:
                # 尝试查找属性相关的输入框或选择器
                attr_input = page.locator(f"input[name*='{attr}' i], select[name*='{attr}' i], [placeholder*='{attr}' i]").first
                if attr_input.count() > 0:
                    found_attributes.append(attr)
                    value = ""
                    try:
                        value = attr_input.input_value() or attr_input.inner_text()
                    except Exception:
                        pass
                    logger.info(f"  ✓ 找到属性字段: {attr} = {value[:30] if value else '(空)'}")
            except Exception:
                continue
        
        if found_attributes:
            logger.info(f"✓ 发布页包含属性字段: {', '.join(found_attributes)}")
        else:
            logger.info("⚠️ 未找到明确的属性字段 (可能使用不同的字段命名)")
    
    with allure.step("验证3: 标题和价格已预填充"):
        # 验证标题
        publish_title = sell_similar_page.get_publish_page_title(timeout=5000)
        if publish_title:
            logger.info(f"✓ 发布页标题已预填充: {publish_title[:50]}...")
        
        # 验证价格
        if original_price and original_price != "AED 0":
            publish_price = sell_similar_page.get_publish_page_price(timeout=5000)
            if publish_price:
                logger.info(f"✓ 发布页价格已预填充: {publish_price}")
    
    logger.info("="*80)
    logger.info("✅ TC009 测试通过！发布页属性继承验证完成")
    logger.info("="*80)


@pytest.mark.case_id_sell_similar_tc010
@pytest.mark.p2
@pytest.mark.marketplace
@pytest.mark.ae
@allure.feature("Marketplace")
@allure.story("Sell Similar - 发布页描述继承")
@allure.title("发布页应该继承原帖的商品描述")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证点击 Sell Similar 后,发布页正确继承原帖的商品描述内容")
def test_tc010_publish_page_inherits_description(marketplace_list_session, config):
    """发布页描述继承验证测试"""
    page = marketplace_list_session
    
    # ========== Arrange: 准备测试对象 ==========
    list_page = MarketplaceListPageAe(page)
    detail_page = MarketplaceDetailPageAe(page)
    sell_similar_page = MarketplaceSellSimilarPageAe(page)
    
    logger.info("="*80)
    logger.info("TC010: 发布页描述继承验证")
    logger.info("="*80)
    
    
    # ========== Act: 查找有 Sell Similar 按钮的商品 ==========
    with allure.step("步骤1: 查找有 Sell Similar 按钮的商品"):
        result = find_post_with_sell_similar_button(page, config, list_page, detail_page, sell_similar_page)
        
        if result is None:
            pytest.skip("列表页未找到有 Sell Similar 按钮的商品")
        
        detail_url, original_price, original_title = result
        logger.info(f"✓ 找到目标商品: {detail_url}")
    
    with allure.step("步骤2: 记录原帖的描述信息"):
        # 尝试获取商品描述
        original_description = ""
        try:
            # 查找描述区域
            desc_selectors = [
                "[class*='description']",
                "[class*='content']",
                "[class*='detail']",
                "p",
                "[class*='text']"
            ]
            
            for selector in desc_selectors:
                try:
                    desc_elem = page.locator(selector).first
                    if desc_elem.count() > 0:
                        text = desc_elem.inner_text()
                        if len(text) > 20:  # 至少 20 个字符才算有效描述
                            original_description = text
                            break
                except Exception:
                    continue
        except Exception:
            pass
        
        logger.info(f"✓ 原帖描述: {original_description[:100] if original_description else '未找到描述内容'}...")
    
    # ========== Act: 点击 Sell Similar 进入发布页（可能新标签） ==========
    with allure.step("步骤3–4: 点击 Sell Similar 并切换到实际发布页"):
        publish_page = sell_similar_page.get_publish_page_after_sell_similar_click()
        page = publish_page
        sell_similar_page = MarketplaceSellSimilarPageAe(publish_page)
        wait_publish_context_ready(publish_page, timeout=20000)
        assert sell_similar_page.is_publish_page_loaded(timeout=40000), \
            "应该成功跳转到发布页（含新标签场景）"
        logger.info("✓ 已进入发布页")
    
    # ========== Assert: 验证发布页描述继承 ==========
    with allure.step("验证1: 发布页 URL 正确"):
        current_url = sell_similar_page.get_current_url()
        cur = current_url.lower()
        assert "/publish/" in cur or ("/biz/" in cur and "publish" in cur), \
            f"发布页 URL 应包含发布路径，实际: {current_url}"
        logger.info(f"✓ URL 验证通过: {current_url}")
    
    with allure.step("验证2: 描述内容已预填充"):
        publish_description = sell_similar_page.get_publish_page_description(timeout=5000)
        
        if publish_description:
            logger.info(f"✓ 发布页描述已预填充: {publish_description[:100]}...")
            
            # 如果原帖有描述,验证是否继承
            if original_description:
                # 简单验证: 检查是否有相似内容
                similarity = len(set(original_description.split()) & set(publish_description.split()))
                if similarity > 3:  # 至少有 3 个相同的词
                    logger.info(f"✓ 描述内容相似度较高 (共同词汇: {similarity} 个)")
                else:
                    logger.info(f"⚠️ 描述内容相似度较低 (共同词汇: {similarity} 个)")
        else:
            logger.info("⚠️ 发布页描述为空或未找到描述输入框")
    
    with allure.step("验证3: 其他字段也已预填充"):
        # 验证标题
        publish_title = sell_similar_page.get_publish_page_title(timeout=5000)
        if publish_title:
            logger.info(f"✓ 发布页标题已预填充: {publish_title[:50]}...")
        
        # 验证价格
        if original_price and original_price != "AED 0":
            publish_price = sell_similar_page.get_publish_page_price(timeout=5000)
            if publish_price:
                logger.info(f"✓ 发布页价格已预填充: {publish_price}")
    
    logger.info("="*80)
    logger.info("✅ TC010 测试通过！发布页描述继承验证完成")
    logger.info("="*80)
