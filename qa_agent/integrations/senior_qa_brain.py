from __future__ import annotations

from pathlib import Path

from qa_agent.io import write_json, write_text
from qa_agent.models import RequirementPacket


class SeniorQABrainIntegration:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.prompts_root = self.root / "references" / "prompts"

    def prepare_analysis_bundle(self, run_dir: Path, requirement: RequirementPacket) -> dict[str, str]:
        bundle_dir = run_dir / "analysis_bundle"
        bundle_dir.mkdir(parents=True, exist_ok=True)
        prompts = {
            "01_analyze_figma": str(self.prompts_root / "01_analyze_figma.md"),
            "02_generate_analysis_report": str(self.prompts_root / "02_generate_analysis_report.md"),
            "03_diff_with_prd": str(self.prompts_root / "03_diff_with_prd.md"),
            "04_generate_markdown_testcases": str(self.prompts_root / "04_generate_markdown_testcases.md"),
        }
        write_json(bundle_dir / "inputs.json", requirement.__dict__)
        write_json(bundle_dir / "prompts.json", prompts)
        write_text(
            bundle_dir / "NEXT_STEP.md",
            "\n".join(
                [
                    "# senior-qa-brain 分析资料包",
                    "",
                    "1. 使用 01_analyze_figma.md 读取并分析 Figma。",
                    "2. 使用 02_generate_analysis_report.md 生成分析报告。",
                    "3. 如果有 PRD，再使用 03_diff_with_prd.md 追加差距分析。",
                    "4. 人工确认后再使用 04_generate_markdown_testcases.md 生成 Markdown 用例。",
                ]
            ),
        )
        return {
            "bundle_dir": str(bundle_dir),
            "next_step": str(bundle_dir / "NEXT_STEP.md"),
        }

    def prepare_testcase_bundle(self, run_dir: Path, analysis_report_path: str) -> dict[str, str]:
        bundle_dir = run_dir / "testcase_bundle"
        bundle_dir.mkdir(parents=True, exist_ok=True)
        write_json(
            bundle_dir / "bundle.json",
            {
                "analysis_report": analysis_report_path,
                "prompt": str(self.prompts_root / "04_generate_markdown_testcases.md"),
            },
        )
        write_text(
            bundle_dir / "NEXT_STEP.md",
            "\n".join(
                [
                    "# Markdown 用例生成说明",
                    "",
                    "基于已确认的分析报告运行 senior-qa-brain 的 04_generate_markdown_testcases prompt。",
                    "生成后的原始 Markdown 请保存为 testcases_raw.md，并作为输入重新传回 conductor。",
                ]
            ),
        )
        return {
            "bundle_dir": str(bundle_dir),
            "next_step": str(bundle_dir / "NEXT_STEP.md"),
        }
