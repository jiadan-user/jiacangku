# AE 站 Job Preferences - Edit 功能测试用例

> **生成时间**：2026-03-02  
> **站点**：AE（阿联酋站）`https://ae.58v5.cn`  
> **目标页**：Job Preferences 编辑页 `https://aepub.58v5.cn/biz/en/jobPreference?returnUrl=...`  
> **入口**：Jobs 列表页顶部 Job Preference 标签栏 → 点击 **Edit** 链接  
> **测试账号**：`wangyongli@58.com / Qwer1234`  
> **录制方式**：MCP 浏览器实测（非猜测）  
> **去重说明**：已去除与 `ok-sg-首页Jobs金刚位-测试用例-20260227.md` 中场景相同的用例，仅保留 AE Edit 特有场景  
> **总用例数**：15条  
> **可自动化**：15条（14 全自动化 + 1 半自动化）

---

## 测试环境配置

| 字段 | 值 |
|------|---|
| 站点 | ae |
| 站点名称 | 阿联酋站 |
| 基础URL | https://ae.58v5.cn |
| 编辑页URL | https://aepub.58v5.cn/biz/en/jobPreference |
| 角色 |  |
| 账号名称 |  |
| 测试账号 | wangyongli@58.com |
| 测试密码 | Qwer1234 |

---

## 页面结构（MCP 实测）

| 模块 | 元素 | 说明 |
|------|------|------|
| Job Functions | 触发器（含已选 tag + 数量计数） | 最多 10 项，两栏面板（左：31个分类，右：子分类） |
| Location | 触发器（含已选 tag + 数量计数） | 最多 5 项，单栏 checkbox 列表（8个AE城市） |
| Salary | Pay type 下拉按钮 + AED 金额输入框 | Pay type：Yearly / Monthly / Hourly |
| Workplace Type | 多选 checkbox | Onsite / Remote / Hybrid，可选 |
| Job Type | 多选 checkbox | Full-time / Part-time / Contract / Internship / Temporary，可选 |
| 操作按钮 | Back / Continue | Back 返回列表，Continue 提交并回跳 returnUrl |

---

## 一、页面访问与入口（AE Edit 特有）

### TC001: 已登录用户从 Jobs 列表页点击 Edit 应进入 Job Preferences 编辑页并回填已有数据

- **前置条件**：已登录账号，且该账号已有 Job Preference 数据；当前在 `https://ae.58v5.cn/en/city/cate-jobs/?iconSource=jobs`
- **操作步骤**：
  1. 观察页面顶部 Job Preference 标签栏，确认 Edit 链接可见
  2. 点击 **Edit** 链接
- **预期结果**：
  - 跳转至 `https://aepub.58v5.cn/biz/en/jobPreference?returnUrl=...`（URL 含 returnUrl 参数）
  - 页面显示 "Job Preferences" 标题
  - 已有数据回填：Job Functions 触发器显示已选 tag 和计数、Location 显示已选城市、Salary 显示已填金额和 Pay type
- **优先级**：P0
- **测试类型**：正向 / 功能
- **UI自动化**：✅ 可自动化

---

## 二、数据回填（AE Edit 特有）

> SG 文件中的 Job Preferences 为「首次创建」场景，无数据回填。以下用例仅 AE Edit 流程特有。

### TC002: Edit 页面应正确回填已有 Job Functions 数据（tag + 计数）

- **前置条件**：账号已设置 Job Functions（如5项：Collections/Accounts Officers/Clerks/Accounts Payable/Accounts Receivable/Analysis & Reporting）
- **操作步骤**：
  1. 点击 Edit 进入编辑页
  2. 查看 Job Functions 触发器区域
- **预期结果**：
  - 触发器显示所有已选项目 tag（每项带 × 删除按钮）
  - 计数显示正确，如 `(5/10)`
- **优先级**：P1
- **测试类型**：正向 / 功能
- **UI自动化**：✅ 可自动化

---

### TC003: Edit 页面应正确回填已有 Location 数据（tag + 计数）

- **前置条件**：账号已设置 Location（如 Dubai）
- **操作步骤**：
  1. 点击 Edit 进入编辑页
  2. 查看 Location 触发器区域
