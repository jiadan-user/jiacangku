# 元素被遮挡处理指南（Sticky Header / Modal Overlay）

## 问题描述

点击操作超时，报错：

```
Locator.click: Timeout 30000ms exceeded.
... <div class="TopBar_topBarContent__NQD60"> ... intercepts pointer events
```

原因：目标元素在视窗中的位置被固定（sticky/fixed）的顶部导航栏、Modal 覆层或其他元素挡住，Playwright 的默认点击坐标落在遮挡元素上。

---

## 场景一：Sticky/Fixed 顶部导航栏遮挡

### 症状
- 页面存在固定在顶部的 `TopBar`、`Header`、`NavBar`；
- 目标元素（如下拉框触发器）在滚动到视窗中心时恰好被顶栏覆盖；
- 截图可以看到元素在页面中，但点击无效。

### 解决方案

```python
def _click_dropdown(self, label_text: str):
    """
    将目标元素滚入视窗，等待顶栏动画结束后再点击。
    适用于存在 sticky header 的页面中的下拉框、按钮等交互元素。

    DOM 结构示例（label 与触发器是同级兄弟节点）：
      <div class="field">          ← 字段容器
        <div>Experience *</div>    ← label（text= 找到这里）
        <div class="trigger">...</div>  ← following-sibling::div[1]（目标）
      </div>
    """
    # ✅ 正确：从 label 直接找它的下一个兄弟 div（触发器）
    trigger = (
        self.page.locator(f"text={label_text}")
        .locator("xpath=following-sibling::div[1]")
    )
    trigger.scroll_into_view_if_needed()
    self.page.wait_for_timeout(300)   # 等待顶栏遮挡动画结束
    trigger.click()
    self.page.wait_for_timeout(300)   # 等待下拉选项面板渲染
```

### ⚠️ XPath 路径陷阱：不要加 `.locator("..")`

**错误写法（曾经导致点击错误元素）**：

```python
# ❌ 多走了一层！
trigger = (
    self.page.locator(f"text={label_text}")
    .locator("..")                              # 上跳到字段容器
    .locator("xpath=following-sibling::div[1]") # 找容器的兄弟 → 下一个字段容器！
)
```

`.locator("..")` 会从 label 上跳到字段容器，然后 `following-sibling::div[1]` 找到的是**相邻字段的容器**（如 Education 容器），而不是 Experience 的触发器。

**正确路径**：直接从 label 找它的下一个兄弟节点，不需要跳到父级。

### 原理
1. `scroll_into_view_if_needed()` 让浏览器滚动到元素可见位置；
2. 第一个 `wait_for_timeout(300)` 给顶部导航栏的 CSS transition 留出时间；
3. `trigger.click()` 点击触发器打开下拉；
4. 第二个 `wait_for_timeout(300)` 等待选项面板渲染稳定后再进行后续操作。

### 适用位置
- Page Object 中任何「页面下方区域」的交互方法；
- 尤其是表单第二步及之后的字段（Experience、Education、Salary 等）。

---

## 场景二：Modal 弹窗覆层遮挡（intercepts pointer events）

### 症状
- 页面出现登录弹窗、确认弹窗后，主页面元素点击被 Modal 背景层拦截；
- 报错中遮挡元素是 Modal 的半透明遮罩（`backdrop`/`overlay`）。

### 解决方案

```python
# 等待 Modal 消失后再操作主页面
modal_overlay = page.locator("[class*='modal-backdrop'], [class*='overlay']")
if modal_overlay.is_visible():
    modal_overlay.wait_for(state="hidden", timeout=10000)

# 或者在 Modal 内操作，使用 Modal 容器定位
modal = page.locator("[role='dialog'][aria-modal='true']")
modal.wait_for(state="visible", timeout=10000)
modal.locator("button:has-text('Confirm')").click()
```

---

## 场景三：元素位于视窗边缘（scroll_into_view 不够）

### 症状
- `scroll_into_view_if_needed()` 已调用，但元素仍被遮挡；
- 通常出现在顶部 sticky 高度较大（> 60px）的页面。

### 解决方案：使用 JavaScript 精确滚动

```python
def _scroll_past_sticky(self, locator):
    """
    先滚入视窗，再用 JS 向上多滚 80px，绕过 sticky header 遮挡区域。
    """
    locator.scroll_into_view_if_needed()
    self.page.evaluate("window.scrollBy(0, -80)")
    self.page.wait_for_timeout(300)
    locator.click()
```

---

## 识别信号（CLI 录制时）

| 信号 | 可能原因 |
|------|----------|
| `intercepts pointer events` 报错 | Sticky header 或 Modal overlay 遮挡 |
| 元素在截图可见但点击超时 | 固定定位层覆盖了点击区域 |
| 点击后无响应，页面无变化 | 点击落在遮挡层上而非目标元素 |
| 仅在页面下方表单字段出现 | 顶部导航栏遮挡（页面顶部字段不受影响） |

## CLI 录制建议

录制时如遇上述情况，在记录该步骤时注明：
```
# 注意：此元素有 sticky header 遮挡风险，已用 scroll_into_view_if_needed + wait 处理
```

这样代码转换时可直接使用 `_click_dropdown` 模式，无需猜测。

---

## 场景四：弹窗内同名元素冲突（多匹配 / strict mode violation）

### 症状

```
Locator.click: Timeout 30000ms exceeded.
... <div class="ValidAccount__overlay"> ... intercepts pointer events
```

或：

```
strict mode violation: locator resolved to N elements
```

**原因**：页面主体与 Modal 弹窗中存在同名按钮/输入框，未限定容器时选择器命中多个元素。

### 解决方案

所有在弹窗内的操作统一以弹窗容器为父级进行链式定位：

```python
# ❌ 未限定容器，可能命中主页面同名按钮
page.locator("button:has-text('Continue')").click()

# ✅ 先定位弹窗容器，再在容器内查找
modal = page.locator("[role='dialog'][aria-modal='true']")
modal.wait_for(state="visible", timeout=10000)
modal.locator("button:has-text('Continue')").click()
```

**适用场景**：
- 登录 Modal 内的邮箱输入框、Continue 按钮、密码输入框、Login 按钮
- 确认弹窗内的"确定"/"取消"按钮
- 任何弹窗内与主页面有同名元素的情况

### 登录 Modal 完整示例

详见 `login-flow-recording.md` 中的 `LoginPage._modal()` 模式。
