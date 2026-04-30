# Marketplace探索列表页业务流程

> **业务目标**：为用户提供高效的 Marketplace 商品浏览、筛选和发现能力,支持多维度筛选和快速定位目标商品。

## 1. 完整流程图

> **要求**：专注于本业务域内的详细步骤,**不包含**跨域交互的复杂逻辑分支(跨域逻辑统一在业务全景文档中展示)。

```mermaid
graph TD
    A[首页金刚位点击 Marketplace] --> B[进入 Marketplace 列表页]
    B --> C[默认展示 Best Match 排序]
    C --> D[默认类别: Marketplace]
    D --> E[默认地点: 当前城市]
    E --> F[Tag区显示: Location + Category]
    
    F --> G{用户操作?}
    
    subgraph 排序操作
        G -->|切换排序| S1[点击排序下拉]
        S1 --> S2{选择排序项?}
        S2 -->|Best Match| S3[sortId=0]
        S2 -->|Newest First| S4[sortId=1]
        S2 -->|Lowest Price| S5[sortId=3]
        S2 -->|Highest Price| S6[sortId=4]
        S3 --> S7[列表刷新]
        S4 --> S7
        S5 --> S7
        S6 --> S7
    end
    
    subgraph 类别切换操作
        G -->|切换类别| C1[点击类别筛选项]
        C1 --> C2{选择主类?}
        C2 -->|Marketplace| C3[hover Marketplace]
        C3 --> C4[展开子类]
        C4 --> C5[点击子类如 Computers & Tablets]
        C2 -->|Jobs/Property/Cars/Services/Community| C6[切换到其他主类]
        C2 -->|Shop| C7[向左滑动后选择 Shop]
        C5 --> C8[URL/Tag/筛选项同步]
        C6 --> C8
        C7 --> C8
        C8 --> C9[列表刷新]
    end
    
    subgraph 地点筛选操作
        G -->|切换地点| L1[点击地点筛选项]
        L1 --> L2{操作方式?}
        L2 -->|搜索| L3[输入城市名]
        L3 --> L4[选择搜索结果]
        L2 -->|滚动| L5[滚动城市列表]
        L5 --> L6[点击可见城市]
        L2 -->|首字母| L7[点击字母索引]
        L7 --> L8[列表跳转至对应区间]
        L8 --> L9[选择城市]
        L4 --> L10[URL路径变化: city-{citycode}]
        L6 --> L10
        L9 --> L10
        L10 --> L11[Location Tag更新]
        L11 --> L12[列表刷新]
    end
    
    subgraph 价格筛选操作
        G -->|设置价格| P1[点击 Price]
        P1 --> P2{输入方式?}
        P2 -->|仅 Min| P3[输入 Min值]
        P2 -->|仅 Max| P4[输入 Max值]
        P2 -->|Min+Max| P5[输入 Min和Max]
        P3 --> P6[应用]
        P4 --> P6
        P5 --> P6
        P6 --> P7[Price Tag出现]
        P7 --> P8[列表刷新]
    end
    
    subgraph Transaction/Condition筛选
        G -->|设置交易方式| T1[点击 Transaction]
        T1 --> T2[单选 Online等]
        T2 --> T3[应用]
        T3 --> T4[Transaction Tag出现]
        T4 --> T5[列表刷新]
        
        G -->|设置商品状态| CO1[点击 Condition]
        CO1 --> CO2[多选 New/Used/Excellent]
        CO2 --> CO3[应用]
        CO3 --> CO4[Condition Tag出现]
        CO4 --> CO5[列表刷新]
    end
    
    subgraph Filter面板操作
        G -->|打开Filter| F1[点击 Filter]
        F1 --> F2[Filter面板展开]
        F2 --> F3[设置Price/Condition等]
        F3 --> F4{操作类型?}
        F4 -->|应用| F5[点击Apply]
        F4 -->|重置| F6[点击Reset]
        F5 --> F7[筛选项生效]
        F6 --> F8[清除所有筛选]
        F7 --> F9[列表刷新]
        F8 --> F9
    end
    
    subgraph Tag操作
        G -->|删除筛选| TAG1[点击Tag的×]
        TAG1 --> TAG2{哪个Tag?}
        TAG2 -->|Category| TAG3[类别条件清除]
        TAG2 -->|Location| TAG4[地点条件清除]
        TAG2 -->|Price| TAG5[价格条件清除]
        TAG3 --> TAG6[筛选项同步]
        TAG4 --> TAG6
        TAG5 --> TAG6
        TAG6 --> TAG7[列表刷新]
    end
    
    subgraph 列表浏览与跳转
        G -->|浏览列表| V1[查看列表卡片]
        V1 --> V2[卡片显示: 封面图/标题/价格/条件标签]
        V2 --> V3{操作?}
        V3 -->|点击卡片| V4[进入商品详情页-新标签页]
        V3 -->|翻页| V5[点击页码2/3/Next]
        V5 --> V6[URL页码参数更新]
        V6 --> V7[列表刷新]
    end
    
    S7 --> G
    C9 --> G
    L12 --> G
    P8 --> G
    T5 --> G
    CO5 --> G
    F9 --> G
    TAG7 --> G
    V7 --> G
```

