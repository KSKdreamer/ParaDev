# Product Vision And Background

Status: draft

## One-Sentence Goal

ParaDev is a HeavenBase-backed toolkit and editor platform for making complex Paradox Interactive mods reproducible, searchable, automatable, and pleasant to author, starting with Hearts of Iron IV and the PIHC3 flagship mod.

## Product Scope

ParaDev is not just a parser library. It is a product program with five connected surfaces:

1. Python package: parser, data model, compiler, validator, asset pipeline, localization, map tooling, HOI4 entities, and stable project APIs.
2. Developer tools: CLI, project manifest, deterministic build graph, diff/parity tools, tests, sample corpora, and documentation.
3. Editor tools: standalone PDX LSP, VS Code extension, webview panels, visual mod editor workflows, and schema-versioned JSON payloads.
4. Knowledge and agent layer: HeavenBase workspaces, search indexes, MCP tools, prompt templates, LLM routing, wiki/game references, localization memory, and project memory.
5. Flagship content program: PIHC3, a clean rebuild of the legacy PIHC2 mod that proves the platform on real content.

## Target Users

- Mod authors who want lower-friction HOI4 content creation without learning every internal file convention first.
- Python developers who want programmable, testable mod generation.
- PIHC maintainers migrating a large production mod with story, art, map, entities, and custom systems.
- Editor users who want interactive focus-tree, map, localization, and asset workflows.
- AI agents that need deterministic tool contracts rather than fragile chat-only instructions.
- Future community contributors who need a normal open-source package and docs path.

## Background: Hearts of Iron IV And PDX Modding

Hearts of Iron IV mods are mostly built from a mix of:

- PDX script files under roots such as `common/`, `events/`, `history/`, `interface/`, `gfx/`, `map/`, `music/`, and `localisation/`;
- localization YAML files with game-specific syntax, language folders, BOM quirks, version suffixes, and format codes;
- image formats such as DDS, TGA, PNG, BMP, and atlas/strip-like assets;
- map data such as provinces, states, strategic regions, terrain, heightmaps, adjacencies, supply, and history files;
- gameplay families such as countries, characters, focuses, ideas, events, decisions, technologies, doctrines, traits, achievements, equipment, and scripted helpers;
- load-order and replacement rules such as descriptor metadata, `replace_path`, and copied static resources.

This makes HOI4 modding a data and tooling problem, not only a code-generation problem. A useful platform must model files, game semantics, assets, localization, build ownership, and editor interactions together.

## Background: Legacy Heaven, AgentHeaven, And HeavenBase

The old Heaven and AgentHeaven line provided useful conventions:

- short, stable helper names for common operations;
- centralized path, file, serialization, database, LLM, and config utilities;
- model/provider routing for LLM work;
- agent-friendly execution and memory patterns.

HeavenBase is the intended successor substrate. It provides:

- a `HeavenBase` workspace boundary;
- logical `Entity` schemas with `object_id`;
- `Catalog` and `MetaSchema` system entities;
- backend-aware storage placement;
- SQL, vector, search, JSON, graph, artifact, and structured logical type direction;
- `CM_HVNB` config;
- MCP toolkit surfaces;
- LLM, prompt, embedding, image, and session utilities;
- extension and backend registration patterns.

The restart should use HeavenBase as the shared data and agent substrate, but must not block basic file-based mod authoring on a heavy database service. HeavenBase should improve metadata, search, indexing, MCP, and structured workflows while Git source files remain inspectable and version-controlled.

## Background: HOI4DEV

HOI4DEV is the legacy HOI4 automation tool. It is valuable because it already encoded many practical solutions:

- resource-first compilation from folders;
- `Add*` domain functions for countries, characters, ideas, focuses, events, decisions, technologies, equipment, special projects, achievements, traits, and models;
- `locs.txt` localization conventions;
- image helpers built around Wand/ImageMagick;
- DDS/TGA handling;
- JSON-like intermediate structures;
- duplicate-key conventions such as `__D1`, `__D2`;
- PIHC-specific generator knowledge and file path habits.

HOI4DEV should be treated as a behavior reference and migration oracle, not as an architecture to copy. The restarted ParaDev should preserve proven output contracts and ergonomics while replacing global state, hidden config, implicit merge rules, and project-specific assumptions.

## Background: PIHC2

