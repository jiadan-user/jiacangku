"""
OK美国站 - 职位发布（Job Basics）测试

本脚本由 playwright-test-generator 生成
录制文档：/Users/a58/Desktop/测试用例/OK-JobPublish-测试用例-20260302.md
生成时间：2026-03-02
"""
import pytest
import allure
from datetime import datetime
from pages.login_page import LoginPage
from pages.job_basics_page import JobBasicsPage
from utils.session_manager import SessionManager
from utils.logger import setup_logger

logger = setup_logger()

# ============================================
# 测试环境配置（来自录制文档，录制与运行使用同一账号）
# ============================================
_CONFIG = {
    "site": "us",
    "site_name": "OK美国站",
    "role": "seller",
    "user_name": "weijingjing02_us_seller",
    "base_url": "https://uspub.58v5.cn",
    "test_account": {
        "username": "weijingjing02@58.com",
        "password": "Ok123456"
    },
    "target_page": "https://uspub.58v5.cn/biz/en/publish/job?categoryId=4000",
    "locale": "en-US",
    "currency": "USD",
    "browser": {
        "type": "chromium",
        "headless": False,
        "viewport": {"width": 1920, "height": 1080}
    },
    "timeout": {
        "default": 30000,
        "wait": 10000,
        "navigation": 30000
    }
}


@pytest.fixture
def setup_job_basics_page(page, config):
    """
    准备 Job Basics 页面测试环境
    
    包含：
    1. Session 复用登录
    2. 导航到 Job Basics 页面
    3. 返回 JobBasicsPage 实例
    """
    # Session 复用
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    
    if not session_manager.load_session():
        # 首次运行或 session 过期，执行登录
        login_page = LoginPage(page)
        login_page.navigate_to_home_page()
        login_page.login(config['test_account']['username'], config['test_account']['password'])
        session_manager.save_session()
        logger.info(f"✓ 登录成功并保存 session: {session_name}")
    else:
        logger.info(f"✓ 加载 session 成功: {session_name}")
    
    # 导航到 Job Basics 页面
    page.goto(config['target_page'])
    page.wait_for_load_state("load")
    
    # 处理 Cookie 弹窗（如果存在）
    try:
        # 尝试多种可能的 Cookie 弹窗按钮文本
        cookie_selectors = [
            "button:has-text('Accept All')",
            "button:has-text('Accept all')",
            "button:has-text('Accept')",
            "button:has-text('I Accept')",
            ".CookieConsent_cookieConsent__xhIgs button"
        ]
        
        for selector in cookie_selectors:
            try:
                cookie_button = page.locator(selector).first
                if cookie_button.is_visible(timeout=2000):
                    cookie_button.click()
                    page.wait_for_timeout(1000)
                    logger.info(f"✓ 已关闭 Cookie 弹窗（使用选择器: {selector}）")
                    break
            except Exception:
                continue
    except Exception:
        # Cookie 弹窗不存在或已关闭，继续执行
        pass
    
    # 返回 Page Object
    job_basics_page = JobBasicsPage(page)
    return job_basics_page


