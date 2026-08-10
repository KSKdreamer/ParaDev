# Developer Manual

## English

This page is for developers extending ParaDev, not for ordinary mod authoring.

## Architecture Boundary

Keep HoI4 logic in the Python SDK and game package:

```text
src/paradev/sdk/        public Python API
src/paradev/project/    project discovery and manifest loading
src/paradev/pdx/        tokenizer, AST, formatter, diagnostics
src/paradev/build/      modules, collections, artifacts, manifests
src/paradev/games/hoi4/ HoI4 profile and built-in families
src/paradev/hb/         HeavenBase catalog integration
src/paradev/surfaces/   CLI, MCP, REST, LSP, VS Code adapters
```

Surfaces call the SDK. They do not own domain logic.

## Installed Wheel GUI Gate

Build the wheel through its exact-inventory wrapper, then launch it in a
disposable runtime through the same loopback REST lifecycle used by the React
application:

```bash
rtk bash scripts/build-wheel.bash
rtk bash scripts/smoke-wheel-gui.bash \
  --wheel dist/python/paradev-0.1.0.0.dev0-py3-none-any.whl \
  --project projects/PIHC3 \
  --expect-project-id PIHC3 \
  --clean --cached \
  --family military_industrial_organization \
  --module military_industrial_organization/ai_bonus_weights
```

The smoke creates a fresh virtual environment, isolated application home,
isolated temporary directory, and isolated generated-mod root. The installed
app receives a system-only `PATH`, so a passing build proves it uses its own
`sys.executable -m paradev` runtime rather than a developer checkout, `uv`, or
a separately installed `paradev` command. It verifies the packaged hashed
frontend, same-origin bootstrap, deferred project discovery, terminal build
status, compact build summary, and zero-error result for every requested
scope. Omit the build flags for a quick install/launch/project-discovery gate.

Use `--evidence PATH` when durable JSON evidence is required. The destination
must not already exist; the smoke never overwrites prior release evidence.
Use `--copy-project` for small committed fixtures so the compiler cannot write
generated state into the checkout. Do not use it for the multi-gigabyte PIHC3
project; that smoke already isolates its app state, temporary files, and
generated mod while intentionally reusing the project's build cache.

SDK facade audits should prefer `paradev.sdk.get_sdk_api_table()` and `SDK_API_TABLE_SCHEMA` instead of copying `paradev.sdk.__all__` or maintaining separate public-import lists. Regenerate [SDK API Reference](sdk-api-reference.md) with CLI `sdk-api --markdown` whenever public SDK exports change.

Project object audits should prefer `paradev.sdk.get_project_api_table()` and `PROJECT_API_TABLE_SCHEMA` instead of copying `Project` dataclass fields, methods, CLI adapters, frontend operation ids, or inspection-kind mappings. Regenerate [Project API Reference](project-api-reference.md) with CLI `project-api --markdown` whenever the public `Project` surface changes.

Build facade audits should prefer `paradev.build.get_build_api_table()` and `BUILD_API_TABLE_SCHEMA` instead of copying `paradev.build.__all__` or maintaining separate compiler record, family, slot, loader, writer, manifest, view, graph, or planning import lists. Regenerate [Build API Reference](build-api-reference.md) with CLI `build-api --markdown` whenever public build exports change.

Architecture graph helpers describe the cross-surface contract without importing adapter modules. Use `ARCHITECTURE_API_TABLE_ROWS` and `ARCHITECTURE_API_TABLE_SCHEMA` as fixed SDK anchors for architecture table code, `paradev.sdk.get_architecture_api_table()` when audits need the SDK/CLI/REST/MCP entry rows, and `paradev.sdk.render_architecture_api_reference_markdown()` or CLI `architecture --api-table-markdown` to regenerate [Architecture API Reference](architecture-api-reference.md).

PDX parse/format helpers own their own API-standard table. Use `PDX_API_TABLE_ROWS`, `PDX_API_TABLE_SCHEMA`, `paradev.sdk.get_pdx_api_table()`, and `paradev.sdk.render_pdx_api_reference_markdown()` when audits need the SDK `parse_pdx_file(...)`, `format_pdx_text(...)`, `format_pdx_file(...)`, CLI `parse`/`format`/`pdx-api`, REST `/pdx/parse`/`/pdx/format`, and MCP `pdx_parse`/`pdx_format` rows. Regenerate [PDX API Reference](pdx-api-reference.md) with CLI `pdx-api --markdown` whenever the PDX parser, formatter, or adapter table changes.

PDX core facade audits should prefer `paradev.pdx.get_pdx_core_api_table()` and `PDX_CORE_API_TABLE_SCHEMA` instead of copying `paradev.pdx.__all__` or maintaining separate tokenizer, AST, parser, diagnostics, scalar-constant, or facade-helper import lists. Regenerate [PDX Core API Reference](pdx-core-api-reference.md) with CLI `pdx-core-api --markdown` whenever public `paradev.pdx` exports change.

LSP editor helpers also own an API-standard table. Use `LSP_API_TABLE_ROWS`, `LSP_API_TABLE_SCHEMA`, `paradev.sdk.get_lsp_api_table()`, and `paradev.sdk.render_lsp_api_reference_markdown()` when audits need the SDK diagnostics, symbols, hover, formatting, completion, and semantic-token functions, CLI `lsp-api`/`lsp ...` commands, REST `/lsp/...` routes, and JSON-RPC `textDocument/*` methods. Regenerate [LSP API Reference](lsp-api-reference.md) with CLI `lsp-api --markdown` whenever an editor-facing LSP capability changes.

LSP server facade audits should prefer `paradev.lsp.get_lsp_server_api_table()` and `LSP_SERVER_API_TABLE_SCHEMA` instead of copying `paradev.lsp.__all__` or maintaining separate document, JSON-RPC dispatcher, stdio framing, stdio server, or facade-helper import lists. Regenerate [LSP Server API Reference](lsp-server-api-reference.md) with CLI `lsp-server-api --markdown` whenever public `paradev.lsp` exports change.

Surface contract helpers describe the current adapter boundary without starting external services. Use `SURFACE_CONTRACT_IDS`, `SURFACE_CONTRACT_INDEX_CATALOG`, and `SURFACE_CONTRACT_SUMMARY_SCHEMA` as the fixed SDK anchors for table code, `paradev.surfaces.get_surface_contracts()` when audits or tooling need the bundle, CLI, LSP, MCP, OpenAPI, and VS Code contract payloads keyed by stable surface identifier, `paradev.surfaces.get_surface_contract_ids()` when they need a mutable ordered id list, `paradev.surfaces.get_surface_contract_index_catalog()` when they need documented summary index dimensions, `paradev.surfaces.get_surface_contract_summary()` when API tables or dashboards need typed `SurfaceContractSummary` / `SurfaceContractSummaryRow` row-count metadata and the status index, `paradev.surfaces.get_surface_contract_status_ids(status)` when they need the ordered surface ids for one contract status, `paradev.surfaces.get_surface_contract_summary_row(identifier)` when they need one compact table row, and `paradev.surfaces.get_surface_contract(identifier)` when code needs one exact payload. Use `paradev.surfaces.render_surface_contract_reference_markdown()` or CLI `architecture --surface-contracts-markdown` to regenerate [Surface Contract Reference](surface-contract-reference.md). `get_frontend_api_contract()` is the maintained operation list for GUI, importer, desktop, REST, MCP, VS Code, and LSP-facing work; it groups project, module, collection, build, PDX, LSP, catalog, and surface operations and marks unstable gaps as `planned` instead of hiding them.

Surface facade audits should prefer `paradev.surfaces.get_surfaces_api_table()` and `SURFACES_API_TABLE_SCHEMA` instead of copying `paradev.surfaces.__all__` or maintaining separate adapter import lists. Regenerate [Surfaces API Reference](surfaces-api-reference.md) with CLI `surfaces-api --markdown` whenever CLI, REST, MCP, LSP, VS Code, bundle, API catalog, or surface contract facade exports change.

Browser-backed source editing is part of that canonical list. Use `project.source_text` for `GET /projects/{project_id}/sources`, `module.draft` for `POST /projects/{project_id}/modules/{family_id}/drafts`, and `project.draft_apply` for `POST /projects/{project_id}/drafts/apply`; `plan_frontend_api_rest_request(...)` fills `{project_id}` and `{family_id}` from normalized input values before returning the executable REST plan.

Use `get_frontend_api_operation(operation_id)` and `get_frontend_api_group(group_id)` when adapter code already knows the stable id and needs one row or one group slice. Use `get_frontend_api_workspace()` when GUI or importer code needs SDK-owned navigation sections and `paradev.sdk.frontend-api.action.v1` action rows with derived `execution.default_surface`, `execution.available_surfaces`, `execution.confirmation`, callable `bindings`, `form_schema`, `normalizer_schema`, and `rest_request_schema` hints. Use `get_frontend_api_action(operation_id)` when adapter code needs one selected action detail that combines the canonical operation row, workspace action, section membership, derived form, option-source field list, bindings, and execution hints. Use `get_frontend_api_form(operation_id)` when adapter code needs a derived UI/action schema for one operation, including field text, validation, aliases, JSON Schema, and `paradev.sdk.frontend-api.option-source.v1` provider hints for dynamic choices. Use `resolve_frontend_api_options(operation_id, field_name, values)` when adapter code needs to execute those option sources without copying provider dispatch. Use `normalize_frontend_api_inputs(operation_id, values)` when a Python adapter needs submitted form state split into project, parameter, selector, and projection buckets, `plan_frontend_api_rest_request(operation_id, values)` when an adapter needs the REST method, path, query, and JSON body for that same state, and `get_frontend_api_binding_lookup(...)`, `get_frontend_api_binding_operation_ids(...)`, `get_frontend_api_binding_index(...)`, `build_frontend_api_rest_index_key(...)`, or `get_frontend_api_rest_operation_ids(...)` when an adapter needs to map a surface call key or whole adapter surface back to stable operation ids. Use `render_frontend_api_typescript()` or CLI `frontend-api --typescript` to regenerate `apps/desktop/src/generated/frontendApi.ts`, then use `apps/desktop/src/data/frontendApi.ts` from desktop code for the generated `frontendApiSummary`, workspace action rows, selected-action summaries through `getFrontendApiActionDetail(...)`, selected-action panel state through `getFrontendApiActionPanelState(...)`, form defaults through `getFrontendApiFormValuesWithDefaults(...)`, form render state through `getFrontendApiFormControls(...)`, option request planning through `getFrontendApiFormOptionRequests(...)`, option request execution through `resolveFrontendApiFormOptionRequest(...)`, normalization/rest-plan result state through `resolveFrontendApiNormalizeRequest(...)` and `resolveFrontendApiRestPlanRequest(...)`, REST execution request/result state through `buildFrontendApiRestExecutionRequest(...)` and `resolveFrontendApiRestExecutionRequest(...)`, Run disabled/detail/status state through `getFrontendApiActionRunState(...)`, binding helpers, binding-index helpers through `frontendApiBindingIndex`, `getFrontendApiBindingOperationIds(...)`, `buildFrontendApiRestIndexKey(...)`, and `getFrontendApiRestOperationIds(...)`, group/status-index helpers through `frontendApiGroupIndex`, `frontendApiStatusIndex`, `getFrontendApiGroupOperationIds(...)`, and `getFrontendApiStatusOperationIds(...)`, surface-index helpers through `frontendApiSurfaceIndex` and `getFrontendApiSurfaceOperationIds(...)`, input/default/option-source helpers, endpoint/request/payload helpers, and lookup helpers, including `buildFrontendApiOptionsRequest(...)`, `buildFrontendApiNormalizeRequest(...)`, and `buildFrontendApiRestPlanRequest(...)` for frontend API JSON POST meta endpoints, plus `buildFrontendApiBindingLookupUrl(...)` for the binding lookup GET endpoint. They are read-only SDK views over the same operation list, so new frontend-visible capabilities still start by adding one canonical row to `get_frontend_api_contract()`. Do not rederive summary counts, including surface coverage, in TypeScript; `frontendApiSummary` should point at `PARADEV_FRONTEND_API_CONTRACT.summary`. Use `contract["index"]["group"]`, `contract["index"]["status"]`, `getFrontendApiGroupOperationIds(...)`, or `getFrontendApiStatusOperationIds(...)` when a client needs every operation id in one group/status slice. Use `contract["index"]["surface"]` or `getFrontendApiSurfaceOperationIds(...)` when a client needs every operation id backed by one surface. Regenerate the full manual table through `render_frontend_api_reference_markdown()` or CLI `frontend-api --markdown`, and regenerate the compact SDK/CLI table through `render_frontend_api_sdk_cli_markdown()` or CLI `frontend-api --sdk-cli-markdown`; tests keep [Frontend API Reference](frontend-api-reference.md) and [SDK And CLI API Reference](sdk-cli-reference.md) byte-for-byte aligned with those renderers.

