# AU站 Property 地图模式房源点数量功能测试用例

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

**功能描述**：验证地图模式下房源点（Pin 点）的数量展示功能，包括：Pin 点总数与结果徽标一致性、Pin 点含价格文字、Pin 点带 Rent 类型标识、缩放后 Pin 点数量稳定、从列表视图切换后 Pin 点正常加载。

**测试入口 URL**：
`https://au.58v5.cn/en/city-canberra/cate-property/?iconSource=rent&view=map&viewport=c%3A-35.2802%2C149.1310%7Cz%3A11`

**录制数据（2026-03-20 实测，Canberra / Rent）**：
- 结果徽标（badge）：33 results
- 地图 Pin 点总数：33 个（`img[alt="bottom icon"]`）
- Sale Marker 数量：0（Rent 页面无 sale marker）
- Pin 点类型 class：`PropertyMarker_rent__9TYMC`（橙色）
- 缩放前后 Pin 点总数：均为 33（视口内房源不变）

**关键 DOM 元素**：
- 结果数量徽标：`.MapView_resultsBadge__yvMxa`（显示 "N results"）
- Pin 点容器：`[class*="PropertyMarker_markerWrapper"]`（共 N 个）
- Rent 类型 Pin 点：`[class*="PropertyMarker_rent"]`（橙色圆角标签）
- Pin 点价格文字：`.PropertyMarker_priceText__M8l6x`（如 "132"、"5K+"）
- bottom icon（Rent Pin 底部图标）：`img[alt="bottom icon"]`
- sale marker（Sale Pin 底部图标）：`img[alt="sale marker"]`
- 地图放大按钮：控制区域第2个按钮（index=1），`button.MapControls_controlButton__RjUAL`
- 地图缩小按钮：控制区域第3个按钮（index=2）

**数量规则**：
- `Pin 点总数（bottom icon + sale marker）= 结果徽标数字`
- Rent 页面所有 Pin 点均有 `PropertyMarker_rent` class
- 每个 Pin 点均有价格文字（`.PropertyMarker_priceText__M8l6x` 非空）
- 缩放操作（同视口范围内）不改变 Pin 点总数

---

## 测试用例

### TC001 地图 Pin 点总数与结果徽标数字相等

**前提条件**：直接访问含 `view=map` 参数的地图模式 URL

**测试步骤**：
1. 打开目标 URL
2. 处理 Cookie 弹窗（如出现）
3. 等待地图加载完成（`.gm-style` 出现）
4. 统计 Pin 点总数：`img[alt="bottom icon"]` 数量 + `img[alt="sale marker"]` 数量
5. 获取结果徽标数字（`.MapView_resultsBadge__yvMxa`）
6. 验证：Pin 点总数 = 结果徽标数字

**预期结果**：
- Pin 点总数 > 0
- Pin 点总数 = 结果徽标数字（实测：33 = 33）

---

### TC002 所有 Pin 点均显示价格文字

**前提条件**：地图视图已加载完成，Pin 点已渲染

**测试步骤**：
1. 打开目标 URL
2. 等待地图加载完成
3. 获取所有 Pin 点容器（`[class*="PropertyMarker_markerWrapper"]`）
4. 检查每个 Pin 点的 `.PropertyMarker_priceText__M8l6x` 元素文字是否非空
5. 验证：有价格文字的 Pin 点数量 = Pin 点总数

**预期结果**：
- 每个 Pin 点均显示价格文字（如 "132"、"5K+"、"100M+"）
- 无空白 Pin 点（价格文字非空率 = 100%）

---

### TC003 Rent 页面所有 Pin 点均带 Rent 类型 class

**前提条件**：访问 Rent（租房）类型的地图模式页面

**测试步骤**：
1. 打开目标 URL（`iconSource=rent`）
2. 等待地图加载完成
3. 统计所有含 `PropertyMarker_rent` class 的 Pin 点数量
4. 获取 Pin 点总数
5. 验证：Rent 类型 Pin 点数量 = Pin 点总数（且 Sale 类型 Pin 点数量 = 0）

**预期结果**：
- 所有 Pin 点均含 `PropertyMarker_rent` class（橙色）
- `img[alt="sale marker"]` 数量 = 0（无蓝色 Sale Pin）
- 实测：33 个 Rent Pin，0 个 Sale Pin

---

### TC004 地图缩放后 Pin 点总数与 badge 保持一致

**前提条件**：地图视图已加载，zoom=11，视口内包含全部 33 条房源

**测试步骤**：
1. 打开目标 URL（zoom=11）
2. 等待地图加载，记录 Pin 点总数（如 33）
3. 点击缩小按钮（`MapControls_controlButton__RjUAL` index=2），zoom 变为 10
4. 等待地图数据重新加载（2s）
5. 再次统计 Pin 点总数
6. 获取结果徽标数字
7. 验证：缩放后 Pin 点总数 = 结果徽标数字

**预期结果**：
- 缩小后 URL 中 `z:10`（zoom 已更新）
- Pin 点总数与 badge 保持相等（当视口内房源不变时）
- 实测：zoom 11→10，Pin 点 33→33（Canberra 数据仍在视口内）

---

### TC005 从列表视图切换到地图视图后 Pin 点正常加载

**前提条件**：初始为列表视图（URL 不含 `view=map`）

**测试步骤**：
1. 打开列表视图 URL：`https://au.58v5.cn/en/city-canberra/cate-property/?iconSource=rent`
2. 处理 Cookie 弹窗
3. 点击 Map 切换按钮（`page.getByRole('button', { name: 'Map' }).click()`）
4. 等待地图容器（`.gm-style`）加载完成（最多 30s）
5. 等待 Pin 点渲染（`img[alt="bottom icon"]` 出现）
6. 统计 Pin 点总数
7. 获取结果徽标数字
8. 验证：Pin 点总数 = 结果徽标数字，且 > 0

**预期结果**：
- 切换后地图正常加载，URL 包含 `view=map`
- Pin 点渲染完成，至少 1 个可见
- Pin 点总数 = 结果徽标数字

---

## 执行记录

| 用例 | 执行日期 | 结果 | 备注 |
|------|---------|------|------|
| TC001 | - | - | - |
| TC002 | - | - | - |
| TC003 | - | - | - |
| TC004 | - | - | - |
| TC005 | - | - | - |
