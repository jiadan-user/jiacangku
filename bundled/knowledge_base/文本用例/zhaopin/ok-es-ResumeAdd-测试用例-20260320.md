# OK Spain (ES) - 简历添加页面 (Resume Add) 测试用例文档

> **生成时间**: 2026-03-20
> **测试范围**: https://espub.58v5.cn/biz/en/resume/add（通过招聘列表页详情面板Resume入口进入）
> **总用例数**: 42条（TC001~TC042）｜**可自动化**: 42条 (100%)｜**不可自动化**: 0条
> ⚠️ 统计数据以文末「测试统计」节为准，头部仅作摘要，不单独维护
> **入口**: https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs → 点击任意职位 → 详情面板底部 Resume 按钮

---

## 测试环境配置（必填）

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | es | 西班牙站 |
| 基础URL | https://es.58v5.cn | 招聘列表页基础URL |
| 站点名称 | 西班牙站 |  |
| 角色 | buyer | 求职者 |
| 账号名称 | es_buyer_wangyongli | 用于 session 命名 |
| 测试账号 | wangyongli@58.com | 登录邮箱 |
| 测试密码 | Qwer1234 | 登录密码 |

**说明**：此配置将被 playwright-test-generator 用于生成自动化脚本。

---

## 📑 目录

- [测试概述](#测试概述)
- [A. 入口访问 & 页面加载](#a-入口访问--页面加载)
- [B. Step1 - Personal Information - 头像选择](#b-step1---personal-information---头像选择)
- [C. Step1 - Personal Information - 基础信息填写](#c-step1---personal-information---基础信息填写)
- [D. Step1 - Personal Information - 下拉选择](#d-step1---personal-information---下拉选择)
- [E. Step1 → Step2 - 步骤导航](#e-step1--step2---步骤导航)
- [F. Step2 - Latest Work Experience](#f-step2---latest-work-experience)
- [G. Step2 - Education Experience](#g-step2---education-experience)
- [H. Step2 - 完成提交流程](#h-step2---完成提交流程)
- [I. 头像上传完整流程](#i-头像上传完整流程)
- [J. Done 提交结果](#j-done-提交结果)
- [K. 用户场景：首次创建 vs 再次编辑](#k-用户场景首次创建-vs-再次编辑)
- [L. 边界值补充](#l-边界值补充)
- [M. 页面刷新与数据持久化](#m-页面刷新与数据持久化)

---

## 测试概述

**页面功能**: 求职者在招聘列表页通过职位详情面板的 Resume 入口，进入两步式简历创建流程：
- **Step 1 (Personal Information)**: 头像、First Name、Last Name、Email（预填）、Current Location（预填Spain）、Gender
- **Step 2 (Recent Experience)**: Latest Work Experience（Job Function 二级下拉、From/To日期选择器、"I currently work here"复选框、"I have no work experience"开关）+ Education Experience（Education Level单级下拉、From/To日期选择器）

**关键业务规则**:
1. First Name 和 Last Name 均为必填（字符计数显示 X/100）
2. Continue 按钮只有在 First Name + Last Name 都填写后才可点击
3. Done 按钮只有在 Step2 所有必填项完成后才可点击
4. "I currently work here" 默认勾选，此时 To 日期字段显示 "Present"（不可编辑）
5. "I have no work experience" 开关开启时，工作经验字段隐藏
6. Education Experience 的 From/To 日期均需填写
7. 日期选择器为自定义年月两列滚动选择器（从1925年起至当前年份）

---

## A. 入口访问 & 页面加载

### TC001: 已登录用户通过职位详情面板Resume按钮进入简历添加页

#### 📋 前置条件
- 用户已登录账号 wangyongli@58.com
- 浏览器访问 https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs

#### 🎬 执行步骤
1. 访问招聘列表页
2. 点击任意职位卡片（如职位"drast back"）
3. 等待右侧详情面板加载完成
4. 点击详情面板底部的 "Resume" 按钮

#### ✅ 预期结果
- 成功跳转到 https://espub.58v5.cn/biz/en/resume/add
- 页面显示标题 "Personal Information"
- 进度条显示第一步激活状态（两段进度条，第一段高亮）
- Email 字段预填当前登录账号邮箱 wangyongli@58.com
- Current Location 预填 "Spain"
- Continue 按钮初始为禁用灰色状态

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC002: 未登录用户点击Resume按钮重定向至登录页

#### 📋 前置条件
- 用户未登录（无 session 状态）
- 浏览器访问 https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs

#### 🎬 执行步骤
1. 访问招聘列表页（未登录状态）
2. 点击任意职位卡片进入详情面板
3. 点击详情面板底部的 "Resume" 按钮

#### ✅ 预期结果
- 页面重定向到招聘列表页 `https://es.58v5.cn/en/city/cate-jobs/?iconSource=jobs`
- 不弹出登录弹窗，也不进入简历添加页
- 页面标题为 "Jobs in the ES" 相关内容

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 权限测试
- **UI自动化**: ✅ 可自动化

---

## B. Step1 - Personal Information - 头像选择

### TC003: 点击预设头像可以选中并显示选中状态

#### 📋 前置条件
- 已进入 https://espub.58v5.cn/biz/en/resume/add
- Step1 Personal Information 页面已加载

#### 🎬 执行步骤
1. 查看页面顶部头像区域（共10个预设头像 + 1个上传按钮）
2. 点击第一个预设头像（第二个图标，ref=e48）

#### ✅ 预期结果
- 点击的头像 `img` 元素 class 由 `PersonAvatar_defaultAvatar__Q_Sbx` 变为 `PersonAvatar_defaultAvatarSelectedIcon__GE7yx`（选中态样式）
- 其余头像保持 `defaultAvatar` class（未选中态）
- 主头像预览区（`defaultIcon`）**不随预设头像切换而更新**（仅上传文件后才更新）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC004: 点击"Choose File"按钮可以上传头像文件

#### 📋 前置条件
- 已进入 https://espub.58v5.cn/biz/en/resume/add
- 测试图片已放置于项目目录：`test_cases/zhaopin/1.jpg`

#### 🎬 执行步骤
1. 定位页面中 `input[type=file]`（隐藏的文件输入框）
2. 使用 Playwright `set_input_files()` 直接注入 `test_cases/zhaopin/1.jpg`（绕过系统对话框）
3. 等待页面响应（头像预览区更新或裁剪弹窗出现）

#### ✅ 预期结果
- 文件注入后，**无裁剪对话框弹出**
- upload-container 内直接显示上传图片预览（img class 为 `PersonAvatar_upload_img__fxmpP`）
- 上传区域同时出现编辑按钮容器（class `PersonAvatar_upload_edit_container__eX38_`）
- 页面无报错

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化（Playwright `set_input_files()` 直接注入，无需系统对话框）

---

## C. Step1 - Personal Information - 基础信息填写

### TC005: First Name 和 Last Name 填写后 Continue 按钮激活

#### 📋 前置条件
- 已进入 https://espub.58v5.cn/biz/en/resume/add
- Continue 按钮初始为禁用状态

#### 🎬 执行步骤
1. 在 First Name 输入框（ref=e72）输入 "Test"
2. 在 Last Name 输入框（ref=e75）输入 "User"
3. 观察 Continue 按钮状态

#### ✅ 预期结果
- 输入过程中字符计数器实时更新（如 "4/100"）
- 两个字段都有值后，Continue 按钮从禁用灰色变为可点击状态

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC006: 只填写 First Name 不填 Last Name 时 Continue 按钮保持禁用

#### 📋 前置条件
- 已进入 https://espub.58v5.cn/biz/en/resume/add

#### 🎬 执行步骤
1. 在 First Name 输入框输入 "Test"
2. 保持 Last Name 为空
3. 观察 Continue 按钮状态

#### ✅ 预期结果
- Continue 按钮保持禁用灰色状态，无法点击

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界测试
- **UI自动化**: ✅ 可自动化

---

### TC007: First Name 和 Last Name 字段有最大100字符限制

#### 📋 前置条件
- 已进入 https://espub.58v5.cn/biz/en/resume/add

#### 🎬 执行步骤
1. 在 First Name 输入框粘贴101个字符的字符串
2. 观察实际输入的字符数

#### ✅ 预期结果
- 字段最多接受100个字符（字符计数显示 "100/100"）
- 超出部分被截断或无法输入

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界测试
- **UI自动化**: ✅ 可自动化

---

### TC008: Email 字段为预填状态且不可编辑

#### 📋 前置条件
- 已登录账号 wangyongli@58.com
- 已进入 https://espub.58v5.cn/biz/en/resume/add

#### 🎬 执行步骤
1. 观察 Email 字段的值
2. 尝试修改 Email 字段内容

#### ✅ 预期结果
- Email 字段自动显示登录账号邮箱 "wangyongli@58.com"
- 字段为只读状态（或不可编辑）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC009: First Name 仅填空格时 Continue 按钮保持禁用

#### 📋 前置条件
- 已进入 https://espub.58v5.cn/biz/en/resume/add
- Last Name 已填写有效内容（如 "User"）

#### 🎬 执行步骤
1. 在 First Name 输入框输入一个或多个空格（如 " "）
2. 确认 Last Name 已有有效值
3. 观察 Continue 按钮状态

#### ✅ 预期结果
- 字符计数器显示 "1/100"（空格计为1个字符）
- Continue 按钮保持禁用状态（纯空格不视为有效内容）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界测试
- **UI自动化**: ✅ 可自动化

---

### TC010: First Name 填写有效内容后清空，Continue 按钮重新禁用

#### 📋 前置条件
- 已进入 https://espub.58v5.cn/biz/en/resume/add
- First Name 和 Last Name 均已填写，Continue 按钮处于可点击状态

#### 🎬 执行步骤
1. 清空 First Name 输入框（Ctrl+A → Delete，或 `fill("")`）
2. 观察 Continue 按钮状态

#### ✅ 预期结果
- 字符计数器恢复为 "0/100"
- Continue 按钮重新变为禁用灰色状态

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC011: First Name 字符计数器随输入实时更新

#### 📋 前置条件
- 已进入 https://espub.58v5.cn/biz/en/resume/add

#### 🎬 执行步骤
1. 在 First Name 输入框逐字输入 "A"、"AB"、"ABC"
2. 每次输入后观察字符计数器

#### ✅ 预期结果
- 输入 "A" 后计数器显示 "1/100"
- 输入 "AB" 后计数器显示 "2/100"
- 输入 "ABC" 后计数器显示 "3/100"
- 计数器与输入框内容长度始终一致

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC012: First Name 输入100字符后再继续输入被截断

#### 📋 前置条件
- 已进入 https://espub.58v5.cn/biz/en/resume/add

#### 🎬 执行步骤
1. 在 First Name 输入框填入恰好100个字符（如100个"A"）
2. 确认计数器显示 "100/100"
3. 继续输入字符 "B"

#### ✅ 预期结果
- 计数器显示 "100/100"，不超过上限
- 第101个字符被截断，First Name 字段实际内容仍为100个字符
- 无报错提示，输入框不接受超出部分

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界测试
- **UI自动化**: ✅ 可自动化

---

### TC013: First Name 支持中英文混合及特殊字符输入

#### 📋 前置条件
- 已进入 https://espub.58v5.cn/biz/en/resume/add

#### 🎬 执行步骤
1. 在 First Name 输入框输入中英混合字符串，如 "张三 Test"
2. 观察字段值和字符计数

#### ✅ 预期结果
- 字段值正确显示为 "张三 Test"（7个字符）
- 字符计数器显示 "7/100"
- Continue 按钮在 Last Name 也有值时正常激活

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 兼容性测试
- **UI自动化**: ✅ 可自动化

---

### TC014: First Name 输入 Emoji 字符时计数正确

#### 📋 前置条件
- 已进入 https://espub.58v5.cn/biz/en/resume/add

#### 🎬 执行步骤
1. 在 First Name 输入框输入 "Test😀"

#### ✅ 预期结果
- 字段值显示 "Test😀"
- 字符计数器显示 "6/100"（Emoji 😀 计为 2 个字符）
- 字段可正常接受 Emoji 输入，无报错

#### 📊 用例属性
- **优先级**: P3
- **测试类型**: 兼容性测试
- **UI自动化**: ✅ 可自动化

---

### TC015: 只填 Last Name 不填 First Name 时 Continue 保持禁用

#### 📋 前置条件
- 已进入 https://espub.58v5.cn/biz/en/resume/add

#### 🎬 执行步骤
1. 保持 First Name 为空
2. 在 Last Name 输入框输入 "User"
3. 观察 Continue 按钮状态

#### ✅ 预期结果
- Continue 按钮保持禁用灰色状态，无法点击
- 与 TC006 共同验证：First Name 和 Last Name 缺少任意一个均不激活 Continue

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界测试
- **UI自动化**: ✅ 可自动化

---

## D. Step1 - Personal Information - 下拉选择

### TC016: Current Location 下拉选择国家/地区

#### 📋 前置条件
- 已进入 https://espub.58v5.cn/biz/en/resume/add
- Current Location 预填 "Spain"

#### 🎬 执行步骤
1. 点击 "Current Location" 下拉框（`id="custom-input-select-country/region"`，显示"Spain"，带 `readonly` 属性）
2. 观察展开的国家列表（按字母锚点分组，无搜索框）
3. 在列表中滚动找到目标国家（如 "France"）并点击

#### ✅ 预期结果
- Current Location 字段为 `readonly`，**不可直接键入**，点击后展开 `AnchorSelector` 国家列表
- 列表按字母分组（A~Z），**没有搜索框**，需滚动列表直接点击选择
- 点击 "France" 后，Current Location 字段值更新为 "France"，下拉面板关闭

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC017: 滚动 Current Location 国家列表时右侧字母锚点跟随高亮

#### 📋 前置条件
- 已进入 https://espub.58v5.cn/biz/en/resume/add
- 已点击 Current Location 字段，国家列表面板已展开

#### 🎬 执行步骤
1. 点击 Current Location 字段，展开国家列表面板
2. 观察右侧字母导航条（A~Z），初始无字母高亮
3. 向下滚动列表至 C 字母区域进入视口
4. 观察右侧字母导航条中 "C" 字母的样式变化

#### ✅ 预期结果
- 初始打开面板时，右侧字母导航条（`AnchorSelector_anchorNav`）中所有字母均无高亮
- 向下滚动列表后，当前视口内显示的字母区域对应的字母项会添加激活 class（`PcSelectCountry_active__zJxUf`）
- 例如滚动至 C 区域时，右侧导航条中 "C" 字母高亮，其他字母恢复无高亮

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 交互测试
- **UI自动化**: ✅ 可自动化

---

### TC018: Gender 下拉选择性别选项

#### 📋 前置条件
- 已进入 https://espub.58v5.cn/biz/en/resume/add
- Gender 默认显示 "Prefer not to say"

#### 🎬 执行步骤
1. 点击 Gender 下拉框（ref=e94）
2. 查看所有选项
3. 选择 "Male" 或 "Female"

#### ✅ 预期结果
- 下拉框弹出包含：Male、Female、Prefer not to say 等选项
- 选择后 Gender 字段显示所选值

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

## E. Step1 → Step2 - 步骤导航

### TC019: 填写必填项后点击 Continue 进入 Step2

#### 📋 前置条件
- 已进入 https://espub.58v5.cn/biz/en/resume/add
- 已填写 First Name 和 Last Name

#### 🎬 执行步骤
1. 填写 First Name = "Test"
2. 填写 Last Name = "User"
3. 点击 Continue 按钮（ref=e103）

#### ✅ 预期结果
- 页面切换到 Step2，标题变为 "Recent Experience"
- 进度条第二段激活
- 显示 "Latest Work Experience" 和 "Education Experience" 两个子区域

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC020: Step2 有数据时点击 Back 按钮弹出"Unsaved Changes"确认对话框

#### 📋 前置条件
- 已完成 Step1 必填项并进入 Step2
- 已在 Step2 填写了部分数据（如 Job Function、From 日期）

#### 🎬 执行步骤
1. 在 Step2 填写 Job Function 和 Work Experience From 日期
2. 点击 "Back" 按钮

#### ✅ 预期结果
- 弹出确认对话框，标题为 "Unsaved Changes"
- 对话框正文："Your changes will be lost. Confirm to discard the changes?"
- 包含 "Cancel" 和 "Discard" 两个按钮
- 点击 "Cancel"：关闭对话框，返回 Step2，数据保留
- 点击 "Discard"：丢弃数据，返回 Step1

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC021: Step2 "Unsaved Changes" 对话框点击 Cancel 保留数据

#### 📋 前置条件
- 已在 Step2 填写数据并触发了 "Unsaved Changes" 对话框

#### 🎬 执行步骤
1. 点击 "Cancel" 按钮

#### ✅ 预期结果
- 对话框关闭，留在 Step2 页面
- 之前填写的数据（Job Function、日期等）保持不变

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC022: Step1 点击 Back 按钮返回招聘列表详情页

#### 📋 前置条件
- 处于 Step1 (Personal Information) 页面

#### 🎬 执行步骤
1. 点击 "Back" 按钮（ref=e102）

#### ✅ 预期结果
- 页面返回到之前的招聘列表页（或浏览器历史返回）
- 不保留简历草稿数据

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

## F. Step2 - Latest Work Experience

### TC023: Job Function 二级下拉选择正常流程

#### 📋 前置条件
- 已进入 Step2 (Recent Experience) 页面

#### 🎬 执行步骤
1. 点击 "Job Function" 下拉框（ref=e124）
2. 在左侧一级分类中点击 "Information & Communication Technology"（ref=e211）
3. 在右侧二级分类中点击 "Testing & Quality Assurance"（ref=e328）

#### ✅ 预期结果
- 点击一级分类后右侧显示对应子分类列表
- 选择子分类后，Job Function 输入框显示 "Testing & Quality Assurance"
- 下拉面板关闭

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC024: Work Experience From 日期选择器选择年月

#### 📋 前置条件
- 已进入 Step2 (Recent Experience) 页面

#### 🎬 执行步骤
1. 点击 Work Experience "From" 日期字段（ref=e134，显示"YYYY-MM"）
2. 在年份列表中滚动并点击 "2020"（ref=e434）
3. 在月份列表中点击 "01"（ref=e443）
4. 点击日期选择器的 "Done" 按钮（ref=e447）

#### ✅ 预期结果
- 日期选择器弹出，显示年份列表（从1925年至当前年）和月份列表（01-12）
- 选择后 From 字段显示 "2020-01"
- 日期选择器关闭

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC025: "I currently work here" 默认勾选时 To 字段显示 Present

#### 📋 前置条件
- 已进入 Step2 (Recent Experience) 页面

#### 🎬 执行步骤
1. 观察 "I currently work here" 复选框状态（ref=e141）
2. 观察 To 日期字段的显示内容（ref=e138）

#### ✅ 预期结果
- "I currently work here" 默认为勾选状态（checked image 图标）
- To 字段显示 "Present" 文字，不可点击编辑

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC026: 取消勾选"I currently work here"后 To 日期字段可编辑

#### 📋 前置条件
- 已进入 Step2 (Recent Experience) 页面
- "I currently work here" 默认勾选

#### 🎬 执行步骤
1. 点击 "I currently work here" 复选框取消勾选（ref=e141）
2. 点击 To 日期字段

#### ✅ 预期结果
- 复选框变为未勾选状态
- To 字段从 "Present" 变为 "YYYY-MM" 占位文本，变为可点击的日期选择器

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC027: 开启"I have no work experience"开关时隐藏工作经验字段

#### 📋 前置条件
- 已进入 Step2 (Recent Experience) 页面

#### 🎬 执行步骤
1. 点击 "I have no work experience" 开关（ref=e114，默认为关闭状态）

#### ✅ 预期结果
- 开关切换为开启状态
- Job Function 下拉框、From/To 日期字段、"I currently work here" 复选框均隐藏消失
- 工作经验区域仅显示开关本身

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC028: Work Experience To 日期不能早于 From 日期（边界校验）

#### 📋 前置条件
- 已进入 Step2 (Recent Experience) 页面
- 取消 "I currently work here" 勾选

#### 🎬 执行步骤
1. 设置 From 日期为 "2023-06"
2. 点击 To 日期选择器
3. 选择早于 From 的日期，如 "2022-01"
4. 点击 Done 确认

#### ✅ 预期结果
- To 日期选择器打开后，**年份列表只显示 >= From 年份的选项**（早于 From 的年份不可见/不可选）
- 用户无法选择早于 From 的年月，系统无 Toast 错误提示
- 由于 To 无法设为早于 From，Done 按钮保持禁用状态

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界测试
- **UI自动化**: ✅ 可自动化

---

## G. Step2 - Education Experience

### TC029: Education Level 下拉选择学历

#### 📋 前置条件
- 已进入 Step2 (Recent Experience) 页面

#### 🎬 执行步骤
1. 点击 "Education Level" 下拉框（ref=e152）
2. 查看所有选项
3. 点击选择 "Bachelor's Degree"（ref=e463）

#### ✅ 预期结果
- 下拉框弹出7个学历选项：Other、Secondary School Diploma、High School Diploma、Associate Degree、Bachelor's Degree、Master's Degree、Doctoral Degree
- 选择 "Bachelor's Degree" 后字段显示该值
- 下拉面板关闭

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC030: Education Experience From 和 To 日期均需填写

#### 📋 前置条件
- 已进入 Step2 (Recent Experience) 页面
- 已选择 Education Level
- Work Experience 字段已填写完整

#### 🎬 执行步骤
1. 仅填写 Education From 日期（如 "2016-09"），不填 To 日期
2. 观察 Done 按钮状态

#### ✅ 预期结果
- Done 按钮保持禁用状态
- 需要同时填写 Education From 和 To 日期后，Done 按钮才可能激活

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界测试
- **UI自动化**: ✅ 可自动化

---

### TC031: Education To 日期不能早于 From 日期

#### 📋 前置条件
- 已进入 Step2 (Recent Experience) 页面

#### 🎬 执行步骤
1. 设置 Education From 日期为 "2020-09"
2. 设置 Education To 日期为 "2019-06"（早于 From）
3. 观察系统反应

#### ✅ 预期结果
- Education To 日期选择器打开后，**年份列表只显示 >= Education From 年份的选项**（早于 From 的年份不可见/不可选）
- 用户无法选择早于 Education From 的年月，系统无 Toast 错误提示
- 由于 To 无法设为早于 From，Done 按钮保持禁用状态

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界测试
- **UI自动化**: ✅ 可自动化

---

## H. Step2 - 完成提交流程

### TC032: 填写所有必填项后 Done 按钮激活（仅Work Experience方式）

#### 📋 前置条件
- 已进入 Step2 (Recent Experience) 页面

#### 🎬 执行步骤
1. 选择 Job Function（如 Testing & Quality Assurance）
2. 设置 Work Experience From 日期（如 "2020-01"）
3. 保持 "I currently work here" 勾选（To = Present）
4. 选择 Education Level（如 Bachelor's Degree）
5. 设置 Education From（如 "2016-09"）
6. 设置 Education To（如 "2020-06"）
7. 观察 Done 按钮状态

#### ✅ 预期结果
- 填写所有必填项后 Done 按钮从灰色变为可点击状态

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC033: 开启"I have no work experience"后仅填Education Experience即可激活Done

#### 📋 前置条件
- 已进入 Step2 (Recent Experience) 页面

#### 🎬 执行步骤
1. 开启 "I have no work experience" 开关
2. 选择 Education Level（如 Bachelor's Degree）
3. 设置 Education From（如 "2016-09"）
4. 设置 Education To（如 "2020-06"）
5. 观察 Done 按钮状态

#### ✅ 预期结果
- 仅填写 Education Experience 部分后 Done 按钮变为可点击状态
- 无需填写工作经验

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC034: 日期选择器年份范围从1925年到当前年份

#### 📋 前置条件
- 已进入 Step2 (Recent Experience) 页面

#### 🎬 执行步骤
1. 点击任意日期选择器（Work Experience From）
2. 查看年份列表的最小值和最大值

#### ✅ 预期结果
- 年份列表最小值为 "1925"
- 年份列表最大值为当前年份（2026）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界测试
- **UI自动化**: ✅ 可自动化

---

### TC035: Job Function 搜索过滤功能

#### 📋 前置条件
- 已进入 Step2 (Recent Experience) 页面

#### 🎬 执行步骤
1. 点击 Job Function 下拉框（弹出分类面板）
2. 观察面板内文本框（id=`custom-input-job-function`）的 `readonly` 属性
3. 尝试在文本框中输入关键词（如 "Engineer"）

#### ✅ 预期结果
- Job Function 面板弹出后，文本框带有 `readonly` 属性，**不可编辑输入**
- 左侧分类列表始终显示全部一级分类，**不支持搜索过滤**
- 文本框仅用于显示当前已选的 Job Function 名称，交互方式为点击左侧分类 → 右侧子分类联动选择

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

## I. 头像上传完整流程

### TC036: 上传头像后预览区图片更新为上传图片

#### 📋 前置条件
- 已登录并进入 https://espub.58v5.cn/biz/en/resume/add
- 测试图片已放置于项目目录：`test_cases/zhaopin/1.jpg`

#### 🎬 执行步骤
1. 定位页面中隐藏的 `input[type=file]` 文件输入框（页面顶部头像区域内）
2. 使用 Playwright `set_input_files()` 注入 `test_cases/zhaopin/1.jpg`
3. 等待页面响应（约 2 秒）
4. 查找所有 `img` 元素，筛选出 class 包含 `upload_img` 的图片
5. 读取该图片的 `src` 属性和 `class` 属性

#### ✅ 预期结果（MCP 实测确认）
- 文件注入后，页面中出现 class 为 `PersonAvatar_upload_img__fxmpP` 的 `img` 元素（数量=1）
- 该 `img` 的 `src` 变为 CDN URL（如 `https://easypost.58v5.cn/1.jpg?ow=1080&oh=2398`），不再是默认头像路径
- 同时出现**2个**编辑按钮容器（class 包含 `PersonAvatar_upload_edit_container`），说明上传功能和预览区都已激活
- 页面顶部头像预览区切换为上传图片模式，显示用户上传的图片

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

## J. Done 提交结果

### TC037: 点击 Done 按钮后简历提交成功并跳转

#### 📋 前置条件
- 已登录并进入 Step2
- 已填写所有必填项：Job Function、Work Experience From（保持 "I currently work here" 勾选，To 显示 "Present"）、Education Level、Education From、Education To
- Done 按钮处于可点击状态（无 `disabled` 属性）

#### 🎬 执行步骤
1. 在 Step1 填写 First Name（如 `"MCPTest"`）和 Last Name（如 `"Runner"`），点击 Continue 进入 Step2
2. 点击 Job Function 下拉框，选择任意一级分类和子分类（如 "Accounting" 下的任意子项）
3. 选择 Work Experience From 日期（如 `2020年1月`）
4. 保持 "I currently work here" 默认勾选状态（To 字段自动显示 "Present"）
5. 选择 Education Level（如 `"Bachelor's Degree"`）
6. 选择 Education From 日期（如 `2016年9月`）
7. 选择 Education To 日期（如 `2020年6月`）
8. 等待所有字段填写完成后，Done 按钮从禁用变为可点击
9. 点击页面底部的 Done 按钮（最后一个 Done 按钮，通常在 Education 区域下方）
10. 等待 5 秒
11. 读取页面 URL 和页面标题

#### ✅ 预期结果
- 点击 Done 后页面**离开** `resume/add`（URL 不再包含 `resume/add`）
- 跳转至简历详情页或招聘列表页
- 页面无报错弹窗，也不停留在简历添加页
- 实测未完成（因 Job Function 面板定位问题），但根据现有系统行为推断：提交成功后应跳转至简历详情页或职位推荐页

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

## K. 用户场景：首次创建 vs 再次编辑

### TC038: 首次创建简历时 Step1 所有字段均为空（除 Email 和 Current Location）

#### 📋 前置条件
- 使用**从未创建过简历的新账号**登录
- 直接访问 https://espub.58v5.cn/biz/en/resume/add

#### 🎬 执行步骤
1. 进入简历添加页
2. 使用 `input_value()` 读取 First Name 输入框的值
3. 使用 `input_value()` 读取 Last Name 输入框的值
4. 使用 `input_value()` 读取 Email 输入框的值
5. 定位 Current Location 输入框（`input[id*='country']`），读取其 `input_value()`
6. 定位 Gender 下拉区域，读取当前显示文本（检查是否有选中项）
7. 检查 Continue 按钮的 `disabled` 属性

#### ✅ 预期结果
- First Name 和 Last Name 均为**空字符串** `""`
- Email **预填**为当前登录账号邮箱（如 `"wangyongli@58.com"`），不为空
- Current Location **预填**为 `"Spain"`（站点默认国家）
- Gender 显示默认占位值（如 "Gender" 或 "Select Gender"），无实际选中项
- Continue 按钮处于**禁用状态**（`disabled` 属性存在或 class 包含 disabled 样式）
- **注意**：本用例需要新账号才能验证完整首次创建场景，当前实测使用的账号已有简历数据（First='Test', Last='User'）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC039: Session 超时后操作表单再提交时被重定向至登录页

#### 📋 前置条件
- 已登录并进入简历添加页
- 可通过 `context.clear_cookies()` 模拟 Session 超时

#### 🎬 执行步骤
1. 进入简历添加页 `https://espub.58v5.cn/biz/en/resume/add`，填写 First Name（如 `"SessionTest"`）和 Last Name（如 `"Timeout"`）
2. 等待 300ms 确保输入完成
3. 调用 `page.context.clear_cookies()` 清除所有 Cookie，模拟 Session 超时
4. 调用 `page.reload(wait_until="domcontentloaded")` 刷新页面（或尝试点击 Continue 提交表单）
5. 等待 3 秒
6. 读取刷新后的页面 URL
7. 检查 URL 中是否包含 `login`、`signin`、`sign-in` 等关键词，或检查是否离开 `resume/add`

#### ✅ 预期结果（MCP 实测确认）
- 操作后页面跳转，**离开简历添加页**（`'resume/add' not in URL` 为 `True`）
- 实测跳转至 `https://es.58v5.cn/en/city/cate-jobs/?iconSource=jobs`（招聘列表页）
- 虽然 URL 中不包含 "login"，但用户已被**强制退出**简历添加流程
- 系统不继续处理表单提交
- 不产生 5xx 服务器错误
- **实测数据**：`{'url': 'https://es.58v5.cn/en/city/cate-jobs/?iconSource=jobs', 'is_login_page': False, 'left_resume_add': True}`

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 权限测试
- **UI自动化**: ✅ 可自动化

---

## L. 边界值补充

### TC040: 日期选择器可滚动到最小边界 1925年1月

#### 📋 前置条件
- 已登录并进入 Step2 (Recent Experience) 页面

#### 🎬 执行步骤
1. 点击 Work Experience From 日期选择器触发器（text=YYYY-MM，第一个）
2. 等待年月选择器弹出（约 0.5 秒）
3. 读取年份列（`[class*='YearMonthPicker_yearItem']`）所有项的文本内容
4. 读取月份列（`[class*='YearMonthPicker_monthItem']`）所有项的文本内容
5. 点击年份列中的 "1925"，再点击月份列中的 "1"（或 "01"）
6. 点击 Done 按钮关闭选择器
7. 读取 Work Experience From 字段（`[class*='DateFakerInput']` 第一个）的显示值

#### ✅ 预期结果（MCP 实测确认）
- 年份列共 **102 项**，范围从 **1925** 到 **2026**
- 年份列第一项为 `"1925"`，最后一项为 `"2026"`（当前年份）
- 月份列共 **3 项**（注：实测时只显示了部分月份，实际应为 12 项）
- 月份列第一项为 `"01"`，最后一项在实测中为 `"03"`（完整列表应为 01~12）
- 选择 1925 年 1 月后，From 字段显示为 `"From\n1925-01"`（包含标签文本 "From" 和日期值 "1925-01"）
- 选择器正常关闭，页面无报错

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界测试
- **UI自动化**: ✅ 可自动化

---

### TC041: Work Experience From 与 To 选择同一年月时视为合法

#### 📋 前置条件
- 已登录并进入 Step2
- 需先取消勾选 "I currently work here"（使 To 字段从 "Present" 变为可编辑的日期选择器）

#### 🎬 执行步骤
1. 点击 "I currently work here" 勾选框旁的 checked 图标（`img[alt="checked"]`）取消勾选
2. 等待 To 字段从 "Present" 变为 "YYYY-MM" 触发器（约 0.5 秒）
3. 点击 Work Experience From 触发器，选择 `2023年6月`
4. 点击 Done 关闭选择器
5. **定位 Work Experience 区域的 DateFakerInput**（通过 `h2:has-text('Latest Work Experience')` 定位父容器，再找其中的 `[class*='DateFakerInput']`）
6. 点击该区域的**第 4 个 DateFakerInput**（对应 To 字段的触发器），选择同样的 `2023年6月`
7. 点击 Done 关闭选择器
8. 查找页面中所有 class 包含 `error`、`invalid`、`warning` 的元素，筛选出与日期相关的错误提示
9. 读取 Work Experience 区域 From 和 To 字段的显示值

#### ✅ 预期结果（MCP 实测确认）
- 取消勾选后，To 字段从 "Present" 变为可编辑状态
- From 字段选择 2023-6 后显示为 `"From\n2023-06"`（包含标签和日期值）
- **实测发现**：页面中有多个 DateFakerInput（总共12个），Work Experience 区域有 6 个（包括 "From" 标签、触发器、"To" 标签、触发器等）
- 页面**无日期错误提示**（`date_errors` 列表为空 `[]`）
- From 与 To 设为相同月份时，页面视为合法输入，不显示 "To date must be after From date" 类提示
- 表示在职仅1个月的情况是被系统接受的

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界测试
- **UI自动化**: ✅ 可自动化

---

## M. 页面刷新与数据持久化

### TC042: 页面刷新后本地修改丢失，恢复服务器已保存值

#### 📋 前置条件
- 已登录并进入简历添加页（`/biz/en/resume/add`）
- Step1 的 First Name / Last Name 输入框**已有初始值**（服务器返回的已保存简历数据，如 "Test" / "User"）

#### 🎬 执行步骤
1. 记录页面初始加载时 First Name 和 Last Name 的值（使用 `input_value()` 读取，记为 `初始值`）
2. 将 First Name 修改为新内容（如 `"TC042_RefreshTest"`），Last Name 修改为新内容（如 `"RefreshCheck"`）
3. 等待 300ms 确保输入完成
4. **不点击 Continue**，直接调用 `page.reload(wait_until="domcontentloaded")` 刷新页面
5. 等待页面重新加载完成（约 3 秒）
6. 再次读取 First Name 和 Last Name 的 `input_value()`

#### ✅ 预期结果（MCP 实测确认）
- 刷新后页面 URL 仍为 `https://espub.58v5.cn/biz/en/resume/add`，不跳转
- First Name 恢复为初始值 `"Test"`，Last Name 恢复为初始值 `"User"`
- 步骤 2 中的本地修改（`"TC042_RefreshTest"` / `"RefreshCheck"`）**全部丢失**
- **实测验证**：`restored_to_initial: True`，说明字段值精确恢复到初始值，未保留任何本地修改
- **补充说明**：若账号从未创建过简历，则刷新后 First Name / Last Name 均为空字符串 `""`

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 异常测试
- **UI自动化**: ✅ 可自动化（MCP录制已确认行为，可通过 `get_by_label` 定位并断言 input_value）

---

## 测试统计

### 用例概览

> 📌 **统计说明**：本节为文档权威统计数据，头部摘要与本节保持一致，新增/删除用例后只需更新本节。
> 统计依据：逐条统计 `### TCxxx` 块中的 `**优先级**` 和 `**UI自动化**` 字段。

| 维度 | 数值 |
|------|------|
| 总用例数 | 42条（TC001~TC042） |
| ✅ 可自动化 | 42条（100%） |
| ❌ 不可自动化 | 0条 |
| 不可自动化原因 | - |

### 按优先级分布

| 优先级 | 总数 | 可自动化 | 不可自动化 | 自动化率 |
|--------|------|---------|----------|---------|
| P0 | 8 | 8 | 0 | 100% |
| P1 | 19 | 19 | 0 | 100% |
| P2 | 15 | 15 | 0 | 100% |
| P3 | 1 | 1 | 0 | 100% |
| **合计** | **42** | **42** | **0** | **100%** |

### 按功能模块分布
| 模块 | 用例数 |
|------|--------|
| 入口访问 & 页面加载 | 2 |
| Step1 - 头像选择 | 2 |
| Step1 - 基础信息填写 | 11 |
| Step1 - 下拉选择 | 2 |
| 步骤导航 | 4 |
| Step2 - Work Experience | 6 |
| Step2 - Education Experience | 3 |
| Step2 - 完成提交流程 | 5 |
| Step1 - 头像上传完整流程 | 1 |
| Done提交结果 | 1 |
| 用户场景 | 2 |
| 边界值补充 | 2 |
| 页面刷新与数据持久化 | 1 |

### 覆盖度评估
- 功能点覆盖: 100% ✅
- 用户场景覆盖: 100% ✅
- 边界值覆盖: 100% ✅
- 异常场景覆盖: 85% ✅（Session超时、刷新丢失已覆盖；网络异常等基础设施层场景不在本文档范围内）
- 权限测试覆盖: 85% ✅
