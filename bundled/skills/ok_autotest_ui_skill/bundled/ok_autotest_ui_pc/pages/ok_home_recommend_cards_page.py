# pages/ok_home_recommend_cards_page.py
"""纽约首页 Top Picks / Popular in For Sale 推荐横滑区（MCP 录制选择器）"""
import re

from playwright.sync_api import Locator

from pages.base_page import BasePage
from utils.logger import setup_logger


class OkHomeRecommendCardsPage(BasePage):
    """金刚位下方推荐卡片：区头、横滑箭头、卡片跳转、收藏心形（与 MCP Ran Playwright code 一致）"""

    CSS_CAROUSEL_RIGHT = '[class*="Recommend_itemIconRight"]'
    CSS_CAROUSEL_LEFT = '[class*="Recommend_itemIconLeft"]'
    CSS_FAVORITE_BTN = ".list-components-item-favorite"

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    def top_picks_heading(self) -> Locator:
        return self.page.get_by_text("Top Picks", exact=True).first

    def top_picks_carousel_right_arrow(self) -> Locator:
        return self.page.locator(self.CSS_CAROUSEL_RIGHT).first

    def top_picks_carousel_left_arrow(self) -> Locator:
        return self.page.locator(self.CSS_CAROUSEL_LEFT).first

    def popular_for_sale_carousel_right_arrow(self) -> Locator:
        """Popular in For Sale 与 Top Picks 共用类名，取页面中第二组右箭头"""
        return self.page.locator(self.CSS_CAROUSEL_RIGHT).nth(1)

    def popular_for_sale_carousel_left_arrow(self) -> Locator:
        return self.page.locator(self.CSS_CAROUSEL_LEFT).nth(1)

    def wait_top_picks_loaded(self, timeout: int = 40000):
        """等待 Top Picks 区头与首张卡片链接出现"""
        try:
            hdr = self.page.get_by_role(
                "link", name=re.compile(r"Top Picks\s*\|\s*View more", re.I)
            )
            try:
                hdr.wait_for(state="visible", timeout=timeout)
            except Exception:
                self.page.reload(wait_until="domcontentloaded", timeout=60000)
                self.page.wait_for_timeout(2000)
                hdr.wait_for(state="visible", timeout=timeout)
            self.first_top_picks_card_link().wait_for(state="visible", timeout=timeout)
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception as e:
            self.logger.error(f"等待 Top Picks 区域失败: {e}")
            raise

    def top_picks_view_more_link(self) -> Locator:
        # MCP: await page.getByRole('link', { name: 'Top Picks | View more' }).click();
        return self.page.get_by_role("link", name="Top Picks | View more")

    def popular_in_for_sale_view_more_link(self) -> Locator:
        # MCP: getByRole('link', { name: 'Popular in For Sale | View' })（文案在 a11y 树中截断）
        return self.page.get_by_role("link", name=re.compile(r"Popular in For Sale \| View", re.I))

    def click_top_picks_view_more(self):
        try:
            self.top_picks_view_more_link().click()
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception as e:
            self.logger.error(f"点击 Top Picks View more 失败: {e}")
            raise

    def click_top_picks_view_more_middle(self):
        """中键点击 View more（Chromium 常新开后台标签；见测试内归一到当前标签逻辑）"""
        try:
            self.top_picks_view_more_link().click(button="middle")
            self.page.wait_for_timeout(800)
        except Exception as e:
            self.logger.error(f"中键点击 Top Picks View more 失败: {e}")
            raise

    def click_top_picks_carousel_right_first(self):
        # MCP run_code: page.locator('[class*="Recommend_itemIconRight"]').first().click()
        try:
            self.page.locator(self.CSS_CAROUSEL_RIGHT).first.click(timeout=20000)
            self.page.wait_for_timeout(600)
        except Exception as e:
            self.logger.error(f"点击 Top Picks 右箭头失败: {e}")
            raise

    def click_top_picks_carousel_left_first(self):
        try:
            self.page.locator(self.CSS_CAROUSEL_LEFT).first.click(timeout=20000)
            self.page.wait_for_timeout(600)
        except Exception as e:
            self.logger.error(f"点击 Top Picks 左箭头失败: {e}")
            raise

    def top_picks_cate_card_links(self) -> Locator:
        """Top Picks 横滑区内所有类目详情卡片链接（与 first 同源 xpath）"""
        vm = self.top_picks_view_more_link()
        return vm.locator('xpath=../following-sibling::*//a[contains(@href,"/cate-")]')

    def first_top_picks_card_link(self) -> Locator:
        """
        MCP run_code：View more 同块的 following 兄弟内首张帖子详情链
        await vm.locator('xpath=../following-sibling::*//a[contains(@href,"/cate-")]').first()
        """
        try:
            return self.top_picks_cate_card_links().first
        except Exception as e:
            self.logger.error(f"定位 Top Picks 首张卡片失败: {e}")
            raise

    def card_has_title_truncation_ui(self, card: Locator) -> bool:
        """
        单张推荐卡内是否存在长标题的截断/省略表现（div 以外如 span/p 亦扫描；含 line-clamp）。
        """
        try:
            return bool(
                card.evaluate(
                    """(el) => {
                        const MIN_LEN = 16;
                        const it = (el.innerText || '');
                        if (/\\u2026/.test(it)) return true;
                        const nodes = [el, ...el.querySelectorAll('*')];
                        for (const node of nodes) {
                            if (node.nodeType !== 1) continue;
                            const raw = (node.textContent || '').replace(/\\s+/g, ' ').trim();
                            if (raw.length < MIN_LEN) continue;
                            const st = getComputedStyle(node);
                            const wlc = st.getPropertyValue('-webkit-line-clamp');
                            if (wlc && wlc !== 'none' && parseInt(wlc, 10) > 0) return true;
                            if (st.textOverflow === 'ellipsis' || st.textOverflow === 'clip') {
                                return true;
                            }
                            if (st.whiteSpace === 'nowrap' && st.textOverflow === 'ellipsis') {
                                return true;
                            }
                            if (node.scrollWidth > node.clientWidth + 2) return true;
                            const ox = st.overflowX;
                            const oy = st.overflowY;
                            if (raw.length >= 24 && (ox === 'hidden' || oy === 'hidden')) {
                                if (st.textOverflow === 'ellipsis' || st.textOverflow === 'clip') {
                                    return true;
                                }
                            }
                        }
                        return false;
                    }"""
                )
            )
        except Exception as e:
            self.logger.error(f"检测卡片标题截断失败: {e}")
            raise

    def first_top_picks_favorite(self) -> Locator:
        """首张 Top Picks 卡片上的收藏按钮（避免整页 .first 误点心形）"""
        try:
            return self.first_top_picks_card_link().locator(self.CSS_FAVORITE_BTN).first
        except Exception as e:
            self.logger.error(f"定位 Top Picks 首张收藏按钮失败: {e}")
            raise

    def click_first_top_picks_favorite(self):
        # MCP: page.locator('.list-components-item-favorite').first().click()
        try:
            self.first_top_picks_favorite().click(timeout=15000)
        except Exception as e:
            self.logger.error(f"点击首张卡片收藏失败: {e}")
            raise

    def favorite_icon_fingerprint(self, fav: Locator) -> str:
        """用于断言收藏态变化（整段 outerHTML，避免 class/fill 未变导致假阴性）"""
        try:
            return fav.evaluate("(el) => el.outerHTML || ''")
        except Exception as e:
            self.logger.error(f"读取收藏图标指纹失败: {e}")
            raise

    def favorite_dom_token(self, fav: Locator) -> str:
        """收藏按钮 DOM 态：class、aria、img.src、父链上含 favorite/active 的 class（图标资源未变时仍可能切换态）"""
        try:
            return fav.evaluate(
                """(el) => {
                    const img = el.querySelector('img');
                    const chain = [];
                    let p = el;
                    for (let i = 0; i < 6 && p; i++) {
                        chain.push((p.className || '').toString());
                        p = p.parentElement;
                    }
                    return [
                        el.className || '',
                        el.getAttribute('aria-pressed') || '',
                        el.getAttribute('data-active') || '',
                        img ? img.src : '',
                        img ? (img.className || '') : '',
                        chain.join('>'),
                    ].join('|');
                }"""
            )
        except Exception as e:
            self.logger.error(f"读取收藏 DOM token 失败: {e}")
            raise

    def favorite_img_compute_token(self, fav: Locator) -> str:
        """心形 img 的计算样式（同 src 时可能用 filter/opacity 区分空心/实心）"""
        try:
            return fav.evaluate(
                """(el) => {
                    const img = el.querySelector('img');
                    if (!img) return '';
                    const s = getComputedStyle(img);
                    return [s.filter, s.opacity, s.transform, s.color].join('|');
                }"""
            )
        except Exception as e:
            self.logger.error(f"读取收藏图标计算样式失败: {e}")
            raise

    def top_picks_card_link_by_href_contains(self, href_part: str) -> Locator:
        """
        在 Top Picks 横滑区内按 href 片段定位卡片链接。
        注意：top_picks_cate_card_links() 已是 a 节点，不可再 .locator('a[...]')（会找子级 a，永远匹配不到）。
        """
        try:
            safe = (href_part or "").replace('"', '\\"')
            vm = self.top_picks_view_more_link()
            return vm.locator(
                "xpath=../following-sibling::*//a[contains(@href,\"/cate-\") "
                f"and contains(@href,\"{safe}\")]"
            )
        except Exception as e:
            self.logger.error(f"按 href 片段定位 Top Picks 卡片失败: {e}")
            raise

    def scroll_top_picks_card_into_view_by_href(self, href_part: str, max_steps: int = 14) -> Locator:
        """横滑轮播直至含指定 href 的卡片出现在区链接集合中并尽量可见"""
        try:
            self.wait_top_picks_loaded()
            for _ in range(max_steps):
                raw = self.top_picks_card_link_by_href_contains(href_part)
                try:
                    if raw.count() > 0:
                        c = raw.first
                        c.wait_for(state="visible", timeout=2500)
                        c.scroll_into_view_if_needed(timeout=5000)
                        return c
                except Exception:
                    pass
                self.click_top_picks_carousel_right_first()
                self.page.wait_for_timeout(450)
            return self.top_picks_card_link_by_href_contains(href_part).first
        except Exception as e:
            self.logger.error(f"横滑查找 Top Picks 卡片失败: {e}")
            raise

    def scroll_top_picks_card_into_view_by_href_candidates(
        self, href_parts: list, max_steps: int = 14
    ) -> Locator:
        """依次尝试多个 href 片段（编码/解码/帖子 ID 不一致时），横滑直至匹配到可见卡片"""
        try:
            seen = []
            for p in href_parts:
                if not p or p in seen:
                    continue
                seen.append(p)
                try:
                    # 每个候选前重置页面，避免上一轮横滑把起点移到末尾导致后续片段永远匹配不到
                    self.page.reload(wait_until="domcontentloaded", timeout=60000)
                    self.page.wait_for_timeout(500)
                    c = self.scroll_top_picks_card_into_view_by_href(str(p), max_steps=max_steps)
                    c.wait_for(state="visible", timeout=10000)
                    return c
                except Exception:
                    continue
            raise RuntimeError(f"横滑后仍未匹配到 Top Picks 卡片: {href_parts!r}")
        except Exception as e:
            self.logger.error(f"多候选横滑查找 Top Picks 卡片失败: {e}")
            raise

    def click_popular_in_for_sale_view_more(self):
        try:
            self.popular_in_for_sale_view_more_link().click()
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception as e:
            self.logger.error(f"点击 Popular in For Sale View more 失败: {e}")
            raise

    def scroll_popular_in_for_sale_into_view(self):
        try:
            self.popular_in_for_sale_view_more_link().scroll_into_view_if_needed(timeout=15000)
            self.page.wait_for_timeout(400)
        except Exception as e:
            self.logger.error(f"滚动 Popular in For Sale 失败: {e}")
            raise

    def first_top_picks_card_snippet(self) -> str:
        """首张卡片可见文案摘要（用于横滑前后对比）"""
        try:
            return (self.first_top_picks_card_link().inner_text() or "").strip()[:220]
        except Exception as e:
            self.logger.error(f"读取首张卡片摘要失败: {e}")
            raise

    def top_picks_carousel_scroll_left(self) -> int:
        """
        Top Picks 横滑位移：优先 scrollLeft，否则取 transform translateX（与实测横滑只改位移、不改 DOM 顺序一致）。
        """
        try:
            v = self.page.evaluate(
                """() => {
                    function readOffset(el) {
                        if (!el) return null;
                        if (el.scrollLeft > 2) return el.scrollLeft;
                        const t = getComputedStyle(el).transform;
                        if (t && t !== 'none') {
                            const m = t.match(/matrix\\(([^)]+)\\)/);
                            if (m) {
                                const p = m[1].split(',').map(s => parseFloat(s.trim()));
                                if (p.length >= 6 && Math.abs(p[4]) > 1) return p[4];
                            }
                        }
                        return null;
                    }
                    const all = [...document.querySelectorAll('a')];
                    const vm = all.find(a => {
                        const t = (a.innerText || '');
                        return t.includes('Top Picks') && t.includes('View more');
                    });
                    if (!vm) return -1;
                    let n = vm.closest('div');
                    for (let d = 0; d < 14 && n; d++) {
                        const cardLinks = [...n.querySelectorAll('a')].filter(
                            x => /\\/cate-/.test(x.getAttribute('href') || '')
                        );
                        if (cardLinks.length >= 2) {
                            const cand = [n, n.firstElementChild, ...n.querySelectorAll('div')];
                            for (const el of cand) {
                                const o = readOffset(el);
                                if (o !== null) return Math.round(o);
                            }
                            let p = n;
                            while (p) {
                                if (p.scrollWidth > p.clientWidth + 6) {
                                    const o = readOffset(p);
                                    if (o !== null) return Math.round(o);
                                }
                                p = p.parentElement;
                            }
                        }
                        n = n.parentElement;
                    }
                    return -2;
                }"""
            )
            return int(v)
        except Exception as e:
            self.logger.error(f"读取 Top Picks 横滑 scrollLeft 失败: {e}")
            raise

    def click_locator_at_fraction(self, loc: Locator, x_ratio: float, y_ratio: float):
        """在定位器包围盒内按比例点击（标题区 / 价格区，避免写死帖子标题）"""
        try:
            try:
                loc.scroll_into_view_if_needed(timeout=8000)
            except Exception:
                pass
            box = loc.bounding_box()
            if not box:
                raise RuntimeError("bounding_box 为空")
            self.page.mouse.click(
                box["x"] + box["width"] * x_ratio,
                box["y"] + box["height"] * y_ratio,
            )
            self.page.wait_for_timeout(400)
        except Exception as e:
            self.logger.error(f"比例点击失败: {e}")
            raise

    def read_list_card_price_line(self, card: Locator) -> str:
        """从列表卡片文案中提取价格相关一行（动态卡片）"""
        try:
            text = card.inner_text() or ""
            for line in reversed([ln.strip() for ln in text.splitlines() if ln.strip()]):
                if re.search(r"(\$|Free|/hour|Monthly|/year|/day)", line, re.I):
                    return line
            return ""
        except Exception as e:
            self.logger.error(f"解析列表卡价格文案失败: {e}")
            raise

    def read_detail_hero_price_text(self) -> str:
        """详情页主价格区首行（与 MCP 快照中 h1 同块的 $ 文案一致）"""
        try:
            return self.page.evaluate(
                """() => {
                    const h = document.querySelector('h1');
                    if (!h) return '';
                    let block = h.parentElement;
                    for (let i = 0; i < 8 && block; i++) {
                        const lines = (block.innerText || '').split(/\\n/).map(s => s.trim()).filter(Boolean);
                        for (const line of lines) {
                            if (line.length < 120 && /\\$|Free|\\/hour|Monthly|year|day/i.test(line)) {
                                return line;
                            }
                        }
                        block = block.parentElement;
                    }
                    return '';
                }"""
            )
        except Exception as e:
            self.logger.error(f"读取详情主价格失败: {e}")
            raise

    def is_top_picks_below_kingkong(self) -> bool:
        """Top Picks 区头是否在金刚位容器下方（纵向顺序）"""
        try:
            return self.page.evaluate(
                """() => {
                    const kk = document.querySelector('a[href*="iconSource=marketplace"]');
                    const tp = Array.from(document.querySelectorAll('a')).find(
                        a => a.textContent && a.textContent.includes('Top Picks')
                            && a.textContent.includes('View more'));
                    if (!kk || !tp) return false;
                    const r1 = kk.getBoundingClientRect();
                    const r2 = tp.getBoundingClientRect();
                    return r2.top >= r1.bottom - 4;
                }"""
            )
        except Exception as e:
            self.logger.error(f"判断 Top Picks 相对金刚位位置失败: {e}")
            raise
