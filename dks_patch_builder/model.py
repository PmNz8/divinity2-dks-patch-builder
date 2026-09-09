"""Headless document model for the modular DKS Patch Builder.

The model owns user-visible document state and an ordered queue of immutable
archive plans.  It delegates package parsing/compilation, DV2 planning and all
serialization to the already accepted layers; this module contains no NIF,
texture, compression or archive writer implementation.
"""

# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
import os
from pathlib import Path
from dks_patch_builder import dv2lib

from .archive_factory import create_empty_dks_patch
from .handlers import HandlerRegistry, default_registry
from .inventory import DKS_PATCH_FILE_NAME, PackedInventory, SelectedDKS, scan_packed, select_dks_patch
from .package import load_asset_package
from .planner import CompiledResourcePlan, RemovalPlan, plan_compiled_resource, plan_remove_override
from .transaction import TransactionSaveResult, save_as_transaction, save_in_place_transaction


Plan = CompiledResourcePlan | RemovalPlan


class BuilderModelError(ValueError):
    """Raised when a document operation cannot be completed safely."""


@dataclass(frozen=True, slots=True)
class ArchiveEntryRow:
    path: str
    key: str
    storage_mode: str
    stored_size: int
    logical_size: int
    pending_action: str | None


@dataclass(frozen=True, slots=True)
class PendingChangeRow:
    order: int
    action: str
    target_logical_path: str
    target_key: str
    asset_type: str | None
    template_logical_path: str | None
    compiled_sha256: str | None
    compiled_size: int | None
    warnings: tuple[str, ...]
    warning_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class BuilderSnapshot:
    opened: bool
    packed_root: str | None
    selected_dks: str | None
    selected_sha256: str | None
    selected_size: int | None
    entry_count: int
    pending_count: int
    dirty: bool


@dataclass(frozen=True, slots=True)
class SaveOutcome:
    result: TransactionSaveResult
    selected_output: bool
    warnings: tuple[str, ...]


