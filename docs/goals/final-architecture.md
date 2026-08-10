# ParaDev Final Architecture

Status: finalized design draft

Date: 2026-06-06

Purpose: define the smallest extensible architecture for a Python SDK, desktop app, and MCP server that compile feature-oriented Paradox mod sources into game-ready artifacts, starting with Hearts of Iron IV.

## Summary

ParaDev should be a source-to-artifact compiler with one shared Python SDK. The CLI, MCP server, REST API, LSP, VS Code extension, and desktop app are clients of that SDK. No surface owns HoI4 business logic.

The user-facing model is intentionally small:

1. A project contains modules.
2. Modules are grouped into collections when a game feature needs sibling context.
3. Build profiles compile modules and collections into artifacts.

The implementation model is only slightly deeper:

```text
source files -> modules -> collections -> artifacts -> manifests/indexes
```

This matches the HoI4 problem described in `design-considerations.md`: authors want local feature folders, while the game expects global folders such as `common/`, `events/`, `localisation/`, `gfx/`, and `interface/`.

## Architecture Rules

1. The Python SDK is the single source of truth.
2. Public concepts stay small: project, module, collection, artifact, family.
3. Every module family is registered. Built-in HoI4 families and project-local custom families use the same extension path.
4. Metadata is plain structured data. Do not create extra public wrapper classes for metadata, tags, IDs, or source slots unless they enforce real invariants.
5. Collections are first-class build state. Do not hide focus-tree, decision-category, event-namespace, or sprite-bundle logic inside unit compilers.
6. Generated outputs are owned by artifacts and manifests, not by ad hoc file writes.
7. Every output should be traceable back to its source module and source slot.
8. PDX script remains an editable source format. ParaDev may provide structured helpers, but raw PDX escape hatches are required.

## Package Boundaries

```text
src/paradev/
  sdk/          public Python API and view contracts
  project/      project discovery, paradev.yaml, source roots
  pdx/          tokenizer, AST, formatter, diagnostics
  build/        registry, module loading, collections, artifacts, manifests
  games/hoi4/   HoI4 game profile and built-in module families
  hb/           HeavenBase indexes, search, memory, MCP integration
  surfaces/     CLI, MCP, REST, LSP, VS Code, bundle adapters
```

The desktop app talks to REST/OpenAPI or a local bridge backed by the same transport-neutral `api/projects` service; REST is a peer adapter, not the owner of desktop project behavior. MCP tools call the SDK. LSP calls the PDX parser and project diagnostics. All generated editor payloads come from build records and manifests.

The desktop source editor is CodeMirror 6 by default and long-term. The GUI should continue to compose editor behavior through CM6 extensions and `@uiw/react-codemirror`, while ParaDev language semantics stay in the Python SDK/LSP. Monaco is not the main GUI editor path; keep it only as an optional future target for a separate VS Code-like surface that connects to the same backend language service.

## Public API Shape

Keep the first public API compact:

```python
project = paradev.Project.load(path)
result = project.build(profile="hoi4")
```

Family authors register capabilities:

```python
def register(registry):
    registry.add(SupereventFamily())
```

The core public records should stay few:

| Record | Role | Notes |
| --- | --- | --- |
| `Project` | Workspace boundary and build entry point. | Public. |
| `Family` | Registered compiler for one module type. | Public for plugin authors. |
| `Artifact` | One planned or emitted output. | Public in build results. |
| `Module` | Normalized discovered source unit. | Public in manifests/views. |
| `Collection` | Grouped build state. | Public in manifests/views, rarely hand-created. |

Avoid parallel helper front doors such as `build_project(...)`, `compile_mod(...)`, and `run_build(...)` unless a surface adapter needs them internally. Prefer `Project.load(...).build(...)`.

## Source Folder Contract

New source folders should be feature-oriented and readable in Git:

```text
modules/
  focus/
    GER_rearmament - optional note/
      meta.yaml (optional)
      def.txt
      main.loc
      icon.png
      assets/
  focus_tree/
    GER_main/
      meta.yaml (optional)
      def.txt
      focuses/
        GER_rearmament/
          meta.yaml (optional)
          def.txt
          main.loc
          icon.png
```

