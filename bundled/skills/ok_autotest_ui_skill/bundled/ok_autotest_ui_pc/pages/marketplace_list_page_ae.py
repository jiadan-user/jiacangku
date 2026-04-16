# pages/marketplace_list_page_ae.py
import re
from urllib.parse import urljoin

from pages.base_page import BasePage
from utils.logger import setup_logger

# 详情页 URL 含 /cate-{分类}/，与列表 /cate-marketplace/ 区分（用例文档实测路径）
# 匹配详情分类段：cate-apple3、cate-bedroom-furniture 等（排除 cate-marketplace）；兼容无前导 / 的相对 href
_MARKETPLACE_DETAIL_HREF = re.compile(r"cate-(?!marketplace)\w", re.IGNORECASE)


class MarketplaceListPageAe(BasePage):
    """AE站 Marketplace 二手列表页面对象（静默执行）"""
    
    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()
    
    # ========== 页面导航 ==========
    
    def navigate_to_marketplace_from_homepage(self):
        """
        从首页金刚位进入 Marketplace 列表页
        前置条件：已在首页
        MCP 录制: await page.getByRole('link', { name: 'Marketplace Marketplace' }).click();
        """
        try:
            marketplace_link = self.page.get_by_role('link', name='Marketplace Marketplace')
            marketplace_link.click()
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击 Marketplace 金刚位失败: {e}")
            raise
    
    def navigate_to_marketplace_directly(self, base_url, max_retries=3):
        """
        直接导航到 Marketplace 列表页（带重试机制）
        
        Args:
            base_url: 站点基础 URL
            max_retries: 最大重试次数，默认3次
        """
        url = f"{base_url}/en/city-abu-dhabi/cate-marketplace/"
        last_error = None
        
        for attempt in range(max_retries):
            try:
                self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
                self.page.wait_for_load_state("load", timeout=15000)
                self.page.wait_for_timeout(2000)
                
                # 验证是否成功加载（不是错误页）
                if "chrome-error://" in self.page.url or "about:blank" in self.page.url:
                    raise RuntimeError(f"页面导航失败，当前URL: {self.page.url}")
                
                self.logger.info(f"✓ 导航成功: {self.page.url}")
                return
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"导航尝试 {attempt + 1}/{max_retries} 失败: {e}")
                
                if attempt < max_retries - 1:
                    self.page.wait_for_timeout(2000)
                    # 尝试重新加载页面
                    try:
                        self.page.reload(wait_until="domcontentloaded", timeout=15000)
                    except:
                        pass
        
        self.logger.error(f"直接导航到 Marketplace 失败（已重试{max_retries}次）: {last_error}")
        raise RuntimeError(f"导航失败: {last_error}")
    
    def prepare_marketplace_list_with_transaction_chip(self, base_url: str, attempts: int = 3) -> None:
        """多次直达列表直至筛选区与 Transaction 文案均出现（TC040 等边界用例）"""
        last_err = None
        for i in range(attempts):
            try:
                self.navigate_to_marketplace_directly(base_url)
                if not self.is_filter_area_visible(timeout=12000):
                    raise RuntimeError("filter area missing")
                tx = self.page.get_by_text("Transaction", exact=True).first
                if not tx.is_visible(timeout=12000):
                    raise RuntimeError("Transaction not visible")
                return
            except Exception as e:
                last_err = e
                self.page.wait_for_timeout(2500)
        raise RuntimeError(f"marketplace list not ready after {attempts} tries: {last_err}")

    def wait_for_transaction_filter_entry(self, timeout=45000):
        """Transaction 文案可见后再点筛选（慢网/冷启动，TC040）"""
        loc = self.page.get_by_text("Transaction", exact=True).first
        try:
            loc.wait_for(state="visible", timeout=timeout)
        except Exception:
            try:
                self.page.reload(wait_until="domcontentloaded", timeout=30000)
                self.page.wait_for_timeout(3500)
                loc.wait_for(state="visible", timeout=timeout)
            except Exception as e:
                self.logger.error(f"等待 Transaction 入口失败: {e}")
                raise

    # ========== 页面状态检查 ==========
    
    def is_marketplace_page_loaded(self, timeout=10000):
        """
        判断 Marketplace 列表页是否加载完成
        
        Returns:
            bool: True 表示页面已加载
        """
        try:
            # 检查URL
            if "marketplace" not in self.page.url.lower():
                return False
            
            # 检查关键元素：搜索框或商品卡片列表
            search_box = self.page.get_by_placeholder('Search').first
            if search_box.is_visible(timeout=timeout):
                return True
            
            # 备选检查：商品卡片
            item_cards = self.page.locator('[class*="list-components-item-card"]').first
            if item_cards.is_visible(timeout=2000):
                return True
            
            return False
        except Exception:
            return False
    
    # ========== 搜索功能 ==========
    
    def click_search_box(self):
        """
        点击搜索框（触发历史搜索或联想词）
        MCP 录制: await page.getByRole('textbox', { name: 'Search for anything' }).click();
        """
        try:
            search_box = self.page.get_by_role('textbox', name='Search for anything')
            search_box.click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击搜索框失败: {e}")
            raise
    
    def input_search_keyword(self, keyword):
        """
        在搜索框输入关键词
        MCP 录制: await page.getByRole('textbox', { name: 'Search for anything' }).fill('iPhone');
        
        Args:
            keyword: 搜索关键词
        """
        try:
            # 等待页面稳定
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            self.page.wait_for_timeout(500)
            
            # 多种定位策略，按优先级尝试
            search_box = None
            locators = [
                lambda: self.page.get_by_role('textbox', name='Search for anything'),
                lambda: self.page.get_by_placeholder('Search').first,
                lambda: self.page.locator('input[placeholder*="Search"]').first,
                lambda: self.page.locator('input[type="text"]').first,
                lambda: self.page.locator('input.search-input').first,
            ]
            
            for i, locator_func in enumerate(locators):
                try:
                    search_box = locator_func()
                    if search_box.is_visible(timeout=3000):
                        self.logger.info(f"✓ 使用定位器{i+1}找到搜索框")
                        break
                except Exception as e:
                    self.logger.debug(f"定位器{i+1}失败: {e}")
                    continue
            
            if search_box is None:
                raise Exception("无法定位搜索框（尝试了5种选择器）")
            
            search_box.fill(keyword)
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"输入搜索关键词失败: {e}")
            raise
    
    def submit_search(self):
        """
        提交搜索（按回车或点击搜索按钮）
        """
        try:
            # 方法1：按回车键
            search_box = self.page.get_by_placeholder('Search').first
            search_box.press('Enter')
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"提交搜索失败: {e}")
            raise
    
    def clear_search(self):
        """
        清空搜索框并提交（使搜索参数生效）
        """
        try:
            search_box = self.page.get_by_placeholder('Search').first
            
            # 方法1：三次点击选中所有文本并删除
            search_box.click()
            search_box.click(click_count=3)  # 三击选中全部
            self.page.keyboard.press('Backspace')
            self.page.wait_for_timeout(300)
            
            # 如果还有内容，用 fill 清空
            if search_box.input_value():
                search_box.fill('')
                self.page.wait_for_timeout(300)
            
            # 提交清空（按回车让URL更新）
            search_box.press('Enter')
            self.page.wait_for_timeout(1000)
            
        except Exception as e:
            self.logger.error(f"清空搜索失败: {e}")
            raise
    
    def get_search_keyword_value(self):
        """
        获取搜索框当前值
        
        Returns:
            str: 搜索框内容
        """
        try:
            search_box = self.page.get_by_placeholder('Search').first
            return search_box.input_value()
        except Exception as e:
            self.logger.error(f"获取搜索框值失败: {e}")
            return ""
    
    # ========== Transaction 筛选（MCP 录制）==========
    
    def click_transaction_filter(self):
        """
        打开 Transaction 筛选器
        MCP: await page.getByText('Transaction', { exact: true }).click();
        """
        try:
            try:
                fa = self.page.locator("#istPageFilterArea")
                try:
                    fa.first.scroll_into_view_if_needed()
                    self.page.wait_for_timeout(400)
                except Exception:
                    pass
                if fa.is_visible(timeout=8000):
                    fa.get_by_text("Transaction", exact=True).first.click(timeout=20000, force=True)
                else:
                    raise RuntimeError("filter area not visible")
            except Exception:
                try:
                    self.page.evaluate("window.scrollTo(0, 0)")
                    self.page.wait_for_timeout(400)
                except Exception:
                    pass
                self.page.get_by_text("Transaction", exact=True).first.click(timeout=60000, force=True)
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击 Transaction 筛选失败: {e}")
            raise
    
    def select_transaction_online(self):
        """
        在 Transaction 面板中选择 Online
        MCP: await page.getByText('Online', { exact: true }).click();
        """
        try:
            self.page.get_by_text("Online", exact=True).click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择 Online 失败: {e}")
            raise
    
    def select_transaction_offline(self):
        """
        在列表筛选区从 Online 切换为 Offline
        改进：兼容芯片状态（已应用 Online 时，先点击芯片取消，再选择 Offline）
        """
        try:
            # 方案1: 尝试点击筛选区的 Online 芯片（如果存在）
            filter_area = self.page.locator("#istPageFilterArea")
            online_chip = filter_area.get_by_text("Online", exact=True).first
            
            try:
                if online_chip.is_visible(timeout=2000):
                    self.logger.info("检测到 Online 芯片，点击取消...")
                    online_chip.click(timeout=5000)
                    self.page.wait_for_timeout(800)
            except Exception:
                # 如果芯片不可见，说明还在面板中，继续原有逻辑
                self.logger.info("未检测到 Online 芯片，使用面板切换")
            
            # 方案2: 确保面板打开 - 点击 Transaction 或当前芯片
            try:
                # 尝试点击 Transaction 文字（如果面板已关闭）
                self.page.get_by_text("Transaction", exact=True).first.click(timeout=3000)
                self.page.wait_for_timeout(500)
            except Exception:
                # 如果 Transaction 文字不存在，尝试点击筛选区任意可点击元素
                try:
                    filter_area.first.click(timeout=3000)
                    self.page.wait_for_timeout(500)
                except Exception:
                    pass
            
            # 取消 Online 选择（如果面板中有 Online 选项）
            try:
                panel_online = self.page.get_by_text("Online", exact=True)
                if panel_online.count() > 0:
                    # 点击面板中的 Online（取消选择）
                    for i in range(panel_online.count()):
                        try:
                            panel_online.nth(i).click(timeout=2000)
                            self.page.wait_for_timeout(300)
                            break
                        except Exception:
                            continue
            except Exception:
                pass
            
            # 选择 Offline
            self.page.get_by_text("Offline", exact=True).click(timeout=10000)
            self.page.wait_for_timeout(500)
            
        except Exception as e:
            self.logger.error(f"切换为 Offline 失败: {e}")
            # 不抛出异常，允许测试继续
            self.logger.warning("尝试直接点击 Offline（降级方案）")
            try:
                self.page.get_by_text("Offline", exact=True).first.click(timeout=5000)
                self.page.wait_for_timeout(500)
            except Exception as e2:
                self.logger.error(f"降级方案也失败: {e2}")
                raise
    
    def click_filter_confirm(self):
        """
        筛选面板点击 Confirm 应用条件
        MCP: await page.getByRole('button', { name: 'Confirm' }).click();
        """
        try:
            self.page.get_by_role("button", name="Confirm").click()
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击筛选 Confirm 失败: {e}")
            raise
    
    def wait_until_product_link_visible(self, link_name: str, timeout: int = 25000) -> bool:
        """轮询直至指定商品详情链接可见（筛选后列表异步刷新）"""
        elapsed = 0
        step = 1500
        while elapsed < timeout:
            if self.is_product_link_visible(link_name, timeout=2500):
                return True
            self.page.wait_for_timeout(step)
            elapsed += step
        return False

    def is_filter_area_visible(self, timeout=10000):
        """列表筛选容器 #istPageFilterArea 是否可见（文档/MCP 摘要）"""
        try:
            return self.page.locator("#istPageFilterArea").is_visible(timeout=timeout)
        except Exception:
            return False
    
    def is_transaction_online_label_in_filter_area(self, timeout=8000):
        """筛选区内展示 Online 标签（TC002 断言；容器同 MCP #istPageFilterArea）"""
        try:
            return self.page.locator("#istPageFilterArea").get_by_text(
                "Online", exact=True
            ).first.is_visible(timeout=timeout)
        except Exception:
            return False
    
    @staticmethod
    def _href_is_marketplace_detail_listing(href: str) -> bool:
        """是否为进入非 marketplace 分类下的商品详情链接（排除 cate-marketplace?attr 等筛选链）"""
        if not href or href.strip() in ("", "#"):
            return False
        return bool(_MARKETPLACE_DETAIL_HREF.search(href))

    @staticmethod
    def _href_is_transaction_or_filter_noise(href: str) -> bool:
        """同名 link 可能是 Transaction/筛选产生的查询链，不应作为进详情目标"""
        if not href:
            return False
        h = href.strip().lower()
        if h.startswith("?"):
            return True
        if "cate-marketplace" in h and "attr_" in h:
            return True
        return False

    @staticmethod
    def _link_is_inside_ist_page_filter_area(locator) -> bool:
        """同名 accessible name 可能同时出现在 #istPageFilterArea 内，与列表商品链区分（MCP 容器 id）"""
        try:
            return bool(
                locator.evaluate(
                    "el => !!document.querySelector('#istPageFilterArea')?.contains(el)"
                )
            )
        except Exception:
            return False

    def is_product_link_visible(self, link_name: str, timeout=8000):
        """
        指定名称的商品「详情」链接是否可见。
        MCP: getByRole('link', { name: ... })；若存在多条同名链接，取 href 指向详情分类路径者。
        """
        try:
            links = self.page.get_by_role("link", name=link_name)
            n = links.count()
            candidates = []
            for i in range(n):
                loc = links.nth(i)
                if self._link_is_inside_ist_page_filter_area(loc):
                    continue
                candidates.append(loc)
            if not candidates:
                candidates = [links.nth(i) for i in range(n)]
            for loc in candidates:
                if not loc.is_visible(timeout=timeout):
                    continue
                href = loc.get_attribute("href") or ""
                if self._href_is_marketplace_detail_listing(href):
                    return True
                if not self._href_is_transaction_or_filter_noise(href):
                    return True
            return False
        except Exception:
            return False

    def get_first_detail_listing_link_href(self) -> str:
        """
        列表区首条「进入商品详情」的链接 href（排除 #istPageFilterArea 内与噪声链）。
        用于 TC030 对照 Online/Offline 结果集。
        """
        try:
            links = self.page.get_by_role("link")
            n = links.count()
            for i in range(n):
                loc = links.nth(i)
                if not loc.is_visible(timeout=1500):
                    continue
                if self._link_is_inside_ist_page_filter_area(loc):
                    continue
                href = loc.get_attribute("href") or ""
                if self._href_is_marketplace_detail_listing(href):
                    return href
            return ""
        except Exception:
            return ""

    def press_escape(self):
        try:
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"按 ESC 失败: {e}")
            raise

    def open_transaction_panel_only(self):
        """
        仅打开 Transaction 面板，不切换筛选结果（TC040）。
        应用 Online/Offline 后 URL 可能带 attr 参数，筛选区常只展示 Online/Offline 芯片而无「Transaction」文案，
        与 MCP TC005 一致：优先在 #istPageFilterArea 内点当前交易态芯片再打开面板。
        """
        try:
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(350)
        except Exception:
            pass
        fa = self.page.locator("#istPageFilterArea")
        try:
            fa.first.scroll_into_view_if_needed()
            self.page.wait_for_timeout(400)
        except Exception:
            pass
        fa.wait_for(state="visible", timeout=20000)
        try:
            chip = fa.get_by_text("Transaction", exact=True).first
            if chip.is_visible(timeout=2500):
                chip.click(timeout=15000, force=True)
                self.page.wait_for_timeout(400)
                return
        except Exception:
            pass
        try:
            chip = fa.get_by_text("Online", exact=True).first
            if chip.is_visible(timeout=5000):
                chip.click(timeout=15000, force=True)
                self.page.wait_for_timeout(400)
                return
        except Exception:
            pass
        try:
            chip = fa.get_by_text("Offline", exact=True).first
            if chip.is_visible(timeout=5000):
                chip.click(timeout=15000, force=True)
                self.page.wait_for_timeout(400)
                return
        except Exception:
            pass
        self.wait_for_transaction_filter_entry()
        self.click_transaction_filter()

    def select_offline_in_transaction_panel_no_confirm(self):
        """面板内点选 Offline，不 Confirm（TC040）"""
        try:
            self.page.get_by_text("Offline", exact=True).first.click()
            self.page.wait_for_timeout(400)
        except Exception as e:
            self.logger.error(f"面板内选择 Offline 失败: {e}")
            raise

    def select_online_in_transaction_panel_no_confirm(self):
        """面板内点选 Online，不 Confirm（TC040）"""
        try:
            self.page.get_by_text("Online", exact=True).first.click()
            self.page.wait_for_timeout(400)
        except Exception as e:
            self.logger.error(f"面板内选择 Online 失败: {e}")
            raise

    def click_product_link_by_name(self, link_name: str):
        """
        点击指定名称的商品链接进入详情。
        MCP: await page.getByRole('link', { name: 'iPhone 12 Pro' }).click();
        先在全部同名 link 中查找指向详情分类的 href 并 goto（与点击等价、避免误点筛选链）。
        """
        try:
            links = self.page.get_by_role("link", name=link_name)
            n = links.count()
            detail_href = None
            for i in range(n):
                href = links.nth(i).get_attribute("href") or ""
                if self._href_is_marketplace_detail_listing(href):
                    detail_href = href
                    break
            if detail_href:
                resolved = urljoin(self.page.url, detail_href)
                self.page.goto(resolved, wait_until="domcontentloaded", timeout=30000)
                self.page.wait_for_timeout(2000)
                return
            outside_filter = []
            for i in range(n):
                loc = links.nth(i)
                if self._link_is_inside_ist_page_filter_area(loc):
                    continue
                outside_filter.append(loc)
            if not outside_filter:
                outside_filter = [links.nth(i) for i in range(n)]
            target = None
            fallback = None
            for loc in outside_filter:
                href = loc.get_attribute("href") or ""
                if self._href_is_marketplace_detail_listing(href):
                    target = loc
                    break
                if fallback is None and not self._href_is_transaction_or_filter_noise(href):
                    fallback = loc
            if target is None and fallback is None and outside_filter:
                for loc in reversed(outside_filter):
                    href = loc.get_attribute("href") or ""
                    if not self._href_is_transaction_or_filter_noise(href):
                        target = loc
                        break
            if target is None:
                target = fallback if fallback is not None else links.first
            target.click()
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击商品链接失败: {e}")
            raise


    # ========== 筛选功能 ==========
    
    def open_filter_panel(self):
        """
        打开筛选器面板
        MCP 录制: await page.getByText('Filter·').click();
        """
        try:
            # 多种定位策略
            filter_btn = None
            locators = [
                lambda: self.page.get_by_text('Filter·'),
                lambda: self.page.get_by_text('Filter'),
                lambda: self.page.locator('button:has-text("Filter")').first,
                lambda: self.page.locator('[class*="filter"][class*="button"]').first,
                lambda: self.page.locator('button:has([class*="filter-icon"])').first,
            ]
            
            for locator_func in locators:
                try:
                    filter_btn = locator_func()
                    if filter_btn.is_visible(timeout=2000):
                        break
                except Exception:
                    continue
            
            if filter_btn is None:
                raise Exception("无法定位筛选器按钮（尝试了多种选择器）")
            
            filter_btn.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"打开筛选器面板失败: {e}")
            raise
    
    def select_category_filter(self, category_name):
        """
        选择分类筛选
        
        Args:
            category_name: 分类名称（如 "Electronics"）
        """
        try:
            category_option = self.page.get_by_text(category_name, exact=True).first
            category_option.click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择分类筛选失败: {e}")
            raise
    
    def apply_filter(self):
        """
        应用筛选条件（点击确认按钮）
        """
        try:
            apply_btn = self.page.get_by_role('button', name='Apply').first
            if not apply_btn.is_visible(timeout=2000):
                # 备选文本
                apply_btn = self.page.locator('button:has-text("确认"), button:has-text("Confirm")').first
            
            apply_btn.click()
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"应用筛选失败: {e}")
            raise
    
    def clear_all_filters(self):
        """
        清除所有筛选条件
        实际文案: "Clear"
        """
        try:
            # 实际页面使用 "Clear" 文案
            clear_btn = self.page.get_by_role('button', name='Clear')
            clear_btn.click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"清除筛选失败: {e}")
            raise
    
    def is_filter_tag_visible(self, filter_name):
        """
        判断筛选标签是否可见
        
        Args:
            filter_name: 筛选标签文本
        
        Returns:
            bool: True 表示标签可见
        """
        try:
            tag = self.page.locator(f'span:has-text("{filter_name}"), .filter-tag:has-text("{filter_name}")').first
            return tag.is_visible(timeout=2000)
        except Exception:
            return False
    
    # ========== 排序功能 ==========
    
    def select_sort_option(self, sort_name):
        """
        选择排序方式
        MCP 录制: 
          1. await page.getByText('Best Match', { exact: true }).click(); (打开下拉)
          2. await page.getByText('Newest First').click(); (选择具体选项)
        
        Args:
            sort_name: 排序名称
                - "Best Match" (默认)
                - "Newest First" (最新优先)
                - "Lowest Price" (价格从低到高)
                - "Highest Price" (价格从高到低)
        """
        try:
            # 第1步：打开排序下拉框（点击当前排序选项）
            # 简化定位器：直接通过文本查找当前排序，不限制容器
            current_sort = None
            for sort_text in ["Best Match", "Newest First", "Lowest Price", "Highest Price"]:
                try:
                    loc = self.page.get_by_text(sort_text, exact=True).first
                    if loc.is_visible(timeout=1000):
                        current_sort = loc
                        break
                except Exception:
                    continue
            
            if current_sort is None:
                # Fallback：尝试通过其他方式定位排序区域
                self.logger.warning("未找到标准排序选项，尝试fallback定位")
                sort_selectors = [
                    'button:has-text("Match")',
                    '[class*="sort"]',
                    '[class*="Sort"]',
                    'button:has([class*="sort"])',
                ]
                for selector in sort_selectors:
                    try:
                        current_sort = self.page.locator(selector).first
                        if current_sort.is_visible(timeout=1000):
                            self.logger.info(f"✓ Fallback找到排序元素: {selector}")
                            break
                    except Exception:
                        continue
            
            if current_sort is None:
                raise RuntimeError("未找到当前排序选项（尝试了所有fallback）")
            
            current_sort.click()
            self.page.wait_for_timeout(800)
            
            # 第2步：在弹出的下拉菜单中选择目标排序选项
            # 增强定位策略：使用多种方式查找排序选项
            target_option = None
            selectors = [
                lambda: self.page.get_by_text(sort_name, exact=True).first,
                lambda: self.page.get_by_text(sort_name, exact=False).first,
                lambda: self.page.locator(f'text="{sort_name}"').first,
                lambda: self.page.locator(f'[role="option"]:has-text("{sort_name}")').first,
            ]
            
            for selector_func in selectors:
                try:
                    target_option = selector_func()
                    if target_option.is_visible(timeout=2000):
                        break
                except Exception:
                    continue
            
            if target_option is None:
                raise RuntimeError(f"未找到排序选项: {sort_name}")
            
            target_option.click()
            self.page.wait_for_timeout(500)
            
            # 第3步：点击确认按钮
            confirm_btn = self.page.get_by_role('button', name='Confirm')
            confirm_btn.click()
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            self.page.wait_for_timeout(2000)
            
        except Exception as e:
            self.logger.error(f"选择排序失败: {e}")
            raise
    
    def click_sort_confirm(self):
        """
        点击排序的确认按钮
        MCP 录制: await page.getByRole('button', { name: 'Confirm' }).click();
        """
        try:
            confirm_btn = self.page.get_by_role('button', name='Confirm')
            confirm_btn.click()
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击排序确认按钮失败: {e}")
            raise
    
    def open_sort_dropdown(self):
        """
        打开排序下拉框（不选择具体选项）
        用于TC045/TC046等需要单独打开下拉框的场景
        """
        try:
            # 查找当前排序选项并点击打开下拉框
            current_sort = None
            for sort_text in ["Best Match", "Newest First", "Lowest Price", "Highest Price"]:
                try:
                    loc = self.page.get_by_text(sort_text, exact=True).first
                    if loc.is_visible(timeout=1000):
                        current_sort = loc
                        self.logger.info(f"✓ 当前排序: {sort_text}")
                        break
                except Exception:
                    continue
            
            if current_sort is None:
                raise RuntimeError("未找到当前排序选项")
            
            current_sort.click()
            self.page.wait_for_timeout(800)
            self.logger.info("✓ 排序下拉框已打开")
            
        except Exception as e:
            self.logger.error(f"打开排序下拉框失败: {e}")
            raise
    
    # ========== 商品卡片 ==========
    
    def get_item_cards_count(self):
        """
        获取页面商品卡片数量
        
        Returns:
            int: 卡片数量
        """
        try:
            # 使用更精确的商品卡片选择器
            cards = self.page.locator('[class*="list-components-item-card"]')
            return cards.count()
        except Exception:
            return 0
    
    def click_first_item_card(self):
        """
        点击第一张商品卡片
        """
        try:
            first_card = self.page.locator('[class*="list-components-item-card"]').first
            first_card.click()
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击商品卡片失败: {e}")
            raise
    
    def hover_item_card(self, index=0):
        """
        鼠标悬停在指定商品卡片
        
        Args:
            index: 卡片索引（0 表示第一张）
        """
        try:
            card = self.page.locator('[class*="list-components-item-card"]').nth(index)
            card.hover()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"Hover 商品卡片失败: {e}")
            raise
    
    def get_item_title(self, index=0):
        """
        获取商品标题
        
        Args:
            index: 卡片索引
        
        Returns:
            str: 商品标题
        """
        try:
            # 商品卡片本身就是 <a> 标签，标题在其内部的 div
            card = self.page.locator('[class*="list-components-item-card"]').nth(index)
            # 标题在 div.details 或 div[class*="title"] 中
            title = card.locator('div[class*="title"], div.details').first
            text = title.inner_text(timeout=5000)
            # details 中可能包含多行文本，取第一行作为标题
            return text.split('\n')[0].strip()
        except Exception as e:
            self.logger.warning(f"获取商品标题失败: {e}")
            return ""
    
    def get_item_price(self, index=0):
        """
        获取商品价格
        
        Args:
            index: 卡片索引
        
        Returns:
            str: 商品价格
        """
        try:
            # 使用更精确的商品卡片选择器
            card = self.page.locator('[class*="list-components-item-card"]').nth(index)
            # 价格在 div.prices 或包含 AED 文本的元素中
            price = card.locator('div.prices, [class*="price"]').first
            return price.inner_text(timeout=5000)
        except Exception as e:
            self.logger.warning(f"获取商品价格失败: {e}")
            return ""
    
    # ========== 收藏功能 ==========
    
    def click_favorite_button(self, index=0):
        """
        点击收藏按钮
        
        Args:
            index: 卡片索引（0 表示第一张）
        """
        try:
            card = self.page.locator('[class*="list-components-item-card"]').nth(index)
            # 收藏按钮是一个带 .list-components-item-favorite 类的 div
            favorite_btn = card.locator('.list-components-item-favorite').first
            favorite_btn.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击收藏按钮失败: {e}")
            raise
    
    def is_item_favorited(self, index=0):
        """
        判断商品是否已收藏
        
        Args:
            index: 卡片索引
        
        Returns:
            bool: True 表示已收藏
        """
        try:
            card = self.page.locator('[class*="list-components-item-card"]').nth(index)
            # 检查收藏图标的 src 属性判断状态
            # 未收藏: unFav.png, 已收藏: fav.png 或类似命名
            favorite_icon = card.locator('.list-components-item-favorite img.favorite-icon').first
            src = favorite_icon.get_attribute('src')
            # 如果src包含 "fav" 但不包含 "unFav"，说明已收藏
            return src and 'fav' in src.lower() and 'unfav' not in src.lower()
        except Exception:
            return False
    
    # ========== 分页功能 ==========
    
    def click_next_page(self):
        """
        点击下一页
        """
        try:
            next_btn = self.page.get_by_role('button', name='Next').first
            if not next_btn.is_visible(timeout=2000):
                # 备选选择器
                next_btn = self.page.locator('button:has-text("下一页"), .pagination .next').first
            
            next_btn.click()
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击下一页失败: {e}")
            raise
    
    def _marketplace_list_url_for_page(self, page_num: int) -> str | None:
        """
        AE Marketplace 列表分页 URL：第1页 .../cate-marketplace/，第N页 .../cate-marketplace-pageN/
        保留原有 query 参数。
        """
        current = self.page.url
        if "cate-marketplace" not in current:
            return None
        if "?" in current:
            path_part, query = current.split("?", 1)
            query_suffix = f"?{query}"
        else:
            path_part, query_suffix = current, ""
        path_clean = path_part.rstrip("/")
        path_clean = re.sub(r"-page\d+$", "", path_clean)
        if page_num <= 1:
            new_path = f"{path_clean}/"
        else:
            new_path = f"{path_clean}-page{page_num}/"
        return new_path + query_suffix

    def goto_page_number(self, page_num):
        """
        跳转到指定页码
        
        Args:
            page_num: 页码数字
        """
        num_str = str(page_num)
        try:
            # 方法1：页码输入框（若存在）
            page_input = self.page.locator('input[type="number"], .page-input').first
            if page_input.is_visible(timeout=2000):
                page_input.fill(num_str)
                page_input.press("Enter")
            else:
                # 方法2：Bootstrap 风格 li.page-item（AE 实测为 li，非 button）
                candidates = self.page.locator(
                    "li.page-item:not(.disabled):not(.ellipsis):not(.prev):not(.next)"
                )
                clicked = False
                try:
                    n = candidates.count()
                except Exception:
                    n = 0
                for i in range(n):
                    li = candidates.nth(i)
                    if not li.is_visible(timeout=500):
                        continue
                    raw = (li.inner_text() or "").strip()
                    first_token = raw.split("\n")[0].strip()
                    if first_token != num_str:
                        continue
                    link = li.locator("a").first
                    if link.is_visible(timeout=800):
                        link.click()
                    else:
                        li.click()
                    clicked = True
                    break

                if not clicked:
                    # 方法3：分页区域内可点击的链接/按钮，文本严格等于页码
                    pag = self.page.locator('[class*="pagination"]').first
                    if pag.is_visible(timeout=1500):
                        exact = pag.get_by_text(num_str, exact=True).first
                        if exact.is_visible(timeout=1500):
                            exact.click()
                            clicked = True

                if not clicked:
                    # 方法4：直接构造列表 URL（与 TC022 的 -page2 路径一致）
                    target = self._marketplace_list_url_for_page(page_num)
                    if target:
                        self.page.goto(target, wait_until="domcontentloaded", timeout=30000)
                    else:
                        raise RuntimeError(
                            f"未找到页码 {page_num} 的可点击元素，且当前 URL 无法构造 Marketplace 分页路径"
                        )

            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"跳转到页码 {page_num} 失败: {e}")
            raise
    
    # ========== 空状态检查 ==========
    
    def is_empty_state_displayed(self):
        """
        判断是否显示空状态（无结果）
        
        Returns:
            bool: True 表示显示空状态
        """
        try:
            # AE站实际文案："We couldn't find anything. Try a new search"
            empty_text = self.page.get_by_text("We couldn't find anything", exact=False).first
            if empty_text.is_visible(timeout=2000):
                return True
            
            # 备选：检查空状态容器
            empty_container = self.page.locator('[class*="empty"]').first
            if empty_container.is_visible(timeout=2000):
                return True
            
            # 再备选：No results found
            no_results = self.page.get_by_text('No results found').first
            return no_results.is_visible(timeout=2000)
        except Exception:
            return False
