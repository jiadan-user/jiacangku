# AE 站 Job Preferences - 未登录入口（Add Job Preference）功能测试用例

> **生成时间**：2026-03-05  
> **站点**：AE（阿联酋站）`https://ae.58v5.cn`  
> **目标流程**：未登录用户 → Jobs 列表页点击 "Add Job Preference" → 弹出登录弹窗 → 完成登录 → 跳转到 Job Preferences 编辑页  
> **入口 URL**：`https://ae.58v5.cn/en/city/cate-jobs/?iconSource=jobs`  
> **编辑页 URL**：`https://aepub.58v5.cn/biz/en/jobPreference`（无 returnUrl 参数，区别于 Edit 入口）  
> **测试账号**：`wangyongli@58.com / Qwer1234`  
> **录制方式**：MCP 浏览器实测（2026-03-05 实际录制）  
> **与原文件关系**：本文件为 `ok-ae-JobPreferences-Edit-测试用例-20260302.md` 的**补充**，专注于未登录入口的新流程，原文件侧重于已登录状态的 Edit 入口
> **总用例数**：5 条  
> **可自动化**：5 条（全自动化）

---

## 测试环境配置

| 字段 | 值 |
|------|---|
| 站点 | ae |
| 站点名称 | 阿联酋站 |
| 基础URL | https://ae.58v5.cn |
| 入口URL | https://ae.58v5.cn/en/city/cate-jobs/?iconSource=jobs |
| 编辑页URL | https://aepub.58v5.cn/biz/en/jobPreference |
| 角色 | jobseeker |
| 账号名称 | wangyongli_ae |
| 测试账号 | wangyongli@58.com |
| 测试密码 | Qwer1234 |

---

## 页面结构（MCP 实测 - 2026-03-05）

### 未登录状态 - Jobs 列表页（入口区域）

| 元素 | 说明 |
|------|------|
| Add Job Preference 卡片 | 排在列表顶部第一个位置，包含图标、"+ Add Job Preference" 标题、"Unlock more opportunities tailored for you." 副文本 |
| 登录弹窗（dialog） | 点击 Add Job Preference 后弹出，不跳转页面 |

### 登录弹窗（仅作结构说明，弹窗功能用例不在本文件覆盖范围）

| 元素 | 说明 |
|------|------|
| 两步登录 | 邮箱输入 → Continue → 密码输入 → Log in |
| 第三方登录 | Google / Facebook / Apple（OR 分隔线下方） |
| × 关闭按钮 | 右上角，关闭弹窗 |

### 登录后 - Job Preferences 编辑页

| 模块 | 元素 | 说明 |
|------|------|------|
| Job Functions | 触发器（含已选 tag + 数量计数） | 最多 10 项，回填已有数据 |
| Location | 触发器（含已选 tag + 数量计数） | 最多 5 项，回填已有数据 |
| Salary | Pay type 下拉 + AED 金额输入框 | 回填已有 Pay type 和金额 |
| Workplace Type | 多选 checkbox | Onsite / Remote / Hybrid |
| Job Type | 多选 checkbox | Full-time / Part-time / Contract / Internship / Temporary |
| Back / Continue | 操作按钮 | Back 跳转列表页（无 returnUrl，行为待验证） |

---

## 一、Add Job Preference 入口展示

### TC001: 未登录用户访问 Jobs 列表页应在顶部显示 "Add Job Preference" 卡片

- **前置条件**：未登录状态；当前在 `https://ae.58v5.cn/en/city/cate-jobs/?iconSource=jobs`
- **操作步骤**：
  1. 以未登录状态访问 Jobs 列表页
  2. 查看列表顶部第一个位置的内容
- **预期结果**：
  - 列表顶部第一个元素为 "Add Job Preference" 卡片（不是 Job 列表项）
  - 卡片显示标题 "+ Add Job Preference"
  - 卡片显示副文本 "Unlock more opportunities tailored for you."
  - 卡片整体可点击（cursor: pointer）
  - 无 "Edit" 链接（已登录才显示 Edit）
- **优先级**：P0
- **测试类型**：正向 / 功能 / UI
- **UI自动化**：✅ 可自动化

---

### TC002: 已登录用户访问 Jobs 列表页不应显示 "Add Job Preference" 卡片，而是显示 Job Preference 标签栏

- **前置条件**：已登录状态（账号已有 Job Preference 数据）
- **操作步骤**：
  1. 以已登录状态访问 Jobs 列表页
  2. 查看列表顶部
- **预期结果**：
  - 不显示 "Add Job Preference" 卡片
  - 显示已选 Job Functions 标签（如 Accounts Officers/Clerks 等）+ "Edit" 链接
  - Edit 链接可点击，跳转到编辑页（含 returnUrl 参数）
- **优先级**：P1
- **测试类型**：正向 / 功能
- **UI自动化**：✅ 可自动化

---

## 二、登录成功后跳转到编辑页（核心流程）

### TC003: 未登录用户通过 "Add Job Preference" 入口登录后应直接跳转到编辑页（无 returnUrl 参数）

- **前置条件**：未登录状态，当前在 Jobs 列表页
- **操作步骤**：
  1. 点击 "Add Job Preference" 卡片，弹出登录弹窗
  2. 输入邮箱 `wangyongli@58.com`，点击 Continue
  3. 输入密码 `Qwer1234`，点击 Log in
- **预期结果**：
  - 登录成功，弹窗关闭
  - 页面跳转至 `https://aepub.58v5.cn/biz/en/jobPreference`
  - **URL 不包含 returnUrl 参数**（区别于 Edit 入口）
  - 页面显示 "Job Preferences" 标题
  - 已有数据回填（Job Functions / Location / Salary 等）
  - 右上角显示登录用户名（如 OKer_fm6gntd）
