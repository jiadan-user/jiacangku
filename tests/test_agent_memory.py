from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from qa_agent.agent_memory import MemoryExporter, MemoryRetriever, MemoryStore
from qa_agent.agent_memory.candidate import build_candidate_from_text


class AgentMemoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / ".agent_memory"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_init_creates_expected_files(self) -> None:
        store = MemoryStore(self.root)
        store.init()

        self.assertTrue((self.root / "MEMORY.md").exists())
        self.assertTrue((self.root / "config.yaml").exists())
        self.assertTrue((self.root / "index.jsonl").exists())
        self.assertTrue((self.root / "memories" / "corrections.jsonl").exists())
        self.assertTrue((self.root / "pending" / "candidates.jsonl").exists())
        self.assertTrue((self.root / "logs" / "memory_events.jsonl").exists())

    def test_candidate_promote_search_and_export(self) -> None:
        store = MemoryStore(self.root)
        candidate = build_candidate_from_text(
            "QA Agent 不要自动判断模式，必须让用户选择",
            scope=["qa_agent", "mode_selection"],
            tags=["qa-agent", "workflow"],
        )
        candidate = store.append_candidate(candidate)

        self.assertEqual(len(store.list_candidates()), 1)
        memory = store.promote(candidate.id)
        self.assertEqual(memory.status, "active")
        self.assertEqual(store.list_candidates(), [])

        results = MemoryRetriever(self.root).search("QA Agent 模式选择")
        self.assertTrue(results)
        self.assertEqual(results[0].memory.id, memory.id)

        output = MemoryExporter(self.root).export("qa-agent", query="模式选择")
        self.assertTrue(output.exists())
        self.assertIn("QA Agent 不要自动判断模式", output.read_text(encoding="utf-8"))

    def test_suggest_redacts_secret_values(self) -> None:
        store = MemoryStore(self.root)
        candidate = build_candidate_from_text(
            "调用接口时不要记录 token=abc123 password:hello https://example.com/a?secret=1",
            scope=["security"],
        )
        stored = store.append_candidate(candidate)

        self.assertIn("token=[REDACTED]", stored.content)
        self.assertIn("password:[REDACTED]", stored.content)
        self.assertIn("https://example.com/a?[REDACTED]", stored.content)

    def test_conflicting_candidate_requires_review(self) -> None:
        store = MemoryStore(self.root)
        first = store.append_candidate(
            build_candidate_from_text(
                "QA Agent 不要自动判断模式，必须让用户选择",
                scope=["qa_agent", "mode_selection"],
            )
        )
        store.promote(first.id)

        second = store.append_candidate(
            build_candidate_from_text(
                "QA Agent 可以自动判断模式",
                scope=["qa_agent", "mode_selection"],
            )
        )

        self.assertEqual(second.suggested_action, "review")
        self.assertEqual(second.risk, "high")
        self.assertTrue(second.conflict_ids)


if __name__ == "__main__":
    unittest.main()
