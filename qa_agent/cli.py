from __future__ import annotations

import argparse
import json
import os
import re
import signal
import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

from qa_agent.agent_memory import MemoryExporter, MemoryRetriever, MemoryStore
from qa_agent.agent_memory.candidate import build_candidate_from_text
from qa_agent.agent_memory.models import to_data as memory_to_data
from qa_agent.config import load_config
from qa_agent.conductor import QAConductor
from qa_agent.dashboard_publish import publish_coverage, publish_ok_ui_run, publish_run
from qa_agent.io import write_json
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

    memory = sub.add_parser("memory", aliases=["记忆"], help="独立 Agent Memory 管理")
    memory_sub = memory.add_subparsers(dest="memory_command", required=True)

    memory_sub.add_parser("init", aliases=["初始化"], help="初始化 .agent_memory 目录")

    search = memory_sub.add_parser("search", aliases=["搜索"], help="搜索正式记忆")
    search.add_argument("query", help="搜索关键词")
    search.add_argument("--scope", action="append", default=[], help="限定 scope，可多次传入")
    search.add_argument("--limit", type=int, default=8)
    search.add_argument("--json", action="store_true")

    suggest = memory_sub.add_parser("suggest", aliases=["候选"], help="生成候选记忆，不写入正式记忆")
    suggest.add_argument("--text", required=True, help="需要沉淀的纠错、偏好或结论")
    suggest.add_argument("--type", default="correction", choices=["correction", "decision", "preference", "lesson", "summary"])
    suggest.add_argument("--scope", action="append", default=[])
    suggest.add_argument("--tag", action="append", default=[])
    suggest.add_argument("--priority", default="high", choices=["pinned", "high", "medium", "low"])
    suggest.add_argument("--risk", default="medium", choices=["low", "medium", "high"])
    suggest.add_argument("--run-id")
    suggest.add_argument("--json", action="store_true")

    list_pending = memory_sub.add_parser("list-pending", aliases=["待确认"], help="列出待确认候选记忆")
    list_pending.add_argument("--json", action="store_true")

    promote = memory_sub.add_parser("promote", aliases=["写入"], help="把候选记忆写入正式记忆")
    promote.add_argument("--id", dest="candidate_id")
    promote.add_argument("--all-recommended", action="store_true", help="写入所有 suggested_action=promote 的 pending 候选")
    promote.add_argument("--json", action="store_true")

    reject = memory_sub.add_parser("reject", aliases=["拒绝"], help="拒绝候选记忆")
    reject.add_argument("--id", dest="candidate_id", required=True)
    reject.add_argument("--json", action="store_true")

    export = memory_sub.add_parser("export", aliases=["导出"], help="导出给不同 AI 工具读取的记忆上下文")
    export.add_argument("--target", required=True, choices=["qa-agent", "claude", "cursor"])
    export.add_argument("--query", default="")
    export.add_argument("--limit", type=int, default=8)

    dashboard = sub.add_parser("dashboard", help="QA Agent Dashboard 发布")
    dashboard_sub = dashboard.add_subparsers(dest="dashboard_command", required=True)
    dashboard_publish = dashboard_sub.add_parser("publish", help="发布本地 run 到 ui_test_management")
    dashboard_publish.add_argument("--run-id", required=True)
    dashboard_publish.add_argument("--url", help="ui_test_management 地址，默认 http://10.192.35.53:8001，可用 QA_AGENT_DASHBOARD_URL 覆盖")
    dashboard_publish.add_argument("--api-key", help="发布 API Key，默认读取 QA_AGENT_DASHBOARD_API_KEY")
    dashboard_publish.add_argument("--allow-incomplete", action="store_true", help="允许手动发布未完成 run，用于调试")
    dashboard_publish.add_argument("--json", action="store_true")
    dashboard_coverage = dashboard_sub.add_parser("publish-coverage", help="只刷新项目用例覆盖度快照")
    dashboard_coverage.add_argument("--url", help="ui_test_management 地址，默认 http://10.192.35.53:8001，可用 QA_AGENT_DASHBOARD_URL 覆盖")
    dashboard_coverage.add_argument("--api-key", help="发布 API Key，默认读取 QA_AGENT_DASHBOARD_API_KEY")
    dashboard_coverage.add_argument("--project-key", default="OK", help="目标项目名，默认 OK")
    dashboard_coverage.add_argument("--json", action="store_true")
    dashboard_ok_ui_publish = dashboard_sub.add_parser("publish-ok-ui-run", help="发布单独 ok_autotest_ui_skill run 到 ui_test_management")
    dashboard_ok_ui_publish.add_argument("--ok-ui-run-id", help="OK UI skill 输出的 run_id；不传则读取 ok_test_latest_run.txt")
    dashboard_ok_ui_publish.add_argument("--url", help="ui_test_management 地址，默认 http://10.192.35.53:8001，可用 QA_AGENT_DASHBOARD_URL 覆盖")
    dashboard_ok_ui_publish.add_argument("--api-key", help="发布 API Key，默认读取 QA_AGENT_DASHBOARD_API_KEY")
    dashboard_ok_ui_publish.add_argument("--project-key", default="OK", help="目标项目名，默认 OK")
    dashboard_ok_ui_publish.add_argument("--module", help="覆盖展示用模块；不传则读取 OK UI summary.selected_modules")
    dashboard_ok_ui_publish.add_argument("--site", help="覆盖展示用站点；不传则读取 OK UI summary.selection.site")
    dashboard_ok_ui_publish.add_argument("--change-mode", default="OK UI 独立回归", help="平台执行模式展示文案")
    dashboard_ok_ui_publish.add_argument("--json", action="store_true")
    dashboard_ok_ui_run = dashboard_sub.add_parser("run-ok-ui", help="按精确条件执行 OK UI 用例并发布到 ui_test_management")
    dashboard_ok_ui_run.add_argument("--module")
    dashboard_ok_ui_run.add_argument("--feature")
    dashboard_ok_ui_run.add_argument("--story")
    dashboard_ok_ui_run.add_argument("--priority")
    dashboard_ok_ui_run.add_argument("--site")
    dashboard_ok_ui_run.add_argument("--case-id")
    dashboard_ok_ui_run.add_argument("--path")
    dashboard_ok_ui_run.add_argument("--nodeid")
    dashboard_ok_ui_run.add_argument("--workers", default="1", help="并发 worker 数，支持 1、正整数或 auto；默认 1")
    dashboard_ok_ui_run.add_argument("--max-workers", type=int)
    dashboard_ok_ui_run.add_argument("--artifact-retention", choices=["full", "lean"])
    dashboard_ok_ui_run.add_argument("--case-timeout", type=int, help="单条用例超时秒数，默认由 OK UI runner 决定；0 表示关闭")
    dashboard_ok_ui_run.add_argument("--idle-timeout", type=int, help="pytest 阶段无输出/无产物进展超时秒数，默认由 OK UI runner 决定；0 表示关闭")
    dashboard_ok_ui_run.add_argument("--phase-timeout", type=int, help="pytest 阶段总时长硬上限秒数，默认关闭")
    dashboard_ok_ui_run.add_argument("--failed-reruns", type=int, help="失败用例二次执行次数，默认由 OK UI runner 决定；0 表示关闭")
    dashboard_ok_ui_run.add_argument("--outer-timeout", type=int, default=0, help="qa-agent 外层最终兜底超时秒数，默认关闭")
    dashboard_ok_ui_run.add_argument("--url", help="ui_test_management 地址，默认 http://10.192.35.53:8001，可用 QA_AGENT_DASHBOARD_URL 覆盖")
    dashboard_ok_ui_run.add_argument("--api-key", help="发布 API Key，默认读取 QA_AGENT_DASHBOARD_API_KEY")
    dashboard_ok_ui_run.add_argument("--project-key", default="OK", help="目标项目名，默认 OK")
    dashboard_ok_ui_run.add_argument("--change-mode", default="OK UI 独立回归", help="平台执行模式展示文案")
    dashboard_ok_ui_run.add_argument("--json", action="store_true")

    return parser


