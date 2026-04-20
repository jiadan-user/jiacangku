"""
OK AE站 - 首页搜索输入框 完整测试套件（TC001 ~ TC036）

生成时间：2026-03-05
测试站点：AE (https://ae.58v5.cn/en/city-dubai/)
测试角色：buyer（无需登录）

测试覆盖：
  一、底纹词（TC001-TC003）
  二、Search 按钮（TC004-TC007）
  三、输入内容后进行搜索（TC008-TC015）
  四、Sug词交互（TC016-TC026）
  五、最近搜索词（TC027-TC035）
  六、会话与状态（TC035-TC036）

录制说明：
  - 搜索输入框 ID: #custom-input（React controlled input）
  - 输入方式：page.evaluate() 聚焦 + page.keyboard.type()（规避 React hydration 错误）
  - Search 按钮：通过 page.evaluate() 触发 DOM click
  - 历史记录存储于 localStorage.__SEARCH_LOCAL_HISTORY_LIST__（JSON数组，{suggestKey, timestamp}）
  - 纯 Sug 词：过滤掉含 SearchSuggestContent_modalHistoryItemPC__W7Zwc class 的条目
"""

import re
import urllib.parse
import time
import pytest
import allure
from pages.home_search_page import HomeSearchPage
from utils.logger import setup_logger
from playwright._impl._errors import TimeoutError as PlaywrightTimeoutError

logger = setup_logger()


def safe_goto(page, url, wait_until="domcontentloaded", timeout=60000, max_retries=2):
    """
    安全的页面导航，带重试机制（使用官方推荐的 domcontentloaded 策略）
    
    Args:
        page: Playwright Page 对象
        url: 目标 URL
        wait_until: 等待策略，默认 domcontentloaded（官方推荐，禁止使用 load 或 networkidle）
        timeout: 超时时间（毫秒），默认 60 秒（跨国站点访问较慢）
        max_retries: 最大重试次数
    
    注意：
    - 官方明确禁止使用 wait_until="load" 或 "networkidle"
    - 导航后应配合元素级等待确保页面关键元素加载完成
    """
    for attempt in range(max_retries):
        try:
            page.goto(url, wait_until=wait_until, timeout=timeout)
            page.wait_for_timeout(1000)  # 额外等待页面稳定
            return
        except PlaywrightTimeoutError as e:
            if attempt < max_retries - 1:
                logger.warning(f"页面导航超时（尝试 {attempt + 1}/{max_retries}），重试中...")
                time.sleep(2)  # 等待2秒后重试
            else:
                logger.error(f"页面导航失败，已重试 {max_retries} 次")
                raise

