# OK.com - 金刚位导航区 测试用例

> **生成时间**: 2026-03-24  
> **探测方式**: Playwright MCP 实测（阶段三已完成）+ 本地 Playwright 复核 URL/标题/登录态差异  
> **测试范围**: 纽约站首页（`city-new-york1`）搜索框下方的金刚位（图标+文案核心业务入口）  
> **总用例数**: 17 条  
> **可自动化**: 17 条（100%）  
> **实测视口**: 宽屏 **1440×900**

---

## 测试环境配置

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | us | 美国站 |
| 基础URL | https://us.ok.com/en/city-new-york1/ | 纽约城市页（英文入口） |
| 站点名称 | US OK.com | 用于日志展示 |
| 角色 | visitor / buyer | 访客（未登录）/ 买家（已登录） |
| 账号名称 | shenchang_buyer_us | session 命名 |
| 测试账号 | shenchang@58.com | 登录邮箱（实测使用） |
| 测试密码 | 123456Tt | 登录密码 |

**说明**：登录弹层若被 Cookie 条遮挡，需先关闭/接受 Cookie 后再点「Log in」。截图证据目录：`web-qa-brain/screenshots/`。

---

## 截图证据索引

| 编号 | 文件（相对仓库根目录） | 主要关联用例 |
|------|------------------------|--------------|
| S01 | `web-qa-brain/screenshots/kingkong-nyc-guest-overview-20260324.png` | TC001 |
| S02 | `web-qa-brain/screenshots/kingkong-guest-marketplace-20260324.png` | TC002 |
| S03 | `web-qa-brain/screenshots/kingkong-buyer-marketplace-20260324.png` | TC003 |
| S04 | `web-qa-brain/screenshots/kingkong-guest-free-20260324.png` | TC004 |
| S05 | `web-qa-brain/screenshots/kingkong-buyer-free-20260324.png` | TC005 |
| S06 | `web-qa-brain/screenshots/kingkong-guest-jobs-20260324.png` | TC006 |
| S07 | `web-qa-brain/screenshots/kingkong-buyer-jobs-20260324.png` | TC007 |
| S08 | `web-qa-brain/screenshots/kingkong-guest-property-20260324.png` | TC008 |
| S09 | `web-qa-brain/screenshots/kingkong-buyer-property-20260324.png` | TC009 |
| S10 | `web-qa-brain/screenshots/kingkong-guest-cars-20260324.png` | TC010 |
| S11 | `web-qa-brain/screenshots/kingkong-buyer-cars-20260324.png` | TC011 |
| S12 | `web-qa-brain/screenshots/kingkong-guest-services-20260324.png` | TC012 |
| S13 | `web-qa-brain/screenshots/kingkong-buyer-services-20260324.png` | TC013 |
| S14 | `web-qa-brain/screenshots/kingkong-guest-community-20260324.png` | TC014 |
| S15 | `web-qa-brain/screenshots/kingkong-buyer-community-20260324.png` | TC015 |
| S16 | `web-qa-brain/screenshots/kingkong-guest-all-listpage-20260324.png` | TC016 |
| S17 | `web-qa-brain/screenshots/kingkong-buyer-nyc-home-20260324.png` | 买家流程上下文（可选） |
| S18 | `web-qa-brain/screenshots/kingkong-buyer-all-listpage-20260324.png` | TC017 |

---

## 阶段一：Application Overview（实测摘要）

### 功能定位

金刚位位于首页首屏搜索框下方，以图标+文案提供 **Marketplace、Free、Jobs、Property、Cars、Services、Community** 七类业务入口，以及 **All** 全部分类聚合页入口；点击后整页跳转至对应列表或导购页。

### 用户角色

- **visitor**：顶栏显示 **「Log in / Register」**；金刚位八个入口均可见、可点击。  
- **buyer**：使用同一套金刚位；顶栏展示名实测为 **「OKerUS_t8bete9」**（与邮箱不同）。

### 业务规则与差异（均已实测）

