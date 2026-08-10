# Python SDK

## English

The CLI is a thin wrapper over the SDK. Prefer the SDK when you need automation, tests, or custom scripts.

For the generated overall inventory of API reference tables, read [API Catalog Reference](api-catalog-reference.md). It is generated from `paradev.surfaces.get_api_catalog_table()` and lists the schema, row count, index names, owner-module index, surface index, CLI regeneration command, and doc page for each maintained SDK, CLI, REST, MCP, frontend, and surface contract reference. For package-level imports such as `Project`, `CM_PARADEV`, and `__version__`, read [Package API Reference](package-api-reference.md), generated from `paradev.get_package_api_table()`. For config defaults and the shared ConfigManager facade, read [Config API Reference](config-api-reference.md), generated from `paradev.config.get_config_api_table()`. For the installed GUI launcher facade, read [GUI API Reference](gui-api-reference.md), generated from `paradev.gui.get_gui_api_table()`. For SDK-owned desktop state helpers, read [Desktop API Reference](desktop-api-reference.md), generated from `paradev.desktop.get_desktop_api_table()`. For game profile registry helpers, read [Games API Reference](games-api-reference.md), generated from `paradev.games.get_games_api_table()`. For surface facade imports such as CLI, REST, MCP, LSP, VS Code, bundle, API catalog, and surface contract helpers, read [Surfaces API Reference](surfaces-api-reference.md), generated from `paradev.surfaces.get_surfaces_api_table()`. For a generated list of every public `paradev.sdk` import, read [SDK API Reference](sdk-api-reference.md). It is generated from `paradev.sdk.get_sdk_api_table()` and groups the facade by module, feature, and symbol kind so contributors can audit export drift without reading `__all__` by hand. For the public `Project` object surface itself, read [Project API Reference](project-api-reference.md). It is generated from `paradev.sdk.get_project_api_table()` and groups fields and methods by feature, row kind, CLI command, frontend operation, and inspection kind. For authoring-template schemas and scaffold-planning helpers, read [Authoring Templates API Reference](templates-api-reference.md), generated from `paradev.sdk.templates.get_templates_api_table()`. For compatibility overlay copy-root helpers, read [Copy Roots API Reference](copy-roots-api-reference.md), generated from `paradev.sdk.copy_roots.get_copy_roots_api_table()`. For the narrower `paradev.project` import facade, read [Project Facade API Reference](project-facade-api-reference.md), generated from `paradev.project.get_project_facade_api_table()`. For HOI4 language alias normalization helpers, read [Localization API Reference](localization-api-reference.md), generated from `paradev.localization.get_localization_api_table()`. For compiler extension imports such as build records, families, slots, loaders, manifests, views, and artifact writers, read [Build API Reference](build-api-reference.md), generated from `paradev.build.get_build_api_table()`. For a generated list of every current Python SDK call and CLI command, read [SDK And CLI API Reference](sdk-cli-reference.md). It is derived from the same operation contract as the frontend API and includes a feature-level SDK/CLI coverage summary, so it is the shortest way to answer "which verb do I use for project, module, collection, build, PDX, LSP, or catalog work?" For a CLI-command-first adapter table, read [CLI API Reference](cli-api-reference.md), generated from `paradev.surfaces.cli.get_cli_api_table()`. For lower-level parser/editor/catalog/REST/MCP contracts, read [PDX API Reference](pdx-api-reference.md), generated from `paradev.sdk.get_pdx_api_table()`, [LSP API Reference](lsp-api-reference.md), generated from `paradev.sdk.get_lsp_api_table()`, [Catalog API Reference](catalog-api-reference.md), generated from `paradev.hb.get_catalog_api_table()`, [REST API Reference](rest-api-reference.md), generated from `paradev.surfaces.rest.get_rest_api_table()`, and [MCP API Reference](mcp-api-reference.md), generated from `paradev.surfaces.mcp.get_mcp_api_table()`. For the public REST package facade that exposes the local API server helpers, read [REST Facade API Reference](rest-facade-api-reference.md), generated from `paradev.api.get_rest_facade_api_table()`. For the public HeavenBase import facade that exposes those catalog helpers and table helpers, read [HeavenBase Facade API Reference](hb-api-reference.md), generated from `paradev.hb.get_hb_api_table()`.

For the low-level parser facade itself, read [PDX Core API Reference](pdx-core-api-reference.md), generated from `paradev.pdx.get_pdx_core_api_table()`. It groups tokenizer, token, AST, parser, diagnostics, scalar constants, and PDX facade-reference helper imports by module, feature, and symbol kind. For the public LSP server package facade, read [LSP Server API Reference](lsp-server-api-reference.md), generated from `paradev.lsp.get_lsp_server_api_table()`. It groups the stdio server, JSON-RPC dispatcher, document cache, framing helpers, and facade-reference helpers by module, feature, and symbol kind.

Create and build a starter project:

```python
from paradev.sdk import Project

project = Project.create("projects/starter-mod", title="Starter Mod")
result = project.build(emit_artifacts=True, emit_manifests=True)
assert not result.blocked
print(result.summary())
```

Load an existing project:

```python
from paradev.sdk import Project

found = Project.find("demos/assets/projects/minimal/src/modules/focus/GER_sample")
assert found["found"]

project = Project.load("demos/assets/projects/minimal")
summary = project.summary()
print(summary["summary"])
```

List known local projects, compose the desktop project state, and read the project browser tree:

```python
from paradev.sdk import Project, desktop_state, registered_projects

registry = registered_projects(search_roots=("demos/assets/projects",))
project_ids = [row["project_id"] for row in registry["projects"]]
state = desktop_state("demos/assets/projects/minimal")
assert state["active_project"]["project_id"] == "minimal_hoi4"
browser = Project.load("demos/assets/projects/minimal").browser(kind="module")
assert browser["items"][0]["module_id"] == "focus/GER_sample"
```

Rename the project display title without moving files or changing `project_id`:

```python
project = Project.load("projects/starter-mod")
project = project.rename("Renamed Starter Mod")
print(project.to_view()["title"])
```

Rename a source module folder without changing authored HoI4 ids inside the files:

```python
project = Project.load("projects/starter-mod")
payload = project.rename_module(
    "modifier/starter_mod_starter_modifier",
    "starter_mod_renamed_modifier",
    title="Renamed Modifier",
)
print(payload["module_id"])
assert payload["content_rewritten"] is False
```

When a localized display-title edit also changes the readable folder suffix,
commit both through one guarded draft request:

```python
module_root = project.root / "src/modules/idea/IDEA_ALPHA"
payload = project.apply_source_draft(
    source_edits=[
        {
            "path": str(module_root / "main.loc"),
            "text": "[en.IDEA_ALPHA]\nReadable Alpha\n",
        }
    ],
    module_rename={
        "module_id": "idea/IDEA_ALPHA",
        "object_id": "IDEA_ALPHA",
        "title": "Readable Alpha",
    },
)
print(payload["module_rename"]["root"])
```

Read and replace one text source file inside a module:

```python
project = Project.load("projects/starter-mod")
source = project.read_module_file("modifier/starter_mod_starter_modifier", "def.txt")

updated = source["text"].replace("0.05", "0.10")
payload = project.write_module_file(
    "modifier/starter_mod_starter_modifier",
    "def.txt",
    updated,
)
assert payload["written"]
```

Inspect a Registry-owned image or copied resource without loading its bytes,
then replace it with the exact stable revision guard returned by the SDK:

```python
import base64

asset = project.read_module_asset(
    "idea/IDEA_ALPHA",
    "icon.png",
)
assert asset["source_slots"]
assert "content_base64" not in asset

payload = project.apply_source_draft(
    source_replacements=[
        {
            **asset["draft_guard"],
            "content_base64": base64.b64encode(new_png_bytes).decode("ascii"),
        }
    ]
)
assert payload["written"]
```

Pass `include_content=True` to `read_module_asset(...)` only when the current
bytes are needed. `Project.read_source_binary(...)` provides the same bounded,
digest-bearing stable snapshot for a project-contained binary path that is not
being selected as a module asset.

For Registry-supported JSON or PDX sources, prefer guided controls over raw
text replacement. Control ids come from `Project.source_form(...)`; never
guess them. Plan several edits without writing, review the exact changes, then
apply the combined revision-guarded draft once:

```python
def control_id(form, patch_path):
    sections = list(form["sections"])
    while sections:
        section = sections.pop()
        for control in section.get("controls", []):
            if control.get("patch", {}).get("path") == patch_path:
                return control["id"]
        sections.extend(section.get("sections", []))
    raise KeyError(patch_path)


project = Project.load("projects/PIHC3")
first_source = project.read_module_file("entity/VIENTO_MIRROR", "record.json")
second_source = project.read_module_file("entity/VIENTO_AIR_AIRSHIP", "record.json")
first_form = project.source_form(first_source["path"])
second_form = project.source_form(second_source["path"])
assert first_form is not None and second_form is not None

plan = project.plan_source_form_updates(
    [
        {
            "source_path": first_source["path"],
            "values": {control_id(first_form, ["mesh", "scale"]): 4.5},
        },
        {
            "source_path": second_source["path"],
            "values": {control_id(second_form, ["mesh", "scale"]): 3.5},
        },
    ]
)
for update in plan["updates"]:
    print(update["changes"])

if plan["changed"]:
    payload = project.apply_source_draft(source_edits=plan["source_edits"])
    assert payload["written"]
```

Read and replace one text source file inside a collection descriptor:

```python
project = Project.load("projects/starter-mod")
created = project.create_collection(
    "event",
    "germany",
    metadata={"title": "Germany Events"},
    write=True,
)
assert created["written"]
project.write_collection_file(
    "germany",
    "category.txt",
    "add_namespace = germany\n",
    family="event",
    create=True,
)

source = project.read_collection_file("germany", "category.txt", family="event")

payload = project.write_collection_file(
    "germany",
    "category.txt",
    source["text"],
    family="event",
)
assert payload["written"]
```

Add two idea modules to an existing project:

```python
from paradev.sdk import Project

project = Project.load("projects/starter-mod")

for object_id, title, description in (
    ("GER_industry_spirit", "German Industry Spirit", "Industrial production spirit."),
    ("GER_army_spirit", "German Army Spirit", "Army modernization spirit."),
):
    plan = project.scaffold_module(
        "hoi4:idea/basic",
        object_id,
        values={"title": title, "description": description},
        write=True,
    )
    if plan["blocked"]:
        raise RuntimeError(plan["diagnostics"])

result = project.build()
assert not result.blocked
```

By package default, unknown keys in module or collection `meta.yaml` files are warning diagnostics. Omitted `Project.build(...)` and `Project.diagnostics(...)` calls inherit `paradev.build.strict_metadata` from `CM_PARADEV`; pass `strict_metadata=True` when an importer, cleanup script, or CI gate should force blocking errors:

```python
strict_plan = project.build(strict_metadata=True)
unknown_key_diagnostics = project.diagnostics(
    strict_metadata=True,
    code="metadata.unknown_key",
)
```

Use `Project.create_module(...)` as the normal SDK verb for adding a new module. It writes files by default and returns the same plan payload used for diagnostics. It accepts either an unambiguous family shorthand such as `idea` or a full template id such as `hoi4:idea/basic`. If one project-local template matches a family, ParaDev uses it before built-ins; if multiple templates match, pass the full template id from `Project.templates()`. `Project.scaffold_module(...)` remains the lower-level name for callers that want to dry-run scaffold planning before writing.

Template argument defaults can reference scaffold values such as `{object_id}`, `{family}`, `{family_tag}`, `{module_id}`, and the generated `{title}`. `family_tag` strips a matching uppercase family prefix from the object id, so `IDEA_GER_INDUSTRY` becomes `GER_INDUSTRY` for an `idea` template. Each template argument in `Project.templates()` includes an `advanced` flag. GUI and script helpers should show non-advanced fields first and keep advanced fields behind an optional section because they already have defaults.

Use `Project.templates()` to inspect available authoring templates. Built-in templates cover system families; project-local templates can be declared in top-level `paradev.yaml` `templates` when a module needs different arguments or starter files:

`meta.yaml` is optional in the canonical typed module layout. The family and
object id come from `modules/{family}/{object_id}`. A template that needs a
display label can write only `title`; omit the file when it has no authored
metadata.

```yaml
templates:
  modifier/custom:
    title: Custom Modifier
    family: modifier
    args:
      title:
        required: true
      bonus:
        default: "0.05"
    files:
      meta.yaml: |
        title: {title}
      def.txt: |
        {object_id} = {{
          stability_factor = {bonus}
        }}
      main.loc: |
        [en.{object_id}]
        {title}

        [en.{object_id}_desc]
        Custom modifier.
```

