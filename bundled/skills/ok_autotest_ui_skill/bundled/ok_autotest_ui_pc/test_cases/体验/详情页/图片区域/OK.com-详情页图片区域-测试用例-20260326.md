# OK.com - 详情页图片区域 测试用例

> **生成时间**: 2026-03-26  
> **测试站点**: 阿联酋站 Community 类目  
> **测试范围**: 列表页进入详情页后，图片区域的展示和交互功能  
> **总用例数**: 17 条  
> **可自动化**: 16 条 (94%)  

---

## 测试环境配置

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | ae | 阿联酋站 |
| 基础URL | https://ae.ok.com/en/city-abu-dhabi/cate-community/ | Community 列表页 |
| 站点名称 | AE OK.com | 用于日志展示 |
| 角色 | visitor / buyer | 访客（未登录）/ 买家（已登录） |
| 测试视口 | 1440×900 | 宽屏 |

---

## 阶段一：Application Overview（功能摘要）

### 功能定位
详情页图片区域是用户查看商品/服务的主要视觉入口，支持两种形态：
1. **单图模式**：仅展示一张主图，无缩略图区域
2. **多图模式**：展示主图 + 缩略图列表，支持图片切换、放大查看等交互

### 核心功能
- 图片加载与展示
- 缩略图切换（多图模式）
- 图片放大预览（lightbox/modal）
- 图片导航（上一张/下一张，支持循环）
- 大图模式缩略图翻页（图片 > 7 张时）

### 用户角色
- **visitor**：可正常查看所有图片功能
- **buyer**：与 visitor 权限一致（图片查看不区分登录态）

---

## 阶段二：测试计划

### 模块 A：单图模式（3个用例）
- TC001: 单图卡片进入详情页应正确展示图片
- TC002: 单图模式无缩略图区域
- TC003: 单图加载失败应显示占位图

### 模块 B：多图模式 - 基础展示（5个用例）
- TC004: 多图卡片进入详情页应展示主图和缩略图
- TC005: 默认展示第一张图片为主图
- TC006: 缩略图数量应与实际图片数一致
- TC007: 当前选中的缩略图应有高亮样式
- TC008: 图片应正确加载并显示

### 模块 C：多图模式 - 切换交互（4个用例）
- TC009: 点击缩略图应切换主图
- TC010: 主图切换时当前缩略图高亮应更新
- TC011: 支持左右箭头按钮循环切换图片
- TC012: 点击主图应打开放大预览弹层

### 模块 D：大图模式 - 图片翻页（5个用例）
- TC013: 大图模式主图支持左右箭头循环翻页
- TC014: 大图模式缩略图高亮应与主图同步
- TC015: 大图模式支持关闭返回详情页
- TC016: 大图模式 7+ 图片时缩略图区域显示翻页箭头
- TC017: 大图模式缩略图翻页箭头支持循环翻页

---

## 模块 A：单图模式

### TC001: 单图卡片进入详情页应正确展示图片

#### 📋 前置条件
- 访问 https://ae.ok.com/en/city-abu-dhabi/cate-community/
- 列表页已加载完成，存在单图卡片

#### 🎬 执行步骤
1. 在列表页中识别单图卡片（仅显示一张图片的卡片）
2. 点击该卡片进入详情页
3. 观察详情页图片区域

#### ✅ 预期结果
- 详情页成功加载，URL 变更为详情页地址
- 图片区域显示该商品的唯一图片
- 图片清晰可见，无加载失败或错位
- 图片尺寸适配展示区域，保持比例不变形

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### TC002: 单图模式无缩略图区域

#### 📋 前置条件
- 已进入单图详情页

#### 🎬 执行步骤
1. 观察图片区域下方或侧边
2. 检查是否存在缩略图列表

#### ✅ 预期结果
- 不显示缩略图区域
- 不显示图片切换箭头（上一张/下一张）
- 整个图片区域简洁，仅展示单张主图

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### TC003: 单图加载失败应显示占位图

