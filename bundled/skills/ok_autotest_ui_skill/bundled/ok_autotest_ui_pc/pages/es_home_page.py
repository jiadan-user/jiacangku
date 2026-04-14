"""
ES站（西班牙站）首页 Page Object
用于验证登录状态和首页交互

页面URL: https://es.58v5.cn/en/city-madrid2/
"""

from pages.base_page import BasePage
from utils.logger import setup_logger


class EsHomePage(BasePage):
    """ES站首页页面对象"""
    
    # 用户登录状态相关选择器
    LOGIN_REGISTER_BUTTON = "text=Log in / Register"
    USER_MENU_BUTTON = "OKerES_"  # 登录后显示的用户名前缀
    USER_PROFILE_ICON = ".UserMenu_"  # 用户头像/菜单图标
    
    # Jobs金刚位选择器（录制得到）
    JOBS_ICON = "link:has-text('Jobs Jobs')"
    
    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()
    
    def is_logged_in(self):
        """
        检查是否已登录
        登录后会显示用户名（以OKerES_开头）
        """
        try:
            # 方法1：检查用户名是否可见
            user_menu = self.page.locator("text=/OKerES_/")
            if user_menu.is_visible(timeout=3000):
                self.logger.info("✓ 检测到登录用户名")
                return True
            
            # 方法2：检查登录/注册按钮是否不可见
            login_btn = self.page.get_by_text("Log in / Register")
            if not login_btn.is_visible(timeout=2000):
                self.logger.info("✓ 登录/注册按钮不可见，判定为已登录")
                return True
            
            return False
        except Exception as e:
            self.logger.warning(f"检查登录状态异常: {e}")
            return False
    
    def click_jobs_icon(self):
        """点击Jobs金刚位"""
        self.page.get_by_role("link", name="Jobs Jobs").click()
        self.logger.info("点击Jobs金刚位")
    
    def navigate_to_home(self, base_url="https://es.58v5.cn"):
        """导航到ES站首页"""
        url = f"{base_url}/en/city-madrid2/"
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")
        self.logger.info(f"导航到ES站首页: {url}")