Template rows include `authoring_ready`. It is `true` when the template's `family` is registered by the current HoI4 profile, a project-local `families` declaration, or a project Python registry module. Each row also includes `family_id`, the stable browser/workspace identity for that Registry family; GUI and agent clients should use it instead of maintaining their own singular/plural family table. If `authoring_ready` is `false`, the row includes `diagnostic_codes: ["template.unknown_family"]`, and `Project.scaffold_module(...)` will ask you to declare that family before it writes files. The payload also includes `index` maps for `id`, `family`, `family_id`, `source`, `authoring_ready`, and `diagnostic_code`, so scripts and GUI clients can jump to relevant rows without scanning the table themselves. The `family` filter accepts either Registry or browser identity. Pass filters such as `template_id=...`, `family=...`, `source=...`, `authoring_ready=True`, or `diagnostic_code=...` to return a smaller table; the returned index always points into the filtered table.

The same template surface is available from the CLI. `templates` is read-only, while `scaffold` returns a dry plan unless `--write` is present. Scaffold plans include the same nested `authoring_plan` payload as `Project.authoring_plan(...)`, so a tool can show whether the target's expected source slots are still `empty`, already `satisfied`, or blocked by diagnostics before asking the user to write files:

```bash
rtk uv run paradev templates projects/starter-mod --json
rtk uv run paradev templates projects/starter-mod --family idea --authoring-ready --json
rtk uv run paradev scaffold projects/starter-mod hoi4:idea/basic GER_industry_spirit \
  --value "title=German Industry Spirit" \
  --value "description=Industrial production spirit." \
  --write \
  --json
```

For multi-root projects, `Project.templates()` and `paradev templates` list valid source roots and mark the default root. Pass `source_root="imports"` to `Project.scaffold_module(...)` or `--source-root imports` to the CLI when the new module should live outside the default root. The nested authoring plan uses that selected source root too.

When you are building a GUI, importer, or project-local family workflow, use `Project.families()["authoring"]` for the source roots and canonical `modules/{family}/{object_id}` / `collections/{family}/{collection_id}` folder templates. Each family row includes `metadata.keys` for all accepted top-level `meta.yaml` keys, `metadata.common_keys` for SDK-wide keys, `metadata.family_keys` for compiler-owned keys, and `metadata.unknown_key_policy` for loose/strict severity. It also includes `outputs`, a derived list of artifact types the compiler can plan, with template key, template text, owner kind, target root, and route or sprite-slot context when applicable. The same payload includes an `index` that maps family ids, compiler kinds, source slots, collection descriptor slots, sprite slots, routes, output artifact types, and artifact writer types to returned row numbers. `index["output_artifact_type"]` points at family rows; `index["artifact_type"]` points at writer rows. `Project.templates()` answers "which ready-made starter files can I use?", while `Project.families()` answers "which family contracts, authoring locations, and output plans does this profile support?".

Filter `Project.families(...)` when a tool only needs one contract:

```python
idea_contract = project.families(
    family="idea",
    source_slot="icon",
    artifact_type="sprite_gfx",
)
sprite_output = idea_contract["families"][0]["outputs"][-1]
assert sprite_output["artifact_type"] == "sprite_gfx"
assert idea_contract["index"]["output_artifact_type"]["sprite_gfx"] == [0]
```

Use `Project.authoring_path(...)` when a tool needs one concrete destination without creating files:

```python
path_plan = project.authoring_path("module", "idea", "GER_industry_spirit")
print(path_plan["root"])
```

Use `Project.authoring_plan(...)` when the same tool also needs to show the source files that the selected family expects before anything is written:

```python
plan = project.authoring_plan("module", "idea", "GER_industry_spirit")
for slot in plan["source_slots"]:
    print(slot["slot"], slot["status"], slot["match"], slot["relative_paths"])
```

Each source slot row reports `status`, `source_count`, `relative_paths`, `paths`, and `diagnostic_codes` when diagnostics apply. Exact source slots also report `suggested_relative_paths` and `suggested_paths`, even when already satisfied, so a GUI, importer, REST client, or MCP tool can show the expected file location for missing required slots. Use `empty` for optional slots with no files, `missing` for required slots with no files, `satisfied` for matched slots, and `diagnostic` for matched slots with slot-level problems such as collisions or too many matches. The `index["status"]` map lets tools find missing and diagnostic rows without running a build or duplicating slot matching.

Adapters that already have explicit project roots and source roots can call `paradev.build.authoring_path_view(...)`, `authoring_plan_view(...)`, or `authoring_view(...)` for the same JSON-safe authoring payloads without loading a `Project` wrapper.

REST and MCP clients should use the same surface names instead of copying CLI behavior. The OpenAPI seed exposes `/projects/templates`, `/projects/authoring-path`, `/projects/authoring-plan`, and `/projects/scaffold`; the MCP contract exposes read-only `project_templates`, `project_authoring_path`, `project_authoring_plan`, plus write-capable `project_scaffold`. These routes return the same SDK-owned payloads as `Project.templates()`, `Project.authoring_path(...)`, `Project.authoring_plan(...)`, and `Project.scaffold_module(...)`.

Inspect build surfaces:

```python
project = Project.load("demos/assets/projects/minimal")

families = project.families()
modules = project.modules()
artifacts = project.artifacts()
diagnostics = project.diagnostics()
source_slots = project.source_slots()
sources = project.sources()
source_map = project.source_map()
```

Use `Project.source_slots(...)` when a script or UI needs to answer "which expected files are present or missing for this module?" without joining family contracts and source rows by hand. Each row includes the owner, family, declared slot pattern or patterns, loader kind when known, matched paths, diagnostic codes, and a slot-level status: `satisfied`, `missing`, `empty`, or `diagnostic`.

```python
missing_slots = project.source_slots(status="missing")
idea_slots = project.source_slots(family="idea", module_id="idea/GER_industry_spirit")
```

Use `Project.sources(...)` when a script needs the actual source file rows directly. Pass `owner_kind="collection"` when a collection descriptor screen needs descriptor-owned source files only:

```python
collection_sources = project.sources(collection_id="GER_main", owner_kind="collection")
module_sources = project.sources(collection_id="GER_main", owner_kind="module")
```

Use `Project.inspect("catalog-preview")` for a read-only HeavenBase-ready catalog payload, and use `Project.inspect("catalog-query", ...)` after a catalog has been written or refreshed:

```python
from paradev.hb import catalog_refresh
from paradev.sdk import Project

project = Project.load("demos/assets/projects/minimal")
catalog_refresh(project)
catalog = project.inspect("catalog-preview")
pdx_sources = project.inspect("catalog-query", entity="source-file", tag="loader:pdx")
```

Catalog writes enable the HeavenBase `hoi4` extension and persist rows as `hoi4-*` entities; `catalog-query` still accepts short entity selectors such as `source-file` and `pdx-symbol`. The catalog `source-file` rows come from the same `sources.json` payload as `Project.sources(...)`, with extra Catalog tags such as `module:focus/GER_sample`, `slot:def`, `loader:pdx`, and `status:loaded`. Read `pdx_sources["rows"][0]["data"]` for the original source inventory row after a catalog search hit.

REST clients can use the same catalog boundary without learning HeavenBase internals: `GET /projects/catalog` reports the default local database status through `Project.catalog_status()` without creating it, `POST /projects/catalog` writes a new catalog database through `paradev.hb.catalog_write(...)`, `PUT /projects/catalog` refreshes it through `paradev.hb.catalog_refresh(...)`, and `GET /projects/inspect?kind=catalog-query` reads rows through the SDK inspection dispatcher.

Adapter-style clients can dispatch by kind instead of duplicating command routing:

```python
modules = project.inspect("modules", family="focus", source_slot="def")
missing_slots = project.inspect("source-slots", status="missing")
sources = project.inspect("sources", module_id="focus/GER_sample", loader="pdx")
collection_sources = project.inspect("sources", collection_id="GER_main", owner_kind="collection")
assets = project.inspect("assets", module_id="focus/GER_sample", file_format="png")
sprites = project.inspect("sprites", module_id="idea/GER_industry_spirit", name="GFX_idea_GER_industry_spirit")
graph = project.inspect("build-graph", module_id="focus/GER_sample")
explain = project.inspect("build-explain", module_id="focus/GER_sample")
catalog = project.inspect("catalog-query", entity="source-file", tag="loader:pdx")
```

`build-graph` is the inspection for visual trace panels. Each node keeps stable ids plus `type`, `label`, and source/artifact fields, and adds `group`, `display_label`, `display_detail`, and `display_path` for UI grouping and compact rendering. Use `graph["index"]["nodes_by_group"]` to select groups such as `artifact:output`, `module:focus`, `source:focus`, or `reference:idea` without scanning every node.

Use the direct methods in normal Python scripts when the target is known. Use `Project.inspect(...)` when a GUI, MCP tool, REST route, importer, or CLI adapter receives the inspection kind and filters from a user action. Use `Project.inspections()` when that adapter needs to list supported kinds and filter names:

```python
contract = project.inspections()
module_filters = contract["index"]["filter"]["module_id"]
```

For maintained inspection kind/filter tables, use [Project Inspection Reference](project-inspection-reference.md), generated by `rtk uv run paradev inspections --markdown`. Code that only needs one slice should prefer `get_project_inspection_kinds()`, `get_project_inspection_row(kind)`, `get_project_inspection_index_catalog()`, or `get_project_inspection_filter_kinds(filter_name)` instead of reading raw indexes.

Static adapter registration does not need a loaded project. Use `get_project_inspection_contract()` when a CLI, MCP, REST/OpenAPI, or GUI bridge only needs the SDK-owned list of inspection kinds, CLI command names, and filters:

```python
from paradev.sdk import get_project_inspection_contract

contract = get_project_inspection_contract()
source_filters = contract["index"]["filter"]["slot"]
```

Use `get_frontend_api_contract()` when a GUI, importer, desktop app, MCP bridge, REST client, or VS Code extension needs the full maintained operation list. Read `api["summary"]` first for SDK-owned operation, group, status, read/write, and workspace-section counts before adding a new frontend action. Use `get_frontend_api_operation(...)` or `get_frontend_api_group(...)` when the caller already knows the stable id, `get_frontend_api_group_operation_ids(...)` or `get_frontend_api_status_operation_ids(...)` when it needs group/status operation-id lists, `get_frontend_api_mode_operation_ids(...)` when it needs a read/write operation-id list, `get_frontend_api_workspace(...)` for SDK-owned navigation, `get_frontend_api_action(...)` when it needs one selected action's workspace row, derived form, bindings, execution hints, and option-source summary, `get_frontend_api_form(...)` when it needs a derived field schema for one action, `resolve_frontend_api_options(...)` when a field has an SDK-owned dynamic option source, `normalize_frontend_api_inputs(...)` when it needs submitted form state split into project loading, SDK parameters, selectors, and projections, `plan_frontend_api_rest_request(...)` when it needs the REST method, path, query, and JSON body for the same submitted state, `get_frontend_api_binding_lookup(...)`, `get_frontend_api_binding_operation_ids(...)`, `get_frontend_api_binding_index(...)`, or `get_frontend_api_rest_operation_ids(...)` when it needs to map a surface call key or whole adapter surface back to stable operation ids, `get_frontend_api_surface_operation_ids(...)`, `get_frontend_api_payload_operation_ids(...)`, or `get_frontend_api_workspace_section_operation_ids(...)` when it needs grouped operation lists without scanning rows, and `render_frontend_api_typescript()` when it needs to regenerate the checked-in desktop TypeScript source artifact. Desktop TypeScript code should import workspace action rows, binding helpers, input/default/option-source helpers, endpoint/request/payload helpers, and typed helper lookups from `apps/desktop/src/data/frontendApi.ts` instead of reaching into the generated file directly:

Use `get_frontend_api_index_catalog()` when docs, audits, or generated clients need the maintained map from each raw `contract["index"]` path to its Python and TypeScript helper.

Use `frontendApiWorkspaceSections` for desktop sidebars and tabs; use `frontendApiWorkspaceActions`, `getFrontendApiSectionActions(...)`, `getFrontendApiDefaultSectionAction(...)`, and `getFrontendApiRequiredInputNames(...)` for action rows. Use `getFrontendApiActionPanelState(...)` for selected-action panels that need the operation summary, execution surfaces, generated fields, defaults, option-source field names, controls, option requests, normalize/rest-plan requests, confirmation state, Run state, and stable request keys. Keep local selected-action values in React state, but pass them through the helper before rendering field and execution state. Use `resolveFrontendApiFormOptionRequest(...)` to execute available option requests and render `ready`, `unavailable`, or `error` result state. Feed those results back into the panel-state helper so static choices and SDK option payload rows render through the same select-control option model. Use `resolveFrontendApiNormalizeRequest(...)` and `resolveFrontendApiRestPlanRequest(...)` when an execution-plan panel needs SDK-owned normalization and REST request planning state for the same submitted values. Once the REST plan is ready and Run state is enabled, use `buildFrontendApiRestExecutionRequest(...)` and `resolveFrontendApiRestExecutionRequest(...)` to execute the planned target request through the configured REST bridge; direct component-level `fetch` calls should not own URL, body, or bridge-unavailable shaping. Use `frontendApiBindingIndex`, `getFrontendApiBindingOperationIds(...)`, and `getFrontendApiRestOperationIds(...)` when codegen or inspectors need to map a surface call key back to stable operation ids; use `frontendApiGroupIndex`, `frontendApiStatusIndex`, `getFrontendApiGroupOperationIds(...)`, and `getFrontendApiStatusOperationIds(...)` when API tables need group/status operation-id slices; use `frontendApiModeIndex` and `getFrontendApiModeOperationIds(...)` when API tables need read/write operation-id slices. Keep tab and sidebar state on the generated workspace-section id type.

