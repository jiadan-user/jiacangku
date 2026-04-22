# 登录模块自动化测试说明

## 概述

本目录包含 OK AE站登录模块的自动化测试用例，基于 Playwright 和 pytest 框架实现。

**特点**：
- ✅ 所有用例在同一个浏览器中连续执行，无需重复启动浏览器
- ✅ 只有标记 `@pytest.mark.need_logout` 的用例会执行退登操作
- ✅ 每个用例执行前不打开新的浏览器窗口，在原窗口继续操作
- ✅ 不需要退登的用例完成后，如果登录弹窗打开则自动关闭

## 文件结构

```
login/
├── conftest.py                      # 共享 fixtures 和配置
├── test_login_welcome_page.py       # 欢迎页测试 (TC001-TC012)
├── test_login_email_password.py     # 邮箱密码登录测试 (TC013-TC026)
├── test_login_phone_password.py     # 手机号密码登录测试 (TC027-TC038)
└── README.md                        # 本文档
```

## 核心设计

### 1. 共享浏览器实例

使用 `module` scope 的 fixtures：
- `shared_browser`: 模块级共享浏览器
- `shared_context`: 模块级共享浏览器上下文
- `shared_page`: 模块级共享页面实例
- `login_page`: 模块级登录页面对象

### 2. 自动退登机制

通过 `@pytest.mark.need_logout` 标记需要退登的用例：

```python
@pytest.mark.need_logout  # 标记此用例需要退登
def test_tc013_email_login_success(...):
    ...
```

**需要退登的用例（3条）**：
- TC012: 登录后刷新页面右上角显示已登录状态
- TC013: 已注册邮箱正确密码登录成功
- TC027: 已注册手机号正确密码登录成功

### 3. 退登实现方式

退登操作在 `conftest.py` 的 `logout_if_needed()` 函数中实现：

1. Hover 到页面右上角用户头像
2. 等待下拉菜单出现
3. 点击下拉菜单中的 "Log Out" 按钮
4. 验证退登成功（右上角显示"Log in / Register"）

### 4. 弹窗自动关闭

对于不需要退登的用例，如果测试完成后登录弹窗仍然打开，会自动点击关闭按钮关闭弹窗。

## 使用方法

### 运行所有登录测试

```bash
# 在 test_cases/login 目录下
pytest -v

# 或指定具体文件
pytest test_login_welcome_page.py -v
pytest test_login_email_password.py -v
pytest test_login_phone_password.py -v
```

### 运行特定用例

```bash
# 按用例编号
pytest -k tc013 -v

# 按优先级
pytest -m p0 -v

# 只运行需要退登的用例
pytest -m need_logout -v
```

### 生成 Allure 报告

```bash
# 运行测试并生成 allure 数据
pytest --alluredir=./allure-results

# 生成并打开报告
allure serve ./allure-results
```

### 调试模式

```bash
# 显示详细输出
pytest -v -s

# 失败后进入调试器
pytest --pdb

# 只运行失败的用例
pytest --lf
```

## 测试账号

测试账号配置在 `conftest.py` 中：

```python
config = {
    "base_url": "https://ae.58v5.cn/en/city-dubai/",
    "email_account": "mamengmeng02@58.com",
    "email_password": "Qwer1234",
    "phone_number": "501234570",
    "phone_password": "Qwer1234",
    "unregistered_email": "mamengmeng001@58.com",
}
```

## 扩展指南

### 添加新的测试用例

1. 在对应的测试文件中添加新的测试方法
2. 使用共享的 `shared_page` 和 `login_page` fixtures
3. 如果用例需要退登，添加 `@pytest.mark.need_logout` 标记
4. 在方法参数中添加 `cleanup_after_test` fixture

示例：

```python
@pytest.mark.case_id("tc999")
@pytest.mark.p1
@pytest.mark.need_logout  # 如果需要退登
@allure.title("TC999: 新测试用例标题")
def test_tc999_new_test_case(
    self,
    shared_page: Page,
    login_page: LoginPage,
    config: dict,
    cleanup_after_test  # 必须添加此参数
):
    # 测试步骤
    ...
```

### 创建新的测试文件

如果需要创建新的测试文件（例如忘记密码、第三方登录等）：

1. 在 `login/` 目录下创建新文件，例如 `test_login_forgot_password.py`
2. 使用相同的 fixtures（`shared_page`, `login_page`, `config`, `cleanup_after_test`）
3. 保持与现有文件相同的结构和命名规范

## 注意事项

1. **执行顺序**：由于所有用例共享同一个浏览器，建议按用例编号顺序执行
2. **状态隔离**：需要退登的用例会自动清理登录状态，确保后续用例从未登录状态开始
3. **弹窗管理**：不需要退登的用例会自动关闭登录弹窗，避免影响后续用例
4. **错误处理**：如果退登失败，会生成截图 `debug_logout_failed.png` 便于调试
5. **浏览器窗口**：整个测试模块共享一个浏览器窗口，不要在测试用例中关闭窗口

## 常见问题

### Q: 如何修改浏览器为 headless 模式？

A: 在 `conftest.py` 中修改 `shared_browser` fixture：

```python
browser = playwright.chromium.launch(headless=True, ...)
```

### Q: 如何调整超时时间？

A: 在各个 expect 语句中使用 `timeout` 参数：

```python
expect(element).to_be_visible(timeout=10000)  # 10秒
```

### Q: 为什么有些用例需要退登？

A: 需要退登的用例通常是登录成功的核心流程，执行后会改变系统状态（从未登录变为已登录）。为了保证后续用例能够从预期的初始状态开始，需要退登恢复到未登录状态。

### Q: 如何跳过某些用例？

A: 使用 pytest 的 skip 功能：

```python
# 方法1：在用例上添加 skip marker
@pytest.mark.skip(reason="临时跳过")
def test_tc999(...):
    ...

# 方法2：在运行时跳过
pytest -k "not tc999" -v

# 方法3：条件跳过
if some_condition:
    pytest.skip("跳过原因")
```

## 性能优化

当前设计已经实现了以下优化：

- ✅ 浏览器复用：整个模块只启动一次浏览器
- ✅ 页面复用：所有用例在同一个页面上执行
- ✅ 上下文复用：Cookie 和会话状态在模块内持久化
- ✅ 智能清理：只在必要时执行退登或关闭弹窗

**预估性能提升**：相比传统方式（每个用例启动一次浏览器），可节省 **70-80%** 的执行时间。

## 维护建议

1. 定期更新测试数据（账号密码）
2. 关注页面元素定位器的变化，及时更新 `login_page.py`
3. 保持测试用例与文本用例的同步
4. 定期运行全量测试确保稳定性
5. 对失败的用例及时修复或标记 skip

---

**最后更新**: 2026-04-20  
**维护人**: QA Team
