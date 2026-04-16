# AE站 Marketplace 列表页自动化测试套件

> **项目**: OK AE站 UI自动化测试  
> **模块**: Marketplace 二手列表页  
> **生成时间**: 2026-03-23  
> **框架**: Pytest + Playwright + Allure

---

# AE站 Marketplace 列表页自动化测试套件

> **项目**: OK AE站 UI自动化测试  
> **模块**: Marketplace 二手列表页  
> **更新时间**: 2026-04-01  
> **框架**: Pytest + Playwright + Allure

---

## 📋 测试用例覆盖度

### 总体覆盖情况
| 状态 | 数量 | 百分比 |
|------|------|--------|
| ✅ 已实现 | 60/60 | **100%** |
| 🔴 未实现 | 0/60 | 0% |

**用例文档**: 
- 基准版: [ok-ae-Marketplace-ListPage-测试用例-20260323.md](./ok-ae-Marketplace-ListPage-测试用例-20260323.md) (TC001-TC025)
- 扩展版: [ok-ae-Marketplace-ListPage-测试用例-扩展版-20260401.md](./ok-ae-Marketplace-ListPage-测试用例-扩展版-20260401.md) (TC001-TC060)

---

## 🗂️ 测试脚本组织结构

### 📦 测试脚本列表（4个文件，60个用例）

#### 1️⃣ 冒烟测试套件
**文件**: `test_ae_marketplace_full.py`  
**用例数**: 7个  
**用途**: 快速验证核心功能路径，适合CI/CD快速回归

**覆盖用例**:
- ✅ TC001: 从首页金刚位进入Marketplace
- ✅ TC003: 搜索关键词
- ✅ TC007: 打开筛选面板
- ✅ TC012: 切换排序方式
- ✅ TC017: 点击卡片跳转详情
- ✅ TC018: 已登录收藏商品
- ✅ TC022: 点击下一页

**执行时间**: 约 8-10 分钟  
**优先级**: P0（冒烟测试）

---

#### 2️⃣ 页面进入 + 搜索功能测试
**文件**: `test_ae_marketplace_list_basic.py`  
**用例数**: 19个（原6个 + 新增13个）

**覆盖用例**:

**A. 页面进入与基础展示**:
- ✅ TC001: 从首页金刚位进入Marketplace
- ✅ TC002: 列表页默认状态检查
- ✅ TC026: 直接访问列表页URL（深度链接）
- ✅ TC027: 空列表状态检查
- ✅ TC028: 单条商品展示
- ✅ TC029: 页面加载性能检查
- ✅ TC030: 页面骨架屏/加载动画

**B. 搜索功能**:
- ✅ TC003: 搜索框输入关键词并提交
- ✅ TC004: 搜索无结果关键词
- ✅ TC005: 清空搜索关键词
- ✅ TC006: 搜索特殊字符
- ✅ TC031: 搜索关键词长度边界测试
- ✅ TC032: 搜索建议/自动完成功能
- ✅ TC033: 搜索历史记录
- ✅ TC034: 搜索结果高亮显示
- ✅ TC035: 搜索与筛选组合
- ✅ TC036: 搜索结果相关性排序
- ✅ TC037: 搜索防抖（Debounce）
- ✅ TC038: 多语言搜索

**执行时间**: 约 15-20 分钟

---

#### 3️⃣ 筛选 + 排序功能测试
**文件**: `test_ae_marketplace_filter_sort.py`  
**用例数**: 16个（原8个 + 新增8个）

**覆盖用例**:

**C. 筛选功能**:
- ✅ TC007: 打开筛选器面板
- ✅ TC008: 选择分类筛选
- ✅ TC009: 价格区间筛选
- ✅ TC010: 多条件组合筛选
- ✅ TC011: 清除筛选条件
- ✅ TC039: 价格输入边界值测试
- ✅ TC040: 位置筛选（多级联动）
- ✅ TC041: 筛选器重置功能
- ✅ TC042: 筛选条件计数显示
- ✅ TC043: Transaction筛选（交易方式）
- ✅ TC044: 筛选器收起/展开动画

