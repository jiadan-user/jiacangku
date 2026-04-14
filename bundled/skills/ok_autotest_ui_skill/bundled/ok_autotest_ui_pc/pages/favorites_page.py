# pages/favorites_page.py
import re
import time

from pages.base_page import BasePage
from pages.login_page import LoginPage
from utils.session_manager import SessionManager

FAVORITES_LIST_PATH = "/biz/en/list/favorites"


class FavoritesPage(BasePage):
    """OK.com 收藏列表页（/biz/en/list/favorites）"""

    def favorites_full_url(self, base_url: str) -> str:
        base = (base_url or "").rstrip("/")
        return f"{base}{FAVORITES_LIST_PATH}"

    def navigate_to_favorites_list(self, base_url: str, timeout: int = 60000):
        self.goto(
            self.favorites_full_url(base_url),
            timeout=timeout,
            wait_until="domcontentloaded",
        )
        self.page.wait_for_load_state("load", timeout=30000)

    def reset_to_guest(self):
        """清除 cookie 与本地存储，用于访客场景。"""
        self.page.context.clear_cookies()
        self.page.evaluate(
            "() => { try { localStorage.clear(); sessionStorage.clear(); } catch (e) {} }"
        )

    def ensure_email_step_login_modal(self, login_page: LoginPage, timeout: int = 15000):
        """
        收藏页上可能出现自动弹出的登录框；若无则点击顶部 Log in / Register。
        确保处于「邮箱步骤」（Welcome to OK.com）视图。
        """
        email_box = self.page.get_by_role("textbox", name="Email or phone number")
        if email_box.is_visible(timeout=4000):
            return
        welcome = self.page.get_by_text("Welcome to OK.com")
        if welcome.is_visible(timeout=2000):
            return
        login_page.handle_cookie_popup()
        login_page.click_login_register_button()
        email_box.wait_for(state="visible", timeout=timeout)

    def listing_cards_locator(self):
        """收藏帖子卡片链接（与页脚等链接区分：ae 站详情链 + 含图）。"""
        return self.page.locator("a[href*='ae.ok.com'][href*='/cate-']").filter(
            has=self.page.locator("img")
        )

    def wait_for_listing_cards(self, minimum: int = 1, timeout: int = 20000):
        """SPA / 后退后列表异步渲染时等待卡片出现。"""
        deadline = time.monotonic() + timeout / 1000.0
        while time.monotonic() < deadline:
            if self.listing_cards_locator().count() >= minimum:
                return
            self.page.wait_for_timeout(400)
        raise TimeoutError(
            f"收藏列表在 {timeout}ms 内未出现至少 {minimum} 张含图卡片链接"
        )

    def _session_name(self, config: dict) -> str:
        return f"{config['site']}_{config['role']}_{config['user_name']}"

    def ensure_logged_in_favorites(
        self,
        login_page: LoginPage,
        config: dict,
        *,
        reuse_if_list_ready: bool = False,
    ) -> SessionManager:
        """
        加载 Session；无效或未登录则走完整登录并保存 Session。
        优先以「列表卡片已渲染」判定已登录，避免顶栏文案误判导致误 clear。
        reuse_if_list_ready: module 级 page 下上一用例已留在收藏列表且顶栏有效时，勿再 load_session+goto，
        否则叠加重注入 Cookie / SPA 软导航会破坏顶栏菜单（见 batch5 TC021→TC022）。
        """
        sm = SessionManager(
            self.page, config["base_url"], session_name=self._session_name(config)
        )
        if reuse_if_list_ready and FAVORITES_LIST_PATH in (self.page.url or ""):
            login_page.handle_cookie_popup()
            if self.listing_cards_locator().count() >= 1:
                try:
                    self.wait_for_listing_cards(minimum=1, timeout=12000)
                    return sm
                except TimeoutError:
                    pass
        sm.load_session()
        self.navigate_to_favorites_list(config["base_url"])
        login_page.handle_cookie_popup()
        try:
            self.wait_for_listing_cards(minimum=1, timeout=15000)
            return sm
        except TimeoutError:
            pass
        self.reset_to_guest()
        self.navigate_to_favorites_list(config["base_url"])
        login_page.handle_cookie_popup()
        self.ensure_email_step_login_modal(login_page)
        login_page.input_email(config["test_account"]["username"])
        login_page.click_continue_button()
        login_page.input_password(config["test_account"]["password"])
        login_page.click_login_button()
        self.page.get_by_role("dialog").wait_for(state="hidden", timeout=25000)
        sm.save_session()
        return sm

    def favorites_card_locator(self):
        """收藏列表卡片根节点（与推荐位一致 class 时存在）。"""
        return self.page.locator(".list-components-item-favorite")

    def first_favorites_card_favorite_icon_src(self) -> str:
        try:
            return self.page.evaluate(
                """() => {
                  const icons = document.querySelectorAll(
                    '.list-components-item-favorite img.favorite-icon');
                  return icons.length ? icons[0].src : '';
                }"""
            )
        except Exception:
            return ""

    def first_listing_card_link(self):
        """首张帖子卡片（外链至 ae.ok.com 详情）。"""
        return (
            self.page.locator("a[href*='ae.ok.com'][href*='/cate-']")
            .filter(has=self.page.locator("img"))
            .first
        )

    def listing_card_link_by_text(self, substring: str):
        """包含指定文案的收藏列表主链接（优先无障碍名称，避免 has(img) 误排 DOM）。"""
        by_role = self.page.get_by_role(
            "link", name=re.compile(re.escape(substring), re.I)
        )
        if by_role.count() > 0:
            return by_role.first
        return self.page.locator("a[href*='ae.ok.com'][href*='/cate-']").filter(
            has_text=re.compile(re.escape(substring), re.I)
        ).first

    def listing_post_links_loose(self):
        """列表帖子链（不强制 a 内含 img，用于计数/补位断言）。"""
        return self.page.locator("a[href*='ae.ok.com'][href*='/cate-']")

    def favorites_grid_post_links(self):
        """收藏网格内帖子卡链接（排除页脚等同域链）。"""
        by_class = self.page.locator(
            "a[class*='list-components-item-card'][href*='ae.ok.com']"
        )
        if by_class.count() > 0:
            return by_class
        return self.listing_cards_locator()

    def card_container_by_text(self, substring: str):
        """包含指定文案的卡片容器（优先 list-components-item-favorite，否则回退到链接祖先）。"""
        inner = self.page.locator(".list-components-item-favorite").filter(
            has_text=re.compile(re.escape(substring), re.I)
        )
        if inner.count() > 0:
            return inner.first
        return self.listing_card_link_by_text(substring)

    def click_favorite_icon_unfavorite_card_containing(self, substring: str) -> bool:
        """点击含 substring 的列表卡片上的心形（取消收藏）。自卡片链接向上查找 favorite-icon。"""
        return self.page.evaluate(
            """(t) => {
              const links = [...document.querySelectorAll(
                'a[href*="ae.ok.com"][href*="/cate-"]')];
              const a = links.find(x => x.innerText && x.innerText.includes(t));
              if (!a) return false;
              let el = a;
              for (let i = 0; i < 12 && el; i++) {
                const icon = el.querySelector('img.favorite-icon');
                if (icon) { icon.click(); return true; }
                el = el.parentElement;
              }
              return false;
            }""",
            substring,
        )

    def scroll_to_pagination(self):
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.wait_for_timeout(600)

    def _pager_control(self, label: str):
        return self.page.get_by_text(label, exact=True).last

    def pager_prev_is_disabled(self) -> bool:
        prev_all = self.page.get_by_text("Prev", exact=True)
        if prev_all.count() == 0:
            return True
        loc = prev_all.last
        return bool(
            loc.evaluate(
                """el => {
                  const li = el.closest('li');
                  const lc = (li && li.className) || '';
                  return lc.includes('disabled')
                    || el.getAttribute('aria-disabled') === 'true'
                    || el.hasAttribute('disabled');
                }"""
            )
        )

    def pager_next_is_disabled(self) -> bool:
        next_all = self.page.get_by_text("Next", exact=True)
        if next_all.count() == 0:
            return True
        loc = next_all.last
        return bool(
            loc.evaluate(
                """el => {
                  const li = el.closest('li');
                  const lc = (li && li.className) || '';
                  return lc.includes('disabled')
                    || el.getAttribute('aria-disabled') === 'true'
                    || el.hasAttribute('disabled');
                }"""
            )
        )

    def click_pager_next(self):
        self._pager_control("Next").click()
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(800)

    def click_pager_prev(self):
        self._pager_control("Prev").click()
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(800)

    def click_pager_page_number(self, num: str) -> bool:
        """点击分页器上的页码（与 Prev/Next 同一块 ul/nav 内），exact 匹配文案。"""
        self.scroll_to_pagination()
        want = str(num)
        clicked = self.page.evaluate(
            """(n) => {
              const want = String(n);
              for (const lab of ['Next', 'Prev']) {
                const nodes = [...document.querySelectorAll('a, button, span')].filter(
                  el => (el.textContent || '').trim() === lab);
                const el = nodes.length ? nodes[nodes.length - 1] : null;
                if (!el) continue;
                const root = el.closest('ul') || el.closest('nav') || el.parentElement;
                if (!root) continue;
                for (const c of root.querySelectorAll('a, button')) {
                  if ((c.textContent || '').trim() !== want) continue;
                  c.click();
                  return true;
                }
              }
              return false;
            }""",
            want,
        )
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(800)
        return bool(clicked)

    def current_page_number_highlighted(self, num: str) -> bool:
        """页码 num 是否为当前页（常见 active/current/aria-current）。"""
        return bool(
            self.page.evaluate(
                """(n) => {
                  const nodes = document.querySelectorAll(
                    '[aria-current="page"], .active, .current, [class*="active"]');
                  for (const el of nodes) {
                    const t = (el.textContent || '').trim();
                    if (t === n) return true;
                  }
                  const all = document.querySelectorAll('a, button, span');
                  for (const el of all) {
                    if ((el.textContent || '').trim() !== n) continue;
                    const cls = (el.className && String(el.className)) || '';
                    if (cls.includes('active') || cls.includes('current') ||
                        cls.includes('selected')) return true;
                  }
                  return false;
                }""",
                num,
            )
        )

    def _user_menu_trigger_scope(self):
        if self.page.locator("header").count() > 0:
            return self.page.locator("header").first
        return self.page.locator("[class*='Header'], [class*='UserInfo']").first

    def open_user_menu(self, config: dict = None, display_name: str = None):
        """点击顶栏展示名展开用户菜单（AE 站 OKerAE_* 或配置 expected_username_display）。"""
        name = display_name or (config or {}).get("expected_username_display") or ""

        def _click_header_user_chip() -> bool:
            return self.page.evaluate(
                """(exactName) => {
                  const want = (exactName || '').trim();
                  const roots = [];
                  for (const sel of ['header', '[class*="Header"]', '[class*="TopBar"]']) {
                    const r = document.querySelector(sel);
                    if (r && !roots.includes(r)) roots.push(r);
                  }
                  if (!roots.length) roots.push(document.body);
                  let best = null;
                  for (const root of roots) {
                    for (const el of root.querySelectorAll('a, button, div, span')) {
                      const t = (el.textContent || '').trim();
                      if (!t || !el.offsetParent) continue;
                      if (want) {
                        if (!(t === want || t.includes(want))) continue;
                      } else if (!/OKerAE_\\w+/.test(t)) continue;
                      if (t.length > 120) continue;
                      if (!best || t.length < best.t.length) best = { el, t };
                    }
                  }
                  if (!best) return false;
                  const el = best.el;
                  const host = el.closest(
                    'button, a, [role="button"], [class*="UserInfo"], [class*="user-info"]'
                  ) || el;
                  host.click();
                  return true;
                }""",
                name,
            )

        def _logout_in_open_menu():
            """菜单内 Log Out：避免全页 get_by_text().last 点到隐藏副本永不 visible。"""
            mi = self.page.get_by_role("menuitem", name=re.compile(r"log\s*out", re.I))
            if mi.count():
                return mi.first
            for sel in ('[role="menu"]', '[role="listbox"]'):
                panel = self.page.locator(sel).filter(has_text=re.compile(r"Log\s*Out", re.I))
                if panel.count() and panel.first.is_visible(timeout=500):
                    return panel.first.get_by_text(re.compile(r"Log\s*Out", re.I)).first
            return self.page.get_by_text(re.compile(r"Log\s*Out", re.I)).first

        # module 级 page 复用时，上一用例展开过菜单后首击可能成「收起」；Escape + 最多 3 次展开
        for attempt in range(3):
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(450)
            if name:
                self.page.get_by_text(re.compile(re.escape(name))).last.wait_for(
                    state="visible", timeout=20000
                )
            else:
                self.page.get_by_text(re.compile(r"OKerAE_\w+")).last.wait_for(
                    state="visible", timeout=20000
                )

            assert _click_header_user_chip(), "应在顶栏内找到可点的用户名展示节点"
            self.page.wait_for_timeout(900)
            lo = _logout_in_open_menu()
            if lo.is_visible(timeout=2200):
                lo.wait_for(state="visible", timeout=10000)
                return
            try:
                self.page.locator("[class*='PcUserInfo'], [class*='UserInfo']").first.click(
                    timeout=6000, force=True
                )
                self.page.wait_for_timeout(700)
            except Exception:
                pass
            lo = _logout_in_open_menu()
            if lo.is_visible(timeout=2200):
                lo.wait_for(state="visible", timeout=10000)
                return

        lo = _logout_in_open_menu()
        lo.wait_for(state="visible", timeout=8000)

    def click_log_out_in_user_menu(self):
        out = self.page.get_by_role("menuitem", name=re.compile(r"log\s*out", re.I))
        if out.count() == 0:
            out = self.page.get_by_text(re.compile(r"Log\s*Out", re.I)).first
        else:
            out = out.first
        out.wait_for(state="visible", timeout=10000)
        out.click()
        self.page.wait_for_load_state("load", timeout=30000)
        self.page.wait_for_timeout(1500)

    def user_menu_option_visible(self, label: str) -> bool:
        loc = self.page.get_by_text(label, exact=True)
        return loc.last.is_visible(timeout=3000)
