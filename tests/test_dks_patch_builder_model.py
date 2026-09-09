# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from dks_patch_builder import (
    ADD_NEW,
    ADD_OVERRIDE,
    REMOVE_OVERRIDE,
    REPLACE,
    BuilderModelError,
    DKSPatchBuilderModel,
)
from tests.test_dks_patch_builder_texture import TexturePackageFixture
from dks_patch_builder import dv2lib
from tests.synth_builder import build_synthetic


TEMPLATE = r"Win32\Textures\Dragon_A_DM.nif"
OVERRIDE = r"Win32\Textures\Dragon_B_DM.nif"
NEW = r"Win32\Textures\Mod_New_DM.nif"
CONTROL = r"Global\Control.bin"


def write_archive(path: Path, entries: list[tuple[str, bytes, str]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(build_synthetic(entries, 1))
    return path


class BuilderModelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.packed = self.root / "Packed"
        self.packed.mkdir()
        self.packages = self.root / "packages"
        self.packages.mkdir()
        self.template_fixture = TexturePackageFixture(self.packages / "replace")
        self.template_payload = self.template_fixture.template_payload
        write_archive(
            self.packed / "Patch.dv2",
            [(OVERRIDE, b"old packed override", "raw")],
        )
        write_archive(
            self.packed / "Textures.dv2",
            [(TEMPLATE, self.template_payload, "zlib")],
        )
        self.dks = write_archive(
            self.packed / "DKS_Patch.dv2",
            [
                (TEMPLATE, self.template_payload, "zlib"),
                (CONTROL, b"control", "raw"),
            ],
        )
        self.model = DKSPatchBuilderModel()

    def open(self) -> None:
        self.model.open_archive(self.packed, self.dks, expected_count=3)

    def package(self, name: str, target: str) -> TexturePackageFixture:
        fixture = TexturePackageFixture(self.packages / name)
        fixture.write_asset(target_logical_path=target)
        return fixture

    def test_open_lists_every_entry_and_filters_without_type_assumptions(self) -> None:
        snapshot = self.model.open_archive(self.packed, self.dks, expected_count=3)
        self.assertTrue(snapshot.opened)
        self.assertEqual(snapshot.entry_count, 2)
        self.assertEqual([row.path for row in self.model.list_entries()], [TEMPLATE, CONTROL])
        self.assertEqual([row.path for row in self.model.list_entries("control")], [CONTROL])
        self.assertEqual(self.model.list_entries("absent"), ())

    def test_import_classifies_replace_override_and_new_in_queue_order(self) -> None:
        self.open()
        override = self.package("override", OVERRIDE)
        new = self.package("new", NEW)
        replace_row = self.model.import_package(self.template_fixture.root)
        override_row = self.model.import_package(override.root)
        new_row = self.model.import_package(new.root)

        self.assertEqual(
            [replace_row.action, override_row.action, new_row.action],
            [REPLACE, ADD_OVERRIDE, ADD_NEW],
        )
        self.assertEqual([row.order for row in self.model.pending_changes()], [1, 2, 3])
        self.assertIn("add_new_no_existing_occurrence", new_row.warning_codes)
        self.assertEqual(
            {row.path: row.pending_action for row in self.model.list_entries()},
            {TEMPLATE: REPLACE, CONTROL: None},
        )

    def test_duplicate_casefold_is_rejected_until_cancelled(self) -> None:
        self.open()
        self.model.import_package(self.template_fixture.root)
        duplicate = self.package("duplicate", TEMPLATE.lower())
        with self.assertRaisesRegex(BuilderModelError, "already targets"):
            self.model.import_package(duplicate.root)
        cancelled = self.model.cancel(TEMPLATE.upper())
        self.assertEqual(cancelled.action, REPLACE)
        accepted = self.model.import_package(duplicate.root)
        self.assertEqual(accepted.action, REPLACE)

    def test_invalid_package_does_not_mutate_pending_queue(self) -> None:
        self.open()
        self.model.remove_override(CONTROL)
        bad = self.package("bad", NEW)
        document = json.loads((bad.root / "asset.json").read_text(encoding="utf-8"))
        document["template"]["payload_sha256"] = "0" * 64
        (bad.root / "asset.json").write_text(json.dumps(document), encoding="utf-8")
        before = self.model.pending_changes()
        with self.assertRaisesRegex(BuilderModelError, "cannot import"):
            self.model.import_package(bad.root)
        self.assertEqual(self.model.pending_changes(), before)

    def test_remove_cancel_and_clear_only_affect_pending_state(self) -> None:
        self.open()
        before = self.dks.read_bytes()
        row = self.model.remove_override(CONTROL)
        self.assertEqual(row.action, REMOVE_OVERRIDE)
        self.assertEqual(self.model.cancel(CONTROL).target_logical_path, CONTROL)
        self.model.remove_override(CONTROL)
        self.model.import_package(self.template_fixture.root)
        self.assertEqual(self.model.clear_pending(), 2)
        self.assertEqual(self.model.pending_changes(), ())
        self.assertEqual(self.dks.read_bytes(), before)

    def test_pending_changes_guard_open_close_and_explicit_discard(self) -> None:
        self.open()
        self.model.remove_override(CONTROL)
        with self.assertRaisesRegex(BuilderModelError, "pending changes"):
            self.model.close()
        with self.assertRaisesRegex(BuilderModelError, "pending changes"):
            self.model.open_archive(self.packed, self.dks)
        self.assertFalse(self.model.close(discard_pending=True).opened)

    def test_stale_save_failure_preserves_pending_and_does_not_publish(self) -> None:
        self.open()
        self.model.remove_override(CONTROL)
        write_archive(
            self.dks,
            [(TEMPLATE, self.template_payload, "zlib"), (CONTROL, b"changed", "raw")],
        )
        changed = self.dks.read_bytes()
        with self.assertRaisesRegex(BuilderModelError, "cannot save"):
            self.model.save_in_place()
        self.assertEqual(self.dks.read_bytes(), changed)
        self.assertEqual(len(self.model.pending_changes()), 1)
        self.assertFalse(self.dks.with_name("DKS_Patch.dv2.bak").exists())

    def test_in_place_save_refreshes_document_clears_queue_and_keeps_backup(self) -> None:
        self.open()
        before = self.dks.read_bytes()
        self.model.remove_override(CONTROL)
        self.model.import_package(self.template_fixture.root)
        outcome = self.model.save_in_place()

        self.assertTrue(outcome.selected_output)
        self.assertFalse(self.model.has_pending_changes)
        self.assertEqual(self.dks.with_name("DKS_Patch.dv2.bak").read_bytes(), before)
        session = dv2lib.DV2Session(self.dks)
        self.assertEqual([entry.path for entry in session.entries], [TEMPLATE])
        self.assertEqual(session.read_entry_bytes(TEMPLATE), self.template_payload)
        self.assertEqual(self.model.snapshot().selected_sha256, outcome.result.output_sha256)

    def test_save_as_exact_external_selects_output_and_clears_queue(self) -> None:
        self.open()
        self.model.remove_override(CONTROL)
        output = self.root / "external" / "DKS_Patch.dv2"
        output.parent.mkdir()
        outcome = self.model.save_as(output)
        self.assertTrue(outcome.selected_output)
        self.assertEqual(self.model.snapshot().selected_dks, str(output.absolute()))
        self.assertFalse(self.model.has_pending_changes)
        self.assertTrue(self.dks.exists())

    def test_save_as_exact_inside_packed_accounts_for_new_archive(self) -> None:
        self.open()
        self.model.remove_override(CONTROL)
        output = self.packed / "mods" / "DKS_Patch.dv2"
        output.parent.mkdir()
        outcome = self.model.save_as(output)
        self.assertTrue(outcome.selected_output)
        self.assertEqual(self.model.inventory.archive_count, 4)  # type: ignore[union-attr]
        self.assertEqual(self.model.snapshot().selected_dks, str(output.absolute()))

    def test_save_as_unusual_name_is_nonfatal_and_keeps_current_pending(self) -> None:
        self.open()
        self.model.remove_override(CONTROL)
        output = self.root / "preview.dv2"
        outcome = self.model.save_as(output)
        self.assertFalse(outcome.selected_output)
        self.assertTrue(outcome.warnings)
        self.assertEqual(self.model.snapshot().selected_dks, str(self.dks.absolute()))
        self.assertEqual(len(self.model.pending_changes()), 1)
        self.assertTrue(output.exists())

    def test_save_as_unusual_name_inside_packed_refreshes_corpus(self) -> None:
        self.open()
        self.model.remove_override(CONTROL)
        output = self.packed / "preview.dv2"
        outcome = self.model.save_as(output)
        self.assertFalse(outcome.selected_output)
        self.assertEqual(self.model.inventory.archive_count, 4)  # type: ignore[union-attr]
        self.assertEqual(self.model.snapshot().selected_dks, str(self.dks.absolute()))
        self.assertEqual(len(self.model.pending_changes()), 1)

    def test_create_new_inside_packed_rescans_and_opens_empty_archive(self) -> None:
        self.dks.unlink()
        model = DKSPatchBuilderModel()
        snapshot = model.create_archive(
            self.packed,
            self.dks,
            expected_count=2,
        )
        self.assertTrue(snapshot.opened)
        self.assertEqual(snapshot.entry_count, 0)
        self.assertEqual(model.inventory.archive_count, 3)  # type: ignore[union-attr]
        self.assertEqual(dv2lib.DV2Session(self.dks).deep_verify()["entries"], 0)

    def test_model_has_no_asset_codec_or_gui_dependency(self) -> None:
        source = (Path(__file__).parents[1] / "dks_patch_builder" / "model.py").read_text(
            encoding="utf-8"
        )
        for forbidden in (
            "tools.texture_codec",
            "TextureNIFHandler",
            "tkinter",
            "pywebview",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
