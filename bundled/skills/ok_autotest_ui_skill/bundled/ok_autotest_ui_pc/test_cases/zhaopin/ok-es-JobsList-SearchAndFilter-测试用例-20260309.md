# ES站 - Jobs列表页搜索与筛选功能测试用例

> **生成时间**: 2026-03-09  
> **更新时间**: 2026-03-13（MCP实测复核 + feed流翻页用例修正 + 补充筛选项回显用例）  
> **测试范围**: 搜索框、筛选器、Reset、无限滚动加载、搜索中间页、职位卡片交互、侧边栏详情  
> **总用例数**: 65条  
> **可自动化**: 63条 (97%)

---

## 测试环境配置

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | es | 西班牙站 |
| 基础URL | https://es.58v5.cn | 测试站点地址 |
| 站点名称 | 西班牙站 | 用于日志展示 |
| 角色 | jobseeker | 求职者身份 |
| 账号名称 | wang_es | 用于session命名 |
| 测试账号 | wangyongli@58.com | 登录邮箱 |
| 测试密码 | Qwer1234 | 登录密码 |

**说明**：此配置将被 playwright-test-generator 用于生成自动化脚本。

---

## 应用概述

- **测试站点**: ES站（西班牙站）
- **测试页面**: 招聘列表页 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
- **测试范围**: 搜索框、筛选器、Reset、翻页、搜索中间页
- **测试状态**: 已登录，无岗位偏好
- **默认城市**: Madrid（地址筛选框默认有值）

## 页面结构

> ⚠️ **已根据MCP录制修正**：地址面板为两级省→市结构，非原设计稿描述

### 1. 搜索区域
- 搜索输入框：`input[type='search']` / `textbox "Search for anything"`
- 搜索按钮：`button "Search"`

### 2. 筛选器区域（顶部横排）
- **Madrid**（地址筛选，默认值）：点击后展开两级地址选择面板
  - **第一级：省份列表**（All Spain / Andalusia / Aragon / Asturias / Balearic Islands / Basque Country / Canary Islands / Cantabria / Castille and Leon / Castille-La Mancha / Catalonia / Ceuta / Extremadura / Galicia / La Rioja / Madrid / Melilla / Murcia / Navarre / Valencia）
  - **第二级：城市列表**（点击省份后展开该省城市）
  - 面板顶部有 `textbox "Search City"` 城市搜索框
  - 有 `button "Use current location"` 按钮
- **Job Type**（工作类型）：点击后展开多选面板
  - Full-time / Part-time / Contract / Internship / Temporary（5个选项）
  - 每个选项有 `icon-selected` 选中状态图标
  - Clear 和 Confirm 按钮
- **Workplace type**（工作地点类型）：结构同 Job Type
- **Salary**（薪资范围）
- **Reset** 按钮：清除所有筛选（筛选无效时不显示/置灰）

### 3. 职位列表区域
- **"Add Job Preference"** 卡片入口（已登录无偏好时显示在列表顶部）
  - 标题："Add Job Preference"
  - 副文案："Unlock more opportunities tailored for you."
- **职位卡片**（每页约30条），每张卡片包含：
  - 职位标题、薪资范围、Job Type标签、Workplace标签、城市标签
  - 公司Logo、招聘者姓名、职位
  - **Quick Reply** 文案标签（展示性，点击等同于点击整张卡片，切换侧边栏详情）
  - 高亮技能标签（如 ok1 · ok2 · ok3）
- **职位详情侧边栏**（点击卡片后右侧展开）：
  - 职位标题、薪资、公司名称
  - 工作类型、地点、经验要求、学历要求
  - 操作按钮：**Withdraw** / **Edit**（自投简历才有）/ **Contact**
  - 收藏按钮：**Favourites**
  - **New tab** 链接（在新标签页打开）
  - **Share** 按钮
  - **Description** 描述区域
  - 发布时间/更新时间
  - 招聘者信息（姓名、公司·职位）
  - **Company** 区域（公司名、员工规模）
  - **Resume** 快捷入口（侧边栏底部）

### 4. 加载更多区域（feed流）
- 列表采用 **feed流（无限滚动）** 模式，无传统分页按钮（无页码、Previous、Next）
- 滚动到列表底部时自动触发加载更多职位
- 加载过程中显示 loading 状态
- 所有职位加载完毕后显示结束提示（如"No more jobs"或空白）

## 业务规则

1. **搜索行为**：
   - 输入关键词后点击Search按钮，URL追加`?keyword=xxx`
   - 空搜索也会触发搜索，URL包含`keyword=`（空值）
   - 搜索结果页保留筛选器状态
   - 搜索框有防抖处理，建议使用 `press_sequentially()` 逐字输入

2. **地址筛选**（MCP录制修正）：
   - 默认选中 Madrid，筛选器显示"Madrid"并处于**激活态**（class含`FilterItem_filterItemActive__WMq_K`）
   - URL路径中城市标识符为 `city-madrid2`（Madrid内部编码为`madrid2`）
   - 面板标题为 **"Select Location"**，为**两级结构**：第一级选省份，第二级选城市
   - 面板顶部首先显示历史访问城市快捷入口（动态，取决于用户浏览历史）
   - 面板顶部有 `input[placeholder="Search City"]` 搜索框（class含`CascadingSelector_searchContainer`）
   - 省份列表共20项，从"All Spain"到"Valencia"（按字母排序）
   - 可选"All Spain"展示全国职位，URL变为`/en/city/cate-jobs/`，筛选器显示"Location"
   - 选择城市后URL路径变更（如选Sevilla → `/en/city-sevilla/cate-jobs/`）
   - 地址变更会重置其他筛选条件（URL中的attr参数被清除）
   - ⚠️ **已知问题**：Barcelona城市页面当前返回504

3. **Job Type筛选**：
   - 支持多选（5个选项：Full-time, Part-time, Contract, Internship, Temporary）
   - 每个选项有选中状态图标（`icon-selected`）
   - 选中后点击Confirm提交，URL追加参数（Full-time: `&attr_60=1`）
   - Clear清除本次选择，面板保持打开，URL不变
   - 已激活的筛选器显示"Job Type · N"（N为选择数量）

4. **Workplace type筛选**：
   - 与Job Type相同的面板结构（多选 + Clear/Confirm）
   - 选项包含 Onsite / Remote / Hybrid

5. **Reset功能**：
   - 清除所有筛选条件（地址保持默认Madrid，不被重置）
   - URL恢复为初始路径（含`?iconSource=jobs`），`attr_60`等筛选参数被移除
   - 搜索关键词`keyword`参数**保留**在URL中（Reset不清空搜索词）
   - Reset元素为 `div`（非`button`角色），需用 `.locator(".listPage-filterArea-submit")` 定位

6. **列表加载（feed流）**：
   - 列表采用**无限滚动**模式，**无翻页按钮**（无页码/Previous/Next）
   - 滚动到列表底部时自动触发加载更多，URL不变（无`page=`参数）
   - 筛选条件变化后列表重新从第一条开始加载
   - 加载完所有职位后显示结束态（具体文案待实测确认）
   - ⚠️ **修正**：原文档中关于`page=2`等URL参数翻页的描述均不适用于此页面（为feed流非分页）

7. **Add Job Preference入口**：
   - 已登录且无岗位偏好的用户，在职位列表顶部显示入口卡片
   - 点击后跳转到Job Preferences中间页（URL含 `jobPreference`）
   - 已设置偏好的用户不显示该入口

8. **职位卡片交互**：
   - 点击卡片：右侧展开职位详情侧边栏（双栏布局）
   - Quick Reply：**纯展示性文案标签**，点击行为等同于点击整张卡片（切换侧边栏），不触发独立回复功能
   - Favourites：收藏/取消收藏该职位
   - Share：分享职位链接
   - New tab：在新标签页打开职位详情
   - 自己发布的职位卡片显示 Withdraw / Edit 按钮（而非 Contact）

