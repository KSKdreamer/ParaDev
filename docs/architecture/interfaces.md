# ParaDev Product Architecture

Status: active

Date: 2026-06-06

## Goal

ParaDev is a desktop-first Paradox Interactive game mod development app backed by a common Python SDK. The desktop app should feel like a focused Codex or Cowork-style workspace for mod projects, while the backend remains reusable from CLI, MCP, REST, LSP, VS Code, tests, scripts, and future automation.

## Design Brief

- Product: ParaDev, an installable macOS-first desktop app for structured Paradox mod development, prioritizing Hearts of Iron IV; Windows native packaging is deferred.
- Visual source: low-contrast round-rectangle material UI, using the repo UI style tokens plus cues from Ollama, Codex, GitHub Desktop, and Claude Cowork.
- Interactivity level: native desktop workbench with real project browsing, source editing, build lifecycle, configuration, tabs, split panes, and SDK-backed feature surfaces. Incomplete domain features remain explicit instead of being simulated in React.
- Non-goal: GUI-owned HoI4 business logic, a second compiler in the frontend or host, or build continuation across a full native-app process restart.

## Architecture Rule

All surfaces depend on the SDK API. No surface owns domain logic.

```text
Python backend
  -> SDK API
      -> MCP toolkit adapter
      -> Typer + Rich CLI
      -> VS Code extension and PDX LSP contracts
      -> REST API
          -> OpenAPI contract
          -> packaged React/Vite assets
          -> Python-wheel loopback host
          -> macOS system WebView
          -> Chromium app/browser fallback
```

React and Vite are build-time tools. The installed application requires only
the Python wheel and platform WebView; Windows native packaging is deferred.

## Installed GUI Host

`paradev dashboard` is the canonical installed application boundary. It composes the
existing `paradev.api.build_app()` REST surface with the existing React/Vite
build from `paradev.resources/gui`; it does not introduce another frontend or
another compiler. The server binds only to loopback, chooses a free port by
default, rejects untrusted Host headers and cross-origin mutations, and serves
a no-store runtime bootstrap so the frontend discovers the same-origin API
without build-time URLs. On macOS the default host is a thin native WKWebView,
with the default browser as its fallback. `--app` explicitly requests a
Chromium app window, while `--browser` and `--no-open` make the remaining host
behavior explicit. `--install-app` creates a Finder- and Dock-launchable
`~/Applications/ParaDev.app` whose process owns the same loopback server and
stops it when the application closes. The `paradev-gui` executable calls the
same parser and lifecycle owner as a compatibility entry point.

`scripts/smoke-macos-installed-app.bash` is the release boundary for that app:
it installs the built wheel into an isolated runtime and HOME, verifies the
bundle metadata and ad-hoc signature, launches through LaunchServices, probes
health, runtime bootstrap, and one hashed frontend asset, then quits and proves
the child listener exited. Startup failures retain only the last 8 KiB of child
stderr for the native alert and terminate the stay-open OSA app after the alert
is dismissed.

The frontend uses only the validated same-origin runtime bridge. On macOS, the
Python desktop shell owns native project-folder and verified project-package
selection through `POST /desktop/select-project` and
`POST /desktop/import-project-package`. The latter calls the Python
`desktop_install_project_package(...)` contract, including its user-owned
default destination, catalog validation, private staging, and atomic
publication. Project loading and validation remain SDK-owned.

## Editor And LSP Architecture

The adopted editor architecture is backend-first and editor-agnostic. The Python SDK owns PDX parsing, diagnostics, formatting, document symbols, hover, semantic tokens, HeavenBase catalog-backed symbols, and HOI4 keyword completion. `paradev lsp serve` exposes those capabilities over stdio JSON-RPC for IDEs such as VS Code, while REST exposes the same SDK functions for the desktop app and non-LSP product actions.

CodeMirror 6 is the long-term default and main GUI code editor for ParaDev. This is not a temporary prototype choice: the desktop app should invest in CodeMirror's extension model, keep editor behavior explicit in `apps/desktop/src/moduleEditor/codeMirrorSetup.ts`, and treat Monaco as optional rather than default. The current CodeMirror baseline uses CM6 direct packages for command/history/search/lint/view behavior plus `@uiw/react-codemirror` as the thin React wrapper. The default extension bundle should include line numbers, fold gutter, history, search, keymaps, close brackets, bracket matching, syntax highlighting, indentation, active line/gutter, custom selection drawing, multiple and rectangular selections, drop cursor, special-character highlighting, selection-match highlighting, and lint affordances before ParaDev-specific LSP extensions are layered on top. Official extension references live at [CodeMirror core extensions](https://codemirror.net/docs/extensions/) and [CodeMirror system guide](https://codemirror.net/docs/guide/).

The ParaDev GUI CodeMirror adapter debounces completion and semantic-token requests, cancels stale work, avoids backend calls for short implicit prefixes and large implicit-completion buffers, sends cursor `offset` with completion requests, checks semantic-token size limits before copying full document text, and routes editor requests through the same-origin Python API instead of spawning Python for every query. `paradev lsp serve` should not synchronously parse large documents on every `textDocument/didChange`; the default `--change-diagnostics-max-bytes` gate keeps large-buffer diagnostics to open/save or explicit requests until the backend has an async incremental diagnostic scheduler. Monaco remains the target client only when ParaDev needs a fuller VS Code-style surface outside the main GUI: Monaco rendering, tabs, context menus, keybindings, and `monaco-languageclient` should connect to the same PDX language service through a WebSocket or bridge adapter rather than reimplementing language semantics in TypeScript.

The backend target stays compatible with the suggested Python LSP shape:

```text
Python backend
  -> PDX lexer / parser / AST / symbol index
  -> HeavenBase catalog and HOI4 keyword dataset
  -> diagnostics / completion / hover / definition / rename
  -> code actions / refactors / generation commands
  -> pygls-compatible LSP transport
  -> optional FastAPI side channel for non-LSP product actions
```

Definition, rename, code actions, refactors, and generation commands should be added as SDK-owned LSP methods or command handlers as the underlying project/index APIs mature. The desktop and VS Code clients should remain thin adapters over those contracts.

## Repository Shape

```text
src/paradev/
  sdk/          common public Python API and architecture contracts
  pdx/          future parser, AST, formatter, diagnostics
  project/      project discovery, manifest, workspace boundary
  build/        build graph, artifact manifest, validation stages
  games/hoi4/   HOI4 package, entity families, game profiles
  hb/           HeavenBase workspace integration and MCP bridge
  surfaces/     CLI, MCP, REST, OpenAPI, LSP, VS Code, bundle adapters
  api/          application/project orchestration and lazy REST compatibility
  lsp/          language-server entry points and payload schemas
  desktop/      Python desktop API and native bridge helpers
  gui*.py       thin installed-GUI launcher, asset resolver, and macOS installer
  resources/gui/ packaged output of the one React/Vite application
apps/desktop/
  src/          build-time React/Vite application
  host/         thin system-WebView host scripts
```

The SDK layer starts small: immutable architecture specs, a project view model, and stable JSON projections for downstream surfaces. As parser/build/game systems land, they should extend these contracts rather than bypass them.

## Surface Boundaries

| Surface | Path | Runtime | Boundary |
| --- | --- | --- | --- |
| Package API | `src/paradev/__init__.py`, `src/paradev/package_api.py` | Python | Root import facade; `get_package_api_table()` audits package-level exports such as `Project`, `CM_PARADEV`, `__version__`, and the package table helpers by module, feature, and symbol kind. |
| Config API | `src/paradev/config.py`, `src/paradev/config_api.py` | Python | Public config module facade; `get_config_api_table()` audits config defaults, the shared `CM_PARADEV` manager, and config-reference helpers by module, feature, and symbol kind. |
| GUI API | `src/paradev/gui.py`, `src/paradev/gui_assets.py`, `src/paradev/gui_macos.py`, `src/paradev/gui_api.py` | Python argparse + Uvicorn + macOS WKWebView | Installed loopback GUI host, thin desktop launcher, and application installer; `get_gui_api_table()` audits the public `paradev-gui` parser helper, process entry point, and GUI-reference helpers by module, feature, and symbol kind. |
| Desktop API | `src/paradev/desktop/` | Python | Desktop shell package facade; `get_desktop_api_table()` audits the SDK-owned desktop state schema, `desktop_state(...)`, local source/cache/config helpers, desktop build command planning and lifecycle helpers, HOI4 launch planning, path opener planning, path status inspection, and desktop-reference helpers by module, feature, and symbol kind. |
| Games API | `src/paradev/games/`, `src/paradev/games/api.py` | Python | Game profile package facade; `get_games_api_table()` audits the game profile registry, profile registry resolver, and games-reference helpers by module, feature, and symbol kind. |
| Project Package API | `src/paradev/project/`, `src/paradev/project/api.py` | Python | Project package import facade; `get_project_facade_api_table()` audits `Project`, `ProjectManifestError`, and project facade-reference helpers by module, feature, and symbol kind while the canonical object behavior remains in the Project API table. |
| Localization API | `src/paradev/localization/`, `src/paradev/localization/api.py` | Python | Public language helper import facade; `get_localization_api_table()` audits HOI4 language alias normalization helpers and localization facade-reference helpers by module, feature, and symbol kind. |
| SDK API | `src/paradev/sdk/` | Python | Canonical import surface and JSON view contracts; `get_sdk_api_table()` audits the public `paradev.sdk` facade by module, feature, and symbol kind. |
| Authoring Templates API | `src/paradev/sdk/templates.py` | Python | SDK authoring-template module; `get_templates_api_table()` audits template payload schemas, dataclasses, registry helpers, and scaffold planning by feature and symbol kind. |
| Copy Roots API | `src/paradev/sdk/copy_roots.py` | Python | SDK compatibility-overlay copy-root module; `get_copy_roots_api_table()` audits target roots, manifest model, parser, copied artifact generation, and merge/shadow diagnostics by feature and symbol kind. |
| PDX Core API | `src/paradev/pdx/`, `src/paradev/pdx/api.py` | Python | Low-level PDX parser import facade; `get_pdx_core_api_table()` audits tokenizer, token, AST, parser, diagnostics, scalar constants, and PDX facade-reference helper exports by module, feature, and symbol kind. |
| HeavenBase API | `src/paradev/hb/`, `src/paradev/hb/api.py` | Python | Public HeavenBase import facade; `get_hb_api_table()` audits catalog schemas, catalog helper exports, and HB facade-reference helpers by module, feature, and symbol kind. |
| API Catalog | `src/paradev/surfaces/api_catalog.py` | Python | Overall generated reference inventory; `get_api_catalog_table()` lists every maintained API/reference contract with schema, row count, owner-module indexes, surface indexes, regeneration command, doc page, and SDK/CLI/REST/MCP lookup helpers. |
| Surfaces API | `src/paradev/surfaces/__init__.py`, `src/paradev/surfaces/api.py` | Python | Surface adapter import facade; `get_surfaces_api_table()` audits CLI, REST, MCP, LSP, VS Code, bundle, API catalog, and surface contract exports by module, feature, and symbol kind. |
| CLI | `src/paradev/cli.py`, `src/paradev/surfaces/cli.py` | Python, Typer, Rich | Human and script entry point over SDK calls; `get_cli_contract()` lists command-to-SDK adapters plus SDK-owned filter metadata, and `get_cli_api_table()` turns that static contract into the generated command reference. |
| MCP | `src/paradev/surfaces/mcp.py` | HeavenBase MCP | Tool schema and toolkit registration over SDK calls; `paradev mcp serve` runs the clean, implemented stdio authoring subset with read-only template/path/plan discovery and guarded batch creation, while the surface-wide `status: scaffold` remains honest about the broader target catalog returned by `get_mcp_contract()`. |
| REST | `src/paradev/surfaces/rest.py` | FastAPI | Local HTTP contract for desktop and external clients; `get_openapi_seed()` exposes API catalog lookup, architecture, frontend API discovery/action detail/option resolution/normalization/rest-request planning/binding lookup, PDX parse/format plus the PDX API selector, LSP diagnostics/symbols/hover/formatting/completion/semantic tokens plus the LSP API selector, project create/open/view/list/state/browser/find/rename, desktop state/project-selection/path-status/build lifecycle routes, module and collection mutations, project authoring, project build plan/emit, catalog status/write/refresh, and project inspection paths plus inspection filters. |
| Project Application API | `src/paradev/api/projects.py`, `src/paradev/api/__init__.py` | Python | Transport-neutral project orchestration shared by desktop and REST adapters. The package facade eagerly exposes project source, draft, module-create, guided-form, and localization services while resolving `build_app` and `get_openapi_seed` lazily for compatibility. `get_rest_facade_api_table()` preserves the established public facade/reference contract. |
| OpenAPI | `src/paradev/surfaces/rest.py`, lazy exports in `src/paradev/api/` | JSON | Exported REST contract consumed by frontend codegen later; generated clients should call SDK-owned inspection payloads rather than invent GUI-side models, and each REST operation advertises linked frontend operation ids through `x-paradev-frontend-api-operation-ids`. |
| TypeScript Contract | `apps/desktop/src/generated/frontendApi.ts`, `apps/desktop/src/data/frontendApi.ts` | Generated TS + typed helper | Checked-in frontend API contract generated by `render_frontend_api_typescript()` / CLI `frontend-api --typescript`, plus the desktop helper that exposes operation/action id types, summaries, workspace section/action rows, binding helpers, input/default/option-source helpers, option request planning/execution, REST execution request/result helpers, endpoint/request/payload helpers, and lookup helpers so GUI code does not maintain its own action list, navigation registry, form-default registry, option-request planner/executor, frontend API query-string builder, JSON request builder, or REST execution mapper. |
| Bundle | `scripts/build-wheel.bash`, `src/paradev/resources/gui/` | Python wheel | Reproducible application wheel containing the exact built frontend and thin host assets. |
| LSP | `src/paradev/surfaces/lsp.py`, `src/paradev/lsp/` | Python stdio JSON-RPC | PDX diagnostics, symbols, hover, formatting, catalog-backed completion, and semantic-token highlighting via `paradev lsp serve`. |
| LSP Server API | `src/paradev/lsp/`, `src/paradev/lsp/api.py` | Python | Public LSP server import facade; `get_lsp_server_api_table()` audits the document cache, JSON-RPC dispatcher, stdio framing helpers, stdio server entry point, and facade-reference helpers by module, feature, and symbol kind. |
| VS Code | `src/paradev/surfaces/vscode.py`, `packages/vscode-paradev/` | TypeScript VS Code extension | Thin client that launches `paradev lsp serve` for `paradox-pdx` documents and can reuse CLI and REST contracts. |
| Desktop | `apps/desktop/`, `src/paradev/resources/gui/` | Build-time React/Vite, Python loopback host, macOS WKWebView | One packaged GUI served by the installed Python host; Chromium and browser modes are explicit fallbacks. |

