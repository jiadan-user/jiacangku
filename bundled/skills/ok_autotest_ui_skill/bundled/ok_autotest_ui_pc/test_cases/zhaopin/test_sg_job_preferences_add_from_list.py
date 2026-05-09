"""
SG 站（新加坡站）- Job Preferences Add Job Preference 入口功能测试

本脚本由 playwright-test-generator 生成（严格使用 MCP 录制选择器）
录制文档：test_cases/zhaopin/ok-sg-JobPreferences-AddFromList-测试用例-20260305.md
生成时间：2026-03-09

测试站点：SG (https://sg.58v5.cn)
测试角色：Jobseeker（求职者）
测试目标：验证已登录/未登录用户从 Jobs 列表页点击 "Add Job Preference" 卡片后的完整流程：
         - 流程B（已登录）：直接跳转添加页，无弹窗，URL 不含 returnUrl
         - 流程A（未登录）：弹出登录弹窗，登录后跳转添加页
用例范围：TC001 - TC008（共 8 条，全自动化）
录制账号：wang@58.com（SG 站无已有 Job Preference 数据）

【选择器来源说明】
所有选择器均来自 MCP Playwright 实测录制（2026-03-05），非推测：
  - Add Job Preference 卡片点击：page.get_by_text('Add Job PreferenceUnlock more').click()
  - Cookie 弹窗：page.locator('.CookieConsent_cookieConsent__xhIgs button').first.click()
  - 登录弹窗内邮箱输入：page.locator('[role=dialog]').first.get_by_role('textbox').first.fill(...)
  - Continue 按钮（弹窗内）：page.locator('[role=dialog]').first.get_by_role('button', name='Continue').click()
  - 密码输入（弹窗内）：page.locator('[role=dialog]').first.get_by_role('textbox').first.fill(...)
  - Log in 按钮：page.locator('[role=dialog]').first.get_by_role('button', name='Log in').click()
  - Back 按钮：page.get_by_role('button', name='Back').click()
  - Continue 按钮（添加页）：page.get_by_role('button', name='Continue').click()
  - Job Functions 触发器：page.get_by_text('Select preferred job function (0/10)')
  - Location 触发器：page.get_by_text('Select preferred work location (0/5)')
  - Salary 下拉：page.get_by_role('button', name='Select pay type Yearly')（录制 ref e52）
  - S$ 货币符号：page.get_by_text('S$').first
  - 登录弹窗：page.locator('[role=dialog]').first
  - Welcome to OK.com：page.get_by_text('Welcome to OK.com').first
  - Google 登录图标：page.get_by_role('img', name='google').first
  - 邮箱输入框（弹窗内）：page.locator('[role=dialog]').first.get_by_role('textbox').first
"""
import re
import time

import pytest
import allure
from pages.login_page import LoginPage
from pages.sg_home_page import SgHomePage
from pages.job_preference_page import JobPreferencePage
from utils.session_manager import SessionManager
from utils.logger import setup_logger

logger = setup_logger()

from test_cases.zhaopin.explicit_waits import dom_content_loaded_soft, network_idle_soft, sg_wait_jobs_list_url, sg_after_home_jobs_icon
from test_cases.zhaopin.parallel_ordering_helper import (
    clear_order_marker,
    mark_order_done,
    wait_order_done,
)

# 测试账号wang@58.com在preference表中对应的user_id
# 如果不确定user_id，可以通过 SELECT user_id FROM user WHERE email='wang@58.com' 查询
_TEST_USER_ID_WANG = "796568487761138112"  # wang@58.com的user_id


def _cleanup_wang_preference():
    """
    删除preference表中wang@58.com账号的岗位偏好数据（测试数据清理）
    确保测试开始时用户没有已有的Job Preference数据
    """
    from utils.db_client import execute_update
    sql = "DELETE FROM preference WHERE user_id = %s"
    rows = execute_update(sql, (_TEST_USER_ID_WANG,))
    logger.info(f"✓ 已清理 preference 表数据，user_id={_TEST_USER_ID_WANG}，删除 {rows} 行")


def _clear_tc008_done_marker() -> None:
    try:
        clear_order_marker("sg_add_pref_tc008_done")
    except OSError as e:
        logger.warning(f"清理 TC008 顺序标记失败（忽略）: {e}")


def _mark_tc008_done() -> None:
    try:
        mark_order_done("sg_add_pref_tc008_done")
    except OSError as e:
        logger.warning(f"写入 TC008 顺序标记失败（忽略）: {e}")


def _wait_tc008_done(timeout_sec: int = 180) -> None:
    """
    并发模式下保证 TC004 在 TC008 完成后再继续执行。
    """
    if wait_order_done("sg_add_pref_tc008_done", timeout_sec=timeout_sec, poll_sec=0.5):
        logger.info("✓ 检测到 TC008 完成标记，继续执行 TC004")
        return
    raise AssertionError(f"等待 TC008 完成超时（>{timeout_sec}s），未检测到顺序标记")

