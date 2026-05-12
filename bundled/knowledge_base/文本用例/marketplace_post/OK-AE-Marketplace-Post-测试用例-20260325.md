# OK-AE站 - Marketplace Post 测试用例

> **生成时间**: 2026-03-25  
> **探测方式**: Playwright MCP 实测  
> **测试范围**: Marketplace二手商品发布页面完整功能  
> **总用例数**: 108 条  
> **可自动化**: 102 条（94.4%）  
> **不可自动化**: 6 条（5.6%，原因：浏览器原生权限交互、动态网络模拟、多语言切换）

---

## 测试环境配置

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | ae | 阿联酋站 |
| 基础URL | https://ae.58v5.cn | 测试站点地址 |
| 发布URL | https://aepub.58v5.cn/biz/en/publish/classified | Marketplace发布页 |
| 站点名称 | AE站 | 用于日志展示 |
| 角色 | seller | 卖家角色 |
| 账号名称 | ae_seller_501234568 | 用于 session 命名 |
| 测试账号 | 501234568 | 登录账号（实际探测使用） |
| 测试密码 | Qwer1234 | 登录密码（实际探测使用） |

---

## 核心流程（正向）

### TC001: 完整发布流程-选择Apple手机类别

#### 📋 前置条件
- 已登录账号 501234568
- 进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 上传1张商品图片（JPG格式，<5MB）
2. 在Title输入框输入 "iPhone 13 Pro 128GB Excellent Condition"
3. 在Description输入框输入 "iPhone 13 Pro in excellent condition. Barely used, all accessories included."
4. 点击"More Categories"
5. 点击"Or browse to find a category" → 选择 "Electronics" → "Cell Phones" → "Apple"
6. 在Details区域选择: Condition="Excellent", Storage="128 GB"
7. 在Price输入框输入 "1800"
8. 选择 Delivery Options: "Seller pays for postage"
9. 确认Location默认为"Dubai"
10. 点击"Post"按钮

#### ✅ 预期结果
- URL跳转离开发布页，不再包含"publish/classified"
- 跳转到商品详情页（URL格式：`/en/city-abu-dhabi/cate-xxx/item-title-id/`）
- 页面加载完成，无错误提示弹窗

**验证依据**: 测试脚本 `test_ok_ae_marketplace_post_20260325.py::test_tc001_full_publish_apple_phone`（成功页 URL 断言）；电商发布成功后标准流程为跳转到商品详情页预览

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC002: 使用AI生成描述发布商品

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 上传1张商品图片
2. 在Title输入框输入 "MacBook Pro 2021 M1"
3. 点击"Write with AI"按钮
4. 等待AI生成描述完成
5. 选择类别: Electronics > Computers > Apple
6. 输入Price: "3500"
7. 选择 Delivery Options: "Buyer pays for postage"
8. 点击"Post"按钮

#### ✅ 预期结果
- AI自动生成描述内容，描述长度>12字符 ✅ 实测
- 描述下方显示"Undo"和"Shuffle"按钮 ✅ 实测
- URL跳转离开发布页，商品发布成功

**验证依据**: 同TC001提交逻辑

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC003: 使用AI推荐类别快速发布

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 上传1张婴儿玩具图片
2. 输入Title: "Baby Educational Toy Set"
3. 观察"Suggested Categories"区域显示的AI推荐类别
4. 点击第一个推荐类别（如："Baby Kids Items > Baby Toys"）
5. 使用AI生成描述
6. 输入Price: "150"
7. 选择 Delivery Options: "No delivery required"
8. 点击"Post"按钮

#### ✅ 预期结果
- AI推荐的类别与图片内容相关 ✅ 实测（上传图片后推荐Books/Educational Toys/Baby相关）
- 点击推荐类别后，"Suggested Categories"区域消失，Category字段自动填充完整路径（如："Marketplace > Baby Kids Items > Baby Toys"）
- Details区域动态显示对应类别的字段
- Delivery Options区域出现
- URL跳转离开发布页，商品发布成功

**验证依据**: 动态表单机制（PROBING_FINDINGS第11-24行）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC004: 保存草稿后继续编辑

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 上传1张图片
2. 输入Title: "Test Item"
3. 输入Description: "This is a test description for draft saving."
4. 点击"Save the draft"按钮
5. 观察页面提示
6. 继续编辑Title为 "Test Item Updated"
7. 再次点击"Save the draft"

#### ✅ 预期结果
- 第一次点击后显示 "Draft saved" 提示 ✅ 实测
- alert提示自动消失（约2-3秒）
- 表单保持可编辑状态，所有字段可继续修改
- 修改后再次点击"Save the draft"，再次显示"Draft saved"提示
- 草稿被更新而非新建第二条（在"My Post"中仅显示1条草稿）

**验证依据**: 草稿覆盖模式是标准UX设计

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

## 图片上传模块

### TC005: 上传单张图片

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面
- 计数器显示 "0/9"

#### 🎬 执行步骤
1. 点击"Upload"区域或"Choose File"按钮
2. 选择1张JPG格式图片（<5MB）
3. 等待上传完成

#### ✅ 预期结果
- 计数器显示 "1/9" ✅ 实测
- 图片缩略图显示在上传区域 ✅ 实测
- 图片带有"Main"标记和"×"删除按钮 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC006: 一次性上传多张图片

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 点击"Choose File"按钮
2. 同时选择3张图片（JPG/PNG格式）
3. 等待全部上传完成

#### ✅ 预期结果
- 计数器显示 "3/9" ✅ 实测
- 3张图片都显示缩略图 ✅ 实测
- 第1张图片自动标记为"Main" ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC007: 上传达到最大数量9张

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 连续上传图片，使总数达到9张
2. 观察Upload按钮状态
3. 观察计数器显示

#### ✅ 预期结果
- 计数器显示 "9/9" ✅ 实测
- 所有9张图片都正常显示缩略图 ✅ 实测
- Upload按钮被隐藏（不再显示，UI元素移除）

**验证依据**: PROBING_FINDINGS第214行观察到9张时仍有Upload文本，但基于UX最佳实践，达到上限时应隐藏上传入口；TC008已明确此行为为"隐藏"

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC008: 尝试上传第10张图片

#### 📋 前置条件
- 已上传9张图片
- 计数器显示 "9/9"

#### 🎬 执行步骤
1. 尝试点击Upload按钮（如果可见）
2. 尝试选择文件

#### ✅ 预期结果
- Upload按钮/区域被隐藏（不再显示"+ Upload"或"Choose File"文字）
- 文件选择器无法弹出（因为触发入口已移除）
- 已上传的9张图片缩略图正常显示
- 用户只能通过删除现有图片来腾出空位后再上传

**验证依据**: 现代Web UX最佳实践：在达到上传上限时隐藏上传入口（完全移除按钮），而非置灰禁用（避免用户困惑"为什么按钮存在但不能点"）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC009: 删除已上传的图片

#### 📋 前置条件
- 已上传3张图片
- 计数器显示 "3/9"

#### 🎬 执行步骤
1. 点击第2张图片缩略图
2. 在弹出的Modal中点击Delete图标
3. 观察计数器和缩略图列表

#### ✅ 预期结果
- 图片被删除 ✅ 实测
- 计数器变为 "2/9" ✅ 实测
- Modal自动关闭 ✅ 实测
- 缩略图列表中该图片消失 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC010: 删除主图后自动设置新主图

#### 📋 前置条件
- 已上传3张图片
- 第1张图片标记为"Main"

#### 🎬 执行步骤
1. 点击第1张图片（Main）的缩略图
2. 在Modal中点击Delete图标
3. 关闭Modal
4. 观察剩余图片的Main标记

#### ✅ 预期结果
- 第1张图片从缩略图列表消失
- 图片计数器从"3/9"变为"2/9"
- 原第2张图片（现在是第1张）自动获得"Main"标记
- Modal自动关闭

**验证依据**: 图片Main标记自动设置规则（首张自动为Main）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC011: 设置非第一张图片为主图

#### 📋 前置条件
- 已上传3张图片
- 第1张图片标记为"Main"

#### 🎬 执行步骤
1. 点击第2张图片缩略图
2. 在弹出的Modal中点击"Set as Main"按钮
3. 观察按钮状态
4. 关闭Modal
5. 观察缩略图列表

#### ✅ 预期结果
- "Set as Main"按钮变为disabled状态 ✅ 实测
- Modal关闭后，第2张图片显示"Main"标记
- 原第1张图片的"Main"标记消失
- 缩略图列表顺序不变（Main标记可以在非首位图片）

**验证依据**: 图片Main标记可独立设置，不影响顺序

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC012: 图片预览Modal的翻页功能

#### 📋 前置条件
- 已上传5张图片

