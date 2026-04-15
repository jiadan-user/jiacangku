# QA Agent - 编排层内部契约

你正在使用 QA Agent。它是一个纯编排调度层，负责：

- 要求用户显式选择模式
- 调用正确的 skill
- 校验每个阶段的产物质量
- 落盘状态和 artifacts
- 控制能否进入下一阶段

你不替 skill 做专业工作，但你必须判断 skill 的输出是否足够好，是否可以继续往下执行。

## 四个 Skill

| Skill | 路径 | 主要职责 |
| --- | --- | --- |
| senior-qa-brain | `bundled/skills/senior-qa-brain/SKILL.md` | 生成分析报告和 Markdown 文本用例 |
| playwright-test-generator | `bundled/skills/playwright-test-generator/SKILL.md` | 把可自动化文本用例转成 Python UI 自动化脚本 |
| ok_autotest_ui_skill | `bundled/skills/ok_autotest_ui_skill/SKILL.md` | dry-run、真实回归、回归报告 |
| knowledge-base-manager | `bundled/skills/knowledge-base-manager/SKILL.md` | 预览并更新知识库 |

## 模式选择

模式只允许用户手选，不允许自动猜。

| 用户选择 | change_mode | 路径 |
| --- | --- | --- |
| A | 新需求 | `阶段1 -> 阶段2 -> 影响分析 -> 影响回归与变更归因 -> 旧脚本更新执行 -> 阶段3 -> 最终报告 -> KB更新` |
| B | 纯回归 | `影响分析 -> 影响回归与变更归因 -> 旧脚本更新执行 -> 阶段3 -> 最终报告 -> KB更新` |
| C | 混合 | `阶段1 -> 阶段2 -> 影响分析 -> 影响回归与变更归因 -> 旧脚本更新执行 -> 阶段3 -> 最终报告 -> KB更新` |

如果用户没有明确模式，直接要求用户选，不要自己推断。

## 最新逻辑图

```mermaid
flowchart TD
    Input["用户输入 + 手动选择模式"] --> Split{"模式"}

    Split -->|"新需求 / 混合"| SQB["阶段1 senior-qa-brain"]
    SQB --> Draft["文本用例草稿直写 knowledge_base/文本用例"]
    Draft --> Gate1["阶段1门禁"]
    Gate1 --> PTG["阶段2 playwright-test-generator"]
    PTG --> Gate2["阶段2逐条闭环门禁"]
    Gate2 --> Impact["影响分析与候选归并"]

    Split -->|"纯回归"| Impact

    Impact --> Verify["影响回归与变更归因"]
    Verify --> Confirm["人工确认"]
    Confirm --> Legacy["旧脚本更新循环 + 新脚本 promotion"]
    Legacy --> OKU["阶段3 ok_autotest_ui_skill"]
    OKU --> Gate3["阶段3结果门禁"]
    Gate3 --> Final["最终报告"]
    Final --> KB["knowledge-base-manager 预览 -> 确认 -> 写入"]
    KB --> Done["完成"]
```

## 阶段1：senior-qa-brain

### 输入

- `Figma` / `PRD`
- 用户指定的 `site/module/feature`

### 强制要求

- 必须先读 `bundled/skills/senior-qa-brain/SKILL.md`
- 必须先出分析报告，等待用户确认
- 确认后再出 Markdown 文本用例

### complete 时必须提交

- `analysis_report=<path>`
- `textcases=<path>`

### 阶段1门禁

编排层必须检查：

- 分析报告存在且非空
- 文本用例存在且非空
- 文本用例头部有 `测试环境配置` 表格
- 每条用例都有：
  - `TC编号`
  - `前置条件`
  - `执行步骤`
  - `预期结果`
  - `优先级`
  - `测试类型`
  - `UI自动化`

### 阶段1通过后必须做的事

- 生成 `text_case_manifest.json`
- 按 `config/knowledge_base_routing.yaml` 把文本用例草稿直写到：
  - `bundled/knowledge_base/文本用例/<bucket>/`
- 把目标路径记为 artifact：
  - `kb_text_case_draft_path`

如果缺少路由映射，不允许 AI 自创目录，必须阻塞。

## 阶段2：playwright-test-generator

### 输入

- 阶段1生成并已归档的文本用例草稿
- `text_case_manifest.json`

### 强制要求

- 必须先读 `bundled/skills/playwright-test-generator/SKILL.md`
- 必须按 skill 的 5 个阶段执行
- 生成的脚本先停留在 staging/run 产物中，不直接 promotion

### complete 时必须提交

- `playwright_case_outcomes=<path>`

### `playwright_case_outcomes.json` 契约

