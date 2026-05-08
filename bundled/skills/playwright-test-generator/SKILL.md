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

## 🚥 标准工作流（阶段2A先测完，阶段2B再脚本化）

严格按 QA Agent instruction 指定的子阶段执行。阶段2A只做真实浏览器执行、预期验证、proof 和 bug list；阶段2B只消费阶段2A录制通过的 proof 生成 Python 脚本并自测。**【重要】进入每个子阶段前，必须主动使用 `Read` 工具读取对应指南文件，不要试图一次性把所有规范装进脑子里。**

### 阶段2A-1：解析与批次规划

**👉 动作前必读（使用 Read 工具读取）**：
- `references/doc-env-config.md` - 了解如何解析用例文档头部的测试环境配置

**执行流程**：
1. **解析配置**：从输入的 Markdown 文档头部提取测试环境配置（站点、Base URL、账号、角色等）。
2. **提取预期结果**：从每个用例的"预期结果"部分提取验证点（URL、文案、元素可见性等）。
3. **强制分批**：为防上下文超载导致跳步，**每次最多处理 5 个用例**（例如：12 条用例分为 5 + 5 + 2 三批处理）。

### 阶段2A-2：浏览器真实交互录制与验证（核心）

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
    4. 阶段2B跳过该用例，不生成 Python 脚本
    5. 继续下一个用例
  - 如果**符合预期**：
    1. 标记为 `PASSED`
    2. 继续执行后续步骤
    3. 录制完成后输出证明存档
- 每个用例录制完毕后，**必须按照 `enforcement-gates.md` 的格式**向用户输出带有真实 JavaScript 代码的"证明存档"（仅针对 PASSED 的用例），并同步保存结构化 `recording_trace.json`。

**录制特点**：
- 使用 CLI 命令进行浏览器自动化
- Token 效率高，输出简洁（YAML 快照格式）
- 易于集成到 CI/CD 流程
- 单命令可完成多个操作
- **实时验证预期结果，发现产品 bug**

### 阶段2A-3：录制执行报告与 outcome

**👉 动作前必读（使用 Read 工具读取）**：
- `references/bug-report-template.md` - Bug 清单报告格式规范
- `references/enforcement-gates.md` - proof 与 recording_trace 输出格式

**执行流程**：
- 阶段2A结束时必须落盘：
  - `playwright_recording_outcomes.json`
  - `playwright_recording_report.md`
  - `playwright_bug_report.md`（仅当存在 bug_recorded 时必填）
- `playwright_recording_outcomes.json` 对每条 `UI自动化=✅` 的用例必须且只能给出一个 outcome：
  - `recording_passed`：必须附带 `proof_artifact_path`，建议在 `details.recording_trace_path` 中附带结构化 trace
  - `bug_recorded`：必须附带 `bug_report_path`
  - `manual_review`：必须附带 `manual_review_reason`
- 阶段2A只证明需求测试已经真实执行，不生成 Python 脚本。QA Agent 会先展示录制报告和 bug list，等待用户确认后才进入阶段2B。

### 阶段2B-1：Python 代码生成（仅针对 recording_passed 用例）

**👉 动作前必读（使用 Read 工具读取）**：
- 回归项目的用例编写规范 `ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/docs/test-case-authoring-spec.md` - 文件命名、`_CONFIG`、pytest.mark、allure 装饰器、fixture 复用、等待与断言等全部规范
- 回归项目的代码模板 `ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/docs/templates/` 下的三个模板文件（standard-flow / stateful-session / component-batch），选择最匹配的模板
- 目标模块目录下已有的 `conftest.py` 和 `pages/` 文件，以便复用现有 Page Object 和 fixture
- `references/js-to-py-conversion.md` - JavaScript 到 Python 的严格转换规则
- `references/element-location-strategies.md` - 选择器生成规范

**执行流程**：
- **仅针对阶段2A `recording_passed` 的用例生成代码**；`bug_recorded` 和 `manual_review` 不进入脚本生成。
- 先从 `recording_trace.json` / proof 中的 CLI JavaScript 生成最小 replay 脚本，验证 JS → Python 转换能在 pytest 环境中跑通。
- replay 通过后，再按 `test-case-authoring-spec.md` 整理成 OK UI 规范脚本，补齐 `_CONFIG`、pytest.mark、allure、fixture/POM 复用。
- 生成代码必须来自阶段2A proof 中真实记录的 JavaScript。若 proof 没有对应动作，不能凭空猜；必须输出 `script_blocker_report.md` 并在 outcome 中标记 `script_blocked`。

