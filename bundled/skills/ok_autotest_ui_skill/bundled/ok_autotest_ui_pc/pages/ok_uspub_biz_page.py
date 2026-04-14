# pages/ok_uspub_biz_page.py
"""uspub.ok.com 业务子域通用页（收藏 / 发布 / 消息，MCP 录制）"""
import re

from pages.base_page import BasePage
from utils.logger import setup_logger


class OkUspubBizPage(BasePage):
    """Favorites / Post front / Messages 等 uspub 页面断言辅助"""

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    def wait_for_favorites_list_url(self, timeout: int = 60000):
        try:
            self.page.wait_for_url(
                "**/list/favorites**",
                timeout=timeout,
                wait_until="domcontentloaded",
            )
        except Exception as e:
            self.logger.error(f"等待收藏列表 URL 失败: {e}")
            raise

    def wait_for_publish_front_url(self, timeout: int = 90000):
        try:
            self.page.wait_for_url(
                re.compile(r"https?://[^/]*uspub\.ok\.com/.*/publish/.*front"),
                timeout=timeout,
                wait_until="domcontentloaded",
            )
        except Exception as e:
            self.logger.error(f"等待发布前台 URL 失败: {e}")
            raise

    def wait_for_chat_url(self, timeout: int = 90000):
        try:
            self.page.wait_for_url(
                re.compile(r"https?://[^/]*uspub\.ok\.com/.*/chat"),
                timeout=timeout,
                wait_until="domcontentloaded",
            )
        except Exception as e:
            self.logger.error(f"等待消息中心 URL 失败: {e}")
            raise

    def favorites_empty_copy_visible(self, timeout: int = 15000) -> bool:
        try:
            t = "You currently haven't collected any content yet"
            self.page.get_by_text(t).first.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def publish_front_category_visible(self, timeout: int = 25000) -> bool:
        try:
            ph = self.page.locator(
                'input[placeholder*="Search for category"], input[placeholder*="category"]'
            ).first
            ph.wait_for(state="visible", timeout=timeout)
            for name in (
                "Marketplace",
                "Jobs",
                "Property",
                "Cars",
                "Services",
                "Community",
            ):
                self.page.get_by_text(name, exact=True).first.wait_for(
                    state="visible", timeout=timeout
                )
            return True
        except Exception:
            return False

    def messages_promo_copy_visible(self, timeout: int = 15000) -> bool:
        try:
            self.page.get_by_text("Install OK.com").first.wait_for(
                state="visible", timeout=timeout
            )
            self.page.get_by_text("Stay updated with your messages and listings").first.wait_for(
                state="visible", timeout=timeout
            )
            self.page.get_by_text("Get").first.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False
