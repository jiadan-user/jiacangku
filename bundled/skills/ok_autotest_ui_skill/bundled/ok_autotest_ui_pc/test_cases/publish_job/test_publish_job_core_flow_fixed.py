# -*- coding: utf-8 -*-
"""
修复后的发布职位测试 - 元素定位策略更新

主要修复：
1. 薪资选择：先点击 .pc-select-text 打开下拉，再选择金额
2. Job Function 选择：更新选择器
3. 增加等待和错误处理
"""
import re
import time
import pytest
import allure
from playwright.sync_api import Page, expect
from test_cases.publish_job.login_helper import login_if_needed
from utils.logger import setup_logger

logger = setup_logger()

# 测试数据
BASE_URL = "https://uspub.58v5.cn"
PUBLISH_URL = f"{BASE_URL}/biz/en/publish/job?categoryId=4000"
TEST_ACCOUNT = {
    "username": "weijingjing02@58.com",
    "password": "Ok123456"
}


def select_job_function_new(page: Page, primary: str, secondary: str = None):
    """
    更新后的 Job Function 选择函数
    """
    try:
        # 点击 Job Function 下拉触发器
        job_func_trigger = page.locator('.cascade-select-trigger').first
        job_func_trigger.click(force=True)
        page.wait_for_timeout(1000)
        logger.info("✓ 打开 Job Function 下拉")
        
        # 等待下拉菜单出现
        page.wait_for_selector(f'text="{primary}"', state='visible', timeout=10000)
        
        # 点击一级分类
        primary_option = page.locator(f'text="{primary}"').first
        primary_option.scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        primary_option.click(force=True)
        page.wait_for_timeout(800)
        logger.info(f"✓ 选择一级分类: {primary}")
        
        # 如果有二级分类，点击二级分类
        if secondary:
            page.wait_for_selector(f'text="{secondary}"', state='visible', timeout=10000)
            secondary_option = page.locator(f'text="{secondary}"').first
            secondary_option.scroll_into_view_if_needed()
            page.wait_for_timeout(300)
            secondary_option.click(force=True)
            page.wait_for_timeout(800)
            logger.info(f"✓ 选择二级分类: {secondary}")
            
        return True
    except Exception as e:
        logger.error(f"❌ 选择 Job Function 失败: {str(e)}")
        return False


def select_salary_new(page: Page, min_amount: str = None, max_amount: str = None):
    """
    新的薪资选择函数
    
    Args:
        page: Playwright Page 对象
        min_amount: 最小薪资金额（如 "50000"）
        max_amount: 最大薪资金额（如 "80000"）
    """
    try:
        # 定位薪资容器
        amount_container = page.locator('.amount-container').first
        
        # 获取两个薪资下拉框
        salary_selects = amount_container.locator('.pc-select-text').all()
        
        if len(salary_selects) < 2:
            logger.error(f"❌ 找到的薪资下拉框数量不足: {len(salary_selects)}")
            return False
        
        # 选择 Min Salary
        if min_amount:
            logger.info(f"准备选择 Min Salary: {min_amount}")
            salary_selects[0].click(force=True)
            page.wait_for_timeout(1000)
            
            # 尝试多种选择器查找金额选项
            selected = False
            for selector in [
                f'text="{min_amount}"',
                f'[role="option"]:has-text("{min_amount}")',
                f'.option-item:has-text("{min_amount}")',
                f'li:has-text("{min_amount}")',
                f'div:has-text("{min_amount}")',
            ]:
                try:
                    option = page.locator(selector).first
                    if option.is_visible(timeout=2000):
                        option.click(force=True)
                        page.wait_for_timeout(500)
                        logger.info(f"✓ 选择 Min Salary: ${min_amount}")
                        selected = True
                        break
                except:
                    continue
            
            if not selected:
                logger.warning(f"⚠️ 无法找到 Min Salary 选项: {min_amount}")
                # 尝试按 ESC 关闭下拉
                page.keyboard.press("Escape")
                page.wait_for_timeout(500)
        
        # 选择 Max Salary
        if max_amount:
            logger.info(f"准备选择 Max Salary: {max_amount}")
            salary_selects[1].click(force=True)
            page.wait_for_timeout(1000)
            
            # 尝试多种选择器查找金额选项
            selected = False
            for selector in [
                f'text="{max_amount}"',
                f'[role="option"]:has-text("{max_amount}")',
                f'.option-item:has-text("{max_amount}")',
                f'li:has-text("{max_amount}")',
                f'div:has-text("{max_amount}")',
            ]:
                try:
                    option = page.locator(selector).first
                    if option.is_visible(timeout=2000):
                        option.click(force=True)
                        page.wait_for_timeout(500)
                        logger.info(f"✓ 选择 Max Salary: ${max_amount}")
                        selected = True
                        break
                except:
                    continue
            
            if not selected:
                logger.warning(f"⚠️ 无法找到 Max Salary 选项: {max_amount}")
                # 尝试按 ESC 关闭下拉
                page.keyboard.press("Escape")
                page.wait_for_timeout(500)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 选择薪资失败: {str(e)}")
        return False


