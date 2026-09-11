"""Strict handler for the fixed new-FoV narrative bundle package."""

# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any

from ..narrative_profile_data import PROFILE
from ..package import AssetPackage, AssetPackageError, _read_bounded
from .base import CompiledBundle, CompiledResource, HandlerError


ASSET_TYPE_NARRATIVE = "narrative.fov_debt.v1"
BUNDLE_SCHEMA = "divinity2.narrative_bundle"
BUNDLE_SCHEMA_VERSION = 1
COMPILER = "quest-author-fov-debt-v1"
BUNDLE_FILE_NAME = "bundle.json"
CONFIG_FILE_NAME = "quest.json"
MAX_BUNDLE_BYTES = 128 * 1024
MAX_CONFIG_BYTES = 128 * 1024
MAX_RESOURCE_BYTES = 16 * 1024 * 1024
_SHA256_RE = re.compile(r"[0-9a-fA-F]{64}\Z")
_KEY_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,23}\Z", re.ASCII)

_TEXT_KEYS = (
    "beata.START",
    "beata.ABOUT.answer",
    "beata.ABOUT.reply",
    "beata.ACCEPT.answer",
    "beata.ACCEPT.reply",
    "beata.WAITING.answer",
    "beata.WAITING.reply",
    "beata.REPORT.answer",
    "beata.REPORT.reply",
    "beata.DONE.answer",
    "beata.DONE.reply",
    "beata.EXIT.answer",
    "beata.EXIT.reply",
    "hansel.REMIND.answer",
    "hansel.REMIND.reply",
    "hansel.REFUSAL.answer",
    "hansel.REFUSAL.reply",
    "hansel.THREAT.answer",
    "hansel.THREAT.reply",
    "hansel.PROMISE.answer",
    "hansel.PROMISE.reply",
    "hansel.SETTLED.answer",
    "hansel.SETTLED.reply",
)
_JOURNAL_KEYS = (
    "Accepted.long",
    "Accepted.short",
    "Completed.long",
    "Completed.short",
    "Closed.long",
    "Closed.short",
    "Failed.long",
    "Failed.short",
)
_EXPECTED_BUNDLE_FIELDS = frozenset(
    {
        "schema",
        "schema_version",
        "asset_type",
        "profile_id",
        "deployment",
        "compiler",
        "quest_key",
        "quest_title",
        "config_file",
        "config_sha256",
        "resources",
    }
)
_EXPECTED_RESOURCE_FIELDS = frozenset(
    {
        "role",
        "file",
        "logical_path",
        "sha256",
        "size",
        "source_archive",
        "source_sha256",
        "source_size",
    }
)


class NarrativeBundleHandlerError(HandlerError):
    """Raised when a fixed narrative bundle is malformed or unsupported."""


