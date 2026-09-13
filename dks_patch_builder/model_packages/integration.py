# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only
"""Atomic model-package groups; existing Builder remains the archive writer."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..inventory import PackedInventory, SelectedDKS
from ..package import _reject_link_components
from ..planner import CompiledResourcePlan, plan_compiled_resource
from .reader import ModelPackage, ModelPackageError, read_model_package
from .sources import ModelSourceAudit, audit_model_sources


def require_external(path: str | Path, root: Path) -> None:
    path=Path(path).absolute()
    if any(p.name.rstrip(' .') != p.name for p in (path, *path.parents)):
        raise ModelPackageError('Ambiguous trailing-space/dot model output path')
    _reject_link_components(path if path.exists() or path.is_symlink() else path.parent,'model DKS output')
    resolved=path.resolve()
    if resolved.is_relative_to(root.resolve()) or any(p.name.casefold()=='packed' for p in (resolved,*resolved.parents)):
        raise ModelPackageError('Model-package DKS outputs must stay outside Packed; create/open an external DKS_Patch.dv2')


@dataclass(frozen=True)
class ModelGroup:
    package: ModelPackage
    plans: tuple[CompiledResourcePlan, ...]
    audit: ModelSourceAudit | None

    @property
    def keys(self) -> frozenset[str]:
        return frozenset(p.target_key.casefold() for p in self.plans)


class ModelPackageImports:
    """Module-owned group audit state; no direct mutation of the document queue."""

    def __init__(self) -> None:
        self._groups: list[ModelGroup]=[]

    def clear(self) -> None:
        self._groups.clear()

    @property
    def active(self) -> bool:
        return bool(self._groups)

    def prepare(self,path,inventory: PackedInventory,selected: SelectedDKS,pending) -> ModelGroup:
        package=read_model_package(path)
        if not package.changed: return ModelGroup(package,(),None)
        require_external(selected.physical_path,inventory.root)
        keys={r.logical_path.casefold() for r in package.changed}
        if keys.intersection(pending):
            raise ModelPackageError('Model package overlaps pending targets; cancel the conflicting group/operation first')
        audit=audit_model_sources(inventory,package)
        plans=tuple(plan_compiled_resource(inventory,selected,r.compiled) for r in package.changed)
        if any(p.classification=='ADD_NEW' for p in plans):
            raise ModelPackageError('Model import cannot introduce unbound new logical paths')
        return ModelGroup(package,plans,audit)

    def add(self,group: ModelGroup) -> None:
        if group.plans:self._groups.append(group)

    def group_for(self,key: str) -> ModelGroup | None:
        return next((g for g in self._groups if key.casefold() in g.keys),None)

    def remove(self,group: ModelGroup) -> None:
        self._groups.remove(group)

    def warnings_for(self,key: str) -> tuple[str,...]:
        group=self.group_for(key)
        if not group:return ()
        return (*group.package.warnings,
                *(group.audit.warnings if group.audit else ()),
                f'Model group: {group.package.path.name}; canceling any member cancels all {len(group.plans)} pending resources.')

    def recheck(self,pending) -> None:
        for group in self._groups:
            if any(pending.get(p.target_key.casefold()) is not p for p in group.plans) or group.audit is None:
                raise ModelPackageError('Incomplete or replaced model-package group; cancel and re-import')
            group.audit.recheck()
