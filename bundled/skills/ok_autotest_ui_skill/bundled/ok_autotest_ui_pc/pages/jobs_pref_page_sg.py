# pages/jobs_pref_page_sg.py
"""
SG站 岗位偏好页（Job Preferences）Page Object
基于MCP Playwright录制生成

对应测试用例: ok-sg-JobPref-Submit-测试用例-20260319.md (TC001-TC008)

MCP实测确认的真实选择器：
- Jobs金刚位: page.getByRole('link', { name: 'Jobs Jobs' })
- Job Functions入口: page.getByText('Select preferred job function')
- Job Functions一级分类（ICT）: page.getByText('Information & Communication')
- Job Functions二级（Developers）: page.getByText('Developers/Programmers')
- Job Functions面板Confirm: page.getByRole('button', { name: 'Confirm' })
- Location入口: page.getByText('Select preferred work')
- Singapore checkbox: page.getByRole('checkbox', { name: 'Singapore', exact: True })
- Location面板Confirm: page.getByRole('button', { name: 'Confirm' })
- Pay Type按钮: page.getByRole('button', { name: 'Select pay type ...' })
- Monthly checkbox: page.getByRole('checkbox', { name: 'Monthly' })
- Salary金额输入框: page.locator('form').get_by_role('textbox')
- Onsite checkbox: page.getByRole('checkbox', { name: 'Onsite' })
- Remote checkbox: page.getByRole('checkbox', { name: 'Remote' })
- Hybrid checkbox: page.getByRole('checkbox', { name: 'Hybrid' })
- Full-time checkbox: page.getByRole('checkbox', { name: 'Full-time' })
- Continue（提交）: page.getByRole('button', { name: 'Continue' })
- Skip: page.getByRole('link', { name: 'Skip' })

提交成功跳转URL: https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs
"""
from pages.base_page import BasePage
from utils.logger import setup_logger


