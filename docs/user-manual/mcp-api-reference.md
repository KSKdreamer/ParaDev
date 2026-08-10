# MCP API Reference

Generated from `paradev.surfaces.mcp.get_mcp_api_table()`.

Regenerate this file whenever the MCP tool contract changes:

```bash
rtk uv run paradev mcp-api --markdown > docs/user-manual/mcp-api-reference.md
```

## Summary / 汇总

- API rows / API 行数: 51
- Read tools / 读取工具数: 31
- Write tools / 写入工具数: 20
- Features / Feature 数: 14
- Frontend-bound operations / 前端绑定操作数: 60
- Runtime server / Runtime server: `paradev mcp serve` (`stdio`)
- Runtime status / Runtime status: `implemented` (`authoring` scope)
- Selector helper / Selector helper: Use `get_mcp_api_selection(symbol=..., index_name=..., key=...)` returns the table, one MCP tool row, or one tool-symbol index projection.

## Mode Index / 模式索引

| Mode | Tools | Symbols |
| --- | --- | --- |
| `read` | 31 | `project_inspections`, `project_inspect`, `project_templates`, `project_authoring_path`, `project_authoring_plan`, `project_open`, `project_view`, `project_browser`, `project_find`, `module_diagram`, `module_file`, `module_asset`, `module_source_form`, `module_source_form_update`, `module_source_form_update_batch`, `localization_workspace`, `localization_plan`, `collection_file`, `frontend_api`, `api_catalog`, `surface_contracts`, `pdx_parse`, `pdx_api`, `lsp_api`, `catalog_api`, `mcp_api`, `cli_api`, `inspect_project`, `list_surfaces`, `describe_architecture`, `architecture_api` |
| `write` | 20 | `project_scaffold`, `project_create_modules`, `project_draft_apply`, `collection_scaffold`, `project_create`, `project_rename`, `project_preferred_language`, `module_rename`, `module_duplicate`, `module_collection_set`, `module_activity_set`, `module_metadata_clean`, `module_diagram_edit`, `module_remove`, `module_edit`, `collection_edit`, `collection_create`, `collection_rename`, `collection_remove`, `pdx_format` |

## Feature Index / Feature 索引

| Feature | Tools | Symbols |
| --- | --- | --- |
| `inspections` | 2 | `project_inspections`, `project_inspect` |
| `authoring` | 9 | `project_templates`, `project_authoring_path`, `project_authoring_plan`, `project_scaffold`, `project_create_modules`, `project_draft_apply`, `collection_scaffold`, `localization_workspace`, `localization_plan` |
| `projects` | 8 | `project_create`, `project_open`, `project_view`, `project_browser`, `project_find`, `project_rename`, `project_preferred_language`, `inspect_project` |
| `modules` | 14 | `module_rename`, `module_duplicate`, `module_collection_set`, `module_activity_set`, `module_metadata_clean`, `module_diagram`, `module_diagram_edit`, `module_remove`, `module_file`, `module_asset`, `module_source_form`, `module_source_form_update`, `module_source_form_update_batch`, `module_edit` |
| `collections` | 5 | `collection_file`, `collection_edit`, `collection_create`, `collection_rename`, `collection_remove` |
| `frontend-api` | 1 | `frontend_api` |
| `api-catalog` | 1 | `api_catalog` |
| `surface-contracts` | 1 | `surface_contracts` |
| `pdx` | 3 | `pdx_parse`, `pdx_format`, `pdx_api` |
| `lsp` | 1 | `lsp_api` |
| `catalog` | 1 | `catalog_api` |
| `mcp` | 1 | `mcp_api` |
| `cli` | 1 | `cli_api` |
| `architecture` | 3 | `list_surfaces`, `describe_architecture`, `architecture_api` |

## Frontend Operation Index / 前端操作索引

