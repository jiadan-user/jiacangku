# OK.com - Marketplace Post 完整测试用例（含图片上传与配送选项）

> **生成时间**: 2026-02-27  
> **探测方式**: Playwright MCP 实测 + Web QA Brain 分析  
> **测试范围**: 图片/视频上传、Delivery Options（三种配送方式）、完整发布流程  
> **总用例数**: 18 条  
> **可自动化**: 15 条（83%）

---

## 测试环境

- **测试网站**: https://aepub.58v5.cn/biz/en/publish/classified
- **测试账号**: liwenfeng01@58.com
- **密码**: Liwenfeng01
- **测试图片路径**: C:\Users\liwenfeng01\Pictures\Saved Pictures
- **分类路径**: Marketplace → Electronics → Cell Phones → Apple
- **浏览器**: Chromium (Playwright)

---

## 模块一：图片上传功能

### TC001: 上传单张图片 - JPG格式

**前置条件**:
- 已登录账号
- 在 Marketplace Post 发布页面
- 图片路径下有可用的 JPG 图片

**执行步骤**:
1. 点击 "Choose File" 按钮或 Upload 区域
2. 在文件选择对话框中，导航到 `C:\Users\liwenfeng01\Pictures\Saved Pictures`
3. 选择一张 JPG 格式的图片（如 `test_image.jpg`，文件大小 < 5MB）
4. 确认选择

**预期结果**:
- 图片上传成功，显示缩略图预览 ⚠️ 推断
- 计数器从 "0/9" 变为 "1/9" ⚠️ 推断
- 可以看到已上传图片的删除按钮 ⚠️ 推断

- **优先级**: P0
- **测试类型**: 正向 / 核心功能
- **UI自动化**: ✅ 可自动化（使用 `set_input_files()`）

---

### TC002: 上传单张图片 - PNG格式

**前置条件**:
- 已登录，在发布页面
- 图片路径下有可用的 PNG 图片

**执行步骤**:
1. 点击 Upload 区域
2. 选择一张 PNG 格式的图片（文件大小 < 5MB）
3. 确认选择

**预期结果**:
- PNG 图片上传成功 ⚠️ 推断
- 计数器变为 "1/9" ⚠️ 推断

- **优先级**: P1
- **测试类型**: 正向 / 格式支持
- **UI自动化**: ✅ 可自动化

---

### TC003: 上传多张图片（3张）

**前置条件**:
- 已登录，在发布页面
- 图片路径下有至少3张可用图片

**执行步骤**:
1. 点击 Upload 区域
2. 在文件选择对话框中，按住 Ctrl 键，同时选择3张图片
3. 确认选择

**预期结果**:
- 3张图片全部上传成功 ⚠️ 推断
- 计数器显示 "3/9" ⚠️ 推断
- 每张图片都有独立的删除按钮 ⚠️ 推断

- **优先级**: P0
- **测试类型**: 正向 / 批量上传
- **UI自动化**: ✅ 可自动化（传递多个文件路径）

---

### TC004: 上传图片达到上限（9张）

**前置条件**:
- 已登录，在发布页面
- 图片路径下有至少9张可用图片

**执行步骤**:
1. 连续上传9张图片（可分批上传）
2. 观察计数器变化
3. 尝试再次点击 Upload 区域

**预期结果**:
- 所有9张图片上传成功 ⚠️ 推断
- 计数器显示 "9/9" ⚠️ 推断
- Upload 按钮变为禁用状态或提示"已达上限" ⚠️ 推断
- 无法继续上传第10张图片 ⚠️ 推断

- **优先级**: P1
- **测试类型**: 边界值 / 上限验证
- **UI自动化**: ✅ 可自动化

---

### TC005: 尝试上传第10张图片（超出限制）

**前置条件**:
- 已登录，在发布页面
- 已上传9张图片（计数器显示 9/9）

**执行步骤**:
1. 尝试点击 Upload 区域或选择新图片

**预期结果**:
- Upload 按钮禁用，无法继续上传 ⚠️ 推断
- 或显示错误提示："最多只能上传9张图片" ⚠️ 推断

- **优先级**: P1
- **测试类型**: 负向 / 边界值
- **UI自动化**: ✅ 可自动化

---

### TC006: 删除已上传的图片

**前置条件**:
- 已登录，在发布页面
- 已上传至少1张图片

**执行步骤**:
1. 找到已上传图片的删除按钮（通常是 X 图标或删除图标）
2. 点击删除按钮
3. 观察页面变化

**预期结果**:
- 图片被成功删除，缩略图消失 ⚠️ 推断
- 计数器减1（如从 "3/9" 变为 "2/9"）⚠️ 推断
- 可以继续上传新图片 ⚠️ 推断