Group/status API tables and audits should use Python `get_frontend_api_group_operation_ids(...)` / `get_frontend_api_status_operation_ids(...)` or TypeScript `frontendApiGroupIndex` / `frontendApiStatusIndex` / `getFrontendApiGroupOperationIds(...)` / `getFrontendApiStatusOperationIds(...)` instead of reading raw indexes or filtering rows directly.

Read/write mode API tables and audits should use Python `get_frontend_api_mode_operation_ids(...)` or TypeScript `frontendApiModeIndex` / `getFrontendApiModeOperationIds(...)` instead of filtering operation rows by `mutates`.

Payload renderer registries should use `contract["index"]["payload"]` or TypeScript `frontendApiPayloadIndex` / `getFrontendApiPayloadOperationIds(...)` to list every operation id returning one payload schema. Rows without a declared payload are grouped under `untyped`.

Workspace navigation and section-level API tables should use `contract["index"]["workspace_section"]` or TypeScript `frontendApiWorkspaceSectionIndex` / `getFrontendApiWorkspaceSectionOperationIds(...)` to list every operation id in one SDK-owned workspace section.

Python adapters should prefer `get_frontend_api_group_operation_ids(...)`, `get_frontend_api_status_operation_ids(...)`, `get_frontend_api_binding_index(...)`, `get_frontend_api_surface_operation_ids(...)`, `get_frontend_api_payload_operation_ids(...)`, and `get_frontend_api_workspace_section_operation_ids(...)` over raw `contract["index"]` access for those same grouped operation lists.

Project inspection API tables and adapter preflight UI should use `get_project_inspection_kinds()`, `get_project_inspection_row(kind)`, `get_project_inspection_index_catalog()`, and `get_project_inspection_filter_kinds(filter_name)` over raw `get_project_inspection_contract()["index"]` access. Regenerate [Project Inspection Reference](project-inspection-reference.md) with CLI `inspections --markdown` whenever a `Project.inspect(...)` kind or filter changes.

Authoring template module audits should use `paradev.sdk.templates.get_templates_api_table()` and `TEMPLATES_API_TABLE_SCHEMA` instead of copying template schema constants, dataclasses, registry helpers, or scaffold-planning functions. Regenerate [Authoring Templates API Reference](templates-api-reference.md) with CLI `templates-api --markdown` whenever SDK authoring-template helpers such as `TemplateArg`, `ModuleTemplate`, `template_index(...)`, or `module_scaffold_plan(...)` change.

Copy-root module audits should use `paradev.sdk.copy_roots.get_copy_roots_api_table()` and `COPY_ROOTS_API_TABLE_SCHEMA` instead of copying target-root constants, manifest parser signatures, copied artifact generation, or merge/shadow diagnostic behavior. Regenerate [Copy Roots API Reference](copy-roots-api-reference.md) with CLI `copy-roots-api --markdown` whenever `ARTIFACT_TARGET_ROOTS`, `CopyRootSpec`, `project_copy_roots(...)`, `copy_root_artifacts(...)`, or `merge_copy_root_artifacts(...)` changes.

Overall API reference audits should use `paradev.surfaces.get_api_catalog_table()` and `API_CATALOG_SCHEMA` before copying any reference list by hand. Use `owner_module_index` for module ownership audits and `surface_index` for SDK/CLI/REST/MCP/LSP/frontend/docs coverage audits instead of filtering rows manually. Regenerate [API Catalog Reference](api-catalog-reference.md) with CLI `api-catalog --markdown` whenever an API reference table or generated contract is added, removed, renamed, or moved to a different doc page.

Root package facade audits should use `paradev.get_package_api_table()` and `PACKAGE_API_TABLE_SCHEMA` instead of copying `paradev.__all__`. Regenerate [Package API Reference](package-api-reference.md) with CLI `package-api --markdown` whenever package-level imports such as `Project`, `CM_PARADEV`, `__version__`, or package API table helpers change.

Config facade audits should use `paradev.config.get_config_api_table()` and `CONFIG_API_TABLE_SCHEMA` instead of copying `paradev.config.__all__` or maintaining a second list of config defaults and manager exports. Regenerate [Config API Reference](config-api-reference.md) with CLI `config-api --markdown` whenever public config imports such as `DEFAULT_CONFIG`, `BOOTSTRAP_CONFIG`, `CM_PARADEV`, or config API table helpers change.

GUI launcher facade audits should use `paradev.gui.get_gui_api_table()` and `GUI_API_TABLE_SCHEMA` instead of copying `paradev.gui.__all__` or maintaining a second list of `paradev-gui` launcher exports. Regenerate [GUI API Reference](gui-api-reference.md) with CLI `gui-api --markdown` whenever public GUI launcher imports such as `build_parser`, `main`, or GUI API table helpers change.

Desktop facade audits should use `paradev.desktop.get_desktop_api_table()` and `DESKTOP_API_TABLE_SCHEMA` instead of copying `paradev.desktop.__all__` or maintaining a second desktop state helper list in GUI clients. Regenerate [Desktop API Reference](desktop-api-reference.md) with CLI `desktop-api --markdown` whenever public desktop imports such as `DESKTOP_STATE_SCHEMA`, `desktop_state`, or desktop API table helpers change.

Games facade audits should use `paradev.games.get_games_api_table()` and `GAMES_API_TABLE_SCHEMA` instead of copying `paradev.games.__all__` or maintaining a second game profile registry helper list. Regenerate [Games API Reference](games-api-reference.md) with CLI `games-api --markdown` whenever public games imports such as `PROFILE_REGISTRIES`, `registry_for_profile`, or games API table helpers change.

Project package facade audits should use `paradev.project.get_project_facade_api_table()` and `PROJECT_FACADE_API_TABLE_SCHEMA` instead of copying `paradev.project.__all__`. Regenerate [Project Facade API Reference](project-facade-api-reference.md) with CLI `project-facade-api --markdown` whenever compatibility project package imports or facade helpers change.

Localization facade audits should use `paradev.localization.get_localization_api_table()` and `LOCALIZATION_API_TABLE_SCHEMA` instead of copying `paradev.localization.__all__` or maintaining a second list of language helper exports. Regenerate [Localization API Reference](localization-api-reference.md) with CLI `localization-api --markdown` whenever public localization imports change.

HeavenBase facade audits should use `paradev.hb.get_hb_api_table()` and `HB_API_TABLE_SCHEMA` instead of copying `paradev.hb.__all__` or maintaining a second list of catalog helper exports. Regenerate [HeavenBase Facade API Reference](hb-api-reference.md) with CLI `hb-api --markdown` whenever public `paradev.hb` imports change.

CLI command table and adapter audits should prefer `paradev.surfaces.cli.get_cli_api_table()` and `CLI_API_TABLE_SCHEMA` instead of copying `get_cli_contract()` command names, command groups, SDK/helper adapters, projections, filters, or frontend operation reverse-index lists. Regenerate [CLI API Reference](cli-api-reference.md) with CLI `cli-api --markdown` whenever a CLI command or adapter mapping changes.

REST facade audits should prefer `paradev.api.get_rest_facade_api_table()` and `REST_FACADE_API_TABLE_SCHEMA` instead of copying `paradev.api.__all__` or maintaining separate local API server, OpenAPI seed, source text, project draft, module draft, or facade-helper import lists. Regenerate [REST Facade API Reference](rest-facade-api-reference.md) with CLI `rest-facade-api --markdown` whenever public `paradev.api` exports change.

MCP tool table and adapter audits should prefer `paradev.surfaces.mcp.get_mcp_api_table()` and `MCP_API_TABLE_SCHEMA` instead of copying `get_mcp_contract()` tool names, SDK methods, read/write flags, feature groups, or frontend operation reverse-index lists. Regenerate [MCP API Reference](mcp-api-reference.md) with CLI `mcp-api --markdown` whenever an MCP tool changes.

The REST/OpenAPI seed also exposes read-only Catalog recovery status through `GET /projects/catalog`; this bridge helper intentionally remains outside the generic frontend workspace-operation catalog.

Module create, rename, remove, and contained source-draft adapters must preserve the SDK's additive Catalog invalidation contract. Before changing project sources, the SDK durably marks any configured derived Catalog stale under the project Catalog lock. A successful source write then returns `paradev.hb.catalog-mutation.v1` as `catalog_mutation`: `not_configured` / `catalog.mutation.not_configured` when no Catalog exists, or `failed` / `catalog.mutation.failed` with an actionable Refresh message when the Catalog requires a coherent rebuild. `applied` / `catalog.mutation.applied` remains reserved for a future atomic path that updates every dependent entity; current module authoring must not emit it. Create nests the result in its scaffold plan; rename and completed remove return it at the top level. Validate the complete parent response and request identity first. If a validated source-success response omits or malforms the nested result, the desktop adapter must preserve that success as local `paradev.desktop.catalog-mutation-unverified.v1` / `unverified` / `catalog.mutation.unverified`, not reject it or invite a retry. Dry, blocked, and non-written responses must omit `catalog_mutation`. Treat refresh-required `failed` as source success plus stale derived state: do not retry the source operation, keep and latch the source-backed local view, and offer explicit Catalog Refresh. `catalog_status` maps the stale marker to existing `incomplete` / `catalog.incomplete` compatibility state, while Catalog query and completion calls fail closed until `catalog_refresh` completes a coherent rebuild and clears the marker. Canonical module mutations hold one project Catalog lock across invalidation and source mutation; initial write and full refresh use the same lock. Create, rename, and removal paths are lexical and descriptor-anchored with no-follow traversal. Scaffold files stage under `source_root/.paradev/module-transactions` before installation; forced replacements keep recoverable originals until the complete install succeeds, rollback ordinary failures, and return `scaffold.rollback_incomplete` with `recovery_path` instead of deleting the last backup when rollback itself fails. Removal atomically moves the canonical folder to same-source-root quarantine before best-effort cleanup; a remaining tombstone is a successful removal with typed `paradev.module.remove-cleanup.v1` warning state. These operations fail closed on hosts without the required primitives, which remains a cross-platform packaging blocker rather than permission to use a path-based fallback.

