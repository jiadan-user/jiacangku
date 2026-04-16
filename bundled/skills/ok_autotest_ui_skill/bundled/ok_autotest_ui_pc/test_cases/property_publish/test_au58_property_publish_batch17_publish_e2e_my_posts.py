"""
AU58 - 批次17：模块9 TC006 端到端发布成功并在「我的发布」可见

文档：test_plans/au58-Property-房产发布功能测试用例.md — 模块9-TC006

说明：真实点击 Post 会创建线上帖子；请在可接受环境运行。失败时检查账号权限、必填项与审核策略。
"""

from __future__ import annotations

import os
import re
import time
import pytest
import allure
from pathlib import Path

from pages.login_page import LoginPage
from pages.property_publish_page import PropertyPublishPage
from utils.session_manager import SessionManager
from utils.logger import setup_logger

logger = setup_logger()

_ROOT = Path(__file__).resolve().parents[2]
_IMG1 = _ROOT / "test_data" / "images" / "apartment_1.png"

_CONFIG = {
    "site": "au",
    "site_name": "澳洲站",
    "role": "seller",
    "user_name": "au_seller_liuyue",
    "base_url": "https://au.58v5.cn",
    "publish_url": "https://aupub.58v5.cn/biz/en",
    "test_account": {
        "username": "liuyue62@58.com",
        "password": "Xindemima1%",
    },
    "locale": "en-AU",
    "currency": "AUD",
    "browser": {
        "type": "chromium",
        "headless": True if os.getenv("CI") else False,
        "viewport": {"width": 1920, "height": 1080},
    },
    "timeout": {
        "default": 30000,
        "wait": 10000,
        "navigation": 60000,
    },
}


def _goto_with_retry(page, url: str, config, *, attempts: int = 3) -> None:
    nav_timeout = config["timeout"]["navigation"]
    last_err: BaseException | None = None
    for i in range(attempts):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=nav_timeout)
            return
        except BaseException as e:
            last_err = e
            logger.warning("goto 重试 %s/%s %s — %s", i + 1, attempts, url, e)
            if i < attempts - 1:
                page.wait_for_timeout(1500 * (i + 1))
    raise last_err  # type: ignore[misc]


def _ensure_logged_in(page, config) -> None:
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config["base_url"], session_name)
    login_page = LoginPage(page)
    if session_manager.load_session():
        logger.info("✓ Session 已加载")
    else:
        login_page.navigate_to_home_page(config["base_url"])
        login_page.handle_cookie_popup()
        login_page.login(
            config["test_account"]["username"],
            config["test_account"]["password"],
        )
        session_manager.save_session()
        logger.info("✓ 登录并保存 Session")


def _open_property_rent_house_form(page, config) -> PropertyPublishPage:
    front = f"{config['publish_url']}/publish/front"
    _goto_with_retry(page, front, config)
    page.wait_for_timeout(2000)
    try:
        btn = page.get_by_role("button", name="Accept all").first
        if btn.is_visible(timeout=2000):
            btn.click()
            page.wait_for_timeout(500)
    except Exception:
        pass
    rent = page.get_by_text("Property For Rent", exact=True)
    if rent.is_visible(timeout=8000):
        rent.click()
        page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
        page.wait_for_timeout(2000)
        if page.get_by_text("House", exact=False).first.is_visible(timeout=3000):
            page.get_by_text("House").first.click()
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_timeout(2000)
    else:
        _goto_with_retry(
            page,
            f"{config['publish_url']}/publish/property?categoryId=9",
            config,
        )
        page.wait_for_timeout(3000)
    return PropertyPublishPage(page)


def _accept_cookies(page, timeout_ms: int = 2000) -> None:
    try:
        btn = page.get_by_role("button", name=re.compile(r"Accept all", re.I)).first
        if btn.is_visible(timeout=timeout_ms):
            btn.click()
            page.wait_for_timeout(500)
    except Exception:
        pass


def _all_frames(page):
    """返回所有未被 detach 的 frame（主 frame 在前）。"""
    result = []
    for fr in page.frames:
        try:
            _ = fr.url  # 若 frame 已 detached 会抛异常
            result.append(fr)
        except Exception:
            pass
    return result


def _scroll_in_frame(fr, page) -> None:
    """在 frame 内向下滚动，兼容 iframe 和主 frame。"""
    try:
        fr.evaluate("() => window.scrollBy(0, 600)")
    except Exception:
        try:
            page.mouse.wheel(0, 600)
        except Exception:
            pass


