# PIHC3 module-activity authoring

Date: 2026-08-02

## Outcome

PIHC3 no longer needs a parallel `inactive_modules` tree or manual YAML edits
to recover an inactive module. ParaDev now treats activity as a generic,
Registry-compatible property of every standalone module:

- Browser and HeavenBase Catalog projections include active and inactive
  source modules so both remain discoverable and editable.
- Full, cached, family-partial, and module-partial compilation use the active
  compiler projection only.
- Directly targeting an inactive module fails with an activate-first message
  instead of pretending that the module does not exist.
- A guarded exact-hash transaction changes activity through the Python SDK,
  CLI, REST, MCP, Tauri bridge, and desktop GUI.
- Deactivation writes only `inactive: true`; activation removes that key and
  deletes an otherwise empty visible `meta.yaml`.
- Obsolete hidden activity metadata is migrated in the same source
  transaction. Compiler-owned routing metadata remains hidden under
  `.paradev/`.

## PIHC3 physical audit

The authoritative tree at `projects/PIHC3/src` has:

- 14,575 physical module folders, all named `id - localized title`;
- zero `_component` or `_asset_component` folders;
- zero `legacy` folders;
- zero `inactive_modules` folders;
- zero malformed module or collection instance folder names;
- one user-visible module metadata file:
  `bookmark/PIHC_DIE_NEBENWELT - 新世界/meta.yaml`, containing only
  `inactive: true`;
- 847 system-owned metadata files hidden under module-local `.paradev/`
  directories and zero collection metadata files.

No PIHC3 source data was changed while verifying the activity UI.

## Compile evidence

| Mode | Modules | Collections | Artifacts | Diagnostics | Blocked |
| --- | ---: | ---: | ---: | ---: | --- |
| clean/full | 14,574 | 106 | 33,438 | 0 | no |
| cached full | 14,574 | 106 | 33,438 | 0 | no |
| family partial: `technology` | 301 | 0 | 10,204 | 0 | no |
| module partial: `technology/TECHNOLOGY_FIREARM_I` | 1 | 0 | 9,300 | 0 | no |

These are the current post-consolidation baselines. The smaller artifact count
relative to older release notes is the documented removal of duplicate
component and localization outputs, not a change introduced by module
activity.

## Regression and native-app evidence

- Python: 2,536 passed, 9 expected native-Windows-only skips, zero failures.
- Desktop: 89 files and 1,463 tests passed.
- Focused activity UI/service/model tests: 5 files and 296 tests passed.
- Rust/Tauri: 95 tests passed; `cargo check` passed.
- TypeScript and Vite production build passed.
- Critical Ruff syntax/name checks passed for every touched Python surface.
- The bundled backend runtime smoke passed against HeavenBase and the
  project-package catalog.
- The ad-hoc-signed native app rendered PIHC3 Bookmarks through the bundled
  backend. It displayed both `PIHC` and inactive `PIHC_DIE_NEBENWELT`, exposed
  the All/Active/Inactive filter, showed Activate for the inactive module, and
  disabled direct module build with an activate-first explanation.

The verified local artifacts are:

- `apps/desktop/src-tauri/target/debug/bundle/macos/ParaDev.app`
- `apps/desktop/src-tauri/target/debug/bundle/dmg/ParaDev_0.1.0-0_aarch64.dmg`

The DMG is an unsigned/ad-hoc local development artifact. Its checksum,
mounted app signature, and Applications link passed, but this run explicitly
allowed the missing external PIHC3 companion archive, so it is not a public
release candidate.

## Architecture note

The Heaven-style boundary remains intact: Registry/entity definitions own
family behavior and source resources; Project owns guarded source
transactions and authoring/compiler projections; surface adapters only map
their transport; the GUI consumes the generated contract and does not add a
PIHC3-specific activity path.
