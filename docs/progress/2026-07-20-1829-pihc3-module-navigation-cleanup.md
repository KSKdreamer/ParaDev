# PIHC3 module navigation cleanup

Date: 2026-07-20 18:29 +08

## Outcome

The PIHC3 module sidebar now represents authoring families instead of exposing every internal build family. The normal project-backed list contains 47 real PIHC3 families: 44 template-backed authoring families plus three real child-domain families. Forty-two migration-support families remain active in discovery and builds but are explicitly hidden from novice navigation. Four frontend-only placeholder rows are no longer allowed to appear as project modules.

This is project-owned policy. PIHC3 declares visibility in `paradev.yaml`; neither the SDK nor the desktop app guesses from a `_component` suffix. That keeps a hidden family build-authoritative and allows a future component family to remain visible when a project chooses that policy.

All hands-on cleanup and rebuilding used the disposable project:

`/Users/magolor/Projects/ParaDev/PIHC3-GUI-Smoke`

The protected checkout at `/Users/magolor/Projects/ParaDev/ParaDev-3/projects/PIHC3` was not modified.

## What produced the mixed list

The former 93-row sidebar was an exact combination of four groups:

| Group | Rows | Prior language behavior | Current navigation behavior |
| --- | ---: | --- | --- |
| Template-backed authoring families | 44 | Localized | Visible |
| Real child-domain families | 3 | English fallback | Visible and localized |
| Migration-support component families | 42 | English fallback | Hidden from normal authoring; still build-active |
| Static placeholders with no PIHC3 family | 4 | Localized | Omitted for a loaded project |

The three real child-domain families are `equipment_module`, `equipment_module_category`, and `special_project_reward`. They are now presented as Equipment Modules, Equipment Module Categories, and Special Project Rewards, with corresponding Chinese labels.

The four phantom rows were `assets`, `localization`, `map`, and `music`. They had no physical PIHC3 family, items, or authoring template. Static metadata may still decorate a discovered family, but it no longer seeds a project-backed sidebar row.

## Why the 42 support families were not deleted

The English component rows looked like old duplicates, but a fresh build inventory proved that they are current path-preserving output owners:

- 42 families contain 4,917 modules.
- They inspect 25,635 source files.
- Every family owns generated output.
- Together they own 13,156 artifacts, about 35% of the compiled mod.

For example, `portrait_asset_component` owns 1,917 artifacts, `localization_component` owns 1,763, `event_asset_component` owns 1,733, and `focus_asset_component` owns 1,477. Deleting those directories would silently remove required game files.

The safe migration boundary is therefore active versus visible:

- `active` controls discovery, validation, dependencies, and build emission.
- `visible` controls ordinary authoring navigation.
- Browser payloads remain complete so diagnostics and a future Advanced/Build Support surface can address hidden families.

## Source cleanup and workspace rebuild

An exhaustive comparison of the disposable workspace against the clean canonical PIHC3 worktree found only eight GUI-smoke mutations: a six-file `GUI_SMOKE_ENTITY` module and two temporary Entity scale edits. The scale values were restored to canonical values. The extra module was recoverably moved to:

`/private/tmp/paradev-gui-smoke-quarantine-20260720-1754/GUI_SMOKE_ENTITY`

After cleanup, all 81,263 shared files under `src/modules` matched the canonical PIHC3 source byte-for-byte, and no extra module remained.

The cleaned workspace then completed:

- Dry build: 18,175 modules, 78 collections, 37,555 planned artifacts, zero diagnostics, not blocked.
- Full isolated-SDK build: 18,175 modules, 78 collections, 37,556 emitted artifacts, zero diagnostics, not blocked.
- Output: `/Users/magolor/Projects/ParaDev/PIHC3-GUI-Smoke/build/gui-smoke-mod`.
- Build manifests: `/Users/magolor/Projects/ParaDev/PIHC3-GUI-Smoke/.paradev/.cache/build`.

The source tree remained unchanged by the build apart from the intentional local visibility declarations in `paradev.yaml`.

## Implementation contracts

The SDK now parses an exact boolean `ProjectFamilySpec.visible`, propagates it through generic and custom family types, validates it in `BuildRegistry`, and exposes explicit visibility from both project-browser surfaces. Hidden families stay fully active and retain artifacts, provenance, dependencies, diagnostics, and inspection rows.

