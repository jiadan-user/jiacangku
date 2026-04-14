# SG 站 Job Preferences - Add Job Preference 入口功能测试用例

> **生成时间**：2026-03-05  
> **站点**：SG（新加坡站）`https://sg.58v5.cn`  
> **目标流程**：
> - 流程A（未登录）：未登录用户 → Jobs 列表页点击 "Add Job Preference" → 弹出登录弹窗 → 完成登录 → 跳转到 Job Preferences 添加页
> - 流程B（已登录）：已登录用户 → Jobs 列表页点击 "Add Job Preference" → 直接跳转到 Job Preferences 添加页（无弹窗）
> **入口 URL**：`https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs`  
> **添加页 URL**：`https://sgpub.58v5.cn/biz/en/jobPreference`（无 returnUrl 参数，区别于 Edit 入口）  
> **测试账号**：`wang@58.com / Qwer1234`（账号无已有 Job Preference 数据，添加页为空表单）
> **录制方式**：Playwright Python 脚本实测（2026-03-05 实际录制）  
> **与原文件关系**：本文件为 `ok-ae-JobPreferences-AddFromList-测试用例-20260305.md` 的 **SG 站平行版**，专注于 SG 站特有行为（货币 S$、城市 Singapore）及已登录用户直接进入添加页的流程  
> **总用例数**：8 条  
> **可自动化**：8 条（全自动化）

---

## 测试环境配置

| 字段 | 值 |
|------|---|
| 站点 | sg |
| 站点名称 | 新加坡站 |
| 基础URL | https://sg.58v5.cn |
| 入口URL | https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs |
| 添加页URL | https://sgpub.58v5.cn/biz/en/jobPreference |
| 角色 | jobseeker |
| 账号名称 | wang_sg |
| 测试账号 | wang@58.com |
| 测试密码 | Qwer1234 |

---

## 页面结构（Playwright 实测 - 2026-03-05）

### 未登录/已登录状态 - Jobs 列表页（入口区域）

| 元素 | 说明 |
|------|------|
| Add Job Preference 卡片 | 排在列表顶部第一个位置，包含图标（zhaopin-list-post-add.png）、"Add Job Preference" 标题、"Unlock more opportunities tailored for you." 副文本 |
| 登录弹窗（dialog） | 未登录时点击 Add Job Preference 后弹出，URL 不变，停留在列表页 |
| 直接跳转 | 已登录时点击 Add Job Preference 后直接跳转，无弹窗 |

**关键差异（SG vs AE）**：
- **SG 站已登录 + 无已有偏好** → 列表页仍显示 "Add Job Preference" 卡片（同未登录态）
- **AE 站已登录 + 有已有偏好** → 列表页显示 Job Functions 标签 + "Edit" 链接

### 登录弹窗（仅作结构说明）

| 元素 | 说明 |
|------|------|
| 两步登录 | 邮箱/手机号输入 → Continue → 密码输入 → Log in |
| 欢迎语 | 新账号显示 "Welcome to OK.com"，已有账号显示 "Welcome back!" |
| Cookie 弹窗 | 首次访问触发，需先 Accept 才能正常点击登录按钮 |
| 第三方登录 | Google / Facebook / Apple（OR 分隔线下方） |
| × 关闭按钮 | 右上角，关闭弹窗 |

### 已登录/登录后 - Job Preferences 添加页

| 模块 | 元素 | 说明 |
|------|------|------|
| 页面标题 | "Job Preferences" | 顶部标题 |
| Job Functions | 触发器 "Select preferred job function (0/10)" | 最多 10 项，新用户为空 |
| Location | 触发器 "Select preferred work location (0/5)" | 最多 5 项，新用户为空 |
| Salary | Pay type 下拉 "Select pay type" + S$（新加坡元）金额输入框 | 新用户为空，默认 Yearly |
| Workplace Type | 多选 checkbox | Onsite / Remote / Hybrid |
| Job Type | 多选 checkbox | Full-time / Part-time / Contract / Internship / Temporary |
| Back 按钮 | 返回 Jobs 列表页 | URL: `https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs` |
| Continue 按钮 | 提交表单 | 三个必填字段均为空时点击显示校验错误 |

### 必填字段校验错误文案（实测）

| 字段 | 错误提示文案 |
|------|------|
| Job Functions | "Don't leave this field empty." |
| Location | "Don't leave this field empty." |
| Salary | "Don't leave this field empty." |

---

## 一、Add Job Preference 入口展示（已登录用户 - 无已有偏好）

### TC001: 已登录且无 Job Preference 数据的用户访问 Jobs 列表页应显示 "Add Job Preference" 卡片

