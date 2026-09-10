# Changelog

## 0.2.0.dev0 — local development, unreleased

- Fixed new-FoV `narrative.fov_debt.v1` package handler and immutable resource bundles.
- Atomic five-resource import/cancellation, pristine-source checks and external-only
  narrative DKS output; no merge, partial removal or in-place quest upgrade.
- Quest Author/Tkinter → package → Builder/Tkinter → DKS pipeline verified locally,
  including readback equality of all five resources. No new game-runtime Pass.
- Existing texture and transaction behavior retained; no runtime dependency added.

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
