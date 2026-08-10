# REST API Reference

Generated from `paradev.surfaces.rest.get_rest_api_table()`.

Regenerate this file whenever the REST/OpenAPI route table changes:

```bash
rtk uv run paradev rest-api --markdown > docs/user-manual/rest-api-reference.md
```

## Summary / 汇总

- API rows / API 行数: 84
- Methods / Method 数: 5
- Features / Feature 数: 17
- Frontend-bound operations / 前端绑定操作数: 92
- Selector helper / Selector helper: Use `get_rest_api_selection(symbol=..., index_name=..., key=...)` returns the table, one route row, or one route-symbol index projection.

## Method Index / Method 索引

| Method | Routes | Symbols |
| --- | --- | --- |
| `GET` | 37 | `GET /health`, `GET /api-catalog`, `GET /rest-api`, `GET /cli-api`, `GET /surface-contracts`, `GET /frontend-api`, `GET /frontend-api/workspace`, `GET /frontend-api/action`, `GET /frontend-api/binding`, `GET /architecture`, `GET /projects/{project_id}/sources`, `GET /projects/modules/diagram`, `GET /pdx/parse`, `GET /pdx-api`, `GET /lsp-api`, `GET /catalog-api`, `GET /lsp/keywords`, `GET /projects/inspections`, `GET /projects/templates`, `GET /projects/authoring-path`, `GET /projects/authoring-plan`, `GET /projects/catalog`, `GET /projects`, `GET /projects/list`, `GET /desktop/state`, `GET /desktop/builds`, `GET /desktop/builds/status`, `GET /desktop/path-status`, `GET /desktop/hoi4-launch-readiness`, `GET /desktop/app-config`, `GET /desktop/config-value`, `GET /desktop/ai/profiles`, `GET /projects/browser`, `GET /projects/find`, `GET /projects/modules/file`, `GET /projects/collections/file`, `GET /projects/inspect` |
| `POST` | 34 | `POST /frontend-api/normalize`, `POST /frontend-api/rest-request`, `POST /frontend-api/options`, `POST /projects/{project_id}/sources/form`, `POST /projects/{project_id}/localization/workspace`, `POST /projects/{project_id}/localization/plan`, `POST /projects/{project_id}/drafts/apply`, `POST /projects/{project_id}/modules/{family_id}/drafts`, `POST /projects/modules/create-batch`, `POST /projects/modules/duplicate`, `POST /projects/modules/metadata/clean`, `POST /projects/modules/collection`, `POST /projects/modules/activity`, `POST /projects/modules/diagram/edit`, `POST /pdx/format`, `POST /lsp/diagnostics`, `POST /lsp/symbols`, `POST /lsp/hover`, `POST /lsp/formatting`, `POST /lsp/completion`, `POST /lsp/semantic-tokens`, `POST /projects/scaffold`, `POST /projects/build`, `POST /projects/catalog`, `POST /projects`, `POST /desktop/builds`, `POST /desktop/builds/interrupt`, `POST /desktop/open-path`, `POST /desktop/select-project`, `POST /desktop/import-project-package`, `POST /desktop/llm/test`, `POST /desktop/ai/chat`, `POST /projects/collections/scaffold`, `POST /projects/collections` |
| `PUT` | 4 | `PUT /projects/catalog`, `PUT /desktop/app-config`, `PUT /desktop/config-value`, `PUT /desktop/ai/profiles/{profile_id}` |
| `DELETE` | 3 | `DELETE /desktop/ai/profiles/{profile_id}`, `DELETE /projects/modules/remove`, `DELETE /projects/collections` |
| `PATCH` | 6 | `PATCH /projects/rename`, `PATCH /projects/language`, `PATCH /projects/modules/rename`, `PATCH /projects/modules/file`, `PATCH /projects/collections/rename`, `PATCH /projects/collections/file` |

## Feature Index / Feature 索引

