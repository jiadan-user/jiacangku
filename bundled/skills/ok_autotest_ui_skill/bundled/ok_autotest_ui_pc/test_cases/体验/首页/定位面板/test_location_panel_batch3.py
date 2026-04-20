"""
OK.com - 定位面板功能测试（批次3：TC021、TC022、TC029、TC030）

本脚本由 playwright-test-generator 生成
测试文档：OK.com-定位面板-测试用例-20260228-实测版-2026-03-09.md
生成时间：2026-03-09

测试站点：AE (https://ae.ok.com)
测试角色：Visitor (访客，无需登录)
测试批次：Batch 3 (TC021、TC022、TC029、TC030)
测试目标：验证定位面板的Top Cities和Used Locations功能

包含测试用例:
- TC021: 选择城市后Used Locations应更新为最近选择
- TC022: 从Used Locations选择城市应成功切换
- TC029: Top Cities显示常用热门城市
- TC030: 从Top Cities选择Abu Dhabi应成功切换
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


@pytest.mark.case_id_tc021
@pytest.mark.p1
@pytest.mark.positive
@pytest.mark.location_panel
@pytest.mark.ae
@pytest.mark.batch3
@allure.feature("OK")
@allure.story("Used Locations - 正向场景")
@allure.title("TC021 - 选择城市后Used Locations应更新为最近选择")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证用户连续选择多个城市后，Used Locations能够正确显示最近访问的城市（不包括当前城市）")
def test_select_city_should_update_used_locations(page: Page, config: dict):
    """TC021: 选择城市后Used Locations应更新为最近选择"""
    
    # ========== Arrange：准备测试数据和对象 ==========
    location_panel_page = LocationPanelPage(page)
    
    base_url = config['base_url']
    
    logger.info("="*80)
    logger.info("TC021 - 选择城市后Used Locations应更新")
    logger.info("="*80)
    logger.info(f"站点: {config['site_name']}")
    logger.info("操作: Abu Dhabi → Dubai → Ajman，验证Used Locations显示Dubai")
    logger.info("="*80)
    
    # ========== Act 阶段：执行操作 ==========
    with allure.step("步骤1：访问Abu Dhabi页面（清除历史）"):
        page.goto(f"{base_url}/en/city-abu-dhabi/")
        page.wait_for_load_state("networkidle")
        logger.info("✓ 已访问Abu Dhabi（清除历史）")
    
    with allure.step("步骤2：选择Dubai"):
        location_panel_page.click_location_icon()
        assert location_panel_page.is_location_panel_open(), "定位面板未打开"
        location_panel_page.select_city_from_top_cities("Dubai")
        page.wait_for_timeout(2000)
        logger.info("✓ 已选择Dubai")
    
    with allure.step("步骤3：选择Ajman（让Used Locations出现）"):
        location_panel_page.click_location_icon()
        assert location_panel_page.is_location_panel_open(), "定位面板未打开"
        location_panel_page.select_city_from_all_cities("Ajman")
        page.wait_for_timeout(2000)
        logger.info("✓ 已选择Ajman")
    
    with allure.step("步骤4：重新打开定位面板"):
        location_panel_page.click_location_icon()
        assert location_panel_page.is_location_panel_open(), "定位面板未打开"
        logger.info("✓ 重新打开定位面板")
    
    # ========== Assert 阶段：验证结果 ==========
    with allure.step("验证1：Used Locations部分存在"):
        has_used_locations = location_panel_page.has_used_locations_section()
        logger.info(f"✓ Used Locations功能存在: {has_used_locations}")
        assert has_used_locations, "Used Locations功能未出现，不符合预期"
    
    with allure.step("验证2：Dubai出现在Used Locations中"):
        dubai_in_used_locations = page.locator(
            "[role='tooltip'] >> text='Used Locations' >> .. >> [class*='QuickCities_tagText']", 
            has_text="Dubai"
        )
        assert dubai_in_used_locations.is_visible(timeout=5000), "Dubai未出现在Used Locations中"
        logger.info("✓ Dubai出现在Used Locations中")
    
    with allure.step("验证3：Ajman（当前城市）未出现在Used Locations中"):
        ajman_in_used_locations = page.locator(
            "[role='tooltip'] >> text='Used Locations' >> .. >> [class*='QuickCities_tagText']", 
            has_text="Ajman"
        )
        assert not ajman_in_used_locations.is_visible(timeout=2000), "Ajman（当前城市）错误地出现在Used Locations中"
        logger.info("✓ Ajman（当前城市）未出现在Used Locations中，符合预期")
    
    logger.info("="*80)
    logger.info("✅ TC021 测试通过")
    logger.info("="*80)


@pytest.mark.case_id_tc022
@pytest.mark.p1
@pytest.mark.positive
@pytest.mark.location_panel
@pytest.mark.ae
@pytest.mark.batch3
@allure.feature("OK")
@allure.story("Used Locations - 正向场景")
@allure.title("TC022 - 从Used Locations选择城市应成功切换")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证用户从Used Locations部分选择城市后，页面能够成功切换到目标城市，且定位面板自动关闭")
def test_select_city_from_used_locations_should_switch(page: Page, config: dict):
    """TC022: 从Used Locations选择城市应成功切换"""
    
    # ========== Arrange：准备测试数据和对象 ==========
    location_panel_page = LocationPanelPage(page)
    
    base_url = config['base_url']
    
    logger.info("="*80)
    logger.info("TC022 - 从Used Locations选择城市应成功切换")
    logger.info("="*80)
    logger.info(f"站点: {config['site_name']}")
    logger.info("目标城市: Dubai（从Used Locations选择）")
    logger.info("="*80)
    
    # ========== Act 阶段：执行操作 - 前置：创建Used Locations历史 ==========
    with allure.step("前置步骤1：访问Abu Dhabi（起点）"):
        page.goto(f"{base_url}/en/city-abu-dhabi/")
        page.wait_for_load_state("networkidle")
        logger.info("✓ 已访问Abu Dhabi（起点）")
    
    with allure.step("前置步骤2：选择Dubai（创建历史）"):
        location_panel_page.click_location_icon()
        assert location_panel_page.is_location_panel_open(), "定位面板未打开"
        location_panel_page.select_city_from_top_cities("Dubai")
        page.wait_for_timeout(2000)
        logger.info("✓ 已选择Dubai（创建历史）")
    
    with allure.step("前置步骤3：选择Ajman（让Used Locations出现）"):
        location_panel_page.click_location_icon()
        assert location_panel_page.is_location_panel_open(), "定位面板未打开"
        location_panel_page.select_city_from_all_cities("Ajman")
        page.wait_for_timeout(2000)
        logger.info("✓ 已选择Ajman（让Used Locations出现）")
    
    # ========== Act 阶段：执行测试操作 ==========
    with allure.step("步骤1：打开定位面板"):
        location_panel_page.click_location_icon()
        assert location_panel_page.is_location_panel_open(), "定位面板未打开"
        logger.info("✓ 定位面板已打开")
    
    with allure.step("步骤2：验证Used Locations存在"):
        has_used_locations = location_panel_page.has_used_locations_section()
        logger.info(f"✓ Used Locations功能存在: {has_used_locations}")
        assert has_used_locations, "Used Locations功能未出现，不符合预期"
    
    with allure.step("步骤3：从Used Locations选择Dubai"):
        location_panel_page.select_city_from_used_locations("Dubai")
        logger.info("✓ 已从Used Locations点击Dubai")
    
    # ========== Assert 阶段：验证结果 ==========
    with allure.step("验证1：URL已切换到Dubai"):
        page.wait_for_timeout(2000)
        current_city = location_panel_page.get_current_city_from_url()
        assert current_city == "dubai", f"URL未切换到dubai，当前: {current_city}"
        logger.info(f"✓ URL已切换到: {current_city}")
    
    with allure.step("验证2：页面标题包含Dubai"):
        assert location_panel_page.verify_page_title_contains("Dubai"), "页面标题不包含Dubai"
        logger.info("✓ 页面标题包含Dubai")
    
    with allure.step("验证3：定位面板已自动关闭"):
        assert location_panel_page.is_location_panel_closed(), "定位面板未关闭"
        logger.info("✓ 定位面板已自动关闭")
    
    logger.info("="*80)
    logger.info("✅ TC022 测试通过")
    logger.info("="*80)


@pytest.mark.case_id_tc029
@pytest.mark.p1
@pytest.mark.ui
@pytest.mark.location_panel
@pytest.mark.ae
@pytest.mark.batch3
@allure.feature("OK")
@allure.story("Top Cities - UI验证")
@allure.title("TC029 - Top Cities显示常用热门城市")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证定位面板的Top Cities部分能够正确显示热门城市列表，且城市标签可点击")
def test_top_cities_should_display_popular_cities(page: Page, config: dict):
    """TC029: Top Cities显示常用热门城市"""
    
    # ========== Arrange：准备测试数据和对象 ==========
    location_panel_page = LocationPanelPage(page)
    
    base_url = config['base_url']
    
    logger.info("="*80)
    logger.info("TC029 - Top Cities显示常用热门城市")
    logger.info("="*80)
    logger.info(f"站点: {config['site_name']}")
    logger.info("="*80)
    
    # ========== Act 阶段：执行操作 ==========
    with allure.step("步骤1：打开Abu Dhabi城市页面"):
        page.goto(f"{base_url}/en/city-abu-dhabi/")
        logger.info("✓ 打开Abu Dhabi页面")
        page.wait_for_load_state("load", timeout=30000)
    
    with allure.step("步骤2：点击定位图标打开面板"):
        location_panel_page.click_location_icon()
        assert location_panel_page.is_location_panel_open(), "定位面板未打开"
        logger.info("✓ 定位面板已打开")
    
    # ========== Assert 阶段：验证结果 ==========
    with allure.step("验证1：Top Cities标题显示"):
        top_cities_section = page.locator("[role='tooltip'] >> text='Top Cities'")
        assert top_cities_section.is_visible(timeout=5000), "Top Cities标题未显示"
        logger.info("✓ Top Cities标题显示")
    
    with allure.step("验证2：Dubai显示在Top Cities中"):
        top_cities_section = page.locator("[role='tooltip']").locator("text='Top Cities'").locator("..")
        dubai_tag = top_cities_section.locator("[class*='QuickCities_tagText']").filter(has_text="Dubai")
        assert dubai_tag.is_visible(timeout=5000), "Dubai未显示在Top Cities中"
        logger.info("✓ Dubai显示在Top Cities中")
    
    with allure.step("验证3：Abu Dhabi显示在Top Cities中"):
        abu_dhabi_tag = top_cities_section.locator("[class*='QuickCities_tagText']").filter(has_text="Abu Dhabi")
        assert abu_dhabi_tag.is_visible(timeout=5000), "Abu Dhabi未显示在Top Cities中"
        logger.info("✓ Abu Dhabi显示在Top Cities中")
    
    with allure.step("验证4：Top Cities标签可点击"):
        dubai_tag_clickable = dubai_tag.is_enabled()
        assert dubai_tag_clickable, "Dubai标签不可点击"
        logger.info("✓ Top Cities标签可点击")
    
    logger.info("="*80)
    logger.info("✅ TC029 测试通过")
    logger.info("="*80)


@pytest.mark.case_id_tc030
@pytest.mark.p1
@pytest.mark.positive
@pytest.mark.location_panel
@pytest.mark.ae
@pytest.mark.batch3
@allure.feature("OK")
@allure.story("Top Cities - 城市切换 - 正向场景")
@allure.title("TC030 - 从Top Cities选择Abu Dhabi应成功切换")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证用户从Top Cities部分选择Abu Dhabi后，页面能够成功切换到Abu Dhabi，且定位面板自动关闭")
def test_select_abu_dhabi_from_top_cities_should_switch(page: Page, config: dict):
    """TC030: 从Top Cities选择Abu Dhabi应成功切换"""
    
    # ========== Arrange：准备测试数据和对象 ==========
    location_panel_page = LocationPanelPage(page)
    
    base_url = config['base_url']
    target_city = "Abu Dhabi"
    
    logger.info("="*80)
    logger.info("TC030 - 从Top Cities选择Abu Dhabi应成功切换")
    logger.info("="*80)
    logger.info(f"站点: {config['site_name']}")
    logger.info("当前位置: Dubai")
    logger.info(f"目标城市: {target_city}")
    logger.info("="*80)
    
    # ========== Act 阶段：执行操作 ==========
    with allure.step("步骤1：打开Dubai城市页面（当前位置）"):
        page.goto(f"{base_url}/en/city-dubai/")
        logger.info("✓ 打开Dubai页面（当前位置）")
        page.wait_for_load_state("load", timeout=30000)
    
    with allure.step("步骤2：点击定位图标打开面板"):
        location_panel_page.click_location_icon()
        assert location_panel_page.is_location_panel_open(), "定位面板未打开"
        logger.info("✓ 定位面板已打开")
    
    with allure.step(f"步骤3：从Top Cities选择 {target_city}"):
        location_panel_page.select_city_from_top_cities(target_city)
        page.wait_for_timeout(2000)
        logger.info(f"✓ 已点击Top Cities中的 {target_city}")
    
    # ========== Assert 阶段：验证结果 ==========
    with allure.step("验证1：URL已切换到Abu Dhabi"):
        current_city = location_panel_page.get_current_city_from_url()
        assert current_city == "abu-dhabi", f"URL未切换到abu-dhabi，当前: {current_city}"
        logger.info(f"✓ URL已切换到: {current_city}")
    
    with allure.step("验证2：页面标题包含Abu Dhabi"):
        assert location_panel_page.verify_page_title_contains(target_city), f"页面标题不包含{target_city}"
        logger.info(f"✓ 页面标题包含 {target_city}")
    
    with allure.step("验证3：定位面板已自动关闭"):
        assert location_panel_page.is_location_panel_closed(), "定位面板未关闭"
        logger.info("✓ 定位面板已自动关闭")
    
    logger.info("="*80)
    logger.info("✅ TC030 测试通过")
    logger.info("="*80)
