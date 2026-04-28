# Marketplace探索列表页规则

## 1. 功能概述
- **业务价值**：为用户提供高效的商品浏览、筛选和发现能力,支持多维度筛选(排序、类别、地点、价格、交易方式、商品状态)和快速定位目标商品,提升用户购物体验。
- **用户角色**：
  - 访客(visitor):未登录用户,可浏览列表、筛选商品、查看详情,但部分操作(如收藏、购买)需登录
  - 已登录用户:完整权限,可浏览、筛选、收藏、购买
- **入口位置**：
  - 入口1:首页金刚位 → 点击「Marketplace」图标(URL包含 `iconSource=marketplace`)
  - 入口2:首页综合搜索 → 输入关键词 → 切换到 Marketplace 类别
  - 入口3:其他业务域(如 Jobs/Property/Cars)通过类别筛选项切换到 Marketplace
  - 入口4:All分类导航页 → 点击 Marketplace 分类

## 2. 核心流程
- **主流程**：
  1. 用户从首页金刚位点击「Marketplace」,进入 Marketplace 大类列表页(URL:`/en/city-{city}/cate-marketplace/?iconSource=marketplace`)
  2. 页面默认展示:
     - 排序项:Best Match
     - 类别:Marketplace
     - 地点:当前城市(如 Abu Dhabi)
     - 已选条件 Tag:`Location:Abu Dhabi`、`Category:Marketplace`
  3. 用户可通过筛选器调整条件:
     - 排序:Best Match / Newest First / Lowest Price / Highest Price(对应 sortId=0/1/3/4)
     - 类别:切换主类(Marketplace/Jobs/Property/Cars/Services/Community/Shop)及子类
     - 地点:搜索城市/滚动选择/首字母快速定位
     - Price:输入 Min/Max 价格范围
     - Transaction:单选(如 Online)
     - Condition:多选(如 New/Used/Excellent)
  4. 筛选后列表刷新,Tag 区同步更新,URL 参数同步(如 `sortId=3&attr_149=xxx`)
  5. 用户浏览列表卡片(封面图、标题、价格、条件标签、Verified User、Free Delivery)
  6. 点击卡片进入商品详情页(新标签页打开)
  7. 列表底部分页切换(点击页码 2、3 或 Next)

- **异常流程**：
  - 城市搜索无结果 → 显示无结果提示,不崩溃
  - Price Min > Max → 显示错误提示(前端校验)
  - 筛选条件过严无结果 → 显示空状态
  - 点击 Tag 的关闭(×) → 移除对应筛选条件,列表刷新
  - 切换类别后筛选项联动 → 不适用项清空或禁用(如从 Marketplace 切到 Jobs 后,Transaction 消失,出现薪资等)
  - Filter 面板内切换类别 → 筛选项合法性校验,无非法组合

## 3. 业务规则

### 3.1 输入规则

| 功能模块 | 字段 | 类型 | 必填 | 格式 | 说明 |
|---------|------|------|------|------|------|
| 排序 | sortId | Enum | 否 | 0/1/3/4 | Best Match(0)、Newest First(1)、Lowest Price(3)、Highest Price(4) |
| 类别 | Category | 下拉多级 | 否 | 主类+子类 | 主类:Marketplace/Jobs/Property/Cars/Services/Community/Shop;子类按主类动态展示 |
| 地点 | Location | 下拉搜索 | 否 | 城市名 | 支持搜索/滚动选择/首字母快速定位;URL路径变化(`city-{citycode}`) |
| 价格 | Price Min/Max | Number | 否 | 正整数 | 仅输入 Min、仅输入 Max、同时输入均合法;Min ≤ Max |
| 交易方式 | Transaction | 单选 | 否 | attr_149 | Online 等,单选互斥,URL参数 `attr_149` |
| 商品状态 | Condition | 多选 | 否 | - | New/Used/Excellent 等,支持多选,多选逻辑以产品为准(AND/OR) |

### 3.2 校验规则

| 字段 | 校验规则 | 前端行为 | 后端校验 |
|------|---------|---------|---------|
| sortId | 合法值:0/1/3/4 | 下拉仅展示合法项;非法值降级为 Best Match | ✅ |
| Price Min | 非负数 | 输入时前端校验;非法输入提示错误 | ✅ |
| Price Max | 非负数,且 Max ≥ Min | Min > Max 时提示 "Max price must be higher than min price" | ✅ |
| City Search | 已知城市列表 | 搜索无结果显示空状态,不崩溃 | ✅ |
| Category | 主类与子类一致性 | 切换主类后子类联动更新;不出现 Marketplace 大类与 Jobs 子类不匹配 | ✅ |

### 3.3 权限规则

| 规则项 | 规则内容 | 说明 |
|--------|----------|------|
| 访问权限 | 访客可浏览列表页,无需登录 | 浏览、筛选、查看详情均无需登录;收藏、购买需登录 |
| 筛选权限 | 所有用户可使用筛选器 | 筛选功能对访客和已登录用户均开放 |
| 分页权限 | 所有用户可翻页 | 无权限限制 |

