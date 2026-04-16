#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


MANAGED_PREFIXES = ("test_cases/", "pages/", "utils/", "test_data/")
ROOT_CANDIDATES = ("requirements.txt", "pytest.ini", "run_tests_ci.sh")
PROTECTED_PREFIXES = ("tooling/ok_test/", "catalog/", "docs/")
FIXED_EXCLUDE_PARTS = {
    ".git",
    ".playwright-mcp",
    ".pytest_cache",
    "__pycache__",
    "allure-results",
    "dist",
    "ok-ui-autotest",
    "openskills",
    "playwright-test-generator",
    "reports",
    "screenshots",
    "sessions",
    "test-case-submitter",
    "venv",
    "web-qa-brain",
}
ROOT_DEBUG_PATTERN = re.compile(r"^debug_.*\.(?:png|html)$", re.IGNORECASE)


@dataclass
class CopyPlan:
    copy_files: list[str]
    excluded_files: list[str]
    source_test_cases: list[str]


def run_git(source: Path, args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(source), *args],
        text=True,
        capture_output=True,
        check=check,
    )


def git_output(source: Path, args: list[str]) -> str:
    return run_git(source, args).stdout.strip()


def git_ls_files(source: Path, paths: list[str] | None = None) -> list[str]:
    command = ["ls-files", "-z"]
    if paths:
        command.extend(paths)
    output = run_git(source, command).stdout
    return sorted(item for item in output.split("\0") if item)


def verify_source(source: Path) -> tuple[bool, list[str], str]:
    errors: list[str] = []
    if not source.exists():
        return False, [f"source 不存在: {source}"], ""
    try:
        inside = git_output(source, ["rev-parse", "--is-inside-work-tree"])
        branch = git_output(source, ["branch", "--show-current"])
        head = git_output(source, ["rev-parse", "HEAD"])
        origin_master = git_output(source, ["rev-parse", "origin/master"])
        status = run_git(source, ["status", "--porcelain"]).stdout.strip()
    except subprocess.CalledProcessError as exc:
        return False, [f"source git 校验失败: {exc.stderr.strip() or exc.stdout.strip()}"], ""

    if inside != "true":
        errors.append("source 不是 git 仓库")
    if branch != "master":
        errors.append(f"source 当前分支不是 master: {branch}")
    if head != origin_master:
        errors.append(f"source HEAD 不等于 origin/master: HEAD={head}, origin/master={origin_master}")
    if status:
        errors.append("source 存在未提交或未跟踪变更，请先 reset/clean")
    return not errors, errors, head


def parts(rel_path: str) -> set[str]:
    return set(Path(rel_path).parts)


def is_fixed_excluded(rel_path: str) -> bool:
    rel_parts = parts(rel_path)
    if rel_parts & FIXED_EXCLUDE_PARTS:
        return True
    return bool(ROOT_DEBUG_PATTERN.match(rel_path))


def is_allowed_candidate(rel_path: str) -> bool:
    if rel_path.startswith("test_cases/"):
        return True
    if rel_path.startswith(("pages/", "utils/")):
        return not is_fixed_excluded(rel_path)
    if rel_path.startswith("test_data/"):
        return not is_fixed_excluded(rel_path) and ".DS_Store" not in parts(rel_path)
    return False


