# utils/session_manager.py
"""
Session 管理工具
用于保存和复用浏览器 Cookie，避免每个测试用例重复登录
"""
import json
from pathlib import Path
from playwright.sync_api import Page, BrowserContext
from utils.logger import setup_logger

logger = setup_logger()


class SessionManager:
    """Session 管理器：保存和加载浏览器 Cookie"""
    
    # Session 文件存储目录
    SESSION_DIR = Path("reports/sessions")
    
    def __init__(self, page: Page, base_url: str, session_name: str = "default"):
        """
        初始化 Session 管理器
        
        Args:
            page: Playwright Page 对象
            base_url: 网站基础URL
            session_name: Session 名称（用于区分不同站点/账号）
        """
        self.page = page
        self.context: BrowserContext = page.context
        self.base_url = base_url
        self.session_name = session_name
        
        # 确保 Session 目录存在
        self.SESSION_DIR.mkdir(parents=True, exist_ok=True)
        
        # Session 文件路径
        self.session_file = self.SESSION_DIR / f"{session_name}_session.json"
    
    def save_session(self):
        """
        保存当前浏览器 Cookie 到文件
        
        Returns:
            bool: 保存成功返回 True，失败返回 False
        """
        try:
            # 获取当前所有 Cookie
            cookies = self.context.cookies()
            
            if not cookies:
                logger.error("没有可保存的 Cookie")
                return False
            
            # 保存到文件
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Session 已保存到: {self.session_file}")
            return True
            
        except Exception as e:
            logger.error(f"保存 Session 失败: {e}")
            return False
    
    def load_session(self) -> bool:
        """
        从文件加载 Cookie 到浏览器
        
        Returns:
            bool: 加载成功返回 True，失败或文件不存在返回 False
        """
        try:
            # 检查 Session 文件是否存在
            if not self.session_file.exists():
                logger.debug(f"Session 文件不存在: {self.session_file}")
                return False
            
            # 读取 Cookie
            with open(self.session_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            if not cookies:
                logger.debug("Session 文件为空")
                return False

            try:
                self.context.clear_cookies()
            except Exception:
                pass
            self.context.add_cookies(cookies)
            
            logger.debug(f"Session 已加载: {self.session_file}")
            return True
            
        except Exception as e:
            logger.error(f"加载 Session 失败: {e}")
            return False
    
    def clear_session(self):
        """清除已保存的 Session 文件和浏览器当前的所有存储"""
        try:
            # 清除浏览器当前的所有 Cookie
            self.context.clear_cookies()
            logger.debug("浏览器 Cookie 已清除")
            
            # 清除 LocalStorage 和 SessionStorage
            try:
                self.page.evaluate("""() => {
                    try { localStorage.clear(); } catch(e) {}
                    try { sessionStorage.clear(); } catch(e) {}
                }""")
                logger.debug("LocalStorage 和 SessionStorage 已清除")
            except Exception as e:
                logger.debug(f"清除 Storage 时出错（可能页面未加载）: {e}")
            
            # 删除 Session 文件
            if self.session_file.exists():
                self.session_file.unlink()
                logger.debug(f"Session 文件已删除: {self.session_file}")
        except Exception as e:
            logger.error(f"清除 Session 失败: {e}")
    
    def is_logged_in(self, check_element_selector: str = None) -> bool:
        """
        检查是否已登录
        
        Args:
            check_element_selector: 用于验证登录状态的元素选择器（如用户头像）
        
        Returns:
            bool: 已登录返回 True，未登录返回 False
        """
        try:
            # 如果提供了检查元素，验证该元素是否存在
            if check_element_selector:
                return self.page.locator(check_element_selector).is_visible(timeout=3000)
            
            # 默认检查 URL 是否包含 login
            current_url = self.page.url
            return "login" not in current_url.lower()
            
        except Exception:
            return False

