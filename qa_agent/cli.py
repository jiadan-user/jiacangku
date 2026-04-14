from __future__ import annotations

import argparse
import json
from pathlib import Path

from qa_agent.config import load_config
from qa_agent.conductor import QAConductor
from qa_agent.exceptions import PhaseBlockedError
from qa_agent.presentation import format_status_for_display, normalize_change_mode, normalize_command_name


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qa-agent",
        description="AI 测试资产编排器，用于串联 senior-qa-brain、playwright-test-generator 与回归测试 skill。",
        add_help=False,
    )
    parser.add_argument("-h", "--help", "--帮助", action="help", help="显示帮助并退出。")
    parser._positionals.title = "子命令"
    parser._optionals.title = "可选参数"
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name, aliases, help_text in (
        ("plan", ["计划"], "只生成需求包与执行规划，不推进完整链路。"),
        ("run", ["运行", "执行"], "执行完整编排链路；缺少外部产物时会阻塞并给出下一步说明。"),
    ):
        sub = subparsers.add_parser(name, aliases=aliases, help=help_text, add_help=False)
        sub.add_argument("-h", "--help", "--帮助", action="help", help="显示帮助并退出。")
        sub._optionals.title = "可选参数"
        _add_common_args(sub, include_run_id=True)
        if name == "run":
            sub.add_argument("--analysis-approved", "--分析已确认", dest="analysis_approved", action="store_true", help="确认分析报告已经过人工审核。")
            sub.add_argument("--execute-regression", "--执行回归预演", dest="execute_regression", action="store_true", help="继续执行回归预演阶段。")
            sub.add_argument("--execute-real-run", "--执行真实回归", dest="execute_real_run", action="store_true", help="在回归预演通过后继续执行真实回归。")
            sub.add_argument("--no-auto-promote", "--不自动提升", dest="no_auto_promote", action="store_true", help="跳过脚本自动提升到回归池。")

    status = subparsers.add_parser("status", aliases=["状态"], help="查看指定运行ID的当前状态。", add_help=False)
    status.add_argument("-h", "--help", "--帮助", action="help", help="显示帮助并退出。")
    status._optionals.title = "可选参数"
    status.add_argument("--run-id", "--运行ID", dest="run_id", required=True, help="需要查询的运行ID。")

    resume = subparsers.add_parser("resume", aliases=["恢复", "继续"], help="基于已有运行ID继续执行。", add_help=False)
    resume.add_argument("-h", "--help", "--帮助", action="help", help="显示帮助并退出。")
    resume._optionals.title = "可选参数"
    _add_common_args(resume, include_run_id=False)
    resume.add_argument("--run-id", "--运行ID", dest="run_id", required=True, help="需要继续执行的运行ID。")
    resume.add_argument("--analysis-approved", "--分析已确认", dest="analysis_approved", action="store_true", help="确认分析报告已经过人工审核。")
    resume.add_argument("--execute-regression", "--执行回归预演", dest="execute_regression", action="store_true", help="继续执行回归预演阶段。")
    resume.add_argument("--execute-real-run", "--执行真实回归", dest="execute_real_run", action="store_true", help="在回归预演通过后继续执行真实回归。")
    resume.add_argument("--no-auto-promote", "--不自动提升", dest="no_auto_promote", action="store_true", help="跳过脚本自动提升到回归池。")

    promote = subparsers.add_parser("promote", aliases=["提升", "入库"], help="将已通过提升守卫的脚本提升到回归池。", add_help=False)
    promote.add_argument("-h", "--help", "--帮助", action="help", help="显示帮助并退出。")
    promote._optionals.title = "可选参数"
    promote.add_argument("--run-id", "--运行ID", dest="run_id", required=True, help="需要执行提升的运行ID。")

    return parser


