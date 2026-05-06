# test_cases/体验/详情页/面包屑导航/test_breadcrumb_batch4.py
"""
详情页面包屑导航 - 批次4：响应式设计
测试用例：TC-BREADCRUMB-D-001 ~ TC-BREADCRUMB-D-002
"""

import pytest
import allure
from pages.breadcrumb_page import BreadcrumbPage
from utils.logger import setup_logger

logger = setup_logger()

# ========== 测试配置 ==========

@pytest.fixture(scope="module")
def config_mobile(config):
    """移动端配置"""
    mobile_config = config.copy()
    mobile_config["browser"] = {
        **config['browser'],
        "viewport": {"width": 375, "height": 667}  # iPhone
    }
    return mobile_config


@pytest.fixture(scope="module")
def config_tablet(config):
    """平板配置"""
    tablet_config = config.copy()
    tablet_config["browser"] = {
        **config['browser'],
        "viewport": {"width": 768, "height": 1024}  # iPad
    }
    return tablet_config








# ========== 测试用例 ==========

@pytest.mark.case_id_breadcrumb_d_001
@pytest.mark.responsive
@pytest.mark.p1
@pytest.mark.breadcrumb
@pytest.mark.ae
@pytest.mark.mobile
@allure.feature("OK")
@allure.story("详情页 - 面包屑导航")
@allure.title("TC-BREADCRUMB-D-001：移动端显示（375px）")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证面包屑导航在移动端（375px）的显示和功能")
def test_breadcrumb_mobile_display(page, config_mobile):
    """TC-BREADCRUMB-D-001: 移动端显示（375px）"""
    
    breadcrumb = BreadcrumbPage(page)
    detail_url = config_mobile['detail_url']
    
    logger.info("="*80)
    logger.info("TC-BREADCRUMB-D-001: 移动端显示（375px）")
    logger.info("="*80)
    logger.info(f"站点: {config_mobile['site'].upper()} ({config_mobile['site_name']})")
    logger.info(f"角色: {config_mobile['role'].upper()} (访客)")
    logger.info(f"Viewport: {config_mobile['browser']['viewport']}")
    logger.info(f"测试URL: {detail_url}")
    logger.info("="*80)
    
    with allure.step("步骤1：访问测试详情页"):
        breadcrumb.goto(detail_url, timeout=60000)
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 打开详情页: {page.url}")
    
    with allure.step("验证1：面包屑导航可见"):
        assert breadcrumb.is_breadcrumb_visible(timeout=10000), "面包屑导航不可见"
        logger.info("✓ 面包屑导航可见")
    
    with allure.step("验证2：面包屑节点数量正确"):
        items_count = breadcrumb.get_breadcrumb_items_count()
        assert items_count >= 4, f"节点数量太少: {items_count}"
        logger.info(f"✓ 节点数量: {items_count}")
    
    with allure.step("验证3：获取面包屑位置"):
        position = breadcrumb.get_breadcrumb_position()
        logger.info(f"移动端面包屑位置: top={position['top']}px, width={position['width']}px, height={position['height']}px")
        assert position is not None, "无法获取位置"
        logger.info("✓ 位置信息正常")
    
    with allure.step("验证4：链接功能正常（点击Home）"):
        breadcrumb.click_breadcrumb_item("Home")
        page.wait_for_timeout(2000)
        current_url = page.url
        # 验证URL包含base_url和city路径
        assert config_mobile['base_url'] in current_url, f"跳转URL不包含base_url: {current_url}"
        assert "/city-" in current_url, f"跳转URL不包含city路径: {current_url}"
        logger.info(f"✓ 移动端链接点击正常: {current_url}")
    
    logger.info("="*80)
    logger.info("✅ TC-BREADCRUMB-D-001 测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_breadcrumb_d_002
@pytest.mark.responsive
@pytest.mark.p2
@pytest.mark.breadcrumb
@pytest.mark.ae
@allure.feature("OK")
@allure.story("详情页 - 面包屑导航")
@allure.title("TC-BREADCRUMB-D-002：平板端显示（768px）")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证面包屑导航在平板端（768px）的显示和功能")
def test_breadcrumb_tablet_display(page, config_tablet):
    """TC-BREADCRUMB-D-002: 平板端显示（768px）"""
    
    breadcrumb = BreadcrumbPage(page)
    detail_url = config_tablet['detail_url']
    
    logger.info("="*80)
    logger.info("TC-BREADCRUMB-D-002: 平板端显示（768px）")
    logger.info("="*80)
    logger.info(f"站点: {config_tablet['site'].upper()} ({config_tablet['site_name']})")
    logger.info(f"角色: {config_tablet['role'].upper()} (访客)")
    logger.info(f"Viewport: {config_tablet['browser']['viewport']}")
    logger.info(f"测试URL: {detail_url}")
    logger.info("="*80)
    
    with allure.step("步骤1：访问测试详情页"):
        breadcrumb.goto(detail_url, timeout=60000)
        page.locator("body").wait_for(state="visible", timeout=10000)
        logger.info(f"✓ 打开详情页: {page.url}")
    
    with allure.step("验证1：面包屑导航可见"):
        assert breadcrumb.is_breadcrumb_visible(timeout=10000), "面包屑导航不可见"
        logger.info("✓ 面包屑导航可见")
    
    with allure.step("验证2：面包屑节点数量正确"):
        items_count = breadcrumb.get_breadcrumb_items_count()
        assert items_count >= 4, f"节点数量太少: {items_count}"
        logger.info(f"✓ 节点数量: {items_count}")
    
    with allure.step("验证3：获取面包屑位置"):
        position = breadcrumb.get_breadcrumb_position()
        logger.info(f"平板端面包屑位置: top={position['top']}px, width={position['width']}px, height={position['height']}px")
        assert position is not None, "无法获取位置"
        logger.info("✓ 位置信息正常")
    
    with allure.step("验证4：链接功能正常（点击一级分类）"):
        items_text = breadcrumb.get_breadcrumb_items_text()
        if len(items_text) < 2:
            pytest.fail("面包屑节点少于2个")
        category_name = items_text[1]
        breadcrumb.click_breadcrumb_item(category_name)
        page.wait_for_timeout(2000)
        current_url = page.url
        # 验证URL包含cate路径
        assert "/cate-" in current_url, f"跳转URL不包含cate路径: {current_url}"
        assert config_tablet['base_url'] in current_url, f"跳转URL不包含base_url: {current_url}"
        logger.info(f"✓ 平板端链接点击正常: {current_url}")
    
    logger.info("="*80)
    logger.info("✅ TC-BREADCRUMB-D-002 测试通过！")
    logger.info("="*80)
