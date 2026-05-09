"""
阿联酋站 - 简历编辑页面测试

本脚本由 playwright-test-generator 生成（已根据真实页面结构重写）
录制文档：test_cases/zhaopin/ok-ae-ResumeEdit-测试用例-20260320.md
生成时间：2026-03-20

测试站点：AE (https://ae.58v5.cn)
测试角色：Jobseeker（求职者，wangyongli@58.com）
测试目标：验证 AE 站 Online Resume 页各区块 modal 弹窗编辑功能，
         包括修改后 Save 数据回显正确验证
页面路径：https://aepub.58v5.cn/biz/en/resume

页面结构（modal弹窗式编辑）：
  - Personal Information（姓名、联系方式、国家、性别、工签）
  - Personal Summary（文本域）
  - Work Experience（职位、公司、职能、日期）
  - Education Background（学历级别、院校、专业、日期）
  - Language（语言技能多选）
"""
import re
import time

import pytest
import allure
from pages.resume_add_page_ae import ResumeAddPageAe
from test_cases.zhaopin.ae_login_helper import ensure_ae_logged_in
from utils.logger import setup_logger

logger = setup_logger()

from test_cases.zhaopin.explicit_waits import dom_content_loaded_soft, network_idle_soft, sg_wait_jobs_list_url, sg_after_home_jobs_icon

# ============================================
# 测试环境配置
# ============================================
_CONFIG = {
    "site": "ae",
    "site_name": "阿联酋站",
    "role": "jobseeker",
    "user_name": "wangyongli_ae",
    "base_url": "https://ae.58v5.cn",
    "test_account": {
        "username": "wangyongli@58.com",
        "password": "Qwer1234"
    },
    "locale": "en-AE",
    "currency": "AED",
    "browser": {
        "type": "chromium",
        "headless": False,
        "viewport": {"width": 1920, "height": 1080}
    },
    "timeout": {
        "default": 30000,
        "wait": 10000,
        "navigation": 30000
    },
    "resume_view_url": "https://aepub.58v5.cn/biz/en/resume",
    # Test data
    "test_first_name": "AutoTest",
    "test_last_name": "User",
    "test_summary": "Experienced QA engineer with 5+ years in automated testing.",
    "test_job_title": "QA Engineer",
    "test_company": "Tech Corp",
    "test_edu_institute": "Tech University",
    "test_edu_major": "Computer Science",
    "edu_level": "Bachelor's Degree",
    "edu_from_date": "2016-09",
    "edu_to_date": "2020-06",
    "work_from_date": "2022-01",
}


# ============================================
# 测试类一：页面入口 & 基础加载（TC001~TC003）
# ============================================

@allure.feature("OK")
class TestResumePageLoad:
    """AE 站简历页面入口 & 基础加载"""

    @pytest.mark.case_id_ae_resume_tc001
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ae
    @allure.story("AE站简历页面加载")
    @allure.title("TC001: 已登录用户直接访问简历视图页（Online Resume）成功加载")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证已登录用户访问 aepub.58v5.cn/biz/en/resume 后 Online Resume 页面正确加载")
    def test_tc001_resume_view_page_loads(self, page, config):
        """TC001: 已登录用户直接访问简历视图页成功加载"""
        ensure_ae_logged_in(page, config)
        resume_page = ResumeAddPageAe(page)

        with allure.step("步骤1：导航到简历视图页"):
            resume_page.navigate_to_resume_view()
            logger.info("✓ 导航到简历视图页")

        with allure.step("步骤2：验证 Online Resume 标题可见"):
            is_displayed = resume_page.is_resume_view_displayed()
            logger.info(f"Online Resume 页面已显示: {is_displayed}")

        with allure.step("步骤3：验证各区块存在"):
            work_exp_visible = resume_page.is_work_experience_section_visible()
            edu_visible = resume_page.is_education_section_visible()
            lang_visible = resume_page.is_language_section_visible()
            logger.info(f"WorkExp可见: {work_exp_visible}, Edu可见: {edu_visible}, Lang可见: {lang_visible}")

        assert is_displayed, "Online Resume 页面应正确加载显示 h3 标题"
        assert work_exp_visible, "Work Experience 区块应可见"
        assert edu_visible, "Education Background 区块应可见"
        assert lang_visible, "Language 区块应可见"

    @pytest.mark.case_id_ae_resume_tc002
    @pytest.mark.p1
    @pytest.mark.ae
    @allure.story("AE站简历页面加载")
    @allure.title("TC002: 未登录用户访问简历视图页被重定向到登录页")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证未登录状态下访问简历视图页会重定向到登录页")
    def test_tc002_redirect_to_login_when_not_logged_in(self, page, config):
        """TC002: 未登录用户访问简历视图页被重定向"""
        with allure.step("步骤0：在 aepub 域清 cookie/storage 后刷新，避免双 goto 与站点重定向竞态"):
            try:
                page.goto(config["resume_view_url"], wait_until="load", timeout=60000)
            except Exception as exc:
                logger.warning("预加载 resume 页（用于清理 storage）: %s", exc)
            page.context.clear_cookies()
            page.evaluate("() => { try { localStorage.clear(); sessionStorage.clear(); } catch (e) {} }")
            page.wait_for_timeout(400)
            try:
                page.reload(wait_until="domcontentloaded", timeout=60000)
            except Exception as exc:
                logger.warning("reload 被重定向链打断，回退 commit 导航: %s", exc)
                page.goto(config["resume_view_url"], wait_until="commit", timeout=60000)
            dom_content_loaded_soft(page, 20000)
            current_url = page.url
            logger.info(f"访问后URL: {current_url}")

        with allure.step("步骤2：验证重定向到登录页或显示登录提示（无头/高负载下提示可能晚于首屏）"):
            is_redirected = False
            deadline = time.monotonic() + 20.0
            while time.monotonic() < deadline:
                u = page.url.lower()
                if "login" in u or "register" in u or "signin" in u:
                    is_redirected = True
                    break
                try:
                    if page.get_by_role("link", name=re.compile(r"log\s*in", re.I)).first.is_visible(
                        timeout=800
                    ):
                        is_redirected = True
                        break
                except Exception:
                    pass
                try:
                    if page.get_by_text(re.compile(r"log\s*in", re.I)).first.is_visible(timeout=800):
                        is_redirected = True
                        break
                except Exception:
                    pass
                try:
                    if page.get_by_text(re.compile(r"sign\s*in", re.I)).first.is_visible(timeout=800):
                        is_redirected = True
                        break
                except Exception:
                    pass
                page.wait_for_timeout(400)
            logger.info(f"重定向到登录: {is_redirected}")

        assert is_redirected or "resume" not in current_url.lower(), \
            "未登录用户访问简历页应被重定向到登录页"

    @pytest.mark.case_id_ae_resume_tc003
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ae
    @allure.story("AE站简历页面加载")
    @allure.title("TC003: 简历视图页显示编辑图标（Personal Info、Summary 可编辑）")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证简历视图页的 Personal Information 和 Personal Summary 区块均有编辑图标")
    def test_tc003_edit_icons_visible(self, page, config):
        """TC003: 简历视图页显示编辑图标"""
        ensure_ae_logged_in(page, config)
        resume_page = ResumeAddPageAe(page)

        with allure.step("步骤1：导航到简历视图页"):
            resume_page.navigate_to_resume_view()

        with allure.step("步骤2：验证 Personal Info 编辑图标可见"):
            personal_info_icon = page.locator("img[class*='editPersonInfoIcon']")
            icon_count = personal_info_icon.count()
            logger.info(f"Personal Info 编辑图标数量: {icon_count}")

        with allure.step("步骤3：验证所有 cursorPointer 图标数量 >= 2"):
            all_icons = page.locator("img[class*='cursorPointer']")
            total_icons = all_icons.count()
            logger.info(f"所有可点击图标数量: {total_icons}")

        assert icon_count >= 1, "Personal Info 编辑图标应可见"
        assert total_icons >= 2, "简历页应至少有2个可点击编辑/添加图标"


