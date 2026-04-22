# 登录模块自动化测试 - 快速开始

## 🚀 快速开始（5分钟）

### 1. 一键运行测试

```bash
cd test_cases/login
chmod +x run_tests.sh
./run_tests.sh
```

选择菜单选项即可运行测试！

### 2. 命令行运行

```bash
# 运行所有测试
pytest -v

# 只运行需要退登的用例
pytest -m need_logout -v

# 只运行 P0 用例
pytest -m p0 -v
```

---

## 📊 已实现的测试用例

### ✅ 欢迎页测试 (8个用例)

| 用例编号 | 标题 | 优先级 | 需要退登 |
|---------|------|--------|----------|
| TC001 | 点击「Log in / Register」打开欢迎弹窗 | P0 | ❌ |
| TC002 | 输入邮箱后 Continue 按钮变为可用 | P0 | ❌ |
| TC003 | 输入手机号后 Continue 按钮变为可用 | P0 | ❌ |
| TC004 | 输入框为空时 Continue 按钮保持禁用 | P0 | ❌ |
| TC005 | 输入非法格式邮箱 | P1 | ❌ |
| TC009 | 点击蒙层区域验证弹窗关闭 | P1 | ❌ |
| TC010 | 按 ESC 键验证弹窗关闭 | P1 | ❌ |
| TC012 | 登录后刷新页面保持已登录状态 | P0 | ✅ **需要退登** |

### ✅ 邮箱密码登录测试 (8个用例)

| 用例编号 | 标题 | 优先级 | 需要退登 |
|---------|------|--------|----------|
| TC013 | 已注册邮箱正确密码登录成功 | P0 | ✅ **需要退登** |
| TC014 | 密码为空时 Log in 按钮禁用 | P0 | ❌ |
| TC015 | 密码显示/隐藏切换 | P1 | ❌ |
| TC016 | 输入错误密码登录失败 | P0 | ❌ |
| TC017 | 未注册邮箱跳转到注册页面 | P0 | ❌ |
| TC022 | 正确显示邮箱地址 | P1 | ❌ |
| TC023 | 「Forgot your password?」链接展示 | P0 | ❌ |
| TC024 | 底部隐私声明文案展示 | P2 | ❌ |

### ✅ 手机号密码登录测试 (5个用例)

| 用例编号 | 标题 | 优先级 | 需要退登 |
|---------|------|--------|----------|
| TC027 | 已注册手机号正确密码登录成功 | P0 | ✅ **需要退登** |
| TC028 | 密码为空时 Log in 按钮禁用 | P0 | ❌ |
| TC029 | 密码显示/隐藏切换 | P1 | ❌ |
| TC032 | 正确显示手机号 | P1 | ❌ |
| TC033 | 「Forgot your password?」链接展示 | P0 | ❌ |

**总计**: 21 个自动化测试用例  
**需要退登**: 3 个用例 (TC012, TC013, TC027)

---

## 🎯 核心特性

### 1. ✅ 单浏览器执行
- 所有用例共享同一个浏览器实例
- 节省 70-80% 执行时间
- 无需重复启动浏览器

### 2. ✅ 智能退登
- 只有 3 条用例需要退登
- 自动 Hover 用户头像 → 点击 "Log Out"
- 验证退登成功

### 3. ✅ 自动弹窗管理
- 不需要退登的用例完成后自动关闭弹窗
- 保持测试环境整洁

### 4. ✅ 无窗口切换
- 所有用例在原浏览器窗口继续操作
- 不打开新标签页

---

## 📖 常用命令

### 运行测试

```bash
# 运行所有测试
pytest -v

# 运行特定文件
pytest test_login_welcome_page.py -v

# 运行特定用例
pytest -k tc013 -v

# 运行需要退登的用例
pytest -m need_logout -v

# 运行 P0 优先级用例
pytest -m p0 -v
```

### 生成报告

```bash
# 生成 Allure 报告
pytest --alluredir=./allure-results
allure serve ./allure-results

# 生成 HTML 报告
pytest --html=report.html --self-contained-html
```

### 调试

```bash
# 显示详细输出
pytest -v -s

# 失败后进入调试器
pytest --pdb

# 只运行失败的用例
pytest --lf

# 先运行失败的，再运行其他
pytest --ff
```

---

## 🔧 配置说明

### 测试账号

在 `conftest.py` 中配置：

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

### 浏览器模式

在 `conftest.py` 中修改：

```python
# Headless 模式（无界面）
browser = playwright.chromium.launch(headless=True, ...)

# 有界面模式（默认）
browser = playwright.chromium.launch(headless=False, ...)
```

---

## 📝 添加新用例

### 步骤

1. 在对应的测试文件中添加新方法
2. 使用 `@pytest.mark.case_id("tcXXX")` 标记
3. 如需退登，添加 `@pytest.mark.need_logout`
4. 参数中添加 `cleanup_after_test`

### 示例

```python
@pytest.mark.case_id("tc999")
@pytest.mark.p1
@pytest.mark.need_logout  # 如果需要退登
@allure.title("TC999: 测试标题")
def test_tc999_new_test(
    self,
    shared_page: Page,
    login_page: LoginPage,
    config: dict,
    cleanup_after_test  # 必须添加
):
    # 测试步骤
    with allure.step("步骤1"):
        ...
```

---

## ⚠️ 注意事项

1. **执行顺序**: 建议按用例编号顺序执行
2. **状态隔离**: 需要退登的用例会自动清理登录状态
3. **弹窗管理**: 不需要退登的用例会自动关闭登录弹窗
4. **错误处理**: 退登失败会生成截图 `debug_logout_failed.png`
5. **浏览器窗口**: 不要在测试用例中关闭浏览器窗口

---

## 🐛 常见问题

### Q: 如何跳过某个用例？

```bash
# 命令行跳过
pytest -k "not tc013" -v

# 代码中跳过
@pytest.mark.skip(reason="临时跳过")
def test_tc999(...):
    ...
```

### Q: 如何只运行某个测试类？

```bash
pytest test_login_welcome_page.py::TestLoginWelcomePage -v
```

### Q: 如何查看执行时间？

```bash
pytest -v --durations=10  # 显示最慢的 10 个用例
```

### Q: 如何并行执行？

```bash
# 安装 pytest-xdist
pip install pytest-xdist

# 并行执行（注意：login 测试共享浏览器，不建议并行）
pytest -n 4 -v
```

---

## 📈 性能优化

当前设计已实现：

- ✅ 浏览器复用（节省 70-80% 时间）
- ✅ 页面复用
- ✅ 上下文复用
- ✅ 智能清理

**预估执行时间**:
- 单个用例: 2-5 秒
- 全部 21 个用例: 约 2-3 分钟

---

## 📞 支持

遇到问题？查看 [README.md](./README.md) 获取更详细的文档。

---

**最后更新**: 2026-04-20  
**维护人**: QA Team
