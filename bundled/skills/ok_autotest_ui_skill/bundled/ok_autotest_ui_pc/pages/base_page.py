# pages/base_page.py
from playwright.sync_api import Page


class BasePage:
    """页面基类，封装 Playwright 常用操作（静默执行）"""
    
    def __init__(self, page: Page):
        self.page = page
    
    def goto(self, url, timeout=60000, wait_until="domcontentloaded"):
        """
        导航到指定 URL（官方推荐：使用 domcontentloaded + 元素级等待）
        
        Args:
            url: 目标 URL（可以是完整 URL 或相对路径）
            timeout: 超时时间（毫秒），默认 60 秒（跨国站点访问较慢）
            wait_until: 加载策略，默认 domcontentloaded（官方推荐，禁止使用 networkidle）
                       可选值：domcontentloaded/commit（commit 对重定向更宽容）
        
        注意：
        - 官方明确禁止使用 wait_until="load" 或 "networkidle"
        - 导航后应配合元素级等待：page.locator("关键元素").wait_for(state="visible")
        """
        try:
            self.page.goto(url, timeout=timeout, wait_until=wait_until)
        except Exception as e:
            if "ERR_ABORTED" in str(e) and wait_until != "commit":
                # 重定向/资源中断导致，用 commit 重试后等待 dom 就绪
                try:
                    self.page.goto(url, timeout=timeout, wait_until="commit")
                    self.page.wait_for_load_state("domcontentloaded", timeout=15000)
                except Exception:
                    raise e
            else:
                raise
    
    def wait_for_page_load(self, state="load", timeout=30000):
        """
        等待页面加载完成
        
        Args:
            state: 加载状态 (load/domcontentloaded/networkidle)
            timeout: 超时时间（毫秒）
        """
        self.page.wait_for_load_state(state, timeout=timeout)
    
    def wait_for_selector(self, selector, state="visible", timeout=30000):
        """
        等待元素出现
        
        Args:
            selector: 元素选择器
            state: 元素状态 (visible/attached/hidden)
            timeout: 超时时间（毫秒）
        """
        self.page.wait_for_selector(selector, state=state, timeout=timeout)
    
    def wait_for_url(self, url_pattern, timeout=30000):
        """
        等待 URL 匹配指定模式
        
        Args:
            url_pattern: URL 模式（支持通配符）
            timeout: 超时时间（毫秒）
        """
        self.page.wait_for_url(url_pattern, timeout=timeout)

    def wait_for_any_selector(self, selectors, state="visible", timeout=30000):
        """
        依次等待一组候选选择器，直到其中一个满足条件。

        Args:
            selectors: 候选选择器列表
            state: 元素状态 (visible/attached/hidden)
            timeout: 总超时时间（毫秒）

        Returns:
            str: 命中的选择器
        """
        last_error = None
        for selector in selectors:
            try:
                self.page.wait_for_selector(selector, state=state, timeout=timeout)
                return selector
            except Exception as exc:
                last_error = exc
        if last_error:
            raise last_error
        raise ValueError("selectors 不能为空")

    def wait_for_key_section(self, selectors, timeout=30000):
        """
        等待页面关键区块 ready，适合替代大段固定 sleep。
        """
        return self.wait_for_any_selector(selectors, state="visible", timeout=timeout)

    def wait_for_url_ready(self, url_pattern=None, timeout=30000, load_state="domcontentloaded"):
        """
        先等待页面 load_state，再按需等待 URL ready。
        """
        self.page.wait_for_load_state(load_state, timeout=timeout)
        if url_pattern:
            self.page.wait_for_url(url_pattern, timeout=timeout)

    def dismiss_modal_dialogs(self, attempts=3, settle_timeout=200):
        """
        尝试关闭当前页面上的模态弹窗，返回实际关闭尝试次数。
        """
        closed = 0
        for _ in range(attempts):
            dialog = self.page.locator('[role="dialog"][aria-modal="true"]')
            try:
                if dialog.count() == 0 or not dialog.first.is_visible(timeout=500):
                    break
            except Exception:
                break
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(settle_timeout)
            closed += 1
        return closed
    
    def fill(self, selector, text, timeout=30000):
        """
        输入文本
        
        Args:
            selector: 元素选择器
            text: 输入的文本
            timeout: 超时时间（毫秒）
        """
        self.page.fill(selector, text, timeout=timeout)
    
    def click(self, selector, timeout=30000):
        """
        点击元素
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        self.page.click(selector, timeout=timeout)
    
    def get_text(self, selector, timeout=30000):
        """
        获取元素文本
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        
        Returns:
            str: 元素文本内容
        """
        self.page.wait_for_selector(selector, timeout=timeout)
        return self.page.locator(selector).inner_text()
    
    def is_visible(self, selector, timeout=5000):
        """
        判断元素是否可见
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        
        Returns:
            bool: 元素是否可见
        """
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=timeout)
            return True
        except Exception:
            return False
    
    def is_hidden(self, selector, timeout=5000):
        """
        判断元素是否隐藏
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        
        Returns:
            bool: 元素是否隐藏
        """
        try:
            self.page.wait_for_selector(selector, state="hidden", timeout=timeout)
            return True
        except Exception:
            return False
    
    def get_attribute(self, selector, attribute, timeout=30000):
        """
        获取元素属性值
        
        Args:
            selector: 元素选择器
            attribute: 属性名
            timeout: 超时时间（毫秒）
        
        Returns:
            str: 属性值
        """
        self.page.wait_for_selector(selector, timeout=timeout)
        return self.page.locator(selector).get_attribute(attribute)
    
    def select_option(self, selector, value, timeout=30000):
        """
        选择下拉框选项
        
        Args:
            selector: 下拉框选择器
            value: 选项值
            timeout: 超时时间（毫秒）
        """
        self.page.select_option(selector, value, timeout=timeout)
    
    def check(self, selector, timeout=30000):
        """
        勾选复选框/单选框
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        self.page.check(selector, timeout=timeout)
    
    def uncheck(self, selector, timeout=30000):
        """
        取消勾选复选框
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        self.page.uncheck(selector, timeout=timeout)
    
    def hover(self, selector, timeout=30000):
        """
        鼠标悬停
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        self.page.hover(selector, timeout=timeout)
    
    def press(self, selector, key, timeout=30000):
        """
        按下键盘按键
        
        Args:
            selector: 元素选择器
            key: 按键名（Enter/Tab/Escape等）
            timeout: 超时时间（毫秒）
        """
        self.page.press(selector, key, timeout=timeout)
    
    def get_current_url(self):
        """
        获取当前页面 URL
        
        Returns:
            str: 当前 URL
        """
        return self.page.url
    
    def get_title(self):
        """
        获取页面标题
        
        Returns:
            str: 页面标题
        """
        return self.page.title()
    
    def reload(self, timeout=60000):
        """
        刷新页面（使用 domcontentloaded 策略）
        
        Args:
            timeout: 超时时间（毫秒），默认 60 秒
        
        注意：刷新后应配合元素级等待确保页面关键元素加载完成
        """
        self.page.reload(wait_until="domcontentloaded", timeout=timeout)
    
    def go_back(self, timeout=60000):
        """
        后退（使用 domcontentloaded 策略）
        
        Args:
            timeout: 超时时间（毫秒），默认 60 秒
        
        注意：后退后应配合元素级等待确保页面关键元素加载完成
        """
        self.page.go_back(wait_until="domcontentloaded", timeout=timeout)
    
    def go_forward(self, timeout=60000):
        """
        前进（使用 domcontentloaded 策略）
        
        Args:
            timeout: 超时时间（毫秒），默认 60 秒
        
        注意：前进后应配合元素级等待确保页面关键元素加载完成
        """
        self.page.go_forward(wait_until="domcontentloaded", timeout=timeout)
    
    def screenshot(self, path, full_page=False):
        """
        截图
        
        Args:
            path: 保存路径
            full_page: 是否全页面截图
        """
        self.page.screenshot(path=path, full_page=full_page)
