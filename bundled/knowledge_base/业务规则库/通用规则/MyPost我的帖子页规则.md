# MyPost我的帖子页规则

## 1. 功能概述

### 业务价值
- 为用户提供统一的帖子管理入口，支持查看、编辑、删除、分享、下架等全生命周期管理
- 支持按状态（Active/Pending/Expired/Draft）和分类（Jobs/Property/Marketplace/Services/Community/Cars）双维度筛选
- 提供 EasyChat AI 自动回复功能，提升卖家与买家的沟通效率

### 用户角色
- **Seller（卖家）**：管理自己发布的所有帖子

### 入口位置
- **直接访问**：`https://aepub.58v5.cn/biz/en/publish/list`
- **权限要求**：必须登录，未登录用户访问会重定向至登录页

---

## 2. 核心流程

### 主流程
```
1. 用户登录后访问 My Post 页面
   ↓
2. 默认展示 All 分类 + Active 状态的帖子列表
   ↓
3. 用户可切换分类 Tab（Jobs/Property/Marketplace等）或状态 Tab（Active/Pending/Expired/Draft）
   ↓
4. 点击帖子操作菜单（...）选择操作：
   - Active: Edit / Share / Withdraw / Delete
   - Expired: Re-listing / Delete / Reason
   - Draft: Edit / Delete
   ↓
5. 执行对应操作（编辑跳转/分享复制链接/删除确认/下架确认/重新上架）
```

### 异常流程
- **场景1：未登录访问** → 重定向至登录页
- **场景2：列表为空** → 显示空状态图标和文案 "There's nothing here."
- **场景3：操作失败** → 显示错误提示或保持原状态
- **场景4：刷新页面** → 恢复默认状态（All + Active）

---

## 3. 业务规则

### 3.1 Tab 筛选规则

| Tab 类型 | 选项 | 说明 |
|---------|------|------|
| **分类 Tab** | All / Jobs / Property / Marketplace / Services / Community / Cars | 可与状态 Tab 交叉筛选 |
| **状态 Tab** | Active / Pending / Expired / Draft | 默认选中 Active |
| **默认状态** | All + Active | 页面初次加载或刷新后的默认状态 |
| **URL 参数** | 无 | Tab 状态不保留在 URL 中 |

### 3.2 帖子列表展示规则

| 规则项 | 说明 | 示例/值 |
|--------|------|---------|
| **每页数量** | 每页展示 10 条帖子 | 固定值 |
| **分页导航** | 支持页码点击、Previous/Next 按钮 | 1, 2, 3, ..., Next |
| **帖子卡片内容** | 缩略图 / 标题 / 价格 / Exposure / Views / Favorites | "AED 500" |
| **曝光数据** | Exposure（曝光次数）/ Views（查看次数）/ Favorites（收藏次数） | "Exposure: 123" |
| **EasyChat Settings** | 仅 Marketplace 类别帖子显示 | 卡片右下角入口 |
| **EasyChat On 标签** | 开启 AI Auto-Reply 后在卡片右上角显示 | "EasyChat On" |
| **验证提示** | "Get more visibility after verified >" 链接 | 跳转至身份认证页 |

### 3.3 操作菜单规则

| 状态 | 可用操作 | 说明 |
|------|---------|------|
| **Active** | Edit / Share / Withdraw / Delete | 4个操作 |
| **Expired** | Re-listing / Delete / Reason | 3个操作 |
| **Draft** | Edit / Delete | 2个操作 |
| **Pending** | （通常无帖子，显示空状态） | - |

### 3.4 操作行为规则

#### Edit（编辑）
| 规则项 | 说明 |
|--------|------|
| **跳转目标** | `/publish/classified?id={post_id}` |
| **数据预填** | 标题、图片、价格、描述、分类等 |
| **适用状态** | Active / Expired / Draft |

#### Share（分享）
| 规则项 | 说明 |
|--------|------|
| **行为** | 复制帖子链接至剪贴板 |
| **Toast 提示** | "Link Copied"（页面底部弹出） |
| **链接域名** | `ae.58v5.cn`（前台域名） |
| **适用状态** | 仅 Active |

#### Withdraw（下架）
| 规则项 | 说明 |
|--------|------|
| **二次确认弹窗标题** | "Heads Up" |
| **二次确认弹窗内容** | "Do you want to withdraw the listing?" |
| **按钮** | Cancel / OK |
| **操作结果** | 帖子从 Active 列表移除（可能进入 Expired） |
| **适用状态** | Active |

#### Delete（删除）
| 规则项 | 说明 |
|--------|------|
| **二次确认弹窗标题** | "Heads Up" |
| **二次确认弹窗内容** | "Once you delete the post, it will be deleted permanently. Do you want to continue?" |
| **按钮** | Cancel / OK |
| **操作结果** | 帖子永久删除，列表总数减 1 |
| **适用状态** | Active / Expired / Draft |

