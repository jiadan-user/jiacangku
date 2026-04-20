"""
OK.com - 定位面板功能测试（批次1：TC001-TC005）

本脚本由 playwright-test-generator 生成
测试文档：OK.com-定位面板-测试用例-20260228-实测版-2026-03-09.md
生成时间：2026-03-09

测试站点：AE (https://ae.ok.com)
测试角色：Visitor (访客，无需登录)
测试批次：Batch 1 (TC001-TC005)
测试目标：验证定位面板的核心交互功能

包含测试用例:
- TC001: 点击定位图标应打开定位面板
- TC002: 从Top Cities选择城市应成功切换并关闭面板
- TC003: 从All Cities选择城市应成功切换并关闭面板
- TC005: 点击面板外部应关闭定位面板
"""
import pytest
import allure
from playwright.sync_api import Page
from pages.location_panel_page import LocationPanelPage
from utils.logger import setup_logger

logger = setup_logger()

# ============================================
# 测试环境配置（来自测试文档）
# ============================================
_CONFIG = {
    "site": "ae",
    "site_name": "阿联酋站",
    "role": "visitor",
    "user_name": "visitor_ae",
    "base_url": "https://ae.58v5.cn",
    "test_account": None,  # 无需登录
    "locale": "en-AE",
    "currency": "AED",
    "browser": {
        "type": "chromium",
        "headless": True,
        "viewport": {"width": 1920, "height": 1080}
    },
    "timeout": {
        "default": 30000,
        "wait": 10000,
        "navigation": 30000
    }
}


@pytest.mark.case_id_tc001
@pytest.mark.p1
@pytest.mark.smoke
@pytest.mark.location_panel
@pytest.mark.ae
@pytest.mark.batch1
@allure.feature("OK")
@allure.story("定位面板打开/关闭 - 正向场景")
@allure.title("TC001 - 点击定位图标应打开定位面板")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证用户点击页面顶部导航栏的定位图标时，定位面板能够正确打开并显示所有必要元素")
def test_click_location_icon_should_open_panel(page: Page, config: dict):
    """TC001: 点击定位图标应打开定位面板"""
    
    # ========== Arrange：准备测试数据和对象 ==========
    location_panel_page = LocationPanelPage(page)
    
    # 从 config 读取配置
    site = config['site']
    role = config['role']
    base_url = config['base_url']
    site_name = config['site_name']
    
    # 记录测试配置
    logger.info("="*80)
    logger.info("TC001 - 点击定位图标应打开定位面板")
    logger.info("="*80)
    logger.info(f"站点: {site.upper()} ({site_name})")
    logger.info(f"角色: {role.upper()} (访客)")
    logger.info(f"Base URL: {base_url}")
    logger.info("="*80)
    
    # ========== Act 阶段：执行操作 ==========
    with allure.step("步骤1：打开阿联酋站Abu Dhabi城市页面"):
        # 直接导航到城市页面
        location_panel_page.goto(f"{base_url}/en/city-abu-dhabi/")
        logger.info(f"✓ 打开城市页面: {base_url}/en/city-abu-dhabi/")
        
        # 等待页面加载完成
        page.wait_for_load_state("load", timeout=30000)
    
    with allure.step("步骤2：点击定位图标"):
        location_panel_page.click_location_icon()
        logger.info("✓ 点击定位图标")
    
    # ========== Assert 阶段：验证结果 ==========
    with allure.step("验证1：定位面板已打开"):
        assert location_panel_page.is_location_panel_open(), "定位面板未打开"
        logger.info("✓ 定位面板已成功打开")
    
    with allure.step("验证2：检查面板关键元素"):
        elements_status = location_panel_page.verify_location_panel_elements()
        
        # 验证搜索框
        assert elements_status["search_input"], "搜索框未显示"
        logger.info("✓ 搜索框显示正常")
        
        # 验证当前位置
        assert elements_status["current_location"], "当前位置未显示"
        logger.info("✓ 当前位置显示正常")
        
        # 验证Top Cities部分
        assert elements_status["top_cities_section"], "Top Cities部分未显示"
        logger.info("✓ Top Cities部分显示正常")
        
        # 验证字母索引
        assert elements_status["alphabet_nav"], "字母索引未显示"
        logger.info("✓ 字母索引显示正常")
        
        # 验证城市列表
        assert elements_status["cities_list"], "城市列表未显示"
        logger.info("✓ 城市列表显示正常")
    
    logger.info("="*80)
    logger.info("✅ TC001 测试通过")
    logger.info("="*80)