- **优先级**: P1
- **测试类型**: 正向 / 删除功能
- **UI自动化**: ✅ 可自动化

---

### TC007: 上传视频文件（正常）

**前置条件**:
- 已登录，在发布页面
- 图片路径下有可用的视频文件（< 200MB）

**执行步骤**:
1. 点击 Upload 区域
2. 选择一个视频文件（如 `.mp4`, `.mov`, `.avi`）
3. 确认选择

**预期结果**:
- 视频上传成功 ⚠️ 推断
- 显示视频缩略图或视频图标 ⚠️ 推断
- 提示："Only one video can be uploaded, and it must be under 200MB." ✅ 实测（页面提示文案）

- **优先级**: P1
- **测试类型**: 正向 / 视频支持
- **UI自动化**: ✅ 可自动化

---

### TC008: 上传超大视频（> 200MB）

**前置条件**:
- 已登录，在发布页面
- 准备一个大于 200MB 的视频文件

**执行步骤**:
1. 点击 Upload 区域
2. 选择超过 200MB 的视频文件
3. 确认选择

**预期结果**:
- 上传失败，显示错误提示："视频文件必须小于 200MB" ⚠️ 推断
- 或上传进度显示后中断，提示文件过大 ⚠️ 推断

- **优先级**: P2
- **测试类型**: 负向 / 边界值
- **UI自动化**: ✅ 可自动化

---

### TC009: 同时上传图片和视频

**前置条件**:
- 已登录，在发布页面

**执行步骤**:
1. 先上传3张图片
2. 再上传1个视频文件

**预期结果**:
- 图片和视频都上传成功 ⚠️ 推断
- 图片计数器显示 "3/9"，视频单独显示 ⚠️ 推断

- **优先级**: P2
- **测试类型**: 正向 / 混合上传
- **UI自动化**: ✅ 可自动化

---

### TC010: 未上传图片直接提交

**前置条件**:
- 已登录，在发布页面
- 填写了所有其他必填字段（Title, Description, Category, Price, Location, Delivery Options）
- **未上传任何图片**

**执行步骤**:
1. 不上传图片
2. 点击 "Post" 按钮

**预期结果**:
- 提交失败 ✅ 实测
- Pictures 区域下方显示红色错误提示："Please upload a photo before submitting." ✅ 实测
- 页面不跳转，停留在发布页 ✅ 实测

- **优先级**: P0
- **测试类型**: 必填验证 / 负向
- **UI自动化**: ✅ 可自动化

---

## 模块二：Delivery Options（配送选项）

### TC011: 选择 "Seller pays for postage" 完整提交

**前置条件**:
- 已登录，在发布页面
- 已填写所有必填字段：
  - ✅ Pictures: 已上传至少1张图片
  - ✅ Title: "iPhone 14 Pro Max 256GB"
  - ✅ Description: "Brand new iPhone 14 Pro Max with 256GB storage."
  - ✅ Category: Marketplace → Electronics → Cell Phones → Apple
  - ✅ Price: "3500"
  - ✅ Location: 默认值（Arabian Tea House - Jumeirah Archaeological Site, Dubai）

**执行步骤**:
1. 在 Delivery Options 区域，点击 "Seller pays for postage" 选项
2. 观察该选项是否被选中（高亮或勾选标记）
3. 点击 "Post" 按钮
4. 观察页面跳转或提示

**预期结果**:
- 步骤1：✅ "Seller pays for postage" 被选中，错误提示消失 ✅ 实测（错误提示消失已验证）
- 步骤3：提交成功，页面跳转到发布成功页面 ⚠️ 推断
- 或显示成功 Toast 提示："发布成功" ⚠️ 推断
- 或返回到帖子详情页 ⚠️ 推断

- **优先级**: P0
- **测试类型**: 正向 / 核心流程
- **UI自动化**: ✅ 可自动化

**实测截图**: `.playwright-mcp\page-2026-02-28T02-52-56-710Z.png`

---

### TC012: 选择 "Buyer pays for postage" 完整提交

**前置条件**:
- 已登录，在发布页面
- 所有必填字段已填写（同 TC011）

**执行步骤**:
1. 在 Delivery Options 区域，点击 "Buyer pays for postage" 选项
2. 观察该选项是否被选中
3. 点击 "Post" 按钮
4. 观察提交结果

**预期结果**:
- "Buyer pays for postage" 被选中 ⚠️ 推断
- 提交成功，页面跳转或显示成功提示 ⚠️ 推断

- **优先级**: P0
- **测试类型**: 正向 / 核心流程
- **UI自动化**: ✅ 可自动化

