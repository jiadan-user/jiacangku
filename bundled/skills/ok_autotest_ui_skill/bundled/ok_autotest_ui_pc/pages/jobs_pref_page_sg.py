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
           c. 尝试从首页重新进入（清除缓存）
           d. 最后使用直接 URL（带认证状态）
        """
        try:
            # 确保导航到首页
            self.page.goto(f"{base_url}/en/city-singapore/", wait_until="domcontentloaded", timeout=30000)
            self.page.wait_for_load_state("domcontentloaded")
            try:
                self.page.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                pass
            
            # 等待 Jobs 金刚位出现并点击
            jobs_link = self.page.get_by_role("link", name="Jobs Jobs")
            jobs_link.wait_for(state="visible", timeout=10000)
            
            # 使用 expect_navigation 确保跳转完成
            try:
                with self.page.expect_navigation(timeout=15000):
                    jobs_link.click()
            except Exception:
                # 如果 expect_navigation 超时，尝试等待 URL 变化
                self.page.wait_for_timeout(2000)
            
            # 等待页面稳定
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            except Exception:
                pass
            
            current_url = self.page.url
            self.logger.info(f"点击 Jobs 金刚位后 URL: {current_url}")
            
            # 检查是否已进入 jobPreference 页面
            if "jobPreference" in current_url:
                self.logger.info("✓ 直接进入岗位偏好页")
                self.page.wait_for_timeout(1000)
                return

            # 已跳转到 cate-jobs，尝试多种入口
            self.logger.info(f"⚠️ 当前在 Jobs 列表页，尝试进入偏好页")
            
            # 策略1: 尝试 Edit 链接（页面上可能有多个，找最显眼的）
            edit_selectors = [
                'a:has-text("Edit"):has([class*="preference"])',
                'a:has-text("Edit")',
                '[class*="preference"] a:has-text("Edit")',
                'button:has-text("Edit")',
            ]
            
            for selector in edit_selectors:
                try:
                    self.logger.info(f"尝试 selector: {selector}")
                    edit_elem = self.page.locator(selector).first
                    if edit_elem.is_visible(timeout=2000):
                        self.logger.info(f"找到 Edit 元素，selector: {selector}")
                        edit_elem.click()
                        try:
                            self.page.wait_for_url("**/jobPreference**", timeout=10000)
                            self.logger.info("✓ 通过 Edit 链接进入偏好页")
                            return
                        except Exception:
                            self.logger.info("点击 Edit 但未跳转到 jobPreference")
                except Exception as e:
                    self.logger.debug(f"Selector {selector} 失败: {e}")
                    continue
            
            # 策略2: 强制刷新 cate-jobs 页面，寻找 Add Job Preference
            self.logger.info("尝试刷新 Jobs 列表页并寻找 Add Job Preference")
            self.page.goto(f"{base_url}/en/city-singapore/cate-jobs/?iconSource=jobs",
                          wait_until="domcontentloaded", timeout=30000)
            try:
                self.page.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                pass
            
            # 尝试多种 Add Preference 入口
            add_pref_selectors = [
                'text=Add Job Preference',
                'button:has-text("Add")',
                '[class*="add"][class*="preference"]',
                'a:has-text("Add Job Preference")',
            ]
            
            for selector in add_pref_selectors:
                try:
                    add_elem = self.page.locator(selector).first
                    if add_elem.is_visible(timeout=3000):
                        self.logger.info(f"找到 Add Preference 元素，selector: {selector}")
                        add_elem.click()
                        try:
                            self.page.wait_for_url("**/jobPreference**", timeout=10000)
                            self.logger.info("✓ 通过 Add Job Preference 进入偏好页")
                            return
                        except Exception:
                            self.logger.info("点击 Add 但未跳转到 jobPreference")
                except Exception as e:
                    self.logger.debug(f"Add selector {selector} 失败: {e}")
                    continue
            
            # 策略3: 最后尝试直接访问偏好页 URL（使用当前认证状态）
            self.logger.info("所有入口失败，尝试直接访问偏好页 URL")
            pref_url = f"https://sgpub.58v5.cn/biz/en/jobPreference?showSkip=1&returnUrl=https%3A%2F%2Fsg.58v5.cn%2Fen%2Fcity-singapore%2Fcate-jobs%2F%3FiconSource%3Djobs"
            self.page.goto(pref_url, wait_until="domcontentloaded", timeout=30000)
            self.page.wait_for_timeout(2000)
            
            if "jobPreference" in self.page.url:
                self.logger.info("✓ 通过直接 URL 进入偏好页")
                return
            
            # 所有策略都失败
            raise RuntimeError(
                f"无法进入岗位偏好页，当前URL: {self.page.url}，"
                "所有入口均失败（Edit/Add/Direct URL），请检查账号状态或页面结构"
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
            # 点击一级分类，使用 .first 避免多匹配
            self.page.get_by_text(category).first.click()
            self.page.wait_for_timeout(600)
            
            # 点击二级分类，限定在选项区域内（JointLevelPcSelectInput_optionItem 类）
            # 使用更精确的定位器避免匹配到已选标签
            subcategory_option = self.page.locator(
                f'div[class*="optionItem"]:has-text("{subcategory}")'
            ).first
            subcategory_option.click()
            self.page.wait_for_timeout(500)
            self.logger.info(f"✓ 已选择 Job Function: {category} > {subcategory}")
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
            cb = self.page.get_by_role("checkbox", name=location_name, exact=True)
            cb.wait_for(state="visible", timeout=25000)
            cb.click()
            self.page.wait_for_timeout(300)
        except Exception:
            try:
                self.page.get_by_label(location_name, exact=True).click()
                self.page.wait_for_timeout(300)
            except Exception:
                try:
                    self.page.locator(
                        f'label:has-text("{location_name}")'
                    ).first.click()
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
        """点击 Skip 链接跳过岗位偏好设置（增加无头模式适配）"""
        try:
            # 在无头模式下，Skip链接可能需要等待页面完全渲染
            self.page.wait_for_timeout(1000)
            skip_link = self.page.get_by_role("link", name="Skip")
            # 增加等待时间确保元素可见
            skip_link.wait_for(state="visible", timeout=15000)
            # 尝试滚动到元素可见区域
            try:
                skip_link.scroll_into_view_if_needed(timeout=5000)
            except Exception:
                pass
            skip_link.click(timeout=10000)
        except Exception as e:
            self.logger.error(f"点击Skip失败: {e}")
            # 尝试备用方案：使用文本定位
            try:
                self.logger.info("尝试使用备用选择器定位Skip链接")
                self.page.get_by_text("Skip", exact=True).click(timeout=10000)
            except Exception as e2:
                self.logger.error(f"备用方案也失败: {e2}")
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
        在无头模式下需要在两次点击之间添加极短的延迟以确保点击都被注册
        """
        try:
            btn = self.page.get_by_role("button", name="Continue")
            # 确保按钮可见且可点击
            btn.wait_for(state="visible", timeout=10000)
            btn.click()
            # 在无头模式下，添加极短延迟确保第二次点击被注册
            self.page.wait_for_timeout(50)
            # 尝试第二次点击，可能已经开始跳转所以需要捕获异常
            try:
                btn.click(timeout=2000)
            except Exception:
                # 如果第二次点击失败（页面已跳转），这是预期行为
                self.logger.info("第二次点击时页面可能已开始跳转（正常）")
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
            # 先尝试点击 Job Functions 触发器打开面板
            trigger = self.page.get_by_text("Select preferred job function").first
            if not trigger.is_visible(timeout=3000):
                # 如果看不到 "Select preferred job function"，说明可能已有预填值
                # 尝试点击已填充的值触发器
                trigger = self.page.locator('div[class*="SelectInput"] >> text="Job Function"').first
                if not trigger.is_visible(timeout=2000):
                    # 最后尝试通用触发器
                    trigger = self.page.locator('//div[contains(@class, "PcSelectInput")]//div[contains(@class, "trigger")]').first
            
            trigger.click()
            self.page.wait_for_timeout(800)
            
            # 查找并点击 Clear 按钮
            clear_btn = self.page.get_by_role("button", name="Clear").first
            if clear_btn.is_visible(timeout=2000):
                clear_btn.click()
                self.page.wait_for_timeout(300)
                self.logger.info("✓ 已点击 Clear 清除预填数据")
            
            # 确认关闭面板
            confirm_btn = self.page.get_by_role("button", name="Confirm").first
            confirm_btn.click()
            self.page.wait_for_timeout(500)
            self.logger.info("✓ Job Functions 已清除")
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
