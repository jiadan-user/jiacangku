# AE站 - 二手想卖同款功能测试用例

本文档与 `test_ae_marketplace_sell_similar_v2.py` 实现一一对应；用例编号 **TC001～TC010**（脚本中无 TC006）。

## 脚本与用例映射

| 用例 ID | pytest 函数 | 标记 |
|---------|-------------|------|
| TC001 | `test_tc001_non_own_post_shows_sell_similar_button` | smoke, p0 |
| TC002 | `test_tc002_click_sell_similar_navigates_to_publish_page` | smoke, p1 |
| TC003 | `test_tc003_own_post_does_not_show_sell_similar_button` | smoke, p0 |
| TC004 | `test_tc004_publish_page_preloads_original_post_data` | smoke, p1 |
| TC005 | `test_tc005_not_logged_in_user_shows_login_popup` | smoke, p1 |
| TC007 | `test_tc007_non_marketplace_posts_do_not_show_sell_similar` | p1 |
| TC008 | `test_tc008_sell_similar_button_in_spanish_language` | p2 |
| TC009 | `test_tc009_publish_page_inherits_product_attributes` | p2 |
| TC010 | `test_tc010_publish_page_inherits_description` | p2 |

---

## 测试环境配置

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | ae | 阿联酋站 |
| 基础URL | https://ae.58v5.cn | 测试站点地址 |
| 站点名称 | 阿联酋站 | 用于日志展示 |
| 角色 | buyer | 买家 |
| 账号名称 | ae_buyer_sell_similar | 用于 session 命名 |
| 测试账号 | wangyongli@58.com | 登录邮箱 |
| 测试密码 | Qwer1234 | 登录密码 |
| locale | en-AE | 脚本 `_CONFIG` |
| 货币 | AED | 价格展示校验 |

---

## 公共实现说明

### 查找「有 Sell Similar 的非本人帖」：`find_post_with_sell_similar_button`

- 访问列表：`{base_url}/{language}/city-abu-dhabi/cate-marketplace/`（默认 `language=en`，TC008 使用 `es`）。
- 从列表收集候选详情链接（含 AED 价格锚点向上找 `a[href]`，或备用规则过滤 `cate-marketplace`、`?`、非 `/` 结尾、商品 ID 等）。
- 逐个打开详情：需 **Contact 可见** 且 **无 Withdraw/Edit**，且 **Sell Similar 可见**，否则跳过该条。
- 返回 `(detail_url, original_price, original_title)`；找不到则对应用例 **pytest.skip**（如：未找到有按钮的商品）。

### 本人帖列表（TC003）

- 使用：`/en/city-abu-dhabi/cate-marketplace/?iconSource=marketplace` 提高命中本人帖概率。
- 遍历商品详情直至出现 **Withdraw 或 Edit**。

---

## TC001: 非本人帖详情页展示 Sell Similar 按钮

**测试目标**: 在非本人发布的二手帖子详情页，正确展示「Sell Similar」，且不展示本人帖操作按钮。

**前置条件**:
- 用户已登录（`ensure_ae_logged_in`）
- 通过 `find_post_with_sell_similar_button` 找到带 Sell Similar 的非本人帖（找不到则 skip）

**测试步骤**:
1. 调用 helper 定位并进入目标详情页
2. 校验详情页 URL：包含 `/cate-`，且不包含 `cate-marketplace`（非列表页）
3. 校验展示价格文案（`get_price_text`，含 AED 等业务展示）
4. 校验不展示 Withdraw、Edit
5. 校验展示 Contact
6. 校验展示 Sell Similar（`is_sell_similar_button_visible`）

**预期结果**:
- URL 符合详情页特征
- 有价格信息
- 非本人帖：无 Withdraw/Edit，有 Contact，有 Sell Similar

**优先级**: P0

**测试类型**: 正向场景

---

## TC002: 点击 Sell Similar 跳转发布页

**测试目标**: 点击 Sell Similar 后进入发布流程页面。