- **Jobs 与登录态相关（重要）**：在纽约首页从金刚位 **点击「Jobs Jobs」** 时，**访客**落地 **纽约** 职位列表（URL 含 `city-new-york1`，标题含 **「12K+ Jobs in the New York」**）；**已登录买家**落地 **全美** 职位列表（URL 为 `https://us.ok.com/en/city/cate-jobs/?iconSource=jobs`，标题含 **「159K+ Jobs in the US」**）。面包屑 **Home** 链接也不同：纽约列表为 `https://us.ok.com/en/city-new-york1/`，全美列表为 `https://us.ok.com/en/`。  
- **Jobs 链的 href 与点击行为**：访客态快照里金刚位「Jobs」的 `href` 可能展示为 `https://us.ok.com/en/city/cate-jobs/`；若在地址栏**直接打开**该 URL，会进入全美列表标题（**159K+ Jobs in the US**），与从纽约首页**点击**金刚位进入纽约列表（**12K+ Jobs in the New York**）不一致 ✅ 实测（自动化应用 **click** 校验落地 URL，勿仅用 `href` 做断言）。  
- **其余金刚位（Marketplace / Free / Property / Cars / Services / Community / All）**：访客与已登录买家在实测中 **URL 与页面标题一致**（同页复测）。

### 页面状态枚举（已实测）

1. 纽约首页：金刚区八个入口 + 下方 Top Picks 等模块。  
2. 各分类落地页：顶栏 Browse、搜索框、分类面包屑/主标题、列表或导购内容。  
3. **All** 落地页（`listpage`）：展示 **Marketplace、Jobs** 等大类及下级分类文案入口（如 Collectibles & Art、Accounting 等）。

---

## 阶段二：测试计划

| 模块 | 优先级 | 用例范围 |
|------|--------|----------|
| 金刚区展示 | P0 | 访客首页八个入口可见性、首页标题 |
| Marketplace | P0 | 访客/买家点击跳转、标题、关键元素 |
| Free | P0 | 同上 |
| Jobs | P0 | 同上 + **登录态 URL/标题/Home 差异** |
| Property | P0 | 同上 |
| Cars | P0 | 同上 |
| Services | P0 | 同上 |
| Community | P0 | 同上 |
| All | P0 | 同上（城市分类聚合页） |

---

## 阶段三：模块与用例（逐条实测）

### 模块 A：金刚区展示（访客）

### TC001: 访客在纽约首页应展示完整金刚位入口

#### 📋 前置条件

- 未登录。  
- 访问 https://us.ok.com/en/city-new-york1/。  
- 视口 1440×900。

#### 🎬 执行步骤

1. 打开上述纽约首页。  
2. 在搜索框下方观察金刚位区域。

#### ✅ 预期结果

- 金刚位依次可见可点击入口文案 **「Marketplace」「Free」「Jobs」「Property」「Cars」「Services」「Community」「All」**（各含图标与重复可读名称，如「Marketplace Marketplace」）✅ 实测  
- 页面标题为 **New York Classified Information Website - OK** ✅ 实测  
- **证据**：`browser_snapshot` + `web-qa-brain/screenshots/kingkong-nyc-guest-overview-20260324.png`（S01）

#### 📊 用例属性

- **优先级**: P0  
- **测试类型**: 正向 / UI  
- **UI自动化**: ✅ 可自动化  

---

### 模块 B：Marketplace

### TC002: 访客点击金刚位 Marketplace 应进入纽约 Marketplace 导购页

#### 📋 前置条件

- 未登录，位于 https://us.ok.com/en/city-new-york1/。

#### 🎬 执行步骤

1. 点击金刚位 **「Marketplace Marketplace」**。

#### ✅ 预期结果

- URL 为 `https://us.ok.com/en/city-new-york1/cate-marketplace/?iconSource=marketplace` ✅ 实测  
- 页面标题为 **425 Marketplace in the New York: The Ultimate Buyers Guide (2026) | ok.com** ✅ 实测  
- 导航区内可见 **「Home」** 链向 `https://us.ok.com/en/city-new-york1/`，主文案区域可见 **「Marketplace in New York」** 与 **「Best Match」** 等列表控件 ✅ 实测  
- 页面 **h1** 为 **Marketplace** ✅ 实测  
- **证据**：`browser_snapshot` + `web-qa-brain/screenshots/kingkong-guest-marketplace-20260324.png`（S02）

#### 📊 用例属性

- **优先级**: P0  
- **测试类型**: 正向  
- **UI自动化**: ✅ 可自动化  

---

### TC003: 买家点击金刚位 Marketplace 行为应与访客一致

#### 📋 前置条件

- 已使用 **shenchang@58.com** / **123456Tt** 登录。  
- 位于 https://us.ok.com/en/city-new-york1/，顶栏展示 **「OKerUS_t8bete9」**。

#### 🎬 执行步骤

