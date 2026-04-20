# pages/ai_publish_marketplace_page.py
from pages.base_page import BasePage
from utils.logger import setup_logger


class AiPublishMarketplacePage(BasePage):
    """AI推荐 - Marketplace发布页面对象（静默执行）"""

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    # ========== 页面操作方法（静默执行）==========

    def click_marketplace_category(self):
        """点击Marketplace类目，进入Marketplace发布页面"""
        try:
            self.page.locator('span').filter(has_text='Marketplace').click()
            self.page.wait_for_timeout(1000)
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception as e:
            self.logger.error(f"点击Marketplace类目失败: {e}")
            raise

    def upload_single_image(self, image_path):
        """
        上传单张图片

        Args:
            image_path: 图片绝对路径
        """
        try:
            file_input = self.page.locator('input[type="file"]').first
            file_input.set_input_files(image_path)
            self.page.wait_for_timeout(3000)
        except Exception as e:
            self.logger.error(f"上传单张图片失败: {e}")
            raise

    def upload_multiple_images(self, image_paths):
        """
        上传多张图片

        Args:
            image_paths: 图片绝对路径列表
        """
        try:
            file_input = self.page.locator('input[type="file"]').first
            file_input.set_input_files(image_paths)
            self.page.wait_for_timeout(8000)  # 多张图片上传+AI分析需要更长时间
        except Exception as e:
            self.logger.error(f"上传多张图片失败: {e}")
            raise

    def input_title(self, title):
        """
        输入Title（通过id="title"的input元素）

        Args:
            title: Title内容
        """
        try:
            title_input = self.page.locator('input#title').first
            if not title_input.is_visible(timeout=3000):
                raise Exception("未找到input#title元素")
            title_input.click()
            self.page.wait_for_timeout(500)
            title_input.clear()
            title_input.fill(title)
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"输入Title失败: {e}")
            raise

    def click_title_outside(self):
        """
        点击Title字段外部触发失焦
        
        多种策略尝试：
        1. 点击 Description * 标签
        2. 点击 Description textarea
        3. 点击 Body 元素（兜底方案）
        """
        # 策略1: 尝试点击 Description * 文本
        try:
            desc_label = self.page.get_by_text("Description *").first
            if desc_label.is_visible(timeout=2000):
                desc_label.click()
                self.page.wait_for_timeout(1000)
                return
        except Exception:
            pass
        
        # 策略2: 尝试点击 Description 区域的 textarea
        try:
            desc_textarea = self.page.locator('textarea.limited-textarea-input').first
            if desc_textarea.is_visible(timeout=2000):
                desc_textarea.click()
                self.page.wait_for_timeout(1000)
                return
        except Exception:
            pass
        
        # 策略3: 尝试点击 Description 容器
        try:
            desc_container = self.page.locator('div').filter(has_text='Description').first
            if desc_container.is_visible(timeout=2000):
                desc_container.click()
                self.page.wait_for_timeout(1000)
                return
        except Exception:
            pass
        
        # 策略4: 兜底方案 - 直接触发 Title 输入框的 blur 事件
        try:
            self.page.evaluate("""
                const titleInput = document.querySelector('input#title') || 
                                 document.querySelector('input[placeholder*="Modern"]');
                if (titleInput) {
                    titleInput.blur();
                }
            """)
            self.page.wait_for_timeout(1000)
            self.logger.info("✓ 使用 blur 事件触发失焦")
            return
        except Exception as e:
            self.logger.warning(f"所有失焦策略均失败: {e}")
            # 不抛出异常，因为失焦操作可能不是必须的
            pass

    def click_write_with_ai(self):
        """点击 Write with AI 按钮"""
        try:
            self.page.get_by_role("button", name="Write with AI").click()
            self.page.wait_for_timeout(3000)
        except Exception as e:
            self.logger.error(f"点击Write with AI按钮失败: {e}")
            raise
    
    def is_write_with_ai_button_visible(self):
        """
        判断 Write with AI 按钮是否显示且可点击
        
        Returns:
            bool: True表示按钮可见且可点击，False表示不可见或不可点击
        """
        try:
            button = self.page.get_by_role("button", name="Write with AI")
            if button.count() > 0:
                return button.is_visible(timeout=1000) and button.is_enabled(timeout=1000)
            return False
        except Exception:
            return False

    def click_suggested_category_first(self):
        """点击第一个AI推荐类目"""
        try:
            # 先等待 Suggested Categories 区域出现
            self.page.wait_for_timeout(1000)
            # 定位 Suggested Categories 区域内的第一个可点击类目标签
            suggested_area = self.page.get_by_text("Suggested Categories").first
            # 取其父容器，再找第一个子 div/span
            first_category = suggested_area.locator('xpath=following-sibling::*').first
            if first_category.count() == 0:
                # 备选：找第一个含有推荐类目文本的可见按钮或标签
                first_category = self.page.locator('.suggest-category-item, [class*="suggest"], [class*="category-tag"]').first
            first_category.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击第一个推荐类目失败: {e}")
            raise

    def is_suggested_categories_displayed(self, timeout=3000):
        """
        检查 Suggested Categories 区域是否显示

        Returns:
            bool: 是否显示
        """
        try:
            return self.page.get_by_text("Suggested Categories").first.is_visible(timeout=timeout)
        except Exception:
            return False

    def get_suggested_categories_text(self):
        """
        获取所有推荐类目的文本（Marketplace商品类目关键词）

        Returns:
            list: 推荐类目文本列表
        """
        try:
            self.page.wait_for_timeout(2000)

            categories = []
            keywords = [
                'Electronics', 'Cell Phones', 'Computers', 'Laptops',
                'Tablets', 'Accessories', 'Clothing', 'Furniture',
                'Home', 'Sports', 'Books', 'Toys', 'Tools',
                'Automotive', 'Music', 'Cameras', 'Gaming'
            ]
            for keyword in keywords:
                try:
                    elements = self.page.get_by_text(keyword, exact=False)
                    count = elements.count()
                    for i in range(count):
                        try:
                            elem = elements.nth(i)
                            if elem.is_visible(timeout=500):
                                text = elem.inner_text().strip()
                                if len(text) < 100 and text not in categories and keyword.lower() in text.lower():
                                    categories.append(text)
                                    break
                        except Exception:
                            continue
                except Exception as e:
                    self.logger.error(f"查找关键词 {keyword} 失败: {e}")
                    continue

            return categories
        except Exception as e:
            self.logger.error(f"获取推荐类目文本失败: {e}")
            return []

    def get_upload_count(self):
        """
        获取已上传图片数量

        Returns:
            str: 上传计数（如 "1/9"）
        """
        try:
            upload_area = self.page.locator('div').filter(has_text='Pictures').first
            upload_text = upload_area.locator('div').filter(has_text='/9').first.inner_text()
            return upload_text.strip()
        except Exception as e:
            self.logger.error(f"获取上传计数失败: {e}")
            try:
                count_elem = self.page.locator('text=/9').first
                return count_elem.inner_text().strip()
            except Exception:
                return "0/9"

    def get_description_value(self):
        """
        获取Description字段的值，兼容 textarea 和 contenteditable 两种形态。

        Returns:
            str: Description内容
        """
        try:
            desc_textarea = self.page.locator('textarea#content').first
            if desc_textarea.count() > 0 and desc_textarea.is_visible(timeout=1000):
                val = desc_textarea.input_value()
                if val:
                    return val
        except Exception:
            pass

        try:
            desc_textarea = self.page.locator('textarea#description').first
            if desc_textarea.count() > 0 and desc_textarea.is_visible(timeout=1000):
                val = desc_textarea.input_value()
                if val:
                    return val
        except Exception:
            pass

        try:
            desc_textarea = self.page.locator('div').filter(has_text='Description *').locator('textarea').first
            if desc_textarea.count() > 0 and desc_textarea.is_visible(timeout=1000):
                val = desc_textarea.input_value()
                if val:
                    return val
        except Exception:
            pass

        try:
            desc_editable = self.page.locator('[contenteditable="true"]').first
            if desc_editable.count() > 0 and desc_editable.is_visible(timeout=1000):
                val = desc_editable.inner_text().strip()
                if val:
                    return val
        except Exception:
            pass

        try:
            desc_container = self.page.locator('div').filter(has_text='Description *').first
            editable = desc_container.locator('[contenteditable]').first
            if editable.count() > 0 and editable.is_visible(timeout=1000):
                val = editable.inner_text().strip()
                if val:
                    return val
        except Exception as e:
            self.logger.error(f"获取Description值失败: {e}")

        return ""

    def wait_for_ai_recommendations(self, timeout=3000):
        """
        等待 AI 推荐加载

        Args:
            timeout: 超时时间（毫秒），保留参数兼容性
        """
        try:
            self.page.wait_for_timeout(8000)
        except Exception as e:
            self.logger.error(f"等待 AI 推荐失败: {e}")
            raise

    def parse_upload_count(self, upload_count_str):
        """
        解析上传计数字符串为当前已上传数量。
        例如 "0/9" -> 0, "Upload 1/9" -> 1, "3/9" -> 3

        Args:
            upload_count_str: get_upload_count() 返回值

        Returns:
            int: 已上传图片数量，解析失败返回 0
        """
        try:
            if not upload_count_str:
                return 0
            import re
            match = re.search(r'(\d+)/9', upload_count_str)
            if match:
                return int(match.group(1))
            return 0
        except Exception:
            return 0

    def delete_one_uploaded_image(self):
        """
        删除一张已上传的图片（点击一个 pic-close 并确认弹窗）。

        Returns:
            bool: 是否成功删除一张
        """
        try:
            self.page.wait_for_timeout(500)
            pic_close_elements = self.page.locator('.pic-close')
            if pic_close_elements.count() == 0:
                return False
            first_close = pic_close_elements.first
            if not first_close.is_visible(timeout=1000):
                return False
            first_close.click()
            self.page.wait_for_timeout(500)
            try:
                ok_btn = self.page.get_by_role("button", name="Ok")
                if ok_btn.is_visible(timeout=1000):
                    ok_btn.click()
            except Exception:
                try:
                    self.page.locator('button:has-text("Ok")').first.click()
                except Exception:
                    pass
            self.page.wait_for_timeout(1500)
            return True
        except Exception as e:
            self.logger.error(f"删除单张图片失败: {e}")
            return False