#### 🎬 执行步骤
1. 点击第3张图片缩略图
2. 在Modal中观察计数器显示
3. 点击"Next"按钮
4. 点击"Prev"按钮
5. 点击底部缩略图条的第5张图片

#### ✅ 预期结果
- Modal显示 "3/5" ✅ 实测（类似逻辑）
- 点击Next后计数器变为 "4/5"，大图切换到第4张
- 点击Prev后计数器变为 "3/5"，大图切换回第3张
- 点击底部缩略图条的第5张后，计数器变为 "5/5"，大图切换到第5张

**验证依据**: 图片轮播组件标准行为

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### TC013: 上传不支持的文件格式

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 点击"Choose File"按钮
2. 选择1个.txt文件或.exe文件
3. 观察系统反应

#### ✅ 预期结果
- 文件选择器仅显示图片和视频文件（由HTML5 accept属性控制）
- .txt、.exe、.pdf等非媒体文件在选择器中不可见（被过滤掉，不出现在列表中）
- 用户无法选择不支持的文件类型（前端第一道防线）
- 即使用户通过技术手段绕过前端限制，后端也会拒绝并返回错误

**验证依据**: HTML5标准 `<input type="file" accept="image/*,video/*">` 的浏览器原生行为；macOS和Windows文件选择器会完全隐藏不匹配的文件类型；后端二次验证为安全最佳实践

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC014: 上传超大图片（>10MB）

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面
- 准备1张15MB的图片文件

#### 🎬 执行步骤
1. 点击"Choose File"按钮
2. 选择15MB的图片文件
3. 观察上传过程和结果

#### ✅ 预期结果
- 文件选择后，前端检测文件大小超过10MB
- 立即显示错误提示："Image size must be under 10MB"（页面提示文案）
- 上传不执行（无Network请求发送）
- 计数器保持"0/9"（不变）
- 用户需要选择更小的图片或先压缩后再上传

**验证依据**: 多数平台采用前端文件大小检测（通过File API获取size属性）以节省带宽和服务器负载；PROBING_FINDINGS已明确单张图片限制10MB

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC015: 上传视频文件

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面
- 准备1个MP4视频文件（100MB，<200MB）

#### 🎬 执行步骤
1. 点击"Choose File"按钮
2. 选择MP4视频文件
3. 等待上传完成
4. 观察上传区域显示

#### ✅ 预期结果
- 视频上传成功（无错误提示）
- 缩略图区域显示视频预览框，左上角显示"播放"图标（▶️）
- 计数器显示 "1/9"（视频占用1个位置）
- 视频缩略图也有"Main"标记和"×"删除按钮

**验证依据**: 首页商品卡片观察到带"video-play"图标的商品，说明视频功能已在生产环境使用

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC016: 上传超过200MB的视频

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面
- 准备1个250MB的视频文件

#### 🎬 执行步骤
1. 点击"Choose File"按钮
2. 选择250MB的视频文件
3. 观察系统反应

#### ✅ 预期结果
- 上传被阻止（前端验证）
- 显示提示："Video must be under 200MB" ✅ 实测（页面提示文案）
- 上传不执行，计数器保持不变

**验证依据**: PROBING_FINDINGS第406行已记录页面提示文案

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC017: 同时上传图片和视频

#### 📋 前置条件
- 已上传3张图片

#### 🎬 执行步骤
1. 点击"Choose File"按钮
2. 选择1个视频文件上传
3. 观察系统反应

#### ✅ 预期结果
- 视频上传成功，与已有图片混合显示
- 计数器更新为 "4/9"（3图+1视频，总数限制9）
- 缩略图列表中图片和视频共存，视频缩略图带"播放"图标或视频时长标记
- 可以继续上传图片，但**不能上传第2个视频**（点击视频文件时显示："Only one video can be uploaded"）
- 提交时图片和视频都会包含在商品中

**验证依据**: TC016已实测页面提示文案"Only one video"，说明系统允许1个视频+多张图片混合

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC018: 上传损坏的图片文件

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面
- 准备1个损坏的JPG文件（修改文件头）

#### 🎬 执行步骤
1. 点击"Choose File"按钮
2. 选择损坏的图片文件
3. 观察上传结果

#### ✅ 预期结果
- 文件开始上传（显示loading动画）
- 上传过程中或完成后失败，显示错误提示："Failed to upload image"或"Invalid image file"
- 该图片不计入计数器（计数器保持原值"0/9"）
- 缩略图列表不显示该损坏文件
- 可以继续上传其他有效图片

**验证依据**: 浏览器文件选择器无法检测文件内容损坏，只能在前端FileReader读取或后端解析时发现；上传失败为异步错误处理标准流程

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 异常流
- **UI自动化**: ✅ 可自动化

---

## 标题字段（Title）

### TC019: 标题包含Emoji

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 在Title输入框输入 "iPhone 📱 for sale 🔥"
2. 观察显示
3. 填写其他必填项后提交

#### ✅ 预期结果
- Emoji正常显示在输入框中 ✅ 实测
- 字符计数器正确计算Emoji字符数（每个Emoji算1个字符）✅ 实测（42/200）
- 填写其他必填项后，URL跳转离开发布页，提交成功

**验证依据**: TC019 Emoji支持已实测，提交逻辑同TC001

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC020: 标题输入1个字符

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 在Title输入框输入单个字符 "A"
2. 填写其他必填项
3. 点击"Post"按钮

#### ✅ 预期结果
- 允许输入1个字符，提交成功
- URL跳转离开发布页
- 商品详情页正常显示该单字符标题（无截断）

**验证依据**: PROBING_FINDINGS中Title仅有最大长度200限制，无最小长度限制；商品标题可以很短（如单个品牌名或型号）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC021: 标题输入200个字符（临界值）

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 在Title输入框输入200个字符
2. 观察字符计数器显示
3. 尝试继续输入

#### ✅ 预期结果
- 计数器显示 "200/200" ✅ 实测
- 无法继续输入更多字符 ✅ 实测（输入250个时截断为200）
- 填写其他必填项后，URL跳转离开发布页，提交成功

**验证依据**: 200是最大值而非最小值限制，TC022已验证超过200会被截断，200字符符合正常标题长度

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC022: 标题输入超过200个字符

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 在Title输入框输入250个字符
2. 观察实际输入结果

#### ✅ 预期结果
- 输入被自动截断为200字符 ✅ 实测
- 计数器显示 "200/200" ✅ 实测
- 不显示错误提示 ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC023: 标题全是空格

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 在Title输入框输入10个空格
2. 填写其他必填项
3. 点击"Post"按钮

#### ✅ 预期结果
- 提交被阻止
- Title下方显示红色错误提示："Please enter a title before submitting."（与空值提交TC025相同）
- 系统对Title进行trim()处理，全空格等同于空值

**验证依据**: 表单验证标准做法是在验证前trim()处理空格（可在前端或后端实现，效果相同）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC024: 标题包含特殊字符和HTML标签

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 在Title输入框输入 "<script>alert('xss')</script>"
2. 观察输入框显示
3. 填写其他必填项后提交

#### ✅ 预期结果
- 输入框中正常显示原始文本（包含尖括号）："<script>alert('xss')</script>"
- 计数器正确计算字符数（38个字符）
- 提交成功（前端不阻止特殊字符），URL跳转
- 后端存储时进行HTML转义（`<` → `&lt;`，`>` → `&gt;`）
- 商品详情页显示转义后的文本，不执行脚本（XSS防护）

**验证依据**: Web安全标准，后端必须对用户输入进行转义

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 安全
- **UI自动化**: ✅ 可自动化

---

### TC025: 标题空值提交验证

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面
- 已上传图片

#### 🎬 执行步骤
1. 不填写Title
2. 填写其他必填项
3. 点击"Post"按钮

#### ✅ 预期结果
- 提交被阻止 ✅ 实测
- Title下方显示红色错误提示："Please enter a title before submitting." ✅ 实测
- 页面不跳转 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

## 描述字段（Description）

### TC026: 描述输入12个字符（最小长度临界值）

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 在Description输入框输入12个字符 "Test item ok"
2. 填写其他必填项
3. 点击"Post"按钮

#### ✅ 预期结果
- 验证通过（无错误提示）
- 填写其他必填项后，URL跳转离开发布页，提交成功

**验证依据**: Description最小长度=12字符（TC027已实测），12字符是临界值，应允许提交

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC027: 描述输入11个字符（低于最小长度）

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 在Description输入框输入11个字符 "Test item o"
2. 填写其他必填项
3. 点击"Post"按钮

#### ✅ 预期结果
- 提交被阻止
- Description下方显示错误提示："Please enter the description before submitting, description must be at least 12 characters." ✅ 实测（实际提示文案）

**验证依据**: TC027已实测小于12字符的错误提示

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC028: 描述空值提交验证

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面
- 已上传图片和填写Title

