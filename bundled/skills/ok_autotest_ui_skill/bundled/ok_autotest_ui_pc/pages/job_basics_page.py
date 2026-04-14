# pages/job_basics_page.py
from pages.base_page import BasePage
from utils.logger import setup_logger


class JobBasicsPage(BasePage):
    """职位发布 - Job Basics 页面对象（静默执行）"""
    
    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()
    
    # ========== 页面操作方法（静默执行）==========
    
    def input_job_title(self, title):
        """
        输入职位标题
        
        Args:
            title: 职位标题
        """
        try:
            # 直接转换录制的 JavaScript 代码
            # await page.locator('#title').click();
            # await page.locator('#title').fill('Software Engineer Test 20260302');
            self.page.locator('#title').click()
            self.page.wait_for_timeout(500)
            self.page.locator('#title').fill(title)
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"输入 Job Title 失败: {e}")
            raise
    
    def dismiss_suggestions(self):
        """
        关闭推荐浮层（Job Title 输入后触发）
        通过点击页面标题来关闭
        """
        try:
            # 直接转换录制的 JavaScript 代码
            # await page.getByRole('heading', { name: 'Job Basics' }).click();
            self.page.get_by_role("heading", name="Job Basics").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"关闭推荐浮层失败: {e}")
            raise
    
    def select_job_function(self, category, subcategory):
        """
        选择 Job Function（两级选择）
        
        Args:
            category: 一级分类（如 "Information & Communication Technology"）
            subcategory: 二级分类（如 "Developers/Programmers"）
        """
        try:
            # 直接转换录制的 JavaScript 代码
            # await page.locator('div').filter({ hasText: 'Select Job Functions' }).nth(4).click();
            # await page.getByText('Information & Communication').first().click();
            # await page.getByText('Developers/Programmers').click();
            
            self.page.locator('div').filter(has_text='Select Job Functions').nth(4).click()
            self.page.wait_for_timeout(1000)
            
            self.page.get_by_text(category).first.click()
            self.page.wait_for_timeout(500)
            
            self.page.get_by_text(subcategory).click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择 Job Function 失败: {e}")
            raise
    
    def select_pay_type(self, pay_type):
        """
        选择 Pay Type
        
        Args:
            pay_type: 薪资类型（如 "Per Year"）
        """
        try:
            # 直接转换录制的 JavaScript 代码
            # await page.getByText('Pay TypePer Year').click();
            # await page.getByText('Per Year').nth(1).click();
            
            self.page.get_by_text(f"Pay Type{pay_type}").click()
            self.page.wait_for_timeout(1000)
            
            self.page.get_by_text(pay_type).nth(1).click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择 Pay Type 失败: {e}")
            raise
    
    def select_salary_range(self, min_amount, max_amount):
        """
        选择薪资范围
        
        Args:
            min_amount: 最小金额（如 "50000"）
            max_amount: 最大金额（如 "80000"）
        """
        try:
            # 直接转换录制的 JavaScript 代码
            # await page.locator('div').filter({ hasText: 'Amount($)' }).nth(5).click();
            # await page.getByText('50000', { exact: true }).click();
            # await page.locator('div').filter({ hasText: /^Amount\(\$\)$/ }).nth(1).click();
            # await page.getByText('80000', { exact: true }).click();
            
            # 选择第一个 Amount
            self.page.locator('div').filter(has_text='Amount($)').nth(5).click()
            self.page.wait_for_timeout(1000)
            self.page.get_by_text(min_amount, exact=True).click()
            self.page.wait_for_timeout(500)
            
            # 选择第二个 Amount
            import re
            self.page.locator('div').filter(has_text=re.compile(r'^Amount\(\$\)$')).nth(1).click()
            self.page.wait_for_timeout(1000)
            self.page.get_by_text(max_amount, exact=True).click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择薪资范围失败: {e}")
            raise
    
    def click_continue(self):
        """点击 Continue 按钮"""
        try:
            # 直接转换录制的 JavaScript 代码
            # await page.getByRole('button', { name: 'Continue' }).click();
            self.page.get_by_role("button", name="Continue").click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击 Continue 失败: {e}")
            raise
    
    def select_workplace_type_remote(self):
        """选择 Workplace Type 为 Remote"""
        try:
            # 直接转换录制的 JavaScript 代码
            # await page.getByRole('radio', { name: 'Unselected Remote' }).click();
            self.page.get_by_role("radio", name="Unselected Remote").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择 Remote 失败: {e}")
            raise
    
    def select_workplace_type_hybrid(self):
        """选择 Workplace Type 为 Hybrid"""
        try:
            # 直接转换录制的 JavaScript 代码
            # await page.getByRole('radio', { name: 'Unselected Hybrid' }).click();
            self.page.get_by_role("radio", name="Unselected Hybrid").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择 Hybrid 失败: {e}")
            raise
    
    def select_workplace_type_onsite(self):
        """选择 Workplace Type 为 Onsite"""
        try:
            # 直接转换录制的 JavaScript 代码
            # await page.getByRole('radio', { name: 'Unselected Onsite' }).click();
            self.page.get_by_role("radio", name="Unselected Onsite").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择 Onsite 失败: {e}")
            raise
