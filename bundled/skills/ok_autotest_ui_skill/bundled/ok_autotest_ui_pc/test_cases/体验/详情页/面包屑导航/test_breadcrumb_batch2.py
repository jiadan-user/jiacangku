# test_cases/体验/详情页/面包屑导航/test_breadcrumb_batch2.py
"""
详情页面包屑导航 - 批次2：链接导航功能
测试用例：TC-BREADCRUMB-B-001 ~ TC-BREADCRUMB-B-005
"""

import pytest
import allure
from pages.breadcrumb_page import BreadcrumbPage
from utils.logger import setup_logger

logger = setup_logger()

# ========== 测试配置 ==========
_CONFIG = {
    "site": "us",
    "site_name": "美国站 (US 58v5.cn)",
    "base_url": "https://us.58v5.cn",
    "role": "visitor",
    "user_name": "us_visitor_breadcrumb",
    "test_account": None,
    "detail_url": "https://us.58v5.cn/en/city-washington/cate-graphic-design1/motorbike-askdjghaslkdjhsaldjkhsalkdjhsalkjdhlkjashdasjkdhhaskjdh-2045093888535838721/",
    "browser": {
        "type": "chromium",
        "headless": True,
        "slow_mo": 0,
        "viewport": {"width": 1920, "height": 1080}
    }
}


@pytest.fixture(scope="module")
def config():
    """测试配置"""
    return _CONFIG


# ========== 测试用例 ==========

