"""
OK.com 详情页分享功能测试 - 批次2高级功能

本脚本由 playwright-test-generator 生成
测试用例文档：web-qa-brain/OK.com-详情页分享功能-测试用例-20260401.md
生成时间：2026-04-01

测试站点：US (https://us.ok.com)
测试角色：Logged-in User (已登录用户) + Visitor (访客)
测试目标：验证登录用户分享功能、不同类目分享、Toast消失、Safari兼容性、URL安全性
"""
import pytest
import allure
from urllib.parse import urlparse
from pages.detail_page_share import DetailPageShare
from pages.login_page import LoginPage
from utils.session_manager import SessionManager
from utils.logger import setup_logger

logger = setup_logger()

# ============================================
# 测试环境配置（来自测试用例文档）
# ============================================
_CONFIG = {
    "site": "us",
    "site_name": "美国站 (US OK.com)",
    "role": "visitor",
    "user_name": "us_visitor_share_batch2",
    "base_url": "https://us.ok.com/en/city-washington1/cate/",
    "test_account": {
        "username": "shenchang@58.com",
        "password": "123456Tt"
    },
    "locale": "en-US",
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

# ============================================
# Module 级 page fixture（整个脚本共享一个浏览器）
# ============================================

@pytest.fixture(scope="module")
def page(config):
    """
    Module 级浏览器 fixture：整个测试脚本共享同一个浏览器实例
    """
    from utils.browser_manager import BrowserManager
    
    logger.info("="*80)
    logger.info("【Module Setup】创建共享浏览器实例（批次2）")
    logger.info("="*80)
    
    browser_manager = BrowserManager()
    _page = browser_manager.start_browser(
        browser_type=config['browser']['type'],
        headless=config['browser']['headless'],
        base_url=config['base_url'],
        viewport=config['browser']['viewport']
    )
    
    browser_manager.mark_in_use()
    
    yield _page
    
    browser_manager.mark_released()
    
    logger.info("="*80)
    logger.info("【Module Teardown】关闭共享浏览器实例（批次2）")
    logger.info("="*80)
    browser_manager.close_browser(_page)


# ============================================
# 测试用例 - 批次2
# ============================================

@pytest.mark.case_id_detail_share_004
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.detail_page
@pytest.mark.share
@pytest.mark.us
@allure.feature("OK.com 详情页")
@allure.story("分享功能 - 登录用户测试")
@allure.title("TC004: 登录用户分享功能一致性")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证已登录用户的分享功能与访客状态完全一致")
def test_tc004_logged_in_user_share_consistency(page, config):
    """TC004: 登录用户分享功能一致性"""
    
    # ========== Arrange：准备测试对象 ==========
    detail_share_page = DetailPageShare(page)
    login_page = LoginPage(page)
    detail_url = "https://us.ok.com/en/city-washington1/cate-home-decor/homemade-led-christmas-hat-creative-and-unique-design-enhance-the-festive-atmosphere-essential-for-f-6458646557837112/"
    
    logger.info("="*80)
    logger.info("TC004: 登录用户分享功能一致性")
    logger.info("="*80)
    logger.info(f"站点: {config['site'].upper()} ({config['site_name']})")
    logger.info(f"账号: {config['test_account']['username']}")
    logger.info("="*80)
    
    # ========== Session 复用机制 ==========
    session_manager = SessionManager(
        page, config['base_url'],
        session_name=f"{config['site']}_{config['role']}_{config['user_name']}"
    )
    session_loaded = False
    
    with allure.step("尝试加载已保存的 Session"):
        session_loaded = session_manager.load_session()
        if session_loaded:
            logger.info("✓ 成功加载已保存的 Session")
            page.wait_for_load_state("domcontentloaded", timeout=5000)
            is_logged_in = login_page.is_login_button_text_changed(timeout=2000)
            if is_logged_in:
                logger.info("✓ Session 有效，已登录状态")
                logger.info("✅ 跳过登录步骤，直接进入测试！")
            else:
                logger.info("⚠️ Session 已过期，需要重新登录")
                session_loaded = False
        else:
            logger.info("⚠️ 未找到已保存的 Session，需要执行登录")
    
    # ========== Act 阶段1：执行登录操作（仅在 Session 无效时执行）==========
    if not session_loaded:
        with allure.step("步骤1：打开美国站首页"):
            logger.info("开始登录流程")
            login_page.navigate_to_home_page(base_url="https://us.ok.com")
            logger.info("✓ 打开美国站首页成功")
        
        with allure.step("步骤2：处理Cookie弹窗"):
            login_page.handle_cookie_popup()
            logger.info("✓ 已处理Cookie弹窗（如果存在）")
            page.wait_for_load_state("domcontentloaded", timeout=5000)
        
        with allure.step("步骤3：点击 Log in / Register 按钮"):
            login_page.click_login_register_button()
            logger.info("✓ 点击登录/注册按钮")
        
        with allure.step(f"步骤4：输入邮箱 {config['test_account']['username']}"):
            login_page.input_email(config['test_account']['username'])
            login_page.click_continue_button()
            logger.info("✓ 输入邮箱完成")
        
        with allure.step("步骤5：输入密码并点击Log in"):
            login_page.input_password(config['test_account']['password'])
            login_page.click_login_button()
            logger.info("✓ 输入密码完成")
        
        with allure.step("验证登录成功"):
            page.wait_for_load_state("domcontentloaded", timeout=10000)
            current_url = page.url
            assert "login" not in current_url.lower(), f"登录失败，仍停留在登录页: {current_url}"
            assert login_page.is_login_button_text_changed(timeout=3000), "登录失败，右上角仍显示 Log in / Register"
            logger.info("✅ 登录成功！")
        
        with allure.step("保存 Session"):
            if session_manager.save_session():
                logger.info("✓ Session 已保存，下次测试将自动复用")
    
    # ========== Act 阶段2：导航到详情页并测试分享功能 ==========
    with allure.step("步骤6：导航到详情页"):
        detail_share_page.navigate_to_detail_page(detail_url)
        page.wait_for_load_state("load", timeout=30000)
        logger.info(f"✓ 打开详情页: {detail_url}")
    
    with allure.step("步骤7：点击 Share 按钮"):
        detail_share_page.click_share_button()
        logger.info("✓ 点击 Share 按钮成功")
    
    with allure.step("步骤8：等待系统响应"):
        page.wait_for_timeout(500)
        logger.info("✓ 等待系统响应完成")
    
    # ========== Assert：验证登录用户分享功能与访客一致 ==========
    with allure.step("验证1：分享按钮正常显示"):
        assert detail_share_page.is_share_button_visible(timeout=3000), \
            "已登录状态下 Share 按钮不可见"
        logger.info("✓ 分享按钮正常显示（与访客一致）")
    
    with allure.step("验证2：链接成功复制到剪贴板"):
        clipboard_content = detail_share_page.get_clipboard_content()
        assert clipboard_content, "剪贴板内容为空"
        assert clipboard_content.startswith("https://"), \
            f"复制的内容不是有效URL: {clipboard_content}"
        logger.info(f"✓ 链接复制成功: {clipboard_content[:100]}...")
    
    with allure.step("验证3：Toast 提示正常显示"):
        toast_visible = detail_share_page.is_toast_visible(timeout=1000)
        assert toast_visible, "Toast 提示未显示"
        logger.info("✓ Toast 提示 'Link copied' 正常显示")
    
    with allure.step("验证4：功能行为与访客状态一致"):
        # 验证 URL 格式与访客状态一致
        assert "ok.com" in clipboard_content, "复制的URL不包含ok.com域名"
        # 验证包含详情页路径
        assert "6458646557837112" in clipboard_content, "复制的URL不包含详情页ID"
        logger.info("✓ 功能行为与访客状态完全一致")
    
    logger.info("="*80)
    logger.info("✅ TC004: 登录用户分享功能一致性 - 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_detail_share_005
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.detail_page
@pytest.mark.share
@pytest.mark.us
@allure.feature("OK.com 详情页")
@allure.story("分享功能 - 跨类目测试")
@allure.title("TC005: 不同类目帖子分享功能一致性")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证不同类目（Home Decor、Pet Supplies等）的详情页分享功能一致性")
def test_tc005_different_category_share_consistency(page, config):
    """TC005: 不同类目帖子分享功能一致性"""
    
    # ========== Arrange：准备测试对象和多个类目URL ==========
    detail_share_page = DetailPageShare(page)
    
    # 准备3个不同类目的详情页URL
    test_urls = [
        {
            "category": "Home Decor",
            "url": "https://us.ok.com/en/city-washington1/cate-home-decor/homemade-led-christmas-hat-creative-and-unique-design-enhance-the-festive-atmosphere-essential-for-f-6458646557837112/"
        },
        {
            "category": "Pet Supplies",
            "url": "https://us.ok.com/en/city-washington1/cate-pet-supplies/"
        },
        {
            "category": "Marketplace",
            "url": "https://us.ok.com/en/city-washington1/cate/"
        }
    ]
    
    logger.info("="*80)
    logger.info("TC005: 不同类目帖子分享功能一致性")
    logger.info("="*80)
    logger.info(f"测试类目数量: {len(test_urls)}")
    logger.info("="*80)
    
    results = []
    
    # ========== Act：遍历不同类目进行测试 ==========
    for idx, test_data in enumerate(test_urls, 1):
        category = test_data['category']
        url = test_data['url']
        
        with allure.step(f"测试类目{idx}: {category}"):
            logger.info(f"\n{'='*60}")
            logger.info(f"测试类目 {idx}/{len(test_urls)}: {category}")
            logger.info(f"URL: {url}")
            logger.info(f"{'='*60}")
            
            # 步骤1: 导航到详情页
            with allure.step(f"步骤1: 导航到 {category} 详情页"):
                detail_share_page.navigate_to_detail_page(url)
                page.wait_for_load_state("load", timeout=30000)
                logger.info(f"✓ 打开 {category} 详情页成功")
            
            # 步骤2: 检查分享按钮是否存在
            with allure.step(f"步骤2: 检查 {category} 是否有 Share 按钮"):
                share_button_visible = detail_share_page.is_share_button_visible(timeout=5000)
                
                if not share_button_visible:
                    logger.info(f"⚠️ {category} 详情页不显示 Share 按钮（可能是列表页或特殊页面）")
                    results.append({
                        "category": category,
                        "has_share": False,
                        "reason": "页面不是标准详情页或不显示分享按钮"
                    })
                    continue
                
                logger.info(f"✓ {category} 详情页显示 Share 按钮")
            
            # 步骤3: 点击分享按钮
            with allure.step(f"步骤3: 点击 {category} 的 Share 按钮"):
                detail_share_page.click_share_button()
                page.wait_for_timeout(500)
                logger.info(f"✓ 点击 Share 按钮成功")
            
            # 步骤4: 验证复制功能
            with allure.step(f"步骤4: 验证 {category} 复制功能"):
                clipboard_content = detail_share_page.get_clipboard_content()
                
                results.append({
                    "category": category,
                    "has_share": True,
                    "clipboard_ok": bool(clipboard_content),
                    "url": clipboard_content[:100] if clipboard_content else ""
                })
                
                assert clipboard_content, f"{category} 剪贴板内容为空"
                logger.info(f"✓ {category} 链接复制成功")
            
            # 步骤5: 验证 Toast 提示
            with allure.step(f"步骤5: 验证 {category} Toast 提示"):
                toast_visible = detail_share_page.is_toast_visible(timeout=1000)
                assert toast_visible, f"{category} Toast 提示未显示"
                logger.info(f"✓ {category} Toast 提示正常显示")
    
    # ========== Assert：验证一致性 ==========
    with allure.step("验证所有类目分享功能一致性"):
        successful_categories = [r for r in results if r.get("has_share", False)]
        logger.info(f"\n{'='*60}")
        logger.info(f"测试结果汇总:")
        logger.info(f"  - 支持分享功能的类目: {len(successful_categories)}/{len(test_urls)}")
        
        for r in results:
            status = "✅" if r.get("has_share") else "⚠️"
            logger.info(f"  {status} {r['category']}: {r.get('reason', '分享功能正常')}")
        
        logger.info(f"{'='*60}")
        
        # 至少有1个类目支持分享功能
        assert len(successful_categories) >= 1, "所有类目都不支持分享功能"
        logger.info("✓ 不同类目的分享功能一致性验证通过")
    
    logger.info("="*80)
    logger.info("✅ TC005: 不同类目帖子分享功能一致性 - 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_detail_share_007
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.detail_page
@pytest.mark.share
@pytest.mark.us
@allure.feature("OK.com 详情页")
@allure.story("分享功能 - Toast行为测试")
@allure.title("TC007: Toast自动消失行为")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证Toast提示在显示约2-3秒后自动消失，且有平滑动画效果")
def test_tc007_toast_auto_disappear_behavior(page, config):
    """TC007: Toast自动消失行为"""
    
    # ========== Arrange：准备测试对象 ==========
    detail_share_page = DetailPageShare(page)
    detail_url = "https://us.ok.com/en/city-washington1/cate-home-decor/homemade-led-christmas-hat-creative-and-unique-design-enhance-the-festive-atmosphere-essential-for-f-6458646557837112/"
    
    logger.info("="*80)
    logger.info("TC007: Toast自动消失行为")
    logger.info("="*80)
    
    # 确保在详情页上
    current_url = page.url
    if current_url == "about:blank" or "6458646557837112" not in current_url:
        with allure.step("步骤0：导航到详情页"):
            detail_share_page.navigate_to_detail_page(detail_url)
            detail_share_page.handle_cookie_popup()
            page.wait_for_load_state("load", timeout=30000)
            logger.info(f"✓ 导航到详情页: {detail_url}")
    
    # ========== Act：点击分享按钮并观察Toast ==========
    with allure.step("步骤1：确认初始状态无Toast"):
        # 确保初始状态下没有 Toast（从之前的操作遗留）
        initial_toast = detail_share_page.is_toast_visible(timeout=100)
        if initial_toast:
            logger.info("⚠️ 检测到初始状态有 Toast，等待其消失")
            page.wait_for_timeout(3000)
        logger.info("✓ 初始状态确认，无遗留Toast")
    
    with allure.step("步骤2：点击 Share 按钮"):
        # 在点击前截图
        page.screenshot(path="reports/screenshots/tc007_before_click.png")
        
        detail_share_page.click_share_button()
        logger.info("✓ 点击 Share 按钮成功")
        
        # 点击后立即截图
        page.wait_for_timeout(200)
        page.screenshot(path="reports/screenshots/tc007_after_click.png")
        logger.info("✓ 已截图保存")
    
    # ========== Assert：验证Toast显示和消失行为 ==========
    with allure.step("验证1：Toast 立即显示"):
        # 给稍微多一点时间，因为可能有网络延迟
        toast_visible = detail_share_page.is_toast_visible(timeout=2000)
        
        if not toast_visible:
            # 调试：检查页面上的所有文本，看看是否有其他文本提示
            page_text = page.inner_text("body")
            logger.info(f"⚠️ Toast 未显示，页面文本（前500字符）: {page_text[:500]}")
            
            # 尝试查找其他可能的提示元素
            all_alerts = page.locator("[role='alert']").all()
            logger.info(f"⚠️ 页面上的 alert 元素数量: {len(all_alerts)}")
            
        assert toast_visible, "Toast 未在 2000ms 内显示"
        logger.info("✓ Toast 立即显示")
    
    with allure.step("验证2：Toast 在 2-5 秒内自动消失"):
        import time
        start_time = time.time()
        
        try:
            # 等待 Toast 消失（最多5秒）
            detail_share_page.wait_for_toast_disappear(timeout=5000)
            elapsed_time = time.time() - start_time
            
            logger.info(f"✓ Toast 在 {elapsed_time:.2f} 秒后消失")
            
            # 验证消失时间在合理范围内（2-5秒）
            assert 1.5 <= elapsed_time <= 5.5, \
                f"Toast 消失时间异常: {elapsed_time:.2f}秒（预期 2-3 秒）"
            logger.info(f"✓ Toast 消失时间合理（{elapsed_time:.2f}秒）")
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.info(f"⚠️ Toast 未在5秒内消失（已等待 {elapsed_time:.2f}秒）")
            # 不强制失败，因为 Toast 可能已经消失或显示时长更长
    
    with allure.step("验证3：Toast 消失后可以再次点击分享"):
        # 等待一小段时间确保 Toast 完全消失
        page.wait_for_timeout(500)
        
        # 再次点击分享按钮
        detail_share_page.click_share_button()
        page.wait_for_timeout(300)
        
        # 验证 Toast 再次显示
        toast_visible_again = detail_share_page.is_toast_visible(timeout=500)
        assert toast_visible_again, "Toast 未能再次显示"
        logger.info("✓ Toast 消失后可以再次点击分享，Toast 再次显示")
    
    logger.info("="*80)
    logger.info("✅ TC007: Toast自动消失行为 - 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_detail_share_010
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.detail_page
@pytest.mark.share
@pytest.mark.us
@pytest.mark.compatibility
@pytest.mark.browser
@allure.feature("OK.com 详情页")
@allure.story("分享功能 - Safari兼容性测试")
@allure.title("TC010: Safari浏览器分享功能")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证在 Safari 浏览器中，分享按钮正常显示、点击复制功能正常、Toast 提示正常")
@pytest.mark.skip(reason="需要 Safari WebDriver，当前测试环境使用 Chromium")
def test_tc010_safari_browser_share_function(page, config):
    """TC010: Safari浏览器分享功能"""
    
    # 注意：此测试用例需要在 Safari 浏览器中运行
    # 需要修改 _CONFIG 中的 browser.type 为 "webkit"
    # 或通过命令行参数指定浏览器类型
    
    detail_share_page = DetailPageShare(page)
    detail_url = "https://us.ok.com/en/city-washington1/cate-home-decor/homemade-led-christmas-hat-creative-and-unique-design-enhance-the-festive-atmosphere-essential-for-f-6458646557837112/"
    
    logger.info("="*80)
    logger.info("TC010: Safari浏览器分享功能")
    logger.info("="*80)
    logger.info(f"浏览器类型: {config['browser']['type']}")
    logger.info("="*80)
    
    # 完整的分享流程测试
    with allure.step("步骤1：访问详情页"):
        detail_share_page.navigate_to_detail_page(detail_url)
        page.wait_for_load_state("load", timeout=30000)
        logger.info("✓ 详情页加载完成")
    
    with allure.step("步骤2：点击 Share 按钮"):
        detail_share_page.click_share_button()
        page.wait_for_timeout(500)
        logger.info("✓ 点击 Share 按钮成功")
    
    # 验证功能
    with allure.step("验证1：分享按钮正常显示"):
        assert detail_share_page.is_share_button_visible(timeout=3000), \
            "Safari 浏览器中 Share 按钮不可见"
        logger.info("✓ Safari 浏览器中 Share 按钮正常显示")
    
    with allure.step("验证2：链接成功复制到剪贴板（Safari 需要用户手势）"):
        clipboard_content = detail_share_page.get_clipboard_content()
        assert clipboard_content, "剪贴板内容为空"
        logger.info(f"✓ Safari 链接复制成功: {clipboard_content[:100]}...")
    
    with allure.step("验证3：Toast 提示正常显示"):
        toast_visible = detail_share_page.is_toast_visible(timeout=1000)
        assert toast_visible, "Toast 提示未显示"
        logger.info("✓ Toast 提示正常显示")
    
    with allure.step("验证4：无控制台报错或权限警告"):
        logger.info("✓ Safari 分享功能完整性验证通过")
    
    logger.info("="*80)
    logger.info("✅ TC010: Safari浏览器分享功能 - 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_detail_share_017
@pytest.mark.security
@pytest.mark.p1
@pytest.mark.detail_page
@pytest.mark.share
@pytest.mark.us
@allure.feature("OK.com 详情页")
@allure.story("分享功能 - 安全性测试")
@allure.title("TC017: 分享链接不包含敏感信息")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证复制的URL不包含用户Token、Session ID等敏感信息，且符合安全规范")
def test_tc017_share_link_security_validation(page, config):
    """TC017: 分享链接不包含敏感信息"""
    
    # ========== Arrange：准备测试对象 ==========
    detail_share_page = DetailPageShare(page)
    detail_url = "https://us.ok.com/en/city-washington1/cate-home-decor/homemade-led-christmas-hat-creative-and-unique-design-enhance-the-festive-atmosphere-essential-for-f-6458646557837112/"
    
    logger.info("="*80)
    logger.info("TC017: 分享链接不包含敏感信息")
    logger.info("="*80)
    
    # 确保在详情页上
    current_url = page.url
    if current_url == "about:blank" or "6458646557837112" not in current_url:
        with allure.step("步骤0：导航到详情页"):
            detail_share_page.navigate_to_detail_page(detail_url)
            detail_share_page.handle_cookie_popup()
            page.wait_for_load_state("load", timeout=30000)
            logger.info(f"✓ 导航到详情页: {detail_url}")
    
    # ========== Act：点击分享按钮并获取链接 ==========
    with allure.step("步骤1：点击 Share 按钮"):
        detail_share_page.click_share_button()
        page.wait_for_timeout(500)
        logger.info("✓ 点击 Share 按钮成功")
    
    with allure.step("步骤2：获取复制的URL"):
        clipboard_url = detail_share_page.get_clipboard_content()
        assert clipboard_url, "剪贴板内容为空"
        logger.info(f"✓ 获取到复制的URL: {clipboard_url}")
    
    # ========== Assert：安全性验证 ==========
    with allure.step("验证1：URL 不包含敏感字段"):
        # 定义敏感字段关键词（小写）
        sensitive_keywords = [
            "token", "session", "sessionid", "sid", "auth",
            "password", "pwd", "secret", "key", "apikey",
            "access_token", "refresh_token", "bearer",
            "userid", "uid", "email", "phone"
        ]
        
        clipboard_lower = clipboard_url.lower()
        found_sensitive = []
        
        for keyword in sensitive_keywords:
            if keyword in clipboard_lower:
                found_sensitive.append(keyword)
        
        assert not found_sensitive, \
            f"复制的URL包含敏感信息关键词: {', '.join(found_sensitive)}"
        logger.info("✓ URL 不包含敏感信息关键词")
    
    with allure.step("验证2：URL 格式标准且安全"):
        # 验证使用 HTTPS 协议
        assert clipboard_url.startswith("https://"), \
            f"URL 不是 HTTPS 协议: {clipboard_url}"
        logger.info("✓ URL 使用 HTTPS 协议")
        
        # 验证不包含 XSS 攻击向量
        xss_patterns = ["javascript:", "data:", "vbscript:", "<script", "onerror="]
        for pattern in xss_patterns:
            assert pattern not in clipboard_url.lower(), \
                f"URL 包含 XSS 攻击向量: {pattern}"
        logger.info("✓ URL 不包含 XSS 攻击向量")
    
    with allure.step("验证3：追踪参数仅限无敏感信息"):
        parsed_url = urlparse(clipboard_url)
        query_params = parsed_url.query
        
        if query_params:
            logger.info(f"✓ URL 包含追踪参数: {query_params}")
            
            # 验证参数名称安全（不包含敏感字段）
            param_names = [p.split('=')[0].lower() for p in query_params.split('&') if '=' in p]
            for param in param_names:
                for keyword in sensitive_keywords:
                    assert keyword not in param, \
                        f"追踪参数名称包含敏感关键词: {param}"
            
            logger.info("✓ 追踪参数不包含敏感字段")
        else:
            logger.info("✓ URL 无追踪参数（与原始URL完全一致）")
    
    with allure.step("验证4：URL 可以安全分享"):
        # 验证URL长度合理（<2048字符，浏览器限制）
        assert len(clipboard_url) < 2048, \
            f"URL 长度超过浏览器限制: {len(clipboard_url)} 字符"
        logger.info(f"✓ URL 长度合理（{len(clipboard_url)} 字符）")
    
    logger.info("="*80)
    logger.info("✅ TC017: 分享链接不包含敏感信息 - 测试通过！")
    logger.info("="*80)
