"""Texture-NIF asset-package compiler."""

# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

import hashlib

from dks_patch_builder.codec.nif_texture import NIFTextureError, parse_texture_resource
from dks_patch_builder.codec.roundtrip import TextureRoundTripError, import_texture_set

from ..package import AssetPackage, AssetPackageError
from .base import CompiledResource, HandlerError


ASSET_TYPE_TEXTURE_NIF = "texture_nif"
TEMPLATE_FILE_NAME = "template.nif"
TEXTURE_DIRECTORY_NAME = "texture"
_EXPECTED_ROOT_MEMBERS = frozenset({"asset.json", TEMPLATE_FILE_NAME, TEXTURE_DIRECTORY_NAME})


class TextureNIFHandlerError(HandlerError):
    """Raised when a texture-NIF package cannot be compiled."""


class TextureNIFHandler:
    """Compile an existing texture NIF template with an edited export-set."""

    asset_type = ASSET_TYPE_TEXTURE_NIF

    def compile(self, package: AssetPackage) -> CompiledResource:
        if not isinstance(package, AssetPackage):
            raise TextureNIFHandlerError("texture-NIF handler requires an AssetPackage")
        if package.asset_type != self.asset_type:
            raise TextureNIFHandlerError(
                f"texture-NIF handler cannot compile asset type {package.asset_type!r}"
            )
        if package.template_file_name != TEMPLATE_FILE_NAME:
            raise TextureNIFHandlerError(
                f"texture-NIF package template file must be {TEMPLATE_FILE_NAME!r}"
            )
        if set(package.root_members) != _EXPECTED_ROOT_MEMBERS:
            missing = sorted(_EXPECTED_ROOT_MEMBERS - set(package.root_members))
            extra = sorted(set(package.root_members) - _EXPECTED_ROOT_MEMBERS)
            details: list[str] = []
            if missing:
                details.append(f"missing={missing!r}")
            if extra:
                details.append(f"extra={extra!r}")
            raise TextureNIFHandlerError(
                f"texture-NIF package root members mismatch ({', '.join(details)})"
            )
        if not package.template_logical_path.casefold().endswith(".nif"):
            raise TextureNIFHandlerError("texture-NIF template logical path must end in .nif")
        if not package.target_logical_path.casefold().endswith(".nif"):
            raise TextureNIFHandlerError("texture-NIF target logical path must end in .nif")
        try:
            texture_directory = package.child_directory(TEXTURE_DIRECTORY_NAME)
        except AssetPackageError as error:
            raise TextureNIFHandlerError(
                f"texture-NIF package texture directory is invalid: {error}"
            ) from error
        try:
            resource = parse_texture_resource(
                package.template_payload,
                label=str(package.template_file),
            )
        except NIFTextureError as error:
            raise TextureNIFHandlerError(
                f"template.nif is not a supported texture wrapper: {error}"
            ) from error

        try:
            compiled_payload = import_texture_set(resource, texture_directory)
        except TextureRoundTripError as error:
            raise TextureNIFHandlerError(
                f"texture export-set failed shared validation: {error}"
            ) from error

        # import_texture_set already reparses and validates the generated
        # wrapper through the shared serializer.  Keep this final parse here as
        # an explicit handler boundary and to ensure the output is a complete
        # supported texture resource before it is handed to an archive layer.
        try:
            parse_texture_resource(compiled_payload, label="compiled texture NIF")
        except NIFTextureError as error:  # pragma: no cover - defensive boundary
            raise TextureNIFHandlerError(
                f"compiled texture NIF failed shared validation: {error}"
            ) from error

        compiled_sha256 = hashlib.sha256(compiled_payload).hexdigest()
        return CompiledResource(
            asset_type=self.asset_type,
            template_logical_path=package.template_logical_path,
            target_logical_path=package.target_logical_path,
            compiled_payload=compiled_payload,
            compiled_sha256=compiled_sha256,
            compiled_size=len(compiled_payload),
            template_sha256=package.template_payload_sha256,
            template_size=package.template_payload_size,
            payload_changed=compiled_payload != package.template_payload,
            preferred_storage_mode="raw",
        )


__all__ = ["TextureNIFHandler", "TextureNIFHandlerError"]
