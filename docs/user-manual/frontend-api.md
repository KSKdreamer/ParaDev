# Frontend API Contract

## English

This page is for GUI, importer, REST, MCP, VS Code, and desktop agents that need a stable list of ParaDev operations. The canonical machine-readable list is `get_frontend_api_contract()`:

```python
from paradev.sdk import get_frontend_api_contract

contract = get_frontend_api_contract()
for operation in contract["operations"]:
    print(operation["id"], operation["status"])
```

For the full generated operation table, read [Frontend API Reference](frontend-api-reference.md). It is generated from the same SDK contract with `rtk uv run paradev frontend-api --markdown`, so it should be regenerated whenever a frontend-visible operation row changes. The contract also includes `summary` with operation, group, status, read/write, workspace-section, and SDK/CLI/REST/MCP/LSP binding-coverage counts; the generated reference renders those coverage fields as a surface matrix and renders `index["binding"]` as a surface-call table, so use both as the quick maintenance audit before adding GUI actions or docs. Clients that need group/status operation-id lists should use Python `get_frontend_api_group_operation_ids(...)` / `get_frontend_api_status_operation_ids(...)` or TypeScript `getFrontendApiGroupOperationIds(...)` / `getFrontendApiStatusOperationIds(...)` instead of scanning rows or reading raw indexes; clients that need read/write operation-id lists should use Python `get_frontend_api_mode_operation_ids(...)` or TypeScript `getFrontendApiModeOperationIds(...)`. Python clients should use `get_frontend_api_binding_lookup(...)`, `get_frontend_api_binding_operation_ids(...)`, `get_frontend_api_binding_index(...)`, `build_frontend_api_rest_index_key(...)`, and `get_frontend_api_rest_operation_ids(...)` when a surface call key or whole adapter surface must map back to stable operation ids. Clients that need every operation id for a surface should use Python `get_frontend_api_surface_operation_ids(...)` or TypeScript `getFrontendApiSurfaceOperationIds(...)` instead of scanning rows; clients that need every operation id returning one payload schema should use Python `get_frontend_api_payload_operation_ids(...)` or TypeScript `getFrontendApiPayloadOperationIds(...)`; clients that need every operation id in one workspace section should use Python `get_frontend_api_workspace_section_operation_ids(...)` or TypeScript `getFrontendApiWorkspaceSectionOperationIds(...)`. TypeScript clients should use the desktop helper at `apps/desktop/src/data/frontendApi.ts`; it wraps the generated contract at `apps/desktop/src/generated/frontendApi.ts`, rebuilt with `rtk uv run paradev frontend-api --typescript`, and exposes operation id, group id, status, read/write mode, workspace-section, workspace-action, selected-action detail, selected-action panel state, form-control, binding, binding-index, group-index, status-index, mode-index, surface-index, payload-index, workspace-section-index, input, default-value, option-source, option-request, option-result, normalize result, REST-plan result, REST-execution result, action-run state, endpoint, JSON-request, and response-payload types plus lookup helpers such as `getFrontendApiAction(...)`, `getFrontendApiActionDetail(...)`, `getFrontendApiActionPanelState(...)`, `getFrontendApiFormControls(...)`, `getFrontendApiFormControlKind(...)`, `getFrontendApiFormValuesWithDefaults(...)`, `getFrontendApiFormOptionRequests(...)`, `resolveFrontendApiFormOptionRequest(...)`, `resolveFrontendApiNormalizeRequest(...)`, `resolveFrontendApiRestPlanRequest(...)`, `resolveFrontendApiRestExecutionRequest(...)`, `getFrontendApiActionRunState(...)`, `getFrontendApiSectionActions(...)`, `getFrontendApiDefaultSectionAction(...)`, `getFrontendApiBindings(...)`, `getFrontendApiRestBinding(...)`, `getFrontendApiBindingOperationIds(...)`, `getFrontendApiRestOperationIds(...)`, `getFrontendApiGroupOperationIds(...)`, `getFrontendApiStatusOperationIds(...)`, `getFrontendApiModeOperationIds(...)`, `getFrontendApiSurfaceOperationIds(...)`, `getFrontendApiPayloadOperationIds(...)`, `getFrontendApiWorkspaceSectionOperationIds(...)`, `getFrontendApiInputs(...)`, `getFrontendApiRequiredInputNames(...)`, `getFrontendApiDefaultValues(...)`, `getFrontendApiOptionSourceInputs(...)`, `buildFrontendApiActionUrl(...)`, `buildFrontendApiOptionsRequest(...)`, `buildFrontendApiNormalizeRequest(...)`, `buildFrontendApiRestPlanRequest(...)`, `buildFrontendApiRestIndexKey(...)`, and `buildFrontendApiRestExecutionRequest(...)`.

Use `get_frontend_api_index_catalog()` or the generated Index Catalog section when deciding which raw `contract["index"]` path and helper should back a grouped API table.

The generated Surface Index table renders `contract["index"]["surface"]` as operation-id lists for SDK, CLI, REST, MCP, LSP, and frontend-local/unbound rows.

The generated Group Binding Summary Index table lists concrete SDK, CLI, REST, MCP, and LSP binding keys by operation group, so feature-level API surfaces can be audited without scanning every binding row.

The generated REST Route Index table renders REST bindings as method/path/query rows, so GUI clients and OpenAPI audits do not need to parse human-readable `rest` strings. For route-level OpenAPI summaries, parameter/body requirements, response descriptions, and frontend operation reverse mapping, read [REST API Reference](rest-api-reference.md).

The generated REST Request Planner Index table renders each REST-bound operation's static query defaults, path parameters, and JSON body fields, so GUI clients can audit request planning without running the operation.

The generated Workspace Section REST Summary Index table summarizes REST planner coverage by workspace section before the lower-level REST query/path/body field rows.

The generated Group REST Summary Index table summarizes REST planner coverage by operation group before the lower-level REST query/path/body field rows.

The generated REST Static Query Index table renders fixed query parameters declared by REST bindings, including the rendered value and JSON value type for REST client audits.

The generated REST Dynamic Query Field Index table renders frontend inputs that become REST query parameters at request-plan time, including static defaults they can override when explicitly submitted.

The generated REST Path Parameter Index table renders each frontend input routed to a REST path parameter, including alias-aware parameter names and normalizer targets for REST client audits.

The generated REST Body Field Index table renders each frontend input routed to a REST JSON body field, including alias-aware body names and normalizer targets for REST client audits.

The generated SDK Call Index table renders `contract["index"]["binding"]["sdk"]` as SDK-call-to-operation rows for Python SDK audits.

The generated SDK Call Input Index table renders SDK-bound operation inputs with required/default state, target bucket, and adapter-side alias for Python SDK audits.

The generated MCP Tool Index table renders `contract["index"]["binding"]["mcp"]` as tool-to-operation rows for adapter audits.

The generated MCP Tool Input Index table renders MCP-bound operation inputs with required/default state, target bucket, and adapter-side alias for MCP adapter audits.

The generated CLI Command Index table renders `contract["index"]["binding"]["cli"]` as command-to-operation rows for adapter audits.

The generated CLI Command Input Index table renders CLI-bound operation inputs with required/default state, target bucket, and adapter-side alias for command adapter audits.

The generated LSP Method Index table renders `contract["index"]["binding"]["lsp"]` as method-to-operation rows for VS Code and language-server audits.

The generated LSP Method Input Index table renders LSP-bound operation inputs with required/default state, target bucket, and adapter-side alias for VS Code and language-server audits.

The generated Confirmation Index table renders required `execution.confirmation` rows from the SDK-owned workspace actions, so GUI shells can audit mutation scope, style, and confirm fields without scanning every action.

The generated Group Execution Summary Index table summarizes workspace action execution policy by operation group before the detailed action-level execution rows.

The generated Workspace Section Execution Summary Index table summarizes workspace action execution policy by workspace section before the detailed action-level execution rows.

The generated Workspace Action Execution Index table renders every SDK-owned workspace action's execution kind, default surface, available surfaces, value requirement, state scope, normalizer schema, and REST planner schema.

The generated Group Confirmation Summary Index table summarizes confirmation-gated workspace actions by operation group before the workspace-section and action-level confirmation rows.

The generated Workspace Section Confirmation Summary Index table summarizes confirmation-gated actions by workspace section before the detailed action-level confirmation rows.

The generated Group Option Source Summary Index table summarizes dynamic option-source dependencies by operation group before the detailed field-level option source rows.

The generated Workspace Section Mode Status Index table summarizes read/write mode and implementation status coverage by workspace section, so GUI maintainers can audit mutating and frontend-local action placement without scanning every action.

The generated Group Mode Status Index table summarizes read/write mode and implementation status coverage by operation group.

The generated Workspace Section Payload Coverage Index table summarizes response payload schemas by workspace section and counts untyped actions separately.

The generated Group Payload Coverage Index table summarizes response payload schemas by operation group and counts untyped operations separately.

The generated Workspace Section Surface Coverage Index table summarizes callable surface coverage by workspace section, including frontend-local actions, unbound actions, and default-surface distribution.

The generated Workspace Section Binding Summary Index table lists concrete SDK, CLI, REST, MCP, and LSP binding keys by workspace section before the form-focused section summaries.

The generated Workspace Section Form Summary Index table summarizes each SDK-owned workspace section's action form footprint, including action counts, input counts, required fields, defaults, aliases, option sources, constraints, and control-kind counts.

The generated Workspace Section Control Summary Index table summarizes SDK-derived form control kinds by workspace section before the detailed field-level control rows.

The generated Group Control Summary Index table summarizes SDK-derived form control kinds by operation group before the detailed field-level control rows.

The generated Workspace Section Option Source Summary Index table summarizes dynamic option-source dependencies by workspace section before the detailed field-level option source rows.

The generated Workspace Section Input Target Summary Index table summarizes input target buckets by workspace section, including parameter fields, project-context fields, selectors, projections, and aliases.

The generated Group Input Target Summary Index table summarizes input target buckets by operation group before the detailed field-level input target rows.

The generated Workspace Section Validation Summary Index table summarizes choice and minimum constraints by workspace section before the detailed field-level constraint rows.

The generated Group Validation Summary Index table summarizes choice and minimum constraints by operation group before the detailed field-level constraint rows.

The generated Workspace Section Default Summary Index table summarizes defaulted input fields by workspace section before the detailed field-level default rows.

The generated Group Default Summary Index table summarizes defaulted input fields by operation group before the detailed field-level default rows.

The generated Workspace Section Required Summary Index table summarizes required input fields by workspace section before the detailed field-level required-input rows.

The generated Group Required Summary Index table summarizes required input fields by operation group before the detailed field-level required-input rows.

The generated Workspace Section Alias Summary Index table summarizes frontend-to-SDK input aliases by workspace section before the detailed field-level alias rows.

The generated Group Alias Summary Index table summarizes frontend-to-SDK input aliases by operation group before the detailed field-level alias rows.

The generated Option Source Index table renders `operation.inputs[*].option_source` rows so GUI shells can audit dynamic form dependencies, provider operations, forwarded fields, and fixed filters without scanning every operation.

The generated Option Provider Index table groups those dynamic option fields by provider operation, so provider APIs and their dependent UI fields can be audited from the inverse direction.

The generated Input Field Index table renders every declared input field with type, required/default state, finite choices, frontend-to-SDK alias, and option-source provider for form audits.

The generated Group Form Summary Index table summarizes form footprint by operation group, including input counts, required fields, defaults, aliases, option sources, constraints, and control-kind counts.

The generated Operation Form Summary Index table summarizes each operation's form footprint across input counts, required fields, defaults, aliases, option sources, constraints, and control kinds.

The generated Form Control Index table renders every SDK-derived control kind, including select fields from static choices and combobox fields from dynamic option sources.

The generated Required Input Index table renders every field that must be supplied before execution, including its normalizer target bucket, adapter-side alias, and option-source provider.

The generated Input Default Index table renders every SDK-owned form default with its normalizer target bucket and adapter-side alias, so GUI initial state can be audited without scanning the full input table.

The generated Input Constraint Index table renders every finite choice list and numeric lower bound enforced by the normalizer, so UI controls and validators can be audited without opening each form schema.

The generated Input Target Index table renders every declared input field's normalizer target bucket and adapter-side alias, so SDK, REST, and GUI clients can audit submitted-value routing without opening each form payload.

The generated Input Alias Index table renders only fields whose submitted frontend name is remapped before adapter execution, so alias-sensitive REST and SDK calls can be audited without scanning every input target row.

