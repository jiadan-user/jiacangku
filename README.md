# QA Agent 使用说明

`QA_Agent` 是一个测试编排项目。你在这个仓库里让 AI 工作时，它会帮你串起：

- `senior-qa-brain`：分析 Figma / PRD，输出分析报告和文本用例
- `playwright-test-generator`：先录制执行并产出 bug list，再把录制通过的用例转成 UI 自动化脚本
- `ok_autotest_ui_skill`：做 PC UI 回归
- `knowledge-base-manager`：把本次产物同步回知识库

这个项目的重点不是“替代 skill”，而是“把 skill 串起来，并在每一阶段做验收”。

## 完整逻辑图

```mermaid
flowchart TD
    Input["用户输入"] --> Mode["用户手动选择模式<br/>A 新需求 / B 纯回归 / C 混合"]
    Mode --> Run["qa-agent run<br/>doctor -> plan -> drive_to_action"]

    Run --> Split{"模式路径"}
    Split -->|"新需求 / 混合"| SQB["senior-qa-brain<br/>分析报告 + 文本用例"]
    SQB --> SQBGate["阶段1门禁<br/>结构校验 + 文本用例归档"]
    SQBGate --> PTG2A["playwright-test-generator 2A<br/>录制执行 + proof + bug list"]
    PTG2A --> PTGConfirm["确认录制报告和 bug list"]
    PTGConfirm --> PTG2B["playwright-test-generator 2B<br/>Python 脚本生成 + 自测"]
    PTG2B --> PTGGate["阶段2门禁<br/>录制通过用例脚本化闭环"]
    PTGGate --> Impact["影响分析与候选归并"]

    Split -->|"纯回归"| Impact

    Impact --> Verify["影响回归与变更归因<br/>先跑受影响用例，不改测试代码"]
    Verify --> Confirm["人工确认归因报告"]
    Confirm --> Legacy["旧脚本更新循环 + 新脚本 promotion"]
    Legacy --> OKUI["ok_autotest_ui_skill<br/>dry-run -> 确认 -> 真实回归"]
    OKUI --> Final["最终报告 + 上线建议"]
    Final --> KB["knowledge-base-manager<br/>预览 -> 确认 -> 写入"]
    KB --> Done["完成"]
```

## 你怎么开始

在仓库根目录直接告诉 AI：

- 你要跑哪种模式：`新需求`、`纯回归`、`混合`
- 站点：比如 `ae`
- 模块：比如 `car`
- 功能点：比如 `列表`
- 如果是新需求/混合，再给 `Figma`、`PRD`
- 如果是纯回归/混合，再给改动描述

常见说法：

```text
请用 QA Agent 跑一条新需求链路，站点 ae，模块 car，功能点 列表，PRD 在 /path/to/doc.pdf
```

```text
请用 QA Agent 跑纯回归，站点 ae，模块 car，改动是“列表卡片样式改大卡”
```

```text
请用 QA Agent 跑混合模式，站点 ae，模块 car，功能点 列表，PRD 在 /path/to/doc.pdf，另外列表卡片样式有改动
```

## 三种模式

- `新需求`：先出分析报告和文本用例，再做自动化转译、影响验证、回归、知识库更新
- `纯回归`：直接从影响分析开始，不生成新的文本用例草稿
- `混合`：先走新需求支线，再把新脚本和旧脚本一起纳入回归

模式不自动判断。你需要明确告诉 AI 选哪一种。

## 推荐命令流

最推荐用 `run` 创建并自动推进到第一个可操作点：

```bash
python -m qa_agent.cli run \
  --change-mode 新需求 \
  --site ae \
  --module car \
  --feature 列表 \
  --prd-ref "/path/to/需求文档.pdf"
```

纯回归示例：

```bash
python -m qa_agent.cli run \
  --change-mode 纯回归 \
  --site ae \
  --module car \
  --feature 列表 \
  --change-description "列表卡片样式改大卡"
```

查看下一步该做什么：

```bash
python -m qa_agent.cli status --run-id <run_id> --next-action
```

提交阶段产物并触发门禁：

```bash
python -m qa_agent.cli complete \
  --run-id <run_id> \
  --phase senior-qa-brain \
  --artifact analysis_report=/path/to/analysis.md \
  --artifact textcases=/path/to/textcases.md
```

人工确认后继续自动推进：

```bash
python -m qa_agent.cli next --run-id <run_id>
```

环境预检：

```bash
python -m qa_agent.cli doctor
```

调试时看完整 JSON：

```bash
python -m qa_agent.cli status --run-id <run_id> --json
```

