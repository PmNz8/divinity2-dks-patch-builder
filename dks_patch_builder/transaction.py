"""Central, guarded transactions for DKS Patch Builder.

This module deliberately sits above the DV2 backend.  It binds one selected
``DKS_Patch.dv2`` identity, stages a user-ordered set of operations in one
session, and independently checks a rebuilt candidate before publication.
The backend remains responsible for DV2 parsing and serialization; this
module does not duplicate any texture, NIF, or compression logic.
"""

# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import os
from pathlib import Path
import stat
import uuid
from types import MappingProxyType
from typing import Final, Iterable, Mapping, Sequence

from dks_patch_builder import dv2lib

from .handlers.base import CompiledResource
from .inventory import DKS_PATCH_FILE_NAME, SelectedDKS
from .planner import (
    ADD_NEW,
    ADD_OVERRIDE,
    REPLACE,
    REMOVE_OVERRIDE,
    CompiledResourcePlan,
    RemovalPlan,
)


_REPARSE_POINT: Final = 0x400
_HEADER_FIELDS: Final = (
    "version",
    "unknown_04",
    "unknown_08",
    "layout_mode",
    "compression_mode",
)


class TransactionError(ValueError):
    """Raised when a transaction cannot be safely staged or published."""


class CandidateVerificationError(TransactionError):
    """Raised when a candidate fails the independent transaction allowlist."""


Plan = CompiledResourcePlan | RemovalPlan


@dataclass(frozen=True, slots=True)
class PendingOperationSnapshot:
    """Immutable view of one backend pending operation."""

    kind: str
    path: str
    key: str
    storage: str | None

    @property
    def storage_mode(self) -> str | None:
        return self.storage


@dataclass(frozen=True, slots=True)
class StagedTransaction:
    """A staged transaction and its immutable identity/report snapshot.

    ``session`` is intentionally exposed as the owned in-memory DV2 session
    which will later be saved by one of the guarded save functions.  All
    report-facing operation data is copied into immutable tuples so callers do
    not need to inspect mutable backend ``PendingOp`` objects.
    """

    session: dv2lib.DV2Session = field(repr=False, compare=False)
    plans: tuple[Plan, ...]
    source_path: Path
    source_sha256: str
    source_size: int
    pending_ops: tuple[PendingOperationSnapshot, ...]
    operation_order: tuple[str, ...]
    added: tuple[str, ...]
    replaced: tuple[str, ...]
    removed: tuple[str, ...]

    @property
    def selected_dks_sha256(self) -> str:
        return self.source_sha256

    @property
    def selected_dks_size(self) -> int:
        return self.source_size

    @property
    def pending_operation_set(self) -> frozenset[tuple[str, str, str | None]]:
        return frozenset(
            (operation.kind, operation.key, operation.storage)
            for operation in self.pending_ops
        )

    @property
    def report(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "status": "STAGED",
                "mode": "staged",
                "source": str(self.source_path),
                "source_sha256": self.source_sha256,
                "source_size": self.source_size,
                "operation_order": self.operation_order,
                "added": self.added,
                "replaced": self.replaced,
                "removed": self.removed,
                "pending_ops": self.pending_ops,
                "entry_count": len(self.session.entries),
                "write_performed": False,
            }
        )


@dataclass(frozen=True, slots=True)
class CandidateVerification:
    """Independent allowlist verification result for one candidate archive."""

    source_path: Path
    output_path: Path
    source_sha256: str
    source_size: int
    output_sha256: str
    output_size: int
    entry_count: int
    added: tuple[str, ...]
    replaced: tuple[str, ...]
    removed: tuple[str, ...]
    verification_facts: tuple[str, ...]

    @property
    def source_output_same_bytes(self) -> bool:
        return (
            self.source_sha256 == self.output_sha256
            and self.source_size == self.output_size
        )

    @property
    def report(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "status": "OK",
                "source": str(self.source_path),
                "output": str(self.output_path),
                "source_sha256": self.source_sha256,
                "source_size": self.source_size,
                "output_sha256": self.output_sha256,
                "output_size": self.output_size,
                "entry_count": self.entry_count,
                "added": self.added,
                "replaced": self.replaced,
                "removed": self.removed,
                "verification_facts": self.verification_facts,
            }
        )


@dataclass(frozen=True, slots=True)
class TransactionSaveResult:
    """Immutable result of Save As or guarded in-place Save."""

    mode: str
    source_path: Path
    output_path: Path
    backup_path: Path | None
    source_sha256: str
    source_size: int
    output_sha256: str
    output_size: int
    backup_sha256: str | None
    backup_size: int | None
    entry_count: int
    added: tuple[str, ...]
    replaced: tuple[str, ...]
    removed: tuple[str, ...]
    verification_facts: tuple[str, ...]

    @property
    def report(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "status": "OK",
                "mode": self.mode,
                "source": str(self.source_path),
                "output": str(self.output_path),
                "backup": str(self.backup_path) if self.backup_path is not None else None,
                "source_sha256": self.source_sha256,
                "source_size": self.source_size,
                "output_sha256": self.output_sha256,
                "output_size": self.output_size,
                "backup_sha256": self.backup_sha256,
                "backup_size": self.backup_size,
                "entry_count": self.entry_count,
                "added": self.added,
                "replaced": self.replaced,
                "removed": self.removed,
                "verification_facts": self.verification_facts,
            }
        )


def _path_key(path: Path) -> str:
    return path.absolute().as_posix().casefold()


def _is_link_or_reparse(path: Path, metadata: os.stat_result) -> bool:
    return path.is_symlink() or bool(
        getattr(metadata, "st_file_attributes", 0) & _REPARSE_POINT
    )


