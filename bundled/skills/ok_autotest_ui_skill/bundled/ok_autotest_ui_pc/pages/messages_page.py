# pages/messages_page.py
from pages.base_page import BasePage
from utils.logger import setup_logger


class MessagesPage(BasePage):
    """OK.com Messages页面对象（静默执行）"""
    
    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()
    
    # ========== 页面元素选择器 ==========
    
    # Messages链接/按钮（可能在导航栏或菜单中）
    MESSAGES_LINK = "a[href*='chat'], a[href*='messages'], button:has-text('Messages')"
    MESSAGES_NAV_LINK = "text=Messages"
    
    # Messages页面标识元素
    MESSAGES_PAGE_HEADING = "h1:has-text('Messages'), h2:has-text('Messages')"
    MESSAGES_CONTAINER = ".messages-container, [class*='message'], [class*='chat']"
    
    # Cookie弹窗
    COOKIE_ACCEPT_BUTTON = "button:has-text('Accept all'), button:has-text('Accept')"
    
    # ========== 页面操作方法（静默执行）==========
    
    def navigate_to_messages(self):
        """
        直接导航到Messages页面
        """
        try:
            # 直接访问Messages页面URL
            self.page.goto("https://aepub.ok.com/biz/en/chat", wait_until="domcontentloaded", timeout=60000)
            # 等待页面加载，不使用 networkidle
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"导航到Messages页面失败: {e}")
            raise
    
    def handle_cookie_popup(self):
        """
        处理 Cookie 弹窗（如果存在）
        如果弹窗不存在，不会抛出异常
        """
        try:
            # 尝试多种可能的 Cookie 弹窗按钮
            cookie_selectors = [
                "button:has-text('Accept All')",
                "button:has-text('Accept all')",
                "button:has-text('Accept')",
                "button:has-text('I Accept')"
            ]
            
            for selector in cookie_selectors:
                try:
                    cookie_button = self.page.locator(selector).first
                    if cookie_button.is_visible(timeout=2000):
                        cookie_button.click()
                        self.page.wait_for_timeout(1000)
                        break
                except Exception:
                    continue
        except Exception:
            # Cookie 弹窗不存在，不做任何处理
            pass
    
    def click_messages_link(self):
        """
        点击Messages链接（从首页导航栏）
        """
        try:
            # 尝试多种可能的Messages入口
            messages_selectors = [
                "a[href*='chat']",
                "a[href*='messages']",
                "text=Messages",
                "button:has-text('Messages')"
            ]
            
            for selector in messages_selectors:
                try:
                    messages_link = self.page.locator(selector).first
                    if messages_link.is_visible(timeout=3000):
                        messages_link.click()
                        self.page.wait_for_timeout(2000)
                        return
                except Exception:
                    continue
            
            # 如果所有选择器都失败，抛出异常
            raise Exception("未找到Messages链接")
        except Exception as e:
            self.logger.error(f"点击Messages链接失败: {e}")
            raise
    
    def is_messages_page_loaded(self, timeout=10000):
        """
        验证Messages页面是否加载成功
        
        Args:
            timeout: 超时时间（毫秒）
        
        Returns:
            bool: 页面是否加载成功
        """
        try:
            # 方法1: 检查URL是否包含chat或messages
            current_url = self.page.url
            if 'chat' in current_url.lower() or 'messages' in current_url.lower():
                return True
            
            # 方法2: 检查页面标识元素
            # 尝试查找Messages相关的标题或容器
            page_indicators = [
                "h1:has-text('Messages')",
                "h2:has-text('Messages')",
                "[class*='message']",
                "[class*='chat']",
                "text=Messages"
            ]
            
            for selector in page_indicators:
                try:
                    if self.is_visible(selector, timeout=timeout):
                        return True
                except Exception:
                    continue
            
            return False
        except Exception as e:
            self.logger.error(f"验证Messages页面加载失败: {e}")
            return False
    
    def get_page_url(self):
        """
        获取当前页面URL
        
        Returns:
            str: 当前页面URL
        """
        try:
            return self.page.url
        except Exception as e:
            self.logger.error(f"获取页面URL失败: {e}")
            raise
    
    def get_page_title(self):
        """
        获取页面标题
        
        Returns:
            str: 页面标题
        """
        try:
            return self.page.title()
        except Exception as e:
            self.logger.error(f"获取页面标题失败: {e}")
            raise
