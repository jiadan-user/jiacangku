# 搜索输入框 fill() + debounce 陷阱

## 问题描述

对含防抖（debounce）逻辑的搜索输入框使用 `fill()` 后立即读取结果，DOM 未更新，
`locator.count()` 返回的仍是搜索前的数量。

**典型报错**：
```
AssertionError: 搜索后结果数量(18)应少于全部项目数(18)
assert 18 < 18
```

---

## 根本原因

`fill()` 直接设置 input 的 value，不完整模拟键盘事件序列。某些 React / Vue
搜索组件依赖逐键触发的 `input` 事件来启动防抖计时器；`fill()` 虽然会触发一次
`input` 事件，但在 CI 环境中时序很紧，防抖计时器（通常 300~500ms）来不及触发
网络请求或前端过滤，500ms 的固定等待也可能不足。

```
fill('圣诞')                   ← 一次性设值，触发一次 input 事件
  → 防抖计时器启动（300ms）
  → keyboard.press('Enter')   ← 可能在防抖触发前执行
  → wait_for_timeout(500)     ← 总等待不足，DOM 未更新
  → locator.count()           ← 读到旧值 18，而非过滤后的 5
```

---

## 修复方案

### 方案1：press_sequentially（推荐）

逐字符输入，每个字符间有 delay，充分触发防抖计时器：

```python
# ❌ fill() 在防抖搜索框中不可靠
search_input.fill("圣诞")
page.wait_for_timeout(500)

# ✅ press_sequentially 逐字符触发 input 事件
search_input.press_sequentially("圣诞", delay=100)  # 每字符间隔 100ms
page.wait_for_timeout(1500)                          # 等待 debounce + DOM 更新
```

**参数说明**：
- `delay=100`：每次按键间隔 100ms，模拟真实打字速度，确保防抖计时器正常触发
- `wait_for_timeout(1500)`：1500ms = 防抖时间(500ms) + API/渲染时间(~1000ms)

### 方案2：fill() + 更长等待

如果 `press_sequentially` 对特殊字符支持不好（如某些输入法字符），可保留 `fill()` 但增加等待：

```python
search_input.fill("圣诞")
page.wait_for_timeout(2000)  # 给足防抖 + 渲染时间
```

### 方案3：等待特定元素变化（最健壮）

如果知道搜索后某个非匹配项应消失，用 `expect` 等待：

```python
search_input.press_sequentially("圣诞", delay=100)
# 等待某个"非圣诞"卡片消失，而不是固定等待
expect(
    page.locator("[class*='cardHeader']").filter(has_not_text="圣诞").first
).not_to_be_visible(timeout=5000)
```

---

## 识别规则

**何时使用 `press_sequentially` 而非 `fill()`**：

| 场景 | 推荐方式 |
|------|---------|
| 搜索框（有防抖/实时过滤） | `press_sequentially(delay=100)` |
| 普通表单输入（无实时监听） | `fill()` |
| 密码/验证码框 | `fill()` |
| 含输入法/自动补全的搜索框 | `press_sequentially(delay=150)` |

**识别信号**：
- 输入框 placeholder 含"搜索"、"search"、"查询"
- 文档用例步骤含"实时过滤"、"按关键词搜索"
- CLI 录制中搜索结果随输入实时变化（Enter 前就出结果）

---

## 验证搜索结果的健壮写法

```python
# 1. 记录初始数量（操作前）
initial_count = page.locator("[class*='cardHeader']").count()

# 2. 搜索
search_input.press_sequentially("圣诞", delay=100)
page.wait_for_timeout(1500)

# 3. 验证：用相对断言，不依赖具体数字
filtered_count = page.locator("[class*='cardHeader']").count()
assert filtered_count > 0, "应有匹配结果"
assert filtered_count < initial_count, "搜索后应过滤部分结果"

# 4. 清除并验证恢复（清除后也需等待）
page.get_by_role("button", name="close-circle").click()
page.wait_for_timeout(1000)
assert page.locator("[class*='cardHeader']").count() == initial_count
```

---

## 相关陷阱

- **统计数据/角标异步更新**：见 `async-counter-update.md`
- **严格模式违规**：见 `strict-mode-list-assertions.md`