| Operation | Tools | Symbols |
| --- | --- | --- |
| `project.inspect` | 1 | `project_inspect` |
| `module.list` | 1 | `project_inspect` |
| `module.view` | 1 | `project_inspect` |
| `module.source_slots` | 1 | `project_inspect` |
| `module.sources` | 1 | `project_inspect` |
| `collection.list` | 1 | `project_inspect` |
| `collection.view` | 1 | `project_inspect` |
| `collection.source_slots` | 1 | `project_inspect` |
| `collection.sources` | 1 | `project_inspect` |
| `build.summary` | 1 | `project_inspect` |
| `build.manifests` | 1 | `project_inspect` |
| `build.artifacts` | 1 | `project_inspect` |
| `build.localization` | 1 | `project_inspect` |
| `build.assets` | 1 | `project_inspect` |
| `build.sprites` | 1 | `project_inspect` |
| `build.diagnostics` | 1 | `project_inspect` |
| `build.source_map` | 1 | `project_inspect` |
| `build.dependencies` | 1 | `project_inspect` |
| `build.graph` | 1 | `project_inspect` |
| `build.explain` | 1 | `project_inspect` |
| `build.families` | 1 | `project_inspect` |
| `catalog.preview` | 1 | `project_inspect` |
| `catalog.query` | 1 | `project_inspect` |
| `module.templates` | 1 | `project_templates` |
| `module.authoring_path` | 1 | `project_authoring_path` |
| `collection.authoring_path` | 1 | `project_authoring_path` |
| `module.authoring_plan` | 1 | `project_authoring_plan` |
| `collection.authoring_plan` | 1 | `project_authoring_plan` |
| `module.create` | 1 | `project_scaffold` |
| `module.create_batch` | 1 | `project_create_modules` |
| `project.draft_apply` | 1 | `project_draft_apply` |
| `collection.scaffold` | 1 | `collection_scaffold` |
| `project.create` | 1 | `project_create` |
| `project.open` | 1 | `project_open` |
| `project.view` | 1 | `project_view` |
| `project.browser` | 1 | `project_browser` |
| `project.find` | 1 | `project_find` |
| `project.rename` | 1 | `project_rename` |
| `project.language` | 1 | `project_preferred_language` |
| `module.rename` | 1 | `module_rename` |
| `module.duplicate` | 1 | `module_duplicate` |
| `module.collection.set` | 1 | `module_collection_set` |
| `module.activity.set` | 1 | `module_activity_set` |
| `module.metadata.clean` | 1 | `module_metadata_clean` |
| `module.diagram` | 1 | `module_diagram` |
| `module.diagram.edit` | 1 | `module_diagram_edit` |
| `module.remove` | 1 | `module_remove` |
| `module.file` | 1 | `module_file` |
| `localization.workspace` | 1 | `localization_workspace` |
| `localization.plan` | 1 | `localization_plan` |
| `module.edit` | 1 | `module_edit` |
| `collection.file` | 1 | `collection_file` |
| `collection.edit` | 1 | `collection_edit` |
| `collection.create` | 1 | `collection_create` |
| `collection.rename` | 1 | `collection_rename` |
| `collection.remove` | 1 | `collection_remove` |
| `surface.frontend_api` | 1 | `frontend_api` |
| `pdx.parse` | 1 | `pdx_parse` |
| `pdx.format` | 1 | `pdx_format` |
| `surface.architecture` | 1 | `list_surfaces` |

## API Standard Table / API 标准表

