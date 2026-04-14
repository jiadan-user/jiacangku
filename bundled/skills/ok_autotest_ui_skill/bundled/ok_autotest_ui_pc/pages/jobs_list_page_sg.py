# pages/jobs_list_page_sg.py
from pages.base_page import BasePage
from utils.logger import setup_logger


class JobsListPageSG(BasePage):
    """
    新加坡站职位列表页页面对象 - 搜索与筛选功能
    URL: https://sg.58v5.cn/en/city-singapore/cate-jobs/
    页面结构：搜索框 + 筛选器区域 + 职位列表 + 分页
    """

    # ========== 页面元素选择器（Playwright 语法）==========

    # 搜索区域
    SEARCH_INPUT = "input[type='search']"
    SEARCH_INPUT_BACKUP = "input[placeholder*='Search']"
    SEARCH_BUTTON = "button:has-text('Search')"
    SEARCH_BUTTON_BACKUP = "[role='button']:has-text('Search')"

    # 筛选器区域
    LOCATION_FILTER = "text=Singapore"
    LOCATION_FILTER_DROPDOWN = "[role='button']:has-text('Singapore')"
    JOB_TYPE_FILTER = "text=Job Type"
    JOB_TYPE_FILTER_BTN = "[role='button']:has-text('Job Type')"
    WORKPLACE_TYPE_FILTER = "text=Workplace type"
    WORKPLACE_TYPE_FILTER_BTN = "[role='button']:has-text('Workplace type')"
    SALARY_FILTER = "text=Salary"
    SALARY_FILTER_BTN = "[role='button']:has-text('Salary')"
    RESET_BTN = "text=Reset"
    RESET_BTN_BACKUP = "[cursor='pointer']:has-text('Reset')"

    # 筛选器选项（动态面板）
    FILTER_OPTION_TEMPLATE = "text={option_name}"
    FILTER_CHECKBOX_TEMPLATE = "input[type='checkbox']"

    # 薪资筛选器输入框
    SALARY_MIN_INPUT = "input[placeholder*='Min']"
    SALARY_MAX_INPUT = "input[placeholder*='Max']"
    SALARY_CONFIRM_BTN = "button:has-text('Confirm')"

    # 职位列表区域
    JOB_LIST_CONTAINER = "[class*='job-list'], [class*='JobList']"
    JOB_CARD = "[class*='job-card'], [role='article']"
    FIRST_JOB_CARD = "[class*='job-card']:first-child"

    # 分页区域
    PAGINATION_CONTAINER = "[role='navigation']"
    NEXT_PAGE_BTN = "text=Next"
    NEXT_PAGE_BTN_BACKUP = "[aria-label*='Next']"
    PREV_PAGE_BTN = "text=Previous"
    PAGE_NUMBER_LINK = "[role='button'][aria-label*='page']"

    # 页面标识
    PAGE_HEADING = "h1:has-text('Jobs')"
    BREADCRUMB_NAV = "nav"

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    # ========== 搜索功能方法 ==========

    def input_search_keyword(self, keyword: str):
        """在搜索框中输入关键词"""
        try:
            self.page.locator(self.SEARCH_INPUT).first.fill(keyword)
            self.page.wait_for_timeout(500)
        except Exception:
            try:
                self.logger.error("主定位器失败，尝试备选定位器")
                self.page.locator(self.SEARCH_INPUT_BACKUP).first.fill(keyword)
                self.page.wait_for_timeout(500)
            except Exception as e:
                self.logger.error(f"输入搜索关键词失败: {e}")
                raise

    def click_search_button(self):
        """点击搜索按钮"""
        try:
            self.page.get_by_role("button", name="Search").click()
            self.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            try:
                self.logger.error("主定位器失败，尝试备选定位器")
                self.page.locator(self.SEARCH_BUTTON_BACKUP).first.click()
                self.page.wait_for_load_state("networkidle", timeout=10000)
            except Exception as e:
                self.logger.error(f"点击搜索按钮失败: {e}")
                raise

    def get_search_input_value(self) -> str:
        """获取搜索框当前值"""
        try:
            return self.page.locator(self.SEARCH_INPUT).first.input_value()
        except Exception as e:
            self.logger.error(f"获取搜索框值失败: {e}")
            return ""

    # ========== 筛选器操作方法 ==========

    def is_location_filter_visible(self) -> bool:
        """判断Location筛选器是否可见"""
        try:
            return self.is_visible(self.LOCATION_FILTER, timeout=5000)
        except Exception:
            return False

    def get_location_filter_text(self) -> str:
        """获取Location筛选器显示的文本"""
        try:
            return self.page.locator(self.LOCATION_FILTER).first.inner_text()
        except Exception as e:
            self.logger.error(f"获取Location筛选器文本失败: {e}")
            return ""

    def click_location_filter(self):
        """点击Location筛选器"""
        try:
            self.page.locator(self.LOCATION_FILTER_DROPDOWN).first.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击Location筛选器失败: {e}")
            raise

    def select_filter_option(self, option_name: str):
        """在筛选器面板中选择指定选项（通用方法）"""
        try:
            self.page.get_by_text(option_name, exact=True).first.click()
            self.page.wait_for_timeout(800)
        except Exception:
            try:
                self.page.get_by_text(option_name).first.click()
                self.page.wait_for_timeout(800)
            except Exception as e:
                self.logger.error(f"选择筛选器选项 '{option_name}' 失败: {e}")
                raise

    def click_job_type_filter(self):
        """点击Job Type筛选器"""
        try:
            self.page.get_by_role("button", name="Job Type").click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击Job Type筛选器失败: {e}")
            raise

    def click_workplace_type_filter(self):
        """点击Workplace Type筛选器"""
        try:
            self.page.get_by_role("button", name="Workplace type").click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击Workplace Type筛选器失败: {e}")
            raise

    def click_salary_filter(self):
        """点击Salary筛选器"""
        try:
            self.page.get_by_role("button", name="Salary").click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击Salary筛选器失败: {e}")
            raise

    def input_salary_range(self, min_salary: str = "", max_salary: str = ""):
        """输入薪资范围"""
        try:
            if min_salary:
                self.page.locator(self.SALARY_MIN_INPUT).first.fill(min_salary)
                self.page.wait_for_timeout(500)
            if max_salary:
                self.page.locator(self.SALARY_MAX_INPUT).first.fill(max_salary)
                self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"输入薪资范围失败: {e}")
            raise

    def confirm_salary_filter(self):
        """确认薪资筛选（点击Confirm按钮）"""
        try:
            self.page.get_by_role("button", name="Confirm").click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"确认薪资筛选失败: {e}")
            raise

    def click_reset_button(self):
        """点击Reset按钮重置所有筛选器"""
        try:
            self.page.get_by_text("Reset").first.click()
            self.page.wait_for_load_state("networkidle", timeout=10000)
            self.page.wait_for_timeout(1000)
        except Exception:
            try:
                self.logger.error("主定位器失败，尝试备选定位器")
                self.page.locator(self.RESET_BTN_BACKUP).first.click()
                self.page.wait_for_load_state("networkidle", timeout=10000)
            except Exception as e:
                self.logger.error(f"点击Reset按钮失败: {e}")
                raise

    def is_reset_button_visible(self) -> bool:
        """判断Reset按钮是否可见"""
        try:
            return self.is_visible(self.RESET_BTN, timeout=5000)
        except Exception:
            return False

    # ========== 职位列表验证方法 ==========

    def get_job_card_count(self) -> int:
        """获取职位卡片数量"""
        try:
            self.page.wait_for_timeout(2000)
            return self.page.locator(self.JOB_CARD).count()
        except Exception as e:
            self.logger.error(f"获取职位卡片数量失败: {e}")
            return 0

    def is_job_list_visible(self) -> bool:
        """判断职位列表是否可见"""
        try:
            return self.page.locator(self.JOB_CARD).first.is_visible(timeout=8000)
        except Exception:
            return False

    # ========== 分页功能方法 ==========

    def click_next_page(self):
        """点击下一页按钮"""
        try:
            self.page.get_by_text("Next").first.click()
            self.page.wait_for_load_state("networkidle", timeout=15000)
            self.page.wait_for_timeout(2000)
        except Exception:
            try:
                self.logger.error("主定位器失败，尝试备选定位器")
                self.page.locator(self.NEXT_PAGE_BTN_BACKUP).first.click()
                self.page.wait_for_load_state("networkidle", timeout=15000)
            except Exception as e:
                self.logger.error(f"点击下一页按钮失败: {e}")
                raise

    def click_previous_page(self):
        """点击上一页按钮"""
        try:
            self.page.get_by_text("Previous").first.click()
            self.page.wait_for_load_state("networkidle", timeout=15000)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击上一页按钮失败: {e}")
            raise

    def click_page_number(self, page_num: int):
        """点击指定页码"""
        try:
            self.page.get_by_role("button", name=str(page_num)).click()
            self.page.wait_for_load_state("networkidle", timeout=15000)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击页码 {page_num} 失败: {e}")
            raise

    def is_pagination_visible(self) -> bool:
        """判断分页控件是否可见"""
        try:
            return self.is_visible(self.PAGINATION_CONTAINER, timeout=5000)
        except Exception:
            return False

    # ========== 页面通用方法 ==========

    def navigate_to_jobs_list(self, base_url: str):
        """导航到职位列表页"""
        try:
            jobs_url = f"{base_url}/en/city-singapore/cate-jobs/?iconSource=jobs"
            self.goto(jobs_url)
            self.wait_for_page_load()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"导航到职位列表页失败: {e}")
            raise

    def get_current_url(self) -> str:
        """获取当前页面URL"""
        return self.page.url

    def is_page_loaded(self) -> bool:
        """判断页面是否加载完成（通过标题判断）"""
        try:
            return self.is_visible(self.PAGE_HEADING, timeout=10000)
        except Exception:
            return False

    def wait_for_page_load_complete(self):
        """等待页面完全加载"""
        try:
            self.page.wait_for_load_state("networkidle", timeout=15000)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"等待页面加载超时: {e}")
            raise
