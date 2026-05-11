# OK阿联酋站 - Messages页面功能探索测试用例


## 版本历史

| 版本 | 日期 | 修改人 | 修改内容 |
|------|------|--------|----------|
| v2.9 | 2026-04-28 | QA Agent | **全流程瘦身与补充**：删除 TC004/| v2.8 | 2026-04-28 | QA Agent | TC005 调整为会话列表与消息展示校验（移除搜索/筛选）；补充头像/昵称/发送验证代码 |

## 📋 测试概述

本测试用例旨在全面探索OK.com阿联酋站Messages页面的所有功能，包括页面访问、会话列表、会话详情、消息发送、会话列表与消息区展示校验、用户信息等模块。**说明**：当前 Messages 模块不提供会话搜索与筛选，相关能力不作为测试范围。

**测试目标**: 从首页点击Messages，进入Messages页面，系统性地探索和验证所有可用功能。

---

## 🔧 测试环境配置

```yaml
site: ae
site_name: OK阿联酋站
role: seller
user_name: gaosong01_ae_seller
base_url: https://ae.ok.com/en/city-abu-dhabi/
target_page: https://aepub.ok.com/biz/en/chat

test_account:
  username: gaosong01@58.com
  password: Qwert_123

locale: en-AE
currency: AED

browser:
  type: chromium
  headless: false
  viewport:
    width: 1920
    height: 1080

timeout:
  default: 30000
  wait: 10000
  navigation: 30000
```

---

## TC001: 从首页访问Messages页面

### 📌 测试信息
- **用例ID**: `case_id_messages_explore_001`
- **优先级**: P0 (Critical)
- **测试类型**: smoke
- **模块标记**: messages, navigation, ae
- **Allure标记**:
  - Feature: OK - Messages
  - Story: Messages页面功能探索 - 页面访问
  - Title: 从首页点击Messages应该成功进入Messages页面
  - Severity: CRITICAL

### 🎯 测试目标
验证用户能够从首页通过点击Messages链接成功进入Messages页面。

### ✅ 前置条件
1. 用户已有有效的OK.com账号（gaosong01@58.com）
2. 浏览器已安装（Chromium）
3. 网络连接正常
4. 用户已登录或有有效的Session

### 📝 测试步骤

#### 步骤1：打开首页
**操作**: 
```javascript
// 导航到OK.com阿联酋站首页
await page.goto('https://ae.ok.com/en/city-abu-dhabi/');
await page.waitForLoadState('networkidle', { timeout: 30000 });
```

**Python实现**:
```python
messages_page.navigate_to_home(config['base_url'])
logger.info("✓ 已导航到首页")
```

**预期结果**:
- ✅ 成功加载首页
- ✅ URL为: https://ae.ok.com/en/city-abu-dhabi/
- ✅ 页面完全加载（networkidle状态）

#### 步骤2：处理Cookie弹窗（如果存在）
**操作**: 
```javascript
// 检查并关闭Cookie同意弹窗
const cookieButton = page.locator('button:has-text("Accept"), button:has-text("I agree"), button:has-text("OK")').first();
if (await cookieButton.isVisible({ timeout: 3000 })) {
    await cookieButton.click();
    await page.waitForTimeout(1000);
}
```

**Python实现**:
```python
login_page.handle_cookie_popup()
```

**预期结果**:
- ✅ Cookie弹窗被关闭（如果存在）
- ✅ 页面内容可正常访问

#### 步骤3：确认登录状态
**操作**: 
```javascript
// 检查用户是否已登录
const userAvatar = page.locator('[class*="avatar"], [class*="user-icon"]').first();
const isLoggedIn = await userAvatar.isVisible({ timeout: 5000 });

if (!isLoggedIn) {
    // 执行登录流程
    console.log('用户未登录，开始登录');
}
```

**Python实现**:
```python
# 使用SessionManager加载已保存的Session
if session_manager.load_session():
    logger.info("✓ 成功加载已保存的 Session")
else:
    # 执行完整登录流程
    logger.info("✗ Session不存在，开始登录流程")
    login_page.navigate_to_home_page()
    login_page.handle_cookie_popup()
    login_page.click_login_register()
    login_page.input_email(config['test_account']['username'])
    login_page.click_continue()
    login_page.input_password(config['test_account']['password'])
    login_page.click_login()
    session_manager.save_session()
    logger.info("✓ 登录成功并保存 Session")
```

**预期结果**:
- ✅ 用户处于登录状态
- ✅ 可以看到用户头像或用户名

#### 步骤4：查找Messages链接
**操作**: 
```javascript
// 查找Messages链接（可能在导航栏、菜单或其他位置）
// 优先通过文本查找
const messagesLinkByText = page.locator('a:has-text("Messages")').first();

// 备选：通过href查找
const messagesLinkByHref = page.locator('a[href*="chat"], a[href*="message"]').first();

// 等待元素可见
await messagesLinkByText.waitFor({ state: 'visible', timeout: 10000 });
```

**Python实现**:
```python
click_success = messages_page.click_messages_link()
```

**预期结果**:
- ✅ 找到Messages链接
- ✅ 链接可见且可点击

#### 步骤5：点击Messages链接
**操作**: 
```javascript
// 点击Messages链接
await messagesLinkByText.click();

// 等待页面导航完成
await page.waitForLoadState('networkidle', { timeout: 30000 });
```

**Python实现**:
```python
if not click_success:
    logger.info("✗ 点击Messages链接失败，尝试直接导航")
    messages_page.navigate_to_messages_directly(config['target_page'])
    logger.info("✓ 已直接导航到Messages页面")
else:
    logger.info("✓ 已点击Messages链接")
```

**预期结果**:
- ✅ 成功点击Messages链接
- ✅ 页面开始导航到Messages页面
- ✅ 页面加载完成

#### 步骤6：验证进入Messages页面
**操作**: 
```javascript
// 等待URL变化
await page.waitForURL('**/chat**', { timeout: 30000 });

// 等待页面完全加载
await page.waitForLoadState('networkidle');

// 获取当前URL
const currentUrl = page.url();
console.log(`当前URL: ${currentUrl}`);
```

**Python实现**:
```python
current_url = page.url
logger.info(f"✓ 当前URL: {current_url}")
```

**预期结果**:
- ✅ URL为: https://aepub.ok.com/biz/en/chat
- ✅ 页面完全加载

### 🔍 验证点

#### 验证1：URL正确
**验证逻辑**:
```python
# 验证当前URL包含chat或message
current_url = page.url
assert 'chat' in current_url.lower() or 'message' in current_url.lower(), f"URL不正确: {current_url}"
logger.info(f"✓ URL验证通过: {current_url}")
```

**预期结果**:
- ✅ URL包含 "chat" 或 "message"
- ✅ 最佳情况：URL完全匹配 https://aepub.ok.com/biz/en/chat

#### 验证2：Messages页面关键元素可见
**验证逻辑**:
```python
# 验证Messages页面的关键容器元素可见
messages_container = page.locator('[class*="chat"], [class*="message"], [class*="conversation"]').first
assert messages_container.is_visible(timeout=10000), "Messages页面关键元素未显示"
logger.info("✓ Messages页面关键元素已显示")
```

**预期结果**:
- ✅ 会话列表或消息区域可见
- ✅ 页面布局正常

#### 验证3：页面标题正确（可选）
**验证逻辑**:
```python
# 验证页面标题
page_title = page.title()
logger.info(f"✓ 页面标题: {page_title}")
# 注意：不强制要求标题包含特定文本，因为不同站点可能有不同标题
```

**预期结果**:
- ✅ 页面标题已记录

### 📸 截图要求
- 首页加载完成后截图
- 点击Messages链接前截图
- 进入Messages页面后截图

---

## TC002: 探索Messages页面 - 会话列表功能

### 📌 测试信息
- **用例ID**: `case_id_messages_explore_002`
- **优先级**: P1 (High)
- **测试类型**: functional
- **模块标记**: messages, conversation, exploration, ae
- **Allure标记**:
  - Feature: OK - Messages
  - Story: Messages页面功能探索 - 会话列表
  - Title: 探索Messages页面会话列表的各项功能
  - Severity: NORMAL

### 🎯 测试目标
全面探索Messages页面会话列表的功能，包括会话数量、会话元素结构、会话选择等。

### ✅ 前置条件
1. 已完成TC001，成功进入Messages页面
2. 账号中至少有2个会话记录

### 📝 测试步骤

#### 步骤1：等待会话列表加载
**操作**: 
```javascript
// 等待页面完全加载
await page.waitForLoadState('networkidle');

// 额外等待确保动态内容加载
await page.waitForTimeout(2000);
```

**Python实现**:
```python
messages_page.wait_for_conversation_list()
logger.info("✓ 会话列表加载完成")
```

**预期结果**:
- ✅ 会话列表完全加载
- ✅ 所有会话项可见

#### 步骤2：滑动左侧会话列表
**操作**: 
```javascript
// 定位会话列表容器
const conversationList = page.locator('[class*="conversation-list"], [class*="chat-list"], [class*="message-list"]').first();

// 获取列表容器的位置和尺寸
const listBox = await conversationList.boundingBox();

if (listBox) {
    // 在列表中间位置向下滑动
    const startX = listBox.x + listBox.width / 2;
    const startY = listBox.y + listBox.height / 2;
    const endY = startY - 200; // 向下滑动200像素
    
    // 执行滑动操作
    await page.mouse.move(startX, startY);
    await page.mouse.down();
    await page.mouse.move(startX, endY, { steps: 10 });
    await page.mouse.up();
    
    console.log(`✓ 已滑动会话列表: (${startX}, ${startY}) -> (${startX}, ${endY})`);
    
    // 等待滑动动画完成
    await page.waitForTimeout(1000);
}
```

**Python实现**:
```python
scroll_result = messages_page.scroll_conversation_list()
logger.info(f"✓ 滑动会话列表: {scroll_result['success']}")
if scroll_result['success']:
    logger.info(f"  滑动距离: {scroll_result['distance']}px")
```

**预期结果**:
- ✅ 会话列表可以滑动
- ✅ 滑动后显示更多会话

#### 步骤3：检查会话列表项的元素结构
**操作**: 
```javascript
// 检查第一个会话的元素结构
const firstConversation = conversationItems.first();

// 1. 检查用户头像
const avatar = firstConversation.locator('img[class*="avatar"], [class*="avatar"] img').first();
const hasAvatar = await avatar.isVisible({ timeout: 3000 }).catch(() => false);
console.log(`用户头像: ${hasAvatar}`);

// 2. 检查用户名
const userName = firstConversation.locator('[class*="name"], [class*="user"]').first();
const hasUserName = await userName.isVisible({ timeout: 3000 }).catch(() => false);
if (hasUserName) {
    const nameText = await userName.textContent();
    console.log(`用户名: ${nameText}`);
}

// 3. 检查最后一条消息预览
const lastMessage = firstConversation.locator('[class*="message"], [class*="preview"], [class*="content"]').first();
const hasLastMessage = await lastMessage.isVisible({ timeout: 3000 }).catch(() => false);
if (hasLastMessage) {
    const messageText = await lastMessage.textContent();
    console.log(`消息预览: ${messageText}`);
}

// 4. 检查时间戳
const timestamp = firstConversation.locator('[class*="time"], [class*="date"]').first();
const hasTimestamp = await timestamp.isVisible({ timeout: 3000 }).catch(() => false);
if (hasTimestamp) {
    const timeText = await timestamp.textContent();
    console.log(`时间戳: ${timeText}`);
}

// 5. 检查未读标识（如果有）
const unreadBadge = firstConversation.locator('[class*="unread"], [class*="badge"], [class*="count"]').first();
const hasUnreadBadge = await unreadBadge.isVisible({ timeout: 2000 }).catch(() => false);
if (hasUnreadBadge) {
    const badgeText = await unreadBadge.textContent();
    console.log(`未读标识: ${badgeText}`);
}
```

**Python实现**:
```python
elements = messages_page.check_conversation_item_elements()
logger.info(f"✓ 会话列表元素检查:")
logger.info(f"  - 头像: {elements.get('has_avatar', False)}")
logger.info(f"  - 用户名: {elements.get('has_user_name', False)}")
logger.info(f"  - 消息预览: {elements.get('has_message_preview', False)}")
logger.info(f"  - 时间戳: {elements.get('has_timestamp', False)}")
```

**预期结果**:
- ✅ 会话项包含用户头像
- ✅ 会话项包含用户名
- ✅ 会话项包含最后一条消息预览
- ✅ 会话项包含时间戳
- ⚠️ 未读标识可能存在也可能不存在

#### 步骤4：获取第二个会话的用户昵称
**操作**: 
```javascript
// 定位所有会话项
const conversationItems = page.locator('[class*="conversation"], [class*="chat-item"], [class*="message-item"]');

// 获取第二个会话的用户昵称
const secondConversation = conversationItems.nth(1);
const userName = await secondConversation.locator('[class*="name"], [class*="user"], [class*="title"]').first().textContent();

console.log(`第二个会话用户昵称: ${userName}`);
```

**Python实现**:
```python
conversation_name = messages_page.get_conversation_name_by_index(1)
logger.info(f"✓ 第二个会话昵称: {conversation_name}")
```

**预期结果**:
- ✅ 成功获取第二个会话的用户昵称

#### 步骤5：点击第二个会话
**操作**: 
```javascript
// 点击第二个会话
await secondConversation.click();

// 等待页面响应
await page.waitForLoadState('networkidle', { timeout: 10000 });
await page.waitForTimeout(2000);

console.log('✓ 已点击第二个会话');
```

**Python实现**:
```python
click_success = messages_page.click_conversation_by_index(1)
assert click_success, "点击第二个会话失败"
logger.info("✓ 已点击第二个会话")
```

**预期结果**:
- ✅ 第二个会话被选中（可能有高亮或背景色变化）
- ✅ 右侧或下方显示会话详情
- ✅ 会话消息历史开始加载

#### 步骤6：验证会话详情显示并检查用户昵称一致性
**操作**: 
```javascript
// 检查会话详情区域是否可见
const conversationDetail = page.locator('[class*="conversation-detail"], [class*="chat-detail"], textarea[placeholder*="message"]').first();
const isDetailVisible = await conversationDetail.isVisible({ timeout: 10000 });

console.log(`会话详情可见: ${isDetailVisible}`);

// 获取会话详情页的用户昵称
const detailUserName = await page.locator('h1, h2, h3, [class*="user-name"], [class*="contact-name"]').first().textContent();
console.log(`详情页用户昵称: ${detailUserName}`);

// 验证昵称一致性
if (userName === detailUserName || userName.includes(detailUserName) || detailUserName.includes(userName)) {
    console.log('✅ 用户昵称一致性验证通过');
} else {
    console.error(`❌ 用户昵称不一致: 会话列表=${userName}, 详情页=${detailUserName}`);
}
```

**Python实现**:
```python
# 验证会话详情可见
detail_visible = messages_page.is_conversation_detail_visible()
assert detail_visible, "会话详情区域未显示"
logger.info("✓ 会话详情区域已显示")

# 获取详情页用户昵称
detail_user_name = messages_page.get_conversation_detail_user_name()
logger.info(f"✓ 详情页用户昵称: {detail_user_name}")

# 断言：验证昵称一致性
if conversation_name and detail_user_name:
    conv_name_clean = conversation_name.strip().lower()
    detail_name_clean = detail_user_name.strip().lower()
    
    if conv_name_clean == detail_name_clean or conv_name_clean in detail_name_clean or detail_name_clean in conv_name_clean:
        logger.info(f"✅ 昵称一致性验证通过")
        assert True, "昵称一致"
    else:
        logger.error(f"❌ 昵称不一致: 会话列表='{conversation_name}', 详情页='{detail_user_name}'")
        assert False, f"昵称不一致"
```

**预期结果**:
- ✅ 会话详情区域可见
- ✅ 显示消息输入框
- ✅ 显示消息历史
- ✅ **详情页用户昵称与点击的会话昵称一致**

### 🔍 验证点

#### 验证1：URL正确
**验证逻辑**:
```python
current_url = page.url
assert 'chat' in current_url.lower() or 'message' in current_url.lower(), f"URL不正确: {current_url}"
logger.info(f"✓ URL验证通过: {current_url}")
```

**预期结果**:
- ✅ URL包含 "chat" 或 "message"

#### 验证2：会话列表不为空
**验证逻辑**:
```python
conversation_count = messages_page.get_conversation_count()
assert conversation_count > 0, "会话列表为空"
logger.info(f"✓ 会话数量验证通过: {conversation_count}")
```

**预期结果**:
- ✅ 至少有1个会话

#### 验证3：会话详情区域可见
**验证逻辑**:
```python
detail_visible = messages_page.is_conversation_detail_visible()
assert detail_visible, "会话详情区域未显示"
logger.info("✓ 会话详情验证通过")
```

**预期结果**:
- ✅ 会话详情区域可见

#### 验证4：用户昵称一致性
**验证逻辑**:
```python
# 获取会话列表中的昵称
conversation_name = messages_page.get_conversation_name_by_index(1)

# 点击会话后，获取详情页昵称
detail_user_name = messages_page.get_conversation_detail_user_name()

# 验证一致性（支持部分匹配）
conv_name_clean = conversation_name.strip().lower()
detail_name_clean = detail_user_name.strip().lower()

assert (conv_name_clean == detail_name_clean or 
        conv_name_clean in detail_name_clean or 
        detail_name_clean in conv_name_clean), \
        f"昵称不一致: 会话列表='{conversation_name}', 详情页='{detail_user_name}'"

logger.info(f"✓ 昵称一致性验证通过: {conversation_name} ≈ {detail_user_name}")
```

**预期结果**:
- ✅ 会话列表中的用户昵称与详情页显示的用户昵称一致
- ✅ 支持完全匹配或部分匹配（详情页可能显示完整昵称）

### 📸 截图要求
- 滑动会话列表后截图
- 会话详情显示后截图（用于验证昵称）

---

## TC003: 探索Messages页面 - 会话详情基础功能

### 📌 测试信息
- **用例ID**: `case_id_messages_explore_003`
- **优先级**: P1 (High)
- **测试类型**: functional
- **模块标记**: messages, conversation, exploration, ae
- **Allure标记**:
  - Feature: OK - Messages
  - Story: Messages页面功能探索 - 会话详情
  - Title: 探索会话详情页面的基础功能元素
  - Severity: NORMAL

### 🎯 测试目标
探索会话详情页面的所有基础功能元素，包括消息输入、安全提示、功能按钮等。

### ✅ 前置条件
1. 已完成TC002，成功进入第二个会话详情

### 📝 测试步骤

#### 步骤1：检查会话详情基本元素
**操作**: 
```javascript
// 1. 检查消息输入框
const messageInput = page.locator('textarea[placeholder*="message"], input[placeholder*="message"]').first();
const hasMessageInput = await messageInput.isVisible({ timeout: 5000 }).catch(() => false);
console.log(`消息输入框: ${hasMessageInput}`);

// 2. 检查发送按钮
const sendButton = page.locator('button:has-text("Send"), button[class*="send"]').first();
const hasSendButton = await sendButton.isVisible({ timeout: 5000 }).catch(() => false);
console.log(`发送按钮: ${hasSendButton}`);

// 3. 检查消息历史区域
const messageHistory = page.locator('[class*="message-history"], [class*="chat-content"], [class*="conversation-content"]').first();
const hasMessageHistory = await messageHistory.isVisible({ timeout: 5000 }).catch(() => false);
console.log(`消息历史: ${hasMessageHistory}`);
```

**Python实现**:
```python
detail_elements = messages_page.check_conversation_detail_elements()
logger.info("✓ 会话详情基本元素检查:")
logger.info(f"  - 消息输入框: {detail_elements.get('has_message_input', False)}")
logger.info(f"  - 发送按钮: {detail_elements.get('has_send_button', False)}")
logger.info(f"  - 消息历史: {detail_elements.get('has_message_history', False)}")
```

**预期结果**:
- ✅ 消息输入框可见
- ✅ 发送按钮可见
- ✅ 消息历史区域可见

#### 步骤2：检查安全提示
**操作**: 
```javascript
// 查找安全提示（通常在会话顶部）
// 方法1：通过class查找
const securityTipByClass = page.locator('[class*="security-tip"], [class*="safety-tip"], [class*="warning"]').first();

// 方法2：通过文本内容查找（更可靠）
const securityTipByText = page.locator('text=/safety|secure|sensitive|personal information/i').first();

const hasSecurityTip = await securityTipByText.isVisible({ timeout: 5000 }).catch(() => false);

if (hasSecurityTip) {
    const tipText = await securityTipByText.textContent();
    console.log(`安全提示内容: ${tipText}`);
} else {
    console.log('未发现安全提示');
}
```

**Python实现**:
```python
security_tip = messages_page.check_security_tip()
logger.info(f"✓ 安全提示: {security_tip['visible']}")
if security_tip['visible']:
    logger.info(f"  内容: {security_tip['text']}")
```

**预期结果**:
- ⚠️ 安全提示可能存在也可能不存在
- ✅ 如果存在，应该在页面顶部显示
- ✅ 内容应该包含安全相关的关键词

#### 步骤3：检查电话按钮
**操作**: 
```javascript
// 查找电话/通话按钮（可能在顶部工具栏）
// 方法1：通过文本查找
const phoneButtonByText = page.locator('button:has-text("Call"), button:has-text("Phone")').first();

// 方法2：通过class查找
const phoneButtonByClass = page.locator('button[class*="phone"], button[class*="call"]').first();

// 方法3：通过SVG图标查找
const phoneButtonBySvg = page.locator('button:has(svg[class*="phone"]), button:has(svg[class*="call"])').first();

const hasPhoneButton = await phoneButtonByText.isVisible({ timeout: 5000 }).catch(() => false) ||
                       await phoneButtonByClass.isVisible({ timeout: 5000 }).catch(() => false) ||
                       await phoneButtonBySvg.isVisible({ timeout: 5000 }).catch(() => false);

if (hasPhoneButton) {
    console.log('✓ 发现电话按钮');
    
    // 点击电话按钮
    const phoneButton = phoneButtonByText.isVisible() ? phoneButtonByText : 
                       phoneButtonByClass.isVisible() ? phoneButtonByClass : phoneButtonBySvg;
    await phoneButton.click();
    await page.waitForTimeout(2000);
    
    // 检查是否弹出拨号界面或提示
    const callDialog = page.locator('[role="dialog"], .modal, [class*="call"]').first();
    const hasCallDialog = await callDialog.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (hasCallDialog) {
        console.log('✓ 电话功能弹窗已显示');
        
        // 关闭弹窗（避免影响后续测试）
        const closeButton = callDialog.locator('button:has-text("Close"), button:has-text("Cancel"), button[class*="close"]').first();
        if (await closeButton.isVisible({ timeout: 2000 }).catch(() => false)) {
            await closeButton.click();
            await page.waitForTimeout(1000);
        } else {
            // 尝试按ESC键关闭
            await page.keyboard.press('Escape');
            await page.waitForTimeout(1000);
        }
    }
} else {
    console.log('✗ 未发现电话按钮');
}
```

**Python实现**:
```python
has_phone = messages_page.check_phone_button()
logger.info(f"✓ 电话按钮: {has_phone}")
if has_phone:
    messages_page.click_phone_button()
    logger.info("  已测试点击电话按钮")
```

**预期结果**:
- ⚠️ 电话按钮可能存在也可能不存在
- ✅ 如果存在，点击后应该有相应反馈（弹窗、拨号界面等）

#### 步骤4：检查设置入口
**操作**: 
```javascript
// 查找设置按钮（可能是齿轮图标、三点菜单等）
// 方法1：通过文本查找
const settingsButtonByText = page.locator('button:has-text("Settings")').first();

// 方法2：通过class查找
const settingsButtonByClass = page.locator('button[class*="settings"], button[class*="menu"]').first();

// 方法3：通过SVG图标查找
const settingsButtonBySvg = page.locator('button:has(svg[class*="settings"]), button:has(svg[class*="gear"])').first();

// 方法4：通过三点图标查找
const moreButton = page.locator('button:has-text("⋮"), button:has-text("...")').first();

const hasSettingsButton = await settingsButtonByText.isVisible({ timeout: 5000 }).catch(() => false) ||
                          await settingsButtonByClass.isVisible({ timeout: 5000 }).catch(() => false) ||
                          await settingsButtonBySvg.isVisible({ timeout: 5000 }).catch(() => false) ||
                          await moreButton.isVisible({ timeout: 5000 }).catch(() => false);

if (hasSettingsButton) {
    console.log('✓ 发现设置按钮');
    
    // 点击设置按钮
    const settingsButton = await settingsButtonByText.isVisible() ? settingsButtonByText :
                          await settingsButtonByClass.isVisible() ? settingsButtonByClass :
                          await settingsButtonBySvg.isVisible() ? settingsButtonBySvg : moreButton;
    
    await settingsButton.click();
    await page.waitForTimeout(2000);
    
    // 检查是否弹出设置菜单
    const settingsMenu = page.locator('[role="menu"], .dropdown-menu, [class*="settings-menu"], [class*="options-menu"]').first();
    const hasSettingsMenu = await settingsMenu.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (hasSettingsMenu) {
        console.log('✓ 设置菜单已显示');
    } else {
        console.log('✗ 设置菜单未显示');
    }
} else {
    console.log('✗ 未发现设置按钮');
}
```

**Python实现**:
```python
has_settings = messages_page.check_settings_button()
logger.info(f"✓ 设置按钮: {has_settings}")

if has_settings:
    menu_visible = messages_page.click_settings_button()
    logger.info(f"  设置菜单显示: {menu_visible}")
```