def _fill_title_and_intro(page, title: str, intro: str) -> None:
    """用 JS 填写 Title input 和 Description textarea（React-friendly）。"""
    # 先滚到顶让 Title 区域可见
    page.evaluate("() => window.scrollTo(0, 0)")
    page.wait_for_timeout(500)

    # 填 Title（找 label="Title" 旁边的 input）
    _js_fill_near_label(page, "Title", title)
    page.wait_for_timeout(300)

    # 填 Description / intro（找任意 textarea）
    page.evaluate(
        """(intro) => {
            function run(doc) {
                for (const ta of doc.querySelectorAll('textarea')) {
                    const v = ta.value || '';
                    if (v.length < 10) {
                        const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
                        nativeSetter.call(ta, intro);
                        ta.dispatchEvent(new Event('input', {bubbles: true}));
                        ta.dispatchEvent(new Event('change', {bubbles: true}));
                        return;
                    }
                }
            }
            run(document);
            for (const f of document.querySelectorAll('iframe')) {
                try { if (f.contentDocument) run(f.contentDocument); } catch(e) {}
            }
        }""",
        intro,
    )
    page.wait_for_timeout(300)


def _js_click_exact_text(page, text: str) -> bool:
    """用 JS 在全页（含 iframe）找文本完全匹配的可见叶子元素并点击。"""
    try:
        return bool(page.evaluate(
            """(text) => {
                function tryClick(doc) {
                    const all = doc.querySelectorAll('button, span, div, label, a, li');
                    for (const el of all) {
                        if (el.children.length === 0 && el.textContent.trim() === text) {
                            const rect = el.getBoundingClientRect();
                            if (rect.width > 0 && rect.height > 0) {
                                el.click(); return true;
                            }
                        }
                    }
                    return false;
                }
                if (tryClick(document)) return true;
                for (const fr of document.querySelectorAll('iframe')) {
                    try { if (fr.contentDocument && tryClick(fr.contentDocument)) return true; } catch(e) {}
                }
                return false;
            }""",
            text,
        ))
    except Exception:
        return False


def _js_fill_near_label(page, label_text: str, value: str) -> bool:
    """用 JS 找 label_text 旁边的 input 并填值（React-friendly 触发）。"""
    try:
        return bool(page.evaluate(
            """([label, value]) => {
                function nativeInputValueSetter(inp, val) {
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    nativeInputValueSetter.call(inp, val);
                    inp.dispatchEvent(new Event('input', {bubbles: true}));
                    inp.dispatchEvent(new Event('change', {bubbles: true}));
                }
                function tryFill(doc) {
                    const candidates = doc.querySelectorAll('label, span, div, p, th, td');
                    for (const el of candidates) {
                        if (el.children.length === 0 && el.textContent.trim() === label) {
                            let parent = el.parentElement;
                            for (let i = 0; i < 6 && parent; i++, parent = parent.parentElement) {
                                const inp = parent.querySelector('input:not([type=hidden]):not([type=file]):not([type=checkbox]):not([type=radio])');
                                if (inp) {
                                    nativeInputValueSetter(inp, value);
                                    return true;
                                }
                            }
                        }
                    }
                    return false;
                }
                if (tryFill(document)) return true;
                for (const fr of document.querySelectorAll('iframe')) {
                    try { if (fr.contentDocument && tryFill(fr.contentDocument)) return true; } catch(e) {}
                }
                return false;
            }""",
            [label_text, value],
        ))
    except Exception:
        return False


