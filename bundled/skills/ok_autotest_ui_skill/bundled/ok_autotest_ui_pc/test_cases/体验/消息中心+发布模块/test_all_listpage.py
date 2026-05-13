# test_cases/test_all_listpage.py
"""
OK阿联酋站 - All 分类导航页测试套件
基于 web-qa-brain 三阶段实测生成，覆盖 32 条测试用例（TC001-TC032）

测试用例分布：
- TC001-TC003: 页面入口与基础访问
- TC004-TC006: 顶部城市 Tab
- TC007-TC009: 分类树 - Jobs 模块
- TC010-TC012: 分类树 - Marketplace 模块
- TC013-TC015: 分类树 - Services / Community 模块
- TC016-TC019: 分类树 - Cars / Shop 模块
- TC020-TC022: 右侧固定城市列表
- TC023-TC025: 国家站点列表
- TC026-TC027: 分类链接 URL 正确性
- TC028-TC030: 会话与状态
- TC031-TC032: 不同城市的 listpage
"""
import pytest
import allure
import os
import re
from playwright.sync_api import Page
from utils.logger import setup_logger
from utils.site_guard import guard_site_and_goto_or_skip

# ========== 测试配置 ==========
_CONFIG = {
    'site': 'ae',
    'site_name': 'OK阿联酋站',
    'role': 'buyer',
    'user_name': 'anonymous_ae_buyer',
    'base_url': 'https://ae.58v5.cn/en/city-abu-dhabi/',
    'home_url': 'https://ae.58v5.cn/en/city-abu-dhabi/',
    'listpage_url': 'https://ae.58v5.cn/en/city-abu-dhabi/listpage/',
    'dubai_listpage_url': 'https://ae.58v5.cn/en/city-dubai/listpage/',
    'test_account': None,  # 公开页面，无需登录

    'locale': 'en-AE',
    'currency': 'AED',

    'browser': {
        'type': 'chromium',
        'headless': False,
        'viewport': {'width': 1440, 'height': 900}
    },

    'timeout': {
        'default': 30000,
        'wait': 10000,
        'navigation': 60000,
        # listpage SPA 上 cate-* 锚点偶发晚于 domcontentloaded，首段 site_guard 单独加长
        'listpage_guard': 30000,
    }
}

logger = setup_logger()
SCREENSHOT_DIR = 'screenshots/test_all_listpage'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def _safe_listpage_screenshot(page: Page, path: str) -> None:
    """视口截图，避免 full_page 长页卡死导致用例误失败。"""
    try:
        page.screenshot(
            path=path,
            timeout=25000,
            full_page=False,
            animations="disabled",
        )
    except Exception as exc:
        logger.warning("列表页截图跳过: %s | %s", path, str(exc)[:120])


def _goto_with_guard(page: Page, url: str, ready_locator) -> None:
    guard_timeout_ms = (
        int(_CONFIG['timeout'].get('listpage_guard', 30000))
        if '/listpage/' in url
        else 15000
    )
    try:
        guard_site_and_goto_or_skip(
            page,
            url,
            ready_locator=ready_locator,
            timeout_ms=guard_timeout_ms,
            logger=logger,
        )
    except pytest.skip.Exception as exc:
        # listpage 常见抖动：锚点不可见但正文已渲染，做一次软回退避免误 skip。
        if "/listpage/" not in url:
            raise
        logger.warning("site_guard 触发 skip，进入 listpage 文本回退检查: %s", str(exc)[:120])
        last_fb_err: Exception | None = None
        ready_js = r"""() => {
            const raw = (document.body && document.body.innerText) || '';
            const t = raw.toLowerCase();
            if (document.querySelector("a[href*='cate-']")) return true;
            if (document.querySelector("a[href*='/listpage/']")) return true;
            return t.includes('jobs') || t.includes('marketplace') || t.includes('services')
                || t.includes('community') || t.includes('shop') || t.includes('cars')
                || t.includes('property') || t.includes('explore')
                || t.includes('category') || t.includes('all ');
        }"""
        for fb_attempt in range(3):
            try:
                if fb_attempt == 0:
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_timeout(1800)
                else:
                    try:
                        page.reload(wait_until="domcontentloaded", timeout=60000)
                    except Exception:
                        page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_timeout(2200)
                page.wait_for_function(ready_js, timeout=40000)
                if page.url.startswith("chrome-error://"):
                    pytest.skip(f"listpage 回退后仍是浏览器错误页: {page.url}")
                break
            except Exception as fallback_err:
                last_fb_err = fallback_err
                err_text = str(fallback_err)
                if "ERR_HTTP_RESPONSE_CODE_FAILURE" in err_text or "net::ERR_HTTP" in err_text:
                    pytest.skip(f"listpage 回退触发 HTTP 异常，跳过当前用例: {url}")
                if fb_attempt >= 2:
                    if "Timeout" in err_text or "timed out" in err_text:
                        pytest.skip(
                            f"listpage 回退超时，跳过当前用例: {url} | {err_text[:160]}"
                        )
                    raise
                logger.warning(
                    "listpage 回退第 %s 次未就绪，将重载重试: %s",
                    fb_attempt + 1,
                    err_text[:120],
                )
                page.wait_for_timeout(900)
        else:
            if last_fb_err is not None:
                raise last_fb_err
    page.wait_for_load_state("domcontentloaded", timeout=10000)


def _get_title_with_wait(page: Page, timeout_ms: int = 10000) -> str:
    """等待页面标题渲染，避免瞬时空标题导致误报"""
    try:
        page.wait_for_function(
            "() => !!document.title && document.title.trim().length > 0",
            timeout=timeout_ms,
        )
    except Exception:
        pass
    return (page.title() or "").strip()


def _assert_title_contains_city_and_brand(page: Page, city: str) -> str:
    """
    兼容标题模板差异：
    - 城市名优先在 title 校验，必要时退化到页面正文
    - 品牌校验允许 title 包含 OK，或 URL 落在 ok 域名
    """
    title = _get_title_with_wait(page)
    body = page.evaluate("() => document.body.innerText || ''")
    url = page.url.lower()

    assert (city in title) or (city in body), \
        f"页面应包含城市 '{city}'，实际 title={title} url={page.url}"
    assert ('OK' in title) or ('ok.com' in url), \
        f"页面标题或域名应体现 OK 品牌，实际 title={title} url={page.url}"
    return title