Legacy-style prefixed folders such as `FOCUS_GER_REARMAMENT - optional note/` may be supported by importers and compatibility scanners, but new docs should teach typed parent folders, logical machine ids, and template-owned optional readable suffixes.

`type` is inferred from typed ancestry, such as `modules/focus/*` or
`modules/focus_tree/*/focuses/*`. `meta.yaml` itself is optional when a module
has no authored metadata. When present, it may contain only a human-facing
field such as `title`; new typed-layout modules should not repeat the inferred
`type`. If a compatibility source declares a different `type` than the path
implies, that is a diagnostic.

### Identity

`id` is not required in `meta.yaml`.

The module object id is deduced from the source folder machine segment:

```text
GER_rearmament - optional note/
```

becomes:

```yaml
object_id: GER_rearmament
note: optional note
```

The stable ParaDev identity is the logical `family/object_id`, not the complete
physical folder spelling. The default authoring-template directory is
`{object_id}`; a project-local template may opt into a readable
`directory` format such as `{object_id} - {title}`. Scaffold payloads preserve
the logical `object_id` and `module_id` and expose the rendered physical name
separately as `folder_name`. Directory rendering preserves the authored title
inside localization and projects only the physical suffix into a portable
form: runtime Clausewitz substitutions and formatting are omitted, reserved
path punctuation is replaced, whitespace is collapsed, trailing dots are
removed, and UTF-8 truncation respects the component byte limit.

Duplicating a module creates a new logical identity by default. The active
Registry family owns the identity rewriter, including path and source-token
projection; the SDK owns only guarded planning, publication, and rollback.
Project-local Entity families inherit the standard capability and may replace
or disable it without adding a ParaDev SDK, CLI, REST, MCP, or desktop family
switch. Exact byte-and-path preservation remains an explicit compatibility
mode rather than the normal authoring workflow.

The active registered family may declare ordered `title_loc_keys`. Those
templates are the single source of truth for browser and GUI display-name
resolution when the family title does not use the plain object-id key. An
explicit empty declaration disables localization-derived titles for dynamic
families and falls back to the persisted folder suffix. This system contract
belongs in hidden extension metadata, never in a module's visible
`meta.yaml`.

Scaffold resolution must find at most one physical folder for a logical id. A
unique existing readable folder is reused for idempotent scaffold plans;
multiple aliases, case-only collisions, and Unicode NFC-equivalent collisions
block instead of selecting one. An object-id-only rename changes the logical
machine segment while preserving an existing readable suffix. When the caller
also supplies a title, rename instead canonicalizes the complete physical name
as `{object_id} - {portable title}`; the same object id is valid when only the
suffix changes. The desktop Name field edits the resolved Registry
`title_loc_keys` localization entry and submits that edit with the
folder-title synchronization through one guarded
`Project.apply_source_draft(..., module_rename=...)` request. It never creates
a visible `meta.yaml` merely to store a display title. A module-local
`.paradev/` directory is reserved for system
metadata and ignored when scaffold checks whether an existing module already
matches; a fresh scaffold does not invent importer provenance there. A family
may derive game-specific IDs from the logical id.
For legacy parity, use optional `game_id`, not `id`, so the difference between
ParaDev object identity and HoI4 script identity remains clear.

### Metadata

Minimal optional `meta.yaml`:

```yaml
title: Rebuild the Ruhr
```

Fuller example:

```yaml
title: Rebuild the Ruhr
tags: [industry, political]
collection: GER_main
owner: GER
priority: 20
game_id: GER_rebuild_the_ruhr
requires:
  - idea:GER_industrial_spirit
after:
  - focus:GER_rhineland
settings:
  icon_fit: cover
```

Shared metadata keys:

| Key | Required | Meaning |
| --- | --- | --- |
| `type` | no | Compatibility declaration for an untyped source layout. Typed module ancestry is authoritative, so new modules omit it. |
| `title` | no | Human-facing label for UI/search. Does not replace localisation. |
| `comment` | no | Optional human-readable notes for developers and future agent generation. Does not compile into game output by default. |
| `tags` | no | Search/editor tags. |
| `collection` | no | Explicit collection id when a family needs grouping. |
| `owner` | no | Country tag, project domain, or owning feature. |
| `priority` | no | Deterministic ordering hint. |
| `game_id` | no | Optional game-facing ID override for legacy parity or special naming. |
| `requires` | no | Symbol dependencies. |
| `after` | no | Build/order dependencies that are not game semantics. |
| `settings` | no | Family-specific compiler settings. |

Rules:

- `type` replaces legacy `kind` when an untyped compatibility source needs an explicit family.
- Folder name replaces required `id`.
- Omit `meta.yaml` when there are no authored metadata values; do not create an empty file.
- Omit metadata that a Registry family can derive unambiguously from one of its
  declared resource slots. The family owns that inference and must report a
  blocking diagnostic when the source is missing, ambiguous, or conflicts with
  an explicit value.
- When required routing cannot be inferred from authored source, a trusted
  Registry template or SDK workflow may maintain it under module-local
  `.paradev/meta.yaml`. Such system metadata is hidden from novice editing and
  must participate in the same guarded create/copy/move transaction as the
  source it routes.
- `collection`, `owner`, and `priority` are optional and family-specific in meaning.
- Unknown metadata keys are warnings by default in loose mode and errors in strict mode.
- Family-specific metadata lives under `settings` unless it is common enough to promote.

## Source Slots

A source slot describes files a family knows how to consume. Slots support exact names, glob patterns, and regular expressions.

Conceptual shape:

```python
Slot(name="def", match="def.txt", required=True)
Slot(name="loc", match="**/*.loc", many=True)
Slot(name="icon", match=r"^(icon|goal)\.(png|jpg|dds|tga|bmp)$", regex=True)
Slot(name="body", match="body.txt", kind="pdx")
```

Matching rules:

1. Exact and glob slots are matched relative to the module folder.
2. Regex slots match normalized POSIX-style relative paths.
3. `many=True` registers every match in deterministic path order.
4. Single image slots prefer common editable formats in this order: `png`, `jpg`/`jpeg`, `webp`, `dds`, `tga`, `bmp`.
5. Slot collisions are diagnostics unless the family explicitly allows shared ownership.
6. A source file can be registered to multiple slots only when a family says so.
7. Optional `kind` values `pdx`, `loc`, and `copy` tell the generic loaders how to parse custom slot names.

Example localisation slots:

```python
Slot("loc", "**/*.loc", many=True)
Slot("loc", "loc/**/*.loc", many=True)
Slot("loc_yml", r"^localisation/.+_l_[a-z_]+\.yml$", regex=True, many=True, kind="loc")
```

This lets every `**/*.loc` file become registered translation source without hand-listing `main.loc`, `extra.loc`, or language-specific files.

## Build Stages

The internal pipeline should be explicit but not exposed as a beginner concept:

1. `discover`: find module folders and source slots.
2. `load`: parse metadata and source files into module records.
3. `normalize`: let families canonicalize loaded module records without changing
   module ids or families.
4. `aggregate`: group modules into collections.
5. `check`: run unit, collection, and project validation.
6. `emit`: write or plan artifacts and manifests.
7. `index`: update HeavenBase/search/editor indexes.

`post_compile` should not be a default stage. If an output needs sibling context, model it as collection compilation. If an output is for future GUI or layout review, emit it as a planning artifact.

Cache-enabled builds may reuse parsed source bundles from hidden derived state
under `.paradev/cache/source-families/`. Reuse is valid only when the complete
source-family content fingerprint, declared slots, accepted metadata keys,
strict-metadata mode, ParaDev loader/parser implementation, Python runtime, and
loaded HeavenBase/localization helper source match. Published dependency
versions, including HeavenBase and PyYAML, are also part of the signature. This
means an editable HeavenBase checkout invalidates derived source entries even
when its package version was not bumped. The cache stores bounded compressed
JSON and lossless PDX dumps, never executable pickle data. Missing, stale,
corrupt, oversized, or unwritable entries fall back to ordinary discovery and
parsing. Full builds bypass cache reads and repopulate validated entries, while
cached and targeted builds may also reuse a finalized artifact plan from hidden
derived state under `.paradev/cache/artifact-plans/`.