- **前置条件**：已登录状态（账号 wang@58.com 无 Job Preference 数据）；当前在 `https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs`
- **操作步骤**：
  1. 以已登录状态访问 Jobs 列表页
  2. 查看列表顶部第一个位置的内容
- **预期结果**：
  - 列表顶部第一个元素为 "Add Job Preference" 卡片（与未登录态相同）
  - 卡片显示标题 "Add Job Preference"
  - 卡片显示副文本 "Unlock more opportunities tailored for you."
  - 卡片整体可点击
  - 不显示 "Edit" 链接（已有偏好时才显示）
  - 不显示已选 Job Functions 标签
- **优先级**：P0
- **测试类型**：正向 / 功能 / UI
- **UI自动化**：✅ 可自动化

---

### TC002: 未登录用户访问 Jobs 列表页应显示 "Add Job Preference" 卡片

- **前置条件**：未登录状态；当前在 `https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs`
- **操作步骤**：
  1. 以未登录状态访问 Jobs 列表页
  2. 查看列表顶部第一个位置的内容
- **预期结果**：
  - 列表顶部第一个元素为 "Add Job Preference" 卡片
  - 卡片显示标题 "Add Job Preference"
  - 卡片显示副文本 "Unlock more opportunities tailored for you."
  - 卡片整体可点击（cursor: pointer）
  - 无 "Edit" 链接
- **优先级**：P0
- **测试类型**：正向 / 功能 / UI
- **UI自动化**：✅ 可自动化

---

## 二、已登录用户直接进入添加页（核心流程 - 流程B）

### TC003: 已登录用户点击 "Add Job Preference" 应直接跳转到添加页（无弹窗，无 returnUrl）

- **前置条件**：已登录状态（wang@58.com），当前在 Jobs 列表页
- **操作步骤**：
  1. 以已登录状态访问 `https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs`
  2. 点击 "Add Job Preference" 卡片
- **预期结果**：
  - 无登录弹窗弹出
  - 直接跳转至 `https://sgpub.58v5.cn/biz/en/jobPreference`
  - **URL 不包含 returnUrl 参数**
  - 页面显示 "Job Preferences" 标题
  - 右上角显示登录用户名（如 OKerSG_sjwp7cj）
  - Job Functions、Location、Salary 均为空（账号无已有数据）
- **优先级**：P0
- **测试类型**：正向 / 核心流程
- **UI自动化**：✅ 可自动化

---

### TC004: 添加页应正确显示三个必填字段且均为空（新用户无已有数据）

- **前置条件**：已登录（wang@58.com），已通过 TC003 流程进入添加页
- **操作步骤**：
  1. 进入 `https://sgpub.58v5.cn/biz/en/jobPreference`
  2. 查看页面各字段初始状态
- **预期结果**：
  - Job Functions 触发器显示 "Select preferred job function (0/10)"（空态）
  - Location 触发器显示 "Select preferred work location (0/5)"（空态）
  - Salary 下拉显示 "Select pay type"（空态），金额输入框旁显示 S$（新加坡元）
  - Workplace Type：Onsite / Remote / Hybrid 均未勾选
  - Job Type：Full-time / Part-time / Contract / Internship / Temporary 均未勾选
  - Continue 按钮可点击（非 disabled）
  - Back 按钮可点击
- **优先级**：P1
- **测试类型**：正向 / 数据回填 / UI
- **UI自动化**：✅ 可自动化

---

## 三、必填字段校验

### TC005: 未填任何必填字段直接点击 Continue 应显示三个校验错误

- **前置条件**：已登录，已进入添加页，三个必填字段（Job Functions / Location / Salary）均为空
- **操作步骤**：
  1. 不填任何字段
  2. 直接点击 Continue 按钮
- **预期结果**：
  - 页面不跳转，停留在添加页
  - Job Functions 字段下方显示 "Don't leave this field empty."
  - Location 字段下方显示 "Don't leave this field empty."
  - Salary 字段下方显示 "Don't leave this field empty."
  - 共显示 3 条错误提示
- **优先级**：P0
- **测试类型**：负向 / 表单校验
- **UI自动化**：✅ 可自动化

---

## 四、Back 按钮行为

### TC006: 通过 Add Job Preference 入口进入的添加页点击 Back 应跳回 Jobs 列表页

- **前置条件**：已登录，通过 TC003 流程进入添加页（URL 为 `https://sgpub.58v5.cn/biz/en/jobPreference`，无 returnUrl）；不修改任何字段
- **操作步骤**：
  1. 确认当前 URL 无 returnUrl 参数
  2. 不修改任何字段
  3. 点击 Back 按钮
- **预期结果**：
  - 跳转回 Jobs 列表页：`https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs`
  - 列表页仍显示 "Add Job Preference" 卡片（因未提交，偏好未保存）
