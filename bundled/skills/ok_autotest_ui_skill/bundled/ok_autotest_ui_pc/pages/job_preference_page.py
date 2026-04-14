# pages/job_preference_page.py
"""
Job Preferences 职位偏好设置页面对象
入口：新加坡站首页 → 点击 Jobs 金刚位图标 → 跳转至此中间态表单页
URL：https://sgpub.58v5.cn/biz/en/jobPreference?showSkip=1&returnUrl=...
"""
from pages.base_page import BasePage
from utils.logger import setup_logger


class JobPreferencePage(BasePage):
    """Job Preferences 职位偏好设置页面（静默执行）"""

    # ========== URL 常量 ==========
    JOB_PREF_FULL_URL = (
        "https://sgpub.58v5.cn/biz/en/jobPreference"
        "?showSkip=1"
        "&returnUrl=https%3A%2F%2Fsg.58v5.cn%2Fen%2Fcity-singapore%2Fcate-jobs%2F%3FiconSource%3Djobs"
    )
    JOBS_LIST_URL_PATTERN = "**/cate-jobs/**"

    # ========== 页面元素选择器（Playwright 语法，来自 MCP 实测）==========
    PAGE_HEADING = "h2:has-text('Job Preferences')"
    SKIP_LINK = "a:has-text('Skip')"
    BACK_BUTTON = "button:has-text('Back')"
    CONTINUE_BUTTON = "button:has-text('Continue')"
    JOB_FUNCTIONS_TRIGGER = "text=Select preferred job function"
    LOCATION_TRIGGER = "text=Select preferred work"
    # Pay type 触发器是 div[role='button']，不是真正的 <button> 标签
    PAY_TYPE_BUTTON = "[role='button']:has-text('Select pay type')"
    PAY_TYPE_BUTTON_BACKUP = "[class*='SingleSelectFakeInput']:has-text('pay type')"
    PAY_TYPE_BUTTON_ALT = "[role='button']:has-text('Yearly')"
    VALIDATION_ERROR_TEXT = "Don\u2019t leave this field empty."
    # 注意：页面用弯撇号（Unicode \u2019）而非普通单引号
    VALIDATION_ERROR_SELECTOR = "text=Don\u2019t leave this field empty."
    VALIDATION_ERROR_SELECTOR_ALT = "text=Don\u2019t leave"

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    def navigate_to_job_preferences(self):
        """直接导航至 Job Preferences 页面"""
        try:
            self.goto(self.JOB_PREF_FULL_URL, timeout=20000)
            self.wait_for_page_load(state="domcontentloaded")
        except Exception as e:
            self.logger.error(f"导航至 Job Preferences 失败: {e}")
            raise

    def wait_for_page_heading(self):
        """等待 Job Preferences 标题出现（兼容不同标签）"""
        selectors = [
            self.PAGE_HEADING,                                 # h2:has-text('Job Preferences')
            "h1:has-text('Job Preferences')",
            "h3:has-text('Job Preferences')",
            "text=Job Preferences",                            # 任意元素含此文本
            self.JOB_FUNCTIONS_TRIGGER,                        # 表单已加载的标志
            self.CONTINUE_BUTTON,                              # 另一个表单加载标志
        ]
        for sel in selectors:
            try:
                self.wait_for_selector(sel, timeout=5000)
                self.logger.info(f"✓ 找到 Job Preferences 页面元素: {sel}")
                return
            except Exception:
                continue
        # 最终兜底：通过 URL 判断
        if "jobPreference" in self.page.url:
            self.logger.info("✓ 页面 URL 包含 jobPreference，视为已进入表单页")
            return
        current_url = self.page.url
        self.logger.error(f"等待 Job Preferences 页面超时，当前 URL: {current_url}")
        raise Exception(f"未能进入 Job Preferences 页面，当前 URL: {current_url}")

    def wait_for_jobs_list_page(self):
        """等待跳转至职位列表页"""
        try:
            self.wait_for_url(self.JOBS_LIST_URL_PATTERN, timeout=15000)
        except Exception as e:
            self.logger.error(f"等待职位列表页超时: {e}")
            raise

    def click_skip(self):
        """点击 Skip 链接"""
        try:
            self.wait_for_selector(self.SKIP_LINK, timeout=8000)
            self.click(self.SKIP_LINK)
        except Exception as e:
            self.logger.error(f"点击 Skip 失败: {e}")
            raise

    def click_back(self):
        """点击 Back 按钮"""
        try:
            self.wait_for_selector(self.BACK_BUTTON, timeout=8000)
            self.click(self.BACK_BUTTON)
        except Exception as e:
            self.logger.error(f"点击 Back 失败: {e}")
            raise

    def click_continue(self):
        """点击 Continue 按钮"""
        try:
            self.wait_for_selector(self.CONTINUE_BUTTON, timeout=8000)
            self.click(self.CONTINUE_BUTTON)
        except Exception as e:
            self.logger.error(f"点击 Continue 失败: {e}")
            raise

    def get_validation_error_count(self) -> int:
        """获取当前显示的校验错误数量"""
        try:
            c = self.page.locator(self.VALIDATION_ERROR_SELECTOR).count()
            if c > 0:
                return c
            return self.page.locator(self.VALIDATION_ERROR_SELECTOR_ALT).count()
        except Exception:
            return 0

    def is_skip_link_visible(self) -> bool:
        """判断 Skip 链接是否可见"""
        return self.is_visible(self.SKIP_LINK, timeout=3000)

    def select_job_function(self, category: str, sub_category: str):
        """选择 Job Function（打开面板→选分类→选子分类→确认）"""
        try:
            self.wait_for_selector(self.JOB_FUNCTIONS_TRIGGER, timeout=8000)
            self.page.locator(self.JOB_FUNCTIONS_TRIGGER).first.click()
            self.page.wait_for_timeout(400)
            self.page.get_by_text(category, exact=True).first.click()
            self.page.wait_for_timeout(600)
            self.page.get_by_text(sub_category, exact=True).first.click()
            self.wait_for_selector("button:has-text('Confirm')", timeout=5000)
            self.click("button:has-text('Confirm')")
        except Exception as e:
            self.logger.error(f"选择 Job Function 失败: {e}")
            raise

    def select_location_full(self, location_name: str):
        """选择 Location（打开面板→勾选→确认）"""
        try:
            self.wait_for_selector(self.LOCATION_TRIGGER, timeout=8000)
            self.page.locator(self.LOCATION_TRIGGER).first.click()
            self.page.wait_for_timeout(300)
            self.page.get_by_role("checkbox", name=location_name, exact=True).click()
            self.wait_for_selector("button:has-text('Confirm')", timeout=5000)
            self.click("button:has-text('Confirm')")
        except Exception as e:
            self.logger.error(f"选择 Location 失败: {e}")
            raise

    def set_salary(self, pay_type: str, amount: str):
        """设置薪资（选择 Pay type + 输入金额）"""
        try:
            for selector in [self.PAY_TYPE_BUTTON, self.PAY_TYPE_BUTTON_BACKUP, self.PAY_TYPE_BUTTON_ALT]:
                try:
                    self.page.locator(selector).first.wait_for(state="visible", timeout=3000)
                    self.page.locator(selector).first.click()
                    break
                except Exception:
                    continue
            else:
                raise Exception("未找到 Pay type 按钮")
            self.page.wait_for_timeout(300)
            self.page.get_by_role("checkbox", name=pay_type, exact=True).click()
            self.page.wait_for_timeout(200)
            self.page.locator("form").get_by_role("textbox").fill(amount)
        except Exception as e:
            self.logger.error(f"设置薪资失败: {e}")
            raise

    def select_locations(self, location_names: list):
        """选择多个 Location（打开面板→勾选多个→确认）"""
        try:
            self.wait_for_selector(self.LOCATION_TRIGGER, timeout=8000)
            self.page.locator(self.LOCATION_TRIGGER).first.click()
            self.page.wait_for_timeout(300)
            for name in location_names:
                self.page.get_by_role("checkbox", name=name, exact=True).click()
                self.page.wait_for_timeout(150)
            self.wait_for_selector("button:has-text('Confirm')", timeout=5000)
            self.click("button:has-text('Confirm')")
        except Exception as e:
            self.logger.error(f"选择 Location 失败: {e}")
            raise

    def get_job_functions_trigger_text(self) -> str:
        """获取 Job Functions 触发器文案"""
        try:
            self.wait_for_selector(self.JOB_FUNCTIONS_TRIGGER, timeout=5000)
            return self.page.locator(self.JOB_FUNCTIONS_TRIGGER).first.inner_text()
        except Exception:
            return ""

    def get_location_trigger_text(self) -> str:
        """获取 Location 触发器文案"""
        try:
            self.wait_for_selector(self.LOCATION_TRIGGER, timeout=5000)
            return self.page.locator(self.LOCATION_TRIGGER).first.inner_text()
        except Exception:
            return ""

    def click_job_functions_trigger(self):
        """仅点击 Job Functions 触发器展开面板"""
        try:
            self.wait_for_selector(self.JOB_FUNCTIONS_TRIGGER, timeout=8000)
            self.page.locator(self.JOB_FUNCTIONS_TRIGGER).first.click()
            self.page.wait_for_timeout(400)
        except Exception as e:
            self.logger.error(f"点击 Job Functions 触发器失败: {e}")
            raise

    def click_location_trigger(self):
        """仅点击 Location 触发器展开面板"""
        try:
            self.wait_for_selector(self.LOCATION_TRIGGER, timeout=8000)
            self.page.locator(self.LOCATION_TRIGGER).first.click()
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"点击 Location 触发器失败: {e}")
            raise

    def click_confirm_in_panel(self):
        """点击面板内 Confirm 按钮"""
        try:
            self.wait_for_selector("button:has-text('Confirm')", timeout=5000)
            self.click("button:has-text('Confirm')")
        except Exception as e:
            self.logger.error(f"点击 Confirm 失败: {e}")
            raise

    def click_clear_in_panel(self):
        """点击面板内 Clear 按钮"""
        try:
            if self.is_visible("button:has-text('Clear')", timeout=3000):
                self.click("button:has-text('Clear')")
        except Exception:
            pass

    def clear_job_functions_selection(self):
        """清空 Job Functions 已选项（打开面板→Clear→Confirm）"""
        try:
            # 尝试找到触发器（无论是 "Select..." 还是已选项目数量的文本）
            trigger_selectors = [
                self.JOB_FUNCTIONS_TRIGGER,
                "[class*='trigger']:has-text('Job')",
                "[class*='select']:has-text('Job')",
                "text=Job function",
            ]
            clicked = False
            for sel in trigger_selectors:
                try:
                    if self.is_visible(sel, timeout=2000):
                        self.page.locator(sel).first.click()
                        clicked = True
                        break
                except Exception:
                    continue
            if not clicked:
                # 尝试直接点击 Job Functions 区域的任意可点击元素
                self.page.locator("[class*='jobFunction'], [class*='job-function']").first.click()
            self.page.wait_for_timeout(400)
            self.click_clear_in_panel()
            self.page.wait_for_timeout(200)
            self.click_confirm_in_panel()
            self.page.wait_for_timeout(400)
        except Exception as e:
            self.logger.warning(f"清空 Job Functions 失败（可忽略）: {e}")

    def clear_location_selection(self):
        """清空 Location 已选项（打开面板→Clear→Confirm）"""
        try:
            trigger_selectors = [
                self.LOCATION_TRIGGER,
                "[class*='trigger']:has-text('Location')",
                "[class*='select']:has-text('Location')",
                "text=Location",
            ]
            clicked = False
            for sel in trigger_selectors:
                try:
                    if self.is_visible(sel, timeout=2000):
                        self.page.locator(sel).first.click()
                        clicked = True
                        break
                except Exception:
                    continue
            if not clicked:
                self.page.locator("[class*='location']").first.click()
            self.page.wait_for_timeout(400)
            self.click_clear_in_panel()
            self.page.wait_for_timeout(200)
            self.click_confirm_in_panel()
            self.page.wait_for_timeout(400)
        except Exception as e:
            self.logger.warning(f"清空 Location 失败（可忽略）: {e}")

    def close_panel_by_escape(self):
        """按 ESC 关闭面板"""
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(300)

    # ========== Pay type 专用方法 ==========

    def get_pay_type_button_text(self) -> str:
        """获取 Pay type 按钮当前文案（如 'Select pay type Monthly'）"""
        try:
            for selector in [self.PAY_TYPE_BUTTON, self.PAY_TYPE_BUTTON_ALT]:
                loc = self.page.locator(selector)
                if loc.count() > 0:
                    return loc.first.inner_text()
            return ""
        except Exception:
            return ""

    def select_pay_type(self, pay_type: str):
        """仅切换 Pay type（打开面板→勾选目标项→面板自动收起）

        Args:
            pay_type: "Yearly" | "Monthly" | "Hourly"
        """
        try:
            for selector in [self.PAY_TYPE_BUTTON, self.PAY_TYPE_BUTTON_BACKUP, self.PAY_TYPE_BUTTON_ALT]:
                try:
                    self.page.locator(selector).first.wait_for(state="visible", timeout=3000)
                    self.page.locator(selector).first.click()
                    break
                except Exception:
                    continue
            else:
                raise Exception("未找到 Pay type 按钮")
            self.page.wait_for_timeout(300)
            self.page.get_by_role("checkbox", name=pay_type, exact=True).click()
            self.page.wait_for_timeout(400)
        except Exception as e:
            self.logger.error(f"切换 Pay type 至 {pay_type} 失败: {e}")
            raise

    def clear_salary_amount(self):
        """清空薪资金额输入框"""
        try:
            salary_input = self.page.locator("form").get_by_role("textbox")
            salary_input.first.click(click_count=3)
            salary_input.first.fill("")
            self.page.wait_for_timeout(200)
        except Exception as e:
            self.logger.error(f"清空薪资金额失败: {e}")
            raise

    def input_salary_amount(self, amount: str):
        """输入薪资金额（覆盖已有值）"""
        try:
            salary_input = self.page.locator("form").get_by_role("textbox")
            salary_input.first.fill(amount)
            self.page.wait_for_timeout(200)
        except Exception as e:
            self.logger.error(f"输入薪资金额失败: {e}")
            raise

    def type_salary_amount_sequentially(self, amount: str, delay: int = 80):
        """逐键输入薪资金额（模拟真实键盘，用于验证字符拦截行为）

        与 input_salary_amount 的区别：press_sequentially 会触发 keydown/keypress/input 事件链，
        能真实验证输入框对非法字符的拦截逻辑。
        """
        try:
            salary_input = self.page.locator("form").get_by_role("textbox")
            salary_input.first.click(click_count=3)
            salary_input.first.fill("")
            salary_input.first.press_sequentially(amount, delay=delay)
            self.page.wait_for_timeout(200)
        except Exception as e:
            self.logger.error(f"逐键输入薪资金额失败: {e}")
            raise

    def get_salary_input_value(self) -> str:
        """获取薪资输入框当前值"""
        try:
            return self.page.locator("form").get_by_role("textbox").first.input_value()
        except Exception as e:
            self.logger.error(f"获取薪资输入框值失败: {e}")
            return ""

    def blur_salary_input(self):
        """点击页面标题使薪资输入框失焦"""
        try:
            self.page.locator("h2:has-text('Job Preferences')").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"薪资输入框失焦失败: {e}")
            raise

    def paste_to_salary_input(self, text: str):
        """向薪资输入框粘贴文本（通过 ClipboardEvent 模拟）"""
        try:
            salary_input = self.page.locator("form").get_by_role("textbox")
            salary_input.first.click(click_count=3)
            salary_input.first.fill("")
            self.page.evaluate(
                """(text) => {
                    const clipData = new DataTransfer();
                    clipData.setData('text/plain', text);
                    const pasteEvent = new ClipboardEvent('paste', {
                        clipboardData: clipData,
                        bubbles: true,
                        cancelable: true,
                    });
                    document.activeElement.dispatchEvent(pasteEvent);
                }""",
                text,
            )
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"粘贴至薪资输入框失败: {e}")
            raise

    def get_salary_error_visible(self) -> bool:
        """判断 Salary 区域必填错误提示是否可见"""
        try:
            return self.page.locator(self.VALIDATION_ERROR_SELECTOR).count() > 0
        except Exception:
            return False

    # ========== AE Edit 专用方法 ==========

    def navigate_to_edit_page(self, edit_url: str, return_url: str):
        """导航到 AE Job Preferences 编辑页（含 returnUrl 参数），带重试"""
        full_url = f"{edit_url}?returnUrl={return_url}"
        for attempt in range(3):
            try:
                self.page.goto(full_url, wait_until="domcontentloaded")
                self.page.wait_for_load_state("domcontentloaded", timeout=15000)
                self.page.wait_for_timeout(2000)
                return
            except Exception as e:
                if attempt == 2:
                    self.logger.error(f"导航到编辑页失败（已重试3次）: {e}")
                    raise
                self.page.wait_for_timeout(2000)

    def is_job_functions_trigger_visible(self) -> bool:
        """判断 Job Functions 触发器是否可见"""
        try:
            return self.page.locator(self.JOB_FUNCTIONS_TRIGGER).first.is_visible(timeout=5000)
        except Exception:
            return False

    def get_job_functions_count_text(self) -> str:
        """获取 Job Functions 触发器中的计数文字（如 '(5/10)'）"""
        try:
            return self.page.locator(self.JOB_FUNCTIONS_TRIGGER).first.inner_text()
        except Exception:
            return ""

    def is_location_trigger_visible(self) -> bool:
        """判断 Location 触发器是否可见"""
        try:
            return self.page.locator(self.LOCATION_TRIGGER).first.is_visible(timeout=5000)
        except Exception:
            return False

    def get_location_count_text(self) -> str:
        """获取 Location 触发器中的计数文字（如 '(1/5)'）"""
        try:
            return self.page.locator(self.LOCATION_TRIGGER).first.inner_text()
        except Exception:
            return ""

    def get_aed_prefix_text(self) -> str:
        """获取 Salary 区域 AED 货币前缀文本"""
        try:
            return self.page.get_by_text("AED", exact=True).first.inner_text()
        except Exception:
            return ""

    def is_aed_prefix_visible(self) -> bool:
        """判断 AED 货币前缀是否可见"""
        try:
            return self.page.get_by_text("AED", exact=True).first.is_visible(timeout=5000)
        except Exception:
            return False

    def is_sg_currency_prefix_visible(self) -> bool:
        """判断 S$ 货币前缀是否可见（AE站不应出现）"""
        try:
            return self.page.get_by_text("S$").count() > 0
        except Exception:
            return False

    def get_salary_input_raw_value(self) -> str:
        """获取 Salary 输入框原始值"""
        try:
            return self.page.locator("form").get_by_role("textbox").first.input_value()
        except Exception:
            return ""

    def is_pay_type_yearly_visible(self) -> bool:
        """判断 Pay type 是否显示 Yearly（已回填）"""
        try:
            return self.page.get_by_role("button", name="Select pay type Yearly").first.is_visible(timeout=3000)
        except Exception:
            return False

    def is_workplace_type_heading_visible(self) -> bool:
        """判断 Workplace Type 标题是否可见"""
        try:
            return self.page.get_by_role("heading", name="Workplace Type").first.is_visible(timeout=5000)
        except Exception:
            return False

    def is_job_type_heading_visible(self) -> bool:
        """判断 Job Type 标题是否可见"""
        try:
            return self.page.get_by_role("heading", name="Job Type").first.is_visible(timeout=5000)
        except Exception:
            return False

    def is_workplace_checkbox_checked(self, name: str) -> bool:
        """判断指定 Workplace Type checkbox 是否已勾选"""
        try:
            return self.page.get_by_role("checkbox", name=name).is_checked()
        except Exception:
            return False

    def click_continue(self):
        """点击 Continue 按钮"""
        try:
            self.page.get_by_role("button", name="Continue").click()
        except Exception as e:
            self.logger.error(f"点击 Continue 失败: {e}")
            raise

    def click_back(self):
        """点击 Back 按钮"""
        try:
            self.page.get_by_role("button", name="Back").click()
        except Exception as e:
            self.logger.error(f"点击 Back 失败: {e}")
            raise

    def is_edit_link_visible(self) -> bool:
        """判断 Jobs 列表页 Edit 链接是否可见"""
        try:
            return self.page.get_by_role("link", name="Edit").is_visible(timeout=8000)
        except Exception:
            return False

    def is_oil_gas_category_visible(self) -> bool:
        """判断 Job Functions 面板左栏是否有 Oil & Gas 分类"""
        try:
            return self.page.locator("form").get_by_text("Oil & Gas", exact=True).first.is_visible(timeout=5000)
        except Exception:
            return False

    def is_skilled_trades_category_visible(self) -> bool:
        """判断 Job Functions 面板左栏是否有 Skilled Trades 分类"""
        try:
            return self.page.locator("form").get_by_text("Skilled Trades", exact=True).first.is_visible(timeout=5000)
        except Exception:
            return False

    def click_oil_gas_and_select_drilling(self):
        """点击 Oil & Gas 分类并选择 Drilling 子分类"""
        try:
            self.page.locator("form").get_by_text("Oil & Gas", exact=True).first.click()
            self.page.wait_for_timeout(600)
            drilling = self.page.get_by_text("Oil & Gas - Drilling").first
            drilling.wait_for(state="visible", timeout=5000)
            drilling.click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择 Oil & Gas Drilling 失败: {e}")
            raise

    def click_confirm_and_get_trigger_text(self) -> str:
        """点击 Confirm 后返回 Job Functions 触发器当前文本"""
        try:
            self.page.get_by_role("button", name="Confirm").click()
            self.page.wait_for_timeout(500)
            return self.page.locator(self.JOB_FUNCTIONS_TRIGGER).first.inner_text()
        except Exception as e:
            self.logger.error(f"点击 Confirm 并读取触发器文本失败: {e}")
            return ""

    def is_location_city_visible(self, city_name: str) -> bool:
        """判断 Location 面板中指定城市 checkbox 是否可见"""
        try:
            return self.page.get_by_role("checkbox", name=city_name).is_visible(timeout=5000)
        except Exception:
            return False

    def has_location_city(self, city_name: str) -> bool:
        """判断 Location 面板中是否存在指定城市 checkbox（用于反向验证）"""
        try:
            return self.page.get_by_role("checkbox", name=city_name).count() > 0
        except Exception:
            return False

    def click_workplace_hybrid_toggle(self):
        """点击 Hybrid checkbox（触发修改状态）"""
        try:
            self.page.get_by_role("checkbox", name="Hybrid").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击 Hybrid checkbox 失败: {e}")
            raise

    def is_unsaved_changes_dialog_visible(self) -> bool:
        """判断 Unsaved Changes 确认弹窗是否可见"""
        try:
            return self.page.get_by_role("dialog").is_visible(timeout=5000)
        except Exception:
            return False

    def has_unsaved_changes_title(self) -> bool:
        """判断弹窗中是否有 'Unsaved Changes' 标题文字"""
        try:
            return self.page.get_by_text("Unsaved Changes").first.is_visible(timeout=3000)
        except Exception:
            return False

    def click_discard_in_dialog(self):
        """点击 Unsaved Changes 弹窗中的 Discard 按钮"""
        try:
            self.page.get_by_role("button", name="Discard").click()
        except Exception as e:
            self.logger.error(f"点击 Discard 失败: {e}")
            raise

    def wait_for_navigation_away_from_edit(self, timeout: int = 10000):
        """等待页面从编辑页离开（URL 不含 jobPreference）"""
        try:
            self.page.wait_for_url(lambda url: "jobPreference" not in url, timeout=timeout)
        except Exception:
            pass
        self.page.wait_for_load_state("domcontentloaded", timeout=10000)
        self.page.wait_for_timeout(2000)

    def is_on_ae_jobs_page(self) -> bool:
        """判断当前是否在 AE 站 Jobs 相关页面"""
        current_url = self.page.url
        if current_url == "about:blank":
            self.page.wait_for_timeout(3000)
            current_url = self.page.url
        return "ae.58v5.cn" in current_url

    def is_on_jobs_list_page(self) -> bool:
        """判断当前是否在 Jobs 列表页（含 cate-jobs）"""
        current_url = self.page.url
        if current_url == "about:blank":
            self.page.wait_for_timeout(3000)
            current_url = self.page.url
        return "cate-jobs" in current_url

    def get_current_url(self) -> str:
        """获取当前页面 URL（处理 about:blank 瞬态）"""
        url = self.page.url
        if url == "about:blank":
            self.page.wait_for_timeout(3000)
            url = self.page.url
        return url

    def navigate_to_tampered_edit_page(self, edit_url: str, evil_return_url: str = "https%3A%2F%2Fevil.example.com"):
        """先访问合法编辑页建立合法 Cookie，再篡改 returnUrl 为恶意域名"""
        try:
            self.page.goto(f"{edit_url}?returnUrl=https%3A%2F%2Fae.58v5.cn%2Fen%2Fcity%2Fcate-jobs%2F",
                           wait_until="domcontentloaded")
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            self.page.wait_for_timeout(2000)
            tampered_url = f"{edit_url}?returnUrl={evil_return_url}"
            self.page.goto(tampered_url, wait_until="domcontentloaded")
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"导航至篡改 URL 失败: {e}")
            raise

    def is_evil_domain_in_url(self) -> bool:
        """判断当前 URL 是否跳转至 evil.example.com"""
        return "evil.example.com" in self.page.url

    def is_legitimate_domain_in_url(self) -> bool:
        """判断当前 URL 是否在合法域名（58v5.cn）"""
        return "58v5.cn" in self.page.url

    def is_on_edit_page_with_legitimate_return_url(self) -> bool:
        """判断是否停留在含合法 returnUrl 的编辑页（Open Redirect 防护行为之一）"""
        url = self.page.url
        return "jobPreference" in url and "evil.example.com" not in url

    def reload_and_wait(self):
        """刷新页面并等待加载完成"""
        try:
            self.page.reload()
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"刷新页面失败: {e}")
            raise

    def clear_all_cookies_and_storage(self):
        """通过 Playwright API 清除所有 Cookie（含 HttpOnly）和 localStorage，模拟登录态过期"""
        try:
            self.page.context.clear_cookies()
            self.page.evaluate("() => { try { localStorage.clear(); sessionStorage.clear(); } catch(e) {} }")
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"清除 Cookie 和 localStorage 失败: {e}")
            raise

    def goto_url_after_cookie_clear(self, url: str):
        """Cookie 清除后访问指定 URL（捕获导航异常，允许继续执行后续断言）"""
        try:
            self.page.goto(url, wait_until="domcontentloaded")
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.warning(f"访问 URL 时出错（Cookie 清除后可能重定向）: {e}")

    def is_redirected_to_login(self) -> bool:
        """判断当前是否已重定向至登录页面或显示登录入口"""
        current_url = self.page.url
        if "login" in current_url.lower() or "signin" in current_url.lower():
            return True
        try:
            if self.page.get_by_role("button", name="Log in").is_visible(timeout=3000):
                return True
        except Exception:
            pass
        try:
            if self.page.get_by_text("Log in / Register").is_visible(timeout=3000):
                return True
        except Exception:
            pass
        return False

    def is_edit_form_heading_visible(self) -> bool:
        """判断编辑表单标题 'Job Preferences' 是否可见（用于 Cookie 清除后的反向断言）"""
        try:
            return self.page.get_by_role("heading", name="Job Preferences").is_visible(timeout=3000)
        except Exception:
            return False

    def navigate_to_jobs_list_with_retry(self, jobs_list_url: str):
        """带重试的 Jobs 列表页导航（处理偶发 HTTP 错误）"""
        for attempt in range(3):
            try:
                self.page.goto(jobs_list_url, wait_until="domcontentloaded")
                self.page.wait_for_load_state("domcontentloaded", timeout=15000)
                self.page.wait_for_timeout(1500)
                return
            except Exception as e:
                if attempt == 2:
                    self.logger.error(f"导航到 Jobs 列表页失败（已重试3次）: {e}")
                    raise
                self.page.wait_for_timeout(3000)

    def click_edit_link(self):
        """点击 Jobs 列表页的 Edit 链接"""
        try:
            self.page.get_by_role("link", name="Edit").click()
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击 Edit 链接失败: {e}")
            raise

    def is_url_contains(self, keyword: str) -> bool:
        """判断当前 URL 是否包含指定关键字"""
        return keyword in self.page.url

    def get_no_unsaved_dialog_count(self) -> int:
        """获取 dialog 弹窗数量（用于验证无弹窗）"""
        try:
            return self.page.get_by_role("dialog").count()
        except Exception:
            return 0
