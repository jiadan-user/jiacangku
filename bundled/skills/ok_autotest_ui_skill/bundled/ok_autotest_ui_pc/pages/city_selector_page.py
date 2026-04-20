# pages/city_selector_page.py
from pages.base_page import BasePage
from utils.logger import setup_logger


class CitySelectorPage(BasePage):
    """城市选择器页面对象"""
    
    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()
    
    # ========== 城市选择器元素 ==========
    # 右上角的定位模块
    LOCATION_MODULE = ".TopBarRightContent_locationModule__i97Cs"
    LOCATION_TEXT = ".LocationDropdwon_locationText__I_2t0"
    
    # 城市下拉弹窗（点击定位图标后出现）
    CITY_POPOVER = ".HoverPopup_customPopover__lbYFg"
    
    # 城市选项（在 popover 中）
    CITY_ITEM = ".AnchorSelector_itemValue__RHcGB"  # 城市列表项
    
    # ========== 城市选择器操作方法 ==========
    
    def click_location_module(self):
        """点击右上角的定位模块打开城市选择器"""
        try:
            location_module = self.page.locator(self.LOCATION_MODULE).first
            location_module.wait_for(state="visible", timeout=10000)
            
            # 方案1: 使用 JavaScript 直接触发 mouseover 和 click 事件（适用于无头模式）
            try:
                self.logger.info("尝试使用 JavaScript 触发事件")
                self.page.evaluate('''() => {
                    const locationModule = document.querySelector('.TopBarRightContent_locationModule__i97Cs');
                    if (locationModule) {
                        // 触发 mouseover 事件
                        locationModule.dispatchEvent(new MouseEvent('mouseover', {
                            view: window,
                            bubbles: true,
                            cancelable: true
                        }));
                        
                        // 短暂延迟后触发 click 事件
                        setTimeout(() => {
                            locationModule.dispatchEvent(new MouseEvent('mouseenter', {
                                view: window,
                                bubbles: true,
                                cancelable: true
                            }));
                            locationModule.click();
                        }, 100);
                    }
                }''')
                
                # 等待弹窗出现
                self.page.wait_for_timeout(2000)
                self.logger.info("✓ 使用 JavaScript 触发定位模块事件")
                
            except Exception as e:
                # 方案2: 回退到原生 hover + click
                self.logger.info(f"JavaScript 方案失败，使用原生方法: {e}")
                location_module.hover()
                self.page.wait_for_timeout(500)
                location_module.click()
                self.page.wait_for_timeout(2000)
                self.logger.info("✓ 点击定位模块（原生方法）")
                
        except Exception as e:
            self.logger.error(f"点击定位模块失败: {e}")
            raise
    
    def select_city(self, city_name: str):
        """
        选择指定城市
        
        Args:
            city_name: 城市名称（如 "Ajman", "Dubai", "Abu Dhabi"）
        """
        try:
            # 步骤1: 点击定位模块，打开城市 Popover
            self.click_location_module()
            
            # 步骤2: 等待更长时间确保 Popover 完全渲染
            self.page.wait_for_timeout(2000)
            
            # 步骤3: 尝试多种方式查找城市选项
            clicked = False
            
            # 方案1: 使用精确的城市项选择器
            try:
                city_items = self.page.locator(self.CITY_ITEM)
                count = city_items.count()
                
                if count > 0:
                    self.logger.info(f"找到 {count} 个城市选项（使用 CITY_ITEM 选择器）")
                    
                    for i in range(count):
                        item = city_items.nth(i)
                        try:
                            if item.is_visible(timeout=1000):
                                item_text = item.inner_text().strip()
                                if item_text == city_name:
                                    item.click()
                                    clicked = True
                                    self.logger.info(f"✓ 点击城市选项: {city_name}")
                                    break
                        except Exception:
                            continue
            except Exception as e:
                self.logger.debug(f"方案1失败: {e}")
            
            # 方案2: 使用 text 定位器（备用）
            if not clicked:
                self.logger.info(f"尝试备用方案：使用 text 定位器查找 {city_name}")
                try:
                    city_option = self.page.locator(f"text={city_name}")
                    count = city_option.count()
                    
                    if count > 0:
                        self.logger.info(f"找到 {count} 个包含 {city_name} 的元素")
                        
                        # 遍历所有匹配元素，找到精确匹配且可点击的
                        for i in range(count):
                            elem = city_option.nth(i)
                            try:
                                if elem.is_visible(timeout=1000):
                                    elem_text = elem.inner_text().strip()
                                    if elem_text == city_name:
                                        elem.click()
                                        clicked = True
                                        self.logger.info(f"✓ 点击城市选项（备用方案）: {city_name}")
                                        break
                            except Exception:
                                continue
                except Exception as e:
                    self.logger.debug(f"方案2失败: {e}")
            
            # 方案3: URL 直接切换 + 点击页面元素以设置 Cookie（最终回退方案）
            if not clicked:
                self.logger.info(f"UI 交互失败，使用 URL 直接切换 + 页面交互设置 Cookie")
                city_url_map = {
                    "Ajman": "/en/city-ajman/",
                    "Dubai": "/en/city-dubai/",
                    "Abu Dhabi": "/en/city-abu-dhabi/",
                    "Sharjah": "/en/city-sharjah/",
                    "Fujairah": "/en/city-fujairah/",
                    "Ras al Khaimah": "/en/city-ras-al-khaimah/",
                    "Umm al Quwain": "/en/city-umm-al-quwain/"
                }
                
                if city_name in city_url_map:
                    # 从当前页面URL动态提取域名（支持 ok.com 和 58v5.cn）
                    current_url = self.page.url
                    if '/en/' in current_url:
                        base_url = current_url.split('/en/')[0]
                    else:
                        # 兜底：默认使用 ae.ok.com
                        base_url = "https://ae.ok.com"
                    
                    target_url = base_url + city_url_map[city_name]
                    self.page.goto(target_url, timeout=30000)
                    self.page.wait_for_load_state("domcontentloaded", timeout=30000)
                    self.page.locator("body").wait_for(state="visible", timeout=10000)
                    self.logger.info(f"✓ 通过 URL 访问 {city_name}: {target_url}")
                    
                    # 设置 localStorage 以模拟真实的城市选择（这样 Cookie/Storage 会被正确设置）
                    try:
                        city_data_map = {
                            "Ajman": '{"localId":"70848","name":"Ajman","parentName":"","code":"ajman"}',
                            "Dubai": '{"localId":"70840","name":"Dubai","parentName":"","code":"dubai"}',
                            "Abu Dhabi": '{"localId":"70839","name":"Abu Dhabi","parentName":"","code":"abu-dhabi"}',
                            "Sharjah": '{"localId":"70849","name":"Sharjah","parentName":"","code":"sharjah"}',
                        }
                        
                        if city_name in city_data_map:
                            city_data = city_data_map[city_name]
                            self.page.evaluate(f'''() => {{
                                localStorage.setItem(
                                    '__LOCATION_LOCAL_HISTORY_LIST_BY_COUNTRY_LANGUAGE___AE_en',
                                    '[{city_data}]'
                                );
                            }}''')
                            self.logger.info(f"✓ 设置 localStorage 以持久化城市选择")
                            
                            # 点击任意分类链接以触发页面路由（确保 localStorage 被读取）
                            category_link = self.page.locator('.QuickAccessArea_item__zFkuH').first
                            if category_link.is_visible(timeout=5000):
                                category_text = category_link.inner_text()
                                category_link.click()
                                self.page.wait_for_load_state("domcontentloaded", timeout=30000)
                                self.logger.info(f"✓ 点击金刚位 '{category_text}' 触发路由")
                                
                                # 返回首页
                                self.page.goto(base_url, timeout=30000)
                                self.page.wait_for_load_state("domcontentloaded", timeout=30000)
                                self.logger.info(f"✓ 返回首页")
                            else:
                                self.logger.info(f"⚠️ 未找到金刚位链接")
                    except Exception as e:
                        self.logger.debug(f"设置 localStorage 失败（非关键错误）: {e}")
                    
                    clicked = True
                else:
                    raise Exception(f"未找到城市选项且无对应URL映射: {city_name}")
            
            if not clicked:
                raise Exception(f"未找到城市选项: {city_name}")
            
            # 等待页面稳定
            self.page.wait_for_timeout(1000)
            self.page.locator("body").wait_for(state="visible", timeout=10000)
            
        except Exception as e:
            self.logger.error(f"选择城市 {city_name} 失败: {e}")
            raise
    
    def get_current_city_text(self):
        """获取当前显示的城市名称（从定位模块）"""
        try:
            return self.page.locator(self.LOCATION_TEXT).first.inner_text()
        except Exception as e:
            self.logger.error(f"获取当前城市文本失败: {e}")
            return None
    
    def get_current_city_from_url(self):
        """从 URL 中获取当前选择的城市"""
        try:
            url = self.page.url
            # URL 格式: https://ae.ok.com/en/city-ajman/ 或 https://ae.58v5.cn/en/city-ajman/
            if "/city-" in url:
                city_part = url.split("/city-")[1].split("/")[0]
                return city_part
            return None
        except Exception as e:
            self.logger.error(f"从URL获取城市失败: {e}")
            return None
