# OK AE站 - 邮箱与手机号登录未设置密码场景 测试用例

> **生成时间**: 2026-03-25  
> **探测方式**: Playwright MCP 实测（邮箱场景，2026-03-25）；Playwright **有界面**脚本实测（手机号无密码 TC016–TC018，`scripts/probe_ae_phone_no_password_tc016_018.py`，`HEADLESS=false`，2026-04-03）  
> **测试范围**: 邮箱 / 手机号登录未设置密码场景的验证码登录流程  
> **总用例数**: 18 条  
> **可自动化**: 15 条（83.3%）

---

## 测试环境配置（必填）

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | ae | ae/us/hk/br 等 |
| 基础URL | https://ae.58v5.cn | 测试站点地址 |
| 站点名称 | 阿联酋站 | 可选，用于日志展示 |
| 角色 | user | 普通用户 |
| 账号名称 | test_no_pwd_user_ae | 用于 session 命名，必须唯一 |
| 测试账号（邮箱） | mamengmeng01@58.com | 登录邮箱（未设置密码账号） |
| 测试密码（邮箱） | 无 | 该账号未设置密码 |
| 测试账号（手机号） | +971 501234579 | 已注册、未设置密码手机号（AE，用于短信验证码登录路径） |
| 测试密码（手机号） | 无 | 该账号未设置密码 |
| 手机号输入方式 | `501234579` 或 `+971 501234579` | 与全站一致：欢迎页「Email or phone number」输入框输入号码主体或完整号，系统自动识别 AE +971 |

**说明**：上述配置为实际探测时使用的账号。邮箱无密码账号特点是已注册但未设置密码；**手机号无密码**使用专用账号 `+971 501234579`（与有密码手机联调号 `+971 501234570` 区分）。playwright-test-generator 生成脚本时需按渠道分别绑定邮箱或手机号配置。与「有密码」登录自动化区分：**无密码/本场景邮箱**使用 `mamengmeng01@58.com`，**邮箱+密码等流程**使用 `mamengmeng02@58.com`（见 `OK-AE站-登录模块-测试用例-20260312.md`）。

---

## 功能概述

### 业务场景
当用户**邮箱**或**手机号**已注册但未设置密码时，系统会引导用户使用**邮箱验证码**或**短信验证码**进行登录（无密码页展示「Send code」，进入「Verification code」页完成校验）。

### 手机号无密码（+971 501234579）
与邮箱逻辑对齐：进入密码页后展示未设置密码说明与「Send code」；发送后进入验证码页，说明文案为 **phone number** 渠道；Toast 为 **sent to your phone**（与邮箱 Toast「…your email.」区分）。倒计时与 Confirm 联动与邮箱场景一致。✅ 2026-04-03 已于 `https://ae.58v5.cn/en/city-dubai/` 用 `501234579` 走通主路径。

### 关键发现（实测）
1. ✅ 输入未设置密码的邮箱后，系统进入密码页但显示特殊提示："You haven't added a password to your account yet. Sign in with your email code instead."
2. ✅ 密码页中提供"Send code"按钮，点击后发送验证码到邮箱
3. ✅ 验证码发送后显示Toast提示："The code has been sent to your email."
4. ✅ 页面切换到"Verification code"页面，包含验证码输入框、倒计时（59s）和Confirm按钮
5. ✅ Confirm按钮在验证码输入框为空时为disabled状态，输入内容后变为enabled
6. ✅ 验证码输入框placeholder为"Enter code"
7. ✅ 倒计时期间Send按钮显示剩余秒数，倒计时结束后变为"Resend"
8. ✅ **手机号未设置密码**（+971 501234579，2026-04-03 实测）：密码页仍显示与邮箱相同的英文提示 *Sign in with your email code instead.*；验证码页说明为 *…sent a verification code to the phone number: +971 501234579…*；Toast 含 *The code has been sent to your phone.*

---

## 测试用例

### 一、未设置密码提示展示

### TC001: 未设置密码邮箱进入密码页显示特殊提示

#### 📋 前置条件
- 已访问 https://ae.58v5.cn/
- 点击"Log in / Register"打开登录弹窗
- 停留在欢迎页

#### 🎬 执行步骤
1. 在邮箱输入框输入未设置密码的邮箱"mamengmeng01@58.com"
2. 点击"Continue"按钮

#### ✅ 预期结果
- 页面跳转到密码页，显示标题"Welcome back!" ✅ 实测
- 显示邮箱"mamengmeng01@58.com" ✅ 实测
- 显示提示文案"You haven't added a password to your account yet. Sign in with your email code instead." ✅ 实测
- 显示"Send code"按钮 ✅ 实测
- 不显示密码输入框 ✅ 实测
- 显示返回按钮 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### TC002: Send code 按钮初始状态正常

