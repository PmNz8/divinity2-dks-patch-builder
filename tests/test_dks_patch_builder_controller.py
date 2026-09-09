# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from dks_patch_builder import BuilderController
from tests.test_dks_patch_builder_texture import TexturePackageFixture
from tests.synth_builder import build_synthetic


TEMPLATE = r"Win32\Textures\Dragon_A_DM.nif"
CONTROL = r"Global\Control.bin"


def write_archive(path: Path, entries: list[tuple[str, bytes, str]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(build_synthetic(entries, 1))
    return path


class BuilderControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.packed = self.root / "Packed"
        self.packed.mkdir()
        self.package = TexturePackageFixture(self.root / "package")
        write_archive(self.packed / "Patch.dv2", [(TEMPLATE, self.package.template_payload, "raw")])
        self.dks = write_archive(
            self.packed / "DKS_Patch.dv2",
            [(TEMPLATE, self.package.template_payload, "zlib"), (CONTROL, b"keep", "raw")],
        )
        self.controller = BuilderController()

    def assert_json_safe(self, value: object) -> None:
        json.dumps(value, allow_nan=False)

        def visit(item: object) -> None:
            self.assertNotIsInstance(item, (Path, bytes, tuple))
            if isinstance(item, dict):
                self.assertTrue(all(isinstance(key, str) for key in item))
                for nested in item.values():
                    visit(nested)
            elif isinstance(item, list):
                for nested in item:
                    visit(nested)

        visit(value)

    def open(self) -> dict[str, object]:
        return self.controller.open_archive(
            str(self.packed),
            str(self.dks),
            expected_count=2,
        )

    def test_public_operations_return_json_safe_values(self) -> None:
        responses = [
            self.controller.state(),
            self.open(),
            self.controller.list_entries("texture"),
            self.controller.import_package(str(self.package.root)),
            self.controller.preview(),
            self.controller.cancel(TEMPLATE),
            self.controller.remove_override(CONTROL),
            self.controller.pending_changes(),
            self.controller.clear_pending(),
            self.controller.close(),
        ]
        for response in responses:
            self.assert_json_safe(response)
            self.assertTrue(response["ok"])

    def test_cancelled_dialog_paths_are_successful_no_ops(self) -> None:
        before = self.controller.state()
        for response in (
            self.controller.open_archive("", str(self.dks)),
            self.controller.create_archive(str(self.packed), None),
            self.controller.import_package("   "),
            self.controller.save_as(""),
        ):
            self.assertEqual(response["ok"], True)
            self.assertEqual(response["cancelled"], True)
            self.assert_json_safe(response)
        self.assertEqual(self.controller.state(), before)

    def test_errors_are_reported_without_raising_or_losing_state(self) -> None:
        self.assertTrue(self.open()["ok"])
        self.assertTrue(self.controller.remove_override(CONTROL)["ok"])
        response = self.controller.remove_override(CONTROL)
        self.assertFalse(response["ok"])
        self.assertIn("already targets", response["error"])
        self.assertEqual(response["state"]["pending_count"], 1)
        self.assert_json_safe(response)

    def test_save_as_serializes_nested_transaction_result(self) -> None:
        self.assertTrue(self.open()["ok"])
        self.assertTrue(self.controller.remove_override(CONTROL)["ok"])
        output = self.root / "out" / "DKS_Patch.dv2"
        output.parent.mkdir()
        response = self.controller.save_as(str(output))
        self.assertTrue(response["ok"])
        self.assertEqual(response["result"]["result"]["output_path"], str(output.absolute()))
        self.assertEqual(response["state"]["pending_count"], 0)
        self.assert_json_safe(response)

    def test_controller_import_has_no_gui_dependency_or_side_effect(self) -> None:
        source = (
            Path(__file__).parents[1] / "dks_patch_builder" / "controller.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("tkinter", source)
        self.assertNotIn("pywebview", source)
        self.assertFalse(self.controller.state()["result"]["opened"])


if __name__ == "__main__":
    unittest.main()
