"""
Marketplace Post 登录辅助函数

基于CLI录制过程中总结的登录流程变化规律

账号密码优先级（自动登录，按字段独立解析，`use_env=True` 时）：
1. 函数参数 phone / password（非空则优先于环境变量）
2. 环境变量 MARKETPLACE_TEST_PHONE、MARKETPLACE_TEST_PASSWORD（或 OK_TEST_*）
3. 内置默认值（仅本地兜底）

当 `use_env=False`（如 Marketplace 用例脚本强制使用 `_CONFIG['test_account']`）时：仅使用参数中的 phone/password，缺失则报错，不读环境变量与内置默认。
"""
from __future__ import annotations

import os
import re
import time

from playwright.sync_api import Locator, Page
from utils.logger import setup_logger

logger = setup_logger()

_DEFAULT_PHONE = "15038372881"
_DEFAULT_PASSWORD = "a123456"


def resolve_marketplace_credentials(
    phone: str | None = None,
    password: str | None = None,
    *,
    use_env: bool = True,
) -> tuple[str, str]:
    """解析手机号/邮箱与密码，供自动登录使用。

    use_env=True：每个字段独立为 显式参数（strip 非空）> 环境变量 > 内置默认。
    use_env=False：仅使用显式 phone 与 password，须二者均非空，否则抛出 ValueError。
    """
    sp = str(phone).strip() if phone else ""
    sw = str(password).strip() if password else ""
    if not use_env:
        if not sp or not sw:
            raise ValueError(
                "use_env=False 时必须在参数中提供非空的 phone 与 password（例如模块 _CONFIG['test_account']）"
            )
        return sp, sw
    p = sp or os.environ.get("MARKETPLACE_TEST_PHONE") or os.environ.get("OK_TEST_PHONE") or ""
    w = sw or os.environ.get("MARKETPLACE_TEST_PASSWORD") or os.environ.get("OK_TEST_PASSWORD") or ""
    if not p:
        p = _DEFAULT_PHONE
    if not w:
        w = _DEFAULT_PASSWORD
    return str(p).strip(), str(w)


def _try_switch_to_password_flow(page: Page) -> None:
    """SMS/验证码页上若存在「改用密码」类入口则点击。"""
    patterns = (
        r"use\s+password",
        r"log\s*in\s+with\s+password",
        r"password\s*login",
        r"使用密码",
        r"密码登录",
    )
    for pat in patterns:
        btn = page.get_by_role("button", name=re.compile(pat, re.I))
        if btn.count() > 0:
            try:
                btn.first.click(timeout=2500)
                page.wait_for_timeout(600)
                logger.info("✓ 已尝试切换到密码流程: %s", pat)
                return
            except Exception:
                pass
        link = page.get_by_text(re.compile(pat, re.I))
        if link.count() > 0:
            try:
                link.first.click(timeout=2500)
                page.wait_for_timeout(600)
                logger.info("✓ 已点击文案切换密码: %s", pat)
                return
            except Exception:
                pass


def _resolve_password_input(page: Page) -> Locator | None:
    """在主页面与各 iframe 内解析可见密码框。"""
    frames = [page.main_frame]
    frames.extend(f for f in page.frames if f is not page.main_frame)
    for fr in frames:
        locs = [
            fr.locator("input[type='password']"),
            fr.locator("input[autocomplete='current-password']"),
            fr.locator("input[name='password']"),
            fr.locator("input[placeholder='password']"),
            fr.locator("input[placeholder='Password']"),
        ]
        for loc in locs:
            try:
                if loc.count() == 0:
                    continue
                first = loc.first
                if first.is_visible():
                    return first
            except Exception:
                continue
    candidates_page = [
        page.get_by_placeholder(re.compile(r"password", re.I)),
        page.get_by_label(re.compile(r"password", re.I)),
    ]
    for loc in candidates_page:
        try:
            if loc.count() == 0:
                continue
            first = loc.first
            if first.is_visible():
                return first
        except Exception:
            continue
    return None


def _wait_for_password_input(page: Page, timeout_s: float = 28.0) -> Locator | None:
    """Continue 后轮询等待密码框（应对慢网与 SMS/密码双流程）。"""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        _try_switch_to_password_flow(page)
        pw = _resolve_password_input(page)
        if pw is not None:
            return pw
        page.wait_for_timeout(400)
    return None


def _click_log_in_submit(page: Page) -> None:
    """提交密码页：兼容 Log In / Log in（MCP 快照为 'Log in'）。"""
    patterns = (
        re.compile(r"^log\s*in$", re.I),
        "Log In",
        "Log in",
        "Sign in",
        "Submit",
    )
    for name in patterns:
        btn = page.get_by_role("button", name=name)
        try:
            if btn.count() > 0:
                btn.first.click(timeout=8000)
                return
        except Exception:
            continue
    raise Exception("未找到提交登录的按钮（Log in / Submit）")