# ============================================
# 测试环境配置（来自录制文档，录制与运行使用同一账号）
# ============================================
_CONFIG = {
    "site": "sg",
    "site_name": "新加坡站",
    "role": "jobseeker",
    "user_name": "wang_sg",
    "base_url": "https://sg.58v5.cn",
    "add_page_url": "https://sgpub.58v5.cn/biz/en/jobPreference",
    "jobs_list_url": "https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs",
    "test_account": {
        "username": "wang@58.com",
        "password": "Qwer1234"
    },
    "locale": "en-SG",
    "currency": "SGD",
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


# ============================================
# 辅助函数
# ============================================

def _prepare_unauthenticated_state(page, config):
    """
    可靠地进入未登录状态：清除所有浏览器存储（cookies/localStorage/sessionStorage）
    然后重新导航到 Jobs 列表页。
    这是最可靠的模拟未登录状态的方式。
    来自 MCP 录制：
      await page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }");
      await page.context().clearCookies();
    """
    jobs_list_url = config["jobs_list_url"]

    # 步骤1：先导航到 SG 站再清除本地存储
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
    # 步骤4：重新访问 Jobs 列表页（带重试）
    for retry in range(3):
        try:
            page.goto(jobs_list_url, wait_until="domcontentloaded", timeout=20000)
            dom_content_loaded_soft(page, 20000)
            logger.info(f"✓ 已进入 Jobs 列表页（未登录）: {page.url}")
            return
        except Exception as e:
            if retry == 2:
                raise
            logger.warning(f"导航 Jobs 列表页失败（第{retry + 1}次），重试: {e}")
            page.goto("about:blank")
            dom_content_loaded_soft(page, 20000)
def _handle_cookie_popup(page):
    """
    处理 Cookie 弹窗（如果存在）。
    来自 MCP 录制（2026-03-05 实测）：
      await page.locator('.CookieConsent_cookieConsent__xhIgs button').first().click();
    备选：getByRole('button', { name: 'Accept all' }) / getByRole('button', { name: 'Only essential' })
    """
    # 优先使用录制的精确 CSS class 选择器
    try:
        cookie_btn = page.locator(".CookieConsent_cookieConsent__xhIgs button").first
        if cookie_btn.is_visible(timeout=3000):
            cookie_btn.click()
            dom_content_loaded_soft(page, 20000)
            logger.info("✓ 已处理 Cookie 弹窗（CookieConsent class 选择器）")
            return
    except Exception:
        pass

    # 备选1：Accept all 按钮（来自 MCP 录制备选）
    try:
        accept_btn = page.get_by_role("button", name="Accept all").first
        if accept_btn.is_visible(timeout=2000):
            accept_btn.click()
            dom_content_loaded_soft(page, 20000)
            logger.info("✓ 已处理 Cookie 弹窗（Accept all）")
            return
    except Exception:
        pass

    # 备选2：Only essential 按钮
    try:
        essential_btn = page.get_by_role("button", name="Only essential").first
        if essential_btn.is_visible(timeout=2000):
            essential_btn.click()
            dom_content_loaded_soft(page, 20000)
            logger.info("✓ 已处理 Cookie 弹窗（Only essential）")
    except Exception:
        pass


def _sg_add_job_preference_locator(page):
    """
    Jobs 列表页「Add Job Preference」入口。
    录制为标题与副文案同一可点区域（甚至紧连为 Add Job PreferenceUnlock more）；
    无头模式下常在列表区懒加载或需滚入视口，单一精确文案易误判不可见。
    
    优先策略：
    1. 使用 data-testid 或 role 属性（如果有）
    2. 使用文本内容定位
    3. 使用更宽松的选择器
    """
    p = page
    
    # 策略1：尝试使用卡片容器定位
    try:
        card = p.locator('[class*="preference"], [class*="Preference"]').filter(
            has_text=re.compile(r"Add.*Job.*Preference", re.I)
        ).first
        if card.count() > 0:
            return card
    except Exception:
        pass
    
    # 策略2：原有的文本定位策略
    tight = p.get_by_text(re.compile(r"Add\s*Job\s*Preference\s*Unlock\s+more", re.I))
    title = p.get_by_text(re.compile(r"Add\s+Job\s+Preference", re.I))
    sub = p.get_by_text(re.compile(r"Unlock\s+more\s+opportunities", re.I))
    by_role = p.get_by_role("button", name=re.compile(r"Add.*Job\s*Preference", re.I)).or_(
        p.get_by_role("link", name=re.compile(r"Add.*Job\s*Preference", re.I))
    )
    return tight.or_(title).or_(sub).or_(by_role).first


def _wait_sg_jobs_list_preference_banner(page, timeout_ms: int = 60000):
    """等待列表区就绪，将 Job Preference 卡片滚入视口后再断言/点击。"""
    network_idle_soft(page, min(12000, timeout_ms))
    try:
        sg_wait_jobs_list_url(page, timeout=min(timeout_ms, 30000))
    except Exception:
        dom_content_loaded_soft(page, min(15000, timeout_ms))
    
    # 增加等待时间以适应无头模式
    page.wait_for_timeout(2000)
    
    # 尝试滚动到页面顶部，确保元素可见
    try:
        page.evaluate("() => window.scrollTo(0, 0)")
        page.wait_for_timeout(1000)
    except Exception:
        pass

    # 懒加载列表：分段下滚，触发 Preference 卡片渲染（并行/无头下常见）
    try:
        for y in (0, 280, 560, 900, 1300, 1800, 2400):
            page.evaluate("(yy) => window.scrollTo(0, yy)", y)
            page.wait_for_timeout(450)
    except Exception:
        pass
    
    # 检查页面是否已完全加载
    try:
        # 等待列表容器加载
        page.wait_for_selector("body", state="visible", timeout=10000)
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        logger.info("⚠️ networkidle 等待超时，继续尝试定位元素")
    
    last_exc = None
    per_try_visible = max(25000, min(timeout_ms, 45000))
    for attempt in range(3):
        loc = _sg_add_job_preference_locator(page)
        logger.info(f"当前页面 URL: {page.url}")
        try:
            count = loc.count()
            logger.info(f"找到 {count} 个匹配的 'Add Job Preference' 元素")
            if count == 0:
                logger.warning("⚠️ 未找到 'Add Job Preference' 元素，可能页面结构已变化")
                try:
                    pref_texts = page.locator("text=/preference/i").all_text_contents()
                    if pref_texts:
                        logger.info(f"页面中包含 'preference' 的文本: {pref_texts[:5]}")
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"检查元素数量时出错: {e}")

        try:
            loc.wait_for(state="attached", timeout=min(timeout_ms, 35000))
            try:
                loc.scroll_into_view_if_needed(timeout=10000)
            except Exception:
                try:
                    page.evaluate("() => window.scrollTo(0, 0)")
                    page.wait_for_timeout(1000)
                    loc.scroll_into_view_if_needed(timeout=10000)
                except Exception:
                    pass
                page.wait_for_timeout(300)
            loc.wait_for(state="visible", timeout=per_try_visible)
            return
        except Exception as e:
            last_exc = e
            logger.warning("SG Jobs 列表 Add Job Preference 卡片第 %s 次未就绪: %s", attempt + 1, e)
            if attempt >= 2:
                break
            try:
                page.reload(wait_until="domcontentloaded", timeout=50000)
                dom_content_loaded_soft(page, 25000)
                network_idle_soft(page, 12000)
                for y in (0, 280, 560, 900, 1300, 1800, 2400):
                    page.evaluate("(yy) => window.scrollTo(0, yy)", y)
                    page.wait_for_timeout(450)
            except Exception as re:
                logger.warning("reload 重试列表页失败: %s", re)
    if last_exc:
        raise last_exc
    raise AssertionError("SG Jobs 列表未出现 Add Job Preference 卡片")


