# -*- coding: utf-8 -*-
"""
Marketplace 测试用显式等待：用 locator / load_state / 条件 替代 page.wait_for_timeout 固定睡眠。
"""
from __future__ import annotations

import re
import time
from typing import TYPE_CHECKING

from playwright.sync_api import Page

if TYPE_CHECKING:
    from pages.marketplace_list_page_ae import MarketplaceListPageAe


def wait_dom_content_loaded(page: Page, timeout: int = 20000) -> None:
    try:
        page.wait_for_load_state("domcontentloaded", timeout=timeout)
    except Exception:
        pass


def wait_network_quiet(
    page: Page, timeout: int = 15000, fallback_dom: bool = True
) -> None:
    try:
        page.wait_for_load_state("networkidle", timeout=timeout)
    except Exception:
        if fallback_dom:
            wait_dom_content_loaded(page, timeout=8000)


def wait_list_results_settled(page: Page, timeout: int = 20000) -> None:
    """
    列表搜索/筛选/翻页后：等待「空态」或「商品卡」任一侧稳定可见（与 is_empty_state_displayed 语义对齐）。
    """
    empty_or_results = (
        page.get_by_text("We couldn't find anything", exact=False)
        .first.or_(page.locator('[class*="list-components-item-card"]').first)
        .or_(page.get_by_text("No results found", exact=True).first)
        .or_(page.locator('[class*="empty"]').first)
    )
    empty_or_results.wait_for(state="visible", timeout=timeout)


def wait_list_or_dom_stability(page: Page, timeout: int = 20000) -> None:
    """
    Marketplace 列表用例中通用「页面稳定」：优先等列表结果/空态；失败则回退到 dom + 网络。
    用于替代固定毫秒 sleep，同时兼容偶发非列表子页。
    """
    try:
        wait_list_results_settled(page, timeout=timeout)
    except Exception:
        wait_dom_content_loaded(page, min(20000, max(8000, timeout)))
        try:
            page.wait_for_load_state("load", timeout=min(12000, max(3000, timeout // 2)))
        except Exception:
            pass
        try:
            wait_network_quiet(page, min(20000, max(5000, int(timeout * 0.6))))
        except Exception:
            pass


def wait_list_interactive(
    list_page: "MarketplaceListPageAe", timeout: int = 45000
) -> None:
    list_page.wait_for_marketplace_list_interactive(timeout=timeout)


def wait_after_goto_marketplace_list(
    page: Page, list_page: "MarketplaceListPageAe", timeout: int = 50000
) -> None:
    wait_dom_content_loaded(page, timeout=20000)
    try:
        page.wait_for_load_state("load", timeout=15000)
    except Exception:
        pass
    wait_list_interactive(list_page, timeout=timeout)
    try:
        wait_network_quiet(page, timeout=12000)
    except Exception:
        pass


def wait_aed_listing_price_signal(page: Page, timeout: int = 20000) -> None:
    """列表出现 AED 价签（与业务展示一致）。"""
    page.locator("text=/AED\\s+\\d+/").first.wait_for(state="visible", timeout=timeout)


def wait_marketplace_detail_price(page: Page, timeout: int = 20000) -> None:
    """详情主价区 AED 数字可见。"""
    page.get_by_text(re.compile(r"AED\s*\d+")).first.wait_for(
        state="visible", timeout=timeout
    )


def wait_marketplace_detail_href_in_dom(
    page: Page, timeout_ms: int = 2000
) -> bool:
    """
    等待「非 cate-marketplace 列表链」的详情 a[href*=\"cate-\"] 出现（与列表首链语义一致）。
    用于 _wait_for_list_first_detail_href 轮询步进，替代 time.sleep(450ms)。
    """
    try:
        page.wait_for_function(
            r"""() => {
                const re = /cate-(?!marketplace)\w/i;
                for (const a of document.querySelectorAll('a[href*="cate-"]')) {
                    if (a.closest && a.closest('#istPageFilterArea')) continue;
                    const h = (a.getAttribute('href') || '');
                    if (h && re.test(h) && h.indexOf('cate-marketplace?') < 0) return true;
                }
                return false;
            }""",
            timeout=timeout_ms,
        )
        return True
    except Exception:
        return False


def wait_short_ui_tick(page: Page) -> None:
    """极短步进：等 domcontentloaded 或一帧，替代 100~500ms 盲等。"""
    try:
        page.wait_for_load_state("domcontentloaded", timeout=300)
    except Exception:
        pass


def wait_publish_context_ready(page: Page, timeout: int = 20000) -> None:
    """进入发布/编辑页后：等待 URL 含 publish 或 dom 就绪（替代固定 sleep）。"""
    try:
        page.wait_for_url("**/publish/**", timeout=min(timeout, 30000))
    except Exception:
        try:
            page.wait_for_url("**/biz/**/publish/**", timeout=5000)
        except Exception:
            wait_dom_content_loaded(page, min(15000, timeout))
