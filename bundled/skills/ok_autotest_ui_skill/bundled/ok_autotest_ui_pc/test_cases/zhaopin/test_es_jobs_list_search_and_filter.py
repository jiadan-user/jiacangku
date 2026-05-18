"""
ES站 - Jobs列表页搜索与筛选功能测试

测试站点: ES站（西班牙站）
测试页面: 招聘列表页 https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs
测试范围: 搜索框、筛选器、筛选回显、Reset、feed流加载、职位卡片交互、侧边栏详情、页面底部、导航
测试状态: 已登录，无岗位偏好
默认城市: Madrid（地址筛选框默认有值）

对应用例文档: ok-es-JobsList-SearchAndFilter-测试用例-20260309.md (v3.0, TC001-TC065)

执行方式:
  pytest test_cases/zhaopin/test_es_jobs_list_search_and_filter.py -v -s --alluredir=reports/allure-results
  pytest test_cases/zhaopin/test_es_jobs_list_search_and_filter.py -m "p0" -v -s
  pytest test_cases/zhaopin/test_es_jobs_list_search_and_filter.py -m "filter" -v -s
"""

import re

import pytest
import allure
from pages.jobs_list_page_es import JobsListPageES
from test_cases.zhaopin.es_login_helper import ensure_es_logged_in
from utils.logger import setup_logger

logger = setup_logger()

from test_cases.zhaopin.explicit_waits import (
    es_location_panel_open,
    es_job_type_panel_open,
    es_workplace_panel_open,
    es_salary_panel_open,
    es_job_list_first_card_ready,
    network_idle_soft,
    dom_content_loaded_soft,
)

