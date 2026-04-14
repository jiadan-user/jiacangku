# Playwright JavaScript → Python 完整转换规则

> 本文档提供系统化的Playwright代码转换规则，确保从JavaScript代码准确转换为Python代码

---

## 1. 基础语法转换

### 1.1 命名约定

| JavaScript (camelCase) | Python (snake_case) |
|------------------------|---------------------|
| `newPage()` | `new_page()` |
| `goto()` | `goto()` |
| `getByRole()` | `get_by_role()` |
| `getByText()` | `get_by_text()` |
| `getByTestId()` | `get_by_test_id()` |
| `waitForTimeout()` | `wait_for_timeout()` |
| `waitForSelector()` | `wait_for_selector()` |
| `waitForLoadState()` | `wait_for_load_state()` |
| `innerText()` | `inner_text()` |
| `isVisible()` | `is_visible()` |
| `toBeVisible()` | `to_be_visible()` |

### 1.2 参数传递

**JavaScript**: 使用对象字面量
```javascript
page.getByRole('button', { name: 'Submit' })
page.waitFor({ state: 'hidden', timeout: 5000 })
```

**Python**: 使用关键字参数
```python
page.get_by_role("button", name="Submit")
page.wait_for(state="hidden", timeout=5000)
```

### 1.3 引号约定

**JavaScript**: 单引号或双引号
```javascript
page.getByText('Hello')
```

**Python**: 推荐双引号
```python
page.get_by_text("Hello")
```

---

## 2. 核心API转换

### 2.1 Locator 方法

| JavaScript | Python | 说明 |
|-----------|---------|------|
| `.first()` | `.first` | **属性，不是方法！** |
| `.last()` | `.last` | 属性 |
| `.nth(0)` | `.nth(0)` | 方法调用 |
| `.count()` | `.count()` | 方法调用 |
| `.all()` | `.all()` | 方法调用 |

**关键区别**：
```javascript
// JavaScript
const element = page.getByText('Hello').first()  // ✅ 方法调用

# Python
element = page.get_by_text("Hello").first  # ✅ 属性访问
```

### 2.2 等待方法

| JavaScript | Python | 说明 |
|-----------|---------|------|
| `await page.waitForTimeout(1000)` | `page.wait_for_timeout(1000)` | 固定延迟 |
| `await locator.waitFor()` | `locator.wait_for()` | 等待元素 |
| `await page.waitForLoadState('networkidle')` | `page.wait_for_load_state("networkidle")` | 等待页面加载 |
| `await page.waitForURL('**/admin')` | `page.wait_for_url("**/admin")` | 等待URL |

**状态参数**：
```javascript
// JavaScript
await element.waitFor({ state: 'visible' })
await element.waitFor({ state: 'hidden' })

# Python
element.wait_for(state="visible")
element.wait_for(state="hidden")
```

### 2.3 断言方法

| JavaScript | Python | 说明 |
|-----------|---------|------|
| `await expect(locator).toBeVisible()` | `expect(locator).to_be_visible()` | 可见性 |
| `await expect(locator).toContainText('text')` | `expect(locator).to_contain_text("text")` | 文本包含 |
| `await expect(locator).toHaveValue('value')` | `expect(locator).to_have_value("value")` | 值检查 |
| `await expect(locator).toHaveCount(5)` | `expect(locator).to_have_count(5)` | 数量检查 |

**超时参数**：
```javascript
// JavaScript
await expect(locator).toBeVisible({ timeout: 3000 })

# Python
expect(locator).to_be_visible(timeout=3000)
```

---

## 3. 选择器转换

### 3.1 通用选择器

| JavaScript | Python |
|-----------|---------|
| `page.locator('.class')` | `page.locator(".class")` |
| `page.locator('#id')` | `page.locator("#id")` |
| `page.locator('css=button')` | `page.locator("css=button")` |
| `page.locator('xpath=//button')` | `page.locator("xpath=//button")` |

### 3.2 语义化选择器（推荐）

| JavaScript | Python |
|-----------|---------|
| `page.getByRole('button')` | `page.get_by_role("button")` |
| `page.getByText('Submit')` | `page.get_by_text("Submit")` |
| `page.getByLabel('Email')` | `page.get_by_label("Email")` |
| `page.getByPlaceholder('Enter email')` | `page.get_by_placeholder("Enter email")` |
| `page.getByAltText('logo')` | `page.get_by_alt_text("logo")` |
| `page.getByTitle('Close')` | `page.get_by_title("Close")` |
| `page.getByTestId('submit-btn')` | `page.get_by_test_id("submit-btn")` |

