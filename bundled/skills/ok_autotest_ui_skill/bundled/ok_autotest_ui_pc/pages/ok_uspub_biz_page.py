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
            # 同时支持 uspub.ok.com 和 uspub.58v5.cn
            self.page.wait_for_url(
                re.compile(r"https?://[^/]*uspub\.(ok\.com|58v5\.cn)/.*/publish/.*front"),
                timeout=timeout,
                wait_until="domcontentloaded",
            )
        except Exception as e:
            self.logger.error(f"等待发布前台 URL 失败: {e}")
            raise

    def wait_for_chat_url(self, timeout: int = 90000):
        try:
            # 同时支持 uspub.ok.com 和 uspub.58v5.cn
            self.page.wait_for_url(
                re.compile(r"https?://[^/]*uspub\.(ok\.com|58v5\.cn)/.*/chat"),
                timeout=timeout,
                wait_until="domcontentloaded",
            )
        except Exception as e:
            self.logger.error(f"等待消息中心 URL 失败: {e}")
            raise

    def favorites_empty_copy_visible(self, timeout: int = 15000) -> bool:
        """
        检查收藏页空状态文案（兼容 ok.com 和 58v5.cn）
        """
        try:
            # 常见的空状态文案列表
            empty_texts = [
                "You currently haven't collected any content yet",  # ok.com
                "No favorites yet",
                "You don't have any favorites",
                "No favourites",
                "haven't collected",
                "no favorite",
                "Empty",
            ]
            
            # 尝试精确匹配
            for text in empty_texts:
                try:
                    elem = self.page.get_by_text(text, exact=False).first
                    elem.wait_for(state="visible", timeout=3000)
                    self.logger.info(f"✓ 找到空收藏文案: {text}")
                    return True
                except Exception:
                    continue
            
            # 尝试查找空状态容器（通常有特定class）
            empty_containers = [
                "div[class*='empty']",
                "div[class*='Empty']",
                "div[class*='noData']",
                "div[class*='no-data']",
            ]
            
            for selector in empty_containers:
                try:
                    container = self.page.locator(selector).first
                    if container.is_visible(timeout=2000):
                        content = container.text_content()
                        self.logger.info(f"✓ 找到空状态容器，内容: {content[:100]}")
                        return True
                except Exception:
                    continue
            
            # 最后检查页面中是否有图片 + 任何表示空的文本
            try:
                # 查找可能的空状态图片
                empty_img = self.page.locator("img[class*='empty'], img[alt*='empty'], img[src*='empty']").first
                if empty_img.is_visible(timeout=2000):
                    self.logger.info("✓ 找到空状态图片")
                    return True
            except Exception:
                pass
            
            self.logger.warning("未找到任何空收藏状态标识")
            return False
            
        except Exception as e:
            self.logger.error(f"检查空收藏文案失败: {e}")
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
