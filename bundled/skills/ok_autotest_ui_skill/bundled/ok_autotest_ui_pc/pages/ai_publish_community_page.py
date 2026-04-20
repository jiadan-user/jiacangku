# pages/ai_publish_community_page.py
from pages.base_page import BasePage
from utils.logger import setup_logger


class AiPublishCommunityPage(BasePage):
    """AI推荐 - Community发布页面对象（静默执行）"""

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    # ========== 页面操作方法（静默执行）==========

    def click_community_category(self):
        """点击Community类目，进入Community发布页面"""
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            self.page.wait_for_timeout(2000)
            
            community_locator = self.page.locator('span').filter(has_text='Community')
            community_locator.wait_for(state="visible", timeout=10000)
            community_locator.click(timeout=10000)
            
            self.page.wait_for_timeout(1000)
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception as e:
            self.logger.error(f"点击Community类目失败: {e}")
            raise

    def upload_single_image(self, image_path):
        """
        上传单张图片

        Args:
            image_path: 图片绝对路径
        """
        try:
            file_input = self.page.locator('.upload-input').first
            file_input.wait_for(state="attached", timeout=10000)
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
            file_input = self.page.locator('.upload-input').first
            file_input.wait_for(state="attached", timeout=10000)
            file_input.set_input_files(image_paths)
            self.page.wait_for_timeout(8000)  # 多张图片上传+AI分析需要更长时间
        except Exception as e:
            self.logger.error(f"上传多张图片失败: {e}")
            raise

    def input_title(self, title):
        """
        输入Title

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

    def is_write_with_ai_generating(self):
        """
        判断 Write with AI 按钮是否处于生成中状态（disabled）
        
        Returns:
            bool: True表示正在生成中，False表示未生成
        """
        try:
            button = self.page.get_by_role("button", name="Write with AI")
            # 先检查按钮是否存在且可见
            if button.count() > 0:
                try:
                    # 检查按钮是否 disabled
                    return button.is_disabled(timeout=2000)
                except Exception:
                    # 如果检查 disabled 状态失败，可能是因为按钮不可见，认为正在生成中
                    return True
            else:
                # 按钮不存在，可能是页面状态异常，认为未在生成
                return False
        except Exception:
            return False

    def is_write_with_ai_button_visible(self):
        """
        判断 Write with AI 按钮是否显示且可点击
        
        Returns:
            bool: True表示按钮可见且可点击，False表示不可见或不可点击
        """
        try:
            button = self.page.get_by_role("button", name="Write with AI")
            if button.count() > 0:
                # 检查按钮是否可见且可点击（非disabled）
                return button.is_visible(timeout=1000) and button.is_enabled(timeout=1000)
            return False
        except Exception:
            return False

    def click_suggested_category_first(self):
        """点击第一个AI推荐类目"""
        try:
            self.page.wait_for_timeout(1000)
            first_item = self.page.locator('[class*="recommendCategoryItem"]').first
            if first_item.count() > 0 and first_item.is_visible(timeout=3000):
                first_item.click()
                self.page.wait_for_timeout(1000)
                return
            first_item = self.page.locator('[class*="lastPath"]').first
            if first_item.count() > 0 and first_item.is_visible(timeout=3000):
                first_item.click()
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
        获取所有推荐类目的文本，从 Suggested Categories 容器中直接提取类目项。
        类目项使用 class*=recommendCategoryItem 定位，取最后一级类目名（class*=lastPath）。

        Returns:
            list: 推荐类目文本列表
        """
        try:
            self.page.wait_for_timeout(2000)
            categories = []

            last_path_elems = self.page.locator('[class*="lastPath"]').all()
            for elem in last_path_elems:
                try:
                    if elem.is_visible(timeout=500):
                        text = elem.inner_text().strip()
                        if text and text not in categories:
                            categories.append(text)
                except Exception:
                    continue

            if categories:
                return categories

            category_items = self.page.locator('[class*="recommendCategoryItem"]').all()
            for item in category_items:
                try:
                    if item.is_visible(timeout=500):
                        text = item.inner_text().strip()
                        if text and len(text) < 100 and "More Categories" not in text and text not in categories:
                            categories.append(text)
                except Exception:
                    continue

            return categories
        except Exception as e:
            self.logger.error(f"获取推荐类目文本失败: {e}")
            return []

    def get_upload_count(self):
        """
        获取已上传图片数量

        Returns:
            str: 上传计数（如 "Upload 1/9"），class=photo 的div包含计数信息
        """
        try:
            count_elem = self.page.locator('.photo').first
            if count_elem.count() > 0 and count_elem.is_visible(timeout=2000):
                return count_elem.inner_text().strip()
        except Exception:
            pass

        try:
            import re
            all_divs = self.page.locator('div').all()
            for div in all_divs:
                try:
                    text = div.inner_text(timeout=200)
                    if re.search(r'\d+/9', text) and len(text) < 30:
                        return text.strip()
                except Exception:
                    continue
        except Exception as e:
            self.logger.error(f"获取上传计数失败: {e}")

        return "0/9"

    def get_description_value(self):
        """
        获取Description字段的值，Community页面 textarea id=content。

        Returns:
            str: Description内容
        """
        try:
            desc_textarea = self.page.locator('textarea#content').first
            if desc_textarea.count() > 0 and desc_textarea.is_visible(timeout=2000):
                val = desc_textarea.input_value()
                if val:
                    return val
        except Exception:
            pass

        try:
            desc_textarea = self.page.locator('textarea').first
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
