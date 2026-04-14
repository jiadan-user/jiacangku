# pages/purchase_orders_page.py
"""
Purchase Orders 页面对象
处理已购买订单列表和支付流程
"""
from pages.base_page import BasePage
from utils.logger import setup_logger
from playwright.sync_api import Page
import random


class PurchaseOrdersPage(BasePage):
    """Purchase Orders 页面对象"""
    
    # ========== 页面元素选择器 ==========
    # 头像和菜单
    AVATAR_BUTTON = "[class*='avatar']"
    AVATAR_BUTTON_BACKUP = "[class*='user']"
    PURCHASE_ORDERS_MENU = "text=/Purchase Orders/i"
    
    # 订单列表
    PENDING_TAB = "text=/^Pending$/i"
    ORDER_PRICE = "text=/\\$\\d+\\.\\d+/"
    
    # 订单详情页
    DETAIL_PAY_BUTTON = "button:has-text('Pay')"
    
    # 支付弹窗
    PAYMENT_MODAL = "[role='dialog']"
    REFRESH_BUTTON = "button:has-text('Refresh')"
    
    # 支付结果
    PAID_STATUS = "text=/Paid/i"
    
    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = setup_logger()
    
    def click_avatar(self):
        """点击头像打开菜单"""
        try:
            # 尝试主选择器
            avatar = self.page.locator(self.AVATAR_BUTTON)
            if avatar.count() > 0:
                avatar.first.click()
            else:
                # 备选方案
                self.page.locator(self.AVATAR_BUTTON_BACKUP).first.click()
            
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击头像失败: {e}")
            raise
    
    def click_purchase_orders(self):
        """点击 Purchase Orders 菜单"""
        try:
            self.page.click(self.PURCHASE_ORDERS_MENU)
            self.page.wait_for_timeout(5000)
        except Exception as e:
            self.logger.error(f"点击 Purchase Orders 失败: {e}")
            raise
    
    def navigate_to_purchase_orders(self):
        """导航到 Purchase Orders 页面"""
        try:
            self.click_avatar()
            self.click_purchase_orders()
        except Exception as e:
            self.logger.error(f"导航到 Purchase Orders 失败: {e}")
            raise
    
    def click_pending_tab(self):
        """点击 Pending 标签"""
        try:
            self.page.locator(self.PENDING_TAB).first.click()
            self.page.wait_for_timeout(3000)
        except Exception as e:
            self.logger.error(f"点击 Pending 标签失败: {e}")
            raise
    
    def has_pending_orders(self) -> bool:
        """检查是否有待支付订单"""
        try:
            price_elements = self.page.locator(self.ORDER_PRICE).all()
            return len(price_elements) > 0
        except Exception:
            return False
    
    def click_first_pending_order(self):
        """点击第一条待支付订单"""
        try:
            first_price = self.page.locator(self.ORDER_PRICE).first
            first_price.click()
            self.page.wait_for_timeout(5000)
        except Exception as e:
            self.logger.error(f"点击第一条订单失败: {e}")
            raise
    
    def click_detail_pay_button(self):
        """点击订单详情页的 Pay 按钮"""
        try:
            pay_buttons = [b for b in self.page.locator(self.DETAIL_PAY_BUTTON).all() if b.is_visible()]
            if len(pay_buttons) > 0:
                pay_buttons[0].click(force=True)
                # 增加等待时间，确保支付弹窗完全加载
                self.page.wait_for_timeout(12000)  # 从8秒增加到12秒
        except Exception as e:
            self.logger.error(f"点击 Pay 按钮失败: {e}")
            raise
    
    def is_refresh_button_visible(self) -> bool:
        """检查是否出现 Refresh 按钮（只在 iframe 内查找）"""
        try:
            # Refresh 按钮只会在 iframe 内，不会在主页面
            for frame in self.page.frames:
                try:
                    if frame.locator(self.REFRESH_BUTTON).is_visible(timeout=1000):
                        self.logger.info("  ⚠ 发现 iframe 内的 Refresh 按钮")
                        return True
                except:
                    continue
            return False
        except:
            return False
    
    def click_order_detail_refresh_button(self) -> bool:
        """点击订单详情页的 Refresh 按钮（通常在右上角）"""
        try:
            self.logger.info("  - 查找订单详情页的 Refresh 按钮...")
            refresh_selectors = [
                "button:has-text('Refresh')",  # 标准选择器
                "button:has-text('刷新')",  # 中文
                "[aria-label*='Refresh']",
                "[aria-label*='刷新']",
                "button[class*='refresh']",
                "button:has(svg[class*='refresh'])",  # 包含刷新图标的按钮
            ]
            
            for selector in refresh_selectors:
                try:
                    refresh_btn = self.page.locator(selector).first
                    if refresh_btn.is_visible(timeout=2000):
                        self.logger.info(f"  - 发现订单详情页 Refresh 按钮（选择器: {selector}），准备点击")
                        refresh_btn.click()
                        self.page.wait_for_timeout(2000)  # 等待页面刷新
                        self.logger.info("  ✓ 已点击订单详情页 Refresh 按钮")
                        return True
                except Exception as e:
                    continue
            
            self.logger.warning("  ⚠ 未找到订单详情页 Refresh 按钮")
            return False
        except Exception as e:
            self.logger.error(f"点击订单详情页 Refresh 按钮失败: {e}")
            return False
    
    def click_refresh_button(self):
        """点击支付弹窗中的 Refresh 按钮并关闭支付弹窗"""
        try:
            refresh_clicked = False
            
            # 方案1: 在 iframe 内查找并点击 Refresh 按钮（支付弹窗中的）
            for frame in self.page.frames:
                try:
                    refresh_btn = frame.locator(self.REFRESH_BUTTON)
                    if refresh_btn.is_visible(timeout=1000):
                        self.logger.info("  - 在支付弹窗 iframe 中发现 Refresh 按钮，准备点击")
                        refresh_btn.click()
                        self.page.wait_for_timeout(2000)
                        refresh_clicked = True
                        self.logger.info("  ✓ 已点击支付弹窗 Refresh 按钮")
                        break
                except:
                    continue
            
            if not refresh_clicked:
                self.logger.warning("  ⚠ 未找到支付弹窗 Refresh 按钮")
                
            # 方案2: 尝试点击关闭按钮（X）关闭支付弹窗
            self.logger.info("  - 尝试关闭支付弹窗...")
            close_selectors = [
                'button:has-text("×")',  # × 符号
                'button[aria-label*="close"]',
                'button[aria-label*="Close"]',
                '[class*="close"]',
                'button:has-text("Close")',
            ]
            
            for selector in close_selectors:
                try:
                    close_btn = self.page.locator(selector).first
                    if close_btn.is_visible(timeout=1000):
                        close_btn.click()
                        self.logger.info(f"  ✓ 使用选择器 {selector} 关闭了支付弹窗")
                        self.page.wait_for_timeout(2000)
                        return
                except:
                    continue
            
            # 方案3: 按 ESC 键关闭弹窗
            try:
                self.page.keyboard.press("Escape")
                self.logger.info("  ✓ 使用 ESC 键关闭了支付弹窗")
                self.page.wait_for_timeout(2000)
            except:
                pass
                
        except Exception as e:
            self.logger.error(f"处理 Refresh 按钮失败: {e}")
            raise
    
    def input_cvc_in_iframe(self) -> tuple[bool, str, any]:
        """
        在 iframe 中输入 CVC
        
        Returns:
            tuple[bool, str, Frame]: (是否成功, CVC值, 支付iframe)
        """
        try:
            cvc_value = str(random.randint(100, 999))
            cvc_input = None
            payment_frame = None
            
            # 不需要额外等待，调用方已经等待了
            self.logger.info(f"  - 开始在 iframe 中查找 CVC 输入框...")
            
            # 多次尝试查找CVC输入框（最多5次）
            max_find_attempts = 5
            for find_attempt in range(max_find_attempts):
                self.logger.info(f"  - 第 {find_attempt + 1}/{max_find_attempts} 次尝试查找 CVC 输入框")
                
                # 在所有 iframe 中查找 CVC 输入框
                for frame_idx, frame in enumerate(self.page.frames):
                    try:
                        # 获取 frame 的 URL 用于调试
                        frame_url = frame.url if hasattr(frame, 'url') else 'unknown'
                        
                        inputs = frame.locator("input").all()
                        self.logger.info(f"    Frame {frame_idx} ({frame_url[:50]}...): 找到 {len(inputs)} 个输入框")
                        
                        for inp_idx, inp in enumerate(inputs):
                            try:
                                # 获取输入框的所有属性
                                placeholder = inp.get_attribute("placeholder") or ""
                                name = inp.get_attribute("name") or ""
                                input_id = inp.get_attribute("id") or ""
                                input_class = inp.get_attribute("class") or ""
                                input_type = inp.get_attribute("type") or ""
                                aria_label = inp.get_attribute("aria-label") or ""
                                data_testid = inp.get_attribute("data-testid") or ""
                                
                                # 调试日志：输出所有输入框信息（不管是否包含关键词）
                                self.logger.info(
                                    f"      Input {inp_idx}: "
                                    f"placeholder='{placeholder}', "
                                    f"name='{name}', "
                                    f"id='{input_id}', "
                                    f"type='{input_type}', "
                                    f"class='{input_class[:50]}', "
                                    f"aria-label='{aria_label}', "
                                    f"visible={inp.is_visible()}"
                                )
                                
                                # 检查是否是 CVC 相关输入框（扩展匹配规则）
                                all_text = (placeholder + name + input_id + input_class + aria_label + data_testid).lower()
                                is_cvc_field = (
                                    'cvc' in all_text or 
                                    'cvv' in all_text or
                                    'security' in all_text or
                                    'card-cvc' in all_text or
                                    'cardcvc' in all_text or
                                    'verification' in all_text or
                                    # 如果输入框type是text/tel/number且长度限制为3-4，也可能是CVC
                                    (input_type in ['text', 'tel', 'number'] and 
                                     (inp.get_attribute("maxlength") in ['3', '4'] or
                                      'security' in placeholder.lower() or
                                      placeholder.strip().upper() == 'CVC'))
                                )
                                
                                if is_cvc_field and inp.is_visible():
                                    cvc_input = inp
                                    payment_frame = frame
                                    self.logger.info(f"      ✓ 找到 CVC 输入框！(Frame {frame_idx}, Input {inp_idx})")
                                    break
                            except Exception as e:
                                continue
                    except Exception as e:
                        continue
                    
                    if payment_frame:
                        break
                
                if cvc_input:
                    break
                
                # 如果没找到，等待后重试
                if find_attempt < max_find_attempts - 1:
                    self.logger.info(f"  - 未找到 CVC 输入框，等待 3 秒后重试...")
                    self.page.wait_for_timeout(3000)
            
            # 输入 CVC
            if cvc_input and payment_frame:
                self.logger.info(f"  - 准备输入 CVC: {cvc_value}")
                cvc_input.click()
                self.page.wait_for_timeout(1000)
                cvc_input.fill(cvc_value)
                self.page.wait_for_timeout(2000)
                self.logger.info(f"  ✓ CVC 输入成功: {cvc_value}")
                return True, cvc_value, payment_frame
            else:
                self.logger.warning(f"  ✗ 在所有 {len(self.page.frames)} 个 frame 中都未找到 CVC 输入框")
                return False, "", None
                
        except Exception as e:
            self.logger.error(f"输入 CVC 失败: {e}")
            return False, "", None
    
    def click_pay_button_in_iframe(self, payment_frame=None) -> bool:
        """
        点击 iframe 内的 Pay 按钮
        
        Args:
            payment_frame: 支付iframe（如果提供，则在该iframe中查找）
            
        Returns:
            bool: 是否成功点击
        """
        try:
            # 等待Pay按钮可能需要激活
            self.page.wait_for_timeout(3000)
            self.logger.info(f"  - 开始查找 iframe 内的 Pay 按钮...")
            
            # 如果提供了payment_frame，优先在该frame中查找
            if payment_frame:
                try:
                    self.logger.info(f"  - 在指定的 payment_frame 中查找 Pay 按钮")
                    pay_buttons = payment_frame.locator("button:has-text('Pay'), button:has-text('pay')").all()
                    self.logger.info(f"    找到 {len(pay_buttons)} 个 Pay 按钮")
                    
                    if len(pay_buttons) > 0:
                        for idx, btn in enumerate(pay_buttons):
                            try:
                                if btn.is_visible():
                                    self.logger.info(f"    尝试点击第 {idx + 1} 个 Pay 按钮")
                                    btn.click()
                                    self.page.wait_for_timeout(15000)  # 等待支付处理
                                    self.logger.info(f"  ✓ 成功点击 iframe 内的 Pay 按钮")
                                    return True
                            except Exception as e:
                                self.logger.info(f"    第 {idx + 1} 个按钮点击失败: {e}")
                                continue
                except Exception as e:
                    self.logger.warning(f"  在指定iframe中点击Pay失败: {e}")
            
            # 如果没有提供frame或上面失败了，尝试在所有frame中查找
            max_attempts = 3
            for attempt in range(max_attempts):
                self.logger.info(f"  - 第 {attempt + 1}/{max_attempts} 次尝试在所有 frame 中查找 Pay 按钮")
                
                for frame_idx, frame in enumerate(self.page.frames):
                    try:
                        frame_url = frame.url if hasattr(frame, 'url') else 'unknown'
                        pay_buttons = frame.locator("button:has-text('Pay'), button:has-text('pay')").all()
                        
                        if len(pay_buttons) > 0:
                            self.logger.info(f"    Frame {frame_idx} ({frame_url[:50]}...): 找到 {len(pay_buttons)} 个 Pay 按钮")
                            
                            # 找到第一个可见的Pay按钮
                            for btn_idx, btn in enumerate(pay_buttons):
                                try:
                                    if btn.is_visible():
                                        self.logger.info(f"    尝试点击 Frame {frame_idx} 的第 {btn_idx + 1} 个 Pay 按钮")
                                        btn.click()
                                        self.page.wait_for_timeout(15000)  # 等待支付处理
                                        self.logger.info(f"  ✓ 成功点击 iframe 内的 Pay 按钮")
                                        return True
                                except Exception as e:
                                    self.logger.info(f"    点击失败: {e}")
                                    continue
                    except Exception as e:
                        continue
                
                # 如果没找到，等待后重试
                if attempt < max_attempts - 1:
                    self.logger.info(f"  - 未找到可点击的 Pay 按钮，等待 3 秒后重试...")
                    self.page.wait_for_timeout(3000)
            
            self.logger.warning(f"  ✗ 在所有 {len(self.page.frames)} 个 frame 中都未找到可点击的 Pay 按钮")
            return False
                
        except Exception as e:
            self.logger.error(f"点击 iframe Pay 按钮失败: {e}")
            return False
    
    def is_payment_success(self) -> bool:
        """检查支付是否成功（Pay 按钮消失）"""
        try:
            visible_pay_buttons = [b for b in self.page.locator(self.DETAIL_PAY_BUTTON).all() if b.is_visible()]
            return len(visible_pay_buttons) == 0
        except:
            return False
    
    def is_paid_status_visible(self) -> bool:
        """检查 Paid 状态是否显示"""
        try:
            return self.page.locator(self.PAID_STATUS).is_visible(timeout=5000)
        except:
            return False
    
    def is_paid_status_selected(self) -> bool:
        """检查 Paid 状态是否被选中（进度条激活）- 主要检查圆圈中是否有 checkmark（对勾）"""
        try:
            if not self.is_paid_status_visible():
                self.logger.warning("  ⚠ Paid 状态不可见")
                return False
            
            paid_elem = self.page.locator(self.PAID_STATUS).first
            if not paid_elem.is_visible(timeout=2000):
                self.logger.warning("  ⚠ Paid 元素不可见")
                return False
            
            # 主要方法: 检查 Paid 状态对应的圆圈中是否有 checkmark（对勾）
            # 这是最可靠的检测方式：选中状态 = 圆圈中有白色对勾
            try:
                has_checkmark = paid_elem.evaluate("""
                    el => {
                        // 向上查找整个步骤项容器
                        let stepItem = el.closest('[class*="stepItem"], [class*="step-item"], [class*="stepsItem"]');
                        if (!stepItem) {
                            // 查找包含多个步骤的容器，然后找到 Paid 对应的步骤项
                            const allSteps = el.ownerDocument.querySelectorAll('[class*="stepItem"], [class*="step-item"], [class*="stepsItem"]');
                            for (let step of allSteps) {
                                if (step.textContent && step.textContent.trim().includes('Paid')) {
                                    stepItem = step;
                                    break;
                                }
                            }
                        }
                        
                        if (!stepItem) {
                            return false;
                        }
                        
                        // 在步骤项容器中查找圆圈和 checkmark
                        // 1. 查找 SVG 中的圆圈，检查是否有黑色填充（选中状态 = 黑色填充的圆圈）
                        const svgs = stepItem.querySelectorAll('svg');
                        for (let svg of svgs) {
                            // 查找圆圈元素
                            const circles = svg.querySelectorAll('circle');
                            
                            for (let circle of circles) {
                                const fill = circle.getAttribute('fill');
                                const style = window.getComputedStyle(circle);
                                const computedFill = style.fill;
                                
                                // 检查是否有黑色填充（选中状态通常是黑色填充）
                                const fillValue = fill || computedFill || '';
                                
                                // 检查是否是黑色填充
                                if (fillValue && fillValue !== 'none' && fillValue !== 'transparent' && fillValue !== 'rgba(0, 0, 0, 0)' && fillValue !== '') {
                                    // 检查是否是黑色或深色
                                    if (fillValue === 'black' || fillValue === '#000' || fillValue === '#000000' || 
                                        fillValue === 'rgb(0, 0, 0)' || fillValue.includes('rgb(0, 0, 0)')) {
                                        return true;  // 找到黑色填充的圆圈，说明已选中
                                    }
                                    
                                    // 检查 RGB 值是否是黑色或深色（亮度小于 50）
                                    const rgbMatch = fillValue.match(/\\d+/g);
                                    if (rgbMatch && rgbMatch.length >= 3) {
                                        const r = parseInt(rgbMatch[0]);
                                        const g = parseInt(rgbMatch[1]);
                                        const b = parseInt(rgbMatch[2]);
                                        const brightness = (r + g + b) / 3;
                                        // 如果亮度小于 50，说明是黑色或深色填充
                                        if (brightness < 50) {
                                            return true;  // 找到黑色/深色填充的圆圈，说明已选中
                                        }
                                    }
                                }
                            }
                        }
                        
                        // 2. 如果找到黑色填充的圆圈，再检查是否有 checkmark（对勾）
                        // 重新查找，因为上面已经检查了填充，这里检查 checkmark
                        for (let svg of svgs) {
                            const circles = svg.querySelectorAll('circle');
                            let hasFilledCircle = false;
                            
                            // 检查是否有填充的圆圈
                            for (let circle of circles) {
                                const fill = circle.getAttribute('fill');
                                const style = window.getComputedStyle(circle);
                                const computedFill = style.fill;
                                
                                if ((fill && fill !== 'none' && fill !== 'transparent' && fill !== '') ||
                                    (computedFill && computedFill !== 'none' && computedFill !== 'transparent' && computedFill !== 'rgba(0, 0, 0, 0)')) {
                                    hasFilledCircle = true;
                                    break;
                                }
                            }
                            
                            // 如果找到填充的圆圈，检查是否有 checkmark（path、polyline 或 line）
                            if (hasFilledCircle) {
                                const paths = svg.querySelectorAll('path, polyline, line');
                                if (paths.length > 0) {
                                    // 检查是否有可见的 path（checkmark 通常是白色或浅色的 path）
                                    for (let path of paths) {
                                        const stroke = path.getAttribute('stroke');
                                        const style = window.getComputedStyle(path);
                                        const computedStroke = style.stroke;
                                        
                                        // checkmark 通常是白色或浅色的 stroke
                                        if (stroke && (stroke === 'white' || stroke === '#fff' || stroke === '#ffffff')) {
                                            return true;
                                        }
                                        if (computedStroke && (computedStroke === 'rgb(255, 255, 255)' || computedStroke.includes('255, 255, 255'))) {
                                            return true;
                                        }
                                        // 或者检查路径长度（checkmark 通常有特定的长度）
                                        const pathLength = path.getTotalLength();
                                        if (pathLength > 0 && pathLength < 100) {  // checkmark 通常较短
                                            return true;
                                        }
                                    }
                                }
                            }
                        }
                        
                        // 2. 检查 HTML 内容中是否包含 checkmark 符号（✓ 或 ✔）
                        const html = stepItem.innerHTML;
                        if (html.includes('✓') || html.includes('✔')) {
                            return true;
                        }
                        
                        // 3. 检查是否有 checkmark 相关的元素或 class
                        const checkmarkElements = stepItem.querySelectorAll('[class*="check"], [class*="checkmark"], svg[class*="check"]');
                        if (checkmarkElements.length > 0) {
                            return true;
                        }
                        
                        return false;
                    }
                """)
                
                if has_checkmark:
                    # 检查具体是哪种方式检测到的
                    check_type = paid_elem.evaluate("""
                        el => {
                            let stepItem = el.closest('[class*="stepItem"], [class*="step-item"], [class*="stepsItem"]');
                            if (!stepItem) {
                                const allSteps = el.ownerDocument.querySelectorAll('[class*="stepItem"], [class*="step-item"], [class*="stepsItem"]');
                                for (let step of allSteps) {
                                    if (step.textContent && step.textContent.trim().includes('Paid')) {
                                        stepItem = step;
                                        break;
                                    }
                                }
                            }
                            if (!stepItem) return 'unknown';
                            
                            const svgs = stepItem.querySelectorAll('svg');
                            for (let svg of svgs) {
                                const circles = svg.querySelectorAll('circle');
                                for (let circle of circles) {
                                    const fill = circle.getAttribute('fill');
                                    const style = window.getComputedStyle(circle);
                                    const computedFill = style.fill || '';
                                    const fillValue = fill || computedFill;
                                    
                                    if (fillValue && fillValue !== 'none' && fillValue !== 'transparent' && fillValue !== 'rgba(0, 0, 0, 0)' && fillValue !== '') {
                                        if (fillValue === 'black' || fillValue === '#000' || fillValue === '#000000' || 
                                            fillValue === 'rgb(0, 0, 0)' || fillValue.includes('rgb(0, 0, 0)')) {
                                            return 'black_fill';
                                        }
                                        const rgbMatch = fillValue.match(/\\d+/g);
                                        if (rgbMatch && rgbMatch.length >= 3) {
                                            const r = parseInt(rgbMatch[0]);
                                            const g = parseInt(rgbMatch[1]);
                                            const b = parseInt(rgbMatch[2]);
                                            const brightness = (r + g + b) / 3;
                                            if (brightness < 50) {
                                                return 'dark_fill';
                                            }
                                        }
                                    }
                                }
                            }
                            return 'checkmark';
                        }
                    """)
                    
                    if check_type == 'black_fill' or check_type == 'dark_fill':
                        self.logger.info(f"  ✓ 通过黑色填充检测到 Paid 状态已激活（圆圈有黑色填充）")
                    else:
                        self.logger.info("  ✓ 通过 checkmark 检测到 Paid 状态已激活（圆圈中有对勾）")
                    return True
                else:
                    self.logger.info("  - 未在圆圈中检测到黑色填充或 checkmark")
            except Exception as e:
                self.logger.info(f"  - 检查 checkmark 失败: {e}")
            
            # 备用方法1: 检查父元素的 class
            try:
                parent_class = paid_elem.evaluate("el => el.closest('[class*=\"step\"], [class*=\"status\"], [class*=\"progress\"]')?.className || ''")
                self.logger.info(f"  - 父元素 class: {parent_class[:200]}")
                if any(word in parent_class.lower() for word in ['active', 'selected', 'current', 'completed']):
                    self.logger.info("  ✓ 通过父元素 class 检测到 Paid 状态已激活")
                    return True
            except Exception as e:
                self.logger.info(f"  - 检查父元素 class 失败: {e}")
            
            # 备用方法2: 通过对比 Placed 和 Paid 的状态来判断
            # 如果 Placed 有 checkmark（已完成），且 Paid 在 Placed 之后且可见，那么 Paid 也应该有 checkmark
            try:
                placed_elem = self.page.locator("text=/Placed/i").first
                if placed_elem.is_visible(timeout=1000):
                    # 检查 Placed 是否有填充的圆圈（选中状态）
                    placed_is_selected = placed_elem.evaluate("""
                        el => {
                            // 查找 Placed 的步骤项容器
                            let stepItem = el.closest('[class*="stepItem"], [class*="step-item"], [class*="stepsItem"]');
                            if (!stepItem) {
                                stepItem = el.closest('[class*="step"], [class*="status"], [class*="progress"]');
                            }
                            if (!stepItem) return false;
                            
                            // 检查是否有填充的圆圈
                            const svgs = stepItem.querySelectorAll('svg');
                            for (let svg of svgs) {
                                const circles = svg.querySelectorAll('circle');
                                for (let circle of circles) {
                                    const fill = circle.getAttribute('fill');
                                    if (fill && fill !== 'none' && fill !== 'transparent' && fill !== '') {
                                        return true;
                                    }
                                    const style = window.getComputedStyle(circle);
                                    const bgColor = style.fill || style.backgroundColor;
                                    if (bgColor && bgColor !== 'rgba(0, 0, 0, 0)' && bgColor !== 'transparent') {
                                        const rgb = bgColor.match(/\\d+/g);
                                        if (rgb && rgb.length >= 3) {
                                            const brightness = (parseInt(rgb[0]) + parseInt(rgb[1]) + parseInt(rgb[2])) / 3;
                                            if (brightness < 100) {
                                                return true;
                                            }
                                        }
                                    }
                                }
                            }
                            return false;
                        }
                    """)
                    
                    if placed_is_selected:
                        # 如果 Placed 有 checkmark（已完成），且 Paid 在 Placed 之后且可见，那么 Paid 也应该有
                        self.logger.info("  ✓ 通过对比检查：Placed 已完成（有 checkmark），Paid 应该也已完成")
                        return True
                    else:
                        self.logger.info("  - Placed 状态未完成，无法通过对比判断 Paid 状态")
            except Exception as e:
                self.logger.info(f"  - 对比检查失败: {e}")
            
            # 备用方法3: 如果 Paid 状态可见，且没有 Pay 按钮，可以认为 Paid 已完成
            # 这是一个最后的备用检查
            try:
                no_pay_button = self.is_payment_success()
                if no_pay_button:
                    self.logger.info("  ✓ 通过备用检查：无 Pay 按钮，说明支付已完成，Paid 应该已选中")
                    return True
            except:
                pass
            
            self.logger.warning("  ⚠ 未检测到 Paid 状态被选中（进度条未激活）")
            return False
        except Exception as e:
            self.logger.error(f"检查 Paid 状态选中失败: {e}")
            return False
    
    def click_google_pay_button_in_iframe(self) -> tuple[bool, any]:
        """
        在第三方支付弹窗中点击 'Buy with G Pay' 按钮
        
        Returns:
            tuple[bool, Page]: (是否成功点击, 新窗口页面对象，如果有的话)
        """
        try:
            self.logger.info("  - 开始查找 iframe 中的 'Buy with G Pay' 按钮...")
            
            # 记录当前窗口数量
            context = self.page.context
            pages_before = len(context.pages)
            
            max_attempts = 5
            for attempt in range(max_attempts):
                self.logger.info(f"  - 第 {attempt + 1}/{max_attempts} 次尝试查找 Google Pay 按钮")
                
                # 先等待一下，让按钮加载
                if attempt > 0:
                    self.page.wait_for_timeout(2000)
                
                for frame_idx, frame in enumerate(self.page.frames):
                    try:
                        frame_url = frame.url if hasattr(frame, 'url') else 'unknown'
                        
                        # 尝试多种选择器匹配 Google Pay 按钮
                        google_pay_selectors = [
                            # 精确文本匹配（最优先）
                            "button:has-text('Buy with G Pay')",
                            "button:has-text('Buy with Google Pay')",
                            # 部分文本匹配
                            "button:has-text('G Pay')",
                            "button:has-text('Google Pay')",
                            # 包含文本的元素
                            "[role='button']:has-text('Buy with G Pay')",
                            "[role='button']:has-text('G Pay')",
                            # 属性匹配
                            "[aria-label*='Google Pay']",
                            "[aria-label*='G Pay']",
                            "[aria-label*='Buy with']",
                            # 类名匹配
                            "[class*='google-pay']",
                            "[class*='gpay']",
                            "[class*='googlePay']",
                            "[class*='GooglePay']",
                            # 包含 Google Pay 文本的任何可点击元素
                            "div:has-text('Buy with G Pay'):has(button)",
                            "div[class*='google']:has-text('Pay')",
                        ]
                        
                        for selector in google_pay_selectors:
                            try:
                                buttons = frame.locator(selector).all()
                                if len(buttons) > 0:
                                    self.logger.info(f"    Frame {frame_idx}: 找到 {len(buttons)} 个 Google Pay 按钮（选择器: {selector}）")
                                    
                                    for btn_idx, btn in enumerate(buttons):
                                        try:
                                            # 检查按钮是否可见
                                            if not btn.is_visible(timeout=2000):
                                                self.logger.info(f"    按钮 {btn_idx + 1} 不可见，跳过")
                                                continue
                                            
                                            # 获取按钮信息用于调试
                                            try:
                                                btn_text = btn.inner_text()
                                                btn_class = btn.get_attribute("class") or ""
                                                self.logger.info(f"    找到按钮 {btn_idx + 1}: 文本='{btn_text}', class='{btn_class[:50]}'")
                                            except:
                                                pass
                                            
                                            self.logger.info(f"    尝试点击 Frame {frame_idx} 的第 {btn_idx + 1} 个 Google Pay 按钮")
                                            
                                            # 先滚动到按钮位置，确保可见
                                            btn.scroll_into_view_if_needed()
                                            self.page.wait_for_timeout(500)
                                            
                                            # 尝试多种点击方式
                                            click_success = False
                                            
                                            # 方式1: 普通点击
                                            try:
                                                btn.click(timeout=5000)
                                                self.logger.info("  ✓ 使用普通点击方式")
                                                click_success = True
                                            except Exception as e1:
                                                self.logger.info(f"  普通点击失败: {str(e1)[:50]}")
                                            
                                            # 方式2: 强制点击
                                            if not click_success:
                                                try:
                                                    btn.click(force=True, timeout=5000)
                                                    self.logger.info("  ✓ 使用强制点击方式")
                                                    click_success = True
                                                except Exception as e2:
                                                    self.logger.info(f"  强制点击失败: {str(e2)[:50]}")
                                            
                                            # 方式3: JavaScript 点击
                                            if not click_success:
                                                try:
                                                    btn.evaluate("el => el.click()")
                                                    self.logger.info("  ✓ 使用 JavaScript 点击方式")
                                                    click_success = True
                                                except Exception as e3:
                                                    self.logger.info(f"  JavaScript 点击失败: {str(e3)[:50]}")
                                            
                                            if not click_success:
                                                self.logger.warning("  ✗ 所有点击方式都失败")
                                                continue
                                            
                                            self.logger.info("  ✓ 已点击 Google Pay 按钮")
                                            
                                            # 等待并检查是否有新窗口打开（最多等待30秒）
                                            self.logger.info("  - 等待 Google 登录弹窗打开...")
                                            
                                            # 使用 context.expect_page() 监听新窗口
                                            try:
                                                with context.expect_page(timeout=30000) as new_page_info:
                                                    # 等待新窗口打开
                                                    new_page = new_page_info.value
                                                    self.logger.info("  ✓ 检测到新窗口打开")
                                                    try:
                                                        new_page.wait_for_load_state("domcontentloaded", timeout=15000)
                                                        new_url = new_page.url
                                                        self.logger.info(f"  新窗口 URL: {new_url[:100]}")
                                                        if "accounts.google.com" in new_url or "google.com" in new_url:
                                                            self.logger.info(f"  ✓ 确认是 Google 登录页面")
                                                            return True, new_page
                                                    except Exception as e:
                                                        self.logger.info(f"  等待新窗口加载时出错: {e}")
                                            except Exception as e:
                                                self.logger.info(f"  未通过 expect_page 检测到新窗口: {e}")
                                            
                                            # 如果 expect_page 没有检测到，继续轮询检查
                                            for wait_attempt in range(30):
                                                self.page.wait_for_timeout(1000)
                                                
                                                # 检查新窗口
                                                pages_after = len(context.pages)
                                                if pages_after > pages_before:
                                                    new_page = context.pages[-1]  # 获取最新打开的窗口
                                                    self.logger.info(f"  ✓ 轮询检测到新窗口打开（等待了 {wait_attempt + 1} 秒）")
                                                    try:
                                                        new_page.wait_for_load_state("domcontentloaded", timeout=10000)
                                                        new_url = new_page.url
                                                        self.logger.info(f"  新窗口 URL: {new_url[:100]}")
                                                        if "accounts.google.com" in new_url or "google.com" in new_url:
                                                            self.logger.info(f"  ✓ 确认是 Google 登录页面")
                                                            return True, new_page
                                                    except Exception as e:
                                                        self.logger.info(f"  检查新窗口时出错: {e}")
                                                
                                                # 检查是否有新的 iframe 包含 Google 登录页面
                                                for frame in self.page.frames:
                                                    try:
                                                        frame_url = frame.url if hasattr(frame, 'url') else ''
                                                        if 'accounts.google.com' in frame_url:
                                                            self.logger.info(f"  ✓ 在 iframe 中找到 Google 登录页面: {frame_url[:100]}")
                                                            return True, frame  # 返回找到的 frame 对象
                                                    except:
                                                        pass
                                                
                                                # 检查 pay.google.com iframe 中的嵌套 iframe
                                                for frame in self.page.frames:
                                                    try:
                                                        frame_url = frame.url if hasattr(frame, 'url') else ''
                                                        if 'pay.google.com' in frame_url:
                                                            # 检查嵌套的 iframe
                                                            try:
                                                                for child_frame in frame.child_frames:
                                                                    child_url = child_frame.url if hasattr(child_frame, 'url') else ''
                                                                    if 'accounts.google.com' in child_url:
                                                                        self.logger.info(f"  ✓ 在 pay.google.com 的嵌套 iframe 中找到 Google 登录页面: {child_url[:100]}")
                                                                        return True, child_frame  # 返回找到的嵌套 frame 对象
                                                            except:
                                                                pass
                                                    except:
                                                        pass
                                            
                                            # 如果没有新窗口，等待并检查 iframe 中的登录表单
                                            self.logger.info("  - 未检测到新窗口，等待并检查 iframe 中的登录表单...")
                                            
                                            # 增加等待时间，让 iframe 有足够时间加载（最多等待20秒）
                                            max_wait_seconds = 20
                                            found_frame = None
                                            
                                            for wait_sec in range(max_wait_seconds):
                                                self.page.wait_for_timeout(1000)
                                                self.logger.info(f"  - 等待 iframe 加载... ({wait_sec + 1}/{max_wait_seconds} 秒)")
                                                
                                                # 检查是否有 accounts.google.com 的 frame（优先）
                                                for frame in self.page.frames:
                                                    try:
                                                        frame_url = frame.url if hasattr(frame, 'url') else ''
                                                        if 'accounts.google.com' in frame_url:
                                                            self.logger.info(f"  ✓ 找到 accounts.google.com iframe: {frame_url[:100]}")
                                                            found_frame = frame
                                                            break
                                                    except:
                                                        continue
                                                
                                                if found_frame:
                                                    break
                                                
                                                # 检查 pay.google.com iframe 中的嵌套 iframe
                                                for frame in self.page.frames:
                                                    try:
                                                        frame_url = frame.url if hasattr(frame, 'url') else ''
                                                        if 'pay.google.com' in frame_url:
                                                            self.logger.info(f"  ✓ 找到 pay.google.com iframe: {frame_url[:100]}")
                                                            # 检查嵌套的 iframe
                                                            try:
                                                                for nested_frame in frame.child_frames:
                                                                    nested_url = nested_frame.url if hasattr(nested_frame, 'url') else ''
                                                                    if 'accounts.google.com' in nested_url:
                                                                        self.logger.info(f"  ✓ 在 pay.google.com 的嵌套 iframe 中找到 accounts.google.com: {nested_url[:100]}")
                                                                        found_frame = nested_frame
                                                                        break
                                                                if found_frame:
                                                                    break
                                                            except Exception as e:
                                                                self.logger.info(f"    检查嵌套 iframe 时出错: {e}")
                                                                pass
                                                    except:
                                                        continue
                                                
                                                if found_frame:
                                                    break
                                            
                                            if found_frame:
                                                self.logger.info(f"  ✓ 成功找到 Google 登录 frame，返回 frame 对象")
                                                return True, found_frame
                                            else:
                                                self.logger.warning("  ⚠ 未找到 accounts.google.com frame，但点击成功")
                                                return True, None
                                        except Exception as e:
                                            self.logger.info(f"    点击失败: {e}")
                                            continue
                            except:
                                continue
                    except Exception as e:
                        continue
                
                # 如果没找到，等待后重试
                if attempt < max_attempts - 1:
                    self.logger.info(f"  - 未找到 Google Pay 按钮，等待 3 秒后重试...")
                    self.page.wait_for_timeout(3000)
            
            self.logger.warning(f"  ✗ 在所有 {len(self.page.frames)} 个 frame 中都未找到 Google Pay 按钮")
            return False, None
                
        except Exception as e:
            self.logger.error(f"点击 Google Pay 按钮失败: {e}")
            return False, None
    
    def _collect_all_frames_recursive(self, page_or_frame, depth=0, max_depth=5, path="", collected=None):
        """
        递归收集所有 iframe（包括嵌套的）
        
        Args:
            page_or_frame: Page 或 Frame 对象
            depth: 当前深度
            max_depth: 最大深度
            path: 当前路径（用于日志）
            collected: 已收集的 frame 列表
            
        Returns:
            list: [(path, frame, url, depth), ...]
        """
        if collected is None:
            collected = []
        
        if depth > max_depth:
            return collected
        
        try:
            # 获取所有直接子 frame
            frames = page_or_frame.frames if hasattr(page_or_frame, 'frames') else []
            
            for idx, frame in enumerate(frames):
                try:
                    frame_url = frame.url if hasattr(frame, 'url') else 'unknown'
                    current_path = f"{path}.{idx}" if path else str(idx)
                    
                    # 记录 frame 信息
                    indent = "  " * depth
                    self.logger.info(f"{indent}Frame {current_path} (深度 {depth}): {frame_url[:150]}")
                    
                    # 添加到收集列表
                    collected.append((current_path, frame, frame_url, depth))
                    
                    # 递归检查子 frame
                    if depth < max_depth:
                        try:
                            child_frames = frame.child_frames if hasattr(frame, 'child_frames') else []
                            if len(child_frames) > 0:
                                self.logger.info(f"{indent}  → 发现 {len(child_frames)} 个子 frame，开始递归检查...")
                                self._collect_all_frames_recursive(frame, depth + 1, max_depth, current_path, collected)
                        except Exception as e:
                            self.logger.info(f"{indent}  ⚠ 检查子 frame 时出错: {e}")
                except Exception as e:
                    self.logger.info(f"  ⚠ 处理 frame {idx} 时出错: {e}")
                    continue
            
            return collected
        except Exception as e:
            self.logger.error(f"收集 frame 时出错: {e}")
            return collected
    
    def _wait_for_pay_google_frame(self, base_page, max_wait_seconds=60):
        """
        等待 pay.google.com iframe 加载完成
        
        Args:
            base_page: 基础页面对象
            max_wait_seconds: 最大等待时间（秒）
            
        Returns:
            Frame: 找到的 pay.google.com frame，如果未找到则返回 None
        """
        self.logger.info("="*70)
        self.logger.info("  等待 pay.google.com frame 加载...")
        self.logger.info("="*70)
        
        pay_google_frame = None
        
        # 查找 pay.google.com 的 frame
        self.logger.info("  - 开始查找 pay.google.com frame...")
        for wait_sec in range(max_wait_seconds):
            try:
                # 获取所有 frame（只检查直接子 frame，不递归）
                frames = base_page.frames if hasattr(base_page, 'frames') else []
                self.logger.info(f"  - 第 {wait_sec + 1}/{max_wait_seconds} 秒：检查 {len(frames)} 个 frame...")
                    
                for frame_idx, frame in enumerate(frames):
                    try:
                        frame_url = frame.url if hasattr(frame, 'url') else 'unknown'
                        self.logger.info(f"    Frame {frame_idx}: {frame_url[:150]}")
                            
                        if 'pay.google.com' in frame_url:
                            self.logger.info(f"  ✓ 找到 pay.google.com frame: Frame {frame_idx}")
                            self.logger.info(f"    URL: {frame_url[:150]}")
                            pay_google_frame = frame
                            break
                    except Exception as e:
                        self.logger.info(f"    Frame {frame_idx} 检查失败: {e}")
                        continue
                    
                if pay_google_frame:
                    break
            
                if wait_sec < max_wait_seconds - 1:
                    self.page.wait_for_timeout(2000)  # 每2秒检查一次
            except Exception as e:
                self.logger.info(f"  ⚠ 查找 pay.google.com 时出错: {e}")
                if wait_sec < max_wait_seconds - 1:
                    self.page.wait_for_timeout(2000)
        
        if not pay_google_frame:
            self.logger.warning("  ⚠ 未找到 pay.google.com frame（超时）")
            return None
                
        # 等待 pay.google.com frame 加载完成
        self.logger.info("  - 等待 pay.google.com frame 加载完成...")
        try:
            pay_google_frame.wait_for_load_state("domcontentloaded", timeout=30000)
            self.logger.info("  ✓ pay.google.com frame DOM 加载完成")
        except Exception as e:
            self.logger.info(f"  ⚠ DOM 加载等待超时: {e}，继续...")
        
        # 关键：等待 frame 内容从 pay.google.com 变成 accounts.google.com
        self.logger.info("  - 等待 frame 内容从 pay.google.com 变成 accounts.google.com...")
        self.logger.info("    注意：弹窗还是同一个弹窗，只是内容会变化")
        
        initial_url = pay_google_frame.url if hasattr(pay_google_frame, 'url') else ''
        self.logger.info(f"    初始 URL: {initial_url[:150]}")
        
        max_wait_for_change = 60  # 最多等待60秒
        for wait_sec in range(max_wait_for_change):
            try:
                current_url = pay_google_frame.url if hasattr(pay_google_frame, 'url') else ''
                
                # 每5秒输出一次日志，或者检测到变化时输出
                if wait_sec % 5 == 0 or 'accounts.google.com' in current_url:
                    self.logger.info(f"  - 第 {wait_sec + 1}/{max_wait_for_change} 秒：检查内容变化...")
                    self.logger.info(f"    当前 URL: {current_url[:150]}")
                
                # 检查 URL 是否包含 accounts.google.com
                if 'accounts.google.com' in current_url:
                    self.logger.info("  ✓ frame 内容已变成 accounts.google.com！")
                    # 等待页面完全加载
                    try:
                        pay_google_frame.wait_for_load_state("domcontentloaded", timeout=10000)
                        self.logger.info("  ✓ accounts.google.com 页面加载完成")
                    except:
                        self.logger.info("  ⚠ 等待页面加载超时，继续...")
                        break
                
                # 如果 URL 还没变化，检查 frame 内部是否有 accounts.google.com 的内容
                # 通过查找邮箱输入框来判断内容是否已加载
                try:
                    # 尝试查找邮箱输入框（快速检查）
                    test_inputs = pay_google_frame.locator("input[type='email'], input[placeholder*='邮箱'], input[placeholder*='Email']").all()
                    if len(test_inputs) > 0:
                        self.logger.info(f"  ✓ 检测到 frame 内已有输入框（{len(test_inputs)} 个），内容可能已加载")
                        # 再等待一下确保完全加载
                        self.page.wait_for_timeout(3000)
                        break
                except:
                    pass
                
                # 等待后重试
                if wait_sec < max_wait_for_change - 1:
                    self.page.wait_for_timeout(2000)  # 每2秒检查一次
            except Exception as e:
                if wait_sec % 5 == 0:  # 每5秒输出一次错误
                    self.logger.info(f"  ⚠ 检查内容变化时出错: {e}")
                if wait_sec < max_wait_for_change - 1:
                    self.page.wait_for_timeout(2000)
        
        # 额外等待一段时间，确保页面内容完全渲染
        self.logger.info("  - 等待页面内容完全渲染（3秒）...")
        self.page.wait_for_timeout(3000)
            
        final_url = pay_google_frame.url if hasattr(pay_google_frame, 'url') else ''
        self.logger.info(f"  ✓ frame 已准备就绪")
        self.logger.info(f"    最终 URL: {final_url[:150]}")
        if 'accounts.google.com' in final_url:
            self.logger.info("  ✓ 确认 frame 内容已变成 accounts.google.com")
        else:
            self.logger.info("  ⚠ URL 仍为 pay.google.com，但会在该 frame 中查找邮箱输入框")
        self.logger.info("="*70)
        
        return pay_google_frame
    
    def _check_if_payment_page_loaded(self, target_page) -> bool:
        """
        检查是否已经到达付款页面
        
        Args:
            target_page: 目标页面对象（可能是 Page 或 Frame）
            
        Returns:
            bool: 如果已到达付款页面返回 True，否则返回 False
        """
        try:
            self.logger.info("  - 检查付款页面是否已加载...")
            
            # 检查 URL 是否包含 pay.google.com
            try:
                page_url = target_page.url if hasattr(target_page, 'url') else ''
                if 'pay.google.com' in page_url and '/pay' in page_url:
                    self.logger.info(f"    URL 包含 pay.google.com/pay: {page_url[:100]}")
                else:
                    self.logger.info(f"    URL: {page_url[:100]}")
            except:
                pass
            
            # 检查是否有 Pay 或 付款 按钮
            pay_button_selectors = [
                "button:has-text('付款')",
                "button:has-text('Pay')",
                "button:has-text('Confirm')",
            ]
            
            for selector in pay_button_selectors:
                try:
                    buttons = target_page.locator(selector).all()
                    if len(buttons) > 0:
                        for btn in buttons:
                            try:
                                if btn.is_visible(timeout=2000):
                                    btn_text = btn.inner_text()
                                    self.logger.info(f"    ✓ 找到付款按钮: '{btn_text}'（选择器: {selector}）")
                                    return True
                            except:
                                continue
                except:
                    continue
                    
            # 检查是否有 "Total to pay" 或 "Total" 文本
            try:
                page_text = target_page.locator("body").inner_text() if target_page.locator("body").count() > 0 else ""
                if "Total to pay" in page_text or "Total" in page_text or "付款" in page_text:
                    self.logger.info("    ✓ 页面包含付款相关文本")
                    return True
            except:
                pass
            
            self.logger.info("    - 未检测到付款页面")
            return False
            
        except Exception as e:
            self.logger.info(f"    - 检查付款页面时出错: {e}")
            return False
    
    def _handle_google_pay_intermediate_pages(self, target_page):
        """
        处理 Google Pay 登录后的中间页面
        
        Args:
            target_page: 目标页面对象（可能是 Page 或 Frame）
        """
        try:
            self.logger.info("="*70)
            self.logger.info("  处理 Google Pay 登录后的中间页面...")
            self.logger.info("="*70)
            
            # 等待页面加载
            target_page.wait_for_timeout(3000)
            
            # 步骤1: 检查是否有"设置住址"页面，点击"跳过"
            self.logger.info("  - 步骤1: 检查是否有'设置住址'页面...")
            skip_selectors = [
                "button:has-text('跳过')",  # 中文界面（优先）
                "a:has-text('跳过')",  # 可能是链接
                "button:has-text('Skip')",
                "a:has-text('Skip')",
                "[aria-label*='跳过']",
                "[aria-label*='Skip']",
            ]
            
            skip_clicked = False
            for selector in skip_selectors:
                try:
                    elements = target_page.locator(selector).all()
                    for elem in elements:
                        try:
                            if elem.is_visible(timeout=3000):
                                elem_text = elem.inner_text()
                                self.logger.info(f"    找到'跳过'按钮: '{elem_text}'")
                                elem.click()
                                target_page.wait_for_timeout(3000)
                                self.logger.info("  ✓ 已点击'跳过'按钮")
                                skip_clicked = True
                                break
                        except:
                            continue
                    if skip_clicked:
                        break
                except:
                    continue
            
            if not skip_clicked:
                self.logger.info("  - 未找到'设置住址'页面，继续...")
            
            # 步骤2: 检查是否有其他设置页面，点击"以后再说"
            self.logger.info("  - 步骤2: 检查是否有其他设置页面...")
            later_selectors = [
                "button:has-text('以后再说')",  # 中文界面（优先）
                "a:has-text('以后再说')",
                "button:has-text('Later')",
                "a:has-text('Later')",
                "button:has-text('Not now')",
                "a:has-text('Not now')",
                "[aria-label*='以后再说']",
                "[aria-label*='Later']",
            ]
            
            later_clicked = False
            for selector in later_selectors:
                try:
                    elements = target_page.locator(selector).all()
                    for elem in elements:
                        try:
                            if elem.is_visible(timeout=3000):
                                elem_text = elem.inner_text()
                                self.logger.info(f"    找到'以后再说'按钮: '{elem_text}'")
                                elem.click()
                                target_page.wait_for_timeout(3000)
                                self.logger.info("  ✓ 已点击'以后再说'按钮")
                                later_clicked = True
                                break
                        except:
                            continue
                    if later_clicked:
                        break
                except:
                    continue
            
            if not later_clicked:
                self.logger.info("  - 未找到'以后再说'页面，继续...")
            
            # 等待到达付款页面
            self.logger.info("  - 等待到达付款页面...")
            target_page.wait_for_timeout(5000)
            
            self.logger.info("="*70)
            self.logger.info("  ✓ 中间页面处理完成")
            self.logger.info("="*70)
            
        except Exception as e:
            self.logger.warning(f"  ⚠ 处理中间页面时出错: {e}，继续...")
    
    def _find_email_input_in_frame(self, target_frame, email_selectors, max_attempts=10):
        """
        在指定的 frame 中查找邮箱输入框
        
        Args:
            target_frame: 目标 frame 对象
            email_selectors: 邮箱输入框选择器列表
            max_attempts: 最大尝试次数
            
        Returns:
            tuple: (email_input, target_frame) 或 (None, None)
        """
        self.logger.info("="*70)
        self.logger.info("  开始在 pay.google.com frame 中查找邮箱输入框...")
        self.logger.info("="*70)
        
        frame_url = target_frame.url if hasattr(target_frame, 'url') else 'unknown'
        self.logger.info(f"  目标 frame URL: {frame_url[:150]}")
        self.logger.info(f"  将尝试 {len(email_selectors)} 种选择器，最多尝试 {max_attempts} 次")
        self.logger.info("  注意：该 frame 可能从 pay.google.com 变成 accounts.google.com，但仍是同一个 frame")
        self.logger.info("="*70)
        
        # 先检查是否有 Google 的错误提示（自动化检测）
        try:
            error_texts = [
                "面向应用开发者的信息",
                "使用 Google 账号登录",
                "需要迁移至更安全的替代方法",
                "改用基于浏览器的 OAuth",
                "渐进式 Web 应用",
                "automated software",
                "automated testing",
                "This browser or app may not be secure"
            ]
            
            page_text = target_frame.locator("body").inner_text() if target_frame.locator("body").count() > 0 else ""
            
            for error_text in error_texts:
                if error_text in page_text:
                    self.logger.error("="*70)
                    self.logger.error("  ⚠ Google 检测到自动化工具，阻止登录")
                    self.logger.error("="*70)
                    self.logger.error("  错误信息：Google 检测到这是通过自动化工具访问的")
                    self.logger.error("  建议解决方案：")
                    self.logger.error("    1. 确保浏览器不是 headless 模式")
                    self.logger.error("    2. 使用真实的浏览器环境")
                    self.logger.error("    3. 考虑使用其他支付方式（如银行卡支付）")
                    self.logger.error("="*70)
                    # 不返回 None，继续尝试查找，但记录警告
                    break
        except Exception as e:
            self.logger.info(f"  - 检查错误提示时出错: {e}")
        
        # 先检查 frame 内是否有任何 input 元素（用于调试）
        try:
            all_inputs = target_frame.locator("input").all()
            self.logger.info(f"  - 调试信息：frame 内共有 {len(all_inputs)} 个 input 元素")
            if len(all_inputs) > 0:
                for idx, inp in enumerate(all_inputs[:5]):  # 只显示前5个
                    try:
                        inp_type = inp.get_attribute("type") or ""
                        inp_placeholder = inp.get_attribute("placeholder") or ""
                        inp_name = inp.get_attribute("name") or ""
                        self.logger.info(f"    Input {idx + 1}: type='{inp_type}', placeholder='{inp_placeholder}', name='{inp_name}'")
                    except:
                        pass
        except Exception as e:
            self.logger.info(f"  - 调试信息：检查 input 元素时出错: {e}")
        
        for attempt in range(max_attempts):
            self.logger.info(f"  - 第 {attempt + 1}/{max_attempts} 次尝试查找邮箱输入框...")
            
            # 尝试所有选择器
            for selector_idx, selector in enumerate(email_selectors):
                self.logger.info(f"    尝试选择器 {selector_idx + 1}/{len(email_selectors)}: {selector}")
                try:
                    inputs = target_frame.locator(selector).all()
                    self.logger.info(f"      找到 {len(inputs)} 个匹配的输入框")
                    
                    if len(inputs) == 0:
                        self.logger.info(f"      → 未找到匹配的输入框，继续下一个选择器...")
                        continue
                    
                    for inp_idx, inp in enumerate(inputs):
                        try:
                            self.logger.info(f"      检查输入框 {inp_idx + 1}/{len(inputs)}...")
                            
                            # 获取输入框详细信息
                            placeholder = inp.get_attribute("placeholder") or ""
                            input_type = inp.get_attribute("type") or ""
                            input_name = inp.get_attribute("name") or ""
                            input_id = inp.get_attribute("id") or ""
                            input_class = inp.get_attribute("class") or ""
                            
                            self.logger.info(f"        - placeholder: '{placeholder}'")
                            self.logger.info(f"        - type: '{input_type}'")
                            self.logger.info(f"        - name: '{input_name}'")
                            self.logger.info(f"        - id: '{input_id}'")
                            self.logger.info(f"        - class: '{input_class[:50]}'")
                            
                            # 检查是否可见
                            if inp.is_visible(timeout=2000):
                                self.logger.info(f"        ✓ 输入框 {inp_idx + 1} 可见！")
                                self.logger.info("="*70)
                                self.logger.info(f"  ✓ 成功找到邮箱输入框！")
                                self.logger.info(f"    选择器: {selector}")
                                self.logger.info(f"    输入框索引: {inp_idx + 1}")
                                self.logger.info("="*70)
                                return inp, target_frame
                            else:
                                self.logger.info(f"        ✗ 输入框 {inp_idx + 1} 不可见")
                        except Exception as e:
                            self.logger.info(f"        ✗ 检查输入框 {inp_idx + 1} 时出错: {str(e)[:100]}")
                            continue
                            
                except Exception as e:
                    self.logger.info(f"      ✗ 选择器 {selector} 执行失败: {str(e)[:100]}")
                    continue
            
            # 如果这次尝试没找到，等待后重试
            if attempt < max_attempts - 1:
                wait_time = 3000
                self.logger.info(f"  - 本次尝试未找到邮箱输入框，等待 {wait_time/1000} 秒后重试...")
                self.page.wait_for_timeout(wait_time)
        
        self.logger.info("="*70)
        self.logger.info("  ✗ 在所有尝试中都未找到邮箱输入框")
        self.logger.info("="*70)
        return None, None
    
    def login_google_pay(self, email: str, password: str, google_pay_page=None) -> bool:
        """
        在 Google Pay 弹窗中登录 Google 账号
        
        Args:
            email: Google 账号邮箱
            password: Google 账号密码
            google_pay_page: Google Pay 页面对象或 Frame 对象（如果在新窗口中打开或在 iframe 中）
            
        Returns:
            bool: 是否成功登录
        """
        try:
            self.logger.info("  - 开始 Google Pay 登录流程...")
            self.logger.info(f"  - 目标邮箱: {email}")
            
            # 简化逻辑：直接等待 pay.google.com 加载完成
            target_page = None
            skip_detection = False
            
            # 如果传入的是 pay.google.com frame 对象，直接使用它
            if google_pay_page and hasattr(google_pay_page, 'url'):
                try:
                    frame_url = google_pay_page.url
                    if 'pay.google.com' in frame_url:
                        self.logger.info(f"  ✓ 使用传入的 pay.google.com frame 对象: {frame_url[:100]}")
                        target_page = google_pay_page
                        # 等待 frame 加载完成
                        try:
                            target_page.wait_for_load_state("domcontentloaded", timeout=10000)
                            self.logger.info("  ✓ Frame 已加载完成")
                        except:
                            self.page.wait_for_timeout(3000)
                        skip_detection = True
                except:
                    pass
            
            # 如果没有传入 frame，等待 pay.google.com 加载完成
            if not skip_detection:
                self.logger.info("="*70)
                self.logger.info("  步骤1: 等待 pay.google.com frame 加载...")
                self.logger.info("="*70)
                base_page = google_pay_page if google_pay_page else self.page
                
                pay_google_frame = self._wait_for_pay_google_frame(base_page, max_wait_seconds=60)
                
                if not pay_google_frame:
                    self.logger.error("  ✗ 未找到 pay.google.com frame，登录失败")
                    return False
                
                target_page = pay_google_frame
                self.logger.info("  ✓ pay.google.com frame 已找到并加载完成")
            
            # 在 pay.google.com frame 中查找邮箱输入框
            self.logger.info("="*70)
            self.logger.info("  步骤2: 在 pay.google.com frame 中查找邮箱输入框...")
            self.logger.info("="*70)
            
            email_selectors = [
                "input[placeholder='邮箱或电话号码']",  # 最优先
                "input[placeholder*='邮箱或电话号码']",
                "input[type='email']",
                "input[name='identifier']",
                "input[id*='identifier']",
                "input[placeholder*='邮箱']",
                "input[autocomplete='username']",
                "input[placeholder*='Email']",
                "input[placeholder*='email']",
            ]
            
            email_input, target_frame = self._find_email_input_in_frame(
                target_page, email_selectors, max_attempts=10
            )
            
            if not email_input:
                self.logger.error("  ✗ 未找到邮箱输入框，登录失败")
                return False
                
            # 更新 target_page 为找到输入框的 frame
            target_page = target_frame
            
            # 如果找到了邮箱输入框，开始输入邮箱
            if email_input:
                self.logger.info("="*60)
                self.logger.info("  开始输入邮箱")
                self.logger.info("="*60)
                
                # 输入邮箱
                self.logger.info(f"  - 准备输入邮箱: {email}")
                try:
                    self.logger.info("  - 点击邮箱输入框...")
                    email_input.click()
                    target_page.wait_for_timeout(500)
                    self.logger.info("  ✓ 已点击邮箱输入框")
                    
                    self.logger.info("  - 清空输入框...")
                    email_input.clear()  # 先清空
                    target_page.wait_for_timeout(200)
                    self.logger.info("  ✓ 已清空输入框")
                    
                    self.logger.info("  - 输入邮箱地址...")
                    email_input.fill(email)
                    target_page.wait_for_timeout(1000)
                    
                    # 验证输入是否成功
                    input_value = email_input.input_value()
                    self.logger.info(f"  - 验证输入值: {input_value}")
                    if input_value == email:
                        self.logger.info(f"  ✓ 邮箱输入完成并验证成功: {email}")
                    else:
                        self.logger.warning(f"  ⚠ 输入值不匹配，期望: {email}, 实际: {input_value}")
                except Exception as e:
                    self.logger.warning(f"  ⚠ 使用 fill 方法失败: {e}，尝试使用 type 方法")
                    try:
                        email_input.type(email, delay=100)
                        target_page.wait_for_timeout(1000)
                        input_value = email_input.input_value()
                        self.logger.info(f"  ✓ 使用 type 方法输入完成，验证值: {input_value}")
                    except Exception as e2:
                        self.logger.error(f"  ✗ 输入邮箱失败: {e2}")
                        return False
                    
                # 查找并点击"下一步"按钮（包括中文界面）
                self.logger.info("="*60)
                self.logger.info("  查找'下一步'按钮")
                self.logger.info("="*60)
                
                next_selectors = [
                    "button:has-text('下一步')",  # 中文界面（优先）
                    "button:has-text('Next')",
                    "button[id*='next']",
                    "button[type='button']:has-text('下一步')",  # 中文界面
                    "button[type='button']:has-text('Next')",
                    "button[aria-label*='下一步']",  # 中文界面
                    "button[aria-label*='Next']",
                ]
                
                next_button = None
                # 在 accounts.google.com 窗口中查找
                self.logger.info("  - 在 accounts.google.com 窗口中查找'下一步'按钮...")
                for selector in next_selectors:
                    try:
                        buttons = target_page.locator(selector).all()
                        self.logger.info(f"    选择器 {selector}: 找到 {len(buttons)} 个按钮")
                        for btn_idx, btn in enumerate(buttons):
                            try:
                                if btn.is_visible(timeout=2000):
                                    btn_text = btn.inner_text()
                                    self.logger.info(f"      按钮 {btn_idx + 1} 可见，文本: '{btn_text}'")
                                    next_button = btn
                                    self.logger.info(f"    ✓ 找到'下一步'按钮（选择器: {selector}）")
                                    break
                            except Exception as e:
                                self.logger.info(f"      按钮 {btn_idx + 1} 不可见: {e}")
                                continue
                        if next_button:
                            break
                    except Exception as e:
                        self.logger.info(f"    选择器 {selector} 失败: {e}")
                        continue
                
                if next_button:
                    self.logger.info("  - 点击'下一步'按钮...")
                    try:
                        next_button.click()
                        target_page.wait_for_timeout(5000)  # 增加等待时间
                        self.logger.info("  ✓ 已点击'下一步'按钮")
                    except Exception as e:
                        self.logger.warning(f"  ⚠ 点击失败: {e}，尝试使用 JavaScript")
                        try:
                            next_button.evaluate("el => el.click()")
                            target_page.wait_for_timeout(5000)
                            self.logger.info("  ✓ 使用 JavaScript 点击成功")
                        except Exception as e2:
                            self.logger.error(f"  ✗ JavaScript 点击也失败: {e2}")
                            return False
                else:
                    self.logger.warning("  ⚠ 未找到'下一步'按钮，尝试按 Enter 键")
                    try:
                        email_input.press("Enter")
                        target_page.wait_for_timeout(5000)
                        self.logger.info("  ✓ 已按 Enter 键")
                    except Exception as e:
                        self.logger.error(f"  ✗ 按 Enter 键失败: {e}")
                        return False
                
                # 检查是否出现 Google 错误页面
                self.logger.info("  - 检查是否出现 Google 错误页面...")
                try:
                    page_text = target_page.locator("body").inner_text() if target_page.locator("body").count() > 0 else ""
                    error_indicators = [
                        "Couldn't sign you in",
                        "This browser or app may not be secure",
                        "Try using a different browser",
                        "Try again"
                    ]
                    
                    for indicator in error_indicators:
                        if indicator in page_text:
                            self.logger.error("="*70)
                            self.logger.error("  ⚠ Google 检测到自动化工具，阻止登录")
                            self.logger.error("="*70)
                            self.logger.error("  错误信息：'Couldn't sign you in'")
                            self.logger.error("  原因：Google 检测到这是通过自动化工具访问的")
                            self.logger.error("")
                            self.logger.error("  解决方案：")
                            self.logger.error("    1. Google Pay 登录无法通过自动化工具完成")
                            self.logger.error("    2. 建议使用银行卡支付方式（test_purchase_orders_payment_should_success）")
                            self.logger.error("    3. 或者需要手动完成 Google Pay 登录流程")
                            self.logger.error("="*70)
                            return False
                except Exception as e:
                    self.logger.info(f"  - 检查错误页面时出错: {e}")
                
                # 等待密码输入框出现
                self.logger.info("="*60)
                self.logger.info("  等待密码输入框出现...")
                self.logger.info("="*60)
                target_page.wait_for_timeout(5000)  # 增加等待时间
                
                # 输入密码（包括中文界面）
                password_selectors = [
                    "input[type='password']",
                    "input[name='password']",
                    "input[id*='password']",
                    "input[aria-label*='Password']",
                    "input[aria-label*='password']",
                    "input[placeholder*='Password']",
                    "input[placeholder*='password']",
                    "input[placeholder*='密码']",  # 中文界面
                    "input[placeholder*='输入您的密码']",  # 中文界面
                ]
                
                password_input = None
                # 在 accounts.google.com 窗口中查找密码输入框
                self.logger.info("  - 在 accounts.google.com 窗口中查找密码输入框...")
                for selector in password_selectors:
                    try:
                        inputs = target_page.locator(selector).all()
                        self.logger.info(f"    选择器 {selector}: 找到 {len(inputs)} 个输入框")
                        for inp_idx, inp in enumerate(inputs):
                            try:
                                if inp.is_visible(timeout=3000):
                                    placeholder = inp.get_attribute("placeholder") or ""
                                    self.logger.info(f"      输入框 {inp_idx + 1} 可见，placeholder: '{placeholder}'")
                                    password_input = inp
                                    self.logger.info(f"    ✓ 找到密码输入框（选择器: {selector}）")
                                    break
                            except Exception as e:
                                self.logger.info(f"      输入框 {inp_idx + 1} 不可见: {e}")
                                continue
                        if password_input:
                            break
                    except Exception as e:
                        self.logger.info(f"    选择器 {selector} 失败: {e}")
                        continue
                
                if password_input:
                    self.logger.info("="*60)
                    self.logger.info("  开始输入密码")
                    self.logger.info("="*60)
                    self.logger.info("  - 点击密码输入框...")
                    try:
                        password_input.click()
                        target_page.wait_for_timeout(500)
                        self.logger.info("  ✓ 已点击密码输入框")
                        
                        self.logger.info("  - 清空输入框...")
                        password_input.clear()  # 先清空
                        target_page.wait_for_timeout(200)
                        self.logger.info("  ✓ 已清空输入框")
                        
                        self.logger.info("  - 输入密码...")
                        password_input.fill(password)
                        target_page.wait_for_timeout(1000)
                        self.logger.info("  ✓ 密码输入完成")
                    except Exception as e:
                        self.logger.warning(f"  ⚠ 使用 fill 方法失败: {e}，尝试使用 type 方法")
                        try:
                            password_input.type(password, delay=100)
                            target_page.wait_for_timeout(1000)
                            self.logger.info("  ✓ 使用 type 方法输入完成")
                        except Exception as e2:
                            self.logger.error(f"  ✗ 输入密码失败: {e2}")
                            return False
                    
                    # 查找并点击"下一步"或"登录"按钮（包括中文界面）
                    self.logger.info("="*60)
                    self.logger.info("  查找登录按钮")
                    self.logger.info("="*60)
                    
                    login_selectors = [
                        "button:has-text('下一步')",  # 中文界面（优先）
                        "button:has-text('登录')",  # 中文界面
                        "button:has-text('Next')",
                        "button:has-text('Sign in')",
                        "button:has-text('Sign In')",
                        "button[id*='next']",
                        "button[type='button']:has-text('下一步')",  # 中文界面
                        "button[type='button']:has-text('Next')",
                        "button[type='submit']",
                    ]
                    
                    login_button = None
                    # 在 accounts.google.com 窗口中查找
                    self.logger.info("  - 在 accounts.google.com 窗口中查找登录按钮...")
                    for selector in login_selectors:
                        try:
                            buttons = target_page.locator(selector).all()
                            self.logger.info(f"    选择器 {selector}: 找到 {len(buttons)} 个按钮")
                            for btn_idx, btn in enumerate(buttons):
                                try:
                                    if btn.is_visible(timeout=2000):
                                        btn_text = btn.inner_text()
                                        self.logger.info(f"      按钮 {btn_idx + 1} 可见，文本: '{btn_text}'")
                                        login_button = btn
                                        self.logger.info(f"    ✓ 找到登录按钮（选择器: {selector}）")
                                        break
                                except Exception as e:
                                    self.logger.info(f"      按钮 {btn_idx + 1} 不可见: {e}")
                                    continue
                            if login_button:
                                break
                        except Exception as e:
                            self.logger.info(f"    选择器 {selector} 失败: {e}")
                            continue
                    
                    if login_button:
                        self.logger.info("  - 点击登录按钮...")
                        try:
                            login_button.click()
                            target_page.wait_for_timeout(5000)  # 等待登录完成
                            self.logger.info("  ✓ 已点击登录按钮，等待登录完成...")
                            
                            # 登录成功后，检查是否直接到达付款页面
                            self.logger.info("  - 检查是否直接到达付款页面...")
                            if self._check_if_payment_page_loaded(target_page):
                                self.logger.info("  ✓ 已直接到达付款页面，无需处理中间页面")
                            else:
                                # 如果没有到达付款页面，尝试处理中间页面
                                self.logger.info("  - 未到达付款页面，尝试处理中间页面...")
                                self._handle_google_pay_intermediate_pages(target_page)
                            
                            self.logger.info("  ✓ Google Pay 登录成功")
                            return True
                        except Exception as e:
                            self.logger.warning(f"  ⚠ 点击失败: {e}，尝试使用 JavaScript")
                            try:
                                login_button.evaluate("el => el.click()")
                                target_page.wait_for_timeout(5000)
                                self.logger.info("  ✓ 使用 JavaScript 点击成功")
                                
                                # 登录成功后，检查是否直接到达付款页面
                                self.logger.info("  - 检查是否直接到达付款页面...")
                                if self._check_if_payment_page_loaded(target_page):
                                    self.logger.info("  ✓ 已直接到达付款页面，无需处理中间页面")
                                else:
                                    # 如果没有到达付款页面，尝试处理中间页面
                                    self.logger.info("  - 未到达付款页面，尝试处理中间页面...")
                                    self._handle_google_pay_intermediate_pages(target_page)
                                
                                self.logger.info("  ✓ Google Pay 登录成功")
                                return True
                            except Exception as e2:
                                self.logger.error(f"  ✗ JavaScript 点击也失败: {e2}")
                                return False
                    else:
                        self.logger.warning("  ⚠ 未找到登录按钮，尝试按 Enter 键")
                        try:
                            password_input.press("Enter")
                            target_page.wait_for_timeout(5000)
                            self.logger.info("  ✓ 已按 Enter 键")
                            
                            # 登录成功后，检查是否直接到达付款页面
                            self.logger.info("  - 检查是否直接到达付款页面...")
                            if self._check_if_payment_page_loaded(target_page):
                                self.logger.info("  ✓ 已直接到达付款页面，无需处理中间页面")
                            else:
                                # 如果没有到达付款页面，尝试处理中间页面
                                self.logger.info("  - 未到达付款页面，尝试处理中间页面...")
                                self._handle_google_pay_intermediate_pages(target_page)
                            
                            self.logger.info("  ✓ Google Pay 登录成功（使用 Enter 键）")
                            return True
                        except Exception as e:
                            self.logger.error(f"  ✗ 按 Enter 键失败: {e}")
                            return False
                else:
                    self.logger.warning("  ⚠ 未找到密码输入框")
            return False
                
        except Exception as e:
            self.logger.error(f"Google Pay 登录失败: {e}")
            return False
    
    def click_google_pay_confirm_button(self, google_pay_page=None) -> bool:
        """
        在 Google Pay 弹窗中点击 '付款' 按钮
        
        Args:
            google_pay_page: Google Pay 页面对象（如果在新窗口中打开，可能是 Page 或 Frame）
        
        Returns:
            bool: 是否成功点击
        """
        try:
            self.logger.info("="*70)
            self.logger.info("  开始查找 Google Pay 弹窗中的 '付款' 按钮...")
            self.logger.info("="*70)
            
            # 首先检查所有打开的窗口，找到 pay.google.com 的窗口
            pay_google_window = None
            context = self.page.context
            
            self.logger.info("  - 检查所有打开的窗口...")
            all_pages = context.pages
            self.logger.info(f"    当前有 {len(all_pages)} 个窗口/页面")
            
            for page_idx, page in enumerate(all_pages):
                try:
                    page_url = page.url
                    self.logger.info(f"    窗口 {page_idx}: {page_url[:100]}")
                    if 'pay.google.com' in page_url and '/pay' in page_url:
                        self.logger.info(f"  ✓ 找到 Google Pay 窗口: {page_url[:100]}")
                        pay_google_window = page
                        break
                except Exception as e:
                    self.logger.info(f"    窗口 {page_idx} 检查失败: {e}")
                    continue
            
            # 确定使用哪个页面进行查找
            # 优先使用找到的 pay.google.com 窗口
            if pay_google_window:
                target_page = pay_google_window
                self.logger.info(f"  ✓ 将使用 Google Pay 窗口查找付款按钮")
            elif google_pay_page:
                # 检查是否是 Page 对象（新窗口）
                if hasattr(google_pay_page, 'url') and hasattr(google_pay_page, 'frames'):
                    try:
                        page_url = google_pay_page.url
                        if 'pay.google.com' in page_url or 'accounts.google.com' in page_url:
                            self.logger.info(f"  使用传入的 Google Pay 页面: {page_url[:100]}")
                            target_page = google_pay_page
                        else:
                            target_page = self.page
                    except:
                        target_page = self.page
                else:
                    # 可能是 Frame 对象
                    target_page = self.page
            else:
                target_page = self.page
                self.logger.info("  ⚠ 未找到 Google Pay 窗口，将在主页面查找")
            
            max_attempts = 10  # 增加尝试次数
            for attempt in range(max_attempts):
                self.logger.info(f"  - 第 {attempt + 1}/{max_attempts} 次尝试查找付款按钮...")
                
                # 尝试多种选择器匹配付款按钮（优先中文）
                pay_confirm_selectors = [
                    "button:has-text('付款')",  # 中文界面（最优先）
                    "button:has-text('Pay')",
                    "button:has-text('Confirm')",
                    "button:has-text('确认')",
                    "[aria-label*='付款']",
                    "[aria-label*='Pay']",
                    "[class*='pay-button']",
                    "[class*='confirm-button']",
                    "button[type='button']:has-text('付款')",
                    "button[type='submit']:has-text('付款')",
                ]
                
                # 方法1: 优先在 Google Pay 窗口中查找
                if pay_google_window:
                    try:
                        page_url = pay_google_window.url
                        self.logger.info(f"    在 Google Pay 窗口中查找: {page_url[:100]}")
                        
                        # 等待页面完全加载
                        try:
                            pay_google_window.wait_for_load_state("domcontentloaded", timeout=10000)
                        except:
                            pass
                        pay_google_window.wait_for_timeout(2000)
                        
                        # 方法1.1: 查找所有按钮，然后检查文本内容（更通用）
                        self.logger.info("    方法1.1: 查找所有按钮元素...")
                        try:
                            all_buttons = pay_google_window.locator("button").all()
                            self.logger.info(f"      找到 {len(all_buttons)} 个按钮元素")
                            for btn_idx, btn in enumerate(all_buttons):
                                try:
                                    if btn.is_visible(timeout=1000):
                                        btn_text = btn.inner_text().strip()
                                        btn_aria_label = btn.get_attribute("aria-label") or ""
                                        self.logger.info(f"        按钮 {btn_idx + 1}: 文本='{btn_text}', aria-label='{btn_aria_label}'")
                                        
                                        # 检查是否包含 Pay/付款相关的文本
                                        if any(keyword in btn_text.lower() for keyword in ['pay', '付款', 'confirm', '确认']) or \
                                           any(keyword in btn_aria_label.lower() for keyword in ['pay', '付款', 'confirm', '确认']):
                                            self.logger.info(f"      ✓ 找到匹配的付款按钮: '{btn_text}'")
                                            
                                            # 尝试点击
                                            try:
                                                btn.click(timeout=5000)
                                                self.logger.info("        ✓ 使用普通点击方式")
                                                pay_google_window.wait_for_timeout(10000)
                                                self.logger.info(f"  ✓ 成功点击付款按钮")
                                                return True
                                            except Exception as e1:
                                                self.logger.info(f"        普通点击失败: {str(e1)[:100]}")
                                                try:
                                                    btn.evaluate("el => el.click()")
                                                    self.logger.info("        ✓ 使用 JavaScript 点击方式")
                                                    pay_google_window.wait_for_timeout(10000)
                                                    self.logger.info(f"  ✓ 成功点击付款按钮")
                                                    return True
                                                except Exception as e2:
                                                    self.logger.info(f"        JavaScript 点击失败: {str(e2)[:100]}")
                                                    try:
                                                        btn.click(force=True, timeout=5000)
                                                        self.logger.info("        ✓ 使用强制点击方式")
                                                        pay_google_window.wait_for_timeout(10000)
                                                        self.logger.info(f"  ✓ 成功点击付款按钮")
                                                        return True
                                                    except Exception as e3:
                                                        self.logger.info(f"        强制点击失败: {str(e3)[:100]}")
                                except:
                                    continue
                        except Exception as e:
                            self.logger.info(f"      查找所有按钮失败: {e}")
                        
                        # 方法1.2: 在 iframe 中查找
                        self.logger.info(f"    方法1.2: 在 Google Pay 窗口的 iframe 中查找（共 {len(pay_google_window.frames)} 个）...")
                        for frame_idx, frame in enumerate(pay_google_window.frames):
                            try:
                                frame_url = frame.url if hasattr(frame, 'url') else 'unknown'
                                self.logger.info(f"      Frame {frame_idx}: {frame_url[:100]}")
                                
                                # 在 iframe 中查找所有按钮
                                try:
                                    frame_buttons = frame.locator("button").all()
                                    self.logger.info(f"        找到 {len(frame_buttons)} 个按钮")
                                    for btn_idx, btn in enumerate(frame_buttons):
                                        try:
                                            if btn.is_visible(timeout=1000):
                                                btn_text = btn.inner_text().strip()
                                                btn_aria_label = btn.get_attribute("aria-label") or ""
                                                self.logger.info(f"          按钮 {btn_idx + 1}: 文本='{btn_text}', aria-label='{btn_aria_label}'")
                                                
                                                if any(keyword in btn_text.lower() for keyword in ['pay', '付款', 'confirm', '确认']) or \
                                                   any(keyword in btn_aria_label.lower() for keyword in ['pay', '付款', 'confirm', '确认']):
                                                    self.logger.info(f"        ✓ 在 iframe 中找到匹配的付款按钮: '{btn_text}'")
                                                    
                                                    try:
                                                        btn.click(timeout=5000)
                                                        self.logger.info("          ✓ 使用普通点击方式")
                                                        pay_google_window.wait_for_timeout(10000)
                                                        self.logger.info(f"  ✓ 成功点击付款按钮")
                                                        return True
                                                    except:
                                                        try:
                                                            btn.evaluate("el => el.click()")
                                                            self.logger.info("          ✓ 使用 JavaScript 点击方式")
                                                            pay_google_window.wait_for_timeout(10000)
                                                            self.logger.info(f"  ✓ 成功点击付款按钮")
                                                            return True
                                                        except:
                                                            btn.click(force=True, timeout=5000)
                                                            self.logger.info("          ✓ 使用强制点击方式")
                                                            pay_google_window.wait_for_timeout(10000)
                                                            self.logger.info(f"  ✓ 成功点击付款按钮")
                                                            return True
                                        except:
                                            continue
                                except Exception as e:
                                    self.logger.info(f"        Frame {frame_idx} 查找按钮失败: {e}")
                            except:
                                continue
                        
                        # 方法1.3: 使用选择器查找
                        self.logger.info("    方法1.3: 使用选择器查找...")
                        for selector in pay_confirm_selectors:
                            try:
                                buttons = pay_google_window.locator(selector).all()
                                self.logger.info(f"      选择器 {selector}: 找到 {len(buttons)} 个按钮")
                                for btn_idx, btn in enumerate(buttons):
                                    try:
                                        if btn.is_visible(timeout=2000):
                                            btn_text = btn.inner_text()
                                            self.logger.info(f"        按钮 {btn_idx + 1} 可见，文本: '{btn_text}'")
                                            
                                            # 检查按钮是否在正确的页面中（避免点击主页面的按钮）
                                            try:
                                                btn_url = btn.evaluate("el => window.location.href")
                                                if 'pay.google.com' not in btn_url:
                                                    self.logger.info(f"        按钮不在 pay.google.com 页面，跳过")
                                                    continue
                                            except:
                                                pass
                                            
                                            self.logger.info(f"      ✓ 在 Google Pay 窗口找到付款按钮（选择器: {selector}）")
                                            
                                            # 尝试多种点击方式
                                            click_success = False
                                            
                                            # 方式1: 普通点击
                                            try:
                                                btn.click(timeout=5000)
                                                self.logger.info("        ✓ 使用普通点击方式")
                                                click_success = True
                                            except Exception as e1:
                                                self.logger.info(f"        普通点击失败: {str(e1)[:100]}")
                                                
                                                # 如果被 dialog 拦截，尝试关闭 dialog
                                                if 'intercepts pointer events' in str(e1) or 'dialog' in str(e1).lower():
                                                    self.logger.info("        检测到 dialog 拦截，尝试关闭 dialog...")
                                                    try:
                                                        # 尝试关闭 dialog
                                                        dialogs = pay_google_window.locator("[role='dialog']").all()
                                                        for dialog in dialogs:
                                                            try:
                                                                close_btn = dialog.locator("button[aria-label*='close'], button[aria-label*='Close'], [class*='close']").first
                                                                if close_btn.is_visible(timeout=1000):
                                                                    close_btn.click()
                                                                    pay_google_window.wait_for_timeout(1000)
                                                                    self.logger.info("        ✓ 已关闭 dialog")
                                                                    break
                                                            except:
                                                                continue
                                                    except:
                                                        pass
                                            
                                            # 方式2: JavaScript 点击（如果普通点击失败）
                                            if not click_success:
                                                try:
                                                    btn.evaluate("el => el.click()")
                                                    self.logger.info("        ✓ 使用 JavaScript 点击方式")
                                                    click_success = True
                                                except Exception as e2:
                                                    self.logger.info(f"        JavaScript 点击失败: {str(e2)[:100]}")
                                            
                                            # 方式3: 强制点击
                                            if not click_success:
                                                try:
                                                    btn.click(force=True, timeout=5000)
                                                    self.logger.info("        ✓ 使用强制点击方式")
                                                    click_success = True
                                                except Exception as e3:
                                                    self.logger.info(f"        强制点击失败: {str(e3)[:100]}")
                                            
                                            if click_success:
                                                pay_google_window.wait_for_timeout(10000)  # 等待支付处理
                                                self.logger.info(f"  ✓ 成功点击付款按钮")
                                                return True
                                            else:
                                                self.logger.warning(f"        ✗ 所有点击方式都失败")
                                    except Exception as e:
                                        self.logger.info(f"        按钮 {btn_idx + 1} 处理失败: {e}")
                                        continue
                            except Exception as e:
                                self.logger.info(f"      选择器 {selector} 失败: {e}")
                                continue
                    except Exception as e:
                        self.logger.info(f"    在 Google Pay 窗口查找时出错: {e}")
                
                # 方法2: 如果传入的 google_pay_page 是有效的，也在其中查找
                if google_pay_page and hasattr(google_pay_page, 'url') and google_pay_page != pay_google_window:
                    try:
                        page_url = google_pay_page.url
                        if 'pay.google.com' in page_url:
                            self.logger.info(f"    在传入的 Google Pay 页面中查找: {page_url[:100]}")
                            for selector in pay_confirm_selectors:
                                try:
                                    buttons = google_pay_page.locator(selector).all()
                                    self.logger.info(f"      选择器 {selector}: 找到 {len(buttons)} 个按钮")
                                    for btn_idx, btn in enumerate(buttons):
                                        try:
                                            if btn.is_visible(timeout=2000):
                                                btn_text = btn.inner_text()
                                                self.logger.info(f"        按钮 {btn_idx + 1} 可见，文本: '{btn_text}'")
                                                self.logger.info(f"      ✓ 在 Google Pay 页面找到付款按钮（选择器: {selector}）")
                                                
                                                # 尝试点击
                                                try:
                                                    btn.click(timeout=5000)
                                                    self.logger.info("        ✓ 使用普通点击方式")
                                                except:
                                                    try:
                                                        btn.evaluate("el => el.click()")
                                                        self.logger.info("        ✓ 使用 JavaScript 点击方式")
                                                    except:
                                                        btn.click(force=True, timeout=5000)
                                                        self.logger.info("        ✓ 使用强制点击方式")
                                                
                                                google_pay_page.wait_for_timeout(10000)
                                                self.logger.info(f"  ✓ 成功点击付款按钮")
                                                return True
                                        except Exception as e:
                                            self.logger.info(f"        按钮 {btn_idx + 1} 点击失败: {e}")
                                            continue
                                except Exception as e:
                                    self.logger.info(f"      选择器 {selector} 失败: {e}")
                                    continue
                    except Exception as e:
                        self.logger.info(f"    在传入的 Google Pay 页面查找时出错: {e}")
                
                # 方法3: 在所有 frame 中查找
                self.logger.info(f"    在所有 frame 中查找（共 {len(self.page.frames)} 个）...")
                for frame_idx, frame in enumerate(self.page.frames):
                    try:
                        frame_url = frame.url if hasattr(frame, 'url') else 'unknown'
                        if 'pay.google.com' not in frame_url:
                            continue  # 只检查 pay.google.com 的 frame
                        
                        self.logger.info(f"      Frame {frame_idx}: {frame_url[:100]}")
                        for selector in pay_confirm_selectors:
                            try:
                                buttons = frame.locator(selector).all()
                                if len(buttons) > 0:
                                    self.logger.info(f"        选择器 {selector}: 找到 {len(buttons)} 个按钮")
                                    for btn_idx, btn in enumerate(buttons):
                                        try:
                                            if btn.is_visible(timeout=2000):
                                                btn_text = btn.inner_text()
                                                self.logger.info(f"          按钮 {btn_idx + 1} 可见，文本: '{btn_text}'")
                                                self.logger.info(f"        ✓ 在 Frame {frame_idx} 找到付款按钮")
                                                btn.click()
                                                self.page.wait_for_timeout(10000)  # 等待支付处理
                                                self.logger.info(f"  ✓ 成功点击付款按钮")
                                                return True
                                        except Exception as e:
                                            self.logger.info(f"          按钮 {btn_idx + 1} 点击失败: {e}")
                                            continue
                            except Exception as e:
                                self.logger.info(f"        选择器 {selector} 失败: {e}")
                                continue
                    except Exception as e:
                        self.logger.info(f"      Frame {frame_idx} 检查失败: {e}")
                        continue
                
                # 如果没找到，等待后重试
                if attempt < max_attempts - 1:
                    wait_time = 3000
                    self.logger.info(f"  - 未找到付款按钮，等待 {wait_time/1000} 秒后重试...")
                    self.page.wait_for_timeout(wait_time)
            
            self.logger.warning(f"  ✗ 在所有尝试中都未找到付款按钮")
            self.logger.info("="*70)
            return False
                
        except Exception as e:
            self.logger.error(f"点击付款按钮失败: {e}")
            return False
    
    def is_countdown_displayed(self) -> bool:
        """检查订单详情页上方是否显示发货倒计时（如 'Ship in 6d 23:57:37 or auto-cancel'）"""
        try:
            # 方法1: 查找包含 "Ship in" 文本的元素（发货倒计时）
            ship_in_selectors = [
                "text=/Ship in/i",  # 匹配 "Ship in" 文本（不区分大小写）
                "text=/ship in/i",
                "[class*='ship']",
                "[class*='countdown']",
                "[class*='timer']",
            ]
            
            for selector in ship_in_selectors:
                try:
                    elements = self.page.locator(selector).all()
                    for elem in elements:
                        if elem.is_visible(timeout=2000):
                            text = elem.inner_text().strip()
                            # 检查是否包含 "Ship in" 和倒计时格式（如 "6d 23:57:37"）
                            if text and ("ship in" in text.lower()):
                                # 检查是否包含倒计时格式（数字 + d/h/m/s 或 HH:MM:SS）
                                if any(pattern in text for pattern in ["d ", "h ", "m ", "s", ":", "auto-cancel"]):
                                    self.logger.info(f"✓ 找到发货倒计时: {text[:100]}")
                                    return True
                except:
                    continue
            
            # 方法2: 查找包含倒计时格式的文本（备用方法）
            countdown_selectors = [
                "[class*='countdown']",
                "[class*='timer']",
                "[class*='time']",
                "[id*='countdown']",
                "[id*='timer']",
                "text=/\\d+[dhms]\\s+\\d{2}:\\d{2}:\\d{2}/",  # 匹配格式如 "6d 23:57:37"
                "text=/\\d{2}:\\d{2}:\\d{2}/",  # 匹配时间格式 HH:MM:SS
            ]
            
            for selector in countdown_selectors:
                try:
                    elements = self.page.locator(selector).all()
                    for elem in elements:
                        if elem.is_visible(timeout=2000):
                            text = elem.inner_text()
                            # 检查是否包含时间格式或倒计时相关文本
                            if text and (":" in text or "countdown" in text.lower() or "timer" in text.lower() or "auto-cancel" in text.lower()):
                                self.logger.info(f"✓ 找到倒计时元素: {text[:100]}")
                                return True
                except:
                    continue
            
            self.logger.warning("  ⚠ 未找到发货倒计时")
            return False
        except Exception as e:
            self.logger.error(f"检查倒计时失败: {e}")
            return False

