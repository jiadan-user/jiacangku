# 二手交易业务域 - Marketplace 文本用例归档索引

> **索引目的**：快速定位 Marketplace 列表详情页与 Sell Similar 功能的所有文本用例，方便测试执行、自动化脚本生成和知识库维护  
> **最后更新**：2026-05-09  
> **用例总数**：7 个文件（`marketplace/` 列表详情与 Sell Similar + `marketplace_post/` Marketplace 发布全链路）

---

## 索引分类

### 1. 列表页功能

#### 1.1 列表页完整功能探索（扩展版）

| 文件名 | 站点 | 用例数 | 核心场景 | 自动化状态 |
|--------|------|--------|---------|-----------|
| [ok-ae-Marketplace-ListPage-测试用例-扩展版-20260401.md](../../文本用例/marketplace/ok-ae-Marketplace-ListPage-测试用例-扩展版-20260401.md) | AE（阿联酋） | 60 | 列表页浏览、搜索、筛选、排序、商品卡片、收藏、分页、图片媒体、响应式兼容 | ✅ 97%（58/60） |

**核心流程**：
```
进入列表页 → [可选]搜索关键词 → [可选]应用筛选（Transaction、Category、Price、Location、Condition）→ [可选]排序 → 浏览商品卡片 → 点击商品 → 进入详情页
```

**关键验证点**：
- ✅ P0：从首页金刚位进入列表页，URL 包含 `/cate-marketplace/`
- ✅ P0：列表页默认展示搜索框、筛选器、排序选项、商品卡片
- ✅ P0：Transaction 筛选（Online / Offline）应用后，列表刷新
- ✅ P0：Online 商品显示 "Free Delivery" 标签，Offline 商品不显示
- ✅ P1：搜索关键词后，列表刷新，URL 更新（如 `?keywords=iphone`）
- ✅ P1：筛选条件组合应用后，列表刷新
- ✅ P1：排序选项切换后，列表顺序改变（Default / Newest / Price: Low to High / Price: High to Low）
- ✅ P1：商品卡片包含主图、标题、价格、位置、收藏按钮
- ✅ P1：点击收藏按钮，已登录用户成功收藏，未登录调起登录
- ❌ 负向：列表为空时显示 "No results found"

**用例扩展对比**：

| 模块 | 原有用例 | 新增用例 | 合计 |
|------|---------|---------|------|
| A. 页面进入与基础展示 | 2 | 5 | 7 |
| B. 搜索功能 | 4 | 8 | 12 |
| C. 筛选功能 | 5 | 6 | 11 |
| D. 排序功能 | 3 | 2 | 5 |
| E. 商品卡片与收藏 | 7 | 5 | 12 |
| F. 分页与异常流 | 4 | 3 | 7 |
| G. 图片与媒体（新增） | 0 | 4 | 4 |
| H. 响应式与兼容性（新增） | 0 | 2 | 2 |
| **合计** | **25** | **35** | **60** |

---

### 2. 详情页功能

#### 2.1 详情页完整功能（Online/Offline 差异）

| 文件名 | 站点 | 用例数 | 核心场景 | 自动化状态 |
|--------|------|--------|---------|-----------|
| [ok-ae-Marketplace-DetailPage-测试用例-20260323.md](../../文本用例/marketplace/ok-ae-Marketplace-DetailPage-测试用例-20260323.md) | AE（阿联酋） | 44 | 详情页元素展示、Online/Offline 差异、本人帖/非本人帖操作按钮差异、地图、推荐、导航 | ✅ 98%（43/44） |

**核心流程**：
```
列表页 → 应用 Transaction 筛选（Online/Offline）→ 点击商品 → 进入详情页 → 查看商品信息 → [可选]查看地图/推荐 → [可选]收藏/分享 → [可选]联系卖家/Sell Similar
```

**关键验证点**：
- ✅ P0：列表页应用 Online 筛选后，点击商品进入 Online 详情页
- ✅ P0：列表页应用 Offline 筛选后，点击商品进入 Offline 详情页
- ✅ P0：Online 详情页显示 "Free Delivery" 和 "Available for Pickup" 标签
- ✅ P0：Offline 详情页不显示配送标签
- ✅ P0：本人帖展示 Withdraw/Edit 按钮，不展示 Contact/Sell Similar
- ✅ P0：非本人帖展示 Contact/Sell Similar 按钮，不展示 Withdraw/Edit
- ✅ P1：详情页显示卖家信息（昵称、Verified User 标签、Listings 数量）
- ✅ P1：详情页显示推荐模块（"You may also like"）
- ✅ P1：详情页显示地图模块（"Show map" 按钮）
- ❌ 负向：商品不存在时显示 "This listing is no longer available"

**Online / Offline 差异对照**：

| 项 | Online 详情页 | Offline 详情页 |
|----|--------------|---------------|
| 配送标签 | ✅ Free Delivery / Available for Pickup | ❌ 无配送标签 |
| 位置文案 | 详细地址（如 "ADCB ATM - Emirates Center"） | 通用位置（如 "United Arab Emirates"） |
| 取货标签 | ✅ Available for Pickup | ❌ 无取货标签 |
| 其他元素 | 相同（主图、标题、价格、卖家信息、推荐、地图） | 相同 |

