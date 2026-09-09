"""Small handler and compiled-resource contracts for DKS Patch Builder."""

# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
from typing import Protocol, runtime_checkable

from dks_patch_builder.dv2lib import STORAGE_MODES

from ..package import AssetPackage


_SHA256_RE = re.compile(r"[0-9a-fA-F]{64}\Z")


class HandlerError(ValueError):
    """Base error for asset-handler failures."""


@dataclass(frozen=True, slots=True)
class CompiledResource:
    """Immutable resource payload returned by an asset handler.

    The result intentionally contains no archive or precedence decision.  A
    later archive layer may use it to stage ADD/REPLACE operations.
    """

    asset_type: str
    template_logical_path: str
    target_logical_path: str
    compiled_payload: bytes
    compiled_sha256: str
    compiled_size: int
    template_sha256: str
    template_size: int
    payload_changed: bool
    preferred_storage_mode: str

    def __post_init__(self) -> None:
        if not isinstance(self.asset_type, str) or not self.asset_type:
            raise HandlerError("compiled resource asset_type must be a non-empty string")
        if not isinstance(self.template_logical_path, str) or not self.template_logical_path:
            raise HandlerError("compiled resource template path must be a non-empty string")
        if not isinstance(self.target_logical_path, str) or not self.target_logical_path:
            raise HandlerError("compiled resource target path must be a non-empty string")
        if not isinstance(self.compiled_payload, (bytes, bytearray, memoryview)):
            raise HandlerError("compiled resource payload must be bytes-like")
        payload = bytes(self.compiled_payload)
        object.__setattr__(self, "compiled_payload", payload)
        if not isinstance(self.compiled_sha256, str) or _SHA256_RE.fullmatch(self.compiled_sha256) is None:
            raise HandlerError("compiled resource SHA-256 is invalid")
        actual_sha256 = hashlib.sha256(payload).hexdigest()
        if self.compiled_sha256.casefold() != actual_sha256:
            raise HandlerError("compiled resource SHA-256 does not match payload")
        object.__setattr__(self, "compiled_sha256", actual_sha256)
        if isinstance(self.compiled_size, bool) or not isinstance(self.compiled_size, int):
            raise HandlerError("compiled resource size must be an integer")
        if self.compiled_size < 0 or self.compiled_size != len(payload):
            raise HandlerError("compiled resource size does not match payload")
        if not isinstance(self.template_sha256, str) or _SHA256_RE.fullmatch(self.template_sha256) is None:
            raise HandlerError("compiled resource template SHA-256 is invalid")
        object.__setattr__(self, "template_sha256", self.template_sha256.casefold())
        if isinstance(self.template_size, bool) or not isinstance(self.template_size, int):
            raise HandlerError("compiled resource template size must be an integer")
        if self.template_size < 0:
            raise HandlerError("compiled resource template size cannot be negative")
        if not isinstance(self.payload_changed, bool):
            raise HandlerError("compiled resource payload_changed must be boolean")
        if self.preferred_storage_mode not in STORAGE_MODES:
            raise HandlerError(
                "compiled resource preferred_storage_mode must be one of "
                f"{STORAGE_MODES!r}"
            )

    @property
    def payload(self) -> bytes:
        """Convenient generic name for the compiled payload."""

        return self.compiled_payload


@runtime_checkable
class AssetHandler(Protocol):
    """Minimal protocol implemented by one resource compiler."""

    asset_type: str

    def compile(self, package: AssetPackage) -> CompiledResource:
        ...


class UnsupportedAssetTypeError(HandlerError):
    """Raised when no registered handler supports an asset type."""


class HandlerRegistry:
    """Explicit registry for modular asset handlers."""

    def __init__(self) -> None:
        self._handlers: dict[str, AssetHandler] = {}

    def register(self, handler: AssetHandler) -> None:
        asset_type = getattr(handler, "asset_type", None)
        compile_method = getattr(handler, "compile", None)
        if not isinstance(asset_type, str) or not asset_type:
            raise TypeError("handler.asset_type must be a non-empty string")
        if not callable(compile_method):
            raise TypeError("handler.compile must be callable")
        if asset_type in self._handlers:
            raise HandlerError(f"handler already registered for asset type {asset_type!r}")
        self._handlers[asset_type] = handler

    def get(self, asset_type: str) -> AssetHandler:
        try:
            return self._handlers[asset_type]
        except (KeyError, TypeError) as error:
            raise UnsupportedAssetTypeError(
                f"no asset handler registered for {asset_type!r}"
            ) from error

    def compile(self, package: AssetPackage) -> CompiledResource:
        return self.get(package.asset_type).compile(package)

    def asset_types(self) -> tuple[str, ...]:
        return tuple(sorted(self._handlers))


__all__ = [
    "AssetHandler",
    "CompiledResource",
    "HandlerError",
    "HandlerRegistry",
    "UnsupportedAssetTypeError",
]
