# Agent-Safe Registry-Owned Module Assets

Date: 2026-08-01

## Outcome

ParaDev now exposes one SDK-owned binary snapshot path and one narrower
Registry-owned module-asset path. Desktop and MCP adapters reuse those
contracts instead of reading module bytes through separate implementations.

- `Project.read_source_binary(...)` reads a project-contained regular file
  from one descriptor-stable snapshot, bounded to 20 MiB. It returns MIME and
  format metadata, SHA-256, paired `size`/`mtime_ns`, an exact `draft_guard`,
  and optional base64 content.
- `Project.read_module_asset(...)` accepts only a source matched by the active
  family Registry as a copy slot or image source. It adds module identity and
  the matched source-slot rows, and omits base64 by default.
- MCP `module_asset` exposes that bounded asset contract to authoring agents.
  Its returned guard can be passed unchanged to `project_draft_apply` with a
  new `content_base64` value.
- The desktop binary-source facade delegates stable reading and size policy to
  `Project.read_source_binary(...)`, then preserves the existing Tauri desktop
  payload schema.
- The ParaDev authoring skill and bilingual manuals now direct agents to use
  browser-discovered Registry slots, request asset bytes only when necessary,
  and never recreate `_component` or `_asset_component` folders.

## PIHC3 Verification

The live colocated technology module
`technology/TECHNOLOGY_AIR_AIRSHIP` was inspected without writing sources:

- `icon.png` resolved through the Registry `preview` slot.
- `gfx/interface/technologies/TECHNOLOGY_AIR_AIRSHIP_medium.dds` resolved
  through the Registry `compiled_assets` copy slot.
- `interface/technologies/TECHNOLOGY_AIR_AIRSHIP.gfx` resolved through the
  same copy slot.
- MCP returned the DDS identity, slot ownership, digest, and revision guard
  with `content_included=false`.
- `def.txt` was rejected by the asset API because it is not a registered copy
  or image resource.

A strict module-partial PIHC3 dry build passed:

```text
family: technology
module: TECHNOLOGY_AIR_AIRSHIP
modules: 1
collections: 0
artifacts: 10,997
diagnostics: 0
blocked: false
```

The artifact count includes ParaDev's deterministic project-wide publication
closure; the selected compilation target remained the single technology
module.

## Gates

- ParaDev focused Python/desktop/architecture gate: 696 passed, 2 expected
  native-Win32-only tests skipped on macOS.
- Tauri Rust gate: 95 passed.
- Desktop Vitest gate: 1,438 passed across 87 files.
- Desktop production TypeScript/Vite build: passed.
- ParaDev authoring skill validator: passed.
- Python syntax, fatal Ruff rules, Black, Cargo format, and diff whitespace:
  passed.
- Heaven-style utility scan reported only established broad-file imports in
  `project.py` and `desktop/local.py`; this slice did not add a second binary
  filesystem, MIME, or size-policy owner.

## Next

Use the same Registry-owned resource contract to close remaining GUI asset UX
gaps: show slot provenance and revision-conflict recovery in the image editor,
then add module creation/edit walkthroughs for the largest PIHC3 authoring
families without introducing family-specific desktop logic.
