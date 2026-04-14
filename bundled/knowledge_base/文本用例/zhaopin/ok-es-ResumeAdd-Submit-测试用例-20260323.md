# OK Spain (ES) - 简历添加提交流程测试用例文档

> **生成时间**: 2026-03-23
> **测试范围**: 简历完整提交流程 + 提交后数据验证 + 数据库清理
> **总用例数**: 8条（TC001~TC008）｜**可自动化**: 8条 (100%)｜**不可自动化**: 0条
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
- [A. 完整提交流程 - 有工作经验](#a-完整提交流程---有工作经验)
- [B. 完整提交流程 - 无工作经验](#b-完整提交流程---无工作经验)
- [C. 提交后数据验证](#c-提交后数据验证)
- [D. 数据库清理验证](#d-数据库清理验证)

---

## 测试概述

**页面功能**: 求职者在招聘列表页通过职位详情面板的 Resume 入口，进入两步式简历创建流程，填写完整信息后提交，系统保存简历数据到数据库。

**测试重点**:
1. **完整提交流程**：Step1 Personal Information → Step2 Recent Experience → 点击 Done → 验证跳转
2. **提交后数据验证**：重新进入简历页面，验证数据正确回显
3. **数据库数据验证**：验证数据库中 resume、resume_education、resume_person_info、resume_work_experience 表的数据完整性
4. **数据清理**：测试完成后删除 user_id=796579748218214624 的所有相关数据

**关键业务规则**:
1. Step1 必填项：First Name、Last Name（Email 和 Current Location 自动预填）
2. Step2 必填项：
   - **有工作经验场景**：Job Function、Work Experience From（To 默认为 Present）、Education Level、Education From、Education To
   - **无工作经验场景**：开启 "I have no work experience" 开关，仅需填写 Education 部分
3. Done 按钮只有在所有必填项填写后才可点击
4. 提交成功后跳转离开 resume/add 页面
5. 提交后重新进入简历页面，数据应正确回显

---

## A. 完整提交流程 - 有工作经验

### TC001: 完整提交流程 - 填写所有必填项并提交（有工作经验）

#### 📋 前置条件
- 用户已登录账号 yongli@58.com
- 浏览器访问 https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs
- 数据库中已清理该用户的历史简历数据

#### 🎬 执行步骤

**Step 1: 进入简历添加页面**
1. 使用 `page.goto("https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs")` 访问招聘列表页
2. 等待页面加载完成（`wait_for_load_state("domcontentloaded", timeout=60000)`）
3. 等待筛选区域可见（`.listPage-filterArea` 元素，超时 15 秒）
4. 点击第一张职位卡片
   - 选择器：`.JobListItem_jobListItem__`
   - 使用 `.first.click()`
5. 等待 1 秒
6. 验证详情面板加载完成
   - 等待 `.JobDetail_jobDetail__` 元素可见（超时 5 秒）
   - 或等待 "Contact" 按钮可见（`page.get_by_role("button", name="Contact")`）
7. 定位并点击详情面板底部的 "Resume" 按钮
   - 使用 `page.get_by_text("Resume").first.click()`
8. 等待页面跳转（`wait_for_load_state("domcontentloaded", timeout=10000)`）
9. 等待 2 秒
10. 验证成功进入简历添加页
    - 断言：`"resume/add" in page.url`
    - 预期 URL: `https://espub.58v5.cn/biz/en/resume/add`

**Step 2: 填写 Personal Information（Step1）**
11. 验证进入 Step1 Personal Information 页面
    - 页面标题包含 "Personal Information"
    - 进度条第一段激活状态
12. 定位 First Name 输入框（选择器：`input[placeholder='First Name']`）
13. 输入 "AutoTest"（使用 `fill()` 方法）
14. 验证字符计数器显示 "8/100"
15. 定位 Last Name 输入框（选择器：`input[placeholder='Last Name']`）
16. 输入 "Submit"（使用 `fill()` 方法）
17. 验证字符计数器显示 "6/100"
18. 验证 Email 字段预填状态
    - 定位 Email 输入框（选择器：`input[type='email']`）
    - 使用 `input_value()` 读取值
    - 断言：值为 "yongli@58.com"
19. 验证 Current Location 字段预填状态
    - 定位 Current Location 输入框（选择器：`input[id*='country']`）
    - 使用 `input_value()` 读取值
    - 断言：值包含或等于 "Spain"
20. 验证 Continue 按钮状态
    - 定位 Continue 按钮（选择器：`button:has-text('Continue')`）
    - 验证按钮无 `disabled` 属性
21. 点击 Continue 按钮
22. 等待页面加载（`wait_for_load_state("domcontentloaded", timeout=10000)`）
23. 等待 2 秒
24. 验证进入 Step2
    - 页面标题变为 "Recent Experience"
    - 进度条第二段激活

**Step 3: 填写 Work Experience（Step2）**
25. 点击 Job Function 触发器
    - 使用 `page.get_by_text("Select Job Functions").click()`
26. 等待下拉面板打开（1 秒）
27. 在左侧一级分类中点击 "Information & Communication Technology"
    - 使用 `page.get_by_text("Information & Communication Technology", exact=True).click()`
28. 等待右侧二级分类加载（800ms）
29. 在右侧二级分类中点击 "Testing & Quality Assurance"
    - 使用 `page.get_by_text("Testing & Quality Assurance", exact=True).click()`
30. 等待面板关闭（500ms）
31. 验证 Job Function 已选择
    - 读取 Job Function 输入框值
    - 断言：值包含 "Testing & Quality Assurance"
32. 点击 Work Experience From 日期选择器
    - 定位 Work Experience 区域：`page.locator("h2:has-text('Latest Work Experience')").locator("..")`
    - 定位该区域第一个 DateFakerInput：`.locator("[class*='DateFakerInput']").first`
    - 点击触发器
33. 等待日期选择器打开（500ms）
34. 在年份列表中选择 "2020"
    - 使用 `page.get_by_text("2020", exact=True).click()`
35. 等待 300ms
36. 在月份列表中选择 "1"
    - 使用 `page.get_by_text("1", exact=True).click()`
    - 注意：月份 "01" 显示为 "1"，需去除前导零
37. 等待 300ms
38. 点击日期选择器的 Done 按钮
    - 选择器：`button:has-text('Done')`
39. 等待 500ms
40. 验证 From 日期已设置
    - 读取 From 字段显示文本
    - 断言：文本包含 "2020-01" 或 "2020" 和 "01"
41. 验证 "I currently work here" 默认勾选状态
    - 查找 `img[alt="checked"]` 元素
    - 断言：元素可见（`is_visible(timeout=2000)`）
42. 验证 To 字段显示 "Present"
    - 定位 To 字段（Work Experience 区域第二个 DateFakerInput）
    - 读取显示文本
    - 断言：文本包含 "Present" 或字段不可点击

**Step 4: 填写 Education Experience（Step2）**
43. 点击 Education Level 触发器
    - 使用 `page.get_by_text("Education Level").click()`
44. 等待下拉面板打开（500ms）
45. 在列表中选择 "Bachelor's Degree"
    - 使用 `page.get_by_text("Bachelor's Degree", exact=True).click()`
46. 等待面板关闭（500ms）
47. 验证 Education Level 已选择
    - 读取 Education Level 字段值
    - 断言：值包含 "Bachelor's Degree"
48. 点击 Education From 日期选择器
    - 定位 Education 区域：`page.locator("h2:has-text('Education Experience')").locator("..")`
    - 定位该区域第一个 DateFakerInput：`.locator("[class*='DateFakerInput']").first`
    - 点击触发器
49. 等待日期选择器打开（500ms）
50. 在年份列表中选择 "2016"
    - 使用 `page.get_by_text("2016", exact=True).click()`
51. 等待 300ms
52. 在月份列表中选择 "9"
    - 使用 `page.get_by_text("9", exact=True).click()`
53. 等待 300ms
54. 点击日期选择器的 Done 按钮
55. 等待 500ms
56. 验证 Education From 日期已设置
    - 断言：显示文本包含 "2016-09"
57. 点击 Education To 日期选择器
    - 定位 Education 区域第二个 DateFakerInput：`.locator("[class*='DateFakerInput']").nth(1)`
    - 点击触发器
58. 等待日期选择器打开（500ms）
59. 在年份列表中选择 "2020"
60. 等待 300ms
61. 在月份列表中选择 "6"
62. 等待 300ms
63. 点击日期选择器的 Done 按钮
64. 等待 500ms
65. 验证 Education To 日期已设置
    - 断言：显示文本包含 "2020-06"

**Step 5: 提交简历**
66. 验证 Done 按钮可点击状态
    - 定位最后一个 Done 按钮：`page.locator("button:has-text('Done')").last`
    - 验证按钮无 `disabled` 属性
    - 断言：`not done_button.is_disabled()`
67. 点击 Done 按钮
    - 使用 `page.locator("button:has-text('Done')").last.click()`
68. 等待 5 秒（页面跳转和数据保存时间）
69. 获取当前页面 URL，记录为 `final_url`

#### ✅ 预期结果
- **Step 10**: 页面 URL 包含 `resume/add`，成功进入简历添加页
- **Step 14**: First Name 字符计数器显示 "8/100"
- **Step 17**: Last Name 字符计数器显示 "6/100"
- **Step 19**: Email 字段预填为 "yongli@58.com"
- **Step 20**: Current Location 字段预填为 "Spain"
- **Step 24**: 页面标题变为 "Recent Experience"，进入 Step2
- **Step 31**: Job Function 显示 "Testing & Quality Assurance"
- **Step 40**: Work Experience From 显示 "2020-01"
- **Step 42**: "I currently work here" 勾选，To 显示 "Present"
- **Step 47**: Education Level 显示 "Bachelor's Degree"
- **Step 56**: Education From 显示 "2016-09"
- **Step 65**: Education To 显示 "2020-06"
- **Step 69**: 点击 Done 后，`final_url` **不再包含** `resume/add`
  - 可能跳转到：简历详情页、招聘列表页、或其他成功页面
  - 关键验证：URL 已离开 `resume/add`，表示提交成功
- **数据库验证**（自动化脚本中执行）:
  - `resume` 表：`first_name='AutoTest'`, `last_name='Submit'`
  - `resume_person_info` 表：`email='yongli@58.com'`, `location='Spain'`
  - `resume_work_experience` 表：`job_function` 包含 'Testing', `from_date='2020-01'`
  - `resume_education` 表：`education_level` 包含 'Bachelor', `from_date='2016-09'`, `to_date='2020-06'`

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

#### 🔍 关键验证点
1. 入口访问：从招聘列表页 → 职位详情面板 → Resume 按钮 → 简历添加页
2. Step1 必填项：First Name、Last Name（Email 和 Location 自动预填）
3. Step2 Work Experience：Job Function 二级选择、From 日期、"当前在职"默认勾选
4. Step2 Education：Education Level 单级选择、From/To 日期
5. 提交成功：Done 按钮激活 → 点击 → 页面跳转 → 数据保存

---

### TC002: 完整提交流程 - 头像上传 + 有工作经验场景

#### 📋 前置条件
- 用户已登录账号 yongli@58.com
- 测试图片已放置于项目目录：`test_cases/zhaopin/1.jpg`
- 数据库中已清理该用户的历史简历数据

#### 🎬 执行步骤

**Step 1-5: 进入简历添加页面（同 TC001 步骤 1-5）**

**Step 6: 上传头像**
6. 定位页面中隐藏的 `input[type=file]` 文件输入框
7. 使用 Playwright `set_input_files()` 注入 `test_cases/zhaopin/1.jpg`
8. 等待 2 秒，确认头像预览区更新

**Step 7-15: 填写 Personal Information、Work Experience、Education Experience（同 TC001 步骤 6-25）**

**Step 16: 提交简历（同 TC001 步骤 26-28）**

#### ✅ 预期结果
- 头像上传后预览区显示上传图片（CDN URL）
- 提交成功后页面跳转离开 resume/add
- 数据库中保存的简历数据包含头像 URL

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC003: 完整提交流程 - 修改 Current Location 为其他国家

#### 📋 前置条件
- 用户已登录账号 yongli@58.com
- 数据库中已清理该用户的历史简历数据

#### 🎬 执行步骤

**Step 1-5: 进入简历添加页面（同 TC001 步骤 1-5）**
1. 访问招聘列表页 https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs
2. 点击第一张职位卡片（使用选择器 `.JobListItem_jobListItem__`）
3. 等待右侧详情面板加载完成（等待 `.JobDetail_jobDetail__` 元素可见，超时 5 秒）
4. 点击详情面板底部的 "Resume" 按钮（使用 `page.get_by_text("Resume").first`）
5. 等待页面跳转，验证 URL 包含 `resume/add`

**Step 6-10: 修改 Current Location**
6. 在 Step1 页面，定位 Current Location 输入框（选择器：`input[id*='country']`）
7. 点击 Current Location 输入框，触发国家选择面板
8. 等待国家列表面板加载完成（约 1 秒）
9. 在国家列表中使用 `page.get_by_text("France", exact=True)` 定位并点击 "France"
10. 等待 500ms，验证 Current Location 输入框的 `input_value()` 为 "France"

**Step 11-19: 填写 First Name、Last Name**
11. 在 First Name 输入框（选择器：`input[placeholder='First Name']`）输入 "LocationTest"
12. 验证字符计数器显示 "12/100"
13. 在 Last Name 输入框（选择器：`input[placeholder='Last Name']`）输入 "France"
14. 验证字符计数器显示 "6/100"
15. 验证 Email 预填为 "yongli@58.com"
16. 验证 Current Location 显示为 "France"
17. 验证 Continue 按钮变为可点击状态（无 `disabled` 属性）
18. 点击 Continue 按钮（选择器：`button:has-text('Continue')`）
19. 等待页面加载，验证进入 Step2（页面标题包含 "Recent Experience"）

**Step 20-35: 填写 Work Experience 和 Education（同 TC001 步骤 11-25）**

**Step 36-38: 提交简历**
36. 验证 Done 按钮变为可点击状态
37. 点击页面底部的 Done 按钮（使用 `.last` 定位最后一个 Done 按钮）
38. 等待 5 秒

#### ✅ 预期结果
- **Step 10**: Current Location 输入框的值成功更新为 "France"
- **Step 16**: Current Location 字段持久显示 "France"，未被重置
- **Step 38**: 点击 Done 后，页面 URL 不再包含 `resume/add`，跳转到简历详情页或招聘列表页
- **数据库验证**: 执行 SQL `SELECT location FROM resume_person_info WHERE user_id = '796579748218214624'`，返回值为 "France"

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

#### 🔍 关键验证点
1. 国家选择面板正确打开（检查面板元素是否可见）
2. 点击国家后面板自动关闭
3. 输入框值立即更新为选中的国家
4. 提交后数据库字段正确保存为选中的国家

---

### TC004: 完整提交流程 - 取消 "I currently work here" 并设置 To 日期

#### 📋 前置条件
- 用户已登录账号 yongli@58.com
- 数据库中已清理该用户的历史简历数据

#### 🎬 执行步骤

**Step 1-10: 进入简历添加页面并填写到 Step2（同 TC001 步骤 1-10）**
1-10. （执行 TC001 步骤 1-10）

**Step 11-13: 填写 Job Function**
11. 点击 Job Function 触发器（使用 `page.get_by_text("Select Job Functions")`）
12. 等待面板打开（1 秒）
13. 在左侧一级分类点击 "Information & Communication Technology"（使用 `page.get_by_text("Information & Communication Technology", exact=True)`）
14. 等待右侧二级分类加载（800ms）
15. 在右侧二级分类点击 "Testing & Quality Assurance"（使用 `page.get_by_text("Testing & Quality Assurance", exact=True)`）
16. 等待面板关闭（500ms）

**Step 14-17: 填写 Work Experience From 日期**
17. 定位 Work Experience 区域的第一个 DateFakerInput（使用 `page.locator("h2:has-text('Latest Work Experience')").locator("..").locator("[class*='DateFakerInput']").first`）
18. 点击 From 日期触发器
19. 等待日期选择器打开（500ms）
20. 在年份列表中点击 "2020"（使用 `page.get_by_text("2020", exact=True)`）
21. 等待 300ms
22. 在月份列表中点击 "1"（使用 `page.get_by_text("1", exact=True)`）
23. 等待 300ms
24. 点击日期选择器的 Done 按钮（选择器：`button:has-text('Done')`）
25. 等待 500ms
26. 验证 From 字段显示包含 "2020-01"

**Step 18-21: 取消 "I currently work here" 勾选**
27. 定位 "I currently work here" 区域（使用 `page.get_by_text("I currently work here")`）
28. 验证当前状态：查找 `img[alt="checked"]` 元素是否可见（应该可见，表示已勾选）
29. 点击 "I currently work here" 文本或复选框区域取消勾选
30. 等待 500ms
31. 验证取消勾选后状态：
    - `img[alt="checked"]` 元素不再可见
    - To 日期触发器从 "Present" 文本变为 "YYYY-MM" 占位符
    - To 日期触发器变为可点击状态

**Step 22-27: 设置 Work Experience To 日期**
32. 定位 Work Experience 区域的第二个 DateFakerInput（To 字段触发器）
33. 使用选择器 `page.locator("h2:has-text('Latest Work Experience')").locator("..").locator("[class*='DateFakerInput']").nth(1)` 定位 To 触发器
34. 点击 To 日期触发器
35. 等待日期选择器打开（500ms）
36. 在年份列表中点击 "2023"（使用 `page.get_by_text("2023", exact=True)`）
37. 等待 300ms
38. 在月份列表中点击 "12"（使用 `page.get_by_text("12", exact=True)`）
39. 等待 300ms
40. 点击日期选择器的 Done 按钮
41. 等待 500ms
42. 验证 To 字段显示包含 "2023-12"

**Step 28-36: 填写 Education Experience（同 TC001 步骤 18-25）**
43-50. （执行 TC001 步骤 18-25）

**Step 37-39: 提交简历**
51. 验证 Done 按钮变为可点击状态（检查最后一个 Done 按钮无 `disabled` 属性）
52. 点击页面底部的 Done 按钮（使用 `page.locator("button:has-text('Done')").last`）
53. 等待 5 秒

#### ✅ 预期结果
- **Step 28**: "I currently work here" 复选框显示已勾选状态（checked 图标可见）
- **Step 31**: 取消勾选后，To 字段从 "Present" 变为 "YYYY-MM" 占位符，字段变为可编辑状态
- **Step 42**: To 字段成功显示 "2023-12"
- **Step 53**: 点击 Done 后，页面 URL 不再包含 `resume/add`，跳转成功
- **数据库验证**: 
  - 执行 SQL `SELECT from_date, to_date FROM resume_work_experience WHERE user_id = '796579748218214624'`
  - 返回值：`from_date = '2020-01'`, `to_date = '2023-12'`（或具体的日期格式，如 '2023-12-01'）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

#### 🔍 关键验证点
1. "I currently work here" 默认勾选状态（checked 图标可见）
2. 取消勾选后 To 字段立即从 "Present" 变为可编辑状态
3. To 日期选择器能够正常打开并选择日期
4. To 日期成功保存并显示在字段中
5. 数据库 to_date 字段正确保存为 "2023-12"（而非 "Present" 或 NULL）

---

## B. 完整提交流程 - 无工作经验

### TC005: 完整提交流程 - 开启 "I have no work experience" 仅填写 Education

#### 📋 前置条件
- 用户已登录账号 yongli@58.com
- 数据库中已清理该用户的历史简历数据

#### 🎬 执行步骤

**Step 1-10: 进入简历添加页面并填写到 Step2（同 TC001 步骤 1-10）**

**Step 11: 开启无工作经验开关**
11. 点击 "I have no work experience" 开关
12. 确认工作经验字段（Job Function、From/To 日期）全部隐藏

**Step 12-17: 填写 Education Experience**
13. 点击 Education Level 下拉框
14. 选择 "Master's Degree"
15. 点击 Education From 日期选择器，选择 "2020" 年 "09" 月
16. 点击 Education To 日期选择器，选择 "2024" 年 "06" 月
17. 确认 Done 按钮变为可点击状态

**Step 18: 提交简历**
18. 点击 Done 按钮
19. 等待 5 秒

#### ✅ 预期结果
- 工作经验字段成功隐藏
- 仅填写 Education 部分后 Done 按钮激活
- 提交成功后页面跳转离开 resume/add
- 数据库中 resume_work_experience 表**无该用户记录**，resume_education 表有记录

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

## C. 提交后数据验证

### TC006: 提交后重新进入简历页面验证数据回显

#### 📋 前置条件
- 已完成 TC001 测试用例，简历数据已提交到数据库
- 用户仍保持登录状态
- 数据库中 user_id=796579748218214624 存在以下数据：
  - resume: first_name='AutoTest', last_name='Submit'
  - resume_person_info: email='yongli@58.com', location='Spain'
  - resume_work_experience: job_function='Testing & Quality Assurance', from_date='2020-01', to_date=NULL/Present
  - resume_education: education_level='Bachelor''s Degree', from_date='2016-09', to_date='2020-06'

#### 🎬 执行步骤

**Step 1-4: 重新进入招聘列表页并点击 Resume**
1. 使用 `page.goto("https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs")` 访问招聘列表页
2. 等待页面加载完成（`wait_for_load_state("domcontentloaded")`）
3. 点击第一张职位卡片（选择器：`.JobListItem_jobListItem__`，使用 `.first`）
4. 等待 1 秒
5. 等待详情面板加载（检查 `.JobDetail_jobDetail__` 元素是否可见，超时 5 秒）
6. 点击详情面板底部的 "Resume" 按钮（使用 `page.get_by_text("Resume").first.click()`）
7. 等待页面加载（`wait_for_load_state("domcontentloaded", timeout=15000)`）
8. 等待 3 秒
9. 获取当前页面 URL，记录为 `current_url`

**Step 5: 判断页面类型（编辑模式 vs 详情展示模式）**
10. 检查 URL 是否包含 `resume/add` 或 `resume/edit`
11. 如果包含：页面为编辑模式，继续步骤 11
12. 如果不包含：页面可能为简历详情展示页，需要查找编辑入口
    - 尝试查找 "Edit" 按钮（`page.get_by_text("Edit")`）
    - 如果找到 Edit 按钮，点击进入编辑模式
    - 如果没有 Edit 按钮，说明直接进入了编辑页面

**Step 6-10: 验证 Step1 Personal Information 数据回显**
13. 在 Step1 页面，定位 First Name 输入框（选择器：`input[placeholder='First Name']`）
14. 使用 `input_value()` 方法读取 First Name 字段值，记录为 `first_name_value`
15. 断言：`first_name_value == "AutoTest"`
16. 定位 Last Name 输入框（选择器：`input[placeholder='Last Name']`）
17. 使用 `input_value()` 方法读取 Last Name 字段值，记录为 `last_name_value`
18. 断言：`last_name_value == "Submit"`
19. 定位 Email 输入框（选择器：`input[type='email']`）
20. 使用 `input_value()` 方法读取 Email 字段值，记录为 `email_value`
21. 断言：`email_value == "yongli@58.com"`
22. 定位 Current Location 输入框（选择器：`input[id*='country']`）
23. 使用 `input_value()` 方法读取 Current Location 字段值，记录为 `location_value`
24. 断言：`location_value` 包含 "Spain" 或等于 "Spain"

**Step 11: 进入 Step2**
25. 点击 Continue 按钮（选择器：`button:has-text('Continue')`）
26. 等待页面加载（`wait_for_load_state("domcontentloaded", timeout=10000)`）
27. 等待 2 秒
28. 验证页面标题包含 "Recent Experience" 或存在 "Latest Work Experience" 文本

**Step 12-16: 验证 Step2 Work Experience 数据回显**
29. 定位 Job Function 显示区域（使用 `page.locator("div:has-text('Select Job Functions')")`）
30. 或者定位 Job Function 输入框（`input[id='custom-input-job-function']`）
31. 使用 `input_value()` 或 `text_content()` 读取 Job Function 字段值，记录为 `job_function_value`
32. 断言：`job_function_value` 包含 "Testing & Quality Assurance" 或 "Testing"
33. 定位 Work Experience From 字段（Work Experience 区域的第一个 DateFakerInput）
34. 使用选择器 `page.locator("h2:has-text('Latest Work Experience')").locator("..").locator("[class*='DateFakerInput']").first`
35. 读取 From 字段的显示文本（`text_content()`），记录为 `work_from_value`
36. 断言：`work_from_value` 包含 "2020-01" 或 "2020" 和 "01"
37. 检查 "I currently work here" 复选框状态
38. 查找 `img[alt="checked"]` 元素是否可见（使用 `is_visible(timeout=2000)`）
39. 断言：`img[alt="checked"]` 可见，表示"当前在职"为勾选状态
40. 定位 Work Experience To 字段（Work Experience 区域的第二个 DateFakerInput）
41. 读取 To 字段的显示文本，记录为 `work_to_value`
42. 断言：`work_to_value` 包含 "Present" 或为空（因为勾选了"当前在职"）

**Step 17-19: 验证 Step2 Education Experience 数据回显**
43. 定位 Education Level 显示区域或输入框
44. 使用 `page.locator("div:has-text('Education Level')")` 或查找对应的 select/input 元素
45. 读取 Education Level 字段值，记录为 `education_level_value`
46. 断言：`education_level_value` 包含 "Bachelor's Degree" 或 "Bachelor"
47. 定位 Education From 字段（Education 区域的第一个 DateFakerInput）
48. 使用选择器 `page.locator("h2:has-text('Education Experience')").locator("..").locator("[class*='DateFakerInput']").first`
49. 读取 Education From 字段的显示文本，记录为 `edu_from_value`
50. 断言：`edu_from_value` 包含 "2016-09" 或 "2016" 和 "09"
51. 定位 Education To 字段（Education 区域的第二个 DateFakerInput）
52. 使用选择器 `page.locator("h2:has-text('Education Experience')").locator("..").locator("[class*='DateFakerInput']").nth(1)`
53. 读取 Education To 字段的显示文本，记录为 `edu_to_value`
54. 断言：`edu_to_value` 包含 "2020-06" 或 "2020" 和 "06"

#### ✅ 预期结果
- **Step 9**: 页面成功加载，URL 包含 `resume` 关键词（可能是 `resume/add`、`resume/edit` 或简历详情页）
- **Step 15**: First Name 字段值为 "AutoTest"
- **Step 18**: Last Name 字段值为 "Submit"
- **Step 21**: Email 字段值为 "yongli@58.com"
- **Step 24**: Current Location 字段值包含或等于 "Spain"
- **Step 32**: Job Function 字段值包含 "Testing & Quality Assurance"
- **Step 36**: Work Experience From 字段值包含 "2020-01"
- **Step 39**: "I currently work here" 复选框为勾选状态
- **Step 42**: Work Experience To 字段显示 "Present" 或为空（表示当前在职）
- **Step 46**: Education Level 字段值包含 "Bachelor's Degree"
- **Step 50**: Education From 字段值包含 "2016-09"
- **Step 54**: Education To 字段值包含 "2020-06"
- **整体验证**: 所有字段数据与 TC001 提交的数据完全一致，数据回显正确无误

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

#### 🔍 关键验证点
1. 重新进入 Resume 页面后，系统能够正确识别用户已有简历数据
2. Step1 所有字段（First Name、Last Name、Email、Current Location）正确回显
3. Step2 Work Experience 所有字段（Job Function、From、To、"当前在职"状态）正确回显
4. Step2 Education Experience 所有字段（Level、From、To）正确回显
5. 日期格式一致性（"2020-01" 格式）
6. "当前在职"状态正确保留（勾选框状态 + To 字段显示 "Present"）

#### ⚠️ 注意事项
- 本用例依赖 TC001 先执行，确保数据库中存在测试数据
- 如果页面跳转到简历详情展示页而非编辑页，需要先点击 Edit 按钮进入编辑模式
- 使用 `input_value()` 读取输入框值，使用 `text_content()` 读取静态显示文本
- 日期字段可能返回包含标签的文本（如 "From\n2020-01"），需要使用 `in` 判断而非完全相等

---

### TC007: 数据库数据验证 - 验证 resume 相关表数据完整性

#### 📋 前置条件
- 已完成 TC001 测试用例，简历数据已提交到数据库
- 数据库连接配置正确：pgsql-test.pdb.58dns.org:29000/pdb58_easypost

#### 🎬 执行步骤

**Step 1: 查询 resume 表**
1. 执行 SQL：`SELECT * FROM resume WHERE user_id = '796579748218214624'`
2. 验证返回 1 条记录
3. 验证字段：first_name='AutoTest', last_name='Submit'

**Step 2: 查询 resume_person_info 表**
4. 执行 SQL：`SELECT * FROM resume_person_info WHERE user_id = '796579748218214624'`
5. 验证返回 1 条记录
6. 验证字段：email='yongli@58.com', location='Spain'

**Step 3: 查询 resume_work_experience 表**
7. 执行 SQL：`SELECT * FROM resume_work_experience WHERE user_id = '796579748218214624'`
8. 验证返回 1 条记录
9. 验证字段：job_function='Testing & Quality Assurance', from_date='2020-01', to_date='Present' 或 NULL

**Step 4: 查询 resume_education 表**
10. 执行 SQL：`SELECT * FROM resume_education WHERE user_id = '796579748218214624'`
11. 验证返回 1 条记录
12. 验证字段：education_level='Bachelor''s Degree', from_date='2016-09', to_date='2020-06'

#### ✅ 预期结果
- 所有表均返回记录，数据完整
- 字段值与 TC001 提交的数据一致
- user_id 关联正确

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 数据验证
- **UI自动化**: ✅ 可自动化（通过 db_client 工具）

---

## D. 数据库清理验证

### TC008: 数据库清理 - 删除 user_id=796579748218214624 的所有简历数据

#### 📋 前置条件
- 数据库中存在 user_id=796579748218214624 的简历数据
- 数据库连接配置正确

#### 🎬 执行步骤

**Step 1: 删除 resume_work_experience 表数据**
1. 执行 SQL：`DELETE FROM resume_work_experience WHERE user_id = '796579748218214624'`
2. 记录受影响行数

**Step 2: 删除 resume_education 表数据**
3. 执行 SQL：`DELETE FROM resume_education WHERE user_id = '796579748218214624'`
4. 记录受影响行数

**Step 3: 删除 resume_person_info 表数据**
5. 执行 SQL：`DELETE FROM resume_person_info WHERE user_id = '796579748218214624'`
6. 记录受影响行数

**Step 4: 删除 resume 表数据**
7. 执行 SQL：`DELETE FROM resume WHERE user_id = '796579748218214624'`
8. 记录受影响行数

**Step 5: 验证清理结果**
9. 执行 SQL：`SELECT COUNT(*) FROM resume WHERE user_id = '796579748218214624'`
10. 验证返回 0
11. 对其他三个表执行相同验证

#### ✅ 预期结果
- 所有 DELETE 操作成功执行
- 验证查询均返回 0，确认数据已完全清理
- 数据库无该用户的简历数据残留

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 数据清理
- **UI自动化**: ✅ 可自动化（通过 db_client 工具）

---

## 测试统计

### 用例概览

> 📌 **统计说明**：本测试用例文档聚焦于真正提交简历并验证数据的核心流程。

| 维度 | 数值 |
|------|------|
| 总用例数 | 8条（TC001~TC008） |
| ✅ 可自动化 | 8条（100%） |
| ❌ 不可自动化 | 0条 |

### 按优先级分布

| 优先级 | 总数 | 可自动化 | 不可自动化 | 自动化率 |
|--------|------|---------|----------|---------|
| P0 | 5 | 5 | 0 | 100% |
| P1 | 3 | 3 | 0 | 100% |
| **合计** | **8** | **8** | **0** | **100%** |

### 按功能模块分布

| 模块 | 用例数 |
|------|--------|
| 完整提交流程 - 有工作经验 | 4 |
| 完整提交流程 - 无工作经验 | 1 |
| 提交后数据验证 | 1 |
| 数据库数据验证 | 1 |
| 数据库清理验证 | 1 |

### 覆盖度评估

- 功能点覆盖: 100% ✅（聚焦提交流程）
- 场景覆盖: 100% ✅（有工作经验 + 无工作经验）
- 数据验证覆盖: 100% ✅（页面回显 + 数据库验证）
- 数据清理覆盖: 100% ✅（完整清理流程）

---

## 附录：数据库清理 SQL

```sql
-- 按顺序执行（外键约束）
DELETE FROM resume_work_experience WHERE user_id = '796579748218214624';
DELETE FROM resume_education WHERE user_id = '796579748218214624';
DELETE FROM resume_person_info WHERE user_id = '796579748218214624';
DELETE FROM resume WHERE user_id = '796579748218214624';

-- 验证清理结果
SELECT COUNT(*) FROM resume WHERE user_id = '796579748218214624';  -- 应返回 0
SELECT COUNT(*) FROM resume_person_info WHERE user_id = '796579748218214624';  -- 应返回 0
SELECT COUNT(*) FROM resume_work_experience WHERE user_id = '796579748218214624';  -- 应返回 0
SELECT COUNT(*) FROM resume_education WHERE user_id = '796579748218214624';  -- 应返回 0
```

---

**文档说明**:
- 本文档专注于真正提交简历的核心流程测试
- 所有用例均包含完整的数据验证和清理步骤
- 测试完成后必须执行数据库清理（TC008）
- 适合自动化脚本生成，覆盖率达到 100%
