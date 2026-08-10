# HeavenBase Architecture

Status: draft

## Architecture Goal

The restarted ParaDev should be a Python-first modding platform whose structured data, search, MCP, and memory surfaces are backed by HeavenBase. The package must still work as a normal local tool: a user should be able to install it, format files, build a project, and run tests without understanding the full database architecture.

## Layer Model

### 1. File And Parser Layer

Owns:

- PDX tokenization and AST;
- comments and duplicate-key preservation;
- formatting and conversion;
- source-file classification;
- parser diagnostics.

Does not own:

- HOI4 gameplay semantics;
- editor UI state;
- HeavenBase storage details.

### 2. Project And Build Layer

Owns:

- `paradev.yaml`;
- project root discovery;
- build context;
- copy overlay rules;
- generated output root;
- build graph and artifact manifests;
- deterministic rebuilds.

Does not own:

- family-specific gameplay transformations;
- PIHC-specific migration logic;
- GUI rendering.

### 3. Game Package Layer

Owns:

- HOI4-specific file contracts;
- entity family schemas;
- game version profiles;
- map data model;
- validation rules;
- output path policies.

Future Paradox games should be added as sibling game packages, not as `if game == ...` sprawl inside every subsystem.

### 4. HeavenBase Workspace Layer

Owns:

- structured project metadata;
- entity schemas and rows;
- source-file and artifact catalogs;
- localization memory;
- asset metadata and derivatives;
- map databases;
- HOI4 reference indexes;
- agent memory;
- MCP toolkit surfaces;
- query and search backends.

Does not own:

- Git source as opaque binary truth;
- direct mutation of files without build-layer coordination;
- editor-only rendering state.

### 5. Surface Layer

Owns:

- CLI;
- LSP;
- VS Code extension;
- MCP tools;
- docs and examples.

All surfaces should call stable Python contracts. They must not duplicate domain logic.

## Recommended Repository Shape

The restart can live in a new repo or a clean worktree. Suggested top-level shape:

```text
paradev/
  pyproject.toml
  src/paradev/
    pdx/
    project/
    build/
    games/hoi4/
    assets/
    localization/
    knowledge/
    hb/
    cli/
  packages/
    pdx-lsp/
    vscode-paradev/
  docs/
  tests/
  examples/
  projects/
    PIHC3/
```

If a monorepo is too heavy at first, keep `pdx-lsp` and `vscode-paradev` separate but pin their contracts in this repo.

## Project Layout

The old approved layout remains a sound starting point:

```text
<project>/
  paradev.yaml
  compile.bash
  src/
  assets/
  copies/
  scripts/
  system/
    compile.py
  .paradev/
    .cache/
      build/
      hb/
```

Restart adjustments:

- `.paradev/.cache/hb/` may hold local HeavenBase workspace files and indexes.
- `src/` remains authored truth for ParaDev-native content.
- `copies/` is a compatibility layer, not a permanent source model.
- `assets/` holds source assets and raw creative inputs.
- `system/` contains project-local compile hooks and extension registration.
- `scripts/` contains one-time migration and operator tools.

## HeavenBase Data Model

The first schema pack should define these logical entities.

### System Entities

| Entity | Purpose |
| --- | --- |
| `project` | Project id, game, root, title, output path, active version, default language. |
| `game-version` | HOI4 version profile, supported version range, known validation profile. |
| `source-file` | Path, kind, hash, owner, parse status, language, game root. |
| `build-run` | Build invocation, config snapshot, start/end, status, diagnostics summary. |
| `build-artifact` | Generated path, source owners, hash, artifact kind, replace/copy/native mode. |
| `diagnostic` | Parser, validation, migration, and build diagnostics. |

### PDX Entities

| Entity | Purpose |
| --- | --- |
| `pdx-document` | Parsed document metadata and AST hash. |
| `pdx-symbol` | Named blocks, keys, scopes, symbol positions. |
| `pdx-reference` | Static links between symbols where detectable. |
| `pdx-pattern` | Known templates, snippets, and lint patterns. |

