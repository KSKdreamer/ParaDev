# ParaDev Roadmap

Status: foundation

Date: 2026-06-07

Purpose: state ParaDev's long-term, mid-term, and short-term goals in brief, verifiable terms.

## Evidence Basis

This roadmap is grounded in:

- current ParaDev documentation under [docs/README.md](../README.md);
- PIHC2 authored resources, chapter scripts, and HOI4DEV settings as legacy source evidence;
- HOI4DEV behavior for PDX conversion, localization, image processing, generators, and compile conventions;
- the local HOI4 install, currently recorded as `Case Green v1.18.2.0.41f5 (b781)` in `launcher-settings.json`;
- modern agent-editor product references such as Cursor agent windows, OpenAI Codex, and VS Code agent windows.

HOI4 wiki and patch-note facts must be refreshed during implementation. Roadmap entries should not freeze version-sensitive game mechanics.

## Long-Term Goals

| Goal | Accomplishment criteria |
| --- | --- |
| Python package as the single source of truth | `src/paradev` owns parser, project/build, localization, assets, entities, HOI4 game package, HeavenBase integration, and public Python APIs; all other surfaces call these contracts. |
| Stable CLI and automation surface | `paradev` commands cover inspect, format, parse, build, validate, diff, localization, assets, entities, and HeavenBase status with machine-readable output where useful. |
| PDX language platform | Parser, AST, formatter, diagnostics, duplicate-key preservation, comment preservation, and structured conversion work on representative `.txt`, `.gui`, `.gfx`, and `.asset` corpora. |
| Localization and termbase platform | `.loc` and HOI4 YML round-trip reliably; termbase lookup, fuzzy/prefix search, AI translation provenance, and review status are available from Python, CLI, GUI, and MCP. |
| Asset and map platform | DDS/TGA/image/video transforms, asset cache, map database, province/state/region browsing, map validation, and generated code helpers are reproducible and indexed. |
| Entity and plugin ecosystem | Generic entity contracts support major HOI4 families, while extension APIs support custom systems such as PIHC inventory items, superevents, and state lores without core hacks. |
| Standalone PDX LSP | Editor-neutral LSP provides diagnostics, document symbols, hover, formatting, catalog-backed completion, and semantic-token highlighting; references and richer HOI4 reference help remain future work. |
| Installable desktop app | The Python wheel owns the loopback API and packaged UI; `paradev dashboard` defaults to a thin macOS system-WebView window, `--install-app` installs a Finder/Dock app, and `--app` is the Chromium fallback. `paradev-gui` remains a compatibility entry point. React/Vite remains build-time only, and Windows native packaging is deferred. CodeMirror 6 remains the main GUI editor. |
| HeavenBase knowledge and MCP layer | Project metadata, artifacts, localization memory, assets, HOI4 references, prompts, and agent memory are queryable through HeavenBase workspaces and MCP tools. |
| Community and multi-game path | Public docs, examples, extension guide, and HOI4-first release exist before Victoria 3, Stellaris, or broader Paradox game packages are promoted. |
| Compilable and playable PIHC3 flagship | PIHC3 builds through ParaDev, launches as a HOI4 mod, preserves approved PIHC2 content intent, and has migration parity reports for each migrated family. |

## Mid-Term Goals

| Goal | Accomplishment criteria |
| --- | --- |
| SDK/CLI alpha package | A HoI4 modder with basic CLI/Python fluency can install ParaDev in the documented environment, initialize or open a project, inspect modules, build a tiny runnable mod, read diagnostics, and call the same workflow from Python without reading internal code. |
| Project and build spine | `paradev.yaml`, root discovery, deterministic build graph, `copies/` overlay, descriptor and launcher `.mod` preview generation, artifact manifests, and parity reports work on fixture projects and PIHC3 bootstrap slices. |
| PDX and text processing core | Tokenizer, AST, formatter, parser diagnostics, duplicate-key policy, and corpus tests are implemented before entity compilers depend on them broadly. |
| Localization core | Key ownership, `.loc` source, YML output, language aliases, duplicate/missing diagnostics, termbase constraints, and translation metadata are usable from Python and CLI. |
| Asset core | Wand/ImageMagick-backed DDS/TGA support, resize/crop/extend/compose operations, guarded optional dependencies, cache invalidation, and asset metadata indexing are implemented. |
| Entity engine V1 | Entity family stages are explicit: discover, parse, normalize, aggregate, validate, compile, manifest, and index. Initial families include simple, collection, and layout-heavy cases. |
| Pluggable extension model | Family plugins, project-local hooks, migration importers, and editor payload builders register capabilities instead of editing central planners or hard-coding PIHC rules. |
| PIHC custom systems | Inventory items, superevents, and state lores compile through PIHC3 project extensions with tests, parity reports, and no shared-package PIHC shortcuts. |
| User manual and onboarding interface | `docs/user-manual/` is maintained as a step-by-step HoI4 modder manual with a stable table of contents, CLI and Python examples, troubleshooting, and a PIHC3 continuation path. Manual gaps become tracked work, not incidental cleanup. |
| Versioned editor payloads | Focus tree, localization scan, entity form, asset preview, map selection, and build diagnostics payloads include schema ids, versions, project ids, game ids, and typed diagnostics. |
| Desktop app foundation | React + TypeScript + Vite builds the packaged static UI; the Python loopback service owns process management, project opening, SDK/LSP bridges, and build lifecycle; the macOS system WebView hosts the app without GUI-side HOI4 business logic. |
| Agent-safe workflows | MCP and CLI workflows can inspect, generate previews, validate, and build through stable contracts, with destructive actions gated by dry-run, diff, or review policy. |

## Short-Term Goals

Short-term goals are intentionally brief. Detailed task plans should be created only when implementation begins.

| Goal | Accomplishment criteria |
| --- | --- |
| Freeze evidence | Legacy paths, HOI4 version, PIHC2 source roles, HOI4DEV behavior references, and PIHC_dev compiled baseline are documented in one source manifest. |
| Establish docs spine | Roadmap, final architecture, resource references, tech stack, GUI stack, and next-step plans exist and link from [docs/README.md](../README.md). |
| Select first Python package slice | First package milestone has an accepted implementation spec with public API, CLI command, tests, and verification commands. |
| Ship first SDK/CLI happy path | A tiny HoI4 project can be initialized, built, inspected, and packaged through SDK and CLI commands with verified output and docs. |
| Select first PIHC3 bootstrap slice | First PIHC3 milestone has a clean layout, `paradev.yaml`, output path, compatibility baseline policy, and parity criteria. |
| Start the user manual loop | The manual index, first getting-started page, and PIHC3 continuation page exist and are updated whenever public SDK/CLI behavior changes. |
| Define GUI/LSP boundary | The GUI/LSP spec names the Python SDK/API, loopback REST, JSON/OpenAPI, CodeMirror 6, build-time React, and system-WebView responsibilities before deeper TypeScript work starts. |
