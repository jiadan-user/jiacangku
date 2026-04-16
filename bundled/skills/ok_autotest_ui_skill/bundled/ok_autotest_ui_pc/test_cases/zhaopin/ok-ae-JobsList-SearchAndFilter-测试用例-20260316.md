# OK AE 站 - Jobs 招聘列表页 搜索与筛选 测试用例

> **生成时间**: 2026-03-16（最后更新：2026-03-16）  
> **测试范围**: 搜索框、Recent Searches、搜索中间页（页面结构/卡片点击/修改搜索词）、所有筛选项（Location/Job Type/Workplace type/Salary）、切换岗位偏好类别、Reset、翻页  
> **总用例数**: 63条（TC001~TC063，连续编号）  
> **可自动化**: 62条 (98%)  
> **不可自动化**: 1条（TC015 - 系统地理位置权限）  
> **录制来源**: MCP Playwright 浏览器录制  

---

## 测试环境配置（必填）

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | ae | ae 站 |
| 基础URL | https://ae.58v5.cn | AE 测试站点 |
| 站点名称 | UAE站 | 阿联酋站 |
| 角色 | buyer | 求职者（已登录） |
| 账号名称 | ae_buyer_wangyongli | 用于 session 命名 |
| 测试账号 | wangyongli@58.com | 登录邮箱 |
| 测试密码 | Qwer1234 | 登录密码 |

**说明**：测试账号已有岗位偏好，访问 `https://ae.58v5.cn/en/city/cate-jobs/?iconSource=jobs` 进入招聘列表页。地址筛选框默认无值（显示 "Location"）。

---

## 📑 目录

