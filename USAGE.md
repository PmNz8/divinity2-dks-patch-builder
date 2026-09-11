# DKS Patch Builder usage

## Narrative packages in 0.1.1

Version 0.1.1 accepts `narrative.fov_debt.v1` exported by Quest Author.
This is the fixed Beata/Hansel debt template for a new Flames of Vengeance
campaign, not a general importer for arbitrary quests or existing saves.

1. Select the complete pristine supported GOG Packed root and create a new,
   empty `DKS_Patch.dv2` outside Packed.
2. Import the complete exported folder (`asset.json`, `bundle.json`, `quest.json`
   and five payload members). All resources validate before anything is queued.
3. Review all five rows and their warnings. The full source audit can take time;
   the GUI remains responsive while editing actions are disabled.
4. Save using the normal external archive transaction. Nothing is installed into
   the game. Reopen the output to inspect its five resources.

While a narrative group is pending, other imports are blocked. Save the group
first; texture packages can then be added to that saved DKS, including after
reopening it. This texture-plus-quest combination has a maintainer-reported
runtime success; it is not proof of arbitrary package compatibility.
Cancelling any pending member cancels all five; individual narrative resource
removal and reimport into a nonempty DKS are refused. To revise a quest, change
the saved authoring project and build a fresh package/archive.
There is no comprehensive cross-package conflict protection or automatic
resolution. Review logical target paths yourself: a later import may replace
an existing resource. Multiple narrative packages and in-place quest upgrades
remain unsupported; shared quest resources are not semantically merged.

The first import requires the recognized original 533-archive corpus, with no
unknown overlays. Before saving, original path/size/mtime continuity and exact
used-source hashes are rechecked. A mismatch stops the write; it is not silently
accepted as a new baseline. Package hashes check integrity, not the publisher's
identity or universal correctness of arbitrary binary content. Use trusted exports.

The original quest template has bounded game tests, and the maintainer reports
runtime success with a combined texture/quest DKS. The delivery integration also
has offline and programmatic real-Tk tests. Test your own generated DKS separately;
the runtime report does not certify every configuration. The texture workflow follows.

## Launch and requirements

Use Windows 10/11 x64. Extract the whole portable ZIP into a writable local
folder and launch `DKSPatchBuilder.exe`. Keep `_internal`, `LICENSES`,
`docs/images` and all accompanying documents together; do not launch inside
the ZIP. Python, UV, Node.js, WebView2 and .NET need not be installed separately.
The EXE is unsigned; Windows may show a reputation warning. Do not disable
system protection globally.

The packaged runtime is Python 3.12.6 with Tcl/Tk 8.6.13. It is the tested
development baseline, not a claim of latest security maintenance. This is an
experimental hobby tool, not a sandbox hardened against hostile packages or
concurrent filesystem tampering. Use trusted local inputs and working folders.
Save publication uses hard links and atomic replacement: use a local filesystem
supporting those operations (the tested workflow uses Windows NTFS). A network,
cloud-synced or other unsupported destination may fail; do not bypass guards.

## 1. Prepare a texture package

In Texture Viewer 0.1.0, open a compatible DV2, select a texture and choose
**Export Builder Package**. The package is a directory containing:

```text
asset.json
template.nif
texture/
  texture.json
  mip-00.rgb.png
  mip-00.alpha.png   (when required)
  ...
```

Keep the whole directory. A single PNG and the Viewer's plain **Export Set**
are not Builder packages. The accepted envelope is
`divinity2.dks_asset_package`, schema version 1, asset type `texture_nif`.

Edit the mip PNGs you intend to change. Keep dimensions, channel purpose,
filenames and the existing mip structure. RGB PNGs hold color; required alpha
PNGs hold transparency. Save as 8-bit, non-interlaced PNG, not indexed/paletted
or 16-bit PNG. Do not edit `template.nif` or the inner `texture.json` metadata.
BC1/BC3 changes can be compiled; edited BC2 is rejected. Unchanged supported
packages round-trip without changing the texture payload bytes.