After changing the TypeScript helper, run `rtk npm --prefix apps/desktop run test:unit` for direct summary/group registry alignment, binding-index helper, panel-state, request/resolver, and bridge-unavailable helper coverage, then run the desktop build for TypeScript/Vite integration.

```python
from paradev.sdk import (
    FRONTEND_API_ACTION_DETAIL_SCHEMA,
    FRONTEND_API_ACTION_SCHEMA,
    FRONTEND_API_BINDING_LOOKUP_SCHEMA,
    FRONTEND_API_BINDING_SURFACES,
    FRONTEND_API_FORM_SCHEMA,
    FRONTEND_API_INPUTS_SCHEMA,
    FRONTEND_API_OPTIONS_SCHEMA,
    FRONTEND_API_OPTION_SOURCE_SCHEMA,
    FRONTEND_API_REST_REQUEST_SCHEMA,
    FRONTEND_API_SELECTORS,
    FRONTEND_API_SUMMARY_SCHEMA,
    FRONTEND_API_WORKSPACE_SCHEMA,
    build_frontend_api_rest_index_key,
    get_frontend_api_contract,
    get_frontend_api_action,
    get_frontend_api_binding_index,
    get_frontend_api_binding_lookup,
    get_frontend_api_binding_operation_ids,
    get_frontend_api_form,
    get_frontend_api_group,
    get_frontend_api_group_operation_ids,
    get_frontend_api_index_catalog,
    get_frontend_api_mode_operation_ids,
    get_frontend_api_operation,
    get_frontend_api_payload_operation_ids,
    get_frontend_api_rest_operation_ids,
    get_frontend_api_status_operation_ids,
    get_frontend_api_surface_operation_ids,
    get_frontend_api_workspace,
    get_frontend_api_workspace_section_operation_ids,
    normalize_frontend_api_inputs,
    plan_frontend_api_rest_request,
    render_frontend_api_typescript,
    resolve_frontend_api_options,
)

api = get_frontend_api_contract()
workspace = get_frontend_api_workspace()
assert api["summary"]["schema"] == FRONTEND_API_SUMMARY_SCHEMA
assert api["summary"]["operation_count"] == len(api["operations"])
assert api["summary"]["workspace_section_count"] == len(workspace["sections"])
module_operations = get_frontend_api_group_operation_ids("modules")
planned_operations = get_frontend_api_status_operation_ids("planned")
write_operations = get_frontend_api_mode_operation_ids("write")
index_catalog = get_frontend_api_index_catalog()
project_cli_operations = get_frontend_api_binding_operation_ids("cli", "project")
cli_binding_index = get_frontend_api_binding_index("cli")
project_list_operations = get_frontend_api_binding_operation_ids("cli", "projects")
project_browser_operations = get_frontend_api_binding_operation_ids("cli", "project-browser")
template_operations = get_frontend_api_binding_operation_ids("cli", "templates")
module_rest_operations = get_frontend_api_rest_operation_ids("GET", "/projects/inspect", {"kind": "modules"})
project_browser_rest_operations = get_frontend_api_rest_operation_ids("GET", "/projects/browser")
rest_surface_operations = get_frontend_api_surface_operation_ids("rest")
project_view_payload_operations = get_frontend_api_payload_operation_ids("Project.to_view")
catalog_section_operations = get_frontend_api_workspace_section_operation_ids("catalog")
module_list = get_frontend_api_operation("module.list")
module_group = get_frontend_api_group("modules")
module_create_detail = get_frontend_api_action("module.create")
assert workspace["schema"] == FRONTEND_API_WORKSPACE_SCHEMA
assert workspace["sections"][0]["id"] == "project-switcher"
assert "module.edit" in workspace["index"]["section"]["source-editor"]
source_editor = next(section for section in workspace["sections"] if section["id"] == "source-editor")
module_edit_action = next(action for action in source_editor["actions"] if action["operation_id"] == "module.edit")
assert module_edit_action["schema"] == FRONTEND_API_ACTION_SCHEMA
assert module_edit_action["execution"]["default_surface"] == "rest"
assert module_edit_action["execution"]["rest_request_schema"] == FRONTEND_API_REST_REQUEST_SCHEMA
assert module_create_detail["schema"] == FRONTEND_API_ACTION_DETAIL_SCHEMA
assert module_create_detail["sections"] == ["authoring"]
assert module_create_detail["option_fields"] == ["template_id", "source_root"]
assert get_frontend_api_operation("surface.frontend_api")["selectors"] == list(FRONTEND_API_SELECTORS)
assert FRONTEND_API_BINDING_SURFACES == ("cli", "lsp", "mcp", "rest", "sdk")
assert build_frontend_api_rest_index_key("GET", "/projects/inspect", {"kind": "modules"}) == "GET /projects/inspect?kind=modules"
assert get_frontend_api_binding_lookup("rest", "GET /projects/inspect?kind=modules") == {
    "schema": FRONTEND_API_BINDING_LOOKUP_SCHEMA,
    "surface": "rest",
    "key": "GET /projects/inspect?kind=modules",
    "operation_ids": ["module.list"],
    "count": 1,
}
assert module_list["bindings"]["rest"] == {"method": "GET", "path": "/projects/inspect", "query": {"kind": "modules"}}
assert project_cli_operations == ["project.open", "project.view"]
assert project_list_operations == ["project.list"]
assert project_browser_operations == ["project.browser"]
assert template_operations == ["module.templates"]
assert module_rest_operations == ["module.list"]
assert project_browser_rest_operations == ["project.browser"]
project_state_form = get_frontend_api_form("project.state")
assert project_state_form["defaults"] == {"project_paths": [], "search_roots": []}
project_browser_form = get_frontend_api_form("project.browser")
assert project_browser_form["fields"][2]["label"] == "Kind"
assert project_browser_form["fields"][2]["choices"] == ["module", "collection"]
module_edit_form = get_frontend_api_form("module.edit")
assert module_edit_form["schema"] == FRONTEND_API_FORM_SCHEMA
assert module_edit_form["required"] == ["module_id", "relative_path", "text"]
assert module_edit_form["fields"][3]["label"] == "Text"
assert "source file" in module_edit_form["fields"][3]["description"]
module_create_form = get_frontend_api_form("module.create")
module_create_fields = {field["name"]: field for field in module_create_form["fields"]}
template_source = module_create_fields["template_id"]["option_source"]
assert template_source["schema"] == FRONTEND_API_OPTION_SOURCE_SCHEMA
assert template_source["operation_id"] == "module.templates"
assert template_source["values_path"] == ["templates"]
assert module_create_fields["source_root"]["option_source"]["values_path"] == ["source_roots"]
template_options = resolve_frontend_api_options("module.create", "template_id", {"path": "demos/assets/projects/minimal"})
assert template_options["schema"] == FRONTEND_API_OPTIONS_SCHEMA
assert template_options["provider_operation_id"] == "module.templates"
assert template_options["options"][0]["value"] == "hoi4:idea/basic"
source_file_options = resolve_frontend_api_options("module.file", "relative_path", {"path": "demos/assets/projects/minimal"})
assert source_file_options["available"] is False
assert source_file_options["missing_requirements"] == ["module_id"]
build_artifacts_form = get_frontend_api_form("build.artifacts")
assert build_artifacts_form["json_schema"]["properties"]["target_root"]["enum"] == ["output", "build"]
lsp_hover_form = get_frontend_api_form("lsp.hover")
assert lsp_hover_form["fields"][1]["description"].startswith("Zero-based")
assert lsp_hover_form["json_schema"]["properties"]["line"]["minimum"] == 0
module_edit_values = normalize_frontend_api_inputs(
    "module.edit",
    {"module_id": "modifier/example", "relative_path": "def.txt", "text": "modifier = { value = 1 }"},
)
assert module_edit_values["schema"] == FRONTEND_API_INPUTS_SCHEMA
assert module_edit_values["project"] == {"path": "."}
assert module_edit_values["parameters"]["relative_path"] == "def.txt"
module_edit_request = plan_frontend_api_rest_request(
    "module.edit",
    {"module_id": "modifier/example", "relative_path": "def.txt", "text": "modifier = { value = 1 }"},
)
typescript_contract = render_frontend_api_typescript()
assert module_edit_request["schema"] == FRONTEND_API_REST_REQUEST_SCHEMA
assert module_edit_request["method"] == "PATCH"
assert module_edit_request["path"] == "/projects/modules/file"
assert module_edit_request["body"]["text"].startswith("modifier")
assert "ParaDevFrontendApiOperationId" in typescript_contract
assert '"module.create",' in typescript_contract
project_create_inputs = get_frontend_api_operation("project.create")["inputs"]
module_edit_inputs = get_frontend_api_operation("module.edit")["inputs"]
collection_create_inputs = get_frontend_api_operation("collection.create")["inputs"]
collection_rename_inputs = get_frontend_api_operation("collection.rename")["inputs"]
collection_remove_inputs = get_frontend_api_operation("collection.remove")["inputs"]
pdx_format_inputs = get_frontend_api_operation("pdx.format")["inputs"]
lsp_hover_inputs = get_frontend_api_operation("lsp.hover")["inputs"]
build_artifacts_inputs = get_frontend_api_operation("build.artifacts")["inputs"]
project_state_inputs = get_frontend_api_operation("project.state")["inputs"]
project_browser_inputs = get_frontend_api_operation("project.browser")["inputs"]
catalog_query_inputs = get_frontend_api_operation("catalog.query")["inputs"]
frontend_selector_inputs = get_frontend_api_operation("surface.frontend_api")["inputs"]
```

