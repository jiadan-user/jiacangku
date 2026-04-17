# pages/explore_list_page.py
from urllib.parse import urlparse, parse_qs
from pages.base_page import BasePage
from utils.logger import setup_logger


def _urls_match(current_url: str, target_url: str) -> bool:
    """判断当前 URL 与目标 URL 是否指向同一页面（path + 关键 query 相同）"""
    cur = urlparse(current_url)
    tgt = urlparse(target_url)
    if cur.netloc != tgt.netloc or cur.path.rstrip('/') != tgt.path.rstrip('/'):
        return False
    cur_qs = parse_qs(cur.query)
    tgt_qs = parse_qs(tgt.query)
    # 目标 URL 的每个参数在当前 URL 中都要存在且一致
    for key, val in tgt_qs.items():
        if cur_qs.get(key) != val:
            return False
    # 当前 URL 不能有目标 URL 中没有的筛选参数（防止带着残留筛选跳过导航）
    skip_keys = {'iconSource'}
    for key in cur_qs:
        if key not in tgt_qs and key not in skip_keys:
            return False
    return True


class ExploreListPage(BasePage):
    """探索列表页（Cars分类）页面对象 - AE站"""

    # ========== 页面元素选择器 ==========

    # 页面标题
    PAGE_TITLE = ".carlist-page-title-text"

    # 面包屑
    BREADCRUMB_NAV = "nav ol"
    BREADCRUMB_HOME = "nav ol li a"  # 第一个 <a> 即 Home

    # 筛选栏 - 各项目
    FILTER_ITEM_CONTENT = ".FilterItem_filterItemContent__i4Ik9"
    FILTER_ITEM_WRAPPER = ".FilterItem_filterItem__eblCw"
    RESET_BTN = ".resetText"

    # Location tag (EchoArea)
    LOCATION_TAG = ".EchoArea_echoItem__KH5ms"
    LOCATION_TAG_CLOSE = ".EchoArea_closeIcon__xSyX_"

    # 搜索框
    SEARCH_INPUT = "input.CustomInput_searchInput__Xf3DF"
    SEARCH_BTN = "button:has-text('Search')"

    # Sort 面板
    SORT_OPTION = ".Selector_label__koRaF"
    SORT_SELECTED = ".Selector_selected__7svoy"
    SORT_CLEAR_BTN = "button.button_light__Anmwq"
    SORT_CONFIRM_BTN = "button.button_dark__FJMb_"

    # Filter 面板
    FILTER_MODAL = ".FilterModalPC_customDialog__3K8l1"
    FILTER_MODAL_WRAP = ".FilterModalPC_wrap__1tg0R"
    FILTER_CLEAR_BTN = ".FilterModalPC_btnArea__Y7Tbi button.button_light__Anmwq"
    FILTER_CONFIRM_BTN = ".FilterModalPC_btnArea__Y7Tbi button.button_dark__FJMb_"
    FILTER_MULTISELECT_CONTROL = ".MultiSelect_control__oQ3fK"
    FILTER_MULTISELECT_OPTION = ".MultiSelect_option__2wVjT"
    FILTER_BADGE_POINT = ".FilterItem_filterItemPoint__LWUvZ"
    FILTER_ITEM_ACTIVE = "FilterItem_filterItemActive__gR37G"

    # City / Location 下拉
    CITY_QUICK_TAG = ".QuickCities_tagText__k3Zz3"
    CITY_ANCHOR_ITEM = "[class*='AnchorSelector_item'][class*='itemValue']"
    CITY_SEARCH_INPUT = ".LocationWrapperNew_searchInput__Y7Tl3"

    # Price / Mileage 区间输入（类名对 Price 和 Mileage 面板均适用）
    RANGE_INPUT_MIN = ".RangeInputPair_input__qAEGz:nth-child(1)"
    RANGE_PRICE_MIN = ".RangeInputPair_input__qAEGz"   # 第一个匹配为 Min
    RANGE_PRICE_MAX = ".RangeInputPair_input__qAEGz"   # 第二个匹配为 Max
    RANGE_OVERLAY = ".FilterItemPC_filterItemOverlay__lSvFd"
    RANGE_CONFIRM_BTN = ".FilterItemPC_filterItemOverlay__lSvFd button.button_dark__FJMb_"

    # Brand 面板
    BRAND_MODAL = ".CarModalBrand_carModalBrandWrap__NXNMJ"
    BRAND_POPULAR_ICON = ".QuickCars_tagIcon__cqaQ7"  # by alt text

    # 车辆列表
    CAR_ITEM_LINK = ".default-list-caritem-link"
    CAR_TITLE = ".carcard-title"
    CAR_PRICE_SYMBOL = ".Price_symbol__6Lpfc"
    CAR_PRICE_AMOUNT = ".Price_priceAmount__X0tVJ"
    CAR_DETAIL_SPAN = ".DetailsParams_details-text__J9Tjg"
    CAR_IMAGE = ".carcard-image"

    # 分页
    PAGINATION_NEXT = "button.page-link:has-text('Next')"

    # 导航/辅助
    LOGIN_REGISTER_BTN = "text=Log in / Register"
    BROWSE_BTN = "text=Browse"

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    # ========== 导航 ==========

    def navigate_to_cars_list(self, base_url, city="abu-dhabi"):
        """导航到指定城市的 Cars 探索列表页"""
        try:
            url = f"{base_url}/en/city-{city}/cate-car/?iconSource=car"
            self.navigate_to_url(url)
        except Exception as e:
            self.logger.error(f"导航到 Cars 列表页失败: {e}")
            raise

    def navigate_to_url(self, url):
        """直接导航到指定 URL，若当前页面已匹配则跳过加载"""
        try:
            if _urls_match(self.page.url, url):
                self.logger.info(f"当前页面已匹配目标 URL，跳过导航")
                return
            self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            # 等待筛选栏渲染完成作为页面就绪信号，替代固定 5 秒等待
            try:
                self.page.locator(self.FILTER_ITEM_CONTENT).first.wait_for(
                    state="visible", timeout=15000
                )
            except Exception:
                # 某些极端筛选页面可能无筛选栏，兜底短等待
                self.page.wait_for_timeout(2000)
            # 等待 JS 水合完成，确保 React 事件处理器已绑定
            try:
                self.page.wait_for_load_state("load", timeout=10000)
            except Exception:
                pass
        except Exception as e:
            self.logger.error(f"导航失败: {e}")
            raise

    # ========== 页面信息获取 ==========

    def get_page_title_text(self):
        """获取页面大标题文本（如 'Cars in Abu Dhabi'）"""
        try:
            return self.page.locator(self.PAGE_TITLE).first.inner_text(timeout=5000)
        except Exception as e:
            self.logger.error(f"获取页面标题失败: {e}")
            raise

    def get_browser_title(self):
        """获取浏览器 Tab 标题"""
        try:
            return self.page.title()
        except Exception as e:
            self.logger.error(f"获取浏览器标题失败: {e}")
            raise

    def get_meta_description(self):
        """获取 meta description 内容"""
        try:
            return self.page.locator("meta[name='description']").get_attribute("content", timeout=3000) or ""
        except Exception as e:
            self.logger.error(f"获取 meta description 失败: {e}")
            return ""

    def get_current_url(self):
        """获取当前页面 URL"""
        return self.page.url

    # ========== 面包屑 ==========

    def click_breadcrumb_home(self):
        """点击面包屑中的 Home 链接"""
        try:
            self.page.locator("nav ol li a").first.click()
            self.page.wait_for_timeout(3000)
        except Exception as e:
            self.logger.error(f"点击 Home 面包屑失败: {e}")
            raise

    def click_breadcrumb_cars(self):
        """点击面包屑中的 Cars 链接"""
        try:
            self.page.locator("nav ol li a").last.click()
            self.page.wait_for_timeout(3000)
        except Exception as e:
            self.logger.error(f"点击 Cars 面包屑失败: {e}")
            raise

    def get_breadcrumb_texts(self):
        """获取面包屑所有文本列表"""
        try:
            items = self.page.locator("nav ol li").all()
            return [item.inner_text(timeout=1000).strip() for item in items]
        except Exception as e:
            self.logger.error(f"获取面包屑文本失败: {e}")
            raise

    # ========== Location Tag ==========

    def get_location_tags(self):
        """获取所有 Location Tag 文本列表"""
        try:
            tags = self.page.locator(self.LOCATION_TAG).all()
            return [t.inner_text(timeout=2000).strip() for t in tags]
        except Exception as e:
            self.logger.error(f"获取 Location Tag 失败: {e}")
            raise

    def get_location_tags_count(self):
        """获取 Location Tag 数量"""
        try:
            return len(self.page.locator(self.LOCATION_TAG).all())
        except Exception as e:
            self.logger.error(f"获取 Location Tag 数量失败: {e}")
            raise

    def click_location_tag_close(self):
        """点击 Location Tag 的 × 按钮移除城市筛选"""
        try:
            self.page.locator(self.LOCATION_TAG_CLOSE).first.click()
            self.page.wait_for_timeout(3000)
        except Exception as e:
            self.logger.error(f"点击 Location Tag 关闭失败: {e}")
            raise

    def is_location_tag_visible(self):
        """判断 Location Tag 是否可见"""
        try:
            return self.page.locator(self.LOCATION_TAG).first.is_visible(timeout=3000)
        except Exception:
            return False

    # ========== 搜索 ==========

    def search(self, keyword):
        """在搜索框输入关键词并点击 Search"""
        try:
            search_input = self.page.locator(self.SEARCH_INPUT)
            search_input.fill(keyword)
            self.page.wait_for_timeout(300)
            self.page.get_by_role("button", name="Search").click()
            self.page.wait_for_timeout(3000)
        except Exception as e:
            self.logger.error(f"搜索失败: {e}")
            raise

    def search_and_press_enter(self, keyword):
        """在搜索框输入关键词并按 Enter"""
        try:
            search_input = self.page.locator(self.SEARCH_INPUT)
            search_input.fill(keyword)
            self.page.wait_for_timeout(300)
            search_input.press("Enter")
            self.page.wait_for_timeout(3000)
        except Exception as e:
            self.logger.error(f"搜索(Enter)失败: {e}")
            raise

    def click_search_empty(self):
        """不输入内容直接点击 Search"""
        try:
            self.page.get_by_role("button", name="Search").click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击 Search 失败: {e}")
            raise

    def input_search_text(self, text):
        """只输入搜索文本（不提交）"""
        try:
            self.page.locator(self.SEARCH_INPUT).fill(text)
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"输入搜索文本失败: {e}")
            raise

    # ========== Sort 排序 ==========

    def click_sort(self):
        """点击 Sort 按钮展开排序面板"""
        try:
            self.page.locator(self.FILTER_ITEM_CONTENT).filter(has_text="Sort").first.click()
            self.page.wait_for_timeout(1500)
        except Exception as e:
            self.logger.error(f"点击 Sort 失败: {e}")
            raise

    def select_sort_option(self, option_text):
        """选择排序选项（如 'Price: Low to High'）"""
        try:
            self.page.locator(self.SORT_OPTION).filter(has_text=option_text).first.click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择排序选项 '{option_text}' 失败: {e}")
            raise

    def click_sort_confirm(self):
        """点击 Sort 面板的 Confirm 按钮"""
        try:
            self.page.get_by_text("Confirm", exact=True).first.click()
            self.page.wait_for_timeout(3000)
        except Exception as e:
            self.logger.error(f"点击 Sort Confirm 失败: {e}")
            raise

    def click_sort_clear(self):
        """点击 Sort 面板的 Clear 按钮"""
        try:
            self.page.get_by_text("Clear", exact=True).first.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击 Sort Clear 失败: {e}")
            raise

    def is_sort_panel_visible(self):
        """判断 Sort 面板是否展开（通过面板内 Selector 容器判断）"""
        try:
            # Sort 面板展开时，.Selector_selectorContainer__exIPs 容器可见
            return self.page.locator(".Selector_selectorContainer__exIPs").first.is_visible(timeout=3000)
        except Exception:
            return False

    def is_sort_option_selected(self, option_text):
        """判断指定排序选项是否已选中"""
        try:
            option = self.page.locator(self.SORT_OPTION).filter(has_text=option_text).first
            parent = option.locator("..")
            cls = parent.get_attribute("class", timeout=2000) or ""
            return "selected" in cls.lower()
        except Exception:
            return False

    def is_sort_active(self):
        """判断 Sort 筛选项是否处于激活状态"""
        try:
            sort_item = self.page.locator(self.FILTER_ITEM_WRAPPER).filter(has_text="Sort").first
            cls = sort_item.get_attribute("class", timeout=2000) or ""
            return "Active" in cls
        except Exception:
            return False

    def close_sort_panel_by_escape(self):
        """按 Escape 关闭 Sort 面板"""
        try:
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"按 ESC 关闭 Sort 面板失败: {e}")
            raise

    def click_outside_to_close_sort(self):
        """点击面板外区域关闭 Sort 下拉"""
        try:
            self.page.locator(self.PAGE_TITLE).click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击外部关闭 Sort 失败: {e}")
            raise

    # ========== Filter 综合筛选 ==========

    def click_filter(self):
        """点击 Filter 按钮展开筛选面板"""
        try:
            self.page.locator(self.FILTER_ITEM_CONTENT).filter(has_text="Filter").first.click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击 Filter 失败: {e}")
            raise

    def is_filter_modal_visible(self):
        """判断 Filter 弹窗是否可见"""
        try:
            return self.page.locator(self.FILTER_MODAL).first.is_visible(timeout=3000)
        except Exception:
            return False

    def click_filter_confirm(self):
        """点击 Filter 面板的 Confirm 按钮"""
        try:
            self.page.locator(self.FILTER_CONFIRM_BTN).first.click()
            self.page.wait_for_timeout(3000)
        except Exception as e:
            self.logger.error(f"点击 Filter Confirm 失败: {e}")
            raise

    def click_filter_clear(self):
        """点击 Filter 面板的 Clear 按钮"""
        try:
            self.page.locator(self.FILTER_CLEAR_BTN).first.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击 Filter Clear 失败: {e}")
            raise

    def close_filter_by_escape(self):
        """按 ESC 关闭 Filter 面板"""
        try:
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"按 ESC 关闭 Filter 失败: {e}")
            raise

    def select_first_filter_option(self):
        """选择 Filter 面板中第一个可用选项（用于激活角标）"""
        try:
            first_control = self.page.locator(self.FILTER_MULTISELECT_CONTROL).first
            first_control.click()
            self.page.wait_for_timeout(1500)
            first_option = self.page.locator(self.FILTER_MULTISELECT_OPTION).first
            first_option.click()
            self.page.wait_for_timeout(500)
            # Close dropdown by clicking the modal title (ESC would close the entire modal)
            self.page.locator(".FilterModalPC_title__0CjQO").first.click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择 Filter 首选项失败: {e}")
            raise

    def get_filter_group_index(self, group_name: str) -> int:
        """获取 Filter 弹窗中指定分组的 MultiSelect control 索引（0-based）。
        注意：Engine(cc) 是 range input 不含 MultiSelect control，其后的分组索引需减 1。
        """
        # 分组标题顺序：Body Style(0) Body Color(1) Year(2) Specs(3) Fuel Type(4)
        # Transmission(5) Engine(cc)(6, range input) Drive Type(7)
        # MultiSelect control 索引：Body Style(0) Body Color(1) Year(2) Specs(3)
        # Fuel Type(4) Transmission(5) Drive Type(6)
        ENGINE_CC_TITLE = "Engine(cc)"
        titles = self.page.locator(".FilterModalPC_filterItemTitle__C5bMh").all()
        title_names = []
        for t in titles:
            try:
                raw = t.inner_text(timeout=500).strip()
                # 页面存在分组标题文本重复渲染的问题（如 "TransmissionTransmission"）
                # 对连续重复的文本折叠为单次
                deduped = raw
                for length in range(1, len(raw) // 2 + 1):
                    prefix = raw[:length]
                    if len(raw) % length == 0 and prefix * (len(raw) // length) == raw:
                        deduped = prefix
                        break
                title_names.append(deduped)
            except Exception:
                title_names.append("")
        if group_name not in title_names:
            raise ValueError(f"Filter 分组 '{group_name}' 未找到，当前分组: {title_names}")
        pos = title_names.index(group_name)
        # Engine(cc) 之后的分组 MultiSelect 索引需减 1
        engine_pos = title_names.index(ENGINE_CC_TITLE) if ENGINE_CC_TITLE in title_names else -1
        if engine_pos >= 0 and pos > engine_pos:
            return pos - 1
        return pos

    def select_filter_option_by_group(self, group_name: str, option_text: str = None, option_index: int = 0):
        """在指定分组下拉中选择选项（默认选第一个），返回选中的选项文本"""
        try:
            idx = self.get_filter_group_index(group_name)
            # 滚动弹窗到底部确保下方分组可见
            self.page.locator(".FilterModalPC_wrap__1tg0R").evaluate("el => el.scrollTop = el.scrollHeight")
            self.page.wait_for_timeout(300)
            control = self.page.locator(self.FILTER_MULTISELECT_CONTROL).nth(idx)
            control.scroll_into_view_if_needed()
            control.click(timeout=3000)
            self.page.wait_for_timeout(1000)
            opts = self.page.locator(self.FILTER_MULTISELECT_OPTION).all()
            if option_text:
                target = next((o for o in opts if o.inner_text(timeout=500).strip() == option_text), None)
                if not target:
                    raise ValueError(f"选项 '{option_text}' 在 '{group_name}' 中未找到")
                target.click()
                selected = option_text
            else:
                selected = opts[option_index].inner_text(timeout=500).strip()
                opts[option_index].click()
            self.page.wait_for_timeout(500)
            # 关闭下拉：点标题区域
            self.page.locator(".FilterModalPC_title__0CjQO").first.click()
            self.page.wait_for_timeout(500)
            return selected
        except Exception as e:
            self.logger.error(f"Filter 分组 '{group_name}' 选择失败: {e}")
            raise

    def get_filter_group_options(self, group_name: str) -> list:
        """获取指定分组的所有选项文本列表，获取后自动关闭 Filter 弹窗（含 ESC）"""
        try:
            idx = self.get_filter_group_index(group_name)
            self.page.locator(".FilterModalPC_wrap__1tg0R").evaluate("el => el.scrollTop = el.scrollHeight")
            self.page.wait_for_timeout(300)
            control = self.page.locator(self.FILTER_MULTISELECT_CONTROL).nth(idx)
            control.scroll_into_view_if_needed()
            control.click(timeout=3000)
            self.page.wait_for_timeout(1000)
            opts = self.page.locator(self.FILTER_MULTISELECT_OPTION).all()
            texts = [o.inner_text(timeout=500).strip() for o in opts]
            # 关闭选项下拉，再关闭 Filter 弹窗（按 ESC）
            self.page.locator(".FilterModalPC_title__0CjQO").first.click()
            self.page.wait_for_timeout(500)
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(800)
            return texts
        except Exception as e:
            self.logger.error(f"获取 Filter 分组 '{group_name}' 选项失败: {e}")
            raise

    def select_filter_multi_options(self, group_name: str, option_texts: list):
        """在指定分组中选择多个选项"""
        try:
            idx = self.get_filter_group_index(group_name)
            self.page.locator(".FilterModalPC_wrap__1tg0R").evaluate("el => el.scrollTop = el.scrollHeight")
            self.page.wait_for_timeout(300)
            control = self.page.locator(self.FILTER_MULTISELECT_CONTROL).nth(idx)
            control.scroll_into_view_if_needed()
            control.click(timeout=3000)
            self.page.wait_for_timeout(1000)
            for opt_text in option_texts:
                opts = self.page.locator(self.FILTER_MULTISELECT_OPTION).all()
                target = next((o for o in opts if o.inner_text(timeout=500).strip() == opt_text), None)
                if target:
                    target.click()
                    self.page.wait_for_timeout(300)
            self.page.locator(".FilterModalPC_title__0CjQO").first.click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"Filter 分组 '{group_name}' 多选失败: {e}")
            raise

    def set_engine_cc_range(self, min_cc: int, max_cc: int):
        """在 Filter 弹窗中设置 Engine(cc) 排量区间"""
        try:
            engine_item = self.page.locator(".FilterModalPC_filterItem__pSAw_").nth(6)
            engine_item.scroll_into_view_if_needed()
            inputs = engine_item.locator(".RangeInputPair_input__qAEGz").all()
            if len(inputs) >= 2:
                inputs[0].fill(str(min_cc))
                inputs[1].fill(str(max_cc))
                self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"设置 Engine(cc) 区间失败: {e}")
            raise

    def get_filter_all_group_names(self) -> list:
        """获取 Filter 弹窗中所有分组名称列表（自动归一化重复文本）"""
        def _deduplicate(text: str) -> str:
            for length in range(1, len(text) // 2 + 1):
                prefix = text[:length]
                if len(text) % length == 0 and prefix * (len(text) // length) == text:
                    return prefix
            return text

        try:
            titles = self.page.locator(".FilterModalPC_filterItemTitle__C5bMh").all()
            return [_deduplicate(t.inner_text(timeout=500).strip()) for t in titles]
        except Exception as e:
            self.logger.error(f"获取 Filter 分组名称失败: {e}")
            raise

    def get_filter_badge_count(self):
        """获取 Filter 按钮角标数字（如显示 '· 1' 返回 1，未激活返回 0）"""
        try:
            filter_item = self.page.locator(self.FILTER_ITEM_WRAPPER).filter(has_text="Filter").first
            cls = filter_item.get_attribute("class", timeout=2000) or ""
            if "Active" not in cls:
                return 0
            badge_el = filter_item.locator(self.FILTER_BADGE_POINT).first
            badge_text = badge_el.inner_text(timeout=2000)
            filter_text = filter_item.inner_text(timeout=2000)
            # Extract number after '·'
            import re
            match = re.search(r'\d+', filter_text)
            return int(match.group()) if match else 0
        except Exception:
            return 0

    def is_filter_active(self):
        """判断 Filter 按钮是否处于激活状态"""
        try:
            filter_item = self.page.locator(self.FILTER_ITEM_WRAPPER).filter(has_text="Filter").first
            cls = filter_item.get_attribute("class", timeout=2000) or ""
            return "Active" in cls
        except Exception:
            return False

    # ========== Location / 城市切换 ==========

    def click_city_filter(self):
        """点击城市筛选下拉（如 Abu Dhabi）"""
        try:
            city_el = self.page.locator(self.FILTER_ITEM_CONTENT).filter(has_text="Abu Dhabi").first
            city_el.scroll_into_view_if_needed()
            # 先移开鼠标避免 TopBar 下拉菜单遮挡筛选栏
            self.page.mouse.move(0, 0)
            self.page.wait_for_timeout(300)
            city_el.click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击城市筛选失败: {e}")
            raise

    def select_city_from_quick_list(self, city_name):
        """从快速城市列表中选择城市"""
        try:
            self.page.locator(self.CITY_QUICK_TAG).filter(has_text=city_name).first.click()
            self.page.wait_for_timeout(3000)
        except Exception as e:
            self.logger.error(f"从快速列表选择城市 '{city_name}' 失败: {e}")
            raise

    def is_city_dropdown_visible(self):
        """判断城市下拉是否可见"""
        try:
            return self.page.locator(self.CITY_QUICK_TAG).first.is_visible(timeout=3000)
        except Exception:
            return False

    # ========== Price 价格筛选 ==========

    def click_price_filter(self):
        """点击 Price 筛选下拉"""
        try:
            self.page.locator(self.FILTER_ITEM_CONTENT).filter(has_text="Price").first.click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击 Price 筛选失败: {e}")
            raise

    def set_price_range(self, min_price, max_price):
        """设置价格/里程区间（适用 Price 和 Mileage 面板）"""
        try:
            inputs = self.page.locator(self.RANGE_PRICE_MIN).all()
            min_input = inputs[0] if len(inputs) >= 1 else None
            max_input = inputs[1] if len(inputs) >= 2 else None
            if min_price is not None and min_input:
                min_input.fill(str(min_price))
            if max_price is not None and max_input:
                max_input.fill(str(max_price))
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"设置价格区间失败: {e}")
            raise

    def click_range_confirm(self):
        """点击价格/里程区间面板的 Confirm 按钮"""
        try:
            self.page.locator(self.RANGE_CONFIRM_BTN).first.click()
            self.page.wait_for_timeout(3000)
        except Exception as e:
            self.logger.error(f"点击区间 Confirm 失败: {e}")
            raise

    def is_price_panel_visible(self):
        """判断 Price 输入面板是否可见"""
        try:
            return self.page.locator(self.RANGE_PRICE_MIN).first.is_visible(timeout=3000)
        except Exception:
            return False



    # ========== Mileage 里程筛选 ==========

    def click_mileage_filter(self):
        """点击 Mileage 筛选下拉"""
        try:
            self.page.locator(self.FILTER_ITEM_CONTENT).filter(has_text="Mileage").first.click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击 Mileage 筛选失败: {e}")
            raise

    # ========== Brand 品牌筛选 ==========

    def click_brand_filter(self):
        """点击 Brand 筛选下拉"""
        try:
            self.page.locator(self.FILTER_ITEM_CONTENT).filter(has_text="Brand").first.click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击 Brand 筛选失败: {e}")
            raise

    def select_brand_by_popular(self, brand_alt_text):
        """从热门品牌图标中选择品牌（通过 alt 属性）"""
        try:
            self.page.get_by_alt_text(brand_alt_text).first.click()
            self.page.wait_for_timeout(3000)
        except Exception as e:
            self.logger.error(f"选择热门品牌 '{brand_alt_text}' 失败: {e}")
            raise

    def select_brand_from_list(self, brand_name):
        """从品牌列表（按字母排序）中选择品牌"""
        try:
            self.page.locator(self.CITY_ANCHOR_ITEM).filter(has_text=brand_name).first.click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"从列表选择品牌 '{brand_name}' 失败: {e}")
            raise

    def is_brand_modal_visible(self):
        """判断品牌选择面板是否可见"""
        try:
            return self.page.locator(self.BRAND_MODAL).first.is_visible(timeout=3000)
        except Exception:
            return False

    # ========== Reset 重置 ==========

    def click_reset(self):
        """点击全局 Reset 按钮"""
        try:
            self.page.locator(self.RESET_BTN).first.click()
            self.page.wait_for_timeout(3000)
        except Exception as e:
            self.logger.error(f"点击 Reset 失败: {e}")
            raise

    def is_reset_visible(self):
        """判断 Reset 按钮是否可见"""
        try:
            return self.page.locator(self.RESET_BTN).first.is_visible(timeout=3000)
        except Exception:
            return False

    # ========== 列表结果 ==========

    def get_car_items_count(self):
        """获取当前列表中车辆卡片数量"""
        try:
            return len(self.page.locator(self.CAR_ITEM_LINK).all())
        except Exception as e:
            self.logger.error(f"获取车辆卡片数量失败: {e}")
            raise

    def click_first_car_card(self):
        """点击第一个车辆卡片进入详情页（卡片 target 属性为完整 URL，直接导航）"""
        try:
            href = self.page.locator(self.CAR_ITEM_LINK).first.get_attribute("href", timeout=3000) or ""
            if href and href.startswith("http"):
                self.page.goto(href, wait_until="domcontentloaded", timeout=30000)
            else:
                self.page.locator(self.CAR_ITEM_LINK).first.click()
            self.page.wait_for_timeout(3000)
        except Exception as e:
            self.logger.error(f"点击车辆卡片失败: {e}")
            raise

    def get_first_car_href(self):
        """获取第一个车辆卡片的链接"""
        try:
            return self.page.locator(self.CAR_ITEM_LINK).first.get_attribute("href", timeout=3000) or ""
        except Exception as e:
            self.logger.error(f"获取车辆卡片链接失败: {e}")
            raise

    def is_empty_state_visible(self):
        """判断空态是否显示（列表无结果）"""
        try:
            empty_classes = [
                "[class*='empty']", "[class*='Empty']",
                "[class*='noResult']", "[class*='noData']"
            ]
            for cls in empty_classes:
                if self.page.locator(cls).first.is_visible(timeout=2000):
                    return True
            # Also check by text - but empty state may have different text
            return self.get_car_items_count() == 0
        except Exception:
            return self.get_car_items_count() == 0

    def get_card_titles(self, limit=None):
        """获取列表中所有卡片的标题文本列表"""
        try:
            cards = self.page.locator(self.CAR_ITEM_LINK).all()
            if limit:
                cards = cards[:limit]
            titles = []
            for card in cards:
                el = card.locator(self.CAR_TITLE)
                if el.count():
                    titles.append(el.inner_text().strip())
            return titles
        except Exception as e:
            self.logger.error(f"获取卡片标题失败: {e}")
            raise

    def get_card_prices(self, limit=None):
        """获取列表中所有卡片的价格文本（如 'AED 123'），无价格返回空字符串"""
        try:
            cards = self.page.locator(self.CAR_ITEM_LINK).all()
            if limit:
                cards = cards[:limit]
            prices = []
            for card in cards:
                sym_el = card.locator(self.CAR_PRICE_SYMBOL)
                amt_el = card.locator(self.CAR_PRICE_AMOUNT)
                sym = sym_el.inner_text().strip() if sym_el.count() else ""
                amt = amt_el.inner_text().strip() if amt_el.count() else ""
                prices.append(f"{sym}{amt}".strip())
            return prices
        except Exception as e:
            self.logger.error(f"获取卡片价格失败: {e}")
            raise

    def get_card_detail_params(self, card_index=0):
        """获取指定卡片的详情参数列表（年份、里程、城市）"""
        try:
            card = self.page.locator(self.CAR_ITEM_LINK).nth(card_index)
            spans = card.locator(self.CAR_DETAIL_SPAN).all()
            return [s.inner_text().strip() for s in spans]
        except Exception as e:
            self.logger.error(f"获取卡片详情参数失败: {e}")
            raise

    def get_card_image_src(self, card_index=0):
        """获取指定卡片封面图的 src"""
        try:
            card = self.page.locator(self.CAR_ITEM_LINK).nth(card_index)
            img = card.locator(self.CAR_IMAGE)
            return img.get_attribute("src", timeout=3000) or "" if img.count() else ""
        except Exception as e:
            self.logger.error(f"获取卡片图片 src 失败: {e}")
            raise

    def get_card_image_alt(self, card_index=0):
        """获取指定卡片封面图的 alt 文本"""
        try:
            card = self.page.locator(self.CAR_ITEM_LINK).nth(card_index)
            img = card.locator(self.CAR_IMAGE)
            return img.get_attribute("alt", timeout=3000) or "" if img.count() else ""
        except Exception as e:
            self.logger.error(f"获取卡片图片 alt 失败: {e}")
            raise

    def get_card_href(self, card_index=0):
        """获取指定卡片的跳转链接"""
        try:
            card = self.page.locator(self.CAR_ITEM_LINK).nth(card_index)
            return card.get_attribute("href", timeout=3000) or ""
        except Exception as e:
            self.logger.error(f"获取卡片链接失败: {e}")
            raise

    def is_next_page_btn_visible(self):
        """判断分页 Next 按钮是否可见（实际为 a.page-link）"""
        try:
            return self.page.locator("a.page-link").filter(has_text="Next").first.is_visible(timeout=3000)
        except Exception:
            return False

    def click_next_page(self):
        """点击分页 Next 按钮"""
        try:
            self.page.locator("a.page-link").filter(has_text="Next").first.click()
            self.page.wait_for_timeout(3000)
        except Exception as e:
            self.logger.error(f"点击 Next 页失败: {e}")
            raise

    # ========== 导航/辅助 ==========

    def click_login_register(self):
        """点击右上角登录/注册按钮"""
        try:
            self.page.get_by_text("Log in / Register").first.click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击登录/注册失败: {e}")
            raise

    def click_browse_menu(self):
        """点击 Browse 下拉导航菜单"""
        try:
            self.page.get_by_text("Browse", exact=True).first.click()
            self.page.wait_for_timeout(1500)
        except Exception as e:
            self.logger.error(f"点击 Browse 失败: {e}")
            raise

    def is_login_register_visible(self):
        """判断登录/注册按钮是否可见"""
        try:
            return self.page.get_by_text("Log in / Register").first.is_visible(timeout=3000)
        except Exception:
            return False

    def go_back(self):
        """浏览器后退"""
        try:
            self.page.go_back()
            self.page.wait_for_timeout(4000)
        except Exception as e:
            self.logger.error(f"浏览器后退失败: {e}")
            raise

    def reload_page(self):
        """刷新页面"""
        try:
            self.page.reload(wait_until="domcontentloaded", timeout=30000)
            self.page.wait_for_timeout(5000)
        except Exception as e:
            self.logger.error(f"刷新页面失败: {e}")
            raise
