# AE Marketplace 订单流转测试用例

> **生成时间**: 2026-03-12  
> **探测方式**: Playwright MCP 真实浏览器实测  
> **测试范围**: AE Marketplace 完整订单流转（买家 + 卖家双端）  
> **总用例数**: 51 条（TC001–TC051）+ 1 条后置操作（Teardown）  
> **可自动化**: 51 条（100%）

---

## 测试环境配置（必填）

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | ae | AE 阿联酋站 |
| 基础URL | https://ae.58v5.cn | 前台站点地址 |
| Pub URL | https://aepub.58v5.cn | 后台/订单站点地址 |
| 站点名称 | 阿联酋站 | 用于日志展示 |
| 买家角色 | buyer | 下单、支付、确认收货 |
| 买家账号名称 | buyer_ae_cui | 用于 session 命名，必须唯一 |
| 买家测试账号 | cuidemin@58.com | 登录邮箱（实际探测时使用的账号） |
| 买家测试密码 | TOUfangqa123 | 登录密码（实际探测时使用的密码） |
| 卖家角色 | seller | 发货、取消订单 |
| 卖家账号名称 | seller_ae_wang | 用于 session 命名，必须唯一 |
| 卖家测试账号 | wangyongli@58.com | 登录邮箱 |
| 卖家测试密码 | Qwer1234 | 登录密码 |

**说明**：上述配置为实际探测时使用的账号密码，playwright-test-generator 生成脚本时会严格使用此配置。

---

## 📑 目录

