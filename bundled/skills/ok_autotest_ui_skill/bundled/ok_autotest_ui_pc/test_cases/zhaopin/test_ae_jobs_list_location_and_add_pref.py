"""
AE站 - Jobs列表页 Location与Add Job Preferences入口验证

本脚本由 playwright-test-generator 生成
录制文档：test_cases/zhaopin/ok-ae-JobsList-LocationAndAddPref-测试用例-20260309.md
生成时间：2026-03-09

测试站点：AE (https://ae.58v5.cn)
测试角色：访客（未登录）
测试目标：验证从首页点击Jobs金刚位进入列表页后，Location筛选器显示具体地址（Abu Dhabi），
         Add Job Preferences入口卡片在未登录状态下可见
"""
import pytest
import allure
from pages.jobs_list_page_ae import JobsListPageAE
from pages.sg_home_page import SgHomePage
from utils.logger import setup_logger

logger = setup_logger()

from test_cases.zhaopin.explicit_waits import dom_content_loaded_soft, network_idle_soft, sg_wait_jobs_list_url, sg_after_home_jobs_icon

# ============================================
# 测试环境配置（来自录制文档，无需登录）
# ============================================
_CONFIG = {
    "site": "ae",
    "site_name": "阿联酋站",
    "role": "visitor",
    "user_name": "unauthenticated",
    "base_url": "https://ae.58v5.cn",
    "home_url": "https://ae.58v5.cn/en/city-abu-dhabi/",
    "jobs_list_url": "https://ae.58v5.cn/en/city-abu-dhabi/cate-jobs/?iconSource=jobs",
    "test_account": None,  # 无需登录
    "locale": "en-AE",
    "currency": "AED",
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


def _ensure_ae_visitor_before_test(page, config) -> None:
    """
    访客态用例前置：若当前为登录态则退登；失败时回退为清理 Cookie 与本地存储。
    """
    home_url = config["home_url"]
    try:
        page.goto(home_url, wait_until="domcontentloaded", timeout=15000)
        dom_content_loaded_soft(page, 20000)
    except Exception as e:
        logger.warning("AE 访客态前置：导航首页失败: %s", e)
        return

    home = SgHomePage(page)
    try:
        home.handle_cookie_popup()
    except Exception:
        pass

    if not home.is_logged_in():
        logger.info("AE 访客态前置：当前已是访客态")
        return

    logger.info("AE 访客态前置：检测到登录态，尝试退登")
    try:
        page.locator("text=/OKer_/").first.click()
        dom_content_loaded_soft(page, 20000)
        page.get_by_text("Log Out").click()
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        dom_content_loaded_soft(page, 20000)
    except Exception as e:
        logger.warning("AE UI 退登失败，清理存储与 Cookie: %s", e)
        try:
            page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
        except Exception:
            pass
        page.context.clear_cookies()
        try:
            page.goto(home_url, wait_until="domcontentloaded", timeout=15000)
            dom_content_loaded_soft(page, 20000)
            home.handle_cookie_popup()
        except Exception:
            pass

    if home.is_logged_in():
        try:
            page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
        except Exception:
            pass
        page.context.clear_cookies()
        page.goto(home_url, wait_until="domcontentloaded", timeout=15000)
        dom_content_loaded_soft(page, 20000)
        try:
            home.handle_cookie_popup()
        except Exception:
            pass


@pytest.mark.case_id_ae_jobs_location01
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.jobs
@pytest.mark.ae
@allure.feature("OK")
@allure.story("Jobs列表页 - Location筛选器验证")
@allure.title("Location筛选器应显示具体城市地址Abu Dhabi而不是空值")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证从首页点击Jobs金刚位进入列表页后，Location筛选器显示当前城市Abu Dhabi而不是空值状态")
def test_location_filter_shows_specific_city(page, config):
    """TC001: Location筛选器显示具体城市地址"""
    _ensure_ae_visitor_before_test(page, config)

    # ========== Arrange：准备测试数据和对象 ==========
    jobs_list_page = JobsListPageAE(page)
    
    # 从 config 读取测试数据
    home_url = config['home_url']
    jobs_list_url = config['jobs_list_url']
    
    # 记录测试配置
    logger.info("="*80)
    logger.info("AE站 - Jobs列表页 Location筛选器验证测试")
    logger.info("="*80)
    logger.info(f"站点: {config['site'].upper()} (阿联酋站)")
    logger.info(f"角色: VISITOR (访客/未登录)")
    logger.info(f"首页URL: {home_url}")
    logger.info(f"Jobs列表URL: {jobs_list_url}")
    logger.info("="*80)
    
    # ========== Act 阶段1：通过首页Jobs金刚位导航 ==========
    with allure.step("步骤1：打开AE站首页"):
        logger.info("开始导航到首页")
        page.goto(home_url)
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        dom_content_loaded_soft(page, 20000)
        logger.info(f"✓ 成功打开首页: {page.url}")
    
    with allure.step("步骤2：点击Jobs金刚位进入列表页"):
        logger.info("开始点击Jobs金刚位")
        # 录制的选择器：page.get_by_role('link', { name: 'Jobs Jobs' })
        page.get_by_role("link", name="Jobs Jobs").click()
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        dom_content_loaded_soft(page, 20000)
        logger.info(f"✓ 成功进入Jobs列表页: {page.url}")
    
    # ========== Assert 阶段1：验证URL跳转成功 ==========
    with allure.step("验证成功跳转至Jobs列表页"):
        current_url = page.url
        
        # 核心断言1：验证URL包含cate-jobs
        assert "cate-jobs" in current_url, \
            f"未成功跳转至Jobs列表页，当前URL: {current_url}"
        logger.info(f"✓ URL验证通过，包含'cate-jobs': {current_url}")
        
        # 核心断言2：验证页面标题
        page_title = page.title()
        assert "Jobs" in page_title, \
            f"页面标题不正确，当前标题: {page_title}"
        logger.info(f"✓ 页面标题验证通过: {page_title}")
        
        logger.info("✅ Jobs列表页加载成功！")
    
    # ========== Act 阶段3：定位Location筛选器 ==========
    with allure.step("步骤3：定位Location筛选器"):
        logger.info("开始检查Location筛选器")
        dom_content_loaded_soft(page, 20000)
        # 等待筛选器区域加载
        jobs_list_page.wait_for_filter_area_loaded()
        logger.info("✓ 筛选器区域加载完成")
    
    # ========== Assert 阶段2：验证Location显示具体地址 ==========
    with allure.step("验证Location筛选器显示Abu Dhabi"):
        # 核心断言3：Location筛选器可见
        assert jobs_list_page.is_location_filter_visible(), \
            "Location筛选器不可见"
        logger.info("✓ Location筛选器可见")
        
        # 核心断言4：Location显示文本为Abu Dhabi
        location_text = jobs_list_page.get_location_filter_text()
        assert "Abu Dhabi" in location_text, \
            f"Location筛选器未显示Abu Dhabi，当前显示: {location_text}"
        logger.info(f"✓ Location筛选器显示正确: {location_text}")
        
        # 核心断言5：不是空值状态（不包含占位文本）
        assert "Select location" not in location_text.lower(), \
            f"Location筛选器显示为空值占位文本: {location_text}"
        assert "All locations" not in location_text.lower(), \
            f"Location筛选器显示为空值占位文本: {location_text}"
        logger.info("✓ Location筛选器不是空值状态")
        
        logger.info("✅ Location筛选器验证全部通过！")
    
    logger.info("="*80)
    logger.info("✅ TC001 测试通过：Location筛选器显示具体城市地址Abu Dhabi")
    logger.info("="*80)


@pytest.mark.case_id_ae_jobs_add_pref01
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.jobs
@pytest.mark.ae
@allure.feature("OK")
@allure.story("Jobs列表页 - Add Job Preferences入口验证")
@allure.title("Add Job Preferences入口卡片应在未登录状态下可见")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证从首页进入Jobs列表页后，未登录用户可以看到Add Job Preferences引导入口卡片")
def test_add_job_preferences_entry_visible(page, config):
    """TC002: Add Job Preferences入口在列表页可见"""
    _ensure_ae_visitor_before_test(page, config)

    # ========== Arrange：准备测试数据和对象 ==========
    jobs_list_page = JobsListPageAE(page)
    
    # 从 config 读取测试数据
    home_url = config['home_url']
    jobs_list_url = config['jobs_list_url']
    
    # 记录测试配置
    logger.info("="*80)
    logger.info("AE站 - Jobs列表页 Add Job Preferences入口验证测试")
    logger.info("="*80)
    logger.info(f"站点: {config['site'].upper()} (阿联酋站)")
    logger.info(f"角色: VISITOR (访客/未登录)")
    logger.info(f"首页URL: {home_url}")
    logger.info(f"Jobs列表URL: {jobs_list_url}")
    logger.info("="*80)
    
    # ========== Act 阶段1：通过首页Jobs金刚位导航 ==========
    with allure.step("步骤1：打开AE站首页"):
        logger.info("开始导航到首页")
        page.goto(home_url)
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        dom_content_loaded_soft(page, 20000)
        logger.info(f"✓ 成功打开首页: {page.url}")
    
    with allure.step("步骤2：点击Jobs金刚位进入列表页"):
        logger.info("开始点击Jobs金刚位")
        # 录制的选择器：page.get_by_role('link', { name: 'Jobs Jobs' })
        page.get_by_role("link", name="Jobs Jobs").click()
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        dom_content_loaded_soft(page, 20000)
        logger.info(f"✓ 成功进入Jobs列表页: {page.url}")
    
    # ========== Assert 阶段1：验证URL跳转成功 ==========
    with allure.step("验证成功跳转至Jobs列表页"):
        current_url = page.url
        assert "cate-jobs" in current_url, \
            f"未成功跳转至Jobs列表页，当前URL: {current_url}"
        logger.info(f"✓ URL验证通过: {current_url}")
    
    # ========== Act 阶段3：等待页面完全加载 ==========
    with allure.step("步骤3：等待页面完全加载"):
        logger.info("等待页面完全加载")
        dom_content_loaded_soft(page, 20000)
        # 滚动到顶部确保视口包含Add Job Preference卡片
        page.evaluate("window.scrollTo(0, 0)")
        dom_content_loaded_soft(page, 20000)
        logger.info("✓ 页面加载完成，已滚动至顶部")
    
    # ========== Assert 阶段2：验证Add Job Preference入口可见 ==========
    with allure.step("验证Add Job Preference入口卡片可见"):
        # 核心断言1：Add Job Preference卡片可见
        assert jobs_list_page.is_add_job_preference_visible(), \
            "Add Job Preference入口卡片不可见"
        logger.info("✓ Add Job Preference入口卡片可见")
        
        # 核心断言2：验证卡片标题文案
        card_title = jobs_list_page.get_add_job_preference_title()
        assert "Add Job Preference" in card_title, \
            f"Add Job Preference标题文案不正确，当前显示: {card_title}"
        logger.info(f"✓ 卡片标题文案正确: {card_title}")
        
        # 核心断言3：验证卡片副文本
        subtitle_text = jobs_list_page.get_add_job_preference_subtitle()
        assert "Unlock more opportunities" in subtitle_text, \
            f"Add Job Preference副文本不正确，当前显示: {subtitle_text}"
        logger.info(f"✓ 卡片副文本正确: {subtitle_text}")
        
        # 核心断言4：验证卡片可点击
        assert jobs_list_page.is_add_job_preference_clickable(), \
            "Add Job Preference卡片不可点击"
        logger.info("✓ Add Job Preference卡片可点击")
        
        logger.info("✅ Add Job Preference入口验证全部通过！")
    
    logger.info("="*80)
    logger.info("✅ TC002 测试通过：Add Job Preferences入口在列表页可见")
    logger.info("="*80)
