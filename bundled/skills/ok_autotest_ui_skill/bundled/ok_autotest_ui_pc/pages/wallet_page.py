"""
Wallet页面对象
封装钱包页面的元素定位和操作逻辑
"""
from playwright.sync_api import Page, expect
from utils.logger import setup_logger

logger = setup_logger()


class WalletPage:
    """钱包页面对象类"""
    
    def __init__(self, page: Page):
        self.page = page
        self.base_url = "https://aepub.58v5.cn/biz/en/wallet/home"
        
        # ========== 页面元素定位器（Locators）==========
        # 未登录状态元素（登录对话框会自动弹出）
        self._login_dialog = page.locator("dialog, [role='dialog']").first
        self._login_prompt_text = page.get_by_text("Log in to view more content")
        self._login_button_in_page = page.get_by_role("button", name="Login")
        
        # 余额区域元素
        self._balance_label = page.get_by_text("Balance", exact=False).first
        self._balance_text = page.locator("text=/^[\\*\\$]/").first  # 匹配以*或$开头的文本
        self._balance_eye_icon = page.get_by_role("img").nth(2)  # 第3个图标
        self._balance_question_icon = page.locator('.AmountArea_onGoAnswer__jzIp0')  # 问号图标
        self._local_currency_text = page.get_by_text("≈ AED", exact=False).first
        
        # 银行账户区域元素
        self._bank_account_label = page.get_by_text("Bank Account", exact=False).first
        self._add_bank_account_button = page.get_by_text("Add Bank Account")
        
        # 交易明细相关元素
        self._details_link = page.get_by_text("Details", exact=True).first
        self._transaction_history_title = page.get_by_text("Transaction History", exact=True)
        self._transaction_table = page.locator("table").first
    
    # ========== 页面操作方法（Actions）==========
    
    def navigate_to_wallet_page(self):
        """导航到钱包页面"""
        logger.info(f"导航到钱包页面: {self.base_url}")
        self.page.goto(self.base_url)
    
    def click_balance_eye_icon(self):
        """点击余额右侧的眼睛图标"""
        logger.info("点击余额眼睛图标")
        self._balance_eye_icon.click()
    
    def click_wallet_rules_icon(self):
        """点击Balance旁边的问号图标（Wallet Rules）"""
        logger.info("点击钱包规则图标")
        self._balance_question_icon.click()
    
    def click_details_link(self):
        """点击Details链接"""
        logger.info("点击Details链接")
        self._details_link.click()
    
    def click_add_bank_account(self):
        """点击Add Bank Account按钮"""
        logger.info("点击Add Bank Account按钮")
        add_bank_account_button = self.page.get_by_text("Add Bank Account")
        add_bank_account_button.click()
    
    # ========== 页面状态检查方法（Assertions）==========
    
    def is_login_prompt_visible(self, timeout: int = 5000) -> bool:
        """检查登录提示或登录对话框是否可见（未登录状态会自动弹出登录框）"""
        try:
            # 检查是否有登录对话框或登录相关元素
            # 由于未登录时会自动弹出登录框，我们检查email输入框
            email_input = self.page.get_by_role('textbox', name='Email or phone number')
            expect(email_input).to_be_visible(timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"登录提示未显示: {e}")
            return False
    
    def is_login_button_visible(self, timeout: int = 3000) -> bool:
        """检查Login按钮是否可见（在登录对话框中的Continue按钮）"""
        try:
            continue_button = self.page.get_by_role('button', name='Continue')
            expect(continue_button).to_be_visible(timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"Login按钮未显示: {e}")
            return False
    
    def is_balance_area_visible(self, timeout: int = 5000) -> bool:
        """检查余额区域是否可见"""
        try:
            expect(self._balance_label).to_be_visible(timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"余额区域未显示: {e}")
            return False
    
    def is_bank_account_area_visible(self, timeout: int = 3000) -> bool:
        """检查银行账户区域是否可见"""
        try:
            expect(self._bank_account_label).to_be_visible(timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"银行账户区域未显示: {e}")
            return False
    
    def get_balance_text(self) -> str:
        """获取余额文本内容"""
        try:
            # 查找包含****或$开头的文本
            balance_element = self.page.locator("text=/^(\\*{4}|\\$[\\d\\.]+)/").first
            balance = balance_element.text_content(timeout=3000)
            logger.info(f"当前余额显示: {balance}")
            return balance.strip() if balance else ""
        except Exception as e:
            logger.warning(f"无法获取余额文本: {e}")
            return ""
    
    def is_local_currency_visible(self, timeout: int = 3000) -> bool:
        """检查当地货币等值金额是否可见"""
        try:
            expect(self._local_currency_text).to_be_visible(timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"当地货币等值金额未显示: {e}")
            return False
    
    def is_transaction_history_title_visible(self, timeout: int = 5000) -> bool:
        """检查Transaction History标题是否可见"""
        try:
            expect(self._transaction_history_title).to_be_visible(timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"Transaction History标题未显示: {e}")
            return False
    
    def is_transaction_table_visible(self, timeout: int = 3000) -> bool:
        """检查交易记录表格是否可见"""
        try:
            expect(self._transaction_table).to_be_visible(timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"交易记录表格未显示: {e}")
            return False
