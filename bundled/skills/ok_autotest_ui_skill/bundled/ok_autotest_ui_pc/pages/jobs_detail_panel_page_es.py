"""
ES站 Jobs列表页 详情面板 Page Object
专门用于ES站（西班牙站）招聘列表页右侧详情面板的内容展示与操作功能测试

页面URL: https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs
包含功能:
  - 点击列表卡片加载详情面板
  - 详情面板信息验证（标题/薪资/公司/职位标签/Description）
  - 本人帖操作：Withdraw / Edit（包括Withdraw确认弹窗）
  - 非本人帖操作：Contact（已登录跳转聊天页；未登录弹出登录引导弹窗）
  - 通用操作：Favourites / New tab / Share
  - 操作后 toast 验证
  - 操作跳转 URL 验证
  - 未登录场景：clearCookies 模拟，验证按钮权限隔离

录制依据: MCP Playwright 浏览器录制（2026-03-20 全量重录）
"""

import re

from pages.base_page import BasePage
from utils.logger import setup_logger


class JobsDetailPanelPageES(BasePage):
    """
    ES站职位列表页 - 详情面板操作 Page Object
    URL: https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs
    """

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    # ==================== 导航 ====================

    def navigate_to_jobs_list(self, base_url: str):
        """导航到ES站招聘列表页"""
        try:
            target_url = f"{base_url}/en/city-madrid2/cate-jobs/?iconSource=jobs"
            self.page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
            try:
                self.page.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                pass
            try:
                self.page.wait_for_selector(
                    '[class*="list-components-item-job-card"], '
                    '[class*="JobCard"], [class*="job-card"]',
                    timeout=25000,
                )
            except Exception:
                pass
        except Exception as e:
            self.logger.error(f"导航到ES站招聘列表页失败: {e}")
            raise

    def navigate_to_jobs_list_without_login(self, base_url: str):
        """清除Cookie后导航到ES站招聘列表页（模拟未登录状态）"""
        try:
            self.page.context.clear_cookies()
            target_url = f"{base_url}/en/city-madrid2/cate-jobs/?iconSource=jobs"
            self.page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
            try:
                self.page.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                pass
            # 处理 Cookie 同意弹窗
            self._handle_cookie_consent_if_present()
        except Exception as e:
            self.logger.error(f"未登录状态导航失败: {e}")
            raise

    def _handle_cookie_consent_if_present(self):
        """处理页面 Cookie 同意弹窗（如果存在）"""
        try:
            only_essential = self.page.get_by_role("button", name="Only essential")
            if only_essential.is_visible(timeout=4000):
                only_essential.click()
                self.page.wait_for_timeout(1000)
                return
        except Exception:
            pass
        try:
            accept_all = self.page.get_by_role("button", name="Accept all")
            if accept_all.is_visible(timeout=2000):
                accept_all.click()
                self.page.wait_for_timeout(1000)
        except Exception:
            pass

    # ==================== 卡片点击 ====================

    def click_card_by_info_id(self, info_id: str, *, title_fallback: str = ""):
        """
        通过帖子 InfoID 点击左侧列表卡片（href 中含 infoId，不受标题文案变更影响）

        若列表链接已改为仅含内部长数字 id、不含 im infoId，可传 ``title_fallback`` 用标题回退点击。

        Args:
            info_id: 帖子 InfoID（如非本人帖 6504835552588510）
            title_fallback: 可选，本人帖标题关键词，用于在 href 中找不到 infoId 时点击
        """
        try:
            scoped = self.page.locator(
                f'[class*="list-components-item-job-card"] a[href*="{info_id}"]'
            )
            if scoped.count() == 0:
                scoped = self.page.locator(f'a[href*="{info_id}"]')
            if scoped.count() == 0 and title_fallback:
                self.logger.info(
                    "列表 href 中未出现 infoId=%s，尝试按标题回退: %s",
                    info_id,
                    title_fallback[:80],
                )
                self.click_card_by_text(title_fallback)
                return
            link = scoped.first
            link.wait_for(state="visible", timeout=20000)
            link.scroll_into_view_if_needed()
            link.click(timeout=30000)
            self.page.wait_for_timeout(1500)
        except Exception as e:
            if title_fallback:
                self.logger.warning(
                    "通过 infoId 点击失败: %s，尝试标题回退: %s", e, title_fallback[:80]
                )
                try:
                    self.click_card_by_text(title_fallback)
                    return
                except Exception as e2:
                    self.logger.error("标题回退也失败: %s", e2)
            self.logger.error(f"通过 infoId={info_id} 点击列表卡片失败: {e}")
            raise

    def click_first_non_own_job_card(self, own_post_info_id: str) -> str:
        """
        点击左侧列表中第一条「非本人」职位卡片。

        固定 infoId 的帖子可能已下架或不在当前城市列表，因此用「排除本人帖 id」方式选取，
        避免强依赖历史种子数据仍挂在列表上。

        Args:
            own_post_info_id: 本人帖 InfoID，含该 id 的卡片会跳过

        Returns:
            从卡片 DOM 解析到的帖子 InfoID（若无法解析则为空字符串，可再调用 get_detail_info_id_from_new_tab_href）
        """
        try:
            # 列表异步渲染：滚动触发懒加载，并兼容类名变更
            for _ in range(4):
                try:
                    self.page.evaluate(
                        "() => window.scrollBy(0, Math.min(800, "
                        "document.body.scrollHeight - window.scrollY))"
                    )
                except Exception:
                    pass
                self.page.wait_for_timeout(400)
            # 不依赖 cate-jobs 路径；优先从列表卡片行点击，避免单条 a[href] 与站点路由改版不一致
            try:
                self.page.wait_for_selector(
                    "[class*='list-components-item-job-card'], [class*='JobCard'], "
                    "[class*='job-card']",
                    timeout=30000,
                )
            except Exception:
                pass
            try:
                n_cards = self.page.locator(
                    "[class*='list-components-item-job-card']"
                ).count()
                if n_cards:
                    for i in range(min(n_cards, 40)):
                        card = self.page.locator(
                            "[class*='list-components-item-job-card']"
                        ).nth(i)
                        try:
                            txt = (card.inner_text(timeout=2000) or "")
                            html = card.evaluate("el => el.innerHTML || ''")
                        except Exception:
                            continue
                        blob = f"{txt}\n{html}"
                        if own_post_info_id in blob:
                            continue
                        m = re.search(
                            r"-(\d{12,})(?:[\"'/]|$)", blob, re.S
                        )
                        info_id = m.group(1) if m else ""
                        if not info_id:
                            try:
                                card.scroll_into_view_if_needed()
                                card.click(timeout=15000)
                                self.page.wait_for_timeout(1500)
                                if self._detail_panel_shows_non_own_post():
                                    return ""
                            except Exception:
                                continue
                            continue
                        try:
                            card.scroll_into_view_if_needed()
                            card.click(timeout=15000)
                        except Exception:
                            al = card.locator("a[href]")
                            if al.count() > 0:
                                al.first.click(timeout=15000)
                            else:
                                continue
                        self.page.wait_for_timeout(1500)
                        if self._detail_panel_shows_non_own_post():
                            return info_id
                        self.logger.info(
                            "本列表项点击后仍非 Contact 态（可能仍为本人帖或加载中），尝试下一条"
                        )
            except Exception as e:
                self.logger.debug("按列表卡片行点击非本人帖失败: %s", e)
            # JS：任意主区链接，含长数字 id 且非本人
            try:
                clicked_id = self.page.evaluate(
                    r"""(ownId) => {
                      const links = [...document.querySelectorAll('main a[href], a[href*="/city"], a[href*="/cate"]')];
                      for (const a of links) {
                        const href = a.getAttribute('href') || '';
                        if (!href || href.includes(ownId)) continue;
                        const idm = href.match(/-(\d{12,})(?:/|\?|#|$)/);
                        if (!idm) continue;
                        if (href.length < 28) continue;
                        try { a.scrollIntoView({ block: 'center' }); } catch (e) {}
                        a.click();
                        return idm[1];
                      }
                      return '';
                    }""",
                    own_post_info_id,
                )
                if clicked_id:
                    self.page.wait_for_timeout(1500)
                    if self._detail_panel_shows_non_own_post():
                        return clicked_id
            except Exception:
                pass
            card_sel = (
                '[class*="list-components-item-job-card"] a[href*="/city-"], '
                '[class*="list-components-item-job-card"] a[href*="/city/"], '
                '[class*="JobListItem"] a[href*="/city-"], '
                '[class*="JobListItem"] a[href*="/city/"], '
                'main [class*="list"] a[href*="/city-"], '
                'main [class*="list"] a[href*="/city/"], '
                'main a[href*="/city/"][href*="cate-"]'
            )
            self.page.wait_for_selector(card_sel, timeout=45000)
            cards = self.page.locator(card_sel)
            n = cards.count()
            if n == 0:
                raise RuntimeError("列表页未找到职位卡片")

            for i in range(min(n, 50)):
                card = cards.nth(i)
                try:
                    html = card.evaluate("el => el.outerHTML || ''")
                except Exception:
                    continue
                if own_post_info_id in html:
                    continue
                m = re.search(r"-(\d{12,})(?:[\"'/]|$)", html or "")
                info_id = m.group(1) if m else ""
                if not info_id:
                    try:
                        href = card.locator("a[href]").first.get_attribute("href") or ""
                        info_id = self._extract_info_id_from_href(href)
                    except Exception:
                        pass
                card.scroll_into_view_if_needed()
                card.click(timeout=20000)
                self.page.wait_for_timeout(1500)
                if self._detail_panel_shows_non_own_post():
                    return info_id
                self.logger.info(
                    "链接列表第 %s 条点击后仍非非本人态，试下一条", i
                )

            raise RuntimeError(
                f"未找到非本人职位卡片（列表 {n} 条均含本人帖 id {own_post_info_id}）"
            )
        except Exception as e:
            self.logger.error(f"点击非本人职位卡片失败: {e}")
            raise

    def _detail_panel_shows_non_own_post(self) -> bool:
        """非本人帖：有 Contact 且无 Withdraw；用于列表点击后校验是否真切换到他人帖。"""
        try:
            if self.page.get_by_role("button", name="Withdraw").is_visible(timeout=1200):
                return False
        except Exception:
            pass
        try:
            return self.page.get_by_role("button", name="Contact").is_visible(timeout=3000)
        except Exception:
            return False

    def _extract_info_id_from_href(self, href: str) -> str:
        if not href:
            return ""
        for pattern in (r"-(\d{12,})(?:/|$)", r"infoId=(\d+)", r"/(\d{12,})/"):
            m = re.search(pattern, href, re.I)
            if m:
                return m.group(1)
        return ""

    def get_detail_info_id_from_new_tab_href(self) -> str:
        """从详情区链接解析当前帖子 InfoID（用于接口比对）。优先 New tab，其次详情卡片内帖子链接。"""
        try:
            href = self.get_new_tab_href() or ""
            if not href:
                href = (
                    self.page.get_by_role("link", name="New tab").first.get_attribute("href")
                    or ""
                )
            pid = self._extract_info_id_from_href(href)
            if pid:
                return pid
            # New tab 可能为 javascript: 或空，改为扫描详情卡片内 a[href]
            try:
                links = self.page.locator('[class*="detailsCard"] a[href]').all()
                for link in links[:20]:
                    try:
                        h = link.get_attribute("href") or ""
                        pid = self._extract_info_id_from_href(h)
                        if pid:
                            return pid
                    except Exception:
                        continue
            except Exception:
                pass
            # 最后从详情卡片 HTML 中提取典型 slug-id 形态
            try:
                html = self.page.locator('[class*="detailsCard"]').first.evaluate(
                    "el => el ? el.innerHTML : ''"
                )
                m = re.search(r"-(\d{12,})(?:[\"'/]|$)", html or "")
                if m:
                    return m.group(1)
            except Exception:
                pass
            # 属性 / 全文扫描（New tab 无 href、列表卡片无标准链接时）
            try:
                dom_id = self.page.evaluate("""
                    () => {
                      const roots = document.querySelectorAll(
                        '[class*="detailsCard"], [class*="JobDetail"], [class*="detail"]'
                      );
                      for (const root of roots) {
                        for (const a of root.attributes || []) {
                          const m = (a.value || '').match(/(\\d{13,16})/);
                          if (m) return m[1];
                        }
                        const html = root.innerHTML || '';
                        const m2 = html.match(/-(\\d{13,16})(?:["'/\\\\?]|$)/);
                        if (m2) return m2[1];
                      }
                      return '';
                    }
                """)
                if dom_id:
                    return str(dom_id)
            except Exception:
                pass
        except Exception as e:
            self.logger.error(f"解析详情区 infoId 失败: {e}")
        return ""

    def resolve_info_id_for_current_detail_panel(self, own_post_info_id: str) -> str:
        """
        根据当前详情面板标题，在详情区 DOM 中出现的候选数字 id 中通过 imcinfo 反查匹配的帖子 InfoID。
        用于列表/详情 DOM 中不含标准链接时的兜底（TC014 等）。仅扫描详情卡片，避免整页噪声 id。
        """
        panel_title = (self.get_detail_panel_title() or "").strip()
        if not panel_title:
            return ""
        try:
            detail_html = ""
            try:
                detail_html = self.page.locator('[class*="detailsCard"]').first.evaluate(
                    "el => el ? el.innerHTML : ''"
                ) or ""
            except Exception:
                detail_html = ""
            candidates = set(re.findall(r"\d{13,16}", detail_html))
            # 详情区偶无不暴露数字 id，回退整页候选（imcinfo 探测使用 quiet=True）
            if len(candidates) < 2:
                candidates |= set(re.findall(r"\d{13,16}", self.page.content() or ""))
            exact, partial = [], []
            for cid in candidates:
                if cid == own_post_info_id:
                    continue
                data = self.fetch_post_info_from_api(cid, quiet=True)
                api_t = str(data.get("Title", "")).strip()
                if not api_t:
                    continue
                if api_t == panel_title:
                    exact.append(cid)
                elif api_t in panel_title or panel_title in api_t:
                    partial.append((len(api_t), cid))
            if exact:
                return exact[0]
            if partial:
                partial.sort(reverse=True)
                return partial[0][1]
        except Exception as e:
            self.logger.error(f"resolve_info_id_for_current_detail_panel: {e}")
        return ""

    def click_card_by_text(self, title_text: str):
        """
        通过帖子标题文本点击对应卡片

        Args:
            title_text: 帖子标题关键词（如 "software engineer"），支持子串；匹配多个时优先点左栏列表
        """
        try:
            if not (title_text or "").strip():
                raise ValueError("title_text 为空")
            # 先尝试完整子串（不区分大小写由 Playwright 文本引擎处理）
            matches = self.page.get_by_text(title_text, exact=False).all()
            if not matches:
                # 回退：仅关键词（如 engineer），适配列表只展示部分标题
                for token in re.split(r"\W+", title_text.strip()):
                    if len(token) >= 4:
                        matches = self.page.get_by_text(
                            re.compile(re.escape(token), re.I)
                        ).all()
                        if matches:
                            break
            if not matches:
                raise RuntimeError(f"未找到可点击的「{title_text}」相关列表节点")
            clicked = False
            for el in matches:
                try:
                    # 跳过详情面板中的元素（类名含 detailsCard）
                    class_name = el.evaluate("el => el.className || ''")
                    if 'detailsCard' in class_name or 'DetailsCard' in class_name:
                        continue
                    el.scroll_into_view_if_needed()
                    el.click()
                    clicked = True
                    break
                except Exception:
                    continue
            if not clicked:
                self.page.get_by_text(title_text, exact=False).first.click()
            self.page.wait_for_timeout(1500)
        except Exception as e:
            self.logger.error(f"点击标题为'{title_text}'的卡片失败: {e}")
            raise

    # ==================== 详情面板 - 文本信息读取 ====================

    def _detail_panel_title_heuristic(self) -> str:
        """
        不依赖 detailsCard 类名（线上可能改为 CSS Modules 哈希或结构变化）：
        从 Favourites 按钮向上找标题，或取视口右侧主标题。
        """
        try:
            text = self.page.evaluate(
                r"""
                () => {
                  const EXCLUDE = new Set([
                    'description','company','location','requirements','similar jobs',
                    'employment','salary','job type','favourites','new tab','share',
                    'withdraw','edit','contact','resume',
                  ]);
                  const clean = (s) => (s || '').replace(/\s+/g, ' ').trim();
                  const fav = [...document.querySelectorAll('button, [role="button"], a')].find(
                    (el) => /^Favourites$/i.test(((el.textContent || '').trim()))
                  );
                  const walkUp = (start) => {
                    let n = start;
                    for (let d = 0; d < 18 && n; d++) {
                      const hs = n.querySelectorAll('h1, h2, h3');
                      for (const h of hs) {
                        const t = clean(h.innerText);
                        if (!t || t.length > 500) continue;
                        const low = t.toLowerCase();
                        if (EXCLUDE.has(low)) continue;
                        const r = h.getBoundingClientRect();
                        if (r.width < 2 || r.height < 2) continue;
                        return t;
                      }
                      n = n.parentElement;
                    }
                    return '';
                  };
                  if (fav) {
                    const t = walkUp(fav);
                    if (t) return t;
                  }
                  const vw = window.innerWidth;
                  const vh = window.innerHeight;
                  let best = '';
                  for (const h of document.querySelectorAll('h1, h2, h3')) {
                    const r = h.getBoundingClientRect();
                    if (r.bottom < 40 || r.top > vh - 20 || r.width < 2) continue;
                    if (r.left < vw * 0.35) continue;
                    const t = clean(h.innerText);
                    if (!t || t.length > 500) continue;
                    const low = t.toLowerCase();
                    if (EXCLUDE.has(low)) continue;
                    if (t.length > best.length) best = t;
                  }
                  return best;
                }
                """
            )
            return (text or "").strip()
        except Exception:
            return ""

    def _visible_text_in_right_half(self, substring: str, min_x_ratio: float = 0.30) -> str:
        """
        在页面中查找包含 substring 的节点：优先视口右侧（详情区），否则取 **最靠右** 的匹配
       （列表在左、详情在右，可避免仅命中左栏列表项）。
        """
        sub = (substring or "").strip()
        if len(sub) < 2:
            return ""
        try:
            vw = (self.page.viewport_size or {}).get("width") or 1280
            loc = self.page.get_by_text(sub, exact=False)
            n = loc.count()
            best_txt, best_x = "", -1.0
            for i in range(min(n, 50)):
                el = loc.nth(i)
                try:
                    box = el.bounding_box()
                except Exception:
                    continue
                if not box or box["width"] <= 0:
                    continue
                x = float(box["x"])
                txt = (el.text_content() or "").strip()
                if not txt:
                    continue
                if x >= vw * min_x_ratio:
                    return txt
                if x > best_x:
                    best_x = x
                    best_txt = txt
            if best_txt:
                return best_txt
        except Exception:
            pass
        try:
            loc = self.page.get_by_text(sub, exact=False)
            if loc.count() == 1:
                return (loc.first.text_content() or "").strip()
        except Exception:
            pass
        return ""

    def _description_content_heuristic(self) -> str:
        """从 Description 区块或详情区 innerText 中解析首段描述（不依赖 detailsCard）。"""
        try:
            text = self.page.evaluate(
                r"""
                () => {
                  const clean = (s) => (s || '').replace(/\s+/g, ' ').trim();
                  const roots = document.querySelectorAll(
                    '[class*="JobDetail"], [class*="DetailsCard"], [class*="detail"], aside, main'
                  );
                  for (const root of roots) {
                    const blob = root.innerText || '';
                    const idx = blob.indexOf('Description');
                    if (idx < 0) continue;
                    const after = blob.slice(idx + 11).trim();
                    const lines = after.split('\n').map((s) => s.trim()).filter(Boolean);
                    for (const ln of lines) {
                      if (/^description$/i.test(ln)) continue;
                      if (ln.length > 2 && ln.length < 4000) return ln;
                    }
                  }
                  const heads = document.querySelectorAll('h2, h3, h4, div, span');
                  for (const el of heads) {
                    if (!/^Description$/i.test(clean(el.innerText))) continue;
                    let p = el.parentElement;
                    for (let i = 0; i < 6 && p; i++) {
                      const para = p.querySelector('p');
                      if (para) {
                        const t = clean(para.innerText);
                        if (t && t.length > 2) return t;
                      }
                      p = p.nextElementSibling;
                    }
                  }
                  return '';
                }
                """
            )
            return (text or "").strip()
        except Exception:
            return ""

    def get_detail_panel_title(self, *, api_title_hint: str = "") -> str:
        """获取详情面板帖子标题文本（优先锚定 JobDetail / DetailsCard 根节点，避免全局 aside 误匹配）"""
        if api_title_hint:
            hit = self._visible_text_in_right_half(api_title_hint.strip())
            if hit:
                return hit
        fast = self._detail_panel_title_heuristic()
        if fast:
            return fast

        try:
            self.page.locator(
                "[class*='JobDetail_jobDetail'], [class*='DetailsCard_detailsCard'], "
                "[class*='detailsCard'], [class*='JobDetail']"
            ).first.wait_for(state="visible", timeout=12000)
        except Exception:
            pass
        try:
            self.page.get_by_text("Favourites").first.wait_for(state="visible", timeout=8000)
        except Exception:
            pass
        self.page.wait_for_timeout(400)

        root_selectors = (
            "[class*='JobDetail_jobDetail']",
            "[class*='DetailsCard_detailsCard']",
            "[class*='detailsCard']",
        )
        inner_selectors = (
            "[class*='detailsCardTitle']",
            "[class*='DetailsCard'] [class*='Title']",
            "[class*='DetailsCard'] [class*='title']",
            "h1",
            "h2",
            "h3",
            "[class*='Title']",
            "[class*='jobTitle']",
            "[class*='heading']",
        )
        for rsel in root_selectors:
            root = self.page.locator(rsel).first
            for isel in inner_selectors:
                try:
                    title_el = root.locator(isel).first
                    text = (title_el.text_content(timeout=4000) or "").strip()
                    if text and len(text) < 600:
                        return text
                except Exception:
                    continue
            try:
                ev = root.evaluate(
                    """(el) => {
                    const pick = (n) => (n && (n.innerText || '').trim()) || '';
                    for (const s of ['h1','h2','h3']) {
                      const h = el.querySelector(s);
                      const t = pick(h);
                      if (t && t.length < 600) return t;
                    }
                    const cand = el.querySelectorAll('[class*="Title"], [class*="title"]');
                    for (const n of cand) {
                      const t = pick(n);
                      if (t && t.length < 600 && t.length > 1) return t;
                    }
                    return '';
                }"""
                )
                text = (ev or "").strip()
                if text:
                    return text
            except Exception:
                continue

        fallback_global = (
            "[class*='detailsCardTitle']",
            "[class*='DetailsCard'] [class*='Title'], [class*='DetailsCard'] [class*='title']",
            "[class*='detailsCard'] h1",
            "[class*='detailsCard'] h2",
            "[class*='detailsCard'] h3",
            ".jobDetail-title",
            "[class*='detailPanel'] h1",
            "[class*='rightPanel'] h1",
            "[class*='RightPanel'] h1",
        )
        for sel in fallback_global:
            try:
                title_el = self.page.locator(sel).first
                text = (title_el.text_content(timeout=4000) or "").strip()
                if text:
                    return text
            except Exception:
                continue
        self.logger.error("获取详情面板标题失败：所有候选选择器均未取到文本")
        if api_title_hint:
            hit = self._visible_text_in_right_half(api_title_hint.strip())
            if hit:
                return hit
        return ""

    def get_detail_salary_text(self) -> str:
        """获取详情面板薪资文本（如 '€ 5,000/year'）"""
        try:
            salary_el = self.page.locator("[class*='detailsCardPrice']").first
            return salary_el.text_content(timeout=5000) or ""
        except Exception as e:
            self.logger.error(f"获取详情面板薪资失败: {e}")
            return ""

    def get_detail_company_text(self) -> str:
        """获取详情面板公司名文本（标题下方区域）"""
        try:
            company_el = self.page.locator("[class*='detailsCardCompany']").first
            return company_el.text_content(timeout=5000) or ""
        except Exception as e:
            self.logger.error(f"获取详情面板公司名失败: {e}")
            return ""

    def get_job_tags_count(self) -> int:
        """获取详情面板职位标签数量"""
        try:
            tags = self.page.locator("[class*='detailsCardEmploymentItem'], [class*='employmentItem']").all()
            return len(tags)
        except Exception:
            return 0

    def get_description_content_text(self, *, api_content_hint: str = "") -> str:
        """获取 Description 段落内容文本"""
        hint = (api_content_hint or "").strip()
        if hint:
            hit = self._visible_text_in_right_half(hint[:800])
            if hit:
                return hit
        heur = self._description_content_heuristic()
        if heur:
            return heur

        selectors = (
            "[class*='descriptionWrapper'] p",
            "[class*='DescriptionContent'] p",
            "[class*='detailsCard'] [class*='description' i] p",
            "[class*='detailsCard'] [class*='Description']",
        )
        for sel in selectors:
            try:
                desc_el = self.page.locator(sel).first
                text = (desc_el.text_content(timeout=5000) or "").strip()
                if text:
                    return text
            except Exception:
                continue
        try:
            card = self.page.locator("[class*='detailsCard']").first
            if card.is_visible(timeout=2000):
                blob = (card.inner_text(timeout=5000) or "")
                if "Description" in blob:
                    after = blob.split("Description", 1)[-1]
                    lines = [ln.strip() for ln in after.splitlines() if ln.strip()]
                    if lines:
                        return lines[0][:2000]
        except Exception as e:
            self.logger.error(f"获取Description内容失败: {e}")
        return ""

    # ==================== 详情面板 - 可见性判断 ====================

    def is_detail_panel_visible(self) -> bool:
        """检查右侧详情面板是否可见（通过 Description 标题判断）"""
        try:
            desc_el = self.page.locator("[class*='descriptionTitle']").first
            if desc_el.is_visible(timeout=5000):
                return True
            return self.page.get_by_text("Description").first.is_visible(timeout=3000)
        except Exception:
            return False

    def is_detail_description_visible(self, *, api_content_hint: str = "") -> bool:
        """检查详情面板 Description 区域标题和内容段落是否均可见"""
        hint = (api_content_hint or "").strip()
        if hint and self._visible_text_in_right_half(hint[:200]):
            return True
        try:
            if self._description_content_heuristic().strip():
                return True
        except Exception:
            pass
        try:
            if self.page.get_by_text("Description", exact=False).first.is_visible(timeout=3000):
                return bool(self.get_description_content_text(api_content_hint=hint).strip())
        except Exception:
            pass
        try:
            desc_title = self.page.locator("[class*='descriptionTitle']").first
            if not desc_title.is_visible(timeout=5000):
                return False
            desc_para = self.page.locator(
                "[class*='descriptionWrapper'] p, [class*='DescriptionContent'] p"
            ).first
            return desc_para.is_visible(timeout=3000)
        except Exception:
            return False

    def is_logged_in_state(self) -> bool:
        """判断当前页面是否处于已登录状态（右上角是否有 Log in / Register）"""
        try:
            login_btn = self.page.get_by_text("Log in / Register").first
            return not login_btn.is_visible(timeout=3000)
        except Exception:
            return True

    def is_logged_out_state(self) -> bool:
        """判断当前是否处于未登录状态（右上角显示 Log in / Register）"""
        try:
            login_btn = self.page.get_by_text("Log in / Register").first
            return login_btn.is_visible(timeout=5000)
        except Exception:
            return False

    # ==================== 操作按钮 - 可见性判断 ====================

    def is_withdraw_button_visible(self) -> bool:
        """检查 Withdraw 按钮是否可见（仅本人帖已登录时显示）"""
        try:
            btn = self.page.get_by_role("button", name="Withdraw")
            return btn.is_visible(timeout=3000)
        except Exception:
            return False

    def is_edit_button_visible(self) -> bool:
        """检查 Edit 按钮是否可见（仅本人帖已登录时显示）"""
        try:
            btn = self.page.get_by_role("button", name="Edit")
            return btn.is_visible(timeout=3000)
        except Exception:
            return False

    def is_contact_button_visible(self) -> bool:
        """检查 Contact 按钮是否可见（非本人帖或未登录时显示）"""
        try:
            btn = self.page.get_by_role("button", name="Contact")
            return btn.is_visible(timeout=3000)
        except Exception:
            return False

    def is_favourites_button_visible(self) -> bool:
        """检查 Favourites 按钮是否可见（通用）"""
        try:
            btn = self.page.get_by_text("Favourites").first
            return btn.is_visible(timeout=3000)
        except Exception:
            return False

    def is_new_tab_link_visible(self) -> bool:
        """检查 New tab 链接是否可见（通用）"""
        try:
            link = self.page.get_by_role("link", name="New tab").first
            return link.is_visible(timeout=3000)
        except Exception:
            return False

    def is_share_button_visible(self) -> bool:
        """检查 Share 按钮是否可见（通用）"""
        try:
            btn = self.page.get_by_text("Share").first
            return btn.is_visible(timeout=3000)
        except Exception:
            return False

    # ==================== 操作按钮 - 执行操作 ====================

    def click_edit_button(self):
        """点击 Edit 按钮（本人帖），跳转到编辑页"""
        try:
            self.page.get_by_role("button", name="Edit").click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击Edit按钮失败: {e}")
            raise

    def click_withdraw_button(self):
        """点击 Withdraw 按钮（本人帖），弹出确认对话框"""
        try:
            self.page.get_by_role("button", name="Withdraw").click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击Withdraw按钮失败: {e}")
            raise

    def click_contact_button(self):
        """点击 Contact 按钮（非本人帖），已登录时跳转聊天页，未登录时弹出登录引导弹窗"""
        try:
            self.page.get_by_role("button", name="Contact").click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击Contact按钮失败: {e}")
            raise

    def click_favourites_button(self):
        """点击 Favourites 按钮，触发收藏/取消收藏"""
        try:
            # 优先使用 detailsCardBtnItem 类选择器（精确匹配 Favourites 按钮）
            fav_btn = self.page.locator("[class*='detailsCardBtnItem']:has-text('Favourites')").first
            fav_btn.click(timeout=10000)
        except Exception:
            try:
                self.page.get_by_text("Favourites").first.click()
            except Exception as e:
                self.logger.error(f"点击Favourites按钮失败: {e}")
                raise

    def click_share_button(self):
        """点击 Share 按钮，触发复制链接"""
        try:
            self.page.get_by_text("Share").first.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击Share按钮失败: {e}")
            raise

    def click_new_tab_link(self):
        """点击 New tab 链接，在新标签页打开帖子详情页"""
        try:
            self.page.get_by_role("link", name="New tab").first.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击New tab链接失败: {e}")
            raise

    # ==================== Withdraw 确认弹窗 ====================

    def is_withdraw_dialog_visible(self) -> bool:
        """检查 Withdraw 确认对话框是否出现（自定义弹层，标题 'Heads Up'）"""
        try:
            heading = self.page.get_by_text("Heads Up").first
            return heading.is_visible(timeout=5000)
        except Exception:
            return False

    def get_withdraw_dialog_body_text(self) -> str:
        """获取 Withdraw 对话框正文文本"""
        try:
            body = self.page.get_by_text("Do you want to withdraw the listing?")
            return (body.text_content(timeout=3000) or "").strip()
        except Exception:
            return ""

    def is_withdraw_dialog_has_cancel_button(self) -> bool:
        """检查 Withdraw 对话框是否包含 Cancel 按钮"""
        try:
            btn = self.page.get_by_role("button", name="Cancel")
            return btn.is_visible(timeout=3000)
        except Exception:
            return False

    def is_withdraw_dialog_has_ok_button(self) -> bool:
        """检查 Withdraw 对话框是否包含 OK 按钮"""
        try:
            btn = self.page.get_by_role("button", name="OK")
            return btn.is_visible(timeout=3000)
        except Exception:
            return False

    def click_withdraw_dialog_cancel(self):
        """点击 Withdraw 对话框中的 Cancel 按钮，关闭对话框"""
        try:
            self.page.get_by_role("button", name="Cancel").click()
            self.page.wait_for_timeout(800)
        except Exception as e:
            self.logger.error(f"点击Withdraw对话框Cancel按钮失败: {e}")
            raise

    def click_withdraw_dialog_close_icon(self):
        """点击 Withdraw 对话框右上角 × 关闭按钮"""
        try:
            close_btn = self.page.locator("img[alt='close']").first
            close_btn.click()
            self.page.wait_for_timeout(800)
        except Exception:
            try:
                close_btn = self.page.get_by_role("button", name="close").first
                close_btn.click()
                self.page.wait_for_timeout(800)
            except Exception as e:
                self.logger.error(f"点击Withdraw对话框×关闭按钮失败: {e}")
                raise

    # ==================== 未登录场景 - 登录引导弹窗 ====================

    def is_login_guide_dialog_visible(self) -> bool:
        """检查未登录点击Contact后弹出的登录引导弹窗是否可见（标题 'Welcome to OK.com'）"""
        try:
            heading = self.page.get_by_text("Welcome to OK.com")
            return heading.is_visible(timeout=5000)
        except Exception:
            return False

    def is_login_guide_dialog_has_email_input(self) -> bool:
        """检查登录引导弹窗是否包含 Email or phone number 输入框"""
        try:
            # 弹窗中输入框的 label 文本为 "Email or phone number"，placeholder 为 "placeholder"
            dialog = self.page.get_by_role("dialog")
            input_el = dialog.get_by_role("textbox").first
            return input_el.is_visible(timeout=3000)
        except Exception:
            try:
                input_el = self.page.get_by_text("Email or phone number").first
                return input_el.is_visible(timeout=3000)
            except Exception:
                return False

    def is_login_guide_continue_button_disabled(self) -> bool:
        """检查登录引导弹窗中 Continue 按钮初始状态是否为 disabled"""
        try:
            btn = self.page.get_by_role("button", name="Continue")
            return btn.is_disabled(timeout=3000)
        except Exception:
            return False

    def click_login_guide_dialog_close(self):
        """点击登录引导弹窗右上角 × 关闭按钮"""
        try:
            # 关闭按钮是 img 元素，class 含 'closeBtn'
            close_btn = self.page.locator("img[class*='closeBtn']").first
            close_btn.click()
            self.page.wait_for_timeout(800)
        except Exception:
            try:
                close_btn = self.page.locator("[aria-label='Close'], button.close, button[class*='close'], img[alt='close']").first
                close_btn.click()
                self.page.wait_for_timeout(800)
            except Exception as e:
                self.logger.error(f"点击登录引导弹窗×关闭按钮失败: {e}")
                raise

    # ==================== New tab - 新标签页 ====================

    def click_new_tab_and_get_new_page(self):
        """
        点击 New tab 链接，等待新标签页打开，返回新标签页 Page 对象

        Returns:
            新标签页 Page 对象（Playwright Page）
        """
        try:
            with self.page.context.expect_page() as new_page_info:
                self.page.get_by_role("link", name="New tab").first.click()
            new_page = new_page_info.value
            new_page.wait_for_load_state("domcontentloaded", timeout=15000)
            try:
                new_page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                pass
            return new_page
        except Exception as e:
            self.logger.error(f"点击New tab并等待新标签页失败: {e}")
            raise

    def get_new_tab_href(self) -> str:
        """获取 New tab 链接的 href 属性值（可能为空字符串，为动态赋值）"""
        try:
            href = self.page.get_by_role("link", name="New tab").first.get_attribute("href")
            return href or ""
        except Exception:
            return ""

    # ==================== Resume 入口 ====================

    def is_resume_entry_visible(self) -> bool:
        """检查详情面板侧边的 Resume 入口是否可见"""
        try:
            resume_el = self.page.get_by_text("Resume").first
            return resume_el.is_visible(timeout=5000)
        except Exception:
            return False

    def click_resume_entry(self):
        """点击 Resume 入口，跳转到简历填写页"""
        try:
            self.page.get_by_text("Resume").first.click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击Resume入口失败: {e}")
            raise

    # ==================== 接口查询：帖子信息（标题/描述） ====================

    def fetch_post_info_from_api(self, info_id: str, *, quiet: bool = False) -> dict:
        """
        通过接口查询帖子信息，返回包含 Title、Content 等字段的字典

        接口：GET https://easypost.58v5.cn/crawl/imcinfo/{infoId}
        主要字段：Title（帖子标题）、Content（帖子描述/正文）

        优先使用 Playwright ``APIRequestContext``（``page.request.get``）发起请求，
        避免在页面上下文中用 ``fetch`` 受跨域/CORS 限制导致始终拿不到数据。

        Args:
            info_id: 帖子 InfoID（如 "6522669642316510"）
            quiet: 为 True 时不记录 imcinfo 空响应错误（用于候选 id 探测）

        Returns:
            dict，接口返回的 JSON 对象；若请求失败则返回空 dict
        """
        url = f"https://easypost.58v5.cn/crawl/imcinfo/{info_id}"
        _imc_headers = {
            # 部分网关对纯 APIRequest 返回 406，需贴近真实浏览器 Accept/UA/Referer
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Referer": "https://es.58v5.cn/",
        }
        try:
            api_request = getattr(self.page, "request", None) or self.page.context.request
            resp = api_request.get(url, timeout=30_000, headers=_imc_headers)
            if resp.status != 200:
                # 再试一次：个别环境仅接受 application/json
                if resp.status == 406:
                    resp = api_request.get(
                        url,
                        timeout=30_000,
                        headers={**_imc_headers, "Accept": "application/json"},
                    )
                if resp.status != 200:
                    if not quiet:
                        self.logger.error(
                            f"接口 imcinfo/{info_id} HTTP {resp.status}"
                        )
                    return {}
            data = resp.json()
            if isinstance(data, dict):
                return data
            return {}
        except Exception as e:
            if not quiet:
                self.logger.warning(
                    f"page.request 拉取 imcinfo 失败，回退到页面 fetch: {e}"
                )
        # 回退：部分环境仍可用页面内 fetch
        try:
            result = self.page.evaluate(
                f"""
                async () => {{
                    try {{
                        const resp = await fetch('{url}', {{
                            method: 'GET',
                            headers: {{ 'Content-Type': 'application/json' }}
                        }});
                        if (!resp.ok) return null;
                        return await resp.json();
                    }} catch (e) {{
                        return null;
                    }}
                }}
                """
            )
            if result is None:
                if not quiet:
                    self.logger.error(f"接口 imcinfo/{info_id} 返回 null 或请求失败")
                return {}
            return result if isinstance(result, dict) else {}
        except Exception as e2:
            if not quiet:
                self.logger.error(
                    f"fetch_post_info_from_api 失败 (infoId={info_id}): {e2}"
                )
            return {}

    @staticmethod
    def _imcinfo_pick_title_content(data: dict) -> tuple[str, str]:
        """兼容多种 JSON 字段命名与一层嵌套。"""
        if not isinstance(data, dict):
            return "", ""

        def pick(d: dict) -> tuple[str, str]:
            title = ""
            content = ""
            for k in ("Title", "title", "TITLE", "topic", "Topic"):
                v = d.get(k)
                if v is not None and str(v).strip():
                    title = str(v).strip()
                    break
            for k in ("Content", "content", "CONTENT", "Description", "description"):
                v = d.get(k)
                if v is not None and str(v).strip():
                    content = str(v).strip()
                    break
            return title, content

        t, c = pick(data)
        if t and c:
            return t, c
        nested = data.get("data") or data.get("result") or data.get("body")
        if isinstance(nested, dict):
            nt, nc = pick(nested)
            if not t:
                t = nt
            if not c:
                c = nc
        return t, c

    def get_post_title_from_api(self, info_id: str) -> str:
        """
        从接口返回结果中提取帖子标题（Title 字段）

        Args:
            info_id: 帖子 InfoID

        Returns:
            标题字符串，若接口失败则返回空字符串
        """
        data = self.fetch_post_info_from_api(info_id)
        t, _ = self._imcinfo_pick_title_content(data)
        return t

    def get_post_content_from_api(self, info_id: str) -> str:
        """
        从接口返回结果中提取帖子描述（Content 字段）

        Args:
            info_id: 帖子 InfoID

        Returns:
            描述字符串，若接口失败则返回空字符串
        """
        data = self.fetch_post_info_from_api(info_id)
        _, c = self._imcinfo_pick_title_content(data)
        return c

    # ==================== Toast / Alert 验证 ====================

    def get_toast_text(self) -> str:
        """获取 toast/alert 提示文本"""
        try:
            alert_el = self.page.get_by_role("alert").first
            text = alert_el.text_content(timeout=5000) or ""
            return text.strip()
        except Exception as e:
            self.logger.error(f"获取toast文本失败: {e}")
            return ""

    def wait_for_toast(self, expected_text: str, timeout_ms: int = 5000) -> bool:
        """等待含指定文案的 toast 出现（使用 wait_for_selector 立即捕获）"""
        # 优先使用 wait_for_selector（最快，直到 toast 出现才返回）
        try:
            self.page.wait_for_selector(
                f"[role='alert']:has-text('{expected_text}')",
                timeout=timeout_ms
            )
            return True
        except Exception:
            pass
        # 备用：Bootstrap toast 样式
        try:
            self.page.wait_for_selector(
                f".toast:has-text('{expected_text}')",
                timeout=2000
            )
            return True
        except Exception:
            pass
        # 最后检查当前 alert 文案（toast 可能已消失，只检查现存的）
        try:
            alert_els = self.page.get_by_role("alert").all()
            for alert_el in alert_els:
                try:
                    text = (alert_el.text_content(timeout=500) or "").lower()
                    if text and expected_text.lower() in text:
                        return True
                except Exception:
                    pass
        except Exception:
            pass
        return False

    def wait_for_toast_text(self, timeout_ms: int = 5000) -> str:
        """等待任意 toast 出现并返回其文本内容（用于判断 Added/Removed 状态）"""
        try:
            self.page.wait_for_selector("[role='alert']", timeout=timeout_ms)
            alert_els = self.page.get_by_role("alert").all()
            for el in alert_els:
                try:
                    text = (el.text_content(timeout=500) or "").strip()
                    if text:
                        return text
                except Exception:
                    pass
        except Exception:
            pass
        try:
            self.page.wait_for_selector(".toast", timeout=2000)
            els = self.page.locator(".toast").all()
            for el in els:
                try:
                    text = (el.text_content(timeout=500) or "").strip()
                    if text:
                        return text
                except Exception:
                    pass
        except Exception:
            pass
        return ""