When the caller already knows the stable operation id or group id, use the SDK lookup helpers instead of scanning the list manually. GUI shells that need a maintained navigation/action layout should use `get_frontend_api_workspace(...)`; it groups the same operation ids into project switcher, project browser, authoring, source editor, build, catalog, and surface-contract sections. Each workspace action row uses `paradev.sdk.frontend-api.action.v1` and carries the operation payload schema, callable `bindings`, `execution.default_surface`, `execution.available_surfaces`, `execution.confirmation`, `form_schema`, `normalizer_schema`, and `rest_request_schema` hints derived from the canonical operation row. When rendering or inspecting one selected action, use `get_frontend_api_action(...)`; it combines the canonical operation row, workspace action, section membership, derived form, option-source summary, bindings, and execution hints into one payload. For forms, panels, and action dialogs, use `get_frontend_api_form(...)`; it derives SDK-owned labels/descriptions, required fields, defaults, aliases, target buckets, controls, finite choices, numeric bounds, option sources, and a small JSON Schema from the same operation row. Use `resolve_frontend_api_options(...)` when a field has `option_source`; it returns UI-ready `value`, `label`, `details`, and source rows by executing the provider through the SDK. Python adapters can then use `normalize_frontend_api_inputs(...)` to turn submitted form state into project, parameter, selector, and projection buckets. REST clients can call `plan_frontend_api_rest_request(...)` to split those submitted values into method, path, query, and JSON body:

TypeScript shell code that only needs generated field render state should use `getFrontendApiFormControls(...)`; it derives control kind, default-value preview, submitted-value preview, choice/option-source hints, and disabled reasons for missing option-source requirements from the same operation row. Keep local submitted form values in the shell, then pass them through `getFrontendApiFormValuesWithDefaults(...)` before rendering dependent state. Use `getFrontendApiFormOptionRequests(...)` to plan which option-source calls are available and to build each ready `{ url, init }` request through `buildFrontendApiOptionsRequest(...)`; then call `resolveFrontendApiFormOptionRequest(...)` for each available request to get `ready`, `unavailable`, or `error` state plus the returned option payload. Pass those results back into `getFrontendApiFormControls(operation_id, values, optionResults)` so static `choices` and SDK-resolved option payloads become the same `FrontendApiFormControlOption` rows for select controls. Do not execute option providers, duplicate requirement checks, or call raw `fetch` directly in React components. Panels that need raw generated field metadata should use `frontendApiInputOperations`, `getFrontendApiInputs(...)`, `getFrontendApiRequiredInputNames(...)`, `getFrontendApiDefaultValues(...)`, and `getFrontendApiOptionSourceInputs(...)` from `apps/desktop/src/data/frontendApi.ts` instead of scanning `operation.inputs` or maintaining local form defaults. TypeScript clients calling frontend API meta endpoints should use `frontendApiEndpointPaths`, `buildFrontendApiDiscoveryUrl(...)`, `buildFrontendApiActionUrl(...)`, `buildFrontendApiOptionsUrl(...)`, `buildFrontendApiNormalizeUrl(...)`, and `buildFrontendApiRestRequestUrl(...)`, `buildFrontendApiBindingLookupUrl(...)`; for JSON POST meta endpoints, use `buildFrontendApiOptionsRequest(...)`, `buildFrontendApiNormalizeRequest(...)`, and `buildFrontendApiRestPlanRequest(...)` to create `{ url, init }` fetch inputs from submitted form values, then use `resolveFrontendApiNormalizeRequest(...)` and `resolveFrontendApiRestPlanRequest(...)` for `ready` or `error` result state. Once a REST-plan payload is ready and `execution.confirmation` is satisfied, desktop code should call `buildFrontendApiRestExecutionRequest(plan)` and `resolveFrontendApiRestExecutionRequest(request)` to execute the planned target request and render `loading`, `ready`, or `error` result state. Set `VITE_PARADEV_FRONTEND_API_BASE_URL` when a Vite shell should call a running REST bridge; without it, the helper reports bridge-unavailable state instead of emitting browser 404 errors. The SDK still owns option resolution, normalization, REST request planning, and confirmation policy, while the helper owns browser request shaping and bridge-unavailable handling.

```python
from paradev.sdk import (
    get_frontend_api_binding_lookup,
    get_frontend_api_action,
    get_frontend_api_form,
    get_frontend_api_group,
    get_frontend_api_operation,
    get_frontend_api_workspace,
    normalize_frontend_api_inputs,
    plan_frontend_api_rest_request,
    resolve_frontend_api_options,
)

workspace = get_frontend_api_workspace()
source_editor = next(section for section in workspace["sections"] if section["id"] == "source-editor")
module_edit_action = next(action for action in source_editor["actions"] if action["operation_id"] == "module.edit")
module_list = get_frontend_api_operation("module.list")
module_group = get_frontend_api_group("modules")
module_create_detail = get_frontend_api_action("module.create")
module_edit_form = get_frontend_api_form("module.edit")
module_edit_inputs = normalize_frontend_api_inputs(
    "module.edit",
    {"module_id": "modifier/example", "relative_path": "def.txt", "text": "modifier = { value = 1 }"},
)
print(workspace["sections"][0]["id"], module_list["rest"], module_group["operation_ids"])
print(module_edit_form["required"], module_edit_form["defaults"])
print(module_edit_form["fields"][3]["label"], module_edit_form["fields"][3]["description"])
print(module_edit_inputs["project"], module_edit_inputs["parameters"])
print(module_edit_action["execution"]["default_surface"])
print(module_create_detail["sections"], module_create_detail["option_fields"])
print(get_frontend_api_binding_lookup("rest", "GET /projects/inspect?kind=modules")["operation_ids"])
print(resolve_frontend_api_options("module.create", "template_id", {"path": "demos/assets/projects/minimal"})["options"][0])
print(plan_frontend_api_rest_request("module.edit", module_edit_inputs["values"])["body"])
```

For `module.create`, the selected template row owns the generic creation form for the eventual scaffold. Use its `form.fields` to render template-specific inputs such as `title`, `description`, or `image`; use its `default_assets` for optional preview and override controls. Those default assets are family-level metadata and are not written to the new module unless the user explicitly authors an instance asset.

The same contract is exposed through:

```bash
rtk uv run paradev frontend-api --json
rtk uv run paradev frontend-api --operation module.list --json
rtk uv run paradev frontend-api --group modules --json
rtk uv run paradev frontend-api --workspace --json
rtk uv run paradev frontend-api --operation module.create --action --json
rtk uv run paradev frontend-api --operation module.edit --form --json
rtk uv run paradev frontend-api --binding-surface rest --binding-key 'GET /projects/inspect?kind=modules' --json
rtk uv run paradev frontend-api --sdk-cli-markdown > docs/user-manual/sdk-cli-reference.md
rtk uv run paradev frontend-api --typescript > apps/desktop/src/generated/frontendApi.ts
rtk uv run paradev frontend-api --operation module.create \
  --option-field template_id \
  --values-json '{"path":"demos/assets/projects/minimal"}' \
  --json
rtk uv run paradev frontend-api --operation build.artifacts \
  --values-json '{"path":"/workspace/mod","artifact_path":"common/modifiers/test.txt"}' \
  --json
rtk uv run paradev frontend-api --operation module.edit \
  --values-json '{"path":"/workspace/mod","module_id":"modifier/example","relative_path":"def.txt","text":"modifier = { value = 1 }"}' \
  --rest-request \
  --json
```

REST/OpenAPI exposes `GET /frontend-api`, with optional `operation_id` and `group_id` query selectors that mirror the SDK lookup helpers; `GET /frontend-api/workspace` returns the same workspace projection as `get_frontend_api_workspace(...)`; `GET /frontend-api/action?operation_id=...` returns the same selected-action payload as `get_frontend_api_action(...)`; `form=true` with `operation_id` returns the same derived form contract as `get_frontend_api_form(...)`. `POST /frontend-api/options?operation_id=...&field_name=...` accepts the current form values and returns the same option payload as `resolve_frontend_api_options(...)`. `POST /frontend-api/normalize?operation_id=...` accepts one JSON object of submitted form values and returns the same normalized payload as `normalize_frontend_api_inputs(...)`. `POST /frontend-api/rest-request?operation_id=...` returns the matching REST method, path, query, and JSON body plan without executing the target operation. `GET /frontend-api/binding?binding_surface=...&binding_key=...` returns the same reverse-lookup payload as `get_frontend_api_binding_lookup(...)`. Each OpenAPI operation that backs frontend rows also includes `x-paradev-frontend-api-operation-ids`, so codegen can map shared routes such as `GET /projects`, `GET /projects/inspect`, and `POST /projects/build` back to their stable operation ids. The MCP surface advertises the read-only `frontend_api` tool with the same selector names, and the canonical `surface.frontend_api` row lists those names under `selectors`. Treat the contract as the frontend table of contents: implemented rows can be called today, `planned` rows are intentionally not stable behavior yet, and `frontend-local` rows are UI workspace state rather than SDK project mutation.

Each operation row keeps human-readable surface strings such as `rest` and `cli`, and also publishes a machine-readable `bindings` object when a surface exists. Use `bindings.rest.method`, `bindings.rest.path`, and `bindings.rest.query` for REST clients; use `bindings.cli.command`, `bindings.mcp.tool`, `bindings.lsp.method`, and `bindings.sdk.call` for adapters and generated clients. The contract also builds `contract["index"]["binding"]`, keyed by surface and call key, so a client can ask which operation ids belong to a shared route, tool, command, or LSP method. Python clients should use `get_frontend_api_binding_lookup(...)`, `get_frontend_api_binding_operation_ids(...)`, `get_frontend_api_binding_index(...)`, `build_frontend_api_rest_index_key(...)`, and `get_frontend_api_rest_operation_ids(...)`; CLI clients should use `frontend-api --binding-surface ... --binding-key ...`; REST clients can call `GET /frontend-api/binding?binding_surface=...&binding_key=...`; TypeScript clients should use `frontendApiBindingIndex`, `getFrontendApiBindingOperationIds(...)`, `buildFrontendApiRestIndexKey(...)`, and `getFrontendApiRestOperationIds(...)` from `apps/desktop/src/data/frontendApi.ts` for that reverse lookup instead of reaching into raw generated JSON. Static CLI and MCP contracts mirror their slices as `get_cli_contract()["frontend_operation_ids"]` and `get_mcp_contract()["frontend_operation_ids"]`; those contracts should source the copied surface map through `get_frontend_api_binding_index(...)`. The Python architecture gate `test_frontend_api_contract_indexes_every_surface_binding_and_openapi_annotation` keeps every declared binding present in that reverse index and every REST binding mirrored by the matching OpenAPI `x-paradev-frontend-api-operation-ids` annotation.

Fields that need project-derived dropdowns or autocomplete may include `option_source`, using schema `paradev.sdk.frontend-api.option-source.v1`. The source row points to another canonical operation id, the list path inside that provider payload, value/label/detail fields, required context fields, forwarded form fields, and optional fixed filters. For example, `module.create.template_id` points to `module.templates` at `templates`, `source_root` points to `module.templates` at `source_roots`, `family` points to `build.families`, existing `module_id` and `collection_id` fields point to `module.list` and `collection.list`, artifact fields point to `build.artifacts`, and diagnostic-code fields point to `build.diagnostics`. UI code should call `resolve_frontend_api_options(...)`, CLI `frontend-api --operation ... --option-field ...`, or REST `POST /frontend-api/options`; do not hardcode template ids, family ids, module ids, collection ids, artifact paths, or diagnostic codes in the frontend. When required context fields such as `module_id` are missing, the resolver returns `available=false` with `missing_requirements` so the UI can disable that control until the user fills its dependencies.

Project-management rows list their frontend input fields under `inputs`. `project.create` declares `path`, optional `project_id`, optional `title`, `game` defaulting to `hoi4`, and `force` defaulting to `false`; `project.find`, `project.open`, `project.view`, and `project.browser` default `path` to `"."`; `project.list` accepts optional `project_paths` and `search_roots` arrays for project switchers; `project.state` adds optional `project_path` for the active workspace; `project.browser` accepts optional `profile`, `kind`, `family`, `module_id`, and `collection_id` filters for a read-only workspace tree, with `kind` choices of `module` or `collection`; `project.inspect` exposes generic `path` and SDK inspection `kind` fields for dispatcher clients, while filter-heavy panels should prefer concrete rows such as `module.list` or `build.graph`; `project.rename` requires `title`; frontend-local `project.activate` requires `project_id`.

Implemented rows that take no canonical GUI-submitted values publish `inputs=[]` explicitly. `project.config` is still a CLI-owned configuration namespace rather than a general settings form, and `surface.openapi`, `surface.cli_contract`, `surface.mcp_contract`, and `surface.lsp_contract` are form-less contract export actions; frontend clients should render them as no-input actions instead of treating missing fields as a contract gap.