Project authoring calls follow `desktop/backend -> api/projects -> sdk/project`.
The FastAPI module is a peer adapter over the same `api/projects` operations;
desktop code must not import `paradev.surfaces.rest`.

Overall API reference audits should call `paradev.surfaces.get_api_catalog_table()` before drilling into a specific SDK, CLI, REST, MCP, frontend, or surface contract table. Use `API_CATALOG_SCHEMA` as the fixed top-level schema anchor; rows list each maintained reference id, table/contract schema, row count, index names, owning module, table helper, selector helper when one shared selector path exists, CLI regeneration command, and manual page, while `owner_module_index`, `surface_index`, and `selector_helper_index` group the catalog by Python owner, delivery surface, and shared selector API. Use `get_api_catalog_selection(reference_id=..., index_name=..., key=...)` when a surface needs one shared selector path; CLI `paradev api-catalog`, `paradev api-catalog --reference`, and `paradev api-catalog --index --key` expose that selector as table and projection commands. REST exposes the same lookups as `GET /api-catalog?reference_id=...` and `GET /api-catalog?index_name=...&key=...`; MCP exposes the same selector shape through the read-only `api_catalog` tool. Regenerate `docs/user-manual/api-catalog-reference.md` through `paradev.surfaces.render_api_catalog_reference_markdown()` or CLI `paradev api-catalog --markdown` whenever an API reference table or generated contract is added, removed, or renamed.

Root package facade audits should call `paradev.get_package_api_table()` instead of hand-maintaining imports from `paradev.__all__`. Use `PACKAGE_API_TABLE_SCHEMA` as the fixed table schema anchor; rows are derived from the current root package exports so package-level `Project`, `CM_PARADEV`, `__version__`, architecture helpers, project helpers, and package API table helpers stay grouped by source module, feature, symbol kind, and primary doc page. Regenerate `docs/user-manual/package-api-reference.md` through `paradev.render_package_api_reference_markdown()` or CLI `paradev package-api --markdown` whenever the root package facade changes.

Config facade audits should call `paradev.config.get_config_api_table()` instead of hand-maintaining imports from `paradev.config.__all__`. Use `CONFIG_API_TABLE_SCHEMA` as the fixed table schema anchor; rows are derived from the current config module exports so `DEFAULT_CONFIG`, `BOOTSTRAP_CONFIG`, `CM_PARADEV`, and config API table helpers stay grouped by source module, feature, symbol kind, registry seam, and primary doc page. Regenerate `docs/user-manual/config-api-reference.md` through `paradev.config.render_config_api_reference_markdown()` or CLI `paradev config-api --markdown` whenever the public config facade changes.

GUI launcher facade audits should call `paradev.gui.get_gui_api_table()` instead of hand-maintaining imports from `paradev.gui.__all__` or duplicating the installed `paradev-gui` entry point. Use `GUI_API_TABLE_SCHEMA` as the fixed table schema anchor; rows are derived from the public launcher facade so `build_parser(...)`, `main(...)`, and GUI API table helpers stay grouped by module, feature, symbol kind, registry seam, and primary doc page. Regenerate `docs/user-manual/gui-api-reference.md` through `paradev.gui.render_gui_api_reference_markdown()` or CLI `paradev gui-api --markdown` whenever the public GUI launcher facade changes.

Desktop facade audits should call `paradev.desktop.get_desktop_api_table()` instead of hand-maintaining imports from `paradev.desktop.__all__` or duplicating desktop state helper lists in GUI clients. Use `DESKTOP_API_TABLE_SCHEMA` as the fixed table schema anchor; rows are derived from the public desktop facade so `DESKTOP_STATE_SCHEMA`, `desktop_state(...)`, local desktop source/cache/config helpers, `desktop_project_build_command(...)`, `desktop_start_build(...)`, `desktop_build_status(...)`, `desktop_interrupt_build(...)`, `desktop_run_hoi4(...)`, `desktop_open_path(...)`, `desktop_path_status(...)`, and desktop API table helpers stay grouped by source module, feature, symbol kind, registry seam, and primary doc page. Regenerate `docs/user-manual/desktop-api-reference.md` through `paradev.desktop.render_desktop_api_reference_markdown()` or CLI `paradev desktop-api --markdown` whenever the public desktop facade changes.

Desktop AI chat must route through the Python desktop facade before any GUI conversation UI calls an LLM. `desktop_chat(...)` owns the non-streaming HeavenBase request contract, `POST /desktop/ai/chat` exposes the same `paradev.desktop.ai-chat.v1` payload to the same-origin GUI, and `chatWithParaDevAi(...)` is the TypeScript client wrapper. The compatibility-stable `create-module` profile presents itself as **Create content plan** and may add one discriminated `paradev.desktop.ai-chat-proposal.v1` projection, but only after Python validates the structured model response against the active project's authoring-ready Registry templates. Module proposals call `Project.create_modules(..., write=False)`; collection proposals such as focus trees and decision categories call `Project.scaffold_collection(..., write=False)`. Each proposal carries its normalized request and exact dry plan into the existing retained batch or collection editor. Chat never owns a write verb: only those editors may apply the exact plan hash, edits invalidate the preview, and project/template/source/session changes reject review without replacing user drafts.

The dynamic template catalog in that prompt preserves each field's type,
required state, non-empty default, advanced status, label, description, and
choices. It also publishes `description_source` as `declared` or `generated`.
Relational fields may publish one transport-neutral `reference` with a
Registry family and `module` or `collection` kind. Desktop forms resolve that
hint from the already-loaded project browser as free-form autocomplete, while
AI prompt construction preserves the same hint; neither surface maintains a
family-specific relationship list.
An extension may explicitly set a field's `advanced` boolean to own progressive
disclosure; when omitted, ParaDev retains the compatibility rule that fields
with non-empty defaults are advanced. Invalid non-boolean declarations fail
while loading the template instead of being silently ignored.
Required state, closed choices, finite-number types, and boolean types are
enforced again by the shared scaffold planner. They are not GUI-only hints, so
SDK, CLI, REST, MCP, desktop, and agent-created batches fail with the same
field-specific diagnostic before any file write.
Declared Registry semantics are agent instructions, not merely GUI decoration:
for example, PIHC3's Idea template tells the model that a 2% CIC modifier is
authored as `0.02`. When an extension omits help text, the SDK derives a concise
fallback from the argument's actual folder and generated-file references; it
does not guess family behavior. Desktop prompt construction must not maintain a
family-specific unit or field-description table. It consumes the same
`form.fields` projection as the create dialog, including SDK-generated readable
labels and help. The argument map and form-field names must match exactly; an
incomplete or divergent projection fails closed instead of sending ambiguous
instructions to the model. The desktop typed model retains description
provenance on the rendered help element instead of dropping additive Registry
metadata at the Python/TypeScript boundary.

Desktop GUI controls for real project/runtime settings should use explicit desktop config helpers instead of folding those values into the GUI settings blob. `desktop_config_rows()` exposes the SDK-owned row metadata used to render config controls, while `desktop_read_config_value(...)` and `desktop_write_config_value(...)` expose an allowlisted bridge to `CM_PARADEV` keys such as `paradev.build.parallelism`, `paradev.cli.output`, and `paradev.desktop.thumbnail_cache.max_kb`, so the installed GUI, build-time preview, CLI tests, and Python scripts all read and write the same SDK-owned config value.

## GUI To Python Parity Matrix

Current GUI operations must be expressible through Python SDK/facade APIs plus standard HeavenBase process and file helpers. The macOS host owns only window and child-server lifecycle; domain and local-filesystem effects remain reproducible from Python and are exposed through the loopback API.

