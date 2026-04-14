"""
详情页图片区域 Page Object

封装详情页图片展示和大图预览（lightbox）的元素定位和交互方法
"""
import logging
from playwright.sync_api import Page, Locator, expect

logger = logging.getLogger(__name__)


class DetailPageImageGallery:
    """详情页图片区域"""

    def __init__(self, page: Page):
        self.page = page

    # ========== 详情页图片区域定位器 ==========

    @property
    def gallery_container(self) -> Locator:
        """图片容器区域"""
        return self.page.locator("div").filter(has=self.page.locator("img[alt*='65'][class*='']").first)

    def thumbnail(self, index: int = 0) -> Locator:
        """缩略图（支持索引）"""
        return self.page.locator("img[alt*='65']").nth(index)

    @property
    def all_thumbnails(self) -> Locator:
        """所有缩略图"""
        return self.page.locator("img[alt*='65']")

    @property
    def single_image(self) -> Locator:
        """单图模式的主图"""
        return self.page.locator("img[alt*='65']").first

    @property
    def image_count_badge(self) -> Locator:
        """图片数量徽章（多图模式）"""
        return self.page.locator("generic:has-text('7')")

    # ========== 大图模式（Lightbox）定位器 ==========

    @property
    def lightbox_dialog(self) -> Locator:
        """大图弹窗"""
        return self.page.locator("[role='dialog']")

    @property
    def lightbox_image(self) -> Locator:
        """大图主图"""
        return self.lightbox_dialog.locator("img[alt*='65']").first

    @property
    def lightbox_close_button(self) -> Locator:
        """大图关闭按钮"""
        return self.lightbox_dialog.locator("img[alt='close-icon']")

    @property
    def lightbox_prev_button(self) -> Locator:
        """大图上一张按钮"""
        return self.lightbox_dialog.get_by_role("button", name="prev")

    @property
    def lightbox_next_button(self) -> Locator:
        """大图下一张按钮"""
        return self.lightbox_dialog.get_by_role("button", name="next")

    @property
    def lightbox_counter(self) -> Locator:
        """大图计数器（如 "1/7"）"""
        # 更精确的定位：dialog 内包含 "/" 的文本节点
        return self.lightbox_dialog.locator("text=/\\d+\\/\\d+/")

    @property
    def lightbox_thumbnails(self) -> Locator:
        """大图模式缩略图区域的所有缩略图"""
        # 大图dialog内的所有缩略图（在第2个generic容器中）
        # 从MCP录制看到，缩略图在 generic [ref=e239] 下
        # 更通用的定位：dialog内所有img元素去除第一个（第一个是主图）
        return self.lightbox_dialog.locator("img[alt*='65']")

    def lightbox_thumbnail(self, index: int) -> Locator:
        """大图模式指定缩略图"""
        return self.lightbox_thumbnails.nth(index)

    # ========== 交互方法 ==========

    def wait_page_load(self, timeout: int = 15000):
        """等待详情页加载完成"""
        logger.info("[DEBUG] 等待详情页加载完成...")
        self.page.wait_for_load_state("networkidle", timeout=timeout)
        self.page.wait_for_timeout(2000)
        logger.info("[DEBUG] 详情页加载完成")

    def click_thumbnail(self, index: int = 0):
        """点击缩略图"""
        logger.info(f"[DEBUG] 点击第 {index + 1} 张缩略图")
        self.thumbnail(index).click()
        self.page.wait_for_timeout(500)

    def open_lightbox(self, index: int = 0):
        """点击缩略图打开大图模式"""
        logger.info(f"[DEBUG] 点击第 {index + 1} 张缩略图打开大图")
        self.thumbnail(index).click()
        self.wait_lightbox_open()

    def wait_lightbox_open(self, timeout: int = 5000):
        """等待大图弹窗打开"""
        logger.info("[DEBUG] 等待大图弹窗打开...")
        self.lightbox_dialog.wait_for(state="visible", timeout=timeout)
        self.page.wait_for_timeout(500)
        logger.info("[DEBUG] 大图弹窗已打开")

    def close_lightbox(self):
        """关闭大图弹窗"""
        logger.info("[DEBUG] 点击关闭按钮关闭大图")
        self.lightbox_close_button.click()
        self.wait_lightbox_closed()

    def wait_lightbox_closed(self, timeout: int = 5000):
        """等待大图弹窗关闭"""
        logger.info("[DEBUG] 等待大图弹窗关闭...")
        self.lightbox_dialog.wait_for(state="hidden", timeout=timeout)
        logger.info("[DEBUG] 大图弹窗已关闭")

    def click_lightbox_next(self):
        """点击大图下一张按钮"""
        logger.info("[DEBUG] 点击大图下一张按钮")
        self.lightbox_next_button.click()
        self.page.wait_for_timeout(300)

    def click_lightbox_prev(self):
        """点击大图上一张按钮"""
        logger.info("[DEBUG] 点击大图上一张按钮")
        self.lightbox_prev_button.click()
        self.page.wait_for_timeout(300)

    def click_lightbox_thumbnail(self, index: int):
        """点击大图模式缩略图"""
        logger.info(f"[DEBUG] 点击大图模式第 {index + 1} 张缩略图")
        self.lightbox_thumbnail(index).click()
        self.page.wait_for_timeout(300)

    def get_current_lightbox_counter(self) -> str:
        """获取大图计数器文本（如 "1/7"）"""
        text = self.lightbox_counter.inner_text()
        logger.info(f"[DEBUG] 当前大图计数器: {text}")
        return text

    def get_thumbnail_count(self) -> int:
        """获取详情页缩略图数量"""
        count = self.all_thumbnails.count()
        logger.info(f"[DEBUG] 详情页缩略图数量: {count}")
        return count

    def get_lightbox_thumbnail_count(self) -> int:
        """获取大图模式缩略图数量"""
        count = self.lightbox_thumbnails.count()
        logger.info(f"[DEBUG] 大图模式缩略图数量: {count}")
        return count

    def is_single_image_mode(self) -> bool:
        """判断是否为单图模式"""
        try:
            count = self.get_thumbnail_count()
            is_single = count == 1
            logger.info(f"[DEBUG] 是否为单图模式: {is_single}")
            return is_single
        except Exception as e:
            logger.error(f"[ERROR] 判断单图模式失败: {e}")
            return False

    def is_lightbox_open(self) -> bool:
        """判断大图弹窗是否打开"""
        is_visible = self.lightbox_dialog.is_visible()
        logger.info(f"[DEBUG] 大图弹窗是否可见: {is_visible}")
        return is_visible

    def has_lightbox_nav_buttons(self) -> bool:
        """判断大图是否有翻页按钮"""
        try:
            has_prev = self.lightbox_prev_button.is_visible()
            has_next = self.lightbox_next_button.is_visible()
            result = has_prev and has_next
            logger.info(f"[DEBUG] 大图是否有翻页按钮: {result}")
            return result
        except Exception:
            return False