Module and collection rows use the same `inputs` convention. Read panels list `path` plus inspection filters; `module.templates` lists authoring templates and source roots; `module.view` requires `module_id`; and `collection.view` requires `collection_id`. Authoring rows carry a default `kind` of `module` or `collection` for the shared authoring endpoints. Source-slot status fields advertise `satisfied`, `missing`, `empty`, and `diagnostic`; source inventory status fields advertise `loaded` and `diagnostic`; collection source views advertise `owner_kind` choices of `module` or `collection`. Mutation rows expose confirmation booleans such as `write`, `create`, and `force` with safe `false` defaults, while body-like fields such as `text`, `values`, and `metadata` are listed directly on the operation row.

PDX rows use saved-file inputs: `pdx.parse`, `pdx.tokens`, `pdx.dump`, and `pdx.format` require `path`, and formatting defaults to tab indentation, comment retention, and `write=false`. LSP rows use unsaved editor-buffer inputs: diagnostics, symbols, hover, and formatting require `text`; hover also requires zero-based `line` and `character`, both with `minimum=0`; completion requires the same zero-based position and accepts optional zero-based `offset` so editor adapters can avoid start-of-file scans in large buffers; formatting defaults match the PDX formatter.

Build rows use project `path`, optional `profile`, and row-specific filters. `build.plan`, `build.emit`, and `build.diagnostics` also expose optional `strict_metadata`; omit it to inherit `paradev.build.strict_metadata` from `CM_PARADEV`, or set it explicitly when a GUI, importer, or CI panel should override unknown module or collection metadata keys as warnings versus blocking diagnostics. `build.emit` keeps `emit_artifacts` and `emit_manifests` defaulted to `false`; read-only build rows expose the same filters as their SDK inspection methods. `build.start` is the desktop lifecycle row for starting one build run through `POST /desktop/builds`; it requires `project_root` and accepts `mode`, `profile`, `strict_metadata`, `parallelism`, and `target`. `build.runs` accepts an optional `project_root` filter and returns every active run plus the newest 256 terminal runs known to the current native app process as `paradev.desktop.build-runs.v1`; an exact lookup for an evicted terminal id returns `idle`. `build.status` and `build.interrupt` use `run_id` and return the same `paradev.desktop.build-run.v1` payload as the desktop facade. `build.artifacts` publishes `artifact_path` with `maps_to="path"` because the frontend still needs project `path` for the loaded workspace. Build rows that filter output location advertise `target_root` choices of `output` or `build`, and build diagnostics advertise `severity` choices of `error` or `warning`. Catalog rows use `path`, `profile`, optional `database`, and query filters; `catalog.write` maps to REST `POST /projects/catalog`, and `catalog.refresh` maps to REST `PUT /projects/catalog`. `surface.frontend_api` lists `operation_id`, `group_id`, and the `form=false` projection flag as inputs. `surface.frontend_api.action` returns one operation's selected-action detail, including workspace section ids, the derived form when present, and option-source field names. `surface.frontend_api.options` resolves one field's dynamic choices from the same submitted values used by forms. `surface.frontend_api.normalize` is the adapter row for turning submitted values into SDK buckets through Python, CLI, or REST, and `surface.frontend_api.rest_request` plans one REST call from the same submitted values.

Use raw `inputs` when maintaining the operation list. Use `workspace["sections"]` when rendering the outer app navigation: the section ids and action `operation_id` values are SDK-owned and should be the UI's stable keys. In TypeScript shell code, import `frontendApiWorkspaceActions`, `getFrontendApiAction(...)`, `getFrontendApiActionDetail(...)`, `getFrontendApiFormControls(...)`, `getFrontendApiSectionActions(...)`, and `getFrontendApiDefaultSectionAction(...)` from `apps/desktop/src/data/frontendApi.ts` instead of scanning the generated JSON or keeping a second action registry. Use `get_frontend_api_action(...)` or the generated-contract mirror `getFrontendApiActionDetail(...)` when rendering one selected action detail instead of stitching workspace, form, bindings, and option-source data in component code. Use `getFrontendApiFormControls(...)` for read-only/default form render state and disabled messages before the user supplies all option-source requirements. Use each action's `execution` object to decide the default call path and confirmation policy. GUI shells should normally use `default_surface="rest"` with `getFrontendApiRestBinding(...)`, the embedded REST binding, or the REST planner; `execution.confirmation.required` tells a Run control whether it must stop for explicit user confirmation, and `confirm_fields` lists safe boolean fields such as `write`, `force`, `create`, `emit_artifacts`, or `emit_manifests` that should stay false until the user opts in. SDK scripts can still choose `bindings.sdk`; VS Code/LSP adapters can choose `bindings.lsp`; `frontend-local` actions such as `project.activate` stay in app workspace state and publish no callable SDK/REST binding. Use the derived form contract when rendering UI: `fields` preserves operation order, each field has SDK-owned `label` and `description` text, each field has a `target` bucket, `required` is a plain list for validation, `defaults` is ready for initial form state, `choices` drives select controls, `option_source` points to SDK-owned dynamic choices, `minimum` carries numeric lower bounds, `aliases` maps frontend-safe names like `artifact_path` back to SDK filter names, and `json_schema` is available for adapters that already speak JSON Schema. Use `getFrontendApiBindings(...)` when deciding which non-REST surface call to make; do not parse human-readable `rest`, `cli`, `sdk`, `mcp`, or `lsp` strings. Use the normalizer when executing the action from submitted state: Python calls `normalize_frontend_api_inputs(...)`, CLI calls `frontend-api --operation ... --values-json ...`, REST calls `POST /frontend-api/normalize?operation_id=...`, and TypeScript can call `buildFrontendApiNormalizeRequest(...)` to build that JSON request. The normalizer enforces unsupported fields, required fields, declared choices, and numeric lower bounds before the adapter calls SDK or REST. Use the REST planner when the next step is an HTTP call: Python calls `plan_frontend_api_rest_request(...)`, CLI adds `--rest-request`, REST calls `POST /frontend-api/rest-request?operation_id=...`, and TypeScript can call `buildFrontendApiRestPlanRequest(...)`. REST plan ready after confirmation should be executed through `buildFrontendApiRestExecutionRequest(...)` and `resolveFrontendApiRestExecutionRequest(...)`; components should not hand-maintain REST execution mappers. In normalized input payloads, project-backed rows keep loaded workspace fields under `project`, action parameters under `parameters`, frontend API selectors under `selectors`, and operation projections such as `form` under `projections`.

Desktop TypeScript sidebars and tabs should derive from `frontendApiWorkspaceSections`; selected action rows should still use `frontendApiWorkspaceActions`, `getFrontendApiSectionActions(...)`, `getFrontendApiDefaultSectionAction(...)`, and `getFrontendApiRequiredInputNames(...)`. Selected-action summary panels should use `getFrontendApiActionDetail(...)` for operation summary, execution surfaces, generated fields, defaults, option-source field names, and `execution.confirmation`. Selected-action form panels should use `getFrontendApiFormControls(...)` for read-only control state, default previews, and missing-requirement disabled reasons. Selected-action execution-plan panels should build normalize and REST-plan requests from `getFrontendApiFormValuesWithDefaults(...)` and render `resolveFrontendApiNormalizeRequest(...)` / `resolveFrontendApiRestPlanRequest(...)` result state. Run controls should render `disabled`, `detail`, `status`, and `confirmation_satisfied` from `getFrontendApiActionRunState(...)`. Keep sidebar and tab selection synchronized on the generated workspace-section id.

Selected-action workbench panels should prefer `getFrontendApiActionPanelState(...)` when they need the usual detail, fields, values with defaults, form controls, option requests, normalize/rest-plan requests, confirmation state, Run state, and stable option/execution request keys. Use the lower-level helpers when a panel intentionally needs only one part of that view model.

The desktop helper owns the confirmation acceptance shape: store it as `FrontendApiActionConfirmationStates`, check it with `isFrontendApiActionConfirmationSatisfied(...)`, and reset it when submitted form values change. UI copy and severity should come from `execution.confirmation`, not from component-local write/destructive rules.

The desktop helper also owns run-state interpretation. Components may keep the current REST-plan and REST-execution result in React state, but `getFrontendApiActionRunState(...)` should decide whether Run is disabled and which result/detail/status text is shown.

For frontend helper changes, run `rtk npm --prefix apps/desktop run test:unit`. That test gate checks generated summary/group registry alignment, selected-action panel state, option-resolution state, normalize/rest-plan state, REST-execution request/result shaping, and bridge-unavailable dev behavior against the generated SDK operation list before the broader desktop build.

## Status Values

| Status | Meaning |
| --- | --- |
| `implemented` | The row points to a current SDK, CLI, REST, MCP, or LSP surface. |
| `planned` | The frontend needs the capability, but ParaDev has not stabilized the SDK behavior yet. |
| `frontend-local` | The behavior belongs to the app shell, such as selecting the active project tab. |

## API Groups

| Group | Current operations |
| --- | --- |
| `projects` | `project.create`, `project.find`, `project.open`, `project.view`, `project.list`, `project.state`, `project.browser`, `project.source_text`, `project.draft_apply`, `project.rename`, `project.inspect`, `project.config`, plus frontend-local `project.activate`. |
| `modules` | `module.list`, `module.view`, `module.templates`, `module.create`, `module.draft`, `module.file`, `module.edit`, `module.rename`, `module.remove`, `module.authoring_path`, `module.authoring_plan`, `module.source_slots`, and `module.sources`. |
| `collections` | `collection.list`, `collection.view`, `collection.create`, `collection.file`, `collection.edit`, `collection.rename`, `collection.remove`, `collection.authoring_path`, `collection.authoring_plan`, `collection.source_slots`, and `collection.sources`. |
| `build` | `build.plan`, `build.emit`, `build.start`, `build.runs`, `build.status`, `build.interrupt`, `build.summary`, `build.manifests`, `build.artifacts`, `build.localization`, `build.assets`, `build.sprites`, `build.diagnostics`, `build.source_map`, `build.dependencies`, `build.graph`, `build.explain`, and `build.families`. |
| `pdx` | `pdx.parse`, `pdx.tokens`, `pdx.dump`, and `pdx.format`. |
| `lsp` | `lsp.diagnostics`, `lsp.symbols`, `lsp.hover`, `lsp.formatting`, `lsp.completion`, and `lsp.semantic_tokens`. |
| `catalog` | `catalog.preview`, `catalog.write`, `catalog.refresh`, and `catalog.query`. |
| `surfaces` | `surface.frontend_api`, `surface.frontend_api.workspace`, `surface.frontend_api.action`, `surface.frontend_api.normalize`, `surface.frontend_api.rest_request`, `surface.frontend_api.options`, `surface.frontend_api.binding_lookup`, `surface.architecture`, `surface.openapi`, `surface.cli_contract`, `surface.mcp_contract`, and `surface.lsp_contract`. |

For module and collection screens, prefer the SDK-owned inspection dispatcher instead of separate frontend routing. `Project.inspect("modules", ...)`, `Project.inspect("source-slots", ...)`, `Project.inspect("sources", ...)`, and `Project.inspect("build-explain", ...)` use the same filters documented by `contract["inspection_contract"]`. Source-slot rows now include suggested exact paths, so a UI can offer "create missing file" actions without duplicating family slot rules.

Inspection-backed rows use the same surface bindings: Python `Project.inspect(kind, **filters)`, REST `GET /projects/inspect?kind=...`, and MCP `project_inspect`. This covers `module.list`, `module.view`, `module.sources`, collection list/view/source-slot/source rows, read-only `build.*` rows such as `build.summary`, `build.assets`, `build.sprites`, `build.diagnostics`, `build.graph`, `build.explain`, and read-only catalog rows `catalog.preview` and `catalog.query`. Each row in `get_frontend_api_contract()` lists the concrete payload schema, for example `paradev.build.modules.v1`, `paradev.build.assets.v1`, `paradev.build.sprites.v1`, or `paradev.hb.catalog-preview.v1`. `catalog.query` expects an existing written or refreshed local catalog database.

`build.graph` is the canonical visual trace payload. Its node rows include `group`, `display_label`, `display_detail`, and `display_path` in addition to stable ids and source/artifact fields. Use `index["nodes_by_group"]` for graph lanes and side-panel filters instead of parsing node ids in the frontend.

`build.families` returns `paradev.build.families.v1`. Its family rows include metadata form rules: all accepted top-level keys, SDK common keys, compiler-owned keys, existing settings constraints, and the unknown-key loose/strict diagnostic policy. Use that payload for module creation and import screens instead of maintaining per-family `meta.yaml` allowlists in the frontend.

Catalog write and refresh are mutating project operations, not inspection rows. Python calls `paradev.hb.catalog_write(...)` or `paradev.hb.catalog_refresh(...)`; CLI calls `hb catalog-write` or `hb catalog-refresh`; REST calls `POST /projects/catalog` to create a catalog database and `PUT /projects/catalog` to replace it. The REST request planner can produce those calls from `catalog.write` or `catalog.refresh` submitted values.