#### 📋 前置条件
- 能够模拟图片加载失败（网络拦截或使用测试数据）

#### 🎬 执行步骤
1. 进入单图详情页
2. 模拟图片 URL 返回 404 或加载失败

#### ✅ 预期结果
- 图片区域显示默认占位图或 "Image not available" 提示
- 不显示破损图片图标
- 页面布局不错乱

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 异常 / 容错
- **UI自动化**: ⚠️ 需要 mock 网络响应

---

## 模块 B：多图模式 - 基础展示

### TC004: 多图卡片进入详情页应展示主图和缩略图

#### 📋 前置条件
- 访问 https://ae.ok.com/en/city-abu-dhabi/cate-community/
- 列表页已加载完成，存在多图卡片（显示 2+ 张图片）

#### 🎬 执行步骤
1. 在列表页中识别多图卡片
2. 点击该卡片进入详情页
3. 观察详情页图片区域

#### ✅ 预期结果
- 详情页成功加载
- 图片区域包含两部分：
  - 主图区域（大尺寸展示）
  - 缩略图列表（小尺寸，横向或纵向排列）
- 主图清晰可见
- 缩略图列表可见且排列整齐

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### TC005: 默认展示第一张图片为主图

#### 📋 前置条件
- 已进入多图详情页

#### 🎬 执行步骤
1. 观察主图区域显示的图片
2. 对比缩略图列表的第一张图片

#### ✅ 预期结果
- 主图显示的是第一张图片（与第一个缩略图一致）
- 第一个缩略图有高亮/选中样式（如边框、阴影、透明度变化）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### TC006: 缩略图数量应与实际图片数一致

#### 📋 前置条件
- 已进入多图详情页

#### 🎬 执行步骤
1. 统计缩略图列表中的缩略图数量
2. 通过切换主图，记录实际可切换的图片总数

#### ✅ 预期结果
- 缩略图数量 = 实际图片总数
- 每个缩略图对应一张不同的图片
- 无重复或缺失

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / 数据一致性
- **UI自动化**: ✅ 可自动化

---

### TC007: 当前选中的缩略图应有高亮样式

#### 📋 前置条件
- 已进入多图详情页

#### 🎬 执行步骤
1. 观察初始状态下的第一个缩略图样式
2. 点击第二个缩略图
3. 观察缩略图样式变化

#### ✅ 预期结果
- 初始状态：第一个缩略图有高亮样式（如边框、背景色、透明度）
- 点击第二个缩略图后：
  - 第二个缩略图变为高亮
  - 第一个缩略图恢复普通样式
- 任何时刻只有一个缩略图处于高亮状态

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI / 交互反馈
- **UI自动化**: ✅ 可自动化

---

### TC008: 图片应正确加载并显示

#### 📋 前置条件
- 已进入多图详情页

#### 🎬 执行步骤
1. 观察主图是否完整加载
2. 逐一检查所有缩略图是否完整加载
3. 检查图片清晰度

#### ✅ 预期结果
- 所有图片均成功加载，无破损图标
- 主图清晰，无模糊或像素化
- 缩略图虽尺寸较小，但可辨识内容
- 图片不超出容器边界，无溢出或裁剪错误

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / 性能
- **UI自动化**: ✅ 可自动化

---

## 模块 C：多图模式 - 切换交互

### TC009: 点击缩略图应切换主图

#### 📋 前置条件
- 已进入多图详情页（至少有 3 张图片）

#### 🎬 执行步骤
1. 记录当前主图显示的内容
2. 点击第三个缩略图
3. 观察主图变化

#### ✅ 预期结果
- 主图立即切换为第三张图片
- 主图切换流畅，无卡顿或闪烁
- 第三个缩略图变为高亮状态
- 之前高亮的缩略图恢复普通状态

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / 交互
- **UI自动化**: ✅ 可自动化

---

