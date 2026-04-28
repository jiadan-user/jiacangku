# pages/login_page.py
import re

from pages.base_page import BasePage
from utils.logger import setup_logger


class LoginPage(BasePage):
    """OK.com 登录页面对象（静默执行）"""
    
    def __init__(self, page, base_url=None):
        super().__init__(page)
        self.logger = setup_logger()
        self.base_url = base_url
    
    # ========== 页面操作方法（静默执行）==========
    
    def navigate_to_home_page(self, base_url=None):
        """
        导航到首页
        
        Args:
            base_url: 站点基础 URL，不传则使用构造器中的 default，再否则默认美国站
        """
        try:
            url = base_url or self.base_url or "https://us.58v5.cn"
            self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
            self.page.wait_for_load_state("load")
            try:
                self.page.wait_for_load_state("networkidle", timeout=20000)
            except Exception:
                pass
        except Exception as e:
            self.logger.error(f"打开首页失败: {e}")
            try:
                self.page.screenshot(path="debug_navigate_failed.png")
                self.logger.info("已保存失败截图: debug_navigate_failed.png")
            except Exception:
                pass
            raise
    
    def handle_cookie_popup(self):
        """
        处理 Cookie 弹窗（如果存在）
        如果弹窗不存在，不会抛出异常
        """
        try:
            for label in (
                "Accept all",
                "Accept All",
                "Accept all cookies",
                "I agree",
                "同意",
                "我知道了",
            ):
                btn = self.page.get_by_role("button", name=label).first
                if btn.is_visible(timeout=2000):
                    btn.click()
                    self.page.wait_for_timeout(1000)
                    return
            legacy = self.page.locator("button:has-text('Accept all')").first
            if legacy.is_visible(timeout=1500):
                legacy.click()
                self.page.wait_for_timeout(1000)
        except Exception:
            pass

    def _guest_login_entry_locator(self):
        """
        未登录态顶部入口（兼容文案、空格与节点类型差异）
        """
        p = self.page
        by_text = p.get_by_text(re.compile(r"Log\s*in\s*/\s*Register", re.I)).first
        by_link = p.get_by_role("link", name=re.compile(r"Log\s*in.*Register", re.I)).first
        by_button = p.get_by_role("button", name=re.compile(r"Log\s*in.*Register", re.I)).first
        by_sign = p.get_by_text(re.compile(r"Sign\s*in\s*/\s*Register", re.I)).first
        return by_text.or_(by_link).or_(by_button).or_(by_sign)

    def active_login_dialog(self):
        """
        当前登录流程弹窗定位器。
        站点普遍使用 ARIA role=dialog，未必实现为原生 <dialog open>。
        优先：含 Continue / Log in；备选：含 Welcome to OK.com 的首屏（避免首屏按钮文案差异）。
        """
        p = self.page
        with_cta = p.get_by_role("dialog").filter(
            has=p.get_by_role("button", name=re.compile(r"Continue|Log\s*in", re.I))
        ).first
        welcome = p.get_by_role("dialog").filter(
            has=p.get_by_text(re.compile(r"Welcome to OK\.com", re.I))
        ).first
        return with_cta.or_(welcome)

    def _wait_for_login_modal_visible(self, timeout=20000):
        """点击入口后等待登录层出现（ARIA dialog 优先，兼容原生 dialog[open]）。"""
        try:
            self.active_login_dialog().wait_for(state="visible", timeout=timeout)
            return
        except Exception:
            pass
        try:
            self.page.locator("dialog[open]").first.wait_for(
                state="visible", timeout=min(8000, timeout)
            )
            return
        except Exception:
            pass
        try:
            self.page.get_by_role("dialog").first.wait_for(
                state="visible", timeout=min(8000, timeout)
            )
            return
        except Exception:
            self.logger.warning(
                "登录弹窗未在预期时间内就绪（已尝试含 Continue/Log in 的 dialog、"
                "dialog[open]、任意 dialog）"
            )
            self.page.wait_for_timeout(2000)

    def click_login_register_button(self, timeout=30000):
        """点击登录/注册按钮，并等待登录弹窗出现"""
        try:
            entry = self._guest_login_entry_locator()
            entry.wait_for(state="visible", timeout=timeout)
            entry.scroll_into_view_if_needed(timeout=5000)
            entry.click(timeout=min(15000, timeout))
            self.page.wait_for_timeout(500)
            self._wait_for_login_modal_visible(timeout=min(20000, timeout))
        except Exception as e:
            self.logger.error(f"点击登录/注册按钮失败: {e}")
            raise
    
    def input_email(self, email):
        """
        输入邮箱或手机号
        
        Args:
            email: 邮箱或手机号
        """
        try:
            # 直接转换录制的 JavaScript 代码
            # await page.getByRole('textbox', { name: 'Email or phone number' }).fill('weijingjing02@58.com');
            self.page.get_by_role('textbox', name='Email or phone number').fill(email)
            # 等待输入完成后的客户端验证
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"输入邮箱失败: {e}")
            raise
    
    def input_email_in_dialog(self, email):
        """
        在登录弹窗中输入邮箱或手机号（适用于钱包页面自动弹出的登录对话框）
        
        Args:
            email: 邮箱或手机号
        """
        try:
            self.page.get_by_role('textbox', name='Email or phone number').fill(email)
            self.page.wait_for_timeout(1000)
            self.logger.info(f"✓ 在登录弹窗中输入邮箱: {email}")
        except Exception as e:
            self.logger.error(f"在登录弹窗中输入邮箱失败: {e}")
            raise
    
    def click_continue_button(self):
        """点击 Continue 按钮"""
        try:
            # 直接转换录制的 JavaScript 代码
            # await page.getByRole('button', { name: 'Continue' }).click();
            self.page.get_by_role('button', name='Continue').click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击 Continue 按钮失败: {e}")
            raise
    
    def input_password(self, password):
        """
        输入密码
        
        Args:
            password: 密码
        """
        try:
            # 直接转换录制的 JavaScript 代码
            # await page.getByRole('textbox', { name: 'Enter password' }).fill('Ok123456');
            self.page.get_by_role('textbox', name='Enter password').fill(password)
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"输入密码失败: {e}")
            raise
    
    def input_password_in_dialog(self, password):
        """
        在登录弹窗中输入密码（适用于钱包页面自动弹出的登录对话框）
        
        Args:
            password: 密码
        """
        try:
            self.page.get_by_role('textbox', name='Enter password').fill(password)
            self.page.wait_for_timeout(1000)
            self.logger.info("✓ 在登录弹窗中输入密码")
        except Exception as e:
            self.logger.error(f"在登录弹窗中输入密码失败: {e}")
            raise
    
    def click_login_button(self):
        """点击 Log in 按钮"""
        try:
            # 直接转换录制的 JavaScript 代码
            # await page.getByRole('button', { name: 'Log in' }).click();
            self.page.get_by_role('button', name='Log in').click()
            self.page.wait_for_timeout(3000)
        except Exception as e:
            self.logger.error(f"点击 Log in 按钮失败: {e}")
            raise
    
    def is_login_button_text_changed(self, timeout=5000):
        """
        判断登录按钮文本是否已改变（用于验证登录状态）
        登录前显示"Log in / Register"，登录后显示用户名
        
        Returns:
            bool: True表示已登录（按钮文本不再是"Log in / Register"）
        """
        try:
            login_button = self._guest_login_entry_locator()
            is_visible = login_button.is_visible(timeout=timeout)
            if not is_visible:
                self.logger.debug("✓ 登录入口已不可见,已登录")
                return True
            self.logger.debug("✗ 仍显示访客登录入口,未登录")
            return False
        except Exception as e:
            self.logger.debug(f"✓ 未找到访客登录入口,已登录: {e}")
            return True
    
    def login(self, email, password):
        """
        执行完整的登录流程（便捷方法）
        
        Args:
            email: 邮箱或手机号
            password: 密码
        """
        try:
            # 先处理 Cookie 弹窗
            self.handle_cookie_popup()
            self.click_login_register_button()
            self.input_email(email)
            self.click_continue_button()
            self.input_password(password)
            self.click_login_button()
        except Exception as e:
            self.logger.error(f"登录操作失败: {e}")
            raise