## 2. 详细步骤与观测点

### 步骤1：进入 Marketplace 列表页
- **页面位置**：首页金刚位 → Marketplace 图标
- **操作流程**：
  1. 在首页搜索框下方金刚区找到「Marketplace」图标与文案
  2. 检查该入口的链接目标(DOM `href` 或右键复制链接)
  3. 点击「Marketplace」图标
  4. 跳转至 Marketplace 列表页(URL:`/en/city-{city}/cate-marketplace/?iconSource=marketplace`)
- **观测点**：
  - ✅ P0观测点:「Marketplace」入口可见、可点击
  - ✅ P0观测点:链接路径包含 `cate-marketplace`,且带 `iconSource=marketplace`
  - ✅ P0观测点:城市段与当前首页城市一致(如 `city-abu-dhabi`)
  - ✅ P0观测点:第一个筛选项默认为 Best Match
  - ✅ P0观测点:Tag 区展示 `Location:Abu Dhabi`、`Category:Marketplace`
- **验证方法**：检查 URL、筛选项默认值、Tag 区内容
- **关联规则**：[Marketplace探索列表页规则.md - 2. 核心流程](../../业务规则库/通用规则/Marketplace探索列表页规则.md)

### 步骤2：排序切换(Best Match / Newest First / Lowest Price / Highest Price)
- **页面位置**：筛选区首个排序控件
- **操作流程**：
  1. 点击排序控件(默认展示 Best Match)
  2. 下拉展开,显示四项:Best Match、Newest First、Lowest Price、Highest Price
  3. 选择其中一项(如 Lowest Price)
  4. 列表刷新,URL 中 `sortId` 参数更新为 3
  5. 排序项高亮为 Lowest Price
- **观测点**：
  - ✅ P0观测点:下拉恰好包含且仅包含四项,无缺失、无重复
  - ✅ P0观测点:Best Match 对应 `sortId=0`,Newest First 对应 `sortId=1`,Lowest Price 对应 `sortId=3`,Highest Price 对应 `sortId=4`
  - ✅ P0观测点:URL 中 `sortId` 仅出现一次,无重复
  - ✅ P0观测点:列表结果符合对应排序语义(如 Lowest Price 时价格从低到高)
  - ❌ 负向观测点:非法 `sortId`(如 2/999)降级为 Best Match,不报错
- **验证方法**：读取 URL 中 `sortId`,对首屏卡片价格/时间做抽样校验
- **关联规则**：[Marketplace探索列表页规则.md - 3.1 输入规则](../../业务规则库/通用规则/Marketplace探索列表页规则.md)

### 步骤3：类别切换 - Marketplace 子类
- **页面位置**：筛选区第三个类别筛选项
- **操作流程**：
  1. 点击类别筛选项(默认显示 Marketplace)
  2. 鼠标 hover 在 Marketplace 大类
  3. 右侧展示子类列表
  4. 鼠标 hover Electronics,右侧展示更细分子类
  5. 点击选择 Computers & Tablets
  6. 类别被选中,列表刷新
  7. Tag 区更新为 `Category:Computers & Tablets`
- **观测点**：
  - ✅ P0观测点:类目切换后筛选项与 Tag 同步更新
  - ✅ P0观测点:不出现 Marketplace 大类与叶子类目不匹配
  - ✅ P0观测点:筛选结果更新,仅展示对应子类商品
  - ❌ 负向观测点:切换后残留其他主类专属筛选项(如 Jobs 的薪资筛选)