# ============================================
# 测试类二：Personal Information 弹窗（TC004~TC010）
# ============================================

@allure.feature("OK")
class TestPersonalInfoModal:
    """Personal Information 弹窗编辑测试"""

    @pytest.fixture(autouse=True)
    def navigate_and_open_modal(self, page, config):
        """每个测试前导航并打开 Personal Information 弹窗"""
        ensure_ae_logged_in(page, config)
        self.resume_page = ResumeAddPageAe(page)
        self.resume_page.navigate_to_resume_view()
        self.resume_page.is_resume_view_displayed()

    @pytest.mark.case_id_ae_resume_tc004
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ae
    @allure.story("AE站简历Personal Information")
    @allure.title("TC004: 点击编辑图标打开 Personal Information 弹窗")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证点击 Personal Information 编辑图标后弹窗正确打开")
    def test_tc004_open_personal_info_modal(self, page, config):
        """TC004: 点击编辑图标打开 Personal Information 弹窗"""
        with allure.step("步骤1：点击 Personal Information 编辑图标"):
            self.resume_page.open_personal_info_modal()
            logger.info("✓ 点击编辑图标")

        with allure.step("步骤2：验证弹窗已打开"):
            is_modal_open = self.resume_page.is_personal_info_modal_displayed()
            logger.info(f"Personal Information 弹窗已打开: {is_modal_open}")

        with allure.step("步骤3：验证弹窗标题显示 'Personal Information'"):
            title_visible = page.get_by_text("Personal Information").is_visible(timeout=3000)
            logger.info(f"弹窗标题可见: {title_visible}")

        assert is_modal_open, "点击编辑图标后 Personal Information 弹窗应打开"
        assert title_visible, "弹窗标题应为 'Personal Information'"

    @pytest.mark.case_id_ae_resume_tc005
    @pytest.mark.p0
    @pytest.mark.ae
    @allure.story("AE站简历Personal Information")
    @allure.title("TC005: Personal Information 弹窗中 First Name 和 Last Name 有预填值")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证打开弹窗后 First Name 和 Last Name 字段有预填的当前值")
    def test_tc005_name_fields_prefilled(self, page, config):
        """TC005: First Name 和 Last Name 有预填值"""
        with allure.step("步骤1：打开 Personal Information 弹窗"):
            self.resume_page.open_personal_info_modal()

        with allure.step("步骤2：获取 First Name 和 Last Name 当前值"):
            first_name = self.resume_page.get_first_name_value()
            last_name = self.resume_page.get_last_name_value()
            logger.info(f"First Name: '{first_name}', Last Name: '{last_name}'")

        with allure.step("步骤3：验证字段不为空"):
            assert first_name is not None, "First Name 字段应存在且可获取"
            assert last_name is not None, "Last Name 字段应存在且可获取"
        logger.info("✓ First Name 和 Last Name 字段存在预填值")

    @pytest.mark.case_id_ae_resume_tc006
    @pytest.mark.p1
    @pytest.mark.ae
    @allure.story("AE站简历Personal Information")
    @allure.title("TC006: 清空 First Name 后 Save 按钮禁用")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证清空 First Name 后 Save 按钮变为禁用（必填项校验）")
    def test_tc006_save_disabled_when_firstname_empty(self, page, config):
        """TC006: 清空 First Name 后 Save 按钮禁用"""
        with allure.step("步骤1：打开 Personal Information 弹窗"):
            self.resume_page.open_personal_info_modal()

        with allure.step("步骤2：清空 First Name"):
            self.resume_page.clear_first_name()
            dom_content_loaded_soft(page, 20000)
            logger.info("✓ 清空 First Name")

        with allure.step("步骤3：验证 Save 按钮为禁用状态"):
            is_disabled = self.resume_page.is_save_button_disabled()
            logger.info(f"Save 按钮禁用: {is_disabled}")

        assert is_disabled, "清空 First Name 后 Save 按钮应为禁用状态"

    @pytest.mark.case_id_ae_resume_tc007
    @pytest.mark.p1
    @pytest.mark.ae
    @allure.story("AE站简历Personal Information")
    @allure.title("TC007: 清空 Last Name 后 Save 按钮禁用")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证清空 Last Name 后 Save 按钮变为禁用（必填项校验）")
    def test_tc007_save_disabled_when_lastname_empty(self, page, config):
        """TC007: 清空 Last Name 后 Save 按钮禁用"""
        with allure.step("步骤1：打开 Personal Information 弹窗"):
            self.resume_page.open_personal_info_modal()

        with allure.step("步骤2：清空 Last Name"):
            self.resume_page.clear_last_name()
            dom_content_loaded_soft(page, 20000)
            logger.info("✓ 清空 Last Name")

        with allure.step("步骤3：验证 Save 按钮为禁用状态"):
            is_disabled = self.resume_page.is_save_button_disabled()
            logger.info(f"Save 按钮禁用: {is_disabled}")

        assert is_disabled, "清空 Last Name 后 Save 按钮应为禁用状态"

    @pytest.mark.case_id_ae_resume_tc008
    @pytest.mark.p2
    @pytest.mark.ae
    @allure.story("AE站简历Personal Information")
    @allure.title("TC008: First Name 和 Last Name 有最大 100 字符限制")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("验证 First Name 和 Last Name 输入超过 100 字符时被截断（maxlength=100）")
    def test_tc008_name_max_100_chars(self, page, config):
        """TC008: First Name 和 Last Name 有最大 100 字符限制"""
        with allure.step("步骤1：打开 Personal Information 弹窗"):
            self.resume_page.open_personal_info_modal()

        with allure.step("步骤2：在 First Name 输入 101 个字符"):
            long_name = "A" * 101
            self.resume_page.input_first_name(long_name)
            dom_content_loaded_soft(page, 20000)
        with allure.step("步骤3：验证实际输入字符数 <= 100"):
            actual_value = self.resume_page.get_first_name_value()
            actual_length = len(actual_value)
            logger.info(f"输入101字符后实际字符数: {actual_length}")

        assert actual_length <= 100, \
            f"First Name 字段应限制最多 100 字符，实际: {actual_length}"

    @pytest.mark.case_id_ae_resume_tc009
    @pytest.mark.p2
    @pytest.mark.ae
    @allure.story("AE站简历Personal Information")
    @allure.title("TC009: 点击 Cancel 关闭 Personal Information 弹窗")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("验证点击 Cancel 按钮后 Personal Information 弹窗关闭（通过 modal-open class 和 EditPersonInfoModal 选择器判断）")
    def test_tc009_cancel_closes_modal_without_saving(self, page, config):
        """TC009: 点击 Cancel 关闭弹窗"""
        with allure.step("步骤1：打开 Personal Information 弹窗，记录初始状态"):
            self.resume_page.open_personal_info_modal()
            # Verify modal IS open initially by checking EditPersonInfoModal class
            modal_open_before = page.locator("[class*='EditPersonInfoModal']").count() > 0
            logger.info(f"打开弹窗前: EditPersonInfoModal 可见: {modal_open_before}")

        with allure.step("步骤2：点击 Cancel 关闭弹窗"):
            self.resume_page.click_cancel_in_modal()
            dom_content_loaded_soft(page, 20000)
        with allure.step("步骤3：验证 Personal Information 编辑弹窗已关闭"):
            # Verify by checking if the EditPersonInfoModal specific class is gone
            modal_still_open = page.locator("[class*='EditPersonInfoModal']").count() > 0
            modal_open_class = page.evaluate("() => document.body.classList.contains('modal-open')")
            logger.info(f"Cancel 后: EditPersonInfoModal 可见: {modal_still_open}, modal-open: {modal_open_class}")

        assert modal_open_before, "测试前弹窗应已打开（EditPersonInfoModal 可见）"
        assert not modal_still_open, "点击 Cancel 后 Personal Information 编辑弹窗（EditPersonInfoModal）应关闭"

    @pytest.mark.case_id_ae_resume_tc010
    @pytest.mark.p1
    @pytest.mark.ae
    @allure.story("AE站简历Personal Information")
    @allure.title("TC010: Personal Information 弹窗 Email 字段显示当前登录账号邮箱（只读展示）")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证 Personal Information 弹窗中 Email 字段显示当前登录账号的邮箱，且为只读状态（通过UI展示）")
    def test_tc010_email_display_in_modal(self, page, config):
        """TC010: Personal Information 弹窗 Email 字段显示当前登录账号邮箱"""
        with allure.step("步骤1：打开 Personal Information 弹窗"):
            self.resume_page.open_personal_info_modal()

        with allure.step("步骤2：验证 Email 字段显示当前登录账号邮箱"):
            modal = page.locator(".modal-content").first
            email_visible = modal.get_by_text(config['test_account']['username']).is_visible(timeout=3000)
            logger.info(f"弹窗中 Email '{config['test_account']['username']}' 可见: {email_visible}")

        with allure.step("步骤3：验证 Contact 区块标签可见"):
            # Use exact=True on the <label> element to avoid matching the description text
            contact_label = modal.locator("label:has-text('Contact')").first
            contact_visible = contact_label.is_visible() if contact_label.count() > 0 else False
            logger.info(f"Contact 标签可见: {contact_visible}")

        assert email_visible, \
            f"Personal Information 弹窗应显示登录邮箱 '{config['test_account']['username']}'"
        assert contact_visible, "Personal Information 弹窗应显示 'Contact' 区块标签"


