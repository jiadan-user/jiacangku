# AU站 列表卡片 Bed 图标和数量功能测试用例

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

说明：需要登录，验证学生公寓列表页卡片中 **Bed 图标和数量**的展示与功能。  
目标页面：https://au.58v5.cn/en/city-canberra/cate-student-apartment/?iconSource=student-apartment（学生公寓列表）。  
卡片选择器：`a[href*="cate-student-apartment-"]`。  
Bed 信息通常以图标 + 数字方式展示（如 🛏 1、Bed 2 等）。

---

## 测试用例

### TC001 列表卡片展示 Bed 图标和数量

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_bed_student_apartment.py::test_tc001_bed_icon_and_count_visible`）

**步骤**：打开学生公寓列表页，查看列表卡片内容。  
**预期**：每张卡片均展示 Bed 图标和数量信息（数量为正整数）。  
**验证**：Bed 数量元素可见，值为大于 0 的整数。

---

### TC002 Bed 数量取值合理

**优先级**：P1
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_bed_student_apartment.py::test_tc002_bed_count_value_reasonable`）

**步骤**：在列表页获取多张卡片的 Bed 数量。  
**预期**：Bed 数量为以下三种合理格式之一：
- 纯整数（如 1、6、8）：范围 1～50
- 数字+号（如 5+、8+）：表示至少 N 间
- 描述型文字（如 Studio）：学生公寓特有房型描述  

**验证**：Bed 信息字段为非空且符合上述格式之一，无负数或乱码。

---

### TC003 Bed 图标可见性

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_bed_student_apartment.py::test_tc003_bed_icon_visible_with_size`）

**步骤**：在列表页查看卡片 Bed 区域的图标展示。  
**预期**：Bed 图标（SVG/img）可见，与数量紧挨排列，无遮挡。  
**验证**：Bed 图标元素存在且 bounding_box 宽高大于 0（可见）。

---

### TC004 列表页 Bed 数量与详情页一致

**优先级**：P1
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_bed_student_apartment.py::test_tc004_bed_count_consistent_with_detail_page`）

**步骤**：记录列表页第一张卡片的 Bed 数量，点击进入详情页，查看详情页 Bed 数量。  
**预期**：列表页 Bed 数量与详情页展示一致。  
**验证**：两处 Bed 数量相同。

---

### TC005 Bed 数量为空或特殊情况处理

**优先级**：P2
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_bed_student_apartment.py::test_tc005_bed_missing_cards_handled_gracefully`）

**步骤**：查找 Bed 数量为空或显示特殊情况的卡片（如学生宿舍型房源）。  
**预期**：特殊情况下有合理展示（如 "—"、"Studio" 或无 Bed 信息），不崩溃、不报错。  
**验证**：特殊情况下不显示为乱码或空白，整体页面正常。

---

## 执行记录

| 执行时间 | 结果 | 说明 |
|----------|------|------|
| - | - | 待执行 |