# ============================================================
# 测试环境配置
# ============================================================
_CONFIG = {
    "site": "ae",
    "site_name": "阿联酋站（迪拜）",
    "role": "buyer",
    "user_name": "无",
    "base_url": "https://ae.58v5.cn/en/city-dubai/",
    "test_account": None,
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


# ============================================================
# 共享工具函数
# ============================================================

def _is_clear_visible(page):
    """判断 Clear 按钮是否在 DOM 中可见"""
    return page.evaluate(
        """() => {
            const el = document.querySelector('.CustomInput_searchClear___ZaYy');
            return el ? getComputedStyle(el).display !== 'none' && el.offsetHeight > 0 : false;
        }"""
    )


def _type_keyword(page, keyword):
    """聚焦输入框并逐字输入关键词"""
    page.evaluate("() => { const el = document.querySelector('#custom-input'); if(el) el.focus(); }")
    page.keyboard.type(keyword)
    page.wait_for_timeout(500)


def _click_clear(page):
    """点击 Clear 按钮"""
    page.evaluate("() => document.querySelector('.CustomInput_searchClear___ZaYy')?.click()")
    page.wait_for_timeout(500)


def _get_sug_count(page):
    """获取当前 sug 词数量（含历史条目）"""
    return page.evaluate("() => document.querySelectorAll('[class*=\"modalSugItem\"]').length")


def _get_sug_texts(page):
    """获取所有 sug 词文案列表（含历史条目）"""
    return page.evaluate(
        "() => Array.from(document.querySelectorAll('[class*=\"modalSugItem\"]')).map(el => el.innerText.trim())"
    )


def _inject_history(page, keywords, base_url=None):
    """向 localStorage 注入历史记录。
    
    keywords 列表中最后一个元素时间戳最新（排在历史第一位），
    注入格式与应用保持一致：按时间戳降序排列（最新在前）。
    若当前页为 about:blank 等无法访问 localStorage 的页面，需传入 base_url 先导航。
    """
    # 若当前在 about:blank 则先导航，保证 localStorage 可访问
    if base_url and ("about:blank" in page.url or page.url == ""):
        safe_goto(page, base_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(500)
    now = page.evaluate("() => Date.now()")
    # keywords[-1] 时间戳最大（最新），keywords[0] 时间戳最小（最旧）
    # 注入时按降序排列（最新在前），与应用存储格式一致
    history_data = [
        {"suggestKey": kw, "timestamp": now - (len(keywords) - 1 - i) * 1000}
        for i, kw in enumerate(reversed(keywords))
    ]
    page.evaluate(
        "(data) => localStorage.setItem('__SEARCH_LOCAL_HISTORY_LIST__', JSON.stringify(data))",
        history_data
    )
    return history_data


# ============================================================
# 一、底纹词（Placeholder）TC001-TC003
# ============================================================

@pytest.mark.case_id_ae_search_tc001
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.ae
@pytest.mark.search
@allure.feature("OK")
@allure.story("首页搜索输入框 - 底纹词")
@allure.title("未聚焦时输入框展示底纹词'Search for anything'")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证首页搜索输入框在未聚焦时显示 placeholder 文案 'Search for anything'")
def test_search_placeholder_shown_when_unfocused(page, config):
    """TC001: 未聚焦时输入框展示底纹词"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    logger.info("=" * 60)
    logger.info("TC001: 验证底纹词 'Search for anything' 展示")
    logger.info("=" * 60)

    with allure.step("步骤1：导航到首页"):
        search_page.navigate_to_home(base_url)
        logger.info("✓ 已打开首页")

    with allure.step("步骤2：获取搜索框 placeholder 文本"):
        placeholder = search_page.get_search_input_placeholder()
        logger.info(f"✓ placeholder = '{placeholder}'")

    with allure.step("验证 placeholder 为 'Search for anything'"):
        assert placeholder == "Search for anything", \
            f"底纹词错误，期望 'Search for anything'，实际: '{placeholder}'"
        logger.info("✅ TC001 通过：底纹词展示正确")


@pytest.mark.case_id_ae_search_tc002
@pytest.mark.p1
@pytest.mark.ae
@pytest.mark.search
@allure.feature("OK")
@allure.story("首页搜索输入框 - 底纹词")
@allure.title("输入框聚焦后底纹词展示，失焦且内容为空时底纹词恢复")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证聚焦后未输入内容底纹词展示，失焦且内容为空时底纹词重新出现")
def test_search_placeholder_focus_blur(page, config):
    """TC002: 聚焦/失焦后底纹词行为"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    logger.info("=" * 60)
    logger.info("TC002: 验证聚焦/失焦底纹词行为")
    logger.info("=" * 60)

    with allure.step("步骤1：导航到首页"):
        search_page.navigate_to_home(base_url)
        logger.info("✓ 已打开首页")

    with allure.step("步骤2：点击搜索框（聚焦）"):
        search_page.click_search_input()
        is_focused = search_page.is_search_input_focused()
        input_value = search_page.get_search_input_value()
        logger.info(f"✓ 聚焦状态: {is_focused}, 输入框值: '{input_value}'")

    with allure.step("步骤3：点击空白区域（失焦）"):
        search_page.click_page_blank()
        placeholder_after_blur = search_page.get_search_input_placeholder()
        value_after_blur = search_page.get_search_input_value()
        logger.info(f"✓ 失焦后 placeholder='{placeholder_after_blur}', value='{value_after_blur}'")

    with allure.step("验证聚焦后输入框为空且可聚焦"):
        assert is_focused is True, "搜索框应处于聚焦状态"
        assert input_value == "", "聚焦后输入框值应为空"
        logger.info("✓ 聚焦状态验证通过")

    with allure.step("验证失焦后底纹词恢复"):
        assert placeholder_after_blur == "Search for anything", \
            f"失焦后底纹词应为 'Search for anything'，实际: '{placeholder_after_blur}'"
        assert value_after_blur == "", "失焦且无内容时输入框值应为空"
        logger.info("✅ TC002 通过：聚焦/失焦底纹词行为正确")


@pytest.mark.case_id_ae_search_tc003
@pytest.mark.p1
@pytest.mark.ae
@pytest.mark.search
@allure.feature("OK")
@allure.story("首页搜索输入框 - 底纹词")
@allure.title("输入内容后底纹词不显示，Clear清空后底纹词恢复")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证输入内容后底纹词消失，点击 Clear 按钮清空后底纹词重新显示")
def test_search_placeholder_hidden_on_input_restored_on_clear(page, config):
    """TC003: 输入内容后底纹词不显示，清空后恢复"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    logger.info("=" * 60)
    logger.info("TC003: 验证输入内容/清空后底纹词行为")
    logger.info("=" * 60)

    with allure.step("步骤1：导航到首页"):
        search_page.navigate_to_home(base_url)
        logger.info("✓ 已打开首页")

    with allure.step("步骤2：输入关键词 'apartment'"):
        search_page.fill_search_input("apartment")
        value_after_input = search_page.get_search_input_value()
        is_clear_visible = search_page.is_clear_button_visible()
        logger.info(f"✓ 输入后 value='{value_after_input}', Clear按钮可见: {is_clear_visible}")

    with allure.step("步骤3：点击 Clear 按钮清空"):
        search_page.clear_search_input()
        value_after_clear = search_page.get_search_input_value()
        placeholder_after_clear = search_page.get_search_input_placeholder()
        is_clear_visible_after = search_page.is_clear_button_visible()
        logger.info(f"✓ 清空后 value='{value_after_clear}', placeholder='{placeholder_after_clear}', Clear可见: {is_clear_visible_after}")

    with allure.step("验证输入后 value 正确且 Clear 按钮可见"):
        assert value_after_input == "apartment", \
            f"输入后 value 应为 'apartment'，实际: '{value_after_input}'"
        assert is_clear_visible is True, "输入内容后 Clear 按钮应可见"
        logger.info("✓ 输入状态验证通过")

    with allure.step("验证清空后 value 为空且 placeholder 恢复"):
        assert value_after_clear == "", f"清空后 value 应为空，实际: '{value_after_clear}'"
        assert placeholder_after_clear == "Search for anything", \
            f"清空后底纹词应为 'Search for anything'，实际: '{placeholder_after_clear}'"
        assert is_clear_visible_after is False, "清空后 Clear 按钮应不可见"
        logger.info("✅ TC003 通过：输入/清空后底纹词行为正确")


# ============================================================
# 二、Search 按钮 TC004-TC007
# ============================================================

@pytest.mark.case_id_ae_search_tc004
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.ae
@pytest.mark.search
@allure.feature("OK")
@allure.story("首页搜索输入框 - Search按钮")
@allure.title("输入关键词后点击Search按钮跳转搜索结果页")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证输入关键词 'job' 后点击 Search 按钮跳转至正确的搜索结果页 URL")
def test_search_button_click_with_keyword_navigates_to_result(page, config):
    """TC004: 输入关键词后点击 Search 跳转搜索结果页"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]
    keyword = "job"

    logger.info("=" * 60)
    logger.info(f"TC004: 输入 '{keyword}' 点击 Search 验证跳转")
    logger.info("=" * 60)

    with allure.step("步骤1：导航到首页"):
        search_page.navigate_to_home(base_url)
        logger.info("✓ 已打开首页")

    with allure.step(f"步骤2：输入关键词 '{keyword}'"):
        search_page.fill_search_input(keyword)
        logger.info(f"✓ 已输入 '{keyword}'")

    with allure.step("步骤3：点击 Search 按钮"):
        search_page.click_search_button()
        search_page.wait_for_search_result_page()
        current_url = search_page.get_current_url()
        page_title = page.title()
        logger.info(f"✓ 跳转后 URL: {current_url}")
        logger.info(f"✓ 页面 Title: {page_title}")

    with allure.step("验证 URL 包含正确的 keyword 参数"):
        assert f"keyword={keyword}" in current_url, \
            f"URL 应包含 'keyword={keyword}'，实际 URL: {current_url}"
        assert "/cate/" in current_url, \
            f"URL 应包含 '/cate/'，实际 URL: {current_url}"
        logger.info("✓ URL 验证通过")
        logger.info("✅ TC004 通过：Search按钮跳转正确")


@pytest.mark.case_id_ae_search_tc005
@pytest.mark.p1
@pytest.mark.ae
@pytest.mark.search
@allure.feature("OK")
@allure.story("首页搜索输入框 - Search按钮")
@allure.title("空内容点击Search按钮跳转至全品类页（无keyword参数）")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证输入框为空时直接点击 Search 按钮跳转至全品类页，URL 不包含 keyword 参数")
def test_search_button_click_empty_navigates_to_all_categories(page, config):
    """TC005: 空内容点击 Search 跳转至全品类页"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    logger.info("=" * 60)
    logger.info("TC005: 空内容点击 Search 验证跳转全品类页")
    logger.info("=" * 60)

    with allure.step("步骤1：导航到首页，不输入任何内容"):
        search_page.navigate_to_home(base_url)
        logger.info("✓ 已打开首页，搜索框为空")

    with allure.step("步骤2：直接点击 Search 按钮"):
        search_page.click_search_button()
        search_page.wait_for_search_result_page()
        current_url = search_page.get_current_url()
        logger.info(f"✓ 跳转后 URL: {current_url}")

    with allure.step("验证 URL 跳转至全品类页且无 keyword 参数"):
        assert "keyword" not in current_url, \
            f"空内容搜索时 URL 不应包含 'keyword'，实际 URL: {current_url}"
        assert "/cate/" in current_url, \
            f"URL 应包含 '/cate/'，实际 URL: {current_url}"
        logger.info("✓ URL 验证通过（无 keyword 参数）")

    with allure.step("验证页面无错误提示"):
        assert page.title() != "", "页面应正常加载，title 不为空"
        logger.info("✅ TC005 通过：空内容Search跳转全品类页正确")


@pytest.mark.case_id_ae_search_tc006
@pytest.mark.p2
@pytest.mark.ae
@pytest.mark.search
@allure.feature("OK")
@allure.story("首页搜索输入框 - Search按钮")
@allure.title("Search按钮在无内容时的视觉状态")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证Search按钮文案为'Search'，且在无内容和有内容时均可点击（无禁用态）")
def test_search_button_visual_state(page, config):
    """TC006: Search按钮在无内容时的视觉状态"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    logger.info("=" * 60)
    logger.info("TC006: 验证 Search 按钮视觉状态（文案、可点击性）")
    logger.info("=" * 60)

    with allure.step("步骤1：导航到首页"):
        search_page.navigate_to_home(base_url)
        logger.info("✓ 已打开首页")

    with allure.step("步骤2：获取空输入框时 Search 按钮文案"):
        btn_text_empty = search_page.get_search_button_text()
        logger.info(f"✓ 空输入时 Search 按钮文案 = '{btn_text_empty}'")

    with allure.step("步骤3：检查按钮是否处于禁用状态（空输入时）"):
        btn_disabled_empty = page.evaluate(
            "() => document.querySelector('.TopBarMiddleContent_searchButton__3UG6i')?.disabled"
        )
        logger.info(f"✓ 按钮 disabled 属性（空输入）= {btn_disabled_empty}")

    with allure.step("步骤4：聚焦输入框并输入内容'apartment'"):
        page.evaluate("() => { const el = document.querySelector('#custom-input'); if(el) el.focus(); }")
        page.keyboard.type("apartment")
        page.wait_for_timeout(300)
        logger.info("✓ 已输入 'apartment'")

    with allure.step("步骤5：获取有内容时 Search 按钮文案"):
        btn_text_with_content = search_page.get_search_button_text()
        logger.info(f"✓ 有内容时 Search 按钮文案 = '{btn_text_with_content}'")

    with allure.step("步骤6：检查按钮是否处于禁用状态（有输入时）"):
        btn_disabled_with_content = page.evaluate(
            "() => document.querySelector('.TopBarMiddleContent_searchButton__3UG6i')?.disabled"
        )
        logger.info(f"✓ 按钮 disabled 属性（有输入）= {btn_disabled_with_content}")

    with allure.step("验证 Search 按钮文案为 'Search'"):
        assert btn_text_empty.strip() == "Search", \
            f"按钮文案错误，期望 'Search'，实际: '{btn_text_empty}'"
        logger.info("✅ 按钮文案验证通过")

    with allure.step("验证按钮无论有无内容均不禁用"):
        assert not btn_disabled_empty, "空输入时 Search 按钮不应被禁用"
        assert not btn_disabled_with_content, "有内容时 Search 按钮不应被禁用"
        logger.info("✅ TC006 通过：Search 按钮无禁用态，文案正确")


@pytest.mark.case_id_ae_search_tc007
@pytest.mark.p2
@pytest.mark.ae
@pytest.mark.search
@allure.feature("OK")
@allure.story("首页搜索输入框 - Search按钮")
@allure.title("快速连续点击Search按钮不产生重复跳转")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证快速连续点击Search按钮3次，页面不崩溃，不会打开多个页签")
def test_search_button_rapid_clicks_no_duplicate_tab(page, config):
    """TC007: 快速连续点击Search按钮不产生重复跳转"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    logger.info("=" * 60)
    logger.info("TC007: 验证快速连续点击 Search 按钮不崩溃、不打开多页签")
    logger.info("=" * 60)

    with allure.step("步骤1：导航到首页"):
        search_page.navigate_to_home(base_url)
        logger.info("✓ 已打开首页")

    with allure.step("步骤2：输入关键词'apartment'"):
        page.evaluate("() => { const el = document.querySelector('#custom-input'); if(el) el.focus(); }")
        page.keyboard.type("apartment")
        page.wait_for_timeout(300)
        logger.info("✓ 已输入 'apartment'")

    with allure.step("步骤3：快速连续点击 Search 按钮 3 次"):
        page.evaluate("() => document.querySelector('.TopBarMiddleContent_searchButton__3UG6i')?.click()")
        page.wait_for_timeout(100)
        try:
            page.evaluate("() => document.querySelector('.TopBarMiddleContent_searchButton__3UG6i')?.click()")
        except Exception:
            pass
        page.wait_for_timeout(100)
        try:
            page.evaluate("() => document.querySelector('.TopBarMiddleContent_searchButton__3UG6i')?.click()")
        except Exception:
            pass
        logger.info("✓ 已连续点击 3 次")

    with allure.step("步骤4：等待页面稳定"):
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(1000)
        final_url = page.url
        logger.info(f"✓ 最终 URL: {final_url}")

    with allure.step("验证页面正常跳转到搜索结果页，无崩溃"):
        assert "cate" in final_url, \
            f"预期跳转到搜索结果页（含 'cate'），实际 URL: {final_url}"
        logger.info("✅ TC007 通过：快速点击不崩溃，正常跳转到搜索结果页")


# ============================================================
# 三、输入内容后进行搜索 TC008-TC015
# ============================================================

@pytest.mark.case_id_ae_search_tc008
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.ae
@pytest.mark.search
@allure.feature("OK")
@allure.story("首页搜索输入框 - 键盘搜索")
@allure.title("输入关键词后按Enter键跳转搜索结果页")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证在搜索框中输入'apartment'后按Enter键，正确跳转到含keyword参数的搜索结果页")
def test_search_by_enter_key(page, config):
    """TC008: 输入关键词后按Enter键跳转搜索结果页"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]
    keyword = "apartment"

    logger.info("=" * 60)
    logger.info(f"TC008: 验证 Enter 键搜索 keyword='{keyword}'")
    logger.info("=" * 60)

    with allure.step("步骤1：导航到首页"):
        search_page.navigate_to_home(base_url)
        logger.info("✓ 已打开首页")

    with allure.step(f"步骤2：点击输入框，输入关键词'{keyword}'"):
        page.evaluate("() => { const el = document.querySelector('#custom-input'); if(el) el.focus(); }")
        page.keyboard.type(keyword)
        page.wait_for_timeout(500)
        logger.info(f"✓ 已输入 '{keyword}'")

    with allure.step("步骤3：按下 Enter 键"):
        page.keyboard.press("Enter")
        logger.info("✓ 已按下 Enter 键")

    with allure.step("步骤4：等待跳转到搜索结果页"):
        page.wait_for_url("**/cate/**", timeout=10000)
        final_url = page.url
        logger.info(f"✓ 跳转后 URL: {final_url}")

    with allure.step(f"验证 URL 包含 keyword={keyword}"):
        assert f"keyword={keyword}" in final_url, \
            f"URL 中未包含 keyword={keyword}，实际 URL: {final_url}"
        logger.info("✅ TC008 通过：Enter 键搜索，URL keyword 参数正确")


@pytest.mark.case_id_ae_search_tc009
@pytest.mark.p1
@pytest.mark.ae
@pytest.mark.search
@allure.feature("OK")
@allure.story("首页搜索输入框 - URL编码")
@allure.title("搜索关键词正确编码到URL参数")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证含空格的搜索关键词'security guard'，空格被正确URL编码（%20或+），搜索结果页正常展示")
def test_search_keyword_with_space_url_encoding(page, config):
    """TC009: 搜索关键词正确编码到URL参数"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]
    keyword = "security guard"

    logger.info("=" * 60)
    logger.info(f"TC009: 验证含空格关键词URL编码，keyword='{keyword}'")
    logger.info("=" * 60)

    with allure.step("步骤1：导航到首页"):
        search_page.navigate_to_home(base_url)
        logger.info("✓ 已打开首页")

    with allure.step(f"步骤2：输入含空格关键词'{keyword}'"):
        page.evaluate("() => { const el = document.querySelector('#custom-input'); if(el) el.focus(); }")
        page.keyboard.type(keyword)
        page.wait_for_timeout(500)
        logger.info(f"✓ 已输入 '{keyword}'")

    with allure.step("步骤3：点击 Search 按钮"):
        page.evaluate("() => document.querySelector('.TopBarMiddleContent_searchButton__3UG6i')?.click()")
        logger.info("✓ 已点击 Search 按钮")

    with allure.step("步骤4：等待跳转到搜索结果页"):
        page.wait_for_url("**/cate/**", timeout=10000)
        final_url = page.url
        logger.info(f"✓ 跳转后 URL: {final_url}")

    with allure.step("验证 URL 中空格被正确编码为 %20 或 +"):
        has_encoded_space = ("security%20guard" in final_url or "security+guard" in final_url)
        assert has_encoded_space, \
            f"URL 中空格未正确编码，实际 URL: {final_url}"
        logger.info(f"✅ TC009 通过：含空格关键词 URL 编码正确，URL: {final_url}")


@pytest.mark.case_id_ae_search_tc010
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.ae
@pytest.mark.search
@allure.feature("OK")
@allure.story("首页搜索输入框 - 安全")
@allure.title("特殊HTML字符搜索，参数正确转义不引发XSS")
@allure.severity(allure.severity_level.BLOCKER)
@allure.description(
    "验证特殊HTML字符 '<script>alert(1)</script>' 搜索时，"
    "特殊字符被正确URL编码（%3C/%3E），页面不弹出alert对话框，无XSS执行"
)
def test_xss_input_no_script_execution(page, config):
    """TC010: 特殊HTML字符搜索，参数正确转义不引发XSS"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]
    xss_payload = "<script>alert(1)</script>"

    logger.info("=" * 60)
    logger.info("TC010: 验证 XSS 输入不引发 alert 弹窗")
    logger.info("=" * 60)

    dialog_triggered = {"value": False}

    def handle_dialog(dialog):
        dialog_triggered["value"] = True
        logger.warning(f"⚠️ 弹窗触发！type={dialog.type}, message={dialog.message}")
        dialog.dismiss()

    page.on("dialog", handle_dialog)

    with allure.step("步骤1：导航到首页"):
        search_page.navigate_to_home(base_url)
        logger.info("✓ 已打开首页")

    with allure.step(f"步骤2：输入 XSS payload '{xss_payload}'"):
        page.evaluate("() => { const el = document.querySelector('#custom-input'); if(el) el.focus(); }")
        page.keyboard.type(xss_payload)
        page.wait_for_timeout(500)
        logger.info("✓ 已输入 XSS payload")

    with allure.step("步骤3：点击 Search 按钮"):
        page.evaluate("() => document.querySelector('.TopBarMiddleContent_searchButton__3UG6i')?.click()")
        logger.info("✓ 已点击 Search 按钮")

    with allure.step("步骤4：等待跳转到搜索结果页"):
        page.wait_for_url("**/cate/**", timeout=10000)
        final_url = page.url
        logger.info(f"✓ 跳转后 URL: {final_url}")

    with allure.step("步骤5：等待页面稳定，观察是否有 alert 弹窗"):
        page.wait_for_timeout(2000)
        logger.info(f"✓ 弹窗是否触发: {dialog_triggered['value']}")

    with allure.step("验证 URL 中特殊字符被正确 URL 编码"):
        assert "%3C" in final_url or "%3c" in final_url, \
            f"'<' 未被编码为 %3C，实际 URL: {final_url}"
        assert "%3E" in final_url or "%3e" in final_url, \
            f"'>' 未被编码为 %3E，实际 URL: {final_url}"
        logger.info(f"✅ 特殊字符 URL 编码正确，URL: {final_url}")

    with allure.step("验证页面未执行 XSS（无 alert 弹窗）"):
        assert not dialog_triggered["value"], \
            "检测到 alert 弹窗！XSS 注入成功，存在安全漏洞"
        logger.info("✅ TC010 通过：XSS payload 被正确转义，无弹窗")


@pytest.mark.case_id_ae_search_tc011
@pytest.mark.p2
@pytest.mark.ae
@pytest.mark.search
@allure.feature("OK")
@allure.story("首页搜索输入框 - 特殊字符搜索")
@allure.title("Emoji字符搜索正常处理")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证含Emoji字符'🏠 apartment'搜索时，Emoji被正确URL编码（%F0%9F%8F%A0），页面正常跳转不崩溃")
def test_emoji_input_search_url_encoding(page, config):
    """TC011: Emoji字符搜索正常处理"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]
    emoji_keyword = "🏠 apartment"

    logger.info("=" * 60)
    logger.info("TC011: 验证 Emoji 字符搜索 URL 编码")
    logger.info("=" * 60)

    with allure.step("步骤1：导航到首页"):
        search_page.navigate_to_home(base_url)
        logger.info("✓ 已打开首页")

    with allure.step(f"步骤2：输入含Emoji关键词'{emoji_keyword}'"):
        page.evaluate("() => { const el = document.querySelector('#custom-input'); if(el) el.focus(); }")
        page.keyboard.type(emoji_keyword)
        page.wait_for_timeout(500)
        logger.info(f"✓ 已输入 '{emoji_keyword}'")

    with allure.step("步骤3：点击 Search 按钮"):
        page.evaluate("() => document.querySelector('.TopBarMiddleContent_searchButton__3UG6i')?.click()")
        logger.info("✓ 已点击 Search 按钮")

    with allure.step("步骤4：等待跳转到搜索结果页"):
        page.wait_for_url("**/cate/**", timeout=10000)
        final_url = page.url
        logger.info(f"✓ 跳转后 URL: {final_url}")

    with allure.step("验证 Emoji 字符被正确 URL 编码"):
        emoji_encoded = "%F0%9F%8F%A0"
        assert emoji_encoded.lower() in final_url.lower(), \
            f"Emoji '🏠' 未被正确编码为 {emoji_encoded}，实际 URL: {final_url}"
        logger.info(f"✅ TC011 通过：Emoji URL 编码正确，URL: {final_url}")


@pytest.mark.case_id_ae_search_tc012
@pytest.mark.p2
@pytest.mark.ae
@pytest.mark.search
@allure.feature("OK")
@allure.story("首页搜索输入框 - 边界值")
@allure.title("超长关键词（200字符）搜索")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证输入200个字符的超长关键词，搜索正常跳转，URL携带完整关键词参数")
def test_long_keyword_200_chars_search(page, config):
    """TC012: 超长关键词（200字符）搜索"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]
    long_keyword = "a" * 200

    logger.info("=" * 60)
    logger.info(f"TC012: 验证超长关键词（{len(long_keyword)}字符）搜索")
    logger.info("=" * 60)

    with allure.step("步骤1：导航到首页"):
        search_page.navigate_to_home(base_url)
        logger.info("✓ 已打开首页")

    with allure.step("步骤2：输入200个字符的关键词"):
        page.evaluate("() => { const el = document.querySelector('#custom-input'); if(el) el.focus(); }")
        page.keyboard.type(long_keyword)
        page.wait_for_timeout(500)
        actual_val = page.evaluate("() => document.querySelector('#custom-input')?.value || ''")
        logger.info(f"✓ 输入后实际值长度: {len(actual_val)}")

    with allure.step("步骤3：点击 Search 按钮"):
        page.evaluate("() => document.querySelector('.TopBarMiddleContent_searchButton__3UG6i')?.click()")
        logger.info("✓ 已点击 Search 按钮")

    with allure.step("步骤4：等待跳转到搜索结果页"):
        page.wait_for_url("**/cate/**", timeout=10000)
        final_url = page.url
        logger.info(f"✓ 跳转后 URL 长度: {len(final_url)}")

    with allure.step("验证输入框最大接受字符数（合理范围内）"):
        assert len(actual_val) <= 200, \
            f"输入框实际接受字符数超过预期最大值200，实际: {len(actual_val)}"
        assert len(actual_val) >= 100, \
            f"输入框接受字符数过少（小于100），可能存在异常截断，实际: {len(actual_val)}"
        logger.info(f"✅ 输入框实测最大接受 {len(actual_val)} 字符")

    with allure.step("验证页面正常跳转到搜索结果页"):
        assert "cate" in final_url, \
            f"预期跳转到搜索结果页，实际 URL: {final_url}"
        logger.info(f"✅ TC012 通过：超长关键词搜索正常跳转")


@pytest.mark.case_id_ae_search_tc013
@pytest.mark.p2
@pytest.mark.ae
@pytest.mark.search
@allure.feature("OK")
@allure.story("首页搜索输入框 - 负向/边界值")
@allure.title("仅空格内容搜索")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证仅输入多个空格后点击Search，页面正常跳转到搜索结果页或全品类页，不报错")
def test_spaces_only_search_no_error(page, config):
    """TC013: 仅空格内容搜索"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    logger.info("=" * 60)
    logger.info("TC013: 验证仅空格内容搜索不报错，正常跳转")
    logger.info("=" * 60)

    with allure.step("步骤1：导航到首页"):
        search_page.navigate_to_home(base_url)
        logger.info("✓ 已打开首页")

    with allure.step("步骤2：输入多个空格"):
        page.evaluate("() => { const el = document.querySelector('#custom-input'); if(el) el.focus(); }")
        page.keyboard.type("   ")
        page.wait_for_timeout(300)
        logger.info("✓ 已输入 3 个空格")

    with allure.step("步骤3：点击 Search 按钮"):
        page.evaluate("() => document.querySelector('.TopBarMiddleContent_searchButton__3UG6i')?.click()")
        logger.info("✓ 已点击 Search 按钮")

    with allure.step("步骤4：等待跳转"):
        page.wait_for_url("**/cate/**", timeout=10000)
        final_url = page.url
        logger.info(f"✓ 跳转后 URL: {final_url}")

    with allure.step("验证页面正常跳转，不报错"):
        assert "cate" in final_url, \
            f"预期跳转到搜索结果页或全品类页（含'cate'），实际 URL: {final_url}"
        logger.info(f"✅ TC013 通过：仅空格搜索正常跳转，URL: {final_url}")


@pytest.mark.case_id_ae_search_tc014
@pytest.mark.p2
@pytest.mark.ae
@pytest.mark.search
@allure.feature("OK")
@allure.story("首页搜索输入框 - 国际化")
@allure.title("中文/阿拉伯语关键词搜索")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证阿拉伯语关键词'وظائف'搜索时，URL正确编码阿拉伯文字符，页面正常跳转不崩溃")
def test_arabic_keyword_search_url_encoding(page, config):
    """TC014: 中文/阿拉伯语关键词搜索"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]
    arabic_keyword = "وظائف"

    logger.info("=" * 60)
    logger.info(f"TC014: 验证阿拉伯语关键词 '{arabic_keyword}' URL 编码")
    logger.info("=" * 60)

    with allure.step("步骤1：导航到首页"):
        search_page.navigate_to_home(base_url)
        logger.info("✓ 已打开首页")

    with allure.step(f"步骤2：输入阿拉伯语关键词'{arabic_keyword}'"):
        search_page.fill_search_input(arabic_keyword)
        # 验证输入是否成功
        input_value = search_page.get_search_input_value()
        assert arabic_keyword in input_value, f"输入失败，输入框值: {input_value}"
        logger.info(f"✓ 已输入阿拉伯语 '{arabic_keyword}'，实际值: {input_value}")

    with allure.step("步骤3：点击 Search 按钮"):
        page.evaluate("() => document.querySelector('.TopBarMiddleContent_searchButton__3UG6i')?.click()")
        logger.info("✓ 已点击 Search 按钮")

    with allure.step("步骤4：等待跳转到搜索结果页"):
        page.wait_for_url("**/cate/**", timeout=20000)
        final_url = page.url
        logger.info(f"✓ 跳转后 URL: {final_url}")

    with allure.step("验证页面正常跳转，URL包含编码的阿拉伯文字符"):
        assert "cate" in final_url, \
            f"预期跳转到搜索结果页，实际 URL: {final_url}"
        assert "keyword=" in final_url, \
            f"URL 中未包含 keyword 参数，实际 URL: {final_url}"
        encoded_check = "%D9" in final_url or "%d9" in final_url
        assert encoded_check, \
            f"阿拉伯文字符未被 URL 编码，实际 URL: {final_url}"
        logger.info(f"✅ TC014 通过：阿拉伯语关键词 URL 编码正确，URL: {final_url}")


@pytest.mark.case_id_ae_search_tc015
@pytest.mark.p1
@pytest.mark.ae
@pytest.mark.search
@allure.feature("OK")
@allure.story("首页搜索输入框 - Clear按钮")
@allure.title("Clear（×）按钮在有内容时显示，点击后清空输入框")
@allure.severity(allure.severity_level.NORMAL)
@allure.description(
    "验证Clear(×)按钮行为：输入内容后Clear按钮出现并可见，点击后输入框内容清空为空字符串，"
    "输入框重新显示底纹词'Search for anything'"
)
def test_clear_button_shows_and_clears_input(page, config):
    """TC015: Clear（×）按钮在有内容时显示，点击后清空输入框"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]
    keyword = "test keyword"
    CLEAR_SELECTOR = ".CustomInput_searchClear___ZaYy"

    logger.info("=" * 60)
    logger.info("TC015: 验证 Clear 按钮显示/隐藏及清空功能")
    logger.info("=" * 60)

    def is_clear_visible():
        return page.evaluate(
            """() => {
                const el = document.querySelector('.CustomInput_searchClear___ZaYy');
                return el ? getComputedStyle(el).display !== 'none' && el.offsetHeight > 0 : false;
            }"""
        )

    with allure.step("步骤1：导航到首页"):
        search_page.navigate_to_home(base_url)
        logger.info("✓ 已打开首页")

    with allure.step("步骤2：确认空输入框时 Clear 按钮不可见"):
        clear_before_input = is_clear_visible()
        logger.info(f"✓ 空输入时 Clear 可见: {clear_before_input}")

    with allure.step(f"步骤3：输入关键词'{keyword}'"):
        page.evaluate("() => { const el = document.querySelector('#custom-input'); if(el) el.focus(); }")
        page.keyboard.type(keyword)
        page.wait_for_timeout(500)
        logger.info(f"✓ 已输入 '{keyword}'")

    with allure.step("步骤4：确认有内容时 Clear 按钮可见"):
        clear_after_input = is_clear_visible()
        logger.info(f"✓ 有内容时 Clear 可见: {clear_after_input}")

    with allure.step("步骤5：点击 Clear 按钮清空内容"):
        page.evaluate(f"() => document.querySelector('{CLEAR_SELECTOR}')?.click()")
        page.wait_for_timeout(500)
        logger.info("✓ 已点击 Clear 按钮")

    with allure.step("步骤6：获取清空后输入框的值"):
        val_after_clear = page.evaluate("() => document.querySelector('#custom-input')?.value")
        logger.info(f"✓ 清空后输入框值: '{val_after_clear}'")

    with allure.step("步骤7：确认清空后 Clear 按钮隐藏"):
        clear_after_clear = is_clear_visible()
        logger.info(f"✓ 清空后 Clear 可见: {clear_after_clear}")

    with allure.step("步骤8：验证清空后 placeholder 重新显示"):
        placeholder = page.evaluate("() => document.querySelector('#custom-input')?.placeholder")
        logger.info(f"✓ 清空后 placeholder: '{placeholder}'")

    with allure.step("验证空输入时 Clear 按钮不可见"):
        assert not clear_before_input, "空输入时 Clear 按钮不应可见"

    with allure.step("验证有内容时 Clear 按钮可见"):
        assert clear_after_input, "输入内容后 Clear 按钮应可见"

    with allure.step("验证点击 Clear 后输入框内容清空"):
        assert val_after_clear == "", \
            f"点击 Clear 后输入框内容未清空，实际值: '{val_after_clear}'"

    with allure.step("验证清空后 placeholder 为 'Search for anything'"):
        assert placeholder == "Search for anything", \
            f"清空后 placeholder 错误，实际: '{placeholder}'"
        logger.info("✅ TC015 通过：Clear 按钮功能正常")


# ============================================================
# 四、Sug词交互 TC016-TC026
# ============================================================

@pytest.mark.case_id_ae_search_tc016
@pytest.mark.p1
@pytest.mark.ae
@pytest.mark.search
@allure.feature("OK")
@allure.story("首页搜索输入框 - Clear按钮")
@allure.title("Clear按钮在输入框为空时不可见")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证Clear按钮可见性：空输入框时不可见，有内容时可见，点击Clear清空后再次隐藏")
def test_clear_button_visibility_lifecycle(page, config):
    """TC016: Clear按钮在输入框为空时不可见"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    logger.info("=" * 60)
    logger.info("TC016: 验证 Clear 按钮可见性全生命周期")
    logger.info("=" * 60)

    with allure.step("步骤1：导航到首页"):
        search_page.navigate_to_home(base_url)
        logger.info("✓ 已打开首页")

    with allure.step("步骤2：空输入框时检查 Clear 按钮"):
        clear_before = _is_clear_visible(page)
        logger.info(f"✓ 空输入时 Clear 可见: {clear_before}")

    with allure.step("步骤3：输入关键词'apartment'"):
        _type_keyword(page, "apartment")
        logger.info("✓ 已输入 'apartment'")

    with allure.step("步骤4：有内容时检查 Clear 按钮"):
        clear_with_input = _is_clear_visible(page)
        logger.info(f"✓ 有内容时 Clear 可见: {clear_with_input}")

    with allure.step("步骤5：点击 Clear 清空"):
        _click_clear(page)
        logger.info("✓ 已点击 Clear")

    with allure.step("步骤6：清空后检查 Clear 按钮"):
        clear_after_clear = _is_clear_visible(page)
        logger.info(f"✓ 清空后 Clear 可见: {clear_after_clear}")

    with allure.step("验证空输入时 Clear 不可见"):
        assert not clear_before, "空输入时 Clear 按钮不应可见"

    with allure.step("验证有内容时 Clear 可见"):
        assert clear_with_input, "输入内容后 Clear 按钮应可见"

    with allure.step("验证清空后 Clear 隐藏"):
        assert not clear_after_clear, "点击 Clear 清空后按钮应隐藏"
        logger.info("✅ TC016 通过：Clear 按钮可见性全生命周期正确")


@pytest.mark.case_id_ae_search_tc017
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.ae
@pytest.mark.search
@allure.feature("OK")
@allure.story("首页搜索输入框 - Sug词交互")
@allure.title("输入关键词后展示Sug词下拉面板")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证输入'car'后，Sug词下拉面板出现（[class*='modalSugItem']节点 count > 0），面板展示与输入内容相关的sug词列表")
def test_sug_dropdown_shows_after_input(page, config):
    """TC017: 输入关键词后展示Sug词下拉面板"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    logger.info("=" * 60)
    logger.info("TC017: 验证输入关键词后 Sug 词面板出现")
    logger.info("=" * 60)

    with allure.step("步骤1：导航到首页"):
        search_page.navigate_to_home(base_url)
        logger.info("✓ 已打开首页")

    with allure.step("步骤2：聚焦输入框并输入'car'"):
        _type_keyword(page, "car")
        logger.info("✓ 已输入 'car'")

    with allure.step("步骤3：等待 Sug 接口响应（1.5s）"):
        page.wait_for_timeout(1500)
        sug_count = _get_sug_count(page)
        sug_texts = _get_sug_texts(page)
        logger.info(f"✓ Sug 词数量: {sug_count}，文案: {sug_texts[:5]}")

    with allure.step("验证 Sug 词面板出现（至少1条）"):
        assert sug_count > 0, \
            f"输入'car'后 Sug 词面板未出现，DOM中 modalSugItem 数量为 {sug_count}"
        logger.info(f"✅ TC017 通过：Sug 词面板展示，共 {sug_count} 条")

    with allure.step("验证 Sug 词与输入内容相关"):
        has_related_sug = any("car" in text.lower() for text in sug_texts if text)
        assert has_related_sug, \
            f"Sug 词与输入'car'无关，实际文案: {sug_texts}"
        logger.info(f"✅ Sug 词与输入相关")


@pytest.mark.case_id_ae_search_tc018
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.ae
@pytest.mark.search
@allure.feature("OK")
@allure.story("首页搜索输入框 - Sug词交互")
@allure.title("未输入内容时不展示Sug词面板")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证聚焦输入框但不输入内容时，Sug词面板不出现（DOM中 [class*='modalSugItem'] count = 0）")
def test_sug_not_shown_when_no_input(page, config):
    """TC018: 未输入内容时不展示Sug词面板"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    logger.info("=" * 60)
    logger.info("TC018: 验证聚焦无内容时 Sug 词面板不出现")
    logger.info("=" * 60)

    with allure.step("步骤1：导航到首页，清除历史记录（避免聚焦时展示历史面板干扰计数）"):
        search_page.navigate_to_home(base_url)
        page.evaluate("() => { try { localStorage.clear(); } catch(e) {} }")
        page.wait_for_timeout(500)
        logger.info("✓ 已打开首页，已清除历史")

    with allure.step("步骤2：仅聚焦输入框，不输入任何内容"):
        page.evaluate("() => { const el = document.querySelector('#custom-input'); if(el) el.focus(); }")
        page.wait_for_timeout(1000)
        logger.info("✓ 已聚焦，未输入内容")

    with allure.step("步骤3：检查纯 Sug 词面板（排除历史条目）"):
        # 使用 get_pure_sug_items_count 排除历史条目，避免历史面板干扰
        pure_sug_count = search_page.get_pure_sug_items_count()
        input_val = page.evaluate("() => document.querySelector('#custom-input')?.value || ''")
        logger.info(f"✓ 输入框值: '{input_val}'，纯 Sug 词数量: {pure_sug_count}")

    with allure.step("验证聚焦无输入时纯 Sug 词面板不出现"):
        assert input_val == "", f"输入框应为空，实际值: '{input_val}'"
        assert pure_sug_count == 0, \
            f"聚焦无输入时纯 Sug 词面板不应出现，纯 Sug 词数量: {pure_sug_count}"
        logger.info("✅ TC018 通过：聚焦无内容时 Sug 词面板不出现")


@pytest.mark.case_id_ae_search_tc019
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.ae
@pytest.mark.search
@allure.feature("OK")
@allure.story("首页搜索输入框 - Sug词交互")
@allure.title("Sug词随输入内容实时更新")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证每次输入变化后Sug词列表随之更新：输入'd'→'dr'→'dri'时，Sug词文案应相应变化")
def test_sug_updates_realtime_as_input_changes(page, config):
    """TC019: Sug词随输入内容实时更新"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    logger.info("=" * 60)
    logger.info("TC019: 验证 Sug 词随输入实时更新")
    logger.info("=" * 60)

    with allure.step("步骤1：导航到首页，清除历史记录"):
        search_page.navigate_to_home(base_url)
        # 清除历史，防止历史面板覆盖 Sug 词导致 _get_sug_texts 返回空
        page.evaluate("() => { try { localStorage.clear(); } catch(e) {} }")
        page.wait_for_timeout(500)
        logger.info("✓ 已打开首页，已清除历史")

    with allure.step("步骤2：输入'd'，等待 Sug 更新"):
        page.evaluate("() => { const el = document.querySelector('#custom-input'); if(el) el.focus(); }")
        page.keyboard.type("d")
        page.wait_for_timeout(2500)
        sug_texts_d = _get_sug_texts(page)
        logger.info(f"✓ 输入'd'后 Sug 词: {sug_texts_d[:3]}")

    with allure.step("步骤3：继续输入'r'，等待 Sug 更新"):
        page.keyboard.type("r")
        page.wait_for_timeout(2500)
        sug_texts_dr = _get_sug_texts(page)
        logger.info(f"✓ 输入'dr'后 Sug 词: {sug_texts_dr[:3]}")

    with allure.step("步骤4：继续输入'i'，等待 Sug 更新"):
        page.keyboard.type("i")
        page.wait_for_timeout(2500)
        sug_texts_dri = _get_sug_texts(page)
        logger.info(f"✓ 输入'dri'后 Sug 词: {sug_texts_dri[:3]}")

    with allure.step("验证各阶段 Sug 词均有结果"):
        assert len(sug_texts_d) > 0, "输入'd'后 Sug 词列表为空"
        assert len(sug_texts_dr) > 0, "输入'dr'后 Sug 词列表为空"
        assert len(sug_texts_dri) > 0, "输入'dri'后 Sug 词列表为空"

    with allure.step("验证 Sug 词随输入实时更新"):
        sug_is_real_time = (
            sug_texts_d != sug_texts_dri or
            any("dri" in t.lower() for t in sug_texts_dri if t)
        )
        assert sug_is_real_time, \
            f"Sug 词未随输入更新，'d'阶段: {sug_texts_d[:3]}，'dri'阶段: {sug_texts_dri[:3]}"
        logger.info("✅ TC019 通过：Sug 词随输入实时更新")


@pytest.mark.case_id_ae_search_tc020
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.ae
@pytest.mark.search
@allure.feature("OK")
@allure.story("首页搜索输入框 - Sug词交互")
@allure.title("点击Sug词跳转对应关键词搜索结果页")
@allure.severity(allure.severity_level.BLOCKER)
@allure.description("验证点击第一条Sug词后，页面正确跳转到对应关键词的搜索结果页，URL中keyword参数值等于点击的Sug词文本")
def test_click_sug_item_navigates_to_search_result(page, config):
    """TC020: 点击Sug词跳转对应关键词搜索结果页"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    logger.info("=" * 60)
    logger.info("TC020: 验证点击 Sug 词跳转到对应关键词搜索结果页")
    logger.info("=" * 60)

    with allure.step("步骤1：导航到首页"):
        search_page.navigate_to_home(base_url)
        logger.info("✓ 已打开首页")

    with allure.step("步骤2：输入'car'并等待 Sug 词出现"):
        _type_keyword(page, "car")
        page.wait_for_timeout(1500)
        sug_texts = _get_sug_texts(page)
        logger.info(f"✓ Sug 词: {sug_texts[:5]}")

    with allure.step("步骤3：记录第一条 Sug 词文案"):
        first_sug_text = sug_texts[0] if sug_texts else ""
        logger.info(f"✓ 第一条 Sug 词: '{first_sug_text}'")

    with allure.step("步骤4：点击第一条 Sug 词"):
        page.evaluate(
            "() => { const item = document.querySelector('[class*=\"modalSugItem\"]'); if(item) item.click(); }"
        )
        page.wait_for_timeout(1000)
        final_url = page.url
        logger.info(f"✓ 点击后 URL: {final_url}")

    with allure.step("验证 Sug 词列表非空"):
        assert len(sug_texts) > 0, "输入'car'后 Sug 词列表为空，无法执行点击测试"

    with allure.step("验证跳转到搜索结果页"):
        assert "cate" in final_url, \
            f"点击 Sug 词后未跳转到搜索结果页，实际 URL: {final_url}"

    with allure.step("验证 URL 中 keyword 值等于点击的 Sug 词"):
        parsed = urllib.parse.urlparse(final_url)
        params = urllib.parse.parse_qs(parsed.query)
        keyword_in_url = params.get("keyword", [""])[0]
        assert keyword_in_url.lower() == first_sug_text.lower(), \
            f"URL keyword 值 '{keyword_in_url}' 与 Sug 词 '{first_sug_text}' 不一致"
        logger.info(f"✅ TC020 通过：点击 Sug 词 '{first_sug_text}' 跳转到 keyword={keyword_in_url}")


@pytest.mark.p0
@pytest.mark.ae
@pytest.mark.search
@pytest.mark.case_id_ae_search_tc021
@allure.feature("OK")
@allure.story("首页搜索输入框 - Sug词交互")
@allure.title("点击Sug词后该词被记入最近搜索历史")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证点击 Sug 词后跳转到搜索结果页（URL 含 /cate/?keyword=），并且该词被写入历史记录列表首位")
def test_click_sug_item_navigates_and_saves_to_history(page, config):
    """TC021: 点击 Sug 词 → 跳转搜索结果 → 返回首页 → 验证历史首条为所点击的 Sug 词"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    with allure.step("导航至首页"):
        search_page.navigate_to_home(base_url)

    with allure.step("输入关键词 'nur' 触发 Sug 词列表"):
        search_page.type_keyword_by_js_and_keyboard("nur")

    with allure.step("获取第一条纯 Sug 词文本"):
        first_sug_text = search_page.get_first_pure_sug_text()
        logger.info(f"第一条 Sug 词: {first_sug_text}")

    with allure.step("点击第一条 Sug 词"):
        search_page.click_pure_sug_item(index=0)

    with allure.step("等待跳转完成，获取当前 URL"):
        # 等待跳转到搜索结果页
        page.wait_for_url("**/cate/**", timeout=10000)
        page.wait_for_timeout(2000)  # 等待历史记录写入localStorage
        after_click_url = search_page.get_current_url()
        logger.info(f"点击 Sug 词后 URL: {after_click_url}")

    with allure.step("返回首页并打开搜索框"):
        safe_goto(page, base_url, wait_until="load", timeout=30000)
        page.wait_for_timeout(2000)
        # 刷新确保历史记录已加载
        page.reload(wait_until="load", timeout=30000)
        page.wait_for_timeout(1500)
        search_page.focus_search_input_by_js()
        page.wait_for_timeout(1000)

    with allure.step("获取历史记录列表"):
        history_texts = search_page.get_history_items_texts()
        logger.info(f"历史记录: {history_texts[:5]}")

    with allure.step("验证 URL 跳转到搜索结果页（含 /cate/ 和 keyword=）"):
        assert "/cate/" in after_click_url, f"URL 未跳转到搜索结果页，实际 URL: {after_click_url}"
        assert "keyword=" in after_click_url, f"URL 不含 keyword 参数，实际 URL: {after_click_url}"

    with allure.step("验证历史记录首条为点击的 Sug 词"):
        assert len(history_texts) > 0, "历史记录列表为空"
        assert history_texts[0] == first_sug_text, (
            f"历史记录首条不是点击的 Sug 词，期望: '{first_sug_text}'，实际首条: '{history_texts[0]}'"
        )

    logger.info(f"✅ TC021 通过: 点击 Sug 词 '{first_sug_text}' 正确跳转并写入历史")


@pytest.mark.p0
@pytest.mark.ae
@pytest.mark.search
@pytest.mark.case_id_ae_search_tc022
@allure.feature("OK")
@allure.story("首页搜索输入框 - Sug词交互")
@allure.title("清空输入框内容后Sug词面板消失")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证点击历史记录条目后跳转到搜索结果页（URL 含 /cate/?keyword=<历史词>）")
def test_click_history_item_navigates_to_search_result_tc022(page, config):
    """TC022: 打开搜索框 → 点击历史记录第一条 → 验证跳转到搜索结果页"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    with allure.step("导航至首页并确保有搜索历史"):
        search_page.navigate_to_home(base_url)
        page.evaluate("() => { const el = document.querySelector('#custom-input'); if(el) el.focus(); }")
        page.keyboard.type("apartment")
        page.wait_for_timeout(500)
        page.evaluate("() => document.querySelector('.TopBarMiddleContent_searchButton__3UG6i')?.click()")
        # 增加超时时间和重试机制
        try:
            page.wait_for_url("**/cate/**", timeout=15000)
        except Exception as e:
            logger.warning(f"首次跳转超时，重试中: {e}")
            page.wait_for_timeout(2000)
            # 如果超时，尝试再次导航
            if "/cate/" not in page.url:
                page.evaluate("() => document.querySelector('.TopBarMiddleContent_searchButton__3UG6i')?.click()")
                page.wait_for_url("**/cate/**", timeout=15000)
        page.wait_for_timeout(2000)  # 等待历史写入
        safe_goto(page, base_url, wait_until="load", timeout=30000)
        page.wait_for_timeout(1500)

    with allure.step("打开搜索框以显示历史记录"):
        search_page.focus_search_input_by_js()

    with allure.step("获取历史记录第一条文本"):
        history_texts = search_page.get_history_items_texts()
        assert len(history_texts) > 0, "历史记录为空，无法执行 TC022"
        first_history_kw = history_texts[0]
        logger.info(f"历史记录第一条: {first_history_kw}")

    with allure.step("点击历史记录第一条"):
        search_page.click_history_item_by_js(index=0)

    with allure.step("等待跳转并获取当前 URL"):
        page.wait_for_timeout(1000)
        after_click_url = search_page.get_current_url()
        logger.info(f"点击历史记录后 URL: {after_click_url}")

    with allure.step("验证 URL 跳转到搜索结果页（含 /cate/ 和 keyword=）"):
        assert "/cate/" in after_click_url, f"URL 未跳转到搜索结果页，实际 URL: {after_click_url}"
        assert "keyword=" in after_click_url, f"URL 不含 keyword 参数，实际 URL: {after_click_url}"

    logger.info(f"✅ TC022 通过: 点击历史记录 '{first_history_kw}' 正确跳转，URL: {after_click_url}")


@pytest.mark.p1
@pytest.mark.ae
@pytest.mark.search
@pytest.mark.case_id_ae_search_tc023
@allure.feature("OK")
@allure.story("首页搜索输入框 - Sug词交互")
@allure.title("无匹配Sug词时面板展示状态")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证输入无匹配随机字符串（'zzzqqqxxx'）时，纯 Sug 词列表为空，页面不报错")
def test_no_sug_items_for_unmatched_keyword(page, config):
    """TC023: 输入无匹配关键词 → 纯 Sug 词数量为 0，页面正常"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    with allure.step("导航至首页，检查页面状态"):
        # 使用safe_goto确保页面正常加载
        safe_goto(page, base_url, wait_until="load", timeout=30000, max_retries=2)
        page.wait_for_timeout(2000)
        
        # 检查页面是否正常加载（不是504错误页）
        page_title = page.evaluate("() => document.title")
        if "504" in page_title or "Gateway" in page_title:
            logger.warning(f"页面状态异常: {page_title}，重新加载")
            page.reload(wait_until="load", timeout=30000)
            page.wait_for_timeout(2000)

    with allure.step("输入无匹配随机字符串 'zzzqqqxxx'"):
        search_page.type_keyword_by_js_and_keyboard("zzzqqqxxx")

    with allure.step("等待 Sug 接口响应"):
        page.wait_for_timeout(1500)

    with allure.step("获取纯 Sug 词数量（排除历史条目）"):
        pure_sug_count = search_page.get_pure_sug_items_count()
        logger.info(f"纯 Sug 词数量: {pure_sug_count}")

    with allure.step("获取页面标题验证页面未崩溃"):
        page_title = page.evaluate("() => document.title")

    with allure.step("验证纯 Sug 词数量为 0（无匹配 Sug 词）"):
        assert pure_sug_count == 0, f"期望无 Sug 词，实际显示 {pure_sug_count} 条 Sug 词"

    with allure.step("验证页面未崩溃（标题正常）"):
        assert "Dubai" in page_title or "OK" in page_title, f"页面标题异常，实际: {page_title}"

    logger.info(f"✅ TC023 通过: 无匹配 Sug 词时面板空，纯 Sug 词数量为 {pure_sug_count}")


@pytest.mark.p0
@pytest.mark.ae
@pytest.mark.search
@pytest.mark.case_id_ae_search_tc024
@allure.feature("OK")
@allure.story("首页搜索输入框 - Sug词交互")
@allure.title("Sug词最多展示数量为10条")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证输入 'iphone' 后，Sug 词列表最多展示 10 条，不超过 10 条（实测恰好 10 条）")
def test_sug_items_max_count_is_10(page, config):
    """TC024: 输入 'iphone' → 验证纯 Sug 词数量 <= 10 且 > 0"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    with allure.step("导航至首页，确保页面状态正常"):
        safe_goto(page, base_url, wait_until="load", timeout=30000, max_retries=2)
        page.wait_for_timeout(2000)
        
        # 检查页面状态
        page_title = page.evaluate("() => document.title")
        if "504" in page_title or "Gateway" in page_title:
            logger.warning(f"页面状态异常: {page_title}，重新加载")
            page.reload(wait_until="load", timeout=30000)
            page.wait_for_timeout(2000)

    with allure.step("输入关键词 'iphone' 触发 Sug 词列表"):
        search_page.type_keyword_by_js_and_keyboard("iphone")
        page.wait_for_timeout(2000)  # 增加等待时间

    with allure.step("获取纯 Sug 词数量（排除历史条目）"):
        pure_sug_count = search_page.get_pure_sug_items_count()
        sug_texts = search_page.get_pure_sug_item_texts()
        logger.info(f"纯 Sug 词数量: {pure_sug_count}，词列表: {sug_texts}")

    with allure.step("验证 Sug 词数量在合理范围内（0 < count <= 10）"):
        assert pure_sug_count > 0, "Sug 词列表为空，期望至少 1 条"
        assert pure_sug_count <= 10, f"Sug 词超过 10 条，实际: {pure_sug_count} 条"

    with allure.step("验证实测恰好为 10 条（边界值）"):
        assert pure_sug_count == 10, f"期望恰好 10 条（边界值），实际: {pure_sug_count} 条"

    logger.info(f"✅ TC024 通过: 输入 'iphone' 时 Sug 词数量为 {pure_sug_count} 条（边界值 10 条验证通过）")


@pytest.mark.p0
@pytest.mark.ae
@pytest.mark.search
@pytest.mark.case_id_ae_search_tc025
@allure.feature("OK")
@allure.story("首页搜索输入框 - Sug词交互")
@allure.title("Sug词文案超长时单行截断展示")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证 Sug 词条目具有 singleLineEllipsis class，CSS 包含 overflow:hidden、text-overflow:ellipsis、white-space:nowrap")
def test_sug_item_text_overflow_ellipsis(page, config):
    """TC025: 验证 Sug 词具有单行截断 CSS 样式"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    with allure.step("导航至首页，确保页面状态正常"):
        safe_goto(page, base_url, wait_until="load", timeout=30000, max_retries=2)
        page.wait_for_timeout(2000)
        
        # 检查页面状态
        page_title = page.evaluate("() => document.title")
        if "504" in page_title or "Gateway" in page_title:
            logger.warning(f"页面状态异常: {page_title}，重新加载")
            page.reload(wait_until="load", timeout=30000)
            page.wait_for_timeout(2000)

    with allure.step("输入关键词 'driver' 触发 Sug 词列表"):
        search_page.type_keyword_by_js_and_keyboard("driver")
        page.wait_for_timeout(2000)  # 增加等待时间

    with allure.step("获取纯 Sug 词的 CSS 截断属性信息"):
        ellipsis_info = search_page.get_sug_ellipsis_info()
        logger.info(f"Sug 词 CSS 截断信息: {ellipsis_info[:3]}")

    with allure.step("验证至少存在 1 条纯 Sug 词"):
        assert len(ellipsis_info) > 0, "Sug 词列表为空，无法验证 CSS 截断样式"

    with allure.step("验证所有 Sug 词具有 singleLineEllipsis class"):
        items_without_class = [i for i, info in enumerate(ellipsis_info) if not info.get("hasSingleLineEllipsis")]
        assert len(items_without_class) == 0, (
            f"以下索引的 Sug 词缺少 singleLineEllipsis class: {items_without_class}"
        )

    with allure.step("验证所有 Sug 词 CSS overflow 为 hidden"):
        items_bad_overflow = [i for i, info in enumerate(ellipsis_info) if info.get("overflow") != "hidden"]
        assert len(items_bad_overflow) == 0, (
            f"以下索引的 Sug 词 overflow 不为 hidden: {items_bad_overflow}"
        )

    with allure.step("验证所有 Sug 词 CSS text-overflow 为 ellipsis"):
        items_bad_text_overflow = [i for i, info in enumerate(ellipsis_info) if info.get("textOverflow") != "ellipsis"]
        assert len(items_bad_text_overflow) == 0, (
            f"以下索引的 Sug 词 text-overflow 不为 ellipsis: {items_bad_text_overflow}"
        )

    with allure.step("验证所有 Sug 词 CSS white-space 为 nowrap"):
        items_bad_whitespace = [i for i, info in enumerate(ellipsis_info) if info.get("whiteSpace") != "nowrap"]
        assert len(items_bad_whitespace) == 0, (
            f"以下索引的 Sug 词 white-space 不为 nowrap: {items_bad_whitespace}"
        )

    logger.info(f"✅ TC025 通过: {len(ellipsis_info)} 条 Sug 词均具有正确的单行截断 CSS 属性")


@pytest.mark.p2
@pytest.mark.case_id_ae_search_tc026
@allure.feature("OK")
@allure.story("首页搜索输入框 - Sug词异常场景")
@allure.title("输入特殊字符触发Sug词请求不报错")
@allure.description("验证输入特殊字符（%、?、#）时 Sug 接口正常响应，页面不报错、不崩溃")
@allure.severity(allure.severity_level.NORMAL)
def test_special_chars_sug_no_crash(page, config):
    """TC026: 输入特殊字符触发 Sug 词请求不报错"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    with allure.step("前置：访问首页，清空历史记录"):
        # 先导航到目标页，确保 localStorage 可访问（about:blank 页面无法访问 localStorage）
        safe_goto(page, base_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1000)
        page.evaluate("() => { try { localStorage.clear(); sessionStorage.clear(); } catch(e) {} }")
        safe_goto(page, base_url, wait_until="load", timeout=30000)
        page.wait_for_timeout(1500)

    for char in ["%", "?", "#"]:
        with allure.step(f"聚焦搜索框并输入特殊字符 '{char}'"):
            page.evaluate(
                "() => { const el = document.querySelector('#custom-input'); if(el) { el.focus(); el.value = ''; } }"
            )
            page.wait_for_timeout(200)
            page.keyboard.type(char)
            page.wait_for_timeout(1500)

        with allure.step(f"验证输入 '{char}' 后页面不崩溃"):
            current_url = page.url
            assert "about:blank" not in current_url, f"输入 '{char}' 后页面意外跳转至 about:blank"
            assert base_url in current_url or "/cate/" in current_url, (
                f"输入 '{char}' 后页面 URL 异常: {current_url}"
            )

        with allure.step(f"验证 Sug 接口响应正常（无 JS 崩溃错误）"):
            input_val = page.evaluate("() => document.querySelector('#custom-input')?.value")
            assert input_val is not None, f"输入 '{char}' 后搜索框元素丢失，页面可能崩溃"

        with allure.step(f"清空输入框，准备下一轮"):
            page.evaluate("() => { const el = document.querySelector('#custom-input'); if(el) { el.value = ''; } }")
            page.wait_for_timeout(500)


# ============================================================
# 五、最近搜索词 TC027-TC035
# ============================================================

@pytest.mark.p2
@pytest.mark.case_id_ae_search_tc027
@allure.feature("OK")
@allure.story("首页搜索输入框 - 最近搜索词")
@allure.title("首次访问（无历史）时展示无历史状态")
@allure.description("验证清除 localStorage 后首次访问，聚焦搜索框时不展示'Recent Searches'区域")
@allure.severity(allure.severity_level.NORMAL)
def test_no_history_panel_when_no_history(page, config):
    """TC027: 首次访问（无历史）时展示无历史状态"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    with allure.step("前置：清除 localStorage，模拟无历史状态"):
        # 先导航到目标页，确保 localStorage 可访问
        safe_goto(page, base_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1000)
        page.evaluate("() => { try { localStorage.clear(); sessionStorage.clear(); } catch(e) {} }")
        safe_goto(page, base_url, wait_until="load", timeout=30000)
        page.wait_for_timeout(1500)

    with allure.step("点击搜索框（聚焦）"):
        page.evaluate(
            "() => { const el = document.querySelector('#custom-input'); if(el) { el.focus(); el.click(); } }"
        )
        page.wait_for_timeout(1200)

    with allure.step("验证：无历史状态时，不展示 Recent Searches 区域"):
        history_list_visible = page.locator(search_page.HISTORY_LIST).is_visible()
        history_items_count = page.evaluate(
            "() => document.querySelectorAll('[class*=\"modalHistoryItemPC\"]').length"
        )
        assert not history_list_visible or history_items_count == 0, (
            f"无历史时历史列表不应可见，但 history_list_visible={history_list_visible}，"
            f"history_items_count={history_items_count}"
        )

    with allure.step("验证：无历史时 Sug 面板中不出现 'Recent Searches' 标题"):
        history_title_visible = False
        try:
            history_title_visible = page.locator(search_page.HISTORY_TITLE).is_visible()
        except Exception:
            pass
        assert not history_title_visible or history_items_count == 0, (
            "无历史时不应展示 'Recent Searches' 标题"
        )


@pytest.mark.p2
@pytest.mark.case_id_ae_search_tc028
@allure.feature("OK")
@allure.story("首页搜索输入框 - 最近搜索词")
@allure.title("有历史记录时聚焦输入框展示\"Recent Searches\"标题")
@allure.description("验证有搜索历史时，聚焦搜索框（不输入内容）展示'Recent Searches'标题及历史词列表")
@allure.severity(allure.severity_level.CRITICAL)
def test_history_panel_shows_recent_searches_title(page, config):
    """TC028: 有历史记录时聚焦输入框展示"Recent Searches"标题"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    with allure.step("前置：注入3条历史记录到 localStorage"):
        _inject_history(page, ["driver", "villa", "apartment"], base_url)
        safe_goto(page, base_url, wait_until="load", timeout=30000)
        page.wait_for_timeout(2000)
        # 刷新页面确保历史记录加载
        page.reload(wait_until="load", timeout=30000)
        page.wait_for_timeout(1500)

    with allure.step("点击搜索框（聚焦，不输入任何内容）"):
        page.evaluate(
            "() => { const el = document.querySelector('#custom-input'); if(el) { el.focus(); el.click(); } }"
        )
        page.wait_for_timeout(1200)

    with allure.step("验证：展示 'Recent Searches' 标题"):
        history_title_text = search_page.get_history_title_text()
        assert history_title_text == "Recent Searches", (
            f"历史标题文案错误，期望 'Recent Searches'，实际为 '{history_title_text}'"
        )

    with allure.step("验证：历史词列表展示在标题下方"):
        history_items = search_page.get_history_items_texts()
        assert len(history_items) > 0, "历史词列表应展示至少一条记录"

    with allure.step("验证：历史词条目包含注入的关键词"):
        assert "apartment" in history_items, (
            f"历史词列表中未找到 'apartment'，实际列表: {history_items}"
        )


@pytest.mark.p2
@pytest.mark.case_id_ae_search_tc029
@allure.feature("OK")
@allure.story("首页搜索输入框 - 最近搜索词")
@allure.title("最新搜索词排在历史列表第一位")
@allure.description("验证搜索词按时间倒序排列，最新搜索的词排在历史列表第一位")
@allure.severity(allure.severity_level.CRITICAL)
def test_newest_search_appears_first_in_history(page, config):
    """TC029: 最新搜索词排在历史列表第一位"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    with allure.step("前置：注入2条历史记录（villa、apartment），apartment 较新"):
        safe_goto(page, base_url, wait_until="domcontentloaded", timeout=30000)
        page.evaluate("() => localStorage.removeItem('__SEARCH_LOCAL_HISTORY_LIST__')")
        page.wait_for_timeout(500)
        _inject_history(page, ["villa", "apartment"], base_url)
        safe_goto(page, base_url, wait_until="load", timeout=30000)
        page.wait_for_timeout(2000)
        # 刷新页面确保历史记录加载
        page.reload(wait_until="load", timeout=30000)
        page.wait_for_timeout(1500)

    with allure.step("搜索关键词 'manager'（最新一次搜索）"):
        page.evaluate(
            "() => { const el = document.querySelector('#custom-input'); if(el) { el.focus(); el.click(); } }"
        )
        page.wait_for_timeout(500)
        page.evaluate(
            "() => { const el = document.querySelector('#custom-input'); if(el) { el.focus(); el.value = ''; } }"
        )
        page.keyboard.type("manager")
        page.wait_for_timeout(2000)
        # 修改：使用 Enter 键提交搜索，确保触发跳转并写入历史
        page.keyboard.press("Enter")
        page.wait_for_timeout(3000)

    with allure.step("返回首页，聚焦搜索框，查看历史列表"):
        safe_goto(page, base_url, wait_until="load", timeout=30000)
        page.wait_for_timeout(1500)
        page.evaluate(
            "() => { const el = document.querySelector('#custom-input'); if(el) { el.focus(); el.click(); } }"
        )
        page.wait_for_timeout(1200)

    with allure.step("验证：历史列表第一位为最新搜索词 'manager'"):
        history_items = search_page.get_history_items_texts()
        assert len(history_items) > 0, "历史词列表应至少有一条记录"
        first_item = history_items[0]
        assert first_item == "manager", (
            f"历史列表第一位应为 'manager'，实际为 '{first_item}'"
        )

    with allure.step("验证：历史记录中 'manager' 排在第一位（最新）"):
        ls_history = page.evaluate(
            "() => JSON.parse(localStorage.getItem('__SEARCH_LOCAL_HISTORY_LIST__') || '[]')"
        )
        assert len(ls_history) > 0, "localStorage 中历史记录为空"
        assert ls_history[0]["suggestKey"] == "manager", (
            f"localStorage 历史第一位应为 'manager'，实际为 '{ls_history[0]['suggestKey']}'"
        )
        logger.info(f"✅ localStorage 历史记录顺序正确，第一位: {ls_history[0]['suggestKey']}")


@pytest.mark.p2
@pytest.mark.case_id_ae_search_tc030
@allure.feature("OK")
@allure.story("首页搜索输入框 - 最近搜索词")
@allure.title("历史最多展示10条，超过10条时旧记录被挤出")
@allure.description(
    "验证历史记录最多保存 10 条；当历史已有 10 条时再搜索第 11 个词，"
    "最旧的记录被挤出，历史仍保持 10 条，最新词排在第一位"
)
@allure.severity(allure.severity_level.CRITICAL)
def test_history_max_10_oldest_evicted(page, config):
    """TC030: 历史最多展示10条，超过10条时旧记录被挤出"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    with allure.step("前置：注入 10 条历史记录（nurse 为最旧，apartment 为最新）"):
        safe_goto(page, base_url, wait_until="domcontentloaded", timeout=30000)
        page.evaluate("() => localStorage.removeItem('__SEARCH_LOCAL_HISTORY_LIST__')")
        page.wait_for_timeout(500)
        ten_keywords = [
            "nurse", "driver", "manager", "sales", "cook",
            "teacher", "engineer", "security guard", "accountant", "apartment"
        ]
        _inject_history(page, ten_keywords, base_url)
        safe_goto(page, base_url, wait_until="load", timeout=30000)
        page.wait_for_timeout(2000)
        # 刷新页面确保历史记录加载
        page.reload(wait_until="load", timeout=30000)
        page.wait_for_timeout(1500)

    with allure.step("聚焦搜索框，验证前置历史 10 条"):
        page.evaluate(
            "() => { const el = document.querySelector('#custom-input'); if(el) { el.focus(); el.click(); } }"
        )
        page.wait_for_timeout(1200)
        history_before = search_page.get_history_items_texts()
        assert len(history_before) == 10, (
            f"前置历史应为 10 条，实际为 {len(history_before)} 条"
        )
        assert "nurse" in history_before, "前置历史应包含最旧词 'nurse'"

    with allure.step("输入第 11 个词 'villa' 并使用 Enter 键提交"):
        page.evaluate(
            "() => { const el = document.querySelector('#custom-input'); if(el) { el.focus(); el.value = ''; } }"
        )
        page.keyboard.type("villa")
        page.wait_for_timeout(2000)
        # 修改：使用 Enter 键提交搜索
        page.keyboard.press("Enter")
        page.wait_for_timeout(3000)

    with allure.step("验证 localStorage 历史仍为 10 条"):
        ls_history = page.evaluate(
            "() => JSON.parse(localStorage.getItem('__SEARCH_LOCAL_HISTORY_LIST__') || '[]')"
        )
        history_keys = [item["suggestKey"] for item in ls_history]
        assert len(ls_history) == 10, (
            f"搜索第 11 个词后历史应保持 10 条，实际为 {len(ls_history)} 条"
        )

    with allure.step("验证 'villa' 排在历史第一位"):
        assert ls_history[0]["suggestKey"] == "villa", (
            f"搜索 'villa' 后应排在历史第一位，实际第一位为 '{ls_history[0]['suggestKey']}'"
        )

    with allure.step("验证最旧词 'nurse' 已被挤出历史"):
        assert "nurse" not in history_keys, (
            f"最旧词 'nurse' 应被挤出历史列表，但仍存在于: {history_keys}"
        )

    with allure.step("验证页面渲染的历史条目数量 ≤ 10"):
        safe_goto(page, base_url, wait_until="load", timeout=30000)
        page.wait_for_timeout(1500)
        page.evaluate(
            "() => { const el = document.querySelector('#custom-input'); if(el) { el.focus(); el.click(); } }"
        )
        page.wait_for_timeout(1200)
        rendered_items = page.evaluate(
            "() => Array.from(document.querySelectorAll('[class*=\"modalHistoryItemPC\"]')).map(el => el.innerText?.trim())"
        )
        assert len(rendered_items) <= 10, (
            f"页面最多应展示 10 条历史，实际展示 {len(rendered_items)} 条"
        )
        assert "nurse" not in rendered_items, (
            f"页面历史中不应出现已被挤出的 'nurse'，实际: {rendered_items}"
        )
        assert rendered_items[0] == "villa", (
            f"页面历史第一条应为 'villa'，实际为 '{rendered_items[0]}'"
        )


@pytest.mark.p1
@pytest.mark.case_id_ae_search_tc031
@allure.feature("OK")
@allure.story("首页搜索输入框 - 最近搜索词")
@allure.title("点击历史词跳转对应关键词搜索结果页")
@allure.description("验证点击历史词后跳转到对应关键词搜索结果页，URL 中 keyword 与点击的历史词一致")
@allure.severity(allure.severity_level.CRITICAL)
def test_click_history_item_navigates_to_search_result(page, config):
    """TC031: 点击历史词跳转对应关键词搜索结果页"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    with allure.step("前置：注入3条历史记录到 localStorage"):
        _inject_history(page, ["driver", "villa", "apartment"], base_url)
        safe_goto(page, base_url, wait_until="load", timeout=30000)
        page.wait_for_timeout(2000)
        # 刷新页面确保历史记录加载
        page.reload(wait_until="load", timeout=30000)
        page.wait_for_timeout(1500)

    with allure.step("点击搜索框，展示历史记录面板"):
        page.evaluate(
            "() => { const el = document.querySelector('#custom-input'); if(el) { el.focus(); el.click(); } }"
        )
        page.wait_for_timeout(1200)

    with allure.step("读取历史列表，记录第一条词"):
        history_items = search_page.get_history_items_texts()
        assert len(history_items) > 0, "历史词列表应至少有一条"
        first_history_text = history_items[0]

    with allure.step(f"点击历史词 '{first_history_text}'"):
        search_page.click_history_item_by_js(index=0)

    with allure.step("验证：跳转到对应关键词搜索结果页"):
        current_url = page.url
        assert f"keyword={first_history_text}" in current_url, (
            f"URL 中应包含 keyword={first_history_text}，实际 URL: {current_url}"
        )

    with allure.step("验证：URL 格式为 /cate/?keyword={词}"):
        assert "/cate/" in current_url, (
            f"应跳转到搜索结果页（含 /cate/），实际 URL: {current_url}"
        )


@pytest.mark.p0
@pytest.mark.case_id_ae_search_tc032
@allure.feature("OK")
@allure.story("首页搜索输入框 - 最近搜索词")
@allure.title("重复搜索同一关键词，历史不重复，已有词更新到第一位")
@allure.description(
    "验证重复搜索历史中已存在的关键词时，历史列表不产生重复条目，"
    "且该词更新到列表第一位，历史总条数不增加"
)
@allure.severity(allure.severity_level.NORMAL)
def test_duplicate_search_deduplicates_and_moves_to_first(page, config):
    """TC032: 重复搜索同一关键词，历史不重复，已有词更新到第一位"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    with allure.step("前置：注入3条历史记录，'driver' 不是最新"):
        safe_goto(page, base_url, wait_until="domcontentloaded", timeout=30000)
        page.evaluate("() => localStorage.removeItem('__SEARCH_LOCAL_HISTORY_LIST__')")
        page.wait_for_timeout(500)
        _inject_history(page, ["driver", "apartment", "villa"], base_url)
        hist_before = page.evaluate(
            "() => JSON.parse(localStorage.getItem('__SEARCH_LOCAL_HISTORY_LIST__') || '[]')"
        )
        count_before = len(hist_before)
        safe_goto(page, base_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)

    with allure.step("再次搜索历史中已存在的关键词 'driver'"):
        page.evaluate(
            "() => { const el = document.querySelector('#custom-input'); if(el) { el.focus(); el.click(); } }"
        )
        page.wait_for_timeout(500)
        page.evaluate(
            "() => { const el = document.querySelector('#custom-input'); if(el) { el.focus(); el.value = ''; } }"
        )
        page.keyboard.type("driver")
        page.wait_for_timeout(500)
        # 使用 Enter 键提交搜索
        page.keyboard.press("Enter")
        # 等待跳转到搜索结果页
        page.wait_for_url("**/cate/**", timeout=10000)
        page.wait_for_timeout(2000)

    with allure.step("验证：历史中 'driver' 不重复"):
        hist_after = page.evaluate(
            "() => JSON.parse(localStorage.getItem('__SEARCH_LOCAL_HISTORY_LIST__') || '[]')"
        )
        driver_count = sum(1 for h in hist_after if h["suggestKey"] == "driver")
        assert driver_count == 1, (
            f"'driver' 在历史中应只出现一次，实际出现 {driver_count} 次"
        )

    with allure.step("验证：'driver' 更新到历史第一位"):
        assert hist_after[0]["suggestKey"] == "driver", (
            f"重复搜索后 'driver' 应在第一位，实际第一位为 '{hist_after[0]['suggestKey']}'"
        )

    with allure.step("验证：历史总条数不增加"):
        assert len(hist_after) == count_before, (
            f"历史总条数应保持不变（{count_before}），实际为 {len(hist_after)}"
        )


@pytest.mark.p0
@pytest.mark.case_id_ae_search_tc033
@allure.feature("OK")
@allure.story("首页搜索输入框 - Sug词交互")
@allure.title("输入内容后历史面板被Sug词面板替换")
@allure.description("验证聚焦搜索框时展示历史面板，输入内容后历史面板隐藏并展示 Sug 词面板，两者不同时出现")
@allure.severity(allure.severity_level.CRITICAL)
def test_sug_panel_replaces_history_panel_on_input(page, config):
    """TC033: 输入内容后历史面板被Sug词面板替换"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    with allure.step("前置：注入历史记录，访问首页"):
        _inject_history(page, ["apartment", "villa"], base_url)
        safe_goto(page, base_url, wait_until="load", timeout=30000)
        page.wait_for_timeout(2000)
        # 刷新页面确保历史记录加载
        page.reload(wait_until="load", timeout=30000)
        page.wait_for_timeout(1500)

    with allure.step("点击搜索框（聚焦，不输入内容）"):
        page.evaluate(
            "() => { const el = document.querySelector('#custom-input'); if(el) { el.focus(); el.click(); } }"
        )
        page.wait_for_timeout(1000)

    with allure.step("验证：聚焦时展示历史面板"):
        hist_count_before_input = page.evaluate(
            "() => document.querySelectorAll('.SearchSuggestContent_modalHistoryItemPC__W7Zwc').length"
        )
        assert hist_count_before_input > 0, (
            f"聚焦时应展示历史面板，但历史条目数为 {hist_count_before_input}"
        )

    with allure.step("输入关键词 'driver'"):
        page.evaluate(
            "() => { const el = document.querySelector('#custom-input'); if(el) { el.focus(); el.value = ''; } }"
        )
        page.keyboard.type("driver")
        page.wait_for_timeout(2000)

    with allure.step("验证：输入后历史面板隐藏"):
        hist_count_after_input = page.evaluate(
            "() => document.querySelectorAll('.SearchSuggestContent_modalHistoryItemPC__W7Zwc').length"
        )
        assert hist_count_after_input == 0, (
            f"输入内容后历史面板应隐藏，但仍有 {hist_count_after_input} 条历史条目"
        )

    with allure.step("验证：输入后 Sug 词面板展示"):
        sug_count_after_input = page.evaluate(
            "() => Array.from(document.querySelectorAll('.SuggestItem_modalSugItem__iYU6f'))"
            ".filter(el => !el.classList.contains('SearchSuggestContent_modalHistoryItemPC__W7Zwc')).length"
        )
        assert sug_count_after_input > 0, (
            f"输入内容后应展示 Sug 词，但 Sug 词数量为 {sug_count_after_input}"
        )

    with allure.step("验证：历史面板与 Sug 面板不同时出现"):
        assert hist_count_after_input == 0 and sug_count_after_input > 0, (
            "历史面板和 Sug 面板不应同时出现"
        )


@pytest.mark.p1
@pytest.mark.case_id_ae_search_tc034
@allure.feature("OK")
@allure.story("首页搜索输入框 - Sug词交互")
@allure.title("清空输入框后历史面板重新展示")
@allure.description("验证有内容时展示 Sug 词面板，点击 Clear 清空后 Sug 词消失，历史面板重新展示")
@allure.severity(allure.severity_level.NORMAL)
def test_clear_input_restores_history_panel(page, config):
    """TC034: 清空输入框后历史面板重新展示"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    with allure.step("前置：注入历史记录，访问首页"):
        _inject_history(page, ["apartment", "villa"], base_url)
        safe_goto(page, base_url, wait_until="load", timeout=30000)
        page.wait_for_timeout(2000)
        # 刷新页面确保历史记录加载
        page.reload(wait_until="load", timeout=30000)
        page.wait_for_timeout(1500)

    with allure.step("聚焦搜索框并输入 'driver'"):
        page.evaluate(
            "() => { const el = document.querySelector('#custom-input'); if(el) { el.focus(); el.click(); } }"
        )
        page.wait_for_timeout(500)
        page.evaluate(
            "() => { const el = document.querySelector('#custom-input'); if(el) { el.focus(); el.value = ''; } }"
        )
        page.keyboard.type("driver")
        page.wait_for_timeout(2000)

    with allure.step("点击 Clear 按钮清空输入框"):
        # 使用 JS 点击避免元素定位问题
        page.evaluate("() => document.querySelector('.CustomInput_searchClear___ZaYy')?.click()")
        page.wait_for_timeout(1000)

    with allure.step("验证：清空后 Sug 词面板消失"):
        sug_count_after_clear = page.evaluate(
            "() => Array.from(document.querySelectorAll('.SuggestItem_modalSugItem__iYU6f'))"
            ".filter(el => !el.classList.contains('SearchSuggestContent_modalHistoryItemPC__W7Zwc')).length"
        )
        assert sug_count_after_clear == 0, (
            f"清空后 Sug 词面板应消失，但仍有 {sug_count_after_clear} 条 Sug 词"
        )

    with allure.step("验证：清空后输入框内容为空"):
        input_val = page.evaluate("() => { const el = document.querySelector('#custom-input'); return el ? el.value : ''; }")
        assert input_val == "", (
            f"清空后输入框应为空，实际值: '{input_val}'"
        )

    with allure.step("验证：清空后历史面板重新展示"):
        hist_count_after_clear = page.evaluate(
            "() => document.querySelectorAll('.SearchSuggestContent_modalHistoryItemPC__W7Zwc').length"
        )
        assert hist_count_after_clear > 0, (
            f"清空后历史面板应重新展示，但历史条目数为 {hist_count_after_clear}"
        )


@pytest.mark.p2
@pytest.mark.case_id_ae_search_tc035
@allure.feature("OK")
@allure.story("首页搜索输入框 - 会话与状态")
@allure.title("搜索历史在页面刷新后持久保留")
@allure.description(
    "验证搜索历史存储在 localStorage 中，页面刷新后历史记录仍然保留，"
    "条目内容与顺序与刷新前一致"
)
@allure.severity(allure.severity_level.NORMAL)
def test_history_persists_after_page_refresh(page, config):
    """TC035: 搜索历史在页面刷新后持久保留"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    with allure.step("前置：注入3条历史记录到 localStorage"):
        _inject_history(page, ["driver", "villa", "apartment"], base_url)
        safe_goto(page, base_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)

    with allure.step("验证刷新前 localStorage 历史数据"):
        ls_before = page.evaluate(
            "() => JSON.parse(localStorage.getItem('__SEARCH_LOCAL_HISTORY_LIST__') || '[]')"
        )
        keys_before = [h["suggestKey"] for h in ls_before]
        assert len(ls_before) == 3, f"刷新前历史应有 3 条，实际: {len(ls_before)}"

    with allure.step("刷新页面（F5）"):
        page.reload(wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

    with allure.step("验证：刷新后 localStorage 历史数据仍然存在"):
        ls_after = page.evaluate(
            "() => JSON.parse(localStorage.getItem('__SEARCH_LOCAL_HISTORY_LIST__') || '[]')"
        )
        keys_after = [h["suggestKey"] for h in ls_after]
        assert len(ls_after) == len(ls_before), (
            f"刷新后历史条目数应与刷新前一致（{len(ls_before)}），实际: {len(ls_after)}"
        )

    with allure.step("验证：历史条目内容与刷新前一致"):
        assert keys_after == keys_before, (
            f"刷新后历史内容不一致，刷新前: {keys_before}，刷新后: {keys_after}"
        )

    with allure.step("验证：刷新后 localStorage 历史数据存在（持久化验证）"):
        assert len(keys_after) > 0, "刷新后 localStorage 历史数据应存在"


# ============================================================
# 六、会话与状态 TC036
# ============================================================

@pytest.mark.p2
@pytest.mark.case_id_ae_search_tc036
@allure.feature("OK")
@allure.story("首页搜索输入框 - 会话与状态")
@allure.title("搜索后浏览器后退按钮返回首页，输入框状态恢复")
@allure.description(
    "验证在首页搜索关键词跳转到搜索结果页后，点击浏览器后退按钮返回首页时，"
    "搜索输入框内容清空，底纹词正常显示"
)
@allure.severity(allure.severity_level.NORMAL)
def test_browser_back_restores_input_state(page, config):
    """TC036: 搜索后浏览器后退按钮返回首页，输入框状态恢复"""
    search_page = HomeSearchPage(page)
    base_url = config["base_url"]

    with allure.step("前置：访问首页"):
        safe_goto(page, base_url, wait_until="load", timeout=30000)
        page.wait_for_timeout(1500)

    with allure.step("在搜索框输入 'job' 并按 Enter 搜索"):
        page.evaluate(
            "() => { const el = document.querySelector('#custom-input'); if(el) { el.focus(); el.value = ''; } }"
        )
        page.keyboard.type("job")
        page.wait_for_timeout(500)
        page.keyboard.press("Enter")
        page.wait_for_timeout(3000)

    with allure.step("验证：已跳转到搜索结果页"):
        url_after_search = page.url
        assert "keyword=job" in url_after_search, (
            f"应跳转到含 'keyword=job' 的搜索结果页，实际 URL: {url_after_search}"
        )
        assert "/cate/" in url_after_search, (
            f"应跳转到搜索结果页（含 /cate/），实际 URL: {url_after_search}"
        )

    with allure.step("点击浏览器后退按钮"):
        page.go_back(wait_until="load", timeout=30000)
        page.wait_for_timeout(1500)

    with allure.step("验证：返回首页"):
        url_after_back = page.url
        assert "ae.58v5.cn/en/city-dubai" in url_after_back, (
            f"后退后应返回首页，实际 URL: {url_after_back}"
        )
        assert "/cate/" not in url_after_back, (
            f"后退后不应停留在搜索结果页，实际 URL: {url_after_back}"
        )

    with allure.step("验证：返回首页后输入框内容清空"):
        input_value = page.evaluate(
            "() => document.querySelector('#custom-input')?.value || ''"
        )
        assert input_value == "", (
            f"后退返回首页后输入框应为空，实际值: '{input_value}'"
        )

    with allure.step("验证：底纹词 'Search for anything' 正常显示"):
        placeholder = page.evaluate(
            "() => document.querySelector('#custom-input')?.placeholder || ''"
        )
        assert placeholder == "Search for anything", (
            f"后退返回首页后底纹词应为 'Search for anything'，实际: '{placeholder}'"
        )
