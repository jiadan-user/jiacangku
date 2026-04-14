# OK 房产列表视图（List View）— 自动化用例汇总

> **目录来源**：`test_cases/property_basics/list/`  
> **生成时间**：2026-03-18  
> **用例总数**：162 条（14 个测试文件）  
> **测试站点**：AU 站（au.58v5.cn）  
> **用途说明**：PC 端 UI 自动化用例汇总，可作为探索 **M 端（H5）** 用例的参考基线

---

## 📊 总览

| # | 文件 | 测试类 | 用例数 | 功能域 |
|---|------|--------|--------|--------|
| 1 | test_property_entry_points.py | TestPropertyEntryPoints | 14 | 首页入口与导航 |
| 2 | test_rent_sort.py | TestRentSort | 8 | 租房排序 |
| 3 | test_rent_price_filter.py | TestRentPriceFilter | 10 | 租房价格筛选 |
| 4 | test_rent_beds_filter.py | TestRentBedsFilter | 7 | 租房卧室筛选 |
| 5 | test_rent_bathrooms_filter.py | TestRentBathroomsFilter | 7 | 租房浴室筛选 |
| 6 | test_rent_property_type_filter.py | TestRentPropertyTypeFilter | 9 | 租房房产类型筛选 |
| 7 | test_rent_filter_combo.py | TestRentFilterCombo | 23 | 租房多条件组合筛选 |
| 8 | test_rent_robust.py | TestRentRobust | 13 | 健壮性与兼容性 |
| 9 | test_buy_search_basic.py | TestBuySearchBasic | 10 | 买房关键词搜索 |
| 10 | test_buy_search_sug.py | TestBuySearchSug | 11 | 买房搜索联想（Sug） |
| 11 | test_buy_search_category.py | TestBuySearchCategory | 12 | 买房分类切换 |
| 12 | test_buy_search_history.py | TestBuySearchHistory | 5 | 买房搜索历史 |
| 13 | test_buy_view_navigation.py | TestBuyViewNavigation | 17 | 视图切换与分页导航 |
| 14 | test_buy_filter_combo.py | TestBuyFilterCombo | 6 | 买房筛选组合 |
| **合计** | | | **162** | |

---

## M 端差异说明（探索参考）

> 以下 PC 端行为在 M 端（H5）可能存在差异，重点关注：

| 功能点 | PC 端 | M 端差异 |
|--------|-------|---------|
| Filter 面板 | 侧边或顶部展开 | 底部弹窗（full-sheet） |
| Sort 下拉 | Dropdown 下拉 | 底部 ActionSheet |
| 搜索联想 | 键盘输入自动出现 | 同，但软键盘可能遮挡 |
| 分页翻页 | 点击页码 | 下拉加载更多（无限滚动） |
| 视图切换按钮 | 顶部 List/Map 按钮 | 同，但位置或 icon 不同 |
| 搜索历史 | 点击搜索框展示 | 同，注意软键盘收起时机 |
| 面包屑导航 | 顶部多级面包屑 | 简化面包屑或返回箭头 |
| 房产类型弹窗 | 模态框 | 底部弹窗 |

---

## A. 首页入口与导航

> **文件**：`test_property_entry_points.py`｜**类**：`TestPropertyEntryPoints`｜**用例数**：14

### TC-LIST-001: 首页分类图标"Property"点击，跳转到 For Sale 列表页

**前置条件**：已进入 AU 站首页  
**步骤**：点击首页分类图标中的"Property"图标  
**预期**：跳转到房产 For Sale 列表页，URL 含对应路径参数  
**优先级**：P0 | **类型**：功能 | **自动化**：✅  
**M端备注**：M端图标布局可能为横向滚动，点击同一图标验证跳转 URL 一致

---

### TC-LIST-002: 首页分类图标"Property"跳转后，URL 参数正确

**前置条件**：同上  
**步骤**：点击"Property"图标后检查 URL  
**预期**：URL 中含正确的分类参数（如 `cate=xxx`）  
**优先级**：P0 | **类型**：功能 | **自动化**：✅

---

### TC-LIST-003: 首页"All"图标展开列表，包含房产分类区域

**前置条件**：已进入首页  
**步骤**：点击"All"图标 → 展开全分类列表  
**预期**：全分类列表中可见"Property"分类区域  
**优先级**：P0 | **类型**：功能 | **自动化**：✅  
**M端备注**：M端"All"可能为抽屉/底部弹窗，验证房产区域可见

