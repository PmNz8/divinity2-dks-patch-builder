"""Built-in modular asset handlers."""

# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only

from .base import (
    AssetHandler,
    CompiledBundle,
    CompiledResource,
    HandlerError,
    HandlerRegistry,
    UnsupportedAssetTypeError,
)
from .narrative_bundle import (
    ASSET_TYPE_NARRATIVE,
    NarrativeBundleHandler,
    NarrativeBundleHandlerError,
)
from .texture_nif import (
    ASSET_TYPE_TEXTURE_NIF,
    TEMPLATE_FILE_NAME,
    TEXTURE_DIRECTORY_NAME,
    TextureNIFHandler,
    TextureNIFHandlerError,
)


def default_registry(*, include_narrative: bool = True) -> HandlerRegistry:
    registry = HandlerRegistry()
    registry.register(TextureNIFHandler())
    if include_narrative:
        registry.register(NarrativeBundleHandler())
    return registry


__all__ = [
    "AssetHandler",
    "ASSET_TYPE_TEXTURE_NIF",
    "ASSET_TYPE_NARRATIVE",
    "CompiledBundle",
    "CompiledResource",
    "HandlerError",
    "HandlerRegistry",
    "TEMPLATE_FILE_NAME",
    "TEXTURE_DIRECTORY_NAME",
    "TextureNIFHandler",
    "TextureNIFHandlerError",
    "NarrativeBundleHandler",
    "NarrativeBundleHandlerError",
    "UnsupportedAssetTypeError",
    "default_registry",
]