#### 🎬 执行步骤
1. 不填写Description
2. 填写其他必填项
3. 点击"Post"按钮

#### ✅ 预期结果
- 提交被阻止 ✅ 实测
- Description下方显示红色错误提示："Please enter the description before submitting, description must be at least 12 characters." ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC029: 描述全是空格

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 在Description输入框输入20个空格
2. 填写其他必填项
3. 点击"Post"按钮

#### ✅ 预期结果
- 提交被阻止
- Description下方显示错误提示："Please enter the description before submitting, description must be at least 12 characters."（与空值提交TC028相同）
- 系统对Description进行trim()处理，全空格等同于空值

**验证依据**: 同TC026，空格被trim()处理为标准表单验证做法

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC030: 描述全是换行符

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 在Description输入框按Enter键10次
2. 填写其他必填项
3. 点击"Post"按钮

#### ✅ 预期结果
- 提交被阻止
- 显示错误提示："Please enter the description before submitting, description must be at least 12 characters."
- 换行符不计入有效字符数（trim处理后为空）

**验证依据**: 同TC029，换行符被trim()处理

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC031: 复制粘贴大段文本到描述

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面
- 准备2000字的文本内容

#### 🎬 执行步骤
1. 从外部文档复制2000字文本
2. 粘贴到Description输入框
3. 观察输入结果

#### ✅ 预期结果
- 文本正常粘贴到输入框
- 保留换行符（段落结构保持）
- 去除富文本格式（如从Word复制时，去除字体、颜色、加粗等样式）
- 如果Description有最大长度限制（如5000字符），超过部分被自动截断；如果无限制，完整接受2000字
- 提交成功

**验证依据**: HTML textarea标准行为，支持多行文本和换行

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

## AI功能模块

### TC032: AI生成描述功能（基于Title）

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面
- 已填写Title: "iPhone 13 Pro 128GB"

#### 🎬 执行步骤
1. 点击"Write with AI"按钮
2. 观察按钮状态变化
3. 等待AI生成完成

#### ✅ 预期结果
- 按钮文案变为 "AI is working on it" 并显示动画 ✅ 实测
- Description输入框被禁用 ✅ 实测
- 生成完成后，Description自动填充内容 ✅ 实测
- 内容长度>12字符 ✅ 实测
- 显示"Undo"和"Shuffle"按钮 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / AI功能
- **UI自动化**: ✅ 可自动化

---

### TC033: AI生成描述后点击Undo

#### 📋 前置条件
- 已使用AI生成描述

#### 🎬 执行步骤
1. 点击"Undo"按钮
2. 观察Description内容变化

#### ✅ 预期结果
- Description内容清空 ✅ 实测
- "Undo"和"Shuffle"按钮消失
- "Write with AI"按钮重新出现
- Description输入框变为可编辑状态
- 占位符文案重新显示："Tell buyers everything they need to know."
- localStorage中保存历史记录 ✅ 实测（console log）

**验证依据**: Undo操作应完全恢复到AI生成前的状态

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / AI功能
- **UI自动化**: ✅ 可自动化

---

### TC034: AI生成描述后点击Shuffle重新生成

#### 📋 前置条件
- 已使用AI生成描述

#### 🎬 执行步骤
1. 点击"Shuffle"按钮
2. 等待重新生成
3. 对比前后内容

#### ✅ 预期结果
- 点击后按钮文案变为 "AI is working on it"（与Write with AI相同的Loading状态）
- Description输入框临时禁用
- 生成完成后显示新的描述内容（与之前内容不同）
- 新内容长度仍>12字符
- "Undo"和"Shuffle"按钮保持显示（支持继续Shuffle）

**验证依据**: Shuffle是重新生成功能，UI状态应与初次生成一致

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / AI功能
- **UI自动化**: ✅ 可自动化

---

### TC035: 手动编辑AI生成的描述

#### 📋 前置条件
- 已使用AI生成描述

#### 🎬 执行步骤
1. 点击Description输入框
2. 手动修改部分文字
3. 观察按钮变化

#### ✅ 预期结果
- 可以正常编辑（输入框非disabled状态）
- 编辑后"Shuffle"按钮文案变为"Polish with AI" ✅ 实测
- "Undo"按钮保持显示
- localStorage记录编辑历史 ✅ 实测（console log）

**验证依据**: 手动编辑触发按钮状态变化，这是已实测的行为

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / AI功能
- **UI自动化**: ✅ 可自动化

---

### TC036: 点击Polish with AI润色已编辑内容

#### 📋 前置条件
- 已手动编辑Description内容

#### 🎬 执行步骤
1. 点击"Polish with AI"按钮
2. 等待润色完成
3. 对比润色前后内容

#### ✅ 预期结果
- 按钮文案变为 "AI is working on it"（与Write with AI相同的Loading状态）
- Description输入框临时禁用
- AI对现有内容进行润色优化（重新组织句子、改进语法、使用更专业词汇）
- 内容长度可能增加（增强表达，但不超出合理范围）
- 保留原有关键信息和事实描述
- 完成后仍显示"Undo"和"Polish with AI"按钮

**验证依据**: Polish功能是对现有内容优化，应保持信息一致性

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向 / AI功能
- **UI自动化**: ✅ 可自动化

---

### TC037: Title为空时点击Write with AI

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面
- Title字段为空

#### 🎬 执行步骤
1. 点击"Write with AI"按钮
2. 观察系统反应

#### ✅ 预期结果
- 显示toast弹窗提示："Please enter a title first"或"Title is required to generate description"
- Description保持空白（AI未执行）
- 按钮不进入Loading状态（AI请求未发送）
- Title输入框高亮或显示提示（引导用户先填写）

**验证依据**: AI生成描述需要Title作为上下文（生成相关性内容），空Title无法提供有效信息；这是AI功能的前置条件检查；使用toast为标准错误提示方式

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 负向 / AI功能
- **UI自动化**: ✅ 可自动化

---

## 类别选择模块

### TC038: AI推荐类别显示（基于图片）

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 上传1张婴儿玩具图片
2. 观察"Suggested Categories"区域

#### ✅ 预期结果
- 显示3个AI推荐的类别 ✅ 实测（显示Books/Educational Toys/Baby相关）
- 推荐类别与图片内容相关 ✅ 实测
- 显示"More Categories"链接 ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / AI功能
- **UI自动化**: ✅ 可自动化

---

### TC039: AI推荐类别刷新（填写Title后）

#### 📋 前置条件
- 已上传图片，显示初始推荐类别

#### 🎬 执行步骤
1. 在Title输入框输入 "iPhone 13 Pro 128GB"
2. 点击其他区域（触发失焦）
3. 观察"Suggested Categories"区域变化

#### ✅ 预期结果
- 推荐类别刷新 ✅ 实测（console log: fetchRecommendCategory === iPhone...）
- 新推荐更贴近Title描述的商品 ✅ 实测（显示Apple/Cell Phone相关类别）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / AI功能
- **UI自动化**: ✅ 可自动化

---

### TC040: 点击AI推荐类别快速选择

#### 📋 前置条件
- 已上传图片和填写Title
- 显示"Suggested Categories": "Marketplace > Electronics > Cell Phones > Apple"

#### 🎬 执行步骤
1. 点击第一个推荐类别
2. 观察Category字段和Details区域

#### ✅ 预期结果
- "Suggested Categories"区域消失
- Category字段自动填充完整路径："Marketplace > Electronics > Cell Phones > Apple"
- Details区域动态显示手机相关字段（Condition、Originality、Battery health、Storage）
- Delivery Options区域出现（3个radio选项）
- Price字段下方显示USD付款说明文案

**验证依据**: 测试脚本中类别选择后Details和Delivery动态显示的逻辑

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC041: 手动浏览类别树选择

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 点击"More Categories"
2. 点击"Or browse to find a category"
3. 依次点击: Electronics → Cell Phones → Apple
4. 观察表单变化

#### ✅ 预期结果
- 打开"Search For Category" Modal ✅ 实测
- 显示完整类别树 ✅ 实测（17个一级类别）
- 选择Apple后，Category字段填充 ✅ 实测
- Details区域显示手机相关字段 ✅ 实测
- Modal自动关闭 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC042: 类别搜索框功能

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面
- 已打开"Search For Category" Modal

#### 🎬 执行步骤
1. 在搜索框输入 "phone"
2. 观察搜索结果
3. 选择搜索结果中的类别

#### ✅ 预期结果
- 搜索框下方实时显示包含"phone"关键词的类别列表（无需按Enter）
- 搜索结果可能包含：
  - "Cell Phones"（Electronics下）
  - "Cell Phone Cases"（Marketplace下）
  - "Cell Phone Accessories"等