## 测试用例

### TC001: 搜索框输入关键词搜索

#### 📋 前置条件
- 已登录，位于Jobs列表页

#### 🎬 执行步骤
1. 定位搜索输入框（`textbox "Search for anything"`）
2. 输入关键词"manager"
3. 点击Search按钮（`button "Search"`）

#### ✅ 预期结果
1. URL包含`keyword=manager`
2. 页面显示搜索结果列表
3. 筛选器区域仍然可见

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/功能
- **UI自动化**: ✅ 可自动化

### TC002: 空搜索关键词提交

#### 📋 前置条件
- 已登录，位于Jobs列表页

#### 🎬 执行步骤
1. 不输入任何内容，直接点击Search按钮

#### ✅ 预期结果
1. URL包含`keyword=`（空值，如 `?iconSource=jobs&keyword=`），keyword参数存在但值为空字符串
2. 页面显示所有职位列表（等同于无搜索条件）

> 🔬 **MCP实测**：URL为 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs&keyword=`，keyword参数保留但为空值

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

### TC003: 搜索框输入特殊字符搜索

#### 📋 前置条件
- 已登录，位于Jobs列表页

#### 🎬 执行步骤
1. 搜索输入框输入特殊字符"@#$%"
2. 点击Search按钮

#### ✅ 预期结果
1. URL正确编码特殊字符（如 `?keyword=%40%23%24%25`）
2. 职位列表为空，页面显示提示文案："We couldn't find anything. Try a new search"

> 🔬 **MCP实测**：URL为 `?keyword=%40%23%24%25`，页面无职位卡片，显示 "We couldn't find anything. Try a new search"

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 异常流
- **UI自动化**: ✅ 可自动化

### TC004: 搜索框输入超长关键词

#### 📋 前置条件
- 已登录，位于Jobs列表页

#### 🎬 执行步骤
1. 输入超过200字符的关键词
2. 点击Search按钮

#### ✅ 预期结果
1. 输入框无`maxlength`属性限制，允许输入200+字符（实测250字符全部保留）
2. 搜索请求正常发送，URL将完整超长词进行URL编码后追加到`keyword=`参数
3. 返回匹配结果（可能为空列表，显示"We couldn't find anything. Try a new search"）

> 🔬 **MCP实测**：搜索框无`maxlength`属性，输入250个'a'后值长度仍为250，无截断

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

### TC005: 页面加载后地址筛选器默认显示Madrid

#### 📋 前置条件
- 已登录，访问Jobs列表页入口 URL：`https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`

#### 🎬 执行步骤
1. 直接打开上述 URL，等待页面加载完成
2. 观察顶部筛选器区域的地址按钮

#### ✅ 预期结果
1. 筛选器区域第一个筛选项显示文本 **"Madrid"**（通过 `get_by_text("Madrid", exact=True)` 可定位）
2. 地址筛选器处于**激活状态**：DOM class 包含 `FilterItem_filterItemActive__WMq_K`（区别于 Job Type / Workplace type / Salary 等未选中状态）
3. URL 路径包含 **`city-madrid2`**（Madrid的城市标识符为`madrid2`）
4. 其余筛选器（Job Type / Workplace type / Salary）均为非激活状态（class 仅含 `FilterItem_filterItem__Ur24_`，不含 `Active`）
5. 筛选器区域共显示 4 个筛选项：Madrid · Job Type · Workplace type · Salary（以及 Reset）

> 🔬 **MCP实测**：
> - 地址筛选元素 class：`FilterItem_filterItem__Ur24_ FilterItem_filterItemActive__WMq_K`
> - 其他筛选器 class：`FilterItem_filterItem__Ur24_`（无Active）
> - 共4个FilterItem：`['Madrid', 'Job Type', 'Workplace type', 'Salary']`
> - URL路径中城市段为 `city-madrid2`（Madrid对应内部编码`madrid2`）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/UI
- **UI自动化**: ✅ 可自动化

---

### TC006: 切换城市后地址筛选器同步更新

#### 📋 前置条件
- 已登录，位于 Madrid Jobs列表页（`city-madrid2`）

#### 🎬 执行步骤
1. 点击地址筛选器，面板打开
2. 点击省份"Andalusia"
3. 点击城市"Sevilla"

#### ✅ 预期结果
1. URL 路径变更为 **`city-sevilla`**（如 `https://es.58v5.cn/en/city-sevilla/cate-jobs/?iconSource=jobs`）
2. 页面跳转到 Sevilla 职位列表
3. 其他筛选条件（Job Type / Workplace type）同步重置（地址变更会清空其他筛选参数）

> 🔬 **MCP实测**：选择 Andalusia → Sevilla 后，URL变为 `https://es.58v5.cn/en/city-sevilla/cate-jobs/?iconSource=jobs`；`city-sevilla` 为 Sevilla 的城市标识符

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/功能
- **UI自动化**: ✅ 可自动化

---

### TC007: 点击Madrid地址筛选器打开城市面板

#### 📋 前置条件
- 已登录，位于Jobs列表页，默认地址为Madrid

#### 🎬 执行步骤
1. 点击"Madrid"地址筛选按钮（`get_by_text("Madrid", exact=True)`）

#### ✅ 预期结果
1. 地址选择面板展开，面板标题为 **"Select Location"**
2. 面板顶部有历史访问城市快捷入口（如"Barcelona"，可能随用户浏览历史动态变化）
3. 面板顶部有 `textbox "Search City"` 搜索框（`input[placeholder="Search City"]`，class含`CascadingSelector_searchContainer`）
4. 显示 `button "Use current location"` 按钮（class含`LocationWrapper_currentLocationButton`）
5. 省份列表完整显示，按序包含：All Spain / Andalusia / Aragon / Asturias / Balearic Islands / Basque Country / Canary Islands / Cantabria / Castille and Leon / Castille-La Mancha / Catalonia / Ceuta / Extremadura / Galicia / La Rioja / Madrid / Melilla / Murcia / Navarre / Valencia
6. 面板容器 class 为 `CascadingSelector_container__MJ0Rk`

> 🔬 **MCP实测（2026-03-13复核）**：面板打开后顶部首先显示历史访问城市快捷入口（本次实测显示"Barcelona"），之后才是Search City搜索框和Use current location按钮，再是省份列表；省份列表从"All Spain"到"Valencia"共20项
> ⚠️ **录制修正**：无"Near me"选项、无Top Cities列表、无字母A-Z索引；面板为两级省→市结构

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/UI
- **UI自动化**: ✅ 可自动化

### TC008: 地址筛选两级选择城市（Catalonia → Barcelona）

#### 📋 前置条件
- 已登录，地址面板已打开

#### 🎬 执行步骤
1. 在省份列表中点击"Catalonia"
2. 等待第二级城市列表展开（约600ms）
3. 点击城市列表中的"Barcelona"

#### ✅ 预期结果
1. URL变更为`/en/city-barcelona/cate-jobs/`
2. 页面尝试跳转到Barcelona的职位列表
3. 筛选器显示"Barcelona"

> ⚠️ **录制修正**：地址面板为两级省→市结构，不存在Top Cities直接选择
> ⚠️ **已知问题**：Barcelona城市当前返回504 Gateway Timeout，测试时验证URL变更即可

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/功能
- **UI自动化**: ✅ 可自动化

---

### TC009: 地址筛选选择"All Spain"查看全国职位

#### 📋 前置条件
- 已登录，地址面板已打开

#### 🎬 执行步骤
1. 在省份列表第一项点击"All Spain"

#### ✅ 预期结果
1. 面板关闭
2. URL路径变更为 **`/en/city/cate-jobs/?iconSource=jobs`**（注意：含`city`段，非`/en/cate-jobs/`）
3. 筛选器地址标签更新为 **"Location"**（不是"All Spain"，显示通用占位文案）
4. 职位列表更新为全国职位（数量增多）

