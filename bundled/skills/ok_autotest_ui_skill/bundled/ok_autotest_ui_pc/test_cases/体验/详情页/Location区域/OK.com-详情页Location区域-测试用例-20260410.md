# OK.com 详情页 Location 区域 - 测试用例

## 文档信息

- **项目名称**：OK.com
- **测试模块**：详情页 - Location（位置 / 地图）区域
- **文档版本**：v1.0
- **创建日期**：2026-04-10
- **测试环境**：AE 预览站（58v5）
- **测试角色**：访客（Visitor）
- **进入路径**：首页（实际重定向至城市首页）→ 非招聘、非房产类目详情页

---

## 测试环境配置

```yaml
site: ae
site_name: AE 预览站 (58v5)
base_url: https://ae.58v5.cn
role: visitor
session_name: visitor_ae_58v5
需要登录: 否
入口 URL: https://ae.58v5.cn
测试详情页 URL: https://ae.58v5.cn/en/city-abu-dhabi/cate-cell-phone-cases/123-2041800180981948416/
类目说明: Marketplace > Electronics > Cell Phone Accessories > Cell Phone Cases（非招聘、非房产）
```

---

## Application Overview - 详情页 Location 区域

### 功能定位

Location 区域用于在详情页集中展示与地点相关的信息，并提供「在地图中查看」的能力，帮助买家确认线下位置或地标。

### 业务价值

1. **位置可发现性**：在详情信息流中单独突出「Location」，与描述、发布者等模块并列。
2. **地图核验**：通过内嵌地图（本环境实测为 Google Maps）辅助用户理解地理信息。
3. **与主信息对齐**：地址类文案在主信息区与 Location 模块中应保持一致，降低认知成本。

### 页面状态枚举

- **有地址 + 可展示地图**：展示地址文案与「Show map」入口；点击后打开全屏地图模态。
- **地图模态打开**：全屏 `modal-fullscreen`，内嵌 Google Maps（`gm-style` 等结构），提供返回/关闭控件。
- **地图模态关闭**：返回详情页，Location 模块仍可按需再次打开地图。

### 业务规则（基于本页实测）

1. **模块结构**：`LocationCard_locationCard__rZmTq` 容器内自上而下为：标题「Location」→ 地址文案 →「Show map」预览区与按钮。
2. **标题文案**：标题节点 class 含 `LocationCard_title__6haRB`、`locationTitle`，展示文案为 **`Location`**（英文）。
3. **地址展示**：地址容器 `LocationCard_address__SJx_4`，本页实测文案为 **`Al-Az Pest Control Company`**（与主信息区 `MainInfo_address__TSTas` 文案一致）。
4. **地图入口**：`LocationCard_showMapBtn__sgjv4` 按钮文案为 **`Show map`**；外围存在高度约 145px 的预览卡片区域（`LocationCard_pcShowMapCard__KCxk4` / `LocationCard_showMap__15yGP`）。
5. **地图模态**：点击「Show map」后出现 Bootstrap 风格全屏模态（`modal-dialog modal-fullscreen`，模态根节点 class 含 `LocationCard_modalMap__PhyVC`）；地图区域为 **Google Maps**（页面内出现 `maps.gstatic.com`、`gm-style` 等典型结构）。
6. **关闭地图**：点击模态内左上角 **`alt="close"`** 的返回图片（`img.LocationCard_back__8OIyE`）后，带 `show` 的模态消失（实测 **`Escape` 键不会关闭** 该模态）。

### 模块划分

1. [P0] **基础展示**：标题、地址、Show map 区域布局与文案。
2. [P0] **地图模态**：打开全屏地图、Google Maps 渲染、关闭返回详情页。
3. [P1] **一致性**：主信息区地址与 Location 地址一致。
4. [P2] **无障碍 / 键盘**：地图区域存在 `aria-label="Map"` 的语义节点；`Escape` 关闭行为以本页实测为准（未关闭则记为不支持或缺陷，见下方用例）。

---

## 测试用例

