# pages/property_detail_page.py
from pages.base_page import BasePage
from utils.logger import setup_logger


class PropertyDetailPage(BasePage):
    """OK.com 商业地产租赁详情页对象（静默执行）"""

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    # ========== 页面操作方法（静默执行）==========

    def click_favourites(self):
        """点击收藏图标"""
        try:
            self.page.get_by_role("img", name="fav-icon").first.click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击收藏失败: {e}")
            raise

    def click_share(self):
        """点击分享（精确匹配 span 文本，避免与推荐卡片标题中含 Share 的文字冲突）"""
        try:
            self.page.get_by_text("Share", exact=True).first.click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击分享失败: {e}")
            raise

    def click_show_map(self):
        """点击 Show map 显示地图弹窗"""
        try:
            self.page.get_by_text("Show map").click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击 Show map 失败: {e}")
            raise

    def close_map_dialog_by_escape(self):
        """按 ESC 关闭地图弹窗"""
        try:
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"关闭地图弹窗失败: {e}")
            raise

    def click_breadcrumb_home(self):
        """点击面包屑 Home"""
        try:
            self.page.get_by_role("link", name="Home").click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击 Home 失败: {e}")
            raise

    def click_breadcrumb_property(self):
        """点击面包屑 Property"""
        try:
            self.page.get_by_role("link", name="Property").click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击 Property 失败: {e}")
            raise

    def click_breadcrumb_commercial_rent(self):
        """点击面包屑 Commercial Property for rent"""
        try:
            self.page.get_by_role("link", name="Commercial Property for rent").click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击 Commercial Property for rent 失败: {e}")
            raise

    def click_breadcrumb_other(self):
        """点击面包屑 Other"""
        try:
            self.page.get_by_role("link", name="Other").click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击 Other 失败: {e}")
            raise

    def click_recommendation_card(self, card_title=None):
        """点击推荐卡片。card_title 为 None 时点击推荐区域第一张卡片；否则按标题匹配。
        可能在新标签页打开，返回新页面或当前页面。
        """
        try:
            # 先滚动到推荐区域，确保卡片可见
            self.page.get_by_role("heading", name="You may also like").scroll_into_view_if_needed()
            self.page.wait_for_timeout(500)
        except Exception:
            pass

        def _get_locator():
            if card_title:
                return self.page.get_by_role("link").filter(has_text=card_title).first
            # 推荐区域：取第一个含 property/cate 链接的卡片
            carousel = self.page.locator(
                "[class*='recommend'], [class*='Recommend'], [class*='carousel'], [class*='Carousel']"
            ).first
            try:
                links = carousel.get_by_role("link").all()
                visible = [l for l in links if l.is_visible(timeout=300)]
                if visible:
                    return visible[0]
            except Exception:
                pass
            # fallback：取页面中 href 含 cate- 的链接（排除面包屑）
            return self.page.locator("a[href*='cate-']").last

        try:
            with self.page.context.expect_page(timeout=5000) as new_page_info:
                _get_locator().click()
            new_page = new_page_info.value
            new_page.wait_for_load_state("domcontentloaded", timeout=10000)
            return new_page
        except Exception:
            try:
                _get_locator().click()
            except Exception:
                pass
            self.page.wait_for_timeout(2000)
            return self.page

    def click_address_sailors_rest(self):
        """点击地址 Sailors' Rest"""
        try:
            self.page.get_by_text("Sailors' Rest").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击地址失败: {e}")
            raise

    def click_search_empty(self):
        """空搜索：直接点击 Search（搜索框为空）"""
        try:
            self.page.get_by_role("button", name="Search").click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"空搜索点击失败: {e}")
            raise

    def is_carousel_left_arrow_disabled(self):
        """检查 You may also like 轮播左箭头是否禁用"""
        try:
            carousel_section = self.page.get_by_role("heading", name="You may also like").locator("..")
            buttons = carousel_section.get_by_role("button").all()
            if buttons:
                return buttons[0].get_attribute("disabled") is not None
            return False
        except Exception:
            return False

    def click_carousel_right_arrow(self):
        """点击 You may also like 轮播右箭头"""
        try:
            carousel_section = self.page.get_by_role("heading", name="You may also like").locator("..")
            buttons = carousel_section.get_by_role("button").all()
            if len(buttons) >= 2:
                buttons[1].click()
            else:
                buttons[0].click()
            self.page.wait_for_timeout(800)
        except Exception as e:
            self.logger.error(f"点击右箭头失败: {e}")
            raise

    def fill_search_and_submit(self, keyword="property"):
        """填写搜索框并点击 Search"""
        try:
            self.page.get_by_role("textbox", name="Search for anything").fill(keyword)
            self.page.wait_for_timeout(500)
            self.page.get_by_role("button", name="Search").click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"搜索失败: {e}")
            raise

    def close_map_dialog_by_button(self):
        """点击关闭按钮关闭地图弹窗"""
        try:
            close_btn = self.page.get_by_role("img", name="close")
            if close_btn.is_visible(timeout=2000):
                close_btn.click()
                self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击关闭按钮失败: {e}")
            raise

    def close_map_dialog_by_overlay(self):
        """点击蒙层区域关闭地图弹窗（若支持）"""
        try:
            dialog = self.page.get_by_role("dialog").first
            if dialog.is_visible(timeout=2000):
                box = dialog.bounding_box()
                if box:
                    self.page.mouse.click(box["x"] - 20, box["y"] - 20)
                else:
                    self.page.mouse.click(50, 50)
                self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击蒙层关闭失败: {e}")
            raise

    def click_withdraw_button(self):
        """点击 Withdraw 按钮"""
        try:
            self.page.get_by_role("button", name="Withdraw").click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击 Withdraw 失败: {e}")
            raise

    def click_withdraw_dialog_cancel(self):
        """在 Withdraw 确认弹窗中点击取消"""
        try:
            cancel_btn = self.page.get_by_role("button", name="Cancel").first
            if cancel_btn.is_visible(timeout=3000):
                cancel_btn.click()
            else:
                cancel_btn = self.page.get_by_text("Cancel").first
                if cancel_btn.is_visible(timeout=1000):
                    cancel_btn.click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击 Withdraw 取消失败: {e}")
            raise

    def click_edit_button(self):
        """点击 Edit 按钮"""
        try:
            self.page.get_by_role("button", name="Edit").click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击 Edit 失败: {e}")
            raise

    def is_withdraw_visible(self, timeout=2000):
        """检查 Withdraw 按钮是否可见"""
        try:
            return self.page.get_by_role("button", name="Withdraw").is_visible(timeout=timeout)
        except Exception:
            return False

    def is_edit_visible(self, timeout=2000):
        """检查 Edit 按钮是否可见"""
        try:
            return self.page.get_by_role("button", name="Edit").is_visible(timeout=timeout)
        except Exception:
            return False

    def click_browse_dropdown(self):
        """点击顶部 Browse 下拉"""
        try:
            self.page.get_by_role("button", name="Browse").click()
            self.page.wait_for_timeout(1000)
        except Exception:
            self.page.get_by_text("Browse").first.click()
            self.page.wait_for_timeout(1000)

    def click_footer_link(self, link_text):
        """点击页脚链接（About Us、Terms of Use 等）"""
        try:
            self.page.get_by_role("link", name=link_text).click()
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
        except Exception as e:
            self.logger.error(f"点击页脚链接 {link_text} 失败: {e}")
            raise

    def click_user_avatar_or_nickname(self):
        """点击右上角用户头像或昵称区域"""
        try:
            header = self.page.locator("header")
            imgs = header.get_by_role("img").all()
            if len(imgs) >= 2:
                imgs[-1].click()
            elif imgs:
                imgs[0].click()
            else:
                self.page.get_by_role("button", name="Browse").locator("..").get_by_role("img").first.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击用户头像失败: {e}")
            raise

    def is_toast_visible(self, text, timeout=3000):
        """检查 Toast 是否包含指定文案"""
        try:
            return self.page.get_by_text(text).first.is_visible(timeout=timeout)
        except Exception:
            return False

    def is_map_dialog_visible(self, timeout=3000):
        """检查地图弹窗是否可见"""
        try:
            return self.page.get_by_role("dialog").is_visible(timeout=timeout)
        except Exception:
            return False

    def get_property_introduction_subtitle(self, timeout: int = 10000) -> str:
        """
        获取详情页 Property Introduction 模块的副标题（与列表卡片房产标题一致）。
        """
        try:
            self.page.get_by_text("Property Introduction", exact=False).first.wait_for(
                state="visible", timeout=timeout
            )
        except Exception:
            return ""
        result = self.page.evaluate(
            """
            () => {
                const headings = document.querySelectorAll('h1, h2, h3, h4, [class*="title"], [class*="Title"]');
                for (const h of headings) {
                    const t = (h.textContent || '').trim();
                    if (t === 'Property Introduction' || t.includes('Property Introduction')) {
                        const section = h.parentElement;
                        if (!section) continue;
                        const full = (section.textContent || '').split(/\\s*\\n+\\s*/).map(s => s.trim()).filter(Boolean);
                        for (const line of full) {
                            if (line && line !== 'Property Introduction' && line.length < 500) return line;
                        }
                    }
                }
                const byText = document.evaluate("//*[contains(text(),'Property Introduction')]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                if (byText) {
                    const section = byText.parentElement;
                    if (section) {
                        const full = (section.textContent || '').split(/\\s*\\n+\\s*/).map(s => s.trim()).filter(Boolean);
                        for (const line of full) {
                            if (line && line !== 'Property Introduction' && line.length < 500) return line;
                        }
                    }
                }
                return '';
            }
            """
        )
        return result or ""