Artifact-plan reuse is allowed only for a normal project build whose aggregate
module and collection source signatures, copy inputs, project/profile metadata,
Registry view, family/writer/postprocessor source, runtime dependencies, and
core planner code match exactly. Postprocessors that read state beyond those
inputs must expose `artifact_cache_key(context)`; no hook, an invalid key, or a
failed fingerprint disables plan reuse. PIHC3 localization uses that hook to
fingerprint its resolved external reference roots. Entries are bounded,
checksum-protected JSON/Gzip and contain exact finalized writer payloads, never
pickle or executable code. Cached PDX is stored as its exact rendered text, and
current parsed-source bundles are reattached on read so inspection APIs retain
their normal source/localization/asset views. Corrupt, stale, oversized, or
unwritable plans fall back to ordinary planning without blocking the build.
Full builds always replan and safely refresh the entry. Every mode still runs
target resolution, publication closure, collision/ledger validation,
transactional artifact publication, and canonical manifest emission.

When a validated artifact-plan signature is reused, ParaDev may also reuse the
exact canonical manifest bytes already present in the build root. The hidden
receipt under `.paradev/cache/manifest-publications/` binds the plan signature,
manifest projector implementation, complete canonical manifest inventory, and
every published file's SHA-256. A missing, stale, corrupt, incomplete, or
mismatched receipt falls back to normal projection and atomically refreshes the
receipt. Target tampering is repaired from the canonical projection, and an
unwritable receipt never blocks compilation. This receipt is disposable system
state, not a user-authored manifest or extension contract.

## Family Protocol

A family owns one module type. It declares source slots, validates records, and emits artifacts.

Conceptual protocol:

```python
class Family:
    type: str
    visible: bool = True
    slots: tuple[Slot, ...]
    metadata_keys: tuple[str, ...]
    settings_keys: tuple[str, ...]
    required_settings: tuple[str, ...]
    settings_values: dict[str, tuple[str, ...]]
    settings_normalizers: dict[str, Callable[[object], object]]

    def load(self, module, ctx): ...
    def normalize(self, modules, collections, ctx): ...
    def aggregate(self, modules, ctx): ...
    def check(self, modules, collections, ctx): ...
    def emit(self, modules, collections, ctx): ...
```

Rules:

- `load` does not write files.
- `normalize` may canonicalize module metadata or derive family-owned fields
  such as collection identity from loaded resource slots. It must keep the same
  module ids and families and fail closed when derivation is ambiguous.
- `aggregate` does not write files.
- `check` returns diagnostics, not booleans.
- `emit` returns artifacts; artifact writers handle actual file output.
- A family whose validation and emission share expensive preparation may expose
  one `compile` hook returning `FamilyCompileResult`. The planner invokes that
  hook instead of separate `check` and `emit` calls; ordinary families keep the
  simpler split hooks.
- An artifact writer may additionally expose `render_bytes(artifact)` when it
  owns exact final bytes. It may return `None` for an individual artifact that
  still needs the ordinary `write(artifact, output_root)` staging contract.
  Direct writers may also expose `render_mode(artifact)` when final permission
  bits are part of the artifact contract.
- A writer that already owns a raw SHA-256 of the final file bytes may expose
  `expected_sha256(artifact)`. Publication then streams the retained output and
  skips rendering or staging only on an exact match. Invalid digests fail
  closed; missing or mismatched output uses the ordinary exact publication
  path. HeavenBase deterministic-object hashes are not raw file-byte hashes and
  must not be used for this hook.
- A project postprocessor that can only affect a subset of artifacts should
  expose that scope through the publication transform predicate. Unaffected
  direct artifacts retain the direct path; affected artifacts continue through
  staging and the full transform pipeline.
