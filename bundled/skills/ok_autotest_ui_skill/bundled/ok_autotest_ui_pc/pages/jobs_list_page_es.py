"""
ES站 Jobs列表页 Page Object
专门用于ES站（西班牙站）招聘列表页的搜索与筛选功能测试

页面URL: https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs
包含功能:
  - 搜索框操作
  - 地址筛选（Madrid默认）
  - Job Type筛选（含回显验证）
  - Workplace type筛选（含回显验证）
  - Salary筛选（含回显验证）
  - Reset按钮
  - feed流无限滚动加载
  - 职位卡片交互
  - 侧边栏详情
"""

from pages.base_page import BasePage
from utils.logger import setup_logger


class JobsListPageES(BasePage):
    """
    ES站职位列表页页面对象 - 搜索与筛选功能
    URL: https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs
    """
    
    # ==================== 搜索区域选择器 ====================
    SEARCH_INPUT = "input[type='search']"
    SEARCH_INPUT_BACKUP = "input[placeholder*='Search']"
    SEARCH_BUTTON = "button:has-text('Search')"
    
    # ==================== 筛选器区域选择器 ====================
    LOCATION_FILTER = ".listPage-filterArea"  # 地址筛选区域
    LOCATION_FILTER_TEXT = "Madrid"  # 默认地址文本
    JOB_TYPE_FILTER = "text=Job Type"
    WORKPLACE_TYPE_FILTER = "text=Workplace type"
    SALARY_FILTER = "text=Salary"
    RESET_BUTTON = "button:has-text('Reset')"
    
    # ==================== 地址筛选面板选择器 ====================
    LOCATION_PANEL = ".LocationSelector_locationSelector__"  # 城市选择面板容器
    CURRENT_LOCATION_ICON = "img[alt='location']"
    NEAR_ME_OPTION = "text=Near me"
    TOP_CITIES_CONTAINER = ".QuickCities_"  # Top Cities容器
    ALPHABET_INDEX = ".Letter_"  # 字母索引容器
    CITY_LIST = ".CityList_"
    
    # ==================== Job Type筛选面板选择器 ====================
    JOB_TYPE_PANEL = ".Selector_optionContainer__"
    JOB_TYPE_OPTION = ".Selector_optionItem__er6y4"
    JOB_TYPE_CLEAR = "button:has-text('Clear')"
    JOB_TYPE_CONFIRM = "button:has-text('Confirm')"
    
    # ==================== 职位列表选择器 ====================
    ADD_JOB_PREF_ENTRY = "text=Add Job Preference"
    JOB_CARD = ".JobListItem_"
    JOB_LIST_CONTAINER = ".listPageJobSection"
    
    # ==================== 分页选择器 ====================
    PAGINATION_CONTAINER = "list"  # 分页组件
    PAGE_BUTTON = "button"  # 页码按钮
    NEXT_BUTTON = "button:has-text('Next')"
    PREV_BUTTON = "text=Previous"
    
    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()
    
    # ==================== 导航方法 ====================
    
    def navigate_to_jobs_list(self):
        """导航到Jobs列表页"""
        url = "https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs"
        self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
        try:
            self.page.wait_for_load_state("networkidle", timeout=8000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发，忽略超时
        # 等待筛选区域可见，确保页面关键内容已渲染
        try:
            self.page.locator(".listPage-filterArea").wait_for(state="visible", timeout=15000)
        except Exception:
            self.page.wait_for_timeout(3000)
        self.logger.info(f"导航到Jobs列表页: {url}")
    
    # ==================== 搜索功能方法 ====================
    
    def input_search_keyword(self, keyword: str):
        """在搜索框中输入关键词"""
        try:
            self.page.get_by_role("textbox", name="Search for anything").fill(keyword)
            self.page.wait_for_timeout(500)
            self.logger.info(f"输入搜索关键词: {keyword}")
        except Exception:
            # 备用选择器
            self.page.locator(self.SEARCH_INPUT).first.fill(keyword)
            self.logger.info(f"使用备用选择器输入关键词: {keyword}")
    
    def click_search_button(self):
        """点击搜索按钮"""
        self.page.get_by_role("button", name="Search").click()
        self.logger.info("点击搜索按钮")
    
    def get_search_input_value(self):
        """获取搜索框当前值"""
        try:
            return self.page.get_by_role("textbox", name="Search for anything").input_value()
        except Exception:
            return self.page.locator(self.SEARCH_INPUT).first.input_value()
    
    # ==================== 地址筛选功能方法 ====================
    
    def click_location_filter(self):
        """点击地址筛选器（Madrid）"""
        # 使用MCP录制的选择器：.listPage-filterArea下的Madrid文本
        self.page.locator(self.LOCATION_FILTER).get_by_text("Madrid").click()
        self.logger.info("点击Madrid地址筛选器")
    
    def is_location_panel_visible(self):
        """检查城市选择面板是否可见"""
        try:
            # 检查搜索框（城市面板的标志性元素）
            return self.page.get_by_placeholder("Search City").is_visible(timeout=3000)
        except Exception:
            return False
    
    def is_current_location_displayed(self, city_name: str):
        """检查当前选中的城市是否显示"""
        try:
            # 在面板中查找带location图标的当前城市
            location_element = self.page.locator("img[alt='location']").locator("..").locator("..")
            return city_name in location_element.text_content()
        except Exception:
            return False
    
    def is_near_me_option_visible(self):
        """检查Near me选项是否可见"""
        try:
            return self.page.get_by_text("Near me").is_visible(timeout=2000)
        except Exception:
            return False
    
    def is_top_cities_visible(self):
        """检查Top Cities列表是否可见"""
        try:
            # 查找Top Cities文本
            return self.page.get_by_text("Top Cities").is_visible(timeout=2000)
        except Exception:
            return False
    
    def is_alphabet_index_visible(self):
        """检查字母索引是否可见"""
        try:
            # 查找字母A（索引的第一个字母）
            return self.page.locator("text=A").first.is_visible(timeout=2000)
        except Exception:
            return False
    
    def select_city_from_top_cities(self, city_name: str):
        """从Top Cities中选择城市"""
        self.page.get_by_text(city_name).first.click()
        self.logger.info(f"从Top Cities选择城市: {city_name}")
    
    # ==================== Job Type筛选功能方法 ====================
    
    def click_job_type_filter(self):
        """点击Job Type筛选器（含激活态 badge）"""
        self.page.locator(".listPage-filterArea > div").filter(
            has_text="Job Type"
        ).first.click()
        self.logger.info("点击Job Type筛选器")
    
    def is_job_type_panel_visible(self):
        """检查Job Type面板是否可见"""
        try:
            return self.page.get_by_role("button", name="Confirm").is_visible(timeout=3000)
        except Exception:
            return False
    
    def select_job_type_option(self, option_name: str):
        """选择Job Type选项
        
        Args:
            option_name: Full-time, Part-time, Contract, Internship, Temporary
        """
        # 使用MCP录制的选择器：.Selector_optionItem__er6y4
        self.page.locator(".Selector_optionItem__er6y4").filter(has_text=option_name).first.click()
        self.logger.info(f"选择Job Type: {option_name}")
    
    def click_job_type_confirm(self):
        """点击Job Type的Confirm按钮"""
        self.page.get_by_role("button", name="Confirm").click()
        self.logger.info("点击Job Type Confirm按钮")
        try:
            self.page.locator(".listPage-filterArea").wait_for(state="visible", timeout=12000)
        except Exception:
            self.page.wait_for_timeout(2000)
    
    def click_job_type_clear(self):
        """点击Job Type的Clear按钮"""
        self.page.get_by_role("button", name="Clear").click()
        self.logger.info("点击Job Type Clear按钮")
    
    # ==================== Workplace type筛选功能方法 ====================
    
    def click_workplace_type_filter(self):
        """点击Workplace type筛选器（含激活态 badge）"""
        self.page.locator(".listPage-filterArea > div").filter(
            has_text="Workplace type"
        ).first.click()
        self.logger.info("点击Workplace type筛选器")
    
    def select_workplace_type_option(self, option_name: str):
        """选择Workplace type选项
        
        Args:
            option_name: Onsite, Remote, Hybrid
        """
        self.page.locator(".Selector_optionItem__er6y4").filter(has_text=option_name).first.click()
        self.logger.info(f"选择Workplace type: {option_name}")
    
    def click_workplace_type_confirm(self):
        """点击Workplace type的Confirm按钮"""
        self.page.get_by_role("button", name="Confirm").click()
        self.logger.info("点击Workplace type Confirm按钮")
        try:
            self.page.locator(".listPage-filterArea").wait_for(state="visible", timeout=12000)
        except Exception:
            self.page.wait_for_timeout(2000)
    
    # ==================== Salary筛选功能方法 ====================
    
    def click_salary_filter(self):
        """点击Salary筛选器（含激活态 badge）"""
        self.page.locator(".listPage-filterArea > div").filter(
            has_text="Salary"
        ).first.click()
        self.logger.info("点击Salary筛选器")
    
    def input_salary_range(self, min_salary: str = None, max_salary: str = None):
        """输入薪资范围"""
        if min_salary:
            # 根据实际录制的选择器调整
            self.page.locator("input[type='number']").first.fill(min_salary)
            self.logger.info(f"输入最小薪资: {min_salary}")
        if max_salary:
            self.page.locator("input[type='number']").nth(1).fill(max_salary)
            self.logger.info(f"输入最大薪资: {max_salary}")
    
    def click_salary_confirm(self):
        """点击Salary的Confirm按钮"""
        self.page.get_by_role("button", name="Confirm").click()
        self.logger.info("点击Salary Confirm按钮")
        try:
            self.page.locator(".listPage-filterArea").wait_for(state="visible", timeout=12000)
        except Exception:
            self.page.wait_for_timeout(2000)
    
    # ==================== Reset功能方法 ====================
    
    def click_reset_button(self):
        """点击Reset按钮清除所有筛选"""
        self.page.locator(".listPage-filterArea-submit").click()
        self.logger.info("点击Reset按钮")
    
    def is_reset_button_visible(self):
        """检查Reset按钮是否可见"""
        try:
            return self.page.locator(".listPage-filterArea-submit").is_visible(timeout=3000)
        except Exception:
            return False
    
    # ==================== 职位列表功能方法 ====================
    
    def is_add_job_pref_entry_visible(self):
        """检查Add Job Preference入口是否可见"""
        try:
            return self.page.get_by_text("Add Job Preference").is_visible(timeout=2000)
        except Exception:
            return False
    
    def click_add_job_pref_entry(self):
        """点击Add Job Preference入口"""
        self.page.get_by_text("Add Job Preference").click()
        self.logger.info("点击Add Job Preference入口")
    
    def get_job_card_count(self):
        """获取职位卡片数量"""
        return self.page.locator(self.JOB_CARD).count()
    
    def is_job_list_visible(self):
        """检查职位列表是否可见"""
        try:
            return self.get_job_card_count() > 0
        except Exception:
            return False
    
    # ==================== 分页功能方法 ====================
    
    def click_page_number(self, page_num: int):
        """点击指定页码
        
        Args:
            page_num: 页码数字
        """
        self.page.get_by_role("button", name=str(page_num)).click()
        self.logger.info(f"点击页码: {page_num}")
    
    def click_next_page(self):
        """点击Next按钮"""
        self.page.get_by_role("button", name="Next").click()
        self.logger.info("点击Next按钮")
    
    def click_prev_page(self):
        """点击Previous按钮"""
        self.page.get_by_text("Previous").click()
        self.logger.info("点击Previous按钮")
    
    def is_next_button_enabled(self):
        """检查Next按钮是否可用"""
        try:
            next_btn = self.page.get_by_role("button", name="Next")
            return next_btn.is_enabled() and next_btn.is_visible()
        except Exception:
            return False
    
    def is_prev_button_enabled(self):
        """检查Previous按钮是否可用"""
        try:
            prev_btn = self.page.get_by_text("Previous")
            return prev_btn.is_visible()
        except Exception:
            return False
    
    # ==================== 通用验证方法 ====================
    
    def is_page_loaded(self):
        """检查页面是否加载完成"""
        try:
            # 检查关键元素：搜索框和筛选区域
            search_visible = self.page.get_by_role("textbox", name="Search for anything").is_visible(timeout=5000)
            filter_visible = self.page.locator(".listPage-filterArea").is_visible(timeout=2000)
            return search_visible and filter_visible
        except Exception:
            return False
    
    def is_filter_area_visible(self):
        """检查筛选器区域是否可见"""
        try:
            return self.page.locator(self.LOCATION_FILTER).is_visible(timeout=2000)
        except Exception:
            return False
    
    def get_current_url(self):
        """获取当前页面URL"""
        return self.page.url
    
    def wait_for_filter_update(self):
        """等待筛选更新完成"""
        try:
            self.page.wait_for_load_state("networkidle", timeout=8000)
        except Exception:
            pass  # ES站存在长连接，networkidle不会触发
        self.page.wait_for_timeout(1000)

    # ==================== 地址筛选扩展方法（两级省→市结构）====================

    def select_province(self, province_name: str):
        """在地址筛选面板中选择省份（第一级）
        
        Args:
            province_name: 省份名称，如 Catalonia, Madrid, Andalusia
        """
        try:
            self.page.get_by_text(province_name, exact=True).click()
            self.page.wait_for_timeout(600)
        except Exception as e:
            self.logger.error(f"选择省份失败: {province_name}, {e}")
            raise

    def select_city_from_panel(self, city_name: str):
        """在地址筛选面板中选择城市（第二级）
        
        Args:
            city_name: 城市名称，如 Barcelona, Madrid
        """
        try:
            self.page.get_by_text(city_name, exact=True).first.click()
        except Exception as e:
            self.logger.error(f"选择城市失败: {city_name}, {e}")
            raise

    def is_location_search_box_visible(self):
        """检查地址面板搜索框是否可见"""
        try:
            return self.page.get_by_placeholder("Search City").is_visible(timeout=3000)
        except Exception:
            return False

    # ==================== Job Type筛选扩展方法 ====================

    def is_job_type_option_visible(self, option_name: str):
        """检查Job Type选项是否可见
        
        Args:
            option_name: 选项名称，如 Full-time, Part-time
        """
        try:
            return self.page.locator(".Selector_optionItem__er6y4").filter(
                has_text=option_name
            ).first.is_visible(timeout=2000)
        except Exception:
            return False

    def is_filter_confirm_button_visible(self):
        """检查筛选面板的Confirm按钮是否可见"""
        try:
            return self.page.get_by_role("button", name="Confirm").is_visible(timeout=2000)
        except Exception:
            return False

    def is_job_type_filter_active(self, count: int = 1):
        """检查Job Type筛选器是否已激活并显示正确数量
        
        Args:
            count: 期望的选择数量，如 1 对应 "Job Type · 1"
        """
        try:
            filter_text = self.page.locator(".listPage-filterArea").get_by_text(
                f"Job Type"
            ).first.text_content()
            return f"· {count}" in filter_text or f"·{count}" in filter_text
        except Exception:
            try:
                # 备选：检查URL中是否有attr_60参数（Full-time）
                return "attr_60=" in self.page.url
            except Exception:
                return False

    # ==================== Workplace type筛选扩展方法 ====================

    def is_workplace_type_filter_active(self, count: int = 1):
        """检查Workplace type筛选器是否已激活并显示正确数量
        
        Args:
            count: 期望的选择数量
        """
        try:
            filter_text = self.page.locator(".listPage-filterArea").get_by_text(
                "Workplace type"
            ).first.text_content()
            return f"· {count}" in filter_text or f"·{count}" in filter_text
        except Exception:
            try:
                return "attr_" in self.page.url and "attr_60=" not in self.page.url
            except Exception:
                return False

    # ==================== Salary筛选扩展方法 ====================

    def is_salary_panel_visible(self):
        """检查Salary面板是否可见"""
        try:
            return self.page.get_by_role("button", name="Confirm").is_visible(timeout=3000)
        except Exception:
            return False

    def is_salary_filter_active(self):
        """检查Salary筛选器是否已激活"""
        try:
            filter_text = self.page.locator(".listPage-filterArea").get_by_text(
                "Salary"
            ).first.text_content()
            return "·" in filter_text
        except Exception:
            try:
                return "salary" in self.page.url.lower() or "attr_" in self.page.url
            except Exception:
                return False

    # ==================== Reset功能扩展方法 ====================

    def is_madrid_filter_displayed(self):
        """检查地址筛选器是否显示Madrid"""
        try:
            return self.page.locator(".listPage-filterArea").get_by_text(
                "Madrid"
            ).is_visible(timeout=2000)
        except Exception:
            return False

    # ==================== feed流加载方法 ====================

    def scroll_to_bottom(self):
        """滚动到页面底部，触发 feed 流加载更多"""
        try:
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"滚动到页面底部失败: {e}")
            raise

    def get_job_card_count_by_evaluate(self) -> int:
        """通过 JS 获取当前职位卡片总数（更精确）"""
        try:
            count = self.page.evaluate(
                "() => document.querySelectorAll('.JobListItem_jobListItem__').length"
            )
            return int(count) if count else 0
        except Exception:
            return 0

    def get_scroll_height(self) -> int:
        """获取当前页面 scrollHeight"""
        try:
            return int(self.page.evaluate("() => document.body.scrollHeight"))
        except Exception:
            return 0

    def has_pagination_buttons(self) -> bool:
        """检查页面是否存在分页按钮（Previous/Next/页码）"""
        try:
            has_next = self.page.get_by_role("button", name="Next").count() > 0
            has_prev = self.page.get_by_text("Previous").count() > 0
            return has_next or has_prev
        except Exception:
            return False

    # ==================== 筛选回显验证方法 ====================

    def is_job_type_option_selected(self, option_name: str) -> bool:
        """检查 Job Type 面板中指定选项是否处于选中状态
        
        Args:
            option_name: 选项名称，如 Full-time, Part-time
        Returns:
            True 表示已选中（class 含 Selector_selected__7svoy）
        """
        try:
            option = self.page.locator(".Selector_optionItem__er6y4").filter(
                has_text=option_name
            ).first
            class_attr = option.get_attribute("class") or ""
            return "Selector_selected__7svoy" in class_attr
        except Exception as e:
            self.logger.error(f"检查选项选中状态失败: {option_name}, {e}")
            return False

    def get_selected_job_type_options(self) -> list:
        """获取 Job Type 面板中所有已选中选项的文本列表"""
        try:
            items = self.page.locator(".Selector_optionItem__er6y4").all()
            selected = []
            for item in items:
                class_attr = item.get_attribute("class") or ""
                if "Selector_selected__7svoy" in class_attr:
                    selected.append(item.inner_text().strip())
            return selected
        except Exception as e:
            self.logger.error(f"获取已选中选项失败: {e}")
            return []

    def get_salary_min_value(self) -> str:
        """获取 Salary 面板 Min 输入框当前值"""
        try:
            return self.page.get_by_placeholder("Min").input_value()
        except Exception:
            return ""

    def get_salary_max_value(self) -> str:
        """获取 Salary 面板 Max 输入框当前值"""
        try:
            return self.page.get_by_placeholder("Max").input_value()
        except Exception:
            return ""

    def input_salary_min(self, value: str):
        """在 Salary 面板中输入 Min 值"""
        try:
            self.page.get_by_placeholder("Min").fill(value)
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"输入 Salary Min 失败: {e}")
            raise

    def input_salary_max(self, value: str):
        """在 Salary 面板中输入 Max 值"""
        try:
            self.page.get_by_placeholder("Max").fill(value)
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"输入 Salary Max 失败: {e}")
            raise

    def click_salary_clear(self):
        """点击 Salary 面板的 Clear 按钮"""
        try:
            self.page.get_by_role("button", name="Clear").click()
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"点击 Salary Clear 失败: {e}")
            raise

    def get_salary_filter_badge_text(self) -> str:
        """获取 Salary 筛选器 badge 文本（如 'Salary · 2'）"""
        try:
            return self.page.locator(".listPage-filterArea").get_by_text(
                "Salary"
            ).first.text_content() or ""
        except Exception:
            return ""

    def get_job_type_filter_badge_count(self) -> int:
        """获取 Job Type 筛选器 badge 的数量（如 'Job Type · 2' 返回 2）"""
        try:
            text = self.page.locator(".listPage-filterArea").get_by_text(
                "Job Type"
            ).first.text_content() or ""
            import re
            match = re.search(r'·\s*(\d+)', text)
            return int(match.group(1)) if match else 0
        except Exception:
            return 0

    # ==================== 职位卡片交互方法 ====================

    def click_first_job_card(self):
        """点击第一张职位卡片"""
        try:
            # 实际职位卡片使用 list-components-item-job-card 类
            self.page.locator('[class*="list-components-item-job-card"]').first.click()
            self.page.wait_for_timeout(1000)
        except Exception:
            try:
                self.page.locator(".JobListItem_jobListItem__").first.click()
                self.page.wait_for_timeout(1000)
            except Exception as e:
                self.logger.error(f"点击第一张职位卡片失败: {e}")
                raise

    def is_sidebar_visible(self) -> bool:
        """检查职位详情侧边栏是否可见"""
        try:
            # 实际侧边栏使用 DetailsCard 组件
            if self.page.locator('[class*="DetailsCard_detailsCard__"]').first.is_visible(timeout=5000):
                return True
        except Exception:
            pass
        try:
            return self.page.locator(".JobDetail_jobDetail__").first.is_visible(timeout=3000)
        except Exception:
            try:
                return self.page.get_by_role("button", name="Contact").is_visible(timeout=3000)
            except Exception:
                return False

    def is_sidebar_contact_button_visible(self) -> bool:
        """检查侧边栏 Contact 按钮是否可见"""
        try:
            return self.page.get_by_role("button", name="Contact").is_visible(timeout=3000)
        except Exception:
            return False

    def is_sidebar_withdraw_button_visible(self) -> bool:
        """检查侧边栏 Withdraw 按钮是否可见（自投职位）"""
        try:
            return self.page.get_by_role("button", name="Withdraw").is_visible(timeout=3000)
        except Exception:
            return False

    def is_sidebar_favourites_visible(self) -> bool:
        """检查侧边栏 Favourites 按钮是否可见"""
        try:
            return self.page.get_by_text("Favourites").first.is_visible(timeout=3000)
        except Exception:
            return False

    def is_sidebar_new_tab_link_visible(self) -> bool:
        """检查侧边栏 New tab 链接是否可见"""
        try:
            return self.page.get_by_role("link", name="New tab").is_visible(timeout=3000)
        except Exception:
            return False

    def is_sidebar_resume_entry_visible(self) -> bool:
        """检查侧边栏底部 Resume 快捷入口是否可见"""
        try:
            return self.page.get_by_text("Resume").first.is_visible(timeout=3000)
        except Exception:
            return False

    def click_sidebar_resume(self):
        """点击侧边栏底部 Resume 快捷入口"""
        try:
            self.page.get_by_text("Resume").first.click()
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception as e:
            self.logger.error(f"点击 Resume 入口失败: {e}")
            raise

    def is_quick_reply_label_visible(self) -> bool:
        """检查职位卡片上 Quick Reply 标签是否可见"""
        try:
            return self.page.get_by_text("Quick Reply").first.is_visible(timeout=3000)
        except Exception:
            return False

    def get_filter_area_text(self) -> str:
        """获取筛选器区域完整文本（用于验证Reset后状态）"""
        try:
            return self.page.locator(".listPage-filterArea").text_content() or ""
        except Exception:
            return ""

    def navigate_to_jobs_list_with_params(self, params: str = ""):
        """导航到带参数的 Jobs 列表页
        
        Args:
            params: URL 参数字符串，如 'attr_60=1' 或 'attr_60=2%2C1'
        """
        base = "https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs"
        url = f"{base}&{params}" if params else base
        try:
            self.page.goto(url, wait_until="domcontentloaded")
            try:
                self.page.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                pass  # ES站存在长连接，networkidle不会触发
            self.page.wait_for_timeout(1500)
        except Exception as e:
            self.logger.error(f"导航到 Jobs 列表页失败: {e}")
            raise

    def is_location_filter_active(self) -> bool:
        """检查地址筛选器是否处于激活态（class 含 FilterItem_filterItemActive）"""
        try:
            madrid_el = self.page.locator(".listPage-filterArea").get_by_text("Madrid").first
            class_attr = madrid_el.get_attribute("class") or ""
            return "FilterItemActive" in class_attr or "filterItemActive" in class_attr
        except Exception:
            try:
                return "city-madrid2" in self.page.url
            except Exception:
                return False

    def is_popular_cities_tab_visible(self) -> bool:
        """检查页面底部 Popular Cities 标签页是否可见"""
        try:
            return self.page.get_by_text("Popular Cities").first.is_visible(timeout=3000)
        except Exception:
            return False

    def get_popular_cities_links_count(self) -> int:
        """获取 Popular Cities 标签页下城市链接数量"""
        try:
            tab_panel = self.page.get_by_role("tabpanel").first
            return tab_panel.get_by_role("link").count()
        except Exception:
            return 0

    def click_home_nav_link(self):
        """点击顶部导航 Home 链接"""
        try:
            self.page.get_by_role("link", name="Home").click()
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception as e:
            self.logger.error(f"点击 Home 链接失败: {e}")
            raise

    def click_browse_menu(self):
        """点击顶部导航 Browse 菜单"""
        try:
            self.page.get_by_text("Browse").first.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击 Browse 菜单失败: {e}")
            raise

    def is_no_pagination_button_present(self) -> bool:
        """确认页面无分页按钮（Next/Previous/页码），返回 True 表示无分页"""
        return not self.has_pagination_buttons()

    def clear_search_box(self):
        """清空搜索框内容"""
        try:
            self.page.get_by_role("textbox", name="Search for anything").fill("")
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"清空搜索框失败: {e}")
            raise

    def click_job_type_filter_active(self):
        """点击已激活（含数字badge）的 Job Type 筛选器"""
        try:
            self.page.locator(".listPage-filterArea > div").filter(
                has_text="Job Type"
            ).first.click()
            self.page.wait_for_timeout(800)
        except Exception as e:
            self.logger.error(f"点击 Job Type 激活态筛选器失败: {e}")
            raise

    def click_outside_panel(self):
        """点击面板外部区域以关闭面板"""
        try:
            self.page.get_by_role("heading", name="Jobs").click()
            self.page.wait_for_timeout(500)
        except Exception:
            try:
                self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(500)
            except Exception as e:
                self.logger.error(f"关闭面板失败: {e}")
                raise

    def select_all_job_type_options(self):
        """选中 Job Type 面板的全部5个选项"""
        options = ["Full-time", "Part-time", "Contract", "Internship", "Temporary"]
        for opt in options:
            self.page.locator(".Selector_optionItem__er6y4").filter(has_text=opt).first.click()
            self.page.wait_for_timeout(200)
