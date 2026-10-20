"""Tests for ledger.py and measure.py against tests/fixtures/sample-project."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "plugins" / "prc" / "skills" / "project-coordinator" / "scripts"
FIXTURE = ROOT / "tests" / "fixtures" / "sample-project"


def run(script, *args):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    out = subprocess.run([sys.executable, str(SCRIPTS / script), *args], capture_output=True,
                         text=True, encoding="utf-8", env=env)
    return out.returncode, out.stdout, out.stderr


class LedgerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = self.tmp / "sample"
        shutil.copytree(FIXTURE, self.repo)
        old = time.time() - 60 * 86400
        os.utime(self.repo / "tasks/active/2026-08-01_offline-queue.md", (old, old))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def ledger(self, *args):
        code, out, err = run("ledger.py", str(self.repo), "--json", *args)
        self.assertEqual(code, 0, err)
        return json.loads(out)

    def test_counts_and_percentages(self):
        data = self.ledger()
        self.assertEqual(data["tasks"], {"completed": 3, "open": 4, "percent": 43})
        self.assertEqual(data["steps"], {"done": 5, "total": 10, "percent": 50})
        self.assertEqual(data["source"], "overlay COORDINATOR.md")

    def test_both_checkbox_styles_and_fences(self):
        tasks = {t["name"]: t for t in self.ledger()["open"]}
        self.assertEqual((tasks["offline-queue"]["done"], tasks["offline-queue"]["total"]), (1, 4))
        self.assertEqual((tasks["auth-refresh"]["done"], tasks["auth-refresh"]["total"]), (2, 4))
        self.assertNotIn("README", tasks)

    def test_flags(self):
        tasks = {t["name"]: t for t in self.ledger()["open"]}
        self.assertIn("stale", tasks["offline-queue"]["flags"])
        self.assertIn("all ticked, not archived", tasks["export-csv"]["flags"])
        self.assertIn("says done, still open", tasks["export-csv"]["flags"])
        self.assertEqual(tasks["search-index"]["flags"], ["no checkboxes"])
        self.assertEqual(tasks["offline-queue"]["status"], "blocked on design")

    def test_user_steps(self):
        tasks = {t["name"]: t for t in self.ledger()["open"]}
        users = [s["text"] for s in tasks["auth-refresh"]["remaining"] if s["user"]]
        self.assertEqual(users, ["USER: rotate the production signing key"])

    def test_dashboard_unicode_and_ascii(self):
        code, out, _ = run("ledger.py", str(self.repo))
        self.assertEqual(code, 0)
        self.assertIn("Tasks  █████████░░░░░░░░░░░  3/7", out)
        self.assertIn("REMAINING STEPS (5)", out)
        code, out, _ = run("ledger.py", str(self.repo), "--ascii")
        self.assertIn("Tasks  #########...........", out)
        self.assertNotIn("█", out)

    def test_arguments_override_overlay_and_missing_dirs(self):
        (self.repo / "work").mkdir()
        (self.repo / "work" / "x.md").write_text("- [ ] one\n- [x] two\n", encoding="utf-8")
        data = self.ledger("--active", "work", "--completed", "nowhere")
        self.assertEqual(data["source"], "arguments")
        self.assertEqual(data["tasks"]["completed"], 0)
        self.assertEqual(data["steps"], {"done": 1, "total": 2, "percent": 50})
        empty = self.tmp / "empty"
        empty.mkdir()
        code, _, err = run("ledger.py", str(empty))
        self.assertEqual(code, 2)
        self.assertIn("--active", err)


class MeasureTest(unittest.TestCase):
    def test_reads_overlay_and_candidates(self):
        code, out, err = run("measure.py", str(FIXTURE), "--json")
        self.assertEqual(code, 0, err)
        data = json.loads(out)
        self.assertEqual(data["overlay"]["path"], "COORDINATOR.md")
        self.assertEqual(data["overlay"]["ledger"]["ledger-active"], "tasks/active")
        self.assertIn("tasks/", data["candidates"]["tasks"])
        self.assertTrue(data["machine"]["python_cmd"])

    def test_text_output(self):
        code, out, _ = run("measure.py", str(FIXTURE))
        self.assertEqual(code, 0)
        for section in ("MACHINE", "TOOLS", "OVERLAY", "GIT"):
            self.assertIn(section, out)


if __name__ == "__main__":
    unittest.main()
