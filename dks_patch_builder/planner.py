"""Read-only DKS operation planning and in-memory staging.

Planning records what would happen to one selected DKS patch.  Staging only
uses :class:`DV2Session`'s existing in-memory edit API; this module never
saves an archive and never makes a precedence claim.
"""

# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Final

from dks_patch_builder import dv2lib

from .handlers.base import CompiledResource
from .inventory import (
    ArchiveRecord,
    Occurrence,
    PackedInventory,
    PackedInventoryError,
    SelectedDKS,
    find_occurrences,
    select_dks_patch,
)


REPLACE: Final = "REPLACE"
ADD_OVERRIDE: Final = "ADD_OVERRIDE"
ADD_NEW: Final = "ADD_NEW"
REMOVE_OVERRIDE: Final = "REMOVE_OVERRIDE"


class PlannerError(ValueError):
    """Raised when an operation cannot be safely planned or staged."""


@dataclass(frozen=True, slots=True)
class PlanWarning:
    """A deterministic informational warning attached to an operation plan."""

    code: str
    message: str
    paths: tuple[str, ...] = ()

    def __str__(self) -> str:
        return self.message


@dataclass(frozen=True, slots=True)
class CompiledResourcePlan:
    """Immutable classification and evidence for one compiled resource."""

    classification: str
    operation: str
    target_logical_path: str
    target_key: str
    template_logical_path: str
    selected_dks: SelectedDKS
    compiled: CompiledResource
    storage_mode: str
    selected_entry: dv2lib.DV2Entry | None
    target_occurrences: tuple[Occurrence, ...]
    template_occurrences: tuple[Occurrence, ...]
    root_special_records: tuple[ArchiveRecord, ...]
    warnings: tuple[PlanWarning, ...]

    @property
    def action(self) -> str:
        return self.classification

    @property
    def resource(self) -> CompiledResource:
        return self.compiled

    @property
    def selected_dks_sha256(self) -> str:
        return self.selected_dks.sha256

    @property
    def selected_dks_size(self) -> int:
        return self.selected_dks.file_size

    @property
    def target_storage_mode(self) -> str:
        return self.storage_mode

    @property
    def warning_codes(self) -> tuple[str, ...]:
        return tuple(warning.code for warning in self.warnings)

    @property
    def warning_messages(self) -> tuple[str, ...]:
        return tuple(warning.message for warning in self.warnings)


@dataclass(frozen=True, slots=True)
class RemovalPlan:
    """Immutable evidence and identity binding for one DKS entry removal."""

    classification: str
    operation: str
    target_logical_path: str
    target_key: str
    selected_dks: SelectedDKS
    selected_entry: dv2lib.DV2Entry
    target_occurrences: tuple[Occurrence, ...]
    root_special_records: tuple[ArchiveRecord, ...]
    warnings: tuple[PlanWarning, ...]

    @property
    def action(self) -> str:
        return self.classification

    @property
    def selected_dks_sha256(self) -> str:
        return self.selected_dks.sha256

    @property
    def selected_dks_size(self) -> int:
        return self.selected_dks.file_size

    @property
    def warning_codes(self) -> tuple[str, ...]:
        return tuple(warning.code for warning in self.warnings)


def _normalise_logical_path(path: str) -> str:
    try:
        return dv2lib.normalize_archive_path(path)
    except (dv2lib.DV2Error, TypeError) as error:
        raise PlannerError(f"unsafe logical archive path: {path!r}") from error


def _require_inventory(inventory: PackedInventory) -> PackedInventory:
    if not isinstance(inventory, PackedInventory):
        raise PlannerError("operation planning requires a PackedInventory")
    return inventory


def _require_selected(
    inventory: PackedInventory,
    selected_dks: SelectedDKS | str | os.PathLike,
) -> SelectedDKS:
    if isinstance(selected_dks, SelectedDKS):
        return selected_dks
    try:
        return select_dks_patch(selected_dks, inventory)
    except PackedInventoryError as error:
        raise PlannerError(str(error)) from error


def _entry_for_key(entries: tuple[dv2lib.DV2Entry, ...], key: str) -> dv2lib.DV2Entry | None:
    for entry in entries:
        if entry.key == key:
            return entry
    return None


def _same_path(left: Path, right: Path) -> bool:
    return left.absolute().as_posix().casefold() == right.absolute().as_posix().casefold()


def _multiple_warning(code: str, label: str, occurrences: tuple[Occurrence, ...]) -> PlanWarning | None:
    if len(occurrences) <= 1:
        return None
    paths = tuple(
        sorted(
            (occurrence.physical_relative_path for occurrence in occurrences),
            key=lambda value: (value.casefold(), value),
        )
    )
    return PlanWarning(
        code=code,
        message=f"multiple {label} occurrences found in Packed: {', '.join(paths)}",
        paths=paths,
    )


