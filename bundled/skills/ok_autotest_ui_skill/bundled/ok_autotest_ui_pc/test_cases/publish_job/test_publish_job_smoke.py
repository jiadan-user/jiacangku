# test_cases/publish_job/test_publish_job_smoke.py
"""
OK - 发布职位冒烟测试
快速验证核心功能可用性
"""
import pytest
import allure
import re
from playwright.sync_api import Page, expect
from utils.logger import setup_logger
from test_cases.publish_job.login_helper import login_if_needed

logger = setup_logger()


@pytest.mark.case_id_publish_job_publish_job_smoke_002
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.us
@allure.feature("OK")
@allure.story("发布职位 - 冒烟测试")
@allure.title("登录并访问发布职位页面")
@allure.severity(allure.severity_level.BLOCKER)
def test_login_and_access_publish_page(page: Page, config):
    """冒烟测试：登录并访问发布职位页面"""
    base_url = "https://uspub.58v5.cn"
    
    logger.info("="*80)
    logger.info("冒烟测试：登录并访问发布职位页面")
    logger.info("="*80)
    
    with allure.step("访问发布职位页面"):
        page.goto(f"{base_url}/biz/en/publish/job?categoryId=4000")
        login_if_needed(page, "weijingjing02@58.com", "Ok123456")
        page.wait_for_load_state("load")
        page.wait_for_timeout(2000)
    
    with allure.step("验证页面加载成功"):
        expect(page.locator("h1:has-text('Job Basics')")).to_be_visible(timeout=10000)
        logger.info("✓ 页面加载成功")


@pytest.mark.case_id_publish_job_publish_job_smoke_001
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.us
@allure.feature("OK")
@allure.story("发布职位 - 冒烟测试")
@allure.title("Job Title 输入功能")
@allure.severity(allure.severity_level.CRITICAL)
def test_job_title_input(page: Page, config):
    """冒烟测试：Job Title 输入功能"""
    base_url = "https://uspub.58v5.cn"
    
    logger.info("="*80)
    logger.info("冒烟测试：Job Title 输入")
    logger.info("="*80)
    
    page.goto(f"{base_url}/biz/en/publish/job?categoryId=4000")
    login_if_needed(page, "weijingjing02@58.com", "Ok123456")
    page.wait_for_load_state("load")
    page.wait_for_timeout(2000)
    
    with allure.step("输入 Job Title"):
        page.locator("#title").fill("Test Job Title")
        logger.info("✓ 输入 Job Title")
    
    with allure.step("验证输入值"):
        value = page.locator("#title").input_value()
        assert value == "Test Job Title"
        logger.info(f"✓ 验证输入值: {value}")


@pytest.mark.case_id_publish_job_publish_job_smoke_004
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.us
@allure.feature("OK")
@allure.story("发布职位 - 冒烟测试")
@allure.title("必填字段校验")
@allure.severity(allure.severity_level.CRITICAL)
def test_required_field_validation(page: Page, config):
    """冒烟测试：必填字段校验"""
    base_url = "https://uspub.58v5.cn"
    
    logger.info("="*80)
    logger.info("冒烟测试：必填字段校验")
    logger.info("="*80)
    
    page.goto(f"{base_url}/biz/en/publish/job?categoryId=4000")
    login_if_needed(page, "weijingjing02@58.com", "Ok123456")
    page.wait_for_load_state("load")
    page.wait_for_timeout(2000)
    
    with allure.step("不填写任何字段，直接点击 Continue"):
        page.get_by_role("button", name="Continue").first.click(force=True)
        page.wait_for_timeout(1000)
    
    with allure.step("验证显示校验错误"):
        # 浏览器原生校验会阻止表单提交
        # 验证仍在 Step1 页面
        expect(page.locator("h1:has-text('Job Basics')")).to_be_visible()
        logger.info("✓ 必填字段校验生效")


@pytest.mark.case_id_publish_job_publish_job_smoke_003
@pytest.mark.smoke
@pytest.mark.p1
@pytest.mark.us
@allure.feature("OK")
@allure.story("发布职位 - 冒烟测试")
@allure.title("页面元素完整性检查")
@allure.severity(allure.severity_level.NORMAL)
def test_page_elements_completeness(page: Page, config):
    """冒烟测试：页面元素完整性"""
    base_url = "https://uspub.58v5.cn"
    
    logger.info("="*80)
    logger.info("冒烟测试：页面元素完整性")
    logger.info("="*80)
    
    page.goto(f"{base_url}/biz/en/publish/job?categoryId=4000")
    login_if_needed(page, "weijingjing02@58.com", "Ok123456")
    page.wait_for_load_state("load")
    page.wait_for_timeout(2000)
    
    with allure.step("验证关键元素存在"):
        expect(page.locator("h1:has-text('Job Basics')")).to_be_visible()
        expect(page.locator("#title")).to_be_visible()
        expect(page.locator("text=Select Job Functions")).to_be_visible()
        # 验证 Continue 按钮（使用 first 避免 strict mode violation）
        expect(page.get_by_role("button", name="Continue").first).to_be_visible()
        logger.info("✓ 所有关键元素存在")
