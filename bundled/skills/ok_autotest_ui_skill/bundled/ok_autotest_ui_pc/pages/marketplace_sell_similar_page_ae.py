# pages/marketplace_sell_similar_page_ae.py
from pages.base_page import BasePage
from utils.logger import setup_logger


class MarketplaceSellSimilarPageAe(BasePage):
    """AE站 Marketplace Sell Similar 功能页面对象"""

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    def is_sell_similar_button_visible(self, timeout=5000):
        """
        检查 Sell Similar 按钮是否可见
        录制选择器: page.getByText('Sell Similar')
        """
        try:
            # 先等待页面完全加载
            self.page.wait_for_timeout(1000)
            
            # 尝试多种定位方式
            # 方式1: 精确文本匹配
            try:
                locator = self.page.get_by_text("Sell Similar", exact=True)
                count = locator.count()
                self.logger.info(f"[DEBUG] get_by_text 精确匹配找到 {count} 个元素")
                if count > 0:
                    sell_btn = locator.first
                    sell_btn.scroll_into_view_if_needed(timeout=2000)
                    self.page.wait_for_timeout(500)
                    if sell_btn.is_visible(timeout=2000):
                        self.logger.info("[DEBUG] 方式1成功: 精确文本匹配")
                        return True
            except Exception as e:
                self.logger.warning(f"[DEBUG] 方式1失败: {e}")
            
            # 方式2: 包含文本匹配
            try:
                locator = self.page.locator("text=Sell Similar")
                count = locator.count()
                self.logger.info(f"[DEBUG] locator text= 找到 {count} 个元素")
                if count > 0:
                    sell_btn = locator.first
                    sell_btn.scroll_into_view_if_needed(timeout=2000)
                    self.page.wait_for_timeout(500)
                    if sell_btn.is_visible(timeout=2000):
                        self.logger.info("[DEBUG] 方式2成功: 包含文本匹配")
                        return True
            except Exception as e:
                self.logger.warning(f"[DEBUG] 方式2失败: {e}")
            
            # 方式3: 通过 generic 容器定位 (从 snapshot 看到是 generic 元素)
            try:
                locator = self.page.locator("div, span, a").filter(has_text="Sell Similar")
                count = locator.count()
                self.logger.info(f"[DEBUG] 通用容器 filter 找到 {count} 个元素")
                if count > 0:
                    # 遍历找到可见的那个
                    for i in range(count):
                        sell_btn = locator.nth(i)
                        try:
                            sell_btn.scroll_into_view_if_needed(timeout=2000)
                            self.page.wait_for_timeout(300)
                            if sell_btn.is_visible(timeout=2000):
                                self.logger.info(f"[DEBUG] 方式3成功: 第 {i} 个元素可见")
                                return True
                        except Exception:
                            continue
            except Exception as e:
                self.logger.warning(f"[DEBUG] 方式3失败: {e}")
            
            self.logger.error("[DEBUG] 所有定位方式都失败,按钮不可见")
            return False
        except Exception as e:
            self.logger.error(f"检查 Sell Similar 按钮可见性失败: {e}")
            return False

    def click_sell_similar_button(self):
        """
        点击 Sell Similar 按钮
        录制选择器: page.getByText('Sell Similar').click()
        """
        try:
            self.page.wait_for_timeout(1000)
            
            # 尝试多种定位方式
            clicked = False
            
            # 方式1: 精确文本匹配
            try:
                sell_btn = self.page.get_by_text("Sell Similar", exact=True).first
                if sell_btn.count() > 0:
                    sell_btn.scroll_into_view_if_needed(timeout=2000)
                    self.page.wait_for_timeout(500)
                    sell_btn.click()
                    clicked = True
            except Exception:
                pass
            
            if not clicked:
                # 方式2: 包含文本匹配
                try:
                    sell_btn = self.page.locator("text=Sell Similar").first
                    sell_btn.scroll_into_view_if_needed(timeout=2000)
                    self.page.wait_for_timeout(500)
                    sell_btn.click()
                    clicked = True
                except Exception:
                    pass
            
            if not clicked:
                # 方式3: 通过父容器定位
                sell_btn = self.page.locator("[class*='action'], [class*='button']").filter(has_text="Sell Similar").first
                sell_btn.scroll_into_view_if_needed(timeout=2000)
                self.page.wait_for_timeout(500)
                sell_btn.click()
            
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击 Sell Similar 按钮失败: {e}")
            raise

    def is_publish_page_loaded(self, timeout=10000):
        """
        检查是否成功进入发布页
        验证 URL 包含 /publish/ 或 /biz/en/publish/
        """
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
            url = self.page.url.lower()
            return "/publish/" in url or "post" in self.page.title().lower()
        except Exception:
            return False

    def get_current_url(self):
        """获取当前页面 URL"""
        try:
            return self.page.url
        except Exception as e:
            self.logger.error(f"获取当前 URL 失败: {e}")
            return ""
    
    # ========== 发布页预加载内容验证 ==========
    
    def get_publish_page_category(self, timeout=5000):
        """
        获取发布页的类目信息
        用于验证类目是否继承原帖
        """
        try:
            # 等待类目选择器出现
            category_selector = self.page.locator("[class*='category'], [class*='Category']").first
            category_selector.wait_for(state="visible", timeout=timeout)
            return category_selector.inner_text()
        except Exception as e:
            self.logger.error(f"获取发布页类目失败: {e}")
            return ""
    
    def get_publish_page_price(self, timeout=5000):
        """
        获取发布页的价格信息
        用于验证价格是否继承原帖
        """
        try:
            # 查找价格输入框
            price_input = self.page.locator("input[type='number'], input[name*='price'], input[placeholder*='price' i]").first
            price_input.wait_for(state="visible", timeout=timeout)
            return price_input.input_value()
        except Exception as e:
            self.logger.error(f"获取发布页价格失败: {e}")
            return ""
    
    def get_publish_page_images_count(self, timeout=5000):
        """
        获取发布页已上传的图片数量
        用于验证图片是否被清空
        """
        try:
            # 查找图片预览容器
            images = self.page.locator("[class*='image'], [class*='photo'], img[src*='blob:'], img[src*='data:']").all()
            return len(images)
        except Exception as e:
            self.logger.error(f"获取发布页图片数量失败: {e}")
            return 0
    
    def is_image_upload_area_empty(self, timeout=5000):
        """
        验证图片上传区域是否为空
        用于验证 Sell Similar 后图片被清空
        """
        try:
            # 查找上传按钮或空状态提示
            upload_button = self.page.locator("button:has-text('Upload'), button:has-text('Add'), [class*='upload']").first
            return upload_button.is_visible(timeout=timeout)
        except Exception:
            return False
    
    def get_publish_page_title(self, timeout=5000):
        """
        获取发布页的标题输入框内容
        用于验证标题是否继承原帖
        """
        try:
            title_input = self.page.locator("input[name*='title'], textarea[name*='title'], input[placeholder*='title' i]").first
            title_input.wait_for(state="visible", timeout=timeout)
            return title_input.input_value()
        except Exception as e:
            self.logger.error(f"获取发布页标题失败: {e}")
            return ""
    
    def get_publish_page_description(self, timeout=5000):
        """
        获取发布页的描述内容
        用于验证描述是否继承原帖
        """
        try:
            desc_input = self.page.locator("textarea[name*='description'], textarea[name*='content'], [class*='description']").first
            desc_input.wait_for(state="visible", timeout=timeout)
            return desc_input.input_value()
        except Exception as e:
            self.logger.error(f"获取发布页描述失败: {e}")
            return ""
