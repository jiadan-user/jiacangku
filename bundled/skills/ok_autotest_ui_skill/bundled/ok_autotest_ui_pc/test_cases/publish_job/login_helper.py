# test_cases/publish_job/login_helper.py
"""
登录辅助模块
处理发布职位页面的登录流程，包括 Cookie 弹窗和两步登录
"""
import time
from playwright.sync_api import Page, expect
from utils.logger import setup_logger

logger = setup_logger()


def login_if_needed(page: Page, username: str, password: str):
    """
    检查是否存在登录弹窗，如果存在则执行登录操作
    
    Args:
        page: Playwright Page 对象
        username: 登录邮箱
        password: 登录密码
    """
    try:
        # 首先尝试关闭可能出现的 Cookie Consent 弹窗
        try:
            cookie_consent_accept_button = page.locator('button:has-text("Accept all")')
            if cookie_consent_accept_button.is_visible(timeout=3000):
                cookie_consent_accept_button.click(force=True)
                logger.info("✓ 关闭 Cookie 弹窗")
                page.wait_for_timeout(1000)
        except Exception:
            pass  # Cookie 弹窗可能不存在，忽略
        
        # 检查登录弹窗是否可见
        login_dialog = page.locator('div[role="dialog"][aria-modal="true"]').filter(has_text="Welcome to OK.com")
        
        if login_dialog.is_visible(timeout=3000):
            logger.info("检测到登录弹窗，开始登录...")
            
            # 步骤1: 输入邮箱/手机号
            email_input = login_dialog.get_by_role('textbox', name='Email or phone number')
            email_input.fill(username)
            logger.info(f"✓ 填写邮箱: {username}")
            
            # 点击 Continue 按钮
            login_dialog.get_by_role('button', name='Continue').click(force=True)
            logger.info("✓ 点击 Continue 按钮")
            
            # 等待页面加载密码输入框（增加等待时间）
            page.wait_for_load_state("load")
            page.wait_for_timeout(5000)  # 增加到5秒
            
            # 步骤2: 输入密码（简化为直接使用最可靠的选择器）
            try:
                # 直接使用 input[type="password"]，这是最通用的选择器
                password_input = page.locator('input[type="password"]').first
                password_input.wait_for(state='visible', timeout=10000)
                password_input.fill(password)
                logger.info("✓ 填写密码")
                
                # 点击 Log in 按钮
                page.get_by_role('button', name='Log in').click(force=True)
                logger.info("✓ 点击登录按钮")
                
                # 等待登录弹窗消失
                login_dialog.wait_for(state="hidden", timeout=15000)
                logger.info("✓ 登录成功（弹窗已关闭）")
                
                # 等待页面稳定
                page.wait_for_load_state("load")
                page.wait_for_timeout(3000)
                
            except Exception as e:
                logger.error(f"密码输入或登录失败: {e}")
                # 尝试截图帮助调试
                try:
                    page.screenshot(path=f"reports/login_error_{int(time.time())}.png", timeout=60000)
                    logger.info("✓ 已保存登录错误截图")
                except:
                    pass
                raise
        else:
            logger.info("未检测到登录弹窗，可能已登录。")
    
    except Exception as e:
        logger.error(f"登录过程异常: {e}")
        # 如果登录失败，尝试刷新页面
        try:
            page.reload()
            page.wait_for_load_state("load")
            page.wait_for_timeout(2000)
        except Exception:
            pass