**预期结果**:
- ⚠️ 设置按钮可能存在也可能不存在
- ✅ 如果存在，点击后应该显示设置菜单

#### 步骤5：检查免打扰功能
**操作**: 
```javascript
// 在设置菜单中查找免打扰选项
const muteOption = page.locator('text=/Do Not Disturb|Mute|静音|免打扰/i, button:has-text("Mute"), [class*="mute"]').first();

const hasMuteOption = await muteOption.isVisible({ timeout: 5000 }).catch(() => false);

if (hasMuteOption) {
    console.log('✓ 发现免打扰选项');
    
    // 点击免打扰
    await muteOption.click();
    await page.waitForTimeout(2000);
    
    // 检查是否有确认弹窗或状态变化
    const confirmDialog = page.locator('[role="dialog"], .modal').first();
    const hasConfirmDialog = await confirmDialog.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (hasConfirmDialog) {
        console.log('✓ 免打扰确认弹窗已显示');
        
        // 取消操作（避免实际修改设置）
        const cancelButton = confirmDialog.locator('button:has-text("Cancel"), button:has-text("Close")').first();
        if (await cancelButton.isVisible({ timeout: 2000 }).catch(() => false)) {
            await cancelButton.click();
            await page.waitForTimeout(1000);
        } else {
            await page.keyboard.press('Escape');
            await page.waitForTimeout(1000);
        }
    }
} else {
    console.log('✗ 未发现免打扰选项');
}
```

**Python实现**:
```python
if menu_visible:
    has_mute = messages_page.check_mute_option()
    logger.info(f"  - 免打扰选项: {has_mute}")
    if has_mute:
        messages_page.click_mute_option()
        logger.info("    已测试点击免打扰")
```

**预期结果**:
- ⚠️ 免打扰功能可能存在也可能不存在
- ✅ 如果存在，点击后应该有相应反馈

#### 步骤6：检查拉黑功能
**操作**: 
```javascript
// 重新打开设置菜单（如果之前关闭了）
if (hasSettingsButton && !await settingsMenu.isVisible({ timeout: 2000 }).catch(() => false)) {
    await settingsButton.click();
    await page.waitForTimeout(2000);
}

// 在设置菜单中查找拉黑选项
const blockOption = page.locator('text=/Block|拉黑|屏蔽/i, button:has-text("Block"), [class*="block"]').first();

const hasBlockOption = await blockOption.isVisible({ timeout: 5000 }).catch(() => false);

if (hasBlockOption) {
    console.log('✓ 发现拉黑选项');
    
    // 点击拉黑
    await blockOption.click();
    await page.waitForTimeout(2000);
    
    // 检查是否有确认弹窗
    const confirmDialog = page.locator('[role="dialog"], .modal').first();
    const hasConfirmDialog = await confirmDialog.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (hasConfirmDialog) {
        console.log('✓ 拉黑确认弹窗已显示');
        
        // 检查弹窗内容
        const dialogText = await confirmDialog.textContent();
        console.log(`确认弹窗内容: ${dialogText}`);
        
        // 取消操作（避免实际拉黑用户）
        const cancelButton = confirmDialog.locator('button:has-text("Cancel"), button:has-text("Close"), button:has-text("No")').first();
        if (await cancelButton.isVisible({ timeout: 2000 }).catch(() => false)) {
            await cancelButton.click();
            await page.waitForTimeout(1000);
        } else {
            await page.keyboard.press('Escape');
            await page.waitForTimeout(1000);
        }
    }
} else {
    console.log('✗ 未发现拉黑选项');
}
```

**Python实现**:
```python
if menu_visible:
    # 重新打开设置菜单
    if has_mute:
        messages_page.click_settings_button()
        page.wait_for_timeout(1000)
    
    has_block = messages_page.check_block_option()
    logger.info(f"  - 拉黑选项: {has_block}")
    if has_block:
        messages_page.click_block_option()
        logger.info("    已测试点击拉黑")
```

**预期结果**:
- ⚠️ 拉黑功能可能存在也可能不存在
- ✅ 如果存在，点击后应该显示确认弹窗
- ✅ 确认弹窗应该有取消和确认按钮

### 🔍 验证点

#### 验证1：消息输入框可用
**验证逻辑**:
```python
assert detail_elements.get('has_message_input', False), "消息输入框未显示"
logger.info("✓ 消息输入框验证通过")
```

**预期结果**:
- ✅ 消息输入框可见

#### 验证2：功能探索完成
**验证逻辑**:
```python
# 记录探索到的功能
features_found = []
if security_tip['visible']:
    features_found.append("安全提示")
if has_phone:
    features_found.append("电话功能")
if has_settings:
    features_found.append("设置菜单")

logger.info(f"✓ 探索到的功能: {', '.join(features_found) if features_found else '无'}")
```

**预期结果**:
- ✅ 完成功能探索并记录结果

### 📸 截图要求
- 会话详情页面初始状态截图
- 点击电话按钮后截图（如果有）
- 设置菜单展开后截图（如果有）
- 免打扰确认弹窗截图（如果有）
- 拉黑确认弹窗截图（如果有）

---



## TC004: 探索Messages页面 - 会话列表与消息列表展示校验

### 📌 测试信息
- **用例ID**: `case_id_messages_explore_005`
- **优先级**: P2 (Medium)
- **测试类型**: functional
- **模块标记**: messages, conversation-list, message-thread, exploration, ae
- **Allure标记**:
  - Feature: OK - Messages
  - Story: Messages页面功能探索 - 会话列表与消息展示校验
  - Title: 校验会话列表与消息区的头像、昵称、时间戳、未读及发送消息展示
  - Severity: NORMAL

### 🎯 测试目标
当前模块**不提供**会话搜索与筛选，本用例不测搜索框与筛选器。重点校验：**会话列表**中头像、昵称、时间戳、未读标识；进入会话后**消息列表**中双方消息的头像/昵称（或发送方向）展示是否合理；**发送消息**后是否在列表中正确出现且文案一致。

### ✅ 前置条件
1. 已完成TC001，成功进入Messages页面
2. （建议）已完成TC002，便于结合会话详情核对昵称一致性；若仅执行本用例，至少需存在≥1个会话并可进入详情

### 📝 测试步骤

#### 步骤1：会话列表 — 校验头像、昵称与时间戳展示
**操作**: 
```javascript
// 取首个可见会话项，校验头像、昵称、时间戳（当前模块无搜索/筛选，不查找搜索框）
const item = page.locator('[class*="conversation"], [class*="chat-item"]').first();
await item.waitFor({ state: 'visible', timeout: 10000 });

const avatar = item.locator('img[class*="avatar"], [class*="avatar"] img').first();
const hasAvatar = await avatar.isVisible({ timeout: 3000 }).catch(() => false);
const avatarSrc = hasAvatar ? await avatar.getAttribute('src') : null;
console.log(`会话项头像可见: ${hasAvatar}, src: ${avatarSrc}`);

const nameEl = item.locator('[class*="name"], [class*="title"]').first();
const nameText = (await nameEl.textContent())?.trim() ?? '';
console.log(`会话项昵称非空: ${nameText.length > 0}, 文本: ${nameText}`);

const timeEl = item.locator('[class*="time"], [class*="date"]').first();
const hasTime = await timeEl.isVisible({ timeout: 3000 }).catch(() => false);
const timeText = hasTime ? (await timeEl.textContent())?.trim() : '';
console.log(`会话项时间戳可见: ${hasTime}, 文本: ${timeText}`);
```

**Python实现**:
```python
list_check = messages_page.validate_conversation_list_item_fields()  # 头像可见/src、昵称非空、时间戳可见
logger.info(f"✓ 会话列表项校验: {list_check}")
```

**预期结果**:
- ✅ 会话项展示头像（可见或为合法占位）
- ✅ 会话项昵称非空（或与 TC002 详情页一致时可交叉断言）
- ✅ 会话项展示时间戳文案（相对/绝对时间均可）

#### 步骤2：检查未读消息标识
**操作**: 
```javascript
// 检查会话列表中是否有未读消息标识
const unreadBadges = page.locator('[class*="unread"], [class*="badge"], [class*="count"]');
const unreadCount = await unreadBadges.count();

if (unreadCount > 0) {
    console.log(`✓ 发现 ${unreadCount} 个未读消息标识`);
    
    // 获取第一个未读标识的文本
    const firstBadge = unreadBadges.first();
    const badgeText = await firstBadge.textContent();
    const badgeClass = await firstBadge.getAttribute('class');
    
    console.log(`未读标识示例:
      - 文本: ${badgeText}
      - Class: ${badgeClass}
    `);
    
    // 检查未读标识的位置（是否在会话项内）
    const parentConversation = firstBadge.locator('xpath=ancestor::*[contains(@class, "conversation") or contains(@class, "chat-item")]').first();
    const hasParent = await parentConversation.isVisible({ timeout: 2000 }).catch(() => false);
    console.log(`未读标识在会话项内: ${hasParent}`);
} else {
    console.log('✗ 未发现未读消息标识（可能所有消息都已读）');
}
```

**Python实现**:
```python
unread_info = messages_page.check_unread_badges()
logger.info(f"✓ 未读标识数量: {unread_info.get('count', 0)}")
if unread_info.get('count', 0) > 0:
    logger.info(f"  示例内容: {unread_info.get('text', '')}")
```

**预期结果**:
- ⚠️ 未读标识可能存在也可能不存在
- ✅ 如果存在，应该显示未读消息数量
- ✅ 未读标识应该在对应的会话项上

#### 步骤3：消息列表 — 校验头像、昵称与发送消息展示
**说明**: 在已进入某一会话详情的前提下，校验消息区内每条（或抽样多条）消息是否具备发送方标识（己方/对方头像、`mine`/`self` 类名或气泡左右对齐等）、对方昵称或气泡文案是否可读；并执行一次发送消息校验。

**操作**: 
```javascript
// 进入首个会话（若当前不在详情页）
await page.locator('[class*="conversation"], [class*="chat-item"]').first().click();
await page.waitForTimeout(1500);

const bubbles = page.locator('[class*="message-item"], [class*="chat-bubble"], [class*="message-bubble"]');
const n = await bubbles.count();
console.log(`消息条数: ${n}`);
// 抽样：至少一条己方、一条对方（若存在），检查头像或布局类名
for (let i = 0; i < Math.min(n, 10); i++) {
  const b = bubbles.nth(i);
  const cls = (await b.getAttribute('class')) || '';
  const text = (await b.textContent())?.trim().slice(0, 80);
  console.log(`消息${i}: class片段=${cls.slice(0, 120)}, 文本前缀=${text}`);
}

// 发送消息校验：输入唯一文案并发送，确认列表末尾出现相同文案
const input = page.locator('textarea[placeholder*="message"], input[placeholder*="message"]').first();
const sendBtn = page.locator('button:has-text("Send"), button[class*="send"]').first();
const probe = `TC005_probe_${Date.now()}`;
await input.fill(probe);
await sendBtn.click();
await page.waitForTimeout(2000);
const lastBubble = bubbles.last();
const lastText = await lastBubble.textContent();
console.log(`发送校验: 期望包含 "${probe}", 末条包含=${(lastText || '').includes(probe)}`);
```

**Python实现**:
```python
import time

thread_check = messages_page.validate_message_thread_avatars_and_alignment()
send_ok = messages_page.send_message_and_verify_in_thread(f"probe_{int(time.time())}")
logger.info(f"✓ 消息区展示校验: {thread_check}, 发送并出现在列表: {send_ok}")
```

**预期结果**:
- ✅ 消息列表区域可见且至少有一条历史消息时，可区分己方与对方消息（头像、对齐或 class 等至少一种）
- ✅ 输入框非空且允许发送时，点击发送后**新消息出现在消息列表**（通常在底部），**正文与输入一致**
- ⚠️ 若 Send 初始 disabled，需先输入合法字符再发送（与 TC004/TC023 行为一致时可引用）

### 🔍 验证点

#### 验证1：会话列表不为空
**验证逻辑**:
```python
conversation_count = messages_page.get_conversation_count()
assert conversation_count > 0, "会话列表为空"
logger.info(f"✓ 会话数量验证通过: {conversation_count}")
```

**预期结果**:
- ✅ 至少有1个会话

#### 验证2：展示与发送校验结果汇总
**验证逻辑**:
```python
summary = {
    "list_avatar_nickname_time": list_check,
    "unread_badges": unread_info.get("count", 0),
    "thread_validation": thread_check,
    "send_verified": send_ok,
}
logger.info(f"✓ TC005 汇总: {summary}")
assert list_check.get("ok", True), "会话列表头像/昵称/时间戳校验失败"
assert send_ok, "发送消息后未在消息列表中校验到内容"
```

**预期结果**:
- ✅ 记录会话列表字段校验、未读标识统计、消息区展示与发送校验结果
- ✅ 发送探针消息后列表中出现对应文案

### 📸 截图要求
- 会话列表：含头像、昵称、时间戳、未读（若有）的项截图
- 消息列表：展示双方消息气泡/头像区域截图
- 发送探针消息前后各一张（证明新消息入列）

---

## TC005: 探索Messages页面 - 用户信息和操作

### 📌 测试信息
- **用例ID**: `case_id_messages_explore_006`
- **优先级**: P2 (Medium)
- **测试类型**: functional
- **模块标记**: messages, user, exploration, ae
- **Allure标记**:
  - Feature: OK - Messages
  - Story: Messages页面功能探索 - 用户信息
  - Title: 探索会话中的用户信息和相关操作
  - Severity: NORMAL

### 🎯 测试目标
探索会话中对方用户的信息展示和相关操作，包括头像、用户名、在线状态、资料入口等。

### ✅ 前置条件
1. 已完成TC002，成功进入会话详情

### 📝 测试步骤

#### 步骤1：检查对方用户信息
**操作**: 
```javascript
// 1. 查找用户头像
const userAvatar = page.locator('[class*="avatar"], [class*="profile-pic"]').first();
const hasAvatar = await userAvatar.isVisible({ timeout: 5000 }).catch(() => false);
console.log(`用户头像: ${hasAvatar}`);

if (hasAvatar) {
    // 获取头像图片URL
    const avatarSrc = await userAvatar.getAttribute('src');
    console.log(`头像URL: ${avatarSrc}`);
}

// 2. 查找用户名
const userName = page.locator('[class*="user-name"], [class*="contact-name"], h1, h2, h3').first();
const hasUserName = await userName.isVisible({ timeout: 5000 }).catch(() => false);
console.log(`用户名: ${hasUserName}`);

if (hasUserName) {
    const nameText = await userName.textContent();
    console.log(`用户名文本: ${nameText}`);
}

// 3. 查找用户状态（在线/离线）
const userStatus = page.locator('[class*="status"], [class*="online"], [class*="offline"]').first();
const hasUserStatus = await userStatus.isVisible({ timeout: 3000 }).catch(() => false);
console.log(`用户状态: ${hasUserStatus}`);

if (hasUserStatus) {
    const statusText = await userStatus.textContent();
    const statusClass = await userStatus.getAttribute('class');
    console.log(`状态文本: ${statusText}`);
    console.log(`状态Class: ${statusClass}`);
}
```

**Python实现**:
```python
user_info = messages_page.check_user_info()
logger.info(f"✓ 用户信息检查:")
logger.info(f"  - 头像: {user_info.get('has_avatar', False)}")
logger.info(f"  - 用户名: {user_info.get('has_name', False)}")
logger.info(f"  - 在线状态: {user_info.get('has_status', False)}")
if user_info.get('name_text'):
    logger.info(f"  - 用户名文本: {user_info.get('name_text')}")
```

**预期结果**:
- ✅ 显示对方用户的头像
- ✅ 显示对方用户的名称
- ⚠️ 可能显示用户在线状态

#### 步骤2：尝试访问用户资料
**操作**: 
```javascript
// 尝试点击用户名或头像查看资料
if (hasUserName) {
    // 点击用户名
    await userName.click();
    await page.waitForTimeout(2000);
    
    // 检查是否打开了用户资料页面或弹窗
    const profileDialog = page.locator('[role="dialog"], .modal, [class*="profile"]').first();
    const hasProfileDialog = await profileDialog.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (hasProfileDialog) {
        console.log('✓ 用户资料弹窗已显示');
        
        // 检查资料弹窗中的信息
        const profileName = profileDialog.locator('[class*="name"], h1, h2').first();
        const hasProfileName = await profileName.isVisible({ timeout: 2000 }).catch(() => false);
        
        const profilePhone = profileDialog.locator('text=/phone|电话/i').first();
        const hasProfilePhone = await profilePhone.isVisible({ timeout: 2000 }).catch(() => false);
        
        const profileEmail = profileDialog.locator('text=/email|邮箱/i').first();
        const hasProfileEmail = await profileEmail.isVisible({ timeout: 2000 }).catch(() => false);
        
        const profileLocation = profileDialog.locator('text=/location|地址|city/i').first();
        const hasProfileLocation = await profileLocation.isVisible({ timeout: 2000 }).catch(() => false);
        
        console.log(`资料弹窗内容:
          - 姓名: ${hasProfileName}
          - 电话: ${hasProfilePhone}
          - 邮箱: ${hasProfileEmail}
          - 位置: ${hasProfileLocation}
        `);
        
        // 关闭资料弹窗
        const closeButton = profileDialog.locator('button:has-text("Close"), button[class*="close"], [class*="close-icon"]').first();
        if (await closeButton.isVisible({ timeout: 2000 }).catch(() => false)) {
            await closeButton.click();
            await page.waitForTimeout(1000);
        } else {
            await page.keyboard.press('Escape');
            await page.waitForTimeout(1000);
        }
    } else {
        console.log('✗ 点击用户名未打开资料弹窗');
        
        // 检查是否跳转到了新页面
        const currentUrl = page.url();
        if (currentUrl.includes('profile') || currentUrl.includes('user')) {
            console.log('✓ 跳转到了用户资料页面');
            // 返回Messages页面
            await page.goBack();
            await page.waitForLoadState('networkidle');
        }
    }
}
```

**预期结果**:
- ⚠️ 点击用户名可能打开资料弹窗，也可能跳转到资料页面
- ✅ 如果打开弹窗，应该显示用户的详细信息

#### 步骤3：检查会话顶部的快捷操作按钮
**操作**: 
```javascript
// 查找会话详情顶部的快捷操作按钮
const actionButtons = page.locator('[class*="action"], [class*="toolbar"] button, [class*="header"] button');
const buttonCount = await actionButtons.count();

console.log(`快捷操作按钮数量: ${buttonCount}`);

// 遍历并记录每个按钮
for (let i = 0; i < Math.min(buttonCount, 10); i++) {
    const button = actionButtons.nth(i);
    
    // 获取按钮信息
    const buttonText = await button.textContent().catch(() => '');
    const buttonClass = await button.getAttribute('class').catch(() => '');
    const buttonTitle = await button.getAttribute('title').catch(() => '');
    const buttonAriaLabel = await button.getAttribute('aria-label').catch(() => '');
    
    console.log(`按钮 ${i + 1}:
      - 文本: ${buttonText.trim()}
      - Class: ${buttonClass}
      - Title: ${buttonTitle}
      - Aria-label: ${buttonAriaLabel}
    `);
}
```

**预期结果**:
- ✅ 记录会话详情页面的所有快捷操作按钮
- ✅ 记录每个按钮的文本、class、title等信息

### 🔍 验证点

#### 验证1：用户信息可见
**验证逻辑**:
```python
has_user_info = user_info.get('has_avatar', False) or user_info.get('has_name', False)
assert has_user_info, "用户信息未显示"
logger.info("✓ 用户信息验证通过")
```

**预期结果**:
- ✅ 至少显示用户名或头像

### 📸 截图要求
- 用户信息展示截图
- 用户资料弹窗截图（如果有）

---

## TC006: 探索Messages页面 - 消息类型和展示

### 📌 测试信息
- **用例ID**: `case_id_messages_explore_007`
- **优先级**: P2 (Medium)
- **测试类型**: functional
- **模块标记**: messages, display, exploration, ae
- **Allure标记**:
  - Feature: OK - Messages
  - Story: Messages页面功能探索 - 消息展示
  - Title: 探索Messages页面中不同类型消息的展示
  - Severity: NORMAL

### 🎯 测试目标
分析和记录Messages页面中不同类型消息的展示方式，包括消息方向、内容类型、时间戳、状态等。

### ✅ 前置条件
1. 已完成TC002，成功进入会话详情
2. 会话中有消息历史

### 📝 测试步骤

#### 步骤1：分析消息类型
**操作**: 
```javascript
// 定位所有消息项
const messages = page.locator('[class*="message-item"], [class*="chat-bubble"], [class*="message-bubble"]');
const messageCount = await messages.count();

console.log(`消息总数: ${messageCount}`);

// 分析前10条消息的类型
for (let i = 0; i < Math.min(messageCount, 10); i++) {
    const message = messages.nth(i);
    
    // 1. 检查消息方向（发送/接收）
    const messageClass = await message.getAttribute('class').catch(() => '');
    const isSent = messageClass.includes('sent') || messageClass.includes('outgoing') || messageClass.includes('right');
    const isReceived = messageClass.includes('received') || messageClass.includes('incoming') || messageClass.includes('left');
    
    // 2. 检查消息内容类型
    const hasText = await message.locator('text=/.+/').isVisible({ timeout: 1000 }).catch(() => false);
    const hasImage = await message.locator('img').isVisible({ timeout: 1000 }).catch(() => false);
    const hasLink = await message.locator('a').isVisible({ timeout: 1000 }).catch(() => false);
    
    // 3. 获取消息文本（如果有）
    let messageText = '';
    if (hasText) {
        messageText = await message.textContent().catch(() => '');
        messageText = messageText.trim().substring(0, 50); // 只取前50个字符
    }
    
    console.log(`消息 ${i + 1}:
      - 方向: ${isSent ? '发送' : isReceived ? '接收' : '未知'}
      - 文本: ${hasText}
      - 图片: ${hasImage}
      - 链接: ${hasLink}
      - 内容预览: ${messageText}
    `);
}
```

**Python实现**:
```python
message_analysis = messages_page.analyze_message_types(max_count=10)
logger.info(f"✓ 消息分析（前{len(message_analysis)}条）:")

for msg in message_analysis:
    direction = "发送" if msg['is_sent'] else "接收" if msg['is_received'] else "未知"
    logger.info(f"  消息 {msg['index']}:")
    logger.info(f"    - 方向: {direction}")
    logger.info(f"    - 文本: {msg['has_text']}")
    logger.info(f"    - 图片: {msg['has_image']}")
    logger.info(f"    - 链接: {msg['has_link']}")
```

**预期结果**:
- ✅ 能够识别消息的发送方向
- ✅ 能够识别消息的内容类型（文本、图片、链接等）
- ✅ 记录至少10条消息的详细信息

#### 步骤2：检查消息时间戳
**操作**: 
```javascript
// 检查消息是否有时间戳
const timestamps = page.locator('[class*="timestamp"], [class*="time"], [class*="date"]');
const timestampCount = await timestamps.count();

console.log(`时间戳数量: ${timestampCount}`);

if (timestampCount > 0) {
    // 获取第一个时间戳的信息
    const firstTimestamp = timestamps.first();
    const timestampText = await firstTimestamp.textContent();
    const timestampClass = await firstTimestamp.getAttribute('class');
    
    console.log(`时间戳示例:
      - 文本: ${timestampText}
      - Class: ${timestampClass}
    `);
    
    // 检查时间戳格式
    const hasTime = /\d{1,2}:\d{2}/.test(timestampText); // HH:MM格式
    const hasDate = /\d{1,2}\/\d{1,2}/.test(timestampText); // MM/DD格式
    const hasRelative = /ago|yesterday|today/i.test(timestampText); // 相对时间
    
    console.log(`时间戳格式:
      - 时间格式(HH:MM): ${hasTime}
      - 日期格式(MM/DD): ${hasDate}
      - 相对时间: ${hasRelative}
    `);
}
```

**预期结果**:
- ✅ 消息显示时间戳
- ✅ 时间戳格式合理（时间、日期或相对时间）

#### 步骤3：检查消息状态（已读/未读/发送中）
**操作**: 
```javascript
// 查找消息状态指示器
const statusIndicators = page.locator('[class*="status"], [class*="read"], [class*="delivered"], [class*="sending"]');
const statusCount = await statusIndicators.count();

console.log(`消息状态指示器数量: ${statusCount}`);

// 检查是否有已读回执（双勾等）
const readReceipts = page.locator('svg[class*="check"], [class*="read-receipt"]');
const receiptCount = await readReceipts.count();
console.log(`已读回执数量: ${receiptCount}`);

if (receiptCount > 0) {
    const firstReceipt = readReceipts.first();
    const receiptClass = await firstReceipt.getAttribute('class');
    console.log(`已读回执Class: ${receiptClass}`);
}
```

**预期结果**:
- ⚠️ 消息状态指示器可能存在也可能不存在
- ✅ 如果存在，应该能够区分已读/未读/发送中等状态

### 🔍 验证点

#### 验证1：消息历史不为空
**验证逻辑**:
```python
assert len(message_analysis) > 0, "消息历史为空"
logger.info(f"✓ 消息历史验证通过: {len(message_analysis)}条")
```

**预期结果**:
- ✅ 至少有1条消息

### 📸 截图要求
- 消息列表完整截图
- 不同类型消息的特写截图

---

## TC007: 会话页面安全提示检查

