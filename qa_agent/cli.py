from __future__ import annotations

import argparse
import json
from pathlib import Path

from qa_agent.config import load_config
from qa_agent.conductor import QAConductor
from qa_agent.models import RunStatus, to_data


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qa-agent",
        description="AI 测试编排层：串联 senior-qa-brain、playwright-test-generator、ok_autotest_ui_skill。",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan", aliases=["计划"], help="创建测试计划")
    _add_input_args(plan)

    run = sub.add_parser("run", aliases=["运行"], help="创建测试计划并推进到第一个可操作点")
    _add_input_args(run)
    run.add_argument("--max-steps", dest="max_steps", type=int)

    advance = sub.add_parser("advance", aliases=["推进", "继续"], help="推进到下一阶段")
    advance.add_argument("--run-id", "--运行ID", dest="run_id", required=True)

    next_cmd = sub.add_parser("next", aliases=["下一步"], help="自动推进到下一个可操作点")
    next_cmd.add_argument("--run-id", "--运行ID", dest="run_id", required=True)
    next_cmd.add_argument("--max-steps", dest="max_steps", type=int)
    next_cmd.add_argument("--doctor", action="store_true", help="推进前重新执行环境预检")

    complete = sub.add_parser("complete", aliases=["完成阶段"], help="提交当前阶段产物并触发门禁验收")
    complete.add_argument("--run-id", "--运行ID", dest="run_id", required=True)
    complete.add_argument("--phase", "--阶段", dest="phase", required=True, help="要标记完成的阶段名")
    complete.add_argument(
        "--artifact",
        "--产物",
        dest="artifacts",
        action="append",
        default=[],
        help="附加产物 key=path 格式，可多次；阶段1/2/3/KB 都会按产物做门禁校验",
    )

    status = sub.add_parser("status", aliases=["状态"], help="查看运行状态")
    status.add_argument("--run-id", "--运行ID", dest="run_id", required=True)
    status.add_argument("--next-action", action="store_true", help="显示下一步结构化行动")
    status.add_argument("--json", action="store_true", help="输出完整 JSON 状态")
    status.add_argument("--verbose", action="store_true", help="显示 artifacts 等详细信息")

    sub.add_parser("doctor", aliases=["环境检查"], help="执行 QA Agent 环境预检")

    return parser


def _add_input_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--figma-url", "--figma链接", dest="figma_url")
    parser.add_argument("--prd-ref", "--需求文档", dest="prd_refs", action="append", default=[])
    parser.add_argument("--site", "--站点", dest="site")
    parser.add_argument("--module", "--模块", dest="module")
    parser.add_argument("--feature", "--功能", dest="feature")
    parser.add_argument("--change-description", "--改动描述", dest="change_description")
    parser.add_argument("--change-mode", "--变更模式", dest="change_mode")


def _format_brief(state_data: dict) -> str:
    """一句话状态摘要。"""
    run_id = state_data["run_id"]
    phase = state_data["current_phase"]
    status = state_data["status"]
    mode = state_data["change_mode"]
    reason = state_data.get("blocked_reason", "")
    error_reason = state_data.get("error_reason", "")
    stale_warning = state_data.get("stale_warning", "")

    header = f"[{run_id}] {mode} | {phase}"

    if status == RunStatus.ERROR.value:
        return f"{header} | 执行出错\n  → {error_reason or reason}"
    if status == RunStatus.BLOCKED.value and reason:
        suffix = f"\n  → {stale_warning}" if stale_warning else ""
        return f"{header}\n  → {reason}{suffix}"
    if status == RunStatus.COMPLETED.value:
        report = state_data.get("artifacts", {}).get("final_report", "")
        return f"{header} | 已完成\n  → 最终报告: {report}" if report else f"{header} | 已完成"
    if status == RunStatus.PLANNED.value:
        return f"{header} | 已计划，使用 advance 开始执行"
    if reason:
        return f"{header}\n  → {reason}"
    return header


def _format_next_action(state_data: dict) -> str:
    action = state_data.get("next_action", {}) or {}
    if not action:
        return "下一步: 暂无"
    lines = [
        f"下一步: {action.get('summary', '')}",
        f"- kind: {action.get('kind', '')}",
        f"- phase: {action.get('phase', '')}",
    ]
    if action.get("skill_path"):
        lines.append(f"- skill: {action['skill_path']}")
    if action.get("instruction_path"):
        lines.append(f"- instruction: {action['instruction_path']}")
    if action.get("required_artifacts"):
        lines.append("- required_artifacts: " + ", ".join(action["required_artifacts"]))
    if action.get("resume_command"):
        lines.append(f"- resume: {action['resume_command']}")
    return "\n".join(lines)