| GUI bridge operation | Python equivalent | Equivalent effect |
| --- | --- | --- |
| `loadDesktopState` | `paradev.desktop.desktop_state(...)`, CLI `paradev desktop-state` | Lists registered projects, selects the active project, and optionally includes the SDK browser payload. |
| `loadProjectBrowser` | `Project.load(path).browser(...)`, CLI `paradev project-browser` | Reads the same SDK-owned project tree, complete family/item inventory, family `visible` metadata, diagnostics, templates, and scoped browser filters. Normal navigation projects only visible families; hidden families remain present for build support and advanced/scoped tools. |
| `readProjectBrowserCache` / `writeProjectBrowserCache` | `read_project_browser_cache(...)` / `desktop_write_browser_cache(...)` | Uses the same `.paradev/.cache/desktop/project-browser/browser.json` path, schema check, root validation, size limit, stale-cache removal, and unfiltered `filters: {}` base-payload requirement. Desktop validation rejects legacy family rows without explicit browser visibility so an older cache cannot reintroduce hidden families. Scoped family payloads may overlay that base in memory but may never become the project-wide cache by themselves. |
| `readTextSource` / `readBinarySource` | `desktop_read_text_source(...)` / `desktop_read_binary_source(...)`; binary ownership is `Project.read_source_binary(...)` | Validates project-contained paths and preserves the desktop text and binary MIME payload shapes. Binary reads use the SDK's descriptor-stable snapshot and size limit rather than a second desktop filesystem implementation. |
| `readThumbnailCache` / `writeThumbnailCache` | `desktop_read_thumbnail_cache(...)` / `desktop_write_thumbnail_cache(...)` | Uses the same FNV-1a cache key path under `.paradev/.cache/instance-thumbnails`, PNG MIME override, and the SDK-owned `paradev.desktop.thumbnail_cache.max_kb` byte limit. Reads return `null` when no entry exists and recover a structurally invalid historical PNG as a deleted stale-cache miss; invalid roots/keys and non-file or oversized entries remain errors. Writes validate PNG structure before atomically replacing a cache entry, while transform-less non-PNG previews remain visible without being cached. |
| `readAppConfig` / `writeAppConfig` | `desktop_read_app_config()` / `desktop_write_app_config(...)` | Persists GUI settings through the `CM_PARADEV` key `paradev.desktop.gui`, reached through the same-origin API. |
| Desktop config metadata | `desktop_config_rows()` | Returns the SDK-owned row list that GUI controls use for config keys, defaults, types, choices, and numeric minimums. |
| `readConfigValue` / `writeConfigValue` | `desktop_read_config_value(...)` / `desktop_write_config_value(...)` | Reads and writes allowlisted real `CM_PARADEV` keys such as `paradev.build.parallelism`, `paradev.cli.output`, and `paradev.desktop.thumbnail_cache.max_kb`, so Config-page command/build/cache defaults affect Python SDK, CLI, and GUI behavior through one config source. |
| `chatWithParaDevAi` | `desktop_chat(...)`, REST `POST /desktop/ai/chat` | Sends one non-streaming AI prompt through HeavenBase with the same preset, provider, model, gateway, role, project root, prompt, optional source descriptors, reply, key-source, and route-detail payload fields used by the desktop bridge. Source paths are resolved and read by the Python desktop facade, not by the GUI. |
| `loadDesktopPathStatus` | `desktop_path_status(...)`, REST `GET /desktop/path-status` | Returns the SDK-owned existence, kind, readable, and openable status for one local path before Config-page rows present status chips or enable a path open action. |
| `selectProjectPath` / `importProjectPackage` | `desktop_select_project_path(...)` / `desktop_select_project_package_path(...)`, `desktop_install_project_package(...)`; REST `POST /desktop/select-project` / `POST /desktop/import-project-package` | Opens the native macOS folder or ZIP picker. Package cancellation returns `null`; a selected cataloged archive is verified and published transactionally under the current user's `Documents/ParaDev/Projects` directory. The installed system-WebView host reuses the Python installer contract. |
| `loadProjectCatalogStatus` | `Project.catalog_status()`, REST `GET /projects/catalog` | Classifies the selected project's local Catalog database as present, missing, incomplete, or unreadable without opening SQLite, building the project, or creating project state. `incomplete` also covers a fail-closed stale marker written before a module source mutation; the existing Refresh action rebuilds and clears it. |
| `createModuleDraft` | `Project.scaffold_module(...)`, `Project.create_module(...)`, REST facade `create_module_draft(...)`, CLI `paradev scaffold` | Creates or previews module files from the same SDK templates, values, write flag, and force flag used by the GUI. |
| `applyProjectDraft` | `Project.apply_source_draft(...)`, REST facade `apply_project_draft(...)`; for text-only module files, `Project.write_module_files(...)` | Applies project-contained text edits, removals, base64 byte replacements, and an optional final module-folder rename through one SDK-owned preflight and rollback boundary. |
| `createModuleBatchRequest` | `Project.module_batch_edit_request(...)`; apply with `Project.write_module_files(...)`, CLI `module-batch-request` / `module-batch-edit` | Produces the same canonical batch edit request and writes the same validated module file changes. |
| `renameModule` | `Project.rename_module(...)`, CLI `paradev module-rename` | Moves the module folder within the same family and returns the same rename payload shape. |
| `removeModule` | `Project.remove_module(..., write=True)`, CLI `paradev module-remove`, existing REST `DELETE /projects/modules/remove` | Removes the complete canonical module folder through the SDK; desktop adapters must never translate the action into an enumerated list of individual source-file removals. |
| `startProjectBuild` | `desktop_start_build(...)`, REST `POST /desktop/builds`, frontend operation `build.start`; exact compiler behavior remains `Project.build(emit_artifacts=True, emit_manifests=True, full_rebuild=...)` | Starts the same SDK-owned build through the desktop facade and returns `paradev.desktop.build-run.v1`. GUI callers reach it through the frontend API REST planner; Python owns the child-process lifecycle. |
| `getProjectBuildRuns` | `desktop_build_runs(...)`, REST `GET /desktop/builds`, frontend operation `build.runs` | Lists every active run and the newest 256 terminal runs known to the current native app process, optionally filtered by filesystem-equivalent project root, as `paradev.desktop.build-runs.v1`. The app shell uses this operation to recover full and partial runs after a rail remount or renderer reload. |
| `getProjectBuildStatus` / `interruptProjectBuild` | `desktop_build_status(...)` / `desktop_interrupt_build(...)`, REST `GET /desktop/builds/status` / `POST /desktop/builds/interrupt`, frontend operations `build.status` / `build.interrupt` | Polls or interrupts the desktop build run identified by `run_id`; the compiler and emitted files remain SDK-owned. |
| `runHoi4Game` | `desktop_run_hoi4(...)` or `desktop_hoi4_launch_command(...)` | Uses the same Steam app id, launch modes, local root validation, platform opener command, and `paradev.desktop.game-launch.v1` payload. |
| `requestPdxLspCompletion` / `requestPdxLspSemanticTokens` | SDK `complete_pdx_lsp_text(...)` / `semantic_tokens_pdx_lsp_text(...)`, CLI `paradev lsp ...`, REST `/lsp/...`, LSP `textDocument/*` | Provides the same editor completion and semantic-token payloads through the Python language service. |
| `openProjectPath` | `desktop_open_path(...)` or `desktop_open_path_command(...)` | Validates the path and uses the Python-owned Finder/Explorer/editor/terminal command mapping; callers should use `desktop_path_status(...)` for non-mutating status display before opening. |
| Project activation and split-tab selection | Frontend-local workspace state | Does not mutate project files and intentionally has no SDK side effect. |

`Project.read_source_text(...)` returns UTF-8 text plus paired `size` and string-valued `mtime_ns` from one descriptor-stable snapshot. `Project.apply_source_draft(...)` preflights every text edit before the first filesystem mutation. Text must fit the same UTF-8 byte limit used when reopening it in the editor; `.json` rejects malformed syntax and non-standard numeric constants; `.yaml` and `.yml` must parse through the safe YAML loader. A registered project family may additionally expose `validate_source_text(*, module_id: str, relative_path: str, text: str) -> None` for domain-owned source contracts. The hook must be deterministic and side-effect free and raises `ValueError` to reject the complete draft request. Text edits, guarded removal objects, and existing binary replacements may carry paired `expected_size` and `expected_mtime_ns` fields from that snapshot or a browser-row revision. The pair must appear together. A new binary target may carry `expected_absent=true`, which cannot be combined with a revision, so a file created by another process after the draft opened cannot be overwritten. The outer REST request and every nested object variant are closed contracts; binary conversion also requires `content_format` and `target_format` together. Unknown fields are rejected instead of silently disabling a guard. The SDK rejects the whole request before writing when a guarded source changed, then checks the expected state again while installing or removing it. Guarded installs use same-directory quarantine plus no-replace linking so a file that appears during the final install window is preserved.

`Project.read_source_binary(...)` applies that descriptor-stable snapshot contract to arbitrary project-contained bytes, with a 20 MiB bound, SHA-256 digest, paired revision, and optional base64 content. `Project.read_module_asset(...)` narrows the same operation to sources selected by the active Registry: a source must match a family-declared copy slot or a registered image source. Its payload exposes the matched source-slot ownership and a `draft_guard` that can be passed unchanged to `Project.apply_source_draft(...)`. The bounded authoring MCP exposes this as `module_asset` and omits base64 by default so agents can inspect identity, ownership, digest, and revision without filling context with image data. The desktop binary adapter delegates to `Project.read_source_binary(...)` and only translates the returned bytes into its established desktop wire shape.

Before mutation the SDK captures every target in a private recovery transaction, bounded to 256 targets and 256 MiB of streamed backups. A later write/remove failure rolls earlier targets back only while they still match ParaDev's exact committed inode, size, modification time, and content digest. A newer external edit is never overwritten; an incomplete rollback retains the recovery directory and reports its path. `module_rename` may join that request: the SDK preflights the canonical module identity first, commits the descriptor-anchored folder move only after every file mutation succeeds, and rolls the file mutations back if that final move fails. The response includes the standard rename payload under `module_rename`, so the desktop commits one final entity/path state instead of coordinating two source calls. A request touching canonical modules marks a configured Catalog stale before the first source mutation and returns one aggregate `catalog_mutation` status. Frontends display the refresh-required result while retaining the source-backed view.

A module edit can change module, HOI4-entity, localization, PDX-symbol, source, graph, and artifact projections together. Written module create, rename, remove, and contained source-draft operations therefore do not claim success from a module-only Catalog row delta. Under the shared writer lock, the SDK first writes a durable hidden stale marker; `catalog_status` then returns the existing `incomplete` / `catalog.incomplete` pair, and Catalog query/completion reads fail with an actionable Refresh message until `catalog_refresh(...)` atomically rebuilds the complete Catalog and clears the marker. Create returns `catalog_mutation` inside the scaffold plan, while rename and remove return it at the top level. The existing closed `paradev.hb.catalog-mutation.v1` wire schema remains compatible: no Catalog returns `not_configured` / `catalog.mutation.not_configured`; a configured Catalog returns `failed` / `catalog.mutation.failed` with the refresh instruction; `applied` / `catalog.mutation.applied` remains reserved for a future coherent multi-entity delta. Dry runs, blocked plans, and non-written removals omit the field. The filesystem operation is authoritative once it succeeds, so the refresh-required result must not turn into an automatic source retry. Create writes and folder renames use lexical, descriptor-anchored, no-follow paths. Scaffold contents stage below `source_root/.paradev/module-transactions` before canonical files change; forced replacements retain originals until every install and identity check succeeds, ordinary failures roll back, and an incomplete rollback preserves the transaction with a structured recovery-path diagnostic. A Registry provider that creates a standalone diagram child while editing an existing parent additionally writes `.paradev/diagram-module-transaction/recovery.json` before scaffolding. Recovery orders the ordinary source journal first, classifies all parent sources against exact before/after hashes, and then descriptor-anchors the exact child inventory: before removes only owned exact/partial child content, after requires and retains the complete child, and every mixed or unowned state is preserved fail-closed. The fixed record clears only after scaffold transaction cleanup and child reconciliation. Removal first atomically renames the canonical folder into same-source-root quarantine, retains the stale Catalog marker, then deletes quarantine best-effort; cleanup failure keeps `removed=true` and returns `paradev.module.remove-cleanup.v1` with a warning/tombstone path.

Games facade audits should call `paradev.games.get_games_api_table()` instead of hand-maintaining imports from `paradev.games.__all__` or duplicating profile registry helper lists. Use `GAMES_API_TABLE_SCHEMA` as the fixed table schema anchor; rows are derived from the public games facade so `PROFILE_REGISTRIES`, `registry_for_profile(...)`, and games API table helpers stay grouped by source module, feature, symbol kind, registry seam, and primary doc page. Regenerate `docs/user-manual/games-api-reference.md` through `paradev.games.render_games_api_reference_markdown()` or CLI `paradev games-api --markdown` whenever the public games facade changes.

Project package facade audits should call `paradev.project.get_project_facade_api_table()` instead of hand-maintaining imports from `paradev.project.__all__`. Use `PROJECT_FACADE_API_TABLE_SCHEMA` as the fixed table schema anchor; rows are derived from the current project package exports so compatibility imports such as `Project`, `ProjectManifestError`, and project facade-reference helpers stay grouped by source module, feature, symbol kind, registry seam, and primary doc page. Regenerate `docs/user-manual/project-facade-api-reference.md` through `paradev.project.render_project_facade_api_reference_markdown()` or CLI `paradev project-facade-api --markdown` whenever the public project package facade changes.

Localization facade audits should call `paradev.localization.get_localization_api_table()` instead of hand-maintaining public language helper imports from `paradev.localization.__all__`. Use `LOCALIZATION_API_TABLE_SCHEMA` as the fixed table schema anchor; rows are derived from the current localization package exports so `HOI4_LANGUAGE_ALIASES`, `canonical_language(...)`, and localization facade-reference helpers stay grouped by source module, feature, symbol kind, registry seam, and primary doc page. Regenerate `docs/user-manual/localization-api-reference.md` through `paradev.localization.render_localization_api_reference_markdown()` or CLI `paradev localization-api --markdown` whenever the public localization package facade changes.

Surface facade audits should call `paradev.surfaces.get_surfaces_api_table()` instead of hand-maintaining imports from `paradev.surfaces.__all__`. Use `SURFACES_API_TABLE_SCHEMA` as the fixed table schema anchor; rows are derived from the current surface exports so API catalog, CLI, REST/OpenAPI, MCP, LSP, VS Code, bundle, and static surface-contract helpers stay grouped by source module, feature, symbol kind, registry seam, and primary doc page. Regenerate `docs/user-manual/surfaces-api-reference.md` through `paradev.surfaces.render_surfaces_api_reference_markdown()` or CLI `paradev surfaces-api --markdown` whenever the public surface facade changes.

