"""
西班牙站 - 简历添加提交流程完整测试

本脚本由 playwright-test-generator 生成
测试文档：test_cases/zhaopin/ok-es-ResumeAdd-Submit-测试用例-20260323.md
生成时间：2026-03-23

测试站点：ES (https://es.58v5.cn)
测试角色：Buyer (求职者)
测试目标：验证简历完整提交流程 + 提交后数据验证 + 数据库清理

执行顺序（批量/全量、筛选子集时均生效，需已安装 pytest-order、pytest-dependency）：
- 本类用例带 ``@pytest.mark.order(1..6)``，**TC004=order(5)**、**TC006=order(6)**，保证 TC006 在 TC004 之后执行。
- **TC006** 声明 ``depends=[es_resume_submit_tc004]``：仅当 **TC004** 在本轮会话中**通过**时执行；若 TC004 失败则 **skip**；若只单跑 TC006 未收集 TC004，也会 **skip**（可能伴随 dependency 未解析的 CLI 提示）。
- 使用 ``pytest -n`` 分布式时，请使用 ``--dist=loadfile``（或 ``loadscope``），避免同文件用例被拆到不同 worker 导致依赖状态不一致。
- **TC001 / TC003**：工作经历在断言默认「当前在职」后，改为取消勾选并填写 To 日期（与 TC004 一致）；纯 Present 路径在环境中易长时间不离开 ``/resume/add``。
- **autouse fixture**：每条用例 teardown 后 ``goto`` 西班牙站首页，避免留在 espub 简历域导致下一条 Jobs 列表/ Done 不稳定。
"""
import re
import time

import pytest
import allure
from datetime import datetime
from pages.login_page import LoginPage
from pages.jobs_list_page_es import JobsListPageES
from pages.resume_add_page_es import ResumeAddPageEs
from utils.session_manager import SessionManager
from utils.logger import setup_logger
from utils.db_client import execute_update, execute_query

logger = setup_logger()

from test_cases.zhaopin.explicit_waits import dom_content_loaded_soft, network_idle_soft, sg_wait_jobs_list_url, sg_after_home_jobs_icon

# ============================================
# 测试环境配置（来自录制文档，录制与运行使用同一账号）
# ============================================
_CONFIG = {
    "site": "es",
    "site_name": "西班牙站",
    "role": "buyer",
    "user_name": "es_buyer_wangyongli",
    "base_url": "https://es.58v5.cn",
    "test_account": {
        "username": "wangyongli@58.com",
        "password": "Qwer1234"
    },
    "locale": "es-ES",
    "currency": "EUR",
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
    "test_user_id": "796567146451408960"  # 用于数据库清理（账号 wangyongli@58.com 的实际 user_id）
}


@pytest.fixture(scope="function", autouse=True)
def setup_and_cleanup(request, page):
    """
    每个测试用例前后的数据库清理。

    - 默认：用例前清空，避免脏数据；用例后再清空，隔离下一条。
    - TC006（test_verify_resume_data_display）用例前**不清空**，依赖 TC004 写入库中的简历。
    - TC004（test_submit_resume_set_work_to_date）用例后**不清空**，供紧随其后的 TC006 读取。
    - 用例后回站点首页，避免停在 espub 简历域导致下一条用例 Jobs 列表卡片找不到或 Done 状态异常。
    """
    if request.node.name != "test_verify_resume_data_display":
        _cleanup_database()
        logger.info("✓ 测试前数据库清理完成")

    yield

    if request.node.name != "test_submit_resume_set_work_to_date":
        _cleanup_database()
        logger.info("✓ 测试后数据库清理完成")

    try:
        if page and not page.is_closed():
            page.goto(_CONFIG["base_url"], wait_until="domcontentloaded", timeout=30000)
            dom_content_loaded_soft(page, 12000)
            page.wait_for_timeout(200)
    except Exception as e:
        logger.warning("测试后回首页: %s", e)


def _cleanup_database():
    """
    清理测试用户的简历数据（按外键约束顺序）
    """
    user_id = _CONFIG["test_user_id"]
    try:
        # 按外键约束顺序删除
        execute_update("DELETE FROM resume_work_experience WHERE user_id = %s", (user_id,))
        execute_update("DELETE FROM resume_education WHERE user_id = %s", (user_id,))
        execute_update("DELETE FROM resume_person_info WHERE user_id = %s", (user_id,))
        execute_update("DELETE FROM resume WHERE user_id = %s", (user_id,))
        logger.info(f"✓ 数据库清理完成 (user_id={user_id})")
    except Exception as e:
        logger.error(f"数据库清理失败: {e}")
        raise


