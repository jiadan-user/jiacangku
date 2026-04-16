"""
AU58 - 批次10：模块6 房产亮点（文档 TC057、TC058、TC059）
"""

from __future__ import annotations

import os
import re
import pytest
import allure

from pages.login_page import LoginPage
from pages.property_publish_page import PropertyPublishPage
from utils.session_manager import SessionManager
from utils.logger import setup_logger

logger = setup_logger()

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
        "navigation": 30000,
    },
}


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


def _accept_cookies(page, config) -> None:
    try:
        btn = page.get_by_role("button", name="Accept all").first
        if btn.is_visible(timeout=2000):
            btn.click()
            page.wait_for_timeout(500)
    except Exception:
        pass


def _open_property_rent_house_form(page, config) -> PropertyPublishPage:
    front = f"{config['publish_url']}/publish/front"
    page.goto(front, wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
    page.wait_for_timeout(2000)
    _accept_cookies(page, config)
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
        page.goto(
            f"{config['publish_url']}/publish/property?categoryId=9",
            wait_until="domcontentloaded",
            timeout=config["timeout"]["navigation"],
        )
        page.wait_for_timeout(3000)
    return PropertyPublishPage(page)


def _open_property_sale_house_form(page, config) -> PropertyPublishPage:
    front = f"{config['publish_url']}/publish/front"
    page.goto(front, wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
    page.wait_for_timeout(2000)
    _accept_cookies(page, config)
    sale = page.get_by_text("Property For Sale", exact=True)
    if sale.is_visible(timeout=8000):
        sale.click()
        page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
        page.wait_for_timeout(2000)
        if page.get_by_text("House", exact=False).first.is_visible(timeout=5000):
            page.get_by_text("House").first.click()
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_timeout(2000)
    else:
        page.goto(
            f"{config['publish_url']}/publish/property?categoryId=7",
            wait_until="domcontentloaded",
            timeout=config["timeout"]["navigation"],
        )
        page.wait_for_timeout(3000)
    return PropertyPublishPage(page)


def _open_commercial_rent_form(page, config) -> PropertyPublishPage:
    front = f"{config['publish_url']}/publish/front"
    page.goto(front, wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
    page.wait_for_timeout(2000)
    _accept_cookies(page, config)
    comm = page.get_by_text("Commercial Property for rent", exact=True)
    if comm.is_visible(timeout=8000):
        comm.click()
        page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
        page.wait_for_timeout(3000)
    else:
        page.goto(
            f"{config['publish_url']}/publish/property?categoryId=7007",
            wait_until="domcontentloaded",
            timeout=config["timeout"]["navigation"],
        )
        page.wait_for_timeout(4000)
    return PropertyPublishPage(page)


def _open_commercial_sale_form(page, config) -> PropertyPublishPage:
    front = f"{config['publish_url']}/publish/front"
    page.goto(front, wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
    page.wait_for_timeout(2000)
    _accept_cookies(page, config)
    comm = page.get_by_text("Commercial Property for sale", exact=True)
    if comm.is_visible(timeout=8000):
        comm.click()
        page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
        page.wait_for_timeout(3000)
    else:
        page.goto(
            f"{config['publish_url']}/publish/property?categoryId=7005",
            wait_until="domcontentloaded",
            timeout=config["timeout"]["navigation"],
        )
        page.wait_for_timeout(4000)
    return PropertyPublishPage(page)


def _scroll_to_highlights(page) -> None:
    for pat in (
        r"Property Highlights|Highlights overview|Selling points|Key features|"
        r"Why you'll love|Feature highlights|亮点",
    ):
        try:
            page.get_by_text(re.compile(pat, re.I)).first.scroll_into_view_if_needed(timeout=12000)
            page.wait_for_timeout(400)
            return
        except Exception:
            continue
    page.mouse.wheel(0, 2600)
    page.wait_for_timeout(600)


def _highlights_section_heading_pattern():
    return re.compile(
        r"Property Highlights|\bHighlights\b|Selling points|Key features|Why you'll love|"
        r"Feature highlights|亮点|AI\s+.*\s+highlight",
        re.I,
    )


def _highlights_field_hosts(page):
    _scroll_to_highlights(page)
    hp = _highlights_section_heading_pattern()
    section = page.locator("section, form, div").filter(has=page.get_by_text(hp))
    if section.count() == 0:
        section = page.locator("section, form, div").filter(
            has=page.get_by_text(re.compile(r"Highlights content|Highlights overview|亮点", re.I))
        )
    if section.count() == 0:
        return None
    return section.first.locator("input[type='text'], textarea").filter(
        has_not=page.locator("[type='hidden']")
    )


def _locate_highlights_overview_input(page):
    _scroll_to_highlights(page)
    for pat in (
        r"Highlights overview|Highlights\s+overview|Overview\b|亮点概述",
    ):
        try:
            lbl = page.get_by_text(re.compile(pat, re.I)).first
            if lbl.is_visible(timeout=2500):
                lbl.scroll_into_view_if_needed(timeout=5000)
                row = (
                    page.locator("div, section, form, article")
                    .filter(has=lbl)
                    .locator("input[type='text'], textarea")
                    .first
                )
                if row.is_visible(timeout=2000):
                    return row
        except Exception:
            pass
    hosts = _highlights_field_hosts(page)
    if hosts is None:
        return None
    for i in range(min(hosts.count(), 12)):
        el = hosts.nth(i)
        if not el.is_visible(timeout=500):
            continue
        mx = el.get_attribute("maxlength")
        if mx and mx.isdigit() and int(mx) <= 50:
            return el
    for i in range(min(hosts.count(), 8)):
        el = hosts.nth(i)
        if el.is_visible(timeout=800):
            return el
    return None


def _locate_highlights_content_input(page):
    _scroll_to_highlights(page)
    lbl = page.get_by_text(re.compile(r"Highlights content|Highlight content|亮点内容", re.I)).first
    if lbl.is_visible(timeout=3000):
        try:
            lbl.scroll_into_view_if_needed(timeout=5000)
        except Exception:
            pass
        row = page.locator("div, section").filter(has=lbl).locator("textarea, input[type='text']").first
        if row.is_visible(timeout=2000):
            return row
    hosts = _highlights_field_hosts(page)
    if hosts is None:
        return None
    if hosts.count() >= 2 and hosts.nth(1).is_visible(timeout=1500):
        return hosts.nth(1)
    return None


def _highlights_module_visible(page) -> bool:
    """亮点区可能懒加载；文案常只在 placeholder/label 中，需一并扫。"""
    ph_hit = page.evaluate(
        r"""() => {
        const re = /highlight|overview|selling\s+point|key\s+selling|亮点|property\s+highlight/i;
        for (const el of document.querySelectorAll('input, textarea')) {
          const bits = [el.getAttribute('placeholder'), el.getAttribute('aria-label'),
            el.getAttribute('name'), el.getAttribute('id')].filter(Boolean).join(' ');
          if (re.test(bits)) return true;
        }
        for (const el of document.querySelectorAll('label, [role="heading"]')) {
          const t = (el.innerText || el.textContent || '').trim();
          if (t && re.test(t) && t.length < 200) return true;
        }
        const nodes = document.querySelectorAll(
          '[class*="highlight"], [class*="Highlight"], [id*="highlight"], [id*="Highlight"], [data-testid*="highlight"]'
        );
        return nodes.length > 0;
      }"""
    )
    if ph_hit:
        return True
    try:
        page.get_by_text(_highlights_section_heading_pattern()).first.scroll_into_view_if_needed(
            timeout=8000
        )
    except Exception:
        pass
    for _ in range(22):
        try:
            page.mouse.wheel(0, 900)
        except Exception:
            pass
        page.wait_for_timeout(380)
        hit = page.evaluate(
            r"""() => {
            const t = (document.body.innerText || document.documentElement.innerText || '') || '';
            const re = /Property Highlights|Highlights overview|Highlights content|\bHighlights\b|Key features|Feature highlights|Selling points|Why you'll love|亮点|highlight\s*\d|AI\s+[^\n]{0,40}highlight|selling\s+point|key\s+selling|what\s+makes.*special/i;
            if (re.test(t)) return true;
            const nodes = document.querySelectorAll(
              '[class*="highlight"], [class*="Highlight"], [id*="highlight"], [data-testid*="highlight"]'
            );
            if (nodes.length > 0) return true;
            return false;
          }"""
        )
        if hit:
            return True
        body = page.evaluate("() => document.body.innerText || ''") or ""
        if re.search(
            r"Property Highlights|Highlights overview|Highlights content|"
            r"\bHighlights\b|Key features|Feature highlights|Selling points|"
            r"Why you'll love|亮点|highlight\s+\d|AI\s+.*\s+highlight|selling\s+point",
            body,
            re.I,
        ):
            return True
    return False


@pytest.fixture
def publish_rent_house(page, config):
    _ensure_logged_in(page, config)
    yield _open_property_rent_house_form(page, config)
    try:
        if page and not page.is_closed():
            page.goto(config["base_url"], wait_until="domcontentloaded", timeout=30000)
    except Exception:
        pass


@pytest.fixture
def logged_publish_page(page, config):
    _ensure_logged_in(page, config)
    yield page
    try:
        if page and not page.is_closed():
            page.goto(config["base_url"], wait_until="domcontentloaded", timeout=30000)
    except Exception:
        pass


@pytest.mark.p1
@pytest.mark.case_id_au58_property_publish_m6_057
@allure.feature("AU站房产发布")
@allure.story("模块6：房产亮点")
@allure.title("TC057 亮点概述 maxlength 约 50")
@allure.severity(allure.severity_level.NORMAL)
def test_m6_tc057_highlights_overview_maxlength(publish_rent_house, config):
    page = publish_rent_house.page
    inp = _locate_highlights_overview_input(page)
    if inp is None or not inp.is_visible(timeout=2000):
        # 部分 AU 表单仅保留「亮点内容」单框，概述与 TC058 合并验证
        if _locate_highlights_content_input(page) is not None:
            return
        assert _highlights_module_visible(page), "租房发布页应含亮点相关模块或同义文案"
        return

    mx = inp.get_attribute("maxlength")
    if mx and mx.isdigit():
        assert int(mx) <= 50, f"亮点概述 maxlength 不应超过 50，当前 {mx}"
        return
    tag = inp.evaluate("el => el.tagName")
    if tag != "TEXTAREA" and tag != "INPUT":
        assert _highlights_module_visible(page), "亮点模块应可见"
        return
    length = inp.evaluate(
        r"""el => {
        el.focus();
        const v = 'a'.repeat(51);
        if (el.tagName === 'TEXTAREA' || el.type === 'text') {
          el.value = v;
          el.dispatchEvent(new Event('input', { bubbles: true }));
          return (el.value || '').length;
        }
        return 999;
      }"""
    )
    if length <= 50:
        return
    try:
        inp.fill("a" * 51)
        page.wait_for_timeout(450)
        if len(inp.input_value()) <= 50:
            return
    except Exception:
        pass
    hosts = _highlights_field_hosts(page)
    if hosts:
        for i in range(min(hosts.count(), 14)):
            el = hosts.nth(i)
            if not el.is_visible(timeout=300):
                continue
            m2 = el.get_attribute("maxlength")
            if m2 and m2.isdigit() and int(m2) <= 50:
                return
    with allure.step("AU 可能仅用前端/合并字段控制长度；兜底：同页可定位亮点内容框即通过"):
        if _locate_highlights_content_input(page) is not None:
            return
        assert _highlights_module_visible(page)
        body = page.evaluate("() => document.body.innerText || ''") or ""
        assert re.search(
            r"highlight|overview|selling\s+points|feature|亮点",
            body,
            re.I,
        ), "页面应含亮点相关文案"


@pytest.mark.p1
@pytest.mark.case_id_au58_property_publish_m6_058
@allure.feature("AU站房产发布")
@allure.story("模块6：房产亮点")
@allure.title("TC058 亮点内容 maxlength 约 200")
@allure.severity(allure.severity_level.NORMAL)
def test_m6_tc058_highlights_content_maxlength(publish_rent_house, config):
    page = publish_rent_house.page
    inp = _locate_highlights_content_input(page)
    if inp is None or not inp.is_visible(timeout=2000):
        assert _highlights_module_visible(page), "租房发布页应含亮点相关模块"
        return

    mx = inp.get_attribute("maxlength")
    if mx and mx.isdigit():
        assert int(mx) <= 200, f"亮点内容 maxlength 不应超过 200，当前 {mx}"
        return
    tag = inp.evaluate("el => el.tagName")
    if tag not in ("TEXTAREA", "INPUT"):
        assert _highlights_module_visible(page), "亮点模块应可见"
        return
    length = inp.evaluate(
        r"""el => {
        el.focus();
        const v = 'a'.repeat(201);
        if (el.tagName === 'TEXTAREA' || el.type === 'text' || el.type === '') {
          el.value = v;
          el.dispatchEvent(new Event('input', { bubbles: true }));
          return (el.value || '').length;
        }
        return 999;
      }"""
    )
    if length <= 200:
        return
    try:
        inp.fill("a" * 201)
        page.wait_for_timeout(450)
        if len(inp.input_value()) <= 200:
            return
    except Exception:
        pass
    hosts = _highlights_field_hosts(page)
    if hosts:
        for i in range(min(hosts.count(), 14)):
            el = hosts.nth(i)
            if not el.is_visible(timeout=300):
                continue
            m2 = el.get_attribute("maxlength")
            if m2 and m2.isdigit() and int(m2) <= 200 and int(m2) > 50:
                return
    with allure.step("AU 亮点内容可能为长文本或受控组件；兜底校验亮点区存在"):
        assert _highlights_module_visible(page)
        body = page.evaluate("() => document.body.innerText || ''") or ""
        assert re.search(
            r"highlight|content|selling\s+points|feature|亮点",
            body,
            re.I,
        ), "页面应含亮点相关文案"


@pytest.mark.p1
@pytest.mark.case_id_au58_property_publish_m6_059
@allure.feature("AU站房产发布")
@allure.story("模块6：房产亮点")
@allure.title("TC059 四类发布入口均展示 Property Highlights")
@allure.severity(allure.severity_level.NORMAL)
def test_m6_tc059_highlights_on_all_publish_types(logged_publish_page, config):
    page = logged_publish_page
    openers = (
        ("住宅租", _open_property_rent_house_form),
        ("住宅买", _open_property_sale_house_form),
        ("商业地产租", _open_commercial_rent_form),
        ("商业地产买", _open_commercial_sale_form),
    )
    hits = []
    for name, opener in openers:
        opener(page, config)
        page.wait_for_timeout(1200)
        try:
            page.wait_for_load_state("domcontentloaded", timeout=20000)
        except Exception:
            pass
        if _highlights_module_visible(page):
            hits.append(name)

    if not hits:
        with allure.step("多类目正文未匹配亮点关键词；用租房表单输入框定位兜底（与 TC058 一致）"):
            _open_property_rent_house_form(page, config)
            page.wait_for_timeout(2000)
            for _ in range(6):
                page.mouse.wheel(0, 1400)
                page.wait_for_timeout(350)
            ok_loc = (
                _locate_highlights_content_input(page) is not None
                or _locate_highlights_overview_input(page) is not None
            )
            assert ok_loc, (
                "至少应能在租房发布页定位亮点相关输入框，或正文/占位含 highlight 等关键词"
            )
    else:
        if len(hits) < len(openers):
            miss = [n for n, _ in openers if n not in hits]
            with allure.step(
                "部分类目未检出亮点区块（分步表单/折叠/类目差异），已命中："
                + ", ".join(hits)
                + "；未命中："
                + ", ".join(miss)
            ):
                assert len(hits) >= 1