SDK facade audits should call `paradev.sdk.get_sdk_api_table()` instead of hand-maintaining public import lists from `paradev.sdk.__all__`. Use `SDK_API_TABLE_SCHEMA` as the fixed table schema anchor; the rows are derived from the current facade exports so module grouping, feature grouping, symbol kind, return/value summaries, import paths, and primary doc pages stay aligned with the Python SDK import surface. Regenerate `docs/user-manual/sdk-api-reference.md` through `paradev.sdk.render_sdk_api_reference_markdown()` or CLI `paradev sdk-api --markdown` whenever the SDK facade exports change.

Project object audits should call `paradev.sdk.get_project_api_table()` instead of hand-maintaining `Project` field, classmethod, method, CLI command, frontend operation, or inspection-kind lists. Use `PROJECT_API_TABLE_SCHEMA` as the fixed table schema anchor; the rows are derived from the public `Project` dataclass surface and the static CLI/frontend/inspection contracts, so the object API, command adapters, GUI operation ids, and inspection dispatch stay aligned. Regenerate `docs/user-manual/project-api-reference.md` through `paradev.sdk.render_project_api_reference_markdown()` or CLI `paradev project-api --markdown` whenever the public `Project` object changes.

Authoring template audits should call `paradev.sdk.templates.get_templates_api_table()` instead of copying template schema constants, dataclasses, registry helpers, or scaffold-planning functions by hand. Use `TEMPLATES_API_TABLE_SCHEMA` as the fixed table schema anchor; rows are derived from the module-level `__all__` so template payload schemas, model dataclasses, built-in/project-local template registry helpers, `module_scaffold_plan(...)`, and the reference-table helpers stay grouped by feature, symbol kind, registry seam, and primary doc page. Project-local template rows expose `directory`, which defaults to `{object_id}` and may render a readable physical folder without changing logical identity. Regenerate `docs/user-manual/templates-api-reference.md` through `paradev.sdk.templates.render_templates_api_reference_markdown()` or CLI `paradev templates-api --markdown` whenever SDK authoring-template helpers change.

Copy-root audits should call `paradev.sdk.copy_roots.get_copy_roots_api_table()` instead of copying target-root constants, manifest parser signatures, artifact constructors, or shadow-diagnostic merge behavior by hand. Use `COPY_ROOTS_API_TABLE_SCHEMA` as the fixed table schema anchor; rows are derived from the module-level `__all__` so `ARTIFACT_TARGET_ROOTS`, `CopyRootSpec`, `project_copy_roots(...)`, `copy_root_artifacts(...)`, `merge_copy_root_artifacts(...)`, and the reference-table helpers stay grouped by feature, symbol kind, registry seam, and primary doc page. Regenerate `docs/user-manual/copy-roots-api-reference.md` through `paradev.sdk.copy_roots.render_copy_roots_api_reference_markdown()` or CLI `paradev copy-roots-api --markdown` whenever SDK copy-root helpers change.

Build facade audits should call `paradev.build.get_build_api_table()` instead of hand-maintaining build record, registry, family, slot, loader, artifact writer, manifest, view, graph, or planning import lists from `paradev.build.__all__`. Use `BUILD_API_TABLE_SCHEMA` as the fixed table schema anchor; rows are derived from the current build facade exports so compiler extension APIs stay grouped by module, feature, symbol kind, registry seam, and primary doc page. Regenerate `docs/user-manual/build-api-reference.md` through `paradev.build.render_build_api_reference_markdown()` or CLI `paradev build-api --markdown` whenever the public build facade changes.

Architecture graph API audits should call `paradev.sdk.get_architecture_api_table()` instead of hand-maintaining symbol lists for `ArchitectureSpec`, `SurfaceSpec`, CLI `architecture`, REST `GET /architecture`, or MCP architecture tools. Use `ARCHITECTURE_API_TABLE_ROWS` and `ARCHITECTURE_API_TABLE_SCHEMA` as fixed SDK anchors for table code, and use `get_architecture_api_selection(symbol=..., index_name=..., key=...)` when a surface needs the full table, one architecture API row, or one index projection. CLI exposes the same table selector through `paradev architecture --api-table --symbol ...` and `paradev architecture --api-table --index ... --key ...`; REST exposes it through `GET /architecture?api_table=true&symbol=...` or `GET /architecture?api_table=true&index_name=...&key=...`; MCP exposes it through the read-only `architecture_api` selector tool. Regenerate `docs/user-manual/architecture-api-reference.md` through `paradev.sdk.render_architecture_api_reference_markdown()` or CLI `paradev architecture --api-table-markdown` whenever the graph-facing SDK, CLI, REST, or MCP surface changes.

PDX parse/format API audits should call `paradev.sdk.get_pdx_api_table()` instead of hand-maintaining parser, formatter, or PDX table selector symbol lists. Use `PDX_API_TABLE_ROWS` and `PDX_API_TABLE_SCHEMA` as fixed SDK anchors for `parse_pdx_file(...)`, `format_pdx_text(...)`, `format_pdx_file(...)`, CLI `pdx-api`/`parse`/`format`, REST `GET /pdx/parse`/`POST /pdx/format`/`GET /pdx-api`, and MCP `pdx_parse`/`pdx_format`/`pdx_api`. `get_pdx_api_selection(symbol=..., index_name=..., key=...)` is the shared selector for the full table, one PDX API row, or one surface/feature index projection, and REST/MCP expose that same selector through `/pdx-api` and the read-only `pdx_api` tool. Regenerate `docs/user-manual/pdx-api-reference.md` through `paradev.sdk.render_pdx_api_reference_markdown()` or CLI `paradev pdx-api --markdown` whenever those parse/format or selector entry points change.

PDX core facade audits should call `paradev.pdx.get_pdx_core_api_table()` instead of hand-maintaining public import lists from `paradev.pdx.__all__`. Use `PDX_CORE_API_TABLE_SCHEMA` as the fixed table schema anchor; rows are derived from the current PDX parser facade so tokenizer, token, AST, parser, diagnostics, scalar constants, import paths, symbol kinds, and reference helper exports stay grouped by module, feature, registry seam, and primary doc page. Regenerate `docs/user-manual/pdx-core-api-reference.md` through `paradev.pdx.render_pdx_core_api_reference_markdown()` or CLI `paradev pdx-core-api --markdown` whenever the public PDX facade changes.

HeavenBase facade audits should call `paradev.hb.get_hb_api_table()` instead of hand-maintaining public import lists from `paradev.hb.__all__`. Use `HB_API_TABLE_SCHEMA` as the fixed table schema anchor; rows are derived from the current HeavenBase facade so catalog schema constants, catalog operation helpers, entity type exports, and API-reference helpers stay grouped by module, feature, registry seam, and primary doc page. Regenerate `docs/user-manual/hb-api-reference.md` through `paradev.hb.render_hb_api_reference_markdown()` or CLI `paradev hb-api --markdown` whenever the public HB facade changes.

LSP editor API audits should call `paradev.sdk.get_lsp_api_table()` instead of hand-maintaining diagnostics, symbols, hover, formatting, completion, and semantic-token symbol lists. Use `LSP_API_TABLE_ROWS` and `LSP_API_TABLE_SCHEMA` as fixed SDK anchors for the SDK helpers, CLI `lsp-api`/`lsp ...` commands, REST `GET /lsp-api` / `POST /lsp/...` routes, MCP `lsp_api`, and JSON-RPC `textDocument/*` methods. Use `paradev.sdk.get_lsp_api_selection(symbol=..., index_name=..., key=...)` as the shared selector path for the full table, one LSP API row, or one surface/feature reverse-index projection; regenerate `docs/user-manual/lsp-api-reference.md` through `paradev.sdk.render_lsp_api_reference_markdown()` or CLI `paradev lsp-api --markdown` whenever editor-facing capabilities change.

LSP server facade audits should call `paradev.lsp.get_lsp_server_api_table()` instead of hand-maintaining public import lists from `paradev.lsp.__all__`. Use `LSP_SERVER_API_TABLE_SCHEMA` as the fixed table schema anchor; rows are derived from the current server facade so `PdxDocument`, `PdxLanguageServer`, stdio framing helpers, `serve_pdx_lsp_stdio(...)`, and reference helper exports stay grouped by module, feature, symbol kind, registry seam, and primary doc page. Regenerate `docs/user-manual/lsp-server-api-reference.md` through `paradev.lsp.render_lsp_server_api_reference_markdown()` or CLI `paradev lsp-server-api --markdown` whenever the public LSP server package facade changes.

HeavenBase catalog API audits should call `paradev.hb.get_catalog_api_table()` instead of hand-maintaining catalog preview/status/write/refresh/query/completion symbol lists. Use `CATALOG_API_TABLE_ROWS` and `CATALOG_API_TABLE_SCHEMA` as fixed SDK anchors for `catalog_preview(...)`, `catalog_status(...)`, `catalog_write(...)`, `catalog_refresh(...)`, `catalog_query(...)`, `catalog_completion_items(...)`, CLI `catalog-api`/`hb catalog-*`, REST `GET /catalog-api` / `GET /projects/inspect?kind=catalog-*` and `GET`/`POST`/`PUT /projects/catalog`, and MCP `catalog_api` plus `project_inspect` catalog projections. Use `paradev.hb.get_catalog_api_selection(symbol=..., index_name=..., key=...)` as the shared selector path for the full table, one Catalog API row, or one surface/feature reverse-index projection; regenerate `docs/user-manual/catalog-api-reference.md` through `paradev.hb.render_catalog_api_reference_markdown()` or CLI `paradev catalog-api --markdown` whenever catalog entry points change.

REST/OpenAPI route audits should call `paradev.surfaces.rest.get_rest_api_table()` instead of hand-maintaining route lists or frontend-operation reverse maps. Use `REST_API_TABLE_SCHEMA` as the fixed table schema anchor; the rows are derived from `get_openapi_seed()` so route summaries, method/path pairs, parameters, request bodies, responses, and `x-paradev-frontend-api-operation-ids` stay aligned with the OpenAPI contract. Use `paradev.surfaces.rest.get_rest_api_selection(symbol=..., index_name=..., key=...)`, CLI `paradev rest-api`, or REST `GET /rest-api` when a surface needs the full route table, one route row, or one method/feature/frontend-operation reverse-index projection. Regenerate `docs/user-manual/rest-api-reference.md` through `paradev.surfaces.rest.render_rest_api_reference_markdown()` or CLI `paradev rest-api --markdown` whenever REST/OpenAPI routes change.

REST package facade audits should call `paradev.api.get_rest_facade_api_table()` instead of hand-maintaining public import lists from `paradev.api.__all__`. Use `REST_FACADE_API_TABLE_SCHEMA` as the fixed table schema anchor; rows are derived from the current facade so `build_app()`, `get_openapi_seed()`, project source/draft helpers, module draft helpers, and facade-reference helper exports stay grouped by module, feature, symbol kind, registry seam, and primary doc page. Regenerate `docs/user-manual/rest-facade-api-reference.md` through `paradev.api.render_rest_facade_api_reference_markdown()` or CLI `paradev rest-facade-api --markdown` whenever the public REST package facade changes.

MCP tool audits should call `paradev.surfaces.mcp.get_mcp_api_table()` instead of hand-maintaining tool lists or read/write mode indexes. Use `MCP_API_TABLE_SCHEMA` as the fixed table schema anchor; the rows are derived from `get_mcp_contract()` so tool names, SDK method targets, read/write mode, feature grouping, frontend operation bindings, and the API catalog, surface-contract, and MCP API selector tools stay aligned with the static MCP contract. Use `paradev.surfaces.mcp.get_mcp_api_selection(symbol=..., index_name=..., key=...)`, CLI `paradev mcp-api`, or MCP `mcp_api` when a surface needs the full tool table, one tool row, or one mode/feature/frontend-operation reverse-index projection. Regenerate `docs/user-manual/mcp-api-reference.md` through `paradev.surfaces.mcp.render_mcp_api_reference_markdown()` or CLI `paradev mcp-api --markdown` whenever MCP tools change.

CLI command audits should call `paradev.surfaces.cli.get_cli_api_table()` instead of hand-maintaining command lists, projection rows, or frontend-operation reverse maps. Use `CLI_API_TABLE_SCHEMA` as the fixed table schema anchor; the rows are derived from `get_cli_contract()` so command keys, command groups, SDK/helper adapters, filters, projections, and frontend operation bindings stay aligned with the Typer surface contract. Use `paradev.surfaces.cli.get_cli_api_selection(symbol=..., index_name=..., key=...)`, CLI `paradev cli-api`, REST `GET /cli-api`, or MCP `cli_api` when a surface needs the full command table, one command/projection row, or one kind/feature/adapter/frontend-operation reverse-index projection. Regenerate `docs/user-manual/cli-api-reference.md` through `paradev.surfaces.cli.render_cli_api_reference_markdown()` or CLI `paradev cli-api --markdown` whenever CLI commands or adapter mappings change.

