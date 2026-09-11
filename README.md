# Divinity II DKS Patch Builder 0.1.2

An experimental Windows x64 tool by [PmNz8](https://github.com/PmNz8) for building
texture modifications and fixed-profile narrative bundles in `DKS_Patch.dv2` archives.

Version 0.1.1 adds Quest Author's new-FoV Beata/Hansel package type.
The earlier 0.1.0 release supports textures only.

Built around the game's patch-archive loading mechanism, DKS Patch Builder
keeps supported texture replacements in a dedicated `DKS_Patch.dv2` — so you
can change the game's look without repacking its original asset archives.

Developed and tested exclusively with the **GOG edition of Divinity II:
Developer's Cut**. Compatibility with other editions or storefront versions
has not been verified.

## What it does

- Imports **Builder Packages** exported by [Texture Viewer](https://github.com/PmNz8/divinity2-texture-viewer).
- Compiles edited BC1/BC3 textures; unchanged BC2 packages are also supported.
- Imports batches of texture packages and regenerates existing lower mips from explicit MIP0 packages.
- Creates or opens a DKS archive, queues changes and shows their targets/warnings.
- Saves to a new archive or updates the selected DKS with one previous-file backup.

- Imports `narrative.fov_debt.v1` packages from Quest Author as one five-resource group.
- Validates the recognized pristine source corpus, complete narrative groups
  and supported source versions.

The initial narrative import requires a new empty DKS outside Packed and an empty
queue. Save that group first; texture packages can then be added to the saved DKS.
The maintainer reports successful game-runtime use of a DKS containing textures
and the fixed quest payload. This is a tested combination, not universal mod compatibility.
Merging several narrative packages or upgrading an existing quest is unsupported.
The tool does not install mods, resize textures or create game references
for newly named textures.

### Conflicts are your responsibility

There is **no comprehensive protection against conflicts between packages and no
automatic conflict resolution**. Basic queue/path and source-integrity checks do
not establish that mods are compatible. A later import can replace an existing
resource at the same logical path; the Builder does not merge quest logic, shared
registries or other resource contents. Review targets and warnings, keep backups,
and choose compatible packages yourself.

## Start

Extract the entire Windows ZIP and run **DKSPatchBuilder.exe**. No separate
Python, .NET or WebView2 installation is required. The executable is unsigned.

See **[USAGE.md](USAGE.md)** for the complete workflow, safety rules and limits,
or **[BUILD.md](BUILD.md)** to build the matching source package.

## Examples

Earlier development interface

![DKS Patch Builder interface](docs/images/patch-builder.png)

In-game example of changed textures

![Texture modification example](docs/images/swapped-textures.jpeg)

The screenshots are illustrative, not raw game assets. Depicted game content
remains the property of its respective rights holders. This tool is not
affiliated with the game developer or publisher.

## License

Copyright (C) 2026 PmNz8. Own code: **AGPL-3.0-only**; see [LICENSE](LICENSE),
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and [LICENSES](LICENSES).
Provided without warranty. Using this tool does not automatically put exported
content under AGPL, override existing content licenses or grant permission to
redistribute game assets. Mod authors retain rights to their own original
contributions to the extent they hold those rights.