### 3.3 组合选择器

```javascript
// JavaScript
page.getByRole('button', { name: 'Submit' })
page.getByRole('button', { name: /submit/i })

# Python
page.get_by_role("button", name="Submit")
page.get_by_role("button", name=re.compile("submit", re.IGNORECASE))
```

### 3.4 filter() 过滤器（⚠️ 正则转换高频陷阱）

CLI 录制返回的 JS 中经常含有 `filter({ hasText: ... })`，转换时极易出错。

| JavaScript | Python | 说明 |
|-----------|---------|------|
| `.filter({ hasText: 'text' })` | `.filter(has_text="text")` | 字符串匹配 |
| `.filter({ hasText: /^text$/ })` | `.filter(has_text=re.compile(r"^text$"))` | ⚠️ 正则必须用 `re.compile` |
| `.filter({ hasNotText: 'text' })` | `.filter(has_not_text="text")` | 排除文本 |

**❌ 常见错误——使用不存在的参数名**：
```python
# 不存在 has_text_regex 参数，运行报 TypeError
page.locator("div").filter(has_text_regex=r"^Amount\(\$\)$").nth(1).click()
```

**✅ 正确写法**：
```python
import re
# 字符串模式
page.locator("div").filter(has_text="Amount($)").nth(1).click()

# 正则模式（需要精确匹配时）
page.locator("div").filter(has_text=re.compile(r"^Amount\(\$\)$")).nth(1).click()
```

**识别信号**：CLI 返回代码中含 `filter({ hasText: /.../ })` → 一定要用 `re.compile`。

---

## 4. 页面操作转换

### 4.1 导航

| JavaScript | Python |
|-----------|---------|
| `await page.goto('https://example.com')` | `page.goto("https://example.com")` |
| `await page.reload()` | `page.reload()` |
| `await page.goBack()` | `page.go_back()` |
| `await page.goForward()` | `page.go_forward()` |

### 4.2 交互操作

| JavaScript | Python |
|-----------|---------|
| `await locator.click()` | `locator.click()` |
| `await locator.dblclick()` | `locator.dblclick()` |
| `await locator.fill('text')` | `locator.fill("text")` |
| `await locator.type('text')` | `locator.type("text")` |
| `await locator.check()` | `locator.check()` |
| `await locator.uncheck()` | `locator.uncheck()` |
| `await locator.selectOption('value')` | `locator.select_option("value")` |

### 4.3 键盘操作

```javascript
// JavaScript
await page.keyboard.press('Enter')
await page.keyboard.type('Hello')

# Python
page.keyboard.press("Enter")
page.keyboard.type("Hello")
```

---

## 5. 上下文管理转换

### 5.1 浏览器生命周期

**JavaScript**:
```javascript
const { chromium } = require('playwright');
const browser = await chromium.launch();
const context = await browser.newContext();
const page = await context.newPage();
// ... 操作 ...
await browser.close();
```

**Python Sync API**:
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    # ... 操作 ...
    # 自动关闭
```

**Python Async API**:
```python
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        # ... 操作 ...
        # 自动关闭

asyncio.run(main())
```

---

## 6. 常见陷阱

### 陷阱1：first 是属性不是方法

```javascript
// ❌ JavaScript习惯（Python中错误）
element = page.get_by_text("Hello").first()  # TypeError!

// ✅ Python正确写法
element = page.get_by_text("Hello").first
```

### 陷阱2：参数格式

```javascript
// ❌ JavaScript对象字面量（Python中错误）
page.get_by_role("button", { name: "Submit" })  # SyntaxError!

// ✅ Python关键字参数
page.get_by_role("button", name="Submit")
```

### 陷阱3：wait_for 的状态参数

```javascript
// ❌ 忘记state参数（Python中错误）
element.wait_for("hidden")  # TypeError!

// ✅ Python正确写法
element.wait_for(state="hidden")
```

### 陷阱4：超时单位

```javascript
// JavaScript和Python都是毫秒
await page.waitForTimeout(1000)  // 1秒
page.wait_for_timeout(1000)  # 1秒
```

### 陷阱5：禁止生成局部 fixture（防 ScopeMismatch）

```python
# ❌ 错误：画蛇添足地生成了局部的 config fixture
_CONFIG = { ... }

@pytest.fixture
def config():
    return _CONFIG