Operation rows include machine-readable `bindings` for SDK, CLI, REST, MCP, and LSP surfaces when those surfaces exist. The workspace projection carries SDK-owned navigation sections and `paradev.sdk.frontend-api.action.v1` action rows for GUI shells; each action row publishes derived execution hints such as `execution.default_surface`, `execution.available_surfaces`, `execution.confirmation`, callable `bindings`, `form_schema`, `normalizer_schema`, and `rest_request_schema`. `get_frontend_api_action(...)`, CLI `frontend-api --operation ... --action`, and REST `GET /frontend-api/action?operation_id=...` return the same `paradev.sdk.frontend-api.action-detail.v1` payload for one selected action so frontend code does not stitch workspace, form, bindings, and option-source details by hand. `execution.confirmation` uses `paradev.sdk.frontend-api.confirmation.v1`; non-local mutating actions set `required=true`, carry a `scope` such as `project-files` or `catalog`, a `style` such as `write` or `destructive`, and list `confirm_fields` that should stay false until the user confirms. `render_frontend_api_typescript()` and CLI `frontend-api --typescript` generate `apps/desktop/src/generated/frontendApi.ts`, which exports operation id unions and the full SDK-owned contract; the desktop helper at `apps/desktop/src/data/frontendApi.ts` wraps that generated file with summaries, `frontendApiWorkspaceActions`, `getFrontendApiAction(...)`, `getFrontendApiActionDetail(...)`, `getFrontendApiActionPanelState(...)`, `getFrontendApiFormControls(...)`, `getFrontendApiFormControlKind(...)`, `getFrontendApiFormValuesWithDefaults(...)`, `getFrontendApiFormOptionRequests(...)`, `resolveFrontendApiFormOptionRequest(...)`, `resolveFrontendApiNormalizeRequest(...)`, `resolveFrontendApiRestPlanRequest(...)`, `buildFrontendApiRestExecutionRequest(...)`, `resolveFrontendApiRestExecutionRequest(...)`, `getFrontendApiActionRunState(...)`, `getFrontendApiSectionActions(...)`, `getFrontendApiDefaultSectionAction(...)`, `getFrontendApiBindings(...)`, `getFrontendApiRestBinding(...)`, `frontendApiInputOperations`, `getFrontendApiInputs(...)`, `getFrontendApiRequiredInputNames(...)`, `getFrontendApiDefaultValues(...)`, `getFrontendApiOptionSourceInputs(...)`, `frontendApiEndpointPaths`, `buildFrontendApi*Url(...)`, and JSON request helpers such as `buildFrontendApiOptionsRequest(...)`, `buildFrontendApiNormalizeRequest(...)`, and `buildFrontendApiRestPlanRequest(...)` for TypeScript clients. Form rows carry SDK-owned `label` and `description` text, `choices`, select controls, dynamic `option_source` provider hints, and numeric bounds such as LSP hover `minimum=0`; `normalize_frontend_api_inputs(...)` enforces those constraints before adapters call SDK or REST. Frontend shells may keep local submitted values per selected action, but `getFrontendApiActionPanelState(...)` owns the common selected-action view model: detail, fields, defaults, option requests, controls, normalize/rest-plan requests, confirmation state, Run state, and stable request keys. Use `resolve_frontend_api_options(...)` to populate project-derived choices from `option_source`, for example templates from `module.templates`, families from `build.families`, module ids from `module.list`, collection ids from `collection.list`, artifacts from `build.artifacts`, and diagnostics from `build.diagnostics`; the resolver returns `available=false` plus `missing_requirements` when upstream fields are not filled yet. Use those objects for generated clients and adapters, then request the same SDK-owned adapters instead of reimplementing them: `paradev frontend-api --workspace` returns the same `paradev.sdk.frontend-api.workspace.v1` payload as `get_frontend_api_workspace(...)`; `paradev frontend-api --operation ... --option-field ... --values-json ...` and `POST /frontend-api/options?operation_id=...&field_name=...` return the same `paradev.sdk.frontend-api.options.v1` payload as `resolve_frontend_api_options(...)`; `paradev frontend-api --operation ... --values-json ...` and `POST /frontend-api/normalize?operation_id=...` return the same `paradev.sdk.frontend-api.inputs.v1` payload as `normalize_frontend_api_inputs(...)`; `paradev frontend-api --operation ... --values-json ... --rest-request` and `POST /frontend-api/rest-request?operation_id=...` return the same `paradev.sdk.frontend-api.rest-request.v1` payload as `plan_frontend_api_rest_request(...)`; `paradev frontend-api --binding-surface ... --binding-key ...` and `GET /frontend-api/binding?binding_surface=...&binding_key=...` return the same `paradev.sdk.frontend-api.binding-lookup.v1` payload as `get_frontend_api_binding_lookup(...)`. The reverse `api["index"]["binding"]` map answers which frontend operation ids belong to each surface call key, but Python clients should prefer `get_frontend_api_binding_operation_ids(...)` or `get_frontend_api_rest_operation_ids(...)`; static CLI/MCP contracts expose their slices as `frontend_operation_ids`. OpenAPI operations also carry `x-paradev-frontend-api-operation-ids`, derived from `bindings.rest`, for codegen that starts from the REST document; the Python architecture suite verifies every declared binding is indexed and every REST binding has that OpenAPI annotation.

Desktop confirmation acceptance is frontend-local state over SDK-owned policy. TypeScript clients should store accepted operations in `FrontendApiActionConfirmationStates`, call `isFrontendApiActionConfirmationSatisfied(...)` before enabling Run, and reset accepted state when submitted form values change.

`get_lsp_contract()["frontend_operation_ids"]` mirrors the LSP slice of the same frontend API binding index, so LSP adapters can map `textDocument/*` methods back to canonical operation ids without scanning raw operation rows.

Desktop Run state is frontend-local rendering over SDK-owned policy and REST state. TypeScript clients should call `getFrontendApiActionRunState(...)` and render its `disabled`, `detail`, `status`, and `confirmation_satisfied` fields instead of reimplementing confirmation or REST result interpretation.

Desktop selected-action panels should call `getFrontendApiActionPanelState(...)` when they need the common action detail/form/options/execution bundle. This keeps effect keys and request payloads aligned with the helper instead of scattered across components.

Use `Project.remove_module(...)` as a plan-first destructive operation:

```python
plan = project.remove_module("modifier/starter_starter_modifier")
for source in plan["files"]:
    print(source["module_relative_path"])

removed = project.remove_module("modifier/starter_starter_modifier", write=True)
assert removed["removed"]
```

A written removal atomically moves the canonical folder into `.paradev/module-trash` under the same source root, leaves any configured Catalog fail-closed as stale, and then deletes that quarantine copy best-effort. If cleanup cannot finish, `removed` remains `True`; the payload adds a warning diagnostic and `cleanup` with schema `paradev.module.remove-cleanup.v1`, status `pending`, and the project-local tombstone path. Do not retry the module removal.

Written module create, rename, remove, and contained source-draft calls invalidate an existing project Catalog before changing source files. One module change may also change HOI4 entities, localization, PDX symbols, source rows, graph rows, and artifacts, so ParaDev refuses to label a module-only row update as coherent. A written `Project.create_module(...)` or `Project.scaffold_module(...)` plan carries `plan["catalog_mutation"]`; `Project.rename_module(...)` and a completed `Project.remove_module(..., write=True)` carry the same field at the payload top level. The payload schema remains `paradev.hb.catalog-mutation.v1`:

- `not_configured` with `catalog.mutation.not_configured` means the source change succeeded but this project has no prepared Catalog yet.
- `failed` with `catalog.mutation.failed` and an actionable Refresh message means the source change succeeded and the previously prepared Catalog is now deliberately stale. `Project.catalog_status()` reports `incomplete`, and Catalog queries/completions fail closed until `catalog_refresh(...)` rebuilds every dependent projection.
- `applied` with `catalog.mutation.applied` is reserved for a future coherent multi-entity delta and is not emitted by current module authoring.

Do not retry the source operation when refresh is required; use the app's Catalog Refresh action. Dry runs, blocked plans, and removals that were not written omit `catalog_mutation`. This keeps the primary result unambiguous: `written` or `removed` describes the filesystem operation, while `catalog_mutation` describes its derived search/index projection.

Module scaffold writes, folder rename, and removal require descriptor-anchored, no-follow directory operations. Scaffold destinations remain lexical. A write stages the complete rendered file set under `source_root/.paradev/module-transactions` before installing anything, retains forced-replacement backups until the final identity check, and rolls back ordinary staging or installation failures. If restoring an original also fails, the blocked plan reports `scaffold.rollback_incomplete` with a `recovery_path` and leaves that transaction intact instead of deleting the last recoverable copy. A concurrent component swap blocks and rolls back a new partial module. ParaDev fails these operations closed on hosts that cannot provide the required primitives; a path-based fallback is intentionally not used because it could follow a concurrently replaced symlink.

When a Registry-owned tree provider creates a standalone child and also edits an existing parent source, ParaDev adds a fixed hidden compound journal at `.paradev/diagram-module-transaction`. A later launch/build first recovers the normal source transaction and then reconciles the child from exact hashes: an old parent removes only an exact ParaDev-owned child or partial child, while a committed parent keeps only the complete exact child. Extra or changed child content is preserved and reported as an actionable recovery failure. Users do not maintain this journal; a successful operation or recovery clears its record automatically.

External importers that replace a complete project-source subtree should coordinate with builds and GUI/SDK edits through the public project lock:

```python
from paradev.sdk import project_source_mutation_lock

with project_source_mutation_lock(project.root):
    sources = snapshot_and_validate_sources()
    publish_transaction(sources)
```

Hold the lock from the first source read through the final publication rename, and pass the same lexical project root that `Project.load(...)` uses. The lock coordinates writers; the importer must still reject symlinks, validate its staged tree, and retain a recoverable backup for an interrupted swap.

Use `Project.rename_collection(...)` to move a collection descriptor without rewriting authored content:

```python
renamed = project.rename_collection("germany", "france", family="event")
assert renamed["collection_id"] == "france"
assert renamed["content_rewritten"] is False
```

Use `Project.remove_collection(...)` to preserve and ungroup member modules before removing a descriptor:

```python
plan = project.remove_collection("germany", family="event")
for source in plan["files"]:
    print(source["collection_relative_path"])

removed = project.remove_collection(
    "germany",
    family="event",
    write=True,
    plan_hash=plan["plan_hash"],
)
assert removed["removed"]
```

The plan lists `members` and `member_files`. Applying it clears explicit collection pointers in visible and hidden metadata, preserves unrelated settings, and removes the descriptor in one crash-recoverable transaction. It never deletes member modules.

Adapters that already hold a `BuildRegistry` plus project context can call `paradev.build.families_view(...)` for the same family contract payload that `Project.families(...)` returns. Compiler tests or adapters that already have a `BuildResult` can call the build-layer helpers directly, for example `paradev.build.summary_view(result)`, `manifests_view(result)`, `modules_view(result, family="focus")`, `sources_view(result, loader="pdx")`, `assets_view(result, file_format="png")`, `sprites_view(result, family="idea")`, or `diagnostics_view(result, severity="error")`. These helpers return the same payload shapes and rebuilt indexes that the SDK methods expose.

Parse or format PDX without running a project build:

```python
from paradev.sdk import (
    diagnose_pdx_lsp_text,
    document_symbols_pdx_lsp_text,
    format_pdx_file,
    format_pdx_lsp_text,
    format_pdx_text,
    hover_pdx_lsp_text,
    parse_pdx_file,
)

payload = parse_pdx_file(
    "demos/assets/projects/minimal/src/modules/focus/GER_sample/def.txt",
    include_tokens=True,
)
assert payload["ok"]

formatted = format_pdx_text("focus={id=GER_sample cost=10}", path="focus.pdx")
assert formatted["formatted_text"].startswith("focus = {")

preview = format_pdx_file("demos/assets/projects/minimal/src/modules/focus/GER_sample/def.txt")
assert preview["schema"] == "paradev.pdx.format.v1"

lsp_format = format_pdx_lsp_text("focus={id=GER_sample cost=10}", uri="file:///workspace/focus.pdx")
assert lsp_format["schema"] == "paradev.lsp.formatting.v1"

lsp_diagnostics = diagnose_pdx_lsp_text("value = 0x", uri="file:///workspace/broken.pdx")
assert lsp_diagnostics["schema"] == "paradev.lsp.diagnostics.v1"

lsp_symbols = document_symbols_pdx_lsp_text("focus={id=GER_sample}", uri="file:///workspace/focus.pdx")
assert lsp_symbols["schema"] == "paradev.lsp.symbols.v1"

lsp_hover = hover_pdx_lsp_text("focus={id=GER_sample}", 0, 8, uri="file:///workspace/focus.pdx")
assert lsp_hover["schema"] == "paradev.lsp.hover.v1"
```

Run a dry build and inspect records directly:

```python
result = Project.load("demos/assets/projects/minimal").build()

for artifact in result.artifacts:
    print(artifact.path, artifact.artifact_type, artifact.owner)
```

In HoI4 builds, `mod_descriptor` artifacts are project-owned. Expect `descriptor.mod` under the output root and `launcher/<project_id>.mod` under the build root when `emit_artifacts=True`.

Emit files:

```python
result = Project.load("demos/assets/projects/minimal").build(
    emit_artifacts=True,
    emit_manifests=True,
)
```

Important rule: all GUI, MCP, REST, LSP, and script integrations should call the SDK rather than reimplement HoI4 business logic.

## 中文

CLI 是 SDK 的薄封装。需要自动化、测试或自定义脚本时，优先使用 SDK。