def _active_root_warning(
    inventory: PackedInventory,
    selected: SelectedDKS,
) -> PlanWarning | None:
    active = inventory.root_dks_patch
    if active is None or _same_path(active.physical_path, selected.physical_path):
        return None
    return PlanWarning(
        code="active_root_dks_differs",
        message=(
            "selected DKS_Patch.dv2 differs from the root-level Packed "
            f"DKS_Patch.dv2 ({active.relative_path})"
        ),
        paths=(active.relative_path, str(selected.relative_path or selected.physical_path)),
    )


def _template_warnings(
    compiled: CompiledResource,
    occurrences: tuple[Occurrence, ...],
) -> list[PlanWarning]:
    warnings: list[PlanWarning] = []
    if not occurrences:
        warnings.append(
            PlanWarning(
                code="template_not_found",
                message=(
                    "template logical path was not found in Packed: "
                    f"{compiled.template_logical_path}"
                ),
            )
        )
        return warnings
    mismatches = tuple(
        sorted(
            (
                occurrence.physical_relative_path
                for occurrence in occurrences
                if occurrence.logical_size != compiled.template_size
                or occurrence.logical_sha256.casefold() != compiled.template_sha256.casefold()
            ),
            key=lambda value: (value.casefold(), value),
        )
    )
    if mismatches:
        warnings.append(
            PlanWarning(
                code="template_hash_mismatch",
                message=(
                    "template occurrence hash/size differs from the compiled "
                    f"template in: {', '.join(mismatches)}"
                ),
                paths=mismatches,
            )
        )
    return warnings


def plan_compiled_resource(
    inventory: PackedInventory,
    selected_dks: SelectedDKS | str | os.PathLike,
    compiled: CompiledResource,
) -> CompiledResourcePlan:
    """Classify a compiled resource without writing an archive."""

    inventory = _require_inventory(inventory)
    if not isinstance(compiled, CompiledResource):
        raise PlannerError("compiled resource must be a CompiledResource")
    try:
        target = _normalise_logical_path(compiled.target_logical_path)
        template = _normalise_logical_path(compiled.template_logical_path)
    except PlannerError:
        raise
    selected = _require_selected(inventory, selected_dks)
    target_key = target.casefold()
    selected_entry = _entry_for_key(selected.entries, target_key)
    target_occurrences = find_occurrences(inventory, target)
    template_occurrences = (
        target_occurrences
        if template.casefold() == target_key
        else find_occurrences(inventory, template)
    )

    if selected_entry is not None:
        classification = REPLACE
        storage_mode = selected_entry.storage_mode
    elif target_occurrences:
        classification = ADD_OVERRIDE
        storage_mode = compiled.preferred_storage_mode
    else:
        classification = ADD_NEW
        storage_mode = compiled.preferred_storage_mode

    warnings: list[PlanWarning] = []
    target_warning = _multiple_warning(
        "multiple_target_occurrences", "target", target_occurrences
    )
    if target_warning is not None:
        warnings.append(target_warning)
    template_warning = _multiple_warning(
        "multiple_template_occurrences", "template", template_occurrences
    )
    if template_warning is not None:
        warnings.append(template_warning)
    warnings.extend(_template_warnings(compiled, template_occurrences))
    active_warning = _active_root_warning(inventory, selected)
    if active_warning is not None:
        warnings.append(active_warning)
    if classification == ADD_NEW:
        warnings.append(
            PlanWarning(
                code="add_new_no_existing_occurrence",
                message=(
                    "ADD_NEW target has no existing matching logical payload "
                    "occurrence in the scanned Packed inventory"
                ),
            )
        )

    return CompiledResourcePlan(
        classification=classification,
        operation=classification,
        target_logical_path=target,
        target_key=target_key,
        template_logical_path=template,
        selected_dks=selected,
        compiled=compiled,
        storage_mode=storage_mode,
        selected_entry=selected_entry,
        target_occurrences=target_occurrences,
        template_occurrences=template_occurrences,
        root_special_records=inventory.root_special_records,
        warnings=tuple(warnings),
    )


