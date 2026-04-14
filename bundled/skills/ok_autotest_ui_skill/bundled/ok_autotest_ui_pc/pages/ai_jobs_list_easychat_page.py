# pages/ai_jobs_list_easychat_page.py
"""
Jobs 列表页 EasyChat AI 开关 Page Object

对应页面：https://aepub.58v5.cn/biz/en/publish/list（Jobs Tab）
实测结构（2026-03-18）：
  - 卡片右上角：paragraph > img + "EasyChat On" 文字（AI 开启时显示）
  - 卡片底部：paragraph > img + "EasyChat Settings" 按钮
  - 卡片右下角："..." 更多菜单按钮
  - 弹窗：div.modal-content（非原生 dialog 标签）
    - 关闭按钮：img[class*='pc_close_icon']（img 非 button）
    - Toggle 开关：img[class*='switchIcon']（src 含 checked=ON，unchecked=OFF）
    - 标题：div[class*='pc_title']
    - 描述：p[class*='description']
"""
from pages.base_page import BasePage
from utils.logger import setup_logger


class AiJobsListEasyChatPage(BasePage):
    """Jobs 列表页 EasyChat AI 开关相关操作（静默执行，无断言，无 INFO 日志）"""

    # -------- 列表页选择器 --------
    _JOBS_TAB = "text=Jobs"
    _LIST_CONTAINER = "role=list"
    # 实测：EasyChat Settings 按钮为 paragraph 内含 "EasyChat Settings" 文字
    # 使用 get_by_text 更稳定，以下为备用
    _EASYCHAT_SETTINGS_BTN = "p:has-text('EasyChat Settings')"
    _EASYCHAT_ON_LABEL = "p:has-text('EasyChat On')"
    _MORE_MENU_BTN = "text=..."
    _PAGINATION_NEXT = "button:has-text('Next')"
    _PAGINATION_PAGE_2 = "button:has-text('2')"
    _PAGINATION_PAGE_1_CURRENT = "li.ant-pagination-item-active"

    # -------- 弹窗选择器（实测：弹窗为 div.modal-content，非原生 dialog 标签）--------
    _DIALOG = "[class*='modal-content']"
    _DIALOG_VISIBLE = "[class*='modal-content']:visible"
    _DIALOG_TITLE = "[class*='modal-content'] [class*='pc_title']"
    _DIALOG_CLOSE_BTN = "[class*='modal-content'] img[class*='pc_close_icon']"
    _DIALOG_TOGGLE = "[class*='modal-content'] img[class*='switchIcon']"
    _DIALOG_DESCRIPTION = "[class*='modal-content'] p[class*='description']"

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    # ========== 导航 ==========

    def navigate_to_list_page(self, base_url: str):
        """直接导航到 My Post 列表页，等待帖子列表渲染完成"""
        import time as _time
        try:
            self.page.goto(
                f"{base_url}/biz/en/publish/list",
                wait_until="domcontentloaded",
                timeout=30000,
            )
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            # 轮询等待帖子列表渲染（最多 15 秒）
            deadline = _time.time() + 15
            while _time.time() < deadline:
                if self.get_easychat_settings_btn_count() > 0:
                    break
                self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"导航到列表页失败: {e}")
            raise

    def click_jobs_tab(self):
        """点击 Jobs 分类 Tab（My Post 页面的 Toolbar 内）"""
        try:
            # 使用 role=toolbar 限定范围，避免匹配 Browse 菜单里的 Jobs 链接
            self.page.locator("[role='toolbar']").get_by_text("Jobs", exact=True).first.click()
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            self.page.wait_for_timeout(1500)
        except Exception as e:
            self.logger.error(f"点击 Jobs Tab 失败: {e}")
            raise

    def click_all_tab(self):
        """点击 All 分类 Tab（My Post 页面的 Toolbar 内）"""
        try:
            self.page.locator("[role='toolbar']").get_by_text("All", exact=True).first.click()
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            self.page.wait_for_timeout(1500)
        except Exception as e:
            self.logger.error(f"点击 All Tab 失败: {e}")
            raise

    def click_active_tab(self):
        """点击 Active 状态 Tab"""
        try:
            self.page.get_by_role("button", name="Active").click()
            self.page.wait_for_timeout(1500)
        except Exception as e:
            self.logger.error(f"点击 Active Tab 失败: {e}")
            raise

    def click_pending_tab(self):
        """点击 Pending 状态 Tab"""
        try:
            self.page.get_by_role("button", name="Pending").click()
            self.page.wait_for_timeout(1500)
        except Exception as e:
            self.logger.error(f"点击 Pending Tab 失败: {e}")
            raise

    # ========== 列表数据获取 ==========

    def get_easychat_settings_buttons(self):
        """获取当前页所有 EasyChat Settings 按钮（<p> 类型）"""
        return self.page.locator("p").filter(has_text="EasyChat Settings")

    def get_easychat_on_labels(self):
        """获取当前页所有 EasyChat On 标签（<p> 类型）"""
        return self.page.locator("p").filter(has_text="EasyChat On")

    def get_first_card_easychat_settings_btn(self):
        """获取第一条帖子的 EasyChat Settings 按钮"""
        return self.page.locator("p").filter(has_text="EasyChat Settings").first

    def get_nth_card_easychat_settings_btn(self, n: int):
        """获取第 n 条帖子的 EasyChat Settings 按钮（0-indexed）"""
        return self.page.locator("p").filter(has_text="EasyChat Settings").nth(n)

    def is_first_card_easychat_on(self) -> bool:
        """判断第一条帖子是否显示 EasyChat On 标签"""
        return self._is_card_easychat_on_by_index(0)

    def wait_for_easychat_on_count_decrease(self, before_count: int, timeout: int = 5000) -> bool:
        """等待 EasyChat On 标签总数减少（切换某帖子为 OFF 后），超时返回 False"""
        import time as _time
        deadline = _time.time() + timeout / 1000
        while _time.time() < deadline:
            if self.get_easychat_on_count() < before_count:
                return True
            self.page.wait_for_timeout(300)
        return self.get_easychat_on_count() < before_count

    def wait_for_easychat_on_count_increase(self, before_count: int, timeout: int = 5000) -> bool:
        """等待 EasyChat On 标签总数增加（切换某帖子为 ON 后），超时返回 False"""
        import time as _time
        deadline = _time.time() + timeout / 1000
        while _time.time() < deadline:
            if self.get_easychat_on_count() > before_count:
                return True
            self.page.wait_for_timeout(300)
        return self.get_easychat_on_count() > before_count

    def wait_for_first_card_easychat_on(self, timeout: int = 5000) -> bool:
        """等待第一条帖子出现 EasyChat On 标签，超时返回 False"""
        import time as _time
        deadline = _time.time() + timeout / 1000
        while _time.time() < deadline:
            if self.is_first_card_easychat_on():
                return True
            self.page.wait_for_timeout(300)
        return False

    def wait_for_first_card_easychat_off(self, timeout: int = 5000) -> bool:
        """等待第一条帖子 EasyChat On 标签消失，超时返回 False"""
        import time as _time
        deadline = _time.time() + timeout / 1000
        while _time.time() < deadline:
            if not self.is_first_card_easychat_on():
                return True
            self.page.wait_for_timeout(300)
        return not self.is_first_card_easychat_on()

    def _is_card_easychat_on_by_index(self, n: int) -> bool:
        """
        通过第 n 个 Settings 按钮的 bounding_box 范围，
        判断该卡片是否有 EasyChat On 标签（0-indexed）。
        """
        try:
            settings_btn = self.page.locator("p").filter(has_text="EasyChat Settings").nth(n)
            settings_box = settings_btn.bounding_box(timeout=2000)
            if settings_box is None:
                return False
            on_labels = self.page.locator("p").filter(has_text="EasyChat On").all()
            for label in on_labels:
                try:
                    label_box = label.bounding_box()
                    if label_box and abs(label_box["y"] - settings_box["y"]) < 300:
                        return True
                except Exception:
                    continue
            return False
        except Exception:
            return False

    def is_nth_card_easychat_on(self, n: int) -> bool:
        """判断第 n 条帖子是否显示 EasyChat On 标签（0-indexed）"""
        return self._is_card_easychat_on_by_index(n)

    def get_easychat_on_count(self) -> int:
        """获取当前页 EasyChat On 标签数量"""
        try:
            return self.page.locator("p").filter(has_text="EasyChat On").count()
        except Exception:
            return 0

    def get_easychat_settings_btn_count(self) -> int:
        """获取当前页 EasyChat Settings 按钮数量"""
        try:
            return self.page.locator("p").filter(has_text="EasyChat Settings").count()
        except Exception:
            return 0

    def find_card_without_easychat_on(self) -> int:
        """
        找到第一个没有 EasyChat On 标签的帖子索引（0-indexed）。
        通过逐一检查每个 EasyChat Settings 按钮所属卡片的标签状态。
        返回 -1 表示未找到。
        """
        total = self.get_easychat_settings_btn_count()
        on_count = self.get_easychat_on_count()
        if on_count >= total:
            return -1
        # 找到 EasyChat On 标签数量小于 Settings 按钮数量时，逐一检查
        # 实测：卡片结构为同级，通过父容器识别
        for i in range(total):
            settings_btn = self.page.locator(self._EASYCHAT_SETTINGS_BTN).nth(i)
            # 检查同一卡片内是否有 EasyChat On 标签
            card = settings_btn.locator("xpath=ancestor::*[contains(@class,'list') or contains(@class,'card') or contains(@class,'item')][1]")
            try:
                count = card.locator("p:has-text('EasyChat On')").count()
                if count == 0:
                    return i
            except Exception:
                continue
        return -1

    # ========== EasyChat Settings 弹窗操作 ==========

    def open_easychat_settings(self, card_index: int = 0):
        """打开指定帖子的 EasyChat Settings 弹窗"""
        try:
            btn = self.page.locator("p").filter(has_text="EasyChat Settings").nth(card_index)
            btn.scroll_into_view_if_needed(timeout=5000)
            btn.click(timeout=5000)
            # 弹窗为 div.modal-content（非原生 dialog 标签）
            self.page.wait_for_selector(self._DIALOG_VISIBLE, timeout=10000)
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"打开 EasyChat Settings 弹窗失败 (card={card_index}): {e}")
            raise

    def is_dialog_visible(self) -> bool:
        """判断 EasyChat Settings 弹窗是否可见"""
        try:
            dlg = self.page.locator(self._DIALOG_VISIBLE).first
            return dlg.is_visible(timeout=3000)
        except Exception:
            return False

    def get_dialog_title_text(self) -> str:
        """获取弹窗标题文字"""
        try:
            return self.page.locator(self._DIALOG_TITLE).first.inner_text(timeout=5000)
        except Exception:
            return ""

    def get_dialog_description_text(self) -> str:
        """获取弹窗描述文案"""
        try:
            desc = self.page.locator(self._DIALOG_DESCRIPTION).first
            return desc.inner_text(timeout=5000)
        except Exception:
            return ""

    def _get_toggle_element(self):
        """
        定位弹窗内 Toggle 开关元素（内部辅助方法）。
        实测弹窗结构：
          - img[class*='titleIcon']：EasyChat 品牌图标
          - img[class*='switchIcon']：Toggle 开关（ON 时 src 含 'checked'）
          - img[class*='pc_img']：AI 对话预览截图
        优先通过 class 精确匹配 switchIcon。
        """
        try:
            toggle = self.page.locator(self._DIALOG_TOGGLE).first
            if toggle.count() > 0:
                return toggle
            # 兜底：遍历弹窗内所有 img，找含 switch/checked 关键字的
            imgs = self.page.locator(f"{self._DIALOG_VISIBLE} img").all()
            for img in imgs:
                src = img.get_attribute("src", timeout=1000) or ""
                cls = img.get_attribute("class", timeout=1000) or ""
                if any(kw in src.lower() for kw in ("switch", "toggle", "checked", "unchecked")):
                    return img
                if any(kw in cls.lower() for kw in ("switch", "toggle")):
                    return img
            return imgs[1] if len(imgs) >= 2 else (imgs[0] if imgs else None)
        except Exception:
            return None

    def _get_visible_dialog(self):
        """获取当前可见的弹窗元素"""
        try:
            return self.page.locator(self._DIALOG_VISIBLE).first
        except Exception:
            return None

    def _get_toggle_src(self) -> str:
        """获取弹窗内 Toggle 图标的 src（内部辅助方法）"""
        try:
            el = self._get_toggle_element()
            if el is None:
                return ""
            return el.get_attribute("src", timeout=2000) or ""
        except Exception:
            return ""

    def is_dialog_toggle_on(self) -> bool:
        """
        判断弹窗内 Toggle 开关是否为 ON 状态。
        实测 src 规律：
          ON  → icon_switch_checked.xxx.png（含 "checked"，不含 "unchecked"）
          OFF → icon_switch.xxx.png（不含 "checked"）
        """
        try:
            src = self._get_toggle_src().lower()
            if not src:
                return False
            # unchecked 优先判断（兜底防止误判）
            if "unchecked" in src:
                return False
            return "checked" in src
        except Exception:
            return False

    def is_dialog_toggle_off(self) -> bool:
        """判断弹窗内 Toggle 开关是否为 OFF 状态"""
        return not self.is_dialog_toggle_on()

    def click_dialog_toggle(self):
        """点击弹窗内的 Toggle 开关（切换状态）"""
        try:
            el = self._get_toggle_element()
            if el is None:
                raise Exception("未找到弹窗内 Toggle 开关元素")
            el.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击 Toggle 失败: {e}")
            raise

    def close_dialog_by_x_button(self):
        """点击弹窗右上角关闭图标（img.pc_close_icon）关闭弹窗"""
        try:
            close_btn = self.page.locator(self._DIALOG_CLOSE_BTN).first
            close_btn.click()
            # 等待弹窗消失
            self.page.wait_for_selector(self._DIALOG_VISIBLE, state="hidden", timeout=5000)
        except Exception as e:
            self.logger.error(f"点击 X 关闭弹窗失败: {e}")
            raise

    def close_dialog_by_esc(self):
        """按 ESC 键关闭弹窗"""
        try:
            self.page.keyboard.press("Escape")
            self.page.wait_for_selector(self._DIALOG_VISIBLE, state="hidden", timeout=5000)
        except Exception as e:
            self.logger.error(f"ESC 关闭弹窗失败: {e}")
            raise

    def click_dialog_overlay(self):
        """点击弹窗蒙层区域（弹窗外侧）"""
        try:
            self.page.mouse.click(50, 400)
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击蒙层失败: {e}")
            raise

    def is_dialog_has_close_button(self) -> bool:
        """判断弹窗是否有关闭图标（img.pc_close_icon）"""
        try:
            btn = self.page.locator(self._DIALOG_CLOSE_BTN).first
            return btn.is_visible(timeout=3000)
        except Exception:
            return False

    def is_dialog_has_toggle(self) -> bool:
        """判断弹窗是否有 Toggle 开关（img.switchIcon）"""
        try:
            return self._get_toggle_element() is not None
        except Exception:
            return False

    def is_dialog_has_preview_image(self) -> bool:
        """判断弹窗是否有 AI 对话预览图（img.pc_img）"""
        try:
            preview = self.page.locator(f"{self._DIALOG_VISIBLE} img[class*='pc_img']").first
            return preview.is_visible(timeout=3000)
        except Exception:
            return False

    # ========== 更多菜单操作 ==========

    def open_more_menu(self, card_index: int = 0):
        """打开指定帖子的 ... 更多菜单"""
        try:
            more_btn = self.page.locator("text=...").nth(card_index)
            more_btn.click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"打开更多菜单失败 (card={card_index}): {e}")
            raise

    def is_more_menu_visible(self) -> bool:
        """判断更多菜单是否可见"""
        try:
            return self.page.get_by_text("Edit").is_visible(timeout=3000)
        except Exception:
            return False

    def is_more_menu_has_ai_option(self) -> bool:
        """判断更多菜单是否包含 AI 相关选项"""
        try:
            menu_text = self.page.locator("[role='menu'], [class*='dropdown']").inner_text(timeout=3000)
            return "AI" in menu_text or "EasyChat" in menu_text
        except Exception:
            return False

    def close_more_menu(self):
        """关闭更多菜单（ESC 键）"""
        try:
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"关闭更多菜单失败: {e}")

    # ========== 分页操作 ==========

    def click_next_page(self):
        """点击分页下一页按钮"""
        try:
            self.page.get_by_role("button", name="Next").click()
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            self.page.wait_for_timeout(1500)
        except Exception as e:
            self.logger.error(f"点击下一页失败: {e}")
            raise

    def click_page_number(self, page_num: int):
        """点击指定页码"""
        try:
            self.page.get_by_role("button", name=str(page_num)).click()
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            self.page.wait_for_timeout(1500)
        except Exception as e:
            self.logger.error(f"点击第{page_num}页失败: {e}")
            raise

    def has_pagination(self) -> bool:
        """判断是否有分页"""
        try:
            return self.page.get_by_role("button", name="Next").count() > 0
        except Exception:
            return False

    # ========== 页面刷新 ==========

    def refresh_page(self):
        """刷新当前页面"""
        try:
            self.page.reload(wait_until="domcontentloaded", timeout=30000)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"刷新页面失败: {e}")
            raise