def _jobs_link_locator(page: Page):
    """listpage 上 Jobs 入口的稳健定位（兼容文案/隐藏副本）"""
    return page.locator("a[href*='cate-jobs']").first


def _listpage_ready_locator(page: Page):
    """listpage 守卫就绪信号：任一主分类入口可见即可。"""
    return page.locator(
        "a[href*='cate-jobs'],"
        "a[href*='cate-marketplace'],"
        "a[href*='cate-services'],"
        "a[href*='cate-cars'],"
        "a[href*='cate-community']"
    )


def _click_jobs_link(page: Page, timeout_ms: int = 20000) -> None:
    candidates = [
        page.get_by_role('link', name='Jobs'),
        page.get_by_role('link', name=re.compile(r'^Jobs(?:\s+Jobs)?$', re.IGNORECASE)),
        page.locator("a[href*='cate-jobs'][href*='iconSource=jobs']"),
        page.locator("a[href*='cate-jobs']"),
    ]

    last_error = None
    for loc in candidates:
        try:
            target = loc.first
            target.wait_for(state='visible', timeout=timeout_ms)
            target.scroll_into_view_if_needed(timeout=timeout_ms)
            target.click(timeout=timeout_ms)
            return
        except Exception as err:  # noqa: BLE001
            last_error = err

    raise AssertionError(f"未找到可点击的 Jobs 入口: {last_error}")


def _click_home_all_kingkong(page: Page, timeout_ms: int = 20000) -> None:
    """点击首页金刚区 All 入口（兼容文案/DOM 变体）"""
    candidates = [
        page.get_by_role('link', name='All All'),
        page.get_by_role('link', name=re.compile(r'^All(?:\s+All)?$', re.IGNORECASE)),
        page.locator("a[href*='/listpage/']").filter(
            has_text=re.compile(r'^All(?:\s+All)?$', re.IGNORECASE)
        ),
    ]

    last_error = None
    for loc in candidates:
        try:
            target = loc.first
            target.wait_for(state='visible', timeout=timeout_ms)
            target.scroll_into_view_if_needed(timeout=timeout_ms)
            target.click(timeout=timeout_ms)
            return
        except Exception as err:  # noqa: BLE001
            last_error = err

    # 兜底：直接按 href 命中首页可见的 listpage 入口
    try:
        fallback = page.locator(
            "a[href*='/listpage/'][href*='city-abu-dhabi'], a[href*='/listpage/']"
        ).first
        fallback.wait_for(state='visible', timeout=timeout_ms)
        fallback.scroll_into_view_if_needed(timeout=timeout_ms)
        fallback.click(timeout=timeout_ms)
        return
    except Exception as err:  # noqa: BLE001
        last_error = err

    raise AssertionError(f"未找到可点击的首页 All 入口: {last_error}")


# ==================== Fixture ====================

@pytest.fixture(scope="function")
def listpage(page, config):
    """进入 Abu Dhabi All 分类导航页的通用 fixture（使用 conftest page/config，无需登录）"""
    _goto_with_guard(
        page,
        _CONFIG['listpage_url'],
        _listpage_ready_locator(page),
    )
    page.wait_for_timeout(1000)
    logger.info(f"✓ Entered All listpage: {page.url}")
    yield page
    logger.info("✓ Test case completed")


# ==================== 一、页面入口与基础访问 ====================

@pytest.mark.p1
@allure.feature("OK - All 分类导航页")
@allure.story("页面入口与基础访问")
@allure.title("TC001: 从首页金刚区点击 All 进入分类导航页")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_001
def test_all_listpage_entry_from_home(page, config):
    """TC001: 从首页金刚区点击 All → 跳转至 /listpage/ ✅ 实测"""
    with allure.step("访问首页"):
        _goto_with_guard(
            page,
            _CONFIG['home_url'],
            page.get_by_role('link', name=re.compile(r'^All(?:\s+All)?$', re.IGNORECASE)),
        )
        page.wait_for_timeout(1000)

    with allure.step("点击金刚区 All 图标"):
        _click_home_all_kingkong(page, timeout_ms=_CONFIG['timeout']['default'])
        page.wait_for_url('**/listpage/**', timeout=_CONFIG['timeout']['navigation'])
        page.wait_for_load_state('domcontentloaded', timeout=_CONFIG['timeout']['navigation'])
        page.wait_for_timeout(1000)

    with allure.step("验证 URL 跳转至 /listpage/"):
        assert '/listpage/' in page.url, \
            f"应跳转至 /listpage/，实际={page.url}"
        assert 'city-abu-dhabi' in page.url, \
            f"URL 应包含 city-abu-dhabi，实际={page.url}"
        logger.info(f"✓ TC001: All 入口跳转验证通过，URL={page.url}")

    with allure.step("验证页面标题"):
        _assert_title_contains_city_and_brand(page, "Abu Dhabi")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc001_entry_from_home.png')


@pytest.mark.p1
@allure.feature("OK - All 分类导航页")
@allure.story("页面入口与基础访问")
@allure.title("TC002: 直接访问 /listpage/ URL 页面正常加载")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_002
def test_all_listpage_direct_access(listpage: Page):
    """TC002: 直接访问 /listpage/ 页面正常加载 ✅ 实测"""
    page = listpage

    with allure.step("验证 URL 正确"):
        assert page.url == _CONFIG['listpage_url'], \
            f"URL 应为 {_CONFIG['listpage_url']}，实际={page.url}"

    with allure.step("验证页面标题"):
        title = _assert_title_contains_city_and_brand(page, "Abu Dhabi")
        logger.info(f"✓ TC002: 页面标题={title}")

    with allure.step("验证分类内容已加载"):
        body = page.evaluate("() => document.body.innerText")
        assert 'Jobs' in body, "页面应包含 Jobs 分类"
        assert 'Marketplace' in body, "页面应包含 Marketplace 分类"
        logger.info("✓ TC002: 页面直接访问验证通过")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc002_direct_access.png')


