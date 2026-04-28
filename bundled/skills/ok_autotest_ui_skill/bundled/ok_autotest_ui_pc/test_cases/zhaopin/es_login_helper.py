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

import os
import re

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
    try:
        u = (page.url or "").lower()
        if "chrome-error" in u or "chromewebdata" in u:
            logger.warning("检测到浏览器错误页，回退到 ES 首页以恢复: %s", page.url)
            page.goto(
                config["base_url"],
                wait_until="domcontentloaded",
                timeout=30000,
            )
    except Exception as e:
        logger.warning("错误页恢复尝试失败（忽略）: %s", e)

    # ===== 初始化SessionManager =====
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    
    # ===== 尝试加载Session =====
    logger.info(f"尝试加载Session: {session_name}")
    if session_manager.load_session():
        # ===== 验证Session是否有效 =====
        logger.info("Session加载成功，验证登录状态...")
        page.goto(
            f"{config['base_url']}/en/city-madrid2/",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        try:
            page.wait_for_load_state("networkidle", timeout=12000)
        except Exception:
            pass
        # 官方推荐：等待页面关键元素加载（用户菜单或登录按钮）
        # 使用 or_() 方法组合多个选择器
        page.locator("text=/OKerES_/").or_(page.get_by_text("Log in / Register")).first.wait_for(state="visible", timeout=25000)
        
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
    try:
        page.locator('input[type="password"]').first.wait_for(state="visible", timeout=15000)
    except Exception:
        pass

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
        try:
            page.get_by_text(re.compile(r"Log\s*in\s*/\s*Register", re.I)).first.wait_for(
                state="hidden", timeout=15000
            )
        except Exception:
            try:
                page.wait_for_function(
                    "() => !document.body || !/Log\\s*in\\s*\\/\\s*Register/i.test(document.body.innerText || '')",
                    timeout=10000,
                )
            except Exception:
                pass
        if not es_home_page.is_logged_in():
            logger.error("登录失败！")
            raise AssertionError("ES站登录失败，未检测到登录成功标志")
    
    logger.info("✓ 登录成功！")
    
    # ===== 保存Session =====
    logger.info(f"保存Session: {session_name}")
    session_manager.save_session()
    logger.info("✓ Session已保存，下次测试将自动复用")


def ensure_espub_resume_add_page(page, config, *, navigation_timeout_ms=None):
    """
    打开 espub 简历添加页 Step1。

    若账号已有简历，业务常将 /resume/add 重定向至 /resume，此时无法执行添加页用例，
    调用方应使用 pytest.skip 跳过（避免长时间等待不存在元素）。

    Args:
        navigation_timeout_ms: ``page.goto`` 超时（毫秒）。默认 28000，避免 60s 挂死；
            可通过环境变量 ``ES_RESUME_ADD_GOTO_TIMEOUT_MS`` 覆盖。
    """
    import pytest

    if navigation_timeout_ms is None:
        raw = os.environ.get("ES_RESUME_ADD_GOTO_TIMEOUT_MS", "").strip()
        navigation_timeout_ms = int(raw) if raw.isdigit() else 28000

    base = config.get("base_url", "https://es.58v5.cn")
    pub_url = base.replace("es.58v5.cn", "espub.58v5.cn/biz")
    target = f"{pub_url}/en/resume/add"
    for attempt in range(3):
        try:
            page.goto(
                target,
                wait_until="domcontentloaded",
                timeout=navigation_timeout_ms,
            )
        except Exception:
            page.wait_for_timeout(1200)
            continue
        u = page.url or ""
        if "chrome-error" in u or u.startswith("chrome://"):
            page.wait_for_timeout(1500)
            continue
        try:
            page.wait_for_load_state("domcontentloaded", timeout=8000)
        except Exception:
            pass
        try:
            page.locator("form, main, h1, h2").first.wait_for(state="visible", timeout=10000)
        except Exception:
            pass
        if "/resume/add" in page.url:
            break
        page.wait_for_timeout(800)
    if "/resume/add" not in page.url:
        pytest.skip(
            f"无法停留在 /resume/add（当前 {page.url}），账号可能已有简历；"
            "需无简历账号或清理简历数据后再跑本用例"
        )


def cleanup_es_resume_in_db(config=None):
    """
    删除当前 ES 联调账号在测试库中的简历相关行（与 test_es_resume_submit 清理顺序一致）。

    用于：同一 pytest 会话中先跑会提交简历的用例（见 test_es_resume_submit.py）后，后续仍依赖 /resume/add 的用例
    可在步骤前调用，避免被重定向到 /biz/en/resume 而 skip。

    Args:
        config: 可选；若含 ``test_user_id`` 则使用该值，否则使用默认 wangyongli@58.com 对应 id。
    """
    from utils.db_client import execute_update

    uid = "796567146451408960"
    if config and config.get("test_user_id"):
        uid = str(config["test_user_id"])
    for sql in (
        "DELETE FROM resume_work_experience WHERE user_id = %s",
        "DELETE FROM resume_education WHERE user_id = %s",
        "DELETE FROM resume_person_info WHERE user_id = %s",
        "DELETE FROM resume WHERE user_id = %s",
    ):
        execute_update(sql, (uid,))
    logger.info(f"✓ 已清理数据库简历数据 user_id={uid}")
