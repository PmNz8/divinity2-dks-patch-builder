# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only
"""Read-only exact-source audit shared by the fixed FoV narrative tools.

No installation, original-archive writer or source auto-repair is provided.
The initial audit hashes every original and builds the complete resource index.
Rechecks use path/size/mtime/identity continuity plus exact used-source hashes;
they deliberately do not claim a fresh full-corpus byte proof.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import stat
from typing import Callable

from .dv2lib import DV2Session
from .narrative_profile_data import PROFILE


class NarrativeSourceError(ValueError):
    pass


@dataclass(frozen=True)
class ArchiveSnapshot:
    relative_path: str
    size: int
    mtime_ns: int
    device: int
    inode: int
    sha256: str
    entries: tuple


@dataclass(frozen=True)
class SourcePayload:
    archive: str
    logical_path: str
    sha256: str
    payload: bytes


@dataclass(frozen=True)
class SourceAudit:
    root: Path
    archives: tuple[ArchiveSnapshot, ...]
    payloads: tuple[SourcePayload, ...]
    profile_id: str

    def payload(self, archive: str, logical_path: str) -> bytes:
        for row in self.payloads:
            if row.archive.casefold() == archive.casefold() and row.logical_path.casefold() == logical_path.casefold():
                return row.payload
        raise NarrativeSourceError(f"unrecognized source payload: {archive}: {logical_path}")


def reject_links(path: Path) -> None:
    """Check every existing component, including Windows junctions."""
    path = path.absolute()
    for component in reversed((path, *path.parents)):
        if component.name and (component.name.rstrip(' .') != component.name or any(c in component.name for c in '<>:"|?*')):
            raise NarrativeSourceError(f'ambiguous Windows path component: {component}')
        info = component.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise NarrativeSourceError(f"symlink/reparse path is unsupported: {component}")


def _metadata(path: Path) -> tuple[int, int, int, int]:
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
        raise NarrativeSourceError(f"source must be a regular non-link file: {path}")
    return info.st_size, info.st_mtime_ns, info.st_dev, info.st_ino


def archive_paths(root: Path) -> dict[str, Path]:
    root = root.absolute()
    reject_links(root)
    if not root.is_dir():
        raise NarrativeSourceError("choose the complete supported Packed directory")
    result: dict[str, Path] = {}
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in (*dirs, *files):
            child = Path(directory) / name
            info = child.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise NarrativeSourceError(f"Packed tree contains a link/reparse point: {child}")
        for name in files:
            if not name.casefold().endswith('.dv2'):
                continue
            path = Path(directory) / name
            key = path.relative_to(root).as_posix().casefold()
            if key in result:
                raise NarrativeSourceError(f"duplicate normalized archive: {key}")
            _metadata(path)
            result[key] = path
    return result


def file_hash(path: Path) -> str:
    before = _metadata(path)
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            digest.update(chunk)
    if _metadata(path) != before:
        raise NarrativeSourceError(f"source changed while hashing: {path}")
    return digest.hexdigest()


def audit_sources(root: str | os.PathLike, progress: Callable[[str], None] | None = None) -> SourceAudit:
    root = Path(root).absolute()
    paths = archive_paths(root)
    expected = {row['path'].replace('\\', '/').casefold(): row for row in PROFILE['archives']}
    if set(paths) != set(expected):
        missing = sorted(set(expected) - set(paths))
        extra = sorted(set(paths) - set(expected))
        raise NarrativeSourceError(f"requires pristine supported Packed corpus; missing={missing[:5]}, unexpected={extra[:5]}. Unknown overlays are not accepted.")
    snapshots = []
    for index, (key, record) in enumerate(expected.items(), 1):
        path = paths[key]
        before = _metadata(path)
        if before[0] != record['size']:
            raise NarrativeSourceError(f"original archive size mismatch: {record['path']}")
        if progress:
            progress(f"Checking original archives {index}/{len(expected)}: {record['path']}")
        digest = file_hash(path)
        if digest != record['sha256']:
            raise NarrativeSourceError(f"original archive SHA-256 mismatch: {record['path']}")
        session = DV2Session(path)
        if len(session.entries) != record['entries']:
            raise NarrativeSourceError(f"original archive entry count mismatch: {record['path']}")
        entries = tuple(session.entries)
        if len({entry.key for entry in entries}) != len(entries):
            raise NarrativeSourceError(f"duplicate logical paths: {record['path']}")
        if _metadata(path) != before:
            raise NarrativeSourceError(f"source changed during indexing: {record['path']}")
        snapshots.append(ArchiveSnapshot(record['path'], *before, digest, entries))
    payloads = []
    for resource in PROFILE['resources']:
        logical = resource['logical_path']
        found = [(row, entry) for row in snapshots for entry in row.entries if entry.key == logical.casefold()]
        accepted = {row['archive'].casefold(): row for row in resource['occurrences']}
        if {row.relative_path.casefold() for row, _entry in found} != set(accepted) or len(found) != len(accepted):
            raise NarrativeSourceError(f"source occurrence set mismatch: {logical}")
        for row, entry in found:
            source = accepted[row.relative_path.casefold()]
            data = DV2Session(paths[row.relative_path.replace('\\', '/').casefold()]).read_entry_bytes(entry.path)
            digest = hashlib.sha256(data).hexdigest()
            if len(data) != source['size'] or digest != source['sha256']:
                raise NarrativeSourceError(f"source payload mismatch: {row.relative_path}: {logical}")
            payloads.append(SourcePayload(row.relative_path, logical, digest, data))
    audit = SourceAudit(root, tuple(snapshots), tuple(payloads), PROFILE['profile_id'])
    recheck_sources(audit)
    return audit


def recheck_sources(audit: SourceAudit, *, full: bool = False) -> None:
    """Metadata continuity + used-source hashes; full=True hashes all originals."""
    if audit.profile_id != PROFILE['profile_id']:
        raise NarrativeSourceError('unsupported source audit profile')
    paths = archive_paths(audit.root)
    expected = {row.relative_path.replace('\\', '/').casefold(): row for row in audit.archives}
    if set(paths) != set(expected):
        raise NarrativeSourceError('original path set changed; start a fresh source audit')
    used = {row.archive.casefold() for row in audit.payloads}
    for key, row in expected.items():
        if _metadata(paths[key]) != (row.size, row.mtime_ns, row.device, row.inode):
            raise NarrativeSourceError(f'original metadata changed: {row.relative_path}; start a fresh source audit')
        if full or row.relative_path.casefold() in used:
            if file_hash(paths[key]) != row.sha256:
                raise NarrativeSourceError(f'original bytes changed: {row.relative_path}')


def require_external_output(path: str | os.PathLike, packed_root: Path) -> Path:
    """No output inside Packed, another Packed tree, or a symlink/reparse path."""
    output = Path(path).absolute()
    if not output.name or output.name.rstrip(' .') != output.name or any(c in output.name for c in '<>:"|?*'):
        raise NarrativeSourceError('ambiguous output filename')
    parent = output.parent
    reject_links(parent)
    root = packed_root.resolve()
    resolved = output.resolve()
    if resolved == root or root in resolved.parents or any(p.name.casefold() == 'packed' for p in (resolved, *resolved.parents)):
        raise NarrativeSourceError('narrative outputs must stay outside game Packed directories')
    if output.exists() or output.is_symlink():
        raise NarrativeSourceError(f'output already exists: {output}')
    return output


__all__ = ['PROFILE', 'NarrativeSourceError', 'SourceAudit', 'SourcePayload', 'ArchiveSnapshot',
           'audit_sources', 'recheck_sources', 'archive_paths', 'file_hash', 'reject_links', 'require_external_output']