### TC010: 主图切换时当前缩略图高亮应更新

#### 📋 前置条件
- 已进入多图详情页

#### 🎬 执行步骤
1. 点击第二个缩略图，观察高亮状态
2. 点击第四个缩略图，观察高亮状态
3. 点击第一个缩略图，观察高亮状态

#### ✅ 预期结果
- 每次点击后，被点击的缩略图立即变为高亮
- 之前高亮的缩略图同时取消高亮
- 高亮状态与主图显示的内容始终一致

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / 状态同步
- **UI自动化**: ✅ 可自动化

---

### TC011: 支持左右箭头按钮循环切换图片

#### 📋 前置条件
- 已进入多图详情页（至少有 3 张图片）

#### 🎬 执行步骤
1. 观察主图区域是否有左右箭头按钮
2. 记录当前显示第一张图片
3. 点击左箭头按钮
4. 观察主图变化
5. 连续点击右箭头按钮直到超过图片总数

#### ✅ 预期结果
- 主图区域显示左右箭头导航按钮（可能是悬停时显示）
- 在第一张图片时点击左箭头：主图切换到最后一张图片（循环）
- 连续点击右箭头超过图片总数：从最后一张循环到第一张
- 循环切换流畅，无卡顿
- 缩略图高亮状态同步更新

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / 交互 / 循环逻辑
- **UI自动化**: ✅ 可自动化

---

### TC012: 点击主图应打开放大预览弹层

#### 📋 前置条件
- 已进入多图详情页

#### 🎬 执行步骤
1. 将鼠标悬停在主图上（观察 cursor 变化）
2. 点击主图

#### ✅ 预期结果
- 打开全屏或大尺寸图片预览弹层
- 弹层显示当前主图的高清版本
- 弹层有半透明黑色遮罩背景
- 弹层右上角有关闭按钮（× 图标）
- 弹层显示左右导航箭头用于切换图片

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / 交互
- **UI自动化**: ✅ 可自动化

---

## 模块 D：大图模式 - 图片翻页

### TC013: 大图模式主图支持左右箭头循环翻页

#### 📋 前置条件
- 已进入多图详情页
- 已点击主图打开大图预览弹层

#### 🎬 执行步骤
1. 观察大图弹层中的主图（应该是第一张）
2. 点击左箭头按钮
3. 观察主图是否切换到最后一张
4. 连续点击右箭头按钮，直到超过图片总数
5. 观察是否从最后一张循环回到第一张

#### ✅ 预期结果
- 大图弹层显示左右箭头导航按钮
- 在第一张图片时点击左箭头：主图切换到最后一张（循环）
- 在最后一张图片时点击右箭头：主图切换到第一张（循环）
- 循环切换流畅，有淡入淡出或滑动动画（可选）
- 左右箭头始终保持可点击状态（不禁用）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / 交互 / 循环逻辑
- **UI自动化**: ✅ 可自动化

---

### TC014: 大图模式缩略图高亮应与主图同步

#### 📋 前置条件
- 已进入多图详情页
- 已打开大图预览弹层

#### 🎬 执行步骤
1. 观察大图弹层中缩略图区域（如果存在）
2. 点击右箭头按钮切换 2 次
3. 观察缩略图高亮状态变化
4. 点击左箭头按钮切换 1 次
5. 观察缩略图高亮状态变化

#### ✅ 预期结果
- 大图弹层底部或侧边显示缩略图列表
- 当前显示的主图对应的缩略图高亮显示
- 每次切换主图时，缩略图高亮立即同步更新
- 高亮状态始终与主图一致

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / 状态同步
- **UI自动化**: ✅ 可自动化

---

### TC015: 大图模式支持关闭返回详情页

#### 📋 前置条件
- 已打开大图预览弹层

#### 🎬 执行步骤
1. 测试以下关闭方式：
   - 点击关闭按钮（×）
   - 按 ESC 键
   - 点击弹层外的遮罩区域

