# pages/news_page.py
"""
News 模块页面对象
选择器基于 NEWS_MODULE_选择器规范.md 分析结果
"""
from pages.base_page import BasePage
from utils.logger import setup_logger


class NewsPage(BasePage):
    """News 模块页面对象"""

    # ========== 1. Logo ==========
    LOGO = 'img[alt="ok.com"]'
    LOGO_LINK = 'a:has(img[alt="ok.com"])'
    LOGO_FALLBACK = '[class*="leftLogoWrapper"] img'

    # ========== 2. Browse 菜单 ==========
    BROWSE = "text=Browse"
    BROWSE_FALLBACK = '[class*="SecondLinkageDropdown"]:has-text("Browse")'

    # ========== 3. Log in / Register ==========
    LOGIN_REGISTER = "text=Log in / Register"
    LOGIN_REGISTER_FALLBACK = '[class*="loginButtonText"]'

    # ========== 4. 分类卡片 ==========
    CATEGORY_NEWS = 'a[href="https://us.58v5.cn/ask_news/"]'
    CATEGORY_JOBS = 'a[href*="ask_news_jobs"]'
    CATEGORY_PROPERTY = 'a[href*="ask_news_property"]'
    CATEGORY_CARS = 'a[href*="ask_news_cars"]'
    CATEGORY_SERVICES = 'a[href*="ask_news_services"]'
    CATEGORY_FALLBACK = '.HeaderTop_databaseItem__Qn9yL'

    # ========== 5. 新闻列表项 ==========
    NEWS_ITEM = "a.Content_item__UasVA"
    NEWS_ITEM_FALLBACK = 'a[href*="/ask_news/"][href*="-"]'

    # ========== 6. 分页 ==========
    PAGINATION = "ul.pagination, [class*='pagination']"
    PAGINATION_PREV = "ul.pagination li.prev a, [class*='pagination'] li.prev a"
    PAGINATION_NEXT = "ul.pagination li.next a, [class*='pagination'] li.next a"

    @staticmethod
    def pagination_page(n: int) -> str:
        """页码选择器，使用 text-is 精确匹配避免误匹配"""
        return f"ul.pagination a.page-link:text-is('{n}'), [class*='pagination'] a.page-link:text-is('{n}')"

    # ========== 7. 面包屑 ==========
    BREADCRUMB = 'nav[class*="breadcrumb"]'
    BREADCRUMB_HOME = "nav a:has-text('Home')"
    BREADCRUMB_NEWS = "nav a:has-text('News')"
    BREADCRUMB_FALLBACK = "a.Breadcrumb_breadcrumbLink__2ocVq"

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    def navigate_to_news(self, url: str = "https://us.58v5.cn/ask_news/"):
        """导航到 News 列表页"""
        self.goto(url, timeout=60000)
        self.wait_for_page_load(state="load", timeout=15000)

    def get_logo(self):
        """获取 Logo 元素（用于可见性断言）"""
        return self.page.locator(self.LOGO).first

    def get_logo_link(self):
        """获取 Logo 链接（用于点击跳转首页），若不存在则返回 Logo 父级"""
        link = self.page.locator(self.LOGO_LINK).first
        if link.count() > 0:
            return link
        return self.page.locator(self.LOGO).first

    def get_browse_button(self):
        """获取 Browse 按钮"""
        return self.page.get_by_text("Browse").first

    def get_category(self, name: str):
        """获取分类卡片，name: News, Jobs, Property, Cars, Services"""
        return self.page.locator(f'a[href*="ask_news"]:has-text("{name}")').first

    def get_first_news_item(self):
        """获取第一条新闻（排除分类链接）"""
        return self.page.locator(self.NEWS_ITEM).first

    def get_pagination_next(self):
        """获取 Next 按钮"""
        return self.page.locator(self.PAGINATION_NEXT).first

    def get_pagination_prev(self):
        """获取 Prev 按钮"""
        return self.page.locator(self.PAGINATION_PREV).first

    def get_pagination_page(self, n: int):
        """获取指定页码链接"""
        return self.page.locator(self.pagination_page(n)).first

    def get_breadcrumb_home(self):
        """获取面包屑 Home 链接"""
        return self.page.locator(self.BREADCRUMB_HOME).first