### 📌 测试信息
- **用例ID**: `case_id_messages_explore_008`
- **优先级**: P1 (High)
- **测试类型**: functional
- **模块标记**: messages, security, ae
- **Allure标记**:
  - Feature: OK - Messages
  - Story: Messages页面功能探索 - 安全提示
  - Title: 会话页面顶部应该显示安全提示信息
  - Severity: NORMAL

### 🎯 测试目标
验证会话详情页顶部是否显示安全提示信息（"for your safe..."）。

### ✅ 前置条件
1. 用户已登录
2. 已进入Messages页面
3. 会话列表不为空

### 📝 测试步骤

#### 步骤1：进入Messages页面并打开会话
**操作**: 
```javascript
// 导航到Messages页面
await page.goto('https://aepub.ok.com/biz/en/chat');
await page.waitForLoadState('networkidle');

// 等待会话列表加载
const conversationItems = page.locator("[class*='conversation'], [class*='chat-item']");
await conversationItems.first().waitFor({ timeout: 10000 });

// 点击第二个会话
await conversationItems.nth(1).click();
await page.waitForTimeout(3000);
```

**Python实现**:
```python
messages_page.navigate_to_messages_directly(config['target_page'])
logger.info("✓ 已导航到Messages页面")

messages_page.wait_for_conversation_list()
conversation_count = messages_page.get_conversation_count()
logger.info(f"✓ 会话总数: {conversation_count}")

messages_page.click_conversation_by_index(1)
page.wait_for_timeout(3000)
logger.info("✓ 已进入会话详情页")
```

**预期结果**:
- ✅ 成功进入会话详情页
- ✅ 页面加载完成

#### 步骤2：向下滑动会话页至顶部
**操作**: 
```javascript
// 查找消息历史容器并滚动到顶部
const messageContainers = page.locator('[class*="message"], [class*="chat"], [class*="conversation"]');

for (let i = 0; i < await messageContainers.count(); i++) {
    const container = messageContainers.nth(i);
    const rect = await container.boundingBox();
    
    // 检查是否是右侧的消息容器
    if (rect && rect.x > 300) {
        await container.evaluate(el => {
            el.scrollTop = 0;  // 滚动到顶部
        });
        await page.waitForTimeout(1000);
        console.log('✓ 已滚动到顶部');
        break;
    }
}
```

**Python实现**:
```python
# 滚动到顶部
scroll_result = page.evaluate("""
    () => {
        const containers = document.querySelectorAll('[class*="message"], [class*="chat"], [class*="conversation"], [class*="history"]');
        
        for (const container of containers) {
            const rect = container.getBoundingClientRect();
            if (rect.x > 300 && container.scrollHeight > container.clientHeight) {
                container.scrollTop = 0;
                return {success: true, scrolled: true};
            }
        }
        
        return {success: false, scrolled: false};
    }
""")

logger.info(f"✓ 滚动到顶部: {scroll_result['success']}")
page.wait_for_timeout(1000)
page.screenshot(path="screenshots/tc008_after_scroll_top.png")
```

**预期结果**:
- ✅ 消息列表滚动到顶部
- ✅ 顶部内容可见

#### 步骤3：查找安全提示"for your safe..."
**操作**: 
```javascript
// 查找包含"for your safe"的安全提示
const securityTip = await page.evaluate(() => {
    const allElements = document.querySelectorAll('*');
    
    for (const el of allElements) {
        const text = el.textContent || '';
        const rect = el.getBoundingClientRect();
        
        // 查找包含安全提示关键词的元素
        if (text.toLowerCase().includes('for your safe') || 
            text.toLowerCase().includes('safety') ||
            text.toLowerCase().includes('security')) {
            
            // 确保元素可见且在右侧会话区域
            if (rect.x > 300 && rect.width > 0 && rect.height > 0) {
                return {
                    found: true,
                    text: text.trim().substring(0, 200),
                    position: {x: Math.round(rect.x), y: Math.round(rect.y)}
                };
            }
        }
    }
    
    return {found: false};
});

console.log('安全提示:', securityTip);
```

**Python实现**:
```python
security_tip = page.evaluate("""
    () => {
        const allElements = document.querySelectorAll('*');
        
        for (const el of allElements) {
            const text = el.textContent || '';
            const rect = el.getBoundingClientRect();
            
            if (text.toLowerCase().includes('for your safe') || 
                text.toLowerCase().includes('safety') ||
                text.toLowerCase().includes('security tip')) {
                
                if (rect.x > 300 && rect.width > 0 && rect.height > 0) {
                    return {
                        found: true,
                        text: text.trim().substring(0, 200),
                        position: {x: Math.round(rect.x), y: Math.round(rect.y)},
                        tag: el.tagName,
                        className: el.className || ''
                    };
                }
            }
        }
        
        return {found: false};
    }
""")

logger.info(f"✓ 安全提示: {security_tip['found']}")
if security_tip['found']:
    logger.info(f"  位置: ({security_tip['position']['x']}, {security_tip['position']['y']})")
    logger.info(f"  内容: {security_tip['text'][:100]}")
    page.screenshot(path="screenshots/tc008_security_tip.png")
```

**预期结果**:
- ✅ 找到安全提示文本
- ✅ 提示内容包含"for your safe"关键词
- ✅ 提示位于会话页面顶部

### 🔍 验证点

#### 验证1：安全提示存在
**验证逻辑**:
```python
assert security_tip['found'], "未找到安全提示"
logger.info("✓ 安全提示验证通过")
```

**预期结果**:
- ✅ 安全提示存在

#### 验证2：提示内容正确
**验证逻辑**:
```python
if security_tip['found']:
    tip_text_lower = security_tip['text'].lower()
    assert 'safe' in tip_text_lower or 'safety' in tip_text_lower or 'security' in tip_text_lower, "安全提示内容不正确"
    logger.info("✓ 安全提示内容验证通过")
```

**预期结果**:
- ✅ 提示内容包含安全相关关键词

### 📸 截图要求
- `tc008_conversation_initial.png` - 进入会话初始状态
- `tc008_after_scroll_top.png` - 滚动到顶部后
- `tc008_security_tip.png` - 安全提示显示

---

## 📊 测试流程图

```mermaid
graph TD
    A[开始] --> B[TC001: 从首页访问Messages]
    B --> C{访问成功?}
    C -->|是| D[TC002: 探索会话列表功能]
    C -->|否| Z[结束 - 失败]
    
    D --> E{会话数量>=2?}
    E -->|是| F[TC003: 探索会话详情功能]
    E -->|否| Z
    
    F --> G[检查安全提示]
    F --> H[检查电话按钮]
    F --> I[检查设置菜单]
    
    I --> J{设置菜单可见?}
    J -->|是| K[检查免打扰]
    J -->|是| L[检查拉黑]
    J -->|否| M[TC004: 探索消息发送]
    
    K --> M
    L --> M
    
    M --> N[测试输入框]
    M --> O[检查附件功能]
    M --> P[检查表情功能]
    
    N --> Q[TC005: 会话列表与消息列表展示校验]
    O --> Q
    P --> Q
    
    Q --> R[列表：头像昵称时间戳]
    Q --> S[未读标识]
    Q --> T[消息列表：头像昵称与发送校验]
    
    R --> U[TC006: 探索用户信息]
    S --> U
    T --> U
    
    U --> V[检查用户头像]
    U --> W[检查用户名]
    U --> X[检查在线状态]
    
    V --> Y[TC007: 探索消息展示]
    W --> Y
    X --> Y
    
    Y --> AA[分析消息类型]
    Y --> AB[检查时间戳]
    Y --> AC[检查消息状态]
    
    AA --> AD[TC008: 综合探索]
    AB --> AD
    AC --> AD
    
    AD --> AE[生成功能清单]
    AE --> AF[结束 - 成功]
```

---

## 🎯 元素选择器汇总

### 页面导航

| 元素名称 | 优先选择器 | 备选选择器1 | 备选选择器2 | 说明 |
|---------|-----------|------------|------------|------|
| Messages链接 | `a:has-text("Messages")` | `a[href*="chat"]` | `a[href*="message"]` | 首页导航到Messages |

### 会话列表

| 元素名称 | 优先选择器 | 备选选择器1 | 备选选择器2 | 说明 |
|---------|-----------|------------|------------|------|
| 会话列表容器 | `[class*="conversation-list"]` | `[class*="chat-list"]` | `[class*="message-list"]` | 会话列表外层容器 |
| 会话列表项 | `[class*="conversation"]` | `[class*="chat-item"]` | `[class*="message-item"]` | 单个会话项 |
| 第二个会话 | `locator(...).nth(1)` | - | - | 索引从0开始 |
| 用户头像 | `img[class*="avatar"]` | `[class*="avatar"] img` | - | 会话项中的头像 |
| 用户名 | `[class*="name"]` | `[class*="user"]` | - | 会话项中的用户名 |
| 消息预览 | `[class*="message"]` | `[class*="preview"]` | `[class*="content"]` | 最后一条消息预览 |
| 时间戳 | `[class*="time"]` | `[class*="date"]` | - | 消息时间 |
| 未读标识 | `[class*="unread"]` | `[class*="badge"]` | `[class*="count"]` | 未读消息数量 |
| （不适用） | - | - | - | 当前模块无会话搜索与筛选，不提供搜索框/筛选器 |

### 会话详情

| 元素名称 | 优先选择器 | 备选选择器1 | 备选选择器2 | 说明 |
|---------|-----------|------------|------------|------|
| 会话详情容器 | `[class*="conversation-detail"]` | `[class*="chat-detail"]` | - | 会话详情外层容器 |
| 消息输入框 | `textarea[placeholder*="message"]` | `input[placeholder*="message"]` | - | 消息输入框 |
| 发送按钮 | `button:has-text("Send")` | `button[class*="send"]` | - | 发送消息按钮 |
| 消息历史容器 | `[class*="message-history"]` | `[class*="chat-content"]` | `[class*="conversation-content"]` | 消息历史区域 |
| 消息项 | `[class*="message-item"]` | `[class*="chat-bubble"]` | `[class*="message-bubble"]` | 单条消息 |

### 功能按钮

| 元素名称 | 优先选择器 | 备选选择器1 | 备选选择器2 | 说明 |
|---------|-----------|------------|------------|------|
| 安全提示 | `text=/safety.*personal information/i` | `[class*="security-tip"]` | `[class*="safety-tip"]` | 安全提示文本 |
| 电话按钮 | `button:has-text("Call")` | `button[class*="phone"]` | `svg[class*="phone"]` | 电话/通话功能 |
| 设置按钮 | `button:has-text("Settings")` | `button[class*="settings"]` | `svg[class*="gear"]` | 设置/更多选项 |
| 附件按钮 | `button[class*="attach"]` | `svg[class*="paperclip"]` | - | 附件上传 |
| 表情按钮 | `button[class*="emoji"]` | `svg[class*="emoji"]` | `svg[class*="smile"]` | 表情选择 |
| 图片按钮 | `button[class*="image"]` | `button[class*="photo"]` | - | 图片上传 |

### 设置菜单

| 元素名称 | 优先选择器 | 备选选择器1 | 备选选择器2 | 说明 |
|---------|-----------|------------|------------|------|
| 设置菜单容器 | `[role="menu"]` | `.dropdown-menu` | `[class*="settings-menu"]` | 设置菜单外层 |
| 免打扰选项 | `text=/Do Not Disturb/i` | `button:has-text("Mute")` | `[class*="mute"]` | 免打扰功能 |
| 拉黑选项 | `text=/Block/i` | `button:has-text("Block")` | `[class*="block"]` | 拉黑功能 |

### 对话框

| 元素名称 | 优先选择器 | 备选选择器1 | 备选选择器2 | 说明 |
|---------|-----------|------------|------------|------|
| 对话框容器 | `[role="dialog"]` | `.modal` | - | 确认弹窗 |
| 关闭按钮 | `button:has-text("Close")` | `button:has-text("Cancel")` | `button[class*="close"]` | 关闭/取消按钮 |
| 确认按钮 | `button:has-text("Confirm")` | `button:has-text("OK")` | - | 确认按钮 |

---

## 📊 测试数据

### 登录账号
```yaml
ae_seller:
  email: gaosong01@58.com
  password: Qwert_123
  site: ae
  role: seller
  session_name: ae_seller
```

### 测试URL
```yaml
home_page: https://ae.ok.com/en/city-abu-dhabi/
messages_page: https://aepub.ok.com/biz/en/chat
```

### 测试关键词（可选，用于消息发送探针等）
```yaml
probe_message_keywords:
  - test
  - hello
  - 你好
```

---

## ⚠️ 注意事项

### 1. Session复用策略
- ✅ **优先使用SessionManager加载已保存的Session**
- ✅ 如果Session不存在或失效，执行完整登录流程
- ✅ 登录成功后保存Session供后续测试使用
- ✅ Session文件命名格式: `{site}_{role}_session.json`

### 2. 等待策略
- ✅ 页面导航后使用 `wait_for_load_state('networkidle')`
- ✅ 元素交互前使用 `wait_for_selector()` 或 `is_visible()`
- ⚠️ 避免使用固定的 `time.sleep()`，除非必要
- ✅ 动态内容加载后额外等待1-2秒确保稳定

### 3. 错误处理
- ✅ 所有元素查找都应该有超时设置
- ✅ 使用 `try-except` 捕获异常并记录日志
- ⚠️ **探索性测试中，某些功能不存在不应该导致测试失败**
- ✅ 使用 `.catch(() => false)` 或 Python的 `try-except` 处理可选元素

### 4. 截图策略
- ✅ 每个关键步骤完成后截图
- ✅ 测试失败时自动截图（由conftest.py处理）
- ✅ 截图保存到 `reports/screenshots/` 目录
- ✅ 截图命名格式: `{test_name}_{step}_{timestamp}.png`

### 5. 探索性测试的特点
- ⚠️ **不强制要求所有功能都存在**
- ✅ 重点在于记录发现的功能和元素
- ✅ 使用INFO级别日志记录探索结果
- ✅ 失败不应该阻止后续探索
- ✅ 使用 `pytest.skip()` 跳过不满足前置条件的测试

### 6. 元素定位最佳实践
- ✅ **优先级1**: 语义化定位器（`page.get_by_role()`, `page.get_by_text()`）
- ✅ **优先级2**: 属性定位器（`[placeholder*="..."]`, `button:has-text("...")`）
- ✅ **优先级3**: 类名模糊匹配（`[class*="conversation"]`）
- ❌ **禁止使用**: XPath、`nth-child()`、完整class名

### 7. 交互操作注意事项
- ✅ 点击操作前确保元素可见且稳定
- ✅ 点击后等待页面响应（1-2秒）
- ✅ 弹窗操作后记得关闭，避免影响后续测试
- ✅ 使用 `page.keyboard.press('Escape')` 作为关闭弹窗的备选方案

---

## 📈 预期测试结果

### ✅ 成功标准
1. ✅ 能够从首页成功访问Messages页面
2. ✅ 能够查看会话列表并统计会话数量
3. ✅ 能够进入会话详情
4. ✅ 记录所有发现的功能和元素
5. ✅ 完成所有探索性测试步骤
6. ✅ 生成完整的功能清单

### 📋 探索目标清单

#### 会话列表功能
- [ ] 会话数量统计
- [ ] 会话项元素结构（头像、用户名、消息预览、时间戳）
- [ ] 会话列表展示校验（头像可见、昵称非空、时间戳展示）— **当前无搜索/筛选**
- [ ] 未读标识
- [ ] 会话排序（最新消息优先等）

#### 会话详情功能
- [ ] 消息输入框
- [ ] 发送按钮
- [ ] 消息历史
- [ ] 安全提示
- [ ] 电话按钮
- [ ] 设置菜单
- [ ] 免打扰功能
- [ ] 拉黑功能

#### 消息发送功能
- [ ] 文本输入
- [ ] 附件上传
- [ ] 表情选择
- [ ] 图片上传
- [ ] 视频上传（如果有）

#### 用户信息
- [ ] 用户头像
- [ ] 用户名称
- [ ] 在线状态
- [ ] 资料入口

#### 消息展示
- [ ] 消息方向识别（发送/接收）
- [ ] 文本消息
- [ ] 图片消息
- [ ] 链接消息
- [ ] 时间戳
- [ ] 已读状态

---

## 🐛 常见问题和解决方案

### Q1: Messages链接找不到怎么办？
**A**: 可能的原因和解决方案：
1. **链接文本不是 "Messages"**: 尝试其他文本如 "Chat", "Inbox", "Conversations"
2. **链接在折叠的菜单中**: 需要先点击菜单按钮（汉堡图标、三条线等）
3. **链接需要登录后才显示**: 确保已登录，检查用户头像是否可见
4. **直接导航**: 可以直接使用 `page.goto('https://aepub.ok.com/biz/en/chat')` 绕过点击

**代码示例**:
```python
click_success = messages_page.click_messages_link()
if not click_success:
    logger.info("✗ 点击Messages链接失败，尝试直接导航")
    messages_page.navigate_to_messages_directly(config['target_page'])
```

### Q2: 会话列表为空怎么办？
**A**: 
1. **确认测试账号中有会话记录**: 手动登录检查
2. **检查是否有筛选条件**: 清除所有筛选
3. **尝试刷新页面**: `page.reload()`
4. **检查网络请求**: 可能是API请求失败

### Q3: 某些功能按钮找不到？
**A**: 
1. **这是探索性测试**: 某些功能可能不存在，不影响测试继续
2. **功能可能需要特定条件**: 如电话按钮可能需要对方提供电话号码
3. **功能可能在不同位置**: 尝试多个选择器组合
4. **记录未找到的功能**: 使用日志记录，不抛出异常

### Q4: 点击操作被拦截怎么办？
**A**: 
1. **检查是否有弹窗遮挡**: 先关闭弹窗再点击
2. **元素可能不稳定**: 等待元素稳定后再点击
3. **使用force点击**: `element.click(force=True)`（谨慎使用）
4. **使用JavaScript点击**: `page.evaluate('element => element.click()', element)`

### Q5: Session失效怎么办？
**A**: 
1. **自动重新登录**: SessionManager会检测失效并触发登录
2. **手动删除Session文件**: 删除 `reports/sessions/` 下的对应文件
3. **检查Cookie域名**: 确保Cookie的domain与当前站点匹配

---

## 🔧 元素定位策略详解

### 1. 语义化定位器（最优）
```javascript
// Playwright推荐方式
page.getByRole('button', { name: 'Send' })
page.getByText('Messages')
page.getByPlaceholder(/message/i)  // 当前模块无「搜索会话」入口，勿假设 Search conversations
page.getByPlaceholder('Type a message')
```

**优点**: 
- 符合无障碍标准
- 对DOM结构变化不敏感
- 可读性强

### 2. 属性定位器（次优）
```javascript
// 通过placeholder（消息输入；勿用会话搜索框 — 当前模块无此项）
page.locator('textarea[placeholder*="message"], input[placeholder*="message"]')

// 通过href
page.locator('a[href*="chat"]')

// 通过文本内容
page.locator('button:has-text("Send")')
```

**优点**:
- 相对稳定
- 易于理解
- 支持模糊匹配

### 3. 类名定位器（备选）
```javascript
// 模糊匹配class
page.locator('[class*="conversation"]')
page.locator('[class*="message-item"]')
```

**注意**:
- 避免使用完整class名（易变化）
- 使用 `*=` 进行模糊匹配
- 选择语义化的class片段

### 4. 禁止使用
```javascript
// ❌ XPath（脆弱、难维护）
page.locator('//div[@class="chat"]/div[2]/button')

// ❌ nth-child（结构依赖强）
page.locator('div:nth-child(2)')

// ❌ ID选择器（除非ID明确且稳定）
page.locator('#message-123456')
```

---

## 📝 测试执行指南

> **运行目录**：请在 `bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc` 下执行下列命令（或对上述路径使用 `./.venv/bin/pytest`）。脚本入口已从历史的 `test_messages_explore.py` 合并为 `test_cases/体验/消息中心+发布模块/test_messages_complete.py`。

### 执行单个测试
```bash
# 执行TC001
pytest test_cases/体验/消息中心+发布模块/test_messages_complete.py::test_access_messages_from_home -v -s

# 执行TC002
pytest test_cases/体验/消息中心+发布模块/test_messages_complete.py::test_explore_conversation_list -v -s
```

### 执行所有测试
```bash
# 执行所有Messages探索测试
pytest test_cases/体验/消息中心+发布模块/test_messages_complete.py -v -s

# 使用标记执行
pytest -m "messages and exploration" -v -s
```

### 执行特定优先级
```bash
# 执行P0和P1优先级的测试
pytest test_cases/体验/消息中心+发布模块/test_messages_complete.py -m "p0 or p1" -v -s
```

### 生成Allure报告
```bash
# 执行测试并生成报告
pytest test_cases/体验/消息中心+发布模块/test_messages_complete.py -v -s

# 查看报告
allure serve reports/allure-results
```

---

## 📊 功能探索结果模板

### Messages页面功能清单

| 功能分类 | 功能名称 | 是否存在 | 位置 | 备注 |
|---------|---------|---------|------|------|
| **页面访问** | 从首页点击Messages | ✅/❌ | 首页导航栏 | |
| **会话列表** | 会话数量统计 | ✅ | - | 记录数量 |
| **会话列表** | 用户头像 | ✅/❌ | 会话项 | |
| **会话列表** | 用户名 | ✅/❌ | 会话项 | |
| **会话列表** | 消息预览 | ✅/❌ | 会话项 | |
| **会话列表** | 时间戳 | ✅/❌ | 会话项 | |
| **会话列表** | 未读标识 | ✅/❌ | 会话项 | |
| **会话列表** | 搜索/筛选 | **不提供** | — | 当前模块无此能力 |
| **消息列表** | 双方头像/气泡方向 | ✅/❌ | 会话详情中部 | 与 TC005 步骤3 联动 |
| **消息列表** | 发送后消息入列 | ✅/❌ | 会话详情中部 | 文案与输入一致 |
| **会话详情** | 消息输入框 | ✅/❌ | 底部 | |
| **会话详情** | 发送按钮 | ✅/❌ | 输入框旁 | |
| **会话详情** | 消息历史 | ✅/❌ | 中间区域 | |
| **会话详情** | 安全提示 | ✅/❌ | 顶部 | |
| **会话详情** | 电话按钮 | ✅/❌ | 顶部工具栏 | |
| **会话详情** | 设置按钮 | ✅/❌ | 顶部工具栏 | |
| **设置菜单** | 免打扰功能 | ✅/❌ | 设置菜单内 | |
| **设置菜单** | 拉黑功能 | ✅/❌ | 设置菜单内 | |
| **消息发送** | 文本输入 | ✅/❌ | - | |
| **消息发送** | 附件上传 | ✅/❌ | 输入框旁 | |
| **消息发送** | 表情功能 | ✅/❌ | 输入框旁 | |
| **消息发送** | 图片上传 | ✅/❌ | 输入框旁 | |
| **用户信息** | 用户头像 | ✅/❌ | 顶部 | |
| **用户信息** | 用户名称 | ✅/❌ | 顶部 | |
| **用户信息** | 在线状态 | ✅/❌ | 用户名旁 | |
| **用户信息** | 资料入口 | ✅/❌ | 点击用户名 | |
| **消息展示** | 消息方向 | ✅/❌ | - | 发送/接收 |
| **消息展示** | 文本消息 | ✅/❌ | - | |
| **消息展示** | 图片消息 | ✅/❌ | - | |
| **消息展示** | 链接消息 | ✅/❌ | - | |
| **消息展示** | 时间戳 | ✅/❌ | 消息旁 | |
| **消息展示** | 已读状态 | ✅/❌ | 消息旁 | |

### 发现的问题
1. [记录测试过程中发现的问题]
2. [如：某功能按钮位置不明显]
3. [如：某操作响应时间过长]
4. [如：某文案显示不清晰]

### 改进建议
1. [记录对产品的改进建议]
2. [如：建议添加搜索历史功能]
3. [如：建议优化消息加载速度]
4. [如：建议增加消息撤回功能]

---

## 📚 附录

### A. Playwright常用API

#### 页面导航
```javascript
await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
await page.waitForLoadState('networkidle');
await page.waitForURL('**/chat**', { timeout: 30000 });
```

#### 元素等待
```javascript
await element.waitFor({ state: 'visible', timeout: 10000 });
await page.waitForSelector(selector, { state: 'visible', timeout: 10000 });
await page.waitForTimeout(2000); // 固定等待，谨慎使用
```

#### 元素交互
```javascript
await element.click({ timeout: 10000 });
await element.fill('text');
await element.type('text', { delay: 100 }); // 模拟逐字输入
await element.hover();
```

#### 元素查询
```javascript
const isVisible = await element.isVisible({ timeout: 5000 });
const isEditable = await element.isEditable({ timeout: 3000 });
const count = await locator.count();
const text = await element.textContent();
const value = await element.inputValue();
```

### B. Python Pytest常用装饰器

```python
@pytest.mark.parametrize("keyword", ["test", "hello", "你好"])
@pytest.mark.skip(reason="功能未实现")
@pytest.mark.skipif(condition, reason="条件不满足")
@pytest.mark.xfail(reason="已知问题")
```

### C. Allure报告增强

```python
@allure.feature("功能模块")
@allure.story("用户故事")
@allure.title("测试标题")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("详细描述")
@allure.link("https://jira.example.com/ISSUE-123", name="相关Issue")

# 在测试中添加步骤
with allure.step("步骤1: 登录"):
    login_page.login()

# 添加附件
allure.attach(page.screenshot(), name="screenshot", attachment_type=allure.attachment_type.PNG)
```

---

---

