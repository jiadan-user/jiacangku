# 预期结果验证指南

> 阶段 2 录制过程中的实时验证手册

---

## 核心原则

**在录制过程中，严格按照测试用例文档中的"预期结果"进行验证。如果实际结果与预期不符，立即标记为 FAILED，记录 bug 并跳过代码生成。**

---

## 验证时机

### 时机 1：每个操作步骤执行后

在执行完每个操作（click、fill、type 等）后，立即验证该步骤的预期结果。

```bash
# 执行操作
playwright-cli -s=tc001 click e123

# 立即获取快照验证
playwright-cli -s=tc001 snapshot

# 检查快照中的元素状态
```

### 时机 2：用例执行完成后

在所有操作步骤执行完成后，验证最终的预期结果。

```bash
# 所有操作完成后
playwright-cli -s=tc001 snapshot

# 验证最终状态（URL、页面标题、元素可见性等）
```

---

## 验证维度

从测试用例文档的"预期结果"部分提取以下验证点：

### 1. URL 验证

**预期结果示例**：
```
- 页面跳转至首页，URL 变为 https://example.com/
```

**验证方法**：
```bash
playwright-cli -s=tc001 snapshot
# 检查快照输出中的 "Page URL" 字段
```

**判定标准**：
- ✅ PASSED：实际 URL 与预期完全匹配或包含预期路径
- ❌ FAILED：URL 不匹配、404、或跳转到错误页面

---

### 2. 页面标题验证

**预期结果示例**：
```
- 页面标题显示 "Cars in Abu Dhabi"
- 浏览器 Tab 标题包含 "Abu Dhabi" 或 "Cars"
```

**验证方法**：
```bash
playwright-cli -s=tc001 snapshot
# 检查快照输出中的 "Page Title" 字段
```

**判定标准**：
- ✅ PASSED：标题包含预期文案
- ❌ FAILED：标题不包含预期文案或为空

---

### 3. 元素可见性验证

**预期结果示例**：
```
- 筛选栏显示：Sort / Filter / Abu Dhabi / Price / Mileage / Brand / Reset
- Location Tag 显示 "Location: Abu Dhabi ×"
```

**验证方法**：
```bash
playwright-cli -s=tc001 snapshot
# 检查快照 YAML 文件中的元素列表
```

**判定标准**：
- ✅ PASSED：所有预期元素都在快照中可见（ref 存在）
- ❌ FAILED：任何预期元素不可见或缺失

---

### 4. 文案内容验证

**预期结果示例**：
```
- 显示成功提示："创建成功"
- 错误提示："请填写完整信息"
```

**验证方法**：
```bash
playwright-cli -s=tc001 snapshot
# 在快照 YAML 中搜索预期文案
```

**判定标准**：
- ✅ PASSED：快照中包含预期文案（完全匹配或部分匹配）
- ❌ FAILED：文案不匹配、拼写错误、或完全缺失

---

### 5. 元素状态验证

**预期结果示例**：
```
- Sort 按钮箭头朝上（展开态）
- Filter 按钮显示角标 "1"
- 选项右侧显示填充勾选图标（●）
```

**验证方法**：
```bash
playwright-cli -s=tc001 snapshot
# 检查元素的属性（active、selected、checked 等）
```

**判定标准**：
- ✅ PASSED：元素状态符合预期
- ❌ FAILED：元素状态不符（如应该展开但未展开）

---

### 6. 列表/卡片数量验证

**预期结果示例**：
```
- 列表展示至少 1 个车辆卡片
- 车辆卡片包含：图片、标题、价格、里程、城市
```

**验证方法**：
```bash
playwright-cli -s=tc001 snapshot
# 统计快照中匹配的元素数量
```

**判定标准**：
- ✅ PASSED：数量符合预期（≥1、=N、或在范围内）
- ❌ FAILED：数量不符（如预期有数据但列表为空）

---

### 7. 空态验证

**预期结果示例**：
```
- 列表显示空态：`We couldn't find anything. Try a new search`
- 空态图标正常显示
```

**验证方法**：
```bash
playwright-cli -s=tc001 snapshot
# 搜索空态文案和图标
```

**判定标准**：
- ✅ PASSED：空态文案和图标都存在
- ❌ FAILED：空态显示异常或显示了数据（应该为空但有数据）

---

## FAILED 用例处理流程

当验证发现实际结果与预期不符时，按以下流程处理：

### 步骤 1：截图保存

```bash
playwright-cli -s=tc001 screenshot --filename=bug-tc001.png
```

**命名规范**：`bug-tc{用例编号}.png`

---

### 步骤 2：记录复现步骤

从用例文档的"执行步骤"部分提取，记录到 bug 清单：

```markdown
**复现步骤**：
1. 打开浏览器，访问 https://example.com/search
2. 在搜索框输入 "Toyota"
3. 点击 "Search" 按钮
```

---

### 步骤 3：记录预期与实际结果

```markdown
**预期结果**：页面跳转至搜索结果页，URL 包含 q=Toyota

