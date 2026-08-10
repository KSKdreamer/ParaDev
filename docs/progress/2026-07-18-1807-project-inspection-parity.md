# Project Inspection Parity

Date: 2026-07-18 18:07 SGT

## Outcome

The Tauri desktop now sends one lossless inspection request through the versioned Python backend and delegates validation and dispatch to `Project.inspect`. This removes the duplicated Rust inspection catalog, exposes all 19 HeavenBase-era inspection kinds and all 36 current filters, and preserves JSON values such as `false`, `null`, zero, Unicode, and nested data.

The bridge itself is ready, but the real PIHC3 catalog probe found a separate P1 scalability block: a complete `catalog-preview` response is roughly 584 MB. That payload is a valid SDK response, not an appropriate GUI transport or entity-browser model.

## Fixed

- Removed the Rust allowlist that recognized only 15 of 19 inspection kinds.
- Removed the Rust filter mapping that recognized only 11 of 36 filters.
- Stopped dropping `false`, `null`, and empty values before SDK dispatch.
- Kept `code` and `diagnostic_code` distinct instead of translating both to the CLI `--code` flag.
- Added deterministic camelCase-to-snake_case normalization and collision rejection at the Python boundary.
- Kept incidental SDK stdout off protocol stdout and added concurrent large stdout/stderr regression coverage in Rust.
- Added contract-driven tests so future HeavenBase inspection kinds and filters cannot silently disappear from the desktop bridge.

## PIHC3 Evidence

| Probe | Result |
| --- | --- |
| `inspections` through `paradev.desktop.backend.v1` | 19 kinds and 36 unique filters; PIHC3 project identity preserved |
| `diagnostics` with `severity=error`, `strictMetadata=false`, and `moduleId=null` | zero diagnostics; false and null accepted through the real protocol |
| `catalog-preview` through the real protocol | succeeded in about 86 seconds; roughly 584 MB of JSON |
| Catalog counts | 18,038 modules, 18,038 HOI4 entities, 78 collections, 15,437 assets, 497 sprites, 122,529 localization entries, and 720,730 PDX symbols |
| Bounded `catalog-query` attempt | correctly reported that `.paradev/.cache/hb/catalog.sqlite` has not been materialized for PIHC3 |

The catalog result confirms broad PIHC3 entity coverage, but it also shows that a novice-safe browser needs an explicit catalog refresh/materialization action, indexed queries with mandatory limits, paging, and lazy detail loading. The GUI must not request or deserialize the complete preview.

## Verification

| Gate | Result |
| --- | --- |
| Complete Python suite | 1,293 passed; two warnings |
| Repository Black and Flake gates | passed |
| Complete frontend Vitest gate | 782 passed across 52 files |
| Frontend typecheck and production build | passed; existing chunk-size warnings only |
| Rust tests, default feature set | 36 passed |
| Rust tests, bundled backend | 35 passed |
| Rust production Clippy, default and bundled | passed with warnings denied |
| Rust format check | passed |
| Independent read-only bridge review | no actionable findings |

`cargo clippy --all-targets` still reports two pre-existing test-target lints (`CommandSpec` is imported but unused in the test module, and `run` follows the test module). Production default and bundled targets are clean; those unrelated test-layout findings are not hidden as part of this inspection change.

## Next

- Add a bounded catalog refresh/query workflow and require finite page sizes at the desktop boundary.
- Build the entity browser on `catalog-query` or scoped project-browser payloads, with virtualized lists and lazy details.
- Measure and cap Python-backend stdout before an accidental unbounded response can exhaust desktop memory.
- Re-run entity creation, editing, build, and diagram flows in the native Tauri window as soon as macOS is unlocked.
