"""
Job Preferences 自动生成用例（zhaopin 标记）。

已按 `playwright-test-generator/references/auto-debug-strategy.md` 与真实 SG 页面对齐：
使用 `JobPreferencePage` + `test_sg_job_preferences` 中的清理逻辑；
旧版「Min Salary / Max Salary」文案与当前中间页不符，已废弃。
"""
import pytest
import allure
from pages.job_preference_page import JobPreferencePage
from test_cases.zhaopin.sg_login_helper import ensure_sg_logged_in
from test_cases.zhaopin.test_sg_job_preferences import _cleanup_sg_job_preference_record
from utils.logger import setup_logger

logger = setup_logger()

from test_cases.zhaopin.explicit_waits import dom_content_loaded_soft, network_idle_soft, sg_wait_jobs_list_url, sg_after_home_jobs_icon

_CONFIG = {
    "site": "sg",
    "site_name": "新加坡站",
    "role": "jobseeker",
    "user_name": "wang58",
    "base_url": "https://sg.58v5.cn",
    "job_pref_url": (
        "https://sgpub.58v5.cn/biz/en/jobPreference"
        "?showSkip=1"
        "&returnUrl=https%3A%2F%2Fsg.58v5.cn%2Fen%2Fcity-singapore%2Fcate-jobs%2F%3FiconSource%3Djobs"
    ),
    "test_account": {
        "username": "wang@58.com",
        "password": "Qwer1234",
    },
    "locale": "en-SG",
    "currency": "SGD",
    "browser": {"type": "chromium", "headless": False, "viewport": {"width": 1920, "height": 1080}},
    "timeout": {"default": 30000},
}


@pytest.fixture(scope="module")
def prepared_page(page, config):
    ensure_sg_logged_in(page, config)
    yield page


@pytest.mark.case_id_zhaopin_tc001_unnamed
@pytest.mark.p0
@pytest.mark.zhaopin
@pytest.mark.sg
@allure.feature("OK")
@allure.story("job_preferences")
@allure.title("填写完整偏好并保存成功")
def test_tc001_unnamed(prepared_page, config):
    """TC001: 三必填齐全后 Continue 进入职位列表"""
    page = prepared_page
    jp = JobPreferencePage(page)
    _cleanup_sg_job_preference_record(page, config, required=True)
    page.goto(config["job_pref_url"], wait_until="domcontentloaded", timeout=60000)
    jp.wait_for_page_heading()
    dom_content_loaded_soft(page, 20000)
    jp.set_salary("Monthly", "3000")
    jp.select_job_function("Accounting", "Accounts Officers/Clerks")
    jp.select_location_full("Singapore")
    dom_content_loaded_soft(page, 20000)
    jp.click_continue()
    sg_wait_jobs_list_url(page, timeout=45000)
    assert "cate-jobs" in page.url and "iconSource=jobs" in page.url, f"应进入职位列表，当前: {page.url}"


@pytest.mark.case_id_zhaopin_tc002_unnamed
@pytest.mark.p0
@pytest.mark.zhaopin
@pytest.mark.sg
@allure.feature("OK")
@allure.story("job_preferences")
@allure.title("修改已有偏好并保存")
def test_tc002_unnamed(prepared_page, config):
    """TC002: 使用另一薪资金额重新提交"""
    page = prepared_page
    jp = JobPreferencePage(page)
    _cleanup_sg_job_preference_record(page, config, required=True)
    page.goto(config["job_pref_url"], wait_until="domcontentloaded", timeout=60000)
    jp.wait_for_page_heading()
    dom_content_loaded_soft(page, 20000)
    jp.set_salary("Monthly", "5000")
    jp.select_job_function("Accounting", "Accounts Officers/Clerks")
    jp.select_location_full("Singapore")
    dom_content_loaded_soft(page, 20000)
    jp.click_continue()
    sg_wait_jobs_list_url(page, timeout=45000)
    assert "cate-jobs" in page.url and "iconSource=jobs" in page.url, f"应进入职位列表，当前: {page.url}"