`FRONTEND_API_SELECTORS` is the SDK-owned selector vocabulary for frontend API lookup. `get_cli_contract()` lists Typer commands, their SDK adapters, command filters such as the `frontend-api` selector set and `templates` filter set, `architecture` projections such as `api-table`, `api-table-markdown`, `surface-contract`, `surface-contracts`, and `surface-contracts-markdown`, `frontend-api` projections such as `form`, `action`, `values-json`, `option-field`, `binding-surface`, `binding-key`, `rest-request`, `workspace`, `markdown`, `sdk-cli-markdown`, and `typescript`, `pdx-api`, `pdx-core-api`, `config-api`, `gui-api`, `desktop-api`, `games-api`, `templates-api`, `copy-roots-api`, `project-facade-api`, `localization-api`, `lsp-api`, `lsp-server-api`, `catalog-api`, `hb-api`, `rest-api`, `rest-facade-api`, and `mcp-api` projection `markdown`, the SDK-owned inspection contract from `get_project_inspection_contract()`, and `frontend_operation_ids` derived from `get_frontend_api_binding_index("cli")`. `get_mcp_contract()` lists MCP tools with read/write flags, tool filters, `frontend_api` selectors, `pdx_parse`, `pdx_format`, `project_create`, `project_open`, `project_view`, `project_browser`, `project_find`, `project_rename`, `module_rename`, `module_remove`, `module_file`, `module_edit`, `collection_create`, `collection_file`, `collection_edit`, `collection_rename`, `collection_remove`, the same inspection contract on `project_inspect`, and `frontend_operation_ids` derived from `get_frontend_api_binding_index("mcp")`. `get_openapi_seed()` exposes REST/OpenAPI paths for architecture, frontend API discovery with optional `operation_id`/`group_id` selectors and the `form=true` operation projection, frontend API workspace discovery through `GET /frontend-api/workspace`, frontend API selected-action detail through `GET /frontend-api/action`, frontend API option resolution through `POST /frontend-api/options`, frontend API input normalization through `POST /frontend-api/normalize`, frontend API REST request planning through `POST /frontend-api/rest-request`, frontend API binding reverse lookup through `GET /frontend-api/binding`, PDX parsing/formatting, LSP diagnostics/symbols/hover/formatting/completion/semantic tokens, project creation, project open/view, project registry listing, desktop project state, desktop build lifecycle through `POST /desktop/builds`, `GET /desktop/builds`, `GET /desktop/builds/status`, and `POST /desktop/builds/interrupt`, project browser, project discovery, title-only project rename, source-module rename/removal, collection descriptor create/rename/removal, module and collection text-file read/write, project authoring reads, scaffold plans/writes, project build plan/emit, catalog write/refresh through `POST`/`PUT /projects/catalog`, project inspection contracts, and project inspection payloads. REST operations derived from frontend rows carry `x-paradev-frontend-api-operation-ids`, which must stay generated from `bindings.rest` rather than maintained by hand; `tests/test_architecture.py::test_frontend_api_contract_indexes_every_surface_binding_and_openapi_annotation` guards both the binding index and OpenAPI annotation from drift.

Frontend API operation rows may include `inputs` when the frontend needs a stable form or action signature. Project, module, collection, build, catalog, PDX, LSP, and frontend API selector rows now publish those fields for create/find/open/view/list/templates/authoring/file/edit/rename/remove/activate, build plan/emit/inspection, catalog preview/write/refresh/query, saved-file parse/format, editor-buffer diagnostics/symbols/hover/formatting/completion/semantic tokens, operation/group/action lookup flows, `surface.frontend_api.action`, `surface.frontend_api.options`, `surface.frontend_api.normalize`, `surface.frontend_api.rest_request`, and `surface.frontend_api.binding_lookup`, so GUI and importer code should read that row metadata instead of duplicating CLI option lists, REST request bodies, or OpenAPI parameter names. Rows with SDK, CLI, REST, MCP, or LSP fields also publish derived `bindings`; generated clients should use `bindings.rest.method`, `bindings.rest.path`, and `bindings.rest.query` instead of parsing human-readable `rest` strings. Workspace action rows copy those bindings and add an `execution` object; extend action execution by fixing the canonical operation row or binding derivation, not by adding a GUI-only action registry. `execution.confirmation` is part of that action execution contract and is the only place GUI shells should read confirmation requirements. `get_frontend_api_action(...)` composes one selected action from the operation row, workspace action, form helper, option-source summary, and binding derivation; extend that helper when the selected-action detail payload needs new derived metadata. TypeScript GUI code should use `frontendApiWorkspaceActions`, `getFrontendApiAction(...)`, `getFrontendApiActionDetail(...)`, `getFrontendApiFormControls(...)`, `getFrontendApiFormControlKind(...)`, `getFrontendApiFormValuesWithDefaults(...)`, `getFrontendApiFormOptionRequests(...)`, `resolveFrontendApiFormOptionRequest(...)`, `resolveFrontendApiNormalizeRequest(...)`, `resolveFrontendApiRestPlanRequest(...)`, `getFrontendApiSectionActions(...)`, `getFrontendApiDefaultSectionAction(...)`, `getFrontendApiBindings(...)`, `getFrontendApiRestBinding(...)`, `frontendApiGroupIndex`, `frontendApiStatusIndex`, `frontendApiSurfaceIndex`, `getFrontendApiGroupOperationIds(...)`, `getFrontendApiStatusOperationIds(...)`, `getFrontendApiSurfaceOperationIds(...)`, `frontendApiInputOperations`, `getFrontendApiInputs(...)`, `getFrontendApiRequiredInputNames(...)`, `getFrontendApiDefaultValues(...)`, and `getFrontendApiOptionSourceInputs(...)` from `apps/desktop/src/data/frontendApi.ts` when it needs generated workspace action, selected-action summary, form defaults, form render state, option request planning/execution, normalize/rest-plan result state, binding, group/status/surface operation lists, or raw input rows. Pass `FrontendApiFormOptionResults` into `getFrontendApiFormControls(...)` after option requests resolve; the helper converts both static choices and `paradev.sdk.frontend-api.options.v1` payload rows into `FrontendApiFormControlOption` records for select controls. TypeScript clients that call frontend API meta endpoints should use `frontendApiEndpointPaths`, the `buildFrontendApi*Url(...)` helpers, JSON request helpers such as `buildFrontendApiOptionsRequest(...)`, `buildFrontendApiNormalizeRequest(...)`, and `buildFrontendApiRestPlanRequest(...)`, and the matching resolver helpers from the same file instead of hand-building `operation_id`, `field_name`, request headers, submitted-value bodies, or meta-result state. The same rows derive `index["binding"]`, the reverse lookup from surface call keys back to operation ids; extend it by adding or fixing row-level `bindings`, not by editing surface-specific maps by hand, and use `get_frontend_api_binding_lookup(...)` or `get_frontend_api_binding_operation_ids(...)` from Python instead of raw indexing. They also derive `index["group"]`, `index["status"]`, and `index["surface"]`; extend those projections by fixing canonical operation rows or row-level `bindings`, and consume them through named Python or TypeScript helpers instead of scanning rows. `get_frontend_api_form(...)` derives ordered fields, target buckets, required names, defaults, aliases, controls, option-source provider metadata, and a JSON Schema from those same `inputs`; option sources point to canonical provider operations such as `module.templates`, `build.families`, `module.list`, `collection.list`, `build.artifacts`, and `build.diagnostics`. `resolve_frontend_api_options(...)` executes those supported providers through `Project.templates(...)` or `Project.inspect(...)`, returns `paradev.sdk.frontend-api.options.v1`, and reports `available=false` with `missing_requirements` instead of raising when dependent form fields are absent. `getFrontendApiFormOptionRequests(...)` mirrors that dependency state in TypeScript and returns a request only when the submitted values plus SDK defaults satisfy the provider requirements; `resolveFrontendApiFormOptionRequest(...)` executes one available request and converts offline, non-OK, unavailable, and successful responses into explicit result state. `normalize_frontend_api_inputs(...)` applies defaults, validates unsupported or missing fields, and preserves frontend-safe aliases such as `artifact_path -> parameters.path` without overwriting project `path`; `plan_frontend_api_rest_request(...)` reuses the normalized buckets and `bindings.rest` to return the target method, path, query, body, and source binding. CLI `frontend-api --operation ... --action`, CLI `frontend-api --operation ... --option-field ... --values-json ...`, CLI `frontend-api --operation ... --values-json ...`, CLI `frontend-api --operation ... --values-json ... --rest-request`, CLI `frontend-api --binding-surface ... --binding-key ...`, REST `GET /frontend-api/action?operation_id=...`, REST `POST /frontend-api/options?operation_id=...&field_name=...`, REST `POST /frontend-api/normalize?operation_id=...`, REST `POST /frontend-api/rest-request?operation_id=...`, and REST `GET /frontend-api/binding?binding_surface=...&binding_key=...` must route to those helpers. TypeScript clients should import the typed helper from `apps/desktop/src/data/frontendApi.ts`; only the generator should rewrite `apps/desktop/src/generated/frontendApi.ts`. Do not hand-maintain a second frontend form schema, action detail composer, form-control adapter, action execution map, option-provider map, TypeScript contract, form-default map, option-request planner, option-request executor, option-to-control mapper, frontend API query-string builder, frontend API JSON request builder, frontend API meta-result mapper, REST request mapper, binding reverse lookup, grouped operation lists, or confirmation-policy mapper.

Desktop shells should derive sidebars and tabs from `frontendApiWorkspaceSections`; do not hardcode migration-specific navigation labels or a second workspace-section list. Selected-section action tables should use `getFrontendApiSectionActions(...)`, `getFrontendApiDefaultSectionAction(...)`, and `getFrontendApiRequiredInputNames(...)`; selected-action panels should use `getFrontendApiActionPanelState(...)` for action detail, fields, defaults, controls, option requests, normalize/rest-plan requests, confirmation state, Run state, and stable effect keys; selected-action execution-plan panels should use `resolveFrontendApiNormalizeRequest(...)` and `resolveFrontendApiRestPlanRequest(...)`; selected-action run controls should consume a ready plan through `buildFrontendApiRestExecutionRequest(...)` and `resolveFrontendApiRestExecutionRequest(...)` instead of owning REST URL/body/error shaping in component code, with sidebar and tab selection synchronized on the generated workspace-section id type.

Confirmation acceptance is helper-shaped state, not another policy surface. Use `FrontendApiActionConfirmationStates` for the operation-keyed acceptance map, call `isFrontendApiActionConfirmationSatisfied(...)` before enabling Run, and reset the accepted value when submitted form values change.

Run state is also helper-shaped. Use `getFrontendApiActionRunState(...)` with the selected operation id, `execution.confirmation`, the REST-plan result, the REST-execution result, and confirmation states so components do not duplicate disabled, loading, confirmation, or result-detail logic.

Selected-action panel state is the preferred higher-level helper. Use `getFrontendApiActionPanelState(...)` when a component needs the common selected-action view model, and keep direct calls to individual form/default/request helpers for intentionally narrow panels.

When changing the TypeScript frontend API helper, run `rtk npm --prefix apps/desktop run test:unit` for direct panel-state, request/resolver, and bridge-unavailable helper coverage before the broader desktop build.

GUI, MCP, REST, LSP, and importer agents should extend those helpers when adding a surface capability, then route the actual behavior through `get_frontend_api_contract()`, `get_frontend_api_action(...)`, `resolve_frontend_api_options(...)`, `normalize_frontend_api_inputs(...)`, `plan_frontend_api_rest_request(...)`, `Project.create(...)`, `create_project(...)`, `project_create_payload(...)`, `Project.load(...)`, `Project.to_view()`, `Project.find(...)`, `registered_projects(...)`, `desktop_state(...)`, `Project.browser(...)`, `Project.rename(...)`, `Project.rename_module(...)`, `Project.remove_module(...)`, `Project.read_module_file(...)`, `Project.write_module_file(...)`, `Project.create_collection(...)`, `Project.read_collection_file(...)`, `Project.write_collection_file(...)`, `Project.rename_collection(...)`, `Project.remove_collection(...)`, `Project.templates()`, `Project.authoring_path(...)`, `Project.authoring_plan(...)`, `Project.scaffold_module(...)`, `Project.build(...)`, `Project.inspect(...)`, `Project.inspections()`, `get_project_inspection_contract()`, `paradev.hb.catalog_write(...)`, `paradev.hb.catalog_refresh(...)`, `parse_pdx_file(...)`, `format_pdx_file(...)`, `format_pdx_text(...)`, `diagnose_pdx_lsp_text(...)`, `document_symbols_pdx_lsp_text(...)`, `hover_pdx_lsp_text(...)`, `format_pdx_lsp_text(...)`, or another SDK method.