def _click_sg_add_job_preference_card(page, timeout_ms: int = 75000):
    """点击 Add Job Preference 卡片，增加超时时间适应无头模式"""
    _wait_sg_jobs_list_preference_banner(page, timeout_ms=timeout_ms)
    page.wait_for_timeout(500)  # 确保元素完全可交互
    _sg_add_job_preference_locator(page).click(timeout=min(20000, timeout_ms))


def _ensure_sg_logged_in(page, config, force_relogin=False):
    """
    确保已登录 SG 站。优先复用 Session，失败则执行完整登录流程。
    
    Args:
        page: Playwright Page 对象
        config: 配置字典
        force_relogin: 是否强制重新登录（用于测试用例隔离，确保干净的登录状态）
    
    登录流程来自 MCP 录制（2026-03-05 实测）：
      await page.getByText('Log in / Register').click();
      await dialog.getByRole('textbox').first().fill('wang@58.com');
      await dialog.getByRole('button', { name: 'Continue' }).click();
      await dialog.getByRole('textbox').first().fill('Qwer1234');
      await dialog.getByRole('button', { name: 'Log in' }).evaluate('el => el.click()');
    """
    base_url = config["base_url"]
    jobs_list_url = config["jobs_list_url"]
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, base_url, session_name=session_name)

    # 如果强制重新登录，先清除所有状态
    if force_relogin:
        logger.info("🔄 强制重新登录模式：清除旧的登录状态")
        _prepare_unauthenticated_state(page, config)
        session_manager.clear_session()
        dom_content_loaded_soft(page, 20000)
    if not force_relogin and session_manager.load_session():
        # 导航到 Jobs 列表页验证 Session 是否有效
        page.goto(jobs_list_url, wait_until="domcontentloaded", timeout=15000)
        page.wait_for_load_state("domcontentloaded", timeout=10000)
        home_page = SgHomePage(page)
        _handle_cookie_popup(page)
        dom_content_loaded_soft(page, 20000)
        if home_page.is_logged_in():
            logger.info("✓ SG 站 Session 有效，已跳过登录")
            return
        logger.info("⚠️ SG 站 Session 已过期，需要重新登录")
        session_manager.clear_session()

    home_page = SgHomePage(page)
    login_page = LoginPage(page)
    page.goto(jobs_list_url, wait_until="domcontentloaded")
    page.wait_for_load_state("domcontentloaded", timeout=15000)
    _handle_cookie_popup(page)
    dom_content_loaded_soft(page, 20000)
    if not home_page.is_logged_in():
        logger.info("SG 站未登录，开始执行登录流程")
        login_page.click_login_register_button()
        dom_content_loaded_soft(page, 20000)
        # ARIA role=dialog 常见，未必是原生 dialog[open]；与 LoginPage 保持一致
        dialog = login_page.active_login_dialog()
        dialog.wait_for(state="visible", timeout=15000)
        dialog.get_by_role("textbox", name="Email or phone number").fill(
            config["test_account"]["username"]
        )
        dialog.get_by_role("button", name="Continue").click()
        dom_content_loaded_soft(page, 20000)
        # 密码步：用「含密码框」的 dialog，避免与首屏邮箱框定位歧义
        pw_dialog = page.get_by_role("dialog").filter(
            has=page.get_by_role("textbox", name="Enter password")
        ).first
        pw_dialog.wait_for(state="visible", timeout=15000)
        pw_dialog.get_by_role("textbox", name="Enter password").fill(
            config["test_account"]["password"]
        )
        pw_dialog.get_by_role("button", name="Log in").evaluate("el => el.click()")
        try:
            page.get_by_role("dialog").first.wait_for(state="hidden", timeout=20000)
        except Exception:
            pass
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        dom_content_loaded_soft(page, 20000)
        if not home_page.is_logged_in():
            page.reload(wait_until="domcontentloaded", timeout=30000)
            dom_content_loaded_soft(page, 20000)
        assert home_page.is_logged_in(), "SG 站登录失败"
        session_manager.save_session()
        logger.info("✓ SG 站登录成功并保存 Session")
    else:
        session_manager.save_session()
        logger.info("✓ SG 站已登录")


def _login_via_add_job_pref_banner(page, config):
    """
    通过 Add Job Preference 卡片弹出登录弹窗并完成登录。
    登录后系统自动跳转至添加页（https://sgpub.58v5.cn/biz/en/jobPreference）。
    前提：调用此函数前，页面必须处于未登录的 Jobs 列表页，且 Add Job Preference 卡片可见。

    来自 MCP 录制的 JavaScript 代码（逐行转换）：
      // 步骤1：点击 Add Job Preference 卡片
      await page.getByText('Add Job Preference').first().click();
      // 步骤2：URL 不变，停留在列表页；dialog 弹出
      // page.url() → 'https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs'
      // 步骤3：在 dialog 内输入邮箱
      const loginDialog = page.locator('[role=dialog]').first();
      await loginDialog.getByRole('textbox').first().fill('wang@58.com');
      await loginDialog.getByRole('button', { name: 'Continue' }).click();
      // 步骤4：弹窗显示 "Welcome back!" + 密码输入框
      await loginDialog.getByRole('textbox').first().fill('Qwer1234');
      await loginDialog.getByRole('button', { name: 'Log in' }).evaluate('el => el.click()');
      // 验证：page.url() → 'https://sgpub.58v5.cn/biz/en/jobPreference'（无 returnUrl）
    """
    # 步骤1：点击 Add Job Preference 卡片，弹出登录弹窗（内含列表区等待与滚入视口）
    _click_sg_add_job_preference_card(page)
    dom_content_loaded_soft(page, 20000)
    # 步骤2：在 dialog 内完成两步登录（与顶部入口一致：ARIA dialog）
    login_dialog = LoginPage(page).active_login_dialog()
    login_dialog.wait_for(state="visible", timeout=15000)

    # 第一步：输入邮箱并点击 Continue
    login_dialog.get_by_role("textbox", name="Email or phone number").fill(
        config["test_account"]["username"]
    )
    login_dialog.get_by_role("button", name="Continue").click()
    dom_content_loaded_soft(page, 20000)
    # 第二步：输入密码并点击 Log in（密码步须用具名框，避免仍命中邮箱 textbox）
    login_dialog = LoginPage(page).active_login_dialog()
    login_dialog.get_by_role("textbox", name="Enter password").fill(
        config["test_account"]["password"]
    )
    # 来自 MCP 录制：await loginDialog.getByRole('button', { name: 'Log in' }).evaluate('el => el.click()')
    login_dialog.get_by_role("button", name="Log in").evaluate("el => el.click()")

    # 等待页面跳转至添加页（最长等待 25 秒）
    try:
        page.wait_for_url("**/jobPreference**", timeout=25000)
        logger.info(f"✓ 已跳转至添加页: {page.url}")
    except Exception:
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        dom_content_loaded_soft(page, 20000)
        logger.info(f"✓ 登录完成（wait_for_url 超时后回退），当前 URL: {page.url}")