def build_copy_plan(source: Path) -> CopyPlan:
    source_test_cases = git_ls_files(source, ["test_cases"])
    raw_candidates = sorted(
        set(source_test_cases)
        | set(git_ls_files(source, ["pages"]))
        | set(git_ls_files(source, ["utils"]))
        | set(git_ls_files(source, ["test_data"]))
    )

    copy_files: list[str] = []
    excluded_files: list[str] = []
    for rel_path in raw_candidates:
        if any(rel_path.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            raise RuntimeError(f"拒绝复制 skill 治理资产: {rel_path}")
        if is_allowed_candidate(rel_path):
            copy_files.append(rel_path)
        else:
            excluded_files.append(rel_path)

    illegal_excluded_cases = [path for path in excluded_files if path.startswith("test_cases/")]
    if illegal_excluded_cases:
        raise RuntimeError("test_cases/** 不允许被排除: " + ", ".join(illegal_excluded_cases[:10]))
    return CopyPlan(
        copy_files=sorted(copy_files),
        excluded_files=sorted(excluded_files),
        source_test_cases=source_test_cases,
    )


def backup_existing(dest: Path, rel_path: str, report_dir: Path) -> None:
    target = dest / rel_path
    if not target.exists() or target.is_dir():
        return
    backup = report_dir / "backups" / rel_path
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(target, backup)


def copy_candidates(source: Path, dest: Path, report_dir: Path, rel_paths: list[str], *, apply: bool) -> list[str]:
    copied: list[str] = []
    for rel_path in rel_paths:
        src = source / rel_path
        target = dest / rel_path
        action = "ADD"
        if target.exists():
            action = "UPDATE" if src.read_bytes() != target.read_bytes() else "UNCHANGED"
        copied.append(f"{action} {rel_path}")
        if apply and action != "UNCHANGED":
            backup_existing(dest, rel_path, report_dir)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
    return copied


def requirement_name(line: str) -> str:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return ""
    stripped = stripped.split(";", 1)[0].strip()
    match = re.split(r"\s*(?:==|>=|<=|~=|!=|>|<)\s*", stripped, maxsplit=1)
    return match[0].strip().lower().replace("_", "-")


def merge_requirements(source: Path, dest: Path, *, apply: bool) -> list[str]:
    src_path = source / "requirements.txt"
    dest_path = dest / "requirements.txt"
    if not src_path.exists() or not dest_path.exists():
        return ["SKIP requirements.txt: source 或 dest 不存在"]

    src_lines = src_path.read_text(encoding="utf-8").splitlines()
    dest_text = dest_path.read_text(encoding="utf-8")
    dest_lines = dest_text.splitlines()
    dest_names = {name for line in dest_lines if (name := requirement_name(line))}
    additions = [line for line in src_lines if (name := requirement_name(line)) and name not in dest_names]
    if not additions:
        return ["UNCHANGED requirements.txt"]

    if apply:
        merged = dest_text.rstrip() + "\n\n# Added from ok_autotest_ui_pc migration\n"
        merged += "\n".join(additions) + "\n"
        dest_path.write_text(merged, encoding="utf-8")
    return [f"MERGE requirements.txt: +{len(additions)} dependencies"]


def marker_section_bounds(lines: list[str]) -> tuple[int, int] | None:
    marker_start = next((idx for idx, line in enumerate(lines) if line.strip() == "markers ="), -1)
    if marker_start < 0:
        return None
    marker_end = len(lines)
    for idx in range(marker_start + 1, len(lines)):
        line = lines[idx]
        stripped = line.strip()
        if line.startswith("["):
            marker_end = idx
            break
        if stripped.startswith("#") and not line.startswith((" ", "\t")):
            marker_end = idx
            break
        if stripped and not line.startswith((" ", "\t")) and not stripped.startswith("#"):
            marker_end = idx
            break
    return marker_start, marker_end


def marker_name(line: str) -> str:
    match = re.match(r"^\s+([A-Za-z_][A-Za-z0-9_]*):", line)
    if not match:
        return ""
    name = match.group(1)
    if name.startswith("case_id_"):
        return ""
    return name


def marker_lines(text: str) -> list[str]:
    lines = text.splitlines()
    bounds = marker_section_bounds(lines)
    if not bounds:
        return []
    marker_start, marker_end = bounds
    return [line for line in lines[marker_start + 1 : marker_end] if marker_name(line)]


def merge_pytest_ini(source: Path, dest: Path, *, apply: bool) -> list[str]:
    src_path = source / "pytest.ini"
    dest_path = dest / "pytest.ini"
    if not src_path.exists() or not dest_path.exists():
        return ["SKIP pytest.ini: source 或 dest 不存在"]

    src_markers = marker_lines(src_path.read_text(encoding="utf-8"))
    dest_text = dest_path.read_text(encoding="utf-8")
    dest_lines = dest_text.splitlines()
    dest_names = {marker_name(line) for line in marker_lines(dest_text)}
    additions = [line for line in src_markers if marker_name(line) and marker_name(line) not in dest_names]
    if not additions:
        return ["UNCHANGED pytest.ini markers"]

    if apply:
        insert_index = len(dest_lines)
        bounds = marker_section_bounds(dest_lines)
        if bounds:
            insert_index = bounds[1]
        else:
            dest_lines.extend(["", "markers ="])
            insert_index = len(dest_lines)
        dest_lines[insert_index:insert_index] = additions
        dest_path.write_text("\n".join(dest_lines).rstrip() + "\n", encoding="utf-8")
    return [f"MERGE pytest.ini markers: +{len(additions)} markers"]


def handle_run_tests_ci(source: Path, dest: Path, *, apply: bool) -> list[str]:
    src_path = source / "run_tests_ci.sh"
    dest_path = dest / "run_tests_ci.sh"
    if not src_path.exists():
        return ["SKIP run_tests_ci.sh: source 不存在"]
    if dest_path.exists():
        return ["SKIP run_tests_ci.sh: dest 已存在，不覆盖"]
    if apply:
        shutil.copy2(src_path, dest_path)
    return ["ADD run_tests_ci.sh"]


def write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + ("\n" if lines else ""), encoding="utf-8")


