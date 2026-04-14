"""
OK.com 车列表页 Page Object
"""
from pages.base_page import BasePage


class CarListingPage(BasePage):
    """车列表页面对象"""
    
    def __init__(self, page):
        """
        初始化车列表页
        
        Args:
            page: Playwright Page对象
        """
        super().__init__(page)
        self.page = page
