# AE 站（阿联酋站）Jobs 列表页 - Location 与 Add Job Preferences 入口验证

**录制站点**: AE (https://ae.58v5.cn)  
**录制城市**: Abu Dhabi  
**录制日期**: 2026-03-09  
**录制状态**: ✅ 实测通过  
**测试角色**: 访客（未登录）  
**用例数量**: 2 条

---

## 测试环境配置

| 字段 | 值 |
|------|---|
| 站点 | ae |
| 站点名称 | 阿联酋站 |
| 基础URL | https://ae.58v5.cn |
| 首页URL | https://ae.58v5.cn/en/city-abu-dhabi/ |
| Jobs列表URL | https://ae.58v5.cn/en/city-abu-dhabi/cate-jobs/?iconSource=jobs |
| 角色 | visitor |
| 账号名称 | unauthenticated |
| 测试账号 | 无需登录 |
| 测试密码 | 无需登录 |

---

## Application Overview - AE 站 Jobs 功能

### 功能定位
从 AE 站首页 Jobs 金刚位进入招聘列表页，用户可浏览招聘信息并通过筛选器查找职位。未登录用户可看到 **Add Job Preferences** 引导入口，用于创建求职偏好。

### 录制发现（2026-03-09 实测）

#### ✅ 首页成功录制
- **URL**: `https://ae.58v5.cn/en/city-abu-dhabi/`
- **Jobs 金刚位**: 
  - **选择器**: `page.get_by_role('link', { name: 'Jobs Jobs' })`  
  - **ref**: `e51`
  - **点击后跳转**: `https://ae.58v5.cn/en/city-abu-dhabi/cate-jobs/?iconSource=jobs`

![AE首页-Jobs金刚位](ae-home-page-jobs-icon.png)

#### ✅ Jobs 列表页正常加载
- **URL**: `https://ae.58v5.cn/en/city-abu-dhabi/cate-jobs/?iconSource=jobs`
- **页面标题**: "Abu Dhabi Jobs Job Listings - OK"
- **加载状态**: 正常，无 500 错误

![Jobs列表页](ae-jobs-list-page.png)

### 页面结构（MCP 实测 - 2026-03-09）

#### 筛选器区域
| 筛选器 | 默认值 | 说明 |
|--------|--------|------|
| **Location** | **Abu Dhabi** | 显示当前城市，点击可切换 |
| Job Type | （空） | 未选择 |
| Workplace type | （空） | 未选择 |
| Salary | （空） | 未选择 |
| Reset | 按钮 | 重置所有筛选器 |

#### Location 筛选器详情（点击后弹出面板）
- **面板标题**: "Select Location"
- **搜索框**: "Search City"
- **功能按钮**: "Use current location"（使用当前位置）
- **城市列表**（ref 实测）:
  - All United Arab Emirates（全部阿联酋）
  - Dubai（迪拜）
  - Abu Dhabi（阿布扎比）✅ 当前选中
  - Ras al Khaimah（哈伊马角）
  - Sharjah（沙迦）
  - Fujairah（富查伊拉）
  - Ajman（阿治曼）
  - Umm al Quwain（乌姆盖万）
  - Al Ain（艾因）
  - enhjioujoida

![Location筛选器面板](ae-jobs-location-panel.png)

#### Add Job Preference 入口（未登录状态）
- **位置**: 列表页左侧第一张卡片位置
- **图标**: 绿色图标（带 "+" 号）
- **标题**: "Add Job Preference"
- **副文本**: "Unlock more opportunities tailored for you."
- **选择器**: `page.locator('#istPageFilterArea').get_by_text('Add Job Preference')`
- **ref**: `e61`

![Add Job Preference卡片](ae-jobs-add-preference-card.png)

### 业务规则（实测验证）

1. **Location 筛选器默认状态**: 
   - ✅ **显示具体地址**："Abu Dhabi"（当前访问城市）
   - ✅ **不是空值**
   - ✅ 可点击切换其他城市

2. **Add Job Preferences 入口**: 
   - ✅ 未登录状态下：显示引导卡片
   - ✅ 位置：列表页左侧顶部第一张卡片
   - ✅ 文案包含："Add Job Preference" + 引导副文本

---

## 测试用例

### TC001: Location 筛选器显示具体城市地址

**优先级**: P0  
**测试类型**: 功能 / UI 状态验证  
**自动化可行性**: ✅ 可自动化

**前置条件**:
- 未登录状态
- 浏览器已清除缓存和 cookies
- 访问 Abu Dhabi 城市首页

**测试步骤**:
1. 访问 AE 站首页 `https://ae.58v5.cn/en/city-abu-dhabi/`
2. 等待页面加载完成
3. 定位 Jobs 金刚位（选择器: `page.get_by_role('link', name='Jobs Jobs')`，ref: `e51`）
4. 点击 Jobs 金刚位
5. 等待跳转至 Jobs 列表页（URL 应为 `https://ae.58v5.cn/en/city-abu-dhabi/cate-jobs/?iconSource=jobs`）
6. 定位 Location 筛选器（位于筛选器区域第一个位置）
7. 检查 Location 筛选器显示的文本内容

**预期结果**:
- ✅ 成功跳转至 Jobs 列表页（URL: `https://ae.58v5.cn/en/city-abu-dhabi/cate-jobs/?iconSource=jobs`）
- ✅ 页面标题为 "Abu Dhabi Jobs Job Listings - OK"
- ✅ **Location 筛选器显示具体地址**："Abu Dhabi"
- ✅ **不是空值状态**（不显示占位文本如 "Select location"）
- ✅ Location 筛选器可见且可点击

**实测结果**: ✅ 通过
- Location 筛选器显示文本：`"Abu Dhabi"`（实测 ref: `e38`）
- 选择器：`page.locator('#istPageFilterArea').get_by_text('Abu Dhabi')`
- 点击后弹出城市选择面板（面板标题："Select Location"）

**录制截图**:
- 首页 Jobs 金刚位：`ae-home-page-jobs-icon.png`
- Jobs 列表页筛选区：`ae-jobs-filter-area.png`
- Location 筛选器面板：`ae-jobs-location-panel.png`

---

### TC002: Add Job Preferences 入口在列表页可见

**优先级**: P0  
**测试类型**: 功能 / 入口可见性验证  
**自动化可行性**: ✅ 可自动化

**前置条件**:
- 未登录状态
- 已通过 TC001 进入 Jobs 列表页

**测试步骤**:
1. 在 TC001 基础上，停留在 Jobs 列表页
2. 等待页面完全加载（列表数据渲染完成）
3. 滚动至页面顶部（确保视口包含列表顶部区域）
4. 定位 **Add Job Preference 入口**（左侧第一张卡片）
5. 检查入口的可见性、文案和图标

**预期结果**:
- ✅ **Add Job Preference 入口元素可见**
- ✅ 入口位置：Jobs 列表页左侧顶部第一张卡片位置
- ✅ **入口文案准确**：
  - 标题：`"Add Job Preference"`
  - 副文本：`"Unlock more opportunities tailored for you."`
- ✅ 图标：绿色图标（带 "+" 号）
- ✅ 入口元素可点击（`clickable` 状态）

**实测结果**: ✅ 通过
- 入口卡片可见（实测 ref: `e61`）
- 标题文案：`"Add Job Preference"`（精确匹配）
- 副文本：`"Unlock more opportunities tailored for you."`（精确匹配，带省略号）
- 选择器：
  - 主容器：`page.locator('#istPageFilterArea')`
  - 文本定位：`page.get_by_text('Add Job Preference')`
- 卡片可点击（cursor=pointer）

**录制截图**:
- Jobs 列表页全景：`ae-jobs-list-page.png`
- Add Job Preference 卡片：`ae-jobs-add-preference-card.png`

---

## 实测总结

### ✅ 验证通过项、
1. **Location 筛选器显示具体地址**：显示 "Abu Dhabi"（当前城市），不是空值 ✅
2. **Add Job Preferences 入口可见**：卡片位置、文案、图标均符合预期 ✅

### 🎯 关键发现
- **Location 筛选器行为**：默认显示用户访问的城市（Abu Dhabi），而不是空值状态
- **城市列表完整**：包含 9 个 UAE 城市 + "All United Arab Emirates" 选项
- **Add Job Preference 卡片位置**：位于列表左侧顶部第一张，非常显眼

### 📊 与 SG 站对比
| 项目 | SG 站 | AE 站 |
|------|-------|-------|
| Jobs 列表页状态 | ✅ 正常 | ✅ 正常（之前 500 错误已修复） |
| Location 筛选器默认值 | Singapore（具体城市） | Abu Dhabi（具体城市） ✅ |
| Add Job Preference 入口 | ✅ 可见 | ✅ 可见 |
| 文案一致性 | "Unlock more opportunities tailored for you." | 相同 ✅ |

---

## 参考文档

### SG 站相同功能已验证（对比参考）
- **文档**: `test_cases/zhaopin/ok-sg-JobPreferences-AddFromList-测试用例-20260305.md`
- **脚本**: `test_cases/zhaopin/test_sg_job_preferences_add_from_list.py`
- **验证状态**: ✅ 8/8 测试全部通过（2026-03-09）

### AE 站与 SG 站差异点
| 项目 | SG 站 | AE 站 |
|------|-------|-------|
| 货币 | S$ (SGD) | AED |
| 默认城市 | Singapore | Abu Dhabi |
| 城市数量 | 1 个 | 9 个 |

---

## 变更记录

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|---------|------|
| 2026-03-09 | v1.0 | 初始版本：AE 站 Jobs 列表页实测通过，Location 显示具体地址，Add Job Preference 入口可见 | AI QA |

---

**✅ 测试结论**:  
AE 站 Jobs 列表页功能正常，Location 筛选器显示具体城市地址（Abu Dhabi），Add Job Preferences 入口在未登录状态下正常显示。两项验证目标均实测通过。
