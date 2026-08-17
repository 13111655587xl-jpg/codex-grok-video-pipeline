from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "grok-imagine-video" / "scripts" / "grok_video.py"


class CLITests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_hermes_dry_run_does_not_submit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "test.mp4"
            result = self.run_cli(
                "generate",
                "--backend",
                "hermes",
                "--prompt",
                "test prompt",
                "--output",
                str(output),
                "--dry-run",
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["backend"], "hermes")
        self.assertEqual(payload["request"]["prompt"], "test prompt")

    def test_progrok_dry_run_does_not_require_installation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "test.mp4"
            result = self.run_cli(
                "generate",
                "--backend",
                "progrok",
                "--prompt",
                "test prompt",
                "--output",
                str(output),
                "--dry-run",
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["backend"], "progrok")

    def test_missing_prompt_is_rejected(self) -> None:
        result = self.run_cli("generate", "--output", "/tmp/test.mp4", "--dry-run")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--prompt", result.stderr)

    def test_invalid_duration_is_rejected(self) -> None:
        result = self.run_cli(
            "generate",
            "--backend",
            "hermes",
            "--prompt",
            "test",
            "--duration",
            "30",
            "--output",
            "/tmp/test.mp4",
            "--dry-run",
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