---

### TC013: 选择 "Arrange pickup with the buyer" 完整提交

**前置条件**:
- 已登录，在发布页面
- 所有必填字段已填写（同 TC011）

**执行步骤**:
1. 在 Delivery Options 区域，点击 "Arrange pickup with the buyer" 选项
2. 观察该选项是否被选中
3. 点击 "Post" 按钮
4. 观察提交结果

**预期结果**:
- "Arrange pickup with the buyer" 被选中 ⚠️ 推断
- 提交成功，页面跳转或显示成功提示 ⚠️ 推断

- **优先级**: P0
- **测试类型**: 正向 / 核心流程
- **UI自动化**: ✅ 可自动化

---

### TC014: 未选择 Delivery Options 直接提交

**前置条件**:
- 已登录，在发布页面
- 已选择分类（Marketplace → Electronics → Cell Phones → Apple）
- 已填写其他所有必填字段（Pictures, Title, Description, Price, Location）
- **未选择任何 Delivery Options**

**执行步骤**:
1. 不选择任何 Delivery Options
2. 直接点击 "Post" 按钮

**预期结果**:
- 提交失败 ✅ 实测
- Delivery Options 区域下方显示红色错误提示："Please fill out this field." ✅ 实测
- 页面不跳转，停留在发布页 ✅ 实测

- **优先级**: P0
- **测试类型**: 必填验证 / 负向
- **UI自动化**: ✅ 可自动化

---

### TC015: 切换 Delivery Options 选项

**前置条件**:
- 已登录，在发布页面
- 已填写所有必填字段

**执行步骤**:
1. 先选择 "Seller pays for postage"
2. 观察该选项被选中
3. 再点击 "Buyer pays for postage"
4. 观察选项状态变化

**预期结果**:
- 步骤2："Seller pays for postage" 被选中（高亮或勾选）⚠️ 推断
- 步骤4："Buyer pays for postage" 被选中，"Seller pays for postage" 自动取消选中 ⚠️ 推断
- 每次只能选中一个选项（单选行为）⚠️ 推断

- **优先级**: P1
- **测试类型**: 边界值 / UI交互
- **UI自动化**: ✅ 可自动化

---

### TC016: Delivery Options 说明文案验证

**前置条件**:
- 已登录，在发布页面
- 已选择支持在线交易的分类（如 Cell Phones）

**执行步骤**:
1. 滚动到 Delivery Options 区域
2. 观察说明文案

**预期结果**:
- 显示文案："This category supports online transactions. Choose shipping if needed." ✅ 实测

- **优先级**: P3
- **测试类型**: UI文案验证
- **UI自动化**: ✅ 可自动化

---

### TC017: 不同分类对 Delivery Options 的影响

**前置条件**:
- 已登录，在发布页面

**执行步骤**:
1. 先选择分类："Marketplace → Electronics → Cell Phones"
2. 观察是否显示 Delivery Options 区域
3. 更改分类为："Marketplace → Free Stuff"
4. 观察 Delivery Options 区域是否仍然显示

**预期结果**:
- 步骤2：Cell Phones 分类显示 Delivery Options，且为必填项 ✅ 实测
- 步骤4：Free Stuff 分类可能不显示 Delivery Options（免费物品不涉及邮费）⚠️ 推断

- **优先级**: P2
- **测试类型**: 分类规则 / 动态表单
- **UI自动化**: ✅ 可自动化

---

### TC018: 完整发布流程 - 所有步骤验证

**前置条件**:
- 已登录

**执行步骤**:
1. 导航到发布页面
2. 上传2张图片
3. 填写 Title: "iPhone 14 Pro Max 256GB"
4. 填写 Description: "Brand new iPhone 14 Pro Max with 256GB storage."
5. 选择分类：Marketplace → Electronics → Cell Phones → Apple
6. 选择 Details: Condition = New, Storage = 256 GB
7. 填写 Price: "3500"
8. 保持 Location 默认值
9. 选择 Delivery Options: "Seller pays for postage"
10. 点击 "Post" 按钮

**预期结果**:
- 所有字段填写成功 ⚠️ 推断
- 提交成功，页面跳转到成功页面 ⚠️ 推断
- 或显示成功 Toast："Your post has been published successfully" ⚠️ 推断
- 可以在"My Posts"或首页看到新发布的帖子 ⚠️ 推断

- **优先级**: P0
- **测试类型**: 端到端 / 完整流程
- **UI自动化**: ✅ 可自动化

---

## 测试统计

| 优先级 | 总数 | 可自动化 |
|--------|------|---------|
| P0 | 7 | 7 |
| P1 | 8 | 8 |
| P2 | 2 | 2 |
| P3 | 1 | 1 |
| **合计** | **18** | **18 (100%)** |