如果需要查看 API reference table 的总目录，请阅读 [API Catalog Reference](api-catalog-reference.md)。它由 `paradev.surfaces.get_api_catalog_table()` 生成，列出每个 SDK、CLI、REST、MCP、frontend 和 surface contract reference 的 schema、row count、index name、owner-module index、surface index、CLI 重新生成命令和文档页面。若要查看 `Project`、`CM_PARADEV`、`__version__` 这类 package-level import，请阅读 [Package API Reference](package-api-reference.md)，它由 `paradev.get_package_api_table()` 生成。若要审计 config default 和共享 ConfigManager facade，请阅读 [Config API Reference](config-api-reference.md)，它由 `paradev.config.get_config_api_table()` 生成。若要审计已安装的 GUI launcher facade，请阅读 [GUI API Reference](gui-api-reference.md)，它由 `paradev.gui.get_gui_api_table()` 生成。若要审计 SDK 拥有的 desktop state helper，请阅读 [Desktop API Reference](desktop-api-reference.md)，它由 `paradev.desktop.get_desktop_api_table()` 生成。若要审计 game profile registry helper，请阅读 [Games API Reference](games-api-reference.md)，它由 `paradev.games.get_games_api_table()` 生成。若要审计 CLI、REST、MCP、LSP、VS Code、bundle、API catalog 和 surface contract helper 这类 surface facade import，请阅读 [Surfaces API Reference](surfaces-api-reference.md)，它由 `paradev.surfaces.get_surfaces_api_table()` 生成。如果需要查看所有公开 `paradev.sdk` import，请阅读 [SDK API Reference](sdk-api-reference.md)。它由 `paradev.sdk.get_sdk_api_table()` 生成，并按 module、feature 和 symbol kind 给 facade 分组，便于维护者不用手动读取 `__all__` 也能审计导出漂移。若要审计公开 `Project` 对象本身，请阅读 [Project API Reference](project-api-reference.md)。它由 `paradev.sdk.get_project_api_table()` 生成，并按 feature、row kind、CLI command、frontend operation 和 inspection kind 给字段和方法分组。若要审计 authoring-template schema 和 scaffold-planning helper，请阅读 [Authoring Templates API Reference](templates-api-reference.md)，它由 `paradev.sdk.templates.get_templates_api_table()` 生成。若要审计 compatibility overlay copy-root helper，请阅读 [Copy Roots API Reference](copy-roots-api-reference.md)，它由 `paradev.sdk.copy_roots.get_copy_roots_api_table()` 生成。若要审计较窄的 `paradev.project` import facade，请阅读 [Project Facade API Reference](project-facade-api-reference.md)，它由 `paradev.project.get_project_facade_api_table()` 生成。若要审计 HOI4 language alias normalization helper，请阅读 [Localization API Reference](localization-api-reference.md)，它由 `paradev.localization.get_localization_api_table()` 生成。若要审计 compiler extension import，例如 build record、family、slot、loader、manifest、view 和 artifact writer，请阅读 [Build API Reference](build-api-reference.md)，它由 `paradev.build.get_build_api_table()` 生成。如果需要查看当前所有 Python SDK 调用和 CLI 命令，请阅读 [SDK 与 CLI API Reference](sdk-cli-reference.md)。它由和 frontend API 相同的 operation contract 生成，并包含按 feature 统计的 SDK/CLI coverage summary，因此是查询 project、module、collection、build、PDX、LSP 或 catalog 相关动词的最短路径。需要按 CLI command 优先查看 adapter 表时，阅读 [CLI API Reference](cli-api-reference.md)，它由 `paradev.surfaces.cli.get_cli_api_table()` 生成。若要审计公开 REST package facade 和 local API server helper，请阅读 [REST Facade API Reference](rest-facade-api-reference.md)，它由 `paradev.api.get_rest_facade_api_table()` 生成。

如果需要审计底层 parser facade 本身，请阅读 [PDX Core API Reference](pdx-core-api-reference.md)，它由 `paradev.pdx.get_pdx_core_api_table()` 生成，并按 module、feature 和 symbol kind 分组 tokenizer、token、AST、parser、diagnostics、scalar constant 和 PDX facade-reference helper import。若要审计公开 LSP server package facade，请阅读 [LSP Server API Reference](lsp-server-api-reference.md)，它由 `paradev.lsp.get_lsp_server_api_table()` 生成，并按 module、feature 和 symbol kind 分组 stdio server、JSON-RPC dispatcher、document cache、framing helper 和 facade-reference helper。

创建并构建起步项目：

```python
from paradev.sdk import Project

project = Project.create("projects/starter-mod", title="Starter Mod")
result = project.build(emit_artifacts=True, emit_manifests=True)
assert not result.blocked
print(result.summary())
```

加载已有项目：

```python
from paradev.sdk import Project

found = Project.find("demos/assets/projects/minimal/src/modules/focus/GER_sample")
assert found["found"]

project = Project.load("demos/assets/projects/minimal")
summary = project.summary()
print(summary["summary"])
```

列出本地已知项目，组合桌面项目状态，并读取项目浏览器树：

```python
from paradev.sdk import Project, desktop_state, registered_projects

registry = registered_projects(search_roots=("demos/assets/projects",))
project_ids = [row["project_id"] for row in registry["projects"]]
state = desktop_state("demos/assets/projects/minimal")
assert state["active_project"]["project_id"] == "minimal_hoi4"
browser = Project.load("demos/assets/projects/minimal").browser(kind="module")
assert browser["items"][0]["module_id"] == "focus/GER_sample"
```

只修改项目显示名称，不移动文件，也不改变 `project_id`：

```python
project = Project.load("projects/starter-mod")
project = project.rename("Renamed Starter Mod")
print(project.to_view()["title"])
```

重命名源模块目录，但不修改文件里的 HoI4 id：

```python
project = Project.load("projects/starter-mod")
payload = project.rename_module(
    "modifier/starter_mod_starter_modifier",
    "starter_mod_renamed_modifier",
    title="Renamed Modifier",
)
print(payload["module_id"])
assert payload["content_rewritten"] is False
```

如果 localization 显示名变更还需要同步可读目录后缀，请通过一次受保护的
draft request 提交两者：

```python
module_root = project.root / "src/modules/idea/IDEA_ALPHA"
payload = project.apply_source_draft(
    source_edits=[
        {
            "path": str(module_root / "main.loc"),
            "text": "[zh.IDEA_ALPHA]\n可读名称\n",
        }
    ],
    module_rename={
        "module_id": "idea/IDEA_ALPHA",
        "object_id": "IDEA_ALPHA",
        "title": "可读名称",
    },
)
print(payload["module_rename"]["root"])
```

读取并替换模块内的一个文本源文件：

```python
project = Project.load("projects/starter-mod")
source = project.read_module_file("modifier/starter_mod_starter_modifier", "def.txt")

updated = source["text"].replace("0.05", "0.10")
payload = project.write_module_file(
    "modifier/starter_mod_starter_modifier",
    "def.txt",
    updated,
)
assert payload["written"]
```

读取 Registry 所属图片或复制资源时，默认不载入原始字节；替换时直接使用 SDK
返回的稳定 revision guard：

```python
import base64

asset = project.read_module_asset(
    "idea/IDEA_ALPHA",
    "icon.png",
)
assert asset["source_slots"]
assert "content_base64" not in asset

payload = project.apply_source_draft(
    source_replacements=[
        {
            **asset["draft_guard"],
            "content_base64": base64.b64encode(new_png_bytes).decode("ascii"),
        }
    ]
)
assert payload["written"]
```

只有确实需要当前字节时才向 `read_module_asset(...)` 传入
`include_content=True`。对于不按 module asset 选择、但仍位于项目内的二进制
路径，`Project.read_source_binary(...)` 提供相同的有界、带 digest 的稳定快照。

对于 Registry 支持的 JSON 或 PDX 源文件，应优先使用引导式控件，而不是直接
替换文本。控件 id 必须来自 `Project.source_form(...)`，不要猜测。先在不写入
文件的情况下规划多个修改，检查准确变更，再一次性应用合并后的 revision-guarded
draft：

```python
def control_id(form, patch_path):
    sections = list(form["sections"])
    while sections:
        section = sections.pop()
        for control in section.get("controls", []):
            if control.get("patch", {}).get("path") == patch_path:
                return control["id"]
        sections.extend(section.get("sections", []))
    raise KeyError(patch_path)


project = Project.load("projects/PIHC3")
first_source = project.read_module_file("entity/VIENTO_MIRROR", "record.json")
second_source = project.read_module_file("entity/VIENTO_AIR_AIRSHIP", "record.json")
first_form = project.source_form(first_source["path"])
second_form = project.source_form(second_source["path"])
assert first_form is not None and second_form is not None

plan = project.plan_source_form_updates(
    [
        {
            "source_path": first_source["path"],
            "values": {control_id(first_form, ["mesh", "scale"]): 4.5},
        },
        {
            "source_path": second_source["path"],
            "values": {control_id(second_form, ["mesh", "scale"]): 3.5},
        },
    ]
)
for update in plan["updates"]:
    print(update["changes"])

if plan["changed"]:
    payload = project.apply_source_draft(source_edits=plan["source_edits"])
    assert payload["written"]
```

读取并替换 collection descriptor 内的一个文本源文件：

```python
project = Project.load("projects/starter-mod")
created = project.create_collection(
    "event",
    "germany",
    metadata={"title": "Germany Events"},
    write=True,
)
assert created["written"]
project.write_collection_file(
    "germany",
    "category.txt",
    "add_namespace = germany\n",
    family="event",
    create=True,
)

source = project.read_collection_file("germany", "category.txt", family="event")

payload = project.write_collection_file(
    "germany",
    "category.txt",
    source["text"],
    family="event",
)
assert payload["written"]
```

在已有项目里新增两个 idea 模块：

```python
from paradev.sdk import Project

project = Project.load("projects/starter-mod")

for object_id, title, description in (
    ("GER_industry_spirit", "German Industry Spirit", "Industrial production spirit."),
    ("GER_army_spirit", "German Army Spirit", "Army modernization spirit."),
):
    plan = project.scaffold_module(
        "hoi4:idea/basic",
        object_id,
        values={"title": title, "description": description},
        write=True,
    )
    if plan["blocked"]:
        raise RuntimeError(plan["diagnostics"])

result = project.build()
assert not result.blocked
```

包默认情况下，模块或 collection `meta.yaml` 中的未知键会产生 warning diagnostic。省略参数的 `Project.build(...)` 和 `Project.diagnostics(...)` 会继承 `CM_PARADEV` 中的 `paradev.build.strict_metadata`；导入器、清理脚本或 CI gate 需要强制阻塞构建时，传入 `strict_metadata=True`：

```python
strict_plan = project.build(strict_metadata=True)
unknown_key_diagnostics = project.diagnostics(
    strict_metadata=True,
    code="metadata.unknown_key",
)
```

新增模块时，SDK 的常用入口是 `Project.create_module(...)`。它默认会写入文件，并返回同一份用于查看 diagnostics 的 plan payload。它可以接收不歧义的 family 简写（如 `idea`），也可以接收完整模板 id（如 `hoi4:idea/basic`）。如果某个 family 只有一个项目本地模板，ParaDev 会优先使用项目本地模板；如果有多个匹配模板，则从 `Project.templates()` 中选择完整模板 id。`Project.scaffold_module(...)` 仍然是底层名称，适合需要先 dry-run scaffold plan 再写入的调用方。

模板参数的默认值可以引用 scaffold 值，例如 `{object_id}`、`{family}`、`{family_tag}`、`{module_id}` 和自动生成的 `{title}`。`family_tag` 会从 object id 中去掉匹配的全大写 family 前缀，因此 `idea` 模板中的 `IDEA_GER_INDUSTRY` 会变成 `GER_INDUSTRY`。`Project.templates()` 中每个模板参数都会带有 `advanced` 标记。GUI 和脚本辅助工具应优先展示非 advanced 字段，把 advanced 字段放进可选区域，因为这些字段已经有默认值。

使用 `Project.templates()` 查看当前可用的创建模板。内置模板覆盖系统 family；如果某类模块需要不同参数或不同起始文件，可以在 `paradev.yaml` 顶层 `templates` 中声明项目本地模板：

在标准 typed module 布局中，`meta.yaml` 是可选的。family 和 object id
分别来自 `modules/{family}/{object_id}`。模板需要显示标题时，只写 `title`
即可；没有作者 metadata 时，可以完全省略这个文件。

```yaml
templates:
  modifier/custom:
    title: Custom Modifier
    family: modifier
    args:
      title:
        required: true
      bonus:
        default: "0.05"
    files:
      meta.yaml: |
        title: {title}
      def.txt: |
        {object_id} = {{
          stability_factor = {bonus}
        }}
      main.loc: |
        [en.{object_id}]
        {title}

        [en.{object_id}_desc]
        Custom modifier.
```

模板行包含 `authoring_ready`。当模板的 `family` 已经由当前 HoI4 profile、项目本地 `families` 声明或项目 Python registry module 注册时，它是 `true`。每一行还包含 `family_id`，即该 Registry family 在浏览器和工作区中的稳定身份；GUI 和 Agent 客户端应直接使用它，不应自行维护单复数 family 对照表。如果 `authoring_ready` 是 `false`，该行会包含 `diagnostic_codes: ["template.unknown_family"]`，`Project.scaffold_module(...)` 也会要求先声明这个 family，再写入文件。Payload 还包含 `id`、`family`、`family_id`、`source`、`authoring_ready` 和 `diagnostic_code` 的 `index` map，脚本和 GUI 客户端可以直接跳到相关行，不需要自己扫描表格。`family` filter 同时接受 Registry 身份和浏览器身份。传入 `template_id=...`、`family=...`、`source=...`、`authoring_ready=True` 或 `diagnostic_code=...` 等过滤参数，可以返回更小的表；返回的 index 总是指向过滤后的表。

同一套模板能力也可以通过 CLI 使用。`templates` 只读，`scaffold` 默认返回 dry plan，只有传入 `--write` 才会写文件。Scaffold plan 会包含和 `Project.authoring_plan(...)` 相同的嵌套 `authoring_plan` payload，因此工具在询问用户是否写入之前，就能展示目标位置的期望 source slot 仍是 `empty`、已经 `satisfied`，还是被 diagnostic 阻塞：

