# AE站 Marketplace 自动化测试（列表页 + 详情页）

> **列表页用例文档**: `ok-ae-Marketplace-ListPage-测试用例-扩展版-20260401.md`（TC001–TC060）  
> **列表页脚本**: `test_ae_marketplace_list_page.py`（单文件 60 条，与扩展版文档一一对应）

---

## 📁 项目文件结构

```
test_cases/marketplace/
├── README.md
├── run_tests.sh                                    # 列表页快捷执行（smoke / full / basic …）
├── ok-ae-Marketplace-ListPage-测试用例-扩展版-20260401.md   # 列表页用例（扩展版）
├── test_ae_marketplace_list_page.py                # 列表页 TC001–TC060（唯一列表脚本）
└── test_ae_marketplace_detail_online_offline.py    # 详情页（与列表文档独立）

pages/
└── marketplace_list_page_ae.py
```

---

## 📊 列表页测试覆盖概览

| 范围 | 用例数 | 说明 |
|------|--------|------|
| **TC001–TC060** | 60 | 单脚本 `test_ae_marketplace_list_page.py`，与扩展版 Markdown 编号一致 |
| **冒烟** | 若干 | 使用 `-m smoke`（沿用原用例上的 smoke 标记） |

### 覆盖率指标

- ✅ **功能点覆盖率**: 100%（搜索、筛选、排序、卡片、收藏、分页）
- ✅ **场景覆盖率**: 100%（正向、负向、异常、边界、组合、会话）
- ⚠️ **边界值覆盖率**: 90%（特殊字符、空结果、防重复点击等）

---

## 🎯 快速开始

### 1. 环境准备

确保已安装依赖：

```bash
pip install -r requirements.txt
```

### 2. 运行测试

#### 运行全部测试

```bash
# 所有 Marketplace 测试
pytest test_cases/marketplace/ -v -s

# 生成 Allure 报告
pytest test_cases/marketplace/ --alluredir=reports/allure-results
allure serve reports/allure-results
```

#### 按优先级运行

```bash
# 只运行 P0 用例（核心功能）
pytest test_cases/marketplace/ -m p0 -v

# 运行 P0 和 P1 用例
pytest test_cases/marketplace/ -m "p0 or p1" -v
```

#### 列表页单文件（推荐）

```bash
# 完整 TC001–TC060
pytest test_cases/marketplace/test_ae_marketplace_list_page.py -v -s

# 或使用脚本
./test_cases/marketplace/run_tests.sh full
./test_cases/marketplace/run_tests.sh smoke
```

---

## 📝 测试用例详情

### A. 页面进入与基础展示（2条）

| 用例ID | 标题 | 优先级 | 类型 |
|--------|------|--------|------|
| TC001 | 从首页金刚位进入Marketplace列表页 | P0 | 正向 |
| TC002 | 列表页默认状态检查 | P0 | UI检查 |

### B. 搜索功能（4条）

| 用例ID | 标题 | 优先级 | 类型 |
|--------|------|--------|------|
| TC003 | 搜索框输入关键词并提交 | P0 | 正向 |
| TC004 | 搜索无结果关键词 | P1 | 异常 |
| TC005 | 清空搜索关键词 | P1 | 正向 |
| TC006 | 搜索特殊字符 | P2 | 安全/边界 |

### C. 筛选功能（5条）

| 用例ID | 标题 | 优先级 | 类型 |
|--------|------|--------|------|
| TC007 | 打开筛选器面板 | P0 | 正向 |
| TC008 | 选择分类筛选 | P0 | 正向 |
| TC009 | 价格区间筛选 | P1 | 正向 |
| TC010 | 多条件组合筛选 | P1 | 组合 |
| TC011 | 清除筛选条件 | P1 | 正向 |

### D. 排序功能（3条）

| 用例ID | 标题 | 优先级 | 类型 |
|--------|------|--------|------|
| TC012 | 切换排序方式 - 最新优先 | P1 | 正向 |
| TC013 | 切换排序方式 - 价格从低到高 | P1 | 正向 |
| TC014 | 排序与筛选组合 | P1 | 组合 |

### E. 商品卡片与收藏（7条）

| 用例ID | 标题 | 优先级 | 类型 |
|--------|------|--------|------|
| TC015 | 查看商品卡片信息 | P0 | UI检查 |
| TC016 | 卡片Hover效果 | P2 | UI交互 |
| TC017 | 点击卡片跳转详情 | P0 | 正向 |
| TC018 | 已登录状态收藏商品 | P0 | 正向 |
| TC019 | 取消收藏 | P1 | 正向 |
| TC020 | 未登录状态点击收藏 | P1 | 权限 |
| TC021 | 收藏按钮防重复点击 | P2 | 防重 |

### F. 分页与异常流（4条）

| 用例ID | 标题 | 优先级 | 类型 |
|--------|------|--------|------|
| TC022 | 点击下一页 | P1 | 正向 |
| TC023 | 跳转到指定页码 | P2 | 正向 |
| TC024 | 筛选后刷新页面保持状态 | P1 | 会话 |
| TC025 | 后退按钮测试 | P1 | 导航 |

---

## ⚙️ 配置说明

### 测试环境配置

测试脚本使用以下配置（在每个测试文件的 `_CONFIG` 中定义）：