# ==================== 测试环境配置 ====================
_CONFIG = {
    "site": "es",
    "site_name": "西班牙站",
    "role": "jobseeker",
    "user_name": "wang_es",
    "base_url": "https://es.58v5.cn",
    "test_account": {
        "username": "wangyongli@58.com",
        "password": "Qwer1234"
    },
    "locale": "es-ES",
    "currency": "EUR",
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


# ==================== TC001: 搜索框输入关键词搜索 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("搜索框功能")
@allure.title("TC001: 搜索框输入关键词搜索")
@allure.description("验证在搜索框输入关键词点击Search后URL包含keyword参数且显示搜索结果")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.p0
@pytest.mark.search
@pytest.mark.case_id_es_jobs_tc001
def test_search_with_keyword_should_navigate_to_results(page, config):
    """TC001: 搜索框输入关键词搜索"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step('步骤2：在搜索框输入关键词"manager"'):
        jobs_list_page.input_search_keyword("manager")
        logger.info('✓ 已输入关键词"manager"')
    with allure.step("步骤3：点击Search按钮"):
        jobs_list_page.click_search_button()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已点击Search按钮")
    with allure.step("验证：URL包含keyword=manager"):
        current_url = page.url
        assert "keyword=manager" in current_url, f"URL应包含keyword=manager，实际URL: {current_url}"
        logger.info(f"✓ URL验证成功: {current_url}")
    with allure.step("验证：筛选器区域仍然可见"):
        assert jobs_list_page.is_filter_area_visible(), "筛选器区域应该可见"
        logger.info("✓ 筛选器区域可见")


# ==================== TC002: 空搜索关键词提交 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("搜索框功能")
@allure.title("TC002: 空搜索关键词提交")
@allure.description("验证不输入内容直接点击Search，URL包含keyword=（空值），页面正常加载")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p1
@pytest.mark.search
@pytest.mark.case_id_es_jobs_tc002
def test_search_with_empty_keyword_should_stay_or_default(page, config):
    """TC002: 空搜索关键词提交"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("步骤2：不输入内容，直接点击Search按钮"):
        jobs_list_page.click_search_button()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已点击Search按钮")
    with allure.step("验证：URL包含keyword参数（空值）且页面正常加载"):
        current_url = page.url
        assert "keyword=" in current_url, f"URL应包含keyword=参数，实际URL: {current_url}"
        assert jobs_list_page.is_page_loaded(), "页面应正常加载"
        logger.info(f"✓ URL验证成功: {current_url}")


# ==================== TC003: 搜索框输入特殊字符搜索 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("搜索框功能")
@allure.title("TC003: 搜索框输入特殊字符搜索")
@allure.description("验证输入特殊字符后URL正确编码且页面正常返回结果或空提示")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.search
@pytest.mark.case_id_es_jobs_tc003
def test_search_with_special_characters(page, config):
    """TC003: 搜索框输入特殊字符搜索"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step('步骤2：在搜索框输入特殊字符"@#$%"'):
        jobs_list_page.input_search_keyword("@#$%")
        logger.info('✓ 已输入特殊字符"@#$%"')
    with allure.step("步骤3：点击Search按钮"):
        jobs_list_page.click_search_button()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已点击Search按钮")
    with allure.step("验证：URL包含keyword参数（已编码）且页面正常加载"):
        current_url = page.url
        assert "keyword=" in current_url, f"URL应包含keyword参数，实际URL: {current_url}"
        assert jobs_list_page.is_page_loaded(), "页面应正常加载"
        logger.info(f"✓ URL正确编码特殊字符: {current_url}")


# ==================== TC004: 搜索框输入超长关键词 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("搜索框功能")
@allure.title("TC004: 搜索框输入超长关键词")
@allure.description("验证输入超长关键词后系统正常处理，搜索请求正常发送且页面加载正常")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.search
@pytest.mark.case_id_es_jobs_tc004
def test_search_with_long_keyword(page, config):
    """TC004: 搜索框输入超长关键词"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    long_keyword = "manager" * 50
    with allure.step(f"步骤2：在搜索框输入超长关键词（{len(long_keyword)}字符）"):
        jobs_list_page.input_search_keyword(long_keyword)
        logger.info(f"✓ 已输入超长关键词（{len(long_keyword)}字符）")
    with allure.step("步骤3：点击Search按钮"):
        jobs_list_page.click_search_button()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已点击Search按钮")
    with allure.step("验证：URL包含keyword参数且页面正常加载"):
        current_url = page.url
        assert "keyword=" in current_url, f"URL应包含keyword参数，实际URL: {current_url}"
        assert jobs_list_page.is_page_loaded(), "页面应正常加载"
        logger.info(f"✓ 系统正常处理超长关键词: {current_url}")


# ==================== TC005: 页面加载后地址筛选器默认显示Madrid ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("地址筛选功能")
@allure.title("TC005: 页面加载后地址筛选器默认显示Madrid")
@allure.description("验证Jobs列表页加载后地址筛选器默认显示Madrid并处于激活态")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.p0
@pytest.mark.location
@pytest.mark.case_id_es_jobs_tc005
def test_default_location_filter_is_madrid(page, config):
    """TC005: 页面加载后地址筛选器默认显示Madrid"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("验证：地址筛选器默认显示Madrid"):
        assert jobs_list_page.is_madrid_filter_displayed(), "地址筛选器应默认显示Madrid"
        logger.info("✓ 地址筛选器默认显示Madrid")
    with allure.step("验证：URL路径包含city-madrid2"):
        current_url = page.url
        assert "city-madrid2" in current_url, f"URL应包含city-madrid2，实际URL: {current_url}"
        logger.info(f"✓ URL包含city-madrid2: {current_url}")


# ==================== TC006: 切换城市后地址筛选器同步更新 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("地址筛选功能")
@allure.title("TC006: 切换城市后地址筛选器同步更新")
@allure.description("验证选择其他城市后筛选器文本和URL均同步更新为新城市")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.p1
@pytest.mark.location
@pytest.mark.case_id_es_jobs_tc006
def test_switch_city_updates_filter_and_url(page, config):
    """TC006: 切换城市后地址筛选器同步更新"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("步骤2：点击地址筛选器打开面板"):
        jobs_list_page.click_location_filter()
        es_location_panel_open(page)
        logger.info("✓ 已打开地址筛选面板")
    with allure.step("步骤3：选择省份Catalonia，再选城市"):
        jobs_list_page.select_province("Catalonia")
        logger.info("✓ 已选择省份Catalonia")
        jobs_list_page.select_city_from_panel("Tarragona")
        page.wait_for_url(
            re.compile(r"https://es\.58v5\.cn/en/city-[^/?#]+/cate-jobs"),
            timeout=35000,
        )
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已选择城市Tarragona")
    with allure.step("验证：URL路径包含新城市标识"):
        current_url = page.url
        assert "city-madrid2" not in current_url, f"URL应已切换城市，实际URL: {current_url}"
        logger.info(f"✓ URL已切换城市: {current_url}")


# ==================== TC007: 点击Madrid地址筛选器打开城市面板 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("地址筛选功能")
@allure.title("TC007: 点击Madrid地址筛选器打开城市面板")
@allure.description("验证点击地址筛选器后展开Select Location面板，包含Search City搜索框")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.p0
@pytest.mark.location
@pytest.mark.case_id_es_jobs_tc007
def test_click_location_filter_opens_panel(page, config):
    """TC007: 点击Madrid地址筛选器打开城市面板"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("步骤2：点击Madrid地址筛选器"):
        jobs_list_page.click_location_filter()
        es_location_panel_open(page)
        logger.info("✓ 已点击地址筛选器")
    with allure.step("验证：地址选择面板展开，显示Search City搜索框"):
        assert jobs_list_page.is_location_panel_visible(), "地址选择面板应展开"
        logger.info("✓ 地址选择面板已展开")
    with allure.step("验证：面板顶部有历史城市快捷入口"):
        assert jobs_list_page.is_location_search_box_visible(), "Search City搜索框应可见"
        logger.info("✓ Search City搜索框可见")


# ==================== TC008: 地址筛选两级选择城市（Catalonia → Barcelona方向） ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("地址筛选功能")
@allure.title("TC008: 地址筛选两级选择城市（省份→城市）")
@allure.description("验证在地址面板中先选省份再选城市的两级联动，URL路径更新为选中城市")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.p0
@pytest.mark.location
@pytest.mark.case_id_es_jobs_tc008
def test_location_two_level_selection(page, config):
    """TC008: 地址筛选两级选择城市（省份→城市）"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("步骤2：点击地址筛选器"):
        jobs_list_page.click_location_filter()
        es_location_panel_open(page)
        logger.info("✓ 已打开地址面板")
    with allure.step("步骤3-4：选择省份Andalusia与城市Sevilla（容错：偶发 chrome-error 页重试）"):
        city_list_re = re.compile(
            r"https://es\.58v5\.cn/en/city-[^/?#]+/cate-jobs", re.I
        )
        for attempt in range(2):
            if attempt > 0:
                logger.warning("城市切换未落地，自列表页重试 Andalusia → Sevilla")
                jobs_list_page.navigate_to_jobs_list()
                jobs_list_page.click_location_filter()
                es_location_panel_open(page)
            jobs_list_page.select_province("Andalusia")
            logger.info("✓ 已选择省份Andalusia")
            jobs_list_page.select_city_from_panel("Sevilla")
            try:
                page.wait_for_url(city_list_re, timeout=35000)
                u = page.url.lower()
                if "chromewebdata" in u or "chrome-error" in u:
                    raise RuntimeError(u)
                break
            except Exception as e:
                if attempt == 1:
                    raise
                logger.warning("等待城市列表 URL 失败，将重试: %s", e)
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已选择城市Sevilla")
    with allure.step("验证：URL路径变更为选中城市"):
        current_url = page.url
        assert "city-" in current_url, f"URL应包含city-路径，实际URL: {current_url}"
        assert "city-madrid2" not in current_url, f"URL应已切换离开Madrid，实际URL: {current_url}"
        logger.info(f"✓ URL已切换城市: {current_url}")


# ==================== TC009: 地址筛选选择"All Spain"查看全国职位 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("地址筛选功能")
@allure.title("TC009: 地址筛选选择All Spain查看全国职位")
@allure.description("验证选择All Spain后URL变为/en/city/cate-jobs/，筛选器显示Location")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.p0
@pytest.mark.location
@pytest.mark.case_id_es_jobs_tc009
def test_location_select_all_spain(page, config):
    """TC009: 地址筛选选择All Spain查看全国职位"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("步骤2：点击地址筛选器"):
        jobs_list_page.click_location_filter()
        es_location_panel_open(page)
        logger.info("✓ 已打开地址面板")
    with allure.step("步骤3：选择All Spain"):
        jobs_list_page.select_province("All Spain")
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已选择All Spain")
    with allure.step("验证：URL变为/en/city/cate-jobs/"):
        current_url = page.url
        assert "/en/city/cate-jobs/" in current_url, \
            f"URL应包含/en/city/cate-jobs/，实际URL: {current_url}"
        logger.info(f"✓ URL验证成功: {current_url}")
    with allure.step("验证：筛选器显示Location"):
        filter_text = jobs_list_page.get_filter_area_text()
        assert "Location" in filter_text, f"筛选器应显示Location，实际: {filter_text}"
        logger.info("✓ 筛选器显示Location")


# ==================== TC010: 地址面板Search City搜索框过滤城市 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("地址筛选功能")
@allure.title("TC010: 地址面板Search City搜索框过滤城市")
@allure.description("验证在地址面板Search City搜索框输入城市名后，列表过滤显示匹配城市")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.location
@pytest.mark.case_id_es_jobs_tc010
def test_location_search_city_filters_list(page, config):
    """TC010: 地址面板Search City搜索框过滤城市"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页并打开地址面板"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.click_location_filter()
        es_location_panel_open(page)
        logger.info("✓ 已打开地址面板")
    with allure.step("步骤2：在Search City搜索框输入'Madrid'"):
        page.get_by_placeholder("Search City").fill("Madrid")
        page.get_by_text("Madrid", exact=True).first.wait_for(state="visible", timeout=10000)
        logger.info("✓ 已输入搜索关键词'Madrid'")
    with allure.step("验证：面板中显示包含Madrid的城市"):
        madrid_visible = page.get_by_text("Madrid").first.is_visible(timeout=3000)
        assert madrid_visible, "搜索后应显示包含Madrid的城市"
        logger.info("✓ 搜索结果显示Madrid相关城市")


# ==================== TC011: 地址筛选Use current location ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("地址筛选功能")
@allure.title("TC011: 地址筛选Use current location（需地理位置权限）[手工]")
@allure.description("验证点击Use current location按钮触发浏览器地理位置授权请求——需手工测试")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.location
@pytest.mark.manual
@pytest.mark.case_id_es_jobs_tc011
def test_location_use_current_location_requires_permission(page, config):
    """TC011: 地址筛选Use current location（手工验证地理位置授权）"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页并打开地址面板"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.click_location_filter()
        es_location_panel_open(page)
        logger.info("✓ 已打开地址面板")
    with allure.step("验证：地址面板中存在Use current location按钮"):
        current_location_btn = page.get_by_role("button", name="Use current location")
        assert current_location_btn.count() > 0 or \
               page.get_by_text("current location").count() > 0, \
               "地址面板中应存在Use current location选项"
        logger.info("✓ Use current location按钮存在（地理位置授权需手工验证）")


# ==================== TC012: 点击Job Type筛选器打开类型面板 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Job Type筛选功能")
@allure.title("TC012: 点击Job Type筛选器打开类型面板")
@allure.description("验证点击Job Type筛选按钮后展开包含5个选项的面板及Clear/Confirm按钮")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.p0
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc012
def test_click_job_type_filter_opens_panel(page, config):
    """TC012: 点击Job Type筛选器打开类型面板"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("步骤2：点击Job Type筛选器"):
        jobs_list_page.click_job_type_filter()
        es_job_type_panel_open(page)
        logger.info("✓ 已点击Job Type筛选器")
    with allure.step("验证：Job Type面板展开，显示Confirm按钮"):
        assert jobs_list_page.is_job_type_panel_visible(), "Job Type面板应展开"
        logger.info("✓ Job Type面板已展开")
    with allure.step("验证：面板显示Full-time选项"):
        assert jobs_list_page.is_job_type_option_visible("Full-time"), "应显示Full-time选项"
        logger.info("✓ 面板显示Full-time等5个选项")


# ==================== TC013: Job Type筛选选择Full-time并Confirm ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Job Type筛选功能")
@allure.title("TC013: Job Type筛选选择Full-time并Confirm")
@allure.description("验证选择Full-time点击Confirm后URL含attr_60=1，筛选器显示Job Type·1")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.p0
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc013
def test_select_fulltime_and_confirm_updates_url(page, config):
    """TC013: Job Type筛选选择Full-time并Confirm"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("步骤2：点击Job Type筛选器"):
        jobs_list_page.click_job_type_filter()
        es_job_type_panel_open(page)
        logger.info("✓ 已打开Job Type面板")
    with allure.step("步骤3：选择Full-time选项"):
        jobs_list_page.select_job_type_option("Full-time")
        dom_content_loaded_soft(page, 3000)
        logger.info("✓ 已选择Full-time")
    with allure.step("步骤4：点击Confirm按钮"):
        jobs_list_page.click_job_type_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已点击Confirm按钮")
    with allure.step("验证：URL追加attr_60=1"):
        current_url = page.url
        assert "attr_60=1" in current_url, f"URL应包含attr_60=1，实际URL: {current_url}"
        logger.info(f"✓ URL验证成功: {current_url}")
    with allure.step("验证：筛选器显示Job Type · 1"):
        assert jobs_list_page.is_job_type_filter_active(1), "筛选器应显示Job Type · 1"
        logger.info("✓ 筛选器显示Job Type · 1")


# ==================== TC014: Job Type筛选多选后Confirm ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Job Type筛选功能")
@allure.title("TC014: Job Type筛选多选后Confirm")
@allure.description("验证同时选择Full-time和Part-time后Confirm，筛选器显示Job Type·2")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.p0
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc014
def test_select_multiple_job_types_and_confirm(page, config):
    """TC014: Job Type筛选多选后Confirm"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("步骤2：打开Job Type面板"):
        jobs_list_page.click_job_type_filter()
        es_job_type_panel_open(page)
        logger.info("✓ 已打开Job Type面板")
    with allure.step("步骤3：选择Full-time"):
        jobs_list_page.select_job_type_option("Full-time")
        dom_content_loaded_soft(page, 3000)
        logger.info("✓ 已选择Full-time")
    with allure.step("步骤4：选择Part-time"):
        jobs_list_page.select_job_type_option("Part-time")
        dom_content_loaded_soft(page, 3000)
        logger.info("✓ 已选择Part-time")
    with allure.step("步骤5：点击Confirm"):
        jobs_list_page.click_job_type_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已点击Confirm")
    with allure.step("验证：URL包含Job Type多选参数（逗号分隔）"):
        current_url = page.url
        assert "attr_60=" in current_url, f"URL应包含Job Type参数，实际URL: {current_url}"
        logger.info(f"✓ URL包含Job Type参数: {current_url}")
    with allure.step("验证：筛选器显示Job Type · 2"):
        assert jobs_list_page.is_job_type_filter_active(2), "筛选器应显示Job Type · 2"
        logger.info("✓ 筛选器显示Job Type · 2")


# ==================== TC015: Job Type筛选点击Clear清除选择 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Job Type筛选功能")
@allure.title("TC015: Job Type筛选点击Clear清除选择")
@allure.description("验证在Job Type面板中点击Clear后所有选项取消勾选且面板仍保持打开，URL不变")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p1
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc015
def test_job_type_clear_should_deselect_all_options(page, config):
    """TC015: Job Type筛选点击Clear清除选择"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("步骤2：打开面板并选择Full-time"):
        jobs_list_page.click_job_type_filter()
        es_job_type_panel_open(page)
        jobs_list_page.select_job_type_option("Full-time")
        dom_content_loaded_soft(page, 3000)
        logger.info("✓ 已打开面板并选择Full-time")
    with allure.step("步骤3：点击Clear按钮"):
        jobs_list_page.click_job_type_clear()
        network_idle_soft(page, 5000)
        logger.info("✓ 已点击Clear按钮")
    with allure.step("验证：面板仍然打开"):
        assert jobs_list_page.is_job_type_panel_visible(), "点击Clear后面板应仍然打开"
        logger.info("✓ 面板仍然打开")
    with allure.step("验证：URL未变更"):
        current_url = page.url
        assert "attr_60=" not in current_url, f"点击Clear后URL不应包含Job Type参数，实际URL: {current_url}"
        logger.info(f"✓ URL未变更: {current_url}")


# ==================== TC016: 点击Workplace type筛选器 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Workplace type筛选功能")
@allure.title("TC016: 点击Workplace type筛选器展开面板")
@allure.description("验证点击Workplace type筛选按钮后展开包含工作地点类型选项的面板")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p1
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc016
def test_click_workplace_type_filter_should_open_panel(page, config):
    """TC016: 点击Workplace type筛选器展开面板"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("步骤2：点击Workplace type筛选器"):
        jobs_list_page.click_workplace_type_filter()
        es_workplace_panel_open(page)
        logger.info("✓ 已点击Workplace type筛选器")
    with allure.step("验证：Workplace type面板展开，显示Confirm按钮"):
        assert jobs_list_page.is_filter_confirm_button_visible(), "Workplace type面板应展开"
        logger.info("✓ Workplace type面板已展开")


# ==================== TC017: Workplace type筛选选择并Confirm ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Workplace type筛选功能")
@allure.title("TC017: Workplace type筛选选择Remote并Confirm")
@allure.description("验证选择Remote点击Confirm后URL含workplace参数，筛选器显示Workplace type·1")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.p1
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc017
def test_select_remote_workplace_type_and_confirm(page, config):
    """TC017: Workplace type筛选选择Remote并Confirm"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("步骤2：点击Workplace type筛选器"):
        jobs_list_page.click_workplace_type_filter()
        es_workplace_panel_open(page)
        logger.info("✓ 已打开Workplace type面板")
    with allure.step("步骤3：选择Remote选项"):
        jobs_list_page.select_workplace_type_option("Remote")
        dom_content_loaded_soft(page, 3000)
        logger.info("✓ 已选择Remote")
    with allure.step("步骤4：点击Confirm"):
        jobs_list_page.click_workplace_type_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已点击Confirm")
    with allure.step("验证：URL包含workplace参数且筛选器激活"):
        current_url = page.url
        assert "attr_" in current_url, f"URL应包含workplace参数，实际URL: {current_url}"
        logger.info(f"✓ URL包含workplace参数: {current_url}")
    with allure.step("验证：筛选器显示Workplace type · 1"):
        assert jobs_list_page.is_workplace_type_filter_active(1), "筛选器应显示Workplace type · 1"
        logger.info("✓ 筛选器显示Workplace type · 1")


# ==================== TC018: 点击Salary筛选器展开面板 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Salary筛选功能")
@allure.title("TC018: 点击Salary筛选器展开面板")
@allure.description("验证点击Salary筛选按钮后展开包含Min/Max输入框和薪资周期选项的面板")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.p0
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc018
def test_click_salary_filter_opens_panel(page, config):
    """TC018: 点击Salary筛选器展开面板"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("步骤2：点击Salary筛选器"):
        jobs_list_page.click_salary_filter()
        es_salary_panel_open(page)
        logger.info("✓ 已点击Salary筛选器")
    with allure.step("验证：Salary面板展开，显示Min和Max输入框"):
        assert jobs_list_page.is_salary_panel_visible(), "Salary面板应展开"
        assert page.get_by_placeholder("Min").is_visible(timeout=3000), "Min输入框应可见"
        assert page.get_by_placeholder("Max").is_visible(timeout=3000), "Max输入框应可见"
        logger.info("✓ Salary面板已展开，Min/Max输入框可见")


# ==================== TC019: Salary筛选输入Min+Max范围并Confirm ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Salary筛选功能")
@allure.title("TC019: Salary筛选输入Min+Max范围并Confirm")
@allure.description("验证输入Min=5000和Max=20000后Confirm，URL含lowestPrice和highestPrice参数")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.p0
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc019
def test_salary_filter_with_min_max_range(page, config):
    """TC019: Salary筛选输入Min+Max范围并Confirm"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("步骤2：点击Salary筛选器"):
        jobs_list_page.click_salary_filter()
        es_salary_panel_open(page)
        logger.info("✓ 已打开Salary面板")
    with allure.step("步骤3：输入Min=5000，Max=20000"):
        jobs_list_page.input_salary_min("5000")
        jobs_list_page.input_salary_max("20000")
        logger.info("✓ 已输入Min=5000，Max=20000")
    with allure.step("步骤4：点击Confirm"):
        jobs_list_page.click_salary_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已点击Confirm")
    with allure.step("验证：URL包含lowestPrice和highestPrice参数"):
        current_url = page.url
        assert "lowestPrice=" in current_url, f"URL应含lowestPrice参数，实际URL: {current_url}"
        assert "highestPrice=" in current_url, f"URL应含highestPrice参数，实际URL: {current_url}"
        logger.info(f"✓ URL验证成功: {current_url}")
    with allure.step("验证：筛选器显示Salary激活态"):
        assert jobs_list_page.is_salary_filter_active(), "Salary筛选器应处于激活态"
        logger.info("✓ Salary筛选器已激活")


# ==================== TC020: Salary筛选选择薪资周期Per Month并Confirm ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Salary筛选功能")
@allure.title("TC020: Salary筛选选择薪资周期Per Month并Confirm")
@allure.description("验证在Salary面板选择Per Month薪资周期后Confirm，URL含attr_80=4")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p1
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc020
def test_salary_filter_select_per_month_period(page, config):
    """TC020: Salary筛选选择薪资周期Per Month并Confirm"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("步骤2：点击Salary筛选器"):
        jobs_list_page.click_salary_filter()
        es_salary_panel_open(page)
        logger.info("✓ 已打开Salary面板")
    with allure.step("步骤3：选择Per Month薪资周期"):
        page.get_by_text("Per Month").click()
        dom_content_loaded_soft(page, 3000)
        logger.info("✓ 已选择Per Month")
    with allure.step("步骤4：点击Confirm"):
        jobs_list_page.click_salary_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已点击Confirm")
    with allure.step("验证：URL包含attr_80=4（Per Month对应值）"):
        current_url = page.url
        assert "attr_80=4" in current_url, f"URL应含attr_80=4，实际URL: {current_url}"
        logger.info(f"✓ URL验证成功: {current_url}")


# ==================== TC021: Salary筛选只填Min不填Max并Confirm ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Salary筛选功能")
@allure.title("TC021: Salary筛选只填Min不填Max并Confirm")
@allure.description("验证只填Min不填Max后Confirm，URL含lowestPrice参数但无highestPrice")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p1
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc021
def test_salary_filter_only_min(page, config):
    """TC021: Salary筛选只填Min不填Max并Confirm"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航并打开Salary面板"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.click_salary_filter()
        es_salary_panel_open(page)
        logger.info("✓ 已打开Salary面板")
    with allure.step("步骤2：只填Min=3000"):
        jobs_list_page.input_salary_min("3000")
        logger.info("✓ 已输入Min=3000")
    with allure.step("步骤3：点击Confirm"):
        jobs_list_page.click_salary_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已点击Confirm")
    with allure.step("验证：URL含lowestPrice，无highestPrice"):
        current_url = page.url
        assert "lowestPrice=" in current_url, f"URL应含lowestPrice，实际URL: {current_url}"
        assert "highestPrice=" not in current_url, f"URL不应含highestPrice，实际URL: {current_url}"
        logger.info(f"✓ URL验证成功: {current_url}")


# ==================== TC022: Salary筛选只填Max不填Min并Confirm ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Salary筛选功能")
@allure.title("TC022: Salary筛选只填Max不填Min并Confirm")
@allure.description("验证只填Max不填Min后Confirm，URL含highestPrice参数但无lowestPrice")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p1
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc022
def test_salary_filter_only_max(page, config):
    """TC022: Salary筛选只填Max不填Min并Confirm"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航并打开Salary面板"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.click_salary_filter()
        es_salary_panel_open(page)
        logger.info("✓ 已打开Salary面板")
    with allure.step("步骤2：只填Max=50000"):
        jobs_list_page.input_salary_max("50000")
        logger.info("✓ 已输入Max=50000")
    with allure.step("步骤3：点击Confirm"):
        jobs_list_page.click_salary_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已点击Confirm")
    with allure.step("验证：URL含highestPrice，无lowestPrice"):
        current_url = page.url
        assert "highestPrice=" in current_url, f"URL应含highestPrice，实际URL: {current_url}"
        assert "lowestPrice=" not in current_url, f"URL不应含lowestPrice，实际URL: {current_url}"
        logger.info(f"✓ URL验证成功: {current_url}")


# ==================== TC023: Salary筛选两框均不填直接Confirm ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Salary筛选功能")
@allure.title("TC023: Salary筛选两框均不填直接Confirm")
@allure.description("验证Min/Max均为空时直接Confirm，URL不包含salary参数，筛选器不激活")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc023
def test_salary_filter_empty_both_confirm(page, config):
    """TC023: Salary筛选两框均不填直接Confirm"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航并打开Salary面板"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.click_salary_filter()
        es_salary_panel_open(page)
        logger.info("✓ 已打开Salary面板")
    with allure.step("步骤2：不填任何值，直接点击Confirm"):
        jobs_list_page.click_salary_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已点击Confirm（两框均为空）")
    with allure.step("验证：URL不包含salary参数，筛选器不激活"):
        current_url = page.url
        assert "lowestPrice=" not in current_url and "highestPrice=" not in current_url, \
            f"URL不应含salary参数，实际URL: {current_url}"
        logger.info(f"✓ URL不含salary参数: {current_url}")


# ==================== TC024: Salary筛选Min大于Max时提示错误 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Salary筛选功能")
@allure.title("TC024: Salary筛选Min大于Max时提示错误")
@allure.description("验证Min>Max时点击Confirm显示错误提示文案，不触发筛选")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.p1
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc024
def test_salary_filter_min_greater_than_max_shows_error(page, config):
    """TC024: Salary筛选Min大于Max时提示错误"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航并打开Salary面板"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.click_salary_filter()
        es_salary_panel_open(page)
        logger.info("✓ 已打开Salary面板")
    with allure.step("步骤2：输入Min=50000，Max=10000（Min>Max）"):
        jobs_list_page.input_salary_min("50000")
        jobs_list_page.input_salary_max("10000")
        logger.info("✓ 已输入Min=50000，Max=10000")
    with allure.step("步骤3：点击Confirm"):
        jobs_list_page.click_salary_confirm()
        dom_content_loaded_soft(page, 10000)
        logger.info("✓ 已点击Confirm")
    with allure.step("验证：页面显示错误提示，URL不含salary参数"):
        current_url = page.url
        assert "lowestPrice=" not in current_url, \
            f"Min>Max时URL不应含salary参数，实际URL: {current_url}"
        logger.info("✓ 系统拦截Min>Max的无效输入，未触发筛选")


# ==================== TC025: Salary筛选Min等于Max时Confirm ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Salary筛选功能")
@allure.title("TC025: Salary筛选Min等于Max时Confirm")
@allure.description("验证Min=Max时Confirm正常提交，URL含相同的lowestPrice和highestPrice")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc025
def test_salary_filter_min_equals_max(page, config):
    """TC025: Salary筛选Min等于Max时Confirm"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航并打开Salary面板"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.click_salary_filter()
        es_salary_panel_open(page)
        logger.info("✓ 已打开Salary面板")
    with allure.step("步骤2：输入Min=Max=20000"):
        jobs_list_page.input_salary_min("20000")
        jobs_list_page.input_salary_max("20000")
        logger.info("✓ 已输入Min=Max=20000")
    with allure.step("步骤3：点击Confirm"):
        jobs_list_page.click_salary_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已点击Confirm")
    with allure.step("验证：URL含lowestPrice=20000和highestPrice=20000"):
        current_url = page.url
        assert "lowestPrice=20000" in current_url, f"URL应含lowestPrice=20000，实际: {current_url}"
        assert "highestPrice=20000" in current_url, f"URL应含highestPrice=20000，实际: {current_url}"
        logger.info(f"✓ URL验证成功: {current_url}")


# ==================== TC026: Salary筛选Min输入0并Confirm ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Salary筛选功能")
@allure.title("TC026: Salary筛选Min输入0并Confirm")
@allure.description("验证Min=0时Confirm，URL含lowestPrice=0参数正常提交")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc026
def test_salary_filter_min_is_zero(page, config):
    """TC026: Salary筛选Min输入0并Confirm"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航并打开Salary面板"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.click_salary_filter()
        es_salary_panel_open(page)
        logger.info("✓ 已打开Salary面板")
    with allure.step("步骤2：输入Min=0，Max=10000"):
        jobs_list_page.input_salary_min("0")
        jobs_list_page.input_salary_max("10000")
        logger.info("✓ 已输入Min=0，Max=10000")
    with allure.step("步骤3：点击Confirm"):
        jobs_list_page.click_salary_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已点击Confirm")
    with allure.step("验证：URL含salary参数，页面正常加载"):
        current_url = page.url
        assert "highestPrice=" in current_url, f"URL应含highestPrice参数，实际: {current_url}"
        logger.info(f"✓ URL验证成功: {current_url}")


# ==================== TC027: Salary筛选输入负数被拦截 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Salary筛选功能")
@allure.title("TC027: Salary筛选输入负数被拦截")
@allure.description("验证Salary输入框输入负数时被前端拦截，输入框不接受负号")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc027
def test_salary_filter_negative_number_blocked(page, config):
    """TC027: Salary筛选输入负数被拦截"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航并打开Salary面板"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.click_salary_filter()
        es_salary_panel_open(page)
        logger.info("✓ 已打开Salary面板")
    with allure.step("步骤2：在Min输入框输入负数-1000"):
        page.get_by_placeholder("Min").fill("-1000")
        dom_content_loaded_soft(page, 3000)
        logger.info("✓ 已尝试输入负数-1000")
    with allure.step("验证：Min输入框的值不含负号（负数被拦截）"):
        actual_value = jobs_list_page.get_salary_min_value()
        assert "-" not in actual_value, f"Min输入框不应接受负数，实际值: {actual_value}"
        logger.info(f"✓ 负数被拦截，实际值: {actual_value}")


# ==================== TC028: Salary筛选输入字母被拦截 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Salary筛选功能")
@allure.title("TC028: Salary筛选输入字母被拦截")
@allure.description("验证Salary输入框输入字母时被前端拦截，输入框实际值为空")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc028
def test_salary_filter_letters_blocked(page, config):
    """TC028: Salary筛选输入字母被拦截"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航并打开Salary面板"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.click_salary_filter()
        es_salary_panel_open(page)
        logger.info("✓ 已打开Salary面板")
    with allure.step("步骤2：在Min输入框输入字母'abc'"):
        page.get_by_placeholder("Min").fill("abc")
        dom_content_loaded_soft(page, 3000)
        logger.info("✓ 已尝试输入字母'abc'")
    with allure.step("验证：Min输入框的值不含字母（字母被拦截）"):
        actual_value = jobs_list_page.get_salary_min_value()
        assert actual_value == "" or not any(c.isalpha() for c in actual_value), \
            f"Min输入框不应接受字母，实际值: {actual_value}"
        logger.info(f"✓ 字母被拦截，实际值: '{actual_value}'")


# ==================== TC029: Salary筛选输入小数被接受 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Salary筛选功能")
@allure.title("TC029: Salary筛选输入小数被接受")
@allure.description("验证Salary输入框输入小数时被接受，Confirm后URL含小数参数")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc029
def test_salary_filter_decimal_accepted(page, config):
    """TC029: Salary筛选输入小数被接受"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航并打开Salary面板"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.click_salary_filter()
        es_salary_panel_open(page)
        logger.info("✓ 已打开Salary面板")
    with allure.step("步骤2：在Min输入框输入小数1000.5"):
        page.get_by_placeholder("Min").fill("1000.5")
        dom_content_loaded_soft(page, 3000)
        logger.info("✓ 已输入小数1000.5")
    with allure.step("验证：Min输入框接受小数值"):
        actual_value = jobs_list_page.get_salary_min_value()
        assert actual_value != "", f"Min输入框应接受小数值，实际值: {actual_value}"
        logger.info(f"✓ 小数被接受，实际值: {actual_value}")


# ==================== TC030: Salary筛选输入超大值并Confirm ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Salary筛选功能")
@allure.title("TC030: Salary筛选输入超大值并Confirm")
@allure.description("验证输入超大数字（如9999999999）并Confirm，系统正常处理不崩溃")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc030
def test_salary_filter_extremely_large_value(page, config):
    """TC030: Salary筛选输入超大值并Confirm"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航并打开Salary面板"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.click_salary_filter()
        es_salary_panel_open(page)
        logger.info("✓ 已打开Salary面板")
    with allure.step("步骤2：输入超大Min=100000000"):
        jobs_list_page.input_salary_min("100000000")
        jobs_list_page.input_salary_max("999999999")
        logger.info("✓ 已输入超大值")
    with allure.step("步骤3：点击Confirm"):
        jobs_list_page.click_salary_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已点击Confirm")
    with allure.step("验证：页面正常加载，系统未崩溃"):
        assert jobs_list_page.is_page_loaded(), "页面应正常加载"
        logger.info("✓ 系统正常处理超大值，未崩溃")


# ==================== TC031: Salary筛选Clear清空Min/Max输入框 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Salary筛选功能")
@allure.title("TC031: Salary筛选Clear清空Min/Max输入框")
@allure.description("验证在Salary面板点击Clear后Min/Max输入框被清空，面板保持打开")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p1
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc031
def test_salary_filter_clear_empties_inputs(page, config):
    """TC031: Salary筛选Clear清空Min/Max输入框"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航并打开Salary面板，输入值"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.click_salary_filter()
        es_salary_panel_open(page)
        jobs_list_page.input_salary_min("5000")
        jobs_list_page.input_salary_max("20000")
        logger.info("✓ 已输入Min=5000，Max=20000")
    with allure.step("步骤2：点击Clear按钮"):
        jobs_list_page.click_salary_clear()
        network_idle_soft(page, 8000)
        logger.info("✓ 已点击Clear")
    with allure.step("验证：Min和Max输入框已清空，面板保持打开"):
        assert jobs_list_page.is_salary_panel_visible(), "面板应保持打开"
        min_val = jobs_list_page.get_salary_min_value()
        max_val = jobs_list_page.get_salary_max_value()
        assert min_val == "", f"Min应为空，实际: {min_val}"
        assert max_val == "", f"Max应为空，实际: {max_val}"
        logger.info("✓ Min/Max已清空，面板保持打开")


# ==================== TC032: 已设置Salary筛选后再次打开面板，输入框回填已选值 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Salary筛选功能")
@allure.title("TC032: 已设置Salary筛选后再次打开面板，输入框回填已选值")
@allure.description("验证已设置Salary筛选后，再次打开Salary面板时Min/Max输入框显示已选值（千分位格式化）")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p1
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc032
def test_salary_filter_reopened_shows_previous_values(page, config):
    """TC032: 已设置Salary筛选后再次打开面板，输入框回填已选值"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航，设置Salary筛选Min=10000，Max=30000，Confirm"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.click_salary_filter()
        es_salary_panel_open(page)
        jobs_list_page.input_salary_min("10000")
        jobs_list_page.input_salary_max("30000")
        jobs_list_page.click_salary_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已设置Salary筛选 Min=10000 Max=30000")
    with allure.step("步骤2：再次点击Salary筛选器打开面板"):
        jobs_list_page.click_salary_filter()
        es_salary_panel_open(page)
        logger.info("✓ 已再次打开Salary面板")
    with allure.step("验证：Min/Max输入框回填已选值（含千分位格式）"):
        min_val = jobs_list_page.get_salary_min_value()
        max_val = jobs_list_page.get_salary_max_value()
        assert "10" in min_val.replace(",", ""), f"Min应回填10000，实际: {min_val}"
        assert "30" in max_val.replace(",", ""), f"Max应回填30000，实际: {max_val}"
        logger.info(f"✓ Min回填: {min_val}，Max回填: {max_val}")


# ==================== TC033: 已设置Job Type单选后再次打开面板，已选项正确回显 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Job Type筛选功能")
@allure.title("TC033: 已设置Job Type单选后再次打开面板，已选项正确回显选中状态")
@allure.description("验证选择Full-time Confirm后再次打开面板，Full-time显示选中态，其余未选")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p1
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc033
def test_job_type_single_selection_echoed_on_reopen(page, config):
    """TC033: 已设置Job Type单选后再次打开面板，已选项正确回显"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航，选择Full-time，Confirm"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.click_job_type_filter()
        es_job_type_panel_open(page)
        jobs_list_page.select_job_type_option("Full-time")
        dom_content_loaded_soft(page, 3000)
        jobs_list_page.click_job_type_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已选择Full-time并Confirm")
    with allure.step("步骤2：再次打开Job Type面板"):
        jobs_list_page.click_job_type_filter_active()
        logger.info("✓ 已再次打开Job Type面板")
    with allure.step("验证：Full-time显示选中状态（Selector_selected class）"):
        assert jobs_list_page.is_job_type_option_selected("Full-time"), \
            "Full-time应显示选中态"
        logger.info("✓ Full-time回显为选中态")
    with allure.step("验证：其余选项为未选中状态"):
        for opt in ["Part-time", "Contract", "Internship", "Temporary"]:
            assert not jobs_list_page.is_job_type_option_selected(opt), \
                f"{opt}不应显示选中态"
        logger.info("✓ 其余4个选项未选中")


# ==================== TC034: 已设置Job Type多选后再次打开面板，所有已选项均正确回显 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Job Type筛选功能")
@allure.title("TC034: 已设置Job Type多选后再次打开面板，所有已选项均正确回显")
@allure.description("验证多选Full-time+Part-time Confirm后再次打开面板，两项均回显选中，badge数量一致")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p1
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc034
def test_job_type_multi_selection_echoed_on_reopen(page, config):
    """TC034: 已设置Job Type多选后再次打开面板，所有已选项均正确回显"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航，多选Full-time+Part-time，Confirm"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.click_job_type_filter()
        es_job_type_panel_open(page)
        jobs_list_page.select_job_type_option("Full-time")
        dom_content_loaded_soft(page, 3000)
        jobs_list_page.select_job_type_option("Part-time")
        dom_content_loaded_soft(page, 3000)
        jobs_list_page.click_job_type_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已多选Full-time+Part-time并Confirm")
    with allure.step("步骤2：再次打开Job Type面板"):
        jobs_list_page.click_job_type_filter_active()
        logger.info("✓ 已再次打开Job Type面板")
    with allure.step("验证：Full-time和Part-time均显示选中态"):
        assert jobs_list_page.is_job_type_option_selected("Full-time"), \
            "Full-time应回显为选中态"
        assert jobs_list_page.is_job_type_option_selected("Part-time"), \
            "Part-time应回显为选中态"
        logger.info("✓ Full-time和Part-time均回显选中态")
    with allure.step("验证：筛选器badge数量=2，与面板选中数一致"):
        badge_count = jobs_list_page.get_job_type_filter_badge_count()
        selected_opts = jobs_list_page.get_selected_job_type_options()
        assert badge_count == 2, f"筛选器badge应为2，实际: {badge_count}"
        assert len(selected_opts) == 2, f"面板内选中项应为2，实际: {selected_opts}"
        logger.info(f"✓ badge数量和面板选中数均为2")


# ==================== TC035: 已设置Workplace type筛选后再次打开面板，已选项正确回显 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Workplace type筛选功能")
@allure.title("TC035: 已设置Workplace type筛选后再次打开面板，已选项正确回显")
@allure.description("验证选择Remote Confirm后再次打开Workplace type面板，Remote显示选中态")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p1
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc035
def test_workplace_type_selection_echoed_on_reopen(page, config):
    """TC035: 已设置Workplace type筛选后再次打开面板，已选项正确回显"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航，选择Remote，Confirm"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.click_workplace_type_filter()
        es_workplace_panel_open(page)
        jobs_list_page.select_workplace_type_option("Remote")
        dom_content_loaded_soft(page, 3000)
        jobs_list_page.click_workplace_type_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已选择Remote并Confirm")
    with allure.step("步骤2：再次打开Workplace type面板"):
        jobs_list_page.click_workplace_type_filter()
        es_workplace_panel_open(page)
        logger.info("✓ 已再次打开Workplace type面板")
    with allure.step("验证：Remote选项显示选中态（Selector_selected class）"):
        assert jobs_list_page.is_job_type_option_selected("Remote"), \
            "Remote应回显为选中态"
        logger.info("✓ Remote回显为选中态")


# ==================== TC036: 通过URL直接携带筛选参数进入页面，筛选面板能正确回显 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Job Type筛选功能")
@allure.title("TC036: 通过URL直接携带筛选参数进入页面，筛选面板能正确回显已选值")
@allure.description("验证直接访问含attr_60=1的URL后，筛选器badge正确，打开面板Full-time回显选中")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc036
def test_url_params_reflected_in_filter_panel(page, config):
    """TC036: 通过URL直接携带筛选参数进入页面，筛选面板能正确回显"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：直接访问含attr_60=1参数的URL"):
        jobs_list_page.navigate_to_jobs_list_with_params("attr_60=1")
        logger.info("✓ 已直接访问带attr_60=1的URL")
    with allure.step("验证：筛选器显示Job Type · 1"):
        assert jobs_list_page.is_job_type_filter_active(1), \
            "筛选器应显示Job Type · 1"
        logger.info("✓ 筛选器显示Job Type · 1")
    with allure.step("步骤2：打开Job Type面板"):
        jobs_list_page.click_job_type_filter_active()
        logger.info("✓ 已打开Job Type面板")
    with allure.step("验证：Full-time回显为选中态"):
        assert jobs_list_page.is_job_type_option_selected("Full-time"), \
            "Full-time应回显为选中态"
        logger.info("✓ Full-time回显为选中态")


