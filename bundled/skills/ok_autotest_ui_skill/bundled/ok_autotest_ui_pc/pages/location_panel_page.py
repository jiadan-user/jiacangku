# pages/location_panel_page.py
"""
定位面板页面对象模型 (Page Object Model)
封装定位面板的所有元素定位和操作
"""
from playwright.sync_api import Page
from pages.base_page import BasePage


class LocationPanelPage(BasePage):
    """定位面板页面类"""
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # ========== 元素定位器 (Locators) ==========
        # 定位图标（地图标记） - 使用更精确的选择器策略
        # 优先使用包含图标的可点击区域
        self.location_icon = ".TopBarRightContent_locationModule__i97Cs"
        # 备用选择器：通过图标图片来定位
        self.location_icon_by_img = "img[alt='location icon']"
        # 备用选择器：通过父容器和图标组合
        self.location_icon_container = ".TopBarRightContent_right__2OKOg .TopBarRightContent_locationModule__i97Cs"
        
        # 定位面板容器（打开后的弹出层）- 使用role=tooltip
        self.location_panel = "[role='tooltip']"
        
        # 搜索框
        self.search_input = "input[placeholder*='Search City' i]"
        
        # 当前位置 - 通过img[alt="location"]来定位，它通常旁边显示当前城市
        self.current_location = "[role='tooltip'] img[alt='location']"
        
        # "Near me" 链接
        self.near_me_link = "text='Near me'"
        
        # Used Locations 部分（使用 QuickCities 组件）
        self.used_locations_section = "text='Used Locations'"
        self.used_locations_cities = "[role='tooltip'] [class*='QuickCities_tag']"
        
        # Top Cities 部分（使用 QuickCities 组件）
        self.top_cities_section = "text='Top Cities'"
        self.top_cities_list = "[role='tooltip'] [class*='QuickCities_tag']"
        
        # 字母索引导航 - 在tooltip内查找字母按钮
        self.alphabet_nav = "[role='tooltip'] >> text='A'"  # 第一个字母A作为代表
        
        # 城市列表 - 查找Abu Dhabi作为代表
        self.cities_list = "[role='tooltip'] >> text='Abu Dhabi'"
        self.city_item = "[role='tooltip'] button"  # 城市按钮
    
    # ========== 操作方法 (Actions) ==========
    
    def click_location_icon(self, timeout=20000, max_retries=3):
        """
        点击定位图标打开定位面板
        适配无头模式：增加等待、滚动处理和重试机制
        
        Args:
            timeout: 超时时间（毫秒）
            max_retries: 最大重试次数
        """
        # 1. 等待页面DOM加载完成
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        except Exception:
            pass
        
        # 2. 尝试等待 networkidle（可选）
        try:
            self.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        
        # 3. 滚动到页面顶部
        self.page.evaluate("window.scrollTo(0, 0)")
        self.page.wait_for_timeout(2000)
        
        # 尝试多次点击定位图标打开面板
        for attempt in range(max_retries):
            try:
                # 策略：优先使用语义化选择器，回退到CSS选择器
                # 注意：定位图标可能在页面上出现多次（如移动端和桌面端），需要找到正确的那个
                
                # 方法1：尝试通过 CSS 选择器找到可见的定位图标
                all_icons = self.page.locator(self.location_icon)
                count = all_icons.count()
                
                location_icon_clicked = False
                
                # 尝试所有匹配的元素，找到第一个可见的
                for i in range(count):
                    try:
                        icon = all_icons.nth(i)
                        box = icon.bounding_box(timeout=2000)
                        
                        # 检查是否在顶部区域且可见
                        if box and box['y'] < 150 and box['width'] > 0:
                            icon.scroll_into_view_if_needed(timeout=5000)
                            self.page.wait_for_timeout(500)
                            # 使用 force=True 强制点击
                            icon.click(timeout=5000, force=True)
                            location_icon_clicked = True
                            break
                    except Exception:
                        continue
                
                if not location_icon_clicked:
                    # 如果所有元素都不可见，尝试通过图片定位
                    location_imgs = self.page.locator("img[alt*='location' i], img[src*='location' i]")
                    img_count = location_imgs.count()
                    
                    for i in range(img_count):
                        try:
                            img = location_imgs.nth(i)
                            box = img.bounding_box(timeout=2000)
                            if box and box['y'] < 150:
                                img.scroll_into_view_if_needed(timeout=5000)
                                self.page.wait_for_timeout(500)
                                img.click(timeout=5000, force=True)
                                location_icon_clicked = True
                                break
                        except Exception:
                            continue
                
                if not location_icon_clicked:
                    raise Exception(f"未找到可点击的定位图标（尝试{attempt+1}/{max_retries}）")
                
                # 等待面板打开 - 多重验证策略
                self.page.wait_for_timeout(2000)
                
                # 策略1：等待搜索框可见
                search_box = self.page.locator(self.search_input)
                try:
                    search_box.wait_for(state="visible", timeout=10000)
                    return  # 成功
                except Exception:
                    pass
                
                # 策略2：等待包含搜索框的tooltip
                try:
                    panel_with_search = self.page.locator(f"[role='tooltip']:has({self.search_input})")
                    panel_with_search.wait_for(state="visible", timeout=8000)
                    return  # 成功
                except Exception:
                    pass
                
                # 策略3：JavaScript检查
                try:
                    self.page.wait_for_function(
                        """() => {
                            const tooltips = document.querySelectorAll('[role="tooltip"]');
                            for (const tooltip of tooltips) {
                                const searchInput = tooltip.querySelector('input[placeholder*="Search" i]');
                                if (searchInput && tooltip.offsetParent !== null) {
                                    return true;
                                }
                            }
                            return false;
                        }""",
                        timeout=8000
                    )
                    return  # 成功
                except Exception:
                    if attempt < max_retries - 1:
                        # 重试前先等待
                        self.page.wait_for_timeout(2000)
                        continue
                    else:
                        raise
                        
            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(
                        f"定位面板未能在 {timeout}ms 内打开（已重试{max_retries}次）。"
                        f"最后错误: {e}"
                    )
                self.page.wait_for_timeout(2000)
    
    def click_location_icon_by_selector(self, timeout=10000):
        """
        通过选择器点击定位图标（备用方法）
        
        Args:
            timeout: 超时时间（毫秒）
        """
        self.click(self.location_icon, timeout=timeout)
        self.wait_for_selector(self.location_panel, timeout=timeout)
    
    def is_location_panel_open(self, timeout=5000):
        """
        判断定位面板是否打开
        
        Args:
            timeout: 超时时间（毫秒）
        
        Returns:
            bool: 面板是否打开
        """
        try:
            # 优先检查搜索框（更稳定）
            if self.page.locator(self.search_input).is_visible(timeout=timeout):
                return True
        except Exception:
            pass
        # 回退到检查 tooltip role
        return self.is_visible(self.location_panel, timeout=timeout)
    
    def is_location_panel_closed(self, timeout=5000):
        """
        判断定位面板是否关闭
        
        Args:
            timeout: 超时时间（毫秒）
        
        Returns:
            bool: 面板是否关闭
        """
        return self.is_hidden(self.location_panel, timeout=timeout)
    
    def select_city_from_top_cities(self, city_name, timeout=10000):
        """
        从Top Cities选择城市
        
        Args:
            city_name: 城市名称（如 "Dubai", "Abu Dhabi"）
            timeout: 超时时间（毫秒）
        """
        # 定位到Top Cities区域，然后找到QuickCities_tagText元素（最内层的包含城市名的div）
        top_cities_container = self.page.locator("[role='tooltip']").locator("text='Top Cities'").locator("..")
        city_text = top_cities_container.locator("[class*='QuickCities_tagText']", has_text=city_name)
        city_text.click(timeout=timeout)
        # 等待URL更新
        self.page.wait_for_timeout(1000)
    
    def select_city_from_used_locations(self, city_name, timeout=10000):
        """
        从Used Locations选择城市
        
        Args:
            city_name: 城市名称（如 "Dubai", "Abu Dhabi"）
            timeout: 超时时间（毫秒）
        """
        # 定位到Used Locations区域，然后找到QuickCities_tagText元素
        used_locations_container = self.page.locator("[role='tooltip']").locator("text='Used Locations'").locator("..")
        city_text = used_locations_container.locator("[class*='QuickCities_tagText']", has_text=city_name)
        city_text.click(timeout=timeout)
        self.page.wait_for_timeout(1000)
    
    def select_city_from_all_cities(self, city_name, timeout=10000):
        """
        从All Cities列表选择城市
        
        Args:
            city_name: 城市名称（如 "Abu Dhabi", "Dubai"）
            timeout: 超时时间（毫秒）
        """
        # 使用span标签匹配城市名
        city_item = f"span:has-text('{city_name}')"
        self.click(city_item, timeout=timeout)
        self.page.wait_for_timeout(1000)
    
    def click_outside_panel(self):
        """
        点击面板外部区域关闭面板
        """
        # 点击页面左侧空白区域（坐标在面板外）
        self.page.mouse.click(200, 400)
        self.page.wait_for_timeout(500)
    
    def search_city(self, city_name, timeout=10000):
        """
        在搜索框中搜索城市
        
        Args:
            city_name: 城市名称
            timeout: 超时时间（毫秒）
        """
        self.fill(self.search_input, city_name, timeout=timeout)
        self.page.wait_for_timeout(500)
    
    def get_current_city_from_url(self):
        """
        从URL获取当前城市名称
        
        Returns:
            str: 城市名称（小写）如 "dubai", "abu-dhabi"
        """
        url = self.get_current_url()
        # URL格式: https://ae.ok.com/en/city-dubai/ 或 https://ae.ok.com/en/city-abu-dhabi/
        if "/city-" in url:
            city_part = url.split("/city-")[1].rstrip("/")
            return city_part
        return None
    
    def verify_page_title_contains(self, expected_text, timeout=10000):
        """
        验证页面标题包含指定文本
        
        Args:
            expected_text: 期望包含的文本
            timeout: 超时时间（毫秒）
        
        Returns:
            bool: 是否包含
        """
        self.page.wait_for_timeout(1000)  # 等待标题更新
        title = self.get_title()
        return expected_text in title
    
    # ========== 验证方法 (Assertions) ==========
    
    def verify_location_panel_elements(self):
        """
        验证定位面板的所有关键元素是否存在
        
        Returns:
            dict: 各元素的可见性状态
        """
        return {
            "search_input": self.is_visible(self.search_input, timeout=3000),
            "current_location": self.is_visible(self.current_location, timeout=3000),
            "near_me_link": self.is_visible(self.near_me_link, timeout=3000),
            "top_cities_section": self.is_visible(self.top_cities_section, timeout=3000),
            "alphabet_nav": self.is_visible(self.alphabet_nav, timeout=3000),
            "cities_list": self.is_visible(self.cities_list, timeout=3000)
        }
    
    def has_used_locations_section(self):
        """
        判断是否有Used Locations部分
        
        Returns:
            bool: 是否存在Used Locations
        """
        return self.is_visible(self.used_locations_section, timeout=2000)