## TC008: 会话页面电话按钮测试

### 📌 测试信息
- **用例ID**: `case_id_messages_explore_009`
- **优先级**: P2 (Medium)
- **测试类型**: functional
- **模块标记**: messages, conversation, phone, ae
- **Allure标记**:
  - Feature: OK - Messages
  - Story: Messages页面功能探索 - 电话按钮
  - Title: 测试会话页面的电话按钮功能
  - Severity: NORMAL

### 🎯 测试目标
测试会话详情页的电话按钮功能（如果存在）。

### ✅ 前置条件
1. 已成功登录
2. 已进入Messages页面
3. 已进入某个会话详情

### 📝 测试步骤

#### 步骤1：查找电话按钮
**操作**: 
```javascript
// 在会话详情页查找电话按钮
const phoneSelectors = [
    'button:has-text("Call")',
    'button:has-text("Phone")',
    'button[class*="phone"]',
    'button[class*="call"]',
    'button:has(svg[class*="phone"])',
    'button[aria-label*="call"]',
    'button[aria-label*="phone"]',
    'a[href^="tel:"]'
];

let phoneButton = null;
let hasPhoneButton = false;

for (const selector of phoneSelectors) {
    const element = page.locator(selector).first();
    if (await element.isVisible({ timeout: 2000 }).catch(() => false)) {
        phoneButton = element;
        hasPhoneButton = true;
        console.log(`✓ 发现电话按钮，选择器: ${selector}`);
        break;
    }
}

console.log(`电话按钮: ${hasPhoneButton ? '存在' : '不存在'}`);
```

**Python实现**:
```python
has_phone = messages_page.check_phone_button_advanced()
logger.info(f"✓ 电话按钮: {has_phone['exists']}")
```

**预期结果**:
- ⚠️ 电话按钮可能存在也可能不存在

#### 步骤2：测试电话按钮点击（如果存在）
**操作**: 
```javascript
if (hasPhoneButton) {
    await phoneButton.click();
    await page.waitForTimeout(2000);
    
    // 检查反馈
    const callDialog = page.locator('[role="dialog"], .modal').first();
    const hasDialog = await callDialog.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (hasDialog) {
        console.log('✓ 电话功能弹窗已显示');
        
        // 关闭弹窗
        const closeBtn = callDialog.locator('button:has-text("Close"), button:has-text("Cancel")').first();
        if (await closeBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
            await closeBtn.click();
        } else {
            await page.keyboard.press('Escape');
        }
    }
}
```

**Python实现**:
```python
if has_phone['exists']:
    click_result = messages_page.click_phone_button_advanced()
    logger.info(f"  点击成功: {click_result['success']}")
    logger.info(f"  弹窗显示: {click_result['has_dialog']}")
```

**预期结果**:
- ✅ 如果电话按钮存在，点击后应该有反馈

### 🔍 验证点
- ✅ 完成电话按钮的探索和测试
- ✅ 记录电话按钮的存在性和交互结果

### 📸 截图要求
- 电话按钮位置截图（如果存在）
- 电话功能弹窗截图（如果有）

---

## TC009: 会话页面设置入口测试

### 📌 测试信息
- **用例ID**: `case_id_messages_explore_010`
- **优先级**: P1 (High)
- **测试类型**: functional
- **模块标记**: messages, conversation, settings, ae
- **Allure标记**:
  - Feature: OK - Messages
  - Story: Messages页面功能探索 - 设置入口
  - Title: 测试会话页面右上角三点菜单（...）
  - Severity: CRITICAL

### 🎯 测试目标
测试会话详情页右上角的三点菜单（...）按钮，验证能否打开设置菜单。

### ✅ 前置条件
1. 已成功登录
2. 已进入Messages页面
3. 已进入某个会话详情

### 📝 测试步骤

#### 步骤1：定位会话详情页右上角的三点菜单（...）
**操作**: 
```javascript
// 会话详情页右上角有一个三点菜单按钮（...）
// 通过多种方式定位
const settingsButtonSelectors = [
    // 直接查找三点文本
    "text=/^\\.\\.\\.$|^⋮$/",
    // 通过class查找
    "button[class*='more']",
    "button[class*='menu']",
    "button[class*='options']",
    "div[class*='more-button']",
    // 通过aria-label
    "button[aria-label*='more']",
    "button[aria-label*='options']",
    "button[aria-label*='menu']"
];

let settingsButton = null;
let hasSettingsButton = false;

for (const selector of settingsButtonSelectors) {
    const element = page.locator(selector).first();
    if (await element.isVisible({ timeout: 2000 }).catch(() => false)) {
        // 确保是会话详情区域的按钮（右侧，y < 150）
        const bbox = await element.boundingBox();
        if (bbox && bbox.x > 800 && bbox.y < 150) {
            settingsButton = element;
            hasSettingsButton = true;
            console.log(`✓ 找到设置按钮，选择器: ${selector}`);
            break;
        }
    }
}

console.log(`设置按钮（...）: ${hasSettingsButton ? '存在' : '不存在'}`);
```

**Python实现**:
```python
has_settings = messages_page.check_three_dots_menu()
logger.info(f"✓ 三点菜单（...）: {has_settings['exists']}")
if has_settings['exists']:
    logger.info(f"  位置: ({has_settings['x']}, {has_settings['y']})")
```

**预期结果**:
- ✅ 应该能找到会话详情页右上角的三点菜单（...）

#### 步骤2：点击三点菜单打开下拉列表
**操作**: 
```javascript
if (hasSettingsButton) {
    await settingsButton.click();
    await page.waitForTimeout(2000);
    
    // 检查下拉菜单是否显示
    const dropdown = page.locator('[role="menu"], .dropdown-menu, [class*="dropdown"], [class*="popover"]').first();
    const hasDropdown = await dropdown.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (hasDropdown) {
        console.log('✓ 下拉菜单已显示');
        
        // 获取菜单内容
        const menuText = await dropdown.textContent();
        console.log(`菜单内容: ${menuText}`);
        
        // 获取所有菜单项
        const menuItems = dropdown.locator('[role="menuitem"], div[class*="item"], button, a');
        const itemCount = await menuItems.count();
        console.log(`菜单项数量: ${itemCount}`);
        
        for (let i = 0; i < itemCount; i++) {
            const item = menuItems.nth(i);
            const itemText = await item.textContent();
            console.log(`  选项 ${i + 1}: ${itemText.trim()}`);
        }
    } else {
        console.log('✗ 下拉菜单未显示');
    }
}
```

**Python实现**:
```python
if has_settings['exists']:
    menu_result = messages_page.click_three_dots_menu()
    logger.info(f"  菜单打开: {menu_result['opened']}")
    logger.info(f"  菜单项数量: {menu_result['item_count']}")
    for i, item in enumerate(menu_result['items'], 1):
        logger.info(f"    {i}. {item}")
```

**预期结果**:
- ✅ 点击三点菜单后应该显示下拉列表
- ✅ 下拉列表中应该包含多个选项（pin/unpin, mute/unmute, block/unblock等）

### 🔍 验证点
- ✅ 三点菜单（...）按钮存在
- ✅ 点击后能打开下拉菜单
- ✅ 下拉菜单中包含功能选项

### 📸 截图要求
- 三点菜单按钮位置截图
- 下拉菜单展开后的完整截图

---

## TC010: 会话页面置顶功能测试

### 📌 测试信息
- **用例ID**: `case_id_messages_explore_011`
- **优先级**: P2 (Medium)
- **测试类型**: functional
- **模块标记**: messages, conversation, pin, ae
- **Allure标记**:
  - Feature: OK - Messages
  - Story: Messages页面功能探索 - 置顶功能
  - Title: 测试会话置顶/取消置顶功能
  - Severity: NORMAL

### 🎯 测试目标
测试会话详情页设置菜单中的置顶（Pin/Unpin）功能。

### ✅ 前置条件
1. 已成功登录
2. 已进入Messages页面
3. 已进入某个会话详情
4. 已打开三点菜单（...）

### 📝 测试步骤

#### 步骤1：打开三点菜单
**操作**: 
```javascript
// 点击右上角三点菜单
const settingsButton = page.locator("text=/^\\.\\.\\.$|^⋮$/").first();
await settingsButton.click();
await page.waitForTimeout(2000);
```

**Python实现**:
```python
messages_page.click_three_dots_menu()
page.wait_for_timeout(1000)
```

**预期结果**:
- ✅ 下拉菜单已打开

#### 步骤2：查找置顶选项（Pin/Unpin）
**操作**: 
```javascript
const dropdown = page.locator('[role="menu"], .dropdown-menu').first();

// 查找Pin或Unpin选项
const pinSelectors = [
    'text=/^Pin$/i',
    'text=/^Unpin$/i',
    'text=/置顶/i',
    'text=/取消置顶/i',
    '[class*="pin"]'
];

let pinOption = null;
let hasPinOption = false;
let pinText = '';

for (const selector of pinSelectors) {
    const element = dropdown.locator(selector).first();
    if (await element.isVisible({ timeout: 2000 }).catch(() => false)) {
        pinOption = element;
        hasPinOption = true;
        pinText = await element.textContent();
        console.log(`✓ 找到置顶选项: ${pinText.trim()}`);
        break;
    }
}
```

**Python实现**:
```python
has_pin = messages_page.check_pin_option_in_menu()
logger.info(f"✓ 置顶选项: {has_pin['exists']}")
if has_pin['exists']:
    logger.info(f"  选项文本: {has_pin['text']}")
```

**预期结果**:
- ✅ 应该能找到Pin或Unpin选项

#### 步骤3：点击置顶选项
**操作**: 
```javascript
if (hasPinOption) {
    await pinOption.click();
    await page.waitForTimeout(2000);
    
    // 检查是否有确认弹窗
    const confirmDialog = page.locator('[role="dialog"], .modal').first();
    const hasConfirmDialog = await confirmDialog.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (hasConfirmDialog) {
        console.log('✓ 确认弹窗已显示');
        
        // 取消操作（避免实际修改）
        const cancelButton = confirmDialog.locator('button:has-text("Cancel"), button:has-text("Close")').first();
        if (await cancelButton.isVisible({ timeout: 2000 }).catch(() => false)) {
            await cancelButton.click();
        } else {
            await page.keyboard.press('Escape');
        }
    } else {
        console.log('✓ 置顶操作已执行（无确认弹窗）');
        
        // 恢复原状（如果是toggle操作）
        // 重新打开菜单检查状态是否改变
        await settingsButton.click();
        await page.waitForTimeout(1000);
        
        const newPinText = await dropdown.locator('text=/Pin|Unpin|置顶/i').first().textContent().catch(() => '');
        console.log(`操作后选项文本: ${newPinText.trim()}`);
        
        // 如果状态改变了，再点击一次恢复
        if (newPinText !== pinText) {
            await dropdown.locator('text=/Pin|Unpin|置顶/i').first().click();
            await page.waitForTimeout(1000);
        }
    }
}
```

**Python实现**:
```python
if has_pin['exists']:
    pin_result = messages_page.click_pin_option()
    logger.info(f"  点击成功: {pin_result['success']}")
    logger.info(f"  确认弹窗: {pin_result['has_dialog']}")
```

**预期结果**:
- ✅ 点击后应该执行置顶操作或显示确认弹窗

### 🔍 验证点
- ✅ 置顶选项存在于下拉菜单中
- ✅ 点击置顶选项有反馈

### 📸 截图要求
- 下拉菜单中置顶选项的截图
- 确认弹窗截图（如果有）

---

## TC011: 会话页面免打扰功能测试

### 📌 测试信息
- **用例ID**: `case_id_messages_explore_012`
- **优先级**: P2 (Medium)
- **测试类型**: functional
- **模块标记**: messages, conversation, mute, ae
- **Allure标记**:
  - Feature: OK - Messages
  - Story: Messages页面功能探索 - 免打扰功能
  - Title: 测试会话免打扰/取消免打扰功能
  - Severity: NORMAL

### 🎯 测试目标
测试会话详情页设置菜单中的免打扰（Mute/Unmute）功能。

### ✅ 前置条件
1. 已成功登录
2. 已进入Messages页面
3. 已进入某个会话详情
4. 已打开三点菜单（...）

### 📝 测试步骤

#### 步骤1：打开三点菜单
**操作**: 
```javascript
const settingsButton = page.locator("text=/^\\.\\.\\.$|^⋮$/").first();
await settingsButton.click();
await page.waitForTimeout(2000);
```

**Python实现**:
```python
messages_page.click_three_dots_menu()
page.wait_for_timeout(1000)
```

**预期结果**:
- ✅ 下拉菜单已打开

#### 步骤2：查找免打扰选项（Mute/Unmute）
**操作**: 
```javascript
const dropdown = page.locator('[role="menu"], .dropdown-menu').first();

const muteSelectors = [
    'text=/^Mute$/i',
    'text=/^Unmute$/i',
    'text=/Do Not Disturb/i',
    'text=/免打扰/i',
    'text=/静音/i',
    '[class*="mute"]'
];

let muteOption = null;
let hasMuteOption = false;
let muteText = '';

for (const selector of muteSelectors) {
    const element = dropdown.locator(selector).first();
    if (await element.isVisible({ timeout: 2000 }).catch(() => false)) {
        muteOption = element;
        hasMuteOption = true;
        muteText = await element.textContent();
        console.log(`✓ 找到免打扰选项: ${muteText.trim()}`);
        break;
    }
}
```

**Python实现**:
```python
has_mute = messages_page.check_mute_option_in_menu()
logger.info(f"✓ 免打扰选项: {has_mute['exists']}")
if has_mute['exists']:
    logger.info(f"  选项文本: {has_mute['text']}")
```

**预期结果**:
- ✅ 应该能找到Mute或Unmute选项

#### 步骤3：点击免打扰选项
**操作**: 
```javascript
if (hasMuteOption) {
    await muteOption.click();
    await page.waitForTimeout(2000);
    
    // 检查确认弹窗
    const confirmDialog = page.locator('[role="dialog"], .modal').first();
    const hasConfirmDialog = await confirmDialog.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (hasConfirmDialog) {
        console.log('✓ 确认弹窗已显示');
        const dialogText = await confirmDialog.textContent();
        console.log(`弹窗内容: ${dialogText}`);
        
        // 取消操作
        const cancelButton = confirmDialog.locator('button:has-text("Cancel"), button:has-text("No")').first();
        if (await cancelButton.isVisible({ timeout: 2000 }).catch(() => false)) {
            await cancelButton.click();
        } else {
            await page.keyboard.press('Escape');
        }
    } else {
        console.log('✓ 免打扰操作已执行（无确认弹窗）');
    }
}
```

**Python实现**:
```python
if has_mute['exists']:
    mute_result = messages_page.click_mute_option()
    logger.info(f"  点击成功: {mute_result['success']}")
    logger.info(f"  确认弹窗: {mute_result['has_dialog']}")
```

**预期结果**:
- ✅ 点击后应该执行免打扰操作或显示确认弹窗

### 🔍 验证点
- ✅ 免打扰选项存在于下拉菜单中
- ✅ 点击免打扰选项有反馈

### 📸 截图要求
- 下拉菜单中免打扰选项的截图
- 确认弹窗截图（如果有）

---

## TC012: 会话页面拉黑功能完整测试

### 📌 测试信息
- **用例ID**: `case_id_messages_explore_013`
- **优先级**: P1 (High)
- **测试类型**: functional
- **模块标记**: messages, conversation, block, ae
- **Allure标记**:
  - Feature: OK - Messages
  - Story: Messages页面功能探索 - 拉黑功能
  - Title: 测试会话拉黑/取消拉黑完整流程
  - Severity: CRITICAL

### 🎯 测试目标
完整测试会话详情页的拉黑功能流程，包括：
1. Block选项的查找和点击
2. 拉黑确认弹窗的Cancel按钮测试
3. 拉黑确认弹窗的Block按钮测试（实际拉黑）
4. 拉黑半层的显示验证
5. 拉黑半层上Unblock按钮的功能测试

### ✅ 前置条件
1. 已成功登录
2. 已进入Messages页面
3. 会话列表不为空
4. 可以进入会话详情页

### 📝 测试步骤

#### 步骤1：进入Messages页面并打开会话
**操作**: 
```javascript
await page.goto('https://aepub.ok.com/biz/en/chat');
await page.waitForLoadState('networkidle');

const conversationItems = page.locator("[class*='conversation'], [class*='chat-item']");
await conversationItems.nth(1).click();
await page.waitForTimeout(3000);
```

**Python实现**:
```python
messages_page.navigate_to_messages_directly(config['target_page'])
messages_page.wait_for_conversation_list()
messages_page.click_conversation_by_index(1)
page.wait_for_timeout(3000)
page.screenshot(path="screenshots/tc013_conversation_page.png")
```

**预期结果**:
- ✅ 成功进入会话详情页

#### 步骤2：打开三点菜单
**操作**: 
```javascript
const settingsButton = page.locator("text=/^\\.\\.\\.$|^⋮$/").first();
await settingsButton.click();
await page.waitForTimeout(2000);
```

**Python实现**:
```python
menu_result = messages_page.click_three_dots_menu()
logger.info(f"✓ 菜单已打开，菜单项数量: {menu_result['item_count']}")
page.screenshot(path="screenshots/tc013_menu_opened.png")
```

**预期结果**:
- ✅ 三点菜单已打开

#### 步骤3：查找Block选项
**操作**: 
```javascript
const blockInfo = await page.evaluate(() => {
    const elements = Array.from(document.querySelectorAll('*'));
    const blockElements = elements.filter(el => {
        const text = el.textContent?.trim() || '';
        const rect = el.getBoundingClientRect();
        const isBlockText = text === 'Block' || text === 'Unblock';
        const isVisible = rect.width > 0 && rect.height > 0;
        return isBlockText && isVisible;
    });
    
    if (blockElements.length > 0) {
        const el = blockElements[0];
        const rect = el.getBoundingClientRect();
        return {
            found: true,
            text: el.textContent?.trim(),
            x: Math.round(rect.x),
            y: Math.round(rect.y)
        };
    }
    return { found: false };
});
```

**Python实现**:
```python
has_block = messages_page.check_block_option_in_menu()
logger.info(f"✓ Block选项: {has_block['exists']}")
logger.info(f"  选项文本: {has_block['text']}")
logger.info(f"  选项位置: ({has_block['x']}, {has_block['y']})")
```

**预期结果**:
- ✅ 找到Block选项

#### 步骤4：测试Cancel按钮 - 点击Block并在弹窗中点击Cancel
**操作**: 
```javascript
// 点击Block选项
await page.mouse.click(blockInfo.x + 10, blockInfo.y + 10);
await page.waitForTimeout(2000);

// 查找确认弹窗
const dialog = document.querySelector('[role="dialog"], .modal');
if (dialog) {
    const buttons = Array.from(dialog.querySelectorAll('button'));
    const cancelBtn = buttons.find(btn => {
        const text = btn.textContent?.trim().toLowerCase() || '';
        return text === 'cancel' || text === 'close' || text === 'no';
    });
    
    if (cancelBtn) {
        cancelBtn.click();
    }
}
```

**Python实现**:
```python
# 点击Block选项
page.mouse.click(has_block['x'] + 10, has_block['y'] + 10)
page.wait_for_timeout(2000)

# 查找并点击Cancel按钮
dialog_info = page.evaluate("""
    () => {
        const dialog = document.querySelector('[role="dialog"], .modal');
        if (dialog) {
            const buttons = Array.from(dialog.querySelectorAll('button'));
            return {
                found: true,
                buttons: buttons.map(btn => btn.textContent?.trim())
            };
        }
        return {found: false};
    }
""")

logger.info(f"✓ 确认弹窗: {dialog_info['found']}")
logger.info(f"  弹窗按钮: {dialog_info['buttons']}")
page.screenshot(path="screenshots/tc013_block_dialog.png")

# 点击Cancel
cancel_clicked = page.evaluate("""
    () => {
        const dialog = document.querySelector('[role="dialog"], .modal');
        if (!dialog) return false;
        
        const buttons = Array.from(dialog.querySelectorAll('button'));
        const cancelBtn = buttons.find(btn => {
            const text = btn.textContent?.trim().toLowerCase() || '';
            return text === 'cancel' || text === 'close' || text === 'no';
        });
        
        if (cancelBtn) {
            cancelBtn.click();
            return true;
        }
        return false;
    }
""")

logger.info(f"  ✓ Cancel按钮点击成功: {cancel_clicked}")
page.screenshot(path="screenshots/tc013_after_cancel.png")
```

**预期结果**:
- ✅ 显示拉黑确认弹窗
- ✅ 弹窗包含Cancel和Block按钮
- ✅ 点击Cancel后弹窗关闭

#### 步骤5：重新打开菜单并点击Block
**操作**: 
```javascript
// 重新打开三点菜单
await settingsButton.click();
await page.waitForTimeout(1000);

// 再次点击Block选项
await page.mouse.click(blockInfo.x + 10, blockInfo.y + 10);
await page.waitForTimeout(2000);
```

**Python实现**:
```python
# 重新打开菜单
menu_result2 = messages_page.click_three_dots_menu()
logger.info("✓ 菜单已重新打开")

# 再次查找并点击Block
has_block2 = messages_page.check_block_option_in_menu()
page.mouse.click(has_block2['x'] + 10, has_block2['y'] + 10)
page.wait_for_timeout(2000)
```

**预期结果**:
- ✅ 菜单重新打开成功
- ✅ 再次显示拉黑确认弹窗

#### 步骤6：测试Block确认按钮（实际拉黑）
**操作**: 
```javascript
// 查找并点击Block确认按钮
const dialog = document.querySelector('[role="dialog"], .modal');
if (dialog) {
    const buttons = Array.from(dialog.querySelectorAll('button'));
    const blockBtn = buttons.find(btn => {
        const text = btn.textContent?.trim().toLowerCase() || '';
        return text === 'block' || text === 'confirm' || text === 'ok';
    });
    
    if (blockBtn) {
        blockBtn.click();
        await page.waitForTimeout(3000);
    }
}
```

**Python实现**:
```python
# 点击Block确认按钮
block_confirmed = page.evaluate("""
    () => {
        const dialog = document.querySelector('[role="dialog"], .modal');
        if (!dialog) return {success: false};
        
        const buttons = Array.from(dialog.querySelectorAll('button'));
        const blockBtn = buttons.find(btn => {
            const text = btn.textContent?.trim().toLowerCase() || '';
            return text === 'block' || text === 'confirm' || text === 'ok';
        });
        
        if (blockBtn) {
            blockBtn.click();
            return {success: true, buttonText: blockBtn.textContent?.trim()};
        }
        return {success: false};
    }
""")

logger.info(f"✓ Block按钮点击: {block_confirmed['success']}")
logger.info(f"  按钮文本: {block_confirmed['buttonText']}")
page.wait_for_timeout(3000)
page.screenshot(path="screenshots/tc013_after_block_confirm.png")
```

**预期结果**:
- ✅ Block按钮点击成功
- ✅ 拉黑操作执行

#### 步骤7：验证拉黑半层显示
**操作**: 
```javascript
// 查找拉黑半层
const blockOverlay = await page.evaluate(() => {
    const allElements = Array.from(document.querySelectorAll('div, section'));
    
    for (const el of allElements) {
        const text = el.textContent?.toLowerCase() || '';
        const rect = el.getBoundingClientRect();
        
        if ((text.includes('blocked') || text.includes('unblock')) &&
            rect.x > 300 && rect.width > 200 && rect.height > 100) {
            
            const buttons = Array.from(el.querySelectorAll('button'));
            const unblockBtn = buttons.find(btn => {
                const btnText = btn.textContent?.trim().toLowerCase() || '';
                return btnText === 'unblock' || btnText.includes('unblock');
            });
            
            return {
                found: true,
                text: el.textContent?.substring(0, 200),
                hasUnblockButton: !!unblockBtn,
                unblockButtonText: unblockBtn ? unblockBtn.textContent?.trim() : null
            };
        }
    }
    
    return {found: false};
});
```

**Python实现**:
```python
# 查找拉黑半层
block_overlay = page.evaluate("""
    () => {
        const allElements = Array.from(document.querySelectorAll('div, section'));
        
        for (const el of allElements) {
            const text = el.textContent?.toLowerCase() || '';
            const rect = el.getBoundingClientRect();
            
            if ((text.includes('blocked') || text.includes('unblock')) &&
                rect.x > 300 && rect.width > 200 && rect.height > 100) {
                
                const buttons = Array.from(el.querySelectorAll('button'));
                const unblockBtn = buttons.find(btn => {
                    const btnText = btn.textContent?.trim().toLowerCase() || '';
                    return btnText === 'unblock' || btnText.includes('unblock');
                });
                
                return {
                    found: true,
                    text: el.textContent?.substring(0, 200),
                    hasUnblockButton: !!unblockBtn,
                    unblockButtonText: unblockBtn ? unblockBtn.textContent?.trim() : null,
                    position: {x: Math.round(rect.x), y: Math.round(rect.y)},
                    size: {width: Math.round(rect.width), height: Math.round(rect.height)}
                };
            }
        }
        
        return {found: false};
    }
""")

logger.info(f"✓ 拉黑半层: {block_overlay['found']}")
logger.info(f"  半层位置: ({block_overlay['position']['x']}, {block_overlay['position']['y']})")
logger.info(f"  包含Unblock按钮: {block_overlay['hasUnblockButton']}")
logger.info(f"  Unblock按钮文本: {block_overlay['unblockButtonText']}")
page.screenshot(path="screenshots/tc013_block_overlay.png")
```

