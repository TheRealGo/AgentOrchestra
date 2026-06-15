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

from agent_orchestra_minimal import server_health  # noqa: E402
from agent_orchestra_minimal import server_process  # noqa: E402
from agent_orchestra_minimal.server_process import main as server_process_main  # noqa: E402


class ServerProcessStartupTests(unittest.TestCase):
    def test_records_startup_failure_when_process_exits_before_port_listens(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest = root / "server-processes.json"
            log = root / "server.log"
            stdout = io.StringIO()
            with mock.patch.object(server_health, "tcp_listening", return_value=False), redirect_stdout(stdout):
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
                        "http://127.0.0.1:9877",
                        "--port",
                        "9877",
                        "--allow-tcp-readiness",
                        "--startup-timeout",
                        "1",
                        "--log",
                        str(log),
                        "--",
                        sys.executable,
                        "-c",
                        "import sys; print('bind failed'); sys.exit(48)",
                    ]
                )

            self.assertEqual(result, 1)
            entry = json.loads(manifest.read_text(encoding="utf-8"))["web"]
            self.assertEqual(entry["status"], "startup-failed")
            self.assertEqual(entry["exit_code"], 48)
            self.assertIn("bind failed", entry["log_tail"])
            self.assertEqual(json.loads(stdout.getvalue())["status"], "startup-failed")

    def test_rejects_stale_listener_when_child_exits_after_port_probe_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest = root / "server-processes.json"
            log = root / "server.log"
            stdout = io.StringIO()
            with mock.patch.object(server_health, "tcp_listening", return_value=True), redirect_stdout(stdout):
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
                        "http://127.0.0.1:9878",
                        "--port",
                        "9878",
                        "--allow-tcp-readiness",
                        "--startup-timeout",
                        "1",
                        "--log",
                        str(log),
                        "--",
                        sys.executable,
                        "-c",
                        "import sys, time; time.sleep(0.05); print('OSError: [Errno 48] Address already in use'); sys.exit(48)",
                    ]
                )

            self.assertEqual(result, 1)
            entry = json.loads(manifest.read_text(encoding="utf-8"))["web"]
            self.assertEqual(entry["status"], "startup-failed")
            self.assertIn("Address already in use", entry["log_tail"])
            self.assertEqual(json.loads(stdout.getvalue())["status"], "startup-failed")

    def test_rejects_port_already_listening_before_launch(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest = root / "server-processes.json"
            log = root / "server.log"
            stdout = io.StringIO()
            with (
                mock.patch.object(server_process, "tcp_listening", return_value=True),
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
                        "http://127.0.0.1:9879",
                        "--port",
                        "9879",
                        "--allow-tcp-readiness",
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
            self.assertEqual(entry["startup_failure"], "port-already-listening")
            self.assertIsNone(entry["pid"])
            self.assertEqual(json.loads(stdout.getvalue())["startup_failure"], "port-already-listening")

    def test_rejects_port_without_health_url_or_explicit_tcp_escape_hatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest = root / "server-processes.json"
            log = root / "server.log"
            stdout = io.StringIO()
            with (
                mock.patch.object(server_process, "tcp_listening") as tcp_listening,
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
                        "http://127.0.0.1:9884",
                        "--port",
                        "9884",
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

            self.assertEqual(result, 2)
            tcp_listening.assert_not_called()
            popen.assert_not_called()
            entry = json.loads(manifest.read_text(encoding="utf-8"))["web"]
            self.assertEqual(entry["status"], "startup-failed")
            self.assertEqual(entry["startup_failure"], "missing-health-url")
            self.assertIsNone(entry["pid"])

    def test_timeout_requests_supervised_stop_before_signal_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest = root / "server-processes.json"
            log = root / "server.log"
            process = mock.Mock()
            process.pid = 2468
            process.poll.return_value = None

            stdout = io.StringIO()
            with (
                mock.patch.object(server_process, "tcp_listening", return_value=False),
                mock.patch.object(server_process.subprocess, "Popen", return_value=process),
                mock.patch.object(server_process, "pgid", return_value=2468),
                mock.patch.object(
                    server_process,
                    "wait_for_startup",
                    return_value={"status": "startup-timeout", "exit_code": None},
                ),
                mock.patch.object(server_process, "request_supervised_stop", return_value=True) as supervised_stop,
                mock.patch.object(server_process, "terminate_group") as terminate_group,
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
                        "http://127.0.0.1:9880",
                        "--port",
                        "9880",
                        "--allow-tcp-readiness",
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
            supervised_stop.assert_called_once()
            terminate_group.assert_not_called()
            entry = json.loads(manifest.read_text(encoding="utf-8"))["web"]
            self.assertEqual(entry["status"], "startup-timeout")
            self.assertTrue(entry["stop_file"])
            self.assertEqual(json.loads(stdout.getvalue())["status"], "startup-timeout")

    def test_exports_server_metadata_to_supervised_process_environment(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest = root / "server-processes.json"
            log = root / "server.log"
            captured_env: dict[str, str] = {}
            process = mock.Mock()
            process.pid = 3579
            process.poll.return_value = None

            def fake_popen(*args, **kwargs):
                captured_env.update(kwargs["env"])
                return process

            with (
                mock.patch.object(server_process, "tcp_listening", return_value=False),
                mock.patch.object(server_process.subprocess, "Popen", side_effect=fake_popen),
                mock.patch.object(server_process, "pgid", return_value=3579),
                mock.patch.object(server_process, "wait_for_startup", return_value={"status": "running"}),
                redirect_stdout(io.StringIO()),
            ):
                result = server_process_main(
                    [
                        "start",
                        "--manifest",
                        str(manifest),
                        "--name",
                        "fake-llm",
                        "--cwd",
                        str(root),
                        "--base-url",
                        "http://127.0.0.1:9881",
                        "--port",
                        "9881",
                        "--allow-tcp-readiness",
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
            self.assertEqual(captured_env["AGENT_ORCHESTRA_SERVER_NAME"], "fake-llm")
            self.assertEqual(captured_env["AGENT_ORCHESTRA_SERVER_BASE_URL"], "http://127.0.0.1:9881")
            self.assertEqual(captured_env["AGENT_ORCHESTRA_SERVER_PORT"], "9881")


if __name__ == "__main__":
    unittest.main()