def test_something(page, config):
    pass

# ✅ 正确：只定义字典，直接使用全局 fixture
_CONFIG = { ... }

def test_something(page, config):
    pass
```
**原因**：项目的 `conftest.py` 已经定义了 `scope="module"` 的 `config` fixture。如果在测试文件里再写一个默认 `scope="function"` 的 `config`，会导致 `class` 级别的 `page` fixture 无法调用它，从而抛出致命的 `ScopeMismatch` 错误。

---

## 7. 完整转换示例

### JavaScript 代码

```javascript
// 登录并创建项目
await page.goto('https://test.optell.com/zh/projectManage');
await page.getByRole('button', { name: 'plus 新增项目' }).click();
await page.getByRole('textbox', { name: '* 项目名称' }).fill('Test Project');
await page.getByRole('button', { name: '新 增' }).click();

// 验证成功提示
await expect(page.getByText('项目创建成功').first()).toBeVisible({ timeout: 3000 });
await page.getByText('项目创建成功').first().waitFor({ state: 'hidden', timeout: 5000 });

// 验证项目列表
const count = await page.getByRole('tab', { name: '进行中' }).innerText();
```

### Python 代码（转换后）

```python
# 登录并创建项目
page.goto("https://test.optell.com/zh/projectManage")
page.get_by_role("button", name="plus 新增项目").click()
page.get_by_role("textbox", name="* 项目名称").fill("Test Project")
page.get_by_role("button", name="新 增").click()

# 验证成功提示
expect(page.get_by_text("项目创建成功").first).to_be_visible(timeout=3000)
page.get_by_text("项目创建成功").first.wait_for(state="hidden", timeout=5000)

# 验证项目列表
count = page.get_by_role("tab", name="进行中").inner_text()
```

---

## 8. 自动化转换脚本（可选）

可以使用正则表达式进行基础转换：

```python
import re

def convert_js_to_python(js_code: str) -> str:
    """将JavaScript Playwright代码转换为Python代码"""
    py_code = js_code
    
    # 1. 移除 await
    py_code = re.sub(r'await\s+', '', py_code)
    
    # 2. 转换方法名（camelCase → snake_case）
    camel_to_snake = {
        'getByRole': 'get_by_role',
        'getByText': 'get_by_text',
        'getByTestId': 'get_by_test_id',
        'waitFor': 'wait_for',
        'waitForTimeout': 'wait_for_timeout',
        'innerText': 'inner_text',
        'toBeVisible': 'to_be_visible',
        'toContainText': 'to_contain_text',
    }
    for js_name, py_name in camel_to_snake.items():
        py_code = re.sub(rf'\b{js_name}\b', py_name, py_code)
    
    # 3. 转换 .first() → .first
    py_code = re.sub(r'\.first\(\)', '.first', py_code)
    py_code = re.sub(r'\.last\(\)', '.last', py_code)
    
    # 4. 转换参数格式 { name: 'value' } → name="value"
    py_code = re.sub(r"\{\s*name:\s*'([^']+)'\s*\}", r'name="\1"', py_code)
    py_code = re.sub(r'\{\s*state:\s*\'([^\']+)\'\s*\}', r'state="\1"', py_code)
    py_code = re.sub(r'\{\s*timeout:\s*(\d+)\s*\}', r'timeout=\1', py_code)
    
    # 5. 转换引号
    py_code = py_code.replace("'", '"')
    
    return py_code

# 测试
js_code = """
await page.getByRole('button', { name: 'Submit' }).click()
await page.getByText('Success').first().waitFor({ state: 'hidden' })
"""

print(convert_js_to_python(js_code))
```

---

## 9. 检查清单

在转换代码后，请检查：

- [ ] 所有 `camelCase` 方法名已转换为 `snake_case`
- [ ] `.first()` 已改为 `.first`（无括号）
- [ ] `.last()` 已改为 `.last`（无括号）
- [ ] JavaScript 对象参数 `{ key: value }` 已改为 Python 关键字参数 `key=value`
- [ ] 单引号已改为双引号
- [ ] `await` 关键字已移除（Sync API）
- [ ] 超时值单位为毫秒
- [ ] `state` 参数使用 `state="value"` 格式

---

## 10. 参考资源

- [Playwright Python 官方文档](https://playwright.dev/python/)
- [Playwright JavaScript vs Python API对比](https://playwright.dev/python/docs/api/class-playwright)
- [Playwright Codegen工具](https://playwright.dev/python/docs/codegen)