@pytest.mark.case_id_tc002
@pytest.mark.p1
@pytest.mark.smoke
@pytest.mark.location_panel
@pytest.mark.ae
@pytest.mark.batch1
@allure.feature("OK")
@allure.story("城市切换 - Top Cities - 正向场景")
@allure.title("TC002 - 从Top Cities选择城市应成功切换并关闭面板")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证用户从Top Cities部分选择城市后，页面能够成功切换到目标城市，且定位面板自动关闭")
def test_select_city_from_top_cities_should_switch_and_close_panel(page: Page, config: dict):
    """TC002: 从Top Cities选择城市应成功切换并关闭面板"""
    
    # ========== Arrange：准备测试数据和对象 ==========
    location_panel_page = LocationPanelPage(page)
    
    base_url = config['base_url']
    target_city = "Dubai"
    
    logger.info("="*80)
    logger.info("TC002 - 从Top Cities选择城市应成功切换并关闭面板")
    logger.info("="*80)
    logger.info(f"目标城市: {target_city}")
    logger.info("="*80)
    
    # ========== Act 阶段：执行操作 ==========
    with allure.step("步骤1：打开阿联酋站首页并等待自动跳转完成"):
        location_panel_page.goto(base_url)
        logger.info(f"✓ 打开首页: {base_url}")
        page.wait_for_load_state("networkidle", timeout=30000)
        # 等待首页自动跳转到城市页完成
        try:
            page.wait_for_url("**/city-*/**", timeout=15000)
            logger.info(f"✓ 首页自动跳转完成: {page.url}")
        except Exception:
            logger.info(f"⚠ 首页未跳转或已在城市页: {page.url}")
        
        # 额外等待页面完全稳定
        page.wait_for_timeout(3000)
    
    with allure.step("步骤2：点击定位图标打开面板"):
        location_panel_page.click_location_icon()
        logger.info("✓ 定位面板已打开")
    
    with allure.step(f"步骤3：从Top Cities选择 {target_city}"):
        location_panel_page.select_city_from_top_cities(target_city)
        logger.info(f"✓ 已点击Top Cities中的 {target_city}")
    
    # ========== Assert 阶段：验证结果 ==========
    with allure.step("验证1：URL已更新为目标城市"):
        current_city_url = location_panel_page.get_current_city_from_url()
        assert current_city_url == target_city.lower(), f"URL未正确切换到{target_city}"
        logger.info(f"✓ URL已切换到: {current_city_url}")
    
    with allure.step("验证2：页面标题已更新"):
        assert location_panel_page.verify_page_title_contains(target_city), \
            f"页面标题未包含 {target_city}"
        logger.info(f"✓ 页面标题包含 {target_city}")
    
    with allure.step("验证3：定位面板已自动关闭"):
        assert location_panel_page.is_location_panel_closed(), "定位面板未关闭"
        logger.info("✓ 定位面板已自动关闭")
    
    logger.info("="*80)
    logger.info("✅ TC002 测试通过")
    logger.info("="*80)


