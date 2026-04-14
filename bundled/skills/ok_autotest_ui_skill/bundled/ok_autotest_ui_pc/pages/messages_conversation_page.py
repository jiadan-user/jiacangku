# pages/messages_conversation_page.py
from pages.base_page import BasePage
from utils.logger import setup_logger


class MessagesConversationPage(BasePage):
    """OK.com Messages会话页面对象（静默执行）"""
    
    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()
    
    # ========== 页面元素选择器 ==========
    
    # 会话列表相关
    CONVERSATION_LIST = "[class*='conversation-list'], [class*='chat-list'], .message-list"
    CONVERSATION_ITEM = "[class*='conversation-item'], [class*='chat-item'], [class*='message-item']"
    
    # 会话详情相关
    CONVERSATION_DETAIL = "[class*='conversation-detail'], [class*='chat-detail'], [class*='message-detail']"
    SECURITY_TIP = "[class*='security-tip'], [class*='safety-tip'], [class*='warning-banner']"
    MESSAGE_INPUT = "textarea[placeholder*='message'], input[type='text']"
    
    # 功能按钮
    PHONE_BUTTON = "button[class*='phone'], button[aria-label*='call'], button[aria-label*='phone']"
    SETTINGS_BUTTON = "button[class*='settings'], button[aria-label*='more'], button[aria-label*='settings']"
    MORE_BUTTON = "button:has-text('⋮'), button:has-text('...'), button[aria-label*='more']"
    
    # 设置菜单
    SETTINGS_MENU = "[role='menu'], [class*='dropdown-menu'], [class*='settings-menu']"
    MUTE_OPTION = "text=/mute|do not disturb|免打扰|静音/i"
    BLOCK_OPTION = "text=/block|拉黑|屏蔽/i"
    
    # 对话框
    CONFIRM_DIALOG = "[role='dialog'], [class*='modal'], [class*='confirm']"
    CONFIRM_BUTTON = "button:has-text('Confirm'), button:has-text('确认'), button:has-text('Block')"
    CANCEL_BUTTON = "button:has-text('Cancel'), button:has-text('取消')"
    
    # ========== 页面操作方法（静默执行）==========
    
    def navigate_to_messages(self):
        """导航到Messages页面"""
        try:
            self.page.goto("https://aepub.ok.com/biz/en/chat", wait_until="domcontentloaded", timeout=60000)
            # 等待页面加载，不使用 networkidle
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"导航到Messages页面失败: {e}")
            raise
    
    def wait_for_conversation_list(self, timeout=10000):
        """等待会话列表加载"""
        try:
            # 等待页面加载完成即可，会话列表会自动显示
            self.page.wait_for_load_state('domcontentloaded', timeout=timeout)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"等待会话列表加载失败: {e}")
            raise
    
    def click_second_conversation(self):
        """点击第二个会话"""
        try:
            # 从截图看，左侧会话列表中每个会话都是一个可点击的区域
            # 尝试多种选择器定位会话项
            selectors = [
                "div[class*='conversation']",
                "div[class*='chat']",
                "a[href*='chat']",
                "li",
                "div[role='button']"
            ]
            
            conversation_items = None
            for selector in selectors:
                try:
                    items = self.page.locator(selector)
                    count = items.count()
                    if count >= 2:
                        conversation_items = items
                        break
                except Exception:
                    continue
            
            if conversation_items is None:
                raise Exception("未找到会话列表项")
            
            # 点击第二个会话
            second_conversation = conversation_items.nth(1)
            second_conversation.click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击第二个会话失败: {e}")
            raise
    
    def is_conversation_detail_visible(self, timeout=5000):
        """验证会话详情是否可见"""
        try:
            # 从截图看，右侧会话详情区域包含消息输入框
            # 使用消息输入框作为会话详情的标识
            selectors = [
                "text=/Input message/i",
                "textarea[placeholder*='message']",
                "input[placeholder*='message']",
                self.MESSAGE_INPUT,
                self.CONVERSATION_DETAIL
            ]
            
            for selector in selectors:
                try:
                    if self.is_visible(selector, timeout=timeout):
                        return True
                except Exception:
                    continue
            
            return False
        except Exception as e:
            self.logger.error(f"验证会话详情失败: {e}")
            return False
    
    def is_security_tip_visible(self, timeout=5000):
        """验证安全提示是否可见"""
        try:
            # 根据截图，安全提示文本为："For your safety, please avoid sharing sensitive personal information..."
            # 使用文本内容查找
            selectors = [
                "text=/For your safety/i",
                "text=/avoid sharing sensitive/i",
                "text=/personal information/i",
                self.SECURITY_TIP,
                "[class*='tip']",
                "[class*='alert']",
                "[class*='warning']"
            ]
            
            for selector in selectors:
                try:
                    if self.is_visible(selector, timeout=timeout):
                        return True
                except Exception:
                    continue
            
            return False
        except Exception as e:
            self.logger.error(f"验证安全提示失败: {e}")
            return False
    
    def get_security_tip_text(self):
        """获取安全提示文本"""
        try:
            # 尝试多种方式获取安全提示文本
            selectors = [
                "text=/For your safety/i",
                self.SECURITY_TIP,
                "[class*='tip']"
            ]
            
            for selector in selectors:
                try:
                    security_tip = self.page.locator(selector).first
                    text = security_tip.text_content()
                    if text and len(text) > 0:
                        return text
                except Exception:
                    continue
            
            return ""
        except Exception as e:
            self.logger.error(f"获取安全提示文本失败: {e}")
            return ""
    
    def is_phone_button_visible(self, timeout=3000):
        """检查电话按钮是否存在"""
        try:
            return self.is_visible(self.PHONE_BUTTON, timeout=timeout)
        except Exception:
            return False
    
    def click_phone_button(self):
        """点击电话按钮"""
        try:
            phone_button = self.page.locator(self.PHONE_BUTTON).first
            phone_button.click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击电话按钮失败: {e}")
            raise
    
    def is_settings_button_visible(self, timeout=3000):
        """检查设置按钮是否存在"""
        try:
            # 尝试多种可能的设置按钮
            selectors = [self.SETTINGS_BUTTON, self.MORE_BUTTON]
            for selector in selectors:
                try:
                    if self.is_visible(selector, timeout=timeout):
                        return True
                except Exception:
                    continue
            return False
        except Exception:
            return False
    
    def click_settings_button(self):
        """点击设置按钮"""
        try:
            # 尝试多种可能的设置按钮
            selectors = [self.SETTINGS_BUTTON, self.MORE_BUTTON]
            for selector in selectors:
                try:
                    settings_button = self.page.locator(selector).first
                    if settings_button.is_visible(timeout=2000):
                        settings_button.click()
                        self.page.wait_for_timeout(1000)
                        return
                except Exception:
                    continue
            
            raise Exception("未找到设置按钮")
        except Exception as e:
            self.logger.error(f"点击设置按钮失败: {e}")
            raise
    
    def is_settings_menu_visible(self, timeout=3000):
        """检查设置菜单是否展开"""
        try:
            return self.is_visible(self.SETTINGS_MENU, timeout=timeout)
        except Exception:
            return False
    
    def is_mute_option_visible(self, timeout=3000):
        """检查免打扰选项是否存在"""
        try:
            return self.is_visible(self.MUTE_OPTION, timeout=timeout)
        except Exception:
            return False
    
    def click_mute_option(self):
        """点击免打扰选项"""
        try:
            mute_option = self.page.locator(self.MUTE_OPTION).first
            mute_option.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击免打扰选项失败: {e}")
            raise
    
    def is_block_option_visible(self, timeout=3000):
        """检查拉黑选项是否存在"""
        try:
            return self.is_visible(self.BLOCK_OPTION, timeout=timeout)
        except Exception:
            return False
    
    def click_block_option(self):
        """点击拉黑选项"""
        try:
            block_option = self.page.locator(self.BLOCK_OPTION).first
            block_option.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击拉黑选项失败: {e}")
            raise
    
    def is_confirm_dialog_visible(self, timeout=3000):
        """检查确认对话框是否显示"""
        try:
            return self.is_visible(self.CONFIRM_DIALOG, timeout=timeout)
        except Exception:
            return False
    
    def click_cancel_button(self):
        """点击取消按钮"""
        try:
            cancel_button = self.page.locator(self.CANCEL_BUTTON).first
            cancel_button.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击取消按钮失败: {e}")
            raise
    
    def get_available_features(self):
        """
        探索并返回所有可用功能列表
        
        Returns:
            list: 可用功能名称列表
        """
        features = []
        
        try:
            # 检查电话功能
            if self.is_phone_button_visible(timeout=2000):
                features.append("电话")
            
            # 检查设置功能
            if self.is_settings_button_visible(timeout=2000):
                features.append("设置")
                
                # 打开设置菜单检查子功能
                self.click_settings_button()
                
                if self.is_mute_option_visible(timeout=2000):
                    features.append("免打扰")
                
                if self.is_block_option_visible(timeout=2000):
                    features.append("拉黑")
                
                # 关闭设置菜单（点击其他区域）
                self.page.keyboard.press('Escape')
                self.page.wait_for_timeout(500)
        
        except Exception as e:
            self.logger.error(f"探索功能失败: {e}")
        
        return features