**D. 排序功能**:
- ✅ TC012: 切换排序方式 - 最新优先
- ✅ TC013: 切换排序方式 - 价格从低到高
- ✅ TC014: 排序与筛选组合
- ✅ TC045: 排序保留搜索和筛选条件
- ✅ TC046: 排序选项选中状态显示

**执行时间**: 约 18-22 分钟

---

#### 4️⃣ 卡片 + 收藏 + 分页功能测试
**文件**: `test_ae_marketplace_card_favorite_pagination.py`  
**用例数**: 19个（原11个 + 新增8个）

**覆盖用例**:

**E. 商品卡片与收藏**:
- ✅ TC015: 查看商品卡片信息
- ✅ TC016: 卡片Hover效果
- ✅ TC017: 点击卡片跳转详情
- ✅ TC018: 已登录状态收藏商品
- ✅ TC019: 取消收藏
- ✅ TC020: 未登录状态点击收藏
- ✅ TC021: 收藏按钮防重复点击
- ✅ TC047: 商品卡片图片加载
- ✅ TC048: 商品卡片发布时间
- ✅ TC049: 商品卡片交易标签
- ✅ TC050: 商品卡片悬停效果

**F. 分页与异常流**:
- ✅ TC022: 点击下一页
- ✅ TC023: 跳转到指定页码
- ✅ TC024: 筛选后刷新页面保持状态
- ✅ TC025: 后退按钮测试
- ✅ TC051: 翻页保留筛选条件
- ✅ TC052: 分页器页码显示
- ✅ TC053: 翻页自动滚动到顶部
- ✅ TC054: 分页URL直接访问

**执行时间**: 约 20-25 分钟

---

#### 5️⃣ 性能与兼容性测试
**文件**: `test_ae_marketplace_performance_compatibility.py`  
**用例数**: 6个（全新）

**覆盖用例**:

**G. 图片与媒体**:
- ✅ TC055: 图片懒加载
- ✅ TC056: 图片响应式尺寸
- ✅ TC057: 图片加载失败占位

**H. 响应式与兼容性**:
- ✅ TC058: 移动端响应式布局
- ✅ TC059: 平板端响应式布局
- ✅ TC060: 跨浏览器兼容性

**执行时间**: 约 6-8 分钟

---

## 🚀 快速开始

### 1. 环境准备
```bash
# 安装依赖
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install chromium
```

### 2. 配置说明
测试账号配置已内置在脚本中：
```python
{
    "site": "ae",
    "base_url": "https://ae.58v5.cn",
    "test_account": {
        "username": "wangyongli@58.com",
        "password": "Qwer1234"
    }
}
```

### 3. 执行策略

#### 场景1: 快速冒烟测试（CI/CD）
```bash
# 执行冒烟测试（约10分钟）
pytest test_cases/marketplace/test_ae_marketplace_full.py -m smoke -v -s \
  --alluredir=reports/allure-results

# 或使用执行脚本
./test_cases/marketplace/run_tests.sh smoke

# 生成Allure报告
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

#### 场景2: 完整回归测试（全部60个用例）
```bash
# 使用执行脚本（推荐，包含所有4个测试文件）
./test_cases/marketplace/run_tests.sh full

# 或手动执行所有测试文件
pytest test_cases/marketplace/test_ae_marketplace_list_basic.py -v -s --alluredir=reports/allure-results
pytest test_cases/marketplace/test_ae_marketplace_filter_sort.py -v -s --alluredir=reports/allure-results
pytest test_cases/marketplace/test_ae_marketplace_card_favorite_pagination.py -v -s --alluredir=reports/allure-results
pytest test_cases/marketplace/test_ae_marketplace_performance_compatibility.py -v -s --alluredir=reports/allure-results

# 生成报告
allure generate reports/allure-results -o reports/allure-report --clean
```

#### 场景3: 按功能模块执行
```bash
# 页面进入+搜索功能（19个用例）
./test_cases/marketplace/run_tests.sh basic