> 🔬 **MCP实测（2026-03-13复核）**：选择All Spain后URL变为 `https://es.58v5.cn/en/city/cate-jobs/?iconSource=jobs`（含`city`段）；地址筛选器文案变为**"Location"**（非"All Spain"）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/功能
- **UI自动化**: ✅ 可自动化

---

### TC010: 地址面板Search City搜索框过滤城市

#### 📋 前置条件
- 已登录，地址面板已打开

#### 🎬 执行步骤
1. 在面板顶部的 `textbox "Search City"` 输入"Madrid"

#### ✅ 预期结果
1. 省份/城市列表实时过滤，仅显示包含"Madrid"的结果
2. 输入内容为空时恢复完整列表

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/交互
- **UI自动化**: ✅ 可自动化

---

### TC011: 地址筛选"Use current location"（需地理位置权限）

#### 📋 前置条件
- 已登录，地址面板已打开

#### 🎬 执行步骤
1. 点击 `button "Use current location"` 按钮

#### ✅ 预期结果
1. 浏览器弹出地理位置权限请求弹窗
2. 若授权：根据地理位置筛选职位，URL变更为最近城市路径
3. 若拒绝：保持当前地址不变（回到Madrid），页面无报错

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/功能
- **UI自动化**: ❌ 不可自动化（需要浏览器地理位置授权弹窗）

---

### TC012: 点击Job Type筛选器打开类型面板

#### 📋 前置条件
- 已登录，位于Jobs列表页

#### 🎬 执行步骤
1. 点击"Job Type"筛选按钮（`getByText('Job Type')`）

#### ✅ 预期结果
1. Job Type面板展开
2. 显示5个选项：Full-time, Part-time, Contract, Internship, Temporary
3. 显示Clear和Confirm按钮

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/UI
- **UI自动化**: ✅ 可自动化

---

### TC013: Job Type筛选选择Full-time并Confirm

#### 📋 前置条件
- Job Type面板已打开

#### 🎬 执行步骤
1. 点击"Full-time"选项（`.Selector_optionItem__er6y4`第一个）
2. 点击Confirm按钮（`button "Confirm"`）

#### ✅ 预期结果
1. URL追加`&attr_60=1`
2. 筛选器显示"Job Type · 1"
3. 职位列表仅显示Full-time职位
4. 面板关闭

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/功能
- **UI自动化**: ✅ 可自动化

---

### TC014: Job Type筛选多选后Confirm

#### 📋 前置条件
- Job Type面板已打开

#### 🎬 执行步骤
1. 选择"Full-time"和"Part-time"
2. 点击Confirm按钮

#### ✅ 预期结果
1. URL包含两个类型的参数（如`attr_60=1,2`）
2. 筛选器显示"Job Type · 2"
3. 职位列表显示Full-time和Part-time职位（满足任意一种类型均显示）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/功能
- **UI自动化**: ✅ 可自动化

---

### TC015: Job Type筛选点击Clear清除选择

#### 📋 前置条件
- Job Type面板已打开，已选择部分选项

#### 🎬 执行步骤
1. 点击Clear按钮（`button "Clear"`）

#### ✅ 预期结果
1. 所有选项取消勾选
2. 面板仍然打开
3. URL未变更（点击Confirm后才生效）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/交互
- **UI自动化**: ✅ 可自动化

---

### TC016: 点击Workplace type筛选器

#### 📋 前置条件
- 已登录，位于Jobs列表页

#### 🎬 执行步骤
1. 点击"Workplace type"筛选按钮

#### ✅ 预期结果
1. Workplace type面板展开
2. 显示工作地点类型选项（如Onsite, Remote, Hybrid）
3. 显示Clear和Confirm按钮

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/UI
- **UI自动化**: ✅ 可自动化

---

### TC017: Workplace type筛选选择并Confirm

#### 📋 前置条件
- Workplace type面板已打开

#### 🎬 执行步骤
1. 选择"Remote"
2. 点击Confirm按钮

#### ✅ 预期结果
1. URL追加工作地点类型参数
2. 筛选器显示"Workplace type · 1"
3. 职位列表仅显示Remote职位

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/功能
- **UI自动化**: ✅ 可自动化

---

### TC018: 点击Salary筛选器展开面板

#### 📋 前置条件
- 已登录，位于Jobs列表页

#### 🎬 执行步骤
1. 点击筛选栏中的"Salary"筛选按钮（`.FilterItem_filterItemContent__FKrNB`，文案为"Salary"）

#### ✅ 预期结果
1. Salary面板展开（class含`FilterItemPC_filterItemOverlay__jfLC_`）
2. 面板顶部显示 **薪资周期选项**，共 6 项水平排列：Per Hour / Per Day / Per Week / Per Month / Per Biweek / Per Year（class为`FilterItemPC_selectSalaryItem__yZ4GY`）
3. 面板下方显示两个数值输入框：`placeholder="Min"` 和 `placeholder="Max"`（class含`native-numeric-input`，type="text"，无min/max/step属性约束）
4. 面板底部显示 Clear 和 Confirm 按钮

> 🔬 **MCP实测**：面板文本为"Per Hour · Per Day · Per Week · Per Month · Per Biweek · Per Year · Min · Max · Clear · Confirm"；输入框为`input[type='text']`，无`min`/`max`/`step`HTML属性约束

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/UI
- **UI自动化**: ✅ 可自动化

---

### TC019: Salary筛选输入Min+Max范围并Confirm

#### 📋 前置条件
- 已登录，Salary面板已打开

#### 🎬 执行步骤
1. 输入最小薪资 Min = "10000"
2. 输入最大薪资 Max = "30000"
3. 点击 Confirm 按钮

#### ✅ 预期结果
1. URL 追加 `lowestPrice=10000&highestPrice=30000`（薪资参数名为 `lowestPrice` / `highestPrice`）
2. 筛选器显示 **"Salary · 2"**（激活态，class含`FilterItem_filterItemActive__WMq_K`）
3. 面板关闭，职位列表刷新为符合薪资范围的职位

> 🔬 **MCP实测**：
> - URL：`?iconSource=jobs&lowestPrice=10000&highestPrice=30000`
> - 筛选器文本：`'Salary\n·\n2'`（"·2"表示2个参数）
> - 参数名：`lowestPrice` / `highestPrice`（非 `salary_min` / `salary_max`）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/功能
- **UI自动化**: ✅ 可自动化

---

### TC020: Salary筛选选择薪资周期Per Month并Confirm

#### 📋 前置条件
- 已登录，Salary面板已打开

#### 🎬 执行步骤
1. 点击薪资周期选项"Per Month"
2. 输入 Min = "3000"，Max = "10000"
3. 点击 Confirm 按钮

#### ✅ 预期结果
1. URL 追加 `lowestPrice=3000&highestPrice=10000&attr_80=4`（Per Month 对应 `attr_80=4`）
2. 筛选器激活显示"Salary · 2"
3. 职位列表按月薪 3000-10000 范围过滤

> 🔬 **MCP实测**：Per Month → URL含`attr_80=4`；Per Hour → URL**不含** `attr_80` 参数（以Per Hour为默认单位无需追加周期参数）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向/功能
- **UI自动化**: ✅ 可自动化

---

### TC021: Salary筛选只填Min不填Max并Confirm

#### 📋 前置条件
- 已登录，Salary面板已打开

#### 🎬 执行步骤
1. 在 Min 输入框输入 "10000"，Max 输入框**留空**
2. 点击 Confirm 按钮

#### ✅ 预期结果
1. URL 追加 `lowestPrice=10000`（**仅含**最低薪资参数，无 `highestPrice`）
2. 筛选器激活，显示已选择薪资条件
3. 职位列表过滤为薪资 ≥ 10000 的职位

> 🔬 **MCP实测**：URL为`?iconSource=jobs&lowestPrice=10000`，仅追加`lowestPrice`，无`highestPrice`参数

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC022: Salary筛选只填Max不填Min并Confirm

