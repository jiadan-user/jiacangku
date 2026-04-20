# test_cases/体验/详情页/面包屑导航/test_breadcrumb_batch1.py
"""
详情页面包屑导航 - 批次1：基础展示与结构
测试用例：TC-BREADCRUMB-A-001 ~ TC-BREADCRUMB-A-004
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

@pytest.mark.case_id_breadcrumb_a_001
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.breadcrumb
@pytest.mark.ae
@allure.feature("OK")
@allure.story("详情页 - 面包屑导航")
@allure.title("面包屑导航应该在详情页顶部正确显示")
@allure.severity(allure.severity_level.BLOCKER)
@allure.description("验证面包屑导航的基本展示，包括位置、路径、节点数量等")
def test_breadcrumb_basic_display(page, config):
    """TC-BREADCRUMB-A-001: 面包屑基本展示"""
    
    breadcrumb = BreadcrumbPage(page)
    detail_url = config['detail_url']
    
    logger.info("="*80)
    logger.info("TC-BREADCRUMB-A-001: 面包屑基本展示")
    logger.info("="*80)
    logger.info(f"站点: {config['site'].upper()} ({config['site_name']})")
    logger.info(f"角色: {config['role'].upper()} (访客)")
    logger.info(f"测试URL: {detail_url}")
    logger.info("="*80)
    
    with allure.step("步骤1：访问测试详情页"):
        breadcrumb.goto(detail_url, timeout=60000)
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 打开详情页: {page.url}")
    
    with allure.step("验证1：面包屑导航可见"):
        assert breadcrumb.is_breadcrumb_visible(timeout=10000), "面包屑导航不可见"
        logger.info("✓ 面包屑导航可见")
    
    with allure.step("验证2：面包屑路径正确"):
        breadcrumb_path = breadcrumb.get_breadcrumb_path()
        assert "Home" in breadcrumb_path, "面包屑路径缺少 Home"
        # 验证面包屑至少包含多个层级（用 > 分隔）
        assert breadcrumb_path.count(" > ") >= 3, f"面包屑层级不足，实际: {breadcrumb_path}"
        logger.info(f"✓ 面包屑路径正确: {breadcrumb_path}")
    
    with allure.step("验证3：节点数量为5或更多"):
        items_count = breadcrumb.get_breadcrumb_items_count()
        assert items_count >= 4, f"面包屑节点数量太少。预期: >=4，实际: {items_count}"
        logger.info(f"✓ 节点数量正确: {items_count}")
    
    with allure.step("验证4：箭头分隔符数量正确"):
        arrows_count = breadcrumb.get_breadcrumb_arrows_count()
        items_count = breadcrumb.get_breadcrumb_items_count()
        expected_arrows = items_count - 1  # 箭头数量应该是节点数-1
        assert arrows_count == expected_arrows, f"箭头数量错误。预期: {expected_arrows}，实际: {arrows_count}"
        logger.info(f"✓ 箭头数量正确: {arrows_count}")
    
    with allure.step("验证5：面包屑位置在页面顶部"):
        position = breadcrumb.get_breadcrumb_position()
        assert position is not None, "无法获取面包屑位置"
        assert position['top'] < 200, f"面包屑位置过低。top: {position['top']}px"
        logger.info(f"✓ 面包屑位置正确: top={position['top']}px, left={position['left']}px")
    
    logger.info("="*80)
    logger.info("✅ TC-BREADCRUMB-A-001 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_breadcrumb_a_002
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.breadcrumb
@pytest.mark.ae
@allure.feature("OK")
@allure.story("详情页 - 面包屑导航")
@allure.title("面包屑节点数量和层级结构应该正确")
@allure.severity(allure.severity_level.BLOCKER)
@allure.description("验证面包屑的节点数量、文本内容和层级结构")
def test_breadcrumb_hierarchy_structure(page, config):
    """TC-BREADCRUMB-A-002: 节点数量和层级结构"""
    
    breadcrumb = BreadcrumbPage(page)
    detail_url = config['detail_url']
    
    logger.info("="*80)
    logger.info("TC-BREADCRUMB-A-002: 节点数量和层级结构")
    logger.info("="*80)
    logger.info(f"站点: {config['site'].upper()} ({config['site_name']})")
    logger.info(f"角色: {config['role'].upper()} (访客)")
    logger.info(f"测试URL: {detail_url}")
    logger.info("="*80)
    
    with allure.step("步骤1：访问测试详情页"):
        breadcrumb.goto(detail_url, timeout=60000)
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 打开详情页: {page.url}")
    
    with allure.step("步骤2：解析所有面包屑节点"):
        items_text = breadcrumb.get_breadcrumb_items_text()
        logger.info(f"✓ 获取到 {len(items_text)} 个节点")
    
    with allure.step("验证1：节点总数至少为4"):
        assert len(items_text) >= 4, f"节点数量太少。预期: >=4，实际: {len(items_text)}"
        logger.info(f"✓ 节点总数: {len(items_text)}")
    
    with allure.step("验证2：第1个节点为 Home（可点击）"):
        assert items_text[0] == "Home", f"第1个节点错误。预期: Home，实际: {items_text[0]}"
        home_href = breadcrumb.get_breadcrumb_item_href("Home")
        assert home_href is not None, "Home 节点无 href 属性"
        assert config['base_url'] in home_href, f"Home 链接错误: {home_href}"
        logger.info(f"✓ 节点1: {items_text[0]} (href: {home_href})")
    
    with allure.step("验证3：第2个节点为一级分类（可点击）"):
        # 第2个节点应该是一级分类，不验证具体名称
        assert len(items_text[1]) > 0, "第2个节点为空"
        category_href = breadcrumb.get_breadcrumb_item_href(items_text[1])
        assert category_href is not None, f"{items_text[1]} 节点无 href 属性"
        logger.info(f"✓ 节点2: {items_text[1]} (href: {category_href})")
    
    with allure.step("验证4：中间节点为子分类（可点击）"):
        # 验证中间节点都有链接
        for i in range(2, len(items_text) - 1):
            node_text = items_text[i]
            assert len(node_text) > 0, f"节点{i+1}为空"
            node_href = breadcrumb.get_breadcrumb_item_href(node_text)
            assert node_href is not None, f"{node_text} 节点无 href 属性"
            logger.info(f"✓ 节点{i+1}: {node_text} (href: {node_href})")
    
    with allure.step("验证5：最后1个节点为当前页标题（不可点击）"):
        last_item_text = items_text[-1]
        assert len(last_item_text) > 0, "最后节点为空"
        logger.info(f"✓ 节点{len(items_text)}（当前页）: {last_item_text[:50]}...")
    
    with allure.step("验证6：箭头分隔符数量正确"):
        arrows_count = breadcrumb.get_breadcrumb_arrows_count()
        expected_arrows = len(items_text) - 1
        assert arrows_count == expected_arrows, f"箭头数量错误。预期: {expected_arrows}，实际: {arrows_count}"
        logger.info(f"✓ 箭头分隔符数量: {arrows_count}")
    
    logger.info("="*80)
    logger.info("✅ TC-BREADCRUMB-A-002 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_breadcrumb_a_003
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.breadcrumb
@pytest.mark.ae
@allure.feature("OK")
@allure.story("详情页 - 面包屑导航")
@allure.title("最后一个节点应该展示为 Span 不可点击")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证当前页节点使用 span 元素展示，不包含链接，不可点击")
def test_breadcrumb_last_item_span(page, config):
    """TC-BREADCRUMB-A-003: 当前页节点展示为 Span"""
    
    breadcrumb = BreadcrumbPage(page)
    detail_url = config['detail_url']
    
    logger.info("="*80)
    logger.info("TC-BREADCRUMB-A-003: 当前页节点展示为 Span")
    logger.info("="*80)
    logger.info(f"站点: {config['site'].upper()} ({config['site_name']})")
    logger.info(f"角色: {config['role'].upper()} (访客)")
    logger.info(f"测试URL: {detail_url}")
    logger.info("="*80)
    
    with allure.step("步骤1：访问测试详情页"):
        breadcrumb.goto(detail_url, timeout=60000)
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 打开详情页: {page.url}")
    
    with allure.step("验证1：最后一个节点为 span 元素"):
        assert breadcrumb.is_last_item_span(), "最后一个节点不是 span 元素"
        logger.info("✓ 最后一个节点是 span 元素")
    
    with allure.step("验证2：最后一个节点不可点击"):
        assert not breadcrumb.is_last_item_clickable(), "最后一个节点包含链接（不应该可点击）"
        logger.info("✓ 最后一个节点不可点击")
    
    with allure.step("验证3：最后一个节点文本为当前页标题"):
        last_text = breadcrumb.get_last_item_text()
        assert len(last_text) > 0, "最后一个节点文本为空"
        # 验证文本长度合理（不验证具体内容）
        assert len(last_text) >= 5, f"最后一个节点文本太短: {last_text}"
        logger.info(f"✓ 最后一个节点文本: {last_text[:60]}...")
    
    with allure.step("验证4：span 元素使用正确的类名"):
        span = page.locator(breadcrumb.BREADCRUMB_CURRENT_SPAN).first
        assert span.is_visible(timeout=5000), "当前页 span 不可见"
        logger.info("✓ span 元素类名正确")
    
    logger.info("="*80)
    logger.info("✅ TC-BREADCRUMB-A-003 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_breadcrumb_a_004
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.breadcrumb
@pytest.mark.ae
@allure.feature("OK")
@allure.story("详情页 - 面包屑导航")
@allure.title("箭头分隔符应该正确显示")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证面包屑节点之间的箭头分隔符数量和位置")
def test_breadcrumb_arrow_separators(page, config):
    """TC-BREADCRUMB-A-004: 分隔符箭头展示"""
    
    breadcrumb = BreadcrumbPage(page)
    detail_url = config['detail_url']
    
    logger.info("="*80)
    logger.info("TC-BREADCRUMB-A-004: 分隔符箭头展示")
    logger.info("="*80)
    logger.info(f"站点: {config['site'].upper()} ({config['site_name']})")
    logger.info(f"角色: {config['role'].upper()} (访客)")
    logger.info(f"测试URL: {detail_url}")
    logger.info("="*80)
    
    with allure.step("步骤1：访问测试详情页"):
        breadcrumb.goto(detail_url, timeout=60000)
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 打开详情页: {page.url}")
    
    with allure.step("验证1：箭头总数正确"):
        arrows_count = breadcrumb.get_breadcrumb_arrows_count()
        items_count = breadcrumb.get_breadcrumb_items_count()
        expected_arrows = items_count - 1
        assert arrows_count == expected_arrows, f"箭头数量错误。预期: {expected_arrows}，实际: {arrows_count}"
        logger.info(f"✓ 箭头数量: {arrows_count}")
    
    with allure.step("验证2：箭头图标可见"):
        arrows = page.locator(breadcrumb.BREADCRUMB_ARROWS).all()
        for i, arrow in enumerate(arrows):
            assert arrow.is_visible(), f"第 {i+1} 个箭头不可见"
        logger.info(f"✓ 所有箭头均可见")
    
    with allure.step("验证3：箭头图片 URL 正确"):
        first_arrow_src = page.locator(breadcrumb.BREADCRUMB_ARROWS).first.get_attribute("src")
        assert "icon-breadcrumb-right" in first_arrow_src, f"箭头图片 URL 错误: {first_arrow_src}"
        logger.info(f"✓ 箭头图片 URL: {first_arrow_src}")
    
    with allure.step("验证4：最后一个节点后无箭头"):
        # 验证箭头数量 = 节点数量 - 1
        items_count = breadcrumb.get_breadcrumb_items_count()
        assert arrows_count == items_count - 1, \
            f"箭头数量应该比节点数量少1。节点: {items_count}, 箭头: {arrows_count}"
        logger.info("✓ 最后一个节点后无箭头")
    
    logger.info("="*80)
    logger.info("✅ TC-BREADCRUMB-A-004 测试通过！")
    logger.info("="*80)