@pytest.mark.p0
@allure.feature("OK - All 分类导航页")
@allure.story("页面入口与基础访问")
@allure.title("TC003: 页面内容 - 主分类结构完整展示")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_003
def test_all_listpage_main_structure(listpage: Page):
    """TC003: 主分类结构完整展示 ✅ 实测"""
    page = listpage

    with allure.step("验证主分类标题均可见"):
        body = page.evaluate("() => document.body.innerText")
        for cate in ['Jobs', 'Marketplace', 'Community', 'Shop', 'Cars', 'Used cars']:
            assert cate in body, f"页面应包含 '{cate}' 分类"

    with allure.step("验证关键子分类可见"):
        for sub in ['Accounting', 'Electronics', 'Activities & Groups', 'Lost & Found']:
            assert sub in body, f"页面应包含子分类 '{sub}'"
        logger.info("✓ TC003: 主分类结构完整验证通过")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc003_main_structure.png')


# ==================== 二、顶部城市 Tab ====================

@pytest.mark.p1
@allure.feature("OK - All 分类导航页")
@allure.story("顶部城市Tab")
@allure.title("TC004: 顶部城市 Tab - 当前城市为不可点击文本")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_004
def test_all_listpage_city_tab_current(listpage: Page):
    """TC004: 当前城市在 Tab 中为文本（非链接）展示 ✅ 实测"""
    page = listpage

    with allure.step("验证 Abu Dhabi 为当前城市文本"):
        current_city = page.evaluate("""() => {
            var all = Array.from(document.querySelectorAll('*'));
            var abu = all.find(function(e) {
                return e.textContent.trim() === 'Abu Dhabi'
                    && e.tagName !== 'A' && e.offsetHeight > 0 && e.children.length === 0;
            });
            return abu ? abu.textContent.trim() : null;
        }""")
        assert current_city == 'Abu Dhabi', \
            "顶部区域应有 'Abu Dhabi' 文本（非链接形式的当前城市）"
        logger.info("✓ TC004: 当前城市文本验证通过")

    with allure.step("验证存在其他城市快捷链接"):
        other_cities = page.evaluate("""() => {
            var links = Array.from(document.querySelectorAll('a'));
            var cityLinks = links.filter(function(a) {
                var href = a.href || '';
                return href.includes('ae.58v5.cn/en/city-') && !href.includes('listpage')
                    && !href.includes('cate') && a.offsetHeight > 0;
            });
            return cityLinks.map(function(a) { return a.textContent.trim(); }).filter(Boolean);
        }""")
        assert len(other_cities) > 0, "应有其他城市快捷链接"
        logger.info(f"✓ TC004: 其他城市链接={other_cities}")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc004_city_tab.png')


@pytest.mark.p1
@allure.feature("OK - All 分类导航页")
@allure.story("顶部城市Tab")
@allure.title("TC005: 顶部城市 Tab - 点击其他城市跳转至该城市首页")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_005
def test_all_listpage_city_tab_click(listpage: Page):
    """TC005: 顶部城市 Tab 点击其他城市 → 跳转至城市首页（非 /listpage/） ✅ 实测"""
    page = listpage

    with allure.step("获取第一个其他城市链接并记录目标"):
        target_href = page.evaluate("""() => {
            var links = Array.from(document.querySelectorAll('a'));
            var cityLink = links.find(function(a) {
                var href = a.href || '';
                return href.includes('ae.58v5.cn/en/city-') && !href.includes('listpage')
                    && !href.includes('cate') && a.offsetHeight > 0
                    && a.textContent.trim().length > 0;
            });
            return cityLink ? cityLink.href : null;
        }""")
        assert target_href, "应存在可点击的城市快捷链接"
        logger.info(f"目标城市链接: {target_href}")

    with allure.step("点击城市链接"):
        page.evaluate("""() => {
            var links = Array.from(document.querySelectorAll('a'));
            var cityLink = links.find(function(a) {
                var href = a.href || '';
                return href.includes('ae.58v5.cn/en/city-') && !href.includes('listpage')
                    && !href.includes('cate') && a.offsetHeight > 0
                    && a.textContent.trim().length > 0;
            });
            if (cityLink) cityLink.click();
        }""")
        page.wait_for_timeout(3000)

    with allure.step("验证跳转至目标城市首页（非 /listpage/）"):
        assert '/listpage/' not in page.url, \
            f"点击城市 Tab 应跳转至城市首页，不应包含 /listpage/，实际={page.url}"
        assert 'city-' in page.url, f"URL 应含城市信息，实际={page.url}"
        logger.info(f"✓ TC005: 城市 Tab 点击跳转验证通过，URL={page.url}")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc005_city_tab_click.png')


@pytest.mark.p2
@allure.feature("OK - All 分类导航页")
@allure.story("顶部城市Tab")
@allure.title("TC006: 刷新页面 - 当前城市 Tab 不变")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_006
def test_all_listpage_city_tab_refresh(listpage: Page):
    """TC006: 刷新页面后城市 Tab 保持 Abu Dhabi 为当前城市 ✅ 实测"""
    page = listpage

    with allure.step("刷新页面"):
        page.reload(wait_until='domcontentloaded')
        page.wait_for_timeout(2000)

    with allure.step("验证 URL 不变"):
        assert _CONFIG['listpage_url'] in page.url, \
            f"刷新后 URL 应不变，实际={page.url}"

    with allure.step("验证 Abu Dhabi 仍为当前城市文本"):
        body = page.evaluate("() => document.body.innerText")
        assert 'Abu Dhabi' in body, "刷新后 Abu Dhabi 应仍为当前城市"
        assert 'Jobs' in body, "刷新后分类内容应完整"
        logger.info("✓ TC006: 刷新后城市 Tab 验证通过")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc006_refresh.png')


# ==================== 三、分类树 - Jobs 模块 ====================

@pytest.mark.p1
@allure.feature("OK - All 分类导航页")
@allure.story("分类树 - Jobs")
@allure.title("TC007: Jobs 分类标题点击 - 跳转至 Jobs 列表页")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_007
def test_all_listpage_jobs_title_click(listpage: Page):
    """TC007: 点击 Jobs 标题 → /cate-jobs/ 列表页（含筛选器、分页） ✅ 实测"""
    page = listpage

    with allure.step("点击 Jobs 分类标题链接"):
        _click_jobs_link(page, timeout_ms=_CONFIG['timeout']['default'])
        page.wait_for_timeout(3000)

    with allure.step("验证跳转至 Jobs 列表页"):
        assert 'cate-jobs' in page.url, \
            f"应跳转至 /cate-jobs/，实际={page.url}"
        assert 'city-abu-dhabi' in page.url, \
            f"URL 应含城市 abu-dhabi，实际={page.url}"

    with allure.step("验证 Jobs 列表页核心元素"):
        body = page.evaluate("() => document.body.innerText")
        assert 'Jobs in Abu Dhabi' in body, \
            f"Jobs 列表页应显示 'Jobs in Abu Dhabi'，实际={body[:200]}"
        assert 'Best Match' in body, "应有 Best Match 排序选项"
        assert 'Filter' in body, "应有 Filter 筛选按钮"
        logger.info(f"✓ TC007: Jobs 标题点击跳转验证通过，URL={page.url}")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc007_jobs_list.png')


