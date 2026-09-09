"""Read-only inventory and occurrence lookup for a Packed directory.

This module deliberately stops at observation.  It parses every DV2 archive,
records its entry table, and can hash exact matching resources on demand.  It
does not infer archive precedence and does not write or install anything.
"""

# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import stat
from typing import Final, Iterable

from dks_patch_builder import dv2lib


_REPARSE_POINT: Final = 0x400
MAX_OCCURRENCE_LOGICAL_BYTES: Final = 512 * 1024 * 1024
DKS_PATCH_FILE_NAME: Final = "DKS_Patch.dv2"
FOV_PATCH_FILE_NAME: Final = "FOV_Patch.dv2"
ROOT_PATCH_FILE_NAME: Final = "Patch.dv2"


class PackedInventoryError(ValueError):
    """Raised when a Packed inventory is missing, unsafe, or malformed."""


# Short alias for callers that do not need the storage-specific name.
InventoryError = PackedInventoryError


class _DigestSink:
    __slots__ = ("digest", "size")

    def __init__(self) -> None:
        self.digest = hashlib.sha256()
        self.size = 0

    def write(self, data: bytes) -> int:
        self.digest.update(data)
        self.size += len(data)
        return len(data)


def _is_reparse_or_symlink(path: Path, metadata: os.stat_result | None = None) -> bool:
    if path.is_symlink():
        return True
    if metadata is None:
        try:
            metadata = path.lstat()
        except OSError:
            return False
    return bool(getattr(metadata, "st_file_attributes", 0) & _REPARSE_POINT)


def _lstat(path: Path, label: str) -> os.stat_result:
    try:
        return path.lstat()
    except OSError as error:
        raise PackedInventoryError(f"cannot inspect {label}: {path}") from error


def _reject_link_components(path: Path, label: str) -> None:
    """Reject symlink/reparse traversal in every existing path component."""

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
            raise PackedInventoryError(
                f"{label} must not traverse a symlink or reparse point: {current}"
            )


def _require_directory(path: Path, label: str) -> None:
    metadata = _lstat(path, label)
    if _is_reparse_or_symlink(path, metadata):
        raise PackedInventoryError(f"{label} must not be a symlink or reparse point: {path}")
    if not stat.S_ISDIR(metadata.st_mode):
        raise PackedInventoryError(f"{label} is not a directory: {path}")


def _require_regular_file(path: Path, label: str) -> os.stat_result:
    metadata = _lstat(path, label)
    if _is_reparse_or_symlink(path, metadata):
        raise PackedInventoryError(f"{label} must not be a symlink or reparse point: {path}")
    if not stat.S_ISREG(metadata.st_mode):
        raise PackedInventoryError(f"{label} is not a regular file: {path}")
    return metadata


def _sort_key(path: Path) -> tuple[str, str]:
    return path.name.casefold(), path.name


def _iter_dv2_paths(root: Path) -> Iterable[Path]:
    """Yield every regular .dv2 file while explicitly rejecting links."""

    def visit(directory: Path) -> Iterable[Path]:
        try:
            children = sorted(directory.iterdir(), key=_sort_key)
        except OSError as error:
            raise PackedInventoryError(f"cannot enumerate Packed directory: {directory}") from error
        for child in children:
            metadata = _lstat(child, "Packed entry")
            if _is_reparse_or_symlink(child, metadata):
                raise PackedInventoryError(
                    f"Packed tree must not traverse a symlink or reparse point: {child}"
                )
            if stat.S_ISDIR(metadata.st_mode):
                yield from visit(child)
            elif stat.S_ISREG(metadata.st_mode) and child.suffix.casefold() == ".dv2":
                yield child

    yield from visit(root)


@dataclass(frozen=True, slots=True)
class ArchiveRecord:
    """One parsed physical archive; payload bytes are not read during scan."""

    relative_path: str
    physical_path: Path
    file_size: int
    header: dv2lib.DV2Header
    entries: tuple[dv2lib.DV2Entry, ...]
    entry_table_end: int

    @property
    def path(self) -> Path:
        """Compatibility alias for the physical archive path."""

        return self.physical_path

    @property
    def entry_count(self) -> int:
        return len(self.entries)

    @property
    def name(self) -> str:
        return self.physical_path.name


