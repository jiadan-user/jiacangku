"""
详情页核心信息区域 Page Object

封装详情页核心信息区域（价格、标题、地点、时间、描述）的元素定位和交互方法
"""
import re
from playwright.sync_api import Page, Locator
from utils.logger import setup_logger

logger = setup_logger()


class DetailPageCoreInfo:
    """详情页核心信息区域"""

    def __init__(self, page: Page):
        self.page = page

    # ========== 价格区域定位器 ==========

    @property
    def price_element(self) -> Locator:
        """价格元素 - 基于录制快照：text: $9.9"""
        # 从快照看到价格是纯文本节点，位于generic [ref=e63]下
        # 尝试多种定位策略
        # 策略1：直接查找$开头后跟数字的文本
        return self.page.locator("text=/^\\$\\d/").first

    def get_price_text(self) -> str:
        """获取价格文本"""
        try:
            # 先尝试使用price_element
            text = self.price_element.inner_text().strip()
            # 提取完整价格（可能只匹配到部分）
            price_match = re.search(r'\$[\d.,]+', text)
            if price_match:
                return price_match.group()
            return text
        except Exception as e:
            logger.warning(f"获取价格文本失败，使用备用方案: {e}")
            # 备用方案：直接在页面body中搜索价格模式
            try:
                page_text = self.page.locator("body").inner_text()
                # 查找第一个$价格（排除Free Delivery等干扰）
                lines = page_text.split('\n')
                for line in lines[:20]:  # 只搜索前20行（价格通常在顶部）
                    line = line.strip()
                    if re.match(r'^\$[\d.,]+$', line):
                        return line
            except:
                pass
            return ""

    def is_price_visible(self) -> bool:
        """检查价格是否可见"""
        try:
            return self.price_element.is_visible(timeout=5000)
        except:
            # 备用方案：检查页面是否包含价格
            try:
                page_text = self.page.locator("body").inner_text()
                return bool(re.search(r'\$[\d.,]+', page_text[:1000]))
            except:
                return False

    # ========== 标题区域定位器 ==========

    @property
    def title_element(self) -> Locator:
        """标题元素 - 基于录制快照：heading level=1"""
        # 从快照看到: heading "Homemade LED..." [level=1] [ref=e73]
        return self.page.locator("h1").first

    def get_title_text(self) -> str:
        """获取标题文本"""
        try:
            return self.title_element.inner_text().strip()
        except Exception as e:
            logger.warning(f"获取标题文本失败: {e}")
            return ""

    def is_title_visible(self) -> bool:
        """检查标题是否可见"""
        try:
            return self.title_element.is_visible(timeout=5000)
        except:
            return False
    
    def get_title_length(self) -> int:
        """获取标题字符长度"""
        return len(self.get_title_text())

    # ========== 地点区域定位器 ==========

    @property
    def location_element(self) -> Locator:
        """地点元素 - 基于录制快照：带address图标的generic容器"""
        # 从快照看到: generic [ref=e74] 包含 img "address" + text: United States
        # 定位策略：查找包含address图标的generic（位于h1后面）
        # 使用更稳健的定位方式：查找包含address图标的任意元素
        return self.page.locator("img[alt='address']").locator("..").first

    @property
    def location_text_only(self) -> Locator:
        """地点纯文本元素（不包含图标）"""
        # 地点文本在img之后
        return self.location_element.locator("text").first

    def get_location_text(self) -> str:
        """获取地点文本"""
        try:
            # 获取整个容器的文本，会包含图标后的地点名称
            return self.location_element.inner_text().strip()
        except Exception as e:
            logger.warning(f"获取地点文本失败: {e}")
            return ""

    def is_location_visible(self) -> bool:
        """检查地点是否可见"""
        try:
            return self.location_element.is_visible(timeout=5000)
        except:
            return False
    
    def get_location_icon(self) -> Locator:
        """获取地点图标元素"""
        return self.page.locator("img[alt='address']").first

    # ========== 发布时间区域定位器 ==========

    @property
    def publish_time_element(self) -> Locator:
        """发布时间元素 - 基于录制快照：generic包含时间文本"""
        # 从快照看到: generic [ref=e78]: Updated 1 month ago
        # 位于location元素（img[alt='address']的父元素）之后
        # 使用文本模式定位：查找包含时间关键词的generic
        return self.page.locator("text=/Updated|ago|Posted|Published/i").first

    def get_publish_time_text(self) -> str:
        """获取发布时间文本"""
        try:
            return self.publish_time_element.inner_text().strip()
        except Exception as e:
            logger.warning(f"获取发布时间文本失败: {e}")
            return ""

    def is_publish_time_visible(self) -> bool:
        """检查发布时间是否可见"""
        try:
            return self.publish_time_element.is_visible(timeout=5000)
        except:
            return False

    # ========== 描述区域定位器 ==========

    @property
    def description_section(self) -> Locator:
        """描述区域容器（包含"Description"标题和内容）"""
        # 从快照看到描述在separator之后
        # 使用文本"Description"定位容器
        return self.page.locator("text=Description").locator("..").first

    @property
    def description_title(self) -> Locator:
        """描述标题（"Description"文本）"""
        return self.page.locator("text=Description").first

    @property
    def description_element(self) -> Locator:
        """描述内容元素 - 基于录制快照：paragraph包含长文本描述"""
        # 使用CSS选择器：找到所有p标签中，文本长度最可能是描述的
        # 简化方案：使用nth定位，跳过前面的短paragraph
        # 通常描述是页面中较后面的、较长的paragraph
        # 尝试多个策略
        # 策略1：查找包含"DIY"或其他常见描述关键词的p（针对当前测试数据）
        desc_with_keywords = self.page.locator("p").filter(has_text=re.compile(r'.{50,}', re.DOTALL))
        if desc_with_keywords.count() > 0:
            return desc_with_keywords.first
        
        # 策略2：返回所有p中的第3个（跳过Free Delivery等短文本）
        return self.page.locator("p").nth(2)

    def get_description_text(self) -> str:
        """获取描述文本"""
        try:
            return self.description_element.inner_text()
        except Exception as e:
            logger.warning(f"获取描述文本失败: {e}")
            return ""

    def is_description_visible(self) -> bool:
        """检查描述是否可见"""
        try:
            return self.description_element.is_visible(timeout=5000)
        except:
            return False

    @property
    def description_expand_button(self) -> Locator:
        """描述展开按钮（如果有）"""
        return self.page.get_by_role("button", name="Read more").or_(
            self.page.get_by_role("button", name="Show more")
        )

    def click_description_expand(self):
        """点击展开描述"""
        try:
            if self.description_expand_button.is_visible(timeout=3000):
                self.description_expand_button.click()
                self.page.wait_for_timeout(500)
                logger.info("✓ 已点击展开描述按钮")
        except Exception as e:
            logger.info("描述展开按钮不存在或已展开")
    
    def get_description_length(self) -> int:
        """获取描述字符长度"""
        return len(self.get_description_text())

    # ========== 辅助方法 ==========

    def wait_page_load(self, timeout: int = 30000):
        """等待详情页加载完成"""
        logger.info("等待详情页加载完成...")
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        self.page.wait_for_timeout(2000)
        logger.info("✓ 详情页加载完成")

    def get_all_core_info(self) -> dict:
        """获取所有核心信息"""
        return {
            "price": self.get_price_text(),
            "title": self.get_title_text(),
            "location": self.get_location_text(),
            "publish_time": self.get_publish_time_text(),
            "description": self.get_description_text(),
        }

    def verify_core_elements_visible(self) -> dict:
        """验证核心元素可见性"""
        return {
            "price_visible": self.is_price_visible(),
            "title_visible": self.is_title_visible(),
            "location_visible": self.is_location_visible(),
            "publish_time_visible": self.is_publish_time_visible(),
            "description_visible": self.is_description_visible(),
        }
