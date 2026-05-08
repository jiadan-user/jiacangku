# pages/footer_page.py
from pages.base_page import BasePage
from utils.logger import setup_logger


class FooterPage(BasePage):
    """首页底部 Footer 区域页面对象"""
    
    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()
    
    # ========== Footer 区块选择器 ==========
    # Footer 容器（使用包含PcFooter的div）
    FOOTER_CONTAINER = "div[class*='PcFooter']"
    
    # About Us 区块
    ABOUT_US_SECTION = "text=About Us"
    TERMS_OF_USE_LINK = "a.PcFooter_aTag__uHohU:has-text('Terms of Use')"
    PRIVACY_POLICY_LINK = "a.PcFooter_aTag__uHohU:has-text('Privacy Policy')"
    
    # Help 区块
    HELP_SECTION = "text=Help"
    HELP_LINK = "a.PcFooter_aTag__uHohU:has-text('Help')"
    CONTACT_US_LINK = "a.PcFooter_aTag__uHohU:has-text('Contact Us')"
    FAQ_LINK = "a.PcFooter_aTag__uHohU:has-text('FAQ')"
    SUPPORT_FEEDBACK_LINK = "a.PcFooter_aTag__uHohU:has-text('Support and feedback')"
    RETURN_POLICY_LINK = "a.PcFooter_aTag__uHohU:has-text('Return Policy')"
    REFUND_POLICY_LINK = "a.PcFooter_aTag__uHohU:has-text('Refund Policy')"
    
    # Cookie 区块
    COOKIE_SECTION = "text=Cookie"
    COOKIE_POLICY_LINK = "a.PcFooter_aTag__uHohU:has-text('Cookie Policy')"
    COOKIE_SETTINGS_BUTTON = "span.PcFooter_footerContentSubChild__z2opm:has-text('Cookie Settings')"
    
    # Cookie Settings 弹窗
    COOKIE_MODAL = "[class*='consent-modal']"
    COOKIE_ESSENTIAL_SWITCH = "text=Essential cookies"
    COOKIE_ANALYTICAL_SWITCH = "text=Analytical cookies"
    COOKIE_MARKETING_SWITCH = "text=Marketing cookies"
    COOKIE_ALLOW_SELECTED_BUTTON = "button:has-text('Allow selected items')"
    COOKIE_DROP_CHANGES_BUTTON = "button:has-text('Drop the changes')"
    
    # Our Apps 区块
    OUR_APPS_SECTION = "text=Our Apps"
    # 应用下载链接（支持文本链接和图片链接）
    APP_STORE_LINK = "a[href*='apple.com'], a[href*='itunes.apple.com'], a[href*='apps.apple.com'], a.PcFooter_aTag__uHohU:has-text('App Store')"
    GOOGLE_PLAY_LINK = "a[href*='play.google.com'], a.PcFooter_aTag__uHohU:has-text('Google Play')"
    APP_STORE_IMAGE = "img[alt*='App Store'], img[src*='app-store']"
    GOOGLE_PLAY_IMAGE = "img[alt*='Google Play'], img[src*='google-play']"
    
    # 版权信息
    COPYRIGHT_TEXT = "text=/© 202[0-9] Servanan International Pte. Ltd./"
    
    # ========== Footer 操作方法 ==========
    
    def scroll_to_footer(self):
        """滚动到页面底部 Footer 区域"""
        try:
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            # 等待 Footer 区域可见
            self.page.locator(self.FOOTER_CONTAINER).first.wait_for(state="visible", timeout=10000)
        except Exception as e:
            self.logger.error(f"滚动到 Footer 失败: {e}")
            raise
    
    def is_footer_visible(self, timeout=5000):
        """检查 Footer 区域是否可见"""
        try:
            return self.is_visible(self.FOOTER_CONTAINER, timeout=timeout)
        except Exception:
            return False
    
    def is_about_us_section_visible(self, timeout=5000):
        """检查 About Us 区块是否可见"""
        try:
            return self.is_visible(self.ABOUT_US_SECTION, timeout=timeout)
        except Exception:
            return False
    
    def is_help_section_visible(self, timeout=5000):
        """检查 Help 区块是否可见"""
        try:
            return self.is_visible(self.HELP_SECTION, timeout=timeout)
        except Exception:
            return False
    
    def is_contact_us_link_visible(self, timeout=5000):
        """检查 Contact Us 链接是否可见"""
        try:
            return self.page.locator(self.CONTACT_US_LINK).first.is_visible(timeout=timeout)
        except Exception:
            return False
    
    def is_faq_link_visible(self, timeout=5000):
        """检查 FAQ 链接是否可见"""
        try:
            return self.page.locator(self.FAQ_LINK).first.is_visible(timeout=timeout)
        except Exception:
            return False
    
    def is_cookie_section_visible(self, timeout=5000):
        """检查 Cookie 区块是否可见"""
        try:
            return self.is_visible(self.COOKIE_SECTION, timeout=timeout)
        except Exception:
            return False
    
    def is_our_apps_section_visible(self, timeout=5000):
        """检查 Our Apps 区块是否可见"""
        try:
            return self.is_visible(self.OUR_APPS_SECTION, timeout=timeout)
        except Exception:
            return False
    
    def is_copyright_visible(self, timeout=5000):
        """检查版权信息是否可见"""
        try:
            return self.page.locator(self.COPYRIGHT_TEXT).first.is_visible(timeout=timeout)
        except Exception:
            return False
    
    def get_copyright_text(self):
        """获取版权信息文本"""
        try:
            return self.page.locator(self.COPYRIGHT_TEXT).first.inner_text()
        except Exception as e:
            self.logger.error(f"获取版权信息失败: {e}")
            return ""
    
    def get_footer_position(self):
        """获取 Footer 区域的位置信息（用于验证位置固定）"""
        try:
            footer = self.page.locator(self.FOOTER_CONTAINER).first
            bounding_box = footer.bounding_box()
            page_height = self.page.evaluate("document.body.scrollHeight")
            
            # 安全获取 viewport 高度（兼容 viewport_size 为 None 的情况）
            viewport_size = self.page.viewport_size
            if viewport_size and "height" in viewport_size:
                viewport_height = viewport_size["height"]
            else:
                # 备用方案：通过 JavaScript 获取视口高度
                viewport_height = self.page.evaluate("window.innerHeight")
                self.logger.warning(f"viewport_size 为 None，使用 window.innerHeight 获取视口高度: {viewport_height}px")
            
            # Footer 底部位置
            footer_bottom = bounding_box["y"] + bounding_box["height"]
            # 允许的误差：Footer 底部到页面底部的距离在 100px 以内认为是"在底部"
            # （考虑到页面可能有 body margin/padding 或其他元素的 margin）
            distance_to_bottom = page_height - footer_bottom
            is_at_bottom = distance_to_bottom <= 100
            
            return {
                "y": bounding_box["y"],
                "height": bounding_box["height"],
                "page_height": page_height,
                "viewport_height": viewport_height,
                "footer_bottom": footer_bottom,
                "distance_to_bottom": distance_to_bottom,
                "is_at_bottom": is_at_bottom
            }
        except Exception as e:
            self.logger.error(f"获取 Footer 位置失败: {e}")
            raise
    
    # ========== About Us 链接操作 ==========
    
    def click_terms_of_use(self):
        """点击 Terms of Use 链接"""
        try:
            self.page.locator(self.TERMS_OF_USE_LINK).first.click()
        except Exception as e:
            self.logger.error(f"点击 Terms of Use 链接失败: {e}")
            raise
    
    def get_terms_of_use_href(self):
        """获取 Terms of Use 链接的 href 属性"""
        try:
            return self.page.locator(self.TERMS_OF_USE_LINK).first.get_attribute("href")
        except Exception as e:
            self.logger.error(f"获取 Terms of Use href 失败: {e}")
            return ""
    
    def get_terms_of_use_target(self):
        """获取 Terms of Use 链接的 target 属性"""
        try:
            return self.page.locator(self.TERMS_OF_USE_LINK).first.get_attribute("target")
        except Exception as e:
            self.logger.error(f"获取 Terms of Use target 失败: {e}")
            return ""
    
    def click_privacy_policy(self):
        """点击 Privacy Policy 链接"""
        try:
            self.page.locator(self.PRIVACY_POLICY_LINK).first.click()
        except Exception as e:
            self.logger.error(f"点击 Privacy Policy 链接失败: {e}")
            raise
    
    def get_privacy_policy_href(self):
        """获取 Privacy Policy 链接的 href 属性"""
        try:
            return self.page.locator(self.PRIVACY_POLICY_LINK).first.get_attribute("href")
        except Exception as e:
            self.logger.error(f"获取 Privacy Policy href 失败: {e}")
            return ""
    
    def get_privacy_policy_target(self):
        """获取 Privacy Policy 链接的 target 属性"""
        try:
            return self.page.locator(self.PRIVACY_POLICY_LINK).first.get_attribute("target")
        except Exception as e:
            self.logger.error(f"获取 Privacy Policy target 失败: {e}")
            return ""
    
    # ========== Help 链接操作 ==========
    
    def click_help(self):
        """点击 Help 链接"""
        try:
            self.page.locator(self.HELP_LINK).first.click()
        except Exception as e:
            self.logger.error(f"点击 Help 链接失败: {e}")
            raise
    
    def get_help_href(self):
        """获取 Help 链接的 href 属性"""
        try:
            return self.page.locator(self.HELP_LINK).first.get_attribute("href")
        except Exception as e:
            self.logger.error(f"获取 Help href 失败: {e}")
            return ""
    
    def click_contact_us(self):
        """点击 Contact Us 链接"""
        try:
            self.page.locator(self.CONTACT_US_LINK).first.click()
        except Exception as e:
            self.logger.error(f"点击 Contact Us 链接失败: {e}")
            raise
    
    def get_contact_us_href(self):
        """获取 Contact Us 链接的 href 属性"""
        try:
            return self.page.locator(self.CONTACT_US_LINK).first.get_attribute("href")
        except Exception as e:
            self.logger.error(f"获取 Contact Us href 失败: {e}")
            return ""
    
    def click_faq(self):
        """点击 FAQ 链接"""
        try:
            self.page.locator(self.FAQ_LINK).first.click()
        except Exception as e:
            self.logger.error(f"点击 FAQ 链接失败: {e}")
            raise
    
    def get_faq_href(self):
        """获取 FAQ 链接的 href 属性"""
        try:
            return self.page.locator(self.FAQ_LINK).first.get_attribute("href")
        except Exception as e:
            self.logger.error(f"获取 FAQ href 失败: {e}")
            return ""
    
    def click_support_feedback(self):
        """点击 Support and feedback 链接"""
        try:
            self.page.locator(self.SUPPORT_FEEDBACK_LINK).first.click()
        except Exception as e:
            self.logger.error(f"点击 Support and feedback 链接失败: {e}")
            raise
    
    def get_support_feedback_href(self):
        """获取 Support and feedback 链接的 href 属性"""
        try:
            return self.page.locator(self.SUPPORT_FEEDBACK_LINK).first.get_attribute("href")
        except Exception as e:
            self.logger.error(f"获取 Support and feedback href 失败: {e}")
            return ""
    
    def click_return_policy(self):
        """点击 Return Policy 链接"""
        try:
            self.page.locator(self.RETURN_POLICY_LINK).first.click()
        except Exception as e:
            self.logger.error(f"点击 Return Policy 链接失败: {e}")
            raise
    
    def get_return_policy_href(self):
        """获取 Return Policy 链接的 href 属性"""
        try:
            return self.page.locator(self.RETURN_POLICY_LINK).first.get_attribute("href")
        except Exception as e:
            self.logger.error(f"获取 Return Policy href 失败: {e}")
            return ""
    
    def click_refund_policy(self):
        """点击 Refund Policy 链接"""
        try:
            self.page.locator(self.REFUND_POLICY_LINK).first.click()
        except Exception as e:
            self.logger.error(f"点击 Refund Policy 链接失败: {e}")
            raise
    
    def get_refund_policy_href(self):
        """获取 Refund Policy 链接的 href 属性"""
        try:
            return self.page.locator(self.REFUND_POLICY_LINK).first.get_attribute("href")
        except Exception as e:
            self.logger.error(f"获取 Refund Policy href 失败: {e}")
            return ""
    
    # ========== Cookie 链接操作 ==========
    
    def click_cookie_policy(self):
        """点击 Cookie Policy 链接"""
        try:
            self.page.locator(self.COOKIE_POLICY_LINK).first.click()
        except Exception as e:
            self.logger.error(f"点击 Cookie Policy 链接失败: {e}")
            raise
    
    def get_cookie_policy_href(self):
        """获取 Cookie Policy 链接的 href 属性"""
        try:
            return self.page.locator(self.COOKIE_POLICY_LINK).first.get_attribute("href")
        except Exception as e:
            self.logger.error(f"获取 Cookie Policy href 失败: {e}")
            return ""
    
    def click_cookie_settings(self):
        """点击 Cookie Settings 链接"""
        try:
            self.page.locator(self.COOKIE_SETTINGS_LINK).first.click()
        except Exception as e:
            self.logger.error(f"点击 Cookie Settings 链接失败: {e}")
            raise
    
    def get_cookie_settings_href(self):
        """获取 Cookie Settings 链接的 href 属性"""
        try:
            return self.page.locator(self.COOKIE_SETTINGS_LINK).first.get_attribute("href")
        except Exception as e:
            self.logger.error(f"获取 Cookie Settings href 失败: {e}")
            return ""
    
    # ========== Our Apps 链接操作 ==========
    
    def click_app_store(self):
        """点击 App Store 链接"""
        try:
            self.page.locator(self.APP_STORE_LINK).first.click()
        except Exception as e:
            self.logger.error(f"点击 App Store 链接失败: {e}")
            raise
    
    def get_app_store_href(self):
        """获取 App Store 链接的 href 属性"""
        try:
            return self.page.locator(self.APP_STORE_LINK).first.get_attribute("href")
        except Exception as e:
            self.logger.error(f"获取 App Store href 失败: {e}")
            return ""
    
    def click_google_play(self):
        """点击 Google Play 链接"""
        try:
            self.page.locator(self.GOOGLE_PLAY_LINK).first.click()
        except Exception as e:
            self.logger.error(f"点击 Google Play 链接失败: {e}")
            raise
    
    def get_google_play_href(self):
        """获取 Google Play 链接的 href 属性"""
        try:
            return self.page.locator(self.GOOGLE_PLAY_LINK).first.get_attribute("href")
        except Exception as e:
            self.logger.error(f"获取 Google Play href 失败: {e}")
            return ""
    
    def is_app_store_image_visible(self, timeout=5000):
        """检查 App Store 按钮图标是否可见"""
        try:
            return self.page.locator(self.APP_STORE_IMAGE).first.is_visible(timeout=timeout)
        except Exception:
            return False
    
    def is_google_play_image_visible(self, timeout=5000):
        """检查 Google Play 按钮图标是否可见"""
        try:
            return self.page.locator(self.GOOGLE_PLAY_IMAGE).first.is_visible(timeout=timeout)
        except Exception:
            return False
    
    # ========== Cookie Settings 操作 ==========
    
    def click_cookie_settings(self):
        """点击 Cookie Settings 按钮打开弹窗"""
        try:
            self.scroll_to_footer()
            self.page.locator(self.COOKIE_SETTINGS_BUTTON).first.click()
            
            # 等待弹窗出现（通过检测弹窗标题）
            self.page.locator("text=Cookie Settings").first.wait_for(state="visible", timeout=10000)
            self.page.wait_for_timeout(2000)
            
            self.logger.info("✓ 点击 Cookie Settings")
        except Exception as e:
            self.logger.error(f"点击 Cookie Settings 失败: {e}")
            raise
    
    def enable_all_cookies(self):
        """启用所有 Cookie 选项"""
        try:
            # Cookie 类型：Essential (默认开启), Functional, Analytical, Advertising
            cookie_types = [
                "Functional cookies",
                "Analytical cookies", 
                "Advertising cookies"
            ]
            
            # 等待弹窗完全加载
            self.page.wait_for_timeout(2000)
            
            for cookie_name in cookie_types:
                try:
                    # 查找该 Cookie 类型所在的行
                    cookie_row = self.page.locator(f"text={cookie_name}").first
                    
                    if cookie_row.is_visible(timeout=5000):
                        # 直接使用 JavaScript 来点击开关
                        clicked = self.page.evaluate(f'''() => {{
                            const allDivs = Array.from(document.querySelectorAll('div, span'));
                            const cookieDiv = allDivs.find(el => el.innerText === '{cookie_name}');
                            
                            if (cookieDiv) {{
                                let parent = cookieDiv.closest('div');
                                while (parent && parent !== document.body) {{
                                    const toggle = parent.querySelector('[class*="toggle"], [class*="switch"], [class*="Toggle"], [class*="Switch"]');
                                    
                                    if (toggle) {{
                                        toggle.click();
                                        return true;
                                    }}
                                    parent = parent.parentElement;
                                }}
                            }}
                            return false;
                        }}''')
                        
                        if clicked:
                            self.logger.info(f"✓ 启用 {cookie_name}")
                            self.page.wait_for_timeout(500)
                        else:
                            self.logger.info(f"⚠️ {cookie_name} 开关未找到或已启用")
                    else:
                        self.logger.info(f"⚠️ {cookie_name} 不可见")
                        
                except Exception as e:
                    self.logger.debug(f"处理 {cookie_name} 时出错: {e}")
            
            self.logger.info("✓ 已启用所有 Cookie 选项")
            
        except Exception as e:
            self.logger.error(f"启用所有 Cookie 失败: {e}")
            raise
    
    def click_allow_selected_cookies(self):
        """点击 'Allow selected items' 按钮确认 Cookie 设置"""
        try:
            self.page.locator(self.COOKIE_ALLOW_SELECTED_BUTTON).first.click()
            self.page.wait_for_timeout(2000)
            self.logger.info("✓ 点击 'Allow selected items' 确认设置")
        except Exception as e:
            self.logger.error(f"点击 'Allow selected items' 失败: {e}")
            raise
    
    def setup_all_cookies(self):
        """完整流程：打开 Cookie Settings 并启用所有 Cookie"""
        try:
            self.click_cookie_settings()
            self.enable_all_cookies()
            self.click_allow_selected_cookies()
            self.logger.info("✓ Cookie 设置完成：所有 Cookie 已启用")
        except Exception as e:
            self.logger.error(f"Cookie 设置流程失败: {e}")
            raise

