# pages/property_list_page.py
"""房产列表页 Page Object（列表卡片头像、名称等）"""
import re
from playwright.sync_api import Page
from pages.base_page import BasePage


class PropertyListPage(BasePage):
    """房产列表页（支持 AE/AU 等站点列表卡片）"""

    def __init__(self, page: Page):
        super().__init__(page)

    def navigate_to_list(self, list_url: str, timeout: int = 30000):
        """打开列表页"""
        self.page.goto(list_url, timeout=timeout, wait_until="domcontentloaded")
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)

    def get_list_card_links_count(self, path_part: str = "/cate-property-for-sale-"):
        """列表内卡片链接数量（录制：a[href*=\"...\"]）。等待至少一张卡片出现（最多10秒）。
        商业买房（cate-commercial-buy-）的实际卡片 href 为 cate-commercial-property-for-sale- 或 cate-land-development-sale，
        商业租房（cate-commercial-rent-）的实际卡片 href 为 cate-commercial-property-for-rent-。
        """
        if path_part == "cate-commercial-buy-":
            locator = self.page.locator(
                'a[href*="cate-commercial-property-for-sale-"], a[href*="cate-land-development-sale"]'
            )
        elif path_part == "cate-commercial-rent-":
            locator = self.page.locator('a[href*="cate-commercial-property-for-rent-"]')
        else:
            locator = self.page.locator(f'a[href*="{path_part}"]')
        try:
            locator.first.wait_for(state="visible", timeout=10000)
        except Exception:
            pass
        return locator.count()

    def get_agent_avatar_count(self):
        """列表内经纪人头像数量（录制：img[alt=\"agent-avatar\"]）"""
        return self.page.locator('img[alt="agent-avatar"]').count()

    def get_first_card_agent_name_text(self):
        """第一张卡片内文案（含经纪人名称，录制：卡片 link 内包含 OKerAU_xxx）"""
        first_card = self.page.locator('a[href*="cate-property-for-sale-"]').first
        return first_card.inner_text()

    def get_agent_avatar_src_list(self):
        """所有经纪人头像 img 的 src 列表（用于校验兜底头像 #fff）"""
        return self.page.locator('img[alt="agent-avatar"]').evaluate_all(
            "els => els.map(e => e.getAttribute('src') || '')"
        )

    def click_first_agent_avatar(self):
        """点击第一张卡片的经纪人头像（录制：点击头像可打开新标签页进入详情）"""
        self.page.locator('img[alt="agent-avatar"]').first.click()

    # ---------- 收藏功能（录制：AU 列表页）----------

    def click_first_fav_icon(self):
        """点击第一张卡片的收藏图标（未登录会弹出登录框；已登录会切换收藏状态）"""
        self.page.locator('img[alt="fav-icon"]').first.click()

    def click_fav_icon_nth(self, n: int):
        """点击第 n 张卡片的收藏图标（n 从 0 开始）。等待图标出现后再点击。"""
        fav_locator = self.page.locator('img[alt="fav-icon"]')
        try:
            fav_locator.first.wait_for(state="visible", timeout=15000)
        except Exception:
            pass
        fav_locator.nth(n).click()

    def wait_for_toast_contains(self, text: str, timeout: int = 5000):
        """等待页面出现包含指定文案的 Toast（如 Added to favourites）"""
        self.page.get_by_text(text, exact=False).wait_for(state="visible", timeout=timeout)

    def is_login_dialog_visible(self, timeout: int = 3000):
        """是否出现登录对话框（Welcome to OK.com 或邮箱输入框）"""
        try:
            dialog = self.page.get_by_role("dialog")
            if dialog.is_visible(timeout=timeout):
                return True
        except Exception:
            pass
        try:
            return self.page.get_by_role("textbox", name="Email or phone number").is_visible(timeout=timeout)
        except Exception:
            return False

    def click_menu_dots(self):
        """点击右上角 ··· 菜单（仅在窄视口下可见）。

        在 1920px 桌面端，该按钮被 CSS 隐藏（响应式折叠），无需点击。
        在窄视口（移动/平板）下才会显示。
        """
        self.page.evaluate("window.scrollTo(0, 0)")
        self.page.wait_for_timeout(500)
        btn = self.page.get_by_text("···", exact=True).first
        btn.wait_for(state="attached", timeout=10000)
        box = btn.evaluate(
            "el => { const r = el.getBoundingClientRect(); return { w: r.width, h: r.height }; }"
        )
        if not box or box.get("w", 0) == 0 or box.get("h", 0) == 0:
            return False
        try:
            btn.evaluate("el => el.click()")
        except Exception:
            btn.click(force=True, timeout=5000)
        self.page.wait_for_timeout(500)
        return True

    def click_favourites_in_menu(self):
        """进入收藏页面。

        策略一（宽视口/桌面端）：直接导航到收藏页 URL。
        策略二（窄视口/移动端）：点击 ··· 菜单 → 点击 Favourites 菜单项。
        """
        # 策略一：直接通过 URL 导航（桌面端 1920px 下 ··· 菜单不可见时使用）
        current_url = self.page.url
        # 提取 base URL（scheme + host）
        from urllib.parse import urlparse
        parsed = urlparse(current_url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        favorites_url = f"{base}/biz/en/list/favorites"

        # 先尝试点击 ··· 菜单（窄视口时有效）
        dots_clicked = self.click_menu_dots()
        if dots_clicked:
            # 菜单已展开，点击 Favourites 菜单项
            fav = self.page.get_by_text("Favourites").first
            try:
                fav.wait_for(state="attached", timeout=5000)
                try:
                    fav.evaluate("el => el.click()")
                except Exception:
                    fav.click(force=True, timeout=5000)
                self.page.wait_for_timeout(500)
                return
            except Exception:
                pass

        # 策略一：直接导航到收藏页（桌面端 ··· 不可见时）
        self.page.goto(favorites_url, wait_until="domcontentloaded", timeout=30000)
        self.page.wait_for_timeout(1000)

    def get_first_card_title_in_favorites(self):
        """获取收藏页第一张卡片的标题（用于验证收藏/取消收藏）"""
        try:
            first_card = self.page.locator('a[href*="cate-property-for-sale-"], a[href*="residential-"]').first
            first_card.wait_for(state="visible", timeout=5000)
            text = first_card.inner_text()
            lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
            for ln in lines:
                if ln and not ln.startswith("A$") and not ln.startswith("Free") and "OKerAU_" not in ln:
                    return ln[:100]
            return lines[0] if lines else ""
        except Exception:
            return ""

    def is_card_in_favorites_by_title(self, title: str, timeout: int = 5000):
        """在收藏页中检查是否存在包含指定标题的卡片"""
        try:
            cards = self.page.locator('a[href*="cate-property-for-sale-"], a[href*="residential-"]')
            cards.first.wait_for(state="visible", timeout=timeout)
            n = cards.count()
            for i in range(n):
                try:
                    text = cards.nth(i).inner_text()
                    if title in text:
                        return True
                except Exception:
                    continue
            return False
        except Exception:
            return False

    # ---------- 列表卡片图片（AE/AU 列表页）----------

    def get_list_card_count(self, path_part: str = "cate-property"):
        """列表内卡片数量（支持 cate-property / cate-rent 等）"""
        return self.page.locator(f'a[href*="{path_part}"]').count()

    def get_card_images_count(self):
        """列表内卡片主图 img 数量（每卡至少一图或占位）"""
        return self.page.locator("a[href*='cate-'] img").count()

    def has_multi_image_indicator(self):
        """是否存在多图数量标识（如 1/2、1 / 2 格式的 swiper-pagination）"""
        import re as _re
        try:
            # 优先匹配卡片内的 swiper-pagination（轮播图片索引标识）
            loc = self.page.locator(".swiper-pagination")
            count = loc.count()
            for i in range(count):
                try:
                    text = loc.nth(i).inner_text(timeout=1000).strip()
                    if _re.search(r'\d+\s*/\s*\d+', text):
                        return True
                except Exception:
                    continue
            return False
        except Exception:
            return False

    def get_first_card_carousel_index(self):
        """
        获取第一张多图卡片的当前图片索引（如 "1/3" 返回 (1, 3)）
        注意：定位到第一张卡片内部的索引标识，避免读取到其他卡片的索引
        """
        try:
            # 先定位第一张卡片
            first_card = self.page.locator("a[href*='cate-']").first
            first_card.wait_for(state="visible", timeout=3000)
            # 在该卡片内查找索引标识
            indicator = first_card.locator("text=/\\d+\\s*\\/\\s*\\d+/").first
            indicator.wait_for(state="visible", timeout=3000)
            text = indicator.inner_text().strip()
            match = re.search(r'(\d+)\s*/\s*(\d+)', text)
            if match:
                return (int(match.group(1)), int(match.group(2)))
            return (0, 0)
        except Exception:
            return (0, 0)

    def get_first_card_visible_image_src(self):
        """获取第一张多图卡片当前可见图片的 src"""
        try:
            card = self.page.locator("a[href*='cate-']").first
            visible_img = card.locator("img").first
            return visible_img.get_attribute("src") or ""
        except Exception:
            return ""

    def click_carousel_next_on_first_card(self):
        """在第一张有多图的卡片上点击下一张（优先用 .card-swiper-next，避免匹配分页按钮）"""
        # 用精确的卡片选择器，排除侧边栏链接
        first_card = self.page.locator(
            "a[href*='cate-residential'], a[href*='cate-rent-'], a[href*='student-apartment']"
        ).first
        # 优先：轮播专属 class
        btn = first_card.locator(".card-swiper-next")
        if btn.count() > 0:
            try:
                btn.first.click(timeout=3000)
                self.page.wait_for_timeout(500)
                return
            except Exception:
                pass
        # 备用：卡片内 button（非分页按钮）
        try:
            inner_btn = first_card.locator("button").first
            if inner_btn.count() > 0:
                inner_btn.click(timeout=3000)
        except Exception:
            pass
        self.page.wait_for_timeout(500)

    def click_carousel_prev_on_first_card(self):
        """在第一张有多图的卡片上点击上一张（优先用 .card-swiper-prev，避免匹配分页按钮）"""
        first_card = self.page.locator(
            "a[href*='cate-residential'], a[href*='cate-rent-'], a[href*='student-apartment']"
        ).first
        btn = first_card.locator(".card-swiper-prev")
        if btn.count() > 0:
            try:
                btn.first.click(timeout=3000)
                self.page.wait_for_timeout(500)
                return
            except Exception:
                pass
        try:
            inner_btn = first_card.locator("button").last
            if inner_btn.count() > 0:
                inner_btn.click(timeout=3000)
        except Exception:
            pass
        self.page.wait_for_timeout(500)

    def is_carousel_button_enabled(self, button_name: str):
        """检查轮播按钮是否可用（button_name: "next" 或 "prev"）"""
        try:
            first_card = self.page.locator("a[href*='cate-']").first
            btn = first_card.get_by_role("button", name=button_name).first
            return not btn.is_disabled()
        except Exception:
            try:
                btn = self.page.get_by_role("button", name=button_name).first
                return not btn.is_disabled()
            except Exception:
                return False

    def click_first_card_image(self):
        """点击第一张卡片的主图区域（进入详情）"""
        self.page.locator("a[href*='cate-'] img").first.click()

    def get_page_url(self):
        return self.page.url

    # ---------- 列表卡片排列（商业地产）----------
    def get_commercial_card_count(self):
        """获取商业地产租房列表当前可见卡片总数。
        实际卡片 href 前缀为：
          - cate-commercial-property-for-rent-{subtype}/{slug}（商业租房）
          - cate-land-development-rent/{slug}（土地开发租房）
        需排除纯导航链接（href 以 /cate-commercial-rent/ 或 /cate-commercial-buy/ 结尾）。
        """
        locator = self.page.locator(
            'a[href*="cate-commercial-property-for-rent-"], a[href*="cate-land-development-rent/"]'
        )
        # 等待至少一张卡片出现（最多15秒），避免动态渲染未完成时 count=0
        try:
            locator.first.wait_for(state="visible", timeout=15000)
        except Exception:
            pass
        return locator.count()

    def get_rent_card_count(self):
        """获取普通租房列表当前可见卡片总数（href 含 cate-property-for-rent-）"""
        return self.page.locator('a[href*="cate-property-for-rent-"]').count()

    def get_rent_first_row_count(self):
        """统计普通租房列表第一行卡片数量（y 坐标差 < 50px 视为同行）"""
        cards = self.page.locator('a[href*="cate-property-for-rent-"]')
        total = cards.count()
        first_y = None
        count = 0
        for i in range(min(total, 12)):
            try:
                box = cards.nth(i).bounding_box()
                if box is None:
                    continue
                y = box["y"]
                if first_y is None:
                    first_y = y
                if abs(y - first_y) < 50:
                    count += 1
            except Exception:
                pass
        return count

    # ---------- 学生公寓列表 Bed 图标和数量 ----------
    def get_student_apartment_cards(self):
        """获取学生公寓列表卡片定位器（href 含 student-apartment）"""
        return self.page.locator('a[href*="student-apartment"]')

    def get_student_apartment_card_count(self):
        """获取学生公寓列表当前可见卡片总数"""
        return self.get_student_apartment_cards().count()

    def get_bed_count_from_card(self, card_locator):
        """从单张卡片中获取 Bed 数量文本（录制确认：img[src*='Bedrooms'] → closest item → label）"""
        try:
            return card_locator.evaluate("""el => {
                const img = el.querySelector('img.room-distance-type-item-icon[src*="Bedrooms"]');
                if (!img) return null;
                const item = img.closest('.room-distance-type-item');
                const label = item ? item.querySelector('.room-distance-type-item-label') : null;
                return label ? label.innerText.trim() : null;
            }""")
        except Exception:
            return None

    def get_bed_icon_visible(self, card_locator):
        """验证卡片内 Bed 图标（img[src*='Bedrooms']）是否可见且有尺寸"""
        try:
            icon = card_locator.locator('img[src*="Bedrooms"]')
            if icon.count() == 0:
                return False
            if not icon.first.is_visible(timeout=2000):
                return False
            box = icon.first.bounding_box()
            return box is not None and box["width"] > 0 and box["height"] > 0
        except Exception:
            return False

    def get_all_bed_counts(self, limit: int = 10):
        """批量获取前 N 张学生公寓卡片的 Bed 数量，返回列表（None 表示无 Bed 图标）"""
        cards = self.get_student_apartment_cards()
        total = cards.count()
        results = []
        for i in range(min(total, limit)):
            bed = self.get_bed_count_from_card(cards.nth(i))
            results.append(bed)
        return results

    def click_student_apartment_card(self, index: int = 0):
        """点击指定学生公寓卡片（默认第一张），返回弹出的详情页 page"""
        card = self.get_student_apartment_cards().nth(index)
        with self.page.expect_popup() as popup_info:
            card.click()
        detail_page = popup_info.value
        detail_page.wait_for_load_state("domcontentloaded", timeout=15000)
        detail_page.wait_for_timeout(1500)
        return detail_page

    def get_bed_count_from_detail_page(self, detail_page):
        """从详情页获取当前房源 Bed 数量（录制确认：MainInfo 区 img[src*='Bedrooms'] 旁的 MainInfo_value）"""
        try:
            return detail_page.evaluate("""() => {
                // 详情页顶部 MainInfo 区有独立结构：img.MainInfo_icon + div.MainInfo_value
                // 不能用 room-distance-type-item（那是推荐卡片区，是其他房源数据）
                const mainInfo = document.querySelector('[class*="MainInfo"]');
                if (mainInfo) {
                    const bedImg = mainInfo.querySelector('img[src*="Bedrooms"]');
                    if (bedImg) {
                        const valueEl = bedImg.nextElementSibling;
                        if (valueEl) return valueEl.innerText.trim();
                    }
                }
                // 兜底：直接查 MainInfo_icon 旁的 MainInfo_value
                const bedImg = document.querySelector('img[src*="Bedrooms"][class*="MainInfo"]');
                if (bedImg) {
                    const valueEl = bedImg.nextElementSibling;
                    if (valueEl) return valueEl.innerText.trim();
                }
                return null;
            }""")
        except Exception:
            return None

    # ---------- 学生公寓列表 Bathroom 图标和数量 ----------
    def get_bath_count_from_card(self, card_locator):
        """从单张卡片中获取 Bathroom 数量文本（录制确认：img.room-distance-type-item-icon[src*='Bathrooms'] → closest item → label）"""
        try:
            return card_locator.evaluate("""el => {
                const img = el.querySelector('img.room-distance-type-item-icon[src*="Bathrooms"]');
                if (!img) return null;
                const item = img.closest('.room-distance-type-item');
                const label = item ? item.querySelector('.room-distance-type-item-label') : null;
                return label ? label.innerText.trim() : null;
            }""")
        except Exception:
            return None

    def get_bath_icon_visible(self, card_locator):
        """验证卡片内 Bathroom 图标（img[src*='Bathrooms']）是否可见且有尺寸"""
        try:
            icon = card_locator.locator('img[src*="Bathrooms"]')
            if icon.count() == 0:
                return False
            if not icon.first.is_visible(timeout=2000):
                return False
            box = icon.first.bounding_box()
            return box is not None and box["width"] > 0 and box["height"] > 0
        except Exception:
            return False

    def get_all_bath_counts(self, limit: int = 10):
        """批量获取前 N 张学生公寓卡片的 Bathroom 数量，返回列表（None 表示无图标）"""
        cards = self.get_student_apartment_cards()
        total = cards.count()
        results = []
        for i in range(min(total, limit)):
            bath = self.get_bath_count_from_card(cards.nth(i))
            results.append(bath)
        return results

    def get_bath_count_from_detail_page(self, detail_page):
        """从详情页获取当前房源 Bathroom 数量（录制确认：MainInfo 区 img[src*='Bathrooms'] 旁的 MainInfo_value）"""
        try:
            return detail_page.evaluate("""() => {
                // 详情页顶部 MainInfo 区结构：img.MainInfo_icon[src*='Bathrooms'] + div.MainInfo_value
                // 不能用 room-distance-type-item（推荐卡片区，是其他房源数据）
                const mainInfo = document.querySelector('[class*="MainInfo"]');
                if (mainInfo) {
                    const bathImg = mainInfo.querySelector('img[src*="Bathrooms"]');
                    if (bathImg) {
                        const valueEl = bathImg.nextElementSibling;
                        if (valueEl) return valueEl.innerText.trim();
                    }
                }
                // 兜底：直接查 MainInfo_icon 类的 Bathrooms 图标
                const bathImg = document.querySelector('img[src*="Bathrooms"][class*="MainInfo"]');
                if (bathImg) {
                    const valueEl = bathImg.nextElementSibling;
                    if (valueEl) return valueEl.innerText.trim();
                }
                return null;
            }""")
        except Exception:
            return None

    def is_list_view_active(self):
        """List 按钮是否处于激活状态（active）。等待按钮出现最多10秒。"""
        try:
            btn = self.page.get_by_role("button", name="List")
            btn.wait_for(state="visible", timeout=10000)
            return btn.is_visible()
        except Exception:
            # 降级：按 CSS class 查找（ViewToggle_active 类名表示激活状态）
            try:
                return self.page.locator(
                    "button.ViewToggle_listButton__siNOt, button[class*='listButton']"
                ).is_visible(timeout=5000)
            except Exception:
                return False

    def is_map_view_active(self):
        """地图视图是否激活（URL 含 view=map 或 Map 按钮 active）"""
        return "view=map" in self.page.url

    def click_map_button(self):
        """点击 Map 按钮切换到地图视图，等待 URL 含 view=map"""
        self.page.get_by_role("button", name="Map").click()
        try:
            self.page.wait_for_url("*view=map*", timeout=10000)
        except Exception:
            self.page.wait_for_timeout(2000)

    def click_list_button(self):
        """点击 List 按钮切换回列表视图，等待 URL 不含 view=map"""
        self.page.get_by_role("button", name="List").click()
        try:
            self.page.wait_for_function(
                "() => !window.location.href.includes('view=map')", timeout=10000
            )
        except Exception:
            self.page.wait_for_timeout(2000)

    # ---------- 列表页排序（Sort）----------
    def get_current_sort_text(self):
        """获取当前排序显示文案（如 Best Match、Newest First、Lowest Price、Highest Price）"""
        try:
            for text in ("Best Match", "Newest First", "Lowest Price", "Highest Price"):
                el = self.page.get_by_text(text, exact=True).first
                if el.is_visible(timeout=2000):
                    return text
            return ""
        except Exception:
            return ""

    def is_sort_control_visible(self):
        """排序控件（Sort 或当前排序文案）是否可见"""
        try:
            return (
                self.page.get_by_text("Sort", exact=True).first.is_visible(timeout=2000)
                or bool(self.get_current_sort_text())
            )
        except Exception:
            return False

    def click_sort_button(self):
        """点击排序按钮展开下拉（点击当前排序文案或 Sort）"""
        for text in ("Best Match", "Newest First", "Lowest Price", "Highest Price"):
            try:
                el = self.page.get_by_text(text, exact=True).first
                if el.is_visible(timeout=2000):
                    el.click()
                    self.page.wait_for_timeout(1000)
                    return
            except Exception:
                continue
        try:
            self.page.get_by_text("Sort", exact=True).first.click()
            self.page.wait_for_timeout(1000)
        except Exception:
            raise Exception("未找到可点击的排序按钮")

    def select_sort_option(self, option_name: str):
        """在下拉中选择排序项（如 Newest First、Lowest Price、Highest Price）"""
        self.page.wait_for_timeout(500)
        self.page.get_by_text(option_name, exact=True).first.click()
        self.page.wait_for_timeout(500)

    def click_sort_done(self):
        """点击排序面板 Done 按钮"""
        self.page.locator("button:has-text('Done')").first.click()
        self.page.wait_for_timeout(2000)

    def click_sort_clear(self):
        """点击排序面板 Clear 按钮"""
        self.page.locator("button:has-text('Clear')").first.wait_for(state="visible", timeout=5000)
        self.page.locator("button:has-text('Clear')").first.click()
        self.page.wait_for_timeout(1000)

    # ---------- 列表页分页（Pagination）----------
    def scroll_to_pagination(self, max_scrolls: int = 5, wait_ms: int = 800):
        """滚动到分页区域（多次滚动，等待懒加载的分页组件渲染）

        部分页面的分页组件需要滚动到底部后才会渲染，单次滚动可能不足。
        循环滚动直到页面高度不再增长或达到最大次数。
        """
        last_height = self.page.evaluate("document.body.scrollHeight")
        for _ in range(max_scrolls):
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.page.wait_for_timeout(wait_ms)
            new_height = self.page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def is_pagination_next_visible(self):
        """分页 Next 是否可见（兼容 a 链接和 button，滚动触发懒加载后检测）"""
        try:
            self.scroll_to_pagination()
            # 优先匹配 a:has-text("Next")（录制验证有效）
            loc = self.page.locator('a:has-text("Next")')
            if loc.count() > 0:
                return loc.first.is_visible(timeout=3000)
            # 兜底：button
            loc2 = self.page.get_by_role("button", name="Next")
            if loc2.count() > 0:
                return loc2.first.is_visible(timeout=3000)
            return False
        except Exception:
            return False

    def click_pagination_next(self):
        """点击分页 Next（兼容 a 链接和 button）"""
        self.scroll_to_pagination()
        loc = self.page.locator('a:has-text("Next")')
        if loc.count() > 0:
            loc.first.click()
        else:
            self.page.get_by_role("button", name="Next").first.click()
        self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        self.page.wait_for_timeout(2000)

    def click_pagination_page(self, page_num: int):
        """点击指定页码（兼容 button 和 a 链接）"""
        self.scroll_to_pagination()
        # 优先用 button role（录制验证有效）
        btn = self.page.get_by_role("button", name=str(page_num), exact=True)
        if btn.count() > 0:
            btn.first.click()
        else:
            self.page.locator(f'a:has-text("{page_num}")').first.click()
        self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        self.page.wait_for_timeout(2000)

    def is_pagination_prev_visible(self):
        """分页 Prev 是否可见"""
        try:
            self.scroll_to_pagination()
            return self.page.locator("ul.pagination li.prev a, [class*='pagination'] li.prev a").first.is_visible(timeout=3000)
        except Exception:
            try:
                return self.page.locator("a.page-link").filter(has_text=re.compile(r"Prev", re.I)).first.is_visible(timeout=2000)
            except Exception:
                return False

    def click_pagination_prev(self):
        """点击分页 Prev"""
        self.scroll_to_pagination()
        try:
            self.page.locator("ul.pagination li.prev a, [class*='pagination'] li.prev a").first.click()
        except Exception:
            self.page.locator("a.page-link").filter(has_text=re.compile(r"Prev", re.I)).first.click()
        self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        self.page.wait_for_timeout(2000)

    def get_card_images_quality_status(self, max_cards: int = 5):
        """
        获取前 N 张卡片的图片质量状态（综合检查：加载成功 + 正确渲染）
        返回：[{src, naturalWidth, naturalHeight, complete, width, height, visible, opacity, display, visibility}, ...]
        - 加载成功：naturalWidth/Height > 0 且 complete=True
        - 正确渲染：width/height > 0 且 visible=True
        """
        imgs = self.page.locator("a[href*='cate-'] img")
        n = min(max_cards * 20, imgs.count())
        results = []
        for i in range(n):
            try:
                status = imgs.nth(i).evaluate(
                    """
                    (el) => {
                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);
                        return {
                            src: el.src || '',
                            naturalWidth: el.naturalWidth || 0,
                            naturalHeight: el.naturalHeight || 0,
                            complete: el.complete || false,
                            width: rect.width || 0,
                            height: rect.height || 0,
                            visible: rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden' && parseFloat(style.opacity) > 0,
                            x: rect.x || 0,
                            y: rect.y || 0,
                            opacity: parseFloat(style.opacity) || 1,
                            display: style.display || '',
                            visibility: style.visibility || ''
                        };
                    }
                    """
                )
                results.append(status)
            except Exception:
                pass
        return results[:max_cards * 10]

    # ---------- 列表卡片房产标题（AU 买房列表）----------
    # 业务定义：列表卡片上的「房产标题」= 详情页 Property Introduction 模块的副标题

    # ========== 价格相关方法 ==========

    def get_first_card_price_text(self):
        """获取第一张卡片的价格文本（包含货币符号和周期）"""
        try:
            # 尝试多种卡片定位器（租房、买房、商业地产等）
            first_card = self.page.locator(
                'a[href*="cate-rent-"], '
                'a[href*="cate-property-for-sale-"], '
                'a[href*="residential-"], '
                'a[href*="cate-buy-"], '
                'a[href*="cate-commercial-"]'
            ).first
            first_card.wait_for(state="visible", timeout=5000)
            # 获取卡片全文，从中提取价格信息
            card_text = first_card.inner_text()
            # 使用正则提取价格（A$XXX 或 $XXX 格式，支持负数）
            price_match = re.search(r'A?\$-?[\d,]+(?:\s*(?:\/|per)\s*(?:week|month|year|day))?', card_text, re.IGNORECASE)
            if price_match:
                return price_match.group()
            # 检查是否是 Free 或 Contact for price
            if re.search(r'\bFree\b', card_text, re.IGNORECASE):
                return "Free"
            if re.search(r'Contact for price', card_text, re.IGNORECASE):
                return "Contact for price"
            return ""
        except Exception as e:
            return ""

    def get_card_prices(self, max_cards: int = 5):
        """获取前 N 张卡片的价格列表"""
        cards = self.page.locator(
            'a[href*="cate-rent-"], '
            'a[href*="cate-property-for-sale-"], '
            'a[href*="residential-"], '
            'a[href*="cate-buy-"], '
            'a[href*="cate-commercial-"]'
        )
        count = min(max_cards, cards.count())
        prices = []
        for i in range(count):
            try:
                card = cards.nth(i)
                card_text = card.inner_text()
                # 支持负数价格
                price_match = re.search(r'A?\$-?[\d,]+(?:\s*(?:\/|per)\s*(?:week|month|year|day))?', card_text, re.IGNORECASE)
                if price_match:
                    prices.append(price_match.group())
                elif re.search(r'\bFree\b', card_text, re.IGNORECASE):
                    prices.append("Free")
                elif re.search(r'Contact for price', card_text, re.IGNORECASE):
                    prices.append("Contact for price")
                else:
                    prices.append("")
            except Exception:
                prices.append("")
        return prices

    def is_price_format_valid(self, price_text: str):
        """验证价格格式是否正确（包含货币符号、数字、可能的周期）"""
        import re
        # 匹配格式：A$XXX 或 $XXX，可能包含 /week, per week 等，支持负数
        pattern = r'A?\$-?[\d,]+(\s*(\/|per)\s*(week|month|year|day))?'
        # 或者是 Free / Contact for price
        if price_text in ("Free", "Contact for price"):
            return True
        return bool(re.search(pattern, price_text, re.IGNORECASE))

    def click_first_card_price(self):
        """点击第一张卡片的价格区域（如果价格可点击）"""
        try:
            first_card = self.page.locator('a[href*="cate-rent-"], a[href*="cate-property-for-sale-"], a[href*="residential-"]').first
            # 通常整个卡片都是链接，点击卡片即可
            first_card.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            pass

    # ========== 面积相关方法 ==========

    def get_first_card_area_text(self):
        """获取第一张卡片的面积文本（如 XX sqm、XX m²、XX sq ft）"""
        try:
            first_card = self.page.locator('a[href*="cate-rent-"], a[href*="cate-property-for-sale-"], a[href*="residential-"]').first
            first_card.wait_for(state="visible", timeout=5000)
            card_text = first_card.inner_text()
            area_match = re.search(
                r'[\d,]+\.?\d*\s*(?:sqm|m²|sq\.?\s*m|sq\s*ft|sqft|square\s*metres?)',
                card_text, re.IGNORECASE
            )
            if area_match:
                return area_match.group()
            return ""
        except Exception:
            return ""

    def get_card_areas(self, max_cards: int = 5):
        """获取前 N 张卡片的面积列表"""
        cards = self.page.locator('a[href*="cate-rent-"], a[href*="cate-property-for-sale-"], a[href*="residential-"]')
        count = min(max_cards, cards.count())
        areas = []
        for i in range(count):
            try:
                card = cards.nth(i)
                card_text = card.inner_text()
                area_match = re.search(
                    r'[\d,]+\.?\d*\s*(?:sqm|m²|sq\.?\s*m|sq\s*ft|sqft|square\s*metres?)',
                    card_text, re.IGNORECASE
                )
                if area_match:
                    areas.append(area_match.group())
                else:
                    areas.append("")
            except Exception:
                areas.append("")
        return areas

    def is_area_format_valid(self, area_text: str):
        """验证面积格式是否正确（包含数字和单位）"""
        return bool(re.search(
            r'[\d,]+\.?\d*\s*(?:sqm|m²|sq\.?\s*m|sq\s*ft|sqft|square\s*metres?)',
            area_text, re.IGNORECASE
        ))

    # ========== 位置/邮编相关方法 ==========

    def get_first_card_location_text(self):
        """获取第一张卡片的位置/邮编文本（如 suburb、postcode、ACT 2600）"""
        try:
            first_card = self.page.locator('a[href*="cate-rent-"], a[href*="cate-property-for-sale-"], a[href*="residential-"]').first
            first_card.wait_for(state="visible", timeout=5000)
            card_text = first_card.inner_text()
            # AU 邮编 4 位数字
            postcode_match = re.search(r'\b(\d{4})\b', card_text)
            if postcode_match:
                return postcode_match.group(1)
            # 或 suburb, State 格式（如 Canberra ACT）
            loc_match = re.search(r'([A-Za-z\s\-]+(?:ACT|NSW|VIC|QLD|SA|WA|TAS|NT)\s*\d{4}?)', card_text)
            if loc_match:
                return loc_match.group(1).strip()
            # 或纯 suburb 名称
            lines = [ln.strip() for ln in card_text.split("\n") if ln.strip()]
            for ln in lines:
                if re.match(r"^A\$[\d,]+", ln) or ln == "Free":
                    continue
                if re.match(r"^\d+\s*/\s*\d+$", ln):
                    continue
                if "OKerAU_" in ln or "sqm" in ln or "m²" in ln:
                    continue
                if len(ln) >= 2 and len(ln) <= 80:
                    return ln
            return ""
        except Exception:
            return ""

    def get_card_locations(self, max_cards: int = 5):
        """获取前 N 张卡片的位置/邮编列表"""
        cards = self.page.locator('a[href*="cate-rent-"], a[href*="cate-property-for-sale-"], a[href*="residential-"]')
        count = min(max_cards, cards.count())
        locations = []
        for i in range(count):
            try:
                card = cards.nth(i)
                card_text = card.inner_text()
                postcode_match = re.search(r'\b(\d{4})\b', card_text)
                if postcode_match:
                    locations.append(postcode_match.group(1))
                else:
                    loc_match = re.search(r'([A-Za-z\s\-]+(?:ACT|NSW|VIC|QLD|SA|WA|TAS|NT)\s*\d{4}?)', card_text)
                    if loc_match:
                        locations.append(loc_match.group(1).strip())
                    else:
                        locations.append("")
            except Exception:
                locations.append("")
        return locations

    def is_postcode_format_valid(self, text: str):
        """验证 AU 邮编格式（4 位数字）"""
        return bool(re.search(r'\b\d{4}\b', text))

    # ========== 房产类型相关方法（列表卡片最后一行为类型：House/Unit/Townhomes/Other/Retirement 等）==========

    def _list_card_locator(self, path_part: str = "cate-property-for-rent-"):
        """列表页卡片定位器。租房/买房：仅匹配含 OKerAU_ 或 A$ 的卡片；学生公寓/商业地产等：仅按 href 匹配。

        商业买房（commercial-buy）页面的卡片 href 实际为：
          - cate-commercial-property-for-sale-{subtype}/
          - cate-land-development-sale/
        因此当 path_part 为 "cate-commercial-buy-" 时，改用 cate-commercial-property-for-sale- 匹配。
        """
        if "student" in path_part.lower():
            # 只匹配具体房源卡片（href 含数字 ID），排除城市聚合导航链接
            # 真实房源 href 示例：/cate-property-student-apartment/iglu-xxx-6569330257356510/
            # 聚合链接 href 示例：/en/city-sydney/cate-student-apartment/（无数字 ID，htmlLen≈42）
            return self.page.locator(
                'a[href*="student-apartment"]'
            ).filter(has=self.page.locator('[class*="details"],[class*="prices"],[class*="room-distance"]'))
        # 商业地产买房：实际 href 前缀为 cate-commercial-property-for-sale- 或 cate-land-development-sale
        if path_part == "cate-commercial-buy-":
            return self.page.locator(
                'a[href*="cate-commercial-property-for-sale-"], a[href*="cate-land-development-sale"]'
            )
        if "commercial" in path_part.lower():
            return self.page.locator(f'a[href*="{path_part}"]')
        return self.page.locator(f'a[href*="{path_part}"]').filter(
            has=self.page.locator("text=/OKerAU_|A\\$/")
        )

    def get_first_card_property_type_text(self, path_part: str = "cate-property-for-rent-"):
        """获取第一张卡片的房产类型文本（path_part: 租房/买房/学生公寓/商业地产卖房）。学生公寓时若首卡为空会尝试后续卡片。"""
        from utils.logger import setup_logger
        _logger = setup_logger()
        try:
            # 等待页面主体内容加载稳定
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            except Exception:
                pass

            cards = self._list_card_locator(path_part)

            # 等待至少一张卡片出现（最多15秒）
            try:
                cards.first.wait_for(state="visible", timeout=15000)
            except Exception as e:
                _logger.warning(f"等待卡片可见超时 path_part={path_part}: {e}")
                return ""

            count = cards.count()
            max_try = 15 if "student" in path_part.lower() else (5 if "commercial" in path_part.lower() else 3)
            for i in range(min(max_try, count)):
                try:
                    card = cards.nth(i)
                    card.wait_for(state="visible", timeout=5000)
                    card_text = card.inner_text()
                    lines = [ln.strip() for ln in card_text.split("\n") if ln.strip()]
                    raw = lines[-1] if lines else ""
                    if raw.endswith(" Property Information"):
                        raw = raw.replace(" Property Information", "").strip()
                    if raw:
                        return raw
                except Exception as e:
                    _logger.debug(f"卡片{i} 读取异常: {e}")
                    continue
            return ""
        except Exception as e:
            _logger.warning(f"get_first_card_property_type_text 异常: {e}")
            return ""

    def get_card_property_types(self, max_cards: int = 5, path_part: str = "cate-property-for-rent-"):
        """获取前 N 张卡片的房产类型列表（path_part: 租房/买房/学生公寓/商业地产卖房）。学生公寓时会跳过空文案卡片。"""
        cards = self._list_card_locator(path_part)
        # 等待至少一张卡片出现（最多15秒）
        try:
            cards.first.wait_for(state="visible", timeout=15000)
        except Exception:
            pass
        expand = "student" in path_part.lower() or "commercial" in path_part.lower()
        limit = min(max_cards * 2, cards.count()) if expand else min(max_cards, cards.count())
        types_list = []
        for i in range(limit):
            if len(types_list) >= max_cards:
                break
            try:
                card = cards.nth(i)
                card_text = card.inner_text()
                lines = [ln.strip() for ln in card_text.split("\n") if ln.strip()]
                raw = lines[-1] if lines else ""
                if raw.endswith(" Property Information"):
                    raw = raw.replace(" Property Information", "").strip()
                if ("student" in path_part.lower() or "commercial" in path_part.lower()) and not raw:
                    continue
                types_list.append(raw)
            except Exception:
                types_list.append("")
        return types_list[:max_cards]

    def click_first_list_card_rent(self):
        """点击第一张租房列表卡片（进入详情，可能新开标签）"""
        self._list_card_locator("cate-property-for-rent-").first.click()

    def click_first_list_card(self, path_part: str):
        """点击第一张列表卡片（path_part: cate-property-for-rent- 或 cate-property-for-sale-）"""
        self._list_card_locator(path_part).first.click()

    def is_property_type_valid(self, text: str):
        """验证房产类型文案合理（非空、长度适中或为已知类型）"""
        if not text or not text.strip():
            return False
        if len(text) > 100:
            return False
        known = {
            "house", "unit", "apartment", "townhouse", "townhomes", "villa",
            "other", "retirement", "studio", "apartment&unit",
            "student accommodation",
            # 商业地产卖房实际类型
            "land / development", "land/development",
        }
        return text.strip().lower() in known or bool(re.match(r"^[A-Za-z&/\s]+$", text.strip()))

    def get_first_card_title_text(self):
        """第一张卡片的文案（含标题），用于校验非空与长度（标题来源：详情页 Property Introduction 副标题）"""
        first_card = self.page.locator(
            'a[href*="cate-property-for-sale-"], '
            'a[href*="cate-rent-"], '
            'a[href*="residential-"], '
            'a[href*="cate-buy-"], '
            'a[href*="cate-commercial-"]'
        ).first
        return first_card.inner_text()

    def get_first_card_title_stripped(self):
        """第一张卡片标题区可读文本：取卡片文本中首条非价格/非 agent 的行作为标题近似"""
        raw = self.get_first_card_title_text()
        lines = [ln.strip() for ln in raw.split("\n") if ln.strip()]
        for ln in lines:
            # 匹配价格：A$123, A$-1, A$1,000+, A$500 per day, Free, Contact for price
            if re.match(r"^A\$-?[\d,]+(\+)?(\s+per\s+(day|week|month|year))?$", ln) or re.match(r"^Free$", ln) or "Contact for price" in ln:
                continue
            if re.match(r"^\d+\s*/\s*\d+$", ln):
                continue
            if "OKerAU_" in ln or "agent-avatar" in ln or "fav-icon" in ln:
                continue
            if ln in ("List", "Map", "Filter"):
                continue
            return ln
        return lines[0] if lines else ""

    def get_card_titles_stripped(self, max_cards: int = 5):
        """前 N 张卡片的标题近似文本列表（用于 TC002/TC005）"""
        cards = self.page.locator(
            'a[href*="cate-property-for-sale-"], '
            'a[href*="cate-rent-"], '
            'a[href*="residential-"], '
            'a[href*="cate-buy-"], '
            'a[href*="cate-commercial-"]'
        )
        n = min(max_cards, cards.count())
        result = []
        for i in range(n):
            raw = cards.nth(i).inner_text()
            lines = [ln.strip() for ln in raw.split("\n") if ln.strip()]
            for ln in lines:
                # 匹配价格：A$123, A$-1, A$1,000+, A$500 per day, Free, Contact for price
                if re.match(r"^A\$-?[\d,]+(\+)?(\s+per\s+(day|week|month|year))?$", ln) or ln == "Free" or "Contact for price" in ln:
                    continue
                if re.match(r"^\d+\s*/\s*\d+$", ln):
                    continue
                if "OKerAU_" in ln:
                    continue
                if ln in ("List", "Map", "Filter"):
                    continue
                result.append(ln)
                break
            else:
                result.append(lines[0] if lines else "")
        return result

    def click_first_card_title(self):
        """点击第一张卡片的标题区域进入详情（录制：整卡为 link，点击即进详情）"""
        self.page.locator(
            'a[href*="cate-property-for-sale-"], '
            'a[href*="cate-rent-"], '
            'a[href*="residential-"], '
            'a[href*="cate-buy-"], '
            'a[href*="cate-commercial-"]'
        ).first.click()

    # ─────────────────────────────────────────────
    # 买房列表卡片 Parking（停车位）图标和数量
    # 录制结论：
    #   列表页图标：img.room-distance-type-item-icon[src*="car.png"]
    #   列表页数量：图标父级 .room-distance-type-item > .room-distance-type-item-label
    #   详情页图标：img.MainInfo_icon__kiZFy[src*="parking_space_v1.png"]
    #   详情页数量：图标父级 .MainInfo_item__ZNJ3X > .MainInfo_value__U8n3C
    # ─────────────────────────────────────────────

    def get_buy_cards(self):
        """返回买房列表卡片 locator"""
        return self.page.locator('a[href*="cate-property-for-sale-"]')

    def get_buy_card_count(self):
        """返回买房列表卡片数量"""
        return self.get_buy_cards().count()

    def get_parking_count_from_card(self, card_locator):
        """从卡片 locator 中提取停车位数量文本，无停车位图标则返回 None"""
        try:
            result = card_locator.evaluate("""el => {
                const img = Array.from(el.querySelectorAll('img')).find(
                    i => i.src && i.src.includes('car.png')
                );
                if (!img) return null;
                const label = img.parentElement
                    ? img.parentElement.querySelector('.room-distance-type-item-label')
                    : null;
                return label ? label.innerText.trim() : null;
            }""")
            return result if result else None
        except Exception:
            return None

    def get_parking_icon_visible(self, card_locator):
        """检查卡片中停车位图标是否可见及尺寸"""
        try:
            result = card_locator.evaluate("""el => {
                const img = Array.from(el.querySelectorAll('img')).find(
                    i => i.src && i.src.includes('car.png')
                );
                if (!img) return null;
                const rect = img.getBoundingClientRect();
                return { width: rect.width, height: rect.height, visible: rect.width > 0 && rect.height > 0 };
            }""")
            return result
        except Exception:
            return None

    def get_all_parking_counts(self, max_cards=20):
        """批量获取前 max_cards 张卡片的停车位数量（None 表示无停车位）"""
        cards = self.get_buy_cards()
        total = min(cards.count(), max_cards)
        results = []
        for i in range(total):
            val = self.get_parking_count_from_card(cards.nth(i))
            results.append(val)
        return results

    def get_first_buy_card_href(self):
        """获取第一张有停车位信息的卡片 href"""
        cards = self.get_buy_cards()
        for i in range(min(cards.count(), 20)):
            val = self.get_parking_count_from_card(cards.nth(i))
            if val is not None:
                return cards.nth(i).get_attribute("href")
        return None

    def click_buy_card_by_href(self, href):
        """通过 href 精确点击指定卡片"""
        self.page.locator(f'a[href="{href}"]').first.click()

    def get_parking_count_from_detail_page(self, detail_page):
        """从详情页主信息区提取停车位数量（录制：img[src*='parking_space_v1.png'] 的兄弟 value）"""
        try:
            result = detail_page.evaluate("""() => {
                const items = document.querySelectorAll('.MainInfo_item__ZNJ3X');
                for (const item of items) {
                    const img = item.querySelector('img.MainInfo_icon__kiZFy');
                    if (img && img.src && img.src.includes('parking_space_v1.png')) {
                        const val = item.querySelector('.MainInfo_value__U8n3C');
                        return val ? val.innerText.trim() : null;
                    }
                }
                return null;
            }""")
            return result
        except Exception:
            return None

    # ───────────── 学生公寓列表 - 房间型号相关 ─────────────

    def get_student_apartment_cards(self):
        """返回学生公寓列表卡片 locator"""
        return self.page.locator('a[href*="student-apartment"]')

    def get_student_apartment_card_count(self):
        """返回学生公寓列表卡片数量"""
        return self.get_student_apartment_cards().count()

    def get_room_type_from_card(self, card_locator):
        """从卡片 locator 中提取房间型号文本（无 img 的 .room-distance-type-item）"""
        try:
            result = card_locator.evaluate("""el => {
                const items = el.querySelectorAll('.room-distance-type-item');
                for (const item of items) {
                    if (!item.querySelector('img')) {
                        const label = item.querySelector('.room-distance-type-item-label');
                        if (label) return label.innerText.trim();
                    }
                }
                return null;
            }""")
            return result if result else None
        except Exception:
            return None

    def get_room_type_element_visible(self, card_locator):
        """检查卡片中房间型号文本元素是否可见及其尺寸"""
        try:
            result = card_locator.evaluate("""el => {
                const items = el.querySelectorAll('.room-distance-type-item');
                for (const item of items) {
                    if (!item.querySelector('img')) {
                        const label = item.querySelector('.room-distance-type-item-label');
                        if (label) {
                            const rect = label.getBoundingClientRect();
                            return { width: rect.width, height: rect.height, visible: rect.width > 0 && rect.height > 0 };
                        }
                    }
                }
                return null;
            }""")
            return result
        except Exception:
            return None

    def get_all_room_types(self, max_cards=20):
        """批量获取前 max_cards 张学生公寓卡片的房间型号（None 表示未显示）"""
        cards = self.get_student_apartment_cards()
        total = min(cards.count(), max_cards)
        results = []
        for i in range(total):
            val = self.get_room_type_from_card(cards.nth(i))
            results.append(val)
        return results

    def get_first_student_apartment_card_with_room_type(self):
        """获取第一张有房间型号信息的卡片 href"""
        cards = self.get_student_apartment_cards()
        for i in range(min(cards.count(), 20)):
            val = self.get_room_type_from_card(cards.nth(i))
            if val is not None:
                return cards.nth(i).get_attribute("href")
        return None

    def get_room_type_from_detail_page(self, detail_page):
        """从详情页主信息区提取房间型号（无 img 的 .MainInfo_item__ZNJ3X 内的 .MainInfo_value__U8n3C）"""
        try:
            result = detail_page.evaluate("""() => {
                const items = document.querySelectorAll('.MainInfo_item__ZNJ3X');
                for (const item of items) {
                    const hasImg = item.querySelector('img.MainInfo_icon__kiZFy');
                    if (!hasImg) {
                        const val = item.querySelector('.MainInfo_value__U8n3C');
                        if (val) return val.innerText.trim();
                    }
                }
                return null;
            }""")
            return result
        except Exception:
            return None