| Feature | Routes | Symbols |
| --- | --- | --- |
| `health` | 1 | `GET /health` |
| `api-catalog` | 1 | `GET /api-catalog` |
| `rest` | 1 | `GET /rest-api` |
| `cli` | 1 | `GET /cli-api` |
| `surface-contracts` | 1 | `GET /surface-contracts` |
| `frontend-api` | 7 | `GET /frontend-api`, `GET /frontend-api/workspace`, `GET /frontend-api/action`, `POST /frontend-api/normalize`, `POST /frontend-api/rest-request`, `POST /frontend-api/options`, `GET /frontend-api/binding` |
| `architecture` | 1 | `GET /architecture` |
| `projects` | 13 | `GET /projects/{project_id}/sources`, `POST /projects/{project_id}/sources/form`, `POST /projects/{project_id}/localization/workspace`, `POST /projects/{project_id}/localization/plan`, `POST /projects/{project_id}/drafts/apply`, `GET /projects/inspections`, `GET /projects`, `POST /projects`, `GET /projects/list`, `GET /projects/browser`, `GET /projects/find`, `PATCH /projects/rename`, `PATCH /projects/language` |
| `modules` | 12 | `POST /projects/{project_id}/modules/{family_id}/drafts`, `POST /projects/modules/create-batch`, `POST /projects/modules/duplicate`, `POST /projects/modules/metadata/clean`, `POST /projects/modules/collection`, `POST /projects/modules/activity`, `GET /projects/modules/diagram`, `POST /projects/modules/diagram/edit`, `PATCH /projects/modules/rename`, `DELETE /projects/modules/remove`, `GET /projects/modules/file`, `PATCH /projects/modules/file` |
| `pdx` | 3 | `GET /pdx/parse`, `POST /pdx/format`, `GET /pdx-api` |
| `lsp` | 8 | `GET /lsp-api`, `POST /lsp/diagnostics`, `POST /lsp/symbols`, `POST /lsp/hover`, `POST /lsp/formatting`, `POST /lsp/completion`, `POST /lsp/semantic-tokens`, `GET /lsp/keywords` |
| `catalog` | 4 | `GET /catalog-api`, `GET /projects/catalog`, `POST /projects/catalog`, `PUT /projects/catalog` |
| `authoring` | 4 | `GET /projects/templates`, `GET /projects/authoring-path`, `GET /projects/authoring-plan`, `POST /projects/scaffold` |
| `build` | 1 | `POST /projects/build` |
| `desktop` | 19 | `GET /desktop/state`, `GET /desktop/builds`, `POST /desktop/builds`, `GET /desktop/builds/status`, `POST /desktop/builds/interrupt`, `POST /desktop/open-path`, `POST /desktop/select-project`, `POST /desktop/import-project-package`, `GET /desktop/path-status`, `GET /desktop/hoi4-launch-readiness`, `GET /desktop/app-config`, `PUT /desktop/app-config`, `GET /desktop/config-value`, `PUT /desktop/config-value`, `POST /desktop/llm/test`, `POST /desktop/ai/chat`, `GET /desktop/ai/profiles`, `PUT /desktop/ai/profiles/{profile_id}`, `DELETE /desktop/ai/profiles/{profile_id}` |
| `collections` | 6 | `POST /projects/collections/scaffold`, `POST /projects/collections`, `DELETE /projects/collections`, `PATCH /projects/collections/rename`, `GET /projects/collections/file`, `PATCH /projects/collections/file` |
| `inspections` | 1 | `GET /projects/inspect` |

## Frontend Operation Index / 前端操作索引