def _add_input_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--figma-url", "--figma链接", dest="figma_url")
    parser.add_argument("--prd-ref", "--需求文档", dest="prd_refs", action="append", default=[])
    parser.add_argument("--site", "--站点", dest="site", action="append")
    parser.add_argument("--module", "--模块", dest="module", action="append")
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


def _ok_ui_script_path(config) -> Path:
    return config.project_root / "bundled" / "skills" / "ok_autotest_ui_skill" / "scripts" / "ok_test.py"


def _add_optional_cli_arg(command: list[str], flag: str, value) -> None:
    if value not in (None, "", []):
        command.extend([flag, str(value)])


def _build_ok_ui_run_command(config, args) -> list[str]:
    script = _ok_ui_script_path(config)
    command = [sys.executable, str(script), "run"]
    for attr, flag in (
        ("module", "--module"),
        ("feature", "--feature"),
        ("story", "--story"),
        ("priority", "--priority"),
        ("site", "--site"),
        ("case_id", "--case-id"),
        ("path", "--path"),
        ("nodeid", "--nodeid"),
        ("workers", "--workers"),
        ("max_workers", "--max-workers"),
        ("artifact_retention", "--artifact-retention"),
        ("case_timeout", "--case-timeout"),
        ("idle_timeout", "--idle-timeout"),
        ("phase_timeout", "--phase-timeout"),
        ("failed_reruns", "--failed-reruns"),
    ):
        _add_optional_cli_arg(command, flag, getattr(args, attr, None))
    return command