- **验证方法**：核对 URL、Tag、列表结果与所选子类一致
- **关联规则**：[Marketplace探索列表页规则.md - 3.4 业务约束](../../业务规则库/通用规则/Marketplace探索列表页规则.md)

### 步骤4：类别切换 - 其他主类(Jobs/Property/Cars/Services/Community/Shop)
- **页面位置**：筛选区类别筛选项
- **操作流程**：
  1. 点击类别筛选项
  2. 切换主类到 Jobs(或 Property/Cars/Services/Community)
  3. 在 Jobs 下 hover/展开后点击任一子类
  4. 观察 URL、页面主标题/面包屑与筛选行 Tag
  5. 确认筛选项与 Jobs 场景匹配(如薪资、雇佣类型等)
- **观测点**：
  - ✅ P0观测点:主类为 Jobs,且叶子类目与所点击子类一致
  - ✅ P0观测点:筛选项与 Jobs 场景匹配,不应残留 Marketplace 专属项(如 Transaction)
  - ✅ P0观测点:`Category:` Tag 与子类一致,列表结果随类目更新
  - ✅ P0观测点:Shop 主类需向左滑动后才可见,滑动后可选中
  - ❌ 负向观测点:类别切换后筛选项冲突或无法应用
- **验证方法**：依次切换到 Jobs/Property/Cars/Services/Community/Shop,核对筛选项与场景匹配
- **关联规则**：[Marketplace探索列表页规则.md - 3.4 业务约束](../../业务规则库/通用规则/Marketplace探索列表页规则.md)

### 步骤5：地点筛选 - 搜索城市
- **页面位置**：筛选区地点筛选项(如 Abu Dhabi)
- **操作流程**：
  1. 点击地点筛选项(默认展示当前城市)
  2. 城市选择器弹出
  3. 在搜索框输入已知存在的城市名(如 Dubai)
  4. 选择搜索结果
  5. URL 路径段变化为 `/city-dubai/`
  6. Location Tag 更新为 Dubai
  7. 列表刷新
- **观测点**：
  - ✅ P0观测点:能搜到并选中已知城市
  - ✅ P0观测点:列表与 Location Tag 更新为所选城市
  - ✅ P0观测点:URL 拼接对应城市名的 citycode(如 `city-dubai`)
  - ❌ 负向观测点:输入明显无结果的字符串,展示无结果或不可选提示,页面不崩溃
- **验证方法**：输入城市名 → 选择结果 → 核对 URL/Tag/列表
- **关联规则**：[Marketplace探索列表页规则.md - 3.2 校验规则](../../业务规则库/通用规则/Marketplace探索列表页规则.md)

### 步骤6：地点筛选 - 滚动选择与首字母索引
- **页面位置**：城市选择器
- **操作流程**：
  1. 打开城市列表
  2. 向下滚动后选择可见城市
  3. 或点击某字母/拖动索引条
  4. 列表跳转至对应区间
  5. 选择城市
  6. URL/Tag/列表同步更新
- **观测点**：
  - ✅ P1观测点:滚动选择城市生效,列表刷新正确
  - ✅ P1观测点:点击字母或拖动索引条后,列表跳转至对应区间
  - ✅ P1观测点:选中城市应用正确
- **验证方法**：滚动/字母索引 → 选择城市 → 核对 URL/Tag/列表
- **关联规则**：[Marketplace探索列表页规则.md - 3.1 输入规则](../../业务规则库/通用规则/Marketplace探索列表页规则.md)

### 步骤7：价格筛选 - 仅输入 Min/Max/Min+Max
- **页面位置**：筛选区 Price
- **操作流程**：
  1. 点击 Price 打开面板
  2. 场景1:仅输入 Min 为合法数值(如 100),不填写 Max,点击应用
  3. 场景2:仅输入 Max 为合法数值(如 5000),不填写 Min,点击应用
  4. 场景3:同时填写 Min 与 Max(Min ≤ Max),点击应用
  5. 筛选项或 Tag 反映价格区间
  6. 列表刷新,仅展示符合价格条件的商品
