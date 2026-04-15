from __future__ import annotations

import argparse
import json
from pathlib import Path

from qa_agent.config import load_config
from qa_agent.conductor import QAConductor
from qa_agent.models import RunStatus


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qa-agent",
        description="AI 测试编排层：串联 senior-qa-brain、playwright-test-generator、ok_autotest_ui_skill。",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan", aliases=["计划"], help="创建测试计划")
    _add_input_args(plan)

    advance = sub.add_parser("advance", aliases=["推进", "继续"], help="推进到下一阶段")
    advance.add_argument("--run-id", "--运行ID", dest="run_id", required=True)

    complete = sub.add_parser("complete", aliases=["完成阶段"], help="标记当前阶段完成并推进")
    complete.add_argument("--run-id", "--运行ID", dest="run_id", required=True)
    complete.add_argument("--phase", "--阶段", dest="phase", required=True, help="要标记完成的阶段名")
    complete.add_argument("--artifact", "--产物", dest="artifacts", action="append", default=[], help="附加产物 key=path 格式，可多次")

    status = sub.add_parser("status", aliases=["状态"], help="查看运行状态")
    status.add_argument("--run-id", "--运行ID", dest="run_id", required=True)

    return parser


def _add_input_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--figma-url", "--figma链接", dest="figma_url")
    parser.add_argument("--prd-ref", "--需求文档", dest="prd_refs", action="append", default=[])
    parser.add_argument("--site", "--站点", dest="site")
    parser.add_argument("--module", "--模块", dest="module")
    parser.add_argument("--feature", "--功能", dest="feature")
    parser.add_argument("--change-description", "--改动描述", dest="change_description")
    parser.add_argument("--change-mode", "--变更模式", dest="change_mode", default="auto")


def _format_brief(state_data: dict) -> str:
    """一句话状态摘要。"""
    run_id = state_data["run_id"]
    phase = state_data["current_phase"]
    status = state_data["status"]
    mode = state_data["change_mode"]
    reason = state_data.get("blocked_reason", "")

    header = f"[{run_id}] {mode} | {phase}"

    if status == RunStatus.BLOCKED.value and reason:
        return f"{header}\n  → {reason}"
    if status == RunStatus.COMPLETED.value:
        report = state_data.get("artifacts", {}).get("final_report", "")
        return f"{header} | 已完成\n  → 最终报告: {report}" if report else f"{header} | 已完成"
    if status == RunStatus.PLANNED.value:
        return f"{header} | 已计划，使用 advance 开始执行"
    if reason:
        return f"{header}\n  → {reason}"
    return header


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    config = load_config(Path(__file__).resolve().parents[1])
    conductor = QAConductor(config)

    cmd = args.command
    if cmd in ("plan", "计划"):
        inputs = {k: v for k, v in vars(args).items() if k != "command" and v not in (None, [], "")}
        has_figma = bool(inputs.get("figma_url"))
        has_prd = bool(inputs.get("prd_refs"))
        has_desc = bool(inputs.get("change_description"))
        if not has_figma and not has_prd and not has_desc:
            print("参数错误: 至少需要提供以下输入之一：\n"
                  "  --figma-url / --figma链接（新需求）\n"
                  "  --prd-ref / --需求文档（新需求）\n"
                  "  --change-description / --改动描述（回归）")
            return 1
        try:
            state = conductor.plan(inputs)
            print(_format_brief(conductor.status(state.run_id)))
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
            print(_format_brief(data))
            phases = data.get("phase_statuses", {})
            if phases:
                print("\n阶段状态:")
                for name, st in phases.items():
                    print(f"  {name}: {st}")
        except FileNotFoundError as exc:
            print(f"错误: {exc}")
            return 1
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
