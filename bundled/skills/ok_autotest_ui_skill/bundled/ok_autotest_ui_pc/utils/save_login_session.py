#!/usr/bin/env python3
"""
辅助脚本：手动登录并保存 Session
用于批量测试前预准备登录状态
"""
from playwright.sync_api import sync_playwright
from utils.session_manager import SessionManager
from utils.logger import setup_logger
import yaml

logger = setup_logger()

def save_us_login_session():
    """保存美国站登录 Session"""
    
    # 读取配置
    with open('config/config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    us_config = config['sites']['us']
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 有头模式便于观察
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        try:
            # 访问列表页
            list_url = "https://us.ok.com/en/city-washington1/cate/"
            page.goto(list_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2000)
            
            logger.info(f"已打开列表页: {list_url}")
            
            # 处理 Cookie 弹窗
            try:
                accept_btn = page.get_by_role("button", name="Accept all").first
                if accept_btn.is_visible(timeout=3000):
                    accept_btn.click()
                    page.wait_for_timeout(1000)
                    logger.info("已接受 Cookie")
            except Exception:
                pass
            
            # 点击登录按钮
            login_btn = page.get_by_text("Log in / Register").first
            login_btn.click()
            page.wait_for_timeout(3000)
            
            logger.info("已点击登录按钮，等待登录弹窗...")
            
            # 手动操作提示
            logger.info("=" * 80)
            logger.info("请在浏览器中手动完成以下操作：")
            logger.info("1. 在登录弹窗中输入邮箱: shenchang@58.com")
            logger.info("2. 点击 Continue 按钮")
            logger.info("3. 输入密码: 123456Tt")
            logger.info("4. 点击 Log in 按钮")
            logger.info("5. 等待登录完成后，按 Enter 键继续...")
            logger.info("=" * 80)
            
            input("按 Enter 键继续...")
            
            # 等待登录完成
            page.wait_for_timeout(3000)
            
            # 保存 Session
            session_manager = SessionManager(page, us_config['base_url'], session_name="us_logged_in")
            if session_manager.save_session():
                logger.info("✓ 登录 Session 已保存成功！")
                logger.info(f"Session 文件: {session_manager.session_file}")
            else:
                logger.error("✗ 保存 Session 失败")
            
        finally:
            browser.close()


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("开始保存美国站登录 Session")
    logger.info("=" * 80)
    save_us_login_session()
    logger.info("=" * 80)
    logger.info("完成！")
    logger.info("=" * 80)