- **观测点**：
  - ✅ P0观测点:仅填 Min 时,筛选项或 Tag 反映「下限」,列表符合「不低于所填最小值」
  - ✅ P0观测点:仅填 Max 时,Tag/筛选项反映「上限」,列表符合「不高于所填最大值」
  - ✅ P0观测点:同时填 Min 与 Max 时,列表仅展示价格落在 `[Min, Max]` 区间内的结果
  - ❌ 负向观测点:Min > Max 时,显示错误提示,阻止提交或提示修正
- **验证方法**：依次测试三种场景,抽样列表卡片价格,确认落在约定区间内
- **关联规则**：[Marketplace探索列表页规则.md - 3.2 校验规则](../../业务规则库/通用规则/Marketplace探索列表页规则.md)

### 步骤8：Transaction 与 Condition 筛选
- **页面位置**：筛选区 Transaction 和 Condition
- **操作流程**：
  1. 打开 Transaction,单选 Online,应用
  2. Transaction Tag 出现,列表刷新
  3. 进入 Condition 页面(如 `/city-abu-dhabi/cate-books/`),勾选多项(如 New + Used)
  4. 应用后查看列表
  5. 取消其中一项,列表随选项变化
- **观测点**：
  - ✅ P0观测点:Transaction 单选互斥,列表与 Tag 同步更新,URL 单参(如 `attr_149`)更新
  - ✅ P0观测点:Condition 多选逻辑与产品说明一致(AND/OR),列表随选项变化
  - ❌ 负向观测点:Transaction 与 Condition 组合过滤无互斥残留
- **验证方法**：Transaction 单选 → Condition 多选 → 组合过滤 → 核对列表结果
- **关联规则**：[Marketplace探索列表页规则.md - 3.1 输入规则](../../业务规则库/通用规则/Marketplace探索列表页规则.md)

### 步骤9：Filter 面板组合筛选
- **页面位置**：筛选区 Filter
- **操作流程**：
  1. 点击 Filter 打开面板
  2. 核对 Price、单选、多选等区块与外部状态一致
  3. 在 Filter 中设置价格与 Condition
  4. 切换类别到另一主类
  5. 应用
  6. 观察不适用项清空或禁用,无非法组合
- **观测点**：
  - ✅ P0观测点:面板展示与外部同步,修改后列表与 Filter 计数更新
  - ✅ P0观测点:Filter 内切换类别后筛选项合法,不适用项清空或禁用
  - ✅ P0观测点:仅价格/仅多选/全组合均行为正确,重置恢复默认
- **验证方法**：打开 Filter → 设置筛选 → 切换类别 → 应用 → 核对列表与计数
- **关联规则**：[Marketplace探索列表页规则.md - 3.4 业务约束](../../业务规则库/通用规则/Marketplace探索列表页规则.md)

### 步骤10：Tag 删除操作
- **页面位置**：筛选区下方 Tag 条
- **操作流程**：
  1. 确认 Tag 区存在类别 Tag(如 `Category:Marketplace`)
  2. 点击该 Tag 上的清除/×
  3. 观察 Tag 条、筛选行类别控件、列表结果
  4. 依次测试删除 Location Tag、Price Tag
- **观测点**：
  - ✅ P0观测点:类别 Tag 被移除或恢复默认,筛选行中类别与之一致,列表刷新
  - ✅ P0观测点:地点 Tag 被清除或恢复默认,Location Tag 消失或变为默认态,列表同步
  - ✅ P0观测点:价格 Tag 去除后,价格筛选被清除,列表回到未按该价格条件过滤的状态
  - ✅ P0观测点:删除单个 Tag 后,其它已选 Tag 保持不变(除非产品规则联动清空)
- **验证方法**：依次点击各 Tag 的× → 核对 Tag 条、筛选项、列表
- **关联规则**：[Marketplace探索列表页规则.md - 3.4 业务约束](../../业务规则库/通用规则/Marketplace探索列表页规则.md)

### 步骤11：列表卡片浏览与跳转
- **页面位置**：列表区
- **操作流程**：
  1. 抽查首屏多条卡片
  2. 确认每条包含标题、价格、封面区域
  3. 确认条件类标签(如 New / Used / Excellent)与业务含义一致
  4. 记录卡片标题文案
  5. 点击卡片主体区域进入详情
  6. 核对详情页展示与来源一致性
  7. 确认详情页打开的是新的标签页
