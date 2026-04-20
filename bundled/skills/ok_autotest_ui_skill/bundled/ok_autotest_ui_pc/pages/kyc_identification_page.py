# pages/kyc_identification_page.py
from pages.base_page import BasePage
from utils.logger import setup_logger


class KycIdentificationPage(BasePage):
    """KYC 身份认证页面对象"""

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    # ========== 页面操作方法（静默执行）==========

    def navigate_to_kyc_page(self):
        """导航到 KYC 认证页面"""
        try:
            self.goto("/biz/en/pay/identification", timeout=30000)
            self.wait_for_page_load()
        except Exception as e:
            self.logger.error(f"打开 KYC 认证页面失败: {e}")
            raise

    def click_begin_button(self):
        """点击 Begin 按钮进入上传页面"""
        try:
            begin_btn = self.page.get_by_role("button", name="Begin")
            begin_btn.wait_for(state="visible", timeout=5000)
            begin_btn.click()
            self.page.wait_for_timeout(2000)
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
        except Exception as e:
            self.logger.error(f"点击 Begin 按钮失败: {e}")
            raise

    def upload_document_image(self, file_path: str, wait_for_dialog: bool = True):
        """
        上传证件图片 - 直接设置文件输入而非点击按钮
        
        Args:
            file_path: 图片文件的绝对路径
            wait_for_dialog: 是否等待表单弹窗打开（默认 True）
        """
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            self.page.wait_for_timeout(1000)
            
            # 验证上传按钮可见（确认在上传页）
            upload_btn = self.page.get_by_role("button", name="Upload")
            choose_file_btn = self.page.get_by_role("button", name="Choose File")
            
            btn_found = False
            try:
                upload_btn.wait_for(state="visible", timeout=5000)
                btn_found = True
                self.logger.info("✓ 找到 Upload 按钮")
            except Exception:
                try:
                    choose_file_btn.wait_for(state="visible", timeout=5000)
                    btn_found = True
                    self.logger.info("✓ 找到 Choose File 按钮")
                except Exception as e:
                    self.logger.error(f"上传按钮不可见: {e}")
                    self.page.screenshot(path="reports/screenshots/debug_upload_no_button.png", full_page=True)
                    raise
            
            if not btn_found:
                raise AssertionError("未找到 Upload 或 Choose File 按钮")
            
            # 直接设置文件输入，避免按钮点击被 file input 覆盖
            file_input = self.page.locator('input[type="file"]').first
            file_input.set_input_files(file_path)
            self.logger.info(f"✓ 已设置文件: {file_path}")
            
            # 等待上传处理
            self.page.wait_for_timeout(3000)
            
            # 如果需要等待弹窗，尝试最多 15 秒
            if wait_for_dialog:
                try:
                    dialog = self.page.get_by_role("dialog").filter(has_text="Identity Verification")
                    dialog.wait_for(state="visible", timeout=15000)
                    self.logger.info("✓ 表单弹窗已打开")
                except Exception as e:
                    self.logger.warning(f"等待表单弹窗超时（可能上传失败或处理中）: {e}")
            
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"上传证件图片失败: {e}")
            raise

    def click_enter_manually(self):
        """点击 Enter Manually 链接，打开手动输入表单（MCP ref=e196）"""
        try:
            self.page.get_by_text("Or Enter Manually").click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击 Enter Manually 失败: {e}")
            raise

    def click_retry_button(self):
        """点击 Retry 按钮，从认证失败页进入引导页（MCP: getByRole button Retry）"""
        try:
            self.page.get_by_role("button", name="Retry").click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击 Retry 失败: {e}")
            raise

    def scroll_dialog_to_protocol(self):
        """滚动弹窗使协议区域可见（MCP: dialog.scrollTop=scrollHeight）"""
        try:
            self.page.locator("[role=dialog]").evaluate(
                "el => { el.scrollTop = el.scrollHeight; }"
            )
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"滚动弹窗失败: {e}")
            raise

    def check_agreement_checkbox(self):
        """勾选用户协议复选框（MCP: .OptionalBox_iconWrapper__P3pkZ）"""
        try:
            # 限定在 dialog 内，避免误点其他区域
            dialog = self.page.locator("[role=dialog]")
            icon_wrapper = dialog.locator(".OptionalBox_iconWrapper__P3pkZ").first
            icon_wrapper.click(force=True)
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"勾选协议失败: {e}")
            raise

    def press_escape(self):
        """按 ESC 关闭弹窗（MCP: browser_press_key Escape）"""
        try:
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"按 ESC 失败: {e}")
            raise

    def get_support_email_link_status(self) -> str:
        """
        检查 support@ok.com 是否为链接
        Returns: "no_link" 表示纯文本，否则返回 href 值（MCP 录制）
        """
        try:
            return self.page.get_by_text("support@ok.com").first.evaluate(
                "el => el.closest('a')?.getAttribute('href') || 'no_link'"
            )
        except Exception as e:
            self.logger.error(f"检查 support@ok.com 失败: {e}")
            return ""

    def click_submit_button(self):
        """点击 Submit 按钮"""
        try:
            self.page.get_by_role("button", name="Submit").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击 Submit 按钮失败: {e}")
            raise

    # ========== 验证方法 ==========

    def get_document_type_value(self) -> str:
        """
        获取 Document Type 字段的值
        
        Returns:
            字段值，如果为空则返回占位符文字
        """
        try:
            # 查找 Document Type 按钮，提取文本
            doc_type_button = self.page.get_by_role("button").filter(has_text="Document Type").first
            return doc_type_button.inner_text().strip()
        except Exception as e:
            self.logger.error(f"获取 Document Type 值失败: {e}")
            return ""

    def get_document_number_value(self) -> str:
        """获取 Document Number 字段的值"""
        try:
            input_field = self.page.get_by_role("textbox", name="Document Number")
            return input_field.input_value()
        except Exception as e:
            self.logger.error(f"获取 Document Number 值失败: {e}")
            return ""

    def get_first_name_value(self) -> str:
        """获取 First Name 字段的值"""
        try:
            input_field = self.page.get_by_role("textbox", name="First Name")
            return input_field.input_value()
        except Exception as e:
            self.logger.error(f"获取 First Name 值失败: {e}")
            return ""

    def get_last_name_value(self) -> str:
        """获取 Last Name 字段的值"""
        try:
            input_field = self.page.get_by_role("textbox", name="Last Name")
            return input_field.input_value()
        except Exception as e:
            self.logger.error(f"获取 Last Name 值失败: {e}")
            return ""

    def is_field_error_visible(self, field_name: str) -> bool:
        """
        检查指定字段是否显示错误提示 "Cannot be empty"
        
        Args:
            field_name: 字段名称（如 "Document Type", "Document Number"）
            
        Returns:
            是否显示错误提示
        """
        try:
            # 查找包含 "Cannot be empty" 的文本元素
            error_text = self.page.get_by_text("Cannot be empty", exact=False)
            return error_text.count() > 0
        except Exception:
            return False

    def get_all_error_messages(self) -> list:
        """
        获取所有显示的错误提示文案
        
        Returns:
            错误提示文案列表
        """
        try:
            error_elements = self.page.get_by_text("Cannot be empty").all()
            return [elem.inner_text() for elem in error_elements]
        except Exception as e:
            self.logger.error(f"获取错误提示失败: {e}")
            return []

    def is_form_dialog_visible(self, timeout: int = 5000) -> bool:
        """
        检查手动输入表单弹窗是否可见
        
        Args:
            timeout: 等待超时时间（毫秒），默认 5000ms
            
        Returns:
            弹窗是否可见
        """
        try:
            dialog = self.page.get_by_role("dialog").filter(has_text="Identity Verification")
            dialog.wait_for(state="visible", timeout=timeout)
            return dialog.is_visible()
        except Exception as e:
            self.logger.debug(f"表单弹窗不可见: {e}")
            return False

    def is_upload_thumbnail_visible(self) -> bool:
        """检查上传的图片缩略图是否显示（弹窗内至少有 2 个 img：关闭按钮 + 缩略图）"""
        try:
            dialog = self.page.get_by_role("dialog")
            # 首先等待弹窗可见
            dialog.wait_for(state="visible", timeout=5000)
            
            # 等待图片元素加载
            self.page.wait_for_timeout(1000)
            
            imgs = dialog.locator("img")
            img_count = imgs.count()
            
            # 关闭按钮为第一个 img，缩略图为第二个；若仅有 1 个则视为无缩略图
            if img_count >= 2:
                # 等待第二个图片（缩略图）可见
                try:
                    imgs.nth(1).wait_for(state="visible", timeout=10000)
                    return True
                except Exception:
                    return False
            return False
        except Exception:
            return False