#### ✅ 预期结果
- 三种方式均能成功关闭大图预览弹层
- 关闭后返回详情页，主图保持关闭前的状态
- 页面滚动位置保持不变
- 关闭动画流畅（淡出效果）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / 交互
- **UI自动化**: ✅ 可自动化

---

### TC016: 大图模式 7+ 图片时缩略图区域显示翻页箭头

#### 📋 前置条件
- 已进入多图详情页（图片数量 ≥ 8 张）
- 已打开大图预览弹层

#### 🎬 执行步骤
1. 观察大图弹层中的缩略图区域
2. 检查是否显示左右翻页箭头

#### ✅ 预期结果
- 缩略图区域显示左右翻页箭头按钮
- 缩略图区域一次性显示有限数量的缩略图（如 7 个）
- 箭头按钮清晰可见，样式与主图箭头一致或相似

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI / 条件展示
- **UI自动化**: ✅ 可自动化
- **备注**: ⚠️ 如列表中无 7+ 张图的帖子，此用例可跳过

---

### TC017: 大图模式缩略图翻页箭头支持循环翻页

#### 📋 前置条件
- 已进入多图详情页（图片数量 ≥ 8 张）
- 已打开大图预览弹层
- 缩略图区域显示翻页箭头

#### 🎬 执行步骤
1. 记录初始状态下可见的缩略图（应该是第 1-7 张）
2. 点击右翻页箭头 1 次
3. 观察缩略图列表变化
4. 继续点击右翻页箭头，观察每次点击后的变化
5. 连续点击右翻页箭头直到超过最后一张图片
6. 观察是否循环回到显示第 1-7 张
7. 点击左翻页箭头测试反向逐张滚动

#### ✅ 预期结果
- 初始状态：缩略图区域显示第 1-7 张图片
- 第 1 次点击右翻页箭头：缩略图区域向左滚动一张，显示第 2-8 张
- 第 2 次点击右翻页箭头：缩略图区域再向左滚动一张，显示第 3-9 张
- 继续点击：每次点击右箭头，缩略图列表向左滚动一张（逐张滚动）
- 在最后一组时点击右翻页箭头：循环回到显示第 1-7 张
- 在第一组时点击左翻页箭头：循环到最后一组（如共 10 张图，则显示第 4-10 张）
- 滚动过程流畅，有平滑的过渡动画
- 当前选中的缩略图始终在可见区域内

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / 交互 / 循环逻辑
- **UI自动化**: ✅ 可自动化
- **备注**: ⚠️ 如列表中无 7+ 张图的帖子，此用例可跳过

---

## 阶段三：测试数据准备

### 单图测试数据
需要准备：
- 至少 2 个单图卡片 URL（Community 类目中实际存在的帖子）
- 1 个图片加载失败的测试 URL（用于 TC003）

### 多图测试数据
需要准备：
- 至少 4 个多图卡片 URL，图片数量分别为：
  - 2-3 张图片（基础测试）
  - 4-6 张图片（常规测试）
  - 8-10 张图片（大图模式缩略图翻页测试，TC016-TC017）
  - 15+ 张图片（大量图片压力测试，可选）

### 图片质量要求
- 主图尺寸：建议 ≥ 800×600
- 缩略图尺寸：建议 ≥ 150×150
- 预览大图尺寸：建议 ≥ 1200×900

### 特殊说明
- **TC016-TC017**: 需要图片数 ≥ 8 张的帖子。如果 Community 列表中找不到满足条件的帖子，这两个用例可以标记为 `@pytest.mark.skip(reason="列表中无 7+ 张图的帖子")`

---

## 阶段四：自动化实现建议

### Page Object 设计