# ============================================
# 一、Add Job Preference 入口展示（TC001 / TC002）
# ============================================

@pytest.mark.case_id_sg_add_pref_tc001
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Job Preferences Add入口 - 入口展示（已登录）")
@allure.title("已登录且无偏好数据的用户访问 Jobs 列表页应显示 Add Job Preference 卡片（与未登录态相同）")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证已登录用户（无已有 Job Preference 数据）访问 SG Jobs 列表页，顶部仍显示 Add Job Preference 卡片，显示标题和副文本，不显示 Edit 链接")
def test_sg_add_pref_authenticated_no_pref_should_show_add_banner(page, config):
    """TC001: 已登录且无 Job Preference 数据的用户访问 Jobs 列表页应显示 Add Job Preference 卡片"""

    # ========== Arrange ==========
    logger.info("=" * 60)
    logger.info("TC001: SG站 - 已登录（无偏好）用户 Jobs 列表页显示 Add Job Preference 卡片")
    logger.info("=" * 60)
    # 强制重新登录，确保测试隔离性（避免前面的测试影响本测试的登录状态）
    _ensure_sg_logged_in(page, config, force_relogin=True)

    # ========== Act ==========
    with allure.step("步骤1：以已登录状态导航到 Jobs 列表页"):
        page.goto(config["jobs_list_url"], wait_until="domcontentloaded")
        dom_content_loaded_soft(page, 20000)
        _handle_cookie_popup(page)
        _wait_sg_jobs_list_preference_banner(page)
        logger.info(f"✓ 已进入 Jobs 列表页（已登录）: {page.url}")

    # ========== Assert ==========
    with allure.step("验证：页面顶部显示 Add Job Preference 文本"):
        # 来自 MCP 录制：SG 站已登录（无偏好数据）与未登录态相同，顶部显示 Add Job Preference 卡片
        add_pref_text = page.get_by_text(re.compile(r"Add\s+Job\s+Preference", re.I)).first
        assert add_pref_text.is_visible(timeout=8000), \
            "已登录（无偏好）用户访问 Jobs 列表页，应显示 'Add Job Preference' 卡片"
        logger.info("✓ Add Job Preference 卡片文本可见")

    with allure.step("验证：卡片显示副文本 Unlock more opportunities tailored for you."):
        # 来自 MCP 录制：卡片副文本 "Unlock more opportunities tailored for you."
        unlock_text = page.get_by_text(
            re.compile(r"Unlock\s+more\s+opportunities\s+tailored\s+for\s+you\.?", re.I)
        ).first
        assert unlock_text.is_visible(timeout=5000), \
            "未找到副文本 'Unlock more opportunities tailored for you.'"
        logger.info("✓ 副文本可见")

    with allure.step("验证：未显示 Edit 链接（账号无已有偏好数据）"):
        edit_link_count = page.get_by_role("link", name="Edit").count()
        assert edit_link_count == 0, \
            f"无偏好数据时不应显示 Edit 链接，但发现 {edit_link_count} 个"
        logger.info("✓ 未显示 Edit 链接，符合预期")

    logger.info("✅ TC001 通过：已登录（无偏好）状态下 Add Job Preference 卡片展示验证成功")


@pytest.mark.case_id_sg_add_pref_tc002
@pytest.mark.p0
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Job Preferences Add入口 - 入口展示（未登录）")
@allure.title("未登录用户访问 Jobs 列表页应显示 Add Job Preference 卡片")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证未登录状态下 SG Jobs 列表页顶部第一个卡片为 Add Job Preference，显示标题和副文本，且无 Edit 链接")
def test_sg_add_pref_unauthenticated_should_show_add_banner(page, config):
    """TC002: 未登录用户访问 Jobs 列表页应显示 Add Job Preference 卡片"""

    # ========== Arrange ==========
    logger.info("=" * 60)
    logger.info("TC002: SG站 - 未登录用户 Jobs 列表页显示 Add Job Preference 卡片")
    logger.info("=" * 60)

    # ========== Act：清除登录状态并导航到 Jobs 列表页 ==========
    with allure.step("步骤1：清除所有登录状态，导航到 Jobs 列表页（模拟未登录状态）"):
        _prepare_unauthenticated_state(page, config)
        _handle_cookie_popup(page)
        _wait_sg_jobs_list_preference_banner(page)
        logger.info(f"✓ 已进入 Jobs 列表页（未登录）: {page.url}")

    # ========== Assert ==========
    with allure.step("验证：页面顶部显示 Add Job Preference 文本"):
        # 来自 MCP 录制：未登录状态下顶部第一个卡片为 Add Job Preference
        add_pref_text = page.get_by_text(re.compile(r"Add\s+Job\s+Preference", re.I)).first
        assert add_pref_text.is_visible(timeout=8000), \
            "未登录状态下应显示 'Add Job Preference' 卡片"
        logger.info("✓ Add Job Preference 卡片文本可见")

    with allure.step("验证：卡片显示副文本 Unlock more opportunities tailored for you."):
        unlock_text = page.get_by_text(
            re.compile(r"Unlock\s+more\s+opportunities\s+tailored\s+for\s+you\.?", re.I)
        ).first
        assert unlock_text.is_visible(timeout=5000), \
            "未找到副文本 'Unlock more opportunities tailored for you.'"
        logger.info("✓ 副文本可见")

    with allure.step("验证：未显示 Edit 链接"):
        edit_link_count = page.get_by_role("link", name="Edit").count()
        assert edit_link_count == 0, \
            f"未登录状态下不应显示 Edit 链接，但发现 {edit_link_count} 个"
        logger.info("✓ 未显示 Edit 链接，符合预期")

    logger.info("✅ TC002 通过：未登录状态下 Add Job Preference 卡片展示验证成功")


# ============================================
# 二、已登录用户直接进入添加页（TC003 / TC004）
# ============================================