- Families register through a registry. Do not add central `if type == ...` routing.
- Built-in families and custom project families use the same protocol.
- `visible` controls ordinary discovery and authoring navigation only. A concrete
  family with `visible = False` remains active in discovery, validation, artifact
  planning, emission, source ownership, diagnostics, and scoped/advanced tools.
  Projects must declare this policy as family metadata; GUI adapters must not
  infer it from a family-name suffix.
- Publication-ledger migration state is owned by the persisted extension
  descriptor at `meta.publication.replaces_families`, not by the disposable
  compiler object. The build Registry validates it separately and broadens
  stale-row reconciliation only for a family-wide targeted artifact build;
  narrower module and collection targets keep their normal ownership scope.
- Custom compiler families may declare validated `generated_outputs` contracts
  when emitted artifacts have no single path template. Each contract names the
  artifact type, owner kinds, target root, and optional route, source slots, or
  human-readable description; family inspection marks these rows as generated.
- Family contracts should be inspectable by SDK clients, including source slots,
  top-level metadata keys split into SDK common keys and family-owned keys, the
  unknown-key loose/strict policy, family settings keys, routed setting values,
  and output templates.
- When a family declares `required_settings` or allowed `settings_values`, missing
  or unsupported module settings should produce diagnostics during `check`.
- Generic family helpers may declare per-key `settings_normalizers` so values are
  canonical before routing, validation, manifests, and artifact planning.

## Collections

A collection is build-time grouping. It is required when a final artifact is incomplete without sibling modules.

Initial collection forms:

| Collection form | Examples | Output ownership |
| --- | --- | --- |
| `tree` | focus tree, doctrine tree, technology tree | Collection-owned PDX and layout manifests. |
| `category` | decision category, idea category | Collection-owned grouped script files. |
| `namespace` | event namespace | Collection-owned event files and health manifests. |
| `library` | scripted effects, scripted triggers, scripted localisation | Collection-owned helper files and symbol indexes. |
| `bundle` | sprite bundle, GUI bundle, portrait set | Collection-owned GFX/GUI/asset indexes. |

Collection identity precedence:

1. explicit `collection` in module metadata;
2. collection folder metadata;
3. typed ancestry inference;
4. family-owned semantic inference from a declared resource slot;
5. family default, only when unambiguous.

If two sources of collection identity disagree, strict mode fails and loose
mode warns with deterministic precedence. Family-owned inference must live on
the registered family hook; SDK, desktop, CLI, and MCP clients never parse a
specific family merely to reconstruct grouping.

## Artifacts

An artifact is one output or planned output. It carries path, type, owner, inputs, and content/build action.

Artifact examples:

```text
common/national_focus/GER_main.txt
events/ger_events.txt
common/decisions/GER_industry.txt
localisation/english/GER_rearmament_l_english.yml
gfx/interface/goals/GER_rearmament.dds
interface/paradev_goals.gfx
.paradev/.cache/build/manifests/build.json
```

Artifact ownership:

- Unit-owned: one icon DDS, one small standalone modifier, one portrait derivative.
- Collection-owned: focus tree file, decision category file, event namespace file, sprite bundle.
- Project-owned: descriptor, launcher `.mod`, build summary, source maps, indexes.

Output path collisions are build-level errors unless a merger explicitly owns that artifact type.

## PDX Core

The PDX parser should reuse the v1 prototype direction from `../ParaDev/src/paradev/pdx/`:

- `PDXBlock` is the main public entry point.
- Internally preserve `PDXScalar`, `PDXEntry`, and `PDXBlock`.
- Tokenization should be lenient and BOM-safe.
- Comments, inline comments, operators, scalar types, raw text, and file extension annotations should round-trip.
- Public constructors should include `from_str`, `from_file`, `from_dict`, and `from_tokens`.
- Public exports should include `to_str`, `to_file`, `to_dict`, `to_tokens`, `dump`, `load`, and `clone`.
- `to_dict` may be lossy for simple JSON workflows. `dump` must be lossless for cache/source-map workflows.

The v1 prototype already covers useful HoI4 syntax cases: bare identifiers, strings, numbers, booleans, variables, comparison operators, anonymous blocks, duplicate keys, comments, and `rgb/hsv { ... }` color scalars. The restart should keep those design constraints while tightening public naming and tests.