```python
class DetailPageImageGallery(BasePage):
    """详情页图片区域 Page Object"""
    
    # 单图模式
    single_image = "img.detail-main-image"
    
    # 多图模式 - 详情页
    main_image = "div.gallery-main img"
    thumbnails = "div.gallery-thumbnails img"
    thumbnail_active = "div.gallery-thumbnails img.active"
    arrow_left = "button.gallery-arrow-left"
    arrow_right = "button.gallery-arrow-right"
    
    # 大图预览弹层
    lightbox = "[role='dialog'].image-lightbox"
    lightbox_image = "[role='dialog'] img.lightbox-image"
    lightbox_close = "[role='dialog'] button.close"
    lightbox_arrow_left = "[role='dialog'] button.prev"
    lightbox_arrow_right = "[role='dialog'] button.next"
    lightbox_overlay = "[role='dialog'] .overlay"
    
    # 大图模式缩略图区域（7+ 张图时显示）
    lightbox_thumbnails = "[role='dialog'] .thumbnail-list img"
    lightbox_thumbnail_active = "[role='dialog'] .thumbnail-list img.active"
    lightbox_thumbnail_arrow_left = "[role='dialog'] .thumbnail-nav-left"
    lightbox_thumbnail_arrow_right = "[role='dialog'] .thumbnail-nav-right"
    
    def get_thumbnail_count(self):
        """获取缩略图数量"""
        return self.page.locator(self.thumbnails).count()
    
    def click_thumbnail(self, index: int):
        """点击指定索引的缩略图"""
        self.page.locator(self.thumbnails).nth(index).click()
    
    def get_active_thumbnail_index(self):
        """获取当前高亮缩略图的索引"""
        all_thumbnails = self.page.locator(self.thumbnails)
        count = all_thumbnails.count()
        for i in range(count):
            if "active" in all_thumbnails.nth(i).get_attribute("class"):
                return i
        return -1
    
    def click_main_image(self):
        """点击主图打开大图预览"""
        self.page.locator(self.main_image).click()
    
    def is_lightbox_open(self):
        """判断大图预览弹层是否打开"""
        return self.page.locator(self.lightbox).is_visible()
    
    def close_lightbox_by_esc(self):
        """通过 ESC 键关闭大图预览"""
        self.page.keyboard.press("Escape")
    
    def close_lightbox_by_button(self):
        """通过关闭按钮关闭大图预览"""
        self.page.locator(self.lightbox_close).click()
    
    def close_lightbox_by_overlay(self):
        """通过点击遮罩关闭大图预览"""
        self.page.locator(self.lightbox_overlay).click()
    
    def click_lightbox_arrow_right(self):
        """大图模式点击右箭头"""
        self.page.locator(self.lightbox_arrow_right).click()
    
    def click_lightbox_arrow_left(self):
        """大图模式点击左箭头"""
        self.page.locator(self.lightbox_arrow_left).click()
    
    def click_detail_arrow_right(self):
        """详情页点击右箭头"""
        self.page.locator(self.arrow_right).click()
    
    def click_detail_arrow_left(self):
        """详情页点击左箭头"""
        self.page.locator(self.arrow_left).click()
    
    def get_lightbox_thumbnail_count(self):
        """获取大图模式缩略图数量"""
        return self.page.locator(self.lightbox_thumbnails).count()
    
    def is_lightbox_thumbnail_nav_visible(self):
        """判断大图模式缩略图翻页箭头是否显示"""
        left_visible = self.page.locator(self.lightbox_thumbnail_arrow_left).is_visible()
        right_visible = self.page.locator(self.lightbox_thumbnail_arrow_right).is_visible()
        return left_visible and right_visible
    
    def click_lightbox_thumbnail_nav_right(self):
        """大图模式点击缩略图区域右翻页箭头"""
        self.page.locator(self.lightbox_thumbnail_arrow_right).click()
    
    def click_lightbox_thumbnail_nav_left(self):
        """大图模式点击缩略图区域左翻页箭头"""
        self.page.locator(self.lightbox_thumbnail_arrow_left).click()
    
    def get_visible_lightbox_thumbnails_range(self):
        """获取大图模式当前可见的缩略图范围（返回索引列表）"""
        # 实现逻辑：检查每个缩略图的可见性
        visible_indices = []
        count = self.get_lightbox_thumbnail_count()
        for i in range(count):
            if self.page.locator(self.lightbox_thumbnails).nth(i).is_visible():
                visible_indices.append(i)
        return visible_indices
```

