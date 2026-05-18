# pages/property_map_page.py
"""
Property Map 页面对象（地图模式排序筛选 - 通用）

适用于：Student Accommodation、Property For Rent 等支持地图模式的分类页
录制来源：https://au.58v5.cn/en/city-sydney/cate-student-apartment/?iconSource=student-apartment&view=map
录制时间：2026-03-05
"""
from pages.base_page import BasePage
from utils.logger import setup_logger


class PropertyMapPage(BasePage):
    """Property Map 地图模式页面对象（静默执行）"""

    # ========== Cookie 弹窗 ==========
    COOKIE_ACCEPT_BUTTON = "button:has-text('Accept all')"

    # ========== List / Map 视图切换 ==========
    LIST_BUTTON = "button.ViewToggle_listButton__siNOt"
    LIST_BUTTON_BACKUP = "button:has-text('List')"
    MAP_BUTTON = "button.ViewToggle_mapButton__B2cyp"
    MAP_BUTTON_BACKUP = "button:has-text('Map')"

    # ========== 筛选栏容器（FilterItem DIV）==========
    # 每个筛选项都是 [class*='FilterItem_filterItem'] 的 DIV
    FILTER_ITEM = "[class*='FilterItem_filterItem']"

    # ========== Sort / FilterItemOverlay 面板（Sort / Price / Beds / Bathrooms）==========
    FILTER_ITEM_OVERLAY = "[class*='FilterItemPC_filterItemOverlay']"
    OVERLAY_DONE_BUTTON = "[class*='FilterItemPC_btnArea'] button[type='submit']"
    OVERLAY_CLEAR_BUTTON = "[class*='FilterItemPC_btnArea'] button[type='reset']"

    # Sort 选项在 overlay 里
    SORT_OPTION_LABEL = "[class*='FilterItemPC_filterItemOverlay'] [class*='Selector_label']"

    # Price inputs 在 overlay 里
    PRICE_MIN_INPUT = "[class*='FilterItemPC_filterItemOverlay'] input[placeholder='Min']"
    PRICE_MAX_INPUT = "[class*='FilterItemPC_filterItemOverlay'] input[placeholder='Max']"

    # Beds / Bathrooms 选项 label 在 overlay 里（scoped，避免误点分页）
    BEDS_OPTION_CONTAINER = "[class*='FilterItemPC_filterItemOverlay'] [class*='Selector_selectorContainer']"
    BATHROOMS_OPTION_CONTAINER = "[class*='FilterItemPC_filterItemOverlay'] [class*='Selector_selectorContainer']"

    # ========== Property Type / Filter 综合 Modal ==========
    MODAL = "[role='dialog']"
    MODAL_CLOSE_BTN = "[class*='FilterModalPC_closeBtn']"
    MODAL_DONE_BUTTON = "[class*='FilterModalPC_btnArea'] button[type='submit']"
    MODAL_CLEAR_BUTTON = "[class*='FilterModalPC_btnArea'] button[type='reset']"

    # Property Type / Filter 分类选项（<b> 文本）
    MODAL_CATEGORY_OPTION = "[class*='FilterModalPC_categoryList'] a"

    # Filter 综合面板：Price / Beds / Bathrooms 区域
    FILTER_MODAL_PRICE_MIN = "[role='dialog'] input[placeholder='Min']"
    FILTER_MODAL_PRICE_MAX = "[role='dialog'] input[placeholder='Max']"
    FILTER_MODAL_BEDS_CONTAINER = "[role='dialog'] [class*='FilterModalPC_filterItem']:has([class*='FilterModalPC_filterItemTitle']:text-is('Beds')) [class*='Selector_selectorContainer']"
    FILTER_MODAL_BATH_CONTAINER = "[role='dialog'] [class*='FilterModalPC_filterItem']:has([class*='FilterModalPC_filterItemTitle']:text-is('Bathrooms')) [class*='Selector_selectorContainer']"

    # 筛选栏 Filter 按钮（含徽章）
    FILTER_BADGE_TEXT = "[class*='FilterItem_filterItem']:has-text('Filter') [class*='FilterItem_filterItemContent']"

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    # ========== 页面操作方法（静默执行）==========

    def navigate_to_map_page(self, url: str, timeout: int = 90000):
        """导航到地图模式页面（含重试机制，502/ERR_HTTP 时自动 skip）

        使用 domcontentloaded 而非 load，避免 Google Maps tiles/JS 资源
        拖慢整体导航超时；后续等待确保地图真正可用。
        """
        import pytest
        _502_keywords = ("ERR_HTTP_RESPONSE_CODE_FAILURE", "net::ERR_HTTP", "502")
        for attempt in range(2):
            try:
                self.page.goto(url, timeout=timeout, wait_until="domcontentloaded")
                # 额外等待给 Google Maps API 完成异步初始化时间
                self.page.wait_for_timeout(2000)
                self.logger.info(f"✓ 导航成功: {url}")
                # 检测 502 Bad Gateway 页面，服务器不可用时 skip 而非 fail
                title = self.page.title()
                if "502" in title or "Bad Gateway" in title:
                    pytest.skip(f"服务器返回 502 Bad Gateway，目标页面暂不可用: {url}")
                return
            except Exception as e:
                err_msg = str(e)
                # 502/网络错误直接 skip（重试也无意义）
                if any(kw in err_msg for kw in _502_keywords):
                    pytest.skip(f"服务器返回 HTTP 错误，目标页面暂不可用: {url} | {err_msg[:100]}")
                if attempt == 1:
                    self.logger.error(f"导航到地图模式页面失败: {e}")
                    raise
                self.page.wait_for_timeout(3000)

    def handle_cookie_popup(self):
        """处理 Cookie 弹窗（如存在），优先点击 'Accept all'，兼容 'Only essential'"""
        # 先等待一下，确保弹窗有足够时间渲染出来
        self.page.wait_for_timeout(500)
        
        for selector in [
            "button:has-text('Accept all')",
            "button:has-text('Only essential')",
        ]:
            try:
                btn = self.page.locator(selector).first
                if btn.is_visible(timeout=3000):  # 增加等待时间从 2s 到 3s
                    btn.click()
                    self.page.wait_for_timeout(1000)  # 增加关闭后等待从 800ms 到 1s
                    self.logger.info(f"✓ Cookie 弹窗已关闭（{selector}）")
                    return
            except Exception:
                continue

    def goto_map_and_handle_cookie(self, url: str, nav_timeout: int = 30000, wait_timeout: int = 10000):
        """导航到地图页，处理 Cookie 弹窗，等待地图区域可见。
        
        替代测试用例中裸 page.goto() + page.get_by_text('results') 的导航模式，
        统一在导航后处理 Cookie 弹窗，避免弹窗遮挡地图控件。
        """
        self.page.goto(url, timeout=nav_timeout, wait_until="domcontentloaded")
        self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        self.handle_cookie_popup()
        # 等待地图区域渲染（兼容没有 results 文字的情况）
        try:
            self.page.get_by_text("results").first.wait_for(state="visible", timeout=wait_timeout)
        except Exception:
            # results 文字不存在时，退而等待地图容器出现
            try:
                self.page.wait_for_selector(".gm-style", state="attached", timeout=wait_timeout)
            except Exception:
                pass

    # ---------- List / Map 视图切换 ----------

    def click_list_button(self):
        """点击 List 视图切换按钮"""
        try:
            self.page.locator(self.LIST_BUTTON).click()
        except Exception:
            self.page.locator(self.LIST_BUTTON_BACKUP).first.click()

    def click_map_button(self):
        """点击 Map 视图切换按钮（等待地图加载并生成 viewport 参数）"""
        try:
            self.page.locator(self.MAP_BUTTON).click()
        except Exception:
            self.page.locator(self.MAP_BUTTON_BACKUP).first.click()
        # 等待地图加载并生成 viewport 参数
        self.page.wait_for_timeout(2000)

    def is_map_view_active(self) -> bool:
        """判断当前是否处于地图模式（优先检查 DOM 状态，降级到 URL 参数）"""
        try:
            # 方式1：检查 Map 按钮是否有 active class
            try:
                map_btn = self.page.locator(self.MAP_BUTTON)
                # 检查按钮的 class 属性是否包含 active 标记
                class_attr = map_btn.get_attribute("class", timeout=3000)
                if class_attr and "active" in class_attr.lower():
                    return True
            except Exception:
                pass
            
            # 方式2：检查 URL 是否含 view=map（降级方案）
            url = self.page.url
            if "view=map" in url:
                return True
            
            # 方式3：检查是否存在地图容器元素
            try:
                map_container = self.page.locator("[class*='mapContainer'], [id*='map']").first
                if map_container.is_visible(timeout=2000):
                    # 如果地图容器可见但没有 view=map 参数，仍认为是地图模式
                    # 这种情况说明前端实现改变了，不再使用 URL 参数
                    return True
            except Exception:
                pass
            
            return False
        except Exception as e:
            self.logger.error(f"判断地图模式失败: {e}")
            return False

    def is_list_view_active(self) -> bool:
        """判断当前是否处于列表模式"""
        return "view=map" not in self.page.url

    # ---------- 内部工具：定位 FilterItem ----------

    def _get_filter_item(self, label_text: str):
        """
        通过起始文案定位筛选栏 FilterItem DIV（精确匹配开头，避免误匹配）
        """
        try:
            items = self.page.locator(self.FILTER_ITEM).all()
            for item in items:
                t = item.inner_text().strip()
                if t.startswith(label_text):
                    return item
            raise ValueError(f"未找到筛选项: {label_text}")
        except Exception as e:
            self.logger.error(f"定位 FilterItem '{label_text}' 失败: {e}")
            raise

    def _wait_overlay_visible(self, timeout: int = 5000):
        """等待 FilterItemOverlay 面板出现"""
        self.page.locator(self.FILTER_ITEM_OVERLAY).first.wait_for(
            state="visible", timeout=timeout
        )

    def _wait_overlay_hidden(self, timeout: int = 5000):
        """等待 FilterItemOverlay 面板消失"""
        try:
            self.page.locator(self.FILTER_ITEM_OVERLAY).first.wait_for(
                state="hidden", timeout=timeout
            )
        except Exception:
            pass

    # ---------- Sort 排序 ----------

    def click_sort_filter(self):
        """点击排序筛选项（Best Match / Newest First / ...）展开面板"""
        try:
            self._get_filter_item("Best Match").click()
            self._wait_overlay_visible()
        except Exception:
            # 已选择非默认排序时，按钮文案不是 Best Match
            items = self.page.locator(self.FILTER_ITEM).all()
            for item in items:
                t = item.inner_text().strip()
                if any(s in t for s in ["Best Match", "Newest First", "Lowest Price", "Highest Price"]):
                    item.click()
                    self._wait_overlay_visible()
                    return
            raise

    def select_sort_option(self, option_text: str):
        """
        在排序面板中选择指定选项
        option_text: 'Best Match' / 'Newest First' / 'Lowest Price' / 'Highest Price'
        """
        try:
            overlay = self.page.locator(self.FILTER_ITEM_OVERLAY).first
            overlay.locator(f"[class*='Selector_label']:text-is('{option_text}')").click()
        except Exception as e:
            self.logger.error(f"选择排序选项 '{option_text}' 失败: {e}")
            raise

    def click_sort_done(self):
        """点击排序面板 Done 按钮"""
        try:
            self.page.locator(self.OVERLAY_DONE_BUTTON).click()
            self._wait_overlay_hidden()
        except Exception as e:
            self.logger.error(f"点击排序 Done 按钮失败: {e}")
            raise

    def click_sort_clear(self):
        """点击排序面板 Clear 按钮"""
        try:
            self.page.locator(self.OVERLAY_CLEAR_BUTTON).click()
        except Exception as e:
            self.logger.error(f"点击排序 Clear 按钮失败: {e}")
            raise

    def get_current_sort_text(self) -> str:
        """获取排序按钮当前显示文案"""
        try:
            items = self.page.locator(self.FILTER_ITEM).all()
            for item in items:
                t = item.inner_text().strip()
                if any(s in t for s in ["Best Match", "Newest First", "Lowest Price", "Highest Price"]):
                    return t.split("\n")[0].strip()
            return ""
        except Exception as e:
            self.logger.error(f"获取排序文案失败: {e}")
            return ""

    def verify_default_sort_is_best_match(self) -> bool:
        """验证当前排序为默认 Best Match"""
        text = self.get_current_sort_text()
        return "Best Match" in text

    # ---------- Price 价格筛选 ----------

    def click_price_filter(self):
        """点击 Price 筛选项展开面板"""
        try:
            self._get_filter_item("Price").click()
            self._wait_overlay_visible()
        except Exception as e:
            self.logger.error(f"点击 Price 筛选项失败: {e}")
            raise

    def input_price_min(self, value: str):
        """输入最低价格"""
        try:
            self.page.locator(self.PRICE_MIN_INPUT).fill(value)
        except Exception as e:
            self.logger.error(f"输入最低价格失败: {e}")
            raise

    def input_price_max(self, value: str):
        """输入最高价格"""
        try:
            self.page.locator(self.PRICE_MAX_INPUT).fill(value)
        except Exception as e:
            self.logger.error(f"输入最高价格失败: {e}")
            raise

    def click_price_done(self):
        """点击 Price 面板 Done 按钮"""
        try:
            self.page.locator(self.OVERLAY_DONE_BUTTON).click()
            self._wait_overlay_hidden()
        except Exception as e:
            self.logger.error(f"点击 Price Done 失败: {e}")
            raise

    def click_price_clear(self):
        """点击 Price 面板 Clear 按钮（Clear 后自动点击 Done 使清除生效）"""
        try:
            self.page.locator(self.OVERLAY_CLEAR_BUTTON).click()
            self.page.wait_for_timeout(500)
            self.page.locator(self.OVERLAY_DONE_BUTTON).click()
            self._wait_overlay_hidden()
        except Exception as e:
            self.logger.error(f"点击 Price Clear 失败: {e}")
            raise

    def get_price_error_message(self) -> str:
        """获取 Price 面板错误提示文本"""
        try:
            el = self.page.locator("[class*='FilterItemPC_filterItemOverlay'] .error-msg").first
            return el.inner_text().strip()
        except Exception:
            return ""

    # ---------- Beds 卧室筛选 ----------

    def click_beds_filter(self):
        """点击 Beds 筛选项展开面板"""
        try:
            self._get_filter_item("Beds").click()
            self._wait_overlay_visible()
        except Exception as e:
            self.logger.error(f"点击 Beds 筛选项失败: {e}")
            raise

    def select_beds_value(self, value_str: str):
        """
        在 Beds 面板中选择指定值（scoped 到 overlay，避免误点分页）
        value_str: '1' / '2' / ... / '8+' / 'Studio'
        """
        try:
            overlay = self.page.locator(self.FILTER_ITEM_OVERLAY).first
            overlay.locator(f"[class*='Selector_label']:text-is('{value_str}')").click()
        except Exception as e:
            self.logger.error(f"选择 Beds '{value_str}' 失败: {e}")
            raise

    def click_beds_done(self):
        """点击 Beds 面板 Done 按钮"""
        try:
            self.page.locator(self.OVERLAY_DONE_BUTTON).click()
            self._wait_overlay_hidden()
        except Exception as e:
            self.logger.error(f"点击 Beds Done 失败: {e}")
            raise

    def click_beds_clear(self):
        """点击 Beds 面板 Clear 按钮（Clear 后自动点击 Done 使清除生效）"""
        try:
            self.page.locator(self.OVERLAY_CLEAR_BUTTON).click()
            self.page.wait_for_timeout(500)
            self.page.locator(self.OVERLAY_DONE_BUTTON).click()
            self._wait_overlay_hidden()
        except Exception as e:
            self.logger.error(f"点击 Beds Clear 失败: {e}")
            raise

    # ---------- Bathrooms 浴室筛选 ----------

    def click_bathrooms_filter(self):
        """点击 Bathrooms 筛选项展开面板"""
        try:
            self._get_filter_item("Bathrooms").click()
            self._wait_overlay_visible()
        except Exception as e:
            self.logger.error(f"点击 Bathrooms 筛选项失败: {e}")
            raise

    def select_bathrooms_value(self, value_str: str):
        """
        在 Bathrooms 面板中选择指定值（scoped 到 overlay）
        value_str: '1' / '1.5' / '2' / ... / '5+' / 'Shared'
        """
        try:
            overlay = self.page.locator(self.FILTER_ITEM_OVERLAY).first
            overlay.locator(f"[class*='Selector_label']:text-is('{value_str}')").click()
        except Exception as e:
            self.logger.error(f"选择 Bathrooms '{value_str}' 失败: {e}")
            raise

    def click_bathrooms_done(self):
        """点击 Bathrooms 面板 Done 按钮"""
        try:
            self.page.locator(self.OVERLAY_DONE_BUTTON).click()
            self._wait_overlay_hidden()
        except Exception as e:
            self.logger.error(f"点击 Bathrooms Done 失败: {e}")
            raise

    def click_bathrooms_clear(self):
        """点击 Bathrooms 面板 Clear 按钮（Clear 后自动点击 Done 使清除生效）"""
        try:
            self.page.locator(self.OVERLAY_CLEAR_BUTTON).click()
            self.page.wait_for_timeout(500)
            self.page.locator(self.OVERLAY_DONE_BUTTON).click()
            self._wait_overlay_hidden()
        except Exception as e:
            self.logger.error(f"点击 Bathrooms Clear 失败: {e}")
            raise

    # ---------- Property Type 房产类型筛选（Modal）----------

    def click_property_type_filter(self):
        """点击 Property Type 筛选项，打开 Category 弹窗"""
        try:
            self._get_filter_item("Property Type").click()
            self.page.locator(self.MODAL).first.wait_for(state="visible", timeout=5000)
        except Exception as e:
            self.logger.error(f"点击 Property Type 失败: {e}")
            raise

    def select_property_type_option(self, type_name: str):
        """
        在 Category 弹窗中选择类型
        type_name: 'Student Apartment' / 'Apartment' / 'House' / 'Serviced Apartment' / 'Hotel'
        """
        try:
            modal = self.page.locator(self.MODAL).first
            modal.locator(f"[class*='FilterModalPC_categoryList'] a:has(b:text-is('{type_name}'))").click()
        except Exception as e:
            self.logger.error(f"选择 Property Type '{type_name}' 失败: {e}")
            raise

    def click_property_type_done(self):
        """点击 Property Type 弹窗 Done 按钮"""
        try:
            self.page.locator(self.MODAL_DONE_BUTTON).click()
            self.page.locator(self.MODAL).first.wait_for(state="hidden", timeout=5000)
        except Exception as e:
            self.logger.error(f"点击 Property Type Done 失败: {e}")
            raise

    def click_property_type_clear(self):
        """点击 Property Type 弹窗 Clear 按钮"""
        try:
            self.page.locator(self.MODAL_CLEAR_BUTTON).click()
        except Exception as e:
            self.logger.error(f"点击 Property Type Clear 失败: {e}")
            raise

    def click_property_type_close(self):
        """点击 Property Type 弹窗关闭按钮（×）"""
        try:
            self.page.locator(self.MODAL_CLOSE_BTN).click()
            self.page.locator(self.MODAL).first.wait_for(state="hidden", timeout=5000)
        except Exception as e:
            self.logger.error(f"点击 Property Type 关闭按钮失败: {e}")
            raise

    # ---------- Filter 综合筛选面板（Modal）----------

    def click_filter_comprehensive(self):
        """点击 Filter 综合筛选按钮，打开综合筛选弹窗"""
        try:
            self._get_filter_item("Filter").click()
            self.page.locator(self.MODAL).first.wait_for(state="visible", timeout=5000)
        except Exception as e:
            self.logger.error(f"点击 Filter 综合筛选失败: {e}")
            raise

    def filter_modal_select_type(self, type_name: str):
        """在 Filter 综合面板中选择房产类型"""
        try:
            modal = self.page.locator(self.MODAL).first
            modal.locator(f"[class*='FilterModalPC_categoryList'] a:has(b:text-is('{type_name}'))").click()
        except Exception as e:
            self.logger.error(f"Filter 面板选择类型 '{type_name}' 失败: {e}")
            raise

    def filter_modal_input_price_min(self, value: str):
        """在 Filter 综合面板中输入最低价格"""
        try:
            self.page.locator(self.FILTER_MODAL_PRICE_MIN).fill(value)
        except Exception as e:
            self.logger.error(f"Filter 面板输入 Min 价格失败: {e}")
            raise

    def filter_modal_input_price_max(self, value: str):
        """在 Filter 综合面板中输入最高价格"""
        try:
            self.page.locator(self.FILTER_MODAL_PRICE_MAX).fill(value)
        except Exception as e:
            self.logger.error(f"Filter 面板输入 Max 价格失败: {e}")
            raise

    def filter_modal_select_beds(self, value_str: str):
        """在 Filter 综合面板中选择卧室数量"""
        try:
            modal = self.page.locator(self.MODAL).first
            beds_section = modal.locator(
                "[class*='FilterModalPC_filterItem']:has([class*='FilterModalPC_filterItemTitle']:text-is('Beds'))"
            ).first
            beds_section.locator(f"[class*='Selector_label']:text-is('{value_str}')").click()
        except Exception as e:
            self.logger.error(f"Filter 面板选择 Beds '{value_str}' 失败: {e}")
            raise

    def filter_modal_select_bathrooms(self, value_str: str):
        """在 Filter 综合面板中选择浴室数量"""
        try:
            modal = self.page.locator(self.MODAL).first
            bath_section = modal.locator(
                "[class*='FilterModalPC_filterItem']:has([class*='FilterModalPC_filterItemTitle']:text-is('Bathrooms'))"
            ).first
            bath_section.locator(f"[class*='Selector_label']:text-is('{value_str}')").click()
        except Exception as e:
            self.logger.error(f"Filter 面板选择 Bathrooms '{value_str}' 失败: {e}")
            raise

    def click_filter_modal_done(self):
        """点击 Filter 综合面板 Done 按钮"""
        try:
            self.page.locator(self.MODAL_DONE_BUTTON).click()
            self.page.locator(self.MODAL).first.wait_for(state="hidden", timeout=5000)
        except Exception as e:
            self.logger.error(f"点击 Filter Done 失败: {e}")
            raise

    def click_filter_modal_clear(self):
        """点击 Filter 综合面板 Clear 按钮（Clear 后自动点击 Done 使清除生效）"""
        try:
            self.page.locator(self.MODAL_CLEAR_BUTTON).click()
            self.page.wait_for_timeout(500)
            self.page.locator(self.MODAL_DONE_BUTTON).click()
            self.page.locator(self.MODAL).first.wait_for(state="hidden", timeout=5000)
        except Exception as e:
            self.logger.error(f"点击 Filter Clear 失败: {e}")
            raise

    def click_filter_modal_close(self):
        """点击 Filter 综合面板关闭按钮"""
        try:
            self.page.locator(self.MODAL_CLOSE_BTN).click()
            self.page.locator(self.MODAL).first.wait_for(state="hidden", timeout=5000)
        except Exception as e:
            self.logger.error(f"点击 Filter 关闭按钮失败: {e}")
            raise

    def get_filter_badge_text(self) -> str:
        """获取 Filter 按钮上的完整文案（如 'Filter·1'）"""
        try:
            return self.page.locator(self.FILTER_BADGE_TEXT).first.inner_text().strip()
        except Exception as e:
            self.logger.error(f"获取 Filter 徽章文案失败: {e}")
            return ""

    def is_filter_modal_visible(self) -> bool:
        """判断 Filter/PropertyType 弹窗是否可见"""
        try:
            return self.page.locator(self.MODAL).first.is_visible(timeout=2000)
        except Exception:
            return False

    def is_filter_modal_hidden(self) -> bool:
        """判断 Filter/PropertyType 弹窗是否已关闭"""
        try:
            return not self.page.locator(self.MODAL).first.is_visible(timeout=2000)
        except Exception:
            return True

    # ========== 搜索框操作（Map 模式 placeholder="Map Area"）==========

    # 搜索框 & 按钮
    SEARCH_INPUT_MAP = "[role='textbox'][placeholder='Map Area'], input[placeholder='Map Area']"
    SEARCH_BUTTON = "button:has-text('Search')"
    SEARCH_CLEAR_BUTTON = "input[placeholder='Map Area'] ~ button, [class*='TopBar'] button[aria-label='clear']"

    # 搜索建议/历史下拉
    SUGGEST_DROPDOWN = "[class*='SearchSuggestContent']"
    SUGGEST_ITEM = "[class*='SuggestItem']"

    # 结果计数（地图气泡上方 "N results"）
    RESULT_COUNT_LABEL = "[class*='PropertyList'] [class*='resultCount'], [class*='result-count']"

    # 左侧卡片列表独立滚动容器（实测 class）
    LEFT_CARD_PANEL = ".PropertyList_listContent__3PHpO"

    # 左侧卡片列表分页控件（实测：list 容器在 LEFT_CARD_PANEL 内底部）
    LEFT_PAGINATION_LIST = "[class*='Pagination'], [class*='pagination']"
    LEFT_PAGINATION_PREV = "button[aria-label='Previous'], button:has-text('Prev')"
    LEFT_PAGINATION_NEXT = "button[aria-label='Next'], button:has-text('Next')"

    # ---------- 搜索框 ----------

    def fill_search_box(self, keyword: str):
        """
        填充 Map 模式搜索框（placeholder="Map Area"）
        MCP录制：page.getByRole('textbox', { name: 'Map Area' }).fill('Bruce ACT')
        """
        try:
            self.page.get_by_role("textbox", name="Map Area").fill(keyword)
        except Exception as e:
            self.logger.error(f"填充搜索框失败: {e}")
            raise

    def click_search_button(self):
        """
        点击 Search 按钮触发普通搜索
        MCP录制：page.getByRole('button', { name: 'Search' }).click()
        """
        try:
            self.page.get_by_role("button", name="Search").click()
        except Exception as e:
            self.logger.error(f"点击 Search 按钮失败: {e}")
            raise

    def get_search_box_value(self) -> str:
        """获取搜索框当前内容"""
        try:
            return self.page.get_by_role("textbox", name="Map Area").input_value()
        except Exception:
            return ""

    def click_search_box_to_show_suggest(self):
        """
        点击搜索框（不输入内容），触发历史/建议下拉
        MCP录制：analytics 触发 search_middle_page_history_show
        """
        try:
            self.page.get_by_role("textbox", name="Map Area").click()
        except Exception as e:
            self.logger.error(f"点击搜索框失败: {e}")
            raise

    def wait_for_suggest_dropdown(self, timeout: int = 5000):
        """等待 SUG/历史 下拉出现"""
        try:
            self.page.locator(self.SUGGEST_DROPDOWN).first.wait_for(
                state="visible", timeout=timeout
            )
        except Exception as e:
            self.logger.warning(f"等待 SUG 下拉超时: {e}")

    def is_suggest_dropdown_visible(self) -> bool:
        """判断 SUG/历史 下拉是否可见"""
        try:
            return self.page.locator(self.SUGGEST_DROPDOWN).first.is_visible(timeout=2000)
        except Exception:
            return False

    def get_suggest_items_count(self) -> int:
        """获取 SUG/历史 下拉条目数量"""
        try:
            return self.page.locator(self.SUGGEST_ITEM).count()
        except Exception:
            return 0

    def click_suggest_item_by_text(self, text: str):
        """
        点击 SUG/历史 下拉中指定文字的条目
        MCP录制：page.getByText('Bruce ACT', { exact: true }).click()
        """
        try:
            self.page.locator(self.SUGGEST_DROPDOWN).get_by_text(text, exact=True).click()
        except Exception:
            self.page.get_by_text(text, exact=True).first.click()

    def click_first_suggest_item(self):
        """点击 SUG/历史 下拉中第一个条目"""
        try:
            self.page.locator(self.SUGGEST_ITEM).first.click()
        except Exception as e:
            self.logger.error(f"点击第一条建议失败: {e}")
            raise

    def get_suggest_item_texts(self) -> list:
        """获取 SUG/历史 下拉所有条目文字"""
        try:
            items = self.page.locator(self.SUGGEST_ITEM).all()
            return [item.inner_text().strip() for item in items]
        except Exception:
            return []

    def get_search_result_count_text(self) -> str:
        """
        获取地图区域结果计数文字（如 "13 results"）
        MCP录制：generic[ref=e86] 文本
        """
        try:
            # 优先尝试已知 class 片段
            el = self.page.locator("[class*='resultCount']").first
            if el.is_visible(timeout=2000):
                return el.inner_text().strip()
        except Exception:
            pass
        try:
            # Fallback：通过文本模式匹配 "N results"
            import re
            el = self.page.get_by_text(re.compile(r"\d+\s+results?", re.IGNORECASE)).first
            return el.inner_text().strip()
        except Exception:
            return ""

    # ---------- 左侧卡片面板分页 ----------

    def scroll_left_card_panel_to_bottom(self):
        """
        将左侧卡片独立滚动容器滚动到底部，使分页控件可见
        MCP录制：evaluate('.PropertyList_listContent__3PHpO', scrollTop = scrollHeight)
        """
        try:
            self.page.evaluate(
                "() => { "
                "  const el = document.querySelector('.PropertyList_listContent__3PHpO'); "
                "  if (el) el.scrollTop = el.scrollHeight; "
                "}"
            )
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"滚动左侧卡片面板失败: {e}")
            raise

    def is_left_pagination_visible(self) -> bool:
        """
        判断左侧卡片面板底部分页控件是否可见
        MCP录制：list[ref=e944] 含 Prev/Next/页码按钮
        """
        try:
            # 通过 Next 按钮判断（总是存在于分页中）
            return self.page.get_by_role("button", name="Next").is_visible(timeout=2000)
        except Exception:
            return False

    def click_left_pagination_page(self, page_num: int):
        """
        点击左侧分页指定页码
        MCP录制：page.getByRole('button', { name: '2' }).click()
        """
        try:
            self.page.get_by_role("button", name=str(page_num)).click()
        except Exception as e:
            self.logger.error(f"点击左侧分页第 {page_num} 页失败: {e}")
            raise

    def click_left_pagination_next(self):
        """点击左侧分页 Next 按钮"""
        try:
            self.page.get_by_role("button", name="Next").click()
        except Exception as e:
            self.logger.error(f"点击左侧分页 Next 失败: {e}")
            raise

    def click_left_pagination_prev(self):
        """点击左侧分页 Prev 按钮"""
        try:
            self.page.get_by_role("button", name="Previous").click()
        except Exception:
            self.page.get_by_role("button", name="Prev").first.click()

    def is_left_pagination_prev_enabled(self) -> bool:
        """判断左侧分页 Prev 按钮是否可点击（非第1页时 enabled）"""
        try:
            btn = self.page.get_by_role("button", name="Previous")
            return not btn.is_disabled(timeout=2000)
        except Exception:
            try:
                btn = self.page.get_by_role("button", name="Prev")
                return not btn.is_disabled(timeout=2000)
            except Exception:
                return False

    def get_left_pagination_current_page(self) -> int:
        """
        获取左侧分页当前页码（通过 (current) 标记）
        MCP录制：listitem (current) 标记所在 button 的文本
        """
        try:
            # 通过 aria-current 或 (current) 文本找当前页
            current = self.page.locator(
                "[class*='Pagination'] [aria-current='true'], "
                "[class*='Pagination'] [class*='current'], "
                "[class*='Pagination'] li > :not(button)"
            ).first
            text = current.inner_text().strip()
            return int(text) if text.isdigit() else 1
        except Exception:
            return 1

    def get_first_visible_card_title(self) -> str:
        """获取左侧面板第一张卡片的标题文字（用于翻页前后对比）"""
        try:
            # 左侧卡片列表中可见的第一个 link 的文字
            panel = self.page.locator(self.LEFT_CARD_PANEL)
            links = panel.get_by_role("link").all()
            if links:
                return links[0].inner_text().strip()[:80]
            return ""
        except Exception:
            return ""

    def get_filter_tag_texts(self) -> list:
        """
        获取列表视图页面上方所有激活的筛选标签文字（如 "Price: 200-600 ×"）
        MCP录制：切换到 List 后，页面顶部出现 FilterTag 标签
        """
        try:
            tags = self.page.locator(
                "[class*='FilterTag'], [class*='filterTag'], [class*='ActiveFilter']"
            ).all()
            return [t.inner_text().strip() for t in tags if t.is_visible(timeout=1000)]
        except Exception:
            return []

    # ====================================================================
    # 地图 Pin 点展示 & 列表联动 & 二级类目切换
    # 录制来源：https://au.58v5.cn/en/city-canberra/cate-student-apartment/
    # 录制时间：2026-03-12
    # ====================================================================

    # ========== Pin 点选择器（MCP 实测 CSS class）==========
    PIN_WRAPPER = "[class*='PropertyMarker_markerWrapper']"
    PIN_RENT = "[class*='PropertyMarker_rent']"
    PIN_SALE = "[class*='PropertyMarker_sale']"
    PIN_SELECTED = "[class*='PropertyMarker_selected']"
    PIN_PRICE_TEXT = "[class*='PropertyMarker_priceText']"

    # ========== 弹出卡片（点击 Pin 后出现）==========
    # 实测 DOM：class="property-card-pc pc-hover"（两个 class，非嵌套）
    MAP_POPUP_CARD = ".property-card-pc.pc-hover"

    # ========== 左侧卡片列表辅助选择器 ==========
    LEFT_CARD_ITEM = "[class*='PropertyList_listItem'], [class*='property-card-pc']"

    # ========== 结果数量气泡 ==========
    RESULT_COUNT_BUBBLE = "[class*='result']"

    # ========== 二级类目切换器标签 ==========
    SUBCATEGORY_LABEL_RENT = "Rent"
    SUBCATEGORY_LABEL_SALE = "Sale"

    # ========== 二级类目下拉选项（实测 Ref 与选择器）==========
    OPTION_FOR_RENT = "Property For Rent"
    OPTION_FOR_SALE = "Property For Sale"
    OPTION_STUDENT = "Student Accommodation"
    OPTION_COM_SALE = "Commercial Property for sale"
    OPTION_COM_RENT = "Commercial Property for rent"

    # ----------------------------------------------------------------
    # Pin 点操作
    # ----------------------------------------------------------------

    def wait_for_pins(self, timeout_ms: int = 10000, min_count: int = 1) -> bool:
        """
        等待地图 Pin 点渲染完成（轮询直到 Pin 数量 >= min_count）。
        防止在页面加载完成前就查询 Pin 导致空结果。
        """
        import time
        start = time.time()
        while (time.time() - start) * 1000 < timeout_ms:
            count = self.get_pin_count()
            if count >= min_count:
                self.logger.info(f"✓ Pin 点已加载，数量: {count}")
                return True
            self.page.wait_for_timeout(500)
        self.logger.warning(f"⚠️ 等待 Pin 点超时（{timeout_ms}ms），当前数量: {self.get_pin_count()}")
        return False

    def get_all_pin_elements_info(self) -> list:
        """
        JS 评估：获取所有 Pin 点的 class、文字、坐标。
        返回 list[dict]: { className, text, x, y }
        """
        return self.page.evaluate("""() => {
            const els = Array.from(
                document.querySelectorAll('[class*="PropertyMarker_markerWrapper"]')
            );
            return els.map(el => {
                const r = el.getBoundingClientRect();
                return {
                    className: el.className || '',
                    text: (el.innerText || '').trim(),
                    x: r.left + r.width / 2,
                    y: r.top + r.height / 2,
                    visible: r.width > 0 && r.height > 0
                };
            }).filter(p => p.visible);
        }""")

    def get_pin_count(self) -> int:
        """返回当前可见 Pin 点数量"""
        try:
            pins = self.get_all_pin_elements_info()
            return len(pins) if pins else 0
        except Exception as e:
            self.logger.warning(f"获取 Pin 数量失败: {e}")
            return 0

    def get_first_pin_coords(self) -> "dict | None":
        """
        获取第一个"单体"Pin 点的屏幕中心坐标（优先选非聚合 Pin）。
        MCP 录制代码：
            const el = document.querySelector('[class*="PropertyMarker_markerWrapper"]');
            const r = el?.getBoundingClientRect();
            return r ? { x: r.left + r.width / 2, y: r.top + r.height / 2 } : null;
        改进：优先找不含 K+ 的单体 Pin，避免聚合 Pin 无弹窗。
        """
        return self.page.evaluate(r"""() => {
            const all = Array.from(
                document.querySelectorAll('[class*="PropertyMarker_markerWrapper"]')
            );
            const singles = all.filter(el => {
                const text = (el.innerText || '').trim();
                return text.length > 0 && !/\d+K\+/.test(text);
            });
            const target = singles.length > 0 ? singles[0] : all[0];
            if (!target) return null;
            const r = target.getBoundingClientRect();
            return r && r.width > 0
                ? { x: r.left + r.width / 2, y: r.top + r.height / 2, text: target.innerText.trim() }
                : null;
        }""")

    def click_first_pin(self) -> "dict | None":
        """
        点击第一个 Pin 点，返回该 Pin 的坐标（None 表示未找到）。
        MCP 录制代码：await page.mouse.click(pin.x, pin.y)
        """
        coords = self.get_first_pin_coords()
        if coords:
            self.page.mouse.click(coords["x"], coords["y"])
            self.page.wait_for_timeout(2000)
        return coords

    def click_pin_at_index(self, index: int = 0) -> "dict | None":
        """
        点击第 index 个 Pin 点，返回坐标。
        MCP 录制代码（TC006d）：
            const pins = Array.from(...).map(el => { ... });
            await page.mouse.click(pins[1].x, pins[1].y);
        """
        pins = self.get_all_pin_elements_info()
        if pins and index < len(pins):
            target = pins[index]
            self.page.mouse.click(target["x"], target["y"])
            self.page.wait_for_timeout(1000)
            return target
        return None

    def get_selected_pin_class(self) -> "str | None":
        """
        返回当前处于 selected 状态的 Pin 的 className，无则返回 None。
        MCP 录制代码（TC006a）：
            document.querySelector('[class*="PropertyMarker_selected"]')?.className
        """
        return self.page.evaluate("""() =>
            document.querySelector('[class*="PropertyMarker_selected"]')?.className || null
        """)

    def get_selected_pin_count(self) -> int:
        """返回当前处于选中态（PropertyMarker_selected）的 Pin 数量"""
        return self.page.evaluate("""() =>
            document.querySelectorAll('[class*="PropertyMarker_selected"]').length
        """)

    def has_rent_class_pins(self) -> bool:
        """验证地图上是否存在 PropertyMarker_rent class 的 Pin（橙色）"""
        count = self.page.evaluate("""() =>
            document.querySelectorAll('[class*="PropertyMarker_rent"]').length
        """)
        return count > 0

    def has_sale_class_pins(self) -> bool:
        """验证地图上是否存在 PropertyMarker_sale class 的 Pin（蓝色）"""
        count = self.page.evaluate("""() =>
            document.querySelectorAll('[class*="PropertyMarker_sale"]').length
        """)
        return count > 0

    def get_cluster_pin_coords(self) -> "dict | None":
        """
        找到含 "K+" 文字的聚合 Pin，返回其坐标。
        MCP 录制代码（TC006e）：
            const cluster = all.find(el => /\\d+K\\+/.test(el.innerText?.trim()));
        """
        return self.page.evaluate(r"""() => {
            const all = Array.from(
                document.querySelectorAll('[class*="PropertyMarker_markerWrapper"]')
            );
            const cluster = all.find(el => /\d+K\+/.test((el.innerText || '').trim()));
            if (!cluster) return null;
            const r = cluster.getBoundingClientRect();
            return r.width > 0
                ? { x: r.left + r.width / 2, y: r.top + r.height / 2, text: cluster.innerText.trim() }
                : null;
        }""")

    # ----------------------------------------------------------------
    # 弹出 mini 卡片操作
    # ----------------------------------------------------------------

    def is_popup_card_visible(self, timeout: int = 8000) -> bool:
        """
        验证 click Pin 后弹出的 mini 卡片是否可见。
        先用 JS evaluate 扫描 DOM 中所有含 'card'/'popup'/'hover' 的可见元素，
        同时也用 Playwright locator 检查已知选择器。
        """
        try:
            result = self.page.evaluate("""() => {
                const candidates = Array.from(document.querySelectorAll('*')).filter(el => {
                    const cls = (el.className || '').toString().toLowerCase();
                    const isCard = cls.includes('card') || cls.includes('popup') || cls.includes('hover');
                    if (!isCard) return false;
                    const r = el.getBoundingClientRect();
                    return r.width > 10 && r.height > 10;
                });
                return candidates.map(el => ({
                    tag: el.tagName,
                    className: el.className ? el.className.toString().slice(0, 100) : '',
                    width: Math.round(el.getBoundingClientRect().width),
                    height: Math.round(el.getBoundingClientRect().height)
                }));
            }""")
            if result:
                card_like = [r for r in result if any(
                    k in r.get("className", "").lower()
                    for k in ["card-pc", "popup", "pc-hover", "map-card", "mini-card"]
                )]
                if card_like:
                    self.logger.info(f"✓ JS 扫描发现 popup 相关元素: {card_like[:2]}")
                    return True
        except Exception as e:
            self.logger.debug(f"JS DOM 扫描失败: {e}")

        selectors = [
            self.MAP_POPUP_CARD,
            "[class*='property-card-pc'][class*='hover']",
            "[class*='PropertyCard'][class*='hover']",
            "[class*='pc-hover']",
            "[class*='mapPopup']",
        ]
        for selector in selectors:
            try:
                card = self.page.locator(selector).first
                card.wait_for(state="visible", timeout=timeout // len(selectors))
                self.logger.info(f"✓ popup card 选择器匹配: '{selector}'")
                return True
            except Exception:
                continue
        return False

    def debug_popup_dom(self) -> list:
        """调试：返回点击 Pin 后所有含 card/hover/popup 关键词的可见元素信息"""
        try:
            return self.page.evaluate("""() => {
                return Array.from(document.querySelectorAll('*'))
                    .filter(el => {
                        const cls = (el.className || '').toString().toLowerCase();
                        return (cls.includes('card') || cls.includes('popup') || cls.includes('hover'))
                            && el.getBoundingClientRect().width > 10;
                    })
                    .slice(0, 20)
                    .map(el => ({
                        tag: el.tagName,
                        cls: el.className ? el.className.toString().slice(0, 120) : '',
                        text: (el.innerText || '').trim().slice(0, 50),
                        w: Math.round(el.getBoundingClientRect().width),
                        h: Math.round(el.getBoundingClientRect().height)
                    }));
            }""")
        except Exception:
            return []

    def _get_popup_card_locator(self):
        """获取当前弹出 mini 卡片的 locator（尝试多种选择器）"""
        selectors = [
            self.MAP_POPUP_CARD,
            "[class*='property-card-pc'][class*='hover']",
            "[class*='pc-hover']",
        ]
        for selector in selectors:
            loc = self.page.locator(selector).first
            try:
                if loc.is_visible(timeout=500):
                    return loc
            except Exception:
                continue
        return self.page.locator(self.MAP_POPUP_CARD).first

    def get_popup_card_text(self) -> str:
        """获取弹出 mini 卡片的全文内容"""
        try:
            return self._get_popup_card_locator().inner_text()
        except Exception:
            return ""

    def get_popup_card_img_count(self) -> int:
        """获取弹出 mini 卡片内 img 标签数量"""
        try:
            return self._get_popup_card_locator().locator("img").count()
        except Exception:
            return 0

    def is_popup_card_hidden(self, timeout: int = 3000) -> bool:
        """验证弹出 mini 卡片是否已关闭（hidden）"""
        try:
            card = self.page.locator(self.MAP_POPUP_CARD).first
            card.wait_for(state="hidden", timeout=timeout)
            return True
        except Exception:
            return self.page.locator(self.MAP_POPUP_CARD).count() == 0

    # ----------------------------------------------------------------
    # 结果数量读取
    # ----------------------------------------------------------------

    def get_result_count_text(self) -> str:
        """读取页面上的结果数量文字（如 '281 results'）"""
        try:
            els = self.page.locator(self.RESULT_COUNT_BUBBLE).all()
            for el in els:
                text = el.inner_text().strip()
                if "result" in text.lower():
                    return text
            return ""
        except Exception:
            return ""

    # ----------------------------------------------------------------
    # 二级类目切换操作
    # ----------------------------------------------------------------

    def click_subcategory_switcher(self, current_label: str = "Rent"):
        """
        点击搜索框左侧类目切换器展开下拉。
        MCP 录制代码（TC015）：await page.getByText('Rent', { exact: true }).click()
        """
        self.page.get_by_text(current_label, exact=True).click()
        self.page.wait_for_timeout(500)

    def click_subcategory_option(self, option_text: str):
        """
        点击二级类目下拉选项，并等待页面导航和 Pin 点重新加载。
        MCP 录制代码（TC016）：await page.getByText('Property For Sale', { exact: true }).click()
        """
        self.page.get_by_text(option_text, exact=True).click()
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self.page.wait_for_timeout(2000)
        self.wait_for_pins(timeout_ms=8000)

    def switch_subcategory(self, current_label: str, option_text: str):
        """完整二级类目切换流程：点击切换器 → 点击选项。"""
        self.click_subcategory_switcher(current_label)
        self.click_subcategory_option(option_text)

    def is_subcategory_dropdown_visible(self) -> bool:
        """检查二级类目下拉是否已展开（含 'Property For Rent' 选项可见）"""
        try:
            return self.page.get_by_text(self.OPTION_FOR_RENT, exact=True).is_visible(timeout=3000)
        except Exception:
            return False

    def get_visible_subcategory_options(self) -> list[str]:
        """
        返回当前展开下拉中所有可见的类目选项文字列表。
        使用 SecondCateDropdown 容器范围限制，避免匹配到 H1 等其他文字。
        """
        options = [
            self.OPTION_FOR_RENT, self.OPTION_FOR_SALE, self.OPTION_STUDENT,
            self.OPTION_COM_SALE, self.OPTION_COM_RENT,
        ]
        visible = []
        dropdown_container = self.page.locator(
            "[class*='SecondCateDropdown'], [class*='CategoryDropdown'], [class*='cateDropdown']"
        ).first
        for opt_text in options:
            try:
                opt = dropdown_container.get_by_text(opt_text, exact=True)
                if opt.is_visible(timeout=1500):
                    visible.append(opt_text)
                    continue
            except Exception:
                pass
            try:
                opt = self.page.locator(
                    f"[class*='SecondCateDropdown_selectItemText']:has-text('{opt_text}')"
                ).first
                if opt.is_visible(timeout=1000):
                    visible.append(opt_text)
            except Exception:
                pass
        return visible

    # ----------------------------------------------------------------
    # 左侧卡片列表（Pin 联动）
    # ----------------------------------------------------------------

    def hover_first_list_card(self):
        """
        Hover 左侧第一张卡片链接。
        使用精确选择器定位左侧卡片列表中的卡片。
        MCP 录制代码（TC007）：
            await page.getByRole('link', { name: '1 / 4 OKer_zneza78 agent-' }).hover()
        """
        # 使用精确的卡片选择器，而非泛用的 role="link"
        cards = self.page.locator(
            "[class*='PropertyList_listItem'] a, [class*='property-card-pc'] a"
        ).all()
        
        if len(cards) == 0:
            raise ValueError("左侧卡片列表为空，无法 hover")
        
        # Hover 第一张可见的卡片
        for card in cards:
            try:
                if card.is_visible(timeout=500):
                    card.hover()
                    self.page.wait_for_timeout(500)
                    self.logger.info(f"✓ 已 hover 左侧第一张卡片")
                    return
            except Exception:
                continue
        
        raise ValueError("未找到可见的左侧卡片可供 hover")

    def hover_list_card_by_index(self, index: int = 0):
        """Hover 左侧第 index 张卡片（通过角色 link 列表定位）。"""
        try:
            cards = self.page.locator(
                "[class*='PropertyList_listItem'] a, [class*='property-card-pc'] a"
            ).all()
            visible_cards = [c for c in cards if c.is_visible(timeout=500)]
            if index < len(visible_cards):
                visible_cards[index].hover()
                self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.warning(f"hover card index={index} 失败: {e}")

    def get_h1_text(self) -> str:
        """获取页面 H1 标题文字（尝试多种选择器）"""
        selectors = [
            "h1",
            "[class*='title'] h1",
            "[class*='header'] h1",
            "[class*='breadcrumb'] ~ h1",
            "main h1",
            "article h1"
        ]
        
        for selector in selectors:
            try:
                locator = self.page.locator(selector).first
                locator.wait_for(state="visible", timeout=3000)
                text = locator.inner_text().strip()
                if text:
                    return text
            except Exception:
                continue
        
        self.logger.warning("⚠️ 未找到可见的 H1 元素")
        return ""

    def is_map_url_for_category(self, cate_keyword: str) -> bool:
        """判断当前 URL 是否包含指定类目关键词，且处于地图模式"""
        return cate_keyword in self.page.url and "view=map" in self.page.url

    # ========== 定位授权功能方法 ==========

    # 地图控制按钮组（全屏/放大/缩小/定位）
    # 按钮顺序：[0]=全屏, [1]=放大, [2]=缩小, [3]=定位
    MAP_CONTROL_BUTTON = "[class*='MapControls_controlButton']"
    MAP_LOCATION_BUTTON = "[class*='MapControls_controlButton']"  # 取 .last()

    def is_map_rendered(self) -> bool:
        """验证地图是否已渲染（Google Maps 容器存在于 DOM 且有非零 offsetWidth）。

        使用 offsetWidth 而非 getBoundingClientRect，不受 CSS transform/translate 影响。
        全屏切换、退出全屏时布局重绘期间均能正确返回渲染状态。
        Google Maps API 为异步加载，CI 网络环境下最多等待 60s。
        """
        import time
        deadline = time.time() + 60
        # 先等 DOM attached（最多 50s）
        try:
            self.page.wait_for_selector(".gm-style", state="attached", timeout=50000)
        except Exception:
            return False
        # 再轮询 offsetWidth > 0（最多等剩余时间）
        while time.time() < deadline:
            try:
                w = self.page.evaluate(
                    "() => { var el = document.querySelector('.gm-style'); "
                    "return el ? el.offsetWidth : 0; }"
                )
                if w and w > 0:
                    return True
            except Exception:
                pass
            self.page.wait_for_timeout(300)
        return False

    def is_map_view_active(self) -> bool:
        """验证当前是否处于地图视图（Map 切换按钮处于 active 状态）"""
        try:
            btn = self.page.locator("[class*='mapButton'][class*='active']")
            return btn.is_visible(timeout=3000)
        except Exception:
            return False

    def is_location_button_visible(self) -> bool:
        """验证定位按钮是否可见（地图控制区域中的最后一个按钮）"""
        try:
            # 定位按钮是控制区域中的最后一个（第4个：全屏/放大/缩小/定位）
            btn = self.page.locator(self.MAP_LOCATION_BUTTON).last
            btn.wait_for(state="attached", timeout=5000)
            box = btn.bounding_box()
            return box is not None and box["width"] > 0 and box["height"] > 0
        except Exception:
            return False

    def get_location_button_size(self) -> dict:
        """获取定位按钮的尺寸信息"""
        try:
            btn = self.page.locator(self.MAP_LOCATION_BUTTON).last
            box = btn.bounding_box()
            return box if box else {}
        except Exception as e:
            self.logger.error(f"获取定位按钮尺寸失败: {e}")
            return {}

    def click_location_button(self):
        """点击定位按钮（控制区域最后一个按钮）"""
        try:
            self.page.locator(self.MAP_LOCATION_BUTTON).last.click()
        except Exception as e:
            self.logger.error(f"点击定位按钮失败: {e}")
            raise

    def get_current_viewport_param(self) -> str:
        """获取当前 URL 中的 viewport 参数值"""
        try:
            url = self.page.url
            if "viewport=" in url:
                import urllib.parse
                parsed = urllib.parse.urlparse(url)
                params = urllib.parse.parse_qs(parsed.query)
                return params.get("viewport", [""])[0]
            return ""
        except Exception:
            return ""

    def is_url_contains_map_view(self) -> bool:
        """验证 URL 是否包含 view=map 参数"""
        return "view=map" in self.page.url

    def is_url_contains_viewport(self) -> bool:
        """验证 URL 是否包含 viewport 参数"""
        return "viewport=" in self.page.url

    # ========== 地图全屏切换功能方法 ==========
    # OK 自定义全屏按钮（MapControls 区域第1个按钮，SVG含展开箭头图标）
    MAP_FULLSCREEN_BUTTON = ".MapControls_controls__o6ToG"

    def _get_fullscreen_btn(self):
        """获取全屏切换按钮 locator（页面可能有多个 controls 容器，取第一个的第一个按钮）"""
        return self.page.locator(self.MAP_FULLSCREEN_BUTTON).first.locator("button").first

    def is_fullscreen_button_visible(self) -> bool:
        """验证全屏切换按钮是否可见（通过 bounding_box 判断，兼容有头/无头模式）"""
        try:
            btn = self._get_fullscreen_btn()
            box = btn.bounding_box()
            return box is not None and box["width"] > 0 and box["height"] > 0
        except Exception:
            return False

    def click_fullscreen_button(self):
        """点击全屏切换按钮（进入全屏或退出全屏）"""
        btn = self._get_fullscreen_btn()
        btn.wait_for(state="visible", timeout=10000)
        btn.click()

    def is_in_fullscreen_mode(self) -> bool:
        """验证当前是否处于全屏模式。
        
        判断依据：MapView_fullscreen 类存在 AND fullscreenHint 提示条可见。
        进入全屏后两者均出现；退出全屏后 hint 消失（fullscreenClass 不移除是已知行为）。
        """
        try:
            result = self.page.evaluate("""() => {
                const mapView = document.querySelector('.MapView_mapView__oebEi');
                const hint = document.querySelector('.MapControls_fullscreenHint__Il0Zi');
                const hasFullscreenClass = mapView ? mapView.classList.contains('MapView_fullscreen__ZXGuS') : false;
                const hintVisible = hint ? window.getComputedStyle(hint).display !== 'none' : false;
                return hasFullscreenClass && hintVisible;
            }""")
            return bool(result)
        except Exception:
            return False

    def is_fullscreen_exit_hint_visible(self) -> bool:
        """验证全屏模式下是否出现"Exit full screen by pressing esc"提示"""
        try:
            return self.page.get_by_text("Exit full screen by pressing", exact=False).is_visible(timeout=3000)
        except Exception:
            return False

    def get_fullscreen_button_state(self) -> str:
        """获取全屏按钮当前状态（返回 'visible' 或 'hidden'）"""
        try:
            box = self._get_fullscreen_btn().bounding_box()
            return "visible" if box and box["width"] > 0 else "hidden"
        except Exception:
            return "hidden"

    # ========== 地图加载状态功能方法 ==========
    MAP_RESULTS_BADGE = ".MapView_resultsBadge__yvMxa"
    MAP_VIEW_CONTAINER = ".MapView_mapView__oebEi"
    MAP_PANEL_CONTAINER = ".MapView_mapPanel__0qJq0"
    MAP_PIN_BOTTOM_ICON = 'img[alt="bottom icon"]'
    MAP_PIN_SALE_MARKER = 'img[alt="sale marker"]'
    MAP_CONTROLS_CONTAINER = ".MapControls_controls__o6ToG"
    MAP_CONTROL_BTN = ".MapControls_controlButton__RjUAL"
    MAP_TOGGLE_BUTTON = "[class*='mapButton']"
    LIST_TOGGLE_BUTTON = "[class*='listButton']"

    def is_map_container_loaded(self) -> bool:
        """验证地图容器（.gm-style）和地图外框（.MapView_mapView__oebEi）均已加载。"""
        try:
            self.page.wait_for_selector(".gm-style", state="attached", timeout=50000)
            map_view = self.page.locator(self.MAP_VIEW_CONTAINER)
            return map_view.count() > 0
        except Exception:
            return False

    def get_map_results_badge_text(self) -> str:
        """获取地图结果数量徽标文本（如 '9 results'）。

        地图加载中时徽标显示 'Searching...'，需等待其变为包含数字的 'N results' 文本。
        等待策略：先等徽标 DOM 出现，再轮询最多 25 秒直到文本包含数字。
        """
        import time
        import re as _re
        deadline = time.time() + 45

        # 先等 badge DOM 出现（最多 20s）
        badge = self.page.locator(self.MAP_RESULTS_BADGE)
        try:
            badge.wait_for(state="attached", timeout=20000)
        except Exception:
            return ""

        while time.time() < deadline:
            try:
                # 优先用 JS 读取，稳定性更高
                text = self.page.evaluate(
                    "() => { var el = document.querySelector('.MapView_resultsBadge__yvMxa'); "
                    "return el ? el.innerText.trim() : ''; }"
                )
                if text and "search" not in text.lower() and _re.search(r"\d+", text):
                    return text
            except Exception:
                pass
            self.page.wait_for_timeout(500)

        # 超时后仍是 Searching... 或空，返回空字符串让调用方决定 skip/fail
        return ""

    def is_map_results_badge_visible(self) -> bool:
        """验证地图结果数量徽标是否可见。"""
        try:
            badge = self.page.locator(self.MAP_RESULTS_BADGE)
            return badge.is_visible(timeout=5000)
        except Exception:
            return False

    def get_map_pin_count(self) -> int:
        """获取当前地图上 Pin 点总数（bottom icon + sale marker）。"""
        try:
            bottom = self.page.locator(self.MAP_PIN_BOTTOM_ICON).count()
            sale = self.page.locator(self.MAP_PIN_SALE_MARKER).count()
            return bottom + sale
        except Exception:
            return 0

    def wait_for_map_pins(self, timeout_ms: int = 10000) -> bool:
        """等待地图 Pin 点出现（至少 1 个 bottom icon 或 sale marker）。"""
        try:
            self.page.locator(
                f"{self.MAP_PIN_BOTTOM_ICON}, {self.MAP_PIN_SALE_MARKER}"
            ).first.wait_for(state="visible", timeout=timeout_ms)
            return True
        except Exception:
            return False

    def get_map_control_button_count(self) -> int:
        """获取地图控件按钮数量（缩放/全屏/定位等）。"""
        try:
            return self.page.locator(self.MAP_CONTROL_BTN).count()
        except Exception:
            return 0

    def is_map_controls_visible(self) -> bool:
        """验证地图控件容器（MapControls_controls__o6ToG）是否可见。"""
        try:
            container = self.page.locator(self.MAP_CONTROLS_CONTAINER).first
            return container.is_visible(timeout=5000)
        except Exception:
            return False

    def is_map_toggle_button_active(self) -> bool:
        """验证 Map 切换按钮是否处于激活（active）状态。"""
        try:
            btn = self.page.locator("button[class*='mapButton'][class*='active']")
            return btn.is_visible(timeout=3000)
        except Exception:
            return False

    def click_map_toggle_button(self):
        """点击 Map 切换按钮，从列表视图切换到地图视图。
        
        MCP录制代码：await page.getByRole('button', { name: 'Map' }).click();
        """
        btn = self.page.get_by_role("button", name="Map")
        btn.wait_for(state="visible", timeout=10000)
        btn.click()

    def is_list_toggle_button_active(self) -> bool:
        """验证 List 切换按钮是否处于激活（active）状态。"""
        try:
            btn = self.page.locator("button[class*='listButton'][class*='active']")
            return btn.is_visible(timeout=3000)
        except Exception:
            return False

    def wait_for_map_loaded_after_toggle(self, timeout_ms: int = 30000) -> bool:
        """切换到地图视图后，等待地图完整加载（gm-style 出现）。"""
        try:
            self.page.wait_for_selector(".gm-style", state="attached", timeout=timeout_ms)
            return True
        except Exception:
            return False

    # ========== 地图模式卡片数量和房源点数量功能方法 ==========
    MAP_LIST_WRAP = ".property-list-wrap"
    MAP_LIST_CARD_SELECTOR = ".property-list-wrap > a"
    MAP_PIN_WRAPPER = "[class*='PropertyMarker_markerWrapper']"
    MAP_POPUP_CARD_LINK = "a[href*='cate-property-for-sale-']"
    MAP_POPUP_PAGE_INDICATOR = "[class*='ImageSlider_'], [class*='imageSlider_']"

    def get_map_list_card_count(self) -> int:
        """获取地图模式左侧卡片列表中的卡片数量（.property-list-wrap 的直接子 a 元素）。

        MCP录制：directLinkCount: 9（与badge "9 results"一致）
        """
        try:
            wrap = self.page.locator(self.MAP_LIST_WRAP)
            wrap.wait_for(state="attached", timeout=10000)
            return wrap.locator(":scope > a").count()
        except Exception:
            return 0

    def wait_for_map_list_cards(self, timeout_ms: int = 15000) -> bool:
        """等待地图模式左侧卡片列表渲染完成（至少 1 张卡片）。"""
        try:
            self.page.locator(self.MAP_LIST_CARD_SELECTOR).first.wait_for(
                state="attached", timeout=timeout_ms
            )
            return True
        except Exception:
            return False

    def get_map_marker_wrapper_count(self) -> int:
        """获取地图上 Pin 点容器（PropertyMarker_markerWrapper）总数。

        MCP录制：pinContainerCount: 9（= bottomIcon 8 + saleMarker 1）
        """
        try:
            return self.page.evaluate(
                "document.querySelectorAll('[class*=\"PropertyMarker_markerWrapper\"]').length"
            )
        except Exception:
            return 0

    def get_map_results_badge_number(self) -> int:
        """从结果徽标文本（如 '9 results'）中提取数字并返回。"""
        import re as _re
        text = self.get_map_results_badge_text()
        m = _re.search(r"\d+", text)
        return int(m.group()) if m else 0

    def click_first_pin_by_js(self) -> bool:
        """通过 JS 点击第一个 Pin 点容器（规避 Playwright strict mode 和 pointer-events 拦截）。

        MCP录制：markers[0].click() → 触发 analytics-firebase map_property_point_click
        """
        try:
            result = self.page.evaluate("""() => {
                var markers = document.querySelectorAll('[class*="PropertyMarker_markerWrapper"]');
                if (!markers.length) return false;
                markers[0].click();
                return true;
            }""")
            return bool(result)
        except Exception:
            return False

    def is_map_popup_card_visible(self, timeout_ms: int = 8000) -> bool:
        """验证点击 Pin 点后地图区域弹出的卡片是否可见。

        弹出卡片是地图覆盖层内的 property 链接（href 可能含 cate-rent / cate-property-for-sale 等），
        区别于左侧列表中的卡片（左侧列表父容器带 hidden class）。
        MCP录制：ref=e453 link "zhuzhai zhuzhai 1 / 2 A$580,580..."
        """
        import time
        deadline = time.time() + timeout_ms / 1000

        while time.time() < deadline:
            try:
                # JS 方案：在 mapPanel 区域查找任何可见的 property 链接
                result = self.page.evaluate("""() => {
                    // 查找 mapPanel 容器
                    var mapPanel = document.querySelector('[class*="mapPanel"]');
                    if (!mapPanel) return { found: false, reason: 'no mapPanel' };

                    // 查找所有 property 相关链接（rent/sale/commercial 等分类均适用）
                    var links = mapPanel.querySelectorAll(
                        'a[href*="cate-"], a[href*="property"]'
                    );
                    // 过滤掉左侧列表内的链接（.property-list-wrap 内的）
                    var popupLinks = Array.from(links).filter(function(a) {
                        return !a.closest('.property-list-wrap');
                    });
                    if (popupLinks.length === 0) return { found: false, reason: 'no popup links' };

                    // 检查是否有可见的（非 hidden 状态的）
                    var visibleLinks = popupLinks.filter(function(a) {
                        var r = a.getBoundingClientRect();
                        return r.width > 0 && r.height > 0;
                    });
                    return {
                        found: visibleLinks.length > 0,
                        total: popupLinks.length,
                        visible: visibleLinks.length
                    };
                }""")
                if result and result.get("found"):
                    self.logger.info(f"✓ 弹出卡片可见（mapPanel 内 popup links: {result}）")
                    return True
            except Exception as e:
                self.logger.debug(f"JS 检测弹出卡片失败: {e}")

            # 备用方案：通过 fav-icon 图片判断弹出卡片
            try:
                fav_visible = self.page.evaluate("""() => {
                    var mapPanel = document.querySelector('[class*="mapPanel"]');
                    if (!mapPanel) return false;
                    // 查找 mapPanel 内不在 property-list-wrap 中的 fav-icon
                    var imgs = mapPanel.querySelectorAll('img[alt="fav-icon"]');
                    return Array.from(imgs).some(function(img) {
                        if (img.closest('.property-list-wrap')) return false;
                        var r = img.getBoundingClientRect();
                        return r.width > 0;
                    });
                }""")
                if fav_visible:
                    self.logger.info("✓ 弹出卡片可见（通过 fav-icon 检测）")
                    return True
            except Exception:
                pass

            self.page.wait_for_timeout(500)

        return False

    def get_popup_card_page_indicator(self) -> str:
        """获取弹出卡片中的翻页标识文本（如 '1 / 2'）。

        MCP录制：快照中 generic [ref=e466]: 1 / 2
        """
        try:
            result = self.page.evaluate("""() => {
                // 在地图覆盖层中查找 "N / M" 格式文本
                var allEls = document.querySelectorAll('[class*="mapPanel"] *');
                for (var i = 0; i < allEls.length; i++) {
                    var text = (allEls[i].innerText || '').trim();
                    if (/^\\d+\\s*\\/\\s*\\d+$/.test(text)) {
                        return text;
                    }
                }
                return '';
            }""")
            return result if result else ""
        except Exception:
            return ""

    # ===== 地图 Hover 房源点功能 =====

    def get_map_pin_count_and_hovered_state(self) -> dict:
        """获取地图 Pin 点总数和各 Pin 点的 hovered 状态。

        MCP录制：page.evaluate 查询 [class*="PropertyMarker_markerWrapper"]
        返回：{"markerCount": N, "hoveredCount": N, "allClasses": [...]}
        """
        try:
            return self.page.evaluate("""() => {
                var markers = document.querySelectorAll('[class*="PropertyMarker_markerWrapper"]');
                var count = markers.length;
                var hoveredCount = 0;
                markers.forEach(function(m) {
                    if (m.className.includes('hovered')) hoveredCount++;
                });
                return {
                    markerCount: count,
                    hoveredCount: hoveredCount,
                    allClasses: Array.from(markers).map(function(m) { return m.className; })
                };
            }""")
        except Exception:
            return {"markerCount": 0, "hoveredCount": 0, "allClasses": []}

    def hover_map_pin_by_index(self, index: int) -> bool:
        """通过 JS dispatchEvent 触发指定索引的 Pin 点 hover 事件。

        注意：不使用 Playwright 的 hover() 方法，因为子元素会拦截指针事件。
        MCP录制：markers[index].dispatchEvent(new MouseEvent('mouseover', {bubbles: true}))
        """
        try:
            result = self.page.evaluate(f"""() => {{
                var markers = document.querySelectorAll('[class*="PropertyMarker_markerWrapper"]');
                var m = markers[{index}];
                if (!m) return {{ success: false, reason: 'no marker at index {index}' }};
                m.dispatchEvent(new MouseEvent('mouseover', {{bubbles: true, cancelable: true}}));
                return {{ success: true, markerText: m.innerText.trim() }};
            }}""")
            return bool(result and result.get("success"))
        except Exception:
            return False

    def get_hovered_pin_indices(self) -> list:
        """获取所有当前处于 hovered 状态的 Pin 点索引列表。

        MCP录制：检查 className.includes('hovered') 即 PropertyMarker_hovered__s3K29
        """
        try:
            return self.page.evaluate("""() => {
                var markers = document.querySelectorAll('[class*="PropertyMarker_markerWrapper"]');
                var indices = [];
                markers.forEach(function(m, i) {
                    if (m.className.includes('hovered')) indices.push(i);
                });
                return indices;
            }""")
        except Exception:
            return []

    def wait_for_pin_hover_state(self, expected_index: int, timeout_ms: int = 2000) -> bool:
        """等待指定索引的 Pin 点获得 hovered class。

        轮询检查直到超时，返回是否成功。
        """
        import time
        deadline = time.time() + timeout_ms / 1000
        while time.time() < deadline:
            hovered = self.get_hovered_pin_indices()
            if expected_index in hovered:
                return True
            self.page.wait_for_timeout(100)
        return False

    # ========== 地图控件：放大 / 缩小 / 定位 / 全屏 ==========
    # 按钮顺序（MapControls 区域）：[0]=全屏, [1]=放大(+), [2]=缩小(-), [3]=定位
    _CTRL_BTN = "button.MapControls_controlButton__RjUAL"

    def click_map_zoom_in(self):
        """点击地图放大(+)按钮（控制区域第2个按钮，index=1）"""
        try:
            btns = self.page.locator(self._CTRL_BTN)
            btns.nth(1).click()
        except Exception as e:
            self.logger.error(f"点击放大按钮失败: {e}")
            raise

    def click_map_zoom_out(self):
        """点击地图缩小(-)按钮（控制区域第3个按钮，index=2）"""
        try:
            btns = self.page.locator(self._CTRL_BTN)
            btns.nth(2).click()
        except Exception as e:
            self.logger.error(f"点击缩小按钮失败: {e}")
            raise

    def click_locate_button(self):
        """点击定位（compass）按钮（控制区域最后一个按钮）"""
        try:
            self.page.locator(self._CTRL_BTN).last.click()
        except Exception as e:
            self.logger.error(f"点击定位按钮失败: {e}")
            raise

    def get_zoom_level_from_url(self) -> int:
        """从当前 URL viewport 参数中解析 zoom 级别（z:N 或 z%3AN）"""
        import re as _re
        import urllib.parse
        try:
            url = self.page.url
            # 先尝试从 viewport 参数中解析（URL decode 后）
            parsed = urllib.parse.urlparse(url)
            params = urllib.parse.parse_qs(parsed.query)
            viewport = params.get("viewport", [""])[0]
            if viewport:
                # viewport decode 后格式如：c:-35.2802,149.1310|z:11
                m = _re.search(r"\|z:(\d+)", viewport)
                if m:
                    return int(m.group(1))
            # 直接在原始 URL 中匹配 %7Cz%3A(\d+)（| 和 : 均 URL 编码）
            m = _re.search(r"(?:%7C|[|])z(?:%3A|:)(\d+)", url, _re.IGNORECASE)
            return int(m.group(1)) if m else -1
        except Exception as e:
            self.logger.error(f"解析 zoom 级别失败: {e}")
            return -1

    def is_map_region_visible(self) -> bool:
        """验证地图区域（.gm-style 容器）是否可见"""
        try:
            el = self.page.locator(".gm-style").first
            el.wait_for(state="attached", timeout=10000)
            w = self.page.evaluate(
                "() => { var el = document.querySelector('.gm-style'); "
                "return el ? el.offsetWidth : 0; }"
            )
            return bool(w and w > 0)
        except Exception:
            return False

    def is_fullscreen_hint_visible(self, timeout: int = 3000) -> bool:
        """验证全屏模式下是否显示 'Exit full screen by pressing [esc]' 提示"""
        try:
            return self.page.get_by_text(
                "Exit full screen by pressing", exact=False
            ).is_visible(timeout=timeout)
        except Exception:
            return False

    def is_locate_button_active(self) -> bool:
        """验证定位按钮是否处于激活（active）状态"""
        try:
            btn = self.page.locator(self._CTRL_BTN).last
            cls = btn.get_attribute("class") or ""
            return "active" in cls.lower() or "located" in cls.lower()
        except Exception:
            return False

    def is_property_list_visible(self, timeout: int = 5000) -> bool:
        """验证左侧房源卡片列表是否可见（退出全屏后列表恢复）"""
        selectors = [
            ".property-list-wrap",
            "[class*='PropertyList_listContent']",
            "[class*='PropertyList_listItem']",
        ]
        for sel in selectors:
            try:
                el = self.page.locator(sel).first
                el.wait_for(state="visible", timeout=timeout // len(selectors))
                return True
            except Exception:
                continue
        return False

    def press_escape(self):
        """按下 Escape 键（用于退出全屏模式）"""
        try:
            self.page.keyboard.press("Escape")
        except Exception as e:
            self.logger.error(f"按下 Escape 键失败: {e}")
            raise
