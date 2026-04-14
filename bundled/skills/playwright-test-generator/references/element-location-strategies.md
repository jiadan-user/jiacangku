# 元素定位策略指南

> ⚠️ **核心原则**：CLI 录制结果 > 一切手写定位器。本文档只在录制结果不可用或需要验证时参考。

---

## 🎯 定位器优先级（与 SKILL.md 保持一致）

### 优先级排序

| 级别 | 方式 | 稳定性 | 说明 |
|------|------|--------|------|
| **P0** | CLI 返回的代码 | ★★★★★ | 唯一实测来源，直接使用 |
| **P1** | `get_by_role()` | ★★★★★ | 语义化，Playwright 官方推荐 |
| **P2** | `get_by_label()` / `get_by_placeholder()` | ★★★★ | 基于标签，表单首选 |
| **P3** | `get_by_text()` + 精确匹配 | ★★★ | 需配合作用域限定 |
| **P4** | CSS 类名 + `filter()` | ★★ | CLI snapshot 中提取类名 |
| ❌ **禁止** | 全局 `text="XXX"` / `locator("button")` | ★ | 容易多匹配，造成不可见元素问题 |

```python
# ✅ P0: 直接使用 CLI 返回
page.get_by_role("button", name="Continue").click()

# ✅ P1: 语义定位
page.get_by_role("textbox", name="Job Title").fill("Engineer")

# ✅ P2: 表单标签
page.get_by_label("Email").fill("test@example.com")
page.get_by_placeholder("Set the location for your post.").fill("New York")

# ⚠️ P3: 文本匹配（必须限定范围，见下节）
page.locator("main").get_by_text("Jobs", exact=True).click()

# ❌ 禁止: 全局 text= 匹配
page.locator('text="Jobs"').click()  # 可能命中隐藏的下拉菜单！
```

---

## ⚠️ 多元素冲突：最常见的运行时失败原因

### 问题模式

```
页面中同时存在：
1. <a>Jobs</a>         ← 顶部导航下拉（display:none，不可见）
2. <div>Jobs</div>     ← 分类选择区（可见，应该点这个）

page.locator('text="Jobs"').click()
→ Playwright 选第一个（不可见）→ ElementNotVisible
```

### 三步诊断法

```python
# 第一步：检查匹配数量
locator = page.locator('text="Jobs"')
count = locator.count()
print(f"匹配到 {count} 个元素")

# 第二步：逐个检查可见性
for i in range(count):
    el = locator.nth(i)
    print(f"元素 {i}: visible={el.is_visible()}, html={el.inner_html()[:80]}")

# 第三步：点击可见的那个
for i in range(count):
    el = locator.nth(i)
    if el.is_visible(timeout=2000):
        el.click()
        break
```

### 解决方案：限定搜索范围

```python
# ❌ 问题写法（全局匹配，找到隐藏元素）
page.locator('text="Jobs"').click()

# ✅ 方案1：限定到主内容区
page.locator("main").get_by_text("Jobs", exact=True).click()

# ✅ 方案2：排除干扰容器
page.locator('div:has-text("Jobs"):not([class*="Dropdown"])').click()

# ✅ 方案3：使用 filter(visible)【推荐】
page.locator('text="Jobs"').filter(visible=True).first.click()

# ✅ 方案4：限定在弹窗内（弹窗场景）
modal = page.locator("[role='dialog'][aria-modal='true']")
modal.get_by_role("button", name="Continue").click()
```

---

## 🛡️ 正确的多策略 Fallback（非 try/except 超时）

### ❌ 错误写法（性能差，每次等 timeout）

```python
# 每次失败都要等 3000ms 超时，14个策略 = 42秒
for selector in strategies:
    try:
        page.click(selector, timeout=3000)  # 等满3秒才换下一个
        return
    except:
        continue
```

### ✅ 正确写法（先 count 检查，再 is_visible 过滤）

```python
def robust_click(page, strategies):
    """健壮的点击方法：先检查匹配数，再过滤可见性，不依赖超时"""
    for i, selector in enumerate(strategies):
        locator = page.locator(selector)
        count = locator.count()          # 0ms 同步操作

        if count == 0:
            continue                     # 立即跳过，不等待

        for j in range(count):
            el = locator.nth(j)
            try:
                if el.is_visible(timeout=1000):  # 只等1秒
                    el.click()
                    return
            except Exception:
                continue

    raise Exception("所有策略均失败")

# 使用示例
robust_click(page, [
    'main >> text="Jobs"',                          # 策略1：限定范围
    '[class*="Category"]:not([class*="nav"]) >> text="Jobs"',  # 策略2：排除导航
    'div.category-icon:has-text("Jobs")',            # 策略3：类名+文本
])
```

---

## ⏱️ 等待策略：三层机制

### 异步加载的典型时序

