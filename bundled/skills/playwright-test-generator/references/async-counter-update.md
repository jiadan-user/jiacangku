# 统计数据/角标异步更新陷阱

## 问题描述

创建或删除操作成功后，页面 Tab 角标（如"进行中18"）和统计卡片数字是**异步更新**的。弹窗关闭或 Toast 出现后，计数器可能仍显示旧值，立即读取会导致断言失败。

**典型报错**：
```
AssertionError: 进行中数量应减1: 18 → 18   # 删除成功但计数未变
AssertionError: 取消删除后数量不应变化: 进行中18 → 进行中19  # 基线读太早
```

---

## 根本原因

前端在 API 返回成功后先关闭弹窗，再异步刷新计数器，两者之间存在约 500~800ms 的时间差。

```
API 成功响应
    → 关闭弹窗 (modal.close)        ← expect(".ant-modal").not_to_be_visible() 在此完成
    → Toast 显示 (创建成功/删除成功) ← expect(get_by_text("...")).to_be_visible() 在此完成
    → [异步] 更新 Tab 角标           ← 读取时序问题在此触发
    → [异步] 更新统计卡片
```

---

## 修复方案

### 方案1：在辅助方法末尾统一加等待（推荐）

在 `_create_project`、`_delete_project_by_ui` 等辅助方法内部，确认操作完成后加 800ms 等待：

```python
def _create_project(self, name: str, description: str) -> None:
    page = self.page
    page.get_by_role("button", name="plus 新增项目").click()
    page.get_by_role("textbox", name="* 项目名称").fill(name)
    page.get_by_role("textbox", name="* 项目描述 *").fill(description)
    page.get_by_role("button", name="新 增").click()
    expect(page.get_by_text("项目创建成功")).to_be_visible(timeout=5000)
    expect(page.locator(".ant-modal")).not_to_be_visible(timeout=5000)
    page.wait_for_timeout(800)   # ← 等待 Tab 计数器异步更新
```

```python
# 删除操作后同理
page.get_by_role("button", name="确定删除").click()
expect(page.get_by_text("删除成功")).to_be_visible(timeout=5000)
expect(page.locator(".ant-modal")).not_to_be_visible(timeout=5000)
page.wait_for_timeout(800)   # ← 等待 Tab 计数器异步更新
```

### 方案2：用 expect 等待 Tab 文本变化（更严格）

如果 800ms 不够稳定，可以用 `expect` 明确等待 Tab 显示预期数值：

```python
# 等待进行中 Tab 变为 N-1
expected_text = str(before_num - 1)
expect(in_progress_tab).to_contain_text(expected_text, timeout=5000)
```

---

## 基线读取顺序（必须遵守）

**操作前读基线，操作后等待再对比。**

```python
# ✅ 正确顺序
baseline = in_progress_tab.inner_text()   # 1. 操作前读基线
baseline_num = int(re.search(r"\d+", baseline).group())

_create_project(...)                        # 2. 执行操作（内含 wait_for_timeout(800)）

after = in_progress_tab.inner_text()       # 3. 等待后读新值
after_num = int(re.search(r"\d+", after).group())
assert after_num == baseline_num + 1       # 4. 对比
```

```python
# ❌ 错误：创建后才读基线
_create_project(...)              # 已经触发了计数更新
baseline = in_progress_tab.inner_text()   # 读到的是更新后的值！
# cancel_delete(...)
# assert count == baseline  → 永远为 True，失去测试意义
```

---

## 实战案例（TC011 取消删除）

TC011 需要验证「取消删除后计数不变」，正确逻辑：

```python
# 1. 记录创建前基线
baseline_text = in_progress_tab.inner_text()
baseline_num = int(re.search(r"\d+", baseline_text).group())

# 2. 创建前置项目（内含 800ms wait）
self._create_project(project_name, "...")

# 3. 验证创建后 +1
after_create_num = int(re.search(r"\d+", in_progress_tab.inner_text()).group())
assert after_create_num == baseline_num + 1

# 4. 执行取消删除
card_header.locator(".anticon-more").click()
page.get_by_role("menuitem", name="删除").click()
page.get_by_role("button", name="取 消").click()   # 取消，不是确认
page.wait_for_timeout(500)

# 5. 验证计数仍等于创建后的值（未因取消而减少）
after_cancel_num = int(re.search(r"\d+", in_progress_tab.inner_text()).group())
assert after_cancel_num == after_create_num   # 应该仍是 baseline+1
```

---

## 相关陷阱

- **列表断言严格模式**：见 `strict-mode-list-assertions.md`
- **统计卡片（项目总数）的定位**：顶部5个卡片都含数字，`get_by_text(re.compile(r"^\d+$"))` 会命中全部5个，需要用父容器缩小范围或直接跳过，改用 Tab 角标验证即可。
