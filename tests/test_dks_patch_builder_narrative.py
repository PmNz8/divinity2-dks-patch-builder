# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from dks_patch_builder import (
    ASSET_TYPE_NARRATIVE,
    BuilderModelError,
    CompiledBundle,
    DKSPatchBuilderModel,
    NarrativeBundleHandler,
    NarrativeBundleHandlerError,
    parse_asset_package,
)
from dks_patch_builder import model as model_module
from dks_patch_builder.handlers import narrative_bundle as bundle_module
from dks_patch_builder.handlers.narrative_bundle import MAX_BUNDLE_BYTES
from dks_patch_builder.narrative_sources import SourceAudit
from tests.synth_builder import build_synthetic
from tests.test_dks_patch_builder_texture import TexturePackageFixture


TEXT_KEYS = (
    "beata.START",
    "beata.ABOUT.answer",
    "beata.ABOUT.reply",
    "beata.ACCEPT.answer",
    "beata.ACCEPT.reply",
    "beata.WAITING.answer",
    "beata.WAITING.reply",
    "beata.REPORT.answer",
    "beata.REPORT.reply",
    "beata.DONE.answer",
    "beata.DONE.reply",
    "beata.EXIT.answer",
    "beata.EXIT.reply",
    "hansel.REMIND.answer",
    "hansel.REMIND.reply",
    "hansel.REFUSAL.answer",
    "hansel.REFUSAL.reply",
    "hansel.THREAT.answer",
    "hansel.THREAT.reply",
    "hansel.PROMISE.answer",
    "hansel.PROMISE.reply",
    "hansel.SETTLED.answer",
    "hansel.SETTLED.reply",
)
JOURNAL_KEYS = (
    "Accepted.long",
    "Accepted.short",
    "Completed.long",
    "Completed.short",
    "Closed.long",
    "Closed.short",
    "Failed.long",
    "Failed.short",
)


def make_profile() -> dict[str, object]:
    resources = []
    definitions = (
        ("beata", r"A\beata.xml", "SourceA.dv2"),
        ("hansel", r"B\hansel.xml", "SourceB.dv2"),
        ("quests", r"C\quests.xml", "SourceC.dv2"),
        ("events", r"D\events.xml", "SourceD.dv2"),
        ("seed", r"Win32\Seed.dsg", "SourceE.dv2"),
    )
    for role, logical_path, source_archive in definitions:
        original = f"original-{role}".encode("ascii")
        resources.append(
            {
                "role": role,
                "logical_path": logical_path,
                "source_archive": source_archive,
                "source_sha256": hashlib.sha256(original).hexdigest(),
                "source_size": len(original),
                "occurrences": (),
            }
        )
    return {
        "profile_id": "synthetic-narrative-profile",
        "deployment": "synthetic-new-fov",
        "archives": (),
        "resources": resources,
    }


SYNTH_PROFILE = make_profile()


def make_config() -> dict[str, object]:
    return {
        "schema": "divinity2.debt_template_config.v1",
        "key": "Synthetic_Key",
        "title": "Synthetic Quest",
        "secret": "A printable secret.",
        "texts": {key: f"text {index}" for index, key in enumerate(TEXT_KEYS)},
        "journal": {key: f"journal {index}" for index, key in enumerate(JOURNAL_KEYS)},
    }


