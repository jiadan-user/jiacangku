"""
AE 站点 Settings 页面 Page Object
包含 Account Settings、New Messages 等模块的元素定位和操作
"""
from playwright.sync_api import Page, expect


class SettingsPage:
    """Settings 页面 Page Object"""
    
    def __init__(self, page: Page):
        self.page = page
        
        # Account Settings 标签
        self.account_settings_tab = page.locator("text=Account Settings")
        
        # New Messages 模块
        self.new_messages_title = page.get_by_text("New Messages", exact=True)
        # 描述文字可能有多种表述，使用部分匹配
        self.new_messages_description = page.locator("text=/email notification.*new message/i")
        # 开关元素 - 尝试多种可能的选择器
        self.new_messages_toggle = page.locator(
            "[class*='switchImg'], [class*='switch'], [class*='toggle'], "
            "[role='switch'], input[type='checkbox']"
        ).first
        self.new_messages_enabled_text = page.locator("text=/email notification.*enabled/i")
        self.new_messages_subtext = page.locator("text=/unsubscribe.*notification/i")
        
        # 3rd Party Account 模块（用于定位）
        self.third_party_account_title = page.get_by_text("3rd Party Account", exact=True)
    
    def navigate_to_settings(self):
        """从任意页面导航到 Settings 页面"""
        # 直接通过 URL 导航更可靠
        self.page.goto("https://aepub.58v5.cn/biz/en/user/home?tabindex=1", wait_until="networkidle", timeout=30000)
        self.page.wait_for_timeout(2000)
        
        # 关闭可能弹出的登录对话框（多次尝试）
        for _ in range(3):
            try:
                # 按ESC键
                self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(500)
                
                # 查找并关闭登录弹窗
                close_btn = self.page.locator("button[aria-label='Close'], [class*='closeBtn']").first
                if close_btn.is_visible(timeout=1000):
                    try:
                        self.page.evaluate("(el) => el.click()", close_btn.element_handle())
                    except:
                        close_btn.click(force=True)
                    self.page.wait_for_timeout(1000)
                    
                # 检查是否还有弹窗
                if not self.page.locator("[class*='modal'][role='dialog']").first.is_visible(timeout=500):
                    break
            except:
                break
        
        # 使用 JavaScript 强制清理所有弹窗
        try:
            self.page.evaluate("""
                document.querySelectorAll('[class*="LoginPC"], [class*="loginModal"], [role="dialog"]').forEach(el => {
                    if (el.textContent && (el.textContent.includes('Welcome to OK.com') || 
                        el.textContent.includes('Log in') ||
                        el.textContent.includes('Email or phone number'))) {
                        el.style.display = 'none';
                        el.remove();
                    }
                });
                document.querySelectorAll('.modal-backdrop, [class*="modal-backdrop"]').forEach(el => el.remove());
                document.body.classList.remove('modal-open');
                document.body.style.overflow = '';
            """)
        except:
            pass
        
        self.page.wait_for_timeout(1000)
    
    def scroll_to_new_messages(self):
        """滚动到 New Messages 模块"""
        self.new_messages_title.scroll_into_view_if_needed()
        self.page.wait_for_timeout(500)
    
    def is_new_messages_visible(self) -> bool:
        """检查 New Messages 模块是否可见"""
        return self.new_messages_title.is_visible()
    
    def get_toggle_state(self) -> str:
        """
        获取开关状态
        Returns:
            "enabled" 或 "disabled"
        """
        # 通过检查状态文字判断
        if self.new_messages_enabled_text.is_visible(timeout=2000):
            return "enabled"
        else:
            return "disabled"
    
    def click_toggle(self):
        """点击通知开关，并等待状态更新（接口/UI 可能有延迟）"""
        before_state = self.get_toggle_state()
        try:
            self.page.evaluate("(el) => el.click()", self.new_messages_toggle.element_handle())
        except Exception:
            self.new_messages_toggle.click(force=True)
        self.wait_for_toggle_state_changed(before_state, timeout_ms=8000)
    
    def wait_for_toggle_state_changed(self, from_state: str, timeout_ms: int = 6000) -> str:
        """点击后轮询直到开关状态与 from_state 不同，返回新状态。超时返回当前状态。"""
        poll_interval = 500
        elapsed = 0
        while elapsed < timeout_ms:
            self.page.wait_for_timeout(poll_interval)
            elapsed += poll_interval
            current = self.get_toggle_state()
            if current != from_state:
                return current
        return self.get_toggle_state()
    
    def enable_notifications(self):
        """启用邮件通知（如果未启用）"""
        current_state = self.get_toggle_state()
        if current_state == "disabled":
            self.click_toggle()
    
    def disable_notifications(self):
        """禁用邮件通知（如果已启用）"""
        current_state = self.get_toggle_state()
        if current_state == "enabled":
            self.click_toggle()
    
    def verify_new_messages_module_elements(self):
        """验证 New Messages 模块所有元素都存在"""
        expect(self.new_messages_title).to_be_visible()
        expect(self.new_messages_description).to_be_visible()
        expect(self.new_messages_toggle).to_be_visible()