class JobsPrefPageSG(BasePage):
    """
    SG站 岗位偏好页 Page Object
    目标URL: https://sgpub.58v5.cn/biz/en/jobPreference?showSkip=1&returnUrl=...
    """

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    # ========== 导航方法 ==========

    def navigate_to_jobs_pref_via_home(self, base_url: str):
        """
        从首页点击Jobs金刚位进入岗位偏好页。

        降级策略（按优先级）：
        1. 点击Jobs金刚位，若直接跳转到 jobPreference 页则结束。
        2. 若跳转到 cate-jobs（账号已有偏好）：
           a. 尝试找 Edit 链接点击进入偏好页。
           b. 尝试找 "+ Add Job Preference" 按钮点击进入偏好页。
        注意：不使用直接 goto biz/en/jobPreference，因为该 biz 子域要求独立认证。
        """
        try:
            self.page.goto(f"{base_url}/en/city-singapore/", wait_until="domcontentloaded", timeout=30000)
            try:
                self.page.wait_for_load_state("networkidle", timeout=6000)
            except Exception:
                pass
            self.page.get_by_role("link", name="Jobs Jobs").click()
            try:
                self.page.wait_for_url("**/jobPreference**", timeout=8000)
                self.logger.info("✓ 点击Jobs金刚位后直接进入岗位偏好页")
                return
            except Exception:
                pass

            # 已跳转到 cate-jobs（账号已有偏好或无偏好），尝试 Edit 链接
            current_url = self.page.url
            self.logger.info(f"⚠️ 点击Jobs金刚位后当前URL: {current_url}，尝试进入偏好页")

            # 尝试 Edit 链接（已有偏好的账号）
            try:
                edit_link = self.page.get_by_role("link", name="Edit").first
                edit_link.wait_for(state="visible", timeout=3000)
                edit_link.click()
                self.page.wait_for_url("**/jobPreference**", timeout=10000)
                self.logger.info("✓ 通过 Edit 链接进入岗位偏好页")
                return
            except Exception:
                self.logger.info("⚠️ Edit 链接不可用，尝试 Add Job Preference 入口")

            # 尝试 "+ Add Job Preference" 按钮（无偏好的账号，DB清理后前端未刷新的情况）
            try:
                # 先刷新页面确保 cate-jobs 是最新状态
                self.page.goto(f"{base_url}/en/city-singapore/cate-jobs/?iconSource=jobs",
                               wait_until="domcontentloaded", timeout=30000)
                try:
                    self.page.wait_for_load_state("networkidle", timeout=6000)
                except Exception:
                    pass
                self.page.screenshot(path="debug_cate_jobs_in_test.png")
                self.logger.info(f"cate-jobs 刷新后URL: {self.page.url}，截图已保存到 debug_cate_jobs_in_test.png")
                # 尝试多种选择器找 Add Job Preference 入口
                add_pref_btn = self.page.get_by_text("Add Job Preference").first
                add_pref_btn.wait_for(state="visible", timeout=8000)
                add_pref_btn.click()
                self.page.wait_for_url("**/jobPreference**", timeout=15000)
                self.logger.info("✓ 通过 Add Job Preference 入口进入偏好页")
                return
            except Exception as e:
                self.logger.info(f"⚠️ Add Job Preference 入口也不可用: {e}")

            raise RuntimeError(
                f"无法进入岗位偏好页，当前URL: {self.page.url}，"
                "所有入口均失败，请检查测试账号状态和页面结构"
            )
        except Exception as e:
            self.logger.error(f"从首页进入岗位偏好页失败: {e}")
            raise

    def is_on_job_pref_page(self) -> bool:
        """判断当前是否在岗位偏好页"""
        try:
            return "jobPreference" in self.page.url
        except Exception:
            return False

    def get_current_url(self) -> str:
        """获取当前URL"""
        try:
            return self.page.url
        except Exception as e:
            self.logger.error(f"获取URL失败: {e}")
            raise

    # ========== Job Functions 方法 ==========

    def open_job_functions_panel(self):
        """点击打开 Job Functions 选择面板"""
        try:
            self.page.get_by_text("Select preferred job function").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"打开Job Functions面板失败: {e}")
            raise

    def select_job_function(self, category: str, subcategory: str):
        """
        选择 Job Function（两级级联选择）

        Args:
            category: 一级分类名称（如 "Information & Communication"）
            subcategory: 二级分类名称（如 "Developers/Programmers"）
        """
        try:
            self.page.get_by_text(category).click()
            self.page.wait_for_timeout(600)
            self.page.get_by_text(subcategory).click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择Job Function失败（{category} > {subcategory}）: {e}")
            raise

    def confirm_job_functions(self):
        """点击 Job Functions 面板的 Confirm 按钮"""
        try:
            self.page.get_by_role("button", name="Confirm").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"确认Job Functions失败: {e}")
            raise

    # ========== Location 方法 ==========

    def open_location_panel(self):
        """点击打开 Location 选择面板"""
        try:
            self.page.get_by_text("Select preferred work").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"打开Location面板失败: {e}")
            raise

    def select_location(self, location_name: str):
        """
        勾选指定地点

        Args:
            location_name: 地点名称（如 "Singapore"）
        """
        try:
            self.page.get_by_role("checkbox", name=location_name, exact=True).click()
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"选择Location失败（{location_name}）: {e}")
            raise

    def confirm_location(self):
        """点击 Location 面板的 Confirm 按钮"""
        try:
            self.page.get_by_role("button", name="Confirm").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"确认Location失败: {e}")
            raise

    # ========== Salary 方法 ==========

    def open_pay_type_dropdown(self):
        """
        点击 Pay Type 按钮打开下拉。

        按钮文字随当前值变化（无选择时含 "Select pay type"，已选后为 "Yearly"/"Monthly"/"Hourly"），
        使用 form 内第一个 button（Pay Type 下拉触发器）作为稳定定位目标。
        """
        try:
            # form 内第一个 button 就是 Pay Type 下拉按钮（位于 salary 输入框左侧）
            pay_btn = self.page.locator("form").get_by_role("button").first
            pay_btn.wait_for(state="visible", timeout=5000)
            pay_btn.click()
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"打开Pay Type下拉失败: {e}")
            raise

    def select_pay_type(self, pay_type: str):
        """
        选择薪资周期

        Args:
            pay_type: "Yearly" | "Monthly" | "Hourly"
        """
        try:
            self.page.get_by_role("checkbox", name=pay_type).click()
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"选择Pay Type失败（{pay_type}）: {e}")
            raise

    def input_salary_amount(self, amount: str):
        """
        输入薪资金额

        Args:
            amount: 金额字符串（如 "5000"）
        """
        try:
            self.page.locator("form").get_by_role("textbox").click()
            self.page.locator("form").get_by_role("textbox").fill(amount)
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"输入Salary金额失败: {e}")
            raise

    # ========== Workplace Type 方法 ==========

    def select_workplace_type(self, workplace_type: str):
        """
        勾选 Workplace Type

        Args:
            workplace_type: "Onsite" | "Remote" | "Hybrid"
        """
        try:
            self.page.get_by_role("checkbox", name=workplace_type).click()
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"选择Workplace Type失败（{workplace_type}）: {e}")
            raise

    # ========== Job Type 方法 ==========

    def select_job_type(self, job_type: str):
        """
        勾选 Job Type

        Args:
            job_type: "Full-time" | "Part-time" | "Contract" | "Internship" | "Temporary"
        """
        try:
            self.page.get_by_role("checkbox", name=job_type).click()
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"选择Job Type失败（{job_type}）: {e}")
            raise

    # ========== 提交方法 ==========

    def click_continue(self):
        """点击 Continue 按钮提交岗位偏好"""
        try:
            self.page.get_by_role("button", name="Continue").click()
        except Exception as e:
            self.logger.error(f"点击Continue失败: {e}")
            raise

    def click_back(self):
        """点击 Back 按钮"""
        try:
            self.page.get_by_role("button", name="Back").click()
        except Exception as e:
            self.logger.error(f"点击Back失败: {e}")
            raise

    def click_skip(self):
        """点击 Skip 链接跳过岗位偏好设置"""
        try:
            self.page.get_by_role("link", name="Skip").click()
        except Exception as e:
            self.logger.error(f"点击Skip失败: {e}")
            raise

    # ========== 验证方法 ==========

    def is_submit_success(self, timeout: int = 15000) -> bool:
        """
        验证提交是否成功（URL是否跳转到按岗位偏好类别筛选的招聘大类页）

        MCP录制确认：提交成功后跳转到 returnUrl 指定的 cate-jobs 页
        例：https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs

        Returns:
            bool: True 表示提交成功并跳转到招聘大类页
        """
        try:
            self.page.wait_for_url("**/cate-jobs/**", timeout=timeout)
            return "cate-jobs" in self.page.url
        except Exception:
            return False

    def is_still_on_pref_page(self, timeout: int = 3000) -> bool:
        """
        验证是否仍停留在岗位偏好页（提交失败场景）

        Returns:
            bool: True 表示仍在偏好页（提交被阻止）
        """
        try:
            self.page.wait_for_timeout(timeout)
            return "jobPreference" in self.page.url
        except Exception:
            return False

    def is_jobs_list_page_loaded(self) -> bool:
        """
        验证按岗位偏好类别筛选的招聘大类页是否已加载

        Returns:
            bool: True 表示招聘大类页（cate-jobs）正常加载
        """
        try:
            return "cate-jobs" in self.page.url
        except Exception:
            return False

    def get_field_error_message(self, field: str) -> str:
        """
        获取指定字段下方的错误提示文字

        MCP实测确认：错误文案为 "Don't leave this field empty."

        Args:
            field: "job_functions" | "location" | "salary"
        Returns:
            str: 错误提示文字，获取失败返回空字符串
        """
        try:
            error_el = self.page.locator(".error-message, .field-error, [class*='error']").filter(
                has_text="Don't leave this field empty"
            ).first
            return error_el.inner_text(timeout=3000)
        except Exception:
            return ""

    def is_error_message_visible(self, text: str = "Don't leave this field empty.") -> bool:
        """
        验证页面中是否显示指定错误提示。

        注意：网页上的撇号可能是弯引号（\u2019）而非直引号，使用关键词匹配避免编码差异。

        Args:
            text: 要检查的错误提示文字（支持直引号或弯引号）
        Returns:
            bool: True 表示错误提示存在于页面 DOM 中
        """
        try:
            # 使用不含撇号的关键词片段进行匹配，避免 ' vs ' 编码差异
            # "Don't leave this field empty." -> 匹配 "leave this field empty"
            keyword = "leave this field empty"
            el = self.page.get_by_text(keyword, exact=False).first
            el.wait_for(state="attached", timeout=5000)
            try:
                el.scroll_into_view_if_needed(timeout=2000)
            except Exception:
                pass
            return True
        except Exception:
            return False

    def is_preference_tag_visible(self, tag_text: str) -> bool:
        """
        验证列表页顶部 filter 区域是否显示指定偏好标签

        MCP实测确认：提交成功后列表页顶部显示偏好文字标签（如 "Developers/Programmers"）

        Args:
            tag_text: 标签文字（如 "Developers/Programmers"）
        Returns:
            bool: True 表示标签可见
        """
        try:
            self.page.get_by_text(tag_text, exact=False).first.wait_for(state="visible", timeout=8000)
            return True
        except Exception:
            return False

    def is_edit_link_visible(self) -> bool:
        """
        验证列表页顶部 filter 区域是否显示 Edit 链接

        Returns:
            bool: True 表示 Edit 链接可见
        """
        try:
            self.page.get_by_role("link", name="Edit").first.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False

    def click_continue_twice_fast(self):
        """
        快速连续点击 Continue 按钮两次（TC007：防重复提交测试）

        说明：模拟用户双击行为，验证系统是否只执行一次提交
        """
        try:
            btn = self.page.get_by_role("button", name="Continue")
            btn.click()
            btn.click()
        except Exception as e:
            self.logger.error(f"快速连续点击Continue失败: {e}")
            raise

    def wait_for_submit_result(self, timeout: int = 10000) -> str:
        """
        等待提交结果，返回最终落地页类型

        Returns:
            str: "success"（跳转到cate-jobs）| "blocked"（仍在jobPreference）| "unknown"
        """
        try:
            self.page.wait_for_url("**", timeout=timeout)
            url = self.page.url
            if "cate-jobs" in url:
                return "success"
            elif "jobPreference" in url:
                return "blocked"
            return "unknown"
        except Exception:
            url = self.page.url
            if "cate-jobs" in url:
                return "success"
            elif "jobPreference" in url:
                return "blocked"
            return "unknown"

    # ========== 清除预填数据方法 ==========

    def clear_job_functions(self):
        """
        清除已选的 Job Functions（应对预填数据回填场景）

        MCP实测确认：已提交账号再次进入偏好页时数据会自动回填，
        负向测试用例需要先清除才能验证空值提交场景
        """
        try:
            self.page.get_by_text("Select preferred job function").click()
            self.page.wait_for_timeout(600)
            clear_btn = self.page.get_by_role("button", name="Clear").first
            if clear_btn.is_visible(timeout=2000):
                clear_btn.click()
                self.page.wait_for_timeout(300)
            self.page.get_by_role("button", name="Confirm").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"清除Job Functions失败: {e}")
            raise

    def clear_location(self):
        """
        清除已选的 Location（应对预填数据回填场景）
        """
        try:
            self.page.get_by_text("Select preferred work").click()
            self.page.wait_for_timeout(500)
            clear_btn = self.page.get_by_role("button", name="Clear").first
            if clear_btn.is_visible(timeout=2000):
                clear_btn.click()
                self.page.wait_for_timeout(300)
            self.page.get_by_role("button", name="Confirm").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"清除Location失败: {e}")
            raise

    def clear_salary_amount(self):
        """
        清空 Salary 金额输入框（应对预填数据回填场景）
        """
        try:
            salary_input = self.page.locator("form").get_by_role("textbox")
            salary_input.click(click_count=3)
            salary_input.fill("")
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"清空Salary金额失败: {e}")
            raise