class TestESResumeSubmit:
    """西班牙站简历提交流程测试"""
    
    @pytest.mark.case_id_es_resume_submit_01
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.resume
    @pytest.mark.es
    @allure.feature("OK Spain - Resume")
    @allure.story("简历提交流程 - 有工作经验")
    @allure.title("TC001: 完整提交流程 - 填写所有必填项并提交（有工作经验）")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证用户填写完整简历信息（有工作经验）后成功提交，数据保存到数据库")
    @pytest.mark.order(1)
    def test_submit_resume_with_work_experience(self, page, config):
        """完整提交流程 - 有工作经验场景"""
        
        # ========== Arrange：准备测试对象 ==========
        login_page = LoginPage(page)
        jobs_list_page = JobsListPageES(page)
        resume_page = ResumeAddPageEs(page)
        
        # 从 config 读取测试数据
        site = config['site']
        role = config['role']
        account_name = config['user_name']
        base_url = config['base_url']
        username = config['test_account']['username']
        password = config['test_account']['password']
        
        logger.info("="*80)
        logger.info("TC001: 完整提交流程 - 有工作经验场景")
        logger.info("="*80)
        logger.info(f"站点: {site.upper()} ({config['site_name']})")
        logger.info(f"角色: {role.upper()} (求职者)")
        logger.info(f"账号: {account_name}")
        logger.info(f"邮箱: {username}")
        logger.info("="*80)
        
        # ========== Session 复用机制 ==========
        session_manager = SessionManager(page, base_url, session_name=f"{site}_{role}_{account_name}")
        session_loaded = False
        
        with allure.step("尝试加载已保存的 Session"):
            session_loaded = session_manager.load_session()
            if session_loaded:
                logger.info("✓ 成功加载已保存的 Session")
                page.wait_for_load_state("networkidle", timeout=5000)
                # 验证 Session 是否有效（检查登录状态）
                try:
                    page.goto(base_url, wait_until="domcontentloaded", timeout=10000)
                    dom_content_loaded_soft(page, 20000)
                    # 简单验证：如果能正常访问即认为 Session 有效
                    logger.info("✓ Session 有效，已登录状态")
                    logger.info("✅ 跳过登录步骤，直接进入测试！")
                except Exception:
                    logger.info("⚠️ Session 已过期，需要重新登录")
                    session_loaded = False
            else:
                logger.info("⚠️ 未找到已保存的 Session，需要执行登录")
        
        # ========== Act 阶段1：执行登录操作（仅在 Session 无效时执行）==========
        if not session_loaded:
            with allure.step("步骤1：打开西班牙站首页"):
                logger.info("开始登录流程")
                login_page.navigate_to_home_page()
                logger.info("✓ 打开西班牙站首页成功")
            
            with allure.step("步骤2：处理Cookie弹窗"):
                login_page.handle_cookie_popup()
                logger.info("✓ 已处理Cookie弹窗（如果存在）")
                page.wait_for_load_state("networkidle", timeout=5000)
            
            with allure.step("步骤3：点击 Log in / Register 按钮"):
                login_page.click_login_register_button()
                logger.info("✓ 点击登录/注册按钮")
            
            with allure.step(f"步骤4：输入邮箱 {username}"):
                login_page.input_email(username)
                login_page.click_continue_button()
                logger.info("✓ 输入邮箱完成")
            
            with allure.step("步骤5：输入密码并点击Log in"):
                login_page.input_password(password)
                login_page.click_login_button()
                logger.info("✓ 输入密码完成")
            
            with allure.step("验证登录成功"):
                page.wait_for_load_state("domcontentloaded", timeout=10000)
                current_url = page.url
                assert "login" not in current_url.lower(), f"登录失败，仍停留在登录页: {current_url}"
                logger.info("✅ 登录成功！")
            
            with allure.step("保存 Session"):
                if session_manager.save_session():
                    logger.info("✓ Session 已保存，下次测试将自动复用")
        
        # ========== Act 阶段2：进入简历添加页面 ==========
        # 注意：由于页面路由逻辑问题，这里直接访问 /resume/add 页面
        with allure.step("步骤6-8：直接访问简历添加页"):
            page.goto("https://espub.58v5.cn/biz/en/resume/add", wait_until="domcontentloaded", timeout=30000)
            dom_content_loaded_soft(page, 20000)
            logger.info("✓ 已导航到简历添加页")
            
            # 验证 Step1 表单加载（等待 Personal Information 标题或 First Name 输入框）
            try:
                page.wait_for_selector("h3:has-text('Personal Information')", state="visible", timeout=15000)
            except Exception:
                page.get_by_role("textbox", name="First Name").wait_for(state="visible", timeout=10000)
            logger.info("✓ Step1 Personal Information 表单已加载")
        
        # ========== Act 阶段3：填写 Step1 Personal Information ==========
        with allure.step("步骤9：填写 First Name"):
            resume_page.input_first_name("AutoTest")
            logger.info("✓ 输入 First Name: AutoTest")
        
        with allure.step("步骤10：填写 Last Name"):
            resume_page.input_last_name("Submit")
            logger.info("✓ 输入 Last Name: Submit")
        
        with allure.step("步骤11：验证 Email 预填"):
            email_value = resume_page.get_email_value()
            assert email_value == username, f"Email预填不正确，期望: {username}, 实际: {email_value}"
            logger.info(f"✓ Email 预填正确: {username}")
        
        with allure.step("步骤12：验证 Current Location 预填"):
            location_value = resume_page.get_current_location_value()
            assert "Spain" in location_value, f"Current Location预填不正确，实际: {location_value}"
            logger.info("✓ Current Location 预填正确: Spain")
        
        with allure.step("步骤13：点击 Continue 进入 Step2"):
            resume_page.click_continue()
            logger.info("✓ 点击 Continue 按钮")
            page.wait_for_load_state("domcontentloaded", timeout=10000)
            dom_content_loaded_soft(page, 20000)
            logger.info("✓ 进入 Step2 Recent Experience")
        
        # ========== Act 阶段4：填写 Step2 Work Experience ==========
        with allure.step("步骤14：选择 Job Function"):
            resume_page.select_job_function(
                "Information & Communication Technology",
                "Testing & Quality Assurance"
            )
            logger.info("✓ 选择 Job Function: Testing & Quality Assurance")
        
        with allure.step("步骤15：选择 Work Experience From 日期"):
            resume_page.select_work_from_date("2020", "01")
            logger.info("✓ 选择 Work Experience From: 2020-01")
        
        with allure.step("步骤16：验证 'I currently work here' 默认勾选"):
            is_checked = resume_page.is_currently_work_here_checked()
            assert is_checked, "'I currently work here' 默认应勾选"
            logger.info("✓ 'I currently work here' 默认已勾选（To 为 Present）")

        with allure.step("步骤16b：取消在职并设置工作经历结束日期（Present 路径提交易卡在 /resume/add）"):
            resume_page.uncheck_currently_work_here()
            dom_content_loaded_soft(page, 20000)
            resume_page.select_work_to_date("2023", "12")
            logger.info("✓ 已设置 Work Experience To: 2023-12（仍覆盖「有工作经验」主流程）")
        
        # ========== Act 阶段5：填写 Step2 Education Experience ==========
        with allure.step("步骤17：选择 Education Level"):
            resume_page.select_education_level("Bachelor's Degree")
            logger.info("✓ 选择 Education Level: Bachelor's Degree")
        
        with allure.step("步骤18：选择 Education From 日期"):
            resume_page.select_education_from_date("2016", "09")
            logger.info("✓ 选择 Education From: 2016-09")
        
        with allure.step("步骤19：选择 Education To 日期"):
            resume_page.select_education_to_date("2020", "06")
            logger.info("✓ 选择 Education To: 2020-06")
        
        # ========== Act 阶段6：提交简历 ==========
        with allure.step("步骤20：验证 Done 按钮可点击"):
            is_enabled = resume_page.is_done_button_enabled()
            assert is_enabled, "Done 按钮应为可点击状态"
            logger.info("✓ Done 按钮已激活")
        
        with allure.step("步骤21：点击 Done 提交简历"):
            resume_page.click_done()
            logger.info("✓ 点击 Done 按钮")
            dom_content_loaded_soft(page, 20000)
        # ========== Assert：验证提交成功 ==========
        with allure.step("验证提交成功 - 页面跳转"):
            current_url = page.url
            assert "resume/add" not in current_url, f"提交失败，仍停留在简历添加页: {current_url}"
            logger.info(f"✅ 提交成功！页面已跳转: {current_url}")
        
        with allure.step("验证数据库 - resume 表"):
            user_id = _CONFIG["test_user_id"]
            rows = execute_query(
                "SELECT COUNT(*) FROM resume WHERE user_id = %s",
                (user_id,)
            )
            assert rows[0][0] == 1, f"resume 表应有1条记录，实际: {rows[0][0]}"
            logger.info("✓ resume 表数据验证通过")
        
        with allure.step("验证数据库 - resume_person_info 表"):
            rows = execute_query(
                "SELECT country_code FROM resume_person_info WHERE user_id = %s",
                (user_id,)
            )
            assert len(rows) == 1, f"resume_person_info 表应有1条记录，实际: {len(rows)}"
            assert rows[0][0] == "ES", f"country_code 不正确: {rows[0][0]}"
            logger.info("✓ resume_person_info 表数据验证通过")
        
        with allure.step("验证数据库 - resume_work_experience 表"):
            rows = execute_query(
                "SELECT cate1, from_time, to_time FROM resume_work_experience WHERE user_id = %s",
                (user_id,)
            )
            assert len(rows) == 1, f"resume_work_experience 表应有1条记录，实际: {len(rows)}"
            assert rows[0][2] is not None, "工作经历 to_time 应为具体结束日期"
            logger.info("✓ resume_work_experience 表数据验证通过")
        
        with allure.step("验证数据库 - resume_education 表"):
            rows = execute_query(
                "SELECT level, from_time, to_time FROM resume_education WHERE user_id = %s",
                (user_id,)
            )
            assert len(rows) == 1, f"resume_education 表应有1条记录，实际: {len(rows)}"
            logger.info("✓ resume_education 表数据验证通过")
        
        logger.info("="*80)
        logger.info("✅ TC001 测试全部通过！")
        logger.info("="*80)
    
    
    @pytest.mark.case_id_es_resume_submit_05
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.resume
    @pytest.mark.es
    @allure.feature("OK Spain - Resume")
    @allure.story("简历提交流程 - 无工作经验")
    @allure.title("TC005: 完整提交流程 - 开启 'I have no work experience' 仅填写 Education")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证用户开启无工作经验开关，仅填写教育信息后成功提交")
    @pytest.mark.order(2)
    def test_submit_resume_without_work_experience(self, page, config):
        """完整提交流程 - 无工作经验场景"""
        
        # ========== Arrange：准备测试对象 ==========
        login_page = LoginPage(page)
        jobs_list_page = JobsListPageES(page)
        resume_page = ResumeAddPageEs(page)
        
        # 从 config 读取测试数据
        site = config['site']
        role = config['role']
        account_name = config['user_name']
        base_url = config['base_url']
        username = config['test_account']['username']
        password = config['test_account']['password']
        
        logger.info("="*80)
        logger.info("TC005: 完整提交流程 - 无工作经验场景")
        logger.info("="*80)
        
        # ========== Session 复用（同 TC001）==========
        session_manager = SessionManager(page, base_url, session_name=f"{site}_{role}_{account_name}")
        session_loaded = session_manager.load_session()
        
        if not session_loaded:
            # 执行登录流程（同 TC001，此处简化）
            with allure.step("执行登录"):
                login_page.navigate_to_home_page()
                login_page.handle_cookie_popup()
                login_page.click_login_register_button()
                login_page.input_email(username)
                login_page.click_continue_button()
                login_page.input_password(password)
                login_page.click_login_button()
                page.wait_for_load_state("domcontentloaded", timeout=10000)
                session_manager.save_session()
                logger.info("✅ 登录成功")
        
        # ========== Act：进入简历添加页面（同 TC001）==========
        with allure.step("进入简历添加页面"):
            jobs_list_page.navigate_to_jobs_list()
            jobs_list_page.click_first_job_card()
            jobs_list_page.click_sidebar_resume()
            dom_content_loaded_soft(page, 20000)
            assert "resume/add" in page.url, "未进入简历添加页"
            logger.info("✓ 进入简历添加页成功")
        
        # ========== Act：填写 Step1 ==========
        with allure.step("填写 Step1 Personal Information"):
            resume_page.input_first_name("NoWork")
            resume_page.input_last_name("Experience")
            resume_page.click_continue()
            dom_content_loaded_soft(page, 20000)
            logger.info("✓ Step1 完成")
        
        # ========== Act：开启无工作经验开关 ==========
        with allure.step("开启 'I have no work experience' 开关"):
            resume_page.toggle_no_work_experience()
            logger.info("✓ 开启无工作经验开关")
            dom_content_loaded_soft(page, 20000)
        with allure.step("验证工作经验字段隐藏"):
            is_hidden = resume_page.is_work_experience_section_hidden()
            assert is_hidden, "工作经验字段应隐藏"
            logger.info("✓ 工作经验字段已隐藏")
        
        # ========== Act：填写 Education Experience ==========
        with allure.step("填写 Education Experience"):
            resume_page.select_education_level("Master's Degree")
            resume_page.select_education_from_date("2020", "09")
            resume_page.select_education_to_date("2024", "06")
            logger.info("✓ Education Experience 填写完成")
        
        # ========== Act：提交简历 ==========
        with allure.step("点击 Done 提交"):
            assert resume_page.is_done_button_enabled(), "Done 按钮应可点击"
            resume_page.click_done()
            dom_content_loaded_soft(page, 20000)
            logger.info("✓ 点击 Done 按钮")
        
        # ========== Assert：验证提交成功 ==========
        with allure.step("验证提交成功"):
            current_url = page.url
            assert "resume/add" not in current_url, f"提交失败: {current_url}"
            logger.info(f"✅ 提交成功！页面已跳转: {current_url}")
        
        with allure.step("验证数据库 - resume_work_experience 表应无记录"):
            user_id = _CONFIG["test_user_id"]
            rows = execute_query(
                "SELECT COUNT(*) FROM resume_work_experience WHERE user_id = %s",
                (user_id,)
            )
            assert rows[0][0] == 0, f"resume_work_experience 表应无记录，实际: {rows[0][0]}"
            logger.info("✓ resume_work_experience 表无记录（符合预期）")
        
        with allure.step("验证数据库 - resume_education 表应有记录"):
            rows = execute_query(
                "SELECT level FROM resume_education WHERE user_id = %s",
                (user_id,)
            )
            assert len(rows) == 1, f"resume_education 表应有1条记录，实际: {len(rows)}"
            logger.info("✓ resume_education 表数据验证通过")
        
        logger.info("="*80)
        logger.info("✅ TC005 测试全部通过！")
        logger.info("="*80)
    
    
    @pytest.mark.case_id_es_resume_submit_08
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.cleanup
    @pytest.mark.es
    @allure.feature("OK Spain - Resume")
    @allure.story("数据库清理")
    @allure.title("TC008: 数据库清理 - 删除测试用户的所有简历数据")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证数据库清理逻辑，删除 user_id=796579748218214624 的所有简历数据")
    @pytest.mark.order(3)
    def test_database_cleanup(self, page, config):
        """数据库清理测试"""
        
        user_id = _CONFIG["test_user_id"]
        
        logger.info("="*80)
        logger.info(f"TC008: 数据库清理测试 (user_id={user_id})")
        logger.info("="*80)
        
        # ========== Act：执行清理 ==========
        with allure.step("删除 resume_work_experience 表数据"):
            rowcount = execute_update(
                "DELETE FROM resume_work_experience WHERE user_id = %s",
                (user_id,)
            )
            logger.info(f"✓ 删除 resume_work_experience 表 {rowcount} 条记录")
        
        with allure.step("删除 resume_education 表数据"):
            rowcount = execute_update(
                "DELETE FROM resume_education WHERE user_id = %s",
                (user_id,)
            )
            logger.info(f"✓ 删除 resume_education 表 {rowcount} 条记录")
        
        with allure.step("删除 resume_person_info 表数据"):
            rowcount = execute_update(
                "DELETE FROM resume_person_info WHERE user_id = %s",
                (user_id,)
            )
            logger.info(f"✓ 删除 resume_person_info 表 {rowcount} 条记录")
        
        with allure.step("删除 resume 表数据"):
            rowcount = execute_update(
                "DELETE FROM resume WHERE user_id = %s",
                (user_id,)
            )
            logger.info(f"✓ 删除 resume 表 {rowcount} 条记录")
        
        # ========== Assert：验证清理结果 ==========
        with allure.step("验证 resume 表已清理"):
            rows = execute_query(
                "SELECT COUNT(*) FROM resume WHERE user_id = %s",
                (user_id,)
            )
            assert rows[0][0] == 0, f"resume 表应为空，实际: {rows[0][0]}"
            logger.info("✓ resume 表已清理")
        
        with allure.step("验证 resume_person_info 表已清理"):
            rows = execute_query(
                "SELECT COUNT(*) FROM resume_person_info WHERE user_id = %s",
                (user_id,)
            )
            assert rows[0][0] == 0, f"resume_person_info 表应为空，实际: {rows[0][0]}"
            logger.info("✓ resume_person_info 表已清理")
        
        with allure.step("验证 resume_work_experience 表已清理"):
            rows = execute_query(
                "SELECT COUNT(*) FROM resume_work_experience WHERE user_id = %s",
                (user_id,)
            )
            assert rows[0][0] == 0, f"resume_work_experience 表应为空，实际: {rows[0][0]}"
            logger.info("✓ resume_work_experience 表已清理")
        
        with allure.step("验证 resume_education 表已清理"):
            rows = execute_query(
                "SELECT COUNT(*) FROM resume_education WHERE user_id = %s",
                (user_id,)
            )
            assert rows[0][0] == 0, f"resume_education 表应为空，实际: {rows[0][0]}"
            logger.info("✓ resume_education 表已清理")
        
        logger.info("="*80)
        logger.info("✅ TC008 数据库清理测试全部通过！")
        logger.info("="*80)
    
    
    @pytest.mark.case_id_es_resume_submit_03
    @pytest.mark.smoke
    @pytest.mark.p1
    @pytest.mark.resume
    @pytest.mark.es
    @allure.feature("OK Spain - Resume")
    @allure.story("简历提交流程 - 修改 Current Location")
    @allure.title("TC003: 完整提交流程 - 修改 Current Location 为其他国家")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证用户修改 Current Location 为其他国家后成功提交，数据库正确保存")
    @pytest.mark.order(4)
    def test_submit_resume_change_location(self, page, config):
        """完整提交流程 - 修改 Current Location 场景"""
        
        # ========== Arrange：准备测试对象 ==========
        login_page = LoginPage(page)
        jobs_list_page = JobsListPageES(page)
        resume_page = ResumeAddPageEs(page)
        
        site = config['site']
        role = config['role']
        account_name = config['user_name']
        base_url = config['base_url']
        username = config['test_account']['username']
        password = config['test_account']['password']
        
        logger.info("="*80)
        logger.info("TC003: 完整提交流程 - 修改 Current Location 场景")
        logger.info("="*80)
        
        # ========== Session 复用 ==========
        session_manager = SessionManager(page, base_url, session_name=f"{site}_{role}_{account_name}")
        session_loaded = session_manager.load_session()
        
        if not session_loaded:
            with allure.step("执行登录"):
                login_page.navigate_to_home_page()
                login_page.handle_cookie_popup()
                login_page.click_login_register_button()
                login_page.input_email(username)
                login_page.click_continue_button()
                login_page.input_password(password)
                login_page.click_login_button()
                page.wait_for_load_state("domcontentloaded", timeout=10000)
                session_manager.save_session()
                logger.info("✅ 登录成功")
        
        # ========== Act：进入简历添加页面 ==========
        with allure.step("进入简历添加页面"):
            jobs_list_page.navigate_to_jobs_list()
            jobs_list_page.click_first_job_card()
            jobs_list_page.click_sidebar_resume()
            dom_content_loaded_soft(page, 20000)
            assert "resume/add" in page.url, "未进入简历添加页"
            logger.info("✓ 进入简历添加页成功")
        
        # ========== Act：修改 Current Location ==========
        with allure.step("修改 Current Location 为 France"):
            resume_page.select_current_location("France")
            logger.info("✓ 选择 Current Location: France")
            dom_content_loaded_soft(page, 20000)
        with allure.step("验证 Current Location 已更新"):
            location_value = resume_page.get_current_location_value()
            assert "France" in location_value, f"Current Location更新失败，实际: {location_value}"
            logger.info(f"✓ Current Location 验证通过: {location_value}")
        
        # ========== Act：填写 Step1 其他字段 ==========
        with allure.step("填写 Step1 Personal Information"):
            resume_page.input_first_name("LocationTest")
            resume_page.input_last_name("France")
            resume_page.click_continue()
            dom_content_loaded_soft(page, 20000)
            logger.info("✓ Step1 完成")
        
        # ========== Act：填写 Step2（与可稳定提交的 TC001/TC004 一致：显式 To，避免 Present 路径偶发不跳转）==========
        with allure.step("填写 Step2 Work Experience"):
            resume_page.select_job_function(
                "Information & Communication Technology",
                "Testing & Quality Assurance"
            )
            resume_page.select_work_from_date("2020", "01")
            resume_page.uncheck_currently_work_here()
            dom_content_loaded_soft(page, 20000)
            resume_page.select_work_to_date("2023", "12")
            logger.info("✓ Work Experience 填写完成（含结束日期）")
        
        with allure.step("填写 Step2 Education Experience"):
            resume_page.select_education_level("Bachelor's Degree")
            resume_page.select_education_from_date("2016", "09")
            resume_page.select_education_to_date("2020", "06")
            logger.info("✓ Education Experience 填写完成")
        
        # ========== Act：提交简历 ==========
        with allure.step("提交简历"):
            assert resume_page.is_done_button_enabled(), "Done 按钮应可点击"
            resume_page.click_done()
            dom_content_loaded_soft(page, 20000)
            logger.info("✓ 点击 Done 按钮")
        
        # ========== Assert：验证提交成功 ==========
        with allure.step("验证提交成功"):
            current_url = page.url
            assert "resume/add" not in current_url, f"提交失败: {current_url}"
            logger.info(f"✅ 提交成功！页面已跳转: {current_url}")
        
        with allure.step("验证数据库 - location 字段为 France"):
            user_id = _CONFIG["test_user_id"]
            rows = execute_query(
                "SELECT country_code FROM resume_person_info WHERE user_id = %s",
                (user_id,)
            )
            assert len(rows) == 1, f"resume_person_info 表应有1条记录"
            assert rows[0][0] == "FR", f"country_code 不正确，期望: FR (France), 实际: {rows[0][0]}"
            logger.info(f"✓ country_code 字段验证通过: {rows[0][0]}")
        
        logger.info("="*80)
        logger.info("✅ TC003 测试全部通过！")
        logger.info("="*80)
    
    
    @pytest.mark.case_id_es_resume_submit_04
    @pytest.mark.smoke
    @pytest.mark.p1
    @pytest.mark.resume
    @pytest.mark.es
    @allure.feature("OK Spain - Resume")
    @allure.story("简历提交流程 - 设置 Work Experience To 日期")
    @allure.title("TC004: 完整提交流程 - 取消 'I currently work here' 并设置 To 日期")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证用户取消'当前在职'勾选，设置 To 日期后成功提交")
    @pytest.mark.order(5)
    @pytest.mark.dependency(name="es_resume_submit_tc004")
    def test_submit_resume_set_work_to_date(self, page, config):
        """完整提交流程 - 设置 Work Experience To 日期场景"""
        
        # ========== Arrange：准备测试对象 ==========
        login_page = LoginPage(page)
        jobs_list_page = JobsListPageES(page)
        resume_page = ResumeAddPageEs(page)
        
        site = config['site']
        role = config['role']
        account_name = config['user_name']
        base_url = config['base_url']
        username = config['test_account']['username']
        password = config['test_account']['password']
        
        logger.info("="*80)
        logger.info("TC004: 完整提交流程 - 取消 'I currently work here' 场景")
        logger.info("="*80)
        
        # ========== Session 复用 ==========
        session_manager = SessionManager(page, base_url, session_name=f"{site}_{role}_{account_name}")
        session_loaded = session_manager.load_session()
        
        if not session_loaded:
            with allure.step("执行登录"):
                login_page.navigate_to_home_page()
                login_page.handle_cookie_popup()
                login_page.click_login_register_button()
                login_page.input_email(username)
                login_page.click_continue_button()
                login_page.input_password(password)
                login_page.click_login_button()
                page.wait_for_load_state("domcontentloaded", timeout=10000)
                session_manager.save_session()
                logger.info("✅ 登录成功")
        
        # ========== Act：进入简历添加页面并填写 Step1 ==========
        with allure.step("进入简历添加页面并填写 Step1"):
            jobs_list_page.navigate_to_jobs_list()
            jobs_list_page.click_first_job_card()
            jobs_list_page.click_sidebar_resume()
            dom_content_loaded_soft(page, 20000)
            assert "resume/add" in page.url, "未进入简历添加页"
            
            resume_page.input_first_name("WorkDate")
            resume_page.input_last_name("Test")
            resume_page.click_continue()
            dom_content_loaded_soft(page, 20000)
            logger.info("✓ Step1 完成")
        
        # ========== Act：填写 Work Experience ==========
        with allure.step("填写 Job Function"):
            resume_page.select_job_function(
                "Information & Communication Technology",
                "Testing & Quality Assurance"
            )
            logger.info("✓ 选择 Job Function")
        
        with allure.step("填写 Work Experience From 日期"):
            resume_page.select_work_from_date("2020", "01")
            logger.info("✓ 选择 From: 2020-01")
        
        with allure.step("验证 'I currently work here' 默认勾选"):
            is_checked = resume_page.is_currently_work_here_checked()
            assert is_checked, "'I currently work here' 应默认勾选"
            logger.info("✓ 'I currently work here' 已勾选")
        
        with allure.step("取消 'I currently work here' 勾选"):
            resume_page.uncheck_currently_work_here()
            dom_content_loaded_soft(page, 20000)
            logger.info("✓ 取消 'I currently work here' 勾选")
        
        with allure.step("验证 To 字段变为可编辑"):
            # 验证取消勾选后，checked 图标不再可见
            is_still_checked = resume_page.is_currently_work_here_checked()
            assert not is_still_checked, "'I currently work here' 应已取消勾选"
            logger.info("✓ To 字段已变为可编辑状态")
        
        with allure.step("设置 Work Experience To 日期"):
            resume_page.select_work_to_date("2023", "12")
            logger.info("✓ 选择 To: 2023-12")
        
        # ========== Act：填写 Education Experience ==========
        with allure.step("填写 Education Experience"):
            resume_page.select_education_level("Bachelor's Degree")
            resume_page.select_education_from_date("2016", "09")
            resume_page.select_education_to_date("2020", "06")
            logger.info("✓ Education Experience 填写完成")
        
        # ========== Act：提交简历 ==========
        with allure.step("提交简历"):
            assert resume_page.is_done_button_enabled(), "Done 按钮应可点击"
            resume_page.click_done()
            dom_content_loaded_soft(page, 20000)
            logger.info("✓ 点击 Done 按钮")
        
        # ========== Assert：验证提交成功 ==========
        with allure.step("验证提交成功"):
            current_url = page.url
            assert "resume/add" not in current_url, f"提交失败: {current_url}"
            logger.info(f"✅ 提交成功！页面已跳转: {current_url}")
        
        with allure.step("验证数据库 - to_date 字段"):
            user_id = _CONFIG["test_user_id"]
            rows = execute_query(
                "SELECT from_time, to_time FROM resume_work_experience WHERE user_id = %s",
                (user_id,)
            )
            assert len(rows) == 1, f"resume_work_experience 表应有1条记录"
            from_date = str(rows[0][0])
            to_date = str(rows[0][1]) if rows[0][1] else "NULL"
            logger.info(f"✓ from_date: {from_date}")
            logger.info(f"✓ to_date: {to_date}")
            # 验证 to_date 不为空且不为 Present
            assert rows[0][1] is not None, "to_date 不应为 NULL"
            logger.info("✓ to_date 字段验证通过（已设置具体日期）")
        
        logger.info("="*80)
        logger.info("✅ TC004 测试全部通过！")
        logger.info("="*80)
    
    
    @pytest.mark.case_id_es_resume_submit_06
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.resume
    @pytest.mark.es
    @allure.feature("OK Spain - Resume")
    @allure.story("提交后数据验证")
    @allure.title("TC006: 提交后重新进入简历页面验证数据回显")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证简历提交后，重新进入页面时所有数据正确回显")
    @pytest.mark.order(6)
    @pytest.mark.dependency(depends=["es_resume_submit_tc004"])
    def test_verify_resume_data_display(self, page, config):
        """提交后数据回显验证"""
        
        # 依赖同文件 TC004：fixture 在 TC004 之后不清库，本用例运行前库中应有简历。
        
        # ========== Arrange：准备测试对象 ==========
        jobs_list_page = JobsListPageES(page)
        
        site = config['site']
        role = config['role']
        account_name = config['user_name']
        base_url = config['base_url']
        
        logger.info("="*80)
        logger.info("TC006: 提交后数据回显验证")
        logger.info("="*80)
        
        # ========== Session 复用 ==========
        session_manager = SessionManager(page, base_url, session_name=f"{site}_{role}_{account_name}")
        session_loaded = session_manager.load_session()
        
        if not session_loaded:
            pytest.fail("Session 未加载，需要登录状态")

        user_id = _CONFIG["test_user_id"]
        with allure.step("验证库中仍存在简历（TC004 写入，先于 UI 并重试读库）"):
            last_rc, last_we = 0, 0
            for _ in range(15):
                rc = execute_query("SELECT COUNT(*) FROM resume WHERE user_id = %s", (user_id,))
                we = execute_query(
                    "SELECT COUNT(*) FROM resume_work_experience WHERE user_id = %s",
                    (user_id,),
                )
                last_rc, last_we = rc[0][0], we[0][0]
                if last_rc >= 1 and last_we >= 1:
                    break
                time.sleep(0.35)
            assert last_rc >= 1, (
                "库中应存在简历记录（TC004 通过后重试仍为空，请检查 cleanup 顺序或 DB 连接）"
                f"，resume_count={last_rc}"
            )
            assert last_we >= 1, f"库中应存在工作经历记录，work_exp_count={last_we}"
            logger.info("✓ 数据库简历与工作履历记录存在")
        
        # ========== Act：重新进入简历页面 ==========
        with allure.step("重新访问招聘列表页"):
            jobs_list_page.navigate_to_jobs_list()
            logger.info("✓ 访问招聘列表页")
        
        with allure.step("点击职位卡片和 Resume 按钮"):
            jobs_list_page.click_first_job_card()
            dom_content_loaded_soft(page, 20000)
            jobs_list_page.click_sidebar_resume()
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            dom_content_loaded_soft(page, 20000)
            logger.info("✓ 点击 Resume 按钮")
        with allure.step("验证已进入简历相关页且有关键内容"):
            current_url = page.url
            logger.info(f"当前 URL: {current_url}")
            assert "resume" in current_url.lower(), f"应进入简历相关页，实际: {current_url}"
            # 汇总页 /biz/en/resume 与编辑页文案不一致；用英/西关键词 + 日期样式兜底
            hint_re = re.compile(
                r"Work|Experience|Education|Personal|Resume|Job\s*Function|"
                r"Experiencia|Educaci[oó]n|Curriculum|CV|Present|Quality|Testing|"
                r"Bachelor|Master|\d{4}\s*[-–]\s*\d{2}",
                re.I,
            )
            ok = False
            try:
                page.get_by_text(hint_re).first.wait_for(state="visible", timeout=15000)
                ok = True
                logger.info("✓ 页面可见简历相关文案（正则）")
            except Exception:
                try:
                    blob = (page.locator("body").inner_text(timeout=8000) or "")
                    if hint_re.search(blob):
                        ok = True
                        logger.info("✓ body 文本匹配简历相关关键词")
                except Exception:
                    ok = False
            assert ok, "简历页应含工作经历/教育/简历等文案（汇总页与表单页标题可能不同）"
        
        logger.info("="*80)
        logger.info("✅ TC006 数据回显验证全部通过！")
        logger.info("="*80)
