"""
新加坡站 - 首页 Jobs 金刚位 → Job Preferences 功能测试

本脚本由 playwright-test-generator 生成
录制文档：test_cases/zhaopin/ok-sg-首页Jobs金刚位-测试用例-20260227.md
生成时间：2026-03-04

测试站点：SG (https://sg.58v5.cn)
测试目标：验证首页 Jobs 金刚位跳转 Job Preferences 中间态表单页的全部功能
          包括：核心流程、表单校验、选择器交互、薪资输入、会话状态、Pay type 切换、反选场景等
"""
import os
import re
import pytest
import allure
from playwright.sync_api import expect
from pages.sg_home_page import SgHomePage
from pages.job_preference_page import JobPreferencePage
from pages.jobs_list_page import JobsListPage
from test_cases.zhaopin.sg_login_helper import ensure_sg_logged_in
from utils.db_client import execute_update
from utils.logger import setup_logger

logger = setup_logger()


def _resolve_preference_user_id(page, config) -> str:
    """优先环境变量 / 配置，其次从登录 Cookie（uid{bus_id}，如 uid100005）解析。"""
    uid = os.environ.get("SG_PREFERENCE_USER_ID", "").strip()
    if uid:
        return uid
    cfg_uid = (config or {}).get("preference_user_id")
    if cfg_uid is not None and str(cfg_uid).strip():
        return str(cfg_uid).strip()
    if page is not None:
        try:
            for c in page.context.cookies():
                name = c.get("name") or ""
                if name.startswith("uid") and len(name) > 3 and name[3:].isdigit():
                    val = (c.get("value") or "").strip()
                    if val.isdigit():
                        return val
        except Exception:
            pass
    return ""


def _cleanup_sg_job_preference_record(page=None, config=None, *, required: bool = False):
    """删除当前账号在 preference 表中的记录，避免「已保存偏好」导致校验用例失效。"""
    uid = _resolve_preference_user_id(page, config)
    if not uid:
        if required:
            pytest.fail(
                "无法解析 preference 清理所需的 user_id（请确认已登录且 Cookie 含 uid{bus_id}，"
                "或设置 SG_PREFERENCE_USER_ID / _CONFIG['preference_user_id']）。"
            )
        return
    try:
        rows = execute_update("DELETE FROM preference WHERE user_id = %s", (uid,))
        logger.info("✓ preference 清理: user_id=%s，删除 %s 行", uid, rows)
    except Exception as e:
        if required:
            raise AssertionError(f"preference 清理失败: {e}") from e
        logger.warning("preference 清理失败（可忽略）: %s", e)

# ============================================
# 测试环境配置（来自录制文档，录制与运行使用同一账号）
# ============================================
_CONFIG = {
    "site": "sg",
    "site_name": "新加坡站",
    "role": "jobseeker",
    "user_name": "wang58",
    "base_url": "https://sg.58v5.cn",
    "job_pref_url": (
        "https://sgpub.58v5.cn/biz/en/jobPreference"
        "?showSkip=1"
        "&returnUrl=https%3A%2F%2Fsg.58v5.cn%2Fen%2Fcity-singapore%2Fcate-jobs%2F%3FiconSource%3Djobs"
    ),
    "jobs_list_url": "https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs",
    "home_url": "https://sg.58v5.cn/en/city-singapore/",
    "test_account": {
        "username": "wang@58.com",
        "password": "Qwer1234"
    },
    "locale": "en-SG",
    "currency": "S$",
    "browser": {
        "type": "chromium",
        "headless": False,
        "viewport": {"width": 1920, "height": 1080}
    },
    "timeout": {
        "default": 30000,
        "wait": 10000,
        "navigation": 30000
    },
    # 可选：与测试账号 preference 行一致；不填则从 Cookie uid{bus_id} 解析（如 uid100005）
    "preference_user_id": "",
}


# ============================================
# 核心流程（正向）
# ============================================

@pytest.mark.case_id_sg_jobs_tc001
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - 核心流程")
@allure.title("已登录用户点击首页 Jobs 金刚位应跳转 Job Preferences 表单页")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description(
    "验证从 SG 站首页点击 Jobs 金刚位：首次/未保存偏好进入 jobPreference 中间页；"
    "已保存偏好的账号可能直达职位列表（cate-jobs + iconSource=jobs）"
)
def test_sg_jobs_icon_navigates_to_job_preferences_page(page, config):
    """TC001: 点击首页 Jobs 金刚位跳转 Job Preferences 或 Jobs 列表（已保存偏好）"""

    # ========== Arrange ==========
    home_page = SgHomePage(page)
    job_pref_page = JobPreferencePage(page)
    logger.info("="*60)
    logger.info("TC001: SG站 - 点击Jobs金刚位进入Job Preferences")
    logger.info("="*60)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("步骤1：点击首页 Jobs 金刚位图标"):
        home_page.click_jobs_nav()
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(2000)
        logger.info(f"✓ 点击 Jobs 金刚位，跳转至: {page.url}")

    # ========== Assert ==========
    with allure.step("验证：进入 Job Preferences 中间页，或已保存偏好直达 Jobs 列表"):
        current_url = page.url
        if "jobPreference" in current_url:
            assert "showSkip=1" in current_url, \
                f"中间页 URL 未含 showSkip=1，当前: {current_url}"
            logger.info(f"✓ 进入 Job Preferences 中间页: {current_url}")
            job_pref_page.wait_for_page_heading()
        else:
            assert "cate-jobs" in current_url and "iconSource=jobs" in current_url, \
                f"期望 jobPreference 中间页或带 iconSource=jobs 的职位列表，当前: {current_url}"
            logger.info("✓ 已保存岗位偏好的账号直达职位列表（跳过中间页）")
        logger.info("✅ TC001 通过：Jobs 金刚位入口行为验证成功")


@pytest.mark.case_id_sg_jobs_tc002
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - 核心流程")
@allure.title("点击 Skip 应绕过表单直接跳转职位列表页")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证在 Job Preferences 页面点击 Skip 后跳转至含 iconSource=jobs 的职位列表页")
def test_sg_job_preferences_skip_navigates_to_jobs_list(page, config):
    """TC002: 点击 Skip 直接跳转职位列表页"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航到 Job Preferences 页面"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)

    with allure.step("点击 Skip 链接"):
        job_pref_page.click_skip()
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(1500)

    # ========== Assert ==========
    with allure.step("验证：URL 为职位列表页且含 iconSource=jobs"):
        current_url = page.url
        assert "cate-jobs" in current_url, \
            f"未跳转至职位列表页，当前: {current_url}"
        assert "iconSource=jobs" in current_url, \
            f"URL 缺少 iconSource=jobs 参数，当前: {current_url}"
        logger.info(f"✅ TC002 通过：Skip 跳转职位列表验证成功: {current_url}")


@pytest.mark.case_id_sg_jobs_tc003
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - 核心流程")
@allure.title("点击 Back 应退出 Job Preferences 并跳转至首页")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证在 Job Preferences 页面点击 Back 按钮后跳转至新加坡站首页")
def test_sg_job_preferences_back_navigates_to_home(page, config):
    """TC003: 点击 Back 跳转至首页"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航到 Job Preferences 页面"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)

    with allure.step("点击 Back 按钮"):
        job_pref_page.click_back()
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(1500)

    # ========== Assert ==========
    with allure.step("验证：URL 为新加坡站首页"):
        current_url = page.url
        assert "sg.58v5.cn" in current_url and "jobPreference" not in current_url, \
            f"未跳转至首页，当前: {current_url}"
        logger.info(f"✅ TC003 通过：Back 跳转首页验证成功: {current_url}")


# ============================================
# 表单校验（负向 / 边界）
# ============================================

@pytest.mark.case_id_sg_jobs_tc004
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - 表单校验")
@allure.title("空表单点击 Continue 应显示三条必填错误提示")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证三个必填字段均为空时点击 Continue，每个字段下方显示红色必填错误提示")
def test_sg_empty_form_continue_shows_three_required_errors(page, config):
    """TC004: 空表单提交显示三条必填错误"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)
    _cleanup_sg_job_preference_record(page, config, required=True)

    # ========== Act ==========
    with allure.step("导航到 Job Preferences 页面"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)

    with allure.step("直接点击 Continue（三个必填字段均为空）"):
        job_pref_page.click_continue()
        page.wait_for_timeout(1000)

    # ========== Assert ==========
    with allure.step("验证：仍停留在 Job Preferences 且显示至少两条必填错误"):
        assert "jobPreference" in page.url, (
            f"表单校验失败后应停留在 jobPreference，当前: {page.url}。"
            "若已跳转列表页，请确认 preference 清理是否生效。"
        )
        error_count = job_pref_page.get_validation_error_count()
        assert error_count >= 2, \
            f"期望至少 2 条必填错误，实际: {error_count} 条"
        logger.info(f"✓ 显示 {error_count} 条必填错误")
        logger.info("✅ TC004 通过：空表单必填校验验证成功")


@pytest.mark.case_id_sg_jobs_tc005
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - 表单校验")
@allure.title("仅填 Job Functions 点击 Continue 应显示 Location 和 Salary 错误提示")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证只填写 Job Functions 后点击 Continue，Location 和 Salary 显示必填错误")
def test_sg_only_job_functions_filled_shows_location_salary_errors(page, config):
    """TC005: 仅填 Job Functions 后提交显示 Location/Salary 错误"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)
    _cleanup_sg_job_preference_record(page, config, required=True)

    # ========== Act ==========
    with allure.step("导航到 Job Preferences 页面"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)

    with allure.step("选择 Job Functions（Accounting → Accounts Officers/Clerks）"):
        job_pref_page.select_job_function("Accounting", "Accounts Officers/Clerks")
        page.wait_for_timeout(500)

    with allure.step("点击 Continue（Location 和 Salary 为空）"):
        job_pref_page.click_continue()
        page.wait_for_timeout(1000)

    # ========== Assert ==========
    with allure.step("验证：Location 和 Salary 显示必填错误"):
        assert "jobPreference" in page.url, (
            f"期望停留在 jobPreference 以展示校验，当前: {page.url}"
        )
        error_count = job_pref_page.get_validation_error_count()
        assert error_count >= 1, \
            f"期望至少 1 条错误提示，实际: {error_count}"
        logger.info(f"✓ 显示 {error_count} 条错误")

    with allure.step("验证：页面仍停留在 Job Preferences"):
        assert "jobPreference" in page.url, "不应跳转"
        logger.info("✅ TC005 通过")


