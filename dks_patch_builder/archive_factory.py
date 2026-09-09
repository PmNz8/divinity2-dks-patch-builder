"""DKS-specific factory for a new empty ``DKS_Patch.dv2`` archive."""

# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
import os
from pathlib import Path
from typing import Mapping

from dks_patch_builder.dv2lib import (
    DV2Error,
    DV2Header,
    DV2Session,
    create_empty_archive,
    hash_and_size_file,
)


DKS_PATCH_FILE_NAME = "DKS_Patch.dv2"


@dataclass(frozen=True, slots=True)
class EmptyDKSPatchResult:
    """Immutable result of creating and independently checking DKS_Patch."""

    output: Path
    sha256: str
    size: int
    header: DV2Header
    entry_count: int
    deep_verify: bool

    @property
    def report(self) -> Mapping[str, object]:
        """Return a read-only report view for callers that prefer mappings."""

        return MappingProxyType(
            {
                "status": "OK",
                "operation": "create_empty_dks_patch",
                "output": str(self.output),
                "sha256": self.sha256,
                "size": self.size,
                "header": self.header,
                "entry_count": self.entry_count,
                "deep_verify": self.deep_verify,
            }
        )


def create_empty_dks_patch(output_path: str | os.PathLike) -> EmptyDKSPatchResult:
    """Create a verified empty Developer's Cut patch archive.

    This wrapper only chooses the established DKS header defaults and filename
    policy.  It performs no game-directory, ``Packed`` or installation work.
    """

    try:
        requested = Path(output_path)
    except (TypeError, ValueError) as error:
        raise DV2Error(f"invalid DKS patch output path: {output_path!r}") from error
    if requested.name.casefold() != DKS_PATCH_FILE_NAME.casefold():
        raise DV2Error(
            f"DKS patch output basename must be {DKS_PATCH_FILE_NAME!r}"
        )

    report = create_empty_archive(
        requested,
        version=5,
        unknown_04=1,
        unknown_08=4,
        layout_mode=0,
        compression_mode=1,
    )
    output = Path(report["output"])
    try:
        session = DV2Session(output)
        deep = session.deep_verify()
    except (DV2Error, OSError) as error:
        raise DV2Error(
            f"independent DKS patch verification could not reopen {output}"
        ) from error
    if session.entries or deep.get("entries") != 0 or deep.get("logical_sha256") != {}:
        raise DV2Error("independent DKS patch verification found non-empty content")
    verified_sha256, verified_size = hash_and_size_file(output)
    if verified_sha256 != report["sha256"] or verified_size != report["size"]:
        raise DV2Error("independent DKS patch hash or size differs from factory report")
    expected_header = DV2Header(**report["header"])
    if session.header != expected_header:
        raise DV2Error("independent DKS patch header differs from factory report")

    return EmptyDKSPatchResult(
        output=output,
        sha256=verified_sha256,
        size=verified_size,
        header=session.header,
        entry_count=0,
        deep_verify=True,
    )


__all__ = ["DKS_PATCH_FILE_NAME", "EmptyDKSPatchResult", "create_empty_dks_patch"]
