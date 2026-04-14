# AU站 列表卡片 Bathroom 图标和数量功能测试用例

## 测试环境配置

| 字段 | 值 |
|------|-----|
| 站点 | au |
| 基础URL | https://au.58v5.cn |
| 站点名称 | AU站（澳大利亚） |
| 角色 | buyer |
| 账号名称 | liuyue_buyer_au |
| 测试账号 | liuyue62@58.com |
| 测试密码 | Xindemima1% |

说明：需要登录，验证学生公寓列表页卡片中 **Bathroom 图标和数量**的展示与功能。  
目标页面：https://au.58v5.cn/en/city-canberra/cate-student-apartment/?iconSource=student-apartment（学生公寓列表）。  
卡片选择器：`a[href*="student-apartment"]`。  
Bathroom 图标使用 `Bathrooms.png`，数量展示在 `.room-distance-type-item-label` 中。  
已知格式：整数（如 1、2）、数字+号（如 5+）、描述型文字（如 Studio）。

---

## 测试用例

### TC001 列表卡片展示 Bathroom 图标和数量

**步骤**：打开学生公寓列表页，查看列表卡片内容。  
**预期**：每张卡片均展示 Bathroom 图标和数量信息（数量为正整数或合理描述）。  
**验证**：Bathroom 数量元素可见，值为非空字符串。

---

### TC002 Bathroom 数量取值合理

**步骤**：在列表页获取多张卡片的 Bathroom 数量。  
**预期**：Bathroom 数量为以下格式之一：
- 整数（如 1、2、3、4、5）：范围 1～50
- 小数（如 1.5、2.5、3.5、4.5、5.5）：半卫生间格式，小数部分仅为 0.5
- 数字+号（如 5+、5.5+）：表示至少 N 个
- 描述型文字（如 shared）：共享卫生间描述  

**验证**：Bathroom 信息字段为非空且符合上述格式之一，无负数或乱码。

---

### TC003 Bathroom 图标可见性

**步骤**：在列表页查看卡片 Bathroom 区域的图标展示。  
**预期**：Bathroom 图标（img[src*="Bathrooms"]）可见，与数量紧挨排列，无遮挡。  
**验证**：Bathroom 图标元素存在且 bounding_box 宽高大于 0（18×18px）。

---

### TC004 列表页 Bathroom 数量与详情页一致

**步骤**：记录列表页第一张有 Bathroom 信息的卡片数量，点击进入详情页，查看详情页 Bathroom 数量。  
**预期**：列表页 Bathroom 数量与详情页主信息区展示一致。  
**验证**：两处 Bathroom 数量相同（详情页取 MainInfo 区，非推荐卡片区）。

---

### TC005 Bathroom 数量为空或特殊情况处理

**步骤**：查找 Bathroom 数量为空或无图标的卡片（如 Studio 型学生公寓）。  
**预期**：特殊情况下有合理展示，不崩溃、不报错，页面正常。  
**验证**：无 Bathroom 图标的卡片仍可见且有非空文本内容，整体页面正常。

---

## 执行记录

| 执行时间 | 结果 | 说明 |
|----------|------|------|
| - | - | 待执行 |
