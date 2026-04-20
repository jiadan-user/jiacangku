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
        输入Title（多种定位策略）
        
        Args:
            title: Title内容
        """
        try:
            # 策略1: 通过id定位
            title_input = self.page.locator('input#title').first
            if title_input.count() > 0 and title_input.is_visible(timeout=2000):
                title_input.click()
                self.page.wait_for_timeout(500)
                title_input.clear()
                title_input.fill(title)
                self.page.wait_for_timeout(1000)
                return
        except Exception:
            pass
        
        try:
            # 策略2: 通过placeholder文本定位
            title_input = self.page.get_by_placeholder('e.g. Modern 2BR apartment near city center').first
            if title_input.count() > 0 and title_input.is_visible(timeout=2000):
                title_input.click()
                self.page.wait_for_timeout(500)
                title_input.clear()
                title_input.fill(title)
                self.page.wait_for_timeout(1000)
                return
        except Exception:
            pass
        
        try:
            # 策略3: 通过Label "Title" 关联的input
            title_label = self.page.locator('text=Title').first
            title_container = title_label.locator('..')
            title_input = title_container.locator('input[type="text"]').first
            if title_input.count() > 0 and title_input.is_visible(timeout=2000):
                title_input.click()
                self.page.wait_for_timeout(500)
                title_input.clear()
                title_input.fill(title)
                self.page.wait_for_timeout(1000)
                return
        except Exception:
            pass
        
        # 所有策略都失败
        self.logger.error("所有Title定位策略均失败")
        raise Exception("未找到Title输入框元素")
    
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
    
    def is_write_with_ai_button_visible(self) -> bool:
        """
        检查 Write with AI 按钮是否可见
        
        按照 ai-description-retry-pattern 规则实现：
        - 必须捕获所有异常
        - 超时返回 False，不抛出异常
        - 使用简短的超时（2秒）
        
        Returns:
            bool: True表示按钮可见，False表示不可见
        """
        try:
            button = self.page.get_by_role("button", name="Write with AI").first
            return button.is_visible(timeout=2000)
        except Exception:
            return False
    
    def is_ai_working(self) -> bool:
        """
        检查 AI 是否正在工作（通过检测 "AI is working on it" 文本）
        
        Returns:
            bool: True表示AI正在工作，False表示不在工作
        """
        try:
            # 检查 "AI is working on it" 文本
            ai_working = self.page.get_by_text("AI is working on it").first
            return ai_working.is_visible(timeout=1000)
        except Exception:
            return False
    
    def wait_for_ai_description_generation(self, timeout: int = 100000) -> bool:
        """
        等待 AI 描述生成完成（带智能重试机制）
        
        优化逻辑：
        - 当显示 Write with AI 按钮 → 重新点击，继续操作
        - 当显示 "AI is working on it" → AI 正在生成，继续下次循环判断
        - 否则 → 代表生成完成，停止循环
        
        Args:
            timeout: 最大等待时间(毫秒)，默认100000ms（100秒）
            
        Returns:
            bool: True表示AI成功生成内容，False表示超时未生成
        """
        # 循环检查模式：最多10次，每次等待10秒
        max_retries = 10
        for i in range(max_retries):
            # 1. 等待间隔
            self.page.wait_for_timeout(10000)
            self.logger.info(f"⏳ 已等待 10 秒 (第 {i+1}/{max_retries} 次)")
            
            # 2. 优先检查 Write with AI 按钮是否可见
            if self.is_write_with_ai_button_visible():
                self.logger.info(f"⚠️ 检测到 Write with AI 按钮，重新点击 (第 {i+1}/{max_retries} 次)")
                try:
                    self.click_write_with_ai()
                    continue  # 点击后继续下次循环
                except Exception as e:
                    self.logger.warning(f"重新点击失败: {e}，继续下次循环...")
                    continue
            
            # 3. 检查是否显示 "AI is working on it"
            if self.is_ai_working():
                self.logger.info(f"⏳ 检测到 'AI is working on it'，AI 正在生成中，继续等待... (第 {i+1}/{max_retries} 次)")
                continue  # 继续下次循环
            
            # 4. 既不显示按钮也不显示工作状态 → 代表生成完成
            self.logger.info(f"✓ 未检测到按钮或工作状态，判断为生成完成 (第 {i+1} 次检查)")
            
            # 额外等待3秒确保描述内容完全填充
            self.page.wait_for_timeout(3000)
            
            description = self.get_description_value()
            if len(description) > 0:
                self.logger.info(f"✅ AI描述生成完成，长度: {len(description)}字符")
                return True
            else:
                self.logger.warning(f"⚠️ 判断为生成完成但描述为空或过短(长度: {len(description)})，继续等待...")
                continue
        
        # 超时返回
        self.logger.warning(f"⚠️ AI描述未在 {max_retries * 10}秒 内生成")
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
            str: 上传计数（如 "1/20" 或 "1/9"）
        """
        try:
            # 方法1: 直接查找匹配 "数字/数字" 格式的文本(最简单有效)
            count_elem = self.page.locator('text=/\\d+\\/\\d+/').first
            return count_elem.inner_text(timeout=3000).strip()
        except Exception as e:
            self.logger.error(f"获取上传计数失败(方法1): {e}")
            # 方法2: 通过Pictures区域定位
            try:
                pictures_area = self.page.locator('text=Pictures').first
                parent = pictures_area.locator('..')
                count_text = parent.locator('text=/\\d+\\/\\d+/').first.inner_text(timeout=2000)
                return count_text.strip()
            except Exception as e2:
                self.logger.error(f"获取上传计数失败(方法2): {e2}")
                return "0/20"
    
    def get_description_value(self) -> str:
        """
        获取Description字段的值
        
        实际 HTML 结构：
        <textarea autocomplete="off" placeholder="..." maxlength="10000" 
                  class="limited-textarea-input form-control" ...>内容</textarea>
        
        按照 ai-description-retry-pattern 规则实现：
        - 必须有容错处理
        - 失败时返回空字符串 ""，不抛出异常
        
        Returns:
            str: Description内容，获取失败返回空字符串
        """
        # 方法1: 通过 class "limited-textarea-input form-control"
        try:
            desc_textarea = self.page.locator('textarea.limited-textarea-input.form-control').first
            if desc_textarea.count() > 0 and desc_textarea.is_visible(timeout=1000):
                val = desc_textarea.input_value()
                if val:
                    return val.strip()
        except Exception:
            pass

        # 方法2: 通过 maxlength="10000"
        try:
            desc_textarea = self.page.locator('textarea[maxlength="10000"]').first
            if desc_textarea.count() > 0 and desc_textarea.is_visible(timeout=1000):
                val = desc_textarea.input_value()
                if val:
                    return val.strip()
        except Exception:
            pass
        
        # 方法3: 通过 Description * 容器下的 textarea
        try:
            desc_textarea = self.page.locator('div').filter(has_text='Description *').locator('textarea').first
            if desc_textarea.count() > 0 and desc_textarea.is_visible(timeout=1000):
                val = desc_textarea.input_value()
                if val:
                    return val.strip()
        except Exception:
            pass
        
        # 方法4: 通过 id (备用)
        try:
            desc_textarea = self.page.locator('textarea#description').first
            if desc_textarea.count() > 0 and desc_textarea.is_visible(timeout=1000):
                val = desc_textarea.input_value()
                if val:
                    return val.strip()
        except Exception:
            pass

        # 方法5: 兜底 - contenteditable (旧版本可能使用)
        try:
            desc_editable = self.page.locator('[contenteditable="true"]').first
            if desc_editable.count() > 0 and desc_editable.is_visible(timeout=1000):
                val = desc_editable.inner_text().strip()
                if val:
                    return val
        except Exception:
            pass

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
        例如 "0/20" -> 0, "Upload 1/20" -> 1, "3/20" -> 3, "1/9" -> 1
        
        Args:
            upload_count_str: get_upload_count() 返回值
            
        Returns:
            int: 已上传图片数量，解析失败返回 0
        """
        try:
            if not upload_count_str:
                return 0
            import re
            # 动态匹配 "数字/数字" 格式,不限制总数
            match = re.search(r'(\d+)/(\d+)', upload_count_str)
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
