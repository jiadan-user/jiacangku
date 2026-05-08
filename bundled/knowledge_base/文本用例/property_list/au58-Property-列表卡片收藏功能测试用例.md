# AU站 买房列表 - 列表卡片收藏功能测试用例

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

说明：需要登录，验证列表卡片收藏/取消收藏及收藏页入口。

---

## 测试用例

### TC001 未登录点击收藏图标弹出登录弹窗

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_favorite.py::test_tc001_unlogged_click_fav_opens_login_dialog`）

**步骤**：未登录状态下打开买房列表页，点击某张卡片的收藏图标（心形）。  
**预期**：弹出登录对话框（如 Welcome to OK.com），含邮箱输入框、Continue 等。  
**验证**：登录弹窗可见，或出现要求登录的提示。

---

### TC002 已登录点击收藏图标收藏成功

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_favorite.py::test_tc002_logged_click_fav_adds_favorite`）

**步骤**：已登录状态下打开买房列表页，找到未收藏的卡片，点击收藏图标（空心心形）。  
**预期**：收藏图标变为实心（已收藏），可有成功提示（如 Added to favourites）。  
**验证**：图标状态变化或 Toast 文案含“favourites/favorite/收藏”等。

---

### TC003 进入收藏页面查看已收藏的房产

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_favorite.py::test_tc003_go_to_favorites_page`）

**步骤**：已登录且已收藏至少一条后，点击页面右上角「···」菜单，选择 Favourites 进入收藏页，查找刚收藏的卡片。  
**预期**：跳转到收藏页 URL（如含 favorites），页面中能找到刚收藏的房产卡片。  
**验证**：URL 为收藏页，列表中存在该卡片。

---

### TC004 已登录取消收藏

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_favorite.py::test_tc004_logged_click_fav_removes_favorite`）

**步骤**：已登录且某条已收藏，点击该卡片的收藏图标（实心）。  
**预期**：图标变为空心（未收藏），可有提示（如 Removed from favorites）。  
**验证**：图标状态变化或 Toast 文案含“Removed/取消”等。

---

### TC005 收藏后刷新页面状态保持

**优先级**：P1
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_favorite.py::test_tc005_favorite_persists_after_reload`）

**步骤**：已登录且已收藏某条，刷新列表页，找到该卡片查看收藏图标。  
**预期**：刷新后该卡片收藏图标仍为实心（已收藏状态保持）。  
**验证**：图标仍为已收藏状态。

---

### TC006 取消收藏后到收藏页验证该帖子已移除

**优先级**：P0
**UI自动化**：✅ 可自动化（已匹配自动化脚本：`property_list/test_au58_property_list_favorite.py::test_tc006_unfavorite_then_verify_removed_from_favorites`）

**步骤**：已登录且已收藏某条（记录该卡片标题），取消收藏该卡片，进入收藏页面，查找该卡片。  
**预期**：取消收藏后，进入收藏页面，该卡片不在收藏列表中。  
**验证**：收藏页面中不存在该卡片（通过标题匹配）。

---

## 执行记录

- **脚本**：`test_cases/test_au58_property_list_favorite.py`
- **最新运行**：TC001–TC005 已实现；TC001 未登录弹窗、TC002 收藏成功、TC003 进入收藏页、TC004 取消收藏、TC005 刷新后状态保持。Toast 文案兼容 “favourites”/“favorites”。
- **最新运行**：TC001–TC006 已实现；TC001 未登录弹窗、TC002 收藏成功、TC003 进入收藏页、TC004 取消收藏、TC005 刷新后状态保持、TC006 取消收藏后收藏页验证移除。Toast 文案兼容 "favourites"/"favorites"。
- **TC006 执行**：2026-03-05 通过，收藏第一张卡片 → 记录标题 → 取消收藏 → 进入收藏页 → 验证该卡片不在收藏列表中。POM 新增方法：`get_first_card_title_in_favorites()`、`is_card_in_favorites_by_title()`。