`advance` 仍然保留，但它是低层单步推进命令；日常建议优先使用 `run / next / complete / status`。

## 独立 Agent Memory

项目内提供一个独立记忆系统，用来沉淀重要对话、用户纠错、协作偏好、设计决策和踩坑经验。它不是 QA Agent 状态机的一部分，只给 AI 提供提醒。

初始化本地记忆目录：

```bash
python -m qa_agent.cli memory init
```

把一条纠错先放进候选区，不直接写成长期规则：

```bash
python -m qa_agent.cli memory suggest --text "QA Agent 不要自动判断模式，必须让用户选择"
```

查看和确认候选记忆：

```bash
python -m qa_agent.cli memory list-pending
python -m qa_agent.cli memory promote --id <candidate_id>
python -m qa_agent.cli memory reject --id <candidate_id>
```

搜索和导出记忆上下文：

```bash
python -m qa_agent.cli memory search "旧脚本更新"
python -m qa_agent.cli memory export --target qa-agent --query "QA Agent 旧脚本更新"
```

记忆目录在 `.agent_memory/`，默认不会提交到 git。QA Agent 建 run 时会生成 `memory_context.md` artifact，skill instruction 会提示 AI 先读取这份上下文；但 memory 不能改变模式选择、不能跳过人工确认，也不能直接修改测试代码。

## 你会经历哪些确认点

1. `senior-qa-brain`
   AI 会先停在分析报告，等你确认后再继续生成文本用例。
2. `playwright-test-generator`
   AI 会先执行阶段2A，产出逐条 recording outcome、proof 和 bug list；你确认录制报告后，再进入阶段2B生成 Python 脚本并自测。
3. `影响回归与变更归因`
   AI 会先跑受影响用例，再给你一份简洁归因报告，等你确认后才允许改旧脚本或 promotion 新脚本。
4. `旧脚本更新执行`
   如果旧脚本无法安全 patch，QA Agent 会停下来生成重录子任务，让 AI 按 `playwright-test-generator` 重新录制候选脚本；不会自己盲猜修改旧脚本。
   只要本阶段合并了 `test_cases/**/*.py` 脚本变更，QA Agent 会先刷新 ok_autotest_ui 的 catalog 并审计标识，成功后才进入阶段3。
5. `ok_autotest_ui_skill`
   AI 会先给你 dry-run 预览，等你确认后才真实执行回归。
6. `knowledge-base-manager`
   AI 会先给你知识库更新预览，等你确认后才写入。

## 阶段完成时通常要交哪些产物

如果你用 CLI 或要求 AI 手动 `complete` 某个阶段，常见产物是：

- 阶段1：`analysis_report=<path>`、`textcases=<path>`
- 阶段2A：`playwright_recording_outcomes=<path>`、`playwright_recording_report=<path>`，如有 bug 再加 `playwright_bug_report=<path>`
- 阶段2B：`playwright_case_outcomes=<path>`
- 阶段3：`ok_ui_dry_run_preview=<path>`、`ok_ui_execution_report=<path>`、`release_recommendation=<path>`
- 知识库阶段：`knowledge_base_update_preview=<path>`、`knowledge_base_update_result=<path>`

常见 artifact key 示例：

| 阶段 | artifact key |
| --- | --- |
| 阶段1 | `analysis_report`, `textcases`, `text_case_manifest`, `kb_text_case_draft_path` |
| 阶段2 | `playwright_recording_outcomes`, `playwright_recording_report`, `playwright_bug_report`, `proof_artifacts_manifest`, `playwright_case_outcomes`, `generated_scripts_manifest` |
| 影响分析 | `impact_candidates`, `overlap_report` |
| 影响归因 | `impact_run_selector_plan`, `impact_run_results`, `change_attribution_report` |
| 更新循环 | `legacy_update_tasks`, `legacy_update_gate`, `legacy_rerecord_request`, `legacy_rerecord_instruction`, `legacy_update_candidate_manifest`, `catalog_refresh_after_script_changes_round_XX`, `regression_selector_plan` |
| 阶段3 | `ok_ui_dry_run_preview`, `ok_ui_execution_report`, `release_recommendation` |
| 最终阶段 | `final_report`, `knowledge_base_update_context`, `knowledge_base_update_preview`, `knowledge_base_update_result` |

## 文本用例会放哪里

新需求 / 混合模式下，阶段1通过门禁后，文本用例会直接写到：

`bundled/knowledge_base/文本用例/<目录桶>/`

例如 `car` 会路由到：

`bundled/knowledge_base/文本用例/test_car/`