The current frontend API discovery/action-detail/option-resolution/normalization/rest-request planning, project create, project open/view, project list/state/browser, project find, project rename, module rename, module remove, module text-file, collection create, collection rename, collection remove, collection text-file/source inventory, PDX parse/format, LSP diagnostics/symbols/hover/formatting/completion/semantic tokens, authoring, scaffold, build plan/emit, and catalog write/refresh contracts are explicit across surfaces: CLI `frontend-api`/`frontend-api --action`/`frontend-api --option-field`/`frontend-api --binding-surface --binding-key`/`new`/`project`/`projects`/`desktop-state`/`project-browser`/`project-find`/`project-rename`/`module-rename`/`module-remove`/`module-file`/`module-edit`/`collection-create`/`collection-rename`/`collection-remove`/`collection-file`/`collection-edit`/`sources --owner-kind collection`/`parse`/`format`/`templates`/`authoring-path`/`authoring-plan`/`scaffold`/`build`/`hb catalog-write`/`hb catalog-refresh`, REST `/frontend-api`/`/frontend-api/action`/`/frontend-api/options`/`/frontend-api/normalize`/`/frontend-api/rest-request`/`/frontend-api/binding`/`/projects`/`/projects/list`/`/desktop/state`/`/desktop/builds`/`/desktop/builds/status`/`/desktop/builds/interrupt`/`/projects/browser`/`/projects/find`/`/projects/rename`/`/projects/modules/rename`/`/projects/modules/remove`/`/projects/modules/file`/`/projects/collections`/`/projects/collections/rename`/`/projects/collections/file`/`/projects/inspect?kind=sources`/`/pdx/parse`/`/pdx/format`/`/lsp/diagnostics`/`/lsp/symbols`/`/lsp/hover`/`/lsp/formatting`/`/lsp/completion`/`/lsp/semantic-tokens`/`/projects/templates`/`/projects/authoring-path`/`/projects/authoring-plan`/`/projects/scaffold`/`/projects/build`/`/projects/catalog`, LSP `textDocument/publishDiagnostics`/`textDocument/documentSymbol`/`textDocument/hover`/`textDocument/formatting`/`textDocument/completion`/`textDocument/semanticTokens/full`, and MCP `frontend_api`/`project_create`/`project_open`/`project_view`/`project_browser`/`project_find`/`project_rename`/`module_rename`/`module_remove`/`module_file`/`module_edit`/`collection_create`/`collection_rename`/`collection_remove`/`collection_file`/`collection_edit`/`project_inspect`/`pdx_parse`/`pdx_format`/`project_templates`/`project_authoring_path`/`project_authoring_plan`/`project_scaffold` all map to the same SDK calls.

Frontend API rows backed by `Project.inspect(...)` should always list all three pieces: REST `GET /projects/inspect?kind=...`, MCP `project_inspect`, and the concrete payload schema returned by that inspection kind. This applies to module and collection read panels, collection descriptor source inventory, read-only build panels, and read-only catalog preview/query panels. The generic `project.inspect` row may keep the broader `Project inspection payload` label because its schema depends on `kind`, and its inputs should stay limited to dispatcher-level `path` and `kind`; put detailed filters on the concrete inspection rows.

Family compilers and adapters should consume authored PDX through `load_pdx_sources(...)` or `parse_pdx_file(..., include_dump=True)`, not direct surface-owned `PDXBlock.from_file(...)` calls. That keeps CLI, SDK, REST, GUI, MCP, and build diagnostics on one parser payload while still giving compilers a lossless `PDXBlock`.

## Add A Project-Local Family

Prefer a trusted project-local Python file for each new authored entity family. Keep the
manifest entry small and point it at the family file:

```yaml
python_modules:
  - tools/families/superevent.py
  - tools/families/news_event.py
```

Use one Python file per entity when the family is compact:

```python
from __future__ import annotations

from paradev.build import BuildRegistry, SimpleSourceFamily, Slot


def register(registry: BuildRegistry) -> BuildRegistry:
    registry.add(
        SimpleSourceFamily(
            family="superevent",
            metadata_keys=("scope",),
            pdx_path_template="events/superevents/{object_id}.txt",
            loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
            source_slots=(
                Slot("script", "script.pdx", required=True, kind="pdx"),
                Slot("loc", "*.loc", many=True, kind="loc"),
            ),
        )
    )
    return registry
```

Use a collection family when sibling modules must compile into one shared file:

```python
from __future__ import annotations

from paradev.build import BuildRegistry, CollectionSourceFamily, Slot


def register(registry: BuildRegistry) -> BuildRegistry:
    registry.add(
        CollectionSourceFamily(
            family="news_event",
            pdx_path_template="events/{collection_id}.txt",
            loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
            source_slots=(Slot("body", "body.pdx", required=True, kind="pdx"),),
            collection_source_slots=(
                Slot("header", "header.pdx", required=True, kind="pdx"),
                Slot("strings", "strings.loc", kind="loc"),
            ),
        )
    )
    return registry
```

Larger entities can use a designated folder such as `tools/families/superevent/family.py`;
list that `family.py` path in `python_modules`. The executable examples live under
`docs/examples/families/` and are covered by `tests/test_python_family_examples.py`.

After loading the project, `Project.families()["authoring"]` exposes the SDK-owned source roots plus the canonical `modules/{family}/{object_id}` and `collections/{family}/{collection_id}` folder templates. Family rows expose `metadata.keys`, `metadata.common_keys`, `metadata.family_keys`, `metadata.settings`, and `metadata.unknown_key_policy`, so clients can render `meta.yaml` forms and explain loose/strict diagnostics without duplicating loader allowlists. They also expose `outputs`, derived from the same templates used by the emit stage, so clients can read `artifact_type`, `template_key`, `template`, `owner_kinds`, `target_root`, and route or sprite-slot context without parsing template names. The sibling `index` maps family ids, compiler kinds, source slots, collection descriptor slots, sprite slots, routes, output artifact types, and artifact writer types to returned row numbers; `output_artifact_type` indexes family rows, while `artifact_type` indexes writer rows. Importers, GUI clients, MCP tools, and project-local family helpers should read that payload instead of duplicating discovery or output rules. `Project.templates()` complements it with starter-file templates; each template row includes `authoring_ready`, and rows targeting an unregistered family include `diagnostic_codes: ["template.unknown_family"]`. Its `index` maps `id`, `family`, `source`, `authoring_ready`, and `diagnostic_code` to row numbers. Use exact `Project.templates(...)` filters for those same fields when a surface needs only one template subset; returned index row numbers are local to the filtered payload. Adapters should use those fields to select templates and disable unavailable scaffold actions before calling `Project.scaffold_module(...)`. When a tool needs one family contract, use exact `Project.families(...)` filters such as `family`, `kind`, `source_slot`, `collection_source_slot`, `sprite_slot`, `route`, or `artifact_type`. Adapters that already hold a `BuildRegistry` and explicit project context can call the reusable build-layer wrapper `paradev.build.families_view(...)`. Use `Project.authoring_path("module", family, object_id)` or `Project.authoring_path("collection", family, collection_id)` when a tool needs one concrete root. Use `Project.authoring_plan(...)` when the tool also needs expected source-slot rows plus current `empty`/`missing`/`satisfied`/`diagnostic` status before files exist or before running a build. Lower-level adapters with explicit project roots can reuse `paradev.build.authoring_path_view(...)`, `authoring_plan_view(...)`, and `authoring_view(...)`.

For adapter code that receives an inspection kind from a command, UI action, MCP tool, or REST route, call `Project.inspect(kind, **filters)` instead of maintaining a separate dispatch table. Use `get_project_inspection_contract()` for static adapter registration before a project is loaded, and use `Project.inspections()` when the same contract should include the loaded project id. Supported kinds include `inspections`, `summary`, `manifests`, `modules`, `collections`, `artifacts`, `localization`, `source-slots`, `sources`, `assets`, `sprites`, `diagnostics`, `source-map`, `dependencies`, `build-graph`, `build-explain`, `catalog-preview`, `catalog-query`, and `families`. Specific methods such as `Project.modules(...)` remain fine for direct Python code where the target is known. If compiler tests, MCP internals, or another adapter already hold a `BuildResult`, call the reusable build-layer view helpers such as `paradev.build.summary_view(...)`, `manifests_view(...)`, `modules_view(...)`, `artifacts_view(...)`, `sources_view(...)`, `assets_view(...)`, `sprites_view(...)`, `diagnostics_view(...)`, `source_map_view(...)`, and `dependencies_view(...)` instead of copying SDK filters. Use `Project.source_slots(...)` when a surface needs the expected-versus-found slot matrix for modules or collection descriptors; exact slot rows include suggested paths for missing-file UI, and the reusable build-layer helper is `paradev.build.source_slot_status(...)`. Use `Project.sources(...)` when a surface needs the actual compiler inputs before artifact traceability, pass `owner_kind="collection"` for descriptor-owned collection inputs instead of joining rows by hand, and use `Project.assets(...)` / `Project.sprites(...)` for build panels that need static copy rows or sprite declarations without writing files.

Metadata validation mode is SDK-owned. Unknown module or collection metadata keys are loose-mode warnings by package default, and omitted SDK/CLI/REST/frontend calls inherit `paradev.build.strict_metadata` from `CM_PARADEV`. `strict_metadata=True` promotes those same `metadata.unknown_key` diagnostics to errors through `load_metadata(...)`, discovery, `Project.build(...)`, `Project.diagnostics(...)`, CLI `build --strict-metadata`, REST `POST /projects/build?strict_metadata=true`, and frontend rows `build.plan`, `build.emit`, and `build.diagnostics`; explicit `False` or `--no-strict-metadata` keeps loose mode. New compilers should declare accepted metadata keys in the build registry; the resulting `Project.families()` metadata contract publishes SDK common keys, family keys, and the unknown-key policy, so surfaces should rely on this shared path instead of adding surface-specific unknown-key checks.

Keep source indexing centralized. The HeavenBase `source-file` catalog entity is derived from `sources.json`, so new source loaders should add loader-specific summaries to the source inventory instead of introducing a second catalog path. Catalog tags are additive: source rows keep the simple module/family/slot tags and also expose prefixed tags such as `module:<id>`, `collection:<id>`, `family:<family>`, `slot:<slot>`, `loader:<loader>`, and `status:<status>`.

Declarative `families` entries remain useful for tiny generated manifests where slots and templates are enough, but the normal guide for hand-authored families is Python. The Python path keeps slots, metadata keys, compiler kind, and custom normalizers/checkers in one reviewable file per entity.

Project-owned artifacts should still go through the build registry. The HOI4 profile uses a `mod_descriptor` family plus `ModDescriptorWriter` to emit `descriptor.mod` and the launcher preview from `BuildContext.metadata`; do not add surface-specific file writes in the CLI, GUI, or MCP layer.

## Tests And Gates

Use TDD for behavior changes. Run focused tests first, then repo wrappers:

```bash
rtk uv run pytest tests/test_project_build.py
rtk uv run python .claude/skills/heaven-style/scripts/scan.py src tests
rtk bash scripts/flake.bash --ci
rtk bash scripts/test.bash
rtk uv build
```

Update docs when public behavior changes. For manual changes, verify:

```bash
rtk rg -n "paradev|Project.load|PIHC3|diagnostics|build" docs/user-manual README.en.md docs/workflows/build-flow.md
```