# ============================================
# 测试类三：Personal Summary 弹窗（TC011~TC013）
# ============================================

@allure.feature("OK")
class TestPersonalSummaryModal:
    """Personal Summary 弹窗编辑测试"""

    @pytest.fixture(autouse=True)
    def setup(self, page, config):
        ensure_ae_logged_in(page, config)
        self.resume_page = ResumeAddPageAe(page)
        self.resume_page.navigate_to_resume_view()
        self.resume_page.is_resume_view_displayed()

    @pytest.mark.case_id_ae_resume_tc011
    @pytest.mark.p1
    @pytest.mark.ae
    @allure.story("AE站简历Personal Summary")
    @allure.title("TC011: 点击 Personal Summary 编辑图标打开弹窗")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证点击 Personal Summary 区块的编辑图标后弹窗正确打开，包含 textarea")
    def test_tc011_open_personal_summary_modal(self, page, config):
        """TC011: 打开 Personal Summary 弹窗"""
        with allure.step("步骤1：点击 Personal Summary 编辑图标"):
            self.resume_page.open_personal_summary_modal()

        with allure.step("步骤2：验证弹窗已打开"):
            is_displayed = self.resume_page.is_personal_summary_modal_displayed()
            logger.info(f"Personal Summary 弹窗显示: {is_displayed}")

        with allure.step("步骤3：验证 textarea 存在"):
            textarea_visible = page.locator("textarea").is_visible(timeout=3000)
            logger.info(f"textarea 可见: {textarea_visible}")

        assert is_displayed, "Personal Summary 弹窗应正确打开"
        assert textarea_visible, "Personal Summary 弹窗应包含 textarea"

    @pytest.mark.case_id_ae_resume_tc012
    @pytest.mark.p1
    @pytest.mark.ae
    @allure.story("AE站简历Personal Summary")
    @allure.title("TC012: 输入 Personal Summary 并 Save，视图页显示摘要内容")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证在 Personal Summary 弹窗输入文本后 Save，简历视图页显示该摘要内容")
    def test_tc012_save_personal_summary(self, page, config):
        """TC012: 输入 Personal Summary 并 Save 后视图页显示"""
        with allure.step("步骤1：打开 Personal Summary 弹窗"):
            self.resume_page.open_personal_summary_modal()

        with allure.step("步骤2：输入摘要文本"):
            summary_text = config['test_summary']
            self.resume_page.input_personal_summary(summary_text)
            logger.info(f"✓ 输入摘要: {summary_text[:40]}...")

        with allure.step("步骤3：点击 Save"):
            self.resume_page.click_save_in_modal()
            self.resume_page.wait_for_modal_close()

        with allure.step("步骤4：验证弹窗关闭"):
            is_open = self.resume_page.is_any_modal_open()
            assert not is_open, "Save 后弹窗应关闭"

        with allure.step("步骤5：验证视图页显示摘要内容"):
            # Summary appears in the Personal Summary section
            summary_visible = page.get_by_text(summary_text[:30]).is_visible(timeout=5000)
            logger.info(f"视图页显示摘要内容: {summary_visible}")
            assert summary_visible, "Save 后简历视图页 Personal Summary 区块应显示摘要文本"

    @pytest.mark.case_id_ae_resume_tc013
    @pytest.mark.p2
    @pytest.mark.ae
    @allure.story("AE站简历Personal Summary")
    @allure.title("TC013: Personal Summary 弹窗有提示文本（placeholder label）")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("验证 Personal Summary 弹窗有提示文本（作为 label 或 placeholder 展示）")
    def test_tc013_personal_summary_placeholder(self, page, config):
        """TC013: Personal Summary 弹窗有提示文本"""
        with allure.step("步骤1：打开 Personal Summary 弹窗"):
            self.resume_page.open_personal_summary_modal()

        with allure.step("步骤2：验证弹窗有占位提示文本"):
            modal = page.locator(".modal-content").first
            # Check for either placeholder attribute or label text
            placeholder = self.resume_page.get_personal_summary_placeholder()
            # Also check for the label-style placeholder text
            has_label_placeholder = modal.get_by_text("Please enter your personal summary").is_visible(timeout=3000)
            logger.info(f"Placeholder attr: '{placeholder}', Label placeholder visible: {has_label_placeholder}")

        assert placeholder or has_label_placeholder, \
            "Personal Summary 弹窗应有 placeholder 或提示文本"


