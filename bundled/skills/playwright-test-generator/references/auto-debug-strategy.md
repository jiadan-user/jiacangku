# 每批自动调试策略（阶段6）

> 批次间必做：运行验证 + 错误修复 + 跨批经验传递

---

## 一、运行命令

```bash
# 1. 强制依赖检查（生成代码后必须先执行）
pytest --collect-only {生成的文件路径} 2>&1

# 2. 基础运行（依赖检查通过后执行）
pytest {生成的文件路径} -v --tb=short 2>&1

# 带超时保护（防止卡死）
pytest {生成的文件路径} -v --tb=short --timeout=60 2>&1

# 定向调试单个用例
pytest {文件路径}::{函数名} -v --tb=long -s 2>&1
```

---

## 二、调试循环（最多3轮）

```
代码生成完毕
  ↓
执行 pytest --collect-only
  ├─ 失败 (ModuleNotFoundError) → 修复导包或创建缺失目录/文件 → 重新 collect
  └─ 成功 ↓
运行测试 (pytest)
  ↓
全部通过？
  ├─ 是 → 记录"本批无新问题" → 开始下一批
  └─ 否 → 进入修复流程（最多3轮）
            ↓
          分析报错（见第三节）
            ↓
          修复代码
            ↓
          重新运行
            ↓
          3轮后仍失败 → 暂停，告知用户
```

---

## 三、常见错误分析与修复

### E0：ModuleNotFoundError (导包或目录缺失)

```
E   ModuleNotFoundError: No module named 'pages.ae'
```

**原因**：生成的代码引用了不存在的 POM 目录/文件，或者路径写错。

**修复**：
1. **如果是路径写错**：修改生成的测试文件中的 `import` 语句。
2. **如果是缺少目录/文件**：使用 `Shell` 工具创建缺失的包结构。
```bash
# 示例：创建缺失的 pages/ae 目录及 __init__.py
mkdir -p pages/ae
touch pages/ae/__init__.py
touch pages/ae/settings_page.py
```
*修复后必须再次运行 `pytest --collect-only` 确认通过。*

---

### E1：strict mode violation

```
Error: strict mode violation: locator resolved to N elements
```

**原因**：选择器命中多个元素。

**修复**：
```python
# ❌ 过于宽泛
page.get_by_text("50000", exact=True).click()

# ✅ 用 CSS 类名或 filter 缩小范围
page.locator("span.left").filter(has_text=re.compile(r"^50000$")).click()
```

---

### E2：Locator.click Timeout（元素被拦截）

```
Error: Locator.click: Timeout 30000ms exceeded
  subtree intercepts pointer events
```

**原因A**：动态推荐浮层覆盖了目标元素（如填 Job Title 后出现 Job Function 推荐列表）。

**修复A**：
```python
# 在 select_job_function 等方法开头关闭浮层
self.page.get_by_role("heading", name="Job Basics").click()
self.page.wait_for_timeout(600)
```

**原因B**：sticky TopBar 遮挡了滚动后的元素。

**修复B**：
```python
# 用 JS 滚动并偏移，避开 sticky TopBar（高度约60-80px，偏移160px留余量）
trigger.evaluate(
    "el => { const y = el.getBoundingClientRect().top + window.pageYOffset - 160; "
    "window.scrollTo({ top: y, behavior: 'instant' }); }"
)
self.page.wait_for_timeout(400)
trigger.click()
```

---

### E3：Element is not visible / Timeout（元素未找到）

```
Error: Timeout 30000ms exceeded / Element is not visible
```

**原因A**：全局 `text=` 命中了隐藏元素。

**修复A**：
```python
# ❌ 命中隐藏的导航下拉
page.locator('text="Jobs"').click()
# ✅ 加可见性过滤或限定父容器
page.locator('text="Jobs"').filter(visible=True).first.click()
page.locator("main").get_by_text("Jobs", exact=True).click()
```

**原因B**：SPA 路由后内容未渲染完就断言。

**修复B**：
```python
page.wait_for_url("**/target**", timeout=15000)
page.wait_for_load_state("domcontentloaded", timeout=10000)
```

---

### E4：搜索结果不更新（count() 返回旧值）

