# pages/browse_navigation_page.py
from pages.base_page import BasePage
from utils.logger import setup_logger


class BrowseNavigationPage(BasePage):
    """Browse 导航区域页面对象"""
    
    # ========== 页面元素选择器 ==========
    BROWSE_BUTTON = "text=Browse"
    
    # 一级分类链接（下拉菜单中）
    JOBS_LINK = "link[name='Jobs'][exact]"
    PROPERTY_LINK = "link[name='Property'][exact]"
    CARS_LINK = "link[name='Cars'][exact]"
    SERVICES_LINK = "link[name='Services'][exact]"
    COMMUNITY_LINK = "link[name='Community'][exact]"
    
    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()
    
    # ========== 页面操作方法 ==========
    
    def navigate_to_home_page(self, base_url):
        """导航到首页"""
        try:
            self.goto(base_url, timeout=30000)
            self.wait_for_page_load("domcontentloaded")
        except Exception as e:
            self.logger.error(f"导航到首页失败: {e}")
            raise
    
    def click_browse_button(self):
        """点击 Browse 按钮展开下拉菜单"""
        try:
            self.page.get_by_text("Browse").click()
        except Exception as e:
            self.logger.error(f"点击 Browse 按钮失败: {e}")
            raise
    
    def click_jobs_category(self):
        """点击 Jobs 分类链接"""
        try:
            self.page.get_by_role("link", name="Jobs", exact=True).click()
        except Exception as e:
            self.logger.error(f"点击 Jobs 分类失败: {e}")
            raise
    
    def click_property_category(self):
        """点击 Property 分类链接"""
        try:
            self.page.get_by_role("link", name="Property", exact=True).click()
        except Exception as e:
            self.logger.error(f"点击 Property 分类失败: {e}")
            raise
    
    def click_cars_category(self):
        """点击 Cars 分类链接"""
        try:
            self.page.get_by_role("link", name="Cars", exact=True).click()
        except Exception as e:
            self.logger.error(f"点击 Cars 分类失败: {e}")
            raise
    
    def click_services_category(self):
        """点击 Services 分类链接"""
        try:
            self.page.get_by_role("link", name="Services", exact=True).click()
        except Exception as e:
            self.logger.error(f"点击 Services 分类失败: {e}")
            raise
    
    def is_browse_menu_expanded(self):
        """
        验证 Browse 下拉菜单是否展开
        通过检测一级分类链接是否可见
        """
        try:
            # 检测下拉菜单中的 Marketplace 链接是否可见（更准确）
            # 下拉菜单展开后，会出现 exact 匹配的一级分类链接
            marketplace_link = self.page.get_by_role("link", name="Marketplace", exact=True)
            return marketplace_link.is_visible(timeout=2000)
        except Exception:
            return False
    
    def get_current_url(self):
        """获取当前页面 URL"""
        try:
            return self.page.url
        except Exception as e:
            self.logger.error(f"获取当前 URL 失败: {e}")
            raise
    
    def get_page_title(self):
        """获取当前页面标题"""
        try:
            return self.page.title()
        except Exception as e:
            self.logger.error(f"获取页面标题失败: {e}")
            raise
    
    def click_marketplace_category(self):
        """点击 Marketplace 分类链接"""
        try:
            self.page.get_by_role("link", name="Marketplace", exact=True).click()
        except Exception as e:
            self.logger.error(f"点击 Marketplace 分类失败: {e}")
            raise
    
    def click_secondary_category_collectibles_art(self):
        """点击二级分类：Collectibles & Art"""
        try:
            self.page.get_by_role("link", name="Collectibles & Art").click()
        except Exception as e:
            self.logger.error(f"点击 Collectibles & Art 分类失败: {e}")
            raise
    
    def click_secondary_category_clothing_shoes(self):
        """点击二级分类：Clothing & Shoes"""
        try:
            # 使用 force 选项避免被其他元素拦截
            self.page.get_by_role("link", name="Clothing & Shoes").click(force=True)
        except Exception as e:
            self.logger.error(f"点击 Clothing & Shoes 分类失败: {e}")
            raise
    
    def click_outside_menu(self):
        """点击 Browse 菜单外部区域，使菜单收起"""
        try:
            # 点击页面的 logo 区域（菜单外部），更可靠
            # 或者直接点击页面主体区域
            self.page.locator("body").click(position={"x": 10, "y": 10})
        except Exception as e:
            self.logger.error(f"点击菜单外部区域失败: {e}")
            raise
    
    def hover_on_browse_button(self):
        """悬停在 Browse 按钮上"""
        try:
            self.page.get_by_text("Browse").hover()
        except Exception as e:
            self.logger.error(f"悬停 Browse 按钮失败: {e}")
            raise
    
    def hover_on_jobs_category(self):
        """悬停在 Jobs 分类上"""
        try:
            self.page.get_by_role("link", name="Jobs", exact=True).hover()
        except Exception as e:
            self.logger.error(f"悬停 Jobs 分类失败: {e}")
            raise
    
    def hover_on_accounting_subcategory(self):
        """悬停在 Accounting 子分类上"""
        try:
            # 需要在 Jobs 的子分类中找到 Accounting
            self.page.locator("text=Accounting").first.hover()
        except Exception as e:
            self.logger.error(f"悬停 Accounting 子分类失败: {e}")
            raise
    
    def click_accounts_payable_link(self):
        """点击 Accounts Payable 链接"""
        try:
            self.page.get_by_role("link", name="Accounts Payable").click()
        except Exception as e:
            self.logger.error(f"点击 Accounts Payable 链接失败: {e}")
            raise
    
    def get_breadcrumb_text(self):
        """
        获取面包屑导航文本
        例如：Home > Jobs
        """
        try:
            breadcrumb = self.page.locator("nav").first
            return breadcrumb.inner_text() if breadcrumb.is_visible() else ""
        except Exception:
            return ""
