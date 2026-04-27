# Services发布页规则

## 1. 功能概述

### 业务价值
- 允许用户发布服务类信息
- 支持图片/视频上传、AI辅助描述生成、智能分类推荐
- 提供草稿保存功能，避免数据丢失

### 用户角色
- **Service Provider（服务提供商）**：发布服务类信息

### 入口位置
- 首页 → 点击"Post"按钮 → 点击"Services" → 进入发布表单页
- URL: `https://aepub.58v5.cn/biz/en/publish?categoryId=23&traceId=xxx`

---

## 2. 核心流程

### 主流程
```
1. 上传图片/视频（1-9张，第一张标记Main）
2. 填写Title（maxlength=200）
3. 填写Description（最少12字符，可使用AI生成）
4. 点击Post → 触发显示Suggested Categories
5. 选择Category
6. 填写Location（Google Maps自动完成）
7. 填写Contact信息（电话/邮箱）
8. 点击Post提交 → 跳转成功页
```

### 异常流程
- **空提交** → 按顺序显示错误：图片 → Title → Description → Category
- **Description少于12字符** → 显示错误提示
- **刷新页面** → 所有内容清空
- **保存草稿** → 停留当前页，显示Toast

---

## 3. 业务规则

### 3.1 与Marketplace的关键差异（✅ 2026-04-27 实测验证）

| 功能点 | Marketplace | Services | 验证状态 |
|--------|-------------|----------|----------|
| **Price字段** | ✅ 必填 | ✅ **有（必填）** | ✅ 37条测试确认 |
| **Delivery Options** | ✅ 4种选项 | ❌ 无（服务不涉及配送） | ✅ 实测确认 |
| **Condition字段** | ✅ 5种状态 | ⚠️ **部分分类有**（Home Cleaning无） | ✅ 实测确认 |
| **More Brand** | ✅ 有 | ❌ 无 | ✅ 实测确认 |
| **Contact信息** | ⚠️ 可选 | ⚠️ **待验证**（未在测试中覆盖） | ⚠️ 待补充测试 |
| **Location** | ✅ 有 | ✅ 有（服务地点） | ✅ 实测确认 |

### 3.2 Pictures上传规则

| 规则项 | 说明 |
|--------|------|
| **支持格式** | image/jpeg, image/jpg, image/png, video/mp4, video/quicktime, video/webm |
| **上传上限** | 9张图/视频，计数器显示"x/9" |
| **Main标签** | 第一张图片自动标记"Main" |
| **视频限制** | 最多1个视频，大小<200MB |

### 3.3 Title字段规则

| 规则项 | 说明 |
|--------|------|
| **最大长度** | 200字符（maxlength=200） |
| **超出处理** | 自动截断，不报错 |
| **字符计数** | 显示"x/200" |
| **特殊字符** | 接受HTML标签和Emoji，无XSS执行 |

### 3.4 Description字段规则

| 规则项 | 说明 |
|--------|------|
| **最少字符** | 12字符 |
| **必填校验** | 少于12字符提交时显示错误 |
| **AI工具** | Write with AI / Polish with AI / Undo / Shuffle |

### 3.5 AI工具规则

| 工具 | 前置条件 | 行为 |
|------|---------|------|
| **Write with AI** | 已上传图片 + 已填Title | 生成Description，显示"AI is working on it" |
| **Polish with AI** | 已手动输入Description | 优化现有文本，按钮名称从"Write"变为"Polish" |
| **Undo** | 已使用Polish | 恢复到Polish前的原始文本 |
| **Shuffle** | AI生成后 | 重新生成不同风格的Description |

### 3.6 Categories规则

| 规则项 | 说明 |
|--------|------|
| **显示时机** | 点击Post提交后才出现（触发式显示） |
| **Suggested Categories** | AI根据图片和标题自动推荐服务类目 |
| **More Categories** | 搜索框 + Browse浏览（多级分类树） |
| **选择后** | 显示Category面包屑 |