## 中文

本页面面向扩展 ParaDev 的开发者，不是普通 Mod 作者的日常教程。

## 架构边界

HoI4 逻辑应该放在 Python SDK 和 game package 中：

```text
src/paradev/sdk/        公开 Python API
src/paradev/project/    项目发现和 manifest 加载
src/paradev/pdx/        tokenizer、AST、formatter、diagnostics
src/paradev/build/      modules、collections、artifacts、manifests
src/paradev/games/hoi4/ HoI4 profile 和内置 families
src/paradev/hb/         HeavenBase catalog 集成
src/paradev/surfaces/   CLI、MCP、REST、LSP、VS Code 适配器
```

所有 surface 调用 SDK，不拥有领域逻辑。

SDK facade 审计应优先使用 `paradev.sdk.get_sdk_api_table()` 和 `SDK_API_TABLE_SCHEMA`，不要复制 `paradev.sdk.__all__` 或另行维护公开 import 清单。公开 SDK export 变化时，用 CLI `sdk-api --markdown` 重新生成 [SDK API Reference](sdk-api-reference.md)。

Project object 审计应优先使用 `paradev.sdk.get_project_api_table()` 和 `PROJECT_API_TABLE_SCHEMA`，不要复制 `Project` dataclass 字段、方法、CLI adapter、frontend operation id 或 inspection-kind 映射。公开 `Project` surface 变化时，用 CLI `project-api --markdown` 重新生成 [Project API Reference](project-api-reference.md)。

Build facade 审计应优先使用 `paradev.build.get_build_api_table()` 和 `BUILD_API_TABLE_SCHEMA`，不要复制 `paradev.build.__all__` 或另行维护 compiler record、family、slot、loader、writer、manifest、view、graph 或 planning import 清单。公开 build export 变化时，用 CLI `build-api --markdown` 重新生成 [Build API Reference](build-api-reference.md)。

PDX core facade 审计应优先使用 `paradev.pdx.get_pdx_core_api_table()` 和 `PDX_CORE_API_TABLE_SCHEMA`，不要复制 `paradev.pdx.__all__`，也不要另行维护 tokenizer、AST、parser、diagnostics、scalar constant 或 facade helper import 清单。公开 `paradev.pdx` export 变化时，用 CLI `pdx-core-api --markdown` 重新生成 [PDX Core API Reference](pdx-core-api-reference.md)。

LSP server facade 审计应优先使用 `paradev.lsp.get_lsp_server_api_table()` 和 `LSP_SERVER_API_TABLE_SCHEMA`，不要复制 `paradev.lsp.__all__`，也不要另行维护 document、JSON-RPC dispatcher、stdio framing、stdio server 或 facade helper import 清单。公开 `paradev.lsp` export 变化时，用 CLI `lsp-server-api --markdown` 重新生成 [LSP Server API Reference](lsp-server-api-reference.md)。

architecture graph helper 用来描述跨 surface contract，不需要导入 adapter module。architecture table code 需要固定 SDK anchor 时，使用 `ARCHITECTURE_API_TABLE_ROWS` 和 `ARCHITECTURE_API_TABLE_SCHEMA`；审计需要 SDK/CLI/REST/MCP 入口行时，使用 `paradev.sdk.get_architecture_api_table()`；用 `paradev.sdk.render_architecture_api_reference_markdown()` 或 CLI `architecture --api-table-markdown` 重新生成 [Architecture API Reference](architecture-api-reference.md)。

surface contract helper 用来描述当前 adapter 边界，不需要启动外部服务。table code 需要固定 SDK anchor 时，使用 `SURFACE_CONTRACT_IDS`、`SURFACE_CONTRACT_INDEX_CATALOG` 和 `SURFACE_CONTRACT_SUMMARY_SCHEMA`；审计或工具需要按稳定 surface identifier 读取 bundle、CLI、LSP、MCP、OpenAPI 和 VS Code contract payload 时，使用 `paradev.surfaces.get_surface_contracts()`；需要可变有序 id list 时，使用 `paradev.surfaces.get_surface_contract_ids()`；需要 documented summary index dimensions 时，使用 `paradev.surfaces.get_surface_contract_index_catalog()`；API table 或 dashboard 需要 typed `SurfaceContractSummary` / `SurfaceContractSummaryRow` row-count metadata 和 status index 时，使用 `paradev.surfaces.get_surface_contract_summary()`；需要某个 contract status 对应的有序 surface id 时，使用 `paradev.surfaces.get_surface_contract_status_ids(status)`；只需要一个 compact table row 时，使用 `paradev.surfaces.get_surface_contract_summary_row(identifier)`；代码只需要一个精确 payload 时，使用 `paradev.surfaces.get_surface_contract(identifier)`。用 `paradev.surfaces.render_surface_contract_reference_markdown()` 或 CLI `architecture --surface-contracts-markdown` 重新生成 [Surface Contract Reference](surface-contract-reference.md)。`get_frontend_api_contract()` 是 GUI、导入器、桌面端、REST、MCP、VS Code 和 LSP 面向工作的持续维护操作清单；它按 project、module、collection、build、PDX、LSP、catalog 和 surface 分组，并把尚未稳定的缺口标记为 `planned`，而不是隐式假设。

Surface facade 审计应优先使用 `paradev.surfaces.get_surfaces_api_table()` 和 `SURFACES_API_TABLE_SCHEMA`，不要复制 `paradev.surfaces.__all__` 或另行维护 adapter import 清单。CLI、REST、MCP、LSP、VS Code、bundle、API catalog 或 surface contract facade export 变化时，用 CLI `surfaces-api --markdown` 重新生成 [Surfaces API Reference](surfaces-api-reference.md)。

browser-backed source editing 也属于这份 canonical list。`project.source_text` 对应 `GET /projects/{project_id}/sources`，`module.draft` 对应 `POST /projects/{project_id}/modules/{family_id}/drafts`，`project.draft_apply` 对应 `POST /projects/{project_id}/drafts/apply`；`plan_frontend_api_rest_request(...)` 会先用 normalized input values 填充 `{project_id}` 和 `{family_id}`，再返回可执行的 REST plan。

adapter 代码已经知道稳定 operation id 或 group id，并且只需要一行或一个分组切片时，使用 `get_frontend_api_operation(operation_id)` 和 `get_frontend_api_group(group_id)`。GUI 或导入器代码需要 SDK-owned navigation sections 和 `paradev.sdk.frontend-api.action.v1` action rows 时，使用 `get_frontend_api_workspace()`；action row 会带有派生的 `execution.default_surface`、`execution.available_surfaces`、`execution.confirmation`、可调用 `bindings`、`form_schema`、`normalizer_schema` 和 `rest_request_schema` 提示。adapter 需要一个已选 action detail 时，使用 `get_frontend_api_action(operation_id)`；它会组合 canonical operation row、workspace action、section membership、派生 form、option-source field list、bindings 和 execution hints。adapter 需要某个 operation 的派生 UI/action schema 时，使用 `get_frontend_api_form(operation_id)`；它包含字段文案、校验、alias、JSON Schema，以及用于动态选项的 `paradev.sdk.frontend-api.option-source.v1` provider 提示。adapter 需要执行这些 option source、但不想复制 provider dispatch 时，使用 `resolve_frontend_api_options(operation_id, field_name, values)`。Python adapter 需要把提交的表单状态拆成 project、parameter、selector 和 projection buckets 时，使用 `normalize_frontend_api_inputs(operation_id, values)`；adapter 需要同一份提交状态对应的 REST method、path、query 和 JSON body 时，使用 `plan_frontend_api_rest_request(operation_id, values)`；adapter 需要把 surface call key 或整个 adapter surface 反查为稳定 operation id 时，使用 `get_frontend_api_binding_lookup(...)`、`get_frontend_api_binding_operation_ids(...)`、`get_frontend_api_binding_index(...)`、`build_frontend_api_rest_index_key(...)` 或 `get_frontend_api_rest_operation_ids(...)`。需要重新生成 `apps/desktop/src/generated/frontendApi.ts` 时，使用 `render_frontend_api_typescript()` 或 CLI `frontend-api --typescript`；桌面代码再从 `apps/desktop/src/data/frontendApi.ts` 读取生成的 `frontendApiSummary`、workspace action rows、`getFrontendApiActionDetail(...)` 已选 action summary、`getFrontendApiFormValuesWithDefaults(...)` 表单默认值、`getFrontendApiFormControls(...)` 表单渲染状态、`getFrontendApiFormOptionRequests(...)` 动态选项请求计划、`resolveFrontendApiFormOptionRequest(...)` 动态选项请求执行、`resolveFrontendApiNormalizeRequest(...)` 与 `resolveFrontendApiRestPlanRequest(...)` normalization/REST-plan 结果状态、binding helpers、`frontendApiBindingIndex`、`getFrontendApiBindingOperationIds(...)`、`buildFrontendApiRestIndexKey(...)`、`getFrontendApiRestOperationIds(...)` 这些 binding-index helpers、`frontendApiSurfaceIndex` 与 `getFrontendApiSurfaceOperationIds(...)` 这些 surface-index helpers、input/default/option-source helpers、endpoint/request/payload helpers 和 lookup helpers，包括用于 frontend API JSON POST meta endpoints 的 `buildFrontendApiOptionsRequest(...)`、`buildFrontendApiNormalizeRequest(...)` 和 `buildFrontendApiRestPlanRequest(...)`，以及用于 binding lookup GET endpoint 的 `buildFrontendApiBindingLookupUrl(...)`。它们只是同一份 operation list 的只读 SDK view，因此新增前端可见能力时仍然应先在 `get_frontend_api_contract()` 添加唯一的 canonical 行。不要在 TypeScript 里重新计算 summary 计数，包括 surface coverage；`frontendApiSummary` 应直接指向 `PARADEV_FRONTEND_API_CONTRACT.summary`。client 需要列出某个 surface 支持的全部 operation id 时，使用 `contract["index"]["surface"]` 或 `getFrontendApiSurfaceOperationIds(...)`。完整手册表格应通过 `render_frontend_api_reference_markdown()` 或 CLI `frontend-api --markdown` 重新生成；紧凑 SDK/CLI 表格应通过 `render_frontend_api_sdk_cli_markdown()` 或 CLI `frontend-api --sdk-cli-markdown` 重新生成；测试会让 [Frontend API Reference](frontend-api-reference.md) 和 [SDK 与 CLI API Reference](sdk-cli-reference.md) 与这些 renderer 保持逐字节一致。

group/status API table 或审计需要 operation-id list 时，应使用 Python `get_frontend_api_group_operation_ids(...)` / `get_frontend_api_status_operation_ids(...)`，或 TypeScript `frontendApiGroupIndex` / `frontendApiStatusIndex` / `getFrontendApiGroupOperationIds(...)` / `getFrontendApiStatusOperationIds(...)`，不要直接读取 raw index 或过滤 rows。

read/write mode API table 或审计需要 operation-id list 时，应使用 Python `get_frontend_api_mode_operation_ids(...)`，或 TypeScript `frontendApiModeIndex` / `getFrontendApiModeOperationIds(...)`，不要按 `mutates` 过滤 operation rows。

payload renderer registry 需要列出返回同一 payload schema 的全部 operation id 时，应使用 `contract["index"]["payload"]` 或 TypeScript `frontendApiPayloadIndex` / `getFrontendApiPayloadOperationIds(...)`。未声明 payload 的行归入 `untyped`。

workspace navigation 和按 section 的 API table 需要列出某个 SDK-owned workspace section 中的全部 operation id 时，应使用 `contract["index"]["workspace_section"]` 或 TypeScript `frontendApiWorkspaceSectionIndex` / `getFrontendApiWorkspaceSectionOperationIds(...)`。

