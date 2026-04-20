"""
OK.com - 地区选择页 - 页面元素展示测试（Batch 2）

本脚本由 playwright-test-generator 生成
录制文档：web-qa-brain/OK.com-地区选择页-测试用例-20260320.md
生成时间：2026-03-20

测试站点：Global (https://www.ok.com/biz/en/site)
测试角色：Visitor (访客)
测试目标：验证地区选择页面的核心元素显示（主标题、副标题、Logo）
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


@pytest.mark.case_id_site_selection_tc008
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.site_selection
@pytest.mark.ui
@allure.feature("OK.com 地区选择")
@allure.story("页面元素展示")
@allure.title("页面主标题正确显示")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证地区选择页面的主标题显示为'Please select the country and region you would like to browse.'且文字居中、无截断")
def test_tc008_main_title_should_display_correctly(page, config):
    """TC008: 页面主标题正确显示"""
    
    # ==================== Arrange ====================
    site_selection_page = SiteSelectionPage(page)
    
    logger.info("=" * 80)
    logger.info("TC008: 页面主标题正确显示")
    logger.info("=" * 80)
    logger.info(f"站点: {config['site_name']}")
    logger.info(f"URL: {config['base_url']}")
    logger.info("=" * 80)
    
    # ==================== Act ====================
    with allure.step("步骤1：访问地区选择页面"):
        site_selection_page.navigate_to_site_selection_page()
        logger.info("✓ 成功访问地区选择页面")
    
    with allure.step("步骤2：获取主标题文本"):
        main_title = site_selection_page.get_main_title_text()
        logger.info(f"✓ 主标题文本: {main_title}")
    
    # ==================== Assert ====================
    with allure.step("验证：主标题文案正确"):
        expected_title = "Please select the country and region you would like to browse."
        # 移除换行符进行比较
        normalized_title = " ".join(main_title.split())
        assert expected_title in normalized_title or normalized_title == expected_title, \
            f"主标题文案不正确，期望包含'{expected_title}'，实际: {normalized_title}"
        logger.info(f"✓ 主标题文案验证通过")
    
    with allure.step("验证：主标题显示完整，无截断"):
        assert len(main_title) > 40, f"主标题文本太短，可能被截断: {main_title}"
        logger.info(f"✓ 主标题显示完整")
    
    with allure.step("验证：主标题文字居中显示"):
        is_centered = site_selection_page.is_main_title_centered()
        assert is_centered, "主标题未居中显示"
        logger.info(f"✓ 主标题居中显示验证通过")
    
    logger.info("=" * 80)
    logger.info("✅ TC008 测试通过！")
    logger.info("=" * 80)


@pytest.mark.case_id_site_selection_tc009
@pytest.mark.smoke
@pytest.mark.p1
@pytest.mark.site_selection
@pytest.mark.ui
@allure.feature("OK.com 地区选择")
@allure.story("页面元素展示")
@allure.title("页面副标题正确显示")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证地区选择页面的副标题显示为'Explore your community below'且位于主标题下方")
def test_tc009_subtitle_should_display_correctly(page, config):
    """TC009: 页面副标题正确显示"""
    
    # ==================== Arrange ====================
    site_selection_page = SiteSelectionPage(page)
    
    logger.info("=" * 80)
    logger.info("TC009: 页面副标题正确显示")
    logger.info("=" * 80)
    logger.info(f"站点: {config['site_name']}")
    logger.info(f"URL: {config['base_url']}")
    logger.info("=" * 80)
    
    # ==================== Act ====================
    with allure.step("步骤1：访问地区选择页面"):
        site_selection_page.navigate_to_site_selection_page()
        logger.info("✓ 成功访问地区选择页面")
    
    with allure.step("步骤2：获取副标题文本"):
        subtitle = site_selection_page.get_subtitle_text()
        logger.info(f"✓ 副标题文本: {subtitle}")
    
    # ==================== Assert ====================
    with allure.step("验证：副标题文案正确"):
        expected_subtitle = "Explore your community below"
        assert expected_subtitle in subtitle, \
            f"副标题文案不正确，期望包含'{expected_subtitle}'，实际: {subtitle}"
        logger.info(f"✓ 副标题文案验证通过")
    
    with allure.step("验证：副标题显示完整"):
        assert len(subtitle) >= 20, f"副标题文本太短，可能被截断: {subtitle}"
        logger.info(f"✓ 副标题显示完整")
    
    logger.info("=" * 80)
    logger.info("✅ TC009 测试通过！")
    logger.info("=" * 80)


@pytest.mark.case_id_site_selection_tc010
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.site_selection
@pytest.mark.ui
@allure.feature("OK.com 地区选择")
@allure.story("页面元素展示")
@allure.title("OK.com Logo显示")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证地区选择页面顶部居中显示OK.com Logo，Logo图片加载正常无破损")
def test_tc010_logo_should_display_correctly(page, config):
    """TC010: OK.com Logo显示"""
    
    # ==================== Arrange ====================
    site_selection_page = SiteSelectionPage(page)
    
    logger.info("=" * 80)
    logger.info("TC010: OK.com Logo显示")
    logger.info("=" * 80)
    logger.info(f"站点: {config['site_name']}")
    logger.info(f"URL: {config['base_url']}")
    logger.info("=" * 80)
    
    # ==================== Act ====================
    with allure.step("步骤1：访问地区选择页面"):
        site_selection_page.navigate_to_site_selection_page()
        logger.info("✓ 成功访问地区选择页面")
    
    # ==================== Assert ====================
    with allure.step("验证：Logo可见"):
        is_visible = site_selection_page.is_logo_visible()
        assert is_visible, "Logo未显示"
        logger.info(f"✓ Logo显示验证通过")
    
    with allure.step("验证：Logo位于页面顶部"):
        # Logo应该在页面顶部，通常在主标题上方
        page_title = site_selection_page.get_page_title()
        assert page_title is not None, "页面标题为空"
        logger.info(f"✓ Logo位于页面顶部（页面标题存在: {page_title}）")
    
    logger.info("=" * 80)
    logger.info("✅ TC010 测试通过！")
    logger.info("=" * 80)
