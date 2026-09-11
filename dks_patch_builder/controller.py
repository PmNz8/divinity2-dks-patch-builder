"""JSON-safe exception boundary for DKS Patch Builder front ends.

The controller deliberately has no GUI imports.  A future thin desktop view
may forward dialog results here, while automated tests can exercise the same
state transitions headlessly.
"""

# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import Any, Callable

from .model import DKSPatchBuilderModel


JSONPrimitive = str | int | float | bool | None
JSONValue = JSONPrimitive | list["JSONValue"] | dict[str, "JSONValue"]


class BuilderController:
    """Translate model operations into plain JSON-compatible responses."""

    def __init__(self, model: DKSPatchBuilderModel | None = None) -> None:
        self.model = model or DKSPatchBuilderModel()

    @classmethod
    def _jsonify(cls, value: Any) -> JSONValue:
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, bytes):
            raise TypeError("binary payloads must not cross the controller boundary")
        if is_dataclass(value) and not isinstance(value, type):
            return {
                field.name: cls._jsonify(getattr(value, field.name))
                for field in fields(value)
            }
        if isinstance(value, dict):
            result: dict[str, JSONValue] = {}
            for key, item in value.items():
                if not isinstance(key, str):
                    raise TypeError("controller mappings must have string keys")
                result[key] = cls._jsonify(item)
            return result
        if isinstance(value, (list, tuple)):
            return [cls._jsonify(item) for item in value]
        raise TypeError(
            f"unsupported value at controller boundary: {type(value).__name__}"
        )

    def _state(self) -> JSONValue:
        return self._jsonify(self.model.snapshot())

    def _call(self, operation: Callable[[], Any]) -> dict[str, JSONValue]:
        try:
            result = self._jsonify(operation())
        except Exception as error:
            return {
                "ok": False,
                "error": str(error),
                "error_type": type(error).__name__,
                "state": self._state(),
            }
        return {"ok": True, "result": result, "state": self._state()}

    def _cancelled(self) -> dict[str, JSONValue]:
        return {"ok": True, "cancelled": True, "state": self._state()}

    @staticmethod
    def _dialog_path(path: str | None) -> str | None:
        if path is None or not isinstance(path, str) or not path.strip():
            return None
        return path

    def state(self) -> dict[str, JSONValue]:
        return {"ok": True, "result": self._state(), "state": self._state()}

    def open_archive(
        self,
        packed_root: str | None,
        dks_path: str | None,
        *,
        expected_count: int | None = None,
        discard_pending: bool = False,
    ) -> dict[str, JSONValue]:
        root = self._dialog_path(packed_root)
        selected = self._dialog_path(dks_path)
        if root is None or selected is None:
            return self._cancelled()
        return self._call(
            lambda: self.model.open_archive(
                root,
                selected,
                expected_count=expected_count,
                discard_pending=discard_pending,
            )
        )

    def create_archive(
        self,
        packed_root: str | None,
        dks_path: str | None,
        *,
        expected_count: int | None = None,
        discard_pending: bool = False,
    ) -> dict[str, JSONValue]:
        root = self._dialog_path(packed_root)
        output = self._dialog_path(dks_path)
        if root is None or output is None:
            return self._cancelled()
        return self._call(
            lambda: self.model.create_archive(
                root,
                output,
                expected_count=expected_count,
                discard_pending=discard_pending,
            )
        )

    def close(self, *, discard_pending: bool = False) -> dict[str, JSONValue]:
        return self._call(lambda: self.model.close(discard_pending=discard_pending))

    def list_entries(self, substring: str | None = None) -> dict[str, JSONValue]:
        return self._call(lambda: self.model.list_entries(substring))

    def pending_changes(self) -> dict[str, JSONValue]:
        return self._call(self.model.pending_changes)

    def import_package(self, package_directory: str | None) -> dict[str, JSONValue]:
        package = self._dialog_path(package_directory)
        if package is None:
            return self._cancelled()
        return self._call(lambda: self.model.import_package(package))

    def remove_override(self, logical_path: str) -> dict[str, JSONValue]:
        return self._call(lambda: self.model.remove_override(logical_path))

    def import_packages(self, parent_directory, *, progress=None, cancelled=None):
        parent = self._dialog_path(parent_directory)
        if parent is None:
            return self._cancelled()
        return self._call(lambda: self.model.import_packages(parent,
            progress=progress, cancelled=cancelled))

    def cancel(self, logical_path: str) -> dict[str, JSONValue]:
        return self._call(lambda: self.model.cancel(logical_path))

    def clear_pending(self) -> dict[str, JSONValue]:
        return self._call(self.model.clear_pending)

    def preview(self) -> dict[str, JSONValue]:
        return self.pending_changes()

    def save(self) -> dict[str, JSONValue]:
        return self._call(self.model.save_in_place)

    def save_as(self, output_path: str | None) -> dict[str, JSONValue]:
        output = self._dialog_path(output_path)
        if output is None:
            return self._cancelled()
        return self._call(lambda: self.model.save_as(output))


__all__ = ["BuilderController", "JSONPrimitive", "JSONValue"]
