# ParaDev Short-Term Plan

Status: Linear sync source

Date: 2026-06-07

Purpose: define the next implementation slices for the ParaDev foundation and provide issue bodies for the `ParaDev` Linear project in the `Talirian` workspace.

Linear map: [../plans/linear.md](../plans/linear.md)

## Ordering

Start with infrastructure that every later feature depends on:

1. HeavenBase-aligned CLI and config foundation.
2. PDX tokenizer/AST/formatter, referencing ParaDev v1 behavior and tests.
3. Project manifest and source discovery.
4. Build graph, artifacts, diagnostics, and manifests.
5. First slot compilers for metadata, PDX, localization, and static copy.
6. First SDK/CLI usable package workflow.
7. SDK module template scaffolding for continuing existing projects.
8. CodeMirror 6 GUI editor foundation plus an app-owned desktop build lifecycle over SDK/LSP/frontend contracts.
9. PIHC3 bootstrap skeleton and parity baseline.
10. Continuous user manual and onboarding docs.

This order keeps public APIs small and avoids writing game-family compilers before the parser, config, and build records are stable.

## Current PIHC3 checkpoint (2026-08-03)

- Doctrine now follows the project-local HeavenBase extension pattern used by
  Technology: one Entity owns authored definitions, localization, previews,
  shared PDX support, route inference, compilation, and diagram projection.
- The stale aggregate land/air Doctrine source, separate hidden
  `doctrine_definition` family, and 43 pre-1.17 nodes that emitted no PDX are
  removed. The 51 current modules are the only land/air definition source.
- Standalone subdoctrine creation is now available through the shared
  `diagram-node` capability. Creating from a selected doctrine installs one
  minimal child module and updates the parent-owned outgoing path through one
  guarded compound transaction; no family-specific desktop path exists.
- The next tree-authoring slice is to reuse this Registry-owned compound
  transaction for other parent-owned relationship formats while continuing
  the MIO/Technology/Focus UX audit.
- Collection authoring is no longer a Focus-renderer exception. Registered
  diagram providers may publish `scope_authoring_kind="collection"`, and the
  desktop exposes the same collection-template, rename, guarded removal,
  source-editing, and partial-build paths from that capability. PIHC3 now
  publishes authoring-ready collection templates for both Focus trees and
  Decision categories.
- Collection-owned localization is now first-class across SDK, REST, MCP, and
  desktop. One Registry-resolved v2 target contract handles modules and
  collections, so Decision categories and Focus trees use the same guarded
  cross-language table without raw-file or family-specific UI logic.

## Issue 1: Integrate HeavenBase CLI And Config Foundation

Linear title: `Foundation: integrate HeavenBase CLI and config contracts`