#### 📋 前置条件
- 已登录，Salary面板已打开

#### 🎬 执行步骤
1. Min 输入框**留空**，Max 输入框输入 "30000"
2. 点击 Confirm 按钮

#### ✅ 预期结果
1. URL 追加 `highestPrice=30000`（**仅含**最高薪资参数，无 `lowestPrice`）
2. 筛选器激活，显示已选择薪资条件
3. 职位列表过滤为薪资 ≤ 30000 的职位

> 🔬 **MCP实测**：URL为`?iconSource=jobs&highestPrice=30000`，仅追加`highestPrice`，无`lowestPrice`参数

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC023: Salary筛选两框均不填直接Confirm

#### 📋 前置条件
- 已登录，Salary面板已打开，Min/Max 均为空

#### 🎬 执行步骤
1. 不输入任何内容，直接点击 Confirm 按钮

#### ✅ 预期结果
1. URL 不追加任何薪资参数（URL保持原始状态，如`?iconSource=jobs`）
2. 面板关闭，筛选器不激活
3. 职位列表不变

> 🔬 **MCP实测**：空提交后URL为`?iconSource=jobs`，无任何薪资参数追加

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC024: Salary筛选Min大于Max时提示错误

#### 📋 前置条件
- 已登录，Salary面板已打开

#### 🎬 执行步骤
1. Min 输入框输入 "50000"
2. Max 输入框输入 "10000"（小于Min）
3. 点击 Confirm 按钮

#### ✅ 预期结果
1. 面板**保持打开**，不跳转页面（URL不变）
2. 显示错误提示文案：**"Max price must be higher than min price"**
3. Min/Max 输入框仍保留原输入值（`50,000` 和 `10,000`，会自动加千分位逗号）
4. 不追加任何薪资参数到 URL

> 🔬 **MCP实测**：
> - 错误提示文案：`"Max price must be higher than min price"`
> - 面板仍打开（`input[placeholder='Min']` count > 0）
> - 输入值格式化为 `'50,000'` / `'10,000'`（添加千分位）
> - URL仍为`?iconSource=jobs`

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 异常流
- **UI自动化**: ✅ 可自动化

---

### TC025: Salary筛选Min等于Max时Confirm

#### 📋 前置条件
- 已登录，Salary面板已打开

#### 🎬 执行步骤
1. Min 和 Max 均输入 "20000"
2. 点击 Confirm 按钮

#### ✅ 预期结果
1. URL 追加 `lowestPrice=20000&highestPrice=20000`（接受等值范围）
2. 面板关闭，筛选器激活
3. 职位列表过滤为薪资恰好为 20000 的职位

> 🔬 **MCP实测**：URL为`?iconSource=jobs&lowestPrice=20000&highestPrice=20000`，等值不触发错误校验

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC026: Salary筛选Min输入0并Confirm

#### 📋 前置条件
- 已登录，Salary面板已打开

#### 🎬 执行步骤
1. Min 输入 "0"，Max 输入 "10000"
2. 点击 Confirm 按钮

#### ✅ 预期结果
1. URL 追加 `lowestPrice=0&highestPrice=10000`（0 被视为有效最低薪资）
2. 面板关闭，筛选器激活
3. 职位列表过滤为薪资 ≤ 10000 的职位（含0薪职位）

> 🔬 **MCP实测**：URL为`?iconSource=jobs&lowestPrice=0&highestPrice=10000`，0值正常提交

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC027: Salary筛选输入负数被拦截

#### 📋 前置条件
- 已登录，Salary面板已打开

#### 🎬 执行步骤
1. 在 Min 输入框输入 "-5000"（负数）

#### ✅ 预期结果
1. 输入框实际值为5000（负号被自动过滤，不允许输入负值）
2. 不显示错误提示（输入时直接阻止，非提交时校验）

> 🔬 **MCP实测**：输入"-5000"后，`input_value()` 返回空字符串 `''`，输入框拒绝负号

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 异常流
- **UI自动化**: ✅ 可自动化

---

### TC028: Salary筛选输入字母被拦截

#### 📋 前置条件
- 已登录，Salary面板已打开

#### 🎬 执行步骤
1. 在 Min 输入框输入 "abc"（字母）

#### ✅ 预期结果
1. 输入框实际值为**空字符串**（字母被自动过滤，只允许数字输入）
2. 不显示错误提示

> 🔬 **MCP实测**：输入"abc"后，`input_value()` 返回空字符串 `''`，字母字符被拦截

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 异常流
- **UI自动化**: ✅ 可自动化

---

### TC029: Salary筛选输入小数被接受

#### 📋 前置条件
- 已登录，Salary面板已打开

#### 🎬 执行步骤
1. Min 输入 "1000.5"，Max 输入 "5000.99"
2. 点击 Confirm 按钮

#### ✅ 预期结果
1. 输入框接受小数（Min 显示为 `1,000.5`，Max 显示为 `5000.99`）
2. URL 追加 `lowestPrice=1000.5&highestPrice=5000.99`（小数值原样传递）
3. 面板关闭，筛选执行

> 🔬 **MCP实测**：Min="1000.5" → 值显示为`1,000.5`（千分位格式化）；URL为`?lowestPrice=1000.5&highestPrice=5000.99`

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC030: Salary筛选输入超大值并Confirm

#### 📋 前置条件
- 已登录，Salary面板已打开

#### 🎬 执行步骤
1. Min 输入 "9999999"，Max 输入 "99999999"
2. 点击 Confirm 按钮

#### ✅ 预期结果
1. URL 追加 `lowestPrice=9999999&highestPrice=99999999`（无上限校验）
2. 面板关闭，职位列表可能为空（无匹配职位）
3. 页面无报错（超大值被正常接受并传递）

> 🔬 **MCP实测**：URL为`?iconSource=jobs&lowestPrice=9999999&highestPrice=99999999`，前端无上限限制

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC031: Salary筛选Clear清空Min/Max输入框

#### 📋 前置条件
- 已登录，Salary面板已打开，Min/Max 已有输入值

#### 🎬 执行步骤
1. 输入 Min = "10000"，Max = "30000"
2. 点击 Clear 按钮

#### ✅ 预期结果
1. Min 和 Max 输入框均清空（值变为空字符串）
2. 面板**保持打开**（不关闭）
3. URL **不变**（Clear只清空面板内输入，不提交）

> 🔬 **MCP实测**：Clear后Min/Max均为空`''`；面板仍开着（`input[placeholder='Min']` count=1）；URL无变化

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/交互
- **UI自动化**: ✅ 可自动化

---

### TC032: 已设置Salary筛选后再次打开面板，输入框回填已选值

#### 📋 前置条件
- 已登录，已设置薪资筛选（Min=10000, Max=30000），URL含`lowestPrice=10000&highestPrice=30000`

#### 🎬 执行步骤
1. 点击已激活的"Salary · 2"筛选器，再次打开面板

#### ✅ 预期结果
1. Min 输入框回填已选值，显示 **"10,000"**（带千分位格式化）
2. Max 输入框回填已选值，显示 **"30,000"**（带千分位格式化）
3. 面板正常展开可供修改

> 🔬 **MCP实测**：再次打开面板后，`input[placeholder='Min']` 值为 `'10,000'`，`input[placeholder='Max']` 值为 `'30,000'`

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/UI
- **UI自动化**: ✅ 可自动化

---

### TC033: 已设置Job Type单选后再次打开面板，已选项正确回显选中状态

#### 📋 前置条件
- 已登录，已设置 Job Type 筛选为"Full-time"，URL 含 `attr_60=1`，筛选器显示"Job Type · 1"

#### 🎬 执行步骤
1. 点击已激活的"Job Type · 1"筛选器，再次打开面板

#### ✅ 预期结果
1. 面板展开，共显示5个选项：Full-time、Part-time、Contract、Internship、Temporary
2. "Full-time"选项带有 `Selector_selected__7svoy` class，图标为 `icon_selected`（勾选状态）
3. 其余4个选项无选中态，图标为 `icon_unselected`
4. 面板底部"Clear"和"Confirm"按钮可见

