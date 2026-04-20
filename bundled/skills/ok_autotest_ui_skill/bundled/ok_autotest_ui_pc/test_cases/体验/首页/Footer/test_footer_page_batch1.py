"""
AE站 - 首页底部 Footer 公共区域测试 - 批次1（基础展示与About Us）

测试站点：AE (https://ae.ok.com)
测试角色：Visitor (访客)
测试目标：验证 Footer 区域基础展示和 About Us 区块链接跳转功能

本脚本包含批次 1 的 4 个测试用例：
- TC-FOOTER-A-001：Footer 区域基础展示
- TC-FOOTER-A-002：Footer 区域位置固定
- TC-FOOTER-B-001：Terms of Use 链接跳转
- TC-FOOTER-B-002：Privacy Policy 链接跳转
"""
import pytest
import allure
from pages.footer_page import FooterPage
from utils.logger import setup_logger

logger = setup_logger()

# ============================================
# 测试环境配置（来自录制文档，录制与运行使用同一账号）
# ============================================
_CONFIG = {
    "site": "ae",
    "site_name": "阿联酋站 (AE OK.com)",
    "role": "visitor",
    "user_name": "ae_visitor_footer",
    "base_url": "https://ae.58v5.cn",
    "test_account": None,  # 访客模式，无需登录
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


@pytest.mark.case_id_footer_a_001
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.footer
@pytest.mark.ae
@allure.feature("OK")
@allure.story("首页 Footer 区域 - 基础展示")
@allure.title("Footer 区域基础展示元素应该完整可见")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证首页底部 Footer 区域的基本展示元素是否完整，包括 About Us、Help、Cookie、Our Apps 区块和版权信息")
def test_footer_basic_display(page, config):
    """TC-FOOTER-A-001: Footer 区域基础展示"""
    
    # ========== Arrange：准备测试数据和对象 ==========
    footer_page = FooterPage(page)
    base_url = config['base_url']
    
    # 记录测试配置
    logger.info("="*80)
    logger.info("TC-FOOTER-A-001: Footer 区域基础展示")
    logger.info("="*80)
    logger.info(f"站点: {config['site'].upper()} ({config['site_name']})")
    logger.info(f"角色: {config['role'].upper()} (访客)")
    logger.info(f"测试URL: {base_url}")
    logger.info("="*80)
    
    # ========== Act 阶段1：访问首页并滚动到 Footer ==========
    with allure.step("步骤1：访问首页"):
        footer_page.goto(base_url, timeout=60000)
        # 等待页面关键元素加载
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 打开首页成功: {page.url}")
    
    with allure.step("步骤2：滚动到页面底部"):
        footer_page.scroll_to_footer()
        logger.info("✓ 滚动到页面底部成功")
    
    # ========== Assert 阶段：验证 Footer 区域展示 ==========
    with allure.step("验证1：Footer 区域可见"):
        assert footer_page.is_footer_visible(timeout=5000), \
            "Footer 区域不可见"
        logger.info("✓ Footer 区域可见")
    
    with allure.step("验证2：About Us 区块可见"):
        assert footer_page.is_about_us_section_visible(timeout=5000), \
            "About Us 区块不可见"
        logger.info("✓ About Us 区块可见")
    
    with allure.step("验证3：Help 区块可见"):
        assert footer_page.is_help_section_visible(timeout=5000), \
            "Help 区块不可见"
        logger.info("✓ Help 区块可见")
    
    with allure.step("验证4：Cookie 区块可见"):
        assert footer_page.is_cookie_section_visible(timeout=5000), \
            "Cookie 区块不可见"
        logger.info("✓ Cookie 区块可见")
    
    with allure.step("验证5：Our Apps 区块可见"):
        assert footer_page.is_our_apps_section_visible(timeout=5000), \
            "Our Apps 区块不可见"
        logger.info("✓ Our Apps 区块可见")
    
    with allure.step("验证6：版权信息可见且正确"):
        assert footer_page.is_copyright_visible(timeout=5000), \
            "版权信息不可见"
        
        copyright_text = footer_page.get_copyright_text()
        assert "Servanan International Pte. Ltd." in copyright_text, \
            f"版权信息文本不正确，实际: {copyright_text}"
        logger.info(f"✓ 版权信息正确: {copyright_text}")
    
    logger.info("="*80)
    logger.info("✅ TC-FOOTER-A-001 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_footer_a_002
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.footer
@pytest.mark.ae
@allure.feature("OK")
@allure.story("首页 Footer 区域 - 布局验证")
@allure.title("Footer 区域位置应该固定在页面最底部")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证 Footer 始终位于页面最底部，不会被其他内容遮挡")
def test_footer_position_fixed(page, config):
    """TC-FOOTER-A-002: Footer 区域位置固定"""
    
    # ========== Arrange：准备测试数据和对象 ==========
    footer_page = FooterPage(page)
    base_url = config['base_url']
    
    # 记录测试配置
    logger.info("="*80)
    logger.info("TC-FOOTER-A-002: Footer 区域位置固定")
    logger.info("="*80)
    logger.info(f"站点: {config['site'].upper()} ({config['site_name']})")
    logger.info(f"角色: {config['role'].upper()} (访客)")
    logger.info(f"测试URL: {base_url}")
    logger.info("="*80)
    
    # ========== Act 阶段1：访问首页并滚动到 Footer ==========
    with allure.step("步骤1：访问首页"):
        footer_page.goto(base_url, timeout=60000)
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 打开首页成功: {page.url}")
    
    with allure.step("步骤2：记录页面总高度"):
        page_height = page.evaluate("document.body.scrollHeight")
        logger.info(f"✓ 页面总高度: {page_height}px")
    
    with allure.step("步骤3：滚动到页面底部"):
        footer_page.scroll_to_footer()
        logger.info("✓ 滚动到页面底部成功")
    
    # ========== Assert 阶段：验证 Footer 位置 ==========
    with allure.step("验证：Footer 位于页面最底部"):
        footer_position = footer_page.get_footer_position()
        
        assert footer_position["is_at_bottom"], \
            f"Footer 未位于页面最底部。Footer Y: {footer_position['y']}, " \
            f"页面高度: {footer_position['page_height']}"
        
        logger.info(f"✓ Footer 位于页面最底部")
        logger.info(f"  - Footer Y 坐标: {footer_position['y']}px")
        logger.info(f"  - Footer 高度: {footer_position['height']}px")
        logger.info(f"  - 页面总高度: {footer_position['page_height']}px")
    
    with allure.step("验证：Footer 下方无其他内容"):
        # Footer 底部位置应该接近页面总高度
        footer_bottom = footer_position["y"] + footer_position["height"]
        distance_from_bottom = footer_position["page_height"] - footer_bottom
        
        assert distance_from_bottom < 50, \
            f"Footer 下方有其他内容，距离底部: {distance_from_bottom}px"
        logger.info(f"✓ Footer 下方无其他内容（距离底部 {distance_from_bottom}px）")
    
    logger.info("="*80)
    logger.info("✅ TC-FOOTER-A-002 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_footer_b_001
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.footer
@pytest.mark.ae
@allure.feature("OK")
@allure.story("首页 Footer 区域 - About Us 链接")
@allure.title("Terms of Use 链接应该正确跳转到服务条款页面")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证点击 Terms of Use 链接后，正确跳转到服务条款页面，且在新标签页打开")
def test_terms_of_use_link(page, config):
    """TC-FOOTER-B-001: Terms of Use 链接跳转"""
    
    # ========== Arrange：准备测试数据和对象 ==========
    footer_page = FooterPage(page)
    base_url = config['base_url']
    
    # 记录测试配置
    logger.info("="*80)
    logger.info("TC-FOOTER-B-001: Terms of Use 链接跳转")
    logger.info("="*80)
    logger.info(f"站点: {config['site'].upper()} ({config['site_name']})")
    logger.info(f"角色: {config['role'].upper()} (访客)")
    logger.info(f"测试URL: {base_url}")
    logger.info("="*80)
    
    # ========== Act 阶段1：访问首页并滚动到 Footer ==========
    with allure.step("步骤1：访问首页"):
        footer_page.goto(base_url, timeout=60000)
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 打开首页成功: {page.url}")
    
    with allure.step("步骤2：滚动到 Footer 区域"):
        footer_page.scroll_to_footer()
        logger.info("✓ 滚动到 Footer 区域成功")
    
    # ========== Assert 阶段1：验证链接属性 ==========
    with allure.step("验证1：Terms of Use 链接 href 属性"):
        href = footer_page.get_terms_of_use_href()
        assert href is not None and href != "", \
            "Terms of Use 链接的 href 属性为空"
        logger.info(f"✓ Terms of Use href: {href}")
    
    with allure.step("验证2：Terms of Use 链接在新标签页打开"):
        target = footer_page.get_terms_of_use_target()
        assert target == "_blank", \
            f"Terms of Use 链接的 target 应为 _blank，实际: {target}"
        logger.info(f"✓ Terms of Use target=_blank")
    
    # ========== Act 阶段2：点击链接并验证跳转 ==========
    with allure.step("步骤3：点击 Terms of Use 链接"):
        with page.context.expect_page() as new_page_info:
            footer_page.click_terms_of_use()
            logger.info("✓ 点击 Terms of Use 链接")
        
        new_page = new_page_info.value
        # 等待新页面加载
        new_page.wait_for_load_state("domcontentloaded", timeout=30000)
        new_page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 新页面加载完成: {new_page.url}")
    
    # ========== Assert 阶段2：验证新页面内容 ==========
    with allure.step("验证3：新页面URL和标题正确"):
        new_url = new_page.url
        new_title = new_page.title()
        
        assert "terms" in new_url.lower() or "terms" in new_title.lower(), \
            f"新页面不是服务条款页面。URL: {new_url}, 标题: {new_title}"
        logger.info(f"✓ 新页面URL: {new_url}")
        logger.info(f"✓ 新页面标题: {new_title}")
    
    # 关闭新标签页
    with allure.step("步骤4：关闭新标签页"):
        new_page.close()
        logger.info("✓ 关闭新标签页")
    
    logger.info("="*80)
    logger.info("✅ TC-FOOTER-B-001 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_footer_b_002
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.footer
@pytest.mark.ae
@allure.feature("OK")
@allure.story("首页 Footer 区域 - About Us 链接")
@allure.title("Privacy Policy 链接应该正确跳转到隐私政策页面")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证点击 Privacy Policy 链接后，正确跳转到隐私政策页面，且在新标签页打开")
def test_privacy_policy_link(page, config):
    """TC-FOOTER-B-002: Privacy Policy 链接跳转"""
    
    # ========== Arrange：准备测试数据和对象 ==========
    footer_page = FooterPage(page)
    base_url = config['base_url']
    
    # 记录测试配置
    logger.info("="*80)
    logger.info("TC-FOOTER-B-002: Privacy Policy 链接跳转")
    logger.info("="*80)
    logger.info(f"站点: {config['site'].upper()} ({config['site_name']})")
    logger.info(f"角色: {config['role'].upper()} (访客)")
    logger.info(f"测试URL: {base_url}")
    logger.info("="*80)
    
    # ========== Act 阶段1：访问首页并滚动到 Footer ==========
    with allure.step("步骤1：访问首页"):
        footer_page.goto(base_url, timeout=60000)
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 打开首页成功: {page.url}")
    
    with allure.step("步骤2：滚动到 Footer 区域"):
        footer_page.scroll_to_footer()
        logger.info("✓ 滚动到 Footer 区域成功")
    
    # ========== Assert 阶段1：验证链接属性 ==========
    with allure.step("验证1：Privacy Policy 链接 href 属性"):
        href = footer_page.get_privacy_policy_href()
        assert href is not None and href != "", \
            "Privacy Policy 链接的 href 属性为空"
        logger.info(f"✓ Privacy Policy href: {href}")
    
    with allure.step("验证2：Privacy Policy 链接在新标签页打开"):
        target = footer_page.get_privacy_policy_target()
        assert target == "_blank", \
            f"Privacy Policy 链接的 target 应为 _blank，实际: {target}"
        logger.info(f"✓ Privacy Policy target=_blank")
    
    # ========== Act 阶段2：点击链接并验证跳转 ==========
    with allure.step("步骤3：点击 Privacy Policy 链接"):
        with page.context.expect_page() as new_page_info:
            footer_page.click_privacy_policy()
            logger.info("✓ 点击 Privacy Policy 链接")
        
        new_page = new_page_info.value
        # 等待新页面加载
        new_page.wait_for_load_state("domcontentloaded", timeout=30000)
        new_page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 新页面加载完成: {new_page.url}")
    
    # ========== Assert 阶段2：验证新页面内容 ==========
    with allure.step("验证3：新页面URL和标题正确"):
        new_url = new_page.url
        new_title = new_page.title()
        
        assert "privacy" in new_url.lower() or "privacy" in new_title.lower(), \
            f"新页面不是隐私政策页面。URL: {new_url}, 标题: {new_title}"
        logger.info(f"✓ 新页面URL: {new_url}")
        logger.info(f"✓ 新页面标题: {new_title}")
    
    # 关闭新标签页
    with allure.step("步骤4：关闭新标签页"):
        new_page.close()
        logger.info("✓ 关闭新标签页")
    
    logger.info("="*80)
    logger.info("✅ TC-FOOTER-B-002 测试通过！")
    logger.info("="*80)