### 模块 A：基础展示与信息结构

#### TC-LOCATION-A-001：Location 模块整体可见且结构完整

- **优先级**：P0
- **前置条件**：访客身份；从 `https://ae.58v5.cn` 进入站点，导航至**非招聘、非房产**的详情页（本文件配置块中的测试 URL 可作为基准样例）。
- **测试步骤**：
  1. 打开测试详情页 URL。
  2. 向下滚动至出现「Description」等详情内容之后区域。
  3. 观察 **Location** 卡片区域。

- **预期结果**：✅ 实测
  - 页面存在 class 包含 `LocationCard_locationCard__rZmTq` 的 Location 卡片容器。
  - 卡片整体尺寸约 **宽 667px、高 228px**（视口宽度 1440px 条件下，相对主内容列左侧对齐约 x=152）。
  - 卡片内自上而下可见：**Location** 标题 → 地址一行文案 → **Show map** 区域（含按钮）。

- **自动化可行性**：✅ 高（稳定 class 前缀可作为定位辅证，建议结合标题/按钮文案断言）。

---

#### TC-LOCATION-A-002：Location 标题文案

- **优先级**：P0
- **前置条件**：同 TC-LOCATION-A-001。
- **测试步骤**：
  1. 定位 Location 卡片内标题节点（class 含 `LocationCard_title__6haRB` 与 `locationTitle`）。
  2. 读取其可见文本。

- **预期结果**：✅ 实测
  - 标题可见文本为 **`Location`**（与页面语言一致，本页为英文）。

- **自动化可行性**：✅ 高。

---

#### TC-LOCATION-A-003：地址文案展示

- **优先级**：P0
- **前置条件**：同 TC-LOCATION-A-001。
- **测试步骤**：
  1. 在 Location 卡片内定位 `LocationCard_address__SJx_4` 元素。
  2. 读取其文本内容。

- **预期结果**：✅ 实测
  - 地址文案为 **`Al-Az Pest Control Company`**。
  - 元素高度约 **21px**，宽度与主内容列一致（约 **667px**）。

- **自动化可行性**：✅ 高（样例数据随帖子变化，自动化应断言「非空 + 与主信息区地址一致」而非写死常量）。

---

#### TC-LOCATION-A-004：Show map 预览区与按钮

- **优先级**：P0
- **前置条件**：同 TC-LOCATION-A-001。
- **测试步骤**：
  1. 在 Location 卡片内查找 `LocationCard_showMap__15yGP` 或 `LocationCard_pcShowMapCard__KCxk4` 区域。
  2. 查找 `LocationCard_showMapBtn__sgjv4` 按钮并读取文案。

- **预期结果**：✅ 实测
  - 预览区域高度约 **145px**，宽度约 **667px**。
  - 按钮文案为 **`Show map`**；按钮区域约 **宽 157px、高 44px**（位于预览区中部偏下，本页约 x=407, y=1251）。

- **自动化可行性**：✅ 高。

---

### 模块 B：地图模态（Show map）交互

#### TC-LOCATION-B-001：点击 Show map 打开全屏地图模态

- **优先级**：P0
- **前置条件**：同 TC-LOCATION-A-001；页面已滚动使「Show map」按钮在视口内。
- **测试步骤**：
  1. 点击 `LocationCard_showMapBtn__sgjv4`（或文案为「Show map」的按钮）。
  2. 等待地图初始化（建议等待 2–5 秒）。
  3. 检查是否存在带 `show` class 的模态根节点（class 含 `LocationCard_modalMap__PhyVC`）。

- **预期结果**：✅ 实测
  - 出现全屏模态：`modal-dialog modal-fullscreen` 结构。
  - 模态根节点 class 包含 **`fade LocationCard_modalMap__PhyVC modal show`**。
  - 模态 `modal-body` 内存在 **`id="map"`** 的容器，并渲染 **Google Maps** 相关 DOM（例如 **`gm-style`**、资源域名 **`maps.gstatic.com`**）。