# ============================================
# TC001: 正常填写所有必填项并提交到下一步
# ============================================
@pytest.mark.case_id_job_basics_001
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.job_publish
@pytest.mark.us
@allure.feature("OK")
@allure.story("Job Basics 页面 - 核心流程（正向）")
@allure.title("正常填写所有必填项并提交到下一步应该成功")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("填写 Job Title、Job Function、Pay Type、Salary Range，点击 Continue，验证跳转到 Job Details 页面")
def test_job_basics_submit_all_required_fields_should_success(page, config, setup_job_basics_page):
    """TC001: 正常填写所有必填项并提交到下一步"""
    job_basics_page = setup_job_basics_page
    
    # Arrange - 准备测试数据（添加时间戳确保唯一性）
    job_title = f"Software Engineer Test {datetime.now().strftime('%Y%m%d%H%M%S')}"
    job_function_category = "Information & Communication Technology"
    job_function_subcategory = "Developers/Programmers"
    pay_type = "Per Year"
    salary_min = "50000"
    salary_max = "80000"
    
    # Act - 执行操作
    logger.info("开始填写 Job Basics 表单")
    
    # 1. 输入 Job Title
    job_basics_page.input_job_title(job_title)
    logger.info(f"✓ 已输入 Job Title: {job_title}")
    
    # 2. 关闭推荐浮层（Job Title 输入后会触发）
    job_basics_page.dismiss_suggestions()
    logger.info("✓ 已关闭推荐浮层")
    
    # 3. 选择 Job Function
    job_basics_page.select_job_function(job_function_category, job_function_subcategory)
    logger.info(f"✓ 已选择 Job Function: {job_function_category} / {job_function_subcategory}")
    
    # 4. 选择 Pay Type（已经是默认值 Per Year，点击确认）
    job_basics_page.select_pay_type(pay_type)
    logger.info(f"✓ 已选择 Pay Type: {pay_type}")
    
    # 5. 选择 Salary Range
    job_basics_page.select_salary_range(salary_min, salary_max)
    logger.info(f"✓ 已选择 Salary Range: {salary_min} - {salary_max}")
    
    # 6. 点击 Continue
    job_basics_page.click_continue()
    logger.info("✓ 已点击 Continue")
    
    # Assert - 验证结果
    page.wait_for_load_state("load")
    
    # 验证1：页面标题变为 "Job Details"
    page_heading = page.get_by_role("heading", level=1).text_content()
    assert page_heading == "Job Details", f"期望页面标题为 'Job Details'，实际为 '{page_heading}'"
    logger.info("✓ 验证通过：页面标题为 'Job Details'")
    
    # 验证2：URL 仍为 Job Basics 页面（单页应用）
    current_url = page.url
    assert config['target_page'] in current_url, f"期望 URL 包含 '{config['target_page']}'，实际为 '{current_url}'"
    logger.info(f"✓ 验证通过：URL 正确 ({current_url})")
    
    # 验证3：新表单字段出现
    assert page.get_by_text("Job Description *").is_visible(), "期望 'Job Description *' 字段可见"
    assert page.get_by_text("Job Summary").is_visible(), "期望 'Job Summary' 字段可见"
    assert page.get_by_text("Job Highlights").is_visible(), "期望 'Job Highlights' 字段可见"
    logger.info("✓ 验证通过：Job Details 表单字段已显示")
    
    # 验证4：Back 按钮出现
    assert page.get_by_role("button", name="Back").is_visible(), "期望 'Back' 按钮可见"
    logger.info("✓ 验证通过：Back 按钮已显示")


