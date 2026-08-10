# PIHC3 project-only App builds

Date: 2026-07-30

## Outcome

ParaDev App builds no longer depend on or mutate the external Hearts of Iron IV
launcher descriptor. Full, cached, family-partial, and module-partial
publication all completed successfully against the current PIHC3 project with
strict metadata enabled.

The compatibility SDK/CLI behavior remains available:

- `Project.build(..., sync_launcher_descriptor=True)` is the default.
- CLI builds synchronize by default.
- `--no-sync-launcher-descriptor` selects project-only publication.
- Desktop build command plans and `projects/PIHC3/compile.bash` always select
  project-only publication.
- The synchronous REST build route exposes `sync_launcher_descriptor`.

Project-only publication still writes `descriptor.mod` under the mod output
root and the launcher preview under the hidden build root. It does not read,
lock, claim, create, or replace the external `<project_id>.mod` file or its
ParaDev ownership marker.

## Live PIHC3 build matrix

| Mode | Modules | Collections | Artifacts | Diagnostics | Time |
| --- | ---: | ---: | ---: | ---: | ---: |
| Full/clean | 14,617 | 106 | 35,139 | 0 | 103.27 s |
| Cached | 14,617 | 106 | 35,139 | 0 | 73.44 s |
| Focus family | 738 | 28 | 12,499 | 0 | 46.12 s |
| `focus/FOCUS_C02_PONYVILLE_OPENMIND` | 38 | 1 | 11,071 | 0 | 45.11 s |

For every run, the existing external `PIHC3.mod` and
`.paradev-PIHC3.launcher.json` retained the same bytes and modification time.
The cached run also retained the fingerprints and modification times of seven
representative generated outputs. These are emitted-build timings;
transactional publication and full-plan validation remain included.

## Parsed-source family cache

Cached and targeted builds now reuse lossless parsed module and collection
source bundles from disposable hidden state under
`.paradev/cache/source-families/`. The cache does not store normalized plans,
publication ledgers, or output ownership. Every build still runs the complete
registry normalization, validation, artifact planning, localization
postprocessor, collision checks, and transactional publication path.

The signature covers the complete family tree, slots, metadata contract,
strictness, Python runtime, ParaDev parser/loader code, PyYAML version,
HeavenBase version, and the loaded HeavenBase/localization helper source. This
last check keeps the local editable HeavenBase 0.1.2.1 workflow safe even when
code changes before a version bump. Entries use bounded compressed JSON rather
than pickle; stale, corrupt, oversized, unwritable, or concurrently changing
sources fall back to a fresh parse.

## Source-tree cleanup audit

- Zero physical `_component`, `_asset_component`, `legacy`, or
  `inactive_modules` directories remain under `projects/PIHC3/src`.
- The naming normalizer inspected 14,708 physical source units and reported
  zero folder-name mismatches.
- Source folders use `id - preferred-language title`.
- Seventeen Finder `.DS_Store` files and one generated Python bytecode cache
  were removed outside `.git`.
- A repeat audit after the emitted matrix removed eight newly regenerated
  `.DS_Store` files; the final source re-scan found zero generated debris.
- Historical component identifiers remain only in project extension migration
  declarations such as `retired_families`. They are not source families; they
  let a cached upgrade safely prune outputs from an older component layout.

## Verification

- 944 focused Python SDK, CLI, REST, desktop-contract, architecture, project,
  and collection-template tests passed.
- 19 publication-adversarial and PIHC3 extensibility tests passed.
- The exhaustive Python run reached 2,570 passed and 42 skipped before exposing
  six actionable failures. The six exact failures were repaired and rerun:
  6 passed.
- Desktop: 86 files and 1,409 Vitest tests passed.
- Desktop production TypeScript/Vite build passed.
- Rust format and check passed; 93 Rust library tests passed.
- Generated project, REST, frontend, SDK/CLI, CLI, MCP, catalog, and surface
  contract references match their renderers.
- Parsed-source cache and PDX regression coverage: 251 passed.
- Current fast repository gate: 2,297 passed and 10 platform/fixture tests
  skipped. Three generated-reference assertions in the first run caught
  internal cache controls leaking into the public discovery signatures; cache
  policy was moved behind private `Project` helpers, then the complete fast
  gate passed.

The exhaustive failures were two stale REST expectations, disposable Finder
and Python cache files, an immutable fixture path accidentally changed from its
pinned historical name, and a missing declared `zstandard` bundle dependency
in the local environment. No compiler or artifact-parity failure remained.

## Systematic migration-surface retirement

The authoring project now presents only the current ParaDev model:

- the former 118-file tracked `scripts/` tree and additional one-shot working
  scripts have converged to four supported utilities: two current validators
  or generators and two optional parity reviews;
- all PIHC2 import programs, source-layout migration programs, importer
  contracts, pinned component fixtures, and importer-only tests are retired;
- 84 numbered execution reports under `docs/migration/` are superseded by one
  migration-complete `README.md`; Git remains the historical record;
- 450 `.paradev/import.yaml` files and 228 `.paradev/evidence/*` files were
  removed because no current compiler, SDK, GUI, or extension reads them;
- the remaining 672 module-local hidden files are only current compiler
  routing metadata, diagram editor state, or the Entity catalog:
  `meta.yaml`, `diagram.yaml`, and `entities.json`.

