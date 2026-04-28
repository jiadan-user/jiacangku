# 首页Browse导航区域规则

## 1. 功能概述
- **业务价值**: Browse导航区域提供三级分类导航,用户可快速浏览和访问各业务分类,是首页核心导航功能
- **用户角色**: 访客和买家均可使用,无需登录
- **模块位置**: 页面左上角"Browse"按钮
- **依赖模块**: 分类列表服务

## 2. 核心流程

### 2.1 Browse菜单展开流程
1. 用户点击或悬停"Browse"按钮
2. 下拉菜单展开
3. 显示6个一级分类和Marketplace子分类

### 2.2 分类跳转流程
1. 用户点击分类链接
2. 页面跳转到对应列表页
3. 显示分类内容和筛选器

### 2.3 三级分类导航流程
1. 用户悬停一级分类(如Jobs)
2. 展开二级分类(如Accounting)
3. 悬停二级分类,展开三级分类(如Accounts Payable)
4. 点击三级分类跳转到对应列表页

## 3. 业务规则

### 3.1 Browse按钮规则

| 规则项 | 规则内容 | 说明 |
|--------|----------|------|
| 位置 | 页面左上角 | 固定位置 |
| 文案 | "Browse" | 英文站点 |
| 触发方式 | 点击或悬停 | 两种方式均可触发 |
| 埋点 | home_nevigationbar_browse_click | 点击事件 |

### 3.2 一级分类规则

| 规则项 | 规则内容 | 说明 |
|--------|----------|------|
| 分类数量 | 6个 | 固定数量 |
| 分类列表 | Marketplace/Jobs/Property/Cars/Services/Community | 固定顺序 |
| 默认展示 | Marketplace子分类 | 展开菜单时默认显示14个Marketplace子分类 |
| 跳转URL | `/city-{city}/cate-{category}/` | URL模式 |

### 3.3 Marketplace一级分类规则

| 规则项 | 规则内容 | 说明 |
|--------|----------|------|
| 子分类数量 | 14个 | 固定数量 |
| 子分类列表 | Collectibles & Art/Clothing & Shoes/Baby & Kids/Books · Movies & Music/Electronics/Health & Beauty/Home & Garden/Pet Supplies/Sports & Outdoors/Tickets/Toys · Games & Hobbies/Auto Parts & Accessories/Business & Industrial/Other | 固定顺序 |
| 跳转URL | `/city-{city}/cate-marketplace/` | 一级分类URL |
| 子分类URL | `/city-{city}/cate-{subcategory}/` | 二级分类URL,如`/cate-electronics/` |

### 3.4 Jobs一级分类规则

| 规则项 | 规则内容 | 说明 |
|--------|----------|------|
| 子分类数量 | 31+个 | 包含Accounting等 |
| 跳转URL | `/city-{city}/cate-jobs/` | 一级分类URL |
| 子分类 | Accounting/Administration & Office Support/Advertising · Arts & Media/Banking & Financial Services/Call Center & Customer Service/CEO & General Management等 | 二级分类 |
| 三级分类 | Accounting下包含6+个三级分类 | 如Accounts Officers/Clerks、Accounts Payable、Accounts Receivable等 |
| 三级分类URL | `/city-{city}/cate-{subcategory}/` | 如`/cate-accounts-payable/` |

### 3.5 Property一级分类规则

| 规则项 | 规则内容 | 说明 |
|--------|----------|------|
| 跳转URL | `/city-{city}/cate-property/?iconSource=rent` | 默认显示租房 |
| iconSource | rent | 默认参数 |

### 3.6 Cars一级分类规则

| 规则项 | 规则内容 | 说明 |
|--------|----------|------|
| 跳转URL | `/city-{city}/cate-cars/` | 一级分类URL |

### 3.7 Services一级分类规则

| 规则项 | 规则内容 | 说明 |
|--------|----------|------|
| 跳转URL | `/city-{city}/cate-services/` | 一级分类URL |

### 3.8 Community一级分类规则

| 规则项 | 规则内容 | 说明 |
|--------|----------|------|
| 跳转URL | `/city-{city}/cate-community/` | 一级分类URL |

### 3.9 悬停导航规则

| 规则项 | 规则内容 | 说明 |
|--------|----------|------|
| 一级悬停 | 悬停Browse展开一级分类 | 显示6个一级分类+Marketplace子分类 |
| 二级悬停 | 悬停一级分类展开二级分类 | 如悬停Jobs展开Accounting等 |
| 三级悬停 | 悬停二级分类展开三级分类 | 如悬停Accounting展开Accounts Payable等 |
| 菜单关闭 | 鼠标移出菜单区域 | 菜单自动收起 |

### 3.10 跳转页面规则

| 规则项 | 规则内容 | 说明 |
|--------|----------|------|
| 面包屑 | 显示层级结构 | 如"Home > Jobs > Accounting > Accounts Payable" |
| 页面标题 | 包含城市和分类名 | 如"Washington Accounts Payable Job Listings - OK" |
| 主标题 | 分类名+城市 | 如"Accounts Payable in Washington" |
| 筛选器 | Best Match/Filter/分类/城市/其他筛选项 | 根据分类不同而不同 |
| 列表内容 | 显示对应分类的商品/职位/房产等 | 根据分类类型展示 |

## 4. 错误处理

| 错误码 | 错误信息 | 触发条件 | 用户提示 |
|--------|----------|----------|----------|
| - | 菜单展开失败 | JS错误或组件加载失败 | 降级处理,不阻塞主流程 |
| 404 | 分类页面不存在 | 目标分类页不存在 | 显示404页面 |
| - | 跳转失败 | 网络异常 | 显示错误提示 |

## 5. 依赖模块

### 5.1 上游依赖
- **首页**: 用户访问首页时展示Browse按钮
- **用户操作**: 用户点击或悬停Browse按钮

### 5.2 下游依赖
- **分类列表服务**: 提供分类数据
- **Marketplace列表页**: Marketplace及子分类跳转目标
- **Jobs列表页**: Jobs及子分类跳转目标
- **Property列表页**: Property跳转目标
- **Cars列表页**: Cars跳转目标
- **Services列表页**: Services跳转目标
- **Community列表页**: Community跳转目标

## 6. 已知问题
- **子分类完整性**: 仅Marketplace的14个子分类和Jobs的Accounting子分类经过完整测试,其他子分类待验证
- **响应式布局**: 移动端响应式布局未测试
- **键盘导航**: Tab/Enter/Esc键盘导航支持未测试

## 7. 变更历史

| 日期 | 版本 | 变更内容 | 变更人 |
|-----|------|---------|--------|
| 2026-04-28 | v1.0 | 初始版本,基于OK.com-Browse导航区域-测试用例-20260320.md生成 | AI |