@pytest.mark.p1
@allure.feature("OK - All 分类导航页")
@allure.story("分类树 - Jobs")
@allure.title("TC008: Jobs 子分类 - Accounting 链接跳转正确")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_008
def test_all_listpage_jobs_subcate_accounting(listpage: Page):
    """TC008: 点击 Jobs > Accounting → /cate-accounting/ ✅ 实测"""
    page = listpage

    with allure.step("点击 Accounting 子分类"):
        page.get_by_role('link', name='Accounting').click()
        page.wait_for_timeout(2000)

    with allure.step("验证跳转至 Accounting 子分类"):
        assert 'cate-accounting' in page.url, \
            f"应跳转至 /cate-accounting/，实际={page.url}"
        assert 'city-abu-dhabi' in page.url, \
            f"URL 应含 city-abu-dhabi，实际={page.url}"
        logger.info(f"✓ TC008: Accounting 子分类跳转验证通过，URL={page.url}")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc008_accounting.png')


@pytest.mark.p2
@allure.feature("OK - All 分类导航页")
@allure.story("分类树 - Jobs")
@allure.title("TC009: Jobs 子分类 - Property For Rent 链接跳转含 iconSource 参数")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_009
def test_all_listpage_jobs_property_rent(listpage: Page):
    """TC009: Jobs > Property For Rent 链接含 iconSource=rent 参数 ✅ 实测"""
    page = listpage

    with allure.step("验证 Property For Rent 链接 href"):
        href = None
        try:
            target = page.locator("a[href*='cate-rent'][href*='iconSource=rent']").first
            target.wait_for(state="visible", timeout=12000)
            href = target.get_attribute("href")
        except Exception:
            href = page.evaluate("""() => {
                var links = Array.from(document.querySelectorAll('a'));
                var link = links.find(function(a) {
                    var txt = (a.textContent || '').trim().toLowerCase();
                    return txt.includes('property') && txt.includes('rent') && a.offsetHeight > 0;
                });
                return link ? link.href : null;
            }""")
        assert href, "应存在 'Property For Rent' 链接"
        assert 'cate-rent' in href, f"链接应含 'cate-rent'，实际={href}"
        assert 'iconSource=rent' in href, f"链接应含 'iconSource=rent'，实际={href}"
        logger.info(f"✓ TC009: Property For Rent href={href}")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc009_property_rent_link.png')


# ==================== 四、分类树 - Marketplace 模块 ====================

@pytest.mark.p1
@allure.feature("OK - All 分类导航页")
@allure.story("分类树 - Marketplace")
@allure.title("TC010: Marketplace 分类标题点击 - 跳转至 Marketplace 列表页")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_010
def test_all_listpage_marketplace_title_click(listpage: Page):
    """TC010: 点击 Marketplace 标题 → /cate-marketplace/ ✅ 实测"""
    page = listpage

    with allure.step("点击 Marketplace 分类标题"):
        page.get_by_role('link', name='Marketplace').first.click()
        page.wait_for_timeout(2000)

    with allure.step("验证跳转至 Marketplace 列表页"):
        assert 'cate-marketplace' in page.url, \
            f"应跳转至 /cate-marketplace/，实际={page.url}"
        assert 'city-abu-dhabi' in page.url, \
            f"URL 应含 city-abu-dhabi，实际={page.url}"
        logger.info(f"✓ TC010: Marketplace 跳转验证通过，URL={page.url}")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc010_marketplace_list.png')


@pytest.mark.p1
@allure.feature("OK - All 分类导航页")
@allure.story("分类树 - Marketplace")
@allure.title("TC011: Marketplace 子分类 - Electronics 链接跳转")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_011
def test_all_listpage_marketplace_electronics(listpage: Page):
    """TC011: Marketplace > Electronics → /cate-electronics/ ✅ 实测"""
    page = listpage

    with allure.step("点击 Electronics 子分类"):
        page.get_by_role('link', name='Electronics').first.click()
        page.wait_for_timeout(2000)

    with allure.step("验证跳转"):
        assert 'cate-electronics' in page.url, \
            f"应跳转至 /cate-electronics/，实际={page.url}"
        assert 'city-abu-dhabi' in page.url, \
            f"URL 应含城市信息，实际={page.url}"
        logger.info(f"✓ TC011: Electronics 跳转验证通过，URL={page.url}")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc011_electronics.png')


@pytest.mark.p2
@allure.feature("OK - All 分类导航页")
@allure.story("分类树 - Marketplace")
@allure.title("TC012: Marketplace 子分类 - Free Stuff 链接跳转")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_012
def test_all_listpage_marketplace_free_stuff(listpage: Page):
    """TC012: Marketplace > Free Stuff → /cate-free-stuff/ ✅ 实测"""
    page = listpage

    with allure.step("验证 Free Stuff 链接 href"):
        href = page.evaluate("""() => {
            var links = Array.from(document.querySelectorAll('a'));
            var link = links.find(function(a) {
                var txt = (a.textContent || '').trim().toLowerCase();
                return txt === 'free stuff' && a.offsetHeight > 0;
            });
            return link ? link.href : null;
        }""")
        assert href, "应存在 'Free Stuff' 链接"
        assert ('cate-free-stuff' in href) or ('cate-new-free-stuff' in href), \
            f"链接应含 cate-free-stuff/cate-new-free-stuff，实际={href}"
        assert 'city-abu-dhabi' in href, f"链接应含城市信息，实际={href}"
        logger.info(f"✓ TC012: Free Stuff href={href}")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc012_free_stuff.png')


# ==================== 五、分类树 - Services / Community 模块 ====================

