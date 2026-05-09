# AU站 Property 地图模式卡片数量功能测试用例

## 测试环境配置（必填）

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | au | 澳大利亚站 |
| 基础URL | https://au.58v5.cn | 测试站点地址 |
| 站点名称 | AU站（澳大利亚） | 日志展示用 |
| 角色 | guest | 无需登录 |
| 账号名称 | guest_au | session 命名用 |
| 测试账号 | 无 | 无需登录 |
| 测试密码 | 无 | 无需登录 |

---

## 测试说明

**功能描述**：验证地图模式下左侧卡片列表数量与结果徽标（badge）的一致性关系，包括：单页卡片数量限制、分页后数量约束、从列表视图切换后数量一致性等核心场景。

**测试入口 URL**：
`https://au.58v5.cn/en/city-canberra/cate-property/?iconSource=rent&view=map&viewport=c%3A-35.2802%2C149.1310%7Cz%3A11`

**录制数据（2026-03-20 实测，Canberra / Rent）**：
- 结果徽标（badge）：33 results
- 左侧列表第1页卡片数：24（每页最大限制）
- 左侧列表第2页卡片数：9
- 总数关系：24 + 9 = 33（与 badge 一致）

**关键 DOM 元素**：
- 结果数量徽标：`.MapView_resultsBadge__yvMxa`（显示 "N results"）
- 左侧卡片面板：`.PropertyList_listPanel__Vq3yB`（包含所有卡片 `<a>` 链接）
- 地图视图容器：`.MapView_mapView__oebEi`
- 地图容器：`.gm-style`
- Map 切换按钮：`button[name="Map"]`（`page.getByRole('button', { name: 'Map' }).click()`）
- 分页 Next 按钮：`page.getByRole('button', { name: 'Next' })`

**数量约束规则**：
- 左侧卡片数（当前页） ≤ 结果徽标总数（分页展示，每页最多 24 张）
- 结果徽标格式：`\d+ results`（如 "33 results"）
- 每页最大卡片数：24

---

## 测试用例

### TC001 左侧卡片数量不超过结果徽标数字

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_map_card_count.py::test_left_card_count_le_badge_number`）

**前提条件**：浏览器新标签，直接访问地图模式 URL（含 `view=map` 参数）

**测试步骤**：
1. 打开目标 URL（含 `view=map&viewport` 参数）
2. 处理 Cookie 弹窗（如出现）
3. 等待地图容器（`.gm-style`）加载完成
4. 获取结果数量徽标文本（`.MapView_resultsBadge__yvMxa`），提取数字（如 33）
5. 统计左侧面板（`.PropertyList_listPanel__Vq3yB`）内 `a[href*="cate-property"]` 的数量（如 24）
6. 验证：左侧卡片数量 ≤ 结果徽标数字

**预期结果**：
- 结果徽标数字 > 0
- 左侧卡片数量 > 0
- 左侧卡片数量（24） ≤ 结果徽标数字（33）

---

### TC002 结果徽标正确展示房源总数

**优先级**：P1
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_map_card_count.py::test_results_badge_displays_correctly`）

**前提条件**：地图视图已加载完成

**测试步骤**：
1. 打开目标 URL
2. 等待地图加载完成
3. 验证结果数量徽标（`.MapView_resultsBadge__yvMxa`）可见
4. 获取徽标文本，验证格式为 `N results`（正则：`\d+\s+results?`）
5. 验证提取的数字 > 0

**预期结果**：
- 结果徽标可见
- 文本格式为 "N results"（N > 0）
- 实测值：33 results

---

### TC003 左侧卡片第1页数量不超过每页最大限制（24张）

**优先级**：P1
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_map_card_count.py::test_left_card_page_limit`）

**前提条件**：直接访问含 `view=map` 的地图模式 URL

**测试步骤**：
1. 打开目标 URL
2. 等待地图加载完成
3. 统计左侧面板第1页卡片数量
4. 验证：0 < 卡片数量 ≤ 24
5. 滚动左侧卡片列表到底部
6. 验证分页 Next 按钮可见（说明有多页数据）

**预期结果**：
- 第1页卡片数量 > 0 且 ≤ 24
- 分页 Next 按钮可见（当总数 > 24 时）
- 实测值：24 张（满页）

---

### TC004 翻到第2页后卡片数量仍满足约束

**优先级**：P1
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_map_card_count.py::test_second_page_card_count`）

**前提条件**：地图视图已加载，总房源数 > 24（存在第2页）

**测试步骤**：
1. 打开目标 URL
2. 等待地图加载完成
3. 获取结果徽标总数（如 33）
4. 记录第1页卡片数量（如 24）
5. 滚动到底部，点击 Next 翻到第2页
6. 等待第2页卡片渲染（约 2s）
7. 统计第2页卡片数量（如 9）
8. 验证：第2页卡片数量 > 0 且 ≤ 结果徽标总数

**预期结果**：
- 第2页卡片数量 > 0
- 第2页卡片数量 ≤ 结果徽标总数（33）
- 实测值：9 张（不满页，为最后一页）

---

### TC005 从列表视图切换到地图视图后数量关系正确

**优先级**：P2
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_map_card_count.py::test_switch_to_map_view_card_count`）

**前提条件**：初始为列表视图（URL 不含 `view=map` 参数）

**测试步骤**：
1. 打开列表视图 URL：`https://au.58v5.cn/en/city-canberra/cate-property/?iconSource=rent`
2. 处理 Cookie 弹窗
3. 点击 Map 切换按钮（`page.getByRole('button', { name: 'Map' }).click()`）
4. 等待地图容器（`.gm-style`）加载完成（最多 30s）
5. 验证 URL 包含 `view=map` 参数
6. 获取结果徽标数字
7. 统计左侧卡片数量
8. 验证：卡片数量 ≤ 结果徽标数字

**预期结果**：
- 切换后地图正常加载
- URL 包含 `view=map`
- 结果徽标数字 > 0
- 左侧卡片数量 ≤ 结果徽标数字

---

## 执行记录

| 用例 | 执行日期 | 结果 | 备注 | UI自动化 |
| ------ | --------- | ------ | ------ | --- |
| TC001 | - | - | - | ✅ 可自动化 |
| TC002 | - | - | - | ✅ 可自动化 |
| TC003 | - | - | - | ✅ 可自动化 |
| TC004 | - | - | - | ✅ 可自动化 |
| TC005 | - | - | - | ✅ 可自动化 |