### 3.6 Price字段规则（✅ 2026-04-27 实测新增+确认）

| 规则项 | 说明 |
|--------|------|
| **字段存在** | ✅ Services发布页有Price字段 |
| **必填性** | ❌ **非必填（可选填）**✅ TC036实测确认 |
| **接受类型** | 数字和小数（如 99.5） |
| **拒绝类型** | 负数（自动变为0）|
| **特殊值** | 接受0和空值 |

### 3.7 Condition字段规则（✅ 2026-04-27 实测修正）

| 规则项 | 说明 |
|--------|------|
| **字段存在** | ⚠️ 部分分类有，部分无 |
| **Home Cleaning分类** | ❌ 无Condition字段 |
| **其他分类** | ⚠️ 待测试验证 |

### 3.8 Contact信息规则（✅ 2026-04-27 补充测试）

| 字段 | 类型 | ID | 必填 | 验证状态 |
|------|------|----|----|---------|
| **Contact** | text输入 | contact | ⚠️ 待确认 | ✅ TC035实测字段存在 |

**发现**：
- ✅ Contact字段存在（`<input id="contact">`）
- ✅ 页面文本包含："Contact", "Phone"关键词
- ⚠️ 必填性和格式校验待进一步测试

### 3.9 草稿保存规则

| 规则项 | 说明 |
|--------|------|
| **保存行为** | 停留当前页，显示Toast："Draft Saved Successfully" |
| **草稿入口** | 页面顶部"Draft·N"按钮（N为草稿总数） |
| **草稿列表** | 标题"Draft Box"，按保存时间倒序 |
| **草稿内容** | 封面图 / Title / "Save time: YYYY-MM-DD HH:mm:ss" / 删除图标 |
| **恢复草稿** | 点击草稿content区域，表单填充Title+Description+图片 |
| **删除草稿** | 二次确认弹窗："Delete This Draft ?" |

### 3.10 必填校验规则

空提交时按字段顺序显示错误：

1. "Please upload a photo before submitting."
2. "Please enter a title before submitting."
3. "Please enter the description before submitting, description must be at least 12 characters."
4. "Please fill out this field."（Category）

---

## 4. 错误处理

### 4.1 错误码定义

| 错误场景 | 处理方式 |
|---------|---------|
| 空提交 | 按顺序显示字段错误 |
| Description少于12字符 | 显示字符数要求错误 |
| 未选择Category | 显示"Please fill out this field." |

---

## 5. 依赖模块

### 上游依赖
- **首页Post按钮** → 跳转至分类选择页（/biz/en/publish/front）
- **分类选择页** → 点击Services跳转至发布表单页

### 下游依赖
- **AI服务** → Write with AI / Polish with AI / Suggested Categories
- **发布成功页** → `/biz/en/publish/success?id=xxx`
- **My Post页面** → Draft列表数据

### 跨域交互说明
- **AI生成服务** → 调用AI接口生成Description和推荐Categories
- **图片上传服务** → 上传图片至存储服务
- **草稿存储** → 保存至数据库，关联用户账号
- **Google Maps API** → Location自动完成

---

## 6. 已知问题

### 产品待确认问题
- **Category显示时机** → 为何需要点击Post才显示（而非初始即显示）
- **Contact字段必填性** → 实测为非必填，但是否符合产品预期？（TC037已验证）

### 技术风险
- **刷新丢失数据** → 未自动保存草稿，刷新后所有内容清空
- **AI生成速度** → 网络慢时可能超时
- **图片上传大小** → 未明确图片大小限制（仅视频<200MB）
- **Contact提交异常** → 填写Contact时提交失败（TC041发现，待调查）

---

## 7. 变更历史

| 日期 | 版本 | 变更内容 | 变更人 |
|------|------|---------|--------|
| 2026-04-27 | v2.1 | 更新测试用例编号（删除重复用例后），同步TC编号变更 | AI Assistant |
| 2026-04-27 | v2.0 | 重新生成Services规则，修正Marketplace错误内容 | AI Assistant |