Static adapter audits that need all surface contract payloads should call `paradev.surfaces.get_surface_contracts()` instead of importing each individual contract builder. Use `SURFACE_CONTRACT_IDS`, `SURFACE_CONTRACT_INDEX_CATALOG`, and `SURFACE_CONTRACT_SUMMARY_SCHEMA` as the fixed SDK anchors for table code. Call `paradev.surfaces.get_surface_contract_ids()` when a tool needs a mutable ordered id list, `paradev.surfaces.get_surface_contract_index_catalog()` when it needs documented summary index dimensions, `paradev.surfaces.get_surface_contract_summary()` when an API table or dashboard needs typed `SurfaceContractSummary` / `SurfaceContractSummaryRow` row-count metadata and the status index, `paradev.surfaces.get_surface_contract_status_ids(status)` when it needs the ordered surface ids for one contract status, `paradev.surfaces.get_surface_contract_summary_row(identifier)` when it needs one compact table row, and `paradev.surfaces.get_surface_contract(identifier)` when it needs one exact contract payload. Use `paradev.surfaces.get_surface_contract_selection(identifier=..., status=...)`, CLI `paradev architecture --surface-contracts` / `paradev architecture --surface-contract <id>`, REST `GET /surface-contracts?identifier=...` / `GET /surface-contracts?status=...`, or MCP `surface_contracts` when a surface needs one shared selector path for the summary, one exact contract payload, or one status-index id list. `paradev.surfaces.render_surface_contract_reference_markdown()` and CLI `paradev architecture --surface-contracts-markdown` generate `docs/user-manual/surface-contract-reference.md`, so adapter-reference tables stay derived from the same SDK-owned catalog. These helpers return the bundle, CLI, LSP, MCP, OpenAPI, and VS Code contract payloads keyed by stable surface identifier without starting external services.

## Frontend API Contract

Frontend-facing work must start from the SDK-owned operation list instead of ad hoc GUI action names. `get_frontend_api_contract()` returns `paradev.sdk.frontend-api.v1` with project, module, collection, build, PDX, LSP, catalog, and surface operation groups, plus `paradev.sdk.frontend-api.summary.v1` counts for operations, groups, status values, read/write modes, workspace sections, and SDK/CLI/REST/MCP/LSP binding coverage overall and by group. `get_frontend_api_selection(operation_id=..., group_id=..., form=..., index_name=..., key=...)` is the shared SDK selector for the full contract, one operation row, one group slice, one operation form, or one flat operation-id index such as status, mode, surface, payload, or workspace section; `get_frontend_api_operation(operation_id)` and `get_frontend_api_group(group_id)` remain SDK-owned lookup views over that same list for callers that already know the stable id, while `get_frontend_api_action(operation_id)` returns `paradev.sdk.frontend-api.action-detail.v1` for one selected action by combining the canonical operation row, workspace action, section membership, derived form, option-source field list, bindings, and execution hints. `get_frontend_api_form(operation_id)` derives operation-specific fields, target buckets, required names, defaults, aliases, controls, finite choices, numeric bounds, `paradev.sdk.frontend-api.option-source.v1` dynamic choice providers, and JSON Schema from the same row. `resolve_frontend_api_options(operation_id, field_name, values)` executes those dynamic providers through SDK-owned `Project.templates(...)` or `Project.inspect(...)` calls and returns `paradev.sdk.frontend-api.options.v1` for GUI dropdowns and autocomplete. `render_frontend_api_typescript()` and CLI `frontend-api --typescript` generate `apps/desktop/src/generated/frontendApi.ts`, exporting operation id/group/status/section unions plus the full JSON contract for TypeScript clients. Operation rows keep human-readable surface strings and also expose machine-readable `bindings` for SDK, CLI, REST, MCP, and LSP clients; generated REST clients should use `bindings.rest.method`, `bindings.rest.path`, and `bindings.rest.query` instead of parsing display strings, and desktop TypeScript should call `getFrontendApiBindings(...)` or `getFrontendApiRestBinding(...)` from `apps/desktop/src/data/frontendApi.ts`. Desktop TypeScript should also use generated `frontendApiSummary`, `getFrontendApiActionDetail(...)` for generated-contract selected-action summaries, `getFrontendApiFormValuesWithDefaults(...)` plus `getFrontendApiFormControls(..., optionResults)` for generated form defaults, render state, static choices, and returned dynamic option rows, `getFrontendApiFormOptionRequests(...)` for option-source availability and ready JSON request planning, `resolveFrontendApiFormOptionRequest(...)` for one-request execution/result state, `resolveFrontendApiNormalizeRequest(...)` and `resolveFrontendApiRestPlanRequest(...)` for normalize/rest-plan execution result state, and `frontendApiInputOperations`, `getFrontendApiInputs(...)`, `getFrontendApiRequiredInputNames(...)`, `getFrontendApiDefaultValues(...)`, and `getFrontendApiOptionSourceInputs(...)` when it needs raw generated `inputs` metadata without the richer Python form projection; it should use `frontendApiEndpointPaths` and `buildFrontendApi*Url(...)` helpers when it calls frontend API discovery/action/options/normalize/rest-request/binding endpoints, plus `buildFrontendApiOptionsRequest(...)`, `buildFrontendApiNormalizeRequest(...)`, and `buildFrontendApiRestPlanRequest(...)` when it needs JSON POST fetch inputs for those meta endpoints. OpenAPI operations also expose `x-paradev-frontend-api-operation-ids`, derived from those same REST bindings, so codegen can map shared routes such as `GET /projects/inspect` back to every canonical frontend row. The contract also publishes the reverse `index["binding"]` map so clients can resolve a surface call such as CLI `project`, MCP `project_inspect`, REST `GET /projects/inspect?kind=modules`, or LSP `textDocument/hover` back to stable operation ids; Python adapters should use `get_frontend_api_binding_lookup(...)`, `get_frontend_api_binding_operation_ids(...)`, or `get_frontend_api_rest_operation_ids(...)`, TypeScript adapters should use the matching helper in `apps/desktop/src/data/frontendApi.ts`, and `get_cli_contract()["frontend_operation_ids"]` plus `get_mcp_contract()["frontend_operation_ids"]` mirror their slices for static adapter registration. `normalize_frontend_api_inputs(operation_id, values)` validates submitted form state, including declared choices and numeric lower bounds, and splits it into `project`, `parameters`, `selectors`, and `projections` without forcing GUI code to guess whether a field named `path` loads a project or filters an artifact. `plan_frontend_api_rest_request(operation_id, values)` reuses that normalized payload plus `bindings.rest` to return the REST method, path, query parameters, JSON body, and source binding. `FRONTEND_API_SELECTORS` owns the operation and group selector names, while `index_name`/`key` expose flat operation-id index projections. The same selector path is exposed by CLI `frontend-api`, CLI `frontend-api --operation`, CLI `frontend-api --group`, CLI `frontend-api --operation ... --form`, CLI `frontend-api --index ... --key ...`, MCP `frontend_api`, and REST/OpenAPI `GET /frontend-api`; CLI `--operation`/`--group`/`--index`, REST `operation_id`/`group_id`/`index_name`/`key`, and MCP selectors all narrow that same contract instead of introducing separate action names. CLI `frontend-api --operation ... --action` and REST `GET /frontend-api/action?operation_id=...` expose selected-action detail through the canonical `surface.frontend_api.action` row. CLI `frontend-api --operation ... --form` and REST `GET /frontend-api?operation_id=...&form=true` return the derived form contract. CLI `frontend-api --operation ... --option-field ... --values-json ...` and REST `POST /frontend-api/options?operation_id=...&field_name=...` expose the same option-source payload through the canonical `surface.frontend_api.options` row. CLI `frontend-api --operation ... --values-json ...` and REST `POST /frontend-api/normalize?operation_id=...` expose the same normalized submission payload through the canonical `surface.frontend_api.normalize` row. CLI `frontend-api --operation ... --values-json ... --rest-request` and REST `POST /frontend-api/rest-request?operation_id=...` expose the REST request plan through the canonical `surface.frontend_api.rest_request` row. CLI `frontend-api --binding-surface ... --binding-key ...` and REST `GET /frontend-api/binding?binding_surface=...&binding_key=...` expose binding reverse lookup through the canonical `surface.frontend_api.binding_lookup` row. Implemented rows point at current SDK, CLI, REST, MCP, or LSP calls; starter project creation is implemented through `Project.create`, CLI `new`, MCP `project_create`, and REST/OpenAPI `POST /projects`; project open/view is implemented through `Project.load(...).to_view()`, CLI `project`, MCP `project_open`/`project_view`, and REST/OpenAPI `GET /projects`; project registry and desktop state are implemented through `registered_projects(...)` and `desktop_state(...)`, CLI `projects`/`desktop-state`, and REST/OpenAPI `GET /projects/list`/`GET /desktop/state`; project browser is implemented through `Project.browser(...)`, CLI `project-browser`, MCP `project_browser`, and REST/OpenAPI `GET /projects/browser`; project discovery is implemented through `Project.find`, CLI `project-find`, MCP `project_find`, and REST/OpenAPI `GET /projects/find`; title-only project rename is implemented through `Project.rename`, CLI `project-rename`, MCP `project_rename`, and REST/OpenAPI `PATCH /projects/rename`; source-module folder rename is implemented through `Project.rename_module`, CLI `module-rename`, MCP `module_rename`, and REST/OpenAPI `PATCH /projects/modules/rename`; source-module removal is implemented through `Project.remove_module`, CLI `module-remove`, MCP `module_remove`, and REST/OpenAPI `DELETE /projects/modules/remove`; module text-file read/write is implemented through `Project.read_module_file` and `Project.write_module_file`, CLI `module-file`/`module-edit`, MCP `module_file`/`module_edit`, and REST/OpenAPI `GET`/`PATCH /projects/modules/file`; authoring template discovery is implemented through `Project.templates`, CLI `templates`, MCP `project_templates`, and REST/OpenAPI `GET /projects/templates`; collection descriptor creation is implemented through `Project.create_collection`, CLI `collection-create`, MCP `collection_create`, and REST/OpenAPI `POST /projects/collections`; collection descriptor rename is implemented through `Project.rename_collection`, CLI `collection-rename`, MCP `collection_rename`, and REST/OpenAPI `PATCH /projects/collections/rename`; collection descriptor removal is implemented through `Project.remove_collection`, CLI `collection-remove`, MCP `collection_remove`, and REST/OpenAPI `DELETE /projects/collections`; collection descriptor text-file read/write is implemented through `Project.read_collection_file` and `Project.write_collection_file`, CLI `collection-file`/`collection-edit`, MCP `collection_file`/`collection_edit`, and REST/OpenAPI `GET`/`PATCH /projects/collections/file`; collection descriptor source inventory is implemented through `Project.inspect('sources')` with `owner_kind=collection`, CLI `sources --owner-kind collection`, MCP `project_inspect`, and REST/OpenAPI `GET /projects/inspect?kind=sources`; build plan/emit is implemented through `Project.build`, CLI `build`, and REST/OpenAPI `POST /projects/build`; catalog write/refresh is implemented through `paradev.hb.catalog_write`, `paradev.hb.catalog_refresh`, CLI `hb catalog-write`/`hb catalog-refresh`, and REST/OpenAPI `POST`/`PUT /projects/catalog`; PDX formatting is implemented through `format_pdx_file`, CLI `format`, MCP `pdx_format`, and REST/OpenAPI `POST /pdx/format`; LSP diagnostics, symbols, hover, formatting, completion, and semantic tokens are implemented through `diagnose_pdx_lsp_text`, `document_symbols_pdx_lsp_text`, `hover_pdx_lsp_text`, `format_pdx_lsp_text`, `complete_pdx_lsp_text`, `semantic_tokens_pdx_lsp_text`, LSP `textDocument/publishDiagnostics`/`textDocument/documentSymbol`/`textDocument/hover`/`textDocument/formatting`/`textDocument/completion`/`textDocument/semanticTokens/full`, REST/OpenAPI `POST /lsp/diagnostics`/`POST /lsp/symbols`/`POST /lsp/hover`/`POST /lsp/formatting`/`POST /lsp/completion`/`POST /lsp/semantic-tokens`, and the stdio server command `paradev lsp serve`. Frontend-local rows, currently project activation, stay in app workspace state and must not mutate SDK project files.

