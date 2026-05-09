# AU站 列表卡片位置邮编功能测试用例

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

说明：需要登录，验证列表卡片位置邮编展示与功能。  
目标页面：https://au.58v5.cn/en/city-canberra/cate-rent/?iconSource=rent  
**注**：租房列表（cate-rent）卡片选择器与买房列表不同，若租房列表无卡片则使用买房列表（cate-buy）验证。

---

## 测试用例

### TC001 列表页卡片展示位置/邮编

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_location.py::test_tc001_list_cards_show_location`）

**步骤**：打开列表页，查看列表卡片内容。  
**预期**：每条列表卡片均展示位置或邮编信息（ suburb/postcode 文案可见）。  
**验证**：每张卡片存在非空位置区域或邮编文案。

---

### TC002 列表卡片邮编格式正确

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_location.py::test_tc002_postcode_format_correct`）

**步骤**：在列表页查看卡片邮编展示。  
**预期**：邮编格式正确（澳大利亚邮编为 4 位数字，如 2600）。  
**验证**：邮编包含有效数字格式（4 位或符合 AU 规范）。

---

### TC003 列表卡片位置可读性

**优先级**：P1
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_location.py::test_tc003_location_readability`）

**步骤**：在列表页查看卡片位置/邮编文案。  
**预期**：位置文案清晰可读，字体大小适中，无遮挡。  
**验证**：位置元素可见且文案长度合理。

---

### TC004 列表卡片位置与详情页一致

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_location.py::test_tc004_location_matches_detail_page`）

**步骤**：记录列表页某张卡片的位置/邮编，点击进入详情页，查看详情页位置。  
**预期**：列表页位置与详情页位置一致。  
**验证**：两处 suburb/postcode 相同。

---

### TC005 位置为空或特殊情况处理

**优先级**：P1
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_location.py::test_tc005_location_special_cases`）

**步骤**：查找位置为空或显示特殊情况的卡片。  
**预期**：特殊情况下有合理的展示（如 "Contact for details" 等）。  
**验证**：特殊情况下有明确的文案提示，不显示为空白或错误。

---

## 执行记录

| 执行时间 | 结果 | 说明 |
|----------|------|------|
| - | - | 待执行 |
