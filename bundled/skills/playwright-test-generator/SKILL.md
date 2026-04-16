---
name: playwright-test-generator
description: 从 Markdown 测试用例文档生成 Playwright Python 测试脚本，通过 playwright-cli 录制真实浏览器交互并转换为 Python 代码。录制过程中严格验证预期结果，发现 bug 则记录到报告并跳过脚本生成，确保只生成通过验证的测试用例。当用户提供测试用例文档、需要 UI 自动化脚本，或提到 Playwright 测试开发、CLI 录制、脚本生成时使用。
---

# Playwright 测试生成器

## 🎯 核心理念

现代 Web 应用拥有大量动态 DOM 和复杂的状态管理（如 React/Vue）。依靠猜测去编写 Playwright 选择器会导致极高的失败率和无穷的修 Bug 时间。

因此，本 Skill 的基石是：**100% 依赖真实浏览器 playwright-cli 的录制结果来生成 Python 代码。**

通过严格的分阶段执行、实时验证预期结果和输出录制"证明存档"，以此消除大模型的幻觉式猜测，并在录制阶段发现产品 bug。

---

## 🚥 标准工作流（5 阶段流程）

严格按照以下 5 个阶段顺序流转。**【重要】在进入每个特定阶段前，必须主动使用 `Read` 工具读取对应的指南文件，不要试图一次性把所有规范装进脑子里。**

### 阶段 1：解析与批次规划

**👉 动作前必读（使用 Read 工具读取）**：
- `references/doc-env-config.md` - 了解如何解析用例文档头部的测试环境配置

**执行流程**：
1. **解析配置**：从输入的 Markdown 文档头部提取测试环境配置（站点、Base URL、账号、角色等）。
2. **提取预期结果**：从每个用例的"预期结果"部分提取验证点（URL、文案、元素可见性等）。
3. **强制分批**：为防上下文超载导致跳步，**每次最多处理 5 个用例**（例如：12 条用例分为 5 + 5 + 2 三批处理）。

### 阶段 2：浏览器真实交互录制与验证（核心）

**👉 动作前必读（使用 Read 工具读取）**：
- `references/cli-recording-guide.md` - 了解 playwright-cli 录制流程与准备工作
- `references/result-validation-guide.md` - 了解如何验证预期结果
- `references/login-flow-recording.md` - 如果是登录操作，必须看这个防雷指南
- `references/enforcement-gates.md` - 了解如何输出防伪的证明存档，这是门控核心

**执行流程**：
- 向用户展示本批次清单，并**等待用户回复"可以开始了"**。
- 对本批次用例，依次使用 `playwright-cli` 命令在真实浏览器里执行交互。
- **每个操作步骤执行后，立即验证预期结果**：
  - 使用 `playwright-cli snapshot` 获取页面状态
  - 对比实际结果与用例文档中的预期结果
  - 如果**不符合预期**：
    1. 标记为 `FAILED`
    2. 使用 `playwright-cli screenshot --filename=bug-tcxxx.png` 截图
    3. 记录复现步骤和问题描述
    4. 跳过该用例的代码生成
    5. 继续下一个用例
  - 如果**符合预期**：
    1. 标记为 `PASSED`
    2. 继续执行后续步骤
    3. 录制完成后输出证明存档
- 每个用例录制完毕后，**必须按照 `enforcement-gates.md` 的格式**向用户输出带有真实 JavaScript 代码的"证明存档"（仅针对 PASSED 的用例）。

**录制特点**：
- 使用 CLI 命令进行浏览器自动化
- Token 效率高，输出简洁（YAML 快照格式）
- 易于集成到 CI/CD 流程
- 单命令可完成多个操作
- **实时验证预期结果，发现产品 bug**

### 阶段 3：Python 代码生成（仅针对 PASSED 用例）