def _process_descendants(pid: int) -> list[int]:
    try:
        result = subprocess.run(["pgrep", "-P", str(pid)], capture_output=True, text=True)
    except (OSError, ValueError):
        return []
    if result.returncode not in (0, 1):
        return []
    descendants: list[int] = []
    for raw in result.stdout.split():
        try:
            child = int(raw)
        except ValueError:
            continue
        descendants.append(child)
        descendants.extend(_process_descendants(child))
    return descendants


def _terminate_process_tree(process: subprocess.Popen, *, grace_seconds: float = 3.0) -> None:
    pids = [process.pid, *_process_descendants(process.pid)]
    pgids: set[int] = set()
    for pid in pids:
        try:
            pgids.add(os.getpgid(pid))
        except OSError:
            continue
    for sig in (signal.SIGTERM, signal.SIGKILL):
        for pgid in sorted(pgids):
            try:
                os.killpg(pgid, sig)
            except OSError:
                pass
        try:
            process.wait(timeout=grace_seconds if sig == signal.SIGTERM else 1.0)
            return
        except subprocess.TimeoutExpired:
            continue


def _run_ok_ui_command(command: list[str], *, cwd: Path, timeout_seconds: int = 0, stream: bool = False) -> tuple[int, str, str, bool]:
    process = subprocess.Popen(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT if stream else subprocess.PIPE,
        text=True,
        bufsize=1,
        start_new_session=True,
    )
    stdout_lines: list[str] = []
    stderr_text = ""
    timed_out = False

    if stream:
        assert process.stdout is not None

        def _reader() -> None:
            for line in process.stdout:
                stdout_lines.append(line)
                print(line, end="")

        reader = threading.Thread(target=_reader, daemon=True)
        reader.start()
        try:
            returncode = process.wait(timeout=timeout_seconds or None)
        except subprocess.TimeoutExpired:
            timed_out = True
            _terminate_process_tree(process)
            returncode = process.returncode if process.returncode is not None else -9
        reader.join(timeout=2)
        if process.stdout is not None:
            process.stdout.close()
        return returncode, "".join(stdout_lines), "", timed_out

    try:
        stdout_text, stderr_text = process.communicate(timeout=timeout_seconds or None)
        return process.returncode, stdout_text or "", stderr_text or "", timed_out
    except subprocess.TimeoutExpired:
        timed_out = True
        _terminate_process_tree(process)
        try:
            stdout_text, stderr_text = process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            _terminate_process_tree(process, grace_seconds=0.5)
            stdout_text, stderr_text = "", ""
        return process.returncode if process.returncode is not None else -9, stdout_text or "", stderr_text or "", timed_out


def _extract_ok_ui_run_id(output: str) -> str:
    match = re.search(r"(?m)^run_id=(\S+)\s*$", output)
    return match.group(1) if match else ""


