# 验证步骤录制指南

> 将操作的真实结果转化为高稳定性的断言。

---

## 🎯 为什么不仅要录制操作，还要录制验证？

作为 AI，我们在理解自然语言的用例时（例如：“页面弹出成功提示”），往往会倾向于在代码生成阶段直接去猜测 `expect(page.locator('.success')).to_be_visible()`。

**为什么这种猜测是有害的？**
1. 同一个表单在不同用例下（比如全量填写 vs 必填项），可能触发的验证点样式并不一样。
2. 异常用例的报错位置往往不是标准弹窗，而是内联的 Input Error 状态。
3. 如果你在阶段 2 遗漏了验证动作的录制，在阶段 4 你的断言代码将大概率变成需要人类接手调试的 Flaky Tests。

---

## ✅ 完整的录制流程

### 对于每个测试用例，必须完整包含两个维度的录制：

```
操作步骤（50%）
├─ browser_navigate
├─ browser_snapshot
├─ browser_click / browser_type
└─ 记录 CLI 返回的操作代码

+

验证步骤（50%）⭐ 关键
├─ browser_wait_for → 等待预期变化
├─ browser_take_screenshot → 保存状态
├─ browser_snapshot → 捕获验证点
└─ 记录时序和验证点选择器
```

---

## 📋 验证录制清单

### TC001：创建项目（正常流程）

#### 操作步骤
```javascript
1. browser_navigate("https://example.com/#/project/list")
2. browser_snapshot()
3. browser_click(ref="123", element="新增项目按钮")
   CLI返回：await page.getByRole('button', { name: 'plus 新增项目' }).click();

4. browser_type(ref="456", element="项目名称", text="测试项目")
   CLI返回：await page.getByRole('textbox', { name: '* 项目名称' }).fill('测试项目');

5. browser_click(ref="789", element="新增按钮")
   CLI返回：await page.getByRole('button', { name: '新 增' }).click();
```

#### 验证步骤（⚠️ 必须录制）
```javascript
6. browser_wait_for({ text: "项目创建成功" })
   → 观察：1.2秒后出现提示
   → 记录：expect(page.locator("text=项目创建成功")).to_be_visible(timeout=2000)

7. browser_take_screenshot({ filename: "tc001-success-toast.png" })
   → 保存：成功提示的截图
   → 用途：后续维护时可以看到实际效果

8. browser_snapshot()
   → 分析：提示的DOM结构、项目卡片的位置
   → 提取：项目卡片的选择器

9. browser_wait_for({ time: 2 })
   → 观察：提示停留2秒后消失
   → 记录：page.wait_for_timeout(2000)

10. browser_snapshot()
    → 分析：提示消失后的页面状态
    → 提取：弹窗已关闭、项目卡片显示

11. browser_take_screenshot({ filename: "tc001-final-state.png" })
    → 保存：最终状态截图
```

**生成的验证代码**：
```python
with allure.step("步骤3: 点击'新增'按钮"):
    page.get_by_role("button", name="新 增").click()

with allure.step("验证：显示成功提示"):
    expect(page.locator("text=项目创建成功")).to_be_visible(timeout=2000)
    page.wait_for_timeout(2000)  # 等待提示消失

with allure.step("验证：弹窗关闭"):
    expect(page.locator("dialog")).not_to_be_visible()

with allure.step("验证：项目出现在列表"):
    expect(page.locator(f"text={project_name}").first).to_be_visible()
```

---

### TC002：仅填必填项（必须独立录制！）

❌ **错误做法**：
```
TC002和TC001类似，复制TC001代码，只改输入值
→ 结果：验证逻辑可能不准确
```

✅ **正确做法**：
```javascript
1. 完整录制TC002的所有步骤
2. 观察：只填必填项时，页面有什么不同？
3. 验证：成功提示是否相同？项目卡片显示是否一样？
4. 截图保存实际效果

即使流程相似，也必须实际操作一遍！
```

---

### TC003：输入重名项目（异常流程）

#### 操作步骤
```javascript
1-4. [与TC001相同的操作]
5. browser_click(ref="789", element="新增按钮")
```

#### 验证步骤（⚠️ 关键！异常流程的验证不同）
```javascript
6. browser_wait_for({ text: "项目名称已存在" })
   → 观察：出现错误提示
   → 记录：准确的错误文案

7. browser_take_screenshot({ filename: "tc003-error-toast.png" })
   → 保存：错误提示的截图
   → 用途：知道错误提示长什么样

8. browser_snapshot()
   → 分析：错误提示的位置、样式
   → 提取：错误提示的选择器

9. 观察：弹窗是否还在？
   → 记录：expect(page.locator("dialog")).to_be_visible()
   → 原因：输入错误时弹窗不应该关闭
```

**生成的验证代码**：
```python
with allure.step("验证：显示错误提示"):
    expect(page.locator("text=项目名称已存在")).to_be_visible(timeout=2000)

with allure.step("验证：弹窗保持打开"):
    expect(page.locator("dialog")).to_be_visible()

with allure.step("验证：输入框高亮显示错误"):
    expect(page.get_by_role("textbox", name="* 项目名称")).to_have_class(/error/)
```

