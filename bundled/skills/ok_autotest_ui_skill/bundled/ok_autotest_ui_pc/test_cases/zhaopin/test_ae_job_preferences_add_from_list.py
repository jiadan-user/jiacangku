"""
AE 站（阿联酋站）- Job Preferences 未登录入口（Add Job Preference）测试

本脚本由 playwright-test-generator 生成
录制文档：test_cases/zhaopin/ok-ae-JobPreferences-AddFromList-测试用例-20260305.md
生成时间：2026-03-05

测试站点：AE (https://ae.58v5.cn)
测试目标：验证未登录用户从 Jobs 列表页点击 "Add Job Preference" 卡片，
         通过登录弹窗完成登录后跳转到 Job Preferences 编辑页的完整流程。
用例范围：TC001 - TC005（共 5 条，全自动化）
录制账号：wangyongli@58.com（已有 Job Preference 数据）
"""
import re

import pytest
import allure
from pages.login_page import LoginPage
from pages.sg_home_page import SgHomePage
from pages.job_preference_page import JobPreferencePage
from utils.session_manager import SessionManager
from utils.logger import setup_logger

logger = setup_logger()

from test_cases.zhaopin.explicit_waits import dom_content_loaded_soft, network_idle_soft, sg_wait_jobs_list_url, sg_after_home_jobs_icon