Python adapter 应优先使用 `get_frontend_api_group_operation_ids(...)`、`get_frontend_api_status_operation_ids(...)`、`get_frontend_api_binding_index(...)`、`get_frontend_api_surface_operation_ids(...)`、`get_frontend_api_payload_operation_ids(...)` 和 `get_frontend_api_workspace_section_operation_ids(...)` 获取这些分组 operation list，而不是直接访问 raw `contract["index"]`。

Project inspection API table 和 adapter preflight UI 应优先使用 `get_project_inspection_kinds()`、`get_project_inspection_row(kind)`、`get_project_inspection_index_catalog()` 和 `get_project_inspection_filter_kinds(filter_name)`，不要直接访问 raw `get_project_inspection_contract()["index"]`。`Project.inspect(...)` kind 或 filter 变化时，用 CLI `inspections --markdown` 重新生成 [Project Inspection Reference](project-inspection-reference.md)。

Authoring template module 审计应优先使用 `paradev.sdk.templates.get_templates_api_table()` 和 `TEMPLATES_API_TABLE_SCHEMA`，不要手工复制 template schema constant、dataclass、registry helper 或 scaffold planning function。`TemplateArg`、`ModuleTemplate`、`template_index(...)`、`module_scaffold_plan(...)` 等 SDK authoring-template helper 变化时，用 CLI `templates-api --markdown` 重新生成 [Authoring Templates API Reference](templates-api-reference.md)。

Copy-root module 审计应优先使用 `paradev.sdk.copy_roots.get_copy_roots_api_table()` 和 `COPY_ROOTS_API_TABLE_SCHEMA`，不要手工复制 target-root constant、manifest parser signature、复制 artifact 生成或 merge/shadow diagnostic 行为。`ARTIFACT_TARGET_ROOTS`、`CopyRootSpec`、`project_copy_roots(...)`、`copy_root_artifacts(...)` 或 `merge_copy_root_artifacts(...)` 变化时，用 CLI `copy-roots-api --markdown` 重新生成 [Copy Roots API Reference](copy-roots-api-reference.md)。

整体 API reference 审计应优先使用 `paradev.surfaces.get_api_catalog_table()` 和 `API_CATALOG_SCHEMA`，不要手工复制 reference 清单。需要按模块所有权审计时使用 `owner_module_index`，需要按 SDK/CLI/REST/MCP/LSP/frontend/docs 覆盖面审计时使用 `surface_index`，不要手工过滤 rows。新增、删除、重命名 API reference table 或 generated contract，或移动到不同文档页面时，用 CLI `api-catalog --markdown` 重新生成 [API Catalog Reference](api-catalog-reference.md)。

根 package facade 审计应优先使用 `paradev.get_package_api_table()` 和 `PACKAGE_API_TABLE_SCHEMA`，不要手工复制 `paradev.__all__`。`Project`、`CM_PARADEV`、`__version__` 或 package API table helper 等 package-level import 变化时，用 CLI `package-api --markdown` 重新生成 [Package API Reference](package-api-reference.md)。

Config facade 审计应优先使用 `paradev.config.get_config_api_table()` 和 `CONFIG_API_TABLE_SCHEMA`，不要复制 `paradev.config.__all__`，也不要维护第二份 config default 和 manager export 清单。`DEFAULT_CONFIG`、`BOOTSTRAP_CONFIG`、`CM_PARADEV` 或 config API table helper 等公开 config import 变化时，用 CLI `config-api --markdown` 重新生成 [Config API Reference](config-api-reference.md)。

GUI launcher facade 审计应优先使用 `paradev.gui.get_gui_api_table()` 和 `GUI_API_TABLE_SCHEMA`，不要复制 `paradev.gui.__all__`，也不要维护第二份 `paradev-gui` launcher export 清单。`build_parser`、`main` 或 GUI API table helper 等公开 GUI launcher import 变化时，用 CLI `gui-api --markdown` 重新生成 [GUI API Reference](gui-api-reference.md)。

Desktop facade 审计应优先使用 `paradev.desktop.get_desktop_api_table()` 和 `DESKTOP_API_TABLE_SCHEMA`，不要复制 `paradev.desktop.__all__`，也不要在 GUI client 里维护第二份 desktop state helper 清单。`DESKTOP_STATE_SCHEMA`、`desktop_state` 或 desktop API table helper 等公开 desktop import 变化时，用 CLI `desktop-api --markdown` 重新生成 [Desktop API Reference](desktop-api-reference.md)。

Games facade 审计应优先使用 `paradev.games.get_games_api_table()` 和 `GAMES_API_TABLE_SCHEMA`，不要复制 `paradev.games.__all__`，也不要维护第二份 game profile registry helper 清单。`PROFILE_REGISTRIES`、`registry_for_profile` 或 games API table helper 等公开 games import 变化时，用 CLI `games-api --markdown` 重新生成 [Games API Reference](games-api-reference.md)。

Project package facade 审计应优先使用 `paradev.project.get_project_facade_api_table()` 和 `PROJECT_FACADE_API_TABLE_SCHEMA`，不要手工复制 `paradev.project.__all__`。兼容性 project package import 或 facade helper 变化时，用 CLI `project-facade-api --markdown` 重新生成 [Project Facade API Reference](project-facade-api-reference.md)。

HeavenBase facade 审计应优先使用 `paradev.hb.get_hb_api_table()` 和 `HB_API_TABLE_SCHEMA`，不要手工复制 `paradev.hb.__all__`，也不要维护第二份 catalog helper export 清单。`paradev.hb` 公开 import 变化时，用 CLI `hb-api --markdown` 重新生成 [HeavenBase Facade API Reference](hb-api-reference.md)。

CLI command table 和 adapter 审计应优先使用 `paradev.surfaces.cli.get_cli_api_table()` 和 `CLI_API_TABLE_SCHEMA`，不要复制 `get_cli_contract()` 的 command name、command group、SDK/helper adapter、projection、filter 或 frontend operation reverse-index 清单。CLI command 或 adapter mapping 变化时，用 CLI `cli-api --markdown` 重新生成 [CLI API Reference](cli-api-reference.md)。

HeavenBase catalog API table 和 adapter 审计应优先使用 `paradev.hb.get_catalog_api_table()`、`CATALOG_API_TABLE_ROWS` 和 `CATALOG_API_TABLE_SCHEMA`，不要复制 catalog preview/status/write/refresh/query/completion 的 SDK、CLI、REST 或 MCP 入口清单。catalog surface 变化时，用 CLI `catalog-api --markdown` 重新生成 [Catalog API Reference](catalog-api-reference.md)。`GET /projects/catalog` 提供只读 Catalog 恢复状态；这个 bridge helper 有意不加入通用 frontend workspace operation catalog。

Module create、rename、remove 和 contained source draft adapter 必须保留 SDK 的 Catalog 失效 contract。修改项目源文件前，SDK 会在项目 Catalog lock 内持久标记已有的派生 Catalog 为 stale。源文件写入成功后，通过 `catalog_mutation` 返回 `paradev.hb.catalog-mutation.v1`：不存在 Catalog 时为 `not_configured` / `catalog.mutation.not_configured`；需要完整重建时为带可操作 Refresh 提示的 `failed` / `catalog.mutation.failed`。`applied` / `catalog.mutation.applied` 仅保留给未来能原子更新全部依赖实体的路径；当前 module authoring 不得返回它。Create 把结果放在 scaffold plan 内；rename 和完成的 remove 放在顶层。Adapter 必须先验证完整父 payload 和 request identity；如果已验证的源文件成功响应缺少或损坏嵌套结果，桌面端必须保留这次成功，并转换为本地 `paradev.desktop.catalog-mutation-unverified.v1` / `unverified` / `catalog.mutation.unverified`，不能拒绝响应或提示重试。Dry、blocked 和未写入响应必须省略 `catalog_mutation`。Refresh-required `failed` 表示源文件已成功但派生状态过期：不要重试源文件操作，应保留并 latch source-backed 本地视图，同时提供明确的 Catalog Refresh。`catalog_status` 把 stale marker 映射为兼容的 `incomplete` / `catalog.incomplete`；Catalog query 和 completion 在 `catalog_refresh` 完成一致重建并清除 marker 前都必须 fail closed。Canonical module mutation 会在 Catalog 失效和源文件修改的整个过程中持有同一个项目 lock；首次 write 和 full refresh 也使用该 lock。Create、rename、remove 都使用 lexical、descriptor-anchored、no-follow 路径。Remove 先把 canonical 目录原子移动到同一 source root 的 quarantine，最后 best-effort 清理；残留 tombstone 仍是成功 remove，并以 typed `paradev.module.remove-cleanup.v1` warning 返回。缺少所需 primitive 的平台会 fail closed；这是跨平台打包 blocker，不能改用 path-based fallback 绕过。

REST/OpenAPI route table 和 GUI route 审计应优先使用 `paradev.surfaces.rest.get_rest_api_table()` 和 `REST_API_TABLE_SCHEMA`，不要复制 `get_openapi_seed()` 的 path/method、parameter、request body、response 或 frontend operation reverse-index 清单。REST route 变化时，用 CLI `rest-api --markdown` 重新生成 [REST API Reference](rest-api-reference.md)。

REST facade 审计应优先使用 `paradev.api.get_rest_facade_api_table()` 和 `REST_FACADE_API_TABLE_SCHEMA`，不要复制 `paradev.api.__all__`，也不要另行维护 local API server、OpenAPI seed、source text、project draft、module draft 或 facade helper import 清单。公开 `paradev.api` export 变化时，用 CLI `rest-facade-api --markdown` 重新生成 [REST Facade API Reference](rest-facade-api-reference.md)。

MCP tool table 和 adapter 审计应优先使用 `paradev.surfaces.mcp.get_mcp_api_table()` 和 `MCP_API_TABLE_SCHEMA`，不要复制 `get_mcp_contract()` 的 tool name、SDK method、读写标记、feature group 或 frontend operation reverse-index 清单。MCP tool 变化时，用 CLI `mcp-api --markdown` 重新生成 [MCP API Reference](mcp-api-reference.md)。

`FRONTEND_API_SELECTORS` 是 SDK 拥有的 frontend API lookup selector 词表。`get_cli_contract()` 列出 Typer 命令、SDK adapter、`frontend-api` selector set 和 `templates` 这样的命令过滤字段、`api-table`、`api-table-markdown`、`surface-contract`、`surface-contracts`、`surface-contracts-markdown` 这样的 `architecture` projection、`form`、`action`、`values-json`、`option-field`、`binding-surface`、`binding-key`、`rest-request`、`workspace`、`markdown`、`sdk-cli-markdown` 与 `typescript` 这样的 `frontend-api` projection、`pdx-api`、`pdx-core-api`、`config-api`、`gui-api`、`desktop-api`、`games-api`、`templates-api`、`copy-roots-api`、`project-facade-api`、`localization-api`、`lsp-api`、`lsp-server-api`、`catalog-api`、`hb-api`、`rest-api`、`rest-facade-api` 和 `mcp-api` 的 `markdown` projection、来自 `get_project_inspection_contract()` 的 SDK inspection contract，以及从 `get_frontend_api_binding_index("cli")` 派生的 `frontend_operation_ids`。`get_mcp_contract()` 列出 MCP tools、read/write 标记、tool filters、`frontend_api` selectors、`pdx_parse`、`pdx_format`、`project_create`、`project_open`、`project_view`、`project_browser`、`project_find`、`project_rename`、`module_rename`、`module_remove`、`module_file`、`module_edit`、`collection_create`、`collection_file`、`collection_edit`、`collection_rename`、`collection_remove`，并在 `project_inspect` 上暴露同一份 inspection contract，同时暴露从 `get_frontend_api_binding_index("mcp")` 派生的 `frontend_operation_ids`。`get_openapi_seed()` 暴露 architecture、带可选 `operation_id`/`group_id` selector 和 `form=true` operation projection 的 frontend API discovery、通过 `GET /frontend-api/workspace` 暴露的 frontend API workspace discovery、通过 `GET /frontend-api/action` 暴露的 frontend API selected-action detail、通过 `POST /frontend-api/options` 暴露的 frontend API option resolution、通过 `POST /frontend-api/normalize` 暴露的 frontend API input normalization、通过 `POST /frontend-api/rest-request` 暴露的 frontend API REST request planning、通过 `GET /frontend-api/binding` 暴露的 frontend API binding reverse lookup、PDX parse/format、LSP diagnostics/symbols/hover/formatting/completion/semantic tokens、项目创建、项目打开/视图、项目注册表列表、桌面项目状态、project browser、项目发现、仅修改标题的项目 rename、源模块 rename/remove、collection descriptor 创建/重命名/删除、模块与 collection 文本文件读写、project authoring 读取、scaffold plan/write、project build plan/emit、通过 `POST`/`PUT /projects/catalog` 暴露 catalog write/refresh、project inspection contract 和 project inspection payload 的 REST/OpenAPI 路径。由 frontend row 派生的 REST operation 会带上 `x-paradev-frontend-api-operation-ids`，并且必须从 `bindings.rest` 生成，不要手工维护；`tests/test_architecture.py::test_frontend_api_contract_indexes_every_surface_binding_and_openapi_annotation` 会同时防止 binding index 和 OpenAPI annotation 漂移。

