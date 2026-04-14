"""
OK.com 详情页分享功能 Page Object
负责详情页 Share 按钮的定位和操作
"""
from playwright.sync_api import Page, Locator
from utils.logger import setup_logger


class DetailPageShare:
    """详情页分享功能 Page Object"""

    def __init__(self, page: Page):
        self.page = page
        self.logger = setup_logger()

    # ==================== 元素定位器 ====================

    @property
    def share_button(self) -> Locator:
        """分享按钮（图片下方，分享图标 + Share 文字）"""
        # 使用 exact=True 避免与其他文本冲突
        return self.page.get_by_text("Share", exact=True)

    @property
    def favourites_button(self) -> Locator:
        """收藏按钮（与 Share 相邻）"""
        return self.page.get_by_text("Favourites", exact=True)

    @property
    def sell_similar_button(self) -> Locator:
        """Sell Similar 按钮（与 Share 相邻）"""
        return self.page.get_by_text("Sell Similar", exact=True)

    @property
    def link_copied_toast(self) -> Locator:
        """链接已复制提示 Toast"""
        # Toast 可能有多种呈现方式，使用更宽松的匹配
        return self.page.locator("text='Link copied'").first

    @property
    def cookie_accept_button(self) -> Locator:
        """Cookie 同意按钮"""
        return self.page.get_by_role("button", name="Accept all")

    # ==================== 操作方法 ====================

    def navigate_to_detail_page(self, detail_url: str):
        """
        导航到详情页
        
        Args:
            detail_url: 详情页完整 URL
        """
        try:
            self.page.goto(detail_url, wait_until="domcontentloaded", timeout=30000)
            self.page.wait_for_load_state("load", timeout=30000)
        except Exception as e:
            self.logger.error(f"导航到详情页失败: {e}")
            raise

    def handle_cookie_popup(self):
        """
        处理 Cookie 弹窗（如果存在）
        如果弹窗不存在，不会抛出异常
        """
        try:
            if self.cookie_accept_button.is_visible(timeout=3000):
                self.cookie_accept_button.click()
                self.page.wait_for_timeout(1000)
        except Exception:
            pass

    def click_share_button(self):
        """点击分享按钮"""
        try:
            self.share_button.click()
        except Exception as e:
            self.logger.error(f"点击分享按钮失败: {e}")
            raise

    def is_share_button_visible(self, timeout: int = 5000) -> bool:
        """
        检查分享按钮是否可见
        
        Args:
            timeout: 超时时间（毫秒）
        
        Returns:
            bool: 分享按钮是否可见
        """
        try:
            return self.share_button.is_visible(timeout=timeout)
        except Exception:
            return False

    def is_toast_visible(self, timeout: int = 3000) -> bool:
        """
        检查 "Link copied" Toast 提示是否可见
        
        Args:
            timeout: 超时时间（毫秒）
        
        Returns:
            bool: Toast 是否可见
        """
        try:
            return self.link_copied_toast.is_visible(timeout=timeout)
        except Exception:
            return False

    def wait_for_toast_disappear(self, timeout: int = 5000):
        """
        等待 Toast 提示消失
        
        Args:
            timeout: 超时时间（毫秒）
        """
        try:
            self.link_copied_toast.wait_for(state="hidden", timeout=timeout)
        except Exception as e:
            self.logger.error(f"等待 Toast 消失超时: {e}")
            raise

    def get_current_url(self) -> str:
        """
        获取当前页面 URL
        
        Returns:
            str: 当前页面 URL
        """
        return self.page.url

    def get_clipboard_content(self) -> str:
        """
        获取剪贴板内容
        
        Returns:
            str: 剪贴板中的文本内容
        
        Note:
            在无头模式下，剪贴板 API 可能无法使用。
            此方法会尝试通过 CDP (Chrome DevTools Protocol) 读取剪贴板。
        """
        try:
            # 方法1: 使用 CDP 的剪贴板权限（Chromium only）
            # 授予剪贴板读取权限
            self.page.context.grant_permissions(["clipboard-read"])
            
            # 读取剪贴板内容
            clipboard_text = self.page.evaluate("async () => await navigator.clipboard.readText()")
            return clipboard_text
        except Exception as e:
            self.logger.error(f"读取剪贴板失败: {e}")
            # 尝试方法2: 使用CDP直接读取（需要 Chromium）
            try:
                cdp_session = self.page.context.new_cdp_session(self.page)
                result = cdp_session.send("Browser.grantPermissions", {
                    "permissions": ["clipboardReadWrite"],
                    "origin": self.page.url
                })
                clipboard_text = self.page.evaluate("async () => await navigator.clipboard.readText()")
                return clipboard_text
            except Exception:
                return ""

    def extract_url_path(self, url: str) -> str:
        """
        提取 URL 的 path 路径部分（不包含 query 参数）
        
        Args:
            url: 完整 URL
        
        Returns:
            str: URL 的 path 路径
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        except Exception as e:
            self.logger.error(f"解析 URL 失败: {e}")
            return url