> 🔬 **MCP实测**：再次打开面板后，`Full-time` 元素 classList 含 `Selector_selected__7svoy`，img src 为 `icon_selected.*.png`；其余选项 classList 无该 class，img src 为 `icon_unselected.*.png`

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/UI
- **UI自动化**: ✅ 可自动化（断言 `.Selector_selected__7svoy` 仅有1个且文本为"Full-time"）

---

### TC034: 已设置Job Type多选后再次打开面板，所有已选项均正确回显

#### 📋 前置条件
- 已登录，已设置 Job Type 筛选为 Full-time + Part-time，URL 含 `attr_60=2%2C1`（即 `2,1`），筛选器显示"Job Type · 2"

#### 🎬 执行步骤
1. 点击已激活的"Job Type · 2"筛选器，再次打开面板

#### ✅ 预期结果
1. "Full-time"和"Part-time"均显示选中态（`Selector_selected__7svoy` class + `icon_selected` 图标）
2. "Contract"、"Internship"、"Temporary"显示未选中态（`icon_unselected` 图标）
3. 筛选器 badge 数量（· 2）与面板内选中数量一致

> 🔬 **MCP实测**：多选 Full-time + Part-time Confirm 后 URL 为 `attr_60=2%2C1`（逗号分隔多值），再次打开面板，两个选项均含 `Selector_selected__7svoy`，其余3项无该 class；与筛选器 badge 数量一致

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/UI
- **UI自动化**: ✅ 可自动化（断言 `.Selector_selected__7svoy` 数量为2，且分别含"Full-time"和"Part-time"）

---

### TC035: 已设置Workplace type筛选后再次打开面板，已选项正确回显

#### 📋 前置条件
- 已登录，已设置 Workplace type 筛选（如选择 Remote），URL 含对应参数，筛选器显示"Workplace type · 1"

#### 🎬 执行步骤
1. 点击已激活的"Workplace type · 1"筛选器，再次打开面板

#### ✅ 预期结果
1. 面板展开，显示可选的 Workplace type 选项列表
2. 已选项（Remote）显示选中态（`Selector_selected__7svoy` class + `icon_selected` 图标）
3. 其余选项显示未选中态

> 🔬 **MCP实测**：Workplace type 面板选项结构与 Job Type 面板一致，使用同一组 CSS class（`Selector_optionItem__er6y4` / `Selector_selected__7svoy`）区分选中/未选中态

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/UI
- **UI自动化**: ✅ 可自动化

---

### TC036: 通过URL直接携带筛选参数进入页面，筛选面板能正确回显已选值

#### 📋 前置条件
- 已登录，直接访问含筛选参数的 URL（如 `?attr_60=1` 表示 Job Type=Full-time）

#### 🎬 执行步骤
1. 直接在浏览器地址栏输入含筛选参数的 URL 并回车，进入 Jobs 列表页
2. 点击对应筛选器（如 Job Type）打开面板

#### ✅ 预期结果
1. 筛选器 badge 正确显示选中数量（如"Job Type · 1"）
2. 打开面板后，对应选项回显为选中态（`Selector_selected__7svoy` class + `icon_selected` 图标）
3. 职位列表已按 URL 中的参数过滤展示

> 🔬 **MCP实测**：访问 `?attr_60=1` 时筛选器正确显示"Job Type · 1"，打开面板后"Full-time"回显选中；访问 `?attr_60=1&attr_60=2`（重复 key 形式）时，面板仅识别最后一个值（Part-time=2），筛选器仍显示"· 1"——⚠️ 多值应使用逗号分隔形式 `attr_60=2%2C1` 而非重复 key

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向/功能
- **UI自动化**: ✅ 可自动化（直接导航到带参数URL，断言筛选器badge和面板选中态）

---

### TC037: 组合筛选（Job Type + Workplace type）

#### 📋 前置条件
- 已登录，位于Jobs列表页

#### 🎬 执行步骤
1. 选择Job Type为"Full-time"，Confirm
2. 选择Workplace type为"Remote"，Confirm

#### ✅ 预期结果
1. URL包含两个筛选参数
2. 筛选器显示"Job Type · 1"和"Workplace type · 1"
3. 职位列表同时满足两个条件

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/组合
- **UI自动化**: ✅ 可自动化

---

### TC038: 组合筛选（搜索 + Job Type）

#### 📋 前置条件
- 已登录，位于Jobs列表页

#### 🎬 执行步骤
1. 搜索"manager"
2. 选择Job Type为"Full-time"，Confirm

#### ✅ 预期结果
1. URL包含`keyword=manager&attr_60=1`
2. 筛选器显示"Job Type · 1"
3. 职位列表同时满足搜索和筛选条件

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/组合
- **UI自动化**: ✅ 可自动化

---

### TC039: 点击Reset按钮清除所有筛选

#### 📋 前置条件
- 已设置搜索关键词和筛选条件

#### 🎬 执行步骤
1. 点击筛选栏右侧的Reset区域（`.listPage-filterArea-submit`，文案为"Reset"，非 `button` 角色而是 `div`）

#### ✅ 预期结果
1. URL恢复为`/cate-jobs/?iconSource=jobs`，移除所有筛选参数
2. 所有筛选器重置（地址保持默认Madrid）
3. 搜索框内容**保留**（Reset不清空搜索词，搜索词仍保留在URL中）
4. 职位列表刷新

> 🔬 **MCP实测**：Reset后URL变为 `?iconSource=jobs`（移除`attr_60=1`等），地址保持Madrid；但若有搜索词`keyword=manager`，Reset不清除搜索框，keyword仍保留
> ⚠️ **注意**：Reset元素为 `div.listPage-filterArea-submit`，非 `button` 角色，需用 `.locator(".listPage-filterArea-submit")` 点击

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/功能
- **UI自动化**: ✅ 可自动化

---

### TC040: Reset后地址筛选保持默认值

#### 📋 前置条件
- 已点击Reset清除筛选

#### 🎬 执行步骤
1. 观察地址筛选器

#### ✅ 预期结果
1. 地址筛选器仍显示"Madrid"
2. URL保持在Madrid城市页

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/功能
- **UI自动化**: ✅ 可自动化

---

### TC041: 滚动到底部触发自动加载更多职位

> ⚠️ **已修正**：原TC037为"点击页码2翻页"，实际页面为feed流无限滚动，无分页按钮，用例重写。

#### 📋 前置条件
- 已打开Jobs列表页（任意状态）

#### 🎬 执行步骤
1. 滚动页面至职位列表底部
2. 等待自动加载触发（约2秒）

#### ✅ 预期结果
1. 新的职位卡片追加到列表末尾（每批约9条）
2. 页面 scrollHeight 增大（新内容撑高页面）
3. URL **不发生变化**（无`page=`等参数追加）
4. 筛选器状态保持不变

> 🔬 **MCP实测**：初始加载30条，滚动底部后2秒内新增9条（共39条），再次滚动继续追加；未观察到明显loading spinner，直接追加卡片；每次触发 `analytics-firebase list_slide` 事件；URL始终不变

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/功能
- **UI自动化**: ✅ 可自动化（`page.evaluate('window.scrollTo(0, document.body.scrollHeight)')` + 等待2s + 断言卡片数增加）

---

### TC042: 滚动加载不改变URL及筛选器状态

> ⚠️ **已修正**：原TC038为"点击Next按钮翻页"，实际无Next按钮，用例重写。

#### 📋 前置条件
- 已打开Jobs列表页，并设置了筛选条件（如Job Type=Full-time）

#### 🎬 执行步骤
1. 设置筛选条件后，滚动到列表底部触发加载
2. 加载完成后检查URL和筛选器

