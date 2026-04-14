# pages/order_flow_page.py
"""
AE Marketplace 订单流转页面对象（合并版）

合并来源：
  - order_flow_page.py        （导航、Tab、订单操作、验证）
  - checkout_shipping_page.py （收货地址弹窗表单）
  - checkout_page.py          （Pay 按钮检测）
  - purchase_orders_page.py   （Airwallex iframe CVC 输入 & 支付）

只保留 test_order_flow_v2.py 中实际调用的方法，删除未调用方法。
"""
import logging
import random
import re
from pages.base_page import BasePage
from utils.logger import setup_logger
from playwright.sync_api import Page


class OrderFlowPage(BasePage):
    """AE Marketplace 订单流转页面对象（MCP 精准选择器）"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = setup_logger()

    # ========== 用户名与菜单（MCP 录制）==========
    def click_username_buyer(self, username: str = "AEOKer_cui123"):
        """点击买家用户名打开下拉"""
        self.page.get_by_text(username).click()

    def click_username_seller(self, username: str = "OKer_wangyongli"):
        """点击卖家用户名打开下拉"""
        self.page.get_by_text(username).click()

    def click_purchase_orders(self):
        """点击 Purchase Orders"""
        self.page.get_by_text("Purchase Orders").click()

    def click_sales_orders(self):
        """点击 Sales Orders"""
        self.page.get_by_text("Sales Orders").click()

    def click_logout(self):
        """点击 Log Out"""
        self.page.get_by_text("Log Out").click()

    # ========== Tab 切换（MCP: .first 避免多元素）==========
    def _click_tab(self, tab_text: str, timeout: int = 10000):
        """通用：点击订单管理页 Tab（实际为 div[class*=order_tab_item]，无 role=tab）"""
        # Pending 单独用正则，避免 :has-text("Pending") 误匹配「Pending Receipt」
        if tab_text == "Pending":
            tab = self.page.locator('[class*="order_tab_item"]').filter(
                has_text=re.compile(r"^\s*Pending\s*$")
            ).first
        else:
            tab = self.page.locator(f'[class*="order_tab_item"]:has-text("{tab_text}")').first
        tab.wait_for(state="visible", timeout=timeout)
        tab.click(timeout=timeout)

    def click_pending_tab(self, timeout: int = 10000):
        """点击 Pending Tab"""
        self._click_tab("Pending", timeout=timeout)

    def click_unshipped_tab(self):
        """点击 Unshipped Tab"""
        self._click_tab("Unshipped")

    def click_pending_receipt_tab(self):
        """点击 Pending Receipt Tab"""
        self._click_tab("Pending Receipt")

    def click_completed_tab(self):
        """点击 Completed Tab"""
        self._click_tab("Completed")

    def click_all_tab(self):
        """点击 ALL Tab（限定在订单 Tab 区域，避免误匹配 Browse 下拉中的 All Categories 等）"""
        tablist = self.page.locator('[role="tablist"]')
        if tablist.count() > 0:
            tablist.get_by_text("ALL", exact=True).first.click()
        else:
            self.page.get_by_text("ALL", exact=True).first.click()

    # ========== 订单卡片：统一入口，模拟人工点击右侧列表第一张卡片 ==========
    def click_first_order_in_list(self):
        """
        模拟人工操作：等待右侧订单列表渲染 → 滚动到第一张卡片 → 点击进入订单详情页。
        适用于所有 Tab（Pending / Unshipped / Pending Receipt / Completed）和买卖双端。
        """
        card = self.page.locator('[class*="order_list_item"]').first
        card.wait_for(state="visible", timeout=10000)
        card.scroll_into_view_if_needed(timeout=3000)
        card.click(timeout=8000)

    def click_first_order_card(self):
        """向后兼容别名"""
        self.click_first_order_in_list()

    def click_first_unshipped_card_seller(self):
        """向后兼容别名"""
        self.click_first_order_in_list()

    def click_first_pending_receipt_card(self):
        """向后兼容别名"""
        self.click_first_order_in_list()

    # ========== 订单详情页按钮（MCP 录制）==========
    def click_cancel_button(self):
        """点击 Cancel 按钮"""
        self.page.get_by_role("button", name="Cancel").click()

    def click_add_tracking_button(self):
        """点击 Add Tracking 按钮"""
        self.page.get_by_role("button", name="Add Tracking").click()

    def click_confirm_button(self):
        """点击 Confirm 按钮"""
        self.page.get_by_role("button", name="Confirm").click()

    def click_confirm_in_dialog(self):
        """弹框内点击 Confirm"""
        self.page.get_by_role("dialog").get_by_role("button", name="Confirm").click()

    def click_choose_file_button(self):
        """点击 Choose File 按钮"""
        self.page.get_by_role("button", name="Choose File").click()

    def click_upload_buyer_photos_button(self):
        """点击 Upload Buyer Photos 按钮"""
        self.page.get_by_role("button", name="Upload Buyer Photos").click()

    def click_view_transaction_button(self):
        """点击 View Transaction 按钮"""
        self.page.get_by_role("button", name="View Transaction").click()

    def click_message_seller(self):
        """点击 Message Seller"""
        self.page.get_by_text("Message Seller").click()

    def click_message_buyer(self):
        """点击 Message Buyer"""
        self.page.get_by_text("Message Buyer").click()

    def click_to_view_snapshot(self):
        """点击 click to view"""
        self.page.get_by_text("click to view").click()

    # ========== 取消理由（MCP 录制）==========
    def select_buyer_cancel_reason(self):
        """选择买家取消理由：I don't want to buy it anymore"""
        self.page.get_by_text("I don't want to buy it anymore").click()

    def select_seller_cancel_reason(self):
        """选择卖家取消理由：Buyer requested cancellation"""
        self.page.get_by_text("Buyer requested cancellation").click()

    # ========== Add Tracking 表单（MCP 录制）==========
    def fill_tracking_number(self, value: str = "TEST123456789"):
        """填写 Tracking Number"""
        self.page.get_by_role("textbox", name="Tracking Number").fill(value)

    def select_logistics_dhl(self):
        """选择物流公司 DHL"""
        logistics = self.page.get_by_role("textbox", name="logistics company")
        if logistics.count() > 0:
            logistics.first.click()
            self.page.wait_for_timeout(500)
        self.page.get_by_text("DHL").first.click()

    def click_mark_as_shipped(self):
        """点击 Mark as Shipped"""
        self.page.get_by_text("Mark as Shipped").click()

    # ========== 登录（MCP 录制）==========
    def login(self, email: str, password: str, base_url: str = "https://ae.58v5.cn/en/city-abu-dhabi/"):
        """执行登录流程"""
        self.page.goto(base_url)
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(2000)
        self.page.get_by_text("Log in / Register").click(timeout=10000)
        self.page.wait_for_timeout(2000)
        self.page.get_by_role("textbox", name="Email or phone number").fill(email)
        self.page.get_by_role("button", name="Continue").click()
        self.page.wait_for_timeout(2000)
        self.page.get_by_role("textbox", name="Enter password").fill(password)
        self.page.get_by_role("button", name="Log in").click()
        self.page.wait_for_timeout(4000)

    # ========== Checkout - Pay 按钮（来自 CheckoutPage）==========
    def is_pay_button_visible(self, timeout: int = 3000) -> bool:
        """Pay 按钮是否可见"""
        try:
            return self.page.locator("button:has-text('Pay')").first.is_visible(timeout=timeout)
        except Exception:
            return False

    # ========== Checkout - 收货地址弹窗（来自 CheckoutShippingPage）==========
    def click_address_block(self):
        """点击地址块打开 Address 弹窗；若弹窗已打开则先关闭再点击"""
        for _ in range(3):
            if not self.is_address_modal_visible(timeout=800):
                break
            self.click_close_button()
            self.page.wait_for_timeout(800)
        addr_selectors = [
            'div:has-text("Shipping"):has-text("United Arab Emirates")',
            'text=United Arab Emirates',
        ]
        for sel in addr_selectors:
            try:
                loc = self.page.locator(sel).first
                loc.wait_for(state="visible", timeout=3000)
                loc.scroll_into_view_if_needed(timeout=2000)
                self.page.wait_for_timeout(300)
                loc.click(timeout=5000)
                self.page.wait_for_timeout(500)
                if self.is_address_modal_visible(timeout=2000):
                    return
            except Exception:
                continue
        self.page.get_by_text("United Arab Emirates").first.scroll_into_view_if_needed()
        self.page.wait_for_timeout(300)
        self.page.get_by_text("United Arab Emirates").first.click(force=True, timeout=5000)

    def click_clean_button(self):
        """点击 Clean 按钮清空表单"""
        try:
            self.page.get_by_role("button", name="Clean").first.click()
        except Exception:
            self.page.get_by_text("Clean").first.click()

    def click_apply_button(self, timeout: int = 10000):
        """点击 Apply 按钮（反向遍历 dialogs，优先最内层弹窗，兼容嵌套弹窗场景）"""
        dialog_count = self.page.locator('[role="dialog"]').count()
        for idx in range(dialog_count - 1, -1, -1):
            try:
                dialog = self.page.locator('[role="dialog"]').nth(idx)
                for btn_name in ["Apply", "Save", "Confirm", "Done", "OK", "Submit"]:
                    try:
                        btn = dialog.get_by_role("button", name=btn_name).first
                        if btn.is_visible(timeout=1000):
                            btn.click(timeout=timeout)
                            return
                    except Exception:
                        continue
            except Exception:
                continue
        for btn_name in ["Apply", "Save", "Confirm", "Done", "OK"]:
            try:
                btn = self.page.get_by_role("button", name=btn_name).first
                if btn.is_visible(timeout=1500):
                    btn.click(timeout=timeout)
                    return
            except Exception:
                continue

    def click_close_button(self):
        """点击弹窗右上角 X 关闭"""
        close_selectors = [
            '[role="dialog"] button[aria-label*="close"]',
            '[role="dialog"] button[aria-label*="Close"]',
            '[role="dialog"] button:has-text("×")',
        ]
        for sel in close_selectors:
            try:
                btn = self.page.locator(sel).first
                if btn.is_visible(timeout=2000):
                    btn.click()
                    return
            except Exception:
                continue
        self.page.keyboard.press("Escape")

    def _fill_field_by_id(self, field_id: str, value: str, fallback_index: int = 0):
        """通用：按 ID 填写字段，失败时按 textbox 索引降级"""
        try:
            inp = self.page.locator(f"#{field_id}")
            inp.click(timeout=2000)
            self.page.wait_for_timeout(200)
            inp.fill(value)
        except Exception:
            try:
                inp = self.page.get_by_role("dialog").get_by_role("textbox").nth(fallback_index)
                inp.click(timeout=2000)
                self.page.wait_for_timeout(200)
                inp.fill(value)
            except Exception:
                pass

    def fill_full_name(self, value: str):
        """填写 FULL NAME（id=fullName）"""
        try:
            inp = self.page.locator("#fullName")
            inp.click(timeout=3000)
            self.page.wait_for_timeout(200)
            inp.fill(value)
        except Exception:
            try:
                inp = self.page.get_by_role("dialog").get_by_role("textbox").first
                inp.click(timeout=3000)
                self.page.wait_for_timeout(200)
                inp.fill(value)
            except Exception:
                self.page.get_by_role("dialog").get_by_role("textbox").first.fill(value, force=True)

    def fill_address_line1(self, value: str):
        """填写 ADDRESS LINE 1（id=addressLine1）"""
        self._fill_field_by_id("addressLine1", value, fallback_index=1)

    def fill_city(self, value: str):
        """填写 County/City（id=secondLevel，textbox index=3）"""
        self._fill_field_by_id("secondLevel", value, fallback_index=3)

    def select_state_dropdown(self, state_value: str):
        """点击 State/Province/Region 下拉框并选择选项（支持嵌套弹窗，多种触发文本兼容）"""
        log = logging.getLogger()
        dialog = None
        dialog_count = self.page.locator('[role="dialog"]').count()
        state_trigger_texts = [
            "State / Province / Region",
            "State/Province/Region",
            "State",
            "Province",
        ]
        for idx in range(dialog_count - 1, -1, -1):
            candidate = self.page.locator('[role="dialog"]').nth(idx)
            for trigger_text in state_trigger_texts:
                try:
                    if candidate.locator(f':text-is("{trigger_text}")').first.is_visible(timeout=400):
                        dialog = candidate
                        break
                except Exception:
                    continue
            if dialog is not None:
                break
        if dialog is None:
            dialog = self.page.locator('[role="dialog"]').first

        clicked = False
        specific_selectors = [
            '[class*="FormSelectProvince"]',
            '[class*="SelectProvince"]',
            '[class*="float-label-container"]',
        ]
        for sel in specific_selectors:
            try:
                trigger = dialog.locator(sel).filter(has_text="State").first
                if trigger.is_visible(timeout=800):
                    trigger.click(timeout=3000)
                    clicked = True
                    break
            except Exception:
                continue

        if not clicked:
            for trigger_text in state_trigger_texts:
                try:
                    trigger = dialog.locator(f':text-is("{trigger_text}")').first
                    if trigger.is_visible(timeout=500):
                        trigger.click(timeout=3000)
                        clicked = True
                        break
                except Exception:
                    continue

        if not clicked:
            log.warning(f"select_state_dropdown: 无法找到 State 触发器，state_value={state_value}")
            return

        self.page.wait_for_timeout(500)
        new_dialog_count = self.page.locator('[role="dialog"]').count()
        try:
            self.page.locator('[role="dialog"]').nth(new_dialog_count - 1).wait_for(state="visible", timeout=3000)
        except Exception:
            try:
                self.page.locator('[role="listbox"]').wait_for(state="visible", timeout=2000)
            except Exception:
                pass

        try:
            self.page.locator('[role="dialog"]').nth(new_dialog_count - 1).get_by_text(
                state_value, exact=True
            ).first.click(timeout=3000)
            self.page.wait_for_timeout(300)
            return
        except Exception as e:
            log.warning(f"select_state_dropdown: option in new dialog failed: {e}")

        try:
            self.page.locator('[role="listbox"]').get_by_text(state_value, exact=True).first.click(timeout=2000)
            self.page.wait_for_timeout(300)
            return
        except Exception:
            pass

        try:
            self.page.get_by_text(state_value, exact=True).last.click(timeout=2000)
            self.page.wait_for_timeout(300)
        except Exception as e2:
            log.warning(f"select_state_dropdown: all fallbacks failed: {e2}")

    def fill_state(self, value: str):
        """State/Province/Region 是下拉框，调用 select_state_dropdown"""
        self.select_state_dropdown(value)

    def fill_zip(self, value: str):
        """填写 ZIP / POSTAL CODE（id=postalCode）"""
        self._fill_field_by_id("postalCode", value, fallback_index=4)

    def fill_phone(self, value: str):
        """填写 PHONE / MOBILE（id=phone）"""
        self._fill_field_by_id("phone", value, fallback_index=5)

    # ========== 收货地址弹窗验证 ==========
    def is_address_modal_visible(self, timeout: int = 3000) -> bool:
        """地址编辑弹窗是否可见（通过 #fullName 或 #addressLine1 判断）"""
        try:
            if self.page.locator("#fullName").is_visible(timeout=timeout):
                return True
        except Exception:
            pass
        try:
            if self.page.locator("#addressLine1").is_visible(timeout=500):
                return True
        except Exception:
            pass
        return False

    def is_apply_button_visible(self, timeout: int = 3000) -> bool:
        """Apply 按钮是否可见"""
        try:
            return self.page.get_by_role("button", name="Apply").first.is_visible(timeout=timeout)
        except Exception:
            return False

    def is_clean_button_visible(self, timeout: int = 3000) -> bool:
        """Clean 按钮是否可见"""
        try:
            if self.page.get_by_role("button", name="Clean").first.is_visible(timeout=1000):
                return True
        except Exception:
            pass
        try:
            return self.page.get_by_text("Clean").first.is_visible(timeout=timeout)
        except Exception:
            return False

    def is_shipping_section_visible(self, timeout: int = 3000) -> bool:
        """Shipping 区域是否可见"""
        try:
            return self.page.get_by_text("Shipping", exact=True).first.is_visible(timeout=timeout)
        except Exception:
            return False

    # ========== 订单状态验证（MCP 录制）==========
    def is_unshipped_tab_visible(self) -> bool:
        """Unshipped Tab 是否可见"""
        try:
            return self.page.get_by_text("Unshipped").first.is_visible(timeout=3000)
        except Exception:
            return False

    def is_order_cancelled_visible(self) -> bool:
        """订单是否显示 Order Cancelled"""
        try:
            return self.page.get_by_text("Order Cancelled").is_visible(timeout=3000)
        except Exception:
            return False

    def is_order_completed_visible(self) -> bool:
        """订单是否显示 Order Completed 或 Completed 状态"""
        try:
            if self.page.get_by_text("Order Completed", exact=True).is_visible(timeout=2000):
                return True
        except Exception:
            pass
        try:
            return self.page.get_by_text("Completed", exact=True).is_visible(timeout=2000)
        except Exception:
            return False

    def is_view_transaction_visible(self) -> bool:
        """View Transaction 按钮是否可见"""
        try:
            return self.page.get_by_role("button", name="View Transaction").is_visible(timeout=3000)
        except Exception:
            return False

    def is_confirm_dialog_attention_visible(self) -> bool:
        """确认收货弹框标题 Attention 是否可见"""
        try:
            return self.page.get_by_role("dialog").get_by_text("Attention").is_visible(timeout=3000)
        except Exception:
            return False

    def is_transaction_successful_visible(self) -> bool:
        """View Transaction 弹框是否显示 Transaction Successful"""
        try:
            return self.page.get_by_text("Transaction Successful").is_visible(timeout=5000)
        except Exception:
            return False

    # ========== Airwallex iframe 支付（来自 PurchaseOrdersPage）==========
    def input_cvc_in_iframe(self, cvc_value: str = None) -> tuple:
        """
        在 Airwallex iframe 中输入 CVC。

        Returns:
            tuple[bool, str, Frame]: (是否成功, CVC值, 支付iframe)
        """
        try:
            cvc_value = cvc_value or str(random.randint(100, 999))
            cvc_input = None
            payment_frame = None

            try:
                self.page.wait_for_selector(
                    'iframe[src*="airwallex"], iframe[src*="checkout-demo"], iframe[name*="Airwallex"]',
                    timeout=15000
                )
                self.page.wait_for_timeout(2000)
            except Exception:
                pass

            self.logger.info("  - 开始在 iframe 中查找 CVC 输入框...")
            max_find_attempts = 8
            for find_attempt in range(max_find_attempts):
                self.logger.info(f"  - 第 {find_attempt + 1}/{max_find_attempts} 次尝试查找 CVC 输入框")
                for frame_idx, frame in enumerate(self.page.frames):
                    try:
                        frame_url = frame.url if hasattr(frame, 'url') else 'unknown'
                        inputs = frame.locator("input").all()
                        self.logger.info(
                            f"    Frame {frame_idx} ({frame_url[:50]}...): 找到 {len(inputs)} 个输入框"
                        )
                        for inp_idx, inp in enumerate(inputs):
                            try:
                                placeholder = inp.get_attribute("placeholder") or ""
                                name = inp.get_attribute("name") or ""
                                input_id = inp.get_attribute("id") or ""
                                input_class = inp.get_attribute("class") or ""
                                input_type = inp.get_attribute("type") or ""
                                aria_label = inp.get_attribute("aria-label") or ""
                                data_testid = inp.get_attribute("data-testid") or ""
                                self.logger.info(
                                    f"      Input {inp_idx}: "
                                    f"placeholder='{placeholder}', name='{name}', id='{input_id}', "
                                    f"type='{input_type}', class='{input_class[:50]}', "
                                    f"aria-label='{aria_label}', visible={inp.is_visible()}"
                                )
                                all_text = (
                                    placeholder + name + input_id + input_class + aria_label + data_testid
                                ).lower()
                                is_cvc_field = (
                                    'cvc' in all_text or
                                    'cvv' in all_text or
                                    'security' in all_text or
                                    'card-cvc' in all_text or
                                    'cardcvc' in all_text or
                                    'verification' in all_text or
                                    (input_type in ['text', 'tel', 'number'] and
                                     (inp.get_attribute("maxlength") in ['3', '4'] or
                                      'security' in placeholder.lower() or
                                      placeholder.strip().upper() == 'CVC'))
                                )
                                if is_cvc_field and inp.is_visible():
                                    cvc_input = inp
                                    payment_frame = frame
                                    self.logger.info(
                                        f"      ✓ 找到 CVC 输入框！(Frame {frame_idx}, Input {inp_idx})"
                                    )
                                    break
                            except Exception:
                                continue
                    except Exception:
                        continue
                    if payment_frame:
                        break
                if cvc_input:
                    break
                if find_attempt < max_find_attempts - 1:
                    self.logger.info("  - 未找到 CVC 输入框，等待 5 秒后重试...")
                    self.page.wait_for_timeout(5000)

            if cvc_input and payment_frame:
                self.logger.info(f"  - 准备输入 CVC: {cvc_value}")
                cvc_input.click()
                self.page.wait_for_timeout(1000)
                cvc_input.fill(cvc_value)
                self.page.wait_for_timeout(2000)
                self.logger.info(f"  ✓ CVC 输入成功: {cvc_value}")
                return True, cvc_value, payment_frame
            else:
                self.logger.warning(
                    f"  ✗ 在所有 {len(self.page.frames)} 个 frame 中都未找到 CVC 输入框"
                )
                return False, "", None
        except Exception as e:
            self.logger.error(f"输入 CVC 失败: {e}")
            return False, "", None

    def click_google_pay_in_iframe(
        self, google_email: str = None, google_password: str = None
    ) -> bool:
        """
        在 Airwallex 支付 iframe 中查找并点击 Google Pay 按钮。
        若弹出 Google 账号登录弹窗，自动完成邮箱+密码登录后确认支付。

        Args:
            google_email: Google 账号邮箱（弹窗需要登录时使用）
            google_password: Google 账号密码

        Returns:
            bool: 是否成功点击并完成 Google Pay 整体流程
        """
        _GPAY_SELECTORS = [
            "button[data-testid*='google']",
            "button[aria-label*='Google Pay']",
            "button:has-text('Google Pay')",
            "[class*='google-pay']:visible",
            "[class*='googlepay']:visible",
            "div[role='button'][aria-label*='Google']",
            "img[alt*='Google Pay']",
        ]
        try:
            # 等待 Airwallex iframe 加载（最多 30 秒，每 3 秒检查一次，至少需要 2 个 frame）
            self.logger.info("  - 等待 Airwallex 支付 iframe 加载...")
            for _w in range(10):
                frame_count = len(self.page.frames)
                self.logger.info(f"  - 当前 frame 数量: {frame_count}")
                if frame_count >= 2:
                    break
                self.page.wait_for_timeout(3000)

            self.logger.info(f"  - 开始在 {len(self.page.frames)} 个 frame 中查找 Google Pay 按钮...")
            for frame_idx, frame in enumerate(self.page.frames):
                try:
                    for sel in _GPAY_SELECTORS:
                        btns = frame.locator(sel).all()
                        for btn in btns:
                            try:
                                if not btn.is_visible():
                                    continue
                                self.logger.info(
                                    f"  ✓ 在 Frame {frame_idx} 找到 Google Pay 按钮，准备点击"
                                )
                                btn.scroll_into_view_if_needed()
                                self.page.wait_for_timeout(500)
                                try:
                                    with self.page.expect_popup(timeout=8000) as popup_info:
                                        btn.click()
                                    gpay_popup = popup_info.value
                                    self.logger.info("  - 检测到 Google Pay 弹窗，开始处理...")
                                    self._handle_google_pay_popup(
                                        gpay_popup, google_email, google_password
                                    )
                                except Exception:
                                    btn.click()
                                self.logger.info("  ✓ Google Pay 流程完成")
                                return True
                            except Exception:
                                continue
                except Exception:
                    continue
            self.logger.warning(
                f"  ✗ 在所有 {len(self.page.frames)} 个 frame 中均未找到 Google Pay 按钮"
            )
            return False
        except Exception as e:
            self.logger.error(f"点击 Google Pay 按钮失败: {e}")
            return False

    def _handle_google_pay_popup(
        self, popup, google_email: str = None, google_password: str = None
    ) -> None:
        """
        处理 Google Pay 弹窗完整流程：
          Step 1. 输入邮箱 → 点击 Next → 输入密码 → 点击 Next
          Step 2. 等待页面完全加载（networkidle），循环处理中间跳转页/挑战页
          Step 3. 页面加载完成后，在所有 frame 中查找并点击 "Pay" 按钮
          Step 4. 等待弹窗自动关闭（支付完成）或手动关闭
        """
        try:
            # 等待弹窗初始加载
            popup.wait_for_load_state("domcontentloaded", timeout=15000)
            popup.wait_for_timeout(2000)
            self.logger.info(f"  - Google Pay 弹窗 URL: {popup.url[:100]}")

            # ── Step 1: 登录（邮箱 → Next → 密码 → Next）─────────────────────────
            targets = [popup] + list(popup.frames)
            cur_popup_url = popup.url

            # 场景A：Google 已有 Session → 显示 "Choose an account" 账号列表
            account_chosen = False
            if google_email and "accounts.google.com" in cur_popup_url:
                for tgt in targets:
                    try:
                        for sel in [
                            f'[data-email="{google_email}"]',
                            f'[aria-label*="{google_email}"]',
                            f'li:has-text("{google_email}")',
                            f'div[role="listitem"]:has-text("{google_email}")',
                        ]:
                            el = tgt.locator(sel).first
                            if el.is_visible(timeout=1500):
                                el.click()
                                self.logger.info(f"  - 选择已有账号: {google_email}")
                                popup.wait_for_timeout(3000)
                                account_chosen = True
                                break
                        if account_chosen:
                            break
                    except Exception:
                        continue

            # 场景B：URL 含 "identifier" → 直接判断为邮箱输入页（最可靠，无需元素检测）
            need_login = False
            if not account_chosen:
                if "identifier" in cur_popup_url:
                    # URL 明确指向邮箱登录页，直接登录
                    need_login = True
                    self.logger.info(f"  - URL 含 identifier，直接执行登录流程")
                else:
                    # 元素兜底检测（6s 超时，给 JS 渲染充足时间）
                    for tgt in targets:
                        try:
                            if tgt.locator('input[type="email"]').first.is_visible(timeout=6000):
                                need_login = True
                                break
                        except Exception:
                            continue
                    # Sign in 按钮检测
                    if not need_login:
                        for sel in ["button:has-text('Sign in')", "a:has-text('Sign in')",
                                    "text=Sign in to Google Pay", "text=Sign in"]:
                            try:
                                el = popup.locator(sel).first
                                if el.is_visible(timeout=1500):
                                    el.click()
                                    popup.wait_for_timeout(3000)
                                    need_login = True
                                    break
                            except Exception:
                                continue

                if need_login:
                    if not (google_email and google_password):
                        self.logger.warning("  ✗ 需要 Google 登录凭证但未提供")
                        try:
                            popup.close()
                        except Exception:
                            pass
                        return
                    self._google_signin_in_popup(popup, google_email, google_password)

            # ── Step 2: 等待页面完全加载，处理中间跳转 ──────────────────────────────
            # 密码 Next 后，等待页面完整加载（networkidle = 无网络请求），最多 30 秒
            self.logger.info("  - 等待页面完全加载（networkidle）...")
            try:
                popup.wait_for_load_state("networkidle", timeout=30000)
            except Exception:
                popup.wait_for_timeout(5000)
            self.logger.info(f"  - 页面加载完成，当前 URL: {popup.url[:100]}")

            # 若仍在 accounts.google.com（各种挑战页），循环处理
            _PROCEED_TEXTS = [
                "Continue", "Yes, it's me", "Not now", "Skip",
                "Try another way", "Confirm", "I agree",
            ]
            for _i in range(8):
                if "accounts.google.com" not in popup.url:
                    break
                cur_url = popup.url
                self.logger.info(f"  - 仍在 Google 账号页（第{_i+1}次），URL: {cur_url[:100]}")

                # /identifier：邮箱输入页（Step 1 漏判时的兜底，直接重跑登录流程）
                if "identifier" in cur_url:
                    self.logger.info("  - 仍在邮箱登录页（identifier），兜底执行完整登录...")
                    if google_email and google_password:
                        self._google_signin_in_popup(popup, google_email, google_password)
                        # 等待 URL 离开 identifier 页
                        try:
                            popup.wait_for_function(
                                "() => !location.href.includes('identifier')",
                                timeout=15000
                            )
                        except Exception:
                            popup.wait_for_timeout(4000)
                    else:
                        self.logger.warning("  ✗ 无登录凭证，无法处理 identifier 页")
                        popup.wait_for_timeout(2000)
                    continue

                # /challenge/pwd：Google 要求再次输入密码（安全验证）
                if "/challenge/pwd" in cur_url or "/challenge/ipp" in cur_url:
                    self.logger.info("  - 检测到密码再次验证挑战页，重新输入密码...")
                    # 给页面额外时间渲染输入框
                    popup.wait_for_timeout(1500)
                    pw_filled = False
                    _pw_sels = [
                        'input[type="password"]',
                        'input[name="password"]',
                        'input[name="Passwd"]',
                        'input[autocomplete="current-password"]',
                        'input[aria-label*="password" i]',
                    ]
                    for tgt in [popup] + list(popup.frames):
                        if pw_filled:
                            break
                        for pw_sel in _pw_sels:
                            try:
                                inp = tgt.locator(pw_sel).first
                                if inp.is_visible(timeout=10000):
                                    inp.click()
                                    popup.wait_for_timeout(300)
                                    inp.fill(google_password)
                                    popup.wait_for_timeout(500)
                                    self.logger.info(f"  - 已再次填写密码（selector: {pw_sel}）")
                                    pw_filled = True
                                    break
                            except Exception:
                                continue
                    if pw_filled:
                        # 点击 Next
                        for txt in ["Next", "下一步"]:
                            try:
                                btn = popup.get_by_role("button", name=txt).first
                                if btn.is_visible(timeout=2000):
                                    btn.click()
                                    self.logger.info(f"  ✓ 密码挑战页点击 '{txt}'")
                                    break
                            except Exception:
                                continue
                        else:
                            popup.keyboard.press("Enter")
                        # 等待离开 challenge/pwd 页
                        try:
                            popup.wait_for_function(
                                "() => !location.href.includes('/challenge/pwd')",
                                timeout=15000
                            )
                        except Exception:
                            popup.wait_for_timeout(4000)
                    else:
                        self.logger.warning("  ✗ challenge/pwd 页未找到密码输入框")
                    continue

                # 其他挑战页：找可点击的跳过/继续按钮
                clicked = False
                for txt in _PROCEED_TEXTS:
                    try:
                        btn = popup.get_by_role("button", name=txt).first
                        if btn.is_visible(timeout=2000):
                            btn.click()
                            self.logger.info(f"  - 点击 '{txt}'")
                            try:
                                popup.wait_for_load_state("networkidle", timeout=15000)
                            except Exception:
                                popup.wait_for_timeout(2000)
                            clicked = True
                            break
                    except Exception:
                        continue
                if not clicked:
                    popup.wait_for_timeout(2000)

            self.logger.info(f"  - 最终弹窗 URL: {popup.url[:100]}")

            # ── Step 3: 等待页面完全加载后，直接点击 Pay 按钮完成支付 ─────────────
            # 用户确认流程：密码 → Next → 等待加载 → 直接点击 Pay（无需选卡）
            self.logger.info("  - 等待支付确认页加载...")
            try:
                popup.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                popup.wait_for_timeout(3000)
            self.logger.info(f"  - 支付页加载完成，URL: {popup.url[:100]}")

            # 截图记录支付确认页面状态（点击 Pay 前）
            try:
                popup.screenshot(path="reports/gpay_confirm_page.png")
                self.logger.info("  - 已截图（支付确认页）：reports/gpay_confirm_page.png")
            except Exception:
                pass

            pay_done = False
            all_targets = [popup] + list(popup.frames)
            for _attempt in range(4):
                if pay_done:
                    break
                for tgt in all_targets:
                    try:
                        # 方法1：在 Google Pay 确认页找到底部 "Pay" 按钮（最后一个可见的 Pay 按钮）
                        # 注意：卡行的 > 箭头不是"Pay"，底部蓝色按钮才是
                        pay_btns = tgt.locator("button:has-text('Pay')").all()
                        self.logger.info(f"  - 在 target 中找到 {len(pay_btns)} 个含 'Pay' 的按钮")
                        # 从后往前找，优先点最后一个（底部的 Pay 按钮）
                        for pb in reversed(pay_btns):
                            try:
                                btn_text = pb.text_content() or ""
                                btn_box = pb.bounding_box()
                                self.logger.info(
                                    f"  - 候选 Pay 按钮：text='{btn_text.strip()[:30]}', "
                                    f"box={btn_box}"
                                )
                                # 只点击文本精确为 "Pay" 的按钮（排除 "Pay with Google"、卡行箭头等）
                                if btn_text.strip() in ("Pay",) and pb.is_visible(timeout=1000):
                                    pb.click()
                                    self.logger.info(f"  ✓ 点击底部 Pay 按钮（text='{btn_text.strip()}'）")
                                    popup.wait_for_timeout(3000)
                                    pay_done = True
                                    break
                            except Exception:
                                continue
                        if pay_done:
                            break
                    except Exception:
                        pass
                    # 备选：精确角色匹配（exact=True）
                    try:
                        btn = tgt.get_by_role("button", name="Pay", exact=True).last
                        if btn.is_visible(timeout=2000):
                            btn.click()
                            self.logger.info("  ✓ 点击 Pay 按钮（role=button, exact）")
                            popup.wait_for_timeout(3000)
                            pay_done = True
                            break
                    except Exception:
                        pass
                if not pay_done:
                    self.logger.info(f"  - 第{_attempt+1}次未找到 Pay 按钮，等待 2 秒重试...")
                    popup.wait_for_timeout(2000)

            if not pay_done:
                self.logger.warning("  ✗ 未找到 Google Pay 底部 Pay 按钮")

            # ── Step 4: 等待弹窗关闭 ─────────────────────────────────────────────
            # 截图记录点击 Pay 后的页面状态
            try:
                popup.screenshot(path="reports/gpay_before_close.png")
                self.logger.info("  - 已截图（Pay 点击后）：reports/gpay_before_close.png")
            except Exception:
                pass
            # 点击 Pay 后支付处理需要时间，最多等待 60 秒让弹窗自动关闭
            self.logger.info("  - 等待 Google Pay 支付完成（最多 60 秒）...")
            try:
                popup.wait_for_event("close", timeout=60000)
                self.logger.info("  ✓ Google Pay 弹窗已自动关闭（支付完成）")
            except Exception:
                self.logger.info(f"  - 弹窗 60 秒后仍未关闭，当前 URL: {popup.url[:100]}")
                # 再尝试一次点击 Pay（可能第一次点击未生效）
                for tgt in [popup] + list(popup.frames):
                    try:
                        btn = tgt.locator("button:has-text('Pay')").first
                        if btn.is_visible(timeout=2000):
                            btn.click()
                            self.logger.info("  - 再次点击 Pay 按钮")
                            try:
                                popup.wait_for_event("close", timeout=30000)
                                self.logger.info("  ✓ 第二次点击后弹窗自动关闭")
                            except Exception:
                                pass
                            break
                    except Exception:
                        continue
                try:
                    if not popup.is_closed():
                        popup.close()
                        self.logger.info("  - Google Pay 弹窗已手动关闭")
                except Exception:
                    pass

        except Exception as e:
            self.logger.warning(f"  - 处理 Google Pay 弹窗异常: {e}")
            try:
                if not popup.is_closed():
                    popup.close()
            except Exception:
                pass

    def _google_signin_in_popup(self, popup, email: str, password: str) -> None:
        """
        在 Google 登录弹窗中完成邮箱+密码登录：
          1. 找到 input[type=email] → 填入邮箱 → 点击 Next/下一步
          2. 等待密码框出现 → 填入密码 → 点击 Next/下一步
          3. 等待页面跳转（networkidle）
        """
        _NEXT_TEXTS = ["Next", "下一步"]

        def _click_next(step_name: str) -> bool:
            all_tgts = [popup] + list(popup.frames)
            for txt in _NEXT_TEXTS:
                for tgt in all_tgts:
                    try:
                        btn = tgt.get_by_role("button", name=txt).first
                        if btn.is_visible(timeout=2000):
                            btn.click()
                            self.logger.info(f"  ✓ 点击 '{txt}'（{step_name}）")
                            return True
                    except Exception:
                        continue
                    try:
                        btn = tgt.locator(f"button:has-text('{txt}')").first
                        if btn.is_visible(timeout=1000):
                            btn.click()
                            self.logger.info(f"  ✓ 点击 '{txt}'（{step_name}，备选）")
                            return True
                    except Exception:
                        continue
            # 终极备选：Enter 键
            try:
                popup.keyboard.press("Enter")
                self.logger.info(f"  - Enter 键替代 Next（{step_name}）")
                return True
            except Exception:
                return False

        try:
            # 邮箱
            all_tgts = [popup] + list(popup.frames)
            email_filled = False
            for tgt in all_tgts:
                try:
                    inp = tgt.locator('input[type="email"]').first
                    if inp.is_visible(timeout=3000):
                        inp.click()
                        popup.wait_for_timeout(300)
                        inp.fill(email)
                        popup.wait_for_timeout(500)
                        self.logger.info(f"  - 已填写邮箱: {email}")
                        email_filled = True
                        break
                except Exception:
                    continue
            if not email_filled:
                self.logger.warning("  ✗ 未找到邮箱输入框")
                return
            _click_next("邮箱")
            # 等待 URL 从 /identifier 页离开（networkidle 可能在重定向完成前就触发，故用 JS 轮询）
            try:
                popup.wait_for_function(
                    "() => !location.href.includes('identifier')",
                    timeout=15000
                )
            except Exception:
                popup.wait_for_timeout(4000)
            popup.wait_for_timeout(1000)

            # 密码 - 支持多种选择器，超时延长至 15s
            pw_filled = False
            pw_selectors = [
                'input[type="password"]',
                'input[name="password"]',
                'input[name="Passwd"]',
                'input[autocomplete="current-password"]',
                'input[aria-label*="password" i]',
            ]
            for tgt in [popup] + list(popup.frames):
                if pw_filled:
                    break
                for pw_sel in pw_selectors:
                    try:
                        inp = tgt.locator(pw_sel).first
                        if inp.is_visible(timeout=15000):
                            inp.click()
                            popup.wait_for_timeout(300)
                            inp.fill(password)
                            popup.wait_for_timeout(500)
                            self.logger.info("  - 已填写密码")
                            pw_filled = True
                            break
                    except Exception:
                        continue
            if not pw_filled:
                self.logger.warning("  ✗ 未找到密码输入框")
                return
            _click_next("密码")
            # 等待页面加载（密码提交后可能有重定向）
            try:
                popup.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                popup.wait_for_timeout(3000)
            self.logger.info(f"  ✓ 登录提交完成，当前 URL: {popup.url[:100]}")
        except Exception as e:
            self.logger.warning(f"  - Google 登录弹窗异常: {e}")

    def _google_signin(self, page, email: str, password: str) -> None:
        """在独立 Google 账号登录页（非弹窗）完成邮箱 + 密码登录（兼容旧调用）"""
        try:
            page.wait_for_selector('input[type="email"]', timeout=10000)
            page.fill('input[type="email"]', email)
            self.logger.info(f"  - 已输入 Google 邮箱: {email}")
            page.wait_for_timeout(500)
            page.keyboard.press("Enter")
            page.wait_for_timeout(2500)
            page.wait_for_selector('input[type="password"]', timeout=15000)
            page.fill('input[type="password"]', password)
            self.logger.info("  - 已输入 Google 密码")
            page.wait_for_timeout(500)
            page.keyboard.press("Enter")
            page.wait_for_timeout(4000)
            self.logger.info(f"  ✓ Google 登录完成，当前 URL: {page.url[:80]}")
        except Exception as e:
            self.logger.warning(f"  - Google 登录步骤异常: {e}")

    def click_pay_button_in_iframe(self, payment_frame=None) -> bool:
        """
        点击 Airwallex iframe 内的 Pay 按钮。

        Args:
            payment_frame: 支付 iframe（若提供则优先在该 frame 中查找）

        Returns:
            bool: 是否成功点击
        """
        try:
            self.page.wait_for_timeout(3000)
            self.logger.info("  - 开始查找 iframe 内的 Pay 按钮...")
            if payment_frame:
                try:
                    pay_buttons = payment_frame.locator(
                        "button:has-text('Pay'), button:has-text('pay')"
                    ).all()
                    self.logger.info(f"    在指定 payment_frame 中找到 {len(pay_buttons)} 个 Pay 按钮")
                    for idx, btn in enumerate(pay_buttons):
                        try:
                            if btn.is_visible():
                                self.logger.info(f"    尝试点击第 {idx + 1} 个 Pay 按钮")
                                btn.click()
                                self.page.wait_for_timeout(15000)
                                self.logger.info("  ✓ 成功点击 iframe 内的 Pay 按钮")
                                return True
                        except Exception as e:
                            self.logger.info(f"    第 {idx + 1} 个按钮点击失败: {e}")
                            continue
                except Exception as e:
                    self.logger.warning(f"  在指定 iframe 中点击 Pay 失败: {e}")

            max_attempts = 3
            for attempt in range(max_attempts):
                self.logger.info(f"  - 第 {attempt + 1}/{max_attempts} 次尝试在所有 frame 中查找 Pay 按钮")
                for frame_idx, frame in enumerate(self.page.frames):
                    try:
                        frame_url = frame.url if hasattr(frame, 'url') else 'unknown'
                        pay_buttons = frame.locator(
                            "button:has-text('Pay'), button:has-text('pay')"
                        ).all()
                        if len(pay_buttons) > 0:
                            self.logger.info(
                                f"    Frame {frame_idx} ({frame_url[:50]}...): 找到 {len(pay_buttons)} 个 Pay 按钮"
                            )
                            for btn_idx, btn in enumerate(pay_buttons):
                                try:
                                    if btn.is_visible():
                                        self.logger.info(f"    尝试点击第 {btn_idx + 1} 个 Pay 按钮")
                                        btn.click()
                                        self.page.wait_for_timeout(15000)
                                        self.logger.info("  ✓ 成功点击 Pay 按钮")
                                        return True
                                except Exception:
                                    continue
                    except Exception:
                        continue
                if attempt < max_attempts - 1:
                    self.page.wait_for_timeout(3000)

            self.logger.warning("  ✗ 未找到可点击的 Pay 按钮")
            return False
        except Exception as e:
            self.logger.error(f"点击 iframe Pay 按钮失败: {e}")
            return False