```
AssertionError: expected 1 but got 3
```

**原因**：`fill()` 不触发 input 事件，防抖计时器未启动。

**修复**：
```python
# ❌
search_input.fill("关键词")
page.wait_for_timeout(500)

# ✅
search_input.press_sequentially("关键词", delay=100)
page.wait_for_timeout(1500)  # 防抖(~500ms) + 渲染(~1000ms)
```

---

### E5：统计角标/数字读取旧值

```
AssertionError: expected 5 but got 4
```

**原因**：弹窗关闭后 Tab 角标异步更新约 800ms，立即读取拿到旧值。

**修复**：
```python
expect(page.locator(".ant-modal")).not_to_be_visible(timeout=5000)
page.wait_for_timeout(800)  # 等角标异步刷新
count = tab.inner_text()    # 再读取
```

---

### E6：element detached from DOM

```
Error: element was detached from the DOM
```

**原因**：下拉联动面板 DOM 重排，点击子选项时节点已消失。

**修复**：
```python
self.page.locator(".item-label-text").get_by_text(category, exact=True).click()
self.page.wait_for_timeout(600)   # 等待子面板 DOM 稳定
self.page.get_by_text(sub_category).click()
```

---

### E7：弹窗内元素冲突

```
Error: element intercepts pointer events
```

**原因**：Modal 未关闭时点击了主页面同名元素。

**修复**：
```python
modal = page.locator("[role='dialog'][aria-modal='true']")
modal.locator("button:has-text('Continue')").click()
```

---

### E8：复杂组件无法触发校验（如 Google Maps Location）

```
AssertionError: 应停留在 Step1，实际跳转 Step2
```

**原因**：Location 等使用地图/外部组件的字段，React 内部 state 与 DOM input.value 分离，
`fill("")` 不清空实际选中值，表单认为字段有效，Continue 直接成功。

**处理**：标记该用例为 skip，原因说明清楚：
```python
@pytest.mark.skip(
    reason="Location 使用 Google Maps 坐标，清空文本输入不清空内部坐标 state，无法触发校验"
)
```

---

## 四、跨批经验传递

每轮调试结束后，将修复记录追加到会话级**已知陷阱列表**：

```
【已知陷阱列表】（会话累积，每批调试后更新）

- [批次1] 搜索框用 press_sequentially(delay=100) 替代 fill()
- [批次1] Tab 角标读取前加 wait_for_timeout(800)
- [批次1] fill_job_title → select_job_function 序列：
           需在 select_job_function 开头调用 heading.click() 关闭推荐浮层
- [批次1] sticky TopBar：用 JS scrollTo 偏移160px 替代 scroll_into_view_if_needed()
- [批次2] 列表卡片选择器用 [class*='cardHeader'] 而非 div.filter()
```

**下一批代码生成前的检查**：

| 已知陷阱 | 本批次是否涉及 | 处理方式 |
|---------|-------------|---------|
| 推荐浮层拦截 | ✅ TCxxx 有联动字段 | 在方法开头加 heading.click() |
| sticky TopBar | ✅ TCyyy 有 trigger.click | 用 JS scrollTo 偏移 |
| 搜索框 fill() | ❌ 本批无搜索 | 跳过 |

---

## 五、3轮后仍失败的处理

向用户说明：

```
⚠️ 调试未完全通过（3轮后仍有失败）

失败用例：
- test_tcxxx：触发器点击超时（已尝试 heading.click() + JS偏移，仍超时）

可能原因：
1. 该页面有特殊的弹窗/浮层行为，需要重新录制确认
2. 网络延迟导致页面加载慢，需要调整等待时间

建议：
A. 重新录制 TCxxx，用 browser_snapshot 观察实际 DOM 状态
B. 跳过 TCxxx，继续下一批（后续单独补录）

请选择处理方式。
```

---

## 六、pytest 未安装时的降级处理

1. 先尝试：`python -m pytest {文件路径} -v --tb=short`
2. 仍失败：进行**静态代码检查**：
   - 语法检查：`python -m py_compile {文件路径}`
   - 逐行检查转换陷阱（见 `references/js-to-py-conversion.md` 检查清单）
3. 告知用户无法自动运行，建议手动执行后反馈结果