---

### TC-LIST-004: All → Property for sale 跳转正确

**步骤**：All → 点击 Property for sale  
**预期**：跳转到 For Sale 列表页  
**优先级**：P0 | **类型**：功能 | **自动化**：✅

---

### TC-LIST-005: All → Property for rent 跳转正确

**步骤**：All → 点击 Property for rent  
**预期**：跳转到 For Rent 列表页  
**优先级**：P0 | **类型**：功能 | **自动化**：✅

---

### TC-LIST-006: All → Student accommodation 跳转正确

**步骤**：All → 点击 Student accommodation  
**预期**：跳转到学生公寓列表页  
**优先级**：P0 | **类型**：功能 | **自动化**：✅

---

### TC-LIST-007: All → Commercial for sale 跳转正确

**步骤**：All → 点击 Commercial for sale  
**预期**：跳转到商业地产 For Sale 列表页  
**优先级**：P0 | **类型**：功能 | **自动化**：✅

---

### TC-LIST-008: 顶部 Browse 菜单展开，包含 Property 选项

**步骤**：点击顶部 Browse 菜单  
**预期**：下拉菜单展开，显示 Property 选项  
**优先级**：P1 | **类型**：功能 | **自动化**：✅  
**M端备注**：M端无 Browse 菜单，等价入口为汉堡菜单或底部导航

---

### TC-LIST-009: Browse 悬停 Property 显示子菜单

**步骤**：鼠标悬停在 Browse → Property  
**预期**：显示 Property 子菜单（For Rent / For Sale / Commercial / Student）  
**优先级**：P1 | **类型**：功能 | **自动化**：✅  
**M端备注**：M端无悬停，改为点击展开

---

### TC-LIST-010 ~ TC-LIST-014: Browse 子菜单各入口跳转

| 编号 | 操作 | 预期 | 优先级 |
|------|------|------|--------|
| TC-LIST-010 | Browse → Property for rent | 跳转 For Rent 列表页 | P0 |
| TC-LIST-011 | Browse → Property for sale | 跳转 For Sale 列表页 | P0 |
| TC-LIST-012 | Browse → Student accommodation | 跳转学生公寓列表页 | P0 |
| TC-LIST-013 | Browse → Commercial for sale | 跳转商业地产列表页 | P0 |
| TC-LIST-014 | Browse 直接点击 Property（不展开子菜单） | 跳转默认房产页 | P1 |

---

## B. 租房排序（Sort）

> **文件**：`test_rent_sort.py`｜**类**：`TestRentSort`｜**用例数**：8

### TC-LIST-015: 默认排序为"Best Match"，URL 无 sort_id 参数

**前置条件**：进入 For Rent 列表页，未进行任何排序操作  
**步骤**：查看 URL  
**预期**：URL 中无 `sortId` 或 `sort_id` 参数，列表按默认顺序排列  
**优先级**：P0 | **类型**：功能 | **自动化**：✅  
**M端备注**：M端同样验证 URL，Sort 入口通常为顶部 Bar 右侧按钮

---

### TC-LIST-016: 选择"Newest First"，URL 含对应 sort_id

**步骤**：打开 Sort 面板 → 选择"Newest First" → 确认  
**预期**：URL 含 sort_id 参数（对应 Newest 值）；列表按发布时间倒序  
**优先级**：P0 | **类型**：功能 | **自动化**：✅  
**M端备注**：M端 Sort 以底部 ActionSheet 交互，选项与 PC 一致

---

### TC-LIST-017: 选择"Lowest Price"，URL 含对应 sort_id

**步骤**：选择"Lowest Price"  
**预期**：URL 含对应 sort_id；列表价格从低到高  
**优先级**：P0 | **类型**：功能 | **自动化**：✅

---

### TC-LIST-018: 选择"Highest Price"，URL 含对应 sort_id

**步骤**：选择"Highest Price"  
**预期**：URL 含对应 sort_id；列表价格从高到低  
**优先级**：P0 | **类型**：功能 | **自动化**：✅

---

### TC-LIST-019: 清除排序，恢复默认，URL 无 sort_id

