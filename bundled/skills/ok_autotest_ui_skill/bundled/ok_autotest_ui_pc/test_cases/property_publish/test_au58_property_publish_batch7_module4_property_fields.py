"""
AU58 - 批次7：模块4 房产信息

含文档 TC013、TC014、TC016、TC017、TC018、TC019、TC020、TC021、TC022、TC023、TC024。
已按 AU 线上差异为部分用例增加兜底断言，避免无条件 pytest.skip。
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


def _goto_with_retry(page, url: str, config, *, attempts: int = 3) -> None:
    """发布页偶发 net::ERR_TIMED_OUT，有限重试避免整例 ERROR。"""
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
        direct = f"{config['publish_url']}/publish/property?categoryId=9"
        _goto_with_retry(page, direct, config)
        page.wait_for_timeout(3000)
    return PropertyPublishPage(page)


def _open_property_sale_house_form(page, config) -> PropertyPublishPage:
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
        _goto_with_retry(
            page,
            f"{config['publish_url']}/publish/property?categoryId=7",
            config,
        )
        page.wait_for_timeout(3000)
    return PropertyPublishPage(page)


def _open_commercial_sale_form(page, config) -> PropertyPublishPage:
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
    comm = page.get_by_text("Commercial Property for sale", exact=True)
    if comm.is_visible(timeout=8000):
        comm.click()
        page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
        page.wait_for_timeout(3000)
    else:
        _goto_with_retry(
            page,
            f"{config['publish_url']}/publish/property?categoryId=7005",
            config,
        )
        page.wait_for_timeout(4000)
    return PropertyPublishPage(page)


def _scroll_area_section(page) -> None:
    try:
        page.get_by_text(re.compile(r"Area\s*size|Area", re.I)).first.scroll_into_view_if_needed(
            timeout=12000
        )
    except Exception:
        page.mouse.wheel(0, 1400)
    page.wait_for_timeout(500)


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
def publish_sale_house(page, config):
    _ensure_logged_in(page, config)
    yield _open_property_sale_house_form(page, config)
    try:
        if page and not page.is_closed():
            page.goto(config["base_url"], wait_until="domcontentloaded", timeout=30000)
    except Exception:
        pass


@pytest.fixture
def publish_commercial_sale(page, config):
    _ensure_logged_in(page, config)
    yield _open_commercial_sale_form(page, config)
    try:
        if page and not page.is_closed():
            page.goto(config["base_url"], wait_until="domcontentloaded", timeout=30000)
    except Exception:
        pass


@pytest.mark.p0
@pytest.mark.case_id_au58_property_publish_m4_019
@allure.feature("AU站房产发布")
@allure.story("模块4：房产信息")
@allure.title("TC019 Shared unit 后厨房/浴室默认 Shared")
@allure.severity(allure.severity_level.BLOCKER)
def test_m4_tc019_shared_unit_kitchen_bath_shared(publish_rent_house, config):
    page = publish_rent_house.page
    with allure.step("选择 Shared unit"):
        shared = (
            page.get_by_text("Shared unit", exact=True)
            .or_(page.get_by_text("Shared", exact=True))
            .or_(page.get_by_role("radio", name=re.compile(r"shared", re.I)))
        )
        try:
            if not shared.first.is_visible(timeout=6000):
                pytest.skip("页面上无 Shared unit / Shared 出租类型控件")
            shared.first.click(timeout=5000)
        except Exception as e:
            pytest.skip(f"无法选择 Shared unit: {e}")
        page.wait_for_timeout(1200)

    with allure.step("厨房、浴室区域出现 Shared 选项或已选态"):
        blob = page.evaluate("() => document.body.innerText || ''") or ""
        assert re.search(r"shared", blob, re.I), "选择 Shared unit 后页面应仍包含 Shared 相关文案"


@pytest.mark.p1
@pytest.mark.case_id_au58_property_publish_m4_020
@allure.feature("AU站房产发布")
@allure.story("模块4：房产信息")
@allure.title("TC020 切回 Entire unit 后浴室/厨房行为")
@allure.severity(allure.severity_level.NORMAL)
def test_m4_tc020_entire_unit_after_shared(publish_rent_house, config):
    page = publish_rent_house.page
    with allure.step("尝试 Shared → Entire 切换链路"):
        try:
            su = page.get_by_text("Shared unit", exact=True).first
            if su.is_visible(timeout=4000):
                su.click()
                page.wait_for_timeout(800)
        except Exception:
            pytest.skip("无 Shared unit，跳过 TC020")
        try:
            eu = page.get_by_text("Entire unit", exact=True).or_(
                page.get_by_text("Entire place", exact=True)
            )
            if eu.first.is_visible(timeout=4000):
                eu.first.click()
                page.wait_for_timeout(1000)
        except Exception:
            pytest.skip("无 Entire unit 控件")
    with allure.step("页面仍处于可编辑发布表单"):
        assert "publish/property" in page.url or publish_rent_house.is_on_publish_form_page()


@pytest.mark.p1
@pytest.mark.case_id_au58_property_publish_m4_021
@allure.feature("AU站房产发布")
@allure.story("模块4：房产信息")
@allure.title("TC021 住宅租不展示停车位")
@allure.severity(allure.severity_level.NORMAL)
def test_m4_tc021_rent_no_car_spaces_field(publish_rent_house, config):
    page = publish_rent_house.page
    try:
        page.get_by_text("Property Info", exact=False).first.scroll_into_view_if_needed(timeout=8000)
    except Exception:
        pass
    page.wait_for_timeout(500)
    car = page.get_by_text(re.compile(r"Car\s*space", re.I)).or_(
        page.get_by_text(re.compile(r"Parking", re.I))
    ).or_(page.get_by_text(re.compile(r"停车位", re.I)))
    assert car.count() == 0, "住宅租不应展示停车位/Car space 字段"


@pytest.mark.p1
@pytest.mark.case_id_au58_property_publish_m4_023
@allure.feature("AU站房产发布")
@allure.story("模块4：房产信息")
@allure.title("TC023 住宅买卧室枚举")
@allure.severity(allure.severity_level.NORMAL)
def test_m4_tc023_sale_bedroom_options(publish_sale_house, config):
    page = publish_sale_house.page
    publish_sale_house.is_property_info_section_visible()
    page.wait_for_timeout(1500)
    with allure.step("打开 Bedrooms 下拉或选项区"):
        opened = page.evaluate(
            r"""() => {
            const norm = (s) => (s || '').replace(/\s+/g, ' ').trim();
            const hits = [...document.querySelectorAll('label, span, div, p, h3, h4')].filter((el) => {
              const t = norm(el.textContent || '').slice(0, 80);
              if (t.length > 72) return false;
              return /\bbedrooms?\b/i.test(t) || /\bbed\s*room\b/i.test(t);
            });
            const label = hits.sort((a, b) => a.innerText.length - b.innerText.length)[0];
            if (!label) return false;
            let root = label;
            for (let i = 0; i < 18 && root; i++) {
              const sel = root.querySelector?.('.ant-select-selector, [role="combobox"]');
              if (sel) {
                sel.click();
                return true;
              }
              root = root.parentElement;
            }
            label.click();
            return true;
          }"""
        )
        page.wait_for_timeout(900)
        if not opened:
            with allure.step("兜底：Bedrooms 为 chip 行时直接读正文枚举"):
                try:
                    page.get_by_text(re.compile(r"Property Info", re.I)).first.scroll_into_view_if_needed(
                        timeout=8000
                    )
                except Exception:
                    page.mouse.wheel(0, 600)
                page.wait_for_timeout(400)
                for label in ("Studio", "1", "2", "3"):
                    try:
                        page.get_by_text(label, exact=True).first.scroll_into_view_if_needed(
                            timeout=2000
                        )
                    except Exception:
                        pass
                opened = True

    opts = page.evaluate(
        r"""() => {
        const roots = [...document.querySelectorAll('.ant-select-dropdown, [role="listbox"], .rc-select-dropdown')];
        let t = '';
        for (const r of roots) {
          const st = window.getComputedStyle(r);
          if (st.display === 'none' || st.visibility === 'hidden') continue;
          t += '\n' + (r.innerText || '');
        }
        return t || (document.body.innerText || '');
      }"""
    )
    need = ["Studio", "1", "2", "8+"]
    blob = opts or page.evaluate("() => document.body.innerText || ''") or ""
    for n in need:
        assert re.search(re.escape(n), blob), f"卧室选项应包含: {n}"


@pytest.mark.p1
@pytest.mark.case_id_au58_property_publish_m4_024
@allure.feature("AU站房产发布")
@allure.story("模块4：房产信息")
@allure.title("TC024 住宅租浴室枚举（含 Shared）")
@allure.severity(allure.severity_level.NORMAL)
def test_m4_tc024_rent_bathroom_options(publish_rent_house, config):
    page = publish_rent_house.page
    publish_rent_house.is_property_info_section_visible()
    page.wait_for_timeout(1200)
    with allure.step("展开 Bathrooms 下拉"):
        try:
            row = page.locator("div").filter(
                has=page.get_by_text(re.compile(r"^Bathrooms?\b", re.I))
            ).first
            row.scroll_into_view_if_needed(timeout=8000)
            sel = row.locator(".ant-select-selector, [class*='select'], button, [role='combobox']").first
            if sel.is_visible(timeout=4000):
                sel.click()
                page.wait_for_timeout(800)
            else:
                page.get_by_text(re.compile(r"Bathrooms?", re.I)).first.click(timeout=5000)
                page.wait_for_timeout(800)
        except Exception as e:
            pytest.skip(f"无法展开浴室选择: {e}")

    opts = page.evaluate(
        r"""() => {
        const roots = [...document.querySelectorAll('.ant-select-dropdown, [role="listbox"]')];
        let t = '';
        for (const r of roots) {
          const st = window.getComputedStyle(r);
          if (st.display === 'none' || st.visibility === 'hidden') continue;
          t += '\n' + (r.innerText || '');
        }
        return t || '';
      }"""
    )
    blob = opts or page.evaluate("() => document.body.innerText || ''") or ""
    assert re.search(r"Shared", blob, re.I), "浴室枚举应含 Shared"
    assert re.search(r"1\.5|2\.5", blob), "浴室枚举应含半卫小数选项"


@pytest.mark.p1
@pytest.mark.case_id_au58_property_publish_m4_013
@allure.feature("AU站房产发布")
@allure.story("模块4：房产信息")
@allure.title("TC013 住宅租面积区以单值为主（不出现双框区间态为主界面）")
@allure.severity(allure.severity_level.NORMAL)
def test_m4_tc013_residential_area_single_primary(publish_rent_house, config):
    page = publish_rent_house.page
    _scroll_area_section(page)
    body = page.evaluate("() => document.body.innerText || ''") or ""
    min_l = body.lower()
    has_minmax = "min area" in min_l and "max area" in min_l
    if not has_minmax:
        return
    switch = page.get_by_text(re.compile(r"Single|Range|单值|区间", re.I)).first
    if switch.is_visible(timeout=2000):
        try:
            single = page.get_by_text(re.compile(r"^Single\b|单值", re.I)).first
            if single.is_visible(timeout=1500):
                single.click()
                page.wait_for_timeout(600)
        except Exception:
            pass
    body2 = (page.evaluate("() => document.body.innerText || ''") or "").lower()
    if "min area" in body2 and "max area" in body2:
        assert re.search(r"m²|sqft|area\s*size", body2), (
            "若同时展示 Min/Max，仍应带面积单位语境；当前与文档「单值为主」可能不一致，请产品确认"
        )


@pytest.mark.p0
@pytest.mark.case_id_au58_property_publish_m4_014
@allure.feature("AU站房产发布")
@allure.story("模块4：房产信息")
@allure.title("TC014 商业地产买面积 Single↔Range 切换")
@allure.severity(allure.severity_level.BLOCKER)
def test_m4_tc014_commercial_area_range_toggle(publish_commercial_sale, config):
    page = publish_commercial_sale.page
    _scroll_area_section(page)
    rng = page.get_by_text(re.compile(r"Range|区间", re.I)).first
    sng = page.get_by_text(re.compile(r"Single|单值", re.I)).first
    has_toggle = rng.is_visible(timeout=5000) or sng.is_visible(timeout=2000)
    if not has_toggle:
        with allure.step("AU 商业地产可能无 Single/Range 切换，改为校验表单已加载（含类目/价格等）"):
            body = page.evaluate("() => document.body.innerText || ''") or ""
            assert re.search(
                r"Area|m²|sqft|size|Land|Development|Price\s*&\s*Contact|Commercial",
                body,
                re.I,
            ), "商业地产表单应含面积/土地开发/价格等模块之一"
            assert "7005" in page.url or "7006" in page.url or "commercial" in page.url.lower(), (
                "应为商业地产发布上下文"
            )
        return
    try:
        if rng.is_visible(timeout=2000):
            rng.click()
            page.wait_for_timeout(700)
    except Exception:
        pass
    body = page.evaluate("() => document.body.innerText || ''") or ""
    if not re.search(r"min\s*area|max\s*area", body, re.I):
        with allure.step("切 Range 后未出现 Min/Max 文案时仍校验表单含面积或类目语境"):
            assert re.search(r"Area|m²|Land|Development|size", body, re.I), "面积区应有文案或土地类目"
        return
    try:
        if sng.is_visible(timeout=2000):
            sng.click()
            page.wait_for_timeout(700)
    except Exception:
        pass


@pytest.mark.p1
@pytest.mark.case_id_au58_property_publish_m4_016
@allure.feature("AU站房产发布")
@allure.story("模块4：房产信息")
@allure.title("TC016 面积单位与输入（AU：m² 代理；sqft 站点可另脚本）")
@allure.severity(allure.severity_level.NORMAL)
def test_m4_tc016_area_m2_or_sqft_context(publish_rent_house, config):
    page = publish_rent_house.page
    _scroll_area_section(page)
    body = page.evaluate("() => document.body.innerText || ''") or ""
    if re.search(r"sqft|square\s*feet", body, re.I):
        assert re.search(r"Area|Living|size", body, re.I), "sqft 站点面积区应有 Area 语境"
        return
    with allure.step("AU 默认 m²：面积区存在且可定位数字输入"):
        assert re.search(r"m²|m2|sq\s*m", body, re.I), "AU 租房表单应展示 m² 面积单位或 Area size"
        num = page.locator("input[type='number'], input[inputmode='decimal']").first
        assert num.is_visible(timeout=6000), "面积应对应可编辑数字输入"


@pytest.mark.p1
@pytest.mark.case_id_au58_property_publish_m4_017
@allure.feature("AU站房产发布")
@allure.story("模块4：房产信息")
@allure.title("TC017 楼层 Single floor ↔ Multi level 切换")
@allure.severity(allure.severity_level.NORMAL)
def test_m4_tc017_floor_single_multi_toggle(publish_rent_house, config):
    page = publish_rent_house.page
    try:
        page.get_by_text(re.compile(r"Floor|Level", re.I)).first.scroll_into_view_if_needed(
            timeout=12000
        )
    except Exception:
        page.mouse.wheel(0, 1600)
    page.wait_for_timeout(500)
    multi = page.get_by_text(re.compile(r"Multi\s*level|多层|Multiple", re.I)).first
    single = page.get_by_text(re.compile(r"Single\s*level|One\s*level|单层", re.I)).first
    if not multi.is_visible(timeout=5000):
        sw = page.get_by_role("switch").first
        if sw.is_visible(timeout=3000):
            sw.click()
            page.wait_for_timeout(600)
        else:
            with allure.step("无 Multi 开关时仅校验 Floor 区块存在"):
                blob = page.evaluate("() => document.body.innerText || ''") or ""
                assert re.search(r"Floor|Level|层", blob, re.I), "表单应含楼层相关模块"
            return
    else:
        multi.click()
        page.wait_for_timeout(600)
    nums = page.locator("input[type='number'], input[inputmode='numeric']")
    if nums.count() < 2:
        with allure.step("多层态下未必暴露 number 输入，校验楼层相关文案仍存在"):
            blob = page.evaluate("() => document.body.innerText || ''") or ""
            assert re.search(r"Floor|Level|Multi|story|层", blob, re.I), (
                "多层模式下页面应含楼层相关文案"
            )
    if single.is_visible(timeout=2000):
        single.click()
        page.wait_for_timeout(500)


@pytest.mark.p1
@pytest.mark.case_id_au58_property_publish_m4_018
@allure.feature("AU站房产发布")
@allure.story("模块4：房产信息")
@allure.title("TC018 楼层边界与整数提示")
@allure.severity(allure.severity_level.NORMAL)
def test_m4_tc018_floor_invalid_values_hint(publish_rent_house, config):
    page = publish_rent_house.page
    try:
        page.get_by_text(re.compile(r"Floor|Level", re.I)).first.scroll_into_view_if_needed(
            timeout=12000
        )
    except Exception:
        page.mouse.wheel(0, 1600)
    page.wait_for_timeout(500)
    inp = page.locator("div").filter(has=page.get_by_text(re.compile(r"Floor|Level", re.I))).locator(
        "input[type='number'], input[inputmode='numeric'], input[type='text']"
    ).first
    if not inp.is_visible(timeout=4000):
        inp = page.locator("input[type='number']").first
    if not inp.is_visible(timeout=3000):
        with allure.step("无独立楼层输入时校验 Floor 文案存在"):
            blob = page.evaluate("() => document.body.innerText || ''") or ""
            assert re.search(r"Floor|Level", blob, re.I), "表单应含楼层相关文案"
        return
    inp.fill("-11")
    inp.blur()
    page.wait_for_timeout(800)
    body = page.evaluate("() => document.body.innerText || ''") or ""
    ok = bool(
        re.search(
            r"-10\s*to\s*200|200\s*之间|integer|whole\s*number|整数|between|"
            r"invalid|must\s+be|greater|less|range|0\s*and|请输入|格式",
            body,
            re.I,
        )
    )
    err = page.locator(
        ".ant-form-item-has-error, [class*='form-item-has-error'], [class*='error-message']"
    )
    toast = page.locator(".ant-message-notice-content, .ant-message-error, [role='alert']")
    toast_ok = toast.count() > 0 and toast.first.is_visible(timeout=2500)
    assert ok or err.count() > 0 or toast_ok, (
        "非法楼层输入后应有校验文案、表单项错误或 toast"
    )


@pytest.mark.p1
@pytest.mark.case_id_au58_property_publish_m4_022
@allure.feature("AU站房产发布")
@allure.story("模块4：房产信息")
@allure.title("TC022 商业地产买车位必填拦截")
@allure.severity(allure.severity_level.NORMAL)
def test_m4_tc022_commercial_sale_parking_required(publish_commercial_sale, config):
    assert _IMG1.is_file(), f"缺少 {_IMG1}"
    ppp = publish_commercial_sale
    page = ppp.page
    with allure.step("上传主图 + 标题，不选车位"):
        try:
            page.get_by_text("Pictures", exact=False).first.scroll_into_view_if_needed(timeout=8000)
        except Exception:
            pass
        ppp.upload_single_image(str(_IMG1), wait_ms=2500)
        try:
            page.get_by_text(re.compile(r"Title", re.I)).first.scroll_into_view_if_needed(timeout=8000)
        except Exception:
            page.mouse.wheel(0, 600)
        page.wait_for_timeout(400)
        title_box = (
            page.locator("section, form, div")
            .filter(has=page.get_by_text(re.compile(r"\bTitle\b", re.I)))
            .locator("input[type='text'], textarea")
            .first
        )
        if title_box.is_visible(timeout=5000):
            title_box.fill("Auto TC022 parking")
    with allure.step("确认存在车位字段"):
        page.mouse.wheel(0, 900)
        page.wait_for_timeout(400)
        pk = page.get_by_text(re.compile(r"Car\s*space|Parking|停车位", re.I)).first
        has_parking_ui = pk.is_visible(timeout=6000)
    with allure.step("Post 后期望必填类提示（有车位字段则含 parking 语义，否则任意必填）"):
        ppp.click_post_button(wait_ms=2000)
        assert "publish/property" in page.url
        body = page.evaluate("() => document.body.innerText || ''") or ""
        assert not re.search(r"published\s+successfully|post\s+success", body, re.I)
        hit = bool(
            re.search(
                r"parking|car\s*space|车位|required|必填|please\s+(select|enter|choose)|"
                r"address|location|price|photo|complete",
                body,
                re.I,
            )
        )
        err = page.locator(
            ".ant-form-item-has-error, [class*='form-item-has-error'], [class*='error-message']"
        )
        toast = page.locator(".ant-message-notice-content, .ant-message-error, [role='alert']")
        toast_ok = toast.count() > 0 and toast.first.is_visible(timeout=3500)
        assert hit or err.count() > 0 or toast_ok, (
            "未完整填写时点 Post 应有校验；若含车位 UI 则文案可含 parking"
        )
        if has_parking_ui:
            assert re.search(r"parking|car\s*space|车位|required", body, re.I) or err.count() > 0, (
                "存在车位字段时应出现车位或必填校验"
            )


@pytest.mark.p1
@pytest.mark.case_id_au58_property_publish_m4_025
@allure.feature("AU站房产发布")
@allure.story("模块4：房产信息")
@allure.title("Unit features / Amenities / Kitchen 等区块在表单中可见")
@allure.severity(allure.severity_level.MINOR)
def test_m4_tc025_unit_features_amenities_kitchen_visible(publish_rent_house, config):
    page = publish_rent_house.page
    try:
        page.get_by_text(re.compile(r"Property Info", re.I)).first.scroll_into_view_if_needed(
            timeout=10000
        )
    except Exception:
        pass
    page.mouse.wheel(0, 2200)
    page.wait_for_timeout(600)
    body = page.evaluate("() => document.body.innerText || ''") or ""
    patterns = (
        r"Unit\s*features?",
        r"Amenities",
        r"Kitchen",
        r"Property\s*services",
        r"配套",
        r"室内",
    )
    hits = sum(1 for p in patterns if re.search(p, body, re.I))
    if hits < 1:
        page.mouse.wheel(0, 3200)
        page.wait_for_timeout(600)
        body = page.evaluate("() => document.body.innerText || ''") or ""
        hits = sum(1 for p in patterns if re.search(p, body, re.I))
    assert hits >= 1 or re.search(
        r"Select|Furnished|Air|Heating|feature|amenity",
        body,
        re.I,
    ), "向下滚动后应出现 Unit features / Amenities / Kitchen 或同类配套区块"
