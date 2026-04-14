"""
AE站 首页搜索输入框 Page Object

覆盖：底纹词、Search按钮、Clear按钮、Sug词、历史记录
"""
from pages.base_page import BasePage
from utils.logger import setup_logger


class HomeSearchPage(BasePage):
    """首页搜索区域页面对象"""

    SEARCH_INPUT = "input[type='text']"
    SEARCH_BUTTON = ".TopBarMiddleContent_searchButton__3UG6i"
    CLEAR_BUTTON = ".CustomInput_searchClear___ZaYy"
    DROPDOWN_WRAPPER = ".TopBarMiddleContent_dropdownWrapper__MT_eh"
    DROPDOWN_SHOW_CLASS = "dropdownWrapperShow"
    SUG_ITEMS = ".SuggestItem_modalSugItem__iYU6f"
    HISTORY_LIST = ".SearchSuggestContent_modalHistoryList__vD8Y_"
    HISTORY_ITEMS = ".SearchSuggestContent_modalHistoryItemPC__W7Zwc"
    HISTORY_TITLE = ".SearchSuggestContent_modalHistoryListTitle__s1S_g"

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    # ========== 搜索框操作 ==========

    def get_search_input_placeholder(self):
        """获取搜索框 placeholder 文本"""
        try:
            return self.page.locator(self.SEARCH_INPUT).first.get_attribute("placeholder")
        except Exception as e:
            self.logger.error(f"获取 placeholder 失败: {e}")
            raise

    def get_search_input_value(self):
        """获取搜索框当前值"""
        try:
            return self.page.locator(self.SEARCH_INPUT).first.input_value()
        except Exception as e:
            self.logger.error(f"获取搜索框值失败: {e}")
            raise

    def is_search_input_focused(self):
        """判断搜索框是否处于聚焦状态"""
        try:
            return self.page.evaluate(
                "() => document.activeElement === document.querySelector(\"input[type='text']\")"
            )
        except Exception as e:
            self.logger.error(f"判断聚焦状态失败: {e}")
            raise

    def click_search_input(self):
        """点击搜索框使其聚焦"""
        try:
            self.page.locator(self.SEARCH_INPUT).first.click()
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"点击搜索框失败: {e}")
            raise

    def fill_search_input(self, keyword):
        """
        输入搜索关键词（使用 press_sequentially 触发防抖）

        Args:
            keyword: 搜索关键词
        """
        try:
            self.page.locator(self.SEARCH_INPUT).first.click()
            self.page.locator(self.SEARCH_INPUT).first.fill(keyword)
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"输入搜索关键词失败: {e}")
            raise

    def fill_search_input_slowly(self, keyword):
        """
        逐字输入搜索关键词（触发 sug 接口 debounce）

        Args:
            keyword: 搜索关键词
        """
        try:
            self.page.locator(self.SEARCH_INPUT).first.click()
            self.page.locator(self.SEARCH_INPUT).first.press_sequentially(keyword, delay=100)
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"逐字输入关键词失败: {e}")
            raise

    def clear_search_input(self):
        """点击 Clear 按钮清空搜索框"""
        try:
            self.page.locator(self.CLEAR_BUTTON).first.click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击 Clear 按钮失败: {e}")
            raise

    def is_clear_button_visible(self):
        """判断 Clear 按钮是否可见"""
        try:
            return self.page.locator(self.CLEAR_BUTTON).first.is_visible()
        except Exception:
            return False

    def click_search_button(self):
        """点击 Search 按钮执行搜索"""
        try:
            self.page.evaluate("() => window.scrollTo(0, 0)")
            self.page.wait_for_timeout(300)
            self.page.locator(self.SEARCH_BUTTON).first.click(force=True)
        except Exception as e:
            self.logger.error(f"点击 Search 按钮失败: {e}")
            raise

    def search_by_enter(self):
        """在搜索框中按 Enter 键执行搜索"""
        try:
            self.page.locator(self.SEARCH_INPUT).first.press("Enter")
        except Exception as e:
            self.logger.error(f"按 Enter 键搜索失败: {e}")
            raise

    def click_page_blank(self):
        """点击页面空白区域使搜索框失焦"""
        try:
            self.page.locator("body").click(position={"x": 10, "y": 10})
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击空白区域失败: {e}")
            raise

    def get_search_button_text(self):
        """获取 Search 按钮文案"""
        try:
            return self.page.locator(self.SEARCH_BUTTON).first.inner_text()
        except Exception as e:
            self.logger.error(f"获取 Search 按钮文案失败: {e}")
            raise

    # ========== Sug 词操作 ==========

    def is_sug_dropdown_visible(self):
        """判断 Sug 词下拉面板是否可见（class 含 dropdownWrapperShow）"""
        try:
            wrapper = self.page.locator(self.DROPDOWN_WRAPPER).first
            class_attr = wrapper.get_attribute("class") or ""
            return self.DROPDOWN_SHOW_CLASS in class_attr
        except Exception:
            return False

    def get_sug_items(self):
        """获取当前展示的所有 Sug 词元素"""
        try:
            self.page.wait_for_selector(self.SUG_ITEMS, timeout=3000)
            return self.page.locator(self.SUG_ITEMS).all()
        except Exception:
            return []

    def get_sug_items_count(self):
        """获取 Sug 词数量"""
        try:
            self.page.wait_for_selector(self.SUG_ITEMS, timeout=3000)
            return self.page.locator(self.SUG_ITEMS).count()
        except Exception:
            return 0

    def get_pure_sug_items_count(self):
        """获取纯 Sug 词数量（排除历史条目，历史条目同时含 modalHistoryItemPC class）"""
        try:
            return self.page.evaluate(
                "() => Array.from(document.querySelectorAll('.SuggestItem_modalSugItem__iYU6f'))"
                ".filter(el => !el.classList.contains('SearchSuggestContent_modalHistoryItemPC__W7Zwc')).length"
            )
        except Exception:
            return 0

    def get_pure_sug_item_texts(self):
        """获取纯 Sug 词的文本列表（排除历史条目）"""
        try:
            return self.page.evaluate(
                "() => Array.from(document.querySelectorAll('.SuggestItem_modalSugItem__iYU6f'))"
                ".filter(el => !el.classList.contains('SearchSuggestContent_modalHistoryItemPC__W7Zwc'))"
                ".map(el => el.innerText.trim())"
            )
        except Exception:
            return []

    def click_pure_sug_item(self, index=0):
        """
        点击指定索引的纯 Sug 词（排除历史条目）

        Args:
            index: 纯 Sug 词索引（默认第一条）
        """
        try:
            self.page.evaluate(
                f"() => {{ const items = Array.from(document.querySelectorAll('.SuggestItem_modalSugItem__iYU6f'))"
                f".filter(el => !el.classList.contains('SearchSuggestContent_modalHistoryItemPC__W7Zwc'));"
                f"if(items[{index}]) items[{index}].click(); }}"
            )
            self.page.wait_for_timeout(3000)
        except Exception as e:
            self.logger.error(f"点击纯 Sug 词失败: {e}")
            raise

    def get_first_pure_sug_text(self):
        """获取第一条纯 Sug 词文本"""
        try:
            return self.page.evaluate(
                "() => { const items = Array.from(document.querySelectorAll('.SuggestItem_modalSugItem__iYU6f'))"
                ".filter(el => !el.classList.contains('SearchSuggestContent_modalHistoryItemPC__W7Zwc'));"
                "return items[0]?.innerText?.trim() || ''; }"
            )
        except Exception:
            return ""

    def get_sug_ellipsis_info(self):
        """
        获取纯 Sug 词的 CSS 截断属性信息

        Returns:
            list: 每个条目包含 hasSingleLineEllipsis, overflow, textOverflow, whiteSpace
        """
        try:
            return self.page.evaluate(
                "() => Array.from(document.querySelectorAll('.SuggestItem_modalSugItem__iYU6f'))"
                ".filter(el => !el.classList.contains('SearchSuggestContent_modalHistoryItemPC__W7Zwc'))"
                ".map(el => { const style = window.getComputedStyle(el);"
                "return { hasSingleLineEllipsis: el.classList.contains('singleLineEllipsis'),"
                "overflow: style.overflow, textOverflow: style.textOverflow, whiteSpace: style.whiteSpace }; })"
            )
        except Exception:
            return []

    def click_sug_item(self, index=0):
        """
        点击指定索引的 Sug 词

        Args:
            index: Sug 词索引（默认第一条）
        """
        try:
            items = self.page.locator(self.SUG_ITEMS).all()
            if items and len(items) > index:
                items[index].click()
                self.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception as e:
            self.logger.error(f"点击 Sug 词失败: {e}")
            raise

    def get_sug_item_text(self, index=0):
        """获取指定索引的 Sug 词文案"""
        try:
            items = self.page.locator(self.SUG_ITEMS).all()
            if items and len(items) > index:
                return items[index].inner_text()
            return ""
        except Exception as e:
            self.logger.error(f"获取 Sug 词文案失败: {e}")
            return ""

    # ========== 历史记录操作 ==========

    def is_history_panel_visible(self):
        """判断历史记录面板是否可见"""
        try:
            return self.page.locator(self.HISTORY_LIST).first.is_visible()
        except Exception:
            return False

    def get_history_title_text(self):
        """获取历史记录标题文案"""
        try:
            return self.page.locator(self.HISTORY_TITLE).first.inner_text()
        except Exception:
            return ""

    def get_history_items_count(self):
        """获取历史记录条数"""
        try:
            self.page.wait_for_selector(self.HISTORY_ITEMS, timeout=3000)
            return self.page.locator(self.HISTORY_ITEMS).count()
        except Exception:
            return 0

    def get_history_item_text(self, index=0):
        """获取指定索引的历史记录文案"""
        try:
            items = self.page.locator(self.HISTORY_ITEMS).all()
            if items and len(items) > index:
                return items[index].inner_text().strip()
            return ""
        except Exception:
            return ""

    def click_history_item(self, index=0):
        """点击指定索引的历史记录条目"""
        try:
            items = self.page.locator(self.HISTORY_ITEMS).all()
            if items and len(items) > index:
                items[index].click()
                self.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception as e:
            self.logger.error(f"点击历史记录失败: {e}")
            raise

    def click_history_item_by_js(self, index=0):
        """通过 JS 点击指定索引的历史记录条目（规避 React 事件问题）"""
        try:
            self.page.evaluate(
                f"() => {{ const items = document.querySelectorAll('.SearchSuggestContent_modalHistoryItemPC__W7Zwc');"
                f"if(items[{index}]) items[{index}].click(); }}"
            )
            # 等待页面跳转
            self.page.wait_for_url("**/cate/**", timeout=10000)
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"JS 点击历史记录失败: {e}")
            raise

    def get_history_items_texts(self):
        """获取所有历史记录文本列表"""
        try:
            return self.page.evaluate(
                "() => Array.from(document.querySelectorAll('.SearchSuggestContent_modalHistoryItemPC__W7Zwc'))"
                ".map(el => el.innerText?.trim())"
            )
        except Exception:
            return []

    def focus_search_input_by_js(self):
        """通过 JS focus 聚焦搜索框（规避 React hydration 问题）"""
        try:
            self.page.evaluate(
                "() => { const el = document.querySelector('#custom-input'); if(el) { el.focus(); el.click(); } }"
            )
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"聚焦搜索框失败: {e}")
            raise

    def type_keyword_by_js_and_keyboard(self, keyword):
        """
        通过 JS focus + keyboard.type 输入关键词（规避 React hydration 问题）

        Args:
            keyword: 要输入的关键词
        """
        try:
            self.page.evaluate(
                "() => { const el = document.querySelector('#custom-input'); if(el) { el.focus(); el.value = ''; } }"
            )
            self.page.wait_for_timeout(200)
            self.page.keyboard.type(keyword)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"键盘输入关键词失败: {e}")
            raise

    # ========== 导航与 URL 验证 ==========

    def navigate_to_home(self, base_url):
        """导航到首页（使用官方推荐的元素级等待策略）"""
        try:
            # 官方推荐：使用 domcontentloaded + 增加超时 + 元素级等待
            self.page.goto(base_url, timeout=60000, wait_until="domcontentloaded")
            # 等待搜索框或页面关键元素加载完成
            self.page.locator(self.SEARCH_INPUT).or_(self.page.locator(self.SEARCH_BUTTON)).first.wait_for(state="visible", timeout=10000)
        except Exception as e:
            self.logger.error(f"导航到首页失败: {e}")
            raise

    def get_current_url(self):
        """获取当前 URL"""
        return self.page.url

    def wait_for_search_result_page(self, timeout=10000):
        """等待跳转到搜索结果页"""
        try:
            self.page.wait_for_url("**/cate/**", timeout=timeout)
        except Exception as e:
            self.logger.error(f"等待搜索结果页超时: {e}")
            raise