1. 点击金刚位 **「Marketplace Marketplace」**。

#### ✅ 预期结果

- URL 为 `https://us.ok.com/en/city-new-york1/cate-marketplace/?iconSource=marketplace` ✅ 实测  
- 页面标题为 **425 Marketplace in the New York: The Ultimate Buyers Guide (2026) | ok.com** ✅ 实测  
- 可见 **「Marketplace in New York」** 与 **「Best Match」** ✅ 实测  
- 页面 **h1** 为 **Marketplace** ✅ 实测  
- **证据**：`web-qa-brain/screenshots/kingkong-buyer-marketplace-20260324.png`（S03）

#### 📊 用例属性

- **优先级**: P0  
- **测试类型**: 正向 / 权限  
- **UI自动化**: ✅ 可自动化  

---

### 模块 C：Free

### TC004: 访客点击金刚位 Free 应进入纽约 Free（0 价筛选）列表

#### 📋 前置条件

- 未登录，位于纽约首页。

#### 🎬 执行步骤

1. 点击金刚位 **「Free Free」**。

#### ✅ 预期结果

- URL 为 `https://us.ok.com/en/city-new-york1/cate/?lowestPrice=0&highestPrice=0` ✅ 实测  
- 页面标题为 **New York Classifieds Website - OK** ✅ 实测  
- 页面可见一级标题 **「All」**、可见 **「Filter」** 文案（筛选区域）✅ 实测  
- **证据**：`web-qa-brain/screenshots/kingkong-guest-free-20260324.png`（S04）

#### 📊 用例属性

- **优先级**: P0  
- **测试类型**: 正向  
- **UI自动化**: ✅ 可自动化  

---

### TC005: 买家点击金刚位 Free 应与访客一致

#### 📋 前置条件

- 已登录买家，位于纽约首页。

#### 🎬 执行步骤

1. 点击金刚位 **「Free Free」**。

#### ✅ 预期结果

- URL 为 `https://us.ok.com/en/city-new-york1/cate/?lowestPrice=0&highestPrice=0` ✅ 实测  
- 页面标题为 **New York Classifieds Website - OK** ✅ 实测  
- 可见 **「All」** 标题与 **「Filter」** ✅ 实测  
- **证据**：`web-qa-brain/screenshots/kingkong-buyer-free-20260324.png`（S05）

#### 📊 用例属性

- **优先级**: P0  
- **测试类型**: 正向  
- **UI自动化**: ✅ 可自动化  

---

### 模块 D：Jobs（登录态差异）

### TC006: 访客点击金刚位 Jobs 应进入纽约职位列表

#### 📋 前置条件

- 未登录，位于纽约首页。

#### 🎬 执行步骤

1. 点击金刚位 **「Jobs Jobs」**。

#### ✅ 预期结果

- URL 为 `https://us.ok.com/en/city-new-york1/cate-jobs/?iconSource=jobs` ✅ 实测  
- 页面标题为 **12K+ Jobs in the New York: The Ultimate Buyers Guide (2026) | ok.com** ✅ 实测  
- 导航区 **「Home」** 链向 `https://us.ok.com/en/city-new-york1/` ✅ 实测  
- 页面 **h1** 为 **Jobs**，可见 **Search** 相关搜索框 ✅ 实测  
- **证据**：`web-qa-brain/screenshots/kingkong-guest-jobs-20260324.png`（S06）

#### 📊 用例属性

- **优先级**: P0  
- **测试类型**: 正向  
- **UI自动化**: ✅ 可自动化  

---

### TC007: 买家点击金刚位 Jobs 应进入全美职位列表（与访客不同）

#### 📋 前置条件

- 已登录买家，位于纽约首页。

#### 🎬 执行步骤

1. 点击金刚位 **「Jobs Jobs」**。

#### ✅ 预期结果

- URL 为 `https://us.ok.com/en/city/cate-jobs/?iconSource=jobs`（**不含** `city-new-york1`）✅ 实测  
- 页面标题为 **159K+ Jobs in the US: The Ultimate Buyers Guide (2026) | ok.com** ✅ 实测  
- 导航区 **「Home」** 链向 `https://us.ok.com/en/`（**非** 纽约城市首页）✅ 实测  
- 页面 **h1** 为 **Jobs** ✅ 实测  
- **证据**：`web-qa-brain/screenshots/kingkong-buyer-jobs-20260324.png`（S07）