# 筛选+排序功能（16个用例）
./test_cases/marketplace/run_tests.sh filter

# 卡片+收藏+分页功能（19个用例）
./test_cases/marketplace/run_tests.sh card

# 性能与兼容性测试（6个用例）
./test_cases/marketplace/run_tests.sh performance
```

#### 场景4: 按优先级执行
```bash
# 仅执行P0用例
pytest test_cases/marketplace/ -m p0 -v -s

# 或使用执行脚本
./test_cases/marketplace/run_tests.sh p0

# 仅执行P1用例
pytest test_cases/marketplace/ -m p1 -v -s

# 或使用执行脚本
./test_cases/marketplace/run_tests.sh p1

# 执行P0+P1用例
pytest test_cases/marketplace/ -m "p0 or p1" -v -s
```

#### 场景5: 按功能特性执行
```bash
# 仅执行性能测试
pytest test_cases/marketplace/ -m performance -v -s

# 仅执行兼容性测试
pytest test_cases/marketplace/ -m compatibility -v -s

# 仅执行国际化测试
pytest test_cases/marketplace/ -m i18n -v -s
```

---

## 📊 测试用例详细清单

### 📂 第一部分：原有功能测试（TC001-TC025）

### A. 页面进入与基础展示 (2个)
| 用例ID | 标题 | 优先级 | 脚本位置 |
|--------|------|--------|---------|
| TC001 | 从首页金刚位进入Marketplace列表页 | P0 | list_basic, full |
| TC002 | 列表页默认状态检查 | P0 | list_basic |

### B. 搜索功能 (4个)
| 用例ID | 标题 | 优先级 | 脚本位置 |
|--------|------|--------|---------|
| TC003 | 搜索框输入关键词并提交 | P0 | list_basic, full |
| TC004 | 搜索无结果关键词 | P1 | list_basic |
| TC005 | 清空搜索关键词 | P1 | list_basic |
| TC006 | 搜索特殊字符 | P2 | list_basic |

### C. 筛选功能 (5个)
| 用例ID | 标题 | 优先级 | 脚本位置 |
|--------|------|--------|---------|
| TC007 | 打开筛选器面板 | P0 | filter_sort, full |
| TC008 | 选择分类筛选 | P0 | filter_sort |
| TC009 | 价格区间筛选 | P1 | filter_sort |
| TC010 | 多条件组合筛选 | P1 | filter_sort |
| TC011 | 清除筛选条件 | P1 | filter_sort |

### D. 排序功能 (3个)
| 用例ID | 标题 | 优先级 | 脚本位置 |
|--------|------|--------|---------|
| TC012 | 切换排序方式 - 最新优先 | P1 | filter_sort, full |
| TC013 | 切换排序方式 - 价格从低到高 | P1 | filter_sort |
| TC014 | 排序与筛选组合 | P1 | filter_sort |

### E. 商品卡片与收藏 (7个)
| 用例ID | 标题 | 优先级 | 脚本位置 |
|--------|------|--------|---------|
| TC015 | 查看商品卡片信息 | P0 | card_favorite_pagination |
| TC016 | 卡片Hover效果 | P2 | card_favorite_pagination |
| TC017 | 点击卡片跳转详情 | P0 | card_favorite_pagination, full |
| TC018 | 已登录状态收藏商品 | P0 | card_favorite_pagination, full |
| TC019 | 取消收藏 | P1 | card_favorite_pagination |
| TC020 | 未登录状态点击收藏 | P1 | card_favorite_pagination **【新增】** |
| TC021 | 收藏按钮防重复点击 | P2 | card_favorite_pagination |

### F. 分页与异常流 (4个)
| 用例ID | 标题 | 优先级 | 脚本位置 |
|--------|------|--------|---------|
| TC022 | 点击下一页 | P1 | card_favorite_pagination, full |
| TC023 | 跳转到指定页码 | P2 | card_favorite_pagination |
| TC024 | 筛选后刷新页面保持状态 | P1 | card_favorite_pagination |
| TC025 | 后退按钮测试 | P1 | card_favorite_pagination |

---

## 📈 质量保障

### 1. Pytest 标记 (Markers)
所有用例已添加以下标记，方便灵活执行：
```python
@pytest.mark.smoke        # 冒烟测试
@pytest.mark.p0          # P0优先级
@pytest.mark.p1          # P1优先级
@pytest.mark.p2          # P2优先级
@pytest.mark.ae          # AE站点
@pytest.mark.marketplace # 模块标记
@pytest.mark.regression  # 回归测试
```

### 2. Allure 报告集成
所有用例包含：
- ✅ Feature/Story分类
- ✅ 严重级别标记
- ✅ 步骤详细说明
- ✅ 截图附件
- ✅ 用例描述

### 3. 日志记录
所有用例包含详细的日志输出：
```python
logger.info("=" * 80)
logger.info("TC001: 从首页金刚位进入Marketplace列表页")
logger.info("=" * 80)
logger.info("✓ 已登录AE站")
logger.info("✅ TC001 测试通过！")
```

---

## 🛠️ 故障排查

### 常见问题

#### 1. 登录失败
**现象**: 测试用例在登录步骤失败

**解决方案**:
```bash
# 检查账号是否正常
# 手动访问 https://ae.58v5.cn 并登录验证