## Initial Slot Compilers

Implement shared slot compilers before many domain families.

| Slot compiler | Inputs | Normalized output | Priority |
| --- | --- | --- | --- |
| Metadata loader | `meta.yaml`, optional collection metadata | Plain metadata dict plus diagnostics | P0 |
| PDX loader | `def.txt`, `*.pdx`, raw `.txt/.gfx/.gui/.asset` when declared | `PDXBlock` plus source map | P0 |
| Localisation loader | `**/*.loc`, `loc/**/*.loc`, optional existing HoI4 YML | Localisation entries keyed by language and scope | P0 |
| Image loader | `icon.*`, `portrait.*`, `picture.*` | Asset record with dimensions/hash/format | P0 |
| Static copy loader | `copy/**`, `assets/**` when declared | Copy records with hash/provenance | P1 |
| Audio loader | `music.*`, `sound.*` | Asset record and copy/descriptor hints | P2 |
| GUI fragment loader | declared `.gui`/`.gfx` fragments | `PDXBlock` or raw fragment with ownership | P2 |
| Collection descriptor loader | `collection.yaml`, collection `meta.yaml` | Collection defaults and ordering hints | P1 |

## Initial Artifact Compilers

Implement these artifact compilers first:

| Artifact compiler | Outputs | Priority |
| --- | --- | --- |
| PDX text writer | `common/**/*.txt`, `events/**/*.txt`, `interface/**/*.gfx`, `interface/**/*.gui`, `*.asset` | P0 |
| Localisation YML writer | `localisation/<lang>/*_l_<hoi4_lang>.yml` | P0 |
| DDS/TGA image writer | `gfx/**/*.dds`, `gfx/**/*.tga` | P0 |
| Static copy writer | copied assets and passthrough files | P0 |
| Sprite GFX writer | aggregated `spriteType` declarations | P1 |
| Descriptor writer | `descriptor.mod` and launcher `.mod` preview | P1 |
| Manifest writer | unit, collection, artifact, source-map, and build summary JSON | P0 |
| Diagnostic writer | machine-readable build/check reports | P0 |
| Graph/view writer | focus tree, decision category, event namespace, asset bundle views | P2 |
| HeavenBase index writer | module, artifact, loc, asset, and reference index rows | P2 |

## First Domain Families

The first domain families should prove three complexity levels:

| Level | Families | Why |
| --- | --- | --- |
| Simple unit | modifier, trait, opinion modifier | PDX plus optional loc, minimal collection behavior. |
| Asset unit | idea, achievement | PDX plus loc plus icon pipeline. |
| Collection | event namespace, decision category | Required aggregation without GUI layout. |
| Layout collection | focus tree | Required aggregation plus graph/layout payloads. |
| Custom extension | superevent | Proves project-local plugins can emit event, GUI, GFX, loc, audio, and image artifacts. |

Do not start with country or character as the first proof. They are valuable but composite and asset-heavy enough to obscure the core compiler contract.

## Example: Focus Family

Source:

```text
modules/focus_tree/GER_main/
  meta.yaml (optional)
  def.txt
  focuses/
    GER_rearmament/
      meta.yaml (optional)
      def.txt
      main.loc
      icon.png
```

Build behavior:

1. Discover `GER_rearmament` as a `focus` module.
2. Load `def.txt`, `main.loc`, and `icon.png`.
3. Infer `collection = GER_main` from ancestry unless metadata overrides it.
4. Aggregate focuses into the `GER_main` focus-tree collection.
5. Validate duplicate object/game IDs, prerequisites, mutual exclusions, missing loc, icon policy, and layout collisions.
6. Emit:
   - `common/national_focus/GER_main.txt`
   - `localisation/english/GER_rearmament_l_english.yml`
   - `gfx/interface/goals/GER_rearmament.dds`
   - `interface/paradev_goals.gfx`
   - focus-tree view and source-map manifests.

## Example: Superevent Extension

Project extension:

```python
def register(registry):
    registry.add(SupereventFamily())
```

Source:

```text
modules/superevent/FALL_OF_PARIS/
  meta.yaml (optional)
  def.txt
  title.loc
  image.png
  music.ogg
  gui.pdx
```

Metadata:

```yaml
type: superevent
title: Fall of Paris
tags: [war, europe]
owner: FRA
requires:
  - event:france.100
settings:
  image_fit: cover
```

Possible artifacts:

- `events/superevents.txt`
- `common/scripted_effects/superevents.txt`
- `interface/superevents.gui`
- `interface/superevents.gfx`
- `localisation/english/superevents_l_english.yml`
- `gfx/event_pictures/FALL_OF_PARIS.dds`
- `music/superevents.asset`
- `.paradev/.cache/build/views/superevent/FALL_OF_PARIS.json`

The core does not need to know what a superevent is. It only needs registered slots, records, diagnostics, artifacts, and manifests.

## MCP And Desktop Surface

MCP tools should expose structured operations:

```text
inspect_project
list_families
list_modules
describe_module
create_module
check_project
build_project
preview_collection
search_localisation
search_references
```

The desktop app should call equivalent SDK/REST operations and render versioned payloads:

```text
module.list.v1
module.detail.v1
collection.graph.v1
focus-tree.view.v1
loc-scan.view.v1
asset-preview.view.v1
build-diagnostics.view.v1
```

MCP and desktop must not parse raw HoI4 files independently when SDK operations exist.

## Validation

Validation layers:

| Layer | Examples |
| --- | --- |
| Source | missing required slots, malformed YAML, unreadable image, PDX parse errors. |
| Module | missing game ID, invalid metadata, missing required loc keys, bad icon dimensions. |
| Collection | duplicate focus IDs, event namespace collisions, decision/category mismatch, graph cycles. |
| Project | artifact path collisions, localisation key collisions, descriptor problems, replace-path hazards. |
| Reference | unresolved effects/triggers/modifiers/helpers against configured game references. |

Diagnostics should include:

- severity: error, warning, hint;
- source module and slot;
- source span when available;
- artifact path when available;
- stable diagnostic code.

## Manifests

Manifests are product contracts for CLI, MCP, desktop, LSP, migration, and tests.

Required manifests:

```text
.paradev/.cache/build/modules.json
.paradev/.cache/build/collections.json
.paradev/.cache/build/dependencies.json
.paradev/.cache/build/artifacts.json
.paradev/.cache/build/assets.json
.paradev/.cache/build/diagnostics.json
.paradev/.cache/build/localization.json
.paradev/.cache/build/sources.json
.paradev/.cache/build/source-map.json
.paradev/.cache/build/summary.json
```

Each manifest should include a schema id and version. Additive changes are preferred; breaking changes require a new schema version.

## Implementation Order

1. PDX core from v1 prototype constraints: tokenizer, AST, formatter, lossless dump/load, diagnostics.
2. Project spine: `paradev.yaml`, project root discovery, source roots, output roots, profile selection.
3. Build spine: registry, slots, module discovery, artifact model, manifests.
4. Shared slot compilers: metadata, PDX, localisation, images, static copy.
5. Shared artifact compilers: PDX text, loc YML, DDS/TGA, static copy, manifests, diagnostics.
6. Simple families: modifier, trait, opinion modifier.
7. Asset families: idea, achievement.
8. Collection families: event namespace and decision category.
9. Layout family: focus tree.
10. Project-local extension proof: superevent.

## Non-Goals

- Do not invent a replacement language for PDX script.
- Do not make the desktop app a separate compiler.
- Do not force all source files into Python.
- Do not require HeavenBase to build a local file-based mod.
- Do not make HoI4-specific assumptions part of the generic compiler layer.
- Do not implement every family before the build spine and manifests are stable.

## Decision

Adopt a registry-based compiler architecture with folder-based modules, optional metadata, source-slot matching, explicit collections, artifact-owned outputs, and manifest-backed surfaces.

This gives beginners the smallest usable model: add a module, build, fix diagnostics. It gives advanced developers a clean extension model: register a family, declare slots, aggregate collections, emit artifacts, and expose the results through the same SDK, desktop, and MCP contracts.