### 阶段2B-2：自测调试与闭环（批次内必须闭环）

**👉 动作前必读（使用 Read 工具读取）**：
- `references/auto-debug-strategy.md` - 自动调试与排错手册
- `references/cleanup-strategy.md` - 测试数据清理原则

**执行流程**：
- **仅针对生成了代码的 recording_passed 用例执行此阶段**
- **第一步：强制依赖检查**：本批次生成完毕后，必须使用 `Shell` 工具执行 `pytest --collect-only <生成的文件路径>`。
  - 如果报 `ModuleNotFoundError`，必须进入自我修复循环（修改导包路径，或使用 `mkdir -p` 和 `touch __init__.py` 创建缺失的 POM 目录结构），直到 `collect-only` 通过。
- **第二步：执行测试**：`collect-only` 通过后，自动在终端运行 `pytest` 跑一遍生成的文件。
- 如果报错，自我诊断并修复（限 3 次）；修复成功后记录此次排坑经验。
- 3 轮后仍失败：输出 `script_blocker_report.md`，在 `playwright_case_outcomes.json` 中标记 `script_blocked`，并停止当前脚本批次。QA Agent 会阻塞在阶段2B，不进入影响分析。
- 本批次彻底通过后，再进入下一批次的阶段2B。

阶段2B结束时必须落盘 `playwright_case_outcomes.json`。对每条阶段2A `recording_passed` 的用例，最终必须是：
- `script_generated`：必须附带 `script_path`，并证明 `collect_only_passed=true`、`pytest_passed=true`
- `script_blocked`：必须附带 `script_blocker_report_path`，表示当前批次仍需人工处理，QA Agent 不会放行

---

## 🔍 强制状态追踪

为了防止在长对话中发生步骤跳跃或遗忘当前进度，**在每一次回复末尾，都必须附带以下格式的「状态追踪块」**：

```markdown
> **当前状态**：[阶段2A/阶段2B] 正在处理批次 N (TCxxx-TCyyy)
> **本批次统计**：PASSED: X 个 | FAILED: Y 个
> **下一步动作**：[用一句话明确说明接下来要做什么，或要请求用户确认什么]
```

---

## 📋 批次完成汇总格式

每个批次完成后必须输出汇总。阶段2A汇总侧重录制验证和 bug；阶段2B汇总侧重脚本生成和自测：

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━
【批次 N 完成汇总】

✅ recording_passed 用例（已保存 proof）：
- TC001: 直接访问 URL，页面标题正确展示 → proof-tc001.md
- TC002: 点击面包屑跳转首页 → proof-tc002.md

❌ bug_recorded 用例（已记录 bug）：
- TC003: 搜索功能异常 → bug-tc003.png

📁 生成文件：
- playwright_recording_outcomes.json
- playwright_recording_report.md
- playwright_bug_report.md (如有 bug)

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

### 典型工作流（先测完，再脚本化）

1. 用户提供 Markdown 测试用例文档
2. Skill 解析配置、提取预期结果并规划批次（每批 ≤5 个用例）
3. 阶段2A使用 `playwright-cli` 命令录制每个用例的浏览器交互
4. **每个步骤执行后立即验证预期结果**
5. 如果验证失败：截图、记录 bug、输出 `bug_recorded`
6. 如果验证通过：输出 proof、`recording_trace.json`、`recording_passed`
7. 所有批次执行完成后，落盘 `playwright_recording_outcomes.json`、`playwright_recording_report.md` 和可选 `playwright_bug_report.md`
8. QA Agent 展示录制执行结果，等待用户确认
9. 阶段2B只针对 `recording_passed` 用例生成 Python 脚本，先 replay 再整理成 OK UI 规范脚本
10. 每批运行 `pytest --collect-only` 和 `pytest`；3 轮仍失败则输出 `script_blocker_report.md` 并阻塞
11. 最终交付：bug 清单、proof/trace、通过自测的 Python 脚本和 `playwright_case_outcomes.json`

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
