"""Generic asset-package v1 loader for the DKS Patch Builder.

The package layer validates only the common envelope shared by future asset
handlers.  It deliberately does not know whether a handler expects a NIF,
texture export-set, model, audio bank, or any other child layout.

Every package has a root ``asset.json`` and a template file whose safe
basename is declared by that JSON document.  Other root members are recorded
and are left for the selected handler to validate.
"""

# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import re
import stat
from typing import Final

from dks_patch_builder.dv2lib import DV2Error, normalize_archive_path


ASSET_SCHEMA: Final = "divinity2.dks_asset_package"
ASSET_SCHEMA_VERSION: Final = 1
ASSET_JSON_NAME: Final = "asset.json"

# These are envelope limits, not engine limits.  They bound accidental input
# while leaving room for the large resources already present in the corpus.
MAX_ASSET_JSON_BYTES: Final = 1 << 20
MAX_TEMPLATE_PAYLOAD_BYTES: Final = 512 << 20
MAX_LOGICAL_PATH_BYTES: Final = 4096
MAX_ASSET_TYPE_BYTES: Final = 128
MAX_TEMPLATE_FILE_NAME_BYTES: Final = 255
_REPARSE_POINT: Final = 0x400
_SHA256_RE: Final = re.compile(r"[0-9a-fA-F]{64}\Z")
_ASSET_TYPE_RE: Final = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*\Z")
_WINDOWS_FORBIDDEN_NAME_CHARS: Final = frozenset('<>:"/\\|?*')
_WINDOWS_RESERVED_NAMES: Final = frozenset(
    {"con", "prn", "aux", "nul"}
    | {f"com{index}" for index in range(1, 10)}
    | {f"lpt{index}" for index in range(1, 10)}
)


class AssetPackageError(ValueError):
    """Raised when an asset package is malformed or unsafe to read."""


def _lstat(path: Path, label: str) -> os.stat_result:
    try:
        return path.lstat()
    except OSError as error:
        raise AssetPackageError(f"cannot inspect {label}: {path}") from error


def _is_reparse_or_symlink(path: Path, metadata: os.stat_result | None = None) -> bool:
    """Return whether *path* is a symlink or Windows reparse point."""

    if path.is_symlink():
        return True
    if metadata is None:
        try:
            metadata = path.lstat()
        except OSError:
            return False
    return bool(getattr(metadata, "st_file_attributes", 0) & _REPARSE_POINT)


def _reject_link_components(path: Path, label: str) -> None:
    """Reject symlink/reparse traversal in every component leading to *path*."""

    absolute = path.absolute()
    anchor = Path(absolute.anchor) if absolute.anchor else Path.cwd().anchor
    current = Path(anchor) if anchor else Path()
    parts = absolute.parts
    if absolute.anchor and parts and parts[0] == absolute.anchor:
        parts = parts[1:]
    for part in parts:
        current = current / part
        metadata = _lstat(current, f"{label} path component")
        if _is_reparse_or_symlink(current, metadata):
            raise AssetPackageError(
                f"{label} must not traverse a symlink or reparse point: {current}"
            )


def _require_directory(path: Path, label: str) -> None:
    metadata = _lstat(path, label)
    if _is_reparse_or_symlink(path, metadata):
        raise AssetPackageError(f"{label} must not be a symlink or reparse point: {path}")
    if not stat.S_ISDIR(metadata.st_mode):
        raise AssetPackageError(f"{label} is not a directory: {path}")


def _require_regular_file(path: Path, label: str) -> None:
    metadata = _lstat(path, label)
    if _is_reparse_or_symlink(path, metadata):
        raise AssetPackageError(f"{label} must not be a symlink or reparse point: {path}")
    if not stat.S_ISREG(metadata.st_mode):
        raise AssetPackageError(f"{label} is not a regular file: {path}")


