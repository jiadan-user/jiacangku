# AU站 买房列表 - 列表卡片头像和名称功能测试用例

## 测试环境配置

| 字段 | 值 |
|------|-----|
| 站点 | au |
| 基础URL | https://au.58v5.cn |
| 站点名称 | AU站（澳大利亚） |
| 角色 | guest |
| 账号名称 | guest_au |
| 测试账号 | 无 |
| 测试密码 | 无 |

说明：无需登录，直接访问买房列表页验证列表卡片上的头像和名称展示。

---

## 测试用例

### TC001 列表页卡片展示头像区域

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_avatar_name.py::test_tc001_list_cards_have_avatar_area`）

**步骤**：打开买房列表页（Canberra 等），等待列表加载。  
**预期**：每条列表卡片上均有头像展示区域（经纪人/发布者头像或占位图）。  
**验证**：列表区域内每张卡片可见头像元素（img 或带背景的占位区域）。

---

### TC002 列表页卡片展示名称

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_avatar_name.py::test_tc002_list_cards_show_name`）

**步骤**：在同一列表页查看卡片内容。  
**预期**：每条列表卡片上均展示名称（经纪人姓名或发布者名称等）。  
**验证**：每张卡片上存在可见的名称文案，且非空。

---

### TC003 头像与名称同卡关联展示

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_avatar_name.py::test_tc003_avatar_and_name_in_same_card`）

**步骤**：任选一条列表卡片，观察头像与名称的位置关系。  
**预期**：头像与名称在同一卡片内、关联展示（如同一行或相邻区域）。  
**验证**：单张卡片内同时存在头像元素和名称文案，且布局合理。

---

### TC004 无头像时显示兜底头像

**优先级**：P1
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_avatar_name.py::test_tc004_default_avatar_display`）

**步骤**：在列表中找到无自定义头像的卡片（或通过数据/多页查找）。  
**预期**：无头像时展示兜底头像（如默认灰色/白色小人图标）。  
**验证**：该卡片仍显示头像区域（占位图或默认图标），不出现空白或裂图。

---

### TC005 头像或名称可点击，点击后进入卡片详情页

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_card_avatar_name.py::test_tc005_click_avatar_opens_detail`）

**步骤**：点击某条卡片的头像或名称区域。  
**预期**：点击后进入该卡片的详情页（房产详情页）。  
**验证**：当前页或新标签页 URL 为该房源的详情页地址。