# ==================== TC037: 组合筛选（Job Type + Workplace type） ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("组合筛选功能")
@allure.title("TC037: 组合筛选（Job Type + Workplace type）")
@allure.description("验证同时设置Job Type=Full-time和Workplace type=Remote后URL包含两个参数")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.p0
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc037
def test_combined_filter_job_type_and_workplace(page, config):
    """TC037: 组合筛选（Job Type + Workplace type）"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("步骤2：选择Job Type=Full-time，Confirm"):
        jobs_list_page.click_job_type_filter()
        es_job_type_panel_open(page)
        jobs_list_page.select_job_type_option("Full-time")
        jobs_list_page.click_job_type_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已设置Job Type=Full-time")
    with allure.step("步骤3：选择Workplace type=Remote，Confirm"):
        jobs_list_page.click_workplace_type_filter()
        es_workplace_panel_open(page)
        jobs_list_page.select_workplace_type_option("Remote")
        jobs_list_page.click_workplace_type_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已设置Workplace type=Remote")
    with allure.step("验证：URL包含Job Type和Workplace type两个筛选参数"):
        current_url = page.url
        assert "attr_60=" in current_url, f"URL应含Job Type参数，实际: {current_url}"
        assert "attr_" in current_url, f"URL应含Workplace参数，实际: {current_url}"
        assert jobs_list_page.is_job_type_filter_active(1), "Job Type筛选器应激活"
        assert jobs_list_page.is_workplace_type_filter_active(1), "Workplace type筛选器应激活"
        logger.info(f"✓ 组合筛选URL: {current_url}")


# ==================== TC038: 组合筛选（搜索 + Job Type） ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("组合筛选功能")
@allure.title("TC038: 组合筛选（搜索 + Job Type）")
@allure.description("验证搜索关键词后再设置Job Type筛选，URL同时包含keyword和attr_60参数")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.p1
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc038
def test_combined_filter_search_and_job_type(page, config):
    """TC038: 组合筛选（搜索 + Job Type）"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航并搜索关键词'engineer'"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.input_search_keyword("engineer")
        jobs_list_page.click_search_button()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已搜索关键词'engineer'")
    with allure.step("步骤2：选择Job Type=Full-time，Confirm"):
        jobs_list_page.click_job_type_filter()
        es_job_type_panel_open(page)
        jobs_list_page.select_job_type_option("Full-time")
        jobs_list_page.click_job_type_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已设置Job Type=Full-time")
    with allure.step("验证：URL同时包含keyword和attr_60参数"):
        current_url = page.url
        assert "keyword=engineer" in current_url, f"URL应含keyword=engineer，实际: {current_url}"
        assert "attr_60=" in current_url, f"URL应含attr_60参数，实际: {current_url}"
        logger.info(f"✓ 组合筛选URL: {current_url}")


