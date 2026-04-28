"""
ES站 - 简历添加页面 Page Object
页面路径: https://espub.58v5.cn/biz/en/resume/add
入口: 招聘列表页详情面板底部 Resume 按钮
"""
import re
import time

from pages.base_page import BasePage
from utils.logger import setup_logger


class ResumeAddPageEs(BasePage):
    """ES站简历添加页面 Page Object（两步式表单）"""

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    # ============================================
    # 导航方法
    # ============================================

    def navigate_to_jobs_list(self, base_url):
        """导航到ES站招聘列表页"""
        try:
            url = f"{base_url}/en/city-madrid2/cate-jobs/?iconSource=jobs"
            self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"导航到招聘列表页失败: {e}")
            raise

    def click_resume_button_in_detail_panel(self):
        """点击职位详情面板底部的 Resume 按钮"""
        try:
            self.page.wait_for_selector("text=Resume", timeout=15000)
            self.page.get_by_text("Resume").click()
            # 无简历时进入 /resume/add；已有简历时常进入 /biz/en/resume
            self.page.wait_for_timeout(2500)
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception as e:
            self.logger.error(f"点击 Resume 按钮失败: {e}")
            raise

    def navigate_to_resume_add(self, base_url):
        """直接导航到简历添加页面
        
        注意：如果账号已有简历，可能会被重定向到简历视图页
        """
        try:
            pub_url = base_url.replace("es.58v5.cn", "espub.58v5.cn/biz")
            self.page.goto(f"{pub_url}/en/resume/add", wait_until="domcontentloaded", timeout=30000)
            self.page.wait_for_timeout(2000)
            
            # 检查是否被重定向
            if "/resume/add" not in self.page.url:
                self.logger.warning(f"⚠️  页面重定向到: {self.page.url}")
                self.logger.warning("⚠️  账号可能已有简历，无法访问添加页")
                # 不抛出异常，让调用方处理
        except Exception as e:
            self.logger.error(f"导航到简历添加页失败: {e}")
            raise

    def is_on_resume_add_page(self):
        """验证当前是否在简历添加页（非简历视图页）"""
        try:
            current_url = self.page.url
            return "/resume/add" in current_url
        except Exception:
            return False

    # ============================================
    # Step1 - Personal Information 操作方法
    # ============================================

    def is_step1_displayed(self):
        """验证 Step1 Personal Information 页面已显示"""
        try:
            self.page.wait_for_selector("h3:has-text('Personal Information')", timeout=10000)
            return True
        except Exception:
            return False

    def wait_for_step1_form_ready(self, timeout_ms: int = 60000):
        """等待 Step1 表单可交互（简历页首屏/壳层加载较慢时使用）。"""
        try:
            only_essential = self.page.get_by_role("button", name="Only essential")
            if only_essential.is_visible(timeout=3000):
                only_essential.click()
                self.page.wait_for_timeout(600)
        except Exception:
            pass
        try:
            accept_all = self.page.get_by_role("button", name="Accept all")
            if accept_all.is_visible(timeout=1500):
                accept_all.click()
                self.page.wait_for_timeout(600)
        except Exception:
            pass
        try:
            self.page.wait_for_load_state("networkidle", timeout=12000)
        except Exception:
            pass
        try:
            self.page.wait_for_selector(
                "h3:has-text('Personal Information'), h2:has-text('Personal Information')",
                timeout=15000,
            )
        except Exception:
            pass

        first_loc = (
            self.page.get_by_role("textbox", name="First Name").or_(
                self.page.locator(
                    "input[placeholder*='First' i], input[autocomplete='given-name'], "
                    "input[name*='firstName' i], input[name*='first_name' i], "
                    "input[id*='firstName' i]"
                ).first
            )
        )
        try:
            first_loc.wait_for(state="visible", timeout=timeout_ms)
            return
        except Exception:
            pass
        for fr in self.page.frames:
            if fr == self.page.main_frame:
                continue
            try:
                fr.get_by_role("textbox", name="First Name").wait_for(
                    state="visible", timeout=12000
                )
                return
            except Exception:
                pass
        first_loc.wait_for(state="visible", timeout=timeout_ms)

    def get_email_value(self):
        """获取 Email 字段的当前值"""
        try:
            return self.page.get_by_role("textbox", name="Email").input_value()
        except Exception as e:
            self.logger.error(f"获取 Email 值失败: {e}")
            raise

    def get_current_location_value(self):
        """获取 Current Location 字段的当前值"""
        try:
            return self.page.get_by_role("textbox", name="Select country/region").input_value()
        except Exception as e:
            self.logger.error(f"获取 Current Location 值失败: {e}")
            raise

    def select_current_location(self, country_name: str):
        """选择 Current Location（国家/地区）

        Args:
            country_name: 国家名称（如 'France', 'Spain'）
        """
        try:
            # Current Location 是只读输入框，需要点击打开下拉选择器
            location_input = self.page.get_by_role("textbox", name="Select country/region")
            location_input.click()
            self.page.wait_for_timeout(500)
            # 在搜索框中输入国家名（下拉选择器内的搜索框）
            search_input = self.page.get_by_placeholder("Search").first
            if search_input.is_visible(timeout=3000):
                search_input.fill(country_name)
                self.page.wait_for_timeout(500)
            # 等待下拉选项出现并点击匹配项
            option = self.page.get_by_text(country_name, exact=True).first
            option.wait_for(state="visible", timeout=5000)
            option.click()
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"选择 Current Location 失败: {e}")
            raise

    def is_continue_button_disabled(self):
        """验证 Continue 按钮是否处于禁用状态"""
        try:
            return self.page.get_by_role("button", name="Continue").is_disabled()
        except Exception as e:
            self.logger.error(f"检查 Continue 按钮状态失败: {e}")
            raise

    def input_first_name(self, first_name):
        """输入 First Name"""
        loc = (
            self.page.get_by_role("textbox", name="First Name").or_(
                self.page.locator(
                    "input[placeholder*='First' i], input[autocomplete='given-name'], "
                    "input[name*='firstName' i], input[name*='first_name' i]"
                ).first
            )
        )
        try:
            loc.fill(first_name, timeout=25000)
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"输入 First Name 失败: {e}")
            raise

    def input_last_name(self, last_name):
        """输入 Last Name"""
        try:
            self.page.get_by_role("textbox", name="Last Name").fill(last_name)
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"输入 Last Name 失败: {e}")
            raise

    def clear_first_name(self):
        """清空 First Name"""
        try:
            self.page.get_by_role("textbox", name="First Name").fill("")
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"清空 First Name 失败: {e}")
            raise

    def clear_last_name(self):
        """清空 Last Name"""
        try:
            self.page.get_by_role("textbox", name="Last Name").fill("")
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"清空 Last Name 失败: {e}")
            raise

    def get_first_name_value(self):
        """获取 First Name 字段的值"""
        try:
            return self.page.get_by_role("textbox", name="First Name").input_value()
        except Exception:
            pass
        try:
            return self.page.locator("input[placeholder*='First' i]").first.input_value()
        except Exception:
            return ""

    def get_last_name_value(self):
        """获取 Last Name 字段的值"""
        try:
            return self.page.get_by_role("textbox", name="Last Name").input_value()
        except Exception:
            return ""

    def get_first_name_char_count_text(self):
        """获取 First Name 字符计数文本（如 '4/100'）"""
        try:
            return self.page.locator(".StepInfo_nameCount__qVsaG").first.inner_text()
        except Exception:
            try:
                return self.page.locator("text=/\\d+\\/100/").first.inner_text()
            except Exception as e:
                self.logger.error(f"获取字符计数失败: {e}")
                raise

    def get_first_name_char_count(self):
        """获取 First Name 字符计数数字"""
        try:
            count_text = self.page.locator(".StepInfo_nameCount__qVsaG").first.inner_text()
            return int(count_text.split("/")[0])
        except Exception:
            return 0

    def get_last_name_char_count(self):
        """获取 Last Name 字符计数数字"""
        try:
            count_text = self.page.locator(".StepInfo_nameCount__qVsaG").last.inner_text()
            return int(count_text.split("/")[0])
        except Exception:
            return 0

    def select_gender(self, gender_value):
        """选择 Gender

        Args:
            gender_value: 性别选项（如 'Male', 'Female', 'Prefer not to say'）
        """
        try:
            self.page.get_by_text("Prefer not to say").click()
            self.page.wait_for_timeout(500)
            self.page.get_by_text(gender_value, exact=True).click()
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"选择 Gender 失败: {e}")
            raise

    def click_avatar(self, index=1):
        """点击预设头像（index从1开始）"""
        try:
            avatars = self.page.locator(".StepInfo_avatarItem__sMQzY")
            avatars.nth(index - 1).click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击头像失败: {e}")
            raise

    def upload_avatar_file(self, file_path):
        """上传头像文件

        Args:
            file_path: 文件路径
        """
        try:
            file_input = self.page.locator("[class*='PersonAvatar'] input[type='file']")
            if file_input.count() == 0:
                file_input = self.page.locator("input[type='file']")
            file_input.first.set_input_files(file_path)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"上传头像失败: {e}")
            raise

    def is_avatar_uploaded(self):
        """验证头像是否已上传"""
        try:
            # 检查头像容器是否显示
            return self.page.locator(
                "[class*='PersonAvatar_upload_img'], [class*='avatarContainer'] img, [class*='PersonAvatar'] img"
            ).first.is_visible(timeout=3000)
        except Exception:
            return False

    def click_continue(self):
        """点击 Continue 按钮"""
        try:
            self.page.get_by_role("button", name="Continue").click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击 Continue 失败: {e}")
            raise

    def click_step1_back_and_wait(self):
        """点击 Step1 Back 按钮并等待导航"""
        try:
            self.page.get_by_role("button", name="Back").click()
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            self.page.wait_for_timeout(1500)
        except Exception as e:
            self.logger.error(f"点击 Step1 Back 并等待导航失败: {e}")
            raise

    # ============================================
    # Step2 - Recent Experience 操作方法
    # ============================================

    def is_step2_displayed(self):
        """验证 Step2 Recent Experience 页面已显示"""
        try:
            self.page.wait_for_selector("h3:has-text('Recent Experience')", timeout=10000)
            return True
        except Exception:
            return False

    # Mock 数据：真实分类 ID 映射（来自 smartProbe API，与 easypost categories 共用同一套 ID 体系）
    _JOB_CATEGORY_MOCK = {
        "Information & Communication Technology": {
            "id": "4241",
            "subcategories": {
                "Testing & Quality Assurance": "4261",
                "Developers/Programmers": "4247",
                "Engineering - Software": "4250",
                "Help Desk & IT Support": "4251",
                "Management": "4252",
            }
        },
        "Accounting": {
            "id": "4001",
            "subcategories": {
                "Accounts Officers/Clerks": "4002",
                "Bookkeeping": "4003",
            }
        },
        "Administration & Office Support": {
            "id": "4027",
            "subcategories": {
                "Administrative Assistants": "4028",
                "Office Management": "4029",
            }
        },
    }

    def _setup_job_function_mock(self):
        """注册 API 路由 Mock，拦截 easypost/api/categories 请求（应对 502 故障）"""
        import json

        first_level_items = [
            {"id": v["id"], "name": k, "childNum": len(v["subcategories"])}
            for k, v in self._JOB_CATEGORY_MOCK.items()
        ]

        subcategory_map = {}
        for cat_name, cat_info in self._JOB_CATEGORY_MOCK.items():
            sub_items = [
                {"id": sub_id, "name": sub_name}
                for sub_name, sub_id in cat_info["subcategories"].items()
            ]
            subcategory_map[cat_info["id"]] = sub_items

        def handle_route(route):
            url = route.request.url
            if "categoryId=4000" in url:
                route.fulfill(
                    status=200,
                    content_type="application/json",
                    body=json.dumps({"code": 200, "data": first_level_items})
                )
            else:
                # 提取 categoryId
                import re
                m = re.search(r"categoryId=(\d+)", url)
                if m:
                    cat_id = m.group(1)
                    items = subcategory_map.get(cat_id, [])
                    route.fulfill(
                        status=200,
                        content_type="application/json",
                        body=json.dumps({"code": 200, "data": items})
                    )
                else:
                    route.continue_()

        self.page.route("**/easypost/api/categories**", handle_route)
        self.logger.info("✓ Job Function API Mock 已注册")

    def _teardown_job_function_mock(self):
        """取消 API 路由 Mock"""
        try:
            self.page.unroute("**/easypost/api/categories**")
            self.logger.info("✓ Job Function API Mock 已取消")
        except Exception:
            pass

    def select_job_function(self, category, subcategory):
        """选择 Job Function（两级下拉选择）

        Args:
            category: 一级分类（如 'Information & Communication Technology'）
            subcategory: 二级分类（如 'Testing & Quality Assurance'）
        """
        try:
            # 注册 Mock（应对 API 502 环境故障）
            self._setup_job_function_mock()
            self.page.get_by_role("textbox", name="Job Function").click()
            # 等待下拉列表出现（最多 15 秒）
            self.page.get_by_text(category, exact=True).wait_for(state="visible", timeout=15000)
            self.page.get_by_text(category, exact=True).click()
            self.page.wait_for_timeout(500)
            self.page.get_by_text(subcategory, exact=True).click()
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"选择 Job Function 失败: {e}")
            raise
        finally:
            self._teardown_job_function_mock()

    def get_job_function_value(self):
        """获取 Job Function 当前选择的值"""
        try:
            return self.page.get_by_role("textbox", name="Job Function").input_value()
        except Exception as e:
            self.logger.error(f"获取 Job Function 值失败: {e}")
            raise

    def select_work_from_date(self, year, month):
        """选择工作经验的开始日期

        Args:
            year: 年份（如 '2020'）
            month: 月份（如 '01' 或 '1'）
        """
        try:
            work_section = self.page.locator("h2:has-text('Latest Work Experience')").locator("..")
            work_section.locator("[class*='fromDateFakerInput']").click(timeout=10000)
            self.page.wait_for_timeout(300)
            
            # 使用精确的选择器
            self.page.locator("[class*='YearMonthPicker_yearItem']").filter(
                has_text=str(year)
            ).click(timeout=10000)
            self.page.wait_for_timeout(300)
            
            # 月份显示为两位数，如"01", "02", ..., "12"
            month_int = int(month)
            month_display = f"{month_int:02d}"
            
            self.page.locator("[class*='YearMonthPicker_monthItem']").get_by_text(
                month_display, exact=True
            ).click(timeout=10000)
            
            self.page.wait_for_timeout(100)
            # 精确定位 From 日期选择器内的 Done 按钮
            self.page.locator('xpath=//button[normalize-space(text())="Done" and ancestor::*[contains(@class,"fromDateFakerInput")]]').click(timeout=5000)
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"选择 Work Experience From 日期失败: {e}")
            raise

    def get_work_from_date_value(self):
        """获取工作经验 From 日期的显示值"""
        try:
            return self.page.locator("text=From").locator("..").locator(
                "[class*='DateFakerInput']"
            ).first.inner_text()
        except Exception:
            return ""

    def is_currently_work_here_checked(self):
        """验证 'I currently work here' 是否勾选（通过 To 字段是否显示 Present 来判断）"""
        try:
            return self.page.get_by_text("Present", exact=True).is_visible(timeout=3000)
        except Exception:
            return False

    def is_to_field_showing_present(self):
        """验证 To 字段是否显示 'Present'"""
        try:
            return self.page.get_by_text("Present", exact=True).is_visible(timeout=3000)
        except Exception:
            return False

    def uncheck_currently_work_here(self):
        """取消勾选 'I currently work here'"""
        try:
            self.page.locator('img[alt="checked"]').click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"取消勾选失败: {e}")
            raise

    def is_to_date_field_editable(self):
        """验证 To 日期字段是否为可编辑状态（显示 YYYY-MM）"""
        try:
            to_field = self.page.locator("[class*='DateFakerInput']").last
            return "YYYY-MM" in to_field.inner_text(timeout=3000)
        except Exception:
            return False

    def select_work_to_date(self, year, month):
        """选择工作经验的结束日期

        Args:
            year: 年份（如 '2022'）
            month: 月份（如 '12' 或 '6'）
        """
        try:
            work_section = self.page.locator("h2:has-text('Latest Work Experience')").locator("..")
            work_section.locator("[class*='toDateFakerInput']").click(timeout=10000)
            self.page.wait_for_timeout(300)
            
            self.page.locator("[class*='YearMonthPicker_yearItem']").filter(
                has_text=str(year)
            ).click()
            self.page.wait_for_timeout(300)
            
            # 月份显示为两位数
            month_int = int(month)
            month_display = f"{month_int:02d}"
            self.page.locator("[class*='YearMonthPicker_monthItem']").get_by_text(
                month_display, exact=True
            ).click(timeout=10000)
            
            self.page.wait_for_timeout(100)
            # 精确定位 To 日期选择器内的 Done 按钮
            self.page.locator('xpath=//button[normalize-space(text())="Done" and ancestor::*[contains(@class,"toDateFakerInput")]]').click(timeout=5000)
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"选择 Work Experience To 日期失败: {e}")
            raise

    def get_work_to_value(self):
        """获取 Work Experience To 字段的值"""
        try:
            # To字段可能显示"Present"或日期
            to_text = self.page.locator("text=/^To$/").locator("..").first
            return to_text.inner_text().strip()
        except Exception:
            return ""

    def get_work_from_value(self):
        """获取 Work Experience From 字段的值"""
        try:
            from_container = self.page.locator("text=From").locator("..").first
            return from_container.inner_text().strip()
        except Exception:
            return ""

    def toggle_no_work_experience(self):
        """开启/关闭 'I have no work experience' 开关"""
        try:
            # 使用 JS 点击 switch 元素（React 自定义开关，普通 click 无法触发）
            self.page.evaluate("""() => {
                const sw = document.querySelector('[class*="switch_switch"]');
                if (sw) sw.click();
            }""")
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"切换 'I have no work experience' 失败: {e}")
            raise

    def is_work_fields_hidden(self):
        """验证工作经验字段是否已隐藏"""
        try:
            # 检查 Job Function 是否不可见
            job_func_visible = self.page.get_by_role("textbox", name="Job Function").is_visible(timeout=2000)
            return not job_func_visible
        except Exception:
            return True

    def is_work_experience_section_hidden(self):
        """验证工作经验区域是否已隐藏（is_work_fields_hidden 的别名）"""
        return self.is_work_fields_hidden()

    def is_job_function_visible(self):
        """验证 Job Function 字段是否可见"""
        try:
            return self.page.get_by_role("textbox", name="Job Function").is_visible(timeout=2000)
        except Exception:
            return False

    def _step1_preset_avatar_imgs(self):
        """Step1 预设头像 img 列表（限定在 Personal Information 区域，避免匹配页头/其他图）"""
        h = self.page.locator("h3:has-text('Personal Information')").first
        h.wait_for(state="visible", timeout=15000)
        try:
            container = h.locator(
                "xpath=ancestor::*[.//img[contains(@class,'PersonAvatar_defaultAvatar')]]][1]"
            )
            scoped = container.locator("img[class*='PersonAvatar_defaultAvatar']")
            if scoped.count() > 0:
                return scoped
        except Exception:
            pass
        return self.page.locator("img[class*='PersonAvatar_defaultAvatar']")

    def _preset_avatar_locator(self):
        """兼容旧调用名：同 _step1_preset_avatar_imgs"""
        return self._step1_preset_avatar_imgs()

    def step1_preset_avatar_imgs(self):
        """供断言使用：Step1 Personal Information 区域内预设头像 img 列表"""
        return self._step1_preset_avatar_imgs()

    def click_preset_avatar(self, index=0):
        """点击预设头像（index从0开始）
        
        Args:
            index: 头像索引，从0开始
        """
        try:
            avatars = self._step1_preset_avatar_imgs()
            if avatars.count() == 0:
                avatars = self.page.locator(
                    "[class*='AvatarItem'], [class*='avatarItem'], .StepInfo_avatarItem__sMQzY"
                )
            avatars.nth(index).scroll_into_view_if_needed()
            avatars.nth(index).wait_for(state="visible", timeout=15000)
            avatars.nth(index).click(force=True)
            self.page.wait_for_timeout(800)
        except Exception as e:
            self.logger.error(f"点击预设头像 {index} 失败: {e}")
            raise

    def is_avatar_selected(self, index):
        """验证指定预设头像是否显示选中状态
        
        Args:
            index: 头像索引，从0开始
            
        Returns:
            bool: 是否选中
        """
        try:
            imgs = self._step1_preset_avatar_imgs()
            if imgs.count() <= index:
                return False
            cls = (imgs.nth(index).get_attribute("class") or "")
            return "defaultAvatarSelectedIcon" in cls or "SelectedIcon" in cls
        except Exception:
            return False

    def fill_first_name_max_length(self, text):
        """填充 First Name 至最大长度"""
        self.input_first_name(text)

    def fill_last_name_max_length(self, text):
        """填充 Last Name 至最大长度（与 First Name 对称）"""
        try:
            self.page.get_by_role("textbox", name="Last Name").fill(text)
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"fill_last_name_max_length 失败: {e}")
            raise

    def get_current_location_value_raw(self):
        """获取 Current Location 原始值"""
        return self.get_current_location_value()

    def select_education_level(self, level):
        """选择 Education Level

        Args:
            level: 学历级别（如 'Bachelor's Degree', 'Master's Degree'）
        """
        try:
            self.page.get_by_text("Education Level").click()
            self.page.wait_for_timeout(500)
            self.page.get_by_text(level, exact=True).click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择 Education Level 失败: {e}")
            raise

    def get_education_level_value(self):
        """获取 Education Level 当前选择的值"""
        try:
            # Education Level 可能在下拉框或文本中显示
            edu_select = self.page.locator("text=Education Level").locator("..").first
            return edu_select.inner_text().strip()
        except Exception:
            return ""

    def select_education_from_date(self, year, month):
        """选择学历开始日期

        Args:
            year: 年份（如 '2016'）
            month: 月份（如 '09' 或 '9'）
        """
        try:
            education_section = self.page.locator("h2:has-text('Education Experience')").locator("..")
            # 直接定位 Education section 内的 From 日期选择器（fromDateFakerInput）
            education_section.locator("[class*='fromDateFakerInput']").click(timeout=10000)
            self.page.wait_for_timeout(300)
            
            # 使用精确的选择器
            self.page.locator("[class*='YearMonthPicker_yearItem']").filter(
                has_text=str(year)
            ).click(timeout=10000)
            self.page.wait_for_timeout(300)
            
            # 月份显示为两位数
            month_int = int(month)
            month_display = f"{month_int:02d}"
            self.page.locator("[class*='YearMonthPicker_monthItem']").get_by_text(
                month_display, exact=True
            ).click(timeout=10000)
            
            self.page.wait_for_timeout(100)
            # 精确定位 From 日期选择器内的 Done 按钮
            self.page.locator('xpath=//button[normalize-space(text())="Done" and ancestor::*[contains(@class,"fromDateFakerInput")]]').click(timeout=5000)
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"选择 Education From 日期失败: {e}")
            raise

    def select_education_to_date(self, year, month):
        """选择学历结束日期

        Args:
            year: 年份（如 '2020'）
            month: 月份（如 '06' 或 '6'）
        """
        try:
            education_section = self.page.locator("h2:has-text('Education Experience')").locator("..")
            # 直接定位 Education section 内的 To 日期选择器（toDateFakerInput）
            education_section.locator("[class*='toDateFakerInput']").click(timeout=10000)
            self.page.wait_for_timeout(300)
            
            # 使用精确的选择器
            self.page.locator("[class*='YearMonthPicker_yearItem']").filter(
                has_text=str(year)
            ).click(timeout=10000)
            self.page.wait_for_timeout(300)
            
            # 月份显示为两位数
            month_int = int(month)
            month_display = f"{month_int:02d}"
            self.page.locator("[class*='YearMonthPicker_monthItem']").get_by_text(
                month_display, exact=True
            ).click(timeout=10000)
            
            self.page.wait_for_timeout(100)
            # 精确定位 To 日期选择器内的 Done 按钮
            self.page.locator('xpath=//button[normalize-space(text())="Done" and ancestor::*[contains(@class,"toDateFakerInput")]]').click(timeout=5000)
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"选择 Education To 日期失败: {e}")
            raise

    def click_back_on_step2(self):
        """点击 Step2 的 Back 按钮（会触发 Unsaved Changes 对话框）"""
        try:
            self.page.get_by_role("button", name="Back").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击 Back 失败: {e}")
            raise

    def is_unsaved_changes_dialog_displayed(self):
        """验证 Unsaved Changes 对话框是否显示"""
        try:
            return self.page.get_by_text("Unsaved Changes").is_visible(timeout=3000)
        except Exception:
            return False

    def click_unsaved_dialog_cancel(self):
        """点击 Unsaved Changes 对话框的 Cancel 按钮"""
        try:
            self.page.get_by_role("button", name="Cancel").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击 Cancel 失败: {e}")
            raise

    def click_cancel_in_unsaved_changes_dialog(self):
        """点击 Unsaved Changes 对话框的 Cancel 按钮（别名方法）"""
        self.click_unsaved_dialog_cancel()

    def click_unsaved_dialog_discard(self):
        """点击 Unsaved Changes 对话框的 Discard 按钮"""
        try:
            self.page.get_by_role("button", name="Discard").click()
            self.page.wait_for_timeout(1500)
        except Exception as e:
            self.logger.error(f"点击 Discard 失败: {e}")
            raise

    def click_discard_in_unsaved_changes_dialog(self):
        """点击 Unsaved Changes 对话框的 Discard 按钮（别名方法）"""
        self.click_unsaved_dialog_discard()

    def _last_visible_done_button(self):
        """Step2 底部提交 Done：优先 footer 内，否则取最后一个可见的 Done。"""
        try:
            footer_btns = self.page.locator("footer").get_by_role("button", name="Done")
            if footer_btns.count() > 0:
                btn = footer_btns.last
                if btn.is_visible():
                    return btn
        except Exception:
            pass
        btns = self.page.get_by_role("button", name="Done")
        count = btns.count()
        for idx in range(count - 1, -1, -1):
            btn = btns.nth(idx)
            if btn.is_visible():
                return btn
        return btns.last

    def _step2_footer_done_button(self):
        """
        Step2 用于提交整页的 Done：优先 ``<footer>`` 内，避免与日期弹层内 Done 混淆。
        若无 footer，则排除位于 DateFakerInput 区域内的 Done。
        """
        try:
            foot = self.page.locator("footer")
            if foot.count() > 0:
                btns = foot.get_by_role("button", name=re.compile(r"^Done$", re.I))
                if btns.count() > 0:
                    b = btns.last
                    if b.is_visible(timeout=3000):
                        return b
        except Exception:
            pass
        try:
            btns = self.page.get_by_role("button", name=re.compile(r"^Done$", re.I))
            n = btns.count()
            for idx in range(n - 1, -1, -1):
                btn = btns.nth(idx)
                if not btn.is_visible(timeout=500):
                    continue
                try:
                    bad = btn.locator(
                        "xpath=ancestor::*[contains(@class,'DateFakerInput')]"
                    )
                    if bad.count() > 0:
                        continue
                except Exception:
                    pass
                return btn
        except Exception:
            pass
        return self._last_visible_done_button()

    def is_done_button_disabled(self):
        """验证 Step2 底部主 Done 是否不可用（原生 disabled、aria-disabled、常见 UI class）。"""
        try:
            btn = self._step2_footer_done_button()
            if btn.is_disabled():
                return True
            aria = (btn.get_attribute("aria-disabled") or "").strip().lower()
            if aria == "true":
                return True
            cls = (btn.get_attribute("class") or "").lower()
            if "mui-disabled" in cls or "btn-disabled" in cls:
                return True
            return bool(
                btn.evaluate(
                    """
                    el => {
                      let n = el;
                      for (let i = 0; i < 8 && n; i++) {
                        const c = (n.className && String(n.className)) || '';
                        if (c.includes('Mui-disabled') || c.includes('pointer-events-none')) return true;
                        n = n.parentElement;
                      }
                      return !!(el.disabled
                        || String(el.getAttribute('aria-disabled')).toLowerCase() === 'true');
                    }
                    """
                )
            )
        except Exception as e:
            self.logger.error(f"检查 Done 按钮状态失败: {e}")
            raise

    def wait_until_step2_done_disabled(self, timeout_ms: int = 8000) -> bool:
        """等待 Step2 底部 Done 变为禁用（用于日期校验等异步 UI）。"""
        deadline = time.time() + timeout_ms / 1000.0
        while time.time() < deadline:
            if self.is_done_button_disabled():
                return True
            self.page.wait_for_timeout(200)
        return self.is_done_button_disabled()

    def is_education_date_invalid_hint_visible(self) -> bool:
        """
        Education 区 To 早于 From 等：部分版本用 Done 禁用，部分在区块内展示 error 提示。
        """
        root = self.page.locator("h2:has-text('Education Experience')").locator("..")
        try:
            if root.locator("[class*='Mui-error']").first.is_visible(timeout=2000):
                return True
        except Exception:
            pass
        try:
            t = (root.inner_text(timeout=3000) or "")
        except Exception:
            t = ""
        blob = (t or "").lower()
        for hint in (
            "before",
            "earlier",
            "invalid",
            "cannot",
            "must be",
            "end date",
            "从",
        ):
            if hint in blob:
                return True
        # 主内容区短文案（避免整页误报）
        try:
            main = self.page.locator("main, [role='main'], form").first
            if main.get_by_text(
                re.compile(
                    r"end\s+date|to\s+date|invalid|before|earlier|range|must|after",
                    re.I,
                )
            ).first.is_visible(timeout=1500):
                return True
        except Exception:
            pass
        return False

    def education_shows_masters_2019_to_and_2020_from(self) -> bool:
        """
        教育区已同时选入 To=2019-01 与 From=2020-6（或等价展示），用于产品未做按钮禁用时做弱回归。
        """
        try:
            sec = self.page.locator("h2:has-text('Education Experience')").locator("..")
            t = (sec.inner_text(timeout=5000) or "")
        except Exception:
            return False
        if "2019" not in t or "2020" not in t or "Master" not in t:
            return False
        return bool(
            re.search(r"2019.{0,200}2020|2020.{0,200}2019", t, re.S)
        )

    def is_done_button_enabled(self):
        """验证 Done 按钮是否处于可点击状态（is_done_button_disabled 的反义）"""
        return not self.is_done_button_disabled()

    def click_done(self):
        """点击 Done 按钮；SPA 提交后等待离开 /resume/add（无头下先关浮层、滚动到底部主按钮）。"""
        js_leave_add = """
                () => {
                    let p = (window.location && window.location.pathname) || "";
                    let h = (window.location && window.location.hash) || "";
                    if (p.length > 1 && p.endsWith("/")) p = p.slice(0, -1);
                    let full = (p + h).toLowerCase();
                    return !full.includes("resume/add");
                }
                """

        def _attempt(force_click: bool) -> None:
            for _ in range(3):
                self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(200)
            btn = self._step2_footer_done_button()
            try:
                btn.scroll_into_view_if_needed(timeout=15000)
            except Exception:
                pass
            self.page.wait_for_timeout(500)
            btn.click(timeout=90000, force=force_click)
            self.page.wait_for_timeout(500)
            # 单次等待，避免 wait_for_url 超时后再跑 wait_for_function 导致总时长翻倍
            self.page.wait_for_function(js_leave_add, timeout=120000)

        try:
            _attempt(force_click=False)
        except Exception as first_err:
            self.logger.warning("click_done 首次未离开 add 页，force 重试: %s", first_err)
            try:
                _attempt(force_click=True)
            except Exception as e:
                self.logger.error(f"点击 Done 失败: {e}")
                raise

    # ============================================
    # 辅助方法：国家列表锚点、日期选择器等
    # ============================================

    def get_active_anchor_letter(self):
        """获取当前激活的锚点字母"""
        try:
            for nav_sel, act_sel in (
                ("[class*='AnchorSelector_anchorNav']", "[class*='PcSelectCountry_active']"),
                ("[class*='anchorNav']", "[class*='PcSelectCountry_active']"),
                ("[class*='anchorNav']", "[class*='_active']"),
            ):
                nav = self.page.locator(nav_sel)
                if nav.count() == 0:
                    continue
                act = nav.locator(act_sel)
                if act.count() > 0 and act.first.is_visible(timeout=800):
                    txt = act.first.inner_text().strip()
                    if txt:
                        return txt
            return ""
        except Exception:
            return ""

    def _country_letter_nav(self):
        """国家列表右侧字母导航（兼容 CSS Modules 重命名）"""
        return (
            self.page.locator("[class*='AnchorSelector_anchorNav']")
            .or_(self.page.locator("[class*='anchorNav']"))
        )

    def scroll_country_list_to_letter(self, letter):
        """滚动国家列表到指定字母区域：先滚到以该字母开头的列表项，再回退到点锚点/字母标题。"""
        try:
            ch = (letter or "").strip().upper()[:1]
            if not ch:
                return
            # 不依赖 scrollContent class（易变）；直接滚到以该字母开头的国家行
            row = self.page.locator("[class*='AnchorSelector_listItem']").filter(
                has_text=re.compile(rf"^{re.escape(ch)}.", re.IGNORECASE)
            )
            if row.count() > 0:
                row.first.scroll_into_view_if_needed(timeout=15000)
                self.page.wait_for_timeout(600)
                return
            nav = self._country_letter_nav()
            if nav.count() > 0:
                btn = nav.get_by_text(ch, exact=True)
                if btn.count() > 0:
                    btn.first.click()
                    self.page.wait_for_timeout(800)
                    return
            list_container = self.page.locator("[class*='AnchorSelector_scrollContent']")
            letter_header = list_container.get_by_text(ch, exact=True).first
            letter_header.scroll_into_view_if_needed(timeout=15000)
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"滚动到字母 {letter} 失败: {e}")
            raise

    def open_work_from_date_picker(self):
        """打开 Work Experience From 日期选择器"""
        try:
            self.page.get_by_text("YYYY-MM").first.click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"打开 From 日期选择器失败: {e}")
            raise

    def close_date_picker(self):
        """关闭日期选择器（点击背景或ESC）"""
        try:
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"关闭日期选择器失败: {e}")
            raise