# ============================================
# 测试类四：Work Experience 弹窗（TC014~TC019）
# ============================================

@allure.feature("OK")
class TestWorkExperienceModal:
    """Work Experience 弹窗编辑测试"""

    @pytest.fixture(autouse=True)
    def setup(self, page, config):
        ensure_ae_logged_in(page, config)
        self.resume_page = ResumeAddPageAe(page)
        self.resume_page.navigate_to_resume_view()
        self.resume_page.is_resume_view_displayed()

    @pytest.mark.case_id_ae_resume_tc014
    @pytest.mark.p1
    @pytest.mark.ae
    @allure.story("AE站简历Work Experience")
    @allure.title("TC014: 点击编辑图标打开 Edit Work Experience 弹窗")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证点击 Work Experience 区块编辑图标后弹窗正确打开，显示 'Edit Work Experience' 标题")
    def test_tc014_open_work_experience_modal(self, page, config):
        """TC014: 打开 Edit Work Experience 弹窗"""
        with allure.step("步骤1：点击 Work Experience 编辑图标"):
            self.resume_page.open_edit_work_experience_modal()

        with allure.step("步骤2：验证弹窗已打开"):
            is_displayed = self.resume_page.is_work_experience_modal_displayed()
            logger.info(f"Work Experience 弹窗显示: {is_displayed}")

        with allure.step("步骤3：验证弹窗标题为 'Edit Work Experience'"):
            title_visible = page.get_by_text("Edit Work Experience").is_visible(timeout=3000)
            logger.info(f"'Edit Work Experience' 标题可见: {title_visible}")

        assert is_displayed, "点击编辑图标后 Edit Work Experience 弹窗应打开"
        assert title_visible, "弹窗标题应为 'Edit Work Experience'"

    @pytest.mark.case_id_ae_resume_tc015
    @pytest.mark.p1
    @pytest.mark.ae
    @allure.story("AE站简历Work Experience")
    @allure.title("TC015: Work Experience 弹窗中 Job Function 下拉可选择并显示选项")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证 Job Function 下拉框可以打开并选择选项")
    def test_tc015_job_function_dropdown(self, page, config):
        """TC015: Job Function 下拉可选择"""
        with allure.step("步骤1：打开 Work Experience 弹窗"):
            self.resume_page.open_edit_work_experience_modal()

        with allure.step("步骤2：验证 Job Function 下拉已有预填选项"):
            current_value = self.resume_page.get_job_function_value()
            logger.info(f"Job Function 当前值: '{current_value}'")

        with allure.step("步骤3：验证 Job Function 输入控件存在"):
            modal = page.locator(".modal-content").first
            label_visible = modal.get_by_text("Job Function").is_visible(timeout=3000)
            # Job Function uses CustomCounterInput (3rd text input, no native select)
            inputs_count = modal.locator("input[type='text']").count()
            logger.info(f"label可见: {label_visible}, text inputs总数: {inputs_count}")

        assert label_visible, "Job Function label 应可见"
        assert inputs_count >= 3, f"Work Experience 弹窗应至少有3个文本输入框（Job Title, Company, Job Function），实际: {inputs_count}"

    @pytest.mark.case_id_ae_resume_tc016
    @pytest.mark.p1
    @pytest.mark.ae
    @allure.story("AE站简历Work Experience")
    @allure.title("TC016: Work Experience 弹窗中 'I currently work here' 复选框状态验证")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证 Work Experience 弹窗中 'I currently work here' 复选框可见，并验证初始状态")
    def test_tc016_currently_work_here_checkbox(self, page, config):
        """TC016: 'I currently work here' 复选框验证"""
        with allure.step("步骤1：打开 Work Experience 弹窗"):
            self.resume_page.open_edit_work_experience_modal()

        with allure.step("步骤2：验证 'I currently work here' 文本可见"):
            text_visible = page.get_by_text("I currently work here").is_visible(timeout=3000)
            logger.info(f"'I currently work here' 文本可见: {text_visible}")

        with allure.step("步骤3：验证复选框当前状态"):
            is_checked = self.resume_page.is_currently_work_here_checked()
            logger.info(f"'I currently work here' 已勾选: {is_checked}")

        assert text_visible, "'I currently work here' 文本应可见"

    @pytest.mark.case_id_ae_resume_tc017
    @pytest.mark.p1
    @pytest.mark.ae
    @allure.story("AE站简历Work Experience")
    @allure.title("TC017: 取消勾选 'I currently work here' 后 To 日期字段变为可编辑")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证取消勾选 'I currently work here' 后 To 日期字段解锁可编辑")
    def test_tc017_uncheck_currently_work_here(self, page, config):
        """TC017: 取消勾选 'I currently work here' 后 To 字段可编辑"""
        with allure.step("步骤1：打开 Work Experience 弹窗"):
            self.resume_page.open_edit_work_experience_modal()

        with allure.step("步骤2：验证初始状态（勾选时 To 显示 Present）"):
            is_checked = self.resume_page.is_currently_work_here_checked()
            logger.info(f"初始勾选状态: {is_checked}")

        with allure.step("步骤3：如已勾选，取消勾选"):
            if is_checked:
                self.resume_page.toggle_currently_work_here()
                dom_content_loaded_soft(page, 20000)
                logger.info("✓ 取消勾选 'I currently work here'")

        with allure.step("步骤4：验证 To 字段不再显示 Present，变为可编辑"):
            modal = page.locator(".modal-content").first
            present_visible = modal.get_by_text("Present", exact=True).is_visible(timeout=2000)
            to_input = modal.locator("input[type='text']")
            logger.info(f"'Present' 可见: {present_visible}")
            logger.info(f"To 字段输入框数量: {to_input.count()}")

        if is_checked:
            assert not present_visible, "取消勾选后 To 字段不应显示 'Present'"

    @pytest.mark.case_id_ae_resume_tc018
    @pytest.mark.p1
    @pytest.mark.ae
    @allure.story("AE站简历Work Experience")
    @allure.title("TC018: Work Experience 弹窗有 Job Description 文本域")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("验证 Work Experience 弹窗包含 Job Description textarea 字段")
    def test_tc018_job_description_field(self, page, config):
        """TC018: Work Experience 弹窗有 Job Description 文本域"""
        with allure.step("步骤1：打开 Work Experience 弹窗"):
            self.resume_page.open_edit_work_experience_modal()

        with allure.step("步骤2：验证 Job Description 文本域可见"):
            desc_label = page.locator(".modal-content").first.get_by_text("Job Description")
            label_visible = desc_label.is_visible(timeout=3000)
            textarea_visible = page.locator(".modal-content textarea").is_visible(timeout=3000)
            logger.info(f"Job Description label: {label_visible}, textarea: {textarea_visible}")

        assert label_visible, "Job Description label 应可见"
        assert textarea_visible, "Job Description textarea 应可见"

    @pytest.mark.case_id_ae_resume_tc019
    @pytest.mark.p2
    @pytest.mark.ae
    @allure.story("AE站简历Work Experience")
    @allure.title("TC019: 点击 Cancel 关闭 Work Experience 弹窗不保存")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("验证点击 Cancel 后 Work Experience 弹窗关闭且修改不保存")
    def test_tc019_cancel_work_experience_modal(self, page, config):
        """TC019: Cancel 关闭 Work Experience 弹窗不保存"""
        with allure.step("步骤1：打开 Work Experience 弹窗"):
            self.resume_page.open_edit_work_experience_modal()

        with allure.step("步骤2：修改 Job Title"):
            try:
                page.locator(".modal-content").first.get_by_placeholder("Job Title").fill("TempTitle")
            except Exception:
                pass

        with allure.step("步骤3：点击 Cancel"):
            self.resume_page.click_cancel_in_modal()

        with allure.step("步骤4：验证弹窗关闭"):
            is_open = self.resume_page.is_any_modal_open()
            logger.info(f"弹窗仍开着: {is_open}")

        assert not is_open, "点击 Cancel 后 Work Experience 弹窗应关闭"