def _try_fill_price_beds_address(page) -> None:
    """用 JS 填写全部必填字段。先整体滚动保证所有字段已渲染，再逐一操作。"""
    # 整体向下再向上滚动，让懒加载字段全部渲染
    for _ in range(8):
        page.mouse.wheel(0, 500)
        page.wait_for_timeout(150)
    page.evaluate("() => window.scrollTo(0, 0)")
    page.wait_for_timeout(600)

    # ---------- 价格：找第一个空 number input ----------
    for fr in _all_frames(page):
        try:
            for sel in ("input[type='number']", "input[inputmode='decimal']", "input[inputmode='numeric']"):
                loc = fr.locator(sel)
                cnt = loc.count()
                for i in range(min(cnt, 12)):
                    el = loc.nth(i)
                    try:
                        if el.is_visible(timeout=300) and not (el.input_value() or "").strip():
                            el.scroll_into_view_if_needed(timeout=3000)
                            el.fill("450")
                            page.wait_for_timeout(200)
                            break
                    except Exception:
                        continue
        except Exception:
            continue

    page.wait_for_timeout(300)

    # ---------- rental-type: Entire Unit ----------
    _js_click_exact_text(page, "Entire Unit")
    page.wait_for_timeout(300)

    # ---------- Beds: 1 ----------
    # JS 找 Beds 容器内的 "1"
    page.evaluate(
        """() => {
            function run(doc) {
                for (const el of doc.querySelectorAll('*')) {
                    if (/^Beds?$/.test((el.textContent || '').trim()) && el.children.length === 0) {
                        let p = el.parentElement;
                        for (let i = 0; i < 4 && p; i++, p = p.parentElement) {
                            for (const b of p.querySelectorAll('button, span, div, label')) {
                                if (b.children.length === 0 && b.textContent.trim() === '1') {
                                    b.click(); return;
                                }
                            }
                        }
                    }
                }
            }
            run(document);
            for (const f of document.querySelectorAll('iframe')) {
                try { if (f.contentDocument) run(f.contentDocument); } catch(e) {}
            }
        }"""
    )
    page.wait_for_timeout(300)

    # ---------- Bathrooms: 1 ----------
    page.evaluate(
        """() => {
            function run(doc) {
                for (const el of doc.querySelectorAll('*')) {
                    if (/^Bathrooms?$/.test((el.textContent || '').trim()) && el.children.length === 0) {
                        let p = el.parentElement;
                        for (let i = 0; i < 4 && p; i++, p = p.parentElement) {
                            for (const b of p.querySelectorAll('button, span, div, label')) {
                                if (b.children.length === 0 && b.textContent.trim() === '1') {
                                    b.click(); return;
                                }
                            }
                        }
                    }
                }
            }
            run(document);
            for (const f of document.querySelectorAll('iframe')) {
                try { if (f.contentDocument) run(f.contentDocument); } catch(e) {}
            }
        }"""
    )
    page.wait_for_timeout(300)

    # ---------- Floor ----------
    # 策略：先点 One Level，再填隐藏 input（如果出现），同时兜底直接填 number input
    _js_click_exact_text(page, "One Level")
    page.wait_for_timeout(600)
    # 点击 One Level 后，找 Floor section 内所有 number/text input 填 1
    for fr in _all_frames(page):
        try:
            # 找包含 "Floor" 文字的容器
            floor_containers = fr.locator("div, section, fieldset").filter(
                has=fr.get_by_text(re.compile(r"^Floor$", re.I))
            )
            cnt = floor_containers.count()
            for ci in range(min(cnt, 5)):
                c = floor_containers.nth(ci)
                try:
                    # 找里面的 input
                    for sel in ("input[type='number']", "input[inputmode='decimal']", "input[type='text']"):
                        inps = c.locator(sel)
                        ic = inps.count()
                        for ii in range(min(ic, 5)):
                            inp = inps.nth(ii)
                            try:
                                if inp.is_visible(timeout=400):
                                    inp.fill("1")
                                    page.wait_for_timeout(200)
                                    break
                            except Exception:
                                continue
                except Exception:
                    continue
        except Exception:
            continue
    page.wait_for_timeout(300)

    # ---------- Area Size: 100 ----------
    _js_fill_near_label(page, "Area Size", "100")
    page.wait_for_timeout(300)

    # ---------- 地址 ----------
    for fr in _all_frames(page):
        try:
            addr = fr.get_by_placeholder(re.compile(r"address|location|street", re.I)).first
            if not addr.is_visible(timeout=800):
                addr = fr.get_by_role("textbox", name=re.compile(r"address|location", re.I)).first
            if addr.is_visible(timeout=800):
                addr.scroll_into_view_if_needed(timeout=5000)
                addr.fill("1 George St")
                page.wait_for_timeout(1400)
                opts = page.get_by_role("option")
                if opts.count() >= 1 and opts.first.is_visible(timeout=5000):
                    opts.first.click()
                    page.wait_for_timeout(800)
                    break
                addr.fill("")
                addr.fill("Canberra")
                page.wait_for_timeout(1200)
                opt = page.locator("[role='option'], .ant-select-item, li").filter(
                    has_text=re.compile(r"Canberra", re.I)
                ).first
                if opt.is_visible(timeout=4000):
                    opt.click()
                    page.wait_for_timeout(800)
                    break
        except Exception:
            continue


def _wait_publish_success_or_fail(page, *, timeout_ms: int = 120000) -> bool:
    """返回 True 表示观察到成功类反馈；False 表示未识别（由调用方结合 URL 判断）。"""
    deadline = time.monotonic() + timeout_ms / 1000.0
    while time.monotonic() < deadline:
        try:
            body = page.evaluate("() => document.body.innerText || ''") or ""
        except Exception as e:
            # 页面导航跳转会销毁执行上下文，通常意味着发布成功跳转
            if "navigation" in str(e).lower() or "context" in str(e).lower() or "destroyed" in str(e).lower():
                page.wait_for_timeout(2000)
                return True
            body = ""
        if re.search(
            r"published\s+successfully|post\s+success|successfully\s+posted|"
            r"listing\s+(is\s+)?live|submitted\s+successfully|发布成功|已发布",
            body,
            re.I,
        ):
            return True
        for sel in (".ant-message-success", ".ant-message-notice-success", "[class*='toast'][class*='success']"):
            el = page.locator(sel).first
            try:
                if el.is_visible(timeout=400):
                    return True
            except Exception:
                pass
        if "publish/list" in (page.url or "") or "my-post" in (page.url or "").lower():
            return True
        if re.search(
            r"error|failed|invalid|something\s+went\s+wrong|"
            r"unable\s+to\s+publish|发布失败",
            body,
            re.I,
        ) and not re.search(r"published\s+success", body, re.I):
            for ign in ("field-error", "ant-form-item-has-error"):
                if page.locator(f".{ign}").count() == 0 and "success" not in body.lower():
                    pass
        page.wait_for_timeout(1000)
    return False


