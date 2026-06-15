from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal import server_process  # noqa: E402
from agent_orchestra_minimal.server_process import main as server_process_main  # noqa: E402


class ServerProcessHealthStartupTests(unittest.TestCase):
    def test_rejects_existing_listener_even_when_health_url_matches_before_launch(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest = root / "server-processes.json"
            log = root / "server.log"
            stdout = io.StringIO()
            with (
                mock.patch.object(server_process, "tcp_listening", return_value=True),
                mock.patch.object(server_process, "http_health_check", return_value={"ok": True, "status": 200}),
                mock.patch.object(server_process.subprocess, "Popen") as popen,
                redirect_stdout(stdout),
            ):
                result = server_process_main(
                    [
                        "start",
                        "--manifest",
                        str(manifest),
                        "--name",
                        "web",
                        "--cwd",
                        str(root),
                        "--base-url",
                        "http://127.0.0.1:9882",
                        "--port",
                        "9882",
                        "--health-url",
                        "http://127.0.0.1:9882/health",
                        "--health-contains",
                        "run-marker",
                        "--startup-timeout",
                        "1",
                        "--log",
                        str(log),
                        "--",
                        sys.executable,
                        "-c",
                        "import time; time.sleep(30)",
                    ]
                )

            self.assertEqual(result, 1)
            popen.assert_not_called()
            entry = json.loads(manifest.read_text(encoding="utf-8"))["web"]
            self.assertEqual(entry["status"], "startup-failed")
            self.assertEqual(entry["startup_failure"], "port-already-serving-health-url")
            self.assertEqual(entry["health_url"], "http://127.0.0.1:9882/health")
            self.assertEqual(entry["health_contains"], "run-marker")

    def test_records_health_url_for_running_process(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest = root / "server-processes.json"
            log = root / "server.log"
            process = mock.Mock()
            process.pid = 4680
            process.poll.return_value = None

            with (
                mock.patch.object(server_process, "tcp_listening", return_value=False),
                mock.patch.object(server_process.subprocess, "Popen", return_value=process),
                mock.patch.object(server_process, "pgid", return_value=4680),
                mock.patch.object(
                    server_process,
                    "wait_for_startup",
                    return_value={"status": "running", "health_url": "http://127.0.0.1:9883/health"},
                ),
                redirect_stdout(io.StringIO()),
            ):
                result = server_process_main(
                    [
                        "start",
                        "--manifest",
                        str(manifest),
                        "--name",
                        "web",
                        "--cwd",
                        str(root),
                        "--base-url",
                        "http://127.0.0.1:9883",
                        "--port",
                        "9883",
                        "--health-url",
                        "http://127.0.0.1:9883/health",
                        "--health-contains",
                        "run-marker",
                        "--startup-timeout",
                        "1",
                        "--log",
                        str(log),
                        "--",
                        sys.executable,
                        "-c",
                        "import time; time.sleep(30)",
                    ]
                )

            self.assertEqual(result, 0)
            entry = json.loads(manifest.read_text(encoding="utf-8"))["web"]
            self.assertEqual(entry["status"], "running")
            self.assertEqual(entry["health_url"], "http://127.0.0.1:9883/health")
            self.assertEqual(entry["health_contains"], "run-marker")


if __name__ == "__main__":
    unittest.main()