### 测试用例结构示例

```python
@pytest.mark.case_id_detail_image_tc011
@allure.feature("详情页")
@allure.story("图片区域 - 多图切换")
@allure.title("支持左右箭头按钮循环切换图片")
@allure.severity(allure.severity_level.CRITICAL)
def test_arrow_navigation_with_cycle(page, multi_image_url):
    """TC011: 支持左右箭头按钮循环切换图片"""
    gallery = DetailPageImageGallery(page)
    
    # 进入详情页
    page.goto(multi_image_url)
    page.wait_for_load_state("networkidle")
    
    # 获取图片总数
    total_images = gallery.get_thumbnail_count()
    assert total_images >= 3, "至少需要 3 张图片"
    
    # 测试在第一张时点击左箭头（循环到最后一张）
    assert gallery.get_active_thumbnail_index() == 0, "初始应在第一张"
    gallery.click_detail_arrow_left()
    page.wait_for_timeout(500)  # 等待切换动画
    assert gallery.get_active_thumbnail_index() == total_images - 1, "应循环到最后一张"
    
    # 测试在最后一张时点击右箭头（循环到第一张）
    gallery.click_detail_arrow_right()
    page.wait_for_timeout(500)
    assert gallery.get_active_thumbnail_index() == 0, "应循环回第一张"


@pytest.mark.case_id_detail_image_tc013
@allure.feature("详情页")
@allure.story("图片区域 - 大图模式")
@allure.title("大图模式主图支持左右箭头循环翻页")
@allure.severity(allure.severity_level.CRITICAL)
def test_lightbox_arrow_navigation_with_cycle(page, multi_image_url):
    """TC013: 大图模式主图支持左右箭头循环翻页"""
    gallery = DetailPageImageGallery(page)
    
    # 进入详情页并打开大图
    page.goto(multi_image_url)
    page.wait_for_load_state("networkidle")
    gallery.click_main_image()
    assert gallery.is_lightbox_open(), "大图预览应打开"
    
    # 获取图片总数
    total_images = gallery.get_thumbnail_count()
    
    # 测试循环逻辑
    # 在第一张时点击左箭头 → 应到最后一张
    gallery.click_lightbox_arrow_left()
    page.wait_for_timeout(500)
    # 验证逻辑：可通过缩略图高亮或其他方式验证
    
    # 在最后一张时点击右箭头 → 应回到第一张
    gallery.click_lightbox_arrow_right()
    page.wait_for_timeout(500)
    # 验证回到第一张


@pytest.mark.case_id_detail_image_tc017
@pytest.mark.skipif(
    "not has_7plus_images_post()",
    reason="列表中无 7+ 张图的帖子"
)
@allure.feature("详情页")
@allure.story("图片区域 - 大图模式缩略图翻页")
@allure.title("大图模式缩略图翻页箭头支持循环翻页")
@allure.severity(allure.severity_level.NORMAL)
def test_lightbox_thumbnail_nav_cycle(page, large_image_set_url):
    """TC017: 大图模式缩略图翻页箭头支持逐张滚动和循环翻页（需 8+ 张图）"""
    gallery = DetailPageImageGallery(page)
    
    # 进入详情页并打开大图
    page.goto(large_image_set_url)
    page.wait_for_load_state("networkidle")
    
    total_images = gallery.get_thumbnail_count()
    assert total_images >= 8, "此用例需要至少 8 张图片"
    
    gallery.click_main_image()
    assert gallery.is_lightbox_open(), "大图预览应打开"
    
    # 验证缩略图翻页箭头存在
    assert gallery.is_lightbox_thumbnail_nav_visible(), "应显示缩略图翻页箭头"
    
    # 记录初始可见范围（应该是第 1-7 张）
    initial_range = gallery.get_visible_lightbox_thumbnails_range()
    logger.info(f"初始可见缩略图范围: {initial_range}")
    assert len(initial_range) == 7, "初始应显示 7 张缩略图"
    assert initial_range == list(range(0, 7)), "初始应显示第 1-7 张（索引 0-6）"
    
    # 第一次点击右翻页箭头，应该向左滚动一张，显示第 2-8 张
    gallery.click_lightbox_thumbnail_nav_right()
    page.wait_for_timeout(500)  # 等待滚动动画
    range_after_1_click = gallery.get_visible_lightbox_thumbnails_range()
    logger.info(f"点击右箭头 1 次后可见范围: {range_after_1_click}")
    assert range_after_1_click == list(range(1, 8)), "应显示第 2-8 张（索引 1-7）"
    
    # 第二次点击右翻页箭头，应该再向左滚动一张，显示第 3-9 张
    gallery.click_lightbox_thumbnail_nav_right()
    page.wait_for_timeout(500)
    range_after_2_clicks = gallery.get_visible_lightbox_thumbnails_range()
    logger.info(f"点击右箭头 2 次后可见范围: {range_after_2_clicks}")
    assert range_after_2_clicks == list(range(2, 9)), "应显示第 3-9 张（索引 2-8）"
    
    # 测试循环：连续点击右箭头直到超过最后一张
    clicks_needed = total_images - 2  # 已经点击了 2 次，需要点击到超过最后一张
    for i in range(clicks_needed):
        gallery.click_lightbox_thumbnail_nav_right()
        page.wait_for_timeout(500)
    
    # 此时应该循环回到显示第 1-7 张
    final_range = gallery.get_visible_lightbox_thumbnails_range()
    logger.info(f"循环后可见范围: {final_range}")
    assert final_range == list(range(0, 7)), "应循环回到第 1-7 张"
    
    # 测试反向：点击左翻页箭头
    gallery.click_lightbox_thumbnail_nav_left()
    page.wait_for_timeout(500)
    range_after_left = gallery.get_visible_lightbox_thumbnails_range()
    logger.info(f"点击左箭头后可见范围: {range_after_left}")
    # 应该显示最后 7 张（例如 10 张图时显示 3-9，即索引 3-9）
    expected_left = list(range(total_images - 7, total_images))
    assert range_after_left == expected_left, f"应循环到最后 7 张（索引 {expected_left}）"
```