def _reject_link_components(
    path: Path,
    label: str,
    *,
    allow_missing_leaf: bool = False,
) -> Path:
    """Reject links/reparse points in every existing component of *path*."""

    absolute = Path(path).absolute()
    anchor = Path(absolute.anchor) if absolute.anchor else Path()
    current = anchor
    parts = absolute.parts
    if absolute.anchor and parts and parts[0] == absolute.anchor:
        parts = parts[1:]
    for index, part in enumerate(parts):
        current = current / part
        try:
            metadata = current.lstat()
        except FileNotFoundError:
            if allow_missing_leaf and index == len(parts) - 1:
                return absolute
            raise TransactionError(f"{label} path component does not exist: {current}")
        except OSError as error:
            raise TransactionError(f"cannot inspect {label} path component: {current}") from error
        if _is_link_or_reparse(current, metadata):
            raise TransactionError(
                f"{label} must not traverse a symlink or reparse point: {current}"
            )
    return absolute


def _require_existing_file(path: Path, label: str) -> Path:
    absolute = _reject_link_components(path, label)
    try:
        metadata = absolute.lstat()
    except OSError as error:
        raise TransactionError(f"cannot inspect {label}: {absolute}") from error
    if _is_link_or_reparse(absolute, metadata):
        raise TransactionError(f"{label} must not be a symlink or reparse point: {absolute}")
    if not stat.S_ISREG(metadata.st_mode):
        raise TransactionError(f"{label} is not a regular file: {absolute}")
    return absolute


def _require_existing_directory(path: Path, label: str) -> Path:
    absolute = _reject_link_components(path, label)
    try:
        metadata = absolute.lstat()
    except OSError as error:
        raise TransactionError(f"cannot inspect {label}: {absolute}") from error
    if _is_link_or_reparse(absolute, metadata):
        raise TransactionError(f"{label} must not be a symlink or reparse point: {absolute}")
    if not stat.S_ISDIR(metadata.st_mode):
        raise TransactionError(f"{label} is not a directory: {absolute}")
    return absolute


def _safe_new_dv2_path(path: str | os.PathLike, source: Path) -> Path:
    try:
        output = Path(path).absolute()
    except (TypeError, ValueError) as error:
        raise TransactionError(f"invalid output path: {path!r}") from error
    if output.suffix.casefold() != ".dv2":
        raise TransactionError(f"output must have a .dv2 suffix: {output}")
    if _path_key(output) == _path_key(source):
        raise TransactionError("Save As output must be a different path from the selected source")
    _require_existing_directory(output.parent, "output parent")
    try:
        metadata = output.lstat()
    except FileNotFoundError:
        metadata = None
    except OSError as error:
        raise TransactionError(f"cannot inspect output path: {output}") from error
    if metadata is not None:
        raise TransactionError(f"output already exists; refusing to overwrite: {output}")
    return output


def _safe_new_sibling(directory: Path, stem: str, suffix: str = ".dv2") -> Path:
    _require_existing_directory(directory, "transaction directory")
    for _ in range(32):
        candidate = directory / f".{stem}.{uuid.uuid4().hex}{suffix}"
        try:
            candidate.lstat()
        except FileNotFoundError:
            return candidate
        except OSError as error:
            raise TransactionError(f"cannot inspect transaction temporary path: {candidate}") from error
    raise TransactionError("could not allocate a unique transaction temporary path")


def _file_identity(path: Path) -> tuple[int, int] | None:
    try:
        metadata = os.stat(path, follow_symlinks=False)
    except OSError:
        return None
    return metadata.st_dev, metadata.st_ino


def _candidate_consumed(path: Path) -> bool:
    return _file_identity(path) is None


# These narrow helpers are intentional test seams.  Tests can inject a
# publication failure without replacing process-global os.link/os.replace.
def _link(source: Path, destination: Path) -> None:
    os.link(source, destination)


def _unlink(path: Path) -> None:
    os.unlink(path)


def _atomic_replace(source: Path, destination: Path) -> None:
    os.replace(source, destination)


def _restore_atomic_replace(source: Path, destination: Path) -> None:
    """Restore seam kept separate from the attempted forward installation."""

    os.replace(source, destination)


def _publish_exclusive(temporary: Path, destination: Path) -> Path:
    """Create *destination* atomically without overwriting a race winner."""

    identity = _file_identity(temporary)
    if identity is None:
        raise TransactionError(f"cannot inspect transaction temporary: {temporary}")
    try:
        _link(temporary, destination)
    except FileExistsError as error:
        raise TransactionError(
            f"output appeared during publication; refusing to overwrite: {destination}"
        ) from error
    except OSError as error:
        raise TransactionError(f"cannot publish output without overwrite: {destination}") from error
    try:
        _unlink(temporary)
    except OSError as error:
        if _file_identity(destination) == identity:
            try:
                _unlink(destination)
            except OSError as cleanup_error:
                raise TransactionError(
                    f"cannot finalize publication cleanup: {destination}"
                ) from cleanup_error
        raise TransactionError(f"cannot finalize output publication: {destination}") from error
    if not _candidate_consumed(temporary):
        # A seam or an unusual filesystem must not make a successful result
        # while both owned names remain visible.
        if _file_identity(destination) == identity:
            try:
                _unlink(destination)
            except OSError:
                pass
        raise TransactionError(f"cannot finalize output publication: {destination}")
    return destination