```bash
rtk uv run paradev templates projects/starter-mod --json
rtk uv run paradev templates projects/starter-mod --family idea --authoring-ready --json
rtk uv run paradev scaffold projects/starter-mod hoi4:idea/basic GER_industry_spirit \
  --value "title=German Industry Spirit" \
  --value "description=Industrial production spirit." \
  --write \
  --json
```

对于多源目录项目，`Project.templates()` 和 `paradev templates` 会列出可用源目录，并标记默认目录。如果新模块应写到默认目录之外，在 `Project.scaffold_module(...)` 中传入 `source_root="imports"`，或在 CLI 中使用 `--source-root imports`。嵌套的 authoring plan 也会使用这个选中的源目录。

构建 GUI、导入器或项目本地 family 工作流时，使用 `Project.families()["authoring"]` 读取源目录，以及标准的 `modules/{family}/{object_id}` / `collections/{family}/{collection_id}` 目录模板。每个 family 行包含 `metadata.keys`，列出所有接受的顶层 `meta.yaml` key；`metadata.common_keys` 列出 SDK 通用 key；`metadata.family_keys` 列出 compiler 自己的 key；`metadata.unknown_key_policy` 列出 loose/strict 严重级别。它还会包含 `outputs`，这是一份派生出来的 artifact 计划能力清单，列出 artifact type、template key、template 文本、owner kind、target root，以及必要的 route 或 sprite-slot 上下文。同一个 payload 还包含 `index`，会把 family id、编译器种类、源 slot、collection descriptor slot、sprite slot、route、output artifact type 和 artifact writer 类型映射到返回的行号。`index["output_artifact_type"]` 指向 family 行；`index["artifact_type"]` 指向 writer 行。`Project.templates()` 回答“有哪些现成起始文件可用？”，`Project.families()` 回答“当前 profile 支持哪些 family contract、作者目录位置和输出计划？”。

工具只需要一个 contract 时，可以过滤 `Project.families(...)`：

```python
idea_contract = project.families(
    family="idea",
    source_slot="icon",
    artifact_type="sprite_gfx",
)
sprite_output = idea_contract["families"][0]["outputs"][-1]
assert sprite_output["artifact_type"] == "sprite_gfx"
assert idea_contract["index"]["output_artifact_type"]["sprite_gfx"] == [0]
```

工具只需要一个具体目标目录、但不应创建文件时，使用 `Project.authoring_path(...)`：

```python
path_plan = project.authoring_path("module", "idea", "GER_industry_spirit")
print(path_plan["root"])
```

同一个工具还需要展示该 family 期望哪些源文件、但不应写入文件时，使用 `Project.authoring_plan(...)`：

```python
plan = project.authoring_plan("module", "idea", "GER_industry_spirit")
for slot in plan["source_slots"]:
    print(slot["slot"], slot["status"], slot["match"], slot["relative_paths"])
```

每个 source slot 行都会报告 `status`、`source_count`、`relative_paths`、`paths`，有诊断时还会报告 `diagnostic_codes`。Exact source slot 还会报告 `suggested_relative_paths` 和 `suggested_paths`，即使已经 satisfied 也会保留，方便 GUI、导入器、REST 客户端或 MCP tool 展示缺失必需文件应该放在哪里。可选 slot 没有文件时是 `empty`；必需 slot 没有文件时是 `missing`；匹配成功时是 `satisfied`；匹配到文件但存在 slot 级问题（例如冲突或匹配过多）时是 `diagnostic`。`index["status"]` 可以让工具不运行构建、不复制 slot 匹配逻辑，也能直接找到 missing 和 diagnostic 行。

如果 adapter 已经持有明确的项目根目录和源目录，可以调用 `paradev.build.authoring_path_view(...)`、`authoring_plan_view(...)` 或 `authoring_view(...)`，不用加载 `Project` wrapper 也能得到相同的 JSON-safe authoring payload。

REST 和 MCP 客户端也应该使用相同的 surface 名称，不要复制 CLI 行为。OpenAPI seed 暴露 `/projects/templates`、`/projects/authoring-path`、`/projects/authoring-plan` 和 `/projects/scaffold`；MCP contract 暴露只读的 `project_templates`、`project_authoring_path`、`project_authoring_plan`，以及可写的 `project_scaffold`。它们返回的都是 `Project.templates()`、`Project.authoring_path(...)`、`Project.authoring_plan(...)` 和 `Project.scaffold_module(...)` 拥有的 SDK payload。

检查构建表面：

```python
project = Project.load("demos/assets/projects/minimal")

families = project.families()
modules = project.modules()
artifacts = project.artifacts()
diagnostics = project.diagnostics()
source_slots = project.source_slots()
sources = project.sources()
source_map = project.source_map()
```

脚本或 UI 需要回答“这个模块期望哪些文件、哪些已经存在或缺失？”时，使用 `Project.source_slots(...)`，不需要手动把 family contract 和 source rows 拼起来。每一行包含 owner、family、声明的 slot pattern（一个或多个）、已知 loader kind、匹配路径、diagnostic codes，以及 slot 级状态：`satisfied`、`missing`、`empty` 或 `diagnostic`。

```python
missing_slots = project.source_slots(status="missing")
idea_slots = project.source_slots(family="idea", module_id="idea/GER_industry_spirit")
```

脚本只需要直接读取实际源文件行时，使用 `Project.sources(...)`。collection descriptor 页面只需要 descriptor 自己拥有的源文件时，传入 `owner_kind="collection"`：

```python
collection_sources = project.sources(collection_id="GER_main", owner_kind="collection")
module_sources = project.sources(collection_id="GER_main", owner_kind="module")
```

需要只读 HeavenBase-ready catalog payload 时，使用 `Project.inspect("catalog-preview")`；catalog 已写入或刷新后，用 `Project.inspect("catalog-query", ...)` 查询：

```python
from paradev.hb import catalog_refresh
from paradev.sdk import Project

project = Project.load("demos/assets/projects/minimal")
catalog_refresh(project)
catalog = project.inspect("catalog-preview")
pdx_sources = project.inspect("catalog-query", entity="source-file", tag="loader:pdx")
```

Catalog 写入会启用 HeavenBase 的 `hoi4` extension，并把行持久化为 `hoi4-*` entities；`catalog-query` 仍接受 `source-file`、`pdx-symbol` 这类短 entity selector。catalog 中的 `source-file` 行来自和 `Project.sources(...)` 相同的 `sources.json` payload，并额外带有 `module:focus/GER_sample`、`slot:def`、`loader:pdx`、`status:loaded` 等 Catalog tag。catalog 搜索命中后，读取 `pdx_sources["rows"][0]["data"]` 就能得到原始 source inventory 行。

REST client 可以使用同一条 catalog 边界，不需要了解 HeavenBase 内部：`GET /projects/catalog` 通过 `Project.catalog_status()` 只读报告默认本地数据库状态且不会创建数据库，`POST /projects/catalog` 通过 `paradev.hb.catalog_write(...)` 写入新的 catalog 数据库，`PUT /projects/catalog` 通过 `paradev.hb.catalog_refresh(...)` 刷新数据库，`GET /projects/inspect?kind=catalog-query` 通过 SDK inspection dispatcher 读取行。

adapter 风格的客户端可以按 kind 分发，不需要重复实现命令路由：

```python
modules = project.inspect("modules", family="focus", source_slot="def")
missing_slots = project.inspect("source-slots", status="missing")
sources = project.inspect("sources", module_id="focus/GER_sample", loader="pdx")
collection_sources = project.inspect("sources", collection_id="GER_main", owner_kind="collection")
assets = project.inspect("assets", module_id="focus/GER_sample", file_format="png")
sprites = project.inspect("sprites", module_id="idea/GER_industry_spirit", name="GFX_idea_GER_industry_spirit")
graph = project.inspect("build-graph", module_id="focus/GER_sample")
explain = project.inspect("build-explain", module_id="focus/GER_sample")
catalog = project.inspect("catalog-query", entity="source-file", tag="loader:pdx")
```

`build-graph` 是给可视化追踪面板使用的 inspection。每个 node 保留稳定 id，以及 `type`、`label` 和 source/artifact 字段，同时增加 `group`、`display_label`、`display_detail` 和 `display_path`，方便 UI 分组和紧凑渲染。使用 `graph["index"]["nodes_by_group"]` 可以直接选择 `artifact:output`、`module:focus`、`source:focus` 或 `reference:idea` 这类分组，不需要扫描全部 node。

普通 Python 脚本已经知道要查询什么时，直接使用具体方法即可。GUI、MCP 工具、REST route、导入器或 CLI adapter 从用户操作中收到 inspection kind 和过滤条件时，使用 `Project.inspect(...)`。adapter 需要列出支持的 kind 和过滤字段时，使用 `Project.inspections()`：

```python
contract = project.inspections()
module_filters = contract["index"]["filter"]["module_id"]
```

维护版 inspection kind/filter 表见 [Project Inspection Reference](project-inspection-reference.md)，由 `rtk uv run paradev inspections --markdown` 生成。代码如果只需要其中一个切片，应优先使用 `get_project_inspection_kinds()`、`get_project_inspection_row(kind)`、`get_project_inspection_index_catalog()` 或 `get_project_inspection_filter_kinds(filter_name)`，不要直接读取 raw index。

静态 adapter 注册不需要先加载项目。CLI、MCP、REST/OpenAPI 或 GUI bridge 只需要 SDK 拥有的 inspection kind、CLI 命令名和过滤字段时，使用 `get_project_inspection_contract()`：

```python
from paradev.sdk import get_project_inspection_contract

contract = get_project_inspection_contract()
source_filters = contract["index"]["filter"]["slot"]
```

GUI、导入器、桌面端、MCP bridge、REST client 或 VS Code extension 需要完整、持续维护的操作清单时，使用 `get_frontend_api_contract()`。新增 frontend action 前，先读 `api["summary"]`，用 SDK-owned 的 operation、group、status、read/write 和 workspace-section 计数做审计。调用方已经知道稳定 id 时，使用 `get_frontend_api_operation(...)` 或 `get_frontend_api_group(...)`；需要按 group/status 获取 operation-id list 时，使用 `get_frontend_api_group_operation_ids(...)` 或 `get_frontend_api_status_operation_ids(...)`；需要按 read/write 获取 operation-id list 时，使用 `get_frontend_api_mode_operation_ids(...)`；需要 SDK-owned navigation 时，使用 `get_frontend_api_workspace(...)`；需要一个已选 action 的 workspace row、派生 form、bindings、execution hints 和 option-source 摘要时，使用 `get_frontend_api_action(...)`；需要某个 action 的派生字段 schema 时，使用 `get_frontend_api_form(...)`；字段有 SDK-owned 动态选项来源时，使用 `resolve_frontend_api_options(...)`；需要把提交后的表单状态拆成 project loading、SDK 参数、selector 和 projection 时，使用 `normalize_frontend_api_inputs(...)`；需要同一份提交状态对应的 REST method、path、query 和 JSON body 时，使用 `plan_frontend_api_rest_request(...)`；需要把 surface call key 或整个 adapter surface 反查为稳定 operation id 时，使用 `get_frontend_api_binding_lookup(...)`、`get_frontend_api_binding_operation_ids(...)`、`get_frontend_api_binding_index(...)` 或 `get_frontend_api_rest_operation_ids(...)`；需要不扫描 row 就获取按 surface、payload 或 workspace section 分组的 operation list 时，使用 `get_frontend_api_surface_operation_ids(...)`、`get_frontend_api_payload_operation_ids(...)` 或 `get_frontend_api_workspace_section_operation_ids(...)`；需要重新生成 checked-in desktop TypeScript source artifact 时，使用 `render_frontend_api_typescript()`。桌面 TypeScript 代码应从 `apps/desktop/src/data/frontendApi.ts` 导入 workspace action rows、binding helper、input/default/option-source helper、endpoint/request/payload helper 和 typed helper lookup，不要直接依赖 generated file：

docs、审计或 generated client 需要从每条 raw `contract["index"]` path 映射到 Python 和 TypeScript helper 时，使用 `get_frontend_api_index_catalog()`。