#### Re-listing（重新上架）
| 规则项 | 说明 |
|--------|------|
| **跳转目标** | `/publish/classified?id={post_id}` |
| **数据预填** | 图片、标题、价格、描述、分类 |
| **页面标题** | "Marketplace Post" 或对应类别标题 |
| **底部按钮** | "Post" |
| **适用状态** | 仅 Expired |

#### Reason（查看原因）
| 规则项 | 说明 |
|--------|------|
| **弹窗标题** | "Voluntary Removal" |
| **弹窗内容** | "You have voluntarily taken down your post." |
| **按钮** | "I got it" |
| **适用状态** | 仅 Expired |

### 3.5 EasyChat Settings 规则

| 规则项 | 说明 |
|--------|------|
| **入口位置** | 帖子卡片右下角 |
| **适用类别** | 仅 Marketplace 类别帖子 |
| **弹窗标题** | "EasyChat Settings" |
| **核心功能** | AI Auto-Reply 开关 |
| **开启后标识** | 帖子卡片右上角显示 "EasyChat On" 标签 |
| **弹窗关闭方式** | ESC 键 / 点击背景蒙层 / 点击关闭按钮 |

### 3.6 帖子详情页规则

| 规则项 | 说明 |
|--------|------|
| **跳转方式** | 点击帖子卡片主体区域（非操作按钮区） |
| **详情页域名** | `ae.58v5.cn`（前台域名） |
| **详情页内容** | 图片、价格、标题、描述、地址、发布时间、面包屑导航 |
| **卖家侧操作** | Withdraw / Edit 按钮（仅卖家本人可见） |

### 3.7 权限规则

| 规则项 | 说明 |
|--------|------|
| **访问权限** | 必须登录 |
| **未登录访问** | 重定向至登录页或首页 |
| **数据范围** | 仅展示当前登录用户的帖子 |
| **跨域权限** | 卖家可在详情页（ae.58v5.cn）看到 Withdraw/Edit 按钮 |

### 3.8 业务约束

| 约束项 | 说明 |
|--------|------|
| **分页固定数量** | 每页固定 10 条帖子 |
| **Tab 状态不持久** | 刷新页面后恢复默认（All + Active） |
| **空状态文案** | "There's nothing here." |
| **Toast 显示时长** | 约 3 秒后自动消失 |
| **弹窗层级** | 模态弹窗，背景蒙层阻止操作 |

---

## 4. 错误处理

### 4.1 错误码定义

| 错误场景 | HTTP 状态码 | 处理方式 |
|---------|------------|---------|
| 未登录访问 | 302 | 重定向至登录页 |
| 权限不足 | 403 | 显示权限错误提示 |
| 帖子不存在 | 404 | 显示帖子不存在提示 |
| 操作失败 | 500 | 显示操作失败提示，保持原状态 |

### 4.2 错误提示文案

| 场景 | 文案 |
|------|------|
| 删除失败 | "Failed to delete the post. Please try again." |
| 下架失败 | "Failed to withdraw the post. Please try again." |
| 网络错误 | "Network error. Please check your connection." |

---

## 5. 依赖模块

### 上游依赖（谁调用我）
- **发布成功页** → 点击 "View My Posts" 跳转至 My Post 页面
- **顶部导航栏** → "My Posts" 菜单项
- **个人中心** → "我的帖子"入口

### 下游依赖（我调用谁）
- **发布/编辑页** → Edit / Re-listing 操作跳转
- **帖子详情页** → 点击帖子卡片跳转（ae.58v5.cn）
- **身份认证页** → "Get more visibility after verified" 链接跳转
- **登录页** → 未登录访问时重定向

### 跨域交互说明
- **跨域名跳转** → 管理页（aepub.58v5.cn）↔ 详情页（ae.58v5.cn）
- **Session 共享** → 两个域名需要共享登录态
- **EasyChat AI服务** → 调用 AI 自动回复服务（外部依赖）

---

## 6. 已知问题

### 产品待确认问题
- **Pending 状态帖子规则未明确** → 当前测试账号无 Pending 帖子，业务规则待补充
- **EasyChat 开启后的具体效果** → 买家端消息展示规则待补充
- **身份认证后的可见度提升机制** → 具体提升策略未明确

### 技术风险
- **跨域名 Session 一致性** → ae.58v5.cn 和 aepub.58v5.cn 之间的 Session 同步可能存在延迟
- **分页性能** → 帖子数量过多时（如上千条），分页组件性能待优化
- **Tab 状态不持久** → 刷新页面后 Tab 状态丢失，用户体验可能受影响

---

## 7. 变更历史

| 日期 | 版本 | 变更内容 | 变更人 |
|------|------|---------|--------|
| 2026-04-27 | v1.0 | 初始版本，基于测试用例归档 | AI Assistant |