def _remove_owned(path: Path | None, identity: tuple[int, int] | None) -> None:
    if path is None or identity is None:
        return
    if _file_identity(path) != identity:
        return
    try:
        _unlink(path)
    except OSError:
        # Cleanup is best effort and identity-guarded.  Never remove a path
        # which has been substituted by another process.
        return


def _copy_fsync(source: Path, destination: Path) -> tuple[str, int]:
    """Copy one file to a new sibling, flush it, and return its digest/size."""

    digest = hashlib.sha256()
    size = 0
    destination_identity: tuple[int, int] | None = None
    try:
        with source.open("rb") as source_stream, destination.open("xb") as target:
            destination_identity = _file_identity(destination)
            if destination_identity is None:
                raise TransactionError(
                    f"cannot identify newly-created transaction copy: {destination}"
                )
            while True:
                chunk = source_stream.read(dv2lib.IO_CHUNK)
                if not chunk:
                    break
                target.write(chunk)
                digest.update(chunk)
                size += len(chunk)
            target.flush()
            os.fsync(target.fileno())
    except TransactionError:
        _remove_owned(destination, destination_identity)
        raise
    except Exception as error:
        _remove_owned(destination, destination_identity)
        raise TransactionError(f"cannot create flushed transaction copy: {destination}") from error
    return digest.hexdigest(), size


def _hash_file(path: Path) -> tuple[str, int]:
    try:
        return dv2lib.hash_and_size_file(path)
    except OSError as error:
        raise TransactionError(f"cannot hash transaction file: {path}") from error


def _validate_plans(plans: tuple[Plan, ...]) -> SelectedDKS:
    if not plans:
        raise TransactionError("transaction requires a non-empty tuple of plans")
    if not isinstance(plans, tuple):  # pragma: no cover - callers use _coerce_plans
        raise TransactionError("plans must be supplied as an ordered tuple")
    if not isinstance(plans[0], (CompiledResourcePlan, RemovalPlan)):
        raise TransactionError(
            "transaction plans must be CompiledResourcePlan or RemovalPlan instances"
        )
    selected = plans[0].selected_dks
    if not isinstance(selected, SelectedDKS):
        raise TransactionError("every plan must bind a SelectedDKS")
    try:
        selected_path_key = _path_key(selected.physical_path)
    except (TypeError, ValueError) as error:
        raise TransactionError("selected DKS physical path is invalid") from error
    if (
        not isinstance(selected.sha256, str)
        or len(selected.sha256) != 64
        or any(character not in "0123456789abcdefABCDEF" for character in selected.sha256)
        or isinstance(selected.file_size, bool)
        or not isinstance(selected.file_size, int)
        or selected.file_size < 0
    ):
        raise TransactionError("selected DKS SHA-256 is invalid")
    seen: set[str] = set()
    for plan in plans:
        if not isinstance(plan, (CompiledResourcePlan, RemovalPlan)):
            raise TransactionError(
                "transaction plans must be CompiledResourcePlan or RemovalPlan instances"
            )
        if not isinstance(plan.selected_dks, SelectedDKS):
            raise TransactionError("every plan must bind a SelectedDKS")
        other = plan.selected_dks
        if not isinstance(plan.target_logical_path, str) or not isinstance(plan.target_key, str):
            raise TransactionError("transaction plan target path/key must be strings")
        try:
            other_path_key = _path_key(other.physical_path)
        except (TypeError, ValueError) as error:
            raise TransactionError("selected DKS physical path is invalid") from error
        if (
            not isinstance(other.sha256, str)
            or len(other.sha256) != 64
            or any(character not in "0123456789abcdefABCDEF" for character in other.sha256)
            or isinstance(other.file_size, bool)
            or not isinstance(other.file_size, int)
            or other.file_size < 0
        ):
            raise TransactionError("selected DKS identity is invalid")
        if (
            other_path_key != selected_path_key
            or other.file_size != selected.file_size
            or other.sha256.casefold() != selected.sha256.casefold()
        ):
            raise TransactionError("all plans must bind the exact same selected DKS identity")

        try:
            normalized = dv2lib.normalize_archive_path(plan.target_logical_path)
        except (dv2lib.DV2Error, TypeError) as error:
            raise TransactionError(f"unsafe transaction target path: {plan.target_logical_path!r}") from error
        if normalized.casefold() != plan.target_key.casefold():
            raise TransactionError("transaction plan target key does not match its normalized path")
        target_key = plan.target_key.casefold()
        if target_key in seen:
            raise TransactionError(
                f"duplicate transaction target key (case-insensitive): {plan.target_key!r}"
            )
        seen.add(target_key)

        if isinstance(plan, CompiledResourcePlan):
            if plan.operation != plan.classification or plan.classification not in (
                REPLACE,
                ADD_OVERRIDE,
                ADD_NEW,
            ):
                raise TransactionError(f"unsupported compiled plan classification: {plan.classification!r}")
            if not isinstance(plan.compiled, CompiledResource):
                raise TransactionError("compiled plan has no valid compiled resource")
            if plan.storage_mode not in dv2lib.STORAGE_MODES:
                raise TransactionError(f"invalid planned storage mode: {plan.storage_mode!r}")
            try:
                compiled_target = dv2lib.normalize_archive_path(plan.compiled.target_logical_path)
            except (dv2lib.DV2Error, TypeError) as error:
                raise TransactionError("compiled resource target path is unsafe") from error
            if compiled_target.casefold() != target_key:
                raise TransactionError("compiled resource target differs from its operation plan")
            if plan.classification == REPLACE:
                if not isinstance(plan.selected_entry, dv2lib.DV2Entry):
                    raise TransactionError("REPLACE plan is missing its selected source entry")
                if plan.storage_mode != plan.selected_entry.storage_mode:
                    raise TransactionError("REPLACE plan does not preserve source storage mode")
            elif plan.selected_entry is not None:
                raise TransactionError("ADD plan unexpectedly contains a selected source entry")
            elif plan.storage_mode != plan.compiled.preferred_storage_mode:
                raise TransactionError("ADD plan storage mode differs from compiled resource preference")
        else:
            if plan.operation != REMOVE_OVERRIDE or plan.classification != REMOVE_OVERRIDE:
                raise TransactionError("unsupported removal plan classification")
            if not isinstance(plan.selected_entry, dv2lib.DV2Entry):
                raise TransactionError("REMOVE_OVERRIDE plan is missing its selected source entry")
            if plan.selected_entry.key != target_key:
                raise TransactionError("REMOVE_OVERRIDE target differs from its selected source entry")
    return selected


