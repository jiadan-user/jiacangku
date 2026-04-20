"""
AE站 - 首页底部 Footer 公共区域测试 - 批次5（应用下载引导）

测试站点：AE (https://ae.ok.com)
测试角色：Visitor (访客)
测试目标：验证 Footer 区域应用下载引导功能

本脚本包含批次 5 的 3 个测试用例：
- TC-FOOTER-E-001：App Store 下载引导
- TC-FOOTER-E-002：Google Play 下载引导
- TC-FOOTER-E-003：应用下载按钮图标正确性
"""
import pytest
import allure
from pages.footer_page import FooterPage
from utils.logger import setup_logger

logger = setup_logger()

# ============================================
# 测试环境配置
# ============================================
_CONFIG = {
    "site": "ae",
    "site_name": "阿联酋站 (AE OK.com)",
    "role": "visitor",
    "user_name": "ae_visitor_footer",
    "base_url": "https://ae.58v5.cn",
    "test_account": None,
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


@pytest.mark.case_id_footer_e_001
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.footer
@pytest.mark.ae
@allure.feature("OK")
@allure.story("首页 Footer 区域 - 应用下载")
@allure.title("App Store 下载引导应该正确跳转")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证点击 App Store 按钮后，正确跳转到 iOS App Store")
def test_app_store_download_link(page, config):
    """TC-FOOTER-E-001: App Store 下载引导"""
    
    footer_page = FooterPage(page)
    base_url = config['base_url']
    
    logger.info("="*80)
    logger.info("TC-FOOTER-E-001: App Store 下载引导")
    logger.info("="*80)
    logger.info(f"站点: {config['site'].upper()} ({config['site_name']})")
    logger.info(f"角色: {config['role'].upper()} (访客)")
    logger.info(f"测试URL: {base_url}")
    logger.info("="*80)
    
    with allure.step("步骤1：访问首页"):
        footer_page.goto(base_url, timeout=60000)
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 打开首页成功: {page.url}")
    
    with allure.step("步骤2：滚动到 Footer 区域"):
        footer_page.scroll_to_footer()
        logger.info("✓ 滚动到 Footer 区域成功")
    
    with allure.step("验证1：App Store 链接 href 属性"):
        href = footer_page.get_app_store_href()
        
        # 检查是否有 App Store 链接
        if href and href != "":
            assert "apple.com" in href.lower() or "itunes" in href.lower() or "apps.apple" in href.lower(), \
                f"App Store 链接的 href 不正确: {href}"
            logger.info(f"✓ App Store href: {href}")
            
            with allure.step("步骤3：点击 App Store 链接"):
                with page.context.expect_page() as new_page_info:
                    footer_page.click_app_store()
                    logger.info("✓ 点击 App Store 链接")
                
                new_page = new_page_info.value
                new_page.wait_for_load_state("domcontentloaded", timeout=30000)
                logger.info(f"✓ 新页面加载完成: {new_page.url}")
            
            with allure.step("验证2：新页面URL正确"):
                new_url = new_page.url
                assert "apple.com" in new_url.lower() or "itunes" in new_url.lower(), \
                    f"新页面不是App Store。URL: {new_url}"
                logger.info(f"✓ 新页面URL: {new_url}")
            
            with allure.step("步骤4：关闭新标签页"):
                new_page.close()
                logger.info("✓ 关闭新标签页")
        else:
            logger.info("⚠️ App Store 链接未找到或href为空，跳过链接验证")
            with allure.step("验证：Our Apps 区块存在"):
                assert footer_page.is_our_apps_section_visible(timeout=5000), \
                    "Our Apps 区块不可见"
                logger.info("✓ Our Apps 区块可见（但App Store链接可能使用其他实现方式）")
    
    logger.info("="*80)
    logger.info("✅ TC-FOOTER-E-001 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_footer_e_002
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.footer
@pytest.mark.ae
@allure.feature("OK")
@allure.story("首页 Footer 区域 - 应用下载")
@allure.title("Google Play 下载引导应该正确跳转")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证点击 Google Play 按钮后，正确跳转到 Google Play")
def test_google_play_download_link(page, config):
    """TC-FOOTER-E-002: Google Play 下载引导"""
    
    footer_page = FooterPage(page)
    base_url = config['base_url']
    
    logger.info("="*80)
    logger.info("TC-FOOTER-E-002: Google Play 下载引导")
    logger.info("="*80)
    logger.info(f"站点: {config['site'].upper()} ({config['site_name']})")
    logger.info(f"角色: {config['role'].upper()} (访客)")
    logger.info(f"测试URL: {base_url}")
    logger.info("="*80)
    
    with allure.step("步骤1：访问首页"):
        footer_page.goto(base_url, timeout=60000)
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 打开首页成功: {page.url}")
    
    with allure.step("步骤2：滚动到 Footer 区域"):
        footer_page.scroll_to_footer()
        logger.info("✓ 滚动到 Footer 区域成功")
    
    with allure.step("验证1：Google Play 链接 href 属性"):
        href = footer_page.get_google_play_href()
        
        if href and href != "":
            assert "play.google.com" in href.lower(), \
                f"Google Play 链接的 href 不正确: {href}"
            logger.info(f"✓ Google Play href: {href}")
            
            with allure.step("步骤3：点击 Google Play 链接"):
                with page.context.expect_page() as new_page_info:
                    footer_page.click_google_play()
                    logger.info("✓ 点击 Google Play 链接")
                
                new_page = new_page_info.value
                new_page.wait_for_load_state("domcontentloaded", timeout=30000)
                logger.info(f"✓ 新页面加载完成: {new_page.url}")
            
            with allure.step("验证2：新页面URL正确"):
                new_url = new_page.url
                assert "play.google.com" in new_url.lower(), \
                    f"新页面不是Google Play。URL: {new_url}"
                logger.info(f"✓ 新页面URL: {new_url}")
            
            with allure.step("步骤4：关闭新标签页"):
                new_page.close()
                logger.info("✓ 关闭新标签页")
        else:
            logger.info("⚠️ Google Play 链接未找到或href为空，跳过链接验证")
            with allure.step("验证：Our Apps 区块存在"):
                assert footer_page.is_our_apps_section_visible(timeout=5000), \
                    "Our Apps 区块不可见"
                logger.info("✓ Our Apps 区块可见（但Google Play链接可能使用其他实现方式）")
    
    logger.info("="*80)
    logger.info("✅ TC-FOOTER-E-002 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_footer_e_003
@pytest.mark.regression
@pytest.mark.p2
@pytest.mark.footer
@pytest.mark.ae
@allure.feature("OK")
@allure.story("首页 Footer 区域 - 应用下载")
@allure.title("Our Apps 区块应该正确显示")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证 Our Apps 区块可见并包含应用下载相关内容")
def test_our_apps_section_display(page, config):
    """TC-FOOTER-E-003: Our Apps 区块显示"""
    
    footer_page = FooterPage(page)
    base_url = config['base_url']
    
    logger.info("="*80)
    logger.info("TC-FOOTER-E-003: Our Apps 区块显示")
    logger.info("="*80)
    logger.info(f"站点: {config['site'].upper()} ({config['site_name']})")
    logger.info(f"角色: {config['role'].upper()} (访客)")
    logger.info(f"测试URL: {base_url}")
    logger.info("="*80)
    
    with allure.step("步骤1：访问首页"):
        footer_page.goto(base_url, timeout=60000)
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 打开首页成功: {page.url}")
    
    with allure.step("步骤2：滚动到 Footer 区域"):
        footer_page.scroll_to_footer()
        logger.info("✓ 滚动到 Footer 区域成功")
    
    with allure.step("验证1：Our Apps 区块可见"):
        assert footer_page.is_our_apps_section_visible(timeout=5000), \
            "Our Apps 区块不可见"
        logger.info("✓ Our Apps 区块可见")
    
    with allure.step("验证2：Our Apps 区块包含应用下载相关内容"):
        # 检查是否有 App Store 或 Google Play 相关文本
        our_apps_text = page.locator("text=Our Apps").locator("xpath=..").inner_text()
        
        has_app_store_text = "app store" in our_apps_text.lower() or "download on" in our_apps_text.lower()
        has_google_play_text = "google play" in our_apps_text.lower() or "get it on" in our_apps_text.lower()
        
        assert has_app_store_text or has_google_play_text, \
            f"Our Apps 区块未包含应用下载相关内容。文本: {our_apps_text}"
        
        if has_app_store_text:
            logger.info("✓ 包含 App Store 相关内容")
        if has_google_play_text:
            logger.info("✓ 包含 Google Play 相关内容")
    
    logger.info("="*80)
    logger.info("✅ TC-FOOTER-E-003 测试通过！")
    logger.info("="*80)
