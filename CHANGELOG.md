# Changelog

## 0.2.8 — 2026-09-13

- Import `.d2model` packages with edited models, textures and prepared collision
  through the ordinary Import Model workflow.
- Support packages exported from CAT and ITEM containers, including embedded
  model edits; queue the complete owning container under its original path.
- Support recognized static ITEM topology, UV/normal edits, existing manual LODs,
  material parameters, embedded texture pixels and qualified raw normal-map edits.
- Import prepared v4 collision packages; preserve unchanged v3 physics.
- Group model changes atomically, omit unchanged resources, show target details
  and warnings, and recheck recorded sources before saving.
- Warn about alternate same-path source variants without rejecting an otherwise
  verified package. Existing archive transaction and cancellation safeguards remain.
- Keep existing texture/batch/MIP and fixed-profile narrative workflows.

## 0.2.5 — local Farm B candidate

- Updated source-bound core: static ITEM topology, UV/normal arrays, conservative
  derived bounds, named parameters and owned embedded texture pixels.
- Prepared triangle-physics v4 carrier with explicit per-face material indices;
  actual cooking remains in the separate CLI. No automatic source selection.
- Whole-owner model edits no longer count as normal-map pixel edits merely
  because the same CAT/ITEM also owns an unchanged embedded normal texture.
  Actual normal-map pixel edits remain guarded.
- Existing component/hierarchy/source identities and transaction checks remain.
  No game installation, universal ITEM support or runtime certification.

## 0.2.3 — local experimental candidate

- Whole-owner CAT/ITEM diagnostics; native primary paths remain the write target.
- Updated pinned model core: static CAT fallback on unsupported animation binding,
  animated ITEM recognition, and guarded combined geometry/animation validation.
- Original clips and opaque container data remain preserved. No guessed skeleton
  alias, DIV2 write expansion, implicit merge, or game installation.


## 0.2.0 — local experimental candidate

- Modular `.d2model` v1/v2 reader, native-edit/assembly verifier, exact source
  audit and atomic pending model groups; existing DV2 writer remains unchanged.
- Import Model file dialog and read-only `inspect-model` report command.
- Only changed native payloads are queued; original/no-op resources are omitted.
- Complete source occurrence scan, ambiguous-variant rejection, pre-save source
  recheck and external-only model outputs. No installation or reference rewriting.
- Existing texture/batch/narrative behavior preserved; no new runtime dependency.
- Windows binary version fields now derive from the same application version.

## 0.1.2 — local experimental candidate

- Batch import of direct child texture packages with progress and cancellation.
- Duplicate targets remain errors; successful imports only queue until explicit Save.
- Source-bound MIP0 v2 generation for BC1/BC3 with raw-channel or sRGB/opacity area filtering.
- Unedited base preserves all source bytes, including lower compressed mip data.
- Existing full-mip v1, BC2 no-op, narrative and archive transaction policies retained.

## 0.1.1 — 2026-09-11

- Fixed new-FoV `narrative.fov_debt.v1` package handler and immutable resource bundles.
- Atomic five-resource import/cancellation, pristine-source checks and external-only
  narrative DKS output; no narrative merge, partial removal or in-place quest upgrade.
- Quest Author/Tkinter → package → Builder/Tkinter → DKS pipeline verified locally,
  including readback equality of all five resources.
- Existing texture and transaction behavior retained; no runtime dependency added.
- Retains adding textures after saving the narrative group. The maintainer reports
  successful runtime use of a combined texture/quest DKS; arbitrary combinations
  are not certified. Documented the lack of comprehensive conflict protection
  and automatic resolution.
- Added source-audit regression tests for unknown overlays, missing originals,
  metadata drift, exact used-source hashes and the documented fast-recheck limit.

## 0.1.0 — experimental release

- Standalone Tkinter DKS archive builder with a single serialized backend worker.
- Texture Viewer v1 Builder Package import; BC1/BC3 edits and unchanged BC2.
- Complete Packed inventory, operation queue, warnings and cancellation.
- Verified Save As and in-place Save with one previous-file backup.
- Portable Windows x64 packaging and matching source distribution.
- The maintainer tested the candidate ZIP on a second Windows computer:
  the Builder produced a DKS archive, the game loaded it and the texture
  replacements were visible. Final release preparation changes documentation
  and window/About wording only; it does not change archive or texture behavior.
# 0.2.1 — experimental convex physics import

- Explicit Physics Experiment entry point for v3 model/physics carriers.
- Vertex-only NXB mutation without recooking; original non-target bytes retained.
- Fixed topology, recognized convex layouts and unique actor/mesh use only.
- Existing atomic model group, exact source checks and external-only save guards.
- Runtime behavior is untested; this mode may crash or produce incorrect collision.
# 0.2.2 — prepared collision carriers

- Ordinary Import Model supports v4 prepared by D2Model Cooker 0.1.0.
- Verify source/geometry binding and non-target NXB preservation, without SDK.
- Accept unchanged v3 physics; changed uncooked v3 remains blocked by default.
