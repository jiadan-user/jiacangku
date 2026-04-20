"""
AE站 - 首页底部 Footer 公共区域测试 - 批次2（Help 链接）

测试站点：AE (https://ae.ok.com)
测试角色：Visitor (访客)
测试目标：验证 Footer 区域 Help 区块的链接跳转功能

本脚本包含批次 2 的 5 个测试用例：
- TC-FOOTER-C-001：Help 链接跳转
- TC-FOOTER-C-002：Contact Us 链接跳转
- TC-FOOTER-C-003：FAQ 链接跳转
- TC-FOOTER-C-004：Support and feedback 链接跳转
- TC-FOOTER-C-005：Return Policy 链接跳转
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


@pytest.mark.case_id_footer_c_001
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.footer
@pytest.mark.ae
@allure.feature("OK")
@allure.story("首页 Footer 区域 - Help 区块")
@allure.title("Help 区块应该正确显示")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证 Help 区块标题和下属链接正确显示")
def test_help_section_display(page, config):
    """TC-FOOTER-C-001: Help 区块显示"""
    
    footer_page = FooterPage(page)
    base_url = config['base_url']
    
    logger.info("="*80)
    logger.info("TC-FOOTER-C-001: Help 区块显示")
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
    
    with allure.step("验证1：Help 区块标题可见"):
        assert footer_page.is_help_section_visible(timeout=5000), \
            "Help 区块不可见"
        logger.info("✓ Help 区块可见")
    
    with allure.step("验证2：Help 区块下的链接可见"):
        contact_us_visible = footer_page.is_contact_us_link_visible(timeout=3000)
        faq_visible = footer_page.is_faq_link_visible(timeout=3000)
        
        assert contact_us_visible or faq_visible, \
            "Help 区块下没有可见的链接"
        
        if contact_us_visible:
            logger.info("✓ Contact Us 链接可见")
        if faq_visible:
            logger.info("✓ FAQ 链接可见")
    
    logger.info("="*80)
    logger.info("✅ TC-FOOTER-C-001 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_footer_c_002
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.footer
@pytest.mark.ae
@allure.feature("OK")
@allure.story("首页 Footer 区域 - Help 链接")
@allure.title("Contact Us 链接应该正确跳转到联系我们页面")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证点击 Contact Us 链接后，正确跳转到联系我们页面，且在新标签页打开")
def test_contact_us_link(page, config):
    """TC-FOOTER-C-002: Contact Us 链接跳转"""
    
    footer_page = FooterPage(page)
    base_url = config['base_url']
    
    logger.info("="*80)
    logger.info("TC-FOOTER-C-002: Contact Us 链接跳转")
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
    
    with allure.step("验证1：Contact Us 链接 href 属性"):
        href = footer_page.get_contact_us_href()
        assert href is not None and href != "", \
            "Contact Us 链接的 href 属性为空"
        logger.info(f"✓ Contact Us href: {href}")
    
    with allure.step("步骤3：点击 Contact Us 链接"):
        with page.context.expect_page() as new_page_info:
            footer_page.click_contact_us()
            logger.info("✓ 点击 Contact Us 链接")
        
        new_page = new_page_info.value
        new_page.wait_for_load_state("domcontentloaded", timeout=30000)
        new_page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 新页面加载完成: {new_page.url}")
    
    with allure.step("验证2：新页面URL和内容正确"):
        new_url = new_page.url
        new_title = new_page.title()
        
        assert "contact" in new_url.lower() or "contact" in new_title.lower(), \
            f"新页面不是联系我们页面。URL: {new_url}, 标题: {new_title}"
        logger.info(f"✓ 新页面URL: {new_url}")
        logger.info(f"✓ 新页面标题: {new_title}")
    
    with allure.step("步骤4：关闭新标签页"):
        new_page.close()
        logger.info("✓ 关闭新标签页")
    
    logger.info("="*80)
    logger.info("✅ TC-FOOTER-C-002 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_footer_c_003
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.footer
@pytest.mark.ae
@allure.feature("OK")
@allure.story("首页 Footer 区域 - Help 链接")
@allure.title("FAQ 链接应该正确跳转到常见问题页面")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证点击 FAQ 链接后，正确跳转到常见问题页面，且在新标签页打开")
def test_faq_link(page, config):
    """TC-FOOTER-C-003: FAQ 链接跳转"""
    
    footer_page = FooterPage(page)
    base_url = config['base_url']
    
    logger.info("="*80)
    logger.info("TC-FOOTER-C-003: FAQ 链接跳转")
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
    
    with allure.step("验证1：FAQ 链接 href 属性"):
        href = footer_page.get_faq_href()
        assert href is not None and href != "", \
            "FAQ 链接的 href 属性为空"
        logger.info(f"✓ FAQ href: {href}")
    
    with allure.step("步骤3：点击 FAQ 链接"):
        with page.context.expect_page() as new_page_info:
            footer_page.click_faq()
            logger.info("✓ 点击 FAQ 链接")
        
        new_page = new_page_info.value
        new_page.wait_for_load_state("domcontentloaded", timeout=30000)
        new_page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 新页面加载完成: {new_page.url}")
    
    with allure.step("验证2：新页面URL和内容正确"):
        new_url = new_page.url
        new_title = new_page.title()
        
        assert "faq" in new_url.lower() or "faq" in new_title.lower(), \
            f"新页面不是FAQ页面。URL: {new_url}, 标题: {new_title}"
        logger.info(f"✓ 新页面URL: {new_url}")
        logger.info(f"✓ 新页面标题: {new_title}")
    
    with allure.step("步骤4：关闭新标签页"):
        new_page.close()
        logger.info("✓ 关闭新标签页")
    
    logger.info("="*80)
    logger.info("✅ TC-FOOTER-C-003 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_footer_c_004
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.footer
@pytest.mark.ae
@allure.feature("OK")
@allure.story("首页 Footer 区域 - Help 链接")
@allure.title("Support and feedback 链接应该正确跳转到支持反馈页面")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证点击 Support and feedback 链接后，正确跳转到支持反馈页面，且在新标签页打开")
def test_support_feedback_link(page, config):
    """TC-FOOTER-C-004: Support and feedback 链接跳转"""
    
    footer_page = FooterPage(page)
    base_url = config['base_url']
    
    logger.info("="*80)
    logger.info("TC-FOOTER-C-004: Support and feedback 链接跳转")
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
    
    with allure.step("验证1：Support and feedback 链接 href 属性"):
        href = footer_page.get_support_feedback_href()
        assert href is not None and href != "", \
            "Support and feedback 链接的 href 属性为空"
        logger.info(f"✓ Support and feedback href: {href}")
    
    with allure.step("步骤3：点击 Support and feedback 链接"):
        with page.context.expect_page() as new_page_info:
            footer_page.click_support_feedback()
            logger.info("✓ 点击 Support and feedback 链接")
        
        new_page = new_page_info.value
        new_page.wait_for_load_state("domcontentloaded", timeout=30000)
        new_page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 新页面加载完成: {new_page.url}")
    
    with allure.step("验证2：新页面URL和内容正确"):
        new_url = new_page.url
        new_title = new_page.title()
        
        assert "support" in new_url.lower() or "feedback" in new_url.lower() or \
               "support" in new_title.lower() or "feedback" in new_title.lower(), \
            f"新页面不是支持反馈页面。URL: {new_url}, 标题: {new_title}"
        logger.info(f"✓ 新页面URL: {new_url}")
        logger.info(f"✓ 新页面标题: {new_title}")
    
    with allure.step("步骤4：关闭新标签页"):
        new_page.close()
        logger.info("✓ 关闭新标签页")
    
    logger.info("="*80)
    logger.info("✅ TC-FOOTER-C-004 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_footer_c_005
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.footer
@pytest.mark.ae
@allure.feature("OK")
@allure.story("首页 Footer 区域 - Help 链接")
@allure.title("Return Policy 链接应该正确跳转到退货政策页面")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证点击 Return Policy 链接后，正确跳转到退货政策页面，且在新标签页打开")
def test_return_policy_link(page, config):
    """TC-FOOTER-C-005: Return Policy 链接跳转"""
    
    footer_page = FooterPage(page)
    base_url = config['base_url']
    
    logger.info("="*80)
    logger.info("TC-FOOTER-C-005: Return Policy 链接跳转")
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
    
    with allure.step("验证1：Return Policy 链接 href 属性"):
        href = footer_page.get_return_policy_href()
        assert href is not None and href != "", \
            "Return Policy 链接的 href 属性为空"
        logger.info(f"✓ Return Policy href: {href}")
    
    with allure.step("步骤3：点击 Return Policy 链接"):
        with page.context.expect_page() as new_page_info:
            footer_page.click_return_policy()
            logger.info("✓ 点击 Return Policy 链接")
        
        new_page = new_page_info.value
        new_page.wait_for_load_state("domcontentloaded", timeout=30000)
        new_page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 新页面加载完成: {new_page.url}")
    
    with allure.step("验证2：新页面URL和内容正确"):
        new_url = new_page.url
        new_title = new_page.title()
        
        assert "return" in new_url.lower() or "policy" in new_url.lower() or \
               "return" in new_title.lower(), \
            f"新页面不是退货政策页面。URL: {new_url}, 标题: {new_title}"
        logger.info(f"✓ 新页面URL: {new_url}")
        logger.info(f"✓ 新页面标题: {new_title}")
    
    with allure.step("步骤4：关闭新标签页"):
        new_page.close()
        logger.info("✓ 关闭新标签页")
    
    logger.info("="*80)
    logger.info("✅ TC-FOOTER-C-005 测试通过！")
    logger.info("="*80)