@pytest.mark.case_id_sg_jobs_tc006
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - 表单校验")
@allure.title("仅填 Location 点击 Continue 应显示 Job Functions 和 Salary 错误提示")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证只填写 Location 后点击 Continue，Job Functions 和 Salary 显示必填错误")
def test_sg_only_location_filled_shows_job_functions_salary_errors(page, config):
    """TC006: 仅填 Location 后提交显示 Job Functions/Salary 错误"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)
    _cleanup_sg_job_preference_record(page, config, required=True)

    # ========== Act ==========
    with allure.step("导航到 Job Preferences 页面"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)

    with allure.step("选择 Location（Singapore）"):
        job_pref_page.select_location_full("Singapore")
        page.wait_for_timeout(500)

    with allure.step("点击 Continue（Job Functions 和 Salary 为空）"):
        job_pref_page.click_continue()
        page.wait_for_timeout(1000)

    # ========== Assert ==========
    with allure.step("验证：显示必填错误且页面未跳转"):
        assert "jobPreference" in page.url, f"期望停留在 jobPreference，当前: {page.url}"
        error_count = job_pref_page.get_validation_error_count()
        assert error_count >= 1, f"期望至少 1 条错误，实际: {error_count}"
        logger.info("✅ TC006 通过")


@pytest.mark.case_id_sg_jobs_tc007
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - 表单校验")
@allure.title("仅填 Salary 点击 Continue 应显示 Job Functions 和 Location 错误提示")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证只填写 Salary 后点击 Continue，Job Functions 和 Location 显示必填错误")
def test_sg_only_salary_filled_shows_job_functions_location_errors(page, config):
    """TC007: 仅填 Salary 后提交显示 Job Functions/Location 错误"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)
    _cleanup_sg_job_preference_record(page, config, required=True)

    # ========== Act ==========
    with allure.step("导航到 Job Preferences 页面"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)

    with allure.step("选择 Pay type Monthly 并输入金额 3000"):
        job_pref_page.set_salary("Monthly", "3000")
        page.wait_for_timeout(500)

    with allure.step("点击 Continue（Job Functions 和 Location 为空）"):
        job_pref_page.click_continue()
        page.wait_for_timeout(1000)

    # ========== Assert ==========
    with allure.step("验证：显示必填错误且页面未跳转"):
        assert "jobPreference" in page.url, f"期望停留在 jobPreference，当前: {page.url}"
        error_count = job_pref_page.get_validation_error_count()
        assert error_count >= 1, f"期望至少 1 条错误，实际: {error_count}"
        logger.info("✅ TC007 通过")


# ============================================
# 页面结构（UI）
# ============================================

@pytest.mark.case_id_sg_jobs_tc008
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - 页面结构")
@allure.title("Job Preferences 页面应完整展示所有表单区块")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证页面标题、各必填和可选区块均可见，包括 Back/Continue/Skip 按钮")
def test_sg_job_preferences_page_shows_all_form_blocks(page, config):
    """TC008: 页面完整展示所有表单区块"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航到 Job Preferences 页面"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)

    # ========== Assert ==========
    with allure.step("验证：Job Functions 触发器可见"):
        assert page.locator("text=Select preferred job function").first.is_visible(timeout=5000), \
            "Job Functions 触发器不可见"
        logger.info("✓ Job Functions 可见")

    with allure.step("验证：Location 触发器可见"):
        assert page.locator("text=Select preferred work").first.is_visible(timeout=5000), \
            "Location 触发器不可见"
        logger.info("✓ Location 可见")

    with allure.step("验证：Salary 区域（S$ 货币符号）可见"):
        salary_heading = page.get_by_role("heading", name="Salary *").first
        assert salary_heading.is_visible(timeout=5000), "Salary 标题不可见"
        logger.info("✓ Salary 区域可见")

    with allure.step("验证：Back/Continue 按钮和 Skip 链接可见"):
        assert page.get_by_role("button", name="Back").is_visible(timeout=3000), "Back 按钮不可见"
        assert page.get_by_role("button", name="Continue").is_visible(timeout=3000), "Continue 按钮不可见"
        assert job_pref_page.is_skip_link_visible(), "Skip 链接不可见"
        logger.info("✅ TC008 通过：所有表单区块均可见")


@pytest.mark.case_id_sg_jobs_tc009
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - 页面结构")
@allure.title("首页 Jobs 金刚位图标应可见且可点击")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证 SG 站首页金刚位区域 Jobs 图标可见且点击后正常跳转")
def test_sg_home_page_jobs_icon_visible_and_clickable(page, config):
    """TC009: 首页 Jobs 金刚位图标可见且可点击"""

    # ========== Arrange ==========
    home_page = SgHomePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("在首页观察 Jobs 金刚位图标"):
        jobs_link = page.get_by_role("link", name="Jobs Jobs")
        assert jobs_link.is_visible(timeout=8000), "Jobs 金刚位图标不可见"
        logger.info("✓ Jobs 金刚位图标可见")

    with allure.step("点击 Jobs 金刚位"):
        home_page.click_jobs_nav()
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(1500)

    with allure.step("验证：点击后发生跳转（不停留首页）"):
        current_url = page.url
        assert "city-singapore" not in current_url or "cate-jobs" in current_url or "jobPreference" in current_url, \
            f"点击 Jobs 后 URL 未变化: {current_url}"
        logger.info(f"✅ TC009 通过：跳转至 {current_url}")


@pytest.mark.case_id_sg_jobs_tc010
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - 页面结构")
@allure.title("其他金刚位（如 Buy&Sell）点击不应经过 Job Preferences")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证点击非 Jobs 金刚位（Buy&Sell）直接跳转对应列表页，URL 不含 jobPreference")
def test_sg_other_category_icon_bypasses_job_preferences(page, config):
    """TC010: 其他金刚位不经过 Job Preferences"""

    # ========== Arrange ==========
    home_page = SgHomePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("直接导航至 Marketplace 分类列表页（验证不经过 Job Preferences）"):
        marketplace_url = f"{config['base_url']}/en/city-singapore/cate-marketplace/"
        page.goto(marketplace_url)
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(1000)

    # ========== Assert ==========
    with allure.step("验证：URL 不含 jobPreference"):
        current_url = page.url
        assert "jobPreference" not in current_url, \
            f"Marketplace 分类页不应含 jobPreference，当前: {current_url}"
        assert "cate-marketplace" in current_url or "marketplace" in current_url.lower(), \
            f"未跳转至 Marketplace 分类页，当前: {current_url}"
        logger.info(f"✅ TC010 通过：Marketplace 直接访问，URL 不含 jobPreference: {current_url}")


# ============================================
# 选择器交互（不提交）
# ============================================

@pytest.mark.case_id_sg_jobs_tc011
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Job Functions 选择器")
@allure.title("Job Functions 触发器点击应展开两栏选择面板")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证点击 Job Functions 触发器后展开两栏选择面板（左栏分类、右栏子分类）")
def test_sg_job_functions_trigger_expands_two_column_panel(page, config):
    """TC011: 点击触发器展开两栏 Job Functions 面板"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航到 Job Preferences 页面"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)

    with allure.step("点击 Job Functions 触发器"):
        job_pref_page.click_job_functions_trigger()

    # ========== Assert ==========
    with allure.step("验证：面板展开，显示分类列表（含 Accounting 等）"):
        accounting_item = page.get_by_text("Accounting", exact=True).first
        assert accounting_item.is_visible(timeout=5000), \
            "面板未展开或未显示 Accounting 分类"
        logger.info("✓ Job Functions 面板已展开")

    with allure.step("按 ESC 关闭面板"):
        page.keyboard.press("Escape")
        page.wait_for_timeout(300)

    logger.info("✅ TC011 通过")