@dataclass(frozen=True, slots=True)
class PackedInventory:
    """Deterministic, immutable parse inventory for one Packed root."""

    root: Path
    archives: tuple[ArchiveRecord, ...]
    root_patch: ArchiveRecord
    root_dks_patch: ArchiveRecord | None
    root_fov_patch: ArchiveRecord | None

    @property
    def records(self) -> tuple[ArchiveRecord, ...]:
        return self.archives

    @property
    def archive_count(self) -> int:
        return len(self.archives)

    @property
    def root_special_records(self) -> tuple[ArchiveRecord, ...]:
        """Root-level Patch/DKS_Patch/FOV_Patch records, in stable order."""

        records = [self.root_patch]
        if self.root_dks_patch is not None:
            records.append(self.root_dks_patch)
        if self.root_fov_patch is not None:
            records.append(self.root_fov_patch)
        return tuple(records)

    @property
    def root_overlays(self) -> tuple[ArchiveRecord, ...]:
        """Alias for optional root special records; no precedence is implied."""

        return tuple(record for record in self.root_special_records if record is not self.root_patch)

    @property
    def root_level_patch(self) -> ArchiveRecord:
        return self.root_patch

    @property
    def root_level_dks_patch(self) -> ArchiveRecord | None:
        return self.root_dks_patch

    @property
    def root_level_fov_patch(self) -> ArchiveRecord | None:
        return self.root_fov_patch


@dataclass(frozen=True, slots=True)
class Occurrence:
    """One exact logical-path occurrence and its physical archive identity."""

    requested_logical_path: str
    physical_relative_path: str
    physical_path: Path
    physical_file_size: int
    physical_sha256: str
    entry_index: int
    canonical_entry_path: str
    storage_mode: str
    stored_size: int
    logical_size: int
    logical_sha256: str

    @property
    def archive_relative_path(self) -> str:
        return self.physical_relative_path

    @property
    def archive_path(self) -> Path:
        return self.physical_path

    @property
    def physical_size(self) -> int:
        return self.physical_file_size

    @property
    def archive_size(self) -> int:
        return self.physical_file_size

    @property
    def archive_sha256(self) -> str:
        return self.physical_sha256

    @property
    def entry_path(self) -> str:
        return self.canonical_entry_path


@dataclass(frozen=True, slots=True)
class SelectedDKS:
    """A selected DKS patch archive bound to its physical file hash and size."""

    physical_path: Path
    relative_path: str | None
    file_size: int
    sha256: str
    header: dv2lib.DV2Header
    entries: tuple[dv2lib.DV2Entry, ...]
    entry_table_end: int
    inside_packed: bool

    @property
    def path(self) -> Path:
        return self.physical_path

    @property
    def size(self) -> int:
        return self.file_size

    @property
    def physical_size(self) -> int:
        return self.file_size

    @property
    def physical_sha256(self) -> str:
        return self.sha256

    @property
    def archive_sha256(self) -> str:
        return self.sha256

    @property
    def entry_count(self) -> int:
        return len(self.entries)

    @property
    def archive(self) -> ArchiveRecord:
        """Snapshot view useful to planner code and callers."""

        return ArchiveRecord(
            relative_path=self.relative_path or self.physical_path.name,
            physical_path=self.physical_path,
            file_size=self.file_size,
            header=self.header,
            entries=self.entries,
            entry_table_end=self.entry_table_end,
        )


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError as error:  # pragma: no cover - defensive
        raise PackedInventoryError(f"archive is outside Packed root: {path}") from error


def _record_from_path(path: Path, *, relative_path: str) -> ArchiveRecord:
    metadata = _require_regular_file(path, "DV2 archive")
    try:
        session = dv2lib.DV2Session(path)
    except (dv2lib.DV2Error, OSError) as error:
        raise PackedInventoryError(f"cannot parse DV2 archive {path}: {error}") from error
    # Keep scan read-only and avoid source_sha256/deep_verify here.
    if session.file_size != metadata.st_size:
        raise PackedInventoryError(f"DV2 archive changed while parsing: {path}")
    return ArchiveRecord(
        relative_path=relative_path,
        physical_path=path.absolute(),
        file_size=session.file_size,
        header=session.header,
        entries=session.entries,
        entry_table_end=session.entry_table_end,
    )


def _resnapshot_record(record: ArchiveRecord) -> ArchiveRecord:
    """Re-read one matched archive's table before any payload access."""

    metadata = _require_regular_file(record.physical_path, "Packed archive")
    try:
        session = dv2lib.DV2Session(record.physical_path)
    except (dv2lib.DV2Error, OSError) as error:
        raise PackedInventoryError(
            f"cannot reparse matched DV2 archive {record.relative_path}: {error}"
        ) from error
    if (
        session.file_size != record.file_size
        or metadata.st_size != record.file_size
        or session.header != record.header
        or session.entries != record.entries
        or session.entry_table_end != record.entry_table_end
    ):
        raise PackedInventoryError(
            f"Packed archive entry table is stale for matched archive {record.relative_path}"
        )
    return ArchiveRecord(
        relative_path=record.relative_path,
        physical_path=record.physical_path,
        file_size=session.file_size,
        header=session.header,
        entries=session.entries,
        entry_table_end=session.entry_table_end,
    )