**👉 动作前必读（使用 Read 工具读取）**：
- 回归项目的用例编写规范 `ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/docs/test-case-authoring-spec.md` - 文件命名、`_CONFIG`、pytest.mark、allure 装饰器、fixture 复用、等待与断言等全部规范
- 回归项目的代码模板 `ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/docs/templates/` 下的三个模板文件（standard-flow / stateful-session / component-batch），选择最匹配的模板
- 目标模块目录下已有的 `conftest.py` 和 `pages/` 文件，以便复用现有 Page Object 和 fixture
- `references/js-to-py-conversion.md` - JavaScript 到 Python 的严格转换规则
- `references/element-location-strategies.md` - 选择器生成规范

**执行流程**：
- **仅针对阶段 2 标记为 PASSED 的用例生成代码**
- 先根据 `test-case-authoring-spec.md` 选择合适的模板，再将阶段 2 "证明存档"中真实记录的 JavaScript 代码，严格转换为 Python 的 Page Object 与 Test Case。
- 生成的代码必须符合 `test-case-authoring-spec.md` 的全部要求（`_CONFIG` 字段、pytest.mark、allure 装饰器、禁止裸 `wait_for_timeout` 等）。
- **陷阱提示**：遇到组件遮挡、防抖搜索等具体报错时，请查阅 `references/` 下的相关问题文档（如 `sticky-header-click.md` 或 `search-input-debounce.md`）。
- **逻辑约束**：如果在阶段 2 没有录制出对应的动作，绝不能在此时盲目"猜"代码，遇到遗漏应请求补充录制。

### 阶段 4：Bug 清单报告生成（如有 FAILED 用例）

**👉 动作前必读（使用 Read 工具读取）**：
- `references/bug-report-template.md` - Bug 清单报告格式规范

**执行流程**：
- **仅当本批次存在 FAILED 用例时执行此阶段**
- 检查是否已存在 bug 清单文件（`bug-report.md`）
  - 如果存在：追加新发现的 bug 到文件末尾
  - 如果不存在：创建新文件
- Bug 清单格式（简洁版）：
  ```markdown
  ## TCxxx: [用例标题]
  
  **复现步骤**：
  1. 步骤1
  2. 步骤2
  3. 步骤3
  
  **预期结果**：[从用例文档提取]
  
  **实际结果**：[录制时观察到的实际情况]
  
  **问题截图**：`bug-tcxxx.png`
  
  ---
  ```
- **禁止添加多余内容**：不要添加优先级、严重程度、修复建议等额外信息

### 阶段 5：自测调试与闭环（仅针对 PASSED 用例）

**👉 动作前必读（使用 Read 工具读取）**：
- `references/auto-debug-strategy.md` - 自动调试与排错手册
- `references/cleanup-strategy.md` - 测试数据清理原则

**执行流程**：
- **仅针对生成了代码的 PASSED 用例执行此阶段**
- **第一步：强制依赖检查**：本批次生成完毕后，必须使用 `Shell` 工具执行 `pytest --collect-only <生成的文件路径>`。
  - 如果报 `ModuleNotFoundError`，必须进入自我修复循环（修改导包路径，或使用 `mkdir -p` 和 `touch __init__.py` 创建缺失的 POM 目录结构），直到 `collect-only` 通过。
- **第二步：执行测试**：`collect-only` 通过后，自动在终端运行 `pytest` 跑一遍生成的文件。
- 如果报错，自我诊断并修复（限 3 次）；修复成功后记录此次排坑经验。
- 本批次彻底通过后，再进入下一批次的"阶段 2"。

---

## 🔍 强制状态追踪

为了防止在长对话中发生步骤跳跃或遗忘当前进度，**在每一次回复末尾，都必须附带以下格式的「状态追踪块」**：

```markdown
> **当前状态**：[阶段 X] 正在处理批次 N (TCxxx-TCyyy)
> **本批次统计**：PASSED: X 个 | FAILED: Y 个
> **下一步动作**：[用一句话明确说明接下来要做什么，或要请求用户确认什么]
```

---

## 📋 批次完成汇总格式

每个批次完成后（阶段 5 结束），必须输出以下汇总：

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━
【批次 N 完成汇总】

✅ PASSED 用例（已生成脚本）：
- TC001: 直接访问 URL，页面标题正确展示
- TC002: 点击面包屑跳转首页