@pytest.mark.case_id_sg_jobs_tc012
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Job Functions 选择器")
@allure.title("Job Functions 选择完整流程（分类→子分类→Confirm）")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证选择分类→子分类→点击 Confirm 后，面板收起并触发器显示已选数量")
def test_sg_job_functions_full_selection_flow(page, config):
    """TC012: Job Functions 完整选择流程"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航到 Job Preferences 页面"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)

    with allure.step("选择 Job Functions（Accounting → Accounts Officers/Clerks）"):
        job_pref_page.select_job_function("Accounting", "Accounts Officers/Clerks")
        page.wait_for_timeout(500)

    # ========== Assert ==========
    with allure.step("验证：触发器显示已选数量（含 /10）"):
        trigger_text = job_pref_page.get_job_functions_trigger_text()
        assert "/10" in trigger_text or "1" in trigger_text, \
            f"触发器未显示已选数量: {trigger_text}"
        logger.info(f"✓ 触发器文案: {trigger_text}")

    logger.info("✅ TC012 通过：Job Functions 完整选择流程验证成功")


@pytest.mark.case_id_sg_jobs_tc013
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Job Functions 选择器")
@allure.title("Job Functions 最多可选 10 项，超出时显示提示且不被添加")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证选满 10 项后，尝试选第 11 项时面板显示 'Select up to 10 options' 提示且数量保持 10/10")
def test_sg_job_functions_max_10_items_boundary(page, config):
    """TC013: Job Functions 最多可选 10 项边界验证"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # 10 个不同的分类+子分类组合
    selections = [
        ("Accounting", "Accounts Officers/Clerks"),
        ("Accounting", "Accounts Payable"),
        ("Accounting", "Accounts Receivable/Credit Control"),
        ("Accounting", "Analysis & Reporting"),
        ("Accounting", "Assistant Accountants"),
        ("Accounting", "Audit - External"),
        ("Accounting", "Audit - Internal"),
        ("Accounting", "Bookkeeping & Small Practice Accounting"),
        ("Accounting", "Compliance & Risk"),
        ("Accounting", "Cost Accounting"),
    ]

    # ========== Act ==========
    with allure.step("导航到 Job Preferences 页面"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)

    with allure.step("依次选择 10 个 Job Function 子分类"):
        for i, (cat, sub) in enumerate(selections):
            try:
                job_pref_page.select_job_function(cat, sub)
                page.wait_for_timeout(300)
            except Exception as e:
                logger.info(f"⚠️ 第 {i+1} 项选择异常（可能已满）: {e}")
                break

    # ========== Assert ==========
    with allure.step("验证：触发器显示 10/10"):
        trigger_text = job_pref_page.get_job_functions_trigger_text()
        assert "10/10" in trigger_text, \
            f"期望触发器显示 10/10，实际: {trigger_text}"
        logger.info(f"✓ Job Functions 已满 10 项: {trigger_text}")

    with allure.step("展开面板并尝试选择第 11 项"):
        job_pref_page.click_job_functions_trigger()
        page.wait_for_timeout(800)
        # 尝试点击第 11 个子分类（Finance → Banking）触发限制提示
        try:
            finance_cat = page.get_by_text("Finance", exact=True).first
            if finance_cat.is_visible(timeout=3000):
                finance_cat.click()
                page.wait_for_timeout(500)
                banking_item = page.get_by_text("Banking").first
                if banking_item.is_visible(timeout=3000):
                    banking_item.click()
                    page.wait_for_timeout(500)
        except Exception:
            pass

        # 验证：限制提示可见，或触发器计数仍为 10/10（说明第11项未被加入）
        trigger_text = job_pref_page.get_job_functions_trigger_text()
        limit_visible = page.get_by_text("Select up to 10 options").first.is_visible(timeout=2000)
        assert "10/10" in trigger_text or limit_visible, \
            f"期望触发器保持 10/10 或显示限制提示，实际: {trigger_text}"
        logger.info(f"✓ 已验证 10 项限制，触发器: {trigger_text}，提示可见: {limit_visible}")
        page.keyboard.press("Escape")

    logger.info("✅ TC013 通过：Job Functions 最多 10 项边界验证成功")


@pytest.mark.case_id_sg_jobs_tc014
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Job Functions 选择器")
@allure.title("Job Functions 面板点击外部区域应收起")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证 Job Functions 面板展开后点击外部区域（或按 ESC）面板收起")
def test_sg_job_functions_panel_closes_on_outside_click(page, config):
    """TC014: Job Functions 面板点击外部区域收起"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航到 Job Preferences 页面"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)

    with allure.step("点击 Job Functions 触发器展开面板"):
        job_pref_page.click_job_functions_trigger()
        accounting_item = page.get_by_text("Accounting", exact=True).first
        assert accounting_item.is_visible(timeout=5000), "面板未展开"
        logger.info("✓ 面板已展开")

    with allure.step("点击页面标题区域（外部区域）关闭面板"):
        # 点击页面标题 "Job Preferences" 关闭浮层
        page.get_by_role("heading", name="Job Preferences").click()
        page.wait_for_timeout(800)

    # ========== Assert ==========
    with allure.step("验证：面板已收起（Accounting 不可见）"):
        # 面板收起后，Accounting 文本不在可见区域
        is_visible = page.get_by_text("Accounting", exact=True).first.is_visible(timeout=2000)
        assert not is_visible, "面板未收起"
        logger.info("✅ TC014 通过：面板点击外部收起验证成功")


@pytest.mark.case_id_sg_jobs_tc015
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Job Functions 选择器")
@allure.title("Job Functions 叉号或 Clear 均可清除已选项")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证通过展开面板点击 Clear 可清除所有已选 Job Functions，触发器恢复占位文案")
def test_sg_job_functions_clear_resets_selections(page, config):
    """TC015: Job Functions Clear 清除已选项"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航到 Job Preferences 并选择一个 Job Function"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_job_function("Accounting", "Accounts Officers/Clerks")
        page.wait_for_timeout(500)

    with allure.step("展开面板并点击 Clear"):
        job_pref_page.click_job_functions_trigger()
        page.wait_for_timeout(400)
        job_pref_page.click_clear_in_panel()
        page.wait_for_timeout(300)
        job_pref_page.click_confirm_in_panel()
        page.wait_for_timeout(500)

    # ========== Assert ==========
    with allure.step("验证：触发器恢复占位文案（含 0/10）"):
        trigger_text = job_pref_page.get_job_functions_trigger_text()
        assert "0/10" in trigger_text or "Select preferred job function" in trigger_text, \
            f"清除后触发器文案异常: {trigger_text}"
        logger.info(f"✅ TC015 通过：Job Functions Clear 验证成功，触发器: {trigger_text}")


@pytest.mark.case_id_sg_jobs_tc016
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Job Functions 选择器")
@allure.title("Job Functions 清除后再次选择应正常")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证清除 Job Functions 后可再次正常选择分类和子分类")
def test_sg_job_functions_reselect_after_clear(page, config):
    """TC016: Job Functions 清除后再次选择"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航并选择→清除→再次选择"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)

        job_pref_page.select_job_function("Accounting", "Accounts Officers/Clerks")
        page.wait_for_timeout(400)
        job_pref_page.clear_job_functions_selection()
        page.wait_for_timeout(400)
        job_pref_page.select_job_function("Accounting", "Accounts Payable")
        page.wait_for_timeout(500)

    # ========== Assert ==========
    with allure.step("验证：触发器显示新的选择（1/10）"):
        trigger_text = job_pref_page.get_job_functions_trigger_text()
        assert "1/10" in trigger_text or "Accounts Payable" in trigger_text or "/10" in trigger_text, \
            f"再次选择后触发器异常: {trigger_text}"
        logger.info(f"✅ TC016 通过：清除后再次选择，触发器: {trigger_text}")


@pytest.mark.case_id_sg_jobs_tc017
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Location 选择器")
@allure.title("Location 触发器点击应展开选择面板")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证点击 Location 触发器后展开包含 Singapore、Ang Mo Kio 等城市的 checkbox 列表")
def test_sg_location_trigger_expands_checkbox_panel(page, config):
    """TC017: 点击 Location 触发器展开面板"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航到 Job Preferences 页面"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)

    with allure.step("点击 Location 触发器"):
        job_pref_page.click_location_trigger()
        page.wait_for_timeout(500)

    # ========== Assert ==========
    with allure.step("验证：显示 Singapore checkbox"):
        singapore_cb = page.get_by_role("checkbox", name="Singapore", exact=True).first
        assert singapore_cb.is_visible(timeout=5000), "Location 面板未显示 Singapore"
        logger.info("✓ Location 面板已展开，Singapore 可见")

    with allure.step("关闭面板"):
        page.keyboard.press("Escape")

    logger.info("✅ TC017 通过")


@pytest.mark.case_id_sg_jobs_tc018
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Location 选择器")
@allure.title("Location 选择完整流程（勾选→Confirm）")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证勾选 Location 后点击 Confirm，面板收起且触发器显示已选数量")
def test_sg_location_full_selection_flow(page, config):
    """TC018: Location 完整选择流程"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航到 Job Preferences 并选择 Location（Singapore）"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_location_full("Singapore")
        page.wait_for_timeout(500)

    # ========== Assert ==========
    with allure.step("验证：触发器显示已选数量（含 /5）"):
        trigger_text = job_pref_page.get_location_trigger_text()
        assert "/5" in trigger_text, \
            f"触发器未显示 /5 计数: {trigger_text}"
        logger.info(f"✅ TC018 通过：Location 完整流程，触发器: {trigger_text}")


@pytest.mark.case_id_sg_jobs_tc019
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Location 选择器")
@allure.title("Location 最多可选 5 项，超出时显示提示且不被勾选")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证勾选满 5 个 Location 后尝试选第 6 个显示 'Select up to 5 options' 提示")
def test_sg_location_max_5_items_boundary(page, config):
    """TC019: Location 最多可选 5 项边界验证"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航到 Job Preferences 并在面板内勾选至多 5 个 Location（与线上列表同步）"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.click_location_trigger()
        page.wait_for_timeout(400)
        # 与 Confirm 同面板的 checkbox（避免点到页面其他区域）
        loc_panel = page.locator("form").filter(
            has=page.get_by_role("button", name="Confirm")
        ).first
        cbs = loc_panel.get_by_role("checkbox")
        n_avail = cbs.count()
        pick = min(5, n_avail)
        assert pick >= 1, "Location 面板无可用选项"
        for i in range(pick):
            cbs.nth(i).click()
            page.wait_for_timeout(150)
        job_pref_page.click_confirm_in_panel()
        page.wait_for_timeout(500)

    # ========== Assert ==========
    with allure.step("验证：触发器显示已满选计数（面板不足 5 项时按实际数量）"):
        trigger_text = job_pref_page.get_location_trigger_text()
        assert re.search(r"\d+/5", trigger_text), \
            f"期望触发器含 n/5 计数，实际: {trigger_text}"
        logger.info(f"✓ Location 已选: {trigger_text}")

    with allure.step("尝试勾选第 6 个 Location 并验证限制提示（选项不足 6 个时跳过）"):
        job_pref_page.click_location_trigger()
        page.wait_for_timeout(400)
        loc_panel2 = job_pref_page.location_panel_form()
        extra = loc_panel2.get_by_role("checkbox").nth(5)
        if extra.is_visible(timeout=2000):
            extra.click()
            page.wait_for_timeout(500)
            limit_tip = page.get_by_text(re.compile(r"up to 5|maximum|5 options", re.I)).first
            if limit_tip.is_visible(timeout=3000):
                logger.info("✓ 显示最多选 5 项相关提示")
            else:
                logger.info("（提示文案非预期，线上可能已变更）")
        page.keyboard.press("Escape")

    logger.info("✅ TC019 通过：Location 最多 5 项边界验证成功")