**步骤**：已选排序后点击 Clear/重置  
**预期**：URL 中 sort_id 消失；回到 Best Match  
**优先级**：P1 | **类型**：功能 | **自动化**：✅

---

### TC-LIST-020: 打开 Sort 面板不选择，点击 Done，URL 不变

**步骤**：打开 Sort 面板 → 不做选择 → 点击 Done  
**预期**：URL 无变化，排序状态不变  
**优先级**：P1 | **类型**：功能 | **自动化**：✅

---

### TC-LIST-021: 点击 Sort 面板外部，面板关闭

**步骤**：打开 Sort 面板 → 点击面板外部区域  
**预期**：面板关闭，排序状态不变  
**优先级**：P1 | **类型**：功能 | **自动化**：✅  
**M端备注**：M端点击 sheet 外部区域（遮罩层）关闭，效果一致

---

### TC-LIST-022: 排序状态在分页后保持

**步骤**：选择"Lowest Price" → 翻到第2页  
**预期**：URL 中 sort_id 保留，第2页仍按低价排序  
**优先级**：P1 | **类型**：功能 | **自动化**：✅

---

## C. 租房价格筛选

> **文件**：`test_rent_price_filter.py`｜**类**：`TestRentPriceFilter`｜**用例数**：10

### TC-LIST-023: 输入有效 Min/Max 价格，URL 含价格参数

**前置条件**：For Rent 列表页，打开 Filter 面板  
**步骤**：Price 区间输入 Min=500, Max=1000 → 点击 Done  
**预期**：URL 含 `lowestPrice=500&highestPrice=1000`；列表过滤正确  
**优先级**：P0 | **类型**：功能 | **自动化**：✅  
**M端备注**：M端 Filter 为底部弹窗，输入框在软键盘上方，需验证不被遮挡

---

### TC-LIST-024: 只输入 Min 价格，URL 含 lowestPrice 参数

**步骤**：只填 Min=800，Max 留空 → Done  
**预期**：URL 含 `lowestPrice=800`，无 highestPrice  
**优先级**：P0 | **类型**：功能 | **自动化**：✅

---

### TC-LIST-025: 只输入 Max 价格，URL 含 highestPrice 参数

**步骤**：只填 Max=2000，Min 留空 → Done  
**预期**：URL 含 `highestPrice=2000`，无 lowestPrice  
**优先级**：P0 | **类型**：功能 | **自动化**：✅

---

### TC-LIST-026: Min > Max 时，系统拦截（不提交或报错）

**步骤**：Min=2000, Max=500 → Done  
**预期**：系统拦截，显示提示或自动交换值；不提交错误请求  
**优先级**：P0 | **类型**：异常 | **自动化**：✅

---

### TC-LIST-027: 输入负数 Min，系统拒绝

**步骤**：Min=-100  
**预期**：前端不接受负数输入，或失焦后清空/报错  
**优先级**：P1 | **类型**：边界 | **自动化**：✅

---

### TC-LIST-028: 输入非数字 Min，系统拒绝

**步骤**：Min 输入框输入"abc"  
**预期**：输入被过滤或失焦后清空  
**优先级**：P1 | **类型**：异常 | **自动化**：✅

---

### TC-LIST-029: 输入超大值，页面不崩溃

**步骤**：Min=99999999  
**预期**：接受大数值，页面不崩溃，正常提交  
**优先级**：P2 | **类型**：健壮性 | **自动化**：✅

---

### TC-LIST-030: 输入小数值，系统正常处理

**步骤**：Min=500.5, Max=1000.5  
**预期**：系统正常处理小数（接受或取整），不崩溃  
**优先级**：P2 | **类型**：边界 | **自动化**：✅

---

### TC-LIST-031: 输入 Min=0，系统正常处理

**步骤**：Min=0  
**预期**：接受0值（等效不限下限），页面正常  
**优先级**：P2 | **类型**：边界 | **自动化**：✅

---

### TC-LIST-032: 清除价格筛选，URL 中价格参数消失

**步骤**：已设价格筛选 → 点击 Clear 或删除价格值 → Done  
**预期**：URL 中 lowestPrice / highestPrice 全部消失  
**优先级**：P0 | **类型**：功能 | **自动化**：✅

---

## D. 租房卧室筛选（Beds）

> **文件**：`test_rent_beds_filter.py`｜**类**：`TestRentBedsFilter`｜**用例数**：7