def _add_common_args(parser: argparse.ArgumentParser, include_run_id: bool) -> None:
    if include_run_id:
        parser.add_argument("--run-id", "--运行ID", dest="run_id", help="已有运行ID；为空时会自动新建一次运行。")
    parser.add_argument("--figma-url", "--figma链接", dest="figma_url", help="Figma 原型链接。")
    parser.add_argument("--prd-ref", "--需求文档", dest="prd_refs", action="append", default=[], help="需求文档、PRD、PDF 或其他需求材料路径，可重复传入。")
    parser.add_argument("--git-diff-file", "--git-diff文件", dest="git_diff_file", help="git diff 文件路径。")
    parser.add_argument("--git-diff-summary", "--git-diff摘要", dest="git_diff_summary", help="git diff 的文本摘要。")
    parser.add_argument("--site", "--站点", dest="site", help="站点标识，例如 sg、ae、us。")
    parser.add_argument("--module", "--模块", dest="module", help="业务模块名。")
    parser.add_argument("--feature", "--功能", dest="feature", help="功能名或 feature key。")
    parser.add_argument(
        "--change-mode",
        "--变更模式",
        dest="change_mode",
        default="auto",
        choices=["auto", "自动", "regression_only", "仅回归", "new_feature_only", "仅新需求", "mixed", "混合"],
        help="变更模式；默认自动推断。",
    )
    parser.add_argument("--analysis-report", "--分析报告", dest="analysis_report", help="senior-qa-brain 产出的分析报告路径。")
    parser.add_argument("--testcases-raw", "--原始用例", dest="testcases_raw", help="senior-qa-brain 产出的原始 Markdown 用例路径。")
    parser.add_argument("--testcases-enriched", "--增强用例", dest="testcases_enriched", help="补充 UI Probe 信息后的 Markdown 用例路径。")
    parser.add_argument("--probe-notes", "--探测补充说明", dest="probe_notes", help="UI Probe/MCP 实测补充说明路径。")
    parser.add_argument("--proof-dir", "--证明产物目录", dest="proof_dir", help="playwright-test-generator 产出的证明产物目录。")
    parser.add_argument("--visual-report", "--视觉报告", dest="visual_report", help="视觉门禁报告路径。")
    parser.add_argument("--ui-report", "--UI报告", dest="ui_report", help="UI 门禁报告路径。")
    parser.add_argument("--api-report", "--API报告", dest="api_report", help="API 门禁报告路径。")


def namespace_to_inputs(namespace: argparse.Namespace) -> dict[str, object]:
    data = vars(namespace).copy()
    data["auto_promote"] = not data.pop("no_auto_promote", False)
    data.pop("command", None)
    if "change_mode" in data:
        data["change_mode"] = normalize_change_mode(data.get("change_mode"))
    return {key: value for key, value in data.items() if value not in (None, [], "")}


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    command = normalize_command_name(args.command)
    config = load_config(Path(__file__).resolve().parents[1])
    conductor = QAConductor(config)

    try:
        if command == "plan":
            state = conductor.plan(namespace_to_inputs(args))
            print(json.dumps(format_status_for_display(conductor.status(state.run_id)), indent=2, ensure_ascii=False))
            return 0
        if command == "run":
            state = conductor.run(namespace_to_inputs(args))
            print(json.dumps(format_status_for_display(conductor.status(state.run_id)), indent=2, ensure_ascii=False))
            return 0
        if command == "resume":
            state = conductor.resume(args.run_id, namespace_to_inputs(args))
            print(json.dumps(format_status_for_display(conductor.status(state.run_id)), indent=2, ensure_ascii=False))
            return 0
        if command == "status":
            print(json.dumps(format_status_for_display(conductor.status(args.run_id)), indent=2, ensure_ascii=False))
            return 0
        if command == "promote":
            state = conductor.promote(args.run_id)
            print(json.dumps(format_status_for_display(conductor.status(state.run_id)), indent=2, ensure_ascii=False))
            return 0
    except PhaseBlockedError as exc:
        run_id = getattr(exc, "run_id", None) or getattr(args, "run_id", None)
        if run_id:
            payload = conductor.status(run_id)
            print(json.dumps(format_status_for_display(payload), indent=2, ensure_ascii=False))
        else:
            print(str(exc))
        return 2
    except ValueError as exc:
        print(f"参数错误: {exc}")
        return 1
    except FileNotFoundError as exc:
        print(f"错误: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
