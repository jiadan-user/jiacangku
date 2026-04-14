# pages/site_selection_page.py
from pages.base_page import BasePage
from utils.logger import setup_logger


class SiteSelectionPage(BasePage):
    """OK.com 地区选择页面对象"""

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    # ========== 页面操作方法（静默执行）==========

    def navigate_to_site_selection_page(self):
        """导航到地区选择页面"""
        try:
            self.goto("https://www.ok.com/biz/en/site", timeout=30000)
            self.wait_for_page_load()
        except Exception as e:
            self.logger.error(f"打开地区选择页面失败: {e}")
            raise

    def click_country_link(self, country_name: str):
        """
        点击指定国家/地区链接
        
        Args:
            country_name: 国家/地区名称（如 "United States", "香港", "الإمارات العربية المتحدة"）
        """
        try:
            self.page.get_by_role("link", name=country_name).click()
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception as e:
            self.logger.error(f"点击国家链接 '{country_name}' 失败: {e}")
            raise

    def get_page_title(self) -> str:
        """获取当前页面标题"""
        try:
            return self.page.title()
        except Exception as e:
            self.logger.error(f"获取页面标题失败: {e}")
            raise

    def get_current_url(self) -> str:
        """获取当前页面URL"""
        try:
            return self.page.url
        except Exception as e:
            self.logger.error(f"获取页面URL失败: {e}")
            raise

    def get_all_country_links(self) -> list:
        """
        获取页面上所有国家/地区链接的信息
        
        Returns:
            包含 {text, url} 的字典列表
        """
        try:
            # 第1层：等待DOM完全加载
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            
            # 第2层：等待关键元素出现（至少有一个国家链接）
            self.page.wait_for_selector("a[href*='ok.com']", state="visible", timeout=10000)
            
            # 第3层：额外等待确保所有元素渲染完成
            self.page.wait_for_timeout(800)
            
            result = self.page.evaluate("""
                () => {
                    const links = Array.from(document.querySelectorAll('a[href*="ok.com"]'));
                    return links.map(link => ({
                        text: link.textContent.trim(),
                        url: link.href
                    })).filter(item => item.url.match(/^https:\\/\\/[a-z]{2}\\.ok\\.com\\/?$/));
                }
            """)
            return result
        except Exception as e:
            self.logger.error(f"获取国家链接列表失败: {e}")
            raise

    def count_country_links(self) -> int:
        """统计页面上的国家/地区链接数量"""
        try:
            links = self.get_all_country_links()
            return len(links)
        except Exception as e:
            self.logger.error(f"统计国家链接数量失败: {e}")
            raise

    def verify_url_format(self, url: str, country_code: str) -> bool:
        """
        验证URL格式是否符合标准
        
        Args:
            url: 要验证的URL
            country_code: 国家代码（如 "us", "ae", "hk"）
            
        Returns:
            True 如果格式正确，否则 False
        """
        try:
            expected_pattern = f"https://{country_code}.ok.com"
            return url.startswith(expected_pattern)
        except Exception as e:
            self.logger.error(f"验证URL格式失败: {e}")
            raise

    def get_main_title_text(self) -> str:
        """获取页面主标题文本"""
        try:
            # 主标题包含 "Please select the country and region"
            title_element = self.page.locator("text=Please select the country and region")
            return title_element.inner_text()
        except Exception as e:
            self.logger.error(f"获取主标题失败: {e}")
            raise

    def get_subtitle_text(self) -> str:
        """获取页面副标题文本"""
        try:
            subtitle = self.page.locator("text=Explore your community below")
            return subtitle.inner_text()
        except Exception as e:
            self.logger.error(f"获取副标题失败: {e}")
            raise

    def is_logo_visible(self) -> bool:
        """检查Logo是否可见"""
        try:
            # Logo 通常是一个图片或 SVG
            logo = self.page.locator("img[alt*='logo'], svg, img").first
            return logo.is_visible(timeout=3000)
        except Exception as e:
            self.logger.error(f"检查Logo可见性失败: {e}")
            return False

    def is_main_title_centered(self) -> bool:
        """检查主标题是否居中显示"""
        try:
            result = self.page.evaluate("""
                () => {
                    const element = document.evaluate(
                        "//*[contains(text(), 'Please select the country')]",
                        document,
                        null,
                        XPathResult.FIRST_ORDERED_NODE_TYPE,
                        null
                    ).singleNodeValue;
                    if (!element) return false;
                    const parent = element.parentElement || element;
                    const style = window.getComputedStyle(parent);
                    return style.textAlign === 'center';
                }
            """)
            return result
        except Exception as e:
            self.logger.error(f"检查标题居中失败: {e}")
            return False

    def get_country_link_elements(self):
        """获取所有国家链接元素"""
        try:
            # 直接使用已有的 get_all_country_links 方法获取链接信息
            all_links = self.get_all_country_links()
            
            # 为每个链接创建 locator
            link_elements = []
            for link_info in all_links:
                country_text = link_info["text"]
                # 使用 get_by_role 找到对应的链接元素
                link_locator = self.page.get_by_role("link", name=country_text)
                link_elements.append(link_locator)
            
            return link_elements
        except Exception as e:
            self.logger.error(f"获取国家链接元素失败: {e}")
            raise

    def is_country_link_visible(self, link_element) -> bool:
        """检查国家链接是否可见"""
        try:
            return link_element.is_visible(timeout=3000)
        except Exception:
            return False

    def has_flag_icon(self, link_element) -> bool:
        """检查链接是否包含国旗图标"""
        try:
            # 国旗图标通常是 img 或 SVG
            flag_icon = link_element.locator("img, svg").first
            return flag_icon.is_visible(timeout=2000)
        except Exception:
            return False

    def get_page_load_time(self) -> float:
        """获取页面加载时间（毫秒）"""
        try:
            load_time = self.page.evaluate("""
                () => {
                    const timing = performance.timing;
                    return timing.domContentLoadedEventEnd - timing.navigationStart;
                }
            """)
            return load_time
        except Exception as e:
            self.logger.error(f"获取页面加载时间失败: {e}")
            raise