- **预期结果**：
  - 触发器显示已选城市 tag（如 "Dubai ×"）
  - 计数显示正确，如 `(1/5)`
- **优先级**：P1
- **测试类型**：正向 / 功能
- **UI自动化**：✅ 可自动化

---

### TC004: Edit 页面应正确回填已有 Salary 数据（Pay type + AED 金额）

- **前置条件**：账号已设置 Salary（如 Yearly, 200569）
- **操作步骤**：
  1. 点击 Edit 进入编辑页
  2. 查看 Salary 区域
- **预期结果**：
  - Pay type 按钮显示已选类型（如 "Yearly"）
  - 金额输入框显示已填数值（格式化显示，如 "200,569"）
  - 货币前缀为 "AED"（区别于 SG 站的 "S$"）
- **优先级**：P1
- **测试类型**：正向 / 功能
- **UI自动化**：✅ 可自动化

---

### TC005: Edit 页面应正确回填已有 Workplace Type 和 Job Type 勾选状态

- **前置条件**：账号已设置 Workplace Type（如 Onsite + Remote）和 Job Type（如 Contract + Internship）
- **操作步骤**：
  1. 点击 Edit 进入编辑页
  2. 查看 Workplace Type 和 Job Type 区域
- **预期结果**：
  - 已选选项处于勾选状态（checkbox checked）
  - 未选选项处于未勾选状态
- **优先级**：P1
- **测试类型**：正向 / 功能
- **UI自动化**：✅ 可自动化

---

## 三、提交成功并回跳（AE Edit 特有）

### TC006: 三个必填字段全填后点击 Continue 应提交成功并回跳 returnUrl

- **前置条件**：Job Functions/Location/Salary 均已填写有效数据，当前在编辑页
- **操作步骤**：
  1. 确认三个必填字段均已填写
  2. 点击 Continue
- **预期结果**：
  - 提交成功（HTTP 响应无报错，无错误提示弹窗）
  - 页面跳转回 `https://ae.58v5.cn/en/city/cate-jobs/?iconSource=jobs`（returnUrl）
  - Jobs 列表页顶部 Job Preference 标签栏显示更新后的数据，且以下字段与本次提交内容一致：
    - Job Functions：已选 tag 数量和名称与提交时选择一致
    - Location：已选城市与提交时一致
    - Salary：Pay type 和金额与提交时一致
- **优先级**：P0
- **测试类型**：正向 / 核心流程
- **UI自动化**：✅ 可自动化

---

## 四、AE 站特有 Job Functions 分类（AE Edit 特有）

### TC007: AE 站特有分类 Oil & Gas 和 Skilled Trades 可正常选择并回显

- **前置条件**：Job Preferences 编辑页，Job Functions 已选项 < 10
- **操作步骤**：
  1. 点击 Job Functions 触发器，展开面板
  2. 点击左栏 "Oil & Gas"，在右栏选择一个子分类（如 Drilling），点击 Confirm
  3. 再次打开面板，点击 "Skilled Trades"，在右栏选择一个子分类（如 Electrician），点击 Confirm
- **预期结果**：
  - 两个 AE 特有分类均可正常展示子分类并完成选择
  - 触发器显示已选项 tag（含所选子分类名称），计数正确更新
- **优先级**：P1
- **测试类型**：正向 / 国际化（AE 站特有）
- **UI自动化**：✅ 可自动化

---

## 五、AE 站特有 Location（AE Edit 特有）

### TC008: AE 站 Location 列表应仅显示 UAE 城市（8个，不含新加坡城市）

- **前置条件**：在 Job Preferences 编辑页
- **操作步骤**：
  1. 点击 Location 触发器
  2. 查看全部 checkbox 选项
- **预期结果**：
  - 展开包含 8 个 UAE 城市的 checkbox 列表：Dubai、Abu Dhabi、Ras al Khaimah、Sharjah、Fujairah、Ajman、Umm al Quwain、Al Ain
  - 不显示新加坡城市（Singapore、Ang Mo Kio 等）
- **优先级**：P1
- **测试类型**：国际化（AE 站特有）
- **UI自动化**：✅ 可自动化

---

## 六、AE 站特有 Salary 货币（AE Edit 特有）

