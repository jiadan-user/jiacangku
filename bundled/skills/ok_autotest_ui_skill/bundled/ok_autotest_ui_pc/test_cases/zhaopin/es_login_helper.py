"""
ES站登录辅助模块
封装ES站（西班牙站）的登录逻辑，确保测试用例的登录前置条件满足

功能:
  - ensure_es_logged_in(): 确保已登录ES站（支持Session复用）
  - 自动处理Cookie弹窗
  - 使用SessionManager复用登录状态

使用方式:
  from test_cases.zhaopin.es_login_helper import ensure_es_logged_in
  
  def test_something(page, config):
      ensure_es_logged_in(page, config)
      # 现在已经登录，可以执行测试步骤
"""

from pages.login_page import LoginPage
from pages.es_home_page import EsHomePage
from utils.session_manager import SessionManager
from utils.logger import setup_logger

logger = setup_logger()


def ensure_es_logged_in(page, config):
    """
    确保已登录ES站（西班牙站）
    
    逻辑:
      1. 尝试加载已保存的Session（Cookies）
      2. 如果Session有效，直接返回
      3. 如果Session无效，执行完整登录流程
      4. 登录成功后保存Session供下次复用
    
    Args:
        page: Playwright Page对象
        config: 测试配置字典（包含base_url、test_account等）
    
    Raises:
        AssertionError: 如果登录失败
    """
    
    # ===== 初始化SessionManager =====
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    
    # ===== 尝试加载Session =====
    logger.info(f"尝试加载Session: {session_name}")
    if session_manager.load_session():
        # ===== 验证Session是否有效 =====
        logger.info("Session加载成功，验证登录状态...")
        page.goto(f"{config['base_url']}/en/city-madrid2/")
        # 官方推荐：等待页面关键元素加载（用户菜单或登录按钮）
        # 使用 or_() 方法组合多个选择器
        page.locator("text=/OKerES_/").or_(page.get_by_text("Log in / Register")).first.wait_for(state="visible", timeout=10000)
        
        # 使用ES首页Page Object验证登录状态
        es_home_page = EsHomePage(page)
        if es_home_page.is_logged_in():
            logger.info("✓ Session有效，已登录ES站")
            return
        else:
            logger.warning("Session已过期，将执行登录流程")
    else:
        logger.info("未找到有效Session，将执行登录流程")
    
    # ===== 执行登录流程 =====
    logger.info("开始ES站登录流程...")
    login_page = LoginPage(page)
    
    # 步骤1：导航到ES站首页
    logger.info("导航到ES站首页...")
    login_page.navigate_to_home_page(base_url=config['base_url'])
    
    # 步骤2：处理Cookie弹窗
    logger.info("处理Cookie弹窗...")
    login_page.handle_cookie_popup()
    
    # 步骤3：点击登录按钮（官方推荐：等待元素可见而不是 networkidle）
    logger.info("点击Log in / Register按钮...")
    login_page.click_login_register_button()
    # 等待登录表单加载完成（等待邮箱输入框可见）
    page.wait_for_selector('input[type="text"], input[type="email"], [role="textbox"]', state='visible', timeout=10000)
    
    # 步骤4：填写用户名
    logger.info("填写用户名...")
    login_page.input_email(config['test_account']['username'])
    
    # 步骤5：点击Continue按钮
    logger.info("点击Continue按钮...")
    login_page.click_continue_button()
    page.wait_for_timeout(2000)
    
    # 步骤6：填写密码
    logger.info("填写密码...")
    login_page.input_password(config['test_account']['password'])
    
    # 步骤7：点击Login按钮提交
    logger.info("点击Login按钮提交...")
    login_page.click_login_button()
    # 官方推荐：等待登录后的用户菜单元素出现（表示登录成功并跳转）
    page.locator("text=/OKerES_/").wait_for(state="visible", timeout=15000)
    
    # ===== 验证登录结果 =====
    logger.info("验证登录状态...")
    es_home_page = EsHomePage(page)
    if not es_home_page.is_logged_in():
        # 最后一次尝试：等待更长时间
        page.wait_for_timeout(3000)
        if not es_home_page.is_logged_in():
            logger.error("登录失败！")
            raise AssertionError("ES站登录失败，未检测到登录成功标志")
    
    logger.info("✓ 登录成功！")
    
    # ===== 保存Session =====
    logger.info(f"保存Session: {session_name}")
    session_manager.save_session()
    logger.info("✓ Session已保存，下次测试将自动复用")