Desktop build lifecycle rows are implemented separately from `Project.build` plan/emit rows: `build.start`, `build.runs`, `build.status`, and `build.interrupt` bind to `desktop_start_build(...)`, `desktop_build_runs(...)`, `desktop_build_status(...)`, `desktop_interrupt_build(...)`, and REST/OpenAPI `POST /desktop/builds`, `GET /desktop/builds`, `GET /desktop/builds/status`, and `POST /desktop/builds/interrupt`. Canonical frontend status/interrupt operations and REST routes require an exact nonblank `run_id`; explicit empty or whitespace values are invalid. The Python registry retains oldest-active selection only when the id is genuinely omitted for compatibility callers. GUI code executes these operations through `plan_frontend_api_rest_request(...)`; the Python process owns child lifecycle.

The desktop module workspace treats Registry-discovered collections as
first-class entities. Source edits use the guarded draft writer, identity
changes use `Project.rename_collection`, removal performs the exact
`Project.remove_collection` dry-plan/apply hash pair, and per-collection builds
target `kind="collection"`. Creation comes from
`Project.templates(kind="collection")`. A diagram exposes scope creation only
when its registered provider publishes
`scope_authoring_kind="collection"`; renderer and family names are not routing
inputs.

Static LSP adapters should also read `get_lsp_contract()["frontend_operation_ids"]` when they need the stable frontend operation ids for `textDocument/*` methods.

`get_frontend_api_binding_index(surface)` returns a copied reverse binding map for one callable surface. Python surface-contract builders such as `get_cli_contract()`, `get_mcp_contract()`, and `get_lsp_contract()` should use it for `frontend_operation_ids` instead of reading raw `contract["index"]["binding"]`.

`get_frontend_api_group_operation_ids(group_id)` and `get_frontend_api_status_operation_ids(status)` return copied operation-id lists for API tables, dashboards, and audits that need group/status slices without reading raw `contract["index"]`.

Desktop TypeScript clients should use `frontendApiGroupIndex` / `getFrontendApiGroupOperationIds(...)` and `frontendApiStatusIndex` / `getFrontendApiStatusOperationIds(...)` from `apps/desktop/src/data/frontendApi.ts` for the same group/status slices instead of filtering `frontendApiOperations`.

`get_frontend_api_mode_operation_ids(mode)` and desktop TypeScript `frontendApiModeIndex` / `getFrontendApiModeOperationIds(...)` return read/write operation-id lists for API tables and dashboards without filtering operation rows.

`contract["index"]["surface"]` lists every operation id backed by SDK, CLI, REST, MCP, or LSP, plus `unbound` frontend-local rows. Python clients should use `get_frontend_api_surface_operation_ids(...)` for surface-wide tables instead of scanning operation rows.

`contract["index"]["payload"]` maps payload schema names to operation ids and groups rows without a declared response payload under `untyped`. Python renderer registries and payload-specific panels should use `get_frontend_api_payload_operation_ids(...)` instead of scanning operation rows.

`contract["index"]["workspace_section"]` maps SDK-owned workspace section ids to operation ids. Python shell navigation and section-level API tables should use `get_frontend_api_workspace_section_operation_ids(...)` instead of scanning `workspace["sections"]` rows.

Inspection-backed frontend rows use the shared dispatcher instead of bespoke endpoints: `Project.inspect(kind, **filters)`, REST/OpenAPI `GET /projects/inspect?kind=...`, and MCP `project_inspect`. Those rows include module and collection read panels, read-only build panels, and read-only catalog preview/query panels; each row advertises its concrete payload schema such as `paradev.build.modules.v1`, `paradev.build.summary.v1`, `paradev.build.assets.v1`, `paradev.build.sprites.v1`, or `paradev.hb.catalog-preview.v1`. Mutating catalog write/refresh rows use the project-scoped resource endpoint `POST`/`PUT /projects/catalog` instead of the inspection dispatcher.

`build.graph` is the frontend visualization contract for source, artifact, and dependency traces. Graph node rows expose stable `group`, `display_label`, `display_detail`, and `display_path` fields plus `summary["nodes_by_group"]` and `index["nodes_by_group"]`, so clients can render graph lanes and filters without reverse-parsing node ids.

Project-management frontend rows expose stable `inputs` for GUI forms and importer actions. `project.create`, `project.find`, `project.open`, `project.view`, `project.list`, `project.state`, `project.browser`, `project.inspect`, `project.rename`, and frontend-local `project.activate` list their field names, primitive types, required flags, and defaults directly in the operation row so clients do not copy CLI options or OpenAPI parameter lists. `project.inspect` intentionally exposes only generic dispatcher `path` and SDK inspection `kind` fields; panels that need detailed filters should use the concrete inspection-backed rows.

Every implemented frontend operation must declare its input contract. Use concrete `inputs` rows for GUI-submitted values, and use explicit `inputs=[]` for form-less implemented actions such as contract exports or CLI-owned namespaces that should not become accidental GUI forms.

Module and collection frontend rows follow the same contract. List/source-slot/source rows expose inspection filters, view rows require the selected `module_id` or `collection_id`, shared authoring rows carry default `kind` values, and mutating file/scaffold/remove/create rows keep body fields plus safe booleans such as `write`, `create`, and `force` in the operation row.

PDX and LSP frontend rows expose editor-facing inputs with distinct boundaries. PDX parse/token/dump/format rows operate on saved files through required `path` fields and safe formatter defaults, while LSP diagnostics/symbols/hover/formatting/completion/semantic-token rows operate on unsaved editor text with optional document identity, required positions where relevant, and optional project/catalog paths for database-backed completions.

Build, catalog, and surface rows also publish frontend inputs. Build rows expose project `path`, `profile`, and SDK inspection filters; `build.plan`, `build.emit`, and `build.diagnostics` also expose optional `strict_metadata` so callers can inherit `paradev.build.strict_metadata` from `CM_PARADEV` or explicitly choose loose versus blocking unknown metadata diagnostics. `build.start` exposes the desktop build lifecycle with required `project_root` plus optional `mode`, `profile`, `strict_metadata`, `parallelism`, and `target`; `build.runs` accepts an optional `project_root` filter and returns `paradev.desktop.build-runs.v1`; canonical `build.status` and `build.interrupt` require an exact `run_id` and return `paradev.desktop.build-run.v1`. `build.artifacts` uses frontend `artifact_path` with `maps_to="path"` to avoid colliding with project `path`, `build.assets` uses `file_format` for image/static-copy filtering, and `build.sprites` uses exact `name` filtering for sprite panels. Dynamic option-source fields should call `resolve_frontend_api_options(...)` instead of using GUI-owned lists: templates and source roots come from `module.templates`, families from `build.families`, existing modules from `module.list`, existing collections from `collection.list`, artifact choices from `build.artifacts`, and diagnostic codes from `build.diagnostics`. Catalog write/refresh/query rows expose the optional database path and query filters, with write bound to REST `POST /projects/catalog` and refresh bound to REST `PUT /projects/catalog`; `surface.frontend_api` publishes its operation/group selectors plus the `form=false` projection flag as input fields, `surface.frontend_api.action` publishes the required `operation_id` for selected-action detail, `surface.frontend_api.options` publishes required `operation_id` and `field_name` plus submitted `values`, `surface.frontend_api.normalize` publishes the required `operation_id` plus submitted `values`, and `surface.frontend_api.rest_request` publishes the same required `operation_id` plus submitted `values` for request planning.

GUI navigation should consume `get_frontend_api_workspace()` or CLI/REST `frontend-api --workspace` / `GET /frontend-api/workspace` rather than duplicating panel/action grouping. The workspace projection is derived from the canonical operation ids and groups actions into project switcher, project browser, authoring, source editor, build, catalog, and surface-contract sections. Workspace action rows use `paradev.sdk.frontend-api.action.v1`; each row exposes the operation payload schema, callable `bindings`, `execution.default_surface`, `execution.available_surfaces`, `execution.confirmation`, `form_schema`, `normalizer_schema`, and `rest_request_schema` hints. GUI shells should call `get_frontend_api_action(operation_id)`, CLI `frontend-api --operation ... --action`, REST `GET /frontend-api/action?operation_id=...`, or TypeScript `getFrontendApiActionDetail(operation_id)` when rendering one selected action detail instead of stitching workspace, form, bindings, and option-source data in frontend code. TypeScript GUI code should import `apps/desktop/src/data/frontendApi.ts` for the typed helper and use `frontendApiWorkspaceActions`, `getFrontendApiAction(...)`, `getFrontendApiActionDetail(...)`, `getFrontendApiFormValuesWithDefaults(...)`, `getFrontendApiFormControls(...)`, `getFrontendApiFormOptionRequests(...)`, `resolveFrontendApiFormOptionRequest(...)`, `resolveFrontendApiNormalizeRequest(...)`, `resolveFrontendApiRestPlanRequest(...)`, `getFrontendApiSectionActions(...)`, and `getFrontendApiDefaultSectionAction(...)` for workspace action rows, selected-action summaries, local form values plus defaults, form render state, option-source request planning/execution, and normalize/rest-plan result state; use `frontendApiInputOperations`, `getFrontendApiInputs(...)`, `getFrontendApiRequiredInputNames(...)`, `getFrontendApiDefaultValues(...)`, and `getFrontendApiOptionSourceInputs(...)` when a panel only needs generated input rows, required-name lists, defaults, or option-source fields. Use `frontendApiEndpointPaths`, `buildFrontendApiActionUrl(...)`, `buildFrontendApiOptionsUrl(...)`, `buildFrontendApiNormalizeUrl(...)`, and `buildFrontendApiRestRequestUrl(...)` when calling SDK-owned frontend API meta endpoints from TypeScript. Use `buildFrontendApiOptionsRequest(...)` and `resolveFrontendApiFormOptionRequest(...)` only through the helper/planner path so option requirement checks, fetch inputs, and offline/non-OK error shaping stay centralized; use `buildFrontendApiNormalizeRequest(...)`, `buildFrontendApiRestPlanRequest(...)`, `resolveFrontendApiNormalizeRequest(...)`, and `resolveFrontendApiRestPlanRequest(...)` through the same helper path so submitted-value bodies and meta-result status stay centralized. Use `apps/desktop/src/generated/frontendApi.ts` only as the machine-generated source artifact and regenerate it with `rtk uv run paradev frontend-api --typescript` whenever the Python operation list changes. GUI shells should treat REST as the default executable surface when `execution.default_surface` is `rest`, and must honor `execution.confirmation.required` before executing a planned REST request; SDK scripts, VS Code, MCP, and LSP adapters can choose their own available binding. Frontend-local rows such as `project.activate` remain app workspace state and must not publish a callable SDK/REST binding. GUI form rendering should consume `get_frontend_api_form(operation_id)` rather than duplicating `inputs` normalization. The form contract is derived from the canonical row and includes ordered `fields`, SDK-owned field `label` and `description` text, field-level `target` buckets, plain `required`, ready-to-apply `defaults`, finite `choices`, `option_source` provider hints, numeric `minimum` bounds, frontend-to-SDK `aliases`, and `json_schema`. Python adapters that receive submitted values should call `normalize_frontend_api_inputs(...)`, CLI adapters should call `frontend-api --operation ... --values-json ...`, and REST adapters should call `POST /frontend-api/normalize?operation_id=...`; all three return the same payload shape after enforcing unsupported fields, required values, declared choices, and lower bounds. Use `project["path"]` to load the workspace and `parameters` as the SDK method/filter kwargs. When the next adapter step is an HTTP call, call `plan_frontend_api_rest_request(...)`, CLI `frontend-api --operation ... --values-json ... --rest-request`, or REST `POST /frontend-api/rest-request?operation_id=...` so query/body splitting remains SDK-owned.

Confirmation UI state is frontend-local but policy-owned by the SDK. TypeScript shells should store accepted confirmation in `FrontendApiActionConfirmationStates`, check it through `isFrontendApiActionConfirmationSatisfied(...)`, render the SDK title/summary/scope/style from `execution.confirmation`, and reset accepted state whenever submitted values change.

Run button state is helper-shaped too. TypeScript shells should pass the selected operation id, confirmation policy, REST-plan result, REST-execution result, and confirmation acceptance map to `getFrontendApiActionRunState(...)`; render its `disabled`, `detail`, `status`, and `confirmation_satisfied` fields instead of recomputing readiness or error text inside React components.