---

## 🎯 关键原则

### 原则1：每个用例独立录制

**为什么？**
- TC001（正常）vs TC003（异常）：验证点完全不同
- TC001（完整）vs TC002（必填）：可能有细微差异
- 不实际操作，无法知道真实行为

---

### 原则2：操作和验证都要录制

**为什么？**
- 操作决定"做什么"
- 验证决定"怎么判断成功/失败"
- 两者同样重要！

---

### 原则3：保存关键状态截图

**为什么？**
- 截图是"地图"，代码是"导航"
- 后续维护时可以看到实际效果
- 帮助理解代码意图

---

## 📊 录制完整性检查

### 每个用例录制完成后，确认：

- [ ] 调用了所有操作相关的 CLI 工具
- [ ] 记录了所有 CLI 返回的 Playwright 代码
- [ ] 调用了 `browser_wait_for` 等待验证点
- [ ] 调用了 `browser_take_screenshot` 保存关键状态
- [ ] 调用了 `browser_snapshot` 捕获验证点选择器
- [ ] 观察并记录了时序信息
- [ ] 提取了所有验证点的准确文案

---

## 🚨 避免常见错误

### 误区1：只录制TC001就推演其余

```
✅ TC001: 11步CLI调用
❌ TC002: "和TC001类似，复制TC001的操作逻辑"
```

**为什么这会出错**：即便是同样的一个表单，只填写“必填项”和“填写全量”，在业务逻辑和验证结果上都会有差异（更不用提异常校验）。必须老老实实逐一调用 CLI 体验一遍。

---

### 误区2：忽略验证点的确认

```
✅ 点击"新增"按钮
❌ 然后呢？成功提示长什么样？在 DOM 的哪一层？
```

**为什么这会出错**：生成的断言代码全靠想象，极容易引发 ElementNotVisible 报错。

---

### 误区3：过度依赖固定超时 (Timeout)

```python
# ❌ 基于猜测的生硬等待
page.wait_for_timeout(3000)

# ✅ 基于真实录制时感知的条件等待
expect(page.locator("text=项目创建成功")).to_be_visible(timeout=2000)
page.wait_for_timeout(2000)  # 这是录制时观察到气泡停留的2秒
```

---

## 📈 改进效果预期

### 改进前
```
录制TC001：15分钟
生成代码：5分钟
运行测试：5/5 failed
调试修复：30分钟
───────────
总计：50分钟
```

### 改进后
```
录制TC001-TC005：每个5分钟 = 25分钟（包含验证）
生成代码：10分钟（自动生成验证）
运行测试：5/5 passed ✅
调试修复：0分钟
───────────
总计：35分钟
```

**关键收益**：
- ✅ 节省时间 30%
- ✅ 一次生成，直接可用
- ✅ 代码质量更高
- ✅ 有截图参考，易维护

---

## 💡 实施建议

在使用 skill 时，明确告诉 AI：

```
"使用 playwright-test-generator 生成测试脚本
测试用例文档：@/path/to/test-cases.md

⚠️ 重要要求：
1. 每个用例都必须独立录制，不可参考其他用例
2. 每个用例都必须录制验证步骤，包括：
   - 等待成功/错误提示
   - 截图保存关键状态
   - 捕获验证点选择器
3. 观察并记录时序信息"
```

---

## ⚠️ 文案断言：Unicode 字符编码陷阱

页面文案中的撇号、引号等特殊字符可能是 Unicode 弯引号（`'` U+2019、`"` U+201C/201D），而非 ASCII 直引号（`'` U+0027、`"` U+0022）。断言时字符不匹配会静默失败（`is_visible()` 返回 `False`）。

**识别信号**：文案断言失败，但截图中文字可见；错误里含 `'`/`"` 等撇号/引号。

**录制时的检查步骤**：对含撇号/引号的文案，在 CLI 录制时用 `browser_evaluate` 验证字符编码：

```javascript
// CLI browser_evaluate 检查关键字符的 charCode
() => {
  const txt = document.querySelector('p').innerText;
  const idx = txt.indexOf("ve ");   // 定位到目标字符的位置
  const ch = txt[idx - 1];
  return "char:" + ch + " code:" + ch.charCodeAt(0);
}
// 返回 code:8217 → U+2019 弯引号，需用 \u2019 写入断言
// 返回 code:39  → U+0027 ASCII 直引号，正常写法即可
```

**Python 断言写法**：

```python
# ❌ 直引号，若页面用弯引号则静默失败
assert page.locator("text=You've done it").is_visible()

# ✅ 用 \u2019 明确弯引号
assert page.locator("text=You\u2019ve done it").is_visible()

# ✅ 或绕开特殊字符，用不含引号的子串做断言
assert page.locator("text=You").is_visible()
```

**规范**：凡录制的验证文案中含有 `'`、`"`、`'`、`"` 字符，必须先用 `browser_evaluate` 确认 charCode，再写断言。

---

**最后更新**：2026-02-26  
**用途**：确保完整录制操作+验证，避免生成的代码需要调试