class DKSPatchBuilderModel:
    """Stateful, GUI-independent Builder document model."""

    def __init__(self, registry: HandlerRegistry | None = None) -> None:
        self._registry = registry or default_registry()
        self._inventory: PackedInventory | None = None
        self._selected: SelectedDKS | None = None
        self._expected_count: int | None = None
        self._pending: OrderedDict[str, Plan] = OrderedDict()

    @property
    def registry(self) -> HandlerRegistry:
        return self._registry

    @property
    def inventory(self) -> PackedInventory | None:
        return self._inventory

    @property
    def selected(self) -> SelectedDKS | None:
        return self._selected

    @property
    def has_pending_changes(self) -> bool:
        return bool(self._pending)

    def snapshot(self) -> BuilderSnapshot:
        if self._inventory is None or self._selected is None:
            return BuilderSnapshot(False, None, None, None, None, 0, 0, False)
        return BuilderSnapshot(
            opened=True,
            packed_root=str(self._inventory.root),
            selected_dks=str(self._selected.physical_path),
            selected_sha256=self._selected.sha256,
            selected_size=self._selected.file_size,
            entry_count=len(self._selected.entries),
            pending_count=len(self._pending),
            dirty=bool(self._pending),
        )

    def _require_open(self) -> tuple[PackedInventory, SelectedDKS]:
        if self._inventory is None or self._selected is None:
            raise BuilderModelError("no DKS Patch document is open")
        return self._inventory, self._selected

    def _guard_discard(self, discard_pending: bool) -> None:
        if self._pending and not discard_pending:
            raise BuilderModelError(
                "pending changes must be saved, cancelled, cleared, or explicitly discarded"
            )

    def open_archive(
        self,
        packed_root: str | os.PathLike,
        dks_path: str | os.PathLike,
        *,
        expected_count: int | None = None,
        discard_pending: bool = False,
    ) -> BuilderSnapshot:
        self._guard_discard(discard_pending)
        try:
            inventory = scan_packed(packed_root, expected_count=expected_count)
            selected = select_dks_patch(dks_path, inventory)
        except Exception as error:
            raise BuilderModelError(f"cannot open DKS Patch document: {error}") from error
        self._inventory = inventory
        self._selected = selected
        self._expected_count = expected_count
        self._pending.clear()
        return self.snapshot()

    def create_archive(
        self,
        packed_root: str | os.PathLike,
        dks_path: str | os.PathLike,
        *,
        expected_count: int | None = None,
        discard_pending: bool = False,
    ) -> BuilderSnapshot:
        self._guard_discard(discard_pending)
        try:
            # Validate the source corpus before performing the explicitly
            # requested creation.  Re-scan afterwards when the new archive is
            # inside Packed so the inventory cannot omit it.
            inventory = scan_packed(packed_root, expected_count=expected_count)
            created = create_empty_dks_patch(dks_path)
            output = created.output.absolute()
            try:
                output.relative_to(inventory.root)
            except ValueError:
                selected = select_dks_patch(output, inventory)
            else:
                adjusted_count = expected_count + 1 if expected_count is not None else None
                inventory = scan_packed(inventory.root, expected_count=adjusted_count)
                selected = select_dks_patch(output, inventory)
                expected_count = adjusted_count
        except Exception as error:
            raise BuilderModelError(f"cannot create DKS Patch document: {error}") from error
        self._inventory = inventory
        self._selected = selected
        self._expected_count = expected_count
        self._pending.clear()
        return self.snapshot()

    def close(self, *, discard_pending: bool = False) -> BuilderSnapshot:
        self._guard_discard(discard_pending)
        self._inventory = None
        self._selected = None
        self._expected_count = None
        self._pending.clear()
        return self.snapshot()

    def list_entries(self, substring: str | None = None) -> tuple[ArchiveEntryRow, ...]:
        _inventory, selected = self._require_open()
        if substring is not None and not isinstance(substring, str):
            raise BuilderModelError("entry filter must be text or null")
        query = (substring or "").casefold()
        rows: list[ArchiveEntryRow] = []
        for entry in selected.entries:
            if query and query not in entry.path.casefold():
                continue
            pending = self._pending.get(entry.key)
            rows.append(
                ArchiveEntryRow(
                    path=entry.path,
                    key=entry.key,
                    storage_mode=entry.storage_mode,
                    stored_size=entry.stored_size,
                    logical_size=entry.logical_size,
                    pending_action=pending.classification if pending is not None else None,
                )
            )
        return tuple(rows)

    @staticmethod
    def _pending_row(order: int, plan: Plan) -> PendingChangeRow:
        warnings = tuple(str(warning.message) for warning in plan.warnings)
        warning_codes = tuple(str(warning.code) for warning in plan.warnings)
        if isinstance(plan, CompiledResourcePlan):
            return PendingChangeRow(
                order=order,
                action=plan.classification,
                target_logical_path=plan.target_logical_path,
                target_key=plan.target_key,
                asset_type=plan.compiled.asset_type,
                template_logical_path=plan.template_logical_path,
                compiled_sha256=plan.compiled.compiled_sha256,
                compiled_size=plan.compiled.compiled_size,
                warnings=warnings,
                warning_codes=warning_codes,
            )
        return PendingChangeRow(
            order=order,
            action=plan.classification,
            target_logical_path=plan.target_logical_path,
            target_key=plan.target_key,
            asset_type=None,
            template_logical_path=None,
            compiled_sha256=None,
            compiled_size=None,
            warnings=warnings,
            warning_codes=warning_codes,
        )

    def pending_changes(self) -> tuple[PendingChangeRow, ...]:
        return tuple(
            self._pending_row(index, plan)
            for index, plan in enumerate(self._pending.values(), start=1)
        )

    def _queue(self, plan: Plan) -> PendingChangeRow:
        key = plan.target_key.casefold()
        if key in self._pending:
            raise BuilderModelError(
                f"a pending operation already targets {plan.target_logical_path!r}; cancel it first"
            )
        self._pending[key] = plan
        return self._pending_row(len(self._pending), plan)

    def import_package(self, package_directory: str | os.PathLike) -> PendingChangeRow:
        inventory, selected = self._require_open()
        try:
            package = load_asset_package(package_directory)
            key = package.target_logical_path.casefold()
            if key in self._pending:
                raise BuilderModelError(
                    f"a pending operation already targets {package.target_logical_path!r}; cancel it first"
                )
            compiled = self._registry.compile(package)
            plan = plan_compiled_resource(inventory, selected, compiled)
            return self._queue(plan)
        except BuilderModelError:
            raise
        except Exception as error:
            raise BuilderModelError(f"cannot import asset package: {error}") from error

    def remove_override(self, logical_path: str) -> PendingChangeRow:
        inventory, selected = self._require_open()
        try:
            normalized = dv2lib.normalize_archive_path(logical_path)
            if normalized.casefold() in self._pending:
                raise BuilderModelError(
                    f"a pending operation already targets {normalized!r}; cancel it first"
                )
            return self._queue(plan_remove_override(inventory, selected, normalized))
        except BuilderModelError:
            raise
        except Exception as error:
            raise BuilderModelError(f"cannot remove DKS override: {error}") from error

    def cancel(self, logical_path: str) -> PendingChangeRow:
        try:
            key = dv2lib.normalize_archive_path(logical_path).casefold()
        except Exception as error:
            raise BuilderModelError(f"cannot cancel pending operation: {error}") from error
        plan = self._pending.pop(key, None)
        if plan is None:
            raise BuilderModelError(f"no pending operation targets {logical_path!r}")
        return self._pending_row(0, plan)

    def clear_pending(self) -> int:
        count = len(self._pending)
        self._pending.clear()
        return count

    def _plan_tuple(self) -> tuple[Plan, ...]:
        self._require_open()
        if not self._pending:
            raise BuilderModelError("there are no pending changes to save")
        return tuple(self._pending.values())

    def _refresh_selected(self, selected_path: Path, *, archive_added: bool = False) -> None:
        inventory, _old_selected = self._require_open()
        try:
            selected_path.absolute().relative_to(inventory.root)
        except ValueError:
            selected = select_dks_patch(selected_path, inventory)
        else:
            expected_count = self._expected_count
            if archive_added and expected_count is not None:
                expected_count += 1
            inventory = scan_packed(inventory.root, expected_count=expected_count)
            selected = select_dks_patch(selected_path, inventory)
            self._expected_count = expected_count
        self._inventory = inventory
        self._selected = selected

    def save_in_place(self) -> SaveOutcome:
        plans = self._plan_tuple()
        try:
            result = save_in_place_transaction(plans)
        except Exception as error:
            raise BuilderModelError(f"cannot save DKS Patch in place: {error}") from error
        self._pending.clear()
        try:
            self._refresh_selected(result.output_path)
        except Exception as error:
            self._inventory = None
            self._selected = None
            self._expected_count = None
            raise BuilderModelError(
                "DKS Patch was saved successfully but the refreshed document could not be reopened"
            ) from error
        return SaveOutcome(result=result, selected_output=True, warnings=())

    def save_as(self, output_path: str | os.PathLike) -> SaveOutcome:
        plans = self._plan_tuple()
        try:
            result = save_as_transaction(plans, output_path)
        except Exception as error:
            raise BuilderModelError(f"cannot save DKS Patch copy: {error}") from error

        if result.output_path.name.casefold() != DKS_PATCH_FILE_NAME.casefold():
            inventory, selected = self._require_open()
            try:
                result.output_path.absolute().relative_to(inventory.root)
            except ValueError:
                pass
            else:
                expected_count = self._expected_count
                if expected_count is not None:
                    expected_count += 1
                try:
                    refreshed = scan_packed(inventory.root, expected_count=expected_count)
                    refreshed_selected = select_dks_patch(
                        selected.physical_path,
                        refreshed,
                    )
                except Exception as error:
                    raise BuilderModelError(
                        "DKS Patch copy was saved successfully inside Packed, but the corpus could not be refreshed"
                    ) from error
                self._inventory = refreshed
                self._selected = refreshed_selected
                self._expected_count = expected_count
            return SaveOutcome(
                result=result,
                selected_output=False,
                warnings=(
                    "The copy was saved, but its unusual filename was not selected as the active DKS Patch; pending changes remain.",
                ),
            )

        try:
            inventory, _selected = self._require_open()
            try:
                result.output_path.absolute().relative_to(inventory.root)
            except ValueError:
                archive_added = False
            else:
                # Save As publishes exclusively to a previously absent path.
                archive_added = True
            self._refresh_selected(result.output_path, archive_added=archive_added)
        except Exception as error:
            raise BuilderModelError(
                "DKS Patch copy was saved successfully but could not be selected; reopen it explicitly"
            ) from error
        self._pending.clear()
        return SaveOutcome(result=result, selected_output=True, warnings=())


__all__ = [
    "ArchiveEntryRow",
    "BuilderModelError",
    "BuilderSnapshot",
    "DKSPatchBuilderModel",
    "PendingChangeRow",
    "SaveOutcome",
]