### TC009: AE 站编辑页 Salary 货币前缀应显示 AED（非 S$/USD）

- **前置条件**：在 Job Preferences 编辑页
- **操作步骤**：
  1. 查看 Salary 区域货币前缀文本
- **预期结果**：货币前缀显示 "AED"（区别于 SG 站的 "S$"）
- **优先级**：P1
- **测试类型**：国际化（AE 站特有）
- **UI自动化**：✅ 可自动化

---

## 七、Back 按钮与 returnUrl（AE Edit 特有）

> SG 文件中 Back 按钮回跳首页（TC003）；AE Edit 的 Back 回跳 returnUrl（Jobs 列表页），机制不同。
> TC010/TC011 按"有无数据修改"分别覆盖两种不同的 Back 行为分支。

### TC010: 未修改任何数据时点击 Back 应直接跳回 Jobs 列表页（无确认弹窗）

- **前置条件**：已登录，直接进入编辑页（含 returnUrl 参数），**不修改任何字段**
- **操作步骤**：
  1. 通过 `https://aepub.58v5.cn/biz/en/jobPreference?returnUrl=...` 直接进入编辑页
  2. 不做任何字段修改
  3. 点击 **Back** 按钮
- **预期结果**：
  - **不弹出** Unsaved Changes 确认弹窗
  - 直接跳转回 returnUrl 对应的 Jobs 列表页（`https://ae.58v5.cn/en/city/cate-jobs/?iconSource=jobs`）
- **优先级**：P1
- **测试类型**：正向 / 功能
- **UI自动化**：✅ 可自动化

---

### TC011: 修改数据后点击 Back 应弹出 Unsaved Changes 确认弹窗，点击 Discard 放弃修改并回跳

- **前置条件**：已登录，进入编辑页后**修改至少一个字段**（如切换 Workplace Type）
- **操作步骤**：
  1. 进入编辑页
  2. 修改任意字段（如勾选 / 取消勾选 Hybrid）
  3. 点击 **Back** 按钮
  4. 弹出 Unsaved Changes 弹窗后，点击 **Discard**
- **预期结果**：
  - 点击 Back 后弹出标题为 "Unsaved Changes" 的确认弹窗
  - 点击 Discard 后跳转回 Jobs 列表页（`https://ae.58v5.cn/en/city/cate-jobs/?iconSource=jobs`）
  - Jobs 列表页显示的 Job Preference 数据为修改前的旧数据（本次修改未保存）
- **优先级**：P1
- **测试类型**：正向 / 功能
- **UI自动化**：✅ 可自动化

---

### TC012: 篡改 returnUrl 参数为外部域名后点击 Back 应跳转至合法域名（Open Redirect 验证）

- **前置条件**：已在编辑页
- **操作步骤**：
  1. 手动将地址栏 returnUrl 参数改为 `https://evil.example.com`
  2. 点击 Back 按钮
- **预期结果**：跳转被限制在合法域名内，fallback 至 AE 招聘列表页（`https://ae.58v5.cn/en/city/cate-jobs/?iconSource=jobs`）
- **实际行为（20260305 执行记录）**：系统检测到恶意 returnUrl 后，自动将其替换为 Cookie/Session 中记录的合法 returnUrl，并重定向回编辑页（含合法 returnUrl），未跳至恶意域名。Open Redirect 防护生效。注：早期版本脚本未带合法 returnUrl 直接访问恶意 URL，导致 fallback 至 SG 城市页（已修复步骤，改为先进入合法编辑页再篡改 returnUrl，与手工测试一致）。
- **优先级**：P2
- **测试类型**：安全 / Open Redirect
- **UI自动化**：✅ 可自动化

---

## 八、会话与状态（AE Edit 特有）

### TC013: 刷新 Edit 页面后已保存数据应重新从服务端回填（不显示空表单）

- **前置条件**：在 Edit 页面，已有回填数据（如 5 个 Job Functions、Dubai、Yearly 200569）。此前置数据为测试账号 `wangyongli@58.com` 的预设固定数据（可通过 TC006 提交后复用），执行本用例前应确保该账号已保存 Job Preference 数据。
- **操作步骤**：
  1. 记录当前回填内容（Job Functions 数量/名称、Location、Salary Pay type 和金额）
  2. 按 F5 刷新页面
  3. 等待页面加载完成