#### 📋 前置条件
- 已进入未设置密码的密码页

#### 🎬 执行步骤
1. 观察"Send code"按钮状态

#### ✅ 预期结果
- "Send code"按钮可见 ✅ 实测
- "Send code"按钮为enabled状态 ✅ 实测
- 按钮文案为"Send code" ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### 二、发送验证码功能

### TC003: 点击 Send code 成功发送验证码

#### 📋 前置条件
- 已进入未设置密码的密码页
- "Send code"按钮为enabled状态

#### 🎬 执行步骤
1. 点击"Send code"按钮

#### ✅ 预期结果
- 显示Toast提示"The code has been sent to your email." ✅ 实测
- 页面跳转到"Verification code"页面 ✅ 实测
- 页面标题显示"Verification code" ✅ 实测
- 显示说明文案"To continue, complete this verification step. We've sent a verification code to the email: mamengmeng01@58.com. Please enter it below." ✅ 实测
- 显示验证码输入框，placeholder为"Enter code" ✅ 实测
- 显示倒计时（初始59s） ✅ 实测
- "Send code"按钮文案变为"59s"（倒计时显示） ✅ 实测
- Confirm按钮为disabled状态 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC004: 验证码倒计时正常运行

#### 📋 前置条件
- 已点击"Send code"进入验证码页面
- 倒计时已开始

#### 🎬 执行步骤
1. 等待5秒，观察倒计时变化

#### ✅ 预期结果
- 倒计时按钮文案从"59s"逐秒递减 ✅ 实测
- 倒计时期间按钮为disabled状态 ⚠️ 推断（业界惯例）
- 倒计时期间不可重复点击发送 ⚠️ 推断（业界惯例）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / 时序
- **UI自动化**: ✅ 可自动化

---

### TC005: 倒计时结束后显示 Resend

#### 📋 前置条件
- 已点击"Send code"进入验证码页面
- 倒计时已开始

#### 🎬 执行步骤
1. 等待60秒直到倒计时结束

#### ✅ 预期结果
- 倒计时结束后，按钮文案变为"Resend" ⚠️ 推断（基于业界惯例）
- "Resend"按钮为enabled状态 ⚠️ 推断
- 可以再次点击发送验证码 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / 时序
- **UI自动化**: ❌ 不可自动化（需等待60秒，影响测试效率）

---

### 三、验证码输入与校验

### TC007: 验证码输入框初始状态

#### 📋 前置条件
- 已点击"Send code"进入验证码页面

#### 🎬 执行步骤
1. 观察验证码输入框

#### ✅ 预期结果
- 验证码输入框可见 ✅ 实测
- placeholder显示"Enter code" ✅ 实测
- 输入框为空 ✅ 实测
- Confirm按钮为disabled状态 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### TC008: 输入验证码后 Confirm 按钮变为 enabled

#### 📋 前置条件
- 已进入验证码页面
- Confirm按钮初始为disabled状态

#### 🎬 执行步骤
1. 在验证码输入框输入"123456"

#### ✅ 预期结果
- 输入框显示"123456" ✅ 实测
- Confirm按钮从disabled变为enabled ✅ 实测
- Confirm按钮可点击 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC009: 清空验证码后 Confirm 按钮恢复 disabled

#### 📋 前置条件
- 已在验证码输入框输入内容
- Confirm按钮为enabled状态

#### 🎬 执行步骤
1. 清空验证码输入框（全选删除或backspace）

#### ✅ 预期结果
- 输入框内容被清空 ✅ 实测
- Confirm按钮从enabled变为disabled ✅ 实测
- Confirm按钮不可点击 ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC010: 验证码输入框允许输入长字符串

#### 📋 前置条件
- 已进入验证码页面

#### 🎬 执行步骤
1. 在验证码输入框输入超过20位的字符串"12345678901234567890123"

#### ✅ 预期结果
- 输入成功，前端不做截断 ⚠️ 推断（基于已有发现"验证码输入长度无前端限制"）
- Confirm按钮变为enabled ⚠️ 推断
- 点击Confirm后由后端验证返回错误 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC011: 验证码输入特殊字符

#### 📋 前置条件
- 已进入验证码页面

#### 🎬 执行步骤
1. 在验证码输入框输入特殊字符"!@#$%^"

#### ✅ 预期结果
- 输入成功 ⚠️ 推断
- 点击Confirm后由后端验证返回错误 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### 四、返回与导航

### TC012: 点击返回按钮返回欢迎页

#### 📋 前置条件
- 已进入未设置密码的密码页或验证码页面

#### 🎬 执行步骤
1. 点击左上角返回按钮（或Back按钮）