### TC-LIST-033: 选择 Beds=3，URL 含 attr_168 对应值

**步骤**：Filter 面板 → 选择 Beds=3 → Done  
**预期**：URL 含 `attr_168=xxx`（3对应枚举值）  
**优先级**：P0 | **类型**：功能 | **自动化**：✅  
**M端备注**：M端 Beds 选项以底部弹窗 Chip 形式展示，选中效果一致

---

### TC-LIST-034: 选择最小值 Beds=1，URL 含对应参数

**步骤**：选择 Beds=1  
**预期**：URL 含 attr_168 最小值参数  
**优先级**：P0 | **类型**：边界 | **自动化**：✅

---

### TC-LIST-035: 选择最大值 Beds=8+，URL 含对应参数

**步骤**：选择 Beds=8+  
**预期**：URL 含 attr_168 最大值参数  
**优先级**：P0 | **类型**：边界 | **自动化**：✅

---

### TC-LIST-036: 选择 Beds=Studio，URL 含 Studio 对应参数

**步骤**：选择 Beds=Studio  
**预期**：URL 含 attr_168=Studio 枚举值  
**优先级**：P0 | **类型**：功能 | **自动化**：✅

---

### TC-LIST-037: 连续多次点击 Beds，最后一次选择生效

**步骤**：快速依次点击 Beds=1 → 2 → 3  
**预期**：最终选中3，URL 含 Beds=3 的参数  
**优先级**：P1 | **类型**：功能 | **自动化**：✅

---

### TC-LIST-038: 清除 Beds 筛选，URL 中 attr_168 消失

**步骤**：已选 Beds=2 → Clear → Done  
**预期**：URL 中 attr_168 消失  
**优先级**：P0 | **类型**：功能 | **自动化**：✅

---

### TC-LIST-039: Beds 筛选无结果时，显示空态文案

**步骤**：选择 Beds=8+ 且加其他严格条件，导致无结果  
**预期**：列表显示"No properties found"空态；无崩溃  
**优先级**：P1 | **类型**：异常 | **自动化**：✅  
**M端备注**：M端空态文案位置可能不同，需验证空态区域可见

---

## E. 租房浴室筛选（Bathrooms）

> **文件**：`test_rent_bathrooms_filter.py`｜**类**：`TestRentBathroomsFilter`｜**用例数**：7

### TC-LIST-040 ~ TC-LIST-046: Bathrooms 筛选全场景

| 编号 | 场景 | 预期 | 优先级 |
|------|------|------|--------|
| TC-LIST-040 | 选择 Bathrooms=2 | URL 含 attr_166 对应值 | P0 |
| TC-LIST-041 | 选择 Bathrooms=1（最小值） | URL 含 attr_166 最小值 | P0 |
| TC-LIST-042 | 选择 Bathrooms=1.5（半间） | URL 含 1.5 对应枚举值 | P0 |
| TC-LIST-043 | 选择 Bathrooms=5+（最大值） | URL 含最大值 | P0 |
| TC-LIST-044 | 选择 Bathrooms=Shared | URL 含 Shared 枚举值 | P0 |
| TC-LIST-045 | 全枚举映射验证（Shared/1/1.5/.../5+） | 各枚举值对应 attr_166 参数正确 | P1 |
| TC-LIST-046 | 清除 Bathrooms，URL 中 attr_166 消失 | URL 恢复 | P0 |

**M端备注**：M端 Bathrooms 选项交互与 Beds 一致，底部弹窗 Chip

---

## F. 租房房产类型筛选（Property Type）

> **文件**：`test_rent_property_type_filter.py`｜**类**：`TestRentPropertyTypeFilter`｜**用例数**：9

### TC-LIST-047: 选择 House，URL 路径变化

**步骤**：Filter → Property Type → House → Done  
**预期**：URL 路径更新（如 `/house-for-rent/`）  
**优先级**：P0 | **类型**：功能 | **自动化**：✅  
**M端备注**：M端 Property Type 弹窗改为底部 Sheet，选项与 PC 一致

---

### TC-LIST-048 ~ TC-LIST-054: Property Type 各子类及交互

