"""
OK.com 详情页推荐模块 Page Object
负责详情页底部推荐区域（You may also like）的元素定位和操作
"""
from playwright.sync_api import Page, Locator
from utils.logger import setup_logger
from typing import List, Dict


class DetailPageRecommendation:
    """详情页推荐模块 Page Object"""

    def __init__(self, page: Page):
        self.page = page
        self.logger = setup_logger()

    # ==================== 元素定位器 ====================

    @property
    def recommendation_title(self) -> Locator:
        """推荐模块标题 'You may also like'"""
        return self.page.get_by_role("heading", name="You may also like", level=2)

    @property
    def cookie_accept_button(self) -> Locator:
        """Cookie 同意按钮"""
        return self.page.get_by_role("button", name="Accept all")

    @property
    def left_arrow_button(self) -> Locator:
        """左箭头按钮（通过nth定位，因为snapshot中没有明确的name属性）"""
        # 根据录制证明，左箭头是第3个button（nth(3)），右箭头是第4个button（nth(4)）
        # 但这个索引可能不稳定，建议使用更精确的定位方式
        return self.page.get_by_role("button").nth(3)

    @property
    def right_arrow_button(self) -> Locator:
        """右箭头按钮"""
        return self.page.get_by_role("button").nth(4)

    # ==================== 操作方法 ====================

    def navigate_to_detail_page(self, detail_url: str):
        """
        导航到详情页
        
        Args:
            detail_url: 详情页完整 URL
        """
        try:
            self.page.goto(detail_url, wait_until="domcontentloaded", timeout=30000)
            self.page.wait_for_load_state("load", timeout=30000)
        except Exception as e:
            self.logger.error(f"导航到详情页失败: {e}")
            raise

    def handle_cookie_popup(self):
        """
        处理 Cookie 弹窗（如果存在）
        如果弹窗不存在，不会抛出异常
        """
        try:
            if self.cookie_accept_button.is_visible(timeout=3000):
                self.cookie_accept_button.click()
                self.page.wait_for_timeout(1000)
        except Exception:
            pass

    def scroll_to_recommendation_module(self):
        """
        滚动到推荐模块位置
        """
        try:
            # 滚动到页面底部
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            # 等待推荐模块加载完成（至少3秒，推荐模块是动态加载的）
            self.page.wait_for_timeout(3000)
        except Exception as e:
            self.logger.error(f"滚动到推荐模块失败: {e}")
            raise

    def is_recommendation_title_visible(self, timeout: int = 5000) -> bool:
        """
        检查推荐模块标题是否可见
        
        Args:
            timeout: 超时时间（毫秒）
        
        Returns:
            bool: 推荐模块标题是否可见
        """
        try:
            # 等待页面稳定和动态内容加载
            self.page.wait_for_timeout(2000)
            return self.recommendation_title.is_visible(timeout=timeout)
        except Exception:
            return False

    def get_recommendation_cards_count(self) -> int:
        """
        获取推荐卡片数量
        
        Returns:
            int: 推荐卡片数量
        """
        try:
            # 根据录制证明，推荐卡片包含 .list-components-item-favorite.pc-card 类
            count = self.page.evaluate(
                "document.querySelectorAll('.list-components-item-favorite.pc-card').length"
            )
            return count
        except Exception as e:
            self.logger.error(f"获取推荐卡片数量失败: {e}")
            return 0

    def get_recommendation_card_titles(self) -> List[str]:
        """
        获取所有推荐卡片的标题
        
        Returns:
            List[str]: 推荐卡片标题列表
        """
        try:
            titles = self.page.evaluate("""
                Array.from(document.querySelectorAll('a[href*="cate-"] .details .title'))
                    .slice(0, 6)
                    .map(el => el.textContent.trim())
            """)
            return titles if titles else []
        except Exception as e:
            self.logger.error(f"获取推荐卡片标题失败: {e}")
            return []

    def is_left_arrow_disabled(self) -> bool:
        """
        检查左箭头是否禁用
        
        Returns:
            bool: 左箭头是否禁用
        """
        try:
            return self.left_arrow_button.is_disabled()
        except Exception:
            return False

    def is_right_arrow_disabled(self) -> bool:
        """
        检查右箭头是否禁用
        
        Returns:
            bool: 右箭头是否禁用
        """
        try:
            return self.right_arrow_button.is_disabled()
        except Exception:
            return False

    def is_left_arrow_enabled(self) -> bool:
        """
        检查左箭头是否可用
        
        Returns:
            bool: 左箭头是否可用
        """
        try:
            return self.left_arrow_button.is_enabled()
        except Exception:
            return False

    def is_right_arrow_enabled(self) -> bool:
        """
        检查右箭头是否可用
        
        Returns:
            bool: 右箭头是否可用
        """
        try:
            return self.right_arrow_button.is_enabled()
        except Exception:
            return False

    def click_right_arrow(self):
        """点击右箭头"""
        try:
            self.right_arrow_button.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击右箭头失败: {e}")
            raise

    def click_left_arrow(self):
        """点击左箭头"""
        try:
            self.left_arrow_button.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击左箭头失败: {e}")
            raise

    def click_first_recommendation_card(self):
        """
        点击第一张推荐卡片
        """
        try:
            # 等待推荐卡片加载完成
            self.page.wait_for_timeout(1000)
            # 使用更精确的选择器：从推荐模块标题找到父容器，然后获取第一张卡片链接
            self.page.evaluate("""
                const module = Array.from(document.querySelectorAll('h2')).find(h => h.textContent.includes('You may also like'))?.parentElement;
                if (module) {
                    const cards = module.querySelectorAll('a[href*="cate-"]');
                    if (cards.length > 0) {
                        cards[0].click();
                    }
                }
            """)
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception as e:
            self.logger.error(f"点击第一张推荐卡片失败: {e}")
            raise

    def click_favorite_icon_on_first_card(self):
        """
        点击第一张推荐卡片上的收藏图标
        """
        try:
            # 根据录制证明，收藏图标需要通过 DOM 查询定位
            # 增加等待和错误检测
            self.page.evaluate("""
                const icons = document.querySelectorAll('.list-components-item-favorite.pc-card img.favorite-icon');
                if (icons.length > 0) {
                    icons[0].click();
                } else {
                    throw new Error('未找到收藏图标');
                }
            """)
            # 等待收藏状态更新（需要 2-3 秒）
            self.page.wait_for_timeout(3000)
        except Exception as e:
            self.logger.error(f"点击收藏图标失败: {e}")
            raise

    def get_favorite_icon_state_on_first_card(self) -> str:
        """
        获取第一张推荐卡片的收藏图标状态
        
        Returns:
            str: "favorited" 表示已收藏，"unfavorited" 表示未收藏，"error" 表示获取失败
        """
        try:
            icon_src = self.page.evaluate(
                "document.querySelectorAll('.list-components-item-favorite.pc-card img.favorite-icon')[0].src"
            )
            if "fav.6bfdbb5e.png" in icon_src:
                return "favorited"
            elif "unFav.d2971929.png" in icon_src:
                return "unfavorited"
            else:
                return "error"
        except Exception as e:
            self.logger.error(f"获取收藏图标状态失败: {e}")
            return "error"

    def has_card_with_free_delivery(self) -> bool:
        """
        检查推荐卡片是否包含 Free Delivery 标签
        
        Returns:
            bool: 是否包含 Free Delivery 标签
        """
        try:
            free_delivery_locator = self.page.get_by_text("Free Delivery").first
            return free_delivery_locator.is_visible(timeout=3000)
        except Exception:
            return False

    def wait_for_recommendation_module(self, timeout: int = 15000):
        """
        等待推荐模块加载完成
        
        Args:
            timeout: 超时时间（毫秒）
        """
        try:
            self.recommendation_title.wait_for(state="visible", timeout=timeout)
        except Exception as e:
            self.logger.warning(f"等待推荐模块超时: {e}")

    def get_current_url(self) -> str:
        """
        获取当前页面 URL
        
        Returns:
            str: 当前页面 URL
        """
        return self.page.url