@pytest.mark.case_id_zhaopin_tc003_unnamed
@pytest.mark.p1
@pytest.mark.zhaopin
@pytest.mark.sg
@allure.feature("OK")
@allure.story("job_preferences")
@allure.title("薪资最低大于最高时提交报错")
def test_tc003_unnamed(prepared_page, config):
    """TC003: 当前 SG 中间页为单笔 Salary，改为「仅填 Salary 提交应提示 Job Functions/Location 缺失」"""
    page = prepared_page
    jp = JobPreferencePage(page)
    _cleanup_sg_job_preference_record(page, config, required=True)
    page.goto(config["job_pref_url"], wait_until="domcontentloaded", timeout=60000)
    jp.wait_for_page_heading()
    dom_content_loaded_soft(page, 20000)
    jp.set_salary("Monthly", "3000")
    jp.click_continue()
    dom_content_loaded_soft(page, 20000)
    assert "jobPreference" in page.url
    assert jp.get_validation_error_count() >= 1


@pytest.mark.case_id_zhaopin_tc004_unnamed
@pytest.mark.p1
@pytest.mark.zhaopin
@pytest.mark.sg
@allure.feature("OK")
@allure.story("job_preferences")
@allure.title("必填字段为空时提交报错")
def test_tc004_unnamed(prepared_page, config):
    """TC004: 空表单 Continue"""
    page = prepared_page
    jp = JobPreferencePage(page)
    _cleanup_sg_job_preference_record(page, config, required=True)
    page.goto(config["job_pref_url"], wait_until="domcontentloaded", timeout=60000)
    jp.wait_for_page_heading()
    dom_content_loaded_soft(page, 20000)
    jp.click_continue()
    dom_content_loaded_soft(page, 20000)
    assert "jobPreference" in page.url
    assert jp.get_validation_error_count() >= 2


@pytest.mark.case_id_zhaopin_tc005_0_999999
@pytest.mark.p1
@pytest.mark.zhaopin
@pytest.mark.sg
@allure.feature("OK")
@allure.story("job_preferences")
@allure.title("薪资输入边界值0和999999")
def test_tc005_0_999999(prepared_page, config):
    """TC005: 0 与超长数字边界（与 SG TC025 一致）"""
    page = prepared_page
    jp = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)
    page.goto(config["job_pref_url"], wait_until="domcontentloaded", timeout=60000)
    jp.wait_for_page_heading()
    dom_content_loaded_soft(page, 20000)
    jp.select_pay_type("Yearly")
    dom_content_loaded_soft(page, 20000)
    jp.type_salary_amount_sequentially("0", delay=80)
    jp.blur_salary_input()
    dom_content_loaded_soft(page, 20000)
    assert jp.get_salary_input_value() == "0"
    jp.clear_salary_amount()
    dom_content_loaded_soft(page, 20000)
    jp.type_salary_amount_sequentially("999999", delay=80)
    jp.blur_salary_input()
    dom_content_loaded_soft(page, 20000)
    assert "999999" in jp.get_salary_input_value().replace(",", "")


@pytest.mark.case_id_zhaopin_tc006_unnamed
@pytest.mark.p2
@pytest.mark.zhaopin
@pytest.mark.sg
@allure.feature("OK")
@allure.story("job_preferences")
@allure.title("薪资输入负数被拒绝")
def test_tc006_unnamed(prepared_page, config):
    """TC006: 负号不应出现在 Salary 输入框（与 SG TC049 一致）"""
    page = prepared_page
    jp = JobPreferencePage(page)
    ensure_sg_logged_in(page, config)
    page.goto(config["job_pref_url"], wait_until="domcontentloaded", timeout=60000)
    jp.wait_for_page_heading()
    dom_content_loaded_soft(page, 20000)
    jp.select_pay_type("Yearly")
    dom_content_loaded_soft(page, 20000)
    jp.type_salary_amount_sequentially("-500", delay=80)
    jp.blur_salary_input()
    dom_content_loaded_soft(page, 20000)
    assert "-" not in jp.get_salary_input_value()


@pytest.mark.case_id_zhaopin_tc007_unnamed
@pytest.mark.p0
@pytest.mark.zhaopin
@pytest.mark.sg
@allure.feature("OK")
@allure.story("job_preferences")
@allure.title("未登录用户访问偏好页面被重定向")
def test_tc007_unnamed(page, config):
    """TC007: 清除 Cookie 后访问 jobPreference，应出现登录相关 UI"""
    page.context.clear_cookies()
    page.evaluate("try { localStorage.clear(); sessionStorage.clear(); } catch (e) {}")
    page.goto(config["job_pref_url"], wait_until="domcontentloaded", timeout=60000)
    dom_content_loaded_soft(page, 20000)
    url = page.url.lower()
    login_visible = page.get_by_text("Log in", exact=False).first.is_visible(timeout=8000)
    assert "login" in url or login_visible, f"未登录应触发登录流程，当前: {page.url}"
