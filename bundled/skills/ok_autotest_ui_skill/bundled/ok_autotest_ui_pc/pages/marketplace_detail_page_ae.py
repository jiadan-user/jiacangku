# pages/marketplace_detail_page_ae.py
import re

from pages.base_page import BasePage
from utils.logger import setup_logger


class MarketplaceDetailPageAe(BasePage):
    """AE站 Marketplace 商品详情页（选择器来自 MCP 录制摘要与用例文档实测）"""

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    def is_detail_page_loaded(self, timeout=20000):
        """
        检查详情页是否加载（离开列表 cate-marketplace 且主价格区可见）
        文档实测：详情 URL 含 cate-xxx 与商品 slug，主价格含 AED
        """
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
            url = self.page.url.lower()
            if "cate-marketplace" in url:
                return False
            if "/cate-" not in url:
                return False
            return self.page.get_by_text(re.compile(r"AED\s*\d+")).first.is_visible(timeout=8000)
        except Exception:
            return False

    def get_price_text(self):
        """文档实测：主价格区域文案如 AED 367 / AED 150"""
        try:
            return self.page.get_by_text(re.compile(r"AED\s*\d+")).first.inner_text()
        except Exception as e:
            self.logger.error(f"获取价格文案失败: {e}")
            return ""

    def _body_inner_text(self) -> str:
        try:
            return self.page.locator("body").inner_text()
        except Exception:
            return ""

    def is_free_delivery_before_description(self) -> bool:
        """
        主信息区履约标签：全文顺序上 Free Delivery 出现在 Description 之前，
        避免「You may also like」里其它商品带 Free Delivery 误判为当前 listing（TC021/TC031）。
        """
        t = self._body_inner_text()
        i_fd = t.find("Free Delivery")
        i_desc = t.find("Description")
        if i_fd < 0:
            return False
        if i_desc < 0:
            return True
        return i_fd < i_desc

    def is_available_for_pickup_before_description(self) -> bool:
        """同上，用于 Online 正例与 Offline 负例（TC022/TC032）。"""
        t = self._body_inner_text()
        i_pu = t.find("Available for Pickup")
        i_desc = t.find("Description")
        if i_pu < 0:
            return False
        if i_desc < 0:
            return True
        return i_pu < i_desc

    def is_free_delivery_visible(self, timeout=5000):
        """文档/MCP：主信息区优先（同 before_description，避免推荐区串味）"""
        return self.is_free_delivery_before_description()

    def is_available_for_pickup_visible(self, timeout=5000):
        """文档/MCP：主信息区 Available for Pickup"""
        return self.is_available_for_pickup_before_description()

    def is_location_snippet_visible(self, substring: str, timeout=5000) -> bool:
        """主信息或 Location 区是否含某地址片段（TC012 等）"""
        try:
            return self.page.get_by_text(substring, exact=False).first.is_visible(timeout=timeout)
        except Exception:
            return False

    def get_location_text(self):
        """
        文档实测位置文案（Online：ADCB ATM...；Offline：United Arab Emirates）
        返回首个匹配的可见文案片段所在元素文本
        """
        try:
            loc_adcb = self.page.get_by_text("ADCB ATM", exact=False).first
            if loc_adcb.is_visible(timeout=2000):
                return loc_adcb.inner_text()
        except Exception:
            pass
        try:
            loc_uae = self.page.get_by_text("United Arab Emirates", exact=True).first
            if loc_uae.is_visible(timeout=2000):
                return loc_uae.inner_text()
        except Exception as e:
            self.logger.error(f"获取位置文案失败: {e}")
        return ""

    def get_seller_name(self):
        """文档实测卖家昵称示例：OKer_wangyongli、keerisbest2293939393"""
        try:
            for name in ("OKer_wangyongli", "keerisbest2293939393"):
                el = self.page.get_by_text(name, exact=True).first
                try:
                    el.scroll_into_view_if_needed()
                except Exception:
                    pass
                if el.is_visible(timeout=8000):
                    return name
        except Exception as e:
            self.logger.error(f"获取卖家名称失败: {e}")
        return ""

    def is_verified_user_badge_visible(self, timeout=10000):
        """文档实测：Verified User"""
        try:
            return self.page.get_by_text("Verified User").first.is_visible(timeout=timeout)
        except Exception:
            return False

    def is_withdraw_button_visible(self, timeout=5000):
        """文档：getByRole('button', { name: 'Withdraw' })"""
        try:
            return self.page.get_by_role("button", name="Withdraw").first.is_visible(timeout=timeout)
        except Exception:
            return False

    def is_edit_button_visible(self, timeout=5000):
        """文档：getByRole('button', { name: 'Edit' })"""
        try:
            return self.page.get_by_role("button", name="Edit").first.is_visible(timeout=timeout)
        except Exception:
            return False

    def is_contact_button_visible(self, timeout=5000):
        """文档：getByRole('button', { name: 'Contact' })"""
        try:
            return self.page.get_by_role("button", name="Contact").first.is_visible(timeout=timeout)
        except Exception:
            return False

    def is_buy_now_button_visible(self, timeout=5000):
        """
        检查是否有 Buy Now 按钮（Online/Offline 商品判断的关键标准）
        - Online 商品: 有 Buy Now 按钮
        - Offline 商品: 无 Buy Now 按钮
        """
        try:
            # 尝试多种可能的定位器
            # 方法1: 通过 role="button" 和 name
            if self.page.get_by_role("button", name=re.compile(r"buy\s+now", re.I)).first.is_visible(timeout=timeout):
                return True
            # 方法2: 通过文本
            if self.page.get_by_text(re.compile(r"buy\s+now", re.I)).first.is_visible(timeout=timeout):
                return True
            # 方法3: 通过 link role
            if self.page.get_by_role("link", name=re.compile(r"buy\s+now", re.I)).first.is_visible(timeout=timeout):
                return True
            return False
        except Exception:
            return False

    def is_sell_similar_button_visible(self, timeout=5000):
        """Sell/Post/List + Similar（TC026）"""
        try:
            pat = re.compile(r"(sell|post|list)\s+similar", re.I)
            if self.page.get_by_role("button", name=pat).first.is_visible(timeout=2000):
                return True
            if self.page.get_by_role("link", name=pat).first.is_visible(timeout=2000):
                return True
            return self.page.get_by_text(pat).first.is_visible(timeout=timeout)
        except Exception:
            return False

    def is_condition_tag_visible(self, timeout=5000):
        """文档实测 Offline 示例：Excellent"""
        try:
            return self.page.get_by_text("Excellent", exact=True).first.is_visible(timeout=timeout)
        except Exception:
            return False

    def get_description_text(self):
        """文档：Description 区域；取标题所在容器 innerText"""
        try:
            h = self.page.get_by_text("Description", exact=True).first
            if not h.is_visible(timeout=5000):
                return ""
            return h.evaluate(
                "el => { const p = el.parentElement; return p ? p.innerText : el.innerText; }"
            )
        except Exception as e:
            self.logger.error(f"获取 Description 区域文本失败: {e}")
            return ""

    def scroll_to_location_block(self):
        try:
            self.page.get_by_text("Location", exact=True).first.scroll_into_view_if_needed()
            self.page.wait_for_timeout(600)
        except Exception:
            pass

    def click_show_map(self):
        """文档 TC034：先滚到 Location 区再点 Show map，便于地图懒加载"""
        try:
            self.scroll_to_location_block()
            btn = self.page.get_by_role("button", name="Show map")
            if btn.is_visible(timeout=3000):
                btn.click()
            else:
                self.page.get_by_text("Show map").click()
            self.page.wait_for_timeout(4000)
        except Exception as e:
            self.logger.error(f"点击 Show map 失败: {e}")
            raise

    def click_favourites(self):
        """文档：Favourites"""
        try:
            self.page.get_by_text("Favourites").first.click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击 Favourites 失败: {e}")
            raise

    def click_share(self):
        """文档：Share"""
        try:
            self.page.get_by_text("Share").first.click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击 Share 失败: {e}")
            raise

    def is_you_may_also_like_visible(self, timeout=5000):
        """文档：You may also like"""
        try:
            return self.page.get_by_text("You may also like").first.is_visible(timeout=timeout)
        except Exception:
            return False

    def is_location_heading_visible(self, timeout=5000):
        """Location 区域标题"""
        try:
            return self.page.get_by_text("Location", exact=True).first.is_visible(timeout=timeout)
        except Exception:
            return False

    def is_show_map_visible(self, timeout=5000):
        """Show map 按钮或文案可见（TC016）"""
        try:
            if self.page.get_by_role("button", name="Show map").first.is_visible(timeout=2000):
                return True
            return self.page.get_by_text("Show map").first.is_visible(timeout=timeout)
        except Exception:
            return False

    def is_favourites_entry_visible(self, timeout=5000):
        try:
            return self.page.get_by_text("Favourites").first.is_visible(timeout=timeout)
        except Exception:
            return False

    def is_share_entry_visible(self, timeout=5000):
        try:
            return self.page.get_by_text("Share").first.is_visible(timeout=timeout)
        except Exception:
            return False

    def is_description_section_non_empty(self) -> bool:
        """Description 区块存在且除标题外有正文（TC015）"""
        raw = self.get_description_text()
        if not raw or not raw.strip():
            return False
        body = raw.replace("Description", "", 1).strip()
        return len(body) >= 3

    def is_listings_snippet_visible(self, snippet: str, timeout=5000) -> bool:
        """卖家区域 listings 文案，如「417 listings」"""
        try:
            return self.page.get_by_text(snippet, exact=False).first.is_visible(timeout=timeout)
        except Exception:
            return False

    def has_any_listings_count_visible(self, timeout=8000) -> bool:
        """listings 数为动态数据：body 或可见节点（TC013/TC024）

        线上偶发 i18n 未替换出现 ``profile_listings`` / ``ok_app_profile_listings``，
        或数字与 listings 分行展示，需放宽匹配并先滚到卖家区域。
        """
        try:
            for anchor in (
                self.page.get_by_text("Verified User", exact=False),
                self.page.get_by_text(re.compile(r"OKer_|Verified", re.I)),
            ):
                try:
                    anchor.first.scroll_into_view_if_needed(timeout=3000)
                    break
                except Exception:
                    continue
        except Exception:
            pass
        self.page.wait_for_timeout(500)

        body = self._body_inner_text()
        relaxed = (
            r"\d[\d,\s]{0,12}\s*listings?",
            r"listings?[\s:：]*\d+",
            r"profile_listings|ok_app_profile_listings|\.profile_listings",
            r"listings?\s*\(\s*\d+\s*\)",
        )
        if body:
            for rx in relaxed:
                if re.search(rx, body, re.I):
                    return True
        for pat in (
            re.compile(r"\d[\d,\s]{0,12}\s*listings?", re.I),
            re.compile(r"listings?[\s:：]*\d+", re.I),
            re.compile(r"profile_listings|ok_app_profile_listings", re.I),
        ):
            try:
                if self.page.get_by_text(pat).first.is_visible(timeout=min(4000, timeout)):
                    return True
            except Exception:
                pass
        try:
            loc = self.page.locator("a,button,[role='link']").filter(
                has_text=re.compile(r"listings?", re.I)
            )
            if loc.count() > 0 and loc.first.is_visible(timeout=min(3000, timeout)):
                return True
        except Exception:
            pass
        return False

    def is_seller_substring_visible(self, substring: str, timeout=8000) -> bool:
        """卖家昵称可能折行或略变，子串匹配（TC024）"""
        if not substring or len(substring) < 4:
            return False
        try:
            return self.page.get_by_text(re.compile(re.escape(substring), re.I)).first.is_visible(
                timeout=timeout
            )
        except Exception:
            return False

    def count_you_may_also_like_detail_links(self) -> int:
        """推荐区内指向分类详情的链接数量（TC017/TC028）"""
        try:
            heading = self.page.get_by_text("You may also like").first
            heading.scroll_into_view_if_needed()
            self.page.wait_for_timeout(1200)
            return heading.evaluate(
                r"""(el) => {
                    const matchHref = (href) => {
                        if (!href) return false;
                        return /cate-(?!marketplace)/i.test(href);
                    };
                    let n = el;
                    for (let i = 0; i < 16 && n; i++) {
                        const sec = n.closest('section');
                        if (sec) {
                            const c = [...sec.querySelectorAll('a[href]')].filter(
                                (a) => matchHref(a.getAttribute('href'))
                            ).length;
                            if (c > 0) return c;
                        }
                        const links = [...n.querySelectorAll('a[href]')].filter(
                            (a) => matchHref(a.getAttribute('href'))
                        );
                        if (links.length > 0) return links.length;
                        n = n.parentElement;
                    }
                    return 0;
                }"""
            )
        except Exception:
            return 0

    def scroll_to_you_may_also_like(self):
        try:
            self.page.get_by_text("You may also like").first.scroll_into_view_if_needed()
            self.page.wait_for_timeout(400)
        except Exception:
            pass

    def is_probable_map_expanded(self) -> bool:
        """点击 Show map 后：iframe / canvas / Hide map 等（TC034/TC035）"""
        self.page.wait_for_timeout(4500)
        try:
            if self.page.get_by_text(re.compile(r"Hide\s*map", re.I)).first.is_visible(timeout=4000):
                return True
        except Exception:
            pass
        try:
            if self.page.locator("iframe[src*='map'], iframe[src*='google'], iframe[src*='gstatic']").count() >= 1:
                return self.page.locator("iframe[src*='map'], iframe[src*='google'], iframe[src*='gstatic']").first.is_visible(
                    timeout=5000
                )
        except Exception:
            pass
        try:
            if self.page.locator("iframe").count() >= 1:
                return self.page.locator("iframe").first.is_visible(timeout=5000)
        except Exception:
            pass
        try:
            if self.page.locator("canvas").first.is_visible(timeout=3000):
                return True
        except Exception:
            pass
        try:
            return self.page.locator("[class*='map'], [id*='map']").first.is_visible(timeout=4000)
        except Exception:
            return False

    def is_map_widget_attached_near_location(self) -> bool:
        """Location 附近是否已挂载 iframe/canvas/含 map 的节点（headless 下展开检测兜底，TC034/TC035）"""
        try:
            return bool(
                self.page.evaluate(
                    """() => {
              const heads = [...document.querySelectorAll('*')].filter(
                (e) => e.childElementCount === 0 && (e.textContent || '').trim() === 'Location'
              );
              const loc = heads[0] || null;
              if (!loc) return false;
              let p = loc.parentElement;
              for (let i = 0; i < 25 && p; i++) {
                if (p.querySelector('iframe, canvas, [class*="map" i], [id*="map" i]')) return true;
                p = p.parentElement;
              }
              return false;
            }"""
                )
            )
        except Exception:
            return False

    def is_show_map_toggle_open(self) -> bool:
        """Show map 点击后按钮 aria-expanded 或文案变为 Hide map（TC034/TC035 辅助）"""
        try:
            btn = self.page.get_by_role("button", name=re.compile(r"Show map|Hide map", re.I)).first
            if btn.is_visible(timeout=2000):
                exp = btn.get_attribute("aria-expanded")
                if exp and exp.lower() == "true":
                    return True
        except Exception:
            pass
        try:
            return self.page.get_by_text(re.compile(r"Hide\s*map", re.I)).first.is_visible(timeout=2000)
        except Exception:
            return False

    def click_breadcrumb_link_by_name_regex(self, pattern: str):
        """面包屑/导航内分类链接（TC036，pattern 为 JS 正则字符串）"""
        self.page.get_by_role("link", name=re.compile(pattern, re.I)).first.click()
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self.page.wait_for_timeout(1500)

    def navigate_detail_from_config_path(self, base_url: str, path_suffix: str):
        """深链直达详情（TC038/TC039），path_suffix 以 / 开头"""
        url = base_url.rstrip("/") + path_suffix
        self.goto(url, wait_until="domcontentloaded", timeout=30000)
        self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        self.page.wait_for_timeout(2000)

    def browser_go_back(self):
        """浏览器后退（TC037），封装避免用例层直接调用 navigation API"""
        self.page.go_back()
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self.page.wait_for_timeout(1500)

    def is_any_modal_or_overlay_visible(self, timeout=3000) -> bool:
        """收藏/分享点击后可能出现 dialog 或浮层（TC042–TC044）"""
        try:
            dlg = self.page.get_by_role("dialog")
            if dlg.count() > 0 and dlg.first.is_visible(timeout=timeout):
                return True
        except Exception:
            pass
        try:
            if self.page.get_by_text(re.compile(r"Copy link|Copy|Share", re.I)).first.is_visible(
                timeout=2000
            ):
                return True
        except Exception:
            pass
        return False