# ============================================
# 测试环境配置（来自录制文档，录制与运行使用同一账号）
# ============================================
_CONFIG = {
    "site": "ae",
    "site_name": "阿联酋站",
    "role": "jobseeker",
    "user_name": "wangyongli_ae",
    "base_url": "https://ae.58v5.cn",
    "edit_url": "https://aepub.58v5.cn/biz/en/jobPreference",
    "jobs_list_url": "https://ae.58v5.cn/en/city/cate-jobs/?iconSource=jobs",
    "test_account": {
        "username": "wangyongli@58.com",
        "password": "Qwer1234"
    },
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


def _expected_ae_jobs_list_url(config: dict) -> str:
    """AE Jobs 列表规范 URL（与产品默认一致，见 config jobs_list_url）。"""
    return config["jobs_list_url"].rstrip("/")


def _wait_then_assert_on_ae_jobs_list(page, config, action_label: str) -> None:
    """Back / Continue 后应落在 AE Jobs 列表页（与 jobs_list_url 完全一致）。"""
    try:
        page.wait_for_load_state("networkidle", timeout=30000)
    except Exception:
        pass
    page.wait_for_timeout(2000)
    expected = _expected_ae_jobs_list_url(config)
    actual = page.url.rstrip("/")
    assert actual == expected, (
        f"{action_label}后应回到 {expected}，当前 URL: {page.url}"
    )


def _assert_jobs_list_pref_bar_visible(page, job_pref_page: JobPreferencePage) -> None:
    """列表页动态区块渲染后再校验偏好栏 / Edit。"""
    try:
        page.wait_for_load_state("networkidle", timeout=25000)
    except Exception:
        pass
    page.wait_for_timeout(2000)
    edit_ok = job_pref_page.is_edit_link_visible()
    if not edit_ok:
        edit_ok = page.get_by_role("link", name="Edit").is_visible(timeout=12000)
    if not edit_ok:
        edit_ok = page.get_by_text("Edit").first.is_visible(timeout=5000)
    assert edit_ok, (
        "Jobs 列表页应显示 Job Preference 标签栏（含 Edit 链接）"
    )


# ============================================
# 辅助函数
# ============================================

def _do_logout(page):
    """
    执行注销操作（来自 MCP 录制）：
      await page.getByText('OKer_fm6gntd').click();   // 点击用户名展开菜单
      await page.getByText('Log Out').click();         // 点击 Log Out
    用户名格式通常为 OKer_ 开头，使用正则或 partial 文本匹配。
    """
    home = SgHomePage(page)
    if not home.is_logged_in():
        logger.info("✓ 当前已是未登录状态，无需注销")
        return

    logger.info("执行注销流程...")

    # 策略1：通过用户名文本（OKer_ 开头）点击展开菜单（来自 MCP 录制）
    try:
        # 找到包含 OKer 的用户名元素并点击
        user_name_el = page.locator("text=/OKer_/").first
        user_name_el.click()
        dom_content_loaded_soft(page, 20000)
        page.get_by_text("Log Out").click()
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        dom_content_loaded_soft(page, 20000)
        logger.info("✓ 注销成功（OKer_ 用户名点击方式）")
        return
    except Exception as e:
        logger.warning(f"OKer_ 匹配注销失败: {e}")

    # 策略2：直接尝试点击 Log Out（如果菜单已经打开）
    try:
        if page.get_by_text("Log Out").is_visible(timeout=2000):
            page.get_by_text("Log Out").click()
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            dom_content_loaded_soft(page, 20000)
            logger.info("✓ 注销成功（直接点击 Log Out）")
            return
    except Exception as e:
        logger.warning(f"直接点击 Log Out 失败: {e}")

    # 策略3：hover 顶部右侧用户区域
    try:
        page.locator("header").get_by_role("button").last.hover()
        dom_content_loaded_soft(page, 20000)
        page.get_by_text("Log Out").click()
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        dom_content_loaded_soft(page, 20000)
        logger.info("✓ 注销成功（header button hover 方式）")
        return
    except Exception as e:
        logger.warning(f"header button hover 注销失败: {e}")

    logger.warning("注销操作未能完成，继续执行")


def _ensure_ae_logged_in(page, config):
    """确保已登录 AE 站。优先复用 Session，失败则执行完整登录流程。"""
    base_url = config["base_url"]
    jobs_list_url = config["jobs_list_url"]
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, base_url, session_name=session_name)

    if session_manager.load_session():
        page.wait_for_load_state("domcontentloaded", timeout=10000)
        home_page = SgHomePage(page)
        home_page.handle_cookie_popup()
        dom_content_loaded_soft(page, 20000)
        if home_page.is_logged_in():
            logger.info("✓ AE 站 Session 有效，已跳过登录")
            return
        logger.info("⚠️ AE 站 Session 已过期，需要重新登录")
        session_manager.clear_session()

    home_page = SgHomePage(page)
    login_page = LoginPage(page)
    page.goto(jobs_list_url, wait_until="domcontentloaded")
    page.wait_for_load_state("domcontentloaded", timeout=15000)
    home_page.handle_cookie_popup()
    dom_content_loaded_soft(page, 20000)
    if not home_page.is_logged_in():
        logger.info("AE 站未登录，开始执行登录流程")
        login_page.click_login_register_button()
        dom_content_loaded_soft(page, 20000)
        login_page.input_email(config["test_account"]["username"])
        login_page.click_continue_button()
        dom_content_loaded_soft(page, 20000)
        login_page.input_password(config["test_account"]["password"])
        login_page.click_login_button()
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        dom_content_loaded_soft(page, 20000)
        assert home_page.is_logged_in(), "AE 站登录失败"
        session_manager.save_session()
        logger.info("✓ AE 站登录成功并保存 Session")
    else:
        session_manager.save_session()
        logger.info("✓ AE 站已登录")


