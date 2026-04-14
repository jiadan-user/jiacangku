# 测试数据清理策略

> 如何基于录制的删除操作实现自动清理

## 核心思想

测试用例文档中必然包含"创建"和"删除"用例：
- **创建用例（TC001-TC005）**：录制创建操作
- **删除用例（TC009）**：录制删除操作

**关键洞察**：删除用例的录制操作 = 清理方法的实现

```
优势：
✅ 完全基于UI录制，不依赖API
✅ 删除逻辑与删除测试保持一致
✅ 无需手动编写清理代码
✅ 自动化程度高
```

---

## 识别清理需求

### 用例类型判断

```python
def identify_cleanup_need(case_title: str) -> str:
    """识别用例是否需要清理"""
    
    # 创建类：需要清理
    if any(word in case_title for word in ["创建", "新增", "添加", "create", "add"]):
        # 排除失败场景
        if any(word in case_title for word in ["失败", "错误", "重复", "已存在"]):
            return "NO_CLEANUP"  # 创建失败，无需清理
        return "NEED_CLEANUP"
    
    # 删除类：提取为清理方法
    if any(word in case_title for word in ["删除", "移除", "delete", "remove"]):
        return "IS_CLEANUP_SOURCE"
    
    # 编辑类：需要先创建测试数据
    if any(word in case_title for word in ["编辑", "修改", "更新", "edit", "update"]):
        return "NEED_PREPARE_AND_CLEANUP"
    
    # 查询类：可能需要准备数据
    if any(word in case_title for word in ["搜索", "查询", "筛选", "search", "filter"]):
        return "NEED_PREPARE_DATA"
    
    return "NO_CLEANUP"
```

### 清理需求矩阵

| 用例场景 | 示例标题 | 清理需求 | 处理方式 |
|---------|---------|---------|---------|
| 正向创建 | TC001: 创建项目-完整信息 | ✅ 需要 | 追踪项目名称 |
| 负向创建 | TC003: 创建项目-重复名称 | ❌ 不需要 | 创建失败 |
| 删除功能 | TC009: 删除项目 | ⚠️ 提取方法 | 作为清理源 |
| 编辑功能 | TC006: 编辑项目名称 | ✅ 需要 | 先创建后清理 |
| 搜索功能 | TC017: 搜索项目 | ⚠️ 准备数据 | 批量创建+清理 |

---

## 代码生成策略

### 1. 提取删除方法（从TC009）

**输入**：TC009删除用例的CLI录制
```python
# CLI返回的代码
page.locator('.anticon-more').first.click()
page.locator('.ant-dropdown').get_by_text('删除').click()
page.get_by_role('button', name='确定').click()
```

**输出**：公共清理方法
```python
def _delete_project_by_ui(self, project_name: str):
    """
    通过UI删除项目
    此方法从TC009录制操作自动提取
    
    Args:
        project_name: 项目名称
    """
    with allure.step(f"清理：删除项目 {project_name}"):
        # 定位项目卡片
        project_card = self.page.locator(f'text={project_name}').locator(
            'xpath=ancestor::div[contains(@class, "projectCard")]'
        ).first
        
        # 录制的操作（自动插入）
        project_card.locator('.anticon-more').click()
        self.page.wait_for_timeout(500)
        
        self.page.locator('.ant-dropdown').get_by_text('删除').click()
        self.page.wait_for_timeout(500)
        
        self.page.get_by_role('button', name='确定').click()
        
        # 等待删除成功
        expect(self.page.locator("text=删除成功")).to_be_visible(timeout=3000)
        self.page.wait_for_timeout(1000)
        
        logger.info(f"🧹 已删除: {project_name}")
```

### 2. 生成清理fixture

**自动添加到测试类**：
```python
@pytest.fixture(autouse=True)
def auto_cleanup(self, page: Page):
    """自动清理fixture（自动生成）"""
    self.page = page
    self.created_projects = []  # 追踪创建的项目
    yield
    # 测试后自动清理
    logger.info(f"🧹 开始清理，共{len(self.created_projects)}个项目")
    for project_name in self.created_projects:
        try:
            self._delete_project_by_ui(project_name)
        except Exception as e:
            logger.warning(f"⚠️ 清理失败: {project_name}, {e}")
    logger.info("✅ 清理完成")
```

### 3. 为创建用例添加追踪