- [搜索框功能](#搜索框功能)（TC001~TC009）
  - TC001: 搜索关键词跳转中间页
  - TC002: 空格搜索
  - TC003: 超长关键词
  - TC004: 特殊字符
  - TC005: 中文关键词
  - TC006: Enter 键触发搜索
  - TC007: 已有筛选条件时搜索
  - TC008: 聚焦搜索框显示 Recent Searches
  - TC009: 点击历史记录触发搜索
- [搜索中间页](#搜索中间页)（TC010）
  - TC010: 在搜索页修改关键词并再次搜索
- [Location 地址筛选](#location-地址筛选)（TC011~TC016）
- [Job Type 工作类型筛选](#job-type-工作类型筛选)（TC017~TC022）
- [Workplace Type 工作方式筛选](#workplace-type-工作方式筛选)（TC023~TC027）
- [Salary 薪资筛选](#salary-薪资筛选)（TC028~TC036）
- [岗位偏好类别切换（Job Preferences Category）](#岗位偏好类别切换)（TC037~TC041）
- [Reset 重置功能](#reset-重置功能)（TC042~TC045）
- [翻页功能](#翻页功能)（TC046~TC049）
- [筛选组合与联动](#筛选组合与联动)（TC050~TC063）

---

## 测试概述

### 页面结构（MCP 录制确认）

- **顶部搜索栏**：`textbox "Search for anything"` + `button "Search"`
- **岗位偏好类别栏**：横向滚动标签（如 Accounts Officers/Clerks、Accounts Payable 等） + `link "Edit"`
- **筛选栏**：Location | Job Type（选后显示·N徽章） | Workplace type | Salary | Reset
- **列表区域**：左侧职位卡片列表 + 右侧详情面板（默认展开第一条）
- **无筛选条件时**：地址筛选器显示"Location"（无默认值）
- **分页方式**：无限滚动到底部（`You've reached the end`）
- **搜索跳转**：搜索后进入中间搜索结果页（URL包含`keyword=xxx`），页面结构变化

### 关键业务规则（对齐ES站MCP实测）

1. **搜索行为**：输入关键词点击Search后，URL追加 `keyword=xxx`；空搜索也会触发，URL包含 `keyword=`（空值）
2. **Job Type参数**：Full-time对应 `attr_60=1`，多选使用逗号分隔（如 `attr_60=2%2C1`），筛选器显示 "Job Type · N"
3. **Workplace type参数**：Onsite/Remote/Hybrid对应相应参数，筛选器显示 "Workplace type · N"
4. **Salary参数**：最低薪资为 `lowestPrice`，最高薪资为 `highestPrice`；Per Hour为默认不追加周期参数，Per Month对应 `attr_80=4`；同时填写Min+Max时筛选器显示 "Salary · 2"
5. **Reset行为**：清除所有筛选参数（`attr_60`、`attr_80`、`lowestPrice`、`highestPrice`等），URL恢复为 `?iconSource=jobs`；搜索词 `keyword` 参数**保留**
6. **Location行为**：选择具体城市后URL路径变为 `/en/city-xxx/cate-jobs/`；选择"All UAE"后URL变为 `/en/city/cate-jobs/`，筛选器文案恢复为 "Location"
7. **输入框约束**：Salary的Min/Max输入框为 `type="text"`，无HTML属性约束；字母/负号被自动拦截（输入后值为空），小数被接受；Min>Max提交时显示 "Max price must be higher than min price"
8. **面板Clear行为**：仅清空面板内选中状态，面板保持打开，URL不变（需点击Confirm才生效）
9. **无限滚动**：列表采用feed流模式，无分页按钮（无Previous/Next/页码）；滚动到底部自动追加新卡片，URL始终不变；加载完毕显示 "You've reached the end"
10. **Recent Searches**：在 Jobs 列表页（搜索框为空）聚焦搜索框时，展示历史搜索下拉（标题"Recent Searches"，最多7条，含清空按钮）；每条为 `cursor=pointer` 的 div，点击触发对应关键词搜索（跳转中间页）；历史支持各类字符（中文、特殊符号、超长文本）
11. **搜索中间页差异**：进入搜索中间页（`?keyword=xxx`）后，页面结构发生根本变化——无偏好标签栏、无右侧详情面板、无 Reset 按钮、**无清空搜索词按钮（× 号）**；搜索框右侧出现当前搜索词 chip（可点击但只触发重新搜索，非清空）；筛选栏新增 `Best Match`、`Filter·N`、`Jobs`、`Unit`；结果卡片为 `<a>` link 元素（点击新标签打开）；`Filter·N` 数字反映所有已激活维度（含 keyword 本身计1）；修改关键词须手动编辑搜索框内容

---

## 搜索框功能

### TC001: 在Jobs列表页搜索框输入关键词并点击Search-应跳转搜索中间页且URL包含keyword

#### 📋 前置条件
- 已登录账号（有岗位偏好）
- 当前页面：`https://ae.58v5.cn/en/city/cate-jobs/?iconSource=jobs`

#### 🎬 执行步骤
1. 点击顶部搜索框 `textbox "Search for anything"`
2. 输入关键词 `manager`
3. 点击 `button "Search"`
4. 等待页面加载完成

#### ✅ 预期结果（MCP实测更新）
1. URL 变为 `https://ae.58v5.cn/en/city/cate-jobs/?keyword=manager`（**仅保留 `keyword` 参数，`iconSource=jobs` 被移除**）
2. 页面进入搜索中间页视图，页面结构从「左侧职位卡片+右侧详情面板」变为**纯卡片链接列表**（每条职位为独立 `<a>` link 元素）
3. 顶部筛选栏变为：`Best Match` | `Filter·1` | `Jobs` | `Location` | `Salary` | `Job Type` | `Workplace type` | `Unit`
4. 面包屑显示 `Category:Jobs`
5. **岗位偏好类别标签栏消失**（搜索后不显示）
6. 右侧详情面板消失（搜索中间页无双栏结构）
7. 结果卡片格式：公司名、职位名、描述摘要、地点（带图标）、薪资

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC002: 搜索框输入空格后点击Search-不显示结果

#### 📋 前置条件
- 当前页面：Jobs 列表页

#### 🎬 执行步骤
1. 点击搜索框
2. 输入若干空格（如3个空格）
3. 点击 Search 按钮

#### ✅ 预期结果（MCP实测更新）
1. URL 变为 `?iconSource=jobs&keyword=%20%20%20`（**保留 `iconSource=jobs` 参数**，与普通关键词搜索不同；空格被编码为 `%20`，有多少空格就有多少 `%20`）
2. 进入搜索中间页视图，筛选栏变为 `Best Match | Filter·1 | Jobs | Location | Salary | Job Type | Workplace type | Unit`
3. 职位列表为空，页面显示无结果插图 + 文案 **"We couldn't find anything. Try a new search"**
4. analytics 触发 `no_result_show` 事件（可通过控制台确认）
5. 右侧详情面板消失（无结果时不显示）
6. **注意**：空格搜索不会跳转到独立路径，路径仍为 `/en/city/cate-jobs/`

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界测试
- **UI自动化**: ✅ 可自动化

---

### TC003: 搜索框输入超长关键词-不报错且正常展示结果

#### 📋 前置条件
- 当前页面：Jobs 列表页

#### 🎬 执行步骤
1. 点击搜索框
2. 输入超过200字符的关键词
3. 点击 Search 按钮

#### ✅ 预期结果（MCP实测更新）
1. 输入框无 `maxlength` 属性限制，允许输入 200+ 字符（实测输入210字符全部被接收）
2. 搜索请求正常发送，URL 完整保留超长词（不截断），格式为 `?keyword=aaa...（N个字符）`（**不附带 `iconSource=jobs`**）
3. 返回无结果，analytics 触发 `no_result_show` 事件，页面显示 "We couldn't find anything. Try a new search"

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界测试
- **UI自动化**: ✅ 可自动化

---

### TC004: 搜索框输入特殊字符-不报错

#### 📋 前置条件
- 当前页面：Jobs 列表页

#### 🎬 执行步骤
1. 点击搜索框
2. 输入特殊字符 `@#$%`
3. 点击 Search 按钮

#### ✅ 预期结果（MCP实测更新）
1. URL 正确编码特殊字符：`?keyword=%40%23%24%25`（`@`→`%40`，`#`→`%23`，`$`→`%24`，`%`→`%25`；**不附带 `iconSource=jobs`**）
2. analytics 触发 `no_result_show` 事件，职位列表为空，显示 "We couldn't find anything. Try a new search"

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 安全测试
- **UI自动化**: ✅ 可自动化

---

### TC005: 搜索框输入中文关键词-正常搜索

#### 📋 前置条件
- 当前页面：Jobs 列表页

#### 🎬 执行步骤
1. 点击搜索框
2. 输入中文关键词，如 `工程师`
3. 点击 Search 按钮

#### ✅ 预期结果（MCP实测更新）
1. URL 为 `?keyword=%E5%B7%A5%E7%A8%8B%E5%B8%88`（中文「工程师」的UTF-8编码，**不附带 `iconSource=jobs`**）
2. AE站为英文职位平台，中文搜索触发 `no_result_show` 事件，显示 "We couldn't find anything. Try a new search"

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC006: 搜索框按Enter键触发搜索-与点击Search等效

#### 📋 前置条件
- 当前页面：Jobs 列表页

#### 🎬 执行步骤
1. 点击搜索框
2. 输入关键词 `developer`
3. 按 Enter 键

#### ✅ 预期结果（MCP实测更新）
- 与点击 Search 按钮效果完全相同：URL 变为 `?keyword=developer`（**不附带 `iconSource=jobs`**），进入搜索中间页视图

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC007: 已有筛选条件时搜索-搜索结果URL保留筛选参数

#### 📋 前置条件
- 当前页面：Jobs 列表页
- 已设置 Job Type = Full-time（URL: `?iconSource=jobs&attr_60=1`）

#### 🎬 执行步骤
1. 在当前有筛选条件的列表页搜索框输入 `manager`
2. 点击 Search 按钮

#### ✅ 预期结果（MCP实测更新）
- URL 变为 `?attr_60=1&keyword=manager`（**`iconSource=jobs` 被移除**，`attr_60=1` 保留，`keyword=manager` 追加）
- 进入搜索中间页视图，筛选栏 Job Type 显示徽章（`Job Type` 已激活）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC008: 搜索框聚焦时显示Recent Searches历史记录下拉

#### 📋 前置条件
- 当前页面：Jobs 列表页（`?iconSource=jobs`，搜索框为空）
- 已登录账号，且历史上曾搜索过关键词（如 `manager`、`engineer` 等）

#### 🎬 执行步骤
1. 点击顶部搜索框（`textbox "Search for anything"`，ref=e14）
2. 不输入任何内容，仅聚焦

#### ✅ 预期结果（MCP实测更新）
1. 搜索框下方出现历史搜索记录下拉（ref=e893）
2. 下拉标题为 **"Recent Searches"**（ref=e894）
3. 历史记录最多显示 **10 条**，每条含历史图标 + 关键词文本，均为 `cursor=pointer`（ref=e895~e907）
4. 实测历史记录内容：`manager`、`engineer`、`xyzxyzxyz12345`、`developer`、`工程师`、`@#$%`、超长字符串（支持中文、特殊字符、超长文本等各类历史词）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC009: 点击Recent Searches历史记录条目-触发搜索并进入中间页

#### 📋 前置条件
- Jobs 列表页搜索框已聚焦，Recent Searches 下拉已显示
- 历史记录中含 `manager` 条目

#### 🎬 执行步骤
1. 点击 Recent Searches 下拉中的 `manager` 历史条目（ref=e895，`cursor=pointer`）

#### ✅ 预期结果（MCP实测更新）
1. 搜索框填充该历史词（显示 `manager`）
2. 页面跳转至搜索中间页，URL 变为 `?keyword=manager`（**不含 `iconSource=jobs`**）
3. 进入搜索中间页结构（链接列表）
4. analytics 触发 `search_sug_click` 事件

> **Playwright 定位参考**：历史条目为 `generic[cursor=pointer]` 内嵌文本节点，需使用 `page.evaluate()` 点击（如查找 `textContent === 'manager'` 的 text 节点的父 `cursor=pointer` 容器）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---


### TC010: 搜索中间页-在搜索页继续修改关键词并再次搜索

#### 📋 前置条件
- 已在搜索中间页（URL: `?keyword=manager`）

#### 🎬 执行步骤
1. 点击搜索框（ref=e14），手动全选并删除旧关键词（Ctrl+A → Delete / 三击选中 → 清空）
   > ⚠️ 搜索中间页**没有清空按钮（× 号）**，也不能点击搜索词 chip（chip 点击只会重新搜索同词）；修改关键词只能通过手动编辑搜索框内容实现
2. 输入新关键词 `engineer`
3. 点击 `button "Search"` 或按 Enter 键

#### ✅ 预期结果（MCP实测更新）
- URL 更新为 `?keyword=engineer`（旧关键词被完全替换，**不附带 `iconSource=jobs`**）
- 搜索框显示 `engineer`，搜索词 chip 同步更新为 `engineer`
- 结果列表重新加载，显示 engineer 相关职位

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

## Location 地址筛选

### TC011: 点击Location筛选框-弹出城市选择面板且默认无选中值

#### 📋 前置条件
- 当前页面：Jobs 列表页（URL: `?iconSource=jobs`）
- 未设置任何地址筛选

#### 🎬 执行步骤
1. 点击 `Location` 筛选项（ref=e48，text="Location"）

#### ✅ 预期结果
- 弹出城市选择面板
- 面板标题为 "Select Location"
- 包含搜索框 `textbox "Search City"`
- 包含提示文案（关于位置设置的说明）
- 包含 "Use current location" 按钮
- **历史记录区**：顶部显示最近选择的城市（如 `Dubai`）——点击可快速选择
- 提示文案：`"Results are based on the location you selected for this search. To change your preferred work location, update it in job preference."` + `link "Set now"`
- `button "Use current location"` ✅（TC015 单独测试）
- 城市列表（完整）：`All United Arab Emirates`、`Dubai`、`Abu Dhabi`、`Ras al Khaimah`、`Sharjah`、`Fujairah`、`Ajman`、`Umm al Quwain`、`Al Ain`
- **无默认选中城市**（筛选器显示"Location"而非具体城市名）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC012: Location筛选-选择Dubai城市-页面URL更新且结果过滤

#### 📋 前置条件
- 已打开 Location 选择面板

#### 🎬 执行步骤
1. 点击面板中的 `Dubai`（ref=e925，使用选择器 `div:nth-child(2) > .CascadingSelector_itemContent__RM88u > div`）

#### ✅ 预期结果（MCP实测更新）
1. 面板关闭
2. URL 变更为 `https://ae.58v5.cn/en/city-dubai/cate-jobs/?iconSource=jobs`（**路径从 `/city/` 变为 `/city-dubai/`，不再是 query param**）
3. 筛选栏 Location 显示 **"Dubai"**（而非默认的 "Location"）
4. 职位列表刷新，显示 Dubai 范围职位（页面标题变为 `140 Jobs in the Dubai...`）
5. 底部页脚从 "Popular Cities" 变为 **"Popular Jobs"** 标签（显示Dubai职位分类链接）
6. analytics 触发 `location_list_click` 和 `filterSubmit` 事件

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC013: Location筛选-搜索城市名过滤列表

#### 📋 前置条件
- 已打开 Location 选择面板

#### 🎬 执行步骤
1. 在 `textbox "Search City"` 中输入 `Abu`

#### ✅ 预期结果
1. 城市列表实时过滤，仅显示包含 "Abu" 的城市
2. 实测显示：过滤后列表仅剩 **"Abu Dhabi"**（附带 `United Arab Emirates,Abu Dhabi` 地理信息）
3. 输入框右侧出现清除按钮（`×`），点击可清空输入并恢复完整列表

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC014: Location筛选-选择All United Arab Emirates-返回全国职位

#### 📋 前置条件
- 已选择某城市（如 Dubai）

#### 🎬 执行步骤
1. 再次点击 Location 筛选项
2. 选择 `All United Arab Emirates`（ref=e922）

#### ✅ 预期结果
1. 面板关闭
2. URL 路径变更为 **`/en/city/cate-jobs/?iconSource=jobs`**（含 `city` 段，无具体城市标识符）
3. 筛选栏 Location 恢复为 **"Location"**（通用占位文案，非 "All UAE"）
4. 职位列表更新为全国职位（数量增多）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC015: Location筛选-Use current location按钮触发定位权限

#### 📋 前置条件
- 已打开 Location 选择面板

#### 🎬 执行步骤
1. 点击 `button "Use current location"` 按钮

#### ✅ 预期结果
1. 浏览器弹出地理位置权限请求弹窗
2. 若授权：根据地理位置筛选职位，URL 变更为最近城市路径
3. 若拒绝：保持当前状态，页面无报错

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ❌ 不可自动化

---

### TC016: Location筛选-提示文案中Set now链接可点击

#### 📋 前置条件
- 已打开 Location 选择面板，面板显示提示文案

#### 🎬 执行步骤
1. 点击提示文案中的 `link "Set now"`（ref=e914）

#### ✅ 预期结果
- 跳转到岗位偏好设置页面（job preference）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

## Job Type 工作类型筛选

### TC017: 点击Job Type筛选框-弹出工作类型选择面板

#### 📋 前置条件
- 当前页面：Jobs 列表页，未选任何 Job Type 筛选

#### 🎬 执行步骤
1. 点击筛选栏 `Job Type` 筛选项（定位器：`page.locator('#istPageFilterArea').getByText('Job Type').click()`）

#### ✅ 预期结果
1. Job Type 面板在页面下方弹出
2. 显示 5 个选项（按顺序）：`Full-time`、`Part-time`、`Contract`、`Internship`、`Temporary`
3. **初始状态：所有 5 个选项均显示 `icon-selected` 图标（全选状态）**
4. 显示 `Clear` 按钮和 `Confirm` 按钮
5. 筛选栏 Job Type 标签无数字徽章（无已确认筛选项）

> **关键行为说明**：Job Type 面板默认全选所有类型（即未筛选状态），点击某选项会**取消**该选项的选中状态。

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC018: Job Type筛选-仅选Full-time后点击Confirm-URL参数更新

#### 📋 前置条件
- Job Type 面板已打开

#### 🎬 执行步骤
1. 点击面板内 `Clear` 按钮，取消所有选中状态（`page.getByRole('button', { name: 'Clear' }).click()`）
2. 点击 `Full-time` 选项（`page.locator('.Selector_optionItem__er6y4').filter({ hasText: 'Full-time' }).click()`）
3. 点击 `Confirm` 按钮（`page.getByRole('button', { name: 'Confirm' }).click()`）

#### ✅ 预期结果
1. 面板关闭
2. URL 变为 **`?iconSource=jobs&attr_60=1`**（`attr_60=1` 对应 Full-time）
3. 筛选栏显示 **"Job Type · 1"**（数字徽章 1 表示已选 1 个类型）
4. 职位列表仅显示 Full-time 类型职位
5. 触发 `filterClick` 和 `filterSubmit` 分析事件

> **attr_60 参数映射**：Full-time=1, Part-time=2, Contract=3, Internship=4, Temporary=5

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC019: Job Type筛选-同时选择多个类型-URL参数包含多个值

#### 📋 前置条件
- Job Type 面板已打开

#### 🎬 执行步骤
1. 点击 `Clear` 按钮取消全选
2. 点击 `Full-time` 选项（`page.locator('.Selector_optionItem__er6y4').filter({ hasText: 'Full-time' }).click()`）
3. 点击 `Part-time` 选项（`page.locator('.Selector_optionItem__er6y4').filter({ hasText: 'Part-time' }).click()`）
4. 点击 `Confirm` 按钮

#### ✅ 预期结果
1. 面板关闭
2. URL 变为 **`?iconSource=jobs&attr_60=1%2C2`**（逗号被 URL 编码为 `%2C`；Full-time=1，Part-time=2）
3. 筛选栏显示 **"Job Type · 2"**（数字徽章为 2）
4. 职位列表显示 Full-time 和 Part-time 职位（满足任意一种类型均显示）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC020: Job Type筛选-点击Clear按钮-清除面板内已选项但不触发筛选

#### 📋 前置条件
- 已打开 Job Type 选择面板，已选中若干选项

#### 🎬 执行步骤
1. 选中 Full-time 和 Part-time
2. 点击 `button "Clear"`

#### ✅ 预期结果
1. 所有选项取消勾选
2. 面板仍然打开
3. URL 未变更（点击 Confirm 后才生效）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC021: Job Type筛选-不选任何选项直接Confirm-筛选器无徽章

#### 📋 前置条件
- 已打开 Job Type 选择面板，未选中任何选项

#### 🎬 执行步骤
1. 不选中任何 Job Type
2. 点击 `Confirm` 按钮

#### ✅ 预期结果
1. 面板关闭
2. 筛选栏 Job Type 无数字徽章显示（文案仅为 "Job Type"）
3. URL 不包含 `attr_60` 等 Job Type 相关参数

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界测试
- **UI自动化**: ✅ 可自动化

---

### TC022: Job Type筛选-按Escape键关闭面板-不触发筛选

#### 📋 前置条件
- 已打开 Job Type 选择面板

#### 🎬 执行步骤
1. 选中 Full-time
2. 按 `Escape` 键（`page.keyboard.press('Escape')`）

#### ✅ 预期结果
1. 面板关闭
2. URL 不变（未触发 Confirm）
3. 筛选栏无徽章

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

## Workplace Type 工作方式筛选

### TC023: 点击Workplace type筛选框-弹出工作方式选择面板

#### 📋 前置条件
- 当前页面：Jobs 列表页，未选任何 Workplace type 筛选

#### 🎬 执行步骤
1. 点击筛选栏 `Workplace type` 筛选项（`page.locator('#istPageFilterArea').getByText('Workplace type').click()`）

#### ✅ 预期结果
1. Workplace type 面板弹出
2. 显示 **3 个**工作地点类型选项（按顺序）：`Onsite`、`Remote`、`Hybrid`，均可点击
3. 初始状态：所有 3 个选项均显示 `icon-selected`（默认全选状态）
4. 显示 `Clear` 按钮和 `Confirm` 按钮

> **attr_61 参数映射**：Onsite=1, Remote=2, Hybrid=3

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC024: Workplace type筛选-选择Onsite后Confirm-URL更新且结果过滤

#### 📋 前置条件
- Workplace type 面板已打开

#### 🎬 执行步骤
1. 点击 `Clear` 按钮取消全选
2. 点击 `Onsite` 选项（`page.locator('.Selector_optionItem__er6y4').filter({ hasText: 'Onsite' }).click()`）
3. 点击 `Confirm` 按钮

#### ✅ 预期结果
1. 面板关闭
2. URL 变为 **`?iconSource=jobs&attr_61=1`**（`attr_61=1` 对应 Onsite）
3. 筛选栏显示 **"Workplace type · 1"**
4. 职位列表仅显示 Onsite 类型职位
5. 触发 `filterSubmit` 分析事件

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC025: Workplace type筛选-选择Remote-职位列表显示Remote职位

#### 📋 前置条件
- Workplace type 面板已打开

#### 🎬 执行步骤
1. 点击 `Clear` 取消全选
2. 点击 `Remote` 选项（`page.locator('.Selector_optionItem__er6y4').filter({ hasText: 'Remote' }).click()`）
3. 点击 `Confirm`

#### ✅ 预期结果
1. 面板关闭
2. URL 变为 **`?iconSource=jobs&attr_61=2`**（`attr_61=2` 对应 Remote）
3. 筛选栏显示 **"Workplace type · 1"**
4. 职位列表仅显示 Remote 类型职位

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC026: Workplace type筛选-选择Hybrid-职位列表显示Hybrid职位

#### 📋 前置条件
- Workplace type 面板已打开

#### 🎬 执行步骤
1. 点击 `Clear` 取消全选
2. 点击 `Hybrid` 选项（`page.locator('.Selector_optionItem__er6y4').filter({ hasText: 'Hybrid' }).click()`）
3. 点击 `Confirm`

#### ✅ 预期结果
1. 面板关闭
2. URL 变为 **`?iconSource=jobs&attr_61=3`**（`attr_61=3` 对应 Hybrid）
3. 筛选栏显示 **"Workplace type · 1"**
4. 职位列表仅显示 Hybrid 类型职位

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC027: Workplace type筛选-Clear按钮清除已选项

#### 📋 前置条件
- 已打开 Workplace type 面板，已选中 Onsite

#### 🎬 执行步骤
1. 点击 `Clear`（ref=e822）

#### ✅ 预期结果
1. 所有选项取消勾选
2. 面板仍然打开
3. URL 未变更（点击 Confirm 后才生效）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

## Salary 薪资筛选

### TC028: 点击Salary筛选框-弹出薪资设置面板

#### 📋 前置条件
- 当前页面：Jobs 列表页，未选任何 Salary 筛选

#### 🎬 执行步骤
1. 点击筛选栏 `Salary` 筛选项（`page.locator('#istPageFilterArea').getByText('Salary').click()`）

#### ✅ 预期结果
1. Salary 面板从页面底部弹出
2. 面板顶部显示 **6 个**薪资周期选项（横向排列）：`Per Hour` / `Per Day` / `Per Week` / `Per Month` / `Per Biweek` / `Per Year`
3. 面板中部显示两个文本输入框：`Min`（placeholder="Min"）和 `Max`（placeholder="Max"），类型为 `type="text"` 无数值约束
4. 面板底部显示 `Clear` 和 `Confirm` 按钮

> **attr_80 参数映射**：Per Hour=无参数, Per Day=2, Per Week=3, Per Month=4, Per Biweek=5, Per Year=6

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC029: Salary筛选-选择Per Month并输入Min/Max后Confirm-URL更新

#### 📋 前置条件
- Salary 面板已打开

#### 🎬 执行步骤
1. 点击 `Per Month`（`page.getByText('Per Month', { exact: true }).click()`）
2. 在 Min 输入框（`page.getByPlaceholder('Min')`）输入 `1000`
3. 在 Max 输入框（`page.getByPlaceholder('Max')`）输入 `5000`
4. 点击 `Confirm` 按钮

#### ✅ 预期结果
1. 面板关闭
2. URL 变为 **`?iconSource=jobs&lowestPrice=1000&highestPrice=5000&attr_80=4`**
   - `lowestPrice=1000`：最低薪资
   - `highestPrice=5000`：最高薪资
   - `attr_80=4`：Per Month 对应值
3. 筛选栏显示 **"Salary · 1"**（整个 Salary 筛选作为 1 个筛选项计数）
4. 职位列表刷新为符合薪资范围的职位
5. 触发 `filterSubmit` 和 `filter_item_salary_min_in`、`filter_item_salary_max_in`、`filter_item_salary_unit_c` 分析事件

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC030: Salary筛选-只输入Min不输入Max-正常筛选

#### 📋 前置条件
- Salary 面板已打开

#### 🎬 执行步骤
1. 点击 `Per Month`
2. 在 Min 输入框输入 `3000`，Max 输入框留空
3. 点击 `Confirm`

#### ✅ 预期结果
1. 面板关闭
2. URL 变为 **`?iconSource=jobs&lowestPrice=3000&attr_80=4`**（**仅含** `lowestPrice`，无 `highestPrice`）
3. 筛选栏显示 **"Salary · 1"**
4. 职位列表过滤为薪资 ≥ 3000/月的职位

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界测试
- **UI自动化**: ✅ 可自动化

---

### TC031: Salary筛选-只输入Max不输入Min-正常筛选

#### 📋 前置条件
- Salary 面板已打开

#### 🎬 执行步骤
1. 点击 `Per Month`
2. Max 输入框输入 `5000`，Min 输入框留空
3. 点击 `Confirm`

#### ✅ 预期结果
1. 面板关闭
2. URL 变为 **`?iconSource=jobs&highestPrice=5000&attr_80=4`**（**仅含** `highestPrice`，无 `lowestPrice`）
3. 筛选栏显示 **"Salary · 1"**
4. 职位列表过滤为薪资 ≤ 5000/月的职位

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界测试
- **UI自动化**: ✅ 可自动化

---

### TC032: Salary筛选-Min大于Max-提交被静默忽略面板关闭

#### 📋 前置条件
- Salary 面板已打开

#### 🎬 执行步骤
1. 点击 `Per Month`
2. Min 输入 `8000`，Max 输入 `3000`（小于 Min）
3. 点击 `Confirm`

#### ✅ 预期结果
1. 面板**直接关闭**（非阻止提交）
2. URL 变为 **`?iconSource=jobs`**（**未附加任何薪资参数**，提交被静默忽略）
3. 筛选栏 Salary **无数字徽章**（恢复为 "Salary"）
4. **无内联错误提示文案**（与原预期不符，实际行为是静默清空）

> ⚠️ **实测与原预期不符**：实际行为是静默忽略提交并清空薪资筛选，而非显示错误提示。建议后续 Bug 复查。

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界测试
- **UI自动化**: ✅ 可自动化

---

### TC033: Salary筛选-输入负数-负号被自动过滤输入框清空

#### 📋 前置条件
- 已打开 Salary 设置面板

#### 🎬 执行步骤
1. 在 Min 输入框输入 `-5000`（负数）

#### ✅ 预期结果
1. 输入框实际值为空字符串（负号被自动过滤，不允许输入负值）
2. 不显示错误提示（输入时直接阻止，非提交时校验）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界测试
- **UI自动化**: ✅ 可自动化

---

### TC034: Salary筛选-输入小数-是否允许

#### 📋 前置条件
- 已打开 Salary 设置面板

#### 🎬 执行步骤
1. 在 Min 输入框输入 `1000.5`，Max 输入 `5000.99`
2. 点击 Confirm

#### ✅ 预期结果
1. 输入框接受小数（Min 显示为 `1,000.5`，Max 显示为 `5000.99`，自动加千分位）
2. URL 追加 `lowestPrice=1000.5&highestPrice=5000.99`（小数值原样传递）
3. 面板关闭，筛选执行

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界测试
- **UI自动化**: ✅ 可自动化

---

### TC035: Salary筛选-选择不同薪资周期-周期选项可切换

#### 📋 前置条件
- 已打开 Salary 设置面板（点击 Salary 筛选器）

#### 🎬 执行步骤
1. 依次点击 Per Hour、Per Day、Per Week、Per Month、Per Biweek、Per Year，每次点击后 Confirm

#### ✅ 预期结果
1. 每次点击后对应选项显示选中态，**只能单选**
2. 各周期对应的 `attr_80` 参数值（实测确认）：
   - Per Hour → **无 `attr_80` 参数**（默认，URL 仅为 `?iconSource=jobs`）
   - Per Day → `attr_80=2`
   - Per Week → `attr_80=3`
   - Per Month → `attr_80=4`
   - Per Biweek → `attr_80=5`
   - Per Year → `attr_80=6`
3. Confirm 后面板关闭，URL 追加对应 `attr_80` 参数，筛选栏显示 "Salary · 1"

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC036: Salary筛选-Clear按钮清除已填数据

#### 📋 前置条件
- 已填写 Min/Max 并选择周期

#### 🎬 执行步骤
1. 输入 Min = "10000"，Max = "30000"
2. 点击 Clear 按钮（ref=e842）

#### ✅ 预期结果
1. Min 和 Max 输入框均清空（值变为空字符串）
2. 面板**保持打开**（不关闭）
3. URL **不变**（Clear 只清空面板内输入，不提交）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

## 岗位偏好类别切换

### TC037: 默认显示岗位偏好类别标签栏

#### 📋 前置条件
- 已登录（有岗位偏好设置）的账号访问 Jobs 列表页

#### 🎬 执行步骤
1. 观察页面筛选栏上方的偏好类别标签区域（`generic[ref=e37]`）

#### ✅ 预期结果
1. 显示横向滚动的岗位偏好类别标签：
   - `Accounts Officers/Clerks`（`generic[ref=e38]`）
   - `Accounts Payable`（`generic[ref=e39]`）
   - `Accounts Receivable/Credit Control`（`generic[ref=e40]`）
   - `Collections`（`generic[ref=e41]`）
   - `Analysis & Reporting`（`generic[ref=e42]`）
2. 标签末尾有 `link "Edit"`（`link[ref=e43]`）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC038: 点击偏好类别标签-切换显示对应类别的职位

#### 📋 前置条件
- 岗位偏好类别标签栏已显示（Jobs 列表页已加载）

#### 🎬 执行步骤
1. 点击 `Accounts Payable` 标签（快照 `generic[ref=e39]`，点击最小元素 `Accounts Payable`）

#### ✅ 预期结果
1. URL 追加 `preferenceCateId=3003`：`?iconSource=jobs&preferenceCateId=3003`
2. 职位列表刷新，显示 Accounts Payable 类别的职位
3. `Accounts Payable` 标签呈选中高亮状态

> **注意**：不同偏好类别对应不同的 `preferenceCateId` 值（如 Accounts Payable = 3003）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC039: 点击Edit链接-跳转至岗位偏好设置页

#### 📋 前置条件
- 岗位偏好类别标签栏已显示

#### 🎬 执行步骤
1. 点击标签栏末尾的 `link "Edit"`（`link[ref=e43]`，`page.getByRole('link', { name: 'Edit' })`）

#### ✅ 预期结果
- 跳转至岗位偏好编辑页面（Job Preferences 页）

> **注意**：Edit link 的 href 为空（JavaScript 动态处理），需用 `page.waitForNavigation()` 或 `page.waitForURL()` 等待跳转完成验证新 URL。

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC040: 岗位偏好类别标签栏-切换不同类别筛选条件独立

#### 📋 前置条件
- 已选择 Job Type = Full-time 筛选（URL: `?iconSource=jobs&attr_60=1`）
- 偏好类别标签栏已显示

#### 🎬 执行步骤
1. 点击 `Accounts Payable` 偏好类别标签

#### ✅ 预期结果
1. URL 追加 `preferenceCateId=3003`：`?iconSource=jobs&attr_60=1&preferenceCateId=3003`
2. `attr_60=1`（Job Type=Full-time）**保留不清除**（实测确认）
3. 职位列表刷新，同时满足 Full-time 和 Accounts Payable 两个条件

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC041: 未登录用户访问Jobs列表-不显示岗位偏好类别栏

#### 📋 前置条件
- 未登录状态访问 `https://ae.58v5.cn/en/city/cate-jobs/?iconSource=jobs`

#### 🎬 执行步骤
1. 以未登录状态访问 Jobs 列表页
2. 观察页面头部结构

#### ✅ 预期结果
- 不显示岗位偏好类别标签栏（因无登录态无偏好数据）
- 其他筛选功能正常显示

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 权限测试
- **UI自动化**: ✅ 可自动化

---

## Reset 重置功能

### TC042: 无筛选条件时Reset按钮存在但点击无效果

#### 📋 前置条件
- Jobs 列表页，未设置任何筛选

#### 🎬 执行步骤
1. 观察 Reset 按钮状态（ref=e61）
2. 点击 `Reset`（`page.getByText('Reset').click()`）

#### ✅ 预期结果
1. Reset 按钮始终显示（无论是否有筛选条件）
2. 无筛选时点击不报错，URL 保持不变（仍为 `?iconSource=jobs`）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC043: 设置Job Type筛选后点击Reset-清除查询参数筛选

#### 📋 前置条件
- 已设置 Job Type = Full-time（URL: `?iconSource=jobs&attr_60=1`）

#### 🎬 执行步骤
1. 点击筛选栏 `Reset`（`page.locator('#istPageFilterArea').getByText('Reset').click()`）

#### ✅ 预期结果
1. URL 中移除 `attr_60=1` 等查询参数，恢复为 **`?iconSource=jobs`**
2. 筛选栏：Job Type、Workplace type、Salary 的数字徽章全部消失
3. 筛选栏文案恢复为 **"Location Job Type Workplace type Salary Reset"**（无任何徽章）
4. 职位列表恢复显示全部职位

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC044: 设置多个筛选条件后Reset-仅清除查询参数（不清除城市路径）

#### 📋 前置条件
- 已通过 Location 选择 Dubai 城市（URL路径：`/en/city-dubai/cate-jobs/`），并设置 Job Type=Full-time

#### 🎬 执行步骤
1. 点击 `Reset`

#### ✅ 预期结果
1. URL 的**查询参数部分**被清除（`attr_60` 等参数消失），但**城市路径保留**
2. 结果 URL：**`/en/city-dubai/cate-jobs/?iconSource=jobs`**（Dubai 城市路径不变）
3. 筛选栏 Job Type/Workplace type/Salary 徽章均消失
4. **Location 筛选仍显示 "Dubai"**（因为城市在URL路径中，未被 Reset 清除）

> ⚠️ **重要行为**：Reset 只清除查询参数中的筛选条件（`attr_60`/`attr_61`/`attr_80`/`lowestPrice`/`highestPrice`），不清除 URL 路径中的城市段（`/city-dubai/`）。若要清除城市筛选，需要在 Location 面板选择 "All United Arab Emirates"。

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC045: 搜索中间页-无Reset按钮（与列表页筛选栏结构不同）

#### 📋 前置条件
- 在搜索中间页（URL 含 `keyword=manager`），且已设置 Job Type=Full-time

#### 🎬 执行步骤
1. 直接访问 `?keyword=manager&attr_60=1`
2. 查看筛选栏，检查是否有 Reset 按钮

#### ✅ 预期结果
1. **搜索中间页筛选栏没有 Reset 按钮**（与列表页不同）
2. 筛选栏文本：`Best Match Filter·2 Jobs Location Salary Job Type·1 Workplace type Unit`
3. 若需清除筛选，须手动点击各筛选器内的 Clear 按钮

> ⚠️ **重要差异**：搜索中间页（`?keyword=*`）的筛选栏与列表页（`?iconSource=jobs`）完全不同，**没有 Reset**，且显示 `Best Match`、`Filter·N`、`Jobs` 等额外选项。这是 TC045 的核心行为差异（原文档预期有误）。

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试（差异探索）
- **UI自动化**: ✅ 可自动化

---

## 翻页功能

### TC046: Jobs列表页-滚动到底部加载更多职位（无限滚动）

#### 📋 前置条件
- Jobs 列表页已加载（`/en/city/cate-jobs/?iconSource=jobs`）

#### 🎬 执行步骤
1. 记录初始 `document.body.scrollHeight`（实测约 7924px）
2. 执行 `window.scrollTo(0, document.body.scrollHeight)` 滚动到底部
3. 等待约 2 秒，再次记录 scrollHeight

#### ✅ 预期结果
1. 滚动后 `scrollHeight` 增大（实测：7924 → 9661，增加约 1737px）
2. 新的职位卡片追加到列表末尾
3. URL **不发生变化**（仍为 `?iconSource=jobs`，无 `page=` 参数）
4. 筛选器状态保持不变

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC047: 滚动到底部-显示已加载全部提示

#### 📋 前置条件
- 已设置能产生有限结果的筛选（如特定 Job Type）

#### 🎬 执行步骤
1. 持续滚动到列表最底部，重复多次

#### ✅ 预期结果
1. 某次滚动后卡片数不再增加
2. 显示 `You've reached the end` 文案
3. URL 无变化

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC048: 搜索结果页-翻页机制与列表页一致

#### 📋 前置条件
- 已在搜索结果页（中间页）

#### 🎬 执行步骤
1. 向下滚动页面

#### ✅ 预期结果
1. 搜索结果支持无限滚动加载更多（与列表页一致）
2. URL 不追加 `page=` 等分页参数（无传统分页按钮）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC049: 筛选后列表-滚动加载结果仍符合筛选条件

#### 📋 前置条件
- 已设置 Job Type = Full-time 筛选

#### 🎬 执行步骤
1. 向下滚动，触发加载更多
2. 观察新加载的职位标签

#### ✅ 预期结果
- 新加载的职位均为 Full-time 类型，不出现其他类型

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

## 筛选组合与联动

### TC050: 同时设置Location和Job Type-两个筛选共同生效

#### 📋 前置条件
- Jobs 列表页已加载

#### 🎬 执行步骤
1. 直接访问 Dubai 城市页：`https://ae.58v5.cn/en/city-dubai/cate-jobs/?iconSource=jobs`
2. 点击 Job Type 筛选器，点 Clear，选 Full-time，点 Confirm

#### ✅ 预期结果
1. 职位列表显示 Dubai + Full-time 的职位
2. URL：`https://ae.58v5.cn/en/city-dubai/cate-jobs/?iconSource=jobs&attr_60=1`
3. URL 同时包含城市路径段 `city-dubai` 和 Job Type 参数 `attr_60=1`
4. 筛选栏显示 "Job Type · 1"

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC051: 同时设置Job Type和Workplace type-两个筛选共同生效

#### 📋 前置条件
- Jobs 列表页已加载（`/en/city/cate-jobs/?iconSource=jobs`）

#### 🎬 执行步骤
1. 点击 Job Type 筛选器，Clear，选 Full-time，Confirm
2. 点击 Workplace type 筛选器，Clear，选 Remote，Confirm

#### ✅ 预期结果
1. URL：`https://ae.58v5.cn/en/city/cate-jobs/?iconSource=jobs&attr_60=1&attr_61=2`
2. 筛选栏显示 "Job Type · 1" 和 "Workplace type · 1"（文本内容：`LocationJob Type·1Workplace type·1SalaryReset`）
3. 职位列表同时满足 Full-time + Remote 两个条件

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC052: 同时设置Job Type和Salary范围-两个筛选共同生效

#### 📋 前置条件
- Jobs 列表页已加载（`/en/city/cate-jobs/?iconSource=jobs`）

#### 🎬 执行步骤
1. 点击 Job Type 筛选器，Clear，选 Full-time，Confirm
2. 点击 Salary 筛选器，选 Per Month，填 Min=3000，Max=10000，Confirm

#### ✅ 预期结果
1. URL：`https://ae.58v5.cn/en/city/cate-jobs/?iconSource=jobs&attr_60=1&lowestPrice=3000&highestPrice=10000&attr_80=4`
2. 筛选栏显示 "Job Type · 1" 和 "Salary · 1"
3. 职位列表显示 Full-time 且月薪 3000-10000 的职位

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC053: 搜索关键词后在中间页再叠加Job Type筛选-两者共同生效

#### 📋 前置条件
- 已在搜索中间页（`?keyword=manager`）

#### 🎬 执行步骤
1. 在搜索框输入 `manager` 并点击 Search，URL 变为 `?keyword=manager`
2. 点击 Job Type 筛选器，Clear，选 Full-time，Confirm

#### ✅ 预期结果
1. URL：`https://ae.58v5.cn/en/city/cate-jobs/?keyword=manager&attr_60=1`（`keyword` 保留）
2. 筛选栏显示 "Job Type · 1"（文本：`Best MatchFilter·2JobsLocationSalaryJob Type·1Workplace typeUnit`）
3. 职位列表同时满足搜索和筛选条件

> **注意**：搜索结果中间页的筛选栏与纯列表页不同，显示 `Best Match`/`Filter·2`/`Jobs` 等额外选项。

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC054: 筛选后切换岗位偏好类别-筛选参数是否保留

#### 📋 前置条件
- 已设置 Job Type = Full-time
- 偏好类别标签栏可见

#### 🎬 执行步骤
1. 点击另一个偏好类别标签

#### ✅ 预期结果
1. URL 中 `preferenceCateId` 更新为新类别的 ID
2. 其他筛选参数（如 Job Type 的 `attr_60`）**保留**，不被清除（MCP实测：切换类别后 `attr_60=1` 仍存在于 URL）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC055: 多筛选组合后Reset-清除查询参数（城市路径保留）

#### 📋 前置条件
- 已在 Dubai 城市页，并设置 Job Type=Full-time、Workplace type=Onsite、Salary=Per Month Min1000 Max5000
- Reset 前 URL：`/en/city-dubai/cate-jobs/?iconSource=jobs&attr_60=1&attr_61=1&lowestPrice=1000&highestPrice=5000&attr_80=4`

#### 🎬 执行步骤
1. 点击 Reset

#### ✅ 预期结果
1. URL 变为：`https://ae.58v5.cn/en/city-dubai/cate-jobs/?iconSource=jobs`（查询参数全部清除，**Dubai 路径保留**）
2. 筛选栏 Job Type/Workplace type/Salary 徽章全部消失
3. **Location 仍显示 "Dubai"**（因城市路径未被清除）
4. 筛选栏文本：`DubaiJob TypeWorkplace typeSalaryReset`

> ⚠️ **与TC055预期的差异**：Reset 无法清除 URL 路径中的城市（`/city-dubai/`），只清除查询参数中的筛选器。

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC056: 职位卡片右侧详情面板-默认展开第一条

#### 📋 前置条件
- Jobs 列表页已加载（`/en/city/cate-jobs/?iconSource=jobs`）

#### 🎬 执行步骤
1. 不点击任何职位，观察页面右侧详情面板

#### ✅ 预期结果
1. 右侧详情面板（`generic[ref=e779]`）**默认展开第一条职位详情**
2. 面板内容包含：
   - 职位名称（如 "Teacher Trainer"）
   - 薪资（如 "AED 1,000-5,000/month"）
   - 公司名称（如 "CCC"）
   - 工作类型标签（Full-time / Onsite / No experience limit / No degree limit）
3. 面板底部按钮行：`Contact`（`button[ref=e799]`）、`Favourites`（`generic[ref=e801]`）、`New tab`（`link[ref=e802]`）、`Share`（`generic[ref=e806]`）
4. 面板底部有 `Resume` 入口（`generic[ref=e831]`）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC057: 点击职位卡片-右侧详情面板切换显示对应职位

#### 📋 前置条件
- Jobs 列表页已加载，右侧面板默认显示第一条职位详情（如 "Teacher Trainer"）

#### 🎬 执行步骤
1. 点击列表中第二条职位卡片（如 "M70848"，位于 `generic[ref=e91]`）

#### ✅ 预期结果
1. 右侧详情面板切换，显示第二条职位的详情（职位名称、薪资、公司名称、描述等）
2. URL **不发生变化**（仍为 `?iconSource=jobs`，详情面板是前端路由切换）
3. 第二条卡片在列表中呈高亮选中状态
4. Contact / Favourites / New tab / Share 按钮在新面板中同样可见

> **Locator 参考**：
> - 第二条卡片（实测第一页第二条）：`page.locator('generic[ref=e91]').click()` 或 `page.locator('[data-index="1"]').click()`

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC058: Popular Cities标签-点击跳转对应城市Jobs页

#### 📋 前置条件
- Jobs 列表页已加载，页面底部 Popular Cities 标签栏可见

#### 🎬 执行步骤
1. 页面向下滚动，找到底部 Popular Cities 选项卡
2. 点击 `link "Abu Dhabi Jobs"`（`link[ref=e839]`，href=`/en/city-abu-dhabi/cate-jobs/`）

#### ✅ 预期结果
- 跳转至 Abu Dhabi 的 Jobs 列表页：`https://ae.58v5.cn/en/city-abu-dhabi/cate-jobs/`

> **Popular Cities 列表（实测）**：
> - `Dubai Jobs` → `/en/city-dubai/cate-jobs/`（`link[ref=e838]`）
> - `Abu Dhabi Jobs` → `/en/city-abu-dhabi/cate-jobs/`（`link[ref=e839]`）
> - `Sharjah Jobs` → `/en/city-sharjah/cate-jobs/`（`link[ref=e840]`）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC059: 职位详情面板-Contact按钮可点击

#### 📋 前置条件
- Jobs 列表页已加载，右侧职位详情面板已展开某职位（已登录）

#### 🎬 执行步骤
1. 点击右侧面板中的 `Contact` 按钮（`button[ref=e799]`，`getByRole('button', { name: 'Contact' }).first()`）

#### ✅ 预期结果
1. 页面跳转到聊天页：`https://aepub.58v5.cn/biz/en/chat?postId=...&shopId=...&cateCode=jobs`（携带职位 ID、公司 ID 等参数），**不是弹窗**
2. 聊天页标题显示 `Messages`，展示与该招聘方的对话窗口

> **验证**：Contact 按钮 `isVisible = true`（已实测）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC060: 职位详情面板-New tab链接在新标签页打开职位

#### 📋 前置条件
- Jobs 列表页已加载，右侧职位详情面板已展开某职位

#### 🎬 执行步骤
1. 点击右侧面板中的 `New tab` 链接（`link[ref=e802]`，`getByRole('link', { name: 'New tab' })`）

#### ✅ 预期结果
1. 在新标签页打开该职位详情页（URL 为该职位的详情页地址）
2. 原列表页标签不关闭，保持当前筛选状态

> **注意**：New tab 链接的 href 为空字符串（`""`），是 JavaScript 动态处理的，不能用 `href` 验证，需监听新标签页打开事件（`page.waitForEvent('popup')`）来验证跳转。

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC061: 职位详情面板-Favourites收藏功能

#### 📋 前置条件
- 已登录，右侧职位详情面板已展开某职位

#### 🎬 执行步骤
1. 点击 `Favourites` 按钮（ref=e801）

#### ✅ 预期结果
- 职位被收藏，Favourites 按钮状态切换（如变为已收藏态）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC062: 筛选区域右侧面板-Resume入口显示

#### 📋 前置条件
- Jobs 列表页已加载（`/en/city/cate-jobs/?iconSource=jobs`）

#### 🎬 执行步骤
1. 观察右侧职位详情面板底部

#### ✅ 预期结果
1. 右侧面板底部显示 `Resume` 入口（`generic[ref=e831]`，cursor=pointer）
2. 点击后跳转至简历相关页面

> **Locator**：`page.locator('text=Resume').last()` 或 `page.locator('[class*="DetailPanel"]').getByText('Resume')`

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC063: 页面加载性能-Jobs列表页首屏加载时间合理

#### 📋 前置条件
- 已登录账号

#### 🎬 执行步骤
1. 导航至 `https://ae.58v5.cn/en/city/cate-jobs/?iconSource=jobs`，等待 `networkidle`
2. 通过 Navigation Timing API 获取加载耗时：
   ```python
   timing = page.evaluate("() => JSON.parse(JSON.stringify(window.performance.timing))")
   load_time = timing['loadEventEnd'] - timing['navigationStart']
   ```

#### ✅ 预期结果
- `loadEventEnd - navigationStart` < 5000ms（5 秒内）
- 页面可见职位列表，无明显白屏

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 性能测试
- **UI自动化**: ✅ 可自动化

---

## 测试统计

### 用例概览
- 总用例数: 65条
- 可自动化: 64条 (98%)
- 不可自动化: 1条 (2%)
  - TC015：Use current location（浏览器定位权限弹窗，依赖真实 GPS，自动化不稳定）

### 按优先级分布

| 优先级 | 总数 | 可自动化 | 自动化率 |
|--------|------|---------|---------|
| P0 | 18 | 18 | 100% |
| P1 | 28 | 28 | 100% |
| P2 | 19 | 18 | 95% |

### 按模块分布

| 模块 | 用例数 |
|------|------|
| 搜索框功能 | 7 |
| 搜索中间页 | 5 |
| Location 地址筛选 | 6 |
| Job Type 工作类型筛选 | 6 |
| Workplace Type 工作方式筛选 | 5 |
| Salary 薪资筛选 | 9 |
| 岗位偏好类别切换 | 5 |
| Reset 重置功能 | 4 |
| 翻页功能 | 4 |
| 筛选组合与联动 | 14 |

---

## MCP 录制关键选择器汇总

| 元素 | MCP 录制选择器 | 说明 |
|------|-------------|------|
| 搜索框 | `page.getByRole('textbox', { name: 'Search for anything' })` | 顶部搜索输入框 |
| Search按钮 | `page.getByRole('button', { name: 'Search' })` | 搜索触发按钮 |
| Location筛选器 | `page.getByText('Location')` | 地址筛选入口 |
| Dubai城市选项 | `page.locator('div:nth-child(2) > .CascadingSelector_itemContent__RM88u > div')` | Location弹窗中的Dubai |
| Search City输入框 | `page.getByRole('textbox', { name: 'Search City' })` | 城市搜索框 |
| Use current location按钮 | `page.getByRole('button', { name: 'Use current location' })` | 使用当前位置 |
| Job Type筛选器 | `page.getByText('Job Type')` | 工作类型筛选入口 |
| Full-time选项 | `page.locator('.Selector_optionItem__er6y4').first()` | Job Type的Full-time |
| Confirm按钮 | `page.getByRole('button', { name: 'Confirm' })` | 筛选面板确认按钮 |
| Clear按钮 | `page.getByRole('button', { name: 'Clear' })` | 筛选面板清除按钮 |
| Workplace type筛选器 | `page.getByText('Workplace type')` | 工作方式筛选入口 |
| Onsite选项 | ref=e812 | Workplace type的Onsite |
| Salary筛选器 | `page.getByText('Salary', { exact: true })` | 薪资筛选入口 |
| Min输入框 | `page.getByRole('textbox', { name: 'Min' })` | 最低薪资输入框 |
| Max输入框 | `page.getByRole('textbox', { name: 'Max' })` | 最高薪资输入框 |
| Reset按钮 | `page.getByText('Reset')` | 重置所有筛选 |
| 偏好类别Edit | `page.getByRole('link', { name: 'Edit' })` | 编辑岗位偏好 |