def _prepare_unauthenticated_state(page, config):
    """
    可靠地进入未登录状态：清除所有浏览器存储（cookies/localStorage/sessionStorage）
    然后重新导航到 Jobs 列表页，验证 Add Job Preference 卡片可见。
    这是最可靠的模拟未登录状态的方式。
    """
    # 步骤1：先导航到 AE 站以便执行 JS 清除本地存储
    try:
        page.goto(config["base_url"], wait_until="domcontentloaded", timeout=15000)
        dom_content_loaded_soft(page, 20000)
        page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
    except Exception as e:
        logger.warning(f"清除本地存储时出现异常（忽略）: {e}")

    # 步骤2：清除浏览器上下文的所有 cookies（Playwright API）
    page.context.clear_cookies()
    logger.info("✓ 已清除所有 cookies 和本地存储")

    # 步骤3：先跳到空白页，再导航到目标，避免残留导航干扰
    page.goto("about:blank")
    dom_content_loaded_soft(page, 20000)
    # 步骤4：重新访问 Jobs 列表页（带重试），使用 networkidle 确保动态内容加载完成
    for retry in range(3):
        try:
            page.goto(config["jobs_list_url"], wait_until="networkidle", timeout=30000)
            # 额外等待确保动态内容渲染完成
            page.wait_for_timeout(2000)
            logger.info(f"✓ 已进入 Jobs 列表页（未登录）: {page.url}")
            return
        except Exception as e:
            if retry == 2:
                raise
            logger.warning(f"导航 Jobs 列表页失败（第{retry+1}次），重试: {e}")
            page.goto("about:blank")
            dom_content_loaded_soft(page, 20000)


def _ensure_ae_add_job_pref_banner_visible(page, timeout_ms: int = 25000) -> None:
    """Jobs 列表懒加载 + 全目录并行时，卡片可能需滚动后才进入视口。"""
    network_idle_soft(page, min(12000, timeout_ms))
    try:
        for y in (0, 280, 560, 900, 1300, 1800):
            page.evaluate("(yy) => window.scrollTo(0, yy)", y)
            page.wait_for_timeout(350)
    except Exception:
        pass
    page.get_by_text(re.compile(r"Add\s+Job\s+Preference", re.I)).first.wait_for(
        state="visible",
        timeout=timeout_ms,
    )


def _login_via_add_job_pref_banner(page, config):
    """
    通过 Add Job Preference 卡片弹出登录弹窗并完成登录。
    来自 MCP 录制的 JavaScript 代码（直接转换）：
      await page.getByText('Add Job PreferenceUnlock more').click();
      await page.getByRole('textbox', { name: 'Email or phone number' }).fill(...);
      await page.getByRole('button', { name: 'Continue' }).click();
      await page.getByRole('textbox', { name: 'Enter password' }).fill(...);
      await page.getByRole('button', { name: 'Log in' }).click();
    登录后系统自动跳转至编辑页（https://aepub.58v5.cn/biz/en/jobPreference）
    前提：调用此函数前，页面必须处于未登录的 Jobs 列表页，且 Add Job Preference 卡片可见。
    """
    login_page = LoginPage(page)
    # 验证前置条件：Add Job Preference 卡片可见
    _ensure_ae_add_job_pref_banner_visible(page, timeout_ms=25000)
    # 点击 Add Job Preference 卡片，弹出登录弹窗
    page.get_by_text("Add Job PreferenceUnlock more").click()
    dom_content_loaded_soft(page, 20000)
    # 第一步：输入邮箱并点击 Continue
    login_page.input_email(config["test_account"]["username"])
    login_page.click_continue_button()
    dom_content_loaded_soft(page, 20000)
    # 第二步：输入密码并点击 Log in
    login_page.input_password(config["test_account"]["password"])
    login_page.click_login_button()
    # 等待页面跳转至编辑页（最长等待 25 秒）
    try:
        page.wait_for_url("**/jobPreference**", timeout=25000)
        logger.info(f"✓ 已跳转至编辑页: {page.url}")
    except Exception:
        # 备选：等待页面加载完成
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        dom_content_loaded_soft(page, 20000)
        logger.info(f"✓ 登录完成（wait_for_url 超时后回退），当前 URL: {page.url}")


# ============================================
# 一、Add Job Preference 入口展示（TC001 / TC002）
# ============================================

