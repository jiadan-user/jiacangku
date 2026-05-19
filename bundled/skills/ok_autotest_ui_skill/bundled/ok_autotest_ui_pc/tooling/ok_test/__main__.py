from __future__ import annotations

import argparse
import sys

from .catalog import handle_catalog_build
from .coverage import handle_coverage
from .decision import handle_decide
from .doctor import handle_doctor
from .identifiers import handle_identifier_audit
from .runner import handle_run
from .selector import handle_list


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tooling.ok_test")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor_parser = subparsers.add_parser("doctor", help="Run environment and collect health checks")
    doctor_parser.set_defaults(handler=handle_doctor)

    run_parser = subparsers.add_parser("run", help="Preview or execute selected UI automation cases")
    def add_selection_arguments(command_parser: argparse.ArgumentParser) -> None:
        command_parser.add_argument("--module")
        command_parser.add_argument("--feature")
        command_parser.add_argument("--story")
        command_parser.add_argument("--priority")
        command_parser.add_argument("--site")
        command_parser.add_argument("--case-id")
        command_parser.add_argument("--path")
        command_parser.add_argument("--nodeid")
    add_selection_arguments(run_parser)
    run_parser.add_argument("--dry-run", action="store_true")
    run_parser.add_argument("--workers", help="并发 worker 数，支持 1、正整数或 auto；默认 1")
    run_parser.add_argument("--max-workers", type=int, help="auto/N 的安全上限，默认 4")
    run_parser.add_argument("--case-timeout", type=int, help="单条用例超时秒数，默认 300；0 表示关闭")
    run_parser.add_argument("--idle-timeout", type=int, help="pytest 阶段无输出/无产物进展超时秒数，默认按选中用例数动态取 900/1800/2400；0 表示关闭")
    run_parser.add_argument("--phase-timeout", type=int, help="pytest 阶段总时长硬上限秒数，默认关闭")
    run_parser.add_argument("--failed-reruns", type=int, help="失败用例二次执行次数，默认 1；0 表示关闭")
    run_parser.add_argument(
        "--artifact-retention",
        choices=["full", "lean"],
        help="运行产物保留策略；lean 仅在真实执行通过后清理重复中间件",
    )
    run_parser.set_defaults(handler=handle_run)

    ops_parser = subparsers.add_parser("ops", help="Maintenance commands for catalog and identifier governance")
    ops_subparsers = ops_parser.add_subparsers(dest="ops_command", required=True)
    ops_catalog_build = ops_subparsers.add_parser("catalog-build", help="Rebuild catalog metadata")
    ops_catalog_build.add_argument("--output")
    ops_catalog_build.set_defaults(handler=handle_catalog_build)
    ops_identifier_audit = ops_subparsers.add_parser("audit-identifiers", help="Audit and optionally apply missing identifiers")
    ops_identifier_audit.add_argument("--output-json")
    ops_identifier_audit.add_argument("--output-md")
    ops_identifier_audit.add_argument("--apply", action="store_true")
    ops_identifier_audit.set_defaults(handler=handle_identifier_audit)
    return parser


def _legacy_dispatch(argv: list[str]) -> int | None:
    if not argv:
        return None

    command = argv[0]
    if command == "catalog":
        parser = argparse.ArgumentParser(prog="python -m tooling.ok_test catalog")
        subparsers = parser.add_subparsers(dest="catalog_command", required=True)
        build = subparsers.add_parser("build")
        build.add_argument("--output")
        build.set_defaults(handler=handle_catalog_build)
        args = parser.parse_args(argv[1:])
        return args.handler(args)

    if command == "audit":
        parser = argparse.ArgumentParser(prog="python -m tooling.ok_test audit")
        subparsers = parser.add_subparsers(dest="audit_command", required=True)
        identifiers = subparsers.add_parser("identifiers")
        identifiers.add_argument("--output-json")
        identifiers.add_argument("--output-md")
        identifiers.add_argument("--apply", action="store_true")
        identifiers.set_defaults(handler=handle_identifier_audit)
        args = parser.parse_args(argv[1:])
        return args.handler(args)

    if command == "list":
        parser = argparse.ArgumentParser(prog="python -m tooling.ok_test list")
        parser.add_argument("--module")
        parser.add_argument("--feature")
        parser.add_argument("--story")
        parser.add_argument("--priority")
        parser.add_argument("--site")
        parser.add_argument("--case-id")
        parser.add_argument("--path")
        parser.add_argument("--nodeid")
        parser.set_defaults(handler=handle_list)
        args = parser.parse_args(argv[1:])
        return args.handler(args)

    if command == "coverage":
        parser = argparse.ArgumentParser(prog="python -m tooling.ok_test coverage")
        parser.add_argument("--run-id")
        parser.add_argument("--module")
        parser.add_argument("--dashboard", action="store_true")
        parser.add_argument("--knowledge-base-path")
        parser.add_argument("--dashboard-output")
        parser.set_defaults(handler=handle_coverage)
        args = parser.parse_args(argv[1:])
        return args.handler(args)

    if command == "decide":
        parser = argparse.ArgumentParser(prog="python -m tooling.ok_test decide")
        parser.add_argument("--run-id", required=True)
        parser.set_defaults(handler=handle_decide)
        args = parser.parse_args(argv[1:])
        return args.handler(args)

    return None


def main() -> int:
    legacy_result = _legacy_dispatch(sys.argv[1:])
    if legacy_result is not None:
        return legacy_result
    parser = build_parser()
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