`project.create` creates a buildable starter project and returns `paradev.project.create.v1`. Use `Project.create(...)` from Python, CLI `new`, REST `POST /projects`, or MCP `project_create`; all surfaces route to the SDK and produce the same project view plus starter module id. REST requires `path` and accepts optional `project_id`, `title`, `game=hoi4`, and `force=false`. Use `force` only when the user has confirmed writing starter files into a non-empty directory.

`project.open` and `project.view` return the SDK-owned project view model from `Project.to_view`. Use `Project.load(...).to_view()` from Python, CLI `project`, REST `GET /projects`, or MCP `project_open`/`project_view`. REST accepts optional `path`, `game`, and `title`; use `GET /projects/find` first when the UI needs a non-throwing existence check before opening.

`project.browser` returns `paradev.sdk.project-browser.v1`. Use `Project.browser(...)` from Python, CLI `project-browser`, REST `GET /projects/browser`, or MCP `project_browser` when a GUI, importer, or desktop shell needs one read-only module/collection tree with labels, path context, source roots, family groups, and lookup indexes. It is not a generic filesystem browser; it is derived from the same build module and collection payloads used by inspections.

`project.source_text`, `module.draft`, and `project.draft_apply` are the canonical source-editor bridge operations for browser-row editing. `project.source_text` reads a project-contained UTF-8 source file through `Project.read_source_text` and returns text plus paired `size` and `mtime_ns` from the same stable snapshot. `module.draft` plans or writes a module from a frontend browser family id such as `ideas`, using the same SDK scaffold plan as `module.create`. `project.draft_apply` applies validated text edits, removals, and binary replacements inside the project root through `Project.apply_source_draft`; CLI `draft-apply` exposes the same SDK helper for scripts. GUI edits, guarded removal objects, and existing replacements send the source's paired `expected_size` and `expected_mtime_ns` revision when available; both fields must be supplied together. A new replacement sends `expected_absent=true`, which cannot be combined with a revision. When a supplied guard detects that a source changed, disappeared, or appeared, the entire request is rejected. Legacy unguarded inputs remain compatible but do not provide this protection. One request is bounded to 256 targets and 256 MiB of streamed backups. After a later failure, an earlier mutation is rolled back only while it still matches ParaDev's exact mutation token; newer external edits are preserved and incomplete recovery reports its retained path.

`module.rename` is a source-module container operation. It moves a module to
a new object-id folder in the same family and returns
`paradev.module.rename.v1`; it does not rewrite PDX identifiers, localization
keys, or other authored file contents. Its optional `title` input
canonicalizes the physical name as `{object_id} - {portable title}` and may be
used while keeping the same object id. The desktop writes the Registry-owned
localization title before requesting this suffix synchronization.

`module.remove` is also a source-module container operation. It returns `paradev.module.remove.v1`, dry-runs by default, inventories the files that would be removed, and deletes the module folder only when `write` is explicit. Use it for confirmation dialogs and cleanup flows; it does not remove generated build artifacts.

`module.file` and `module.edit` are text-file operations inside an existing module root. They return `paradev.module.file.v1`, reject paths that escape the module folder, and preserve the exact text passed by the caller. Use them for editor panes and importers; use the PDX parser and build diagnostics for semantic validation.

`collection.create` plans or writes a collection descriptor folder plus `meta.yaml`. It returns `paradev.collection.create.v1`, nests the same authoring-plan payload used by collection source-slot screens, blocks existing metadata unless `force` is explicit, and leaves descriptor source files to `collection.edit --create`.

`collection.file` and `collection.edit` are the same text-file boundary for collection descriptor roots. They return `paradev.collection.file.v1`, accept optional `family` and `source_root` disambiguation, reject paths outside the descriptor folder, and preserve exact text. Use them for focus-tree, event-namespace, decision-category, and other shared-output descriptor screens.

`collection.sources` returns `paradev.build.sources.v1` from the same `sources` inspection as `module.sources`, but defaults `owner_kind=collection`. Use it when a collection descriptor screen needs the actual descriptor-owned compiler inputs, not every module source associated with the same collection id.

`collection.rename` is a collection descriptor container operation. It returns `paradev.collection.rename.v1` and commits the descriptor-folder move plus every explicit `collection` pointer in member `meta.yaml` and `.paradev/meta.yaml` files through one crash-recoverable transaction. Hidden settings and unrelated visible metadata are preserved. Authored PDX identifiers, localization keys, and generated artifacts are not rewritten.

`collection.remove` is a collection-grouping operation. It returns `paradev.collection.remove.v1` and dry-runs by default with an exact `plan_hash`, descriptor inventory, preserved member list, and visible/hidden metadata edits. Applying that hash preserves every module, clears its explicit `collection` pointer, and removes the descriptor through one crash-recoverable transaction. Generated build artifacts are not edited; rebuild after removal to refresh derived output.

`build.plan` and `build.emit` both return `BuildResult.to_dict`. `Project.build(...)` and CLI `build` dry-run by default; REST `POST /projects/build` exposes that same plan for desktop and GUI callers. Omit `strict_metadata` to inherit `CM_PARADEV`; pass `strict_metadata=true` when the user wants unknown metadata keys to block the build, or `strict_metadata=false` / `--no-strict-metadata` when the user explicitly wants loose-mode warnings. Use `emit_artifacts=true` and/or `emit_manifests=true` only after the dry-run result is not blocked. The REST route preflights artifact emission and returns the blocked plan instead of writing files when blocking diagnostics exist. `build.start`, `build.runs`, `build.status`, and `build.interrupt` expose the Python-owned child-process lifecycle through `desktop_start_build(...)`, `desktop_build_runs(...)`, `desktop_build_status(...)`, `desktop_interrupt_build(...)`, and REST `POST /desktop/builds`, `GET /desktop/builds`, `GET /desktop/builds/status`, and `POST /desktop/builds/interrupt`, so the installed GUI and build-time native-web preview use the same frontend API REST planner. Status and interrupt forms require the exact nonblank `run_id` returned by start or listing. Only a genuinely omitted id retains lower-level compatibility behavior; empty or whitespace values are invalid.

`pdx.format` returns `paradev.pdx.format.v1`. `format_pdx_text(...)` formats unsaved editor buffers, and `format_pdx_file(..., write=False)` previews a file without mutation. CLI `format PATH --write` and REST `POST /pdx/format?write=true` replace the file only after parsing succeeds.

`lsp.formatting` returns `paradev.lsp.formatting.v1`. `format_pdx_lsp_text(...)` accepts current editor text and returns LSP `TextEdit` rows with zero-based ranges; REST `POST /lsp/formatting` exposes the same SDK helper for GUI agents that do not speak JSON-RPC directly. The payload reports parse errors as LSP diagnostics and does not write files.

`lsp.diagnostics` returns `paradev.lsp.diagnostics.v1`. `diagnose_pdx_lsp_text(...)` accepts current editor text and returns LSP diagnostics with zero-based ranges and numeric severity; REST `POST /lsp/diagnostics` exposes the same SDK helper for GUI agents. It is the editor-buffer companion to file-oriented `pdx.parse`.

`lsp.symbols` returns `paradev.lsp.symbols.v1`. `document_symbols_pdx_lsp_text(...)` accepts current editor text and returns nested LSP `DocumentSymbol` rows from parsed PDX keys; REST `POST /lsp/symbols` exposes the same SDK helper. Use it for outline panes and quick navigation without teaching the GUI the PDX AST.

`lsp.hover` returns `paradev.lsp.hover.v1`. `hover_pdx_lsp_text(...)` accepts current editor text plus a zero-based `line` and `character`, then returns an LSP `Hover` object when the position lands on a parsed PDX key. REST `POST /lsp/hover` exposes the same helper for GUI agents. Current hovers describe key spans only; value and full-node ranges will need richer parser spans later.

`lsp.completion` returns `paradev.lsp.completion.v1`. `complete_pdx_lsp_text(...)` accepts current editor text, a zero-based position, optional cursor `offset`, and an optional project/catalog database; when a HeavenBase catalog has been written it returns completion items from persisted HOI4 entities, localization keys, and parsed PDX symbols. REST `POST /lsp/completion`, the desktop editor bridge, and `paradev lsp serve` use the same SDK helper. Desktop implicit completion skips large buffers by default and explicit completion passes `offset` for a bounded context scan.

`lsp.semantic_tokens` returns `paradev.lsp.semantic-tokens.v1`. `semantic_tokens_pdx_lsp_text(...)` accepts current editor text and returns LSP semantic-token data plus expanded token rows for GUI highlighting. REST `POST /lsp/semantic-tokens`, the desktop CodeMirror bridge, and `paradev lsp serve` use the same helper.

When adding a public frontend-visible capability, update `src/paradev/sdk/frontend_api.py`, the related surface helper, this page, the generated references, `apps/desktop/src/generated/frontendApi.ts`, the desktop helper at `apps/desktop/src/data/frontendApi.ts` when its typed views change, and the focused architecture tests in the same change. Regenerate `docs/user-manual/frontend-api-reference.md` with `frontend-api --markdown` and `docs/user-manual/sdk-cli-reference.md` with `frontend-api --sdk-cli-markdown`. At minimum, the architecture tests should prove the operation row appears in the binding reverse index and, for REST-backed rows, in the OpenAPI frontend-operation annotation. Do not hand-maintain TypeScript operation id unions or frontend action lists.

## 中文

本页面向 GUI、导入器、REST、MCP、VS Code 和桌面端 agent，用来维护 ParaDev 可调用操作的稳定清单。唯一的机器可读清单是 `get_frontend_api_contract()`：

```python
from paradev.sdk import get_frontend_api_contract

contract = get_frontend_api_contract()
for operation in contract["operations"]:
    print(operation["id"], operation["status"])
```

完整的生成版 operation table 见 [前端 API Reference](frontend-api-reference.md)。它由同一份 SDK contract 通过 `rtk uv run paradev frontend-api --markdown` 生成；每次 frontend-visible operation 行变化时，都应重新生成。contract 还包含 `summary`，列出 operation、group、status、read/write、workspace-section 和 SDK/CLI/REST/MCP/LSP binding coverage 计数；生成版 reference 会把这些 coverage 字段渲染成 surface 矩阵，并把 `index["binding"]` 渲染成 surface-call table，因此新增 GUI action 或文档前，应同时用这两处做维护审计。client 需要按 group/status 获取 operation-id list 时，应使用 Python `get_frontend_api_group_operation_ids(...)` / `get_frontend_api_status_operation_ids(...)` 或 TypeScript `getFrontendApiGroupOperationIds(...)` / `getFrontendApiStatusOperationIds(...)`，不要扫描 rows 或直接读取 raw index；需要按 read/write 获取 operation-id list 时，应使用 Python `get_frontend_api_mode_operation_ids(...)` 或 TypeScript `getFrontendApiModeOperationIds(...)`。Python client 需要把 surface call key 或整个 adapter surface 反查为稳定 operation id 时，应使用 `get_frontend_api_binding_lookup(...)`、`get_frontend_api_binding_operation_ids(...)`、`get_frontend_api_binding_index(...)`、`build_frontend_api_rest_index_key(...)` 和 `get_frontend_api_rest_operation_ids(...)`。client 需要列出某个 surface 的全部 operation id 时，应使用 Python `get_frontend_api_surface_operation_ids(...)` 或 TypeScript `getFrontendApiSurfaceOperationIds(...)` helper，不要扫描 rows；client 需要列出返回同一 payload schema 的全部 operation id 时，应使用 Python `get_frontend_api_payload_operation_ids(...)` 或 TypeScript `getFrontendApiPayloadOperationIds(...)`；client 需要列出某个 workspace section 中的全部 operation id 时，应使用 Python `get_frontend_api_workspace_section_operation_ids(...)` 或 TypeScript `getFrontendApiWorkspaceSectionOperationIds(...)`。TypeScript client 应使用 `apps/desktop/src/data/frontendApi.ts` 中的桌面 helper；它包装 `apps/desktop/src/generated/frontendApi.ts` 中的生成版 contract，并用 `rtk uv run paradev frontend-api --typescript` 重新生成，同时暴露 operation id、group id、status、read/write mode、workspace-section、workspace-action、selected-action detail、selected-action panel state、form-control、binding、binding-index、group-index、status-index、mode-index、surface-index、payload-index、workspace-section-index、input、default-value、option-source、option-request、option-result、normalize result、REST-plan result、REST-execution result、endpoint、JSON-request 和 response-payload 类型，以及 `getFrontendApiAction(...)`、`getFrontendApiActionDetail(...)`、`getFrontendApiActionPanelState(...)`、`getFrontendApiFormControls(...)`、`getFrontendApiFormControlKind(...)`、`getFrontendApiFormValuesWithDefaults(...)`、`getFrontendApiFormOptionRequests(...)`、`resolveFrontendApiFormOptionRequest(...)`、`resolveFrontendApiNormalizeRequest(...)`、`resolveFrontendApiRestPlanRequest(...)`、`resolveFrontendApiRestExecutionRequest(...)`、`getFrontendApiSectionActions(...)`、`getFrontendApiDefaultSectionAction(...)`、`getFrontendApiBindings(...)`、`getFrontendApiRestBinding(...)`、`getFrontendApiBindingOperationIds(...)`、`getFrontendApiRestOperationIds(...)`、`getFrontendApiGroupOperationIds(...)`、`getFrontendApiStatusOperationIds(...)`、`getFrontendApiModeOperationIds(...)`、`getFrontendApiSurfaceOperationIds(...)`、`getFrontendApiPayloadOperationIds(...)`、`getFrontendApiWorkspaceSectionOperationIds(...)`、`getFrontendApiInputs(...)`、`getFrontendApiRequiredInputNames(...)`、`getFrontendApiDefaultValues(...)`、`getFrontendApiOptionSourceInputs(...)`、`buildFrontendApiActionUrl(...)`、`buildFrontendApiOptionsRequest(...)`、`buildFrontendApiNormalizeRequest(...)`、`buildFrontendApiRestPlanRequest(...)`、`buildFrontendApiRestIndexKey(...)` 和 `buildFrontendApiRestExecutionRequest(...)` 等 lookup helper。