def _coerce_plans(plans: Sequence[Plan] | Iterable[Plan]) -> tuple[Plan, ...]:
    # The public contract is deliberately tuple-shaped.  Accepting a list is
    # useful for a UI caller but immediately freezes it into the one order used
    # by this transaction; strings and mappings are rejected explicitly.
    if isinstance(plans, (str, bytes, bytearray)):
        raise TransactionError("plans must be a non-empty ordered sequence")
    try:
        frozen = tuple(plans)
    except TypeError as error:
        raise TransactionError("plans must be a non-empty ordered sequence") from error
    if not frozen:
        raise TransactionError("transaction requires a non-empty tuple of plans")
    return frozen


def _open_bound_session(selected: SelectedDKS) -> tuple[dv2lib.DV2Session, str, int]:
    """Open and hash-bind the selected source exactly once for staging."""

    source = _require_existing_file(selected.physical_path, "selected DKS archive")
    if source.name.casefold() != DKS_PATCH_FILE_NAME.casefold():
        raise TransactionError(f"selected archive basename must be {DKS_PATCH_FILE_NAME!r}")
    try:
        session = dv2lib.DV2Session(source)
        sha256, size = dv2lib.hash_and_size_file(source)
    except (dv2lib.DV2Error, OSError) as error:
        raise TransactionError(f"cannot reopen/hash selected DKS archive: {source}") from error
    if (
        size != session.file_size
        or size != selected.file_size
        or sha256.casefold() != selected.sha256.casefold()
    ):
        raise TransactionError("selected DKS changed since planning; refusing to stage a stale archive")
    return session, sha256, size


def _entry_for_key(entries: Iterable[dv2lib.DV2Entry], key: str) -> dv2lib.DV2Entry | None:
    for entry in entries:
        if entry.key == key:
            return entry
    return None


def _snapshot_pending(session: dv2lib.DV2Session) -> tuple[PendingOperationSnapshot, ...]:
    return tuple(
        PendingOperationSnapshot(
            kind=operation.kind,
            path=operation.path,
            key=operation.key,
            storage=operation.storage,
        )
        for operation in session.pending_ops()
    )


def _assert_pending_set(session: dv2lib.DV2Session, plans: tuple[Plan, ...]) -> None:
    expected = {plan.target_key.casefold() for plan in plans}
    pending = session.pending_ops()
    actual = [operation.key for operation in pending]
    if len(pending) != len(plans) or set(actual) != expected or len(set(actual)) != len(actual):
        raise TransactionError("staging produced an unexpected pending-operation set")
    for plan in plans:
        operation = next(
            operation for operation in pending if operation.key == plan.target_key.casefold()
        )
        if isinstance(plan, RemovalPlan):
            expected_kind, expected_storage = dv2lib.OP_REMOVE, None
        elif plan.classification == REPLACE:
            expected_kind, expected_storage = dv2lib.OP_SET, None
        else:
            expected_kind, expected_storage = dv2lib.OP_ADD, plan.storage_mode
        if operation.kind != expected_kind or operation.storage != expected_storage:
            raise TransactionError(
                f"pending operation for {plan.target_key!r} differs from its plan"
            )


def stage_transaction(plans: Sequence[Plan] | Iterable[Plan]) -> StagedTransaction:
    """Stage a non-empty ordered set of plans in one DV2 session.

    The selected archive is reopened and full-hashed once.  No save or output
    file is created by this function.
    """

    frozen_plans = _coerce_plans(plans)
    selected = _validate_plans(frozen_plans)
    session, source_sha256, source_size = _open_bound_session(selected)
    for plan in frozen_plans:
        current_entry = _entry_for_key(session.entries, plan.target_key.casefold())
        try:
            if isinstance(plan, RemovalPlan):
                if current_entry is None:
                    raise TransactionError(
                        f"planned REMOVE_OVERRIDE target no longer exists: {plan.target_logical_path!r}"
                    )
                session.stage_remove(current_entry.path)
            elif plan.classification == REPLACE:
                if current_entry is None:
                    raise TransactionError(
                        f"planned REPLACE target no longer exists: {plan.target_logical_path!r}"
                    )
                session.stage_set(current_entry.path, plan.compiled.compiled_payload)
            else:
                if current_entry is not None:
                    raise TransactionError(
                        f"planned ADD target now exists: {plan.target_logical_path!r}"
                    )
                session.stage_add(
                    plan.target_logical_path,
                    plan.compiled.compiled_payload,
                    plan.storage_mode,
                )
        except dv2lib.DV2Error as error:
            raise TransactionError(f"cannot stage {plan.classification}: {error}") from error
    _assert_pending_set(session, frozen_plans)
    operation_order = tuple(plan.target_key.casefold() for plan in frozen_plans)
    added: list[str] = []
    replaced: list[str] = []
    removed: list[str] = []
    for plan in frozen_plans:
        if isinstance(plan, RemovalPlan):
            removed.append(plan.selected_entry.path)
        elif plan.classification in (ADD_NEW, ADD_OVERRIDE):
            added.append(plan.target_logical_path)
        else:
            replaced.append(plan.selected_entry.path)
    return StagedTransaction(
        session=session,
        plans=frozen_plans,
        source_path=session.path,
        source_sha256=source_sha256,
        source_size=source_size,
        pending_ops=_snapshot_pending(session),
        operation_order=operation_order,
        added=tuple(added),
        replaced=tuple(replaced),
        removed=tuple(removed),
    )


