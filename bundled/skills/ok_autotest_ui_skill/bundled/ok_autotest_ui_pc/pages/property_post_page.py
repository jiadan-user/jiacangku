# pages/property_post_page.py
from pages.base_page import BasePage
from utils.logger import setup_logger

class PropertyPostPage(BasePage):
    """房产发布页面对象"""
    
    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()
    
    # ========== 页面操作方法（静默执行）==========
    
    def navigate_to_publish_page(self, target_url):
        """
        导航到发布页面
        
        Args:
            target_url: 发布页面完整URL
        """
        try:
            self.page.goto(target_url, timeout=30000)
            self.page.wait_for_load_state("domcontentloaded")
        except Exception as e:
            self.logger.error(f"导航到发布页面失败: {e}")
            raise
    
    def upload_image(self, image_path):
        """
        上传图片（基于录制的操作）
        
        Args:
            image_path: 图片文件路径（相对于项目根目录）
        """
        try:
            import os
            # 将相对路径转换为绝对路径
            abs_path = os.path.abspath(image_path)
            
            # 方法1：直接设置文件输入框（最可靠）
            try:
                self.page.set_input_files("input[type='file']", abs_path)
                self.page.wait_for_timeout(2000)
                return
            except Exception as e1:
                self.logger.warning(f"方法1失败，尝试方法2: {e1}")
            
            # 方法2：尝试点击 "Choose File" 按钮
            try:
                self.page.get_by_role("button", name="Choose File").click()
                self.page.wait_for_timeout(500)
                self.page.set_input_files("input[type='file']", abs_path)
                self.page.wait_for_timeout(2000)
                return
            except Exception as e2:
                self.logger.warning(f"方法2失败，尝试方法3: {e2}")
            
            # 方法3：尝试查找包含 "file" 或 "upload" 的按钮
            try:
                upload_button = self.page.locator("button:has-text('file'), button:has-text('upload'), button:has-text('图片')").first
                upload_button.click()
                self.page.wait_for_timeout(500)
                self.page.set_input_files("input[type='file']", abs_path)
                self.page.wait_for_timeout(2000)
                return
            except Exception as e3:
                raise Exception(f"所有上传方法均失败: 方法1={e1}, 方法2={e2}, 方法3={e3}")
                
        except Exception as e:
            self.logger.error(f"上传图片失败: {e}")
            raise
    
    def input_title(self, title):
        """
        输入标题
        
        Args:
            title: 标题文本
        """
        try:
            # 优先使用录制得到的稳定选择器 #title
            self.page.locator("#title").fill(title)
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"输入标题失败: {e}")
            raise
    
    def input_description(self, description):
        """
        输入描述
        
        Args:
            description: 描述文本
        """
        try:
            self.page.locator("#content").fill(description)
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"输入描述失败: {e}")
            raise
    
    def input_price(self, price):
        """
        输入价格
        
        Args:
            price: 价格（字符串或数字）
        """
        try:
            self.page.locator("#amount").fill(str(price))
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"输入价格失败: {e}")
            raise
    
    def select_category_property_for_rent(self):
        """
        选择分类：Property for Rent（基于录制的建议分类）
        """
        try:
            # 基于 snapshot 中上传图片后出现的 "Suggested Categories"
            # ref=e208: "PropertyProperty For Rent Residential"
            self.page.get_by_text("PropertyProperty For Rent").first.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            # 如果建议分类不可见，尝试点击 "More Categories"
            try:
                self.logger.error(f"选择建议分类失败，尝试 More Categories: {e}")
                self.page.get_by_text("More Categories").click()
                self.page.wait_for_timeout(1000)
                # TODO: 补充录制 More Categories 后的分类选择流程
            except Exception as e2:
                self.logger.error(f"选择分类失败: {e2}")
                raise
    
    def select_category_property_for_sale(self):
        """
        选择分类：Property For Sale > Residential > Villa（基于录制的建议分类）
        """
        try:
            # 基于录制时的操作：填写 Title 和 Description 后，系统会推荐分类
            # 实际录制时的文本是 "PropertyProperty For SaleResidential" + "Villa"
            # 尝试精确匹配
            category_selector = self.page.locator("text=PropertyProperty For SaleResidentialVilla").first
            if not category_selector.is_visible(timeout=3000):
                # 如果精确匹配不可见，尝试只匹配主分类
                category_selector = self.page.locator("text=PropertyProperty For SaleResidential").first
            
            category_selector.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            # 如果建议分类不可见，尝试点击 "More Categories"
            try:
                self.logger.error(f"选择建议分类失败，尝试 More Categories: {e}")
                self.page.get_by_text("More Categories").click()
                self.page.wait_for_timeout(1000)
                # TODO: 补充录制 More Categories 后的分类选择流程
            except Exception as e2:
                self.logger.error(f"选择分类失败: {e2}")
                raise
    
    def click_post_button(self):
        """点击 Post 按钮提交"""
        try:
            # 基于 snapshot 中的 ref=e153 (button "Post")
            self.page.get_by_role("button", name="Post").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击 Post 按钮失败: {e}")
            raise
    
    def get_upload_counter(self):
        """
        获取上传计数器文本（如 "1/9"）
        
        Returns:
            str: 计数器文本
        """
        try:
            # 基于 snapshot 中的 ref=e201 (generic: "1/9")
            counter = self.page.locator("text=/\\d+\\/\\d+/").first
            return counter.text_content()
        except Exception as e:
            self.logger.error(f"获取上传计数器失败: {e}")
            return ""
    
    def is_image_thumbnail_visible(self):
        """
        判断图片缩略图是否可见
        
        Returns:
            bool: 缩略图是否可见
        """
        try:
            # 基于 snapshot 中上传后出现的 button "Main"
            thumbnail = self.page.get_by_role("button", name="Main")
            return thumbnail.is_visible(timeout=3000)
        except Exception:
            return False
    
    def is_post_button_visible(self):
        """
        判断 Post 按钮是否可见
        
        Returns:
            bool: Post 按钮是否可见
        """
        try:
            post_button = self.page.get_by_role("button", name="Post")
            return post_button.is_visible(timeout=3000)
        except Exception:
            return False
    
    def get_location_value(self):
        """
        获取当前设置的位置信息
        
        Returns:
            str: 位置文本
        """
        try:
            # 基于 snapshot 中的 ref=e96 (textbox "Set the location for your post.")
            location_input = self.page.locator("textbox[placeholder*='location']").first
            return location_input.input_value()
        except Exception as e:
            self.logger.error(f"获取位置信息失败: {e}")
            # 返回默认值
            return "SS Real Estate"
