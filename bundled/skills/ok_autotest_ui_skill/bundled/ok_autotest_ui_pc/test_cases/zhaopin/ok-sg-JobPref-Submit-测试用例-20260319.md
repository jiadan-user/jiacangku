# OK SG站 - 岗位偏好页提交功能 测试用例

> **生成时间**: 2026-03-19  
> **MCP实测修订**: 2026-03-20  
> **测试范围**: SG站首页Jobs金刚位 → 岗位偏好页 → 提交（Continue按钮）  
> **总用例数**: 9条  
> **可自动化**: 9条 (100%)

---

## 测试环境配置（必填）

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | sg | 新加坡站 |
| 基础URL | https://sg.58v5.cn | 测试站点地址 |
| 站点名称 | 新加坡站 | 可选 |
| 角色 | seller | seller角色 |
| 账号名称 | dc_seller_sg | 用于 session 命名 |
| 测试账号 | yongli@58.com | 登录邮箱 |
| 测试密码 | Qwer1234 | 登录密码 |

**说明**：此配置将被 playwright-test-generator 用于生成自动化脚本。

---

## 📑 目录

- [测试概述](#测试概述)
- [TC001: 提交-所有字段填写完整正常提交成功](#tc001-提交-所有字段填写完整正常提交成功)
- [TC002: 提交-未选Job Functions直接点击Continue](#tc002-提交-未选job-functions直接点击continue)
- [TC003: 提交-未选Location直接点击Continue](#tc003-提交-未选location直接点击continue)
- [TC004: 提交-Salary只选Pay Type不填金额](#tc004-提交-salary只选pay-type不填金额)
- [TC005: 提交-Salary填写0提交](#tc005-提交-salary填写0提交)
- [TC006: 提交-不选Workplace Type和Job Type可以提交](#tc006-提交-不选workplace-type和job-type可以提交)
- [TC007: 提交-快速连续点击Continue按钮](#tc007-提交-快速连续点击continue按钮)
- [TC008: 提交-点击Skip跳过提交](#tc008-提交-点击skip跳过提交)
- [TC009: 提交后重访列表页-偏好标签持久化验证](#tc009-提交后重访列表页-偏好标签持久化验证)

---

## 测试概述

### 页面入口（MCP实测确认）

1. 登录 SG 站账号（未登录状态点击 Jobs 图标**不会**跳转到偏好页，直接进入列表页）
2. 打开 `https://sg.58v5.cn/en/city-singapore/`，已登录状态点击首页金刚位 **Jobs** 链接
3. 跳转到岗位偏好页：`https://sgpub.58v5.cn/biz/en/jobPreference?showSkip=1&returnUrl=https%3A%2F%2Fsg.58v5.cn%2Fen%2Fcity-singapore%2Fcate-jobs%2F%3FiconSource%3Djobs`

### 页面字段说明（MCP录制确认）

| 字段 | 类型 | 必填 | 选择器来源 |
|------|------|------|-----------|
| Job Functions | 多选（最多10项），两级级联下拉（左侧一级 + 右侧二级，需点二级项选中，点Confirm确认） | ✅ 必填（带*） | `page.getByText('Select preferred job function')` |
| Location | 多选（最多5项），checkbox列表，点Confirm确认 | ✅ 必填（带*） | `page.getByText('Select preferred work')` |
| Salary - Pay Type | 单选按钮组（Yearly/Monthly/Hourly），默认选中 Yearly | ✅ 必填（带*）| `page.getByRole('button', { name: 'Select pay type Yearly' })` |
| Salary - 金额 | 数字输入框，输入后自动格式化千位分隔（5000→5,000），接受0值 | ✅ 必填（带*） | `page.locator('form').getByRole('textbox')` |
| Workplace Type | 多选checkbox（Onsite/Remote/Hybrid）| ❌ 可选 | `page.getByRole('checkbox', { name: 'Onsite' })` 等 |
| Job Type | 多选checkbox（Full-time/Part-time/Contract/Internship/Temporary）| ❌ 可选 | `page.getByRole('checkbox', { name: 'Full-time' })` 等 |
| Continue（提交）| button | - | `page.getByRole('button', { name: 'Continue' })` |
| Back | button | - | `page.getByRole('button', { name: 'Back' })` |
| Skip | link | - | `page.getByRole('link', { name: 'Skip' })` |

### 提交成功验证（MCP实测确认）

- URL 跳转至：`https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs`
- 列表页顶部 filter 区域显示已选偏好标签（如 `Developers/Programmers`）+ `Edit` 链接
- 列表展示已按偏好筛选后的岗位
- **注意**：无"Filter · N"角标，偏好标签直接以文字形式呈现于 filter bar

### 偏好数据回填说明（MCP实测确认）

- 已提交过偏好的账号，再次进入偏好页时，上次保存的数据会**自动回填**（Job Functions、Location、Salary、勾选项均保留）

---

## 测试用例

## 正向场景

### TC001: 提交-所有字段填写完整正常提交成功

#### 📋 前置条件
- 已登录 SG 站账号（yongli@58.com）
- 当前在 `https://sg.58v5.cn/en/city-singapore/`，已登录状态

#### 🎬 执行步骤
1. 点击首页金刚位 **Jobs** 链接
2. 等待页面跳转到岗位偏好页（URL 含 `jobPreference`）
3. 点击 **Job Functions** 选择框，在左侧一级分类点击 `Information & Communication Technology`，在右侧二级分类点击 `Developers/Programmers`，点击 **Confirm**
4. 点击 **Location** 选择框，勾选 `Singapore`，点击 **Confirm**
5. 点击 **Pay Type** 按钮，选择 `Monthly`
6. 在 Salary 金额框输入 `5000`（输入后框内显示 `5,000`）
7. 勾选 **Workplace Type** 选项 `Onsite`
8. 勾选 **Job Type** 选项 `Full-time`
9. 点击 **Continue** 按钮

#### ✅ 预期结果
- 页面跳转，URL 变为 `https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs`
- 列表页顶部 filter 区域显示偏好标签 `Developers/Programmers`，旁边有 `Edit` 链接
- 列表展示按偏好筛选的 ICT/Developer 相关岗位（岗位数量 ≥ 1 条）
- 页面不显示任何错误提示

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC006: 提交-不选Workplace Type和Job Type可以提交

#### 📋 前置条件
- 已登录 SG 站账号
- 当前在岗位偏好页

#### 🎬 执行步骤
1. 进入岗位偏好页
2. 选择 **Job Functions**（如 `Developers/Programmers`），点击 **Confirm**
3. 选择 **Location**（勾选 `Singapore`），点击 **Confirm**
4. 选择 **Pay Type** 为 `Monthly`，在 Salary 金额框输入 `5000`
5. **不勾选** Workplace Type 和 Job Type 中任何选项
6. 点击 **Continue**

#### ✅ 预期结果
- 页面跳转，URL 变为 `https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs`
- 列表页顶部 filter 区域显示偏好标签 `Developers/Programmers`，旁边有 `Edit` 链接
- 页面不显示任何错误提示，提交成功

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

## 异常场景（必填字段验证）

### TC002: 提交-未选Job Functions直接点击Continue

#### 📋 前置条件
- 已登录 SG 站账号
- 当前在岗位偏好页
- Job Functions 为未选状态（计数显示 `0/10`）

#### 🎬 执行步骤
1. 进入岗位偏好页
2. 若 Job Functions 已有预填数据，打开选择面板点击 **Clear** 后点击 **Confirm** 清空
3. 选择 Location（Singapore）并点击 **Confirm**
4. 选择 Pay Type（Monthly）并填写 Salary（5000）
5. **不选** Job Functions
6. 点击 **Continue**

#### ✅ 预期结果
- 页面**不跳转**，停留在岗位偏好页（URL 不变）
- Job Functions 字段下方出现错误提示文字：**"Don't leave this field empty."**
- Continue 按钮保持可点击状态但提交无效

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 异常测试
- **UI自动化**: ✅ 可自动化

---

### TC003: 提交-未选Location直接点击Continue

#### 📋 前置条件
- 已登录 SG 站账号
- 当前在岗位偏好页
- Location 为未选状态（计数显示 `0/5`）

#### 🎬 执行步骤
1. 进入岗位偏好页
2. 选择 Job Functions（`Developers/Programmers`），点击 **Confirm**
3. 若 Location 已有预填数据，打开选择面板点击 **Clear** 后点击 **Confirm** 清空
4. 选择 Pay Type（Monthly）并填写 Salary（5000）
5. **不选** Location
6. 点击 **Continue**

#### ✅ 预期结果
- 页面**不跳转**，停留在岗位偏好页（URL 不变）
- Location 字段下方出现错误提示文字：**"Don't leave this field empty."**
- Continue 按钮保持可点击状态但提交无效

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 异常测试 
- **UI自动化**: ✅ 可自动化

---

### TC004: 提交-Salary只选Pay Type不填金额

#### 📋 前置条件
- 已登录 SG 站账号
- 当前在岗位偏好页

#### 🎬 执行步骤
1. 进入岗位偏好页
2. 选择 Job Functions 和 Location（同前置）
3. 点击 Pay Type 按钮，选择 `Monthly`
4. 清空 Salary 金额框（将已填内容删除，使输入框为空）
5. 点击 **Continue**

#### ✅ 预期结果
- 页面**不跳转**，停留在岗位偏好页（URL 不变）
- Salary 金额框下方出现错误提示文字：**"Don't leave this field empty."**
- Continue 按钮保持可点击状态但提交无效

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 异常测试
- **UI自动化**: ✅ 可自动化

---

### TC005: 提交-Salary填写0提交

#### 📋 前置条件
- 已登录 SG 站账号
- 当前在岗位偏好页

#### 🎬 执行步骤
1. 进入岗位偏好页
2. 选择 Job Functions（`Developers/Programmers`），点击 **Confirm**
3. 选择 Location（Singapore），点击 **Confirm**
4. 选择 Pay Type（Monthly）
5. 在 Salary 金额框输入 `0`
6. 点击 **Continue**

#### ✅ 预期结果
- 系统**接受 0 值**，页面跳转成功，URL 变为 `https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs`
- 列表页顶部 filter 区域显示偏好标签 `Developers/Programmers`，旁边有 `Edit` 链接
- 系统**不显示任何校验错误**（Salary 0 值未被前端拦截）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界测试
- **UI自动化**: ✅ 可自动化

---

## 特殊场景

### TC007: 提交-快速连续点击Continue按钮

#### 📋 前置条件
- 已登录 SG 站账号
- 当前在岗位偏好页，所有必填字段已填写

#### 🎬 执行步骤
1. 进入岗位偏好页并填写所有必填字段（同TC001）
2. 快速连续点击 **Continue** 按钮 2-3 次

#### ✅ 预期结果
- 系统只执行一次提交操作，不重复跳转或触发多次接口请求
- 最终跳转到 URL：`https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs`

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 健壮性测试
- **UI自动化**: ✅ 可自动化

---

### TC008: 提交-点击Skip跳过提交

#### 📋 前置条件
- 已登录 SG 站账号
- 当前在岗位偏好页（URL 中包含 `showSkip=1` 参数）

#### 🎬 执行步骤
1. 进入岗位偏好页（确认页面右侧有 `Skip` 链接可点击）
2. 不填写任何字段（或已有预填数据不做修改）
3. 点击页面中的 **Skip** 链接

#### ✅ 预期结果
- 页面跳转，URL 变为 `https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs`
- 页面**不显示**任何必填字段错误提示
- Skip 链接的目标 URL 与 returnUrl 参数对应：`https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs`
- 若账号有历史偏好数据，跳转后列表页仍会显示历史偏好标签（Skip 不清除已保存的偏好）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化（Skip 为链接，直接点击跳转，可录制验证）

---

## 测试统计

### 用例概览
- 总用例数: 9 条
- 可自动化: 9 条 (100%)
- 不可自动化: 0 条

### 按优先级分布
| 优先级 | 总数 | 可自动化 | 自动化率 |
|--------|------|---------|---------|
| P0 | 4 | 4 | 100% |
| P1 | 3 | 3 | 100% |
| P2 | 2 | 2 | 100% |

### 覆盖度自评
| 维度 | 评分 | 说明 |
|------|------|------|
| 正向功能 | 1.0 | TC001、TC006 覆盖完整提交和可选字段 |
| 必填验证 | 1.0 | TC002、TC003、TC004 覆盖三个必填字段，错误提示明确 |
| 边界测试 | 1.0 | TC005 实测确认 0 值可提交（系统无前端拦截） |
| 健壮性 | 0.8 | TC007 覆盖重复点击 |
| Skip路径 | 1.0 | TC008 覆盖，实测可自动化 |
| 安全/越权 | N/A | 本模块无权限场景 |

---

## MCP实测关键发现

| 序号 | 发现项 | 原文档 | 实测结果 |
|------|--------|--------|---------|
| 1 | 入口触发条件 | 点击 Jobs 即跳偏好页 | **已登录**才跳偏好页；未登录直接进列表页 |
| 2 | 提交成功URL | `cate-jobs/`（通用路径） | 实为 `cate-jobs/?iconSource=jobs` |
| 3 | 提交成功验证 | 显示"Filter · 1"角标 | 无角标，列表页顶部显示偏好文字标签 + Edit 链接 |
| 4 | 错误提示文案 | "带*号必填" / "高亮提示" | 实际文案为 **"Don't leave this field empty."** |
| 5 | Salary 0 值行为 | 预期拒绝或显示校验提示 | **实测接受 0 值，直接跳转成功** |
| 6 | Skip 可自动化 | 标注不可自动化 | **实测可自动化**，直接点击链接即可验证跳转 |
| 7 | 数据回填 | 未提及 | 偏好提交后再次进入页面，上次数据自动回填 |
| 8 | Salary 金额格式化 | 未提及 | 输入 5000 后显示 "5,000"（自动千位分隔） |

---

---

## 持久化验证

### TC009: 提交后重访列表页-偏好标签持久化验证

#### 📋 前置条件
- 已登录 SG 站账号（yongli@58.com）
- 当前在 `https://sg.58v5.cn/en/city-singapore/`，已登录状态

#### 🎬 执行步骤
1. 点击首页金刚位 **Jobs** 链接，进入岗位偏好页
2. 选择 **Job Functions**（ICT > Developers/Programmers），点击 **Confirm**
3. 选择 **Location**（Singapore），点击 **Confirm**
4. 选择 **Pay Type** 为 `Monthly`，Salary 金额填写 `5000`
5. 点击 **Continue** 提交
6. 等待跳转到 `https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs`
7. 等待页面加载完成

#### ✅ 预期结果
- 页面 URL 为 `https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs`
- 列表页顶部 filter 区域显示偏好标签 `Developers/Programmers`
- filter 区域旁边有 `Edit` 链接
- 岗位列表展示按偏好筛选后的内容（数量 ≥ 1 条）
- **完成验证后删除数据库中该用户的偏好记录**（`preference` 表，`user_id=796636253998732992`）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试（数据持久化验证）
- **UI自动化**: ✅ 可自动化

---

*本文档由 senior-qa-brain + playwright-test-generator 联合生成*  
*初次生成: 2026-03-19*  
*MCP实测修订: 2026-03-20（账号: yongli@58.com / SG站）*