最终知识库更新阶段会优先回写这同一份草稿，不会默认新建第二份重复文本用例。

## 产物去哪看

每次运行都会落到：

`/Users/a58/Desktop/QA_Agent/.qa_agent/runs/<run_id>/`

重点看这些文件：

- `run_state.json`
- `analysis_report.*`
- `text_case_manifest.json`
- `playwright_recording_outcomes.json`
- `playwright_recording_report.md`
- `playwright_bug_report.md`
- `playwright_case_outcomes.json`
- `impact_candidates.json`
- `change_attribution_report.md`
- `legacy_update_tasks.json`
- `regression_selector_plan.json`
- `final_report.md`
- `knowledge_base_update_context.md`

## ui_test_management Dashboard 同步

QA Agent 在完成态 run 结束后会自动把执行记录、Allure 报告入口、最终报告和覆盖快照发布到 `ui_test_management`。默认发布地址是 `http://10.192.35.53:8001`；如果你在本地调试，也可以用环境变量覆盖成自己的后端地址。

常用环境变量：

- `QA_AGENT_DASHBOARD_URL=http://127.0.0.1:8001`：覆盖目标 `ui_test_management` 后端地址；不配置时默认使用 `http://10.192.35.53:8001`。
- `QA_AGENT_DASHBOARD_PROJECT_KEY=OK`：目标业务项目，默认就是 `OK`。
- `QA_AGENT_DASHBOARD_API_KEY=...`：如果平台开启发布密钥校验，就配置这个值。
- `QA_AGENT_DASHBOARD_ENABLED=false`：需要临时关闭自动发布时使用。

手动补发某次 run：

```bash
python -m qa_agent.cli dashboard publish --run-id <run_id>
```

只刷新覆盖快照，不新增执行记录：

```bash
python -m qa_agent.cli dashboard publish-coverage --project-key OK
```

如果只是想按 OK UI 目录或 nodeid 精确跑一批现有自动化用例，不需要走完整 QA Agent 影响分析，可以使用独立 OK UI 回归入口。它不会发散找候选，只把传入的筛选条件直接交给 `ok_autotest_ui_skill`，执行后自动发布到 `ui_test_management`：

```bash
python -m qa_agent.cli dashboard run-ok-ui \
  --path test_cases/zhaopin/ \
  --workers 1 \
  --project-key OK
```

如果已经单独跑过 `ok_autotest_ui_skill`，也可以用 OK UI 自己输出的 `run_id` 补发到平台：

```bash
python -m qa_agent.cli dashboard publish-ok-ui-run --ok-ui-run-id <ok_ui_run_id>
```

覆盖度口径来自 `bundled/knowledge_base/文本用例` 的 Markdown 文本用例扫描：所有 `### TC` 标题都会计入文本用例总数。缺少 `优先级` 或 `UI自动化` 字段的旧格式 TC 不会被丢弃，会标记为“字段待补齐”；这些 TC 已计入总数，但会影响优先级归因和自动化率判断。

`bundled/skills/ok_autotest_ui_skill/references/coverage-dashboard.md` 只保留为历史静态快照参考，不再作为页面最新覆盖数据源。平台上的 `用例覆盖度` 页签以 QA Agent publish 生成的结构化覆盖快照为准。

页面归属统一放在 `OK` 项目内的 `QA-Agent执行记录` 和 `用例覆盖度` 页签。历史上本地 DB 里可能存在名为 `QA Agent` 的项目，它只是早期 publish 映射留下的系统/脏数据项目，不是业务项目，新记录不应再写入那里。

## 卡住时怎么继续

- 如果 AI 提示“等待确认”，说明这是正常门禁，确认后继续即可
- 如果提示缺少某个 artifact，就把对应文件补齐后再次 `complete`
- 如果 `next_action.kind=run_skill` 且阶段是 `旧脚本更新执行`，说明需要按 `legacy_rerecord_instruction.md` 调用 `playwright-test-generator`，产出 `legacy_update_candidate_manifest`
- 如果停在 `manual-review`，说明自动循环已经到边界，需要人工介入

查看状态：

```bash
python -m qa_agent.cli status --run-id <run_id> --next-action
```

推进下一阶段：

```bash
python -m qa_agent.cli next --run-id <run_id>
```

如果 `doctor` 报 fatal，需要先修复内嵌 skill、知识库或项目根目录；如果只有 warning，`run` 会继续创建任务，但会把预检结果保存到本次 run。

完整内部编排契约、阶段门禁和状态持久化说明见 [AGENTS.md]。
