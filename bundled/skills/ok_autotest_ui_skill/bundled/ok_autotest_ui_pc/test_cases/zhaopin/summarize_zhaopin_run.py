#!/usr/bin/env python3
"""
从 pytest --junitxml 产物与可选控制台日志生成 Markdown 汇总：
- 总耗时（优先从日志中解析 `time -p` 的 real 秒；否则用 JUnit testsuite 的 time 之和近似）
- 每个测试脚本（文件）的耗时（JUnit testcase @time 按文件聚合）
- 失败、跳过、错误用例列表
用法:
  python3 summarize_zhaopin_run.py [--junit PATH] [--console PATH] [--out PATH]
"""
from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def parse_pytest_summary_line(console_text: str) -> str | None:
    """提取 ``======= 5 failed, 296 passed, ... =======`` 一行。"""
    m = re.search(
        r"^=+\s+(\d+\s+failed,.*\d+\s+(?:passed|error|skipped).*) in [\d.]+s.*$",
        console_text,
        re.MULTILINE,
    )
    return m.group(1).strip() if m else None


def parse_time_from_console(console_text: str) -> tuple[float | None, float | None, float | None]:
    """从 `time -p` 输出解析 real / user / sys（秒）。"""
    real = user = sys_ = None
    m = re.search(r"^real\s+([0-9.]+)", console_text, re.MULTILINE)
    if m:
        real = float(m.group(1))
    m = re.search(r"^user\s+([0-9.]+)", console_text, re.MULTILINE)
    if m:
        user = float(m.group(1))
    m = re.search(r"^sys\s+([0-9.]+)", console_text, re.MULTILINE)
    if m:
        sys_ = float(m.group(1))
    return real, user, sys_


def junit_path_from_classname(classname: str) -> str:
    """dotted.module[.TestClass] -> test_cases/.../module.py。

    pytest junit 的 classname 可能是 ``pkg.mod.test_file`` 或 ``pkg.mod.test_file.TestClass``。
    仅当最后一段为类名（PascalCase）时去掉，避免出现 ``test_cases.zhaopin`` -> ``zhaopin.py`` 的错误聚合。
    """
    if not classname:
        return ""
    parts = classname.split(".")
    if len(parts) >= 2 and parts[-1][:1].isupper():
        parts = parts[:-1]
    mod = ".".join(parts)
    if "." not in mod:
        return ""
    return mod.replace(".", "/") + ".py"


def testcase_script_path(case) -> str:
    """优先使用 pytest 写入的 file 属性，否则从 classname 推断。"""
    f = (case.get("file") or "").strip()
    if f:
        return f.replace("\\", "/")
    cn = case.get("classname") or ""
    inferred = junit_path_from_classname(cn)
    return inferred.replace("\\", "/")


def summarize_junit(junit_path: Path) -> dict:
    tree = ET.parse(junit_path)
    root = tree.getroot()
    # pytest 可能用 testsuites 包裹单个 testsuite
    suites = root.findall(".//testsuite") if root.tag.endswith("testsuites") else [root]

    per_file_time: dict[str, float] = defaultdict(float)
    per_file_counts: dict[str, dict[str, int]] = defaultdict(
        lambda: {"passed": 0, "failure": 0, "skipped": 0, "error": 0}
    )
    failures: list[tuple[str, str, str]] = []  # file, name, message snippet
    skipped: list[tuple[str, str, str]] = []
    errors: list[tuple[str, str, str]] = []

    total_cases = 0
    junit_wall = 0.0

    for suite in suites:
        junit_wall += float(suite.get("time") or 0)
        for case in suite.findall("testcase"):
            total_cases += 1
            name = case.get("name") or ""
            fpath = testcase_script_path(case)
            t = float(case.get("time") or 0)
            key = fpath if fpath.endswith(".py") else (case.get("classname") or "unknown")
            per_file_time[key] += t

            fail = case.find("failure")
            sk = case.find("skipped")
            err = case.find("error")

            if fail is not None:
                per_file_counts[key]["failure"] += 1
                msg = (fail.get("message") or fail.text or "")[:500]
                failures.append((key, name, msg.strip()))
            elif err is not None:
                per_file_counts[key]["error"] += 1
                msg = (err.get("message") or err.text or "")[:500]
                errors.append((key, name, msg.strip()))
            elif sk is not None:
                per_file_counts[key]["skipped"] += 1
                msg = (sk.get("message") or sk.text or "")[:500]
                skipped.append((key, name, msg.strip()))
            else:
                per_file_counts[key]["passed"] += 1

    return {
        "per_file_time": dict(sorted(per_file_time.items(), key=lambda x: -x[1])),
        "per_file_counts": {k: per_file_counts[k] for k in sorted(per_file_counts.keys())},
        "failures": failures,
        "skipped": skipped,
        "errors": errors,
        "total_cases": total_cases,
        "junit_suite_time_sum": junit_wall,
    }


