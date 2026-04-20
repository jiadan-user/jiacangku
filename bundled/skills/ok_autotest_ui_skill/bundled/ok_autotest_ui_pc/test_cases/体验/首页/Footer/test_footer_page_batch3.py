"""
AE站 - 首页底部 Footer 公共区域测试 - 批次3（Help 链接扩展 + Cookie 基础）

测试站点：AE (https://ae.ok.com)
测试角色：Visitor (访客)
测试目标：验证 Footer 区域 Refund Policy 和 Cookie Policy 链接跳转功能

本脚本包含批次 3 的 2 个测试用例（Cookie Settings 相关用例因页面结构调整暂时跳过）：
- TC-FOOTER-C-006：Refund Policy 链接跳转
- TC-FOOTER-D-001：Cookie Policy 链接跳转

注意：TC-FOOTER-D-002~D-009（Cookie Settings 相关）需要进一步确认页面实现方式
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


@pytest.mark.case_id_footer_c_006
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.footer
@pytest.mark.ae
@allure.feature("OK")
@allure.story("首页 Footer 区域 - Help 链接")
@allure.title("Refund Policy 链接应该正确跳转到退款政策页面")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证点击 Refund Policy 链接后，正确跳转到退款政策页面，且在新标签页打开")
def test_refund_policy_link(page, config):
    """TC-FOOTER-C-006: Refund Policy 链接跳转"""
    
    footer_page = FooterPage(page)
    base_url = config['base_url']
    
    logger.info("="*80)
    logger.info("TC-FOOTER-C-006: Refund Policy 链接跳转")
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
    
    with allure.step("验证1：Refund Policy 链接 href 属性"):
        href = footer_page.get_refund_policy_href()
        assert href is not None and href != "", \
            "Refund Policy 链接的 href 属性为空"
        logger.info(f"✓ Refund Policy href: {href}")
    
    with allure.step("步骤3：点击 Refund Policy 链接"):
        with page.context.expect_page() as new_page_info:
            footer_page.click_refund_policy()
            logger.info("✓ 点击 Refund Policy 链接")
        
        new_page = new_page_info.value
        new_page.wait_for_load_state("domcontentloaded", timeout=30000)
        new_page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 新页面加载完成: {new_page.url}")
    
    with allure.step("验证2：新页面URL和内容正确"):
        new_url = new_page.url
        new_title = new_page.title()
        
        assert "refund" in new_url.lower() or "policy" in new_url.lower() or \
               "refund" in new_title.lower(), \
            f"新页面不是退款政策页面。URL: {new_url}, 标题: {new_title}"
        logger.info(f"✓ 新页面URL: {new_url}")
        logger.info(f"✓ 新页面标题: {new_title}")
    
    with allure.step("步骤4：关闭新标签页"):
        new_page.close()
        logger.info("✓ 关闭新标签页")
    
    logger.info("="*80)
    logger.info("✅ TC-FOOTER-C-006 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_footer_d_001
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.footer
@pytest.mark.ae
@allure.feature("OK")
@allure.story("首页 Footer 区域 - Cookie 管理")
@allure.title("Cookie Policy 链接应该正确跳转到 Cookie 政策页面")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证点击 Cookie Policy 链接后，正确跳转到 Cookie 政策页面，且在新标签页打开")
def test_cookie_policy_link(page, config):
    """TC-FOOTER-D-001: Cookie Policy 链接跳转"""
    
    footer_page = FooterPage(page)
    base_url = config['base_url']
    
    logger.info("="*80)
    logger.info("TC-FOOTER-D-001: Cookie Policy 链接跳转")
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
    
    with allure.step("验证1：Cookie Policy 链接 href 属性"):
        href = footer_page.get_cookie_policy_href()
        assert href is not None and href != "", \
            "Cookie Policy 链接的 href 属性为空"
        logger.info(f"✓ Cookie Policy href: {href}")
    
    with allure.step("验证2：Cookie Policy 链接在新标签页打开"):
        # 检查 target 属性
        target = page.locator(footer_page.COOKIE_POLICY_LINK).first.get_attribute("target")
        assert target == "_blank", \
            f"Cookie Policy 链接的 target 应为 _blank，实际: {target}"
        logger.info(f"✓ Cookie Policy target=_blank")
    
    with allure.step("步骤3：点击 Cookie Policy 链接"):
        with page.context.expect_page() as new_page_info:
            footer_page.click_cookie_policy()
            logger.info("✓ 点击 Cookie Policy 链接")
        
        new_page = new_page_info.value
        new_page.wait_for_load_state("domcontentloaded", timeout=30000)
        new_page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 新页面加载完成: {new_page.url}")
    
    with allure.step("验证3：新页面URL和内容正确"):
        new_url = new_page.url
        new_title = new_page.title()
        
        assert "cookie" in new_url.lower() or "cookie" in new_title.lower(), \
            f"新页面不是Cookie政策页面。URL: {new_url}, 标题: {new_title}"
        logger.info(f"✓ 新页面URL: {new_url}")
        logger.info(f"✓ 新页面标题: {new_title}")
    
    with allure.step("步骤4：关闭新标签页"):
        new_page.close()
        logger.info("✓ 关闭新标签页")
    
    logger.info("="*80)
    logger.info("✅ TC-FOOTER-D-001 测试通过！")
    logger.info("="*80)
