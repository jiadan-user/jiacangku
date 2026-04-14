from __future__ import annotations

import json
import pprint
import re
import shutil
from collections import defaultdict
from pathlib import Path

from qa_agent.io import read_json, write_json, write_text
from qa_agent.markdown_cases import parse_markdown_document
from qa_agent.models import CaseManifestEntry, CaseStatus, ProofArtifact, ValidationResult
from qa_agent.utils import normalize_text, slugify


SITE_LOCALE = {
    "ae": ("en-AE", "AED"),
    "sg": ("en-SG", "SGD"),
    "us": ("en-US", "USD"),
    "au": ("en-AU", "AUD"),
    "hk": ("zh-HK", "HKD"),
}


class PlaywrightGeneratorIntegration:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()

    def readiness_checks(self, enriched_markdown_path: str | Path) -> list[ValidationResult]:
        doc = parse_markdown_document(enriched_markdown_path)
        env = doc.env_config
        checks = [
            ValidationResult(
                ok=shutil.which("playwright-cli") is not None,
                name="Playwright CLI",
                message="playwright-cli 已安装" if shutil.which("playwright-cli") else "playwright-cli 未安装",
            ),
            ValidationResult(
                ok=(Path.home() / ".playwright" / "cli.config.json").exists()
                or (self.root / ".playwright" / "cli.config.json").exists(),
                name="Playwright CLI 配置",
                message="找到 playwright-cli 配置" if ((Path.home() / ".playwright" / "cli.config.json").exists() or (self.root / ".playwright" / "cli.config.json").exists()) else "缺少 .playwright/cli.config.json",
            ),
            ValidationResult(
                ok=bool(env.get("基础URL")),
                name="基础URL",
                message="测试环境配置包含基础URL" if env.get("基础URL") else "测试环境配置缺少基础URL",
            ),
        ]
        requires_login = env.get("测试账号", "").strip() not in {"", "无"}
        if requires_login:
            checks.append(
                ValidationResult(
                    ok=bool(env.get("测试密码")),
                    name="账号凭据",
                    message="测试账号密码齐备" if env.get("测试密码") else "需要登录但缺少测试密码",
                )
            )
        return checks

    def build_recording_bundle(
        self,
        run_dir: Path,
        enriched_markdown_path: str,
        entries: list[CaseManifestEntry],
    ) -> dict[str, str]:
        bundle_dir = run_dir / "recording_bundle"
        bundle_dir.mkdir(parents=True, exist_ok=True)
        write_json(
            bundle_dir / "bundle.json",
            {
                "enriched_markdown_path": enriched_markdown_path,
                "cases": [entry.__dict__ for entry in entries],
                "max_cases_per_batch": 5,
            },
        )
        write_text(
            bundle_dir / "NEXT_STEP.md",
            "\n".join(
                [
                    "# Playwright 录制资料包",
                    "",
                    "1. 仅处理 bundle.json 中列出的 case。",
                    "2. 每批最多 5 条。",
                    "3. 录制后必须将证明产物保存到 proof_artifacts/*.json。",
                    "4. 如果录制验证失败，生成 bug-report.md，并将对应 case 标记为“阻塞于缺陷”。",
                ]
            ),
        )
        return {
            "bundle_dir": str(bundle_dir),
            "next_step": str(bundle_dir / "NEXT_STEP.md"),
        }

    def load_proof_artifacts(self, proof_dir: str | Path) -> dict[str, ProofArtifact]:
        artifacts: dict[str, ProofArtifact] = {}
        root = Path(proof_dir)
        if not root.exists():
            return artifacts
        for path in sorted(root.iterdir()):
            if path.suffix == ".json":
                payload = read_json(path)
                if payload:
                    artifact = ProofArtifact(**payload)
                    artifact.source_path = str(path)
                    artifacts[artifact.tc_id] = artifact
            elif path.suffix == ".md":
                artifact = self._parse_proof_markdown(path)
                artifacts[artifact.tc_id] = artifact
        return artifacts

    def _parse_proof_markdown(self, path: Path) -> ProofArtifact:
        text = path.read_text(encoding="utf-8")
        tc_match = re.search(r"TC[\w-]+", text)
        tc_id = tc_match.group(0) if tc_match else path.stem
        refs_match = re.search(r"ref list:\s*(.+)", text)
        refs = re.findall(r"e\d+", refs_match.group(1)) if refs_match else []
        js_blocks = re.findall(r"```js\n(.*?)```", text, re.DOTALL)
        verifications = re.findall(r"- Verification point text.*?:\s*\"([^\"]*)\"", text)
        stats = {
            key: int(value)
            for key, value in re.findall(r"(open|snapshot|click|fill|type|press|screenshot|close):(\d+)", text)
        }
        return ProofArtifact(
            tc_id=tc_id,
            batch_id=path.parent.name,
            refs=refs,
            cli_js_code=[line.strip() for block in js_blocks for line in block.splitlines() if line.strip()],
            dynamic_discoveries=[],
            verification_points=verifications,
            cli_stats=stats,
            screenshots=re.findall(r"bug-[^`\s]+\.png", text),
            source_path=str(path),
        )

    def build_batches(self, entries: list[CaseManifestEntry], max_cases: int = 5) -> list[list[CaseManifestEntry]]:
        active = [
            entry
            for entry in entries
            if entry.status in {CaseStatus.NEW_CANDIDATE.value, CaseStatus.REGEN_REQUIRED.value} and entry.ui_automatable
        ]
        happy = [
            entry
            for entry in active
            if entry.priority == "P0" and not self._is_negative(entry)
        ]
        negative = [
            entry
            for entry in active
            if self._is_negative(entry)
        ]
        remaining = [entry for entry in active if entry not in happy and entry not in negative]
        first_batch: list[CaseManifestEntry] = []
        if happy:
            first_batch.append(happy[0])
        if negative:
            first_batch.append(negative[0])
        for entry in active:
            if entry not in first_batch and len(first_batch) < max_cases:
                first_batch.append(entry)
        batches: list[list[CaseManifestEntry]] = [first_batch] if first_batch else []
        leftovers = [entry for entry in active if entry not in first_batch]
        while leftovers:
            batches.append(leftovers[:max_cases])
            leftovers = leftovers[max_cases:]
        return batches

    def _is_negative(self, entry: CaseManifestEntry) -> bool:
        title = normalize_text(entry.title)
        test_type = normalize_text(entry.test_type)
        return any(token in title or token in test_type for token in ["异常", "错误", "负向", "边界", "校验", "invalid", "error"])

    def env_config_from_markdown(self, markdown_path: str | Path) -> dict[str, object]:
        doc = parse_markdown_document(markdown_path)
        env = doc.env_config
        site = env.get("站点", "us").lower()
        locale, currency = SITE_LOCALE.get(site, ("en-US", "USD"))
        return {
            "site": site,
            "site_name": env.get("站点名称") or site.upper(),
            "role": env.get("角色", "visitor"),
            "user_name": env.get("账号名称", "guest"),
            "base_url": env.get("基础URL", ""),
            "test_account": {
                "username": env.get("测试账号", ""),
                "password": env.get("测试密码", ""),
            },
            "locale": locale,
            "currency": currency,
            "browser": {
                "type": "chromium",
                "headless": False,
                "viewport": {"width": 1920, "height": 1080},
            },
            "timeout": {
                "default": 30000,
            },
        }

    def generate_python_drafts(
        self,
        run_dir: Path,
        env_config: dict[str, object],
        module: str,
        feature_key: str,
        entries: list[CaseManifestEntry],
        proof_artifacts: dict[str, ProofArtifact],
    ) -> list[str]:
        output_dir = run_dir / "generated_drafts"
        output_dir.mkdir(parents=True, exist_ok=True)
        groups: dict[str, list[CaseManifestEntry]] = defaultdict(list)
        for entry in entries:
            if entry.tc_id in proof_artifacts:
                groups[feature_key].append(entry)

        draft_paths: list[str] = []
        for group_key, group_entries in groups.items():
            filename = f"test_{module}_{slugify(group_key)}.py"
            path = output_dir / filename
            write_text(path, self._render_group_script(env_config, module, group_key, group_entries, proof_artifacts))
            draft_paths.append(str(path))
        return draft_paths

    def _render_group_script(
        self,
        env_config: dict[str, object],
        module: str,
        feature_key: str,
        entries: list[CaseManifestEntry],
        proof_artifacts: dict[str, ProofArtifact],
    ) -> str:
        module_mark = slugify(module)
        site_mark = slugify(str(env_config.get("site", "us")))
        config_json = pprint.pformat(env_config, width=100, sort_dicts=False)
        lines = [
            '"""',
            f"根据证明产物为 {feature_key} 自动生成。",
            '"""',
            "import pytest",
            "import allure",
            "from utils.logger import setup_logger",
            "",
            "logger = setup_logger()",
            "",
            f"_CONFIG = {config_json}",
            "",
        ]
        for entry in entries:
            proof = proof_artifacts[entry.tc_id]
            func_name = f"test_{slugify(entry.tc_id)}_{slugify(entry.title)[:50]}"
            lines.extend(
                [
                    "",
                    f"@pytest.mark.{entry.generated_case_id}",
                    f"@pytest.mark.{entry.priority.lower()}",
                    f"@pytest.mark.{module_mark}",
                    f"@pytest.mark.{site_mark}",
                    '@allure.feature("OK")',
                    f'@allure.story("{feature_key}")',
                    f'@allure.title("{entry.title}")',
                    f"def {func_name}(page, config):",
                    f'    """{entry.tc_id}: {entry.title}"""',
                    '    with allure.step("执行录制流程"):',
                ]
            )
            if not proof.cli_js_code:
                lines.append("        pass")
            for js_line in proof.cli_js_code:
                translated = self._translate_js_line(js_line)
                lines.append(f"        # 原始录制 JS: {js_line}")
                lines.append(f"        {translated}")
            lines.extend(
                [
                    "",
                    '    with allure.step("验证关键点"):',
                ]
            )
            if proof.verification_points:
                for check in proof.verification_points:
                    escaped = check.replace('"', '\\"')
                    lines.append(f'        assert page.locator("body").inner_text().__contains__("{escaped}"), \\')
                    lines.append(f'            "页面中未找到预期文案: {escaped}"')
            else:
                lines.append('        assert True, "TODO: 补充更明确的验证断言"')
        return "\n".join(lines).rstrip() + "\n"

    def _translate_js_line(self, js_line: str) -> str:
        line = js_line.strip().rstrip(";")
        if line.startswith("await "):
            line = line[6:]
        replacements = {
            ".getByRole(": ".get_by_role(",
            ".getByText(": ".get_by_text(",
            ".getByLabel(": ".get_by_label(",
            ".getByPlaceholder(": ".get_by_placeholder(",
            ".getByTitle(": ".get_by_title(",
            ".getByTestId(": ".get_by_test_id(",
            ".waitForTimeout(": ".wait_for_timeout(",
            ".waitForURL(": ".wait_for_url(",
            ".waitForSelector(": ".wait_for_selector(",
            ".waitFor(": ".wait_for(",
            ".goBack(": ".go_back(",
            ".goForward(": ".go_forward(",
            ".newPage(": ".new_page(",
        }
        for source, target in replacements.items():
            line = line.replace(source, target)
        line = line.replace(".first()", ".first")
        line = re.sub(r"\{ name: '([^']+)' \}", r'name="\1"', line)
        line = re.sub(r'\{ name: "([^"]+)" \}', r'name="\1"', line)
        line = line.replace("'", '"')
        return line