def _fill_password_and_submit(page: Page, password: str) -> None:
    pw = _wait_for_password_input(page)
    if pw is None:
        logger.error("⚠️ 未找到密码输入框，可能是 SMS 验证流程")
        raise Exception("需要SMS验证码，无法自动化")
    pw.fill(password)
    page.wait_for_timeout(400)
    _click_log_in_submit(page)
    page.wait_for_timeout(3000)
    if not guest_welcome_visible(page):
        logger.info("✓ 登录成功，Modal已关闭")
    else:
        logger.error("❌ 登录失败，Modal未关闭")
        raise Exception("登录Modal未关闭")


def _fill_account_identifier(page: Page, account: str) -> None:
    """欢迎弹窗第一步：输入邮箱或手机号（MCP：textbox name='Email or phone number'）。"""
    factories = (
        lambda: page.get_by_role("textbox", name="Email or phone number"),
        lambda: page.get_by_label(re.compile(r"email\s+or\s+phone", re.I)),
        lambda: page.get_by_placeholder(re.compile(r"email|phone|number", re.I)),
        lambda: page.get_by_placeholder("Enter phone number"),
    )
    last_err: Exception | None = None
    for factory in factories:
        try:
            loc = factory()
            if loc.count() == 0:
                continue
            box = loc.first
            box.wait_for(state="visible", timeout=8000)
            box.fill(account)
            page.wait_for_timeout(350)
            logger.info("✓ 已填写账号（邮箱或手机）")
            return
        except Exception as e:
            last_err = e
            continue
    raise Exception(f"未找到账号输入框: {last_err}")


def _click_continue_if_enabled(page: Page) -> None:
    btn = page.get_by_role("button", name="Continue")
    try:
        btn.first.wait_for(state="visible", timeout=10000)
    except Exception as e:
        raise Exception("未找到 Continue 按钮") from e
    for _ in range(40):
        try:
            if btn.first.is_enabled():
                btn.first.click(timeout=5000)
                page.wait_for_timeout(500)
                return
        except Exception:
            pass
        page.wait_for_timeout(250)
    raise Exception("Continue 按钮长时间处于 disabled，请检查账号格式或页面状态")


def perform_marketplace_login(page: Page, phone=None, password=None, *, use_env: bool = True):
    """
    执行Marketplace Post页面登录
    
    支持两种登录流程：
    1. 密码登录（常见）
    2. SMS验证（偶发，无法自动化）
    
    从CLI录制学到：
    - 登录流程可能随机切换（密码/SMS）
    - SMS流程无法自动化，需要跳过或手动处理
    
    Args:
        page: Playwright Page对象
        phone: 手机号（默认使用CLI录制账号）
        password: 密码（默认使用CLI录制密码）
        use_env: 是否允许用环境变量/内置默认补齐账号（与 resolve_marketplace_credentials 一致）
    
    Raises:
        Exception: SMS验证流程或其他登录失败
    """
    phone, password = resolve_marketplace_credentials(phone, password, use_env=use_env)
    try:
        # 检查是否需要登录
        login_btn = page.get_by_role("button", name=re.compile(r"^log\s*in$", re.I))
        if login_btn.count() == 0:
            logger.info("✓ 已登录，跳过登录流程")
            return
        
        # 开始登录流程
        login_btn.first.click()
        page.wait_for_timeout(1000)
        
        _fill_account_identifier(page, phone)
        _click_continue_if_enabled(page)
        _fill_password_and_submit(page, password)
    
    except Exception as e:
        logger.error(f"登录失败: {e}")
        raise


def guest_welcome_visible(page: Page) -> bool:
    """访客欢迎层（需走账号密码）是否可见。与发布页「误判已登录」排查一致。"""
    try:
        w = page.get_by_text(re.compile(r"Welcome to OK", re.I))
        if w.count() == 0:
            return False
        return w.first.is_visible(timeout=2000)
    except Exception:
        return False


def needs_marketplace_publish_login(page: Page) -> bool:
    """
    当前页面是否仍处「未登录」发布态：
    - 顶部可见 Log In，或
    - 访客 Welcome 欢迎层可见（此时常无独立 Log In，易误判）。
    """
    try:
        login_btn = page.get_by_role("button", name=re.compile(r"^log\s*in$", re.I))
        if login_btn.count() > 0:
            try:
                if login_btn.first.is_visible(timeout=1200):
                    return True
            except Exception:
                return True
    except Exception:
        pass
    return guest_welcome_visible(page)


