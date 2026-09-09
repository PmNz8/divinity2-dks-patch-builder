from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
import stat
import tempfile
import unittest
from unittest import mock

from dks_patch_builder import (
    ADD_NEW,
    ADD_OVERRIDE,
    CompiledResource,
    HandlerError,
    PackedInventoryError,
    PlannerError,
    REPLACE,
    REMOVE_OVERRIDE,
    find_occurrences,
    plan_compiled_resource,
    plan_remove_override,
    scan_packed,
    select_dks_patch,
    stage_compiled_plan,
    stage_remove_plan,
)
from dks_patch_builder import dv2lib
from tests.synth_builder import build_synthetic


def write_archive(
    path: Path,
    entries: list[tuple[str, bytes, str]] | None = None,
    *,
    layout_mode: int = 1,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(build_synthetic(entries or [], layout_mode))
    return path


def compiled_resource(
    *,
    template: str = r"Win32\Textures\Template.nif",
    target: str = r"Win32\Textures\Target.nif",
    template_payload: bytes = b"template bytes",
    compiled_payload: bytes = b"compiled bytes",
    preferred_storage_mode: str = "raw",
) -> CompiledResource:
    return CompiledResource(
        asset_type="texture_nif",
        template_logical_path=template,
        target_logical_path=target,
        compiled_payload=compiled_payload,
        compiled_sha256=hashlib.sha256(compiled_payload).hexdigest(),
        compiled_size=len(compiled_payload),
        template_sha256=hashlib.sha256(template_payload).hexdigest(),
        template_size=len(template_payload),
        payload_changed=compiled_payload != template_payload,
        preferred_storage_mode=preferred_storage_mode,
    )


class InventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "Packed"
        self.root.mkdir()

    def test_scan_is_deterministic_and_does_not_hash_archives(self) -> None:
        write_archive(self.root / "Patch.dv2")
        write_archive(self.root / "Maps" / "b.dv2")
        write_archive(self.root / "Maps" / "a.dv2")
        with mock.patch.object(
            dv2lib, "hash_and_size_file", side_effect=AssertionError("scan must not hash")
        ):
            inventory = scan_packed(self.root, expected_count=3)
        self.assertEqual(
            [record.relative_path for record in inventory.archives],
            ["Maps/a.dv2", "Maps/b.dv2", "Patch.dv2"],
        )
        self.assertEqual(inventory.root_patch.relative_path, "Patch.dv2")
        self.assertEqual(inventory.root_special_records, (inventory.root_patch,))

    def test_optional_root_overlays_are_reported_without_precedence_claim(self) -> None:
        write_archive(self.root / "Patch.dv2")
        write_archive(self.root / "DKS_Patch.dv2")
        write_archive(self.root / "FOV_Patch.dv2")
        inventory = scan_packed(self.root)
        self.assertEqual(inventory.root_dks_patch.relative_path, "DKS_Patch.dv2")
        self.assertEqual(inventory.root_fov_patch.relative_path, "FOV_Patch.dv2")
        self.assertEqual(
            [record.relative_path for record in inventory.root_special_records],
            ["Patch.dv2", "DKS_Patch.dv2", "FOV_Patch.dv2"],
        )

    def test_missing_root_patch_count_and_casefold_collision_fail(self) -> None:
        write_archive(self.root / "other.dv2")
        with self.assertRaisesRegex(Exception, "root-level Patch"):
            scan_packed(self.root)
        (self.root / "other.dv2").unlink()
        with self.assertRaisesRegex(Exception, "positive integer"):
            scan_packed(self.root, expected_count=0)
        write_archive(self.root / "Patch.dv2")
        write_archive(self.root / "PATCH.DV2")
        if len(list(self.root.iterdir())) != 2:
            self.skipTest("filesystem is case-insensitive; physical case collision cannot be created")
        with self.assertRaisesRegex(Exception, "case-insensitive"):
            scan_packed(self.root)

    def test_malformed_archive_is_not_silently_skipped(self) -> None:
        write_archive(self.root / "Patch.dv2")
        (self.root / "broken.dv2").write_bytes(b"not a dv2")
        with self.assertRaisesRegex(Exception, "cannot parse DV2 archive"):
            scan_packed(self.root)

    def test_link_traversal_is_rejected_when_supported(self) -> None:
        write_archive(self.root / "Patch.dv2")
        real = self.root / "real"
        real.mkdir()
        write_archive(real / "inside.dv2")
        linked = self.root / "linked"
        try:
            linked.symlink_to(real, target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"symlink creation unavailable: {error}")
        with self.assertRaisesRegex(Exception, "symlink or reparse"):
            scan_packed(self.root)

    def test_occurrences_hash_physical_and_matching_logical_payload_only(self) -> None:
        logical = r"Win32\Textures\Target.nif"
        write_archive(self.root / "Patch.dv2", [(logical, b"one", "raw")])
        second = write_archive(
            self.root / "Maps" / "Map.dv2",
            [(logical.lower(), b"two", "zlib"), (r"Other\ignored.bin", b"x", "raw")],
        )
        inventory = scan_packed(self.root)
        occurrences = find_occurrences(inventory, logical.upper())
        self.assertEqual(len(occurrences), 2)
        self.assertEqual([row.physical_relative_path for row in occurrences], ["Maps/Map.dv2", "Patch.dv2"])
        self.assertEqual([row.storage_mode for row in occurrences], ["zlib", "raw"])
        self.assertEqual(
            occurrences[0].physical_sha256,
            hashlib.sha256(second.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            {row.logical_sha256 for row in occurrences},
            {hashlib.sha256(b"one").hexdigest(), hashlib.sha256(b"two").hexdigest()},
        )
        with self.assertRaisesRegex(Exception, "exceeds occurrence limit"):
            find_occurrences(inventory, logical, maximum_size=2)

    def test_matching_archive_table_mutation_after_scan_fails_closed_before_hash(self) -> None:
        original = r"Win32\Textures\Target.nif"
        changed = r"Win32\Textures\TargeT.nif"
        archive = write_archive(self.root / "Patch.dv2", [(original, b"payload", "raw")])
        inventory = scan_packed(self.root)
        archive.write_bytes(build_synthetic([(changed, b"payload", "raw")], 1))
        self.assertEqual(archive.stat().st_size, inventory.root_patch.file_size)
        with mock.patch.object(
            dv2lib, "hash_and_size_file", side_effect=AssertionError("stale table must fail before hash")
        ):
            with self.assertRaisesRegex(PackedInventoryError, "entry table is stale"):
                find_occurrences(inventory, original)


class PlannerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "Packed"
        self.root.mkdir()

    def inventory_with_selected(
        self,
        selected_entries: list[tuple[str, bytes, str]],
        other_entries: list[tuple[str, bytes, str]] | None = None,
        *,
        active_root: bool = False,
    ):
        write_archive(self.root / "Patch.dv2", other_entries or [])
        if active_root:
            write_archive(self.root / "DKS_Patch.dv2", selected_entries)
        else:
            write_archive(self.root / "DKS_Patch.dv2", selected_entries)
        return scan_packed(self.root), self.root / "DKS_Patch.dv2"

    def test_all_classifications_and_warnings(self) -> None:
        target = r"Win32\Textures\Target.nif"
        template = r"Win32\Textures\Template.nif"
        # REPLACE: the selected DKS contains the target and preserves zlib.
        inventory, selected_path = self.inventory_with_selected(
            [(target, b"old", "zlib"), (template, b"template bytes", "raw")],
            [(target, b"override", "raw"), (template, b"template bytes", "raw")],
        )
        selected = select_dks_patch(selected_path, inventory)
        plan = plan_compiled_resource(
            inventory,
            selected,
            compiled_resource(template=template, target=target),
        )
        self.assertEqual(plan.classification, REPLACE)
        self.assertEqual(plan.storage_mode, "zlib")
        self.assertIsNotNone(plan.selected_entry)
        self.assertEqual(len(plan.target_occurrences), 2)
        self.assertEqual(len(plan.template_occurrences), 2)
        self.assertIn("multiple_target_occurrences", {warning.code for warning in plan.warnings})

        # ADD_OVERRIDE: selected DKS lacks target, but Packed contains it.
        write_archive(self.root / "DKS_Patch.dv2")
        inventory = scan_packed(self.root)
        selected = select_dks_patch(self.root / "DKS_Patch.dv2", inventory)
        override_plan = plan_compiled_resource(
            inventory,
            selected,
            compiled_resource(template=template, target=target),
        )
        self.assertEqual(override_plan.classification, ADD_OVERRIDE)
        self.assertEqual(override_plan.storage_mode, "raw")

        # ADD_NEW: neither selected DKS nor Packed contains the target.
        new_target = r"Win32\Textures\BrandNew.nif"
        new_plan = plan_compiled_resource(
            inventory,
            selected,
            compiled_resource(template=template, target=new_target),
        )
        self.assertEqual(new_plan.classification, ADD_NEW)
        self.assertIn("add_new_no_existing_occurrence", {warning.code for warning in new_plan.warnings})

    def test_template_warning_active_root_difference_and_external_selection(self) -> None:
        target = r"Win32\Textures\Target.nif"
        template = r"Win32\Textures\Template.nif"
        write_archive(self.root / "Patch.dv2", [(target, b"target", "raw"), (template, b"wrong", "raw")])
        write_archive(self.root / "DKS_Patch.dv2")
        external = Path(self.temporary.name) / "external" / "DKS_Patch.dv2"
        write_archive(external, [(target, b"old", "raw")])
        inventory = scan_packed(self.root)
        selected = select_dks_patch(external, inventory)
        plan = plan_compiled_resource(
            inventory,
            selected,
            compiled_resource(template=template, target=target),
        )
        codes = {warning.code for warning in plan.warnings}
        self.assertIn("template_hash_mismatch", codes)
        self.assertIn("active_root_dks_differs", codes)
        self.assertEqual(plan.selected_dks_sha256, hashlib.sha256(external.read_bytes()).hexdigest())

    def test_stage_add_replace_remove_binds_identity_and_creates_no_output(self) -> None:
        target = r"Win32\Textures\Target.nif"
        template = r"Win32\Textures\Template.nif"
        write_archive(self.root / "Patch.dv2", [(target, b"override", "raw"), (template, b"template bytes", "raw")])
        selected_path = write_archive(
            self.root / "DKS_Patch.dv2",
            [(target, b"old", "raw"), (template, b"template bytes", "raw")],
        )
        inventory = scan_packed(self.root)
        selected = select_dks_patch(selected_path, inventory)
        original_sha = hashlib.sha256(selected_path.read_bytes()).hexdigest()
        plan = plan_compiled_resource(
            inventory,
            selected,
            compiled_resource(template=template, target=target),
        )
        staged = stage_compiled_plan(plan)
        self.assertEqual(len(staged.pending_ops()), 1)
        self.assertEqual(staged.pending_ops()[0].kind, dv2lib.OP_SET)
        self.assertEqual(staged.pending_ops()[0].key, target.casefold())
        self.assertIn(template, {entry.path for entry in staged.entries})
        self.assertEqual(hashlib.sha256(selected_path.read_bytes()).hexdigest(), original_sha)
        self.assertEqual(set(path.name for path in self.root.iterdir()), {"Patch.dv2", "DKS_Patch.dv2"})

        # ADD staging uses the preferred storage mode and remains in memory.
        write_archive(selected_path, [(template, b"template bytes", "raw")])
        inventory = scan_packed(self.root)
        selected = select_dks_patch(selected_path, inventory)
        add_plan = plan_compiled_resource(
            inventory,
            selected,
            compiled_resource(template=template, target=target, preferred_storage_mode="raw"),
        )
        self.assertEqual(add_plan.classification, ADD_OVERRIDE)
        staged = stage_compiled_plan(add_plan)
        self.assertEqual(len(staged.pending_ops()), 1)
        self.assertEqual(staged.pending_ops()[0].kind, dv2lib.OP_ADD)
        self.assertEqual(staged.pending_ops()[0].storage, "raw")
        self.assertIn(template, {entry.path for entry in staged.entries})

        # Removal is explicit and also creates only an in-memory pending op.
        write_archive(selected_path, [(target, b"old", "raw"), (template, b"template bytes", "raw")])
        inventory = scan_packed(self.root)
        selected = select_dks_patch(selected_path, inventory)
        removal = plan_remove_override(inventory, selected, target)
        self.assertEqual(removal.classification, REMOVE_OVERRIDE)
        staged_remove = stage_remove_plan(removal)
        self.assertEqual(len(staged_remove.pending_ops()), 1)
        self.assertEqual(staged_remove.pending_ops()[0].kind, dv2lib.OP_REMOVE)
        self.assertIn(template, {entry.path for entry in staged_remove.entries})
        with self.assertRaisesRegex(PlannerError, "no entry"):
            plan_remove_override(inventory, selected, r"Win32\Textures\Missing.nif")

    def test_compiled_resource_storage_mode_uses_dv2_modes(self) -> None:
        with self.assertRaises(HandlerError):
            compiled_resource(preferred_storage_mode="not-a-dv2-mode")

    def test_stale_selected_archive_is_rejected_before_staging(self) -> None:
        target = r"Win32\Textures\Target.nif"
        write_archive(self.root / "Patch.dv2")
        selected_path = write_archive(self.root / "DKS_Patch.dv2", [(target, b"old", "raw")])
        inventory = scan_packed(self.root)
        selected = select_dks_patch(selected_path, inventory)
        plan = plan_compiled_resource(inventory, selected, compiled_resource(target=target))
        selected_path.write_bytes(selected_path.read_bytes() + b"\x00")
        with self.assertRaisesRegex(PlannerError, "stale archive"):
            stage_compiled_plan(plan)

    def test_selected_dks_hashes_before_and_after_parse_and_rejects_between_hash_mutation(self) -> None:
        target = r"Win32\Textures\Target.nif"
        write_archive(self.root / "Patch.dv2")
        selected_path = write_archive(self.root / "DKS_Patch.dv2", [(target, b"old", "raw")])
        real_hash = dv2lib.hash_and_size_file
        selected_calls = 0

        def hash_then_mutate(path: Path):
            nonlocal selected_calls
            result = real_hash(path)
            if Path(path).absolute() == selected_path.absolute():
                selected_calls += 1
                if selected_calls == 1:
                    selected_path.write_bytes(
                        build_synthetic([(target, b"new", "raw")], 1)
                    )
            return result

        with mock.patch.object(dv2lib, "hash_and_size_file", side_effect=hash_then_mutate):
            with self.assertRaisesRegex(PackedInventoryError, "changed while hashing/parsing"):
                select_dks_patch(selected_path)
        self.assertEqual(selected_calls, 2)


if __name__ == "__main__":
    unittest.main()
