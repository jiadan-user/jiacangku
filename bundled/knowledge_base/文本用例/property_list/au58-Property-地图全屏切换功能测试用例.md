# AU站 Property 地图全屏切换功能测试用例

## 测试环境配置（必填）

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | au | 澳大利亚站 |
| 基础URL | https://au.58v5.cn | 测试站点地址 |
| 站点名称 | AU站（澳大利亚） | 用于日志展示 |
| 角色 | guest | 无需登录 |
| 账号名称 | guest_au | 用于 session 命名 |
| 测试账号 | 无 | 无需登录 |
| 测试密码 | 无 | 无需登录 |

**目标页面**：`https://au.58v5.cn/en/city-canberra/cate-buy/?iconSource=buy&view=map&viewport=c%3A-35.2802%2C149.1310%7Cz%3A11`

---

## 功能说明

地图视图提供全屏切换按钮，用户可将地图放大至全屏浏览，并可退出全屏恢复正常视图。

---

## 测试用例

### TC001 地图视图默认加载

**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_map_fullscreen.py::test_tc001_map_view_loads_correctly`）

**优先级**：P0
**类型**：smoke

**前置条件**：无需登录，直接访问目标 URL（含 `view=map` 参数）

**测试步骤**：
1. 打开目标页面
2. 等待地图加载完成

**预期结果**：
- 页面以地图模式展示
- URL 中包含 `view=map`
- 地图容器可见

---

### TC002 点击全屏按钮进入全屏模式

**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_map_fullscreen.py::test_tc002_click_fullscreen_button_enters_fullscreen`）

**优先级**：P0
**类型**：smoke

**前置条件**：已在地图视图页面

**测试步骤**：
1. 打开目标页面，等待地图加载
2. 找到全屏切换按钮（Expand/Fullscreen 图标）
3. 点击全屏按钮

**预期结果**：
- 地图进入全屏模式
- 全屏按钮图标变为退出全屏状态（或出现退出全屏按钮）
- 地图占满整个视口

---

### TC003 全屏模式下地图正常展示

**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_map_fullscreen.py::test_tc003_fullscreen_map_renders_correctly`）

**优先级**：P1
**类型**：smoke

**前置条件**：已进入全屏模式

**测试步骤**：
1. 打开目标页面，点击全屏按钮
2. 等待全屏模式加载完成
3. 验证地图内容

**预期结果**：
- 地图在全屏状态下正常渲染
- 地图上的 Pin 点/标记仍可见
- 无报错或白屏

---

### TC004 全屏模式下点击退出全屏按钮恢复正常视图

**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_map_fullscreen.py::test_tc004_click_exit_fullscreen_restores_normal_view`）

**优先级**：P0
**类型**：smoke

**前置条件**：已进入全屏模式

**测试步骤**：
1. 打开目标页面，点击全屏按钮进入全屏
2. 点击退出全屏按钮（Collapse/Exit Fullscreen 图标）

**预期结果**：
- 页面恢复为正常地图+列表布局
- 地图尺寸恢复正常
- 退出全屏按钮变回进入全屏状态

---

### TC005 全屏切换按钮持续可见

**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_map_fullscreen.py::test_tc005_fullscreen_button_always_visible`）

**优先级**：P1
**类型**：regression

**前置条件**：已在地图视图页面

**测试步骤**：
1. 打开目标页面
2. 验证全屏按钮可见性
3. 点击进入全屏，验证按钮仍可见
4. 点击退出全屏，验证按钮仍可见

**预期结果**：
- 无论全屏/非全屏状态，切换按钮始终可见
- 按钮尺寸合理，可点击

---

## 执行记录

| 用例 | 状态 | 执行时间 | 备注 | UI自动化 |
| ------ | ------ | ---------- | ------ | --- |
| TC001 | 待执行 | - | - | ✅ 可自动化 |
| TC002 | 待执行 | - | - | ✅ 可自动化 |
| TC003 | 待执行 | - | - | ✅ 可自动化 |
| TC004 | 待执行 | - | - | ✅ 可自动化 |
| TC005 | 待执行 | - | - | ✅ 可自动化 |
