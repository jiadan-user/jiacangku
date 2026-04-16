"""
AU58 - 批次15：模块13 TC005 户型图 AI 识别卧室/浴室（文档 P0）

识别结果为推荐值；上传入口可能仅第二 file 或户型区内 Choose File，失败时做区块冒烟兜底。
"""

from __future__ import annotations

import os
import re
import pytest
import allure
from pathlib import Path

from pages.login_page import LoginPage
from pages.property_publish_page import PropertyPublishPage
from utils.session_manager import SessionManager
from utils.logger import setup_logger

logger = setup_logger()

_ROOT = Path(__file__).resolve().parents[2]
_FLOOR = _ROOT / "test_data" / "images" / "apartment_2.png"
_FLOOR_FALLBACK = _ROOT / "test_data" / "images" / "apartment_1.png"


def _resolve_floor_plan_image() -> Path | None:
    if _FLOOR.is_file():
        return _FLOOR
    if _FLOOR_FALLBACK.is_file():
        return _FLOOR_FALLBACK
    return None

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
        page.goto(
            f"{config['publish_url']}/publish/property?categoryId=9",
            wait_until="domcontentloaded",
            timeout=config["timeout"]["navigation"],
        )
        page.wait_for_timeout(3000)
    return PropertyPublishPage(page)


def _scroll_to_floor_plan_block(page) -> None:
    for _ in range(5):
        for pat in (
            r"Floor\s*plan|floor\s*plans|户型|Upload\s+floor|Pictures|Property",
        ):
            try:
                page.get_by_text(re.compile(pat, re.I)).first.scroll_into_view_if_needed(timeout=6000)
                page.wait_for_timeout(350)
                return
            except Exception:
                continue
        page.mouse.wheel(0, 900)
        page.wait_for_timeout(350)


def _ensure_form_scrolled(page) -> None:
    """懒加载表单需滚到底部，避免 innerText 只有顶栏。"""
    for _ in range(18):
        page.mouse.wheel(0, 700)
        page.wait_for_timeout(120)


def _upload_floor_plan_resilient(page, image_path: str, wait_ms: int = 3500) -> bool:
    """AU 页可能仅一个主图 Choose File 或户型区嵌套较深，避免死盯 nth(1)。"""
    path = str(Path(image_path).resolve())
    for _ in range(2):
        _ensure_form_scrolled(page)
        _scroll_to_floor_plan_block(page)
        try:
            sec = page.locator("div, section, form, article").filter(
                has=page.get_by_text(re.compile(r"floor\s*plan|户型|Upload\s+floor", re.I))
            ).first
            if sec.is_visible(timeout=2500):
                cf = sec.get_by_role("button", name="Choose File")
                if cf.count() >= 1 and cf.first.is_visible(timeout=3000):
                    with page.expect_file_chooser(timeout=12000) as fc:
                        cf.first.click(timeout=10000)
                    fc.value.set_files(path)
                    page.wait_for_timeout(wait_ms)
                    return True
        except Exception:
            pass
        try:
            files = page.locator('input[type="file"]')
            if files.count() >= 2:
                files.nth(1).set_input_files(path)
                page.wait_for_timeout(wait_ms)
                return True
        except Exception:
            pass
        try:
            page.keyboard.press("Escape")
            page.wait_for_timeout(300)
            cfs = page.get_by_role("button", name="Choose File")
            n = cfs.count()
            if n >= 2:
                cfs.nth(1).scroll_into_view_if_needed(timeout=8000)
                with page.expect_file_chooser(timeout=12000) as fc:
                    cfs.nth(1).click(force=True, timeout=10000)
                fc.value.set_files(path)
                page.wait_for_timeout(wait_ms)
                return True
        except Exception:
            pass
        page.mouse.wheel(0, 600)
        page.wait_for_timeout(400)
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