def _goto_published_tab_if_any(page) -> None:
    for tab in ("Published", "Live", "Active", "Posted", "My listings", "Listings"):
        try:
            t = page.get_by_role("tab", name=re.compile(rf"^{re.escape(tab)}$", re.I))
            if t.count() and t.first.is_visible(timeout=1500):
                t.first.click()
                page.wait_for_timeout(2200)
                return
        except Exception:
            continue
        try:
            t = page.get_by_role("tab", name=re.compile(tab, re.I))
            if t.count() and t.first.is_visible(timeout=1200):
                t.first.click()
                page.wait_for_timeout(2200)
                return
        except Exception:
            continue


@pytest.mark.p0
@pytest.mark.case_id_au58_property_publish_m9_006
@allure.feature("AU站房产发布")
@allure.story("模块9：存草稿与发布闭环")
@allure.title("TC006 填写必填后发布成功并在我的发布中找到该帖")
@allure.severity(allure.severity_level.BLOCKER)
def test_m9_tc006_publish_e2e_visible_in_my_posts(page, config):
    if not _IMG1.is_file():
        pytest.skip("缺少 test_data/images/apartment_1.png")
    unique = f"AU58-E2E-{int(time.time())}"
    intro = (
        "Automation TC006 end-to-end publish. Short intro for AU property rent house. "
        "Please ignore or delete in non-prod cleanup."
    )

    _ensure_logged_in(page, config)
    ppp = _open_property_rent_house_form(page, config)

    with allure.step("上传主图"):
        try:
            page.get_by_text("Pictures", exact=False).first.scroll_into_view_if_needed(timeout=8000)
        except Exception:
            pass
        ppp.upload_single_image(str(_IMG1), wait_ms=3000)

    with allure.step("填写全部必填字段：价格、rental-type、卧室、卫浴、楼层、面积、地址"):
        _try_fill_price_beds_address(page)

    with allure.step("填写标题和描述"):
        _fill_title_and_intro(page, unique, intro)

    with allure.step("滚回顶部确认无残留校验错误后提交 Post"):
        # 滚到顶再滚一遍到底，确保所有 lazy 字段都渲染过
        page.evaluate("() => window.scrollTo(0, 0)")
        page.wait_for_timeout(800)
        page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(800)
        # 找 Post 按钮
        try:
            page.get_by_role("button", name=re.compile(r"^Post$", re.I)).first.scroll_into_view_if_needed(timeout=15000)
        except Exception:
            page.mouse.wheel(0, 4500)
        page.wait_for_timeout(500)
        ppp.click_post_button(wait_ms=2000)

    with allure.step("等待发布成功或跳转发帖列表"):
        ok = _wait_publish_success_or_fail(page, timeout_ms=120000)
        if not ok and "publish/list" not in (page.url or ""):
            body = page.evaluate("() => document.body.innerText || ''") or ""
            if re.search(
                r"error|failed|required|please\s+(enter|select|add)|invalid",
                body,
                re.I,
            ) and not re.search(r"published|successfully\s+posted|live", body, re.I):
                pytest.fail(
                    f"发布后未检测到成功提示，页面可能仍有校验错误。URL={page.url!r} 片段={body[:900]!r}"
                )

    with allure.step("进入我的发布列表"):
        my_list = f"{config['publish_url']}/publish/list"
        _goto_with_retry(page, my_list, config)
        page.wait_for_timeout(2500)
        _accept_cookies(page)
        assert "publish/list" in (page.url or ""), "应打开发帖列表页"
        _goto_published_tab_if_any(page)
        page.wait_for_timeout(1500)

    with allure.step(f"列表中可见标题关键字: {unique}"):
        page.wait_for_timeout(2000)
        hit = page.get_by_text(unique, exact=False)
        if hit.count() == 0:
            page.keyboard.press("F5")
            page.wait_for_timeout(3500)
            _goto_published_tab_if_any(page)
        assert hit.first.is_visible(timeout=25000), (
            f"「我的发布」中应能找到刚发布标题含 {unique} 的帖子；当前 URL={page.url!r}"
        )