def _ensure_staged(value: StagedTransaction | Sequence[Plan] | Iterable[Plan]) -> StagedTransaction:
    if isinstance(value, StagedTransaction):
        # The backend session is deliberately mutable: callers may inspect it
        # or accidentally add/cancel pending operations between staging and
        # saving.  The immutable plan tuple and bound source identity are the
        # transaction authority, so rebuild a fresh session at the save
        # boundary instead of trusting the stored session's pending set.
        selected = _validate_plans(value.plans)
        try:
            metadata_path_key = _path_key(value.source_path)
            selected_path_key = _path_key(selected.physical_path)
        except (TypeError, ValueError) as error:
            raise TransactionError("staged transaction source path is invalid") from error
        if (
            not isinstance(value.source_sha256, str)
            or not isinstance(value.source_size, int)
            or metadata_path_key != selected_path_key
            or value.source_sha256.casefold() != selected.sha256.casefold()
            or value.source_size != selected.file_size
        ):
            raise TransactionError("staged transaction identity metadata does not match its plans")
        return stage_transaction(value.plans)
    return stage_transaction(value)


def _plans_and_selected(
    value: StagedTransaction | Sequence[Plan] | Iterable[Plan],
) -> tuple[tuple[Plan, ...], SelectedDKS]:
    if isinstance(value, StagedTransaction):
        selected = _validate_plans(value.plans)
        return value.plans, selected
    frozen = _coerce_plans(value)
    return frozen, _validate_plans(frozen)


def _all_stored_hashes(session: dv2lib.DV2Session) -> dict[str, str]:
    hashes = session.stored_region_hashes()
    empty_hash = hashlib.sha256(b"").hexdigest()
    return {entry.key: hashes.get(entry.key, empty_hash) for entry in session.entries}


def _header_difference(source: dv2lib.DV2Header, output: dv2lib.DV2Header) -> str | None:
    for field_name in _HEADER_FIELDS:
        expected = getattr(source, field_name)
        actual = getattr(output, field_name)
        if expected != actual:
            return f"header field {field_name} changed ({expected!r} -> {actual!r})"
    return None


def _raise_candidate(message: str) -> None:
    raise CandidateVerificationError(message)