def scan_packed(
    root: str | os.PathLike,
    expected_count: int | None = None,
) -> PackedInventory:
    """Parse every regular ``.dv2`` under *root* without hashing payloads.

    The root-level ``Patch.dv2`` is mandatory.  Optional root-level
    ``DKS_Patch.dv2`` and ``FOV_Patch.dv2`` are reported as records only; this
    function intentionally makes no precedence claim.
    """

    if expected_count is not None:
        if isinstance(expected_count, bool) or not isinstance(expected_count, int) or expected_count <= 0:
            raise PackedInventoryError("expected_count must be a positive integer")
    packed_root = Path(root).absolute()
    _reject_link_components(packed_root, "Packed root")
    _require_directory(packed_root, "Packed root")

    paths = list(_iter_dv2_paths(packed_root))
    relative_by_key: dict[str, str] = {}
    for path in paths:
        relative = _relative_path(packed_root, path)
        key = relative.casefold()
        previous = relative_by_key.get(key)
        if previous is not None:
            raise PackedInventoryError(
                f"case-insensitive physical archive path collision: {previous!r} and {relative!r}"
            )
        relative_by_key[key] = relative

    records = tuple(
        sorted(
            (_record_from_path(path, relative_path=_relative_path(packed_root, path)) for path in paths),
            key=lambda record: (record.relative_path.casefold(), record.relative_path),
        )
    )
    if expected_count is not None and len(records) != expected_count:
        raise PackedInventoryError(
            f"Packed archive count is {len(records)}; expected exactly {expected_count}"
        )

    def root_record(name: str) -> ArchiveRecord | None:
        key = name.casefold()
        matches = [
            record
            for record in records
            if "/" not in record.relative_path and record.relative_path.casefold() == key
        ]
        return matches[0] if matches else None

    patch = root_record(ROOT_PATCH_FILE_NAME)
    if patch is None:
        raise PackedInventoryError(
            f"Packed root must contain exactly one root-level {ROOT_PATCH_FILE_NAME}"
        )
    dks_patch = root_record(DKS_PATCH_FILE_NAME)
    fov_patch = root_record(FOV_PATCH_FILE_NAME)
    return PackedInventory(
        root=packed_root,
        archives=records,
        root_patch=patch,
        root_dks_patch=dks_patch,
        root_fov_patch=fov_patch,
    )


def _validate_maximum_size(maximum_size: int) -> int:
    if isinstance(maximum_size, bool) or not isinstance(maximum_size, int) or maximum_size <= 0:
        raise PackedInventoryError("maximum_size must be a positive integer")
    return maximum_size


def _normalise_logical_path(logical_path: str) -> str:
    try:
        return dv2lib.normalize_archive_path(logical_path)
    except (dv2lib.DV2Error, TypeError) as error:
        raise PackedInventoryError(f"unsafe logical archive path: {logical_path!r}") from error


def _hash_logical_entry(record: ArchiveRecord, entry: dv2lib.DV2Entry, maximum_size: int) -> tuple[str, int]:
    if entry.logical_size > maximum_size:
        raise PackedInventoryError(
            f"logical payload for {entry.path!r} exceeds occurrence limit ({maximum_size} bytes)"
        )
    sink = _DigestSink()
    try:
        with record.physical_path.open("rb") as stream:
            produced = dv2lib.consume_entry(stream, record.header, entry, sink)
    except (dv2lib.DV2Error, OSError) as error:
        raise PackedInventoryError(
            f"cannot hash logical payload {entry.path!r} in {record.relative_path}: {error}"
        ) from error
    if produced != entry.logical_size or sink.size != entry.logical_size:
        raise PackedInventoryError(
            f"logical payload size mismatch for {entry.path!r} in {record.relative_path}"
        )
    return sink.digest.hexdigest(), sink.size