| 编号 | 场景 | 预期 | 优先级 |
|------|------|------|--------|
| TC-LIST-048 | 选择 Townhomes | URL 路径含 townhomes | P0 |
| TC-LIST-049 | 选择 Apartment / Unit | URL 路径含 apartment | P0 |
| TC-LIST-050 | 选择 Villa | URL 路径含 villa | P0 |
| TC-LIST-051 | 选择 Retirement | URL 路径含 retirement | P0 |
| TC-LIST-052 | 选择 Other | URL 路径含 other | P0 |
| TC-LIST-053 | 点击弹窗 X 关闭，URL 不变 | 未选，URL 保持 | P1 |
| TC-LIST-054 | Clear 清除类型，恢复默认 URL | URL 路径恢复 | P0 |
| TC-LIST-055 | 刷新页面，Property Type 状态保持 | URL 中类型参数保留，选中态恢复 | P1 |

---

## G. 租房多条件组合筛选

> **文件**：`test_rent_filter_combo.py`｜**类**：`TestRentFilterCombo`｜**用例数**：23

### TC-LIST-056: Filter Badge 初始计数含图标来源

**步骤**：进入列表页，查看 Filter 按钮上的 badge  
**预期**：Badge 数字与当前已激活筛选数量一致  
**优先级**：P1 | **类型**：UI | **自动化**：✅

---

### TC-LIST-057: 添加 Price 筛选后，Badge 数字更新

**步骤**：设置 Price 筛选 → 查看 badge  
**预期**：Badge +1  
**优先级**：P1 | **类型**：UI | **自动化**：✅

---

### TC-LIST-058 ~ TC-LIST-078: 多条件组合 URL 参数验证

| 编号 | 组合 | 验证点 | 优先级 |
|------|------|--------|--------|
| TC-LIST-058 | Price + Beds | URL 同时含 price 和 attr_168 参数 | P0 |
| TC-LIST-059 | Sort + Price | URL 同时含 sortId 和 price 参数 | P0 |
| TC-LIST-060 | Sort + Property Type | URL 同时含 sortId 和路径类型 | P0 |
| TC-LIST-061 | Beds → Price（顺序组合） | URL 同时含两参数 | P0 |
| TC-LIST-062 | Bathrooms + Property Type | URL 同时含 attr_166 和路径类型 | P0 |
| TC-LIST-063 | Beds + Bathrooms | URL 同时含 attr_168 和 attr_166 | P0 |
| TC-LIST-064 | Sort + Beds + Price（三合一） | URL 含全部三个参数 | P0 |
| TC-LIST-065 | Price + Bathrooms | URL 含两参数 | P1 |
| TC-LIST-066 | Price + Property Type | URL 含两参数 | P1 |
| TC-LIST-067 | Beds + Property Type | URL 含两参数 | P1 |
| TC-LIST-068 | Sort + Bathrooms | URL 含两参数 | P1 |
| TC-LIST-069 | Price + Beds + Bathrooms（三合一） | URL 含全部三参数 | P0 |
| TC-LIST-070 | Sort + Price + Property Type（三合一） | URL 含全部三参数 | P0 |
| TC-LIST-071 | Beds + Bathrooms + Property Type（三合一） | URL 含全部三参数 | P0 |
| TC-LIST-072 | 全部五个条件 | URL 含所有参数 | P0 |
| TC-LIST-073 | 修改 Price，Beds 参数不变 | 修改单一条件，其他参数不受影响 | P0 |
| TC-LIST-074 | 清除一个筛选，其他保留 | 目标参数消失，其余不变 | P0 |
| TC-LIST-075 | Beds 先选后 Price（顺序无关性） | URL 参数一致 | P1 |
| TC-LIST-076 | 快速切换 Beds，最后一次生效 | 防抖，最终 URL 为最后选择 | P1 |
| TC-LIST-077 | Price + Beds 无结果，显示空态 | 空态可见，无崩溃 | P1 |
| TC-LIST-078 | 三个筛选后全 Reset，URL 恢复默认 | 全部参数清除 | P0 |

**M端备注**：M端 Filter 全部在同一底部 Sheet 中操作，需验证同一 Sheet 内多条件选择后点 Done，URL 参数正确

---

## H. 健壮性与兼容性

> **文件**：`test_rent_robust.py`｜**类**：`TestRentRobust`｜**用例数**：13

### TC-LIST-079 ~ TC-LIST-091

