# pages/ok_kingkong_nav_page.py
"""纽约城市页搜索框下方金刚位导航（MCP 录制：link name 为「文案 文案」）"""
import re
import time

from pages.base_page import BasePage
from utils.logger import setup_logger


class OkKingkongNavPage(BasePage):
    """金刚位：Marketplace/For Sale / Free / Jobs / Property / Cars / Services / Community / All"""

    LINK_MARKETPLACE = "Marketplace Marketplace"
    LINK_FOR_SALE = "For Sale For Sale"  # 58v5.cn 使用
    LINK_FREE = "Free Free"
    LINK_JOBS = "Jobs Jobs"
    LINK_PROPERTY = "Property Property"
    LINK_CARS = "Cars Cars"
    LINK_SERVICES = "Services Services"
    LINK_COMMUNITY = "Community Community"
    LINK_ALL = "All All"
    ALL_NAME_PATTERN = re.compile(r"^All(?:\s+All)?$", re.IGNORECASE)

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    def kingkong_link(self, link_name: str):
        """金刚位入口链接（与 MCP 返回的 getByRole('link', { name }) 一致）"""
        return self.page.get_by_role("link", name=link_name)
    
    def kingkong_marketplace_or_for_sale_link(self):
        """
        金刚位 Marketplace/For Sale 链接（兼容58v5.cn和ok.com）
        优先尝试 For Sale (58v5.cn)，兜底 Marketplace (ok.com)
        """
        try:
            for_sale = self.kingkong_link(self.LINK_FOR_SALE)
            if for_sale.count() > 0 and for_sale.is_visible(timeout=2000):
                return for_sale
        except Exception:
            pass
        
        return self.kingkong_link(self.LINK_MARKETPLACE)

    def goto_nyc_home(self, base_url: str):
        """打开纽约城市首页（金刚位所在页）"""
        try:
            self.goto(base_url, timeout=60000, wait_until="domcontentloaded")
            self.page.wait_for_load_state("domcontentloaded", timeout=20000)
        except Exception as e:
            self.logger.error(f"打开纽约首页失败: {e}")
            raise

    def click_kingkong_link(self, link_name: str):
        """
        点击指定金刚位链接（MCP: await page.getByRole('link', { name: '...' }).click()）
        """
        try:
            loc = self.kingkong_link(link_name)
            loc.wait_for(state="visible", timeout=20000)
            loc.click()
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception as e:
            self.logger.error(f"点击金刚位「{link_name}」失败: {e}")
            raise

    def listpage_content_root(self):
        """全部分类页正文根节点（兼容无 main 的页面结构）"""
        main = self.page.locator("main").first
        try:
            if main.count() and main.is_visible(timeout=2000):
                return main
        except Exception:
            pass
        by_role = self.page.get_by_role("main").first
        try:
            if by_role.count() and by_role.is_visible(timeout=2000):
                return by_role
        except Exception:
            pass
        nxt = self.page.locator("#__next").first
        try:
            if nxt.count() and nxt.is_visible(timeout=1500):
                return nxt
        except Exception:
            pass
        return self.page.locator("body").first

    def listpage_link_href_contains(self, href_substring: str):
        """listpage 上按 href 片段定位链接（可能命中隐藏节点，优先用 wait_listpage_href_link_visible）"""
        return self.page.locator(f'a[href*="{href_substring}"]').first

    def wait_listpage_href_link_visible(self, href_substring: str, timeout: int = 20000):
        """在 listpage 上等待第一个可见的 href 匹配链接（跳过顶栏下拉内隐藏副本）"""
        deadline = time.monotonic() + timeout / 1000.0
        base = self.page.locator(f'a[href*="{href_substring}"]')
        while time.monotonic() < deadline:
            try:
                n = base.count()
                for i in range(min(n, 50)):
                    cand = base.nth(i)
                    if cand.is_visible(timeout=500):
                        return cand
            except Exception:
                pass
            self.page.wait_for_timeout(300)
        raise TimeoutError(f"listpage 上未找到可见链接: {href_substring}")

    def click_kingkong_all_expect_navigation(self, timeout_ms: int = 35000):
        """点击 All 并等待 URL 进入 listpage（兼容客户端路由，不用 expect_navigation）"""
        candidates = [
            self.page.get_by_role("link", name=self.LINK_ALL),
            self.page.get_by_role("link", name=self.ALL_NAME_PATTERN),
            self.page.locator("a[href*='/listpage/']").filter(has_text=self.ALL_NAME_PATTERN),
            self.page.locator("a[href*='/listpage/'][href*='city-']"),
            self.page.locator("a[href*='/listpage/']"),
        ]
        last_error = None
        try:
            for loc in candidates:
                try:
                    target = loc.first
                    target.wait_for(state="visible", timeout=20000)
                    target.scroll_into_view_if_needed(timeout=timeout_ms)
                    target.click(timeout=timeout_ms)
                    break
                except Exception as click_error:
                    last_error = click_error
            else:
                raise TimeoutError(f"未找到可点击 All 入口: {last_error}")

            self.page.wait_for_url("**/listpage/**", timeout=timeout_ms)
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception as e:
            self.logger.error(f"点击金刚位 All 并等待 listpage 失败: {e}")
            raise

    def wait_for_visible_text(self, text: str, exact: bool = True, timeout: int = 20000):
        """
        轮询查找页面上第一个可见的文本节点（兼容 DOM 中多个同名隐藏副本）
        """
        deadline = time.monotonic() + timeout / 1000.0
        while time.monotonic() < deadline:
            try:
                locs = self.page.get_by_text(text, exact=exact)
                n = locs.count()
                for i in range(min(n, 30)):
                    cand = locs.nth(i)
                    if cand.is_visible(timeout=500):
                        return cand
            except Exception:
                pass
            self.page.wait_for_timeout(300)
        raise TimeoutError(f"超时未找到可见文本: {text}")

    def get_nav_home_href(self):
        """列表页面包屑区域 Home 链接 href（用于 Jobs 访客/买家差异断言）"""
        try:
            nav = self.page.get_by_role("navigation").first
            return nav.get_by_role("link", name="Home").get_attribute("href")
        except Exception as e:
            self.logger.error(f"读取导航 Home 链接失败: {e}")
            raise

    def get_primary_h1_text(self):
        """页面主 h1 文案（取第一个 heading level=1）"""
        try:
            return self.page.get_by_role("heading", level=1).first.inner_text()
        except Exception as e:
            self.logger.error(f"读取主 h1 失败: {e}")
            raise

    def is_top_search_visible(self):
        """顶栏「Search for anything」搜索框是否可见（Jobs 等列表页）"""
        try:
            return self.page.get_by_role("textbox", name="Search for anything").is_visible(
                timeout=5000
            )
        except Exception:
            return False