决定某个 grouped API table 应使用哪条 raw `contract["index"]` path 和 helper 时，使用 `get_frontend_api_index_catalog()` 或生成版 Index Catalog section。

生成版 Surface Index table 会把 `contract["index"]["surface"]` 渲染成 SDK、CLI、REST、MCP、LSP 和 frontend-local/unbound row 的 operation-id list。

生成版 Group Binding Summary Index table 会按 operation group 列出 concrete SDK、CLI、REST、MCP 和 LSP binding key，因此 feature-level API surface 不必扫描每个 binding row 就能审计。

生成版 REST Route Index table 会把 REST binding 渲染成 method/path/query 行，因此 GUI client 和 OpenAPI 审计不需要解析给人阅读的 `rest` 字符串。需要 route 级别 OpenAPI 摘要、parameter/body 要求、response description 和 frontend operation 反向映射时，阅读 [REST API Reference](rest-api-reference.md)。

生成版 REST Request Planner Index table 会渲染每个 REST-bound operation 的 static query defaults、path parameters 和 JSON body fields，GUI client 可用它审计 request planning，不必执行 operation。

生成版 Workspace Section REST Summary Index table 会先按 workspace section 汇总 REST planner coverage，再进入 lower-level REST query/path/body field 明细。

生成版 Group REST Summary Index table 会先按 operation group 汇总 REST planner coverage，再进入 lower-level REST query/path/body field 明细。

生成版 REST Static Query Index table 会渲染 REST binding 声明的 fixed query parameter，包括 rendered value 和 JSON value type，供 REST client 审计使用。

生成版 REST Dynamic Query Field Index table 会渲染 request-plan time 会变成 REST query parameter 的 frontend input，并列出显式提交时可覆盖的 static default。

生成版 REST Path Parameter Index table 会渲染每个会进入 REST path parameter 的 frontend input，包括 alias-aware parameter name 和 normalizer target，供 REST client 审计使用。

生成版 REST Body Field Index table 会渲染每个会进入 REST JSON body 的 frontend input，包括 alias-aware body name 和 normalizer target，供 REST client 审计使用。

生成版 SDK Call Index table 会把 `contract["index"]["binding"]["sdk"]` 渲染成 SDK-call-to-operation row，供 Python SDK 审计使用。

生成版 SDK Call Input Index table 会渲染 SDK-bound operation 的 input，包括 required/default state、target bucket 和 adapter-side alias，供 Python SDK 审计使用。

生成版 MCP Tool Index table 会把 `contract["index"]["binding"]["mcp"]` 渲染成 tool-to-operation row，供 adapter 审计使用。

生成版 MCP Tool Input Index table 会渲染 MCP-bound operation 的 input，包括 required/default state、target bucket 和 adapter-side alias，供 MCP adapter 审计使用。

生成版 CLI Command Index table 会把 `contract["index"]["binding"]["cli"]` 渲染成 command-to-operation row，供 adapter 审计使用。

生成版 CLI Command Input Index table 会渲染 CLI-bound operation 的 input，包括 required/default state、target bucket 和 adapter-side alias，供 command adapter 审计使用。

生成版 LSP Method Index table 会把 `contract["index"]["binding"]["lsp"]` 渲染成 method-to-operation row，供 VS Code 和 language-server 审计使用。

生成版 LSP Method Input Index table 会渲染 LSP-bound operation 的 input，包括 required/default state、target bucket 和 adapter-side alias，供 VS Code 和 language-server 审计使用。

生成版 Confirmation Index table 会渲染 SDK-owned workspace action 中 required 的 `execution.confirmation` row，GUI shell 可用它审计 mutation scope、style 和 confirm fields，不必扫描每个 action。

生成版 Group Execution Summary Index table 会先按 operation group 汇总 workspace action execution policy，再进入 action-level execution 明细。

生成版 Workspace Section Execution Summary Index table 会先按 workspace section 汇总 workspace action execution policy，再进入 action-level execution 明细。

生成版 Workspace Action Execution Index table 会渲染每个 SDK-owned workspace action 的 execution kind、default surface、available surfaces、value requirement、state scope、normalizer schema 和 REST planner schema。

生成版 Group Confirmation Summary Index table 会先按 operation group 汇总需要 confirmation 的 workspace action，再进入 workspace-section 和 action-level confirmation 明细。

生成版 Workspace Section Confirmation Summary Index table 会先按 workspace section 汇总需要 confirmation 的 action，再进入 action-level confirmation 明细。

生成版 Group Option Source Summary Index table 会先按 operation group 汇总 dynamic option-source dependency，再进入 field-level option source 明细。

生成版 Workspace Section Mode Status Index table 会按 workspace section 汇总 read/write mode 和 implementation status coverage，因此 GUI 维护者不必扫描每个 action 就能审计 mutating 与 frontend-local action 的位置。

生成版 Group Mode Status Index table 会按 operation group 汇总 read/write mode 和 implementation status coverage。

生成版 Workspace Section Payload Coverage Index table 会按 workspace section 汇总 response payload schema，并单独统计 untyped actions。

生成版 Group Payload Coverage Index table 会按 operation group 汇总 response payload schema，并单独统计 untyped operations。

生成版 Workspace Section Surface Coverage Index table 会按 workspace section 汇总 callable surface coverage，包括 frontend-local actions、unbound actions 和 default-surface distribution。

生成版 Workspace Section Binding Summary Index table 会先按 workspace section 列出 concrete SDK、CLI、REST、MCP 和 LSP binding key，再进入 form-focused section summary。

生成版 Workspace Section Form Summary Index table 会按 SDK-owned workspace section 汇总 action form footprint，包括 action counts、input counts、required fields、defaults、aliases、option sources、constraints 和 control-kind counts。

生成版 Workspace Section Control Summary Index table 会先按 workspace section 汇总 SDK-derived form control kind，再进入 field-level control 明细。

生成版 Group Control Summary Index table 会先按 operation group 汇总 SDK-derived form control kind，再进入 field-level control 明细。

生成版 Workspace Section Option Source Summary Index table 会先按 workspace section 汇总 dynamic option-source dependency，再进入 field-level option source 明细。

生成版 Workspace Section Input Target Summary Index table 会按 workspace section 汇总 input target bucket，包括 parameter fields、project-context fields、selectors、projections 和 aliases。

生成版 Group Input Target Summary Index table 会先按 operation group 汇总 input target bucket，再进入 field-level input target 明细。

生成版 Workspace Section Validation Summary Index table 会先按 workspace section 汇总 choice 与 minimum constraint，再进入 field-level constraint 明细。

生成版 Group Validation Summary Index table 会先按 operation group 汇总 choice 与 minimum constraint，再进入 field-level constraint 明细。

生成版 Workspace Section Default Summary Index table 会先按 workspace section 汇总带 default 的 input field，再进入 field-level default 明细。

生成版 Group Default Summary Index table 会先按 operation group 汇总带 default 的 input field，再进入 field-level default 明细。

生成版 Workspace Section Required Summary Index table 会先按 workspace section 汇总 required input field，再进入 field-level required-input 明细。

生成版 Group Required Summary Index table 会先按 operation group 汇总 required input field，再进入 field-level required-input 明细。

生成版 Workspace Section Alias Summary Index table 会先按 workspace section 汇总 frontend-to-SDK input alias，再进入 field-level alias 明细。

生成版 Group Alias Summary Index table 会先按 operation group 汇总 frontend-to-SDK input alias，再进入 field-level alias 明细。

生成版 Option Source Index table 会渲染 `operation.inputs[*].option_source` row，GUI shell 可用它审计 dynamic form dependency、provider operation、forwarded fields 和 fixed filters，不必扫描每个 operation。

生成版 Option Provider Index table 会按 provider operation 汇总这些 dynamic option fields，因此 provider API 及其 dependent UI fields 可以从反向依赖关系审计。

生成版 Input Field Index table 会渲染每个声明的 input field，包括 type、required/default 状态、有限 choices、frontend-to-SDK alias 和 option-source provider，供表单审计使用。

生成版 Group Form Summary Index table 会按 operation group 汇总 form footprint，包括 input counts、required fields、defaults、aliases、option sources、constraints 和 control-kind counts。

生成版 Operation Form Summary Index table 会按 operation 汇总 form footprint，包括 input count、required fields、defaults、aliases、option sources、constraints 和 control kinds。

生成版 Form Control Index table 会渲染每个 SDK-derived control kind，包括由 static choices 派生的 select 字段，以及由 dynamic option sources 派生的 combobox 字段。

生成版 Required Input Index table 会渲染每个 execution 前必须提交的字段，包括 normalizer target bucket、adapter-side alias 和 option-source provider。

生成版 Input Default Index table 会渲染每个 SDK-owned form default 及其 normalizer target bucket 和 adapter-side alias，因此 GUI initial state 可被单独审计，不必扫描完整 input table。

生成版 Input Constraint Index table 会渲染 normalizer 强制校验的每个有限 choice list 和 numeric lower bound，UI controls 和 validators 可用它审计约束，不必逐个打开 form schema。

生成版 Input Target Index table 会渲染每个声明 input field 的 normalizer target bucket 和 adapter-side alias，SDK、REST 和 GUI client 可用它审计 submitted-value routing，不必逐个打开 form payload。

生成版 Input Alias Index table 只渲染 adapter execution 前会重映射 submitted frontend name 的字段，因此 alias-sensitive 的 REST 和 SDK call 可被单独审计，不必扫描每个 input target row。

调用方已经知道稳定的 operation id 或 group id 时，应使用 SDK lookup helper，不要手写列表扫描。GUI shell 需要维护好的导航/action 布局时，应使用 `get_frontend_api_workspace(...)`；它会把同一批 operation id 分组为 project switcher、project browser、authoring、source editor、build、catalog 和 surface-contract sections。每个 workspace action row 使用 `paradev.sdk.frontend-api.action.v1`，并从 canonical operation row 派生 operation payload schema、可调用 `bindings`、`execution.default_surface`、`execution.available_surfaces`、`execution.confirmation`、`form_schema`、`normalizer_schema` 和 `rest_request_schema` 提示。渲染或检查一个已选 action 时，使用 `get_frontend_api_action(...)`；它会把 canonical operation row、workspace action、section membership、派生 form、option-source 摘要、bindings 和 execution hints 组合成一份 payload。表单、面板和 action dialog 应使用 `get_frontend_api_form(...)`；它会从同一行 operation 的 `inputs` 派生 SDK-owned 的 label/description、required fields、defaults、aliases、target buckets、controls、有限 choices、数值下界、option sources 和小型 JSON Schema。字段包含 `option_source` 时，使用 `resolve_frontend_api_options(...)`；它会通过 SDK 执行 provider，并返回可直接渲染的 `value`、`label`、`details` 和原始来源行。Python adapter 可以继续用 `normalize_frontend_api_inputs(...)` 把提交的表单状态转换成 project、parameter、selector 和 projection buckets。REST client 可以调用 `plan_frontend_api_rest_request(...)`，把同一份提交值拆成 method、path、query 和 JSON body：