| Operation | Routes | Symbols |
| --- | --- | --- |
| `surface.frontend_api` | 1 | `GET /frontend-api` |
| `surface.frontend_api.workspace` | 1 | `GET /frontend-api/workspace` |
| `surface.frontend_api.action` | 1 | `GET /frontend-api/action` |
| `surface.frontend_api.normalize` | 1 | `POST /frontend-api/normalize` |
| `surface.frontend_api.rest_request` | 1 | `POST /frontend-api/rest-request` |
| `surface.frontend_api.options` | 1 | `POST /frontend-api/options` |
| `surface.frontend_api.binding_lookup` | 1 | `GET /frontend-api/binding` |
| `surface.architecture` | 1 | `GET /architecture` |
| `project.source_text` | 1 | `GET /projects/{project_id}/sources` |
| `project.source_form` | 1 | `POST /projects/{project_id}/sources/form` |
| `localization.workspace` | 1 | `POST /projects/{project_id}/localization/workspace` |
| `localization.plan` | 1 | `POST /projects/{project_id}/localization/plan` |
| `project.draft_apply` | 1 | `POST /projects/{project_id}/drafts/apply` |
| `module.draft` | 1 | `POST /projects/{project_id}/modules/{family_id}/drafts` |
| `module.create_batch` | 1 | `POST /projects/modules/create-batch` |
| `module.duplicate` | 1 | `POST /projects/modules/duplicate` |
| `module.metadata.clean` | 1 | `POST /projects/modules/metadata/clean` |
| `module.collection.set` | 1 | `POST /projects/modules/collection` |
| `module.activity.set` | 1 | `POST /projects/modules/activity` |
| `module.diagram` | 1 | `GET /projects/modules/diagram` |
| `module.diagram.edit` | 1 | `POST /projects/modules/diagram/edit` |
| `pdx.parse` | 1 | `GET /pdx/parse` |
| `pdx.tokens` | 1 | `GET /pdx/parse` |
| `pdx.dump` | 1 | `GET /pdx/parse` |
| `pdx.format` | 1 | `POST /pdx/format` |
| `lsp.diagnostics` | 1 | `POST /lsp/diagnostics` |
| `lsp.symbols` | 1 | `POST /lsp/symbols` |
| `lsp.hover` | 1 | `POST /lsp/hover` |
| `lsp.formatting` | 1 | `POST /lsp/formatting` |
| `lsp.completion` | 1 | `POST /lsp/completion` |
| `lsp.semantic_tokens` | 1 | `POST /lsp/semantic-tokens` |
| `lsp.keywords` | 1 | `GET /lsp/keywords` |
| `module.templates` | 1 | `GET /projects/templates` |
| `module.authoring_path` | 1 | `GET /projects/authoring-path` |
| `collection.authoring_path` | 1 | `GET /projects/authoring-path` |
| `module.authoring_plan` | 1 | `GET /projects/authoring-plan` |
| `collection.authoring_plan` | 1 | `GET /projects/authoring-plan` |
| `module.create` | 1 | `POST /projects/scaffold` |
| `build.plan` | 1 | `POST /projects/build` |
| `build.emit` | 1 | `POST /projects/build` |
| `catalog.write` | 1 | `POST /projects/catalog` |
| `catalog.refresh` | 1 | `PUT /projects/catalog` |
| `project.open` | 1 | `GET /projects` |
| `project.view` | 1 | `GET /projects` |
| `project.create` | 1 | `POST /projects` |
| `project.list` | 1 | `GET /projects/list` |
| `project.state` | 1 | `GET /desktop/state` |
| `build.runs` | 1 | `GET /desktop/builds` |
| `build.start` | 1 | `POST /desktop/builds` |
| `build.status` | 1 | `GET /desktop/builds/status` |
| `build.interrupt` | 1 | `POST /desktop/builds/interrupt` |
| `ai.chat` | 1 | `POST /desktop/ai/chat` |
| `ai.profiles` | 1 | `GET /desktop/ai/profiles` |
| `ai.profile.write` | 1 | `PUT /desktop/ai/profiles/{profile_id}` |
| `ai.profile.reset` | 1 | `DELETE /desktop/ai/profiles/{profile_id}` |
| `project.browser` | 1 | `GET /projects/browser` |
| `project.find` | 1 | `GET /projects/find` |
| `project.rename` | 1 | `PATCH /projects/rename` |
| `project.language` | 1 | `PATCH /projects/language` |
| `module.rename` | 1 | `PATCH /projects/modules/rename` |
| `module.remove` | 1 | `DELETE /projects/modules/remove` |
| `module.file` | 1 | `GET /projects/modules/file` |
| `module.edit` | 1 | `PATCH /projects/modules/file` |
| `collection.scaffold` | 1 | `POST /projects/collections/scaffold` |
| `collection.create` | 1 | `POST /projects/collections` |
| `collection.remove` | 1 | `DELETE /projects/collections` |
| `collection.rename` | 1 | `PATCH /projects/collections/rename` |
| `collection.file` | 1 | `GET /projects/collections/file` |
| `collection.edit` | 1 | `PATCH /projects/collections/file` |
| `project.inspect` | 1 | `GET /projects/inspect` |
| `module.list` | 1 | `GET /projects/inspect` |
| `module.view` | 1 | `GET /projects/inspect` |
| `module.source_slots` | 1 | `GET /projects/inspect` |
| `module.sources` | 1 | `GET /projects/inspect` |
| `collection.list` | 1 | `GET /projects/inspect` |
| `collection.view` | 1 | `GET /projects/inspect` |
| `collection.source_slots` | 1 | `GET /projects/inspect` |
| `collection.sources` | 1 | `GET /projects/inspect` |
| `build.summary` | 1 | `GET /projects/inspect` |
| `build.manifests` | 1 | `GET /projects/inspect` |
| `build.artifacts` | 1 | `GET /projects/inspect` |
| `build.localization` | 1 | `GET /projects/inspect` |
| `build.assets` | 1 | `GET /projects/inspect` |
| `build.sprites` | 1 | `GET /projects/inspect` |
| `build.diagnostics` | 1 | `GET /projects/inspect` |
| `build.source_map` | 1 | `GET /projects/inspect` |
| `build.dependencies` | 1 | `GET /projects/inspect` |
| `build.graph` | 1 | `GET /projects/inspect` |
| `build.explain` | 1 | `GET /projects/inspect` |
| `build.families` | 1 | `GET /projects/inspect` |
| `catalog.preview` | 1 | `GET /projects/inspect` |
| `catalog.query` | 1 | `GET /projects/inspect` |

## API Standard Table / API 标准表

