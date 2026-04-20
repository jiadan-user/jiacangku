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
        """图片容器区域（多图模式的MulPicture容器或单图的SiglePicture容器）"""
        # 优先查找多图容器，如果没有则查找单图容器
        mul_container = self.page.locator("[class*='MulPicture']").first
        if mul_container.count() > 0:
            return mul_container
        return self.page.locator("[class*='SiglePicture'], [class*='SinglePicture']").first

    def thumbnail(self, index: int = 0) -> Locator:
        """缩略图（支持索引）- 多图容器内的img"""
        return self.page.locator("[class*='MulPicture'] img").nth(index)

    @property
    def all_thumbnails(self) -> Locator:
        """所有缩略图 - 多图容器内的所有img"""
        return self.page.locator("[class*='MulPicture'] img")

    @property
    def single_image(self) -> Locator:
        """单图模式的主图 - 在SiglePicture容器中"""
        # 单图在SiglePicture或SinglePicture容器中（注意可能的拼写错误）
        return self.page.locator("[class*='SiglePicture'] img, [class*='SinglePicture'] img").first

    @property
    def image_count_badge(self) -> Locator:
        """图片数量徽章（多图模式）- 通常显示如"1/7"的文本"""
        return self.page.locator("text=/\\d+\\/\\d+/")

    # ========== 大图模式（Lightbox）定位器 ==========

    @property
    def lightbox_dialog(self) -> Locator:
        """大图弹窗"""
        return self.page.locator("[role='dialog']")

    @property
    def lightbox_image(self) -> Locator:
        """大图主图 - lightbox内的主要展示图片"""
        return self.lightbox_dialog.locator("img").first

    @property
    def lightbox_close_button(self) -> Locator:
        """大图关闭按钮"""
        return self.lightbox_dialog.locator("img[alt='close-icon'], button[aria-label*='close'], button[aria-label*='Close']")

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
        # lightbox内的缩略图容器中的img
        return self.lightbox_dialog.locator("[class*='thumb'] img, [class*='Thumb'] img")

    def lightbox_thumbnail(self, index: int) -> Locator:
        """大图模式指定缩略图"""
        return self.lightbox_thumbnails.nth(index)

    # ========== 交互方法 ==========

    def wait_page_load(self, timeout: int = 30000):
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
        """获取详情页缩略图数量（多图模式）或图片数量（单图模式）"""
        # 先尝试获取多图模式的缩略图
        mul_count = self.all_thumbnails.count()
        
        if mul_count > 0:
            logger.info(f"[DEBUG] 详情页缩略图数量（多图）: {mul_count}")
            return mul_count
        
        # 如果没有多图缩略图，检查是否有单图
        single_count = self.page.locator("[class*='SiglePicture'] img, [class*='SinglePicture'] img").count()
        
        if single_count > 0:
            logger.info(f"[DEBUG] 详情页图片数量（单图）: {single_count}")
            return single_count
        
        logger.info(f"[DEBUG] 详情页图片数量: 0")
        return 0

    def get_lightbox_thumbnail_count(self) -> int:
        """获取大图模式缩略图数量"""
        count = self.lightbox_thumbnails.count()
        logger.info(f"[DEBUG] 大图模式缩略图数量: {count}")
        return count

    def is_single_image_mode(self) -> bool:
        """判断是否为单图模式"""
        try:
            # 检查是否有MulPicture容器（多图）
            mul_count = self.all_thumbnails.count()
            if mul_count > 0:
                logger.info(f"[DEBUG] 是多图模式: {mul_count}张")
                return False
            
            # 检查是否有SiglePicture容器（单图）
            single_count = self.page.locator("[class*='SiglePicture'] img, [class*='SinglePicture'] img").count()
            is_single = single_count == 1
            
            logger.info(f"[DEBUG] 是否为单图模式: {is_single} (单图数量: {single_count})")
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
