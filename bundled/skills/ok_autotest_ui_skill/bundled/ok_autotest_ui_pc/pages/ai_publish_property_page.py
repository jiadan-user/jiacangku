# pages/ai_publish_property_page.py
from pages.base_page import BasePage
from utils.logger import setup_logger


class AiPublishPropertyPage(BasePage):
    """AI推荐 - Property发布页面对象（静默执行）"""
    
    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()
    
    # ========== 页面操作方法（静默执行）==========
    
    def navigate_to_publish_front_and_click_property(self, base_url):
        """
        从发布首页点击 Property For Rent 进入发布页
        自动处理 beforeunload 确认对话框
        
        Args:
            base_url: 站点基础URL
        """
        try:
            # 提前注册对话框监听器，自动点击"离开"
            # 这里使用 once 确保只处理一次，避免影响后续测试
            def handle_dialog(dialog):
                self.logger.info(f"检测到对话框: {dialog.message}")
                dialog.accept()
            
            self.page.once("dialog", handle_dialog)
            
            # 导航到发布首页（这里可能触发 beforeunload 对话框）
            self.page.goto(f"{base_url}/biz/en/publish/front", timeout=30000, wait_until="domcontentloaded")
            self.page.wait_for_timeout(1000)
            
            # 点击 Property For Rent
            self.page.locator('span').filter(has_text='Property For Rent').click()
            self.page.wait_for_timeout(1000)
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception as e:
            self.logger.error(f"从首页进入Property For Rent失败: {e}")
            raise
    
    def click_property_category(self):
        """点击Property For Rent类目，进入Property发布页面"""
        try:
            self.page.locator('span').filter(has_text='Property For Rent').click()
            self.page.wait_for_timeout(1000)
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception as e:
            self.logger.error(f"点击Property For Rent类目失败: {e}")
            raise
    
    def upload_single_image(self, image_path):
        """
        上传单张图片
        
        Args:
            image_path: 图片绝对路径
        """
        try:
            # 直接设置文件到file input（更可靠的方法）
            file_input = self.page.locator('input[type="file"]').first
            file_input.set_input_files(image_path)
            self.page.wait_for_timeout(3000)  # 等待图片上传和AI分析
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
            # 直接设置文件到file input（更可靠的方法）
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
            # 直接通过id定位Title输入框
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
        """点击Title字段外部触发失焦（录制：getByText Description *）"""
        try:
            self.page.get_by_text("Description *").first.click()
            self.page.wait_for_timeout(3000)
        except Exception as e:
            self.logger.error(f"点击Title外部失败: {e}")
            raise
    
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
            # 点击Suggested Categories区域的第一个推荐类目
            first_category = self.page.locator('div').filter(has_text='Suggested Categories').locator('..').locator('div').nth(1)
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
        获取所有推荐类目的文本
        
        Returns:
            list: 推荐类目文本列表
        """
        try:
            # 等待推荐区域可见
            self.page.wait_for_timeout(2000)
            
            categories = []
            keywords = ['Villa', 'Apartment', 'Residential', 'Townhouse', 'Penthouse', 'Pent House', 'House']
            for keyword in keywords:
                try:
                    elements = self.page.get_by_text(keyword, exact=False)
                    count = elements.count()
                    for i in range(count):
                        try:
                            elem = elements.nth(i)
                            if elem.is_visible(timeout=500):
                                text = elem.inner_text().strip()
                                if len(text) < 100 and text not in categories and keyword in text:
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
            # 定位Upload计数显示（更精确的选择器）
            # 查找包含"Upload"和数字的文本
            upload_area = self.page.locator('div').filter(has_text='Pictures').first
            upload_text = upload_area.locator('div').filter(has_text='/9').first.inner_text()
            return upload_text.strip()
        except Exception as e:
            self.logger.error(f"获取上传计数失败: {e}")
            # 尝试备选方案：直接查找包含/9的文本
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
        # 优先尝试 textarea
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

        # 兜底：尝试 contenteditable div
        try:
            desc_editable = self.page.locator('[contenteditable="true"]').first
            if desc_editable.count() > 0 and desc_editable.is_visible(timeout=1000):
                val = desc_editable.inner_text().strip()
                if val:
                    return val
        except Exception:
            pass

        try:
            self.logger.debug("尝试通过 Description 标签附近查找内容区域")
            desc_container = self.page.locator('div').filter(has_text='Description *').first
            # 查找同级或子级的 contenteditable
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
            timeout: 超时时间（毫秒）
        """
        try:
            self.page.wait_for_timeout(8000)
        except Exception as e:
            self.logger.error(f"等待 AI 推荐失败: {e}")
            raise
    
    def delete_uploaded_image_by_index(self, index=0):
        """
        删除已上传的图片（通过索引）
        
        Args:
            index: 图片索引（0开始）
        """
        try:
            # 点击图片缩略图打开预览
            thumbnails = self.page.locator('button').filter(has_text='Main')
            if thumbnails.count() > 0:
                thumbnails.first.click()
                self.page.wait_for_timeout(1000)
                
                # 点击删除按钮
                self.page.get_by_role("img", name="delete").click()
                self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"删除图片失败: {e}")
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
    
    def cleanup_uploaded_images(self):
        """
        清理所有已上传的图片
        通过循环点击pic-close元素删除已上传的图片，并确认删除弹窗
        
        Returns:
            int: 删除的图片数量
        """
        try:
            delete_count = 0
            self.page.wait_for_timeout(1000)
            
            max_attempts = 10
            for attempt in range(max_attempts):
                try:
                    pic_close_elements = self.page.locator('.pic-close')
                    element_count = pic_close_elements.count()
                    
                    if element_count == 0:
                        break
                    
                    first_close = pic_close_elements.first
                    if first_close.is_visible(timeout=1000):
                        first_close.click()
                        self.page.wait_for_timeout(500)
                        
                        try:
                            ok_button = None
                            try:
                                ok_button = self.page.get_by_role("button", name="Ok")
                                if ok_button.is_visible(timeout=1000):
                                    ok_button.click()
                                else:
                                    ok_button = None
                            except Exception:
                                ok_button = None
                            
                            if not ok_button:
                                try:
                                    ok_button = self.page.locator('button:has-text("Ok")').first
                                    if ok_button.is_visible(timeout=1000):
                                        ok_button.click()
                                except Exception:
                                    pass
                        except Exception:
                            pass
                        
                        self.page.wait_for_timeout(1500)
                        delete_count += 1
                    else:
                        break
                except Exception:
                    break
            
            if delete_count > 0:
                self.page.wait_for_timeout(1500)
            return delete_count
        except Exception as e:
            self.logger.error(f"清理图片失败: {e}")
            return 0