- **优先级**：P1
- **测试类型**：正向 / 功能（Back 按钮行为）
- **UI自动化**：✅ 可自动化
- **备注**：区分于 Edit 入口（Edit 入口的 URL 含 returnUrl 参数）

---

## 五、未登录入口登录后跳转（流程A）

### TC007: 未登录用户通过 "Add Job Preference" 入口登录后应直接跳转到添加页（无 returnUrl）

- **前置条件**：未登录状态，当前在 Jobs 列表页
- **操作步骤**：
  1. 访问 `https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs`
  2. 处理 Cookie 弹窗（点击 Accept）
  3. 点击 "Add Job Preference" 卡片，弹出登录弹窗
  4. 在弹窗中输入邮箱 `wang@58.com`，点击 Continue
  5. 输入密码 `Qwer1234`，点击 Log in
- **预期结果**：
  - 弹窗显示 "Welcome back!"（已有账号识别）
  - 登录成功，弹窗关闭
  - 页面跳转至 `https://sgpub.58v5.cn/biz/en/jobPreference`
  - **URL 不包含 returnUrl 参数**
  - 页面显示 "Job Preferences" 标题
  - 右上角显示登录用户名（如 OKerSG_sjwp7cj）
- **优先级**：P0
- **测试类型**：正向 / 核心流程
- **UI自动化**：✅ 可自动化

---

### TC008: 未登录用户点击 "Add Job Preference" 应弹出登录弹窗且 URL 不跳转

- **前置条件**：未登录状态，当前在 Jobs 列表页
- **操作步骤**：
  1. 以未登录状态访问 Jobs 列表页
  2. 记录当前 URL
  3. 点击 "Add Job Preference" 卡片
- **预期结果**：
  - 弹出登录弹窗（dialog）
  - URL 保持不变（仍为 `https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs`）
  - 弹窗显示 "Welcome to OK.com" 标题
  - 弹窗包含邮箱/手机号输入框和 Continue 按钮
  - 弹窗包含 OR 分隔线和第三方登录选项（Google / Facebook / Apple）
- **优先级**：P0
- **测试类型**：正向 / 功能
- **UI自动化**：✅ 可自动化

---

---

## 测试统计

### 用例概览

- **总用例数**：8 条
- **全自动化**：8 条（100%）
- **半自动化**：0 条
- **不可自动化**：0 条

### 与 `ok-ae-JobPreferences-AddFromList-测试用例-20260305.md` 的关系（SG vs AE 差异）

| 维度 | AE 文件 | 本文件（SG 站） |
|------|---------|----------------|
| 账号特征 | 已有 Job Preference 数据，登录后显示 Edit | 无已有数据，已登录仍显示 Add Job Preference |
| 已登录行为 | 点击 Edit 跳转（Edit 入口） | 点击 Add Job Preference 直接跳转添加页（无弹窗）|
| 未登录行为 | 点击 Add Job Preference → 弹出登录弹窗 | 点击 Add Job Preference → 弹出登录弹窗（相同）|
| 添加页 URL | `https://aepub.58v5.cn/biz/en/jobPreference` | `https://sgpub.58v5.cn/biz/en/jobPreference` |
| 货币 | AED（迪拉姆） | S$（新加坡元）|
| 城市路径 | `/en/city/cate-jobs/` | `/en/city-singapore/cate-jobs/` |
| 数据回填 | 有已有数据回填 | 空表单（新用户）|

### 按优先级分布

| 优先级 | 总数 | 可自动化 | 自动化率 |
|--------|------|---------|---------|
| P0 | 5 | 5 | 100% |
| P1 | 3 | 3 | 100% |
| **合计** | **8** | **8（全自动化）** | **100%** |

---

## 附录：Playwright 实测证明存档（2026-03-05）

### 录制环境

- Playwright Python（venv）
- Chrome Chromium headless
- 录制时间：2026-03-05

### 主流程录制证明（TC003 + TC007）

**【MCP JavaScript 代码（由 Playwright Python 实测转换）】**

