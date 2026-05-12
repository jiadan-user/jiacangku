# OK ES 站 - 招聘列表页 详情面板展示与操作 测试用例

> **生成时间**: 2026-03-16  
> **MCP实测修正**: 2026-03-20（全量重新录制验证）  
> **产品变更**: 2026-05-12 — **TC024 / TC025**：未登录点击 Contact 改为直接进入 **espub 访客微聊会话页**（不再在列表页弹出登录引导弹窗）；TC025 改为「微聊页浏览器后退返回列表」验证。  
> **测试范围**: 招聘列表页右侧详情面板内容展示（帖子信息）、本人帖操作（Withdraw/Edit）、非本人帖操作（Contact）、通用操作（Favourites/New tab/Share）及其跳转验证  
> **总用例数**: 28条（TC001~TC028）  
> **可自动化**: 28条 (100%)  
> **不可自动化**: 0条  
> **录制来源**: MCP Playwright 浏览器录制（2026-03-20 实测）

---

## 测试环境配置（必填）

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | es | ES 站（西班牙站） |
| 基础URL | https://es.58v5.cn | ES 测试站点 |
| 站点名称 | 西班牙站 | Spain |
| 角色 | seller | 发帖人（已登录，账号下有帖子） |
| 账号名称 | es_seller_wangyongli | 用于 session 命名 |
| 测试账号 | wangyongli@58.com | 登录邮箱 |
| 测试密码 | Qwer1234 | 登录密码 |

**说明**：
- 测试账号（wangyongli@58.com）在列表第一条展示自己发布的帖子"drast back"，用于验证本人帖操作。
- 列表中另有其他用户帖子（如"software engineer" by OKerES_wjj，帖子ID=6504835552588510），用于验证非本人帖操作。
- 目标页面：`https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`

### 本人帖判断标准（技术实现）

**接口**：`GET https://easypost.58v5.cn/crawl/imcinfo/{infoId}`  
**判断规则**：当接口返回的 `UserID == 796567146451408960` 时，该帖子为本人帖（wangyongli@58.com 账号发布）

> ⚠️ JavaScript 中该大整数会损失精度，接口响应中显示为 `796567146451408900`，实际值为 `796567146451408960`，校验时应以字符串形式对比或在服务端查询。

| 帖子 | InfoID | UserID（实际值） | 是否本人帖 |
|------|--------|----------------|-----------|
| drast back | `6522669642316510` | `796567146451408960` | ✅ 本人帖 |
| software engineer | `6504835552588510` | `796556801459984608` | ❌ 非本人帖（OKerES_wjj） |

**接口返回示例（drast back）**：
```json
{
  "InfoID": 6522669642316510,
  "Title": "drast back",
  "UserID": 796567146451408960,
  "State": 10,
  "country": "ES"
}
```

---

## 📑 目录