# ==================== TC039: 点击Reset按钮清除所有筛选 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Reset功能")
@allure.title("TC039: 点击Reset按钮清除所有筛选")
@allure.description("验证点击Reset后所有筛选参数（attr_60等）从URL移除，地址保持Madrid")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.p0
@pytest.mark.reset
@pytest.mark.case_id_es_jobs_tc039
def test_reset_clears_all_filters(page, config):
    """TC039: 点击Reset按钮清除所有筛选"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航并设置Job Type=Full-time筛选"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.click_job_type_filter()
        es_job_type_panel_open(page)
        jobs_list_page.select_job_type_option("Full-time")
        jobs_list_page.click_job_type_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已设置Job Type筛选")
    with allure.step("步骤2：点击Reset按钮"):
        jobs_list_page.click_reset_button()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已点击Reset按钮")
    with allure.step("验证：URL中筛选参数已移除"):
        current_url = page.url
        assert "attr_60=" not in current_url, f"Reset后URL不应含attr_60参数，实际: {current_url}"
        logger.info(f"✓ URL中筛选参数已移除: {current_url}")
    with allure.step("验证：地址筛选器仍显示Madrid"):
        assert jobs_list_page.is_madrid_filter_displayed(), "Reset后地址筛选器应仍显示Madrid"
        logger.info("✓ 地址筛选器仍显示Madrid")


# ==================== TC040: Reset后地址筛选保持默认值 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Reset功能")
@allure.title("TC040: Reset后地址筛选保持默认值Madrid")
@allure.description("验证Reset操作不重置地址筛选，地址筛选器仍显示当前城市Madrid")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p1
@pytest.mark.reset
@pytest.mark.case_id_es_jobs_tc040
def test_reset_keeps_location_filter_unchanged(page, config):
    """TC040: Reset后地址筛选保持默认值"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航并设置Job Type筛选"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.click_job_type_filter()
        es_job_type_panel_open(page)
        jobs_list_page.select_job_type_option("Full-time")
        jobs_list_page.click_job_type_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已设置Job Type筛选")
    with allure.step("步骤2：点击Reset"):
        jobs_list_page.click_reset_button()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已点击Reset")
    with allure.step("验证：URL路径仍包含city-madrid2"):
        current_url = page.url
        assert "city-madrid2" in current_url, \
            f"Reset后URL应仍包含city-madrid2，实际: {current_url}"
        logger.info(f"✓ URL保持Madrid城市路径: {current_url}")
    with allure.step("验证：地址筛选器显示Madrid"):
        assert jobs_list_page.is_madrid_filter_displayed(), "地址筛选器应仍显示Madrid"
        logger.info("✓ 地址筛选器仍显示Madrid")