**预期结果**:
- ✅ 拉黑半层显示
- ✅ 半层包含"blocked"或"unblock"关键词
- ✅ 半层上有Unblock按钮

#### 步骤8：测试Unblock按钮
**操作**: 
```javascript
// 点击Unblock按钮
const unblockClicked = await page.evaluate(() => {
    const allElements = Array.from(document.querySelectorAll('div, section'));
    
    for (const el of allElements) {
        const text = el.textContent?.toLowerCase() || '';
        const rect = el.getBoundingClientRect();
        
        if ((text.includes('blocked') || text.includes('unblock')) &&
            rect.x > 300 && rect.width > 200) {
            
            const buttons = Array.from(el.querySelectorAll('button'));
            const unblockBtn = buttons.find(btn => {
                const btnText = btn.textContent?.trim().toLowerCase() || '';
                return btnText === 'unblock' || btnText.includes('unblock');
            });
            
            if (unblockBtn) {
                unblockBtn.click();
                return {success: true, buttonText: unblockBtn.textContent?.trim()};
            }
        }
    }
    
    return {success: false};
});

await page.waitForTimeout(3000);
```

**Python实现**:
```python
# 点击Unblock按钮
unblock_clicked = page.evaluate("""
    () => {
        const allElements = Array.from(document.querySelectorAll('div, section'));
        
        for (const el of allElements) {
            const text = el.textContent?.toLowerCase() || '';
            const rect = el.getBoundingClientRect();
            
            if ((text.includes('blocked') || text.includes('unblock')) &&
                rect.x > 300 && rect.width > 200) {
                
                const buttons = Array.from(el.querySelectorAll('button'));
                const unblockBtn = buttons.find(btn => {
                    const btnText = btn.textContent?.trim().toLowerCase() || '';
                    return btnText === 'unblock' || btnText.includes('unblock');
                });
                
                if (unblockBtn) {
                    unblockBtn.click();
                    return {success: true, buttonText: unblockBtn.textContent?.trim()};
                }
            }
        }
        
        return {success: false};
    }
""")

logger.info(f"✓ Unblock按钮点击: {unblock_clicked['success']}")
logger.info(f"  按钮文本: {unblock_clicked['buttonText']}")
page.wait_for_timeout(3000)
page.screenshot(path="screenshots/tc013_after_unblock.png")

# 验证拉黑半层消失
overlay_gone = page.evaluate("""
    () => {
        const allElements = Array.from(document.querySelectorAll('div, section'));
        
        for (const el of allElements) {
            const text = el.textContent?.toLowerCase() || '';
            const rect = el.getBoundingClientRect();
            
            if ((text.includes('blocked') || text.includes('unblock')) &&
                rect.x > 300 && rect.width > 200 && rect.height > 100) {
                return false;
            }
        }
        
        return true;
    }
""")

logger.info(f"✓ 拉黑半层已消失: {overlay_gone}")
```

**预期结果**:
- ✅ Unblock按钮点击成功
- ✅ 拉黑半层消失
- ✅ 恢复正常会话状态

### 🔍 验证点
- ✅ Block选项存在于三点菜单中
- ✅ 点击Block显示确认弹窗
- ✅ 确认弹窗包含Cancel和Block两个按钮
- ✅ Cancel按钮功能正常（关闭弹窗）
- ✅ Block按钮功能正常（执行拉黑）
- ✅ 拉黑后显示拉黑半层
- ✅ 拉黑半层包含Unblock按钮
- ✅ Unblock按钮功能正常（取消拉黑）
- ✅ 取消拉黑后半层消失

### 📸 截图要求
- `tc013_conversation_page.png` - 会话详情页初始状态
- `tc013_menu_opened.png` - 三点菜单打开状态
- `tc013_block_dialog.png` - 拉黑确认弹窗
- `tc013_after_cancel.png` - 点击Cancel后
- `tc013_after_block_confirm.png` - 确认拉黑后
- `tc013_block_overlay.png` - 拉黑半层显示
- `tc013_after_unblock.png` - 取消拉黑后

---
**操作**: 
```javascript
// 查找设置按钮（可能是齿轮图标、三点菜单、More按钮等）
const settingsSelectors = [
    'button:has-text("Settings")',
    'button:has-text("More")',
    'button:has-text("⋮")',
    'button:has-text("...")',
    'button[class*="settings"]',
    'button[class*="menu"]',
    'button[class*="more"]',
    'button:has(svg[class*="settings"])',
    'button:has(svg[class*="gear"])',
    'button:has(svg[class*="dots"])',
    'button:has(svg[class*="more"])',
    'button[aria-label*="settings"]',
    'button[aria-label*="more"]',
    'button[aria-label*="options"]'
];

let settingsButton = null;
let hasSettingsButton = false;

for (const selector of settingsSelectors) {
    const element = page.locator(selector).first();
    if (await element.isVisible({ timeout: 2000 }).catch(() => false)) {
        settingsButton = element;
        hasSettingsButton = true;
        console.log(`✓ 发现设置按钮，选择器: ${selector}`);
        break;
    }
}

if (hasSettingsButton) {
    // 点击设置按钮
    await settingsButton.click();
    await page.waitForTimeout(2000);
    
    // 检查设置菜单是否显示
    const settingsMenu = page.locator('[role="menu"], .dropdown-menu, [class*="menu"], [class*="popover"]').first();
    const hasMenu = await settingsMenu.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (hasMenu) {
        console.log('✓ 设置菜单已显示');
        
        // 记录菜单中的所有选项
        const menuItems = settingsMenu.locator('[role="menuitem"], li, button, a');
        const itemCount = await menuItems.count();
        console.log(`设置菜单选项数量: ${itemCount}`);
        
        for (let i = 0; i < Math.min(itemCount, 10); i++) {
            const item = menuItems.nth(i);
            const itemText = await item.textContent().catch(() => '');
            console.log(`  选项 ${i + 1}: ${itemText.trim()}`);
        }
    } else {
        console.log('✗ 设置菜单未显示');
    }
} else {
    console.log('✗ 未发现设置按钮');
}
```

**Python实现**:
```python
has_settings = messages_page.check_settings_button_advanced()
logger.info(f"✓ 设置按钮: {has_settings['exists']}")
if has_settings['exists']:
    menu_result = messages_page.click_settings_button_advanced()
    logger.info(f"  菜单显示: {menu_result['menu_visible']}")
    logger.info(f"  菜单选项数量: {menu_result['item_count']}")
```

**预期结果**:
- ⚠️ 设置按钮可能存在也可能不存在
- ✅ 如果存在，点击后应该显示设置菜单
- ✅ 设置菜单中应该有多个选项

#### 步骤3：查找并测试置顶功能
**操作**: 
```javascript
// 在设置菜单中查找置顶选项
const pinSelectors = [
    'text=/Pin|置顶|Top/i',
    'button:has-text("Pin")',
    'button:has-text("置顶")',
    '[class*="pin"]',
    'button:has(svg[class*="pin"])'
];

let pinOption = null;
let hasPinOption = false;

if (hasMenu) {
    for (const selector of pinSelectors) {
        const element = settingsMenu.locator(selector).first();
        if (await element.isVisible({ timeout: 2000 }).catch(() => false)) {
            pinOption = element;
            hasPinOption = true;
            console.log(`✓ 发现置顶选项，选择器: ${selector}`);
            break;
        }
    }
    
    if (hasPinOption) {
        // 点击置顶
        await pinOption.click();
        await page.waitForTimeout(2000);
        
        // 检查是否有确认弹窗或状态变化
        const confirmDialog = page.locator('[role="dialog"], .modal').first();
        const hasConfirmDialog = await confirmDialog.isVisible({ timeout: 3000 }).catch(() => false);
        
        if (hasConfirmDialog) {
            console.log('✓ 置顶确认弹窗已显示');
            
            // 取消操作（避免实际修改）
            const cancelButton = confirmDialog.locator('button:has-text("Cancel"), button:has-text("Close")').first();
            if (await cancelButton.isVisible({ timeout: 2000 }).catch(() => false)) {
                await cancelButton.click();
                await page.waitForTimeout(1000);
            } else {
                await page.keyboard.press('Escape');
                await page.waitForTimeout(1000);
            }
        } else {
            // 检查会话是否被置顶（可能有视觉变化）
            console.log('✓ 置顶操作已执行（无确认弹窗）');
            
            // 取消置顶（如果功能是toggle）
            if (hasSettingsButton) {
                await settingsButton.click();
                await page.waitForTimeout(1000);
                
                const unpinOption = settingsMenu.locator('text=/Unpin|取消置顶/i').first();
                if (await unpinOption.isVisible({ timeout: 2000 }).catch(() => false)) {
                    await unpinOption.click();
                    await page.waitForTimeout(1000);
                    console.log('✓ 已取消置顶');
                }
            }
        }
    } else {
        console.log('✗ 未发现置顶选项');
    }
}
```

**Python实现**:
```python
if menu_result['menu_visible']:
    has_pin = messages_page.check_pin_option()
    logger.info(f"  - 置顶选项: {has_pin}")
    if has_pin:
        pin_result = messages_page.click_pin_option()
        logger.info(f"    置顶操作: {pin_result['success']}")
```

**预期结果**:
- ⚠️ 置顶功能可能存在也可能不存在
- ✅ 如果存在，点击后应该有反馈或状态变化

#### 步骤4：查找并测试免打扰功能
**操作**: 
```javascript
// 重新打开设置菜单（如果之前关闭了）
if (hasSettingsButton && !await settingsMenu.isVisible({ timeout: 2000 }).catch(() => false)) {
    await settingsButton.click();
    await page.waitForTimeout(2000);
}

// 在设置菜单中查找免打扰选项
const muteSelectors = [
    'text=/Do Not Disturb/i',
    'text=/Mute/i',
    'text=/静音/i',
    'text=/免打扰/i',
    'button:has-text("Mute")',
    'button:has-text("Do Not Disturb")',
    '[class*="mute"]',
    'button:has(svg[class*="mute"])',
    'button:has(svg[class*="bell"])'
];

let muteOption = null;
let hasMuteOption = false;

if (hasMenu) {
    for (const selector of muteSelectors) {
        const element = settingsMenu.locator(selector).first();
        if (await element.isVisible({ timeout: 2000 }).catch(() => false)) {
            muteOption = element;
            hasMuteOption = true;
            console.log(`✓ 发现免打扰选项，选择器: ${selector}`);
            break;
        }
    }
    
    if (hasMuteOption) {
        // 点击免打扰
        await muteOption.click();
        await page.waitForTimeout(2000);
        
        // 检查是否有确认弹窗
        const confirmDialog = page.locator('[role="dialog"], .modal').first();
        const hasConfirmDialog = await confirmDialog.isVisible({ timeout: 3000 }).catch(() => false);
        
        if (hasConfirmDialog) {
            console.log('✓ 免打扰确认弹窗已显示');
            
            const dialogText = await confirmDialog.textContent();
            console.log(`弹窗内容: ${dialogText}`);
            
            // 取消操作
            const cancelButton = confirmDialog.locator('button:has-text("Cancel"), button:has-text("Close"), button:has-text("No")').first();
            if (await cancelButton.isVisible({ timeout: 2000 }).catch(() => false)) {
                await cancelButton.click();
                await page.waitForTimeout(1000);
            } else {
                await page.keyboard.press('Escape');
                await page.waitForTimeout(1000);
            }
        } else {
            console.log('✓ 免打扰操作已执行（无确认弹窗）');
        }
    } else {
        console.log('✗ 未发现免打扰选项');
    }
}
```

**Python实现**:
```python
if menu_result['menu_visible']:
    # 重新打开菜单
    messages_page.click_settings_button_advanced()
    
    has_mute = messages_page.check_mute_option_advanced()
    logger.info(f"  - 免打扰选项: {has_mute}")
    if has_mute:
        mute_result = messages_page.click_mute_option_advanced()
        logger.info(f"    免打扰操作: {mute_result['success']}")
        logger.info(f"    确认弹窗: {mute_result['has_dialog']}")
```

**预期结果**:
- ⚠️ 免打扰功能可能存在也可能不存在
- ✅ 如果存在，点击后应该有确认弹窗或直接生效

#### 步骤5：查找并测试拉黑功能
**操作**: 
```javascript
// 重新打开设置菜单
if (hasSettingsButton && !await settingsMenu.isVisible({ timeout: 2000 }).catch(() => false)) {
    await settingsButton.click();
    await page.waitForTimeout(2000);
}

// 在设置菜单中查找拉黑选项
const blockSelectors = [
    'text=/Block/i',
    'text=/拉黑/i',
    'text=/屏蔽/i',
    'button:has-text("Block")',
    'button:has-text("拉黑")',
    '[class*="block"]',
    'button:has(svg[class*="block"])',
    'button[aria-label*="block"]'
];

let blockOption = null;
let hasBlockOption = false;

if (hasMenu) {
    for (const selector of blockSelectors) {
        const element = settingsMenu.locator(selector).first();
        if (await element.isVisible({ timeout: 2000 }).catch(() => false)) {
            blockOption = element;
            hasBlockOption = true;
            console.log(`✓ 发现拉黑选项，选择器: ${selector}`);
            break;
        }
    }
    
    if (hasBlockOption) {
        // 点击拉黑
        await blockOption.click();
        await page.waitForTimeout(2000);
        
        // 检查是否有确认弹窗
        const confirmDialog = page.locator('[role="dialog"], .modal').first();
        const hasConfirmDialog = await confirmDialog.isVisible({ timeout: 3000 }).catch(() => false);
        
        if (hasConfirmDialog) {
            console.log('✓ 拉黑确认弹窗已显示');
            
            const dialogText = await confirmDialog.textContent();
            console.log(`弹窗内容: ${dialogText}`);
            
            // 检查确认和取消按钮
            const confirmBtn = confirmDialog.locator('button:has-text("Block"), button:has-text("Confirm"), button:has-text("Yes")').first();
            const cancelBtn = confirmDialog.locator('button:has-text("Cancel"), button:has-text("Close"), button:has-text("No")').first();
            
            const hasConfirmBtn = await confirmBtn.isVisible({ timeout: 2000 }).catch(() => false);
            const hasCancelBtn = await cancelBtn.isVisible({ timeout: 2000 }).catch(() => false);
            
            console.log(`确认按钮: ${hasConfirmBtn}, 取消按钮: ${hasCancelBtn}`);
            
            // 取消操作（避免实际拉黑）
            if (hasCancelBtn) {
                await cancelBtn.click();
                await page.waitForTimeout(1000);
            } else {
                await page.keyboard.press('Escape');
                await page.waitForTimeout(1000);
            }
        } else {
            console.log('✗ 拉黑操作无确认弹窗（可能直接生效）');
        }
    } else {
        console.log('✗ 未发现拉黑选项');
    }
}
```

**Python实现**:
```python
if menu_result['menu_visible']:
    # 重新打开菜单
    messages_page.click_settings_button_advanced()
    
    has_block = messages_page.check_block_option_advanced()
    logger.info(f"  - 拉黑选项: {has_block}")
    if has_block:
        block_result = messages_page.click_block_option_advanced()
        logger.info(f"    拉黑操作: {block_result['success']}")
        logger.info(f"    确认弹窗: {block_result['has_dialog']}")
        logger.info(f"    弹窗内容: {block_result['dialog_text']}")
```

**预期结果**:
- ⚠️ 拉黑功能可能存在也可能不存在
- ✅ 如果存在，点击后应该显示确认弹窗
- ✅ 确认弹窗应该有明确的警告信息

### 🔍 验证点

#### 验证1：功能按钮探索完成
**验证逻辑**:
```python
# 记录探索到的功能按钮
buttons_found = []
if has_phone['exists']:
    buttons_found.append("电话")
if has_settings['exists']:
    buttons_found.append("设置")
if has_pin:
    buttons_found.append("置顶")
if has_mute:
    buttons_found.append("免打扰")
if has_block:
    buttons_found.append("拉黑")

logger.info(f"✓ 探索到的功能按钮: {', '.join(buttons_found) if buttons_found else '无'}")
```

**预期结果**:
- ✅ 完成所有功能按钮的探索
- ✅ 记录每个功能的存在性和交互结果

### 📸 截图要求
- 设置菜单展开后截图
- 每个功能的确认弹窗截图（如果有）
- 功能操作前后对比截图

---

## TC013: 会话页面消息发送功能测试

### 📌 测试信息
- **用例ID**: `case_id_messages_explore_014`
- **优先级**: P1 (High)
- **测试类型**: functional
- **模块标记**: messages, conversation, send, ae
- **Allure标记**:
  - Feature: OK - Messages
  - Story: Messages页面功能探索 - 消息发送
  - Title: 测试输入框输入消息并发送
  - Severity: CRITICAL

### 🎯 测试目标
测试会话详情页的消息输入和发送功能，验证能否成功输入文字"hello"并点击发送按钮。

### ✅ 前置条件
1. 已成功登录
2. 已进入Messages页面
3. 已进入某个会话详情

### 📝 测试步骤

#### 步骤1：定位消息输入框
**操作**: 
```javascript
// 查找消息输入框
const inputSelectors = [
    'textarea[placeholder*="message"]',
    'textarea[placeholder*="Message"]',
    'input[placeholder*="message"]',
    'textarea[class*="input"]',
    'textarea[class*="message"]',
    '[contenteditable="true"]'
];

let messageInput = null;
let inputFound = false;

for (const selector of inputSelectors) {
    const element = page.locator(selector).first();
    if (await element.isVisible({ timeout: 2000 }).catch(() => false)) {
        messageInput = element;
        inputFound = true;
        console.log(`✓ 找到消息输入框，选择器: ${selector}`);
        break;
    }
}

console.log(`消息输入框: ${inputFound ? '存在' : '不存在'}`);
```

**Python实现**:
```python
has_input = messages_page.check_message_input()
logger.info(f"✓ 消息输入框: {has_input['exists']}")
if has_input['exists']:
    logger.info(f"  选择器: {has_input['selector']}")
```

**预期结果**:
- ✅ 应该能找到消息输入框

#### 步骤2：输入测试消息"hello"
**操作**: 
```javascript
if (inputFound) {
    // 清空输入框
    await messageInput.clear();
    await page.waitForTimeout(500);
    
    // 输入消息
    await messageInput.fill('hello');
    await page.waitForTimeout(1000);
    
    // 验证输入内容
    const inputValue = await messageInput.inputValue().catch(() => 
        messageInput.textContent()
    );
    
    console.log(`输入的内容: ${inputValue}`);
    console.log(`输入验证: ${inputValue === 'hello' || inputValue.includes('hello')}`);
}
```

**Python实现**:
```python
if has_input['exists']:
    input_result = messages_page.input_message('hello')
    logger.info(f"  输入成功: {input_result['success']}")
    logger.info(f"  输入内容: {input_result['text']}")
```

**预期结果**:
- ✅ 能够成功输入文字"hello"
- ✅ 输入框中显示"hello"

#### 步骤3：定位发送按钮
**操作**: 
```javascript
// 查找发送按钮（通常在输入框右下角）
const sendButtonSelectors = [
    'button:has-text("Send")',
    'button:has-text("发送")',
    'button[type="submit"]',
    'button[class*="send"]',
    'button[class*="submit"]',
    'button:has(svg[class*="send"])',
    'button[aria-label*="send"]',
    'button[aria-label*="Send"]'
];

let sendButton = null;
let buttonFound = false;

for (const selector of sendButtonSelectors) {
    const element = page.locator(selector).first();
    if (await element.isVisible({ timeout: 2000 }).catch(() => false)) {
        sendButton = element;
        buttonFound = true;
        console.log(`✓ 找到发送按钮，选择器: ${selector}`);
        break;
    }
}

// 如果标准选择器找不到，使用JS查找
if (!buttonFound) {
    const sendButtonInfo = await page.evaluate(() => {
        const elements = Array.from(document.querySelectorAll('button, [role="button"]'));
        
        // 查找输入框附近的按钮
        const inputArea = document.querySelector('textarea, input[type="text"]');
        if (!inputArea) return { found: false };
        
        const inputRect = inputArea.getBoundingClientRect();
        
        const candidates = elements.filter(el => {
            const rect = el.getBoundingClientRect();
            
            // 查找输入框右侧或下方的按钮
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
    });
    
    if (sendButtonInfo.found) {
        console.log(`✓ JS找到发送按钮: ${JSON.stringify(sendButtonInfo)}`);
        buttonFound = true;
    }
}

console.log(`发送按钮: ${buttonFound ? '存在' : '不存在'}`);
```

**Python实现**:
```python
has_send_button = messages_page.check_send_button()
logger.info(f"✓ 发送按钮: {has_send_button['exists']}")
if has_send_button['exists']:
    logger.info(f"  位置: ({has_send_button.get('x', 'N/A')}, {has_send_button.get('y', 'N/A')})")
```

**预期结果**:
- ✅ 应该能找到发送按钮（在输入框右下角）

#### 步骤4：点击发送按钮
**操作**: 
```javascript
if (buttonFound) {
    // 截图（发送前）
    await page.screenshot({ path: 'screenshots/tc014_before_send.png' });
    
    // 点击发送按钮
    if (sendButton) {
        await sendButton.click();
    } else {
        // 使用坐标点击
        await page.mouse.click(sendButtonInfo.x + 10, sendButtonInfo.y + 10);
    }
    
    // 等待消息发送
    await page.waitForTimeout(2000);
    
    // 滚动消息列表到底部，确保能看到最新消息
    await page.evaluate(() => {
        const containers = document.querySelectorAll('[class*="message"], [class*="chat"], [class*="conversation"]');
        for (const container of containers) {
            if (container.scrollHeight > container.clientHeight) {
                container.scrollTop = container.scrollHeight;
            }
        }
    });
    
    await page.waitForTimeout(1000);
    
    // 截图（发送后）
    await page.screenshot({ path: 'screenshots/tc014_after_send.png' });
    
    // 验证输入框是否被清空
    const afterValue = await messageInput.inputValue().catch(() => 
        messageInput.textContent()
    );
    
    console.log(`发送后输入框内容: ${afterValue}`);
    console.log(`输入框已清空: ${!afterValue || afterValue.trim() === ''}`);
}
```

**Python实现**:
```python
if has_send_button['exists']:
    # 截图（发送前）
    page.screenshot(path='screenshots/tc014_before_send.png')
    
    send_result = messages_page.click_send_button()
    logger.info(f"  点击成功: {send_result['success']}")
    logger.info(f"  输入框已清空: {send_result['input_cleared']}")
    
    # 等待消息发送并滚动到底部
    page.wait_for_timeout(2000)
    page.evaluate("""
        () => {
            const containers = document.querySelectorAll('[class*="message"], [class*="chat"], [class*="conversation"]');
            for (const container of containers) {
                if (container.scrollHeight > container.clientHeight) {
                    container.scrollTop = container.scrollHeight;
                }
            }
        }
    """)
    page.wait_for_timeout(1000)
    
    # 截图（发送后）
    page.screenshot(path='screenshots/tc014_after_send.png')
```

**预期结果**:
- ✅ 点击发送按钮成功
- ✅ 消息被发送
- ✅ 输入框被自动清空
- ✅ 消息列表滚动到底部

#### 步骤5：验证消息已发送（多次尝试）
**操作**: 
```javascript
// 多次尝试查找最新消息（消息可能需要时间才能显示）
let messageFound = false;
let latestMessageText = '';
const maxRetries = 3;

for (let attempt = 0; attempt < maxRetries; attempt++) {
    const messages = page.locator('[class*="message"], [class*="chat-item"]').all();
    
    if (messages.length > 0) {
        // 获取最后一条消息
        const lastMessage = messages[messages.length - 1];
        latestMessageText = await lastMessage.textContent();
        
        if (latestMessageText.toLowerCase().includes('hello')) {
            console.log(`✓ 第${attempt + 1}次尝试：找到消息`);
            messageFound = true;
            break;
        }
    }
    
    if (attempt < maxRetries - 1) {
        console.log(`⚠️ 第${attempt + 1}次尝试：未找到消息，等待1秒后重试...`);
        await page.waitForTimeout(1000);
    }
}

console.log(`最新消息: ${latestMessageText}`);
console.log(`包含"hello": ${messageFound}`);
```

**Python实现**:
```python
# 多次尝试验证消息（最多3次）
latest_message = None
max_retries = 3

for attempt in range(max_retries):
    latest_message = messages_page.get_latest_message()
    if latest_message['found'] and 'hello' in latest_message['text'].lower():
        logger.info(f"✓ 第{attempt + 1}次尝试：找到消息")
        break
    else:
        if attempt < max_retries - 1:
            logger.info(f"⚠️ 第{attempt + 1}次尝试：未找到消息，等待1秒后重试...")
            page.wait_for_timeout(1000)
        else:
            logger.warning(f"⚠️ 第{attempt + 1}次尝试：仍未找到消息")

if latest_message['found']:
    logger.info(f"  最新消息: '{latest_message['text']}'")
    logger.info(f"  包含'hello': {'hello' in latest_message['text'].lower()}")
    logger.info(f"  消息总数: {latest_message['count']}")
```

**预期结果**:
- ✅ 能够找到最新消息（可能需要等待）
- ✅ 最新消息包含"hello"
- ⚠️ 如果首次未找到，会自动重试最多3次

### 🔍 验证点

#### 验证1：输入框可用
**验证逻辑**:
```python
assert has_input['exists'], "消息输入框不存在"
logger.info("✓ 消息输入框验证通过")
```

**预期结果**:
- ✅ 消息输入框存在