def _verify_candidate_paths(
    source_path: Path,
    output_path: Path,
    plans: tuple[Plan, ...],
    selected: SelectedDKS,
    *,
    require_bound_source: bool,
) -> CandidateVerification:
    source = _require_existing_file(source_path, "verification source archive")
    output = _require_existing_file(output_path, "verification output archive")
    try:
        source_session = dv2lib.DV2Session(source)
        output_session = dv2lib.DV2Session(output)
        source_sha256, source_size = _hash_file(source)
        output_sha256, output_size = _hash_file(output)
        source_deep = source_session.deep_verify()
        output_deep = output_session.deep_verify()
        source_stored = _all_stored_hashes(source_session)
        output_stored = _all_stored_hashes(output_session)
    except (dv2lib.DV2Error, OSError, TransactionError) as error:
        raise CandidateVerificationError(f"candidate archive cannot be independently verified: {error}") from error

    if require_bound_source and (
        _path_key(source) != _path_key(selected.physical_path)
        or source_size != selected.file_size
        or source_sha256.casefold() != selected.sha256.casefold()
    ):
        _raise_candidate("verification source no longer matches the selected DKS identity")
    difference = _header_difference(source_session.header, output_session.header)
    if difference:
        _raise_candidate(difference)

    plan_by_key: dict[str, Plan] = {}
    for plan in plans:
        target_key = plan.target_key.casefold()
        if target_key in plan_by_key:
            _raise_candidate(f"duplicate target key in allowlist: {plan.target_key!r}")
        plan_by_key[target_key] = plan

    source_by_key = {entry.key: entry for entry in source_session.entries}
    output_by_key = {entry.key: entry for entry in output_session.entries}
    for plan in plans:
        source_entry = source_by_key.get(plan.target_key.casefold())
        if isinstance(plan, RemovalPlan):
            if source_entry is None:
                _raise_candidate(f"source is missing planned removal target: {plan.target_logical_path!r}")
            if plan.target_key.casefold() in output_by_key:
                _raise_candidate(f"removed target is still present: {plan.target_logical_path!r}")
        elif plan.classification == REPLACE:
            if source_entry is None:
                _raise_candidate(f"source is missing planned replacement target: {plan.target_logical_path!r}")
        elif source_entry is not None:
            _raise_candidate(f"ADD target already exists in verification source: {plan.target_logical_path!r}")

    expected_paths: list[str] = []
    for entry in source_session.entries:
        plan = plan_by_key.get(entry.key)
        if isinstance(plan, RemovalPlan):
            continue
        expected_paths.append(entry.path)
    for plan in plans:
        if isinstance(plan, CompiledResourcePlan) and plan.classification in (ADD_NEW, ADD_OVERRIDE):
            expected_paths.append(plan.target_logical_path)
    actual_paths = [entry.path for entry in output_session.entries]
    if actual_paths != expected_paths:
        _raise_candidate(
            "candidate entry path/order differs from allowlist: "
            f"expected {expected_paths!r}, got {actual_paths!r}"
        )

    source_logical = source_deep["logical_sha256"]
    output_logical = output_deep["logical_sha256"]
    for source_entry in source_session.entries:
        plan = plan_by_key.get(source_entry.key)
        if isinstance(plan, RemovalPlan):
            continue
        output_entry = output_by_key.get(source_entry.key)
        if output_entry is None:
            _raise_candidate(f"candidate is missing source entry {source_entry.path!r}")
        if output_entry.path != source_entry.path:
            _raise_candidate(f"canonical source path changed for {source_entry.path!r}")
        if plan is None:
            if output_entry.storage_mode != source_entry.storage_mode:
                _raise_candidate(f"unchanged storage mode changed for {source_entry.path!r}")
            if output_logical.get(source_entry.key) != source_logical.get(source_entry.key):
                _raise_candidate(f"unchanged logical payload changed for {source_entry.path!r}")
            if output_stored.get(source_entry.key) != source_stored.get(source_entry.key):
                _raise_candidate(f"unchanged stored payload changed for {source_entry.path!r}")
        elif isinstance(plan, CompiledResourcePlan):
            if plan.classification == REPLACE:
                if output_entry.storage_mode != source_entry.storage_mode:
                    _raise_candidate(f"replacement storage mode changed for {source_entry.path!r}")
                expected_sha = plan.compiled.compiled_sha256.casefold()
                if output_logical.get(plan.target_key.casefold(), "").casefold() != expected_sha:
                    _raise_candidate(f"replacement logical SHA differs for {source_entry.path!r}")

    added_plans = [
        plan
        for plan in plans
        if isinstance(plan, CompiledResourcePlan)
        and plan.classification in (ADD_NEW, ADD_OVERRIDE)
    ]
    for plan in added_plans:
        output_entry = output_by_key.get(plan.target_key.casefold())
        if output_entry is None:
            _raise_candidate(f"added target is missing: {plan.target_logical_path!r}")
        if output_entry.path != plan.target_logical_path:
            _raise_candidate(f"added target path is not canonical: {plan.target_logical_path!r}")
        if output_entry.storage_mode != plan.storage_mode:
            _raise_candidate(f"added storage mode differs for {plan.target_logical_path!r}")
        expected_sha = plan.compiled.compiled_sha256.casefold()
        if output_logical.get(plan.target_key.casefold(), "").casefold() != expected_sha:
            _raise_candidate(f"added logical SHA differs for {plan.target_logical_path!r}")

    facts = (
        "source_deep_verify_passed",
        "output_deep_verify_passed",
        "preserved_header_fields_verified",
        "entry_path_order_allowlist_verified",
        "unchanged_logical_and_stored_payloads_verified",
        "planned_target_hashes_and_storage_verified",
        "no_runtime_claim_made",
    )
    return CandidateVerification(
        source_path=source,
        output_path=output,
        source_sha256=source_sha256,
        source_size=source_size,
        output_sha256=output_sha256,
        output_size=output_size,
        entry_count=len(output_session.entries),
        added=tuple(
            plan.target_logical_path for plan in added_plans
        ),
        replaced=tuple(
            plan.selected_entry.path
            for plan in plans
            if isinstance(plan, CompiledResourcePlan) and plan.classification == REPLACE
        ),
        removed=tuple(
            plan.selected_entry.path for plan in plans if isinstance(plan, RemovalPlan)
        ),
        verification_facts=facts,
    )


def verify_candidate(
    source_path: str | os.PathLike,
    output_path: str | os.PathLike,
    transaction: StagedTransaction | Sequence[Plan] | Iterable[Plan],
) -> CandidateVerification:
    """Independently verify a candidate against the selected source/allowlist."""

    plans, selected = _plans_and_selected(transaction)
    return _verify_candidate_paths(
        Path(source_path),
        Path(output_path),
        plans,
        selected,
        require_bound_source=True,
    )


def verify_staged_candidate(
    transaction: StagedTransaction,
    output_path: str | os.PathLike,
) -> CandidateVerification:
    """Convenience form of :func:`verify_candidate` for a staged result."""

    if not isinstance(transaction, StagedTransaction):
        raise TransactionError("verify_staged_candidate requires a StagedTransaction")
    return verify_candidate(transaction.source_path, output_path, transaction)


def _check_bound_source(staged: StagedTransaction) -> tuple[str, int]:
    source = _require_existing_file(staged.source_path, "selected DKS archive")
    sha256, size = _hash_file(source)
    if size != staged.source_size or sha256.casefold() != staged.source_sha256.casefold():
        raise TransactionError("selected DKS changed during transaction; refusing to continue")
    return sha256, size


def _save_result(
    mode: str,
    staged: StagedTransaction,
    output_path: Path,
    verification: CandidateVerification,
    *,
    backup_path: Path | None = None,
    backup_sha256: str | None = None,
    backup_size: int | None = None,
) -> TransactionSaveResult:
    return TransactionSaveResult(
        mode=mode,
        source_path=staged.source_path,
        output_path=output_path,
        backup_path=backup_path,
        source_sha256=staged.source_sha256,
        source_size=staged.source_size,
        output_sha256=verification.output_sha256,
        output_size=verification.output_size,
        backup_sha256=backup_sha256,
        backup_size=backup_size,
        entry_count=verification.entry_count,
        added=staged.added,
        replaced=staged.replaced,
        removed=staged.removed,
        verification_facts=verification.verification_facts,
    )