def _reject_reparse_children(directory: Path, label: str) -> None:
    """Reject link-like direct children before a handler traverses a child."""

    try:
        entries = tuple(directory.iterdir())
    except OSError as error:
        raise AssetPackageError(f"cannot enumerate {label}: {directory}") from error
    for entry in entries:
        metadata = _lstat(entry, f"{label} entry {entry.name!r}")
        if _is_reparse_or_symlink(entry, metadata):
            raise AssetPackageError(
                f"{label} entry must not be a symlink or reparse point: {entry.name!r}"
            )


def _read_bounded(path: Path, label: str, limit: int) -> bytes:
    _require_regular_file(path, label)
    try:
        with path.open("rb") as stream:
            chunks: list[bytes] = []
            total = 0
            while True:
                chunk = stream.read(min(1 << 20, limit - total + 1))
                if not chunk:
                    break
                total += len(chunk)
                if total > limit:
                    raise AssetPackageError(
                        f"{label} exceeds the supported size limit ({limit} bytes): {path}"
                    )
                chunks.append(chunk)
    except AssetPackageError:
        raise
    except OSError as error:
        raise AssetPackageError(f"cannot read {label}: {path}") from error
    return b"".join(chunks)


def _parse_json(raw: bytes, label: str) -> object:
    def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key {key!r}")
            result[key] = value
        return result

    def reject_constant(value: str) -> object:
        raise ValueError(f"non-finite JSON constant {value}")

    try:
        text = raw.decode("utf-8", "strict")
        return json.loads(
            text,
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as error:
        raise AssetPackageError(f"{label}: invalid UTF-8 JSON") from error


def _require_exact_keys(value: object, expected: set[str], label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise AssetPackageError(f"{label} must be a JSON object")
    keys = set(value)
    if keys != expected:
        missing = sorted(expected - keys)
        extra = sorted(keys - expected)
        details: list[str] = []
        if missing:
            details.append(f"missing={missing!r}")
        if extra:
            details.append(f"extra={extra!r}")
        raise AssetPackageError(f"{label} fields mismatch ({', '.join(details)})")
    return value


def _require_string(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise AssetPackageError(f"{label} must be a string")
    return value


def _require_integer(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise AssetPackageError(f"{label} must be an integer")
    return value


def _validate_sha256(value: object, label: str) -> str:
    candidate = _require_string(value, label)
    if _SHA256_RE.fullmatch(candidate) is None:
        raise AssetPackageError(f"{label} must be a 64-character hexadecimal SHA-256")
    return candidate.casefold()


def _normalize_logical_path(value: object, label: str) -> str:
    raw = _require_string(value, label)
    if "\x00" in raw:
        raise AssetPackageError(f"{label} contains a NUL character")
    try:
        raw_size = len(raw.encode("utf-8", "surrogatepass"))
    except UnicodeEncodeError as error:
        raise AssetPackageError(f"{label} is not valid text") from error
    if raw_size > MAX_LOGICAL_PATH_BYTES:
        raise AssetPackageError(f"{label} exceeds the supported path length")
    try:
        return normalize_archive_path(raw)
    except (DV2Error, UnicodeEncodeError) as error:
        raise AssetPackageError(f"{label} is not a safe archive path: {raw!r}") from error


def _validate_asset_type(value: object) -> str:
    candidate = _require_string(value, "asset.json.asset_type")
    try:
        size = len(candidate.encode("ascii"))
    except UnicodeEncodeError as error:
        raise AssetPackageError(
            "asset.json.asset_type must use ASCII machine-style characters"
        ) from error
    if not 1 <= size <= MAX_ASSET_TYPE_BYTES:
        raise AssetPackageError("asset.json.asset_type has an unsupported length")
    if _ASSET_TYPE_RE.fullmatch(candidate) is None:
        raise AssetPackageError(
            "asset.json.asset_type must match [A-Za-z0-9][A-Za-z0-9_.-]*"
        )
    return candidate


def _validate_template_file_name(value: object) -> str:
    candidate = _require_string(value, "asset.json.template.file")
    try:
        size = len(candidate.encode("utf-8", "surrogatepass"))
    except UnicodeEncodeError as error:
        raise AssetPackageError("asset.json.template.file is not valid text") from error
    if not 1 <= size <= MAX_TEMPLATE_FILE_NAME_BYTES:
        raise AssetPackageError("asset.json.template.file has an unsupported length")
    if (
        candidate in {".", "..", ASSET_JSON_NAME}
        or any(character in _WINDOWS_FORBIDDEN_NAME_CHARS for character in candidate)
        or "\x00" in candidate
        or any(ord(character) < 0x20 for character in candidate)
        or candidate[-1] in {" ", "."}
    ):
        raise AssetPackageError(
            "asset.json.template.file must be one safe direct-child basename"
        )
    windows_path = PureWindowsPath(candidate)
    if windows_path.is_absolute() or windows_path.drive or windows_path.root:
        raise AssetPackageError(
            "asset.json.template.file must be one safe direct-child basename"
        )
    stem = candidate.split(".", 1)[0].casefold()
    if stem in _WINDOWS_RESERVED_NAMES:
        raise AssetPackageError(
            "asset.json.template.file must be one safe direct-child basename"
        )
    return candidate


def _validate_child_name(name: object) -> str:
    if not isinstance(name, str) or not name:
        raise AssetPackageError("package child name must be a non-empty string")
    if name in {".", ".."} or "/" in name or "\\" in name or "\x00" in name:
        raise AssetPackageError(f"package child name is not a safe basename: {name!r}")
    return name


@dataclass(frozen=True, slots=True)
class AssetPackage:
    """Validated generic asset-package metadata and immutable template bytes."""

    root: Path
    asset_json_file: Path
    template_file: Path
    template_file_name: str
    root_members: tuple[str, ...]
    schema: str
    schema_version: int
    asset_type: str
    template_logical_path: str
    target_logical_path: str
    template_payload_sha256: str
    template_payload_size: int
    _template_payload: bytes = field(repr=False, compare=False)

    @property
    def template_payload(self) -> bytes:
        return self._template_payload

    @property
    def template_sha256(self) -> str:
        return self.template_payload_sha256

    def child(self, name: str) -> Path:
        """Return one existing, link-free direct child of the package root."""

        safe_name = _validate_child_name(name)
        if safe_name not in self.root_members:
            raise AssetPackageError(f"asset package has no root member {safe_name!r}")
        child = self.root / safe_name
        metadata = _lstat(child, f"asset package child {safe_name!r}")
        if _is_reparse_or_symlink(child, metadata):
            raise AssetPackageError(
                f"asset package child must not be a symlink or reparse point: {safe_name!r}"
            )
        return child

    def child_directory(self, name: str) -> Path:
        """Return one link-free direct child directory and inspect its children."""

        child = self.child(name)
        _require_directory(child, f"asset package child directory {name!r}")
        _reject_reparse_children(child, f"asset package child directory {name!r}")
        return child


def parse_asset_package(package_directory: str | os.PathLike[str]) -> AssetPackage:
    """Read and validate one generic v1 asset-package directory.

    The parser accepts unsupported asset types and arbitrary additional root
    members so future handlers can share this envelope.  Handler-specific
    layout and extension checks happen after this function returns.
    """

    root = Path(package_directory).absolute()
    _reject_link_components(root, "asset package root")
    _require_directory(root, "asset package root")

    try:
        entries = tuple(root.iterdir())
    except OSError as error:
        raise AssetPackageError(f"cannot enumerate asset package root: {root}") from error
    root_members: list[str] = []
    for entry in entries:
        metadata = _lstat(entry, f"asset package entry {entry.name!r}")
        if _is_reparse_or_symlink(entry, metadata):
            raise AssetPackageError(
                f"asset package entry must not be a symlink or reparse point: {entry.name!r}"
            )
        root_members.append(entry.name)
    if ASSET_JSON_NAME not in root_members:
        raise AssetPackageError("asset package root is missing asset.json")

    asset_json_file = root / ASSET_JSON_NAME
    _require_regular_file(asset_json_file, ASSET_JSON_NAME)
    asset_json = _read_bounded(asset_json_file, ASSET_JSON_NAME, MAX_ASSET_JSON_BYTES)
    raw_document = _parse_json(asset_json, ASSET_JSON_NAME)
    document = _require_exact_keys(
        raw_document,
        {"schema", "schema_version", "asset_type", "template", "target_logical_path"},
        ASSET_JSON_NAME,
    )

    schema = _require_string(document["schema"], "asset.json.schema")
    if schema != ASSET_SCHEMA:
        raise AssetPackageError(f"asset.json.schema must be {ASSET_SCHEMA!r}")
    schema_version = _require_integer(document["schema_version"], "asset.json.schema_version")
    if schema_version != ASSET_SCHEMA_VERSION:
        raise AssetPackageError(
            f"asset.json.schema_version must be {ASSET_SCHEMA_VERSION}, got {schema_version}"
        )
    asset_type = _validate_asset_type(document["asset_type"])
    template = _require_exact_keys(
        document["template"],
        {"file", "logical_path", "payload_sha256", "payload_size"},
        "asset.json.template",
    )
    template_file_name = _validate_template_file_name(template["file"])
    if template_file_name not in root_members:
        raise AssetPackageError(
            f"asset package root is missing declared template file {template_file_name!r}"
        )
    template_logical_path = _normalize_logical_path(
        template["logical_path"], "asset.json.template.logical_path"
    )
    target_logical_path = _normalize_logical_path(
        document["target_logical_path"], "asset.json.target_logical_path"
    )
    template_payload_sha256 = _validate_sha256(
        template["payload_sha256"], "asset.json.template.payload_sha256"
    )
    template_payload_size = _require_integer(
        template["payload_size"], "asset.json.template.payload_size"
    )
    if not 0 <= template_payload_size <= MAX_TEMPLATE_PAYLOAD_BYTES:
        raise AssetPackageError(
            "asset.json.template.payload_size is outside the supported bounds"
        )

    template_file = root / template_file_name
    _require_regular_file(template_file, template_file_name)
    template_payload = _read_bounded(
        template_file, template_file_name, MAX_TEMPLATE_PAYLOAD_BYTES
    )
    actual_size = len(template_payload)
    actual_sha256 = hashlib.sha256(template_payload).hexdigest()
    if template_payload_size != actual_size:
        raise AssetPackageError(
            f"asset.json.template.payload_size does not match {template_file_name}"
        )
    if template_payload_sha256 != actual_sha256:
        raise AssetPackageError(
            f"asset.json.template.payload_sha256 does not match {template_file_name}"
        )

    return AssetPackage(
        root=root,
        asset_json_file=asset_json_file,
        template_file=template_file,
        template_file_name=template_file_name,
        root_members=tuple(sorted(root_members)),
        schema=schema,
        schema_version=schema_version,
        asset_type=asset_type,
        template_logical_path=template_logical_path,
        target_logical_path=target_logical_path,
        template_payload_sha256=template_payload_sha256,
        template_payload_size=template_payload_size,
        _template_payload=template_payload,
    )


load_asset_package = parse_asset_package


__all__ = [
    "ASSET_JSON_NAME",
    "ASSET_SCHEMA",
    "ASSET_SCHEMA_VERSION",
    "AssetPackage",
    "AssetPackageError",
    "MAX_ASSET_JSON_BYTES",
    "MAX_ASSET_TYPE_BYTES",
    "MAX_LOGICAL_PATH_BYTES",
    "MAX_TEMPLATE_FILE_NAME_BYTES",
    "MAX_TEMPLATE_PAYLOAD_BYTES",
    "load_asset_package",
    "parse_asset_package",
]
