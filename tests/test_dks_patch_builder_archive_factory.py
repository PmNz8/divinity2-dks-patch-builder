from __future__ import annotations

from dataclasses import FrozenInstanceError
import hashlib
from pathlib import Path
import tempfile
import unittest

from dks_patch_builder import (
    DKS_PATCH_FILE_NAME,
    EmptyDKSPatchResult,
    create_empty_dks_patch,
)
from dks_patch_builder.dv2lib import BLOCK_SIZE, DV2Error


class DKSArchiveFactoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def test_creates_established_dks_patch_and_returns_immutable_report(self) -> None:
        output = self.root / DKS_PATCH_FILE_NAME
        result = create_empty_dks_patch(output)
        self.assertIsInstance(result, EmptyDKSPatchResult)
        self.assertEqual(result.output, output.absolute())
        self.assertEqual(result.size, BLOCK_SIZE)
        self.assertEqual(result.sha256, hashlib.sha256(output.read_bytes()).hexdigest())
        self.assertEqual(result.entry_count, 0)
        self.assertTrue(result.deep_verify)
        self.assertEqual(result.header.version, 5)
        self.assertEqual(result.header.unknown_04, 1)
        self.assertEqual(result.header.unknown_08, 4)
        self.assertEqual(result.header.layout_mode, 0)
        self.assertEqual(result.header.compression_mode, 1)
        self.assertEqual(result.header.data_offset, BLOCK_SIZE)
        self.assertEqual(result.header.path_table_size, 0)
        report = result.report
        self.assertEqual(report["operation"], "create_empty_dks_patch")
        self.assertEqual(report["sha256"], result.sha256)
        self.assertEqual(report["size"], result.size)
        self.assertEqual(report["header"], result.header)
        with self.assertRaises(TypeError):
            report["size"] = 0  # type: ignore[index]
        with self.assertRaises(FrozenInstanceError):
            result.size = 0  # type: ignore[misc]

    def test_filename_check_is_case_insensitive_but_rejects_other_names(self) -> None:
        accepted = self.root / "dks_patch.DV2"
        result = create_empty_dks_patch(accepted)
        self.assertEqual(result.output.name, accepted.name)

        for name in ("Patch.dv2", "DKS_Patch.zip", "DKS_Patch.dv2.bak", "dks_patch"):
            with self.subTest(name=name):
                output = self.root / name
                with self.assertRaises(DV2Error):
                    create_empty_dks_patch(output)
                self.assertFalse(output.exists())

    def test_existing_destination_is_not_overwritten(self) -> None:
        output = self.root / DKS_PATCH_FILE_NAME
        sentinel = b"preserve me"
        output.write_bytes(sentinel)
        with self.assertRaises(DV2Error):
            create_empty_dks_patch(output)
        self.assertEqual(output.read_bytes(), sentinel)


if __name__ == "__main__":
    unittest.main()