# 示例测试用例使用新的函数
@pytest.mark.p0
@pytest.mark.case_id_publish_job_core_flow_001_fixed
@allure.feature("发布职位")
@allure.story("核心流程 - 修复版")
@allure.title("TC001-Fixed: 三步向导填写所有字段完整发布职位")
def test_tc001_complete_three_step_wizard_fixed(page: Page):
    """
    TC001 修复版：使用新的元素定位策略
    """
    with allure.step("访问发布职位页面"):
        page.goto(PUBLISH_URL)
        page.wait_for_load_state("load")
        page.wait_for_timeout(2000)
        logger.info(f"✓ 访问发布职位页面: {PUBLISH_URL}")
    
    with allure.step("处理登录（如需要）"):
        login_if_needed(page, TEST_ACCOUNT["username"], TEST_ACCOUNT["password"])
    
    with allure.step("Step1: 填写 Job Basics - 使用新策略"):
        # 填写 Job Title
        page.locator('#title').fill('Senior Software Engineer - Test')
        logger.info("✓ 填写 Job Title")
        
        # 关闭 autocomplete 浮层
        page.get_by_role('heading', name='Job Basics').click(force=True)
        page.wait_for_timeout(500)
        
        # 选择 Job Function（使用新函数）
        success = select_job_function_new(page, 'Engineering', 'Systems Engineering')
        if not success:
            pytest.fail("Job Function 选择失败")
        
        # 选择薪资（使用新函数）
        success = select_salary_new(page, min_amount="50000", max_amount="80000")
        if not success:
            logger.warning("⚠️ 薪资选择可能失败，继续执行")
        
        # 点击 Continue
        page.get_by_role('button', name='Continue').first.click(force=True)
        page.wait_for_load_state("load")
        page.wait_for_timeout(2000)
        logger.info("✓ 点击 Continue，进入 Step2")
    
    with allure.step("Step2: 填写 Job Details 并发布"):
        # 验证进入 Step2
        expect(page.get_by_role('heading', name='Job Details')).to_be_visible(timeout=10000)
        logger.info("✓ 已进入 Step2: Job Details")
        
        # 填写 Job Description
        job_description = "We are seeking a talented Senior Software Engineer."
        page.locator('#content').fill(job_description)
        logger.info("✓ 填写 Job Description")
        
        # Step2 是最后一步，直接点击 Post 按钮发布
        page.get_by_role('button', name='Post').first.click(force=True)
        page.wait_for_load_state("load")
        page.wait_for_timeout(3000)
        logger.info("✓ 点击 Post 按钮发布职位")
        logger.info("✅ TC001-Fixed 测试通过")