def _strict_json(raw: bytes, label: str) -> object:
    def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"duplicate JSON key {key!r}")
            result[key] = value
        return result

    def constant(value: str) -> object:
        raise ValueError(f"non-finite JSON constant {value}")

    try:
        return json.loads(
            raw.decode("utf-8", "strict"),
            object_pairs_hook=pairs,
            parse_constant=constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as error:
        raise NarrativeBundleHandlerError(f"{label}: invalid strict UTF-8 JSON") from error


def _object(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise NarrativeBundleHandlerError(f"{label} must be a JSON object")
    return value


def _exact(value: object, fields: frozenset[str], label: str) -> dict[str, object]:
    result = _object(value, label)
    keys = set(result)
    if keys != fields:
        missing = sorted(fields - keys)
        extra = sorted(keys - fields)
        detail = []
        if missing:
            detail.append(f"missing={missing!r}")
        if extra:
            detail.append(f"extra={extra!r}")
        raise NarrativeBundleHandlerError(f"{label} fields mismatch ({', '.join(detail)})")
    return result


def _string(value: object, label: str) -> str:
    if type(value) is not str:
        raise NarrativeBundleHandlerError(f"{label} must be a string")
    return value


def _integer(value: object, label: str) -> int:
    if isinstance(value, bool) or type(value) is not int:
        raise NarrativeBundleHandlerError(f"{label} must be an integer")
    return value


def _sha256(value: object, label: str) -> str:
    candidate = _string(value, label)
    if _SHA256_RE.fullmatch(candidate) is None:
        raise NarrativeBundleHandlerError(f"{label} must be a 64-character SHA-256")
    return candidate.casefold()


def _ascii_text(value: object, label: str, maximum: int) -> str:
    candidate = _string(value, label)
    if not 1 <= len(candidate) <= maximum or any(ord(char) < 32 or ord(char) > 126 for char in candidate):
        raise NarrativeBundleHandlerError(
            f"{label} must contain printable ASCII text of length 1..{maximum}"
        )
    return candidate


def _read_file(package: AssetPackage, name: str, limit: int) -> bytes:
    try:
        path = package.child(name)
        return _read_bounded(path, name, limit)
    except NarrativeBundleHandlerError:
        raise
    except (AssetPackageError, OSError) as error:
        raise NarrativeBundleHandlerError(f"cannot read package member {name!r}") from error


def _validate_config(value: object) -> dict[str, object]:
    config = _exact(
        value,
        frozenset({"schema", "key", "title", "secret", "texts", "journal"}),
        "quest.json",
    )
    if config["schema"] != "divinity2.debt_template_config.v1":
        raise NarrativeBundleHandlerError("quest.json schema is unsupported")
    key = _string(config["key"], "quest.json.key")
    if _KEY_RE.fullmatch(key) is None:
        raise NarrativeBundleHandlerError("quest.json.key has an unsupported format")
    _ascii_text(config["title"], "quest.json.title", 96)
    _ascii_text(config["secret"], "quest.json.secret", 400)
    texts = _object(config["texts"], "quest.json.texts")
    if set(texts) != set(_TEXT_KEYS):
        raise NarrativeBundleHandlerError("quest.json.texts must contain the exact 23 dialogue slots")
    for slot in _TEXT_KEYS:
        _ascii_text(texts[slot], f"quest.json.texts.{slot}", 600)
    journal = _object(config["journal"], "quest.json.journal")
    if set(journal) != set(_JOURNAL_KEYS):
        raise NarrativeBundleHandlerError("quest.json.journal must contain the exact 8 slots")
    for slot in _JOURNAL_KEYS:
        _ascii_text(journal[slot], f"quest.json.journal.{slot}", 600)
    return config


class NarrativeBundleHandler:
    """Validate and import five precompiled resources from a trusted exporter.

    Hashes enforce package integrity, not compiler authenticity or game semantics.
    The Builder does not recompile quest.json or execute imported content.
    """

    asset_type = ASSET_TYPE_NARRATIVE

    def compile(self, package: AssetPackage) -> CompiledBundle:
        if not isinstance(package, AssetPackage):
            raise NarrativeBundleHandlerError("narrative handler requires an AssetPackage")
        if package.asset_type != self.asset_type:
            raise NarrativeBundleHandlerError(
                f"narrative handler cannot compile asset type {package.asset_type!r}"
            )
        if package.template_file_name != BUNDLE_FILE_NAME:
            raise NarrativeBundleHandlerError("narrative package template file must be bundle.json")

        expected_members = {
            "asset.json",
            BUNDLE_FILE_NAME,
            CONFIG_FILE_NAME,
            *(f"{row['role']}.bin" for row in PROFILE["resources"]),
        }
        if set(package.root_members) != expected_members:
            missing = sorted(expected_members - set(package.root_members))
            extra = sorted(set(package.root_members) - expected_members)
            details = []
            if missing:
                details.append(f"missing={missing!r}")
            if extra:
                details.append(f"extra={extra!r}")
            raise NarrativeBundleHandlerError(
                f"narrative package root members mismatch ({', '.join(details)})"
            )

        anchor = next(row["logical_path"] for row in PROFILE["resources"] if row["role"] == "seed")
        if package.template_logical_path != anchor or package.target_logical_path != anchor:
            raise NarrativeBundleHandlerError(
                "narrative package template and target paths must equal the profile root startup path"
            )

        if len(package.template_payload) > MAX_BUNDLE_BYTES:
            raise NarrativeBundleHandlerError(
                "bundle.json exceeds the supported 128 KiB manifest limit"
            )
        manifest = _object(_strict_json(package.template_payload, BUNDLE_FILE_NAME), BUNDLE_FILE_NAME)
        manifest = _exact(manifest, _EXPECTED_BUNDLE_FIELDS, BUNDLE_FILE_NAME)
        if manifest["schema"] != BUNDLE_SCHEMA or _integer(
            manifest["schema_version"], "bundle.json.schema_version"
        ) != BUNDLE_SCHEMA_VERSION:
            raise NarrativeBundleHandlerError("bundle.json schema/version is unsupported")
        if manifest["asset_type"] != self.asset_type:
            raise NarrativeBundleHandlerError("bundle.json asset_type does not match the handler")
        if manifest["profile_id"] != PROFILE["profile_id"]:
            raise NarrativeBundleHandlerError("bundle.json profile_id is unsupported")
        if manifest["deployment"] != PROFILE["deployment"]:
            raise NarrativeBundleHandlerError("bundle.json deployment is unsupported")
        if manifest["compiler"] != COMPILER:
            raise NarrativeBundleHandlerError("bundle.json compiler is unsupported")
        if manifest["config_file"] != CONFIG_FILE_NAME:
            raise NarrativeBundleHandlerError("bundle.json config_file must be quest.json")

        config_bytes = _read_file(package, CONFIG_FILE_NAME, MAX_CONFIG_BYTES)
        config = _validate_config(_strict_json(config_bytes, CONFIG_FILE_NAME))
        config_sha256 = hashlib.sha256(config_bytes).hexdigest()
        if _sha256(manifest["config_sha256"], "bundle.json.config_sha256") != config_sha256:
            raise NarrativeBundleHandlerError("bundle.json config_sha256 does not match quest.json")
        if manifest["quest_key"] != config["key"] or manifest["quest_title"] != config["title"]:
            raise NarrativeBundleHandlerError("bundle.json quest identity does not match quest.json")

        resources = manifest["resources"]
        if type(resources) is not list or len(resources) != len(PROFILE["resources"]):
            raise NarrativeBundleHandlerError("bundle.json.resources must contain exactly five resources")

        compiled: list[CompiledResource] = []
        for index, profile_row in enumerate(PROFILE["resources"]):
            resource = _exact(resources[index], _EXPECTED_RESOURCE_FIELDS, f"bundle.json.resources[{index}]")
            expected_file = f"{profile_row['role']}.bin"
            expected = {
                "role": profile_row["role"],
                "file": expected_file,
                "logical_path": profile_row["logical_path"],
                "source_archive": profile_row["source_archive"],
                "source_sha256": profile_row["source_sha256"].casefold(),
                "source_size": profile_row["source_size"],
            }
            for field in ("role", "file", "logical_path", "source_archive"):
                if resource[field] != expected[field]:
                    raise NarrativeBundleHandlerError(
                        f"bundle.json.resources[{index}].{field} does not match the frozen profile"
                    )
            if _sha256(resource["source_sha256"], f"bundle.json.resources[{index}].source_sha256") != expected["source_sha256"]:
                raise NarrativeBundleHandlerError(
                    f"bundle.json.resources[{index}].source_sha256 does not match the frozen profile"
                )
            if _integer(resource["source_size"], f"bundle.json.resources[{index}].source_size") != expected["source_size"]:
                raise NarrativeBundleHandlerError(
                    f"bundle.json.resources[{index}].source_size does not match the frozen profile"
                )
            payload = _read_file(package, expected_file, MAX_RESOURCE_BYTES)
            if not payload:
                raise NarrativeBundleHandlerError(f"{expected_file} must not be empty")
            payload_sha256 = hashlib.sha256(payload).hexdigest()
            if _sha256(resource["sha256"], f"bundle.json.resources[{index}].sha256") != payload_sha256:
                raise NarrativeBundleHandlerError(
                    f"bundle.json.resources[{index}].sha256 does not match the payload"
                )
            if _integer(resource["size"], f"bundle.json.resources[{index}].size") != len(payload):
                raise NarrativeBundleHandlerError(
                    f"bundle.json.resources[{index}].size does not match the payload"
                )
            compiled.append(
                CompiledResource(
                    asset_type=self.asset_type,
                    template_logical_path=expected["logical_path"],
                    target_logical_path=expected["logical_path"],
                    compiled_payload=payload,
                    compiled_sha256=payload_sha256,
                    compiled_size=len(payload),
                    template_sha256=expected["source_sha256"],
                    template_size=expected["source_size"],
                    payload_changed=payload_sha256 != expected["source_sha256"],
                    preferred_storage_mode="zlib",
                )
            )

        return CompiledBundle(
            asset_type=self.asset_type,
            profile_id=PROFILE["profile_id"],
            resources=tuple(compiled),
            manifest_sha256=hashlib.sha256(package.template_payload).hexdigest(),
            warnings=(
                "new FoV only",
                "fixed recipe",
                "no in-place quest upgrades",
                "no new runtime acceptance",
            ),
        )


__all__ = [
    "ASSET_TYPE_NARRATIVE",
    "BUNDLE_FILE_NAME",
    "CONFIG_FILE_NAME",
    "NarrativeBundleHandler",
    "NarrativeBundleHandlerError",
]