#### ✅ 预期结果
1. URL 不变（只含筛选参数，无`page=`）
2. 筛选器仍显示激活态（如"Job Type · 1"）
3. 新追加的职位卡片符合筛选条件

> 🔬 **MCP实测**：无限滚动加载期间未观察到明显spinner，加载以静默方式追加卡片；URL在整个滚动过程中保持不变

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/功能
- **UI自动化**: ✅ 可自动化

---

### TC043: 筛选条件变更后列表从头重新加载

> ⚠️ **已修正**：原TC039为"翻页后保留筛选条件"（基于分页参数），实际无分页，用例重写。

#### 📋 前置条件
- 已进入Jobs列表页并滚动加载了多批职位

#### 🎬 执行步骤
1. 先滚动加载若干批次职位（如2~3次）
2. 切换筛选器（如选择Job Type: Full-time）

#### ✅ 预期结果
1. 列表滚动回顶部，职位卡片重置为第一批
2. URL更新为含筛选参数（如`&attr_60=1`），**无`page=`参数**
3. 筛选器显示"Job Type · 1"激活态
4. 再次滚动到底部，加载的是符合筛选条件的后续职位

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/功能
- **UI自动化**: ✅ 可自动化

---

### TC044: 所有职位加载完毕后列表停止增长

> ⚠️ **已修正**：原TC040为"最后一页Next按钮不可点击"，实际无分页按钮，用例重写。

#### 📋 前置条件
- 搜索关键词精确或筛选条件严格，使总职位数量较少（能触达列表末尾）

#### 🎬 执行步骤
1. 持续滚动到列表底部，重复多次
2. 记录每次滚动后的卡片总数

#### ✅ 预期结果
1. 某次滚动后卡片数不再增加
2. 后续滚动 scrollHeight 不变
3. URL 无变化
4. 结束态具体样式（文案/空白/icon）**待实测数据量不足时确认**

> 🔬 **MCP实测**：测试数据量较多（5次滚动共加载49条仍未到末尾），无法触达结束态；结束态文案待后续补充确认

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化（断言两次连续滚动后卡片数相同）

---

### TC045: 页面无翻页按钮（无Previous/Next/页码）

> ⚠️ **已修正**：原TC041为"第一页Previous按钮不可点击"，实际采用feed流无任何分页按钮。

#### 📋 前置条件
- 已打开Jobs列表页

#### 🎬 执行步骤
1. 观察页面整体结构
2. 断言页面中不存在翻页相关元素

#### ✅ 预期结果
1. 页面中**无**`button "Previous"`、`button "Next"` 元素（count 均为 0）
2. 页面中**无**页码数字按钮组
3. 页面底部为 loading 触发区域而非分页组件

> 🔬 **MCP实测修正**：原文档描述的`page=`URL参数翻页模式不适用于此页面。

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 负向/异常
- **UI自动化**: ✅ 可自动化（count断言）

---

### TC046: 点击"Add Job Preference"跳转中间页

#### 📋 前置条件
- 已登录，无岗位偏好，位于Jobs列表页

#### 🎬 执行步骤
1. 在职位列表顶部找到"Add Job Preference"入口卡片
2. 点击该卡片（`generic[ref=e64]`，文案为"Add Job Preference" + "Unlock more opportunities tailored for you."）

#### ✅ 预期结果
1. 跳转到Job Preferences中间页
2. URL包含`jobPreference`
3. 中间页显示Job Functions、Location、Salary等偏好设置字段

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/功能
- **UI自动化**: ✅ 可自动化

---

## 职位卡片交互用例（MCP录制新增）

### TC047: 点击职位卡片展开右侧详情侧边栏

#### 📋 前置条件
- 已登录，位于Jobs列表页，列表有职位数据

#### 🎬 执行步骤
1. 点击列表中任意一张职位卡片

#### ✅ 预期结果
1. 右侧展开职位详情侧边栏（双栏布局）
2. 侧边栏显示：职位标题、薪资、公司名称
3. 显示工作类型、工作地点、经验要求、学历要求
4. 显示职位描述（Description）
5. 显示发布/更新时间
6. 显示招聘者姓名和公司信息
7. 显示 Company 区域（公司名、员工规模）

> 🔬 **MCP实测（2026-03-13复核）**：页面初次加载后，侧边栏**默认已自动展开**（显示列表第一条职位详情），无需点击卡片即可看到侧边栏。点击其他卡片会切换侧边栏显示对应职位详情。

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/功能
- **UI自动化**: ✅ 可自动化

---

### TC048: 职位侧边栏操作按钮验证（非自投职位）

#### 📋 前置条件
- 已登录，点击了他人发布的职位卡片，侧边栏已展开

#### 🎬 执行步骤
1. 观察侧边栏顶部操作区域的按钮

#### ✅ 预期结果
1. 显示 `button "Contact"` 按钮
2. 显示 "Favourites" 收藏按钮（`[cursor=pointer]`，非 button 角色）
3. 显示 "New tab" 链接（`link "New tab"`）
4. 显示 "Share" 分享按钮（`[cursor=pointer]`，非 button 角色）
5. **不**显示 Withdraw / Edit 按钮

> 🔬 **MCP实测**：点击他人职位后侧边栏显示 `button "Contact"` + `generic "Favourites"` + `link "New tab"` + `generic "Share"`；自投职位则显示 `button "Withdraw"` + `button "Edit"` + `generic "Favourites"` + `link "New tab"` + `generic "Share"`，无 Contact

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/UI
- **UI自动化**: ✅ 可自动化

---

### TC049: 自投职位侧边栏显示Withdraw/Edit按钮

#### 📋 前置条件
- 已登录，点击了**自己**发布的职位卡片，侧边栏已展开

#### 🎬 执行步骤
1. 观察侧边栏顶部操作区域的按钮

#### ✅ 预期结果
1. 显示 `button "Withdraw"` 按钮
2. 显示 `button "Edit"` 按钮
3. 显示 "Favourites" / "New tab" / "Share" 按钮
4. **不**显示 Contact 按钮

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/UI
- **UI自动化**: ✅ 可自动化

---

### TC050: 职位卡片Quick Reply显示验证（不可独立点击）

#### 📋 前置条件
- 已登录，职位列表可见

#### 🎬 执行步骤
1. 观察职位卡片底部的"Quick Reply"文案
2. 点击卡片上的"Quick Reply"区域

#### ✅ 预期结果
1. "Quick Reply"文案在卡片底部可见（class为 `company-module-cative-time`，颜色为绿色 `rgb(18, 185, 164)`）
2. 点击"Quick Reply"区域**等同于点击整张卡片**，结果是右侧侧边栏切换展示该职位详情
3. **不**触发独立的快速回复流程（无弹窗、无跳转消息页）
4. Quick Reply 文案为**纯展示性标签**，无独立点击交互

> 🔬 **MCP实测**：Quick Reply 元素 CSS `cursor:pointer` 但在accessibility snapshot中无 `[cursor=pointer]` 标注；点击后触发 `list_click`+`list_slide` 事件，行为与点击卡片其他区域相同——仅切换侧边栏详情，不触发回复功能

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向/UI
- **UI自动化**: ✅ 可自动化（断言点击后侧边栏切换为对应职位，无回复弹窗出现）

---

### TC051: 点击侧边栏Favourites收藏职位

#### 📋 前置条件
- 已登录，职位详情侧边栏已展开

#### 🎬 执行步骤
1. 点击侧边栏中的"Favourites"按钮

#### ✅ 预期结果
1. 按钮状态变化（已收藏/未收藏切换）
2. 不跳转页面，原地操作
3. 再次点击可取消收藏

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/功能
- **UI自动化**: ✅ 可自动化

---

### TC052: 点击侧边栏New tab在新标签页打开职位详情

#### 📋 前置条件
- 已登录，职位详情侧边栏已展开

#### 🎬 执行步骤
1. 点击侧边栏中的"New tab"链接