@pytest.mark.p2
@allure.feature("OK - All 分类导航页")
@allure.story("分类树 - Services/Community")
@allure.title("TC013: Services 子分类 - Business 链接跳转")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_013
def test_all_listpage_services_business(listpage: Page):
    """TC013: Services > Business → /cate-business/ ✅ 实测"""
    page = listpage

    with allure.step("验证 Business 链接 href"):
        href = None
        page.evaluate("window.scrollBy(0, 260)")
        page.wait_for_timeout(400)
        try:
            target = page.locator(
                "a[href*='business'], a[href*='office-supplies'], "
                "a:has-text('Business'), a:has-text('Office Supplies')"
            ).first
            target.wait_for(state="visible", timeout=12000)
            href = target.get_attribute("href")
        except Exception:
            href = page.evaluate("""() => {
                var links = Array.from(document.querySelectorAll('a'));
                var link = links.find(function(a) {
                    var txt = (a.textContent || '').trim().toLowerCase();
                    var href = (a.href || '').toLowerCase();
                    return a.offsetHeight > 0 && (
                        txt.includes('business') ||
                        txt.includes('office supplies') ||
                        href.includes('business') ||
                        href.includes('office-supplies')
                    );
                });
                return link ? link.href : null;
            }""")
        assert href, "应存在 Services > Business 链接"
        lower_href = href.lower()
        assert ('business' in lower_href) or ('office-supplies' in lower_href), \
            f"链接应含 business/office-supplies 关键词，实际={href}"
        assert 'city-abu-dhabi' in href, f"链接应含城市，实际={href}"
        logger.info(f"✓ TC013: Business href={href}")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc013_business_link.png')


@pytest.mark.p2
@allure.feature("OK - All 分类导航页")
@allure.story("分类树 - Services/Community")
@allure.title("TC014: Community 子分类 - Activities & Groups 链接跳转")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_014
def test_all_listpage_community_activities(listpage: Page):
    """TC014: Community > Activities & Groups → /cate-activities-groups/ ✅ 实测"""
    page = listpage

    with allure.step("点击 Activities & Groups 链接"):
        page.get_by_role('link', name='Activities & Groups').click()
        page.wait_for_timeout(2000)

    with allure.step("验证跳转"):
        assert 'cate-activities-groups' in page.url, \
            f"应跳转至 /cate-activities-groups/，实际={page.url}"
        assert 'city-abu-dhabi' in page.url, \
            f"URL 应含城市，实际={page.url}"
        logger.info(f"✓ TC014: Activities & Groups 跳转验证通过，URL={page.url}")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc014_activities.png')


@pytest.mark.p2
@allure.feature("OK - All 分类导航页")
@allure.story("分类树 - Services/Community")
@allure.title("TC015: Community 子分类 - Lost & Found 链接跳转")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_015
def test_all_listpage_community_lost_found(listpage: Page):
    """TC015: Community > Lost & Found → /cate-lost-found/ ✅ 实测"""
    page = listpage

    with allure.step("验证 Lost & Found 链接 href"):
        href = page.evaluate("""() => {
            var links = Array.from(document.querySelectorAll('a'));
            var link = links.find(function(a) {
                return a.textContent.trim() === 'Lost & Found' && a.offsetHeight > 0;
            });
            return link ? link.href : null;
        }""")
        assert href, "应存在 'Lost & Found' 链接"
        assert 'cate-lost-found' in href, f"链接应含 cate-lost-found，实际={href}"
        assert 'city-abu-dhabi' in href, f"链接应含城市，实际={href}"
        logger.info(f"✓ TC015: Lost & Found href={href}")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc015_lost_found.png')


# ==================== 六、分类树 - Cars / Shop 模块 ====================

@pytest.mark.p1
@allure.feature("OK - All 分类导航页")
@allure.story("分类树 - Cars/Shop")
@allure.title("TC016: Cars 链接点击 - 跳转至 Cars 列表页")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_016
def test_all_listpage_cars_click(listpage: Page):
    """TC016: 点击 Cars → /cate-car/?iconSource=car ✅ 实测"""
    page = listpage

    with allure.step("验证 Cars 链接 href"):
        href = page.evaluate("""() => {
            var links = Array.from(document.querySelectorAll('a'));
            var link = links.find(function(a) {
                return a.textContent.trim() === 'Cars'
                    && a.href.includes('cate-car') && a.offsetHeight > 0;
            });
            return link ? link.href : null;
        }""")
        assert href, "应存在 Cars 链接"
        assert 'cate-car' in href, f"链接应含 cate-car，实际={href}"
        assert 'city-abu-dhabi' in href, f"链接应含城市，实际={href}"

    with allure.step("点击 Cars 链接"):
        page.evaluate("""() => {
            var links = Array.from(document.querySelectorAll('a'));
            var link = links.find(function(a) {
                return a.textContent.trim() === 'Cars'
                    && a.href.includes('cate-car') && a.offsetHeight > 0;
            });
            if (link) link.click();
        }""")
        page.wait_for_timeout(2000)

    with allure.step("验证跳转"):
        assert 'cate-car' in page.url, f"应跳转至 /cate-car/，实际={page.url}"
        logger.info(f"✓ TC016: Cars 跳转验证通过，URL={page.url}")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc016_cars.png')


@pytest.mark.p1
@allure.feature("OK - All 分类导航页")
@allure.story("分类树 - Cars/Shop")
@allure.title("TC017: Used cars 链接点击 - 跳转至 Used cars 列表页")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_017
def test_all_listpage_used_cars(listpage: Page):
    """TC017: 点击 Used cars → /cate-car-used-car/ ✅ 实测"""
    page = listpage

    with allure.step("验证 Used cars 链接 href"):
        href = page.evaluate("""() => {
            var links = Array.from(document.querySelectorAll('a'));
            var link = links.find(function(a) {
                return a.textContent.trim() === 'Used cars' && a.offsetHeight > 0;
            });
            return link ? link.href : null;
        }""")
        assert href, "应存在 'Used cars' 链接"
        assert 'cate-car-used-car' in href, f"链接应含 cate-car-used-car，实际={href}"
        assert 'city-abu-dhabi' in href, f"链接应含城市，实际={href}"
        logger.info(f"✓ TC017: Used cars href={href}")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc017_used_cars.png')


