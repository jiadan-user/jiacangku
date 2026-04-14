# pages/vidflow_login_page.py
"""
Vidflow 登录页封装
用于 vidflow.ok.com 登录流程，若需 58 盾请人工处理或后续 MCP 录制补全。
"""
from pages.base_page import BasePage
from utils.logger import setup_logger


class VidflowLoginPage(BasePage):
    """Vidflow 登录页面对象（静默执行）"""

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    def navigate_to_home_page(self, base_url):
        """打开 Vidflow 首页"""
        try:
            self.page.goto(base_url, wait_until="domcontentloaded", timeout=60000)
            self.page.wait_for_load_state("load")
        except Exception as e:
            self.logger.error(f"打开首页失败: {e}")
            raise

    def handle_cookie_popup(self):
        """处理 Cookie 弹窗（若存在）"""
        try:
            for text in ("Accept all", "接受全部", "同意", "我知道了"):
                btn = self.page.get_by_role("button", name=text).first
                if btn.is_visible(timeout=2000):
                    btn.click()
                    self.page.wait_for_timeout(1000)
                    return
        except Exception:
            pass

    def is_login_visible(self, timeout=5000):
        """是否显示登录入口（未登录态）"""
        try:
            return (
                self.page.get_by_text("登录").first.is_visible(timeout=timeout)
                or self.page.get_by_text("Log in").first.is_visible(timeout=0)
            )
        except Exception:
            return False

    def click_login_entry(self):
        """点击登录入口（文案以实测为准）"""
        try:
            for text in ("登录", "Log in", "登 录"):
                loc = self.page.get_by_text(text).first
                if loc.is_visible(timeout=2000):
                    loc.click()
                    self.page.wait_for_timeout(2000)
                    return
            self.page.get_by_role("button", name="登录").click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击登录入口失败: {e}")
            raise

    def input_email(self, email):
        """输入邮箱（选择器需实测确认）"""
        try:
            self.page.get_by_role("textbox", name="Email or phone number").fill(email)
            self.page.wait_for_timeout(1000)
        except Exception:
            try:
                self.page.locator('input[type="text"]').first.fill(email)
                self.page.wait_for_timeout(1000)
            except Exception as e:
                self.logger.error(f"输入邮箱失败: {e}")
                raise

    def input_password(self, password):
        """输入密码（选择器需实测确认）"""
        try:
            self.page.get_by_role("textbox", name="Enter password").fill(password)
            self.page.wait_for_timeout(1000)
        except Exception:
            try:
                self.page.locator('input[type="password"]').fill(password)
                self.page.wait_for_timeout(1000)
            except Exception as e:
                self.logger.error(f"输入密码失败: {e}")
                raise

    def click_continue(self):
        """点击继续（兼容 Continue / 继续 / Next 等）"""
        try:
            for name in ("Continue", "继续", "Next", "下一步"):
                btn = self.page.get_by_role("button", name=name).first
                if btn.is_visible(timeout=3000):
                    btn.click()
                    self.page.wait_for_timeout(2000)
                    return
            self.page.get_by_role("button", name="Continue").click(timeout=5000)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击 Continue/继续 失败: {e}")
            raise

    def click_submit_login(self):
        """点击登录提交（文案以实测为准）"""
        try:
            for name in ("Log in", "登录", "登 录", "确定"):
                btn = self.page.get_by_role("button", name=name).first
                if btn.is_visible(timeout=2000):
                    btn.click()
                    self.page.wait_for_timeout(3000)
                    return
        except Exception as e:
            self.logger.error(f"点击登录按钮失败: {e}")
            raise

    def is_logged_in(self, username_part=None, timeout=5000):
        """是否已登录（可传用户名部分用于校验）"""
        try:
            if username_part:
                return self.page.get_by_text(username_part).first.is_visible(timeout=timeout)
            return not self.is_login_visible(timeout=timeout)
        except Exception:
            return False
