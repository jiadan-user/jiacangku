#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

SENIOR_QA_SOURCE="${SENIOR_QA_SOURCE:-/Users/a58/Desktop/senior-qa-brain}"
PLAYWRIGHT_SOURCE="${PLAYWRIGHT_SOURCE:-/Users/a58/Desktop/playwright-test-generator}"
OK_UI_SOURCE="${OK_UI_SOURCE:-/Users/a58/Desktop/ok_autotest_ui_skill}"
KNOWLEDGE_BASE_SOURCE="${KNOWLEDGE_BASE_SOURCE:-/Users/a58/Desktop/knowledge_base}"

mkdir -p "${ROOT_DIR}/bundled/skills" "${ROOT_DIR}/bundled/knowledge_base"

write_bundle_manifest() {
  local manifest_path="$1"
  local source_repo="$2"
  local source_commit="$3"
  local synced_target="$4"
  local synced_at
  synced_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  cat > "${manifest_path}" <<EOF
{
  "source_repo": "${source_repo}",
  "source_commit": "${source_commit}",
  "synced_at": "${synced_at}",
  "target": "${synced_target}"
}
EOF
}

ensure_latest_knowledge_base() {
  local branch
  branch="$(git -C "${KNOWLEDGE_BASE_SOURCE}" branch --show-current)"
  if [[ "${branch}" != "main" ]]; then
    echo "knowledge_base 源仓库必须位于 main，当前为: ${branch}" >&2
    exit 1
  fi

  if [[ -n "$(git -C "${KNOWLEDGE_BASE_SOURCE}" status --porcelain)" ]]; then
    echo "knowledge_base 源仓库存在未提交改动，请先清理后再同步。" >&2
    exit 1
  fi

  local remote_head local_head
  remote_head="$(git -C "${KNOWLEDGE_BASE_SOURCE}" ls-remote origin refs/heads/main | awk '{print $1}')"
  if [[ -z "${remote_head}" ]]; then
    echo "无法获取 knowledge_base 远端 main HEAD。" >&2
    exit 1
  fi

  local_head="$(git -C "${KNOWLEDGE_BASE_SOURCE}" rev-parse HEAD)"
  if [[ "${local_head}" != "${remote_head}" ]]; then
    git -C "${KNOWLEDGE_BASE_SOURCE}" pull --ff-only origin main
    local_head="$(git -C "${KNOWLEDGE_BASE_SOURCE}" rev-parse HEAD)"
  fi

  if [[ "${local_head}" != "${remote_head}" ]]; then
    echo "knowledge_base 源仓库未能同步到远端 main 最新提交。" >&2
    exit 1
  fi
}

rsync -a --delete --exclude '.git' \
  "${SENIOR_QA_SOURCE}/" \
  "${ROOT_DIR}/bundled/skills/senior-qa-brain/"

rsync -a --delete --exclude '.git' \
  "${PLAYWRIGHT_SOURCE}/" \
  "${ROOT_DIR}/bundled/skills/playwright-test-generator/"

ensure_latest_knowledge_base

KNOWLEDGE_BASE_REMOTE="$(git -C "${KNOWLEDGE_BASE_SOURCE}" remote get-url origin)"
KNOWLEDGE_BASE_HEAD="$(git -C "${KNOWLEDGE_BASE_SOURCE}" rev-parse HEAD)"

rsync -a --delete --exclude '.git' --exclude '.claude' \
  "${KNOWLEDGE_BASE_SOURCE}/" \
  "${ROOT_DIR}/bundled/knowledge_base/"

rsync -a --delete --exclude '.git' \
  "${KNOWLEDGE_BASE_SOURCE}/.claude/skills/knowledge-base-manager/" \
  "${ROOT_DIR}/bundled/skills/knowledge-base-manager/"

if [[ -f "${ROOT_DIR}/bundled/knowledge_base/README.md" ]]; then
  perl -0pi -e 's#`\.claude/skills/knowledge-base-manager/#`bundled/skills/knowledge-base-manager/#g' \
    "${ROOT_DIR}/bundled/knowledge_base/README.md"
fi

write_bundle_manifest \
  "${ROOT_DIR}/bundled/knowledge_base/.bundle-manifest.json" \
  "${KNOWLEDGE_BASE_REMOTE}" \
  "${KNOWLEDGE_BASE_HEAD}" \
  "bundled/knowledge_base"

write_bundle_manifest \
  "${ROOT_DIR}/bundled/skills/knowledge-base-manager/.bundle-manifest.json" \
  "${KNOWLEDGE_BASE_REMOTE}" \
  "${KNOWLEDGE_BASE_HEAD}" \
  "bundled/skills/knowledge-base-manager"

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
