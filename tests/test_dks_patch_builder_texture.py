# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

from dataclasses import FrozenInstanceError
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from dks_patch_builder import (
    ASSET_SCHEMA,
    ASSET_SCHEMA_VERSION,
    ASSET_TYPE_NARRATIVE,
    ASSET_TYPE_TEXTURE_NIF,
    AssetPackageError,
    MAX_ASSET_JSON_BYTES,
    TextureNIFHandler,
    TextureNIFHandlerError,
    default_registry,
    parse_asset_package,
)
from dks_patch_builder.handlers.base import UnsupportedAssetTypeError
from tests.test_texture_roundtrip import (
    _bc1_block,
    _bc2_block,
    _bc3_block,
    _resource,
)
from dks_patch_builder.codec import bc
from dks_patch_builder.codec.png import encode_png_rgb
from dks_patch_builder.codec.roundtrip import build_export_set, decode_mip_views


def _canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode(
        "utf-8"
    )


class TexturePackageFixture:
    def __init__(self, root: Path, pixel_format: int = bc.FORMAT_BC1) -> None:
        self.root = root
        self.texture_directory = root / "texture"
        self.texture_directory.mkdir(parents=True)
        if pixel_format == bc.FORMAT_BC1:
            data = _bc1_block(0xF800, 0x07E0)
        elif pixel_format == bc.FORMAT_BC2:
            data = _bc2_block(bytes(range(8)))
        elif pixel_format == bc.FORMAT_BC3:
            data = _bc3_block(alpha_indices=0x123456789ABC)
        else:  # pragma: no cover - fixture misuse
            raise AssertionError(f"unsupported fixture format {pixel_format}")
        self.resource = _resource(pixel_format, data)
        self.template_payload = self.resource._payload
        self.template_path = root / "template.nif"
        self.template_path.write_bytes(self.template_payload)
        for name, payload in build_export_set(self.resource).items():
            (self.texture_directory / name).write_bytes(payload)
        self.write_asset()

    def asset_document(
        self,
        *,
        asset_type: str = ASSET_TYPE_TEXTURE_NIF,
        template_file: str = "template.nif",
        template_logical_path: str = r"Win32\Textures\Dragon_A_DM.nif",
        target_logical_path: str = r"Win32\Textures\Dragon_A_DM.nif",
    ) -> dict[str, object]:
        return {
            "schema": ASSET_SCHEMA,
            "schema_version": ASSET_SCHEMA_VERSION,
            "asset_type": asset_type,
            "template": {
                "file": template_file,
                "logical_path": template_logical_path,
                "payload_sha256": hashlib.sha256(self.template_payload).hexdigest(),
                "payload_size": len(self.template_payload),
            },
            "target_logical_path": target_logical_path,
        }

    def write_asset(self, **kwargs: object) -> None:
        document = self.asset_document(**kwargs)
        (self.root / "asset.json").write_bytes(_canonical_json(document))


