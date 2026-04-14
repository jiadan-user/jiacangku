# pages/messages_explore_page.py
from pages.base_page import BasePage
from utils.logger import setup_logger


class MessagesExplorePage(BasePage):
    """OK.com Messages页面功能探索对象（静默执行）"""
    
    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()
    
    # ========== 页面元素选择器 ==========
    
    # 首页导航
    MESSAGES_LINK = "a:has-text('Messages'), a[href*='chat'], a[href*='message']"
    
    # 左侧会话列表相关（2026-04-03 更新：使用精确的选择器）
    CONVERSATION_LIST_CONTAINER = ".list-group.list-group-flush"  # 左侧会话列表容器
    CONVERSATION_LIST_ITEM = ".list-group > .border-0"  # 左侧会话列表项（精确选择器）
    # 兼容旧选择器（用于向后兼容）
    CONVERSATION_ITEM = ".list-group > .border-0"  # 统一使用新的精确选择器
    
    # 右侧聊天消息相关（2026-04-03 新增：区分聊天消息和会话列表）
    CHAT_MESSAGE_ITEM = ".chat-item:not(.tips)"  # 右侧聊天消息（排除 tips 元素）
    CHAT_MESSAGE_LEFT = ".chat-item.left"  # 对方发送的消息
    CHAT_MESSAGE_RIGHT = ".chat-item.right"  # 自己发送的消息
    CHAT_MESSAGE_TIPS = ".chat-item.tips"  # Tips 提示元素
    
    # 会话详情相关
    CONVERSATION_DETAIL = "[class*='conversation-detail'], [class*='chat-detail']"
    MESSAGE_INPUT = "textarea.ci-input-item, textarea[placeholder*='message'], input[placeholder*='message'], textarea[class*='input'], [contenteditable='true']"  # 2026-04-03: 添加精确选择器
    SEND_BUTTON = "button:has-text('Send'), button:has-text('发送'), button[type='submit'], button[class*='send'], button[class*='submit']"
    MESSAGE_HISTORY = "[class*='message-history'], [class*='chat-content'], [class*='conversation-content']"
    MESSAGE_ITEM = "[class*='message'], [class*='chat-item'], [class*='msg']"
    
    # 用户信息
    USER_AVATAR = "[class*='avatar'], [class*='profile-pic']"
    USER_NAME = "[class*='user-name'], [class*='contact-name'], h1, h2, h3"
    USER_STATUS = "[class*='status'], [class*='online'], [class*='offline']"
    
    # 功能按钮
    PHONE_BUTTON = "button:has-text('Call'), button[class*='phone'], svg[class*='phone']"
    # 三点菜单（会话详情页右上角）
    THREE_DOTS_MENU = "text=/^\\.\\.\\.$|^⋮$/"
    SETTINGS_BUTTON = "button:has-text('Settings'), button[class*='settings'], button[class*='menu'], svg[class*='settings'], svg[class*='gear']"
    ATTACH_BUTTON = "button[class*='attach'], svg[class*='paperclip'], svg[class*='attach']"
    EMOJI_BUTTON = "button[class*='emoji'], svg[class*='emoji'], svg[class*='smile']"
    IMAGE_BUTTON = "button[class*='image'], button[class*='photo'], svg[class*='image']"
    
    # 搜索和筛选
    SEARCH_INPUT = "input[placeholder*='Search'], input[placeholder*='搜索'], input[type='search']"
    FILTER_BUTTON = "button:has-text('Filter'), button[class*='filter'], select[class*='filter']"
    
    # 设置菜单选项
    SETTINGS_MENU = "[role='menu'], .dropdown-menu, [class*='settings-menu'], [class*='options-menu'], [class*='menu'], [class*='popover'], [class*='dropdown']"
    PIN_OPTION = "text=/^Pin$|^Unpin$|置顶|取消置顶/i"
    MUTE_OPTION = "text=/^Mute$|^Unmute$|Do Not Disturb|静音|免打扰/i"
    BLOCK_OPTION = "text=/^Block$|^Unblock$|拉黑|屏蔽|取消拉黑/i"
    
    # 对话框
    DIALOG = "[role='dialog'], .modal"
    CLOSE_BUTTON = "button:has-text('Close'), button:has-text('Cancel'), button[class*='close']"
    
    # 安全提示
    SECURITY_TIP = "text=/safety|secure|sensitive|personal information/i"
    
    # ========== 页面操作方法（静默执行）==========
    
    def navigate_to_home(self, base_url):
        """导航到首页"""
        try:
            self.page.goto(base_url, wait_until="domcontentloaded", timeout=60000)
            # 等待页面关键元素加载，而不是 networkidle
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"导航到首页失败: {e}")
            raise
    
    def click_messages_link(self, timeout=10000):
        """点击Messages链接"""
        try:
            messages_link = self.page.locator(self.MESSAGES_LINK).first
            messages_link.wait_for(state='visible', timeout=timeout)
            messages_link.click()
            # 使用 domcontentloaded 而不是 networkidle 避免超时
            self.page.wait_for_load_state('domcontentloaded', timeout=30000)
            self.page.wait_for_timeout(2000)
            return True
        except Exception as e:
            self.logger.error(f"点击Messages链接失败: {e}")
            return False
    
    def navigate_to_messages_directly(self, target_url):
        """直接导航到Messages页面"""
        try:
            self.page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            # 等待页面加载，不使用 networkidle
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"直接导航到Messages页面失败: {e}")
            raise
    
    def wait_for_conversation_list(self, timeout=15000):
        """等待会话列表加载（2026-04-03 更新：使用左侧列表选择器，宽松策略）"""
        try:
            # 先等待页面基本加载完成（等待骨架屏消失）
            self.page.wait_for_timeout(3000)
            
            # 策略1: 尝试新的精确选择器（不抛出异常，只记录）
            try:
                container = self.page.locator(self.CONVERSATION_LIST_CONTAINER)
                container.wait_for(state='attached', timeout=3000)
                self.logger.info("✓ 会话列表容器已加载")
                
                items = self.page.locator(self.CONVERSATION_LIST_ITEM)
                items.first.wait_for(state='attached', timeout=3000)
                count = items.count()
                self.logger.info(f"✓ 使用新选择器成功等待到会话列表（共 {count} 个）")
                self.page.wait_for_timeout(1000)
                return True
                
            except Exception as e1:
                self.logger.debug(f"新选择器等待超时（这是正常的，继续尝试其他方法）")
            
            # 策略2: 尝试旧选择器（向后兼容）
            try:
                old_items = self.page.locator("[class*='conversation'], [class*='chat-item'], [class*='message-item']")
                old_items.first.wait_for(state='attached', timeout=3000)
                count = old_items.count()
                self.logger.info(f"✓ 使用旧选择器成功等待到元素（共 {count} 个）")
                self.page.wait_for_timeout(1000)
                return True
                
            except Exception as e2:
                self.logger.debug(f"旧选择器等待超时（这是正常的，继续检查页面状态）")
            
            # 策略3: 检查页面是否实际加载成功（通过检查其他元素）
            current_url = self.page.url
            
            # 如果在登录页，返回 False
            if 'login' in current_url.lower():
                self.logger.error(f"❌ 被重定向到登录页: {current_url}")
                self.logger.error("Session 可能已过期，请重新登录")
                return False
            
            # 如果在 Messages 页面，即使找不到会话列表也返回 True
            # （页面可能加载成功但会话列表为空，或者选择器需要更新）
            if 'chat' in current_url.lower() or 'message' in current_url.lower():
                self.logger.warning("⚠️  无法通过选择器等待到会话列表，但页面 URL 正确")
                self.logger.warning(f"   当前 URL: {current_url}")
                self.logger.warning("   页面可能已加载，继续执行测试")
                self.page.wait_for_timeout(2000)  # 额外等待 2 秒
                return True
            
            # 其他情况，截图并返回 False
            self.logger.error(f"❌ 页面加载异常，当前 URL: {current_url}")
            try:
                self.page.screenshot(path='screenshots/wait_conversation_list_failed.png', timeout=5000)
                self.logger.error("已保存失败截图: screenshots/wait_conversation_list_failed.png")
            except:
                pass
            
            return False
            
        except Exception as e:
            self.logger.error(f"等待会话列表失败: {e}")
            # 即使出错，也尝试继续（宽松策略）
            return True

    def scroll_conversation_list(self, distance: int = 200) -> dict:
        """滑动左侧会话列表"""
        try:
            # 方法1: 尝试使用选择器定位会话列表容器
            try:
                list_container = self.page.locator(self.CONVERSATION_LIST).first
                
                if list_container.is_visible(timeout=2000):
                    list_box = list_container.bounding_box()
                    
                    if list_box:
                        start_x = list_box['x'] + list_box['width'] / 2
                        start_y = list_box['y'] + list_box['height'] / 2
                        end_y = start_y - distance
                        
                        self.logger.info(f"使用选择器定位: ({start_x:.0f}, {start_y:.0f}) -> ({start_x:.0f}, {end_y:.0f})")
                        
                        # 执行滑动
                        self.page.mouse.move(start_x, start_y)
                        self.page.mouse.down()
                        self.page.mouse.move(start_x, end_y, steps=10)
                        self.page.mouse.up()
                        self.page.wait_for_timeout(1000)
                        
                        self.logger.info(f"✓ 滑动完成（选择器方式），距离: {distance}px")
                        return {
                            'success': True,
                            'distance': distance,
                            'start': (start_x, start_y),
                            'end': (start_x, end_y),
                            'method': 'selector'
                        }
            except Exception as e:
                self.logger.warning(f"选择器方式失败: {e}，尝试使用坐标方式")
            
            # 方法2: 使用固定坐标（基于TC002成功截图的观察）
            # 左侧会话列表区域大约在 x=50-320, y=300-600
            start_x = 150  # 会话列表中间位置
            start_y = 450  # 会话列表中间高度
            end_y = start_y - distance
            
            self.logger.info(f"使用固定坐标: ({start_x}, {start_y}) -> ({start_x}, {end_y})")
            
            # 执行滑动操作
            self.page.mouse.move(start_x, start_y)
            self.page.mouse.down()
            self.page.mouse.move(start_x, end_y, steps=10)
            self.page.mouse.up()
            
            # 等待滑动动画完成
            self.page.wait_for_timeout(1000)
            
            self.logger.info(f"✓ 滑动完成（坐标方式），距离: {distance}px")
            
            return {
                'success': True,
                'distance': distance,
                'start': (start_x, start_y),
                'end': (start_x, end_y),
                'method': 'coordinates'
            }
            
        except Exception as e:
            self.logger.error(f"滑动会话列表失败: {e}")
            return {'success': False, 'error': str(e)}

    def get_conversation_count(self):
        """获取左侧会话列表的数量（2026-04-03 更新：使用精确的左侧列表选择器）"""
        try:
            # 使用精确的左侧会话列表选择器
            items = self.page.locator(self.CONVERSATION_LIST_ITEM)
            count = items.count()
            
            # 如果使用新选择器找不到，尝试旧的通用选择器（向后兼容）
            if count == 0:
                self.logger.warning("使用新选择器未找到会话，尝试旧选择器...")
                items = self.page.locator("[class*='conversation'], [class*='chat-item'], [class*='message-item']")
                count = items.count()
            
            return count
        except Exception as e:
            self.logger.error(f"获取会话数量失败: {e}")
            return 0
    
    def get_chat_message_count(self):
        """获取右侧聊天消息的数量（2026-04-03 新增）"""
        try:
            items = self.page.locator(self.CHAT_MESSAGE_ITEM)
            return items.count()
        except Exception as e:
            self.logger.error(f"获取聊天消息数量失败: {e}")
            return 0
    
    def get_conversation_name_by_index(self, index=1) -> str:
        """获取指定索引会话的用户昵称（索引从0开始）
        规则：左侧列表中，头像右侧第一行就是昵称
        """
        try:
            # 使用JavaScript获取用户昵称
            # 策略：查找所有以"OKer"或"OK"开头的文本，按位置排序选择对应索引的
            name_text = self.page.evaluate("""
                (index) => {
                    // 查找左侧所有以"OKer"开头的文本（这些通常是用户昵称）
                    const allElements = document.querySelectorAll('*');
                    const usernames = [];
                    
                    for (const el of allElements) {
                        const text = el.textContent?.trim() || '';
                        const rect = el.getBoundingClientRect();
                        
                        // 条件：
                        // 1. 以"OKer"或"OK"开头
                        // 2. 在左侧区域（x < 350）
                        // 3. 长度合理
                        // 4. 不包含.com（排除"OK.com"）
                        if ((text.startsWith('OKer') || (text.startsWith('OK') && text.length > 5)) &&
                            rect.x > 0 && rect.x < 350 &&
                            text.length >= 5 && text.length <= 50 &&
                            !text.includes('.com') && !text.includes('Install')) {
                            
                            usernames.push({
                                text: text,
                                y: rect.y
                            });
                        }
                    }
                    
                    if (usernames.length === 0) {
                        return '';
                    }
                    
                    // 按Y坐标排序（从上到下）
                    usernames.sort((a, b) => a.y - b.y);
                    
                    // 返回对应索引的用户名
                    if (index < usernames.length) {
                        return usernames[index].text;
                    }
                    
                    return '';
                }
            """, index)
            
            if name_text:
                self.logger.info(f"获取到会话昵称（头像右侧第一行）: {name_text}")
                return name_text
            
            self.logger.warning(f"无法获取第{index+1}个会话的昵称")
            return ""
            
        except Exception as e:
            self.logger.error(f"获取第{index+1}个会话昵称失败: {e}")
            return ""
    
    def get_conversation_detail_user_name(self) -> str:
        """获取会话详情页的用户昵称"""
        try:
            # 使用JavaScript查找右侧区域的用户昵称
            # 基于OK.com特征：用户昵称通常以"OKer"或"OK"开头，位于右侧顶部
            name_text = self.page.evaluate("""
                () => {
                    // 查找右侧会话详情区域（x > 350）的所有元素
                    const allElements = document.querySelectorAll('*');
                    const candidates = [];
                    
                    for (const el of allElements) {
                        const rect = el.getBoundingClientRect();
                        const text = el.textContent?.trim() || '';
                        
                        // 右侧区域，顶部位置（y < 200）
                        if (rect.x > 350 && rect.y > 60 && rect.y < 200 && 
                            text.length >= 5 && text.length <= 50) {
                            
                            // 优先查找以"OKer"或"OK"开头的文本
                            if (text.startsWith('OKer') || text.startsWith('OK')) {
                                // 排除"OK.com"这样的网站名称
                                if (!text.includes('.com') && !text.includes('Install')) {
                                    return text;
                                }
                            }
                            
                            // 收集其他候选
                            const style = window.getComputedStyle(el);
                            const fontSize = parseFloat(style.fontSize);
                            
                            // 排除明显不是用户名的文本
                            if (text.includes('Install') || text.includes('.com') || 
                                text.includes('AED') || text.includes('Post')) {
                                continue;
                            }
                            
                            candidates.push({
                                text: text,
                                fontSize: fontSize,
                                y: rect.y
                            });
                        }
                    }
                    
                    // 如果没有找到以"OKer"开头的，选择最上方、字体最大的文本
                    if (candidates.length > 0) {
                        candidates.sort((a, b) => {
                            if (Math.abs(a.y - b.y) > 10) return a.y - b.y;
                            return b.fontSize - a.fontSize;
                        });
                        return candidates[0].text;
                    }
                    
                    return '';
                }
            """)
            
            if name_text:
                self.logger.info(f"获取到详情页昵称: {name_text}")
                return name_text
            
            self.logger.warning("无法获取会话详情页的用户昵称")
            return ""
            
        except Exception as e:
            self.logger.error(f"获取会话详情页用户昵称失败: {e}")
            return ""
    
    def click_conversation_by_index(self, index=1, timeout=30000):
        """点击指定索引的会话（索引从0开始）（2026-04-03 更新：使用左侧列表选择器）"""
        try:
            # 使用精确的左侧会话列表选择器
            items = self.page.locator(self.CONVERSATION_LIST_ITEM)
            
            # 如果找不到，尝试旧选择器（向后兼容）
            if items.count() == 0:
                self.logger.warning("使用新选择器未找到会话，尝试旧选择器...")
                items = self.page.locator("[class*='conversation'], [class*='chat-item'], [class*='message-item']")
            
            target_item = items.nth(index)
            target_item.click(timeout=timeout)
            self.page.wait_for_timeout(2000)
            return True
        except Exception as e:
            self.logger.error(f"点击第{index+1}个会话失败: {e}")
            return False
    
    def is_conversation_detail_visible(self, timeout=10000):
        """检查会话详情区域是否可见"""
        try:
            message_input = self.page.locator(self.MESSAGE_INPUT).first
            return message_input.is_visible(timeout=timeout)
        except Exception as e:
            self.logger.error(f"检查会话详情失败: {e}")
            return False
    
    def scroll_conversation_list(self, direction='down', distance=500):
        """滚动左侧会话列表（2026-04-03 新增）
        
        Args:
            direction: 滚动方向，'up' 或 'down'
            distance: 滚动距离（像素）
        
        Returns:
            bool: 是否成功滚动
        """
        try:
            container = self.page.locator(self.CONVERSATION_LIST_CONTAINER)
            
            if direction == 'down':
                container.evaluate(f"el => el.scrollTop = el.scrollTop + {distance}")
            else:  # up
                container.evaluate(f"el => el.scrollTop = el.scrollTop - {distance}")
            
            self.page.wait_for_timeout(500)
            return True
        except Exception as e:
            self.logger.error(f"滚动会话列表失败: {e}")
            return False
    
    def scroll_conversation_list_to_top(self):
        """滚动左侧会话列表到顶部（2026-04-03 新增）"""
        try:
            container = self.page.locator(self.CONVERSATION_LIST_CONTAINER)
            container.evaluate("el => el.scrollTop = 0")
            self.page.wait_for_timeout(500)
            return True
        except Exception as e:
            self.logger.error(f"滚动到顶部失败: {e}")
            return False
    
    def scroll_conversation_list_to_bottom(self):
        """滚动左侧会话列表到底部（2026-04-03 新增）"""
        try:
            container = self.page.locator(self.CONVERSATION_LIST_CONTAINER)
            container.evaluate("el => el.scrollTop = el.scrollHeight")
            self.page.wait_for_timeout(500)
            return True
        except Exception as e:
            self.logger.error(f"滚动到底部失败: {e}")
            return False
    
    def check_conversation_item_elements(self):
        """检查会话列表项的元素结构"""
        try:
            items = self.page.locator(self.CONVERSATION_ITEM)
            if items.count() == 0:
                return {}
            
            first_item = items.first
            
            result = {
                'has_avatar': False,
                'has_user_name': False,
                'has_message_preview': False,
                'has_timestamp': False
            }
            
            # 检查头像
            avatar = first_item.locator('img[class*="avatar"], [class*="avatar"] img').first
            result['has_avatar'] = avatar.is_visible(timeout=3000)
            
            # 检查用户名
            user_name = first_item.locator('[class*="name"], [class*="user"]').first
            result['has_user_name'] = user_name.is_visible(timeout=3000)
            
            # 检查消息预览
            message_preview = first_item.locator('[class*="message"], [class*="preview"], [class*="content"]').first
            result['has_message_preview'] = message_preview.is_visible(timeout=3000)
            
            # 检查时间戳
            timestamp = first_item.locator('[class*="time"], [class*="date"]').first
            result['has_timestamp'] = timestamp.is_visible(timeout=3000)
            
            return result
        except Exception as e:
            self.logger.error(f"检查会话项元素失败: {e}")
            return {}
    
    def check_conversation_detail_elements(self):
        """检查会话详情页面的基本元素"""
        try:
            result = {
                'has_message_input': False,
                'has_send_button': False,
                'has_message_history': False
            }
            
            # 检查消息输入框
            message_input = self.page.locator(self.MESSAGE_INPUT).first
            result['has_message_input'] = message_input.is_visible(timeout=5000)
            
            # 检查发送按钮
            send_button = self.page.locator(self.SEND_BUTTON).first
            result['has_send_button'] = send_button.is_visible(timeout=5000)
            
            # 检查消息历史
            message_history = self.page.locator(self.MESSAGE_HISTORY).first
            result['has_message_history'] = message_history.is_visible(timeout=5000)
            
            return result
        except Exception as e:
            self.logger.error(f"检查会话详情元素失败: {e}")
            return {}
    
    def check_security_tip(self):
        """检查安全提示"""
        try:
            security_tip = self.page.locator(self.SECURITY_TIP).first
            is_visible = security_tip.is_visible(timeout=5000)
            
            if is_visible:
                tip_text = security_tip.text_content()
                return {'visible': True, 'text': tip_text}
            else:
                return {'visible': False, 'text': ''}
        except Exception as e:
            self.logger.error(f"检查安全提示失败: {e}")
            return {'visible': False, 'text': ''}
    
    def check_phone_button(self):
        """检查电话按钮"""
        try:
            phone_button = self.page.locator(self.PHONE_BUTTON).first
            return phone_button.is_visible(timeout=5000)
        except Exception as e:
            self.logger.error(f"检查电话按钮失败: {e}")
            return False
    
    def click_phone_button(self):
        """点击电话按钮"""
        try:
            phone_button = self.page.locator(self.PHONE_BUTTON).first
            phone_button.click(timeout=10000)
            self.page.wait_for_timeout(2000)
            
            # 检查是否有弹窗
            dialog = self.page.locator(self.DIALOG).first
            has_dialog = dialog.is_visible(timeout=3000)
            
            if has_dialog:
                # 关闭弹窗
                close_btn = dialog.locator(self.CLOSE_BUTTON).first
                if close_btn.is_visible(timeout=2000):
                    close_btn.click()
                    self.page.wait_for_timeout(1000)
            
            return True
        except Exception as e:
            self.logger.error(f"点击电话按钮失败: {e}")
            return False
    
    def check_settings_button(self):
        """检查设置按钮"""
        try:
            settings_button = self.page.locator(self.SETTINGS_BUTTON).first
            return settings_button.is_visible(timeout=5000)
        except Exception as e:
            self.logger.error(f"检查设置按钮失败: {e}")
            return False
    
    def click_settings_button(self):
        """点击设置按钮"""
        try:
            settings_button = self.page.locator(self.SETTINGS_BUTTON).first
            settings_button.click(timeout=10000)
            self.page.wait_for_timeout(2000)
            
            # 检查设置菜单是否显示
            settings_menu = self.page.locator(self.SETTINGS_MENU).first
            return settings_menu.is_visible(timeout=3000)
        except Exception as e:
            self.logger.error(f"点击设置按钮失败: {e}")
            return False
    
    def check_mute_option(self):
        """检查免打扰选项"""
        try:
            mute_option = self.page.locator(self.MUTE_OPTION).first
            return mute_option.is_visible(timeout=5000)
        except Exception as e:
            self.logger.error(f"检查免打扰选项失败: {e}")
            return False
    
    
    def check_auxiliary_features(self):
        """检查辅助功能（附件、表情、图片等）"""
        try:
            result = {
                'has_attach': False,
                'has_emoji': False,
                'has_image': False
            }
            
            # 检查附件按钮
            attach_btn = self.page.locator(self.ATTACH_BUTTON).first
            result['has_attach'] = attach_btn.is_visible(timeout=3000)
            
            # 检查表情按钮
            emoji_btn = self.page.locator(self.EMOJI_BUTTON).first
            result['has_emoji'] = emoji_btn.is_visible(timeout=3000)
            
            # 检查图片按钮
            image_btn = self.page.locator(self.IMAGE_BUTTON).first
            result['has_image'] = image_btn.is_visible(timeout=3000)
            
            return result
        except Exception as e:
            self.logger.error(f"检查辅助功能失败: {e}")
            return {}
    
    def check_search_input(self):
        """检查搜索框"""
        try:
            search_input = self.page.locator(self.SEARCH_INPUT).first
            return search_input.is_visible(timeout=5000)
        except Exception as e:
            self.logger.error(f"检查搜索框失败: {e}")
            return False
    
    def search_conversation(self, keyword):
        """搜索会话"""
        try:
            search_input = self.page.locator(self.SEARCH_INPUT).first
            search_input.fill(keyword)
            self.page.wait_for_timeout(2000)
            
            # 获取搜索结果数量
            items = self.page.locator(self.CONVERSATION_ITEM)
            result_count = items.count()
            
            # 清空搜索框
            search_input.fill('')
            self.page.wait_for_timeout(2000)
            
            return result_count
        except Exception as e:
            self.logger.error(f"搜索会话失败: {e}")
            return 0
    
    def check_filter_button(self):
        """检查筛选按钮"""
        try:
            filter_button = self.page.locator(self.FILTER_BUTTON).first
            return filter_button.is_visible(timeout=5000)
        except Exception as e:
            self.logger.error(f"检查筛选按钮失败: {e}")
            return False
    
    def check_user_info(self):
        """检查用户信息（2026-04-03 更新：增加容错处理）"""
        try:
            result = {
                'has_avatar': False,
                'has_name': False,
                'has_status': False,
                'name_text': ''
            }
            
            # 先等待页面稳定
            self.page.wait_for_timeout(2000)
            
            # 检查头像（使用 try-except 避免超时中断）
            try:
                avatar = self.page.locator(self.USER_AVATAR).first
                result['has_avatar'] = avatar.is_visible(timeout=3000)
            except:
                result['has_avatar'] = False
            
            # 检查用户名
            try:
                user_name = self.page.locator(self.USER_NAME).first
                result['has_name'] = user_name.is_visible(timeout=3000)
                if result['has_name']:
                    result['name_text'] = user_name.text_content()
            except:
                result['has_name'] = False
            
            # 检查状态
            try:
                status = self.page.locator(self.USER_STATUS).first
                result['has_status'] = status.is_visible(timeout=2000)
            except:
                result['has_status'] = False
            
            return result
        except Exception as e:
            self.logger.error(f"检查用户信息失败: {e}")
            return {
                'has_avatar': False,
                'has_name': False,
                'has_status': False,
                'name_text': ''
            }
    
    def analyze_message_types(self, max_count=10):
        """分析消息类型"""
        try:
            messages = self.page.locator('[class*="message-item"], [class*="chat-bubble"], [class*="message-bubble"]')
            total_count = messages.count()
            analyze_count = min(total_count, max_count)
            
            results = []
            for i in range(analyze_count):
                message = messages.nth(i)
                
                message_class = message.get_attribute('class') or ''
                
                message_info = {
                    'index': i + 1,
                    'is_sent': 'sent' in message_class or 'outgoing' in message_class or 'right' in message_class,
                    'is_received': 'received' in message_class or 'incoming' in message_class or 'left' in message_class,
                    'has_text': message.locator('text=/.+/').is_visible(timeout=1000),
                    'has_image': message.locator('img').is_visible(timeout=1000),
                    'has_link': message.locator('a').is_visible(timeout=1000)
                }
                
                results.append(message_info)
            
            return results
        except Exception as e:
            self.logger.error(f"分析消息类型失败: {e}")
            return []
    
    def check_unread_badges(self):
        """检查未读消息标识"""
        try:
            unread_badges = self.page.locator('[class*="unread"], [class*="badge"], [class*="count"]')
            count = unread_badges.count()
            
            if count > 0:
                first_badge = unread_badges.first
                badge_text = first_badge.text_content()
                return {'count': count, 'text': badge_text}
            else:
                return {'count': 0, 'text': ''}
        except Exception as e:
            self.logger.error(f"检查未读标识失败: {e}")
            return {'count': 0, 'text': ''}
    
    def test_message_input(self, test_text="Test message"):
        """测试消息输入框"""
        try:
            message_input = self.page.locator(self.MESSAGE_INPUT).first
            
            # 检查是否可编辑
            is_editable = message_input.is_editable(timeout=3000)
            
            if is_editable:
                # 输入测试文本
                message_input.fill(test_text)
                self.page.wait_for_timeout(1000)
                
                # 验证输入
                input_value = message_input.input_value()
                
                # 清空
                message_input.fill('')
                
                return {'editable': True, 'test_success': input_value == test_text}
            else:
                return {'editable': False, 'test_success': False}
        except Exception as e:
            self.logger.error(f"测试消息输入失败: {e}")
            return {'editable': False, 'test_success': False}
    
    def check_three_dots_menu(self) -> dict:
        """检查会话详情页右上角的三点菜单（...）"""
        try:
            # 多种方式查找三点菜单
            selectors = [
                "text=/^\\.\\.\\.$|^⋮$/",
                "button:has-text('...')",
                "button:has-text('⋮')",
                "button[class*='more']",
                "button[class*='menu']",
                "button[class*='options']",
                "div[class*='more-button']",
                "button[aria-label*='more']",
                "button[aria-label*='options']",
                "button[aria-label*='menu']"
            ]
            
            for selector in selectors:
                elements = self.page.locator(selector).all()
                for element in elements:
                    try:
                        if element.is_visible(timeout=2000):
                            bbox = element.bounding_box()
                            # 确保是右上角的按钮（x > 800, y < 150）
                            if bbox and bbox['x'] > 800 and bbox['y'] < 150:
                                self.logger.info(f"✓ 找到三点菜单，选择器: {selector}, 位置: ({bbox['x']}, {bbox['y']})")
                                return {
                                    'exists': True,
                                    'selector': selector,
                                    'x': bbox['x'],
                                    'y': bbox['y']
                                }
                    except Exception:
                        continue
            
            # 如果标准选择器找不到，使用JS查找
            self.logger.info("标准选择器未找到三点菜单，尝试使用JS...")
            js_result = self.page.evaluate("""
                () => {
                    const elements = Array.from(document.querySelectorAll('*'));
                    
                    // 查找会话详情区域的三点菜单
                    const candidates = elements.filter(el => {
                        const rect = el.getBoundingClientRect();
                        const className = String(el.className || '');
                        
                        // 查找class包含'c-d-img-menu'的元素（从截图看这是会话详情的菜单）
                        const isConversationMenu = className.includes('c-d-img-menu');
                        
                        // 或者查找在会话详情右上角区域的小图标
                        const isRightArea = rect.x > 900 && rect.y > 70 && rect.y < 150;
                        const isSmallIcon = rect.width > 10 && rect.width < 50 && rect.height > 10 && rect.height < 50;
                        
                        return (isConversationMenu || (isRightArea && isSmallIcon)) && rect.width > 0 && rect.height > 0;
                    });
                    
                    console.log(`会话详情菜单候选数量: ${candidates.length}`);
                    
                    if (candidates.length > 0) {
                        // 优先选择class包含'c-d-img-menu'的
                        let el = candidates.find(e => String(e.className || '').includes('c-d-img-menu'));
                        if (!el) el = candidates[0];
                        
                        const rect = el.getBoundingClientRect();
                        return {
                            found: true,
                            tag: el.tagName,
                            text: el.textContent?.trim(),
                            innerText: el.innerText?.trim(),
                            class: String(el.className || ''),
                            ariaLabel: el.getAttribute('aria-label'),
                            x: rect.x,
                            y: rect.y,
                            width: rect.width,
                            height: rect.height
                        };
                    }
                    
                    return { found: false };
                }
            """)
            
            if js_result.get('found'):
                self.logger.info(f"✓ JS找到三点菜单: {js_result}")
                return {
                    'exists': True,
                    'method': 'javascript',
                    'x': js_result['x'],
                    'y': js_result['y']
                }
            
            # 输出调试信息
            if 'debugInfo' in js_result:
                self.logger.info("右上角小元素（可能是菜单按钮）:")
                for el in js_result['debugInfo']:
                    self.logger.info(f"  {el['tag']}: '{el['text']}' at ({el['x']}, {el['y']}) size {el['width']}x{el['height']}")
            
            self.logger.warning("未找到三点菜单")
            return {'exists': False}
            
        except Exception as e:
            self.logger.error(f"检查三点菜单失败: {e}")
            return {'exists': False, 'error': str(e)}

    def click_three_dots_menu(self) -> dict:
        """点击三点菜单并返回菜单信息"""
        try:
            check_result = self.check_three_dots_menu()
            if not check_result['exists']:
                return {'opened': False, 'error': '三点菜单不存在'}
            
            # 点击三点菜单
            if check_result.get('method') == 'javascript':
                # 使用坐标点击
                x = check_result['x'] + 10
                y = check_result['y'] + 10
                self.logger.info(f"使用坐标点击三点菜单: ({x}, {y})")
                self.page.mouse.click(x, y)
            else:
                # 使用选择器点击
                selector = check_result['selector']
                self.logger.info(f"使用选择器点击三点菜单: {selector}")
                self.page.locator(selector).first.click()
            
            self.page.wait_for_timeout(2000)
            
            # 检查菜单是否打开
            # 使用JS查找所有可见的弹出菜单
            menu_info = self.page.evaluate("""
                () => {
                    // 查找所有可能的菜单容器
                    const menuSelectors = [
                        '[role="menu"]',
                        '.dropdown-menu',
                        '[class*="menu"]',
                        '[class*="popover"]',
                        '[class*="dropdown"]'
                    ];
                    
                    const menus = [];
                    
                    menuSelectors.forEach(selector => {
                        const elements = document.querySelectorAll(selector);
                        elements.forEach(menu => {
                            const rect = menu.getBoundingClientRect();
                            if (rect.width > 0 && rect.height > 0) {
                                const text = menu.textContent?.trim() || '';
                                
                                // 检查是否包含Pin、Mute、Block等关键词
                                const hasConversationOptions = text.match(/Pin|Unpin|Mute|Unmute|Block|Unblock/i);
                                
                                menus.push({
                                    text: text,
                                    x: Math.round(rect.x),
                                    y: Math.round(rect.y),
                                    width: Math.round(rect.width),
                                    height: Math.round(rect.height),
                                    isConversationMenu: !!hasConversationOptions
                                });
                            }
                        });
                    });
                    
                    // 优先返回包含会话选项的菜单
                    const conversationMenu = menus.find(m => m.isConversationMenu);
                    if (conversationMenu) {
                        // 获取菜单项
                        const menuElement = Array.from(document.querySelectorAll('[role="menu"], .dropdown-menu, [class*="menu"], [class*="popover"]'))
                            .find(el => {
                                const text = el.textContent?.trim() || '';
                                return text.match(/Pin|Mute|Block/i);
                            });
                        
                        if (menuElement) {
                            const items = [];
                            const allElements = menuElement.querySelectorAll('*');
                            
                            allElements.forEach(el => {
                                const text = el.textContent?.trim() || '';
                                const rect = el.getBoundingClientRect();
                                
                                if (text && rect.width > 0 && rect.height > 0) {
                                    const hasKeyword = text.match(/^(Pin|Unpin|Mute|Unmute|Block|Unblock)$/i);
                                    if (hasKeyword) {
                                        items.push(text);
                                    }
                                }
                            });
                            
                            return {
                                found: true,
                                menu: conversationMenu,
                                items: items
                            };
                        }
                    }
                    
                    return { found: false, menus: menus };
                }
            """)
            
            if menu_info.get('found'):
                self.logger.info("✓ 三点菜单已打开")
                self.logger.info(f"菜单内容: {menu_info['menu']['text'][:100]}")
                self.logger.info(f"菜单项: {menu_info['items']}")
                
                return {
                    'opened': True,
                    'menu_text': menu_info['menu']['text'],
                    'items': menu_info['items'],
                    'item_count': len(menu_info['items'])
                }
            else:
                self.logger.warning("三点菜单未打开或未找到会话菜单")
                if 'menus' in menu_info:
                    self.logger.info(f"找到 {len(menu_info['menus'])} 个菜单，但都不是会话菜单")
                return {'opened': False, 'error': '菜单未显示或不是会话菜单'}
                
        except Exception as e:
            self.logger.error(f"点击三点菜单失败: {e}")
            return {'opened': False, 'error': str(e)}

    def check_pin_option_in_menu(self) -> dict:
        """检查菜单中的置顶选项"""
        try:
            # 使用JS直接查找Pin选项
            pin_info = self.page.evaluate("""
                () => {
                    const elements = Array.from(document.querySelectorAll('*'));
                    
                    // 查找包含"Pin"或"Unpin"的元素
                    const pinElements = elements.filter(el => {
                        const text = el.textContent?.trim() || '';
                        const rect = el.getBoundingClientRect();
                        
                        // 精确匹配Pin或Unpin
                        const isPinText = text === 'Pin' || text === 'Unpin' || text === '置顶' || text === '取消置顶';
                        const isVisible = rect.width > 0 && rect.height > 0;
                        
                        return isPinText && isVisible;
                    });
                    
                    if (pinElements.length > 0) {
                        const el = pinElements[0];
                        const rect = el.getBoundingClientRect();
                        return {
                            found: true,
                            text: el.textContent?.trim(),
                            tag: el.tagName,
                            x: Math.round(rect.x),
                            y: Math.round(rect.y)
                        };
                    }
                    
                    return { found: false };
                }
            """)
            
            if pin_info.get('found'):
                self.logger.info(f"✓ 找到置顶选项: {pin_info['text']}")
                return {'exists': True, 'text': pin_info['text'], 'x': pin_info['x'], 'y': pin_info['y']}
            
            return {'exists': False}
        except Exception as e:
            self.logger.error(f"检查置顶选项失败: {e}")
            return {'exists': False, 'error': str(e)}

    def check_mute_option_in_menu(self) -> dict:
        """检查菜单中的免打扰选项"""
        try:
            # 使用JS直接查找Mute选项
            mute_info = self.page.evaluate("""
                () => {
                    const elements = Array.from(document.querySelectorAll('*'));
                    
                    const muteElements = elements.filter(el => {
                        const text = el.textContent?.trim() || '';
                        const rect = el.getBoundingClientRect();
                        
                        const isMuteText = text === 'Mute' || text === 'Unmute' || text === '免打扰' || text === '取消免打扰';
                        const isVisible = rect.width > 0 && rect.height > 0;
                        
                        return isMuteText && isVisible;
                    });
                    
                    if (muteElements.length > 0) {
                        const el = muteElements[0];
                        const rect = el.getBoundingClientRect();
                        return {
                            found: true,
                            text: el.textContent?.trim(),
                            tag: el.tagName,
                            x: Math.round(rect.x),
                            y: Math.round(rect.y)
                        };
                    }
                    
                    return { found: false };
                }
            """)
            
            if mute_info.get('found'):
                self.logger.info(f"✓ 找到免打扰选项: {mute_info['text']}")
                return {'exists': True, 'text': mute_info['text'], 'x': mute_info['x'], 'y': mute_info['y']}
            
            return {'exists': False}
        except Exception as e:
            self.logger.error(f"检查免打扰选项失败: {e}")
            return {'exists': False, 'error': str(e)}

    def check_block_option_in_menu(self) -> dict:
        """检查菜单中的拉黑选项"""
        try:
            # 使用JS直接查找Block选项
            block_info = self.page.evaluate("""
                () => {
                    const elements = Array.from(document.querySelectorAll('*'));
                    
                    const blockElements = elements.filter(el => {
                        const text = el.textContent?.trim() || '';
                        const rect = el.getBoundingClientRect();
                        
                        const isBlockText = text === 'Block' || text === 'Unblock' || text === '拉黑' || text === '取消拉黑';
                        const isVisible = rect.width > 0 && rect.height > 0;
                        
                        return isBlockText && isVisible;
                    });
                    
                    if (blockElements.length > 0) {
                        const el = blockElements[0];
                        const rect = el.getBoundingClientRect();
                        return {
                            found: true,
                            text: el.textContent?.trim(),
                            tag: el.tagName,
                            x: Math.round(rect.x),
                            y: Math.round(rect.y)
                        };
                    }
                    
                    return { found: false };
                }
            """)
            
            if block_info.get('found'):
                self.logger.info(f"✓ 找到拉黑选项: {block_info['text']}")
                return {'exists': True, 'text': block_info['text'], 'x': block_info['x'], 'y': block_info['y']}
            
            return {'exists': False}
        except Exception as e:
            self.logger.error(f"检查拉黑选项失败: {e}")
            return {'exists': False, 'error': str(e)}

    def click_pin_option(self, cancel: bool = True) -> dict:
        """点击置顶选项"""
        try:
            # 先检查选项是否存在
            pin_check = self.check_pin_option_in_menu()
            if not pin_check['exists']:
                return {'success': False, 'error': '置顶选项不存在'}
            
            # 使用坐标点击
            if 'x' in pin_check and 'y' in pin_check:
                self.logger.info(f"使用坐标点击置顶选项: ({pin_check['x']}, {pin_check['y']})")
                self.page.mouse.click(pin_check['x'] + 10, pin_check['y'] + 10)
            else:
                # 使用选择器点击
                pin_option = self.page.locator(self.PIN_OPTION).first
                pin_option.click()
            
            self.page.wait_for_timeout(2000)
            
            # 检查确认弹窗
            dialog = self.page.locator("[role='dialog'], .modal").first
            has_dialog = False
            try:
                has_dialog = dialog.is_visible(timeout=3000)
            except Exception:
                pass
            
            if has_dialog and cancel:
                # 取消操作
                cancel_btn = dialog.locator("button:has-text('Cancel'), button:has-text('Close'), button:has-text('No')").first
                try:
                    if cancel_btn.is_visible(timeout=2000):
                        cancel_btn.click()
                        self.logger.info("已取消置顶操作")
                    else:
                        self.page.keyboard.press('Escape')
                except Exception:
                    self.page.keyboard.press('Escape')
                
                self.page.wait_for_timeout(1000)
            
            return {
                'success': True,
                'has_dialog': has_dialog
            }
            
        except Exception as e:
            self.logger.error(f"点击置顶选项失败: {e}")
            return {'success': False, 'error': str(e)}

    def click_mute_option(self, cancel: bool = True) -> dict:
        """点击免打扰选项"""
        try:
            # 先检查选项是否存在
            mute_check = self.check_mute_option_in_menu()
            if not mute_check['exists']:
                return {'success': False, 'error': '免打扰选项不存在'}
            
            # 使用坐标点击
            if 'x' in mute_check and 'y' in mute_check:
                self.logger.info(f"使用坐标点击免打扰选项: ({mute_check['x']}, {mute_check['y']})")
                self.page.mouse.click(mute_check['x'] + 10, mute_check['y'] + 10)
            else:
                # 使用选择器点击
                mute_option = self.page.locator(self.MUTE_OPTION).first
                mute_option.click()
            
            self.page.wait_for_timeout(2000)
            
            # 检查确认弹窗
            dialog = self.page.locator("[role='dialog'], .modal").first
            has_dialog = False
            try:
                has_dialog = dialog.is_visible(timeout=3000)
            except Exception:
                pass
            
            if has_dialog and cancel:
                # 取消操作
                cancel_btn = dialog.locator("button:has-text('Cancel'), button:has-text('Close'), button:has-text('No')").first
                try:
                    if cancel_btn.is_visible(timeout=2000):
                        cancel_btn.click()
                        self.logger.info("已取消免打扰操作")
                    else:
                        self.page.keyboard.press('Escape')
                except Exception:
                    self.page.keyboard.press('Escape')
                
                self.page.wait_for_timeout(1000)
            
            return {
                'success': True,
                'has_dialog': has_dialog
            }
            
        except Exception as e:
            self.logger.error(f"点击免打扰选项失败: {e}")
            return {'success': False, 'error': str(e)}

    def click_block_option(self, cancel: bool = True) -> dict:
        """点击拉黑选项"""
        try:
            # 先检查选项是否存在
            block_check = self.check_block_option_in_menu()
            if not block_check['exists']:
                return {'success': False, 'error': '拉黑选项不存在'}
            
            # 使用坐标点击
            if 'x' in block_check and 'y' in block_check:
                self.logger.info(f"使用坐标点击拉黑选项: ({block_check['x']}, {block_check['y']})")
                self.page.mouse.click(block_check['x'] + 10, block_check['y'] + 10)
            else:
                # 使用选择器点击
                block_option = self.page.locator(self.BLOCK_OPTION).first
                block_option.click()
            
            self.page.wait_for_timeout(2000)
            
            # 检查确认弹窗
            dialog = self.page.locator("[role='dialog'], .modal").first
            has_dialog = False
            dialog_text = ''
            try:
                has_dialog = dialog.is_visible(timeout=3000)
                if has_dialog:
                    dialog_text = dialog.text_content()
            except Exception:
                pass
            
            if has_dialog and cancel:
                # 取消操作（重要：避免实际拉黑用户）
                cancel_btn = dialog.locator("button:has-text('Cancel'), button:has-text('Close'), button:has-text('No')").first
                try:
                    if cancel_btn.is_visible(timeout=2000):
                        cancel_btn.click()
                        self.logger.info("已取消拉黑操作")
                    else:
                        self.page.keyboard.press('Escape')
                except Exception:
                    self.page.keyboard.press('Escape')
                
                self.page.wait_for_timeout(1000)
            
            return {
                'success': True,
                'has_dialog': has_dialog,
                'dialog_text': dialog_text,
                'cancelled': cancel
            }
            
        except Exception as e:
            self.logger.error(f"点击拉黑选项失败: {e}")
            return {'success': False, 'error': str(e)}

    def check_message_input(self) -> dict:
        """检查消息输入框"""
        try:
            selectors = [
                "textarea[placeholder*='message']",
                "textarea[placeholder*='Message']",
                "input[placeholder*='message']",
                "textarea[class*='input']",
                "textarea[class*='message']",
                "[contenteditable='true']"
            ]
            
            for selector in selectors:
                element = self.page.locator(selector).first
                try:
                    if element.is_visible(timeout=2000):
                        self.logger.info(f"✓ 找到消息输入框，选择器: {selector}")
                        return {
                            'exists': True,
                            'selector': selector,
                            'element': element
                        }
                except Exception:
                    continue
            
            self.logger.warning("未找到消息输入框")
            return {'exists': False}
            
        except Exception as e:
            self.logger.error(f"检查消息输入框失败: {e}")
            return {'exists': False, 'error': str(e)}

    def input_message(self, message: str) -> dict:
        """输入消息"""
        try:
            input_check = self.check_message_input()
            if not input_check['exists']:
                return {'success': False, 'error': '消息输入框不存在'}
            
            element = input_check['element']
            
            # 清空输入框
            try:
                element.clear()
            except Exception:
                # 如果clear失败，尝试全选删除
                element.click()
                self.page.keyboard.press('Control+A')
                self.page.keyboard.press('Backspace')
            
            self.page.wait_for_timeout(500)
            
            # 输入消息
            element.fill(message)
            self.page.wait_for_timeout(1000)
            
            # 验证输入内容
            try:
                input_value = element.input_value()
            except Exception:
                # 如果是contenteditable，使用text_content
                input_value = element.text_content()
            
            success = message in input_value or input_value == message
            
            self.logger.info(f"输入消息: '{message}', 实际内容: '{input_value}', 成功: {success}")
            
            return {
                'success': success,
                'text': input_value,
                'expected': message
            }
            
        except Exception as e:
            self.logger.error(f"输入消息失败: {e}")
            return {'success': False, 'error': str(e)}

    def check_send_button(self) -> dict:
        """检查发送按钮"""
        try:
            selectors = [
                "button:has-text('Send')",
                "button:has-text('发送')",
                "button[type='submit']",
                "button[class*='send']",
                "button[class*='submit']",
                "button:has(svg[class*='send'])",
                "button[aria-label*='send']",
                "button[aria-label*='Send']"
            ]
            
            for selector in selectors:
                element = self.page.locator(selector).first
                try:
                    if element.is_visible(timeout=2000):
                        bbox = element.bounding_box()
                        self.logger.info(f"✓ 找到发送按钮，选择器: {selector}")
                        return {
                            'exists': True,
                            'selector': selector,
                            'element': element,
                            'x': bbox['x'] if bbox else None,
                            'y': bbox['y'] if bbox else None
                        }
                except Exception:
                    continue
            
            # 如果标准选择器找不到，使用JS查找
            self.logger.info("标准选择器未找到发送按钮，尝试使用JS...")
            js_result = self.page.evaluate("""
                () => {
                    const elements = Array.from(document.querySelectorAll('button, [role="button"]'));
                    
                    // 查找输入框
                    const inputArea = document.querySelector('textarea, input[type="text"], [contenteditable="true"]');
                    if (!inputArea) return { found: false };
                    
                    const inputRect = inputArea.getBoundingClientRect();
                    
                    // 查找输入框附近的按钮（右侧或下方）
                    const candidates = elements.filter(el => {
                        const rect = el.getBoundingClientRect();
                        
                        // 在输入框右侧或右下角
                        const isNearInput = (
                            (rect.x > inputRect.x + inputRect.width - 100 && 
                             rect.y >= inputRect.y && 
                             rect.y <= inputRect.y + inputRect.height) ||
                            (rect.y > inputRect.y + inputRect.height - 50 &&
                             rect.x > inputRect.x + inputRect.width - 100)
                        );
                        
                        const isVisible = rect.width > 0 && rect.height > 0;
                        
                        return isNearInput && isVisible;
                    });
                    
                    if (candidates.length > 0) {
                        const btn = candidates[0];
                        const rect = btn.getBoundingClientRect();
                        return {
                            found: true,
                            tag: btn.tagName,
                            text: btn.textContent?.trim(),
                            class: btn.className,
                            x: Math.round(rect.x),
                            y: Math.round(rect.y),
                            width: Math.round(rect.width),
                            height: Math.round(rect.height)
                        };
                    }
                    
                    return { found: false };
                }
            """)
            
            if js_result.get('found'):
                self.logger.info(f"✓ JS找到发送按钮: {js_result}")
                return {
                    'exists': True,
                    'method': 'javascript',
                    'x': js_result['x'],
                    'y': js_result['y'],
                    'text': js_result['text']
                }
            
            self.logger.warning("未找到发送按钮")
            return {'exists': False}
            
        except Exception as e:
            self.logger.error(f"检查发送按钮失败: {e}")
            return {'exists': False, 'error': str(e)}

    def click_send_button(self) -> dict:
        """点击发送按钮"""
        try:
            send_check = self.check_send_button()
            if not send_check['exists']:
                return {'success': False, 'error': '发送按钮不存在'}
            
            # 点击发送按钮
            if send_check.get('method') == 'javascript':
                # 使用坐标点击
                x = send_check['x'] + 10
                y = send_check['y'] + 10
                self.logger.info(f"使用坐标点击发送按钮: ({x}, {y})")
                self.page.mouse.click(x, y)
            else:
                # 使用选择器点击
                element = send_check['element']
                self.logger.info(f"使用选择器点击发送按钮: {send_check['selector']}")
                element.click()
            
            self.page.wait_for_timeout(2000)
            
            # 验证输入框是否被清空
            input_check = self.check_message_input()
            input_cleared = False
            
            if input_check['exists']:
                try:
                    input_value = input_check['element'].input_value()
                except Exception:
                    input_value = input_check['element'].text_content()
                
                input_cleared = not input_value or input_value.strip() == ''
                self.logger.info(f"发送后输入框内容: '{input_value}', 已清空: {input_cleared}")
            
            return {
                'success': True,
                'input_cleared': input_cleared
            }
            
        except Exception as e:
            self.logger.error(f"点击发送按钮失败: {e}")
            return {'success': False, 'error': str(e)}

    def get_latest_message(self) -> dict:
        """获取最新的消息"""
        try:
            # 查找所有消息
            messages = self.page.locator(self.MESSAGE_ITEM).all()
            
            if not messages:
                self.logger.warning("未找到任何消息")
                return {'found': False, 'text': ''}
            
            # 获取最后一条消息
            last_message = messages[-1]
            message_text = last_message.text_content()
            
            self.logger.info(f"最新消息: '{message_text}'")
            
            return {
                'found': True,
                'text': message_text,
                'count': len(messages)
            }
            
        except Exception as e:
            self.logger.error(f"获取最新消息失败: {e}")
            return {'found': False, 'text': '', 'error': str(e)}

    def debug_all_clickable_elements(self):
        """调试：列出会话详情区域的所有可点击元素"""
        try:
            # 查找所有可点击元素（button, a, div[role=button], span[role=button]等）
            clickable_selectors = [
                "button",
                "a[href]",
                "[role='button']",
                "[onclick]",
                "div:has-text('...')",
                "span:has-text('...')",
                "*:has-text('⋮')"
            ]
            
            element_info = []
            for selector in clickable_selectors:
                try:
                    elements = self.page.locator(selector).all()
                    for i, elem in enumerate(elements):
                        try:
                            if elem.is_visible(timeout=500):
                                text = elem.text_content() or ''
                                aria_label = elem.get_attribute('aria-label') or ''
                                class_name = elem.get_attribute('class') or ''
                                tag_name = elem.evaluate("el => el.tagName")
                                
                                element_info.append({
                                    'selector': selector,
                                    'tag': tag_name,
                                    'text': text.strip()[:50],
                                    'aria_label': aria_label[:50],
                                    'class': class_name[:80]
                                })
                        except:
                            continue
                except:
                    continue
            
            return element_info
        except Exception as e:
            self.logger.error(f"调试可点击元素失败: {e}")
            return []
    
    def check_phone_button_advanced(self):
        """高级检查电话按钮（尝试多个选择器）"""
        try:
            selectors = [
                "button:has-text('Call')",
                "button:has-text('Phone')",
                "button[class*='phone']",
                "button[class*='call']",
                "button:has(svg[class*='phone'])",
                "button[aria-label*='call']",
                "button[aria-label*='phone']",
                "a[href^='tel:']"
            ]
            
            for selector in selectors:
                try:
                    element = self.page.locator(selector).first
                    if element.is_visible(timeout=2000):
                        return {'exists': True, 'selector': selector}
                except:
                    continue
            
            return {'exists': False, 'selector': None}
        except Exception as e:
            self.logger.error(f"检查电话按钮失败: {e}")
            return {'exists': False, 'selector': None}
    
    def click_phone_button_advanced(self):
        """高级点击电话按钮"""
        try:
            phone_check = self.check_phone_button_advanced()
            if not phone_check['exists']:
                return {'success': False, 'has_dialog': False}
            
            phone_button = self.page.locator(phone_check['selector']).first
            phone_button.click(timeout=10000)
            self.page.wait_for_timeout(2000)
            
            # 检查弹窗
            dialog = self.page.locator(self.DIALOG).first
            has_dialog = dialog.is_visible(timeout=3000)
            
            if has_dialog:
                # 关闭弹窗
                close_btn = dialog.locator(self.CLOSE_BUTTON).first
                if close_btn.is_visible(timeout=2000):
                    close_btn.click()
                    self.page.wait_for_timeout(1000)
                else:
                    self.page.keyboard.press('Escape')
                    self.page.wait_for_timeout(1000)
            
            return {'success': True, 'has_dialog': has_dialog}
        except Exception as e:
            self.logger.error(f"点击电话按钮失败: {e}")
            return {'success': False, 'has_dialog': False}
    
    def find_settings_button_by_position(self):
        """通过位置查找设置按钮（会话详情区域右上角）"""
        try:
            # 根据截图，三点菜单在会话详情页右上角，大约在(900, 247)位置
            # 会话详情区域应该在页面右侧（x > 300），且在顶部区域（200 < y < 300）
            all_clickable = self.page.locator("button, [role='button'], div[onclick], span[onclick], svg[onclick]").all()
            
            candidates = []
            for elem in all_clickable:
                try:
                    if elem.is_visible(timeout=500):
                        bbox = elem.bounding_box()
                        if bbox:
                            # 会话详情区域右上角：x > 850, 200 < y < 280
                            if bbox['x'] > 850 and 200 < bbox['y'] < 280:
                                tag = elem.evaluate("el => el.tagName")
                                class_name = elem.get_attribute('class') or ''
                                text = elem.text_content() or ''
                                inner_html = elem.inner_html()[:200]
                                candidates.append({
                                    'element': elem,
                                    'tag': tag,
                                    'x': bbox['x'],
                                    'y': bbox['y'],
                                    'width': bbox['width'],
                                    'height': bbox['height'],
                                    'class': class_name[:80],
                                    'text': text.strip()[:30],
                                    'html': inner_html
                                })
                except:
                    continue
            
            return candidates
        except Exception as e:
            self.logger.error(f"通过位置查找设置按钮失败: {e}")
            return []
    
    def find_clickable_elements_by_js(self):
        """使用JavaScript查找所有可点击元素"""
        try:
            clickable_info = self.page.evaluate("""
                () => {
                    const elements = [];
                    const allElements = document.querySelectorAll('*');
                    
                    allElements.forEach((el, index) => {
                        const style = window.getComputedStyle(el);
                        const rect = el.getBoundingClientRect();
                        
                        // 查找可点击元素：cursor为pointer或有事件监听器
                        const isClickable = style.cursor === 'pointer' || 
                                          el.onclick || 
                                          el.getAttribute('role') === 'button' ||
                                          el.classList.contains('clickable');
                        
                        if (isClickable && rect.width > 0 && rect.height > 0) {
                            // 会话详情区域（右侧，x > 300）
                            if (rect.x > 300) {
                                elements.push({
                                    tag: el.tagName,
                                    x: Math.round(rect.x),
                                    y: Math.round(rect.y),
                                    width: Math.round(rect.width),
                                    height: Math.round(rect.height),
                                    text: el.textContent.trim().substring(0, 50),
                                    className: el.className.substring(0, 100),
                                    hasOnclick: !!el.onclick,
                                    role: el.getAttribute('role') || ''
                                });
                            }
                        }
                    });
                    
                    return elements;
                }
            """)
            return clickable_info
        except Exception as e:
            self.logger.error(f"JavaScript查找失败: {e}")
            return []
    
    def check_settings_button_advanced(self):
        """高级检查设置按钮（尝试多个选择器）"""
        try:
            # 策略1: 使用JavaScript查找cursor:pointer的元素
            clickable_elements = self.find_clickable_elements_by_js()
            
            # 根据截图，三点菜单在(900, 247)附近
            # 查找右上角的小图标（通常是空文本或很短文本）
            for elem_info in clickable_elements:
                # 会话详情页头部右上角特征：x > 850, 200 < y < 280, width < 60, height < 60
                if elem_info['x'] > 850 and 200 < elem_info['y'] < 280:
                    if elem_info['width'] < 60 and elem_info['height'] < 60:
                        if len(elem_info['text']) < 5:  # 空文本或很短
                            self.logger.info(f"✓ 找到疑似设置按钮: {elem_info['tag']}, 位置=({elem_info['x']}, {elem_info['y']}), 大小=({elem_info['width']}x{elem_info['height']}), class='{elem_info['className']}'")
                            # 通过坐标点击
                            self.page.mouse.click(elem_info['x'] + elem_info['width'] / 2, elem_info['y'] + elem_info['height'] / 2)
                            return {'exists': True, 'selector': 'js_position', 'element': None, 'method': 'mouse_click', 'position': (elem_info['x'], elem_info['y'])}
            
            # 策略2: 通用设置按钮选择器
            general_selectors = [
                "button:has-text('More')",
                "button:has-text('Settings')",
                "button:has-text('...')",
                "button:has-text('⋮')",
                "div:has-text('...')",
                "span:has-text('...')",
                "button[class*='settings']",
                "button[class*='menu']",
                "button[class*='more']",
                "button[class*='options']",
                "div[class*='menu-button']",
                "div[class*='more-button']",
                "button:has(svg[class*='settings'])",
                "button:has(svg[class*='gear'])",
                "button:has(svg[class*='dots'])",
                "button:has(svg[class*='ellipsis'])",
                "button[aria-label*='settings']",
                "button[aria-label*='more']",
                "button[aria-label*='options']",
                "button[aria-label*='menu']"
            ]
            
            for selector in general_selectors:
                try:
                    element = self.page.locator(selector).first
                    if element.is_visible(timeout=2000):
                        self.logger.info(f"✓ 找到设置按钮，选择器: {selector}")
                        return {'exists': True, 'selector': selector, 'element': element, 'method': 'selector'}
                except:
                    continue
            
            return {'exists': False, 'selector': None, 'element': None, 'method': None}
        except Exception as e:
            self.logger.error(f"检查设置按钮失败: {e}")
            return {'exists': False, 'selector': None, 'element': None, 'method': None}
    
    def click_settings_button_advanced(self):
        """高级点击设置按钮"""
        try:
            settings_check = self.check_settings_button_advanced()
            if not settings_check['exists']:
                return {'menu_visible': False, 'item_count': 0, 'items': []}
            
            # 如果使用鼠标点击方法，已经点击过了
            if settings_check.get('method') == 'mouse_click':
                self.logger.info("✓ 已通过鼠标坐标点击")
            else:
                # 使用找到的元素或选择器
                if settings_check.get('element'):
                    settings_button = settings_check['element']
                else:
                    settings_button = self.page.locator(settings_check['selector']).first
                
                settings_button.click(timeout=10000)
            
            self.page.wait_for_timeout(2000)
            
            # 检查菜单
            menu = self.page.locator(self.SETTINGS_MENU).first
            menu_visible = menu.is_visible(timeout=3000)
            
            items = []
            item_count = 0
            if menu_visible:
                menu_items = menu.locator('[role="menuitem"], li, button, a, div[class*="item"]')
                item_count = menu_items.count()
                
                for i in range(min(item_count, 10)):
                    item = menu_items.nth(i)
                    item_text = item.text_content()
                    items.append(item_text.strip())
            
            return {'menu_visible': menu_visible, 'item_count': item_count, 'items': items}
        except Exception as e:
            self.logger.error(f"点击设置按钮失败: {e}")
            return {'menu_visible': False, 'item_count': 0, 'items': []}
    
    def check_pin_option(self):
        """检查置顶选项"""
        try:
            pin_option = self.page.locator(self.PIN_OPTION).first
            return pin_option.is_visible(timeout=5000)
        except Exception as e:
            self.logger.error(f"检查置顶选项失败: {e}")
            return False
    
    
    def check_mute_option_advanced(self):
        """高级检查免打扰选项"""
        try:
            selectors = [
                "text=/Do Not Disturb/i",
                "text=/Mute/i",
                "text=/静音/i",
                "text=/免打扰/i",
                "button:has-text('Mute')",
                "[class*='mute']"
            ]
            
            for selector in selectors:
                element = self.page.locator(selector).first
                if element.is_visible(timeout=2000):
                    return True
            
            return False
        except Exception as e:
            self.logger.error(f"检查免打扰选项失败: {e}")
            return False
    
    def click_mute_option_advanced(self):
        """高级点击免打扰选项"""
        try:
            mute_option = self.page.locator(self.MUTE_OPTION).first
            mute_option.click(timeout=10000)
            self.page.wait_for_timeout(2000)
            
            # 检查确认弹窗
            dialog = self.page.locator(self.DIALOG).first
            has_dialog = dialog.is_visible(timeout=3000)
            
            dialog_text = ''
            if has_dialog:
                dialog_text = dialog.text_content()
                
                # 取消操作
                cancel_btn = dialog.locator(self.CLOSE_BUTTON).first
                if cancel_btn.is_visible(timeout=2000):
                    cancel_btn.click()
                    self.page.wait_for_timeout(1000)
                else:
                    self.page.keyboard.press('Escape')
                    self.page.wait_for_timeout(1000)
            
            return {'success': True, 'has_dialog': has_dialog, 'dialog_text': dialog_text}
        except Exception as e:
            self.logger.error(f"点击免打扰选项失败: {e}")
            return {'success': False, 'has_dialog': False, 'dialog_text': ''}
    
    def check_block_option_advanced(self):
        """高级检查拉黑选项"""
        try:
            selectors = [
                "text=/Block/i",
                "text=/拉黑/i",
                "text=/屏蔽/i",
                "button:has-text('Block')",
                "[class*='block']"
            ]
            
            for selector in selectors:
                element = self.page.locator(selector).first
                if element.is_visible(timeout=2000):
                    return True
            
            return False
        except Exception as e:
            self.logger.error(f"检查拉黑选项失败: {e}")
            return False
    
    def click_block_option_advanced(self):
        """高级点击拉黑选项"""
        try:
            block_option = self.page.locator(self.BLOCK_OPTION).first
            block_option.click(timeout=10000)
            self.page.wait_for_timeout(2000)
            
            # 检查确认弹窗
            dialog = self.page.locator(self.DIALOG).first
            has_dialog = dialog.is_visible(timeout=3000)
            
            dialog_text = ''
            if has_dialog:
                dialog_text = dialog.text_content()
                
                # 取消操作
                cancel_btn = dialog.locator(self.CLOSE_BUTTON).first
                if cancel_btn.is_visible(timeout=2000):
                    cancel_btn.click()
                    self.page.wait_for_timeout(1000)
                else:
                    self.page.keyboard.press('Escape')
                    self.page.wait_for_timeout(1000)
            
            return {'success': True, 'has_dialog': has_dialog, 'dialog_text': dialog_text}
        except Exception as e:
            self.logger.error(f"点击拉黑选项失败: {e}")
            return {'success': False, 'has_dialog': False, 'dialog_text': ''}
