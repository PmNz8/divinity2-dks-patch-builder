# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only
"""Exercise the actual narrative source guard, without game fixtures."""
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from dks_patch_builder import narrative_sources as sources
from tests.synth_builder import build_synthetic


class NarrativeSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'Packed'
        self.root.mkdir()
        self.logical = r'Episodes\Episode_2\Dialogs\Synthetic.xml'
        self.payload = b'synthetic-original'
        self.used = self.root / 'Patch.dv2'
        self.unused = self.root / 'Unused.dv2'
        self.used.write_bytes(build_synthetic([(self.logical, self.payload, 'zlib')], 1))
        self.unused.write_bytes(build_synthetic([(r'Control.bin', b'untouched', 'raw')], 1))
        self.profile = dict(profile_id='synthetic-source-guard', archives=[
            dict(path=p.name, size=p.stat().st_size,
                 sha256=hashlib.sha256(p.read_bytes()).hexdigest(), entries=1)
            for p in (self.used, self.unused)], resources=[dict(logical_path=self.logical,
                occurrences=[dict(archive='Patch.dv2', size=len(self.payload),
                    sha256=hashlib.sha256(self.payload).hexdigest())])])
        guard = patch.object(sources, 'PROFILE', self.profile)
        guard.start()
        self.addCleanup(guard.stop)

    def test_complete_audit_and_full_recheck(self):
        audit = sources.audit_sources(self.root)
        self.assertEqual(len(audit.archives), 2)
        self.assertEqual(audit.payload('patch.dv2', self.logical.lower()), self.payload)
        sources.recheck_sources(audit, full=True)

    def test_unknown_overlay_and_missing_original_rejected(self):
        overlay = self.root / 'DKS_Patch.dv2'
        overlay.write_bytes(build_synthetic([], 1))
        with self.assertRaisesRegex(sources.NarrativeSourceError, 'pristine'):
            sources.audit_sources(self.root)
        overlay.unlink()
        self.unused.unlink()
        with self.assertRaisesRegex(sources.NarrativeSourceError, 'pristine'):
            sources.audit_sources(self.root)

    def test_metadata_drift_rejected(self):
        audit = sources.audit_sources(self.root)
        info = self.unused.stat()
        os.utime(self.unused, ns=(info.st_atime_ns, info.st_mtime_ns + 10_000_000))
        with self.assertRaisesRegex(sources.NarrativeSourceError, 'metadata'):
            sources.recheck_sources(audit)

    def test_used_source_same_metadata_byte_drift_rejected(self):
        audit = sources.audit_sources(self.root)
        info = self.used.stat()
        data = bytearray(self.used.read_bytes())
        data[-1] ^= 1
        self.used.write_bytes(data)
        os.utime(self.used, ns=(info.st_atime_ns, info.st_mtime_ns))
        with self.assertRaisesRegex(sources.NarrativeSourceError, 'bytes changed'):
            sources.recheck_sources(audit)

    def test_fast_recheck_is_not_full_byte_identity_proof(self):
        audit = sources.audit_sources(self.root)
        info = self.unused.stat()
        data = bytearray(self.unused.read_bytes())
        data[-1] ^= 1
        self.unused.write_bytes(data)
        os.utime(self.unused, ns=(info.st_atime_ns, info.st_mtime_ns))
        sources.recheck_sources(audit)
        with self.assertRaisesRegex(sources.NarrativeSourceError, 'bytes changed'):
            sources.recheck_sources(audit, full=True)

    def test_payload_and_occurrence_mismatch_fail_closed(self):
        self.profile['resources'][0]['occurrences'][0]['sha256'] = '0' * 64
        with self.assertRaisesRegex(sources.NarrativeSourceError, 'payload mismatch'):
            sources.audit_sources(self.root)
        self.profile['resources'][0]['occurrences'] = []
        with self.assertRaisesRegex(sources.NarrativeSourceError, 'occurrence set'):
            sources.audit_sources(self.root)

    def test_output_must_be_new_and_outside_packed(self):
        with self.assertRaises(sources.NarrativeSourceError):
            sources.require_external_output(self.root / 'out.dv2', self.root)
        output = Path(self.temp.name) / 'out.dv2'
        self.assertEqual(sources.require_external_output(output, self.root), output)
        output.write_bytes(b'keep')
        with self.assertRaises(sources.NarrativeSourceError):
            sources.require_external_output(output, self.root)
        self.assertEqual(output.read_bytes(), b'keep')
