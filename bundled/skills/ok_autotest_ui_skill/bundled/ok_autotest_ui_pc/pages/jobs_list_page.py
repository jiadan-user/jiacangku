# pages/jobs_list_page.py
from pages.base_page import BasePage
from utils.logger import setup_logger


class JobsListPage(BasePage):
    """
    新加坡站职位列表页页面对象
    URL: https://sg.58v5.cn/en/city-singapore/cate-jobs/
    页面结构：左侧职位列表 + 右侧职位详情面板 + 右侧 Popular Jobs 分类
    """

    # ========== 页面元素选择器（Playwright 语法）==========

    # 页面标识（面包屑区域的 h1，页面上有 2 个 h1，通过 class 精准定位面包屑标题）
    JOBS_PAGE_HEADING = "h1[class*='Breadcrumb']"
    JOBS_PAGE_HEADING_BACKUP = "nav h1"
    BREADCRUMB_NAV = "nav"
    BREADCRUMB_HOME_LINK = "nav a:has-text('Home')"
    BREADCRUMB_JOBS_TEXT = "nav >> text=Jobs"

    # 位置筛选器
    LOCATION_FILTER_AREA = "text=Singapore"
    RESET_FILTER_BTN = "text=Reset"
    RESET_FILTER_BTN_BACKUP = "[cursor=pointer]:has-text('Reset')"

    # 职位偏好 CTA
    ADD_JOB_PREFERENCE_CTA = "text=Add Job Preference"
    ADD_JOB_PREFERENCE_CTA_BACKUP = "text=Unlock more opportunities"

    # 职位列表（左侧面板）
    JOB_LIST_CONTAINER = "text=not whatsapp user"  # 备用锚定
    FIRST_JOB_CARD = "div[class*='job']:first-child, [cursor=pointer]:has-text('S$')"

    # 职位详情面板（右侧）
    JOB_DETAIL_CONTACT_BTN = "button:has-text('Contact')"
    JOB_DETAIL_FAVOURITES_BTN = "text=Favourites"
    JOB_DETAIL_SHARE_BTN = "text=Share"
    JOB_DETAIL_NEW_TAB_BTN = "text=New tab"
    JOB_DETAIL_DESCRIPTION = "text=Description"
    JOB_DETAIL_POSTED_DATE = "text=Posted"

    # Popular Jobs 分类（右侧底部 tab）
    POPULAR_JOBS_TAB = "[role='tab']:has-text('Popular Jobs')"
    POPULAR_JOBS_TAB_BACKUP = "text=Popular Jobs"
    POPULAR_JOBS_CATEGORIES = "[role='tabpanel'] a"

    # 底部 Resume FAB 按钮
    RESUME_FAB_BTN = "text=Resume"

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    # ========== 页面操作方法（静默执行）==========

    def navigate_to_jobs_list(self, base_url: str):
        """直接导航到职位列表页"""
        try:
            jobs_url = f"{base_url}/en/city-singapore/cate-jobs/"
            self.goto(jobs_url)
            self.wait_for_page_load()
        except Exception as e:
            self.logger.error(f"导航到职位列表页失败: {e}")
            raise

    def wait_for_jobs_list_loaded(self):
        """等待职位列表页加载完成（等待面包屑 h1）"""
        try:
            self.page.wait_for_selector(self.JOBS_PAGE_HEADING, timeout=15000)
        except Exception:
            try:
                self.page.wait_for_selector(self.JOBS_PAGE_HEADING_BACKUP, timeout=10000)
            except Exception as e:
                self.logger.error(f"等待职位列表页加载超时: {e}")
                raise

    def get_page_heading_text(self) -> str:
        """获取面包屑 h1 标题文字（明确定位面包屑标题，避免与详情面板 Company h1 冲突）"""
        try:
            self.page.wait_for_selector(self.JOBS_PAGE_HEADING, timeout=10000)
            return self.page.locator(self.JOBS_PAGE_HEADING).first.inner_text()
        except Exception:
            try:
                self.logger.error("主定位器失败，尝试备选定位器 nav h1")
                return self.page.locator(self.JOBS_PAGE_HEADING_BACKUP).first.inner_text()
            except Exception as e:
                self.logger.error(f"获取页面标题失败: {e}")
                raise

    def is_breadcrumb_home_visible(self) -> bool:
        """判断面包屑 Home 链接是否可见"""
        try:
            return self.is_visible(self.BREADCRUMB_HOME_LINK, timeout=5000)
        except Exception:
            return False

    def is_location_filter_visible(self) -> bool:
        """判断位置筛选器（Singapore）是否可见"""
        try:
            return self.is_visible(self.LOCATION_FILTER_AREA, timeout=5000)
        except Exception:
            return False

    def is_reset_filter_visible(self) -> bool:
        """判断重置筛选器按钮是否可见"""
        try:
            return self.is_visible(self.RESET_FILTER_BTN, timeout=5000)
        except Exception:
            return self.is_visible(self.RESET_FILTER_BTN_BACKUP, timeout=3000)

    def is_add_job_preference_visible(self) -> bool:
        """判断 Add Job Preference CTA 是否可见"""
        try:
            return self.is_visible(self.ADD_JOB_PREFERENCE_CTA, timeout=5000)
        except Exception:
            return self.is_visible(self.ADD_JOB_PREFERENCE_CTA_BACKUP, timeout=3000)

    def click_first_job_card(self):
        """点击第一个职位卡片"""
        try:
            self.wait_for_selector("button:has-text('Contact')", timeout=10000)
        except Exception as e:
            self.logger.error(f"等待职位详情面板失败，可能职位列表为空: {e}")
            raise

    def is_job_detail_panel_visible(self) -> bool:
        """判断右侧职位详情面板是否可见（通过 Contact 按钮）"""
        try:
            return self.is_visible(self.JOB_DETAIL_CONTACT_BTN, timeout=8000)
        except Exception:
            return False

    def is_favourites_button_visible(self) -> bool:
        """判断收藏按钮是否可见"""
        try:
            return self.is_visible(self.JOB_DETAIL_FAVOURITES_BTN, timeout=5000)
        except Exception:
            return False

    def is_share_button_visible(self) -> bool:
        """判断分享按钮是否可见"""
        try:
            return self.is_visible(self.JOB_DETAIL_SHARE_BTN, timeout=5000)
        except Exception:
            return False

    def is_description_section_visible(self) -> bool:
        """判断职位描述区域是否可见"""
        try:
            return self.is_visible(self.JOB_DETAIL_DESCRIPTION, timeout=5000)
        except Exception:
            return False

    def is_popular_jobs_tab_visible(self) -> bool:
        """判断 Popular Jobs 分类 tab 是否可见"""
        try:
            return self.is_visible(self.POPULAR_JOBS_TAB, timeout=5000)
        except Exception:
            return self.is_visible(self.POPULAR_JOBS_TAB_BACKUP, timeout=3000)

    def get_popular_jobs_category_count(self) -> int:
        """获取 Popular Jobs 分类链接数量"""
        try:
            self.wait_for_selector(self.POPULAR_JOBS_CATEGORIES, timeout=8000)
            return self.page.locator(self.POPULAR_JOBS_CATEGORIES).count()
        except Exception as e:
            self.logger.error(f"获取 Popular Jobs 分类数量失败: {e}")
            return 0

    def is_resume_fab_visible(self) -> bool:
        """判断 Resume FAB 按钮是否可见"""
        try:
            return self.is_visible(self.RESUME_FAB_BTN, timeout=5000)
        except Exception:
            return False

    def get_current_url(self) -> str:
        """获取当前页面 URL"""
        return self.page.url

    def click_breadcrumb_home(self):
        """点击面包屑 Home 链接返回首页"""
        try:
            self.click(self.BREADCRUMB_HOME_LINK)
        except Exception as e:
            self.logger.error(f"点击面包屑 Home 失败: {e}")
            raise