**前置条件**:
- 用户已登录
- helper 找到带 Sell Similar 的非本人帖（找不到则 skip）

**测试步骤**:
1. 确认 Sell Similar 可见
2. `click_sell_similar_button`
3. 等待 `domcontentloaded` 与短等待
4. 断言 `is_publish_page_loaded`
5. 断言 URL 含 `/publish/` 或 `/biz/en/publish/`（不区分大小写），**或** 页面标题含 `post`（不区分大小写）

**预期结果**:
- 发布页加载成功
- URL 或标题满足上述任一组合

**优先级**: P1

**测试类型**: 正向场景

---

## TC003: 本人帖详情页不展示 Sell Similar 按钮

**测试目标**: 本人发布的二手帖详情页不展示 Sell Similar，展示本人操作入口。

**前置条件**:
- 用户已登录
- 在 `?iconSource=marketplace` 列表中遍历详情，找到含 Withdraw 或 Edit 的本人帖（找不到则 skip：建议先发布测试商品）

**测试步骤**:
1. 确认本人帖：展示 Withdraw **或** Edit
2. 确认不展示 Contact
3. 确认不展示 Sell Similar

**预期结果**:
- 本人帖特征与脚本断言一致

**优先级**: P0

**测试类型**: 正向场景

---

## TC004: 发布页预加载原帖数据（价格/标题/图片数量）

**测试目标**: 进入发布页后 URL 正确；在条件允许时校验价格、标题预填；记录图片数量（脚本对「图片清空」为日志级，强断言可能随页面调整）。

**前置条件**:
- 用户已登录
- helper 找到目标帖（找不到则 skip）

**测试步骤**:
1. 记录 `original_price`、`original_title`
2. 点击 Sell Similar，等待发布页 `is_publish_page_loaded`
3. 断言当前 URL 包含 `/publish/`
4. 若原帖价格存在且非 `AED 0`：尝试 `get_publish_page_price` 并打日志
5. `get_publish_page_images_count` 记录张数
6. 若有 `original_title`：尝试 `get_publish_page_title` 并打日志

**预期结果**:
- 发布页 URL 含 `/publish/`
- 价格/标题以脚本日志与分支为准（部分为弱校验/告警日志）

**优先级**: P1

**测试类型**: 正向场景 / 数据继承

---

## TC005: 未登录点击 Sell Similar 调起登录

**测试目标**: 未登录用户点击 Sell Similar 应出现登录能力（弹窗/对话框/登录页），不应直接进入发布页。

**前置条件**:
- 清除 Cookies、`localStorage`、`sessionStorage`
- 未登录打开列表，页面可见 Log in / Register 等未登录标识

**测试步骤**:
1. 访问 `/en/city-abu-dhabi/cate-marketplace/`
2. 断言存在未登录标识（多种文案/选择器轮询）
3. `get_first_detail_listing_link_href` 进入首个详情
4. 若无 Sell Similar 则 skip
5. 点击 Sell Similar
6. 断言：`Email or phone number` 输入框可见 **或** `[role='dialog']` 可见 **或** URL 含 `login`
7. 断言：不应处于「无登录拦截的直接发布页」逻辑（脚本：`/publish/` 与 `login` 的组合断言）

**预期结果**:
- 出现登录相关 UI 或跳转登录
- 不直接完成发布页发布流程（与脚本断言一致）

**优先级**: P1

**测试类型**: 会话 / 安全入口

---

## TC007: 非 Marketplace 分类帖不展示 Sell Similar

**测试目标**: Jobs、Services 等非二手分类详情页不展示 Sell Similar。

**前置条件**:
- 用户已登录

**测试步骤**:
1. **Jobs**：访问 `/en/city-abu-dhabi/cate-jobs/`，解析首个合适详情链接并进入
2. **Services**：访问 `/en/city-abu-dhabi/cate-services/`，同上
3. 每类详情页断言 `is_sell_similar_button_visible` 为 false（找不到链接时该类 skip 日志后继续下一类）

