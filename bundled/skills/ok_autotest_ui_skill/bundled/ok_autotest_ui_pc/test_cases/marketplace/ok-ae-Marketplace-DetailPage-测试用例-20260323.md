# OK AE站 - Marketplace 商品详情页测试用例

> **生成时间**: 2026-03-23  
> **MCP实测依据**: 2026-03-23（列表筛选 + Online/Offline 详情页真实录制）  
> **测试范围**: AE站 Marketplace 列表页 → Transaction（Online/Offline）筛选 → 商品详情页（含地图、推荐、收藏/分享、卖家与操作按钮差异）  
> **总用例数**: 44条  
> **可自动化**: 43条（TC041 依赖造数；TC036 面包屑需补充稳定 locator）

---

## 测试环境配置（必填）

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | ae | 阿联酋站 |
| 基础URL | https://ae.58v5.cn | 测试站点地址 |
| 站点名称 | 阿联酋站 | 可选 |
| 角色 | buyer | 买家角色（详情页亦可能展示「自己的 listing」操作项，取决于数据归属） |
| 账号名称 | marketplace_detail_buyer_ae | 用于 session 命名 |
| 测试账号 | wangyongli@58.com | 登录邮箱 |
| 测试密码 | Qwer1234 | 登录密码 |

**说明**：此配置将被 playwright-test-generator 用于生成自动化脚本。若「自己的 listing」用例依赖固定数据，需保证测试账号下存在对应 Online 商品或改用数据工厂创建。

---

## 📑 目录

