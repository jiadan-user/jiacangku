#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

SENIOR_QA_SOURCE="${SENIOR_QA_SOURCE:-/Users/a58/Desktop/senior-qa-brain}"
PLAYWRIGHT_SOURCE="${PLAYWRIGHT_SOURCE:-/Users/a58/Desktop/playwright-test-generator}"
OK_UI_SOURCE="${OK_UI_SOURCE:-/Users/a58/Desktop/ok_autotest_ui_skill}"
KNOWLEDGE_BASE_SOURCE="${KNOWLEDGE_BASE_SOURCE:-/Users/a58/Desktop/knowledge_base}"

mkdir -p "${ROOT_DIR}/bundled/skills" "${ROOT_DIR}/bundled/knowledge_base"

rsync -a --delete --exclude '.git' \
  "${SENIOR_QA_SOURCE}/" \
  "${ROOT_DIR}/bundled/skills/senior-qa-brain/"

rsync -a --delete --exclude '.git' \
  "${PLAYWRIGHT_SOURCE}/" \
  "${ROOT_DIR}/bundled/skills/playwright-test-generator/"

rsync -a --delete --exclude '.git' --exclude '.claude' \
  "${KNOWLEDGE_BASE_SOURCE}/" \
  "${ROOT_DIR}/bundled/knowledge_base/"

rsync -a --delete \
  --exclude '.git' \
  --exclude 'venv' \
  --exclude '.pytest_cache' \
  --exclude '__pycache__' \
  --exclude 'allure-results' \
  --exclude 'allure-report' \
  --exclude 'screenshots' \
  --exclude 'reports/ok_test_runs' \
  "${OK_UI_SOURCE}/" \
  "${ROOT_DIR}/bundled/skills/ok_autotest_ui_skill/"

echo "内嵌资源同步完成。"