# ============================================
# TC002: 从第二步点击 Back 返回第一步，数据保留
# ============================================
@pytest.mark.case_id_job_basics_002
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.job_publish
@pytest.mark.us
@allure.feature("OK")
@allure.story("Job Basics 页面 - 核心流程（正向）")
@allure.title("从第二步点击 Back 返回第一步，数据保留")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("完成 TC001 后，点击 Back 返回 Job Basics，验证所有填写的数据保留")
def test_job_basics_back_from_job_details_data_retained(page, config, setup_job_basics_page):
    """TC002: 从第二步点击 Back 返回第一步，数据保留"""
    job_basics_page = setup_job_basics_page
    
    # Arrange - 准备测试数据
    job_title = f"Software Engineer Test {datetime.now().strftime('%Y%m%d%H%M%S')}"
    job_function_category = "Information & Communication Technology"
    job_function_subcategory = "Developers/Programmers"
    pay_type = "Per Year"
    salary_min = "50000"
    salary_max = "80000"
    
    # Act - 先完成 TC001 的操作（到达 Job Details 页面）
    logger.info("开始填写 Job Basics 表单（前置步骤）")
    job_basics_page.input_job_title(job_title)
    job_basics_page.dismiss_suggestions()
    job_basics_page.select_job_function(job_function_category, job_function_subcategory)
    job_basics_page.select_pay_type(pay_type)
    job_basics_page.select_salary_range(salary_min, salary_max)
    job_basics_page.click_continue()
    page.wait_for_load_state("load")
    logger.info("✓ 已到达 Job Details 页面")
    
    # Act - 点击 Back 按钮
    page.get_by_role("button", name="Back").click()
    page.wait_for_load_state("load")
    logger.info("✓ 已点击 Back 按钮")
    
    # Assert - 验证结果
    # 验证1：返回 Job Basics 页面
    page_heading = page.get_by_role("heading", level=1).text_content()
    assert page_heading == "Job Basics", f"期望页面标题为 'Job Basics'，实际为 '{page_heading}'"
    logger.info("✓ 验证通过：已返回 Job Basics 页面")
    
    # 验证2：Job Title 数据保留
    job_title_value = page.locator('#title').input_value()
    assert job_title_value == job_title, f"期望 Job Title 为 '{job_title}'，实际为 '{job_title_value}'"
    logger.info(f"✓ 验证通过：Job Title 数据保留 ({job_title_value})")
    
    # 验证3：Job Function 数据保留
    job_function_text = page.locator('div.float-label-container.hasValue.mark-container').filter(has_text='Select Job Functions').first.text_content()
    assert job_function_category in job_function_text, f"期望 Job Function 包含 '{job_function_category}'，实际为 '{job_function_text}'"
    assert job_function_subcategory in job_function_text, f"期望 Job Function 包含 '{job_function_subcategory}'，实际为 '{job_function_text}'"
    logger.info(f"✓ 验证通过：Job Function 数据保留 ({job_function_text})")
    
    # 验证4：Salary Range 数据保留
    salary_range_text = page.locator('div').filter(has_text='Amount($)').first.text_content()
    assert salary_min in salary_range_text, f"期望第一个 Amount 为 '{salary_min}'，实际为 '{salary_range_text}'"
    logger.info(f"✓ 验证通过：Salary Range 最小值保留 ({salary_min})")
    
    salary_range_text_max = page.locator('div').filter(has_text='Amount($)').nth(1).text_content()
    assert salary_max in salary_range_text_max, f"期望第二个 Amount 为 '{salary_max}'，实际为 '{salary_range_text_max}'"
    logger.info(f"✓ 验证通过：Salary Range 最大值保留 ({salary_max})")


# ============================================
# TC003: 选择 Workplace Type 为 Remote
# ============================================
@pytest.mark.case_id_job_basics_003
@pytest.mark.p1
@pytest.mark.job_publish
@pytest.mark.us
@allure.feature("OK")
@allure.story("Job Basics 页面 - 核心流程（正向）")
@allure.title("选择 Workplace Type 为 Remote 应该成功")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("点击 Remote 单选按钮，验证 Remote 被选中，Onsite 取消选中")
def test_job_basics_select_workplace_type_remote_should_success(page, config, setup_job_basics_page):
    """TC003: 选择 Workplace Type 为 Remote"""
    job_basics_page = setup_job_basics_page
    
    # Act - 选择 Remote
    logger.info("开始选择 Workplace Type 为 Remote")
    job_basics_page.select_workplace_type_remote()
    logger.info("✓ 已点击 Remote 单选按钮")
    
    # Assert - 验证结果
    # 验证1：Remote 被选中
    remote_radio = page.get_by_role("radio", name="Selected Remote")
    assert remote_radio.is_checked(), "期望 Remote 单选按钮被选中"
    logger.info("✓ 验证通过：Remote 已被选中")
    
    # 验证2：Onsite 取消选中
    onsite_radio = page.get_by_role("radio", name="Unselected Onsite")
    assert not onsite_radio.is_checked(), "期望 Onsite 单选按钮未被选中"
    logger.info("✓ 验证通过：Onsite 已取消选中")
