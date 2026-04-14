"""
OK.com 车详情页 Page Object
"""
from pages.base_page import BasePage


class CarDetailPage(BasePage):
    """车详情页面对象"""
    
    def __init__(self, page):
        """
        初始化车详情页
        
        Args:
            page: Playwright Page对象
        """
        super().__init__(page)
        self.page = page