@pytest.mark.case_id_ae_add_pref_tc001
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.ae
@allure.feature("OK")
@allure.story("AE站 Job Preferences Add入口 - 入口展示")
@allure.title("未登录用户访问 Jobs 列表页应在顶部显示 Add Job Preference 卡片")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证未登录状态下 Jobs 列表页顶部第一个卡片为 Add Job Preference，显示标题和副文本，且无 Edit 链接")
def test_ae_add_pref_unauthenticated_should_show_add_banner(page, config):
    """TC001: 未登录用户访问 Jobs 列表页应显示 Add Job Preference 卡片"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    home_page = SgHomePage(page)
    logger.info("=" * 60)
    logger.info("TC001: AE站 - 未登录用户 Jobs 列表页显示 Add Job Preference 卡片")
    logger.info("=" * 60)

    # ========== Act：清除登录状态并导航到 Jobs 列表页 ==========
    with allure.step("步骤1：清除所有登录状态，导航到 Jobs 列表页（模拟未登录状态）"):
        _prepare_unauthenticated_state(page, config)
        logger.info(f"✓ 已进入 Jobs 列表页（未登录）: {page.url}")

    # ========== Assert ==========
    with allure.step("验证：页面顶部显示 Add Job Preference 文本"):
        add_pref_card = page.get_by_text("Add Job Preference").first
        assert add_pref_card.is_visible(timeout=8000), \
            "未找到 'Add Job Preference' 文本，未登录状态下应显示该卡片"
        logger.info("✓ Add Job Preference 卡片文本可见")

    with allure.step("验证：卡片显示副文本 Unlock more opportunities"):
        unlock_text = page.get_by_text("Unlock more opportunities tailored for you.").first
        assert unlock_text.is_visible(timeout=5000), \
            "未找到副文本 'Unlock more opportunities tailored for you.'"
        logger.info("✓ 副文本可见")

    with allure.step("验证：未显示 Edit 链接"):
        # 未登录时不应有 Edit 链接
        edit_link_count = page.get_by_role("link", name="Edit").count()
        assert edit_link_count == 0, \
            f"未登录状态下不应显示 Edit 链接，但发现 {edit_link_count} 个"
        logger.info("✓ 未显示 Edit 链接，符合预期")

    logger.info("✅ TC001 通过：未登录状态下 Add Job Preference 卡片展示验证成功")


@pytest.mark.case_id_ae_add_pref_tc002
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("AE站 Job Preferences Add入口 - 入口展示")
@allure.title("已登录用户访问 Jobs 列表页不应显示 Add Job Preference 卡片而是显示 Job Preference 标签栏")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证已登录且有 Job Preference 数据的用户，Jobs 列表页顶部显示已选标签和 Edit 链接，不显示 Add Job Preference 卡片")
def test_ae_add_pref_authenticated_should_show_tag_bar_not_add_banner(page, config):
    """TC002: 已登录用户访问 Jobs 列表页应显示 Job Preference 标签栏"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    logger.info("=" * 60)
    logger.info("TC002: AE站 - 已登录用户 Jobs 列表页显示 Job Preference 标签栏")
    logger.info("=" * 60)
    _ensure_ae_logged_in(page, config)

    # ========== Act ==========
    with allure.step("步骤1：导航到 AE 站 Jobs 列表页"):
        page.goto(config["jobs_list_url"], wait_until="domcontentloaded")
        dom_content_loaded_soft(page, 20000)
        logger.info(f"✓ 已进入 Jobs 列表页: {page.url}")

    # ========== Assert ==========
    with allure.step("验证：不显示 Add Job Preference 卡片"):
        add_banner_visible = page.get_by_text("Add Job Preference").is_visible()
        assert not add_banner_visible, \
            "已登录状态下不应显示 'Add Job Preference' 卡片"
        logger.info("✓ 未显示 Add Job Preference 卡片，符合预期")

    with allure.step("验证：显示 Edit 链接（已有 Job Preference 数据）"):
        assert job_pref_page.is_visible("a:has-text('Edit')", timeout=8000) or \
               page.get_by_role("link", name="Edit").is_visible(), \
            "已登录且有 Job Preference 数据时应显示 Edit 链接"
        logger.info("✓ Edit 链接可见，符合预期")

    logger.info("✅ TC002 通过：已登录状态下标签栏展示验证成功")