def _run_publish_password_login(
    page: Page,
    phone: str,
    password: str,
    *,
    use_env_credentials: bool,
) -> None:
    """在发布页执行欢迎层或顶部 Log In 密码登录（不负责 navigate）。"""
    if guest_welcome_visible(page):
        logger.info("检测到登录/欢迎 Modal，执行登录流程...")
        page.wait_for_timeout(500)
        _fill_account_identifier(page, phone)
        _click_continue_if_enabled(page)
        logger.info("已点击 Continue，轮询等待密码输入框（最长约 28s）...")
        _fill_password_and_submit(page, password)
        return
    if page.get_by_role("button", name=re.compile(r"^log\s*in$", re.I)).count() > 0:
        perform_marketplace_login(page, phone, password, use_env=use_env_credentials)


def ensure_logged_in_for_publish(
    page: Page,
    base_url: str,
    phone=None,
    password=None,
    *,
    use_env_credentials: bool = True,
) -> None:
    """
    若检测到未登录，自动完成 Marketplace 发布页密码登录；已登录则立即返回。

    适用于：用例中途掉登录、goto 后欢迎层再次出现、仅关 DOM 未补会话等场景。
    """
    phone, password = resolve_marketplace_credentials(
        phone, password, use_env=use_env_credentials
    )
    if not needs_marketplace_publish_login(page):
        return
    logger.info("检测到未登录，自动完成 Marketplace 发布页登录")
    _run_publish_password_login(
        page, phone, password, use_env_credentials=use_env_credentials
    )
    dismiss_stale_login_modal(page)
    if needs_marketplace_publish_login(page):
        logger.warning("首次自动登录后仍显示未登录态，刷新发布页后重试一次")
        navigate_to_publish_page(page, base_url)
        page.wait_for_timeout(2500)
        if needs_marketplace_publish_login(page):
            _run_publish_password_login(
                page, phone, password, use_env_credentials=use_env_credentials
            )
            dismiss_stale_login_modal(page)


def is_logged_in(page: Page) -> bool:
    """
    判断是否已登录（发布页上下文：无可见 Log In、无访客欢迎层）。
    """
    try:
        return not needs_marketplace_publish_login(page)
    except Exception as e:
        logger.error(f"检查登录状态失败: {e}")
        return False


def navigate_to_publish_page(page: Page, base_url: str):
    """
    导航到Marketplace发布页面
    
    两种方式：
    1. 直接URL（更快）
    2. 从首页导航（完整流程）
    """
    try:
        # 方式1: 直接URL（推荐）
        page.goto(f"{base_url}/biz/en/publish/classified", timeout=30000)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)
        
        logger.info("✓ 已导航到Marketplace发布页面")
    except Exception as e:
        logger.error(f"导航到发布页面失败: {e}")
        raise


def force_remove_login_pc_overlay(page: Page) -> None:
    """DOM 级移除 LoginPC 弹层；在 Close 无法命中或仍拦截点击时使用。

    线上常见仅残留 `LoginPC_loginModalPCBackdrop`（无 dialog），原逻辑在仍有其它
    `dialog.modal.show`（如 Draft Box）时不清 backdrop，会导致 Save the draft 整段被遮罩拦截。
    """
    try:
        page.evaluate(
            """() => {
  document.querySelectorAll('[role="dialog"]').forEach((el) => {
    const c = String(el.className || '');
    if (c.includes('LoginPC') || c.includes('loginModalPC')) {
      el.remove();
    }
  });
  document.querySelectorAll('.modal-backdrop, [class*="Backdrop"]').forEach((el) => {
    const c = String(el.className || '');
    if (c.includes('LoginPC') || c.includes('loginModalPC')) el.remove();
  });
  const shown = document.querySelectorAll('[role="dialog"].modal.show');
  if (shown.length === 0) {
    document.querySelectorAll('.modal-backdrop').forEach((el) => el.remove());
  }
  document.body.classList.remove('modal-open');
  if (document.body.style.overflow === 'hidden') {
    document.body.style.overflow = '';
  }
}"""
        )
    except Exception as e:
        logger.warning("DOM 移除 LoginPC 失败: %s", e)