def plan_remove_override(
    inventory: PackedInventory,
    selected_dks: SelectedDKS | str | os.PathLike,
    logical_path: str,
) -> RemovalPlan:
    """Plan removing one existing entry from the selected DKS patch."""

    inventory = _require_inventory(inventory)
    selected = _require_selected(inventory, selected_dks)
    target = _normalise_logical_path(logical_path)
    target_key = target.casefold()
    selected_entry = _entry_for_key(selected.entries, target_key)
    if selected_entry is None:
        raise PlannerError(
            f"cannot plan REMOVE_OVERRIDE: selected DKS has no entry {target!r}"
        )
    target_occurrences = find_occurrences(inventory, target)
    warnings: list[PlanWarning] = []
    target_warning = _multiple_warning(
        "multiple_target_occurrences", "target", target_occurrences
    )
    if target_warning is not None:
        warnings.append(target_warning)
    active_warning = _active_root_warning(inventory, selected)
    if active_warning is not None:
        warnings.append(active_warning)
    return RemovalPlan(
        classification=REMOVE_OVERRIDE,
        operation=REMOVE_OVERRIDE,
        target_logical_path=selected_entry.path,
        target_key=target_key,
        selected_dks=selected,
        selected_entry=selected_entry,
        target_occurrences=target_occurrences,
        root_special_records=inventory.root_special_records,
        warnings=tuple(warnings),
    )


def _bound_session(selected: SelectedDKS) -> dv2lib.DV2Session:
    try:
        current = select_dks_patch(selected.physical_path)
    except PackedInventoryError as error:
        raise PlannerError(str(error)) from error
    if current.file_size != selected.file_size or current.sha256 != selected.sha256:
        raise PlannerError(
            "selected DKS changed since planning; refusing to stage against a stale archive"
        )
    try:
        return dv2lib.DV2Session(selected.physical_path)
    except (dv2lib.DV2Error, OSError) as error:
        raise PlannerError(f"cannot reopen selected DKS for staging: {error}") from error


def _assert_one_pending(session: dv2lib.DV2Session, target_key: str) -> None:
    pending = session.pending_ops()
    if len(pending) != 1 or pending[0].key != target_key:
        raise PlannerError("staging produced an unexpected pending-operation set")


def stage_compiled_plan(plan: CompiledResourcePlan) -> dv2lib.DV2Session:
    """Reopen a bound DKS and stage exactly one add/replace in memory."""

    if not isinstance(plan, CompiledResourcePlan):
        raise PlannerError("stage_compiled_plan requires a CompiledResourcePlan")
    session = _bound_session(plan.selected_dks)
    current_entry = _entry_for_key(session.entries, plan.target_key)
    if plan.classification == REPLACE:
        if current_entry is None:
            raise PlannerError("planned REPLACE target no longer exists in selected DKS")
        try:
            session.stage_set(current_entry.path, plan.compiled.compiled_payload)
        except dv2lib.DV2Error as error:
            raise PlannerError(f"cannot stage planned replacement: {error}") from error
    elif plan.classification in (ADD_OVERRIDE, ADD_NEW):
        if current_entry is not None:
            raise PlannerError("planned add target now exists in selected DKS")
        try:
            session.stage_add(
                plan.target_logical_path,
                plan.compiled.compiled_payload,
                plan.storage_mode,
            )
        except dv2lib.DV2Error as error:
            raise PlannerError(f"cannot stage planned addition: {error}") from error
    else:  # pragma: no cover - immutable plan constructors only expose known values
        raise PlannerError(f"unsupported compiled plan classification: {plan.classification!r}")
    _assert_one_pending(session, plan.target_key)
    return session


def stage_remove_plan(plan: RemovalPlan) -> dv2lib.DV2Session:
    """Reopen a bound DKS and stage exactly one removal in memory."""

    if not isinstance(plan, RemovalPlan):
        raise PlannerError("stage_remove_plan requires a RemovalPlan")
    session = _bound_session(plan.selected_dks)
    current_entry = _entry_for_key(session.entries, plan.target_key)
    if current_entry is None:
        raise PlannerError("planned REMOVE_OVERRIDE target no longer exists in selected DKS")
    try:
        session.stage_remove(current_entry.path)
    except dv2lib.DV2Error as error:
        raise PlannerError(f"cannot stage planned removal: {error}") from error
    _assert_one_pending(session, plan.target_key)
    return session


# Explicit aliases keep the API discoverable without changing operation names.
plan_remove = plan_remove_override
stage_remove_override = stage_remove_plan


__all__ = [
    "ADD_NEW",
    "ADD_OVERRIDE",
    "CompiledResourcePlan",
    "PlanWarning",
    "PlannerError",
    "REPLACE",
    "REMOVE_OVERRIDE",
    "RemovalPlan",
    "plan_compiled_resource",
    "plan_remove",
    "plan_remove_override",
    "stage_compiled_plan",
    "stage_remove_override",
    "stage_remove_plan",
]
