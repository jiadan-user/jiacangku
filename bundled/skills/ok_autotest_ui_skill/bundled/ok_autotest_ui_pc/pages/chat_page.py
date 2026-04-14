# pages/chat_page.py
from pages.base_page import BasePage
from utils.logger import setup_logger


class ChatPage(BasePage):
    """聊天页面对象（静默执行）"""

    CHAT_URL_PATTERN = "aepub.58v5.cn/biz/en/chat"
    CHAT_BASE_URL = "https://aepub.58v5.cn/biz/en/chat"

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    # ========== 页面操作方法（静默执行）==========

    def click_contact_button_primary(self):
        """点击职位详情页主区 Contact 按钮（录制: getByRole('button',{name:'Contact'}).first()）"""
        try:
            self.page.get_by_role("button", name="Contact").first.click()
            self._wait_for_chat_panel_open()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击主区 Contact 按钮失败: {e}")
            raise

    def click_contact_button_sidebar(self):
        """点击职位详情页右侧卡片 Contact 按钮（录制: getByRole('button',{name:'Contact'}).nth(1)）"""
        try:
            self.page.get_by_role("button", name="Contact").nth(1).click()
            self._wait_for_chat_panel_open()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击右侧卡片 Contact 按钮失败: {e}")
            raise

    def _wait_for_chat_panel_open(self, timeout=15000):
        """等待聊天面板打开：优先等待 URL 跳转，若聊天以侧边栏/弹窗形式内嵌则降级等待输入框出现"""
        try:
            self.page.wait_for_url(f"**/{self.CHAT_URL_PATTERN}**", timeout=timeout)
        except Exception:
            # 聊天以嵌入面板形式打开，URL 不变，改为等待输入框出现
            self.page.wait_for_selector(
                "role=textbox[name='Input message']",
                state="visible",
                timeout=timeout
            )

    def get_current_url(self):
        """获取当前页面 URL"""
        try:
            return self.page.url
        except Exception as e:
            self.logger.error(f"获取 URL 失败: {e}")
            raise

    def wait_for_chat_loaded(self):
        """等待聊天页面内容加载完成"""
        try:
            self.page.wait_for_selector(
                "role=textbox[name='Input message']",
                state="visible",
                timeout=15000
            )
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"等待聊天页面加载失败: {e}")
            raise

    def get_initial_message_text(self):
        """获取系统自动发送的初始消息文案"""
        try:
            # 初始消息为第一条己方消息气泡
            return self.page.locator(
                "text=I'm interested in your job posting and open to discussing more details."
            ).first.inner_text()
        except Exception as e:
            self.logger.error(f"获取初始消息失败: {e}")
            raise

    def is_initial_message_visible(self):
        """判断初始消息是否已发送并显示"""
        try:
            return self.page.locator(
                "text=I'm interested in your job posting and open to discussing more details."
            ).first.is_visible(timeout=8000)
        except Exception:
            return False

    def is_send_button_disabled(self):
        """判断 Send 按钮是否处于禁用状态（录制: button "Send" [disabled]）"""
        try:
            return self.page.get_by_role("button", name="Send").is_disabled(timeout=3000)
        except Exception as e:
            self.logger.error(f"检查 Send 按钮状态失败: {e}")
            raise

    def is_send_button_enabled(self):
        """判断 Send 按钮是否处于可用状态"""
        try:
            return self.page.get_by_role("button", name="Send").is_enabled(timeout=3000)
        except Exception as e:
            self.logger.error(f"检查 Send 按钮状态失败: {e}")
            raise

    def fill_message_input(self, text):
        """在输入框填入消息文本（录制: getByRole('textbox',{name:'Input message'}).fill(...)）"""
        try:
            self.page.get_by_role("textbox", name="Input message").fill(text)
            self.page.wait_for_timeout(300)
        except Exception as e:
            self.logger.error(f"填入消息失败: {e}")
            raise

    def send_message_by_enter(self, text, post_send_wait: int = 20000):
        """填入消息并按 Enter 发送（录制: fill + keyboard.press('Enter')）

        Args:
            text: 要发送的消息内容
            post_send_wait: 发送后等待时长（ms），默认 20000ms，给 AI 足够时间响应
        """
        try:
            self.page.get_by_role("textbox", name="Input message").fill(text)
            self.page.wait_for_timeout(300)
            self.page.keyboard.press("Enter")
            self.logger.info(f"消息已发送，等待 {post_send_wait}ms ...")
            self.page.wait_for_timeout(post_send_wait)
        except Exception as e:
            self.logger.error(f"发送消息失败: {e}")
            raise

    def get_input_value(self):
        """获取输入框当前内容"""
        try:
            return self.page.get_by_role("textbox", name="Input message").input_value()
        except Exception as e:
            self.logger.error(f"获取输入框内容失败: {e}")
            raise

    def is_message_visible_in_chat(self, text):
        """判断指定消息文本是否显示在聊天区域"""
        try:
            return self.page.get_by_text(text).first.is_visible(timeout=8000)
        except Exception:
            return False

    def wait_for_reply(self, timeout=10000):
        """等待对方（AI Auto Reply）回复出现"""
        try:
            self.page.wait_for_selector(
                "text=AI Auto Reply",
                state="visible",
                timeout=timeout
            )
        except Exception as e:
            self.logger.error(f"等待回复超时: {e}")
            raise

    def is_ai_auto_reply_visible(self):
        """判断 AI Auto Reply 标签是否可见"""
        try:
            return self.page.locator("text=AI Auto Reply").first.is_visible(timeout=8000)
        except Exception:
            return False

    def get_seller_name_in_header(self):
        """动态获取聊天页面顶部 seller 名称（聊天面板 header 区域第一个文本节点）"""
        try:
            # 聊天面板顶部结构：header 容器 > seller 名称 + 状态标签
            # 取第一个子文本节点，即 seller 用户名
            name = self.page.locator(
                "[class*='chat'] [class*='header'] [class*='name'], "
                "[class*='chat'] [class*='header'] [class*='user'], "
                "[class*='chat-header'] [class*='name']"
            ).first.inner_text(timeout=5000)
            if name:
                return name
        except Exception:
            pass

        # fallback：从 URL 的 shopName 参数解析
        try:
            import urllib.parse
            url = self.page.url
            parsed = urllib.parse.urlparse(url)
            # chat URL 的 query 可能是双重编码，先解码一次
            query_str = urllib.parse.unquote(parsed.query)
            params = dict(urllib.parse.parse_qsl(query_str))
            shop_name = params.get("shopName", "")
            if shop_name:
                self.logger.info(f"从 URL 参数解析 seller 名称: {shop_name}")
                return shop_name
        except Exception as e:
            self.logger.error(f"从 URL 解析 seller 名称失败: {e}")

        raise RuntimeError("无法从页面或 URL 获取 seller 名称")

    def is_seller_name_visible(self, seller_name):
        """判断顶部 seller 名称是否可见"""
        try:
            return self.page.get_by_text(seller_name).first.is_visible(timeout=5000)
        except Exception:
            return False

    def get_job_title_in_chat(self):
        """动态获取聊天页面内职位卡片的标题，优先从 URL 的 postName 参数解析"""
        try:
            import urllib.parse
            url = self.page.url
            parsed = urllib.parse.urlparse(url)
            query_str = urllib.parse.unquote(parsed.query)
            params = dict(urllib.parse.parse_qsl(query_str))
            post_name = params.get("postName", "")
            if post_name:
                self.logger.info(f"从 URL 参数解析职位名称: {post_name}")
                return post_name
        except Exception as e:
            self.logger.error(f"从 URL 解析职位名称失败: {e}")

        # fallback：从聊天区域职位卡片 DOM 读取
        try:
            title = self.page.locator(
                "[class*='job-card'] [class*='title'], "
                "[class*='post-card'] [class*='title'], "
                "[class*='chat'] [class*='card'] [class*='title']"
            ).first.inner_text(timeout=5000)
            if title:
                return title
        except Exception:
            pass

        raise RuntimeError("无法从页面或 URL 获取职位名称")

    def is_job_card_visible(self, job_title):
        """判断聊天内职位卡片是否可见"""
        try:
            return self.page.get_by_text(job_title).first.is_visible(timeout=5000)
        except Exception:
            return False

    def is_safety_notice_visible(self):
        """判断安全提示语是否存在于聊天页面。
        共享页面模式下消息增多后安全提示语可能滚出视口，
        改用 count() 检查 DOM 是否存在，不依赖视口可见性。
        """
        try:
            locator = self.page.locator(
                "text=For your safety, please avoid sharing sensitive personal information"
            )
            locator.first.wait_for(state="attached", timeout=5000)
            return locator.count() > 0
        except Exception:
            return False

    def get_page_title(self):
        """获取页面标题"""
        try:
            return self.page.title()
        except Exception as e:
            self.logger.error(f"获取页面标题失败: {e}")
            raise