**TC001创建测试（自动注入）**：
```python
def test_tc001_create_project(self):
    """TC001: 创建项目"""
    
    # 生成唯一名称
    project_name = f"测试项目_{int(time.time())}"
    
    # === 录制的创建操作（保持不变）===
    with allure.step("创建项目"):
        # ... 录制的代码 ...
    
    # === 验证（保持不变）===
    with allure.step("验证创建成功"):
        expect(self.page.locator("text=创建成功")).to_be_visible()
    
    # 🔥 自动添加追踪（生成时注入）
    self.created_projects.append(project_name)
```

---

## 完整示例

### 测试用例文档结构

```markdown
# 项目管理测试用例

## 一、项目创建核心流程
- TC001: 创建项目-完整信息        ← 需要清理
- TC002: 创建项目-必填项          ← 需要清理
- TC003: 创建项目-重复名称        ← 不需要清理（创建失败）

## 二、项目删除功能
- TC009: 删除项目                ← 提取为清理方法
```

### 生成的测试代码

```python
"""
项目管理测试 - 自动清理版
"""
import time
import pytest
import allure
from playwright.sync_api import Page, expect
from utils.logger import logger

class TestProjectManagement:
    """项目管理测试（自动生成）"""
    
    # === 自动生成的清理fixture ===
    @pytest.fixture(autouse=True)
    def auto_cleanup(self, page: Page, base_url: str):
        """自动清理fixture"""
        self.page = page
        self.base_url = base_url
        self.created_projects = []
        
        # 前置：导航
        page.goto(f"{base_url}/projectManage/")
        page.wait_for_load_state("networkidle")
        
        yield
        
        # 后置：自动清理
        if self.created_projects:
            logger.info(f"🧹 开始清理，共{len(self.created_projects)}个项目")
            for name in self.created_projects:
                try:
                    self._delete_project_by_ui(name)
                except Exception as e:
                    logger.warning(f"⚠️ 清理失败: {name}, {e}")
    
    # === 从TC009提取的清理方法 ===
    def _delete_project_by_ui(self, project_name: str):
        """通过UI删除项目（从TC009提取）"""
        with allure.step(f"删除项目: {project_name}"):
            # 定位项目卡片
            project_card = self.page.locator(f'text={project_name}').locator(
                'xpath=ancestor::div[contains(@class, "projectCard")]'
            ).first
            
            # TC009录制的操作
            project_card.locator('.anticon-more').click()
            self.page.wait_for_timeout(500)
            
            self.page.locator('.ant-dropdown').get_by_text('删除').click()
            self.page.wait_for_timeout(500)
            
            self.page.get_by_role('button', name='确定').click()
            expect(self.page.locator("text=删除成功")).to_be_visible(timeout=3000)
            self.page.wait_for_timeout(1000)
            
            logger.info(f"🧹 已删除: {project_name}")
    
    # === 测试用例 ===
    
    @allure.title("TC001: 创建项目-完整信息")
    @pytest.mark.p0
    def test_tc001_create_complete(self):
        """TC001: 创建项目-完整信息"""
        project_name = f"完整项目_{int(time.time())}"
        
        # 录制的创建操作
        with allure.step("创建项目"):
            self.page.locator('button:has-text("新增项目")').click()
            self.page.get_by_role("textbox", name="项目名称").fill(project_name)
            self.page.get_by_role("textbox", name="项目描述").fill("测试描述")
            self.page.get_by_role("button", name="新 增").click()
        
        # 验证
        with allure.step("验证创建成功"):
            expect(self.page.locator("text=创建成功")).to_be_visible()
        
        # 🔥 自动添加追踪
        self.created_projects.append(project_name)
    
    @allure.title("TC002: 创建项目-必填项")
    @pytest.mark.p0
    def test_tc002_create_required(self):
        """TC002: 创建项目-必填项"""
        project_name = f"必填项_{int(time.time())}"
        
        # 录制的操作...
        
        # 🔥 自动添加追踪
        self.created_projects.append(project_name)
    
    @allure.title("TC003: 创建项目-重复名称")
    @pytest.mark.p0
    @pytest.mark.negative
    def test_tc003_duplicate_name(self):
        """TC003: 创建项目-重复名称（失败场景）"""
        
        # 使用已存在的名称
        project_name = "春节活动"
        
        # 录制的操作...
        
        # 验证错误提示
        expect(self.page.locator("text=项目名称已存在")).to_be_visible()
        
        # ❌ 不追踪（创建失败）
    
    @allure.title("TC009: 删除项目")
    @pytest.mark.p0
    def test_tc009_delete_project(self):
        """TC009: 删除项目（此用例测试删除功能）"""
        
        # 前置：创建测试数据
        test_project = f"待删除_{int(time.time())}"
        with allure.step("准备测试数据"):
            # 快速创建...
            pass
        
        # ❌ 不追踪（测试会删除它）
        
        # 执行删除（这就是被提取的方法）
        self._delete_project_by_ui(test_project)
        
        # 验证
        expect(self.page.locator(f"text={test_project}")).not_to_be_visible()
```