TypeScript shell 代码如果只需要 generated field render state，应使用 `apps/desktop/src/data/frontendApi.ts` 中的 `getFrontendApiFormControls(...)`；它会从同一行 operation 派生 control kind、默认值预览、提交值预览、choices/option-source 提示，以及缺少 option-source requirement 时的 disabled reason。shell 可以保存本地提交值，但应先通过 `getFrontendApiFormValuesWithDefaults(...)` 合并 SDK 默认值，再渲染依赖状态。使用 `getFrontendApiFormOptionRequests(...)` 判断哪些 option-source call 已可用，并通过 `buildFrontendApiOptionsRequest(...)` 为每个可用字段生成 `{ url, init }`；之后对每个可用 request 调用 `resolveFrontendApiFormOptionRequest(...)`，得到 `ready`、`unavailable` 或 `error` 状态以及返回的 option payload。把这些结果传回 `getFrontendApiFormControls(operation_id, values, optionResults)`，让静态 `choices` 和 SDK 解析出的 option payload 都转成同一种 `FrontendApiFormControlOption` row，供 select 控件渲染。不要在 React 组件里执行 option provider、复制 requirement 检查或直接手写 `fetch`。只需要 raw metadata 的面板应使用 `frontendApiInputOperations`、`getFrontendApiInputs(...)`、`getFrontendApiRequiredInputNames(...)`、`getFrontendApiDefaultValues(...)` 和 `getFrontendApiOptionSourceInputs(...)`，不要扫描 `operation.inputs` 或维护本地表单默认值。TypeScript client 调用 frontend API meta endpoints 时应使用 `frontendApiEndpointPaths`、`buildFrontendApiDiscoveryUrl(...)`、`buildFrontendApiActionUrl(...)`、`buildFrontendApiOptionsUrl(...)`、`buildFrontendApiNormalizeUrl(...)`、`buildFrontendApiRestRequestUrl(...)` 和 `buildFrontendApiBindingLookupUrl(...)`；对 JSON POST meta endpoints，使用 `buildFrontendApiOptionsRequest(...)`、`buildFrontendApiNormalizeRequest(...)` 和 `buildFrontendApiRestPlanRequest(...)` 从提交后的表单值生成 `{ url, init }` fetch 输入，再用 `resolveFrontendApiNormalizeRequest(...)` 和 `resolveFrontendApiRestPlanRequest(...)` 渲染 `ready` 或 `error` 结果状态。REST-plan payload ready 且 `execution.confirmation` 已满足后，桌面代码应调用 `buildFrontendApiRestExecutionRequest(plan)` 和 `resolveFrontendApiRestExecutionRequest(request)` 执行已计划的目标 request，并渲染 `loading`、`ready` 或 `error` 状态。如果 Vite shell 需要调用正在运行的 REST bridge，设置 `VITE_PARADEV_FRONTEND_API_BASE_URL`；未设置时 helper 会返回 bridge-unavailable 状态，而不会在浏览器里产生 404。option resolution、normalization、REST request planning 和确认策略仍由 SDK 拥有；浏览器请求塑形和 bridge-unavailable 处理由 helper 拥有。

```python
from paradev.sdk import (
    get_frontend_api_binding_lookup,
    get_frontend_api_action,
    get_frontend_api_form,
    get_frontend_api_group,
    get_frontend_api_operation,
    get_frontend_api_workspace,
    normalize_frontend_api_inputs,
    plan_frontend_api_rest_request,
    resolve_frontend_api_options,
)

workspace = get_frontend_api_workspace()
source_editor = next(section for section in workspace["sections"] if section["id"] == "source-editor")
module_edit_action = next(action for action in source_editor["actions"] if action["operation_id"] == "module.edit")
module_list = get_frontend_api_operation("module.list")
module_group = get_frontend_api_group("modules")
module_create_detail = get_frontend_api_action("module.create")
module_edit_form = get_frontend_api_form("module.edit")
module_edit_inputs = normalize_frontend_api_inputs(
    "module.edit",
    {"module_id": "modifier/example", "relative_path": "def.txt", "text": "modifier = { value = 1 }"},
)
print(workspace["sections"][0]["id"], module_list["rest"], module_group["operation_ids"])
print(module_edit_form["required"], module_edit_form["defaults"])
print(module_edit_form["fields"][3]["label"], module_edit_form["fields"][3]["description"])
print(module_edit_inputs["project"], module_edit_inputs["parameters"])
print(module_edit_action["execution"]["default_surface"])
print(module_create_detail["sections"], module_create_detail["option_fields"])
print(get_frontend_api_binding_lookup("rest", "GET /projects/inspect?kind=modules")["operation_ids"])
print(resolve_frontend_api_options("module.create", "template_id", {"path": "demos/assets/projects/minimal"})["options"][0])
print(plan_frontend_api_rest_request("module.edit", module_edit_inputs["values"])["body"])
```

对 `module.create` 来说，选中的模板行就是后续 scaffold 的通用创建表单来源。GUI 应使用其中的 `form.fields` 渲染 `title`、`description` 或 `image` 等模板输入，并把 `default_assets` 用作可选预览和覆盖入口。这些默认资源只是 family 级别 metadata；除非用户显式创建实例资源，否则不会写入新模块目录。

同一份 contract 也可以通过 CLI 获取：

```bash
rtk uv run paradev frontend-api --json
rtk uv run paradev frontend-api --operation module.list --json
rtk uv run paradev frontend-api --group modules --json
rtk uv run paradev frontend-api --workspace --json
rtk uv run paradev frontend-api --operation module.create --action --json
rtk uv run paradev frontend-api --operation module.edit --form --json
rtk uv run paradev frontend-api --binding-surface rest --binding-key 'GET /projects/inspect?kind=modules' --json
rtk uv run paradev frontend-api --sdk-cli-markdown > docs/user-manual/sdk-cli-reference.md
rtk uv run paradev frontend-api --typescript > apps/desktop/src/generated/frontendApi.ts
rtk uv run paradev frontend-api --operation module.create \
  --option-field template_id \
  --values-json '{"path":"demos/assets/projects/minimal"}' \
  --json
rtk uv run paradev frontend-api --operation build.artifacts \
  --values-json '{"path":"/workspace/mod","artifact_path":"common/modifiers/test.txt"}' \
  --json
rtk uv run paradev frontend-api --operation module.edit \
  --values-json '{"path":"/workspace/mod","module_id":"modifier/example","relative_path":"def.txt","text":"modifier = { value = 1 }"}' \
  --rest-request \
  --json
```

REST/OpenAPI 暴露 `GET /frontend-api`，并支持可选的 `operation_id` 和 `group_id` query selector，与 SDK lookup helper 对齐；`GET /frontend-api/workspace` 会返回与 `get_frontend_api_workspace(...)` 相同的 workspace projection；`GET /frontend-api/action?operation_id=...` 会返回与 `get_frontend_api_action(...)` 相同的已选 action payload；同时传 `operation_id` 和 `form=true` 会返回与 `get_frontend_api_form(...)` 相同的派生表单 contract。`POST /frontend-api/options?operation_id=...&field_name=...` 接收当前表单值，并返回与 `resolve_frontend_api_options(...)` 相同的动态选项 payload。`POST /frontend-api/normalize?operation_id=...` 接收一份提交后的表单 JSON object，并返回与 `normalize_frontend_api_inputs(...)` 相同的 normalized payload。`POST /frontend-api/rest-request?operation_id=...` 返回对应 REST method、path、query 和 JSON body plan，不会执行目标 operation。`GET /frontend-api/binding?binding_surface=...&binding_key=...` 返回与 `get_frontend_api_binding_lookup(...)` 相同的反向查询 payload。每个支撑 frontend row 的 OpenAPI operation 也会包含 `x-paradev-frontend-api-operation-ids`，让 codegen 能把 `GET /projects`、`GET /projects/inspect`、`POST /projects/build` 这类共享路由映射回稳定 operation id。MCP surface 暴露只读 `frontend_api` tool，并使用同样的 selector 名称；canonical `surface.frontend_api` 行也会在 `selectors` 字段列出这些名称。请把这份 contract 当作前端功能目录：`implemented` 行代表现在可以调用；`planned` 行代表前端确实需要，但 SDK 行为还没有稳定；`frontend-local` 行代表应用外壳自己的工作区状态，不是 SDK 项目变更。

每个 operation 行会保留 `rest`、`cli` 这类给人阅读的 surface 字符串；如果某个 surface 存在，也会发布机器可读的 `bindings` object。REST client 使用 `bindings.rest.method`、`bindings.rest.path` 和 `bindings.rest.query`；adapter 或生成客户端使用 `bindings.cli.command`、`bindings.mcp.tool`、`bindings.lsp.method` 和 `bindings.sdk.call`。Contract 还会构建 `contract["index"]["binding"]`，按 surface 和 call key 反查某个共享 route、tool、command 或 LSP method 对应哪些 operation id。Python client 应使用 `get_frontend_api_binding_lookup(...)`、`get_frontend_api_binding_operation_ids(...)`、`get_frontend_api_binding_index(...)`、`build_frontend_api_rest_index_key(...)` 和 `get_frontend_api_rest_operation_ids(...)`；CLI client 应使用 `frontend-api --binding-surface ... --binding-key ...`；REST client 可以调用 `GET /frontend-api/binding?binding_surface=...&binding_key=...`；TypeScript client 应使用 `apps/desktop/src/data/frontendApi.ts` 中的 `frontendApiBindingIndex`、`getFrontendApiBindingOperationIds(...)`、`buildFrontendApiRestIndexKey(...)` 和 `getFrontendApiRestOperationIds(...)` 做反向查询，不要直接读取 raw generated JSON。静态 CLI 与 MCP contract 会分别在 `get_cli_contract()["frontend_operation_ids"]` 和 `get_mcp_contract()["frontend_operation_ids"]` 暴露自己的切片；这些 contract 应通过 `get_frontend_api_binding_index(...)` 获取 copied surface map。Python architecture gate `test_frontend_api_contract_indexes_every_surface_binding_and_openapi_annotation` 会确保每个声明的 binding 都进入这个反向索引，并确保每个 REST binding 都同步出现在 OpenAPI 的 `x-paradev-frontend-api-operation-ids` 标注中。

需要项目派生下拉或自动补全的字段可以携带 `option_source`，schema 是 `paradev.sdk.frontend-api.option-source.v1`。source 行会指向另一个 canonical operation id、provider payload 内的列表路径、value/label/detail 字段、必要上下文字段、可转发的当前表单字段，以及可选固定过滤器。例如，`module.create.template_id` 指向 `module.templates` 的 `templates`，`source_root` 指向 `module.templates` 的 `source_roots`，`family` 指向 `build.families`，已有的 `module_id` 和 `collection_id` 字段指向 `module.list` 和 `collection.list`，artifact 字段指向 `build.artifacts`，diagnostic code 字段指向 `build.diagnostics`。UI 代码应调用 `resolve_frontend_api_options(...)`、CLI `frontend-api --operation ... --option-field ...` 或 REST `POST /frontend-api/options`；不要在前端硬编码 template id、family id、module id、collection id、artifact path 或 diagnostic code。如果缺少 `module_id` 这样的必要上下文字段，resolver 会返回 `available=false` 和 `missing_requirements`，前端可以据此禁用控件直到用户补齐依赖字段。

project 管理相关行会在 `inputs` 中列出前端输入字段。`project.create` 声明 `path`、可选 `project_id`、可选 `title`、默认 `hoi4` 的 `game`，以及默认 `false` 的 `force`；`project.find`、`project.open`、`project.view` 和 `project.browser` 的 `path` 默认是 `"."`；`project.list` 接受可选的 `project_paths` 和 `search_roots` 数组，供项目切换器使用；`project.state` 额外接受可选的 `project_path` 作为当前激活工作区；`project.browser` 接受可选的 `profile`、`kind`、`family`、`module_id` 和 `collection_id` 过滤字段，用来获取只读工作区树，其中 `kind` 的 choices 是 `module` 或 `collection`；`project.inspect` 暴露通用的 `path` 和 SDK inspection `kind` 字段，供 dispatcher client 使用；需要大量过滤字段的面板应优先使用 `module.list` 或 `build.graph` 这样的具体行；`project.rename` 必须传 `title`；frontend-local 的 `project.activate` 必须传 `project_id`。

已经实现但不需要 GUI 提交值的行会显式发布 `inputs=[]`。`project.config` 仍是 CLI 负责的配置命名空间，不是通用设置表单；`surface.openapi`、`surface.cli_contract`、`surface.mcp_contract` 和 `surface.lsp_contract` 是无需表单的 contract 导出 action。前端应把它们渲染为无输入 action，而不是把缺少字段当成 contract 漏洞。