The tool does not regenerate lower mips. Editing mip 0 alone leaves other mips
unchanged, so the original appearance may return with distance. Prepare each
existing mip you want to change in your image editor.

Normally leave the target path in `asset.json` unchanged. An advanced user may
edit only `target_logical_path` to a safe `.nif` logical path. This does not
create a material/reference that makes the game use the new resource.

## 2. Open or create your mod archive

Work on a separate mod archive **outside the game installation**. Select the
complete `Packed` directory when prompted: it is read for archive inventory
and occurrence checks, including root `Patch.dv2`. Then use **New** to create
a new external `DKS_Patch.dv2`, or **Open** for an existing file with that name.
New creates the empty file immediately; it is not merely a pending action.

The selected Packed and DKS paths appear above the tables. Filtering and Reset
affect the entry list only. Non-texture entries already in the archive are
listed without decoding and are preserved unless you explicitly remove them.
Do not rename an original game archive to trick it into being a DKS input.

## 3. Queue and review changes

Choose **Import Package** and select the complete package directory. Compilation
and planning run in a single background worker; wait for the operation to finish.
Import does not save the archive. The pending table can show:

- **REPLACE:** the selected DKS already has this target path.
- **ADD_OVERRIDE:** the target exists in Packed but not in the selected DKS.
- **ADD_NEW:** the target was not found in either place.
- **REMOVE_OVERRIDE:** remove a selected entry from this DKS only.

Review **Preview**, the report and warnings before saving. Occurrence and
operation names are not proof of universal game archive priority. Multiple
sources, template differences or new paths can produce warnings rather than
block compilation; resolve uncertainty before manually installing a mod.

Only one queued operation per case-insensitive target is allowed. Use
**Cancel Selected** to remove one pending operation or **Clear Pending** for
all. **Remove Override** queues removal; it does not delete an original Packed
resource. Re-import a package after further PNG edits: queued compiled bytes
are not a live link to the package directory.

## 4. Save and recover

**Save As** publishes to a new, non-existing `.dv2` file after verification.
Use the basename `DKS_Patch.dv2`; another basename may be written with a warning
but will not reopen as an editable DKS document. Existing outputs are refused.
The successfully reopened output becomes the selected archive.

**Save** updates the selected DKS only after source identity and planned changes
pass verification. It keeps a byte-perfect copy of the immediately previous
archive as **DKS_Patch.dv2.bak**. The next Save replaces that backup; it is not
a history system. Keep any additional backups you need outside the working
archive. A failed save must not be treated as success; inspect the report and
retain the queue. Do not change the source archive externally while it is open.

If an error explicitly says the archive was saved but could not be reopened,
the write has already succeeded: preserve and inspect that output rather than
assuming nothing changed or repeating the operation blindly.

To recover manually, close the Builder and the game, preserve the suspect mod
file separately, then restore your known-good DKS or the verified previous
`.bak`. This tool does not restore original game files or install/uninstall mods.

Opening, creating, closing or exiting with pending changes asks whether to
discard them. Declining or cancelling a chooser preserves the queue. Closing
the window while work is active waits; it does not interrupt a transaction.

## Scope and diagnostics

Only existing-layout standalone texture NIFs and their existing mip geometry
are supported. There is no model/audio/item import, texture resizing, arbitrary
wrapper creation or automatic mip generation. Size/memory limits apply; large
valid textures or archives can still consume substantial memory and CPU.
Canonical DV2 paths use backslashes; noncanonical paths are outside the tested
support. Structural validity does not prove runtime use. Existing-path texture
replacement has bounded user-tested game evidence, not universal approval.

A headless check can create a new diagnostic file:

```powershell
.\DKSPatchBuilder.exe check --report .\check-result.json
```

The file must not already exist. This checks imports/runtime, not a Tk window.
The report, window title and About dialog identify the application version. Include
the app version, ZIP SHA-256 and exact error text when reporting a problem.
Reports may contain local paths; remove private information before sharing.
Do not attach game archives, textures, saves or package contents automatically.
The app has no telemetry, updater or runtime downloader; the GitHub profile
link opens only when clicked.
