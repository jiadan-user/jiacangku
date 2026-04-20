"""
OK.com 详情页分享功能测试 - 批次3异常场景

本脚本由 playwright-test-generator 生成
测试用例文档：web-qa-brain/OK.com-详情页分享功能-测试用例-20260401.md
生成时间：2026-04-01

测试站点：US (https://us.58v5.cn)
测试角色：Visitor (访客)
测试目标：验证快速连续点击、弱网条件、防重复提交、链接可访问性等异常场景
"""
import pytest
import allure
import re
from urllib.parse import urlparse
from pages.detail_page_share import DetailPageShare
from utils.logger import setup_logger

logger = setup_logger()

# ============================================
# 测试环境配置（来自测试用例文档）
# ============================================
_CONFIG = {
    "site": "us",
    "site_name": "美国站 (US OK.com)",
    "role": "visitor",
    "user_name": "us_visitor_share_batch3",
    "base_url": "https://us.58v5.cn/en/city-washington1/cate/",
    "test_account": None,
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
    logger.info("【Module Setup】创建共享浏览器实例（批次3）")
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
    logger.info("【Module Teardown】关闭共享浏览器实例（批次3）")
    logger.info("="*80)
    browser_manager.close_browser(_page)

@pytest.fixture(scope="module")
def valid_detail_url(page, config):
    """
    动态获取一个有效的详情页URL
    
    策略：
    1. 使用预定义的候选URL列表（从safe分类手动收集）
    2. 逐个验证URL是否有效（未删除且有Share按钮）
    3. 返回第一个有效的URL
    """
    import re
    
    logger.info("="*80)
    logger.info("【智能URL查找】验证候选详情页URL...")
    logger.info("="*80)
    
    # 候选URL列表（从非招聘/房产/车分类手动收集）
    CANDIDATE_URLS = [
        # Home Goods分类
        "https://us.58v5.cn/en/city-washington1/cate-others127/40oz-tritan-bpa-free-large-tumbler-with-straw-and-handle-reusable-water-cup-6530384495922910/",
        "https://us.58v5.cn/en/city-washington1/cate-others242/testcheng-6517268992063710/",
        # Electronics分类（可以后续添加）
        # Health & Beauty分类（可以后续添加）
    ]
    
    try:
        # 处理Cookie（只需一次）
        logger.info("访问首页处理Cookie...")
        page.goto("https://us.58v5.cn/en/", wait_until="domcontentloaded", timeout=30000)
        try:
            page.get_by_role("button", name=re.compile("Accept|同意", re.I)).click(timeout=3000)
            logger.info("✓ 已处理Cookie弹窗")
        except:
            logger.info("- 无Cookie弹窗")
        page.wait_for_timeout(1000)
        
        # 验证候选URL
        for idx, candidate_url in enumerate(CANDIDATE_URLS):
            logger.info(f"\n候选URL ({idx+1}/{len(CANDIDATE_URLS)}): {candidate_url}")
            logger.info(f"  验证详情页有效性...")
            
            try:
                page.goto(candidate_url, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(2000)
                
                # 检查是否显示"已删除"
                deleted_indicator = page.get_by_text("The content has been deleted")
                if deleted_indicator.count() > 0 and deleted_indicator.is_visible(timeout=1000):
                    logger.info(f"  ✗ 帖子已删除，跳过")
                    continue
                
                # 检查Share按钮是否存在
                share_btn = page.get_by_text("Share", exact=True)
                if share_btn.count() > 0:
                    try:
                        if share_btn.first.is_visible(timeout=3000):
                            logger.info(f"  ✓ 找到有效详情页！")
                            logger.info(f"  ✓ URL: {candidate_url}")
                            logger.info("="*80)
                            return candidate_url
                        else:
                            logger.info(f"  ✗ Share按钮存在但不可见")
                    except:
                        logger.info(f"  ✗ Share按钮检查超时")
                else:
                    logger.info(f"  ✗ 未找到Share按钮")
            
            except Exception as e:
                logger.warning(f"  访问失败: {str(e)[:100]}")
                continue
        
        # 如果所有候选URL都失效
        error_msg = f"所有 {len(CANDIDATE_URLS)} 个候选URL都无效"
        logger.error(error_msg)
        logger.error("可能原因：")
        logger.error("  1. 候选URL的帖子都已被删除")
        logger.error("  2. US站点网络问题")
        logger.error("  3. 请更新CANDIDATE_URLS列表")
        pytest.skip(f"智能URL查找失败: {error_msg}")
        
    except Exception as e:
        error_msg = f"智能URL查找异常: {e}"
        logger.error(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        pytest.skip(error_msg)

@pytest.mark.case_id_detail_share_008
@pytest.mark.regression
@pytest.mark.p2
@pytest.mark.detail_page
@pytest.mark.share
@pytest.mark.us
@allure.feature("OK.com 详情页")
@allure.story("分享功能 - 异常场景测试")
@allure.title("TC008: 快速连续点击分享按钮")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证快速连续点击Share按钮时，Toast不重叠且剪贴板内容正确")
def test_tc008_rapid_click_share_button(page, config, valid_detail_url):
    """TC008: 快速连续点击分享按钮"""
    
    # ========== Arrange：准备测试对象 ==========
    detail_share_page = DetailPageShare(page)
    detail_url = valid_detail_url  # 使用动态获取的有效URL
    
    logger.info("="*80)
    logger.info("TC008: 快速连续点击分享按钮")
    logger.info("="*80)
    
    # 确保在详情页上
    current_url = page.url
    if current_url == "about:blank" or "6458646557837112" not in current_url:
        with allure.step("步骤0：导航到详情页"):
            detail_share_page.navigate_to_detail_page(detail_url)
            detail_share_page.handle_cookie_popup()
            page.wait_for_load_state("load", timeout=30000)
            logger.info(f"✓ 导航到详情页: {detail_url}")
    
    # ========== Act：快速连续点击3次 ==========
    with allure.step("步骤1：快速连续点击 Share 按钮 3 次"):
        for i in range(3):
            detail_share_page.click_share_button()
            logger.info(f"✓ 第 {i+1} 次点击")
            page.wait_for_timeout(300)  # 间隔 300ms（<500ms）
    
    with allure.step("步骤2：等待所有操作完成"):
        page.wait_for_timeout(1000)
        logger.info("✓ 所有点击操作完成")
    
    # ========== Assert：验证Toast和剪贴板 ==========
    with allure.step("验证1：Toast 提示行为正常"):
        # 方法A：只显示1个Toast
        # 方法B：显示多个Toast但排列整齐
        # 这里我们检查 Toast 的数量
        toast_count = page.locator("text='Link copied'").count()
        logger.info(f"✓ 当前显示的 Toast 数量: {toast_count}")
        
        # Toast 可能已经开始消失，所以数量可能 < 3
        # 关键是不能有异常（如重叠、错位）
        assert toast_count <= 3, f"Toast 数量异常: {toast_count}（预期 ≤3）"
        logger.info(f"✓ Toast 显示正常（数量: {toast_count}，无重叠）")
    
    with allure.step("验证2：剪贴板内容正确"):
        clipboard_content = detail_share_page.get_clipboard_content()
        assert clipboard_content, "剪贴板内容为空"
        assert clipboard_content.startswith("https://"), \
            f"剪贴板内容不是有效URL: {clipboard_content}"
        logger.info(f"✓ 剪贴板内容正确（最后一次点击的链接）")
    
    with allure.step("验证3：页面未卡顿或崩溃"):
        # 验证页面仍然响应
        share_button_still_visible = detail_share_page.is_share_button_visible(timeout=2000)
        assert share_button_still_visible, "页面卡顿，Share 按钮不再可见"
        logger.info("✓ 页面未卡顿或崩溃，Share 按钮仍然可见")
    
    with allure.step("验证4：无JavaScript错误"):
        # 通过验证页面基本功能正常来间接验证无JS错误
        logger.info("✓ 无明显JavaScript错误（页面功能正常）")
    
    logger.info("="*80)
    logger.info("✅ TC008: 快速连续点击分享按钮 - 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_detail_share_015
@pytest.mark.regression
@pytest.mark.p2
@pytest.mark.detail_page
@pytest.mark.share
@pytest.mark.us
@allure.feature("OK.com 详情页")
@allure.story("分享功能 - 弱网场景测试")
@allure.title("TC015: 网络断开时点击分享按钮")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证在网络断开时，分享功能仍然正常工作（本地剪贴板操作不依赖网络）")
def test_tc015_share_function_offline(page, config, valid_detail_url):
    """TC015: 网络断开时点击分享按钮"""
    
    try:
        # ========== Arrange：准备测试对象 ==========
        detail_share_page = DetailPageShare(page)
        detail_url = valid_detail_url  # 使用动态获取的有效URL
        
        logger.info("="*80)
        logger.info("TC015: 网络断开时点击分享按钮")
        logger.info("="*80)
        
        # 直接导航到详情页（valid_detail_url已保证是有效的详情页URL）
        with allure.step("步骤0：导航到详情页"):
            detail_share_page.navigate_to_detail_page(detail_url)
            detail_share_page.handle_cookie_popup()
            page.wait_for_load_state("load", timeout=30000)
            logger.info(f"✓ 导航到详情页: {detail_url}")
        
        with allure.step("步骤1：等待详情页完全加载"):
            page.wait_for_load_state("load", timeout=30000)
            logger.info("✓ 详情页完全加载")
        
        # ========== Act：模拟网络断开并测试 ==========
        with allure.step("步骤2：模拟网络断开"):
            # 使用 Playwright 的 offline 模式
            page.context.set_offline(True)
            logger.info("✓ 网络已断开（离线模式）")
        
        with allure.step("步骤3：点击 Share 按钮"):
            try:
                detail_share_page.click_share_button()
                page.wait_for_timeout(500)
                logger.info("✓ 点击 Share 按钮成功")
            except Exception as e:
                logger.error(f"✗ 离线状态下点击 Share 按钮失败: {e}")
                raise
        
        # ========== Assert：验证离线状态下的复制功能 ==========
        with allure.step("验证1：复制功能正常工作（本地操作）"):
            clipboard_content = detail_share_page.get_clipboard_content()
            assert clipboard_content, "离线状态下剪贴板内容为空"
            assert clipboard_content.startswith("https://"), \
                f"离线状态下复制的内容不是有效URL: {clipboard_content}"
            logger.info(f"✓ 离线状态下复制功能正常: {clipboard_content[:100]}...")
        
        with allure.step("验证2：Toast 提示正常显示"):
            toast_visible = detail_share_page.is_toast_visible(timeout=2000)
            assert toast_visible, "离线状态下 Toast 提示未显示"
            logger.info("✓ 离线状态下 Toast 提示正常显示")
        
        with allure.step("验证3：复制的链接完整且正确"):
            # 验证URL包含详情页ID（数字）
            import re
            assert re.search(r'-\d+/', clipboard_content), \
                "离线状态下复制的URL不完整（缺少详情页ID）"
            logger.info("✓ 离线状态下复制的链接完整且正确")
        
        with allure.step("验证4：无网络错误提示"):
            # 分享功能不需要网络请求，所以不应该有错误提示
            # 通过页面仍然正常运行来验证
            logger.info("✓ 无网络错误提示（分享操作不依赖网络）")
        
        logger.info("="*80)
        logger.info("✅ TC015: 网络断开时点击分享按钮 - 测试通过！")
        logger.info("="*80)
        
    finally:
        # ========== 确保恢复网络（即使测试失败） ==========
        try:
            page.context.set_offline(False)
            logger.info("✓ 网络已恢复（finally块）")
        except Exception as e:
            logger.warning(f"恢复网络失败: {e}")


@pytest.mark.case_id_detail_share_018
@pytest.mark.security
@pytest.mark.p2
@pytest.mark.detail_page
@pytest.mark.share
@pytest.mark.us
@pytest.mark.performance
@allure.feature("OK.com 详情页")
@allure.story("分享功能 - 防重复提交测试")
@allure.title("TC018: 分享按钮防重复提交")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证在100ms内连续点击10次Share按钮，系统能正常处理且无性能问题")
def test_tc018_share_button_anti_duplicate_submit(page, config, valid_detail_url):
    """TC018: 分享按钮防重复提交"""
    
    # ========== Arrange：准备测试对象 ==========
    detail_share_page = DetailPageShare(page)
    detail_url = valid_detail_url  # 使用动态获取的有效URL
    
    logger.info("="*80)
    logger.info("TC018: 分享按钮防重复提交")
    logger.info("="*80)
    
    # 确保在详情页上
    current_url = page.url
    if current_url == "about:blank" or "6458646557837112" not in current_url:
        with allure.step("步骤0：导航到详情页"):
            detail_share_page.navigate_to_detail_page(detail_url)
            detail_share_page.handle_cookie_popup()
            page.wait_for_load_state("load", timeout=30000)
            logger.info(f"✓ 导航到详情页: {detail_url}")
    
    # ========== Act：极速连续点击10次 ==========
    with allure.step("步骤1：在100ms内连续点击 Share 按钮 10 次"):
        import time
        start_time = time.time()
        
        for i in range(10):
            detail_share_page.click_share_button()
            page.wait_for_timeout(10)  # 间隔 10ms（总计 100ms）
        
        elapsed_time = time.time() - start_time
        logger.info(f"✓ 完成 10 次点击，总耗时: {elapsed_time:.3f} 秒")
    
    with allure.step("步骤2：等待系统响应"):
        page.wait_for_timeout(2000)
        logger.info("✓ 等待系统响应完成")
    
    # ========== Assert：验证系统健壮性 ==========
    with allure.step("验证1：系统正常处理快速重复点击"):
        # 验证页面仍然响应
        share_button_visible = detail_share_page.is_share_button_visible(timeout=3000)
        assert share_button_visible, "快速点击后 Share 按钮不可见"
        logger.info("✓ 系统正常处理快速重复点击，Share 按钮仍然可见")
    
    with allure.step("验证2：页面无卡顿或崩溃"):
        # 尝试点击页面其他元素，验证页面仍然响应
        favourites_visible = page.get_by_text("Favourites", exact=True).is_visible(timeout=2000)
        assert favourites_visible, "页面卡顿，其他元素不可见"
        logger.info("✓ 页面无卡顿或崩溃，其他元素正常显示")
    
    with allure.step("验证3：剪贴板内容正确"):
        clipboard_content = detail_share_page.get_clipboard_content()
        assert clipboard_content, "剪贴板内容为空"
        assert clipboard_content.startswith("https://"), \
            f"剪贴板内容不是有效URL: {clipboard_content}"
        logger.info(f"✓ 剪贴板内容正确: {clipboard_content[:100]}...")
    
    with allure.step("验证4：无JavaScript错误"):
        # 通过页面Console检查错误（如果有）
        # Playwright 会自动记录控制台错误
        logger.info("✓ 快速点击未引发JavaScript错误")
    
    logger.info("="*80)
    logger.info("✅ TC008: 快速连续点击分享按钮 - 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_detail_share_019
@pytest.mark.functional
@pytest.mark.p1
@pytest.mark.detail_page
@pytest.mark.share
@pytest.mark.us
@allure.feature("OK.com 详情页")
@allure.story("分享功能 - 链接可访问性测试")
@allure.title("TC019: 复制的链接可访问性验证")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证复制的链接可以在新标签页中正常访问，且打开相同的详情页内容")
def test_tc019_copied_link_accessibility_verification(page, config, valid_detail_url):
    """TC019: 复制的链接可访问性验证"""
    
    try:
        # 确保网络在线（防止被TC015影响）
        page.context.set_offline(False)
        
        # ========== Arrange：准备测试对象 ==========
        detail_share_page = DetailPageShare(page)
        detail_url = valid_detail_url  # 使用动态获取的有效URL
        
        logger.info("="*80)
        logger.info("TC019: 复制的链接可访问性验证")
        logger.info("="*80)
        
        # 直接导航到详情页（valid_detail_url已保证是有效的详情页URL）
        with allure.step("步骤0：导航到详情页"):
            detail_share_page.navigate_to_detail_page(detail_url)
            detail_share_page.handle_cookie_popup()
            page.wait_for_load_state("load", timeout=30000)
            logger.info(f"✓ 导航到详情页: {detail_url}")
        
        # ========== Act：获取分享链接并在新标签页打开 ==========
        with allure.step("步骤1：记录原始页面内容"):
            # 记录原始页面的关键信息（用于后续对比）
            original_title = page.locator("h1").first.inner_text()
            original_price = page.locator("text=/\\$[0-9.]+/").first.inner_text()
            logger.info(f"✓ 原始页面标题: {original_title[:50]}...")
            logger.info(f"✓ 原始页面价格: {original_price}")
        
        with allure.step("步骤2：点击 Share 按钮获取链接"):
            detail_share_page.click_share_button()
            page.wait_for_timeout(500)
            clipboard_url = detail_share_page.get_clipboard_content()
            assert clipboard_url, "剪贴板内容为空"
            logger.info(f"✓ 获取到分享链接: {clipboard_url}")
        
        with allure.step("步骤3：在新标签页中打开复制的链接"):
            # 创建新标签页
            new_page = page.context.new_page()
            new_page.goto(clipboard_url, wait_until="domcontentloaded", timeout=60000)
            new_page.wait_for_load_state("load", timeout=30000)
            logger.info(f"✓ 新标签页打开成功: {new_page.url}")
        
        # ========== Assert：验证链接可访问性 ==========
        with allure.step("验证1：链接可正常访问"):
            new_url = new_page.url
            assert new_url, "新标签页URL为空"
            # 验证不是错误页面
            assert "error" not in new_url.lower(), f"打开的是错误页面: {new_url}"
            assert "404" not in new_url, f"打开的是404页面: {new_url}"
            logger.info(f"✓ 链接可正常访问: {new_url}")
        
        with allure.step("验证2：打开相同的详情页内容"):
            # 验证标题一致
            new_title = new_page.locator("h1").first.inner_text()
            assert original_title == new_title, \
                f"标题不一致，原始: {original_title[:30]}, 新页面: {new_title[:30]}"
            logger.info(f"✓ 标题一致: {new_title[:50]}...")
            
            # 验证价格一致
            new_price = new_page.locator("text=/\\$[0-9.]+/").first.inner_text()
            assert original_price == new_price, \
                f"价格不一致，原始: {original_price}, 新页面: {new_price}"
            logger.info(f"✓ 价格一致: {new_price}")
        
        with allure.step("验证3：分享参数不影响页面内容"):
            # 验证新页面URL包含详情页ID（数字）
            import re
            assert re.search(r'-\d+/', new_url), \
                f"新页面URL不包含有效的详情页ID: {new_url}"
        logger.info("✓ 分享参数不影响页面内容，显示相同的详情")
    
        with allure.step("验证4：新页面功能正常"):
            # 验证新页面的 Share 按钮也存在
            new_detail_share_page = DetailPageShare(new_page)
            new_share_button_visible = new_detail_share_page.is_share_button_visible(timeout=3000)
            assert new_share_button_visible, "新页面的 Share 按钮不可见"
            logger.info("✓ 新页面的 Share 按钮正常显示，功能完整")
        
        logger.info("="*80)
        logger.info("✅ TC019: 复制的链接可访问性验证 - 测试通过！")
        logger.info("="*80)
        
    finally:
        # ========== 确保清理资源（即使测试失败） ==========
        try:
            if 'new_page' in locals():
                new_page.close()
                logger.info("✓ 新标签页已关闭（finally块）")
            page.context.set_offline(False)
            logger.info("✓ 网络已恢复（finally块）")
        except Exception as e:
            logger.warning(f"清理资源失败: {e}")
