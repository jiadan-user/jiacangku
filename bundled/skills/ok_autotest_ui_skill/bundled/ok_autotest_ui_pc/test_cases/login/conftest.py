# test_cases/login/conftest.py
"""登录模块退登逻辑 - 支持单浏览器连续执行"""

import pytest
from playwright.sync_api import Page
from pages.login_page import LoginPage
from utils.logger import setup_logger

logger = setup_logger()


@pytest.fixture(scope="module")
def login_page(page):
    """
    模块级登录页面对象
    所有测试用例共享同一个登录页面对象实例
    """
    return LoginPage(page)


def logout_if_needed(page: Page, need_logout: bool):
    """
    根据用例要求执行退登操作
    
    Args:
        page: Playwright Page 对象
        need_logout: 是否需要退登
    """
    if not need_logout:
        # 不需要退登，检查登录弹窗是否打开
        # 注意：登录弹窗没有关闭按钮，不支持overlay/ESC关闭
        # 由于测试用例会在下一个用例开始时重新导航页面，弹窗会自动清除
        # 因此这里不需要特殊处理
        try:
            # 检查弹窗是否可见
            welcome_text = page.get_by_text("Welcome to OK.com").first
            if welcome_text.is_visible(timeout=1000):
                logger.info("ℹ️ 登录弹窗仍然打开（产品无关闭按钮，下一用例导航时会自动清除）")
        except Exception:
            pass
        return
    
    # 需要退登
    try:
        # 1. 检查是否已登录（右上角是否有用户信息）
        user_icon = page.locator('.PcUserInfo_avatar__1XZhQ, [data-testid="user-avatar"]').first
        if not user_icon.is_visible(timeout=3000):
            logger.info("⚠️ 用户未登录，跳过退登")
            return
        
        # 2. Hover 到用户头像显示下拉菜单
        user_icon.hover()
        page.wait_for_timeout(1000)
        
        # 3. 点击下拉菜单中的 "Log Out" 按钮
        logout_btn = page.get_by_text("Log Out", exact=False).first
        if logout_btn.is_visible(timeout=2000):
            logout_btn.click()
            page.wait_for_timeout(2000)
            logger.info("✅ 退登成功")
            
            # 4. 验证退登是否成功（右上角应该显示"Log in / Register"）
            login_btn = page.get_by_text("Log in / Register", exact=False).first
            if login_btn.is_visible(timeout=3000):
                logger.info("✅ 退登验证通过：右上角显示「Log in / Register」")
            else:
                logger.warning("⚠️ 退登后未检测到登录按钮")
        else:
            logger.warning("⚠️ 未找到 Log Out 按钮")
            
    except Exception as e:
        logger.error(f"❌ 退登失败: {e}")
        # 截图以便调试
        try:
            page.screenshot(path="debug_logout_failed.png")
            logger.info("已保存退登失败截图: debug_logout_failed.png")
        except Exception:
            pass


@pytest.fixture
def cleanup_after_test(page: Page, request):
    """
    测试用例执行后的清理 fixture
    根据用例的 need_logout marker 决定是否退登
    """
    yield
    
    # 获取用例的 need_logout marker
    marker = request.node.get_closest_marker("need_logout")
    need_logout = marker is not None
    
    # 执行退登或关闭弹窗
    logout_if_needed(page, need_logout)
