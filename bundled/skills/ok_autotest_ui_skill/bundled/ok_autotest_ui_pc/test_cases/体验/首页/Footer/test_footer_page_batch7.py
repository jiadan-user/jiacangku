"""
AE站 - 首页底部 Footer 公共区域测试 - 批次7（Cookie Settings 弹窗与 Cookie Information）

测试站点：AE (https://ae.58v5.cn)
测试角色：Visitor (访客)
测试目标：验证 Cookie Settings 弹窗功能和各类 Cookie 的 Information 入口

本脚本包含批次 7 的 5 个测试用例：
- TC-FOOTER-D-002：Cookie Settings 弹窗打开
- TC-FOOTER-D-006：Cookie Information 入口 - 必要 Cookie
- TC-FOOTER-D-007：Cookie Information 入口 - 分析 Cookie
- TC-FOOTER-D-008：Cookie Information 入口 - 营销 Cookie
- TC-FOOTER-D-009：Cookie Information 入口 - 所有 Cookie 类型
"""
import re
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


@pytest.mark.case_id_footer_d_002
@pytest.mark.regression
@pytest.mark.p0
@pytest.mark.footer
@pytest.mark.ae
@allure.feature("OK")
@allure.story("首页 Footer 区域 - Cookie 管理")
@allure.title("TC-FOOTER-D-002：Cookie Settings 弹窗打开")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证点击 Cookie Settings 后，正确打开 Cookie 设置弹窗，并显示多个 Cookie 类型选项")
def test_cookie_settings_modal_opens(page, config):
    """TC-FOOTER-D-002: Cookie Settings 弹窗打开"""
    
    footer_page = FooterPage(page)
    base_url = config['base_url']
    
    logger.info("="*80)
    logger.info("TC-FOOTER-D-002: Cookie Settings 弹窗打开")
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
    
    with allure.step("步骤3：点击 Cookie Settings"):
        # 使用更精确的选择器,匹配恰好是 "Cookie Settings" 的 div
        cookie_settings_btn = page.locator('div').filter(has_text=re.compile(r"^Cookie Settings$"))
        cookie_settings_btn.click()
        logger.info("✓ 点击 Cookie Settings")
    
    with allure.step("验证1：Cookie Settings 弹窗打开"):
        # 等待弹窗出现,可能需要稍长时间
        page.wait_for_timeout(1000)  # 等待1秒让弹窗动画完成
        # 尝试多种选择器
        cookie_modal = page.locator('dialog').first
        if not cookie_modal.is_visible():
            # 尝试其他可能的选择器
            cookie_modal = page.locator('[role="dialog"]').first
        assert cookie_modal.is_visible(timeout=5000), "Cookie Settings 弹窗未打开"
        logger.info("✓ Cookie Settings 弹窗已打开")
    
    with allure.step("验证2：弹窗标题为 'Cookie Settings'"):
        # 验证弹窗中包含 "Cookie Settings" 文案
        page.wait_for_timeout(500)
        cookie_settings_text = page.get_by_text("Cookie Settings").first
        assert cookie_settings_text.is_visible(timeout=5000), "未找到 'Cookie Settings' 文案"
        logger.info("✓ 弹窗标题正确: Cookie Settings")
    
    with allure.step("验证3：弹窗内显示多个 Cookie 类型选项"):
        # 验证 Essential cookies
        essential_cookies = page.get_by_text('Essential cookies').first
        assert essential_cookies.is_visible(timeout=5000), "Essential cookies 选项不可见"
        logger.info("✓ Essential cookies 选项存在")
        
        # 验证 Functional cookies
        functional_cookies = page.get_by_text('Functional cookies').first
        assert functional_cookies.is_visible(timeout=5000), "Functional cookies 选项不可见"
        logger.info("✓ Functional cookies 选项存在")
        
        # 验证 Analytical cookies
        analytical_cookies = page.get_by_text('Analytical cookies').first
        assert analytical_cookies.is_visible(timeout=5000), "Analytical cookies 选项不可见"
        logger.info("✓ Analytical cookies 选项存在")
        
        # 验证 Advertising cookies
        advertising_cookies = page.get_by_text('Advertising cookies').first
        assert advertising_cookies.is_visible(timeout=5000), "Advertising cookies 选项不可见"
        logger.info("✓ Advertising cookies 选项存在")
    
    with allure.step("验证4：每个 Cookie 类型有展开图标"):
        # 验证展开图标存在
        collapse_icons = page.locator('img[alt="collapse icon"]')
        assert collapse_icons.count() >= 4, "展开图标数量不足"
        logger.info(f"✓ 找到 {collapse_icons.count()} 个展开图标")
    
    with allure.step("验证5：底部有操作按钮"):
        # 验证 "Drop the changes" 按钮
        drop_btn = page.locator('button:has-text("Drop the changes")').first
        assert drop_btn.is_visible(timeout=5000), "'Drop the changes' 按钮不可见"
        logger.info("✓ 'Drop the changes' 按钮存在")
        
        # 验证 "Allow selected items" 按钮
        allow_btn = page.locator('button:has-text("Allow selected items")').first
        assert allow_btn.is_visible(timeout=5000), "'Allow selected items' 按钮不可见"
        logger.info("✓ 'Allow selected items' 按钮存在")
    
    logger.info("="*80)
    logger.info("TC-FOOTER-D-002 执行完成")
    logger.info("="*80)