def save_as_transaction(
    transaction: StagedTransaction | Sequence[Plan] | Iterable[Plan],
    output_path: str | os.PathLike,
) -> TransactionSaveResult:
    """Build, verify, and exclusively publish a new Save As archive."""

    staged = _ensure_staged(transaction)
    source = _require_existing_file(staged.source_path, "selected DKS archive")
    output = _safe_new_dv2_path(output_path, source)
    candidate = _safe_new_sibling(output.parent, output.stem)
    candidate_identity: tuple[int, int] | None = None
    published_identity: tuple[int, int] | None = None
    try:
        try:
            staged.session.save_as(candidate)
        except Exception as error:
            # A backend failure is allowed to occur after it has created a
            # partial candidate.  Capture that path's current identity for
            # the outer identity-guarded cleanup; a later substitution is
            # still protected by _remove_owned's no-follow identity check.
            candidate_identity = _file_identity(candidate)
            if isinstance(error, TransactionError):
                raise
            raise TransactionError(f"cannot build Save As candidate: {candidate}") from error
        candidate_identity = _file_identity(candidate)
        if candidate_identity is None:
            raise TransactionError("Save As backend returned without a candidate file")
        verification = verify_candidate(source, candidate, staged)
        _check_bound_source(staged)
        if _file_identity(candidate) != candidate_identity:
            raise TransactionError("Save As candidate identity changed before publication")
        _publish_exclusive(candidate, output)
        candidate = None  # type: ignore[assignment]
        observed_published_identity = _file_identity(output)
        if observed_published_identity is None:
            raise TransactionError("published Save As output disappeared")
        if observed_published_identity != candidate_identity:
            raise TransactionError("published Save As output identity changed")
        # Only mark the destination as owned after its identity has been
        # proven equal to the candidate.  If a publication seam or another
        # process substituted the path before this check, cleanup must not
        # remove that external file.
        published_identity = observed_published_identity
        post = verify_candidate(source, output, staged)
        if (
            post.output_sha256 != verification.output_sha256
            or post.output_size != verification.output_size
        ):
            raise TransactionError("published Save As output differs from its pre-publication candidate")
        if _file_identity(output) != published_identity:
            raise TransactionError("published Save As output changed during final verification")
        return _save_result("save_as", staged, output, post)
    except Exception:
        _remove_owned(candidate, candidate_identity)
        _remove_owned(output, published_identity or candidate_identity)
        raise


def _validate_in_place_source(staged: StagedTransaction) -> tuple[Path, Path]:
    source = _require_existing_file(staged.source_path, "selected DKS archive")
    if source.name.casefold() != DKS_PATCH_FILE_NAME.casefold():
        raise TransactionError(f"in-place Save requires basename {DKS_PATCH_FILE_NAME!r}")
    backup = source.with_name("DKS_Patch.dv2.bak")
    _reject_link_components(backup.parent, "backup parent")
    try:
        metadata = backup.lstat()
    except FileNotFoundError:
        metadata = None
    except OSError as error:
        raise TransactionError(f"cannot inspect fixed backup path: {backup}") from error
    if metadata is not None:
        if _is_link_or_reparse(backup, metadata):
            raise TransactionError(f"fixed backup must not be a symlink or reparse point: {backup}")
        if not stat.S_ISREG(metadata.st_mode):
            raise TransactionError(f"fixed backup is not a regular file: {backup}")
    return source, backup


def _verify_installed(
    backup: Path,
    installed: Path,
    staged: StagedTransaction,
    expected_output_sha256: str,
    expected_output_size: int,
) -> CandidateVerification:
    """Verify an installed source against the fixed old-source backup."""

    backup_sha256, backup_size = _hash_file(backup)
    if backup_sha256.casefold() != staged.source_sha256.casefold() or backup_size != staged.source_size:
        raise CandidateVerificationError("fixed backup is not a byte-perfect copy of the previous source")
    verification = _verify_candidate_paths(
        backup,
        installed,
        staged.plans,
        staged.plans[0].selected_dks,
        require_bound_source=False,
    )
    if (
        verification.output_sha256.casefold() != expected_output_sha256.casefold()
        or verification.output_size != expected_output_size
    ):
        raise CandidateVerificationError("installed archive differs from the preverified candidate")
    return verification


def _handle_final_install_failure(
    source: Path,
    backup: Path,
    staged: StagedTransaction,
    error: BaseException,
) -> None:
    """Classify an ambiguous final replacement and restore when necessary."""

    source_is_old = False
    try:
        _require_existing_file(source, "selected DKS archive after final replacement")
        current_sha256, current_size = _hash_file(source)
        source_is_old = (
            current_sha256.casefold() == staged.source_sha256.casefold()
            and current_size == staged.source_size
        )
    except Exception:
        source_is_old = False
    if source_is_old:
        raise TransactionError(
            "final replacement failed; selected source remains byte-identical"
        ) from error
    try:
        _restore_from_backup(source, backup, staged)
    except Exception as restore_error:
        raise TransactionError(
            "final replacement failed and source restoration failed"
        ) from restore_error
    raise TransactionError(
        "final replacement failed; source restored from fixed backup"
    ) from error