PIHC2 is the legacy production mod corpus and the strongest proof requirement for ParaDev. Its canonical authored content is primarily under:

- `/Users/magolor/Documents/Paradox Interactive/Hearts of Iron IV/mod/PIHC2/resources/`
- `/Users/magolor/Documents/Paradox Interactive/Hearts of Iron IV/mod/PIHC2/scripts/`
- `/Users/magolor/Documents/Paradox Interactive/Hearts of Iron IV/mod/PIHC2/hoi4dev_settings/`

Supporting folders such as `__workspace__`, `__materials__`, `steamdown`, and `wiki` should be investigated as references, but not assumed to be canonical.

PIHC2 has enough real content to stress the platform:

- hundreds of focuses, events, decisions, ideas, technologies, equipment entries, opinions, characters, and traits;
- custom systems such as inventory items, superevents, and state lores;
- multilingual localization;
- many art pipelines;
- map, country, history, and strategic-region content;
- scripted helpers, on-actions, interface files, music, and static copy roots.

## Background: Current ParaDev

The current ParaDev codebase is useful evidence, but the user has declared it stale because the project became too messy. It should be mined for:

- parser and formatter behavior;
- test corpus and validation resources;
- project layout and build contract decisions;
- localization parser/termbase lessons;
- image subsystem lessons;
- entity family classifications and generated artifact maps;
- PIHC migration inventories and parity strategy;
- VS Code and LSP boundary decisions;
- simplicity guardrails and agent workflow documents.

It should not be used as the default implementation base. Reusing old code should require a deliberate extraction review with tests proving the behavior is worth preserving.

## Specific Product Goals

### Python Package

The Python package is the source of truth. It should provide:

- PDX tokenization, AST parsing, formatting, and conversion;
- project manifest loading and build context;
- deterministic build graph and artifact manifests;
- localization source parsing, YML output, translation hooks, and termbase integration;
- asset processing and image cache;
- HOI4 game data extraction and validation;
- HOI4 entity authoring and generation;
- map database and map-derived code helpers;
- package-level extension contracts;
- CLI commands that wrap stable APIs.

### LSP

The PDX LSP should be a separate package or workspace. It should provide:

- project discovery through `paradev.yaml`;
- parser-backed diagnostics;
- document symbols;
- hover;
- formatting delegation or coordination with the formatter CLI;
- catalog-backed completion and semantic-token highlighting;
- later references, richer localization key awareness, and HOI4 database help.

It should not own domain logic and should not be embedded inside the VS Code extension.

### VS Code GUI And Mod Editor

The VS Code extension should be a thin client over:

- CLI commands;
- LSP requests;
- schema-versioned JSON payloads;
- local webview panels.

Expected interactive workflows include:

- PDX formatting and diagnostics;
- localization lookup, scan, and translation review;
- focus-tree browse, layout preview, and eventual writeback;
- map and province/state/region selection;
- entity creation wizard;
- asset preview and conversion;
- build, validation, and diff result panels.

The long-term mod editor may live inside VS Code first, but should keep reusable contracts so a future standalone GUI can reuse the same core.

### PIHC3

PIHC3 is the clean flagship project. It should:

- use the generic ParaDev project layout;
- build through ParaDev, not HOI4DEV;
- migrate content from PIHC2 with controlled parity checks;
- keep PIHC-only mechanics in project-local extensions;
- demonstrate the beginner path after migration debt is separated from public package design.

### Agent And MCP Surface

The agent surface should expose deterministic tools:

- inspect project;
- parse/format/check files;
- list and describe entity schemas;
- create or update entities through validated contracts;
- query localization, termbase, HOI4 docs, and build manifests;
- run build/diff/validation;
- use HeavenBase MCP for structured data and memory.

Agents must not edit raw game files by guesswork when a structured operation exists.

## Product Principles

1. Source files are human-readable and Git-owned.
2. HeavenBase stores structured, queryable, searchable, and agent-facing state.
3. Every public feature has one obvious happy path.
4. Every editor payload is versioned.
5. Every generator is deterministic.
6. Every migration wave leaves a durable artifact: spec, validator, test, parity report, schema, or docs page.
7. Project-specific behavior is config-driven and project-local.
8. Version-sensitive HOI4 claims are refreshed from live sources before implementation.
9. Legacy code is evidence, not a dependency.
10. PIHC3 proves the platform but does not define all public APIs.
