# pages/jobs_list_search_filter_page_ae.py
"""
AE站 Jobs招聘列表页 - 搜索与筛选功能 Page Object
基于MCP Playwright录制生成

对应测试用例: ok-ae-JobsList-SearchAndFilter-测试用例-20260316.md (TC001-TC063)

MCP实测确认的真实选择器：
- 搜索框: page.getByRole('textbox', { name: 'Search for anything' })
- Search按钮: page.getByRole('button', { name: 'Search' })
- Location筛选: page.getByText('Location')
- Dubai城市: div:nth-child(2) > .CascadingSelector_itemContent__RM88u > div
- All UAE: .CascadingSelector_itemContent__RM88u > div (first)
- Job Type筛选: page.locator('#istPageFilterArea').getByText('Job Type')
- Full-time选项: page.locator('.Selector_optionItem__er6y4').first()
- Confirm: page.getByRole('button', { name: 'Confirm' })
- Clear: page.getByRole('button', { name: 'Clear' })
- Workplace type筛选: page.getByText('Workplace type')
- Salary筛选: page.getByText('Salary', { exact: true })
- Min输入框: page.getByRole('textbox', { name: 'Min' })
- Max输入框: page.getByRole('textbox', { name: 'Max' })
- Reset: page.getByText('Reset')

关键URL参数说明（MCP实测）：
- attr_60: Job Type (Full-time=1, Part-time=2, Contract=3, Internship=4, Temporary=5)
- attr_61: Workplace type (Onsite=1, Remote=2, Hybrid=3)
- attr_80: 薪资周期 (Per Hour=默认无, Per Day=2, Per Week=3, Per Month=4, Per Biweek=5, Per Year=6)
- lowestPrice / highestPrice: 薪资Min/Max（替代旧的min_price/max_price）
- preferenceCateId: 岗位偏好类别ID
- 城市筛选：通过URL路径实现（如/city-dubai/），非query参数
"""
from pages.base_page import BasePage
from utils.logger import setup_logger

import re