# ============================================
# 二、登录成功后跳转到编辑页（TC003）
# ============================================

@pytest.mark.case_id_ae_add_pref_tc003
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.ae
@allure.feature("OK")
@allure.story("AE站 Job Preferences Add入口 - 核心登录流程")
@allure.title("未登录用户通过 Add Job Preference 入口登录后应直接跳转到编辑页（无 returnUrl 参数）")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证未登录用户点击 Add Job Preference 卡片，通过弹窗两步登录后，页面跳转至编辑页且 URL 不含 returnUrl 参数，已有数据正确回填")
def test_ae_add_pref_login_via_banner_should_redirect_to_edit_page(page, config):
    """TC003: 未登录用户通过 Add Job Preference 入口登录后跳转编辑页"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    home_page = SgHomePage(page)
    logger.info("=" * 60)
    logger.info("TC003: AE站 - Add Job Preference 入口登录后跳转编辑页")
    logger.info("=" * 60)

    with allure.step("步骤1：清除所有登录状态，进入 Jobs 列表页（模拟未登录状态）"):
        _prepare_unauthenticated_state(page, config)

    # ========== Act ==========
    with allure.step("步骤2：点击 Add Job Preference 卡片并完成登录"):
        _login_via_add_job_pref_banner(page, config)
        logger.info(f"✓ 登录流程完成，当前 URL: {page.url}")

    # ========== Assert ==========
    with allure.step("验证：URL 跳转至编辑页（含 jobPreference）"):
        current_url = page.url
        assert "jobPreference" in current_url, \
            f"登录后应跳转到 jobPreference 编辑页，当前 URL: {current_url}"
        logger.info(f"✓ URL 包含 jobPreference: {current_url}")

    with allure.step("验证：URL 不包含 returnUrl 参数（区别于 Edit 入口）"):
        current_url = page.url
        assert "returnUrl" not in current_url, \
            f"Add 入口登录后 URL 不应含 returnUrl 参数，当前 URL: {current_url}"
        logger.info("✓ URL 不含 returnUrl，符合 Add 入口预期")

    with allure.step("验证：页面显示 Job Preferences 标题"):
        job_pref_page.wait_for_page_heading()
        logger.info("✓ Job Preferences 标题已显示")

    with allure.step("验证：已有数据回填（Job Functions 触发器可见）"):
        assert job_pref_page.is_job_functions_trigger_visible(), \
            "Job Functions 触发器未显示，数据回填失败"
        logger.info("✓ Job Functions 触发器可见，数据已回填")

    logger.info("✅ TC003 通过：Add 入口登录后跳转编辑页验证成功")


# ============================================
# 三、Add 入口与 Edit 入口的差异（TC004 / TC005）
# ============================================

@pytest.mark.case_id_ae_add_pref_tc004
@pytest.mark.p1
@pytest.mark.ae
@allure.feature("OK")
@allure.story("AE站 Job Preferences Add入口 - 入口差异验证")
@allure.title("通过 Add Job Preference 入口进入编辑页点击 Back 应跳回 Jobs 列表页")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证通过 Add 入口进入的编辑页（无 returnUrl），点击 Back 后跳转回 AE Jobs 列表页，且列表页展示岗位偏好类目")
def test_ae_add_pref_back_button_should_redirect_to_jobs_list(page, config):
    """TC004: 通过 Add 入口进入编辑页点击 Back 应跳回 Jobs 列表页"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    home_page = SgHomePage(page)
    logger.info("=" * 60)
    logger.info("TC004: AE站 - Add入口编辑页 Back 按钮跳转验证")
    logger.info("=" * 60)

    # 注销再通过 Add 入口重新进入编辑页
    with allure.step("步骤1：清除所有登录状态，通过 Add 入口登录进入编辑页"):
        _prepare_unauthenticated_state(page, config)
        _login_via_add_job_pref_banner(page, config)
        logger.info(f"✓ 已进入编辑页: {page.url}")

    with allure.step("步骤2：确认当前在编辑页且 URL 无 returnUrl"):
        current_url = page.url
        assert "jobPreference" in current_url, \
            f"未进入编辑页，当前 URL: {current_url}"
        assert "returnUrl" not in current_url, \
            f"URL 不应含 returnUrl，当前: {current_url}"

    # ========== Act ==========
    with allure.step("步骤3：点击 Back 按钮"):
        job_pref_page.click_back()
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        dom_content_loaded_soft(page, 20000)
        logger.info(f"✓ 点击 Back 后跳转至: {page.url}")

    # ========== Assert ==========
    with allure.step("验证：跳转回 Jobs 列表页（默认 https://ae.58v5.cn/en/city/cate-jobs/?iconSource=jobs）"):
        _wait_then_assert_on_ae_jobs_list(page, config, "Back")
        logger.info(f"✓ 已回到: {page.url}")

    with allure.step("验证：列表页展示岗位偏好标签栏（已选类目可见）"):
        _assert_jobs_list_pref_bar_visible(page, job_pref_page)
        logger.info("✓ 列表页显示 Job Preference 标签栏，符合预期")

    logger.info("✅ TC004 通过：Add 入口 Back 按钮跳转验证成功")