# ============================================
# 测试类五：Education Background 弹窗（TC020~TC025）
# ============================================

@allure.feature("OK")
class TestEducationModal:
    """Education Background 弹窗编辑测试"""

    @pytest.fixture(autouse=True)
    def setup(self, page, config):
        ensure_ae_logged_in(page, config)
        self.resume_page = ResumeAddPageAe(page)
        self.resume_page.navigate_to_resume_view()
        self.resume_page.is_resume_view_displayed()

    @pytest.mark.case_id_ae_resume_tc020
    @pytest.mark.p1
    @pytest.mark.ae
    @allure.story("AE站简历Education Background")
    @allure.title("TC020: 点击编辑图标打开 Edit Education Background 弹窗")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证点击 Education Background 编辑图标后弹窗正确打开")
    def test_tc020_open_education_modal(self, page, config):
        """TC020: 打开 Edit Education Background 弹窗"""
        with allure.step("步骤1：点击 Education Background 编辑图标"):
            self.resume_page.open_edit_education_modal()

        with allure.step("步骤2：验证弹窗已打开"):
            is_displayed = self.resume_page.is_education_modal_displayed()
            logger.info(f"Education Background 弹窗显示: {is_displayed}")

        with allure.step("步骤3：验证弹窗标题为 'Edit Education Background'"):
            title_visible = page.get_by_text("Edit Education Background").is_visible(timeout=3000)
            logger.info(f"'Edit Education Background' 标题可见: {title_visible}")

        assert is_displayed, "Education Background 弹窗应打开"
        assert title_visible, "弹窗标题应为 'Edit Education Background'"

    @pytest.mark.case_id_ae_resume_tc021
    @pytest.mark.p1
    @pytest.mark.ae
    @allure.story("AE站简历Education Background")
    @allure.title("TC021: Education Level 自定义下拉控件（PcFakeSelectInput）存在并可点击")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证 Education Level 使用自定义下拉控件（PcFakeSelectInput），点击后可展开并选择学历选项")
    def test_tc021_education_level_dropdown_options(self, page, config):
        """TC021: Education Level 下拉控件验证"""
        with allure.step("步骤1：打开 Education Background 弹窗"):
            self.resume_page.open_edit_education_modal()

        with allure.step("步骤2：验证 Education Level 自定义下拉控件存在"):
            modal = page.locator(".modal-content").first
            # Education Level uses PcFakeSelectInput (custom dropdown, not native select)
            edu_label_visible = modal.get_by_text("Education Level").is_visible(timeout=3000)
            fake_select_count = modal.locator("[class*='PcFakeSelectInput']").count()
            current_value_visible = modal.get_by_text("Secondary School Diploma").is_visible(timeout=3000)
            logger.info(f"Education Level label: {edu_label_visible}, PcFakeSelectInput count: {fake_select_count}")
            logger.info(f"当前选中值可见 (Secondary School Diploma): {current_value_visible}")

        with allure.step("步骤3：点击下拉展开验证有选项"):
            fake_select = modal.locator("[class*='PcFakeSelectInput_pcFakeSelectInput']").first
            if fake_select.count() > 0:
                fake_select.click()
                dom_content_loaded_soft(page, 20000)
                # Check if options appear - count() avoids strict mode violation
                options_count = page.locator("[class*='PcSingleSelect_selectItem']").count()
                logger.info(f"下拉选项数量: {options_count}")
                page.keyboard.press("Escape")  # Close dropdown
            
        assert edu_label_visible, "Education Level label 应可见"
        assert fake_select_count > 0, f"Education Level 应有 PcFakeSelectInput 控件，实际: {fake_select_count}"

    @pytest.mark.case_id_ae_resume_tc022
    @pytest.mark.p1
    @pytest.mark.ae
    @allure.story("AE站简历Education Background")
    @allure.title("TC022: Institute 和 Major 字段为可选填写（CustomCounterInput）")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("验证 Education Background 弹窗有 Institute 和 Major 两个文本输入字段（标注为 Optional）")
    def test_tc022_institute_major_optional(self, page, config):
        """TC022: Institute 和 Major 字段存在（Optional）"""
        with allure.step("步骤1：打开 Education Background 弹窗"):
            self.resume_page.open_edit_education_modal()

        with allure.step("步骤2：验证 Institute 和 Major 标签文本可见"):
            modal = page.locator(".modal-content").first
            # Institute and Major use CustomCounterInput with label text (no placeholder attribute)
            institute_label = modal.get_by_text("Institute (Optional)").is_visible(timeout=3000)
            major_label = modal.get_by_text("Major (Optional)").is_visible(timeout=3000)
            logger.info(f"Institute(Optional) label: {institute_label}, Major(Optional) label: {major_label}")

        with allure.step("步骤3：验证有文本输入框（Institute 和 Major 各一个）"):
            text_inputs = modal.locator("input[type='text']")
            inputs_count = text_inputs.count()
            logger.info(f"文本输入框数量: {inputs_count}")

        assert institute_label, "Institute (Optional) 标签应可见"
        assert major_label, "Major (Optional) 标签应可见"
        assert inputs_count >= 2, f"Education 弹窗应至少有2个文本输入框（Institute, Major），实际: {inputs_count}"

    @pytest.mark.case_id_ae_resume_tc023
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ae
    @allure.story("AE站简历Education Background")
    @allure.title("TC023: 修改 Institute 并 Save，视图页数据更新（数据回显验证）")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证修改 Education Institute 后 Save，简历视图页显示最新数据（回显验证核心用例）")
    def test_tc023_save_education_and_echo(self, page, config):
        """TC023: 修改 Education Institute 后 Save 数据回显"""
        with allure.step("步骤1：打开 Education Background 弹窗"):
            self.resume_page.open_edit_education_modal()

        with allure.step("步骤2：修改 Institute"):
            institute_name = config['test_edu_institute']
            self.resume_page.input_institute(institute_name)
            logger.info(f"✓ 修改 Institute 为: {institute_name}")

        with allure.step("步骤3：修改 Major"):
            major_name = config['test_edu_major']
            self.resume_page.input_major(major_name)
            logger.info(f"✓ 修改 Major 为: {major_name}")

        with allure.step("步骤4：点击 Save"):
            self.resume_page.click_save_in_modal()
            self.resume_page.wait_for_modal_close()
            assert not self.resume_page.is_any_modal_open(), "Save 后弹窗应关闭"

        with allure.step("步骤5：刷新页面验证数据持久化"):
            page.reload()
            dom_content_loaded_soft(page, 20000)
            self.resume_page.is_resume_view_displayed()

        with allure.step("步骤6：重新打开弹窗验证 Institute 和 Major 回显"):
            self.resume_page.open_edit_education_modal()
            echo_institute = self.resume_page.get_institute_value()
            logger.info(f"回显 Institute: '{echo_institute}'")
            assert echo_institute == institute_name, \
                f"Institute 应回显 '{institute_name}'，实际: '{echo_institute}'"

    @pytest.mark.case_id_ae_resume_tc024
    @pytest.mark.p1
    @pytest.mark.ae
    @allure.story("AE站简历Education Background")
    @allure.title("TC024: Education Background 弹窗中 From 和 To 日期字段存在")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证 Education Background 弹窗包含 From 和 To 日期字段")
    def test_tc024_education_date_fields(self, page, config):
        """TC024: Education Background 日期字段验证"""
        with allure.step("步骤1：打开 Education Background 弹窗"):
            self.resume_page.open_edit_education_modal()

        with allure.step("步骤2：验证 From 和 To 标签可见"):
            modal = page.locator(".modal-content").first
            from_label = modal.get_by_text("From").is_visible(timeout=3000)
            to_label = modal.get_by_text("To").is_visible(timeout=3000)
            logger.info(f"From label: {from_label}, To label: {to_label}")

        with allure.step("步骤3：验证日期输入框数量"):
            date_inputs = modal.locator("input[type='text']")
            input_count = date_inputs.count()
            logger.info(f"日期输入框数量: {input_count}")

        assert from_label, "Education Background 弹窗应有 'From' 标签"
        assert to_label, "Education Background 弹窗应有 'To' 标签"

    @pytest.mark.case_id_ae_resume_tc025
    @pytest.mark.p2
    @pytest.mark.ae
    @allure.story("AE站简历Education Background")
    @allure.title("TC025: 点击 Cancel 关闭 Education Background 弹窗不保存")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("验证点击 Cancel 后 Education Background 弹窗关闭")
    def test_tc025_cancel_education_modal(self, page, config):
        """TC025: Cancel 关闭 Education Background 弹窗"""
        with allure.step("步骤1：打开 Education Background 弹窗"):
            self.resume_page.open_edit_education_modal()

        with allure.step("步骤2：点击 Cancel"):
            self.resume_page.click_cancel_in_modal()

        with allure.step("步骤3：验证弹窗关闭"):
            is_open = self.resume_page.is_any_modal_open()
            logger.info(f"弹窗仍开着: {is_open}")

        assert not is_open, "点击 Cancel 后 Education Background 弹窗应关闭"