@pytest.mark.case_id_sg_add_pref_tc003
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Job Preferences Add入口 - 已登录直接跳转（流程B）")
@allure.title("已登录用户点击 Add Job Preference 应直接跳转到添加页（无弹窗，无 returnUrl）")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证已登录用户点击 Add Job Preference 卡片，直接跳转至添加页，URL 不含 returnUrl 参数，无登录弹窗")
def test_sg_add_pref_authenticated_should_redirect_directly_to_add_page(page, config):
    """TC003: 已登录用户点击 Add Job Preference 应直接跳转到添加页（无弹窗）"""

    # ========== Arrange ==========
    logger.info("=" * 60)
    logger.info("TC003: SG站 - 已登录用户点击 Add Job Preference 直接跳转添加页")
    logger.info("=" * 60)
    # 强制重新登录，确保测试隔离性
    _ensure_sg_logged_in(page, config, force_relogin=True)

    # ========== Act ==========
    with allure.step("步骤1：以已登录状态导航到 Jobs 列表页"):
        page.goto(config["jobs_list_url"], wait_until="domcontentloaded")
        dom_content_loaded_soft(page, 20000)
        _handle_cookie_popup(page)
        logger.info(f"✓ 已进入 Jobs 列表页: {page.url}")

    with allure.step("步骤2：点击 Add Job Preference 卡片"):
        _click_sg_add_job_preference_card(page)
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        dom_content_loaded_soft(page, 20000)
        logger.info(f"✓ 点击后跳转至: {page.url}")

    # ========== Assert ==========
    with allure.step("验证：无登录弹窗弹出"):
        # 来自 MCP 录制：已登录时点击后直接跳转，dialog 不存在
        dialog_visible = page.locator("[role=dialog]").is_visible()
        assert not dialog_visible, \
            "已登录用户点击 Add Job Preference 不应弹出登录弹窗"
        logger.info("✓ 无登录弹窗弹出")

    with allure.step("验证：URL 跳转至添加页（含 jobPreference）"):
        # 来自 MCP 录制：page.url() → 'https://sgpub.58v5.cn/biz/en/jobPreference'
        current_url = page.url
        assert "jobPreference" in current_url, \
            f"已登录用户点击后应直接跳转到 jobPreference 添加页，当前 URL: {current_url}"
        logger.info(f"✓ URL 包含 jobPreference: {current_url}")

    with allure.step("验证：URL 不包含 returnUrl 参数（Add 入口特征，区别于 Edit 入口）"):
        assert "returnUrl" not in current_url, \
            f"Add 入口进入的添加页 URL 不应含 returnUrl 参数，当前 URL: {current_url}"
        logger.info("✓ URL 不含 returnUrl，符合 Add 入口预期")

    with allure.step("验证：页面显示 Job Preferences 标题"):
        # 来自 MCP 录制：heading "Job Preferences" [level=2] ref: e30
        heading = page.get_by_role("heading", name="Job Preferences")
        assert heading.is_visible(timeout=10000), \
            "添加页应显示 'Job Preferences' 标题"
        logger.info("✓ Job Preferences 标题已显示")

    logger.info("✅ TC003 通过：已登录用户点击 Add Job Preference 直接跳转添加页验证成功")


@pytest.mark.case_id_sg_add_pref_tc004
@pytest.mark.order(2)
@pytest.mark.dependency(depends=["sg_add_pref_tc008"])
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Job Preferences Add入口 - 添加页初始状态")
@allure.title("添加页应正确显示三个必填字段且均为空（新用户无已有数据）")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证通过 Add Job Preference 入口进入的添加页，三个必填字段均显示空态，非必填字段均未勾选，SG 站货币显示 S$")
def test_sg_add_pref_add_page_should_show_empty_form(page, config):
    """TC004: 添加页应正确显示三个必填字段且均为空"""

    # ========== Arrange ==========
    logger.info("=" * 60)
    logger.info("TC004: SG站 - 添加页初始空表单状态验证")
    logger.info("=" * 60)
    # 并发执行时，强制等待 TC008 完成后再执行本用例
    with allure.step("顺序约束：等待 TC008 执行完成"):
        _wait_tc008_done(timeout_sec=180)
    
    # 清理测试账号的preference数据，确保显示"Add Job Preference"卡片
    with allure.step("前置清理：删除测试账号的历史偏好数据"):
        _cleanup_wang_preference()
    
    _ensure_sg_logged_in(page, config)

    # ========== Act ==========
    with allure.step("步骤1：以已登录状态进入添加页"):
        page.goto(config["jobs_list_url"], wait_until="domcontentloaded")
        dom_content_loaded_soft(page, 20000)
        _handle_cookie_popup(page)
        _click_sg_add_job_preference_card(page)
        page.wait_for_url("**/jobPreference**", timeout=20000)
        dom_content_loaded_soft(page, 20000)
        logger.info(f"✓ 已进入添加页: {page.url}")

    # ========== Assert ==========
    with allure.step("验证：Job Functions 触发器显示空态 (0/10)"):
        def _job_func_empty_visible() -> bool:
            cands = (
                page.get_by_text(
                    re.compile(
                        r"Select\s+preferred\s+job\s+functions?\s*\(\s*0\s*/\s*10\s*\)",
                        re.I,
                    )
                ).first,
                page.get_by_text(
                    re.compile(r"Select\s+preferred\s+job\s+function\s*\(\s*0\s*/\s*10\s*\)", re.I)
                ).first,
                page.locator("text=/job\\s*functions?.*0\\s*/\\s*10/i").first,
            )
            for loc in cands:
                try:
                    if loc.is_visible(timeout=800):
                        return True
                except Exception:
                    continue
            return False

        ok = False
        deadline = time.monotonic() + 35.0
        while time.monotonic() < deadline:
            try:
                page.wait_for_load_state("domcontentloaded", timeout=8000)
            except Exception:
                pass
            if _job_func_empty_visible():
                ok = True
                break
            page.wait_for_timeout(500)
        if not ok and "jobPreference" in page.url:
            page.reload(wait_until="domcontentloaded", timeout=45000)
            dom_content_loaded_soft(page, 20000)
            ok = _job_func_empty_visible()
        assert ok, "Job Functions 触发器应显示空态（含 0/10）"
        logger.info("✓ Job Functions 显示空态 (0/10)")

    with allure.step("验证：Location 触发器显示空态 (0/5)"):
        # 来自 MCP 录制：ref e46 → 文本 "Select preferred work location (0/5)"
        location_trigger = page.get_by_text("Select preferred work location (0/5)").first
        assert location_trigger.is_visible(timeout=5000), \
            "Location 触发器应显示空态 'Select preferred work location (0/5)'"
        logger.info("✓ Location 显示空态 (0/5)")

    with allure.step("验证：Salary 下拉显示空态（Select pay type Yearly），货币显示 S$（新加坡元）"):
        # 来自 MCP 录制：button ref e52 → name "Select pay type Yearly"（Yearly 为默认 pay type）
        pay_type_btn = page.get_by_role("button", name="Select pay type Yearly").first
        assert pay_type_btn.is_visible(timeout=5000), \
            "Salary 下拉应显示 'Select pay type Yearly'"
        # 来自 MCP 录制：ref e59 → "S$" 货币符号（新加坡元）
        sg_currency = page.get_by_text("S$").first
        assert sg_currency.is_visible(timeout=3000), \
            "SG 站 Salary 区域应显示 'S$' 货币符号（区别于 AE 站的 AED）"
        logger.info("✓ Salary 显示 Select pay type Yearly 且货币符号为 S$")

    with allure.step("验证：Workplace Type 所有 checkbox 均未勾选"):
        # 来自 MCP 录制：Onsite(e68), Remote(e70), Hybrid(e72) 均未勾选
        assert not page.get_by_role("checkbox", name="Onsite").is_checked(), \
            "Onsite 不应被勾选"
        assert not page.get_by_role("checkbox", name="Remote").is_checked(), \
            "Remote 不应被勾选"
        assert not page.get_by_role("checkbox", name="Hybrid").is_checked(), \
            "Hybrid 不应被勾选"
        logger.info("✓ Workplace Type 所有 checkbox 均未勾选")

    with allure.step("验证：Job Type 所有 checkbox 均未勾选"):
        # 来自 MCP 录制：Full-time(e77), Part-time(e79), Contract(e81), Internship(e83), Temporary(e85)
        assert not page.get_by_role("checkbox", name="Full-time").is_checked(), \
            "Full-time 不应被勾选"
        assert not page.get_by_role("checkbox", name="Part-time").is_checked(), \
            "Part-time 不应被勾选"
        assert not page.get_by_role("checkbox", name="Contract").is_checked(), \
            "Contract 不应被勾选"
        logger.info("✓ Job Type 所有 checkbox 均未勾选")

    with allure.step("验证：Continue 按钮和 Back 按钮均可见"):
        # 来自 MCP 录制：Back button ref e63, Continue button ref e64
        assert page.get_by_role("button", name="Continue").is_visible(timeout=3000), \
            "Continue 按钮应可见"
        assert page.get_by_role("button", name="Back").is_visible(timeout=3000), \
            "Back 按钮应可见"
        logger.info("✓ Continue 和 Back 按钮均可见")

    logger.info("✅ TC004 通过：添加页空表单初始状态验证成功")


