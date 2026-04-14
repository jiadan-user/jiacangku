# pages/ai_publish_job_page.py
from pages.base_page import BasePage
from utils.logger import setup_logger


class AiPublishJobPage(BasePage):
    """AI推荐 - Job发布页面对象（静默执行）"""
    
    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()
    
    # ========== 页面操作方法（静默执行）==========
    
    def click_jobs_category(self):
        """点击Jobs类目，进入Job发布页面"""
        try:
            self.page.locator('span').filter(has_text='Jobs').click()
            self.page.wait_for_timeout(1000)
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception as e:
            self.logger.error(f"点击Jobs类目失败: {e}")
            raise
    
    def click_job_title(self):
        """点击 Job Title 输入框"""
        try:
            self.page.locator('#title').click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击 Job Title 输入框失败: {e}")
            raise
    
    def input_job_title(self, title):
        """
        输入职位标题
        
        Args:
            title: 职位标题
        """
        try:
            self.page.locator('#title').fill(title)
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"输入 Job Title 失败: {e}")
            raise
    
    def select_job_title_autocomplete_first(self):
        """
        选择 Job Title 联想列表第一项
        等待联想下拉出现后，通过精确文字匹配点击第一个候选项
        """
        try:
            title_val = self.page.locator('#title').input_value()
            # 等待联想列表出现（精确匹配候选文字）
            candidate = self.page.get_by_text(title_val, exact=True).first
            candidate.wait_for(state="visible", timeout=5000)
            candidate.click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择 Job Title 联想第一项失败: {e}")
            raise
    
    def clear_job_title(self):
        """清空 Job Title 字段（输入框有内容时才点清空按钮，否则直接清空）"""
        try:
            current_value = self.page.locator('#title').input_value()
            if not current_value:
                self.logger.info("Job Title 已为空，无需清空")
                return
            clear_btn = self.page.get_by_role("img", name="clear")
            if clear_btn.is_visible(timeout=3000):
                clear_btn.click()
                self.page.wait_for_timeout(500)
            else:
                self.page.locator('#title').fill("")
                self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"清空 Job Title 失败: {e}")
            raise
    
    def click_job_function(self):
        """点击 Job Function 下拉框"""
        try:
            self.page.locator('div').filter(has_text='Select Job Functions').nth(4).click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击 Job Function 下拉框失败: {e}")
            raise
    
    def wait_for_ai_recommendations(self, timeout=3000):
        """
        等待 AI 推荐加载
        
        Args:
            timeout: 超时时间（毫秒）
        """
        try:
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"等待 AI 推荐失败: {e}")
            raise
    
    def is_recommendations_displayed(self, timeout=8000):
        """
        检查 AI Recommendations 推荐结果是否显示。
        
        该方法会主动确保 Job Function 下拉框处于打开状态，然后验证 AI 推荐内容。
        页面结构：下拉打开后左侧有 Recommendations 文字项，右侧显示 3 条 AI 推荐子类目。
        验证标准：下拉框中的 cascade-select 元素有 'open' class 且右侧推荐区域有内容。
        
        Returns:
            bool: 是否显示 AI 推荐结果
        """
        try:
            # 确保下拉框处于打开状态
            is_open = self.page.evaluate("""
                () => document.querySelector('.cascade-select.open') !== null
            """)
            if not is_open:
                self.click_job_function()
                self.page.wait_for_timeout(2000)
            
            # 等待 cascade-select 有 open class（超时范围内）
            deadline = timeout
            interval = 500
            elapsed = 0
            while elapsed < deadline:
                result = self.page.evaluate("""
                    () => {
                        const cascade = document.querySelector('.cascade-select.open');
                        if (!cascade) return {open: false, cols: 0, children: 0};
                        const cols = cascade.querySelectorAll(':scope > div');
                        return {
                            open: true,
                            cols: cols.length,
                            children: cols.length >= 2 ? cols[1].children.length : 0
                        };
                    }
                """)
                if result.get('open') and result.get('children', 0) > 0:
                    return True
                self.page.wait_for_timeout(interval)
                elapsed += interval
            return False
        except Exception:
            return False
    
    def get_job_title_value(self):
        """
        获取 Job Title 输入框的值
        
        Returns:
            str: Job Title 值
        """
        try:
            return self.page.locator('#title').input_value()
        except Exception as e:
            self.logger.error(f"获取 Job Title 值失败: {e}")
            raise
    
    def is_job_function_dropdown_open(self):
        """
        确保 Job Function 下拉框处于打开状态并验证 AI 推荐是否显示。
        
        Returns:
            bool: 下拉框是否成功打开且有推荐内容
        """
        return self.is_recommendations_displayed()
    
    def close_job_function_dropdown(self):
        """关闭 Job Function 下拉框（按 Escape 键）"""
        try:
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"关闭 Job Function 下拉框失败: {e}")
            raise