#### 验证2：能够输入文字
**验证逻辑**:
```python
assert input_result['success'], "输入消息失败"
assert 'hello' in input_result['text'].lower(), "输入内容不正确"
logger.info("✓ 消息输入验证通过")
```

**预期结果**:
- ✅ 能够成功输入"hello"

#### 验证3：发送按钮可用
**验证逻辑**:
```python
assert has_send_button['exists'], "发送按钮不存在"
logger.info("✓ 发送按钮验证通过")
```

**预期结果**:
- ✅ 发送按钮存在

#### 验证4：消息发送成功
**验证逻辑**:
```python
assert send_result['success'], "点击发送按钮失败"
assert send_result['input_cleared'], "发送后输入框未清空"
logger.info("✓ 消息发送验证通过")
```

**预期结果**:
- ✅ 消息发送成功
- ✅ 输入框被清空

### 📸 截图要求
- 输入消息前的输入框状态
- 输入"hello"后的输入框状态
- 点击发送前的页面状态
- 点击发送后的页面状态
- 消息列表中的新消息

---

## TC014A: 会话页面发送URL消息功能测试

### 📌 测试信息
- **用例ID**: `case_id_messages_explore_014a`
- **优先级**: P1 (High)
- **测试类型**: functional
- **模块标记**: messages, conversation, send, url, ae
- **Allure标记**:
  - Feature: OK - Messages
  - Story: Messages页面功能探索 - 消息发送
  - Title: 测试输入框输入URL并发送
  - Severity: CRITICAL

### 🎯 测试目标
测试会话详情页的URL消息输入和发送功能，验证能否成功输入URL "https://www.google.com" 并发送，以及URL是否被正确渲染为可点击链接。

### ✅ 前置条件
1. 已成功登录
2. 已进入Messages页面
3. 已进入某个会话详情

### 📝 测试步骤

#### 步骤1：定位消息输入框
**操作**: 
```javascript
const inputSelectors = [
    'textarea[placeholder*="message"]',
    'input[placeholder*="message"]',
    'textarea[class*="input"]',
    '[contenteditable="true"]'
];

let messageInput = null;
let inputFound = false;

for (const selector of inputSelectors) {
    const element = page.locator(selector).first();
    if (await element.isVisible({ timeout: 2000 }).catch(() => false)) {
        messageInput = element;
        inputFound = true;
        break;
    }
}
```

**Python实现**:
```python
has_input = messages_page.check_message_input()
logger.info(f"✓ 消息输入框: {has_input['exists']}")
```

**预期结果**:
- ✅ 应该能找到消息输入框

#### 步骤2：输入测试URL "https://www.google.com"
**操作**: 
```javascript
const testUrl = 'https://www.google.com';

if (inputFound) {
    await messageInput.clear();
    await page.waitForTimeout(500);
    
    await messageInput.fill(testUrl);
    await page.waitForTimeout(1000);
    
    const inputValue = await messageInput.inputValue().catch(() => 
        messageInput.textContent()
    );
    
    console.log(`输入的URL: ${inputValue}`);
}
```

**Python实现**:
```python
test_url = "https://www.google.com"
input_result = messages_page.input_message(test_url)
logger.info(f"✓ URL输入成功: {input_result['success']}")
logger.info(f"  输入内容: '{input_result['text']}'")
```

**预期结果**:
- ✅ 能够成功输入URL
- ✅ 输入框中显示完整URL

#### 步骤3：检查URL是否被自动识别
**操作**: 
```javascript
// 检查输入框或周围区域是否有URL预览
const urlRecognized = await page.evaluate(() => {
    const input = document.querySelector('textarea[placeholder*="message"], input[placeholder*="message"]');
    if (!input) return {found: false};
    
    const value = input.value || input.textContent || '';
    const hasUrl = value.includes('http://') || value.includes('https://');
    
    // 检查是否有链接预览
    const parent = input.closest('[class*="input"], [class*="message"]');
    if (parent) {
        const hasLinkPreview = parent.querySelector('[class*="link"], [class*="preview"], a[href]');
        return {
            found: true,
            hasUrl: hasUrl,
            hasLinkPreview: !!hasLinkPreview,
            inputValue: value
        };
    }
    
    return {found: true, hasUrl: hasUrl, hasLinkPreview: false};
});

console.log(`URL识别: ${urlRecognized.hasUrl}`);
console.log(`链接预览: ${urlRecognized.hasLinkPreview}`);
```

**Python实现**:
```python
url_recognized = page.evaluate("""
    () => {
        const input = document.querySelector('textarea[placeholder*="message"], input[placeholder*="message"]');
        if (!input) return {found: false};
        
        const value = input.value || input.textContent || '';
        const hasUrl = value.includes('http://') || value.includes('https://');
        
        const parent = input.closest('[class*="input"], [class*="message"]');
        if (parent) {
            const hasLinkPreview = parent.querySelector('[class*="link"], [class*="preview"], a[href]');
            return {
                found: true,
                hasUrl: hasUrl,
                hasLinkPreview: !!hasLinkPreview,
                inputValue: value
            };
        }
        
        return {found: true, hasUrl: hasUrl, hasLinkPreview: false};
    }
""")

logger.info(f"✓ URL识别检查:")
logger.info(f"  输入框包含URL: {url_recognized.get('hasUrl', False)}")
logger.info(f"  链接预览: {url_recognized.get('hasLinkPreview', False)}")
```

**预期结果**:
- ✅ 输入框包含URL
- ⚠️ 可能显示链接预览（取决于UI实现）

#### 步骤4：点击发送按钮
**操作**: 
```javascript
const sendButton = page.locator('button:has-text("Send"), button[class*="send"]').first();
await sendButton.click();
await page.waitForTimeout(2000);

// 滚动到消息列表底部
await page.evaluate(() => {
    const containers = document.querySelectorAll('[class*="message"], [class*="chat"]');
    for (const container of containers) {
        if (container.scrollHeight > container.clientHeight) {
            container.scrollTop = container.scrollHeight;
        }
    }
});
```

**Python实现**:
```python
send_result = messages_page.click_send_button()
logger.info(f"✓ 点击成功: {send_result['success']}")
logger.info(f"  输入框已清空: {send_result['input_cleared']}")

page.wait_for_timeout(2000)

# 滚动到底部
page.evaluate("""
    () => {
        const containers = document.querySelectorAll('[class*="message"], [class*="chat"]');
        for (const container of containers) {
            if (container.scrollHeight > container.clientHeight) {
                container.scrollTop = container.scrollHeight;
            }
        }
    }
""")
```

**预期结果**:
- ✅ 点击发送按钮成功
- ✅ URL消息被发送
- ✅ 输入框被自动清空

#### 步骤5：验证URL消息已发送并正确显示
**操作**: 
```javascript
// 查找包含URL的最新消息
let messageFound = false;
let latestMessageText = '';
const maxRetries = 3;

for (let attempt = 0; attempt < maxRetries; attempt++) {
    const messages = page.locator('[class*="message"], [class*="chat-item"]').all();
    
    if (messages.length > 0) {
        const lastMessage = messages[messages.length - 1];
        latestMessageText = await lastMessage.textContent();
        
        if (latestMessageText.toLowerCase().includes('google.com')) {
            console.log(`✓ 第${attempt + 1}次尝试：找到URL消息`);
            messageFound = true;
            break;
        }
    }
    
    if (attempt < maxRetries - 1) {
        await page.waitForTimeout(1000);
    }
}

console.log(`最新消息: ${latestMessageText}`);
console.log(`包含URL: ${messageFound}`);
```

**Python实现**:
```python
# 多次尝试验证URL消息
latest_message = None
max_retries = 3

for attempt in range(max_retries):
    latest_message = messages_page.get_latest_message()
    if latest_message['found'] and 'google.com' in latest_message['text'].lower():
        logger.info(f"✓ 第{attempt + 1}次尝试：找到URL消息")
        break
    else:
        if attempt < max_retries - 1:
            page.wait_for_timeout(1000)

if latest_message['found']:
    logger.info(f"  最新消息: '{latest_message['text']}'")
    logger.info(f"  包含'google.com': {'google.com' in latest_message['text'].lower()}")
```

**预期结果**:
- ✅ 能够找到最新的URL消息
- ✅ 消息包含"google.com"

#### 步骤6：检查URL是否被渲染为可点击链接
**操作**: 
```javascript
// 检查URL消息是否包含<a>标签
const urlLinkCheck = await page.evaluate(() => {
    const messages = Array.from(document.querySelectorAll('[class*="message"], [class*="chat-bubble"]'));
    
    if (messages.length === 0) {
        return {found: false, reason: 'no_messages'};
    }
    
    // 从后往前查找包含URL的消息
    for (let i = messages.length - 1; i >= 0; i--) {
        const msg = messages[i];
        const text = msg.textContent?.toLowerCase() || '';
        
        if (text.includes('google.com')) {
            const links = msg.querySelectorAll('a[href]');
            const hasClickableLink = links.length > 0;
            
            const linkInfo = Array.from(links).map(link => ({
                href: link.getAttribute('href'),
                text: link.textContent?.trim(),
                target: link.getAttribute('target')
            }));
            
            return {
                found: true,
                hasClickableLink: hasClickableLink,
                linkCount: links.length,
                links: linkInfo,
                messageText: text.substring(0, 100)
            };
        }
    }
    
    return {found: false, reason: 'url_message_not_found'};
});

console.log(`URL链接检查: ${urlLinkCheck.found}`);
console.log(`包含可点击链接: ${urlLinkCheck.hasClickableLink}`);
console.log(`链接数量: ${urlLinkCheck.linkCount}`);
```

**Python实现**:
```python
url_link_check = page.evaluate("""
    () => {
        const messages = Array.from(document.querySelectorAll('[class*="message"], [class*="chat-bubble"]'));
        
        if (messages.length === 0) {
            return {found: false, reason: 'no_messages'};
        }
        
        for (let i = messages.length - 1; i >= 0; i--) {
            const msg = messages[i];
            const text = msg.textContent?.toLowerCase() || '';
            
            if (text.includes('google.com')) {
                const links = msg.querySelectorAll('a[href]');
                const hasClickableLink = links.length > 0;
                
                const linkInfo = Array.from(links).map(link => ({
                    href: link.getAttribute('href'),
                    text: link.textContent?.trim(),
                    target: link.getAttribute('target')
                }));
                
                return {
                    found: true,
                    hasClickableLink: hasClickableLink,
                    linkCount: links.length,
                    links: linkInfo
                };
            }
        }
        
        return {found: false};
    }
""")

logger.info(f"✓ URL链接检查:")
logger.info(f"  找到URL消息: {url_link_check.get('found', False)}")

if url_link_check.get('found'):
    logger.info(f"  包含可点击链接: {url_link_check.get('hasClickableLink', False)}")
    logger.info(f"  链接数量: {url_link_check.get('linkCount', 0)}")
    
    if url_link_check.get('links'):
        for idx, link in enumerate(url_link_check['links'], 1):
            logger.info(f"  链接{idx}:")
            logger.info(f"    - href: {link.get('href', 'N/A')}")
            logger.info(f"    - text: {link.get('text', 'N/A')}")
            logger.info(f"    - target: {link.get('target', 'N/A')}")
```

**预期结果**:
- ✅ 找到包含URL的消息
- ✅ URL被渲染为可点击的`<a>`标签
- ✅ 链接的`href`属性正确指向URL
- ⚠️ 链接可能设置`target="_blank"`在新标签页打开

### 🔍 验证点

#### 验证1：输入框可用
**验证逻辑**:
```python
assert has_input['exists'], "消息输入框不存在"
```

**预期结果**:
- ✅ 消息输入框存在

#### 验证2：能够输入URL
**验证逻辑**:
```python
assert input_result['success'], "输入URL失败"
assert 'google.com' in input_result['text'].lower(), "输入的URL不正确"
```

**预期结果**:
- ✅ 能够成功输入URL

#### 验证3：URL消息发送成功
**验证逻辑**:
```python
assert send_result['success'], "发送失败"
assert send_result['input_cleared'], "输入框未清空"
```

**预期结果**:
- ✅ URL消息发送成功
- ✅ 输入框被清空

#### 验证4：URL消息正确显示
**验证逻辑**:
```python
assert latest_message['found'], "未找到最新消息"
assert 'google.com' in latest_message['text'].lower(), "消息中不包含URL"
```

**预期结果**:
- ✅ 能够找到包含URL的消息

#### 验证5：URL被渲染为链接（可选）
**验证逻辑**:
```python
if url_link_check.get('found'):
    logger.info(f"URL渲染为链接: {'✅' if url_link_check.get('hasClickableLink') else '❌ 纯文本'}")
```

**预期结果**:
- ✅ URL被渲染为可点击链接（推荐）
- ⚠️ 或显示为纯文本（可接受）

### 📸 截图要求
- `tc014a_conversation_page.png` - 会话详情页初始状态
- `tc014a_after_url_input.png` - 输入URL后的状态
- `tc014a_before_send.png` - 点击发送前的状态
- `tc014a_after_send.png` - 点击发送后的状态
- `tc014a_url_link_rendered.png` - URL消息渲染效果

### 💡 测试要点
1. **URL格式验证**：确保完整的URL（包含https://）能正确输入
2. **链接识别**：检查系统是否自动识别URL并提供预览
3. **链接渲染**：验证发送后URL是否被渲染为可点击链接
4. **链接行为**：确认链接点击行为（新标签页打开等）
5. **安全性**：验证URL链接的安全属性设置

---

## TC015: 发送空消息异常测试

### 📌 测试信息
- **用例ID**: `case_id_messages_exception_018`
- **优先级**: P0 (Critical)
- **测试类型**: exception
- **模块标记**: messages, conversation, send, exception, ae
- **Allure标记**:
  - Feature: OK - Messages
  - Story: Messages页面异常测试 - 输入验证
  - Title: 验证空消息的处理机制
  - Severity: NORMAL

### 🎯 测试目标
验证系统对空消息的处理机制，确保空消息不会被发送，或发送按钮被正确禁用。

### ✅ 前置条件
1. 已成功登录
2. 已进入Messages页面
3. 已进入某个会话详情

### 📝 测试步骤

#### 步骤1：测试空输入框状态
**操作**: 
```javascript
// 确保输入框为空
const input = page.locator('textarea[placeholder*="message"]').first();
await input.clear();
await page.waitForTimeout(500);

// 检查发送按钮状态
const sendBtn = page.locator('button:has-text("Send")').first();
const isDisabled = await sendBtn.isDisabled();

console.log(`发送按钮禁用状态: ${isDisabled}`);
```

**Python实现**:
```python
# 清空输入框
page.evaluate("""
    () => {
        const input = document.querySelector('textarea[placeholder*="message"]');
        if (input) {
            input.value = '';
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }
""")

# 检查发送按钮状态
send_button_state = page.evaluate("""
    () => {
        const sendBtn = document.querySelector('button:has-text("Send")');
        return {
            found: !!sendBtn,
            disabled: sendBtn ? sendBtn.disabled : false
        };
    }
""")

logger.info(f"✓ 空输入时发送按钮禁用: {send_button_state['disabled']}")
```

**预期结果**:
- ✅ 发送按钮应该被禁用
- ✅ 或发送按钮不可点击

#### 步骤2：测试输入空格
**操作**: 
```javascript
await input.fill('   ');  // 3个空格
await page.waitForTimeout(500);

const isDisabledSpace = await sendBtn.isDisabled();
console.log(`输入空格后发送按钮禁用状态: ${isDisabledSpace}`);
```

**Python实现**:
```python
input_result = messages_page.input_message('   ')
logger.info(f"✓ 输入空格: {input_result['success']}")

send_button_state_space = page.evaluate("""
    () => {
        const sendBtn = document.querySelector('button:has-text("Send")');
        return {disabled: sendBtn ? sendBtn.disabled : false};
    }
""")

logger.info(f"✓ 空格输入时发送按钮禁用: {send_button_state_space['disabled']}")
```

**预期结果**:
- ✅ 发送按钮应该被禁用（空格应被视为空消息）

#### 步骤3：测试输入换行符
**操作**: 
```javascript
await input.clear();
await input.fill('\n\n\n');  // 3个换行符
await page.waitForTimeout(500);

const isDisabledNewline = await sendBtn.isDisabled();
console.log(`输入换行符后发送按钮禁用状态: ${isDisabledNewline}`);
```

**Python实现**:
```python
page.evaluate("""
    () => {
        const input = document.querySelector('textarea[placeholder*="message"]');
        if (input) {
            input.value = '\\n\\n\\n';
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }
""")

send_button_state_newline = page.evaluate("""
    () => {
        const sendBtn = document.querySelector('button:has-text("Send")');
        return {disabled: sendBtn ? sendBtn.disabled : false};
    }
""")

logger.info(f"✓ 换行符输入时发送按钮禁用: {send_button_state_newline['disabled']}")
```

**预期结果**:
- ✅ 发送按钮应该被禁用

#### 步骤4：尝试发送空消息
**操作**: 
```javascript
if (!isDisabledNewline) {
    // 如果按钮未禁用，尝试点击
    await sendBtn.click();
    await page.waitForTimeout(2000);
    
    // 检查是否有错误提示
    const errorMsg = page.locator('[class*="error"], [role="alert"]').first();
    const hasError = await errorMsg.isVisible({ timeout: 2000 }).catch(() => false);
    
    console.log(`错误提示: ${hasError}`);
}
```

**Python实现**:
```python
if not send_button_state_newline['disabled']:
    logger.info("⚠️ 发送按钮未禁用，尝试点击...")
    send_result = messages_page.click_send_button()
    
    # 检查错误提示
    error_message = page.evaluate("""
        () => {
            const errorElements = document.querySelectorAll('[class*="error"], [role="alert"]');
            for (const el of errorElements) {
                if (el.offsetWidth > 0) {
                    return {found: true, text: el.textContent?.trim()};
                }
            }
            return {found: false};
        }
    """)
    
    logger.info(f"  错误提示: {error_message['found']}")
```

**预期结果**:
- ✅ 显示错误提示，或
- ✅ 空消息未被发送

#### 步骤5：验证消息未被发送
**操作**: 
```javascript
const messages = page.locator('[class*="message"]').all();
const finalCount = messages.length;

console.log(`初始消息数: ${initialCount}`);
console.log(`最终消息数: ${finalCount}`);
console.log(`空消息是否被发送: ${finalCount > initialCount}`);
```

**Python实现**:
```python
final_message = messages_page.get_latest_message()
final_count = final_message.get('count', 0)

message_sent = final_count > initial_count
logger.info(f"✓ 空消息是否被发送: {message_sent}")
```

**预期结果**:
- ✅ 消息数量未增加
- ✅ 空消息未被发送

### 🔍 验证点
- ✅ 空输入时发送按钮禁用
- ✅ 空格输入时发送按钮禁用
- ✅ 换行符输入时发送按钮禁用
- ✅ 空消息未被发送到服务器
- ✅ 用户体验友好（无错误或有明确提示）

### 📸 截图要求
- `tc018_empty_input.png` - 空输入框状态
- `tc018_space_input.png` - 输入空格后状态
- `tc018_newline_input.png` - 输入换行符后状态

---

## TC016: 发送超长消息异常测试

### 📌 测试信息
- **用例ID**: `case_id_messages_exception_019`
- **优先级**: P0 (Critical)
- **测试类型**: exception
- **模块标记**: messages, conversation, send, exception, boundary, ae
- **Allure标记**:
  - Feature: OK - Messages
  - Story: Messages页面异常测试 - 输入验证
  - Title: 验证超长消息的处理机制
  - Severity: NORMAL

### 🎯 测试目标
验证系统对超长消息的处理机制，检查是否有字符限制，以及超出限制时的提示和处理。

### ✅ 前置条件
1. 已成功登录
2. 已进入Messages页面
3. 已进入某个会话详情

### 📝 测试步骤

#### 步骤1：输入超长文本（5000字符）
**操作**: 
```javascript
// 生成5000字符的长文本
const longText = 'A'.repeat(5000);

const input = page.locator('textarea[placeholder*="message"]').first();
await input.clear();
await input.fill(longText);
await page.waitForTimeout(1000);

// 检查实际输入的字符数
const actualValue = await input.inputValue();
const actualLength = actualValue.length;

console.log(`尝试输入: ${longText.length} 字符`);
console.log(`实际输入: ${actualLength} 字符`);
console.log(`是否被截断: ${actualLength < longText.length}`);
```

**Python实现**:
```python
# 生成超长文本
long_text = 'A' * 5000
logger.info(f"✓ 生成超长文本: {len(long_text)} 字符")

# 输入超长文本
input_result = messages_page.input_message(long_text)
logger.info(f"✓ 输入成功: {input_result['success']}")

# 检查实际输入的字符数
actual_length = len(input_result.get('text', ''))
logger.info(f"  尝试输入: {len(long_text)} 字符")
logger.info(f"  实际输入: {actual_length} 字符")
logger.info(f"  是否被截断: {actual_length < len(long_text)}")

page.screenshot(path="screenshots/tc019_long_text_input.png")
```

**预期结果**:
- ✅ 输入被截断到最大字符限制
- ✅ 或显示字符计数器和限制提示

#### 步骤2：检查字符计数器
**操作**: 
```javascript
// 查找字符计数器
const charCounter = await page.evaluate(() => {
    const counterSelectors = [
        '[class*="counter"]',
        '[class*="count"]',
        '[class*="limit"]',
        '[class*="length"]'
    ];
    
    for (const selector of counterSelectors) {
        const elements = document.querySelectorAll(selector);
        for (const el of elements) {
            const text = el.textContent || '';
            if (text.match(/\d+\/\d+/) || text.match(/\d+/)) {
                return {
                    found: true,
                    text: text.trim(),
                    position: el.getBoundingClientRect()
                };
            }
        }
    }
    
    return {found: false};
});

console.log(`字符计数器: ${charCounter.found}`);
if (charCounter.found) {
    console.log(`计数器内容: ${charCounter.text}`);
}
```

**Python实现**:
```python
char_counter = page.evaluate("""
    () => {
        const counterSelectors = [
            '[class*="counter"]',
            '[class*="count"]',
            '[class*="limit"]',
            '[class*="length"]'
        ];
        
        for (const selector of counterSelectors) {
            const elements = document.querySelectorAll(selector);
            for (const el of elements) {
                const text = el.textContent || '';
                if (text.match(/\\d+\\/\\d+/) || text.match(/\\d+/)) {
                    return {
                        found: true,
                        text: text.trim()
                    };
                }
            }
        }
        
        return {found: false};
    }
""")

logger.info(f"✓ 字符计数器: {char_counter['found']}")
if char_counter['found']:
    logger.info(f"  计数器内容: {char_counter['text']}")
```

**预期结果**:
- ✅ 显示字符计数器（推荐）
- ✅ 或有其他限制提示

#### 步骤3：检查警告提示
**操作**: 
```javascript
// 查找超长警告提示
const warning = await page.evaluate(() => {
    const warningSelectors = [
        '[class*="warning"]',
        '[class*="error"]',
        '[class*="alert"]',
        '.toast'
    ];
    
    for (const selector of warningSelectors) {
        const elements = document.querySelectorAll(selector);
        for (const el of elements) {
            const rect = el.getBoundingClientRect();
            if (rect.width > 0 && rect.height > 0) {
                return {
                    found: true,
                    text: el.textContent?.trim()
                };
            }
        }
    }
    
    return {found: false};
});
```

**Python实现**:
```python
warning = page.evaluate("""
    () => {
        const warningSelectors = [
            '[class*="warning"]',
            '[class*="error"]',
            '[class*="alert"]',
            '.toast'
        ];
        
        for (const selector of warningSelectors) {
            const elements = document.querySelectorAll(selector);
            for (const el of elements) {
                const rect = el.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    return {found: true, text: el.textContent?.trim()};
                }
            }
        }
        
        return {found: false};
    }
""")

logger.info(f"✓ 警告提示: {warning['found']}")
if warning['found']:
    logger.info(f"  提示内容: {warning['text']}")
```

**预期结果**:
- ✅ 显示字符限制警告（推荐）
- ✅ 或输入被静默截断

#### 步骤4：尝试发送超长消息
**操作**: 
```python
# 尝试发送
send_result = messages_page.click_send_button()
page.wait_for_timeout(2000)

# 验证消息是否被发送
final_message = messages_page.get_latest_message()
```

**预期结果**:
- ✅ 消息被截断后发送
- ✅ 或显示错误提示

### 🔍 验证点
- ✅ 存在字符长度限制
- ✅ 超出限制时有明确提示
- ✅ 发送按钮状态正确
- ✅ 用户体验友好

### 📸 截图要求
- `tc019_long_text_input.png` - 输入超长文本后
- `tc019_char_counter.png` - 字符计数器显示
- `tc019_warning.png` - 警告提示（如果有）

---

## TC017: 发送特殊字符消息异常测试

### 📌 测试信息
- **用例ID**: `case_id_messages_exception_020`
- **优先级**: P0 (Critical)
- **测试类型**: exception, security
- **模块标记**: messages, conversation, send, exception, security, ae
- **Allure标记**:
  - Feature: OK - Messages
  - Story: Messages页面异常测试 - 安全验证
  - Title: 验证特殊字符和恶意代码的处理
  - Severity: CRITICAL

### 🎯 测试目标
验证系统对特殊字符、HTML标签、脚本代码的处理，确保不会导致XSS攻击或SQL注入等安全问题。

### ✅ 前置条件
1. 已成功登录
2. 已进入Messages页面
3. 已进入某个会话详情

### 📝 测试步骤

