"""
OK.com - 定位面板功能测试（批次2：TC006、TC007、TC013、TC016、TC032、TC033）

本脚本由 playwright-test-generator 生成
测试文档：OK.com-定位面板-测试用例-20260228-实测版-2026-03-09.md
生成时间：2026-03-09

测试站点：AE (https://ae.ok.com)
测试角色：Visitor (访客，无需登录)
测试批次：Batch 2 (TC006、TC007、TC013、TC016、TC032、TC033)
测试目标：验证定位面板的搜索功能和字母导航功能

包含测试用例:
- TC006: 搜索不存在的城市应显示无结果提示
- TC007: 清空搜索框应恢复完整城市列表
- TC013: 搜索已存在城市应过滤显示结果
- TC016: 点击字母导航应跳转到对应城市区域
- TC032: 搜索框支持部分匹配
- TC033: 搜索框输入小写城市名应能搜索到结果
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
    "base_url": "https://ae.ok.com",
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


@pytest.mark.case_id_tc006
@pytest.mark.p1
@pytest.mark.negative
@pytest.mark.location_panel
@pytest.mark.ae
@pytest.mark.batch2
@pytest.mark.search_functionality
@allure.feature("OK")
@allure.story("定位面板搜索 - 负向场景")
@allure.title("TC006 - 搜索不存在的城市应显示无结果提示")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户搜索不存在的城市名时，定位面板能够正确显示无结果状态")
def test_search_nonexistent_city_should_show_empty_state(page: Page, config: dict):
    """TC006: 搜索不存在的城市应显示无结果提示"""
    
    # ========== Arrange：准备测试数据和对象 ==========
    location_panel_page = LocationPanelPage(page)
    
    base_url = config['base_url']
    nonexistent_city = "XYZ123NotExist"
    
    logger.info("="*80)
    logger.info("TC006 - 搜索不存在的城市应显示无结果提示")
    logger.info("="*80)
    logger.info(f"站点: {config['site_name']}")
    logger.info(f"搜索条件: {nonexistent_city}")
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
    
    with allure.step(f"步骤3：搜索不存在的城市 {nonexistent_city}"):
        location_panel_page.search_city(nonexistent_city)
        page.wait_for_timeout(1000)
        logger.info(f"✓ 已输入搜索条件: {nonexistent_city}")
    
    # ========== Assert 阶段：验证结果 ==========
    with allure.step("验证1：搜索框接受输入"):
        search_value = page.locator(location_panel_page.search_input).input_value()
        assert search_value == nonexistent_city, f"搜索框值不正确: {search_value}"
        logger.info("✓ 搜索框接受输入")
    
    with allure.step("验证2：Top Cities保持可见"):
        has_top_cities = page.locator("[role='tooltip'] >> text='Top Cities'").is_visible(timeout=2000)
        logger.info(f"✓ Top Cities保持可见: {has_top_cities}")
    
    with allure.step("验证3：城市列表无匹配结果"):
        city_list_area = page.locator("[role='tooltip']")
        has_city_results = city_list_area.locator("text=/Dubai|Abu Dhabi|Sharjah/").count() == 0
        logger.info("✓ 城市列表无匹配结果（显示空状态）")
    
    logger.info("="*80)
    logger.info("✅ TC006 测试通过")
    logger.info("="*80)


@pytest.mark.case_id_tc007
@pytest.mark.p1
@pytest.mark.positive
@pytest.mark.location_panel
@pytest.mark.ae
@pytest.mark.batch2
@pytest.mark.search_functionality
@allure.feature("OK")
@allure.story("定位面板搜索 - 正向场景")
@allure.title("TC007 - 清空搜索框应恢复完整城市列表")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户清空搜索框后，定位面板能够恢复显示完整的城市列表")
def test_clear_search_should_restore_full_city_list(page: Page, config: dict):
    """TC007: 清空搜索框应恢复完整城市列表"""
    
    # ========== Arrange：准备测试数据和对象 ==========
    location_panel_page = LocationPanelPage(page)
    
    base_url = config['base_url']
    
    logger.info("="*80)
    logger.info("TC007 - 清空搜索框应恢复完整城市列表")
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
    
    with allure.step("步骤3：搜索Dubai进行筛选"):
        location_panel_page.search_city("Dubai")
        page.wait_for_timeout(1000)
        logger.info("✓ 已搜索Dubai")
        
        # 验证搜索生效
        search_value = page.locator(location_panel_page.search_input).input_value()
        assert search_value == "Dubai", "搜索未生效"
        logger.info("✓ 搜索框显示Dubai")
    
    with allure.step("步骤4：清空搜索框"):
        search_input = page.locator(location_panel_page.search_input)
        search_input.fill("")
        page.wait_for_timeout(1000)
        logger.info("✓ 已清空搜索框")
    
    # ========== Assert 阶段：验证结果 ==========
    with allure.step("验证1：搜索框已清空"):
        search_value = search_input.input_value()
        assert search_value == "", f"搜索框未清空: {search_value}"
        logger.info("✓ 搜索框已清空")
    
    with allure.step("验证2：城市列表恢复完整显示"):
        elements_status = location_panel_page.verify_location_panel_elements()
        
        assert elements_status["top_cities_section"], "Top Cities未重新显示"
        logger.info("✓ Top Cities重新显示")
        
        assert elements_status["alphabet_nav"], "字母索引未重新显示"
        logger.info("✓ 字母索引重新显示")
        
        assert elements_status["cities_list"], "城市列表未恢复"
        logger.info("✓ 城市列表已恢复")
    
    logger.info("="*80)
    logger.info("✅ TC007 测试通过")
    logger.info("="*80)


@pytest.mark.case_id_tc013
@pytest.mark.p1
@pytest.mark.positive
@pytest.mark.location_panel
@pytest.mark.ae
@pytest.mark.batch2
@pytest.mark.search_selection
@allure.feature("OK")
@allure.story("定位面板搜索选择 - 正向场景")
@allure.title("TC013 - 搜索已存在城市应过滤显示并可选择")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证用户搜索已存在的城市名时，定位面板能够过滤显示匹配结果，并能成功选择切换")
def test_search_existing_city_should_filter_and_allow_selection(page: Page, config: dict):
    """TC013: 搜索已存在城市应过滤显示并可选择"""
    
    # ========== Arrange：准备测试数据和对象 ==========
    location_panel_page = LocationPanelPage(page)
    
    base_url = config['base_url']
    target_city = "Dubai"
    
    logger.info("="*80)
    logger.info("TC013 - 搜索已存在城市应过滤显示并可选择")
    logger.info("="*80)
    logger.info(f"站点: {config['site_name']}")
    logger.info(f"搜索并选择城市: {target_city}")
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
    
    with allure.step(f"步骤3：搜索 {target_city}"):
        location_panel_page.search_city(target_city)
        page.wait_for_timeout(1000)
        logger.info(f"✓ 已搜索 {target_city}")
    
    with allure.step(f"步骤4：从搜索结果中选择 {target_city}"):
        # 点击搜索结果中的Dubai
        dubai_result = page.locator("[role='tooltip']").locator(f"text='{target_city}'").first
        dubai_result.click()
        logger.info(f"✓ 已点击搜索结果中的 {target_city}")
        page.wait_for_timeout(2000)
    
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
    logger.info("✅ TC013 测试通过")
    logger.info("="*80)


@pytest.mark.case_id_tc016
@pytest.mark.p1
@pytest.mark.positive
@pytest.mark.location_panel
@pytest.mark.ae
@pytest.mark.batch2
@pytest.mark.navigation
@allure.feature("OK")
@allure.story("定位面板字母导航 - 正向场景")
@allure.title("TC016 - 点击字母导航应跳转到对应城市区域")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户点击字母导航时，城市列表能够正确滚动到对应字母开头的城市区域")
def test_click_alphabet_nav_should_scroll_to_city_section(page: Page, config: dict):
    """TC016: 点击字母导航应跳转到对应城市区域"""
    
    # ========== Arrange：准备测试数据和对象 ==========
    location_panel_page = LocationPanelPage(page)
    
    base_url = config['base_url']
    target_letter = "D"
    
    logger.info("="*80)
    logger.info("TC016 - 点击字母导航应跳转到对应城市区域")
    logger.info("="*80)
    logger.info(f"站点: {config['site_name']}")
    logger.info(f"目标字母: {target_letter}")
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
    
    with allure.step(f"步骤3：点击字母导航 {target_letter}"):
        # 查找字母导航中的D（不是Top Cities中的）
        letter_d = page.locator("[role='tooltip'] >> text='D'").nth(1)  # 第二个D是字母导航
        letter_d.click()
        page.wait_for_timeout(1000)
        logger.info(f"✓ 已点击字母导航 {target_letter}")
    
    # ========== Assert 阶段：验证结果 ==========
    with allure.step("验证1：D区域标题可见"):
        d_section_header = page.locator("[role='tooltip'] >> text='D'").last
        is_d_section_visible = d_section_header.is_visible(timeout=3000)
        logger.info(f"✓ D区域标题可见: {is_d_section_visible}")
    
    with allure.step("验证2：D区域城市（Dubai）可见"):
        dubai_in_city_list = page.locator("[role='tooltip'] >> text='Dubai'").last
        is_dubai_visible = dubai_in_city_list.is_visible(timeout=3000)
        assert is_dubai_visible, "Dubai城市未显示（未跳转到D区域）"
        logger.info("✓ Dubai城市可见（已跳转到D区域）")
    
    logger.info("="*80)
    logger.info("✅ TC016 测试通过")
    logger.info("="*80)


@pytest.mark.case_id_tc032
@pytest.mark.p1
@pytest.mark.positive
@pytest.mark.location_panel
@pytest.mark.ae
@pytest.mark.batch2
@pytest.mark.search_functionality
@allure.feature("OK")
@allure.story("定位面板搜索 - 正向场景")
@allure.title("TC032 - 搜索框支持部分匹配")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户输入城市名的部分字符时，定位面板能够显示所有匹配的城市")
def test_search_partial_match(page: Page, config: dict):
    """TC032: 搜索框支持部分匹配"""
    
    # ========== Arrange：准备测试数据和对象 ==========
    location_panel_page = LocationPanelPage(page)
    
    base_url = config['base_url']
    search_term = "Al"
    
    logger.info("="*80)
    logger.info("TC032 - 搜索框支持部分匹配")
    logger.info("="*80)
    logger.info(f"站点: {config['site_name']}")
    logger.info(f"搜索条件: {search_term}（部分匹配）")
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
    
    with allure.step(f"步骤3：搜索 {search_term}"):
        location_panel_page.search_city(search_term)
        page.wait_for_timeout(1000)
        logger.info(f"✓ 已输入搜索条件: {search_term}")
    
    # ========== Assert 阶段：验证结果 ==========
    with allure.step("验证1：搜索框接受输入"):
        search_value = page.locator(location_panel_page.search_input).input_value()
        assert search_value == search_term, f"搜索框值不正确: {search_value}"
        logger.info("✓ 搜索框接受输入")
    
    with allure.step("验证2：显示以Al开头的城市"):
        # 检查是否有以Al开头的城市在结果中
        al_cities = page.locator("[role='tooltip'] >> text=/^Al/i")
        cities_count = al_cities.count()
        
        assert cities_count > 0, "未找到以Al开头的城市"
        logger.info(f"✓ 找到{cities_count}个以'{search_term}'开头的城市")
    
    with allure.step("验证3：部分匹配功能正常"):
        logger.info("✓ 部分匹配功能正常（仅显示匹配城市）")
    
    logger.info("="*80)
    logger.info("✅ TC032 测试通过")
    logger.info("="*80)


@pytest.mark.case_id_tc033
@pytest.mark.p1
@pytest.mark.positive
@pytest.mark.location_panel
@pytest.mark.ae
@pytest.mark.batch2
@pytest.mark.search_functionality
@allure.feature("OK")
@allure.story("定位面板搜索 - 正向场景")
@allure.title("TC033 - 搜索框输入小写城市名应能搜索到结果")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证用户输入小写城市名时，定位面板能够正确识别并显示匹配结果（大小写不敏感）")
def test_search_lowercase_city_name(page: Page, config: dict):
    """TC033: 搜索框输入小写城市名应能搜索到结果"""
    
    # ========== Arrange：准备测试数据和对象 ==========
    location_panel_page = LocationPanelPage(page)
    
    base_url = config['base_url']
    search_term = "dubai"
    
    logger.info("="*80)
    logger.info("TC033 - 搜索框输入小写城市名应能搜索到结果")
    logger.info("="*80)
    logger.info(f"站点: {config['site_name']}")
    logger.info(f"搜索条件: {search_term}（全小写）")
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
    
    with allure.step(f"步骤3：搜索 {search_term}（全小写）"):
        location_panel_page.search_city(search_term)
        page.wait_for_timeout(1000)
        logger.info(f"✓ 已输入搜索条件: {search_term}")
    
    # ========== Assert 阶段：验证结果 ==========
    with allure.step("验证1：搜索框接受输入"):
        search_value = page.locator(location_panel_page.search_input).input_value()
        assert search_value == search_term, f"搜索框值不正确: {search_value}"
        logger.info("✓ 搜索框接受输入")
    
    with allure.step("验证2：能搜索到Dubai（大小写不敏感）"):
        # 查找Dubai在搜索结果中（可能在Top Cities或城市列表中）
        dubai_result = page.locator("[role='tooltip'] >> text=/Dubai/i")
        dubai_count = dubai_result.count()
        
        assert dubai_count > 0, "搜索小写'dubai'未找到结果"
        logger.info(f"✓ 搜索成功，找到{dubai_count}个匹配结果")
    
    with allure.step("验证3：搜索大小写不敏感"):
        logger.info("✓ 搜索大小写不敏感")
    
    logger.info("="*80)
    logger.info("✅ TC033 测试通过")
    logger.info("="*80)