The post-cleanup physical audit found 75 module families, 14,618 module
folders, two collection families, and 90 collection folders. Every folder uses
`id - preferred-language title`; there are zero `_component`,
`_asset_component`, `legacy`, or `inactive_modules` directories, zero naming
mismatches, zero visible metadata-key violations, zero import manifests, and
zero evidence directories.

Post-cleanup emitted builds remain green:

| Mode | Modules | Collections | Artifacts | Diagnostics |
| --- | ---: | ---: | ---: | ---: |
| Full/clean | 14,617 | 106 | 35,139 | 0 |
| Cached | 14,617 | 106 | 35,139 | 0 |
| Focus family | 738 | 28 | 12,499 | 0 |
| `focus/FOCUS_C01_C02_EVERFREE_FIELDTRIP` | 83 | 1 | 11,161 | 0 |

The structural regression suite passed 12 focused tests. The current fast
repository gate passed 2,160 tests with nine native-Windows tests skipped.
The reduced count is intentional: unsupported migration/importer behavior and
its pinned component fixture are no longer part of the product contract.

## Tree-authoring extension ownership

The tree-creation audit corrected an important modeling assumption: focus
trees are collection-owned, while current PIHC3 technology and doctrine nodes
are standalone modules and each MIO module owns one or more organization trait
trees. The App now follows those registered source contracts instead of
forcing every graph into a collection workflow.

- Focus retains its dedicated collection and focus-node authoring flows.
- Technology, doctrine, and MIO graph toolbars open the same guarded
  single-module planner used by normal module authoring.
- The create action remains available for an empty source-backed diagram, so a
  new tree does not require leaving the diagram workspace.
- Diagram authoring behavior is selected through an explicit capability fact
  (`focus-node` or `module`) rather than a technology-only UI branch.
- Doctrine `.paradev/diagram.yaml` initialization moved out of the central
  SDK. The PIHC3 doctrine extension template now declares both its routing
  metadata and hidden diagram state through trusted `system_files`.

The resulting doctrine-family publication compiled 94 modules and 11,037
artifacts with zero collections, diagnostics, or errors. The complete fast
Python gate passed 2,161 tests with nine expected native-Windows skips; the
focused authoring/diagram regression set passed 58 tests; all 86 desktop test
files passed 1,410 tests; and the strict TypeScript/Vite production build
passed.

## Registry-owned diagram providers

Completed 2026-07-31.

Source-backed diagrams are now first-class build-registry capabilities rather
than a second hard-coded family system:

- `ModuleDiagramProvider` declares open-vocabulary ids and aliases, compatible
  families, renderer, projection callback, optional edit planner, and optional
  authoring kind.
- `BuildRegistry` validates, replaces, resolves, and exposes providers through
  `diagram_views_by_family()`.
- `paradev_diagram_provider` is a HeavenBase runtime extension kind.
- PIHC3's focus, technology, doctrine, and MIO extensions explicitly replace
  their profile providers from their own extension folders.
- `Project.module_diagram()` and `Project.edit_module_diagram()` dispatch only
  through the registry. The former focus/doctrine/MIO private dispatch helpers
  were removed.
- Browser family rows carry the resolved `diagram` descriptor. The desktop
  derives tabs, renderer selection, labels, visibility, editability, and
  authoring actions from that descriptor; its four-family capability table was
  removed.
- REST/MCP schemas now accept registered diagram ids as an open vocabulary.
  Runtime providers remain authoritative for intent validation.

The recursive physical audit again found zero `_component`,
`_asset_component`, `legacy`, or `inactive_modules` directories anywhere
under PIHC3 modules, collections, or extensions.

Live registered diagram projection:

| Provider | Nodes | Edges | Blocking diagnostics |
| --- | ---: | ---: | ---: |
| Focus | 738 | 863 | 0 |
| Technology | 300 | 391 | 0 |
| Doctrine | 94 | 122 | 0 |
| MIO | 441 | 868 | 0 |

Technology reports three warnings for edges whose other endpoint is outside
the reviewed PIHC3 sources; these are non-blocking external/base-game
references.

Post-refactor emitted builds, all with launcher synchronization disabled:

| Mode | Modules | Collections | Artifacts | Diagnostics |
| --- | ---: | ---: | ---: | ---: |
| Full/clean | 14,617 | 106 | 35,139 | 0 |
| Cached | 14,617 | 106 | 35,139 | 0 |
| Focus family | 738 | 28 | 12,499 | 0 |
| Technology family | 300 | 0 | 11,899 | 0 |
| Doctrine family | 94 | 0 | 11,037 | 0 |
| MIO family | 7 | 0 | 11,001 | 0 |
| `focus/FOCUS_C01_C02_EVERFREE_FIELDTRIP` | 83 | 1 | 11,161 | 0 |

Verification passed 137 focused Python registry/diagram/architecture tests,
2,165 fast Python tests with nine expected native-Windows skips, all 86
desktop test files with 1,410 tests, and the strict TypeScript/Vite production
build. The Nuitka package-data traversal is retained but now marked `slow`;
it exceeded 15 minutes in this environment and is not part of the App/SDK fast
gate.

## Next high-impact slice

1. Add template-driven relationship defaults to the generic graph create
   flow, allowing a new technology, doctrine, focus, or MIO node to start
   relative to the current selection without a second edit.
2. Add project-owned provider examples for a PIHC3-exclusive graph or
   collection so extension authors can copy one small working folder.
3. Profile and cache only the next safe immutable planning boundary.
   Normalization, cross-family validation, localization closure, collision
   checks, and publication ownership must remain authoritative.