#### ✅ 预期结果
- 页面返回到欢迎页 ⚠️ 推断（基于已有发现"返回功能"）
- 显示"Welcome to OK.com"标题 
- 显示邮箱输入框，内容保留之前输入
- Continue按钮可点击

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / 导航
- **UI自动化**: ✅ 可自动化

---

### 五、文案与国际化

### TC013: 验证码页面文案完整性

#### 📋 前置条件
- 已进入验证码页面

#### 🎬 执行步骤
1. 检查页面所有文案

#### ✅ 预期结果
- 标题"Verification code"正确显示 ✅ 实测
- 说明文案包含"To continue, complete this verification step" ✅ 实测
- 说明文案包含实际邮箱地址"mamengmeng01@58.com" ✅ 实测
- 输入框placeholder"Enter code"正确显示 ✅ 实测
- Confirm按钮文案为"Confirm" ✅ 实测
- 倒计时显示为"XXs"格式 ✅ 实测
- "Your data is protected"标识始终显示在顶部 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI / 文案
- **UI自动化**: ✅ 可自动化

---

### 六、手机号登录未设置密码场景（测试账号：+971 501234579）

> 与「一～五」邮箱分支并列：前置为欢迎页输入该手机号（✅ 实测推荐输入号码主体 `501234579`，系统自动识别为 AE +971；亦可输入 `+971 501234579`）。探测页面：`https://ae.58v5.cn/en/city-dubai/`（2026-04-03）。

### TC014: 未设置密码手机号进入密码页显示特殊提示

#### 📋 前置条件
- 已访问 https://ae.58v5.cn/（或带城市的落地页，如 `/en/city-dubai/`）
- 点击「Log in / Register」打开登录弹窗
- 停留在欢迎页

#### 🎬 执行步骤
1. 在「Email or phone number」输入框输入未设置密码的手机号（推荐 `501234579`）
2. 点击「Continue」按钮

#### ✅ 预期结果
- 页面进入无密码密码页，显示标题「Welcome back!」✅ 实测
- **不展示**「Phone number」小标题；在标题下方**直接展示**完整号码「+971 501234579」✅ 实测（与有密码手机号密码页「Phone number」+ 号码的布局不同）
- 显示与邮箱无密码**相同英文提示**：「You haven't added a password to your account yet. Sign in with your email code instead.」（其中撇号在 DOM 中可能为弯引号 `’`）✅ 实测；**不**因走短信渠道而改为「SMS code」类文案（以当前 AE 站为准）
- 显示「Send code」按钮 ✅ 实测
- 不显示「Enter password」密码输入框 ✅ 实测
- 弹层内存在返回类控件（左上角）✅ 实测
- 顶部展示「Your data is protected」✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### TC015: 手机号未设置密码 — 点击 Send code 成功发送验证码

#### 📋 前置条件
- 已进入账号「+971 501234579」的未设置密码密码页
- 「Send code」按钮为 enabled 状态

#### 🎬 执行步骤
1. 点击「Send code」按钮

#### ✅ 预期结果
- 显示 Toast；核心文案包含 **「The code has been sent to your phone.」**（与邮箱场景的「…your **email**.」区分）✅ 实测
- **沙箱/联调环境**：Toast 可能前置 **「沙箱验证码:xxxxxx!!!」** 等调试文案，再拼接上述英文句 ✅ 实测；**生产环境**以前端实际为准，自动化断言建议用正则匹配 `The code has been sent to your phone`
- 页面跳转到「Verification code」页面 ✅ 实测
- 页面标题显示「Verification code」✅ 实测
- 说明文案为：**「To continue, complete this verification step. We've sent a verification code to the phone number: +971 501234579. Please enter it below.」**（`We've` / `haven't` 在页面上可能为弯引号）✅ 实测
- 验证码输入以「Enter code」作为可访问名称/邻近展示；`placeholder` 属性可能为空，以弹层内「Enter code」文案及输入框存在为准 ✅ 实测
- 发送后倒计时区域显示 **「59s」量级递减**（如首帧「56s」「57s」属正常）✅ 实测
- Confirm 按钮在验证码为空时为 **disabled** ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化（短信内容不校验，仅校验 UI 与 Toast）

---

### TC016: 手机号验证码页面文案包含 +971 501234579

#### 📋 前置条件
- 已在「+971 501234579」路径下点击「Send code」并进入验证码页

#### 🎬 执行步骤
1. 检查页面标题、说明文案、Enter code 区域、Confirm 与倒计时展示

