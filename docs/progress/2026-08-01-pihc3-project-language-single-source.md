# PIHC3 project-language single source

Date: 2026-08-01

## Outcome

- Added the optional author-facing `preferred_language` project manifest field.
  Projects without it keep the portable `en` fallback; PIHC3 declares `zh`
  once in `paradev.yaml`.
- `Project.templates()` now resolves every localization-bearing module template
  through that project preference without mutating the underlying Registry
  descriptor. SDK, desktop, REST, MCP, and atomic batch creation therefore use
  the same default, while an explicit per-module language still wins.
- Kept the preference out of module `meta.yaml`. Extension descriptors retain
  their portable fallback so a standalone external Entity remains usable
  outside PIHC3.
- Exposed the resolved preference in the Project and template payloads, updated
  compatible desktop types, and regenerated the Project/API catalog references.
- Added one guarded `Project.set_preferred_language(...)` transaction. It plans
  by default, writes only with the exact reviewed hash, blocks stale edits, and
  is the sole mutation owner behind CLI, REST, MCP, Tauri, and the compact
  desktop Project-language selector. Accepted aliases are normalized to one of
  ten short manifest values; a no-op preserves the manifest byte for byte.

## Physical source audit

- The live PIHC3 tree contains 71 module families, 14,618 non-empty module
  folders, two collection families, and 90 collection folders.
- There are zero `_component` or `_asset_component` directories, zero `legacy`
  directories, zero `inactive_modules` directories, zero source symlinks, and
  zero malformed direct module or collection folder names.
- All 1,306 visible module metadata files are valid and contain only the
  user-meaningful keys `collection` (1,305 occurrences) or `inactive` (one
  occurrence). Compiler-owned routing remains under `.paradev/`.
- Pre-cutover component paths may still appear as deletions in PIHC3's nested
  Git status until the migration is committed; they are not present on disk or
  used by discovery and compilation.

## Verification

- Standard Python gate: 2,263 passed, nine native-Windows tests skipped.
- Complete PIHC3 contract set: 198 passed.
- Desktop suite: 1,438 passed; TypeScript check and production Vite build pass.
- Rust formatting and all 95 desktop library tests pass.
- Architecture reference contract: 92 passed.
- Clean/full and cached PIHC3 builds: 14,617 active modules, 106 collections,
  35,139 artifacts, zero diagnostics or errors.
- Focus family partial: 738 modules, 28 collections, 12,499 artifacts, zero
  diagnostics or errors.
- Focus module partial (`FOCUS_C12_SHADOWS_OF_THE_PAST`): 129 modules, one
  collection, 11,253 artifacts, zero diagnostics or errors. The isolated
  publication closure remains all 35,139 files after partial compilation.

## Next usability work

- Continue improving the field descriptions and validation feedback of the
  existing Registry-backed editors; all visible template families already have
  a guided create path, while advanced free-form PDX remains an intentional
  escape hatch.
- Continue converging focus, technology, doctrine, and MIO graph authoring on
  Registry-owned Entity resource slots rather than GUI family-name cases.
- Add live folder-title preview to the Project-language selector so users can
  see the naming effect before applying it to newly created modules.