The desktop app filters only families explicitly reported as hidden. A hidden canonical family dominates aliases and template metadata, preventing a support family from leaking back through a visible alias. Cached project-browser rows from older packages are rejected when they lack explicit visibility, so an upgrade cannot preserve the old mixed list.

Regression cases cover a hidden family without a component-like name and a visible family whose name ends in `_component`. This proves the behavior is metadata-driven rather than a naming heuristic.

## Verification

- Focused Python registry/project contracts: 277 passed.
- PIHC3 visibility integration: 89 total families, 47 visible, 42 hidden; passed.
- Hidden-family build contract: hidden family remained build-active and emitted artifacts; passed.
- Frontend module/cache contracts: 14 passed.
- Full desktop frontend: 62 files and 1,133 tests passed.
- TypeScript production build: passed; only the existing large-chunk advisory remains.
- Rust/Tauri: 63 tests passed.
- Focused visibility/registry/project/documentation slice: 9 passed against both the local fixture boundary and canonical PIHC3 where applicable.
- Generated Project API reference contracts: 3 passed after refreshing the documented signature.
- Backend subprocess checks: 3 passed with access to HeavenBase's local SQLite cache; their sandbox-only failures were environmental.
- Repository formatting/lint: 162 files unchanged.

The all-Python diagnostic run reported 1,776 passed, one skipped, 76 failed, and four fixture errors. Three test failures shared the stale generated-signature cause corrected in this pass. Three backend failures shared the sandboxed-cache cause described above. One killed-process lock test passed alone and is an xdist/timing failure. The remaining failures and all four setup errors are dominated by PIHC3 migration-contract checks against the gitignored `projects/PIHC3` fixture in this ParaDev worktree. That standalone fixture is at `7a4efe41`, while canonical PIHC3 is 20 commits and 957 changed files ahead at `6441e2d23`; it lacks `scripts/data/pihc2_entity_contract.yaml`, which exactly accounts for the four setup errors. A representative inventory importer that fails on the local fixture passes against canonical PIHC3.

The old fixture was not overwritten because it is outside the selected GUI workspace and bulk replacement would be a separate destructive migration decision.

## Packaged native regression

The exact release bundle reopened the remembered `PIHC3 GUI Smoke` project in Chinese. The accessibility tree reported `模块 47` and contained exactly 47 family buttons. The three formerly untranslated real families appeared as `装备模块`, `装备模块类别`, and `特殊项目奖励`. No button contained `component`, and none of the four phantom families appeared.

Searching normal navigation for `component` returned `模块 0`, proving that hidden support families cannot be recovered through the sidebar filter. Clearing the search restored all 47 rows. Opening `装备模块` succeeded as a preview/source surface with 1,040 directly discovered source files, after which the tab and search state were returned to their neutral starting state.

The package was built with `scripts/build-tauri.bash --headless-dmg --adhoc-sign`. Nuitka, Vite, Rust/Tauri release compilation, application signature verification, DMG checksum verification, read-only mount, mounted-application signature verification, the Applications link, and detach all passed.

| Artifact | Result |
| --- | --- |
| Application | 79 MiB on disk; strict deep signature verification passed |
| Bundled backend SHA-256 | `b0611b5341b65b2c85b97eb9dbde51f80effeddfb9b226ec87f7275317999508` |
| DMG | 80,573,565 bytes |
| DMG SHA-256 | `d08e5d7df7865c85bdbb00dcf62f77cf02222a6a02304370b719ac905b958042` |

This remains a local QA package. Public macOS distribution still requires Developer ID signing, notarization, stapling, and Gatekeeper validation on a clean machine.

## Durable project policy

The 42 `visible: false` declarations are committed in the canonical PIHC3 repository, not only in the disposable GUI workspace. The ParaDev SDK/frontend policy and the PIHC3 manifest change were pushed independently to their existing pull-request branches.

## Remaining boundary

The support families are intentionally absent from the novice sidebar but remain reachable through APIs, builds, diagnostics, and inspection payloads. A dedicated Advanced/Build Support editor is still future work; hiding them from normal navigation does not delete or merge their source ownership.