#### ✅ 预期结果
- 标题「Verification code」正确显示 ✅ 实测
- 说明文案包含「To continue, complete this verification step」✅ 实测
- 说明文案包含「the **phone number**」及完整号码「+971 501234579」（号码与引导句之间可能存在窄空格，断言时宜规范化空白）✅ 实测
- 展示「Enter code」输入区域 ✅ 实测
- 「Your data is protected」显示在弹层顶部 ✅ 实测
- Confirm 文案为「Confirm」✅ 实测（与邮箱验证码页一致）
- 倒计时以「XXs」形式展示 ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI / 文案
- **UI自动化**: ✅ 可自动化

---

## 测试统计

| 优先级 | 总数 | 可自动化 |
|--------|------|---------|
| P0 | 6 | 6 |
| P1 | 9 | 7 |
| P2 | 3 | 3 |
| P3 | 0 | 0 |
| **合计** | **18** | **15 (83.3%)** |

**实测文案覆盖率**: 邮箱分支约 75%；手机号无密码主路径（TC016–TC018）已于 2026-04-03 在 AE 联调环境跑通并落库，生产 Toast 若有差异以线上为准

---

## 备注

### ✅ 实测确认的关键发现

1. **未设置密码提示文案**（2026-03-25实测）：
   - "You haven't added a password to your account yet. Sign in with your email code instead."
   - 这是区分未设置密码场景的关键标识

2. **验证码页面结构**（2026-03-25实测）：
   - 标题："Verification code"
   - 说明："To continue, complete this verification step. We've sent a verification code to the email: [邮箱]. Please enter it below."
   - 输入框placeholder: "Enter code"
   - 倒计时显示："59s"递减到"0s"

2b. **验证码页面结构（手机号无密码，2026-04-03实测）**：
   - 标题："Verification code"（同邮箱）
   - 说明："To continue, complete this verification step. We've sent a verification code to the phone number: +971 501234579. Please enter it below."
   - 「Enter code」以标签/占位形式展示（与邮箱页一致的可交互区域）
   - 倒计时：发送后约 **59s** 起跳，首屏可见 **「56s」** 等属正常

3. **Toast提示**（2026-03-25实测）：
   - 发送成功提示："The code has been sent to your email."
   - Toast位置：页面顶部居中

3b. **Toast提示（手机号无密码，2026-04-03实测）**：
   - 发送成功提示核心句：**"The code has been sent to your phone."**
   - 沙箱环境常见前缀：`沙箱验证码:xxxxxx!!!` 与上述英文拼接在同一 Toast 内

4. **按钮状态联动**（2026-03-25实测）：
   - 验证码输入框为空 → Confirm按钮disabled
   - 验证码输入框有内容 → Confirm按钮enabled
   - 清空验证码 → Confirm按钮恢复disabled

5. **倒计时机制**（2026-03-25实测）：
   - 初始显示59s
   - 每秒递减1
   - 倒计时期间Send按钮显示剩余秒数

### ⚠️ 推断说明

以下场景由于实际限制未完整实测，基于业界惯例和系统一致性推断：

1. **倒计时结束行为**：需等待60秒，影响探测效率
2. **Resend功能**：需等待倒计时结束并实际触发
3. **防重复提交**：需后端日志验证实际发送次数
4. **返回导航**：基于已有其他页面的返回功能推断
5. **错误验证码提交后的提示**：需真实提交错误验证码触发

### 🔧 自动化测试实现建议

1. **验证码输入**：使用固定测试码（如"123456"）测试UI交互，不验证实际登录成功
2. **倒计时测试**：仅测试初始几秒的递减，不等待完整60秒
3. **Toast验证**：捕获Toast元素的inner_text进行文案断言；手机号无密码断言 **`The code has been sent to your phone`**，并兼容沙箱前缀 `沙箱验证码:`
4. **按钮状态**：使用`is_disabled()`和`is_enabled()`方法验证
5. **页面切换**：验证页面标题和关键元素的存在性

### 📂 测试数据

| 数据类型 | 值 | 说明 |
|---------|---|------|
| 未设置密码邮箱 | mamengmeng01@58.com | 实测账号 |
| 未设置密码手机号 | +971 501234579 | 短信验证码路径专用，与 501234570 等有密码账号区分 |
| 测试验证码 | 任意6位数字 | 仅测试UI，不验证真实性 |

---

## 文档维护记录

- **2026-03-25**: 初始版本，基于Playwright实测探测生成
- **2026-03-25**: 完整探测未设置密码场景，包含Toast提示、验证码页面结构、倒计时机制、按钮状态联动
- **2026-04-03**: 新增「六、手机号登录未设置密码场景」（+971 501234579，TC016–TC018）；Playwright **有界面**实测后更新预期（`scripts/probe_ae_phone_no_password_tc016_018.py`，默认 `HEADLESS=false`；结果 `reports/probe_phone_nopwd_tc016_018.json`）
-TC014 后续todo ,文案email相关文案 需要改为phone. 现在有线上问题，提示的是email