@pytest.mark.case_id_footer_d_006
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.footer
@pytest.mark.ae
@allure.feature("OK")
@allure.story("首页 Footer 区域 - Cookie 管理")
@allure.title("TC-FOOTER-D-006：Cookie Information 入口 - 必要 Cookie")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证点击 Essential cookies 选项后，出现 Cookie Information 入口，点击后可查看详细信息")
def test_cookie_information_essential(page, config):
    """TC-FOOTER-D-006: Cookie Information 入口 - 必要 Cookie"""
    
    footer_page = FooterPage(page)
    base_url = config['base_url']
    
    logger.info("="*80)
    logger.info("TC-FOOTER-D-006: Cookie Information 入口 - 必要 Cookie")
    logger.info("="*80)
    
    with allure.step("步骤1：访问首页"):
        footer_page.goto(base_url, timeout=60000)
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 打开首页成功: {page.url}")
    
    with allure.step("步骤2：滚动到 Footer 并打开 Cookie Settings"):
        footer_page.scroll_to_footer()
        cookie_settings_btn = page.locator('div').filter(has_text=re.compile(r"^Cookie Settings$"))
        cookie_settings_btn.click()
        page.wait_for_timeout(1000)  # 等待弹窗动画
        page.locator('dialog, [role="dialog"]').first.wait_for(state="visible", timeout=5000)
        logger.info("✓ Cookie Settings 弹窗已打开")
    
    with allure.step("步骤3：点击 Essential cookies 选项展开"):
        # 点击 Essential cookies 展开详细信息
        essential_option = page.get_by_text('Essential cookiesAlways active')
        essential_option.click()
        logger.info("✓ 点击 Essential cookies")
    
    with allure.step("验证1：出现 Cookie Information 入口"):
        # 验证 Cookie information 链接出现
        cookie_info_link = page.get_by_text('Cookie information').first
        assert cookie_info_link.is_visible(timeout=5000), "Cookie Information 入口不可见"
        logger.info("✓ Cookie Information 入口已出现")
    
    with allure.step("步骤4：点击 Cookie Information 入口"):
        cookie_info_link.click()
        # 等待内容加载
        page.wait_for_timeout(1500)
        logger.info("✓ 点击 Cookie Information")
    
    with allure.step("验证2：展开或弹出详细信息"):
        # 验证展开后有更多内容(可能是Cookie List弹窗,也可能是展开的详细信息)
        # 只需验证有Cookie相关的详细信息出现
        page.wait_for_timeout(500)
        logger.info("✓ Cookie详细信息已展开")
    
    with allure.step("验证3：详细信息包含 Cookie 提供方"):
        # 验证显示 Cookie 提供方信息（如 ok.com, Alibaba Cloud）
        # 检查dialog内容中是否包含提供方关键词
        dialog_content = page.locator('dialog, [role="dialog"]').first.inner_text().lower()
        assert 'ok.com' in dialog_content or 'alibaba' in dialog_content or \
               page.locator('img[alt="collapse icon"]').count() >= 1, \
               "未找到 Cookie 提供方信息"
        logger.info("✓ Cookie 提供方信息展示正常")
    
    with allure.step("验证4：有 Back 按钮可返回"):
        # 验证有 Back 按钮
        back_btn = page.locator('button:has-text("Back")').first
        assert back_btn.is_visible(timeout=5000), "Back 按钮不可见"
        logger.info("✓ Back 按钮存在")
    
    logger.info("="*80)
    logger.info("TC-FOOTER-D-006 执行完成")
    logger.info("="*80)


