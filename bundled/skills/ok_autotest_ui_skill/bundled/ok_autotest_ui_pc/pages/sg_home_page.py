# pages/sg_home_page.py
from pages.base_page import BasePage
from utils.logger import setup_logger


class SgHomePage(BasePage):
    """新加坡站首页页面对象（https://sg.58v5.cn/en/city-singapore/）"""

    # ========== 页面元素选择器（Playwright 语法）==========

    # Cookie 同意弹窗
    COOKIE_ACCEPT_ALL_BTN = "button:has-text('Accept all')"
    COOKIE_POPUP = "text=Consent to Non-essential Cookies"

    # 顶部导航
    LOGO = "img[alt*='ok']"
    SEARCH_INPUT = "input[placeholder='Search for anything']"
    SEARCH_BTN = "button:has-text('Search')"
    LOGIN_REGISTER_BTN = "text=Log in / Register"

    # 分类导航栏（首页顶部图标导航区，带 img[alt='Jobs'] 限定避免匹配到页面内其他 cate-jobs 链接）
    JOBS_NAV_LINK = "a[href*='cate-jobs']:has(img[alt='Jobs'])"
    JOBS_NAV_LINK_BACKUP = "a[class*='dropdownItemLabel'][href*='cate-jobs']"
    BUY_SELL_NAV_LINK = "a[href*='cate-marketplace']"
    PROPERTY_NAV_LINK = "a[href*='cate-property']"
    CARS_NAV_LINK = "a[href*='cate-cars']"
    SERVICES_NAV_LINK = "a[href*='cate-services']"
    COMMUNITY_NAV_LINK = "a[href*='cate-community']"

    # 首页内容区
    TOP_PICKS_SECTION = "text=Top Picks"
    VIEW_MORE_LINK = "text=View more"

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    # ========== 页面操作方法（静默执行）==========

    def navigate_to_home(self, base_url: str):
        """导航到新加坡站首页"""
        try:
            home_url = f"{base_url}/en/city-singapore/"
            self.goto(home_url)
            self.wait_for_page_load()
        except Exception as e:
            self.logger.error(f"打开新加坡首页失败: {e}")
            raise

    def handle_cookie_popup(self):
        """处理 Cookie 同意弹窗（接受全部）"""
        try:
            if self.is_visible(self.COOKIE_ACCEPT_ALL_BTN, timeout=5000):
                self.click(self.COOKIE_ACCEPT_ALL_BTN)
        except Exception as e:
            self.logger.error(f"处理 Cookie 弹窗失败: {e}")
            raise

    def click_jobs_nav(self):
        """点击顶部分类导航中的 Jobs 金刚位（精确匹配 'Jobs Jobs' 避免点到 Popular in Jobs）"""
        try:
            # 优先使用 getByRole 精确匹配导航区 "Jobs Jobs"，避免误点 "Popular in Jobs | View more"
            nav_link = self.page.get_by_role("link", name="Jobs Jobs")
            nav_link.wait_for(state="visible", timeout=15000)
            nav_link.click()
        except Exception as e:
            try:
                self.logger.warning(f"getByRole 失败，尝试 CSS 定位器: {e}")
                self.page.wait_for_selector(self.JOBS_NAV_LINK, timeout=15000)
                self.page.locator(self.JOBS_NAV_LINK).first.click()
            except Exception as e2:
                try:
                    self.logger.warning(f"主定位器失败，尝试备选: {e2}")
                    self.page.locator(self.JOBS_NAV_LINK_BACKUP).first.click()
                except Exception as e3:
                    self.logger.error(f"点击 Jobs 导航失败（所有定位器均失败）: {e3}")
                    raise

    def is_cookie_popup_visible(self) -> bool:
        """判断 Cookie 弹窗是否可见"""
        try:
            return self.is_visible(self.COOKIE_POPUP, timeout=3000)
        except Exception:
            return False

    def is_logged_in(self) -> bool:
        """判断用户是否已登录（通过检查登录按钮文字）"""
        try:
            return not self.is_visible(self.LOGIN_REGISTER_BTN, timeout=3000)
        except Exception:
            return False

    def get_page_title(self) -> str:
        """获取页面标题"""
        try:
            return self.get_title()
        except Exception as e:
            self.logger.error(f"获取页面标题失败: {e}")
            raise

    def is_jobs_nav_visible(self) -> bool:
        """判断 Jobs 分类导航是否可见"""
        try:
            self.page.wait_for_selector(self.JOBS_NAV_LINK, state="visible", timeout=5000)
            return True
        except Exception:
            try:
                self.page.wait_for_selector(self.JOBS_NAV_LINK_BACKUP, state="visible", timeout=3000)
                return True
            except Exception:
                return False

    def click_add_job_preference_card(self) -> bool:
        """在 Jobs 列表页点击 'Add Job Preference' 卡片（已有 Job Preference 时的编辑入口）"""
        try:
            selectors = [
                "text=Add Job Preference",
                "text=Unlock more opportunities tailored for you.",
                "[class*='preference'] >> text=Add",
            ]
            for sel in selectors:
                try:
                    self.page.locator(sel).first.wait_for(state="visible", timeout=3000)
                    self.page.locator(sel).first.click()
                    self.logger.info("✓ 点击 Add Job Preference 卡片")
                    return True
                except Exception:
                    continue
            return False
        except Exception:
            return False
