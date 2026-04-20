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

    def click_favourites_button(self, force_click=False):
        """
        点击收藏按钮
        
        Args:
            force_click: 是否强制点击（绕过遮挡元素）。
                        访客场景不应使用force，以便正常触发登录弹窗。
                        登录场景可能需要force来绕过意外弹窗。
        """
        if force_click:
            # 先强制关闭任何可能存在的登录弹窗
            try:
                # 尝试多种方式关闭弹窗
                # 方法1: 按Escape键
                self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(300)
                
                # 方法2: 如果弹窗仍然存在，点击关闭按钮
                close_btn = self.page.locator("img[src*='close-black']")
                if close_btn.count() > 0 and close_btn.is_visible(timeout=500):
                    close_btn.first.click(timeout=1000)
                    self.page.wait_for_timeout(300)
                    logger.info("✓ 已关闭阻挡的登录弹窗")
            except Exception:
                pass
            
            # 使用 force=True 强制点击，即使有元素遮挡
            try:
                self.favourites_button.click(force=True, timeout=5000)
                logger.info("✓ 点击收藏按钮（强制）")
            except Exception as e:
                logger.warning(f"强制点击失败，尝试普通点击: {e}")
                # 如果强制点击失败，尝试普通点击
                self.favourites_button.click()
                logger.info("✓ 点击收藏按钮")
        else:
            # 普通点击，不强制，让登录弹窗正常触发
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
        """
        验证登录弹窗是否可见
        
        检测策略：
        1. 优先检测dialog[open]元素（最可靠）
        2. 备用：检测邮箱输入框是否在可见且包含"Email or phone"文字
        """
        try:
            # 方案1: 检测dialog[open]元素
            dialogs = self.page.locator("dialog[open]")
            if dialogs.count() > 0:
                for i in range(dialogs.count()):
                    try:
                        if dialogs.nth(i).is_visible(timeout=500):
                            # 确认这个dialog包含登录相关元素
                            email_in_dialog = dialogs.nth(i).locator("input[type='text'], input[type='email']")
                            if email_in_dialog.count() > 0:
                                return True
                    except:
                        continue
        except Exception:
            pass
        
        try:
            # 方案2: 检测邮箱输入框（但必须确保它在弹窗中）
            if self.email_input.count() > 0 and self.email_input.is_visible(timeout=1000):
                # 额外验证：确保Continue按钮也存在（登录弹窗的特征）
                if self.continue_button.count() > 0:
                    return True
        except Exception:
            pass
        
        return False

    def is_login_dialog_closed(self) -> bool:
        """验证登录弹窗是否已关闭（通过检测邮箱输入框不可见）"""
        try:
            # 检测邮箱输入框是否不可见
            return not self.email_input.is_visible(timeout=1000)
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