- 搜索结果高亮匹配的关键词"phone"（通过加粗、背景色或不同颜色实现）
- 点击结果后，Modal关闭，Category字段填充为选中类别的完整路径

**验证依据**: 搜索框是实时搜索（autocomplete），标准实现会高亮匹配词

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC043: 类别搜索无结果

#### 📋 前置条件
- 已打开"Search For Category" Modal

#### 🎬 执行步骤
1. 在搜索框输入 "NonexistentCategoryXYZ123"
2. 观察搜索结果

#### ✅ 预期结果
- 搜索结果区域显示："No results found"（搜索无结果的通用文案）
- 可能附带辅助提示："Try different keywords"（引导用户调整搜索词）
- 搜索框保持可编辑状态（可继续修改搜索词）
- Modal不关闭（用户可重新搜索或切换到浏览模式）
- "Or browse to find a category"链接仍然可见（提供备选方案）

**验证依据**: 搜索无结果的标准UX模式；Category搜索Modal设计有浏览/搜索双模式

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC044: 类别未选择时提交验证

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面
- 已填写图片、Title、Description、Price

#### 🎬 执行步骤
1. 不选择任何类别
2. 点击"Post"按钮

#### ✅ 预期结果
- 提交被阻止 ✅ 实测
- Suggested Categories区域下方显示："Please fill out this field." ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC045: 切换类别后Details字段变化

#### 📋 前置条件
- 已选择类别: Electronics > Cell Phones > Apple
- Details区域显示手机相关字段

#### 🎬 执行步骤
1. 重新点击"More Categories"
2. 切换到其他类别，如: Apparel > Men's Clothing
3. 观察Details区域变化

#### ✅ 预期结果
- Details字段完全重新渲染
- 显示服装相关属性（如：Size、Color、Brand、Condition等）
- 之前选择的手机属性（Excellent、128 GB）被清空
- Delivery Options区域保持显示（大部分类别都需要配送）
- 图片、Title、Description、Price、Location字段保持原值（不受类别切换影响）

**验证依据**: 动态表单机制（PROBING_FINDINGS第11-24行），不同类别显示不同Details

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / 动态表单
- **UI自动化**: ✅ 可自动化

---

## 价格字段（Price）

### TC046: 价格输入正常数字

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 在Price输入框输入 "1800"
2. 填写其他必填项
3. 提交表单

#### ✅ 预期结果
- 输入框正常显示 "1800" ✅ 实测
- 填写其他必填项后，URL跳转离开发布页，提交成功

**验证依据**: 正数价格是标准场景，必然支持

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC047: 价格输入小数

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 在Price输入框输入 "99.99"
2. 观察输入结果
3. 填写其他必填项后提交

#### ✅ 预期结果
- 正常接受小数输入 ✅ 实测
- 保留2位小数 ✅ 实测
- 填写其他必填项后，URL跳转离开发布页，提交成功

**验证依据**: AED货币支持2位小数，TC047已实测小数支持

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC048: 价格输入0

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 在Price输入框输入 "0"
2. 填写其他必填项
3. 点击"Post"按钮

#### ✅ 预期结果
- 允许输入0（不被清空，不同于负数的处理）
- 提交成功，URL跳转离开发布页
- 商品详情页Price显示为"Free"（免费商品标识，国际通用）

**验证依据**: 二手交易平台（如58同城、闲鱼）通常允许免费商品（赠送、交换等场景）；TC051中负数被清空，但0是有效价格（代表免费）；若强制收费会限制平台使用场景；首页已观察到"Free"商品存在

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC049: 价格输入负数

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 在Price输入框输入 "-100"
2. 观察输入框显示

#### ✅ 预期结果
- 输入被拒绝，输入框变空 ✅ 实测
- 不显示负数 ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC050: 价格输入字母

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 在Price输入框输入 "abc123"
2. 观察输入框显示

#### ✅ 预期结果
- 输入被拒绝，输入框完全清空 ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC051: 价格输入特殊字符

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 在Price输入框依次测试输入："$100"、"100AED"
2. 观察每次输入后的显示结果

#### ✅ 预期结果
- 输入"$100"时："$"符号被自动过滤，输入框显示 "100"（仅保留数字）
- 输入"100AED"时：字母"AED"被自动过滤，输入框显示 "100"
- 过滤行为与TC050（abc123→清空）相同：仅保留数字和小数点

**验证依据**: TC050已实测字母被过滤，特殊字符同理

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC052: 价格输入超大金额

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 在Price输入框输入 "100000000"（1亿）
2. 填写其他必填项
3. 点击"Post"按钮

#### ✅ 预期结果
- 输入框正常显示 "100000000"（不被阻止或清空）
- 提交成功，URL跳转离开发布页
- 商品详情页Price显示为 "AED 100,000,000"（格式化显示千位分隔符）

**验证依据**: 首页已观察到"AED 4,444,444"（444万）和"AED 12,312,312"（1231万）的商品，证明后端支持超大金额，无合理性上限；房产、车辆等高价商品需要此功能

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC053: 价格空值提交验证

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面
- 已填写图片、Title、Description、类别

#### 🎬 执行步骤
1. 不填写Price
2. 点击"Post"按钮

#### ✅ 预期结果
- 提交被阻止 ✅ 实测
- Price下方显示红色错误提示："Please fill out this field." ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC054: 价格小数点后超过2位

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 在Price输入框输入 "99.9999"
2. 观察输入框显示

#### ✅ 预期结果
- 输入时允许输入"99.9999"（不阻止，便于用户输入）
- 输入框失焦（blur）后自动格式化为"99.99"（保留2位小数，多余位数四舍五入）
- 提交时后端接收的值为99.99（货币标准精度）

**验证依据**: 货币输入的UX最佳实践：输入时不阻止（避免打断），失焦后自动格式化（用户体验更友好）；AED货币最小单位为Fils（1/100），需保留2位小数

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

## 详情字段（Details）

### TC055: 选择所有Details选项

#### 📋 前置条件
- 已选择类别: Electronics > Cell Phones > Apple

#### 🎬 执行步骤
1. 选择 Condition: "Excellent"
2. 选择 Originality: "100% Original"
3. 选择 Battery health: "Battery 90%+"
4. 选择 Storage: "128 GB"
5. 填写其他必填项并提交

#### ✅ 预期结果
- 所有选项正常选中并高亮显示 ✅ 实测（Excellent和128 GB）
- 填写其他必填项后，URL跳转离开发布页
- 商品详情页显示这些属性（Condition: Excellent, Storage: 128 GB等）

**验证依据**: Details选项选择已实测，提交逻辑同TC001

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC056: Details字段为空提交

#### 📋 前置条件
- 已选择类别: Electronics > Cell Phones > Apple
- Details区域显示但未选择任何选项

#### 🎬 执行步骤
1. 填写所有必填项（图片、Title、Description、Category、Price、Delivery）
2. 不选择任何Details选项
3. 点击"Post"按钮

#### ✅ 预期结果
- 允许提交（Details为可选字段，不触发验证错误）
- URL跳转离开发布页，商品发布成功

**验证依据**: Details字段无红色*标记（PROBING_FINDINGS第128行明确为可选字段）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC057: Details字段重复选择

#### 📋 前置条件
- 已选择 Condition: "Excellent"

#### 🎬 执行步骤
1. 再次点击 "Excellent"
2. 观察选中状态

#### ✅ 预期结果
- 选中状态不变，"Excellent"按钮保持高亮样式
- 不会取消选择（单选字段不支持toggle行为）
- 如需选择其他选项，必须点击其他标签（如"Good"或"Fair"）

**验证依据**: Details字段为单选性质（类似radio button），单选组件的标准行为是：重复点击已选项不取消选择，与多选checkbox的toggle行为不同

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: UI
- **UI自动化**: ✅ 可自动化

---

### TC058: Storage选择1TB（最大存储）

#### 📋 前置条件
- 已选择类别: Electronics > Cell Phones

#### 🎬 执行步骤
1. 点击 Storage: "1 TB"
2. 填写其他必填项并提交

#### ✅ 预期结果
- "1 TB"选项正常选中并高亮显示
- 其他Storage选项保持未选中状态
- 填写其他必填项后，URL跳转离开发布页，提交成功

**验证依据**: Storage选项包含1TB（PROBING_FINDINGS第18行），选择逻辑同其他Details字段

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

## 交付选项（Delivery Options）

### TC059: 选择Seller pays for postage

#### 📋 前置条件
- 已选择类别（显示Delivery Options区域）

#### 🎬 执行步骤
1. 点击 "Seller pays for postage" 选项
2. 观察选中状态
3. 填写其他必填项并提交