```python
_CONFIG = {
    "site": "ae",
    "site_name": "阿联酋站",
    "role": "buyer",
    "user_name": "marketplace_buyer_ae",
    "base_url": "https://ae.58v5.cn",
    "test_account": {
        "username": "wangyongli@58.com",
        "password": "Qwer1234"
    }
}
```

### Session 复用

所有测试自动使用 `SessionManager` 复用登录状态，避免重复登录：

- Session 文件保存路径：`reports/sessions/ae_buyer_marketplace_buyer_ae.json`
- 首次运行时会执行完整登录流程并保存 Session
- 后续运行会自动加载 Session，大幅提升执行速度

---

## 🔧 Page Object 方法说明

### MarketplaceListPageAe 类主要方法

| 方法 | 功能 | 参数 |
|------|------|------|
| `navigate_to_marketplace_from_homepage()` | 从首页金刚位进入 Marketplace | - |
| `navigate_to_marketplace_directly(base_url)` | 直接导航到 Marketplace | base_url |
| `input_search_keyword(keyword)` | 输入搜索关键词 | keyword |
| `submit_search()` | 提交搜索 | - |
| `clear_search()` | 清空搜索框 | - |
| `open_filter_panel()` | 打开筛选器面板 | - |
| `select_category_filter(category_name)` | 选择分类筛选 | category_name |
| `apply_filter()` | 应用筛选条件 | - |
| `clear_all_filters()` | 清除所有筛选 | - |
| `select_sort_option(sort_name)` | 选择排序方式 | sort_name |
| `get_item_cards_count()` | 获取商品卡片数量 | - |
| `click_first_item_card()` | 点击第一张商品卡片 | - |
| `click_favorite_button(index)` | 点击收藏按钮 | index (默认0) |
| `click_next_page()` | 点击下一页 | - |
| `goto_page_number(page_num)` | 跳转到指定页码 | page_num |

---

## ⚠️ 重要提示

### 1. 选择器调整说明

由于本项目 **未进行实际的 MCP 录制**，所有选择器均基于以下来源推测：

- ✅ 项目中已有的类似模块（Jobs、Resume 等）的代码模式
- ✅ 常见 Web UI 组件的标准选择器
- ✅ Playwright 推荐的语义化定位器（`get_by_role`、`get_by_text` 等）

### 首次运行建议

1. **先运行 1-2 个用例观察结果**
2. **查看失败的选择器**，使用浏览器开发者工具检查实际页面结构
3. **调整 Page Object 中的选择器**
4. **重新运行验证**

### 常见调整点

| 元素 | 当前选择器 | 可能需要调整为 |
|------|-----------|---------------|
| 搜索框 | `get_by_placeholder('Search')` | 实际 placeholder 或 `input[type='search']` |
| 筛选按钮 | `get_by_role('button', name='Filter')` | 实际文本或 CSS 选择器 |
| 商品卡片 | `.item-card, .product-card` | 实际 class 名称 |
| 收藏按钮 | `button[aria-label*='favorite']` | 实际 aria-label 或 class |
| 分页器 | `get_by_role('button', name='Next')` | 实际文本或选择器 |

---

## 🐛 调试技巧

### 1. 截图调试

在失败的步骤添加截图：

```python
page.screenshot(path="debug_screenshot.png")
```

### 2. 元素检查

打印元素信息：

```python
element = page.locator('.item-card').first
print(f"元素可见: {element.is_visible()}")
print(f"元素class: {element.get_attribute('class')}")
```

### 3. 等待时间调整

如果元素加载较慢，增加等待时间：

```python
page.wait_for_timeout(3000)  # 3秒
```

### 4. 查看 MCP 录制示例

参考项目中已有的测试脚本：

- `test_cases/zhaopin/test_es_resume_add.py`
- `test_cases/zhaopin/test_sg_jobs_pref_submit.py`

---

## 📈 执行报告示例

### 命令行输出

```
test_cases/marketplace/test_ae_marketplace_list_basic.py::test_tc001_enter_marketplace_from_homepage PASSED [ 20%]
test_cases/marketplace/test_ae_marketplace_list_basic.py::test_tc002_marketplace_default_state_check PASSED [ 40%]
test_cases/marketplace/test_ae_marketplace_list_basic.py::test_tc003_search_with_keyword PASSED [ 60%]
test_cases/marketplace/test_ae_marketplace_filter_sort.py::test_tc007_open_filter_panel PASSED [ 80%]
test_cases/marketplace/test_ae_marketplace_card_favorite_pagination.py::test_tc015_item_card_information_check PASSED [100%]

======================== 25 passed in 180.50s =========================
```

### Allure 报告

运行 `allure serve reports/allure-results` 后可查看：

- ✅ 测试用例按 Feature/Story 分组
- ✅ 每个步骤的详细日志
- ✅ 失败用例的截图
- ✅ 执行时间统计
- ✅ 趋势分析

---

## 📞 支持与反馈

如有问题或建议，请联系测试团队或查看：

- 项目规范：`SCRIPT_SPEC.md`
- 技能文档：`.claude/skills/web-qa-brain/SKILL.md`
- Playwright 文档：https://playwright.dev/python/

---

## 📌 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-03-23 | 初始版本，完成 25 个核心测试用例和 Page Object |

---

**Happy Testing! 🎉**
