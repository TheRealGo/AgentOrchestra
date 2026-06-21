from __future__ import annotations

import json
import io
import os
import shlex
import signal
import sys
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex"))

from agent_orchestra_minimal import server_process  # noqa: E402
from agent_orchestra_minimal import server_health  # noqa: E402
from agent_orchestra_minimal import server_process_runtime  # noqa: E402
from agent_orchestra_minimal.server_process import main as server_process_main  # noqa: E402


class ServerProcessTests(unittest.TestCase):
    def test_start_records_manifest_and_stop_updates_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest = root / "server-processes.json"
            log = root / "server.log"
            port = 9876

            with (
                mock.patch.dict(
                    os.environ,
                    {"AGENT_ORCHESTRA_AGENT_ID": "pro-env", "AGENT_ORCHESTRA_TMUX_PANE": "%222"},
                    clear=False,
                ),
                mock.patch.object(server_health, "tcp_listening", return_value=True),
                redirect_stdout(io.StringIO()),
            ):
                start_result = server_process_main(
                    [
                        "start",
                        "--manifest",
                        str(manifest),
                        "--name",
                        "web",
                        "--cwd",
                        str(root),
                        "--base-url",
                        f"http://127.0.0.1:{port}",
                        "--port",
                        str(port),
                        "--allow-tcp-readiness",
                        "--log",
                        str(log),
                        "--",
                        sys.executable,
                        "-c",
                        "import time; time.sleep(30)",
                    ]
                )
            self.assertEqual(start_result, 0)
            data = json.loads(manifest.read_text(encoding="utf-8"))
            entry = data["web"]
            self.assertEqual(entry["base_url"], f"http://127.0.0.1:{port}")
            self.assertEqual(entry["port"], port)
            self.assertEqual(entry["log_path"], str(log))
            self.assertGreater(entry["pid"], 0)
            self.assertGreater(entry["pgid"], 0)
            self.assertEqual(entry["pid"], entry["supervisor_pid"])
            self.assertTrue(Path(entry["stop_file"]).name.startswith("web-"))
            self.assertEqual(entry["status"], "running")
            self.assertEqual(entry["owner_agent_id"], "pro-env")
            self.assertEqual(entry["owner_tmux_pane"], "%222")
            self.assertIn("--manifest", entry["cleanup_command"])
            self.assertIn(shlex.quote(str(manifest)), entry["cleanup_command"])
            self.assertIn("--name web", entry["cleanup_command"])

            with redirect_stdout(io.StringIO()):
                stop_result = server_process_main(["stop", "--manifest", str(manifest), "--name", "web"])
            self.assertEqual(stop_result, 0)
            stopped = json.loads(manifest.read_text(encoding="utf-8"))["web"]
            self.assertEqual(stopped["status"], "stopped")
            self.assertFalse(Path(stopped["stop_file"]).exists())

            time.sleep(0.1)

    def test_stop_falls_back_to_direct_pid_when_group_kill_is_denied(self) -> None:
        calls: list[tuple[int, signal.Signals | int]] = []

        def fake_kill(target: int, sig: signal.Signals | int) -> None:
            calls.append((target, sig))
            if target < 0:
                raise PermissionError("operation not permitted")

        with (
            mock.patch.object(server_process_runtime.os, "kill", side_effect=fake_kill),
            mock.patch.object(server_process_runtime, "alive", return_value=False),
            mock.patch.object(server_process_runtime, "reaped", return_value=False),
            redirect_stderr(io.StringIO()),
        ):
            stopped = server_process_runtime.terminate_group(1234, 5678, 0.01)

        self.assertTrue(stopped)
        self.assertEqual(calls, [(-1234, signal.SIGTERM), (5678, signal.SIGTERM)])

    def test_stop_uses_supervised_stop_file_before_signal_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            stop_file = root / "web.stop"
            entry = {"stop_file": str(stop_file)}
            alive_calls = 0

            def fake_alive(pid: int) -> bool:
                nonlocal alive_calls
                alive_calls += 1
                return alive_calls < 2

            with (
                mock.patch.object(server_process_runtime, "alive", side_effect=fake_alive),
                mock.patch.object(server_process_runtime, "reaped", return_value=False),
            ):
                stopped = server_process_runtime.request_supervised_stop(entry, 2468, 1.0)

            self.assertTrue(stopped)
            self.assertTrue(stop_file.exists())

    def test_parallel_stops_do_not_overwrite_manifest_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest = root / "server-processes.json"

            for name in ("web", "fake-llm"):
                with redirect_stdout(io.StringIO()):
                    result = server_process_main(
                        [
                            "start",
                            "--manifest",
                            str(manifest),
                            "--name",
                            name,
                            "--cwd",
                            str(root),
                            "--base-url",
                            f"http://127.0.0.1/{name}",
                            "--log",
                            str(root / f"{name}.log"),
                            "--",
                            sys.executable,
                            "-c",
                            "import time; time.sleep(30)",
                        ]
                    )
                self.assertEqual(result, 0)

            def stop(name: str) -> int:
                with redirect_stdout(io.StringIO()):
                    return server_process_main(
                        ["stop", "--manifest", str(manifest), "--name", name, "--timeout", "5"]
                    )

            with ThreadPoolExecutor(max_workers=2) as executor:
                results = list(executor.map(stop, ("web", "fake-llm")))

            self.assertEqual(results, [0, 0])
            data = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(data["web"]["status"], "stopped")
            self.assertEqual(data["fake-llm"]["status"], "stopped")

    def test_stop_all_stops_every_running_manifest_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest = root / "server-processes.json"
            data = {
                "web": {"status": "running", "pid": 111, "pgid": 111, "stop_file": str(root / "web.stop")},
                "fake": {"status": "starting", "pid": 222, "pgid": 222, "stop_file": str(root / "fake.stop")},
                "old": {"status": "stopped", "pid": 333, "pgid": 333},
            }
            manifest.write_text(json.dumps(data), encoding="utf-8")

            with (
                mock.patch.object(server_process, "request_supervised_stop", return_value=True) as supervised_stop,
                mock.patch.object(server_process, "terminate_group") as terminate_group,
                redirect_stdout(io.StringIO()) as stdout,
            ):
                result = server_process_main(["stop-all", "--manifest", str(manifest)])

            self.assertEqual(result, 0)
            self.assertEqual(supervised_stop.call_count, 2)
            terminate_group.assert_not_called()
            stopped = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(stopped["web"]["status"], "stopped")
            self.assertEqual(stopped["fake"]["status"], "stopped")
            self.assertEqual(stopped["old"]["status"], "stopped")
            output = json.loads(stdout.getvalue())
            self.assertEqual(output["web"]["status"], "stopped")

if __name__ == "__main__":
    unittest.main()
