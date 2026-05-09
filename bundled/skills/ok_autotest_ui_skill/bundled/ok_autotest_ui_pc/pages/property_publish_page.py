# pages/property_publish_page.py
"""房产发布页 Page Object"""
from __future__ import annotations

import re
import time
from typing import Union

from playwright.sync_api import Frame, Page, FileChooser
from pages.base_page import BasePage


class PropertyPublishPage(BasePage):
    """房产发布页（支持 AU 等站点发布功能）"""

    def __init__(self, page: Page):
        super().__init__(page)

    def navigate_to_homepage(self, url: str = "https://au.58v5.cn", timeout: int = 30000):
        """打开首页"""
        self.page.goto(url, timeout=timeout, wait_until="domcontentloaded")
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)

    def set_mobile_viewport(self, width: int = 375, height: int = 812):
        """设置移动端视口（发布入口在移动端可见）"""
        self.page.set_viewport_size({"width": width, "height": height})

    def click_menu_dots(self):
        """点击右上角 ··· 菜单（移动端）
        
        注意：页面中可能有多个 ··· 元素，需要定位到顶部导航栏的菜单按钮
        """
        self.page.evaluate("window.scrollTo(0, 0)")
        self.page.wait_for_timeout(500)
        
        menu_btn = self.page.locator("div").filter(has_text="···").nth(3)
        menu_btn.wait_for(state="visible", timeout=10000)
        menu_btn.click()
        self.page.wait_for_timeout(1000)

    def click_post_button_in_tooltip(self):
        """点击 tooltip 中的 Post 按钮
        
        注意：tooltip中包含多个选项（Canberra、English、Favourites、Post、Messages）
        需要精确定位到"Post"文本
        """
        tooltip = self.page.get_by_role("tooltip")
        tooltip.wait_for(state="visible", timeout=5000)
        
        post_btn = tooltip.get_by_text("Post", exact=True)
        post_btn.wait_for(state="visible", timeout=5000)
        post_btn.click()
        
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)

    def get_current_url(self) -> str:
        """获取当前页面URL"""
        return self.page.url

    def is_on_publish_front_page(self) -> bool:
        """是否在发布前置页（二级分类选择页）"""
        return "publish/front" in self.page.url

    def click_secondary_category(self, category_name: str):
        """点击二级分类（如 Property For Rent）
        
        注意：需要等待分类列表加载完成
        """
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self.page.wait_for_timeout(2000)
        
        try:
            category_btn = self.page.locator(f"text={category_name}").first
            category_btn.wait_for(state="visible", timeout=10000)
            category_btn.click(timeout=10000)
        except Exception as e:
            raise Exception(f"点击二级分类失败：{category_name}，错误：{e}")
        
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self.page.wait_for_timeout(1000)

    def is_on_publish_form_page(self) -> bool:
        """是否在发布表单页"""
        return "publish/property" in self.page.url

    def click_tertiary_category(self, category_name: str):
        """点击三级分类按钮（如 House, Apartment&Unit）
        
        注意：需要等待三级分类按钮加载完成
        """
        self.page.wait_for_timeout(1000)
        category_btn = self.page.locator(f"text={category_name}").first
        category_btn.wait_for(state="visible", timeout=10000)
        category_btn.click()
        self.page.wait_for_timeout(1000)

    def get_page_title_text(self) -> str:
        """获取页面标题文本（如 Property For Rent Post）"""
        return self.page.locator("h1").inner_text()

    def is_property_info_section_visible(self) -> bool:
        """Property Info 区域是否可见（兼容文案变化与滚动加载）。

        匹配策略（任一命中即返回 True）：
        1. 标题含 Property Info / Property Details / Property Details 等（大小写不敏感）；
        2. 页面出现 Bedroom / Bathrooms / Bedrooms 等房型字段标签；
        3. 正文含 Bedroom/Bathroom 任意一词。
        """
        page = self.page
        try:
            page.wait_for_load_state("domcontentloaded", timeout=10000)
        except Exception:
            pass
        page.wait_for_timeout(800)

        # 策略1：多种标题文案
        for pat in (
            r"Property\s+Info",
            r"Property\s+Details?",
            r"Property\s+Information",
        ):
            try:
                loc = page.get_by_text(re.compile(pat, re.I))
                if loc.first.is_visible(timeout=3000):
                    return True
            except Exception:
                pass

        # 策略2：卧室/卫浴字段标签
        for pat in (r"Bedrooms?\b", r"Bathrooms?\b", r"Beds?\b"):
            try:
                loc = page.get_by_text(re.compile(pat, re.I))
                if loc.first.is_visible(timeout=2000):
                    return True
            except Exception:
                pass

        # 策略3：页面正文（含 iframe）
        for fr in page.frames:
            try:
                body = fr.evaluate("() => document.body ? document.body.innerText : ''") or ""
                if re.search(r"Bedroom|Bathroom|Beds?\b|Baths?\b", body, re.I):
                    return True
            except Exception:
                continue

        return False

    def _scroll_frame_towards_pictures(self, frame: Frame) -> None:
        """在指定 frame 内将主图 / Pictures 区滚入视口（iframe 内需对 frame 滚动）。"""
        root = self.page
        for pat in (
            r"\bPictures\b",
            r"Main\s*(photo|image|picture)s?\b",
            r"Upload\s*(photo|image|picture)",
        ):
            try:
                frame.get_by_text(re.compile(pat, re.I)).first.scroll_into_view_if_needed(
                    timeout=10000
                )
                root.wait_for_timeout(400)
                return
            except Exception:
                continue
        for _ in range(14):
            try:
                frame.evaluate("() => { try { window.scrollBy(0, 900); } catch (e) {} }")
            except Exception:
                try:
                    root.mouse.wheel(0, 900)
                except Exception:
                    pass
            root.wait_for_timeout(220)

    def _scroll_to_main_pictures_section(self) -> None:
        """主文档 frame：将 Pictures 区滚入视口。"""
        self._scroll_frame_towards_pictures(self.page.main_frame)

    def _apply_files_to_chooser(self, fc: FileChooser, paths: Union[str, list]) -> None:
        if isinstance(paths, list):
            fc.set_files(paths if len(paths) > 1 else paths[0])
        else:
            fc.set_files(paths)

    def _try_upload_single_in_frame(self, frame: Frame, image_path: str, wait_ms: int) -> bool:
        """在单个 frame 内尝试主图上传。成功返回 True。"""
        root = self.page
        self._scroll_frame_towards_pictures(frame)

        # 优先走 file input：不依赖 role=button「Choose File」可见，避免旧版 .first.click 长超时
        files = frame.locator('input[type="file"]')
        n_inp = files.count()
        if n_inp >= 1:
            for idx in range(min(n_inp, 8)):
                try:
                    files.nth(idx).set_input_files(image_path, timeout=15000)
                    root.wait_for_timeout(wait_ms)
                    return True
                except Exception:
                    continue

        try:
            sec = frame.locator("div, section, form, article").filter(
                has=frame.get_by_text(re.compile(r"Pictures", re.I))
            ).first
            if sec.is_visible(timeout=5000):
                cfs = sec.get_by_role("button", name=re.compile(r"Choose File", re.I))
                for i in range(min(cfs.count(), 8)):
                    b = cfs.nth(i)
                    if b.is_visible(timeout=2000):
                        with root.expect_file_chooser(timeout=25000) as fc_info:
                            b.scroll_into_view_if_needed(timeout=10000)
                            try:
                                b.click(timeout=8000)
                            except Exception:
                                b.click(timeout=8000, force=True)
                        self._apply_files_to_chooser(fc_info.value, image_path)
                        root.wait_for_timeout(wait_ms)
                        return True
        except Exception:
            pass

        try:
            all_cf = frame.get_by_role("button", name=re.compile(r"Choose File", re.I))
            for i in range(min(all_cf.count(), 12)):
                b = all_cf.nth(i)
                if b.is_visible(timeout=2000):
                    with root.expect_file_chooser(timeout=25000) as fc_info:
                        b.scroll_into_view_if_needed(timeout=10000)
                        try:
                            b.click(timeout=8000)
                        except Exception:
                            b.click(timeout=8000, force=True)
                    self._apply_files_to_chooser(fc_info.value, image_path)
                    root.wait_for_timeout(wait_ms)
                    return True
        except Exception:
            pass

        return False

    def _scroll_frame_towards_floor_plan(self, frame: Frame) -> None:
        """将户型图区块滚入视口（iframe 内需对 frame 滚动；懒加载表单常见）。"""
        root = self.page
        for pat in (
            r"Floor\s*plan",
            r"floor\s*plans",
            r"户型",
            r"Upload\s+floor",
            r"AI\s+will\s+automatically\s+identify",
        ):
            try:
                frame.get_by_text(re.compile(pat, re.I)).first.scroll_into_view_if_needed(
                    timeout=8000
                )
                root.wait_for_timeout(350)
                return
            except Exception:
                continue
        for _ in range(12):
            try:
                frame.evaluate("() => { try { window.scrollBy(0, 850); } catch (e) {} }")
            except Exception:
                try:
                    root.mouse.wheel(0, 850)
                except Exception:
                    pass
            root.wait_for_timeout(200)

    def _try_upload_floor_plan_in_frame(self, frame: Frame, image_path: str, wait_ms: int) -> bool:
        """单 frame 内尝试户型图上传（与录制 nth(1) 相比兼容 iframe / 仅 1 个按钮 / 仅 file input）。"""
        root = self.page
        choose_re = re.compile(r"Choose File", re.I)
        upload_btn_re = re.compile(
            r"Choose File|Upload\s*photos?|Add\s+photos?|^Upload$|Upload\s+image",
            re.I,
        )
        self._scroll_frame_towards_floor_plan(frame)

        floor_sec = None
        try:
            cand = frame.locator("div, section, form, article").filter(
                has=frame.get_by_text(re.compile(r"floor\s*plan|户型|Upload\s+floor", re.I))
            ).first
            if cand.is_visible(timeout=4000):
                floor_sec = cand
        except Exception:
            floor_sec = None

        # 1) 户型区块内 Choose File
        if floor_sec is not None:
            try:
                cfs = floor_sec.get_by_role("button", name=choose_re)
                for i in range(min(cfs.count(), 8)):
                    b = cfs.nth(i)
                    try:
                        if not b.is_visible(timeout=2500):
                            continue
                        with root.expect_file_chooser(timeout=20000) as fc_info:
                            b.scroll_into_view_if_needed(timeout=8000)
                            try:
                                b.click(timeout=10000)
                            except Exception:
                                b.click(timeout=10000, force=True)
                        self._apply_files_to_chooser(fc_info.value, image_path)
                        root.wait_for_timeout(wait_ms)
                        return True
                    except Exception:
                        continue
            except Exception:
                pass

            # 1b) 户型区块内 Upload / Add photo（线上可能不叫 Choose File）
            try:
                ups = floor_sec.get_by_role("button", name=upload_btn_re)
                for i in range(min(ups.count(), 10)):
                    b = ups.nth(i)
                    try:
                        if not b.is_visible(timeout=2000):
                            continue
                        with root.expect_file_chooser(timeout=20000) as fc_info:
                            b.scroll_into_view_if_needed(timeout=8000)
                            try:
                                b.click(timeout=10000)
                            except Exception:
                                b.click(timeout=10000, force=True)
                        self._apply_files_to_chooser(fc_info.value, image_path)
                        root.wait_for_timeout(wait_ms)
                        return True
                    except Exception:
                        continue
            except Exception:
                pass

            # 1c) 户型区块内 file input（避免与整页序错乱）
            try:
                fin_sec = floor_sec.locator('input[type="file"]')
                for idx in range(min(fin_sec.count(), 6)):
                    try:
                        fin_sec.nth(idx).set_input_files(image_path, timeout=15000)
                        root.wait_for_timeout(wait_ms)
                        return True
                    except Exception:
                        continue
            except Exception:
                pass

        # 2) 常见：首张图为 Pictures，第二张 input 为户型图
        try:
            files = frame.locator('input[type="file"]')
            n_inp = files.count()
            if n_inp >= 2:
                for idx in range(1, min(n_inp, 10)):
                    try:
                        files.nth(idx).set_input_files(image_path, timeout=15000)
                        root.wait_for_timeout(wait_ms)
                        return True
                    except Exception:
                        continue
        except Exception:
            pass

        # 3) 全局 Choose File：录制曾用 nth(1)，线上可能仅有 1 个可见或顺序变化 → 收集可见再试
        try:
            cfs = frame.get_by_role("button", name=choose_re)
            visible_idx: list[int] = []
            for i in range(min(cfs.count(), 16)):
                try:
                    if cfs.nth(i).is_visible(timeout=1800):
                        visible_idx.append(i)
                except Exception:
                    continue
            order: list[int] = []
            if len(visible_idx) >= 2:
                order.append(visible_idx[1])
            order.extend(i for i in visible_idx if i not in order)
            if len(visible_idx) == 1:
                order.append(visible_idx[0])
            for idx in order:
                b = cfs.nth(idx)
                try:
                    with root.expect_file_chooser(timeout=20000) as fc_info:
                        b.scroll_into_view_if_needed(timeout=8000)
                        try:
                            b.click(timeout=10000)
                        except Exception:
                            b.click(timeout=10000, force=True)
                    self._apply_files_to_chooser(fc_info.value, image_path)
                    root.wait_for_timeout(wait_ms)
                    return True
                except Exception:
                    continue
        except Exception:
            pass

        return False

    def upload_single_image(self, image_path: str, wait_ms: int = 2000):
        """上传单张图片（主图区）。

        优先点击 Pictures 区块内「首个可见」的 Choose File；避免 `.first` 命中隐藏或非主图区按钮导致超时。
        失败则对 ``input[type=file]`` 使用 ``set_input_files``。
        遍历 **所有 frame**（发布表单常在 iframe，仅搜主 frame 会超时）。
        """
        last_err: Union[BaseException, None] = None
        for fr in self.page.frames:
            try:
                if self._try_upload_single_in_frame(fr, image_path, wait_ms):
                    return
            except BaseException as e:
                last_err = e
                continue
        raise RuntimeError(
            "未找到主图上传入口（各 frame 内 Pictures 区 Choose File 或 input[type=file]）"
        ) from last_err

    def upload_media_file(self, file_path: str, wait_ms: int = 2000):
        """主媒体区上传单个文件（图片或站点允许的 mp4 等，语义上与 upload_single_image 相同入口）。"""
        self.upload_single_image(file_path, wait_ms=wait_ms)

    def upload_main_images_via_file_chooser(self, paths: list, wait_ms: int = 8000):
        """主图区一次选择多文件上传（paths 为绝对路径列表）。

        用于边界测试：避免对同一物理路径连续多次上传被前端去重或状态异常。
        """
        if not paths:
            return
        root = self.page
        payload = paths if len(paths) > 1 else paths[0]
        last_err: Union[BaseException, None] = None
        for fr in self.page.frames:
            self._scroll_frame_towards_pictures(fr)
            try:
                fin = fr.locator('input[type="file"]')
                if fin.count() >= 1:
                    fin.first.set_input_files(payload, timeout=15000)
                    root.wait_for_timeout(wait_ms)
                    return
            except Exception as e:
                last_err = e
            try:
                sec = fr.locator("div, section, form, article").filter(
                    has=fr.get_by_text(re.compile(r"Pictures", re.I))
                ).first
                if sec.is_visible(timeout=5000):
                    cfs = sec.get_by_role("button", name=re.compile(r"Choose File", re.I))
                    for i in range(min(cfs.count(), 8)):
                        b = cfs.nth(i)
                        if b.is_visible(timeout=2000):
                            with root.expect_file_chooser(timeout=25000) as fc_info:
                                b.scroll_into_view_if_needed(timeout=10000)
                                try:
                                    b.click(timeout=8000)
                                except Exception:
                                    b.click(timeout=8000, force=True)
                            self._apply_files_to_chooser(fc_info.value, paths)
                            root.wait_for_timeout(wait_ms)
                            return
            except Exception as e:
                last_err = e
            try:
                all_cf = fr.get_by_role("button", name=re.compile(r"Choose File", re.I))
                for i in range(min(all_cf.count(), 12)):
                    b = all_cf.nth(i)
                    if b.is_visible(timeout=2000):
                        with root.expect_file_chooser(timeout=25000) as fc_info:
                            b.scroll_into_view_if_needed(timeout=10000)
                            try:
                                b.click(timeout=8000)
                            except Exception:
                                b.click(timeout=8000, force=True)
                        self._apply_files_to_chooser(fc_info.value, paths)
                        root.wait_for_timeout(wait_ms)
                        return
            except Exception as e:
                last_err = e
        raise RuntimeError("未找到主图多文件上传入口")

    @staticmethod
    def _js_find_n_slash_20_once() -> str:
        """在 document 上深度遍历（含 Shadow DOM）查找首个 n/20 片段；仅单次调用，勿放入高频轮询。"""
        return """() => {
          const re = /\\b\\d+\\s*\\/\\s*20\\b/;
          const found = [];
          const walk = (node) => {
            if (!node) return;
            if (node.nodeType === Node.TEXT_NODE) {
              const t = node.nodeValue || '';
              const m = t.match(re);
              if (m) found.push(m[0]);
            }
            if (node.shadowRoot) walk(node.shadowRoot);
            for (const c of node.childNodes) walk(c);
          };
          walk(document.documentElement || document.body);
          return found.length ? found[0] : '';
        }"""

    def count_main_media_thumbnails(self) -> int:
        """主图区已上传缩略图数量（首个 Choose File 祖先容器内 img 数，计数文案缺失时兜底）。

        使用与 upload 相同的可访问名定位按钮，避免纯 textContent 与按钮实际子节点不一致。
        """
        try:
            cf = self.page.get_by_role("button", name="Choose File").first
            cf.wait_for(state="visible", timeout=5000)
            n = cf.evaluate(
                """(btn) => {
                  let el = btn.parentElement;
                  let best = 0;
                  for (let i = 0; i < 45 && el; i++) {
                    const k = el.querySelectorAll("img").length;
                    if (k > best) best = k;
                    el = el.parentElement;
                  }
                  return best;
                }"""
            )
            return int(n) if n is not None else -1
        except Exception:
            return -1

    def get_upload_count_text(self, timeout_ms: int = 20000) -> str:
        """获取主图区上传计数器文本（如 1/20，已去掉空格）。

        先各 frame 做一次含 Shadow 的深度文本扫描；再轮询 innerText / Choose File 祖先链（轻量）。
        """
        js_once = self._js_find_n_slash_20_once()
        for frame in self.page.frames:
            try:
                raw = frame.evaluate(js_once)
                if raw:
                    return re.sub(r"\s+", "", str(raw).strip())
            except Exception:
                continue

        deadline = time.monotonic() + timeout_ms / 1000.0
        while time.monotonic() < deadline:
            try:
                choose = self.page.get_by_role("button", name="Choose File").first
                if choose.is_visible(timeout=1500):
                    raw = choose.evaluate(
                        """(btn) => {
                          let el = btn;
                          for (let i = 0; i < 30 && el; i++) {
                            const t = el.innerText || '';
                            const m = t.match(/\\b\\d+\\s*\\/\\s*20\\b/);
                            if (m) return m[0];
                            el = el.parentElement;
                          }
                          return '';
                        }"""
                    )
                    if raw:
                        return re.sub(r"\s+", "", str(raw).strip())
            except Exception:
                pass
            raw = self.page.evaluate(
                """() => {
                  const t = document.body.innerText || '';
                  const m = t.match(/\\b\\d+\\s*\\/\\s*20\\b/);
                  return m ? m[0] : '';
                }"""
            )
            if raw:
                return re.sub(r"\s+", "", str(raw).strip())
            self.page.wait_for_timeout(250)
        raise TimeoutError("未找到主图区 n/20 计数")

    def is_main_label_visible(self) -> bool:
        """是否显示 Main 标签（第一张图片）"""
        try:
            return self.page.get_by_role("button", name="Main").is_visible(timeout=3000)
        except Exception:
            return False

    def get_selected_category(self) -> str:
        """获取当前选中的三级分类（通过检查黑色背景或 active 状态）
        
        注意：AI识图可能自动切换分类
        """
        self.page.wait_for_timeout(500)
        categories = ["House", "Townhomes", "Apartment&Unit", "Villa", "Retirement", "Other"]
        for cat in categories:
            try:
                elem = self.page.locator(f"text={cat}").first
                if elem.is_visible(timeout=1000):
                    bg_color = elem.evaluate("el => window.getComputedStyle(el).backgroundColor")
                    if bg_color and ("0, 0, 0" in bg_color or "rgb(0, 0, 0)" in bg_color):
                        return cat
            except Exception:
                continue
        return ""

    def upload_multiple_images(self, image_paths: list, wait_ms: int = 2000):
        """批量上传多张图片
        
        Args:
            image_paths: 图片文件绝对路径列表
            wait_ms: 每次上传后等待时间（毫秒）
        """
        for image_path in image_paths:
            self.upload_single_image(image_path, wait_ms=wait_ms)

    def upload_floor_plan(self, image_path: str, wait_ms: int = 2000):
        """上传户型图

        旧实现仅在主 document 上 ``Choose File.nth(1).click()``：表单在 iframe、仅 1 个按钮或
        顺序变化时会 30s 超时。现与 ``upload_single_image`` 一致遍历各 frame，并优先户型区块内按钮 /
        第二枚 ``input[type=file]``。
        """
        last_err: Union[BaseException, None] = None
        for fr in self.page.frames:
            try:
                if self._try_upload_floor_plan_in_frame(fr, image_path, wait_ms):
                    return
            except BaseException as e:
                last_err = e
                continue
        raise RuntimeError(
            "未找到户型图上传入口（各 frame 内 Floor plan 区 Choose File 或多枚 input[type=file]）"
        ) from last_err

    def get_floor_plan_count_text(self) -> str:
        """获取户型图上传计数器文本（如 1/10）"""
        return self.page.locator("text=/\\d+\\/10/").inner_text()

    def is_floor_plan_tip_visible(self) -> bool:
        """是否显示户型图提示文案"""
        try:
            tip_text = "Upload floor plans, and AI will automatically identify and fill in property details for you."
            return self.page.get_by_text(tip_text).is_visible(timeout=3000)
        except Exception:
            return False

    def click_post_button(self, wait_ms: int = 2000):
        """点击发布表单底部 Post 提交按钮（处理 dy-group 等浮层遮挡）"""
        post = self.page.get_by_role("button", name="Post")
        post.scroll_into_view_if_needed(timeout=15000)
        self.page.wait_for_timeout(400)
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(400)
        try:
            post.click(timeout=8000)
        except Exception:
            post.click(force=True, timeout=10000)
        self.page.wait_for_timeout(wait_ms)

    def _first_main_area_preview_element(self):
        """主图区首张预览图 ElementHandle（排除户型图区：户型在「Floor plan」标题下方）。

        仅在与户型图缩略图共存时使用；用几何位置分割，避免误点户型区首张图。
        """
        handle = self.page.evaluate_handle(
            r"""() => {
            const floorSectionTopY = () => {
                let best = Infinity;
                for (const el of document.querySelectorAll('div,span,h3,h4,p,label,strong')) {
                    const t = (el.textContent || '').trim().split('\n')[0].trim();
                    if (!/^Floor\s*plan\b/i.test(t)) continue;
                    if (t.length > 48) continue;
                    const r = el.getBoundingClientRect();
                    const st = window.getComputedStyle(el);
                    if (r.width < 8 || r.height < 4) continue;
                    if (st.display === 'none' || st.visibility === 'hidden') continue;
                    if (r.top < best) best = r.top;
                }
                return best === Infinity ? Infinity : best;
            };
            const floorY = floorSectionTopY();
            const isBad = (img) => {
                const s = img.getAttribute('src') || '';
                if (s.includes('icon-upload') || s.includes('static/media')) return true;
                if (s.startsWith('data:image') && s.includes('svg')) return true;
                return false;
            };
            const imgs = [...document.querySelectorAll('img')].filter((img) => {
                if (isBad(img)) return false;
                const s = img.getAttribute('src') || '';
                if (s.includes('blob:')) return true;
                if (s.startsWith('data:image') && !s.includes('svg')) return true;
                const r = img.getBoundingClientRect();
                return r.width >= 28 && r.height >= 28;
            });
            let candidates = imgs;
            if (floorY < Infinity) {
                candidates = candidates.filter(
                    (img) => img.getBoundingClientRect().top < floorY - 8
                );
            }
            candidates = candidates.filter((img) => {
                const r = img.getBoundingClientRect();
                return r.width > 2 && r.height > 2;
            });
            candidates.sort(
                (a, b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top
            );
            return candidates[0] || null;
        }"""
        )
        return handle.as_element()

    def _floor_plan_upload_count_positive(self) -> bool:
        try:
            t = self.get_floor_plan_count_text().strip()
            m = re.match(r"^(\d+)\s*/\s*10", t)
            return bool(m and int(m.group(1)) > 0)
        except Exception:
            return False

    def _locator_main_row_cover_image(self):
        """Main 标签所在缩略条上的首张真实预览图（blob 或 png/jpeg/webp data）。"""
        main_btn = self.page.get_by_role("button", name="Main")
        host = main_btn.locator("xpath=ancestor::*[.//img][1]")
        for sel in (
            "img[src*='blob:']",
            "img[src*='data:image/png']",
            "img[src*='data:image/jpeg']",
            "img[src*='data:image/jpg']",
            "img[src*='data:image/webp']",
        ):
            loc = host.locator(sel).first
            try:
                if loc.is_visible(timeout=1200):
                    return loc
            except Exception:
                continue
        return host.locator("img[src*='blob:']").first

    def _main_row_delete_locator(self):
        """Main 缩略条容器内的删除按钮（避免全局 .first 点到户型区等）。

        host 取「同时含 Main 与 blob 预览图」的块，比单一 ancestor 更易包住浮层/Portal 挂载点。
        """
        host = (
            self.page.locator("div")
            .filter(has=self.page.get_by_role("button", name="Main"))
            .filter(
                has=self.page.locator(
                    "img[src*='blob:'], img[src*='data:image/png'], img[src*='data:image/jpeg']"
                )
            )
            .first
        )
        return (
            host.locator("button[aria-label*='delete' i]")
            .or_(host.locator("button[aria-label*='remove' i]"))
            .or_(host.locator("button[title*='delete' i]"))
            .or_(host.get_by_role("button", name=re.compile(r"delete|remove", re.I)))
            .or_(host.locator("svg[class*='delete']").locator(".."))
            .or_(host.locator("[class*='delete'][class*='icon']"))
            .or_(host.locator("[class*='Delete'][class*='icon']"))
        )

    def _dom_click_delete_near_main_badge(self) -> bool:
        """从「Main」按钮向上扩层，在含主图预览的节点子树内查找删除类控件并点击。"""
        return bool(
            self.page.evaluate(
                r"""() => {
                const norm = (s) => (s || '').replace(/\s+/g, ' ').trim();
                const mainBtn = [...document.querySelectorAll('button')].find(
                    (b) => norm(b.textContent) === 'Main'
                );
                if (!mainBtn) return false;
                let root = mainBtn;
                for (let depth = 0; depth < 22 && root; depth++) {
                    const imgs = root.querySelectorAll(
                        'img[src*="blob:"], img[src^="data:image/png"], img[src^="data:image/jpeg"], img[src^="data:image/jpg"]'
                    );
                    for (const img of imgs) {
                        const src = img.getAttribute('src') || '';
                        if (src.includes('svg')) continue;
                        let el = img;
                        for (let i = 0; i < 14 && el; i++) {
                            const cand = el.querySelectorAll(
                                'button, [role="button"], span[role="button"], div[role="button"]'
                            );
                            for (const b of cand) {
                                const lab = (
                                    (b.getAttribute('aria-label') || '') +
                                    (b.title || '') +
                                    (b.innerText || '') +
                                    (b.className || '')
                                ).toLowerCase();
                                if (
                                    lab.includes('delete') ||
                                    lab.includes('remove') ||
                                    lab.includes('trash') ||
                                    lab.includes('close') ||
                                    lab.includes('icon-close')
                                ) {
                                    b.click();
                                    return true;
                                }
                            }
                            el = el.parentElement;
                        }
                    }
                    root = root.parentElement;
                }
                return false;
            }"""
            )
        )

    def delete_first_image(self):
        """删除主图区第一张已上传缩略图（主图）
        
        仅匹配 blob:/data: 等真实预览图；与户型图共存时只删主图区（Floor plan 上方），避免误删户型缩略图。
        """
        self.page.wait_for_timeout(1000)
        try:
            self.page.get_by_text("Pictures", exact=False).first.scroll_into_view_if_needed(
                timeout=5000
            )
        except Exception:
            pass
        self.page.wait_for_timeout(400)

        use_main_only = self._floor_plan_upload_count_positive()
        first_el = None
        first_image = None
        main_hovered = False
        try:
            if self.is_main_label_visible():
                tv = self._locator_main_row_cover_image()
                tv.scroll_into_view_if_needed(timeout=8000)
                bx = tv.bounding_box()
                if bx:
                    self.page.mouse.move(
                        bx["x"] + bx["width"] / 2,
                        bx["y"] + bx["height"] / 2,
                    )
                    self.page.wait_for_timeout(500)
                tv.hover(force=True, timeout=10000)
                self.page.wait_for_timeout(800)
                main_hovered = True
        except Exception:
            pass

        if not main_hovered:
            if use_main_only:
                first_el = self._first_main_area_preview_element()
                if not first_el:
                    raise Exception("未找到已上传的图片")
                try:
                    first_el.evaluate(
                        "el => el && el.scrollIntoView({ block: 'center', inline: 'nearest' })"
                    )
                except Exception:
                    pass
                self.page.wait_for_timeout(400)
                box = first_el.bounding_box()
                if box:
                    self.page.mouse.move(
                        box["x"] + box["width"] / 2,
                        box["y"] + box["height"] / 2,
                    )
                    self.page.wait_for_timeout(500)
                try:
                    first_el.hover(force=True, timeout=10000)
                except Exception:
                    first_el.evaluate(
                        """(el) => {
                        if (!el) return;
                        ['mouseenter', 'mouseover', 'mousemove'].forEach((t) =>
                            el.dispatchEvent(
                                new MouseEvent(t, { bubbles: true, cancelable: true, view: window })
                            )
                        );
                    }"""
                    )
                self.page.wait_for_timeout(800)
            else:
                uploaded_images = self.page.locator("img[src*='blob:']").or_(
                    self.page.locator("img[src*='data:image/png']")
                ).or_(self.page.locator("img[src*='data:image/jpeg']")).or_(
                    self.page.locator("img[src*='data:image/jpg']")
                ).or_(self.page.locator("img[src*='data:image/webp']"))
                if uploaded_images.count() == 0:
                    uploaded_images = self.page.locator("img").filter(
                        has_not=self.page.locator("[src*='icon-upload']")
                    ).filter(
                        has_not=self.page.locator("[src*='static/media']")
                    ).filter(
                        has_not=self.page.locator("[src*='image/svg+xml']")
                    )
                if uploaded_images.count() == 0:
                    raise Exception("未找到已上传的图片")
                first_image = uploaded_images.first
                first_image.scroll_into_view_if_needed(timeout=5000)
                try:
                    b2 = first_image.bounding_box()
                    if b2:
                        self.page.mouse.move(
                            b2["x"] + b2["width"] / 2,
                            b2["y"] + b2["height"] / 2,
                        )
                        self.page.wait_for_timeout(500)
                except Exception:
                    pass
                first_image.hover(force=True, timeout=10000)
                self.page.wait_for_timeout(800)

        page_del = (
            self.page.locator("button[aria-label*='delete' i]")
            .or_(self.page.locator("button[aria-label*='remove' i]"))
            .or_(self.page.locator("button[title*='delete' i]"))
            .or_(self.page.get_by_role("button", name=re.compile(r"delete|remove", re.I)))
            .or_(self.page.locator("svg[class*='delete']").locator(".."))
            .or_(self.page.locator("[class*='delete'][class*='icon']"))
            .or_(self.page.locator("[class*='Delete'][class*='icon']"))
        )
        delete_btn = (
            self._main_row_delete_locator()
            if self.is_main_label_visible()
            else page_del
        )
        try:
            delete_btn.first.click(timeout=8000, force=True)
        except Exception:
            pass
        self.page.wait_for_timeout(1200)
        if use_main_only:
            self._dom_click_delete_near_main_badge()
            self.page.wait_for_timeout(1000)

        clicked = self.page.evaluate(
            """({ restrictToMain }) => {
                const floorSectionTopY = () => {
                    let best = Infinity;
                    for (const el of document.querySelectorAll('div,span,h3,h4,p,label,strong')) {
                        const t = (el.textContent || '').trim().split('\\n')[0].trim();
                        if (!/^Floor\\s*plan\\b/i.test(t)) continue;
                        if (t.length > 48) continue;
                        const r = el.getBoundingClientRect();
                        const st = window.getComputedStyle(el);
                        if (r.width < 8 || r.height < 4) continue;
                        if (st.display === 'none' || st.visibility === 'hidden') continue;
                        if (r.top < best) best = r.top;
                    }
                    return best === Infinity ? Infinity : best;
                };
                const floorY = restrictToMain ? floorSectionTopY() : Infinity;
                const isBad = (img) => {
                    const s = img.getAttribute('src') || '';
                    if (s.includes('icon-upload') || s.includes('static/media')) return true;
                    if (s.startsWith('data:image') && s.includes('svg')) return true;
                    return false;
                };
                const imgs = [...document.querySelectorAll('img')].filter((img) => {
                    if (isBad(img)) return false;
                    const s = img.getAttribute('src') || '';
                    if (s.includes('blob:')) return true;
                    if (s.startsWith('data:image') && !s.includes('svg')) return true;
                    const r = img.getBoundingClientRect();
                    return r.width >= 28 && r.height >= 28;
                });
                let candidates = imgs;
                if (floorY < Infinity) {
                    candidates = candidates.filter(
                        (img) => img.getBoundingClientRect().top < floorY - 8
                    );
                }
                candidates.sort(
                    (a, b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top
                );
                const img = candidates[0];
                if (!img) return false;
                const tryClickDelete = (root) => {
                    const tryAnt = (container) => {
                        if (!container || !container.querySelectorAll) return false;
                        const sels = [
                            '.anticon-delete',
                            '.anticon-close',
                            '.anticon-close-circle',
                            '[class*="DeleteOutlined"]',
                            '[class*="delete-outlined"]',
                            '[data-testid*="delete" i]',
                            '[data-testid*="remove" i]',
                        ];
                        for (const sel of sels) {
                            const n = container.querySelector(sel);
                            if (n) {
                                const btn = n.closest('button, [role="button"], a') || n;
                                btn.click();
                                return true;
                            }
                        }
                        return false;
                    };
                    let el = root;
                    for (let depth = 0; depth < 14 && el; depth++) {
                        if (tryAnt(el)) return true;
                        const btns = el.querySelectorAll
                            ? el.querySelectorAll('button, [role="button"]')
                            : [];
                        for (const b of btns) {
                            const label = (
                                (b.getAttribute('aria-label') || '') +
                                (b.title || '') +
                                (b.innerText || '')
                            ).toLowerCase();
                            const cls = String(b.className || '').toLowerCase();
                            if (
                                label.includes('delete') ||
                                label.includes('remove') ||
                                label.includes('trash') ||
                                cls.includes('delete') ||
                                cls.includes('trash') ||
                                cls.includes('icon-close')
                            ) {
                                b.click();
                                return true;
                            }
                        }
                        el = el.parentElement;
                    }
                    const card =
                        img.closest('li') ||
                        img.closest('[class*="list-item"]') ||
                        img.closest('[class*="upload"]') ||
                        img.parentElement;
                    if (card && tryAnt(card)) return true;
                    return false;
                };
                if (tryClickDelete(img)) return true;
                {
                    const r = img.getBoundingClientRect();
                    const pts = [
                        [r.right - 10, r.top + 10],
                        [r.right - 6, r.top + 14],
                        [r.right - 14, r.top + 8],
                    ];
                    for (const [x, y] of pts) {
                        const hit = document.elementFromPoint(x, y);
                        const btn =
                            hit &&
                            hit.closest &&
                            hit.closest('button, [role="button"], a[href="#"]');
                        if (btn) {
                            btn.click();
                            return true;
                        }
                    }
                }
                const local =
                    img.closest('li') ||
                    img.closest('[class*="list-item"]') ||
                    img.closest('[class*="item"]') ||
                    img.parentElement;
                if (local) {
                    for (const b of local.querySelectorAll('button, [role="button"]')) {
                        const label = (
                            (b.getAttribute('aria-label') || '') + b.innerText
                        ).toLowerCase();
                        const cls = String(b.className || '').toLowerCase();
                        if (
                            label.includes('delete') ||
                            label.includes('remove') ||
                            /close|×/i.test(label) ||
                            cls.includes('delete') ||
                            cls.includes('trash')
                        ) {
                            b.click();
                            return true;
                        }
                    }
                }
                const picturesBlock = [...document.querySelectorAll('div')].find(
                    (d) =>
                        d.innerText &&
                        d.innerText.includes('Pictures') &&
                        d.querySelector('img')
                );
                if (picturesBlock) {
                    for (const b of picturesBlock.querySelectorAll('button, [role="button"]')) {
                        if (floorY < Infinity) {
                            const br = b.getBoundingClientRect();
                            if (br.top >= floorY - 4) continue;
                        }
                        const label = (
                            (b.getAttribute('aria-label') || '') + b.innerText
                        ).toLowerCase();
                        const cls = String(b.className || '').toLowerCase();
                        if (
                            label.includes('delete') ||
                            label.includes('remove') ||
                            /close|×/i.test(label) ||
                            cls.includes('delete') ||
                            cls.includes('trash')
                        ) {
                            b.click();
                            return true;
                        }
                    }
                }
                return false;
            }""",
            {"restrictToMain": use_main_only},
        )
        self.page.wait_for_timeout(800)
        if not clicked:
            try:
                if self.is_main_label_visible():
                    self._locator_main_row_cover_image().evaluate(
                        "(el) => { if (el) { el.setAttribute('tabindex','-1'); el.focus(); } }"
                    )
                elif use_main_only and first_el is not None:
                    first_el.evaluate(
                        "(el) => { if (el) { el.setAttribute('tabindex','-1'); el.focus(); } }"
                    )
                elif first_image is not None:
                    first_image.evaluate(
                        "(el) => { if (el) { el.setAttribute('tabindex','-1'); el.focus(); } }"
                    )
                self.page.wait_for_timeout(200)
                self.page.keyboard.press("Delete")
            except Exception:
                pass
        self.page.wait_for_timeout(2000)