module 和 collection 行也使用同一套 `inputs` 约定。只读面板会列出 `path` 和 inspection 过滤字段；`module.templates` 列出可用于创建模块的 authoring templates 和 source roots；`module.view` 必须传 `module_id`，`collection.view` 必须传 `collection_id`。authoring 行会为共享 authoring endpoint 带上默认 `kind`：`module` 或 `collection`。source-slot status 字段会声明 `satisfied`、`missing`、`empty`、`diagnostic`，source inventory status 字段会声明 `loaded` 和 `diagnostic`，collection source view 会声明 `owner_kind` 可以是 `module` 或 `collection`。会写文件的行会把 `write`、`create`、`force` 这类确认布尔值默认设为安全的 `false`，同时把 `text`、`values`、`metadata` 这类 body 字段直接列在 operation 行上。

PDX 行使用已保存文件输入：`pdx.parse`、`pdx.tokens`、`pdx.dump` 和 `pdx.format` 都需要 `path`；格式化默认使用 tab 缩进、保留注释，并且 `write=false`。LSP 行使用未保存的编辑器 buffer 输入：diagnostics、symbols、hover 和 formatting 都需要 `text`；hover 还需要零基的 `line` 和 `character`，两者都有 `minimum=0`；completion 需要同样的零基位置，并接受可选的零基 `offset`，让编辑器 adapter 在大 buffer 中避免从文件开头扫描；formatting 的默认值与 PDX formatter 对齐。

build 行使用项目 `path`、可选 `profile` 和每个行自己的过滤字段。`build.plan`、`build.emit` 和 `build.diagnostics` 也暴露可选的 `strict_metadata`；省略它时会继承 `CM_PARADEV` 中的 `paradev.build.strict_metadata`，显式设置时则由 GUI、导入器或 CI 面板决定未知模块或 collection 元数据键是 warning 还是 blocking diagnostic。`build.emit` 会把 `emit_artifacts` 和 `emit_manifests` 默认设为 `false`；只读 build 行暴露的过滤字段与对应 SDK inspection 方法一致。`build.start` 是通过 `POST /desktop/builds` 启动一次桌面构建的生命周期行；它必须传 `project_root`，并接受 `mode`、`profile`、`strict_metadata`、`parallelism` 和 `target`。`build.runs` 接受可选的 `project_root` 过滤字段，并以 `paradev.desktop.build-runs.v1` 返回当前原生应用进程所知的全部活动构建和最新 256 条终态构建；对已淘汰终态 id 的精确查询会返回 `idle`。`build.status` 与 `build.interrupt` 使用 `run_id`，返回与桌面 facade 相同的 `paradev.desktop.build-run.v1` payload。`build.artifacts` 发布 `artifact_path`，并带有 `maps_to="path"`，因为前端仍然需要把项目 `path` 留给当前工作区。过滤输出位置的 build 行会声明 `target_root` choices：`output` 或 `build`；build diagnostics 会声明 `severity` choices：`error` 或 `warning`。catalog 行使用 `path`、`profile`、可选 `database` 和 query 过滤字段；`catalog.write` 映射到 REST `POST /projects/catalog`，`catalog.refresh` 映射到 REST `PUT /projects/catalog`。`surface.frontend_api` 会把 `operation_id`、`group_id` 和默认 `false` 的 `form` projection flag 列为输入。`surface.frontend_api.action` 返回一个 operation 的已选 action detail，包括 workspace section id、存在时的派生 form，以及 option-source field name。`surface.frontend_api.options` 会用同一份提交值解析某个字段的动态选项。`surface.frontend_api.normalize` 是把提交值通过 Python、CLI 或 REST 拆成 SDK buckets 的 adapter 行，`surface.frontend_api.rest_request` 会从同一份提交值计划一个 REST call。

维护 operation list 时看原始 `inputs`；渲染外层 app 导航时使用 `workspace["sections"]`：section id 和 action `operation_id` 都由 SDK 维护，应作为 UI stable keys。TypeScript shell 代码应从 `apps/desktop/src/data/frontendApi.ts` 导入 `frontendApiWorkspaceActions`、`getFrontendApiAction(...)`、`getFrontendApiActionDetail(...)`、`getFrontendApiFormControls(...)`、`getFrontendApiSectionActions(...)` 和 `getFrontendApiDefaultSectionAction(...)`，并在只需要 raw input rows、required field names、defaults 或 option-source fields 时使用 `frontendApiInputOperations`、`getFrontendApiInputs(...)`、`getFrontendApiRequiredInputNames(...)`、`getFrontendApiDefaultValues(...)` 和 `getFrontendApiOptionSourceInputs(...)`，不要扫描 generated JSON 或维护第二份 action registry/form defaults。渲染一个已选 action detail 时使用 `get_frontend_api_action(...)`，或在桌面静态 shell 中使用 generated-contract mirror `getFrontendApiActionDetail(...)`；不要在组件里手工拼接 workspace、form、bindings 和 option-source 数据。使用 `getFrontendApiFormControls(...)` 渲染 read-only/default form state，并在用户尚未提供所有 option-source requirements 时显示 disabled reason。使用每个 action 的 `execution` object 决定默认调用路径和确认策略；GUI shell 通常使用 `default_surface="rest"` 和 `getFrontendApiRestBinding(...)`、嵌入的 REST binding 或 REST planner，`execution.confirmation.required` 表示 Run 控件必须先等待用户显式确认，`confirm_fields` 列出 `write`、`force`、`create`、`emit_artifacts` 或 `emit_manifests` 等安全布尔字段，用户未确认前应保持 false。SDK 脚本仍可选择 `bindings.sdk`，VS Code/LSP adapter 可选择 `bindings.lsp`，`project.activate` 这样的 `frontend-local` action 保留在 app workspace state 中，不发布可调用的 SDK/REST binding。渲染 UI 表单时用派生表单 contract：`fields` 保持 operation 顺序，每个 field 都带有 SDK-owned 的 `label` 和 `description` 文案，每个 field 都有一个 `target` bucket，`required` 是可直接用于校验的列表，`defaults` 可直接作为初始表单状态，`choices` 用于 select 控件，`option_source` 指向 SDK 维护的动态选项，`minimum` 表示数值下界，`aliases` 会把 `artifact_path` 这样的前端安全字段映射回 SDK filter name，`json_schema` 则给已经使用 JSON Schema 的 adapter 使用。选择非 REST surface call 时使用 `getFrontendApiBindings(...)`；不要解析给人阅读的 `rest`、`cli`、`sdk`、`mcp` 或 `lsp` 字符串。执行 action 时再调用 normalizer：Python 用 `normalize_frontend_api_inputs(...)`，CLI 用 `frontend-api --operation ... --values-json ...`，REST 用 `POST /frontend-api/normalize?operation_id=...`，TypeScript 可用 `buildFrontendApiNormalizeRequest(...)` 生成该 JSON request。normalizer 会在调用 SDK 或 REST 前检查不支持的字段、必填字段、声明的 choices 和数值下界。如果下一步是 HTTP call，则使用 REST planner：Python 调用 `plan_frontend_api_rest_request(...)`，CLI 增加 `--rest-request`，REST 调用 `POST /frontend-api/rest-request?operation_id=...`，TypeScript 可用 `buildFrontendApiRestPlanRequest(...)`。REST plan ready 并完成确认后，桌面 shell 用 `buildFrontendApiRestExecutionRequest(...)` 和 `resolveFrontendApiRestExecutionRequest(...)` 执行已计划的目标 request，并渲染 `loading`、`ready` 或 `error` 状态；不要在组件里手写 REST 执行 mapper。normalized input payload 会把项目加载相关字段放在 `project`，action 参数放在 `parameters`，frontend API selector 放在 `selectors`，`form` 这样的 operation projection 放在 `projections`。

桌面 TypeScript 的 sidebar 和 tab 应从 `frontendApiWorkspaceSections` 派生；已选 action row 仍使用 `frontendApiWorkspaceActions`、`getFrontendApiSectionActions(...)`、`getFrontendApiDefaultSectionAction(...)` 和 `getFrontendApiRequiredInputNames(...)`。已选 action summary panel 应使用 `getFrontendApiActionDetail(...)` 获取 operation summary、execution surfaces、generated fields、defaults、option-source field names 和 `execution.confirmation`。已选 action form panel 应使用 `getFrontendApiFormControls(...)` 获取 read-only control state、default preview 和 missing-requirement disabled reason。已选 action execution-plan panel 应从 `getFrontendApiFormValuesWithDefaults(...)` 构造 normalize 与 REST-plan request，并渲染 `resolveFrontendApiNormalizeRequest(...)` / `resolveFrontendApiRestPlanRequest(...)` 的结果状态。Run 控件应从 `getFrontendApiActionRunState(...)` 渲染 `disabled`、`detail`、`status` 和 `confirmation_satisfied`。sidebar 与 tab selection 应同步到同一个 generated workspace-section id。

selected-action workbench panel 如果需要常见的 detail、fields、合并默认值后的 values、form controls、option requests、normalize/rest-plan request、confirmation state、Run state，以及稳定的 option/execution request key，应优先使用 `getFrontendApiActionPanelState(...)`。只有当 panel 明确只需要其中一块时，才直接调用 lower-level helper。

桌面 helper 拥有确认接受状态的形状：用 `FrontendApiActionConfirmationStates` 保存，用 `isFrontendApiActionConfirmationSatisfied(...)` 检查，并在提交的表单值变化时重置。UI 文案和严重程度来自 `execution.confirmation`，不要在组件里维护本地 write/destructive 规则。

桌面 helper 也拥有 Run state 解释。组件可以在 React state 中保存当前 REST-plan 和 REST-execution 结果，但应由 `getFrontendApiActionRunState(...)` 决定 Run 是否 disabled，以及展示哪一段 result/detail/status 文案。

修改 frontend helper 时，运行 `rtk npm --prefix apps/desktop run test:unit`。该测试 gate 会先用 checked-in generated SDK operation list 验证 generated summary/group registry alignment、selected-action panel state、option-resolution state、normalize/rest-plan state、REST-execution request/result shaping 和 dev 模式 bridge-unavailable 行为，再进入更大的 desktop build。

## 状态含义

| 状态 | 含义 |
| --- | --- |
| `implemented` | 这一行已经指向当前 SDK、CLI、REST、MCP 或 LSP surface。 |
| `planned` | 前端需要这个能力，但 ParaDev 尚未稳定对应 SDK 行为。 |
| `frontend-local` | 行为属于 app shell，例如选择当前激活的项目 tab。 |

## API 分组

| 分组 | 当前操作 |
| --- | --- |
| `projects` | `project.create`、`project.find`、`project.open`、`project.view`、`project.list`、`project.state`、`project.browser`、`project.source_text`、`project.draft_apply`、`project.rename`、`project.inspect`、`project.config`，以及 frontend-local 的 `project.activate`。 |
| `modules` | `module.list`、`module.view`、`module.templates`、`module.create`、`module.draft`、`module.file`、`module.edit`、`module.rename`、`module.remove`、`module.authoring_path`、`module.authoring_plan`、`module.source_slots` 和 `module.sources`。 |
| `collections` | `collection.list`、`collection.view`、`collection.create`、`collection.file`、`collection.edit`、`collection.rename`、`collection.remove`、`collection.authoring_path`、`collection.authoring_plan`、`collection.source_slots` 和 `collection.sources`。 |
| `build` | `build.plan`、`build.emit`、`build.start`、`build.runs`、`build.status`、`build.interrupt`、`build.summary`、`build.manifests`、`build.artifacts`、`build.localization`、`build.assets`、`build.sprites`、`build.diagnostics`、`build.source_map`、`build.dependencies`、`build.graph`、`build.explain` 和 `build.families`。 |
| `pdx` | `pdx.parse`、`pdx.tokens`、`pdx.dump` 和 `pdx.format`。 |
| `lsp` | `lsp.diagnostics`、`lsp.symbols`、`lsp.hover`、`lsp.formatting`、`lsp.completion` 和 `lsp.semantic_tokens`。 |
| `catalog` | `catalog.preview`、`catalog.write`、`catalog.refresh` 和 `catalog.query`。 |
| `surfaces` | `surface.frontend_api`、`surface.frontend_api.workspace`、`surface.frontend_api.action`、`surface.frontend_api.normalize`、`surface.frontend_api.rest_request`、`surface.frontend_api.options`、`surface.frontend_api.binding_lookup`、`surface.architecture`、`surface.openapi`、`surface.cli_contract`、`surface.mcp_contract` 和 `surface.lsp_contract`。 |

模块和集合页面应优先使用 SDK 拥有的 inspection dispatcher，而不是在前端维护另一套路由。`Project.inspect("modules", ...)`、`Project.inspect("source-slots", ...)`、`Project.inspect("sources", ...)` 和 `Project.inspect("build-explain", ...)` 使用的过滤字段都来自 `contract["inspection_contract"]`。Source-slot 行已经包含 exact path 建议，因此 UI 可以提供“创建缺失文件”操作，而不需要复制 family slot 规则。