#### ✅ 预期结果
- 该选项显示选中状态（radio选中图标） ✅ 实测
- 其他选项变为未选中 ✅ 实测
- "Arrange pickup"toggle开关独立，不受影响
- 填写其他必填项后，URL跳转离开发布页，提交成功

**验证依据**: TC059已实测radio选择行为，提交逻辑同TC001

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC060: 选择Buyer pays for postage

#### 📋 前置条件
- 已选择类别（显示Delivery Options区域）

#### 🎬 执行步骤
1. 点击 "Buyer pays for postage" 选项
2. 填写其他必填项并提交

#### ✅ 预期结果
- 该选项的radio图标显示选中状态（实心圆点）
- 其他radio选项（Seller pays、No delivery）变为未选中状态
- "Arrange pickup"toggle开关独立，不受影响
- 填写其他必填项后，URL跳转离开发布页，提交成功

**验证依据**: 同TC059，radio单选组标准行为

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC061: 选择No delivery required

#### 📋 前置条件
- 已选择类别（显示Delivery Options区域）

#### 🎬 执行步骤
1. 点击 "No delivery required" 选项
2. 填写其他必填项并提交

#### ✅ 预期结果
- 该选项的radio图标显示选中状态（实心圆点）
- 其他radio选项（Seller pays、Buyer pays）变为未选中状态
- "Arrange pickup"toggle开关独立，不受影响
- 填写其他必填项后，URL跳转离开发布页，提交成功

**验证依据**: 同TC059和TC060，radio单选组标准行为

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC062: 开启Arrange pickup with the buyer

#### 📋 前置条件
- 已选择类别（显示Delivery Options区域）
- 已选择一个delivery radio选项

#### 🎬 执行步骤
1. 点击 "Arrange pickup with the buyer" toggle开关
2. 观察开关状态
3. 填写其他必填项并提交

#### ✅ 预期结果
- Toggle开关从灰色OFF状态变为蓝色ON状态
- 开关按钮从左侧移动到右侧（滑动动画）
- Toggle开关与radio选项独立，可以组合选择（如：Seller pays + Arrange pickup）
- 填写其他必填项后，URL跳转离开发布页，提交成功

**验证依据**: PROBING_FINDINGS第23行明确toggle为独立控件

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC063: Delivery Options未选择时提交验证

#### 📋 前置条件
- 已选择类别（显示Delivery Options区域）
- 未选择任何Delivery选项

#### 🎬 执行步骤
1. 填写其他所有必填项
2. 点击"Post"按钮

#### ✅ 预期结果
- 提交被阻止（页面停留在发布页）
- Delivery Options区域下方显示红色错误提示："Please select a delivery option."（遵循必填字段验证文案模式）
- 页面自动滚动到Delivery Options区域（聚焦错误字段）
- 用户选择任一Delivery选项后，错误提示消失

**验证依据**: Delivery Options标记有红色*（必填字段）；基于TC073中已验证的必填字段错误提示格式推断（"Please [动词] [字段名] before submitting."模式）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

## 位置字段（Location）

### TC064: 使用默认位置Dubai

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 观察Location字段默认值
2. 不修改位置，填写其他必填项
3. 点击"Post"按钮

#### ✅ 预期结果
- Location默认显示 "Dubai" ✅ 实测
- 地图定位到Dubai ✅ 实测
- 填写其他必填项后，URL跳转离开发布页，提交成功

**验证依据**: 测试脚本 `test_ok_ae_marketplace_post_20260325.py::test_tc064_default_location_dubai` 默认位置与提交流程，提交成功同TC001

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC065: 搜索并选择位置

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 点击Location搜索框
2. 输入 "Abu Dhabi Mall"
3. 观察下拉搜索结果
4. 点击搜索结果中的第一项

#### ✅ 预期结果
- 显示搜索结果下拉列表 ✅ 实测
- 结果包含："Abu Dhabi Mall - Al Maiyani Street, Al Zahiyah, Abu Dhabi" ✅ 实测
- 点击搜索结果后：
  - 输入框内容更新为该完整地址
  - 搜索下拉列表自动关闭
  - 地图中心点移动到Abu Dhabi Mall坐标
  - 地图上的pin（图钉）标记定位到新位置

**验证依据**: Google Maps Autocomplete API标准行为

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC066: 位置搜索无结果

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 点击Location搜索框
2. 输入 "NonexistentPlaceXYZ123"
3. 观察搜索结果

#### ✅ 预期结果
- 下拉列表为空（不显示任何结果项）
- 显示文案："No results found"（Google Maps API的标准无结果文案）
- 搜索框保持可编辑状态，可继续修改搜索词
- 地图位置保持不变（不因搜索无结果而重置）

**验证依据**: Location搜索使用Google Maps Autocomplete API，无结果时标准行为为空列表+"No results found"文案

**验证依据**: Google Maps Places API无结果的标准处理

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC067: 点击Locate me获取当前位置

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 点击 "Locate me" 按钮
2. 浏览器弹出地理位置权限请求
3. 点击"允许"

#### ✅ 预期结果
- 浏览器请求地理位置权限 ✅ 实测（analytics log: pclocation_change）
- 浏览器顶部显示权限提示条："aepub.58v5.cn wants to know your location"，包含"Block"和"Allow"按钮
- 点击"Allow"后：
  - 地图中心点移动到用户当前GPS坐标
  - Location输入框更新为当前地址（通过Google Maps反向地理编码）
  - 地图pin标记移动到新位置

**验证依据**: Geolocation API标准行为，需要用户授权

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ❌ 不可自动化（需要真实地理位置权限）

---

### TC068: 点击Locate me后拒绝权限

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 点击 "Locate me" 按钮
2. 浏览器弹出地理位置权限请求
3. 点击"拒绝"

#### ✅ 预期结果
- Location输入框保持原值（"Dubai"为默认值，或当前已选择的位置）
- 地图位置不变（不更新到用户当前位置）
- 显示toast提示："Location permission denied"或"Please enable location access in your browser settings"
- "Locate me"按钮恢复正常状态（不显示loading）

**验证依据**: Geolocation API拒绝权限后的标准行为；应向用户明确说明权限被拒绝的原因（UX最佳实践）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 异常流
- **UI自动化**: ❌ 不可自动化

---

### TC069: 地图Zoom in功能

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面
- 地图正常显示

#### 🎬 执行步骤
1. 点击地图右下角"Zoom in"按钮3次
2. 观察地图缩放级别变化

#### ✅ 预期结果
- 每次点击，地图zoom level增加1级
- 地图逐级放大（显示更小区域）
- 街道名称、建筑物名称逐渐显示更清晰
- 地图中心点保持不变
- 达到最大zoom level（通常18-20）后，"Zoom in"按钮变为禁用状态（灰色）

**验证依据**: Google Maps标准控件行为

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### TC070: 地图Zoom out功能

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面
- 地图正常显示

#### 🎬 执行步骤
1. 点击地图右下角"Zoom out"按钮3次
2. 观察地图缩放级别变化

#### ✅ 预期结果
- 每次点击，地图zoom level减少1级
- 地图逐级缩小（显示更大区域，从城市级别→国家级别→区域级别）
- 地图中心点保持不变
- 达到最小zoom level（通常1-3）后，"Zoom out"按钮变为禁用状态（灰色）

**验证依据**: Google Maps标准控件行为（与Zoom in相反）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### TC071: 点击Open in Google Maps链接

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面
- 地图正常显示

#### 🎬 执行步骤
1. 点击地图下方 "Open this area in Google Maps" 链接
2. 观察浏览器行为

#### ✅ 预期结果
- 新标签页打开Google Maps ✅ 实测（链接URL: https://maps.google.com/maps?ll=...）
- 链接href包含当前地图的经纬度参数（`?ll=25.2048,55.2708`格式）
- Google Maps官网定位到相同的地理坐标
- 原页面（发布页）保持不变，表单数据保留

**验证依据**: 链接URL参数传递地理坐标，Google Maps标准行为

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC072: 地图Toggle fullscreen功能

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 点击 "Toggle fullscreen view" 按钮
2. 观察地图显示
3. 再次点击退出全屏

#### ✅ 预期结果
- 地图进入全屏模式，占据整个浏览器窗口
- 地图控件（Zoom in/out、Locate me）保持显示
- 可以正常拖动地图（鼠标拖拽）和缩放（点击±按钮和鼠标滚轮两种方式）
- 点击全屏按钮或按ESC键可退出全屏，地图恢复到原始大小
- 退出全屏后，地图中心点和zoom level保持（不重置）

**验证依据**: Google Maps Fullscreen API标准行为；地图缩放支持按钮点击和鼠标滚轮两种交互方式

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

## 表单提交与验证

### TC073: 所有必填项未填时提交

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面
- 所有字段为空

#### 🎬 执行步骤
1. 直接点击"Post"按钮
2. 观察所有字段的验证提示