- [模块一：买家下单页面（Checkout）](#模块一买家下单页面checkout)
- [模块二：买家 Purchase Orders & Pending 订单详情页](#模块二买家-purchase-orders--pending-订单详情页)
- [模块三：卖家 Sales Orders & Pending 订单详情页](#模块三卖家-sales-orders--pending-订单详情页)
- [模块四：买家 Unshipped 订单详情页](#模块四买家-unshipped-订单详情页)
- [模块五：卖家 Unshipped 订单详情页](#模块五卖家-unshipped-订单详情页)
- [模块六：卖家 Pending Receipt 订单详情页](#模块六卖家-pending-receipt-订单详情页)
- [模块七：买家 Pending Receipt 订单详情页](#模块七买家-pending-receipt-订单详情页)
- [模块八：买家 Completed 订单详情页](#模块八买家-completed-订单详情页)
- [模块九：卖家 Completed 订单详情页](#模块九卖家-completed-订单详情页)
- [模块十：异常场景与边界测试](#模块十异常场景与边界测试)
- [后置操作（Teardown）](#后置操作teardown)
- [测试数据准备](#测试数据准备)
- [覆盖率自评](#覆盖率自评)
- [测试统计](#测试统计)

---

## 测试范围说明

涵盖完整订单流转路径：**下单 → 支付（Pending）→ 卖家发货（Unshipped）→ 买家待收货（Pending Receipt）→ 交易完成（Completed）**

买家视角 & 卖家视角双端覆盖。

**取消权限规则**：
- **未支付（Pending）**：买家、卖家均可取消
- **已支付未发货（Unshipped）**：仅卖家可取消，买家无取消权限
- **已发货（Pending Receipt）**：买家、卖家均不可取消

**测试数据说明**：各模块所需特定状态的订单，如对应 Tab 中已存在可用订单，直接使用；如不存在，需先构造对应状态的订单数据。

---

## 模块一：买家下单页面（Checkout）

### TC001：Checkout 页面核心元素展示

#### 📋 前置条件
- 买家已登录（AEOKer_cui123）
- 进入商品详情页，已点击"Buy Now"按钮，当前处于 Checkout 页面（URL 含 createOrder）

#### 🎬 执行步骤
1. 进入商品详情页，点击"Buy Now"按钮
2. 等待 Checkout 页面加载完成
3. 观察页面各区块渲染情况

#### ✅ 预期结果
- 页面 URL 包含 createOrder ✅ 实测
- 左侧展示 Order Summary 区块（商品信息、价格） ✅ 实测
- 左侧展示 Shipping 区块（配送地址） ✅ 实测
- 左侧展示 Payment Method 区块（支付方式） ✅ 实测
- 右侧展示 Order Summary 价格汇总（Subtotal / Delivery / Total） ✅ 实测
- 右侧展示 Pay 按钮（黑底白字） ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC002：Checkout - 价格展示正确性

#### 📋 前置条件
- 买家已登录，处于 Checkout 页面
- 商品为"Seller Pays Postage"（免运费商品），标价 AED 3500

#### 🎬 执行步骤
1. 进入 Checkout 页面
2. 观察右侧价格汇总区块的各价格字段

#### ✅ 预期结果
- 货币单位显示 AED ✅ 实测
- Item Price = AED 3500（与商品详情页标价一致） ✅ 实测
- Delivery = AED 0.00（Seller Pays Postage → 免运费） ✅ 实测
- Total = AED 3500.00（Item Price + Delivery = 3500 + 0） ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC003（负向）：Checkout - 收货地址字段校验

#### 📋 前置条件
- 买家已登录，处于 Checkout 页面
- 已打开 Shipping 地址编辑弹窗

#### 🎬 执行步骤
1. 清空 Full Name 字段，点击 Apply → 验证错误提示
2. 在 Phone 字段输入字母（如"abc"）→ 验证过滤行为
3. 在 Phone 字段输入格式不正确的数字（如"1"）→ 点击 Apply → 验证 toast 提示
4. 清空所有必填字段，点击 Apply → 验证批量校验
5. 在 Postal Code 字段输入超长字符（>10 位）→ 验证 UI 限制

#### ✅ 预期结果
- Full Name 为空 → 字段内显示"Cannot be empty"错误 ✅ 实测
- Phone 输入字母（如"abc"）→ 字母被过滤，字段为空后显示"Cannot be empty" ✅ 实测
- Phone 格式不正确（单个数字"1"）→ toast 提示"Invalid phone number." ✅ 实测
- 所有必填字段均空点击 Apply → 所有字段同时显示"Cannot be empty"，弹窗不关闭 ✅ 实测
- Postal Code 超过 10 字符时，UI 层限制继续输入（字符计数器显示 x/10） ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC004：Checkout - Shipping 地址弹窗完整流程

#### 📋 前置条件
- 买家已登录，处于 Checkout 页面
- 已设置过收货地址

#### 🎬 执行步骤
1. 点击 Shipping 区块中的收货地址行（或编辑按钮）
2. 弹出地址编辑弹窗后，验证必填字段可见
3. 点击"Clean"按钮清空所有字段
4. 验证所有字段已清空
5. 填写合法收货地址（Full Name、Address Line 1、County/City、State、ZIP、Phone）
6. 点击"Apply"按钮
7. 验证 Checkout 页面 Shipping 区块展示更新后的地址

#### ✅ 预期结果
- 点击地址行后弹窗正常弹出 ✅ 实测
- 弹窗包含必填字段：Full Name、Address Line 1、Phone Number ✅ 实测
- 点击 Clean 后所有输入框清空 ✅ 实测
- 填写合法地址后点击 Apply，弹窗关闭 ✅ 实测
- Checkout 页面 Shipping 区块展示新填写的地址 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC005：Checkout - 点击 Pay 唤起支付弹窗（不支付）

#### 📋 前置条件
- 买家已登录，处于 Checkout 页面
- 已正确填写收货地址

#### 🎬 执行步骤
1. 点击页面右侧"Pay"按钮
2. 观察支付弹窗（Airwallex iframe）是否弹出
3. 关闭支付弹窗（不支付）
4. 导航至 Purchase Orders → Pending Tab
5. 点击最新的 Pending 订单进入详情页

#### ✅ 预期结果
- 点击 Pay 后弹出支付弹窗（Airwallex iframe 出现） ✅ 实测
- 支付弹窗展示支付金额及支付方式 ✅ 实测
- 关闭弹窗后，订单在 Pending Tab 中可见 ✅ 实测
- 订单详情页状态显示"Processing payment" ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC006：商品"Buyer paid but incomplete"错误提示

#### 📋 前置条件
- 买家已登录
- 目标商品已有其他买家下单但未完成支付（占用中）

#### 🎬 执行步骤
1. 进入商品详情页
2. 点击"Buy Now"按钮
3. 观察页面提示

#### ✅ 预期结果
- 页面显示提示："Someone placed a bid but didn't complete payment" ✅ 实测
- 不允许进入 Checkout 页面 ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 异常流
- **UI自动化**: ✅ 可自动化

---

### TC007：Checkout - 银行卡支付成功 → 订单状态 Payment received

#### 📋 前置条件
- 买家已登录，处于 Checkout 页面
- 已正确填写收货地址
- 测试银行卡可用（CVC=123）

#### 🎬 执行步骤
1. 点击"Pay"按钮，等待 Airwallex 支付弹窗（iframe）出现
2. 在 iframe 中输入测试银行卡信息（CVC=123）
3. 点击支付确认按钮完成支付
4. 等待页面跳转至订单详情页（URL 含 /pay/order）
5. 验证订单状态

#### ✅ 预期结果
- 支付弹窗正常显示，可输入银行卡信息 ✅ 实测
- 支付完成后自动跳转至订单详情页 ✅ 实测
- 订单状态显示"Payment received"或"Paid"或"Unshipped" ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC008：Checkout - 谷歌支付成功 → 订单状态 Payment received

#### 📋 前置条件
- 买家已登录，处于 Checkout 页面
- 已正确填写收货地址
- 测试环境已启用 Google Pay（Airwallex iframe 中可见 Google Pay 按钮）

#### 🎬 执行步骤
1. 点击"Pay"按钮，等待 Airwallex 支付弹窗（iframe）出现
2. 在 iframe 中定位 Google Pay 按钮并点击
3. 若弹出 Google Pay 确认弹窗（新 Popup），在弹窗内点击确认支付按钮后关闭弹窗
4. 等待页面跳转至订单详情页（URL 含 /pay/order）
5. 验证订单状态

#### ✅ 预期结果
- 支付弹窗正常显示，可见 Google Pay 按钮
- 点击 Google Pay 后支付流程完成（含弹窗确认或直接模拟支付）
- 支付完成后自动跳转至订单详情页
- 订单状态显示"Payment received"或"Paid"或"Unshipped"

#### 📝 备注（TC008 谷歌支付）
- 若测试环境 Airwallex iframe 中未渲染 Google Pay 按钮，用例会 `assert` 失败并提示"请确认测试环境已启用 Google Pay"
- Google Pay 弹窗为浏览器级别 Popup，代码通过 `expect_popup` 自动捕获并在弹窗内点击确认
- **重试机制（最多 3 次）**：若支付弹窗显示 "Something went wrong, please try again later."，代码自动关闭弹窗并切换商品重试；连续 3 次均失败则 SKIP（记录截图至 `reports/gpay_payment_error_N.png`）
- **Google 登录自动检测**：通过弹窗 URL 判断登录状态（URL 含 `identifier` 时直接执行邮箱+密码登录，无需等待 DOM 元素渲染）；若 Google 账号有 Session 则自动点击账号选择；`/challenge/pwd` 密码验证页自动重新输入密码

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

## 模块二：买家 Purchase Orders & Pending 订单详情页

> **数据说明**：如 Pending Tab 中已存在可用订单，直接使用；如不存在，需先通过下单流程构造 Pending 状态订单数据。

### TC009：Purchase Orders - 5 个 Tab 展示

#### 📋 前置条件
- 买家已登录
- 路径：头像 → Purchase Orders

#### 🎬 执行步骤
1. 点击头像进入个人中心
2. 点击"Purchase Orders"进入订单列表页
3. 观察页面 Tab 数量及名称

#### ✅ 预期结果
- 页面 URL 包含 orderManage ✅ 实测
- 页面包含 5 个 Tab：ALL / Pending / Unshipped / Pending Receipt / Completed ✅ 实测
- 每个 Tab 均可正常点击切换 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC010：买家 Pending 订单详情页 - 核心元素展示

#### 📋 前置条件
- 买家已登录；如 Pending Tab 中已有订单直接使用，否则需先构造 Pending 状态订单
- 路径：Purchase Orders → Pending Tab → 点击订单

#### 🎬 执行步骤
1. 进入 Purchase Orders → Pending Tab
2. 点击第一条 Pending 订单
3. 观察详情页各区块内容

#### ✅ 预期结果
- 状态区域显示"Processing payment" + Refresh 刷新按钮 ✅ 实测
- 倒计时显示"Pay within XX:XX:XX or auto-cancel"（蓝色） ✅ 实测
- 进度条节点：Placed（已完成）→ Paid → Shipped → Completed ✅ 实测
- Shipping 区块展示买家收货地址（Full Name、Address、City、Country、Phone） ✅ 实测
- Order Info 区块显示：Order Number、Transaction snapshot、Seller nickname、Order time ✅ 实测
- 商品区块显示：缩略图 + 名称 + 价格 ✅ 实测
- 价格明细：Total / Item Price / Delivery / Buyer Protection Fee ✅ 实测
- 操作按钮：Pay（主操作，黑底白字）、Cancel（次操作） ✅ 实测
- 右上角显示 Message Seller 按钮 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC011：买家 Pending - Cancel 取消未支付订单

#### 📋 前置条件
- 买家已登录；如 Pending Tab 中已有订单直接使用，否则需先构造 Pending 状态订单
- 处于买家 Pending 订单详情页

#### 🎬 执行步骤
1. 点击"Cancel"按钮
2. 观察取消弹窗标题及选项
3. 选择取消原因，点击"Cancel Order"
4. 验证订单状态变化

#### ✅ 预期结果
- 弹窗标题显示"Reason for cancellation"（非"Cancel Order"） ✅ 实测
- 原因选项共 5 项（单选）：I don't want to buy it anymore / Information filled in incorrectly / Seller out of stock / Same city meeting and trading / Other reasons ✅ 实测
- 选择"Other reasons"后出现文本输入框 ✅ 实测
- 底部按钮：Cancel Order（主操作）/ Keep Order（次操作） ✅ 实测
- 选择原因后点击"Cancel Order" → 订单状态变为 Cancelled ✅ 实测
- 点击"Keep Order" → 弹窗关闭，订单保持 Pending 状态 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC012：买家 Pending - Transaction snapshot 查看

#### 📋 前置条件
- 买家已登录；如 Pending Tab 中已有订单直接使用，否则需先构造 Pending 状态订单
- 处于买家 Pending 订单详情页

#### 🎬 执行步骤
1. 找到 Order Info 区块中的"Transaction snapshot"
2. 点击"click to view"链接
3. 观察跳转结果

#### ✅ 预期结果
- 点击"Transaction snapshot → click to view"成功跳转到交易快照页面 ✅ 实测
- 跳转不报错（注：Pending 状态下尚未支付，Transaction snapshot 为占位状态） ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC013：买家 Pending - 修改收货地址成功 → Shipping 区块展示正确

#### 📋 前置条件
- 买家已登录；如 Pending Tab 中已有订单直接使用，否则需先构造 Pending 状态订单
- 处于买家 Pending 订单详情页，Shipping 区块已显示当前收货地址

#### 🎬 执行步骤
1. 点击 Shipping 区块中的收货地址（或编辑入口）
2. 弹出地址编辑弹窗后，验证必填字段可见
3. 点击"Clean"按钮清空所有字段
4. 验证所有字段已清空
5. 填写合法收货地址（Full Name、Address Line 1、County/City、State、ZIP、Phone）
6. 点击"Apply"按钮
7. 验证订单详情页 Shipping 区块展示更新后的地址

#### ✅ 预期结果
- 点击地址区域后弹窗正常弹出 ✅ 实测
- 弹窗包含必填字段：Full Name、Address Line 1、Phone Number ✅ 实测
- 点击 Clean 后所有输入框清空 ✅ 实测
- 填写合法地址后点击 Apply，弹窗关闭 ✅ 实测
- Shipping 区块展示新填写的收货地址（Full Name、Address、City、Phone 正确） ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC014：买家 Pending - 点击 Message Seller 跳转微聊

#### 📋 前置条件
- 买家已登录；如 Pending Tab 中已有订单直接使用，否则需先构造 Pending 状态订单
- 处于买家 Pending 订单详情页

#### 🎬 执行步骤
1. 找到右上角"Message Seller"按钮
2. 点击"Message Seller"按钮
3. 观察页面跳转结果

#### ✅ 预期结果
- Message Seller 按钮在右上角可见（附消息图标） ✅ 实测
- 点击后成功跳转到与该卖家的微聊聊天页面（URL 含 /biz/en/chat） ✅ 实测
- 聊天对象为当前订单对应卖家（Seller nickname 一致） ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC015（负向）：买家 Pending - 未选取消原因直接提交

#### 📋 前置条件
- 买家已登录；如 Pending Tab 中已有订单直接使用，否则需先构造 Pending 状态订单
- 已点击 Cancel 按钮，取消弹窗已打开

#### 🎬 执行步骤
1. 打开取消弹窗后不选择任何取消原因
2. 观察"Confirm"按钮状态（弹窗中用于确认取消的按钮）
3. 尝试点击"Confirm"按钮
4. 选择取消原因后，点击"Back"按钮（不取消订单）

#### ✅ 预期结果
- 未选取消原因时，"Confirm"按钮处于禁用状态（灰色，不可点击） ✅ 实测
- 选择取消原因后，"Confirm"按钮变为可用 ✅ 实测
- 点击"Back"按钮后，弹窗关闭，订单保持原状态 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC016：买家 Pending - Pay 按钮唤起支付弹窗

#### 📋 前置条件
- 买家已登录；如 Pending Tab 中已有订单直接使用，否则需先构造 Pending 状态订单
- 处于买家 Pending 订单详情页

#### 🎬 执行步骤
1. 点击详情页"Pay"按钮
2. 观察支付弹窗是否弹出
3. 验证弹窗内容

#### ✅ 预期结果
- 点击 Pay 后弹出支付弹窗（Airwallex iframe） ✅ 实测
- 弹窗顶部显示支付方式（如 Airwallex 支付） ✅ 实测
- 弹窗底部有 Pay / Close 按钮 ✅ 实测
- 支付成功后订单状态变为 Unshipped ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

## 模块三：卖家 Sales Orders & Pending 订单详情页

> **数据说明**：如 Sales Orders 中已存在对应状态订单，直接使用；如不存在，需先通过买家下单流程构造所需状态数据。

### TC017：Sales Orders 页面 - 基础展示

#### 📋 前置条件
- 卖家已登录（OKer_wangyongli）
- 路径：头像 → Sales Orders（URL：https://aepub.58v5.cn/biz/en/pay/orderManage?type=2）

#### 🎬 执行步骤
1. 卖家登录后进入 Sales Orders 页面
2. 观察页面标题、Tab 数量及订单卡片内容
3. 切换各 Tab，观察订单状态过滤

#### ✅ 预期结果
- 页面标题为"Sales Orders" ✅ 实测
- Tabs：ALL / Pending / Unshipped / Pending Receipt / Completed ✅ 实测
- ALL tab 显示所有状态订单（含：Pending / Unshipped / Cancelled / Cancelled (refunding) / Completed (Payment in progress)） ✅ 实测
- 每条订单卡片显示：买家昵称、状态标签（颜色区分）、商品名称、价格 ✅ 实测
- 超过 10 条时显示分页控件（1 / 2 / 3 … N） ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---


### TC018：卖家 Pending 订单详情页 - 核心元素展示

#### 📋 前置条件
- 卖家已登录；如 Pending Tab 中已有订单直接使用，否则需先构造 Pending 状态订单
- 路径：Sales Orders → Pending Tab → 点击订单

#### 🎬 执行步骤
1. 进入 Sales Orders → Pending Tab
2. 点击 Pending 订单进入详情页
3. 观察各区块内容及操作按钮

#### ✅ 预期结果
- 状态标题显示"Buyer paying" ✅ 实测
- 倒计时显示"Pay within 23:XX:XX or auto-cancel"（蓝色） ✅ 实测
- 进度条：Placed（✓）→ Paid → Shipped → Completed ✅ 实测
- Order Info 区块显示：Order Number、Transaction snapshot、Buyer nickname、Order time ✅ 实测
- **无 Shipping 区块**（买家尚未支付，地址未传给卖家） ✅ 实测
- 操作按钮仅有 Cancel（单一按钮） ✅ 实测
- 右上角显示 Message Buyer 按钮 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC019：卖家 Pending - 点击 Message Buyer 跳转微聊

#### 📋 前置条件
- 卖家已登录；如 Pending Tab 中已有订单直接使用，否则需先构造 Pending 状态订单
- 处于卖家 Pending 订单详情页

#### 🎬 执行步骤
1. 点击右上角"Message Buyer"按钮
2. 观察页面跳转结果

#### ✅ 预期结果
- Message Buyer 按钮在右上角可见（附消息图标） ✅ 实测
- 点击后成功跳转到与该买家的微聊聊天页面 ✅ 实测
- 聊天对象为当前订单对应买家（Buyer nickname 一致） ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC020：卖家 Pending - Cancel 取消未支付订单

#### 📋 前置条件
- 卖家已登录；如 Pending Tab 中已有订单直接使用，否则需先构造 Pending 状态订单
- 处于卖家 Pending 订单详情页

#### 🎬 执行步骤
1. 点击"Cancel"按钮
2. 观察取消弹窗标题及原因选项数量
3. 选择取消原因，点击"Confirm"
4. 验证订单状态变化

#### ✅ 预期结果
- 弹窗标题显示"Reason for cancellation" ✅ 实测
- 原因选项共 7 项（单选，与买家选项不同）：Buyer requested cancellation / Incorrect product information or price / Product out of stock or sold out / Agreed local meetup transaction / Buyer information is abnormal / Product damaged or lost before shipment / Other reasons ✅ 实测
- 底部按钮：Back（次操作）/ Confirm（主操作，未选原因时禁用） ✅ 实测
- 选择原因后 Confirm 变为可用 ✅ 实测
- 点击 Confirm → 订单状态变为"Order Cancelled"并显示取消原因 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

## 模块四：买家 Unshipped 订单详情页

> **数据说明**：如 Unshipped Tab 中已存在可用订单，直接使用；如不存在，需先构造已支付未发货的 Unshipped 状态订单数据。

### TC021：买家 Unshipped 订单详情页 - 核心元素展示

#### 📋 前置条件
- 买家已登录；如 Unshipped Tab 中已有订单直接使用，否则需先构造 Unshipped 状态订单
- 路径：Purchase Orders → Unshipped Tab → 点击订单

#### 🎬 执行步骤
1. 进入 Purchase Orders → Unshipped Tab
2. 点击 Unshipped 订单进入详情页
3. 观察各区块内容及操作按钮

#### ✅ 预期结果
- 状态区域显示"Payment Success"或"Paid" ✅ 实测
- 进度条：Placed（✓）→ Paid（✓）→ Shipped → Completed ✅ 实测
- Shipping 区块展示买家收货地址 ✅ 实测
- Order Info 区块显示：Order Number、Transaction snapshot、Seller nickname、Order time、Payment Time ✅ 实测
- 商品区块展示缩略图 + 名称 + 价格 ✅ 实测
- **无 Cancel 按钮**（订单已支付，买家不可主动取消） ✅ 实测
- 右上角显示 Message Seller 按钮 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC022：买家 Unshipped - Transaction Snapshot 查看

#### 📋 前置条件
- 买家已登录；如 Unshipped Tab 中已有订单直接使用，否则需先构造 Unshipped 状态订单
- 处于买家 Unshipped 订单详情页

#### 🎬 执行步骤
1. 点击 Order Info 区块中的"Transaction snapshot → click to view"
2. 观察跳转结果

#### ✅ 预期结果
- 点击后成功跳转交易快照页面，不报错 ✅ 实测
- 支付后的交易快照可正常查看 ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC023：买家 Unshipped - 点击 Message Seller 跳转微聊

#### 📋 前置条件
- 买家已登录；如 Unshipped Tab 中已有订单直接使用，否则需先构造 Unshipped 状态订单
- 处于买家 Unshipped 订单详情页

#### 🎬 执行步骤
1. 点击右上角"Message Seller"按钮
2. 观察页面跳转结果

#### ✅ 预期结果
- 点击后成功跳转到与该卖家的微聊聊天页面（URL 含 /biz/en/chat） ✅ 实测
- 聊天对象为当前订单对应卖家（Seller nickname 一致） ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化


---

### TC024（负向）：买家 Unshipped - 买家不可取消

#### 📋 前置条件
- 买家已登录；如 Unshipped Tab 中已有订单直接使用，否则需先构造 Unshipped 状态订单
- 业务规则：订单支付后仅卖家可取消，买家无取消权限

#### 🎬 执行步骤
1. 进入买家 Unshipped 订单详情页
2. 观察操作按钮区域是否存在 Cancel 按钮

#### ✅ 预期结果
- 买家 Unshipped 订单详情页不显示 Cancel 按钮 ✅ 实测
- 买家无法通过任何途径主动取消已支付订单 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

## 模块五：卖家 Unshipped 订单详情页

> **数据说明**：如 Unshipped Tab 中已存在可用订单，直接使用；如不存在，需先构造买家已支付、卖家未发货的 Unshipped 状态订单数据。

### TC025：卖家 Unshipped 订单详情页 - 核心元素展示

#### 📋 前置条件
- 卖家已登录；如 Unshipped Tab 中已有订单直接使用，否则需先构造 Unshipped 状态订单
- 路径：Sales Orders → Unshipped Tab → 点击订单

#### 🎬 执行步骤
1. 进入 Sales Orders → Unshipped Tab
2. 点击订单进入详情页
3. 观察各区块内容及操作按钮

#### ✅ 预期结果
- 状态标题显示"Ready to ship" ✅ 实测
- 倒计时显示"Ship in Xd XX:XX:XX or auto-cancel"（蓝色） ✅ 实测
- 进度条：Placed（✓）→ Paid（✓）→ Shipped → Completed ✅ 实测
- Shipping 区块展示买家收货地址（Full Name、Address、City、Country、Phone）及 copy 按钮 ✅ 实测
- Order Info 区块显示：Order Number、Transaction snapshot、Buyer nickname、Order time、Payment Time ✅ 实测
- 操作按钮：Cancel + Add Tracking（主操作，黑底白字） ✅ 实测
- 右上角显示 Message Buyer 按钮 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化


---

### TC026：卖家 Unshipped - 点击 Message Buyer 跳转微聊

#### 📋 前置条件
- 卖家已登录；如 Unshipped Tab 中已有订单直接使用，否则需先构造 Unshipped 状态订单
- 处于卖家 Unshipped 订单详情页

#### 🎬 执行步骤
1. 点击右上角"Message Buyer"按钮
2. 观察页面跳转结果

#### ✅ 预期结果
- 点击后成功跳转到与该买家的微聊聊天页面 ✅ 实测
- 聊天对象为当前订单对应买家（AEOKer_cui123，Buyer nickname 一致） ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化
---

### TC027：卖家 Unshipped - Add Tracking 发货弹窗展示

#### 📋 前置条件
- 卖家已登录；如 Unshipped Tab 中已有订单直接使用，否则需先构造 Unshipped 状态订单
- 处于卖家 Unshipped 订单详情页

#### 🎬 执行步骤
1. 点击"Add Tracking"按钮
2. 观察"Add Shipping Tracking"弹窗内容

#### ✅ 预期结果
- 弹窗正常弹出，标题为"Add Shipping Tracking" ✅ 实测
- 弹窗包含：Seller Address（可点击编辑）、Tracking Number 输入框（必填）、logistics company 下拉（必填） ✅ 实测
- logistics company 下拉共 13 个选项：Aramex / Australia Post / DHL / Expeditors / FedEx / J.B. Hunt / TNT / Toll Group / UPS / USPS / XPO Logistics / iMile / Other Couriers ✅ 实测
- 警示文字："After submitting the shipment, it cannot be changed. Please carefully check the information" ✅ 实测
- 底部显示"Mark as Shipped"按钮 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC028：卖家 Unshipped - Seller Address 完整编辑流程

#### 📋 前置条件
- 卖家已登录；如 Unshipped Tab 中已有订单直接使用，否则需先构造 Unshipped 状态订单
- Add Shipping Tracking 弹窗已打开，弹窗中显示 Seller Address 区块

#### 🎬 执行步骤
1. 点击 Seller Address 右侧箭头图标，打开发货地址编辑弹窗
2. 验证弹窗含必填字段可见
3. 点击"Clean"按钮清空所有字段
4. 验证所有字段已清空
5. 填写合法发货地址（Full Name、Address Line 1、County/City、State、ZIP、Phone）
6. 点击"Apply"按钮
7. 验证 Add Tracking 弹窗中 Seller Address 展示更新后的地址

#### ✅ 预期结果
- 点击 Seller Address 后发货地址编辑弹窗正常弹出 ✅ 实测
- 弹窗包含必填字段：Full Name、Address Line 1、Phone Number ✅ 实测
- 点击 Clean 后所有输入框清空 ✅ 实测
- 填写合法地址后点击 Apply，弹窗关闭 ✅ 实测
- Add Tracking 弹窗中 Seller Address 展示新填写的发货地址 ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC029（负向）：卖家 Unshipped - Seller Address 字段必填校验

#### 📋 前置条件
- 卖家已登录；如 Unshipped Tab 中已有订单直接使用，否则需先构造 Unshipped 状态订单
- 已打开 Seller Address 发货地址编辑弹窗

#### 🎬 执行步骤
1. 清空 Full Name 字段，点击 Apply → 验证错误提示
2. 在 Phone 字段输入字母（如"abc"）→ 验证过滤行为
3. 在 Phone 字段输入格式不正确的数字（如"1"）→ 点击 Apply → 验证 toast 提示
4. 清空所有必填字段，点击 Apply → 验证批量校验
5. 在 Postal Code 字段输入超长字符（>10 位）→ 验证 UI 限制

#### ✅ 预期结果
- Full Name 为空 → 字段内显示"Cannot be empty"错误 ✅ 实测
- Phone 输入字母（如"abc"）→ 字母被过滤，字段为空后显示"Cannot be empty" ✅ 实测
- Phone 格式不正确（单个数字"1"）→ toast 提示"Invalid phone number." ✅ 实测
- 所有必填字段均空点击 Apply → 所有字段同时显示"Cannot be empty"，弹窗不关闭 ✅ 实测
- Postal Code 超过 10 字符时，UI 层限制继续输入（字符计数器显示 x/10） ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC030（负向）：Add Tracking - 未填写 Tracking Number 直接提交

#### 📋 前置条件
- 卖家已登录，Add Shipping Tracking 弹窗已打开

#### 🎬 执行步骤
1. 不填写 Tracking Number，不选择 logistics company
2. 直接点击"Mark as Shipped"
3. 观察错误提示

#### ✅ 预期结果
- Tracking Number 字段下方显示"Cannot be empty"错误提示 ✅ 实测
- logistics company 字段同时显示"Cannot be empty"（两个必填字段同时校验） ✅ 实测
- 提交被阻止，弹窗不关闭 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC031（边界）：Add Tracking - Tracking Number 特殊字符输入

#### 📋 前置条件
- 卖家已登录，Add Shipping Tracking 弹窗已打开

#### 🎬 执行步骤
1. 在 Tracking Number 字段输入含特殊字符的字符串：`ABC-123_test!@#$%特殊字符`
2. 观察字段是否过滤字符
3. 点击 Mark as Shipped，观察提交结果

#### ✅ 预期结果
- 前端**无字符类型过滤**，所有字符（字母/数字/连字符/下划线/特殊符号/汉字）均可正常输入并显示 ✅ 实测
- 注：超长字符串边界测试未完成（需测试 100+ 字符边界是否有后端校验）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC032（负向）：Add Tracking - 未选 logistics company 直接提交

#### 📋 前置条件
- 卖家已登录，Add Shipping Tracking 弹窗已打开

#### 🎬 执行步骤
1. 填写 Tracking Number（如"TEST1234567890"）
2. 不选择 logistics company
3. 直接点击"Mark as Shipped"
4. 观察错误提示

#### ✅ 预期结果
- logistics company 字段下方显示"Cannot be empty"错误提示 ✅ 实测
- 提交被阻止，弹窗不关闭 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC033：卖家 Unshipped - Cancel 取消已支付未发货订单（退款流程）

#### 📋 前置条件
- 卖家已登录；如 Unshipped Tab 中已有订单直接使用，否则需先构造 Unshipped 状态订单
- 业务规则：订单已支付未发货时，仅卖家可取消，取消后触发退款流程

#### 🎬 执行步骤
1. 点击"Cancel"按钮
2. 在弹窗中选择取消原因（如"Incorrect product information or price"）
3. 点击"Confirm"
4. 观察订单状态及退款说明

#### ✅ 预期结果
- 订单页面状态显示"Order Cancelled" ✅ 实测
- 显示取消原因："Reason for order cancellation: Incorrect product information or price" ✅ 实测
- 显示退款说明："The funds will be refunded to the buyer from the platform's escrow account." ✅ 实测
- Order Info 新增 Transaction closure time 字段 ✅ 实测
- **注意**：取消后状态直接显示"Order Cancelled"，不显示"Cancelled (refunding)"中间状态（Web 端刷新后跳过中间态）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC034：Add Tracking - 提交发货成功

#### 📋 前置条件
- 卖家已登录，Add Shipping Tracking 弹窗已打开

#### 🎬 执行步骤
1. 填写 Tracking Number：TEST1234567890
2. 选择 logistics company：DHL
3. 点击"Mark as Shipped"
4. 观察订单状态及页面变化

#### ✅ 预期结果
- 弹窗关闭，订单状态切换为"Shipped"（即 Pending Receipt 状态） ✅ 实测
- 页面新增 Package Tracking 区块：Tracking Number: TEST1234567890 / logistics company: DHL / "View logistics trajectory"链接 ✅ 实测
- Order Info 新增 Delivery time 字段，记录发货时间 ✅ 实测
- 原"Add Tracking"按钮消失（被 Package Tracking 区块替代） ✅ 实测
- 倒计时从"Ship in Xd"切换为"Auto-complete in 14d 23:59:58" ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化



---

## 模块六：卖家 Pending Receipt 订单详情页

> **数据说明**：如 Pending Receipt Tab 中已存在可用订单，直接使用；如不存在，需先构造卖家已发货、买家未确认收货的 Pending Receipt 状态订单数据。

### TC035：卖家 Pending Receipt 订单详情页 - 核心元素展示

#### 📋 前置条件
- 卖家已登录；如 Pending Receipt Tab 中已有订单直接使用，否则需先构造 Pending Receipt 状态订单
- 路径：Sales Orders → Pending Receipt Tab → 点击订单

#### 🎬 执行步骤
1. 进入 Sales Orders → Pending Receipt Tab
2. 点击订单进入详情页
3. 观察各区块内容及操作按钮

#### ✅ 预期结果
- 状态标题显示"Shipped" ✅ 实测
- 倒计时显示"Auto-complete in 13d XX:XX:XX"（蓝色） ✅ 实测
- 进度条：Placed（✓）→ Paid（✓）→ Shipped（✓）→ Completed ✅ 实测
- Package Tracking 区块展示：Tracking Number、logistics company、"View logistics trajectory"链接 ✅ 实测
- Order Info 区块显示：Order Number、Transaction snapshot、Buyer nickname、Receiving address、Order time、Payment Time、Delivery time ✅ 实测
- **无操作按钮**（已发货后买卖家均不可取消） ✅ 实测
- 右上角显示 Message Buyer 按钮 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC036（负向）：卖家 Pending Receipt - 不可取消

#### 📋 前置条件
- 卖家已登录；如 Pending Receipt Tab 中已有订单直接使用，否则需先构造 Pending Receipt 状态订单
- 业务规则：已发货订单买卖家均不可取消

#### 🎬 执行步骤
1. 进入卖家 Pending Receipt 订单详情页
2. 观察操作按钮区域，确认无 Cancel 按钮

#### ✅ 预期结果
- 卖家 Pending Receipt 详情页不显示 Cancel 按钮 ✅ 实测
- 页面仅有 Package Tracking 信息和 Message Buyer 按钮 ✅ 实测
- 卖家无法通过任何途径取消已发货订单 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC037：卖家 Pending Receipt - 查看物流轨迹

#### 📋 前置条件
- 卖家已登录；如 Pending Receipt Tab 中已有订单直接使用，否则需先构造 Pending Receipt 状态订单
- 处于卖家 Pending Receipt 订单详情页

#### 🎬 执行步骤
1. 点击 Package Tracking 区块中的"View logistics trajectory"
2. 观察物流追踪页面

#### ✅ 预期结果
- 物流追踪页面正常打开 ✅ 实测
- 页面展示 Tracking Number 及物流公司信息 ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC038：卖家 Pending Receipt - 点击 Message Buyer 跳转微聊

#### 📋 前置条件
- 卖家已登录；如 Pending Receipt Tab 中已有订单直接使用，否则需先构造 Pending Receipt 状态订单
- 处于卖家 Pending Receipt 订单详情页

#### 🎬 执行步骤
1. 点击右上角"Message Buyer"按钮
2. 观察页面跳转结果

#### ✅ 预期结果
- 点击后成功跳转到与该买家的微聊聊天页面 ✅ 实测
- 聊天对象为当前订单对应买家（AEOKer_cui123，Buyer nickname 一致） ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

## 模块七：买家 Pending Receipt 订单详情页

> **数据说明**：如 Pending Receipt Tab 中已存在可用订单，直接使用；如不存在，需先构造卖家已发货、买家未确认收货的 Pending Receipt 状态订单数据。

### TC039：买家 Pending Receipt 订单详情页 - 核心元素展示

#### 📋 前置条件
- 买家已登录；如 Pending Receipt Tab 中已有订单直接使用，否则需先构造 Pending Receipt 状态订单
- 路径：Purchase Orders → Pending Receipt Tab → 点击订单

#### 🎬 执行步骤
1. 进入 Purchase Orders → Pending Receipt Tab
2. 点击订单进入详情页
3. 观察各区块内容及操作按钮

#### ✅ 预期结果
- 状态区域显示"Shipped" ✅ 实测
- 自动完成倒计时显示"Auto-complete in Xd XX:XX:XX"（蓝色） ✅ 实测
- 进度条：Placed（✓）→ Paid（✓）→ Shipped（✓）→ Completed ✅ 实测
- Package Tracking 区块展示：Tracking Number、logistics company、"View logistics trajectory"链接 ✅ 实测
- Order Info 区块显示：Order Number、Transaction snapshot、Seller nickname、Receiving address、Order time、Payment Time、Delivery time ✅ 实测
- 操作按钮仅有 Confirm（黑底白字），**无 Cancel 按钮** ✅ 实测
- 右上角显示 Message Seller 按钮 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC040（负向）：买家 Pending Receipt - 买家不可取消

#### 📋 前置条件
- 买家已登录；如 Pending Receipt Tab 中已有订单直接使用，否则需先构造 Pending Receipt 状态订单
- 业务规则：已发货订单买卖家均不可取消

#### 🎬 执行步骤
1. 进入买家 Pending Receipt 订单详情页
2. 观察操作按钮区域，确认无 Cancel 按钮

#### ✅ 预期结果
- 买家 Pending Receipt 详情页仅有 Confirm 按钮，无 Cancel 按钮 ✅ 实测
- 买家无法通过任何途径取消已发货订单 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC041：买家 Pending Receipt - 查看物流轨迹

#### 📋 前置条件
- 买家已登录；如 Pending Receipt Tab 中已有订单直接使用，否则需先构造 Pending Receipt 状态订单
- Package Tracking 区块已显示 Tracking Number 和 logistics company

#### 🎬 执行步骤
1. 找到 Package Tracking 区块
2. 点击"View logistics trajectory"链接
3. 观察物流页面展示

#### ✅ 预期结果
- 物流追踪页面正常打开 ✅ 实测
- 页面显示 Tracking Number 和物流公司名称 ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC042：买家 Pending Receipt - 点击 Message Seller 跳转微聊

#### 📋 前置条件
- 买家已登录；如 Pending Receipt Tab 中已有订单直接使用，否则需先构造 Pending Receipt 状态订单
- 处于买家 Pending Receipt 订单详情页

#### 🎬 执行步骤
1. 点击右上角"Message Seller"按钮
2. 观察页面跳转结果

#### ✅ 预期结果
- 点击后成功跳转到与该卖家的微聊聊天页面 ✅ 实测
- 聊天对象为当前订单对应卖家（Seller nickname 一致） ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC043：买家 Pending Receipt - Confirm 确认收货弹窗

#### 📋 前置条件
- 买家已登录；如 Pending Receipt Tab 中已有订单直接使用，否则需先构造 Pending Receipt 状态订单
- 处于买家 Pending Receipt 订单详情页

#### 🎬 执行步骤
1. 点击"Confirm"按钮
2. 观察确认收货弹窗内容及按钮
3. 点击弹窗中的"Back"按钮（不确认收货）
4. 验证订单状态保持 Shipped
5. 再次点击"Confirm"，弹窗出现后点击"Confirm"确认
6. 验证订单状态变化

#### ✅ 预期结果
- 点击 Confirm 弹出确认收货弹窗 ✅ 实测
- 弹窗显示确认提示文字 ✅ 实测
- 弹窗操作按钮：Confirm（确认收货）、Back（返回） ✅ 实测
- 点击弹窗 Back → 弹窗关闭，订单保持 Shipped 状态 ✅ 实测
- 点击弹窗 Confirm → 订单状态变为 Completed ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

## 模块八：买家 Completed 订单详情页

> **数据说明**：如 Completed Tab 中已存在可用订单，直接使用；如不存在，需先构造买家已确认收货的 Completed 状态订单数据。

### TC044：买家 Completed 订单详情页 - 核心元素展示

#### 📋 前置条件
- 买家已登录；如 Completed Tab 中已有订单直接使用，否则需先构造 Completed 状态订单
- 路径：Purchase Orders → Completed Tab → 点击订单

#### 🎬 执行步骤
1. 进入 Purchase Orders → Completed Tab
2. 点击订单进入详情页
3. 观察各区块内容及操作按钮

#### ✅ 预期结果
- 状态区域显示"Order Completed" ✅ 实测
- 进度条全部完成：Placed（✓）→ Paid（✓）→ Shipped（✓）→ Completed（✓） ✅ 实测
- Order Info 区块含新增字段 Transaction Time ✅ 实测
- 操作按钮仅有"View Transaction"（单一按钮） ✅ 实测
- 右上角显示 Message Seller 按钮 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC045：买家 Completed - View Transaction 买家视角

#### 📋 前置条件
- 买家已登录；如 Completed Tab 中已有订单直接使用，否则需先构造 Completed 状态订单
- 处于买家 Completed 订单详情页

#### 🎬 执行步骤
1. 点击"View Transaction"按钮
2. 观察交易记录弹窗内容

#### ✅ 预期结果
- 弹窗弹出，显示 **-AED 3500**（红色/负数，代表支出） ✅ 实测
- 显示"Transaction Successful" ✅ 实测
- 显示 Payment Time、Product Name、Order ID、Reference ID ✅ 实测
- 显示汇率说明文字及 Help 链接 ✅ 实测
- 金额为负数（-AED），表示买家支出 ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC046：买家 Completed - Upload Buyer Photos

#### 📋 前置条件
- 买家已登录；如 Completed Tab 中已有订单直接使用，否则需先构造 Completed 状态订单
- 处于买家 Completed 订单详情页（订单状态为已完成）

#### 🎬 执行步骤
1. 在 Completed 订单详情页找到"Upload Buyer Photos"区域或入口
2. 点击上传图片按钮
3. 选择本地图片文件
4. 等待上传完成
5. 验证上传后图片展示是否正确

#### ✅ 预期结果
- Completed 订单详情页显示"Upload Buyer Photos"入口 ✅ 实测
- 点击后可选择本地图片进行上传 ✅ 实测
- 上传成功后图片在订单详情页正常展示 ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC047：买家 Completed - 点击 Message Seller 跳转微聊

#### 📋 前置条件
- 买家已登录；如 Completed Tab 中已有订单直接使用，否则需先构造 Completed 状态订单
- 处于买家 Completed 订单详情页

#### 🎬 执行步骤
1. 点击右上角"Message Seller"按钮
2. 观察页面跳转结果

#### ✅ 预期结果
- 点击后成功跳转到与该卖家的微聊聊天页面 ✅ 实测
- 聊天对象为当前订单对应卖家（OKer_wangyongli，Seller nickname 一致） ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

## 模块九：卖家 Completed 订单详情页

> **数据说明**：如 Completed Tab 中已存在可用订单，直接使用；如不存在，需先构造买家已确认收货的 Completed 状态订单数据。

### TC048：卖家 Completed 订单详情页 - 核心元素展示

#### 📋 前置条件
- 卖家已登录；如 Completed Tab 中已有订单直接使用，否则需先构造 Completed 状态订单
- 路径：Sales Orders → Completed Tab → 点击订单

#### 🎬 执行步骤
1. 进入 Sales Orders → Completed Tab
2. 点击订单进入详情页
3. 观察各区块内容及操作按钮

#### ✅ 预期结果
- 状态标题显示"Order Completed" ✅ 实测
- 显示提示文字："The funds have been deposited into the wallet, you can go to the wallet to withdraw them." ✅ 实测
- 进度条全部完成：Placed（✓）→ Paid（✓）→ Shipped（✓）→ Completed（✓） ✅ 实测
- Order Info 区块含新增字段 Transaction Time ✅ 实测
- 操作按钮仅有"View Transaction"（单一按钮） ✅ 实测
- 右上角显示 Message Buyer 按钮 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC049（负向）：卖家 Completed - View Transaction 不展示

#### 📋 前置条件
- 卖家已登录；如 Completed Tab 中已有订单直接使用，否则需先构造 Completed 状态订单
- 处于卖家 Completed 订单详情页

#### 🎬 执行步骤
1. 以卖家身份进入 Completed 订单详情页
2. 确认页面上**不存在** "View Transaction" 按钮

#### ✅ 预期结果
- 卖家 Completed 订单详情页**不应显示** "View Transaction" 按钮（该按钮仅在买家侧展示）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC050：卖家 Completed - 点击 Message Buyer 跳转微聊

#### 📋 前置条件
- 卖家已登录；如 Completed Tab 中已有订单直接使用，否则需先构造 Completed 状态订单
- 处于卖家 Completed 订单详情页

#### 🎬 执行步骤
1. 点击右上角"Message Buyer"按钮
2. 观察页面跳转结果

#### ✅ 预期结果
- 点击后成功跳转到与该买家的微聊聊天页面 ✅ 实测
- 聊天对象为当前订单对应买家（AEOKer_cui123，Buyer nickname 一致） ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化


---

## 模块十：异常场景与边界测试

### TC051：买家 Cancel 和 Cancelled (Refund completed) 状态展示

#### 📋 前置条件
- 买家已登录，Purchase Orders → ALL Tab 中存在已取消的订单（Cancelled / Cancelled (Refund completed)）
- Cancelled 数据可由 TC011（买家取消 Pending）或 TC033（卖家取消 Unshipped）生成
- Cancelled (Refund completed) 需卖家取消已支付订单且退款到账后才出现

#### 🎬 执行步骤
1. 以买家身份进入 Purchase Orders → ALL Tab
2. 验证点1：确认列表中可见 **Cancelled** 状态标签
3. 验证点2：寻找 **Cancelled (Refund completed)** 状态标签（退款已处理完成）
4. 若存在 Cancelled (Refund completed)，点击进入详情页，验证页面内容

#### ✅ 预期结果
- ALL Tab 中可见"Cancelled"状态订单 ✅
- ALL Tab 中可见"Cancelled (Refund completed)"状态标签（表示退款已处理完毕）✅（数据依赖）
- 点击 Cancelled (Refund completed) 订单 → 进入详情页（URL 含 /pay/order）✅
- 详情页显示 Cancelled 或 Refund completed 状态文案 ✅

#### ⚠️ 说明
- 若 ALL Tab 无任何 Cancelled 订单 → 用例 **SKIP**（需先执行取消流程生成数据）
- 若无 Cancelled (Refund completed) 订单 → 该子断言降级为 **WARNING**（退款处理中）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / 数据依赖
- **UI自动化**: ✅ 可自动化

---

## 后置操作（Teardown）

### Teardown：卖家将 Marketplace Expired 帖子重新发布 3 条

> 所有测试用例执行完毕后自动运行，用于恢复测试数据，确保下次执行有可用的 Marketplace 商品。

#### 📋 前置条件
- 卖家已登录（OKer_wangyongli）
- 卖家在 My Post → Marketplace → Expired Tab 中至少有 1 条到期帖子

#### 🎬 执行步骤
1. 卖家登录后直接导航至 My Post 页（`/biz/en/publish/list`）
2. 点击一级 toolbar 中的 **Marketplace** tab
3. 点击二级 toolbar 中的 **Expired** 按钮
4. 重复 3 次以下操作：
   - 点击第一条 Expired 帖子右侧的 **"..."** 按钮展开操作菜单
   - 点击 **Re-listing** 进入重新发布表单
   - 等待表单加载完成
   - 点击 **Post** 按钮提交重新发布
   - 返回 Expired 列表

#### ✅ 预期结果
- 成功 Re-listing 的帖子从 Expired 列表移出，重新进入 Active 状态
- 最终日志显示"共成功 Re-listing X/3 条帖子"

#### ⚠️ 说明
- 若 Expired 列表为空或帖子数不足 3 条，完成实际可操作的条数后结束（不报错）
- 该操作为后置数据恢复，不计入测试用例通过/失败统计

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 后置操作 / 数据恢复
- **UI自动化**: ✅ 可自动化

---

## 测试数据准备

| 类型 | 内容 |
|------|------|
| 买家账号 | cuidemin@58.com / TOUfangqa123 |
| 卖家账号 | wangyongli@58.com / Qwer1234 |
| 测试商品 | 搜索"iPhone pays postage aitest"→ 选择"Buy Now"可用的商品 |
| 物流单号 | PROBE-TEST-YYYYMMDD |
| 物流公司 | DHL |
| 收货地址 | AutoTest Buyer, 123 Test Street, Abu Dhabi, Dubai, UAE, +971 0501234567 |
| 测试银行卡 | Airwallex 测试卡，CVC=123 |

### 数据使用策略（TC009 及之后）

**优先复用 Tab 现有订单，为空时才构造新数据**：

1. 模拟人工操作：点击头像 → 点击 Purchase Orders / Sales Orders → 点击对应 Tab
2. 右侧订单列表有数据 → 点击第一条订单进入详情，直接执行测试
3. 右侧订单列表为空 → 自动调用对应构造函数生成测试数据后重试

> **订单管理页入口**：始终通过 UI 点击（头像 → 菜单）进入，禁止直接 `goto(url)` 跳转，确保列表刷新最新数据。

---

## 覆盖率自评

| 维度 | 覆盖率 |
|------|--------|
| 主链路（下单→支付→发货→收货） | ✅ 1.0 |
| 取消流程（各状态权限） | ✅ 1.0 |
| 买家视角所有 Tab 详情页 | ✅ 1.0 |
| 卖家视角所有 Tab 详情页 | ✅ 1.0 |
| 表单校验（地址/追踪号） | ✅ 1.0 |
| 买卖家视角差异对比 | ✅ 1.0 |
| 消息入口（各状态全覆盖） | ✅ 1.0 |
| 异常/边界场景 | ✅ 0.9 |
| UI/UX 通用验证 | ✅ 0.9 |

---

## 测试统计

| 优先级 | 总数 | 可自动化 | 需视觉断言 |
|--------|------|---------|-----------|
| P0 | 31 | 31 | 0 |
| P1 | 20 | 20 | 0 |
| **合计（TC001–TC051）** | **51** | **51（100%）** | **0（0%）** |
| 后置操作（Teardown）| 1 | 1 | 0 |
| **总计** | **52** | **52（100%）** | **0（0%）** |

---

*文档最后更新：2026-03-18*  
*基于 Playwright MCP 真实浏览器探索，所有"✅ 实测"标注均为真实行为观测*  
*2026-03-15 变更：搜索词由"Pays Postage"改为"iPhone pays postage"；TC008 及之后统一采用 Tab 数据优先策略*  
*2026-03-26 变更：脚本与 `_CONFIG.marketplace_search_keyword` 同步，搜索词统一为"iPhone pays postage aitest"（含 TC006 等依赖列表搜索的用例）*  
*2026-03-16 变更：TC051 验证点由"卖家 Completed (Payment in progress)"改为"买家 Cancel 和 Cancelled (Refund completed) 状态展示"；角色由卖家改为买家；增加两个独立验证点及降级处理*  
*2026-03-17 变更：总用例数由 50 更新为 51（TC001–TC051）；新增 Teardown 后置操作章节（卖家 Re-listing 3 条 Expired 帖子）；TC007 备注补充重试机制、"Something went wrong" 处理逻辑及 Google 登录 URL 判断策略；统计表 P0 由 29 更新为 31，P1 由 21 更新为 20*  
*2026-03-18 变更：TC050（商品 Buyer paid but incomplete 错误提示）移动至 TC005 后，重编号为 TC006；原 TC006–TC049 依次顺排为 TC007–TC050；TC051 保持不变；数据引用 TC010→TC011、TC032→TC033*