def write_bundle(root: Path, *, mutate: str | None = None) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    config = make_config()
    config_data = (json.dumps(config, sort_keys=True, indent=2) + "\n").encode("utf-8")
    payloads = {
        row["role"]: f"compiled-{row['role']}".encode("ascii")
        for row in SYNTH_PROFILE["resources"]
    }
    resources = []
    for row in SYNTH_PROFILE["resources"]:
        role = row["role"]
        payload = payloads[role]
        resources.append(
            {
                "role": role,
                "file": f"{role}.bin",
                "logical_path": row["logical_path"],
                "sha256": hashlib.sha256(payload).hexdigest(),
                "size": len(payload),
                "source_archive": row["source_archive"],
                "source_sha256": row["source_sha256"],
                "source_size": row["source_size"],
            }
        )
    anchor = SYNTH_PROFILE["resources"][-1]["logical_path"]
    bundle = {
        "schema": "divinity2.narrative_bundle",
        "schema_version": 1,
        "asset_type": ASSET_TYPE_NARRATIVE,
        "profile_id": SYNTH_PROFILE["profile_id"],
        "deployment": SYNTH_PROFILE["deployment"],
        "compiler": "quest-author-fov-debt-v1",
        "quest_key": config["key"],
        "quest_title": config["title"],
        "config_file": "quest.json",
        "config_sha256": hashlib.sha256(config_data).hexdigest(),
        "resources": resources,
    }
    bundle_data = (json.dumps(bundle, sort_keys=True, indent=2) + "\n").encode("utf-8")
    asset = {
        "schema": "divinity2.dks_asset_package",
        "schema_version": 1,
        "asset_type": ASSET_TYPE_NARRATIVE,
        "template": {
            "file": "bundle.json",
            "logical_path": anchor,
            "payload_sha256": hashlib.sha256(bundle_data).hexdigest(),
            "payload_size": len(bundle_data),
        },
        "target_logical_path": anchor,
    }
    if mutate == "asset_path":
        asset["target_logical_path"] = r"..\unsafe"
    if mutate == "schema":
        bundle["schema"] = "wrong.schema"
        bundle_data = (json.dumps(bundle, sort_keys=True, indent=2) + "\n").encode("utf-8")
        asset["template"]["payload_sha256"] = hashlib.sha256(bundle_data).hexdigest()
        asset["template"]["payload_size"] = len(bundle_data)
    if mutate == "duplicate_bundle_key":
        bundle_data = b'{"schema":"divinity2.narrative_bundle","schema":"duplicate"}'
        asset["template"]["payload_sha256"] = hashlib.sha256(bundle_data).hexdigest()
        asset["template"]["payload_size"] = len(bundle_data)
    if mutate == "resource_hash":
        bundle["resources"][0]["sha256"] = "0" * 64
        bundle_data = (json.dumps(bundle, sort_keys=True, indent=2) + "\n").encode("utf-8")
        asset["template"]["payload_sha256"] = hashlib.sha256(bundle_data).hexdigest()
        asset["template"]["payload_size"] = len(bundle_data)
    if mutate == "resource_duplicate":
        bundle["resources"][1]["role"] = bundle["resources"][0]["role"]
        bundle_data = (json.dumps(bundle, sort_keys=True, indent=2) + "\n").encode("utf-8")
        asset["template"]["payload_sha256"] = hashlib.sha256(bundle_data).hexdigest()
        asset["template"]["payload_size"] = len(bundle_data)

    (root / "asset.json").write_text(json.dumps(asset, sort_keys=True), encoding="utf-8")
    (root / "bundle.json").write_bytes(bundle_data)
    (root / "quest.json").write_bytes(config_data)
    for role, payload in payloads.items():
        (root / f"{role}.bin").write_bytes(payload)
    return root


class NarrativeBuilderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.packed = self.root / "Packed"
        self.packed.mkdir()
        (self.packed / "Patch.dv2").write_bytes(build_synthetic([], 1))
        self.external = self.root / "external" / "DKS_Patch.dv2"
        self.external.parent.mkdir()
        self.external.write_bytes(build_synthetic([], 1))
        self.package = write_bundle(self.root / "bundle")
        self.profile_patches = (
            patch.object(bundle_module, "PROFILE", SYNTH_PROFILE),
            patch.object(model_module, "PROFILE", SYNTH_PROFILE),
        )
        for item in self.profile_patches:
            item.start()
            self.addCleanup(item.stop)
        self.audit = SourceAudit(self.packed, (), (), SYNTH_PROFILE["profile_id"])
        self.audit_mock = patch.object(model_module, "audit_sources", return_value=self.audit)
        self.recheck_patch = patch.object(model_module, "recheck_sources")
        self.audit_mock.start()
        self.recheck_mock = self.recheck_patch.start()
        self.addCleanup(self.audit_mock.stop)
        self.addCleanup(self.recheck_patch.stop)

    def open_model(self, dks: Path | None = None) -> DKSPatchBuilderModel:
        model = DKSPatchBuilderModel()
        selected = dks or self.external
        expected_count = len(tuple(self.packed.rglob("*.dv2")))
        model.open_archive(self.packed, selected, expected_count=expected_count)
        return model

    def test_handler_validates_bundle_and_builds_five_zlib_resources(self) -> None:
        package = parse_asset_package(self.package)
        bundle = NarrativeBundleHandler().compile(package)
        self.assertEqual(bundle.asset_type, ASSET_TYPE_NARRATIVE)
        self.assertEqual(bundle.profile_id, SYNTH_PROFILE["profile_id"])
        self.assertEqual(len(bundle.resources), 5)
        self.assertEqual([row.target_logical_path for row in bundle.resources], [row["logical_path"] for row in SYNTH_PROFILE["resources"]])
        self.assertTrue(all(row.preferred_storage_mode == "zlib" for row in bundle.resources))
        self.assertIn("new FoV only", bundle.warnings)
        self.assertIn("no in-place quest upgrades", bundle.warnings)

    def test_handler_rejects_malformed_manifest_hash_duplicate_and_schema(self) -> None:
        for mutation in ("duplicate_bundle_key", "resource_hash", "resource_duplicate", "schema"):
            with self.subTest(mutation=mutation):
                root = write_bundle(self.root / mutation, mutate=mutation)
                package = parse_asset_package(root)
                with self.assertRaises(NarrativeBundleHandlerError):
                    NarrativeBundleHandler().compile(package)

    def test_handler_rejects_extra_member_and_unsafe_asset_path(self) -> None:
        extra = write_bundle(self.root / "extra")
        (extra / "unexpected.bin").write_bytes(b"extra")
        with self.assertRaises(NarrativeBundleHandlerError):
            NarrativeBundleHandler().compile(parse_asset_package(extra))

        unsafe = write_bundle(self.root / "unsafe", mutate="asset_path")
        with self.assertRaises(ValueError):
            parse_asset_package(unsafe)

    def test_handler_rejects_oversized_manifest_and_directory_member(self) -> None:
        oversized = write_bundle(self.root / "oversized")
        manifest = b" " * (MAX_BUNDLE_BYTES + 1)
        (oversized / "bundle.json").write_bytes(manifest)
        asset_path = oversized / "asset.json"
        asset = json.loads(asset_path.read_text(encoding="utf-8"))
        asset["template"]["payload_sha256"] = hashlib.sha256(manifest).hexdigest()
        asset["template"]["payload_size"] = len(manifest)
        asset_path.write_text(json.dumps(asset), encoding="utf-8")
        with self.assertRaises(NarrativeBundleHandlerError):
            NarrativeBundleHandler().compile(parse_asset_package(oversized))

        directory_member = write_bundle(self.root / "directory-member")
        (directory_member / "beata.bin").unlink()
        (directory_member / "beata.bin").mkdir()
        with self.assertRaises(NarrativeBundleHandlerError):
            NarrativeBundleHandler().compile(parse_asset_package(directory_member))

    def test_narrative_import_is_atomic_and_cancels_as_one_group(self) -> None:
        model = self.open_model()
        rows = model.import_package(self.package)
        self.assertIsInstance(rows, tuple)
        self.assertEqual(len(rows), 5)
        self.assertEqual(len(model.pending_changes()), 5)
        self.assertIn("new FoV only", rows[0].warnings)
        self.assertIn("no new runtime acceptance", rows[0].warnings)
        cancelled = model.cancel(rows[2].target_logical_path)
        self.assertIsInstance(cancelled, tuple)
        self.assertEqual(len(cancelled), 5)
        self.assertEqual(model.pending_changes(), ())
        self.assertIsNone(model._narrative_audit)

        broken = write_bundle(self.root / "broken", mutate="resource_hash")
        with self.assertRaises(BuilderModelError):
            model.import_package(broken)
        self.assertEqual(model.pending_changes(), ())

    def test_model_rejects_wrong_bundle_profile_or_target_identity(self) -> None:
        package = parse_asset_package(self.package)
        compiled = NarrativeBundleHandler().compile(package)

        class StubRegistry:
            def __init__(self, result: CompiledBundle) -> None:
                self.result = result

            def compile(self, _package: object) -> CompiledBundle:
                return self.result

        for bad in (
            replace(compiled, profile_id="wrong-profile"),
            replace(
                compiled,
                resources=(
                    replace(compiled.resources[0], target_logical_path=r"Wrong\Target.bin"),
                    *compiled.resources[1:],
                ),
            ),
        ):
            with self.subTest(bad=bad):
                model = DKSPatchBuilderModel(registry=StubRegistry(bad))
                model.open_archive(self.packed, self.external, expected_count=1)
                with self.assertRaisesRegex(BuilderModelError, "profile|frozen target"):
                    model.import_package(self.package)
                self.assertEqual(model.pending_changes(), ())

    def test_narrative_requires_external_empty_dks_and_blocks_mixed_or_removal(self) -> None:
        inside = self.packed / "DKS_Patch.dv2"
        inside.write_bytes(build_synthetic([], 1))
        model = self.open_model(inside)
        with self.assertRaisesRegex(BuilderModelError, "external"):
            model.import_package(self.package)

        model = self.open_model()
        with self.assertRaisesRegex(BuilderModelError, "recognized narrative targets"):
            model.remove_override(SYNTH_PROFILE["resources"][0]["logical_path"])

        model.import_package(self.package)
        with self.assertRaisesRegex(BuilderModelError, "individual removals"):
            model.remove_override(r"Unrelated\Path.bin")

    def test_source_recheck_blocks_save_and_output_inside_packed(self) -> None:
        model = self.open_model()
        model.import_package(self.package)
        self.recheck_mock.side_effect = ValueError("stale source")
        (self.root / "out").mkdir()
        with self.assertRaisesRegex(BuilderModelError, "cannot save"):
            model.save_as(self.root / "out" / "DKS_Patch.dv2")
        self.assertEqual(len(model.pending_changes()), 5)

        self.recheck_mock.side_effect = None
        with self.assertRaisesRegex(BuilderModelError, "outside every Packed"):
            model.save_as(self.packed / "out" / "DKS_Patch.dv2")
        self.assertEqual(len(model.pending_changes()), 5)

        with self.assertRaisesRegex(BuilderModelError, "outside every Packed"):
            model.save_as(self.root / "external. " / "DKS_Patch.dv2")
        self.assertEqual(len(model.pending_changes()), 5)

    def test_successful_external_save_resets_group(self) -> None:
        model = self.open_model()
        model.import_package(self.package)
        output = self.root / "published" / "DKS_Patch.dv2"
        output.parent.mkdir()
        outcome = model.save_as(output)
        self.assertTrue(outcome.selected_output)
        self.assertFalse(model.has_pending_changes)
        self.assertIsNone(model._narrative_audit)
        self.assertEqual(len(model.pending_changes()), 0)

    def test_saved_narrative_archive_accepts_texture_without_changing_quest_resources(self) -> None:
        fixture = TexturePackageFixture(self.root / "texture-package")
        texture_path = r"Win32\Textures\Dragon_A_DM.nif"
        (self.packed / "Patch.dv2").write_bytes(
            build_synthetic([(texture_path, fixture.template_payload, "zlib")], 1)
        )
        model = self.open_model()
        model.import_package(self.package)
        model.save_in_place()
        from dks_patch_builder.dv2lib import DV2Session
        before = DV2Session(self.external)
        narrative = {entry.path: before.read_entry_bytes(entry.path) for entry in before.entries}
        for reopened in (False, True):
            with self.subTest(reopened=reopened):
                if reopened:
                    model = self.open_model()
                model.import_package(fixture.root)
                self.assertEqual(len(model.pending_changes()), 1)
                model.save_in_place()
                self.assertEqual(model.pending_changes(), ())
                after = DV2Session(self.external)
                self.assertEqual(len(after.entries), 6)
                for path, payload in narrative.items():
                    self.assertEqual(after.read_entry_bytes(path), payload)
                self.assertEqual(after.read_entry_bytes(texture_path), fixture.template_payload)


if __name__ == "__main__":
    unittest.main()