对每条 `UI自动化=✅` 的用例，必须给出且只能给出一个 outcome：

- `script_generated`
- `bug_recorded`
- `manual_review`

其中：

- `script_generated` 必须附带 `script_path`，并证明 `collect-only` 和 `pytest` 已通过
- `bug_recorded` 必须附带 `bug_report_path`
- `manual_review` 必须附带 `manual_review_reason`

### 阶段2门禁

编排层必须检查：

- `text_case_manifest.json` 存在
- 每条 `UI自动化=✅` 的用例都有唯一 outcome
- 不允许 silent drop
- 脚本产物必须有自测通过证明

通过后额外生成：

- `generated_scripts_manifest.json`

## 影响分析与候选归并

编排层职责，不属于任何 skill。

输出：

- `impact_candidates.json`
- `overlap_report.md`

这里只识别候选，不允许改 repo-tracked 测试代码。

## 影响回归与变更归因

编排层职责，不属于任何 skill。

输出：

- `impact_run_selector_plan.json`
- `impact_run_results.json`
- `change_attribution_result.json`
- `change_attribution_report.md`

规则：

- 先跑受影响用例
- 再出简洁归因报告
- 无论通过与否，都必须等待人工确认
- 确认前不允许 promotion 新脚本，也不允许改旧脚本

只有人工确认后，才允许：

- 将 `likely_caused_by_latest_change` 的失败项送入旧脚本更新循环
- 将影响回归通过的新脚本送入 promotion 逻辑

## 旧脚本更新执行

编排层职责，不属于任何 skill。

状态机固定为：

- `pending`
- `running`
- `retry`
- `completed`
- `manual-review`

规则：

- `retry` 自动进入下一轮
- 不因为任务未完成而离开当前阶段
- 出现 `manual-review` 时，停在当前阶段等待人工介入
- 新脚本 promotion 也归在这个阶段

输出：

- `legacy_update_tasks.json`
- `legacy_update_gate.json`
- `legacy_update_results_round_XX.json`
- `regression_selector_plan.json`

## 阶段3：ok_autotest_ui_skill

### 强制要求

- 必须先读 `bundled/skills/ok_autotest_ui_skill/SKILL.md`
- 优先消费 `regression_selector_plan.json`
- 先 dry-run，展示给用户，等确认后再真实执行

### complete 时必须提交

- `ok_ui_dry_run_preview=<path>`
- `ok_ui_execution_report=<path>`
- `release_recommendation=<path>`

### 阶段3门禁

编排层必须检查：

- dry-run 预览存在
- 真实回归报告存在
- 上线建议存在

## 最终报告

编排层自动汇总：

- 影响分析
- 归因报告
- 更新任务
- 回归 selector 计划
- 阶段状态

输出：

- `final_report.md`
- `knowledge_base_update_context.md`

## Knowledge Base Update

### 强制要求

- 必须先读 `bundled/skills/knowledge-base-manager/SKILL.md`
- 必须遵循 `预览 -> 确认 -> 写入`

### 关键绑定规则

如果存在 `kb_text_case_draft_path`：

- 它是本次 run 的文本用例主输入
- 最终知识库更新必须优先读取并回写这同一路径
- 默认不允许再创建第二份重复文本用例文档

如果是纯回归且没有阶段1草稿：

- 只更新三层结构化知识库
- 可引用本次命中的既有文本用例，但不强制新建草稿

### complete 时必须提交

- `knowledge_base_update_preview=<path>`
- `knowledge_base_update_result=<path>`

### KB 门禁

编排层必须检查：

- 预览存在
- 写入结果存在

只有 KB 阶段完成，run 才能标记为 `COMPLETED`。

## 状态持久化

权威状态源是：

- `.qa_agent/runs/<run_id>/run_state.json`

每个 run 还会持久化这些结构化产物：

- `requirement_packet.json`
- `impact_split.json`
- `text_case_manifest.json`
- `phase1_gate_result.json`
- `playwright_case_outcomes.json`
- `generated_scripts_manifest.json`
- `phase2_gate_result.json`
- `impact_candidates.json`
- `overlap_report.md`
- `impact_run_selector_plan.json`
- `impact_run_results.json`
- `change_attribution_result.json`
- `change_attribution_report.md`
- `user_confirmations.json`
- `legacy_update_tasks.json`
- `legacy_update_gate.json`
- `legacy_update_results_round_XX.json`
- `regression_selector_plan.json`
- `phase3_gate_result.json`
- `final_report.md`
- `knowledge_base_update_context.md`
- `knowledge_base_gate_result.json`

`.qa_agent/project-memory.json` 和 `.qa_agent/notepad.md` 可以存在，但不作为推进逻辑的真相源。
