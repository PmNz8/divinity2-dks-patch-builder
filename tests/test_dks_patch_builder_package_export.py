# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

from dataclasses import FrozenInstanceError
import json
from pathlib import Path
import tempfile
import unittest

from dks_patch_builder import (
    PackageExportError,
    build_texture_asset_package_files,
    default_registry,
    parse_asset_package,
)
from tests.texture_fixtures import _make_texture
from dks_patch_builder.codec import bc
from dks_patch_builder.codec.nif_texture import parse_texture_resource


SOURCE = r"Win32\Textures\Source_DM.nif"
TARGET = r"Win32\Textures\Modded_DM.nif"


def materialize(root: Path, files: object) -> None:
    for relative_name, payload in files.items():
        destination = root / Path(*relative_name.split("/"))
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)


class TexturePackageExportTests(unittest.TestCase):
    def test_all_formats_build_deterministic_compilable_noop_packages(self) -> None:
        for pixel_format in (bc.FORMAT_BC1, bc.FORMAT_BC2, bc.FORMAT_BC3):
            with self.subTest(pixel_format=pixel_format), tempfile.TemporaryDirectory() as temporary:
                payload = _make_texture(pixel_format)
                resource = parse_texture_resource(payload, SOURCE)
                first = build_texture_asset_package_files(resource, SOURCE)
                second = build_texture_asset_package_files(resource, SOURCE)
                self.assertEqual(dict(first.files), dict(second.files))
                self.assertEqual(first.template_sha256, resource.payload_sha256)
                self.assertEqual(first.template_size, len(payload))
                root = Path(temporary) / "package"
                materialize(root, first.files)
                package = parse_asset_package(root)
                compiled = default_registry().compile(package)
                self.assertEqual(compiled.compiled_payload, payload)
                self.assertFalse(compiled.payload_changed)

    def test_target_path_is_independently_editable_in_outer_sidecar(self) -> None:
        payload = _make_texture(bc.FORMAT_BC3)
        resource = parse_texture_resource(payload, SOURCE)
        result = build_texture_asset_package_files(
            resource,
            SOURCE,
            target_logical_path=TARGET,
        )
        document = json.loads(result.files["asset.json"].decode("utf-8"))
        self.assertEqual(document["template"]["logical_path"], SOURCE)
        self.assertEqual(document["target_logical_path"], TARGET)
        self.assertEqual(result.target_logical_path, TARGET)

    def test_unsafe_or_non_nif_paths_fail_before_returning_files(self) -> None:
        resource = parse_texture_resource(_make_texture(bc.FORMAT_BC1), SOURCE)
        for path in (r"..\escape.nif", r"Win32\Textures\bad.png", ""):
            with self.subTest(path=path), self.assertRaises(PackageExportError):
                build_texture_asset_package_files(resource, path)

    def test_result_and_file_mapping_are_immutable(self) -> None:
        resource = parse_texture_resource(_make_texture(bc.FORMAT_BC1), SOURCE)
        result = build_texture_asset_package_files(resource, SOURCE)
        with self.assertRaises(TypeError):
            result.files["extra"] = b"bad"  # type: ignore[index]
        with self.assertRaises(FrozenInstanceError):
            result.template_size = 0  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