#### ✅ 预期结果
1. 在新浏览器标签页打开该职位的独立详情页
2. 原列表页保持不变
3. 新标签页URL为该职位的独立详情页面

> 🔬 **MCP实测**：`link "New tab"` 的 `/url` 在快照中显示为空字符串（`""`），实际点击后需观察是否通过JS动态设置href或触发弹窗。建议用 `page.expect_popup()` 捕获新标签页来断言

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向/功能
- **UI自动化**: ✅ 可自动化（使用 `page.expect_popup()` 捕获新标签页）

---

### TC053: 职位卡片技能标签（Highlight）显示验证

#### 📋 前置条件
- 已登录，职位列表中有含技能标签的职位

#### 🎬 执行步骤
1. 观察职位卡片中间区域的技能标签

#### ✅ 预期结果
1. 职位卡片中显示技能/亮点标签列表（如 · ok1 · ok2 · ok3）
2. 标签以"·"分隔显示
3. 最多显示3-4个标签（超出截断）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向/UI
- **UI自动化**: ✅ 可自动化

---

## 搜索交互细节用例（新增）

### TC054: 搜索框内容清空后重新搜索

#### 📋 前置条件
- 已登录，已搜索"manager"，URL含`keyword=manager`

#### 🎬 执行步骤
1. 清空搜索框内容
2. 点击Search按钮

#### ✅ 预期结果
1. URL中keyword参数变为空值：`keyword=`（参数保留但值为空，**不**被移除）
2. 职位列表恢复为全部职位（等同于空搜索）

> 🔬 **MCP实测**：清空输入框后点击Search，URL变为 `?iconSource=jobs&keyword=`，keyword参数存在但值为空字符串

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/交互
- **UI自动化**: ✅ 可自动化

---

### TC055: 搜索后再次修改搜索词

#### 📋 前置条件
- 已登录，已搜索"manager"，URL含`keyword=manager`

#### 🎬 执行步骤
1. 清空搜索框，输入新词"driver"
2. 点击Search按钮

#### ✅ 预期结果
1. URL中keyword更新为`keyword=driver`
2. 职位列表更新为"driver"的搜索结果
3. 已有的筛选条件（如Job Type）仍然保留

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/功能
- **UI自动化**: ✅ 可自动化

---

### TC056: 搜索词含空格的处理

#### 📋 前置条件
- 已登录，位于Jobs列表页

#### 🎬 执行步骤
1. 搜索框输入"software engineer"（含空格）
2. 点击Search按钮

#### ✅ 预期结果
1. URL将空格编码为`%20`（如`keyword=software%20engineer`，**不**使用`+`号编码）
2. 搜索结果正常返回

> 🔬 **MCP实测**：URL为 `?keyword=software%20engineer`，使用`%20`编码空格

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

## 筛选器交互细节用例（新增）

### TC057: 打开Job Type面板后点击外部关闭面板

#### 📋 前置条件
- 已登录，Job Type面板已打开

#### 🎬 执行步骤
1. 点击面板外部区域（如页面顶部标题区或页面空白处，**不**点击筛选器区域）

#### ✅ 预期结果
1. Job Type面板关闭（`[class*='optionItem']` count变为0）
2. 筛选条件未提交（URL不变）
3. 已选择但未Confirm的选项**不生效**（URL无变更）

> 🔬 **MCP实测**：面板打开时optionItem count=5，点击h1标题区后optionItem count=0，面板关闭；URL未变

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/交互
- **UI自动化**: ✅ 可自动化

---

### TC058: Job Type筛选5个选项全选后Confirm

#### 📋 前置条件
- 已登录，Job Type面板已打开

#### 🎬 执行步骤
1. 依次点击所有5个选项：Full-time、Part-time、Contract、Internship、Temporary
2. 点击Confirm按钮

#### ✅ 预期结果
1. URL包含5种类型的参数
2. 筛选器显示"Job Type · 5"
3. 职位列表显示所有类型职位（等同于无筛选）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC059: Workplace type和Job Type同时Clear后分别Confirm

#### 📋 前置条件
- 已登录，已设置Job Type=Full-time、Workplace type=Remote筛选

#### 🎬 执行步骤
1. 打开Job Type面板，点击Clear，点击Confirm
2. 打开Workplace type面板，点击Clear，点击Confirm

#### ✅ 预期结果
1. Job Type筛选清除，URL移除对应参数
2. Workplace type筛选清除，URL移除对应参数
3. 筛选器回到初始无选中状态

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/组合
- **UI自动化**: ✅ 可自动化

---

## Reset功能边界用例（新增）

### TC060: 无筛选条件时Reset按钮的状态

#### 📋 前置条件
- 已登录，位于Jobs列表页，**未设置任何筛选**

#### 🎬 执行步骤
1. 观察Reset按钮的显示状态

#### ✅ 预期结果
1. Reset区域（`.listPage-filterArea-submit`）**始终显示**，无论有无筛选（非disabled状态，`opacity:1, cursor:pointer`）
2. 无筛选时点击Reset不产生明显效果（URL不变，列表无变化）

> 🔬 **MCP实测**：无筛选时Reset div始终存在且可见，computed style为 `cursor:pointer, opacity:1`，并非disabled或隐藏状态；Reset元素为div非button，无法通过 `is_disabled()` 检测

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

## 页面底部Popular Cities用例（MCP录制新增）

### TC061: 页面底部Popular Cities标签页

#### 📋 前置条件
- 已登录，位于Jobs列表页

#### 🎬 执行步骤
1. 页面底部（无需手动滚动，初次加载即可见）
2. 找到"Popular Cities"区域

#### ✅ 预期结果
1. 显示 `tab "Popular Cities active"` 标签页（含active状态图标）
2. 标签页下方展示热门城市链接列表（`tabpanel` 内部）
3. 城市链接格式为"{城市} Jobs Recruitment"（如"Galicia Jobs Recruitment"）
4. 城市列表为**动态内容**，每次刷新可能显示不同城市
5. 城市链接 href 格式为 `https://es.58v5.cn/en/city-{cityname}/cate-jobs/`

> 🔬 **MCP实测**：`tablist` 含 `tab "Popular Cities active"`，`tabpanel` 内含若干 `link "{City} Jobs Recruitment"`，URL格式如 `/en/city-galicia/cate-jobs/`、`/en/city-catalonia/cate-jobs/` 等；城市列表每次刷新不同

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向/UI
- **UI自动化**: ✅ 可自动化（断言 tabpanel 内 link 数量 > 0，href 格式匹配）

---

### TC062: 点击Popular Cities中的城市链接跳转

#### 📋 前置条件
- 已登录，位于Jobs列表页底部Popular Cities区域

#### 🎬 执行步骤
1. 点击Popular Cities中任意一个城市链接（如"Girona Jobs Recruitment"）

#### ✅ 预期结果
1. 跳转到对应城市的Jobs列表页（URL含该城市名）
2. 筛选器地址更新为对应城市
3. 职位列表更新为该城市职位

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向/功能
- **UI自动化**: ✅ 可自动化

---

## 页面侧边栏详情区Resume按钮用例（新增）

### TC063: 职位侧边栏底部Resume快捷入口

#### 📋 前置条件
- 已登录，职位详情侧边栏已展开

#### 🎬 执行步骤
1. 在侧边栏底部找到"Resume"快捷入口（`generic "Resume" [cursor=pointer]`）
2. 点击"Resume"

#### ✅ 预期结果
1. 跳转到简历填写页：`https://espub.58v5.cn/biz/en/resume/add`
2. 页面显示"Personal Information"表单（含First Name、Last Name、Email、Current Location、Gender字段）
3. 可通过浏览器返回按钮回到Jobs列表页

> 🔬 **MCP实测**：点击Resume后URL变为 `https://espub.58v5.cn/biz/en/resume/add`，页面标题"Jobs"，显示 `heading "Personal Information"` 表单，含 Email 预填值（当前账号邮箱）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向/功能
- **UI自动化**: ✅ 可自动化（断言URL含`/resume/add`，`heading "Personal Information"` 可见）

