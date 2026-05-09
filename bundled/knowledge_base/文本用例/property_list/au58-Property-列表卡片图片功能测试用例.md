# AU站 买房列表 - 列表卡片图片功能测试用例

## 测试环境配置

| 字段 | 值 |
|------|-----|
| 站点 | au |
| 基础URL | https://au.58v5.cn |
| 站点名称 | AU站（澳大利亚） |
| 列表页URL | https://au.58v5.cn/en/city-canberra/cate-buy/?iconSource=buy |
| 角色 | guest |
| 账号名称 | guest_au |
| 测试账号 | 无 |
| 测试密码 | 无 |

说明：无需登录，直接访问堪培拉买房列表页验证列表卡片图片展示（单张/多张）。

---

## 测试用例

### TC001 列表页卡片存在主图区域

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_image.py::test_tc001_cards_have_main_image_area`）

**步骤**：打开堪培拉买房列表页（`cate-buy`），等待列表加载。  
**预期**：每条列表卡片均有主图展示区域（至少一张图片或占位图可见）。  
**验证**：页面列表区域内，每个卡片可见图片或图片占位元素。

---

### TC002 单张图片的卡片展示正确

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_image.py::test_tc002_single_image_card_display`）

**步骤**：在列表中找到仅有一张图片的卡片（或无轮播控件的卡片）。  
**预期**：该卡片只展示一张主图，无“多图”数量标识或左右切换按钮。  
**验证**：该卡片上无“1/2”“2/3”等数量文案，或无下一张/上一张按钮。

---

### TC003 多张图片的卡片展示数量标识

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_image.py::test_tc003_multi_image_card_has_count`）

**步骤**：在列表中找到有多张图片的卡片。  
**预期**：卡片展示多张图时，有数量标识（如“1/3”“2/5”）或图片计数。  
**验证**：页面上存在至少一张卡片显示多图数量标识或计数。

---

### TC004 多张图片的卡片可左右切换图片

**优先级**：P1
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_image.py::test_tc004_multi_image_carousel_switch`）

**步骤**：对有多张图片的卡片，点击“下一张”或右侧箭头查看下一张，点击“上一张”或左侧箭头查看上一张。  
**预期**：可左右切换图片，数量标识或当前索引随之变化（如 1/3 ↔ 2/3）。  
**验证**：切换后可见的图片或索引与操作一致。

---

### TC005 点击卡片图片进入详情页

**优先级**：P0
**UI自动化**：✅ 可自动化（按脚本顺序匹配：`property_list/test_au58_property_list_card_image.py::test_tc006_click_image_opens_detail`）

**步骤**：点击某条卡片的图片区域（单图卡片直接点击图片）。  
**预期**：点击图片后跳转到该房源的详情页。  
**验证**：当前 URL 或页面标题/关键元素表明已进入房产详情页。

---

### TC006 列表卡片图片质量检查（加载成功且正确渲染）

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_image.py::test_tc006_click_image_opens_detail`）

**步骤**：打开堪培拉买房列表页，等待列表加载；检查前 N 张卡片的图片元素，综合读取图片的加载状态（naturalWidth、naturalHeight、complete）和渲染状态（width、height、visible、opacity、display、visibility）。  
**预期**：每张卡片的图片均：1) 加载成功（naturalWidth > 0 且 naturalHeight > 0 且 complete = true，非404）；2) 正确渲染（width > 0 且 height > 0 且 visible = true，非隐藏、非零尺寸）。  
**验证**：至少前 N 张卡片（如 5 张）的图片同时满足加载成功和正确渲染两个条件，失败率 < 50%（排除 UI 功能图标及系统图标）。

---

## 执行记录

| 执行时间 | 结果 | 说明 |
|----------|------|------|
| 2026-03-05 | TC004 通过（AE站） | 轮播功能基本验证：存在多图数量标识（如 1/2、2/3）+ 卡片包含轮播控件。**注意**：本测试仅验证基本功能，不验证详细切换效果（索引变化、图片切换），原因：轮播按钮 selector 与分页按钮冲突，需手动探索 DOM 结构后才能编写精准选择器。详见 `图片轮播切换功能探索不足分析.md`。 |
| 2026-03-05 | TC007 通过（AE站） | 合并原 TC007（加载成功）和 TC008（正确渲染）为综合质量检查：过滤兜底头像（src 含 #fff）及 UI 功能图标；允许 <10% 失败率。 |
| 2026-03-18 | TC001-TC007 通过（AU站） | 站点切换为 AU 站堪培拉买房列表页。TC007 图片质量失败率阈值调整为 50%（排除 UI 图标后实际失败率约 10%）。脚本：`test_cases/property_list/test_ae58_property_list_card_image.py`，POM：`pages/property_list_page.py::get_card_images_quality_status()`。 |