❌ FAILED 用例（已记录 bug）：
- TC003: 搜索功能异常 → bug-tc003.png

📁 生成文件：
- test_cases/test_module.py (2 个测试用例)
- bug-report.md (1 个 bug，追加模式)

━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🛠️ playwright-cli 工具

本 Skill 使用 **playwright-cli** 进行浏览器录制：

**特点**：
- ✅ **Token 效率高**（输出简洁，减少上下文消耗）
- ✅ **YAML 快照格式**（结构清晰，易于解析）
- ✅ **CI/CD 友好**（标准 CLI 命令）
- ✅ **录制速度快**（单命令完成多个操作）
- ✅ **实时验证**（录制过程中验证预期结果）

**安装**：
```bash
npm install -g @playwright/cli@latest
playwright-cli --help
```

**配置**：使用 `.playwright/cli.config.json` 进行浏览器配置（参见项目根目录示例）

---

## 📚 参考资源

所有详细规则存储在 `references/` 目录，按需使用 `Read` 工具读取。

**核心流程**：
- `cli-recording-guide.md` - CLI 录制详细指南
- `result-validation-guide.md` - 预期结果验证指南（新增）
- `bug-report-template.md` - Bug 清单报告模板（新增）
- `js-to-py-conversion.md` - JavaScript 到 Python 转换规则
- `enforcement-gates.md` - 证明存档格式定义

**陷阱与调试**：
- `conversion-pitfalls.md` - 转换常见陷阱
- `auto-debug-strategy.md` - 自动调试策略
- `ai-execution-guide.md` - AI 执行指南

**特定场景**：
- `login-flow-recording.md` - 登录流程录制防雷
- `search-input-debounce.md` - 搜索输入防抖处理
- `sticky-header-click.md` - 粘性头部遮挡处理
- `async-counter-update.md` - 异步计数器更新
- `card-content-reading.md` - 卡片内容读取
- `strict-mode-list-assertions.md` - 严格模式列表断言

**配置工具**：
- `doc-env-config.md` - 测试环境配置解析
- `element-location-strategies.md` - 元素定位策略
- `validation-recording.md` - 验证录制
- `cleanup-strategy.md` - 清理策略
- `no-login-example.md` - 无需登录示例

---

## 📦 依赖项

**必需**：
- `pytest` - Python 测试框架
- `playwright` - 浏览器自动化库
- `allure-pytest` - 测试报告
- `@playwright/cli` - CLI 录制工具（必须全局安装）

**安装**：
```bash
pip install pytest playwright allure-pytest
playwright install chromium
npm install -g @playwright/cli@latest
```

---

## 🎯 使用示例

### 典型工作流（带验证）

1. 用户提供 Markdown 测试用例文档
2. Skill 解析配置、提取预期结果并规划批次（每批 ≤5 个用例）
3. 使用 `playwright-cli` 命令录制每个用例的浏览器交互
4. **每个步骤执行后立即验证预期结果**
5. 如果验证失败：截图、记录 bug、跳过代码生成
6. 如果验证通过：输出证明存档、生成 Python 代码
7. 生成 bug 清单报告（如有 FAILED 用例）
8. 运行 `pytest --collect-only` 和 `pytest` 验证生成的代码
9. 处理下一批次，直到所有用例完成
10. 最终交付：测试脚本 + bug 清单报告

### 验证示例

```bash
# 执行操作
playwright-cli -s=tc001 click e123

# 立即验证预期结果
playwright-cli -s=tc001 snapshot

# 检查快照中的元素/文案是否符合预期
# 如果不符合：
playwright-cli -s=tc001 screenshot --filename=bug-tc001.png
# 记录到 bug-report.md
# 跳过代码生成

# 如果符合：
# 继续下一步操作
```

---

## 🔧 移动端支持

移动端测试脚本生成请使用专门的 skill：
- `playwright-mobile-test-generator` - 支持移动端设备配置、tap/swipe 等移动端 API

本 Skill 专注于桌面端 Web 应用的测试脚本生成。