- **自动化可行性**：✅ 中高（建议断言模态 `show` + `#map` + `.gm-style` 之一组合）。

---

#### TC-LOCATION-B-002：地图模态内存在关闭/返回入口

- **优先级**：P0
- **前置条件**：已按 TC-LOCATION-B-001 打开地图模态。
- **测试步骤**：
  1. 在模态内查找左上角关闭/返回图标。

- **预期结果**：✅ 实测
  - 存在 **`img.LocationCard_back__8OIyE`**，`alt` 属性为 **`close`**（用于关闭模态）。

- **自动化可行性**：✅ 高。

---

#### TC-LOCATION-B-003：点击关闭图标关闭地图模态

- **优先级**：P0
- **前置条件**：地图模态已打开。
- **测试步骤**：
  1. 点击 `img.LocationCard_back__8OIyE`（或 `img[alt='close']`）。
  2. 等待动画结束（建议 ≥1s）。
  3. 检查是否仍存在 `LocationCard_modalMap__PhyVC.modal.show`。

- **预期结果**：✅ 实测
  - 打开后 `LocationCard_modalMap__PhyVC.modal.show` 匹配 **1** 个可见模态。
  - 点击关闭后，**不再存在**带 `show` 的该模态（计数为 **0**），页面回到详情页浏览态。

- **自动化可行性**：✅ 高。

---

#### TC-LOCATION-B-004：关闭后可再次打开地图

- **优先级**：P1
- **前置条件**：已完成 TC-LOCATION-B-003，模态已关闭。
- **测试步骤**：
  1. 再次点击「Show map」按钮。
  2. 验证模态重新出现且地图区域可加载。

- **预期结果**：✅ 实测（逻辑与 B-001/B-003 一致，建议在自动化中作为回归串联步骤）
  - 可再次打开全屏地图模态，行为与首次一致。

- **自动化可行性**：✅ 高。

---

### 模块 C：与主信息区的一致性

#### TC-LOCATION-C-001：主信息区地址与 Location 地址一致

- **优先级**：P1
- **前置条件**：同 TC-LOCATION-A-001。
- **测试步骤**：
  1. 读取主信息区地址元素 `MainInfo_address__TSTas` 的文本。
  2. 读取 Location 区 `LocationCard_address__SJx_4` 的文本。
  3. 比对二者。

- **预期结果**：✅ 实测
  - 两处文本均为 **`Al-Az Pest Control Company`**，完全一致。

- **自动化可行性**：✅ 高。

---

### 模块 D：键盘与无障碍（补充）

#### TC-LOCATION-D-001：地图模态打开后按 Escape 的行为

- **优先级**：P2
- **前置条件**：地图模态已打开。
- **测试步骤**：
  1. 按下键盘 **`Escape`** 一次。
  2. 观察模态是否关闭。

- **预期结果**：✅ 实测
  - 本页按下 **`Escape` 后模态仍保持打开**（`LocationCard_modalMap__PhyVC.modal.show` 仍存在）。
  - **说明**：若产品期望支持 Escape 关闭，则当前行为可记录为**缺陷 / 体验缺口**；测试脚本不应默认 Escape 可关闭。

- **自动化可行性**：✅ 中（需与产品期望对齐后固定断言）。

---

## 探测与证据说明（内部追溯）

- **页面探测**：使用 Playwright 对 `https://ae.58v5.cn` 及上述详情页进行真实访问，采集 DOM class、尺寸与交互结果；关键结构见仓库内 `web-qa-brain/location_probe_result.json` 与截图 `location_probe_detail_full.png`、`location_probe_map_modal.png`（若已生成）。
- **预期标注**：本文档中带 **✅ 实测** 的条目均来自上述探测过程；未在其它类目 / 其它帖子逐一复测的变体（例如无地址、无坐标）**未写死结论**，建议作为后续扩展场景单独立项探测。

---

## 修订记录

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-04-10 | 首版：基于 AE 58v5 预览站、手机壳类目详情页实测撰写 |
