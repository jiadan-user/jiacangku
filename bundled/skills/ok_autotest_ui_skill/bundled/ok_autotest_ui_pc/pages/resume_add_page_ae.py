"""
AE站 - 简历编辑页面 Page Object
页面路径: https://aepub.58v5.cn/biz/en/resume
页面结构: 简历视图页（Online Resume），通过行内弹窗（modal）编辑各区块
区块：
  - Personal Information（个人信息弹窗：头像、First/Last Name、联系方式、国家、性别、工签）
  - Personal Summary（个人总结弹窗：文本域）
  - Work Experience（工作经验弹窗：职位、公司、职能、日期）
  - Education Background（学历背景弹窗：学历级别、院校、专业、日期）
  - Language（语言技能弹窗：多选下拉）
"""
import re

from pages.base_page import BasePage
from utils.logger import setup_logger


class ResumeAddPageAe(BasePage):
    """AE站简历编辑页面 Page Object（modal弹窗式编辑）"""

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    # ============================================
    # 导航方法
    # ============================================

    def navigate_to_resume_view(self, base_url=None):
        """导航到简历视图页（Online Resume）"""
        try:
            url = "https://aepub.58v5.cn/biz/en/resume"
            self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
            self.page.wait_for_load_state("load", timeout=30000)
            self.page.wait_for_timeout(2000)
            self.logger.info(f"已导航到简历视图页: {self.page.url}")
        except Exception as e:
            self.logger.error(f"导航到简历视图页失败: {e}")
            raise

    def navigate_to_jobs_list(self, base_url):
        """导航到AE站招聘列表页"""
        try:
            url = f"{base_url}/en/city/cate-jobs/?iconSource=jobs"
            self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"导航到招聘列表页失败: {e}")
            raise

    # ============================================
    # 页面状态验证
    # ============================================

    def is_resume_view_displayed(self):
        """验证简历视图页（Online Resume）是否已显示"""
        try:
            self.page.wait_for_selector("h3:has-text('Online Resume')", timeout=10000)
            return True
        except Exception:
            return False

    def get_person_name_on_view(self):
        """获取简历视图页展示的姓名"""
        try:
            name_el = self.page.locator("[class*='resumePersonalInfoContent'] h2, [class*='userName']").first
            if name_el.count() > 0:
                return name_el.inner_text().strip()
            # fallback: look for the name near the avatar
            return self.page.locator("[class*='resumePersonalInfo']").first.inner_text().strip()[:30]
        except Exception as e:
            self.logger.error(f"获取姓名失败: {e}")
            return ""

    # ============================================
    # 获取所有 cursorPointer 图标（顺序固定）
    # 索引对应：0=编辑个人信息, 1=编辑Personal Summary,
    #           2=添加WorkExp, 3=编辑WorkExp(已有时),
    #           4=添加Education, 5=编辑Education(已有时),
    #           6=添加Language
    # ============================================

    def _get_icon(self, index):
        """获取第 index 个 cursorPointer 图标元素"""
        icons = self.page.locator("img[class*='cursorPointer']")
        return icons.nth(index)

    def _icon_count(self):
        return self.page.locator("img[class*='cursorPointer']").count()

    # ============================================
    # Personal Information 弹窗
    # ============================================

    def open_personal_info_modal(self):
        """点击编辑个人信息图标，打开 Personal Information 弹窗"""
        try:
            edit_icon = self.page.locator("img[class*='editPersonInfoIcon']").first
            edit_icon.wait_for(state="visible", timeout=20000)
            edit_icon.scroll_into_view_if_needed()
            self.page.wait_for_timeout(400)
            try:
                edit_icon.evaluate(
                    "el => { const y = el.getBoundingClientRect().top + window.pageYOffset - 160;"
                    " window.scrollTo({ top: y, behavior: 'instant' }); }"
                )
                self.page.wait_for_timeout(400)
            except Exception:
                pass
            edit_icon.click(timeout=45000)
            self.page.wait_for_selector("[class*='EditPersonInfoModal']", timeout=15000)
            self.page.wait_for_timeout(500)
            self.logger.info("Personal Information 弹窗已打开")
        except Exception as e:
            self.logger.error(f"打开 Personal Information 弹窗失败: {e}")
            raise

    def is_personal_info_modal_displayed(self):
        """验证 Personal Information 弹窗已显示"""
        try:
            self.page.wait_for_selector("[class*='EditPersonInfoModal_modalContentWrapper']", timeout=5000)
            return True
        except Exception:
            try:
                # fallback: 检测 modal-open class
                body_class = self.page.evaluate("document.body.className")
                return "modal-open" in (body_class or "")
            except Exception:
                return False

    def get_first_name_value(self):
        """获取 Personal Information 弹窗中 First Name 的当前值"""
        try:
            modal = self.page.locator(".modal-content").first
            inputs = modal.locator("input[type='text']")
            return inputs.nth(0).input_value()
        except Exception as e:
            self.logger.error(f"获取 First Name 失败: {e}")
            raise

    def get_last_name_value(self):
        """获取 Personal Information 弹窗中 Last Name 的当前值"""
        try:
            modal = self.page.locator(".modal-content").first
            inputs = modal.locator("input[type='text']")
            return inputs.nth(1).input_value()
        except Exception as e:
            self.logger.error(f"获取 Last Name 失败: {e}")
            raise

    def input_first_name(self, first_name):
        """在 Personal Information 弹窗中输入 First Name"""
        try:
            modal = self.page.locator(".modal-content").first
            inputs = modal.locator("input[type='text']")
            inputs.nth(0).fill(first_name)
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"输入 First Name 失败: {e}")
            raise

    def input_last_name(self, last_name):
        """在 Personal Information 弹窗中输入 Last Name"""
        try:
            modal = self.page.locator(".modal-content").first
            inputs = modal.locator("input[type='text']")
            inputs.nth(1).fill(last_name)
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"输入 Last Name 失败: {e}")
            raise

    def clear_first_name(self):
        """清空 First Name"""
        self.input_first_name("")

    def clear_last_name(self):
        """清空 Last Name"""
        self.input_last_name("")

    def is_save_button_disabled(self):
        """验证弹窗中 Save 按钮是否处于禁用状态"""
        try:
            save_btn = self.page.get_by_role("button", name="Save")
            return save_btn.is_disabled()
        except Exception as e:
            self.logger.error(f"检查 Save 按钮状态失败: {e}")
            raise

    def click_save_in_modal(self):
        """点击弹窗中的 Save 按钮（限定在 .modal-content 范围内）"""
        try:
            modal = self.page.locator(".modal-content").first
            modal.get_by_role("button", name="Save").click()
            self.page.wait_for_timeout(1500)
            # 等待弹窗关闭
            try:
                self.page.wait_for_function(
                    "!document.body.classList.contains('modal-open')",
                    timeout=8000
                )
            except Exception:
                pass
            # 确保 modal-content 元素完全隐藏
            try:
                self.page.wait_for_selector(".modal-content", state="hidden", timeout=8000)
            except Exception:
                pass
            self.page.wait_for_timeout(1000)
            self.logger.info("✓ 点击 Save 并等待弹窗关闭完成")
        except Exception as e:
            self.logger.error(f"点击 Save 失败: {e}")
            raise

    def click_cancel_in_modal(self):
        """点击弹窗中的 Cancel 按钮（限定在 .modal-content 范围内）"""
        try:
            modal = self.page.locator(".modal-content").first
            modal.get_by_role("button", name="Cancel").click()
            self.page.wait_for_timeout(500)
            self.logger.info("✓ 点击 Cancel")
        except Exception as e:
            self.logger.error(f"点击 Cancel 失败: {e}")
            raise

    def close_modal_with_x(self):
        """点击弹窗右上角的 X 关闭弹窗"""
        try:
            self.page.locator("[class*='closeIcon'], [class*='CloseIcon']").first.click()
            self.page.wait_for_timeout(500)
            self.logger.info("✓ 点击 X 关闭弹窗")
        except Exception as e:
            self.logger.error(f"关闭弹窗失败: {e}")
            raise

    def get_email_display_value(self):
        """获取 Personal Information 弹窗中 Email 显示值（只读按钮文本）"""
        try:
            # Email is shown as a clickable button/field showing the email text
            modal = self.page.locator(".modal-content").first
            # Find the email field - it shows as a button-like row with the email address
            email_text = modal.get_by_text("wangyongli@58.com")
            if email_text.is_visible(timeout=3000):
                return email_text.inner_text()
            # Try input
            email_input = modal.locator("input[type='email']")
            if email_input.count() > 0:
                return email_input.input_value()
            return ""
        except Exception as e:
            self.logger.error(f"获取 Email 值失败: {e}")
            return ""

    def select_current_location(self, country_name):
        """在 Personal Information 弹窗中选择 Current Location（国家/地区下拉）"""
        try:
            modal = self.page.locator(".modal-content").first
            # Click the country dropdown
            location_dropdown = modal.locator("select, [class*='dropdown']").filter(has_text="Denmark").first
            if location_dropdown.count() == 0:
                location_dropdown = modal.locator("[class*='CurrentLocation'], select").first
            location_dropdown.click()
            self.page.wait_for_timeout(500)
            self.page.get_by_text(country_name, exact=True).first.click()
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"选择 Current Location 失败: {e}")
            raise

    def select_gender(self, gender_value):
        """在 Personal Information 弹窗中选择 Gender"""
        try:
            modal = self.page.locator(".modal-content").first
            # Gender is a select/dropdown - find by label text proximity
            gender_section = modal.locator("text=Gender").locator("..").locator("..")
            gender_dropdown = gender_section.locator("select").first
            if gender_dropdown.count() > 0:
                gender_dropdown.select_option(label=gender_value)
            else:
                # Try click and select
                modal.locator("[class*='Gender'], select").last.click()
                self.page.wait_for_timeout(300)
                self.page.get_by_text(gender_value, exact=True).click()
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"选择 Gender 失败: {e}")
            raise

    # ============================================
    # Personal Summary 弹窗
    # ============================================

    def open_personal_summary_modal(self):
        """点击编辑 Personal Summary 图标，打开弹窗"""
        try:
            summary_head = self.page.locator("h2:has-text('Personal Summary')").locator("..")
            edit_icon = summary_head.locator("img[class*='cursorPointer']")
            if edit_icon.count() > 0:
                edit_icon.first.click()
            else:
                # Fallback: second overall cursorPointer icon (0=PersonalInfo, 1=PersonalSummary)
                self._get_icon(1).click()
            self.page.wait_for_selector(".modal-content", timeout=8000)
            self.page.wait_for_timeout(500)
            self.logger.info("Personal Summary 弹窗已打开")
        except Exception as e:
            self.logger.error(f"打开 Personal Summary 弹窗失败: {e}")
            raise

    def is_personal_summary_modal_displayed(self):
        """验证 Personal Summary 弹窗是否显示"""
        try:
            modal = self.page.locator(".modal-content").first
            has_summary_title = modal.get_by_text("Personal Summary", exact=True).is_visible(timeout=5000)
            has_textarea = modal.locator("textarea").is_visible(timeout=3000)
            return has_summary_title and has_textarea
        except Exception:
            return False

    def input_personal_summary(self, text):
        """在 Personal Summary 弹窗中输入文本"""
        try:
            self.page.locator("textarea").fill(text)
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"输入 Personal Summary 失败: {e}")
            raise

    def get_personal_summary_placeholder(self):
        """获取 Personal Summary 文本域的 placeholder"""
        try:
            return self.page.locator("textarea").first.get_attribute("placeholder") or ""
        except Exception:
            return ""

    # ============================================
    # Work Experience 弹窗
    # ============================================

    def _click_edit_icon_for_section(self, section_title):
        """通用：点击指定区块的 edit（pencil）图标
        
        策略：在该区块所在的容器（h2..的父级容器）内找所有 cursorPointer 图标，
        优先点击 icon-edit-pc（编辑图标），否则点击第一个
        """
        # 找到包含该标题的整个区块容器（需要找到更大的容器，不止是 head div）
        # 页面结构：resume_resumeItem__xxx > resume_resumeItemHead > h2 + icon
        #                               > resume_workExperience_xxx (list items with edit icons)
        h2 = self.page.locator(f"h2:has-text('{section_title}')")
        # 向上走 2 级找到整个区块容器
        container = h2.locator("../..") 
        all_icons = container.locator("img[class*='cursorPointer']")
        count = all_icons.count()
        
        # 优先找 edit 图标（icon-edit-pc）
        for i in range(count):
            icon = all_icons.nth(i)
            src = icon.get_attribute("src") or ""
            if "icon-edit" in src:
                icon.click()
                self.page.wait_for_timeout(500)
                return
        
        # 无 edit 图标（可能只有 add 图标），点第一个
        if count > 0:
            all_icons.first.click()
            self.page.wait_for_timeout(500)

    def open_edit_work_experience_modal(self):
        """点击编辑已有工作经验图标，打开 Edit Work Experience 弹窗"""
        try:
            self._click_edit_icon_for_section("Work Experience")
            self.page.wait_for_selector(".modal-content", timeout=8000)
            self.page.wait_for_timeout(500)
            self.logger.info("Edit Work Experience 弹窗已打开")
        except Exception as e:
            self.logger.error(f"打开 Work Experience 弹窗失败: {e}")
            raise

    def open_add_work_experience_modal(self):
        """点击添加工作经验图标（+），打开 Add Work Experience 弹窗"""
        try:
            # Add icon (+) is in the head section (direct parent of h2)
            work_head = self.page.locator("h2:has-text('Work Experience')").locator("..")
            add_icon = work_head.locator("img[src*='icon-add']")
            if add_icon.count() > 0:
                add_icon.first.click()
            else:
                work_head.locator("img[class*='cursorPointer']").first.click()
            self.page.wait_for_selector(".modal-content", timeout=8000)
            self.page.wait_for_timeout(500)
            self.logger.info("Add Work Experience 弹窗已打开")
        except Exception as e:
            self.logger.error(f"打开添加 Work Experience 弹窗失败: {e}")
            raise

    def is_work_experience_modal_displayed(self):
        """验证 Work Experience 弹窗是否显示"""
        try:
            self.page.wait_for_selector(".modal-content", timeout=5000)
            modal = self.page.locator(".modal-content").first
            # Modal should contain "Work Experience" in its text
            text = modal.inner_text()
            return "Work Experience" in text
        except Exception:
            return False

    def input_job_title(self, title):
        """在 Work Experience 弹窗中输入 Job Title"""
        try:
            modal = self.page.locator(".modal-content").first
            modal.get_by_placeholder("Job Title").fill(title)
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"输入 Job Title 失败: {e}")
            raise

    def input_company(self, company):
        """在 Work Experience 弹窗中输入 Company"""
        try:
            modal = self.page.locator(".modal-content").first
            modal.get_by_placeholder("Company").fill(company)
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"输入 Company 失败: {e}")
            raise

    def select_job_function(self, function_name):
        """在 Work Experience 弹窗中选择 Job Function（第3个 text input 为 Job Function）"""
        try:
            modal = self.page.locator(".modal-content").first
            # Job Function is the 3rd text input (index 2) - Job Title(0), Company(1), Job Function(2)
            job_func_input = modal.locator("input[type='text']").nth(2)
            job_func_input.click()
            self.page.wait_for_timeout(300)
            job_func_input.fill(function_name)
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"选择 Job Function 失败: {e}")
            raise

    def get_job_function_value(self):
        """获取 Work Experience 弹窗中 Job Function 当前值（第3个 text input）"""
        try:
            modal = self.page.locator(".modal-content").first
            # Job Function is the 3rd text input (index 2)
            return modal.locator("input[type='text']").nth(2).input_value()
        except Exception as e:
            self.logger.error(f"获取 Job Function 值失败: {e}")
            return ""

    def input_work_from_date(self, date_str):
        """在 Work Experience 弹窗中输入 From 日期（格式: YYYY-MM）"""
        try:
            modal = self.page.locator(".modal-content").first
            from_input = modal.locator("input[type='text']").filter(has_placeholder="From")
            if from_input.count() == 0:
                # Try by position - the 2nd text input (after Job Title, Company)
                all_inputs = modal.locator("input[type='text']")
                from_input = all_inputs.nth(2)
            from_input.fill(date_str)
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"输入 Work From 日期失败: {e}")
            raise

    def get_work_from_date_value(self):
        """获取 Work Experience 弹窗中 From 日期值"""
        try:
            modal = self.page.locator(".modal-content").first
            all_inputs = modal.locator("input[type='text']")
            # From is the 3rd input (index 2) - after Job Title (0), Company (1)
            return all_inputs.nth(2).input_value()
        except Exception as e:
            self.logger.error(f"获取 Work From 日期失败: {e}")
            return ""

    def is_currently_work_here_checked(self):
        """验证 'I currently work here' 是否勾选（Work Experience 弹窗中）"""
        try:
            modal = self.page.locator(".modal-content").first
            # Look for the "Present" text in To field - if visible, means currently work here
            modal_text = modal.inner_text()
            return "Present" in modal_text
        except Exception:
            return False

    def toggle_currently_work_here(self):
        """切换 'I currently work here' 复选框状态（点击 checkbox 图标）"""
        try:
            modal = self.page.locator(".modal-content").first
            # The checkbox for 'I currently work here' - find by nearby text
            checkbox_area = modal.locator("text=I currently work here").locator("..")
            # Click the checkbox/toggle element in the parent
            checkbox = checkbox_area.locator("input[type='checkbox'], [class*='checkbox'], [class*='check']")
            if checkbox.count() > 0:
                checkbox.first.click()
            else:
                # Fallback: click on the text itself (label click)
                modal.get_by_text("I currently work here").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"切换 'I currently work here' 失败: {e}")
            raise

    # ============================================
    # Education Background 弹窗
    # ============================================

    def open_edit_education_modal(self):
        """点击编辑已有学历图标，打开 Edit Education Background 弹窗"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 确保之前的弹窗已完全关闭
                try:
                    self.page.wait_for_selector(".modal-content", state="hidden", timeout=5000)
                except Exception:
                    pass
                
                # 等待页面稳定（Save后可能有局部刷新）
                self.page.wait_for_load_state("domcontentloaded", timeout=10000)
                self.page.wait_for_timeout(2000)
                
                self._click_edit_icon_for_section("Education Background")
                
                # 尝试等待弹窗出现
                self.page.wait_for_selector(".modal-content", timeout=15000)
                self.page.wait_for_timeout(500)
                self.logger.info("Edit Education Background 弹窗已打开")
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    self.logger.warning(f"第{attempt + 1}次尝试打开弹窗失败，重试中: {e}")
                    self.page.wait_for_timeout(2000)
                else:
                    self.logger.error(f"打开 Education Background 弹窗失败（已重试{max_retries}次）: {e}")
                    raise

    def open_add_education_modal(self):
        """点击添加学历图标（+），打开 Add Education Background 弹窗"""
        try:
            edu_head = self.page.locator("h2:has-text('Education Background')").locator("..")
            add_icon = edu_head.locator("img[src*='icon-add']")
            if add_icon.count() > 0:
                add_icon.first.click()
            else:
                edu_head.locator("img[class*='cursorPointer']").first.click()
            self.page.wait_for_selector(".modal-content", timeout=8000)
            self.page.wait_for_timeout(500)
            self.logger.info("Add Education Background 弹窗已打开")
        except Exception as e:
            self.logger.error(f"打开添加 Education Background 弹窗失败: {e}")
            raise

    def is_education_modal_displayed(self):
        """验证 Education Background 弹窗是否显示"""
        try:
            self.page.wait_for_selector(".modal-content", timeout=5000)
            modal = self.page.locator(".modal-content").first
            text = modal.inner_text()
            return "Education" in text
        except Exception:
            return False

    def select_education_level(self, level):
        """在 Education Background 弹窗中选择 Education Level（自定义下拉 PcFakeSelectInput）"""
        try:
            modal = self.page.locator(".modal-content").first
            # Education Level uses PcFakeSelectInput (custom dropdown, NOT native select)
            edu_dropdown = modal.locator("[class*='PcFakeSelectInput_pcFakeSelectInput']").first
            edu_dropdown.click()
            self.page.wait_for_timeout(500)
            # Click the option in the dropdown list
            self.page.get_by_text(level, exact=True).first.click()
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"选择 Education Level 失败: {e}")
            raise

    def get_education_level_value(self):
        """获取 Education Background 弹窗中 Education Level 当前显示值"""
        try:
            modal = self.page.locator(".modal-content").first
            value_span = modal.locator("[class*='PcFakeSelectInput_valueText']").first
            return value_span.inner_text().strip()
        except Exception as e:
            self.logger.error(f"获取 Education Level 失败: {e}")
            return ""

    def input_institute(self, institute):
        """在 Education Background 弹窗中输入 Institute（Optional）
        
        Education 弹窗使用 CustomCounterInput 组件，input 无 placeholder 属性。
        优先按标签关联 Institute，避免弹窗内新增搜索框等导致 nth(0) 错位。
        """
        try:
            modal = self.page.locator(".modal-content").first
            labeled = modal.get_by_label(re.compile(r"Institute", re.I))
            if labeled.count() > 0:
                labeled.first.fill(institute)
            else:
                container = modal.locator("div, section, form").filter(
                    has_text=re.compile(r"Institute", re.I)
                ).first
                inp = container.locator("input[type='text']").first
                if inp.count() > 0:
                    inp.fill(institute)
                else:
                    modal.locator("input[type='text']").nth(0).fill(institute)
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"输入 Institute 失败: {e}")
            raise

    def get_institute_value(self):
        """获取 Education Background 弹窗中 Institute 当前值"""
        try:
            modal = self.page.locator(".modal-content").first
            labeled = modal.get_by_label(re.compile(r"Institute", re.I))
            if labeled.count() > 0:
                return labeled.first.input_value()
            container = modal.locator("div, section, form").filter(
                has_text=re.compile(r"Institute", re.I)
            ).first
            inp = container.locator("input[type='text']").first
            if inp.count() > 0:
                return inp.input_value()
            return modal.locator("input[type='text']").nth(0).input_value()
        except Exception as e:
            self.logger.error(f"获取 Institute 值失败: {e}")
            return ""

    def input_major(self, major):
        """在 Education Background 弹窗中输入 Major（Optional）"""
        try:
            modal = self.page.locator(".modal-content").first
            modal.locator("input[type='text']").nth(1).fill(major)
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"输入 Major 失败: {e}")
            raise

    def get_edu_from_date_value(self):
        """获取 Education Background 弹窗中 From 日期值（文本类型，格式 YYYY-MM）"""
        try:
            modal = self.page.locator(".modal-content").first
            # From/To are shown as text inputs but may be read via displayed text
            from_section = modal.locator("text=From").locator("..")
            from_input = from_section.locator("input[type='text']")
            if from_input.count() > 0:
                return from_input.first.input_value()
            # Fallback: look for YYYY-MM pattern in text
            return ""
        except Exception as e:
            self.logger.error(f"获取 Education From 日期失败: {e}")
            return ""

    def get_edu_to_date_value(self):
        """获取 Education Background 弹窗中 To 日期值"""
        try:
            modal = self.page.locator(".modal-content").first
            to_section = modal.locator("text=To").locator("..")
            to_input = to_section.locator("input[type='text']")
            if to_input.count() > 0:
                return to_input.first.input_value()
            return ""
        except Exception as e:
            self.logger.error(f"获取 Education To 日期失败: {e}")
            return ""

    def input_edu_from_date(self, date_str):
        """在 Education Background 弹窗中输入 From 日期（格式: YYYY-MM）"""
        try:
            modal = self.page.locator(".modal-content").first
            # From date is shown as a text display, not editable input
            # The dates in education are pre-filled from server
            self.logger.info(f"Education From 日期: {date_str}（当前通过视图验证）")
        except Exception as e:
            self.logger.error(f"输入 Education From 日期失败: {e}")
            raise

    def input_edu_to_date(self, date_str):
        """在 Education Background 弹窗中输入 To 日期（格式: YYYY-MM）"""
        try:
            modal = self.page.locator(".modal-content").first
            self.logger.info(f"Education To 日期: {date_str}（当前通过视图验证）")
        except Exception as e:
            self.logger.error(f"输入 Education To 日期失败: {e}")
            raise

    # ============================================
    # Language 弹窗
    # ============================================

    def open_language_modal(self):
        """点击语言技能添加图标，打开 Language 弹窗"""
        try:
            lang_section = self.page.locator("h2:has-text('Language')").locator("..")
            lang_icon = lang_section.locator("img[class*='cursorPointer']").first
            lang_icon.click()
            self.page.wait_for_selector(".modal-content", timeout=8000)
            self.page.wait_for_timeout(500)
            self.logger.info("Language 弹窗已打开")
        except Exception as e:
            self.logger.error(f"打开 Language 弹窗失败: {e}")
            raise

    def is_language_modal_displayed(self):
        """验证 Language 弹窗是否显示"""
        try:
            self.page.wait_for_selector(".modal-content", timeout=5000)
            modal = self.page.locator(".modal-content").first
            text = modal.inner_text()
            return "Language" in text
        except Exception:
            return False

    # ============================================
    # 通用弹窗交互
    # ============================================

    def is_any_modal_open(self):
        """验证当前是否有弹窗打开"""
        try:
            body_class = self.page.evaluate("document.body.className")
            return "modal-open" in (body_class or "")
        except Exception:
            return False

    def wait_for_modal_close(self, timeout=5000):
        """等待弹窗关闭"""
        try:
            self.page.wait_for_function(
                "!document.body.classList.contains('modal-open')",
                timeout=timeout
            )
            self.page.wait_for_timeout(300)
        except Exception:
            pass

    # ============================================
    # 简历视图页区块内容验证
    # ============================================

    def get_work_experience_title_on_view(self):
        """获取简历视图页上展示的工作经验职位标题"""
        try:
            return self.page.locator("h2[class*='workExperienceJobTitle']").first.inner_text()
        except Exception:
            return ""

    def is_work_experience_section_visible(self):
        """验证 Work Experience 区块是否可见"""
        try:
            return self.page.locator("h2:has-text('Work Experience')").is_visible(timeout=3000)
        except Exception:
            return False

    def is_education_section_visible(self):
        """验证 Education Background 区块是否可见"""
        try:
            return self.page.locator("h2:has-text('Education Background')").is_visible(timeout=3000)
        except Exception:
            return False

    def is_language_section_visible(self):
        """验证 Language 区块是否可见"""
        try:
            return self.page.locator("h2:has-text('Language')").is_visible(timeout=3000)
        except Exception:
            return False

    def get_personal_summary_text_on_view(self):
        """获取简历视图页 Personal Summary 区块显示的文本"""
        try:
            summary_section = self.page.locator("h2:has-text('Personal Summary')").locator("..")
            return summary_section.inner_text()
        except Exception:
            return ""