**预期结果**:
- 上述分类详情页不出现 Sell Similar

**优先级**: P1

**测试类型**: 负向 / 范围限定

---

## TC008: 西班牙语环境 Sell Similar 展示

**测试目标**: 使用 `language='es'` 的列表路径查找商品后，详情页仍应能识别 Sell Similar（英文或西语文案）。

**前置条件**:
- 用户已登录
- ES 列表页能找到带按钮的商品（找不到则 skip）

**测试步骤**:
1. `find_post_with_sell_similar_button(..., language='es')`
2. 断言：`is_sell_similar_button_visible` **或** 页面存在匹配 `Vender.*similar` 的文案

**预期结果**:
- 至少一种语言形态的按钮可见（脚本允许后端语言重定向）

**优先级**: P2

**测试类型**: 国际化

---

## TC009: 发布页继承商品属性

**测试目标**: 进入发布页后 URL 正确；尝试发现 brand/model/condition 等属性控件并打日志；校验标题、价格预填（与 TC004 部分重叠，更侧重属性区域）。

**前置条件**:
- 用户已登录
- helper 找到目标帖（找不到则 skip）

**测试步骤**:
1. 详情页尝试解析属性键值（`[class*='attribute']` 等，含冒号文本）
2. 点击 Sell Similar，等待发布页加载，URL 含 `/publish/`
3. 在发布页查找 `brand`、`model`、`condition`、`color`、`size` 等相关 input/select
4. `get_publish_page_title` / `get_publish_page_price` 日志校验

**预期结果**:
- 发布页 URL 正确；属性字段存在性以日志为主（脚本对未命名字段仅告警）

**优先级**: P2

**测试类型**: 数据继承

---

## TC010: 发布页继承商品描述

**测试目标**: 进入发布页后校验描述区域预填；可与原帖描述做简单词交集统计（共同词 > 3 记为相似度较高）。

**前置条件**:
- 用户已登录
- helper 找到目标帖（找不到则 skip）

**测试步骤**:
1. 详情页用多选择器尝试抓取较长文本作为 `original_description`（≥20 字符）
2. 点击 Sell Similar，发布页 URL 含 `/publish/`
3. `get_publish_page_description`；若有原帖描述则比较词集合交集数量
4. 日志校验标题、价格预填

**预期结果**:
- URL 正确；描述/相似度以脚本日志与分支为准

**优先级**: P2

**测试类型**: 数据继承

---

## 测试数据说明

**判断是否为本人帖（与脚本一致）**:
- 本人帖：详情页有 Withdraw **或** Edit，且无 Contact（TC003 以 Withdraw/Edit 命中为准）
- 非本人帖（helper）：有 Contact，且无 Withdraw、无 Edit

**参考代码（摘自脚本逻辑）**:
```python
# 非本人且可点 Sell Similar：有 Contact，无 Withdraw/Edit
has_contact = detail_page.is_contact_button_visible(timeout=3000)
has_withdraw = detail_page.is_withdraw_button_visible(timeout=2000)
has_edit = detail_page.is_edit_button_visible(timeout=2000)
if not has_contact or has_withdraw or has_edit:
    continue  # 跳过
```

---

## 注意事项

1. **动态等待**: 列表与详情异步渲染，脚本多处 `wait_for_timeout` 与显式等待并用。
2. **选择器**: 以 Page Object（`MarketplaceListPageAe`、`MarketplaceDetailPageAe`、`MarketplaceSellSimilarPageAe`）为准。
3. **Skip 条件**: 无可用商品、无本人帖、无 Sell Similar、ES 列表无命中等会 skip，属数据依赖而非用例失败。
4. **TC006**: 当前脚本未实现该编号，文档不占用 TC006。
5. **弱断言**: TC004/009/010 中部分为日志与分支，升级强断言时需同步改 Page Object 与选择器稳定性。
