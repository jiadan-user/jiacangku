# AU站 学生公寓列表 - 列表卡片房产类型功能测试用例

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
| 卡片定位器 | a[href*="cate-student-apartment"] |

---

## 功能说明

学生公寓列表卡片中展示房产类型（Property Type）标签：

- 定位：`.room-distance-type-item-label`（位于 `.room-distance-type` 末尾）
- 常见取值：`Student Apartment`、`Studio` 等
- 卡片链接 href 包含 `cate-student-apartment`

---

## 测试用例

### TC001 列表页卡片展示房产类型（学生公寓）

**步骤**：打开学生公寓列表页，统计卡片数量，获取第一张卡片的房产类型文本。
**预期**：列表至少有一张卡片，且第一张卡片房产类型文案非空。
**验证**：`get_list_card_links_count(path_part="cate-student-apartment") > 0`，`get_first_card_property_type_text` 非空。

---

### TC002 列表卡片房产类型取值合理（学生公寓）

**步骤**：获取第一张卡片房产类型文本，调用合理性校验。
**预期**：取值为系统支持的枚举值或合理英文字符串（`is_property_type_valid` 返回 True）。
**验证**：房产类型文案通过合理性校验，无乱码或异常值。

---

### TC003 列表卡片房产类型可读性（学生公寓）

**步骤**：获取第一张卡片房产类型文本，检查长度。
**预期**：文案清晰可读，长度小于 100 字符。
**验证**：`len(prop_type) < 100`。

---

### TC004 列表卡片房产类型与详情页一致（学生公寓）

**步骤**：记录列表页第一张卡片房产类型，点击进入详情页，检查详情页正文。
**预期**：详情页 body 文本中包含列表页的房产类型文案。
**验证**：`list_prop_type in detail_page.locator("body").inner_text()`。

---

### TC005 房产类型为空或特殊情况处理（学生公寓）

**步骤**：获取前 5 张卡片的房产类型文本列表。
**预期**：至少有一张卡片展示了有效的房产类型文案。
**验证**：`valid_count > 0`（valid_count 为非空、非空白文本的卡片数）。

---

## 执行记录

| 执行时间 | 结果 | 说明 |
|----------|------|------|
| - | - | 待执行 |