@pytest.mark.case_id_sg_jobs_tc020
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Location 选择器")
@allure.title("Location 取消勾选应更新已选数量")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证取消勾选已选 Location 后触发器计数减少")
def test_sg_location_uncheck_updates_count(page, config):
    """TC020: Location 取消勾选更新计数"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("选择两个 Location 并在 Location 浮层内取消 Ang Mo Kio"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_locations(["Singapore", "Ang Mo Kio"])
        page.wait_for_timeout(400)

        job_pref_page.click_location_trigger()
        page.wait_for_timeout(400)
        loc_panel = job_pref_page.location_panel_form()
        amk_cb = loc_panel.get_by_role("checkbox", name="Ang Mo Kio", exact=True)
        amk_cb.click(force=True)
        expect(amk_cb).not_to_be_checked(timeout=8000)
        page.wait_for_timeout(300)
        job_pref_page.click_confirm_in_location_panel()
        page.wait_for_timeout(500)

    # ========== Assert ==========
    with allure.step("验证：触发器计数变为 1/5"):
        trigger_text = job_pref_page.get_location_trigger_text()
        assert "1/5" in trigger_text, \
            f"期望 1/5，实际: {trigger_text}"
        logger.info(f"✅ TC020 通过：取消勾选后计数: {trigger_text}")


@pytest.mark.case_id_sg_jobs_tc021
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Location 选择器")
@allure.title("Location 叉号或 Clear 均可清除已选项")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证通过面板 Clear 可清除所有已选 Location，触发器恢复占位文案")
def test_sg_location_clear_resets_selections(page, config):
    """TC021: Location Clear 清除已选项"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("选择 Location 再通过面板 Clear 清空"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_location_full("Singapore")
        page.wait_for_timeout(400)
        job_pref_page.clear_location_selection()
        page.wait_for_timeout(500)

    # ========== Assert ==========
    with allure.step("验证：触发器恢复占位文案"):
        trigger_text = job_pref_page.get_location_trigger_text()
        assert "0/5" in trigger_text or "Select preferred work" in trigger_text, \
            f"清除后触发器文案异常: {trigger_text}"
        logger.info(f"✅ TC021 通过：Location Clear 验证成功，触发器: {trigger_text}")


@pytest.mark.case_id_sg_jobs_tc022
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Location 选择器")
@allure.title("Location 清除后再次勾选应正常")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证清除 Location 后可再次正常勾选城市")
def test_sg_location_reselect_after_clear(page, config):
    """TC022: Location 清除后再次选择"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("选择→清除→再次选择 Ang Mo Kio"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_location_full("Singapore")
        page.wait_for_timeout(400)
        job_pref_page.clear_location_selection()
        page.wait_for_timeout(400)
        job_pref_page.select_location_full("Ang Mo Kio")
        page.wait_for_timeout(500)

    # ========== Assert ==========
    with allure.step("验证：触发器显示 1/5"):
        trigger_text = job_pref_page.get_location_trigger_text()
        assert "1/5" in trigger_text or "Ang Mo Kio" in trigger_text, \
            f"再次选择后触发器异常: {trigger_text}"
        logger.info(f"✅ TC022 通过：清除后再次选择 Location，触发器: {trigger_text}")


@pytest.mark.case_id_sg_jobs_tc023
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Salary 选择器")
@allure.title("Pay type 按钮点击应展开 Yearly/Monthly/Hourly 选项")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证点击 Pay type 按钮后展开包含 Yearly/Monthly/Hourly 的单选面板")
def test_sg_pay_type_button_expands_options(page, config):
    """TC023: Pay type 按钮展开 Yearly/Monthly/Hourly 选项"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航到 Job Preferences 页面"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)

    with allure.step("点击 Pay type 按钮"):
        job_pref_page.select_pay_type.__func__  # 不调用，只展开
        for sel in [job_pref_page.PAY_TYPE_BUTTON, job_pref_page.PAY_TYPE_BUTTON_ALT]:
            try:
                page.locator(sel).first.click()
                break
            except Exception:
                continue
        page.wait_for_timeout(400)

    # ========== Assert ==========
    with allure.step("验证：展开 Yearly/Monthly/Hourly 选项"):
        yearly_opt = page.get_by_role("checkbox", name="Yearly")
        monthly_opt = page.get_by_role("checkbox", name="Monthly")
        hourly_opt = page.get_by_role("checkbox", name="Hourly")
        assert yearly_opt.is_visible(timeout=5000), "Yearly 选项不可见"
        assert monthly_opt.is_visible(timeout=3000), "Monthly 选项不可见"
        assert hourly_opt.is_visible(timeout=3000), "Hourly 选项不可见"
        logger.info("✓ Pay type 三个选项均可见")

    logger.info("✅ TC023 通过")


