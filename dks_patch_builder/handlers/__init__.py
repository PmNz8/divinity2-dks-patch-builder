"""Built-in modular asset handlers."""

# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only

from .base import (
    AssetHandler,
    CompiledResource,
    HandlerError,
    HandlerRegistry,
    UnsupportedAssetTypeError,
)
from .texture_nif import (
    ASSET_TYPE_TEXTURE_NIF,
    TEMPLATE_FILE_NAME,
    TEXTURE_DIRECTORY_NAME,
    TextureNIFHandler,
    TextureNIFHandlerError,
)


def default_registry() -> HandlerRegistry:
    registry = HandlerRegistry()
    registry.register(TextureNIFHandler())
    return registry


__all__ = [
    "AssetHandler",
    "ASSET_TYPE_TEXTURE_NIF",
    "CompiledResource",
    "HandlerError",
    "HandlerRegistry",
    "TEMPLATE_FILE_NAME",
    "TEXTURE_DIRECTORY_NAME",
    "TextureNIFHandler",
    "TextureNIFHandlerError",
    "UnsupportedAssetTypeError",
    "default_registry",
]