| Symbol | Kind | Layer | Feature | Method | Path | Inputs | Required Inputs | Returns | Raises | Frontend Operation IDs | Registry Seam | Doc Page | Test Anchor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `GET /health` | `REST route` | `rest` | `health` | `GET` | `/health` | `none` | `none` | `200 Local API process is responding.` |  |  | `OpenAPI path /health` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /api-catalog` | `REST route` | `rest` | `api-catalog` | `GET` | `/api-catalog` | `query:reference_id, query:index_name, query:key` | `none` | `200 API catalog table, row, or index lookup payload.` | `400 Invalid API catalog selector.` |  | `OpenAPI path /api-catalog` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /rest-api` | `REST route` | `rest` | `rest` | `GET` | `/rest-api` | `query:symbol, query:index_name, query:key` | `none` | `200 REST API table, row, or index lookup payload.` | `400 Invalid REST API selector.` |  | `OpenAPI path /rest-api` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /cli-api` | `REST route` | `rest` | `cli` | `GET` | `/cli-api` | `query:symbol, query:index_name, query:key` | `none` | `200 CLI API table, row, or index lookup payload.` | `400 Invalid CLI API selector.` |  | `OpenAPI path /cli-api` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /surface-contracts` | `REST route` | `rest` | `surface-contracts` | `GET` | `/surface-contracts` | `query:identifier, query:status` | `none` | `200 Surface contract summary, contract payload, or status id list.` | `400 Invalid surface contract selector.` |  | `OpenAPI path /surface-contracts` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /frontend-api` | `REST route` | `rest` | `frontend-api` | `GET` | `/frontend-api` | `query:operation_id, query:group_id, query:form, query:index_name, query:key` | `none` | `200 Frontend API contract or selected projection.` | `400 Invalid frontend API selector.` | `surface.frontend_api` | `OpenAPI path /frontend-api` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /frontend-api/workspace` | `REST route` | `rest` | `frontend-api` | `GET` | `/frontend-api/workspace` | `none` | `none` | `200 Frontend API workspace projection.` |  | `surface.frontend_api.workspace` | `OpenAPI path /frontend-api/workspace` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /frontend-api/action` | `REST route` | `rest` | `frontend-api` | `GET` | `/frontend-api/action` | `query:operation_id` | `query:operation_id` | `200 Frontend API action detail.` |  | `surface.frontend_api.action` | `OpenAPI path /frontend-api/action` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /frontend-api/normalize` | `REST route` | `rest` | `frontend-api` | `POST` | `/frontend-api/normalize` | `query:operation_id, body` | `query:operation_id` | `200 Normalized frontend API input payload.` |  | `surface.frontend_api.normalize` | `OpenAPI path /frontend-api/normalize` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /frontend-api/rest-request` | `REST route` | `rest` | `frontend-api` | `POST` | `/frontend-api/rest-request` | `query:operation_id, body` | `query:operation_id` | `200 Frontend API REST request plan.` |  | `surface.frontend_api.rest_request` | `OpenAPI path /frontend-api/rest-request` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /frontend-api/options` | `REST route` | `rest` | `frontend-api` | `POST` | `/frontend-api/options` | `query:operation_id, query:field_name, body` | `query:operation_id, query:field_name` | `200 Frontend API option-source payload.` |  | `surface.frontend_api.options` | `OpenAPI path /frontend-api/options` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /frontend-api/binding` | `REST route` | `rest` | `frontend-api` | `GET` | `/frontend-api/binding` | `query:binding_surface, query:binding_key` | `query:binding_surface, query:binding_key` | `200 Frontend API binding lookup payload.` |  | `surface.frontend_api.binding_lookup` | `OpenAPI path /frontend-api/binding` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /architecture` | `REST route` | `rest` | `architecture` | `GET` | `/architecture` | `query:api_table, query:symbol, query:index_name, query:key` | `none` | `200 ParaDev architecture graph or architecture API table selection.` | `400 Invalid architecture API table selector.` | `surface.architecture` | `OpenAPI path /architecture` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /projects/{project_id}/sources` | `REST route` | `rest` | `projects` | `GET` | `/projects/{project_id}/sources` | `path:project_id, query:path, query:project_root` | `path:project_id, query:path` | `200 Project source text and stable revision.` | `400 Invalid project or source path.` | `project.source_text` | `OpenAPI path /projects/{project_id}/sources` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /projects/{project_id}/sources/form` | `REST route` | `rest` | `projects` | `POST` | `/projects/{project_id}/sources/form` | `path:project_id, body` | `path:project_id, body` | `200 Source form payload or null when unsupported.` | `400 Invalid project, source path, editor text, or family form contract.` | `project.source_form` | `OpenAPI path /projects/{project_id}/sources/form` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /projects/{project_id}/localization/workspace` | `REST route` | `rest` | `projects` | `POST` | `/projects/{project_id}/localization/workspace` | `path:project_id, body` | `path:project_id, body` | `200 Registry-owned source-unit localization workspace.` | `400 Invalid project, target, source, draft, or localization syntax.` | `localization.workspace` | `OpenAPI path /projects/{project_id}/localization/workspace` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /projects/{project_id}/localization/plan` | `REST route` | `rest` | `projects` | `POST` | `/projects/{project_id}/localization/plan` | `path:project_id, body` | `path:project_id, body` | `200 Revision-guarded source-unit localization update plan.` | `400 Invalid project, target, draft, localization operation, or source state.` | `localization.plan` | `OpenAPI path /projects/{project_id}/localization/plan` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /projects/{project_id}/drafts/apply` | `REST route` | `rest` | `projects` | `POST` | `/projects/{project_id}/drafts/apply` | `path:project_id, body` | `path:project_id, body` | `200 Applied project draft edits.` | `400 Invalid project or draft request.` | `project.draft_apply` | `OpenAPI path /projects/{project_id}/drafts/apply` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /projects/{project_id}/modules/{family_id}/drafts` | `REST route` | `rest` | `modules` | `POST` | `/projects/{project_id}/modules/{family_id}/drafts` | `path:project_id, path:family_id, body` | `path:project_id, path:family_id, body` | `200 SDK scaffold draft plan.` | `400 Invalid project or scaffold request.` | `module.draft` | `OpenAPI path /projects/{project_id}/modules/{family_id}/drafts` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /projects/modules/create-batch` | `REST route` | `rest` | `modules` | `POST` | `/projects/modules/create-batch` | `body` | `body` | `200 SDK module batch plan or apply payload.` | `400 Invalid project or module batch request.` | `module.create_batch` | `OpenAPI path /projects/modules/create-batch` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /projects/modules/duplicate` | `REST route` | `rest` | `modules` | `POST` | `/projects/modules/duplicate` | `body` | `body` | `200 SDK module duplicate plan or apply payload.` | `400 Invalid project or module duplicate request.` | `module.duplicate` | `OpenAPI path /projects/modules/duplicate` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /projects/modules/metadata/clean` | `REST route` | `rest` | `modules` | `POST` | `/projects/modules/metadata/clean` | `body` | `body` | `200 SDK module metadata cleanup plan or apply payload.` | `400 Invalid project or metadata cleanup request.` | `module.metadata.clean` | `OpenAPI path /projects/modules/metadata/clean` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /projects/modules/collection` | `REST route` | `rest` | `modules` | `POST` | `/projects/modules/collection` | `body` | `body` | `200 SDK module collection plan or apply payload.` | `400 Invalid project or module collection request.` | `module.collection.set` | `OpenAPI path /projects/modules/collection` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /projects/modules/activity` | `REST route` | `rest` | `modules` | `POST` | `/projects/modules/activity` | `body` | `body` | `200 SDK module activity plan or apply payload.` | `400 Invalid project or module activity request.` | `module.activity.set` | `OpenAPI path /projects/modules/activity` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /projects/modules/diagram` | `REST route` | `rest` | `modules` | `GET` | `/projects/modules/diagram` | `query:path, query:family, query:profile` | `query:family` | `200 SDK source-backed module diagram payload.` | `400 Invalid project or module diagram request.` | `module.diagram` | `OpenAPI path /projects/modules/diagram` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /projects/modules/diagram/edit` | `REST route` | `rest` | `modules` | `POST` | `/projects/modules/diagram/edit` | `body` | `body` | `200 SDK module diagram edit plan or apply payload.` | `400 Invalid project or module diagram edit request.` | `module.diagram.edit` | `OpenAPI path /projects/modules/diagram/edit` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /pdx/parse` | `REST route` | `rest` | `pdx` | `GET` | `/pdx/parse` | `query:path, query:include_dump, query:include_tokens` | `query:path` | `200 PDX parse payload.` |  | `pdx.parse`, `pdx.tokens`, `pdx.dump` | `OpenAPI path /pdx/parse` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /pdx/format` | `REST route` | `rest` | `pdx` | `POST` | `/pdx/format` | `query:path, query:indent, query:comments, query:write` | `query:path` | `200 PDX format payload.` |  | `pdx.format` | `OpenAPI path /pdx/format` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /pdx-api` | `REST route` | `rest` | `pdx` | `GET` | `/pdx-api` | `query:symbol, query:index_name, query:key` | `none` | `200 PDX API table, row, or index lookup payload.` | `400 Invalid PDX API selector.` |  | `OpenAPI path /pdx-api` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /lsp-api` | `REST route` | `rest` | `lsp` | `GET` | `/lsp-api` | `query:symbol, query:index_name, query:key` | `none` | `200 LSP API table, row, or index lookup payload.` | `400 Invalid LSP API selector.` |  | `OpenAPI path /lsp-api` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /catalog-api` | `REST route` | `rest` | `catalog` | `GET` | `/catalog-api` | `query:symbol, query:index_name, query:key` | `none` | `200 Catalog API table, row, or index lookup payload.` | `400 Invalid catalog API selector.` |  | `OpenAPI path /catalog-api` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /lsp/diagnostics` | `REST route` | `rest` | `lsp` | `POST` | `/lsp/diagnostics` | `body` | `body` | `200 LSP diagnostics payload.` |  | `lsp.diagnostics` | `OpenAPI path /lsp/diagnostics` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /lsp/symbols` | `REST route` | `rest` | `lsp` | `POST` | `/lsp/symbols` | `body` | `body` | `200 LSP document symbols payload.` |  | `lsp.symbols` | `OpenAPI path /lsp/symbols` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /lsp/hover` | `REST route` | `rest` | `lsp` | `POST` | `/lsp/hover` | `body` | `body` | `200 LSP hover payload.` |  | `lsp.hover` | `OpenAPI path /lsp/hover` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /lsp/formatting` | `REST route` | `rest` | `lsp` | `POST` | `/lsp/formatting` | `body` | `body` | `200 LSP formatting payload.` |  | `lsp.formatting` | `OpenAPI path /lsp/formatting` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /lsp/completion` | `REST route` | `rest` | `lsp` | `POST` | `/lsp/completion` | `body` | `body` | `200 LSP completion payload.` |  | `lsp.completion` | `OpenAPI path /lsp/completion` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /lsp/semantic-tokens` | `REST route` | `rest` | `lsp` | `POST` | `/lsp/semantic-tokens` | `body` | `body` | `200 LSP semantic tokens payload.` |  | `lsp.semantic_tokens` | `OpenAPI path /lsp/semantic-tokens` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /lsp/keywords` | `REST route` | `rest` | `lsp` | `GET` | `/lsp/keywords` | `query:game_root` | `none` | `200 HOI4 keyword dataset payload.` |  | `lsp.keywords` | `OpenAPI path /lsp/keywords` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /projects/inspections` | `REST route` | `rest` | `projects` | `GET` | `/projects/inspections` | `query:path` | `none` | `200 Project inspection contract.` |  |  | `OpenAPI path /projects/inspections` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /projects/templates` | `REST route` | `rest` | `authoring` | `GET` | `/projects/templates` | `query:path, query:template_id, query:family, query:kind, query:source, query:authoring_ready, query:diagnostic_code` | `none` | `200 Project authoring template payload.` |  | `module.templates` | `OpenAPI path /projects/templates` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /projects/authoring-path` | `REST route` | `rest` | `authoring` | `GET` | `/projects/authoring-path` | `query:path, query:kind, query:family, query:target_id, query:source_root` | `query:kind, query:family, query:target_id` | `200 Project authoring path payload.` |  | `module.authoring_path`, `collection.authoring_path` | `OpenAPI path /projects/authoring-path` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /projects/authoring-plan` | `REST route` | `rest` | `authoring` | `GET` | `/projects/authoring-plan` | `query:path, query:kind, query:family, query:target_id, query:source_root, query:profile` | `query:kind, query:family, query:target_id` | `200 Project authoring plan payload.` |  | `module.authoring_plan`, `collection.authoring_plan` | `OpenAPI path /projects/authoring-plan` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /projects/scaffold` | `REST route` | `rest` | `authoring` | `POST` | `/projects/scaffold` | `query:path, query:template_id, query:object_id, query:source_root, query:write, query:force, body` | `query:template_id, query:object_id` | `200 Project module scaffold payload.` |  | `module.create` | `OpenAPI path /projects/scaffold` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /projects/build` | `REST route` | `rest` | `build` | `POST` | `/projects/build` | `query:path, query:profile, query:emit_artifacts, query:emit_manifests, query:strict_metadata, query:family, query:module_id, query:collection_id, query:full_rebuild, query:sync_launcher_descriptor, query:parallelism` | `none` | `200 Build result payload.` | `400 Invalid project path or build options.` | `build.plan`, `build.emit` | `OpenAPI path /projects/build` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /projects/catalog` | `REST route` | `rest` | `catalog` | `GET` | `/projects/catalog` | `query:path` | `none` | `200 Catalog status payload.` |  |  | `OpenAPI path /projects/catalog` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /projects/catalog` | `REST route` | `rest` | `catalog` | `POST` | `/projects/catalog` | `query:path, query:profile, query:database` | `none` | `200 Catalog write payload.` |  | `catalog.write` | `OpenAPI path /projects/catalog` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `PUT /projects/catalog` | `REST route` | `rest` | `catalog` | `PUT` | `/projects/catalog` | `query:path, query:profile, query:database` | `none` | `200 Catalog refresh payload.` |  | `catalog.refresh` | `OpenAPI path /projects/catalog` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /projects` | `REST route` | `rest` | `projects` | `GET` | `/projects` | `query:path, query:game, query:title` | `none` | `200 Project view payload.` |  | `project.open`, `project.view` | `OpenAPI path /projects` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /projects` | `REST route` | `rest` | `projects` | `POST` | `/projects` | `query:path, query:project_id, query:title, query:game, query:force` | `query:path` | `200 Project create payload.` |  | `project.create` | `OpenAPI path /projects` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /projects/list` | `REST route` | `rest` | `projects` | `GET` | `/projects/list` | `query:project_paths, query:search_roots` | `none` | `200 Project registry payload.` |  | `project.list` | `OpenAPI path /projects/list` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /desktop/state` | `REST route` | `rest` | `desktop` | `GET` | `/desktop/state` | `query:project_path, query:project_paths, query:search_roots` | `none` | `200 Desktop state payload.` |  | `project.state` | `OpenAPI path /desktop/state` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /desktop/builds` | `REST route` | `rest` | `desktop` | `GET` | `/desktop/builds` | `query:project_root` | `none` | `200 Desktop build-runs payload.` |  | `build.runs` | `OpenAPI path /desktop/builds` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /desktop/builds` | `REST route` | `rest` | `desktop` | `POST` | `/desktop/builds` | `body` | `body` | `200 Desktop build run payload.` |  | `build.start` | `OpenAPI path /desktop/builds` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /desktop/builds/status` | `REST route` | `rest` | `desktop` | `GET` | `/desktop/builds/status` | `query:run_id` | `query:run_id` | `200 Desktop build run payload.` |  | `build.status` | `OpenAPI path /desktop/builds/status` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /desktop/builds/interrupt` | `REST route` | `rest` | `desktop` | `POST` | `/desktop/builds/interrupt` | `body` | `body` | `200 Desktop build run payload.` |  | `build.interrupt` | `OpenAPI path /desktop/builds/interrupt` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /desktop/open-path` | `REST route` | `rest` | `desktop` | `POST` | `/desktop/open-path` | `body` | `body` | `200 Desktop open-path payload.` |  |  | `OpenAPI path /desktop/open-path` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /desktop/select-project` | `REST route` | `rest` | `desktop` | `POST` | `/desktop/select-project` | `none` | `none` | `200 Desktop project-selection payload.` |  |  | `OpenAPI path /desktop/select-project` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /desktop/import-project-package` | `REST route` | `rest` | `desktop` | `POST` | `/desktop/import-project-package` | `none` | `none` | `200 Desktop project-package installation payload or null.` |  |  | `OpenAPI path /desktop/import-project-package` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /desktop/path-status` | `REST route` | `rest` | `desktop` | `GET` | `/desktop/path-status` | `query:path` | `query:path` | `200 Desktop path status payload.` |  |  | `OpenAPI path /desktop/path-status` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /desktop/hoi4-launch-readiness` | `REST route` | `rest` | `desktop` | `GET` | `/desktop/hoi4-launch-readiness` | `query:project_root` | `query:project_root` | `200 Desktop HOI4 launch-readiness payload.` |  |  | `OpenAPI path /desktop/hoi4-launch-readiness` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /desktop/app-config` | `REST route` | `rest` | `desktop` | `GET` | `/desktop/app-config` | `none` | `none` | `200 Desktop app config payload.` |  |  | `OpenAPI path /desktop/app-config` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `PUT /desktop/app-config` | `REST route` | `rest` | `desktop` | `PUT` | `/desktop/app-config` | `body` | `body` | `200 Desktop app config write status.` |  |  | `OpenAPI path /desktop/app-config` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /desktop/config-value` | `REST route` | `rest` | `desktop` | `GET` | `/desktop/config-value` | `query:key` | `query:key` | `200 Desktop config value payload.` |  |  | `OpenAPI path /desktop/config-value` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `PUT /desktop/config-value` | `REST route` | `rest` | `desktop` | `PUT` | `/desktop/config-value` | `body` | `body` | `200 Desktop config value payload.` |  |  | `OpenAPI path /desktop/config-value` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /desktop/llm/test` | `REST route` | `rest` | `desktop` | `POST` | `/desktop/llm/test` | `body` | `body` | `200 Desktop LLM route test payload.` |  |  | `OpenAPI path /desktop/llm/test` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /desktop/ai/chat` | `REST route` | `rest` | `desktop` | `POST` | `/desktop/ai/chat` | `body` | `body` | `200 Desktop AI chat payload.` |  | `ai.chat` | `OpenAPI path /desktop/ai/chat` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /desktop/ai/profiles` | `REST route` | `rest` | `desktop` | `GET` | `/desktop/ai/profiles` | `query:project_root` | `none` | `200 Desktop AI chat profile payload.` |  | `ai.profiles` | `OpenAPI path /desktop/ai/profiles` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `PUT /desktop/ai/profiles/{profile_id}` | `REST route` | `rest` | `desktop` | `PUT` | `/desktop/ai/profiles/{profile_id}` | `path:profile_id, body` | `path:profile_id, body` | `200 Desktop AI chat profile payload.` |  | `ai.profile.write` | `OpenAPI path /desktop/ai/profiles/{profile_id}` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `DELETE /desktop/ai/profiles/{profile_id}` | `REST route` | `rest` | `desktop` | `DELETE` | `/desktop/ai/profiles/{profile_id}` | `path:profile_id, query:project_root` | `path:profile_id` | `200 Desktop AI chat profile payload.` |  | `ai.profile.reset` | `OpenAPI path /desktop/ai/profiles/{profile_id}` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /projects/browser` | `REST route` | `rest` | `projects` | `GET` | `/projects/browser` | `query:path, query:profile, query:kind, query:family, query:module_id, query:collection_id` | `none` | `200 Project browser payload.` |  | `project.browser` | `OpenAPI path /projects/browser` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /projects/find` | `REST route` | `rest` | `projects` | `GET` | `/projects/find` | `query:path` | `none` | `200 Project discovery payload.` |  | `project.find` | `OpenAPI path /projects/find` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `PATCH /projects/rename` | `REST route` | `rest` | `projects` | `PATCH` | `/projects/rename` | `query:path, query:title` | `query:title` | `200 Project rename payload.` |  | `project.rename` | `OpenAPI path /projects/rename` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `PATCH /projects/language` | `REST route` | `rest` | `projects` | `PATCH` | `/projects/language` | `query:path, query:preferred_language, query:write, query:plan_hash` | `query:preferred_language` | `200 Guarded project language plan or apply payload.` |  | `project.language` | `OpenAPI path /projects/language` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `PATCH /projects/modules/rename` | `REST route` | `rest` | `modules` | `PATCH` | `/projects/modules/rename` | `query:path, query:module_id, query:object_id, query:title, query:source_root` | `query:module_id, query:object_id` | `200 Module rename payload.` |  | `module.rename` | `OpenAPI path /projects/modules/rename` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `DELETE /projects/modules/remove` | `REST route` | `rest` | `modules` | `DELETE` | `/projects/modules/remove` | `query:path, query:module_id, query:source_root, query:write` | `query:module_id` | `200 Module remove payload.` |  | `module.remove` | `OpenAPI path /projects/modules/remove` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /projects/modules/file` | `REST route` | `rest` | `modules` | `GET` | `/projects/modules/file` | `query:path, query:module_id, query:relative_path, query:source_root, query:encoding` | `query:module_id, query:relative_path` | `200 Module file payload.` |  | `module.file` | `OpenAPI path /projects/modules/file` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `PATCH /projects/modules/file` | `REST route` | `rest` | `modules` | `PATCH` | `/projects/modules/file` | `query:path, query:module_id, query:relative_path, query:source_root, query:create, query:encoding, body` | `query:module_id, query:relative_path, body` | `200 Module file payload.` |  | `module.edit` | `OpenAPI path /projects/modules/file` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /projects/collections/scaffold` | `REST route` | `rest` | `collections` | `POST` | `/projects/collections/scaffold` | `query:path, query:template_id, query:collection_id, query:source_root, query:write, query:force, query:plan_hash, body` | `query:template_id, query:collection_id` | `200 Guarded collection scaffold plan or apply payload.` |  | `collection.scaffold` | `OpenAPI path /projects/collections/scaffold` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `POST /projects/collections` | `REST route` | `rest` | `collections` | `POST` | `/projects/collections` | `query:path, query:family, query:collection_id, query:source_root, query:write, query:force, body` | `query:family, query:collection_id` | `200 Collection create payload.` |  | `collection.create` | `OpenAPI path /projects/collections` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `DELETE /projects/collections` | `REST route` | `rest` | `collections` | `DELETE` | `/projects/collections` | `query:path, query:collection_id, query:family, query:source_root, query:write, query:plan_hash` | `query:collection_id` | `200 Collection remove payload.` |  | `collection.remove` | `OpenAPI path /projects/collections` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `PATCH /projects/collections/rename` | `REST route` | `rest` | `collections` | `PATCH` | `/projects/collections/rename` | `query:path, query:collection_id, query:target_id, query:family, query:source_root` | `query:collection_id, query:target_id` | `200 Collection rename payload.` |  | `collection.rename` | `OpenAPI path /projects/collections/rename` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /projects/collections/file` | `REST route` | `rest` | `collections` | `GET` | `/projects/collections/file` | `query:path, query:collection_id, query:relative_path, query:family, query:source_root, query:encoding` | `query:collection_id, query:relative_path` | `200 Collection file payload.` |  | `collection.file` | `OpenAPI path /projects/collections/file` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `PATCH /projects/collections/file` | `REST route` | `rest` | `collections` | `PATCH` | `/projects/collections/file` | `query:path, query:collection_id, query:relative_path, query:family, query:source_root, query:create, query:encoding, body` | `query:collection_id, query:relative_path, body` | `200 Collection file payload.` |  | `collection.edit` | `OpenAPI path /projects/collections/file` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
| `GET /projects/inspect` | `REST route` | `rest` | `inspections` | `GET` | `/projects/inspect` | `query:path, query:kind` | `query:kind` | `200 Project inspection payload.` |  | `project.inspect`, `module.list`, `module.view`, `module.source_slots`, `module.sources`, `collection.list`, `collection.view`, `collection.source_slots`, `collection.sources`, `build.summary`, `build.manifests`, `build.artifacts`, `build.localization`, `build.assets`, `build.sprites`, `build.diagnostics`, `build.source_map`, `build.dependencies`, `build.graph`, `build.explain`, `build.families`, `catalog.preview`, `catalog.query` | `OpenAPI path /projects/inspect` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_rest_api_table_lists_openapi_routes` |