| 编号 | 场景 | 预期 | 优先级 |
|------|------|------|--------|
| TC-LIST-079 | 筛选参数在分页后保持 | 翻页不丢失筛选参数 | P0 |
| TC-LIST-080 | 筛选参数在视图切换（List↔Map）后保持 | 切换视图参数保留 | P0 |
| TC-LIST-081 | 筛选参数在进入详情页再返回后保持 | 返回列表页参数不丢失 | P0 |
| TC-LIST-082 | Filter 面板文案拼写正确 | 关键 Label 无错别字 | P2 |
| TC-LIST-083 | 已激活 Tag 格式统一（如"Price: $500-$1000"） | 格式一致无乱码 | P2 |
| TC-LIST-084 | Property Type 面包屑与页面标题一致 | 标题与面包屑同步 | P1 |
| TC-LIST-085 | 直接带参数访问 URL，筛选状态正确恢复 | URL 参数反映在 UI 选中态 | P0 |
| TC-LIST-086 | URL 含无效 sort_id，页面优雅降级 | 不崩溃，使用默认排序 | P1 |
| TC-LIST-087 | URL 含 XSS 脚本，不执行 | 脚本被转义，无弹窗 | P1 |
| TC-LIST-088 | 断网后提交 Filter，显示错误不崩溃 | 友好错误提示 | P1 |
| TC-LIST-089 | API 超时，显示 Loading 或超时提示 | 不白屏 | P1 |
| TC-LIST-090 | 服务器 500，显示友好错误文案 | 不暴露堆栈 | P1 |
| TC-LIST-091 | 快速多次点击 Done，不重复提交 | 防抖，只触发一次请求 | P1 |

**M端备注**：TC-LIST-088/089/090 在 M 端同样适用；TC-LIST-082/083 需在 M 端 UI 尺寸下验证文案不截断

---

## I. 买房关键词搜索

> **文件**：`test_buy_search_basic.py`｜**类**：`TestBuySearchBasic`｜**用例数**：10

### TC-LIST-092 ~ TC-LIST-101

| 编号 | 场景 | 预期 | 优先级 |
|------|------|------|--------|
| TC-LIST-092 | 输入关键词回车，URL 含 q 参数 | `?q=keyword` 出现 | P0 |
| TC-LIST-093 | 输入关键词按 Enter 触发搜索 | 页面刷新列表 | P0 |
| TC-LIST-094 | 搜索结果匹配关键词（标题含关键词） | 结果相关 | P0 |
| TC-LIST-095 | 输入特殊字符搜索，页面无报错 | 正常展示（可能无结果） | P1 |
| TC-LIST-096 | 搜索后，搜索历史记录该词 | 下次点击搜索框显示历史 | P0 |
| TC-LIST-097 | 输入纯空格搜索，被忽略 | 不产生空关键词搜索 | P1 |
| TC-LIST-098 | 输入内容后点击清除图标，输入框清空 | 清除图标出现并可点击 | P0 |
| TC-LIST-099 | 多次搜索不同词，历史记录按倒序排列 | 最新在最前 | P1 |
| TC-LIST-100 | 重复搜索同一词，历史不重复 | 历史无重复条目 | P1 |
| TC-LIST-101 | 搜索大小写不敏感（"Sydney" == "sydney"） | 返回相同结果 | P2 |

**M端备注**：M端搜索框位于顶部固定区域，点击唤起软键盘；历史下拉在软键盘展开时可能被遮挡，需验证可滚动

---

## J. 买房搜索联想（Sug）

> **文件**：`test_buy_search_sug.py`｜**类**：`TestBuySearchSug`｜**用例数**：11

### TC-LIST-102 ~ TC-LIST-112

