# -*- coding: utf-8 -*-
"""
发布职位测试 - 通用辅助函数模块
提供修复后的元素定位和操作函数
"""
from playwright.sync_api import Page
from utils.logger import setup_logger

logger = setup_logger()


def select_job_function(page: Page, primary: str, secondary: str = None) -> bool:
    """
    选择 Job Function (修复后的版本)
    
    Args:
        page: Playwright Page 对象
        primary: 一级分类名称（如 "Engineering"）
        secondary: 二级分类名称（如 "Systems Engineering"），可选
        
    Returns:
        bool: 是否选择成功
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
        
        logger.info(f"✓ 选择 Job Function: {primary} / {secondary if secondary else primary}")
        return True
        
    except Exception as e:
        logger.error(f"❌ 选择 Job Function 失败: {str(e)}")
        return False


def select_salary(page: Page, min_amount: str = None, max_amount: str = None) -> bool:
    """
    选择薪资范围 (修复后的版本)
    
    Args:
        page: Playwright Page 对象
        min_amount: 最小薪资金额（如 "50000"）
        max_amount: 最大薪资金额（如 "80000"）
        
    Returns:
        bool: 是否选择成功
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
                page.keyboard.press("Escape")
                page.wait_for_timeout(500)
                return False
        
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
                page.keyboard.press("Escape")
                page.wait_for_timeout(500)
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 选择薪资失败: {str(e)}")
        return False


def fill_job_title(page: Page, title: str) -> bool:
    """
    填写 Job Title
    
    Args:
        page: Playwright Page 对象
        title: 职位标题
        
    Returns:
        bool: 是否填写成功
    """
    try:
        page.locator('#title').fill(title)
        logger.info(f"✓ 填写 Job Title: {title}")
        
        # 关闭 autocomplete 浮层
        page.get_by_role('heading', name='Job Basics').click(force=True)
        page.wait_for_timeout(500)
        
        return True
    except Exception as e:
        logger.error(f"❌ 填写 Job Title 失败: {str(e)}")
        return False


def fill_job_description(page: Page, description: str) -> bool:
    """
    填写 Job Description
    
    Args:
        page: Playwright Page 对象
        description: 职位描述
        
    Returns:
        bool: 是否填写成功
    """
    try:
        page.locator('#content').fill(description)
        logger.info("✓ 填写 Job Description")
        return True
    except Exception as e:
        logger.error(f"❌ 填写 Job Description 失败: {str(e)}")
        return False
