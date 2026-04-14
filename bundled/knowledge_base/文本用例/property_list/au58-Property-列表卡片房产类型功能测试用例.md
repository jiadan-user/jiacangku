# AU站 列表卡片房产类型功能测试用例

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

说明：需要登录，验证列表卡片房产类型展示与功能。  
- **租房列表**：https://au.58v5.cn/en/city-canberra/cate-rent/?iconSource=rent  
- **买房列表（sale）**：https://au.58v5.cn/en/city-canberra/cate-buy/?iconSource=buy  
- **学生公寓**：https://au.58v5.cn/en/city-canberra/cate-student-apartment/?iconSource=student-apartment  
房产类型通常为 House、Unit、Apartment、Townhouse、Villa、Student 等；列表卡片选择器 path 不同（cate-property-for-rent- / cate-property-for-sale- / cate-student-apartment）。

---

## 测试用例

### TC001 列表页卡片展示房产类型

**步骤**：打开列表页，查看列表卡片内容。  
**预期**：每条列表卡片均展示房产类型信息（如 House、Unit、Apartment 等文案可见）。  
**验证**：每张卡片存在非空房产类型区域或类型文案。

---

### TC002 列表卡片房产类型取值合理

**步骤**：在列表页查看卡片房产类型展示。  
**预期**：房产类型为系统支持的枚举值（如 House、Unit、Apartment、Townhouse、Villa、Studio 等）。  
**验证**：类型文案在已知类型集合内或为合理英文单词。

---

### TC003 列表卡片房产类型可读性

**步骤**：在列表页查看卡片房产类型文案。  
**预期**：类型文案清晰可读，字体大小适中，无遮挡。  
**验证**：类型元素可见且文案长度合理（通常 1～2 个单词）。

---

### TC004 列表卡片房产类型与详情页一致

**步骤**：记录列表页某张卡片的房产类型，点击进入详情页，查看详情页房产类型。  
**预期**：列表页房产类型与详情页一致。  
**验证**：两处类型文案相同或语义一致（如 Apartment / Unit 按业务约定可视为一致时需说明）。

---

### TC005 房产类型为空或特殊情况处理

**步骤**：查找房产类型为空或显示特殊情况的卡片。  
**预期**：特殊情况下有合理的展示（如 "Contact for details"、"-" 或默认类型）。  
**验证**：特殊情况下有明确文案或占位，不显示为空白或错误。

---

## 执行记录

| 执行时间 | 结果 | 说明 |
|----------|------|------|
| - | - | 待执行 |