桌面 sidebar 和 tab 使用 `frontendApiWorkspaceSections`；action row 使用 `frontendApiWorkspaceActions`、`getFrontendApiSectionActions(...)`、`getFrontendApiDefaultSectionAction(...)` 和 `getFrontendApiRequiredInputNames(...)`。已选 action panel 使用 `getFrontendApiActionPanelState(...)` 获取 operation summary、execution surfaces、generated fields、defaults、option-source field names、controls、option requests、normalize/rest-plan requests、confirmation state、Run state 和稳定 request key。React 可以按已选 action 保存本地提交值，但渲染字段和执行状态前应先经过 helper。使用 `resolveFrontendApiFormOptionRequest(...)` 执行可用 option request，并渲染 `ready`、`unavailable` 或 `error` 结果状态。把这些结果传回 panel-state helper，让静态 choices 和 SDK option payload row 通过同一种 select-control option model 渲染。执行计划面板应通过 `resolveFrontendApiNormalizeRequest(...)` 和 `resolveFrontendApiRestPlanRequest(...)` 展示同一份提交值的 SDK-owned normalization 与 REST request plan 状态。REST plan ready 且 Run state enabled 后，使用 `buildFrontendApiRestExecutionRequest(...)` 和 `resolveFrontendApiRestExecutionRequest(...)` 通过已配置的 REST bridge 执行目标 request；组件层不要自己维护 URL、body 或 bridge-unavailable 处理。codegen 或 inspector 需要把 surface call key 反查为稳定 operation id 时，使用 `frontendApiBindingIndex`、`getFrontendApiBindingOperationIds(...)` 和 `getFrontendApiRestOperationIds(...)`；API table 需要 group/status operation-id slice 时，使用 `frontendApiGroupIndex`、`frontendApiStatusIndex`、`getFrontendApiGroupOperationIds(...)` 和 `getFrontendApiStatusOperationIds(...)`；API table 需要 read/write operation-id slice 时，使用 `frontendApiModeIndex` 和 `getFrontendApiModeOperationIds(...)`。tab 与 sidebar state 应使用 generated workspace-section id 类型。

修改 TypeScript helper 后，先运行 `rtk npm --prefix apps/desktop run test:unit` 做 summary/group registry alignment、binding-index helper、panel-state、request/resolver 和 bridge-unavailable helper 的直接 coverage，再运行 desktop build 验证 TypeScript/Vite 集成。

```python
from paradev.sdk import (
    FRONTEND_API_ACTION_DETAIL_SCHEMA,
    FRONTEND_API_ACTION_SCHEMA,
    FRONTEND_API_BINDING_LOOKUP_SCHEMA,
    FRONTEND_API_BINDING_SURFACES,
    FRONTEND_API_FORM_SCHEMA,
    FRONTEND_API_INPUTS_SCHEMA,
    FRONTEND_API_OPTIONS_SCHEMA,
    FRONTEND_API_OPTION_SOURCE_SCHEMA,
    FRONTEND_API_REST_REQUEST_SCHEMA,
    FRONTEND_API_SELECTORS,
    FRONTEND_API_SUMMARY_SCHEMA,
    FRONTEND_API_WORKSPACE_SCHEMA,
    build_frontend_api_rest_index_key,
    get_frontend_api_contract,
    get_frontend_api_action,
    get_frontend_api_binding_index,
    get_frontend_api_binding_lookup,
    get_frontend_api_binding_operation_ids,
    get_frontend_api_form,
    get_frontend_api_group,
    get_frontend_api_group_operation_ids,
    get_frontend_api_index_catalog,
    get_frontend_api_mode_operation_ids,
    get_frontend_api_operation,
    get_frontend_api_payload_operation_ids,
    get_frontend_api_rest_operation_ids,
    get_frontend_api_status_operation_ids,
    get_frontend_api_surface_operation_ids,
    get_frontend_api_workspace,
    get_frontend_api_workspace_section_operation_ids,
    normalize_frontend_api_inputs,
    plan_frontend_api_rest_request,
    render_frontend_api_typescript,
    resolve_frontend_api_options,
)

api = get_frontend_api_contract()
workspace = get_frontend_api_workspace()
assert api["summary"]["schema"] == FRONTEND_API_SUMMARY_SCHEMA
assert api["summary"]["operation_count"] == len(api["operations"])
assert api["summary"]["workspace_section_count"] == len(workspace["sections"])
module_operations = get_frontend_api_group_operation_ids("modules")
planned_operations = get_frontend_api_status_operation_ids("planned")
write_operations = get_frontend_api_mode_operation_ids("write")
index_catalog = get_frontend_api_index_catalog()
project_cli_operations = get_frontend_api_binding_operation_ids("cli", "project")
cli_binding_index = get_frontend_api_binding_index("cli")
project_list_operations = get_frontend_api_binding_operation_ids("cli", "projects")
project_browser_operations = get_frontend_api_binding_operation_ids("cli", "project-browser")
template_operations = get_frontend_api_binding_operation_ids("cli", "templates")
module_rest_operations = get_frontend_api_rest_operation_ids("GET", "/projects/inspect", {"kind": "modules"})
project_browser_rest_operations = get_frontend_api_rest_operation_ids("GET", "/projects/browser")
rest_surface_operations = get_frontend_api_surface_operation_ids("rest")
project_view_payload_operations = get_frontend_api_payload_operation_ids("Project.to_view")
catalog_section_operations = get_frontend_api_workspace_section_operation_ids("catalog")
module_list = get_frontend_api_operation("module.list")
module_group = get_frontend_api_group("modules")
module_create_detail = get_frontend_api_action("module.create")
assert workspace["schema"] == FRONTEND_API_WORKSPACE_SCHEMA
assert workspace["sections"][0]["id"] == "project-switcher"
assert "module.edit" in workspace["index"]["section"]["source-editor"]
source_editor = next(section for section in workspace["sections"] if section["id"] == "source-editor")
module_edit_action = next(action for action in source_editor["actions"] if action["operation_id"] == "module.edit")
assert module_edit_action["schema"] == FRONTEND_API_ACTION_SCHEMA
assert module_edit_action["execution"]["default_surface"] == "rest"
assert module_edit_action["execution"]["rest_request_schema"] == FRONTEND_API_REST_REQUEST_SCHEMA
assert module_create_detail["schema"] == FRONTEND_API_ACTION_DETAIL_SCHEMA
assert module_create_detail["sections"] == ["authoring"]
assert module_create_detail["option_fields"] == ["template_id", "source_root"]
assert get_frontend_api_operation("surface.frontend_api")["selectors"] == list(FRONTEND_API_SELECTORS)
assert FRONTEND_API_BINDING_SURFACES == ("cli", "lsp", "mcp", "rest", "sdk")
assert build_frontend_api_rest_index_key("GET", "/projects/inspect", {"kind": "modules"}) == "GET /projects/inspect?kind=modules"
assert get_frontend_api_binding_lookup("rest", "GET /projects/inspect?kind=modules") == {
    "schema": FRONTEND_API_BINDING_LOOKUP_SCHEMA,
    "surface": "rest",
    "key": "GET /projects/inspect?kind=modules",
    "operation_ids": ["module.list"],
    "count": 1,
}
assert module_list["bindings"]["rest"] == {"method": "GET", "path": "/projects/inspect", "query": {"kind": "modules"}}
assert project_cli_operations == ["project.open", "project.view"]
assert project_list_operations == ["project.list"]
assert project_browser_operations == ["project.browser"]
assert template_operations == ["module.templates"]
assert module_rest_operations == ["module.list"]
assert project_browser_rest_operations == ["project.browser"]
project_state_form = get_frontend_api_form("project.state")
assert project_state_form["defaults"] == {"project_paths": [], "search_roots": []}
project_browser_form = get_frontend_api_form("project.browser")
assert project_browser_form["fields"][2]["label"] == "Kind"
assert project_browser_form["fields"][2]["choices"] == ["module", "collection"]
module_edit_form = get_frontend_api_form("module.edit")
assert module_edit_form["schema"] == FRONTEND_API_FORM_SCHEMA
assert module_edit_form["required"] == ["module_id", "relative_path", "text"]
assert module_edit_form["fields"][3]["label"] == "Text"
assert "source file" in module_edit_form["fields"][3]["description"]
module_create_form = get_frontend_api_form("module.create")
module_create_fields = {field["name"]: field for field in module_create_form["fields"]}
template_source = module_create_fields["template_id"]["option_source"]
assert template_source["schema"] == FRONTEND_API_OPTION_SOURCE_SCHEMA
assert template_source["operation_id"] == "module.templates"
assert template_source["values_path"] == ["templates"]
assert module_create_fields["source_root"]["option_source"]["values_path"] == ["source_roots"]
template_options = resolve_frontend_api_options("module.create", "template_id", {"path": "demos/assets/projects/minimal"})
assert template_options["schema"] == FRONTEND_API_OPTIONS_SCHEMA
assert template_options["provider_operation_id"] == "module.templates"
assert template_options["options"][0]["value"] == "hoi4:idea/basic"
source_file_options = resolve_frontend_api_options("module.file", "relative_path", {"path": "demos/assets/projects/minimal"})
assert source_file_options["available"] is False
assert source_file_options["missing_requirements"] == ["module_id"]
build_artifacts_form = get_frontend_api_form("build.artifacts")
assert build_artifacts_form["json_schema"]["properties"]["target_root"]["enum"] == ["output", "build"]
lsp_hover_form = get_frontend_api_form("lsp.hover")
assert lsp_hover_form["fields"][1]["description"].startswith("Zero-based")
assert lsp_hover_form["json_schema"]["properties"]["line"]["minimum"] == 0
module_edit_values = normalize_frontend_api_inputs(
    "module.edit",
    {"module_id": "modifier/example", "relative_path": "def.txt", "text": "modifier = { value = 1 }"},
)
assert module_edit_values["schema"] == FRONTEND_API_INPUTS_SCHEMA
assert module_edit_values["project"] == {"path": "."}
assert module_edit_values["parameters"]["relative_path"] == "def.txt"
module_edit_request = plan_frontend_api_rest_request(
    "module.edit",
    {"module_id": "modifier/example", "relative_path": "def.txt", "text": "modifier = { value = 1 }"},
)
typescript_contract = render_frontend_api_typescript()
assert module_edit_request["schema"] == FRONTEND_API_REST_REQUEST_SCHEMA
assert module_edit_request["method"] == "PATCH"
assert module_edit_request["path"] == "/projects/modules/file"
assert module_edit_request["body"]["text"].startswith("modifier")
assert "ParaDevFrontendApiOperationId" in typescript_contract
assert '"module.create",' in typescript_contract
project_create_inputs = get_frontend_api_operation("project.create")["inputs"]
module_edit_inputs = get_frontend_api_operation("module.edit")["inputs"]
collection_create_inputs = get_frontend_api_operation("collection.create")["inputs"]
collection_rename_inputs = get_frontend_api_operation("collection.rename")["inputs"]
collection_remove_inputs = get_frontend_api_operation("collection.remove")["inputs"]
pdx_format_inputs = get_frontend_api_operation("pdx.format")["inputs"]
lsp_hover_inputs = get_frontend_api_operation("lsp.hover")["inputs"]
build_artifacts_inputs = get_frontend_api_operation("build.artifacts")["inputs"]
project_state_inputs = get_frontend_api_operation("project.state")["inputs"]
project_browser_inputs = get_frontend_api_operation("project.browser")["inputs"]
catalog_query_inputs = get_frontend_api_operation("catalog.query")["inputs"]
frontend_selector_inputs = get_frontend_api_operation("surface.frontend_api")["inputs"]
```