### 辅助函数

```python
def has_7plus_images_post():
    """
    检查测试数据中是否有 7+ 张图的帖子
    在 conftest.py 或测试数据准备模块中实现
    """
    # 实现逻辑：扫描测试数据文件或数据库
    # 返回 True/False
    pass
```

---

## 阶段五：性能指标

### 关键性能指标
- 图片加载时间：< 2s（主图）
- 缩略图加载时间：< 3s（全部）
- 图片切换响应时间：< 200ms
- 预览弹层打开时间：< 300ms

### 兼容性要求
- 浏览器：Chrome 90+, Safari 14+, Firefox 88+
- 设备：Desktop (1440×900), Tablet (768×1024)
- 网络：3G/4G/WiFi 环境下均需正常加载

---

## 附录：常见问题

### Q1: 如何判断是单图还是多图模式？
A: 可通过缩略图容器的存在性判断，或通过 API 返回的图片数量判断。

### Q2: 图片懒加载如何测试？
A: 使用 Playwright 的 `page.evaluate()` 监听图片 IntersectionObserver 回调。

### Q3: 预览弹层的关闭动画会影响测试吗？
A: 需要在关闭后等待动画完成（`wait_for_load_state` 或 `wait_for_timeout`）。

---

**文档状态**: ✅ 已完成  
**最后更新**: 2026-03-26  
**维护人**: QA Team
