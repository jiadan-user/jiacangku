# pages/ok_city_header_page.py
"""US OK.com 城市页顶栏右侧功能区（MCP 录制选择器）"""
import re

from pages.base_page import BasePage
from utils.logger import setup_logger


class OkCityHeaderPage(BasePage):
    """Provo 城市页顶栏：城市 / 语言 / 收藏 / 发布 / 消息 / 登录或账号入口"""

    _TOOLTIP_PANEL = "#tooltip-bottom"

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    def _dialog(self):
        return self.page.get_by_role("dialog").first

    def _close_floating_layers(self):
        """避免底部同名 tooltip 与顶栏 strict 冲突，先收起浮层"""
        try:
            self.page.keyboard.press("Escape")
            self.page.locator(self._TOOLTIP_PANEL).wait_for(state="hidden", timeout=2000)
        except Exception:
            pass

    def _topbar_item_exact(self, text: str):
        """MCP 录制为 getByText；配合 _close_floating_layers 后 .first 对应顶栏节点"""
        return self.page.get_by_text(text, exact=True).first

    def _topbar_item_regex(self, pattern: re.Pattern):
        return self.page.get_by_text(pattern).first

    def _wait_dropdown_visible(self, timeout: int = 20000):
        """语言/账号浮层：同时兼容 role=tooltip 与 #tooltip-bottom"""
        try:
            self.page.wait_for_function(
                """() => {
                    const tip = document.querySelector('[role="tooltip"]');
                    const pan = document.querySelector('#tooltip-bottom');
                    const vis = (el) => el && el.offsetParent !== null;
                    return vis(tip) || vis(pan);
                }""",
                timeout=timeout,
            )
        except Exception:
            try:
                self.page.get_by_role("tooltip").wait_for(state="visible", timeout=timeout)
            except Exception:
                self.page.locator(self._TOOLTIP_PANEL).wait_for(
                    state="visible", timeout=timeout
                )

    def wait_login_dialog_visible(self, timeout: int = 35000):
        """欢迎登录弹层出现（访客点收藏/发布/消息）；兼容文案/占位符微调"""
        try:
            # 直接检查 dialog 是否包含特定文本元素
            self._dialog().get_by_text("Welcome to OK.com").wait_for(state="visible", timeout=timeout)
        except Exception as e:
            self.logger.error(f"等待登录 dialog 失败: {e}")
            # 尝试额外的调试信息
            try:
                dialogs_count = self.page.locator('[role="dialog"]').count()
                self.logger.error(f"页面上 dialog 数量: {dialogs_count}")
                if dialogs_count > 0:
                    for i in range(min(dialogs_count, 3)):  # 最多检查3个
                        try:
                            dialog_text = self.page.locator('[role="dialog"]').nth(i).inner_text()[:200]
                            self.logger.error(f"Dialog {i} 内容片段: {dialog_text}")
                            is_visible = self.page.locator('[role="dialog"]').nth(i).is_visible()
                            self.logger.error(f"Dialog {i} 是否可见: {is_visible}")
                        except Exception:
                            pass
            except Exception:
                pass
            raise

    def set_viewport_recording_size(self):
        """与用例文档一致的视口 1440×900（MCP 录制视口）"""
        try:
            self.page.set_viewport_size({"width": 1440, "height": 900})
        except Exception as e:
            self.logger.error(f"设置视口失败: {e}")
            raise

    def dismiss_ok_cookie_banner(self):
        """OK.com 底部 Cookie 条会拦截顶栏与弹层内按钮，需关闭"""
        try:
            wrap = self.page.locator("div[class*='CookieConsent_cookieConsent']")
            if wrap.is_visible(timeout=2500):
                for pat in (
                    re.compile(r"accept", re.I),
                    re.compile(r"agree", re.I),
                ):
                    try:
                        wrap.get_by_role("button", name=pat).first.click(timeout=5000)
                        self.page.wait_for_load_state("domcontentloaded", timeout=5000)
                        return
                    except Exception:
                        continue
                try:
                    wrap.locator("button").first.click(timeout=5000)
                    self.page.wait_for_load_state("domcontentloaded", timeout=5000)
                    return
                except Exception:
                    pass
            candidates = (
                self.page.get_by_role("button", name=re.compile(r"accept", re.I)).first,
                self.page.locator('[class*="CookieConsent"] button').first,
                self.page.locator("button:has-text('Accept')").first,
            )
            for btn in candidates:
                try:
                    if btn.is_visible(timeout=1500):
                        btn.click()
                        self.page.wait_for_load_state("domcontentloaded", timeout=5000)
                        return
                except Exception:
                    continue
        except Exception:
            pass

    def open_city_provo_en(self, base_url: str):
        """打开英文 Provo 城市页"""
        try:
            url = (base_url or "").strip()
            if not url:
                raise ValueError("base_url 为空")
            self.goto(url, timeout=60000, wait_until="domcontentloaded")
            self.page.wait_for_load_state("domcontentloaded", timeout=45000)
            self.dismiss_ok_cookie_banner()
        except Exception as e:
            self.logger.error(f"打开城市页失败: {e}")
            raise

    def open_city_provo_es_from_us_host(self):
        """打开西语 Provo 城市页（固定路径，用于语言保持用例）"""
        try:
            self.goto(
                "https://us.ok.com/es/city-provo/",
                timeout=60000,
                wait_until="domcontentloaded",
            )
            self.page.wait_for_load_state("domcontentloaded", timeout=45000)
            self.dismiss_ok_cookie_banner()
        except Exception as e:
            self.logger.error(f"打开西语城市页失败: {e}")
            raise

    def wait_toolbar_text_visible(self, text: str, timeout: int = 15000):
        try:
            if "Log" in text and "Register" in text:
                self._topbar_item_regex(
                    re.compile(r"Log\s*in\s*/\s*Register", re.I)
                ).wait_for(state="visible", timeout=timeout)
            elif text == "English":
                # 58v5.cn 使用图标而非文本，检查图标是否存在
                try:
                    lang_icon = self.page.locator("div[class*='TopBarRightContent'] div[class*='iconList'] img").first
                    if lang_icon.is_visible(timeout=2000):
                        self.logger.info("语言选择器为图标形式（58v5.cn）")
                        return
                except Exception:
                    pass
                # 兜底：检查文本
                self._topbar_item_exact(text).wait_for(state="visible", timeout=timeout)
            else:
                self._topbar_item_exact(text).wait_for(
                    state="visible", timeout=timeout
                )
        except Exception as e:
            self.logger.error(f"等待顶栏文案失败 text={text}: {e}")
            raise

    def click_log_in_register(self):
        """MCP: await page.getByText('Log in / Register').click()"""
        try:
            self.dismiss_ok_cookie_banner()
            self._close_floating_layers()
            self._topbar_item_regex(re.compile(r"Log\s*in\s*/\s*Register", re.I)).click(
                force=True
            )
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击 Log in / Register 失败: {e}")
            raise

    def click_header_english(self):
        """
        触发语言选择器下拉面板（ok.com是点击"English"文本，58v5.cn是悬停图标）
        """
        try:
            self._close_floating_layers()
            
            # 优先尝试图标悬停方式（58v5.cn）
            try:
                # 查找顶部右侧区域的语言图标（通常是第一个或前几个图标）
                lang_icon = self.page.locator("div[class*='TopBarRightContent'] div[class*='iconList'] img").first
                if lang_icon.is_visible(timeout=2000):
                    self.logger.info("使用悬停方式触发语言面板（58v5.cn）")
                    lang_icon.hover()  # 悬停而不是点击
                    self.page.wait_for_timeout(1000)  # 增加等待时间
                    
                    # 检查是否有任何浮层出现
                    try:
                        # 先检查是否有任何tooltip或dropdown可见
                        visible_check = self.page.wait_for_function(
                            """() => {
                                const tooltips = document.querySelectorAll('[role="tooltip"], [id*="tooltip"], div[class*="dropdown"], div[class*="panel"]');
                                for (let el of tooltips) {
                                    if (el.offsetParent !== null) {
                                        return true;
                                    }
                                }
                                return false;
                            }""",
                            timeout=5000,
                        )
                        self.logger.info("✓ 悬停后检测到浮层")
                        # 悬停成功，直接返回，不再尝试点击文本
                        return
                    except Exception as e:
                        self.logger.warning(f"悬停后未检测到浮层: {e}")
                        # 继续尝试传统方式
            except Exception as e:
                self.logger.info(f"图标悬停方式失败，尝试文本点击方式: {e}")
            
            # 兜底：文本点击方式（ok.com）
            self.logger.info("使用点击方式触发语言面板（ok.com）")
            self._topbar_item_exact("English").click()
            try:
                self._wait_dropdown_visible(12000)
            except Exception:
                self.dismiss_ok_cookie_banner()
                self._topbar_item_exact("English").click()
                self._wait_dropdown_visible(25000)
                
        except Exception as e:
            self.logger.error(f"触发语言选择器失败: {e}")
            raise

    def click_language_español(self):
        """
        点击语言浮层中的 Español 选项
        需要确保浮层保持打开状态
        """
        try:
            # 在点击前确保浮层依然打开（可能需要重新悬停）
            try:
                # 先检查浮层是否可见
                tooltip_visible = self.page.get_by_role("tooltip").is_visible(timeout=2000)
                if not tooltip_visible:
                    self.logger.warning("浮层已消失，重新悬停...")
                    # 重新悬停以打开浮层
                    lang_icon = self.page.locator("div[class*='TopBarRightContent'] div[class*='iconList'] img").first
                    lang_icon.hover()
                    self.page.wait_for_timeout(1000)
            except Exception:
                pass
            
            # 直接尝试点击全局可见的 Español（最简单有效）
            try:
                self.page.get_by_text("Español", exact=True).first.click(timeout=10000)
                self.page.wait_for_load_state("domcontentloaded", timeout=45000)
                self.logger.info("✓ 成功点击 Español")
                return
            except Exception as e:
                self.logger.warning(f"全局点击 Español 失败: {e}")
                
                # 兜底：在tooltip中查找
                try:
                    self.page.get_by_role("tooltip").get_by_text("Español").first.click(timeout=8000)
                    self.page.wait_for_load_state("domcontentloaded", timeout=45000)
                    self.logger.info("✓ 在tooltip中点击 Español 成功")
                    return
                except Exception as e2:
                    self.logger.error(f"在tooltip中点击 Español 也失败: {e2}")
                    raise
        except Exception as e:
            self.logger.error(f"点击 Español 失败: {e}")
            raise

    def press_f5_refresh(self):
        """MCP: await page.keyboard.press('F5')"""
        try:
            self.page.keyboard.press("F5")
            self.page.wait_for_load_state("load", timeout=45000)
        except Exception as e:
            self.logger.error(f"F5 刷新失败: {e}")
            raise

    def click_favourites(self):
        """MCP: await page.getByText('Favourites').click()"""
        try:
            self.dismiss_ok_cookie_banner()
            self._close_floating_layers()
            self._topbar_item_exact("Favourites").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击 Favourites 失败: {e}")
            raise

    def click_post_toolbar(self):
        """MCP: await page.getByText('Post', { exact: true }).click()"""
        try:
            self.dismiss_ok_cookie_banner()
            self._close_floating_layers()
            self._topbar_item_exact("Post").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击 Post 失败: {e}")
            raise

    def click_messages_toolbar(self):
        """MCP: await page.getByText('Messages').click()"""
        try:
            self.dismiss_ok_cookie_banner()
            self._close_floating_layers()
            self._topbar_item_exact("Messages").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击 Messages 失败: {e}")
            raise

    def get_logged_in_display_name(self, timeout: int = 10000) -> str:
        """
        获取登录后顶栏显示的用户昵称（动态获取，避免硬编码）
        返回昵称文本，如果未找到则返回空字符串
        """
        try:
            # 查找顶部右侧区域中以"OKer"开头的文本（用户昵称模式）
            # 58v5.cn 和 ok.com 都使用 OKer 前缀
            user_locator = self.page.locator("div[class*='TopBarRightContent'] >> text=/^OKer/").first
            user_locator.wait_for(state="visible", timeout=timeout)
            display_name = user_locator.text_content().strip()
            self.logger.info(f"✓ 获取到登录用户昵称: {display_name}")
            return display_name
        except Exception as e:
            self.logger.warning(f"获取用户昵称失败: {e}")
            return ""
    
    def click_account_display_name(self, display_name: str):
        """MCP: await page.getByText('OKerUS_xxx').click()"""
        try:
            self.dismiss_ok_cookie_banner()
            self._close_floating_layers()
            self._topbar_item_exact(display_name).click(timeout=15000)
            self._wait_dropdown_visible()
            self.page.wait_for_timeout(400)
        except Exception as e:
            self.logger.error(f"点击账号展示名失败: {e}")
            raise

    def click_log_out(self):
        """MCP: await page.getByText('Log Out').click()"""
        try:
            last_err = None
            for container in (
                self.page.get_by_role("tooltip"),
                self.page.locator(self._TOOLTIP_PANEL),
            ):
                try:
                    container.get_by_text("Log Out", exact=True).first.click(timeout=8000)
                    self.page.wait_for_load_state("domcontentloaded", timeout=15000)
                    return
                except Exception as e:
                    last_err = e
                    continue
            raise last_err if last_err else RuntimeError("Log Out 未点击")
        except Exception as e:
            self.logger.error(f"点击 Log Out 失败: {e}")
            raise

    def click_log_out_spanish_ui(self):
        """MCP: await page.getByText('Finalizar la sesión').click()"""
        try:
            self.page.get_by_text("Finalizar la sesión").click()
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception as e:
            self.logger.error(f"点击 Finalizar la sesión 失败: {e}")
            raise

    def is_login_dialog_visible(self, timeout: int = 12000) -> bool:
        try:
            return self._dialog().is_visible(timeout=timeout)
        except Exception:
            return False

    def welcome_dialog_has_copy(self, fragment: str, timeout: int = 8000) -> bool:
        try:
            return self._dialog().get_by_text(fragment).first.is_visible(timeout=timeout)
        except Exception:
            return False

    def is_welcome_step_continue_disabled(self) -> bool:
        try:
            return self._dialog().get_by_role("button", name="Continue").is_disabled()
        except Exception as e:
            self.logger.error(f"读取 Continue 状态失败: {e}")
            raise

    def is_password_step_visible(self, timeout: int = 10000) -> bool:
        try:
            return self._dialog().get_by_text("Welcome back!").is_visible(timeout=timeout)
        except Exception:
            return False

    def password_field_value_contains(self, needle: str) -> bool:
        try:
            v = self._dialog().get_by_role("textbox", name="Enter password").input_value()
            return needle in (v or "")
        except Exception as e:
            self.logger.error(f"读取密码框失败: {e}")
            raise

    def top_incorrect_password_alert_visible(self, timeout: int = 8000) -> bool:
        try:
            loc = self.page.locator('[role="alert"]').filter(
                has_text="Incorrect password"
            )
            return loc.first.is_visible(timeout=timeout)
        except Exception:
            return False

    def navigate_away_to_reset_overlays(self, base_url: str):
        """关闭可能残留的弹层，回到城市页"""
        try:
            self.open_city_provo_en(base_url)
        except Exception as e:
            self.logger.error(f"重置页面失败: {e}")
            raise

    def language_tooltip_text_visible(self, fragment: str, timeout: int = 8000) -> bool:
        """语言/地区浮层内文案可见（限定在 tooltip 内，避免匹配页面其他区域）"""
        for container in (
            self.page.get_by_role("tooltip"),
            self.page.locator(self._TOOLTIP_PANEL),
        ):
            try:
                container.wait_for(state="visible", timeout=timeout)
                if fragment == "Español":
                    if container.get_by_text(re.compile(r"Español")).first.is_visible(
                        timeout=timeout
                    ):
                        return True
                elif container.get_by_text(fragment).first.is_visible(timeout=timeout):
                    return True
            except Exception:
                continue
        return False

    def account_menu_item_visible(self, name: str, timeout: int = 8000) -> bool:
        """账号下拉菜单项可见（限定 tooltip）"""
        for container in (
            self.page.get_by_role("tooltip"),
            self.page.locator(self._TOOLTIP_PANEL),
        ):
            try:
                container.wait_for(state="visible", timeout=timeout)
                if container.get_by_text(name, exact=True).first.is_visible(timeout=timeout):
                    return True
            except Exception:
                continue
        return False

    def is_display_name_visible(self, display_name: str, timeout: int = 3000) -> bool:
        try:
            return self._topbar_item_exact(display_name).is_visible(timeout=timeout)
        except Exception:
            return False