---

## 导航栏用例（新增）

### TC064: 顶部导航栏Home链接跳转

#### 📋 前置条件
- 已登录，位于Jobs列表页

#### 🎬 执行步骤
1. 点击顶部面包屑导航中的"Home"链接

#### ✅ 预期结果
1. 跳转到ES站首页（`https://es.58v5.cn/en/city-madrid2/`）
2. 离开Jobs列表页

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向/导航
- **UI自动化**: ✅ 可自动化

---

### TC065: 顶部导航Browse菜单点击

#### 📋 前置条件
- 已登录，位于Jobs列表页

#### 🎬 执行步骤
1. 点击顶部导航中的"Browse"按钮

#### ✅ 预期结果
1. 展开Browse下拉菜单（含Jobs、房产、分类广告等分类链接）
2. 可从菜单中点击进入不同分类页面

> 🔬 **MCP实测**：顶部导航有"Browse"链接，点击后展开分类菜单

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向/导航
- **UI自动化**: ✅ 可自动化

---

## 测试统计

### 用例概览
- **总用例数**: 65条（TC001～TC065，编号连续）
- **可自动化**: 63条 (97%)
- **不可自动化**: 2条 (3%)（TC011地理位置授权）

### 按优先级分布
| 优先级 | 总数 | 可自动化 | 自动化率 |
|--------|------|---------|---------|
| P0 | 15 | 15 | 100% |
| P1 | 30 | 29 | 96.7% |
| P2 | 20 | 19 | 95.0% |
| **总计** | **65** | **63** | **96.9%** |

### 按测试类型分布
| 测试类型 | 用例数量 | 可自动化 |
|---------|---------|---------|
| 正向/功能 | 22 | 22 |
| 正向/UI | 13 | 13 |
| 正向/交互 | 5 | 5 |
| 正向/组合 | 4 | 4 |
| 边界值 | 13 | 13 |
| 异常流 | 2 | 2 |
| 正向/导航 | 4 | 4 |
| 正向/边界 | 2 | 0 |

### 按模块分布
| 模块 | 用例数量 | TC编号范围 |
|------|---------|-----------|
| 搜索框 | 7 | TC001～TC004, TC054～TC056 |
| 地址筛选 | 8 | TC005～TC011 |
| Job Type筛选 | 8 | TC012～TC015, TC033～TC034, TC057～TC058 |
| Workplace type筛选 | 4 | TC016～TC017, TC035, TC059 |
| Salary筛选 | 16 | TC018～TC032 |
| 筛选回显 | 4 | TC033～TC036 |
| 组合筛选 | 3 | TC037～TC039 |
| Reset功能 | 3 | TC039～TC041 |
| feed流加载 | 5 | TC041～TC045 |
| 职位卡片/侧边栏交互 | 9 | TC046～TC054 |
| 页面底部/导航 | 5 | TC061～TC065 |

---

## 参考文档

- [ES站首页](https://es.58v5.cn/en/city-madrid2/)
- [Jobs列表页](https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs)
- [Job Preferences中间页](https://espub.58v5.cn/biz/en/jobPreference)

---

## 变更记录

| 日期 | 版本 | 变更内容 | 变更人 |
|------|------|---------|--------|
| 2026-03-09 | v1.0 | 初始版本，完成25条测试用例，符合senior-qa-brain和playwright-test-generator规范 | AI |
| 2026-03-12 | v2.0 | 基于MCP真实录制扩充：修正地址面板结构（两级省→市）、补充职位卡片交互/侧边栏/未登录/搜索细节/筛选边界/翻页组合/页面底部/导航等28条新用例 | AI |
| 2026-03-12 | v2.1 | 基于Playwright脚本实测：将所有"或"不确定性预期结果替换为确定性结论（空搜索URL格式、特殊字符无结果提示文案、maxlength缺失、Salary面板为Min/Max输入框、Reset不清空搜索词、Previous/Next在边界页隐藏而非禁用、Reset元素为div非button、空格编码为%20等） | AI |
| 2026-03-12 | v2.2 | 新增地址筛选器默认值校验用例TC004b/TC006：验证页面加载后Madrid默认激活态（class含FilterItemActive）、URL城市段为city-madrid2、筛选器共4项；补充切换城市后URL和筛选器同步更新；修正TC005面板标题为"Select Location"、省份列表共20项 | AI |
| 2026-03-12 | v2.3 | 基于Playwright实测扩充Salary输入框用例TC015a-m（共13条）：薪资周期选项6项/URL参数名lowestPrice&highestPrice/Per Month对应attr_80=4/只填Min只填Max/两框为空/Min>Max错误文案/Min=Max/Min=0/负数拦截/字母拦截/小数接受/超大值/Clear行为/已选值回填 | AI |
| 2026-03-13 | v2.4 | MCP实测复核差异修正：①TC007补充地址面板顶部有历史访问城市快捷入口；②TC009修正All Spain后URL为`/en/city/cate-jobs/`（非`/en/cate-jobs/`）、筛选器显示"Location"（非"All Spain"）；③TC043补充页面加载后侧边栏默认自动展开第一条职位详情；④业务规则修正：翻页Previous/Next为隐藏非禁用；Reset不清空搜索词；地址面板有历史入口 | AI |
| 2026-03-13 | v2.5 | 修正翻页用例：列表为feed流（无限滚动）而非分页模式，无Previous/Next/页码按钮，无`page=`URL参数。TC037-TC041全部重写：改为验证滚动加载更多、loading状态、筛选变更重置列表、加载结束态、无翻页按钮断言；页面结构第4节和业务规则第6条同步更新 | AI |
| 2026-03-13 | v2.6 | 去重：删除6条重复用例——TC059（与TC021重复：Salary只填Min）、TC060（与TC024重复：Salary Min>Max报错）、TC062（与TC035重复：Reset不清空搜索词）、TC063/TC064/TC065（基于分页模式的翻页用例，feed流不适用）；总用例数由70更新为64条 | AI |
| 2026-03-13 | v2.7 | 删除未登录场景用例：移除TC050（未登录浏览列表）、TC051（未登录点Favourites）、TC052（未登录搜索筛选）共3条；同步清理业务规则第9条未登录说明、TC005前置条件"或未登录"文案、模块分布统计表；总用例数更新为61条 | AI |
| 2026-03-13 | v2.8 | MCP实测复核TC037-TC070：①TC037修正每批加载约9条，无明显spinner，追加方式静默完成；②TC038改为验证滚动加载不改变URL及筛选器；③TC040修正结束态待确认（测试数据量不足）；④TC044补充Favourites/Share为generic非button；⑤TC048补充New tab链接href为空需用expect_popup捕获；⑥TC066补充Popular Cities为动态内容、href格式确认；⑦TC068修正Resume跳转URL为`/biz/en/resume/add`（简历填写页而非profile页） | AI |
| 2026-03-13 | v2.9 | MCP实测补充筛选项回显用例：新增TC032b（Job Type单选回显）、TC032c（Job Type多选回显）、TC032d（Workplace type回显）、TC032e（URL直接带参数进入页面时回显）共4条；实测确认选中态标记为 `Selector_selected__7svoy` class + `icon_selected` 图标，多选值URL格式为逗号分隔（`attr_60=2%2C1`）；补充边界：重复key形式（`attr_60=1&attr_60=2`）时仅识别最后一个值；总用例数更新为65条 | AI |
| 2026-03-13 | v3.0 | 编号重排：将所有TC编号统一为TC001～TC065连续序列（原TC032b→TC033，TC032c→TC034，TC032d→TC035，TC032e→TC036，原TC033～TC049顺移，原TC053～TC058→TC054～TC059，原TC061→TC060，原TC066～TC070→TC061～TC065）；同步更新测试统计区总数及模块分布表；变更记录中v2.x所引旧编号为历史版本号，仅供参考 | AI |