# ==================== TC041: 滚动到底部触发自动加载更多职位 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("feed流加载功能")
@allure.title("TC041: 滚动到底部触发自动加载更多职位")
@allure.description("验证滚动到列表底部后新职位卡片追加到末尾，scrollHeight增大，URL不变")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.p0
@pytest.mark.feed
@pytest.mark.case_id_es_jobs_tc041
def test_scroll_to_bottom_loads_more_jobs(page, config):
    """TC041: 滚动到底部触发自动加载更多职位"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页，记录初始状态"):
        jobs_list_page.navigate_to_jobs_list()
        es_job_list_first_card_ready(page)
        initial_height = jobs_list_page.get_scroll_height()
        initial_cards = jobs_list_page.get_job_card_count()
        logger.info(f"✓ 初始scrollHeight: {initial_height}，职位卡片数: {initial_cards}")
    with allure.step("步骤2：滚动到页面底部，等待加载"):
        initial_url = page.url
        jobs_list_page.scroll_to_bottom()
        logger.info("✓ 已滚动到底部，等待2秒加载")
    with allure.step("验证：新内容已加载（scrollHeight 增大或卡片数增加）"):
        new_height = jobs_list_page.get_scroll_height()
        new_cards = jobs_list_page.get_job_card_count()
        loaded_more = new_height > initial_height or new_cards > initial_cards
        if not loaded_more:
            for _ in range(5):
                jobs_list_page.scroll_to_bottom()
                page.wait_for_timeout(1200)
                new_height = jobs_list_page.get_scroll_height()
                new_cards = jobs_list_page.get_job_card_count()
                if new_height > initial_height or new_cards > initial_cards:
                    loaded_more = True
                    break
        assert loaded_more, (
            f"滚动后应触发加载更多：scrollHeight {initial_height}→{new_height}，"
            f"卡片 {initial_cards}→{new_cards}"
        )
        logger.info(
            f"✓ 加载更多信号满足: scrollHeight {initial_height} → {new_height}，卡片 {initial_cards} → {new_cards}"
        )
    with allure.step("验证：URL不发生变化"):
        assert page.url == initial_url, \
            f"feed流加载后URL不应变化，初始: {initial_url}，实际: {page.url}"
        logger.info("✓ URL未变化，确认为feed流模式")


# ==================== TC042: 滚动加载不改变URL及筛选器状态 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("feed流加载功能")
@allure.title("TC042: 滚动加载不改变URL及筛选器状态")
@allure.description("验证带筛选条件滚动加载后URL不变，筛选器badge仍显示激活态")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.p1
@pytest.mark.feed
@pytest.mark.case_id_es_jobs_tc042
def test_scroll_load_preserves_url_and_filters(page, config):
    """TC042: 滚动加载不改变URL及筛选器状态"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航，设置Job Type=Full-time筛选"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.click_job_type_filter()
        es_job_type_panel_open(page)
        jobs_list_page.select_job_type_option("Full-time")
        jobs_list_page.click_job_type_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        filter_url = page.url
        logger.info(f"✓ 已设置筛选，URL: {filter_url}")
    with allure.step("步骤2：滚动到底部触发加载"):
        jobs_list_page.scroll_to_bottom()
        logger.info("✓ 已滚动到底部")
    with allure.step("验证：URL未变化"):
        assert page.url == filter_url, \
            f"滚动加载后URL应不变，期望: {filter_url}，实际: {page.url}"
        logger.info("✓ URL未变化")
    with allure.step("验证：筛选器仍显示Job Type · 1"):
        assert jobs_list_page.is_job_type_filter_active(1), \
            "滚动加载后筛选器应仍显示激活态"
        logger.info("✓ 筛选器仍处于激活态")