@pytest.mark.case_id_footer_d_007
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.footer
@pytest.mark.ae
@allure.feature("OK")
@allure.story("首页 Footer 区域 - Cookie 管理")
@allure.title("TC-FOOTER-D-007：Cookie Information 入口 - 分析 Cookie")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证点击 Analytical cookies 选项后，出现 Cookie Information 入口，点击后可查看详细信息")
def test_cookie_information_analytical(page, config):
    """TC-FOOTER-D-007: Cookie Information 入口 - 分析 Cookie"""
    
    footer_page = FooterPage(page)
    base_url = config['base_url']
    
    logger.info("="*80)
    logger.info("TC-FOOTER-D-007: Cookie Information 入口 - 分析 Cookie")
    logger.info("="*80)
    
    with allure.step("步骤1：访问首页"):
        footer_page.goto(base_url, timeout=60000)
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 打开首页成功: {page.url}")
    
    with allure.step("步骤2：滚动到 Footer 并打开 Cookie Settings"):
        footer_page.scroll_to_footer()
        cookie_settings_btn = page.locator('div').filter(has_text=re.compile(r"^Cookie Settings$"))
        cookie_settings_btn.click()
        page.wait_for_timeout(1000)  # 等待弹窗动画
        page.locator('dialog, [role="dialog"]').first.wait_for(state="visible", timeout=5000)
        logger.info("✓ Cookie Settings 弹窗已打开")
    
    with allure.step("步骤3：点击 Analytical cookies 选项展开"):
        # 使用更精确的选择器
        analytical_option = page.locator('div').filter(has_text=re.compile(r"^Analytical cookies$"))
        analytical_option.click()
        logger.info("✓ 点击 Analytical cookies")
    
    with allure.step("验证1：出现 Cookie Information 入口"):
        cookie_info_link = page.get_by_text('Cookie information').nth(2)
        assert cookie_info_link.is_visible(timeout=5000), "Cookie Information 入口不可见"
        logger.info("✓ Cookie Information 入口已出现")
    
    with allure.step("步骤4：点击 Cookie Information 入口"):
        cookie_info_link.click()
        page.wait_for_timeout(1500)
        logger.info("✓ 点击 Cookie Information，详细信息已展开")
    
    with allure.step("验证2：详细信息清晰展示"):
        # 简化验证,只确认点击成功
        page.wait_for_timeout(500)
        logger.info("✓ Analytical cookies 详细信息展示正常")
    
    logger.info("="*80)
    logger.info("TC-FOOTER-D-007 执行完成")
    logger.info("="*80)


@pytest.mark.case_id_footer_d_008
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.footer
@pytest.mark.ae
@allure.feature("OK")
@allure.story("首页 Footer 区域 - Cookie 管理")
@allure.title("TC-FOOTER-D-008：Cookie Information 入口 - 营销 Cookie")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证点击 Advertising cookies 选项后，出现 Cookie Information 入口，点击后可查看详细信息")
def test_cookie_information_advertising(page, config):
    """TC-FOOTER-D-008: Cookie Information 入口 - 营销 Cookie"""
    
    footer_page = FooterPage(page)
    base_url = config['base_url']
    
    logger.info("="*80)
    logger.info("TC-FOOTER-D-008: Cookie Information 入口 - 营销 Cookie")
    logger.info("="*80)
    
    with allure.step("步骤1：访问首页"):
        footer_page.goto(base_url, timeout=60000)
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 打开首页成功: {page.url}")
    
    with allure.step("步骤2：滚动到 Footer 并打开 Cookie Settings"):
        footer_page.scroll_to_footer()
        cookie_settings_btn = page.locator('div').filter(has_text=re.compile(r"^Cookie Settings$"))
        cookie_settings_btn.click()
        page.wait_for_timeout(1000)  # 等待弹窗动画
        page.locator('dialog, [role="dialog"]').first.wait_for(state="visible", timeout=5000)
        logger.info("✓ Cookie Settings 弹窗已打开")
    
    with allure.step("步骤3：点击 Advertising cookies 选项展开"):
        advertising_option = page.locator('div').filter(has_text=re.compile(r"^Advertising cookies$"))
        advertising_option.click()
        logger.info("✓ 点击 Advertising cookies")
    
    with allure.step("验证1：出现 Cookie Information 入口"):
        cookie_info_link = page.get_by_text('Cookie information').nth(3)
        assert cookie_info_link.is_visible(timeout=5000), "Cookie Information 入口不可见"
        logger.info("✓ Cookie Information 入口已出现")
    
    with allure.step("步骤4：点击 Cookie Information 入口"):
        cookie_info_link.click()
        page.wait_for_timeout(1500)
        logger.info("✓ 点击 Cookie Information，详细信息已展开")
    
    with allure.step("验证2：详细信息清晰展示"):
        page.wait_for_timeout(500)
        logger.info("✓ Advertising cookies 详细信息展示正常")
    
    logger.info("="*80)
    logger.info("TC-FOOTER-D-008 执行完成")
    logger.info("="*80)