当前端需要稳定的表单或 action 签名时，frontend API operation 行可以包含 `inputs`。project、module、collection、build、catalog、PDX、LSP 和 frontend API selector 行已经为 create/find/open/view/list/templates/authoring/file/edit/rename/remove/activate、build plan/emit/inspection、catalog preview/write/refresh/query、已保存文件 parse/format、编辑器 buffer diagnostics/symbols/hover/formatting/completion/semantic tokens、operation/group/action lookup 流程，以及 `surface.frontend_api.action`、`surface.frontend_api.options`、`surface.frontend_api.normalize`、`surface.frontend_api.rest_request`、`surface.frontend_api.binding_lookup` 发布这些字段，因此 GUI 和导入器代码应读取这份 row metadata，不要复制 CLI option list、REST request body 或 OpenAPI parameter name。带 SDK、CLI、REST、MCP 或 LSP 字段的行也会发布派生的 `bindings`；生成客户端应使用 `bindings.rest.method`、`bindings.rest.path` 和 `bindings.rest.query`，不要解析给人阅读的 `rest` 字符串。Workspace action rows 会复制这些 bindings，并增加 `execution` object；扩展 action execution 时应修正 canonical operation row 或 binding derivation，不要新增 GUI-only action registry。`execution.confirmation` 是 action execution contract 的一部分，GUI shell 只能从这里读取确认要求。`get_frontend_api_action(...)` 会从 operation row、workspace action、form helper、option-source 摘要和 binding derivation 组合一个已选 action；已选 action detail payload 需要新的派生元数据时，应扩展这个 helper。TypeScript GUI 代码如果只需要 generated workspace action、binding、surface operation lists 或 raw input rows，应使用 `apps/desktop/src/data/frontendApi.ts` 中的 `frontendApiWorkspaceActions`、`getFrontendApiAction(...)`、`getFrontendApiActionDetail(...)`、`getFrontendApiFormControls(...)`、`getFrontendApiFormControlKind(...)`、`getFrontendApiFormValuesWithDefaults(...)`、`getFrontendApiFormOptionRequests(...)`、`resolveFrontendApiFormOptionRequest(...)`、`resolveFrontendApiNormalizeRequest(...)`、`resolveFrontendApiRestPlanRequest(...)`、`getFrontendApiSectionActions(...)`、`getFrontendApiDefaultSectionAction(...)`、`getFrontendApiBindings(...)`、`getFrontendApiRestBinding(...)`、`frontendApiSurfaceIndex`、`getFrontendApiSurfaceOperationIds(...)`、`frontendApiInputOperations`、`getFrontendApiInputs(...)`、`getFrontendApiRequiredInputNames(...)`、`getFrontendApiDefaultValues(...)` 和 `getFrontendApiOptionSourceInputs(...)`。TypeScript client 调用 frontend API meta endpoints 时应使用同一文件的 `frontendApiEndpointPaths`、`buildFrontendApi*Url(...)` helpers、`buildFrontendApiOptionsRequest(...)`、`buildFrontendApiNormalizeRequest(...)`、`buildFrontendApiRestPlanRequest(...)` 这类 JSON request helpers，以及匹配的 resolver helpers；不要手写 `operation_id`、`field_name` query string、request headers、submitted-value body 或 meta-result state。同一组行还会派生 `index["binding"]`，从 surface call key 反查 operation id；扩展它时应添加或修正 row-level `bindings`，不要手工编辑 surface 专属映射，并且 Python 端应使用 `get_frontend_api_binding_lookup(...)` 或 `get_frontend_api_binding_operation_ids(...)`，而不是直接索引 raw map。它们也会派生 `index["surface"]`，即 surface 到 operation id 的投影；扩展它时应修正 row-level `bindings`，并通过 `contract["index"]["surface"]` 或 `getFrontendApiSurfaceOperationIds(...)` 消费，不要扫描 rows。`get_frontend_api_form(...)` 会从同一份 `inputs` 派生有序 fields、target buckets、required names、defaults、aliases、controls、option-source provider metadata 和 JSON Schema；option source 会指向 canonical provider operations，例如 `module.templates`、`build.families`、`module.list`、`collection.list`、`build.artifacts` 和 `build.diagnostics`。`resolve_frontend_api_options(...)` 会通过 `Project.templates(...)` 或 `Project.inspect(...)` 执行这些支持的 provider，返回 `paradev.sdk.frontend-api.options.v1`，并在缺少依赖字段时返回 `available=false` 和 `missing_requirements`，而不是抛错。`getFrontendApiFormOptionRequests(...)` 在 TypeScript 中镜像同一套依赖状态，并且只有在提交值加 SDK 默认值满足 provider requirements 时才返回 request。`normalize_frontend_api_inputs(...)` 会应用 defaults、校验未知或缺失字段，并保留 `artifact_path -> parameters.path` 这样的前端安全 alias，而不会覆盖 project `path`；`plan_frontend_api_rest_request(...)` 会复用 normalized buckets 和 `bindings.rest`，返回目标 method、path、query、body 和来源 binding。CLI `frontend-api --operation ... --action`、CLI `frontend-api --operation ... --option-field ... --values-json ...`、CLI `frontend-api --operation ... --values-json ...`、CLI `frontend-api --operation ... --values-json ... --rest-request`、CLI `frontend-api --binding-surface ... --binding-key ...`、REST `GET /frontend-api/action?operation_id=...`、REST `POST /frontend-api/options?operation_id=...&field_name=...`、REST `POST /frontend-api/normalize?operation_id=...`、REST `POST /frontend-api/rest-request?operation_id=...` 和 REST `GET /frontend-api/binding?binding_surface=...&binding_key=...` 必须路由到这些 helper。TypeScript client 应从 `apps/desktop/src/data/frontendApi.ts` 导入 typed helper；只有 generator 应改写 `apps/desktop/src/generated/frontendApi.ts`。不要再手工维护第二份 frontend form schema、action detail composer、action execution map、option-provider map、TypeScript contract、form-default map、option-request planner、frontend API query-string builder、frontend API JSON request builder、frontend API meta-result mapper、REST request mapper、binding reverse lookup、surface operation list 或 confirmation-policy mapper。

桌面 shell 应从 `frontendApiWorkspaceSections` 派生 sidebar 和 tab；不要硬编码迁移专属导航文案，也不要维护第二份 workspace-section list。已选 section 的 action table 应使用 `getFrontendApiSectionActions(...)`、`getFrontendApiDefaultSectionAction(...)` 和 `getFrontendApiRequiredInputNames(...)`；已选 action panel 应使用 `getFrontendApiActionPanelState(...)` 获取 action detail、fields、defaults、controls、option requests、normalize/rest-plan requests、confirmation state、Run state 和稳定的 effect keys；已选 action execution-plan panel 应使用 `resolveFrontendApiNormalizeRequest(...)` 和 `resolveFrontendApiRestPlanRequest(...)`；已选 action 的 Run 控件再通过 `buildFrontendApiRestExecutionRequest(...)` 与 `resolveFrontendApiRestExecutionRequest(...)` 消费 ready plan，不要在组件代码里维护 REST URL/body/error shaping，同时让 sidebar 与 tab selection 同步到 generated workspace-section id 类型。

确认接受状态属于 helper-shaped frontend state，不是新的策略 surface。使用 `FrontendApiActionConfirmationStates` 保存按 operation id 索引的接受状态，启用 Run 前调用 `isFrontendApiActionConfirmationSatisfied(...)`，提交值变化时重置接受状态。

Run state 同样属于 helper-shaped state。使用 `getFrontendApiActionRunState(...)` 传入已选 operation id、`execution.confirmation`、REST-plan result、REST-execution result 和确认状态，这样组件就不需要重复实现 disabled、loading、confirmation 或 result-detail 逻辑。

selected-action panel state 是优先使用的 higher-level helper。组件需要常见的已选 action view model 时使用 `getFrontendApiActionPanelState(...)`；只有很窄的 panel 才直接调用单个 form/default/request helper。

修改 TypeScript frontend API helper 时，先运行 `rtk npm --prefix apps/desktop run test:unit` 做 summary/group registry alignment、panel-state、request/resolver 和 bridge-unavailable helper 的直接 coverage，再运行更大的 desktop build。

GUI、MCP、REST、LSP 和导入器 agent 增加 surface 能力时，应同步扩展这些 helper，然后把实际行为路由到 `get_frontend_api_contract()`、`get_frontend_api_action(...)`、`resolve_frontend_api_options(...)`、`normalize_frontend_api_inputs(...)`、`plan_frontend_api_rest_request(...)`、`Project.create(...)`、`create_project(...)`、`project_create_payload(...)`、`Project.load(...)`、`Project.to_view()`、`Project.find(...)`、`registered_projects(...)`、`desktop_state(...)`、`Project.browser(...)`、`Project.rename(...)`、`Project.rename_module(...)`、`Project.remove_module(...)`、`Project.read_module_file(...)`、`Project.write_module_file(...)`、`Project.create_collection(...)`、`Project.read_collection_file(...)`、`Project.write_collection_file(...)`、`Project.rename_collection(...)`、`Project.remove_collection(...)`、`Project.templates()`、`Project.authoring_path(...)`、`Project.authoring_plan(...)`、`Project.scaffold_module(...)`、`Project.build(...)`、`Project.inspect(...)`、`Project.inspections()`、`get_project_inspection_contract()`、`paradev.hb.catalog_write(...)`、`paradev.hb.catalog_refresh(...)`、`parse_pdx_file(...)`、`format_pdx_file(...)`、`format_pdx_text(...)`、`diagnose_pdx_lsp_text(...)`、`document_symbols_pdx_lsp_text(...)`、`hover_pdx_lsp_text(...)`、`format_pdx_lsp_text(...)` 或其他 SDK 方法。

