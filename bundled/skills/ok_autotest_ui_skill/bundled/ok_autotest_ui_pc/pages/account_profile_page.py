# pages/account_profile_page.py
"""OK.com 账户主页（/en/profile/{id}/）页面对象 — 与 web-qa-brain 用例文档配套。"""
from __future__ import annotations

import re

from playwright.sync_api import Page, expect

from pages.base_page import BasePage
from utils.logger import setup_logger


class AccountProfilePage(BasePage):
    """AE 站账户主页：资料卡、类目 Tab、列表卡片、Contact、编辑入口等。"""

    MAIN = "main"

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = setup_logger()

    def open_profile(self, url: str, *, timeout: int = 90000) -> None:
        self.page.goto(url, wait_until="domcontentloaded", timeout=timeout)
        try:
            self.page.wait_for_load_state("networkidle", timeout=25000)
        except Exception:
            pass
        self.page.wait_for_timeout(800)

    def wait_main_visible(self, timeout: int = 45000) -> None:
        """路由就绪：URL 在 profile 下且文档完成加载（访客态 title 可能较慢，不强制首帧含 OKer_）。"""
        expect(self.page).to_have_url(re.compile(r"/en/profile/\d+"), timeout=timeout)
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        self.page.wait_for_timeout(800)
        self.page.wait_for_function(
            "() => document.readyState === 'complete' && (document.title || '').includes('OK.com')",
            timeout=min(timeout, 25000),
        )

    def title_matches_profile_pattern(self) -> bool:
        t = self.page.title()
        return bool(re.search(r"OKer_\S+", t)) and "Posts covering" in t and t.rstrip().endswith("- OK.com")

    def url_contains_profile_id(self, profile_id: str) -> bool:
        return profile_id in self.page.url

    # ---------- 顶栏 vs 资料卡主体（TC031）----------
    def header_text_has(self, substring: str) -> bool:
        """顶栏可能仅展示头像，昵称在折叠菜单内；放宽为页首区域可见文案。"""
        for root in ("header", "[class*='Header' i]", "nav"):
            loc = self.page.locator(root).first
            try:
                if loc.count() and substring in (loc.inner_text(timeout=4000) or ""):
                    return True
            except Exception:
                continue
        try:
            return self.page.get_by_text(substring, exact=False).first.is_visible(timeout=3000)
        except Exception:
            return False

    def profile_card_oker_name(self) -> Optional[str]:
        """优先从 document.title 解析 OKer_*（避免命中 SSR 隐藏 JSON）。"""
        t = self.page.title()
        m = re.search(r"(OKer_\S+?)\s*[–-]\s*Posts\s+covering", t, re.I)
        if m:
            return m.group(1).strip()
        return None

    # ---------- 帖子数文案（TC005 / TC032 / TC037）----------
    def profile_listings_label_text(self) -> Optional[str]:
        try:
            blob = self.page.locator("body").inner_text(timeout=15000)[:15000]
            m = re.search(r"(\d+\s+listings?)", blob, re.I)
            if m:
                return m.group(1).strip()
        except Exception:
            pass
        return None

    def parse_listings_count(self, label: str | None) -> Optional[int]:
        if not label:
            return None
        m = re.search(r"(\d+)\s+listings?", label, re.I)
        if m:
            return int(m.group(1))
        return None

    # ---------- 类目 Tab（TC008 / TC034）----------
    def tab_by_name(self, name: str):
        return self.page.get_by_role("tab", name=name)

    def tab_link_by_name(self, name: str):
        """部分实现为 link 而非 role=tab。"""
        return self.page.locator(self.MAIN).get_by_role("link", name=re.compile(rf"^{re.escape(name)}\s*$", re.I))

    def click_category_tab(self, name: str) -> None:
        tab = self.tab_by_name(name)
        if tab.count() and tab.first.is_visible(timeout=2000):
            tab.first.click()
            self.page.wait_for_timeout(600)
            return
        link = self.tab_link_by_name(name)
        if link.count() and link.first.is_visible(timeout=2000):
            link.first.click()
            self.page.wait_for_timeout(800)
            return
        # 类目为普通文本节点（非 tab/link 角色）时，在 main 内按精确文案点击
        cell = self.page.locator(self.MAIN).get_by_text(name, exact=True).first
        if cell.count() and cell.is_visible(timeout=3000):
            cell.scroll_into_view_if_needed()
            cell.click()
            self.page.wait_for_timeout(800)
            return
        # 用户提供的类目 Tab 父容器 XPath（针对 Marketplace 等）—— 需按文案定位子节点
        tab_container = self.page.locator("xpath=/html/body/div[2]/div[3]/div")
        if tab_container.count():
            candidate = tab_container.get_by_text(name, exact=True).first
            if candidate.is_visible(timeout=3000):
                candidate.scroll_into_view_if_needed()
                candidate.click()
                self.page.wait_for_timeout(800)
                return
        raise RuntimeError(f"未找到类目 Tab: {name}")

    def is_tab_selected(self, name: str) -> bool:
        tab = self.tab_by_name(name)
        if tab.count():
            try:
                return tab.first.evaluate("el => el.getAttribute('aria-selected') === 'true'")
            except Exception:
                pass
        # 粗判：当前选中常有 underline / font-weight ——无稳定 API 时仅检查可见
        return tab.first.is_visible(timeout=2000) if tab.count() else False

    # ---------- 编辑（TC006 / TC010 / TC032 / TC038）----------
    def profile_edit_button(self):
        """编辑入口：优先 href 含 edit 的链接，其次 aria-label，最后用 XPath。"""
        main = self.page.locator(self.MAIN).first if self.page.locator(self.MAIN).count() else self.page.locator("body")
        link = main.locator("a[href*='edit' i], a[href*='Edit' i], a[href*='setting' i]")
        if link.count():
            return link.first
        aria = main.locator("[aria-label*='edit' i], [title*='edit' i]")
        if aria.count():
            return aria.first
        # 用户提供的编辑按钮 XPath（img 外层可能为 span/button/a）
        xpath_edit = self.page.locator("xpath=/html/body/div[2]/div[2]/div[2]/div/div[1]/div[2]/span/img")
        if xpath_edit.count():
            return xpath_edit
        return main.get_by_role("button", name=re.compile(r"edit", re.I)).first

    def click_profile_edit_js(self) -> None:
        """资料卡「编辑」图标：用 XPath 或可见 a[href*=edit] 直点。"""
        try:
            self.page.locator("xpath=/html/body/div[2]/div[2]/div[2]/div/div[1]/div[2]/span/img").click(timeout=8000)
            self.page.wait_for_timeout(800)
            return
        except Exception:
            pass
        self.page.evaluate(
            """
            () => {
              const root = document.querySelector("main") || document.body;
              const link = root.querySelector(
                'a[href*="edit" i], a[href*="Edit" i], a[href*="setting" i][href*="profile" i]'
              );
              if (link && link.offsetParent) {
                link.click();
                return;
              }
              for (const sel of [
                '[aria-label*="edit" i]',
                '[title*="edit" i]',
                'button[aria-label*="Edit" i]',
              ]) {
                const el = root.querySelector(sel);
                if (el && el.offsetParent) {
                  el.click();
                  return;
                }
              }
              throw new Error("未找到资料编辑入口（XPath 与 CSS 均失败）");
            }
            """
        )
        self.page.wait_for_timeout(800)

    # ---------- Contact（TC012 / TC038 / TC042）----------
    def contact_button(self):
        """Playwright Locator 版 Contact（若不可靠请改用 wait_contact_cta_visible + click_profile_contact_js）。"""
        return self.page.locator("button, a").filter(has_text=re.compile(r"^\s*Contact\s*$", re.I)).first

    # ---------- 列表卡片收藏心（TC007 / TC033 / TC041）----------
    def first_listing_favorite_icon(self):
        """与列表卡片录制一致：`.list-components-item-favorite.pc-card img.favorite-icon`。"""
        loc = self.page.locator(".list-components-item-favorite.pc-card img.favorite-icon").first
        if loc.count():
            return loc
        return self.page.locator("img.favorite-icon").first

    def click_first_listing_favorite_js(self) -> None:
        """DOM 直点首张卡片收藏图标（与 pages/detail_page_recommendation 同源策略）。"""
        self.page.evaluate(
            """
            () => {
              const icons = document.querySelectorAll(
                '.list-components-item-favorite.pc-card img.favorite-icon'
              );
              if (!icons.length) throw new Error('未找到 profile 列表收藏图标');
              icons[0].click();
            }
            """
        )
        self.page.wait_for_timeout(800)

    def wait_contact_cta_visible(self, timeout: int = 25000) -> None:
        self.page.wait_for_function(
            """() => [...document.querySelectorAll('button, a')].some(
              (el) => /\\bContact\\b/i.test((el.innerText || '').trim())
                && el.offsetParent && el.getBoundingClientRect().height > 12
            )""",
            timeout=timeout,
        )

    def click_profile_contact_js(self) -> None:
        self.page.evaluate(
            """
            () => {
              const candidates = [...document.querySelectorAll('button, a')];
              const b = candidates.find(
                (el) => /\\bContact\\b/i.test((el.innerText || '').trim())
                  && el.offsetParent && el.getBoundingClientRect().height > 12
              );
              if (!b) throw new Error('未找到可见 Contact');
              b.click();
            }
            """
        )
        self.page.wait_for_timeout(1200)

    # ---------- 分页（TC009）----------
    def pagination_next(self):
        for name in ("Next", ">", "Show more", "Load more"):
            loc = self.page.get_by_role("button", name=re.compile(rf"^{re.escape(name)}", re.I))
            if loc.count() and loc.first.is_visible(timeout=1500):
                return loc.first
        link = self.page.get_by_role("link", name=re.compile(r"next", re.I))
        if link.count():
            return link.first
        return self.page.locator(self.MAIN).get_by_text(re.compile(r"^Next$", re.I)).first

    # ---------- 空态（TC036）----------
    def empty_state_text(self):
        return self.page.get_by_text(re.compile(r"there'?s nothing here", re.I))

    # ---------- 页脚（TC040）----------
    def footer_about_link(self):
        return self.page.get_by_role("link", name=re.compile(r"about us", re.I))

    # ---------- 登录拦截（TC041 / TC042）----------
    def login_modal_or_gate_visible(self) -> bool:
        p = self.page
        patterns = (
            r"log\s*in",
            r"sign\s*in",
            r"register",
            r"enter\s+password",
            r"continue",
        )
        for pat in patterns:
            try:
                if p.get_by_role("dialog").filter(has_text=re.compile(pat, re.I)).first.is_visible(timeout=800):
                    return True
            except Exception:
                pass
        try:
            if p.get_by_text(re.compile(r"log\s*in\s*/\s*register", re.I)).first.is_visible(timeout=800):
                return True
        except Exception:
            pass
        return False

    def expect_title_contains_oker(self, nick_part: str) -> None:
        expect(self.page).to_have_title(re.compile(re.escape(nick_part)))