@pytest.mark.case_id_tc003
@pytest.mark.p1
@pytest.mark.smoke
@pytest.mark.location_panel
@pytest.mark.ae
@pytest.mark.batch1
@allure.feature("OK")
@allure.story("城市切换 - All Cities - 正向场景")
@allure.title("TC003 - 从All Cities选择城市应成功切换并关闭面板")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证用户从All Cities列表选择城市后，页面能够成功切换到目标城市，且定位面板自动关闭")
def test_select_city_from_all_cities_should_switch_and_close_panel(page: Page, config: dict):
    """TC003: 从All Cities选择城市应成功切换并关闭面板"""
    
    # ========== Arrange：准备测试数据和对象 ==========
    location_panel_page = LocationPanelPage(page)
    
    base_url = config['base_url']
    # 首先导航到Dubai，然后从All Cities切换回Abu Dhabi
    target_city = "Abu Dhabi"
    
    logger.info("="*80)
    logger.info("TC003 - 从All Cities选择城市应成功切换并关闭面板")
    logger.info("="*80)
    logger.info(f"目标城市: {target_city}")
    logger.info("="*80)
    
    # ========== Act 阶段：执行操作 ==========
    with allure.step("步骤1：打开Dubai页面"):
        # 先访问Dubai，为了测试从All Cities切换
        location_panel_page.goto(f"{base_url}/en/city-dubai/")
        logger.info("✓ 打开Dubai页面")
        page.wait_for_load_state("load", timeout=30000)
    
    with allure.step("步骤2：点击定位图标打开面板"):
        location_panel_page.click_location_icon()
        logger.info("✓ 定位面板已打开")
    
    with allure.step(f"步骤3：从All Cities列表选择 {target_city}"):
        location_panel_page.select_city_from_all_cities(target_city)
        logger.info(f"✓ 已从城市列表点击 {target_city}")
    
    # ========== Assert 阶段：验证结果 ==========
    with allure.step("验证1：URL已更新为目标城市"):
        current_city_url = location_panel_page.get_current_city_from_url()
        expected_city_url = "abu-dhabi"
        assert current_city_url == expected_city_url, f"URL未正确切换到{target_city}"
        logger.info(f"✓ URL已切换到: {current_city_url}")
    
    with allure.step("验证2：页面标题已更新"):
        assert location_panel_page.verify_page_title_contains(target_city), \
            f"页面标题未包含 {target_city}"
        logger.info(f"✓ 页面标题包含 {target_city}")
    
    with allure.step("验证3：定位面板已自动关闭"):
        assert location_panel_page.is_location_panel_closed(), "定位面板未关闭"
        logger.info("✓ 定位面板已自动关闭")
    
    logger.info("="*80)
    logger.info("✅ TC003 测试通过")
    logger.info("="*80)


@pytest.mark.case_id_tc005
@pytest.mark.p1
@pytest.mark.smoke
@pytest.mark.location_panel
@pytest.mark.ae
@pytest.mark.batch1
@allure.feature("OK")
@allure.story("定位面板打开/关闭 - 正向场景")
@allure.title("TC005 - 点击面板外部应关闭定位面板")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证用户点击定位面板外部区域时，面板能够正确关闭")
def test_click_outside_panel_should_close_panel(page: Page, config: dict):
    """TC005: 点击面板外部应关闭定位面板"""
    
    # ========== Arrange：准备测试数据和对象 ==========
    location_panel_page = LocationPanelPage(page)
    
    base_url = config['base_url']
    
    logger.info("="*80)
    logger.info("TC005 - 点击面板外部应关闭定位面板")
    logger.info("="*80)
    
    # ========== Act 阶段：执行操作 ==========
    with allure.step("步骤1：打开阿联酋站首页并等待自动跳转完成"):
        location_panel_page.goto(base_url)
        logger.info(f"✓ 打开首页: {base_url}")
        page.wait_for_load_state("networkidle", timeout=30000)
        # 等待首页自动跳转到城市页完成
        try:
            page.wait_for_url("**/city-*/**", timeout=15000)
            logger.info(f"✓ 首页自动跳转完成: {page.url}")
        except Exception:
            logger.info(f"⚠ 首页未跳转或已在城市页: {page.url}")
        
        # 额外等待页面完全稳定
        page.wait_for_timeout(3000)
    
    with allure.step("步骤2：点击定位图标打开面板"):
        location_panel_page.click_location_icon()
        logger.info("✓ 定位面板已打开")
        
        # 确认面板已打开
        assert location_panel_page.is_location_panel_open(), "定位面板未打开"
    
    with allure.step("步骤3：点击面板外部区域"):
        location_panel_page.click_outside_panel()
        logger.info("✓ 已点击面板外部")
    
    # ========== Assert 阶段：验证结果 ==========
    with allure.step("验证：定位面板已关闭"):
        assert location_panel_page.is_location_panel_closed(), "定位面板未关闭"
        logger.info("✓ 定位面板已成功关闭")
    
    logger.info("="*80)
    logger.info("✅ TC005 测试通过")
    logger.info("="*80)