**实际结果**：页面未跳转，URL 仍为 /search，搜索框清空但无任何反应
```

---

### 步骤 4：追加到 bug-report.md

```markdown
## TC006: 输入关键词点击 Search 执行搜索

**复现步骤**：
1. 打开浏览器，访问 https://example.com/search
2. 在搜索框输入 "Toyota"
3. 点击 "Search" 按钮

**预期结果**：页面跳转至搜索结果页，URL 包含 q=Toyota

**实际结果**：页面未跳转，URL 仍为 /search，搜索框清空但无任何反应

**问题截图**：`bug-tc006.png`

---
```

---

### 步骤 5：跳过代码生成

- 不输出该用例的"证明存档"
- 不生成该用例的 Python 代码
- 在批次汇总中标记为 FAILED

---

### 步骤 6：继续下一个用例

关闭当前浏览器会话，开始下一个用例的录制：

```bash
playwright-cli -s=tc001 close
# 继续 TC002
playwright-cli -s=tc002 open "https://example.com/..."
```

---

## 验证清单

每个用例验证时，确认以下检查项：

- [ ] 已从用例文档提取所有预期结果
- [ ] 每个操作步骤后都执行了 snapshot
- [ ] 对比了实际结果与预期结果的所有维度
- [ ] 如果 FAILED：已截图、已记录复现步骤、已追加到 bug-report.md
- [ ] 如果 PASSED：已输出证明存档、准备生成代码

---

## 常见验证陷阱

### 陷阱 1：只验证部分预期结果

❌ **错误做法**：
```
预期结果有 3 点，只验证了第 1 点就判定 PASSED
```

✅ **正确做法**：
```
逐一验证所有预期结果，全部符合才判定 PASSED
```

---

### 陷阱 2：对"推断"的预期结果过于宽松

❌ **错误做法**：
```
用例文档标注 "⚠️ 推断"，就不严格验证
```

✅ **正确做法**：
```
即使是推断的预期结果，也要严格验证。如果不符合，仍然标记 FAILED
```

---

### 陷阱 3：遇到异常就猜测原因

❌ **错误做法**：
```
验证失败后，猜测"可能是网络问题"，重试后就判定 PASSED
```

✅ **正确做法**：
```
如果第一次验证失败，可以重试 1 次。如果仍然失败，标记 FAILED 并记录 bug
```

---

### 陷阱 4：忘记截图

❌ **错误做法**：
```
发现 bug 后直接记录到 bug-report.md，没有截图
```

✅ **正确做法**：
```
必须先截图，再记录 bug。截图是 bug 报告的必需部分
```

---

## 验证示例

### 示例 1：URL 验证失败

**用例文档预期**：
```
- 页面跳转至首页，URL 变为 https://example.com/
```

**实际快照输出**：
```
Page URL: https://example.com/404
```

**判定**：❌ FAILED

**处理**：
```bash
playwright-cli -s=tc002 screenshot --filename=bug-tc002.png
# 记录到 bug-report.md
```

---

### 示例 2：元素可见性验证失败

**用例文档预期**：
```
- Location Tag 显示 "Location: Abu Dhabi ×"
```

**实际快照输出**：
```yaml
# 快照中未找到包含 "Location: Abu Dhabi" 的元素
```

**判定**：❌ FAILED

**处理**：
```bash
playwright-cli -s=tc004 screenshot --filename=bug-tc004.png
# 记录到 bug-report.md
```

---

### 示例 3：文案验证失败

**用例文档预期**：
```
- 显示成功提示："创建成功"
```

**实际快照输出**：
```yaml
- generic: "创建失敗"  # 注意：繁体字，拼写错误
```

**判定**：❌ FAILED（文案错误）

**处理**：
```bash
playwright-cli -s=tc001 screenshot --filename=bug-tc001.png
# 记录到 bug-report.md：文案显示为繁体字且拼写错误
```

---

## 总结

验证是录制过程中最关键的环节，直接决定：
1. 是否生成测试脚本
2. 是否记录 bug
3. 最终交付的质量

**核心原则**：严格对照用例文档的预期结果，不符合就是 bug，不要猜测，不要放水。

---

**Last updated**: 2026-03-30  
**Purpose**: Guide for validating expected results during Phase 2 recording
