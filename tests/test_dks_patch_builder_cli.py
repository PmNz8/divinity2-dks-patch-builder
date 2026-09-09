# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

from dks_patch_builder import cli


ROOT = Path(__file__).resolve().parents[1]


class BuilderCLITests(unittest.TestCase):
    def test_check_does_not_create_a_window_or_load_editor_stack(self) -> None:
        script = """
import importlib.abc, sys
class BlockEditor(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'terrain_viewer', 'webview', 'clr', 'pythonnet'}:
            raise ImportError('editor/WebView dependency forbidden: ' + fullname)
sys.meta_path.insert(0, BlockEditor())
import tkinter
def no_window(*args, **kwargs):
    raise AssertionError('headless check must not create Tk')
tkinter.Tk = no_window
from dks_patch_builder.cli import main
assert main(['check']) == 0
"""
        result = subprocess.run(
            [sys.executable, "-c", script], cwd=ROOT,
            capture_output=True, text=True, timeout=30, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["ok"])
        self.assertEqual(report["frontend"], "tkinter")
        self.assertFalse(report["gui_tested"])

    def test_missing_tk_reports_failure_without_launching_gui(self) -> None:
        with mock.patch.dict(sys.modules, {"tkinter": None}), contextlib.redirect_stdout(io.StringIO()) as output:
            code = cli.main(["check"])
        self.assertEqual(code, 2)
        self.assertFalse(json.loads(output.getvalue())["ok"])

    def test_gui_dispatches_only_when_explicitly_requested(self) -> None:
        with mock.patch("dks_patch_builder.desktop.run_gui", return_value=0) as run:
            self.assertEqual(cli.main(["gui"]), 0)
        run.assert_called_once_with()

    def test_module_check_entrypoint(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "dks_patch_builder", "check"], cwd=ROOT,
            capture_output=True, text=True, timeout=30, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)["gui_tested"])


if __name__ == "__main__":
    unittest.main()