```js
// ====== 流程B：已登录用户直接进入添加页（TC003）======

// 步骤1：登录
await page.goto('https://sg.58v5.cn/en/city-singapore/');
// 处理 Cookie 弹窗
await page.locator('.CookieConsent_cookieConsent__xhIgs button').first().click();
await page.getByText('Log in / Register').click();
// 两步登录
const dialog = page.locator('[role=dialog]').first();
await dialog.getByRole('textbox').first().fill('wang@58.com');
await dialog.getByRole('button', { name: 'Continue' }).click();
await dialog.getByRole('textbox').first().fill('Qwer1234');
await dialog.getByRole('button', { name: 'Log in' }).evaluate('el => el.click()');
// 已登录，用户名 OKerSG_sjwp7cj 显示在右上角

// 步骤2：访问 Jobs 列表页，点击 Add Job Preference
await page.goto('https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs');
await page.getByText('Add Job Preference').first().click();

// 验证：直接跳转到添加页，无弹窗
// page.url() → 'https://sgpub.58v5.cn/biz/en/jobPreference'
// dialog 不存在

// ====== 流程A：未登录用户通过弹窗登录（TC007）======

// 步骤1：未登录，访问 Jobs 列表页
await page.goto('https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs');
// 处理 Cookie 弹窗
await page.locator('.CookieConsent_cookieConsent__xhIgs button').first().click();
// 点击 Add Job Preference → 弹出登录弹窗
await page.getByText('Add Job Preference').first().click();
// page.url() 仍为 'https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs'

// 步骤2：在弹窗中登录
const loginDialog = page.locator('[role=dialog]').first();
await loginDialog.getByRole('textbox').first().fill('wang@58.com');
await loginDialog.getByRole('button', { name: 'Continue' }).click();
// 弹窗显示 "Welcome back!" + 密码输入框
await loginDialog.getByRole('textbox').first().fill('Qwer1234');
await loginDialog.getByRole('button', { name: 'Log in' }).evaluate('el => el.click()');

// 验证：跳转到添加页
// page.url() → 'https://sgpub.58v5.cn/biz/en/jobPreference'（无 returnUrl）
```

**【TC005：空表单校验录制证明】**

```js
// 进入添加页
await page.goto('https://sgpub.58v5.cn/biz/en/jobPreference');
// 直接点击 Continue（不填任何字段）
await page.getByRole('button', { name: 'Continue' }).evaluate('el => el.click()');

// 验证：3条错误
// page.locator('[class*="error"], [class*="Error"]').count() === 3
// 错误文案：'Don\'t leave this field empty.'（3处）
```

**【TC006：Back 按钮录制证明】**

```js
// 进入添加页后点击 Back
await page.getByRole('button', { name: 'Back' }).click();
// page.url() → 'https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs'
```

**【关键 ref 编号（来自 Playwright 实测快照）】**
- Add Job Preference 卡片：`class="PostCard_zhaopinComponentsListWraperPost__ec58w"`
- Email 输入框（dialog 内）：`dialog.getByRole('textbox').first()`
- Continue 按钮：`dialog.getByRole('button', { name: 'Continue' })`
- Password 输入框：`dialog.getByRole('textbox').first()`（密码步骤）
- Log in 按钮：`dialog.getByRole('button', { name: 'Log in' })`
- Cookie Accept 按钮：`.CookieConsent_cookieConsent__xhIgs button`
- Back 按钮：`page.getByRole('button', { name: 'Back' })`
- Continue 按钮（添加页）：`page.getByRole('button', { name: 'Continue' })`

**【验证证明】**
- TC003：已登录后点击 Add Job Preference → URL = `https://sgpub.58v5.cn/biz/en/jobPreference`（无 returnUrl）✅
- TC004：添加页显示空表单：Job Functions(0/10)、Location(0/5)、Salary(空) ✅
- TC005：空表单提交 → 3条 "Don't leave this field empty." 错误 ✅
- TC006：Back 按钮 → URL = `https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs` ✅
- TC007：未登录点击 → 弹窗 → 登录 → URL = `https://sgpub.58v5.cn/biz/en/jobPreference` ✅
- TC008：未登录点击 → dialog 弹出，URL 不变 ✅
- MCP调用统计：navigate:6 click:12 fill:8 evaluate:6 wait:15

### SG 站特有关键发现（区别于 AE 站）

| 发现项 | 详情 |
|-------|------|
| 已登录无偏好时的状态 | 已登录用户（无已有偏好）访问 Jobs 列表，仍显示 "Add Job Preference"（与未登录态相同） |
| 直接跳转 | 已登录用户点击 "Add Job Preference" → **直接跳转**添加页（无弹窗，区别于未登录需要弹窗登录）|
| Cookie 弹窗必须处理 | SG 站首次访问必定出现 Cookie Consent 弹窗，不处理则 Log in 按钮被遮挡 |
| 货币符号 | 添加页 Salary 字段旁显示 S$（新加坡元），非 AED |
| 城市路径格式 | `/en/city-singapore/cate-jobs/`（含具体城市名），AE 站为 `/en/city/cate-jobs/` |
| 添加页 URL | `sgpub.58v5.cn`（非 `aepub.58v5.cn`） |
| Back 跳转目标 | `https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs` |