| 编号 | 场景 | 预期 | 优先级 |
|------|------|------|--------|
| TC-LIST-102 | 输入1个字符，联想面板行为（可能不出现） | 不崩溃，按产品规则 | P1 |
| TC-LIST-103 | 输入2个字符，联想面板出现 | 显示联想地址列表 | P0 |
| TC-LIST-104 | 选择联想地址，URL 含 suglevel 参数 | `suglevel=xxx` 出现 | P0 |
| TC-LIST-105 | 输入3个以上字符，联想更精准 | 匹配更具体 | P1 |
| TC-LIST-106 | 选择联想地址，记录到搜索历史 | 下次点搜索框显示该地址 | P0 |
| TC-LIST-107 | 手动输入（不选联想）搜索，无 suglevel 参数 | URL 无 suglevel | P0 |
| TC-LIST-108 | 键盘方向键选择联想项，回车确认 | 选中态跟随键盘，回车触发搜索 | P1 |
| TC-LIST-109 | 输入无匹配词，联想面板为空态 | 显示"No results"或面板消失 | P1 |
| TC-LIST-110 | 点击联想面板外部，面板关闭 | 面板关闭，搜索框保留输入值 | P1 |
| TC-LIST-111 | 按 Esc 键，联想面板关闭 | 面板关闭 | P1 |
| TC-LIST-112 | 联想地址历史以全名显示 | 历史条目显示完整地址名 | P1 |

**M端备注**：M端无键盘方向键（TC-LIST-108），改为触摸滚动选择；Esc（TC-LIST-111）改为收起软键盘或点击返回

---

## K. 买房分类切换

> **文件**：`test_buy_search_category.py`｜**类**：`TestBuySearchCategory`｜**用例数**：12

### TC-LIST-113 ~ TC-LIST-124

| 编号 | 场景 | 预期 | 优先级 |
|------|------|------|--------|
| TC-LIST-113 | 切换分类，Filters 被清除 | 筛选条件重置 | P0 |
| TC-LIST-114 | 切换分类，搜索关键词保留 | q 参数保留 | P0 |
| TC-LIST-115 | 搜索 + 多 Filters，URL 含所有参数 | 参数完整 | P0 |
| TC-LIST-116 | 搜索 + Filters + 分页，URL 全保留 | 翻页后参数不丢 | P0 |
| TC-LIST-117 | List 切换到 Map，URL 含 view 参数 | `view=map` 出现 | P0 |
| TC-LIST-118 | Map 切换到 List，URL 移除 view 参数 | view 参数消失 | P0 |
| TC-LIST-119 | 分类下拉显示所有选项 | 选项完整（Rent/Sale/Commercial/Student） | P0 |
| TC-LIST-120 | 切换分类时保留联想地址搜索 | sug 地址参数保留 | P1 |
| TC-LIST-121 | 点击面板外部关闭分类下拉 | 面板关闭 | P1 |
| TC-LIST-122 | 快速多次切换分类，无报错 | 最终停在最后一次选择 | P1 |
| TC-LIST-123 | 切换分类后重新搜索，参数正确更新 | 旧参数被新分类+搜索覆盖 | P1 |
| TC-LIST-124 | 切换分类后再加新 Filter，组合正确 | 新分类 + 新 Filter 同时生效 | P1 |

**M端备注**：M端分类切换可能为顶部 Tab 滑动（如 Rent / Sale / Commercial），而非下拉菜单，交互差异需单独验证

---

## L. 买房搜索历史

> **文件**：`test_buy_search_history.py`｜**类**：`TestBuySearchHistory`｜**用例数**：5

### TC-LIST-125 ~ TC-LIST-129

| 编号 | 场景 | 预期 | 优先级 |
|------|------|------|--------|
| TC-LIST-125 | 首次访问，点击搜索框，无搜索历史 | 历史列表为空或不展示 | P0 |
| TC-LIST-126 | 搜索后再次点击搜索框，显示搜索历史 | 历史列表含该词 | P0 |
| TC-LIST-127 | 点击历史条目，自动执行该次搜索 | 触发对应关键词或地址搜索 | P0 |
| TC-LIST-128 | 历史记录有 FIFO 上限（最多 N 条） | 超出上限时最旧条目消失 | P1 |
| TC-LIST-129 | 历史混合关键词和联想地址，分别正确展示 | 关键词和 Sug 历史均显示 | P1 |

**M端备注**：M端历史下拉在软键盘激活时展示在键盘上方，注意验证区域高度是否可用；TC-LIST-128 上限条数需确认 M 端是否与 PC 一致

---

## M. 视图切换与分页导航

> **文件**：`test_buy_view_navigation.py`｜**类**：`TestBuyViewNavigation`｜**用例数**：17

### TC-LIST-130 ~ TC-LIST-146