def dismiss_stale_login_modal(page: Page) -> None:
    """关闭残留登录/欢迎弹层（不输入密码），避免误走 SMS 分支。

    线上常见 `LoginPC_loginModalPC___*` 等类名弹层，若仅用文案过滤可能匹配不到，
    会拦截底部「Save the draft」点击（Playwright 报 intercepts pointer events）。
    """
    close_selectors = (
        'button[aria-label="Close"]',
        "button.btn-close",
        ".modal-header button",
        'button[data-dismiss="modal"]',
    )

    def _try_close(locator: Locator) -> bool:
        if locator.count() == 0:
            return False
        try:
            box = locator.first
            if not box.is_visible():
                return False
        except Exception:
            return False
        for sel in close_selectors:
            try:
                b = box.locator(sel)
                if b.count() > 0:
                    b.first.click(timeout=2000)
                    return True
            except Exception:
                continue
        try:
            page.keyboard.press("Escape")
            return True
        except Exception:
            return False

    for _ in range(5):
        closed_any = False

        # 1) PC 登录弹层（类名含 LoginPC / loginModal，未必匹配下方文案正则）
        pc = page.locator(
            '[role="dialog"].modal.show[class*="LoginPC"], '
            '[role="dialog"][class*="loginModalPC"], '
            '[role="dialog"][class*="LoginPC_"]'
        )
        if pc.count() > 0:
            if _try_close(pc):
                closed_any = True

        # 2) 原：Welcome / Log In / 密码 / 验证码 等文案
        dlg = page.locator('[role="dialog"]').filter(
            has_text=re.compile(
                r"Welcome|Log\s*In|phone|password|验证码|Verify|Continue|OK\.com",
                re.I,
            )
        )
        if dlg.count() > 0:
            if _try_close(dlg):
                closed_any = True

        # 3) 兜底：任意仍可见的 modal 登录框（窄匹配，避免关 Draft Box）
        if not closed_any:
            narrow = page.locator('[role="dialog"].modal.show').filter(
                has_text=re.compile(r"log\s*in|sign\s*in|password|phone|verify", re.I)
            )
            if narrow.count() > 0 and _try_close(narrow):
                closed_any = True

        page.wait_for_timeout(350)
        if not closed_any:
            break

    # 4) LoginPC 仍拦截点击：force 点 Close / ESC，再 DOM 移除
    pc_left = page.locator(
        '[role="dialog"][class*="LoginPC"], [role="dialog"][class*="loginModalPC"]'
    )
    if pc_left.count() > 0:
        for sel in close_selectors:
            try:
                btn = pc_left.first.locator(sel)
                if btn.count() > 0:
                    btn.first.click(timeout=2000, force=True)
                    page.wait_for_timeout(300)
                    break
            except Exception:
                continue
        try:
            page.keyboard.press("Escape")
        except Exception:
            pass
        page.wait_for_timeout(200)
        if page.locator(
            '[role="dialog"][class*="LoginPC"], [role="dialog"][class*="loginModalPC"]'
        ).count() > 0:
            logger.warning("LoginPC 仍可见，执行 DOM 级移除遮罩")
            force_remove_login_pc_overlay(page)


def login_and_navigate_to_post_page(
    page: Page,
    base_url: str,
    phone=None,
    password=None,
    *,
    use_env_credentials: bool = True,
):
    """
    登录并导航到Marketplace发布页面（一站式）
    
    用于测试前置条件
    
    重要发现：页面可能以两种状态出现：
    1. 顶部有"Log In"按钮（未登录）
    2. 顶部无"Log In"按钮但有登录Modal（部分登录状态/cookie）
    
    账号密码：默认显式参数（非空）> 环境变量 > 内置默认。
    use_env_credentials=False 时仅使用传入的 phone/password（用于测试模块固定 _CONFIG['test_account']）。
    """
    phone, password = resolve_marketplace_credentials(
        phone, password, use_env=use_env_credentials
    )

    # 1. 导航
    navigate_to_publish_page(page, base_url)
    # 欢迎层异步渲染：若过早判断「无欢迎 + 无 Log In」会误判已登录并跳过密码流程
    page.wait_for_timeout(3000)

    # 1b. 快速路径：needs_marketplace_publish_login=False 且表单已就绪 → 有效会话（含 storage_state）
    try:
        if not needs_marketplace_publish_login(page):
            title_el = page.locator("#title")
            if title_el.count() > 0:
                title_el.first.wait_for(state="visible", timeout=8000)
                logger.info("✓ 已登录并进入发布页面（跳过 Modal 流程）")
                dismiss_stale_login_modal(page)
                return
    except Exception:
        pass

    # 2–3. 欢迎层或顶部 Log In：统一走密码登录（勿先 dismiss 欢迎层 DOM）
    if needs_marketplace_publish_login(page):
        logger.info("检测到未登录（访客欢迎层或 Log In），执行账号密码登录")
        _run_publish_password_login(
            page, phone, password, use_env_credentials=use_env_credentials
        )

    dismiss_stale_login_modal(page)
    # 兜底：中途失败、仅关弹层未补会话时再次检测并自动登录
    ensure_logged_in_for_publish(
        page, base_url, phone, password, use_env_credentials=use_env_credentials
    )
    logger.info("✓ 已登录并进入发布页面")
