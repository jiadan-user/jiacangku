# AE站 Marketplace Sell Similar 功能测试报告

## 📋 测试概览

**生成时间**: 2026-04-09  
**测试站点**: AE (https://ae.58v5.cn)  
**测试角色**: Buyer (买家)  
**测试账号**: wangyongli@58.com  
**生成方式**: playwright-test-generator (CLI 录制 + Python 代码生成)

---

## 🎯 测试目标

验证 AE 站 Marketplace 二手详情页的 "Sell Similar" (想卖同款) 功能:
1. 非本人帖子详情页应展示 "Sell Similar" 按钮
2. 点击 "Sell Similar" 按钮应跳转到发布页面

---

## 📊 测试结果

### 总体统计

| 指标 | 数量 |
|------|------|
| 测试用例总数 | 2 |
| 通过 | 2 ✅ |
| 失败 | 0 |
| 通过率 | 100% |

### 用例详情

#### ✅ TC001: 非本人帖详情页展示 Sell Similar 按钮

**优先级**: P0 (Critical)  
**测试类型**: 正向功能测试

**测试步骤**:
1. 确保已登录 AE 站
2. 访问 Marketplace 列表页
3. 点击第一个非本人商品卡片进入详情页
4. 验证详情页加载成功
5. 验证不展示 Withdraw 按钮(非本人帖特征)
6. 验证不展示 Edit 按钮(非本人帖特征)
7. 验证展示 Contact 按钮(非本人帖特征)
8. 验证展示 Sell Similar 按钮(核心功能)

**预期结果**: 
- 非本人帖详情页应展示 "Sell Similar" 按钮
- 不应展示 "Withdraw" 和 "Edit" 按钮
- 应展示 "Contact" 按钮

**实际结果**: ✅ PASSED

**关键验证点**:
```python
# 验证非本人帖特征
assert not detail_page.is_withdraw_button_visible()  # ✓
assert not detail_page.is_edit_button_visible()      # ✓
assert detail_page.is_contact_button_visible()       # ✓

# 验证核心功能
assert sell_similar_page.is_sell_similar_button_visible()  # ✓
```

---

#### ✅ TC002: 点击 Sell Similar 按钮跳转发布页

**优先级**: P1 (Critical)  
**测试类型**: 正向功能测试

**测试步骤**:
1. 确保已登录 AE 站
2. 访问 Marketplace 列表页并进入详情页
3. 验证 Sell Similar 按钮可见
4. 点击 Sell Similar 按钮
5. 等待页面跳转
6. 验证成功跳转到发布页

**预期结果**: 
- 点击 "Sell Similar" 按钮后应跳转到发布页
- 发布页 URL 应包含 "/publish/"
- 页面标题应包含 "Post"

**实际结果**: ✅ PASSED

**关键验证点**:
```python
# 验证跳转成功
assert sell_similar_page.is_publish_page_loaded()  # ✓

# 验证 URL 和标题
assert "/publish/" in current_url.lower()  # ✓
assert "post" in page_title.lower()        # ✓
```

**实际跳转 URL**: `https://aepub.58v5.cn/biz/en/publish/classified?id=2042181746522443777`

---

## 🔧 技术实现

### 录制过程

使用 `playwright-cli` 进行真实浏览器交互录制:

```bash
# 打开浏览器
playwright-cli open https://ae.58v5.cn/en/city-abu-dhabi/cate-marketplace/

# 登录流程
playwright-cli click e37  # 点击 "Log in / Register"
playwright-cli fill e43 "wangyongli@58.com"  # 输入邮箱
playwright-cli click e44  # 点击 "Continue"
playwright-cli fill e45 "Qwer1234"  # 输入密码
playwright-cli click e46  # 点击 "Log in"

# 进入详情页并点击 Sell Similar
playwright-cli click e123  # 点击商品卡片
playwright-cli click e234  # 点击 "Sell Similar" 按钮
```

### 生成的 Playwright 代码

**录制的 JavaScript 代码**:
```javascript
await page.goto('https://ae.58v5.cn/en/city-abu-dhabi/cate-marketplace/');
await page.getByText('Log in / Register').click();
await page.getByRole('textbox', { name: 'Email or phone number' }).fill('wangyongli@58.com');
await page.getByRole('button', { name: 'Continue' }).click();
await page.getByRole('textbox', { name: 'Enter password' }).fill('Qwer1234');
await page.getByRole('button', { name: 'Log in' }).click();
await page.getByRole('link', { name: '123 AED 100' }).click();
await page.getByText('Sell Similar').click();
```

**转换的 Python 代码**:
```python
page.goto("https://ae.58v5.cn/en/city-abu-dhabi/cate-marketplace/")
page.get_by_text("Log in / Register").click()
page.get_by_role("textbox", name="Email or phone number").fill("wangyongli@58.com")
page.get_by_role("button", name="Continue").click()
page.get_by_role("textbox", name="Enter password").fill("Qwer1234")
page.get_by_role("button", name="Log in").click()
page.get_by_role("link", name="123 AED 100").click()
page.get_by_text("Sell Similar").click()
```

### Page Object 设计

#### MarketplaceSellSimilarPageAe

```python
class MarketplaceSellSimilarPageAe(BasePage):
    """AE站 Marketplace Sell Similar 功能页面对象"""
    
    def is_sell_similar_button_visible(self, timeout=5000):
        """检查 Sell Similar 按钮是否可见"""
        
    def click_sell_similar_button(self):
        """点击 Sell Similar 按钮"""
        
    def is_publish_page_loaded(self, timeout=10000):
        """检查是否成功进入发布页"""
        
    def get_current_url(self):
        """获取当前页面 URL"""
```

---

## 🐛 调试过程

### 问题1: 选择器冲突 - 多元素匹配

**现象**: 
```
TimeoutError: Locator.wait_for: Timeout 15000ms exceeded.
locator resolved to hidden <a class="ThirdLinkageDropdown_dropdownItemLabel__IaQcf" 
href="https://ae.58v5.cn/en/city-abu-dhabi/cate-jobs/">Jobs</a>
```

**原因**: 
选择器 `a[href*="/cate-"]` 匹配到了隐藏的下拉菜单中的链接,而不是列表页的商品卡片。

**解决方案**:
使用 `MarketplaceListPageAe.get_first_detail_listing_link_href()` 方法,该方法会:
1. 过滤掉隐藏元素
2. 排除筛选区内的链接
3. 只返回真正的商品详情链接

```python
# ❌ 错误写法
first_card_link = page.locator('a[href*="/cate-"]').first
first_card_link.click()

# ✅ 正确写法
first_href = list_page.get_first_detail_listing_link_href()
detail_url = urljoin(page.url, first_href)
page.goto(detail_url, wait_until="domcontentloaded", timeout=30000)
```

### 问题2: Sell Similar 按钮不可见

**现象**: 
第二次运行 TC001 时失败,按钮检测不到。

**原因**: 
按钮可能在页面下方,需要滚动到可见区域。

**解决方案**:
在检测和点击前先滚动到元素位置:

```python
def is_sell_similar_button_visible(self, timeout=5000):
    try:
        sell_btn = self.page.get_by_text("Sell Similar").first
        # 先滚动到元素位置
        sell_btn.scroll_into_view_if_needed(timeout=3000)
        self.page.wait_for_timeout(500)
        return sell_btn.is_visible(timeout=timeout)
    except Exception:
        return False
```

---

## 📝 关键学习点

### 1. 避免全局选择器冲突

**问题**: 使用 `a[href*="/cate-"]` 这样的全局选择器会匹配到隐藏的导航菜单。

**最佳实践**:
- 使用 Page Object 提供的方法,这些方法已经处理了多元素冲突
- 如果必须使用选择器,添加 `.filter(visible=True)` 过滤可见元素
- 限定搜索范围,如 `page.locator("main").get_by_text(...)`

### 2. 元素可见性检测

**问题**: 元素存在但不在可视区域,导致 `is_visible()` 返回 False。

**最佳实践**:
- 在检测可见性前先 `scroll_into_view_if_needed()`
- 给滚动操作留出时间 `wait_for_timeout(500)`

### 3. 登录状态管理

**最佳实践**:
- 使用 `ensure_ae_logged_in()` helper 函数统一管理登录
- 利用 SessionManager 复用登录状态,避免每个测试都重新登录
- 第一次登录后保存 Session,后续测试直接加载

### 4. 录制选择器的使用

**录制时的选择器**:
```javascript
page.getByText('Sell Similar')
page.getByRole('button', { name: 'Continue' })
page.getByRole('textbox', { name: 'Email or phone number' })
```

**转换为 Python**:
```python
page.get_by_text("Sell Similar")
page.get_by_role("button", name="Continue")
page.get_by_role("textbox", name="Email or phone number")
```

**优势**:
- 语义化选择器,更稳定
- 不依赖 CSS 类名或 XPath
- 录制时已经过真实浏览器验证

---

## 📂 生成的文件

### 测试脚本
- `test_cases/marketplace/test_ae_marketplace_sell_similar.py` (主测试文件)

### Page Object
- `pages/marketplace_sell_similar_page_ae.py` (Sell Similar 功能页面对象)

### 测试用例文档
- `test_cases/marketplace/sell_similar_test_cases.md` (Markdown 格式测试用例)

### 测试报告
- `test_cases/marketplace/SELL_SIMILAR_TEST_REPORT.md` (本文件)

---

## ✅ 结论

**测试状态**: 全部通过 ✅

**功能验证**:
1. ✅ 非本人帖详情页正确展示 "Sell Similar" 按钮
2. ✅ 点击 "Sell Similar" 按钮成功跳转到发布页
3. ✅ 非本人帖不展示 "Withdraw" 和 "Edit" 按钮
4. ✅ 非本人帖正确展示 "Contact" 按钮

**代码质量**:
- ✅ 遵循 SCRIPT_SPEC.md 规范
- ✅ 使用 Page Object Model 架构
- ✅ 使用录制的语义化选择器
- ✅ 包含详细的 Allure 注解
- ✅ 完善的日志记录
- ✅ 健壮的错误处理

**可维护性**:
- ✅ 代码结构清晰,易于理解
- ✅ 复用现有的 helper 函数和 Page Object
- ✅ Session 管理优化,提高执行效率

---

## 🚀 后续建议

### 可选的扩展测试用例

1. **TC003: 本人帖详情页不展示 Sell Similar 按钮**
   - 验证本人发布的帖子不应展示 "Sell Similar" 按钮
   - 需要创建测试数据(发布一个商品)

2. **TC004: Sell Similar 预填充数据验证**
   - 验证进入发布页后,商品信息是否正确预填充
   - 验证标题、价格、描述等字段

3. **TC005: 未登录用户点击 Sell Similar**
   - 验证未登录用户点击按钮后的行为
   - 应该跳转到登录页或显示登录弹窗

### 性能优化

1. 考虑使用 `@pytest.mark.parametrize` 参数化测试不同站点
2. 使用 `pytest-xdist` 并行执行测试用例
3. 优化 Session 复用策略,减少登录次数

---

**报告生成时间**: 2026-04-09 18:04:09  
**生成工具**: playwright-test-generator v1.0  
**测试框架**: Playwright + Pytest + Allure