Linear issue: [TAL-290](https://linear.app/talirian/issue/TAL-290/foundation-integrate-heavenbase-cli-and-config-contracts)

Labels: `foundation`, `cli`, `config`, `heavenbase`

Priority: high

Depends on: none

### Goal

Make ParaDev's CLI and config entry points follow the HeavenBase style while preserving the repo's uv-first wrapper model.

### Scope

- Inspect HeavenBase's CLI/config patterns in `/Users/magolor/Utils/HeavenBase/HeavenBase`.
- Decide the minimal ParaDev config namespace and defaults.
- Route shared infrastructure defaults through HeavenBase/`CM_HVNB` where appropriate.
- Keep ParaDev project-specific config thin and explicit.
- Add CLI smoke commands that prove config can be read and projected as JSON.

### Candidate Files

- `src/paradev/config.py`
- `src/paradev/cli.py`
- `src/paradev/sdk/project.py`
- `src/paradev/hb/__init__.py`
- `tests/test_config.py`
- `tests/test_cli.py`
- `README.en.md`

### Acceptance Criteria

- `uv run paradev config list` returns deterministic JSON-safe config rows.
- `uv run paradev cfg get paradev.project.name` works through the supported config path.
- Public examples use `heavenbase` conventions where shared infrastructure is involved.
- No conda, bare pip, or generated requirements edits are introduced.
- README CLI examples stay current.

### Verification

```bash
rtk bash scripts/test.bash
rtk bash scripts/flake.bash --ci
rtk uv run paradev config list --json
rtk uv run paradev cfg get paradev.project.name
```

## Issue 2: Port And Harden The PDX Core From ParaDev V1

Linear title: `Foundation: implement PDX tokenizer, AST, formatter, and round-trip tests`

Linear issue: [TAL-291](https://linear.app/talirian/issue/TAL-291/foundation-implement-pdx-tokenizer-ast-formatter-and-round-trip-tests)

Labels: `foundation`, `pdx`, `parser`

Priority: high

Depends on: Issue 1

### Goal

Implement `src/paradev/pdx/` as the first real language platform slice, using ParaDev v1 as a behavior reference rather than a direct architectural dependency.

### Scope

- Mine `/Users/magolor/Utils/ParaDev/src/paradev/pdx/` and `/Users/magolor/Utils/ParaDev/tests/test_pdx_parser.py`.
- Preserve the useful v1 public shape: `PDXBlock` as primary entry point, with internal scalar/entry/block records.
- Preserve lossless `dump`/`load`, lossy `to_dict`, comment handling, duplicate-key handling, BOM-safe parsing, and token round trips.
- Add parser diagnostics instead of only raising generic exceptions.
- Cover `.txt`, `.gfx`, `.gui`, and `.asset` samples.

### Candidate Files

- `src/paradev/pdx/__init__.py`
- `src/paradev/pdx/token.py`
- `src/paradev/pdx/parser.py`
- `src/paradev/pdx/ast.py`
- `src/paradev/pdx/format.py`
- `tests/test_pdx_token.py`
- `tests/test_pdx_ast.py`
- `tests/test_pdx_roundtrip.py`
- `demos/assets/pdx/`

### Acceptance Criteria

- `PDXBlock.from_str(...).to_str()` works on representative PDX snippets.
- `PDXBlock.dump()` and `PDXBlock.load(...)` preserve comments, operators, scalar types, and duplicate entries.
- `PDXBlock.to_dict()` provides a JSON-safe lossy projection with deterministic duplicate-key encoding.
- Parser failures produce structured diagnostics with source span where available.
- Tests include v1-derived snippets but do not import v1 code at runtime.

### Verification

```bash
rtk bash scripts/test.bash
rtk bash scripts/flake.bash --ci
rtk uv run python - <<'PY'
from paradev.pdx import PDXBlock
block = PDXBlock.from_str('focus = { id = GER_test cost = 10 }')
assert 'GER_test' in block.to_str()
print(block.to_dict())
PY
```

## Issue 3: Implement Project Manifest And Source Discovery

Linear title: `Foundation: implement paradev.yaml project loading and source discovery`

Linear issue: [TAL-292](https://linear.app/talirian/issue/TAL-292/foundation-implement-paradevyaml-project-loading-and-source-discovery)

Labels: `foundation`, `project`, `sdk`

Priority: high

Depends on: Issue 1

### Goal

Make `Project.load(path)` discover a ParaDev workspace, load `paradev.yaml`, and expose deterministic source roots without building artifacts yet.

### Scope

- Define the minimal `paradev.yaml` schema for `project_id`, `title`, `game`, `source_roots`, `output_root`, and `build_root`.
- Implement upward root discovery from a path.
- Add JSON-safe project view payloads for CLI/MCP/desktop.
- Keep authored source files as Git-owned truth.
- Do not introduce database requirements for basic project loading.

### Candidate Files

- `src/paradev/project/__init__.py`
- `src/paradev/sdk/project.py`
- `src/paradev/surfaces/cli.py`
- `src/paradev/cli.py`
- `tests/test_project.py`
- `demos/assets/projects/minimal/paradev.yaml`
- `README.en.md`

### Acceptance Criteria

- `Project.load(path)` works for a project root and a nested file path.
- Missing `paradev.yaml` produces a contextual error.
- `uv run paradev project <path> --json` returns stable project fields.
- The schema is documented in README or a focused docs section.

### Verification

```bash
rtk bash scripts/test.bash
rtk bash scripts/flake.bash --ci
rtk uv run paradev project demos/assets/projects/minimal --json
```

## Issue 4: Implement Build Graph, Artifact, Diagnostic, And Manifest Core

Linear title: `Foundation: implement build graph records and manifests`

Linear issue: [TAL-293](https://linear.app/talirian/issue/TAL-293/foundation-implement-build-graph-records-and-manifests)

Labels: `foundation`, `build`, `artifacts`

Priority: high

Depends on: Issues 2 and 3

### Goal

Create the build spine that later module families will use: modules, collections, artifacts, diagnostics, source maps, and build summaries.

### Scope

- Add minimal records for `Module`, `Collection`, `Artifact`, `Diagnostic`, and `BuildResult`.
- Implement a registry for families and artifact writers.
- Implement dry-run build planning before filesystem output.
- Emit stable JSON manifests under `.paradev/.cache/build/`.
- Validate artifact path collisions at build level.
- Keep family-specific HoI4 behavior out of the generic build core.

### Candidate Files

- `src/paradev/build/__init__.py`
- `src/paradev/build/records.py`
- `src/paradev/build/registry.py`
- `src/paradev/build/plan.py`
- `src/paradev/build/manifest.py`
- `src/paradev/sdk/project.py`
- `tests/test_build_records.py`
- `tests/test_build_manifest.py`

### Acceptance Criteria

- A test family can register and emit a planned artifact.
- Dry-run build returns a `BuildResult` without writing generated files.
- Manifest output includes modules, collections, artifacts, diagnostics, source map, and summary.
- Duplicate artifact paths produce a blocking diagnostic.

### Verification

```bash
rtk bash scripts/test.bash
rtk bash scripts/flake.bash --ci
```

## Issue 5: Implement Initial Source Slot And Artifact Writers

Linear title: `Foundation: implement metadata, PDX, localization, and copy slot compilers`

Linear issue: [TAL-294](https://linear.app/talirian/issue/TAL-294/foundation-implement-metadata-pdx-localization-and-copy-slot-compilers)

Labels: `foundation`, `compiler`, `localization`

Priority: medium

Depends on: Issues 2, 3, and 4

### Goal

Implement the first reusable source-slot loaders and artifact writers so the first simple module family can be built next.

### Scope

- Implement slot matching with exact, glob, and regex modes.
- Implement `many=True` deterministic source registration, especially for `*.loc`.
- Add metadata loader for `meta.yaml`.
- Add PDX loader using the new `PDXBlock`.
- Add localization source loader for `.loc`.
- Add static copy loader/writer.
- Add PDX text writer and manifest/diagnostic writers.

### Candidate Files

- `src/paradev/build/slots.py`
- `src/paradev/build/artifacts.py`
- `src/paradev/localization/__init__.py`
- `src/paradev/pdx/__init__.py`
- `tests/test_slots.py`
- `tests/test_artifact_writers.py`
- `tests/test_localization_loader.py`
- `demos/assets/modules/`

### Acceptance Criteria

- Exact, glob, and regex slot matching are covered by tests.
- `*.loc` files register in deterministic order.
- `meta.yaml` uses `type`, inferred folder identity, optional `game_id`, and optional `collection`/`owner`/`priority`.
- PDX artifacts can be emitted from a `PDXBlock`.
- Static copies preserve relative path and hash metadata.

### Verification

```bash
rtk bash scripts/test.bash
rtk bash scripts/flake.bash --ci
```

## Issue 6: Ship First SDK/CLI Usable Package Workflow

Linear title: `Foundation: ship first SDK/CLI usable package workflow`

Linear issue: [TAL-296](https://linear.app/talirian/issue/TAL-296/foundation-ship-first-sdkcli-usable-package-workflow)

Labels: `foundation`, `sdk`, `cli`, `release`

Priority: high

Depends on: Issues 2, 3, 4, and 5

### Goal

Turn the current SDK/CLI foundation into a first usable package path for a HoI4 modder who is comfortable with command lines and light Python.

### Scope

- Define the first supported install/development environment, including how `heavenbase` is resolved outside this repo.
- Add a project bootstrap command or equivalent documented SDK helper that creates `paradev.yaml`, source roots, output roots, build roots, and one valid starter module.
- Emit descriptor and launcher `.mod` preview artifacts for the tiny project.
- Keep dry-run as the default, but make the `--emit-artifacts --emit-manifests` path produce a complete tiny runnable mod output.
- Add a Python SDK example that performs the same workflow as the CLI.
- Make package release status explicit: version, build artifact, supported APIs, and unsupported alpha caveats.

### Candidate Files

- `src/paradev/cli.py`
- `src/paradev/sdk/project.py`
- `src/paradev/project/__init__.py`
- `src/paradev/build/artifacts.py`
- `src/paradev/build/manifest.py`
- `src/paradev/games/hoi4/__init__.py`
- `tests/test_cli.py`
- `tests/test_project.py`
- `tests/test_project_build.py`
- `tests/test_sdk_examples.py`
- `demos/assets/projects/`
- `README.en.md`
- `docs/workflows/build-flow.md`
- `docs/user-manual/`

### Acceptance Criteria

- `rtk uv build` succeeds and the generated wheel includes the SDK/CLI package files needed for the alpha workflow.
- A documented command initializes a tiny HoI4 project from an empty folder or documented fixture.
- `rtk uv run paradev build <project> --emit-artifacts --emit-manifests --json` produces output-root game files and build-root manifests without blocking diagnostics.
- The tiny output includes descriptor/launcher metadata or a documented preview artifact sufficient to explain how the mod would be installed.
- The same flow is covered by a short Python SDK example using `Project.load(...).build(...)`.
- README and user manual point to the workflow without relying on internal developer-only context.

### Verification

```bash
rtk bash scripts/test.bash
rtk bash scripts/flake.bash --ci
rtk uv build
rtk uv run paradev project demos/assets/projects/minimal --json
rtk uv run paradev build demos/assets/projects/minimal --emit-artifacts --emit-manifests --json
rtk uv run python - <<'PY'
from paradev.sdk import Project
result = Project.load("demos/assets/projects/minimal").build(emit_artifacts=True, emit_manifests=True)
assert not result.blocked
print(result.summary.to_dict())
PY
```

## Issue 6A: Add SDK Module Template Scaffolding

Linear title: `Foundation: add SDK module template scaffolding`

Linear issue: [TAL-298](https://linear.app/talirian/issue/TAL-298/foundation-add-sdk-module-template-scaffolding)

Labels: `foundation`, `sdk`, `docs`

Priority: high

Depends on: Issue 6 and the continuous user-manual issue.

### Goal

Give Python SDK users a generic way to initialize new source module folders from authoring templates, with GUI/CLI clients using the same contract instead of hard-coded commands per module type.

### Design

- Keep build families and authoring templates separate. Families describe compiler behavior and emitted artifacts; authoring templates create source files under `src/modules/<family>/<object_id>/`.
- Provide built-in default templates for system families, starting with a minimal HoI4 idea template.
- Allow project-local custom templates in `paradev.yaml` so different module types can require different arguments and users can define their own templates.
- Keep `Project.create_module(...)` as the minimal user-facing Python SDK verb. The CLI now exposes `templates` for inspection and `scaffold` for dry-run/write plans, but richer interactive argument entry remains deferred.
- Return JSON-safe dry plans with diagnostics before writing, so GUI, MCP, REST, and scripts can inspect or confirm the operation later.

### Scope

- Add SDK template inspection and module-scaffold APIs.
- Parse project-local template definitions from top-level `paradev.yaml` `templates`.
- Validate template ids, family ids, argument declarations, file paths, and missing values.
- Write files only when the plan is not blocked and `write=True` is requested.
- Update the user manual with the existing-project workflow: add two new ideas from Python.
- Add targeted tests for built-in templates, custom templates, missing arguments, and path safety.

### Candidate Files

- `src/paradev/sdk/project.py`
- `src/paradev/sdk/templates.py`
- `tests/test_project.py`
- `tests/test_sdk_examples.py`
- `docs/user-manual/sdk-python.md`
- `docs/user-manual/modules-and-collections.md`
- `docs/plans/linear.md`

### Acceptance Criteria

- `Project.load(...).templates()` lists built-in and project-local module templates.
- `Project.load(...).scaffold_module("hoi4:idea/basic", "GER_industry_spirit", values={...}, write=True)` creates a valid idea module folder with metadata, PDX, and localization files.
- A project-local template can declare different required/default arguments and render multiple files.
- Missing required arguments return a blocked scaffold plan without writing partial files.
- Unsafe custom template paths are rejected at project load.
- Docs explain the Python-first `create_module(...)` workflow, the CLI `templates`/`scaffold` companion commands, and when callers should use full template ids.

### Verification

```bash
rtk uv run pytest tests/test_project.py::test_project_templates_list_builtin_authoring_templates tests/test_project.py::test_project_scaffold_module_writes_builtin_idea_template tests/test_project.py::test_project_scaffold_module_supports_project_local_template_args tests/test_project.py::test_project_scaffold_module_blocks_missing_required_args tests/test_project.py::test_project_manifest_rejects_unsafe_scaffold_template_file_path -q
rtk uv run pytest tests/test_sdk_examples.py::test_project_add_two_ideas_with_sdk_templates_example -q
rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk tests/test_project.py tests/test_sdk_examples.py
```

## Issue 7: Bootstrap PIHC3 Project And Parity Baseline

Linear title: `PIHC3: bootstrap clean project skeleton and parity baseline`

Linear issue: [TAL-297](https://linear.app/talirian/issue/TAL-297/pihc3-bootstrap-clean-project-skeleton-and-parity-baseline)

Labels: `pihc3`, `migration`, `project`, `foundation`

Priority: high

Depends on: Issue 6

### Goal

Instantiate the PIHC3 migration plan as an executable ParaDev project skeleton before importing large legacy domains.

### Scope

- Create `projects/PIHC3/` with a real `paradev.yaml`, clean source roots, output root, build root, and migration notes folder.
- Record the PIHC2 source paths, compiled `PIHC_dev` baseline path, HOI4 version, descriptor metadata, and DLC assumptions.
- Produce a first legacy file inventory and hash manifest for PIHC2 and compiled `PIHC_dev`.
- Produce a source-to-output map by PIHC2 chapter script, starting with `C00` and the first tiny generated/copy fixtures.
- Add one tiny generated fixture and one copied static fixture that build through ParaDev.
- Define the copy-overlay baseline policy for roots temporarily kept under `copies/`.
- Keep PIHC-only behavior out of `src/paradev`; use project-local extension hooks when needed.

### Candidate Files

- `projects/PIHC3/paradev.yaml`
- `projects/PIHC3/src/`
- `projects/PIHC3/copies/`
- `projects/PIHC3/docs/migration/README.md`
- `projects/PIHC3/extensions/`
- `docs/resources/00-resources-and-references.md`
- `docs/resources/04-pihc3-source-cutover.md`
- `docs/user-manual/pihc3.md`
- `tests/test_project_build.py`
- `tests/test_sdk_examples.py`

### Acceptance Criteria

- `Project.load("projects/PIHC3")` succeeds.
- `rtk uv run paradev summary projects/PIHC3 --json` returns a valid summary payload.
- `rtk uv run paradev build projects/PIHC3 --emit-manifests --json` writes build manifests without requiring legacy imports.
- PIHC2 and compiled `PIHC_dev` evidence paths and hash inventory outputs are documented.
- The first migration note explains which legacy chapter/output slice is represented by the tiny generated and copied fixtures.
- The PIHC3 user-manual page explains how a modder continues the project without reading HOI4DEV internals.

### Verification

```bash
rtk bash scripts/test.bash
rtk bash scripts/flake.bash --ci
rtk uv run paradev project projects/PIHC3 --json
rtk uv run paradev summary projects/PIHC3 --json
rtk uv run paradev build projects/PIHC3 --emit-manifests --json
```

## Completed Follow-Up: Fast Cached Publication

Linear: ongoing usability goal

Priority: urgent

Depends on: the retained publication ledger, artifact writers, and manifest
projection.

### Goal

Make repeated PIHC3 builds feel responsive without adding a second compiler or
GUI-owned cache and without weakening exact-output or crash-recovery guarantees.

### Scope

- Retain validated publication rows in memory across safe output/build/
  postprocessor checkpoints instead of reparsing the complete ledger each time.
- Project artifact ledger rows once per result and pass those rows through
  validation, staging, checkpoint, and reconciliation boundaries explicitly.
- Compare deterministic manifest bytes before replacing an unchanged manifest.
- Keep private staging storage bounded and progress limited to user-visible
  checkpoints.
- Re-profile before changing targeted planning or adding another derived cache;
  cached builds must still perform normalization, validation, artifact planning,
  postprocessing, and publication safety.

### Acceptance Criteria

- Full, cached, family, and module builds preserve exact PIHC3 output digests
  and zero-diagnostic counts.
- Interrupted output, build-root, postprocessor, ledger, and manifest writes
  remain recoverable through the existing pending transaction contract.
- A cached full build improves by at least another 20% from the recorded
  66.33-second reference run on the same machine, with phase evidence recorded.
- A desktop-progress build stays within 5% of the no-progress build and does
  not emit per-artifact JSONL events.
- No duplicate compiler, publication path, or GUI-side cache is introduced.

### Verification

```bash
rtk bash scripts/test.bash tests/test_artifact_writers.py tests/test_publication_adversarial.py tests/test_project_build.py -q
rtk bash scripts/test.bash
rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --no-sync-launcher-descriptor --summary
```

### Outcome (2026-08-10)

- Added one internal projected-publication plan and explicit checkpoint
  transaction to the existing SDK path. The transaction retains validated
  rows after each durable write; it does not add a compiler, cache, or GUI
  publication implementation.
- Removed redundant staging-path filesystem resolution only after the artifact
  batch validates every path for traversal and Windows portability. Direct
  writer targets, anchored publication, returned-path validation, and retained
  root checks remain intact.
- Changed desktop builds to request the compact summary payload, made
  `summary_view()` project only `summary.json`, and skipped atomic replacement
  of byte-identical manifests.
- PIHC3 cached publication with desktop JSONL reached 52.89 seconds, 20.3%
  faster than the 66.33-second reference and 34.9% faster than the original
  81.28-second baseline. The no-progress run was 53.12 seconds, a 0.4%
  difference, and the progress stream remained at 98 events.
- Clean/full, cached, Technology-family, and
  `technology/TECHNOLOGY_FIREARM_I` builds completed with zero diagnostics and
  preserved the same 33,436 compiler-owned output artifacts. The complete
  compiler-owned output digest is
  `ba17e0ffda128cc5b142f244d36de0ced7775335635fdd530ab4bee47ef83038`.
- The broad gates passed with 2,414 Python tests plus 9 expected macOS skips
  and 1,510 desktop tests. The focused writer/publication/project gate passed
  210 tests.

## Completed Follow-Up: Stabilize Desktop Build Lifecycle

Linear: ongoing usability goal

Priority: urgent

Depends on: the desktop build facade, frontend `build.*` operations, and native process ownership.

### Goal

Let a mod author start a PIHC3 build, continue working elsewhere in ParaDev, and return to clear progress and Interrupt controls without understanding process ids or build internals.

### Scope

- Own build presentation state at app-shell lifetime rather than Build-page lifetime.
- Key runs by project root and run identity so project switching cannot leak status across workspaces.
- List and reconcile every active or retained terminal full/partial run before enabling new build controls.
- Keep polling while the Build rail is unmounted and recover automatically after a renderer/webview reload within the same native app process.
- Preserve generated confirmation policy for Build and Interrupt, and keep terminal history attributed to the project that started the run.
- On graceful native app close, cancel and reap all app-owned build process groups.
- Treat continuation across a full native-process exit, crash, or relaunch as an explicit non-goal; do not market renderer reload recovery as process-restart persistence.

### Candidate Files

- `src/paradev/desktop/builds.py`
- `src/paradev/sdk/frontend_api.py`
- `src/paradev/surfaces/rest.py`
- `src/paradev/gui.py`
- `apps/desktop/host/macos_app.js`
- `apps/desktop/src/App.tsx`
- `apps/desktop/src/buildPage/`
- `apps/desktop/src/services/paradev.ts`
- `tests/test_desktop_api_selection.py`
- `tests/test_native_web_bridge.py`
- `tests/test_gui_launcher.py`
- `tests/test_gui_macos.py`

### Acceptance Criteria

- A full build remains visible and interruptible after leaving and returning to the Build rail.
- A renderer/webview reload within the same native process recovers every active full and partial run automatically.
- Runs from another project never appear as the selected project's current build.
- Full, partial, and same-target conflicts are scoped to one normalized project root; independent projects can build concurrently.
- Artifact and manifest emission holds one stable SDK source snapshot and is serialized for filesystem-equivalent output roots, build roots, and eligible external HoI4 launcher descriptor targets, including across independent project processes.
- New build controls remain disabled until initial recovery succeeds or presents an actionable error.
- Each terminal run is added to the correct project's history once and refreshes only that project's visible diagnostics.
- Graceful native-app shutdown interrupts and reaps every app-owned build process group; no child compiler is left running.
- Relaunching a new native app process does not claim or continue runs from the previous process.

### Verification

```bash
rtk npm --prefix apps/desktop run test:unit -- --run src/buildPage/BuildPage.test.tsx src/components/AppShell.test.tsx src/services/paradev.test.ts
rtk bash scripts/test.bash tests/test_desktop_api_selection.py tests/test_native_web_bridge.py tests/test_gui_launcher.py tests/test_gui_macos.py -q
rtk npm --prefix apps/desktop run build
```

### Outcome (2026-08-10)

- Moved build-run presentation ownership to the long-lived React app shell,
  while keeping the Python/native process registries authoritative. Polling,
  recovery, history, refresh, start, and interrupt state now survive Build-rail
  unmounts without introducing a frontend process registry.
- Added global active/retained-run recovery for renderer reloads, durable
  best-effort presentation checkpoints for native-process restart detection,
  project-root isolation, causal terminal sequences, bounded history, and
  stale-response protection for concurrent starts, polls, and interrupts.
- Scoped full/partial/same-target conflicts by filesystem-equivalent project
  roots in the Python registry. Independent projects remain concurrent, while
  the existing SDK source snapshot and cross-process publication/launcher
  locks serialize shared filesystem mutations.
- Made graceful installed-app and native-web shutdown close the registry before
  signalling, stop every owned process group, escalate and reap descendants,
  remove registry-owned temporary files, and reject later starts.
- Verified the complete desktop suite, focused Python desktop/native-web and
  installed-host lifecycle tests, source-snapshot and cross-process
  filesystem-lock tests, and a production TypeScript/Vite build.

## Completed Follow-Up: Durable Desktop Authoring Sessions

Linear: ongoing usability goal

Priority: urgent

Depends on: SDK browser/template contracts, the module editor, diagram editor,
workspace tabs, and the native exit bridge.

### Goal

Let a PIHC3 author move between projects, tabs, and editor surfaces without
losing a draft or applying one against changed source, and make every app-exit
path explicit while authoring work or a write is in progress.

### Scope

- Own module and diagram session state at app-shell lifetime, keyed by canonical
  project root and family.
- Preserve dirty entities, inline and batch creation, diagram history, and
  owned blob resources while their views unmount.
- Serialize family mutations across module and diagram views and expose one
  shared busy state.
- Keep dirty or busy orphan tabs reachable; dispose clean sessions before
  removing their tabs and make disposal failures retryable.
- Detect diagram base changes and missing source entities before writes can
  overwrite external changes.
- Treat only complete family refreshes as authoritative absence; filtered
  Catalog pages and searches must not turn omitted dirty rows into false
  missing-source conflicts.
- Return each canonical source read with a descriptor-stable size and
  nanosecond modification-time revision; retain that pair for text edits,
  existing replacements, and guarded removals, while new replacements use
  `expected_absent=true`.
- Reconcile successful backend mutations into retained session state even when
  the originating component unmounts before the response settles.
- Apply multi-file source drafts transactionally, invalidate the complete
  derived Catalog before changing any touched module, and return explicit
  refresh-required status after source success.
- Guard browser unload and installed system-WebView quit/window-close flows, with a
  retrying renderer reservation/activation lease. Before activation, normal
  native exit remains blocked fail-closed; exit requests are emitted only after
  the frontend listener exists. Bind each pending request to the acknowledged
  active lease and one-use nonce, and require a live heartbeat while its dialog
  is open. Bound only the non-destructive native confirmation acquire phase;
  once cleanup starts, pin the request and keep the full application shell
  modal and inert until definitive failure or process exit.

### Acceptance Criteria

- Switching rail, project, or module/diagram surface preserves the correct
  project-family draft and never leaks it into another checkout with the same
  project id.
- A mutation in either family view makes both views inert until it settles; a
  second overlapping Apply is rejected.
- Backend removal of a modified or removal-draft entity produces a visible,
  non-writable source conflict; backend restoration clears it.
- A paged or filtered Catalog result never fabricates a missing-source
  conflict, and a source changed outside ParaDev cannot be overwritten by a
  retained draft.
- A changed diagram base cannot be overwritten by retained dirty history.
- Clean orphan tabs release their resources before disappearing; dirty, busy,
  or cleanup-failed sessions remain reachable.
- Successful Apply state survives editor unmount and an unsuccessful later
  phase preserves only the unapplied drafts; a failed Catalog phase cannot
  advance a queued rename or release an unacknowledged image resource.
- If a later mutation fails, earlier mutations are rolled back only while they
  still match ParaDev's exact mutation token; newer external edits are
  preserved and incomplete recovery exposes its retained path. A successful
  filesystem request leaves any configured derived Catalog explicitly stale,
  blocks Catalog reads until Refresh, and reports failed or unverified status.
- Browser unload, native menu quit, keyboard quit, and window close all warn
  for dirty or busy work; native confirmation must match the active lease and
  exit-request nonce. A failed dialog retry must rotate to a fresh acknowledged
  nonce idempotently, including after a lost bridge response. A missed
  heartbeat preserves the lease for that retry or a fresh close request, and
  only a subsequently unacknowledged request retires the dead renderer lease.
- Native confirmation performs no cleanup unless both lifecycle locks, the
  exact acknowledged nonce, and the renderer begin signal are acquired within
  five seconds. After cleanup starts, cancel, release, expiry, retry, renderer
  replacement, a second confirmation, and renderer-await loss cannot unlock or
  strand the transaction; successful cleanup is followed by worker-owned
  native exit, while failure preserves a retryable request.
- In-memory session history is bounded and its process-restart limitation is
  documented honestly.

### Verification

```bash
rtk npm --prefix apps/desktop test -- --run
rtk npm --prefix apps/desktop run build
rtk bash scripts/test.bash tests/test_native_web_bridge.py tests/test_gui_launcher.py tests/test_gui_macos.py -q
rtk bash scripts/smoke-macos-installed-app.bash \
  --wheel dist/python/paradev-0.1.0.0.dev0-py3-none-any.whl
```

### Outcome (reverified 2026-08-10)

- The React app shell owns bounded project-root/family authoring sessions;
  module and diagram editors are disposable views over the same draft,
  history, resource, conflict, and busy state.
- Complete Catalog refreshes, descriptor-stable source revisions, diagram-base
  fingerprints, and transactional SDK mutations prevent retained drafts from
  overwriting missing or externally changed PIHC3 source.
- Cleanup-first orphan handling keeps dirty, busy, or failed-cleanup work
  reachable. Successful backend phases reconcile before view lifetime or
  resource cleanup can hide their result.
- Browser and installed-app exit paths use the shared dirty/busy snapshot. Native exit
  confirmation remains fail-closed through renderer leases, acknowledged
  one-use nonces, liveness heartbeats, bounded pre-cleanup acquisition, and a
  pinned cleanup/exit phase.
- Current verification passed the focused renderer lifecycle, SDK
  project/desktop transaction, loopback-host, installed-app lifecycle, complete
  desktop, and production TypeScript/Vite gates. The detailed
  architecture and earlier full PIHC3 evidence remain recorded in
  `docs/progress/2026-07-26-desktop-authoring-session-lifecycle.md`.

## Completed Follow-Up: Consolidate Built-in PIHC3 Family Overlays

Priority: urgent

Depends on: HeavenBase 0.1.2.2 Registry loading and the built-in HoI4 Idea and
Event persistence contracts.

### Outcome (2026-08-10)

- Removed the title-only `PIHC3Idea` and `PIHC3Event` Entity wrappers and their
  empty HeavenBase extension definitions. The built-in module/family schema is
  now the only persistence owner for these standard HoI4 families.
- Kept one thin project compiler overlay per family for PIHC3-only resource
  slots, shared Idea PDX routing, Event collection/module output paths,
  Registry-owned field hints, authoring templates, and replacement hooks.
- Fresh HeavenBase installation resolves the two build-family targets and no
  longer exposes `pihc3-idea` or `pihc3-event` Entity modules. An isolated cold
  Catalog refresh materialized 765,033 rows with only the canonical `hoi4`
  extension and its 16 Entity types.
- Cached full, both changed family targets, and representative Idea/Event
  module targets completed with zero diagnostics. The 33,436 compiler-owned
  output artifacts retained digest
  `ba17e0ffda128cc5b142f244d36de0ced7775335635fdd530ab4bee47ef83038`.

## Completed Follow-Up: Compact the PIHC3 HeavenBase Catalog

Priority: urgent

Depends on: HeavenBase 0.1.2.2 Entity storage, the canonical `hoi4` extension,
and current Catalog query/completion contracts.

### Goal

Make first PIHC3 Catalog refresh and editor recovery materially lighter without
adding a second database, shadow index, lossy symbol projection, or GUI-owned
cache.

### Scope

- Keep every PDX symbol as a first-class registered HeavenBase Entity row and
  preserve the existing `pdx-symbol` query and completion payloads.
- Replace the repeated generic JSON payload for PDX symbols with supported
  typed Entity fields and derive Catalog discovery fields from those columns.
- Keep all other HoI4 Catalog entity types on the existing generic projection.
- Preserve fresh-write/public-upsert parity, atomic refresh, stale-read
  rejection, paging, and bounded completion behavior.
- Benchmark the same 20,000-symbol fixture before and after the change, then
  verify a cold PIHC3 Catalog refresh and completion/query parity.

### Acceptance Criteria

- The 20,000-symbol fixture preserves all rows and public payloads while
  reducing SQLite size by at least 20% from the 38,596,608-byte baseline.
- A cold PIHC3 refresh retains 454,836 PDX symbols and zero diagnostics with no
  second persistence or indexing path.
- Catalog query hydration and PDX completion labels/details match the previous
  public contract, including absent optional fields.
- The focused HeavenBase/LSP gates and repository-wide Python gate pass.

### Verification

```bash
rtk bash scripts/test.bash tests/test_hb.py tests/test_lsp.py -q
rtk bash scripts/test.bash
rtk bash scripts/flake.bash --ci --paths src/paradev/hb tests/test_hb.py tests/test_lsp.py
```

### Outcome (2026-08-10)

- Replaced only the generic `hoi4-pdx-symbol` JSON payload with the explicit
  registered `Hoi4PdxSymbol` Entity. Catalog fields are derived from typed
  columns, and every other HoI4 Entity keeps the existing generic projection.
- Preserved public query/completion payloads, absent optional fields, and
  pre-normalization JSON Catalog reads through one provider-safe field mapping.
- Closed initial-write visibility with the existing stale-marker contract, so
  readers cannot observe a partial first Catalog and clean failures remain
  retryable.
- The exact 20,000-symbol fixture fell from 38,596,608 to 29,167,616 bytes
  (24.43%); the target table fell 66.36%, with all rows retained.
- A cold isolated PIHC3 write completed in 762.93 seconds with 765,033 Catalog
  rows, all 454,836 PDX symbols, zero diagnostics, and an immutable
  1,283,936,256-byte database. Real typed hydration and completion probes
  succeeded before the disposable database was deleted.
- The focused 102-test HeavenBase/LSP gate, 2,421-test standard Python gate,
  and 2,577-test slow-inclusive Python gate passed, with 9 expected
  native-Windows skips on macOS. The repository-wide Black/Flake8 gate also
  passed.

## Completed Follow-Up: Accelerate PIHC3 Catalog Batches At The HeavenBase Owner

Priority: urgent

Depends on: the typed PIHC3 PDX-symbol Entity and HeavenBase 0.1.2.2 Catalog
writer contract.

### Goal

Reduce the first PIHC3 Catalog refresh without a second store, a ParaDev-owned
persistence bypass, lossy projection, parallel database writers, or another
cache.

### Scope

- Profile the exact typed writer workload and distinguish ParaDev projection
  cost from HeavenBase materialization, Catalog derivation, and backend writes.
- Remove repeated owner-side configuration resolution from per-row Catalog and
  SQLite JSON paths.
- Add an explicit public fresh-Catalog assertion that omits only prior-Catalog
  lookup when the caller owns a new database, while preserving the merge-safe
  default and every downstream write/validation stage.
- Capability-gate ParaDev so the local refactored HeavenBase uses the public
  mode and the published 0.1.2.2 wheel retains its existing compatibility path.
- Prove exact synthetic rows and one isolated PIHC3 database with real query and
  completion reads.

### Outcome (2026-08-10)

- Profiling found roughly 70,000 configuration reads in a 5,000-row write:
  Catalog identifier length was resolved once per row and text-backed JSON
  encoding resolved presentation indentation for approximately 13 columns per
  Catalog row.
- HeavenBase now snapshots identifier length once per batch, uses compact
  persistence JSON directly, and exposes `catalog_mode="fresh"`. Fresh mode
  skips only prior-Catalog lookup; Entity materialization, derives, routing,
  backend ordering, graph validation, and Catalog persistence are unchanged.
  The default remains merge-safe.
- The exact 20,000-row public workload fell from 16.155 to 3.298 seconds
  (79.6%) and from 22,962,176 to 21,819,392 bytes, retaining all 20,000 Entity
  and 20,000 Catalog rows.
- The isolated PIHC3 write fell from 762.93 to 228.55 seconds (70.0%). It
  retained all 765,033 Catalog rows, including 454,836 typed symbols, with zero
  diagnostics and exact physical/logical counts. The immutable database was
  1,268,346,880 bytes. A three-row hydrated query and a real `ai_will_do`
  completion both returned the typed `hoi4-pdx-symbol` Entity before the
  temporary database was deleted.
- Exact peak RSS was 2,254,143,488 bytes. The prior 1.45 GB number was a sampled
  observation rather than a process peak, so they are not treated as directly
  comparable; build/planning memory remains a separate profiling target.
- Local and published-wheel ParaDev Catalog/LSP gates both passed 103 tests.
  HeavenBase passed its 963-test fast tier and 1,158-test full tier, with only
  policy-declared environment/external skips, plus formatting and documentation
  checks. ParaDev's repository-wide standard tier passed 2,422 tests with 9
  expected native-Windows filesystem skips on macOS; the slow-inclusive tier
  passed 2,578 tests with the same skips. The published wheel does not yet
  contain the new public mode, so clean-install throughput will receive this
  improvement after the next HeavenBase release.

## Continuous Issue: Maintain HoI4 Modder User Manual

Linear title: `Continuous: maintain HoI4 modder user manual`

Linear issue: [TAL-295](https://linear.app/talirian/issue/TAL-295/continuous-maintain-hoi4-modder-user-manual)

Labels: `continuous`, `documentation`, `manual`, `cli`, `sdk`

Priority: urgent

Depends on: none; update during every public SDK/CLI workflow change.

### Goal

Maintain a stable markdown manual interface for a HoI4 modder who is familiar with CLI/Python basics and wants to start or continue a ParaDev project such as PIHC3.

### Scope

- Keep `docs/user-manual/README.md` as the manual table of contents and current learning path.
- Add step-by-step pages for install/environment, project creation, project continuation, source module layout, build/diagnostics, SDK examples, PIHC3 continuation, and troubleshooting.
- Every public CLI command or SDK workflow promoted in README or build-flow docs must have a manual entry or a clear "not ready" note.
- Document desktop-first build, progress, navigation recovery, Interrupt, and shutdown behavior in plain language that does not require a run id or command-line knowledge.
- Manual examples must use copyable commands with `rtk` where appropriate and Python snippets that run under `uv`.
- Manual pages should explain concepts from the user's perspective first: project, module, collection, artifact, diagnostic, source map, and build output.
- PIHC3 manual pages should separate migration-only tasks from normal mod authoring tasks.
- Treat stale commands, missing screenshots/outputs, and unexplained diagnostics as tracked documentation bugs.

### Candidate Files

- `docs/user-manual/README.md`
- `docs/user-manual/getting-started.md`
- `docs/user-manual/project-layout.md`
- `docs/user-manual/modules-and-collections.md`
- `docs/user-manual/build-and-diagnostics.md`
- `docs/user-manual/sdk-python.md`
- `docs/user-manual/pihc3.md`
- `docs/user-manual/troubleshooting.md`
- `docs/README.md`
- `README.en.md`
- `docs/workflows/build-flow.md`

### Acceptance Criteria

- The manual index exists and states the target reader, current alpha scope, and recommended reading order.
- A user can follow the manual to inspect the minimal demo project with CLI and Python.
- A desktop user can start a build, leave and return to the Build rail, read progress, interrupt an active full build, and understand that closing the app cancels rather than resumes it later.
- The manual explains how to continue PIHC3 once the bootstrap project exists.
- Each five-hour loop that changes public SDK/CLI behavior either updates the manual or records why the behavior is internal-only.
- The manual links back to architecture docs only for deeper context; beginner steps do not require reading roadmap or legacy docs.

### Verification

```bash
rtk rg -n "paradev|Project.load|PIHC3|diagnostics|build" docs/user-manual README.en.md docs/workflows/build-flow.md
rtk uv run paradev summary demos/assets/projects/minimal --json
rtk uv run python - <<'PY'
from paradev.sdk import Project
payload = Project.load("demos/assets/projects/minimal").summary()
assert payload["schema"] == "paradev.build.summary.v1"
print(payload["summary"])
PY
```

## Deferred Until After These Issues

- Full country and character compilers.
- Full DDS/TGA conversion and Wand/ImageMagick image operations beyond copy/metadata inspection.
- Full event namespace, decision category, and focus-tree semantics beyond the current scaffold behavior.
- Focus-tree layout writeback and GUI editing.
- Map/world data compilers.
- Superevent project-local extension proof.
- Build continuation across a full native-app process restart; graceful close intentionally cancels app-owned builds.

## Linear Sync Notes

These issues have been created in the `Talirian` workspace under the `ParaDev` project. If duplicate open issues appear later, update existing issues instead of creating new ones.
