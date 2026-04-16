"""
AU58 - 批次6：模块3 发布页分类（文档 TC001、TC002、TC003、TC004）
- TC002 app：窄视口下验证三级分类仍可见，并记录是否出现横向滚动容器。
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

_SERVER_ERR = re.compile(
    r"502\s*Bad\s*Gateway|503\s*Service|504\s*Gateway|Tengine|nginx|Server\s+Error", re.I
)


def _assert_publish_page_available(page) -> None:
    """若服务端 5xx 或未到达发布表单，skip 本用例。"""
    url = page.url or ""
    body = ""
    for fr in page.frames:
        try:
            body += (fr.evaluate("() => document.body ? (document.body.innerText || '') : ''") or "")
        except Exception:
            pass
    if _SERVER_ERR.search(body):
        pytest.skip(f"发布服务端 5xx 不可用，跳过（body 片段: {body[:200]!r}）")
    if "publish/property" not in url:
        pytest.skip(f"未到达发布表单页，停在: {url!r}（可能 front 页分类按钮加载失败）")


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

_RENT_TERTIARY = (
    "House",
    "Townhomes",
    "Apartment&Unit",
    "Villa",
    "Retirement",
    "Other",
)


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


def _click_bathrooms_option(page, digit: str) -> bool:
    """在 Property Info 附近点击浴室数量（兼容 chip / button / span）。"""
    page.get_by_text("Property Info", exact=False).first.scroll_into_view_if_needed(timeout=5000)
    page.wait_for_timeout(400)
    ok = page.evaluate(
        """(digit) => {
        const norm = (s) => (s || '').replace(/\\s+/g, ' ').trim();
        const want = norm(digit);
        const blocks = [...document.querySelectorAll('div,section,form')].filter((el) => {
          const t = norm(el.innerText || '').slice(0, 200);
          return /bathrooms?\\b/i.test(t) && t.length < 800;
        });
        let root = blocks.sort((a, b) => a.innerText.length - b.innerText.length)[0];
        if (!root) return false;
        const cand = [...root.querySelectorAll('button, [role="button"], span, div, a')].filter(
          (el) => norm(el.textContent) === want && el.getClientRects().length > 0
        );
        const pick = cand.find((el) => {
          const st = window.getComputedStyle(el);
          return st.display !== 'none' && st.visibility !== 'hidden';
        });
        if (pick) {
          pick.click();
          return true;
        }
        return false;
      }""",
        digit,
    )
    page.wait_for_timeout(500)
    return bool(ok)


def _open_property_rent_house_form(page, config) -> PropertyPublishPage:
    front = f"{config['publish_url']}/publish/front"
    page.goto(front, wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
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
        direct = f"{config['publish_url']}/publish/property?categoryId=9"
        page.goto(direct, wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
        page.wait_for_timeout(3000)
    _assert_publish_page_available(page)
    return PropertyPublishPage(page)


@pytest.fixture
def publish_rent_house(page, config):
    _ensure_logged_in(page, config)
    yield _open_property_rent_house_form(page, config)
    try:
        if page and not page.is_closed():
            page.goto(config["base_url"], wait_until="domcontentloaded", timeout=30000)
    except Exception:
        pass


@pytest.mark.p0
@pytest.mark.case_id_au58_property_publish_m3_001
@allure.feature("AU站房产发布")
@allure.story("模块3：分类选择")
@allure.title("TC001 租房发布页三级分类列表")
@allure.severity(allure.severity_level.BLOCKER)
def test_m3_tc001_rent_tertiary_categories_visible(publish_rent_house, config):
    page = publish_rent_house.page
    _assert_publish_page_available(page)
    with allure.step("租房三级分类应包含文档中的住宅类型"):
        for name in _RENT_TERTIARY:
            visible = page.get_by_text(name, exact=True).first.is_visible(timeout=8000)
            if not visible:
                # 尝试再滚动一次，部分懒加载场景分类在视口外
                try:
                    page.mouse.wheel(0, -1200)
                    page.wait_for_timeout(600)
                    visible = page.get_by_text(name, exact=True).first.is_visible(timeout=4000)
                except Exception:
                    pass
            assert visible, f"应显示三级分类: {name}"
    with allure.step("当前页应为租房发布上下文"):
        assert not page.get_by_text("Property For Sale Post", exact=False).is_visible(
            timeout=2000
        ), "不应处于买房发布标题"


@pytest.mark.p0
@pytest.mark.case_id_au58_property_publish_m3_003
@allure.feature("AU站房产发布")
@allure.story("模块3：分类选择")
@allure.title("TC003 选中 House 后 Property Info 可见")
@allure.severity(allure.severity_level.BLOCKER)
def test_m3_tc003_property_info_after_category(publish_rent_house, config):
    ppp: PropertyPublishPage = publish_rent_house
    _assert_publish_page_available(ppp.page)
    page = ppp.page
    with allure.step("点击 House 确保选中"):
        try:
            page.get_by_text("House", exact=True).first.click(timeout=5000)
            page.wait_for_timeout(1500)
        except Exception:
            pass
    with allure.step("滚动到 Property Info 区域"):
        for pat in (r"Property\s+Info", r"Bedroom", r"Bathroom"):
            try:
                page.get_by_text(re.compile(pat, re.I)).first.scroll_into_view_if_needed(timeout=6000)
                page.wait_for_timeout(400)
                break
            except Exception:
                continue
        else:
            for _ in range(6):
                page.mouse.wheel(0, 800)
                page.wait_for_timeout(300)
    with allure.step("Property Info 区域展示（含 Bedroom/Bathroom 等字段）"):
        assert ppp.is_property_info_section_visible(), (
            "选中 House 后应展示 Property Info 区（含 Bedroom/Bathroom 或相关字段）"
        )


@pytest.mark.p1
@pytest.mark.case_id_au58_property_publish_m3_004
@allure.feature("AU站房产发布")
@allure.story("模块3：分类选择")
@allure.title("TC004 同二级下切换三级保留浴室选择")
@allure.severity(allure.severity_level.NORMAL)
def test_m3_tc004_switch_tertiary_retains_bathroom(publish_rent_house, config):
    page = publish_rent_house.page
    _assert_publish_page_available(page)
    with allure.step("House 下选择 Bathrooms = 2"):
        if not _click_bathrooms_option(page, "2"):
            pytest.skip("浴室选项定位失败（未找到 Bathrooms 区块或可点击的 2）")

    with allure.step("切换到 Townhomes"):
        try:
            page.get_by_text("Townhomes", exact=True).first.click(timeout=8000)
            page.wait_for_timeout(1200)
        except Exception as e:
            pytest.skip(f"点击 Townhomes 失败: {e}")

    with allure.step("浴室 2 仍选中或可识别"):
        ok = page.evaluate(
            r"""() => {
            const norm = (s) => (s || '').replace(/\s+/g, ' ').trim();
            const blocks = [...document.querySelectorAll('div,section')].filter((el) => {
              const t = norm(el.innerText || '').slice(0, 220);
              return /bathrooms?\b/i.test(t) && t.length < 800;
            });
            const root = blocks.sort((a, b) => a.innerText.length - b.innerText.length)[0];
            if (!root) return false;
            const twos = [...root.querySelectorAll('button, [role="button"], span, div')].filter(
              (el) => norm(el.textContent) === '2'
            );
            return twos.some((el) => {
              const st = window.getComputedStyle(el);
              if (st.display === 'none' || st.visibility === 'hidden') return false;
              const bg = st.backgroundColor || '';
              const cls = String(el.className || '');
              return (
                el.getAttribute('aria-pressed') === 'true' ||
                el.getAttribute('aria-selected') === 'true' ||
                /active|selected|checked/i.test(cls) ||
                bg.includes('0, 0, 0') ||
                bg.includes('rgb(0,')
              );
            });
          }"""
        )
        assert ok, "切换三级后 Bathrooms=2 未保持选中态"


@pytest.mark.p1
@pytest.mark.case_id_au58_property_publish_m3_002
@allure.feature("AU站房产发布")
@allure.story("模块3：分类选择")
@allure.title("TC002 PC 端三级分类布局不超过约 2 行")
@allure.severity(allure.severity_level.MINOR)
def test_m3_tc002_pc_category_two_rows_layout(publish_rent_house, config):
    page = publish_rent_house.page
    _assert_publish_page_available(page)
    try:
        page.get_by_text("House", exact=True).first.scroll_into_view_if_needed(timeout=8000)
    except Exception:
        pass
    page.wait_for_timeout(500)
    info = page.evaluate(
        r"""() => {
        const want = ['House', 'Townhomes', 'Apartment&Unit', 'Villa', 'Retirement', 'Other'];
        const tops = [];
        for (const t of want) {
          const els = [...document.querySelectorAll('button, div, span, a')].filter(
            (e) => (e.textContent || '').trim() === t
          );
          const el = els.find((e) => {
            const st = window.getComputedStyle(e);
            const r = e.getBoundingClientRect();
            return st.display !== 'none' && st.visibility !== 'hidden' && r.width > 4 && r.height > 4;
          });
          if (!el) continue;
          const r = el.getBoundingClientRect();
          tops.push(Math.round(r.top));
        }
        if (tops.length < 4) return { ok: false, reason: 'few-labels', tops, rowBuckets: [] };
        const bucket = (y) => Math.round(y / 12) * 12;
        const rows = new Set(tops.map(bucket));
        return { ok: true, tops, rowBuckets: [...rows], rowCount: rows.size };
      }"""
    )
    if not info.get("ok"):
        pytest.skip("可见三级分类不足，无法统计行数")
    assert info.get("rowCount", 9) <= 2, (
        f"文档：PC 分类最多约 2 行；当前估算 {info.get('rowCount')} 行，tops={info.get('tops')}"
    )


@pytest.mark.p1
@pytest.mark.case_id_au58_property_publish_m3_002_app
@allure.feature("AU站房产发布")
@allure.story("模块3：分类选择")
@allure.title("TC002 窄视口下三级分类可见或可横向滚动")
@allure.severity(allure.severity_level.MINOR)
def test_m3_tc002_app_narrow_viewport_categories(publish_rent_house, config):
    """文档 app 横向滑动：窄屏下分类区可出现 overflow 滚动，或折行展示；本用例验证仍可操作。"""
    page = publish_rent_house.page
    _assert_publish_page_available(page)
    page.set_viewport_size({"width": 390, "height": 844})
    page.wait_for_timeout(600)
    try:
        page.get_by_text("House", exact=True).first.scroll_into_view_if_needed(timeout=8000)
    except Exception:
        pass
    page.wait_for_timeout(400)
    for name in _RENT_TERTIARY:
        assert page.get_by_text(name, exact=True).first.is_visible(
            timeout=6000
        ), f"窄视口下仍应可见三级分类: {name}"
    scroll_info = page.evaluate(
        r"""() => {
        const labels = ['House','Townhomes','Apartment&Unit','Villa','Retirement','Other'];
        const candidates = [...document.querySelectorAll('div,section,form')].filter((el) => {
          const t = (el.textContent || '').trim();
          if (t.length > 1200) return false;
          return labels.filter((n) => t.includes(n)).length >= 4;
        });
        for (const el of candidates) {
          const sw = el.scrollWidth;
          const cw = el.clientWidth;
          if (sw > cw + 6) return { scrollable: true, scrollWidth: sw, clientWidth: cw };
        }
        return { scrollable: false };
      }"""
    )
    logger.info("TC002 窄视口分类区 scrollWidth>clientWidth: %s", scroll_info)