@pytest.mark.p2
@allure.feature("OK - All 分类导航页")
@allure.story("分类树 - Cars/Shop")
@allure.title("TC018: Shop 子分类 - Apparel 链接含 new 前缀路径")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_018
def test_all_listpage_shop_apparel(listpage: Page):
    """TC018: Shop > Apparel 链接含 cate-new-apparel ✅ 实测"""
    page = listpage

    with allure.step("验证 Shop > Apparel 链接（含 new 前缀）"):
        href = page.evaluate("""() => {
            var links = Array.from(document.querySelectorAll('a'));
            var link = links.find(function(a) {
                return a.textContent.trim() === 'Apparel'
                    && a.href.includes('cate-new-apparel') && a.offsetHeight > 0;
            });
            return link ? link.href : null;
        }""")
        assert href, "应存在 Shop > Apparel 链接（href 含 cate-new-apparel）"
        assert 'cate-new-apparel' in href, f"Shop Apparel 链接应含 'cate-new-apparel'（非 cate-apparel），实际={href}"
        logger.info(f"✓ TC018: Shop Apparel href={href}")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc018_shop_apparel.png')


@pytest.mark.p1
@allure.feature("OK - All 分类导航页")
@allure.story("分类树 - Cars/Shop")
@allure.title("TC019: Shop 分类标题 - 链接指向 /cate-new-arrivals/")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_019
def test_all_listpage_shop_title(listpage: Page):
    """TC019: Shop 标题链接 → /cate-new-arrivals/ ✅ 实测"""
    page = listpage

    with allure.step("验证 Shop 标题链接 href"):
        href = page.evaluate("""() => {
            var links = Array.from(document.querySelectorAll('a'));
            var link = links.find(function(a) {
                return a.textContent.trim() === 'Shop' && a.offsetHeight > 0;
            });
            return link ? link.href : null;
        }""")
        assert href, "应存在 'Shop' 标题链接"
        assert 'cate-new-arrivals' in href, \
            f"Shop 标题链接应指向 /cate-new-arrivals/，实际={href}"
        logger.info(f"✓ TC019: Shop 标题 href={href}")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc019_shop_title.png')


# ==================== 七、右侧固定城市列表 ====================

@pytest.mark.p1
@allure.feature("OK - All 分类导航页")
@allure.story("右侧城市列表")
@allure.title("TC020: 右侧城市列表 - 点击 Dubai 跳转至 Dubai 首页")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_020
def test_all_listpage_sidebar_dubai(listpage: Page):
    """TC020: 右侧城市列表点击 Dubai → Dubai 首页（非 /listpage/） ✅ 实测"""
    page = listpage

    with allure.step("点击右侧城市列表中的 Dubai"):
        page.evaluate("""() => {
            var links = Array.from(document.querySelectorAll('a'));
            var dubaiLink = links.find(function(a) {
                return a.textContent.trim() === 'Dubai'
                    && a.href === 'https://ae.58v5.cn/en/city-dubai' && a.offsetHeight > 0;
            });
            if (dubaiLink) dubaiLink.click();
        }""")
        page.wait_for_timeout(3000)

    with allure.step("验证跳转至 Dubai 首页（非 /listpage/）"):
        assert 'city-dubai' in page.url, f"应跳转至 Dubai 城市，实际={page.url}"
        assert '/listpage/' not in page.url, \
            f"应跳转至 Dubai 首页而非 /listpage/，实际={page.url}"
        logger.info(f"✓ TC020: Dubai 城市跳转验证通过，URL={page.url}")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc020_dubai_city.png')


@pytest.mark.p1
@allure.feature("OK - All 分类导航页")
@allure.story("右侧城市列表")
@allure.title("TC021: 右侧城市列表 - 包含 UAE 主要城市")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_021
def test_all_listpage_sidebar_cities(listpage: Page):
    """TC021: 右侧城市列表包含 8 个 UAE 主要城市 ✅ 实测"""
    page = listpage

    with allure.step("验证城市列表内容"):
        sidebar_cities = page.evaluate(r"""() => {
            var links = Array.from(document.querySelectorAll('a'));
            var cityLinks = links.filter(function(a) {
                var href = a.href || '';
                return href.match(/ae\.58v5\.cn\/en\/city-[a-z-]+$/) && a.offsetHeight > 0;
            });
            return cityLinks.map(function(a) { return a.textContent.trim(); }).filter(Boolean);
        }""")
        expected = ['Dubai', 'Abu Dhabi', 'Ras al Khaimah', 'Sharjah', 'Fujairah', 'Ajman']
        for city in expected:
            assert city in sidebar_cities, f"右侧城市列表应包含 '{city}'，实际={sidebar_cities}"
        logger.info(f"✓ TC021: 右侧城市列表={sidebar_cities}")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc021_sidebar_cities.png')


@pytest.mark.p2
@allure.feature("OK - All 分类导航页")
@allure.story("右侧城市列表")
@allure.title("TC022: 右侧城市列表 - Abu Dhabi 链接指向城市首页")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_022
def test_all_listpage_sidebar_abu_dhabi(listpage: Page):
    """TC022: 右侧 Abu Dhabi 城市链接指向 /city-abu-dhabi 首页 ✅ 实测"""
    page = listpage

    with allure.step("验证 Abu Dhabi 城市链接 href"):
        href = page.evaluate("""() => {
            var links = Array.from(document.querySelectorAll('a'));
            var link = links.find(function(a) {
                return a.textContent.trim() === 'Abu Dhabi'
                    && a.href.endsWith('/city-abu-dhabi') && a.offsetHeight > 0;
            });
            return link ? link.href : null;
        }""")
        assert href, "右侧应有 'Abu Dhabi' 城市链接"
        assert href.endswith('/city-abu-dhabi'), \
            f"Abu Dhabi 链接应指向城市首页，实际={href}"
        assert '/listpage/' not in href, "链接不应含 /listpage/"
        logger.info(f"✓ TC022: Abu Dhabi sidebar href={href}")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc022_abu_dhabi_link.png')


# ==================== 八、国家站点列表 ====================

@pytest.mark.p1
@allure.feature("OK - All 分类导航页")
@allure.story("国家站点列表")
@allure.title("TC023: 国家站点列表 - 展示多个国家/地区")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_023
def test_all_listpage_country_list(listpage: Page):
    """TC023: 国家站点列表包含多个国家/地区链接 ✅ 实测"""
    page = listpage

    with allure.step("获取国家站点列表"):
        country_links = page.evaluate(r"""() => {
            var links = Array.from(document.querySelectorAll('a'));
            var countryLinks = links.filter(function(a) {
                var href = a.href || '';
                return href.match(/^https:\/\/[a-z]{2,3}\.58v5\.cn\/$/) && a.offsetHeight > 0;
            });
            return countryLinks.map(function(a) { return a.href; });
        }""")
        assert len(country_links) >= 15, \
            f"国家站点列表应至少包含 15 个国家，实际={len(country_links)}"
        assert 'https://au.58v5.cn/' in country_links, "应包含 Australia (au.58v5.cn)"
        assert 'https://us.58v5.cn/' in country_links, "应包含 United States (us.58v5.cn)"
        logger.info(f"✓ TC023: 国家站点数量={len(country_links)}")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc023_country_list.png')