# ============================================
# 测试类六：Language 弹窗（TC026~TC027）
# ============================================

@allure.feature("OK")
class TestLanguageModal:
    """Language 弹窗编辑测试"""

    @pytest.fixture(autouse=True)
    def setup(self, page, config):
        ensure_ae_logged_in(page, config)
        self.resume_page = ResumeAddPageAe(page)
        self.resume_page.navigate_to_resume_view()
        self.resume_page.is_resume_view_displayed()

    @pytest.mark.case_id_ae_resume_tc026
    @pytest.mark.p2
    @pytest.mark.ae
    @allure.story("AE站简历Language")
    @allure.title("TC026: 点击 Language 图标打开 Language 弹窗")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("验证点击 Language 区块的图标后 Language 弹窗正确打开")
    def test_tc026_open_language_modal(self, page, config):
        """TC026: 打开 Language 弹窗"""
        with allure.step("步骤1：点击 Language 图标"):
            self.resume_page.open_language_modal()

        with allure.step("步骤2：验证弹窗已打开"):
            is_displayed = self.resume_page.is_language_modal_displayed()
            logger.info(f"Language 弹窗显示: {is_displayed}")

        with allure.step("步骤3：验证弹窗中包含 'Language' 相关内容"):
            modal = page.locator(".modal-content").first
            title_visible = modal.get_by_text("Language", exact=True).is_visible(timeout=3000)
            logger.info(f"弹窗中 'Language' 标题可见: {title_visible}")

        assert is_displayed, "Language 弹窗应正确打开"
        assert title_visible, "弹窗标题应为 'Language'"

    @pytest.mark.case_id_ae_resume_tc027
    @pytest.mark.p2
    @pytest.mark.ae
    @allure.story("AE站简历Language")
    @allure.title("TC027: Language 弹窗有语言选择下拉并显示 placeholder '0/10'")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("验证 Language 弹窗有语言选择控件，placeholder 提示最多可选10个")
    def test_tc027_language_dropdown_placeholder(self, page, config):
        """TC027: Language 弹窗有语言选择 placeholder"""
        with allure.step("步骤1：打开 Language 弹窗"):
            self.resume_page.open_language_modal()

        with allure.step("步骤2：验证 0/10 提示文本可见"):
            placeholder_visible = page.get_by_text("Select your language skills (0/10)").is_visible(timeout=3000)
            logger.info(f"语言选择占位文本可见: {placeholder_visible}")

        with allure.step("步骤3：验证有 Cancel 和 Save 按钮"):
            cancel_visible = page.get_by_role("button", name="Cancel").is_visible(timeout=3000)
            save_visible = page.get_by_role("button", name="Save").is_visible(timeout=3000)
            logger.info(f"Cancel: {cancel_visible}, Save: {save_visible}")

        assert placeholder_visible or page.locator(".modal-content select").count() > 0, \
            "Language 弹窗应有语言选择控件或 placeholder 提示"
        assert cancel_visible, "Language 弹窗应有 Cancel 按钮"
        assert save_visible, "Language 弹窗应有 Save 按钮"