class TextureNIFPackageTests(unittest.TestCase):
    def make_fixture(self, pixel_format: int = bc.FORMAT_BC1) -> tuple[tempfile.TemporaryDirectory[str], TexturePackageFixture]:
        temporary = tempfile.TemporaryDirectory()
        return temporary, TexturePackageFixture(Path(temporary.name) / "package", pixel_format)

    def compile_fixture(self, fixture: TexturePackageFixture):
        package = parse_asset_package(fixture.root)
        return TextureNIFHandler().compile(package)

    def test_valid_unchanged_package_is_byte_perfect(self) -> None:
        temporary, fixture = self.make_fixture()
        try:
            result = self.compile_fixture(fixture)
            self.assertEqual(result.template_logical_path, r"Win32\Textures\Dragon_A_DM.nif")
            self.assertEqual(result.target_logical_path, result.template_logical_path)
            self.assertEqual(result.compiled_payload, fixture.template_payload)
            self.assertEqual(result.compiled_sha256, result.template_sha256)
            self.assertEqual(result.compiled_size, result.template_size)
            self.assertFalse(result.payload_changed)
            with self.assertRaises(FrozenInstanceError):
                result.target_logical_path = "other.nif"  # type: ignore[misc]
        finally:
            temporary.cleanup()

    def test_user_edited_target_path_is_accepted_without_existence_policy(self) -> None:
        temporary, fixture = self.make_fixture()
        try:
            fixture.write_asset(target_logical_path=r"Win32\Textures\Dragon_B.nif")
            result = self.compile_fixture(fixture)
            self.assertEqual(result.target_logical_path, r"Win32\Textures\Dragon_B.nif")
            self.assertFalse(result.payload_changed)
        finally:
            temporary.cleanup()

    def test_asset_json_allows_whitespace_and_key_reordering(self) -> None:
        temporary, fixture = self.make_fixture()
        try:
            document = fixture.asset_document(target_logical_path=r"Win32\Textures\Dragon_B.nif")
            reordered = {
                "target_logical_path": document["target_logical_path"],
                "template": document["template"],
                "asset_type": document["asset_type"],
                "schema_version": document["schema_version"],
                "schema": document["schema"],
            }
            (fixture.root / "asset.json").write_text(
                "  " + json.dumps(reordered, indent=4) + "  \n", encoding="utf-8"
            )
            self.assertEqual(parse_asset_package(fixture.root).target_logical_path, r"Win32\Textures\Dragon_B.nif")
        finally:
            temporary.cleanup()

    def test_edited_bc1_and_bc3_pngs_are_accepted(self) -> None:
        for pixel_format in (bc.FORMAT_BC1, bc.FORMAT_BC3):
            with self.subTest(pixel_format=pixel_format):
                temporary, fixture = self.make_fixture(pixel_format)
                try:
                    views = decode_mip_views(fixture.resource)
                    edited = bytearray(views.rgb)
                    edited[:3] = bytes((0, 255, 0))
                    (fixture.texture_directory / "mip-00.rgb.png").write_bytes(
                        encode_png_rgb(views.width, views.height, edited)
                    )
                    result = self.compile_fixture(fixture)
                    self.assertTrue(result.payload_changed)
                    self.assertNotEqual(result.compiled_payload, fixture.template_payload)
                    self.assertEqual(result.template_sha256, hashlib.sha256(fixture.template_payload).hexdigest())
                finally:
                    temporary.cleanup()

    def test_changed_png_is_not_compared_to_export_time_sha(self) -> None:
        temporary, fixture = self.make_fixture()
        try:
            views = decode_mip_views(fixture.resource)
            # Use a colour far from both fixture endpoints so the compressed
            # range is observably different, while leaving asset.json and the
            # template SHA unchanged.
            edited = bytes((0, 0, 0)) * (views.width * views.height)
            (fixture.texture_directory / "mip-00.rgb.png").write_bytes(
                encode_png_rgb(views.width, views.height, edited)
            )
            # asset.json still binds the unchanged template.nif.  The edited
            # PNG has no export-time SHA contract in texture.json.
            result = self.compile_fixture(fixture)
            self.assertTrue(result.payload_changed)
        finally:
            temporary.cleanup()

    def test_unchanged_bc2_is_byte_perfect_and_changed_bc2_is_rejected(self) -> None:
        temporary, fixture = self.make_fixture(bc.FORMAT_BC2)
        try:
            unchanged = self.compile_fixture(fixture)
            self.assertEqual(unchanged.compiled_payload, fixture.template_payload)
            views = decode_mip_views(fixture.resource)
            edited = bytearray(views.rgb)
            edited[0] ^= 0xFF
            (fixture.texture_directory / "mip-00.rgb.png").write_bytes(
                encode_png_rgb(views.width, views.height, edited)
            )
            with self.assertRaisesRegex(TextureNIFHandlerError, "BC2 edits are unsupported"):
                self.compile_fixture(fixture)
        finally:
            temporary.cleanup()

    def test_template_sha_and_size_mismatch_are_rejected(self) -> None:
        for field, value in (("payload_sha256", "0" * 64), ("payload_size", 1)):
            with self.subTest(field=field):
                temporary, fixture = self.make_fixture()
                try:
                    document = fixture.asset_document()
                    document["template"][field] = value  # type: ignore[index]
                    (fixture.root / "asset.json").write_bytes(_canonical_json(document))
                    with self.assertRaisesRegex(AssetPackageError, "does not match template.nif"):
                        parse_asset_package(fixture.root)
                finally:
                    temporary.cleanup()

    def test_texture_json_and_mip_geometry_are_delegated_to_shared_validation(self) -> None:
        temporary, fixture = self.make_fixture()
        try:
            sidecar = json.loads((fixture.texture_directory / "texture.json").read_text(encoding="utf-8"))
            sidecar["source"]["payload_sha256"] = "0" * 64
            (fixture.texture_directory / "texture.json").write_bytes(_canonical_json(sidecar))
            with self.assertRaisesRegex(TextureNIFHandlerError, "texture.json"):
                self.compile_fixture(fixture)

            # Restore the exact sidecar, then provide a PNG with invalid mip
            # geometry.  The handler must let import_texture_set reject it.
            for name, payload in build_export_set(fixture.resource).items():
                (fixture.texture_directory / name).write_bytes(payload)
            (fixture.texture_directory / "mip-00.rgb.png").write_bytes(
                encode_png_rgb(1, 1, bytes((1, 2, 3)))
            )
            with self.assertRaisesRegex(TextureNIFHandlerError, "dimensions"):
                self.compile_fixture(fixture)
        finally:
            temporary.cleanup()