#### 📊 用例属性

- **优先级**: P0  
- **测试类型**: 正向 / 权限  
- **UI自动化**: ✅ 可自动化  

---

### 模块 E：Property

### TC008: 访客点击金刚位 Property 应进入纽约房产 For Sale 列表

#### 📋 前置条件

- 未登录，位于纽约首页。

#### 🎬 执行步骤

1. 点击金刚位 **「Property Property」**。

#### ✅ 预期结果

- URL 为 `https://us.ok.com/en/city-new-york1/cate-property/?iconSource=buy` ✅ 实测  
- 页面标题为 **3606 For Sale in New York lowest at $1.0+ | ok.com** ✅ 实测  
- 面包屑区域可见 **「Home」**、**「Property」**、**「For Sale」**（**h1** 为 **For Sale**）✅ 实测  
- **证据**：`web-qa-brain/screenshots/kingkong-guest-property-20260324.png`（S08）

#### 📊 用例属性

- **优先级**: P0  
- **测试类型**: 正向  
- **UI自动化**: ✅ 可自动化  

---

### TC009: 买家点击金刚位 Property 应与访客一致

#### 📋 前置条件

- 已登录买家，位于纽约首页。

#### 🎬 执行步骤

1. 点击金刚位 **「Property Property」**。

#### ✅ 预期结果

- URL 为 `https://us.ok.com/en/city-new-york1/cate-property/?iconSource=buy` ✅ 实测  
- 页面标题为 **3606 For Sale in New York lowest at $1.0+ | ok.com** ✅ 实测  
- 可见 **For Sale** 面包屑与 **h1** ✅ 实测  
- **证据**：`web-qa-brain/screenshots/kingkong-buyer-property-20260324.png`（S09）

#### 📊 用例属性

- **优先级**: P0  
- **测试类型**: 正向  
- **UI自动化**: ✅ 可自动化  

---

### 模块 F：Cars

### TC010: 访客点击金刚位 Cars 应进入纽约车辆列表

#### 📋 前置条件

- 未登录，位于纽约首页。

#### 🎬 执行步骤

1. 点击金刚位 **「Cars Cars」**。

#### ✅ 预期结果

- URL 为 `https://us.ok.com/en/city-new-york1/cate-cars/?iconSource=cars` ✅ 实测  
- 页面标题为 **449 Cars in the New York: The Ultimate Buyers Guide (2026) | ok.com** ✅ 实测  
- 页面 **h1** 为 **Cars** ✅ 实测  
- **证据**：`web-qa-brain/screenshots/kingkong-guest-cars-20260324.png`（S10）

#### 📊 用例属性

- **优先级**: P0  
- **测试类型**: 正向  
- **UI自动化**: ✅ 可自动化  

---

### TC011: 买家点击金刚位 Cars 应与访客一致

#### 📋 前置条件

- 已登录买家，位于纽约首页。

#### 🎬 执行步骤

1. 点击金刚位 **「Cars Cars」**。

#### ✅ 预期结果

- URL 为 `https://us.ok.com/en/city-new-york1/cate-cars/?iconSource=cars` ✅ 实测  
- 页面标题为 **449 Cars in the New York: The Ultimate Buyers Guide (2026) | ok.com** ✅ 实测  
- 页面 **h1** 为 **Cars** ✅ 实测  
- **证据**：`web-qa-brain/screenshots/kingkong-buyer-cars-20260324.png`（S11）

#### 📊 用例属性

- **优先级**: P0  
- **测试类型**: 正向  
- **UI自动化**: ✅ 可自动化  

---

### 模块 G：Services

### TC012: 访客点击金刚位 Services 应进入纽约服务列表

#### 📋 前置条件

- 未登录，位于纽约首页。

#### 🎬 执行步骤

1. 点击金刚位 **「Services Services」**。

#### ✅ 预期结果

- URL 为 `https://us.ok.com/en/city-new-york1/cate-services/?iconSource=services` ✅ 实测  
- 页面标题为 **New York Services Business Information - OK** ✅ 实测  
- 页面 **h1** 为 **Services** ✅ 实测  
- **证据**：`web-qa-brain/screenshots/kingkong-guest-services-20260324.png`（S12）

#### 📊 用例属性

- **优先级**: P0  
- **测试类型**: 正向  
- **UI自动化**: ✅ 可自动化  

---

### TC013: 买家点击金刚位 Services 应与访客一致

#### 📋 前置条件

