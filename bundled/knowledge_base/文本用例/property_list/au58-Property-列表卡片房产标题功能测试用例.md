# AU站 买房列表 - 列表卡片房产标题功能测试用例

## 测试环境配置

| 字段 | 值 |
|------|-----|
| 站点 | au |
| 基础URL | https://au.58v5.cn |
| 站点名称 | AU站（澳大利亚） |
| 角色 | buyer |
| 账号名称 | dc_buyer_au |
| 测试账号 | liuyue62@58.com |
| 测试密码 | Xindemima1% |

说明：需要登录，验证列表卡片上的房产标题展示与点击行为。

**名词定义**：列表卡片上的「房产标题」取的是详情页中 **Property Introduction** 模块的**副标题**（与详情页该模块副标题一致）。

---

## 测试用例

### TC001 列表页卡片展示房产标题

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_title.py::test_tc001_list_cards_show_title`）

**步骤**：已打开买房列表页，查看列表卡片内容。  
**预期**：每条列表卡片均展示房产标题（标题文案可见）。  
**验证**：每张卡片存在非空标题区域或标题文案。

---

### TC002 房产标题非空且可读

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_title.py::test_tc002_title_non_empty_and_readable`）

**步骤**：任选若干列表卡片，读取其标题文案。  
**预期**：标题非空、非纯空格，且为可读文本。  
**验证**：至少前 N 张卡片的标题 strip 后长度 > 0。

---

### TC003 点击房产标题进入详情页

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_title.py::test_tc003_click_title_opens_detail`）

**步骤**：点击某条卡片的房产标题区域。  
**预期**：跳转到该房源的详情页（当前页或新标签）。  
**验证**：URL 为该房源详情页地址，或页面内容为详情页。

---

### TC004 标题与卡片内其他信息一致

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_title.py::test_tc004_title_matches_card_info`）

**步骤**：对同一张卡片，对比标题与卡片内地址/价格等是否同属该房源。  
**预期**：标题与该卡片其他信息对应同一套房源。  
**验证**：点击标题进入的详情页与点击该卡片其他区域进入的详情一致（或 URL 一致）。

---

### TC005 标题长度与格式合理

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_title.py::test_tc005_title_length_and_format`）

**步骤**：检查列表内多条卡片的标题长度与展示样式。  
**预期**：标题长度在合理范围内，无截断异常或乱码。  
**验证**：标题字符数在约定范围内（如 1～200），或无明显乱码/截断异常。

---

### TC006 列表卡片房产标题与详情页 Property Introduction 副标题一致

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_title.py::test_tc006_list_title_matches_detail_subtitle`）

**步骤**：在列表页取第一张卡片的房产标题；点击该卡片进入详情页，在详情页找到 Property Introduction 模块并读取其副标题。  
**预期**：列表卡片上的房产标题与详情页 Property Introduction 模块的副标题一致（同一套房源）。  
**验证**：两者文案一致（或副标题包含列表标题 / 去除首尾空格后一致）。

---

## 执行记录

| 执行时间 | 结果 | 说明 |
|----------|------|------|
| 2026-03-04 | 5/5 通过 | 脚本：`test_cases/test_au58_property_list_card_title.py`，Session 复用登录，点击标题在新标签页打开详情。 |
| 2026-03-04 | TC006 已添加 | 新增用例：列表卡片房产标题与详情页 Property Introduction 副标题一致；依赖详情页存在「Property Introduction」区块，PO：`pages/property_detail_page.py`。 |