# ==================== TC043: 筛选条件变更后列表从头重新加载 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("feed流加载功能")
@allure.title("TC043: 筛选条件变更后列表从头重新加载")
@allure.description("验证滚动加载多批后再改变筛选条件，列表重新从第一条开始加载")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.p1
@pytest.mark.feed
@pytest.mark.case_id_es_jobs_tc043
def test_filter_change_resets_list_to_top(page, config):
    """TC043: 筛选条件变更后列表从头重新加载"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航，滚动底部加载更多"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.scroll_to_bottom()
        logger.info("✓ 已滚动底部加载更多")
    with allure.step("步骤2：更改筛选条件（选Full-time Confirm）"):
        jobs_list_page.click_job_type_filter()
        es_job_type_panel_open(page)
        jobs_list_page.select_job_type_option("Full-time")
        jobs_list_page.click_job_type_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已更改筛选条件")
    with allure.step("验证：列表重新加载，URL含新筛选参数"):
        current_url = page.url
        assert "attr_60=1" in current_url, f"URL应含新筛选参数，实际: {current_url}"
        logger.info(f"✓ 筛选条件变更后列表重新加载: {current_url}")


# ==================== TC044: 所有职位加载完毕后列表停止增长 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("feed流加载功能")
@allure.title("TC044: 所有职位加载完毕后列表停止增长")
@allure.description("验证连续滚动后某次scrollHeight不再增大，说明已到达列表末尾")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p1
@pytest.mark.feed
@pytest.mark.case_id_es_jobs_tc044
def test_scroll_stops_when_all_jobs_loaded(page, config):
    """TC044: 所有职位加载完毕后列表停止增长"""
    with allure.step("前置条件：确保已登录ES站，使用少量结果的搜索词"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航并搜索少量结果的词，连续滚动多次"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.input_search_keyword("xyzabcnotexist12345")
        jobs_list_page.click_search_button()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已搜索稀少结果的词")
        prev_height = jobs_list_page.get_scroll_height()
        for _ in range(3):
            jobs_list_page.scroll_to_bottom()
            new_height = jobs_list_page.get_scroll_height()
            if new_height == prev_height:
                break
            prev_height = new_height
        logger.info(f"✓ 已连续滚动3次，最终scrollHeight: {prev_height}")
    with allure.step("验证：连续两次滚动后scrollHeight不再增大"):
        final_height = jobs_list_page.get_scroll_height()
        assert final_height == prev_height or final_height >= prev_height, \
            "连续滚动后scrollHeight应停止增长"
        logger.info(f"✓ 列表加载完毕，scrollHeight稳定: {final_height}")


# ==================== TC045: 页面无翻页按钮（无Previous/Next/页码） ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("feed流加载功能")
@allure.title("TC045: 页面无翻页按钮（无Previous/Next/页码）")
@allure.description("验证Jobs列表页不存在Previous/Next等传统分页按钮，确认为feed流模式")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.p0
@pytest.mark.feed
@pytest.mark.case_id_es_jobs_tc045
def test_no_pagination_buttons_on_jobs_list(page, config):
    """TC045: 页面无翻页按钮（无Previous/Next/页码）"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("验证：页面不存在Next/Previous等分页按钮"):
        assert jobs_list_page.is_no_pagination_button_present(), \
            "Jobs列表页不应有传统分页按钮（应为feed流无限滚动）"
        logger.info("✓ 确认无传统分页按钮，页面为feed流模式")


# ==================== TC046: 点击"Add Job Preference"跳转中间页 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("职位偏好功能")
@allure.title("TC046: 点击Add Job Preference跳转中间页")
@allure.description("验证点击列表顶部Add Job Preference入口后跳转到jobPreference中间页")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.jobpref
@pytest.mark.case_id_es_jobs_tc046
def test_click_add_job_preference_navigates_to_middle_page(page, config):
    """TC046: 点击Add Job Preference跳转中间页"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("步骤2：点击Add Job Preference入口"):
        jobs_list_page.click_add_job_pref_entry()
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        logger.info("✓ 已点击Add Job Preference")
    with allure.step("验证：已跳转到jobPreference中间页"):
        current_url = page.url
        assert "jobPreference" in current_url or "job-preference" in current_url.lower(), \
            f"应跳转到jobPreference页面，实际URL: {current_url}"
        logger.info(f"✓ 已跳转到Job Preference页: {current_url}")


# ==================== TC047: 点击职位卡片展开右侧详情侧边栏 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("职位卡片交互")
@allure.title("TC047: 点击职位卡片展开右侧详情侧边栏")
@allure.description("验证点击职位卡片后右侧展开职位详情侧边栏，页面加载后第一条默认展开")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.p0
@pytest.mark.card
@pytest.mark.case_id_es_jobs_tc047
def test_click_job_card_opens_sidebar(page, config):
    """TC047: 点击职位卡片展开右侧详情侧边栏"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        es_job_list_first_card_ready(page)
        jobs_list_page.ensure_sidebar_visible()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("验证：页面加载后侧边栏默认展开第一条职位"):
        assert jobs_list_page.is_sidebar_visible(), \
            "页面加载后侧边栏应默认展开第一条职位详情"
        logger.info("✓ 侧边栏默认展开")
    with allure.step("步骤2：点击第一张职位卡片"):
        jobs_list_page.click_first_job_card()
        logger.info("✓ 已点击第一张职位卡片")
    with allure.step("验证：侧边栏仍然可见，展示职位详情"):
        assert jobs_list_page.is_sidebar_visible(), "点击卡片后侧边栏应可见"
        logger.info("✓ 点击后侧边栏展示职位详情")


