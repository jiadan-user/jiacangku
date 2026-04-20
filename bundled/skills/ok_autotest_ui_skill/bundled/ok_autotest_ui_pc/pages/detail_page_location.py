# pages/detail_page_location.py
"""详情页 Location 卡片与全屏地图模态（来源：web-qa-brain 实测 + OK.com-详情页Location区域-测试用例-20260410.md）"""

from pages.base_page import BasePage


class DetailPageLocation(BasePage):
    """详情页主栏 Location 区域（非招聘/非房产通用结构）"""

    def goto_detail(self, url: str) -> None:
        self.goto(url, timeout=60000, wait_until="domcontentloaded")
        self.location_card.wait_for(state="visible", timeout=30000)

    @property
    def location_card(self):
        return self.page.locator('[class*="LocationCard_locationCard"]').first

    @property
    def location_section_title(self):
        return self.location_card.locator('[class*="LocationCard_title"]').first

    @property
    def location_address(self):
        return self.location_card.locator('[class*="LocationCard_address"]').first

    @property
    def show_map_preview(self):
        return self.location_card.locator('[class*="LocationCard_pcShowMapCard"], [class*="LocationCard_showMap"]').first

    @property
    def show_map_button(self):
        return self.location_card.locator('[class*="LocationCard_showMapBtn"]').first

    @property
    def main_info_address(self):
        return self.page.locator('[class*="MainInfo_address"]').first

    @property
    def map_modal(self):
        return self.page.locator('[class*="LocationCard_modalMap"].modal.show').first

    @property
    def map_modal_close(self):
        return self.page.locator('[class*="LocationCard_modalMap"].modal.show').locator(
            'img[class*="LocationCard_back"], img[alt="close"]'
        ).first

    def map_container(self):
        return self.page.locator("#map")
