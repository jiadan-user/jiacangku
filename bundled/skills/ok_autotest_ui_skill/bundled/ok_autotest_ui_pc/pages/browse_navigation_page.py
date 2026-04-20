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
            # 检测下拉菜单中的一级分类链接是否可见
            # 使用 Electronics（58v5.cn有）或 Marketplace（ok.com有）或 Jobs（都有）
            # 优先检查 Jobs（两个域名都有）
            jobs_link = self.page.get_by_role("link", name="Jobs", exact=True)
            if jobs_link.count() > 0 and jobs_link.first.is_visible(timeout=2000):
                return True
            
            # 兜底：检查 Electronics（58v5.cn）
            electronics_link = self.page.get_by_role("link", name="Electronics", exact=True)
            if electronics_link.count() > 0 and electronics_link.first.is_visible(timeout=2000):
                return True
                
            # 兜底：检查 Marketplace（ok.com）
            marketplace_link = self.page.get_by_role("link", name="Marketplace", exact=True)
            if marketplace_link.count() > 0 and marketplace_link.first.is_visible(timeout=2000):
                return True
                
            return False
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
        """点击 Marketplace/For Sale 分类链接（ok.com 用 Marketplace，58v5.cn 用 For Sale）"""
        try:
            # 优先尝试 For Sale（58v5.cn，显示名称改了但URL仍是marketplace）
            for_sale = self.page.get_by_role("link", name="For Sale", exact=True)
            if for_sale.count() > 0 and for_sale.is_visible(timeout=1000):
                for_sale.click()
                self.logger.info("✓ 点击 For Sale 分类（58v5.cn）")
                return
        except Exception:
            pass
        
        try:
            # 兜底：尝试 Marketplace（ok.com）
            marketplace = self.page.get_by_role("link", name="Marketplace", exact=True)
            if marketplace.count() > 0 and marketplace.is_visible(timeout=1000):
                marketplace.click()
                self.logger.info("✓ 点击 Marketplace 分类（ok.com）")
                return
        except Exception:
            pass
        
        try:
            # 最后兜底：Electronics
            electronics = self.page.get_by_role("link", name="Electronics", exact=True)
            if electronics.count() > 0:
                electronics.click()
                self.logger.info("✓ 点击 Electronics 分类")
                return
        except Exception as e:
            self.logger.error(f"点击 Marketplace/For Sale/Electronics 分类失败: {e}")
            raise
    
    def click_secondary_category_collectibles_art(self):
        """点击二级分类：Collectibles & Art（如果不存在则查找其他二级分类）"""
        try:
            # 先尝试原始名称
            link = self.page.get_by_role("link", name="Collectibles & Art")
            if link.count() > 0 and link.is_visible(timeout=1000):
                link.click()
                self.logger.info("✓ 点击 Collectibles & Art")
                return
        except Exception:
            pass
        
        # 58v5.cn 环境下可能没有，尝试找其他二级分类
        try:
            self.logger.info("Collectibles & Art 不存在，尝试查找其他二级分类...")
            self.page.wait_for_timeout(1000)
            
            # 悬停 Jobs 触发二级菜单
            jobs_link = self.page.get_by_role("link", name="Jobs", exact=True)
            if jobs_link.count() > 0:
                jobs_link.first.hover()
                self.page.wait_for_timeout(1000)
                self.logger.info("✓ 悬停 Jobs，等待二级菜单")
            
            # 查找 Accounting 作为可靠的二级分类
            accounting = self.page.get_by_role("link", name="Accounting")
            if accounting.count() > 0 and accounting.first.is_visible(timeout=2000):
                accounting.first.click()
                self.logger.info("✓ 点击二级分类: Accounting（替代）")
                return
            
            raise Exception("未找到可用的二级分类")
        except Exception as e:
            self.logger.error(f"点击二级分类失败: {e}")
            raise
    
    def click_secondary_category_clothing_shoes(self):
        """点击二级分类：Clothing & Shoes（如果不存在则查找其他二级分类）"""
        try:
            # 先尝试原始名称
            link = self.page.get_by_role("link", name="Clothing & Shoes")
            if link.count() > 0 and link.is_visible(timeout=1000):
                link.click(force=True)
                self.logger.info("✓ 点击 Clothing & Shoes")
                return
        except Exception:
            pass
        
        # 58v5.cn 环境下可能没有，尝试找其他二级分类
        try:
            self.logger.info("Clothing & Shoes 不存在，尝试查找其他二级分类...")
            self.page.wait_for_timeout(1000)
            
            # 悬停 Property 触发二级菜单
            property_link = self.page.get_by_role("link", name="Property", exact=True)
            if property_link.count() > 0:
                property_link.first.hover()
                self.page.wait_for_timeout(1000)
                self.logger.info("✓ 悬停 Property，等待二级菜单")
            
            # 查找 Buy 或 Rent 作为可靠的二级分类
            for cat_name in ["Buy", "Rent"]:
                cat_link = self.page.get_by_role("link", name=cat_name, exact=True)
                if cat_link.count() > 0 and cat_link.first.is_visible(timeout=2000):
                    cat_link.first.click(force=True)
                    self.logger.info(f"✓ 点击二级分类: {cat_name}（替代）")
                    return
            
            raise Exception("未找到可用的二级分类")
        except Exception as e:
            self.logger.error(f"点击二级分类失败: {e}")
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