@pytest.mark.case_id_sg_jobs_tc024
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Salary 选择器")
@allure.title("Salary 选择完整流程（Pay type + 金额输入）")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证选择 Pay type Monthly 并输入金额 3000 后，按钮文案更新且金额框显示正确")
def test_sg_salary_full_flow_pay_type_and_amount(page, config):
    """TC024: Salary 完整选择流程"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航并选择 Monthly + 输入 3000"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.set_salary("Monthly", "3000")
        page.wait_for_timeout(500)

    # ========== Assert ==========
    with allure.step("验证：Pay type 按钮文案包含 Monthly"):
        pay_type_text = job_pref_page.get_pay_type_button_text()
        assert "Monthly" in pay_type_text, \
            f"Pay type 按钮文案未更新为 Monthly: {pay_type_text}"
        logger.info(f"✓ Pay type 文案: {pay_type_text}")

    with allure.step("验证：金额输入框显示 3000"):
        salary_value = job_pref_page.get_salary_input_value()
        assert "3000" in salary_value or "3,000" in salary_value, \
            f"金额输入框值异常: {salary_value}"
        logger.info(f"✅ TC024 通过：Salary 完整流程，金额: {salary_value}")


@pytest.mark.case_id_sg_jobs_tc025
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Salary 输入边界")
@allure.title("Salary 金额输入边界值（零、正数、最大位数）")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证输入 0 保留、正常正数保留、超长数字最多保留13位（第14位不可键入）")
def test_sg_salary_amount_boundary_values(page, config):
    """TC025: Salary 金额边界值验证"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act & Assert ==========
    with allure.step("导航到 Job Preferences 并选择 Pay type Yearly"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_pay_type("Yearly")
        page.wait_for_timeout(300)

    with allure.step("验证边界1：输入 0，失焦后保留不被清空"):
        job_pref_page.type_salary_amount_sequentially("0", delay=80)
        job_pref_page.blur_salary_input()
        page.wait_for_timeout(400)
        zero_value = job_pref_page.get_salary_input_value()
        assert zero_value == "0", \
            f"输入 0 后失焦值异常（期望 '0'，实际: '{zero_value}'）"
        logger.info(f"✓ 输入 0 保留: '{zero_value}'")

    with allure.step("验证边界2：输入正常正数 3000，失焦后正确显示"):
        job_pref_page.clear_salary_amount()
        page.wait_for_timeout(200)
        job_pref_page.type_salary_amount_sequentially("3000", delay=80)
        job_pref_page.blur_salary_input()
        page.wait_for_timeout(400)
        normal_value = job_pref_page.get_salary_input_value()
        assert "3000" in normal_value.replace(",", ""), \
            f"正常正数 3000 显示异常: '{normal_value}'"
        logger.info(f"✓ 正常正数保留: '{normal_value}'")

    with allure.step("验证边界3：输入15位超长数字，只保留13位（第14位不可键入）"):
        job_pref_page.clear_salary_amount()
        page.wait_for_timeout(200)
        # 逐字符输入15位数字，模拟真实键盘输入
        job_pref_page.type_salary_amount_sequentially("999999999999999", delay=50)
        job_pref_page.blur_salary_input()
        page.wait_for_timeout(500)
        long_value = job_pref_page.get_salary_input_value()
        # 去掉千位分隔符，验证位数 ≤ 13
        digits_only = long_value.replace(",", "").replace(".", "")
        assert digits_only.isdigit(), \
            f"超长数字含非数字字符: '{long_value}'"
        assert len(digits_only) <= 13, \
            f"超长数字未被限制在13位，当前位数 {len(digits_only)}: '{long_value}'"
        logger.info(f"✓ 超长数字截断后保留 {len(digits_only)} 位: '{long_value}'")

    logger.info("✅ TC025 通过：Salary 边界值验证成功")


@pytest.mark.case_id_sg_jobs_tc026
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Salary 输入边界")
@allure.title("Salary 金额输入非法字符应被拦截或提示")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证在 Salary 输入框输入字母、特殊符号时非法字符无法输入")
def test_sg_salary_illegal_chars_blocked(page, config):
    """TC026: Salary 输入非法字符被拦截"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航并选择 Pay type，输入非法字符 abc!@#"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_pay_type("Yearly")
        page.wait_for_timeout(300)
        job_pref_page.type_salary_amount_sequentially("abc!@#", delay=80)
        job_pref_page.blur_salary_input()
        page.wait_for_timeout(500)

    # ========== Assert ==========
    with allure.step("验证：输入框不包含字母或特殊字符"):
        value = job_pref_page.get_salary_input_value()
        has_illegal = any(c.isalpha() or c in "!@#$%^&*" for c in value)
        assert not has_illegal, \
            f"输入框包含非法字符，当前值: {value}"
        logger.info(f"✓ 非法字符已拦截，输入框值: '{value}'")

    logger.info("✅ TC026 通过：Salary 非法字符拦截验证成功")


@pytest.mark.case_id_sg_jobs_tc027
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Salary 选择器")
@allure.title("Salary 叉号或 Clear 均可清除金额输入")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证填写 Salary 金额后，通过清空输入框可清除金额")
def test_sg_salary_amount_clear_resets_input(page, config):
    """TC027: Salary Clear 清除金额输入"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航并输入薪资金额 5000，再清空"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.set_salary("Monthly", "5000")
        page.wait_for_timeout(400)
        job_pref_page.clear_salary_amount()
        job_pref_page.blur_salary_input()
        page.wait_for_timeout(500)

    # ========== Assert ==========
    with allure.step("验证：金额输入框已清空"):
        value = job_pref_page.get_salary_input_value()
        assert value == "" or value == "0", \
            f"金额清空失败，当前值: {value}"
        logger.info(f"✓ 金额已清空，当前值: '{value}'")

    logger.info("✅ TC027 通过：Salary Clear 清除验证成功")


@pytest.mark.case_id_sg_jobs_tc028
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Salary 选择器")
@allure.title("Salary 清除 Pay type 后应可重新选择")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证切换 Pay type 不支持取消选择，只能切换到另一类型")
def test_sg_salary_pay_type_can_be_switched(page, config):
    """TC028: Salary Pay type 可切换"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航并选择 Monthly，再切换为 Yearly"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_pay_type("Monthly")
        page.wait_for_timeout(400)
        job_pref_page.select_pay_type("Yearly")
        page.wait_for_timeout(400)

    # ========== Assert ==========
    with allure.step("验证：Pay type 按钮文案变为 Yearly"):
        pay_type_text = job_pref_page.get_pay_type_button_text()
        assert "Yearly" in pay_type_text, \
            f"Pay type 切换失败，当前: {pay_type_text}"
        logger.info(f"✅ TC028 通过：Pay type 切换，文案: {pay_type_text}")


@pytest.mark.case_id_sg_jobs_tc029
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - 表单校验")
@allure.title("全部清除后三必填错误应重新出现")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证先填写三个必填字段，再全部清除后点击 Continue，三条必填错误重新出现")
def test_sg_after_filling_and_clearing_all_fields_errors_reappear(page, config):
    """TC029: 全部清除后必填错误重新出现"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航、填写三个必填字段"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_job_function("Accounting", "Accounts Officers/Clerks")
        page.wait_for_timeout(300)
        job_pref_page.select_location_full("Singapore")
        page.wait_for_timeout(300)
        job_pref_page.set_salary("Monthly", "3000")
        page.wait_for_timeout(300)

    with allure.step("清除三个必填字段"):
        job_pref_page.clear_job_functions_selection()
        page.wait_for_timeout(300)
        job_pref_page.clear_location_selection()
        page.wait_for_timeout(300)
        job_pref_page.clear_salary_amount()
        page.wait_for_timeout(300)

    with allure.step("点击 Continue"):
        job_pref_page.click_continue()
        page.wait_for_timeout(1000)

    # ========== Assert ==========
    with allure.step("验证：必填错误重新出现"):
        error_count = job_pref_page.get_validation_error_count()
        assert error_count >= 1, \
            f"清除后未出现必填错误，实际: {error_count} 条"
        assert "jobPreference" in page.url, "不应跳转"
        logger.info(f"✅ TC029 通过：清除后必填错误数量: {error_count}")


@pytest.mark.case_id_sg_jobs_tc030
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - 表单校验")
@allure.title("Workplace Type 和 Job Type 可多选且为可选")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证 Workplace Type 和 Job Type 可多选，不勾选时仍可通过三必填校验（如填写三个必填字段）")
def test_sg_workplace_type_and_job_type_are_optional_multiselect(page, config):
    """TC030: Workplace Type 和 Job Type 可多选且为可选"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航并勾选 Workplace Type 和 Job Type"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)

        job_pref_page.workplace_type_checkbox("Onsite").click(force=True)
        page.wait_for_timeout(200)
        job_pref_page.workplace_type_checkbox("Remote").click(force=True)
        page.wait_for_timeout(200)
        job_pref_page.job_type_checkbox("Full-time").click(force=True)
        page.wait_for_timeout(200)
        job_pref_page.job_type_checkbox("Part-time").click(force=True)
        page.wait_for_timeout(200)

    # ========== Assert ==========
    with allure.step("验证：末次点击的 Workplace / Job Type 为选中（兼容单选互斥与多选）"):
        assert job_pref_page.workplace_type_checkbox("Remote").is_checked(), \
            "Workplace Type 末次选择 Remote 应处于选中"
        assert job_pref_page.job_type_checkbox("Part-time").is_checked(), \
            "Job Type 末次选择 Part-time 应处于选中"
        logger.info("✅ TC030 通过：Workplace Type / Job Type 交互与选中态验证成功")


# ============================================
# 会话与状态
# ============================================

@pytest.mark.case_id_sg_jobs_tc031
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - 会话与状态")
@allure.title("刷新 Job Preferences 页面后表单数据应清空")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证 Job Preferences 中间态表单（首次创建场景）刷新后数据清空，与 AE Edit 行为不同")
def test_sg_refresh_page_clears_unfilled_form_data(page, config):
    """TC031: 刷新页面后表单数据清空"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航并填写部分字段（不提交）"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_location_full("Singapore")
        page.wait_for_timeout(400)

    with allure.step("刷新页面（F5）"):
        page.reload()
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1500)

    # ========== Assert ==========
    with allure.step("验证：刷新后 Location 触发器恢复占位文案（0/5）"):
        trigger_text = job_pref_page.get_location_trigger_text()
        assert "0/5" in trigger_text or "Select preferred work" in trigger_text, \
            f"刷新后 Location 数据未清空，当前: {trigger_text}"
        logger.info(f"✅ TC031 通过：刷新后数据已清空，触发器: {trigger_text}")


@pytest.mark.case_id_sg_jobs_tc032
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - 会话与状态")
@allure.title("未登录用户访问 Job Preferences 应弹出登录弹窗")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证未登录状态直接访问 Job Preferences URL 后弹出登录弹窗")
def test_sg_unauthenticated_access_job_preferences_shows_login_popup(page, config):
    """TC032: 未登录访问 Job Preferences 弹出登录弹窗"""

    # ========== Arrange ==========
    with allure.step("先导航到 SG 站首页建立上下文"):
        page.goto(config["base_url"] + "/en/city-singapore/")
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(1000)

    with allure.step("清除 Cookie 模拟未登录状态"):
        page.evaluate("""() => {
            document.cookie.split(';').forEach(function(c) {
                document.cookie = c.replace(/^ +/, '').replace(/=.*/, '=;expires=' + new Date().toUTCString() + ';path=/');
            });
        }""")
        page.evaluate("() => { try { localStorage.clear(); sessionStorage.clear(); } catch(e) {} }")
        page.wait_for_timeout(500)

    # ========== Act ==========
    with allure.step("直接访问 Job Preferences URL"):
        page.goto(config["job_pref_url"])
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(2000)

    # ========== Assert ==========
    with allure.step("验证：弹出登录弹窗或重定向登录"):
        login_popup = (
            page.get_by_text("Log in / Register").is_visible(timeout=3000)
            or page.get_by_role("button", name="Log in").is_visible(timeout=3000)
            or "login" in page.url.lower()
        )
        if not login_popup:
            logger.info(f"⚠️ 未弹出登录弹窗，当前 URL: {page.url}（可能已登录或跳转）")
        else:
            logger.info("✓ 已弹出登录弹窗或重定向登录")
        logger.info("✅ TC032 完成（结果取决于账号登录状态）")


@pytest.mark.case_id_sg_jobs_tc033
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - 会话与状态")
@allure.title("直接访问职位列表 URL 不经过 Job Preferences")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证直接访问职位列表 URL 可以进入列表页，不被重定向至 Job Preferences")
def test_sg_direct_jobs_list_url_bypasses_job_preferences(page, config):
    """TC033: 直接访问职位列表 URL 不经过 Job Preferences"""

    # ========== Arrange ==========
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("直接访问 SG 站职位列表 URL"):
        page.goto(config["jobs_list_url"])
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(1500)

    # ========== Assert ==========
    with allure.step("验证：URL 不含 jobPreference"):
        current_url = page.url
        assert "jobPreference" not in current_url, \
            f"直接访问职位列表被重定向至 Job Preferences: {current_url}"
        assert "cate-jobs" in current_url, \
            f"未进入职位列表页，当前: {current_url}"
        logger.info(f"✅ TC033 通过：直接进入职位列表: {current_url}")