### Localization Entities

| Entity | Purpose |
| --- | --- |
| `loc-entry` | Key, language, text, source path, scope, status. |
| `loc-key` | Cross-language key record and ownership. |
| `term-concept` | Multilingual concept id, tags, notes. |
| `term` | Concept term in one language, preferred status, normalized text. |
| `translation-run` | LLM translation metadata, prompt, term constraints, review status. |

### Asset Entities

| Entity | Purpose |
| --- | --- |
| `asset` | Source asset path, media type, dimensions, hash, owner. |
| `asset-derivative` | DDS/TGA/strip/output asset derived from a source. |
| `asset-recipe` | Reproducible transformation parameters. |
| `image-cache-entry` | Cache key, source hash, dimensions, output format. |
| `generated-media-run` | AI or video generation run metadata and provenance. |

### HOI4 Domain Entities

| Entity | Purpose |
| --- | --- |
| `hoi4-entity` | Generic identity row for game entities. |
| `entity-family` | Family schema, prefix, source slots, artifact contracts. |
| `entity-collection` | Focus tree, decision category, event namespace, technology branch, doctrine track, or asset bundle. |
| `country` | Tag, history, color, ideology, flags, AI, units, map links. |
| `character` | Character id, roles, portraits, traits, country binding. |
| `focus` | Focus node data and tree membership. |
| `event` | Event id, namespace, type, chain, scheduling, pictures. |
| `decision` | Decision id, category, icon, visibility, cooldown, effects. |
| `idea` | Idea id, category, law chain, icon, modifiers. |
| `technology` | Technology id, folder/path, position, prerequisites. |
| `doctrine` | Doctrine id, track, tier, mastery hooks. |
| `equipment` | Equipment, archetype, module, upgrade records. |
| `trait` | Trait subtype, role applicability, exclusivity. |
| `achievement` | Achievement id, conditions, icon, localization. |
| `scripted-helper` | Scripted effects, triggers, localisation, on-actions. |
| `map-province` | Province id, color, terrain, state link. |
| `map-state` | State id, provinces, owner, resources, buildings, history. |
| `strategic-region` | Region id, provinces, weather, air/naval links. |

### Knowledge Entities

| Entity | Purpose |
| --- | --- |
| `hoi4-reference-page` | Wiki, game file, patch note, and internal reference provenance. |
| `hoi4-effect` | Effect signature, parameters, examples, source version. |
| `hoi4-trigger` | Trigger signature, scopes, examples, source version. |
| `hoi4-modifier` | Modifier key, scope, type, source version. |
| `template` | Entity or script template with parameters and docs. |

## Storage Policy

Use local-first defaults:

- SQLite for structured metadata and small projects;
- local vector/search backend for embeddings and fuzzy lookup;
- file artifacts in Git or `.paradev/cache`;
- optional Postgres, LanceDB, Elasticsearch, Milvus, or other backends only after the local path is stable.

HeavenBase placement should be field-level where useful:

- identifiers, status, paths, and short fields in SQL;
- long text in SQL or document storage;
- embeddings in vector backends;
- image bytes in files, with artifact metadata in HeavenBase;
- graph edges either as HyperG-like fields or explicit edge entities.

## Python API Shape

Public examples should be short:

```python
import paradev as pdv

project = pdv.open_project("projects/PIHC3")
project.format("common/national_focus/c01.txt")
project.build()
project.validate()
```

HeavenBase access should be explicit but not mandatory:

```python
import paradev as pdv

project = pdv.open_project("projects/PIHC3")
ws = project.workspace()
rows = ws.query_json("loc-entry", {"filter": {"key": {"$match": "C01"}}}).execute()
```

Game-specific authoring should be discoverable:

```python
from paradev.games import hoi4

mod = hoi4.open_mod("projects/PIHC3")
mod.entities.create("idea", name="C01_FAST_TRAINING")
mod.build()
```