---

### 3. Sell Similar 功能

#### 3.1 Sell Similar 核心流程

| 文件名 | 站点 | 用例数 | 核心场景 | 自动化状态 |
|--------|------|--------|---------|-----------|
| [sell_similar_test_cases.md](../../文本用例/marketplace/sell_similar_test_cases.md) | AE（阿联酋） | 10 | Sell Similar 按钮展示、点击跳转、数据预加载、登录态验证、多语言、非 Marketplace 商品 | ✅ 100% |
| [SELL_SIMILAR_TEST_CASES_SUMMARY.md](../../文本用例/marketplace/SELL_SIMILAR_TEST_CASES_SUMMARY.md) | AE（阿联酋） | 8 | Sell Similar 功能总结（与 `test_ae_marketplace_sell_similar.py` 一一对应） | ✅ 100% |

**核心流程**：
```
非本人帖详情页 → 点击 Sell Similar 按钮 → [未登录则调起登录] → 跳转发布页 → 预加载原帖数据（分类、价格、标题、描述、属性）→ 清空图片/视频 → 用户修改/补充 → 发布
```

**关键验证点**：
- ✅ P0：非本人帖详情页展示 Sell Similar 按钮
- ✅ P0：本人帖不展示 Sell Similar 按钮（显示 Withdraw/Edit）
- ✅ P1：点击 Sell Similar 后，3 秒内跳转发布页，URL 包含 `/publish/`
- ✅ P1：发布页预加载原帖数据（分类、价格、标题、描述、商品属性）
- ✅ P1：发布页图片上传区域为空（不预加载图片）
- ✅ P1：未登录点击 Sell Similar 调起登录弹窗，登录成功后跳转发布页
- ✅ P1：登录后刷新详情页，Sell Similar 按钮继续展示
- ✅ P2：非 Marketplace 分类商品不展示 Sell Similar 按钮
- ✅ P2：多语言环境下，Sell Similar 按钮文案正确（如西班牙语 "Vender Similar"）

**用例映射（与自动化脚本对应）**：

| 用例 ID | pytest 函数 | 标记 | 说明 |
|---------|-------------|------|------|
| TC001 | `test_tc001_non_own_post_shows_sell_similar_button` | smoke, p0 | 非本人帖展示 Sell Similar |
| TC002 | `test_tc002_click_sell_similar_navigates_to_publish_page` | smoke, p1 | 点击跳转发布页 |
| TC003 | `test_tc003_own_post_does_not_show_sell_similar_button` | smoke, p0 | 本人帖不展示 Sell Similar |
| TC004 | `test_tc004_publish_page_preloads_original_post_data` | smoke, p1 | 发布页预加载数据 |
| TC005 | `test_tc005_not_logged_in_user_shows_login_popup` | smoke, p1 | 未登录调起登录 |
| TC007 | `test_tc007_non_marketplace_posts_do_not_show_sell_similar` | p1 | 非 Marketplace 商品不展示 |
| TC008 | `test_tc008_sell_similar_button_in_spanish_language` | p2 | 西班牙语文案 |
| TC009 | `test_tc009_publish_page_inherits_product_attributes` | p2 | 继承商品属性 |
| TC010 | `test_tc010_publish_page_inherits_description` | p2 | 继承描述 |

---

### 4. Marketplace Post 发布页（`文本用例/marketplace_post/`）

> 与列表/详情浏览互补：覆盖 **AE 站 classified 发布页** 的完整发布、图片/视频与配送、以及 **草稿体验**。

#### 4.1 全链路发布（主文档）

| 文件名 | 站点 | 用例数 | 核心场景 | 自动化状态 |
|--------|------|--------|---------|-----------|
| [OK-AE-Marketplace-Post-测试用例-20260325.md](../../文本用例/marketplace_post/OK-AE-Marketplace-Post-测试用例-20260325.md) | AE | 108 | 分类选择、详情字段、价格、配送、发布成功跳转详情页 | ✅ 约 94%（102/108） |

**核心流程**：

```
已登录进入 `/biz/en/publish/classified` → 上传媒体 → 填写标题/描述/类目与 Details → 价格与 Delivery Options → Post → 跳转商品详情页
```

#### 4.2 图片上传与配送选项（专项）

| 文件名 | 站点 | 用例数 | 核心场景 | 自动化状态 |
|--------|------|--------|---------|-----------|
| [OK-Marketplace-Post-图片上传与配送选项-测试用例-20260227.md](../../文本用例/marketplace_post/OK-Marketplace-Post-图片上传与配送选项-测试用例-20260227.md) | AE（aepub） | 18 | 图片/视频上传格式与校验；Delivery Options 三种方式；完整发布 | ✅ 约 83%（15/18） |

#### 4.3 草稿体验优化（PC）