class JobsListSearchFilterPageAE(BasePage):
    """
    AE站 Jobs 招聘列表页 搜索与筛选功能页面对象
    目标URL: https://ae.58v5.cn/en/city/cate-jobs/?iconSource=jobs
    """

    # 筛选条与列表卡片上均可能出现 “Job Type/job type” 文案，必须限定在筛选容器内避免 strict mode 多匹配
    FILTER_AREA_SELECTOR = "#istPageFilterArea"

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    def _filter_area(self):
        return self.page.locator(self.FILTER_AREA_SELECTOR)

    def _job_type_filter_trigger(self):
        # 部分环境文案可能大小写变化（Job type / JOB TYPE），用正则更稳
        return self._filter_area().locator("text=/^Job\\s+Type$/i").first

    def _wait_filters_ready(self, timeout_ms: int = 30000) -> None:
        """等待筛选条容器与核心筛选项可用，规避偶发渲染慢/骨架态导致的超时。"""
        # 先确保筛选容器出现
        self._filter_area().wait_for(state="attached", timeout=timeout_ms)
        # 再确保 Job Type 入口可见
        jt = self._job_type_filter_trigger()
        try:
            jt.scroll_into_view_if_needed(timeout=5000)
        except Exception:
            pass
        jt.wait_for(state="visible", timeout=timeout_ms)

    # ========== 导航方法 ==========

    def navigate_to_jobs_list(self, base_url: str):
        """导航到Jobs列表页"""
        try:
            target_url = f"{base_url}/en/city/cate-jobs/?iconSource=jobs"
            self.page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            # 回到顶部，避免滚动位置导致筛选条不可见/不可点
            try:
                self.page.evaluate("window.scrollTo(0, 0)")
            except Exception:
                pass
            # networkidle 在部分页面可能不稳定，作为 soft wait
            for _ in range(2):
                try:
                    self.page.wait_for_load_state("networkidle", timeout=8000)
                    break
                except Exception:
                    self.page.wait_for_timeout(800)
            # 关键：等待筛选条 ready（含 Job Type）
            self._wait_filters_ready(timeout_ms=30000)
        except Exception as e:
            self.logger.error(f"导航到Jobs列表页失败: {e}")
            raise

    def get_current_url(self) -> str:
        """获取当前URL"""
        try:
            return self.page.url
        except Exception as e:
            self.logger.error(f"获取URL失败: {e}")
            raise

    # ========== 搜索框方法 ==========

    def input_search_keyword(self, keyword: str):
        """在搜索框输入关键词"""
        try:
            self.page.get_by_role("textbox", name="Search for anything").click()
            self.page.get_by_role("textbox", name="Search for anything").fill(keyword)
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"输入搜索关键词失败: {e}")
            raise

    def click_search_button(self):
        """点击Search按钮"""
        try:
            self.page.get_by_role("button", name="Search").click()
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击Search按钮失败: {e}")
            raise

    def search_jobs(self, keyword: str):
        """搜索职位（输入关键词+点击Search）"""
        try:
            self.input_search_keyword(keyword)
            self.click_search_button()
        except Exception as e:
            self.logger.error(f"搜索职位失败: {e}")
            raise

    def press_enter_in_search(self):
        """在搜索框按 Enter 键触发搜索"""
        try:
            self.page.get_by_role("textbox", name="Search for anything").press("Enter")
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"搜索框按Enter失败: {e}")
            raise

    def get_search_box_value(self) -> str:
        """获取搜索框当前值"""
        try:
            return self.page.get_by_role("textbox", name="Search for anything").input_value()
        except Exception as e:
            self.logger.error(f"获取搜索框值失败: {e}")
            return ""

    def is_search_result_page(self) -> bool:
        """判断当前是否为搜索结果中间页"""
        try:
            return "keyword=" in self.page.url
        except Exception:
            return False

    # ========== Location 筛选器方法 ==========

    def click_location_filter(self):
        """点击Location筛选器打开面板（兼容已选城市时按钮文字变为城市名）"""
        try:
            # 优先点击 "Location" 按钮（无城市时）
            loc_btn = self.page.get_by_text("Location", exact=True)
            if loc_btn.count() > 0 and loc_btn.is_visible(timeout=3000):
                loc_btn.click()
            else:
                # 已选城市时，筛选栏第一个按钮文字变为城市名（class=FilterItem_filterItem__Ur24_）
                # 筛选栏容器 #istPageFilterArea 内第一个筛选项即为 Location 按钮
                self.page.locator("#istPageFilterArea .FilterItem_filterItem__Ur24_").first.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击Location筛选器失败: {e}")
            raise

    def is_location_panel_visible(self) -> bool:
        """判断Location选择面板是否可见"""
        try:
            return self.page.locator("text=Select Location").is_visible(timeout=5000)
        except Exception:
            return False

    def search_city(self, city_name: str):
        """在Location面板搜索城市"""
        try:
            self.page.get_by_role("textbox", name="Search City").fill(city_name)
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"搜索城市失败: {e}")
            raise

    def select_city_dubai(self):
        """选择Dubai城市（来自MCP录制的真实选择器）"""
        try:
            self.page.locator("div:nth-child(2) > .CascadingSelector_itemContent__RM88u > div").click()
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"选择Dubai失败: {e}")
            raise

    def select_all_uae(self):
        """选择All United Arab Emirates"""
        try:
            self.page.locator(".CascadingSelector_itemContent__RM88u > div").first.click()
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"选择All UAE失败: {e}")
            raise

    def click_use_current_location(self):
        """点击Use current location按钮"""
        try:
            self.page.get_by_role("button", name="Use current location").click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击Use current location失败: {e}")
            raise

    def is_location_filter_showing_default(self) -> bool:
        """判断Location筛选器是否显示默认状态（无选中城市）"""
        try:
            return self.page.get_by_text("Location", exact=True).is_visible(timeout=3000)
        except Exception:
            return False

    # ========== Job Type 筛选器方法 ==========

    def click_job_type_filter(self):
        """点击Job Type筛选器打开面板"""
        try:
            # 并发/弱网下偶发筛选条未 ready，先 wait
            self._wait_filters_ready(timeout_ms=30000)
            trigger = self._job_type_filter_trigger()
            try:
                trigger.scroll_into_view_if_needed(timeout=5000)
            except Exception:
                pass
            # Click 可能被遮罩拦截，允许重试
            last_err: Exception | None = None
            for _ in range(3):
                try:
                    trigger.click(timeout=15000)
                    last_err = None
                    break
                except Exception as e:
                    last_err = e
                    try:
                        self.page.evaluate("window.scrollTo(0, 0)")
                    except Exception:
                        pass
                    self.page.wait_for_timeout(1200)
                    self._wait_filters_ready(timeout_ms=30000)
            if last_err:
                raise last_err
            self.page.wait_for_timeout(800)
        except Exception as e:
            self.logger.error(f"点击Job Type筛选器失败: {e}")
            raise

    def is_job_type_panel_visible(self) -> bool:
        """判断Job Type面板是否可见"""
        try:
            return self.page.locator(".Selector_optionItem__er6y4").first.is_visible(timeout=5000)
        except Exception:
            return False

    def select_job_type_full_time(self):
        """选择Full-time（MCP录制选择器）"""
        try:
            self.page.locator(".Selector_optionItem__er6y4").first.click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择Full-time失败: {e}")
            raise

    def select_job_type_part_time(self):
        """选择Part-time"""
        try:
            self.page.locator(".Selector_optionItem__er6y4").nth(1).click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择Part-time失败: {e}")
            raise

    def select_job_type_contract(self):
        """选择Contract"""
        try:
            self.page.locator(".Selector_optionItem__er6y4").nth(2).click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择Contract失败: {e}")
            raise

    def click_filter_confirm(self):
        """点击筛选面板的Confirm按钮"""
        try:
            self.page.get_by_role("button", name="Confirm").click()
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            try:
                self.page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                pass
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击Confirm失败: {e}")
            raise

    def click_filter_clear(self):
        """点击筛选面板的Clear按钮"""
        try:
            self.page.get_by_role("button", name="Clear").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击Clear失败: {e}")
            raise

    def is_job_type_filter_has_badge(self) -> bool:
        """判断Job Type筛选器是否有数量徽章"""
        try:
            url = self.page.url
            return "attr_60" in url
        except Exception:
            return False

    def get_job_type_badge_count(self) -> int:
        """获取Job Type筛选器的徽章数量"""
        try:
            badge_locator = self._job_type_filter_trigger().locator("..").locator("text=/·\\s*\\d+/")
            if badge_locator.is_visible(timeout=2000):
                text = badge_locator.text_content()
                import re
                match = re.search(r"(\d+)", text)
                if match:
                    return int(match.group(1))
            return 0
        except Exception:
            return 0

    def close_filter_panel_by_escape(self):
        """按 Escape 键关闭筛选面板"""
        try:
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"按Escape关闭面板失败: {e}")
            raise

    # ========== Workplace Type 筛选器方法 ==========

    def click_workplace_type_filter(self):
        """点击Workplace type筛选器打开面板"""
        try:
            self.page.get_by_text("Workplace type", exact=True).click()
            self.page.wait_for_timeout(800)
        except Exception as e:
            self.logger.error(f"点击Workplace type筛选器失败: {e}")
            raise

    def is_workplace_type_panel_visible(self) -> bool:
        """判断Workplace type面板是否可见（筛选弹出面板）"""
        try:
            # 筛选面板打开后，选项列表容器可见
            return self.page.locator(".Selector_optionItem__er6y4").first.is_visible(timeout=5000)
        except Exception:
            return False

    def select_workplace_onsite(self):
        """选择Onsite"""
        try:
            self.page.locator(".Selector_optionItem__er6y4").filter(has_text="Onsite").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择Onsite失败: {e}")
            raise

    def select_workplace_remote(self):
        """选择Remote"""
        try:
            self.page.locator(".Selector_optionItem__er6y4").filter(has_text="Remote").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择Remote失败: {e}")
            raise

    def select_workplace_hybrid(self):
        """选择Hybrid"""
        try:
            self.page.locator(".Selector_optionItem__er6y4").filter(has_text="Hybrid").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择Hybrid失败: {e}")
            raise

    # ========== Salary 筛选器方法 ==========

    def click_salary_filter(self):
        """点击Salary筛选器打开面板"""
        try:
            self.page.get_by_text("Salary", exact=True).click()
            self.page.wait_for_timeout(800)
        except Exception as e:
            self.logger.error(f"点击Salary筛选器失败: {e}")
            raise

    def is_salary_panel_visible(self) -> bool:
        """判断Salary面板是否可见"""
        try:
            return self.page.get_by_role("textbox", name="Min").is_visible(timeout=5000)
        except Exception:
            return False

    def select_salary_period_per_hour(self):
        """选择Per Hour薪资周期"""
        try:
            self.page.get_by_text("Per Hour").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择Per Hour失败: {e}")
            raise

    def select_salary_period_per_month(self):
        """选择Per Month薪资周期"""
        try:
            self.page.get_by_text("Per Month").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择Per Month失败: {e}")
            raise

    def select_salary_period_per_year(self):
        """选择Per Year薪资周期"""
        try:
            self.page.get_by_text("Per Year").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择Per Year失败: {e}")
            raise

    def input_salary_min(self, value: str):
        """输入最低薪资"""
        try:
            self.page.get_by_role("textbox", name="Min").fill(value)
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"输入最低薪资失败: {e}")
            raise

    def input_salary_max(self, value: str):
        """输入最高薪资"""
        try:
            self.page.get_by_role("textbox", name="Max").fill(value)
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"输入最高薪资失败: {e}")
            raise

    def get_salary_min_value(self) -> str:
        """获取最低薪资输入框的值"""
        try:
            return self.page.get_by_role("textbox", name="Min").input_value()
        except Exception as e:
            self.logger.error(f"获取Min值失败: {e}")
            return ""

    def get_salary_max_value(self) -> str:
        """获取最高薪资输入框的值"""
        try:
            return self.page.get_by_role("textbox", name="Max").input_value()
        except Exception as e:
            self.logger.error(f"获取Max值失败: {e}")
            return ""

    # ========== Reset 方法 ==========

    def click_reset(self):
        """点击Reset按钮清除所有筛选"""
        try:
            self.page.get_by_text("Reset", exact=True).click()
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            try:
                self.page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                pass
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击Reset失败: {e}")
            raise

    def is_filters_cleared(self) -> bool:
        """判断所有筛选器是否已清除（URL不包含筛选参数）"""
        try:
            url = self.page.url
            has_filter = any(p in url for p in [
                "attr_60", "attr_61", "attr_62",
                "lowestPrice", "highestPrice", "attr_80",
                "min_price", "max_price"
            ])
            return not has_filter
        except Exception:
            return False

    # ========== 岗位偏好类别 方法 ==========

    def is_job_preference_category_bar_visible(self) -> bool:
        """判断岗位偏好类别标签栏是否可见"""
        try:
            return self.page.get_by_role("link", name="Edit").is_visible(timeout=5000)
        except Exception:
            return False

    def click_job_preference_category(self, category_name: str):
        """点击指定的偏好类别标签"""
        try:
            self.page.get_by_text(category_name).first.click()
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击偏好类别{category_name}失败: {e}")
            raise

    def click_edit_job_preference(self):
        """点击Edit链接跳转到岗位偏好设置"""
        try:
            self.page.get_by_role("link", name="Edit").click()
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception as e:
            self.logger.error(f"点击Edit失败: {e}")
            raise

    # ========== 列表和详情面板方法 ==========

    def is_job_list_visible(self) -> bool:
        """判断职位列表是否可见"""
        try:
            return self.page.locator("[class*='JobListItem'], .listPageJobSection").first.is_visible(
                timeout=5000
            )
        except Exception:
            return False

    def is_end_of_list_visible(self) -> bool:
        """判断是否显示已到底部提示"""
        try:
            return self.page.get_by_text("You've reached the end").is_visible(timeout=3000)
        except Exception:
            return False

    def scroll_to_bottom(self):
        """滚动到页面底部"""
        try:
            # 兼容 IntersectionObserver 触底加载：多段滚动 + 等待高度变化/到底提示
            max_rounds = 8
            last_h = self.page.evaluate(
                "Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)"
            )
            for _ in range(max_rounds):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                try:
                    self.page.wait_for_load_state("networkidle", timeout=6000)
                except Exception:
                    pass
                self.page.wait_for_timeout(1200)
                if self.is_end_of_list_visible():
                    break
                h = self.page.evaluate(
                    "Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)"
                )
                # 高度没变，再给一次机会（有些页面会先加载骨架再扩高）
                if h <= last_h + 10:
                    self.page.wait_for_timeout(1200)
                    h2 = self.page.evaluate(
                        "Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)"
                    )
                    if h2 <= last_h + 10:
                        break
                    h = h2
                last_h = h
        except Exception as e:
            self.logger.error(f"滚动到底部失败: {e}")
            raise

    def _contact_locator_any(self):
        """Contact 入口可能是 button / link，或文案略有差异"""
        return self.page.locator(
            "[class*='detail'] button:has-text('Contact'), "
            "[class*='Detail'] button:has-text('Contact'), "
            "button:has-text('Contact'), "
            "a:has-text('Contact'), "
            "[aria-label*='Contact' i]"
        ).first

    def ensure_job_detail_panel_open(self):
        """确保右侧详情面板已展开：部分环境需先点击列表职位才出现 Contact/Chat。"""
        self.page.wait_for_timeout(1200)
        try:
            if self._contact_locator_any().is_visible(timeout=2500):
                return
        except Exception:
            pass
        card_candidates = (
            self.page.locator("[class*='JobListItem']"),
            self.page.locator(".listPageJobSection [class*='job']"),
            self.page.locator("article").filter(has=self.page.locator("img")),
        )
        for cards in card_candidates:
            try:
                cnt = cards.count()
                for i in range(min(cnt, 3)):
                    cards.nth(i).scroll_into_view_if_needed()
                    cards.nth(i).click(timeout=8000)
                    self.page.wait_for_timeout(2500)
                    try:
                        if self._contact_locator_any().is_visible(timeout=6000):
                            return
                    except Exception:
                        continue
            except Exception:
                continue

    def is_job_detail_panel_visible(self) -> bool:
        """判断右侧职位详情面板是否可见（Contact 可操作入口）"""
        try:
            return self._contact_locator_any().is_visible(timeout=8000)
        except Exception:
            return False

    def click_contact_in_detail(self):
        """点击详情面板中的Contact按钮"""
        try:
            self.page.get_by_role("button", name="Contact").click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击Contact失败: {e}")
            raise

    def is_search_result_list_visible(self) -> bool:
        """判断搜索结果列表是否可见（中间页）"""
        try:
            # 使用 exact=True 精确匹配筛选栏中的 "Best Match" 文字
            return self.page.get_by_text("Best Match", exact=True).is_visible(timeout=5000)
        except Exception:
            return False

    def get_first_job_title_in_search_result(self) -> str:
        """获取搜索结果中第一条职位的标题"""
        try:
            first_result = self.page.locator("a[href*='/city/cate-']").first
            return first_result.text_content() or ""
        except Exception as e:
            self.logger.error(f"获取第一条搜索结果标题失败: {e}")
            return ""

    def is_filter_badge_visible(self) -> bool:
        """判断Filter徽章是否可见（搜索中间页）"""
        try:
            return self.page.get_by_text("Filter", exact=True).is_visible(timeout=3000)
        except Exception:
            return False