def find_occurrences(
    inventory: PackedInventory,
    logical_path: str,
    *,
    maximum_size: int = MAX_OCCURRENCE_LOGICAL_BYTES,
) -> tuple[Occurrence, ...]:
    """Find and hash every case-insensitive matching entry in *inventory*.

    Non-matching logical payloads are never decoded.  Physical archive SHA-256
    is computed once for each archive containing a match so every occurrence
    carries an auditable archive identity.
    """

    if not isinstance(inventory, PackedInventory):
        raise PackedInventoryError("find_occurrences requires a PackedInventory")
    normalized = _normalise_logical_path(logical_path)
    maximum_size = _validate_maximum_size(maximum_size)
    key = normalized.casefold()
    physical_hashes: dict[str, tuple[str, int]] = {}
    found: list[Occurrence] = []
    for record in inventory.archives:
        candidate_matches = [
            (index, entry)
            for index, entry in enumerate(record.entries)
            if entry.key == key
        ]
        if not candidate_matches:
            continue
        # Re-check the physical path and the complete entry-table snapshot at
        # use time.  A valid same-size replacement must not be interpreted
        # through the stale inventory table.
        _reject_link_components(record.physical_path, "Packed archive")
        verified_record = _resnapshot_record(record)
        matches = [
            (index, entry)
            for index, entry in enumerate(verified_record.entries)
            if entry.key == key
        ]
        try:
            archive_key = verified_record.relative_path.casefold()
            if archive_key not in physical_hashes:
                physical_hashes[archive_key] = dv2lib.hash_and_size_file(
                    verified_record.physical_path
                )
            physical_sha256, physical_size = physical_hashes[archive_key]
        except OSError as error:
            raise PackedInventoryError(
                f"cannot hash physical archive {record.relative_path}: {error}"
            ) from error
        if physical_size != verified_record.file_size:
            raise PackedInventoryError(
                f"physical archive changed while hashing: {record.relative_path}"
            )
        for index, entry in matches:
            logical_sha256, logical_size = _hash_logical_entry(
                verified_record, entry, maximum_size
            )
            found.append(
                Occurrence(
                    requested_logical_path=normalized,
                    physical_relative_path=verified_record.relative_path,
                    physical_path=verified_record.physical_path,
                    physical_file_size=physical_size,
                    physical_sha256=physical_sha256,
                    entry_index=index,
                    canonical_entry_path=entry.path,
                    storage_mode=entry.storage_mode,
                    stored_size=entry.stored_size,
                    logical_size=logical_size,
                    logical_sha256=logical_sha256,
                )
            )
    return tuple(found)


def _selected_path(path: str | os.PathLike) -> Path:
    selected = Path(path).absolute()
    _reject_link_components(selected, "selected DKS archive")
    if selected.name.casefold() != DKS_PATCH_FILE_NAME.casefold():
        raise PackedInventoryError(
            f"selected archive basename must be {DKS_PATCH_FILE_NAME!r}"
        )
    _require_regular_file(selected, "selected DKS archive")
    return selected


def select_dks_patch(
    path: str | os.PathLike,
    inventory: PackedInventory | None = None,
) -> SelectedDKS:
    """Open one selected DKS patch, whether inside or outside Packed."""

    selected = _selected_path(path)
    try:
        sha_before, size_before = dv2lib.hash_and_size_file(selected)
        session = dv2lib.DV2Session(selected)
        sha_after, size_after = dv2lib.hash_and_size_file(selected)
    except (dv2lib.DV2Error, OSError) as error:
        raise PackedInventoryError(f"cannot parse or hash selected DKS archive {selected}: {error}") from error
    if (
        sha_before != sha_after
        or size_before != size_after
        or session.file_size != size_after
    ):
        raise PackedInventoryError(
            f"selected DKS archive changed while hashing/parsing: {selected}"
        )

    relative: str | None = None
    inside = False
    if inventory is not None:
        if not isinstance(inventory, PackedInventory):
            raise PackedInventoryError("inventory must be a PackedInventory")
        try:
            relative = _relative_path(inventory.root, selected)
        except PackedInventoryError:
            relative = None
        else:
            inside = True
    return SelectedDKS(
        physical_path=selected,
        relative_path=relative,
        file_size=size_after,
        sha256=sha_after,
        header=session.header,
        entries=session.entries,
        entry_table_end=session.entry_table_end,
        inside_packed=inside,
    )


__all__ = [
    "ArchiveRecord",
    "DKS_PATCH_FILE_NAME",
    "FOV_PATCH_FILE_NAME",
    "InventoryError",
    "MAX_OCCURRENCE_LOGICAL_BYTES",
    "Occurrence",
    "PackedInventory",
    "PackedInventoryError",
    "ROOT_PATCH_FILE_NAME",
    "SelectedDKS",
    "find_occurrences",
    "scan_packed",
    "select_dks_patch",
]
