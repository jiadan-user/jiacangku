# AU站 Property 地图加载状态功能测试用例

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

**功能描述**：验证地图视图模式下地图的加载状态，包括：地图容器正常渲染、结果数量展示、Pin 点标记加载、地图控件可用性、视图切换后地图重载等核心场景。

**测试入口 URL**：
`https://au.58v5.cn/en/city-canberra/cate-buy/?iconSource=buy&view=map&viewport=c%3A-35.2802%2C149.1310%7Cz%3A11`

**关键 DOM 元素**：
- 地图容器：`.gm-style`（Google Maps 渲染层）
- 地图外框：`.MapView_mapView__oebEi`
- 结果数量徽标：`.MapView_resultsBadge__yvMxa`（显示 "X results"）
- 地图 Pin 点：`img[alt="bottom icon"]`、`img[alt="sale marker"]`
- 地图控件组：`.MapControls_controls__o6ToG`
- 地图视图切换按钮：`button[class*="mapButton"]`（Map 按钮）
- 列表视图切换按钮：`button[class*="listButton"]`（List 按钮）

---

## 测试用例

### TC001 地图容器正常加载渲染

**前提条件**：浏览器新标签，未访问过该页面

**测试步骤**：
1. 打开目标 URL（含 `view=map` 参数）
2. 等待页面加载完成
3. 验证地图容器（`.gm-style`）可见
4. 验证地图外框（`.MapView_mapView__oebEi`）存在
5. 验证 URL 包含 `view=map` 参数

**预期结果**：
- 地图容器可见，无白屏/错误状态
- URL 参数正确

---

### TC002 地图结果数量徽标正常展示

**前提条件**：地图视图已加载完成

**测试步骤**：
1. 打开目标 URL
2. 等待地图加载完成
3. 获取结果数量徽标文本（`.MapView_resultsBadge__yvMxa`）
4. 验证文本非空且包含数字（如 "9 results"）

**预期结果**：
- 结果数量徽标可见
- 文本格式为 "N results"（N > 0）

---

### TC003 地图 Pin 点标记正常渲染

**前提条件**：地图视图已加载完成，当前视口范围内有房产数据

**测试步骤**：
1. 打开目标 URL
2. 等待地图加载完成
3. 统计页面中 Pin 点数量（`img[alt="bottom icon"]`、`img[alt="sale marker"]`）
4. 验证至少有 1 个 Pin 点可见

**预期结果**：
- 地图上显示至少 1 个价格 Pin 点标记
- Pin 点位于地图区域内

---

### TC004 地图控件正常加载（缩放/定位按钮）

**前提条件**：地图视图已加载完成

**测试步骤**：
1. 打开目标 URL
2. 等待地图加载完成
3. 验证地图控件容器（`.MapControls_controls__o6ToG`）可见
4. 统计控件按钮数量（应有 4 个：全屏、放大、缩小、定位）
5. 验证全屏按钮、缩放按钮均可见

**预期结果**：
- 地图控件容器可见
- 含 4 个功能按钮（全屏、放大、缩小、定位）

---

### TC005 从列表视图切换到地图视图后地图正常加载

**前提条件**：初始为列表视图（URL 含 `view=list` 或去掉 `view` 参数）

**测试步骤**：
1. 打开列表视图 URL：`https://au.58v5.cn/en/city-canberra/cate-buy/?iconSource=buy`
2. 验证当前为列表视图（List 按钮处于激活状态）
3. 点击 Map 切换按钮
4. 等待地图加载完成
5. 验证地图容器（`.gm-style`）可见
6. 验证 URL 包含 `view=map` 参数

**预期结果**：
- 切换后地图正常加载渲染
- URL 更新为含 `view=map` 的地址
- 地图 Pin 点可见

---

## 执行记录

| 用例 | 执行日期 | 结果 | 备注 |
|------|---------|------|------|
| TC001 | - | - | - |
| TC002 | - | - | - |
| TC003 | - | - | - |
| TC004 | - | - | - |
| TC005 | - | - | - |
