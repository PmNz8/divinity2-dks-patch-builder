# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only
"""Exact package-source binding; no guessed effective archive precedence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..inventory import PackedInventory, Occurrence, scan_packed, find_occurrences
from ..package import _reject_link_components
from .reader import ModelPackage, ModelPackageError


def _snapshot(inventory: PackedInventory) -> tuple:
    rows=[]
    for archive in inventory.archives:
        _reject_link_components(archive.physical_path,'model source archive')
        info=archive.physical_path.stat()
        rows.append((archive.relative_path.casefold(),info.st_size,info.st_mtime_ns,info.st_dev,info.st_ino))
    return tuple(sorted(rows))


def _table(inventory: PackedInventory) -> tuple:
    return tuple((r.relative_path.casefold(),r.file_size,r.header,r.entries,r.entry_table_end) for r in inventory.archives)


@dataclass(frozen=True)
class ModelSourceAudit:
    root: Path
    archive_snapshot: tuple
    occurrences: tuple[tuple[str, tuple[Occurrence, ...]], ...]
    warnings: tuple[str, ...] = ()

    def recheck(self) -> None:
        fresh=scan_packed(self.root)
        if _snapshot(fresh)!=self.archive_snapshot:
            raise ModelPackageError('Packed archive set/metadata changed; cancel and re-import the model package')
        for logical,expected in self.occurrences:
            if find_occurrences(fresh,logical)!=expected:
                raise ModelPackageError('Model source bytes or occurrences changed: '+logical)
        if _snapshot(fresh)!=self.archive_snapshot:
            raise ModelPackageError('Model sources changed during recheck')


def audit_model_sources(inventory: PackedInventory, package: ModelPackage) -> ModelSourceAudit:
    """Check every packaged source, including unchanged authoring dependencies.

    Complete entry inventory + metadata continuity; exact hashes for all used
    physical archives and logical payloads. Not a full pristine-game audit.
    """
    fresh=scan_packed(inventory.root)
    if _table(fresh)!=_table(inventory):
        raise ModelPackageError('Packed inventory changed; reopen the Builder document')
    snapshot=_snapshot(fresh); evidence=[]; warnings=[]
    for resource in package.resources:
        found=find_occurrences(fresh,resource.logical_path)
        matches=[o for o in found if o.physical_relative_path.replace('/','\\').casefold()==resource.archive_name.casefold()]
        if len(matches)!=1:
            raise ModelPackageError('Missing/ambiguous recorded physical source: '+resource.archive_name+': '+resource.logical_path)
        original=matches[0]
        if (original.physical_sha256!=resource.archive_sha256 or
            original.logical_sha256!=resource.original_sha256 or original.logical_size!=resource.original_size):
            raise ModelPackageError('Recorded source archive/payload differs from Packed: '+resource.logical_path)
        if any(o.logical_sha256!=resource.original_sha256 or o.logical_size!=resource.original_size for o in found):
            variants=', '.join(o.physical_relative_path for o in found)
            warnings.append('Different same-path source variants: '+resource.logical_path+
                            ' ['+variants+']. Using the complete package payload based on verified source '+
                            resource.archive_name+'; original archive precedence is not assumed.')
        evidence.append((resource.logical_path,found))
    if _snapshot(fresh)!=snapshot:
        raise ModelPackageError('Model sources changed while auditing')
    return ModelSourceAudit(fresh.root,snapshot,tuple(evidence),tuple(warnings))