```
页面 goto (0ms)       → 骨架屏
DOM 完成 (~500ms)     → 结构可用，内容可能还在加载
网络空闲 (~1500ms)    → API 数据已到，渲染完成
动画结束 (~2000ms)    → 用户可交互  ← 录制在这里开始
```

### 三层等待代码

```python
# 第1层：等 DOM 结构
page.wait_for_load_state("domcontentloaded", timeout=15000)

# 第2层：等关键元素可见（比 networkidle 更精确）
page.wait_for_selector("h1:has-text('Job Basics')", state="visible", timeout=10000)

# 第3层：等异步更新（如计数器、角标）
page.wait_for_timeout(800)   # 只在有充分理由时使用，来自录制观察
```

### ❌ 不要用 networkidle（SPA 应用不友好）

```python
# ❌ SPA 应用长连接会导致 networkidle 永远等不到
page.wait_for_load_state("networkidle")

# ✅ 用关键元素出现代替
page.wait_for_selector("h1:has-text('Job Basics')", state="visible", timeout=10000)
```

---

## 🔍 CLI 录制后：选择器自检清单

录制完成，生成代码前，对每个选择器过一遍：

```
□ locator.count() > 1？          → 加范围限定或 filter(visible=True)
□ 用了全局 text="XXX"？          → 改为 get_by_role/get_by_text 限定范围
□ 用了 .locator("div")？         → 加 .filter(has_text=...) 缩小匹配
□ 弹窗内的元素？                 → 用 [role="dialog"] >> ... 限定容器
□ 列表/表格中的操作按钮？         → 用行容器 >> 按钮，不能直接全局定位
□ 等待只用了 wait_for_timeout？  → 改为 wait_for_selector 条件等待
□ 使用了 .first 而不是 .first()? → 确认是属性不是方法（Python 语法）
```

---

## 📐 常见场景：标准写法

### 场景1：弹窗内同名按钮（防止主页面被拦截）

```python
# ❌ 未限定容器，可能命中主页面
page.locator("button:has-text('Continue')").click()

# ✅ 限定在弹窗内
modal = page.locator("[role='dialog'][aria-modal='true']")
modal.locator("button:has-text('Continue')").click()
```

### 场景2：列表中操作特定行

```python
# ❌ 全局找删除按钮，会删错行
page.get_by_role("button", name="Delete").click()

# ✅ 先定位行，再找按钮
row = page.locator("tr").filter(has_text="project-name-2026")
row.get_by_role("button", name="Delete").click()
```

### 场景3：导航栏 + 下拉同名元素

```python
# ❌ 点到隐藏的导航下拉
page.locator('text="Jobs"').click()

# ✅ 限定在主内容区
page.locator("main").get_by_text("Jobs", exact=True).click()

# ✅ 或用 filter 过滤可见
page.locator('text="Jobs"').filter(visible=True).first.click()
```

### 场景4：下拉选项（防止 strict mode violation）

```python
# ❌ 选项文本全局匹配，命中多个
page.get_by_text("Engineering").click()

# ✅ 限定在下拉面板中
dropdown_panel = page.locator(".item-label-text")
dropdown_panel.get_by_text("Engineering", exact=True).click()
```

### 场景5：动态列表断言（避免 strict mode violation）

```python
# ❌ 命中最外层容器，子查询触发 strict mode
card = page.locator("div").filter(has_text=project_name).first
expect(card.get_by_text("Active")).to_be_visible()  # N个匹配 → 报错

# ✅ 用 CSS 类名缩小范围（从 browser_snapshot 获取类名）
card = page.locator("[class*='cardHeader']").filter(has_text=project_name)
expect(card.locator("xpath=..").get_by_text("Active")).to_be_visible()
```

---

## 🛠️ 调试三板斧

### 1. `browser_snapshot()` 精确获取 ref 和类名

CLI 录制时，每次操作前必须先执行 `playwright-cli snapshot`，从返回结果中：
- 获取元素的 `ref` 直接点击
- 获取 `class` 名用于 CSS 定位（避免猜测）

### 2. `browser_evaluate()` 验证选择器

```python
# 在录制过程中验证 disabled 选项
browser_evaluate("() => { ... document.querySelectorAll('.list-group-item.disabled') ... }")
```

### 3. Playwright Inspector（本地调试）

```bash
PWDEBUG=1 python3 -m pytest test_cases/post_job/test_post_job_step1_validation.py::test_tc012 -s
```

---

## 💡 核心记忆口诀

```
CLI 返回的代码是金子，优先使用别犹豫；
text= 全局要小心，加上范围才安心；
多个匹配先 count，filter visible 来过滤；
等待不用 networkidle，等关键元素出现好；
弹窗内部找元素，dialog 容器来限定。
```

---

**最后更新**: 2026-02-27
**关联文件**: `SKILL.md` §阶段4、`references/strict-mode-list-assertions.md`、`references/sticky-header-click.md`