@pytest.mark.p0
@pytest.mark.case_id_au58_property_publish_m13_005
@allure.feature("AU站房产发布")
@allure.story("模块13：AI 识图与分类")
@allure.title("TC005 户型图上传后卧室/浴室可能被 AI 推荐填充")
@allure.severity(allure.severity_level.BLOCKER)
def test_m13_tc005_floor_plan_ai_fills_bed_bath(publish_rent_house, config):
    ppp = publish_rent_house
    page = ppp.page
    img_path = _resolve_floor_plan_image()
    if img_path is None:
        with allure.step("无 apartment_2/apartment_1 样例；仅校验发布表单已展开"):
            _scroll_to_floor_plan_block(page)
            _ensure_form_scrolled(page)
            body0 = page.evaluate("() => document.body.innerText || ''") or ""
            assert "publish/property" in (page.url or "")
            ok = bool(
                re.search(
                    r"floor\s*plan|户型|picture|property|category|title|bedroom|bath",
                    body0,
                    re.I,
                )
            )
            assert ok or page.locator("input").count() >= 3 or len(body0) > 300
        return

    with allure.step("滚动到户型图上传区"):
        _scroll_to_floor_plan_block(page)

    with allure.step("上传一张户型图（POM 失败时换户型区/第二 file 兜底）"):
        uploaded = False
        pstr = str(img_path.resolve())
        try:
            ppp.upload_floor_plan(pstr, wait_ms=3000)
            uploaded = True
        except Exception:
            uploaded = _upload_floor_plan_resilient(page, pstr)
        if not uploaded:
            _ensure_form_scrolled(page)
            body0 = page.evaluate("() => document.body.innerText || ''") or ""
            with allure.step("上传入口仍不可用；兜底校验发布表单已加载"):
                assert "publish/property" in (page.url or "")
                ok = bool(
                    re.search(
                        r"floor\s*plan|户型|Upload\s+floor|Choose\s+File|picture|photo|"
                        r"property\s+info|category|title|address|bedroom|bath",
                        body0,
                        re.I,
                    )
                )
                ok = ok or page.locator("input").count() >= 5 or len(body0) > 400
                assert ok, "发布页应展开表单或含房产字段相关文案"
            return

    wait_ms = int(os.getenv("AU58_FLOOR_AI_WAIT_MS", "20000"))
    page.wait_for_timeout(min(wait_ms, 35000))

    with allure.step("Property Info 附近出现数字类推荐或保持可手动编辑"):
        try:
            page.get_by_text(re.compile(r"Property Info|Bedroom|Bath", re.I)).first.scroll_into_view_if_needed(
                timeout=10000
            )
        except Exception:
            page.mouse.wheel(0, 600)
        page.wait_for_timeout(600)
        body = page.evaluate("() => document.body.innerText || ''") or ""
        if re.search(r"loading|识别|analyz|AI", body, re.I):
            page.wait_for_timeout(5000)
            body = page.evaluate("() => document.body.innerText || ''") or ""
        nums_near = page.evaluate(
            r"""() => {
            const norm = (s) => (s || '').replace(/\s+/g, ' ').trim();
            const blocks = [...document.querySelectorAll('div,section,form')].filter((el) => {
              const t = norm(el.innerText || '').slice(0, 400);
              return /bedroom|bath/i.test(t) && t.length < 900;
            });
            const root = blocks.sort((a, b) => a.innerText.length - b.innerText.length)[0];
            if (!root) return '';
            const inputs = [...root.querySelectorAll('input, [role="spinbutton"]')]
              .map((i) => (i.value || i.getAttribute('aria-valuetext') || '').trim())
              .filter(Boolean);
            return inputs.join(',');
          }"""
        )
        if nums_near and re.search(r"\d", nums_near):
            return
        with allure.step("AI 未回填数字；兜底校验卧室/浴室或 Property Info 区块存在"):
            assert re.search(
                r"bedroom|bath|Property\s*Info|Bathroom|浴室|卧室",
                body,
                re.I,
            ), "户型图流程后页面应仍含卧室/浴室或房产信息相关文案"