## CLI Shape

Initial CLI:

```bash
paradev init
paradev project inspect
paradev project source-index
paradev format <path>
paradev parse <path> --json
paradev build
paradev validate
paradev diff --against <path>
paradev loc scan
paradev asset convert <input> <output>
paradev entity families <path>
paradev entity scan <path>
paradev hb status
paradev hb schema-pack
paradev hb catalog-preview <path>
paradev hb catalog-smoke <path>
paradev hb catalog-write <path>
paradev hb catalog-refresh <path>
paradev hb catalog-query <path>
```

Do not expose dozens of commands before the core model is stable. Prefer fewer commands with strong JSON output.

The catalog preview surface is read-only and currently available through
`paradev hb catalog-preview <path> --json`. The seed emits deterministic
project, source-file, build-artifact, build-dependency, loc-entry, asset,
sprite, pdx-document, pdx-symbol, build-graph-node, build-graph-edge,
hoi4-entity, and diagnostic rows from package-owned scanners, planners, and
validators before any workspace write surface is added.
Diagnostic rows are deduplicated across source indexing, localization scanning,
game-aware entity validation, and build-plan artifact diagnostics.

The catalog smoke surface is read-only and currently available through
`paradev hb catalog-smoke <path> --json`. It boots an explicit in-memory
HeavenBase workspace from that preview, enables the `hoi4` extension, upserts
one `hoi4-*` entity row per preview row, and checks Catalog/MetaSchema counts.
It does not write workspace files.

The catalog write surface is available through
`paradev hb catalog-write <path> --json`. It creates a new local SQLite
HeavenBase database from the same preview under `.paradev/.cache/hb/catalog.sqlite` by
default. It refuses to overwrite an existing database, WAL, or SHM file.

The catalog refresh surface is available through
`paradev hb catalog-refresh <path> --json`. It writes a replacement catalog to a
sibling staging SQLite database, checkpoints that file, and only then replaces
the final catalog database. This keeps repeated local catalog rebuilds explicit
without weakening the default no-overwrite write command.

The catalog query surface is available through
`paradev hb catalog-query <path> --json`. It opens the written SQLite catalog in
read-only mode and returns Catalog rows with optional entity, name, tag, and
limit filters. Short entity selectors such as `source-file` normalize to the
persisted `hoi4-source-file` entity. This exposes the minimal persisted index
users need to inspect PDX symbols, localization keys, source files, and planned
build outputs without learning HeavenBase internals.

## JSON Contract Policy

Every payload consumed by VS Code, LSP, or MCP should include:

- `schema`: stable schema id;
- `version`: semantic payload version;
- `project_id`;
- `game`;
- deterministic `object_id` or source path;
- diagnostics in a typed list;
- explicit compatibility notes when fields are deprecated.

The VS Code extension should reject unknown breaking major versions instead of silently guessing.

## MCP Strategy

Start with small toolkits:

- HeavenBase schema-pack toolkit;
- HeavenBase catalog-preview toolkit;
- project inspect and source-index toolkit;
- localization lookup toolkit;
- entity read/create toolkit;
- build and validation toolkit;
- memory/research toolkit backed by HeavenBase.

Expose destructive operations only after undo, review, or dry-run policy exists.

## LLM Strategy

LLM use should sit behind HeavenBase or ParaDev abstractions:

- translation with term constraints;
- writing assistant with lore and mechanics retrieval;
- template suggestion;
- image prompt generation and asset generation metadata;
- code or PDX generation only through validated previews.

Generated content must carry provenance, model/preset, prompt, inputs, and review status.

## What To Avoid

- A hidden global active mod path.
- `project_id.startswith(...)` behavior in package code.
- editor TypeScript that understands HOI4 semantics better than Python.
- unversioned JSON payloads.
- database-only source of truth for authored mod content.
- a large generic entity base class that erases real family differences.
- migration scripts mixed into the reusable package.