- 已登录买家，位于纽约首页。

#### 🎬 执行步骤

1. 点击金刚位 **「Services Services」**。

#### ✅ 预期结果

- URL 为 `https://us.ok.com/en/city-new-york1/cate-services/?iconSource=services` ✅ 实测  
- 页面标题为 **New York Services Business Information - OK** ✅ 实测  
- 页面 **h1** 为 **Services** ✅ 实测  
- **证据**：`web-qa-brain/screenshots/kingkong-buyer-services-20260324.png`（S13）

#### 📊 用例属性

- **优先级**: P0  
- **测试类型**: 正向  
- **UI自动化**: ✅ 可自动化  

---

### 模块 H：Community

### TC014: 访客点击金刚位 Community 应进入纽约社区列表

#### 📋 前置条件

- 未登录，位于纽约首页。

#### 🎬 执行步骤

1. 点击金刚位 **「Community Community」**。

#### ✅ 预期结果

- URL 为 `https://us.ok.com/en/city-new-york1/cate-community/?iconSource=community` ✅ 实测  
- 页面标题为 **686 Community in the New York: The Ultimate Buyers Guide (2026) | ok.com** ✅ 实测  
- 页面 **h1** 为 **Community** ✅ 实测  
- **证据**：`web-qa-brain/screenshots/kingkong-guest-community-20260324.png`（S14）

#### 📊 用例属性

- **优先级**: P0  
- **测试类型**: 正向  
- **UI自动化**: ✅ 可自动化  

---

### TC015: 买家点击金刚位 Community 应与访客一致

#### 📋 前置条件

- 已登录买家，位于纽约首页。

#### 🎬 执行步骤

1. 点击金刚位 **「Community Community」**。

#### ✅ 预期结果

- URL 为 `https://us.ok.com/en/city-new-york1/cate-community/?iconSource=community` ✅ 实测  
- 页面标题为 **686 Community in the New York: The Ultimate Buyers Guide (2026) | ok.com** ✅ 实测  
- 页面 **h1** 为 **Community** ✅ 实测  
- **证据**：`web-qa-brain/screenshots/kingkong-buyer-community-20260324.png`（S15）

#### 📊 用例属性

- **优先级**: P0  
- **测试类型**: 正向  
- **UI自动化**: ✅ 可自动化  

---

### 模块 I：All（分类聚合）

### TC016: 访客点击金刚位 All 应进入纽约全部分类页

#### 📋 前置条件

- 未登录，位于纽约首页。

#### 🎬 执行步骤

1. 点击金刚位 **「All All」**。

#### ✅ 预期结果

- URL 为 `https://us.ok.com/en/city-new-york1/listpage/` ✅ 实测  
- 页面标题为 **New York Classified Information Website - OK** ✅ 实测  
- 正文区域可见大类入口文案 **「Marketplace」**、**「Jobs」** 及多级分类（如 **「Collectibles & Art」**、**「Accounting」** 等）✅ 实测  
- **证据**：`web-qa-brain/screenshots/kingkong-guest-all-listpage-20260324.png`（S16）

#### 📊 用例属性

- **优先级**: P0  
- **测试类型**: 正向  
- **UI自动化**: ✅ 可自动化  

---

### TC017: 买家点击金刚位 All 应与访客一致

#### 📋 前置条件

- 已登录买家，位于纽约首页。

#### 🎬 执行步骤

1. 点击金刚位 **「All All」**。

#### ✅ 预期结果

- URL 为 `https://us.ok.com/en/city-new-york1/listpage/` ✅ 实测  
- 页面标题为 **New York Classified Information Website - OK** ✅ 实测  
- 可见 **「Marketplace」**、**「Jobs」** 等分类入口 ✅ 实测  
- **证据**：`web-qa-brain/screenshots/kingkong-buyer-all-listpage-20260324.png`（S18）

#### 📊 用例属性

- **优先级**: P0  
- **测试类型**: 正向  
- **UI自动化**: ✅ 可自动化  

---

## 测试统计

| 优先级 | 总数 | 可自动化 |
|--------|------|---------|
| P0 | 17 | 17 |
| P1 | 0 | 0 |
| P2 | 0 | 0 |
| P3 | 0 | 0 |
| **合计** | **17** | **17 (100%)** |

实测覆盖率：100%（预期结果均标 **✅ 实测**；Jobs 数量级文案以探测当日页面标题为准，线上可能随数据变化）。