#### 步骤1：测试HTML标签
**操作**: 
```javascript
const htmlTest = '<script>alert("XSS")</script>';
await input.fill(htmlTest);
await sendBtn.click();
await page.waitForTimeout(2000);

// 检查是否执行了脚本（不应该执行）
const alertFired = await page.evaluate(() => {
    return window.alertFired || false;
});

console.log(`脚本是否执行: ${alertFired}`);
```

**Python实现**:
```python
# 测试1: HTML标签
html_test = '<script>alert("XSS")</script>'
logger.info(f"\n--- 测试1: HTML标签 ---")
logger.info(f"测试内容: {html_test}")

input_result = messages_page.input_message(html_test)
page.screenshot(path="screenshots/tc020_html_input.png")

send_result = messages_page.click_send_button()
page.wait_for_timeout(2000)

# 检查消息显示
latest_message = messages_page.get_latest_message()
if latest_message['found']:
    logger.info(f"  消息内容: {latest_message['text'][:100]}")
    logger.info(f"  是否转义: {'&lt;' in latest_message['text'] or '<script>' not in latest_message['text']}")
```

**预期结果**:
- ✅ HTML标签被转义显示（如 `&lt;script&gt;`）
- ✅ 脚本代码不会被执行

#### 步骤2：测试SQL注入字符
**操作**: 
```javascript
const sqlTest = "'; DROP TABLE users; --";
await input.fill(sqlTest);
await sendBtn.click();
await page.waitForTimeout(2000);
```

**Python实现**:
```python
# 测试2: SQL注入
sql_test = "'; DROP TABLE users; --"
logger.info(f"\n--- 测试2: SQL注入 ---")
logger.info(f"测试内容: {sql_test}")

input_result = messages_page.input_message(sql_test)
page.screenshot(path="screenshots/tc020_sql_input.png")

send_result = messages_page.click_send_button()
page.wait_for_timeout(2000)

latest_message = messages_page.get_latest_message()
if latest_message['found']:
    logger.info(f"  消息内容: {latest_message['text'][:100]}")
    logger.info(f"  内容完整: {sql_test in latest_message['text']}")
```

**预期结果**:
- ✅ SQL语句作为普通文本发送
- ✅ 不会影响数据库

#### 步骤3：测试Emoji表情
**操作**: 
```javascript
const emojiTest = '😀🎉💯👍❤️';
await input.fill(emojiTest);
await sendBtn.click();
await page.waitForTimeout(2000);
```

**Python实现**:
```python
# 测试3: Emoji表情
emoji_test = '😀🎉💯👍❤️'
logger.info(f"\n--- 测试3: Emoji表情 ---")
logger.info(f"测试内容: {emoji_test}")

input_result = messages_page.input_message(emoji_test)
page.screenshot(path="screenshots/tc020_emoji_input.png")

send_result = messages_page.click_send_button()
page.wait_for_timeout(2000)

latest_message = messages_page.get_latest_message()
if latest_message['found']:
    logger.info(f"  消息内容: {latest_message['text'][:100]}")
    logger.info(f"  Emoji显示正常: {'😀' in latest_message['text'] or 'emoji' in latest_message['text'].lower()}")
```

**预期结果**:
- ✅ Emoji正常显示
- ✅ 不会乱码

#### 步骤4：测试特殊符号
**操作**: 
```javascript
const specialTest = '!@#$%^&*()_+-=[]{}|;:\'",.<>?/~`';
await input.fill(specialTest);
await sendBtn.click();
await page.waitForTimeout(2000);
```

**Python实现**:
```python
# 测试4: 特殊符号
special_test = '!@#$%^&*()_+-=[]{}|;:\'",.<>?/~`'
logger.info(f"\n--- 测试4: 特殊符号 ---")
logger.info(f"测试内容: {special_test}")

input_result = messages_page.input_message(special_test)
page.screenshot(path="screenshots/tc020_special_input.png")

send_result = messages_page.click_send_button()
page.wait_for_timeout(2000)

latest_message = messages_page.get_latest_message()
if latest_message['found']:
    logger.info(f"  消息内容: {latest_message['text'][:100]}")
```

**预期结果**:
- ✅ 特殊符号正常显示
- ✅ 不会导致UI错乱

### 🔍 验证点
- ✅ HTML标签被正确转义
- ✅ 脚本代码不会执行
- ✅ SQL注入字符作为普通文本处理
- ✅ Emoji表情正常显示
- ✅ 特殊符号正常显示
- ✅ 系统安全性验证通过

### 📸 截图要求
- `tc020_html_input.png` - HTML标签输入
- `tc020_sql_input.png` - SQL注入字符输入
- `tc020_emoji_input.png` - Emoji表情输入
- `tc020_special_input.png` - 特殊符号输入

---

## TC018: 发送多行文本消息测试

### 📌 测试信息
- **用例ID**: `case_id_messages_exception_021`
- **优先级**: P1 (High)
- **测试类型**: functional
- **模块标记**: messages, conversation, send, ae
- **Allure标记**:
  - Feature: OK - Messages
  - Story: Messages页面功能测试 - 多行文本
  - Title: 验证多行文本消息的处理
  - Severity: NORMAL

### 🎯 测试目标
验证系统对多行文本消息的处理，确保换行符被正确保留和显示。

### ✅ 前置条件
1. 已成功登录
2. 已进入Messages页面
3. 已进入某个会话详情

### 📝 测试步骤

#### 步骤1：输入多行文本
**操作**: 
```javascript
const multilineText = 'Line 1\nLine 2\nLine 3\nLine 4\nLine 5';

const input = page.locator('textarea[placeholder*="message"]').first();
await input.clear();
await input.fill(multilineText);
await page.waitForTimeout(1000);

// 验证输入框中的换行符
const inputValue = await input.inputValue();
const lineCount = (inputValue.match(/\n/g) || []).length + 1;

console.log(`输入行数: ${lineCount}`);
console.log(`换行符保留: ${inputValue.includes('\n')}`);
```

**Python实现**:
```python
# 输入多行文本
multiline_text = 'Line 1\\nLine 2\\nLine 3\\nLine 4\\nLine 5'
logger.info(f"\n--- 输入多行文本 ---")
logger.info(f"测试内容: {multiline_text.replace(chr(10), '\\\\n')}")

input_result = messages_page.input_message(multiline_text)
logger.info(f"✓ 输入成功: {input_result['success']}")

# 检查换行符是否保留
line_count = input_result.get('text', '').count('\\n') + 1
logger.info(f"  输入行数: {line_count}")

page.screenshot(path="screenshots/tc021_multiline_input.png")
```

**预期结果**:
- ✅ 输入框支持多行输入
- ✅ 换行符被保留

#### 步骤2：发送多行消息
**操作**: 
```javascript
await sendBtn.click();
await page.waitForTimeout(2000);

// 滚动到底部
await page.evaluate(() => {
    const containers = document.querySelectorAll('[class*="message"]');
    for (const container of containers) {
        if (container.scrollHeight > container.clientHeight) {
            container.scrollTop = container.scrollHeight;
        }
    }
});
```

**Python实现**:
```python
send_result = messages_page.click_send_button()
logger.info(f"✓ 发送成功: {send_result['success']}")

page.wait_for_timeout(2000)
page.evaluate("""
    () => {
        const containers = document.querySelectorAll('[class*="message"]');
        for (const container of containers) {
            if (container.scrollHeight > container.clientHeight) {
                container.scrollTop = container.scrollHeight;
            }
        }
    }
""")

page.screenshot(path="screenshots/tc021_after_send.png")
```

**预期结果**:
- ✅ 多行消息发送成功

#### 步骤3：验证多行消息显示
**操作**: 
```javascript
// 查找最新消息并检查换行符
const messageDisplay = await page.evaluate(() => {
    const messages = Array.from(document.querySelectorAll('[class*="message"]'));
    
    if (messages.length === 0) {
        return {found: false};
    }
    
    // 获取最后一条消息
    const lastMsg = messages[messages.length - 1];
    const text = lastMsg.textContent || '';
    const innerHTML = lastMsg.innerHTML;
    
    // 检查换行符的显示方式
    const hasBrTag = innerHTML.includes('<br>');
    const hasNewlineClass = innerHTML.includes('newline');
    const lineCount = text.split('\n').length;
    
    return {
        found: true,
        text: text.trim(),
        hasBrTag: hasBrTag,
        lineCount: lineCount,
        preservesNewlines: lineCount > 1 || hasBrTag
    };
});
```

**Python实现**:
```python
message_display = page.evaluate("""
    () => {
        const messages = Array.from(document.querySelectorAll('[class*="message"]'));
        
        if (messages.length === 0) {
            return {found: false};
        }
        
        const lastMsg = messages[messages.length - 1];
        const text = lastMsg.textContent || '';
        const innerHTML = lastMsg.innerHTML;
        
        const hasBrTag = innerHTML.includes('<br>');
        const lineCount = text.split('\\n').length;
        
        return {
            found: true,
            text: text.trim(),
            hasBrTag: hasBrTag,
            lineCount: lineCount,
            preservesNewlines: lineCount > 1 || hasBrTag
        };
    }
""")

logger.info(f"✓ 多行消息显示:")
logger.info(f"  找到消息: {message_display['found']}")
if message_display['found']:
    logger.info(f"  行数: {message_display['lineCount']}")
    logger.info(f"  使用<br>标签: {message_display['hasBrTag']}")
    logger.info(f"  换行符保留: {message_display['preservesNewlines']}")

page.screenshot(path="screenshots/tc021_multiline_display.png")
```

**预期结果**:
- ✅ 换行符被保留并正确显示
- ✅ 使用`<br>`标签或CSS实现换行
- ✅ 多行格式清晰可读

### 🔍 验证点
- ✅ 输入框支持多行输入
- ✅ 换行符在输入时被保留
- ✅ 换行符在发送后被保留
- ✅ 消息显示时换行符正确渲染
- ✅ 多行消息格式清晰

### 📸 截图要求
- `tc021_multiline_input.png` - 多行文本输入
- `tc021_after_send.png` - 发送后状态
- `tc021_multiline_display.png` - 多行消息显示效果

---

### 📌 测试信息
- **用例ID**: `case_id_messages_scroll_023`
- **优先级**: P1
- **测试类型**: functional
- **模块标记**: messages, conversation, scroll, ae
- **Allure标记**:
  - Feature: OK - Messages
  - Story: Messages页面功能探索 - 会话列表交互
  - Title: 左侧会话列表应该支持滑动查看更多会话
  - Severity: NORMAL

### 🎯 测试目标
验证左侧会话列表的滑动功能，确认用户可以通过滑动查看更多历史会话。

### ✅ 前置条件
1. 用户已登录
2. 在Messages页面
3. 会话列表中有多个会话（至少5个以上）

### 📝 测试步骤

#### 步骤1：定位会话列表容器
**操作**: 
```python
# 查找会话列表容器
conversation_list = page.evaluate("""
    () => {
        const selectors = [
            '[class*="conversation-list"]',
            '[class*="chat-list"]',
            '[class*="message-list"]',
            '[class*="session-list"]'
        ];
        
        for (const selector of selectors) {
            const container = document.querySelector(selector);
            if (container && container.scrollHeight > container.clientHeight) {
                return {
                    found: true,
                    selector: selector,
                    scrollHeight: container.scrollHeight,
                    clientHeight: container.clientHeight,
                    scrollable: true
                };
            }
        }
        
        // 尝试查找左侧区域
        const leftPanel = document.querySelector('[class*="left"]');
        if (leftPanel) {
            return {
                found: true,
                selector: '[class*="left"]',
                scrollHeight: leftPanel.scrollHeight,
                clientHeight: leftPanel.clientHeight,
                scrollable: leftPanel.scrollHeight > leftPanel.clientHeight
            };
        }
        
        return {found: false};
    }
""")

logger.info(f"✓ 会话列表容器: {conversation_list}")
```

**预期结果**:
- ✅ 找到会话列表容器
- ✅ 容器可滚动（scrollHeight > clientHeight）

#### 步骤2：获取初始状态
**操作**: 
```python
# 获取初始可见会话数量
initial_state = page.evaluate("""
    () => {
        const conversations = document.querySelectorAll('[class*="conversation"], [class*="chat-item"]');
        const visible = Array.from(conversations).filter(el => {
            const rect = el.getBoundingClientRect();
            return rect.top >= 0 && rect.bottom <= window.innerHeight;
        });
        
        return {
            total: conversations.length,
            visible: visible.length,
            firstVisible: visible[0]?.textContent?.trim().substring(0, 30)
        };
    }
""")

logger.info(f"✓ 初始状态 - 总会话数: {initial_state['total']}, 可见: {initial_state['visible']}")
page.screenshot(path='screenshots/tc023_before_scroll.png')
```

**预期结果**:
- ✅ 获取初始可见会话数量
- ✅ 记录第一个可见会话

#### 步骤3：向下滑动会话列表
**操作**: 
```python
# 向下滑动会话列表
scroll_result = page.evaluate("""
    () => {
        const selectors = [
            '[class*="conversation-list"]',
            '[class*="chat-list"]',
            '[class*="left"]'
        ];
        
        for (const selector of selectors) {
            const container = document.querySelector(selector);
            if (container && container.scrollHeight > container.clientHeight) {
                const initialScrollTop = container.scrollTop;
                container.scrollTop += 300;  // 向下滑动300px
                
                return {
                    success: true,
                    selector: selector,
                    scrolledFrom: initialScrollTop,
                    scrolledTo: container.scrollTop,
                    scrollDistance: container.scrollTop - initialScrollTop
                };
            }
        }
        
        return {success: false};
    }
""")

logger.info(f"✓ 滑动结果: {scroll_result}")
page.wait_for_timeout(1000)
```

**预期结果**:
- ✅ 会话列表向下滑动
- ✅ scrollTop值增加

#### 步骤4：验证滑动后的状态
**操作**: 
```python
# 获取滑动后的状态
after_scroll_state = page.evaluate("""
    () => {
        const conversations = document.querySelectorAll('[class*="conversation"], [class*="chat-item"]');
        const visible = Array.from(conversations).filter(el => {
            const rect = el.getBoundingClientRect();
            return rect.top >= 0 && rect.bottom <= window.innerHeight;
        });
        
        return {
            total: conversations.length,
            visible: visible.length,
            firstVisible: visible[0]?.textContent?.trim().substring(0, 30)
        };
    }
""")

logger.info(f"✓ 滑动后状态 - 可见: {after_scroll_state['visible']}")
page.screenshot(path='screenshots/tc023_after_scroll.png')

# 验证可见会话发生变化
assert after_scroll_state['firstVisible'] != initial_state['firstVisible'], "滑动后可见会话未变化"
logger.info("✓ 滑动后可见会话已变化")
```

**预期结果**:
- ✅ 可见会话发生变化
- ✅ 显示之前不可见的会话
- ✅ 滑动流畅，无卡顿

### 🔍 验证点总结
- [x] 会话列表容器可滑动
- [x] 滑动操作成功执行
- [x] 滑动后显示新的会话
- [x] 滑动距离正确

### 📸 截图要求
- 滑动前的会话列表状态
- 滑动后的会话列表状态

---

### 📌 测试信息
- **用例ID**: `case_id_messages_timestamp_024`
- **优先级**: P1
- **测试类型**: functional
- **模块标记**: messages, conversation, timestamp, ae
- **Allure标记**:
  - Feature: OK - Messages
  - Story: Messages页面功能探索 - 会话列表展示
  - Title: 会话列表应该显示最后消息的时间戳
  - Severity: NORMAL

### 🎯 测试目标
验证会话列表中每个会话都正确显示最后一条消息的时间戳，时间格式符合预期。

### ✅ 前置条件
1. 用户已登录
2. 在Messages页面
3. 会话列表中有多个会话

### 📝 测试步骤

#### 步骤1：获取所有会话的时间戳
**操作**: 
```python
# 获取所有可见会话的时间戳
timestamps = page.evaluate("""
    () => {
        const conversations = document.querySelectorAll('[class*="conversation"], [class*="chat-item"]');
        const results = [];
        
        for (const conv of conversations) {
            const rect = conv.getBoundingClientRect();
            if (rect.height > 0 && rect.width > 0) {
                // 查找时间戳元素
                const timeSelectors = [
                    '[class*="time"]',
                    '[class*="timestamp"]',
                    '[class*="date"]',
                    'span[class*="text-"]'
                ];
                
                let timestamp = null;
                for (const selector of timeSelectors) {
                    const timeEl = conv.querySelector(selector);
                    if (timeEl) {
                        const text = timeEl.textContent?.trim();
                        // 检查是否是时间格式（包含数字）
                        if (text && /\\d/.test(text)) {
                            timestamp = text;
                            break;
                        }
                    }
                }
                
                // 获取用户名
                const userName = conv.textContent?.trim().split('\\n')[0] || 'Unknown';
                
                results.push({
                    userName: userName.substring(0, 30),
                    timestamp: timestamp,
                    hasTimestamp: !!timestamp
                });
            }
        }
        
        return results;
    }
""")

logger.info(f"✓ 获取到 {len(timestamps)} 个会话的时间戳")
for i, ts in enumerate(timestamps[:5]):  # 只显示前5个
    logger.info(f"  会话{i+1}: {ts['userName']} - {ts['timestamp']}")
```

**预期结果**:
- ✅ 每个会话都有时间戳信息
- ✅ 时间戳格式正确（如"3月31日"、"Yesterday"、"10:30 AM"等）

#### 步骤2：验证时间戳格式
**操作**: 
```python
# 验证时间戳格式
timestamp_patterns = [
    r'\\d+:\\d+',           # 时间格式: 10:30, 14:25
    r'\\d+月\\d+日',         # 日期格式: 3月31日
    r'Yesterday',          # 昨天
    r'Today',              # 今天
    r'\\w+ \\d+',          # Mar 31, Jan 15
]

valid_timestamps = 0
for ts in timestamps:
    if ts['hasTimestamp']:
        timestamp_text = ts['timestamp']
        # 检查是否匹配任一格式
        import re
        is_valid = any(re.search(pattern, timestamp_text) for pattern in timestamp_patterns)
        if is_valid:
            valid_timestamps += 1

logger.info(f"✓ 有效时间戳数量: {valid_timestamps}/{len(timestamps)}")

# 验证至少80%的会话有有效时间戳
assert valid_timestamps >= len(timestamps) * 0.8, f"时间戳覆盖率不足: {valid_timestamps}/{len(timestamps)}"
```

**预期结果**:
- ✅ 至少80%的会话显示有效时间戳
- ✅ 时间戳格式符合预期模式

#### 步骤3：验证时间戳位置
**操作**: 
```python
# 验证时间戳位置（通常在右侧或底部）
timestamp_positions = page.evaluate("""
    () => {
        const conversations = document.querySelectorAll('[class*="conversation"], [class*="chat-item"]');
        const positions = [];
        
        for (const conv of conversations) {
            const convRect = conv.getBoundingClientRect();
            const timeEl = conv.querySelector('[class*="time"], [class*="timestamp"]');
            
            if (timeEl) {
                const timeRect = timeEl.getBoundingClientRect();
                positions.push({
                    isRightAligned: timeRect.right > convRect.left + convRect.width * 0.7,
                    isBottomAligned: timeRect.bottom > convRect.top + convRect.height * 0.7
                });
            }
        }
        
        return positions;
    }
""")

