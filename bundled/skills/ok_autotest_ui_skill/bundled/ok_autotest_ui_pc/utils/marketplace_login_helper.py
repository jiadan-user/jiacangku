"""
Marketplace Post 登录辅助函数

基于CLI录制过程中总结的登录流程变化规律
"""
from __future__ import annotations

import re
import time

from playwright.sync_api import Locator, Page
from utils.logger import setup_logger

logger = setup_logger()


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


def _fill_password_and_submit(page: Page, password: str) -> None:
    pw = _wait_for_password_input(page)
    if pw is None:
        logger.error("⚠️ 未找到密码输入框，可能是 SMS 验证流程")
        raise Exception("需要SMS验证码，无法自动化")
    pw.fill(password)
    page.wait_for_timeout(400)
    submit_btn = page.get_by_role("button", name="Log In").or_(
        page.get_by_role("button", name="Submit")
    )
    submit_btn.click()
    page.wait_for_timeout(3000)
    if page.locator("text='Welcome to OK.com'").count() == 0:
        logger.info("✓ 登录成功，Modal已关闭")
    else:
        logger.error("❌ 登录失败，Modal未关闭")
        raise Exception("登录Modal未关闭")


def perform_marketplace_login(page: Page, phone="15038372881", password="a123456"):
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
    
    Raises:
        Exception: SMS验证流程或其他登录失败
    """
    try:
        # 检查是否需要登录
        login_btn = page.get_by_role("button", name="Log In")
        if login_btn.count() == 0:
            logger.info("✓ 已登录，跳过登录流程")
            return
        
        # 开始登录流程
        login_btn.click()
        page.wait_for_timeout(1000)
        
        # Step 1: 输入手机号
        phone_input = page.get_by_placeholder("Enter phone number")
        phone_input.wait_for(state="visible", timeout=5000)
        phone_input.fill(phone)
        page.wait_for_timeout(500)
        
        # Step 2: 点击Continue
        page.get_by_role("button", name="Continue").click()
        page.wait_for_timeout(800)
        _fill_password_and_submit(page, password)
    
    except Exception as e:
        logger.error(f"登录失败: {e}")
        raise


def is_logged_in(page: Page) -> bool:
    """
    判断是否已登录
    
    通过检查"Log In"按钮是否存在判断
    同时检查登录Modal是否存在
    """
    try:
        # 检查1: Log In按钮（顶部导航）
        login_btn_count = page.get_by_role("button", name="Log In").count()
        
        # 检查2: 登录Modal（可能已打开但未完成）
        modal_exists = page.locator("text='Welcome to OK.com'").count() > 0
        
        is_logged = (login_btn_count == 0) and (not modal_exists)
        
        if modal_exists:
            logger.warning("⚠️ 检测到登录Modal仍然存在，用户可能未完成登录")
        
        return is_logged
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
    """DOM 级移除 LoginPC 弹层；在 Close 无法命中或仍拦截点击时使用。"""
    try:
        page.evaluate(
            """() => {
  document.querySelectorAll('[role="dialog"]').forEach((el) => {
    const c = String(el.className || '');
    if (c.includes('LoginPC') || c.includes('loginModalPC')) {
      el.remove();
    }
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


def login_and_navigate_to_post_page(page: Page, base_url: str, phone="15038372881", password="a123456"):
    """
    登录并导航到Marketplace发布页面（一站式）
    
    用于测试前置条件
    
    重要发现：页面可能以两种状态出现：
    1. 顶部有"Log In"按钮（未登录）
    2. 顶部无"Log In"按钮但有登录Modal（部分登录状态/cookie）
    
    默认账号来自CLI录制时使用的测试账号
    """
    # 1. 导航
    navigate_to_publish_page(page, base_url)

    # 1b. 已登录且表单可用：直接返回（避免重复点登录进 SMS）
    try:
        title_el = page.locator("#title")
        if title_el.count() > 0 and page.get_by_role("button", name="Log In").count() == 0:
            title_el.first.wait_for(state="visible", timeout=8000)
            logger.info("✓ 已登录并进入发布页面（跳过 Modal 流程）")
            return
    except Exception:
        pass

    dismiss_stale_login_modal(page)
    try:
        if page.locator("#title").count() > 0 and page.get_by_role("button", name="Log In").count() == 0:
            page.locator("#title").first.wait_for(state="visible", timeout=8000)
            logger.info("✓ 关闭残留 Modal 后已登录")
            return
    except Exception:
        pass
    
    # 2. 检查是否有Welcome Modal（实际是登录Modal）
    welcome_modal = page.locator("text='Welcome to OK.com'")
    if welcome_modal.count() > 0:
        logger.info("检测到登录Modal，执行登录流程...")
        
        # Step 1: 输入手机号（通过label定位）
        page.wait_for_timeout(500)
        
        phone_input = page.get_by_label("Email or phone number")
        if phone_input.count() == 0:
            # 备选：尝试placeholder
            phone_input = page.get_by_placeholder("Enter phone number")
        
        if phone_input.count() > 0:
            phone_input.fill(phone)
            page.wait_for_timeout(500)
        else:
            logger.error("❌ 未找到手机号输入框")
            raise Exception("未找到手机号输入框")
        
        # Step 2: 点击Continue
        page.get_by_role("button", name="Continue").click()
        logger.info("已点击Continue，轮询等待密码输入框（最长约 28s）...")
        page.wait_for_timeout(500)
        _fill_password_and_submit(page, password)
    
    # 3. 兜底检查：如果还需要登录（顶部按钮方式）
    elif not is_logged_in(page):
        perform_marketplace_login(page, phone, password)
    
    logger.info("✓ 已登录并进入发布页面")