- **预期结果**：
  - 页面重新加载后，数据重新从服务端回填，内容与刷新前一致（逐字段核对）
  - 不出现空表单（区别于 SG 首次创建场景：刷新后恢复空状态）
- **优先级**：P2
- **测试类型**：会话 / 数据持久化（AE Edit 特有行为）
- **UI自动化**：✅ 可自动化

---

### TC014: 登录状态过期后访问编辑页应重定向登录（JS 清除 Cookie 模拟）

- **前置条件**：已在 AE 站登录
- **操作步骤**：
  1. 通过 `document.cookie` 或 `localStorage.clear()` 清除登录态
  2. 直接访问编辑页 URL `https://aepub.58v5.cn/biz/en/jobPreference?returnUrl=...`
- **预期结果**：页面重定向至登录流程，不展示编辑表单
- **优先级**：P2
- **测试类型**：会话 / 安全
- **UI自动化**：✅ 可自动化（通过 JS 清除 Cookie 模拟）

---

## 九、安全与越权（AE Edit 特有）

### TC015: 用 A 账号 Session 访问 Edit 页面应只能查看/修改自己的 Job Preference

- **前置条件**：两个不同账号均已设置 Job Preference，当前以 A 账号登录
- **操作步骤**：
  1. 以 A 账号登录，进入 Edit 页，记录页面回填的 Job Functions 等数据
  2. 修改地址栏中可能含有用户标识的参数（若有），尝试访问 B 账号数据
- **预期结果**：
  - Edit 页仅展示 A 账号自己的 Job Preference 数据
  - 无法通过修改 URL 参数查看 B 账号数据（返回 401/403 或显示 A 账号数据）
- **优先级**：P1
- **测试类型**：安全 / 横向越权
- **UI自动化**：⚠️ 半自动化（需准备两个不同账号的 session，自动化难度较高；建议手工执行或单独录制）

---

## 测试统计

### 用例概览

- 总用例数：15 条（TC010/TC011 覆盖 Back 按钮无修改/有修改两个分支）
- 全自动化：14 条（93%）
- 半自动化：1 条（TC015 横向越权）
- 不可自动化：0 条
- 已去除与 SG 文件重叠场景：37 条

### 去重说明

以下场景已在 `ok-sg-首页Jobs金刚位-测试用例-20260227.md` 中覆盖，本文件不重复：

| 去除场景 | 对应 SG 用例 |
|---------|------------|
| 未登录访问编辑页重定向登录 | SG TC032 |
| Job Functions 面板展开两栏 | SG TC011 |
| 左栏分类切换右栏子分类 | SG TC012 |
| 选择子分类后 Confirm 更新触发器 | SG TC012 |
| Job Functions 最多 10 项 / 超过上限无法选择 | SG TC013 |
| × 删除单个已选项 / Clear 清空 / 清空后重选 | SG TC015、TC016 |
| Location 面板展开 / 勾选 Confirm / 最多5项 / 超限 / 取消勾选 / Clear / 清空后重选 | SG TC017-TC022 |
| Pay type 展开 Yearly/Monthly/Hourly | SG TC023 |
| 切换 Pay type 文案更新 | SG TC035、TC037、TC039、TC041、TC042、TC043 |
| Salary 输入正数 / 非法字符 / 0 / 超大值 / 清空必填校验 | SG TC024-TC026、TC038、TC044、TC045 |
| Workplace Type / Job Type 多选 | SG TC030 |
| 三必填全空 / 单字段空校验错误提示 | SG TC004-TC007 |
| Back 回跳（SG 回首页，AE 回 returnUrl，机制不同，本文件重写） | SG TC003 |

### 按优先级分布

| 优先级 | 总数 | 可自动化 | 自动化率 |
|--------|------|---------|---------|
| P0 | 2 | 2 | 100% |
| P1 | 10 | 10 | 100% |
| P2 | 3 | 3（1 条半自动化） | 100% |
| **合计** | **15** | **15**（14 全自动化 + 1 半自动化） | **100%** |
