# pages/jobs_list_page_ae.py
from pages.base_page import BasePage
from utils.logger import setup_logger


class JobsListPageAE(BasePage):
    """
    阿联酋站(AE)职位列表页页面对象
    URL: https://ae.58v5.cn/en/city-abu-dhabi/cate-jobs/
    页面结构：左侧职位列表 + 右侧职位详情面板 + 筛选器区域
    """

    # ========== 页面元素选择器（Playwright 语法，来自MCP录制）==========

    # 页面标识
    JOBS_PAGE_HEADING = "h1"
    BREADCRUMB_NAV = "nav"
    BREADCRUMB_HOME_LINK = "nav a:has-text('Home')"
    BREADCRUMB_JOBS_TEXT = "nav >> text=Jobs"

    # 筛选器区域
    FILTER_AREA = "#istPageFilterArea"  # 筛选器容器ID
    LOCATION_FILTER = "text=Abu Dhabi"  # 录制时的具体文本
    LOCATION_FILTER_GENERIC = "#istPageFilterArea >> text=Abu Dhabi"  # 更精确的定位
    LOCATION_FILTER_BACKUP = "[cursor=pointer]:has-text('Abu Dhabi')"
    JOB_TYPE_FILTER = "text=Job Type"
    WORKPLACE_TYPE_FILTER = "text=Workplace type"
    SALARY_FILTER = "text=Salary"
    RESET_FILTER_BTN = "text=Reset"

    # Add Job Preference 入口卡片（录制时的选择器）
    ADD_JOB_PREFERENCE_CARD = "text=Add Job Preference"
    ADD_JOB_PREFERENCE_TITLE = "text=Add Job Preference"
    ADD_JOB_PREFERENCE_SUBTITLE = "text=Unlock more opportunities tailored for you."
    ADD_JOB_PREFERENCE_BACKUP = "text=Unlock more opportunities"

    # 职位列表（左侧面板）
    JOB_LIST_CONTAINER = "div[class*='job']"
    FIRST_JOB_CARD = "div[class*='job']:first-child"

    # 职位详情面板（右侧）
    JOB_DETAIL_CONTACT_BTN = "button:has-text('Contact')"
    JOB_DETAIL_FAVOURITES_BTN = "text=Favourites"
    JOB_DETAIL_SHARE_BTN = "text=Share"

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    # ========== 页面操作方法（静默执行）==========

    def navigate_to_jobs_list(self, jobs_url: str):
        """直接导航到职位列表页"""
        try:
            self.goto(jobs_url)
            self.wait_for_page_load()
        except Exception as e:
            self.logger.error(f"导航到职位列表页失败: {e}")
            raise

    def wait_for_filter_area_loaded(self):
        """等待筛选器区域加载完成"""
        try:
            self.page.wait_for_selector(self.FILTER_AREA, timeout=10000)
        except Exception as e:
            self.logger.error(f"等待筛选器区域加载超时: {e}")
            raise

    # ========== Location 筛选器相关方法 ==========

    def is_location_filter_visible(self) -> bool:
        """判断Location筛选器是否可见"""
        try:
            return self.is_visible(self.LOCATION_FILTER, timeout=5000)
        except Exception:
            try:
                return self.is_visible(self.LOCATION_FILTER_BACKUP, timeout=3000)
            except Exception:
                return False

    def get_location_filter_text(self) -> str:
        """
        获取Location筛选器显示的文本
        录制时发现显示"Abu Dhabi"
        """
        try:
            return self.page.locator(self.LOCATION_FILTER_GENERIC).first.inner_text()
        except Exception:
            try:
                self.logger.error("主定位器失败，尝试备选定位器")
                return self.page.locator(self.LOCATION_FILTER_BACKUP).first.inner_text()
            except Exception as e:
                self.logger.error(f"获取Location筛选器文本失败: {e}")
                raise

    def click_location_filter(self):
        """
        点击Location筛选器打开城市选择面板
        录制时发现点击后弹出面板标题"Select Location"
        """
        try:
            self.page.locator(self.LOCATION_FILTER_GENERIC).first.click()
            # 等待面板打开
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击Location筛选器失败: {e}")
            raise

    # ========== Add Job Preference 卡片相关方法 ==========

    def is_add_job_preference_visible(self) -> bool:
        """
        判断Add Job Preference入口卡片是否可见
        录制时发现卡片位于列表左侧顶部第一张位置
        """
        try:
            return self.is_visible(self.ADD_JOB_PREFERENCE_CARD, timeout=5000)
        except Exception:
            try:
                return self.is_visible(self.ADD_JOB_PREFERENCE_BACKUP, timeout=3000)
            except Exception:
                return False

    def get_add_job_preference_title(self) -> str:
        """
        获取Add Job Preference卡片标题文本
        录制时确认标题为"Add Job Preference"
        """
        try:
            return self.page.locator(self.ADD_JOB_PREFERENCE_TITLE).first.inner_text()
        except Exception as e:
            self.logger.error(f"获取Add Job Preference标题失败: {e}")
            raise

    def get_add_job_preference_subtitle(self) -> str:
        """
        获取Add Job Preference卡片副文本
        录制时确认副文本为"Unlock more opportunities tailored for you."
        """
        try:
            return self.page.locator(self.ADD_JOB_PREFERENCE_SUBTITLE).first.inner_text()
        except Exception as e:
            self.logger.error(f"获取Add Job Preference副文本失败: {e}")
            raise

    def is_add_job_preference_clickable(self) -> bool:
        """
        判断Add Job Preference卡片是否可点击
        录制时确认卡片可点击（cursor=pointer）
        """
        try:
            element = self.page.locator(self.ADD_JOB_PREFERENCE_CARD).first
            return element.is_visible() and element.is_enabled()
        except Exception:
            return False

    def click_add_job_preference(self):
        """
        点击Add Job Preference卡片
        录制时发现点击后弹出登录弹窗（未登录状态）
        """
        try:
            self.page.locator(self.ADD_JOB_PREFERENCE_CARD).first.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击Add Job Preference卡片失败: {e}")
            raise

    # ========== 其他通用方法 ==========

    def is_reset_filter_visible(self) -> bool:
        """判断Reset筛选器按钮是否可见"""
        try:
            return self.is_visible(self.RESET_FILTER_BTN, timeout=5000)
        except Exception:
            return False

    def is_job_detail_panel_visible(self) -> bool:
        """判断右侧职位详情面板是否可见（通过Contact按钮）"""
        try:
            return self.is_visible(self.JOB_DETAIL_CONTACT_BTN, timeout=8000)
        except Exception:
            return False

    def get_current_url(self) -> str:
        """获取当前页面URL"""
        return self.page.url

    def get_page_title(self) -> str:
        """获取页面标题"""
        return self.page.title()