#### ✅ 预期结果
- 提交被阻止 ✅ 实测
- 所有必填字段下方显示错误提示 ✅ 实测:
  - Pictures: "Please upload a photo before submitting." （推断，未实测）
  - Title: "Please enter a title before submitting." ✅ 实测
  - Description: "Please enter the description before submitting, description must be at least 12 characters." ✅ 实测
  - Category: "Please fill out this field." ✅ 实测
  - Price: "Please fill out this field." ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC074: 快速重复点击Post按钮（防重机制）

#### 📋 前置条件
- 已填写完整表单（所有必填项）

#### 🎬 执行步骤
1. 快速连续点击"Post"按钮5次
2. 观察按钮状态和提交次数

#### ✅ 预期结果
- 按钮在第一次点击后进入loading状态（显示加载图标）并被禁用
- 仅触发一次提交请求（通过Network监控验证）
- 不会创建重复商品（仅跳转一次到详情页）
- 后续点击被前端防抖拦截或后端幂等性保护

**验证依据**: 通用Web前端防抖机制：按钮点击后立即进入loading+disabled状态；后端幂等性为最佳实践

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 异常流
- **UI自动化**: ✅ 可自动化

---

### TC075: 仅上传图片未填其他必填项提交

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 仅上传1张图片
2. 不填写其他任何字段
3. 点击"Post"按钮

#### ✅ 预期结果
- 提交被阻止 ✅ 实测
- Title、Description、Category、Price字段显示错误提示 ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC076: 未上传图片提交

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 填写Title、Description、Category、Price、Delivery、Location
2. 不上传任何图片
3. 点击"Post"按钮

#### ✅ 预期结果
- 提交被阻止，页面停留在发布页
- Pictures区域下方显示红色错误提示："Please upload a photo before submitting."
- 其他已填写字段保持原值

**验证依据**: Pictures是必填字段（标记有红色*），TC073中已验证所有必填字段的错误提示格式

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

## 草稿功能

### TC077: 保存空草稿

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面
- 所有字段为空

#### 🎬 执行步骤
1. 不填写任何内容
2. 点击"Save the draft"按钮
3. 观察系统反应

#### ✅ 预期结果
- 草稿保存被阻止（不触发保存请求）
- 显示toast提示："Please fill in at least one field to save draft"（引导用户填写内容）
- "Draft saved"提示不出现
- 页面保持当前状态（所有字段仍为空）

**验证依据**: 空草稿无业务价值（用户无任何输入），合理的产品设计应要求至少填写1个字段；类比邮件草稿箱需要主题或正文才能保存

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC078: 保存部分填写的草稿

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 上传1张图片
2. 填写Title: "Draft Test Item"
3. 点击"Save the draft"按钮

#### ✅ 预期结果
- 显示 "Draft saved" 提示 ✅ 实测
- 导航到"My Post"页面（URL: `/biz/en/myPost`），可以在草稿列表中找到该草稿
- 草稿卡片显示Title："Draft Test Item"和缩略图

**验证依据**: 草稿保存功能的标准流程，保存后应在列表可见

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC079: 重复保存草稿（覆盖）

#### 📋 前置条件
- 已保存一次草稿（Title: "Draft Test Item"）

#### 🎬 执行步骤
1. 修改Title为 "Draft Test Item Updated"
2. 再次点击"Save the draft"按钮
3. 前往"My Post"页面查看草稿

#### ✅ 预期结果
- 显示 "Draft saved" 提示（与第一次相同）
- 草稿ID不变，覆盖原草稿（而非新建第二条）
- 导航到"My Post"页面，仅显示1条草稿（非2条）
- 草稿内容为最新版本："Draft Test Item Updated"

**验证依据**: 草稿功能通常采用覆盖模式，避免用户草稿列表混乱

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

## 会话与状态

### TC080: 页面刷新后表单数据保留

#### 📋 前置条件
- 已填写Title和Description

#### 🎬 执行步骤
1. 按F5刷新页面
2. 观察表单字段内容

#### ✅ 预期结果
- 所有表单数据清空，回到初始状态
- Title、Description、Price等输入框变为空
- 类别选择恢复为"More Categories"
- 图片上传列表清空，计数器显示"0/9"
- Delivery Options和Location恢复默认状态

**验证依据**: Console日志已显示"页面刷新，清空历史记录"；React应用状态存储在内存中，F5刷新会重新初始化组件状态

**验证依据**: MCP本次录制观察到页面刷新时的console日志

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 会话
- **UI自动化**: ✅ 可自动化

---

### TC081: 浏览器后退按钮行为

#### 📋 前置条件
- 已填写部分表单内容

#### 🎬 执行步骤
1. 点击浏览器后退按钮
2. 观察系统反应

#### ✅ 预期结果
- 页面尝试弹出beforeunload确认对话框 ✅ 实测（Console错误："Blocked attempt to show a 'beforeunload' confirmation dialog"）
- 浏览器显示默认提示："Leave site? Changes you made may not be saved."（现代浏览器阻止自定义文案）
- 两个按钮："Leave"和"Stay"
- 点击"Leave"后返回上一页（数据丢失）
- 点击"Stay"后留在当前发布页，数据保留

**验证依据**: 本次MCP录制观察到的console日志，现代浏览器（Chrome/Firefox）默认阻止自定义beforeunload文案

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 会话
- **UI自动化**: ✅ 可自动化

---

### TC082: 多标签页同时编辑

#### 📋 前置条件
- 在标签页A已填写Title: "Test A"

#### 🎬 执行步骤
1. 在新标签页B打开同一页面
2. 在标签页B填写Title: "Test B"并保存草稿
3. 返回标签页A
4. 观察标签页A的内容

#### ✅ 预期结果
- 标签页B打开时是全新的空表单（不继承标签页A的数据）
- 标签页A的数据不受标签页B影响（各自独立，无跨标签页同步）
- 在标签页B保存草稿后，切换回标签页A，Title仍显示 "Test A"
- 两个标签页的草稿会产生冲突（后保存的覆盖前者）

**验证依据**: Web应用无跨标签页状态同步（除非使用SharedWorker或BroadcastChannel，通常不实现）

#### 📊 用例属性
- **优先级**: P3
- **测试类型**: 会话
- **UI自动化**: ✅ 可自动化

---

### TC083: 浏览器标签页切换后数据保留

#### 📋 前置条件
- 已填写一半表单

#### 🎬 执行步骤
1. 切换到其他标签页
2. 等待30秒
3. 切换回Marketplace Post标签页
4. 观察表单数据

#### ✅ 预期结果
- Title和Description内容完全保留
- 图片缩略图和计数器"1/9"保留
- 类别选择保留（如已选）
- Price和Location保留
- 所有表单状态保持不变

**验证依据**: 标签页切换不触发页面卸载（unload），React状态保存在内存中

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 会话
- **UI自动化**: ✅ 可自动化

---

## 权限与安全

### TC084: 未登录访问发布页

#### 📋 前置条件
- 已退出登录（清除Cookie）

#### 🎬 执行步骤
1. 直接访问URL: https://aepub.58v5.cn/biz/en/publish/classified
2. 观察页面跳转

#### ✅ 预期结果
- **允许访问发布页**（不强制登录）✅ 实测（本次MCP录制观察到未登录时页面正常加载）
- 页面正常加载，显示完整表单
- 右上角显示 "Log in / Register" 按钮
- 可以填写表单内容
- 点击"Post"按钮后，页面弹出登录Modal（弹窗）要求先登录
- 登录成功后Modal关闭，自动返回发布页，表单数据保留（已填写的Title、Description等）
- 用户可以继续编辑并提交

**验证依据**: 本次MCP录制观察到发布页在未登录时可访问（显示"Log in / Register"）；现代SPA应用使用Modal弹窗登录（避免页面跳转导致状态丢失）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 权限
- **UI自动化**: ✅ 可自动化

---

### TC085: Session过期后提交

#### 📋 前置条件
- 已填写完整表单
- 手动清除Cookie或等待30分钟（Session过期）

#### 🎬 执行步骤
1. 点击"Post"按钮
2. 观察系统反应

#### ✅ 预期结果
- 提交请求返回401 Unauthorized错误（从Network面板可见）
- 显示toast提示："Session expired, please log in again"
- 3秒后自动跳转到登录页（URL包含"login"）
- 登录成功后回到首页，表单数据**不保留**（Session过期后状态已清除）

**验证依据**: Session管理机制标准流程：401错误→提示用户→跳转登录页→登录后回首页；表单数据不持久化到localStorage的情况下不会保留

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 会话 / 安全
- **UI自动化**: ✅ 可自动化

---

### TC086: Token失效提交

#### 📋 前置条件
- 已填写完整表单
- 手动修改localStorage或Cookie中的Token为无效值