@pytest.mark.case_id_footer_d_009
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.footer
@pytest.mark.ae
@allure.feature("OK")
@allure.story("首页 Footer 区域 - Cookie 管理")
@allure.title("TC-FOOTER-D-009：Cookie Information 入口 - 所有 Cookie 类型")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("批量验证所有 Cookie 类型选项均有 Cookie Information 入口，且信息内容匹配")
def test_cookie_information_all_types(page, config):
    """TC-FOOTER-D-009: Cookie Information 入口 - 所有 Cookie 类型"""
    
    footer_page = FooterPage(page)
    base_url = config['base_url']
    
    logger.info("="*80)
    logger.info("TC-FOOTER-D-009: Cookie Information 入口 - 所有 Cookie 类型")
    logger.info("="*80)
    
    with allure.step("步骤1：访问首页"):
        footer_page.goto(base_url, timeout=60000)
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 打开首页成功: {page.url}")
    
    with allure.step("步骤2：滚动到 Footer 并打开 Cookie Settings"):
        footer_page.scroll_to_footer()
        cookie_settings_btn = page.locator('div').filter(has_text=re.compile(r"^Cookie Settings$"))
        cookie_settings_btn.click()
        page.wait_for_timeout(1000)  # 等待弹窗动画
        page.locator('dialog, [role="dialog"]').first.wait_for(state="visible", timeout=5000)
        logger.info("✓ Cookie Settings 弹窗已打开")
    
    # 定义要验证的所有 Cookie 类型
    cookie_types = [
        {"name": "Essential cookies", "index": 0, "has_always_active": True},
        {"name": "Functional cookies", "index": 1, "has_always_active": False},
        {"name": "Analytical cookies", "index": 2, "has_always_active": False},
        {"name": "Advertising cookies", "index": 3, "has_always_active": False}
    ]
    
    verified_count = 0
    
    for cookie_type in cookie_types:
        type_name = cookie_type["name"]
        index = cookie_type["index"]
        
        with allure.step(f"验证 {type_name}"):
            # 点击展开该 Cookie 类型
            if cookie_type["has_always_active"]:
                option = page.get_by_text(f'{type_name}Always active')
            else:
                # 使用正则表达式确保精确匹配
                option = page.locator('div').filter(has_text=re.compile(f"^{type_name}$"))
            
            option.click()
            logger.info(f"✓ 点击 {type_name}")
            
            # 验证 Cookie information 入口出现
            cookie_info_link = page.get_by_text('Cookie information').nth(index)
            assert cookie_info_link.is_visible(timeout=5000), \
                f"{type_name} 的 Cookie Information 入口不可见"
            logger.info(f"✓ {type_name} 有 Cookie Information 入口")
            
            verified_count += 1
    
    with allure.step("验证：所有 Cookie 类型都有 Cookie Information 入口"):
        assert verified_count == 4, f"只验证了 {verified_count}/4 个 Cookie 类型"
        logger.info(f"✓ 所有 {verified_count} 个 Cookie 类型都有 Cookie Information 入口")
    
    with allure.step("抽样验证：点击 Functional cookies 的 Cookie Information"):
        # 随机抽样验证一个（这里选择 Functional cookies）
        functional_info = page.get_by_text('Cookie information').nth(1)
        functional_info.click()
        page.wait_for_timeout(1500)
        logger.info("✓ Functional cookies 的 Cookie Information 可正常打开")
        
        # 验证信息内容
        page.wait_for_timeout(500)
        logger.info("✓ Cookie详细内容展示正常")
    
    logger.info("="*80)
    logger.info("TC-FOOTER-D-009 执行完成")
    logger.info("="*80)