def _format_doctor(result) -> str:
    payload = to_data(result)
    lines = ["QA Agent doctor:"]
    for check in payload.get("checks", []):
        status = "OK" if check.get("ok") else check.get("severity", "warning").upper()
        lines.append(f"- [{status}] {check.get('name')}: {check.get('message')}")
    return "\n".join(lines)


def _doctor_has_fatal(result) -> bool:
    return bool(getattr(result, "has_fatal", False))


def _validate_plan_inputs(args, inputs: dict) -> str:
    if not args.change_mode:
        return (
            "参数错误: 必须显式选择变更模式：\n"
            "  A 新需求模式  -> --change-mode 新需求\n"
            "  B 纯回归模式  -> --change-mode 纯回归\n"
            "  C 混合模式    -> --change-mode 混合"
        )
    has_figma = bool(inputs.get("figma_url"))
    has_prd = bool(inputs.get("prd_refs"))
    has_desc = bool(inputs.get("change_description"))
    if not has_figma and not has_prd and not has_desc:
        return (
            "参数错误: 至少需要提供以下输入之一：\n"
            "  --figma-url / --figma链接（新需求）\n"
            "  --prd-ref / --需求文档（新需求）\n"
            "  --change-description / --改动描述（回归）"
        )
    return ""


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    config = load_config(Path(__file__).resolve().parents[1])
    conductor = QAConductor(config)

    cmd = args.command
    if cmd in ("plan", "计划"):
        inputs = {k: v for k, v in vars(args).items() if k != "command" and v not in (None, [], "")}
        validation_error = _validate_plan_inputs(args, inputs)
        if validation_error:
            print(validation_error)
            return 1
        try:
            state = conductor.plan(inputs)
            print(_format_brief(conductor.status(state.run_id)))
        except Exception as exc:
            print(f"错误: {exc}")
            return 1
        return 0

    if cmd in ("run", "运行"):
        inputs = {k: v for k, v in vars(args).items() if k != "command" and v not in (None, [], "")}
        validation_error = _validate_plan_inputs(args, inputs)
        if validation_error:
            print(validation_error)
            return 1
        doctor_result = conductor.doctor()
        print(_format_doctor(doctor_result))
        if _doctor_has_fatal(doctor_result):
            print("doctor 存在 fatal 项，未创建 run。")
            return 1
        inputs["doctor_result"] = to_data(doctor_result)
        try:
            state = conductor.plan(inputs)
            state = conductor.drive_to_action(state.run_id, max_steps=args.max_steps)
            data = conductor.status(state.run_id)
            print(_format_brief(data))
            print(_format_next_action(data))
        except Exception as exc:
            print(f"错误: {exc}")
            return 1
        return 0

    if cmd in ("advance", "推进", "继续"):
        try:
            state = conductor.advance(args.run_id)
            print(_format_brief(conductor.status(state.run_id)))
        except FileNotFoundError as exc:
            print(f"错误: {exc}")
            return 1
        return 0

    if cmd in ("next", "下一步"):
        try:
            if args.doctor:
                doctor_result = conductor.doctor()
                print(_format_doctor(doctor_result))
                if _doctor_has_fatal(doctor_result):
                    return 1
            state = conductor.drive_to_action(args.run_id, max_steps=args.max_steps)
            data = conductor.status(state.run_id)
            print(_format_brief(data))
            print(_format_next_action(data))
        except FileNotFoundError as exc:
            print(f"错误: {exc}")
            return 1
        return 0

    if cmd in ("complete", "完成阶段"):
        artifacts = {}
        for item in (args.artifacts or []):
            if "=" in item:
                k, v = item.split("=", 1)
                artifacts[k] = v
        try:
            state = conductor.complete_phase(args.run_id, args.phase, artifacts or None)
            print(_format_brief(conductor.status(state.run_id)))
        except FileNotFoundError as exc:
            print(f"错误: {exc}")
            return 1
        return 0

    if cmd in ("status", "状态"):
        try:
            data = conductor.status(args.run_id)
            if args.json:
                print(json.dumps(data, ensure_ascii=False, indent=2))
                return 0
            print(_format_brief(data))
            if args.next_action:
                print(_format_next_action(data))
            phases = data.get("phase_statuses", {})
            if phases:
                print("\n阶段状态:")
                for name, st in phases.items():
                    print(f"  {name}: {st}")
            if args.verbose:
                artifacts = data.get("artifacts", {})
                if artifacts:
                    print("\n产物:")
                    for name, path in sorted(artifacts.items()):
                        print(f"  {name}: {path}")
        except FileNotFoundError as exc:
            print(f"错误: {exc}")
            return 1
        return 0

    if cmd in ("doctor", "环境检查"):
        result = conductor.doctor()
        print(_format_doctor(result))
        return 1 if _doctor_has_fatal(result) else 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