- **优先级**：P0
- **测试类型**：正向 / 核心流程
- **UI自动化**：✅ 可自动化

---

## 三、Add Job Preference 入口与 Edit 入口的差异（关键区分）

### TC004: 通过 Add Job Preference 入口进入的编辑页 Back 按钮行为（无 returnUrl）

- **前置条件**：通过 TC012 流程进入编辑页（URL 为 `https://aepub.58v5.cn/biz/en/jobPreference`，无 returnUrl 参数）；**不修改任何字段**
- **操作步骤**：
  1. 确认当前 URL 无 returnUrl 参数
  2. 不修改任何字段
  3. 点击 Back 按钮
- **预期结果**：
  - Back 的回跳目标为Jobs列表页，并且列表页展示编辑页所选的岗位偏好类目
- **优先级**：P1
- **测试类型**：正向 / 功能（入口差异验证）
- **UI自动化**：✅ 可自动化
- **备注**：此用例用于明确区分 Add 入口（无 returnUrl）与 Edit 入口（有 returnUrl）的 Back 行为差异

---

### TC005: 通过 Add Job Preference 入口完成编辑提交后应提交成功

- **前置条件**：通过 TC003 流程进入编辑页，三个必填字段（Job Functions / Location / Salary）均已有有效数据
- **操作步骤**：
  1. 进入编辑页后已有回填数据，修改任意选项
  2. 点击 Continue
- **预期结果**：
  - 提交成功（无报错弹窗），用户偏好更新
  - 页面跳转到Jobs列表页，并且列表页展示编辑页所选的岗位偏好类目
- **优先级**：P0
- **测试类型**：正向 / 核心流程
- **UI自动化**：✅ 可自动化

---

---

## 测试统计

### 用例概览

- **总用例数**：5 条
- **全自动化**：5 条（100%）
- **半自动化**：0 条
- **不可自动化**：0 条

### 与 `ok-ae-JobPreferences-Edit-测试用例-20260302.md` 的关系

| 维度 | 原文件（Edit 入口） | 本文件（Add 入口） |
|------|-------------------|--------------------|
| 入口 | 已登录 → Jobs 列表 → Edit 链接 | 未登录 → Jobs 列表 → Add Job Preference 卡片 |
| 跳转方式 | 直接跳转编辑页 | 弹出登录弹窗 → 登录后跳转 |
| 编辑页 URL | 含 `returnUrl` 参数 | 无 `returnUrl` 参数 |
| Back 行为 | 跳转回 returnUrl（Jobs 列表页） | fallback 行为（待验证） |
| 核心差异 | 已登录流程 | 未登录触发登录流程 |

### 关键发现（MCP 实测 2026-03-05）

| 发现项 | 详情 |
|-------|------|
| 入口形式 | Add Job Preference 为**弹窗**形式，不跳转页面 |
| 登录流程 | 两步式：邮箱输入 → Continue → 密码输入 → Log in |
| 账号识别 | 识别已有账号后显示 "Welcome back!"，识别新账号则进入注册流程 |
| 登录后 URL | `https://aepub.58v5.cn/biz/en/jobPreference`（无 returnUrl） |
| 数据回填 | 登录后编辑页正确回填已有数据 |
| 第三方登录 | 支持 Google / Facebook / Apple 三种第三方登录（本次未录制完整流程） |

### 按优先级分布

| 优先级 | 总数 | 可自动化 | 自动化率 |
|--------|------|---------|---------|
| P0 | 3 | 3 | 100% |
| P1 | 3 | 3 | 100% |
| **合计** | **6** | **6**（全自动化） | **100%** |

---

## 附录：MCP 录制证明存档

### 主流程录制（TC003）证明

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`zhaopin/test_ae_job_preferences_add_from_list.py::test_ae_add_pref_login_via_banner_should_redirect_to_edit_page`）

**【MCP JavaScript 代码】**（来自 `### Ran Playwright code` 真实输出）

```js
// 步骤1：注销（模拟未登录状态）
await page.getByText('OKer_fm6gntd').click();
await page.getByText('Log Out').click();

// 步骤2：导航到 Jobs 列表页并点击 Add Job Preference
await page.goto('https://ae.58v5.cn/en/city/cate-jobs/?iconSource=jobs');
await page.getByText('Add Job PreferenceUnlock more').click();

// 步骤3：输入邮箱并点击 Continue
await page.getByRole('textbox', { name: 'Email or phone number' }).fill('wangyongli@58.com');
await page.getByRole('button', { name: 'Continue' }).click();

// 步骤4：输入密码并点击 Log in
await page.getByRole('textbox', { name: 'Enter password' }).fill('Qwer1234');
await page.getByRole('button', { name: 'Log in' }).click();

// 验证：URL 跳转到编辑页
// page.url() → 'https://aepub.58v5.cn/biz/en/jobPreference'
```

**【关键 ref 编号（来自真实 snapshot）】**
- Add Job Preference 卡片：`ref=e61`（snapshot #3）
- Email 输入框：`ref=e898`（snapshot #4）
- Continue 按钮：`ref=e900`
- 密码输入框：`ref=e943`（snapshot #5）
- Log in 按钮：`ref=e949`

**【验证证明】**
- 验证点：登录后 URL = `https://aepub.58v5.cn/biz/en/jobPreference`
- Job Preferences 标题显示正确
- 数据回填：Job Functions 5 项，Location: Dubai，Salary: Yearly 200,569
- MCP调用统计：navigate:2 snapshot:5 click:5 type:2 screenshot:3