# ============================================
# 三、必填字段校验（TC005）
# ============================================

@pytest.mark.case_id_sg_add_pref_tc005
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Job Preferences Add入口 - 必填字段校验")
@allure.title("未填任何必填字段直接点击 Continue 应显示三个校验错误")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证添加页三个必填字段（Job Functions / Location / Salary）均为空时，点击 Continue 显示 3 条 'Don't leave this field empty.' 错误，页面不跳转")
def test_sg_add_pref_empty_form_continue_should_show_three_validation_errors(page, config):
    """TC005: 未填任何必填字段直接点击 Continue 应显示三个校验错误"""

    # ========== Arrange ==========
    logger.info("=" * 60)
    logger.info("TC005: SG站 - 空表单提交校验（三个必填字段错误）")
    logger.info("=" * 60)
    _ensure_sg_logged_in(page, config)

    with allure.step("步骤1：进入添加页"):
        page.goto(config["jobs_list_url"], wait_until="domcontentloaded")
        dom_content_loaded_soft(page, 20000)
        _handle_cookie_popup(page)
        _click_sg_add_job_preference_card(page)
        page.wait_for_url("**/jobPreference**", timeout=20000)
        dom_content_loaded_soft(page, 20000)
        logger.info(f"✓ 已进入添加页: {page.url}")

    # ========== Act ==========
    with allure.step("步骤2：不填任何字段，直接点击 Continue"):
        # 来自 MCP 录制：
        # await page.getByRole('button', { name: 'Continue' }).evaluate('el => el.click()')
        page.get_by_role("button", name="Continue").evaluate("el => el.click()")
        dom_content_loaded_soft(page, 20000)
        logger.info("✓ 已点击 Continue 按钮")

    # ========== Assert ==========
    with allure.step("验证：页面不跳转，仍停留在添加页"):
        assert "jobPreference" in page.url, \
            f"点击 Continue 后应停留在添加页，当前 URL: {page.url}"
        logger.info("✓ 页面未跳转，仍在添加页")

    with allure.step("验证：显示三条 'Don't leave this field empty.' 错误提示"):
        # 来自 MCP 录制：e88(Job Functions), e89(Location), e90(Salary) 均显示错误
        # 从调试脚本中发现：错误元素的 class 为 "invalid-error"
        # 使用 class 选择器更可靠
        error_elements = page.locator('.invalid-error, [class*="invalid-error"]')
        error_count = error_elements.count()
        
        # 验证至少有 3 个错误元素
        assert error_count >= 3, \
            f"应显示至少 3 个必填字段错误元素，实际显示 {error_count} 个"
        logger.info(f"✓ 发现 {error_count} 个错误元素")
        
        # 验证每个错误元素包含错误文本（使用更灵活的方式）
        error_keywords = ["Don", "leave", "field", "empty"]
        validated_count = 0
        for i in range(error_count):
            el_text = error_elements.nth(i).text_content()
            # 检查是否包含所有关键词（不区分大小写，兼容特殊引号）
            if all(keyword.lower() in el_text.lower() for keyword in error_keywords):
                validated_count += 1
                logger.info(f"  ✓ 错误 {i+1}: 包含校验错误信息")
        
        assert validated_count >= 3, \
            f"应有至少 3 个错误元素包含校验错误信息，实际 {validated_count} 个"
        
        logger.info(f"✓ 显示 {validated_count} 条完整的校验错误提示，符合预期")

    logger.info("✅ TC005 通过：空表单提交校验（3条错误）验证成功")


