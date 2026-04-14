#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
REGRESSION_DIR="${ROOT_DIR}/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc"

python3 -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"

python -m pip install --upgrade pip
python -m pip install -e "${ROOT_DIR}"

if [[ -f "${REGRESSION_DIR}/requirements.txt" ]]; then
  python -m pip install -r "${REGRESSION_DIR}/requirements.txt"
fi

if command -v playwright >/dev/null 2>&1; then
  playwright install chromium || true
else
  python -m playwright install chromium || true
fi

echo "环境准备完成。"
echo "激活命令: source ${VENV_DIR}/bin/activate"