# 检查session文件是否过期
rm -rf auth_state_ae_*.json

# 重新执行测试
pytest test_cases/marketplace/test_ae_marketplace_list_basic.py::test_tc001_enter_marketplace_from_homepage -v -s
```

#### 2. 选择器失效
**现象**: 元素定位失败

**解决方案**:
```python
# 页面结构可能变更，需要更新选择器
# 打开 pages/marketplace_list_page_ae.py
# 根据最新页面结构调整定位器
```

#### 3. 测试数据不足
**现象**: TC022/TC023分页测试失败（数据不足）

**解决方案**:
```python
# 这是预期行为，测试会自动跳过
# 或在测试环境准备足够的测试数据（>20条商品）
```

---

## 📝 维护指南

### 1. 新增测试用例
```python
# 在对应的测试文件中添加新用例
# 例如：test_ae_marketplace_filter_sort.py

@pytest.mark.case_id_ae_marketplace_tc026  # 使用新的TC编号
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.ae
@pytest.mark.marketplace
@allure.feature("OK")
@allure.story("AE站Marketplace - 新功能")
@allure.title("TC026: 新功能测试")
@allure.severity(allure.severity_level.NORMAL)
def test_tc026_new_feature(page, config):
    """TC026: 新功能测试描述"""
    # 实现测试逻辑
    pass
```

### 2. 更新选择器
```python
# 打开 pages/marketplace_list_page_ae.py
# 找到对应的方法，更新选择器

def click_favorite_button(self, index: int = 0):
    """点击收藏按钮"""
    # 旧选择器（如果失效）
    # favorite_btn = self.page.locator('.favorite-btn').nth(index)
    
    # 新选择器（根据实际页面更新）
    favorite_btn = self.page.get_by_role('button', name='Favorite').nth(index)
    favorite_btn.click()
```

### 3. 添加新的Page Object
如果页面结构变化较大，可以创建新版本的Page对象：
```python
# pages/marketplace_list_page_ae_v2.py
class MarketplaceListPageAeV2:
    """Marketplace列表页 - 新版本"""
    # 实现新的定位器和方法
```

---

## 🔗 相关文档

- [测试用例文档](./ok-ae-Marketplace-ListPage-测试用例-20260323.md)
- [Page Object - MarketplaceListPageAe](../../pages/marketplace_list_page_ae.py)
- [项目README](../../README.md)
- [Pytest文档](https://docs.pytest.org/)
- [Playwright文档](https://playwright.dev/python/)
- [Allure报告文档](https://docs.qameta.io/allure/)

---

## 📞 联系方式

**维护者**: QA Team  
**更新时间**: 2026-03-23  
**版本**: v1.0.0

---

**祝测试顺利！🎉**
