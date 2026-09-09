from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import dks_patch_builder.transaction as transaction_module
from dks_patch_builder import (
    ADD_OVERRIDE,
    CompiledResource,
    REPLACE,
    REMOVE_OVERRIDE,
    CandidateVerificationError,
    TransactionError,
    save_as_transaction,
    save_in_place_transaction,
    scan_packed,
    select_dks_patch,
    stage_transaction,
    verify_candidate,
    plan_compiled_resource,
    plan_remove_override,
)
from dks_patch_builder import dv2lib
from tests.synth_builder import build_synthetic


TARGET_A = r"Win32\Textures\Target_A.nif"
TARGET_B = r"Win32\Textures\Target_B.nif"
TARGET_C = r"Win32\Textures\Target_C.nif"
TEMPLATE = r"Win32\Textures\Template.nif"
CONTROL = r"Global\Control.bin"


def write_archive(path: Path, entries: list[tuple[str, bytes, str]], *, layout_mode: int = 1) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(build_synthetic(entries, layout_mode))
    return path


def resource(
    target: str,
    payload: bytes,
    *,
    template: str = TEMPLATE,
    template_payload: bytes = b"template",
    preferred_storage_mode: str = "raw",
) -> CompiledResource:
    return CompiledResource(
        asset_type="texture_nif",
        template_logical_path=template,
        target_logical_path=target,
        compiled_payload=payload,
        compiled_sha256=hashlib.sha256(payload).hexdigest(),
        compiled_size=len(payload),
        template_sha256=hashlib.sha256(template_payload).hexdigest(),
        template_size=len(template_payload),
        payload_changed=payload != template_payload,
        preferred_storage_mode=preferred_storage_mode,
    )


class TransactionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.packed = self.root / "Packed"
        self.packed.mkdir()

    def make_fixture(self) -> tuple[Path, object, object, object, object]:
        write_archive(
            self.packed / "Patch.dv2",
            [(TARGET_C, b"packed occurrence", "raw"), (TEMPLATE, b"template", "raw")],
        )
        selected_path = write_archive(
            self.packed / "DKS_Patch.dv2",
            [
                (TARGET_A, b"old A", "zlib"),
                (TARGET_B, b"old B", "raw"),
                (TEMPLATE, b"template", "raw"),
                (CONTROL, b"keep", "raw"),
            ],
        )
        inventory = scan_packed(self.packed)
        selected = select_dks_patch(selected_path, inventory)
        replace_plan = plan_compiled_resource(
            inventory,
            selected,
            resource(TARGET_A, b"new A", preferred_storage_mode="raw"),
        )
        add_plan = plan_compiled_resource(
            inventory,
            selected,
            resource(TARGET_C, b"new C", preferred_storage_mode="raw"),
        )
        remove_plan = plan_remove_override(inventory, selected, TARGET_B)
        return selected_path, replace_plan, add_plan, remove_plan, selected

    def test_stage_mixed_operations_preserves_order_and_writes_nothing(self) -> None:
        selected_path, replace_plan, add_plan, remove_plan, _selected = self.make_fixture()
        before = selected_path.read_bytes()
        staged = stage_transaction((add_plan, remove_plan, replace_plan))

        self.assertEqual(staged.operation_order, (TARGET_C.casefold(), TARGET_B.casefold(), TARGET_A.casefold()))
        self.assertEqual(staged.added, (TARGET_C,))
        self.assertEqual(staged.replaced, (TARGET_A,))
        self.assertEqual(staged.removed, (TARGET_B,))
        self.assertEqual({operation.key for operation in staged.pending_ops}, {
            TARGET_A.casefold(), TARGET_B.casefold(), TARGET_C.casefold()
        })
        self.assertEqual(
            {operation.kind for operation in staged.pending_ops},
            {dv2lib.OP_ADD, dv2lib.OP_SET, dv2lib.OP_REMOVE},
        )
        self.assertEqual(selected_path.read_bytes(), before)
        self.assertEqual({path.name for path in self.packed.iterdir()}, {"Patch.dv2", "DKS_Patch.dv2"})

    def test_duplicate_casefold_and_mixed_selected_identity_are_rejected(self) -> None:
        selected_path, replace_plan, _add_plan, _remove_plan, selected = self.make_fixture()
        duplicate = replace(
            replace_plan,
            target_logical_path=TARGET_A.lower(),
            target_key=TARGET_A.lower().casefold(),
        )
        with self.assertRaisesRegex(TransactionError, "duplicate"):
            stage_transaction((replace_plan, duplicate))

        other_path = self.root / "external" / "DKS_Patch.dv2"
        write_archive(other_path, [(TARGET_A, b"other", "raw")])
        other = select_dks_patch(other_path)
        mixed = replace(replace_plan, selected_dks=other)
        with self.assertRaisesRegex(TransactionError, "same selected DKS identity"):
            stage_transaction((replace_plan, mixed))
        self.assertEqual(selected.physical_path, selected_path.absolute())

    def test_stale_selected_is_rejected_before_staging(self) -> None:
        selected_path, replace_plan, _add_plan, _remove_plan, _selected = self.make_fixture()
        selected_path.write_bytes(build_synthetic(
            [(TARGET_A, b"different", "zlib"), (TARGET_B, b"old B", "raw"), (TEMPLATE, b"template", "raw"), (CONTROL, b"keep", "raw")],
            1,
        ))
        with self.assertRaisesRegex(TransactionError, "stale archive"):
            stage_transaction((replace_plan,))

    def test_save_as_verifies_allowlist_and_is_deterministic(self) -> None:
        selected_path, replace_plan, add_plan, remove_plan, _selected = self.make_fixture()
        staged_one = stage_transaction((replace_plan, add_plan, remove_plan))
        staged_two = stage_transaction((replace_plan, add_plan, remove_plan))
        output_one = self.root / "one.dv2"
        output_two = self.root / "two.dv2"
        result_one = save_as_transaction(staged_one, output_one)
        result_two = save_as_transaction(staged_two, output_two)
        self.assertEqual(output_one.read_bytes(), output_two.read_bytes())
        self.assertEqual(result_one.output_sha256, result_two.output_sha256)
        self.assertEqual(result_one.added, (TARGET_C,))
        self.assertEqual(result_one.replaced, (TARGET_A,))
        self.assertEqual(result_one.removed, (TARGET_B,))
        self.assertEqual(hashlib.sha256(selected_path.read_bytes()).hexdigest(), staged_one.source_sha256)
        verification = verify_candidate(selected_path, output_one, staged_one)
        self.assertEqual(verification.output_sha256, result_one.output_sha256)
        self.assertEqual([entry.path for entry in dv2lib.DV2Session(output_one).entries], [
            TARGET_A, TEMPLATE, CONTROL, TARGET_C,
        ])

    def test_save_restages_immutable_plans_after_mutable_session_is_changed(self) -> None:
        selected_path, replace_plan, _add_plan, _remove_plan, _selected = self.make_fixture()
        staged = stage_transaction((replace_plan,))
        staged.session.clear_pending()
        staged.session.stage_add(TARGET_C, b"accidental extra", "raw")
        output = self.root / "restaged.dv2"
        save_as_transaction(staged, output)
        self.assertEqual(
            [entry.path for entry in dv2lib.DV2Session(output).entries],
            [TARGET_A, TARGET_B, TEMPLATE, CONTROL],
        )
        self.assertEqual(hashlib.sha256(selected_path.read_bytes()).hexdigest(), staged.source_sha256)

        # The in-place boundary also discards the mutated session and uses the
        # immutable one-plan set.
        staged.session.stage_remove(TARGET_B)
        save_in_place_transaction(staged)
        installed = dv2lib.DV2Session(selected_path)
        self.assertEqual([entry.path for entry in installed.entries], [TARGET_A, TARGET_B, TEMPLATE, CONTROL])

    def test_save_as_rejects_existing_output_and_race_winner(self) -> None:
        selected_path, replace_plan, _add_plan, _remove_plan, _selected = self.make_fixture()
        staged = stage_transaction((replace_plan,))
        output = self.root / "existing.dv2"
        output.write_bytes(b"sentinel")
        with self.assertRaises(TransactionError):
            save_as_transaction(staged, output)
        self.assertEqual(output.read_bytes(), b"sentinel")

        race_output = self.root / "race.dv2"
        def race_link(source: Path, destination: Path) -> None:
            race_output.write_bytes(b"race winner")
            raise FileExistsError(destination)

        with mock.patch.object(transaction_module, "_link", side_effect=race_link):
            with self.assertRaisesRegex(TransactionError, "appeared"):
                save_as_transaction(staged, race_output)
        self.assertEqual(race_output.read_bytes(), b"race winner")

    def test_allowlist_rejects_header_path_storage_and_payload_changes(self) -> None:
        selected_path, replace_plan, _add_plan, _remove_plan, _selected = self.make_fixture()
        staged = stage_transaction((replace_plan,))
        candidate = self.root / "candidate.dv2"
        staged.session.save_as(candidate)
        original = candidate.read_bytes()

        # Changing the header is caught independently of the backend report.
        header = bytearray(original)
        header[0:4] = (6).to_bytes(4, "little")
        changed_header = self.root / "changed-header.dv2"
        changed_header.write_bytes(header)
        with self.assertRaises(CandidateVerificationError):
            verify_candidate(selected_path, changed_header, staged)

        # A valid archive with a different target payload fails the target SHA allowlist.
        changed_payload = self.root / "changed-payload.dv2"
        changed_session = dv2lib.DV2Session(candidate)
        changed_session.clear_pending()
        changed_session.stage_set(TARGET_A, b"wrong")
        changed_session.save_as(changed_payload)
        with self.assertRaisesRegex(CandidateVerificationError, "SHA"):
            verify_candidate(selected_path, changed_payload, staged)

    def test_save_as_failure_cleans_owned_candidate_and_preserves_source(self) -> None:
        selected_path, replace_plan, _add_plan, _remove_plan, _selected = self.make_fixture()
        staged = stage_transaction((replace_plan,))
        before = selected_path.read_bytes()
        with mock.patch(
            "dks_patch_builder.transaction.verify_candidate",
            side_effect=CandidateVerificationError("injected verifier failure"),
        ):
            with self.assertRaisesRegex(CandidateVerificationError, "injected"):
                save_as_transaction(staged, self.root / "failed.dv2")
        self.assertEqual(selected_path.read_bytes(), before)
        self.assertEqual(list(self.root.glob(".*.dv2")), [])

    def test_backend_save_failure_leaves_no_candidate(self) -> None:
        selected_path, replace_plan, _add_plan, _remove_plan, _selected = self.make_fixture()
        staged = stage_transaction((replace_plan,))
        before = selected_path.read_bytes()
        with mock.patch.object(
            dv2lib.DV2Session, "save_as", side_effect=OSError("injected backend write failure")
        ):
            with self.assertRaisesRegex(TransactionError, "candidate"):
                save_as_transaction(staged, self.root / "backend-failure.dv2")
        self.assertEqual(selected_path.read_bytes(), before)
        self.assertEqual(list(self.root.glob(".*.dv2")), [])

    def test_backend_partial_save_failure_cleans_owned_candidate(self) -> None:
        selected_path, replace_plan, _add_plan, _remove_plan, _selected = self.make_fixture()
        staged = stage_transaction((replace_plan,))
        before = selected_path.read_bytes()

        def fail_after_partial_save(_session: object, candidate: Path, *args: object, **kwargs: object) -> None:
            candidate.write_bytes(b"partial backend candidate")
            raise OSError("injected backend failure after partial write")

        with mock.patch.object(dv2lib.DV2Session, "save_as", side_effect=fail_after_partial_save):
            with self.assertRaisesRegex(TransactionError, "candidate"):
                save_as_transaction(staged, self.root / "partial-backend-failure.dv2")
        self.assertEqual(selected_path.read_bytes(), before)
        self.assertEqual(list(self.root.glob(".*.dv2")), [])

    def test_backup_copy_failure_leaves_source_and_no_temporary_files(self) -> None:
        selected_path, replace_plan, _add_plan, _remove_plan, _selected = self.make_fixture()
        staged = stage_transaction((replace_plan,))
        before = selected_path.read_bytes()
        with mock.patch.object(
            transaction_module, "_copy_fsync", side_effect=TransactionError("injected backup copy failure")
        ):
            with self.assertRaisesRegex(TransactionError, "backup copy"):
                save_in_place_transaction(staged)
        self.assertEqual(selected_path.read_bytes(), before)
        self.assertFalse(selected_path.with_name("DKS_Patch.dv2.bak").exists())
        self.assertEqual(list(selected_path.parent.glob(".*")), [])

    def test_backup_publish_failure_leaves_source_and_cleans_candidate(self) -> None:
        selected_path, replace_plan, _add_plan, _remove_plan, _selected = self.make_fixture()
        staged = stage_transaction((replace_plan,))
        before = selected_path.read_bytes()
        real_replace = transaction_module._atomic_replace

        def fail_backup_publish(candidate: Path, destination: Path) -> None:
            if destination.name == "DKS_Patch.dv2.bak":
                raise OSError("injected backup publication failure")
            real_replace(candidate, destination)

        with mock.patch.object(
            transaction_module, "_atomic_replace", side_effect=fail_backup_publish
        ):
            with self.assertRaisesRegex(TransactionError, "fixed backup"):
                save_in_place_transaction(staged)
        self.assertEqual(selected_path.read_bytes(), before)
        self.assertFalse(selected_path.with_name("DKS_Patch.dv2.bak").exists())
        self.assertEqual(list(selected_path.parent.glob(".*")), [])

    def test_mode_zero_addition_with_zlib_is_verified(self) -> None:
        target = r"Win32\Textures\ModeZero.nif"
        write_archive(self.packed / "Patch.dv2", [(target, b"packed", "raw")], layout_mode=0)
        selected_path = write_archive(
            self.packed / "DKS_Patch.dv2",
            [(TEMPLATE, b"template", "raw"), (CONTROL, b"keep", "zlib")],
            layout_mode=0,
        )
        inventory = scan_packed(self.packed)
        selected = select_dks_patch(selected_path, inventory)
        plan = plan_compiled_resource(
            inventory,
            selected,
            resource(target, b"added zlib", preferred_storage_mode="zlib"),
        )
        self.assertEqual(plan.classification, ADD_OVERRIDE)
        staged = stage_transaction((plan,))
        result = save_as_transaction(staged, self.root / "mode-zero.dv2")
        self.assertEqual(result.entry_count, 3)
        output_session = dv2lib.DV2Session(self.root / "mode-zero.dv2")
        self.assertEqual(output_session.header.layout_mode, 0)
        self.assertEqual(output_session.find_entry(target).storage_mode, "zlib")
        verify_candidate(selected_path, self.root / "mode-zero.dv2", staged)

    def test_allowlist_rejects_order_and_unchanged_storage_changes(self) -> None:
        selected_path, replace_plan, _add_plan, _remove_plan, _selected = self.make_fixture()
        staged = stage_transaction((replace_plan,))

        reordered = self.root / "reordered.dv2"
        reordered.write_bytes(build_synthetic(
            [(TARGET_B, b"old B", "raw"), (TARGET_A, b"new A", "zlib"),
             (TEMPLATE, b"template", "raw"), (CONTROL, b"keep", "raw")], 1
        ))
        with self.assertRaisesRegex(CandidateVerificationError, "order"):
            verify_candidate(selected_path, reordered, staged)

        changed_storage = self.root / "changed-storage.dv2"
        changed_storage.write_bytes(build_synthetic(
            [(TARGET_A, b"new A", "zlib"), (TARGET_B, b"old B", "zlib"),
             (TEMPLATE, b"template", "raw"), (CONTROL, b"keep", "raw")], 1
        ))
        with self.assertRaisesRegex(CandidateVerificationError, "unchanged storage"):
            verify_candidate(selected_path, changed_storage, staged)

        changed_unrelated = self.root / "changed-unrelated.dv2"
        changed_unrelated.write_bytes(build_synthetic(
            [(TARGET_A, b"new A", "zlib"), (TARGET_B, b"wrong B", "raw"),
             (TEMPLATE, b"template", "raw"), (CONTROL, b"keep", "raw")], 1
        ))
        with self.assertRaisesRegex(CandidateVerificationError, "unchanged logical"):
            verify_candidate(selected_path, changed_unrelated, staged)

        missing_target = self.root / "missing-target.dv2"
        missing_target.write_bytes(build_synthetic(
            [(TARGET_B, b"old B", "raw"), (TEMPLATE, b"template", "raw"),
             (CONTROL, b"keep", "raw")], 1
        ))
        with self.assertRaisesRegex(CandidateVerificationError, "path/order"):
            verify_candidate(selected_path, missing_target, staged)

        extra_target = self.root / "extra-target.dv2"
        extra_target.write_bytes(build_synthetic(
            [(TARGET_A, b"new A", "zlib"), (TARGET_B, b"old B", "raw"),
             (TEMPLATE, b"template", "raw"), (CONTROL, b"keep", "raw"),
             (TARGET_C, b"unexpected", "raw")], 1
        ))
        with self.assertRaisesRegex(CandidateVerificationError, "path/order"):
            verify_candidate(selected_path, extra_target, staged)

    def test_source_change_after_candidate_is_detected_before_save_as_publish(self) -> None:
        selected_path, replace_plan, _add_plan, _remove_plan, _selected = self.make_fixture()
        staged = stage_transaction((replace_plan,))
        before = selected_path.read_bytes()
        real_check = transaction_module._check_bound_source

        def mutate_then_check(current: object):
            selected_path.write_bytes(before + b"changed")
            return real_check(current)

        with mock.patch.object(
            transaction_module, "_check_bound_source", side_effect=mutate_then_check
        ):
            with self.assertRaisesRegex(TransactionError, "changed"):
                save_as_transaction(staged, self.root / "stale.dv2")
        self.assertFalse((self.root / "stale.dv2").exists())

    def test_external_substitution_is_not_removed_by_save_as_cleanup(self) -> None:
        selected_path, replace_plan, _add_plan, _remove_plan, _selected = self.make_fixture()
        staged = stage_transaction((replace_plan,))
        output = self.root / "substituted.dv2"
        real_publish = transaction_module._publish_exclusive

        def publish_then_substitute(candidate: Path, destination: Path) -> Path:
            published = real_publish(candidate, destination)
            published.unlink()
            published.write_bytes(b"external substitution")
            return published

        with mock.patch.object(
            transaction_module, "_publish_exclusive", side_effect=publish_then_substitute
        ):
            with self.assertRaisesRegex(TransactionError, "identity changed"):
                save_as_transaction(staged, output)
        self.assertEqual(output.read_bytes(), b"external substitution")
        self.assertEqual(list(self.root.glob(".*.dv2")), [])

    def test_publish_unlink_failure_cleans_destination_when_identity_is_owned(self) -> None:
        selected_path, replace_plan, _add_plan, _remove_plan, _selected = self.make_fixture()
        staged = stage_transaction((replace_plan,))
        real_unlink = transaction_module._unlink
        calls = 0

        def fail_first_unlink(path: Path) -> None:
            nonlocal calls
            calls += 1
            if calls == 1:
                raise OSError("injected unlink failure")
            real_unlink(path)

        output = self.root / "unlink-failure.dv2"
        with mock.patch.object(transaction_module, "_unlink", side_effect=fail_first_unlink):
            with self.assertRaises(TransactionError):
                save_as_transaction(staged, output)
        self.assertFalse(output.exists())
        self.assertEqual(list(self.root.glob(".*.dv2")), [])

    def test_in_place_failure_before_final_replace_keeps_source_and_cleans_candidate(self) -> None:
        selected_path, replace_plan, _add_plan, _remove_plan, _selected = self.make_fixture()
        staged = stage_transaction((replace_plan,))
        old_source = selected_path.read_bytes()
        real_replace = transaction_module._atomic_replace

        def fail_only_source_replace(candidate: Path, destination: Path) -> None:
            if destination == selected_path.absolute():
                raise OSError("injected final replace failure")
            real_replace(candidate, destination)

        with mock.patch.object(
            transaction_module, "_atomic_replace", side_effect=fail_only_source_replace
        ):
            with self.assertRaisesRegex(TransactionError, "final replacement"):
                save_in_place_transaction(staged)
        self.assertEqual(selected_path.read_bytes(), old_source)
        self.assertEqual(selected_path.with_name("DKS_Patch.dv2.bak").read_bytes(), old_source)
        self.assertEqual(list(selected_path.parent.glob(".*.dv2")), [])

    def test_in_place_save_creates_fixed_byte_perfect_backup_and_replaces_it(self) -> None:
        selected_path, replace_plan, add_plan, remove_plan, _selected = self.make_fixture()
        staged = stage_transaction((replace_plan, add_plan, remove_plan))
        old_source = selected_path.read_bytes()
        backup = selected_path.with_name("DKS_Patch.dv2.bak")
        backup.write_bytes(b"old backup")
        result = save_in_place_transaction(staged)
        self.assertEqual(result.mode, "in_place")
        self.assertEqual(result.output_path, selected_path.absolute())
        self.assertEqual(result.backup_path, backup.absolute())
        self.assertEqual(backup.read_bytes(), old_source)
        self.assertEqual(result.backup_sha256, hashlib.sha256(old_source).hexdigest())
        self.assertNotEqual(selected_path.read_bytes(), old_source)
        self.assertEqual(hashlib.sha256(selected_path.read_bytes()).hexdigest(), result.output_sha256)
        self.assertEqual({path.name for path in selected_path.parent.iterdir()}, {
            "Patch.dv2", "DKS_Patch.dv2", "DKS_Patch.dv2.bak",
        })

    def test_in_place_post_install_failure_restores_source_and_preserves_backup(self) -> None:
        selected_path, replace_plan, _add_plan, _remove_plan, _selected = self.make_fixture()
        staged = stage_transaction((replace_plan,))
        old_source = selected_path.read_bytes()
        backup = selected_path.with_name("DKS_Patch.dv2.bak")
        with mock.patch(
            "dks_patch_builder.transaction._verify_installed",
            side_effect=CandidateVerificationError("injected post-install failure"),
        ):
            with self.assertRaisesRegex(TransactionError, "restored"):
                save_in_place_transaction(staged)
        self.assertEqual(selected_path.read_bytes(), old_source)
        self.assertEqual(backup.read_bytes(), old_source)

    def test_in_place_replace_then_raise_restores_old_source(self) -> None:
        selected_path, replace_plan, _add_plan, _remove_plan, _selected = self.make_fixture()
        staged = stage_transaction((replace_plan,))
        old_source = selected_path.read_bytes()
        real_replace = transaction_module._atomic_replace

        def replace_then_raise(candidate: Path, destination: Path) -> None:
            if destination == selected_path.absolute():
                real_replace(candidate, destination)
                raise OSError("injected after replacement")
            real_replace(candidate, destination)

        with mock.patch.object(
            transaction_module, "_atomic_replace", side_effect=replace_then_raise
        ):
            with self.assertRaisesRegex(TransactionError, "restored"):
                save_in_place_transaction(staged)
        self.assertEqual(selected_path.read_bytes(), old_source)
        self.assertEqual(selected_path.with_name("DKS_Patch.dv2.bak").read_bytes(), old_source)
        self.assertEqual(list(selected_path.parent.glob(".*.dv2")), [])

    def test_in_place_success_then_consumed_invariant_failure_restores_old_source(self) -> None:
        selected_path, replace_plan, _add_plan, _remove_plan, _selected = self.make_fixture()
        staged = stage_transaction((replace_plan,))
        old_source = selected_path.read_bytes()
        real_consumed = transaction_module._candidate_consumed
        calls = 0

        def fail_final_consumed(path: Path) -> bool:
            nonlocal calls
            calls += 1
            if calls == 2:  # backup candidate first, final candidate second
                return False
            return real_consumed(path)

        with mock.patch.object(
            transaction_module, "_candidate_consumed", side_effect=fail_final_consumed
        ):
            with self.assertRaisesRegex(TransactionError, "restored"):
                save_in_place_transaction(staged)
        self.assertEqual(selected_path.read_bytes(), old_source)
        self.assertEqual(selected_path.with_name("DKS_Patch.dv2.bak").read_bytes(), old_source)
        self.assertEqual(list(selected_path.parent.glob(".*.dv2")), [])

    def test_in_place_rejects_wrong_basename_and_link_backup(self) -> None:
        selected_path, replace_plan, _add_plan, _remove_plan, selected = self.make_fixture()
        wrong = self.root / "Not_DKS.dv2"
        write_archive(wrong, [(TARGET_A, b"x", "raw")])
        wrong_selected = replace(selected, physical_path=wrong.absolute())
        wrong_plan = replace(replace_plan, selected_dks=wrong_selected)
        with self.assertRaisesRegex(TransactionError, "basename"):
            stage_transaction((wrong_plan,))

        # The real selected path is valid; a symlink fixed backup is rejected.
        backup = selected_path.with_name("DKS_Patch.dv2.bak")
        target = self.root / "backup-target"
        target.write_bytes(b"target")
        try:
            backup.symlink_to(target)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"symlink creation unavailable: {error}")
        staged = stage_transaction((replace_plan,))
        with self.assertRaisesRegex(TransactionError, "symlink"):
            save_in_place_transaction(staged)


if __name__ == "__main__":
    unittest.main()
