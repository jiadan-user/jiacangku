#!/usr/bin/env python3
"""
以无头模式、多线程并行跑 ``test_cases/zhaopin`` 下每个 ``test_*.py`` 脚本（一线程一文件，线程内
``subprocess`` 起独立 pytest 进程，避免单进程多 pytest/Playwright 状态冲突）。

- 为每个脚本统计墙钟执行时长
- 汇总并输出失败、跳过的用例
- 合并各子任务的 JUnit，可配合 ``summarize_zhaopin_run.py`` 或本脚本内置 Markdown 报告
- 每个 ``test_*.py`` 另生成独立报告：``<out_dir>/per_script_reports/<stem>_run_report.md``
- 仅重跑有失败用例的脚本：``--failed-from-junit <合并后的 junit 路径>``（一线程一文件，与全量相同）

用法（在 ``ok_autotest_ui_pc`` 包根目录执行，见下方 --help）::

  cd /path/to/ok_autotest_ui_pc
  python3 test_cases/zhaopin/run_zhaopin_parallel_headless.py
  python3 test_cases/zhaopin/run_zhaopin_parallel_headless.py --until-pass
  python3 test_cases/zhaopin/run_zhaopin_parallel_headless.py --failed-from-junit test_cases/zhaopin/parallel_headless_run_*/zhaopin_parallel_merged_junit.xml

环境：
  默认设置 ``HEADLESS=1``；可再加 ``CI=1`` 等与 ``conftest`` 中 ``_effective_headless`` 一致。

依赖：标准库 + 本目录 ``summarize_zhaopin_run.summarize_junit``（可选，用于与既有汇总一致）。
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TextIO

# 与 summarize_zhaopin_run 同目录
_HERE = Path(__file__).resolve().parent
_PC_ROOT = _HERE.parent.parent  # .../ok_autotest_ui_pc
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from summarize_zhaopin_run import (  # noqa: E402
    build_markdown,
    parse_time_from_console,
    summarize_junit,
)


@dataclass
class ScriptRunResult:
    relpath: str
    returncode: int
    wall_seconds: float
    junit_path: Path
    log_path: Path
    error: str | None = None


@dataclass
class ThreadResult:
    script: str
    result: ScriptRunResult
    exc: str | None = None


def discover_test_files(zhaopin_dir: Path) -> list[Path]:
    return sorted(p for p in zhaopin_dir.glob("test_*.py") if p.is_file())


def _failed_script_basenames_from_summary(data: dict) -> set[str]:
    """从 ``summarize_junit`` 结果中收集曾出现失败或 error 的 ``test_*.py`` 文件名（basename）。"""
    out: set[str] = set()
    for fp, _n, _m in data.get("failures", []):
        if isinstance(fp, str) and fp.endswith(".py"):
            out.add(Path(fp).name)
    for fp, _n, _m in data.get("errors", []):
        if isinstance(fp, str) and fp.endswith(".py"):
            out.add(Path(fp).name)
    for fp, c in (data.get("per_file_counts") or {}).items():
        if not isinstance(fp, str) or not fp.endswith(".py"):
            continue
        if c.get("failure", 0) + c.get("error", 0) > 0:
            out.add(Path(fp).name)
    return out


def _failed_basenames_from_thread_results(results: list[ThreadResult]) -> set[str]:
    """子进程非 0 退出时，无论 JUnit 是否完整，都纳入待重跑集合。"""
    return {tr.script for tr in results if tr.result.returncode != 0}


def _merge_failed_sets(
    junit_path: Path | None,
    results: list[ThreadResult],
) -> set[str]:
    """JUnit 中的失败/错误 + returncode!=0 的脚本并集。"""
    out = _failed_basenames_from_thread_results(results)
    if junit_path and junit_path.is_file() and junit_path.stat().st_size > 0:
        try:
            sdata = summarize_junit(junit_path)
            out |= _failed_script_basenames_from_summary(sdata)
        except (OSError, ET.ParseError):
            pass
    return out


def test_files_for_rerun(
    zhaopin_dir: Path,
    *,
    only_basenames: set[str] | None = None,
) -> list[Path]:
    all_py = [p for p in zhaopin_dir.glob("test_*.py") if p.is_file()]
    if not only_basenames:
        return sorted(all_py)
    return sorted(p for p in all_py if p.name in only_basenames)


def _merge_junit_files(src_paths: list[Path], dest: Path) -> int:
    """将多个 JUnit 合并为单个 ``<testsuites>``，返回写入的用例数（含 failure/skip 节点）。"""
    root = ET.Element("testsuites")
    n = 0
    for p in src_paths:
        if not p.is_file() or p.stat().st_size == 0:
            continue
        try:
            tree = ET.parse(p)
        except ET.ParseError:
            continue
        r = tree.getroot()
        tag = r.tag.split("}")[-1] if "}" in r.tag else r.tag
        if tag == "testsuites":
            for child in list(r):
                root.append(child)
                n += int(child.get("tests") or 0) or len(child.findall("testcase"))
        elif tag == "testsuite":
            root.append(r)
            n += int(r.get("tests") or 0) or len(r.findall("testcase"))
    tree_out = ET.ElementTree(root)
    try:
        ET.indent(tree_out, space="  ")  # py3.9+
    except Exception:
        pass
    dest.parent.mkdir(parents=True, exist_ok=True)
    tree_out.write(dest, encoding="utf-8", xml_declaration=True)
    return n


def _print_fail_skip(data: dict, f: TextIO = sys.stdout) -> None:
    print("\n========== 失败用例 ==========", file=f)
    for fp, name, msg in data.get("failures", []):
        print(f"  [FAIL] {fp} :: {name}", file=f)
        if msg:
            s = (msg or "").replace("\n", " ")[:400]
            print(f"         {s}", file=f)
    for fp, name, msg in data.get("errors", []):
        print(f"  [ERROR] {fp} :: {name}", file=f)
        if msg:
            s = (msg or "").replace("\n", " ")[:400]
            print(f"          {s}", file=f)
    if not data.get("failures") and not data.get("errors"):
        print("  （无）", file=f)

    print("\n========== 跳过用例 ==========", file=f)
    for fp, name, msg in data.get("skipped", []):
        print(f"  [SKIP] {fp} :: {name}", file=f)
        if msg:
            s = (msg or "").replace("\n", " ")[:300]
            print(f"         {s}", file=f)
    if not data.get("skipped"):
        print("  （无）", file=f)


def _run_subprocess(
    relpath: str,
    junit: Path,
    log_path: Path,
    pc_root: Path,
    extra_env: dict[str, str],
) -> tuple[int, float, str | None]:
    t0 = time.perf_counter()
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        relpath,
        "--override-ini",
        "addopts=-v -s --tb=short",
        f"--junitxml={junit}",
    ]
    env = os.environ.copy()
    env.setdefault("HEADLESS", "1")
    for k, v in extra_env.items():
        env[k] = v
    err: str | None = None
    try:
        with open(log_path, "w", encoding="utf-8", errors="replace") as lf:
            p = subprocess.run(
                cmd,
                cwd=pc_root,
                env=env,
                stdout=lf,
                stderr=subprocess.STDOUT,
                check=False,
            )
        return p.returncode, time.perf_counter() - t0, err
    except OSError as e:
        return 1, time.perf_counter() - t0, str(e)


def write_per_script_reports(results: list[ThreadResult], out_dir: Path) -> list[tuple[str, Path]]:
    """
    为每个 test_*.py 生成独立 Markdown（JUnit + 该脚本控制台日志 + 子进程/墙钟元数据）：
    ``<out_dir>/per_script_reports/<stem>_run_report.md``。
    """
    d = out_dir / "per_script_reports"
    d.mkdir(parents=True, exist_ok=True)
    written: list[tuple[str, Path]] = []
    for tr in results:
        stem = Path(tr.script).stem
        r = tr.result
        log_path = r.log_path
        junit_path = r.junit_path
        log_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.is_file() else ""
        real_s, _, _ = parse_time_from_console(log_text)
        title = f"# `{tr.script}` 无头跑测报告"
        meta = (
            f"\n## 子进程与线程元数据\n\n"
            f"- 子进程 **returncode**: {r.returncode}\n"
            f"- 本脚本墙钟: **{r.wall_seconds:.2f}** s（线程内 pytest 子进程起止）\n"
        )
        if r.error:
            meta += f"- 子进程/线程级错误: `{r.error}`\n"

        out_p = d / f"{stem}_run_report.md"
        body = ""
        parse_note = ""
        if junit_path.is_file() and junit_path.stat().st_size > 0:
            t = junit_path.read_text(encoding="utf-8", errors="replace")
            if "<testsuite" in t or "<testsuites" in t:
                try:
                    data = summarize_junit(junit_path)
                    body = build_markdown(
                        data,
                        log_path if log_path.is_file() else None,
                        log_text,
                        real_s,
                        junit_path,
                        title=title,
                    )
                except (ET.ParseError, OSError, KeyError) as e:
                    parse_note = f"- JUnit 解析说明: {e!s}\n"

        if body:
            out_p.write_text(body + meta, encoding="utf-8")
        else:
            if parse_note:
                meta = meta.rstrip() + f"\n{parse_note}\n"
            out_p.write_text(
                f"{title}（JUnit 未生成或解析失败）\n{meta}\n"
                f"- 控制台: `{log_path}`\n\n## 控制台摘录\n\n"
                f"```\n{(log_text[-20000:] if log_text else '（无）')}\n```\n",
                encoding="utf-8",
            )
        written.append((tr.script, out_p))
    return written


def _run_one_file(
    f: Path,
    pc_root: Path,
    out_dir: Path,
    extra_env: dict[str, str],
) -> ThreadResult:
    relp = f"test_cases/zhaopin/{f.name}"
    logs_dir = out_dir / "per_script_logs"
    junit_dir = out_dir / "junit"
    junit = junit_dir / f"{f.stem}_junit.xml"
    log_path = logs_dir / f"{f.stem}.log"
    code, wall, oerr = _run_subprocess(relp, junit, log_path, pc_root, extra_env)
    return ThreadResult(
        script=f.name,
        result=ScriptRunResult(
            relpath=relp,
            returncode=code,
            wall_seconds=wall,
            junit_path=junit,
            log_path=log_path,
            error=oerr,
        ),
    )


def run_zhaopin_parallel(
    zhaopin_dir: Path,
    pc_root: Path,
    out_dir: Path,
    max_workers: int,
    extra_env: dict[str, str],
    test_files: list[Path] | None = None,
) -> tuple[list[ThreadResult], float]:
    """
    线程池并行：每个任务在线程中 ``subprocess`` 跑一个测试文件；``max_workers`` 0 或大于脚本数
    时，等于「每脚本一个并发槽」，即与脚本数相同的并行度（每个脚本一个线程负责拉起 pytest）。
    ``test_files`` 非空时只跑这些路径（须位于 ``zhaopin_dir`` 下，通常为 ``test_*.py``）；``None`` 表示
    跑目录内全部 ``test_*.py``。
    """
    if test_files is None:
        test_files = discover_test_files(zhaopin_dir)
    else:
        test_files = sorted(test_files, key=lambda p: p.name)
    if not test_files:
        return [], 0.0
    n = len(test_files)
    if max_workers <= 0 or max_workers > n:
        max_workers = n

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "per_script_logs").mkdir(exist_ok=True)
    (out_dir / "junit").mkdir(exist_ok=True)

    t0 = time.perf_counter()
    results: list[ThreadResult] = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        future_map = {ex.submit(_run_one_file, f, pc_root, out_dir, extra_env): f for f in test_files}
        for fut in as_completed(future_map):
            results.append(fut.result())
    wall = time.perf_counter() - t0
    results.sort(key=lambda r: r.script)
    return results, wall


def run_one_batch_and_write_reports(
    zhaopin: Path,
    pc_root: Path,
    out_dir: Path,
    max_workers: int,
    extra_env: dict[str, str],
    test_files: list[Path] | None,
    *,
    report_head_extra: str = "",
) -> tuple[set[str], list[ThreadResult], Path, float]:
    """
    跑一轮并行 pytest、合并 JUnit、写 per-script 与总报告。

    返回 ``(失败脚本 basenames 集合, results, merged_junit_path, pool_wall)``。
    集合为空表示本轮全部通过。
    """
    results, pool_wall = run_zhaopin_parallel(
        zhaopin, pc_root, out_dir, max_workers, extra_env, test_files=test_files
    )
    if not results:
        return set(), [], out_dir / "zhaopin_parallel_merged_junit.xml", pool_wall

    per_script_report_paths = write_per_script_reports(results, out_dir)
    print(f"\n各脚本独立报告目录: {out_dir / 'per_script_reports'}/", flush=True)
    for name, rp in per_script_report_paths:
        print(f"  {name} -> {rp}", flush=True)

    junit_paths = [tr.result.junit_path for tr in results if tr.result.junit_path.is_file()]
    merged = out_dir / "zhaopin_parallel_merged_junit.xml"
    _merge_junit_files(junit_paths, merged)

    print("\n========== 各脚本墙钟执行时长（秒） ==========\n", flush=True)
    for tr in results:
        r = tr.result
        st = f"{r.wall_seconds:8.2f}"
        rc = r.returncode
        line = f"  {st} s  rc={rc}  {r.relpath}"
        if r.error:
            line += f"  ERR: {r.error}"
        print(line, flush=True)

    combined_log = out_dir / "zhaopin_parallel_combined_console.log"
    parts: list[str] = []
    for tr in results:
        lp = tr.result.log_path
        if lp.is_file():
            parts.append(
                f"\n\n========== {tr.script} (rc={tr.result.returncode}, {tr.result.wall_seconds:.2f}s) ==========\n\n"
            )
            parts.append(lp.read_text(encoding="utf-8", errors="replace"))
    combined_log.write_text("".join(parts), encoding="utf-8")
    (out_dir / "zhaopin_parallel_duration_sec.txt").write_text(
        f"thread_pool_wall_sec={pool_wall:.4f}\n", encoding="utf-8"
    )

    data = summarize_junit(merged) if merged.is_file() and merged.stat().st_size > 0 else {}
    if not data:
        print("警告: 未生成有效合并 JUnit，可能子进程均失败", file=sys.stderr)
    else:
        _print_fail_skip(data, sys.stdout)

    failed_set = _merge_failed_sets(merged, results)

    if data:
        md = build_markdown(
            data,
            combined_log,
            f"**线程池墙钟**（全部脚本并发结束）: {pool_wall:.2f} s\n\n"
            + combined_log.read_text(encoding="utf-8", errors="replace")[:50000],
            None,
            merged,
        )
        head = (
            f"# zhaopin 无头多线程并行跑测\n\n{report_head_extra}"
            f"- 输出目录: `{out_dir}`\n- **线程池总墙钟**: {pool_wall:.2f} s\n"
        )
        if (out_dir / "rerun_source.txt").is_file():
            head += "- **模式**: 仅重跑 JUnit 中有失败/错误的脚本，见 `rerun_source.txt`\n"
        head += f"- 各脚本 Markdown: `{out_dir / 'per_script_reports'}/`\n\n## 每脚本报告路径\n\n| 脚本 | Markdown 报告 |\n| --- | --- |\n"
        for name, rp in per_script_report_paths:
            head += f"| `{name}` | `{rp.name}` |\n"
        head += "\n## 每脚本墙钟\n\n| 脚本 | 秒 | returncode |\n| --- | ---: | ---: |\n"
        for tr in results:
            r = tr.result
            head += f"| `{tr.script}` | {r.wall_seconds:.2f} | {r.returncode} |\n"
        head += "\n---\n\n"
        report_path = out_dir / "zhaopin_parallel_headless_run_report.md"
        report_path.write_text(
            head + re.sub(r"^# zhaopin 无头跑测汇总", "## JUnit 汇总", md, count=1),
            encoding="utf-8",
        )
        print(f"\n已写报告: {report_path}", flush=True)
    else:
        report_path = out_dir / "zhaopin_parallel_headless_run_report.md"
        mini = (
            f"# 并行跑测（JUnit 未合并成功）\n\n{report_head_extra}"
            f"输出: `{out_dir}`\n池墙钟: {pool_wall:.2f} s\n"
            f"- 各脚本报告: `{out_dir / 'per_script_reports'}/`\n"
        )
        report_path.write_text(mini, encoding="utf-8")
        print(f"已写简报告: {report_path}", flush=True)

    print(f"\n合并 JUnit: {merged}", flush=True)
    print(f"合并日志: {combined_log}", flush=True)
    return failed_set, results, merged, pool_wall


def main() -> int:
    ap = argparse.ArgumentParser(
        description="zhaopin 目录下按脚本无头多线程并行 pytest，并统计时长与失败/跳过",
    )
    ap.add_argument(
        "--pc-root",
        type=Path,
        default=_PC_ROOT,
        help="ok_autotest_ui_pc 包根（含 pytest.ini、test_cases）",
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="输出目录（合并 junit、报告、per-script 日志），默认在 zhaopin 下带时间戳",
    )
    ap.add_argument(
        "--max-workers",
        type=int,
        default=0,
        help="并发工作线程数；0=与 test_*.py 数量相同（每脚本一槽、槽内子进程跑 pytest）。"
        "可设为较小值以限制同时打开的浏览器数量。",
    )
    ap.add_argument(
        "--zhaopin-set-ci",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="设置 CI=1 以与部分 headless/CI 逻辑一致",
    )
    ap.add_argument(
        "--zhaopin-no-shared",
        action="store_true",
        help="设置 ZHAOPIN_SHARED_CONTEXT=0，适合极端隔离（耗时会增加）",
    )
    ap.add_argument(
        "--failed-from-junit",
        type=Path,
        default=None,
        metavar="PATH",
        help="上次并行的合并 JUnit（如 zhaopin_parallel_merged_junit.xml），仅对其中有失败/错误的脚本重跑",
    )
    ap.add_argument(
        "--scripts",
        nargs="+",
        default=None,
        metavar="NAME",
        help="只跑这些脚本，仅需文件名，如: test_foo.py test_bar.py（与 --failed-from-junit 二选一，后者优先）",
    )
    ap.add_argument(
        "--until-pass",
        action="store_true",
        help="多轮重跑：每轮一线程一脚本并发；仅重跑仍有失败/错误的脚本，直到全部通过或达到 --max-rounds",
    )
    ap.add_argument(
        "--max-rounds",
        type=int,
        default=50,
        metavar="N",
        help="与 --until-pass 合用：最多跑多少轮（默认 50）",
    )
    args = ap.parse_args()
    if args.failed_from_junit and args.scripts:
        ap.error("--failed-from-junit 与 --scripts 不能同时指定")
    if args.until_pass and (args.failed_from_junit or args.scripts):
        ap.error("--until-pass 不能与 --failed-from-junit / --scripts 同时使用")

    pc_root = args.pc_root.resolve()
    zhaopin = pc_root / "test_cases" / "zhaopin"
    if not (pc_root / "pytest.ini").is_file():
        print(f"未在 {pc_root} 发现 pytest.ini，请确认 --pc-root", file=sys.stderr)
        return 2

    extra_env: dict[str, str] = {"HEADLESS": "1"}
    if args.zhaopin_set_ci:
        extra_env["CI"] = "1"
    if args.zhaopin_no_shared:
        extra_env["ZHAOPIN_SHARED_CONTEXT"] = "0"

    ts = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")

    if args.until_pass:
        until_root = (args.out_dir or (zhaopin / f"parallel_headless_until_pass_{ts}")).resolve()
        until_root.mkdir(parents=True, exist_ok=True)
        (until_root / "until_pass_meta.txt").write_text(
            f"started_local={ts}\nmax_rounds={args.max_rounds}\nmax_workers={args.max_workers}\n",
            encoding="utf-8",
        )
        pending_basenames: set[str] | None = None
        for rnd in range(1, args.max_rounds + 1):
            round_dir = until_root / f"round_{rnd:02d}"
            if pending_basenames is None:
                selected_round: list[Path] | None = None
                mode_desc = "首轮全量 test_*.py"
            else:
                if not pending_basenames:
                    break
                selected_round = test_files_for_rerun(zhaopin, only_basenames=pending_basenames)
                if not selected_round:
                    print(
                        f"第 {rnd} 轮：失败集合 {sorted(pending_basenames)!r} 无法映射到 zhaopin 下 test_*.py",
                        file=sys.stderr,
                    )
                    return 2
                mode_desc = f"仅重跑 {len(selected_round)} 个脚本"
            print(
                f"\n{'=' * 60}\n--until-pass 第 {rnd}/{args.max_rounds} 轮（{mode_desc}）\n{'=' * 60}\n",
                flush=True,
            )
            extra_head = f"- **until-pass 轮次**: {rnd} / {args.max_rounds}\n"
            failed_set, results_round, _merged, _pool = run_one_batch_and_write_reports(
                zhaopin,
                pc_root,
                round_dir,
                args.max_workers,
                extra_env,
                selected_round,
                report_head_extra=extra_head,
            )
            if not results_round and not discover_test_files(zhaopin):
                print(f"在 {zhaopin} 下未发现 test_*.py，退出。", file=sys.stderr)
                return 0
            if not failed_set:
                (until_root / "until_pass_success.txt").write_text(
                    f"completed_round={rnd}\nroot={until_root}\n",
                    encoding="utf-8",
                )
                print(f"\n全部脚本已通过。汇总根目录: {until_root}", flush=True)
                return 0
            pending_basenames = failed_set
            print(
                f"\n第 {rnd} 轮仍有 {len(failed_set)} 个脚本未通过: {sorted(failed_set)}",
                flush=True,
            )
        print(
            f"\n已达 --max-rounds={args.max_rounds}，仍未全部通过。见: {until_root}",
            file=sys.stderr,
        )
        return 1

    out_dir = (args.out_dir or (zhaopin / f"parallel_headless_run_{ts}")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    selected: list[Path] | None = None
    if args.failed_from_junit:
        jp = args.failed_from_junit.resolve()
        if not jp.is_file():
            print(f"未找到 JUnit 文件: {jp}", file=sys.stderr)
            return 2
        try:
            sdata = summarize_junit(jp)
        except (OSError, ET.ParseError) as e:
            print(f"无法解析 JUnit: {e}", file=sys.stderr)
            return 2
        basenames = _failed_script_basenames_from_summary(sdata)
        if not basenames:
            print(f"在 {jp} 中未解析到任何失败/错误用例，无需重跑。", file=sys.stderr)
            return 0
        selected = test_files_for_rerun(zhaopin, only_basenames=basenames)
        if not selected:
            print("JUnit 中的失败文件在 zhaopin 下均找不到对应 test_*.py，请检查路径。", file=sys.stderr)
            return 2
        (out_dir / "rerun_source.txt").write_text(
            f"source_junit={jp}\n"
            f"failed_basenames={sorted(basenames)!r}\n"
            f"selected_count={len(selected)}\n",
            encoding="utf-8",
        )
        print(
            f"根据 JUnit 仅重跑有失败/错误的 {len(selected)} 个脚本: "
            f"{', '.join(p.name for p in selected)}",
            flush=True,
        )
    elif args.scripts:
        name_set: set[str] = set()
        for n in args.scripts:
            n = n.strip()
            if not n:
                continue
            name_set.add(n if n.endswith(".py") else f"{n}.py")
        selected = test_files_for_rerun(zhaopin, only_basenames=name_set)
        if not selected:
            print("未找到与 --scripts 匹配的 test_*.py。", file=sys.stderr)
            return 2
        if len(selected) < len(name_set):
            found = {p.name for p in selected}
            missing = sorted(name_set - found)
            print(f"警告: 以下文件在 zhaopin 中不存在: {missing}", file=sys.stderr)

    failed_set, results, _merged, _pool_wall = run_one_batch_and_write_reports(
        zhaopin,
        pc_root,
        out_dir,
        args.max_workers,
        extra_env,
        selected,
    )
    if not results:
        print(f"在 {zhaopin} 下未发现 test_*.py，退出。", file=sys.stderr)
        return 0

    return 1 if failed_set else 0


if __name__ == "__main__":
    raise SystemExit(main())