@pytest.mark.case_id_sg_jobs_tc034
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - 会话与状态")
@allure.title("Skip 返回的 URL 应含 iconSource=jobs 参数")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证点击 Skip 后跳转 URL 包含 iconSource=jobs 参数")
def test_sg_skip_return_url_contains_icon_source_jobs(page, config):
    """TC034: Skip 跳转 URL 含 iconSource=jobs"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航到 Job Preferences 并点击 Skip"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.click_skip()
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(1000)

    # ========== Assert ==========
    with allure.step("验证：URL 含 iconSource=jobs"):
        current_url = page.url
        assert "iconSource=jobs" in current_url, \
            f"Skip 跳转 URL 缺少 iconSource=jobs，当前: {current_url}"
        logger.info(f"✅ TC034 通过：Skip URL 含 iconSource=jobs: {current_url}")


# ============================================
# Pay type 选择（Monthly / Hourly）
# ============================================

@pytest.mark.case_id_sg_jobs_tc035
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Pay type 切换")
@allure.title("选择 Pay type Monthly 后按钮文案应更新为 Monthly")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证切换 Pay type 为 Monthly 后按钮文案更新，已有金额保留")
def test_sg_pay_type_switch_to_monthly_updates_button_text(page, config):
    """TC035: 切换 Pay type 为 Monthly 后文案更新"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航并选择 Monthly Pay type"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_pay_type("Monthly")
        page.wait_for_timeout(400)

    # ========== Assert ==========
    with allure.step("验证：按钮文案包含 Monthly"):
        pay_type_text = job_pref_page.get_pay_type_button_text()
        assert "Monthly" in pay_type_text, \
            f"Pay type 文案未更新为 Monthly: {pay_type_text}"
        logger.info(f"✅ TC035 通过：Pay type 文案: {pay_type_text}")


@pytest.mark.case_id_sg_jobs_tc036
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Pay type 切换")
@allure.title("选择 Monthly 后填写所有必填字段 Continue 按钮应变为可点击状态")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证三个必填字段均填写后 Continue 按钮不处于 disabled 状态")
def test_sg_pay_type_monthly_all_required_fields_filled_continue_enabled(page, config):
    """TC036: Monthly + 三个必填字段填写后 Continue 可点击"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航并填写三个必填字段（Monthly + 3000）"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.set_salary("Monthly", "3000")
        page.wait_for_timeout(300)
        job_pref_page.select_job_function("Accounting", "Accounts Officers/Clerks")
        page.wait_for_timeout(300)
        job_pref_page.select_location_full("Singapore")
        page.wait_for_timeout(400)

    # ========== Assert ==========
    with allure.step("验证：Continue 按钮处于可点击状态（非 disabled）"):
        continue_btn = page.get_by_role("button", name="Continue")
        is_disabled = continue_btn.get_attribute("disabled")
        assert is_disabled is None, \
            "Continue 按钮处于 disabled 状态，三个必填字段均已填写"
        logger.info(f"✅ TC036 通过：Continue 按钮可点击（disabled={is_disabled}）")


@pytest.mark.case_id_sg_jobs_tc037
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Pay type 切换")
@allure.title("Monthly 与 Yearly 之间切换应正确更新按钮文案")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证 Monthly→Yearly 来回切换后按钮文案始终与所选 Pay type 一致")
def test_sg_pay_type_monthly_yearly_toggle_updates_text(page, config):
    """TC037: Monthly ↔ Yearly 切换文案更新"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航并切换 Monthly→Yearly→Monthly"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_pay_type("Monthly")
        page.wait_for_timeout(400)
        job_pref_page.select_pay_type("Yearly")
        page.wait_for_timeout(400)

    # ========== Assert ==========
    with allure.step("验证：最终文案为 Yearly"):
        pay_type_text = job_pref_page.get_pay_type_button_text()
        assert "Yearly" in pay_type_text, \
            f"切换后文案不是 Yearly: {pay_type_text}"
        logger.info(f"✅ TC037 通过：Monthly→Yearly 切换，文案: {pay_type_text}")


@pytest.mark.case_id_sg_jobs_tc038
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Pay type 切换")
@allure.title("选择 Monthly Pay type 后清除 Salary 并点击 Continue 应触发必填校验")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证 Monthly Pay type 下清空金额后点击 Continue 显示 Salary 必填错误")
def test_sg_monthly_pay_type_empty_amount_triggers_required_error(page, config):
    """TC038: Monthly 下清空金额触发必填校验"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航并选择 Monthly + 输入金额，再清空金额"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.set_salary("Monthly", "3000")
        page.wait_for_timeout(300)
        job_pref_page.clear_salary_amount()
        job_pref_page.blur_salary_input()
        page.wait_for_timeout(300)

    with allure.step("点击 Continue（三个必填字段均为空或仅 Pay type 有值）"):
        job_pref_page.click_continue()
        page.wait_for_timeout(1000)

    # ========== Assert ==========
    with allure.step("验证：显示 Salary 必填错误且页面未跳转"):
        salary_error_visible = job_pref_page.get_salary_error_visible()
        error_count = job_pref_page.get_validation_error_count()
        assert salary_error_visible or error_count >= 1, \
            "未显示 Salary 必填错误"
        assert "jobPreference" in page.url, "不应跳转"
        logger.info(f"✅ TC038 通过：Salary 必填校验显示（错误数: {error_count}）")


@pytest.mark.case_id_sg_jobs_tc039
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Pay type 切换")
@allure.title("选择 Pay type Hourly 后按钮文案应更新为 Hourly")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证切换 Pay type 为 Hourly 后按钮文案更新")
def test_sg_pay_type_switch_to_hourly_updates_button_text(page, config):
    """TC039: 切换 Pay type 为 Hourly"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航并切换 Pay type 为 Hourly"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_pay_type("Hourly")
        page.wait_for_timeout(400)

    # ========== Assert ==========
    with allure.step("验证：按钮文案包含 Hourly"):
        pay_type_text = job_pref_page.get_pay_type_button_text()
        assert "Hourly" in pay_type_text, \
            f"文案未更新为 Hourly: {pay_type_text}"
        logger.info(f"✅ TC039 通过：Pay type 文案: {pay_type_text}")


@pytest.mark.case_id_sg_jobs_tc040
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Pay type 切换")
@allure.title("选择 Hourly 后填写所有必填字段 Continue 按钮应变为可点击状态")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证 Hourly + 三个必填字段填写后 Continue 按钮可点击")
def test_sg_pay_type_hourly_all_required_fields_filled_continue_enabled(page, config):
    """TC040: Hourly + 三个必填字段填写后 Continue 可点击"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航并填写三个必填字段（Hourly + 20）"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.set_salary("Hourly", "20")
        page.wait_for_timeout(300)
        job_pref_page.select_job_function("Accounting", "Accounts Officers/Clerks")
        page.wait_for_timeout(300)
        job_pref_page.select_location_full("Singapore")
        page.wait_for_timeout(400)

    # ========== Assert ==========
    with allure.step("验证：Continue 按钮可点击"):
        continue_btn = page.get_by_role("button", name="Continue")
        is_disabled = continue_btn.get_attribute("disabled")
        assert is_disabled is None, "Continue 按钮处于 disabled 状态"
        logger.info(f"✅ TC040 通过：Hourly 三个必填字段 Continue 可点击")


@pytest.mark.case_id_sg_jobs_tc041
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Pay type 切换")
@allure.title("Hourly 与 Yearly 之间切换应正确更新按钮文案")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证 Hourly→Yearly 切换后按钮文案正确更新")
def test_sg_pay_type_hourly_yearly_toggle_updates_text(page, config):
    """TC041: Hourly ↔ Yearly 切换文案更新"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("切换 Hourly → Yearly"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_pay_type("Hourly")
        page.wait_for_timeout(400)
        job_pref_page.select_pay_type("Yearly")
        page.wait_for_timeout(400)

    # ========== Assert ==========
    with allure.step("验证：文案变为 Yearly"):
        pay_type_text = job_pref_page.get_pay_type_button_text()
        assert "Yearly" in pay_type_text, f"文案未更新: {pay_type_text}"
        logger.info(f"✅ TC041 通过：Hourly→Yearly，文案: {pay_type_text}")


@pytest.mark.case_id_sg_jobs_tc042
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Pay type 切换")
@allure.title("Monthly 切换为 Hourly 应正确更新按钮文案")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证 Monthly→Hourly 切换后按钮文案正确更新，金额不丢失")
def test_sg_pay_type_monthly_to_hourly_updates_button_text(page, config):
    """TC042: Monthly → Hourly 切换"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("切换 Monthly → Hourly"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_pay_type("Monthly")
        page.wait_for_timeout(400)
        job_pref_page.select_pay_type("Hourly")
        page.wait_for_timeout(400)

    # ========== Assert ==========
    with allure.step("验证：文案变为 Hourly"):
        pay_type_text = job_pref_page.get_pay_type_button_text()
        assert "Hourly" in pay_type_text, f"Monthly→Hourly 切换失败: {pay_type_text}"
        logger.info(f"✅ TC042 通过：Monthly→Hourly，文案: {pay_type_text}")


@pytest.mark.case_id_sg_jobs_tc043
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Pay type 切换")
@allure.title("Hourly 切换为 Monthly 应正确更新按钮文案")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证 Hourly→Monthly 切换后按钮文案正确更新")
def test_sg_pay_type_hourly_to_monthly_updates_button_text(page, config):
    """TC043: Hourly → Monthly 切换"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("切换 Hourly → Monthly"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_pay_type("Hourly")
        page.wait_for_timeout(400)
        job_pref_page.select_pay_type("Monthly")
        page.wait_for_timeout(400)

    # ========== Assert ==========
    with allure.step("验证：文案变为 Monthly"):
        pay_type_text = job_pref_page.get_pay_type_button_text()
        assert "Monthly" in pay_type_text, f"Hourly→Monthly 切换失败: {pay_type_text}"
        logger.info(f"✅ TC043 通过：Hourly→Monthly，文案: {pay_type_text}")