---

## 边界情况处理

### 1. 批量创建场景

**TC017: 搜索功能（需要多个项目）**

```python
def test_tc017_search_projects(self):
    """TC017: 搜索功能"""
    
    # 准备3个测试项目
    test_projects = []
    for i in range(3):
        name = f"搜索测试_{i}_{int(time.time())}"
        # 创建项目...
        test_projects.append(name)
    
    # 追踪所有项目
    self.created_projects.extend(test_projects)
    
    # 测试搜索功能...
```

### 2. 编辑测试场景

**TC006: 编辑项目（需要先创建）**

```python
def test_tc006_edit_project(self):
    """TC006: 编辑项目名称"""
    
    # 前置：创建测试项目
    original_name = f"原始名称_{int(time.time())}"
    with allure.step("准备测试数据"):
        # 创建项目...
        pass
    
    # 追踪原始名称
    self.created_projects.append(original_name)
    
    # 执行编辑
    new_name = f"修改后_{int(time.time())}"
    # 编辑操作...
    
    # 更新追踪（名称已变更）
    self.created_projects.remove(original_name)
    self.created_projects.append(new_name)
```

### 3. 清理失败处理

```python
def _delete_project_by_ui(self, project_name: str):
    """删除项目（带重试）"""
    max_retries = 2
    for attempt in range(max_retries):
        try:
            # 删除操作...
            logger.info(f"🧹 已删除: {project_name}")
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"清理失败，重试中... ({attempt+1}/{max_retries})")
                self.page.wait_for_timeout(1000)
            else:
                logger.error(f"❌ 清理最终失败: {project_name}, {e}")
                return False
```

---

## 最佳实践

### 1. 唯一性命名

```python
# ✅ 使用时间戳确保唯一
project_name = f"测试项目_{int(time.time())}"

# ❌ 避免硬编码名称
project_name = "测试项目"  # 会导致重复
```

### 2. 及时追踪

```python
# ✅ 创建成功后立即追踪
self.page.get_by_role("button", name="新 增").click()
expect(self.page.locator("text=创建成功")).to_be_visible()
self.created_projects.append(project_name)  # 立即追踪

# ❌ 避免延迟追踪
# ... 很多验证代码 ...
self.created_projects.append(project_name)  # 容易忘记
```

### 3. 容错处理

```python
# ✅ 清理失败不影响测试结果
try:
    self._delete_project_by_ui(name)
except Exception as e:
    logger.warning(f"清理失败（不影响测试）: {e}")

# ❌ 避免清理失败导致测试失败
self._delete_project_by_ui(name)  # 异常会传播
```

---

## 常见问题

### Q1: 如果没有删除用例怎么办？

**A**: 如果测试用例文档中没有删除用例，说明删除功能不在测试范围内。此时：
1. 不生成清理代码（累积测试数据）
2. 或建议用户补充删除用例

### Q2: 删除操作很复杂怎么办？

**A**: 复杂的删除操作更适合用UI清理：
- 录制完整的删除流程（包括确认弹窗、二次验证等）
- 提取为清理方法
- 保持与删除测试一致

### Q3: 清理太慢怎么办？

**A**: UI清理比API慢，但优势是：
- 不依赖API文档
- 与UI测试逻辑一致
- 完全自动化

如果确实需要优化：
1. 批量清理（一次性定位多个项目）
2. 减少等待时间
3. 使用API清理（需要手动配置）

---

## 总结

**核心优势**：
1. ✅ **完全自动化** - 无需手动编写清理代码
2. ✅ **基于录制** - 符合skill的核心理念
3. ✅ **逻辑一致** - 删除测试 = 清理方法
4. ✅ **易于维护** - 删除逻辑变更时自动同步

**适用场景**：
- ✅ 创建/编辑类测试（需要清理）
- ✅ 搜索/筛选类测试（需要准备数据）
- ❌ 纯查询类测试（不需要清理）
- ❌ 失败场景测试（不需要清理）