| 编号 | 场景 | 预期 | 优先级 |
|------|------|------|--------|
| TC-LIST-130 | 切换视图（List→Map），搜索关键词保留 | q 参数保留 | P0 |
| TC-LIST-131 | 切换视图，搜索 + Filters 全保留 | 参数全部保留 | P0 |
| TC-LIST-132 | 面包屑"Home"点击，跳转首页 | 首页正确 | P1 |
| TC-LIST-133 | Logo 点击，跳转首页 | 首页正确 | P1 |
| TC-LIST-134 | 点击第2页，跳转到第2页 | URL 含 page=2 | P0 |
| TC-LIST-135 | 点击第1页（已在第2页），返回第1页 | URL page=1 或无 page 参数 | P0 |
| TC-LIST-136 | 最后一页，Next 按钮不可用 | 无法翻到更多页 | P1 |
| TC-LIST-137 | 访问不存在页码，显示空态或重定向 | 不崩溃 | P2 |
| TC-LIST-138 | 分页后浏览器返回，回到前一页 | 页码正确回退 | P1 |
| TC-LIST-139 | 切换视图，单个 Filter 参数保留 | 参数保留 | P0 |
| TC-LIST-140 | 切换视图，Sug 联想地址参数保留 | suglevel 参数保留 | P0 |
| TC-LIST-141 | 切换视图 + 分页，所有参数保留 | 参数全量保留 | P1 |
| TC-LIST-142 | Map 视图修改 Filter 后切回 List，Filter 有效 | 筛选生效 | P1 |
| TC-LIST-143 | 视图+搜索+Filter+分页全组合 | 全部参数保留 | P1 |
| TC-LIST-144 | 快速多次切换视图，无错误 | 最终停在最后视图 | P2 |
| TC-LIST-145 | 面包屑点击房产分类，跳转到对应分类列表 | 跳转正确 | P1 |
| TC-LIST-146 | 面包屑当前页不可点击 | 当前层面包屑为不可点击态 | P1 |

**M端备注**：  
- M端分页通常为**无限滚动**（下拉加载更多），无页码点击（TC-LIST-134~137 需转换为"滑到底部加载下一批"）  
- 面包屑（TC-LIST-132/145/146）M端可能简化为返回箭头，需单独探索

---

## N. 买房筛选组合

> **文件**：`test_buy_filter_combo.py`｜**类**：`TestBuyFilterCombo`｜**用例数**：6

### TC-LIST-147 ~ TC-LIST-152

| 编号 | 场景 | 预期 | 优先级 |
|------|------|------|--------|
| TC-LIST-147 | 搜索 + Sort + Filter，URL 含所有参数 | 三者参数共存 | P0 |
| TC-LIST-148 | 搜索 + Price Filter，URL 含所有参数 | 参数完整 | P0 |
| TC-LIST-149 | Sug 地址 + Filters 组合，参数完整 | suglevel + filter 参数同时存在 | P0 |
| TC-LIST-150 | 清除 Filter，搜索关键词保留 | q 参数保留，filter 参数消失 | P0 |
| TC-LIST-151 | 清除搜索框，Filters 保留 | filter 参数保留，q 参数消失 | P0 |
| TC-LIST-152 | 切换分类，搜索保留，Filters 清除 | q 保留，filter 参数清除 | P0 |

---

## 🔖 M 端专项探索建议

基于以上 PC 端用例，M 端重点探索以下差异场景：

| # | 探索点 | 说明 |
|---|--------|------|
| 1 | **Filter 底部 Sheet** | 多条件选择在同一 Sheet 中完成，测试 Done 后参数完整性 |
| 2 | **无限滚动分页** | 替代 PC 端的页码翻页，测试滚动加载数据正确性 |
| 3 | **软键盘遮挡** | 搜索框激活时，历史/联想下拉与软键盘的显示冲突 |
| 4 | **分类 Tab 滑动** | M端分类切换是否为横向 Tab，验证与 PC 下拉的逻辑等价性 |
| 5 | **返回箭头 vs 面包屑** | M端面包屑简化，验证返回行为（返回上一页 or 返回首页）|
| 6 | **横屏模式** | Filter Sheet 在横屏时高度是否合理 |
| 7 | **网络慢/弱网** | 列表加载占位图、Filter 提交 Loading 态 |
| 8 | **Search History 与软键盘** | 收起键盘后历史是否仍可操作 |

---

*文档生成：2026-03-18 | 来源：`test_cases/property_basics/list/` 共 14 个测试文件 162 条用例*
