# OK AE站 - 登录模块自动化测试

## 测试概览

本测试套件基于 `OK-AE站-登录模块-测试用例-20260312.md` 文档生成，涵盖登录模块的核心功能测试。

- **生成时间**: 2026-03-12
- **测试范围**: 欢迎页、邮箱密码登录、手机号密码登录、隐私协议与合规
- **总用例数**: 78 条（文档，已移除 TC011/TC021/TC025/TC026）
- **已实现自动化**: 约 48 条
- **自动化覆盖率**: ~61.5%

## 目录结构

```
test_cases/login/
├── README.md                                    # 本文件
├── test_login_welcome_page_tc001_tc012.py       # 欢迎页测试（TC001-TC010、TC012；已移除 TC011）
├── test_login_email_password_tc013_tc026.py     # 邮箱密码登录（TC013-TC024；已移除 TC021/025/026）
├── test_login_phone_password_tc027_tc038.py     # 手机号密码登录测试（TC027-TC038）
└── test_login_privacy_policy_tc066_tc082.py     # 隐私协议与合规测试（TC066-TC082）
```

## 测试环境配置

### 站点信息
- **站点**: AE（阿联酋站）
- **基础URL**: https://ae.58v5.cn/en/city-dubai/
- **站点名称**: 阿联酋站（迪拜）

### 测试账号
- **邮箱（有密码流程）**: `mamengmeng02@58.com` — 欢迎页/邮箱密码/忘记密码/隐私与权限等脚本中的 `TEST_EMAIL` / `test_account`
- **邮箱测试密码**（有密码账号）: `Qwer1234`
- **未注册邮箱**: `mamengmeng001@58.com`
- **手机测试账号**: `+971 501234570`
- **手机测试密码**: `Qwer1234`

## 快速开始

### 1. 安装依赖

```bash
# 确保在项目根目录
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

### 2. 运行测试

#### 运行所有登录模块测试
```bash
cd ok_autotest_ui_pc
pytest test_cases/login/ -v --alluredir=reports/allure-results
```

#### 运行特定测试文件
```bash
# 只运行欢迎页测试
pytest test_cases/login/test_login_welcome_page_tc001_tc012.py -v

# 只运行邮箱密码登录测试
pytest test_cases/login/test_login_email_password_tc013_tc026.py -v

# 只运行手机号密码登录测试
pytest test_cases/login/test_login_phone_password_tc027_tc038.py -v

# 只运行隐私协议测试
pytest test_cases/login/test_login_privacy_policy_tc066_tc082.py -v
```

#### 按优先级运行
```bash
# 只运行 P0 级别测试（核心功能）
pytest test_cases/login/ -v -m P0

# 只运行 P0 和 P1 级别测试
pytest test_cases/login/ -v -m "P0 or P1"
```

#### 按模块运行
```bash
# 运行特定 story
pytest test_cases/login/ -v --allure-epic="登录模块" --allure-feature="一、欢迎页（Welcome Page）"
```

### 3. 生成测试报告

```bash
# 生成 Allure 报告
allure generate reports/allure-results -o reports/allure-report --clean

# 打开报告
allure open reports/allure-report
```

## 测试用例分布

### 一、欢迎页（Welcome Page）- TC001-TC010、TC012
- **用例数**: 11 条
- **覆盖场景**: 
  - 核心流程：打开弹窗、输入邮箱/手机号、按钮状态
  - 表单校验：非法邮箱、空格、超长字符、Emoji
  - 弹窗交互：蒙层关闭、ESC 关闭
  - 会话状态：登录后刷新

### 二、邮箱密码登录页 - TC013-TC024
- **用例数**: 10 条（文档中 TC020 仍为人工；TC021/025/026 已删除）
- **覆盖场景**:
  - 核心流程：正确登录、按钮禁用、密码显示切换
  - 表单校验：错误密码、未注册邮箱、特殊字符、超长密码
  - UI 文案验证

### 三、手机号密码登录页 - TC027-TC038
- **用例数**: 12 条
- **覆盖场景**:
  - 核心流程：手机号登录、国家码自动识别
  - 表单校验：非数字字符、位数不足、错误密码、未注册手机
  - UI文案验证、防重复提交

### 九、隐私协议与合规 - TC066-TC082
- **用例数**: 17 条
- **覆盖场景**:
  - 隐私声明展示：欢迎页、邮箱登录页、手机号登录页
  - 链接跳转：Terms of Use、Privacy Policy
  - 链接一致性、状态保持
  - 安全性：URL 不泄露密码、HTTPS 协议

## 测试标记（Markers）

- `@pytest.mark.P0`: 核心功能，阻塞级别
- `@pytest.mark.P1`: 重要功能，严重级别
- `@pytest.mark.P2`: 次要功能，一般级别

## Allure 报告特性

- **Epic**: 登录模块
- **Feature**: 具体功能模块（欢迎页、邮箱登录页等）
- **Story**: 测试场景分类（核心流程、表单校验、UI文案等）
- **Title**: 测试用例标题
- **Description**: 详细的测试步骤和预期结果
- **Severity**: 严重程度（BLOCKER、CRITICAL、NORMAL、MINOR）

## 注意事项

### 1. 浏览器可见性
测试默认在有头模式下运行（可见浏览器窗口）。如需无头模式：

```bash
# 方式1：环境变量
export HEADLESS=true
pytest test_cases/login/ -v

# 方式2：CI 环境（自动启用无头模式）
export CI=1
pytest test_cases/login/ -v
```

### 2. 会话管理
- 每个测试用例独立运行，不共享会话
- 测试结束后自动清理浏览器状态
- 支持并行执行（使用 pytest-xdist）

### 3. 失败重试
建议配置失败重试策略：

```bash
# 失败后重试 2 次
pytest test_cases/login/ -v --reruns 2 --reruns-delay 3
```

### 4. 并行执行
使用 pytest-xdist 提升执行效率：

```bash
# 使用 4 个进程并行执行
pytest test_cases/login/ -v -n 4
```

## 已知限制

以下测试场景暂未实现自动化（需人工测试或特殊环境）：

1. **TC020、TC035**: 连续错误密码频控（需人工验证频控触发）
2. **TC030**: 手机号登录切换国家码（需观察下拉列表）
3. **TC039-TC048**: 忘记密码流程（需接收真实验证码）
4. **TC049-TC052**: 第三方登录（需真实 OAuth 账号）
5. **TC055、TC056、TC057**: 接口级安全测试（需专用工具）
6. **TC058-TC060**: 网络异常场景（需网络模拟工具）
7. **TC076、TC077**: 页面加载失败（需模拟服务端错误）
8. **TC082**: DOM 篡改测试（需手动操作）

## 维护说明

### 添加新测试用例

1. 确定测试用例所属模块（欢迎页/邮箱登录/手机登录等）
2. 在对应文件中添加测试方法
3. 使用 Allure 装饰器标记（epic、feature、story、title、severity）
4. 使用 pytest.mark 标记优先级（P0/P1/P2）
5. 遵循现有的测试步骤结构（with allure.step）

### 更新测试数据

测试账号配置在各文件顶部的常量中，统一修改即可：

```python
# 有密码流程（如 welcome / email_password / forgot_password 等）
BASE_URL = "https://ae.58v5.cn/en/city-dubai/"
TEST_EMAIL = "mamengmeng02@58.com"
TEST_PASSWORD = "Qwer1234"
```

## 联系方式

如有问题或建议，请联系测试团队。

---

**生成工具**: Cursor AI Assistant  
**文档版本**: v1.0  
**最后更新**: 2026-03-12