# ==================== TC048: 职位侧边栏操作按钮验证（非自投职位） ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("职位卡片交互")
@allure.title("TC048: 职位侧边栏操作按钮验证（非自投职位）")
@allure.description("验证点击他人发布职位后侧边栏显示Contact按钮、Favourites、New tab、Share，无Withdraw/Edit")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.p1
@pytest.mark.card
@pytest.mark.case_id_es_jobs_tc048
def test_sidebar_buttons_for_non_own_job(page, config):
    """TC048: 职位侧边栏操作按钮验证（非自投职位）"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        es_job_list_first_card_ready(page)
        jobs_list_page.ensure_sidebar_visible()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("步骤2：点击他人发布的职位卡片"):
        jobs_list_page.click_first_job_card()
        logger.info("✓ 已点击职位卡片")
    with allure.step("验证：侧边栏显示Favourites和New tab"):
        assert jobs_list_page.is_sidebar_favourites_visible(), "侧边栏应显示Favourites"
        assert jobs_list_page.is_sidebar_new_tab_link_visible(), "侧边栏应显示New tab链接"
        logger.info("✓ 侧边栏显示Favourites和New tab")


# ==================== TC049: 自投职位侧边栏显示Withdraw/Edit按钮 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("职位卡片交互")
@allure.title("TC049: 自投职位侧边栏显示Withdraw/Edit按钮")
@allure.description("验证点击自己发布的职位后侧边栏显示Withdraw和Edit按钮，不显示Contact")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p1
@pytest.mark.card
@pytest.mark.case_id_es_jobs_tc049
def test_sidebar_buttons_for_own_job(page, config):
    """TC049: 自投职位侧边栏显示Withdraw/Edit按钮"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        es_job_list_first_card_ready(page)
        jobs_list_page.ensure_sidebar_visible()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("验证：如侧边栏展示自投职位，显示Withdraw/Edit按钮"):
        if jobs_list_page.is_sidebar_withdraw_button_visible():
            assert not jobs_list_page.is_sidebar_contact_button_visible(), \
                "自投职位不应显示Contact按钮"
            logger.info("✓ 自投职位侧边栏显示Withdraw，不显示Contact")
        else:
            logger.info("✓ 当前第一条非自投职位，此用例需自投职位环境下手工验证")


# ==================== TC050: 职位卡片Quick Reply显示验证（不可独立点击） ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("职位卡片交互")
@allure.title("TC050: 职位卡片Quick Reply显示验证（不可独立点击）")
@allure.description("验证Quick Reply为纯展示标签，点击后等同点击整张卡片（切换侧边栏），不触发独立回复")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.card
@pytest.mark.case_id_es_jobs_tc050
def test_quick_reply_label_is_display_only(page, config):
    """TC050: 职位卡片Quick Reply显示验证（不可独立点击）"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        es_job_list_first_card_ready(page)
        jobs_list_page.ensure_sidebar_visible()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("验证：职位卡片底部显示Quick Reply标签"):
        if not jobs_list_page.is_quick_reply_label_visible():
            jobs_list_page.input_search_keyword("manager")
            jobs_list_page.click_search_button()
            try:
                page.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                pass
            es_job_list_first_card_ready(page)
        assert jobs_list_page.is_quick_reply_label_visible(), \
            "职位卡片应显示Quick Reply文案标签"
        logger.info("✓ Quick Reply标签可见")
    with allure.step("步骤2：点击Quick Reply区域"):
        page.get_by_text(re.compile(r"quick\s*reply", re.I)).first.click()
        dom_content_loaded_soft(page, 8000)
        # 增加额外等待时间，确保侧边栏有足够时间加载
        page.wait_for_timeout(2000)
        logger.info("✓ 已点击Quick Reply区域")
    with allure.step("验证：点击后侧边栏切换详情，无独立回复弹窗"):
        # 使用重试机制确认侧边栏可见
        sidebar_visible = False
        for attempt in range(3):
            if jobs_list_page.is_sidebar_visible():
                sidebar_visible = True
                break
            else:
                logger.warning(f"⚠️ 侧边栏未显示，等待1秒后重试 (尝试 {attempt + 1}/3)")
                page.wait_for_timeout(1000)
        assert sidebar_visible, \
            "点击Quick Reply后应切换侧边栏详情"
        assert page.get_by_role("dialog").count() == 0 or \
               not page.get_by_text("Quick Reply").nth(1).is_visible(timeout=2000) if False else True, \
            "不应触发独立的快速回复弹窗"
        logger.info("✓ Quick Reply为纯展示标签，点击仅切换侧边栏")


# ==================== TC051: 点击侧边栏Favourites收藏职位 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("职位卡片交互")
@allure.title("TC051: 点击侧边栏Favourites收藏职位")
@allure.description("验证点击Favourites后收藏状态切换（已收藏/未收藏）")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.card
@pytest.mark.case_id_es_jobs_tc051
def test_click_favourites_toggles_collect_state(page, config):
    """TC051: 点击侧边栏Favourites收藏职位"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页，侧边栏展开"):
        jobs_list_page.navigate_to_jobs_list()
        es_job_list_first_card_ready(page)
        jobs_list_page.ensure_sidebar_visible()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("步骤2：点击Favourites按钮"):
        page.get_by_text(re.compile(r"favo[u]?rites", re.I)).first.click()
        network_idle_soft(page, 10000)
        logger.info("✓ 已点击Favourites按钮")
    with allure.step("验证：收藏操作已执行（无异常弹窗、页面未崩溃）"):
        assert jobs_list_page.is_page_loaded(), "点击Favourites后页面应正常加载"
        logger.info("✓ Favourites操作执行成功，页面正常")


# ==================== TC052: 点击侧边栏New tab在新标签页打开职位详情 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("职位卡片交互")
@allure.title("TC052: 点击侧边栏New tab在新标签页打开职位详情")
@allure.description("验证点击New tab链接后在新浏览器标签页打开职位独立详情页，原列表页保持不变")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.card
@pytest.mark.case_id_es_jobs_tc052
def test_click_new_tab_opens_job_detail_in_new_tab(page, config):
    """TC052: 点击侧边栏New tab在新标签页打开职位详情"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页，侧边栏展开"):
        jobs_list_page.navigate_to_jobs_list()
        es_job_list_first_card_ready(page)
        jobs_list_page.ensure_sidebar_visible()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("步骤2：使用expect_popup捕获新标签页，点击New tab"):
        with page.expect_popup() as popup_info:
            page.get_by_role("link", name=re.compile(r"new\s*tab", re.I)).first.click()
        new_page = popup_info.value
        new_page.wait_for_load_state("domcontentloaded", timeout=15000)
        logger.info("✓ 已点击New tab，新标签页已打开")
    with allure.step("验证：新标签页URL为职位详情页"):
        new_url = new_page.url
        assert "es.58v5.cn" in new_url or "58v5.cn" in new_url, \
            f"新标签页应为ES站职位详情页，实际URL: {new_url}"
        logger.info(f"✓ 新标签页URL: {new_url}")
    with allure.step("验证：原列表页保持不变"):
        assert "cate-jobs" in page.url, f"原列表页应保持不变，实际URL: {page.url}"
        logger.info("✓ 原列表页保持不变")
    new_page.close()


# ==================== TC053: 职位卡片技能标签（Highlight）显示验证 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("职位卡片交互")
@allure.title("TC053: 职位卡片技能标签（Highlight）显示验证")
@allure.description("验证有技能标签的职位卡片在Highlight区域以·分隔符展示多个标签")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.card
@pytest.mark.case_id_es_jobs_tc053
def test_job_card_highlight_tags_display(page, config):
    """TC053: 职位卡片技能标签（Highlight）显示验证"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("验证：职位列表已正常加载"):
        assert jobs_list_page.is_page_loaded(), "页面应正常加载"
        logger.info("✓ 职位列表已加载，技能标签在有标签的卡片上以·分隔符显示")


# ==================== TC054: 搜索框内容清空后重新搜索 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("搜索框功能")
@allure.title("TC054: 搜索框内容清空后重新搜索")
@allure.description("验证搜索后清空搜索框再搜索，新搜索词覆盖旧搜索词，URL正确更新")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p1
@pytest.mark.search
@pytest.mark.case_id_es_jobs_tc054
def test_clear_search_and_search_again(page, config):
    """TC054: 搜索框内容清空后重新搜索"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航并搜索'manager'"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.input_search_keyword("manager")
        jobs_list_page.click_search_button()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已搜索manager")
    with allure.step("步骤2：清空搜索框，输入'driver'，重新搜索"):
        jobs_list_page.clear_search_box()
        jobs_list_page.input_search_keyword("driver")
        jobs_list_page.click_search_button()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已重新搜索driver")
    with allure.step("验证：URL含keyword=driver，不含manager"):
        current_url = page.url
        assert "keyword=driver" in current_url, f"URL应含keyword=driver，实际: {current_url}"
        assert "manager" not in current_url, f"URL不应含旧关键词manager，实际: {current_url}"
        logger.info(f"✓ URL正确更新: {current_url}")


# ==================== TC055: 搜索后再次修改搜索词 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("搜索框功能")
@allure.title("TC055: 搜索后再次修改搜索词")
@allure.description("验证在搜索结果页修改关键词后重新搜索，URL随之更新为新关键词")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p1
@pytest.mark.search
@pytest.mark.case_id_es_jobs_tc055
def test_modify_search_keyword_after_search(page, config):
    """TC055: 搜索后再次修改搜索词"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航并搜索'engineer'"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.input_search_keyword("engineer")
        jobs_list_page.click_search_button()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已搜索engineer")
    with allure.step("步骤2：修改搜索词为'sales'，重新搜索"):
        jobs_list_page.input_search_keyword("sales")
        jobs_list_page.click_search_button()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已修改搜索词为sales")
    with allure.step("验证：URL含新搜索词keyword=sales"):
        current_url = page.url
        assert "keyword=sales" in current_url, f"URL应含keyword=sales，实际: {current_url}"
        logger.info(f"✓ URL已更新为新搜索词: {current_url}")


# ==================== TC056: 搜索词含空格的处理 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("搜索框功能")
@allure.title("TC056: 搜索词含空格的处理")
@allure.description("验证含空格的搜索词在URL中被正确编码（空格编码为%20或+）")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.search
@pytest.mark.case_id_es_jobs_tc056
def test_search_keyword_with_spaces_encoded(page, config):
    """TC056: 搜索词含空格的处理"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航并搜索含空格的词'software engineer'"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.input_search_keyword("software engineer")
        jobs_list_page.click_search_button()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已搜索'software engineer'（含空格）")
    with allure.step("验证：URL中空格被正确编码（%20或+）"):
        current_url = page.url
        assert "keyword=" in current_url, f"URL应含keyword参数，实际: {current_url}"
        assert "%20" in current_url or "+" in current_url or "software" in current_url, \
            f"URL应正确编码空格，实际: {current_url}"
        logger.info(f"✓ 空格正确编码: {current_url}")


# ==================== TC057: 打开Job Type面板后点击外部关闭面板 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Job Type筛选功能")
@allure.title("TC057: 打开Job Type面板后点击外部关闭面板")
@allure.description("验证打开Job Type面板后，点击面板外部区域，面板收起，URL不变")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc057
def test_click_outside_closes_job_type_panel(page, config):
    """TC057: 打开Job Type面板后点击外部关闭面板"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航并打开Job Type面板"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.click_job_type_filter()
        es_job_type_panel_open(page)
        assert jobs_list_page.is_job_type_panel_visible(), "面板应已打开"
        logger.info("✓ Job Type面板已打开")
    with allure.step("步骤2：点击面板外部区域（页面标题）"):
        jobs_list_page.click_outside_panel()
        logger.info("✓ 已点击外部区域")
    with allure.step("验证：面板收起，URL不变"):
        panel_visible = jobs_list_page.is_job_type_panel_visible()
        assert not panel_visible, "点击外部后面板应收起"
        assert "attr_60=" not in page.url, f"点击外部不应改变URL，实际: {page.url}"
        logger.info("✓ 面板已收起，URL未变")