| Symbol | Kind | Layer | Feature | Mode | SDK Method | Inputs | Returns | Raises | Frontend Operation IDs | Registry Seam | Doc Page | Test Anchor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `project_inspections` | `MCP tool` | `mcp` | `inspections` | `read` | `Project.inspect('inspections')` | `path` | `Project inspection contract` |  |  | `MCP tool registry: project_inspections` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `project_inspect` | `MCP tool` | `mcp` | `inspections` | `read` | `Project.inspect` | `path, kind, filters` | `Project inspection payload` |  | `project.inspect`, `module.list`, `module.view`, `module.source_slots`, `module.sources`, `collection.list`, `collection.view`, `collection.source_slots`, `collection.sources`, `build.summary`, `build.manifests`, `build.artifacts`, `build.localization`, `build.assets`, `build.sprites`, `build.diagnostics`, `build.source_map`, `build.dependencies`, `build.graph`, `build.explain`, `build.families`, `catalog.preview`, `catalog.query` | `MCP tool registry: project_inspect` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `project_templates` | `MCP tool` | `mcp` | `authoring` | `read` | `Project.templates` | `path, template_id, family, kind, source, authoring_ready, diagnostic_code` | `Project authoring template payload` |  | `module.templates` | `MCP tool registry: project_templates` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `project_authoring_path` | `MCP tool` | `mcp` | `authoring` | `read` | `Project.authoring_path` | `path, kind, family, target_id, source_root` | `Project authoring path payload` |  | `module.authoring_path`, `collection.authoring_path` | `MCP tool registry: project_authoring_path` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `project_authoring_plan` | `MCP tool` | `mcp` | `authoring` | `read` | `Project.authoring_plan` | `path, kind, family, target_id, source_root, profile` | `Project authoring plan payload` |  | `module.authoring_plan`, `collection.authoring_plan` | `MCP tool registry: project_authoring_plan` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `project_scaffold` | `MCP tool` | `mcp` | `authoring` | `write` | `Project.scaffold_module` | `path, template_id, object_id, source_root, values, write, force` | `SDK scaffold draft plan` |  | `module.create` | `MCP tool registry: project_scaffold` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `project_create_modules` | `MCP tool` | `mcp` | `authoring` | `write` | `Project.create_modules` | `path, modules, source_root, write, plan_hash` | `SDK atomic module batch plan or apply payload` | `ProjectManifestError, OSError, or ValueError on invalid module batch` | `module.create_batch` | `MCP tool registry: project_create_modules` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `project_draft_apply` | `MCP tool` | `mcp` | `authoring` | `write` | `Project.apply_source_draft` | `path, source_edits, source_removals, source_replacements, module_rename` | `SDK source-draft apply payload` | `ProjectManifestError, OSError, or ValueError on invalid source draft` | `project.draft_apply` | `MCP tool registry: project_draft_apply` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `collection_scaffold` | `MCP tool` | `mcp` | `authoring` | `write` | `Project.scaffold_collection` | `path, template_id, collection_id, values, source_root, write, force, plan_hash` | `SDK guarded collection scaffold plan or apply payload` | `ProjectManifestError, OSError, or ValueError on invalid collection scaffold` | `collection.scaffold` | `MCP tool registry: collection_scaffold` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `project_create` | `MCP tool` | `mcp` | `projects` | `write` | `Project.create` | `path, project_id, title, game, force` | `Project create payload` | `ProjectCreateError on invalid or existing project` | `project.create` | `MCP tool registry: project_create` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `project_open` | `MCP tool` | `mcp` | `projects` | `read` | `Project.load` | `path, game, title` | `Project manifest payload` | `ProjectManifestError on invalid project` | `project.open` | `MCP tool registry: project_open` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `project_view` | `MCP tool` | `mcp` | `projects` | `read` | `Project.to_view` | `path, game, title` | `Project view payload` |  | `project.view` | `MCP tool registry: project_view` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `project_browser` | `MCP tool` | `mcp` | `projects` | `read` | `Project.browser` | `path, profile, kind, family, module_id, collection_id` | `Project browser payload` |  | `project.browser` | `MCP tool registry: project_browser` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `project_find` | `MCP tool` | `mcp` | `projects` | `read` | `Project.find` | `path` | `Project find payload` |  | `project.find` | `MCP tool registry: project_find` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `project_rename` | `MCP tool` | `mcp` | `projects` | `write` | `Project.rename` | `title, path` | `Project rename payload` | `ProjectManifestError or ValueError on invalid project rename` | `project.rename` | `MCP tool registry: project_rename` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `project_preferred_language` | `MCP tool` | `mcp` | `projects` | `write` | `Project.set_preferred_language` | `path, preferred_language, write, plan_hash` | `Guarded project authoring-language plan or apply payload` | `ProjectManifestError or ValueError on invalid project language` | `project.language` | `MCP tool registry: project_preferred_language` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `module_rename` | `MCP tool` | `mcp` | `modules` | `write` | `Project.rename_module` | `path, module_id, object_id, title, source_root` | `Module rename payload` | `ProjectManifestError or ValueError on invalid module rename` | `module.rename` | `MCP tool registry: module_rename` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `module_duplicate` | `MCP tool` | `mcp` | `modules` | `write` | `Project.duplicate_module` | `path, module_id, object_id, source_root, destination_source_root, write, plan_hash` | `SDK guarded module duplicate plan or apply payload` | `ProjectManifestError, OSError, or ValueError on invalid module duplicate` | `module.duplicate` | `MCP tool registry: module_duplicate` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `module_collection_set` | `MCP tool` | `mcp` | `modules` | `write` | `Project.set_module_collection` | `path, module_id, collection_id, source_root, write, plan_hash` | `SDK guarded module collection plan or apply payload` | `ProjectManifestError, OSError, or ValueError on invalid module collection` | `module.collection.set` | `MCP tool registry: module_collection_set` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `module_activity_set` | `MCP tool` | `mcp` | `modules` | `write` | `Project.set_module_active` | `path, module_id, active, source_root, write, plan_hash` | `SDK guarded module activity plan or apply payload` | `ProjectManifestError, OSError, or ValueError on invalid module activity` | `module.activity.set` | `MCP tool registry: module_activity_set` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `module_metadata_clean` | `MCP tool` | `mcp` | `modules` | `write` | `Project.clean_module_metadata` | `path, family, module_id, source_root, write, plan_hash` | `SDK guarded module metadata cleanup plan or apply payload` | `ProjectManifestError, OSError, or ValueError on invalid metadata cleanup` | `module.metadata.clean` | `MCP tool registry: module_metadata_clean` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `module_diagram` | `MCP tool` | `mcp` | `modules` | `read` | `Project.module_diagram` | `path, family, profile` | `SDK source-backed module diagram payload` | `ProjectManifestError, OSError, or ValueError on invalid module diagram` | `module.diagram` | `MCP tool registry: module_diagram` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `module_diagram_edit` | `MCP tool` | `mcp` | `modules` | `write` | `Project.edit_module_diagram` | `path, family, profile, position_intents, edge_intents, node_intents, write, plan_hash` | `SDK guarded module diagram edit plan or apply payload` | `ProjectManifestError, OSError, or ValueError on invalid module diagram edit` | `module.diagram.edit` | `MCP tool registry: module_diagram_edit` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `module_remove` | `MCP tool` | `mcp` | `modules` | `write` | `Project.remove_module` | `path, module_id, source_root, write` | `Module remove payload` | `ProjectManifestError or ValueError on invalid module removal` | `module.remove` | `MCP tool registry: module_remove` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `module_file` | `MCP tool` | `mcp` | `modules` | `read` | `Project.read_module_file` | `path, module_id, relative_path, source_root, encoding` | `Module file payload` | `ProjectManifestError or FileNotFoundError on missing module file` | `module.file` | `MCP tool registry: module_file` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `module_asset` | `MCP tool` | `mcp` | `modules` | `read` | `Project.read_module_asset` | `path, module_id, relative_path, source_root, include_content` | `Registry-owned module asset payload` | `ProjectManifestError, OSError, or ValueError on invalid module asset` |  | `MCP tool registry: module_asset` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `module_source_form` | `MCP tool` | `mcp` | `modules` | `read` | `Project.read_module_file + Project.source_form` | `path, module_id, relative_path, source_root, encoding` | `Stable module file snapshot plus optional Registry-owned source form` | `ProjectManifestError, OSError, or ValueError on invalid module source form` |  | `MCP tool registry: module_source_form` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `module_source_form_update` | `MCP tool` | `mcp` | `modules` | `read` | `Project.read_module_file + Project.plan_source_form_update` | `path, module_id, relative_path, values, source_root, encoding` | `Revision-guarded full-text source edit plan from guided control values` | `ProjectManifestError, OSError, or ValueError on invalid guided source update` |  | `MCP tool registry: module_source_form_update` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `module_source_form_update_batch` | `MCP tool` | `mcp` | `modules` | `read` | `Project.read_module_file + Project.plan_source_form_updates` | `path, updates, source_root, encoding` | `Atomic draft plan for several guided module source updates` | `ProjectManifestError, OSError, or ValueError on invalid guided source update batch` |  | `MCP tool registry: module_source_form_update_batch` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `localization_workspace` | `MCP tool` | `mcp` | `authoring` | `read` | `Project.localization_workspace` | `path, target_kind, target_id, family, source_root, drafts, limit` | `Registry-owned cross-language source-unit localization workspace` | `ProjectManifestError, OSError, or ValueError on invalid localization workspace` | `localization.workspace` | `MCP tool registry: localization_workspace` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `localization_plan` | `MCP tool` | `mcp` | `authoring` | `read` | `Project.plan_localization_update` | `path, target_kind, target_id, operation, family, source_root, drafts, limit` | `Revision-guarded source-unit localization update plan` | `ProjectManifestError, OSError, or ValueError on invalid localization operation` | `localization.plan` | `MCP tool registry: localization_plan` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `module_edit` | `MCP tool` | `mcp` | `modules` | `write` | `Project.write_module_file` | `path, module_id, relative_path, text, source_root, create, encoding` | `Module file payload` | `ProjectManifestError or ValueError on invalid module file edit` | `module.edit` | `MCP tool registry: module_edit` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `collection_file` | `MCP tool` | `mcp` | `collections` | `read` | `Project.read_collection_file` | `path, collection_id, relative_path, family, source_root, encoding` | `Collection file payload` | `ProjectManifestError or FileNotFoundError on missing collection file` | `collection.file` | `MCP tool registry: collection_file` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `collection_edit` | `MCP tool` | `mcp` | `collections` | `write` | `Project.write_collection_file` | `path, collection_id, relative_path, text, family, source_root, create, encoding` | `Collection file payload` | `ProjectManifestError or ValueError on invalid collection file edit` | `collection.edit` | `MCP tool registry: collection_edit` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `collection_create` | `MCP tool` | `mcp` | `collections` | `write` | `Project.create_collection` | `path, family, collection_id, source_root, metadata, write, force` | `Collection create payload` | `ProjectManifestError or ValueError on invalid collection create` | `collection.create` | `MCP tool registry: collection_create` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `collection_rename` | `MCP tool` | `mcp` | `collections` | `write` | `Project.rename_collection` | `path, collection_id, target_id, family, source_root` | `Collection rename payload` | `ProjectManifestError or ValueError on invalid collection rename` | `collection.rename` | `MCP tool registry: collection_rename` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `collection_remove` | `MCP tool` | `mcp` | `collections` | `write` | `Project.remove_collection` | `path, collection_id, family, source_root, write, plan_hash` | `Collection remove payload` | `ProjectManifestError or ValueError on invalid collection removal` | `collection.remove` | `MCP tool registry: collection_remove` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `frontend_api` | `MCP tool` | `mcp` | `frontend-api` | `read` | `get_frontend_api_selection` | `operation_id, group_id, index_name, key` | `Frontend API contract or selected projection` | `ValueError on invalid frontend API selector` | `surface.frontend_api` | `MCP tool registry: frontend_api` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `api_catalog` | `MCP tool` | `mcp` | `api-catalog` | `read` | `get_api_catalog_selection` | `reference_id, index_name, key` | `API catalog table, row, or index lookup payload` | `ValueError or KeyError on invalid API catalog selector` |  | `MCP tool registry: api_catalog` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `surface_contracts` | `MCP tool` | `mcp` | `surface-contracts` | `read` | `get_surface_contract_selection` | `identifier, status` | `Surface contract summary, contract payload, or status id list` | `ValueError or KeyError on invalid surface contract selector` |  | `MCP tool registry: surface_contracts` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `pdx_parse` | `MCP tool` | `mcp` | `pdx` | `read` | `parse_pdx_file` | `path, include_dump, include_tokens` | `PDX parse payload` | `ValueError on invalid PDX parse request` | `pdx.parse` | `MCP tool registry: pdx_parse` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `pdx_format` | `MCP tool` | `mcp` | `pdx` | `write` | `format_pdx_file` | `path, indent, comments, write` | `PDX format payload` | `ValueError on invalid PDX format request` | `pdx.format` | `MCP tool registry: pdx_format` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `pdx_api` | `MCP tool` | `mcp` | `pdx` | `read` | `get_pdx_api_selection` | `symbol, index_name, key` | `PDX API table, row, or index lookup payload` | `ValueError or KeyError on invalid PDX API selector` |  | `MCP tool registry: pdx_api` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `lsp_api` | `MCP tool` | `mcp` | `lsp` | `read` | `get_lsp_api_selection` | `symbol, index_name, key` | `LSP API table, row, or index lookup payload` | `ValueError or KeyError on invalid LSP API selector` |  | `MCP tool registry: lsp_api` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `catalog_api` | `MCP tool` | `mcp` | `catalog` | `read` | `get_catalog_api_selection` | `symbol, index_name, key` | `Catalog API table, row, or index lookup payload` | `ValueError or KeyError on invalid catalog API selector` |  | `MCP tool registry: catalog_api` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `mcp_api` | `MCP tool` | `mcp` | `mcp` | `read` | `get_mcp_api_selection` | `symbol, index_name, key` | `MCP API table, row, or index lookup payload` | `ValueError or KeyError on invalid MCP API selector` |  | `MCP tool registry: mcp_api` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `cli_api` | `MCP tool` | `mcp` | `cli` | `read` | `get_cli_api_selection` | `symbol, index_name, key` | `CLI API table, row, or index lookup payload` | `ValueError or KeyError on invalid CLI API selector` |  | `MCP tool registry: cli_api` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `inspect_project` | `MCP tool` | `mcp` | `projects` | `read` | `Project.to_view` | `path` | `Project view payload` |  |  | `MCP tool registry: inspect_project` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `list_surfaces` | `MCP tool` | `mcp` | `architecture` | `read` | `get_architecture_spec` | `none` | `Architecture graph payload` |  | `surface.architecture` | `MCP tool registry: list_surfaces` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `describe_architecture` | `MCP tool` | `mcp` | `architecture` | `read` | `get_architecture_spec` | `none` | `Architecture graph payload` |  |  | `MCP tool registry: describe_architecture` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
| `architecture_api` | `MCP tool` | `mcp` | `architecture` | `read` | `get_architecture_api_selection` | `symbol, index_name, key` | `Architecture API table, row, or index lookup payload` | `ValueError or KeyError on invalid architecture API selector` |  | `MCP tool registry: architecture_api` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts` |
