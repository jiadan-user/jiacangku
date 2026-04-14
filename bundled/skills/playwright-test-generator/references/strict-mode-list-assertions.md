# 列表场景严格模式违规：原因与修复

## 为什么录制时没有问题，生成的代码才出错？

### CLI 录制阶段

CLI 录制操作时使用 `ref` ID（快照瞬时唯一），不受严格模式约束：

```
录制：browser_click(ref="e1195")  →  page.get_by_role("button", name="新 增").click()
```

**录制只捕获动作（click/fill/navigate），不生成断言代码。**
断言代码是在"代码生成阶段"手写的，这里是引入问题的地方。

---

## 触发场景

页面有多个同类卡片/行时，如果用 `div.filter().first` 作为外层容器：

```python
# ❌ .first 返回的是最外层 div（可能包含整个列表）
card = page.locator("div").filter(has_text=project_name).first
# 子查询 get_by_text("暂无周期") 在整个列表内搜索 → 命中 N 个卡片
expect(card.get_by_text("暂无周期")).to_be_visible()
# 报错：strict mode violation: resolved to 10 elements
```

**原因**：Playwright 的 `.first` 只作用在最外层 `locator("div")` 上，选中"第一个包含该文本的 div"。但页面中第一个包含该文本的 div 往往是很大的父容器（整个列表区域），而不是具体的卡片元素。

---

## 正确写法

### 方法1：用 CSS 类名定位精确组件（推荐）

类名从 **错误日志** 或 **browser_snapshot** 获取：

```python
# 错误日志示例：
# aka locator("div:nth-child(3) > .cardContent___nDegD > .infoWrap___hNpLi > span")
# → 说明卡片内容有 cardContent、cardHeader 等 CSS 类

# ✅ 用 cardHeader 定位（header 内只有项目名 + more 按钮）
card_header = page.locator("[class*='cardHeader']").filter(has_text=project_name)

# 在 cardHeader 内点击 more
card_header.locator(".anticon-more").click()

# 验证 cardHeader 兄弟/父节点内容
card = card_header.locator("xpath=..")
expect(card.get_by_text("暂无周期")).to_be_visible()
```

### 方法2：用 browser_snapshot 确认选择器

对"不确定的验证点"，先用 `browser_snapshot` 观察 snapshot 结构，找到唯一标识的类名/角色再写断言。

### 方法3：接受多个匹配，只取第一个

如果验证点不需要精确到某个卡片（只要存在就行）：

```python
# ✅ 明确取第一个：.first 作用在最终的目标元素上
expect(page.get_by_text("暂无周期").first).to_be_visible()
```

---

## 清理方法中的同类问题

`_delete_project_by_ui` 也必须使用精确定位：

```python
# ❌ 错误：more 按钮在最外层容器内会找到 N 个
card = page.locator("div").filter(has_text=name).first
card.get_by_role("img", name="more").click()  # resolved to 12 elements

# ✅ 正确：cardHeader 内只有一个 more 按钮
card_header = page.locator("[class*='cardHeader']").filter(has_text=name)
card_header.locator(".anticon-more").click()
```

---

## 自检清单

写断言前确认：
- [ ] 验证目标是否在列表/表格/卡片页面中？
- [ ] 是否用了 `div.filter().first` 作为外层容器？（如果是，必须改为 CSS 类名）
- [ ] `browser_snapshot` 是否显示该元素有唯一 CSS 类名或 ARIA 角色？
