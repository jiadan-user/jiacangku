# 首页Browse导航区域业务流程

## 1. 业务概述
首页Browse导航区域位于页面左上角,提供三级分类导航功能,用户可通过点击或悬停方式快速访问Marketplace、Jobs、Property、Cars、Services、Community等业务分类及其子分类。

## 2. 业务目标
- **用户目标**: 快速找到目标分类,浏览商品/职位/房产等内容
- **平台目标**: 提升分类页流量,优化导航体验,增加用户转化率

## 3. 涉及角色
- **访客和买家**: 均可使用,无需登录

## 4. 核心流程图

```mermaid
flowchart TD
    Start([用户访问首页]) --> ShowBrowse[展示Browse按钮]
    ShowBrowse --> UserAction{用户操作?}
    
    UserAction -->|点击Browse| ClickBrowse[点击Browse按钮]
    ClickBrowse --> ExpandMenu[展开下拉菜单]
    ExpandMenu --> ShowCategories[显示6个一级分类+Marketplace子分类]
    ShowCategories --> FireEvent[触发埋点:home_nevigationbar_browse_click]
    
    UserAction -->|悬停Browse| HoverBrowse[悬停Browse按钮]
    HoverBrowse --> ExpandMenu
    
    ShowCategories --> CategoryAction{用户选择?}
    
    CategoryAction -->|点击Marketplace| ClickMarketplace[点击Marketplace]
    ClickMarketplace --> JumpMarketplace[跳转/city-{city}/cate-marketplace/]
    JumpMarketplace --> ShowMarketplaceList[展示Marketplace列表页]
    
    CategoryAction -->|点击Jobs| ClickJobs[点击Jobs]
    ClickJobs --> JumpJobs[跳转/city-{city}/cate-jobs/]
    JumpJobs --> ShowJobsList[展示Jobs列表页]
    
    CategoryAction -->|点击Property| ClickProperty[点击Property]
    ClickProperty --> JumpProperty[跳转/city-{city}/cate-property/?iconSource=rent]
    JumpProperty --> ShowPropertyList[展示Property列表页:默认租房]
    
    CategoryAction -->|点击Cars| ClickCars[点击Cars]
    ClickCars --> JumpCars[跳转/city-{city}/cate-cars/]
    JumpCars --> ShowCarsList[展示Cars列表页]
    
    CategoryAction -->|点击Services| ClickServices[点击Services]
    ClickServices --> JumpServices[跳转/city-{city}/cate-services/]
    JumpServices --> ShowServicesList[展示Services列表页]
    
    CategoryAction -->|点击Community| ClickCommunity[点击Community]
    ClickCommunity --> JumpCommunity[跳转/city-{city}/cate-community/]
    JumpCommunity --> ShowCommunityList[展示Community列表页]
    
    CategoryAction -->|点击Marketplace子分类| ClickSubcategory[点击子分类如Electronics]
    ClickSubcategory --> JumpSubcategory[跳转/city-{city}/cate-electronics/]
    JumpSubcategory --> ShowSubcategoryList[展示子分类列表页]
    
    CategoryAction -->|悬停Jobs| HoverJobs[悬停Jobs一级分类]
    HoverJobs --> ExpandJobsSub[展开Jobs二级分类]
    ExpandJobsSub --> ShowAccountingEtc[显示Accounting/Administration等31+子分类]
    ShowAccountingEtc --> HoverAccounting[悬停Accounting二级分类]
    HoverAccounting --> ExpandAccountingSub[展开Accounting三级分类]
    ExpandAccountingSub --> ShowAccountsPayable[显示Accounts Payable/Accounts Receivable等]
    ShowAccountsPayable --> ClickAccountsPayable[点击Accounts Payable]
    ClickAccountsPayable --> JumpAccountsPayable[跳转/city-{city}/cate-accounts-payable/]
    JumpAccountsPayable --> ShowAccountsPayableList[展示Accounts Payable职位列表]
    
    ShowMarketplaceList --> End([流程结束])
    ShowJobsList --> End
    ShowPropertyList --> End
    ShowCarsList --> End
    ShowServicesList --> End
    ShowCommunityList --> End
    ShowSubcategoryList --> End
    ShowAccountsPayableList --> End
```

## 5. 详细步骤说明

### 步骤1: 点击或悬停Browse按钮
- **触发方式**: 用户点击或悬停页面左上角"Browse"按钮
- **菜单展开**: 下拉菜单成功展开
- **埋点触发**: 点击时触发`home_nevigationbar_browse_click`事件

### 步骤2: 展示分类列表
- **一级分类**: 显示6个分类:Marketplace/Jobs/Property/Cars/Services/Community
- **Marketplace子分类**: 默认展示14个子分类:Collectibles & Art/Clothing & Shoes/Baby & Kids/Books · Movies & Music/Electronics/Health & Beauty/Home & Garden/Pet Supplies/Sports & Outdoors/Tickets/Toys · Games & Hobbies/Auto Parts & Accessories/Business & Industrial/Other

### 步骤3: 点击一级分类跳转
- **Marketplace**: 跳转`/city-washington1/cate-marketplace/`,展示商品列表
- **Jobs**: 跳转`/city-washington1/cate-jobs/`,展示职位列表
- **Property**: 跳转`/city-washington1/cate-property/?iconSource=rent`,展示房产列表(默认租房)
- **Cars**: 跳转`/city-washington1/cate-cars/`,展示汽车列表
- **Services**: 跳转`/city-washington1/cate-services/`,展示服务列表
- **Community**: 跳转`/city-washington1/cate-community/`,展示社区活动列表

### 步骤4: 点击Marketplace子分类跳转
- **示例**: 点击"Electronics"子分类
- **跳转**: URL变为`/city-washington1/cate-electronics/`
- **展示**: 电子产品列表页
- **面包屑**: Marketplace > Electronics

### 步骤5: 三级分类导航(Jobs示例)
1. **悬停Jobs**: 展开Jobs二级分类,显示Accounting/Administration & Office Support等31+子分类
2. **悬停Accounting**: 展开Accounting三级分类,显示Accounts Officers/Clerks、Accounts Payable、Accounts Receivable等6+三级分类
3. **点击Accounts Payable**: 跳转到`/city-washington1/cate-accounts-payable/`
4. **展示页面**:
   - 页面标题:"Washington Accounts Payable Job Listings - OK"
   - 面包屑:"Home > Jobs > Accounting > Accounts Payable"
   - 主标题:"Accounts Payable in Washington"
   - 筛选器:Best Match/Filter/Accounts Payable/Washington/Salary/Job Type/Workplace type/Unit
   - 职位列表:显示Accounts Payable相关职位

## 6. 异常分支

### 6.1 菜单展开失败
- **场景**: JS错误或组件加载失败
- **处理**: 降级处理,不阻塞主流程

### 6.2 分类页面不存在
- **场景**: 目标分类页不存在
- **处理**: 显示404页面

### 6.3 跳转失败
- **场景**: 网络异常
- **处理**: 显示错误提示

## 7. 关联流程
- **首页金刚位导航**: Browse导航与金刚位导航协同提供分类访问功能
- **分类列表页**: Browse导航是进入分类列表页的主要入口
- **首页搜索**: 搜索和Browse导航提供不同的内容发现方式

## 8. 变更历史

| 日期 | 版本 | 变更内容 | 变更人 |
|-----|------|---------|--------|
| 2026-04-28 | v1.0 | 初始版本,基于OK.com-Browse导航区域-测试用例-20260320.md生成 | AI |