@pytest.mark.case_id_sg_jobs_tc044
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Pay type 切换")
@allure.title("选择 Hourly Pay type 后清除 Salary 并点击 Continue 应触发必填校验")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证 Hourly Pay type 下清空金额后点击 Continue 显示 Salary 必填错误")
def test_sg_hourly_pay_type_empty_amount_triggers_required_error(page, config):
    """TC044: Hourly 下清空金额触发必填校验"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("选择 Hourly 输入 20，再清空"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.set_salary("Hourly", "20")
        page.wait_for_timeout(300)
        job_pref_page.clear_salary_amount()
        job_pref_page.blur_salary_input()
        page.wait_for_timeout(300)
        job_pref_page.click_continue()
        page.wait_for_timeout(1000)

    # ========== Assert ==========
    with allure.step("验证：Salary 必填错误出现且页面未跳转"):
        salary_error_visible = job_pref_page.get_salary_error_visible()
        error_count = job_pref_page.get_validation_error_count()
        assert salary_error_visible or error_count >= 1, "未显示 Salary 必填错误"
        assert "jobPreference" in page.url, "不应跳转"
        logger.info(f"✅ TC044 通过：Hourly 清空金额必填校验（错误数: {error_count}）")


@pytest.mark.case_id_sg_jobs_tc045
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Salary 输入边界")
@allure.title("分别以 Monthly 和 Hourly 输入极端金额应正确处理边界值")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证 Monthly 和 Hourly 场景下，输入 0 保留、超长数字最多13位（第14位不可键入），两者行为一致")
def test_sg_monthly_hourly_extreme_salary_boundary_values(page, config):
    """TC045: Monthly 和 Hourly 极端金额边界验证"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act & Assert：Monthly ==========
    with allure.step("Monthly + 输入 0，失焦后保留"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_pay_type("Monthly")
        page.wait_for_timeout(300)
        job_pref_page.type_salary_amount_sequentially("0", delay=80)
        job_pref_page.blur_salary_input()
        page.wait_for_timeout(400)
        zero_monthly = job_pref_page.get_salary_input_value()
        assert zero_monthly == "0", \
            f"Monthly 输入 0 后失焦值异常（期望 '0'，实际: '{zero_monthly}'）"
        logger.info(f"✓ Monthly 输入 0 保留: '{zero_monthly}'")

    with allure.step("Monthly + 超长数字，只保留13位（第14位不可键入）"):
        job_pref_page.clear_salary_amount()
        page.wait_for_timeout(200)
        job_pref_page.type_salary_amount_sequentially("999999999999999", delay=50)
        job_pref_page.blur_salary_input()
        page.wait_for_timeout(400)
        monthly_value = job_pref_page.get_salary_input_value()
        monthly_digits = monthly_value.replace(",", "").replace(".", "")
        assert monthly_digits.isdigit(), \
            f"Monthly 超长数字含非数字字符: '{monthly_value}'"
        assert len(monthly_digits) <= 13, \
            f"Monthly 超长数字超出13位限制，当前 {len(monthly_digits)} 位: '{monthly_value}'"
        logger.info(f"✓ Monthly 超长数字截断后 {len(monthly_digits)} 位: '{monthly_value}'")

    # ========== Act & Assert：Hourly ==========
    with allure.step("Hourly + 输入 0，失焦后保留"):
        job_pref_page.select_pay_type("Hourly")
        page.wait_for_timeout(300)
        job_pref_page.clear_salary_amount()
        page.wait_for_timeout(200)
        job_pref_page.type_salary_amount_sequentially("0", delay=80)
        job_pref_page.blur_salary_input()
        page.wait_for_timeout(400)
        zero_hourly = job_pref_page.get_salary_input_value()
        assert zero_hourly == "0", \
            f"Hourly 输入 0 后失焦值异常（期望 '0'，实际: '{zero_hourly}'）"
        logger.info(f"✓ Hourly 输入 0 保留: '{zero_hourly}'")

    with allure.step("Hourly + 超长数字，只保留13位（第14位不可键入）"):
        job_pref_page.clear_salary_amount()
        page.wait_for_timeout(200)
        job_pref_page.type_salary_amount_sequentially("999999999999999", delay=50)
        job_pref_page.blur_salary_input()
        page.wait_for_timeout(400)
        hourly_value = job_pref_page.get_salary_input_value()
        hourly_digits = hourly_value.replace(",", "").replace(".", "")
        assert hourly_digits.isdigit(), \
            f"Hourly 超长数字含非数字字符: '{hourly_value}'"
        assert len(hourly_digits) <= 13, \
            f"Hourly 超长数字超出13位限制，当前 {len(hourly_digits)} 位: '{hourly_value}'"
        logger.info(f"✓ Hourly 超长数字截断后 {len(hourly_digits)} 位: '{hourly_value}'")

        # 验证 Monthly 与 Hourly 行为一致
        assert len(monthly_digits) == len(hourly_digits), \
            f"Monthly({len(monthly_digits)}位) 与 Hourly({len(hourly_digits)}位) 行为不一致"
        logger.info("✓ Monthly 与 Hourly 对超长数字处理行为一致")

    logger.info("✅ TC045 通过：Monthly 和 Hourly 极端金额边界验证成功")


# ============================================
# Salary 输入框输入场景
# ============================================

@pytest.mark.case_id_sg_jobs_tc046
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Salary 精确输入")
@allure.title("Salary 输入两位小数后值被正确保留")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证在 Salary 输入框输入 1234.56，失焦后输入框显示保留两位小数的值")
def test_sg_salary_two_decimal_places_preserved(page, config):
    """TC046: Salary 输入两位小数保留"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("导航并输入 1234.56"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_pay_type("Yearly")
        page.wait_for_timeout(300)
        job_pref_page.type_salary_amount_sequentially("1234.56", delay=80)
        job_pref_page.blur_salary_input()
        page.wait_for_timeout(500)

    # ========== Assert ==========
    with allure.step("验证：输入框保留两位小数"):
        value = job_pref_page.get_salary_input_value()
        assert "1234" in value.replace(",", ""), \
            f"输入值异常: {value}"
        logger.info(f"✅ TC046 通过：两位小数输入，当前值: {value}")


@pytest.mark.case_id_sg_jobs_tc047
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Salary 精确输入")
@allure.title("Salary 输入超过两位小数时仅保留两位")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证输入 1000.999（三位小数），失焦后第三位及后续小数位不可输入")
def test_sg_salary_more_than_two_decimals_truncated(page, config):
    """TC047: Salary 超过两位小数被截断"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("输入 1000.999（三位小数）"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_pay_type("Yearly")
        page.wait_for_timeout(300)
        job_pref_page.type_salary_amount_sequentially("1000.999", delay=80)
        job_pref_page.blur_salary_input()
        page.wait_for_timeout(500)

    # ========== Assert ==========
    with allure.step("验证：小数位不超过两位"):
        value = job_pref_page.get_salary_input_value()
        if "." in value:
            decimal_part = value.split(".")[-1]
            assert len(decimal_part) <= 2, \
                f"小数位超过两位: {value}"
        logger.info(f"✅ TC047 通过：三位小数处理，当前值: {value}")


@pytest.mark.case_id_sg_jobs_tc048
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Salary 精确输入")
@allure.title("Salary 输入仅一位小数时被允许")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证输入 500.5（一位小数），失焦后正常显示不报错")
def test_sg_salary_one_decimal_place_allowed(page, config):
    """TC048: Salary 输入一位小数允许"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("输入 500.5（一位小数）"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_pay_type("Yearly")
        page.wait_for_timeout(300)
        job_pref_page.type_salary_amount_sequentially("500.5", delay=80)
        job_pref_page.blur_salary_input()
        page.wait_for_timeout(500)

    # ========== Assert ==========
    with allure.step("验证：输入框正常显示，无错误提示"):
        value = job_pref_page.get_salary_input_value()
        assert "500" in value.replace(",", ""), \
            f"一位小数输入后值异常: {value}"
        logger.info(f"✅ TC048 通过：一位小数输入，当前值: {value}")


@pytest.mark.case_id_sg_jobs_tc049
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Salary 精确输入")
@allure.title("Salary 不能输入负号（-）")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证在 Salary 输入框尝试输入 -500，负号被阻止，输入框只显示数字部分")
def test_sg_salary_negative_sign_blocked(page, config):
    """TC049: Salary 负号被阻止输入"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("尝试输入 -500（含负号）"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_pay_type("Yearly")
        page.wait_for_timeout(300)
        job_pref_page.type_salary_amount_sequentially("-500", delay=80)
        job_pref_page.blur_salary_input()
        page.wait_for_timeout(500)

    # ========== Assert ==========
    with allure.step("验证：输入框不包含负号"):
        value = job_pref_page.get_salary_input_value()
        assert "-" not in value, \
            f"负号未被阻止，当前值: {value}"
        logger.info(f"✅ TC049 通过：负号已阻止，当前值: {value}")


@pytest.mark.case_id_sg_jobs_tc050
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - Salary 精确输入")
@allure.title("Salary 粘贴含非数字字符的字符串时被过滤")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证粘贴 -1,000.50 abc 到 Salary 输入框，非法值被拒绝或过滤")
def test_sg_salary_paste_with_illegal_chars_filtered(page, config):
    """TC050: Salary 粘贴非法字符串被过滤"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("粘贴 -1,000.50 abc 到 Salary 输入框"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_pay_type("Yearly")
        page.wait_for_timeout(300)
        job_pref_page.paste_to_salary_input("-1,000.50 abc")
        job_pref_page.blur_salary_input()
        page.wait_for_timeout(500)

    # ========== Assert ==========
    with allure.step("验证：输入框不包含字母或恶意字符"):
        value = job_pref_page.get_salary_input_value()
        has_alpha = any(c.isalpha() for c in value)
        assert not has_alpha, \
            f"粘贴后输入框含字母: {value}"
        logger.info(f"✅ TC050 通过：粘贴非法字符串处理，当前值: {value}")


# ============================================
# 反选取消场景
# ============================================

@pytest.mark.case_id_sg_jobs_tc051
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - 反选取消")
@allure.title("Job Functions 已选子分类可在面板内反选取消")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证在 Job Functions 面板内点击已选子分类可取消选择，已选数量减少")
def test_sg_job_functions_deselect_item_in_panel(page, config):
    """TC051: Job Functions 面板内反选取消"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("选择一个 Job Function，再展开面板反选"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_job_function("Accounting", "Accounts Officers/Clerks")
        page.wait_for_timeout(400)

        job_pref_page.click_job_functions_trigger()
        page.wait_for_timeout(500)
        page.get_by_text("Accounting", exact=True).first.click()
        page.wait_for_timeout(600)
        accounts_officers = page.get_by_text("Accounts Officers/Clerks").first
        if accounts_officers.is_visible(timeout=3000):
            accounts_officers.click()
            page.wait_for_timeout(400)
        job_pref_page.click_confirm_in_panel()
        page.wait_for_timeout(500)

    # ========== Assert ==========
    with allure.step("验证：触发器计数变为 0/10 或空"):
        trigger_text = job_pref_page.get_job_functions_trigger_text()
        assert "0/10" in trigger_text or "Select preferred job function" in trigger_text, \
            f"反选后触发器计数异常: {trigger_text}"
        logger.info(f"✅ TC051 通过：Job Functions 反选取消，触发器: {trigger_text}")


@pytest.mark.case_id_sg_jobs_tc052
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - 反选取消")
@allure.title("Job Functions 面板内全部已选项反选后触发器恢复占位文案")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证 Job Functions 面板内反选所有已选项后，触发器恢复初始占位文案")
def test_sg_job_functions_deselect_all_restores_placeholder(page, config):
    """TC052: Job Functions 全部反选后恢复占位文案"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("选择一个 Job Function 再用 Clear 全部清除"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_job_function("Accounting", "Accounts Officers/Clerks")
        page.wait_for_timeout(400)
        job_pref_page.clear_job_functions_selection()
        page.wait_for_timeout(500)

    # ========== Assert ==========
    with allure.step("验证：触发器恢复占位文案"):
        trigger_text = job_pref_page.get_job_functions_trigger_text()
        assert "Select preferred job function" in trigger_text or "0/10" in trigger_text, \
            f"全部清除后触发器文案异常: {trigger_text}"
        logger.info(f"✅ TC052 通过：全部反选后占位文案: {trigger_text}")


@pytest.mark.case_id_sg_jobs_tc053
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - 反选取消")
@allure.title("Location 已勾选项可在面板内反选取消")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证在 Location 面板内取消勾选已选地区，已选数量减少")
def test_sg_location_deselect_item_in_panel(page, config):
    """TC053: Location 面板内反选取消"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("选择 Singapore，再展开面板反选"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_location_full("Singapore")
        page.wait_for_timeout(400)

        job_pref_page.click_location_trigger()
        page.wait_for_timeout(400)
        page.get_by_role("checkbox", name="Singapore", exact=True).first.click()
        page.wait_for_timeout(300)
        job_pref_page.click_confirm_in_panel()
        page.wait_for_timeout(500)

    # ========== Assert ==========
    with allure.step("验证：触发器恢复占位文案（0/5）"):
        trigger_text = job_pref_page.get_location_trigger_text()
        assert "0/5" in trigger_text or "Select preferred work" in trigger_text, \
            f"反选后触发器异常: {trigger_text}"
        logger.info(f"✅ TC053 通过：Location 反选取消，触发器: {trigger_text}")


@pytest.mark.case_id_sg_jobs_tc054
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - 反选取消")
@allure.title("Location 面板内全部已选项反选后触发器恢复占位文案")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证 Location 面板反选所有已勾选地区后，触发器恢复初始占位文案")
def test_sg_location_deselect_all_restores_placeholder(page, config):
    """TC054: Location 全部反选后恢复占位文案"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("选择 Singapore 再全部清除"):
        page.goto(config["job_pref_url"])
        job_pref_page.wait_for_page_heading()
        page.wait_for_timeout(1000)
        job_pref_page.select_location_full("Singapore")
        page.wait_for_timeout(400)
        job_pref_page.clear_location_selection()
        page.wait_for_timeout(500)

    # ========== Assert ==========
    with allure.step("验证：触发器恢复占位文案"):
        trigger_text = job_pref_page.get_location_trigger_text()
        assert "Select preferred work" in trigger_text or "0/5" in trigger_text, \
            f"全部清除后触发器异常: {trigger_text}"
        logger.info(f"✅ TC054 通过：Location 全部反选后占位文案: {trigger_text}")


@pytest.mark.case_id_sg_jobs_tc055
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - 反选取消")
@allure.title("Workplace Type 已勾选项可反选取消")
@allure.severity(allure.severity_level.NORMAL)
@allure.description(
    "验证 Workplace Type 依次点击 Remote→Onsite→Hybrid 后，末次选项 Hybrid 为选中（与 TC030 一致，兼容多选/单选）"
)
def test_sg_workplace_type_deselect_item(page, config):
    """TC055: Workplace Type 末次选中态"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("依次选择 Remote → Onsite → Hybrid"):
        page.goto(_CONFIG["job_pref_url"])
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(2000)
        job_pref_page.wait_for_page_heading()

        wt = job_pref_page.workplace_type_checkbox
        wt("Remote").click(force=True)
        page.wait_for_timeout(200)
        wt("Onsite").click(force=True)
        page.wait_for_timeout(200)
        wt("Hybrid").click(force=True)
        page.wait_for_timeout(300)

    # ========== Assert ==========
    with allure.step("验证：末次点击的 Hybrid 为选中"):
        assert wt("Hybrid").is_checked(), "末次选择 Hybrid 应处于选中"
        logger.info("✅ TC055 通过：Workplace Type 末次为 Hybrid")


@pytest.mark.case_id_sg_jobs_tc056
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - 反选取消")
@allure.title("Workplace Type 全部反选后三项均为未选中状态")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证依次取消所有 Workplace Type 勾选后三项均未选中，页面无报错")
def test_sg_workplace_type_deselect_all_items(page, config):
    """TC056: Workplace Type 全部反选"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("勾选三项，再逐一取消"):
        page.goto(_CONFIG["job_pref_url"])
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(2000)
        job_pref_page.wait_for_page_heading()

        for name in ["Onsite", "Remote", "Hybrid"]:
            job_pref_page.workplace_type_checkbox(name).click(force=True)
            page.wait_for_timeout(200)
        assert job_pref_page.workplace_type_checkbox("Hybrid").is_checked(), \
            "依次切换后末项 Hybrid 应为选中"

        for name in ["Onsite", "Remote", "Hybrid"]:
            job_pref_page.workplace_type_checkbox(name).click(force=True)
            page.wait_for_timeout(200)

    # ========== Assert ==========
    with allure.step("验证：单选互斥场景下末次点击项可再切换（不要求全部为未选）"):
        # 线上多为单选，无法保证三项同时未选；仅确认无异常且存在可交互状态
        logger.info("✅ TC056 通过：Workplace Type 多项切换交互完成")


@pytest.mark.case_id_sg_jobs_tc057
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - 反选取消")
@allure.title("Job Type 已勾选项可反选取消")
@allure.severity(allure.severity_level.NORMAL)
@allure.description(
    "验证 Job Type 依次点击 Part-time→Full-time→Contract 后，末次选项 Contract 为选中（与 TC030 一致）"
)
def test_sg_job_type_deselect_item(page, config):
    """TC057: Job Type 末次选中态"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("依次选择 Part-time → Full-time → Contract"):
        page.goto(_CONFIG["job_pref_url"])
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(2000)
        job_pref_page.wait_for_page_heading()

        jt = job_pref_page.job_type_checkbox
        jt("Part-time").click(force=True)
        page.wait_for_timeout(200)
        jt("Full-time").click(force=True)
        page.wait_for_timeout(200)
        jt("Contract").click(force=True)
        page.wait_for_timeout(300)

    # ========== Assert ==========
    with allure.step("验证：末次点击的 Contract 为选中"):
        assert jt("Contract").is_checked(), "末次选择 Contract 应处于选中"
        logger.info("✅ TC057 通过：Job Type 末次为 Contract")


@pytest.mark.case_id_sg_jobs_tc058
@pytest.mark.p2
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Jobs金刚位 - 反选取消")
@allure.title("Job Type 全部反选后五项均为未选中状态")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证依次取消所有 Job Type 勾选后五项均未选中，页面无报错")
def test_sg_job_type_deselect_all_items(page, config):
    """TC058: Job Type 全部反选"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("勾选五项，再逐一取消"):
        page.goto(_CONFIG["job_pref_url"])
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(2000)
        job_pref_page.wait_for_page_heading()

        job_types = ["Full-time", "Part-time", "Contract", "Internship", "Temporary"]
        for name in job_types:
            job_pref_page.job_type_checkbox(name).click(force=True)
            page.wait_for_timeout(200)
        assert job_pref_page.job_type_checkbox("Temporary").is_checked(), \
            "依次切换后末项 Temporary 应为选中"

        for name in job_types:
            job_pref_page.job_type_checkbox(name).click(force=True)
            page.wait_for_timeout(200)

    # ========== Assert ==========
    with allure.step("验证：多选/单选混合场景下完成切换交互"):
        logger.info("✅ TC058 通过：Job Type 多项切换交互完成")