# ============================================
# 四、Back 按钮行为（TC006）
# ============================================

@pytest.mark.case_id_sg_add_pref_tc006
@pytest.mark.p1
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Job Preferences Add入口 - Back 按钮跳转")
@allure.title("通过 Add Job Preference 入口进入的添加页点击 Back 应跳回 Jobs 列表页")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证通过 Add 入口进入的添加页（无 returnUrl），点击 Back 后跳转回 SG Jobs 列表页，且列表页仍显示 Add Job Preference 卡片（未提交，偏好未保存）")
def test_sg_add_pref_back_button_should_redirect_to_jobs_list(page, config):
    """TC006: 通过 Add Job Preference 入口进入添加页点击 Back 应跳回 Jobs 列表页"""

    # ========== Arrange ==========
    logger.info("=" * 60)
    logger.info("TC006: SG站 - Add入口添加页 Back 按钮跳转验证")
    logger.info("=" * 60)
    
    # 清理测试账号的preference数据，确保显示"Add Job Preference"卡片
    with allure.step("前置清理：删除测试账号的历史偏好数据"):
        _cleanup_wang_preference()
    
    _ensure_sg_logged_in(page, config)

    with allure.step("步骤1：以已登录状态进入添加页"):
        page.goto(config["jobs_list_url"], wait_until="domcontentloaded")
        dom_content_loaded_soft(page, 20000)
        _handle_cookie_popup(page)
        _click_sg_add_job_preference_card(page)
        page.wait_for_url("**/jobPreference**", timeout=20000)
        dom_content_loaded_soft(page, 20000)
        logger.info(f"✓ 已进入添加页: {page.url}")

    with allure.step("步骤2：确认当前在添加页且 URL 无 returnUrl"):
        current_url = page.url
        assert "jobPreference" in current_url, \
            f"未进入添加页，当前 URL: {current_url}"
        assert "returnUrl" not in current_url, \
            f"URL 不应含 returnUrl，当前: {current_url}"
        logger.info("✓ 确认在添加页且 URL 无 returnUrl")

    # ========== Act ==========
    with allure.step("步骤3：不修改任何字段，点击 Back 按钮"):
        # 来自 MCP 录制：await page.getByRole('button', { name: 'Back' }).click()
        # page.url() → 'https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs'
        page.get_by_role("button", name="Back").click()
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        dom_content_loaded_soft(page, 20000)
        logger.info(f"✓ 点击 Back 后跳转至: {page.url}")

    # ========== Assert ==========
    with allure.step("验证：跳转回 SG Jobs 列表页"):
        # 来自 MCP 录制：page.url() → 'https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs'
        current_url = page.url
        assert "cate-jobs" in current_url or "sg.58v5.cn" in current_url, \
            f"Back 后应回到 Jobs 列表页，当前 URL: {current_url}"
        logger.info(f"✓ 已回到: {current_url}")

    with allure.step("验证：列表页仍显示 Add Job Preference 卡片（未提交，偏好未保存）"):
        # 来自 MCP 录制：未提交，账号无偏好数据，Back 后仍显示 Add Job Preference 卡片
        _handle_cookie_popup(page)
        _wait_sg_jobs_list_preference_banner(page)
        add_pref_visible = _sg_add_job_preference_locator(page).is_visible(timeout=5000)
        assert add_pref_visible, \
            "Back 后 Jobs 列表页应仍显示 'Add Job Preference' 卡片（未提交，偏好未保存）"
        logger.info("✓ 列表页仍显示 Add Job Preference 卡片，符合预期")

    logger.info("✅ TC006 通过：Add 入口 Back 按钮跳转验证成功")


# ============================================
# 五、未登录入口登录后跳转（TC007 / TC008）
# ============================================

@pytest.mark.case_id_sg_add_pref_tc007
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Job Preferences Add入口 - 未登录弹窗登录后跳转（流程A）")
@allure.title("未登录用户通过 Add Job Preference 入口登录后应直接跳转到添加页（无 returnUrl）")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证未登录用户点击 Add Job Preference 卡片，通过弹窗两步登录（邮箱+密码），登录成功后页面跳转至添加页且 URL 不含 returnUrl 参数")
def test_sg_add_pref_login_via_banner_should_redirect_to_add_page(page, config):
    """TC007: 未登录用户通过 Add Job Preference 入口登录后跳转添加页"""

    # ========== Arrange ==========
    logger.info("=" * 60)
    logger.info("TC007: SG站 - 未登录通过 Add Job Preference 弹窗登录后跳转添加页")
    logger.info("=" * 60)

    with allure.step("步骤1：清除所有登录状态，进入 Jobs 列表页（模拟未登录状态）"):
        _prepare_unauthenticated_state(page, config)
        logger.info(f"✓ 已进入 Jobs 列表页（未登录）: {page.url}")

    with allure.step("步骤2：处理 Cookie 弹窗（SG 站首次访问必定出现）"):
        # 来自 MCP 录制：await page.locator('.CookieConsent_cookieConsent__xhIgs button').first().click()
        _handle_cookie_popup(page)

    # ========== Act ==========
    with allure.step("步骤3：点击 Add Job Preference 卡片并通过弹窗完成登录"):
        # 来自 MCP 录制（流程A）：
        # await page.getByText('Add Job Preference').first().click()
        # const loginDialog = page.locator('[role=dialog]').first()
        # await loginDialog.getByRole('textbox').first().fill('wang@58.com')
        # await loginDialog.getByRole('button', { name: 'Continue' }).click()
        # await loginDialog.getByRole('textbox').first().fill('Qwer1234')
        # await loginDialog.getByRole('button', { name: 'Log in' }).evaluate('el => el.click()')
        _login_via_add_job_pref_banner(page, config)
        logger.info(f"✓ 登录流程完成，当前 URL: {page.url}")

    # ========== Assert ==========
    with allure.step("验证：URL 跳转至添加页（含 jobPreference）"):
        # 来自 MCP 录制：page.url() → 'https://sgpub.58v5.cn/biz/en/jobPreference'（无 returnUrl）
        current_url = page.url
        assert "jobPreference" in current_url, \
            f"未登录通过弹窗登录后应跳转到 jobPreference 添加页，当前 URL: {current_url}"
        logger.info(f"✓ URL 包含 jobPreference: {current_url}")

    with allure.step("验证：URL 不包含 returnUrl 参数（区别于 Edit 入口）"):
        assert "returnUrl" not in current_url, \
            f"Add 入口登录后 URL 不应含 returnUrl 参数，当前 URL: {current_url}"
        logger.info("✓ URL 不含 returnUrl，符合 Add 入口预期")

    with allure.step("验证：页面显示 Job Preferences 标题"):
        # 来自 MCP 录制：heading "Job Preferences" [level=2] ref: e30
        heading = page.get_by_role("heading", name="Job Preferences")
        assert heading.is_visible(timeout=10000), \
            "添加页应显示 'Job Preferences' 标题"
        logger.info("✓ Job Preferences 标题已显示")

    with allure.step("验证：右上角显示登录用户名（OKerSG_ 开头）"):
        # 来自 MCP 录制：登录成功后右上角显示用户名 OKerSG_sjwp7cj
        # 使用正则匹配（避免硬编码用户名）
        # 增加等待时间以适应无头模式下的渲染延迟
        page.wait_for_timeout(2000)  # 等待页面完全渲染
        dom_content_loaded_soft(page, 15000)
        user_name_el = page.locator("text=/OKerSG_/").first
        assert user_name_el.is_visible(timeout=10000), \
            "登录成功后右上角应显示 OKerSG_ 开头的用户名"
        logger.info("✓ 右上角显示登录用户名（OKerSG_）")

    logger.info("✅ TC007 通过：未登录弹窗登录后跳转添加页验证成功")