### 3.4 业务约束

| 规则项 | 规则内容 | 说明 |
|--------|----------|------|
| 类别主类横向滚动 | Shop 主类需向左滑动才可见 | 类别筛选项的主类为横向滚动列表,Shop 在列表靠后位置,未横向滑动前不可见 |
| 类别切换筛选项联动 | 切换主类后筛选项场景化更新 | Marketplace 展示 Price/Transaction/Condition;Jobs 展示薪资/雇佣类型;Property 展示房型/租售;Cars 展示 Mileage/Brand;各场景筛选项互不冲突 |
| sortId 唯一性 | URL 中 sortId 仅出现一次 | 同一查询串内 sortId 参数不重复 |
| 地点 URL 路径变化 | 切换城市后 URL 路径段变化 | 从 `/city-abu-dhabi/` 变为 `/city-dubai/`,非查询参数 |
| Tag 与筛选项同步 | Tag 区与筛选器双向同步 | 点击 Tag 的×移除筛选条件,列表刷新;筛选器选中后 Tag 区增加对应 Tag |
| Filter 面板与外部同步 | Filter 内外状态一致 | 打开 Filter 面板时,价格/单选/多选等区块与外部筛选项状态一致;修改后列表与 Filter 计数更新 |
| 首页金刚位默认筛选 | iconSource=marketplace | 从首页金刚位进入时,URL 包含 `iconSource=marketplace`,第一个筛选项默认为 Best Match |
| 综合搜索入口默认类别 | All Categories | 从首页综合搜索进入时,默认类别为 "All Categories",URL 无 `iconSource=marketplace` |

## 4. 错误处理

| 错误场景 | 错误提示 | 前台展示 | 处理方式 |
|---------|---------|---------|---------|
| 城市搜索无结果 | "No results found" | 城市列表显示无结果或空状态 | 前端友好提示,不崩溃 |
| Price Min > Max | "Max price must be higher than min price" | 输入框下方显示错误提示 | 前端校验,阻止提交或提示修正 |
| 筛选条件过严无结果 | "No results found" | 列表区显示空状态 | 建议放宽筛选条件 |
| sortId 非法值(如 2/999) | 降级为 Best Match | 排序项显示 Best Match,列表按默认排序展示 | 后端降级处理,前端不报错 |
| 网络超时 | "Network error, please try again" | 列表区显示加载失败提示 | 捕获网络异常,提示用户重试 |
| 弱网下首屏加载慢 | 骨架屏或 loading 状态 | 显示加载态,最终内容可展示 | 有骨架或加载态,提升体验 |

## 5. 依赖模块

- **上游依赖(谁调用我)**：
  - 首页金刚位:用户点击「Marketplace」图标进入列表页
  - 首页综合搜索:用户输入关键词后切换到 Marketplace 类别进入列表页
  - All分类导航页:用户点击 Marketplace 分类进入列表页
  - 其他业务域列表页:如 Jobs/Property/Cars 列表页通过类别筛选项切换到 Marketplace

- **下游依赖(我调用谁)**：
  - 商品详情页:用户点击列表卡片进入对应商品详情页
  - 城市服务:调用城市列表接口获取可选城市(搜索/滚动/首字母索引)
  - 分类服务:调用分类树接口获取 Marketplace 主类及子类(如 Electronics → Computers & Tablets)

- **跨域交互说明**：
  - 探索列表页与 Jobs/Property/Cars/Services/Community/Shop 列表页共享类别筛选器,切换主类后列表页路由变化(如从 `/cate-marketplace/` 变为 `/cate-jobs/`),筛选项场景化更新
  - Free 金刚位落地到 Marketplace 列表页时,默认价格筛选为 `lowestPrice=0&highestPrice=0`(免费商品)
  - 列表页卡片展示依赖商品详情页数据结构(标题、价格、封面图、条件标签、Verified User、Free Delivery)

## 6. 已知问题

- **产品待确认问题**：
  - 综合搜索 Search 后默认落在「全部分类」还是「上次记忆类别」
  - Condition 多选逻辑为 AND 还是 OR
  - Filter 计数「Filter · N」与清除条件规则
  - Jobs 从首页点击与直接打开 `cate-jobs` 根路径时,城市范围是否一致

- **技术风险**：
  - sortId=2 在当前 SSR 中未出现在 `sortList`,非法值降级行为需确保稳定
  - 弱网下首屏加载慢,需确保有骨架或加载态,避免白屏
  - 类别切换后筛选项联动逻辑复杂,需确保不出现非法组合或残留互斥筛选
  - 分页切换时 URL 参数同步,需确保页码与查询参数一致

## 7. 变更历史

| 日期 | 版本 | 变更内容 | 变更人 |
|-----|------|---------|--------|
| 2026-04-28 | v1.0 | 初始版本,基于 Marketplace 探索列表页测试用例归档生成 | AI |