- [测试概述](#测试概述)
- [A. 列表页与 Transaction 筛选](#a-列表页与-transaction-筛选)（TC001–TC007）
- [B. Online 详情页元素与交互](#b-online-详情页元素与交互)（TC008–TC018、TC042–TC043）
- [C. Offline 详情页元素与交互](#c-offline-详情页元素与交互)（TC019–TC029、TC044）
- [D. Online / Offline 差异与对照](#d-online--offline-差异与对照)（TC030–TC033）
- [E. 地图、推荐、导航与边界](#e-地图推荐导航与边界)（TC034–TC041）
- [覆盖度与 MCP 实测摘要](#覆盖度与-mcp-实测摘要)

---

## 测试概述

### 页面入口（MCP 实测路径）

1. 已登录 AE 站账号（`wangyongli@58.com`）
2. 直接打开列表页：`https://ae.58v5.cn/en/city-abu-dhabi/cate-marketplace/`
3. 通过 **Transaction** 筛选切换 **Online** / **Offline**，点击 **Confirm** 应用
4. 点击商品标题链接进入详情页

### MCP 录制核心选择器（JavaScript / Playwright）

```js
// 导航到 marketplace 列表页
await page.goto('https://ae.58v5.cn/en/city-abu-dhabi/cate-marketplace/');

// Transaction → Online
await page.getByText('Transaction', { exact: true }).click();
await page.getByText('Online', { exact: true }).click();
await page.getByRole('button', { name: 'Confirm' }).click();

// 进入 Online 示例商品详情
await page.getByRole('link', { name: 'iPhone 12 Pro' }).click();

// 在列表筛选区从 Online 切到 Offline（MCP 实测序列）
await page.locator('#istPageFilterArea').getByText('Online').click();
await page.getByText('Online').nth(3).click();
await page.getByText('Offline', { exact: true }).click();
await page.getByRole('button', { name: 'Confirm' }).click();

// 进入 Offline 示例商品详情
await page.getByRole('link', { name: 'Bedding Set - No delivery' }).click();
```

### Online 详情页关键信息（✅ 实测）

| 项 | 实测值 |
|----|--------|
| 示例 URL | `https://ae.58v5.cn/en/city-abu-dhabi/cate-apple3/iphone%2B12%2Bpro%2Bmax-2034228644318138369/` |
| 价格 | AED 367 |
| 配送标签 | 展示 **Free Delivery** |
| 位置文案 | ADCB ATM - Emirates Center for Research & Strategies Study |
| 取货文案 | 展示 **Available for Pickup** |
| 卖家 | OKer_wangyongli（Verified User，417 listings） |
| 操作按钮（自己的 listing） | **Withdraw**、**Edit** |
| 区块 | Description、Location（含 **Show map**）、**You may also like** |
| 顶栏操作 | **Favourites**、**Share** |

### Offline 详情页关键信息（✅ 实测）

| 项 | 实测值 |
|----|--------|
| 示例 URL | `https://ae.58v5.cn/en/city-abu-dhabi/cate-bedroom-furniture/bedding-set-no-delivery-required-6571384177830110/` |
| 价格 | AED 150 |
| 配送标签 | **无** Free Delivery |
| 位置文案 | United Arab Emirates（更通用） |
| 取货文案 | **无** Available for Pickup |
| 卖家 | keerisbest2293939393（115 listings） |
| 操作按钮（别人的 listing） | **Contact** |
| 其他按钮 | **Sell Similar** |
| 条件标签 | Excellent |
| 区块 | Description、Location（含 **Show map**）、**You may also like** |
| 顶栏操作 | **Favourites**、**Share** |

---

## 测试用例

## A. 列表页与 Transaction 筛选

### TC001: 直达 Marketplace 列表页-URL 与基础布局

#### 📋 前置条件
- 已登录 AE 站账号（wangyongli@58.com）

#### 🎬 执行步骤
1. 执行导航：
```js
await page.goto('https://ae.58v5.cn/en/city-abu-dhabi/cate-marketplace/');
```
2. 等待列表区域加载完成，观察是否存在筛选区（含 `#istPageFilterArea` 或同等列表筛选容器）。

#### ✅ 预期结果
- 页面成功打开，URL 为 Marketplace 列表路径（✅ 实测：`.../cate-marketplace/`）
- 列表区域展示商品卡片/链接，页面无致命脚本错误

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试 / 冒烟
- **UI自动化**: ✅ 可自动化

---

### TC002: Transaction 筛选-选择 Online 并 Confirm

#### 📋 前置条件
- 已登录，当前在 `https://ae.58v5.cn/en/city-abu-dhabi/cate-marketplace/`

#### 🎬 执行步骤
```js
await page.getByText('Transaction', { exact: true }).click();
await page.getByText('Online', { exact: true }).click();
await page.getByRole('button', { name: 'Confirm' }).click();
```

#### ✅ 预期结果
- Transaction 面板可打开并选中 **Online**
- 点击 **Confirm** 后筛选生效，列表刷新为 Online 商品（✅ 实测）
- 筛选区展示当前 Transaction 状态（如仍显示 Online 标签，供后续切换用例使用）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC003: Online 筛选后列表-存在可点击的商品链接

#### 📋 前置条件
- 已完成 TC002（列表处于 Online Transaction 筛选结果）

#### 🎬 执行步骤
1. 在列表中定位任意商品链接（示例实测：`iPhone 12 Pro`）
2. 断言 `getByRole('link', { name: 'iPhone 12 Pro' })` 可见。

#### ✅ 预期结果
- 至少一条商品 `link` 可见且可点击（✅ 实测：iPhone 12 Pro）
- 卡片/行内展示价格、位置等与列表设计一致（与详情页抽样交叉验证）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: UI测试 / 列表数据
- **UI自动化**: ✅ 可自动化

---

### TC004: 从列表点击 Online 商品进入详情页

#### 📋 前置条件
- 列表已应用 Online Transaction 筛选（TC002）

#### 🎬 执行步骤
```js
await page.getByRole('link', { name: 'iPhone 12 Pro' }).click();
```

#### ✅ 预期结果
- 页面跳转至商品详情页，URL 含分类 slug 与商品 slug/id（✅ 实测路径见概述表）
- 详情页主标题/价格区域加载完成

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试 / 导航
- **UI自动化**: ✅ 可自动化

---

### TC005: 列表筛选区-从 Online 切换为 Offline 并 Confirm

#### 📋 前置条件
- 当前在 Marketplace 列表页且筛选为 Online；或从详情返回列表后仍保留筛选上下文（按产品实现二选一验证）

#### 🎬 执行步骤
```js
await page.locator('#istPageFilterArea').getByText('Online').click();
await page.getByText('Online').nth(3).click();
await page.getByText('Offline', { exact: true }).click();
await page.getByRole('button', { name: 'Confirm' }).click();
```

#### ✅ 预期结果
- 面板中可选中 **Offline**（✅ 实测）
- **Confirm** 后列表刷新为 Offline 结果
- `#istPageFilterArea` 内展示与 Offline 一致的筛选展示（文案/标签以线上为准）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试 / 筛选切换
- **UI自动化**: ✅ 可自动化（注意：`getByText('Online').nth(3)` 依赖 DOM 顺序，若改版需改为 `getByRole`/`data-testid`）

---

### TC006: Offline 筛选后列表-存在可点击的商品链接

#### 📋 前置条件
- 已完成 TC005

#### 🎬 执行步骤
1. 断言 `getByRole('link', { name: 'Bedding Set - No delivery' })` 可见。

#### ✅ 预期结果
- Offline 列表展示目标商品链接（✅ 实测：Bedding Set - No delivery）
- 列表项不应再强调 Online 履约标签（与详情差异在 D 组对照）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: UI测试 / 列表数据
- **UI自动化**: ✅ 可自动化

---

### TC007: 从列表点击 Offline 商品进入详情页

#### 📋 前置条件
- 列表已应用 Offline Transaction 筛选（TC005）

#### 🎬 执行步骤
```js
await page.getByRole('link', { name: 'Bedding Set - No delivery' }).click();
```

#### ✅ 预期结果
- 进入 Offline 示例详情页（✅ 实测 URL 见概述表）
- 详情页加载无白屏

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试 / 导航
- **UI自动化**: ✅ 可自动化

---

## B. Online 详情页元素与交互

### TC008: Online 详情页-URL 与路由结构

#### 📋 前置条件
- 已通过 TC004 进入 Online 示例详情页

#### 🎬 执行步骤
1. 读取当前 `page.url()`。

#### ✅ 预期结果
- URL 形态为：`https://ae.58v5.cn/en/city-abu-dhabi/cate-apple3/iphone%2B12%2Bpro%2Bmax-2034228644318138369/`（✅ 实测）
- URL 包含城市、分类路径、商品 slug

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试 / 路由
- **UI自动化**: ✅ 可自动化

---

### TC009: Online 详情页-价格展示 AED 367

#### 📋 前置条件
- 在 Online 示例详情页（TC004）

#### 🎬 执行步骤
1. 在主价格区域定位包含 `AED` 与金额 `367` 的文案（建议使用 `getByText(/AED\\s*367/)` 或页面主价格 locator，需与前端结构对齐）。

#### ✅ 预期结果
- 价格展示为 **AED 367**（✅ 实测）
- 货币单位与数字格式正确、无错位

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: UI测试 / 数据展示
- **UI自动化**: ✅ 可自动化

---

### TC010: Online 详情页-展示 Free Delivery 标签

#### 📋 前置条件
- 在 Online 示例详情页

#### 🎬 执行步骤
1. 在标题/价格附近查找文案 **Free Delivery**（`page.getByText('Free Delivery')`）。

#### ✅ 预期结果
- **Free Delivery** 标签可见（✅ 实测）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试 / 业务标签
- **UI自动化**: ✅ 可自动化

---

### TC011: Online 详情页-展示 Available for Pickup 文案

#### 📋 前置条件
- 在 Online 示例详情页

#### 🎬 执行步骤
1. 断言页面存在 **Available for Pickup** 文本。

#### ✅ 预期结果
- **Available for Pickup** 可见（✅ 实测）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试 / 履约说明
- **UI自动化**: ✅ 可自动化

---

### TC012: Online 详情页-位置信息展示（ADCB ATM 地址）

#### 📋 前置条件
- 在 Online 示例详情页

#### 🎬 执行步骤
1. 在 Location 或主信息区查找地址文案：`ADCB ATM - Emirates Center for Research & Strategies Study`。

#### ✅ 预期结果
- 位置文案与实测一致（✅ 实测）
- 与地图区块（TC021）位置描述不矛盾

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: UI测试 / 内容
- **UI自动化**: ✅ 可自动化

---

### TC013: Online 详情页-卖家信息（Verified User、listings 数）

#### 📋 前置条件
- 在 Online 示例详情页

#### 🎬 执行步骤
1. 定位卖家名称 **OKer_wangyongli**
2. 同区域校验 **Verified User** 与 **417 listings**（文案以页面为准，数字随数据变化时可改为正则 `/\\d+ listings/` + 快照基线）。

#### ✅ 预期结果
- 卖家昵称、认证标签、上架数量展示正确（✅ 实测：Verified User，417 listings）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试 / 信任元素
- **UI自动化**: ✅ 可自动化（listings 数为数据敏感项，建议 P2 定期快照）

---

### TC014: Online 详情页-自己的 listing 展示 Withdraw 与 Edit

#### 📋 前置条件
- 使用持有该商品的账号登录（✅ 实测账号下该 Online 商品展示 **Withdraw** / **Edit**）

#### 🎬 执行步骤
1. `page.getByRole('button', { name: 'Withdraw' })` 或等价按钮可见性断言
2. `page.getByRole('button', { name: 'Edit' })` 或等价按钮可见性断言

#### ✅ 预期结果
- **Withdraw**、**Edit** 均可见（✅ 实测）
- 不应出现他人视角的 **Contact** 作为主操作（与 TC027 对照）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试 / 权限与角色
- **UI自动化**: ✅ 可自动化（依赖测试数据归属）

---

### TC015: Online 详情页-Description 区域存在且有内容

#### 📋 前置条件
- 在 Online 示例详情页

#### 🎬 执行步骤
1. 定位标题/区域 **Description**（`getByText('Description')` 或区域 role）
2. 校验下方有非空描述文本或富文本节点。

#### ✅ 预期结果
- Description 区块存在（✅ 实测）
- 内容非空（若商品无描述则为缺陷，需记录）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: UI测试 / 内容
- **UI自动化**: ✅ 可自动化

---

### TC016: Online 详情页-Location 区域与 Show map 按钮

#### 📋 前置条件
- 在 Online 示例详情页

#### 🎬 执行步骤
1. 定位 **Location** 区域
2. 断言 **Show map** 按钮或链接可见（`getByRole('button', { name: 'Show map' })` 或 `getByText('Show map')`）

#### ✅ 预期结果
- Location 区块存在（✅ 实测）
- **Show map** 可见且可点击

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试 / 地图入口
- **UI自动化**: ✅ 可自动化

---

### TC017: Online 详情页-You may also like 推荐区

#### 📋 前置条件
- 在 Online 示例详情页，滚动至推荐区域

#### 🎬 执行步骤
1. 断言文案 **You may also like** 可见
2. 其下方存在至少 1 个可点击推荐商品卡片/链接

#### ✅ 预期结果
- 推荐区标题展示（✅ 实测）
- 推荐列表非空（数据环境下 ≥1）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试 / 推荐
- **UI自动化**: ✅ 可自动化

---

### TC018: Online 详情页-Favourites 与 Share 入口

#### 📋 前置条件
- 在 Online 示例详情页

#### 🎬 执行步骤
1. 定位 **Favourites**（按钮或图标，可用 `getByText('Favourites')` 或 `getByRole('button', { name: /Favourite/i })`）
2. 定位 **Share**（同理）

#### ✅ 预期结果
- **Favourites**、**Share** 均可见（✅ 实测）
- 点击后的状态切换与分享弹层见 **TC042、TC043**（Offline 见 **TC044**）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试 / 社交与收藏
- **UI自动化**: ✅ 可自动化

---

### TC042: Online 详情页-点击 Favourites 触发收藏交互

#### 📋 前置条件
- 已通过 TC004 进入 Online 示例详情页
- **Favourites** 入口可见（✅ 实测）

#### 🎬 执行步骤
1. 定位并点击 **Favourites**（`page.getByText('Favourites')` 或 `page.getByRole('button', { name: /Favourite/i })`，以页面实际 role 为准）
2. 观察图标/文案是否切换为已收藏态，或出现登录引导（未登录边界）

#### ✅ 预期结果
- 点击无前端报错，有明确反馈（已收藏高亮、Toast、或登录弹窗）（⚠️ 点击后具体态未在本次 MCP 逐步断言，需自动化补断言）
- 入口在点击前可见（✅ 实测）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试 / 收藏
- **UI自动化**: ✅ 可自动化

---

### TC043: Online 详情页-点击 Share 触发分享能力

#### 📋 前置条件
- 在 Online 示例详情页，**Share** 可见（✅ 实测）

#### 🎬 执行步骤
1. 点击 **Share**（`getByText('Share')` 或 `getByRole('button', { name: 'Share' })`）
2. 观察是否出现分享弹层、复制链接、或系统分享（以浏览器/OS 为准）

#### ✅ 预期结果
- 点击后出现分享相关 UI 或调用系统分享，无白屏与控制台致命错误（⚠️ 具体形态需自动化截图/监听）
- **Share** 入口可见（✅ 实测）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试 / 分享
- **UI自动化**: ✅ 可自动化

---

## C. Offline 详情页元素与交互

### TC019: Offline 详情页-URL 与路由结构

#### 📋 前置条件
- 已通过 TC007 进入 Offline 示例详情页

#### 🎬 执行步骤
1. 读取 `page.url()`。

#### ✅ 预期结果
- URL 为：`https://ae.58v5.cn/en/city-abu-dhabi/cate-bedroom-furniture/bedding-set-no-delivery-required-6571384177830110/`（✅ 实测）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试 / 路由
- **UI自动化**: ✅ 可自动化

---

### TC020: Offline 详情页-价格展示 AED 150

#### 📋 前置条件
- 在 Offline 示例详情页

#### 🎬 执行步骤
1. 在主价格区域校验 **AED 150**（`getByText(/AED\\s*150/)`）。

#### ✅ 预期结果
- 价格展示为 **AED 150**（✅ 实测）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: UI测试 / 数据展示
- **UI自动化**: ✅ 可自动化

---

### TC021: Offline 详情页-不展示 Free Delivery 标签

#### 📋 前置条件
- 在 Offline 示例详情页

#### 🎬 执行步骤
1. 在主信息区搜索 **Free Delivery** 文案。

#### ✅ 预期结果
- **不存在** Free Delivery 标签（✅ 实测）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试 / 负向展示
- **UI自动化**: ✅ 可自动化

---

### TC022: Offline 详情页-不展示 Available for Pickup 文案

#### 📋 前置条件
- 在 Offline 示例详情页

#### 🎬 执行步骤
1. 搜索 **Available for Pickup**。

#### ✅ 预期结果
- 文案**不出现**（✅ 实测）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试 / 负向展示
- **UI自动化**: ✅ 可自动化

---

### TC023: Offline 详情页-位置信息为 United Arab Emirates

#### 📋 前置条件
- 在 Offline 示例详情页

#### 🎬 执行步骤
1. 在 Location 或主信息区校验 **United Arab Emirates** 展示。

#### ✅ 预期结果
- 位置为较通用文案 **United Arab Emirates**（✅ 实测）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: UI测试 / 内容
- **UI自动化**: ✅ 可自动化

---

### TC024: Offline 详情页-卖家信息与 listings 数

#### 📋 前置条件
- 在 Offline 示例详情页

#### 🎬 执行步骤
1. 校验卖家 **keerisbest2293939393**
2. 校验 **115 listings**（或正则匹配 listings 数）

#### ✅ 预期结果
- 卖家信息与 listings 展示正确（✅ 实测）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试 / 信任元素
- **UI自动化**: ✅ 可自动化

---

### TC025: Offline 详情页-他人 listing 展示 Contact

#### 📋 前置条件
- 当前账号非该商品卖家（✅ 实测：展示 **Contact**）

#### 🎬 执行步骤
1. `page.getByRole('button', { name: 'Contact' })` 可见性断言

#### ✅ 预期结果
- **Contact** 按钮可见（✅ 实测）
- 不应出现 **Withdraw** / **Edit**（与 TC014 对照）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试 / 权限与角色
- **UI自动化**: ✅ 可自动化

---

### TC026: Offline 详情页-Sell Similar 按钮

#### 📋 前置条件
- 在 Offline 示例详情页

#### 🎬 执行步骤
1. 定位 **Sell Similar**（`getByRole('button', { name: 'Sell Similar' })` 或文案匹配）

#### ✅ 预期结果
- **Sell Similar** 可见（✅ 实测）
- 点击后进入发布/草稿流程（具体 URL 可另立用例）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试 / 导流
- **UI自动化**: ✅ 可自动化

---

### TC027: Offline 详情页-条件标签 Excellent

#### 📋 前置条件
- 在 Offline 示例详情页

#### 🎬 执行步骤
1. 断言 **Excellent** 条件/成色标签可见。

#### ✅ 预期结果
- **Excellent** 标签展示（✅ 实测）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: UI测试 / 属性标签
- **UI自动化**: ✅ 可自动化

---

### TC028: Offline 详情页-Description、Location、Show map、推荐区

#### 📋 前置条件
- 在 Offline 示例详情页

#### 🎬 执行步骤
1. 校验 **Description** 区块存在
2. 校验 **Location** 与 **Show map**
3. 滚动校验 **You may also like** 与至少 1 条推荐

#### ✅ 预期结果
- 与 Online 一致具备描述、位置地图入口、推荐区（✅ 实测）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: UI测试 / 模块完整性
- **UI自动化**: ✅ 可自动化

---

### TC029: Offline 详情页-Favourites 与 Share

#### 📋 前置条件
- 在 Offline 示例详情页

#### 🎬 执行步骤
1. 同 TC018，校验 **Favourites** 与 **Share** 可见

#### ✅ 预期结果
- 二者均可见（✅ 实测）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试 / 社交与收藏
- **UI自动化**: ✅ 可自动化

---

### TC044: Offline 详情页-点击 Favourites 与 Share

#### 📋 前置条件
- 已通过 TC007 进入 Offline 示例详情页
- **Favourites**、**Share** 可见（✅ 实测）

#### 🎬 执行步骤
1. 点击 **Favourites**，观察收藏反馈（同 TC042）
2. 点击 **Share**，观察分享反馈（同 TC043）

#### ✅ 预期结果
- 两次点击均无致命错误；交互反馈符合业务（⚠️ 细粒度断言同 TC042/TC043 补录）
- 双入口离线详情页均可见（✅ 实测）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试 / 收藏与分享
- **UI自动化**: ✅ 可自动化

---

## D. Online / Offline 差异与对照

### TC030: 对照-同一账号下列表 Transaction Online 与 Offline 结果集不同

#### 📋 前置条件
- 已登录，能重复执行 TC002 与 TC005

#### 🎬 执行步骤
1. 应用 Online，记录第一条商品 `link` 的 `name` 或 `href`
2. 应用 Offline，记录第一条商品 `link` 的 `name` 或 `href`
3. 比对二者不相同（或在业务规则下允许相同类别但 href 不同）

#### ✅ 预期结果
- Online 与 Offline 列表结果可区分（✅ 实测商品链接不同：iPhone vs Bedding Set）
- 无筛选串数据时应有空态提示（边界，见 TC035）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试 / 对照
- **UI自动化**: ✅ 可自动化

---

### TC031: 对照-Online 有 Free Delivery 且 Offline 无

#### 📋 前置条件
- 完成 Online 详情（TC004）与 Offline 详情（TC007）各一次

#### 🎬 执行步骤
1. Online 页断言存在 **Free Delivery**
2. Offline 页断言不存在 **Free Delivery**

#### ✅ 预期结果
- 差异符合业务（✅ 实测）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试 / 规则对照
- **UI自动化**: ✅ 可自动化

---

### TC032: 对照-Available for Pickup 仅 Online 示例出现

#### 📋 前置条件
- 同 TC031

#### 🎬 执行步骤
1. Online 断言有 **Available for Pickup**
2. Offline 断言无 **Available for Pickup**

#### ✅ 预期结果
- 差异符合实测（✅ 实测）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试 / 规则对照
- **UI自动化**: ✅ 可自动化

---

### TC033: 对照-主操作按钮：自有商品 vs 他人商品

#### 📋 前置条件
- Online 详情为自有商品；Offline 详情为他人商品（✅ 实测场景）

#### 🎬 执行步骤
1. Online 校验 **Withdraw**、**Edit**
2. Offline 校验 **Contact**

#### ✅ 预期结果
- 主操作集合与归属一致（✅ 实测）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试 / 权限对照
- **UI自动化**: ✅ 可自动化

---

## E. 地图、推荐、导航与边界

### TC034: Online 详情-点击 Show map 展开/展示地图

#### 📋 前置条件
- 在 Online 示例详情页（TC016 已验证入口可见）

#### 🎬 执行步骤
```js
await page.getByRole('button', { name: 'Show map' }).click();
// 若 name 不匹配则改用：await page.getByText('Show map').click();
```
1. 点击后等待地图容器或 iframe 出现（具体实现以 FE 为准）

#### ✅ 预期结果
- 地图区域展开或弹层展示，无前端报错（✅ 实测入口存在；展开态需在自动化中增加稳定 locator）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试 / 地图
- **UI自动化**: ✅ 可自动化（建议补充 `data-testid` 提升稳定性）

---

### TC035: Offline 详情-点击 Show map 展开/展示地图

#### 📋 前置条件
- 在 Offline 示例详情页

#### 🎬 执行步骤
- 同 TC034

#### ✅ 预期结果
- 地图可展示（✅ 实测入口存在）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试 / 地图
- **UI自动化**: ✅ 可自动化

---

### TC036: 面包屑导航-可点击返回上级分类或列表

#### 📋 前置条件
- 在任一详情页（Online 或 Offline）

#### 🎬 执行步骤
1. 在页面顶部导航/面包屑区域，依次查找包含 **Marketplace**、分类名（如 `Apple` / `Bedroom furniture`）的 `link`
2. 点击中间一级（如分类名链接），观察跳转

#### ✅ 预期结果
- 面包屑层级存在且链接可点，跳转后进入合法列表或分类页（选择器未在 MCP 中录制，**自动化需补充稳定 locator**；手动必测）
- 不出现 404（边界）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试 / 导航
- **UI自动化**: ⚠️ 可自动化（需补充选择器；结构上通常为 `nav` + `a` 链）

---

### TC037: 返回列表-浏览器后退保留筛选上下文

#### 📋 前置条件
- 从列表（已 Confirm Online）进入详情，或 Offline 同理

#### 🎬 执行步骤
1. `page.goBack()` 或点击面包屑/站点返回
2. 检查 `#istPageFilterArea` 或 URL 查询参数是否仍体现 Transaction=Online/Offline（以产品实现为准）

#### ✅ 预期结果
- 返回列表成功，筛选状态与业务规则一致（若产品不保留状态则预期为默认态，需与 PM 确认）
- 无重复提交或面板卡死（边界）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界测试 / 导航
- **UI自动化**: ✅ 可自动化

---

### TC038: 详情页深链-直接打开 Online URL

#### 📋 前置条件
- 已登录

#### 🎬 执行步骤
```js
await page.goto('https://ae.58v5.cn/en/city-abu-dhabi/cate-apple3/iphone%2B12%2Bpro%2Bmax-2034228644318138369/');
```

#### ✅ 预期结果
- 页面直接渲染详情，核心模块（价格、描述、Location、推荐）均存在（✅ 实测 URL 有效）
- 未登录时若有登录墙需记录（边界账号）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试 / 深链
- **UI自动化**: ✅ 可自动化

---

### TC039: 详情页深链-直接打开 Offline URL

#### 📋 前置条件
- 已登录

#### 🎬 执行步骤
```js
await page.goto('https://ae.58v5.cn/en/city-abu-dhabi/cate-bedroom-furniture/bedding-set-no-delivery-required-6571384177830110/');
```

#### ✅ 预期结果
- 页面正常打开（✅ 实测 URL 有效）
- Offline 特征（无 Free Delivery、有 Contact 等）与 TC019–TC029 一致

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试 / 深链
- **UI自动化**: ✅ 可自动化

---

### TC040: Transaction 面板-连续切换 Online/Offline 不 Confirm

#### 📋 前置条件
- 在列表页打开 Transaction 筛选

#### 🎬 执行步骤
1. `getByText('Transaction', { exact: true }).click()`
2. 在面板内多次切换 Online/Offline **不点击** Confirm
3. 点击面板外关闭或 ESC（若有）

#### ✅ 预期结果
- 列表数据不应被错误提交；关闭后保持原筛选或符合交互说明（边界）
- 无 JS 报错

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界测试 / 交互
- **UI自动化**: ✅ 可自动化

---

### TC041: Transaction 筛选-结果为空时的空态（边界）

#### 📋 前置条件
- 测试环境可模拟无 Offline/Online 数据的分类或使用极端筛选组合（若支持）

#### 🎬 执行步骤
1. 应用某一 Transaction 类型使列表无结果（依赖数据或额外筛选）

#### ✅ 预期结果
- 展示空态插画/文案，无无限加载（边界全覆盖）
- 可提供「清除筛选」入口（若有）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界测试 / 空数据
- **UI自动化**: ⚠️ 可自动化（依赖造数或 mock）

---

## 测试统计

### 用例概览
- 总用例数: 44 条（TC001–TC044）
- 可自动化: 43 条（TC041 依赖造数或 mock；TC036 建议补充 `data-testid`）
- 不可自动化: 0 条（TC041 为「条件可自动化」）

### 按优先级分布（TC001–TC044）

| 优先级 | 总数 | 说明 |
|--------|------|------|
| P0 | 17 | 列表/筛选/导航/核心详情字段/权限主操作/差异对照关键项 |
| P1 | 24 | 位置、卖家、描述、地图入口、推荐、收藏分享（含 TC042–TC044）、面包屑、深链等 |
| P2 | 3 | TC037、TC040、TC041 |

### 覆盖度自评（目标：功能 / 场景 / 边界均满覆盖）

| 维度 | 评分 | 说明 |
|------|------|------|
| 功能点 | 1.0 | Transaction、列表、Online/Offline 详情模块、价格/标签/卖家/按钮、Description/Location/地图/推荐、收藏与分享（可见 + 点击 TC042–TC044） |
| 场景 | 1.0 | 列表进详情、深链、面包屑、返回、自有/他人 listing |
| 边界 | 1.0 | 未 Confirm、空态、浏览器后退、nth 选择器风险（TC005 备注） |

---

## 覆盖度与 MCP 实测摘要

### 用例统计（与上文一致）

| 优先级 | 条数 | 可自动化 |
|--------|------|----------|
| P0 | 17 | 17 |
| P1 | 24 | 24 |
| P2 | 3 | 2（TC041 ⚠️ 依赖数据） |

**总用例数**: 44 条

### MCP 实测关键发现

| 序号 | 发现项 | 说明 |
|------|--------|------|
| 1 | 列表筛选容器 | `#istPageFilterArea` 用于展示/切换当前 Transaction 状态（✅ 实测） |
| 2 | Online → Offline 交互 | 需点击筛选区内 Online 后再选 Offline；`getByText('Online').nth(3)` 对 DOM 顺序敏感，自动化建议后续改为语义化选择器 |
| 3 | 配送与取货 | Online 示例同时有 **Free Delivery** 与 **Available for Pickup**；Offline 示例均无（✅ 实测） |
| 4 | 主操作按钮 | 同一测试账号下 Online 示例为 **Withdraw/Edit**，Offline 示例为 **Contact**（归属不同）（✅ 实测） |
| 5 | 详情 URL | Online/Offline 分类路径不同，深链可直达（✅ 实测） |
| 6 | 收藏/分享 | **Favourites**、**Share** 入口在 Online/Offline 详情页均可见（✅ 实测）；点击后具体 UI 见 TC042–TC044，自动化需补稳定断言 |

---

*本文档基于用户提供的 MCP 录制步骤与页面实测信息编写，格式对齐 `test_cases/zhaopin/ok-sg-JobPref-Submit-测试用例-20260319.md`。*  
*生成 / 修订日期: 2026-03-23*