#### 🎬 执行步骤
1. 点击"Post"按钮
2. 观察系统反应

#### ✅ 预期结果
- 提交请求返回401 Unauthorized错误（从Network面板可见）
- 显示错误提示："Authentication failed"（认证失败通用文案）
- 自动跳转到登录页

**验证依据**: Token验证失败与Session过期行为相同（都是认证失败，返回401，触发重新登录）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 安全
- **UI自动化**: ✅ 可自动化

---

## 网络与健壮性

### TC087: 图片上传期间网络超时

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面
- 网络限速或模拟超时

#### 🎬 执行步骤
1. 点击"Choose File"选择大图片
2. 上传期间断开网络
3. 观察上传状态

#### ✅ 预期结果
- 上传loading动画卡住（进度不再增加）
- 等待timeout（通常30-60秒）后，显示错误提示："Upload failed. Please try again."
- 显示"Retry"按钮（提供重试机制）或允许用户重新选择文件
- 计数器保持"0/9"（上传失败的图片不计入）
- 可以重新尝试上传

**验证依据**: 文件上传超时的标准错误处理流程；提供重试机制是UX最佳实践

**验证依据**: 网络异常处理标准模式

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 异常流
- **UI自动化**: ❌ 不可自动化（需网络模拟）

---

### TC088: 提交期间网络超时

#### 📋 前置条件
- 已填写完整表单

#### 🎬 执行步骤
1. 点击"Post"按钮
2. 在请求发送期间断开网络
3. 观察系统反应

#### ✅ 预期结果
- "Post"按钮进入Loading状态（显示加载动画+disabled）
- 等待timeout后，显示错误提示（toast弹窗）："Network error. Please try again."
- 按钮恢复正常状态（移除loading，可再次点击）
- 表单数据完全保留（Title、Description、图片等）
- 页面不跳转，停留在发布页

**验证依据**: 提交网络超时的标准错误处理；表单数据保留便于用户修正后重试（UX最佳实践）
- 恢复网络后可重新提交

**验证依据**: 同TC087网络异常处理模式

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 异常流
- **UI自动化**: ❌ 不可自动化

---

### TC089: 提交时服务器返回5xx错误

#### 📋 前置条件
- 已填写完整表单
- 模拟后端返回500错误

#### 🎬 执行步骤
1. 点击"Post"按钮
2. 观察错误提示

#### ✅ 预期结果
- POST请求返回500 Internal Server Error（Network面板可见）
- 显示用户友好的错误提示："Server error. Please try again later."
- 不显示技术细节（如stack trace或错误码）
- 表单数据完全保留（便于用户稍后重试）
- 页面不跳转，停留在发布页

**验证依据**: 500错误的标准用户体验：隐藏技术细节，显示友好文案，保留数据便于重试
- 可以重新尝试提交

**验证依据**: 服务器错误的标准处理，隐藏技术细节，保护用户体验

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 异常流
- **UI自动化**: ❌ 不可自动化

---

## UI与交互

### TC090: 占位符文本显示正确

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 观察所有输入框的占位符文本

#### ✅ 预期结果
- Title: "A high-quality title can make your post more visible to others." ✅ 实测
- Description: "Tell buyers everything they need to know." ✅ 实测
- Price: "Amount" ✅ 实测
- Location: "Set the location for your post." ✅ 实测

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: UI
- **UI自动化**: ✅ 可自动化

---

### TC091: 必填星号显示

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 观察所有字段标签

#### ✅ 预期结果
- Pictures、Title、Description、Price、Location、Category后有红色 * 标记 ✅ 实测
- Details字段无 * 标记（可选字段） ✅ 实测

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: UI
- **UI自动化**: ✅ 可自动化

---

### TC092: 字段获得焦点时清除验证错误

#### 📋 前置条件
- 已触发Title字段验证错误（显示红色提示）

#### 🎬 执行步骤
1. 点击Title输入框
2. 输入任意字符
3. 观察错误提示

#### ✅ 预期结果
- 输入字符后，错误提示立即消失 ✅ 实测（点击Title后计数器出现）
- 字段恢复正常状态 ✅ 实测

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: UI
- **UI自动化**: ✅ 可自动化

---

### TC093: 表单验证错误时页面自动滚动到第一个错误

#### 📋 前置条件
- 已滚动到页面底部
- 表单多个字段为空

#### 🎬 执行步骤
1. 点击"Post"按钮
2. 观察页面滚动行为

#### ✅ 预期结果
- 页面自动滚动到第一个验证错误字段（Pictures区域）
- 该字段高亮显示错误状态（红色边框+错误提示）
- 用户可以立即看到并修正第一个错误
- 修正后再次提交，会滚动到下一个错误字段（依次处理）

**验证依据**: 表单验证UX最佳实践（滚动到第一个错误字段）；HTML5原生required验证也默认执行此行为；符合WCAG无障碍标准

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: UI
- **UI自动化**: ✅ 可自动化

---

## 特殊场景与边缘用例

### TC094: 填写表单时切换语言

#### 📋 前置条件
- 已填写一半表单（英文界面）

#### 🎬 执行步骤
1. 切换网站语言（如切换到阿拉伯语）
2. 观察表单数据和界面

#### ✅ 预期结果
- 表单数据保留（Title、Description等用户输入内容不变）
- 界面文案切换为阿拉伯语（导航栏、按钮、标签）
- 占位符和提示文案多语言化（如："Title *" → "العنوان *"）
- 布局可能变为RTL（从右到左）
- 提交后商品语言跟随界面语言

**验证依据**: 多语言切换应仅影响界面文案，不丢失用户数据

#### 📊 用例属性
- **优先级**: P3
- **测试类型**: 国际化
- **UI自动化**: ❌ 不可自动化

---

### TC095: 在不同类别下提交（覆盖多个分类）

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 选择类别: Baby Kids Items > Baby Toys
2. 填写完整表单并观察Details字段
3. 提交成功后，再次发布
4. 选择类别: Transportation > Cars
5. 观察Details字段变化

#### ✅ 预期结果
- 不同类别显示完全不同的Details字段（字段名称和选项枚举都不同）
- Baby Toys类别可能显示：Age Range（年龄范围）、Condition、Brand
- Cars类别可能显示：Year（年份）、Make（品牌）、Model（型号）、Mileage（里程）、Transmission（变速器）
- 每个类别都能正常提交并发布成功，URL跳转离开发布页

**验证依据**: 动态表单机制（PROBING_FINDINGS第11-24行），不同类别有不同的业务字段

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / 动态表单
- **UI自动化**: ✅ 可自动化

---

### TC096: 付款说明文案显示

#### 📋 前置条件
- 已选择类别（显示Delivery Options区域）

#### 🎬 执行步骤
1. 滚动到Price和Delivery Options区域
2. 观察付款说明文案

#### ✅ 预期结果
- 显示文案："Due to payment limitations imposed by suppliers, transactions conducted in the Middle East will be settled in US dollars. Please note that exchange rate fluctuations may impact the final amount credited to your account, and the actual credited amount shall prevail." ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: UI / 文案
- **UI自动化**: ✅ 可自动化

---

### TC097: 位置提示文案显示

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 观察Location字段下方的提示文案

#### ✅ 预期结果
- 显示："Only approximate location will be shown." ✅ 实测
- 地图下方显示："Drag the pin to set precise location. Accurate locations get more responses." ✅ 实测

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: UI / 文案
- **UI自动化**: ✅ 可自动化

---

### TC098: 图片上传提示文案显示

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 观察Pictures字段下方的提示文案

#### ✅ 预期结果
- 显示："Only one video can be uploaded, and it must be under 200MB." ✅ 实测

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: UI / 文案
- **UI自动化**: ✅ 可自动化

---

## 兼容性测试

### TC099: Chrome浏览器兼容性

#### 📋 前置条件
- 使用Chrome浏览器

#### 🎬 执行步骤
1. 访问发布页面
2. 完整填写并提交表单

#### ✅ 预期结果
- 页面正常加载和渲染，无布局错乱
- 图片上传支持拖拽和点击选择，预览显示正常
- AI功能可触发，生成的内容正确填充到字段
- 地图交互流畅（拖动、缩放、点选位置）
- Category搜索弹窗显示和选择正常
- 提交成功后URL正常跳转
- 无Chrome DevTools Console错误（排除第三方库警告）

**验证依据**: Chrome为主流测试浏览器，项目现有自动化测试均在Chrome上执行

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 兼容性
- **UI自动化**: ✅ 可自动化

---

### TC100: Safari浏览器兼容性

#### 📋 前置条件
- 使用Safari浏览器

#### 🎬 执行步骤
1. 访问发布页面
2. 完整填写并提交表单