- [详情面板-基础信息展示](#详情面板-基础信息展示)（TC001~TC006）
- [本人帖操作-Withdraw/Edit](#本人帖操作-withdrawedit)（TC007~TC011）
- [非本人帖操作-Contact](#非本人帖操作-contact)（TC012~TC014）
- [通用操作-Favourites](#通用操作-favourites)（TC015~TC017）
- [通用操作-Share](#通用操作-share)（TC018）
- [通用操作-New tab](#通用操作-new-tab)（TC019~TC020）
- [操作按钮权限隔离](#操作按钮权限隔离)（TC021~TC022）
- [未登录权限](#未登录权限)（TC023~TC026）
- [Resume入口](#resume入口)（TC027~TC028）

---

## 测试概述

### 页面结构（MCP 2026-03-20 录制确认）

- **列表区域**（左侧）：职位卡片 feed 流，点击卡片后右侧面板同步刷新
- **详情面板**（右侧）完整结构（以本人帖"drast back"为例）：

```
┌──────────────────────────────────────────────────┐
│ drast back                         （帖子标题）    │
│ € 5,000/year                       （薪资）        │
│ EDB                                （公司名）       │
│ [Internship] [Onsite] [1 to 2 years]              │
│ [Secondary School Diploma] [AB AZUCARERA IBERIA SL]│
│                                    （职位标签组）   │
│ ┌────────────────────────────────────────────┐    │
│ │ [Withdraw] [Edit]  [Favourites] [New tab] [Share]│
│ └────────────────────────────────────────────┘    │
│                                    （操作按钮区）   │
│ Description                                       │
│ Vhugfghhfccchjgf                  （描述内容）     │
│ Updated 1 month ago               （更新时间）     │
│ 永丽 王                            （发帖人姓名）   │
│ EDB · manager                     （单位·职务）    │
│ Company                           （公司模块标题） │
│ EDB  0-9 employees                （公司信息）     │
└──────────────────────────────────────────────────┘
```

- **本人帖**操作按钮：`button "Withdraw"` + `button "Edit"` + `generic "Favourites"` + `link "New tab"` + `generic "Share"`
- **非本人帖**操作按钮：`button "Contact"` + `generic "Favourites"` + `link "New tab"` + `generic "Share"`
- **非本人帖无 Company 区域**：以"software engineer"为例，底部只显示发帖人昵称 `OKerES_wjj`

### 关键业务规则（MCP 2026-03-20 实测确认）

1. **默认展示**：首次进入列表页，右侧面板自动展示列表第一条本人帖"drast back"详情，无需点击；从其他页面跳转回来后也会默认展示第一条。
2. **Favourites（切换按钮）**：
   - 未收藏状态点击 → 出现绿色 toast（含图标），文案 **"Added to favourites"**，URL 不变
   - 已收藏状态点击 → 出现 toast（含图标），文案 **"Removed from favorites"**（注意拼写差异），URL 不变
3. **Share**：点击后出现 toast（无图标，只有文字），文案 **"Link copied"**，URL 不变
4. **Contact**：跳转至 `https://espub.58v5.cn/biz/en/chat?postId%3D{帖子ID}%26shopId%3D{店铺ID}%26shopName%3D{用户名}%26shopAvatar%3D{头像URL}%26postName%3D{帖子标题}%26shopType%3DB%26cateCode%3Djobs&needLogin=true`（URL 含多个参数）
5. **Edit**：跳转至 `https://espub.58v5.cn/biz/en/publish/job?id={帖子ID}`（如 `?id=6522669642316510`），页面标题 = "Post"
6. **Withdraw**：弹出自定义对话框（dialog 弹层，非浏览器原生 confirm），含关闭按钮（×）；标题 "Heads Up"，内容 "Do you want to withdraw the listing?"，包含 Cancel（灰底）和 OK（黑底）两个按钮；点 Cancel 关闭对话框，帖子不下架；点 ×（关闭图标）同样可关闭
7. **New tab**：点击后在**新标签页**打开帖子独立详情页，URL = `https://es.58v5.cn/en/city/cate-project-management/drast-back-6522669642316510/`，新页标题 = `drast back - OK`；原标签页 URL 不变；New tab 链接的 href 在页面初始加载时为空字符串，点击后动态解析
8. **本人/非本人**识别：系统根据登录账号与帖子发布人匹配，本人帖展示 Withdraw/Edit，非本人帖展示 Contact；切换帖子时操作按钮即时切换  
   - **技术判断依据**：调用 `GET https://easypost.58v5.cn/crawl/imcinfo/{infoId}`，当返回 `UserID == 796567146451408960` 时为本人帖（wangyongli@58.com）
9. **未登录状态**：所有帖子均展示 `Contact`，不展示 `Withdraw` / `Edit`（系统无法识别本人帖）；点击 Contact 不跳转页面，而是在当前页弹出 **"Welcome to OK.com"** 登录引导弹窗，含邮箱/手机输入框、Continue（初始 disabled）、Google/Facebook/Apple 第三方登录、× 关闭按钮

---

## 详情面板-基础信息展示

### TC001: 首次访问列表页-右侧自动展示第一条帖子详情面板（无需点击）

#### 📋 前置条件
- 已用 wangyongli@58.com 登录（session 有效）
- 确保是全新导航到列表页（非列表内部切换）

#### 🎬 执行步骤
1. 直接访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 等待页面完整加载（列表卡片和右侧面板均渲染完毕）
3. 不执行任何点击操作，观察右侧区域

#### ✅ 预期结果
- 右侧详情面板**自动**出现，无需点击任何卡片
- 面板顶部显示标题文本
- 面板内可见 "Description" 标题文字
- 面板内可见操作按钮区域（包含 Withdraw、Edit、Favourites、New tab、Share）
- 右侧详情面板区域的 DOM 结构（ref=e861 对应区域）包含帖子信息节点

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC002: 本人帖详情面板-帖子标题正确展示

#### 📋 前置条件
- 已登录，访问列表页，右侧默认展示本人帖"drast back"详情面板

#### 🎬 执行步骤
1. 访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 等待页面加载完成（右侧详情面板默认展示）
3. 读取详情面板顶部第一个文本元素的内容

#### ✅ 预期结果
- 详情面板最顶部显示帖子标题，文本精确为 **"drast back"**
- 标题字体明显大于下方薪资和公司名，为主标题样式
- 该标题与左侧列表第一条卡片标题一致

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC003: 本人帖详情面板-薪资正确展示

#### 📋 前置条件
- 已登录，右侧默认展示本人帖"drast back"详情面板

#### 🎬 执行步骤
1. 访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 等待页面加载完成
3. 读取详情面板标题下方薪资区域的文本内容

#### ✅ 预期结果
- 详情面板在标题"drast back"正下方显示薪资，文本精确为 **"€ 5,000/year"**
- 薪资格式：货币符号 + 空格 + 金额 + "/" + 周期

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC004: 本人帖详情面板-公司名正确展示（两处）

#### 📋 前置条件
- 已登录，右侧默认展示本人帖"drast back"详情面板

#### 🎬 执行步骤
1. 访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 等待页面加载完成
3. 读取详情面板中公司名区域（薪资下方）的文本
4. 向下滚动，查看底部 Company 模块中的公司信息

#### ✅ 预期结果
- 面板薪资下方显示公司名，文本精确为 **"EDB"**
- 底部 Company 区域显示 `heading "Company"`，其下方显示 **"EDB"** 和 **"0-9 employees"** 两行信息
- 发帖人信息区域显示 **"永丽 王"**（姓名）和 **"EDB · manager"**（单位·职务）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC005: 本人帖详情面板-职位信息标签完整展示（5个标签）

#### 📋 前置条件
- 已登录，右侧默认展示本人帖"drast back"详情面板

#### 🎬 执行步骤
1. 访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 等待页面加载完成
3. 查看公司名"EDB"下方的职位信息标签组区域

#### ✅ 预期结果
- 详情面板展示恰好 **5 个**职位标签，文本依次为：
  1. **"Internship"**（工作类型）
  2. **"Onsite"**（工作地点类型）
  3. **"1 to 2 years"**（工作年限）
  4. **"Secondary School Diploma"**（学历要求）
  5. **"AB AZUCARERA IBERIA SL"**（公司全称/地点）
- 标签以图标+文字形式展示（不同标签有不同前置图标）
- 标签数量不多不少，恰好5个

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC006: 本人帖详情面板-Description区域内容展示

#### 📋 前置条件
- 已登录，右侧默认展示本人帖"drast back"详情面板

#### 🎬 执行步骤
1. 访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 等待页面加载完成
3. 查看操作按钮区域下方的 Description 内容区域

#### ✅ 预期结果
- 操作按钮下方显示标题文字 **"Description"**（大号字体标题）
- "Description"下方紧跟内容段落，文本精确为 **"Vhugfghhfccchjgf"**
- Description 标题和内容均可见，无折叠遮挡

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

## 本人帖操作-Withdraw/Edit

### TC007: 本人帖详情面板-展示Withdraw和Edit按钮，不展示Contact

#### 📋 前置条件
- 已登录（wangyongli@58.com），右侧默认展示本人帖"drast back"详情面板
- 本人帖验证：`GET https://easypost.58v5.cn/crawl/imcinfo/6522669642316510` 返回 `UserID=796567146451408960`

#### 🎬 执行步骤
1. 访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 等待页面加载完成（详情面板默认展示"drast back"）
3. 查看详情面板操作按钮区域（职位标签组下方的按钮行）
4. 逐一检查各按钮的存在性和可见性

#### ✅ 预期结果
- 操作按钮区域**左侧**显示 `button "Withdraw"`，类型为 button，可点击
- 操作按钮区域**左侧**显示 `button "Edit"`，类型为 button，可点击
- 操作按钮区域**不**存在 `button "Contact"`（查询为空或不可见）
- 操作按钮区域**右侧**依次显示 `generic "Favourites"`、`link "New tab"`、`generic "Share"` 三个通用操作，均可见且可点击

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC008: 本人帖点击Edit按钮跳转到帖子编辑页

#### 📋 前置条件
- 已登录，右侧默认展示本人帖"drast back"详情面板

#### 🎬 执行步骤
1. 访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 等待页面加载完成
3. 点击详情面板中的 `button "Edit"`
4. 等待页面跳转完成（等待 networkidle 或 URL 变化）

#### ✅ 预期结果
- 当前页面**跳转**，URL 精确变为 `https://espub.58v5.cn/biz/en/publish/job?id=6522669642316510`
- 页面标题精确为 **"Post"**
- 页面显示帖子编辑表单，Job Title 输入框中预填值为 **"drast back"**
- 页面包含 `button "Continue"` 按钮（发布流程下一步按钮）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC009: 本人帖点击Withdraw按钮弹出自定义确认对话框

#### 📋 前置条件
- 已登录，右侧默认展示本人帖"drast back"详情面板，帖子处于上架状态

#### 🎬 执行步骤
1. 访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 等待页面加载完成
3. 点击详情面板中的 `button "Withdraw"`
4. 等待对话框出现

#### ✅ 预期结果
- 页面弹出**自定义**确认对话框（非浏览器原生 confirm 弹窗，是页面内 dialog 弹层）
- 对话框右上角有关闭图标按钮（×）
- 对话框标题显示 **"Heads Up"**
- 对话框正文显示 **"Do you want to withdraw the listing?"**
- 对话框底部包含 `button "Cancel"`（灰色/白色边框样式）和 `button "OK"`（黑色填充样式）
- 当前页 URL 仍为 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`（未跳转）
- 对话框出现时背景页面变暗（mask 遮罩效果）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC010: Withdraw对话框-点击Cancel关闭对话框且帖子不下架

#### 📋 前置条件
- 已登录，已点击 Withdraw 按钮，"Heads Up" 确认对话框已弹出显示

#### 🎬 执行步骤
1. 访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 点击详情面板中的 `button "Withdraw"`（确认对话框弹出）
3. 点击对话框中的 `button "Cancel"`

#### ✅ 预期结果
- "Heads Up" 确认对话框从页面上**消失**（DOM 中 dialog 节点消失或隐藏）
- 页面背景恢复正常（遮罩消失）
- 详情面板中 `button "Withdraw"` 仍然存在且可见（帖子未被下架）
- 详情面板中 `button "Edit"` 仍然存在且可见
- 当前页 URL 仍为 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`（未跳转）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC011: Withdraw对话框-点击右上角×关闭对话框

#### 📋 前置条件
- 已登录，已点击 Withdraw 按钮，"Heads Up" 确认对话框已弹出

#### 🎬 执行步骤
1. 访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 点击详情面板中的 `button "Withdraw"`（对话框弹出）
3. 点击对话框右上角的关闭图标按钮（img "close"）

#### ✅ 预期结果
- "Heads Up" 确认对话框从页面上消失
- 详情面板中 `button "Withdraw"` 和 `button "Edit"` 仍然可见
- 当前页 URL 不变

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

## 非本人帖操作-Contact

### TC012: 非本人帖详情面板-展示Contact按钮，不展示Withdraw和Edit

#### 📋 前置条件
- 已登录（wangyongli@58.com）
- 列表中存在非本人帖"software engineer"（发帖人：OKerES_wjj，帖子ID=6504835552588510）
- 非本人帖验证：`GET https://easypost.58v5.cn/crawl/imcinfo/6504835552588510` 返回 `UserID=796556801459984608`（≠ 796567146451408960）

#### 🎬 执行步骤
1. 访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 等待页面加载完成
3. 在列表中点击"software engineer"帖子卡片
4. 等待右侧详情面板内容切换完成

#### ✅ 预期结果
- 详情面板顶部标题切换为 **"software engineer"**
- 操作按钮区域左侧显示 `button "Contact"`，类型为 button，可点击
- 操作按钮区域**不**存在 `button "Withdraw"`（查询为空或不可见）
- 操作按钮区域**不**存在 `button "Edit"`（查询为空或不可见）
- 操作按钮区域右侧仍显示 `generic "Favourites"`、`link "New tab"`、`generic "Share"` 三个通用操作

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC013: 非本人帖点击Contact按钮跳转到聊天页

#### 📋 前置条件
- 已登录，右侧详情面板展示非本人帖"software engineer"（帖子ID=6504835552588510）

#### 🎬 执行步骤
1. 访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 点击"software engineer"帖子卡片，等待详情面板切换
3. 点击详情面板中的 `button "Contact"`
4. 等待页面跳转完成

#### ✅ 预期结果
- 当前页面跳转，URL 以 `https://espub.58v5.cn/biz/en/chat` 开头
- URL 中包含参数 `postId%3D6504835552588510`（帖子ID）
- URL 中包含参数 `postName%3Dsoftware+engineer`（帖子标题）
- URL 中包含参数 `shopId%3D796556801459984608`（店铺ID）
- URL 中包含参数 `shopName%3DOKerES_wjj`（发帖人用户名）
- URL 中包含参数 `shopType%3DB`（店铺类型）
- URL 末尾包含 `&needLogin=true`
- 页面标题精确为 **"Messages"**

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC014: 非本人帖详情面板-展示帖子基础信息（6个职位标签）

#### 📋 前置条件
- 已登录，点击"software engineer"帖子卡片，右侧展示其详情面板

#### 🎬 执行步骤
1. 访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 点击"software engineer"帖子卡片
3. 等待详情面板切换完毕
4. 逐一查看详情面板各信息字段

#### ✅ 预期结果
- 详情面板顶部标题文本精确为 **"software engineer"**
- 薪资显示 **"€ 5,000-10,000/year"**（范围薪资）
- 职位标签共 **6 个**，依次为：**"Part-time"**、**"Remote"**、**"Less than 1 year"**、**"Secondary School Diploma"**、**"Negotiable Salary"**、**"Spain"**
- Description 区域显示 "Description" 标题，内容文本精确为 **"software enginneer find a job"**（注意 "enginneer" 有拼写错误，为帖子实际内容）
- 更新时间显示 **"Updated 2 months ago"**
- 底部发帖人昵称显示 **"OKerES_wjj"**
- 面板**不**显示 Company 区域（无 `heading "Company"` 节点）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

## 通用操作-Favourites

### TC015: 点击Favourites（未收藏状态）-出现"Added to favourites"toast提示

#### 📋 前置条件
- 已登录，右侧详情面板展示非本人帖"software engineer"
- 确认该帖子当前处于**未收藏**状态（若已收藏，先点击一次取消收藏）

#### 🎬 执行步骤
1. 访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 点击"software engineer"帖子卡片，等待详情面板切换
3. 记录当前页面 URL（`https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`）
4. 点击详情面板中的 `generic "Favourites"` 按钮
5. 观察 toast 提示内容

#### ✅ 预期结果
- 页面出现 toast 提示（alert 弹层），**包含绿色图标**，文案精确为 **"Added to favourites"**
- toast 短暂显示后自动消失
- 当前页面 URL **不变**，仍为 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
- 页面不刷新，详情面板内容保持不变

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC016: 点击Favourites（已收藏状态）-出现"Removed from favorites"toast提示

#### 📋 前置条件
- 已登录，右侧详情面板展示任意帖子
- 确认该帖子当前处于**已收藏**状态（若未收藏，先点击一次添加收藏）

#### 🎬 执行步骤
1. 访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 点击目标帖子卡片，等待详情面板展示
3. 若帖子未收藏，先点击一次 Favourites 使其进入已收藏状态
4. 再次点击 `generic "Favourites"` 按钮（此时应为取消收藏操作）
5. 观察 toast 提示内容

#### ✅ 预期结果
- 页面出现 toast 提示（alert 弹层），**包含图标**，文案精确为 **"Removed from favorites"**（注意：英式拼写"favourites"改为美式"favorites"，两种状态文案拼写不同）
- toast 短暂显示后自动消失
- 当前页面 URL **不变**
- 页面不刷新

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC017: 本人帖点击Favourites-同样支持收藏操作

#### 📋 前置条件
- 已登录，右侧默认展示本人帖"drast back"详情面板

#### 🎬 执行步骤
1. 访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 等待页面加载完成（本人帖"drast back"默认展示）
3. 点击详情面板中的 `generic "Favourites"` 按钮

#### ✅ 预期结果
- 页面出现 toast 提示，文案为 **"Added to favourites"** 或 **"Removed from favorites"**（取决于当前收藏状态，两种结果均为正确行为）
- 当前页面 URL **不变**
- 确认本人发布的帖子也可以被自己收藏/取消收藏（功能不受本人帖/非本人帖身份限制）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

## 通用操作-Share

### TC018: 点击Share-出现"Link copied"toast提示，页面不跳转

#### 📋 前置条件
- 已登录，右侧详情面板展示任意帖子（以非本人帖"software engineer"为例）

#### 🎬 执行步骤
1. 访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 点击"software engineer"帖子卡片，等待详情面板切换
3. 记录当前页面 URL（`https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`）
4. 点击详情面板中的 `generic "Share"` 按钮
5. 观察 toast 提示

#### ✅ 预期结果
- 页面出现 toast 提示（alert 弹层），文案精确为 **"Link copied"**（无图标，仅文字）
- toast 短暂显示后自动消失
- 当前页面 URL **不变**，仍为 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
- 页面不刷新，详情面板内容保持不变
- 剪贴板中已复制帖子链接（自动化中可通过 clipboard API 验证）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

## 通用操作-New tab

### TC019: New tab链接元素存在且可见

#### 📋 前置条件
- 已登录，右侧默认展示本人帖"drast back"详情面板

#### 🎬 执行步骤
1. 访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 等待页面加载完成
3. 查看详情面板操作按钮区域中的 "New tab" 元素属性

#### ✅ 预期结果
- 详情面板操作按钮区域中存在 `link "New tab"` 元素（role=link，非 button）
- 该元素在页面上**可见**且可被点击
- 元素的 href 属性在页面初始加载时可能为空字符串（动态赋值），但元素本身存在

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC020: 点击New tab-在新标签页打开帖子独立详情页

#### 📋 前置条件
- 已登录，右侧默认展示本人帖"drast back"详情面板

#### 🎬 执行步骤
1. 访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 等待页面加载完成
3. 点击详情面板中的 `link "New tab"`
4. 等待新标签页打开并加载完成（`waitForEvent('page')` + `waitForLoadState`）

#### ✅ 预期结果
- 浏览器**新开一个标签页**（原标签页仍保持打开）
- 新标签页 URL 精确为 `https://es.58v5.cn/en/city/cate-project-management/drast-back-6522669642316510/`
- 新标签页页面标题精确为 **"drast back - OK"**
- **原标签页** URL 不变，仍为 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
- 原标签页详情面板内容保持不变

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

## 操作按钮权限隔离

### TC021: 切换帖子时详情面板操作按钮即时切换（本人帖→非本人帖）

#### 📋 前置条件
- 已登录，当前右侧展示本人帖"drast back"详情（有Withdraw/Edit，无Contact）

#### 🎬 执行步骤
1. 访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 确认右侧详情面板展示本人帖"drast back"（`button "Withdraw"` 可见，`button "Contact"` 不存在）
3. 在列表中点击非本人帖"software engineer"卡片
4. 等待右侧详情面板内容切换完成（面板标题变为"software engineer"）

#### ✅ 预期结果
- 详情面板顶部标题**从 "drast back" 切换为 "software engineer"**
- 操作按钮区域：`button "Contact"` **出现**且可见可点击
- 操作按钮区域：`button "Withdraw"` **消失**（不存在或不可见）
- 操作按钮区域：`button "Edit"` **消失**（不存在或不可见）
- `generic "Favourites"`、`link "New tab"`、`generic "Share"` 三个通用操作**仍然存在**且可见

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC022: 切换帖子时详情面板操作按钮即时切换（非本人帖→本人帖）

#### 📋 前置条件
- 已登录，当前右侧展示非本人帖"software engineer"详情（有Contact，无Withdraw/Edit）

#### 🎬 执行步骤
1. 访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 点击"software engineer"卡片，确认详情面板展示该帖子（`button "Contact"` 可见）
3. 点击本人帖"drast back"卡片
4. 等待右侧详情面板内容切换完成

#### ✅ 预期结果
- 详情面板顶部标题**从 "software engineer" 切换为 "drast back"**
- 操作按钮区域：`button "Withdraw"` **出现**且可见可点击
- 操作按钮区域：`button "Edit"` **出现**且可见可点击
- 操作按钮区域：`button "Contact"` **消失**（不存在或不可见）
- `generic "Favourites"`、`link "New tab"`、`generic "Share"` 三个通用操作仍然存在

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

## 未登录权限

### TC023: 未登录状态-详情面板显示Contact按钮，不显示Withdraw和Edit

#### 📋 前置条件
- 未登录状态（清除全部 Cookie，右上角显示 "Log in / Register" 按钮）
- 访问列表页，右侧默认展示第一条帖子"drast back"详情面板

#### 🎬 执行步骤
1. 清除所有 Cookie（`context.clearCookies()`）后访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 等待页面加载完成（右上角出现 "Log in / Register" 文字，确认未登录状态）
3. 处理 Cookie 同意弹窗（点击 "Only essential" 或 "Accept all"）
4. 查看右侧详情面板操作按钮区域

#### ✅ 预期结果
- 右上角导航显示 **"Log in / Register"** 按钮（而非用户昵称），确认未登录状态
- 右侧详情面板默认展示第一条帖子"drast back"的信息（标题、薪资、公司名等正常展示）
- 操作按钮区域**显示** `button "Contact"`，可见且可点击
- 操作按钮区域**不显示** `button "Withdraw"`（不存在）
- 操作按钮区域**不显示** `button "Edit"`（不存在）
- 操作按钮区域仍显示 `generic "Favourites"`、`link "New tab"`、`generic "Share"` 三个通用操作

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 权限测试
- **UI自动化**: ✅ 可自动化（通过 `clearCookies()` 模拟未登录，不依赖 Session 复用）

---

### TC024: 未登录状态-点击Contact进入访客微聊会话页（espub）

#### 📋 前置条件
- 未登录状态（Cookie 已清除，右上角显示 "Log in / Register"）
- 右侧详情面板可见 Contact 按钮

#### 🎬 执行步骤
1. 清除所有 Cookie 后访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 等待页面加载，处理 Cookie 同意弹窗
3. 点击详情面板中的 `button "Contact"`

#### ✅ 预期结果
- 页面**跳转**离开招聘列表：当前 URL 落在 **`espub.58v5.cn`** 业务域下的**访客微聊**路径（实测为 `.../biz/en/chat-guest-server1/...`，以环境为准；须为微聊/会话类路径，而非列表页）
- URL 查询参数中含 **`needLogin=true`**（表示访客会话场景下仍可引导登录）
- **不再**在 ES 列表页上弹出原「Welcome to OK.com」登录引导弹层（与历史 MCP 录制行为不同，以当前产品为准）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 权限测试
- **UI自动化**: ✅ 可自动化

---

### TC025: 未登录状态-访客微聊页浏览器后退返回列表，Contact仍可用

#### 📋 前置条件
- 未登录状态（Cookie 已清除）
- 已完成「列表页 → 点击 Contact → 进入访客微聊页」（与 TC024 一致）

#### 🎬 执行步骤
1. 清除所有 Cookie 后访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 处理 Cookie 同意弹窗
3. 点击详情面板中的 `button "Contact"`，等待进入 espub 访客微聊页
4. 使用浏览器**后退**（`history.back` / 工具栏后退）返回上一页

#### ✅ 预期结果
- 后退后当前 URL **回到**招聘列表页（包含 `es.58v5.cn` 与 `cate-jobs`，与 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs` 一致或等价）
- 右侧详情面板区域 **`button "Contact"`** 仍可见、可再次点击（与未登录权限一致）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 权限测试 / 导航回归
- **UI自动化**: ✅ 可自动化

---

### TC026: 未登录状态-点击任意帖子均显示Contact按钮

#### 📋 前置条件
- 未登录状态（Cookie 已清除）

#### 🎬 执行步骤
1. 清除所有 Cookie 后访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 等待页面加载，处理 Cookie 同意弹窗
3. 分别点击不同帖子卡片（包含其他用户发布的帖子，如"software engineer"）
4. 每次点击后查看右侧详情面板操作按钮区域

#### ✅ 预期结果
- 未登录状态下，无论点击哪条帖子，详情面板操作按钮区域**均显示 Contact**
- 任何帖子均**不显示 Withdraw** 和 **Edit** 按钮
- 系统无法区分"本人帖"与"非本人帖"（因为没有登录身份），统一展示 Contact
- Favourites、New tab、Share 三个通用操作在所有帖子均正常展示

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 权限测试
- **UI自动化**: ✅ 可自动化

---

## Resume入口

### TC027: 详情面板-Resume入口可见

#### 📋 前置条件
- 已登录（wangyongli@58.com），右侧默认展示本人帖"drast back"详情面板

#### 🎬 执行步骤
1. 访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 等待页面加载完成（右侧详情面板默认展示）
3. 查看详情面板侧边区域的 Resume 入口是否可见

#### ✅ 预期结果
- 详情面板右侧边栏中存在 **"Resume"** 文字入口（`generic "Resume"` 节点）
- Resume 入口处于可见、可点击状态

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC028: 点击Resume入口-跳转到简历填写页

#### 📋 前置条件
- 已登录（wangyongli@58.com），右侧默认展示帖子详情面板，Resume 入口可见

#### 🎬 执行步骤
1. 访问 `https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs`
2. 等待页面加载完成
3. 点击详情面板侧边的 **"Resume"** 入口
4. 等待页面跳转完成

#### ✅ 预期结果
- 当前页面**跳转**，URL 精确变为 `https://espub.58v5.cn/biz/en/resume/add`
- 跳转目标页面标题为 **"Jobs"**
- 页面展示简历填写表单，包含 **"Personal Information"** 标题区域

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

## 测试统计

### 用例概览
- 总用例数: 28条（TC001~TC028，新增 TC027/TC028 Resume 入口验证）
- 可自动化: 28条 (100%)
- 不可自动化: 0条 (0%)

### 按优先级分布
| 优先级 | 总数 | 可自动化 | 自动化率 |
|--------|------|---------|---------|
| P0 | 8 | 8 | 100% |
| P1 | 15 | 15 | 100% |
| P2 | 2 | 2 | 100% |
| P3 | 0 | 0 | - |

---

## MCP实测修正记录（2026-03-20 全量重录）

| 用例 | 修正/扩展内容 |
|------|-------------|
| TC001 | 步骤明确"不执行任何点击操作"；预期结果增加：按钮区域可见（Withdraw/Edit/Favourites/New tab/Share）、DOM节点验证描述 |
| TC002 | 预期结果增加：标题字体样式描述、与列表卡片一致性验证 |
| TC003 | 预期结果增加：薪资格式说明（货币符号+空格+金额+"/"+周期） |
| TC004 | **重要修正**：预期结果补充发帖人信息区（永丽 王 + EDB · manager）；明确"两处"公司名展示位置 |
| TC005 | 预期结果明确标签数量为"恰好5个"，增加"标签以图标+文字形式展示"描述 |
| TC006 | 预期结果增加"无折叠遮挡"验证点 |
| TC007 | 预期结果增加：Contact 查询为空或不可见的验证方式 |
| TC008 | **细节扩展**：预期结果增加 Job Title 输入框预填值验证（"drast back"）、Continue 按钮存在性验证 |
| TC009 | **重大修正**：明确为"自定义 dialog 弹层"非原生 confirm；增加关闭图标（×）存在性、遮罩效果描述；Cancel 按钮样式描述（灰色）、OK 按钮样式（黑色填充） |
| TC010 | 预期结果增加：DOM 节点消失验证（"dialog 节点消失或隐藏"）、遮罩消失验证 |
| **TC011** | **新增**：验证点击×关闭对话框行为 |
| TC012 | 步骤增加"等待详情面板内容切换完成"；预期结果增加 Withdraw/Edit 查询为空或不可见的验证方式 |
| TC013 | **重大修正**：URL 参数从2个扩展到7个（增加 shopId、shopName、shopAvatar、shopType、cateCode），增加 `&needLogin=true` 参数验证 |
| TC014 | **重大修正**：职位标签从5个更正为6个（增加"Spain"标签）；Description 内容注明"enginneer"拼写错误为帖子实际内容 |
| TC015 | **重大修正**：明确"未收藏状态"前置条件；预期结果 toast 包含绿色图标（与 Share 的无图标 toast 区分）；标注"Added to favourites"英式拼写 |
| **TC016** | **新增**：验证已收藏状态点击的"Removed from favorites"toast（美式拼写），并说明两种状态文案拼写差异 |
| TC017 | **重命名**：原 TC016 改为 TC017；预期结果改为"两种结果均为正确行为"的验证方式 |
| TC018 | **重命名**：原 TC017 改为 TC018；预期结果增加"无图标仅文字"的 toast 区分说明；增加剪贴板内容验证建议 |
| TC019 | 预期结果增加 href 动态赋值说明（"初始加载时可能为空字符串"） |
| TC020 | **重大修正**：原标注"不可自动化"改为**可自动化**；步骤改用 `waitForEvent('page')` + `waitForLoadState` 方式；预期结果精确到完整新标签页 URL 和标题 |
| TC021 | **重命名**：原 TC020 改为 TC021 |
| **TC022** | **新增**：反向切换验证（非本人帖→本人帖），确保双向切换均正确 |
| **TC023** | **重大修正**：从"不可自动化"改为**可自动化**（通过 clearCookies 模拟）；明确未登录下 Contact 可见、Withdraw/Edit 不可见的具体预期结果 |
| **TC024** | **产品变更（2026-05-12）**：未登录点击 Contact **跳转 espub 访客微聊**；校验域名、微聊路径、`needLogin=true`；不再校验列表页登录弹窗 |
| **TC025** | **产品变更（2026-05-12）**：由「弹窗×关闭」改为 **访客微聊页浏览器后退** 返回列表，Contact 仍可见 |
| **TC026** | **新增**：未登录状态下任意帖子均统一展示 Contact，无 Withdraw/Edit 的系统行为验证 |
| **TC027** | **新增**：MCP 实测确认 Resume 入口在详情面板侧边可见（`generic "Resume"` 节点） |
| **TC028** | **新增**：MCP 实测确认点击 Resume 入口跳转至 `https://espub.58v5.cn/biz/en/resume/add`，标题含 "Jobs" |
