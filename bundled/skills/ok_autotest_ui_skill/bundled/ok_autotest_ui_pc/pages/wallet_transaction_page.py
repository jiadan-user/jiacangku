"""
Wallet交易明细页面对象
封装交易明细页面的元素定位和操作逻辑
"""
from playwright.sync_api import Page, expect
from utils.logger import setup_logger

logger = setup_logger()


class WalletTransactionPage:
    """钱包交易明细页面对象类"""
    
    def __init__(self, page: Page):
        self.page = page
        self.base_url = "https://aepub.58v5.cn/biz/en/wallet/details"
        
        # ========== 页面元素定位器（Locators）==========
        # 页面标题
        self._transaction_history_title = page.get_by_text("Transaction History", exact=True)
        
        # 交易记录表格
        self._transaction_table = page.locator("table").first
        self._table_rows = page.locator("table tbody tr")
        
        # 表格列（用于读取数据）
        self._first_row_type = page.locator("table tbody tr").first.locator("td").nth(0)
        self._first_row_date = page.locator("table tbody tr").first.locator("td").nth(1)
        self._first_row_amount = page.locator("table tbody tr").first.locator("td").nth(2)
        self._first_row_status = page.locator("table tbody tr").first.locator("td").nth(3)
        self._first_row_operate = page.locator("table tbody tr").first.locator("td").nth(4)
    
    # ========== 页面操作方法（Actions）==========
    
    def navigate_to_transaction_page(self):
        """导航到交易明细页面"""
        logger.info(f"导航到交易明细页面: {self.base_url}")
        self.page.goto(self.base_url)
    
    # ========== 页面状态检查方法（Assertions）==========
    
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
    
    def get_first_transaction_row_data(self) -> dict:
        """
        获取第一行交易记录数据
        
        Returns:
            dict: 包含type, date, amount, status, operate字段的字典
        """
        try:
            # 检查是否有数据行
            row_count = self._table_rows.count()
            if row_count == 0:
                logger.info("交易记录表格为空")
                return {}
            
            # 读取第一行数据
            type_text = self._first_row_type.text_content(timeout=3000).strip()
            date_text = self._first_row_date.text_content(timeout=3000).strip()
            amount_text = self._first_row_amount.text_content(timeout=3000).strip()
            status_text = self._first_row_status.text_content(timeout=3000).strip()
            operate_text = self._first_row_operate.text_content(timeout=3000).strip()
            
            data = {
                'type': type_text,
                'date': date_text,
                'amount': amount_text,
                'status': status_text,
                'operate': operate_text
            }
            
            logger.info(f"第一行交易数据: {data}")
            return data
            
        except Exception as e:
            logger.warning(f"获取第一行交易数据失败: {e}")
            return {}
