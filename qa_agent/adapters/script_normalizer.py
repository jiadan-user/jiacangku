from __future__ import annotations

import re
from pathlib import Path

from qa_agent.io import write_text
from qa_agent.models import CaseManifestEntry


class ScriptNormalizer:
    def __init__(self, max_wait_ms: int = 300) -> None:
        self.max_wait_ms = max_wait_ms

    def normalize(
        self,
        draft_paths: list[str],
        entries: list[CaseManifestEntry],
        output_dir: str | Path,
        env_config: dict[str, object],
    ) -> dict[str, str]:
        target_dir = Path(output_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        template = self.select_template(entries, env_config)
        normalized: dict[str, str] = {}
        for draft_path in draft_paths:
            draft = Path(draft_path)
            text = draft.read_text(encoding="utf-8")
            text = self._clamp_waits(text)
            if template == "stateful-session":
                text = self._apply_stateful_template(text)
            elif template == "component-batch":
                text = self._apply_component_template(text)
            normalized_path = target_dir / draft.name
            write_text(normalized_path, text)
            normalized[str(draft)] = str(normalized_path)
        write_text(target_dir / "template_selection.txt", self._template_label(template) + "\n")
        return normalized

    def select_template(self, entries: list[CaseManifestEntry], env_config: dict[str, object]) -> str:
        account = env_config.get("test_account") if isinstance(env_config, dict) else None
        role = str(env_config.get("role", "visitor")) if isinstance(env_config, dict) else "visitor"
        if isinstance(account, dict) and account.get("username") and role != "visitor":
            return "stateful-session"
        if len(entries) > 1:
            return "component-batch"
        return "standard-flow"

    def _clamp_waits(self, text: str) -> str:
        def repl(match: re.Match[str]) -> str:
            current = int(match.group(1))
            if current <= self.max_wait_ms:
                return match.group(0)
            return f"page.wait_for_timeout({self.max_wait_ms})  # 已从 {current}ms 规范化"

        return re.sub(r"page\.wait_for_timeout\((\d+)\)", repl, text)

    def _apply_stateful_template(self, text: str) -> str:
        if "from utils.session_manager import SessionManager" not in text:
            text = text.replace(
                "from utils.logger import setup_logger\n",
                "from utils.logger import setup_logger\nfrom utils.session_manager import SessionManager\nfrom pages.login_page import LoginPage\n",
                1,
            )
        if "@pytest.fixture(scope=\"module\")\ndef prepared_page" not in text:
            fixture_block = """

@pytest.fixture(scope="module")
def prepared_page(page, config):
    session_name = f"{config['site']}_{config.get('role', 'visitor')}_{config.get('user_name', 'guest')}"
    session_manager = SessionManager(page, config["base_url"], session_name)
    if config.get("test_account", {}).get("username"):
        if not session_manager.load_session():
            login_page = LoginPage(page)
            login_page.navigate_to_home_page(base_url=config["base_url"])
            login_page.login(config["test_account"]["username"], config["test_account"]["password"])
            session_manager.save_session()
    yield page
"""
            marker = "\n_CONFIG = "
            pos = text.find(marker)
            if pos != -1:
                config_end = text.find("\n\n", pos)
                if config_end != -1:
                    text = text[: config_end + 2] + fixture_block + text[config_end + 2 :]
        text = re.sub(r"def (test_[^(]+)\(page, config\):", r"def \1(prepared_page, config):", text)

        def _inject_page_alias(match: re.Match[str]) -> str:
            block = match.group(0)
            if "page = prepared_page" not in block:
                return block + "    page = prepared_page\n"
            return block

        text = re.sub(
            r"def test_[^(]+\(prepared_page, config\):\n\s+\"\"\"[^\n]+\"\"\"\n",
            _inject_page_alias,
            text,
        )
        return text

    def _apply_component_template(self, text: str) -> str:
        if "@pytest.fixture(scope=\"module\")\ndef component_page" not in text:
            fixture_block = """

@pytest.fixture(scope="module")
def component_page(page, config):
    return page
"""
            marker = "\n_CONFIG = "
            pos = text.find(marker)
            if pos != -1:
                config_end = text.find("\n\n", pos)
                if config_end != -1:
                    text = text[: config_end + 2] + fixture_block + text[config_end + 2 :]
        text = re.sub(r"def (test_[^(]+)\(page, config\):", r"def \1(component_page, config):", text)

        def _inject_page_alias(match: re.Match[str]) -> str:
            block = match.group(0)
            if "page = component_page" not in block:
                return block + "    page = component_page\n"
            return block

        text = re.sub(
            r"def test_[^(]+\(component_page, config\):\n\s+\"\"\"[^\n]+\"\"\"\n",
            _inject_page_alias,
            text,
        )
        return text

    def _template_label(self, template: str) -> str:
        return {
            "standard-flow": "标准流程模板",
            "component-batch": "组件批量模板",
            "stateful-session": "有状态会话模板",
        }.get(template, template)
