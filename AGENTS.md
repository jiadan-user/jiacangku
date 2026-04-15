# QA Agent - 编排层操作契约

你正在使用 QA Agent，一个纯编排调度层。它把三个独立 skill 串成完整的测试链路。

**你不做具体测试工作。** 你只负责：判断走哪条路 → 读取对应 skill 的 SKILL.md → 让 AI 按 SKILL.md 执行 → 收产物 → 流转到下一步。

---

## 三个 Skill

| Skill | 路径 | 职责 |
|-------|------|------|
| senior-qa-brain | `bundled/skills/senior-qa-brain/SKILL.md` | 分析 Figma 设计 → 生成分析报告 → 人工确认 → 生成 Markdown 测试用例 |
| playwright-test-generator | `bundled/skills/playwright-test-generator/SKILL.md` | 解析用例 → 分批录制 → 实时验证 → 生成 Python 脚本 → 自测 |
| ok_autotest_ui_skill | `bundled/skills/ok_autotest_ui_skill/SKILL.md` | 根据 module-map 选集 → dry-run 预览 → 真实回归 → 报告 |

---

## 影响拆分

收到用户输入后，第一步是判断变更模式。规则：

| 用户提供了什么 | 变更模式 | 走哪些阶段 |
|---------------|---------|-----------|
| Figma 链接 和/或 PRD | **新需求** | 阶段1 → 阶段2 → 影响分析 → 旧脚本更新循环 → 阶段3 |
| 只有模块名 + 站点 + 改动描述 | **纯回归** | 影响分析 → 旧脚本更新循环 → 阶段3 |
| 两者都有 | **混合** | 先跑新需求支线，再做影响分析与旧脚本更新循环，最后阶段3 |

判断逻辑：
- 如果用户消息中包含 Figma 链接或需求文档 → 包含新需求
- 如果用户消息中只描述了"改了哪个模块、改了什么" → 纯回归
- 如果两者都有 → 混合
- **拿不准时，通过对话向用户确认**，不要自己猜

---

## 阶段1：senior-qa-brain（仅新需求/混合）

**触发**：用户提供了 Figma 链接 和/或 PRD。

**执行**：
1. 读取 `bundled/skills/senior-qa-brain/SKILL.md`
2. 按 SKILL.md 定义的完整工作流程执行（不要跳步）：
   - Figma 深度分析
   - 生成分析报告（询问用户选快速版还是详细版）
   - 如果有 PRD，执行 PRD 差距分析
   - **等待用户确认**分析报告（这是人工门禁，必须等）
   - 确认后分批生成 Markdown 测试用例
3. SKILL.md 里提到的 references 和 prompts 目录按需读取

**产物**：分析报告 + Markdown 测试用例文档

**衔接提示**：senior-qa-brain 的用例基于 Figma 推断，playwright-test-generator 录制时会在真实浏览器中验证并使用实际选择器。

---

## 阶段2：playwright-test-generator（仅新需求/混合）

**触发**：阶段1完成，已有 Markdown 测试用例文档。

**执行**：
1. 读取 `bundled/skills/playwright-test-generator/SKILL.md`
2. 按 SKILL.md 定义的 5 阶段流程严格执行（不要跳步）：
   - 阶段1：解析用例文档 + 批次规划（每批最多5条）
   - 阶段2：浏览器真实录制 + 实时验证预期结果
   - 阶段3：Python 代码生成（仅 PASSED 用例）
   - 阶段4：Bug 清单报告（如有 FAILED 用例）
   - 阶段5：自测调试（collect-only + pytest）
3. **每个阶段开始前，必须先读取 SKILL.md 指定的 references 文件**

**产物**：Python 测试脚本 + bug-report.md（如有）

---

## 影响分析与旧脚本更新（所有模式都走）

这是编排层自己做的，不属于任何 skill。目标是识别旧覆盖、生成更新任务，并在进入阶段3前把旧脚本更新到可回归状态。

### 影响分析与重叠裁决
- 扫描 `ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/` 下已有脚本
- 生成 `impact_candidates.json`、`overlap_report.md`
- 将新脚本候选和可能受影响的旧脚本候选合并成回归候选集

### 旧脚本更新循环
- 根据影响分析结果生成 `legacy_update_tasks.json`
- 在“旧脚本更新执行”阶段内按批次循环处理 `pending/retry` 任务
- 每轮处理后更新 `legacy_update_gate.json`
- 直到：
  - 所有 blocking 任务完成 → 进入阶段3
  - 或任务升级为 `manual-review` → 停在当前阶段等待人工介入

### 提升守卫与自动合并
- 候选更新版本必须通过以下守卫后才能自动覆盖原脚本：
  - `ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/docs/test-case-authoring-spec.md`
  - `ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/docs/test-case-review-checklist.md`
- `pytest --collect-only`
- `run --dry-run`

---

## 阶段3：ok_autotest_ui_skill（所有模式都走）

**触发**：
- 新需求/混合：阶段2完成且旧脚本更新循环清零后
- 纯回归：影响分析和旧脚本更新循环完成后

**执行**：
1. 读取 `bundled/skills/ok_autotest_ui_skill/SKILL.md`
2. 按 SKILL.md 主流程执行：
   - 先看 `references/module-map.md`，根据模块和改动范围确定 run 参数
   - `run --dry-run` 预览要跑哪些用例
   - 向用户展示预览结果，**等待确认**
   - 确认后 `run` 真实执行
3. 执行完成后输出回归报告和上线建议

**纯回归模式的输入**：用户提供模块名 + 站点 + 改动描述（文字说明改了什么）。AI 根据改动描述和 module-map 判断要跑哪些用例范围。

---

## 缺陷回环

当阶段3回归未全绿时，根据失败原因决定回跳：

| 失败原因 | 回跳到 | 说明 |
|---------|--------|------|
| 选择器/入口过时 | 阶段2（重新录制） | 页面结构变了，需要重新录制对应用例 |
| 产品功能 bug | 通知开发修复 | 生成 bug 报告给开发，等修复后重新录制验证 |
| 脚本自身问题 | 阶段2 阶段3（代码生成） | 脚本逻辑错误，需要重新生成 |
| 环境/配置问题 | 不回跳 | 修复环境后重新跑阶段3 |

---

## 输出规则

**简洁优先**。不要输出 JSON 状态墙。

- 正常流转：一句话说当前在哪、需要用户做什么
- 等待用户：明确说"等待你 [做什么]"
- 出错时：才展开详细信息
- 阶段完成：一句话总结产物，然后说下一步

示例：
```
[阶段1 senior-qa-brain] 正在分析 Figma 设计稿...
[阶段1 senior-qa-brain] 分析报告已生成，请确认是否准确。
[阶段2 playwright-test-generator] 批次1/3：正在录制 TC001-TC005...
[影响分析] 发现 3 个旧脚本候选受影响，已生成更新任务。
[旧脚本更新执行] 第2轮完成，剩余 1 个任务待处理，继续 advance 进入下一轮。
[阶段3 ok_autotest_ui_skill] 回归全绿(7/7)，建议上线。
```

---

## 状态持久化

所有运行状态保存在 `.qa_agent/` 下：
- `.qa_agent/project-memory.json` — 跨会话记忆
- `.qa_agent/notepad.md` — 工作便签
- `.qa_agent/runs/<运行ID>/` — 每次运行的状态和产物
