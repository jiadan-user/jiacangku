# pages/breadcrumb_page.py
from pages.base_page import BasePage
from utils.logger import setup_logger
from typing import List, Optional


class BreadcrumbPage(BasePage):
    """详情页面包屑导航页面对象"""
    
    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()
    
    # ========== 面包屑选择器 ==========
    BREADCRUMB_NAV = ".Breadcrumb_breadcrumb__nKH2A"
    BREADCRUMB_ITEMS = ".Breadcrumb_breadcrumbItem__R0lp7"
    BREADCRUMB_LINKS = ".Breadcrumb_breadcrumbLink__7juPR"
    BREADCRUMB_ARROWS = ".Breadcrumb_arrow__CBW9C"
    BREADCRUMB_CURRENT_SPAN = ".Breadcrumb_breadcrumbSpan__B3vYJ"
    
    # ========== 基础方法 ==========
    
    def is_breadcrumb_visible(self, timeout=10000):
        """检查面包屑导航是否可见"""
        try:
            return self.page.locator(self.BREADCRUMB_NAV).first.is_visible(timeout=timeout)
        except Exception:
            return False
    
    def get_breadcrumb_items_count(self):
        """获取面包屑节点总数"""
        try:
            return self.page.locator(self.BREADCRUMB_ITEMS).count()
        except Exception as e:
            self.logger.error(f"获取面包屑节点数量失败: {e}")
            return 0
    
    def get_breadcrumb_items_text(self) -> List[str]:
        """获取所有面包屑节点的文本"""
        try:
            items = self.page.locator(self.BREADCRUMB_ITEMS).all()
            return [item.inner_text().strip() for item in items]
        except Exception as e:
            self.logger.error(f"获取面包屑节点文本失败: {e}")
            return []
    
    def get_breadcrumb_links_count(self):
        """获取可点击链接的数量"""
        try:
            return self.page.locator(self.BREADCRUMB_LINKS).count()
        except Exception as e:
            self.logger.error(f"获取面包屑链接数量失败: {e}")
            return 0
    
    def get_breadcrumb_arrows_count(self):
        """获取箭头分隔符的数量"""
        try:
            return self.page.locator(self.BREADCRUMB_ARROWS).count()
        except Exception as e:
            self.logger.error(f"获取箭头数量失败: {e}")
            return 0
    
    def click_breadcrumb_item(self, text: str):
        """点击指定文本的面包屑节点"""
        try:
            link = self.page.locator(self.BREADCRUMB_LINKS, has_text=text).first
            link.click()
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            self.logger.info(f"✓ 点击面包屑节点: {text}")
        except Exception as e:
            self.logger.error(f"点击面包屑节点失败 [{text}]: {e}")
            raise
    
    def get_breadcrumb_item_href(self, text: str) -> Optional[str]:
        """获取指定文本节点的 href 属性"""
        try:
            link = self.page.locator(self.BREADCRUMB_LINKS, has_text=text).first
            return link.get_attribute("href")
        except Exception as e:
            self.logger.error(f"获取面包屑链接 href 失败 [{text}]: {e}")
            return None
    
    def is_last_item_clickable(self) -> bool:
        """检查最后一个节点是否可点击（是否为链接）"""
        try:
            last_item = self.page.locator(self.BREADCRUMB_ITEMS).last
            has_link = last_item.locator("a").count() > 0
            return has_link
        except Exception:
            return False
    
    def is_last_item_span(self) -> bool:
        """检查最后一个节点是否为 span 元素"""
        try:
            last_item = self.page.locator(self.BREADCRUMB_ITEMS).last
            has_span = last_item.locator("span").count() > 0
            return has_span
        except Exception:
            return False
    
    def get_last_item_text(self) -> str:
        """获取最后一个节点的文本"""
        try:
            last_item = self.page.locator(self.BREADCRUMB_ITEMS).last
            return last_item.inner_text().strip()
        except Exception as e:
            self.logger.error(f"获取最后一个节点文本失败: {e}")
            return ""
    
    def hover_breadcrumb_item(self, text: str):
        """悬停在指定文本的面包屑节点上"""
        try:
            link = self.page.locator(self.BREADCRUMB_LINKS, has_text=text).first
            link.hover()
            self.page.wait_for_timeout(500)
            self.logger.info(f"✓ 悬停在面包屑节点: {text}")
        except Exception as e:
            self.logger.error(f"悬停失败 [{text}]: {e}")
            raise
    
    def get_breadcrumb_position(self) -> dict:
        """获取面包屑导航的位置信息"""
        try:
            return self.page.evaluate(f'''() => {{
                const nav = document.querySelector('{self.BREADCRUMB_NAV}');
                if (!nav) return null;
                
                const rect = nav.getBoundingClientRect();
                return {{
                    top: rect.top,
                    left: rect.left,
                    width: rect.width,
                    height: rect.height
                }};
            }}''')
        except Exception as e:
            self.logger.error(f"获取面包屑位置失败: {e}")
            return {}
    
    def get_breadcrumb_link_style(self, text: str) -> dict:
        """获取指定链接的样式信息"""
        try:
            return self.page.evaluate(f'''() => {{
                const links = Array.from(document.querySelectorAll('{self.BREADCRUMB_LINKS}'));
                const link = links.find(el => el.innerText.includes('{text}'));
                
                if (!link) return null;
                
                const style = window.getComputedStyle(link);
                return {{
                    color: style.color,
                    fontSize: style.fontSize,
                    textDecoration: style.textDecoration,
                    cursor: style.cursor
                }};
            }}''')
        except Exception as e:
            self.logger.error(f"获取链接样式失败 [{text}]: {e}")
            return {}
    
    def get_breadcrumb_path(self) -> str:
        """获取面包屑路径字符串"""
        try:
            items_text = self.get_breadcrumb_items_text()
            return " > ".join(items_text)
        except Exception:
            return ""
