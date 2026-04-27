# All分类导航页规则

## 1. 功能概述

### 业务价值
- 提供用户快速浏览所有分类的入口，帮助用户了解平台提供的所有服务类别
- 聚合展示 Jobs、Marketplace、Services、Community、Shop、Cars 等多个业务域的分类入口
- 支持城市切换和跨国站点导航，提升用户跨地域浏览体验

### 用户角色
- **访客用户**：无需登录即可浏览所有分类
- **已登录用户**：同样可访问，体验一致

### 入口位置
- **主入口**：首页金刚区 "All" 图标
- **直接访问**：URL 直达 `/en/city-{city}/listpage/`

---

## 2. 核心流程

### 主流程
```
1. 用户从首页点击 "All" 图标
   ↓
2. 跳转至 /en/city-{city}/listpage/
   ↓
3. 页面展示分类导航树（Jobs / Marketplace / Services / Community / Shop / Cars）
   ↓
4. 用户点击任意分类或子分类
   ↓
5. 跳转至对应的分类列表页 /en/city-{city}/cate-{slug}/
```

### 异常流程
- **场景1：城市参数缺失** → 使用默认城市（通常为用户定位城市或站点默认城市）
- **场景2：直接访问 URL** → 正常加载，无需通过首页入口
- **场景3：浏览器后退** → 返回上一页（首页或其他来源页）
- **场景4：刷新页面** → 分类树内容保持不变

---

## 3. 业务规则

### 3.1 URL 规则

| 规则项 | 说明 | 示例 |
|--------|------|------|
| URL 格式 | `/en/city-{city}/listpage/` | `https://ae.58v5.cn/en/city-abu-dhabi/listpage/` |
| 城市参数 | 必须与当前城市匹配 | abu-dhabi, dubai, fujairah |
| 页面标题 | `{City} Classified Information Website - OK` | "Abu Dhabi Classified Information Website - OK" |
| HTTP 状态码 | 正常访问返回 200 | - |

### 3.2 顶部城市 Tab 规则

| 规则项 | 说明 | 示例 |
|--------|------|------|
| 当前城市展示 | 纯文本形式，不可点击 | "Abu Dhabi"（无链接） |
| 其他城市数量 | 动态展示 3 个其他城市 | Fujairah, Ras al Khaimah, Dubai |
| 城市链接行为 | 点击跳转至该城市**首页**（非 listpage） | 点击 Fujairah → `/en/city-fujairah/` |
| 动态推荐 | 刷新页面时，3 个城市可能变化 | 随机推荐算法 |

### 3.3 分类树结构规则

| 分类 | 子分类数量 | 特殊说明 |
|------|-----------|---------|
| **Jobs** | 30+ 子项 | 包含 Accounting, Property For Rent 等 |
| **Marketplace** | 19 子项 | 包含 Electronics, Free Stuff 等 |
| **Services** | 多个子项 | 包含 Business 等 |
| **Community** | 多个子项 | 包含 Activities & Groups, Lost & Found 等 |
| **Shop** | 多个子项 | URL 含 "new" 前缀（cate-new-apparel） |
| **Cars** | 独立链接 | 跳转至 `/cate-car/?iconSource=car` |
| **Used cars** | 独立链接 | 跳转至 `/cate-car-used-car/?iconSource=car` |

### 3.4 分类链接点击规则

| 点击目标 | 跳转行为 | URL 格式 |
|----------|---------|---------|
| 一级分类标题（Jobs、Marketplace） | 跳转至分类列表页，含筛选器和分页 | `/en/city-{city}/cate-jobs/` |
| 子分类链接 | 跳转至子分类列表页 | `/en/city-{city}/cate-{slug}/` |
| Cars/Used cars | 跳转至车辆列表页，带 iconSource 参数 | `/en/city-{city}/cate-car/?iconSource=car` |
| Shop 子分类 | URL 含 "new" 前缀 | `/en/city-{city}/cate-new-{slug}/` |

### 3.5 右侧城市列表规则

| 规则项 | 说明 |
|--------|------|
| 展示城市 | UAE 8 个主要城市：Dubai, Abu Dhabi, Ras al Khaimah, Sharjah, Fujairah, Ajman, Umm al Quwain, Al Ain |
| 测试城市 | enhjioujoida（测试环境专用） |
| 点击行为 | 跳转至对应城市**首页**（非 listpage） |

### 3.6 国家站点列表规则

| 规则项 | 说明 |
|--------|------|
| 国家数量 | 22 个国家/地区 |
| 主要国家 | UAE, Australia, United States, United Kingdom 等 |
| 点击行为 | 跳转至对应国家根站点 |
| URL 格式 | `https://{country-code}.58v5.cn` |

### 3.7 权限规则

| 规则项 | 说明 |
|--------|------|
| 访问权限 | **无需登录**，公开访问 |
| 登录状态展示 | 未登录：显示登录/注册入口；已登录：显示用户头像 |
| 功能限制 | 无，所有用户均可访问全部分类链接 |

### 3.8 业务约束

| 约束项 | 说明 |
|--------|------|
| 城市关联性 | 所有分类链接必须包含当前城市参数 `city-{city}` |
| 分类树一致性 | 不同城市的分类树结构相同，仅城市路径不同 |
| 页面稳定性 | 刷新页面后分类树内容不变 |
| 浏览器兼容性 | 支持后退操作，正确返回 listpage |

---

## 4. 错误处理

### 4.1 错误码定义

| 错误场景 | HTTP 状态码 | 处理方式 |
|---------|------------|---------|
| 页面不存在 | 404 | 显示 404 页面 |
| 城市参数错误 | 302 | 重定向至默认城市 listpage |
| 服务器错误 | 500 | 显示错误提示页面 |

### 4.2 错误提示文案

| 场景 | 文案 |
|------|------|
| 页面加载失败 | "Page failed to load. Please refresh and try again." |
| 分类链接失效 | "This category is currently unavailable." |

---

## 5. 依赖模块

### 上游依赖（谁调用我）
- **首页金刚区模块** → 点击 "All" 图标跳转至 listpage
- **直接 URL 访问** → 用户通过浏览器地址栏或书签访问

### 下游依赖（我调用谁）
- **Jobs 列表页** → 点击 Jobs 分类跳转
- **Marketplace 列表页** → 点击 Marketplace 分类跳转
- **其他业务域列表页** → Services, Community, Shop, Cars 等
- **城市首页** → 顶部城市 Tab 和右侧城市列表点击跳转
- **国家站点首页** → 国家站点列表点击跳转

### 跨域交互说明
- **跨城市跳转** → 从当前城市的 listpage 跳转至其他城市的首页
- **跨国站点跳转** → 从当前国家站点跳转至其他国家站点（如 ae → au）
- **跨业务域导航** → 从 listpage 导航至 Jobs、Marketplace、Cars 等不同业务域

---

## 6. 已知问题

### 产品待确认问题
- 无

### 技术风险
- **动态城市推荐** → 顶部 3 个城市的推荐算法未明确，可能存在不一致性
- **跨站点跳转** → 国家站点列表跳转时，用户 session 处理策略未明确
- **分类树数据维护** → 子分类数量可能随业务变化，需定期更新

---

## 7. 变更历史

| 日期 | 版本 | 变更内容 | 变更人 |
|------|------|---------|--------|
| 2026-04-27 | v1.0 | 初始版本，基于测试用例归档 | AI Assistant |