**模块分布**:
- 图片/视频上传：10条
- Delivery Options（配送选项）：8条

**实测覆盖率**：22%（4条实测 / 18条总用例）

---

## 实测验证记录

### 已验证场景

| 场景 | 验证点 | 状态 |
|------|--------|------|
| 未上传图片提交 | 错误提示："Please upload a photo before submitting." | ✅ 实测 |
| 未选择配送选项提交 | 错误提示："Please fill out this field." | ✅ 实测 |
| 选择 Seller pays for postage | 错误提示消失 | ✅ 实测 |
| Delivery Options 说明文案 | "This category supports online transactions. Choose shipping if needed." | ✅ 实测 |

### 待验证场景（需要实际文件上传）

- 图片上传成功后的缩略图显示
- 计数器变化（0/9 → 1/9 → ... → 9/9）
- 图片删除功能
- 视频上传功能
- 提交成功后的跳转页面或成功提示

---

## 测试数据

### 图片文件

**路径**: `C:\Users\liwenfeng01\Pictures\Saved Pictures`

**推荐文件**:
- 测试图片1: `test_image_01.jpg` (< 5MB)
- 测试图片2: `test_image_02.png` (< 5MB)
- 测试图片3-9: 其他 JPG/PNG 图片
- 测试视频: `test_video.mp4` (< 200MB)
- 超大视频（用于负向测试）: `large_video.mp4` (> 200MB)

### 发布内容

- **Title**: iPhone 14 Pro Max 256GB
- **Description**: Brand new iPhone 14 Pro Max with 256GB storage.
- **Category**: Marketplace → Electronics → Cell Phones → Apple
- **Price**: 3500 AED
- **Location**: Arabian Tea House - Jumeirah Archaeological Site, Dubai（默认）
- **Delivery Options**: 
  - 选项1: Seller pays for postage
  - 选项2: Buyer pays for postage
  - 选项3: Arrange pickup with the buyer

---

## 自动化脚本示例

### Playwright Python - 图片上传

```python
import pytest
from playwright.sync_api import Page

def test_upload_single_image(page: Page):
    """TC001: 上传单张图片"""
    # 导航到发布页面
    page.goto("https://aepub.58v5.cn/biz/en/publish/classified?traceId=1772177314370")
    
    # 上传图片
    file_input = page.locator('input[type="file"]')
    file_input.set_input_files(r"C:\Users\liwenfeng01\Pictures\Saved Pictures\test_image.jpg")
    
    # 验证计数器变化
    assert page.get_by_text("1/9").is_visible()

def test_upload_multiple_images(page: Page):
    """TC003: 上传多张图片"""
    page.goto("https://aepub.58v5.cn/biz/en/publish/classified?traceId=1772177314370")
    
    # 上传3张图片
    file_input = page.locator('input[type="file"]')
    file_input.set_input_files([
        r"C:\Users\liwenfeng01\Pictures\Saved Pictures\test_image_01.jpg",
        r"C:\Users\liwenfeng01\Pictures\Saved Pictures\test_image_02.jpg",
        r"C:\Users\liwenfeng01\Pictures\Saved Pictures\test_image_03.jpg"
    ])
    
    # 验证计数器
    assert page.get_by_text("3/9").is_visible()

def test_delivery_option_seller_pays(page: Page):
    """TC011: 选择 Seller pays for postage"""
    page.goto("https://aepub.58v5.cn/biz/en/publish/classified?traceId=1772177314370")
    
    # 填写所有必填字段...
    # （省略登录和填表代码）
    
    # 选择配送选项
    page.get_by_text("Seller pays for postage").click()
    
    # 点击提交
    page.get_by_role("button", name="Post").click()
    
    # 验证提交成功（根据实际页面调整）
    # assert page.get_by_text("发布成功").is_visible()
```

---

## 备注

1. 标记 ✅ 实测 的用例预期结果来自真实浏览器操作验证
2. 标记 ⚠️ 推断 的用例预期结果基于业务规则和 UI 线索推断
3. **图片上传功能** 由于 MCP 工具限制，未进行实际文件上传探测，预期结果基于行业标准实践
4. **提交成功跳转** 由于缺少图片上传，未能验证完整提交流程，建议补充实际探测
5. 建议在自动化测试中使用真实的图片文件进行完整验证

---

**文档生成时间**: 2026-02-27  
**生成方式**: Web QA Brain Skill（三阶段工作流）  
**测试工程师**: AI Agent (Claude Sonnet 4.5)  
**审核状态**: 待人工评审
