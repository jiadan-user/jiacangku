# AU站 学生公寓列表 - 列表卡片房间型号功能测试用例

## 测试环境配置

| 字段 | 值 |
|------|-----|
| 站点 | au |
| 基础URL | https://au.58v5.cn |
| 站点名称 | AU站（澳大利亚） |
| 角色 | guest |
| 账号名称 | guest_au |
| 测试账号 | 无（无需登录） |
| 目标页面 | https://au.58v5.cn/en/city-canberra/cate-student-apartment/?iconSource=student-apartment |
| 卡片定位器 | a[href*="student-apartment"] |

说明：无需登录，直接访问学生公寓列表页验证列表卡片的房间型号展示。

---

## 功能说明

列表卡片中展示房间型号（Room Type）信息，紧靠在 Bed/Bath 图标行之后：

- 定位：`.room-distance-type-item`（无 img 子元素）内的 `.room-distance-type-item-label`
- 常见取值：`Studio`、`1–3 Bedroom Apartment`、`Student Apartment`（兜底值）等
- 详情页主信息区对应：`.MainInfo_item__ZNJ3X`（无 `img.MainInfo_icon__kiZFy`）内的 `.MainInfo_value__U8n3C`

---

## 测试用例

### TC001 列表卡片房间型号正常展示

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_room_type_student_apartment.py::test_tc001_room_type_visible`）

**步骤**：打开学生公寓列表页，等待卡片加载完成，检查前 5 张卡片是否有房间型号文本。
**预期**：至少有一张卡片展示房间型号文案（非空）。
**验证**：`.room-distance-type-item`（无 img）> `.room-distance-type-item-label` 文案非空。

---

### TC002 房间型号取值合理

**优先级**：P1
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_room_type_student_apartment.py::test_tc002_room_type_value_reasonable`）

**步骤**：获取列表中前 10 张卡片的房间型号文本。
**预期**：文案为非空英文字符串，长度在 1～100 字符之间，包含字母或数字，不含乱码或纯符号。
**验证**：所有能取到的房间型号文案均符合格式要求。
**录制样本**：`Studio`、`1–3 Bedroom Apartment`、`Student Apartment`

---

### TC003 房间型号文本元素可见性

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_room_type_student_apartment.py::test_tc003_room_type_element_visible`）

**步骤**：定位列表卡片中的房间型号文本元素。
**预期**：文本在视口内可见，元素尺寸 > 0，无遮挡。
**验证**：元素 getBoundingClientRect().width > 0 且 height > 0，visible = true。
**录制数据**：`Studio` 元素尺寸为 36.4375×18px，visible=True。

---

### TC004 房间型号与详情页一致

**优先级**：P1
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_room_type_student_apartment.py::test_tc004_room_type_consistent_with_detail_page`）

**步骤**：记录列表页第一张有房间型号文本的卡片值，点击进入详情页。
**预期**：详情页主信息区（MainInfo）展示的房间型号与列表页一致。
**验证**：列表页房间型号 == 详情页 `.MainInfo_item__ZNJ3X`（无 img）> `.MainInfo_value__U8n3C` 的值。
**录制验证**：列表 `Studio` == 详情 `Studio`。

---

### TC005 无房间型号的卡片正常展示（不崩溃）

**优先级**：P2
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_room_type_student_apartment.py::test_tc005_missing_room_type_cards_handled_gracefully`）

**步骤**：遍历前 10 张卡片，找到无独立房间型号字段的卡片（card[0] 第一张为特殊小卡片）。
**预期**：此类卡片仍正常可见，不因缺少房间型号而报错或布局异常，内部文本非空。
**验证**：card.inner_text().strip() 长度 > 0。
**录制发现**：card[0] 无 `.room-distance-type-item`（无 img）结构，但卡片正常展示价格和标题。

---

## 执行记录

| 执行时间 | 结果 | 说明 |
|----------|------|------|
| 2026-03-13 | 5 passed in 25.50s | 全部通过 |