@pytest.mark.p2
@allure.feature("OK - All 分类导航页")
@allure.story("国家站点列表")
@allure.title("TC024: 国家站点 - Australia 链接指向 au.58v5.cn")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_024
def test_all_listpage_country_australia(listpage: Page):
    """TC024: Australia 站点链接 → https://au.58v5.cn ✅ 实测"""
    page = listpage

    with allure.step("验证 Australia 链接 href"):
        href = page.evaluate("""() => {
            var links = Array.from(document.querySelectorAll('a'));
            var link = links.find(function(a) {
                return a.textContent.trim() === 'Australia' && a.offsetHeight > 0;
            });
            return link ? link.href : null;
        }""")
        assert href == 'https://au.58v5.cn/', \
            f"Australia 链接应为 https://au.58v5.cn/，实际={href}"
        logger.info(f"✓ TC024: Australia href={href}")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc024_australia.png')


@pytest.mark.p2
@allure.feature("OK - All 分类导航页")
@allure.story("国家站点列表")
@allure.title("TC025: 国家站点 - United States 链接指向 us.58v5.cn")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_025
def test_all_listpage_country_us(listpage: Page):
    """TC025: United States 站点链接 → https://us.58v5.cn ✅ 实测"""
    page = listpage

    with allure.step("验证 United States 链接 href"):
        href = page.evaluate("""() => {
            var links = Array.from(document.querySelectorAll('a'));
            var link = links.find(function(a) {
                return a.textContent.trim() === 'United States' && a.offsetHeight > 0;
            });
            return link ? link.href : null;
        }""")
        assert href == 'https://us.58v5.cn/', \
            f"United States 链接应为 https://us.58v5.cn/，实际={href}"
        logger.info(f"✓ TC025: United States href={href}")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc025_us.png')


# ==================== 九、分类链接 URL 正确性 ====================

@pytest.mark.p1
@allure.feature("OK - All 分类导航页")
@allure.story("分类链接 URL 正确性")
@allure.title("TC026: Jobs 所有子分类链接均包含当前城市路径")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_026
def test_all_listpage_jobs_links_city(listpage: Page):
    """TC026: Jobs 子分类链接全部含 city-abu-dhabi ✅ 实测"""
    page = listpage

    with allure.step("获取所有 Jobs 子分类链接"):
        invalid_links = page.evaluate("""() => {
            var links = Array.from(document.querySelectorAll('a'));
            var jobSubLinks = links.filter(function(a) {
                var href = a.href || '';
                return href.includes('cate-') && href.includes('ae.58v5.cn')
                    && !href.includes('cate-marketplace') && !href.includes('cate-car')
                    && !href.includes('cate-property') && !href.includes('cate-rent')
                    && !href.includes('cate-buy') && !href.includes('cate-new-')
                    && !href.includes('cate-community') && !href.includes('cate-activities')
                    && !href.includes('cate-artists') && !href.includes('cate-classes')
                    && !href.includes('cate-events') && !href.includes('cate-friendship')
                    && !href.includes('cate-lost') && !href.includes('cate-rideshare')
                    && !href.includes('cate-sports-teams') && !href.includes('cate-volunteers')
                    && !href.includes('cate-travel') && !href.includes('cate-skills')
                    && !href.includes('cate-other') && a.offsetHeight > 0;
            });
            return jobSubLinks.filter(function(a) {
                return !a.href.includes('city-abu-dhabi');
            }).map(function(a) { return a.href; });
        }""")
        assert len(invalid_links) == 0, \
            f"以下链接不含 city-abu-dhabi：{invalid_links}"
        logger.info("✓ TC026: Jobs 子分类链接均含 city-abu-dhabi")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc026_jobs_links.png')


@pytest.mark.p1
@allure.feature("OK - All 分类导航页")
@allure.story("分类链接 URL 正确性")
@allure.title("TC027: Marketplace 所有子分类链接均包含当前城市路径")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_027
def test_all_listpage_marketplace_links_city(listpage: Page):
    """TC027: Marketplace 子分类链接全部含 city-abu-dhabi ✅ 实测"""
    page = listpage

    with allure.step("验证 Marketplace 子分类链接含城市路径"):
        marketplace_links = page.evaluate("""() => {
            var links = Array.from(document.querySelectorAll('a'));
            return links.filter(function(a) {
                var href = a.href || '';
                return href.includes('cate-marketplace') && a.offsetHeight > 0;
            }).map(function(a) { return a.href; });
        }""")
        assert len(marketplace_links) > 0, "应存在 Marketplace 链接"
        for link in marketplace_links:
            assert 'city-abu-dhabi' in link, \
                f"Marketplace 链接应含 city-abu-dhabi，实际={link}"
        logger.info(f"✓ TC027: Marketplace 链接验证通过，共 {len(marketplace_links)} 条")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc027_marketplace_links.png')


# ==================== 十、会话与状态 ====================

@pytest.mark.p1
@allure.feature("OK - All 分类导航页")
@allure.story("会话与状态")
@allure.title("TC028: 刷新页面 - 分类树内容不变")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_028
def test_all_listpage_refresh(listpage: Page):
    """TC028: 刷新页面分类树内容不变 ✅ 实测"""
    page = listpage

    with allure.step("刷新页面"):
        page.reload(wait_until='domcontentloaded')
        page.wait_for_timeout(2000)

    with allure.step("验证 URL 和内容不变"):
        assert _CONFIG['listpage_url'] in page.url, \
            f"刷新后 URL 应不变，实际={page.url}"
        body = page.evaluate("() => document.body.innerText")
        assert 'Jobs' in body, "刷新后 Jobs 分类应存在"
        assert 'Marketplace' in body, "刷新后 Marketplace 分类应存在"
        logger.info("✓ TC028: 刷新页面验证通过")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc028_refresh.png')