class AssetPackageInputValidationTests(unittest.TestCase):
    def make_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], TexturePackageFixture]:
        temporary = tempfile.TemporaryDirectory()
        return temporary, TexturePackageFixture(Path(temporary.name) / "package")

    def assert_parse_error(self, fixture: TexturePackageFixture, pattern: str = "") -> None:
        context = self.assertRaisesRegex(AssetPackageError, pattern) if pattern else self.assertRaises(AssetPackageError)
        with context:
            parse_asset_package(fixture.root)

    def test_duplicate_nonfinite_and_oversized_asset_json_are_rejected(self) -> None:
        temporary, fixture = self.make_fixture()
        try:
            (fixture.root / "asset.json").write_bytes(b'{"schema": 1, "schema": 2}')
            self.assert_parse_error(fixture, "invalid UTF-8 JSON")
            (fixture.root / "asset.json").write_bytes(b'{"schema_version": NaN}')
            self.assert_parse_error(fixture, "invalid UTF-8 JSON")
            (fixture.root / "asset.json").write_bytes(b" " * (MAX_ASSET_JSON_BYTES + 1))
            self.assert_parse_error(fixture, "size limit")
        finally:
            temporary.cleanup()

    def test_asset_json_field_types_and_exact_fields_are_rejected(self) -> None:
        variants = (
            ("schema_version", True),
            ("target_logical_path", 7),
            ("asset_type", ""),
            ("asset_type", "model/nif"),
        )
        for field, value in variants:
            with self.subTest(field=field):
                temporary, fixture = self.make_fixture()
                try:
                    document = fixture.asset_document()
                    document[field] = value
                    (fixture.root / "asset.json").write_bytes(_canonical_json(document))
                    self.assert_parse_error(fixture)
                finally:
                    temporary.cleanup()

    def test_unsafe_logical_paths_are_rejected_by_generic_parser(self) -> None:
        paths = (r"..\escape.nif", r"C:\absolute.nif", r"a\..\b.nif", "safe\x00.nif")
        for path in paths:
            with self.subTest(path=path):
                temporary, fixture = self.make_fixture()
                try:
                    fixture.write_asset(target_logical_path=path)
                    self.assert_parse_error(fixture)
                finally:
                    temporary.cleanup()

    def test_non_nif_paths_parse_generically_but_texture_handler_rejects_them(self) -> None:
        temporary, fixture = self.make_fixture()
        try:
            fixture.write_asset(target_logical_path="texture.txt")
            package = parse_asset_package(fixture.root)
            self.assertEqual(package.target_logical_path, "texture.txt")
            with self.assertRaisesRegex(TextureNIFHandlerError, "target logical path"):
                TextureNIFHandler().compile(package)
        finally:
            temporary.cleanup()

        temporary, fixture = self.make_fixture()
        try:
            fixture.write_asset(template_logical_path="template.bin")
            package = parse_asset_package(fixture.root)
            with self.assertRaisesRegex(TextureNIFHandlerError, "template logical path"):
                TextureNIFHandler().compile(package)
        finally:
            temporary.cleanup()

        temporary, fixture = self.make_fixture()
        try:
            template = fixture.root / "template.nif"
            renamed_template = fixture.root / "template.bin"
            template.rename(renamed_template)
            document = fixture.asset_document()
            document["template"]["file"] = "template.bin"  # type: ignore[index]
            (fixture.root / "asset.json").write_bytes(_canonical_json(document))
            package = parse_asset_package(fixture.root)
            with self.assertRaisesRegex(TextureNIFHandlerError, "template file"):
                TextureNIFHandler().compile(package)
        finally:
            temporary.cleanup()

    def test_missing_root_members_fail_generic_parse_but_texture_layout_is_handler_owned(self) -> None:
        for mutation in ("missing_asset", "missing_template"):
            with self.subTest(mutation=mutation):
                temporary, fixture = self.make_fixture()
                try:
                    if mutation == "missing_asset":
                        (fixture.root / "asset.json").unlink()
                    elif mutation == "missing_template":
                        (fixture.root / "template.nif").unlink()
                    elif mutation == "missing_texture":
                        shutil.rmtree(fixture.texture_directory)
                    else:
                        (fixture.root / "unexpected.bin").write_bytes(b"x")
                    self.assert_parse_error(fixture)
                finally:
                    temporary.cleanup()

        for mutation in ("missing_texture", "wrong_texture", "extra"):
            with self.subTest(mutation=mutation):
                temporary, fixture = self.make_fixture()
                try:
                    if mutation == "missing_texture":
                        shutil.rmtree(fixture.texture_directory)
                    elif mutation == "wrong_texture":
                        shutil.rmtree(fixture.texture_directory)
                        fixture.texture_directory.write_bytes(b"not a directory")
                    else:
                        (fixture.root / "unexpected.bin").write_bytes(b"x")
                    package = parse_asset_package(fixture.root)
                    with self.assertRaisesRegex(TextureNIFHandlerError, "root members mismatch" if mutation != "wrong_texture" else "texture directory"):
                        TextureNIFHandler().compile(package)
                finally:
                    temporary.cleanup()

    def test_symlinked_root_members_are_rejected_when_platform_allows_symlinks(self) -> None:
        temporary, fixture = self.make_fixture()
        try:
            source = fixture.root / "template.nif"
            backup = fixture.root / "template.real.nif"
            source.rename(backup)
            try:
                source.symlink_to(backup)
            except (OSError, NotImplementedError) as error:
                source.unlink(missing_ok=True)
                backup.rename(source)
                self.skipTest(f"symlink creation unavailable: {error}")
            self.assert_parse_error(fixture, "symlink or reparse")
        finally:
            temporary.cleanup()

    def test_symlinked_texture_entry_and_package_root_are_rejected_when_available(self) -> None:
        temporary, fixture = self.make_fixture()
        try:
            linked_file = fixture.texture_directory / "link.png"
            try:
                linked_file.symlink_to(fixture.texture_directory / "texture.json")
            except (OSError, NotImplementedError) as error:
                self.skipTest(f"symlink creation unavailable: {error}")
            with self.assertRaisesRegex(AssetPackageError, "symlink"):
                parse_asset_package(fixture.root)
        finally:
            temporary.cleanup()

    def test_symlinked_parent_component_is_rejected_when_available(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        try:
            base = Path(temporary.name)
            real_parent = base / "real-parent"
            real_parent.mkdir()
            fixture = TexturePackageFixture(real_parent / "package")
            linked_parent = base / "linked-parent"
            try:
                linked_parent.symlink_to(real_parent, target_is_directory=True)
            except (OSError, NotImplementedError) as error:
                self.skipTest(f"symlink creation unavailable: {error}")
            with self.assertRaisesRegex(AssetPackageError, "traverse a symlink"):
                parse_asset_package(linked_parent / "package")
        finally:
            temporary.cleanup()

        temporary, fixture = self.make_fixture()
        try:
            linked_root = Path(temporary.name) / "linked-package"
            try:
                linked_root.symlink_to(fixture.root, target_is_directory=True)
            except (OSError, NotImplementedError) as error:
                self.skipTest(f"directory symlink creation unavailable: {error}")
            self.assertRaises(AssetPackageError, parse_asset_package, linked_root)
        finally:
            temporary.cleanup()


class HandlerRegistryTests(unittest.TestCase):
    def test_registry_lookup_and_unsupported_asset_type(self) -> None:
        registry = default_registry()
        self.assertEqual(registry.asset_types(), (ASSET_TYPE_NARRATIVE, ASSET_TYPE_TEXTURE_NIF))
        self.assertIsInstance(registry.get(ASSET_TYPE_TEXTURE_NIF), TextureNIFHandler)
        with self.assertRaises(UnsupportedAssetTypeError):
            registry.get("model_nif")

        temporary = tempfile.TemporaryDirectory()
        try:
            fixture = TexturePackageFixture(Path(temporary.name) / "package")
            fixture.write_asset(asset_type="model_nif")
            package = parse_asset_package(fixture.root)
            self.assertEqual(package.asset_type, "model_nif")
            with self.assertRaises(UnsupportedAssetTypeError):
                registry.compile(package)
        finally:
            temporary.cleanup()


if __name__ == "__main__":
    unittest.main()