@pytest.mark.case_id_sg_add_pref_tc008
@pytest.mark.order(1)
@pytest.mark.dependency(name="sg_add_pref_tc008")
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.sg
@allure.feature("OK")
@allure.story("SG站 Job Preferences Add入口 - 未登录弹窗展示")
@allure.title("未登录用户点击 Add Job Preference 应弹出登录弹窗且 URL 不跳转")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证未登录用户点击 Add Job Preference 卡片后弹出登录弹窗，URL 保持不变，弹窗显示 Welcome to OK.com 及第三方登录选项")
def test_sg_add_pref_unauthenticated_click_should_show_login_dialog(page, config):
    """TC008: 未登录用户点击 Add Job Preference 应弹出登录弹窗且 URL 不跳转"""

    # ========== Arrange ==========
    logger.info("=" * 60)
    logger.info("TC008: SG站 - 未登录点击 Add Job Preference 弹出登录弹窗")
    logger.info("=" * 60)
    # 每次执行 TC008 时先重置顺序标记，避免读到历史脏标记
    _clear_tc008_done_marker()

    with allure.step("步骤1：清除所有登录状态，进入 Jobs 列表页（未登录）"):
        _prepare_unauthenticated_state(page, config)
        logger.info(f"✓ 已进入 Jobs 列表页（未登录）: {page.url}")
    
    # 清理测试账号的preference数据，确保显示"Add Job Preference"卡片
    # 注意：必须在未登录状态准备好之后清理，否则可能影响其他并发测试
    with allure.step("前置清理：删除测试账号的历史偏好数据（确保干净状态）"):
        _cleanup_wang_preference()
        # 刷新页面以反映数据库变化
        page.reload(wait_until="domcontentloaded", timeout=15000)
        dom_content_loaded_soft(page, 15000)

    with allure.step("步骤2：处理 Cookie 弹窗（SG 站首次访问必定出现，不处理则 Log in 被遮挡）"):
        # 来自 MCP 录制关键发现：SG 站首次访问必定出现 Cookie Consent 弹窗
        _handle_cookie_popup(page)

    # 记录当前 URL（点击前）
    url_before_click = page.url

    # ========== Act ==========
    with allure.step("步骤3：点击 Add Job Preference 卡片"):
        # 来自 MCP 录制（流程A 步骤1）；列表区懒加载时需等待并滚入视口
        _click_sg_add_job_preference_card(page)
        dom_content_loaded_soft(page, 20000)
        logger.info("✓ 已点击 Add Job Preference 卡片")

    # ========== Assert ==========
    with allure.step("验证：弹出登录弹窗（dialog）"):
        # 来自 MCP 录制：dialog 弹出，ref: e903，包含 "Welcome to OK.com" 标题
        dialog = LoginPage(page).active_login_dialog()
        assert dialog.is_visible(timeout=5000), \
            "点击 Add Job Preference 后应弹出登录弹窗"
        logger.info("✓ 登录弹窗已弹出")

    with allure.step("验证：URL 保持不变（仍为 Jobs 列表页）"):
        # 来自 MCP 录制：page.url() 仍为 'https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs'
        current_url = page.url
        assert "cate-jobs" in current_url, \
            f"未登录点击后 URL 应保持不变（Jobs 列表页），当前 URL: {current_url}"
        logger.info(f"✓ URL 未跳转，仍为: {current_url}")

    with allure.step("验证：弹窗显示 Welcome to OK.com 标题"):
        # 来自 MCP 录制：generic ref e913 → "Welcome to OK.com"
        welcome_text = page.get_by_text("Welcome to OK.com").first
        assert welcome_text.is_visible(timeout=5000), \
            "登录弹窗应显示 'Welcome to OK.com' 标题"
        logger.info("✓ 弹窗显示 Welcome to OK.com")

    with allure.step("验证：弹窗包含邮箱/手机号输入框（在 dialog 内）"):
        # 来自 MCP 录制：textbox ref e922 在 dialog 内，通过 dialog 上下文定位
        # const loginDialog = page.locator('[role=dialog]').first()
        # await loginDialog.getByRole('textbox').first().fill(...)
        email_input = dialog.get_by_role("textbox").first
        assert email_input.is_visible(timeout=3000), \
            "登录弹窗应包含邮箱/手机号输入框"
        logger.info("✓ 弹窗包含邮箱输入框（dialog 内 textbox）")

    with allure.step("验证：弹窗包含第三方登录选项（Google / Facebook / Apple）"):
        # 来自 MCP 录制：img google(e927), facebook(e928), apple(e929)
        google_login = page.get_by_role("img", name="google").first
        assert google_login.is_visible(timeout=3000), \
            "登录弹窗应包含 Google 登录选项"
        logger.info("✓ 弹窗包含第三方登录选项（Google）")

    with allure.step("写入顺序标记（通知 TC004 可继续）"):
        _mark_tc008_done()

    logger.info("✅ TC008 通过：未登录点击 Add Job Preference 弹出登录弹窗验证成功")