def _restore_from_backup(source: Path, backup: Path, staged: StagedTransaction) -> None:
    _reject_link_components(source.parent, "selected DKS archive before restoration parent")
    try:
        source_metadata = source.lstat()
    except FileNotFoundError:
        source_metadata = None
    except OSError as error:
        raise TransactionError(f"cannot inspect selected DKS archive before restoration: {source}") from error
    if source_metadata is not None:
        if _is_link_or_reparse(source, source_metadata):
            raise TransactionError("selected DKS archive before restoration must not be a symlink")
        if not stat.S_ISREG(source_metadata.st_mode):
            raise TransactionError("selected DKS archive before restoration is not a regular file")
    _require_existing_file(backup, "fixed backup")
    restore_candidate = _safe_new_sibling(source.parent, source.stem, suffix=".restore.tmp")
    restore_candidate_identity: tuple[int, int] | None = None
    try:
        digest, size = _copy_fsync(backup, restore_candidate)
        restore_candidate_identity = _file_identity(restore_candidate)
        if digest.casefold() != staged.source_sha256.casefold() or size != staged.source_size:
            raise TransactionError("fixed backup changed while preparing source restoration")
        _restore_atomic_replace(restore_candidate, source)
        if not _candidate_consumed(restore_candidate):
            raise TransactionError("restore candidate was not consumed by atomic replacement")
        restore_candidate = None  # type: ignore[assignment]
        restored_sha256, restored_size = _hash_file(source)
        if restored_sha256.casefold() != staged.source_sha256.casefold() or restored_size != staged.source_size:
            raise TransactionError("restored source is not byte-perfect")
    finally:
        if restore_candidate is not None:
            _remove_owned(restore_candidate, restore_candidate_identity)


def save_in_place_transaction(
    transaction: StagedTransaction | Sequence[Plan] | Iterable[Plan],
) -> TransactionSaveResult:
    """Build, verify, back up, and atomically install one DKS Patch archive."""

    staged = _ensure_staged(transaction)
    source, backup = _validate_in_place_source(staged)
    candidate = _safe_new_sibling(source.parent, source.stem)
    backup_candidate = _safe_new_sibling(source.parent, source.stem + ".bak", suffix=".tmp")
    candidate_identity: tuple[int, int] | None = None
    backup_candidate_identity: tuple[int, int] | None = None
    try:
        try:
            staged.session.save_as(candidate)
        except Exception as error:
            # Keep a partially-created backend candidate cleanup-safe even
            # when save_as raises before returning its report.
            candidate_identity = _file_identity(candidate)
            if isinstance(error, TransactionError):
                raise
            raise TransactionError(f"cannot build in-place candidate: {candidate}") from error
        candidate_identity = _file_identity(candidate)
        if candidate_identity is None:
            raise TransactionError("in-place backend returned without a candidate file")
        candidate_verification = verify_candidate(source, candidate, staged)
        _check_bound_source(staged)

        copied_sha256, copied_size = _copy_fsync(source, backup_candidate)
        backup_candidate_identity = _file_identity(backup_candidate)
        if backup_candidate_identity is None:
            raise TransactionError("backup copy disappeared before publication")
        if copied_sha256.casefold() != staged.source_sha256.casefold() or copied_size != staged.source_size:
            raise TransactionError("backup copy does not match the selected source identity")
        _check_bound_source(staged)
        try:
            _atomic_replace(backup_candidate, backup)
        except OSError as error:
            raise TransactionError("cannot atomically publish fixed backup") from error
        if not _candidate_consumed(backup_candidate):
            raise TransactionError("backup candidate was not consumed by atomic replacement")
        backup_candidate = None  # type: ignore[assignment]
        backup_candidate_identity = None
        backup_sha256, backup_size = _hash_file(backup)
        if backup_sha256.casefold() != staged.source_sha256.casefold() or backup_size != staged.source_size:
            raise TransactionError("fixed backup failed byte-perfect verification")
        _check_bound_source(staged)

        try:
            # From this call onward the source may be old, new, or in an
            # ambiguous post-error state.  Every exception, including a
            # replace-then-raise seam and the consumed-candidate invariant,
            # goes through the same old-source check/rollback path.
            if _file_identity(candidate) != candidate_identity:
                raise TransactionError("in-place candidate identity changed before final replacement")
            _atomic_replace(candidate, source)
            if not _candidate_consumed(candidate):
                raise TransactionError(
                    "candidate was not consumed by the final atomic replacement"
                )
            candidate = None  # type: ignore[assignment]
            installed = _verify_installed(
                backup,
                source,
                staged,
                candidate_verification.output_sha256,
                candidate_verification.output_size,
            )
        except Exception as install_error:
            _handle_final_install_failure(source, backup, staged, install_error)
        return _save_result(
            "in_place",
            staged,
            source,
            installed,
            backup_path=backup,
            backup_sha256=backup_sha256,
            backup_size=backup_size,
        )
    finally:
        _remove_owned(candidate, candidate_identity)
        _remove_owned(
            backup_candidate,
            backup_candidate_identity,
        )


# Short names are convenient for future GUI code while the explicit names are
# unambiguous in call sites and tests.
stage_plans = stage_transaction
save_as = save_as_transaction
save_in_place = save_in_place_transaction
verify_transaction_candidate = verify_candidate


__all__ = [
    "CandidateVerification",
    "CandidateVerificationError",
    "PendingOperationSnapshot",
    "StagedTransaction",
    "TransactionError",
    "TransactionSaveResult",
    "save_as",
    "save_as_transaction",
    "save_in_place",
    "save_in_place_transaction",
    "stage_plans",
    "stage_transaction",
    "verify_candidate",
    "verify_staged_candidate",
    "verify_transaction_candidate",
]
