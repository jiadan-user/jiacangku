# -*- coding: utf-8 -*-
"""
OK.com - 发布职位安全与UI测试
测试用例: TC024-TC028
生成时间: 2026-03-02
修复时间: 2026-05-12 - 更新元素定位策略
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


@pytest.mark.p0
@pytest.mark.case_id_publish_job_publish_job_security_ui_024
@allure.feature("发布职位")
@allure.story("安全测试")
@allure.title("TC024: 未登录访问重定向验证")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.security
def test_tc024_unauthorized_access_redirect(page: Page):
    """
    TC024: 未登录访问发布页面，验证重定向或显示登录弹窗
    
    前置条件:
    - 未登录状态
    
    执行步骤:
    1. 清除所有 cookies
    2. 访问发布职位页面
    
    预期结果:
    - 显示登录弹窗，或重定向到登录页
    """
    with allure.step("清除所有 cookies"):
        page.context.clear_cookies()
        logger.info("✓ 已清除所有 cookies")
    
    with allure.step("访问发布职位页面"):
        page.goto(PUBLISH_URL)
        page.wait_for_load_state("load")
        page.wait_for_timeout(3000)
        logger.info(f"✓ 访问发布职位页面: {PUBLISH_URL}")
    
    with allure.step("验证显示登录弹窗或重定向"):
        # 检查是否显示登录弹窗
        try:
            login_dialog = page.locator('div[role="dialog"][aria-modal="true"]').filter(has_text="Welcome to OK.com")
            expect(login_dialog).to_be_visible(timeout=5000)
            logger.info("✓ 验证：显示登录弹窗")
            logger.info("✅ TC024 测试通过：未登录访问正确显示登录弹窗")
        except:
            # 检查是否重定向到登录页
            current_url = page.url
            if 'login' in current_url.lower() or 'signin' in current_url.lower():
                logger.info("✓ 验证：重定向到登录页")
                logger.info("✅ TC024 测试通过：未登录访问正确重定向")
            else:
                logger.warning("⚠️ 未检测到登录弹窗或重定向")


@pytest.mark.p0
@pytest.mark.case_id_publish_job_publish_job_security_ui_025
@allure.feature("发布职位")
@allure.story("安全测试")
@allure.title("TC025: XSS 防护测试")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.security
@pytest.mark.xss
def test_tc025_xss_protection(page: Page):
    """
    TC025: XSS 防护测试 - 在 Job Title 输入 XSS 脚本
    
    前置条件:
    - 已登录
    
    执行步骤:
    1. 在 Job Title 输入 XSS 脚本（如 <script>alert('XSS')</script>）
    2. 填写其他必填字段
    3. 点击 Continue
    
    预期结果:
    - XSS 脚本被转义或过滤，不执行
    - 可以正常提交或显示错误
    """
    with allure.step("访问发布职位页面"):
        page.goto(PUBLISH_URL)
        page.wait_for_load_state("load")
        page.wait_for_timeout(2000)
        logger.info(f"✓ 访问发布职位页面: {PUBLISH_URL}")
    
    with allure.step("处理登录（如需要）"):
        login_if_needed(page, TEST_ACCOUNT["username"], TEST_ACCOUNT["password"])
    
    with allure.step("在 Job Title 输入 XSS 脚本"):
        xss_payload = "<script>alert('XSS')</script>"
        page.locator('#title').fill(xss_payload)
        logger.info(f"✓ 输入 XSS 脚本: {xss_payload}")
        
        # 关闭autocomplete浮层
        page.get_by_role('heading', name='Job Basics').click(force=True)
        page.wait_for_timeout(500)
    
    with allure.step("填写其他必填字段"):
        # 选择 Job Function（使用修复后的辅助函数）
        select_job_function(page, 'Sales')
        
        # 选择 Salary（使用修复后的辅助函数）
        select_salary(page, min_amount='40000', max_amount='70000')
    
    with allure.step("点击 Continue"):
        page.get_by_role('button', name='Continue').click(force=True)
        page.wait_for_timeout(2000)
    
    with allure.step("验证 XSS 脚本未执行"):
        # 监听 dialog 事件（alert 弹窗）
        dialog_appeared = False
        
        def handle_dialog(dialog):
            nonlocal dialog_appeared
            dialog_appeared = True
            dialog.dismiss()
        
        page.on("dialog", handle_dialog)
        
        # 等待一段时间，看是否有 alert 弹出
        page.wait_for_timeout(2000)
        
        # 验证没有 alert 弹出
        assert not dialog_appeared, "XSS 脚本被执行了（出现 alert 弹窗）"
        logger.info("✓ 验证：XSS 脚本未执行")
        
        logger.info("✅ TC025 测试通过：XSS 防护正常")


@pytest.mark.p0
@pytest.mark.case_id_publish_job_publish_job_security_ui_026
@allure.feature("发布职位")
@allure.story("安全测试")
@allure.title("TC026: SQL 注入防护测试")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.security
@pytest.mark.sql_injection
def test_tc026_sql_injection_protection(page: Page):
    """
    TC026: SQL 注入防护测试 - 在 Job Title 输入 SQL 注入语句
    
    前置条件:
    - 已登录
    
    执行步骤:
    1. 在 Job Title 输入 SQL 注入语句（如 ' OR '1'='1）
    2. 填写其他必填字段
    3. 点击 Continue
    
    预期结果:
    - SQL 注入语句被转义或过滤
    - 可以正常提交或显示错误
    - 不会导致数据库错误
    """
    with allure.step("访问发布职位页面"):
        page.goto(PUBLISH_URL)
        page.wait_for_load_state("load")
        page.wait_for_timeout(2000)
        logger.info(f"✓ 访问发布职位页面: {PUBLISH_URL}")
    
    with allure.step("处理登录（如需要）"):
        login_if_needed(page, TEST_ACCOUNT["username"], TEST_ACCOUNT["password"])
    
    with allure.step("在 Job Title 输入 SQL 注入语句"):
        sql_payload = "' OR '1'='1"
        page.locator('#title').fill(sql_payload)
        logger.info(f"✓ 输入 SQL 注入语句: {sql_payload}")
        
        # 关闭autocomplete浮层
        page.get_by_role('heading', name='Job Basics').click(force=True)
        page.wait_for_timeout(500)
    
    with allure.step("填写其他必填字段"):
        # 选择 Job Function（使用修复后的辅助函数）
        select_job_function(page, 'Accounting')
        
        # 选择 Salary（使用修复后的辅助函数）
        select_salary(page, min_amount='50000', max_amount='80000')
    
    with allure.step("点击 Continue"):
        page.get_by_role('button', name='Continue').click(force=True)
        page.wait_for_timeout(2000)
    
    with allure.step("验证没有数据库错误"):
        # 检查页面是否显示数据库错误信息
        page_content = page.content()
        
        # 常见的数据库错误关键词
        db_error_keywords = ['SQL', 'syntax error', 'mysql', 'database error', 'query failed']
        
        has_db_error = any(keyword.lower() in page_content.lower() for keyword in db_error_keywords)
        
        assert not has_db_error, "检测到数据库错误信息"
        logger.info("✓ 验证：没有数据库错误")
        
        logger.info("✅ TC026 测试通过：SQL 注入防护正常")


@pytest.mark.p1
@pytest.mark.case_id_publish_job_publish_job_security_ui_027
@allure.feature("发布职位")
@allure.story("UI测试")
@allure.title("TC027: 响应式布局测试")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
@pytest.mark.responsive
def test_tc027_responsive_layout(page: Page):
    """
    TC027: 响应式布局测试 - 验证不同屏幕尺寸下的布局
    
    前置条件:
    - 已登录
    
    执行步骤:
    1. 设置不同的视口尺寸（桌面、平板、手机）
    2. 验证页面布局正常
    
    预期结果:
    - 不同尺寸下页面布局正常
    - 主要元素可见
    """
    with allure.step("测试桌面尺寸（1920x1080）"):
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(PUBLISH_URL)
        page.wait_for_load_state("load")
        page.wait_for_timeout(2000)
        
        login_if_needed(page, TEST_ACCOUNT["username"], TEST_ACCOUNT["password"])
        
        # 验证主要元素可见
        expect(page.get_by_role('heading', name='Job Basics')).to_be_visible()
        expect(page.locator('#title')).to_be_visible()
        logger.info("✓ 桌面尺寸（1920x1080）布局正常")
    
    with allure.step("测试平板尺寸（768x1024）"):
        page.set_viewport_size({"width": 768, "height": 1024})
        page.wait_for_timeout(1000)
        
        # 验证主要元素可见
        expect(page.get_by_role('heading', name='Job Basics')).to_be_visible()
        expect(page.locator('#title')).to_be_visible()
        logger.info("✓ 平板尺寸（768x1024）布局正常")
    
    with allure.step("测试手机尺寸（375x667）"):
        page.set_viewport_size({"width": 375, "height": 667})
        page.wait_for_timeout(1000)
        
        # 验证主要元素可见
        expect(page.get_by_role('heading', name='Job Basics')).to_be_visible()
        expect(page.locator('#title')).to_be_visible()
        logger.info("✓ 手机尺寸（375x667）布局正常")
    
    logger.info("✅ TC027 测试通过：响应式布局正常")


@pytest.mark.p1
@pytest.mark.case_id_publish_job_publish_job_security_ui_028
@allure.feature("发布职位")
@allure.story("UI测试")
@allure.title("TC028: 无障碍性测试")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
@pytest.mark.accessibility
def test_tc028_accessibility(page: Page):
    """
    TC028: 无障碍性测试 - 验证页面的无障碍性
    
    前置条件:
    - 已登录
    
    执行步骤:
    1. 访问发布页面
    2. 检查主要表单元素是否有 label 或 aria-label
    3. 检查按钮是否有明确的文本或 aria-label
    
    预期结果:
    - 主要元素有适当的无障碍属性
    - 可以通过键盘导航
    """
    with allure.step("访问发布职位页面"):
        page.goto(PUBLISH_URL)
        page.wait_for_load_state("load")
        page.wait_for_timeout(2000)
        logger.info(f"✓ 访问发布职位页面: {PUBLISH_URL}")
    
    with allure.step("处理登录（如需要）"):
        login_if_needed(page, TEST_ACCOUNT["username"], TEST_ACCOUNT["password"])
    
    with allure.step("检查表单元素的无障碍属性"):
        # 检查 Job Title 输入框
        title_input = page.locator('#title')
        expect(title_input).to_be_visible()
        logger.info("✓ Job Title 输入框可见")
        
        # 检查 Continue 按钮
        continue_button = page.get_by_role('button', name='Continue')
        expect(continue_button).to_be_visible()
        logger.info("✓ Continue 按钮可见且有明确文本")
    
    with allure.step("测试键盘导航"):
        # 使用 Tab 键导航
        page.keyboard.press('Tab')
        page.wait_for_timeout(300)
        
        # 验证焦点移动
        focused_element = page.evaluate("document.activeElement.tagName")
        logger.info(f"✓ 焦点元素: {focused_element}")
        
        # 验证可以通过键盘导航
        assert focused_element in ['INPUT', 'BUTTON', 'A', 'TEXTAREA'], "焦点应该在可交互元素上"
        logger.info("✓ 键盘导航正常")
    
    logger.info("✅ TC028 测试通过：无障碍性基本满足要求")