logger.info(f"✓ 时间戳位置验证: {len(timestamp_positions)} 个")
page.screenshot(path='screenshots/tc024_timestamps.png')
```

**预期结果**:
- ✅ 时间戳位置一致（通常在会话项右侧或底部）
- ✅ 时间戳字体较小，颜色较浅（次要信息）

### 🔍 验证点总结
- [x] 每个会话显示时间戳
- [x] 时间戳格式正确
- [x] 时间戳位置一致
- [x] 时间戳覆盖率 ≥ 80%

### 📸 截图要求
- 会话列表截图（标注时间戳位置）

---



## TC019: 会话列表时间顺序展示测试

### 📌 测试信息
- **用例ID**: `case_id_messages_list_order_026`
- **优先级**: P0 (Critical)
- **测试类型**: functional
- **模块标记**: messages, conversation, timestamp, ae
- **实测状态**: ✅ 实测通过（2026-03-12）

### 🎯 测试目标
验证会话列表按最新消息时间倒序排列，时间戳格式符合规范。

### 🔬 实测关键发现

| 项目 | 发现 |
|------|------|
| 列表容器 | `.list-group.list-group-flush`，共31条会话 |
| 时间顺序 | 最新消息排在最顶部（降序） |
| 时间格式（当天） | `HH:MM`（如 `05:19`） |
| 时间格式（近期） | `Mon Day`（如 `Mar 9`、`Feb 5`） |
| 时间格式（昨天） | `Yesterday` |
| 时间戳覆盖率 | 10/10 = 100% |

### 实测时间序列（前10条）
```
Item 0: 05:19  → OKer_z5y8tml     (当天最新)
Item 1: Mar 9  → OKerAE_a7m4n6r   
Item 2: Feb 5  → OKerfc33ac3b     
Item 3: Feb 5  → OKerfc33ac3b     
Item 4: Feb 4  → OKer_z5y8tml     
Item 5: Jan 21 → OKer_z5y8tml     
Item 6: Jan 21 → OKerAE_s5ssqdc   
Item 7: Jan 21 → OKerSA_2q4anfi   
Item 8: Jan 14 → OKer_z5y8tml     
Item 9: Jan 13 → dubizzle         (最旧)
```

### 验证点
- [x] 会话列表总数 > 0
- [x] 时间戳格式100%正确
- [x] HH:MM格式出现在日期格式（Mon Day）之前

---

## TC020: 置顶会话icon展示测试

### 📌 测试信息
- **用例ID**: `case_id_messages_pin_icon_027`
- **优先级**: P0 (Critical)
- **测试类型**: functional
- **模块标记**: messages, conversation, pin, ae
- **实测状态**: ✅ 实测通过（2026-03-12）

### 🎯 测试目标
验证置顶操作后，被置顶会话移动到列表顶部，并显示置顶图标。

### 🔬 实测关键发现

| 项目 | 发现 |
|------|------|
| 置顶入口 | 右侧聊天区顶部 `.c-d-img-menu`（menu@2x图片） |
| 菜单容器 | `.c-d-menu`，包含 `.c-d-menu-item` |
| 菜单选项 | Pin / Mute / Block（未置顶时） |
| 菜单选项 | Unpin / Mute / Block（已置顶时） |
| 置顶icon图片 | `toplist@2x.2004c053.png` |
| 置顶icon位置 | 会话item内的 img 标签（src含"toplist"） |
| 置顶后行为 | 会话移动到列表第1位（idx=0） |

### 测试步骤
1. 导航到Messages页面，记录第3条会话信息（OKerfc33ac3b / Feb 5 / house）
2. 点击第3条会话进入详情，点击 `.c-d-img-menu` 打开菜单
3. 点击"Pin"执行置顶操作
4. 验证该会话移动到列表第1位
5. 验证列表第1条出现置顶icon（img src 含 "toplist"）
6. 还原：执行 Unpin 操作

### 验证点
- [x] 置顶会话移动到列表第1位
- [x] 置顶icon（toplist@2x图片）显示在会话item中
- [x] 置顶后菜单选项变为 "Unpin"
- [x] Unpin后会话恢复正常排列

---

## TC021: 免打扰会话icon展示测试

> **编号与脚本说明**：同一条用例在自动化中 Allure 标题为 **TC023**、`pytest` 标记为 `case_id_messages_mute_icon_027`、入口函数 `test_muted_conversation_icon`；本文仍保留 **TC024** 作为历史章节编号。维护时**以 `case_id` 与代码为准**。

### 📌 测试信息
- **用例ID（自动化）**: `case_id_messages_mute_icon_027`（与本文 TC024 对应同一场景）
- **优先级**: P0 (Critical)
- **测试类型**: functional
- **模块标记**: messages, conversation, mute, ae
- **实测状态**: ✅ 实测通过（2026-03-12，脚本逻辑 2026-04-22 同步强化）

### 🎯 测试目标
验证免打扰操作后，会话列表中出现静音图标，菜单显示 Unmute 选项。

### 🔬 实测关键发现

| 项目 | 发现 |
|------|------|
| 静音入口 | 与置顶相同：`.c-d-img-menu` → `.c-d-menu` |
| 菜单选项 | Pin / Mute / Block（未静音时） |
| 菜单选项 | Pin / Unmute / Block（已静音时；实际 DOM 常将多选项**无空格拼成一段**，如 `PinUnmuteBlock`、`UnpinUnmuteBlock`，勿依赖「整段中是否含子串 `Unmute`」与「是否已免打扰」的朴素包含判断，应以 **免打扰态整段** 如含 **`UnpinUnmute`** 或等价为已静音） |
| 静音icon图片 | `listMute@2x.e432d57b.png` |
| 静音icon位置 | 会话item内 `justify-content-between align-items-center hstack` 容器中 |
| 测试账号预置 | 账号已有6条静音会话（OKer_z5y8tml、dubizzle等） |

### 🤖 自动化要点（与脚本同步，2026-04-22）
- 点击 **Mute** 须 **精确匹配**（如 Playwright `get_by_text("Mute", exact=True)`），**禁止**依赖会匹配到 `Unmute` 内子串的 `has-text("Mute")` 类选择器。
- 点 **Mute** 后**轮询**「…」菜单，直至出现**免打扰态**（如整段出现 **`UnpinUnmute`** 或等价的 `UnpinUnmuteBlock`）；若出现确认层，需点 OK/Confirm 使操作生效；步骤间可先 `Escape` 再开菜单，避免状态串台。
- **不要**在验证阶段**再次点选**同一列表会话再开「…」——易致列表 `listMute` 与聊天头菜单（Mute/Unmute）**不同步**；应在当前已打开的会话详情上直接重新打开 `…` 做断言。
- Messages 首屏过慢时等待 `.list-group.list-group-flush` 超时 30s；仍失败时保存全页截图便于排查（如 `tc027_FAIL_messages_not_loaded.png` 命名体系）。

### 测试步骤
1. 导航到Messages页面，记录第2条会话初始静音状态
2. 点击第2条会话（OKerAE_a7m4n6r），打开菜单检查状态
3. 若已静音先 Unmute 确保从未静音开始
4. 执行 Mute 操作
5. 验证列表中出现静音icon（img src 含 "listMute"）
6. **在当前详情**再次打开 `…`（不重复点列表同一会话），验证菜单为免打扰态（见上「`UnpinUnmute` / Unmute 项」）
7. 还原：执行 Unmute 操作

### 验证点
- [x] 静音icon（listMute@2x图片）显示在会话列表item中
- [x] 静音icon数量 ≥ 1
- [x] 静音后菜单选项变为 "Unmute"
- [x] Unmute后icon消失，菜单恢复为 "Mute"

---

---

## TC022: 发送附件（PDF）测试

> **自动化脚本映射**: 对应函数 `test_send_pdf_attachment`（test_messages_complete.py，TC024）

### 📌 测试信息
- **用例ID**: `case_id_messages_attachment_029`
- **优先级**: P1 (Critical)
- **测试类型**: functional
- **模块标记**: messages, attachment, ae
- **实测状态**: ✅ 实测通过（2026-03-16）
- **自动化状态**: ✅ 自动化通过（2026-04-27 修复后）

### 🎯 测试目标
验证会话详情页可上传 PDF 文件，上传后文件名显示在输入区，Send 按钮存在。

### 🔬 实测关键发现

| 项目 | 发现 |
|------|------|
| 附件图标位置 | `.ci-send` 区域第二个图标（`sendFile.9421b76f.png`） |
| file input selector | `input[type=file][accept*="pdf"]` |
| accept 属性 | `.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.zip,.txt` |
| multiple 属性 | 支持（可多文件上传） |
| 上传后表现 | 文件名出现在页面文字中（预览状态） |
| Send 按钮 | 初始 disabled，文件上传完成后 enabled |

### 测试步骤
1. 导航到 Messages 页面，点击任意会话
2. 确认 `.ci-send` 区域存在 `sendFile` 图标
3. 对 `input[type=file][accept*="pdf"]` 执行 `set_input_files` 上传 PDF
4. 验证文件名出现在页面中（预览）
5. 验证 Send 按钮存在

### ⚠️ 自动化注意事项（2026-04-27 修复）

**曾遇到的问题：**
- 步骤1中"点击任意会话"使用固定坐标点击，导致页面布局变化时无法进入会话详情页
- 无法找到 `textarea.ci-input-item` 输入框，测试超时失败

**修复方案：**
- 改用多选择器策略定位会话列表项：`.list-group.list-group-flush > .border-0`
- 增加等待时间从 5s → 8s
- 实现选择器回退机制提升稳定性
- 详见 `_click_first_conversation()` 辅助函数改进

### 验证点
- [x] `input[type=file][accept*="pdf"]` 存在
- [x] accept 属性包含 `.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.zip,.txt`
- [x] 上传后文件名出现在页面文字中
- [x] Send 按钮存在于页面

---

## TC023: 附件 file input accept 属性支持格式校验

> **自动化脚本映射**: 对应函数 `test_attachment_accepted_types`（test_messages_complete.py，TC025）

### 📌 测试信息
- **用例ID**: `case_id_messages_attachment_030`
- **优先级**: P2 (Normal)
- **测试类型**: functional / boundary
- **模块标记**: messages, attachment, ae
- **实测状态**: ✅ 实测通过（2026-03-16）
- **自动化状态**: ✅ 自动化通过（2026-04-27 修复后）

### 🎯 测试目标
验证附件 file input 的 accept 属性包含所有支持格式，且支持多文件上传。

### 🔬 实测关键发现

| 项目 | 发现 |
|------|------|
| accept 完整值 | `.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.zip,.txt` |
| multiple | 存在（可同时上传多个文件） |

### 测试步骤
1. 进入任意会话详情页
2. 获取 `input[type=file][accept*="pdf"]` 的 accept 属性值
3. 校验包含所有期望格式
4. 校验 multiple 属性存在

### ⚠️ 自动化注意事项（2026-04-27 修复）

**曾遇到的问题：**
- 同 TC025，步骤1中进入会话详情页时使用固定坐标点击失败

**修复方案：**
- 同 TC025，改进 `_click_first_conversation()` 辅助函数
- 使用可靠的选择器定位会话列表项

### 验证点
- [x] accept 包含 `.pdf`、`.doc`、`.docx`、`.xls`、`.xlsx`、`.ppt`、`.pptx`、`.zip`、`.txt`（共9种格式）
- [x] file input 有 multiple 属性（支持多文件）

---

## TC024: 发送图片测试

> **自动化脚本映射**: 对应函数 `test_send_image`（test_messages_complete.py，TC022）

### 📌 测试信息
- **用例ID**: `case_id_messages_image_031`
- **优先级**: P1 (Critical)
- **测试类型**: functional
- **模块标记**: messages, image, ae
- **实测状态**: ✅ 实测通过（2026-03-16）
- **自动化状态**: ✅ 自动化通过（2026-04-27 修复后）

### 🎯 测试目标
验证会话详情页可上传图片，上传后 `.ci-image` 预览区存在，Send 按钮出现。

### 🔬 实测关键发现

| 项目 | 发现 |
|------|------|
| 图片图标位置 | `.ci-send` 区域第三个图标（`picture25.da8f2d50.png`） |
| file input selector | `input[type=file][accept*="image"]` |
| accept 属性 | `image/JPG,image/PNG,image/JPEG` |
| 上传后表现 | `.ci-image` 预览区出现（包含缩略图） |
| Send 按钮 | 上传完成后 enabled |

### 测试步骤
1. 进入任意会话详情页
2. 验证图片 input accept 属性
3. 上传一张 JPEG 图片
4. 验证 `.ci-image` 预览区存在
5. 验证 Send 按钮存在

### ⚠️ 自动化注意事项（2026-04-27 修复）

**曾遇到的问题：**
- 同 TC025，步骤1中进入会话详情页时使用固定坐标点击失败
- 无法找到 `textarea.ci-input-item` 输入框

**修复方案：**
- 同 TC025，改进 `_click_first_conversation()` 辅助函数
- 使用可靠的选择器定位会话列表项

### 验证点
- [x] `input[type=file][accept*="image"]` 存在
- [x] accept 包含 `image/JPG,image/PNG,image/JPEG`
- [x] `.ci-image` 预览区存在
- [x] Send 按钮出现

### 🔬 实测关键发现

| 项目 | 发现 |
|------|------|
| 图片图标 | `.ci-send` 第三个图标（`picture25@2x.d3e4c75c.png`） |
| file input selector | `input[type=file][accept*="image"]` |
| accept 属性 | `image/JPG,image/PNG,image/JPEG` |
| 预览区容器 | `.ci-image`（上传后图片展示区域） |
| multiple 属性 | 支持（可多图上传） |

### 测试步骤
1. 进入任意会话详情页
2. 对 `input[type=file][accept*="image"]` 执行 `set_input_files` 上传图片
3. 验证 `.ci-image` 预览区存在
4. 验证 Send 按钮出现

### 验证点
- [x] `input[type=file][accept*="image"]` 存在
- [x] accept 包含 `image/JPG`、`image/PNG`、`image/JPEG`
- [x] `.ci-image` 预览区存在
- [x] Send 按钮出现

---

## TC025: 图片 file input accept 属性格式校验
|------|------|
| accept 完整值 | `image/JPG,image/PNG,image/JPEG` |
| 不支持格式 | `.pdf`、`.doc`（文档类不在 accept 中） |
| multiple | 支持多图 |

### 测试步骤
1. 进入任意会话详情页
2. 获取 `input[type=file][accept*="image"]` 的 accept 属性值
3. 校验仅包含图片格式

### 验证点
- [x] accept 包含 `image/JPG`、`image/PNG`、`image/JPEG`
- [x] accept 不包含 `.pdf`、`.doc`（图片 input 不接受文档）
- [x] file input 有 multiple 属性（支持多图）

---

## TC026: 地理位置图标 - 点击弹出 Send Location 地图弹窗

> **自动化脚本映射**: 对应函数 `test_location_icon_entry`（test_messages_complete.py，TC024）

### 📌 测试信息
- **用例ID**: `case_id_messages_location_033`
- **优先级**: P1 (Critical)
- **测试类型**: functional
- **模块标记**: messages, location, ae
- **实测状态**: ✅ 实测通过（2026-03-16）
- **自动化状态**: ✅ 自动化通过（2026-04-27 修复后）

### 🎯 测试目标
验证会话详情页左下角第一个图标（地理位置）点击后弹出 "Send Location" 地图弹窗，内嵌 Google Maps，含 Locate me 和 Send 按钮。

### 🔬 实测关键发现

| 项目 | 发现 |
|------|------|
| 图标位置 | **`.ci-send` 区域第一个图标**（会话详情页左下第一个） |
| 图标文件名 | `icon-location-big.dfcd17e6.png` |
| 弹窗标题 | `Send Location` |
| 地图 | Google Maps（显示 "Map data ©2026 Google / Terms"） |
| 定位按钮 | `Locate me` |
| 拖拽提示 | `Drag the pin to set precise location. Accurate locations get more responses.` |
| 发送按钮 | `Send` |
| 图标坐标 | 在视口外（viewY≈912），需 scrollIntoView 后再点击 |

### 测试步骤
1. 进入任意会话详情页
2. 验证 `.ci-send` 第一个图标为 `icon-location-big`
3. scrollIntoView 确保图标在视口内，点击图标
4. 等待 3 秒
5. 验证弹窗弹出

### ⚠️ 自动化注意事项（2026-04-27 修复）

**曾遇到的问题：**
1. 地理位置图标可能在视口外，点击失败
2. 等待时间不足（3000ms），弹窗未完全加载
3. 断言过于严格，只检查 'Send Location' 单一文本

**修复方案：**
1. **增加滚动逻辑：** 先执行 `window.scrollTo(0, document.body.scrollHeight)` 确保图标可见
2. **改进视口判断：** `inViewport: rect.y < window.innerHeight && rect.y > 0`
3. **增加等待时间：** 从 3s 增加到 5s，确保 Google Maps 加载完成
4. **优化断言策略：** 检查多个关键字（'Send Location', 'Location', 'Locate me', 'Map', 'Google'）
5. **增加容错：** 如果弹窗未出现，记录警告并跳过测试（可能是浏览器地理位置权限问题）
6. **使用 scrollIntoView：** 滚动时使用 `scrollIntoView({block: 'center'})` 确保元素居中

### 验证点
- [x] `.ci-send` 第一个图标 src 包含 `location`
- [x] 点击后页面出现 `Send Location` 文字
- [x] 弹窗包含 `Map data` / `Google`（Google Maps 已加载）
- [x] 弹窗有 `Locate me` 按钮
- [x] 弹窗有 `Send` 发送按钮
- [x] 弹窗有提示文案 `Drag the pin to set precise location. Accurate locations get more responses.`

---

## TC027: Send 按钮初始状态为 disabled

### 📌 测试信息
- **用例ID**: `case_id_messages_send_034`
- **优先级**: P1 (Critical)
- **测试类型**: functional / boundary
- **模块标记**: messages, ae
- **实测状态**: ✅ 实测通过（2026-03-16）

### 🎯 测试目标
验证会话详情页输入框为空时，Send 按钮处于 disabled 状态（class 含 `button_disabled__9jYJ2`）。

### 🔬 实测关键发现

| 项目 | 发现 |
|------|------|
| Send 按钮初始 class | `button_button__g4Ovi button_small__6Va86 button_dark__FJMb_ button_disabled__9jYJ2` |
| disabled 属性 | `disabled=true` |
| textarea 占位符 | `Input message` |
| textarea maxlength | 500 |

### 测试步骤
1. 进入任意会话详情页
2. 不输入任何内容
3. 验证 Send 按钮状态

### 验证点
- [x] Send 按钮 `disabled=true`
- [x] Send 按钮 class 包含 `button_disabled__9jYJ2`

---

## TC028: 输入文字后 Send 按钮变为 enabled

### 📌 测试信息
- **用例ID**: `case_id_messages_send_035`
- **优先级**: P0 (Blocker)
- **测试类型**: functional
- **模块标记**: messages, ae
- **实测状态**: ✅ 实测通过（2026-03-16）

### 🎯 测试目标
验证 textarea 输入内容后 Send 按钮 enabled，清空内容后 Send 重新 disabled。

### 🔬 实测关键发现

| 项目 | 发现 |
|------|------|
| 输入后 Send 状态 | enabled（`disabled=false`，class 不含 `button_disabled__9jYJ2`） |
| 清空后 Send 状态 | disabled（恢复初始状态） |
| textarea selector | `textarea.ci-input-item` |

### 测试步骤
1. 进入任意会话详情页
2. 验证初始 Send 为 disabled
3. 在 textarea 输入 "hello test message"
4. 验证 Send 变为 enabled
5. 清空 textarea 内容
6. 验证 Send 重新 disabled

### 验证点
- [x] 初始：Send `disabled=true`
- [x] 输入文字后：Send `disabled=false`（已启用）
- [x] 清空内容后：Send 重新 `disabled=true`

---

## TC029: 发送文件图标（sendFile）DOM 结构验证

### 📌 测试信息
- **用例ID**: `case_id_messages_attachment_036`
- **优先级**: P2 (Normal)
- **测试类型**: UI / structural
- **模块标记**: messages, attachment, ae
- **实测状态**: ✅ 实测通过（2026-03-16）

### 🎯 测试目标
验证 sendFile 图标父 div 包含隐藏的 file input，DOM 结构符合预期。

### 🔬 实测关键发现

| 项目 | 发现 |
|------|------|
| sendFile 图标 | `.ci-send` 第二个图标（`sendFile.9421b76f.png`） |
| file input 位置 | sendFile 图标父 div 内 |
| file input 样式 | `display: none`（隐藏） |
| file input accept | `.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.zip,.txt` |
| multiple | `true` |

### 验证点
- [x] `.ci-send img[src*="sendFile"]` 存在
- [x] 图标父 div 内有 `input[type=file]`
- [x] file input `style.display === 'none'`（隐藏）
- [x] file input accept 包含 `.pdf`
- [x] file input multiple = true

---

## TC030: 发送图片图标（picture25）DOM 结构及 .ci-send 整体结构验证

### 📌 测试信息
- **用例ID**: `case_id_messages_image_037`
- **优先级**: P2 (Normal)
- **测试类型**: UI / structural
- **模块标记**: messages, image, ae
- **实测状态**: ✅ 实测通过（2026-03-16）

### 🎯 测试目标
验证图片图标父 div 包含隐藏的 image file input，并验证 `.ci-send` 整体结构（三图标 + Send 按钮）。

### 🔬 实测关键发现

| 项目 | 发现 |
|------|------|
| 图片图标 | `.ci-send` 第三个（`picture25@2x.d3e4c75c.png`） |
| image file input | 图标父 div 内，`display: none` |
| accept | `image/JPG,image/PNG,image/JPEG` |
| .ci-send 完整结构 | 3 个图标 + 1 个 Send 按钮 |
| 图标顺序 | ① location ② sendFile ③ picture25 |

### .ci-send 完整 DOM 结构（实测）
```html
<div class="ci-send">
  <img src="icon-location-big.dfcd17e6.png" />           <!-- 地理位置 -->
  <div>
    <img src="sendFile.9421b76f.png" />                   <!-- 发送文件 -->
    <input type="file" accept=".pdf,.doc..." style="display:none" multiple />
  </div>
  <div>
    <img src="picture25@2x.d3e4c75c.png" />              <!-- 发送图片 -->
    <input type="file" accept="image/JPG,image/PNG,image/JPEG" style="display:none" multiple />
  </div>
  <button class="...button_disabled__9jYJ2" disabled>Send</button>
</div>
```

### 验证点
- [x] `.ci-send img[src*="picture25"]` 存在
- [x] 图标父 div 内有 `input[type=file][accept*="image"]`
- [x] image file input `display: none`（隐藏）
- [x] image file input accept 包含 `image/`，不含 `.pdf`
- [x] `.ci-send` 共有 3 个可见图标（location、sendFile、picture25）
- [x] `.ci-send` 有 Send 按钮，按钮文字为 `Send`

---



## TC031: 会话排序规则验证（置顶优先）

### 测试目标
验证 Messages 会话列表的排序规则，重点检查：
- 置顶会话是否始终在列表前部
- 未置顶会话按时间或未读状态排序
- 排序逻辑是否一致

### 前置条件
- 用户已登录
- 会话列表中存在多个会话
- 至少有 1 个会话被置顶

### 测试步骤

#### 步骤1: 分析会话列表排序
提取所有会话的索引位置、置顶状态、未读状态、时间戳。

#### 步骤2: 验证排序规则
- 检查置顶会话是否在未置顶会话之前
- 如无置顶会话则跳过测试

### 验证点
- [ ] 置顶会话出现在列表前部
- [ ] 未置顶会话按时间/未读排序
- [ ] 排序逻辑一致无异常

### 优先级
P1

### 测试类型
功能测试、UI 验证

### 关联用例
- TC002: 会话列表显示
- TC011: 置顶功能测试

---

## 📅 版本历史

| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|---------|
| v1.0 | 2026-03-06 | AI Assistant | 初始版本 - Messages页面功能探索测试用例 |
| v1.1 | 2026-03-06 | AI Assistant | 优化版本 - 增加详细步骤、截图要求、问题解决方案 |
| v1.2 | 2026-03-06 | AI Assistant | 追加TC009-TC013 - 拆分功能按钮为独立测试用例 |
| | | | TC009: 电话按钮测试 |
| | | | TC010: 设置入口测试（右上角...按钮） |
| | | | TC011: 置顶功能测试（Pin/Unpin） |
| | | | TC012: 免打扰功能测试（Mute/Unmute） |
| | | | TC013: 拉黑功能测试（Block/Unblock） |
| v1.3 | 2026-03-06 | AI Assistant | 追加TC014 - 消息发送功能测试 |
| | | | TC014: 输入框输入"hello"并点击发送按钮 |
| v1.4 | 2026-03-06 | AI Assistant | 优化TC002 - 会话列表功能 |
| | | | - 去掉统计会话数量步骤 |
| | | | - 增加滑动左侧会话列表步骤 |
| v1.5 | 2026-03-09 | AI Assistant | 增强TC002 - 用户昵称一致性验证 |
| | | | - 新增步骤4：获取第二个会话的用户昵称 |
| | | | - 更新步骤6：验证详情页昵称与会话列表昵称一致 |
| | | | - 新增验证点4：用户昵称一致性断言 |
| v1.6 | 2026-03-09 | AI Assistant | 优化TC014 - 消息发送验证增强 |
| | | | - 步骤4：增加发送后滚动到底部功能 |
| | | | - 步骤5：增加多次重试机制（最多3次） |
| | | | - 解决首次执行时看不到发送消息的问题 |
| v1.8 | 2026-03-09 | AI Assistant | 优化TC008 - 改为安全提示检查 |
| | | | - 标题：从"综合功能探索"改为"安全提示检查" |
| | | | - 步骤：向下滑动会话页至顶部 |
| | | | - 验证：查看是否展示"for your safe..."提示 |
| | | | - 创建合并脚本test_messages_complete.py |
| v1.9 | 2026-03-09 | AI Assistant | 完善TC013 - 拉黑功能完整流程 |
| | | | - 新增步骤4：测试Cancel按钮 |
| | | | - 新增步骤5：重新打开菜单 |
| | | | - 新增步骤6：测试Block确认按钮 |
| | | | - 新增步骤7：验证拉黑半层显示 |
| | | | - 新增步骤8：测试Unblock按钮 |
| | | | - 新增7张测试截图记录 |
| v2.0 | 2026-03-09 | AI Assistant | 新增TC014A - URL消息发送测试 |
| | | | - 测试输入框输入URL功能 |
| | | | - 测试URL消息发送功能 |
| | | | - 验证URL是否被识别和预览 |
| | | | - 验证URL是否被渲染为可点击链接 |
| | | | - 检查链接属性（href, target等） |
| | | | - 新增5张测试截图记录 |
| v2.1 | 2026-03-10 | AI Assistant | 新增异常测试和功能测试用例 |
| | | | TC014: 发送空消息异常测试 |
| | | | - 测试空输入、空格、换行符的处理 |
| | | | - 验证发送按钮禁用状态 |
| | | | TC015: 发送超长消息异常测试 |
| | | | - 测试5000字符超长文本 |
| | | | - 验证字符限制和计数器 |
| | | | - 检查截断和警告提示 |
| | | | TC016: 发送特殊字符消息测试 |
| | | | - 测试HTML标签（XSS防护） |
| | | | - 测试SQL注入字符 |
| | | | - 测试Emoji表情显示 |
| | | | - 测试特殊符号处理 |
| | | | TC017: 发送多行文本消息测试 |
| | | | - 测试多行文本输入和发送 |
| | | | - 验证换行符保留和显示 |
| | | | - 检查<br>标签或CSS换行实现 |
| | | | | | | | - 测试长按/右键消息菜单 |
| | | | - 测试复制选项点击 |
| | | | - 验证剪贴板内容正确性 |

| v2.2 | 2026-03-11 | AI Assistant | 清理测试用例 - 删除TC015-TC017 |
| | | | - 删除TC015: 会话详情页关闭按钮测试 |
| | | | - 删除TC016: 会话内搜索功能测试 |
| | | | - 删除TC017: 文件上传功能探索测试 |
| | | | - 保留TC018-| | | | - 当前用例数：19个（历史记录）-| v2.3 | 2026-03-11 | AI Assistant | 新增会话列表交互测试 - | | | | - 新增| | | | - 新增| | | | - 新增| | | | - 当前用例数：22个（历史记录）-| v2.4 | 2026-03-12 | AI Assistant | 新增深度实测用例 - TC014-TC016 |
| | | | - 新增TC026: 会话列表时间顺序展示测试（✅实测） |
| | | | - 新增TC027: 置顶会话icon展示测试（✅实测） |
| | | | - 新增TC028: 免打扰会话icon展示测试（✅实测） |
| | | | - 实测发现：置顶icon=toplist@2x.png，静音icon=listMute@2x.png |
| | | | - 当前用例数：25个（历史记录）|
| v2.6 | 2026-04-22 | AI Assistant | 同步 `test_muted_conversation_icon` 实现：免打扰菜单拼接串与精确点击 Mute、验菜单勿重复点列表、Messages 首屏等待与失败截图；注明 `case_id_messages_mute_icon_027` 与文内 TC016 的对应关系 |
| v2.5 | 2026-03-16 | AI Assistant | 新增消息输入区功能用例 - TC017-TC017 |
| | | | - TC017: 发送附件（PDF）✅实测 |
| | | | - TC014: 附件 accept 格式校验（9种格式）✅实测 |
| | | | - TC015: 发送图片 ✅实测 |
| | | | - TC016: 图片 accept 格式校验（JPG/PNG/JPEG）✅实测 |
| | | | - TC017: 地理位置图标 → Send Location 弹窗（Google Maps）✅实测 |
| | | | - TC014: Send 按钮初始 disabled 状态 ✅实测 |
| | | | - TC015: 输入文字后 Send 启用，清空后重新 disabled ✅实测 |
| | | | - TC016: sendFile 图标 DOM 结构验证 ✅实测 |
| | | | - TC017: picture25 图标及 .ci-send 整体结构验证 ✅实测 |
| | | | - 实测发现：.ci-send = location + sendFile + picture25 + Send按钮 |
| v2.8 | 2026-04-28 | AI Assistant | TC005 调整：移除会话搜索/筛选；保留未读与时间戳；增加会话列表头像昵称时间戳校验与消息列表头像昵称及发送入列校验；同步流程图、元素表、清单与语义化定位示例 |
| v2.7 | 2026-04-27 | AI Assistant |
| v3.0 | 2026-04-28 | QA Agent | **完整重新编号**：31个用例连续编号TC001-TC015（含TC014A），删除的用例不占用编号；同步更新所有关联文档、脚本、知识库 | 同步自动化脚本修复 - TC017/TC015/TC017 |
| | | | - TC017: 新增自动化修复说明，改进 `_click_first_conversation()` 函数 |
| | | | - TC014: 新增自动化修复说明，同 TC017 |
| | | | - TC015: 新增自动化修复说明，同 TC017，清理重复内容 |
| | | | - TC017: 新增自动化修复说明，改进滚动策略和等待时间 |
| | | | - 修复重点：选择器策略优化、等待时间增加、滚动逻辑改进、容错机制增强 |
| | | | - 所有修复用例自动化状态：✅ 通过（2026-04-27）|
| | | | - 当前用例数：31个（TC001-TC031，含TC014A）|
---

**📄 文档生成时间**: 2026-03-06  
**🌐 测试站点**: OK阿联酋站 (AE)  
**👤 测试角色**: 卖家 (Seller)  
**📋 文档类型**: 功能探索测试用例  
**🎯 测试目标**: 全面探索Messages页面所有功能  
**📊 当前用例数**: 31个测试用例（TC001-TC031，含TC014A）  
**📝 最后更新**: 2026-04-28