def build_markdown(
    data: dict,
    console_path: Path | None,
    console_text: str,
    real_s: float | None,
    junit_path: Path,
    *,
    title: str = "# zhaopin 无头跑测汇总报告",
) -> str:
    now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    lines = [
        title,
        "",
        f"- 生成时间: {now}",
        f"- JUnit 输入: `{junit_path}`",
    ]
    if console_path and console_path.is_file():
        lines.append(f"- 控制台日志: `{console_path}`")
    summary = parse_pytest_summary_line(console_text) if console_text.strip() else None
    lines.extend(
        [
            "",
            "## 总耗时",
            "",
        ]
    )
    if summary:
        lines.append(f"- **pytest 汇总**: {summary}")
    if real_s is not None:
        lines.append(f"- **墙钟（time real）**: **{real_s:.2f} s**（约 {real_s / 60:.2f} min）")
    else:
        lines.append(
            f"- **JUnit testsuite time 之和（近似）**: **{data['junit_suite_time_sum']:.2f} s**（若未并行，接近各用例 CPU 累计；与墙钟可能不同）"
        )
    lines.extend(
        [
            f"- 用例总数（JUnit 条目）: {data['total_cases']}",
            "",
            "## 各测试脚本耗时（按 JUnit 单条 time 汇总到文件）",
            "",
            "| 脚本 | 耗时 (s) |",
            "| --- | ---: |",
        ]
    )
    for fp, sec in data["per_file_time"].items():
        lines.append(f"| `{fp}` | {sec:.3f} |")
    lines.extend(["", "## 统计摘要（按文件）", "", "| 脚本 | passed | failed | skipped | error |", "| --- | ---: | ---: | ---: | ---: |"])
    for fp in sorted(data["per_file_counts"].keys()):
        c = data["per_file_counts"][fp]
        lines.append(
            f"| `{fp}` | {c['passed']} | {c['failure']} | {c['skipped']} | {c['error']} |"
        )

    lines.extend(["", "## 失败用例", ""])
    if data["failures"]:
        for fp, name, msg in data["failures"]:
            lines.append(f"- `{fp}` :: `{name}`")
            if msg:
                lines.append(f"  - {msg[:300]}{'…' if len(msg) > 300 else ''}")
    else:
        lines.append("（无）")

    lines.extend(["", "## 错误（setup/teardown 等）", ""])
    if data["errors"]:
        for fp, name, msg in data["errors"]:
            lines.append(f"- `{fp}` :: `{name}`")
            if msg:
                lines.append(f"  - {msg[:300]}{'…' if len(msg) > 300 else ''}")
    else:
        lines.append("（无）")

    lines.extend(["", "## 跳过用例", ""])
    if data["skipped"]:
        for fp, name, msg in data["skipped"]:
            lines.append(f"- `{fp}` :: `{name}`")
            if msg:
                lines.append(f"  - {msg[:300]}{'…' if len(msg) > 300 else ''}")
    else:
        lines.append("（无）")

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--junit", type=Path, default=here / "zhaopin_headless_junit.xml")
    ap.add_argument("--console", type=Path, default=here / "zhaopin_headless_console.log")
    ap.add_argument("--out", type=Path, default=here / "zhaopin_headless_run_report.md")
    args = ap.parse_args()

    if not args.junit.is_file():
        print(f"缺少 JUnit 文件: {args.junit}", file=sys.stderr)
        print("请等待 pytest 跑完后再执行本脚本。", file=sys.stderr)
        return 2

    text = args.junit.read_text(encoding="utf-8", errors="replace")
    if "<testsuite" not in text and "<testsuites" not in text:
        print(f"JUnit 文件不完整或格式异常: {args.junit}", file=sys.stderr)
        return 2

    console_text = ""
    if args.console.is_file():
        console_text = args.console.read_text(encoding="utf-8", errors="replace")
    real_s, user_s, sys_s = parse_time_from_console(console_text)

    data = summarize_junit(args.junit)
    md = build_markdown(
        data,
        args.console if args.console.is_file() else None,
        console_text,
        real_s,
        args.junit,
        title="# zhaopin 无头跑测汇总报告",
    )
    args.out.write_text(md, encoding="utf-8")
    print(f"已写入: {args.out}")
    if real_s is None:
        print("提示: 日志中未解析到 `time -p` 的 real，总墙钟可查看控制台末尾 pytest 时长或重新用 `/usr/bin/time -p` 包裹 pytest。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
