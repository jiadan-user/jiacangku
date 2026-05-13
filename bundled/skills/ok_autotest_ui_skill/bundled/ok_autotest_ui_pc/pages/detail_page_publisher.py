# pages/detail_page_publisher.py
"""详情页右侧发布者信息区域（录制来源：playwright-test-generator 批次 1/2）"""
import re

from pages.base_page import BasePage


class DetailPagePublisher(BasePage):
    """OK.com 商品详情页 — 发布者信息卡片与 Contact"""

    def goto_detail(self, url: str) -> None:
        self.goto(url, timeout=60000, wait_until="domcontentloaded")
        self.contact_button.wait_for(state="visible", timeout=30000)

    @property
    def contact_button(self):
        # 详情页/吸底等场景可能出现多个 Contact，统一取第一个可见实例
        return self.page.get_by_role("button", name="Contact").first

    def publisher_display_name(self, name: str):
        """发布者昵称（卡片内）"""
        return self.page.get_by_text(name, exact=True).first

    def click_publisher_name(self, name: str) -> None:
        self.publisher_display_name(name).click()

    def click_publisher_card_including_badge(self, publisher_name: str = None) -> None:
        """点击发布者卡片区域（含头像、名称、徽章等）"""
        if publisher_name:
            # 尝试精确匹配发布者名称(可能带Verified徽章)
            try:
                self.page.get_by_text(re.compile(rf"{re.escape(publisher_name)}\s*(Verified)?", re.I), exact=False).first.click(timeout=5000)
            except:
                # 如果失败,尝试点击头像区域
                self.page.locator('[class*="avatar"], [class*="Avatar"]').first.click()
        else:
            # 如果没有指定发布者名称,尝试点击头像区域
            self.page.locator('[class*="avatar"], [class*="Avatar"]').first.click()

    def close_login_dialog_if_present(self) -> None:
        """欢迎登录弹层右上角关闭（class 含 closeBtn，避免 CSS Module 全量哈希）"""
        dlg = self.page.locator('[role="dialog"], dialog').filter(
            has_text=re.compile(r"Welcome to OK", re.I)
        ).first
        closer = dlg.locator('[class*="closeBtn"]').first
        try:
            if closer.is_visible(timeout=2500):
                closer.click()
                self.page.wait_for_timeout(400)
        except Exception:
            pass