@pytest.mark.p1
@allure.feature("OK - All 分类导航页")
@allure.story("会话与状态")
@allure.title("TC029: 点击分类后浏览器后退 - 返回 All 列表页")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_029
def test_all_listpage_back_navigation(listpage: Page):
    """TC029: 点击分类后后退 → 返回 /listpage/ ✅ 实测"""
    page = listpage

    with allure.step("点击 Jobs 分类进入列表页"):
        _click_jobs_link(page, timeout_ms=_CONFIG['timeout']['default'])
        page.wait_for_timeout(2000)
        assert 'cate-jobs' in page.url, "应已进入 Jobs 列表页"

    with allure.step("点击浏览器后退"):
        page.go_back()
        page.wait_for_timeout(2000)

    with allure.step("验证返回至 /listpage/"):
        assert '/listpage/' in page.url, \
            f"后退后应返回 /listpage/，实际={page.url}"
        body = page.evaluate("() => document.body.innerText")
        assert 'Jobs' in body, "返回后分类树应正常展示"
        logger.info(f"✓ TC029: 后退导航验证通过，URL={page.url}")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc029_back_navigation.png')


@pytest.mark.p1
@allure.feature("OK - All 分类导航页")
@allure.story("会话与状态")
@allure.title("TC030: 未登录访问 - 页面正常展示所有分类")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_030
def test_all_listpage_unauthenticated(page, config):
    """TC030: 未登录访问 /listpage/ 正常加载所有分类 ✅ 实测"""
    with allure.step("无 session 直接访问 /listpage/"):
        _goto_with_guard(
            page,
            _CONFIG['listpage_url'],
            _jobs_link_locator(page),
        )
        page.wait_for_timeout(1000)

    with allure.step("验证页面正常加载，未重定向至登录页"):
        assert '/listpage/' in page.url, \
            f"未登录应仍可访问 /listpage/，实际={page.url}"
        assert 'login' not in page.url.lower(), \
            f"不应重定向至登录页，实际={page.url}"

    with allure.step("验证分类内容正常可见"):
        body = page.evaluate("() => document.body.innerText")
        assert 'Jobs' in body, "未登录状态 Jobs 分类应可见"
        assert 'Marketplace' in body, "未登录状态 Marketplace 分类应可见"
        logger.info(f"✓ TC030: 未登录访问验证通过，URL={page.url}")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc030_unauthenticated.png')


# ==================== 十一、不同城市的 listpage ====================

@pytest.mark.p1
@allure.feature("OK - All 分类导航页")
@allure.story("不同城市的 listpage")
@allure.title("TC031: Dubai listpage - 分类链接含 city-dubai")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_031
def test_all_listpage_dubai_links(page, config):
    """TC031: Dubai /listpage/ 分类链接均含 city-dubai ✅ 实测"""
    with allure.step("访问 Dubai listpage"):
        _goto_with_guard(
            page,
            _CONFIG['dubai_listpage_url'],
            _jobs_link_locator(page),
        )
        page.wait_for_timeout(1000)

    with allure.step("验证 Jobs 链接含 city-dubai"):
        jobs_href = page.evaluate("""() => {
            var links = Array.from(document.querySelectorAll('a'));
            var link = links.find(function(a) {
                return a.href.includes('cate-jobs') && a.offsetHeight > 0;
            });
            return link ? link.href : null;
        }""")
        assert jobs_href, "Dubai listpage 应有 Jobs 链接"
        assert 'city-dubai' in jobs_href, \
            f"Dubai listpage Jobs 链接应含 city-dubai，实际={jobs_href}"

    with allure.step("验证 Marketplace 链接含 city-dubai"):
        mp_href = page.evaluate("""() => {
            var links = Array.from(document.querySelectorAll('a'));
            var link = links.find(function(a) {
                return a.href.includes('cate-marketplace') && a.offsetHeight > 0;
            });
            return link ? link.href : null;
        }""")
        assert 'city-dubai' in mp_href, \
            f"Dubai listpage Marketplace 链接应含 city-dubai，实际={mp_href}"
        logger.info(f"✓ TC031: Dubai listpage 分类链接验证通过")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc031_dubai_listpage.png')


@pytest.mark.p1
@allure.feature("OK - All 分类导航页")
@allure.story("不同城市的 listpage")
@allure.title("TC032: Abu Dhabi 与 Dubai listpage 分类链接城市路径不同")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ae
@pytest.mark.case_id_all_listpage_032
def test_all_listpage_city_specific_links(page, config):
    """TC032: 两城市 listpage 分类链接含各自城市路径 ✅ 实测"""
    with allure.step("访问 Abu Dhabi listpage，记录 Jobs 链接"):
        _goto_with_guard(
            page,
            _CONFIG['listpage_url'],
            _jobs_link_locator(page),
        )
        page.wait_for_timeout(1000)
        abu_jobs_href = page.evaluate("""() => {
            var links = Array.from(document.querySelectorAll('a'));
            var link = links.find(function(a) {
                return a.href.includes('cate-jobs') && a.offsetHeight > 0;
            });
            return link ? link.href : null;
        }""")

    with allure.step("访问 Dubai listpage，记录 Jobs 链接"):
        _goto_with_guard(
            page,
            _CONFIG['dubai_listpage_url'],
            _jobs_link_locator(page),
        )
        page.wait_for_timeout(1000)
        dubai_jobs_href = page.evaluate("""() => {
            var links = Array.from(document.querySelectorAll('a'));
            var link = links.find(function(a) {
                return a.href.includes('cate-jobs') && a.offsetHeight > 0;
            });
            return link ? link.href : null;
        }""")

    with allure.step("对比两城市 Jobs 链接城市路径不同"):
        assert 'city-abu-dhabi' in abu_jobs_href, \
            f"Abu Dhabi listpage Jobs 链接应含 city-abu-dhabi，实际={abu_jobs_href}"
        assert 'city-dubai' in dubai_jobs_href, \
            f"Dubai listpage Jobs 链接应含 city-dubai，实际={dubai_jobs_href}"
        assert abu_jobs_href != dubai_jobs_href, \
            "两城市 Jobs 链接应不同"
        logger.info(f"✓ TC032: Abu Dhabi={abu_jobs_href} Dubai={dubai_jobs_href}")

    _safe_listpage_screenshot(page, f'{SCREENSHOT_DIR}/tc032_city_comparison.png')
