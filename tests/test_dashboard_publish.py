import os
import unittest
from unittest.mock import patch

from qa_agent.dashboard_publish import DEFAULT_DASHBOARD_URL, _dashboard_url


class DashboardPublishConfigTest(unittest.TestCase):
    def test_default_dashboard_url_is_remote_dashboard(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(_dashboard_url(), DEFAULT_DASHBOARD_URL)

    def test_env_url_overrides_default(self) -> None:
        with patch.dict(os.environ, {"QA_AGENT_DASHBOARD_URL": "http://127.0.0.1:8001"}, clear=True):
            self.assertEqual(_dashboard_url(), "http://127.0.0.1:8001")

    def test_explicit_url_overrides_env(self) -> None:
        with patch.dict(os.environ, {"QA_AGENT_DASHBOARD_URL": "http://127.0.0.1:8001"}, clear=True):
            self.assertEqual(_dashboard_url("http://example.test:8001"), "http://example.test:8001")


if __name__ == "__main__":
    unittest.main()
