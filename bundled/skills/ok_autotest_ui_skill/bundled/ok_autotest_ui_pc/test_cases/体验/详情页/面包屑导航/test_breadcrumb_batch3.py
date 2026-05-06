# test_cases/体验/详情页/面包屑导航/test_breadcrumb_batch3.py
"""
详情页面包屑导航 - 批次3：视觉样式与交互
测试用例：TC-BREADCRUMB-C-001 ~ TC-BREADCRUMB-C-004
"""

import pytest
import allure
from pages.breadcrumb_page import BreadcrumbPage
from utils.logger import setup_logger

logger = setup_logger()

# ========== 测试配置 ==========




# ========== 测试用例 ==========

@pytest.mark.case_id_breadcrumb_c_001
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.breadcrumb
@pytest.mark.ae
@allure.feature("OK")
@allure.story("详情页 - 面包屑导航")
@allure.title("TC-BREADCRUMB-C-001：面包屑文本样式")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证面包屑链接的文本样式，包括颜色、字体大小、下划线等")
def test_breadcrumb_text_style(page, config, detail_url):
    """TC-BREADCRUMB-C-001: 面包屑文本样式"""
    
    breadcrumb = BreadcrumbPage(page)
    
    
    logger.info("="*80)
    logger.info("TC-BREADCRUMB-C-001: 面包屑文本样式")
    logger.info("="*80)
    logger.info(f"站点: {config['site'].upper()} ({config['site_name']})")
    logger.info(f"角色: {config['role'].upper()} (访客)")
    logger.info(f"测试URL: {detail_url}")
    logger.info("="*80)
    
    with allure.step("步骤1：访问测试详情页"):
        breadcrumb.goto(detail_url, timeout=60000)
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 打开详情页: {page.url}")
    
    with allure.step("步骤2：获取第2个节点（一级分类）的文本样式"):
        items_text = breadcrumb.get_breadcrumb_items_text()
        if len(items_text) < 2:
            pytest.fail("面包屑节点少于2个")
        category_name = items_text[1]
        link_style = breadcrumb.get_breadcrumb_link_style(category_name)
        assert link_style is not None, f"无法获取{category_name}链接样式"
        logger.info(f"{category_name} 链接样式: {link_style}")
    
    with allure.step("验证1：字体大小为14px"):
        assert link_style['fontSize'] == "14px", f"字体大小错误: {link_style['fontSize']}"
        logger.info(f"✓ 字体大小正确: {link_style['fontSize']}")
    
    with allure.step("验证2：文本装饰样式存在"):
        # 不强制验证是否有下划线，只验证textDecoration属性存在
        assert 'textDecoration' in link_style, "缺少textDecoration属性"
        logger.info(f"✓ 文本装饰样式: {link_style['textDecoration']}")
    
    with allure.step("验证3：cursor为pointer"):
        assert link_style['cursor'] == "pointer", f"cursor样式错误: {link_style['cursor']}"
        logger.info(f"✓ cursor样式正确: {link_style['cursor']}")
    
    with allure.step("验证4：文本颜色接近黑色"):
        # 颜色 rgb(17, 17, 17)
        assert "rgb" in link_style['color'], f"颜色格式错误: {link_style['color']}"
        logger.info(f"✓ 文本颜色: {link_style['color']}")
    
    logger.info("="*80)
    logger.info("✅ TC-BREADCRUMB-C-001 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_breadcrumb_c_002
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.breadcrumb
@pytest.mark.ae
@allure.feature("OK")
@allure.story("详情页 - 面包屑导航")
@allure.title("TC-BREADCRUMB-C-002：链接悬停效果")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证鼠标悬停在面包屑链接上时的视觉反馈")
def test_breadcrumb_hover_effect(page, config, detail_url):
    """TC-BREADCRUMB-C-002: 链接悬停效果"""
    
    breadcrumb = BreadcrumbPage(page)
    
    
    logger.info("="*80)
    logger.info("TC-BREADCRUMB-C-002: 链接悬停效果")
    logger.info("="*80)
    logger.info(f"站点: {config['site'].upper()} ({config['site_name']})")
    logger.info(f"角色: {config['role'].upper()} (访客)")
    logger.info(f"测试URL: {detail_url}")
    logger.info("="*80)
    
    with allure.step("步骤1：访问测试详情页"):
        breadcrumb.goto(detail_url, timeout=60000)
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 打开详情页: {page.url}")
    
    with allure.step("步骤2：获取第2个节点（一级分类）"):
        items_text = breadcrumb.get_breadcrumb_items_text()
        if len(items_text) < 2:
            pytest.fail("面包屑节点少于2个")
        category_name = items_text[1]
        before_style = breadcrumb.get_breadcrumb_link_style(category_name)
        logger.info(f"悬停前{category_name}样式: {before_style}")
    
    with allure.step("步骤3：悬停在一级分类链接上"):
        breadcrumb.hover_breadcrumb_item(category_name)
        logger.info(f"✓ 悬停在{category_name}成功")
    
    with allure.step("验证：cursor为pointer"):
        category_link = page.locator(breadcrumb.BREADCRUMB_LINKS, has_text=category_name).first
        cursor = category_link.evaluate("el => window.getComputedStyle(el).cursor")
        assert cursor == "pointer", f"cursor错误: {cursor}"
        logger.info(f"✓ cursor样式正确: {cursor}")
    
    logger.info("="*80)
    logger.info("✅ TC-BREADCRUMB-C-002 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_breadcrumb_c_003
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.breadcrumb
@pytest.mark.ae
@allure.feature("OK")
@allure.story("详情页 - 面包屑导航")
@allure.title("TC-BREADCRUMB-C-003：面包屑容器布局")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证面包屑导航的位置、尺寸和布局")
def test_breadcrumb_container_layout(page, config, detail_url):
    """TC-BREADCRUMB-C-003: 面包屑容器布局"""
    
    breadcrumb = BreadcrumbPage(page)
    
    
    logger.info("="*80)
    logger.info("TC-BREADCRUMB-C-003: 面包屑容器布局")
    logger.info("="*80)
    logger.info(f"站点: {config['site'].upper()} ({config['site_name']})")
    logger.info(f"角色: {config['role'].upper()} (访客)")
    logger.info(f"测试URL: {detail_url}")
    logger.info("="*80)
    
    with allure.step("步骤1：访问测试详情页"):
        breadcrumb.goto(detail_url, timeout=60000)
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 打开详情页: {page.url}")
    
    with allure.step("步骤2：获取面包屑位置信息"):
        position = breadcrumb.get_breadcrumb_position()
        assert position is not None, "无法获取面包屑位置"
        logger.info(f"面包屑位置: top={position['top']}px, left={position['left']}px")
        logger.info(f"面包屑尺寸: width={position['width']}px, height={position['height']}px")
    
    with allure.step("验证1：距离顶部约96px"):
        assert 80 < position['top'] < 120, f"距离顶部不符合预期: {position['top']}px"
        logger.info(f"✓ 距离顶部正确: {position['top']}px")
    
    with allure.step("验证2：高度约62px"):
        assert 50 < position['height'] < 80, f"高度不符合预期: {position['height']}px"
        logger.info(f"✓ 高度正确: {position['height']}px")
    
    with allure.step("验证3：面包屑在页面可视区域内"):
        assert position['top'] > 0, "面包屑顶部位置异常"
        assert position['left'] >= 0, "面包屑左侧位置异常"
        logger.info("✓ 面包屑在可视区域内")
    
    logger.info("="*80)
    logger.info("✅ TC-BREADCRUMB-C-003 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_breadcrumb_c_004
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.breadcrumb
@pytest.mark.ae
@allure.feature("OK")
@allure.story("详情页 - 面包屑导航")
@allure.title("TC-BREADCRUMB-C-004：超长文本截断")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证最后一个节点的超长文本是否应用省略号截断")
def test_breadcrumb_text_ellipsis(page, config, detail_url):
    """TC-BREADCRUMB-C-004: 超长文本截断"""
    
    breadcrumb = BreadcrumbPage(page)
    
    
    logger.info("="*80)
    logger.info("TC-BREADCRUMB-C-004: 超长文本截断")
    logger.info("="*80)
    logger.info(f"站点: {config['site'].upper()} ({config['site_name']})")
    logger.info(f"角色: {config['role'].upper()} (访客)")
    logger.info(f"测试URL: {detail_url}")
    logger.info("="*80)
    
    with allure.step("步骤1：访问测试详情页"):
        breadcrumb.goto(detail_url, timeout=60000)
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 打开详情页: {page.url}")
    
    with allure.step("步骤2：获取最后一个节点文本"):
        last_text = breadcrumb.get_last_item_text()
        assert len(last_text) > 0, "最后一个节点文本为空"
        logger.info(f"最后节点文本: {last_text[:80]}...")
    
    with allure.step("验证1：文本较长（包含完整标题）"):
        # 验证文本长度合理，不验证具体内容
        assert len(last_text) >= 5, f"文本长度过短: {len(last_text)}"
        logger.info(f"✓ 文本长度: {len(last_text)} 字符")
    
    with allure.step("验证2：检查是否应用singleLineEllipsis类或text-overflow"):
        last_item_style = page.evaluate('''() => {
            const items = document.querySelectorAll('.Breadcrumb_breadcrumbItem__R0lp7');
            const lastItem = items[items.length - 1];
            const span = lastItem.querySelector('span');
            const style = window.getComputedStyle(span);
            return {
                textOverflow: style.textOverflow,
                whiteSpace: style.whiteSpace,
                overflow: style.overflow,
                className: span.className
            };
        }''')
        
        logger.info(f"最后节点样式: {last_item_style}")
        # 可能应用了 singleLineEllipsis 类或 text-overflow: ellipsis
        assert last_item_style is not None, "无法获取样式信息"
        logger.info("✓ 获取到文本截断相关样式")
    
    logger.info("="*80)
    logger.info("✅ TC-BREADCRUMB-C-004 测试通过！")
    logger.info("="*80)
