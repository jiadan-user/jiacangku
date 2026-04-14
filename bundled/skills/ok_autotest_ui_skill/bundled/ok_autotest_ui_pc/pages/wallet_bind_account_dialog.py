"""
Wallet绑定银行账户对话框对象
封装绑定银行账户弹窗的元素定位和操作逻辑
"""
from playwright.sync_api import Page, expect
from utils.logger import setup_logger

logger = setup_logger()


class WalletBindAccountDialog:
    """钱包绑定银行账户对话框对象类"""
    
    def __init__(self, page: Page):
        self.page = page
        
        # ========== 对话框基础元素（主页面）==========
        self._dialog = page.locator("dialog[open]").first
        self._dialog_title = page.get_by_role("heading", name="Bind Bank Account", level=3)
        self._close_button = page.locator("dialog[open] img").first  # X关闭按钮（修复：不限定在_dialog.locator内）
        self._submit_button = page.get_by_role("button", name="Submit")
        
        # ========== iframe内元素（需要通过iframe访问）==========
        # 获取iframe
        self._iframe = page.frame_locator('iframe[title="beneficiaryForm element iframe"]')
        
        # Account country / region下拉框
        self._country_dropdown_trigger = self._iframe.locator('div').filter(has_text="Select recipient's bank country / region").nth(2)
        self._country_dropdown_label = self._iframe.get_by_text("Account country / region").first
        
        # Account currency下拉框
        self._currency_dropdown = self._iframe.get_by_text("Account currency").first
        self._currency_text = self._iframe.get_by_text("AED", exact=False).first
        
        # Transfer method区域
        self._transfer_method_section = self._iframe.get_by_text("Transfer method")
        
        # LOCAL选项
        self._local_option = self._iframe.get_by_role("heading", name="LOCAL", level=4)
        self._local_description = self._iframe.get_by_text("Domestic bank transfer in the destination country")
        self._local_fee = self._iframe.get_by_text("5.00 USD").first  # 使用.first避免strict mode
        self._local_speed = self._iframe.get_by_text("2 - 3 business days")
        self._local_select_button = self._iframe.get_by_test_id("LOCAL")
        self._local_change_button = self._iframe.get_by_role("button", name="Change transfer method")
        
        # SWIFT选项
        self._swift_option = self._iframe.get_by_role("heading", name="SWIFT", level=4)
        self._swift_description = self._iframe.get_by_text("International bank transfer")
        self._swift_fee = self._iframe.get_by_text("25.00 USD (OUR) or 15.00 USD (SHA)")
        self._swift_speed = self._iframe.get_by_text("0 - 1 business days")
        
        # 银行账户表单字段
        self._iban_input = self._iframe.get_by_role("textbox", name="IBAN")
        self._account_holder_input = self._iframe.get_by_role("textbox", name="Name of account holder")
        self._nickname_input = self._iframe.get_by_role("textbox", name="NicknameOptional")
        self._email_input = self._iframe.get_by_role("textbox", name="Email addressOptional")
        # Address输入框：使用test-id更精确定位，避免strict mode violation
        self._address_input = self._iframe.get_by_test_id("lookupInputSearchValue").get_by_role("textbox")
        self._city_input = self._iframe.get_by_role("textbox", name="City")
    
    # ========== 页面操作方法（Actions）==========
    
    def click_country_dropdown(self):
        """点击Account country / region下拉框"""
        try:
            logger.info("点击Account country / region下拉框")
            self._country_dropdown_trigger.click()
            self.page.wait_for_timeout(1000)  # 等待下拉选项展开
        except Exception as e:
            logger.error(f"点击Account country / region下拉框失败: {e}")
            raise
    
    def select_country(self, country_name: str):
        """
        选择国家
        
        Args:
            country_name: 国家名称，如"United Arab Emirates"
        """
        try:
            logger.info(f"选择国家: {country_name}")
            self._iframe.get_by_role("option", name=country_name).click()
        except Exception as e:
            logger.error(f"选择国家失败: {e}")
            raise
    
    def click_local_select_button(self):
        """点击LOCAL选项的Select按钮"""
        try:
            logger.info("点击LOCAL选项的Select按钮")
            self._local_select_button.click()
        except Exception as e:
            logger.error(f"点击LOCAL选项的Select按钮失败: {e}")
            raise
    
    # ========== 页面状态检查方法（Assertions）==========
    
    def is_dialog_title_visible(self, timeout: int = 5000) -> bool:
        """检查对话框标题是否可见"""
        try:
            expect(self._dialog_title).to_be_visible(timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"对话框标题未显示: {e}")
            return False
    
    def is_close_button_visible(self, timeout: int = 3000) -> bool:
        """检查关闭按钮是否可见"""
        try:
            expect(self._close_button).to_be_visible(timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"关闭按钮未显示: {e}")
            return False
    
    def is_country_dropdown_visible(self, timeout: int = 3000) -> bool:
        """检查Account country / region下拉框是否可见"""
        try:
            expect(self._country_dropdown_label).to_be_visible(timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"Account country / region下拉框未显示: {e}")
            return False
    
    def is_currency_dropdown_visible(self, timeout: int = 3000) -> bool:
        """检查Account currency下拉框是否可见"""
        try:
            expect(self._currency_dropdown).to_be_visible(timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"Account currency下拉框未显示: {e}")
            return False
    
    def is_submit_button_visible(self, timeout: int = 3000) -> bool:
        """检查Submit按钮是否可见"""
        try:
            expect(self._submit_button).to_be_visible(timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"Submit按钮未显示: {e}")
            return False
    
    def get_currency_text(self) -> str:
        """获取Account currency文本内容"""
        try:
            # 尝试多种方式获取货币文本
            currency_locator = self._iframe.get_by_text("AED").first
            text = currency_locator.text_content(timeout=3000)
            logger.info(f"当前货币: {text}")
            return text.strip() if text else ""
        except Exception as e:
            logger.warning(f"获取货币文本失败: {e}")
            return ""
    
    def is_transfer_method_section_visible(self, timeout: int = 3000) -> bool:
        """检查Transfer method区域是否可见"""
        try:
            expect(self._transfer_method_section).to_be_visible(timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"Transfer method区域未显示: {e}")
            return False
    
    def is_local_option_visible(self, timeout: int = 3000) -> bool:
        """检查LOCAL选项是否可见"""
        try:
            expect(self._local_option).to_be_visible(timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"LOCAL选项未显示: {e}")
            return False
    
    def get_local_option_info(self) -> dict:
        """
        获取LOCAL选项详细信息
        
        Returns:
            dict: 包含description, fee, speed字段的字典
        """
        try:
            description = self._local_description.text_content(timeout=3000)
            if not description:
                description = ""
            
            fee = self._local_fee.text_content(timeout=3000)
            if not fee:
                fee = ""
            
            speed = self._local_speed.text_content(timeout=3000)
            if not speed:
                speed = ""
            
            info = {
                'description': description.strip(),
                'fee': fee.strip(),
                'speed': speed.strip()
            }
            
            logger.info(f"LOCAL选项信息: {info}")
            return info
        except Exception as e:
            logger.warning(f"获取LOCAL选项信息失败: {e}")
            # 返回空字符串而不是空字典，避免KeyError
            return {'description': '', 'fee': '', 'speed': ''}
    
    def is_swift_option_visible(self, timeout: int = 3000) -> bool:
        """检查SWIFT选项是否可见"""
        try:
            expect(self._swift_option).to_be_visible(timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"SWIFT选项未显示: {e}")
            return False
    
    def get_swift_option_info(self) -> dict:
        """
        获取SWIFT选项详细信息
        
        Returns:
            dict: 包含description, fee, speed字段的字典
        """
        try:
            description = self._swift_description.text_content(timeout=3000)
            if not description:
                description = ""
            
            fee = self._swift_fee.text_content(timeout=3000)
            if not fee:
                fee = ""
            
            speed = self._swift_speed.text_content(timeout=3000)
            if not speed:
                speed = ""
            
            info = {
                'description': description.strip(),
                'fee': fee.strip(),
                'speed': speed.strip()
            }
            
            logger.info(f"SWIFT选项信息: {info}")
            return info
        except Exception as e:
            logger.warning(f"获取SWIFT选项信息失败: {e}")
            # 返回空字符串而不是空字典，避免KeyError
            return {'description': '', 'fee': '', 'speed': ''}
    
    def is_local_change_button_visible(self, timeout: int = 3000) -> bool:
        """检查LOCAL的Change按钮是否可见"""
        try:
            expect(self._local_change_button).to_be_visible(timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"LOCAL的Change按钮未显示: {e}")
            return False
    
    def is_iban_input_visible(self, timeout: int = 3000) -> bool:
        """检查IBAN输入框是否可见"""
        try:
            expect(self._iban_input).to_be_visible(timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"IBAN输入框未显示: {e}")
            return False
    
    def is_account_holder_input_visible(self, timeout: int = 3000) -> bool:
        """检查Name of account holder输入框是否可见"""
        try:
            expect(self._account_holder_input).to_be_visible(timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"Name of account holder输入框未显示: {e}")
            return False
    
    def is_nickname_input_visible(self, timeout: int = 3000) -> bool:
        """检查Nickname输入框是否可见"""
        try:
            expect(self._nickname_input).to_be_visible(timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"Nickname输入框未显示: {e}")
            return False
    
    def is_email_input_visible(self, timeout: int = 3000) -> bool:
        """检查Email address输入框是否可见"""
        try:
            expect(self._email_input).to_be_visible(timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"Email address输入框未显示: {e}")
            return False
    
    def is_address_input_visible(self, timeout: int = 3000) -> bool:
        """检查Address搜索框是否可见"""
        try:
            expect(self._address_input).to_be_visible(timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"Address搜索框未显示: {e}")
            return False
    
    def is_city_input_visible(self, timeout: int = 3000) -> bool:
        """检查City输入框是否可见"""
        try:
            expect(self._city_input).to_be_visible(timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"City输入框未显示: {e}")
            return False
