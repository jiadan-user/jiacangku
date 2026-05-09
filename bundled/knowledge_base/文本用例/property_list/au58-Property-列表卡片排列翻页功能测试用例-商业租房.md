# AU站 商业地产租房列表 - 列表卡片排列翻页功能测试用例

## 测试环境配置

| 字段 | 值 |
|------|-----|
| 站点 | au |
| 基础URL | https://au.58v5.cn |
| 站点名称 | AU站（澳大利亚） |
| 角色 | guest |
| 账号名称 | guest_au |
| 测试账号 | 无（无需登录） |
| 目标页面 | https://au.58v5.cn/en/city-canberra/cate-commercial-rent/?iconSource=commercial-rent |
| 卡片定位器 | a[href*="cate-commercial"], a[href*="cate-land-development-rent"] |

---

## 功能说明

商业地产租房列表页支持：
- **网格排列**：一行展示 4 个卡片（数据量充足时）
- **翻页**：底部分页条含 Next 按钮和页码按钮
- **视图切换**：List（列表）↔ Map（地图）切换，URL 含 `view=map` 参数

---

## 测试用例

### TC001 列表卡片排列 - 一行展示4个卡片

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_sort_pagination_commercial_rent.py::test_tc001_list_layout_4_cards_per_row`）

**步骤**：打开商业地产租房列表页，等待卡片加载，检测各卡片 y 坐标，统计与第一张卡片同行的卡片数（y 差 < 50px 视为同行）。
**预期**：第一行至少有 1 张卡片，期望 4 张（数据量少时可能不足4个）。
**验证**：`first_row_count >= 1`。

---

### TC002 分页 - 有多页时 Next 按钮可见

**优先级**：P1
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_sort_pagination_commercial_rent.py::test_tc002_pagination_next_visible_when_has_multiple_pages`）

**步骤**：滚动到页面底部分页区域，检查 Next 按钮可见性。
**预期**：当列表有多页时，Next 按钮可见；若仅一页则跳过本用例。
**验证**：`is_pagination_next_visible() == True`（仅一页时 `pytest.skip`）。

---

### TC003 分页 - 点击 Next 后 URL 更新

**优先级**：P1
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_sort_pagination_commercial_rent.py::test_tc003_pagination_click_next_url_updates`）

**步骤**：确认有多页，记录翻页前 URL，点击 Next 按钮，记录翻页后 URL。
**预期**：翻页后 URL 发生变化，或 URL 中含分页参数（`page`/`p=`）。
**验证**：`url_before != url_after` 或 URL 含分页标识。

---

### TC004 分页 - 点击页码 2 进入第二页，布局保持

**优先级**：P1

**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_sort_pagination_commercial_rent.py::test_tc001_list_layout_4_cards_per_row`）

**步骤**：确认有多页，点击页码 2，验证第二页有卡片展示。
**预期**：跳转到第二页后，仍有卡片展示（布局保持网格）。
**验证**：`get_commercial_card_count() > 0`。

---

### TC005 视图切换 - 点击 Map 切换到地图视图

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_sort_pagination_commercial_rent.py::test_tc005_click_map_button_switches_to_map_view`）

**步骤**：确认当前为列表视图，点击 Map 按钮，检查 URL 和视图状态。
**预期**：切换后 URL 含 `view=map`，地图视图激活。
**验证**：`is_map_view_active() == True`。

---

### TC006 视图切换 - 点击 List 切换回列表视图

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_sort_pagination_commercial_rent.py::test_tc006_click_list_button_switches_back_to_list_view`）

**步骤**：先切换到地图视图，再点击 List 按钮，检查 URL 和卡片展示。
**预期**：切换回列表视图后，URL 不含 `view=map`，列表卡片重新展示。
**验证**：`is_map_view_active() == False`，`get_commercial_card_count() > 0`。

---

## 执行记录

| 执行时间 | 结果 | 说明 |
|----------|------|------|
| - | - | 待执行 |