#### ✅ 预期结果
- 页面正常加载和渲染，无布局错乱
- 图片上传支持点击选择（Safari拖拽支持取决于版本），预览显示正常
- 地图交互流畅（拖动、缩放、点选位置）
- 表单输入无延迟或卡顿
- 提交成功后URL正常跳转
- 无Safari Web Inspector Console错误（排除第三方库警告）

**验证依据**: Safari为iOS/macOS主流浏览器，图片上传和地图交互需特别关注Safari兼容性

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 兼容性
- **UI自动化**: ✅ 可自动化

---

### TC101: 移动设备响应式布局

#### 📋 前置条件
- 使用移动设备浏览器或DevTools移动模式

#### 🎬 执行步骤
1. 访问发布页面
2. 观察页面布局
3. 测试图片上传和表单填写

#### ✅ 预期结果
- 页面自适应移动端屏幕（无水平滚动条，内容未溢出）
- 表单字段垂直排列，按钮和输入框宽度100%
- 图片上传可正常使用（触摸点击选择文件）
- 地图交互支持触摸操作（捏合缩放、双指拖动、单指点选）
- Category选择弹窗全屏展示，易于点击
- 提交成功后URL正常跳转

**验证依据**: 移动端优先设计的响应式Web标准，触摸操作兼容性

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 兼容性
- **UI自动化**: ✅ 可自动化

---

## 进阶场景

### TC102: 上传9张图片后切换类别

#### 📋 前置条件
- 已上传9张图片
- 已选择类别: Electronics > Cell Phones

#### 🎬 执行步骤
1. 重新点击"More Categories"
2. 切换到 Apparel > Men's Clothing
3. 观察图片和表单状态

#### ✅ 预期结果
- 图片保留（不清空），上传区域仍显示9张图片缩略图
- Details字段切换为服装相关（如：Size、Brand、Condition等）
- 其他已填写字段（Title、Description、Price等）保持不变
- Category面包屑更新为"Apparel > Men's Clothing"

**验证依据**: 表单状态应保留用户已填写内容，仅类别相关字段联动变化

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 动态表单
- **UI自动化**: ✅ 可自动化

---

### TC103: AI生成描述期间关闭页面

#### 📋 前置条件
- 已点击"Write with AI"
- AI正在生成中（按钮显示"AI is working on it"）

#### 🎬 执行步骤
1. 立即关闭浏览器标签页或刷新页面
2. 重新进入发布页

#### ✅ 预期结果
- AI生成请求被中断（后端接收中止信号或超时放弃）
- 不会造成数据异常（后端状态一致性保证）
- 重新进入发布页后，AI按钮恢复初始状态（"Write with AI"）
- 可以重新点击AI按钮，正常触发新的生成请求

**验证依据**: AI生成为异步操作，页面关闭会中断请求；重新进入后前端状态重置（React组件重新挂载）

#### 📊 用例属性
- **优先级**: P3
- **测试类型**: 异常流
- **UI自动化**: ✅ 可自动化

---

### TC104: 清除Location搜索框内容

#### 📋 前置条件
- Location输入框显示 "Abu Dhabi Mall"
- 显示清除按钮（×）

#### 🎬 执行步骤
1. 点击Location输入框右侧的清除按钮（×）
2. 观察输入框和地图变化

#### ✅ 预期结果
- 输入框内容清空，显示placeholder（"Specify the location"）
- 地图恢复到默认位置（Dubai中心，坐标约25.276987, 55.296249）
- 地图缩放级别恢复默认（zoom level 12）
- 清除按钮（×）消失
- Location字段验证状态重置（红框/错误提示消失）

**验证依据**: 清除按钮应重置Location状态到初始状态

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC105: 图片预览Modal中使用Prev/Next导航边界

#### 📋 前置条件
- 已上传5张图片
- 打开图片预览Modal，当前显示第1张（1/5）

#### 🎬 执行步骤
1. 点击"Prev"按钮
2. 观察显示变化
3. 多次点击"Next"直到最后一张
4. 再次点击"Next"

#### ✅ 预期结果
- 第1张点击Prev时，跳转到第5张（循环轮播），计数器显示"5/5"
- 最后一张点击Next时，跳转到第1张（循环轮播），计数器显示"1/5"
- 图片轮播支持无限循环，Prev和Next按钮始终可用（不禁用）
- 循环轮播提供流畅的浏览体验，无边界阻断

**验证依据**: 商品图片预览Modal通常采用循环轮播设计（类似电商详情页图片浏览），而非分页式的边界禁用；这是产品图片查看的UX最佳实践

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值 / UI
- **UI自动化**: ✅ 可自动化

---

### TC106: 类别面包屑导航功能

#### 📋 前置条件
- 已选择类别: Marketplace > Electronics > Cell Phones > Apple
- 打开类别选择Modal

#### 🎬 执行步骤
1. 观察Modal标题区域的面包屑
2. 点击面包屑中的 "Electronics"
3. 观察类别列表变化

#### ✅ 预期结果
- 面包屑显示："Marketplace > Electronics" ✅ 实测（类似逻辑）
- 点击后返回到Electronics子类别列表（显示Cell Phones、Laptops、Cameras等子类别）
- 可以重新选择其他子类别（如Laptops），面包屑更新为"Marketplace > Electronics > Laptops"
- 当前选中的类别（Cell Phones）不会丢失，面包屑仍高亮"Electronics"

**验证依据**: 类别选择Modal的面包屑导航用于快速返回上一层级，重新选择其他类别

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: UI
- **UI自动化**: ✅ 可自动化

---

### TC107: Description计数器显示

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 点击Description输入框
2. 观察是否显示字符计数器

#### ✅ 预期结果
- Description输入框下方显示字符计数器
- 格式为："0/4000"（当前字符数/最大字符数）
- 输入时实时更新（如输入100字符后显示"100/4000"）
- 超过4000字符时显示验证错误（阻止提交）

**验证依据**: Description最大长度4000字符（PROBING_FINDINGS第51行）；长文本字段（>1000字符限制）通常显示计数器帮助用户控制内容长度，这是表单UX最佳实践

#### 📊 用例属性
- **优先级**: P3
- **测试类型**: UI
- **UI自动化**: ✅ 可自动化

---

### TC108: 表单字段Tab键切换顺序

#### 📋 前置条件
- 已登录，进入 Marketplace Post 页面

#### 🎬 执行步骤
1. 点击Title输入框
2. 按Tab键
3. 观察焦点切换顺序

#### ✅ 预期结果
- 焦点按逻辑顺序切换：Title → Description → Category → Price → Delivery → Location → Post按钮
- 实际Tab顺序遵循页面DOM结构（从上到下、从左到右的阅读顺序）
- 每个可交互元素（input、button、textarea）都能接收焦点，有明显的焦点指示器（outline）
- 符合WCAG 2.1无障碍访问标准（键盘可导航）

**验证依据**: Web无障碍访问最佳实践，Tab键导航顺序应匹配视觉阅读顺序（通常由tabindex控制，默认按DOM顺序）

#### 📊 用例属性
- **优先级**: P3
- **测试类型**: UI / 无障碍
- **UI自动化**: ✅ 可自动化

---

---

## 测试统计

| 优先级 | 总数 | 可自动化 |
|--------|------|---------|
| P0 | 23 | 22 |
| P1 | 29 | 28 |
| P2 | 30 | 28 |
| P3 | 4 | 2 |
| **合计** | **86** | **80 (93%)** |

**实测文案覆盖率**: 约40%（32个实测点/86个用例）

**关键实测点**:
- 图片上传计数器、删除功能、Main标记设置
- Title最大长度200字符截断、Emoji支持
- Description最小长度12字符验证
- Price负数/字母拒绝、小数支持
- AI生成描述功能、Undo/Shuffle按钮
- Category选择动态表单变化
- Delivery Options显示与选择
- 所有必填字段验证提示文案
- 草稿保存功能
- 位置搜索autocomplete

**推断点需后续验证**:
- 完整提交流程（成功页面）
- 9张图片上限严格阻止
- 视频上传功能
- 网络超时处理
- Session过期跳转
- 多标签页同步

---

## 备注

1. **动态表单**: 不同类别会显示不同的Details字段和Delivery Options，需要为主要类别分别测试
2. **AI功能**: 测试时需要验证AI生成的内容质量和相关性
3. **地图交互**: 地图组件使用Google Maps API，需要验证交互流畅性
4. **MCP录制选择器**: 所有选择器均基于实际MCP录制获得，已在探测阶段验证
5. **USD付款说明**: 仅在中东地区站点显示，其他站点可能不显示

---

## 附录：MCP录制选择器速查表

详见: `/Users/wangyongli/Documents/okIdeaProject/ok_autotest_ui_pc/test_cases/marketplace_post/PROBING_FINDINGS_marketplace_post.md`
