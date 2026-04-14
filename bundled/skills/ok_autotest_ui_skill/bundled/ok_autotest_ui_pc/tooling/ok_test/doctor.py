from __future__ import annotations

import argparse
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

from .common import ROOT_DIR, resolve_pytest_command

SECRET_PATTERNS = [
    re.compile(r"@58\.com", re.IGNORECASE),
    re.compile(r"password\s*[:=]\s*[\"'][^\"']+[\"']", re.IGNORECASE),
]
ABSOLUTE_PATH_PATTERN = re.compile(r"/Users/[^\"'\s]+")
EXTERNAL_CAR_IMAGES_DIR = ROOT_DIR / "test_data" / "car_images"
RESOURCE_REFERENCE_RULES = {
    "bundled_test_data_images": "test_data/images",
    "car_publish_image_dir": "test_images_path",
}
WAIT_FOR_TIMEOUT_PATTERN = re.compile(r"wait_for_timeout\(")
OVERSIZED_FILE_LINE_THRESHOLD = 1500


def _dependency_status(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def _run_collect() -> tuple[int, str, str, str]:
    command, display = resolve_pytest_command()
    full_command = command + ["--collect-only", "-q", "-p", "no:rerunfailures", "-o", "addopts="]
    result = subprocess.run(full_command, cwd=ROOT_DIR, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr, display


def _scan_risks() -> list[str]:
    findings: list[str] = []
    for file_path in (ROOT_DIR / "test_cases").rglob("*.py"):
        rel = file_path.relative_to(ROOT_DIR).as_posix()
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            findings.append(f"secret-like content: {rel}")
        if ABSOLUTE_PATH_PATTERN.search(text):
            findings.append(f"absolute path: {rel}")
    return findings


def _iter_code_files() -> list[Path]:
    files: list[Path] = []
    for relative_dir in ("test_cases", "pages", "utils"):
        files.extend((ROOT_DIR / relative_dir).rglob("*.py"))
    return files


def _count_files(path: Path, patterns: list[str]) -> int:
    total = 0
    for pattern in patterns:
        total += len(list(path.glob(pattern)))
    return total


def _scan_resource_dependencies() -> dict[str, list[str]]:
    findings: dict[str, list[str]] = {key: [] for key in RESOURCE_REFERENCE_RULES}
    for file_path in (ROOT_DIR / "test_cases").rglob("*.py"):
        rel = file_path.relative_to(ROOT_DIR).as_posix()
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        for key, pattern in RESOURCE_REFERENCE_RULES.items():
            if pattern in text:
                findings[key].append(rel)
    return findings


def _scan_wait_for_timeout_usage() -> tuple[int, list[tuple[int, str]]]:
    total = 0
    hotspots: list[tuple[int, str]] = []
    for file_path in _iter_code_files():
        rel = file_path.relative_to(ROOT_DIR).as_posix()
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        count = len(WAIT_FOR_TIMEOUT_PATTERN.findall(text))
        if count:
            total += count
            hotspots.append((count, rel))
    hotspots.sort(reverse=True)
    return total, hotspots[:10]


def _scan_oversized_files() -> list[tuple[int, str]]:
    findings: list[tuple[int, str]] = []
    for file_path in _iter_code_files():
        rel = file_path.relative_to(ROOT_DIR).as_posix()
        with file_path.open("r", encoding="utf-8", errors="ignore") as handle:
            line_count = sum(1 for _ in handle)
        if line_count >= OVERSIZED_FILE_LINE_THRESHOLD:
            findings.append((line_count, rel))
    findings.sort(reverse=True)
    return findings[:10]


def _scan_custom_conftests() -> list[str]:
    findings: list[str] = []
    root_conftest = ROOT_DIR / "test_cases" / "conftest.py"
    for file_path in (ROOT_DIR / "test_cases").rglob("conftest.py"):
        if file_path == root_conftest:
            continue
        rel = file_path.relative_to(ROOT_DIR).as_posix()
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        overridden: list[str] = []
        if "def config(" in text:
            overridden.append("config")
        if "def page(" in text:
            overridden.append("page")
        if overridden:
            findings.append(f"{rel}: overrides {', '.join(overridden)}")
    return sorted(findings)


def handle_doctor(_: argparse.Namespace) -> int:
    collect_code, stdout, stderr, pytest_display = _run_collect()
    unknown_markers = sorted(set(re.findall(r"Unknown pytest\.mark\.([A-Za-z0-9_]+)", stderr)))
    collected = re.search(r"(\d+)\s+tests collected", stdout + "\n" + stderr)

    print("[Python/venv/依赖检查]")
    print(f"python={sys.executable}")
    print(f"python_version={sys.version.split()[0]}")
    print(f"pytest_command={pytest_display}")
    print(f"local_venv_exists={(ROOT_DIR / 'venv' / 'bin' / 'pytest').exists()}")
    print(f"dependency_pytest={_dependency_status('pytest')}")
    print(f"dependency_playwright={_dependency_status('playwright.sync_api')}")
    print(f"dependency_allure={_dependency_status('allure')}")

    print("\n[Playwright 检查]")
    print("playwright_importable=" + str(_dependency_status("playwright.sync_api")))

    print("\n[pytest collect 检查]")
    print(f"collect_exit_code={collect_code}")
    print(f"collected_tests={collected.group(1) if collected else 'unknown'}")
    if collect_code != 0:
        print("collect_stderr_tail=" + stderr.strip().splitlines()[-1] if stderr.strip() else "collect_stderr_tail=<empty>")

    print("\n[marker/config/secrets/path 风险检查]")
    print("unknown_markers=" + (", ".join(unknown_markers) if unknown_markers else "none"))
    for finding in _scan_risks()[:20]:
        print(f"- {finding}")

    wait_total, wait_hotspots = _scan_wait_for_timeout_usage()
    oversized_files = _scan_oversized_files()
    custom_conftests = _scan_custom_conftests()

    print("\n[稳定性治理检查]")
    print(f"wait_for_timeout_total={wait_total}")
    print(f"oversized_file_threshold={OVERSIZED_FILE_LINE_THRESHOLD}")
    print("wait_for_timeout_hotspots=")
    for count, rel in wait_hotspots[:8]:
        print(f"- {count}: {rel}")
    print("oversized_files=")
    for line_count, rel in oversized_files[:8]:
        print(f"- {line_count}: {rel}")
    print("custom_conftest_overrides=")
    for finding in custom_conftests[:8]:
        print(f"- {finding}")

    bundled_images_dir = ROOT_DIR / "test_data" / "images"
    bundled_car_images_dir = ROOT_DIR / "test_data" / "car_images"
    bundled_image_count = _count_files(bundled_images_dir, ["*.png", "*.jpg", "*.jpeg", "*.webp"]) if bundled_images_dir.exists() else 0
    car_exterior_count = _count_files(bundled_car_images_dir, ["*外观*.png", "*外观*.jpg", "*外观*.jpeg", "*外观*.webp"]) if bundled_car_images_dir.exists() else 0
    car_interior_count = _count_files(bundled_car_images_dir, ["*内饰*.png", "*内饰*.jpg", "*内饰*.jpeg", "*内饰*.webp"]) if bundled_car_images_dir.exists() else 0
    resource_refs = _scan_resource_dependencies()

    print("\n[测试资源检查]")
    print(f"bundled_test_data_images_exists={bundled_images_dir.exists()}")
    print(f"bundled_test_data_images_count={bundled_image_count}")
    print(f"bundled_car_images_exists={bundled_car_images_dir.exists()}")
    print(f"bundled_car_exterior_images={car_exterior_count}")
    print(f"bundled_car_interior_images={car_interior_count}")
    print(f"external_car_images_exists={EXTERNAL_CAR_IMAGES_DIR.exists()}")
    print(f"external_car_images_path={EXTERNAL_CAR_IMAGES_DIR}")
    print("resource_reference_files=")
    for key, files in resource_refs.items():
        print(f"- {key}: {len(files)}")
        for rel in files[:8]:
            print(f"  * {rel}")
    return 0 if collect_code == 0 else 1
