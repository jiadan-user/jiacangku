from __future__ import annotations

from typing import Any

from qa_agent.models import ChangeMode


CHANGE_MODE_ALIASES = {
    "auto": "auto",
    "自动": "auto",
    "regression_only": ChangeMode.REGRESSION_ONLY.value,
    "仅回归": ChangeMode.REGRESSION_ONLY.value,
    "new_feature_only": ChangeMode.NEW_FEATURE_ONLY.value,
    "仅新需求": ChangeMode.NEW_FEATURE_ONLY.value,
    "mixed": ChangeMode.MIXED.value,
    "混合": ChangeMode.MIXED.value,
}

COMMAND_ALIASES = {
    "plan": "plan",
    "计划": "plan",
    "run": "run",
    "运行": "run",
    "执行": "run",
    "status": "status",
    "状态": "status",
    "resume": "resume",
    "恢复": "resume",
    "继续": "resume",
    "promote": "promote",
    "提升": "promote",
    "入库": "promote",
}

TOP_LEVEL_LABELS = {
    "run_id": "运行ID",
    "status": "运行状态",
    "current_phase": "当前阶段",
    "change_mode": "变更模式",
    "blocked_reason": "阻塞原因",
    "created_at": "创建时间",
    "updated_at": "更新时间",
    "phase_statuses": "阶段状态",
    "artifacts": "产物",
    "notes": "备注",
}

ARTIFACT_LABELS = {
    "requirement_packet": "需求包",
    "analysis_bundle": "分析资料包",
    "analysis_next_step": "分析下一步说明",
    "analysis_report": "分析报告",
    "testcase_bundle": "用例生成资料包",
    "testcase_next_step": "用例生成下一步说明",
    "testcases_raw": "原始Markdown用例",
    "probe_notes": "UI Probe补充说明",
    "probe_checklist": "UI Probe检查清单",
    "testcases_enriched": "增强后的Markdown用例",
    "reality_diff": "设计与真实环境差异",
    "case_manifest": "用例清单",
    "module_map_candidate": "module-map候选映射",
    "batch_plan": "批次计划",
    "readiness_gate": "录制准备检查结果",
    "recording_bundle": "录制资料包",
    "recording_next_step": "录制下一步说明",
    "proof_dir": "证明产物目录",
    "proof_artifacts": "证明产物汇总",
    "generated_drafts": "脚本草稿列表",
    "normalized_scripts": "规范化脚本列表",
    "promotion_guard": "提升守卫结果",
    "promoted_scripts": "已提升脚本列表",
    "regression_plan": "回归计划",
    "regression_dry_run": "回归预演结果",
    "regression_run": "回归执行结果",
    "visual_report": "视觉门禁报告",
    "ui_report": "UI门禁报告",
    "api_report": "API门禁报告",
    "gate_report": "门禁汇总报告",
    "final_report": "最终报告",
}


def normalize_change_mode(value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return CHANGE_MODE_ALIASES.get(text.lower(), CHANGE_MODE_ALIASES.get(text, text))


def normalize_command_name(value: str) -> str:
    return COMMAND_ALIASES.get(value, value)


def artifact_label(key: str) -> str:
    return ARTIFACT_LABELS.get(key, key)


def format_status_for_display(payload: dict[str, Any]) -> dict[str, Any]:
    view: dict[str, Any] = {}
    for key, value in payload.items():
        if key == "artifacts" and isinstance(value, dict):
            view[TOP_LEVEL_LABELS[key]] = {artifact_label(name): path for name, path in value.items()}
            continue
        view[TOP_LEVEL_LABELS.get(key, key)] = value
    return view
