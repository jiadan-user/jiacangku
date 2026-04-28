# -*- coding: utf-8 -*-
"""
Marketplace Post 测试用显式等待：locator / load_state / expect 替代 page.wait_for_timeout 固定睡眠。
"""
from __future__ import annotations

import re
from playwright.sync_api import Page

from test_cases.marketplace.explicit_waits import wait_network_quiet, wait_short_ui_tick


def wait_apple_details_ready_for_tc001(page: Page, timeout: int = 25_000) -> None:
    """TC001：Condition + 容量选项出现（替代固定 4s）。"""
    page.get_by_text("Excellent", exact=True).first.wait_for(state="visible", timeout=timeout)
    page.locator("text=/\\d+\\s*(GB|TB)/i").first.wait_for(state="visible", timeout=timeout)


def wait_price_input_ready(page: Page, timeout: int = 10_000) -> None:
    page.locator("#amount").first.wait_for(state="visible", timeout=timeout)


def wait_after_storage_click(page: Page) -> None:
    try:
        page.wait_for_load_state("domcontentloaded", timeout=5_000)
    except Exception:
        pass
    wait_price_input_ready(page, timeout=8_000)


def wait_location_picked_settled(page: Page) -> None:
    try:
        page.wait_for_load_state("domcontentloaded", timeout=5_000)
    except Exception:
        pass
    try:
        page.locator(
            "input[placeholder*='location' i], input[placeholder*='Location' i], input[placeholder*='Search' i]"
        ).first.wait_for(state="visible", timeout=5_000)
    except Exception:
        pass


def wait_upload_size_validation_settled(page: Page) -> None:
    """大文件上传：等错误提示或非 0/9 计数之一出现。"""
    counter_nonzero = page.locator("text=/[1-9]\\d*\\s*\\/\\s*9/")
    err = page.get_by_text("Image size must be under 10MB")
    err.or_(counter_nonzero).first.wait_for(state="visible", timeout=12_000)


def wait_corrupt_upload_settled(page: Page) -> None:
    err = page.get_by_text(
        re.compile(
            r"Failed to upload image|Invalid image file|Upload failed|Image upload failed|size must",
            re.I,
        )
    )
    ok = page.locator("text=/[1-9]\\d*\\s*\\/\\s*9/")
    err.or_(ok).first.wait_for(state="visible", timeout=12_000)


def wait_post_interaction_settled(page: Page, max_idle_ms: int = 1_200) -> None:
    """
    用 domcontentloaded + 有上限的 network 空闲 替代原固定 `wait_for_timeout`。
    max_idle_ms 为原脚本中的「盲等」毫秒，仅用于推导 network 超时上界，不是再睡眠同等时长。
    """
    try:
        page.wait_for_load_state("domcontentloaded", timeout=4_000)
    except Exception:
        pass
    cap = max(1_200, min(4_000, 500 + int(max_idle_ms * 1.1)))
    try:
        wait_network_quiet(page, cap, fallback_dom=True)
    except Exception:
        try:
            page.wait_for_load_state("load", timeout=min(2_000, cap))
        except Exception:
            wait_short_ui_tick(page)


def wait_draft_bottom_saved_state(page: Page, timeout_ms: int = 15_000) -> None:
    """与 expect_save_draft_gray 等价的 DOM 态：底部 Draft saved 或 Save the draft 置灰。"""
    page.wait_for_function(
        r"""() => {
          const t = (s) => (s || '').toLowerCase();
          for (const el of document.querySelectorAll('[role="button"], button, a')) {
            const tx = t((el.textContent || '').trim());
            if (tx.includes('draft') && (tx.includes('saved') && !tx.includes('save the draft'))) {
              if (el.offsetParent) return true;
            }
          }
          for (const el of document.querySelectorAll('button, a, [role="button"]')) {
            const tx = t((el.textContent || '').trim());
            if (tx.includes('save') && tx.includes('draft')) {
              if (el.disabled) return true;
              if ((el.getAttribute('aria-disabled') || '').toLowerCase() === 'true') return true;
              const c = t(el.getAttribute('class') || '');
              if (c.includes('disabled') || c.includes('saved') || c.includes('inactive')) return true;
            }
          }
          return false;
        }""",
        timeout=timeout_ms,
    )