def _format_duration(seconds) -> str:
    try:
        total = int(round(float(seconds or 0)))
    except (TypeError, ValueError):
        total = 0
    minutes, secs = divmod(total, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h{minutes}m{secs}s"
    if minutes:
        return f"{minutes}m{secs}s"
    return f"{secs}s"


def _format_phase_timings(state_data: dict) -> str:
    timings = state_data.get("phase_timings", {}) or {}
    if not isinstance(timings, dict):
        return ""
    lines = ["阶段耗时:"]
    for phase_name, timing in timings.items():
        if not isinstance(timing, dict) or not timing.get("started_at"):
            continue
        blocked_seconds = float(timing.get("blocked_seconds") or 0)
        wall_seconds = float(timing.get("wall_seconds") or 0)
        now = datetime.now(timezone.utc)
        if timing.get("blocked_at"):
            try:
                blocked_seconds += max(0.0, (now - datetime.fromisoformat(timing["blocked_at"])).total_seconds())
            except (TypeError, ValueError):
                pass
        if timing.get("started_at") and not timing.get("completed_at"):
            try:
                wall_seconds = max(wall_seconds, (now - datetime.fromisoformat(timing["started_at"])).total_seconds())
            except (TypeError, ValueError):
                pass
        lines.append(
            "  "
            f"{phase_name}: active={_format_duration(timing.get('active_seconds'))}, "
            f"wait={_format_duration(blocked_seconds)}, "
            f"wall={_format_duration(wall_seconds)}, "
            f"status={timing.get('last_status', '')}"
        )
    return "\n".join(lines) if len(lines) > 1 else ""


def _format_doctor(result) -> str:
    payload = to_data(result)
    lines = ["QA Agent doctor:"]
    for check in payload.get("checks", []):
        status = "OK" if check.get("ok") else check.get("severity", "warning").upper()
        lines.append(f"- [{status}] {check.get('name')}: {check.get('message')}")
    return "\n".join(lines)


def _doctor_has_fatal(result) -> bool:
    return bool(getattr(result, "has_fatal", False))


def _maybe_publish_dashboard(config, state_data: dict) -> None:
    if state_data.get("status") != RunStatus.COMPLETED.value:
        return
    if os.getenv("QA_AGENT_DASHBOARD_ENABLED", "true").lower() not in {"1", "true", "yes", "on"}:
        result = {
            "success": False,
            "skipped": True,
            "reason": "QA_AGENT_DASHBOARD_ENABLED disabled",
        }
        result_path = config.project_root / ".qa_agent" / "runs" / state_data["run_id"] / "dashboard_publish_result.json"
        write_json(result_path, result)
        print(f"Dashboard 发布跳过: {result['reason']}")
        return
    result = publish_run(config.project_root, state_data["run_id"])
    if result.get("success"):
        print(f"Dashboard 发布成功: {result.get('run_uid', state_data['run_id'])}")
    elif result.get("skipped"):
        print(f"Dashboard 发布跳过: {result.get('reason')}")
    else:
        print(f"Dashboard 发布失败，可稍后补发: {result.get('error') or result.get('reason')}")


def _memory_root(config) -> Path:
    return config.agent_memory_root


def _format_memory_results(results) -> str:
    if not results:
        return "未找到相关正式记忆。"
    lines = ["相关记忆:"]
    for item in results:
        memory = item.memory
        scope = ", ".join(memory.scope) if memory.scope else "general"
        lines.append(f"- {memory.id} [{memory.priority}] {memory.title} ({memory.type}; {scope})")
        lines.append(f"  {memory.content}")
    return "\n".join(lines)


def _format_candidates(candidates) -> str:
    if not candidates:
        return "暂无待确认候选记忆。"
    lines = ["待确认候选记忆:"]
    for candidate in candidates:
        scope = ", ".join(candidate.scope) if candidate.scope else "general"
        conflict = f" | conflict: {', '.join(candidate.conflict_ids)}" if candidate.conflict_ids else ""
        lines.append(
            f"- {candidate.id} [{candidate.risk}/{candidate.suggested_action}] "
            f"{candidate.title} ({candidate.type}; {scope}){conflict}"
        )
        lines.append(f"  {candidate.content}")
    return "\n".join(lines)


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

    cmd = args.command
    if cmd in ("memory", "记忆"):
        store = MemoryStore(_memory_root(config))
        subcmd = args.memory_command
        try:
            if subcmd in ("init", "初始化"):
                store.init()
                print(f"Agent Memory 已初始化: {store.root}")
                return 0

            if subcmd in ("search", "搜索"):
                results = MemoryRetriever(store.root).search(args.query, scopes=args.scope, limit=args.limit)
                if args.json:
                    print(json.dumps([memory_to_data(item) for item in results], ensure_ascii=False, indent=2))
                else:
                    print(_format_memory_results(results))
                return 0

            if subcmd in ("suggest", "候选"):
                candidate = build_candidate_from_text(
                    args.text,
                    memory_type=args.type,
                    scope=args.scope or None,
                    tags=args.tag or None,
                    priority=args.priority,
                    risk=args.risk,
                    run_id=args.run_id,
                )
                candidate = store.append_candidate(candidate)
                if args.json:
                    print(json.dumps(memory_to_data(candidate), ensure_ascii=False, indent=2))
                else:
                    print(f"候选记忆已生成: {candidate.id}")
                    if candidate.conflict_ids:
                        print(f"提示: 发现潜在冲突，需人工确认: {', '.join(candidate.conflict_ids)}")
                return 0

            if subcmd in ("list-pending", "待确认"):
                candidates = store.list_candidates()
                if args.json:
                    print(json.dumps([memory_to_data(item) for item in candidates], ensure_ascii=False, indent=2))
                else:
                    print(_format_candidates(candidates))
                return 0

            if subcmd in ("promote", "写入"):
                promoted = []
                if args.all_recommended:
                    for candidate in store.list_candidates():
                        if candidate.suggested_action == "promote" and not candidate.conflict_ids:
                            promoted.append(store.promote(candidate.id))
                else:
                    if not args.candidate_id:
                        print("参数错误: promote 需要 --id，或使用 --all-recommended")
                        return 1
                    promoted.append(store.promote(args.candidate_id))
                if args.json:
                    print(json.dumps([memory_to_data(item) for item in promoted], ensure_ascii=False, indent=2))
                else:
                    print(f"已写入正式记忆: {len(promoted)} 条")
                    for memory in promoted:
                        print(f"- {memory.id}: {memory.title}")
                return 0

            if subcmd in ("reject", "拒绝"):
                candidate = store.reject(args.candidate_id)
                if args.json:
                    print(json.dumps(memory_to_data(candidate), ensure_ascii=False, indent=2))
                else:
                    print(f"已拒绝候选记忆: {candidate.id}")
                return 0

            if subcmd in ("export", "导出"):
                output = MemoryExporter(store.root).export(args.target, query=args.query, limit=args.limit)
                print(f"记忆上下文已导出: {output}")
                return 0
        except Exception as exc:
            print(f"错误: {exc}")
            return 1

    if cmd == "dashboard":
        if args.dashboard_command == "publish":
            try:
                result = publish_run(
                    config.project_root,
                    args.run_id,
                    base_url=args.url,
                    api_key=args.api_key,
                    allow_incomplete=args.allow_incomplete,
                )
                if args.json:
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                elif result.get("success"):
                    print(f"Dashboard 发布成功: {result.get('run_uid', args.run_id)}")
                    if result.get("report_url"):
                        print(f"报告: {result['report_url']}")
                else:
                    print(f"Dashboard 发布失败: {result.get('error') or result.get('reason')}")
                return 0 if result.get("success") else 1
            except Exception as exc:
                print(f"错误: {exc}")
                return 1
        if args.dashboard_command == "publish-coverage":
            try:
                result = publish_coverage(
                    config.project_root,
                    base_url=args.url,
                    api_key=args.api_key,
                    project_key=args.project_key,
                )
                if args.json:
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                elif result.get("success"):
                    print(f"覆盖度发布成功: project_id={result.get('project_id')}")
                else:
                    print(f"覆盖度发布失败: {result.get('error') or result.get('reason')}")
                return 0 if result.get("success") else 1
            except Exception as exc:
                print(f"错误: {exc}")
                return 1
        if args.dashboard_command == "publish-ok-ui-run":
            try:
                result = publish_ok_ui_run(
                    config.project_root,
                    args.ok_ui_run_id,
                    base_url=args.url,
                    api_key=args.api_key,
                    project_key=args.project_key,
                    module=args.module,
                    site=args.site,
                    change_mode=args.change_mode,
                )
                if args.json:
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                elif result.get("success"):
                    print(f"OK UI run 发布成功: {result.get('run_uid', args.ok_ui_run_id or 'latest')}")
                    if result.get("report_url"):
                        print(f"报告: {result['report_url']}")
                else:
                    print(f"OK UI run 发布失败: {result.get('error') or result.get('reason')}")
                return 0 if result.get("success") else 1
            except Exception as exc:
                print(f"错误: {exc}")
                return 1
        if args.dashboard_command == "run-ok-ui":
            try:
                command = _build_ok_ui_run_command(config, args)
                outer_timeout = int(getattr(args, "outer_timeout", 0) or os.getenv("QA_AGENT_OK_UI_OUTER_TIMEOUT", "0") or 0)
                if args.json:
                    returncode, stdout, stderr, outer_timed_out = _run_ok_ui_command(
                        command,
                        cwd=config.project_root,
                        timeout_seconds=outer_timeout,
                        stream=False,
                    )
                else:
                    returncode, stdout, stderr, outer_timed_out = _run_ok_ui_command(
                        command,
                        cwd=config.project_root,
                        timeout_seconds=outer_timeout,
                        stream=True,
                    )
                combined_output = "\n".join(item for item in [stdout, stderr] if item)
                ok_ui_run_id = _extract_ok_ui_run_id(combined_output)
                publish_result = {}
                if ok_ui_run_id:
                    try:
                        publish_result = publish_ok_ui_run(
                            config.project_root,
                            ok_ui_run_id,
                            base_url=args.url,
                            api_key=args.api_key,
                            project_key=args.project_key,
                            module=args.module,
                            site=args.site,
                            change_mode=args.change_mode,
                        )
                    except Exception as exc:
                        publish_result = {
                            "success": False,
                            "skipped": bool(outer_timed_out),
                            "reason": str(exc),
                        }
                elif outer_timed_out:
                    publish_result = {
                        "success": False,
                        "skipped": True,
                        "reason": "OK UI outer timeout triggered before run_id was available; publish skipped",
                    }
                else:
                    publish_result = {"success": False, "error": "OK UI run_id not found in command output"}
                if args.json:
                    print(
                        json.dumps(
                            {
                                "ok_ui_returncode": returncode,
                                "ok_ui_run_id": ok_ui_run_id,
                                "outer_timed_out": outer_timed_out,
                                "publish_result": publish_result,
                                "stdout": stdout,
                                "stderr": stderr,
                            },
                            ensure_ascii=False,
                            indent=2,
                        )
                    )
                else:
                    if publish_result.get("success"):
                        print(f"OK UI run 已发布到 Dashboard: {publish_result.get('run_uid', ok_ui_run_id)}")
                        if publish_result.get("report_url"):
                            print(f"报告: {publish_result['report_url']}")
                    elif publish_result.get("skipped"):
                        print(f"OK UI run 发布跳过: {publish_result.get('reason')}")
                    else:
                        print(f"OK UI run 发布失败: {publish_result.get('error') or publish_result.get('reason')}")
                if returncode != 0:
                    return returncode
                return 0 if publish_result.get("success") else 1
            except Exception as exc:
                print(f"错误: {exc}")
                return 1

    conductor = QAConductor(config)

    if cmd in ("plan", "计划"):
        inputs = {k: v for k, v in vars(args).items() if k != "command" and v not in (None, [], "")}
        validation_error = _validate_plan_inputs(args, inputs)
        if validation_error:
            print(validation_error)
            return 1
        try:
            state = conductor.plan(inputs)
            data = conductor.status(state.run_id)
            print(_format_brief(data))
            timing_text = _format_phase_timings(data)
            if timing_text:
                print(timing_text)
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
            timing_text = _format_phase_timings(data)
            if timing_text:
                print(timing_text)
            print(_format_next_action(data))
            _maybe_publish_dashboard(config, data)
        except Exception as exc:
            print(f"错误: {exc}")
            return 1
        return 0

    if cmd in ("advance", "推进", "继续"):
        try:
            state = conductor.advance(args.run_id)
            data = conductor.status(state.run_id)
            print(_format_brief(data))
            timing_text = _format_phase_timings(data)
            if timing_text:
                print(timing_text)
            _maybe_publish_dashboard(config, data)
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
            timing_text = _format_phase_timings(data)
            if timing_text:
                print(timing_text)
            print(_format_next_action(data))
            _maybe_publish_dashboard(config, data)
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
            data = conductor.status(state.run_id)
            print(_format_brief(data))
            timing_text = _format_phase_timings(data)
            if timing_text:
                print(timing_text)
            _maybe_publish_dashboard(config, data)
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
            timing_text = _format_phase_timings(data)
            if timing_text:
                print("\n" + timing_text)
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