当前 frontend API discovery/action-detail/option-resolution/normalization/rest-request planning、project create、project open/view、project list/state/browser、project find、project rename、module rename、module remove、module text-file、collection create、collection rename、collection remove、collection text-file/source inventory、PDX parse/format、LSP diagnostics/symbols/hover/formatting/completion/semantic tokens、authoring、scaffold、build plan/emit 与 catalog write/refresh contract 已在各 surface 明确暴露：CLI `frontend-api`/`frontend-api --action`/`frontend-api --option-field`/`frontend-api --binding-surface --binding-key`/`new`/`project`/`projects`/`desktop-state`/`project-browser`/`project-find`/`project-rename`/`module-rename`/`module-remove`/`module-file`/`module-edit`/`collection-create`/`collection-rename`/`collection-remove`/`collection-file`/`collection-edit`/`sources --owner-kind collection`/`parse`/`format`/`templates`/`authoring-path`/`authoring-plan`/`scaffold`/`build`/`hb catalog-write`/`hb catalog-refresh`、REST `/frontend-api`/`/frontend-api/action`/`/frontend-api/options`/`/frontend-api/normalize`/`/frontend-api/rest-request`/`/frontend-api/binding`/`/projects`/`/projects/list`/`/desktop/state`/`/projects/browser`/`/projects/find`/`/projects/rename`/`/projects/modules/rename`/`/projects/modules/remove`/`/projects/modules/file`/`/projects/collections`/`/projects/collections/rename`/`/projects/collections/file`/`/projects/inspect?kind=sources`/`/pdx/parse`/`/pdx/format`/`/lsp/diagnostics`/`/lsp/symbols`/`/lsp/hover`/`/lsp/formatting`/`/lsp/completion`/`/lsp/semantic-tokens`/`/projects/templates`/`/projects/authoring-path`/`/projects/authoring-plan`/`/projects/scaffold`/`/projects/build`/`/projects/catalog`、LSP `textDocument/publishDiagnostics`/`textDocument/documentSymbol`/`textDocument/hover`/`textDocument/formatting`/`textDocument/completion`/`textDocument/semanticTokens/full`、MCP `frontend_api`/`project_create`/`project_open`/`project_view`/`project_browser`/`project_find`/`project_rename`/`module_rename`/`module_remove`/`module_file`/`module_edit`/`collection_create`/`collection_rename`/`collection_remove`/`collection_file`/`collection_edit`/`project_inspect`/`pdx_parse`/`pdx_format`/`project_templates`/`project_authoring_path`/`project_authoring_plan`/`project_scaffold` 都映射到同一组 SDK 调用。

由 `Project.inspect(...)` 支撑的 frontend API 行应始终列出三项信息：REST `GET /projects/inspect?kind=...`、MCP `project_inspect`，以及该 inspection kind 返回的具体 payload schema。这适用于 module 和 collection 的只读面板、collection descriptor source inventory、只读 build 面板，以及只读 catalog preview/query 面板。通用的 `project.inspect` 行可以保留较宽泛的 `Project inspection payload` 标签，因为它的 schema 取决于 `kind`；它的 inputs 应限制在 dispatcher 层面的 `path` 和 `kind`，详细过滤字段应放在具体 inspection 行上。

Family compiler 和 adapter 应通过 `load_pdx_sources(...)` 或 `parse_pdx_file(..., include_dump=True)` 消费作者编写的 PDX，不要在 surface 中直接调用 `PDXBlock.from_file(...)`。这样 CLI、SDK、REST、GUI、MCP 和 build diagnostics 都共享同一个 parser payload，同时 compiler 仍然可以拿到无损的 `PDXBlock`。

## 增加项目本地 Family

新增作者会直接使用的实体 family 时，优先给每个实体放一个可信的项目本地 Python 文件。`paradev.yaml` 只保留很小的注册入口：

```yaml
python_modules:
  - tools/families/superevent.py
  - tools/families/news_event.py
```

紧凑实体使用一个 Python 文件：

```python
from __future__ import annotations

from paradev.build import BuildRegistry, SimpleSourceFamily, Slot


def register(registry: BuildRegistry) -> BuildRegistry:
    registry.add(
        SimpleSourceFamily(
            family="superevent",
            metadata_keys=("scope",),
            pdx_path_template="events/superevents/{object_id}.txt",
            loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
            source_slots=(
                Slot("script", "script.pdx", required=True, kind="pdx"),
                Slot("loc", "*.loc", many=True, kind="loc"),
            ),
        )
    )
    return registry
```

多个 sibling module 需要编译成同一个共享文件时，使用 collection family：

```python
from __future__ import annotations

from paradev.build import BuildRegistry, CollectionSourceFamily, Slot


def register(registry: BuildRegistry) -> BuildRegistry:
    registry.add(
        CollectionSourceFamily(
            family="news_event",
            pdx_path_template="events/{collection_id}.txt",
            loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
            source_slots=(Slot("body", "body.pdx", required=True, kind="pdx"),),
            collection_source_slots=(
                Slot("header", "header.pdx", required=True, kind="pdx"),
                Slot("strings", "strings.loc", kind="loc"),
            ),
        )
    )
    return registry
```

更大的实体可以使用 `tools/families/superevent/family.py` 这样的专门目录，并在 `python_modules` 里列出这个 `family.py`。可执行示例放在 `docs/examples/families/`，并由 `tests/test_python_family_examples.py` 覆盖。

加载项目后，`Project.families()["authoring"]` 会暴露 SDK 拥有的源目录，以及标准的 `modules/{family}/{object_id}` 和 `collections/{family}/{collection_id}` 目录模板。Family 行会暴露 `metadata.keys`、`metadata.common_keys`、`metadata.family_keys`、`metadata.settings` 和 `metadata.unknown_key_policy`，因此客户端可以渲染 `meta.yaml` 表单，并解释 loose/strict diagnostic，而不需要复制 loader allowlist。它也会暴露 `outputs`，由 emit 阶段使用的同一组模板派生，因此客户端可以直接读取 `artifact_type`、`template_key`、`template`、`owner_kinds`、`target_root`，以及 route 或 sprite-slot 上下文，而不需要解析模板名称。旁边的 `index` 会把 family id、编译器种类、源 slot、collection descriptor slot、sprite slot、route、output artifact type 和 artifact writer 类型映射到返回的行号；`output_artifact_type` 索引 family 行，`artifact_type` 索引 writer 行。导入器、GUI 客户端、MCP 工具和项目本地 family helper 应读取这个 payload，而不是重复实现发现或输出规则。`Project.templates()` 补充现成起始文件模板；每个模板行包含 `authoring_ready`，指向未注册 family 的行会包含 `diagnostic_codes: ["template.unknown_family"]`。它的 `index` 会把 `id`、`family`、`source`、`authoring_ready` 和 `diagnostic_code` 映射到返回行号。surface 只需要一个模板子集时，对这些字段使用精确的 `Project.templates(...)` 过滤参数；返回的 index 行号只指向过滤后的 payload。adapter 应用这些字段选择模板，并在调用 `Project.scaffold_module(...)` 前禁用不可用的 scaffold 操作。工具只需要一个 family contract 时，使用 `Project.families(...)` 的精确过滤参数，例如 `family`、`kind`、`source_slot`、`collection_source_slot`、`sprite_slot`、`route` 或 `artifact_type`。adapter 如果已经持有 `BuildRegistry` 和明确的项目上下文，可以调用可复用的 build 层 wrapper：`paradev.build.families_view(...)`。工具需要一个具体根目录时，使用 `Project.authoring_path("module", family, object_id)` 或 `Project.authoring_path("collection", family, collection_id)`；工具还需要在文件存在前或运行构建前展示期望源 slot 以及当前 `empty`/`missing`/`satisfied`/`diagnostic` 状态时，使用 `Project.authoring_plan(...)`；更底层、已经持有项目根目录的 adapter 可以复用 `paradev.build.authoring_path_view(...)`、`authoring_plan_view(...)` 和 `authoring_view(...)`。

adapter 代码如果从命令、UI 操作、MCP 工具或 REST route 中收到 inspection kind，应调用 `Project.inspect(kind, **filters)`，不要维护另一套 dispatch 表。项目加载前的静态 adapter 注册使用 `get_project_inspection_contract()`；需要同一份 contract 带上已加载项目 id 时，使用 `Project.inspections()`。支持的 kind 包括 `inspections`、`summary`、`manifests`、`modules`、`collections`、`artifacts`、`localization`、`source-slots`、`sources`、`assets`、`sprites`、`diagnostics`、`source-map`、`dependencies`、`build-graph`、`build-explain`、`catalog-preview`、`catalog-query` 和 `families`。直接 Python 代码已经知道目标时，继续使用 `Project.modules(...)` 等具体方法即可。如果 compiler 测试、MCP 内部或其他 adapter 已经持有 `BuildResult`，应调用可复用的 build 层 view helper，例如 `paradev.build.summary_view(...)`、`manifests_view(...)`、`modules_view(...)`、`artifacts_view(...)`、`sources_view(...)`、`assets_view(...)`、`sprites_view(...)`、`diagnostics_view(...)`、`source_map_view(...)` 和 `dependencies_view(...)`，不要复制 SDK 过滤逻辑。surface 需要模块或 collection descriptor 的“期望 slot 和实际文件”矩阵时，使用 `Project.source_slots(...)`；exact slot 行会包含 suggested paths，方便 missing-file UI；可复用的 build 层 helper 是 `paradev.build.source_slot_status(...)`。surface 需要在 artifact traceability 之前展示实际 compiler 输入时，使用 `Project.sources(...)`；descriptor 自己拥有的 collection inputs 应传入 `owner_kind="collection"`，不要手工 join rows；build panel 需要静态复制行或 sprite 声明而不写文件时，使用 `Project.assets(...)` / `Project.sprites(...)`。

metadata 校验模式由 SDK 统一拥有。未知模块或 collection 元数据键的包默认行为是 loose-mode warning；省略参数的 SDK、CLI、REST、frontend 调用会继承 `CM_PARADEV` 中的 `paradev.build.strict_metadata`。`strict_metadata=True` 会通过 `load_metadata(...)`、发现流程、`Project.build(...)`、`Project.diagnostics(...)`、CLI `build --strict-metadata`、REST `POST /projects/build?strict_metadata=true`，以及 frontend 行 `build.plan`、`build.emit`、`build.diagnostics`，把同一个 `metadata.unknown_key` diagnostic 提升为 error；显式 `False` 或 `--no-strict-metadata` 会保持 loose mode。新增 compiler 应在 build registry 中声明可接受的 metadata key；对应的 `Project.families()` metadata contract 会发布 SDK common keys、family keys 和 unknown-key policy，因此 surface 应复用这条共享路径，不要在某个 surface 里另写 unknown-key 检查。

源文件索引必须集中维护。HeavenBase 的 `source-file` catalog entity 派生自 `sources.json`，因此新的 source loader 应把 loader 专属摘要加入 source inventory，不要新增第二套 catalog 路径。Catalog tag 是追加式的：source 行保留简单的 module/family/slot tag，也会暴露 `module:<id>`、`collection:<id>`、`family:<family>`、`slot:<slot>`、`loader:<loader>` 和 `status:<status>` 等带前缀 tag。

声明式 `families` 仍然适合 slots 和模板已经足够的小型生成式 manifest，但手写 family 的常规指南是 Python。Python 路径会把 slots、metadata keys、compiler kind，以及自定义 normalizer/checker 放在每个实体一个可 review 的文件里。

项目级 artifact 也应该走 build registry。HOI4 profile 通过 `mod_descriptor` family 和 `ModDescriptorWriter`，从 `BuildContext.metadata` 生成 `descriptor.mod` 与 launcher 预览；不要在 CLI、GUI 或 MCP 层添加 surface 专用写文件逻辑。

## 测试与门禁

行为变更使用 TDD。先跑聚焦测试，再跑仓库 wrapper：

```bash
rtk uv run pytest tests/test_project_build.py
rtk uv run python .claude/skills/heaven-style/scripts/scan.py src tests
rtk bash scripts/flake.bash --ci
rtk bash scripts/test.bash
rtk uv build
```

公开行为变化时必须更新文档。手册变更可用以下命令验证：

```bash
rtk rg -n "paradev|Project.load|PIHC3|diagnostics|build" docs/user-manual README.en.md docs/workflows/build-flow.md
```