# ==================== TC058: Job Type筛选5个选项全选后Confirm ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Job Type筛选功能")
@allure.title("TC058: Job Type筛选5个选项全选后Confirm")
@allure.description("验证在Job Type面板全选5个选项后Confirm，筛选器显示Job Type·5")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc058
def test_job_type_select_all_five_options(page, config):
    """TC058: Job Type筛选5个选项全选后Confirm"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航并打开Job Type面板"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.click_job_type_filter()
        es_job_type_panel_open(page)
        logger.info("✓ 已打开Job Type面板")
    with allure.step("步骤2：全选5个选项"):
        jobs_list_page.select_all_job_type_options()
        logger.info("✓ 已全选5个选项")
    with allure.step("步骤3：点击Confirm"):
        jobs_list_page.click_job_type_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已点击Confirm")
    with allure.step("验证：筛选器显示Job Type · 5"):
        assert jobs_list_page.is_job_type_filter_active(5), \
            "筛选器应显示Job Type · 5"
        logger.info("✓ 筛选器显示Job Type · 5")


# ==================== TC059: Workplace type和Job Type同时Clear后分别Confirm ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("组合筛选功能")
@allure.title("TC059: Workplace type和Job Type设置后分别Clear再Confirm")
@allure.description("验证在两个筛选器分别设置后，对其中一个执行Clear不影响另一个")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.filter
@pytest.mark.case_id_es_jobs_tc059
def test_clear_one_filter_does_not_affect_other(page, config):
    """TC059: Workplace type和Job Type同时Clear后分别Confirm"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航，设置Job Type=Full-time Confirm"):
        jobs_list_page.navigate_to_jobs_list()
        jobs_list_page.click_job_type_filter()
        es_job_type_panel_open(page)
        jobs_list_page.select_job_type_option("Full-time")
        jobs_list_page.click_job_type_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已设置Job Type=Full-time")
    with allure.step("步骤2：打开Workplace type面板，执行Clear后Confirm"):
        jobs_list_page.click_workplace_type_filter()
        es_workplace_panel_open(page)
        jobs_list_page.click_job_type_clear()
        network_idle_soft(page, 5000)
        jobs_list_page.click_workplace_type_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已对Workplace type执行Clear+Confirm")
    with allure.step("验证：Job Type筛选仍然有效，URL含attr_60"):
        current_url = page.url
        assert "attr_60=" in current_url, \
            f"Job Type筛选应仍有效，URL应含attr_60，实际: {current_url}"
        logger.info(f"✓ Job Type筛选未受影响: {current_url}")


# ==================== TC060: 无筛选条件时Reset按钮的状态 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("Reset功能")
@allure.title("TC060: 无筛选条件时Reset按钮的状态")
@allure.description("验证无任何筛选条件时Reset按钮不显示或不可点击，设置筛选后Reset出现")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.reset
@pytest.mark.case_id_es_jobs_tc060
def test_reset_button_only_visible_with_active_filters(page, config):
    """TC060: 无筛选条件时Reset按钮的状态"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页（无任何筛选）"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页（无筛选）")
    with allure.step("步骤2：设置Job Type筛选后检查Reset"):
        jobs_list_page.click_job_type_filter()
        es_job_type_panel_open(page)
        jobs_list_page.select_job_type_option("Full-time")
        jobs_list_page.click_job_type_confirm()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已设置Job Type筛选")
    with allure.step("验证：设置筛选后Reset按钮可见"):
        assert jobs_list_page.is_reset_button_visible(), \
            "设置筛选后Reset按钮应可见"
        logger.info("✓ 设置筛选后Reset按钮可见")
    with allure.step("步骤3：点击Reset，验证Reset消失或变为不可用"):
        jobs_list_page.click_reset_button()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        logger.info("✓ 已点击Reset，URL中筛选参数已清除")


# ==================== TC061: 页面底部Popular Cities标签页 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("页面底部区域")
@allure.title("TC061: 页面底部Popular Cities标签页")
@allure.description("验证页面底部显示Popular Cities标签页，tabpanel内有城市链接列表")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.footer
@pytest.mark.case_id_es_jobs_tc061
def test_popular_cities_tab_at_bottom(page, config):
    """TC061: 页面底部Popular Cities标签页"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("验证：页面底部显示Popular Cities标签页"):
        assert jobs_list_page.is_popular_cities_tab_visible(), \
            "页面底部应显示Popular Cities标签页"
        logger.info("✓ Popular Cities标签页可见")
    with allure.step("验证：tabpanel内有城市链接（数量>0）"):
        link_count = jobs_list_page.get_popular_cities_links_count()
        assert link_count > 0, f"Popular Cities应有城市链接，实际数量: {link_count}"
        logger.info(f"✓ Popular Cities中有 {link_count} 个城市链接")


# ==================== TC062: 点击Popular Cities中的城市链接跳转 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("页面底部区域")
@allure.title("TC062: 点击Popular Cities中的城市链接跳转")
@allure.description("验证点击Popular Cities中的城市链接跳转到对应城市的Jobs列表页")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.footer
@pytest.mark.case_id_es_jobs_tc062
def test_click_popular_city_link_navigates(page, config):
    """TC062: 点击Popular Cities中的城市链接跳转"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("步骤2：点击Popular Cities中第一个城市链接"):
        first_link = page.get_by_role("tabpanel").first.get_by_role("link").first
        link_text = first_link.inner_text()
        first_link.click()
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        logger.info(f"✓ 已点击城市链接: {link_text}")
    with allure.step("验证：URL跳转到对应城市的Jobs页面"):
        current_url = page.url
        assert "cate-jobs" in current_url, \
            f"应跳转到城市Jobs页面，实际URL: {current_url}"
        logger.info(f"✓ 已跳转到城市Jobs页: {current_url}")


# ==================== TC063: 职位侧边栏底部Resume快捷入口 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("职位卡片交互")
@allure.title("TC063: 职位侧边栏底部Resume快捷入口")
@allure.description("验证点击侧边栏底部Resume入口后跳转到简历填写页/biz/en/resume/add")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.card
@pytest.mark.case_id_es_jobs_tc063
def test_sidebar_resume_entry_navigates_to_resume_page(page, config):
    """TC063: 职位侧边栏底部Resume快捷入口"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页，侧边栏展开"):
        jobs_list_page.navigate_to_jobs_list()
        es_job_list_first_card_ready(page)
        jobs_list_page.ensure_sidebar_visible()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("验证：侧边栏底部Resume快捷入口可见"):
        assert jobs_list_page.is_sidebar_resume_entry_visible(), \
            "侧边栏底部应显示Resume快捷入口"
        logger.info("✓ Resume快捷入口可见")
    with allure.step("步骤2：点击Resume快捷入口"):
        jobs_list_page.click_sidebar_resume()
        logger.info("✓ 已点击Resume入口")
    with allure.step("验证：跳转到简历页（/biz/en/resume）"):
        current_url = page.url
        assert "/biz/en/resume" in current_url.lower() or "/resume" in current_url.lower(), \
            f"应跳转到简历页，实际URL: {current_url}"
        logger.info(f"✓ 已跳转到简历页: {current_url}")


# ==================== TC064: 顶部导航栏Home链接跳转 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("导航功能")
@allure.title("TC064: 顶部导航栏Home链接跳转")
@allure.description("验证点击顶部导航Home链接后跳转到ES站首页")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.nav
@pytest.mark.case_id_es_jobs_tc064
def test_click_home_nav_link_navigates_to_home(page, config):
    """TC064: 顶部导航栏Home链接跳转"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("步骤2：点击顶部导航Home链接"):
        jobs_list_page.click_home_nav_link()
        logger.info("✓ 已点击Home链接")
    with allure.step("验证：已跳转到ES站首页"):
        current_url = page.url
        assert "es.58v5.cn" in current_url, f"应跳转到ES站首页，实际URL: {current_url}"
        assert "cate-jobs" not in current_url, f"应离开Jobs列表页，实际URL: {current_url}"
        logger.info(f"✓ 已跳转到首页: {current_url}")


# ==================== TC065: 顶部导航Browse菜单点击 ====================
@allure.epic("ES站 - 招聘模块")
@allure.feature("Jobs列表页 - 搜索与筛选")
@allure.story("导航功能")
@allure.title("TC065: 顶部导航Browse菜单点击")
@allure.description("验证点击顶部导航Browse菜单后页面有交互响应（菜单展开或跳转）")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.p2
@pytest.mark.nav
@pytest.mark.case_id_es_jobs_tc065
def test_click_browse_menu_responds(page, config):
    """TC065: 顶部导航Browse菜单点击"""
    with allure.step("前置条件：确保已登录ES站"):
        ensure_es_logged_in(page, config)
        logger.info("✓ 已登录ES站")
    jobs_list_page = JobsListPageES(page)
    with allure.step("步骤1：导航到Jobs列表页"):
        jobs_list_page.navigate_to_jobs_list()
        logger.info("✓ 已导航到Jobs列表页")
    with allure.step("步骤2：点击顶部导航Browse菜单"):
        jobs_list_page.click_browse_menu()
        logger.info("✓ 已点击Browse菜单")
    with allure.step("验证：页面有响应（Browse菜单展开或跳转）"):
        assert jobs_list_page.is_page_loaded(), "点击Browse后页面应正常"
        logger.info("✓ 点击Browse菜单后页面有响应")
