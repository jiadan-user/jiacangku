# -*- coding: utf-8 -*-
"""
OK.com - 发布职位导航和草稿功能测试
测试用例: TC022-TC023
生成时间: 2026-03-02
修复时间: 2026-05-12 - 更新元素定位策略，删除TC020-TC021（Step3已移除）
"""

import re
import pytest
import allure
from playwright.sync_api import Page, expect
from test_cases.publish_job.login_helper import login_if_needed
from test_cases.publish_job.publish_job_helpers import (
    select_job_function,
    select_salary,
    fill_job_title,
    fill_job_description
)
from utils.logger import setup_logger

logger = setup_logger()

# 测试数据
BASE_URL = "https://uspub.58v5.cn"
PUBLISH_URL = f"{BASE_URL}/biz/en/publish/job?categoryId=4000"
TEST_ACCOUNT = {
    "username": "weijingjing02@58.com",
    "password": "Ok123456"
}


def complete_step1(page: Page):
    """辅助函数：快速完成 Step1"""
    page.locator('#title').fill('Test Job for Navigation')
    page.get_by_role('heading', name='Job Basics').click(force=True)
    page.wait_for_timeout(500)
    
    # 使用修复后的辅助函数
    select_job_function(page, 'Engineering', 'Systems Engineering')
    select_salary(page, min_amount='40000', max_amount='70000')
    
    page.get_by_role('button', name='Continue').first.click(force=True)
    page.wait_for_load_state("load")
    page.wait_for_timeout(2000)
    
    expect(page.get_by_role('heading', name='Job Details')).to_be_visible()
    logger.info("✓ Step1 完成，已进入 Step2")


def complete_step2_and_publish(page: Page):
    """辅助函数：快速完成 Step2 并发布"""
    page.locator('#content').fill('Test job description for navigation tests.')
    page.get_by_role('button', name='Post').first.click(force=True)
    page.wait_for_load_state("load")
    page.wait_for_timeout(3000)
    
    # 验证发布成功
    expect(page.get_by_role('heading', name='Submitted successfully')).to_be_visible()
    logger.info("✓ Step2 完成，职位已发布")


@pytest.mark.p1
@pytest.mark.case_id_publish_job_publish_job_step3_navigation_022
@allure.feature("发布职位")
@allure.story("导航功能")
@allure.title("TC022: Step2 Back 按钮返回 Step1")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.navigation
def test_tc022_step2_back_to_step1(page: Page):
    """
    TC022: Step2 点击 Back 按钮返回 Step1
    
    前置条件:
    - 已完成 Step1，进入 Step2
    
    执行步骤:
    1. 在 Step2 点击 Back 按钮
    
    预期结果:
    - 返回 Step1
    - Step1 的数据保留
    """
    with allure.step("访问发布职位页面"):
        page.goto(PUBLISH_URL)
        page.wait_for_load_state("load")
        page.wait_for_timeout(2000)
        logger.info(f"✓ 访问发布职位页面: {PUBLISH_URL}")
    
    with allure.step("处理登录（如需要）"):
        login_if_needed(page, TEST_ACCOUNT["username"], TEST_ACCOUNT["password"])
    
    with allure.step("完成 Step1"):
        complete_step1(page)
    
    with allure.step("Step2: 点击 Back 按钮"):
        page.get_by_role('button', name='Back').click(force=True)
        page.wait_for_load_state("load")
        page.wait_for_timeout(2000)
        logger.info("✓ 点击 Back 按钮")
    
    with allure.step("验证返回 Step1"):
        expect(page.get_by_role('heading', name='Job Basics')).to_be_visible()
        
        # 验证 Job Title 数据保留
        title_value = page.locator('#title').input_value()
        assert len(title_value) > 0, "Job Title 数据应该保留"
        logger.info("✓ 验证：返回 Step1，数据保留")
        
        logger.info("✅ TC022 测试通过：Back 按钮正确返回 Step1")


@pytest.mark.p1
@pytest.mark.case_id_publish_job_publish_job_step3_navigation_023
@allure.feature("发布职位")
@allure.story("草稿功能")
@allure.title("TC023: 保存草稿功能验证")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.draft
def test_tc023_save_draft_functionality(page: Page):
    """
    TC023: 保存草稿功能验证
    
    前置条件:
    - 在 Step1 页面
    
    执行步骤:
    1. 填写部分 Step1 字段
    2. 点击 "Save the draft" 按钮
    
    预期结果:
    - 显示 "Draft saved" 提示
    - 可以继续编辑或退出
    """
    with allure.step("访问发布职位页面"):
        page.goto(PUBLISH_URL)
        page.wait_for_load_state("load")
        page.wait_for_timeout(2000)
        logger.info(f"✓ 访问发布职位页面: {PUBLISH_URL}")
    
    with allure.step("处理登录（如需要）"):
        login_if_needed(page, TEST_ACCOUNT["username"], TEST_ACCOUNT["password"])
    
    with allure.step("Step1: 填写部分字段"):
        # 填写 Job Title
        page.locator('#title').fill('Draft Job Title')
        page.get_by_role('heading', name='Job Basics').click(force=True)
        page.wait_for_timeout(500)
        logger.info("✓ 填写 Job Title")
        
        # 选择 Job Function（使用修复后的辅助函数）
        select_job_function(page, 'Marketing & Communications', 'Management')
        logger.info("✓ 选择 Job Function")
        
        # 选择 Salary（使用修复后的辅助函数）
        select_salary(page, min_amount='60000', max_amount='100000')
        logger.info("✓ 选择 Salary Range")
    
    with allure.step("点击 Save the draft 按钮"):
        # 点击 "Save the draft" 按钮
        page.locator('div').filter(has_text=re.compile(r"^Save the draft$")).click(force=True)
        page.wait_for_timeout(2000)
        logger.info("✓ 点击 Save the draft 按钮")
    
    with allure.step("验证显示 Draft saved 提示"):
        # 验证显示 "Draft saved" 提示
        expect(page.get_by_text('Draft saved')).to_be_visible(timeout=5000)
        logger.info("✓ 验证：显示 Draft saved 提示")
        
        logger.info("✅ TC023 测试通过：保存草稿功能正常")

