"""
OK.com 详情页收藏功能 Page Object
负责详情页 Favourites 按钮的定位和操作
"""
from playwright.sync_api import Page, Locator
import logging

logger = logging.getLogger(__name__)


class DetailPageFavourites:
    """详情页收藏功能 Page Object"""

    def __init__(self, page: Page):
        self.page = page

    # ==================== 元素定位器 ====================

    @property
    def favourites_button(self) -> Locator:
        """收藏按钮（图片下方，心形图标 + Favourites 文字）"""
        # 使用 exact=True 避免与 Toast "Added to favourites" 冲突
        return self.page.get_by_text("Favourites", exact=True)

    @property
    def login_dialog(self) -> Locator:
        """登录弹窗"""
        return self.page.locator("dialog[open]")

    @property
    def email_input(self) -> Locator:
        """登录弹窗 - 邮箱输入框"""
        return self.page.get_by_role("textbox", name="Email or phone number")

    @property
    def continue_button(self) -> Locator:
        """登录弹窗 - Continue 按钮（第一步）"""
        return self.page.get_by_role("button", name="Continue")

    @property
    def password_input(self) -> Locator:
        """登录弹窗 - 密码输入框"""
        return self.page.get_by_role("textbox", name="Enter password")

    @property
    def login_button(self) -> Locator:
        """登录弹窗 - Log in 按钮（第二步）"""
        return self.page.get_by_role("button", name="Log in")

    @property
    def dialog_close_button(self) -> Locator:
        """登录弹窗 - 右上角关闭按钮（X图标）"""
        return self.page.locator("img[src*='close-black']")

    @property
    def cookie_accept_button(self) -> Locator:
        """Cookie 同意按钮"""
        return self.page.get_by_role("button", name="Accept all")

    @property
    def favourites_toast(self) -> Locator:
        """收藏成功提示 Toast"""
        return self.page.get_by_text("Added to favourites")

    # ==================== 操作方法 ====================

    def handle_cookie_popup(self):
        """
        处理 Cookie 弹窗（如果存在）
        如果弹窗不存在，不会抛出异常
        """
        try:
            if self.cookie_accept_button.is_visible(timeout=3000):
                self.cookie_accept_button.click()
                self.page.wait_for_timeout(1000)
                logger.info("✓ Cookie 弹窗已关闭")
        except Exception:
            pass

    def click_favourites_button(self):
        """点击收藏按钮"""
        self.favourites_button.click()
        logger.info("✓ 点击收藏按钮")

    def close_login_dialog(self):
        """关闭登录弹窗（点击右上角X按钮）"""
        self.dialog_close_button.click()
        logger.info("✓ 点击登录弹窗关闭按钮")

    def login_in_dialog(self, email: str, password: str):
        """
        在登录弹窗中完成登录
        
        Args:
            email: 登录邮箱
            password: 登录密码
        """
        # 填写邮箱
        self.email_input.fill(email)
        logger.info(f"✓ 填写邮箱：{email}")

        # 点击 Continue
        self.continue_button.click()
        self.page.wait_for_timeout(1000)
        logger.info("✓ 点击 Continue 按钮")

        # 填写密码
        self.password_input.fill(password)
        logger.info("✓ 填写密码")

        # 处理 Cookie 弹窗（可能在密码输入后弹出）
        self.handle_cookie_popup()

        # 点击 Log in
        self.login_button.click()
        self.page.wait_for_timeout(2000)
        logger.info("✓ 点击 Log in 按钮")

    # ==================== 验证方法 ====================

    def is_favourites_button_visible(self) -> bool:
        """验证收藏按钮是否可见"""
        return self.favourites_button.is_visible()

    def is_login_dialog_visible(self) -> bool:
        """验证登录弹窗是否可见"""
        try:
            return self.login_dialog.is_visible(timeout=3000)
        except Exception:
            return False

    def is_login_dialog_closed(self) -> bool:
        """验证登录弹窗是否已关闭"""
        try:
            return not self.login_dialog.is_visible(timeout=2000)
        except Exception:
            return True

    def is_toast_visible(self) -> bool:
        """验证收藏成功 Toast 是否可见"""
        try:
            return self.favourites_toast.is_visible(timeout=5000)
        except Exception:
            return False

    def get_favourites_button_text(self) -> str:
        """获取收藏按钮文字"""
        return self.favourites_button.inner_text()

    def wait_for_toast_disappear(self):
        """等待 Toast 消失"""
        try:
            self.favourites_toast.wait_for(state="hidden", timeout=5000)
            logger.info("✓ Toast 提示已消失")
        except Exception:
            pass