- **观测点**：
  - ✅ P0观测点:卡片结构完整,价格币种展示正确(如 AED)
  - ✅ P0观测点:条件类标签(如 New / Used / Excellent)与业务含义一致
  - ✅ P0观测点:进入对应帖子详情 URL,详情标题或关键字段与列表一致
  - ✅ P0观测点:详情页打开的是新的标签页
- **验证方法**：抽查卡片字段 → 点击卡片 → 核对详情页
- **关联规则**：[Marketplace探索列表页规则.md - 5. 依赖模块](../../业务规则库/通用规则/Marketplace探索列表页规则.md)

### 步骤12：分页切换
- **页面位置**：列表底部分页区
- **操作流程**：
  1. 确认列表底部存在分页(如 `1 (current)`、`2`、`3`、`Next`)
  2. 点击 2 或 Next
  3. 观察 URL 或列表内容变化
  4. 确认当前页码高亮正确
- **观测点**：
  - ✅ P0观测点:翻页成功,当前页码高亮正确
  - ✅ P0观测点:URL 页码参数更新(如 `page=2`)
  - ✅ P0观测点:列表内容更新为下一页数据
- **验证方法**：点击页码 → 核对 URL/页码高亮/列表内容
- **关联规则**：[Marketplace探索列表页规则.md - 2. 核心流程](../../业务规则库/通用规则/Marketplace探索列表页规则.md)

## 3. 流程完整性验证清单

- [x] 验证首页金刚位「Marketplace」可见且 href 包含 cate-marketplace 与 iconSource
- [x] 验证从首页综合搜进入列表,默认类别为 All Categories,URL 无 iconSource
- [x] 验证 Marketplace 落地页默认筛选项展示(Best Match、Marketplace、Abu Dhabi)
- [x] 验证排序下拉四项文案与 sortList 一致
- [x] 验证 Best Match(sortId=0)、Newest First(sortId=1)、Lowest Price(sortId=3)、Highest Price(sortId=4)与 URL 一致
- [x] 验证列表结果排序符合语义(如 Lowest Price 时价格从低到高)
- [x] 验证切换子类后 URL、标题与筛选项同步
- [x] 验证类别筛选项切换至 Jobs/Property/Cars/Services/Community/Shop 并选择子类
- [x] 验证 Shop 主类需向左滑动后才可见
- [x] 验证城市搜索存在的城市成功选中
- [x] 验证城市搜索不存在的关键词显示无结果,不崩溃
- [x] 验证滚动城市列表选择生效
- [x] 验证城市首字母/字母索引快速定位
- [x] 验证 Price 仅输入 Min、仅输入 Max、同时输入 Min+Max
- [x] 验证 Price Min > Max 时显示错误提示
- [x] 验证 Transaction 单选切换,URL 单参更新
- [x] 验证 Condition 多选逻辑与产品一致
- [x] 验证 Price + Condition 组合过滤生效
- [x] 验证打开 Filter 面板与列表外显筛选同步
- [x] 验证 Filter 内切换类别后筛选项合法
- [x] 验证 Filter 仅价格/仅多选/全组合行为正确,重置恢复默认
- [x] 验证删除类别 Tag,筛选项与列表同步
- [x] 验证删除地点 Tag,筛选项与列表同步
- [x] 验证价格筛选后出现 Price Tag,删除 Price Tag 筛选被清除
- [x] 验证列表卡片字段完整性与链接可点
- [x] 验证点击卡片进入详情页 URL 与标题对应,新标签页打开
- [x] 验证列表分页切换,页码高亮正确
- [x] 验证弱网下首屏有骨架或加载态,最终内容可展示

## 4. 关联文档

- [通用业务全景](./通用业务全景.md)
- [Marketplace探索列表页规则](../../业务规则库/通用规则/Marketplace探索列表页规则.md)
- [All分类导航业务流程](./All分类导航业务流程.md)
- [首页搜索业务流程](./首页搜索业务流程.md)

## 5. 变更历史

| 日期 | 版本 | 变更内容 | 变更人 |
|-----|------|---------|--------|
| 2026-04-28 | v1.0 | 初始版本,基于 Marketplace 探索列表页测试用例生成 | AI |