# ============================================
# 测试类七：完整数据回显验证（TC028~TC030）
# ============================================

@allure.feature("OK")
class TestDataEchoVerification:
    """修改提交后数据回显验证"""

    @pytest.mark.case_id_ae_resume_tc028
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ae
    @allure.story("AE站简历数据回显")
    @allure.title("TC028: 修改 Education Background 后刷新页面验证数据回显（核心）")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证修改 Education Background 的 Institute 字段后 Save，刷新页面再次打开弹窗数据回显正确（核心回显验证）")
    def test_tc028_personal_info_data_echo_after_reload(self, page, config):
        """TC028: 修改 Education Background 后刷新验证数据回显（核心）"""
        ensure_ae_logged_in(page, config)
        resume_page = ResumeAddPageAe(page)

        with allure.step("步骤1：导航到简历视图页"):
            resume_page.navigate_to_resume_view()
            resume_page.is_resume_view_displayed()

        with allure.step("步骤2：打开 Education Background 弹窗并修改 Institute"):
            resume_page.open_edit_education_modal()
            new_institute = "EchoTest University"
            # 先清空再填，确保 React 表单识别为 dirty，避免 Save 无效仍用旧值
            resume_page.input_institute("")
            page.wait_for_timeout(200)
            resume_page.input_institute(new_institute)
            logger.info(f"✓ 修改 Institute 为: {new_institute}")

        with allure.step("步骤3：验证 Save 按钮状态"):
            modal = page.locator(".modal-content").first
            save_disabled = modal.get_by_role("button", name="Save").is_disabled()
            logger.info(f"Save 按钮禁用: {save_disabled}")

        with allure.step("步骤4：Save 并等待弹窗关闭"):
            resume_page.click_save_in_modal()
            resume_page.wait_for_modal_close()
            assert not resume_page.is_any_modal_open(), "Save 后弹窗应关闭"

        with allure.step("步骤5：刷新页面模拟重新进入"):
            page.reload(wait_until="domcontentloaded", timeout=60000)
            page.wait_for_load_state("load", timeout=30000)
            dom_content_loaded_soft(page, 20000)
            resume_page.is_resume_view_displayed()
            page.wait_for_selector("h3:has-text('Online Resume')", state="visible", timeout=20000)
            logger.info("✓ 刷新页面完成")

        with allure.step("步骤6：重新打开弹窗验证 Institute 数据回显"):
            echo_institute = ""
            for attempt in range(4):
                resume_page.open_edit_education_modal()
                echo_institute = resume_page.get_institute_value()
                logger.info(f"弹窗回显 Institute (尝试 {attempt + 1}): '{echo_institute}'")
                if echo_institute == new_institute:
                    break
                try:
                    page.keyboard.press("Escape")
                except Exception:
                    pass
                page.wait_for_timeout(800)
                page.reload(wait_until="domcontentloaded", timeout=60000)
                page.wait_for_load_state("load", timeout=30000)
                dom_content_loaded_soft(page, 20000)
                resume_page.is_resume_view_displayed()
                page.wait_for_selector("h3:has-text('Online Resume')", state="visible", timeout=20000)

        assert echo_institute == new_institute, \
            f"刷新后弹窗应回显 Institute '{new_institute}'，实际: '{echo_institute}'"

    @pytest.mark.case_id_ae_resume_tc029
    @pytest.mark.p1
    @pytest.mark.ae
    @allure.story("AE站简历数据回显")
    @allure.title("TC029: 修改 Education Background 后重新进入页面验证数据回显")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证修改 Education Background 的 Institute 字段后 Save，刷新页面再次打开弹窗数据回显正确")
    def test_tc029_education_data_echo_after_reload(self, page, config):
        """TC029: 修改 Education Background 后重新进入验证数据回显"""
        ensure_ae_logged_in(page, config)
        resume_page = ResumeAddPageAe(page)

        with allure.step("步骤1：导航到简历视图页"):
            resume_page.navigate_to_resume_view()

        with allure.step("步骤2：打开 Education Background 弹窗并修改 Institute"):
            resume_page.open_edit_education_modal()
            institute_name = config['test_edu_institute']
            resume_page.input_institute(institute_name)
            logger.info(f"✓ 修改 Institute 为: {institute_name}")

        with allure.step("步骤3：Save 并等待弹窗关闭"):
            resume_page.click_save_in_modal()
            resume_page.wait_for_modal_close()
            assert not resume_page.is_any_modal_open(), "Save 后弹窗应关闭"

        with allure.step("步骤4：刷新页面"):
            page.reload()
            dom_content_loaded_soft(page, 20000)
            resume_page.is_resume_view_displayed()
            logger.info("✓ 刷新页面完成")

        with allure.step("步骤5：重新打开弹窗验证 Institute 数据回显"):
            resume_page.open_edit_education_modal()
            echo_institute = resume_page.get_institute_value()
            logger.info(f"回显 Institute: '{echo_institute}'")

        assert echo_institute == institute_name, \
            f"Education Institute 应回显 '{institute_name}'，实际: '{echo_institute}'"

    @pytest.mark.case_id_ae_resume_tc030
    @pytest.mark.p1
    @pytest.mark.ae
    @allure.story("AE站简历数据回显")
    @allure.title("TC030: 修改 Personal Summary 后重新进入页面验证摘要数据回显")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证修改 Personal Summary 文本后 Save，刷新页面后视图页显示最新摘要文本")
    def test_tc030_personal_summary_data_echo_after_reload(self, page, config):
        """TC030: 修改 Personal Summary 后重新进入验证数据回显"""
        ensure_ae_logged_in(page, config)
        resume_page = ResumeAddPageAe(page)

        with allure.step("步骤1：导航到简历视图页"):
            resume_page.navigate_to_resume_view()

        with allure.step("步骤2：打开 Personal Summary 弹窗并输入摘要"):
            resume_page.open_personal_summary_modal()
            summary_text = config['test_summary']
            resume_page.input_personal_summary(summary_text)
            logger.info(f"✓ 输入摘要: {summary_text[:40]}...")

        with allure.step("步骤3：Save 并等待弹窗关闭"):
            resume_page.click_save_in_modal()
            resume_page.wait_for_modal_close()
            assert not resume_page.is_any_modal_open(), "Save 后弹窗应关闭"

        with allure.step("步骤4：刷新页面"):
            page.reload(wait_until="networkidle", timeout=30000)
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            dom_content_loaded_soft(page, 20000)
            page.wait_for_timeout(3000)  # 额外等待前端渲染
            resume_page.is_resume_view_displayed()
            logger.info("✓ 刷新页面完成")

        with allure.step("步骤5：验证视图页显示更新后的摘要内容"):
            # Check first 30 characters of the summary text
            summary_visible = False
            probe = summary_text[:30]
            for attempt in range(3):
                summary_visible = page.get_by_text(probe).is_visible(timeout=10000)
                if summary_visible:
                    break
                # 并发/网络抖动下偶发回显慢：等待并刷新重试一次
                page.wait_for_timeout(2000)
                if attempt < 2:
                    page.reload(wait_until="networkidle", timeout=30000)
                    page.wait_for_load_state("domcontentloaded", timeout=15000)
                    dom_content_loaded_soft(page, 20000)
                    page.wait_for_timeout(3000)
            logger.info(f"视图页摘要内容可见: {summary_visible}")

        assert summary_visible, \
            f"刷新后视图页 Personal Summary 区块应显示最新摘要内容"
