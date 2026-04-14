# pages/profile_page.py
from pages.base_page import BasePage
from utils.logger import setup_logger


class ProfilePage(BasePage):
    """OK.com 个人中心页面对象（静默执行）"""
    
    # ========== 页面元素选择器（Playwright 语法）==========
    # 用户头像菜单
    USER_MENU = "//div[contains(@class, 'user')]"
    USER_MENU_BACKUP = "generic:has-text('OKerUS')"
    
    # Profile下拉菜单选项
    PROFILE_MENU_ITEM = "text='Profile'"
    PROFILE_MENU_ITEM_BACKUP = "a:has-text('Profile')"
    
    # Profile页面URL模式
    PROFILE_URL_PATTERN = "**/profile/**"
    
    # Profile页面特征元素（用于验证）
    PROFILE_CONTAINER = "div[class*='profile']"
    PROFILE_HEADER = "div[class*='header']"
    
    # Profile编辑按钮（用户名右侧的编辑图标）
    EDIT_PROFILE_ICON = "img[src='https://sgj1.ok.com/yongjia/_next/static/media/edit_m.655b3cc6.png']"
    EDIT_PROFILE_ICON_BACKUP = "img[src*='edit_m']"
    
    # Profile编辑页面URL模式
    PROFILE_EDIT_URL_PATTERN = "**/biz/en/user/home"
    
    # Profile左侧导航栏元素（在编辑模式下才有）
    COUNTRY_REGION_NAV = "text='Country & Region'"
    COUNTRY_REGION_NAV_BACKUP = "a:has-text('Country & Region')"
    COUNTRY_REGION_NAV_BACKUP2 = "//a[contains(text(), 'Country') and contains(text(), 'Region')]"
    COUNTRY_REGION_NAV_BACKUP3 = "img[src*='user-language']"  # 使用图标定位
    
    # Country&Region页面URL模式
    COUNTRY_REGION_URL_PATTERN = "**/country**"
    
    # Country&Region页面元素
    COUNTRY_DROPDOWN = ".cont-r-country-l-bottom-text"
    COUNTRY_DROPDOWN_BACKUP = "div.cont-r-country-l-bottom-text"
    COUNTRY_DROPDOWN_ITEMS = ".cont-r-country-l-bottom-text"
    CONFIRM_BUTTON = "button:has-text('Confirm')"
    CONFIRM_BUTTON_BACKUP = "//button[contains(text(), 'Confirm')]"
    CONFIRM_BUTTON_BACKUP2 = "[class*='confirm']"
    
    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()
    
    # ========== 页面操作方法（静默执行）==========
    
    def click_user_menu(self):
        """
        点击右上角用户头像菜单
        支持备选定位器
        """
        try:
            self.wait_for_selector(self.USER_MENU, timeout=10000)
            self.click(self.USER_MENU)
        except Exception as e:
            # 尝试使用备选定位器
            try:
                self.logger.error(f"主定位器失败，尝试备选定位器: {e}")
                self.wait_for_selector(self.USER_MENU_BACKUP, timeout=5000)
                self.click(self.USER_MENU_BACKUP)
            except Exception as e2:
                self.logger.error(f"点击用户菜单失败（所有定位器均失败）: {e2}")
                raise
    
    def click_profile_menu_item(self):
        """
        点击下拉菜单中的Profile选项
        支持备选定位器
        """
        try:
            self.wait_for_selector(self.PROFILE_MENU_ITEM, timeout=5000)
            self.click(self.PROFILE_MENU_ITEM)
        except Exception as e:
            # 尝试使用备选定位器
            try:
                self.logger.error(f"主定位器失败，尝试备选定位器: {e}")
                self.wait_for_selector(self.PROFILE_MENU_ITEM_BACKUP, timeout=5000)
                self.click(self.PROFILE_MENU_ITEM_BACKUP)
            except Exception as e2:
                self.logger.error(f"点击Profile选项失败（所有定位器均失败）: {e2}")
                raise
    
    def navigate_to_profile_from_avatar(self):
        """
        从用户头像导航到Profile页面（便捷方法）
        """
        try:
            self.click_user_menu()
            self.click_profile_menu_item()
            # 等待Profile页面加载
            self.wait_for_url(self.PROFILE_URL_PATTERN, timeout=10000)
        except Exception as e:
            self.logger.error(f"从头像导航到Profile页面失败: {e}")
            raise
    
    def is_profile_page_loaded(self, timeout=5000):
        """
        判断Profile页面是否加载成功
        
        Args:
            timeout: 超时时间（毫秒）
        
        Returns:
            bool: 是否加载成功
        """
        try:
            # 检查URL是否包含profile
            current_url = self.get_current_url()
            return "profile" in current_url.lower()
        except Exception:
            return False
    
    def get_profile_url(self):
        """
        获取当前Profile页面的URL
        
        Returns:
            str: Profile页面URL
        """
        try:
            return self.get_current_url()
        except Exception as e:
            self.logger.error(f"获取Profile URL失败: {e}")
            return ""
    
    # ========== Profile编辑功能方法 ==========
    
    def click_edit_profile_icon(self):
        """
        点击Profile页面上的编辑图标
        支持备选定位器
        """
        try:
            self.wait_for_selector(self.EDIT_PROFILE_ICON, timeout=3000)
            self.click(self.EDIT_PROFILE_ICON)
        except Exception as e:
            try:
                self.logger.error(f"主定位器失败，尝试备选定位器: {e}")
                self.wait_for_selector(self.EDIT_PROFILE_ICON_BACKUP, timeout=3000)
                self.click(self.EDIT_PROFILE_ICON_BACKUP)
            except Exception as e2:
                self.logger.error(f"点击编辑图标失败（所有定位器均失败）: {e2}")
                raise
    
    def get_profile_edit_url(self):
        """
        获取当前Profile编辑页面的URL
        
        Returns:
            str: Profile编辑页面URL
        """
        try:
            return self.get_current_url()
        except Exception as e:
            self.logger.error(f"获取Profile编辑页URL失败: {e}")
            return ""
    
    # ========== Profile左侧导航栏操作方法 ==========
    
    def click_country_region_nav(self):
        """
        点击Profile编辑页面左侧导航栏中的Country & Region选项
        注意：此方法只能在编辑模式（/biz/en/user/home）下使用
        支持多个备选定位器
        """
        try:
            self.wait_for_selector(self.COUNTRY_REGION_NAV, timeout=5000)
            self.click(self.COUNTRY_REGION_NAV)
            self.logger.info("✓ 点击Country & Region导航成功")
        except Exception as e:
            try:
                self.logger.error(f"主定位器失败，尝试备选定位器1: {e}")
                self.wait_for_selector(self.COUNTRY_REGION_NAV_BACKUP, timeout=5000)
                self.click(self.COUNTRY_REGION_NAV_BACKUP)
                self.logger.info("✓ 点击Country & Region导航成功（使用备选定位器1）")
            except Exception as e2:
                try:
                    self.logger.error(f"备选定位器1失败，尝试备选定位器2: {e2}")
                    self.wait_for_selector(self.COUNTRY_REGION_NAV_BACKUP2, timeout=5000)
                    self.click(self.COUNTRY_REGION_NAV_BACKUP2)
                    self.logger.info("✓ 点击Country & Region导航成功（使用备选定位器2）")
                except Exception as e3:
                    try:
                        self.logger.error(f"备选定位器2失败，尝试备选定位器3（使用图标）: {e3}")
                        self.wait_for_selector(self.COUNTRY_REGION_NAV_BACKUP3, timeout=5000)
                        self.click(self.COUNTRY_REGION_NAV_BACKUP3)
                        self.logger.info("✓ 点击Country & Region导航成功（使用备选定位器3-图标）")
                    except Exception as e4:
                        self.logger.error(f"点击Country & Region导航失败（所有定位器均失败）: {e4}")
                        raise
    
    def is_country_region_page_loaded(self, timeout=5000):
        """
        判断Country&Region页面是否加载成功
        
        Args:
            timeout: 超时时间（毫秒）
        
        Returns:
            bool: 是否加载成功
        """
        try:
            current_url = self.get_current_url()
            return "country" in current_url.lower() or "user/home" in current_url
        except Exception:
            return False
    
    def get_country_region_url(self):
        """
        获取当前Country&Region页面的URL
        
        Returns:
            str: Country&Region页面URL
        """
        try:
            return self.get_current_url()
        except Exception as e:
            self.logger.error(f"获取Country&Region URL失败: {e}")
            return ""
    
    # ========== Country & Region 页面操作方法 ==========
    
    def click_country_dropdown(self):
        """
        点击Country下拉框
        支持备选定位器
        """
        try:
            self.wait_for_selector(self.COUNTRY_DROPDOWN, timeout=5000)
            self.click(self.COUNTRY_DROPDOWN)
            self.logger.info("✓ 点击Country下拉框成功")
        except Exception as e:
            try:
                self.logger.error(f"主定位器失败，尝试备选定位器: {e}")
                self.wait_for_selector(self.COUNTRY_DROPDOWN_BACKUP, timeout=5000)
                self.click(self.COUNTRY_DROPDOWN_BACKUP)
                self.logger.info("✓ 点击Country下拉框成功（使用备选定位器）")
            except Exception as e2:
                self.logger.error(f"点击Country下拉框失败（所有定位器均失败）: {e2}")
                raise
    
    def select_country_dropdown_item_by_index(self, index):
        """
        根据索引选择Country下拉框的选项
        
        Args:
            index: 选项索引（从0开始，例如：0=第一条，2=第三条）
        """
        try:
            # 等待下拉列表出现
            self.page.wait_for_timeout(1000)
            
            # 获取所有下拉选项
            dropdown_items = self.page.locator(self.COUNTRY_DROPDOWN_ITEMS).all()
            
            if index < len(dropdown_items):
                dropdown_items[index].click()
                self.logger.info(f"✓ 选择第{index + 1}条选项成功")
            else:
                raise Exception(f"索引 {index} 超出范围，共有 {len(dropdown_items)} 个选项")
        except Exception as e:
            self.logger.error(f"选择下拉选项失败: {e}")
            raise
    
    def click_confirm_button(self):
        """
        点击Confirm按钮（弹窗确认）
        支持多个备选定位器
        """
        try:
            self.wait_for_selector(self.CONFIRM_BUTTON, timeout=5000)
            self.click(self.CONFIRM_BUTTON)
            self.logger.info("✓ 点击Confirm按钮成功")
        except Exception as e:
            try:
                self.logger.error(f"主定位器失败，尝试备选定位器1: {e}")
                self.wait_for_selector(self.CONFIRM_BUTTON_BACKUP, timeout=5000)
                self.click(self.CONFIRM_BUTTON_BACKUP)
                self.logger.info("✓ 点击Confirm按钮成功（使用备选定位器1）")
            except Exception as e2:
                try:
                    self.logger.error(f"备选定位器1失败，尝试备选定位器2: {e2}")
                    self.wait_for_selector(self.CONFIRM_BUTTON_BACKUP2, timeout=5000)
                    self.click(self.CONFIRM_BUTTON_BACKUP2)
                    self.logger.info("✓ 点击Confirm按钮成功（使用备选定位器2）")
                except Exception as e3:
                    self.logger.error(f"点击Confirm按钮失败（所有定位器均失败）: {e3}")
                    raise

