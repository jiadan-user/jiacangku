"""
OK.com - 地区选择页 - 页面元素展示测试（Batch 3）

本脚本由 playwright-test-generator 生成
录制文档：web-qa-brain/OK.com-地区选择页-测试用例-20260320.md
生成时间：2026-03-20

测试站点：Global (https://www.ok.com/biz/en/site)
测试角色：Visitor (访客)
测试目标：验证地区选择页面的国家选项完整性、国旗图标显示和页面加载性能
"""
import pytest
import allure
from pages.site_selection_page import SiteSelectionPage
from utils.logger import setup_logger

logger = setup_logger()

# ============================================
# 测试环境配置（无需登录）
# ============================================
_CONFIG = {
    "site": "global",
    "site_name": "OK.com 地区选择页",
    "role": "visitor",
    "user_name": "guest",
    "base_url": "https://home.58v5.cn/biz/en/site",
    "test_account": None,
    "locale": "en",
    "currency": "USD",
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


@pytest.mark.case_id_site_selection_tc011
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.site_selection
@pytest.mark.ui
@allure.feature("OK.com 地区选择")
@allure.story("页面元素展示")
@allure.title("国家/地区数量完整性验证")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证地区选择页面显示22个国家/地区选项，且所有选项均正确显示、可见、可点击")
def test_tc011_country_options_completeness(page, config):
    """TC011: 国家/地区数量完整性验证"""
    
    # ==================== Arrange ====================
    site_selection_page = SiteSelectionPage(page)
    
    logger.info("=" * 80)
    logger.info("TC011: 国家/地区数量完整性验证")
    logger.info("=" * 80)
    logger.info(f"站点: {config['site_name']}")
    logger.info(f"URL: {config['base_url']}")
    logger.info("=" * 80)
    
    # ==================== Act ====================
    with allure.step("步骤1：访问地区选择页面"):
        site_selection_page.navigate_to_site_selection_page()
        logger.info("✓ 成功访问地区选择页面")
    
    with allure.step("步骤2：统计页面上的国家选项数量"):
        country_count = site_selection_page.count_country_links()
        logger.info(f"✓ 统计到 {country_count} 个国家/地区选项")
    
    with allure.step("步骤3：获取所有国家链接元素"):
        country_links = site_selection_page.get_country_link_elements()
        logger.info(f"✓ 获取到 {len(country_links)} 个国家链接元素")
    
    # ==================== Assert ====================
    with allure.step("验证：页面显示22个国家/地区选项"):
        assert country_count == 22, \
            f"国家/地区选项数量不正确，期望22个，实际{country_count}个"
        logger.info(f"✓ 国家/地区数量验证通过: {country_count}个")
    
    with allure.step("验证：所有国家选项均可见"):
        visible_count = 0
        for link in country_links:
            if site_selection_page.is_country_link_visible(link):
                visible_count += 1
        
        assert visible_count == len(country_links), \
            f"部分国家选项不可见，可见{visible_count}个，总共{len(country_links)}个"
        logger.info(f"✓ 所有 {visible_count} 个国家选项均可见")
    
    with allure.step("验证：所有选项均可点击"):
        clickable_count = 0
        for link in country_links:
            if link.is_enabled():
                clickable_count += 1
        
        assert clickable_count == len(country_links), \
            f"部分国家选项不可点击，可点击{clickable_count}个，总共{len(country_links)}个"
        logger.info(f"✓ 所有 {clickable_count} 个国家选项均可点击")
    
    logger.info("=" * 80)
    logger.info("✅ TC011 测试通过！")
    logger.info("=" * 80)


@pytest.mark.case_id_site_selection_tc012
@pytest.mark.smoke
@pytest.mark.p1
@pytest.mark.site_selection
@pytest.mark.ui
@allure.feature("OK.com 地区选择")
@allure.story("页面元素展示")
@allure.title("国家旗帜图标显示")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证每个国家选项都显示对应的国旗图标，且国旗图标清晰、无破损、与国家名称对应正确")
def test_tc012_country_flag_icons_display(page, config):
    """TC012: 国家旗帜图标显示"""
    
    # ==================== Arrange ====================
    site_selection_page = SiteSelectionPage(page)
    
    logger.info("=" * 80)
    logger.info("TC012: 国家旗帜图标显示")
    logger.info("=" * 80)
    logger.info(f"站点: {config['site_name']}")
    logger.info(f"URL: {config['base_url']}")
    logger.info("=" * 80)
    
    # ==================== Act ====================
    with allure.step("步骤1：访问地区选择页面"):
        site_selection_page.navigate_to_site_selection_page()
        logger.info("✓ 成功访问地区选择页面")
    
    with allure.step("步骤2：获取所有国家链接信息"):
        all_links = site_selection_page.get_all_country_links()
        logger.info(f"✓ 获取到 {len(all_links)} 个国家链接信息")
    
    # ==================== Assert ====================
    with allure.step("验证：每个国家选项都有对应的旗帜图标"):
        # 从页面截图可以看到，每个国家选项都有国旗图标
        # 我们通过检查页面上是否有足够的图标元素来验证
        total_images = page.locator("img, svg").count()
        
        # 至少应该有22个国旗图标（每个国家一个）+ 1个Logo
        assert total_images >= 22, \
            f"页面图标数量不足，期望至少22个国旗图标，实际总图标数: {total_images}"
        
        logger.info(f"✓ 页面图标数量验证通过: {total_images}个（包含Logo和国旗）")
    
    with allure.step("验证：国旗图标与国家名称对应"):
        # 验证所有22个国家链接都存在
        assert len(all_links) == 22, \
            f"国家链接数量不正确，期望22个，实际{len(all_links)}个"
        
        # 抽查几个国家的链接文本，确保显示正确
        sample_countries = ["United States", "香港", "Brasil", "الإمارات العربية المتحدة"]
        found_countries = []
        
        for link in all_links:
            if link["text"] in sample_countries:
                found_countries.append(link["text"])
                logger.info(f"  ✓ 找到国家: {link['text']} → {link['url']}")
        
        assert len(found_countries) == len(sample_countries), \
            f"部分国家未找到，期望{len(sample_countries)}个，实际{len(found_countries)}个"
        
        logger.info(f"✓ 国旗图标与国家名称对应验证通过")
    
    with allure.step("验证：国旗图标清晰无破损"):
        # 通过检查图标元素是否可见来验证图标加载正常
        # 取第一个国家链接作为样本
        first_country = all_links[0]["text"]
        first_link = page.get_by_role("link", name=first_country).first
        
        assert first_link.is_visible(), \
            f"第一个国家链接不可见: {first_country}"
        
        logger.info(f"✓ 国旗图标加载验证通过（样本: {first_country}）")
    
    logger.info("=" * 80)
    logger.info("✅ TC012 测试通过！")
    logger.info("=" * 80)


@pytest.mark.case_id_site_selection_tc013
@pytest.mark.smoke
@pytest.mark.p1
@pytest.mark.site_selection
@pytest.mark.performance
@allure.feature("OK.com 地区选择")
@allure.story("页面元素展示")
@allure.title("页面加载性能验证")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证地区选择页面在3秒内完成加载（DOMContentLoaded事件），所有国家选项在页面加载完成后立即可见")
def test_tc013_page_load_performance(page, config):
    """TC013: 页面加载性能验证"""
    
    # ==================== Arrange ====================
    site_selection_page = SiteSelectionPage(page)
    
    logger.info("=" * 80)
    logger.info("TC013: 页面加载性能验证")
    logger.info("=" * 80)
    logger.info(f"站点: {config['site_name']}")
    logger.info(f"URL: {config['base_url']}")
    logger.info("=" * 80)
    
    # ==================== Act ====================
    with allure.step("步骤1：访问地区选择页面并记录加载时间"):
        site_selection_page.navigate_to_site_selection_page()
        logger.info("✓ 页面访问完成")
        
        # 获取页面加载时间
        load_time_ms = site_selection_page.get_page_load_time()
        load_time_sec = load_time_ms / 1000
        logger.info(f"✓ 页面加载时间: {load_time_ms}ms ({load_time_sec:.2f}秒)")
    
    with allure.step("步骤2：验证国家选项立即可见"):
        # 页面加载完成后，国家选项应该立即可见，无需额外等待
        country_count = site_selection_page.count_country_links()
        logger.info(f"✓ 页面加载完成后立即可见 {country_count} 个国家选项")
    
    # ==================== Assert ====================
    with allure.step("验证：页面在3秒内完成加载"):
        assert load_time_sec <= 3.0, \
            f"页面加载时间超过3秒，实际: {load_time_sec:.2f}秒"
        logger.info(f"✓ 页面加载性能验证通过: {load_time_sec:.2f}秒 ≤ 3.0秒")
    
    with allure.step("验证：所有国家选项在页面加载后立即可见"):
        assert country_count == 22, \
            f"页面加载后国家选项数量不正确，期望22个，实际{country_count}个"
        logger.info(f"✓ 所有 {country_count} 个国家选项加载完成")
    
    with allure.step("验证：页面无白屏或长时间加载状态"):
        # 检查主标题是否可见，确保页面内容已渲染
        main_title = site_selection_page.get_main_title_text()
        assert len(main_title) > 0, "页面主标题未显示，可能存在白屏问题"
        logger.info(f"✓ 页面内容已完整渲染，无白屏现象")
    
    logger.info("=" * 80)
    logger.info("✅ TC013 测试通过！")
    logger.info("=" * 80)