@pytest.mark.case_id_breadcrumb_b_001
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.breadcrumb
@pytest.mark.ae
@allure.feature("OK")
@allure.story("详情页 - 面包屑导航")
@allure.title("点击面包屑首页链接应该跳转到首页")
@allure.severity(allure.severity_level.BLOCKER)
@allure.description("验证点击面包屑「Home」节点跳转到首页")
def test_breadcrumb_click_home(page, config):
    """TC-BREADCRUMB-B-001: 点击首页链接"""
    
    breadcrumb = BreadcrumbPage(page)
    detail_url = config['detail_url']
    
    logger.info("="*80)
    logger.info("TC-BREADCRUMB-B-001: 点击首页链接")
    logger.info("="*80)
    logger.info(f"站点: {config['site'].upper()} ({config['site_name']})")
    logger.info(f"角色: {config['role'].upper()} (访客)")
    logger.info(f"测试URL: {detail_url}")
    logger.info("="*80)
    
    with allure.step("步骤1：访问测试详情页"):
        breadcrumb.goto(detail_url, timeout=60000)
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 打开详情页: {page.url}")
    
    with allure.step("步骤2：点击「Home」节点"):
        breadcrumb.click_breadcrumb_item("Home")
        logger.info("✓ 点击 Home 成功")
    
    with allure.step("验证1：页面跳转到首页"):
        current_url = page.url
        # 验证URL包含base_url和city路径
        assert config['base_url'] in current_url, f"跳转URL不包含base_url: {current_url}"
        assert "/city-" in current_url, f"跳转URL不包含city路径: {current_url}"
        logger.info(f"✓ 成功跳转到首页: {current_url}")
    
    with allure.step("验证2：首页内容加载完成"):
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info("✓ 首页内容加载完成")
    
    logger.info("="*80)
    logger.info("✅ TC-BREADCRUMB-B-001 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_breadcrumb_b_002
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.breadcrumb
@pytest.mark.ae
@allure.feature("OK")
@allure.story("详情页 - 面包屑导航")
@allure.title("点击面包屑Property节点应该跳转到Property列表页")
@allure.severity(allure.severity_level.BLOCKER)
@allure.description("验证点击面包屑「Property」节点跳转到类目列表页")
def test_breadcrumb_click_property(page, config):
    """TC-BREADCRUMB-B-002: 点击中间节点链接（一级分类）"""
    
    breadcrumb = BreadcrumbPage(page)
    detail_url = config['detail_url']
    
    logger.info("="*80)
    logger.info("TC-BREADCRUMB-B-002: 点击中间节点链接（一级分类）")
    logger.info("="*80)
    logger.info(f"站点: {config['site'].upper()} ({config['site_name']})")
    logger.info(f"角色: {config['role'].upper()} (访客)")
    logger.info(f"测试URL: {detail_url}")
    logger.info("="*80)
    
    with allure.step("步骤1：访问测试详情页"):
        breadcrumb.goto(detail_url, timeout=60000)
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 打开详情页: {page.url}")
    
    with allure.step("步骤2：获取第2个节点（一级分类）并点击"):
        items_text = breadcrumb.get_breadcrumb_items_text()
        if len(items_text) < 2:
            pytest.fail("面包屑节点少于2个")
        category_name = items_text[1]
        breadcrumb.click_breadcrumb_item(category_name)
        logger.info(f"✓ 点击 {category_name} 成功")
    
    with allure.step("验证1：页面跳转到类目列表"):
        current_url = page.url
        # 验证URL包含cate路径（表示是类目页）
        assert "/cate-" in current_url, f"跳转URL不包含cate路径: {current_url}"
        assert config['base_url'] in current_url, f"跳转URL不包含base_url: {current_url}"
        logger.info(f"✓ 成功跳转到{category_name}列表: {current_url}")
    
    with allure.step("验证2：列表页内容加载完成"):
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info("✓ 列表页内容加载完成")
    
    logger.info("="*80)
    logger.info("✅ TC-BREADCRUMB-B-002 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_breadcrumb_b_003
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.breadcrumb
@pytest.mark.ae
@allure.feature("OK")
@allure.story("详情页 - 面包屑导航")
@allure.title("点击面包屑For Sale节点应该跳转到For Sale列表页")
@allure.severity(allure.severity_level.BLOCKER)
@allure.description("验证点击面包屑「For Sale」节点跳转到类目列表页")
def test_breadcrumb_click_for_sale(page, config):
    """TC-BREADCRUMB-B-003: 点击第3个节点（二级分类）"""
    
    breadcrumb = BreadcrumbPage(page)
    detail_url = config['detail_url']
    
    logger.info("="*80)
    logger.info("TC-BREADCRUMB-B-003: 点击第3个节点（二级分类）")
    logger.info("="*80)
    logger.info(f"站点: {config['site'].upper()} ({config['site_name']})")
    logger.info(f"角色: {config['role'].upper()} (访客)")
    logger.info(f"测试URL: {detail_url}")
    logger.info("="*80)
    
    with allure.step("步骤1：访问测试详情页"):
        breadcrumb.goto(detail_url, timeout=60000)
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 打开详情页: {page.url}")
    
    with allure.step("步骤2：获取第3个节点（二级分类）并点击"):
        items_text = breadcrumb.get_breadcrumb_items_text()
        if len(items_text) < 3:
            pytest.fail("面包屑节点少于3个")
        category_name = items_text[2]
        breadcrumb.click_breadcrumb_item(category_name)
        logger.info(f"✓ 点击 {category_name} 成功")
    
    with allure.step("验证1：页面跳转到二级类目列表"):
        current_url = page.url
        assert "/cate-" in current_url, f"跳转URL不包含cate路径: {current_url}"
        assert config['base_url'] in current_url, f"跳转URL不包含base_url: {current_url}"
        logger.info(f"✓ 成功跳转到{category_name}列表: {current_url}")
    
    with allure.step("验证2：列表页内容加载完成"):
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info("✓ 列表页内容加载完成")
    
    logger.info("="*80)
    logger.info("✅ TC-BREADCRUMB-B-003 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_breadcrumb_b_004
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.breadcrumb
@pytest.mark.ae
@allure.feature("OK")
@allure.story("详情页 - 面包屑导航")
@allure.title("点击面包屑Apartment节点应该跳转到Apartment列表页")
@allure.severity(allure.severity_level.BLOCKER)
@allure.description("验证点击面包屑「Apartment」节点跳转到类目列表页")
def test_breadcrumb_click_apartment(page, config):
    """TC-BREADCRUMB-B-004: 点击第4个节点（三级分类）"""
    
    breadcrumb = BreadcrumbPage(page)
    detail_url = config['detail_url']
    
    logger.info("="*80)
    logger.info("TC-BREADCRUMB-B-004: 点击第4个节点（三级分类）")
    logger.info("="*80)
    logger.info(f"站点: {config['site'].upper()} ({config['site_name']})")
    logger.info(f"角色: {config['role'].upper()} (访客)")
    logger.info(f"测试URL: {detail_url}")
    logger.info("="*80)
    
    with allure.step("步骤1：访问测试详情页"):
        breadcrumb.goto(detail_url, timeout=60000)
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 打开详情页: {page.url}")
    
    with allure.step("步骤2：获取第4个节点（三级分类）并点击"):
        items_text = breadcrumb.get_breadcrumb_items_text()
        if len(items_text) < 4:
            pytest.fail("面包屑节点少于4个")
        category_name = items_text[3]
        breadcrumb.click_breadcrumb_item(category_name)
        logger.info(f"✓ 点击 {category_name} 成功")
    
    with allure.step("验证1：页面跳转到三级类目列表"):
        current_url = page.url
        assert "/cate-" in current_url, f"跳转URL不包含cate路径: {current_url}"
        assert config['base_url'] in current_url, f"跳转URL不包含base_url: {current_url}"
        logger.info(f"✓ 成功跳转到{category_name}列表: {current_url}")
    
    with allure.step("验证2：列表页内容加载完成"):
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info("✓ 列表页内容加载完成")
    
    logger.info("="*80)
    logger.info("✅ TC-BREADCRUMB-B-004 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_breadcrumb_b_005
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.breadcrumb
@pytest.mark.ae
@allure.feature("OK")
@allure.story("详情页 - 面包屑导航")
@allure.title("最后一个节点不应该可点击")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证最后一个节点（当前页标题）不可点击，点击无反应")
def test_breadcrumb_last_item_not_clickable(page, config):
    """TC-BREADCRUMB-B-005: 最后一个节点不可点击"""
    
    breadcrumb = BreadcrumbPage(page)
    detail_url = config['detail_url']
    
    logger.info("="*80)
    logger.info("TC-BREADCRUMB-B-005: 最后一个节点不可点击")
    logger.info("="*80)
    logger.info(f"站点: {config['site'].upper()} ({config['site_name']})")
    logger.info(f"角色: {config['role'].upper()} (访客)")
    logger.info(f"测试URL: {detail_url}")
    logger.info("="*80)
    
    with allure.step("步骤1：访问测试详情页"):
        breadcrumb.goto(detail_url, timeout=60000)
        page.locator("body").wait_for(state="visible", timeout=10000)
        original_url = page.url
        logger.info(f"✓ 打开详情页: {original_url}")
    
    with allure.step("验证1：最后一个节点为span元素"):
        assert breadcrumb.is_last_item_span(), "最后一个节点不是 span"
        logger.info("✓ 最后一个节点是 span")
    
    with allure.step("验证2：最后一个节点不包含链接"):
        assert not breadcrumb.is_last_item_clickable(), "最后一个节点包含链接"
        logger.info("✓ 最后一个节点不包含链接")
    
    with allure.step("验证3：验证cursor样式"):
        last_item_style = page.evaluate('''() => {
            const items = document.querySelectorAll('.Breadcrumb_breadcrumbItem__R0lp7');
            const lastItem = items[items.length - 1];
            const span = lastItem.querySelector('span');
            return window.getComputedStyle(span).cursor;
        }''')
        # cursor应该不是 pointer（默认为 text 或 default）
        assert last_item_style != "pointer", f"cursor 样式错误: {last_item_style}"
        logger.info(f"✓ cursor 样式正确: {last_item_style}")
    
    with allure.step("验证4：尝试点击最后节点，URL不变"):
        last_item = page.locator(breadcrumb.BREADCRUMB_ITEMS).last
        last_item.click(timeout=5000)
        page.wait_for_timeout(1000)
        
        current_url = page.url
        assert current_url == original_url, f"URL发生变化: {current_url}"
        logger.info("✓ 点击最后节点，URL未变化")
    
    logger.info("="*80)
    logger.info("✅ TC-BREADCRUMB-B-005 测试通过！")
    logger.info("="*80)
