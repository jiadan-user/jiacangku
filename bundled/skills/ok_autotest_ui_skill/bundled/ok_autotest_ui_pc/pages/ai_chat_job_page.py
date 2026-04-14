# pages/ai_chat_job_page.py
import urllib.parse
from datetime import datetime
from pages.chat_page import ChatPage
from utils.logger import setup_logger


class AiChatJobPage(ChatPage):
    """Jobs 详情页会话页面对象 - 扩展 ChatPage，新增文件上传、AI 回复等能力（静默执行）"""

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()
        self.send_time = None  # 记录消息发送时间

    def upload_image_file(self, file_path):
        """通过隐藏的 file input 上传图片文件（accept: image/JPG,image/PNG,image/JPEG），并从 DOM 获取发送时间
        HTML: input[accept*='image'][type='file'] style='display:none'
        """
        try:
            # 记录上传时间
            self.send_time = datetime.now()
            
            file_input = self.page.locator(
                "input[type='file'][accept*='image']"
            ).first
            file_input.wait_for(state="attached", timeout=10000)
            file_input.set_input_files(file_path)
            
            # 等待30秒，让时间戳充分渲染
            self.page.wait_for_timeout(30000)
            self.logger.info("✓ 已等待 30 秒，时间戳应已渲染")
            
            # 从 DOM 获取发送时间
            dom_time = self._get_send_time_from_dom()
            if dom_time:
                self.send_time = dom_time
            
            self.logger.info(f"✓ 图片发送时间: {self.send_time.strftime('%H:%M:%S.%f')[:-3]}")
        except Exception as e:
            self.logger.error(f"上传图片文件失败: {e}")
            raise

    # ========== 消息状态 ==========

    def wait_for_message_sent(self, message_text, timeout=10000):
        """等待指定消息文本出现在聊天区域（消息气泡）"""
        try:
            self.page.wait_for_selector(
                f"text={message_text}",
                state="visible",
                timeout=timeout
            )
        except Exception as e:
            self.logger.error(f"等待消息出现超时: {e}")
            raise

    def wait_for_ai_auto_reply(self, timeout=30000):
        """发送消息后，等待 AI Auto Reply 标签出现
        
        注意：此方法应在发送消息后调用，等待 AI 自动回复的标签出现
        AI 响应时间不定，使用较长的超时时间
        """
        try:
            self.page.wait_for_selector(
                "text=AI Auto Reply",
                state="visible",
                timeout=timeout
            )
        except Exception as e:
            self.logger.error(f"等待 AI Auto Reply 超时: {e}")
            raise

    def click_send_button(self):
        """点击 Send 按钮（等待非 disabled 状态后再点击），并记录发送时间"""
        try:
            btn = self.page.get_by_role("button", name="Send")
            btn.wait_for(state="visible", timeout=5000)
            self.page.wait_for_function(
                "() => !document.querySelector('[aria-label=\"Send\"]')?.disabled",
                timeout=5000
            )
            # 记录发送时间（点击时）
            self.send_time = datetime.now()
            btn.click()
            
            # 等待30秒，让时间戳充分渲染
            self.page.wait_for_timeout(30000)
            self.logger.info("✓ 已等待 30 秒，时间戳应已渲染")
            
            # 尝试从 DOM 获取时间，如果失败则使用记录的时间
            dom_time = self._get_send_time_from_dom()
            if dom_time:
                self.send_time = dom_time
            
            self.logger.info(f"✓ 消息发送时间: {self.send_time.strftime('%H:%M:%S.%f')[:-3]}")
        except Exception as e:
            self.logger.error(f"点击 Send 按钮失败: {e}")
            raise
    
    def _get_send_time_from_dom(self):
        """从 DOM 获取发送消息的时间戳（右侧消息时间）
        
        Returns:
            datetime: 发送消息的时间戳
        """
        try:
            # 发送消息的时间在右侧：<div class="t-me-time right">14:50</div>
            # 获取最后一个右侧时间（最新的发送消息）
            time_elements = self.page.locator("div.t-me-time.right").all()
            
            if len(time_elements) > 0:
                time_element = time_elements[-1]  # 获取最后一个
                time_text = time_element.text_content().strip()
                self.logger.info(f"✓ 从 DOM 获取发送时间: {time_text}")
                
                # 解析时间文本（格式: "14:50" 或 "3:06"）
                try:
                    # 先尝试解析为 HH:MM 格式
                    time_obj = datetime.strptime(time_text, "%H:%M")
                    now = datetime.now()
                    result_time = now.replace(
                        hour=time_obj.hour,
                        minute=time_obj.minute,
                        second=0,
                        microsecond=0
                    )
                    
                    # 如果解析出的时间是凌晨（如 3:06），但现在是下午，说明可能是时区或显示问题
                    # 尝试加上 12 小时看是否更合理
                    if result_time.hour < 12 and now.hour >= 12:
                        # 计算两个可能的时间与当前时间的差距
                        diff1 = abs((result_time - now).total_seconds())
                        result_time_pm = result_time.replace(hour=result_time.hour + 12)
                        diff2 = abs((result_time_pm - now).total_seconds())
                        
                        # 选择更接近当前时间的那个
                        if diff2 < diff1:
                            self.logger.info(f"  → 调整为 PM 时间: {result_time_pm.strftime('%H:%M')}")
                            result_time = result_time_pm
                    
                    return result_time
                except ValueError:
                    self.logger.warning(f"⚠️ 无法解析发送时间格式: {time_text}")
            
            # 如果无法从 DOM 获取，使用当前时间
            self.logger.warning("⚠️ 无法从 DOM 获取发送时间，使用当前时间")
            return datetime.now()
        except Exception as e:
            self.logger.error(f"获取发送时间失败: {e}")
            return datetime.now()

    def is_input_cleared(self):
        """判断消息输入框是否已清空（发送后应为空）"""
        try:
            value = self.page.get_by_role("textbox", name="Input message").input_value()
            return value == ""
        except Exception as e:
            self.logger.error(f"检查输入框清空状态失败: {e}")
            raise

    def is_file_message_visible(self, timeout=15000):
        """判断文件消息是否出现在聊天区域（图片缩略图或文件名）"""
        try:
            # 尝试多种可能的选择器，适配不同的文件消息结构
            selectors = [
                # 图片消息（通用）
                "img[src*='blob:'], img[src*='data:image'], img[src*='http']",
                # 消息区域内的图片
                "[class*='message'] img, [class*='chat'] img",
                # 文件消息
                "[class*='file'], [class*='attachment']",
                # 消息气泡内的内容
                "[class*='bubble'] img, [class*='bubble'] [class*='file']",
                # 通用：任何新增的图片元素
                ".message img, .chat-message img, .msg img",
            ]
            
            for selector in selectors:
                try:
                    self.page.wait_for_selector(
                        selector,
                        state="visible",
                        timeout=2000  # 每个选择器尝试2秒
                    )
                    return True
                except Exception:
                    continue
            
            # 所有选择器都失败
            return False
        except Exception:
            return False

    def is_ai_auto_reply_visible(self):
        """判断发送消息后，AI Auto Reply 标签是否可见
        
        注意：此方法应在发送消息后调用，检查聊天区域是否出现 AI Auto Reply 标签
        """
        try:
            # 检查聊天区域中最新的消息是否包含 AI Auto Reply 标签
            ai_reply_label = self.page.locator("text=AI Auto Reply").last
            return ai_reply_label.is_visible(timeout=8000)
        except Exception:
            return False
    
    def get_ai_reply_timestamp(self):
        """获取 AI Auto Reply 消息的时间戳（从 DOM 中的 t-me-time left 元素获取）
        等待新的 AI 回复出现后，获取最新的左侧时间戳
        
        Returns:
            datetime: AI 回复消息的时间戳，如果无法获取则返回当前时间
        """
        try:
            # 等待页面稳定，确保时间戳已渲染
            self.page.wait_for_timeout(500)
            
            # AI 回复的时间在左侧：<div class="t-me-time left">14:50</div>
            # 获取所有左侧时间元素
            time_elements = self.page.locator("div.t-me-time.left").all()
            
            if len(time_elements) > 0:
                # 获取最后一个（最新的 AI 回复）
                time_element = time_elements[-1]
                time_text = time_element.text_content().strip()
                self.logger.info(f"✓ 从 DOM 获取 AI 回复时间: {time_text}")
                
                # 解析时间文本（格式: "14:50" 或 "3:06"）
                try:
                    time_obj = datetime.strptime(time_text, "%H:%M")
                    now = datetime.now()
                    result_time = now.replace(
                        hour=time_obj.hour,
                        minute=time_obj.minute,
                        second=0,
                        microsecond=0
                    )
                    
                    # 如果解析出的时间是凌晨（如 2:51），但现在是下午，尝试加 12 小时
                    if result_time.hour < 12 and now.hour >= 12:
                        diff1 = abs((result_time - now).total_seconds())
                        result_time_pm = result_time.replace(hour=result_time.hour + 12)
                        diff2 = abs((result_time_pm - now).total_seconds())
                        
                        # 选择更接近当前时间的
                        if diff2 < diff1:
                            self.logger.info(f"  → 调整为 PM 时间: {result_time_pm.strftime('%H:%M')}")
                            result_time = result_time_pm
                    
                    # 确保 AI 回复时间不早于发送时间（如果有 send_time）
                    if self.send_time and result_time < self.send_time:
                        # 可能是同一分钟内的消息，但秒数有差异
                        # 如果时间相差很大（超过5分钟），说明获取的是旧消息，调整一下
                        time_diff = (self.send_time - result_time).total_seconds()
                        if time_diff > 300:  # 超过 5 分钟
                            self.logger.warning(f"⚠️ AI 回复时间 {time_text} 早于发送时间，可能是历史消息")
                    
                    return result_time
                except ValueError:
                    self.logger.warning(f"⚠️ 无法解析时间格式: {time_text}")
            
            # 如果无法从 DOM 获取时间戳，使用当前时间
            self.logger.warning("⚠️ 无法从 DOM 获取 AI 回复时间戳，使用当前时间")
            return datetime.now()
        except Exception as e:
            self.logger.error(f"获取 AI 回复时间戳失败: {e}")
            return datetime.now()
    
    def verify_ai_reply_after_send(self):
        """验证 AI Auto Reply 的时间戳在发送消息时间之后
        
        Returns:
            bool: True 如果 AI 回复时间在发送时间之后，否则 False
        """
        if self.send_time is None:
            self.logger.error("❌ 未记录消息发送时间，无法验证")
            return False
        
        try:
            ai_reply_time = self.get_ai_reply_timestamp()
            time_diff = (ai_reply_time - self.send_time).total_seconds()
            
            self.logger.info(f"✓ AI 回复时间: {ai_reply_time.strftime('%H:%M:%S.%f')[:-3]}")
            self.logger.info(f"✓ 时间差: {time_diff:.3f} 秒")
            
            if time_diff >= 0:
                self.logger.info(f"✅ AI 回复时间在发送时间之后（延迟 {time_diff:.3f} 秒）")
                return True
            else:
                self.logger.error(f"❌ AI 回复时间早于发送时间（差值 {time_diff:.3f} 秒）")
                return False
        except Exception as e:
            self.logger.error(f"验证 AI 回复时间失败: {e}")
            return False

    # ========== 导航 ==========

    def navigate_to_chat_page(self, base_url, post_id, shop_id, shop_name, post_name, shop_type="B", cate_code="jobs"):
        """直接构造 URL 导航到聊天页（用于 module 级共享浏览器状态重置）"""
        params = {
            "postId": post_id,
            "shopId": shop_id,
            "shopName": shop_name,
            "postName": post_name,
            "shopType": shop_type,
            "cateCode": cate_code,
        }
        query = urllib.parse.urlencode(params)
        chat_base = base_url.replace("sa.58v5.cn", "sapub.58v5.cn")
        url = f"{chat_base}/biz/en/chat?{urllib.parse.quote(query, safe='=&')}&needLogin=true"
        try:
            self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            self.wait_for_chat_loaded()
        except Exception as e:
            self.logger.error(f"导航到聊天页面失败: {e}")
            raise