operation 行会在对应 surface 存在时提供机器可读的 `bindings`，覆盖 SDK、CLI、REST、MCP 和 LSP。workspace projection 会为 GUI shell 提供 SDK-owned 的 navigation sections 和 `paradev.sdk.frontend-api.action.v1` action rows；每个 action row 都会发布派生 execution hints，例如 `execution.default_surface`、`execution.available_surfaces`、`execution.confirmation`、可调用 `bindings`、`form_schema`、`normalizer_schema` 和 `rest_request_schema`。`get_frontend_api_action(...)`、CLI `frontend-api --operation ... --action` 和 REST `GET /frontend-api/action?operation_id=...` 会为一个已选 action 返回相同的 `paradev.sdk.frontend-api.action-detail.v1` payload，让前端不需要手工拼接 workspace、form、bindings 和 option-source 细节。`execution.confirmation` 使用 `paradev.sdk.frontend-api.confirmation.v1`；非本地的 mutating action 会设置 `required=true`，携带 `project-files` 或 `catalog` 这样的 `scope`、`write` 或 `destructive` 这样的 `style`，并列出用户确认前应保持 false 的 `confirm_fields`。`render_frontend_api_typescript()` 和 CLI `frontend-api --typescript` 会生成 `apps/desktop/src/generated/frontendApi.ts`，为 TypeScript client 导出 operation id union 和完整 SDK-owned contract；`apps/desktop/src/data/frontendApi.ts` 中的桌面 helper 会包装该 generated file，并提供 summary、`frontendApiWorkspaceActions`、`getFrontendApiAction(...)`、`getFrontendApiActionDetail(...)`、`getFrontendApiFormControls(...)`、`getFrontendApiFormControlKind(...)`、`getFrontendApiFormValuesWithDefaults(...)`、`getFrontendApiFormOptionRequests(...)`、`resolveFrontendApiFormOptionRequest(...)`、`resolveFrontendApiNormalizeRequest(...)`、`resolveFrontendApiRestPlanRequest(...)`、`buildFrontendApiRestExecutionRequest(...)`、`resolveFrontendApiRestExecutionRequest(...)`、`getFrontendApiSectionActions(...)`、`getFrontendApiDefaultSectionAction(...)`、`getFrontendApiBindings(...)`、`getFrontendApiRestBinding(...)`、`frontendApiInputOperations`、`getFrontendApiInputs(...)`、`getFrontendApiRequiredInputNames(...)`、`getFrontendApiDefaultValues(...)`、`getFrontendApiOptionSourceInputs(...)`、`frontendApiEndpointPaths`、`buildFrontendApi*Url(...)`，以及 `buildFrontendApiOptionsRequest(...)`、`buildFrontendApiNormalizeRequest(...)` 和 `buildFrontendApiRestPlanRequest(...)` 这样的 JSON request helpers。form 行也会携带 SDK-owned 的 `label` 和 `description` 文案、`choices`、select 控件、动态 `option_source` provider 提示和数值边界，例如 LSP hover 的 `minimum=0`；`normalize_frontend_api_inputs(...)` 会在 adapter 调用 SDK 或 REST 前检查这些约束。前端 shell 可以按已选 action 保存本地提交值，但 `getFrontendApiFormValuesWithDefaults(...)` 负责合并默认值，`getFrontendApiFormOptionRequests(...)` 负责判断 option-source 是否可用并返回可直接交给 `buildFrontendApiOptionsRequest(...)` 的 fetch 输入，`resolveFrontendApiFormOptionRequest(...)` 负责执行单个 request 并塑形为 ready/unavailable/error result，normalize/rest-plan/Run resolver helpers 负责 execution-plan 和 Run 面板的 ready/error/loading 状态。使用 `resolve_frontend_api_options(...)` 根据 `option_source` 填充项目派生选项：例如 template 来自 `module.templates`，family 来自 `build.families`，module id 来自 `module.list`，collection id 来自 `collection.list`，artifact 来自 `build.artifacts`，diagnostic 来自 `build.diagnostics`；上游字段未填写时，resolver 会返回 `available=false` 和 `missing_requirements`。生成客户端和 adapter 应使用这些对象，然后请求同一组 SDK adapter，而不是重新实现：`paradev frontend-api --workspace` 返回的 payload 与 `get_frontend_api_workspace(...)` 相同，schema 是 `paradev.sdk.frontend-api.workspace.v1`；`paradev frontend-api --operation ... --option-field ... --values-json ...` 和 `POST /frontend-api/options?operation_id=...&field_name=...` 返回的都是与 `resolve_frontend_api_options(...)` 相同的 `paradev.sdk.frontend-api.options.v1` payload；`paradev frontend-api --operation ... --values-json ...` 和 `POST /frontend-api/normalize?operation_id=...` 返回的都是与 `normalize_frontend_api_inputs(...)` 相同的 `paradev.sdk.frontend-api.inputs.v1` payload；`paradev frontend-api --operation ... --values-json ... --rest-request` 和 `POST /frontend-api/rest-request?operation_id=...` 返回的都是与 `plan_frontend_api_rest_request(...)` 相同的 `paradev.sdk.frontend-api.rest-request.v1` payload；`paradev frontend-api --binding-surface ... --binding-key ...` 和 `GET /frontend-api/binding?binding_surface=...&binding_key=...` 返回的 payload 与 `get_frontend_api_binding_lookup(...)` 相同，schema 是 `paradev.sdk.frontend-api.binding-lookup.v1`。反向的 `api["index"]["binding"]` map 可以查询每个 surface call key 对应哪些 frontend operation id，但 Python client 应优先使用 `get_frontend_api_binding_operation_ids(...)` 或 `get_frontend_api_rest_operation_ids(...)`；静态 CLI/MCP contract 也会以 `frontend_operation_ids` 暴露自己的切片。OpenAPI operation 也会带有从 `bindings.rest` 派生的 `x-paradev-frontend-api-operation-ids`，方便从 REST 文档开始生成客户端；Python architecture suite 会验证每个声明的 binding 都进入索引，并验证每个 REST binding 都有对应 OpenAPI annotation。

桌面端确认接受状态是 frontend-local state，但策略来自 SDK。TypeScript client 应用 `FrontendApiActionConfirmationStates` 保存已接受的 operation，启用 Run 前调用 `isFrontendApiActionConfirmationSatisfied(...)`，并在提交的表单值变化时重置接受状态。

`get_lsp_contract()["frontend_operation_ids"]` 会镜像同一个 frontend API binding index 的 LSP 切片，因此 LSP adapter 可以把 `textDocument/*` method 映射回 canonical operation id，而不需要扫描 raw operation row。

桌面端 Run state 是在 SDK-owned 策略和 REST state 之上的 frontend-local rendering。TypeScript client 应调用 `getFrontendApiActionRunState(...)`，并渲染其中的 `disabled`、`detail`、`status` 和 `confirmation_satisfied` 字段，不要重新实现 confirmation 或 REST result 解释。

桌面端 selected-action panel 需要常见 action detail/form/options/execution bundle 时，应调用 `getFrontendApiActionPanelState(...)`。这样 effect key 和 request payload 会与 helper 保持一致，而不是散落在多个组件里。

`Project.remove_module(...)` 是 plan-first 的破坏性操作：

```python
plan = project.remove_module("modifier/starter_starter_modifier")
for source in plan["files"]:
    print(source["module_relative_path"])

removed = project.remove_module("modifier/starter_starter_modifier", write=True)
assert removed["removed"]
```

真正写入的 remove 会先把 canonical 目录原子移动到同一 source root 下的 `.paradev/module-trash`，让已有 Catalog 以 stale 状态 fail closed，最后 best-effort 删除 quarantine copy。如果清理未完成，`removed` 仍为 `True`；payload 会增加 warning diagnostic，以及 schema 为 `paradev.module.remove-cleanup.v1`、status 为 `pending`、包含项目内 tombstone 路径的 `cleanup`。不要重试 module remove。

模块 create、rename、remove 和 contained source draft 在修改源文件前会先让已有 Catalog 失效。一次模块修改也可能改变 HOI4 entity、localization、PDX symbol、source、graph 和 artifact projection，因此 ParaDev 不会再把只更新 `hoi4-module` 行描述为完整同步。写入成功的 `Project.create_module(...)` 或 `Project.scaffold_module(...)` 会在 plan 内返回 `plan["catalog_mutation"]`；`Project.rename_module(...)` 和完成删除的 `Project.remove_module(..., write=True)` 会在顶层返回同一字段。其 schema 仍是 `paradev.hb.catalog-mutation.v1`：

- `not_configured` / `catalog.mutation.not_configured` 表示源文件修改成功，但项目还没有准备 Catalog。
- `failed` / `catalog.mutation.failed` 会返回可操作的 Refresh 提示，表示源文件修改成功，而之前的 Catalog 已被有意标记为 stale。`Project.catalog_status()` 会返回 `incomplete`；在 `catalog_refresh(...)` 重建全部关联 projection 前，Catalog query 和 completion 都会 fail closed。
- `applied` / `catalog.mutation.applied` 仅为未来完整的 multi-entity delta 保留，当前模块 authoring 不会返回它。

需要刷新时不要重试源文件操作，应使用 App 的 Catalog Refresh action。Dry run、blocked plan 和未实际写入的 remove 不会包含 `catalog_mutation`。因此主结果始终明确：`written` 或 `removed` 描述文件系统操作，而 `catalog_mutation` 描述由它派生的搜索/索引 projection。

模块 scaffold 写入、目录 rename/remove 需要 descriptor-anchored、no-follow 的目录操作。Scaffold destination 保持 lexical。写入会先把完整渲染结果暂存到 `source_root/.paradev/module-transactions`，再安装任何正式文件；force 替换的原始备份会保留到最终 identity check 通过，普通的暂存或安装失败会回滚。如果恢复原文件本身也失败，blocked plan 会返回带 `recovery_path` 的 `scaffold.rollback_incomplete`，并保留 transaction，不会删除最后一份可恢复副本。路径组件并发替换会阻止写入并回滚新建的 partial module。无法提供所需能力的平台会 fail closed；ParaDev 有意不使用 path-based fallback，因为并发替换的 symlink 可能被错误跟随。

需要替换完整项目源子树的外部 importer，应使用公共项目锁与 build 和 GUI/SDK 编辑协调：

```python
from paradev.sdk import project_source_mutation_lock

with project_source_mutation_lock(project.root):
    sources = snapshot_and_validate_sources()
    publish_transaction(sources)
```

锁必须从第一次读取源文件一直持有到最后一次 publication rename，并且传入与 `Project.load(...)` 相同的 lexical 项目根目录。这个锁只负责协调 writer；importer 仍须拒绝 symlink、验证 staged tree，并为中断的 swap 保留可恢复备份。

使用 `Project.rename_collection(...)` 移动 collection descriptor，并且不改写作者文件内容：

```python
renamed = project.rename_collection("germany", "france", family="event")
assert renamed["collection_id"] == "france"
assert renamed["content_rewritten"] is False
```

`Project.remove_collection(...)` 会先保留 member 模块并解除其分组，再删除 collection descriptor：

```python
plan = project.remove_collection("germany", family="event")
for source in plan["files"]:
    print(source["collection_relative_path"])

removed = project.remove_collection(
    "germany",
    family="event",
    write=True,
    plan_hash=plan["plan_hash"],
)
assert removed["removed"]
```

计划会列出 `members` 和 `member_files`。应用计划时，ParaDev 会清除可见/隐藏 metadata 中显式的 collection pointer，保留无关设置，并在一个可崩溃恢复的事务中删除 descriptor；它绝不会删除 member 模块。

如果 adapter 已经持有 `BuildRegistry` 和项目上下文，可以调用 `paradev.build.families_view(...)`，拿到与 `Project.families(...)` 相同的 family contract payload。如果 compiler 测试或 adapter 已经有 `BuildResult`，也可以直接调用 build 层 helper，例如 `paradev.build.summary_view(result)`、`manifests_view(result)`、`modules_view(result, family="focus")`、`sources_view(result, loader="pdx")`、`assets_view(result, file_format="png")`、`sprites_view(result, family="idea")` 或 `diagnostics_view(result, severity="error")`。这些 helper 返回的 payload 形状和重建后的 index 与 SDK 方法保持一致。

不运行项目构建，也可以直接解析或格式化 PDX：

```python
from paradev.sdk import (
    diagnose_pdx_lsp_text,
    document_symbols_pdx_lsp_text,
    format_pdx_file,
    format_pdx_lsp_text,
    format_pdx_text,
    hover_pdx_lsp_text,
    parse_pdx_file,
)

payload = parse_pdx_file(
    "demos/assets/projects/minimal/src/modules/focus/GER_sample/def.txt",
    include_tokens=True,
)
assert payload["ok"]

formatted = format_pdx_text("focus={id=GER_sample cost=10}", path="focus.pdx")
assert formatted["formatted_text"].startswith("focus = {")

preview = format_pdx_file("demos/assets/projects/minimal/src/modules/focus/GER_sample/def.txt")
assert preview["schema"] == "paradev.pdx.format.v1"

lsp_format = format_pdx_lsp_text("focus={id=GER_sample cost=10}", uri="file:///workspace/focus.pdx")
assert lsp_format["schema"] == "paradev.lsp.formatting.v1"

lsp_diagnostics = diagnose_pdx_lsp_text("value = 0x", uri="file:///workspace/broken.pdx")
assert lsp_diagnostics["schema"] == "paradev.lsp.diagnostics.v1"

lsp_symbols = document_symbols_pdx_lsp_text("focus={id=GER_sample}", uri="file:///workspace/focus.pdx")
assert lsp_symbols["schema"] == "paradev.lsp.symbols.v1"

lsp_hover = hover_pdx_lsp_text("focus={id=GER_sample}", 0, 8, uri="file:///workspace/focus.pdx")
assert lsp_hover["schema"] == "paradev.lsp.hover.v1"
```

运行 dry build 并直接查看 records：

```python
result = Project.load("demos/assets/projects/minimal").build()

for artifact in result.artifacts:
    print(artifact.path, artifact.artifact_type, artifact.owner)
```

在 HoI4 构建中，`mod_descriptor` artifact 属于项目级输出。使用 `emit_artifacts=True` 时，`descriptor.mod` 会写入输出目录，`launcher/<project_id>.mod` 会写入构建目录。

写出文件：

```python
result = Project.load("demos/assets/projects/minimal").build(
    emit_artifacts=True,
    emit_manifests=True,
)
```

重要规则：GUI、MCP、REST、LSP 和脚本集成都应该调用 SDK，不要重新实现 HoI4 业务逻辑。