@pytest.mark.case_id_ae_add_pref_tc005
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.ae
@allure.feature("OK")
@allure.story("AE站 Job Preferences Add入口 - 核心提交流程")
@allure.title("通过 Add Job Preference 入口完成编辑提交后应提交成功并跳转 Jobs 列表页")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证通过 Add 入口进入编辑页，已有回填数据，点击 Continue 后提交成功，跳转到 Jobs 列表页且显示岗位偏好类目")
def test_ae_add_pref_continue_should_submit_and_redirect_to_jobs_list(page, config):
    """TC005: 通过 Add 入口完成编辑提交后应跳转 Jobs 列表页"""

    # ========== Arrange ==========
    job_pref_page = JobPreferencePage(page)
    home_page = SgHomePage(page)
    logger.info("=" * 60)
    logger.info("TC005: AE站 - Add入口编辑页 Continue 提交验证")
    logger.info("=" * 60)

    # 注销再通过 Add 入口进入编辑页
    with allure.step("步骤1：清除所有登录状态，通过 Add 入口登录进入编辑页"):
        _prepare_unauthenticated_state(page, config)
        _login_via_add_job_pref_banner(page, config)
        logger.info(f"✓ 已进入编辑页: {page.url}")

    with allure.step("步骤2：确认编辑页已有回填数据"):
        job_pref_page.wait_for_page_heading()
        assert job_pref_page.is_job_functions_trigger_visible(), \
            "编辑页 Job Functions 触发器不可见，数据未回填"
        logger.info("✓ 编辑页已有回填数据")

    # ========== Act ==========
    with allure.step("步骤3：点击 Continue 提交"):
        job_pref_page.click_continue()
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        dom_content_loaded_soft(page, 20000)
        logger.info(f"✓ 点击 Continue 后跳转至: {page.url}")

    # ========== Assert ==========
    with allure.step("验证：提交成功，跳转到 Jobs 列表页（与 Back 一致，见 jobs_list_url）"):
        _wait_then_assert_on_ae_jobs_list(page, config, "Continue 提交")
        logger.info(f"✓ 已跳转到: {page.url}")

    with allure.step("验证：Jobs 列表页展示岗位偏好类目（Job Preference 标签可见）"):
        _assert_jobs_list_pref_bar_visible(page, job_pref_page)
        logger.info("✓ Jobs 列表页显示 Job Preference 标签栏，提交成功")

    logger.info("✅ TC005 通过：Add 入口 Continue 提交并跳转验证成功")
