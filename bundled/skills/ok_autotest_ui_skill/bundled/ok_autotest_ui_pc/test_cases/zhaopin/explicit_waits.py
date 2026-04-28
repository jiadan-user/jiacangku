# -*- coding: utf-8 -*-
"""
Zhaopin 招聘用例显式等待：用 locator / load_state / URL 条件替代 page.wait_for_timeout 固定睡眠。
"""
from __future__ import annotations

import re

from playwright.sync_api import Page

__all__ = [
    "network_idle_soft",
    "dom_content_loaded_soft",
    "es_location_panel_open",
    "es_job_type_panel_open",
    "es_workplace_panel_open",
    "es_salary_panel_open",
    "es_job_list_first_card_ready",
    "ae_location_panel_open",
    "ae_job_type_panel_open",
    "ae_workplace_panel_open",
    "ae_salary_panel_open",
    "ae_job_list_first_card_ready",
    "ae_filter_area_ready",
    "es_filter_area_ready",
    "sg_wait_jobs_list_url",
    "wait_for_url_substrings",
    "sg_after_home_jobs_icon",
]


def network_idle_soft(page: Page, timeout: int = 10000) -> None:
    try:
        page.wait_for_load_state("networkidle", timeout=timeout)
    except Exception:
        try:
            page.wait_for_load_state("domcontentloaded", timeout=min(8000, max(3000, timeout // 2)))
        except Exception:
            pass


def dom_content_loaded_soft(page: Page, timeout: int = 20000) -> None:
    try:
        page.wait_for_load_state("domcontentloaded", timeout=timeout)
    except Exception:
        pass


def es_location_panel_open(page: Page, timeout: int = 15000) -> None:
    page.get_by_placeholder("Search City").first.wait_for(
        state="visible", timeout=timeout
    )


def es_job_type_panel_open(page: Page, timeout: int = 12000) -> None:
    page.get_by_role("button", name="Confirm").first.wait_for(state="visible", timeout=timeout)


def es_workplace_panel_open(page: Page, timeout: int = 12000) -> None:
    page.get_by_role("button", name="Confirm").first.wait_for(state="visible", timeout=timeout)


def es_salary_panel_open(page: Page, timeout: int = 12000) -> None:
    try:
        page.get_by_role("textbox", name="Min").first.wait_for(
            state="visible", timeout=timeout
        )
    except Exception:
        page.get_by_placeholder("Min").first.wait_for(state="visible", timeout=timeout)


def es_job_list_first_card_ready(page: Page, timeout: int = 25000) -> None:
    """等待 ES Jobs 列表首条职位卡片可见（兼容 list-components 卡片与旧 JobListItem）。"""
    card = (
        page.locator('[class*="list-components-item-job-card"]').first.or_(
            page.locator(
                '[class*="list-components-item-job-card"] a[href*="/city-"], '
                '[class*="list-components-item-job-card"] a[href*="/city/"]'
            ).first
        )
        .or_(page.locator('.JobListItem_jobListItem__').first)
        .or_(page.locator('[class*="JobListItem"] a[href*="/city-"]').first)
        .or_(page.locator('[class*="JobListItem"] a[href*="/city/"]').first)
        .or_(page.locator("div[class*='JobListItem']").first)
    )
    card.wait_for(state="visible", timeout=timeout)



def ae_filter_area_ready(page: Page, timeout: int = 30000) -> None:
    page.locator("#istPageFilterArea").first.wait_for(state="visible", timeout=timeout)


def ae_location_panel_open(page: Page, timeout: int = 15000) -> None:
    try:
        page.get_by_role("textbox", name="Search City").first.wait_for(
            state="visible", timeout=timeout
        )
    except Exception:
        page.get_by_placeholder("Search City").first.wait_for(
            state="visible", timeout=timeout
        )


def ae_job_type_panel_open(page: Page, timeout: int = 12000) -> None:
    page.get_by_role("button", name="Confirm").first.wait_for(
        state="visible", timeout=timeout
    )


def ae_workplace_panel_open(page: Page, timeout: int = 12000) -> None:
    page.get_by_role("button", name="Confirm").first.wait_for(
        state="visible", timeout=timeout
    )


def ae_salary_panel_open(page: Page, timeout: int = 12000) -> None:
    try:
        page.get_by_role("textbox", name="Min").first.wait_for(
            state="visible", timeout=timeout
        )
    except Exception:
        page.get_by_placeholder("Min").first.wait_for(state="visible", timeout=timeout)


def ae_job_list_first_card_ready(page: Page, timeout: int = 25000) -> None:
    try:
        page.locator('.JobListItem_jobListItem__').first.wait_for(
            state="visible", timeout=timeout
        )
    except Exception:
        page.locator("div[class*='JobListItem']").first.wait_for(
            state="visible", timeout=timeout
        )


def es_filter_area_ready(page: Page, timeout: int = 20000) -> None:
    page.locator(".listPage-filterArea").first.wait_for(state="visible", timeout=timeout)


def sg_wait_jobs_list_url(page: Page, timeout: int = 30000) -> None:
    """进入 SG 带 iconSource=jobs 的职位列表页（Continue / Skip 等后）。"""
    page.wait_for_url("**/cate-jobs**", timeout=timeout)
    try:
        page.wait_for_function(
            "() => location.href.includes('iconSource=jobs')", timeout=15000
        )
    except Exception:
        pass
    dom_content_loaded_soft(page, timeout=min(15000, timeout))
    try:
        page.locator(".listPage-filterArea, #istPageFilterArea, .listPageJobSection, .listPage-job").first.wait_for(
            state="visible", timeout=min(20000, timeout)
        )
    except Exception:
        pass


def wait_for_url_substrings(
    page: Page, a: str, b: str, timeout: int = 30000
) -> None:
    page.wait_for_function(
        f"""() => {{ const u = location.href; return u.includes({a!r}) && u.includes({b!r}); }}""",
        timeout=timeout,
    )


def sg_after_home_jobs_icon(page: Page, timeout: int = 25000) -> None:
    """首页点击 Jobs 金刚位后，等待进入 jobPreference 或带 iconSource 的职位列表。"""
    page.wait_for_function(
        """() => {
            const u = location.href;
            return u.includes("jobPreference") || (u.includes("cate-jobs") && u.includes("iconSource=jobs"));
        }""",
        timeout=timeout,
    )