inspection-backed 行使用同一组 surface 绑定：Python `Project.inspect(kind, **filters)`、REST `GET /projects/inspect?kind=...`、MCP `project_inspect`。它覆盖 `module.list`、`module.view`、`module.sources`，collection 的 list/view/source-slot/source 行，`build.summary`、`build.assets`、`build.sprites`、`build.diagnostics`、`build.graph`、`build.explain` 等只读 `build.*` 行，以及只读 catalog 行 `catalog.preview` 和 `catalog.query`。`get_frontend_api_contract()` 中的每一行都会列出具体 payload schema，例如 `paradev.build.modules.v1`、`paradev.build.assets.v1`、`paradev.build.sprites.v1` 或 `paradev.hb.catalog-preview.v1`。`catalog.query` 需要本地 catalog 数据库已经写入或刷新过。

`build.graph` 是 canonical visual trace payload。它的 node 行除了稳定 id 和 source/artifact 字段，还包含 `group`、`display_label`、`display_detail` 和 `display_path`。前端绘制 graph lane 或侧边栏 filter 时，应使用 `index["nodes_by_group"]`，不要解析 node id。

`build.families` 返回 `paradev.build.families.v1`。它的 family 行包含 metadata 表单规则：所有接受的顶层 key、SDK common keys、compiler 自己的 keys、已有 settings 约束，以及 unknown-key 在 loose/strict 模式下的 diagnostic policy。模块创建和导入界面应使用这个 payload，不要在前端维护每个 family 的 `meta.yaml` allowlist。

catalog write 和 refresh 是会写入的 project 操作，不是 inspection row。Python 调用 `paradev.hb.catalog_write(...)` 或 `paradev.hb.catalog_refresh(...)`；CLI 调用 `hb catalog-write` 或 `hb catalog-refresh`；REST 用 `POST /projects/catalog` 创建 catalog 数据库，用 `PUT /projects/catalog` 替换它。REST request planner 可以根据 `catalog.write` 或 `catalog.refresh` 的提交值生成这些调用。

`project.create` 会创建一个可直接构建的 starter project，并返回 `paradev.project.create.v1`。Python 使用 `Project.create(...)`，CLI 使用 `new`，REST 使用 `POST /projects`，MCP 使用 `project_create`；这些 surface 都路由到 SDK，并返回同一份 project view 和 starter module id。REST 必填 `path`，可选 `project_id`、`title`、`game=hoi4` 和 `force=false`。只有在用户确认要向非空目录写入 starter 文件时才使用 `force`。

`project.open` 和 `project.view` 返回 SDK 拥有的 `Project.to_view` 项目视图。Python 使用 `Project.load(...).to_view()`，CLI 使用 `project`，REST 使用 `GET /projects`，MCP 使用 `project_open`/`project_view`。REST 支持可选的 `path`、`game` 和 `title`；如果 UI 需要先做不会抛错的存在性检查，再打开项目，请先用 `GET /projects/find`。

`project.browser` 返回 `paradev.sdk.project-browser.v1`。GUI、导入器或桌面 shell 需要一个只读的 module/collection 树时，Python 使用 `Project.browser(...)`，CLI 使用 `project-browser`，REST 使用 `GET /projects/browser`，MCP 使用 `project_browser`。payload 包含显示 label、路径上下文、source root、family 分组和 lookup index。它不是通用文件浏览器，而是从 inspection 使用的同一组 build module 和 collection payload 派生出来的。

`project.source_text`、`module.draft` 和 `project.draft_apply` 是 browser-row 编辑场景的 canonical source-editor bridge operations。`project.source_text` 通过 `Project.read_source_text` 读取项目内 UTF-8 source 文件，并从同一个稳定快照返回文本以及成对的 `size`、`mtime_ns`。`module.draft` 根据 `ideas` 这样的前端 browser family id 计划或写入模块，并复用 `module.create` 的 SDK scaffold plan。`project.draft_apply` 通过 `Project.apply_source_draft` 在项目根目录内应用经过校验的文本编辑、删除和二进制替换；CLI `draft-apply` 为脚本暴露同一个 SDK helper。GUI 会在可用时为文本编辑、带保护的删除对象和现有二进制替换一并发送 `expected_size` 与 `expected_mtime_ns`，两者必须同时提供；新建替换则发送不能与修订值组合的 `expected_absent=true`。当已提供的 guard 发现源文件发生变化、消失或新出现时，整个请求都会被拒绝；兼容的旧式无 guard 输入仍可使用，但不具备该保护。单个请求最多包含 256 个 target 和 256 MiB 流式备份。后续步骤失败时，只有仍精确匹配 ParaDev mutation token 的早期变更才会回滚；较新的外部编辑会被保留，不完整恢复会报告保留路径。

`module.rename` 是源模块容器操作。它把 module 移动到同一 family
下的新 object-id 目录，并返回 `paradev.module.rename.v1`；它不会改写
PDX 标识符、本地化 key 或其他作者文件内容。可选 `title` 输入会把
物理目录规范为 `{object_id} - {可移植标题}`，也可以在 object id
不变时只同步可读后缀。桌面端会先写入 Registry-owned 本地化标题，再
请求这次后缀同步。

`module.remove` 也是源模块容器操作。它返回 `paradev.module.remove.v1`，默认只做 dry-run，会列出将被删除的文件；只有显式传入 `write` 才会删除模块目录。前端确认对话框和清理流程使用它；它不会删除已经生成的 build artifacts。

`module.file` 和 `module.edit` 是已有模块目录内的文本文件操作。它们返回 `paradev.module.file.v1`，会拒绝逃出模块目录的路径，并保留调用方传入的精确文本。编辑器面板和导入器使用这两个接口；语义校验仍交给 PDX parser 和 build diagnostics。

`collection.create` 会计划或写入 collection descriptor 目录和 `meta.yaml`。它返回 `paradev.collection.create.v1`，内嵌 collection source-slot 页面使用的同一份 authoring-plan payload；已有 metadata 会阻塞，除非显式使用 `force`；descriptor 源文件仍通过 `collection.edit --create` 添加。

`collection.file` 和 `collection.edit` 是 collection descriptor 根目录上的同类文本文件边界。它们返回 `paradev.collection.file.v1`，支持用可选的 `family` 和 `source_root` 消除歧义，会拒绝逃出 descriptor 目录的路径，并保留精确文本。国策树、事件 namespace、决议类别以及其他共享输出 descriptor 页面使用这两个接口。

`collection.sources` 从和 `module.sources` 相同的 `sources` inspection 返回 `paradev.build.sources.v1`，但默认使用 `owner_kind=collection`。collection descriptor 页面需要实际由 descriptor 拥有的 compiler inputs 时使用它，不要把同一 collection id 下的所有模块源文件混在一起。

`collection.rename` 是 collection descriptor 容器操作。它返回 `paradev.collection.rename.v1`，并在一个可崩溃恢复的事务中提交 descriptor 目录移动以及所有 member `meta.yaml`、`.paradev/meta.yaml` 内显式 `collection` pointer 的改写。隐藏 settings 与无关的可见 metadata 会保留；作者维护的 PDX 标识符、本地化 key 和生成 artifact 不会改写。

`collection.remove` 是 collection 分组操作。它返回 `paradev.collection.remove.v1`，默认 dry-run，并给出精确 `plan_hash`、descriptor 文件清单、会保留的 member 列表，以及可见/隐藏 metadata 的变更。应用该 hash 会保留所有模块，清除它们显式的 `collection` pointer，并在一个可崩溃恢复的事务中删除 descriptor。已有 build artifacts 不会被直接修改；删除后重新构建即可刷新派生输出。

`build.plan` 和 `build.emit` 都返回 `BuildResult.to_dict`。`Project.build(...)` 和 CLI `build` 默认都是 dry-run；REST `POST /projects/build` 为桌面端和 GUI caller 暴露同一个计划结果。省略 `strict_metadata` 时会继承 `CM_PARADEV`；用户需要让未知 metadata key 阻塞构建时传入 `strict_metadata=true`，需要显式保持 loose-mode warning 时传入 `strict_metadata=false` 或 `--no-strict-metadata`。只有在 dry-run 结果没有被 blocking diagnostics 阻塞后，才使用 `emit_artifacts=true` 和/或 `emit_manifests=true`。REST route 会先做 artifact emission preflight；如果存在 blocking diagnostics，会返回被阻塞的计划，不会写文件。`build.start`、`build.runs`、`build.status` 和 `build.interrupt` 通过 `desktop_start_build(...)`、`desktop_build_runs(...)`、`desktop_build_status(...)`、`desktop_interrupt_build(...)` 与 REST `POST /desktop/builds`、`GET /desktop/builds`、`GET /desktop/builds/status` 和 `POST /desktop/builds/interrupt` 暴露由 Python 管理的桌面子进程生命周期；已安装 GUI 与构建期 native-web 预览都使用同一个 frontend API REST planner。状态查询和中断表单必须使用启动或列表返回的精确非空白 `run_id`。只有真正省略 id 时才保留底层兼容行为；空字符串或全空白值无效。

`pdx.format` 返回 `paradev.pdx.format.v1`。`format_pdx_text(...)` 用来格式化未保存的编辑器文本，`format_pdx_file(..., write=False)` 用来无副作用预览文件格式化结果。CLI `format PATH --write` 和 REST `POST /pdx/format?write=true` 只有在解析成功后才会替换文件。

`lsp.formatting` 返回 `paradev.lsp.formatting.v1`。`format_pdx_lsp_text(...)` 接收当前编辑器文本，并返回带零基 range 的 LSP `TextEdit` 行；REST `POST /lsp/formatting` 为不直接使用 JSON-RPC 的 GUI agent 暴露同一个 SDK helper。payload 会把解析错误映射为 LSP diagnostics，不会写文件。

`lsp.diagnostics` 返回 `paradev.lsp.diagnostics.v1`。`diagnose_pdx_lsp_text(...)` 接收当前编辑器文本，并返回带零基 range 和数字 severity 的 LSP diagnostics；REST `POST /lsp/diagnostics` 为 GUI agent 暴露同一个 SDK helper。它是文件型 `pdx.parse` 的编辑器缓冲区版本。

`lsp.symbols` 返回 `paradev.lsp.symbols.v1`。`document_symbols_pdx_lsp_text(...)` 接收当前编辑器文本，并从解析后的 PDX keys 返回嵌套的 LSP `DocumentSymbol` 行；REST `POST /lsp/symbols` 暴露同一个 SDK helper。大纲面板和快速跳转使用它，GUI 不需要理解 PDX AST。

`lsp.hover` 返回 `paradev.lsp.hover.v1`。`hover_pdx_lsp_text(...)` 接收当前编辑器文本，以及零基的 `line` 和 `character`；当位置落在已解析的 PDX key 上时，会返回 LSP `Hover` object。REST `POST /lsp/hover` 为 GUI agent 暴露同一个 helper。当前 hover 只描述 key span；value span 和完整节点 range 需要后续 parser 提供更丰富的 span。

`lsp.completion` 返回 `paradev.lsp.completion.v1`。`complete_pdx_lsp_text(...)` 接收当前编辑器文本、零基位置、可选的 cursor `offset`，以及可选的 project/catalog database；当 HeavenBase catalog 已经写入时，它会从持久化的 HOI4 entities、本地化 key 和已解析 PDX symbols 返回 completion items。REST `POST /lsp/completion`、桌面编辑器桥接和 `paradev lsp serve` 都使用同一个 SDK helper。桌面端默认会跳过大 buffer 的隐式 completion，显式 completion 会传入 `offset` 以使用有界 context scan。

`lsp.semantic_tokens` 返回 `paradev.lsp.semantic-tokens.v1`。`semantic_tokens_pdx_lsp_text(...)` 接收当前编辑器文本，并返回 LSP semantic-token data 以及供 GUI 高亮使用的展开 token 行。REST `POST /lsp/semantic-tokens`、桌面 CodeMirror 桥接和 `paradev lsp serve` 都使用同一个 helper。

新增任何公开、前端可见的能力时，请在同一次变更里更新 `src/paradev/sdk/frontend_api.py`、相关 surface helper、本页、生成版 references、`apps/desktop/src/generated/frontendApi.ts`；当 typed view 变化时也更新 `apps/desktop/src/data/frontendApi.ts`，并同步聚焦 architecture tests。用 `frontend-api --markdown` 重新生成 `docs/user-manual/frontend-api-reference.md`，用 `frontend-api --sdk-cli-markdown` 重新生成 `docs/user-manual/sdk-cli-reference.md`。至少要证明该 operation row 进入 binding reverse index；如果它有 REST binding，还要证明 OpenAPI frontend-operation annotation 同步更新。不要手工维护 TypeScript operation id union 或前端 action list。