Selected-action panel composition should go through `getFrontendApiActionPanelState(...)` when a panel needs the common bundle: selected-action detail, fields, submitted values with defaults, controls, option requests, normalize/rest-plan requests, confirmation state, Run state, and stable option/execution request keys. Use the lower-level helpers only for panels that intentionally need one piece of that bundle.

Checked-in desktop shell navigation derives feature modules and workspace tabs from `frontendApiWorkspaceSections`, with default action copy from `getFrontendApiDefaultSectionAction(...)`; it must not keep PIHC-specific or GUI-only navigation registries. The selected workspace body renders action rows through `getFrontendApiSectionActions(...)`, selected default-action summary, form/control/request state, confirmation state, Run state, and stable request keys through `getFrontendApiActionPanelState(...)`, option result state through `resolveFrontendApiFormOptionRequest(...)`, normalize/rest-plan result state through `resolveFrontendApiNormalizeRequest(...)` and `resolveFrontendApiRestPlanRequest(...)`, ready REST-plan execution through `buildFrontendApiRestExecutionRequest(...)` and `resolveFrontendApiRestExecutionRequest(...)` after the helper-owned Run state is enabled, each action's default execution surface and required-input count through `getFrontendApiRequiredInputNames(...)`, and keeps sidebar and tab selection synchronized on the same generated workspace-section id type.

## Desktop Build Lifecycle Ownership

The native build registry owns child processes for the lifetime of one ParaDev native app process. The React app shell owns the corresponding presentation state above rail-specific pages, keyed by project root and run identity. `BuildPage` renders only the selected project's slice; leaving the Build rail must not stop polling, lose progress, hide an applicable Interrupt action, or let one project's run appear under another project.

Build conflicts are project-scoped. Within one normalized project root, a full build excludes every other build, a partial build cannot overlap that project's full build, and the same partial target cannot run twice. Independent project roots may build concurrently; registry listing, run-id lookup, recovery, and graceful shutdown remain app-global. Artifact and manifest emission acquires deterministic operating-system file locks for the project source snapshot and every filesystem-equivalent output root, build root, and eligible external HoI4 launcher descriptor target. SDK source mutations acquire the same project-source lock, so an emitted build cannot combine files from opposite sides of one batch edit. External importers that transactionally replace project sources must hold public `paradev.sdk.project_source_mutation_lock(project_root)` from their first source snapshot through the final publication rename; using the same lexical project root coordinates them with GUI/SDK edits and emitted builds. Distinct projects may still plan and publish concurrently, while dry plans remain non-mutating snapshots. Registry locks must not substitute for these filesystem mutation locks.

The SDK progress stream owns compiler and publication phases for every build surface. Artifact-emitting whole-project, family, collection, and module builds emit `validating_publication` at 75% after artifact planning and before publication ownership/path preflight. This phase may remain active while a large project checks tens of thousands of existing destinations. Discovery completion events report real `source_cache_hits`, `source_cache_misses`, `source_cache_refreshes`, and cached module/collection counts when cache reuse was attempted; the desktop displays compiler-owned facts instead of inventing simulated time or cache progress. Dry plans and builds blocked before emission do not claim to validate publication.

Parsed-source cache state lives under
`.paradev/cache/source-families/`, outside authored modules and generated mod
output. Each family entry is bounded compressed JSON containing lossless PDX,
localization, copy-source, metadata, diagnostic records, and a separately
checksummed sorted per-file digest inventory. Cache identity includes the source
root, family, complete content fingerprint, slot and metadata contracts,
strictness mode, parser/loader implementation, runtime, PyYAML version, and both
the HeavenBase package version and loaded helper-source fingerprints. A cache
hit first matches every non-source identity field, decodes the bounded payload,
then performs one final source validation against the stored inventory. Digest
reuse requires a trusted local filesystem plus exact size, mtime, precise ctime,
device, and inode observations; changed or ambiguous files are securely opened
and rehashed. Unknown filesystems, coarse metadata, symlinks, cross-device
subtrees, corruption, or concurrent drift fail conservatively. Full builds
parse fresh and may atomically refresh the cache; cached and targeted builds
reuse only exact matches. An editable HeavenBase change therefore invalidates
the entry without requiring a version bump. A missing, stale, corrupt,
oversized, unwritable, or concurrently invalidated entry cannot alter compiler
behavior and falls back to a fresh family parse.
Publication state, artifact ledgers, and output ownership are never loaded from
this cache. Cache controls remain internal to the compiler; the public
`Project.discover_modules(...)` and `Project.discover_collections(...)`
signatures do not expose cache-maintenance arguments.

## Project Extension Registry Lifecycle

Project-local `extensions/*` folders enter every surface through the same
HeavenBase 0.1.2.2 `ModuleService` install, inspect, resolve, and activation
path. SDK, CLI, REST, MCP, and desktop code must not import project extensions
through a privileged fallback.

Editable extension code remains visible at `extensions/<id>/__init__.py`.
Generated Registry metadata belongs at
`extensions/<id>/.paradev/meta.yaml`, outside the ordinary authoring surface.
ParaDev snapshots that source folder, projects the hidden descriptor to the
standard root-level `meta.yaml` required by HeavenBase, verifies equal
content digests before and after staging, and then calls the unchanged
`ModuleService.install(...)` path. An ordinary external HeavenBase bundle with
a root-level `meta.yaml` remains supported. A folder containing both
descriptor locations is rejected rather than choosing one.

For a module family, the project bundle exposes exactly one path-backed
`hb.Entity` and one path-backed `paradev_build_family` target. The Entity class
is the single source of truth for its identifier, record fields, semantic
family, `resource_slots`, and compilation hooks; the co-located family target
must construct its compiler from those slots. A path-backed Entity descriptor
must not retain `meta.definition`: that would be a second, potentially stale
schema beside the Python class. Inline definitions remain appropriate for the
inert HeavenBase Extension registration and authoring-template records.
`scripts/materialize_project_extension_entities.py` removes any stale Entity
definition while materializing or rechecking a project bundle.

The PIHC3 architecture gate installs all project bundles through
`ModuleService`, resolves every Entity and family target from the Registry,
and checks the runtime Entity id, non-empty record schema, family identity,
resource-slot equality, and normalize/check/emit hook coverage. Its
`localisation` bundle is intentionally an auxiliary writer/postprocessor and
therefore has no Entity or module family.

HeavenBase's durable Registry uses compare-and-set publication. ParaDev owns
the integration policy around that public contract: persistent project
extension installs are serialized across ParaDev processes, a conflicting
external publication is refreshed and retried with a finite bound, and
unrefreshable contention remains a contextual project error. Successful
installs publish an ignored
`.paradev/cache/extension-install.json` receipt. That receipt is derived state,
not project metadata: ParaDev reuses it only when extension-folder content
digests, descriptor keys, and every durable installation coordinate and
manifest fingerprint still match. A stale, incomplete, corrupt, deleted, or
unwritable cache never changes extension behavior; ParaDev validates and
reinstalls through HeavenBase instead.

The byte-preserving migration utility
`scripts/hide_project_extension_metadata.py` is dry-run by default. With
`--write`, it publishes the hidden name through a same-filesystem hard link
before removing the visible name. A crash may leave two identical names, but
never an extension without a descriptor; rerunning removes the verified
duplicate.

## Registry-Owned Family Identity

Each build family owns both compiler behavior and presentation identity. A
family registered in Python may set `FamilyPresentation`; a project extension
declares the same inert capability under its hidden build-family descriptor:

```yaml
meta:
  presentation:
    id: inventory-items
    title: Inventory Items
    group: events
    aliases: [inventory]
    title_key: modules.inventoryItems.title
```

The compiler family name remains the source folder and hook identity, such as
`inventory_item`. The presentation `id` is the stable SDK/desktop identity.
`BuildRegistry.resolve_family(...)` is the only alias resolver. Registry
family views and `Project.browser()` expose the normalized presentation,
including registered families with zero modules, so an empty external family
is still create-ready. Invalid or ambiguous selectors fail during Registry
assembly.

The desktop consumes `id`, `title`, `group`, `aliases`, and `title_key` from
the browser contract. It must not keep a second table of known family names,
pluralization rules, navigation groups, or labels. Catalog-hydrated module
rows inherit the selected Registry presentation id; compiler family names are
never reinterpreted as UI ids. This is what allows a PIHC3-only entity family
to appear, group, localize, scaffold, and edit without a ParaDev frontend
change.

Module identity copy is also family-owned. Standard source-family dataclasses
declare `identity_rewriter`; project-local families inherit the default token
rewriter and may replace it or set it to `None`. Registry family views expose
this as `authoring.identity_copy`, and
`BuildRegistry.identity_rewriter_for(...)` is the only resolution seam.
`Project.duplicate_module(...)` uses that capability inside its guarded
filesystem transaction, including projected target paths and content hashes
in the plan. The generic SDK, CLI, REST, MCP, and desktop adapters never
dispatch on family names.

Registry-owned display identity follows the same boundary. Project-browser
module rows expose the concrete ordered `title_keys` resolved from
`title_loc_keys` or the family payload fallback. Desktop Name edits target
that localization key and preferred language, then submit the localization
edit plus `module_rename` through one `Project.apply_source_draft(...)`
request. The final folder move accepts an unchanged object id, preserves
authored file bytes, and never causes the generic desktop client to create a
title-only `meta.yaml`. Direct SDK/CLI callers may still use
`Project.rename_module(..., title=...)` when no source edit is part of the
operation.

On shell startup or renderer/webview reload, the app automatically calls the build-run listing operation before enabling build controls. It reconciles every active full or partial run plus the newest 256 retained terminal runs, then polls each active `run_id` independently. Every retained terminal payload exposes `terminalSequence`, a nonnegative monotonic causal ordinal assigned by that native registry; it orders terminal observations even if the wall clock moves backward. The value is meaningful only between payloads from the same registry lifetime and must not be compared across native-process restarts. Terminal eviction follows this sequence rather than wall-clock timestamps, and best-effort removes the evicted run's temporary output, stderr, and progress files; an exact lookup for an evicted run returns `idle`. Project filters use the same canonical-path/filesystem-identity semantics as conflict checks. This recovery applies only while the same native ParaDev process and its registry remain alive. Users never need to enter or copy a run id.

Renderer build history is best-effort local presentation state, not authoritative process ownership. It may preserve previously recorded terminal rows across a reload, including local removal tombstones, but it cannot recover a child process missing from the native registry or turn an evicted terminal id back into a live backend run.

The renderer also keeps a bounded best-effort checkpoint of the newest concrete run in each project/target slot. This checkpoint contains only presentation fields and deliberately omits registry-local terminal sequence values. Native recovery always wins. When a checkpoint says a run was active but a new native registry does not list that run, the renderer converts the checkpoint into one durable interrupted presentation row and keeps Run Game disabled until a later successful build establishes a clean current state. This does not preserve, revive, or claim ownership of the old child process.

A graceful native app close closes the registry, interrupts every app-owned build process group, reaps its children, and best-effort removes that registry's retained output, stderr, and progress files. Those temporary paths are native-process/session-scoped: they remain reachable while the registry is open but are not durable build artifacts. ParaDev intentionally does not claim that a build survives a full process exit, crash, or relaunch; after a process restart the user starts a new build. An ungraceful hard crash can leave session temp files for later operating-system cleanup, but a normal restart does not accumulate them. This bounded shutdown policy prevents background compilers from becoming orphaned while keeping rail navigation and renderer reload safe.

## Current Desktop Scope

The maintained desktop shell includes:

- left-rail project management, editing, agent authoring, build, configuration,
  and developer workspaces;
- SDK-backed project browsing and source editing through CodeMirror;
- module scaffold, validated source-draft, and project-refresh flows;
- app-level, project-keyed build start/recovery/status/interrupt state;
- build progress, diagnostics, output opening, and HoI4 launch controls;
- main tabs, optional split workspace, inspector, localization, and maintained themes;
- Python-wheel packaging with a thin macOS system-WebView host.

The desktop Agents workspace is a thin discovery and navigation client over
these contracts. Capability totals come from the active project's browser and
template payloads; the page opens the existing reviewed AI batch-authoring flow
and publishes the canonical MCP/skill entry points. The
`paradev.desktop.agent-authoring.v1` payload is resolved by the Python desktop
service from the active runtime and packaged resources, including the resolved
`.agents/skills/paradev-authoring/SKILL.md` path and availability. React does
not maintain a frontend family catalog, start an independent mutation path, or
present placeholder session state as a shipped agent runtime.

## Authoring Surface Contract

Authoring and scaffold flows are SDK-owned across all surfaces:

- CLI: `templates` maps to `Project.templates`, `authoring-path` maps to `Project.authoring_path`, `authoring-plan` maps to `Project.authoring_plan`, `scaffold` maps to `Project.scaffold_module`, `module-batch-create` maps to `Project.create_modules`, and `module-duplicate` maps to `Project.duplicate_module`; the CLI contract helper also lists `templates` filters, and scaffold payloads nest the same authoring-plan contract for the target module.
- REST/OpenAPI: `/projects/templates` lists starter templates, source roots, typed args, GUI-ready form fields, renderer kind, family default assets, per-template `authoring_ready` state, and exact filters for `template_id`, `family`, `source`, `authoring_ready`, and `diagnostic_code`; `/projects/authoring-path` resolves one module or collection destination from required `kind`, `family`, and `target_id` query parameters, plus optional `source_root`; `/projects/authoring-plan` adds the expected source-slot contract, family-level default-asset metadata for matching slots, and current `empty`/`missing`/`satisfied`/`diagnostic` slot status for that destination; `/projects/scaffold` plans or writes a template through `Project.scaffold_module`; `/projects/modules/create-batch` plans or atomically applies one guarded module batch through `Project.create_modules`; `/projects/modules/duplicate` exposes the same Registry-owned identity plan and guarded apply.
- MCP: `paradev mcp serve` is the first-class stdio entry point. Its bounded runtime toolkit exposes read-only `project_templates`, `project_authoring_path`, `project_authoring_plan`, filtered `project_browser`, stable revision-bearing `module_file` and `collection_file`, bounded Registry-owned `module_asset`, generic module/collection localization workspaces and plans, and Registry-backed diagram reads over the same SDK methods. Mutations route through guarded `project_create_modules`, `project_draft_apply`, the bounded `module_source_form_update_batch` planner/apply tool, collection scaffold/removal, module membership/duplicate/metadata cleanup, and diagram-edit contracts. The source-form batch tool resolves module source slots through the active Registry and delegates exact text planning to `Project.plan_source_form_updates(...)`; it never owns family parsing or scalar patch semantics. `module_asset` likewise delegates asset ownership and stable binary snapshots to `Project.read_module_asset(...)`, returning metadata by default and base64 only when requested. `project_templates` advertises the same filter fields as the SDK and CLI. The broader static MCP contract remains the target catalog for additional adapters.

GUI, MCP, REST, importer, and editor clients should call these contracts when they need source roots, starter templates, one concrete authoring destination, the files a compiler family expects before sources exist, or a guarded scaffold write. Batch creation is plan-first: clients apply only with the exact `plan_hash` returned by a current dry plan, and a missing, stale, conflicting, or partially existing module blocks the entire transaction. They should use template `form.fields` to render generic create dialogs, template `renderer` to explain whether files come from declarative file entries or a Python renderer, template `directory` to display the physical naming rule, template `default_assets` plus authoring-plan slot `default_asset` rows for optional preview/override affordances, template `authoring_ready`, the template index, authoring-plan row status, and the status index for preflight UI instead of inferring module folders, source-slot rules, or missing-file checks from CLI command text or duplicate HOI4-specific path rules. Scaffold and batch module plans keep logical `object_id` and `module_id` fields and add `folder_name` for the resolved physical directory. A unique existing folder for the logical id is reused; aliases and case- or NFC-equivalent collisions block. Module-local `.paradev/` content is reserved system metadata and is excluded from scaffold idempotence comparisons; a fresh scaffold creates only trusted extension-declared system files. Default assets are class-level family metadata with `injected: false`; scaffold payloads must not imply that a default asset was copied into an instance folder. Family contract rows from `Project.families(...)` also own metadata form rules: `metadata.keys` is the accepted top-level key set, `metadata.common_keys` is the SDK-wide subset, `metadata.family_keys` is the compiler-owned subset, and `metadata.unknown_key_policy` reports the loose/strict diagnostic severities. The shared `comment` metadata key is accepted for optional developer notes on modules and collections.

Existing PDX editing follows the same open Registry seam. A family may expose
`source_form_field_hints`, keyed by exact PDX field name, with optional
localized `label` and `description` values. The generic exact-token projector
uses those declarations without knowing the family id, marks domain help as
`description_source="declared"`, and supplies contextual generated help for
all remaining scalar controls. Returned forms include a `coverage` object with
`shown_controls`, `total_controls`, and `truncated`. Documents larger than the
bounded 96-control/32-section projection retain Guided mode for the safe
prefix and tell clients exactly what remains available only in Code mode;
malformed source, unsafe tokens, excessive nesting, stale spans, and
family-declared invalid hints still fail closed. The desktop, REST, MCP, and
SDK update planners consume the same exact source spans and never guess PDX
semantics from a family switch.

Localization editing uses that seam as well. `Project.source_form(...)`
offers the generic `paradev.localization.text-form.v1` projector only when the
selected path matches a `loc` resource slot on the active Registry family.
The shared loader and projector use one lossless parser for bracket-section
and language-header sources. Every control carries a guarded
`replace-loc-text` patch with canonical language, key, occurrence, exact
UTF-16 span, original text, newline style, and source-length revision. The
desktop may preview that replacement locally, but Apply always asks the SDK to
reparse and plan the complete text again. Bounded files retain Guided mode for
the first 96 entries and publish exact coverage for the Code-only remainder.
Malformed syntax, mixed line endings, overlapping or stale spans, type
mismatches, and replacement text that would introduce a localization section
fail closed.

The cross-language table is target-generic rather than module-specific.
`Project.localization_workspace(...)` and
`Project.plan_localization_update(...)` accept a discriminated
`target_kind="module" | "collection"`, a target id, and an optional family.
They resolve the selected source unit through the Registry's effective `loc`
slots, return `paradev.localization-workspace.v2` /
`paradev.localization-update-plan.v2` payloads with one nested `target`, and
name source ownership with `unit_relative_path`. REST operations
`localization.workspace` and `localization.plan`, MCP tools
`localization_workspace` and `localization_plan`, and the desktop collection
inspector are projections of that same SDK contract. No adapter guesses a
collection's localization files or maintains a module-only compatibility
route.

Images and other opaque module resources are never family-switched in React.
Their authoring surface is derived from Registry `copy` slots: a unique safe
destination opens the image or asset draft transaction, ambiguous or missing
destinations require explicit review, and Apply retains the same revision and
project-containment guards as text sources.

Registered module-diagram providers may publish `selection_defaults`, a
declarative mapping from fields on the reviewed source-backed selected node to
authoring-template value fields. Optional finite numeric offsets and one
`{value}` string projection are provider-owned. Desktop clients may apply
these mappings only as visible initial form values; template validation, dry
planning, exact-hash application, and source transactions remain SDK-owned.
This lets project extensions define Technology prerequisites, Doctrine hidden
layout/path state, or MIO starting positions without a family switch in
TypeScript or the generic SDK layer.

Providers also own the initial diagram scope. The optional `initial_scope`
capability is a closed protocol: `selected-entity` is the compatibility
default and may seed the first projection from the active source unit, while
`project` starts from the provider's complete project projection. A client
must not let an incidental source-list selection narrow a project-scoped first
view. PIHC3's MIO provider uses `project`; its organization selector then
chooses one organization tree from the complete Registry projection. This is
a provider capability, not a family-id branch in the desktop.

Editable providers publish `relationships` beside those authoring defaults.
The declaration carries an open planner `kind` plus a closed, reusable UI
protocol: `visual_kind`, `selected_endpoint`, `owner_endpoint`, `symmetric`,
and `cardinality`. Desktop controls and canvas picking consume only that
protocol. Renderer adapters own draft projection and source-revision binding;
provider planners still validate the exact edge intent and source grammar.
This keeps bundled and project-defined entities on the same Registry seam and
prevents family ids from leaking into relationship editing.

External diagram providers that do not need a bundled domain-specific canvas
use `renderer="graph"`. Their ordinary `paradev.sdk.module_diagram.v1` payload
supplies unique node ids, paired finite coordinates, optional
`relative_position_id`, localized titles, image/source paths, and reviewed
source revisions. Edges use the open provider-owned `kind` vocabulary and must
reference existing nodes; one `(kind, source, target)` relationship is unique.
The desktop resolves one renderer adapter, projects those facts into the shared
canvas, and sends only generic reviewed position intents (`node_id`, `x`, `y`,
`source_revision`) and edge intents (`kind`, `source_id`, `target_id`,
`present`, `source_revision`) back to the provider planner. Family ids never
participate in renderer dispatch. Malformed nodes, dangling or duplicate edges,
and missing revisions on edited nodes fail visibly instead of being discarded.
The specialized Focus, Technology, Doctrine, and MIO adapters are bundled
renderers over the same SDK seam; unknown renderer ids remain inspectable but
the desktop reports them as unsupported rather than pretending to edit them.

A provider that authors inside an existing graph scope publishes
`node_authoring` and its paired `node_plan`, with
`authoring_kind="diagram-node"`. `node_authoring` declares a bounded scalar
field form and maps reviewed selected-node fields into hidden context;
`node_plan` owns all family semantics and returns either an exact guarded source
replacement plan or a `ModuleDiagramModuleCreation` request for one standalone
module. `Project.edit_module_diagram(..., node_intents=[...])` accepts at most
one such request, rejects mixed position/edge changes, and reuses the same
revision review, exact plan-hash apply, rollback, family build, and Catalog
refresh transaction. PIHC3 Focus and Technology providers create standalone
Entity modules through this seam. Technology's project provider deliberately
projects only modules with one `def` slot while retaining its no-`def`
shared-source support module in the registered family build. The PIHC3 MIO
extension registers the shared HoI4 provider while keeping its
Entity/source slots/compiler project-local; that provider instead adds a trait
and localization inside the selected organization. Neither path requires
desktop or SDK dispatch code to know the family grammar.

The first implemented GUI bridge routes are project-scoped and represented by canonical frontend operation rows. `project.source_text` maps to `GET /projects/{project_id}/sources?path=...` and reads a project-contained UTF-8 source file from either an absolute browser row path or a project-relative path. `module.draft` maps to `POST /projects/{project_id}/modules/{family_id}/drafts`, accepts `object_id`, optional `template_id`, optional scalar `values`, frontend `path` mapped to REST `project_root`, and write flags, resolves browser family ids such as `ideas`, and returns a `paradev.rest.module_draft.v1` wrapper around the SDK scaffold plan. `project.draft_apply` maps to `POST /projects/{project_id}/drafts/apply` and applies validated text edits, file removals, and base64 byte replacements through project-root path validation. `plan_frontend_api_rest_request(...)` fills `{project_id}` and `{family_id}` path parameters from normalized form values so GUI clients do not own route-template substitution.

## Inspection Surface Contract

Read-only project inspections are SDK-owned across all surfaces. `get_project_inspection_contract()` returns the project-independent list of `Project.inspect(...)` kinds, SDK methods, CLI command names, filters, and indexes. `Project.inspections()` returns the same contract with the loaded project id. Static adapters should use the helper before a project exists: `get_cli_contract()["inspection_contract"]`, MCP `project_inspect.inspection_contract`, and OpenAPI `/projects/inspect` `x-paradev-inspection-contract` all expose that same SDK contract. Clients that need one shared selector path should call `get_project_inspection_selection(kind=..., index_name=..., key=...)`; clients that need only convenience slices can still use `get_project_inspection_kinds()`, `get_project_inspection_row(kind)`, `get_project_inspection_index_catalog()`, or `get_project_inspection_filter_kinds(filter_name)` instead of reading raw indexes. `render_project_inspection_reference_markdown()` and CLI `paradev inspections --markdown` generate `docs/user-manual/project-inspection-reference.md`.

## Verification

Backend:

```bash
rtk bash scripts/test.bash
rtk bash scripts/flake.bash --ci
```

Frontend:

```bash
rtk bash scripts/run.bash --web
rtk npm --prefix apps/desktop install
rtk npm --prefix apps/desktop run build
```

Installed host development:

```bash
rtk uv run paradev dashboard
rtk uv run paradev dashboard --no-open
```

Desktop packaging:

```bash
rtk bash scripts/build-wheel.bash
rtk bash scripts/smoke-macos-installed-app.bash \
  --wheel dist/python/paradev-0.1.0.0.dev0-py3-none-any.whl
```

The build-time preview keeps ParaDev on a loopback origin and moves to the next
available development port when necessary. Packaged builds serve the exact
React/Vite output from the Python wheel; `paradev dashboard --install-app` creates the
macOS `.app`, and the installed-app smoke verifies its lifecycle. Windows native
packaging remains deferred.