| 文件名 | 站点 | 用例数 | 核心场景 | 自动化状态 |
|--------|------|--------|---------|-----------|
| [OK-AE-Marketplace-Post-草稿体验优化-测试用例-PC-20260407.md](../../文本用例/marketplace_post/OK-AE-Marketplace-Post-草稿体验优化-测试用例-PC-20260407.md) | AE | 67 | Draft Box、Save the draft、Toast 与按钮态、退出拦截、加载 `?id=` | ✅ 见文档（与 `test_ok_ae_marketplace_post_draft_experience_20260407.py` 对齐） |

**关联规则**：[Marketplace Post草稿与体验扩展规则](../../业务规则库/二手交易模块/Marketplace Post草稿与体验扩展规则.md)

---

## 站点覆盖

| 站点 | 站点名称 | 覆盖模块 |
|------|---------|---------|
| AE | 阿联酋站 | 列表页、详情页（Online/Offline）、Sell Similar、Marketplace Post（classified 发布与草稿） |

---

## 用例统计

| 模块 | 文件数 | 用例数 | 自动化率 |
|------|--------|--------|---------|
| 列表页功能 | 1 | 60 | 97%（58/60） |
| 详情页功能 | 1 | 44 | 98%（43/44） |
| Sell Similar 功能 | 2 | 18（10+8） | 100% |
| Post 全链路 | 1 | 108 | 约 94% |
| Post 图片与配送专项 | 1 | 18 | 约 83% |
| Post 草稿体验（PC） | 1 | 67 | 见文档 |
| **合计** | **7** | **315+** | **—** |

---

## 快速查找指南

### 按功能模块查找

**列表页**：
- 完整功能探索 → `ok-ae-Marketplace-ListPage-测试用例-扩展版-20260401.md`
- 涵盖：页面进入、搜索、筛选、排序、商品卡片、收藏、分页、图片媒体、响应式兼容

**详情页**：
- Online/Offline 详情页 → `ok-ae-Marketplace-DetailPage-测试用例-20260323.md`
- 涵盖：列表筛选、Transaction 切换、详情页元素、本人帖/非本人帖差异、地图、推荐、导航

**Sell Similar**：
- 核心流程与验证 → `sell_similar_test_cases.md`
- 功能总结（与脚本对应）→ `SELL_SIMILAR_TEST_CASES_SUMMARY.md`
- 涵盖：按钮展示、跳转、数据预加载、登录态、多语言、非 Marketplace 商品

**Marketplace Post（发布页）**：
- 主文档（108 条）→ `marketplace_post/OK-AE-Marketplace-Post-测试用例-20260325.md`
- 图片与配送 → `marketplace_post/OK-Marketplace-Post-图片上传与配送选项-测试用例-20260227.md`
- 草稿体验 PC → `marketplace_post/OK-AE-Marketplace-Post-草稿体验优化-测试用例-PC-20260407.md`

### 按优先级查找

**P0（核心功能）**：
- 列表页基础展示、Transaction 筛选、详情页加载
- Sell Similar 按钮展示逻辑（本人帖/非本人帖）
- 详情页操作按钮差异（Withdraw/Edit vs Contact/Sell Similar）

**P1（重要功能）**：
- 搜索、筛选、排序
- 商品卡片元素、收藏功能
- Sell Similar 跳转与数据预加载
- 推荐模块、地图模块

**P2（边界与兼容）**：
- 响应式适配、多语言
- 图片加载失败降级
- 特殊字符、超长文本

---

## 测试环境配置

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | ae | 阿联酋站 |
| 基础URL | https://ae.58v5.cn | 测试站点地址 |
| 列表页URL | https://ae.58v5.cn/en/city-abu-dhabi/cate-marketplace/ | Marketplace 列表页 |
| 角色 | buyer | 买家角色 |
| 测试账号 | wangyongli@58.com | 登录邮箱 |
| 测试密码 | Qwer1234 | 登录密码 |

---

## 关联业务规则与流程

- [Marketplace列表详情与SellSimilar规则](../../业务规则库/二手交易模块/Marketplace列表详情与SellSimilar规则.md)
- [Marketplace Post草稿与体验扩展规则](../../业务规则库/二手交易模块/Marketplace Post草稿与体验扩展规则.md)
- [Marketplace列表详情与SellSimilar业务流程](./Marketplace列表详情与SellSimilar业务流程.md)
- [Marketplace Post发布业务流程](./Marketplace Post发布业务流程.md)
- [二手交易业务全景](./二手交易业务全景.md)
- [商品发布业务流程](./商品发布业务流程.md)

---

## 变更历史

| 日期 | 版本 | 变更内容 | 变更人 |
|------|------|---------|--------|
| 2026-04-28 | v1.0 | 初始版本，整合 Marketplace 列表详情与 Sell Similar 功能的 4 个文本用例文件 | QA Agent |
| 2026-05-09 | v1.1 | 纳入 `文本用例/marketplace_post/` 下 3 个发布页文本用例；补充规则链接与统计 | QA Agent |
| 2026-05-09 | v1.2 | 关联文档新增 Marketplace Post 发布业务流程文档链接 | QA Agent |
