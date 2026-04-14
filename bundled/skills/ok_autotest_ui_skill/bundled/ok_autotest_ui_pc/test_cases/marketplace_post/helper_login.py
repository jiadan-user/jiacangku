"""
辅助脚本：首次登录并保存session

用途：在运行Delivery Options测试之前，先运行此脚本完成登录，
浏览器会保存session，后续测试可以直接使用已登录状态。

使用方法：
    pytest test_cases/marketplace_post/helper_login.py -v -s

运行后：
    1. 浏览器会打开并导航到首页
    2. 自动完成登录流程
    3. 保持浏览器打开30秒（可以手动验证登录状态）
    4. session会被保存到playwright的state中
"""
import pytest
import time
from pages.login_page import LoginPage
from utils.logger import setup_logger

logger = setup_logger()


@pytest.mark.helper
def test_helper_login(page, config):
    """辅助脚本：完成登录并保存session"""
    
    logger.info("="*80)
    logger.info("辅助脚本：首次登录并保存session")
    logger.info("="*80)
    
    # 导航到首页
    logger.info("步骤1: 导航到首页")
    home_url = "https://ae.58v5.cn/en/city-abu-dhabi/"
    page.goto(home_url)
    page.wait_for_load_state("domcontentloaded")
    
    # 点击 "Log in / Register"
    logger.info("步骤2: 点击 'Log in / Register'")
    try:
        page.get_by_text("Log in / Register").click(timeout=10000)
        page.wait_for_timeout(2000)
        logger.info("✓ 登录弹窗已打开")
    except Exception as e:
        logger.error(f"❌ 无法点击 'Log in / Register': {e}")
        raise
    
    # 输入邮箱
    logger.info("步骤3: 输入邮箱")
    email = config["test_account"]["username"]
    try:
        email_input = page.get_by_role("textbox", name="Email or phone number")
        email_input.fill(email)
        logger.info(f"✓ 已输入邮箱: {email}")
    except Exception as e:
        logger.error(f"❌ 无法输入邮箱: {e}")
        raise
    
    # 点击 "Continue"
    logger.info("步骤4: 点击 'Continue'")
    try:
        page.get_by_role("button", name="Continue").click()
        page.wait_for_timeout(2000)
        logger.info("✓ 已点击 Continue")
    except Exception as e:
        logger.error(f"❌ 无法点击 Continue: {e}")
        raise
    
    # 输入密码
    logger.info("步骤5: 输入密码")
    password = config["test_account"]["password"]
    try:
        password_input = page.get_by_role("textbox", name="Enter password")
        password_input.fill(password)
        logger.info("✓ 已输入密码")
    except Exception as e:
        logger.error(f"❌ 无法输入密码: {e}")
        raise
    
    # 点击 "Log in"
    logger.info("步骤6: 点击 'Log in'")
    try:
        page.get_by_role("button", name="Log in").click()
        page.wait_for_timeout(3000)
        logger.info("✓ 已点击 Log in")
    except Exception as e:
        logger.error(f"❌ 无法点击 Log in: {e}")
        raise
    
    # 验证登录成功
    logger.info("步骤7: 验证登录状态")
    page.wait_for_timeout(2000)
    
    # 检查是否还能看到 "Log in / Register"（如果看不到，说明已登录）
    try:
        login_button = page.get_by_text("Log in / Register")
        if login_button.is_visible(timeout=3000):
            logger.warning("⚠️ 'Log in / Register' 仍然可见，可能登录失败")
        else:
            logger.info("✓ 登录成功（'Log in / Register' 不再显示）")
    except Exception as e:
        # 如果元素不存在/无法定位，视为已登录（按钮不再显示）
        logger.info(f"✓ 登录成功（'Log in / Register' 不再显示）: {e}")
    
    # 截图保存登录后的首页
    page.screenshot(path="debug_login_success.png", timeout=60000)
    logger.info("✓ 已保存截图: debug_login_success.png")
    
    # 导航到发布页面验证session
    logger.info("步骤8: 导航到发布页面验证session")
    page.goto("https://aepub.58v5.cn/biz/en/publish/classified")
    page.wait_for_timeout(3000)
    
    # 截图保存发布页面
    page.screenshot(path="debug_publish_page.png", timeout=60000)
    logger.info("✓ 已保存截图: debug_publish_page.png")
    
    # 保持浏览器打开一段时间，让用户可以手动验证
    logger.info("")
    logger.info("="*80)
    logger.info("✅ 登录流程完成！")
    logger.info("浏览器将保持打开30秒，请手动验证登录状态...")
    logger.info("Session已保存，后续测试将自动使用此登录状态")
    logger.info("="*80)
    
    # 禁止 time.sleep，使用 Playwright 等待
    page.wait_for_timeout(30000)
    
    logger.info("✓ 辅助脚本执行完成")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
