# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only
"""Offline model import safety and existing transaction integration."""
import io
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from dks_patch_builder.model import DKSPatchBuilderModel, BuilderModelError
from dks_patch_builder.controller import BuilderController
from dks_patch_builder.inventory import scan_packed, find_occurrences
from dks_patch_builder.model_packages.reader import read_model_package, ModelPackageError
from tests.synth_builder import build_synthetic
from tests.model_fixtures import triangle, package_bytes

LOGICAL = r'Win32\triangle.nif'


def rewrite(raw, edit):
    output = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(raw)) as source, zipfile.ZipFile(output, 'w') as target:
        for name in source.namelist():
            value = source.read(name)
            if name == 'manifest.json':
                manifest = json.loads(value)
                edit(manifest)
                value = json.dumps(manifest).encode()
            target.writestr(name, value)
    return output.getvalue()


class ModelPackagesTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.packed = self.root / 'Packed'
        self.packed.mkdir()
        self.source = self.packed / 'Models.dv2'
        self.original = build_synthetic([(LOGICAL, triangle(), 'zlib')], 1)
        self.source.write_bytes(self.original)
        (self.packed / 'Patch.dv2').write_bytes(build_synthetic([('Global\\baseline.bin', b'baseline', 'raw')], 1))
        self.package = self.root / 'edited.d2model'
        self.raw, self.current = package_bytes(self.original)
        self.package.write_bytes(self.raw)
        self.dks = self.root / 'DKS_Patch.dv2'
        self.dks.write_bytes(build_synthetic([('Global\\control.bin', b'control', 'raw')], 1))
        self.before = self.dks.read_bytes()
        self.model = DKSPatchBuilderModel()
        self.model.open_archive(self.packed, self.dks)

    def test_changed_native_exact_bytes_only_then_transaction(self):
        summary = self.model.import_model_package(self.package)
        self.assertEqual(summary['queued_count'], 1)
        json.dumps(BuilderController._jsonify(summary))
        row, = self.model.pending_changes()
        self.assertEqual(row.asset_type, 'model.d2model')
        self.assertEqual(row.action, 'ADD_OVERRIDE')
        self.assertEqual(self.dks.read_bytes(), self.before)
        outcome = self.model.save_in_place()
        self.assertTrue(outcome.selected_output)
        self.assertFalse(self.model.has_pending_changes)
        self.assertEqual(self.source.read_bytes(), self.original)
        # Inspect output via an independent directory inventory, not model cache.
        check_root = self.root / 'output-check'
        check_root.mkdir()
        (check_root / 'Patch.dv2').write_bytes(self.dks.read_bytes())
        output = scan_packed(check_root)
        model = find_occurrences(output, LOGICAL)
        self.assertEqual(model[0].logical_sha256, summary['resources'][0]['sha256'])
        control, = find_occurrences(output, r'Global\control.bin')
        import hashlib
        self.assertEqual(control.logical_sha256, hashlib.sha256(b'control').hexdigest())

    def test_original_v1_is_noop(self):
        self.package.write_bytes(package_bytes(self.original, edited=False)[0])
        result = self.model.import_model_package(self.package)
        self.assertEqual(result['queued_count'], 0)
        self.assertFalse(self.model.has_pending_changes)
        self.assertEqual(self.dks.read_bytes(), self.before)

    def test_conflict_does_not_partially_mutate_queue(self):
        self.model.import_model_package(self.package)
        before = self.model.pending_changes()
        with self.assertRaisesRegex(BuilderModelError, 'overlaps'):
            self.model.import_model_package(self.package)
        self.assertEqual(self.model.pending_changes(), before)

    def test_cancel_clears_group_and_allows_reimport(self):
        self.model.import_model_package(self.package)
        self.assertEqual(len(self.model.cancel(LOGICAL.upper())), 1)
        self.assertFalse(self.model._model_imports.active)
        self.model.import_model_package(self.package)
        self.model.clear_pending()
        self.assertFalse(self.model._model_imports.active)

    def test_import_is_immutable_snapshot(self):
        self.model.import_model_package(self.package)
        self.package.write_bytes(b'invalid later edit')
        self.model.save_in_place()
        self.assertNotEqual(self.dks.read_bytes(), self.before)

    def test_source_archive_identity_mismatch(self):
        self.package.write_bytes(rewrite(self.raw, lambda m: m['resources'][0].update(archive_sha256='0'*64)))
        with self.assertRaisesRegex(BuilderModelError, 'differs'):
            self.model.import_model_package(self.package)
        self.assertFalse(self.model.has_pending_changes)

    def test_missing_recorded_source(self):
        self.package.write_bytes(rewrite(self.raw, lambda m: m['resources'][0].update(archive_name='Absent.dv2')))
        with self.assertRaisesRegex(BuilderModelError, 'Missing/ambiguous'):
            self.model.import_model_package(self.package)

    def test_duplicate_different_payload_in_root_patch_warns_and_saves(self):
        (self.packed / 'Patch.dv2').write_bytes(build_synthetic([(LOGICAL, b'different', 'raw')], 1))
        self.model.open_archive(self.packed, self.dks)
        duplicate = (self.packed / 'Patch.dv2').read_bytes()
        summary = self.model.import_model_package(self.package)
        self.assertTrue(any('Different same-path source variants' in w for w in summary['warnings']))
        self.assertTrue(any('Different same-path source variants' in w
                            for w in self.model._model_imports.warnings_for(LOGICAL)))
        self.assertEqual(self.dks.read_bytes(), self.before)
        self.model.save_in_place()
        from dks_patch_builder.dv2lib import DV2Session
        output = DV2Session(self.dks)
        expected = read_model_package(self.package).changed[0].compiled.compiled_payload
        self.assertEqual(output.read_entry_bytes(LOGICAL), expected)
        self.assertEqual(self.source.read_bytes(), self.original)
        self.assertEqual((self.packed / 'Patch.dv2').read_bytes(), duplicate)

    def test_warned_variant_drift_still_rejected(self):
        duplicate = self.packed / 'Patch.dv2'
        duplicate.write_bytes(build_synthetic([(LOGICAL, b'different', 'raw')], 1))
        self.model.open_archive(self.packed, self.dks)
        self.model.import_model_package(self.package)
        duplicate.write_bytes(build_synthetic([(LOGICAL, b'changed!', 'raw')], 1))
        with self.assertRaises(BuilderModelError):
            self.model.save_in_place()
        self.assertEqual(self.dks.read_bytes(), self.before)
        self.assertTrue(self.model.has_pending_changes)

    def test_identical_duplicate_allowed(self):
        (self.packed / 'Patch.dv2').write_bytes(self.original)
        self.model.open_archive(self.packed, self.dks)
        self.model.import_model_package(self.package)
        self.model.save_in_place()

    def test_source_drift_before_save_keeps_queue_and_output(self):
        self.model.import_model_package(self.package)
        self.source.write_bytes(self.original + b'changed')
        with self.assertRaises(BuilderModelError):
            self.model.save_in_place()
        self.assertEqual(self.dks.read_bytes(), self.before)
        self.assertTrue(self.model.has_pending_changes)

    def test_new_archive_before_save_rejected(self):
        self.model.import_model_package(self.package)
        (self.packed / 'Additional.dv2').write_bytes(self.original)
        with self.assertRaises(BuilderModelError):
            self.model.save_in_place()
        self.assertEqual(self.dks.read_bytes(), self.before)

    def test_destination_inside_packed_rejected(self):
        internal = self.packed / 'DKS_Patch.dv2'
        internal.write_bytes(self.before)
        self.model.open_archive(self.packed, internal)
        with self.assertRaisesRegex(BuilderModelError, 'outside Packed'):
            self.model.import_model_package(self.package)
        self.assertEqual(internal.read_bytes(), self.before)

    def test_save_as_inside_packed_rejected(self):
        self.model.import_model_package(self.package)
        output = self.packed / 'DKS_Patch.dv2'
        with self.assertRaisesRegex(BuilderModelError, 'outside Packed'):
            self.model.save_as(output)
        self.assertFalse(output.exists())

    def test_external_save_as(self):
        self.model.import_model_package(self.package)
        folder = self.root / 'copy'
        folder.mkdir()
        output = folder / 'DKS_Patch.dv2'
        self.model.save_as(output)
        self.assertTrue(output.exists())
        self.assertEqual(self.dks.read_bytes(), self.before)

    def test_controller_cancellation_and_failure_json_safe(self):
        controller = BuilderController(self.model)
        self.assertTrue(controller.import_model_package(None)['cancelled'])
        self.package.write_bytes(b'bad')
        result = controller.import_model_package(str(self.package))
        self.assertFalse(result['ok'])
        json.dumps(result)
        self.assertFalse(self.model.has_pending_changes)

    def test_tampered_manifest_and_replayed_assembly_rejected(self):
        edits = [lambda m: m.update(schema='unsupported'),
                 lambda m: m['resources'][0].update(sha256='0'*64),
                 lambda m: m['assembly']['components'][0].update(vertices=99),
                 lambda m: m['assembly']['recipe'].update(components=[False]),
                 lambda m: m.update(assembly=None),
                 lambda m: m['resources'][0].update(archive_name='../escape.dv2')]
        for edit in edits:
            with self.subTest(edit=edit):
                self.package.write_bytes(rewrite(self.raw, edit))
                with self.assertRaises(ModelPackageError):
                    read_model_package(self.package)

    def test_plan_failure_leaves_queue_unchanged(self):
        with patch('dks_patch_builder.model_packages.integration.plan_compiled_resource', side_effect=ValueError('plan failure')):
            with self.assertRaisesRegex(BuilderModelError, 'plan failure'):
                self.model.import_model_package(self.package)
        self.assertFalse(self.model.has_pending_changes)
        self.assertFalse(self.model._model_imports.active)

    def multi(self, *, normal=False, changed_texture=True):
        from tests.model_fixtures import textured_triangle, multi_package
        from tests.texture_fixtures import _make_texture
        model, texture = textured_triangle(normal=normal), _make_texture(4)
        archive = build_synthetic([(LOGICAL,model,'zlib'), (r'Win32\texture.nif',texture,'zlib')],1)
        self.source.write_bytes(archive)
        self.package.write_bytes(multi_package(archive,model,texture,changed_texture=changed_texture))
        self.model.open_archive(self.packed, self.dks)

    def test_multi_resource_cancel_preserves_unrelated_pending(self):
        self.multi()
        self.model.remove_override(r'Global\control.bin')
        report = self.model.import_model_package(self.package)
        self.assertEqual(report['queued_count'], 2)
        self.assertEqual(len(self.model.pending_changes()), 3)
        self.assertEqual(len(self.model.cancel(r'Win32\texture.nif')), 2)
        self.assertEqual(len(self.model.pending_changes()), 1)
        self.assertEqual(self.model.pending_changes()[0].action, 'REMOVE_OVERRIDE')

    def test_multi_resource_second_plan_failure_is_atomic(self):
        self.multi()
        from dks_patch_builder.model_packages.integration import plan_compiled_resource
        count = 0
        def fail_second(*args):
            nonlocal count
            count += 1
            if count == 2:
                raise ValueError('second plan rejected')
            return plan_compiled_resource(*args)
        self.model.remove_override(r'Global\control.bin')
        before = self.model.pending_changes()
        with patch('dks_patch_builder.model_packages.integration.plan_compiled_resource', side_effect=fail_second):
            with self.assertRaisesRegex(BuilderModelError, 'second plan'):
                self.model.import_model_package(self.package)
        self.assertEqual(before, self.model.pending_changes())
        self.assertFalse(self.model._model_imports.active)

    def test_multi_material_texture_exact_save(self):
        self.multi()
        expected = read_model_package(self.package)
        self.model.import_model_package(self.package)
        self.model.save_in_place()
        from dks_patch_builder.dv2lib import DV2Session
        output = DV2Session(self.dks)
        self.assertEqual(len(output.entries), 3)
        for resource in expected.changed:
            self.assertEqual(output.read_entry_bytes(resource.logical_path), resource.compiled.compiled_payload)

    def test_normal_pixels_rejected_but_unchanged_normal_allowed(self):
        self.multi(normal=True)
        with self.assertRaisesRegex(ModelPackageError, 'Normal-map pixel'):
            read_model_package(self.package)
        self.multi(normal=True, changed_texture=False)
        self.assertEqual(self.model.import_model_package(self.package)['queued_count'],1)

    def test_unchanged_dependency_still_requires_exact_source(self):
        self.multi(changed_texture=False)
        self.package.write_bytes(rewrite(self.package.read_bytes(), lambda m: next(
            row for row in m['resources'] if row['logical_path'].endswith('texture.nif')).update(archive_sha256='0'*64)))
        with self.assertRaisesRegex(BuilderModelError, 'differs'):
            self.model.import_model_package(self.package)
        self.assertFalse(self.model.has_pending_changes)

    def test_disjoint_texture_import_and_model_group(self):
        from tests.test_dks_patch_builder_texture import TexturePackageFixture
        fixture = TexturePackageFixture(self.root / 'texture-package')
        (self.packed / 'Textures.dv2').write_bytes(build_synthetic([
            (r'Win32\Textures\Dragon_A_DM.nif', fixture.template_payload, 'zlib')], 1))
        self.model.open_archive(self.packed, self.dks)
        self.model.import_package(fixture.root)
        self.model.import_model_package(self.package)
        self.assertEqual(len(self.model.pending_changes()), 2)
        self.model.save_in_place()
        self.assertEqual(len(self.model.list_entries()), 3)

    def test_model_gui_file_dialog_real_controller(self):
        from tests.test_dks_patch_builder_desktop import _make_app
        app, root, dialogs, _, _ = _make_app(BuilderController(self.model),
            dialog_values={'askopenfilename': [str(self.package), '', str(self.root/'absent.d2model')]})
        app.request_import_model()
        root.run_all()
        self.assertEqual(app._snapshot['pending_count'], 1, app.report_text.text)
        queued = list(app.pending)
        app.request_import_model()
        root.run_all()
        self.assertEqual(app.pending, queued)
        app.request_import_model()
        root.run_all()
        self.assertEqual(app.pending, queued)
        self.assertEqual(self.dks.read_bytes(), self.before)

    def test_protected_native_edit_rejected_even_with_correct_hash(self):
        from dks_patch_builder.model_packages._core.nif import parse, geometry
        import struct
        with zipfile.ZipFile(io.BytesIO(self.raw)) as source:
            files = {name: source.read(name) for name in source.namelist()}
        manifest = json.loads(files['manifest.json'])
        row = manifest['resources'][0]
        payload = bytearray(files.pop(row['member']))
        geo = geometry(parse(payload), 1)
        # Keep every source/header/size intact but reverse a protected triangle.
        struct.pack_into('<3H', payload, geo['uv_start'] + 13, 0, 2, 1)
        sha = hashlib.sha256(payload).hexdigest()
        row.update(sha256=sha, member='resources/' + sha + '.bin')
        files[row['member']] = bytes(payload)
        files['manifest.json'] = json.dumps(manifest).encode()
        output = io.BytesIO()
        with zipfile.ZipFile(output, 'w') as target:
            for name, value in files.items():
                target.writestr(name, value)
        self.package.write_bytes(output.getvalue())
        with self.assertRaises(ModelPackageError):
            read_model_package(self.package)

    def test_unbound_extra_resource_rejected(self):
        from dks_patch_builder.model_packages._core.package import Source, build, verify
        manifest = verify(self.raw)
        sources = [Source('Win32/triangle.nif', 'Models.dv2', hashlib.sha256(self.original).hexdigest(),
                          self.current, original_payload=triangle()),
                   Source('Win32/unbound.nif', 'Models.dv2', '0'*64, triangle())]
        self.package.write_bytes(build(sources, 'Win32/triangle.nif', assembly=manifest['assembly']))
        with self.assertRaisesRegex(ModelPackageError, 'Unbound resource'):
            read_model_package(self.package)

    def test_model_group_rechecked_before_transaction(self):
        self.multi()
        self.model.import_model_package(self.package)
        self.model._pending.pop(r'win32\texture.nif')
        with self.assertRaisesRegex(BuilderModelError, 'Incomplete'):
            self.model.save_in_place()
        self.assertEqual(self.dks.read_bytes(), self.before)

    def test_failed_transaction_keeps_whole_group_pending(self):
        self.multi()
        self.model.import_model_package(self.package)
        before = self.model.pending_changes()
        with patch('dks_patch_builder.model.save_in_place_transaction', side_effect=ValueError('transaction failed')):
            with self.assertRaisesRegex(BuilderModelError, 'transaction failed'):
                self.model.save_in_place()
        self.assertEqual(self.model.pending_changes(), before)
        self.assertTrue(self.model._model_imports.active)
        self.assertEqual(self.dks.read_bytes(), self.before)

    def test_v2_original_noop_and_source_reset(self):
        from dks_patch_builder.model_packages._core.package import Source
        from dks_patch_builder.model_packages._core.controller import Preview
        from dks_patch_builder.model_packages._core.replay import PackageCorpus
        source = Source('Win32/triangle.nif','Models.dv2',hashlib.sha256(self.original).hexdigest(),
                        triangle(),original_payload=triangle())
        preview = Preview(PackageCorpus([source]))
        preview.open_model(source)
        self.package.write_bytes(preview.package())
        self.assertEqual(self.model.import_model_package(self.package)['queued_count'], 0)
        self.package.write_bytes(self.raw)
        self.model.import_model_package(self.package)
        self.model.close(discard_pending=True)
        self.assertFalse(self.model._model_imports.active)

    def test_narrative_exclusivity_retained(self):
        self.model._narrative_group_keys = frozenset({'sentinel'})
        with self.assertRaisesRegex(BuilderModelError, 'narrative bundle'):
            self.model.import_model_package(self.package)
        self.assertFalse(self.model._model_imports.active)