def list_dest_files(dest: Path, root: str) -> list[str]:
    base = dest / root
    if not base.exists():
        return []
    result: list[str] = []
    for item in base.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(dest).as_posix()
            if root == "test_cases" or not is_fixed_excluded(rel_path):
                result.append(rel_path)
    return sorted(result)


def build_dest_manifest(dest: Path) -> list[str]:
    return list_dest_files(dest, "test_cases")


def dest_only_files(dest: Path, copy_files: list[str]) -> list[str]:
    expected = set(copy_files)
    actual: set[str] = set()
    for root in ("test_cases", "pages", "utils", "test_data"):
        actual.update(list_dest_files(dest, root))
    return sorted(actual - expected)


def render_adaptation_report(
    *,
    source: Path,
    dest: Path,
    source_commit: str,
    apply: bool,
    plan: CopyPlan,
    copied: list[str],
    missing: list[str],
    excluded: list[str],
    dest_only: list[str],
    root_actions: list[str],
) -> str:
    status = "APPLIED" if apply else "DRY-RUN"
    lines = [
        f"# ok_autotest_ui_pc Migration Report ({status})",
        "",
        f"- source: {source}",
        f"- dest: {dest}",
        f"- source_commit: {source_commit}",
        f"- source test_cases files: {len(plan.source_test_cases)}",
        f"- planned copied files: {len(plan.copy_files)}",
        f"- excluded files: {len(excluded)}",
        f"- missing test_cases after expected copy: {len(missing)}",
        f"- dest-only managed files: {len(dest_only)}",
        "",
        "## Root Candidate Handling",
    ]
    lines.extend(f"- {item}" for item in root_actions)
    lines.extend(
        [
            "",
            "## Adaptation",
            "- ok_autotest_ui_skill 的 tooling/catalog/docs 不从源仓库覆盖。",
            "- requirements.txt 只补源仓库新增依赖，不降级现有依赖。",
            "- pytest.ini 只补源仓库新增 marker，不覆盖 addopts/testpaths。",
            "- catalog/audit 仍需在迁移后通过 ok skill 命令执行。",
        ]
    )
    if missing:
        lines.extend(["", "## Blocking Missing test_cases"])
        lines.extend(f"- {item}" for item in missing[:200])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync ok_autotest_ui_pc cases into ok_autotest_ui_skill safely.")
    parser.add_argument("--source", required=True)
    parser.add_argument("--dest", required=True)
    parser.add_argument("--report-dir", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    dest = Path(args.dest).resolve()
    report_dir = Path(args.report_dir).resolve()
    report_dir.mkdir(parents=True, exist_ok=True)

    ok, errors, source_commit = verify_source(source)
    if not ok:
        write_lines(report_dir / "source_errors.txt", errors)
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    if not dest.exists():
        print(f"dest 不存在: {dest}", file=sys.stderr)
        return 1

    try:
        plan = build_copy_plan(source)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    copied = copy_candidates(source, dest, report_dir, plan.copy_files, apply=args.apply)
    root_actions: list[str] = []
    root_actions.extend(merge_requirements(source, dest, apply=args.apply))
    root_actions.extend(merge_pytest_ini(source, dest, apply=args.apply))
    root_actions.extend(handle_run_tests_ci(source, dest, apply=args.apply))

    if args.apply:
        missing = [rel_path for rel_path in plan.source_test_cases if not (dest / rel_path).exists()]
    else:
        missing = [rel_path for rel_path in plan.source_test_cases if rel_path not in plan.copy_files]
    dest_manifest = build_dest_manifest(dest)
    dest_only = dest_only_files(dest, plan.copy_files)

    write_lines(report_dir / "source_commit.txt", [source_commit])
    write_lines(report_dir / "source_test_cases_manifest.txt", plan.source_test_cases)
    write_lines(report_dir / "dest_test_cases_manifest.txt", dest_manifest)
    write_lines(report_dir / "missing_test_cases.txt", missing)
    write_lines(report_dir / "copied_files.txt", copied + root_actions)
    write_lines(report_dir / "excluded_files.txt", plan.excluded_files)
    write_lines(report_dir / "dest_only_files.txt", dest_only)
    (report_dir / "adaptation_report.md").write_text(
        render_adaptation_report(
            source=source,
            dest=dest,
            source_commit=source_commit,
            apply=args.apply,
            plan=plan,
            copied=copied,
            missing=missing,
            excluded=plan.excluded_files,
            dest_only=dest_only,
            root_actions=root_actions,
        ),
        encoding="utf-8",
    )

    print(f"report_dir={report_dir}")
    print(f"source_commit={source_commit}")
    print(f"source_test_cases={len(plan.source_test_cases)}")
    print(f"copy_candidates={len(plan.copy_files)}")
    print(f"excluded_files={len(plan.excluded_files)}")
    print(f"missing_test_cases={len(missing)}")
    return 2 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
