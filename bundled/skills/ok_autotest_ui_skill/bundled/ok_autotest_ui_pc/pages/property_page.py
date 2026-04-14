# pages/property_page.py
from pages.base_page import BasePage
from utils.logger import setup_logger


class PropertyPage(BasePage):
    """Property 房产页面对象（静默执行）"""
    
    # ========== 页面元素选择器（Playwright 语法）==========
    # Cookie 弹窗相关
    COOKIE_ACCEPT_BUTTON = "button:has-text('Accept all')"
    COOKIE_SETTINGS_TEXT = "text=Cookie settings"
    
    # Property 链接/按钮
    PROPERTY_LINK = "a:has-text('Property'), link:has-text('Property'), button:has-text('Property')"
    PROPERTY_BUTTON = "button:has-text('Property'), [class*='category']:has-text('Property'), [class*='button']:has-text('Property')"
    
    # Property Type 筛选项
    PROPERTY_TYPE_FILTER = "text=Property Type"
    
    # Category 弹窗相关
    CATEGORY_MODAL = "[role='dialog'], .modal, [class*='modal'], [class*='dialog']"
    CATEGORY_THIRD_LEVEL_ITEMS = "[class*='category'], [class*='item'], [class*='option']"
    DONE_BUTTON = "button:has-text('Done')"
    MODAL_CLOSE_BUTTON = "[role='dialog'] button[aria-label='Close'], [role='dialog'] button:has-text('×'), [role='dialog'] button:has-text('X'), .modal button.close, [class*='modal'] [class*='close']"
    
    # 筛选结果回显
    PROPERTY_TYPE_SELECTED_DISPLAY = "text=/Property Type:/i"
    FILTER_TAG = "[class*='tag'], [class*='chip'], [class*='filter-tag']"
    
    # 排序相关
    SORT_BUTTON = "text=Best Match, text=Newest First, text=Lowest Price, text=Highest Price"
    SORT_OPTION_BEST_MATCH = "text=Best Match"
    SORT_OPTION_NEWEST_FIRST = "text=Newest First"
    SORT_OPTION_LOWEST_PRICE = "text=Lowest Price"
    SORT_OPTION_HIGHEST_PRICE = "text=Highest Price"
    SORT_MODAL_DONE_BUTTON = "button:has-text('Done')"
    SORT_MODAL_CLEAR_BUTTON = "button:has-text('Clear')"
    
    # Price 筛选相关
    PRICE_FILTER = "text=Price"
    PRICE_MIN_INPUT = "input[placeholder='Min'], textbox:has-text('Min')"
    PRICE_MAX_INPUT = "input[placeholder='Max'], textbox:has-text('Max')"
    PRICE_DONE_BUTTON = "button:has-text('Done')"
    PRICE_CLEAR_BUTTON = "button:has-text('Clear')"
    PRICE_FILTER_TAG = "text=/Price:/i"
    PRICE_ERROR_MESSAGE = "text=/Max price must be higher than min price/i, [class*='error'], [class*='warning']"
    PRICE_MODAL = "[role='dialog'], .modal, [class*='modal']"
    
    # Beds 筛选相关
    BEDS_FILTER = "text=Beds"
    BEDS_DONE_BUTTON = "button:has-text('Done')"
    BEDS_CLEAR_BUTTON = "button:has-text('Clear')"
    BEDS_FILTER_TAG = "text=/Beds:/i"
    
    # Bathrooms 筛选相关
    BATHROOMS_FILTER = "text=Bathrooms"
    BATHROOMS_DONE_BUTTON = "button:has-text('Done')"
    BATHROOMS_CLEAR_BUTTON = "button:has-text('Clear')"
    BATHROOMS_FILTER_TAG = "text=/Bathrooms:/i"
    
    # Filter 综合筛选相关
    FILTER_BUTTON = "text=Filter"
    FILTER_MODAL = "[role='dialog'], .modal, [class*='modal']"
    FILTER_MODAL_DONE_BUTTON = "button:has-text('Done')"
    FILTER_MODAL_CLEAR_BUTTON = "button:has-text('Clear')"
    FILTER_DISPLAY = "text=/Filter·/i"
    
    # ========== 搜索框相关（Property Buy）==========
    SEARCH_INPUT = "input[placeholder='Search for anything']"
    SEARCH_BUTTON = "button:has-text('Search')"
    SEARCH_CLEAR_ICON = "input[placeholder='Search for anything'] ~ button, input[placeholder='Search for anything'] + *"
    
    # 搜索分类下拉（根据用户截图优化）
    # 位置：搜索框左侧，显示 "Rent" 或 "Sale" 带下拉箭头
    CATEGORY_DROPDOWN_BUTTON = """
        button:has-text('Rent'),
        button:has-text('Sale'),
        [class*='category'] button:has-text('Rent'),
        [class*='category'] button:has-text('Sale'),
        [class*='PropertyTopBar'] button:has-text('Rent'),
        [class*='PropertyTopBar'] button:has-text('Sale')
    """.replace('\n', ' ').strip()
    # 下拉菜单项
    CATEGORY_DROPDOWN_MENU = """
        [role='menu'],
        [class*='dropdown'],
        div:has-text('Property For Rent'),
        div:has-text('Property For Sale'),
        div:has-text('Student Accommodation')
    """.replace('\n', ' ').strip()
    # 菜单中的具体选项
    CATEGORY_MENU_ITEM_RENT = "text=Property For Rent"
    CATEGORY_MENU_ITEM_SALE = "text=Property For Sale"
    CATEGORY_MENU_ITEM_STUDENT = "text=Student Accommodation"
    CATEGORY_MENU_ITEM_COMMERCIAL_SALE = "text=Commercial Property for sale"
    CATEGORY_MENU_ITEM_COMMERCIAL_RENT = "text=Commercial Property for rent"
    
    # 地址 sug 词
    # Sug 词（地址自动建议）- 根据实际页面结构优化
    # 使用更精确的选择器定位到实际的建议面板容器
    SUG_PANEL = "div[class*='PropertySearchSuggestContent_searchSuggestContent']"
    # 地址 sug 词项 - 精确匹配地址建议项的 class
    SUG_ITEM = "div[class*='PropertySuggestItem_modalSugItem']"
    
    # 搜索历史记录
    # 根据截图：标题为 "Recent Searches"，点击搜索框后显示，最多10条
    SEARCH_HISTORY_PANEL = "text=Recent Searches"  # 历史记录面板标题
    SEARCH_HISTORY_CONTAINER = "[class*='RecentSearches'], div:has-text('Recent Searches')"  # 包含标题的容器
    # 历史记录项：尝试多种选择器
    # 优先级：精确class > 通用class > 位置关系
    SEARCH_HISTORY_ITEM = """
        [class*='PropertySearchHistory_item'],
        [class*='RecentSearches'] [class*='item'],
        [class*='search-history'] [class*='item'],
        div:has-text('Recent Searches') ~ div,
        div:has-text('Recent Searches') + div [class*='item']
    """.replace('\n', ' ').strip()
    SEARCH_HISTORY_CLEAR = "button:has-text('Clear history'), button:has-text('Clear')"
    
    # List / Map 模式切换
    LIST_BUTTON = "button:has-text('List')"
    MAP_BUTTON = "button:has-text('Map')"
    
    # 分页
    PAGINATION = "[class*='pagination']"
    PAGE_LINK = "a[href*='page=']"
    
    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()
    
    # ========== 页面操作方法（静默执行）==========
    
    def navigate_to_property_page(self):
        """
        导航到 Property 页面 (https://au.58v5.cn)
        """
        try:
            self.goto("https://au.58v5.cn", timeout=60000)
            self.wait_for_page_load(state="domcontentloaded")
        except Exception as e:
            self.logger.error(f"打开 Property 页面失败: {e}")
            raise
    
    def handle_cookie_popup(self):
        """
        处理 Cookie 弹窗（如果存在）
        如果弹窗不存在，不会抛出异常
        """
        try:
            # 检查是否有 Cookie settings 文本
            if self.is_visible(self.COOKIE_SETTINGS_TEXT, timeout=3000):
                # 查找 Accept all 按钮
                if self.is_visible(self.COOKIE_ACCEPT_BUTTON, timeout=3000):
                    self.click(self.COOKIE_ACCEPT_BUTTON)
        except Exception:
            # Cookie 弹窗不存在，不做任何处理
            pass
    
    def click_property_link(self):
        """
        点击首页上的 Property 链接进入房产列表页
        按照手动执行方式：直接定位包含 'Property' 文本且 href 包含 'cate-property' 的链接
        """
        try:
            # 等待页面加载完成
            self.page.wait_for_timeout(1000)
            
            # 按照手动执行方式：查找 Property 链接
            # 手动执行时定位的是：link "Property Property" [ref=e59]，URL 包含 cate-property
            # 尝试多个选择器，找到可见的 Property 链接
            selectors = [
                "a[href*='cate-property']:has-text('Property')",  # 优先：URL 特征
                "a:has-text('Property')",  # 备选：文本匹配
                "[class*='category']:has-text('Property')",  # 备选：分类按钮
            ]
            
            property_link = None
            for selector in selectors:
                try:
                    elements = self.page.locator(selector).all()
                    for element in elements:
                        try:
                            # 检查元素是否可见
                            if element.is_visible(timeout=2000):
                                # 验证文本包含 Property
                                text = element.inner_text().strip()
                                if "Property" in text:
                                    property_link = element
                                    break
                        except Exception:
                            continue
                    if property_link:
                        break
                except Exception:
                    continue
            
            # 如果找不到可见的，尝试使用第一个找到的元素（可能是 hidden 的）
            if not property_link:
                property_link = self.page.locator("a[href*='cate-property']:has-text('Property')").first
                # 等待元素存在（即使不可见）
                property_link.wait_for(state="attached", timeout=10000)
                # 使用 force click
                property_link.click(force=True)
            else:
                # 如果不在视口内，滚动到可见
                if not property_link.is_visible():
                    property_link.scroll_into_view_if_needed()
                    self.page.wait_for_timeout(500)
                # 直接点击
                property_link.click()
            
            # 等待页面加载
            self.wait_for_page_load(state="domcontentloaded")
            
            # 进入房产列表页后停留2秒（按照手动执行要求）
            self.page.wait_for_timeout(2000)
            
            self.logger.info("✓ 点击 Property 链接成功，已进入房产列表页")
        except Exception as e:
            self.logger.error(f"点击 Property 链接失败: {e}")
            raise
    
    def click_property_type_filter(self):
        """
        点击 Property Type 筛选项
        按照手动执行方式：直接定位文本为 'Property Type' 的元素并点击
        """
        try:
            # 按照手动执行方式：直接定位文本
            property_type_filter = self.page.locator("text=Property Type").first
            property_type_filter.wait_for(state="visible", timeout=10000)
            
            # 直接点击
            property_type_filter.click()
            
            # 等待弹窗出现（按照手动执行，等待1秒）
            self.page.wait_for_timeout(1000)
            
            # 验证弹窗是否出现（使用更灵活的方式）
            modal_visible = False
            selectors = [
                "[role='dialog']",
                ".modal",
                "[class*='modal']",
                "[class*='dialog']"
            ]
            
            for selector in selectors:
                try:
                    modal = self.page.locator(selector).first
                    if modal.count() > 0 and modal.is_visible(timeout=2000):
                        modal_visible = True
                        break
                except Exception:
                    continue
            
            if modal_visible:
                self.logger.info("✓ 点击 Property Type 筛选项成功，Category 弹窗已出现")
            else:
                self.logger.warning("⚠ Category 弹窗可能未立即出现，继续执行...")
        except Exception as e:
            self.logger.error(f"点击 Property Type 筛选项失败: {e}")
            raise
    
    def get_unselected_categories(self):
        """
        获取 Category 弹窗中未选择的类目列表
        
        Returns:
            list: 未选择的类目文本列表
        """
        unselected = []
        try:
            # 等待弹窗出现
            self.page.wait_for_timeout(500)
            
            # 查找所有类目选项（右侧列的具体属性类型）
            selectors = [
                "[class*='category-item']",
                "[class*='category'] [class*='item']",
                "[class*='option']",
                "[role='option']",
                "li[class*='category']",
                "div[class*='category']"
            ]
            
            all_items = []
            for selector in selectors:
                try:
                    items = self.page.locator(selector).all()
                    if items:
                        all_items = items
                        break
                except Exception:
                    continue
            
            # 如果找不到，尝试查找所有可能的类目元素
            if not all_items:
                all_items = self.page.locator(self.CATEGORY_THIRD_LEVEL_ITEMS).all()
            
            # 检查每个类目是否被选中
            for item in all_items:
                try:
                    if item.is_visible(timeout=1000):
                        text = item.inner_text().strip()
                        if text:
                            # 检查是否有选中标记（checked、selected、active等）
                            is_selected = False
                            try:
                                # 检查是否有 checked 属性
                                checked = item.get_attribute("aria-checked")
                                if checked == "true":
                                    is_selected = True
                                
                                # 检查 class 中是否包含 selected/active/checked
                                class_name = item.get_attribute("class") or ""
                                if any(keyword in class_name.lower() for keyword in ['selected', 'active', 'checked']):
                                    is_selected = True
                                
                                # 检查是否有勾选图标
                                checkmark = item.locator("[class*='check'], [class*='icon'], svg").first
                                if checkmark.count() > 0 and checkmark.is_visible(timeout=500):
                                    is_selected = True
                            except Exception:
                                pass
                            
                            # 如果未选中，添加到列表
                            if not is_selected and len(text) < 50:  # 避免匹配整个页面文本
                                unselected.append(text)
                except Exception:
                    continue
            
            return unselected
        except Exception as e:
            self.logger.error(f"获取未选择类目失败: {e}")
            return []
    
    def select_third_level_category(self, index=1):
        """
        在 Category 弹窗中选择三级类目（从第2个选，index=1）
        按照手动执行方式：直接在弹窗内定位文本并点击，不拦截导航
        
        Args:
            index: 类目索引，默认1（第2个，即 Townhomes）
        """
        try:
            # 等待弹窗完全加载（按照手动执行，等待1.5秒）
            self.page.wait_for_timeout(1500)
            
            # 确保弹窗存在且可见
            modal = self.page.locator("[role='dialog']").first
            modal.wait_for(state="visible", timeout=5000)
            self.logger.info("✓ Category 弹窗已找到且可见")
            
            # 确定目标类目文本（租赁房型无 Land，实际选项顺序与弹窗 <a> 一致）
            property_types = ['House', 'Townhomes', 'Apartment&Unit', 'Villa', 'Retirement', 'Retirement', 'Other']
            target_type = property_types[index] if index < len(property_types) else property_types[1]
            
            self.logger.info(f"准备选择第 {index + 1} 个类目: {target_type}")
            
            # 按照手动执行方式：直接在弹窗内定位文本并点击
            # 手动执行时定位的是：generic [ref=e324] [cursor=pointer]: Townhomes
            # 使用 Playwright 的方式：在弹窗内查找包含目标文本的可点击元素
            category_item = modal.locator(f"text={target_type}").first
            
            # 等待元素可见
            category_item.wait_for(state="visible", timeout=5000)
            
            # 如果不在视口内，滚动到可见（只在弹窗内滚动）
            try:
                category_item.scroll_into_view_if_needed()
                self.page.wait_for_timeout(300)
            except Exception:
                pass
            
            # 直接点击（按照手动执行方式，简单直接，不拦截导航）
            category_item.click()
            
            self.logger.info(f"✓ 点击类目成功: {target_type}")
            
            # 等待选中状态更新（按照手动执行，等待1秒）
            self.page.wait_for_timeout(1000)
            
            # 注意：不检查 URL 是否变化，因为点击类目后可能正常跳转到筛选结果页
            # 这是预期的行为，不应该误判为"导航到详情页"
            
        except Exception as e:
            self.logger.error(f"选择三级类目失败: {e}")
            raise
    
    def click_done_button(self):
        """
        点击 Done 按钮
        按照手动执行方式：直接定位并点击，不拦截导航
        """
        try:
            # 按照手动执行方式：直接定位 Done 按钮
            # 手动执行时定位的是：button "Done" [ref=e337]
            done_button = self.page.locator("button:has-text('Done')").first
            done_button.wait_for(state="visible", timeout=10000)
            
            # 直接点击（按照手动执行方式，简单直接）
            done_button.click()
            
            self.logger.info("✓ 点击 Done 按钮成功")
            
            # 等待弹窗关闭和页面更新（按照手动执行，等待2秒）
            self.page.wait_for_timeout(2000)
            self.wait_for_page_load(state="domcontentloaded")
        except Exception as e:
            self.logger.error(f"点击 Done 按钮失败: {e}")
            raise
    
    def close_modal_by_x_button(self):
        """
        点击弹窗右上角的 'X' 按钮关闭弹窗
        按照手动执行方式：直接定位并点击关闭按钮
        """
        try:
            # 按照手动执行方式：查找弹窗右上角的关闭按钮
            # 常见的选择器：带 aria-label="Close" 的按钮，或包含 × 的按钮
            close_button_selectors = [
                "[role='dialog'] button[aria-label='Close']",
                "[role='dialog'] button:has-text('×')",
                "[role='dialog'] button:has-text('X')",
                ".modal button.close",
                "[class*='modal'] [class*='close']",
                "[role='dialog'] [class*='close']"
            ]
            
            close_button = None
            for selector in close_button_selectors:
                try:
                    btn = self.page.locator(selector).first
                    if btn.is_visible(timeout=2000):
                        close_button = btn
                        self.logger.info(f"✓ 找到关闭按钮，使用选择器: {selector}")
                        break
                except Exception:
                    continue
            
            if not close_button:
                self.logger.error("未找到弹窗关闭按钮")
                raise Exception("未找到弹窗关闭按钮")
            
            # 直接点击关闭按钮
            close_button.click()
            self.logger.info("✓ 点击关闭按钮成功")
            
            # 等待弹窗关闭动画完成
            self.page.wait_for_timeout(1000)
            
        except Exception as e:
            self.logger.error(f"点击关闭按钮失败: {e}")
            raise
    
    def is_modal_visible(self):
        """
        检查 Category 弹窗是否可见
        
        Returns:
            bool: 弹窗是否可见
        """
        try:
            modal_selectors = [
                "[role='dialog']",
                ".modal",
                "[class*='modal']",
                "[class*='dialog']"
            ]
            
            for selector in modal_selectors:
                try:
                    modal = self.page.locator(selector).first
                    if modal.is_visible(timeout=2000):
                        return True
                except Exception:
                    continue
            
            return False
        except Exception as e:
            self.logger.error(f"检查弹窗可见性失败: {e}")
            return False
    
    def get_selected_category_text(self):
        """
        获取已选择的三级类目文本（从 Property Type 筛选项位置）
        按照手动执行方式：直接查找显示类目的元素
        根据截图：筛选项按钮显示 "Townhomes"
        
        Returns:
            str: 已选择的类目文本
        """
        try:
            # 等待页面更新
            self.page.wait_for_timeout(1000)
            
            # 按照手动执行方式：查找筛选项位置显示的文本
            # 根据截图：第一个红框显示的是筛选项按钮 "Townhomes"
            # 查找筛选栏中的类目按钮（在 Property Type 位置）
            selectors = [
                "button:has-text('Townhomes')",  # 筛选项按钮
                "button:has-text('House')",
                "[class*='filter'] button:has-text('Townhomes')",
                "[class*='filter'] button:has-text('House')",
                "text=/^Townhomes$|^House$|^Apartment/i"  # 精确匹配
            ]
            
            for selector in selectors:
                try:
                    element = self.page.locator(selector).first
                    if element.is_visible(timeout=2000):
                        text = element.inner_text().strip()
                        # 验证是类目名称（不是整个页面文本）
                        if text in ['Townhomes', 'House', 'Apartment', 'Villa', 'Retirement', 'Land', 'Other']:
                            return text
                except Exception:
                    continue
            
            return ""
        except Exception as e:
            self.logger.error(f"获取已选择类目文本失败: {e}")
            return ""
    
    def is_filter_tag_visible(self, expected_category=None):
        """
        检查筛选结果回显标签是否可见
        按照手动执行方式：直接查找包含 'Property Type' 的标签
        回显内容根据选择的类目而变化，格式为 "Property Type: [类目名称]"
        
        Args:
            expected_category: 期望的类目名称（可选，用于精确验证）
        
        Returns:
            bool: 标签是否可见
        """
        try:
            # 按照手动执行方式：查找筛选结果回显标签
            # 回显格式：Property Type: [选择的类目名称]
            # 使用通用选择器，不硬编码类目名称
            selectors = [
                "*:has-text('Property Type:')",  # 包含冒号（通用）
                "*:has-text('Property Type')",  # 包含文本（通用）
                "text=/Property Type:/i"  # 正则匹配（通用）
            ]
            
            # 如果指定了期望的类目，添加精确匹配
            if expected_category:
                selectors.insert(0, f"*:has-text('Property Type: {expected_category}')")
                selectors.insert(1, f"text=/Property Type.*{expected_category}/i")
            
            for selector in selectors:
                try:
                    filter_tag = self.page.locator(selector).first
                    if filter_tag.is_visible(timeout=2000):
                        text = filter_tag.inner_text()
                        # 验证文本包含 Property Type 且不是整个页面文本
                        if "Property Type" in text and len(text) < 200:
                            # 如果指定了期望的类目，验证是否包含该类目
                            if expected_category:
                                if expected_category in text:
                                    return True
                            else:
                                return True
                except Exception:
                    continue
            
            return False
        except Exception:
            return False
    
    def get_filter_tag_text(self):
        """
        获取筛选结果回显标签的文本
        按照手动执行方式：直接获取包含 'Property Type' 的文本
        回显内容根据选择的类目而变化，格式为 "Property Type: [类目名称]"
        
        Returns:
            str: 标签文本（如 "Property Type: Townhomes" 或 "Property Type: House"）
        """
        try:
            # 按照手动执行方式：查找筛选结果回显标签
            # 回显格式：Property Type: [选择的类目名称]
            # 使用通用选择器，不硬编码类目名称
            selectors = [
                "*:has-text('Property Type:')",  # 包含冒号（通用）
                "*:has-text('Property Type')",  # 包含文本（通用）
                "text=/Property Type:/i"  # 正则匹配（通用）
            ]
            
            for selector in selectors:
                try:
                    filter_tag = self.page.locator(selector).first
                    if filter_tag.is_visible(timeout=2000):
                        text = filter_tag.inner_text().strip()
                        # 验证文本包含 Property Type 且不是整个页面文本
                        if "Property Type" in text and len(text) < 200:
                            return text
                except Exception:
                    continue
            
            return ""
        except Exception as e:
            self.logger.error(f"获取筛选标签文本失败: {e}")
            return ""
    
    def get_property_type_tag_text(self):
        """
        获取 Property Type 筛选结果回显标签的文本
        这是 get_filter_tag_text 的别名方法，用于更清晰的代码表达
        
        Returns:
            str: 标签文本（如 "Property Type:House"）
        """
        return self.get_filter_tag_text()
    
    # ========== 排序功能相关方法 ==========
    
    def get_current_sort_text(self):
        """
        获取当前排序方式的显示文本
        按照手动执行方式：直接查找排序按钮的文本
        
        Returns:
            str: 当前排序方式文本（如 "Best Match", "Newest First" 等）
        """
        try:
            # 按照手动执行方式：查找排序选项的显示文本
            # 从手动执行中看到的 DOM 结构：generic [ref=e57]: Best Match
            selectors = [
                "text=Best Match",
                "text=Newest First",
                "text=Lowest Price",
                "text=Highest Price"
            ]
            
            for selector in selectors:
                try:
                    element = self.page.locator(selector).first
                    if element.is_visible(timeout=2000):
                        text = element.inner_text().strip()
                        # 验证文本是排序选项之一
                        if text in ["Best Match", "Newest First", "Lowest Price", "Highest Price"]:
                            return text
                except Exception:
                    continue
            
            return ""
        except Exception as e:
            self.logger.error(f"获取当前排序方式失败: {e}")
            return ""
    
    def verify_default_sort_is_best_match(self):
        """
        验证默认排序方式是否为 'Best Match'
        按照手动执行方式：检查页面上是否显示 'Best Match' 文本
        
        Returns:
            bool: 如果默认排序是 Best Match 返回 True，否则返回 False
        """
        try:
            # 等待页面加载完成
            self.page.wait_for_timeout(1000)
            
            # 查找 Best Match 文本
            best_match_element = self.page.locator("text=Best Match").first
            is_visible = best_match_element.is_visible(timeout=3000)
            
            if is_visible:
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f"验证默认排序失败: {e}")
            return False
    
    def click_clear_button_in_category_modal(self):
        """
        点击 Property Type / Category 弹窗中的 Clear 按钮（若存在）
        按照手动执行方式：在弹窗内定位 Clear 并点击
        """
        try:
            modal = self.page.locator("[role='dialog']").first
            modal.wait_for(state="visible", timeout=5000)
            clear_button = modal.locator("button:has-text('Clear')").first
            clear_button.wait_for(state="visible", timeout=5000)
            clear_button.click()
            self.logger.info("✓ 点击 Category 弹窗 Clear 按钮成功")
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击 Category 弹窗 Clear 按钮失败: {e}")
            raise

    def click_sort_button(self):
        """
        点击排序按钮，展开排序选项下拉框
        按照手动执行方式：直接点击当前显示的排序文本（如 "Best Match"）
        """
        try:
            # 等待页面加载完成
            self.page.wait_for_timeout(1000)
            
            # 按照手动执行方式：直接点击排序按钮
            # 手动执行时点击的是 generic [ref=e57]: Best Match
            # 查找当前显示的排序选项并点击
            selectors = [
                "text=Best Match",
                "text=Newest First",
                "text=Lowest Price",
                "text=Highest Price"
            ]
            
            for selector in selectors:
                try:
                    element = self.page.locator(selector).first
                    if element.is_visible(timeout=2000):
                        element.click()
                        # 等待下拉框展开
                        self.page.wait_for_timeout(1000)
                        return
                except Exception:
                    continue
            
            raise Exception("未找到可点击的排序按钮")
        except Exception as e:
            self.logger.error(f"点击排序按钮失败: {e}")
            raise
    
    def select_sort_option(self, option_name):
        """
        在排序下拉框中选择指定的排序方式
        按照手动执行方式：直接点击对应的排序选项
        
        Args:
            option_name (str): 排序方式名称，可选值：
                - "Best Match"
                - "Newest First"
                - "Lowest Price"
                - "Highest Price"
        """
        try:
            # 等待下拉框完全展开
            self.page.wait_for_timeout(1000)
            
            # 按照手动执行方式：直接点击对应的排序选项
            # 手动执行时点击的是 generic [ref=e312] [cursor=pointer]: Newest First
            option_selector = f"text={option_name}"
            
            # 查找所有匹配的元素（下拉框中可能有多个相同文本）
            elements = self.page.locator(option_selector).all()
            
            # 点击第二个匹配的元素（第一个是顶部显示的，第二个是下拉框中的）
            # 如果只有一个，就点击那一个
            if len(elements) >= 2:
                elements[1].click()
            elif len(elements) == 1:
                elements[0].click()
            else:
                raise Exception(f"未找到排序选项: {option_name}")
            
            # 等待选中状态更新
            self.page.wait_for_timeout(500)
            
        except Exception as e:
            self.logger.error(f"选择排序方式失败: {e}")
            raise
    
    def click_done_button_in_sort_modal(self):
        """
        点击排序下拉框中的 Done 按钮
        按照手动执行方式：直接点击 Done 按钮
        """
        try:
            # 按照手动执行方式：直接点击 Done 按钮
            # 手动执行时点击的是 button "Done" [ref=e323]
            done_button = self.page.locator("button:has-text('Done')").first
            done_button.click()
            
            # 等待页面刷新
            self.page.wait_for_timeout(2000)
            
        except Exception as e:
            self.logger.error(f"点击 Done 按钮失败: {e}")
            raise
    
    def click_clear_button_in_sort_modal(self):
        """
        点击排序下拉框中的 Clear 按钮
        按照手动执行方式：直接点击 Clear 按钮
        """
        try:
            # 按照手动执行方式：直接点击 Clear 按钮
            # 根据图片，Clear按钮和Done按钮并排显示
            clear_button = self.page.locator("button:has-text('Clear')").first
            clear_button.wait_for(state="visible", timeout=5000)
            clear_button.click()
            
            self.logger.info("✓ 点击 Clear 按钮成功")
            
            # 等待清除操作生效
            self.page.wait_for_timeout(1000)
            
        except Exception as e:
            self.logger.error(f"点击 Clear 按钮失败: {e}")
            raise
    
    # ========== Price 筛选功能相关方法 ==========
    
    def click_price_filter(self):
        """
        点击 Price 筛选项，展开价格筛选下拉框
        兼容未激活 "Price" 和已激活 "Price 500-2000 ×" 两种文本状态
        """
        try:
            # 等待页面加载完成
            self.page.wait_for_timeout(1000)
            
            # 前缀匹配 "Price"（兼容未激活和已激活状态）
            # 未激活: "Price"
            # 已激活: "Price 500-2000 ×"
            price_filter = self.page.locator("text=/^Price/").first
            # 显式等待 Price 筛选器可见（避免页面未完全加载导致超时）
            price_filter.wait_for(state="visible", timeout=10000)
            # 滚动到元素可见区域（如果元素在视口外）
            price_filter.scroll_into_view_if_needed(timeout=5000)
            self.page.wait_for_timeout(500)  # 额外等待确保元素可交互
            price_filter.click()
            
            # 等待下拉框展开
            self.page.wait_for_timeout(1000)
            
        except Exception as e:
            self.logger.error(f"点击 Price 筛选项失败: {e}")
            raise
    
    def input_price_range(self, min_price, max_price):
        """
        在 Price 筛选下拉框中输入价格范围
        按照手动执行方式：直接在 Min 和 Max 输入框中输入数值
        
        Args:
            min_price (str|int): 最低价格
            max_price (str|int): 最高价格
        """
        try:
            # 等待下拉框完全展开
            self.page.wait_for_timeout(1500)
            
            # 按照手动执行方式：查找 Min 和 Max 输入框并输入值
            # 手动执行时找到的是 textbox "Min" [ref=e313] 和 textbox "Max" [ref=e316]
            
            # 输入最低价格 - 使用多种选择器
            min_input = None
            min_selectors = [
                "textbox:has-text('Min')",
                "input[placeholder='Min']",
                "input[placeholder*='Min']",
                "*:has-text('Min') input"
            ]
            
            for selector in min_selectors:
                try:
                    input_elem = self.page.locator(selector).first
                    if input_elem.is_visible(timeout=3000):
                        min_input = input_elem
                        break
                except Exception:
                    continue
            
            if not min_input:
                raise Exception("未找到 Min 输入框")
            
            min_input.fill(str(min_price))
            self.page.wait_for_timeout(500)
            
            # 输入最高价格 - 使用多种选择器
            max_input = None
            max_selectors = [
                "textbox:has-text('Max')",
                "input[placeholder='Max']",
                "input[placeholder*='Max']",
                "*:has-text('Max') input"
            ]
            
            for selector in max_selectors:
                try:
                    input_elem = self.page.locator(selector).first
                    if input_elem.is_visible(timeout=3000):
                        max_input = input_elem
                        break
                except Exception:
                    continue
            
            if not max_input:
                raise Exception("未找到 Max 输入框")
            
            max_input.fill(str(max_price))
            self.page.wait_for_timeout(500)
            
        except Exception as e:
            self.logger.error(f"输入价格范围失败: {e}")
            raise
    
    def click_done_button_in_price_modal(self):
        """
        点击 Price 筛选下拉框中的 Done 按钮
        按照手动执行方式：直接点击 Done 按钮
        """
        try:
            # 按照手动执行方式：直接点击 Done 按钮
            # 手动执行时点击的是 button "Done" [ref=e319]
            done_button = self.page.locator("button:has-text('Done')").first
            done_button.click()
            
            # 等待页面刷新
            self.page.wait_for_timeout(2000)
            
        except Exception as e:
            self.logger.error(f"点击 Done 按钮失败: {e}")
            raise
    
    def get_price_filter_tag_text(self):
        """
        获取 Price 筛选结果回显标签的文本
        按照手动执行方式：查找包含 'Price:' 的文本
        
        Returns:
            str: 标签文本（如 "Price:1-10000"）
        """
        try:
            # 按照手动执行方式：查找 Price 筛选结果回显标签
            # 手动执行时看到的是 generic [ref=e83]: Price:1-10000
            # 回显格式：Price:[Min]-[Max]
            
            selectors = [
                "text=/Price:/i",  # 正则匹配
                "*:has-text('Price:')",  # 包含文本
            ]
            
            for selector in selectors:
                try:
                    elements = self.page.locator(selector).all()
                    for element in elements:
                        if element.is_visible(timeout=2000):
                            text = element.inner_text().strip()
                            # 验证文本包含 Price: 且不是整个页面文本
                            if "Price:" in text and len(text) < 100:
                                return text
                except Exception:
                    continue
            
            return ""
        except Exception as e:
            self.logger.error(f"获取 Price 筛选标签文本失败: {e}")
            return ""
    
    def get_price_filter_display_text(self):
        """
        获取 Price 筛选项的显示文本（如 "Price·2"）
        按照手动执行方式：查找 Price 筛选按钮的显示文本
        
        Returns:
            str: Price 筛选项显示文本
        """
        try:
            # 按照手动执行方式：查找 Price 筛选按钮
            # 手动执行时看到的是 text: Price, generic [ref=e74]: ·, text: "2"
            
            # 尝试多种选择器
            selectors = [
                "text=/Price·/i",
                "*:has-text('Price·')",
                "*:has-text('Price') >> xpath=.."
            ]
            
            for selector in selectors:
                try:
                    elements = self.page.locator(selector).all()
                    for element in elements:
                        try:
                            if element.is_visible(timeout=2000):
                                text = element.inner_text().strip()
                                # 验证文本包含 Price 和数字
                                if "Price" in text and len(text) < 50:
                                    return text
                        except Exception:
                            continue
                except Exception:
                    continue
            
            return ""
        except Exception as e:
            self.logger.error(f"获取 Price 筛选项显示文本失败: {e}")
            return ""
    
    def verify_price_filter_display(self, expected_text="Price"):
        """
        验证 Price 筛选项的显示（包括计数器）
        按照手动执行方式：检查 Price 筛选项是否显示正确的文本
        
        Args:
            expected_text (str): 期望的文本（如 "Price" 或 "Price·2"）
        
        Returns:
            bool: 如果显示正确返回 True，否则返回 False
        """
        try:
            # 等待页面加载完成
            self.page.wait_for_timeout(1000)
            
            # 按照手动执行方式：查找 Price 筛选项
            # 手动执行时看到的是 generic [ref=e71]: Price·2
            # 其中包含 text: Price 和 text: "2"
            
            # 查找包含 Price 的元素
            price_elements = self.page.locator("text=Price").all()
            
            for element in price_elements:
                try:
                    if element.is_visible(timeout=2000):
                        # 获取父元素的完整文本
                        parent = element.locator("xpath=..").first
                        text = parent.inner_text().strip()
                        
                        # 检查是否匹配预期文本（支持部分匹配）
                        if expected_text in text or text == expected_text:
                            return True
                except Exception:
                    continue
            
            return False
        except Exception as e:
            self.logger.error(f"验证 Price 筛选项显示失败: {e}")
            return False
    
    def get_price_input_values(self):
        """
        获取 Price 筛选下拉框中的 Min 和 Max 输入框的值
        按照手动执行方式：读取输入框中的值
        
        Returns:
            tuple: (min_value, max_value) 元组，如果获取失败返回 ("", "")
        """
        try:
            # 等待下拉框完全展开
            self.page.wait_for_timeout(1000)
            
            # 按照手动执行方式：查找 Min 和 Max 输入框并读取值
            # 手动执行时看到的是 textbox "Min" [ref=e236]: "1" 和 textbox "Max" [ref=e239]: 10,000
            
            min_value = ""
            max_value = ""
            
            # 获取 Min 输入框的值 - 使用多种选择器
            min_selectors = [
                "textbox:has-text('Min')",
                "input[placeholder='Min']",
                "input[placeholder*='Min']",
                "*:has-text('Min') input"
            ]
            
            for selector in min_selectors:
                try:
                    min_input = self.page.locator(selector).first
                    if min_input.is_visible(timeout=2000):
                        min_value = min_input.input_value()
                        break
                except Exception:
                    continue
            
            # 获取 Max 输入框的值 - 使用多种选择器
            max_selectors = [
                "textbox:has-text('Max')",
                "input[placeholder='Max']",
                "input[placeholder*='Max']",
                "*:has-text('Max') input"
            ]
            
            for selector in max_selectors:
                try:
                    max_input = self.page.locator(selector).first
                    if max_input.is_visible(timeout=2000):
                        max_value = max_input.input_value()
                        break
                except Exception:
                    continue
            
            return (min_value, max_value)
        except Exception as e:
            self.logger.error(f"获取价格输入框值失败: {e}")
            return ("", "")
    
    def get_price_error_message(self):
        """
        获取 Price 筛选下拉框中的错误提示信息
        按照手动执行方式：读取错误提示文本
        
        Returns:
            str: 错误提示文本，如果没有错误返回空字符串
        """
        try:
            # 等待可能的错误提示出现
            self.page.wait_for_timeout(500)
            
            # 按照手动执行方式：查找错误提示信息
            # 根据图片，错误提示显示为 "Max price must be higher than min price"
            error_selectors = [
                "text=/Max price must be higher than min price/i",
                "[class*='error']",
                "[class*='warning']",
                "[class*='message']:has-text('price')",
                "text=/must be higher/i"
            ]
            
            for selector in error_selectors:
                try:
                    error_element = self.page.locator(selector).first
                    if error_element.is_visible(timeout=2000):
                        error_text = error_element.inner_text().strip()
                        if error_text:
                            self.logger.info(f"✓ 找到错误提示: {error_text}")
                            return error_text
                except Exception:
                    continue
            
            return ""
        except Exception as e:
            self.logger.error(f"获取错误提示失败: {e}")
            return ""
    
    def click_clear_button_in_price_modal(self):
        """
        点击 Price 筛选下拉框中的 Clear 按钮
        按照手动执行方式：直接点击 Clear 按钮
        """
        try:
            # 按照手动执行方式：直接点击 Clear 按钮
            # 根据图片，Clear 按钮和 Done 按钮并排显示
            clear_button = self.page.locator("button:has-text('Clear')").first
            clear_button.wait_for(state="visible", timeout=5000)
            clear_button.click()
            
            self.logger.info("✓ 点击 Clear 按钮成功")
            
            # 等待清除操作生效
            self.page.wait_for_timeout(1000)
            
        except Exception as e:
            self.logger.error(f"点击 Clear 按钮失败: {e}")
            raise
    
    def is_price_modal_visible(self):
        """
        检查 Price 筛选下拉框是否可见
        
        Returns:
            bool: 下拉框是否可见
        """
        try:
            # 等待一小段时间确保动画完成
            self.page.wait_for_timeout(500)
            
            # 检查输入框是否可见（作为下拉框可见的标志）
            # 使用多种选择器
            selectors = [
                "textbox:has-text('Min')",
                "input[placeholder='Min']",
                "input[placeholder*='Min']",
                "textbox:has-text('Max')",
                "input[placeholder='Max']",
                "input[placeholder*='Max']"
            ]
            
            for selector in selectors:
                try:
                    input_elem = self.page.locator(selector).first
                    if input_elem.is_visible(timeout=1000):
                        return True
                except Exception:
                    continue
            
            return False
        except Exception as e:
            self.logger.error(f"检查 Price 下拉框可见性失败: {e}")
            return False
    
    def click_page_blank_area(self):
        """
        点击页面空白处（用于关闭弹窗）
        按照手动执行方式：点击页面上的空白区域
        """
        try:
            # 按照手动执行方式：点击页面上的空白区域
            # 点击页面顶部或侧边的空白处
            # 使用页面坐标点击（避免点击到具体元素）
            self.page.mouse.click(100, 100)
            
            self.logger.info("✓ 点击页面空白处成功")
            
            # 等待弹窗关闭动画完成
            self.page.wait_for_timeout(1000)
            
        except Exception as e:
            self.logger.error(f"点击页面空白处失败: {e}")
            raise
    
    # ========== Beds 筛选功能相关方法 ==========
    
    def click_beds_filter(self):
        """
        点击 Beds 筛选项，展开 Beds 筛选下拉框
        按照手动执行方式：直接点击 Beds 文本
        """
        try:
            # 等待页面加载完成
            self.page.wait_for_timeout(1000)
            
            # 按照手动执行方式：直接点击 Beds 筛选项
            beds_filter = self.page.locator("text=Beds").first
            beds_filter.click()
            
            # 等待下拉框展开
            self.page.wait_for_timeout(1000)
            
        except Exception as e:
            self.logger.error(f"点击 Beds 筛选项失败: {e}")
            raise
    
    def select_beds_values(self, *values):
        """
        在 Beds 筛选下拉框中选择多个值。
        使用 FilterItemPC_filterItemOverlay 容器作用域，避免误点分页按钮。

        Args:
            *values: 可变参数，卧室数量（如 1, 2, 3, '8+', 'Studio'）
        """
        try:
            self.page.wait_for_timeout(800)

            # Beds 面板容器（class 含 FilterItemPC_filterItemOverlay 且处于 show 状态）
            panel = self.page.locator("[class*='FilterItemPC_filterItemOverlay']").last

            for value in values:
                value_str = str(value)
                # 在面板内精确匹配 Selector_label 文本，避免整页搜索误点分页
                option = panel.locator(
                    f"[class*='Selector_label']:text-is('{value_str}')"
                ).first
                option.wait_for(state="visible", timeout=5000)
                option.click()
                self.logger.info(f"✓ 已选择 Beds 值: {value}")
                self.page.wait_for_timeout(300)

        except Exception as e:
            self.logger.error(f"选择 Beds 值失败: {e}")
            raise
    
    def click_done_button_in_beds_modal(self):
        """
        点击 Beds 筛选下拉框中的 Done 按钮
        按照手动执行方式：直接点击 Done 按钮
        """
        try:
            # 按照手动执行方式：直接点击 Done 按钮
            done_button = self.page.locator("button:has-text('Done')").first
            done_button.click()
            
            # 等待页面刷新
            self.page.wait_for_timeout(2000)
            
        except Exception as e:
            self.logger.error(f"点击 Done 按钮失败: {e}")
            raise
    
    def get_beds_filter_display_text(self):
        """
        获取 Beds 筛选项的显示文本（包括计数器）
        按照手动执行方式：读取 Beds 筛选项位置的文本
        
        Returns:
            str: 筛选项显示文本（如 "Beds·2"）
        """
        try:
            # 等待页面更新
            self.page.wait_for_timeout(1000)
            
            # 按照手动执行方式：查找 Beds 筛选项
            # 手动执行时看到的是：generic [ref=e75]: text: Beds, generic [ref=e76]: ·, text: "2"
            
            # 查找包含 Beds 的元素
            beds_elements = self.page.locator("text=Beds").all()
            
            for element in beds_elements:
                try:
                    if element.is_visible(timeout=2000):
                        # 获取父元素以包含完整文本
                        parent = element.locator("..").first
                        text = parent.inner_text().strip()
                        # 验证是否包含 Beds 和计数器
                        if "Beds" in text and "·" in text:
                            return text
                except Exception:
                    continue
            
            return ""
        except Exception as e:
            self.logger.error(f"获取 Beds 筛选项显示文本失败: {e}")
            return ""
    
    def get_beds_filter_tag_text(self):
        """
        获取 Beds 筛选结果回显标签的文本
        按照手动执行方式：查找包含 'Beds:' 的文本
        
        Returns:
            str: 标签文本（如 "Beds:2,4"）
        """
        try:
            # 按照手动执行方式：查找 Beds 筛选结果回显标签
            # 手动执行时看到的是：generic [ref=e83]: Beds:2,4
            # 回显格式：Beds:[值1],[值2]
            
            tag_selectors = [
                "text=/Beds:/i",  # 正则匹配
                "*:has-text('Beds:')",  # 包含文本
            ]
            
            for selector in tag_selectors:
                try:
                    tag_elements = self.page.locator(selector).all()
                    for element in tag_elements:
                        try:
                            if element.is_visible(timeout=2000):
                                text = element.inner_text().strip()
                                # 验证文本包含 Beds: 且不是整个页面文本
                                if "Beds:" in text and len(text) < 50:
                                    return text
                        except Exception:
                            continue
                except Exception:
                    continue
            
            return ""
        except Exception as e:
            self.logger.error(f"获取 Beds 筛选标签文本失败: {e}")
            return ""
    
    def click_clear_button_in_beds_modal(self):
        """
        点击 Beds 筛选下拉框中的 Clear 按钮
        按照手动执行方式：直接点击 Clear 按钮
        """
        try:
            # 按照手动执行方式：直接点击 Clear 按钮
            # 从图片可以看到 Clear 和 Done 按钮并排显示
            clear_button = self.page.locator("button:has-text('Clear')").first
            clear_button.wait_for(state="visible", timeout=5000)
            clear_button.click()
            self.logger.info("✓ 点击 Clear 按钮成功")
            # 等待清除操作生效
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击 Clear 按钮失败: {e}")
            raise
    
    def is_beds_modal_visible(self):
        """
        检查 Beds 下拉框是否可见
        按照手动执行方式：检查下拉框元素是否可见
        
        Returns:
            bool: 下拉框是否可见
        """
        try:
            # 检查 Done 按钮是否可见（作为弹窗打开的标志）
            done_button = self.page.locator("button:has-text('Done')").first
            return done_button.is_visible(timeout=2000)
        except Exception as e:
            self.logger.warning(f"检查 Beds 下拉框可见性失败: {e}")
            return False
    
    def get_selected_beds_values_in_modal(self):
        """
        获取 Beds 下拉框中当前已选择的值（复选框被选中的值）
        按照手动执行方式：查找被选中的复选框对应的值
        
        Returns:
            list: 已选择的卧室数列表（如 [2, 4]）
        """
        try:
            selected_values = []
            
            # 等待弹窗完全加载
            self.page.wait_for_timeout(1000)
            
            # 方法1: 通过查找每个数字，检查是否有选中状态的样式类或属性
            # 从图片可以看到，复选框被选中时会有特定的样式或属性
            for i in range(1, 11):  # 尝试 1-10
                try:
                    # 查找包含数字的所有元素
                    value_str = str(i)
                    # 使用多种策略查找
                    selectors = [
                        f"text=/^{value_str}$/",
                        f"*:has-text('{value_str}')",
                    ]
                    
                    for selector in selectors:
                        try:
                            elements = self.page.locator(selector).all()
                            for element in elements:
                                try:
                                    if not element.is_visible(timeout=500):
                                        continue
                                    
                                    # 获取元素文本，确保是精确匹配
                                    text = element.inner_text().strip()
                                    if text != value_str:
                                        continue
                                    
                                    # 检查父元素或自身是否包含选中状态的标识
                                    # 可能的选中状态标识：checked class、selected class、aria-checked="true"
                                    parent = element.locator("..").first
                                    parent_html = parent.evaluate("el => el.outerHTML")
                                    
                                    # 检查是否包含选中状态的标识
                                    is_checked = (
                                        'checked' in parent_html.lower() or
                                        'selected' in parent_html.lower() or
                                        'aria-checked="true"' in parent_html or
                                        'input' in parent_html and 'type="checkbox"' in parent_html
                                    )
                                    
                                    if is_checked:
                                        # 进一步验证：查找 input checkbox 元素
                                        try:
                                            checkbox = parent.locator("input[type='checkbox']").first
                                            if checkbox.is_checked(timeout=500):
                                                selected_values.append(i)
                                                self.logger.info(f"✓ 检测到选中的 Beds 值: {i}")
                                                break
                                        except Exception:
                                            # 如果找不到 checkbox，但 HTML 中有选中标识，也认为是选中的
                                            if 'checked' in parent_html.lower():
                                                selected_values.append(i)
                                                self.logger.info(f"✓ 检测到选中的 Beds 值: {i}")
                                                break
                                except Exception as e:
                                    continue
                            
                            if i in selected_values:
                                break
                        except Exception:
                            continue
                except Exception as e:
                    self.logger.warning(f"检查 Beds 值 {i} 失败: {e}")
                    continue
            
            # 方法2: 如果方法1失败，尝试直接查找所有 checked 的 checkbox
            if not selected_values:
                try:
                    checkboxes = self.page.locator("input[type='checkbox']").all()
                    for checkbox in checkboxes:
                        try:
                            if checkbox.is_checked(timeout=500) and checkbox.is_visible(timeout=500):
                                # 查找相邻的文本
                                parent = checkbox.locator("..").first
                                text = parent.inner_text().strip()
                                # 提取数字
                                import re
                                numbers = re.findall(r'^\d+$', text)
                                if numbers:
                                    value = int(numbers[0])
                                    if 1 <= value <= 10 and value not in selected_values:
                                        selected_values.append(value)
                        except Exception:
                            continue
                except Exception as e:
                    self.logger.warning(f"方法2获取选中值失败: {e}")
            
            selected_values.sort()
            self.logger.info(f"✓ 获取到已选择的 Beds 值: {selected_values}")
            return selected_values
            
        except Exception as e:
            self.logger.error(f"获取 Beds 下拉框中已选择的值失败: {e}")
            return []
    
    # ========== Bathrooms 筛选功能相关方法 ==========
    
    def click_bathrooms_filter(self):
        """
        点击 Bathrooms 筛选项，展开 Bathrooms 筛选下拉框
        按照手动执行方式：直接点击 Bathrooms 文本
        """
        try:
            # 等待页面加载完成
            self.page.wait_for_timeout(1000)
            
            # 按照手动执行方式：直接点击 Bathrooms 筛选项
            bathrooms_filter = self.page.locator("text=Bathrooms").first
            bathrooms_filter.click()
            
            # 等待下拉框展开
            self.page.wait_for_timeout(1000)
            
        except Exception as e:
            self.logger.error(f"点击 Bathrooms 筛选项失败: {e}")
            raise
    
    def select_bathrooms_values(self, *values):
        """
        在 Bathrooms 筛选下拉框中选择多个值。
        使用 FilterItemPC_filterItemOverlay 容器作用域，避免误点分页按钮。

        Args:
            *values: 可变参数，浴室数量（如 1, 1.5, 2, 2.5, 3, '5+'）
        """
        try:
            self.page.wait_for_timeout(800)

            # Bathrooms 面板容器（与 Beds 共用相同的面板类名）
            panel = self.page.locator("[class*='FilterItemPC_filterItemOverlay']").last

            for value in values:
                value_str = str(value)
                option = panel.locator(
                    f"[class*='Selector_label']:text-is('{value_str}')"
                ).first
                option.wait_for(state="visible", timeout=5000)
                option.click()
                self.logger.info(f"✓ 已选择 Bathrooms 值: {value}")
                self.page.wait_for_timeout(300)

        except Exception as e:
            self.logger.error(f"选择 Bathrooms 值失败: {e}")
            raise
    
    def click_done_button_in_bathrooms_modal(self):
        """
        点击 Bathrooms 筛选下拉框中的 Done 按钮
        按照手动执行方式：直接点击 Done 按钮
        """
        try:
            # 按照手动执行方式：直接点击 Done 按钮
            done_button = self.page.locator("button:has-text('Done')").first
            done_button.click()
            
            # 等待页面刷新
            self.page.wait_for_timeout(2000)
            
        except Exception as e:
            self.logger.error(f"点击 Done 按钮失败: {e}")
            raise
    
    def get_bathrooms_filter_display_text(self):
        """
        获取 Bathrooms 筛选项的显示文本（包括计数器）
        按照手动执行方式：读取 Bathrooms 筛选项位置的文本
        
        Returns:
            str: 筛选项显示文本（如 "Bathrooms·2"）
        """
        try:
            # 等待页面更新
            self.page.wait_for_timeout(1000)
            
            # 按照手动执行方式：查找 Bathrooms 筛选项
            bathrooms_elements = self.page.locator("text=Bathrooms").all()
            
            for element in bathrooms_elements:
                try:
                    if element.is_visible(timeout=2000):
                        # 获取父元素以包含完整文本
                        parent = element.locator("..").first
                        text = parent.inner_text().strip()
                        # 验证是否包含 Bathrooms 和计数器
                        if "Bathrooms" in text and "·" in text:
                            return text
                except Exception:
                    continue
            
            return ""
        except Exception as e:
            self.logger.error(f"获取 Bathrooms 筛选项显示文本失败: {e}")
            return ""
    
    def get_bathrooms_filter_tag_text(self):
        """
        获取 Bathrooms 筛选结果回显标签的文本
        按照手动执行方式：查找包含 'Bathrooms:' 的文本
        
        Returns:
            str: 标签文本（如 "Bathrooms:2,2.5"）
        """
        try:
            # 按照手动执行方式：查找 Bathrooms 筛选结果回显标签
            # 回显格式：Bathrooms:[值1],[值2]
            
            tag_selectors = [
                "text=/Bathrooms:/i",  # 正则匹配
                "*:has-text('Bathrooms:')",  # 包含文本
            ]
            
            for selector in tag_selectors:
                try:
                    tag_elements = self.page.locator(selector).all()
                    for element in tag_elements:
                        try:
                            if element.is_visible(timeout=2000):
                                text = element.inner_text().strip()
                                # 验证文本包含 Bathrooms: 且不是整个页面文本
                                if "Bathrooms:" in text and len(text) < 100:
                                    return text
                        except Exception:
                            continue
                except Exception:
                    continue
            
            return ""
        except Exception as e:
            self.logger.error(f"获取 Bathrooms 筛选标签文本失败: {e}")
            return ""
    
    def click_clear_button_in_bathrooms_modal(self):
        """
        点击 Bathrooms 筛选下拉框中的 Clear 按钮
        按照手动执行方式：直接点击 Clear 按钮
        """
        try:
            # 按照手动执行方式：直接点击 Clear 按钮
            clear_button = self.page.locator("button:has-text('Clear')").first
            clear_button.wait_for(state="visible", timeout=5000)
            clear_button.click()
            self.logger.info("✓ 点击 Clear 按钮成功")
            # 等待清除操作生效
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击 Clear 按钮失败: {e}")
            raise
    
    def is_bathrooms_modal_visible(self):
        """
        检查 Bathrooms 下拉框是否可见
        按照手动执行方式：检查下拉框元素是否可见
        
        Returns:
            bool: 下拉框是否可见
        """
        try:
            # 检查 Done 按钮是否可见（作为弹窗打开的标志）
            done_button = self.page.locator("button:has-text('Done')").first
            return done_button.is_visible(timeout=2000)
        except Exception as e:
            self.logger.warning(f"检查 Bathrooms 下拉框可见性失败: {e}")
            return False
    
    # ========== Filter 综合筛选方法 ==========
    
    def click_filter_button(self):
        """
        点击 Filter 综合筛选按钮
        按照手动执行方式：直接定位并点击 Filter 按钮
        """
        try:
            # 按照手动执行方式：直接定位 Filter 按钮
            # 手动执行时定位的是：generic [ref=e62] 包含 text: Filter
            filter_button = self.page.locator(self.FILTER_BUTTON).first
            filter_button.wait_for(state="visible", timeout=5000)
            filter_button.click()
            self.logger.info("✓ 点击 Filter 按钮成功")
            
            # 等待弹窗打开
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击 Filter 按钮失败: {e}")
            raise
    
    def select_property_type_in_filter_modal(self, property_type="House"):
        """
        在 Filter 弹窗中选择 Property Type
        按照手动执行方式：在弹窗中直接定位文本并点击
        
        Args:
            property_type: 房产类型，如 "House", "Townhomes" 等
        """
        try:
            # 按照手动执行方式：在弹窗中定位 Property Type
            # 手动执行时定位的是：generic [ref=e335] [cursor=pointer]: House
            modal = self.page.locator(self.FILTER_MODAL).first
            modal.wait_for(state="visible", timeout=5000)
            
            # 简单直接的方式：在弹窗内找到包含目标文本的可点击元素
            # 使用 :text() 过滤器，并确保元素有 cursor:pointer 样式
            property_type_option = modal.locator(f"text={property_type}").filter(has=self.page.locator("[style*='cursor: pointer'], [style*='cursor:pointer']")).first
            
            # 如果上述方法失败，尝试更宽松的选择器
            if not property_type_option.count():
                self.logger.warning(f"使用备用方案1查找 Property Type: {property_type}")
                # 在弹窗内查找所有包含目标文本的元素，排除 <a> 标签
                all_options = modal.locator(f"text={property_type}").all()
                for opt in all_options:
                    tag_name = opt.evaluate("el => el.tagName")
                    if tag_name != "A" and opt.is_visible():
                        property_type_option = opt
                        self.logger.info(f"找到 Property Type 选项（标签: {tag_name}）")
                        break
            
            # 如果还是失败，使用最简单的方法
            if not property_type_option or not property_type_option.count():
                self.logger.warning(f"使用备用方案2查找 Property Type: {property_type}")
                property_type_option = modal.locator(f"text={property_type}").nth(0)
            
            property_type_option.wait_for(state="visible", timeout=5000)
            
            # 滚动到元素可见位置并点击
            property_type_option.scroll_into_view_if_needed()
            self.page.wait_for_timeout(300)
            property_type_option.click(force=True)
            
            self.logger.info(f"✓ 选择 Property Type: {property_type} 成功")
            
            # 等待选中状态更新
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择 Property Type 失败: {e}")
            raise
    
    def select_beds_in_filter_modal(self, beds_value):
        """
        在 Filter 弹窗中选择 Beds 值
        按照手动执行方式：在弹窗中直接点击对应的 Beds 值
        
        Args:
            beds_value: Beds 数量，如 3
        """
        try:
            # 按照手动执行方式：在弹窗中定位 Beds 值
            modal = self.page.locator(self.FILTER_MODAL).first
            
            # 找到 Beds 标题所在的 filterItem 容器，然后在其中查找对应的值
            # 使用 XPath 定位到包含 "Beds" 文本的 filterItem
            beds_section = modal.locator("xpath=.//*[contains(@class, 'filterItem') and contains(., 'Beds')]")
            
            if not beds_section.count():
                self.logger.warning("未找到 Beds 区域，使用备用方案")
                beds_option = modal.locator(f"text=/^{beds_value}$/").first
            else:
                # 在 Beds 区域中查找对应的数字值
                beds_option = beds_section.locator(f"text=/^{beds_value}$/").first
            
            beds_option.wait_for(state="visible", timeout=5000)
            beds_option.scroll_into_view_if_needed()
            self.page.wait_for_timeout(300)
            beds_option.click()
            self.logger.info(f"✓ 选择 Beds: {beds_value} 成功")
            
            # 等待选中状态更新
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择 Beds 值失败: {e}")
            raise
    
    def select_bathrooms_in_filter_modal(self, bathrooms_value):
        """
        在 Filter 弹窗中选择 Bathrooms 值
        按照手动执行方式：在弹窗中直接点击对应的 Bathrooms 值
        
        Args:
            bathrooms_value: Bathrooms 数量，如 2 或 2.5
        """
        try:
            # 按照手动执行方式：在弹窗中定位 Bathrooms 值
            modal = self.page.locator(self.FILTER_MODAL).first
            
            # 找到 Bathrooms 标题所在的 filterItem 容器，然后在其中查找对应的值
            # 使用 XPath 定位到包含 "Bathrooms" 文本的 filterItem
            bathrooms_section = modal.locator("xpath=.//*[contains(@class, 'filterItem') and contains(., 'Bathrooms')]")
            
            if not bathrooms_section.count():
                self.logger.warning("未找到 Bathrooms 区域，使用备用方案")
                # 查找所有匹配的数字，选择第二个（跳过 Beds 区域的）
                all_matches = modal.locator(f"text=/^{bathrooms_value}$/").all()
                if len(all_matches) > 1:
                    bathrooms_option = all_matches[1]
                else:
                    bathrooms_option = all_matches[0] if all_matches else None
            else:
                # 在 Bathrooms 区域中查找对应的数字值
                bathrooms_option = bathrooms_section.locator(f"text=/^{bathrooms_value}$/").first
            
            if not bathrooms_option:
                raise Exception(f"未找到 Bathrooms 值: {bathrooms_value}")
            
            bathrooms_option.wait_for(state="visible", timeout=5000)
            bathrooms_option.scroll_into_view_if_needed()
            self.page.wait_for_timeout(300)
            bathrooms_option.click()
            self.logger.info(f"✓ 选择 Bathrooms: {bathrooms_value} 成功")
            
            # 等待选中状态更新
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择 Bathrooms 值失败: {e}")
            raise
    
    def input_price_in_filter_modal(self, min_price=None, max_price=None):
        """
        在 Filter 弹窗中填写 Price 范围
        按照手动执行方式：在弹窗中定位输入框并填写价格
        
        Args:
            min_price: 最低价格
            max_price: 最高价格
        """
        try:
            # 按照手动执行方式：在弹窗中定位 Price 输入框
            # 手动执行时定位的是：textbox "Min" [ref=e355] 和 textbox "Max" [ref=e358]
            modal = self.page.locator(self.FILTER_MODAL).first
            
            if min_price is not None:
                min_input = modal.locator("input[placeholder='Min'], textbox:has-text('Min')").first
                min_input.wait_for(state="visible", timeout=5000)
                min_input.fill(str(min_price))
                self.logger.info(f"✓ 填写 Min Price: {min_price} 成功")
                self.page.wait_for_timeout(300)
            
            if max_price is not None:
                max_input = modal.locator("input[placeholder='Max'], textbox:has-text('Max')").first
                max_input.wait_for(state="visible", timeout=5000)
                max_input.fill(str(max_price))
                self.logger.info(f"✓ 填写 Max Price: {max_price} 成功")
                self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"填写 Price 范围失败: {e}")
            raise
    
    def click_done_button_in_filter_modal(self):
        """
        点击 Filter 弹窗中的 Done 按钮
        按照手动执行方式：直接定位并点击 Done 按钮
        """
        try:
            # 按照手动执行方式：直接定位 Done 按钮
            # 手动执行时定位的是：button "Done" [ref=e412]
            done_button = self.page.locator(self.FILTER_MODAL_DONE_BUTTON).first
            done_button.wait_for(state="visible", timeout=5000)
            done_button.click()
            self.logger.info("✓ 点击 Done 按钮成功")
            
            # 等待弹窗关闭和页面更新
            self.page.wait_for_timeout(2000)
            self.wait_for_page_load(state="domcontentloaded")
        except Exception as e:
            self.logger.error(f"点击 Done 按钮失败: {e}")
            raise
    
    def get_filter_display_text(self):
        """
        获取 Filter 按钮的显示文本（如 "Filter·5"）
        按照手动执行方式：查找包含 Filter 和计数的文本
        
        Returns:
            str: Filter 显示文本
        """
        try:
            # 按照手动执行方式：查找 Filter 按钮的显示文本
            # 手动执行时看到的是：text: Filter, generic [ref=e63]: ·, text: "5"
            
            # 尝试多种选择器
            selectors = [
                "text=/Filter·/i",
                "*:has-text('Filter·')",
                "*:has-text('Filter') >> xpath=.."
            ]
            
            for selector in selectors:
                try:
                    elements = self.page.locator(selector).all()
                    for element in elements:
                        try:
                            if element.is_visible(timeout=2000):
                                text = element.inner_text().strip()
                                # 验证文本包含 Filter 和数字
                                if "Filter" in text and len(text) < 50:
                                    return text
                        except Exception:
                            continue
                except Exception:
                    continue
            
            return ""
        except Exception as e:
            self.logger.error(f"获取 Filter 显示文本失败: {e}")
            return ""
    
    def click_clear_button_in_filter_modal(self):
        """
        点击 Filter 弹窗中的 Clear 按钮
        按照手动执行方式：直接点击 Clear 按钮
        """
        try:
            # 按照手动执行方式：直接点击 Clear 按钮
            clear_button = self.page.locator(self.FILTER_MODAL_CLEAR_BUTTON).first
            clear_button.wait_for(state="visible", timeout=5000)
            clear_button.click()
            self.logger.info("✓ 点击 Filter 弹窗中的 Clear 按钮成功")
            # 等待清除操作生效
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击 Clear 按钮失败: {e}")
            raise
    
    def close_filter_modal_by_x_button(self):
        """
        点击 X 按钮关闭 Filter 弹窗
        按照手动执行方式：直接点击右上角的 X 按钮
        """
        try:
            # 按照手动执行方式：定位弹窗右上角的关闭按钮
            # 常见的选择器：关闭图标、X 按钮
            close_selectors = [
                "[role='dialog'] button[aria-label='Close']",
                "[role='dialog'] img[cursor='pointer']",  # 根据手动执行看到的 img [ref=e324] [cursor=pointer]
                ".modal button.close",
                "[class*='modal'] [class*='close']",
                "[role='dialog'] [class*='close']"
            ]
            
            modal = self.page.locator(self.FILTER_MODAL).first
            
            for selector in close_selectors:
                try:
                    close_button = modal.locator(selector).first
                    if close_button.is_visible(timeout=2000):
                        close_button.click()
                        self.logger.info("✓ 点击 X 按钮关闭 Filter 弹窗成功")
                        self.page.wait_for_timeout(1000)
                        return
                except Exception:
                    continue
            
            # 如果上述选择器都不成功，尝试通用方式
            raise Exception("未找到关闭按钮")
        except Exception as e:
            self.logger.error(f"点击 X 按钮关闭弹窗失败: {e}")
            raise
    
    def click_blank_area_to_close_filter_modal(self):
        """
        点击弹窗外区域关闭 Filter 弹窗
        按照手动执行方式：点击弹窗外的遮罩层或页面空白区域
        """
        try:
            # 按照手动执行方式：点击弹窗外的区域关闭弹窗
            # 获取弹窗元素
            modal = self.page.locator(self.FILTER_MODAL).first
            modal.wait_for(state="visible", timeout=3000)
            
            # 尝试多种方法关闭弹窗
            # 方法1：点击固定的安全位置（左上角）
            try:
                self.logger.info("尝试方法1: 点击页面左上角 (10, 10)")
                self.page.mouse.click(10, 10)
                self.page.wait_for_timeout(800)
                if not self.is_filter_modal_visible():
                    self.logger.info("✓ 点击页面左上角成功关闭弹窗")
                    return
            except Exception as e:
                self.logger.warning(f"方法1失败: {e}")
            
            # 方法2：点击页面中心左侧
            try:
                self.logger.info("尝试方法2: 点击页面左侧中心 (50, 400)")
                self.page.mouse.click(50, 400)
                self.page.wait_for_timeout(800)
                if not self.is_filter_modal_visible():
                    self.logger.info("✓ 点击页面左侧中心成功关闭弹窗")
                    return
            except Exception as e:
                self.logger.warning(f"方法2失败: {e}")
            
            # 方法3：按 ESC 键
            try:
                self.logger.info("尝试方法3: 按 ESC 键")
                self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(800)
                if not self.is_filter_modal_visible():
                    self.logger.info("✓ 按 ESC 键成功关闭弹窗")
                    return
            except Exception as e:
                self.logger.warning(f"方法3失败: {e}")
            
            # 方法4：点击页面右上角
            try:
                self.logger.info("尝试方法4: 点击页面右上角")
                self.page.mouse.click(1800, 10)
                self.page.wait_for_timeout(800)
                if not self.is_filter_modal_visible():
                    self.logger.info("✓ 点击页面右上角成功关闭弹窗")
                    return
            except Exception as e:
                self.logger.warning(f"方法4失败: {e}")
            
            # 如果所有方法都失败
            if self.is_filter_modal_visible():
                raise Exception("无法通过任何方法关闭弹窗")
            else:
                self.logger.info("✓ 弹窗已关闭")
                
        except Exception as e:
            self.logger.error(f"点击弹窗外区域关闭弹窗失败: {e}")
            raise
    
    def is_filter_modal_visible(self):
        """
        检查 Filter 弹窗是否可见
        按照手动执行方式：检查弹窗元素是否可见
        
        Returns:
            bool: 弹窗是否可见
        """
        try:
            # 检查 Done 按钮是否可见（作为弹窗打开的标志）
            modal = self.page.locator(self.FILTER_MODAL).first
            return modal.is_visible(timeout=2000)
        except Exception as e:
            self.logger.warning(f"检查 Filter 弹窗可见性失败: {e}")
            return False
    
    # ========== 搜索框功能（Property Buy）==========
    
    def input_search_keyword(self, keyword, slow=False):
        """
        输入搜索关键词
        Args:
            keyword: 要输入的关键词
            slow: 是否逐字符输入（用于触发 SUG 下拉），默认 False 使用快速 fill
        """
        try:
            search_input = self.page.locator(self.SEARCH_INPUT).first
            search_input.click()
            if slow:
                # 逐字符输入，触发实时 SUG 建议
                search_input.type(keyword, delay=120)
            else:
                # 快速填充
                search_input.fill(keyword)
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"输入搜索关键词失败: {e}")
            raise

    def get_search_input_value(self):
        """获取搜索框当前的值"""
        try:
            return self.page.locator(self.SEARCH_INPUT).first.input_value()
        except Exception as e:
            self.logger.error(f"获取搜索框值失败: {e}")
            return ""
    
    def click_search_button(self):
        """点击搜索按钮"""
        try:
            self.page.locator(self.SEARCH_BUTTON).first.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击搜索按钮失败: {e}")
            raise
    
    def press_enter_in_search(self):
        """在搜索框中按回车键"""
        try:
            self.page.locator(self.SEARCH_INPUT).first.press("Enter")
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"按回车键失败: {e}")
            raise
    
    def get_search_input_value(self):
        """获取搜索框的值"""
        try:
            return self.page.locator(self.SEARCH_INPUT).first.input_value()
        except Exception as e:
            self.logger.error(f"获取搜索框值失败: {e}")
            return ""
    
    def clear_search_input(self):
        """清空搜索框"""
        try:
            search_input = self.page.locator(self.SEARCH_INPUT).first
            search_input.click()
            search_input.fill("")
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"清空搜索框失败: {e}")
            raise
    
    def click_category_dropdown(self):
        """点击分类下拉按钮（搜索框左侧）"""
        try:
            # 根据用户截图：搜索框左侧有图标+文本(Rent/Sale)+下拉箭头的按钮
            # 尝试多种选择器策略
            selectors = [
                # 策略1: 文本包含 Rent 或 Sale 的按钮
                "button:has-text('Rent')",
                "button:has-text('Sale')",
                
                # 策略2: 包含图标的按钮（房子图标）
                "button:has([class*='icon'])",
                "button svg",  # 包含SVG图标的按钮
                
                # 策略3: 基于位置 - 搜索框前面的按钮
                "input[placeholder='Search for anything'] >> xpath=preceding-sibling::button[1]",
                "input[placeholder='Search for anything'] ~ button",
                
                # 策略4: 基于class属性
                "[class*='category'] button",
                "[class*='dropdown'] button",
                "[class*='select'] button",
                "[class*='PropertyTopBar'] button",
                
                # 策略5: 通用 - 搜索框所在容器内的所有按钮
                "button",
            ]
            
            for selector in selectors:
                try:
                    self.logger.debug(f"尝试选择器: {selector}")
                    elements = self.page.locator(selector).all()
                    
                    # 遍历所有匹配的元素，找到包含 Rent 或 Sale 文本的
                    for elem in elements:
                        try:
                            if not elem.is_visible(timeout=1000):
                                continue
                            
                            text = elem.inner_text().strip()
                            html = elem.evaluate("el => el.outerHTML")
                            
                            # 检查是否是分类按钮（包含 Rent 或 Sale）
                            if any(keyword in text for keyword in ['Rent', 'Sale', 'Buy']):
                                self.logger.info(f"✓ 找到分类按钮（选择器: {selector}）: '{text}'")
                                elem.click()
                                self.page.wait_for_timeout(500)
                                return True
                        except:
                            continue
                except Exception as e:
                    self.logger.debug(f"选择器 {selector} 失败: {e}")
                    continue
            
            raise Exception("未找到分类下拉按钮")
            
        except Exception as e:
            self.logger.error(f"点击分类下拉失败: {e}")
            raise
    
    def is_sug_panel_visible(self):
        """检查 sug 词面板是否可见"""
        try:
            return self.page.locator(self.SUG_PANEL).first.is_visible(timeout=2000)
        except:
            return False
    
    def get_sug_items_count(self):
        """获取 sug 词列表数量"""
        try:
            if self.is_sug_panel_visible():
                items = self.page.locator(self.SUG_ITEM).all()
                count = len(items)
                self.logger.info(f"找到 {count} 个地址建议项")
                
                # 记录前几个项的文本以便调试
                for i, item in enumerate(items[:5]):
                    try:
                        text = item.inner_text().strip()
                        self.logger.info(f"  sug 项 [{i}]: {text}")
                    except:
                        pass
                
                return count
            return 0
        except Exception as e:
            self.logger.warning(f"获取 sug 词数量失败: {e}")
            return 0

    def get_sug_item_text(self, index=0):
        """获取指定 sug 词的文本"""
        try:
            items = self.page.locator(self.SUG_ITEM).all()
            if index < len(items):
                return items[index].inner_text().strip()
            return ""
        except Exception as e:
            self.logger.error(f"获取 sug 词文本失败: {e}")
            return ""

    def click_sug_item(self, index=0):
        """点击 sug 词列表中的某一项"""
        try:
            items = self.page.locator(self.SUG_ITEM).all()
            if index < len(items):
                item = items[index]
                text = item.inner_text().strip()
                self.logger.info(f"准备点击第 {index} 个地址 sug 词: '{text}'")
                item.click()
                self.page.wait_for_timeout(500)
                self.logger.info(f"✓ 已点击地址 sug 词: '{text}'")
                return text
            else:
                self.logger.warning(f"没有找到索引为 {index} 的地址 sug 词")
                return None
        except Exception as e:
            self.logger.error(f"点击 sug 词失败: {e}")
            raise
    
    def press_arrow_down_in_sug(self):
        """在 sug 面板中按下方向键"""
        try:
            self.page.keyboard.press("ArrowDown")
            self.page.wait_for_timeout(200)
        except Exception as e:
            self.logger.error(f"按下方向键失败: {e}")
            raise
    
    def press_escape_in_sug(self):
        """按 Esc 键关闭 sug 面板"""
        try:
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"按 Esc 键失败: {e}")
            raise
    
    def is_search_history_visible(self):
        """检查搜索历史面板是否可见"""
        try:
            return self.page.locator(self.SEARCH_HISTORY_PANEL).first.is_visible(timeout=2000)
        except:
            return False
    
    def get_search_history_count(self):
        """获取搜索历史数量（最多10条）"""
        try:
            if not self.is_search_history_visible():
                return 0
            
            # 尝试多个选择器
            selectors = [
                "[class*='PropertySearchHistory_item']",
                "[class*='RecentSearches'] [class*='item']",
                "[class*='search-history'] [class*='item']",
                "div:has-text('Recent Searches') ~ div",
            ]
            
            for selector in selectors:
                try:
                    count = self.page.locator(selector).count()
                    if count > 0 and count <= 10:  # 历史记录最多10条
                        self.logger.info(f"使用选择器 '{selector}' 找到 {count} 条历史记录")
                        return count
                except:
                    continue
            
            return 0
        except Exception as e:
            self.logger.warning(f"获取搜索历史数量失败: {e}")
            return 0
    
    def click_search_history_item(self, index=0):
        """点击搜索历史项"""
        try:
            self.page.locator(self.SEARCH_HISTORY_ITEM).nth(index).click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击搜索历史项失败: {e}")
            raise
    
    def clear_search_history(self):
        """清除搜索历史"""
        try:
            self.page.locator(self.SEARCH_HISTORY_CLEAR).first.click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"清除搜索历史失败: {e}")
            raise
    
    def click_list_button(self):
        """点击 List 模式按钮"""
        try:
            self.page.locator(self.LIST_BUTTON).first.click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击 List 按钮失败: {e}")
            raise
    
    def click_map_button(self):
        """点击 Map 模式按钮"""
        try:
            self.page.locator(self.MAP_BUTTON).first.click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击 Map 按钮失败: {e}")
            raise
    
    def click_page_number(self, page_num):
        """点击页码链接"""
        try:
            self.page.locator(f"a:has-text('{page_num}')").first.click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击页码 {page_num} 失败: {e}")
            raise
    
    def select_category(self, category_name):
        """
        选择分类（如 Rent, Sale, Student Accommodation 等）
        
        Args:
            category_name: 分类名称，如 "Property For Rent", "Property For Sale", "Student Accommodation"
        """
        try:
            # 1. 先点击分类下拉按钮（根据用户截图和实际页面优化）
            # 实际页面显示：搜索框左侧有独立的 "Rent" 或 "Sale" 按钮
            # 该按钮不是标准的button元素，可能是div或其他元素
            
            # 策略：查找包含 "Rent" 或 "Sale" 文本的可点击元素
            # 必须排除页面其他地方的同名元素（如导航链接、表单名称等）
            button_clicked = False
            
            # 尝试直接通过文本点击（最有可能成功）
            try:
                # 查找所有包含 Rent/Sale 文本的元素
                for text in ['Rent', 'Sale', 'Buy']:
                    try:
                        # 使用 :visible 和 位置筛选，确保点击的是顶部导航栏的按钮
                        candidates = self.page.get_by_text(text, exact=False).all()
                        
                        for candidate in candidates:
                            try:
                                if not candidate.is_visible(timeout=500):
                                    continue
                                
                                # 获取元素的boundingbox，确保它在页面顶部（y < 200）
                                box = candidate.bounding_box()
                                if box and box['y'] < 200:  # 顶部导航区域
                                    self.logger.info(f"尝试点击分类按钮（文本: {text}）")
                                    candidate.click()
                                    button_clicked = True
                                    self.logger.info(f"✓ 已点击分类按钮: {text}")
                                    break
                            except:
                                continue
                        
                        if button_clicked:
                            break
                    except:
                        continue
            except Exception as e:
                self.logger.debug(f"文本定位失败: {e}")
            
            if not button_clicked:
                raise Exception("未找到分类下拉按钮")
            
            self.page.wait_for_timeout(800)  # 等待下拉菜单展开
            
            # 2. 点击目标分类
            # 根据截图，菜单项包含 "Property For Rent", "Property For Sale", "Student Accommodation" 等
            category_selectors = [
                f"text={category_name}",  # 精确文本匹配
                f"a:has-text('{category_name}')",
                f"button:has-text('{category_name}')",
                f"[role='menuitem']:has-text('{category_name}')",
                f"li:has-text('{category_name}')",
                f"div:has-text('{category_name}')",
            ]
            
            category_clicked = False
            for selector in category_selectors:
                try:
                    item = self.page.locator(selector).first
                    if item.is_visible(timeout=2000):
                        self.logger.info(f"尝试点击分类项: {selector}")
                        item.click()
                        category_clicked = True
                        self.logger.info(f"✓ 已选择分类: {category_name}（选择器: {selector}）")
                        break
                except Exception as e:
                    self.logger.debug(f"选择器 {selector} 失败: {e}")
                    continue
            
            if not category_clicked:
                raise Exception(f"未找到分类选项: {category_name}")
            
            # 等待页面跳转
            self.page.wait_for_timeout(1500)
            self.page.wait_for_load_state('domcontentloaded', timeout=10000)
            self.logger.info(f"✓ 分类切换完成: {category_name}")
            
        except Exception as e:
            self.logger.error(f"选择分类 {category_name} 失败: {e}")
            # 尝试截图以便调试
            try:
                screenshot_path = f"/tmp/category_select_error_{int(time.time())}.png"
                self.page.screenshot(path=screenshot_path)
                self.logger.info(f"已保存错误截图: {screenshot_path}")
            except:
                pass
            raise

    # ====================================================================
    # 房产列表页入口：金刚位 / All 类目页 / Browse 下拉菜单
    # 录制来源：https://au.58v5.cn/en/city-canberra/
    # 录制时间：2026-03-13
    # ====================================================================

    # ========== 入口选择器（MCP 实测）==========
    HOME_PAGE_CANBERRA = "https://au.58v5.cn/en/city-canberra/"

    # 入口1 - 金刚位 Property（href 精确匹配，避免 Browse 菜单同名链接干扰）
    CATEGORY_ICON_PROPERTY = "a[href*='cate-property'][href*='iconSource=buy']"
    # 入口2 - All 类目页图标
    CATEGORY_ICON_ALL = "a[href*='/listpage/']"

    # 入口3 - Browse 导航
    BROWSE_BUTTON_TEXT = "Browse"

    # ========== 入口1 方法 ==========

    def navigate_to_home(self):
        """导航到 Canberra 首页并处理 Cookie 弹窗"""
        self.page.goto(self.HOME_PAGE_CANBERRA, timeout=30000)
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self.handle_cookie_popup()
        self.page.wait_for_timeout(1000)

    def click_category_icon_property(self):
        """
        点击金刚位「Property」图标 → 进入 Property For Sale 列表
        MCP JS: await page.getByRole('link', { name: 'Property Property' }).click();
        """
        self.page.locator(self.CATEGORY_ICON_PROPERTY).first.click()
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)

    # ========== 入口2 方法 ==========

    def click_category_icon_all(self):
        """
        点击金刚位「All」图标 → 进入全类目 listpage
        MCP JS: await page.getByRole('link', { name: 'All All' }).click();
        """
        self.page.locator(self.CATEGORY_ICON_ALL).first.click()
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)

    def click_listpage_property_for_sale(self):
        """
        在 listpage 中点击「Property For Sale」链接
        MCP JS: await page.getByRole('link', { name: 'Property For Sale' }).click();
        """
        self.page.get_by_role("link", name="Property For Sale").first.click()
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)

    def click_listpage_property_for_rent(self):
        """
        在 listpage 中点击「Property For Rent」链接
        MCP JS: await page.getByRole('link', { name: 'Property For Rent' }).click();
        """
        self.page.get_by_role("link", name="Property For Rent").first.click()
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)

    def click_listpage_student_accommodation(self):
        """
        在 listpage 中点击「Student Accommodation」链接
        MCP JS: await page.getByRole('link', { name: 'Student Accommodation' }).click();
        """
        self.page.get_by_role("link", name="Student Accommodation").first.click()
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)

    def click_listpage_commercial_for_sale(self):
        """
        在 listpage 中点击「Commercial Property for sale」链接
        MCP JS: await page.getByRole('link', { name: 'Commercial Property for sale' }).click();
        """
        self.page.get_by_role("link", name="Commercial Property for sale").first.click()
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)

    # ========== 入口3 方法 ==========

    def click_browse_button(self):
        """
        点击顶部导航「Browse ▾」按钮展开下拉菜单
        MCP JS: await page.getByText('Browse').click();
        """
        self.page.get_by_text("Browse").click()
        self.page.wait_for_timeout(600)

    def hover_browse_property(self):
        """
        在 Browse 下拉中将鼠标悬浮到「Property」一级分类上，展开右侧子菜单
        MCP JS: await page.getByRole('link', { name: 'Property', exact: true }).hover();
        """
        self.page.get_by_role("link", name="Property", exact=True).hover()
        self.page.wait_for_timeout(500)  # hover 不触发页面跳转，只需短暂等待子菜单展开

    def click_browse_property_direct(self):
        """
        在 Browse 下拉中直接点击「Property」一级链接（不 hover，TC014）
        MCP JS: await page.getByRole('link', { name: 'Property', exact: true }).click();
        """
        self.page.get_by_role("link", name="Property", exact=True).click()
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)

    def click_browse_submenu_property_for_rent(self):
        """
        在 Browse > Property 子菜单中点击「Property For Rent」
        MCP JS: await page.getByRole('link', { name: 'Property For Rent' }).click();
        使用 href 精确匹配避免 strict mode（与 Commercial Property for rent 的名称前缀冲突）
        """
        self.page.locator("a[href*='cate-rent'][href*='iconSource=rent']").first.click()
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)

    def click_browse_submenu_property_for_sale(self):
        """
        在 Browse > Property 子菜单中点击「Property For Sale」
        MCP JS: await page.getByRole('link', { name: 'Property For Sale' }).click();
        使用 href 精确匹配避免 strict mode（与 Commercial Property for sale 的名称前缀冲突）
        """
        self.page.locator("a[href*='cate-buy'][href*='iconSource=buy']").first.click()
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)

    def click_browse_submenu_student_accommodation(self):
        """
        在 Browse > Property 子菜单中点击「Student Accommodation」
        MCP JS: await page.getByRole('link', { name: 'Student Accommodation' }).click();
        """
        self.page.get_by_role("link", name="Student Accommodation").click()
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)

    def click_browse_submenu_commercial_for_sale(self):
        """
        在 Browse > Property 子菜单中点击「Commercial Property for sale」
        MCP JS: await page.getByRole('link', { name: 'Commercial Property for sale' }).click();
        """
        self.page.get_by_role("link", name="Commercial Property for sale").click()
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)

    # ========== 入口断言辅助方法 ==========

    def get_page_h1(self) -> str:
        """获取页面 H1 标题文本"""
        try:
            return self.page.locator("h1").first.inner_text().strip()
        except Exception:
            return ""

    def is_browse_dropdown_visible(self) -> bool:
        """检查 Browse 下拉菜单是否已展开（通过 Property 一级链接可见性判断）"""
        try:
            return self.page.get_by_role("link", name="Property", exact=True).is_visible(timeout=3000)
        except Exception:
            return False

    def is_browse_property_submenu_visible(self) -> bool:
        """检查 Browse > Property 子菜单是否已展开（通过 Property For Rent 链接可见性判断）"""
        try:
            return self.page.get_by_role("link", name="Property For Rent").is_visible(timeout=3000)
        except Exception:
            return False

    def get_browse_property_submenu_link_names(self) -> list:
        """
        返回 Browse > Property 子菜单中所有可见链接名称列表
        使用 href 精确匹配代替 name 匹配，避免 "Commercial Property for rent" 与
        "Property For Rent" 的 get_by_role 名称前缀歧义
        """
        href_map = {
            "Property For Rent": "cate-rent/?iconSource=rent",
            "Property For Sale": "cate-buy/?iconSource=buy",
            "Student Accommodation": "cate-student-apartment/?iconSource=student-apartment",
            "Commercial Property for sale": "cate-commercial-buy/?iconSource=commercial-buy",
            "Commercial Property for rent": "cate-commercial-rent/?iconSource=commercial-rent",
        }
        visible = []
        for name, href_fragment in href_map.items():
            try:
                if self.page.locator(f"a[href*='{href_fragment}']").first.is_visible(timeout=5000):
                    visible.append(name)
            except Exception:
                pass
        return visible

    def get_listpage_property_link_names(self) -> list:
        """
        返回全类目页（listpage）中 Property 区块所有可见链接名称列表
        使用 href 匹配确保稳定性（listpage 链接无 iconSource 参数）
        """
        href_map = {
            "Property For Rent": "cate-rent",
            "Property For Sale": "cate-buy",
            "Student Accommodation": "cate-student-apartment",
            "Commercial Property for sale": "cate-commercial-buy",
            "Commercial Property for rent": "cate-commercial-rent",
        }
        visible = []
        for name, href_fragment in href_map.items():
            try:
                if self.page.locator(f"a[href*='{href_fragment}']").first.is_visible(timeout=5000):
                    visible.append(name)
            except Exception:
                pass
        return visible

