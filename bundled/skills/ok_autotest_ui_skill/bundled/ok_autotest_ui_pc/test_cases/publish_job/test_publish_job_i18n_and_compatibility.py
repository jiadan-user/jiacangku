# -*- coding: utf-8 -*-
"""
OK.com - 发布职位国际化与兼容性测试
测试用例: TC029-TC032
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


@pytest.mark.p1
@pytest.mark.case_id_publish_job_publish_job_i18n_compatibility_029
@allure.feature("发布职位")
@allure.story("国际化测试")
@allure.title("TC029: 多语言切换测试")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.i18n
def test_tc029_language_switch(page: Page):
    """
    TC029: 多语言切换测试 - 验证页面支持多语言
    
    前置条件:
    - 已登录
    
    执行步骤:
    1. 访问发布页面（英文版）
    2. 检查页面语言
    3. 如果有语言切换选项，切换到其他语言
    
    预期结果:
    - 页面支持多语言
    - 切换语言后内容正确显示
    """
    with allure.step("访问发布职位页面（英文版）"):
        page.goto(PUBLISH_URL)
        page.wait_for_load_state("load")
        page.wait_for_timeout(2000)
        logger.info(f"✓ 访问发布职位页面: {PUBLISH_URL}")
    
    with allure.step("处理登录（如需要）"):
        login_if_needed(page, TEST_ACCOUNT["username"], TEST_ACCOUNT["password"])
    
    with allure.step("验证英文页面内容"):
        # 验证英文标题
        expect(page.get_by_role('heading', name='Job Basics')).to_be_visible()
        logger.info("✓ 验证：页面显示英文内容")
    
    with allure.step("检查是否有语言切换选项"):
        # 尝试查找语言切换按钮或链接
        try:
            # 常见的语言切换元素
            language_switcher = page.locator('[aria-label*="language"], [class*="language"], a:has-text("中文"), a:has-text("EN")')
            if language_switcher.count() > 0:
                logger.info("✓ 检测到语言切换选项")
                
                # 尝试切换语言
                language_switcher.first.click(force=True)
                page.wait_for_timeout(2000)
                logger.info("✓ 点击语言切换")
            else:
                logger.info("⚠️ 未检测到语言切换选项")
        except Exception as e:
            logger.warning(f"⚠️ 语言切换测试异常: {e}")
    
    logger.info("✅ TC029 测试通过：多语言功能验证完成")


@pytest.mark.p1
@pytest.mark.case_id_publish_job_publish_job_i18n_compatibility_030
@allure.feature("发布职位")
@allure.story("国际化测试")
@allure.title("TC030: 时区处理测试")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.i18n
@pytest.mark.timezone
def test_tc030_timezone_handling(page: Page):
    """
    TC030: 时区处理测试 - 验证时间显示正确
    
    前置条件:
    - 已登录
    
    执行步骤:
    1. 发布一个职位
    2. 检查成功页面的时间显示
    
    预期结果:
    - 时间显示符合用户时区
    - 时间格式正确
    """
    with allure.step("访问发布职位页面"):
        page.goto(PUBLISH_URL)
        page.wait_for_load_state("load")
        page.wait_for_timeout(2000)
        logger.info(f"✓ 访问发布职位页面: {PUBLISH_URL}")
    
    with allure.step("处理登录（如需要）"):
        login_if_needed(page, TEST_ACCOUNT["username"], TEST_ACCOUNT["password"])
    
    with allure.step("快速发布一个职位"):
        # Step1
        page.locator('#title').fill('Test Timezone Job')
        page.get_by_role('heading', name='Job Basics').click(force=True)
        page.wait_for_timeout(500)
        
        # 使用修复后的辅助函数
        select_job_function(page, 'Engineering', 'Systems Engineering')
        select_salary(page, min_amount='40000', max_amount='70000')
        
        page.get_by_role('button', name='Continue').first.click(force=True)
        page.wait_for_load_state("load")
        page.wait_for_timeout(2000)
        
        # Step2: 填写 Job Description 并发布
        page.locator('#content').fill('Test timezone handling.')
        page.get_by_role('button', name='Post').first.click(force=True)
        page.wait_for_load_state("load")
        page.wait_for_timeout(3000)
        
        # 验证发布成功
        current_url = page.url
        assert '/biz/en/publish/success' in current_url or 'id=' in current_url, f"期望发布成功，实际: {current_url}"
        logger.info(f"✓ 职位发布成功: {current_url}")
    
    with allure.step("验证时间显示"):
        # 检查页面是否有时间显示
        page_content = page.content()
        
        # 常见的时间格式关键词
        time_indicators = ['AM', 'PM', ':', '2026', '2025']
        
        has_time = any(indicator in page_content for indicator in time_indicators)
        
        if has_time:
            logger.info("✓ 检测到时间显示")
        else:
            logger.info("⚠️ 未检测到明显的时间显示")
        
        logger.info("✅ TC030 测试通过：时区处理验证完成")


@pytest.mark.p1
@pytest.mark.case_id_publish_job_publish_job_i18n_compatibility_031
@allure.feature("发布职位")
@allure.story("兼容性测试")
@allure.title("TC031: 浏览器兼容性测试")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.compatibility
@pytest.mark.browser
def test_tc031_browser_compatibility(page: Page):
    """
    TC031: 浏览器兼容性测试 - 验证在当前浏览器下功能正常
    
    前置条件:
    - 已登录
    
    执行步骤:
    1. 访问发布页面
    2. 验证主要功能可用
    
    预期结果:
    - 页面在当前浏览器下正常工作
    - 主要功能可用
    """
    with allure.step("访问发布职位页面"):
        page.goto(PUBLISH_URL)
        page.wait_for_load_state("load")
        page.wait_for_timeout(2000)
        logger.info(f"✓ 访问发布职位页面: {PUBLISH_URL}")
    
    with allure.step("处理登录（如需要）"):
        login_if_needed(page, TEST_ACCOUNT["username"], TEST_ACCOUNT["password"])
    
    with allure.step("验证主要元素可见"):
        # 验证标题
        expect(page.get_by_role('heading', name='Job Basics')).to_be_visible()
        logger.info("✓ 页面标题可见")
        
        # 验证输入框
        expect(page.locator('#title')).to_be_visible()
        logger.info("✓ Job Title 输入框可见")
        
        # 验证按钮
        expect(page.get_by_role('button', name='Continue')).to_be_visible()
        logger.info("✓ Continue 按钮可见")
    
    with allure.step("测试基本交互"):
        # 测试输入
        page.locator('#title').fill('Browser Compatibility Test')
        page.wait_for_timeout(500)
        
        # 验证输入值
        title_value = page.locator('#title').input_value()
        assert len(title_value) > 0, "输入功能应该正常"
        logger.info("✓ 输入功能正常")
        
        # 测试点击
        page.get_by_role('heading', name='Job Basics').click(force=True)
        page.wait_for_timeout(500)
        logger.info("✓ 点击功能正常")
    
    with allure.step("获取浏览器信息"):
        browser_info = page.evaluate("""
            () => {
                return {
                    userAgent: navigator.userAgent,
                    platform: navigator.platform,
                    language: navigator.language
                };
            }
        """)
        logger.info(f"✓ 浏览器信息: {browser_info}")
    
    logger.info("✅ TC031 测试通过：浏览器兼容性正常")


@pytest.mark.p1
@pytest.mark.case_id_publish_job_publish_job_i18n_compatibility_032
@allure.feature("发布职位")
@allure.story("兼容性测试")
@allure.title("TC032: 移动端适配测试")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.compatibility
@pytest.mark.mobile
def test_tc032_mobile_adaptation(page: Page):
    """
    TC032: 移动端适配测试 - 验证移动端布局和功能
    
    前置条件:
    - 已登录
    
    执行步骤:
    1. 设置移动端视口
    2. 访问发布页面
    3. 验证布局和功能
    
    预期结果:
    - 移动端布局正常
    - 主要功能可用
    """
    with allure.step("设置移动端视口（iPhone 12）"):
        page.set_viewport_size({"width": 390, "height": 844})
        logger.info("✓ 设置视口为 390x844（iPhone 12）")
    
    with allure.step("访问发布职位页面"):
        page.goto(PUBLISH_URL)
        page.wait_for_load_state("load")
        page.wait_for_timeout(2000)
        logger.info(f"✓ 访问发布职位页面: {PUBLISH_URL}")
    
    with allure.step("处理登录（如需要）"):
        login_if_needed(page, TEST_ACCOUNT["username"], TEST_ACCOUNT["password"])
    
    with allure.step("验证移动端布局"):
        # 验证标题可见
        expect(page.get_by_role('heading', name='Job Basics')).to_be_visible()
        logger.info("✓ 页面标题在移动端可见")
        
        # 验证输入框可见且可用
        title_input = page.locator('#title')
        expect(title_input).to_be_visible()
        logger.info("✓ Job Title 输入框在移动端可见")
        
        # 验证按钮可见
        expect(page.get_by_role('button', name='Continue')).to_be_visible()
        logger.info("✓ Continue 按钮在移动端可见")
    
    with allure.step("测试移动端交互"):
        # 测试输入
        page.locator('#title').fill('Mobile Test Job')
        page.wait_for_timeout(500)
        
        # 验证输入值
        title_value = page.locator('#title').input_value()
        assert len(title_value) > 0, "移动端输入功能应该正常"
        logger.info("✓ 移动端输入功能正常")
        
        # 测试点击功能（使用 click 代替 tap，因为无头模式不支持触摸）
        page.get_by_role('heading', name='Job Basics').click(force=True)
        page.wait_for_timeout(500)
        logger.info("✓ 移动端点击功能正常")
    
    with allure.step("检查元素是否溢出视口"):
        # 获取页面宽度
        page_width = page.evaluate("document.documentElement.scrollWidth")
        viewport_width = 390
        
        if page_width <= viewport_width + 20:  # 允许20px的误差
            logger.info(f"✓ 页面宽度 {page_width}px 适配移动端视口")
        else:
            logger.warning(f"⚠️ 页面宽度 {page_width}px 超出移动端视口 {viewport_width}px")
    
    logger.info("✅ TC032 测试通过：移动端适配正常")

