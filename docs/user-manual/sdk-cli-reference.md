# SDK And CLI API Reference

Generated from `paradev.sdk.get_frontend_api_contract()`.

## English

This page is the compact HoI4 modder and automation entry map. Use it when you need to know which Python SDK call or CLI command backs a project, module, collection, build, PDX, LSP, catalog, or surface operation. For REST, MCP, LSP method, payload, and binding details, read [Frontend API Reference](frontend-api-reference.md).

Regenerate this file whenever the frontend API operation list changes:

```bash
rtk uv run paradev frontend-api --sdk-cli-markdown > docs/user-manual/sdk-cli-reference.md
```

## 中文

本页是面向 HoI4 Mod 作者和自动化脚本的紧凑入口表。需要确认某个 project、module、collection、build、PDX、LSP、catalog 或 surface 操作对应哪个 Python SDK 调用或 CLI 命令时，优先看这里。REST、MCP、LSP method、payload 和 binding 细节见 [前端 API Reference](frontend-api-reference.md)。

每次 frontend API operation list 变化后，用下面的命令重新生成本文件：

```bash
rtk uv run paradev frontend-api --sdk-cli-markdown > docs/user-manual/sdk-cli-reference.md
```

## Summary / 汇总

- Operations / 操作数: 98
- Implemented / 已实现: 97
- Frontend-local / 前端本地: 1

## Feature Summary / 功能汇总

Counts show how many operations each feature group exposes through Python SDK calls and CLI commands.

| Group | Title | Operations | Python SDK | CLI | Read | Write |
| --- | --- | --- | --- | --- | --- | --- |
| `projects` | Projects | 15 | 14 | 12 | 9 | 6 |
| `modules` | Modules | 20 | 20 | 19 | 9 | 11 |
| `collections` | Collections | 12 | 12 | 12 | 7 | 5 |
| `localization` | Localization | 2 | 2 | 0 | 2 | 0 |
| `build` | Build | 18 | 18 | 14 | 15 | 3 |
| `pdx` | PDX | 4 | 4 | 4 | 3 | 1 |
| `lsp` | LSP | 7 | 7 | 1 | 6 | 1 |
| `catalog` | Catalog | 4 | 4 | 4 | 2 | 2 |
| `ai` | AI | 4 | 4 | 0 | 2 | 2 |
| `surfaces` | Surfaces | 12 | 12 | 8 | 12 | 0 |

## Operation Matrix / 操作矩阵

### Projects (`projects`, 15 operations)

| Operation | Group | Mode | Python SDK | CLI | Inputs | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `project.create` | `projects` | `write` | `Project.create` | `new` | `path`, `project_id`, `title`, `game`, `force` | Create a starter project. |
| `project.find` | `projects` | `read` | `Project.find` | `project-find` | `path` | Find a project from a root or nested path without raising for missing manifests. |
| `project.open` | `projects` | `read` | `Project.load` | `project` | `path`, `game`, `title` | Discover and load a project from a root or nested path. |
| `project.view` | `projects` | `read` | `Project.to_view` | `project` | `path`, `game`, `title` | Return the loaded project view model. |
| `project.list` | `projects` | `read` | `registered_projects` | `projects` | `project_paths`, `search_roots` | List registered local ParaDev projects. |
| `project.inspect` | `projects` | `read` | `Project.inspect` | `inspections and inspection commands` | `path`, `kind` | Run one SDK-owned read-only inspection by kind and filters. |
| `project.config` | `projects` | `write` | `CM_PARADEV` | `config` |  | Read and write stored ParaDev config scopes. |
| `project.rename` | `projects` | `write` | `Project.rename` | `project-rename` | `title`, `path` | Rename the project display title without moving source folders. |
| `project.language` | `projects` | `write` | `Project.set_preferred_language` | `project-language` | `preferred_language`, `path`, `write`, `plan_hash` | Plan or apply the project-wide module-authoring language. |
| `project.activate` | `projects` | `write` |  |  | `project_id` | Select the active project in a frontend workspace. |
| `project.state` | `projects` | `read` | `desktop_state` | `desktop-state` | `project_path`, `project_paths`, `search_roots` | Return SDK-owned project switcher state for a desktop workspace. |
| `project.browser` | `projects` | `read` | `Project.browser` | `project-browser` | `path`, `profile`, `kind`, `family`, `module_id`, `collection_id` | Return the read-only project browser tree and indexes for frontend clients. |
| `project.source_text` | `projects` | `read` | `Project.read_source_text` |  | `project_id`, `path`, `source_path` | Read one project-contained source file from a browser row path. |
| `project.source_form` | `projects` | `read` | `Project.source_form` |  | `project_id`, `path`, `source_path`, `text`, `query` | Return an optional guided form for current canonical JSON or PDX source text. |
| `project.draft_apply` | `projects` | `write` | `Project.apply_source_draft` | `draft-apply` | `project_id`, `path`, `source_edits`, `source_removals`, `source_replacements`, `module_rename` | Apply validated source edits and an optional module-folder rename inside one project transaction. |

### Modules (`modules`, 20 operations)

| Operation | Group | Mode | Python SDK | CLI | Inputs | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `module.list` | `modules` | `read` | `Project.inspect('modules')` | `modules` | `path`, `profile`, `family`, `module_id`, `collection_id`, `source_slot` | List discovered build modules with filters. |
| `module.view` | `modules` | `read` | `Project.inspect('build-explain')` | `build-explain --module` | `path`, `module_id`, `profile` | Explain one module with source, artifact, dependency, and diagnostic context. |
| `module.templates` | `modules` | `read` | `Project.templates` | `templates` | `path`, `template_id`, `family`, `kind`, `source`, `authoring_ready`, `diagnostic_code` | List authoring templates and source roots available to module creation. |
| `module.create` | `modules` | `write` | `Project.scaffold_module` | `scaffold` | `path`, `template_id`, `object_id`, `source_root`, `values`, `write`, `force` | Plan or write a source module from an authoring template. |
| `module.create_batch` | `modules` | `write` | `Project.create_modules` | `module-batch-create` | `project_id`, `path`, `modules`, `source_root`, `write`, `plan_hash` | Plan or atomically create several source modules from one guarded plan. |
| `module.draft` | `modules` | `write` | `Project.create_module_draft` |  | `project_id`, `family_id`, `path`, `template_id`, `object_id`, `values`, `write`, `force` | Plan or write a source-module draft from a frontend browser family id. |
| `module.authoring_path` | `modules` | `read` | `Project.authoring_path` | `authoring-path` | `path`, `kind`, `family`, `target_id`, `source_root` | Resolve one canonical module folder without writing files. |
| `module.authoring_plan` | `modules` | `read` | `Project.authoring_plan` | `authoring-plan` | `path`, `kind`, `family`, `target_id`, `source_root`, `profile` | Resolve a module folder plus expected source-slot status. |
| `module.source_slots` | `modules` | `read` | `Project.inspect('source-slots')` | `source-slots` | `path`, `profile`, `family`, `module_id`, `collection_id`, `slot`, `status` | Show expected-versus-found source slots for modules. |
| `module.sources` | `modules` | `read` | `Project.inspect('sources')` | `sources` | `path`, `profile`, `family`, `module_id`, `collection_id`, `slot`, `loader`, `status` | Show compiler input source files for modules. |
| `module.diagram` | `modules` | `read` | `Project.module_diagram` | `module-diagram` | `path`, `family`, `profile` | Project one authoritative module family into a source-backed diagram. |
| `module.diagram.edit` | `modules` | `write` | `Project.edit_module_diagram` | `module-diagram-edit` | `path`, `family`, `profile`, `position_intents`, `edge_intents`, `node_intents`, `write`, `plan_hash` | Plan or apply bounded source-backed module diagram intents. |
| `module.file` | `modules` | `read` | `Project.read_module_file` | `module-file` | `path`, `module_id`, `relative_path`, `source_root`, `encoding` | Read one text source file from a module. |
| `module.edit` | `modules` | `write` | `Project.write_module_file` | `module-edit` | `path`, `module_id`, `relative_path`, `text`, `source_root`, `create`, `encoding` | Write one text source file inside a module. |
| `module.rename` | `modules` | `write` | `Project.rename_module` | `module-rename` | `path`, `module_id`, `object_id`, `title`, `source_root` | Rename a source module folder or synchronize its readable title without rewriting PDX content. |
| `module.duplicate` | `modules` | `write` | `Project.duplicate_module` | `module-duplicate` | `path`, `module_id`, `object_id`, `source_root`, `destination_source_root`, `identity`, `write`, `plan_hash` | Plan or atomically create an independent module copy through its family identity rewriter. |
| `module.collection.set` | `modules` | `write` | `Project.set_module_collection` | `module-collection-set` | `path`, `module_id`, `collection_id`, `source_root`, `write`, `plan_hash` | Plan or atomically move a module into a same-family collection, or clear its membership. |
| `module.activity.set` | `modules` | `write` | `Project.set_module_active` | `module-activity-set` | `path`, `module_id`, `active`, `source_root`, `write`, `plan_hash` | Plan or atomically include or omit one module in every compilation mode. |
| `module.metadata.clean` | `modules` | `write` | `Project.clean_module_metadata` | `module-metadata-clean` | `path`, `family`, `module_id`, `source_root`, `write`, `plan_hash` | Plan or atomically remove redundant path-derived module metadata. |
| `module.remove` | `modules` | `write` | `Project.remove_module` | `module-remove` | `path`, `module_id`, `source_root`, `write` | Plan or remove a source module folder. |

### Collections (`collections`, 12 operations)

| Operation | Group | Mode | Python SDK | CLI | Inputs | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `collection.list` | `collections` | `read` | `Project.inspect('collections')` | `collections` | `path`, `profile`, `family`, `collection_id`, `module_id`, `source_slot` | List discovered build collections with filters. |
| `collection.view` | `collections` | `read` | `Project.inspect('collections')` | `collections --collection` | `path`, `collection_id`, `profile` | Explain one collection with source, artifact, dependency, and diagnostic context. |
| `collection.authoring_path` | `collections` | `read` | `Project.authoring_path` | `authoring-path` | `path`, `kind`, `family`, `target_id`, `source_root` | Resolve one canonical collection descriptor folder without writing files. |
| `collection.authoring_plan` | `collections` | `read` | `Project.authoring_plan` | `authoring-plan` | `path`, `kind`, `family`, `target_id`, `source_root`, `profile` | Resolve a collection descriptor folder plus expected source-slot status. |
| `collection.source_slots` | `collections` | `read` | `Project.inspect('source-slots')` | `source-slots` | `path`, `profile`, `family`, `module_id`, `collection_id`, `slot`, `status` | Show expected-versus-found source slots for collection descriptors. |
| `collection.sources` | `collections` | `read` | `Project.inspect('sources')` | `sources --owner-kind collection` | `path`, `profile`, `family`, `collection_id`, `slot`, `loader`, `status`, `owner_kind` | Show compiler input source files owned by collection descriptors. |
| `collection.file` | `collections` | `read` | `Project.read_collection_file` | `collection-file` | `path`, `collection_id`, `relative_path`, `family`, `source_root`, `encoding` | Read one text source file from a collection descriptor. |
| `collection.scaffold` | `collections` | `write` | `Project.scaffold_collection` | `collection-scaffold` | `path`, `template_id`, `collection_id`, `source_root`, `values`, `write`, `force`, `plan_hash` | Plan or transactionally write a collection from a Registry-backed template. |
| `collection.create` | `collections` | `write` | `Project.create_collection` | `collection-create` | `path`, `family`, `collection_id`, `source_root`, `metadata`, `write`, `force` | Plan or write a collection descriptor metadata scaffold. |
| `collection.edit` | `collections` | `write` | `Project.write_collection_file` | `collection-edit` | `path`, `collection_id`, `relative_path`, `text`, `family`, `source_root`, `create`, `encoding` | Write one text source file inside a collection descriptor. |
| `collection.rename` | `collections` | `write` | `Project.rename_collection` | `collection-rename` | `path`, `collection_id`, `target_id`, `family`, `source_root` | Rename a collection descriptor folder within its current family without rewriting authored content. |
| `collection.remove` | `collections` | `write` | `Project.remove_collection` | `collection-remove` | `path`, `collection_id`, `family`, `source_root`, `write`, `plan_hash` | Plan or remove a collection while preserving and ungrouping its modules. |

### Localization (`localization`, 2 operations)

| Operation | Group | Mode | Python SDK | CLI | Inputs | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `localization.workspace` | `localization` | `read` | `Project.localization_workspace` |  | `project_id`, `path`, `target_kind`, `target_id`, `family`, `source_root`, `drafts`, `limit` | Return one Registry-owned cross-language localization workspace for a module or collection. |
| `localization.plan` | `localization` | `read` | `Project.plan_localization_update` |  | `project_id`, `path`, `target_kind`, `target_id`, `family`, `source_root`, `drafts`, `limit`, `operation` | Plan one lossless Registry-owned localization edit without writing source files. |

### Build (`build`, 18 operations)

| Operation | Group | Mode | Python SDK | CLI | Inputs | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `build.plan` | `build` | `read` | `Project.build` | `build` | `path`, `profile`, `strict_metadata` | Run a dry build plan. |
| `build.emit` | `build` | `write` | `Project.build` | `build --emit-artifacts/--emit-manifests` | `path`, `profile`, `strict_metadata`, `emit_artifacts`, `emit_manifests` | Plan once, write only when diagnostics pass, and return the blocked dry result otherwise. |
| `build.start` | `build` | `write` | `desktop_start_build` |  | `project_root`, `mode`, `profile`, `strict_metadata`, `parallelism`, `target` | Start one desktop build run through the Python desktop facade. |
| `build.runs` | `build` | `read` | `desktop_build_runs` |  | `project_root` | List active and retained terminal desktop build runs. |
| `build.status` | `build` | `read` | `desktop_build_status` |  | `run_id` | Return active or retained terminal status for one exact desktop build run. |
| `build.interrupt` | `build` | `write` | `desktop_interrupt_build` |  | `run_id` | Interrupt one exact active desktop build run or return its retained terminal status. |
| `build.summary` | `build` | `read` | `Project.inspect('summary')` | `summary` | `path`, `profile` | Read the build summary. |
| `build.manifests` | `build` | `read` | `Project.inspect('manifests')` | `manifests` | `path`, `profile` | Read all build manifest payloads. |
| `build.artifacts` | `build` | `read` | `Project.inspect('artifacts')` | `artifacts` | `path`, `profile`, `artifact_type`, `target_root`, `owner`, `artifact_path`, `mode`, `module_id`, `collection_id` | List planned artifacts. |
| `build.localization` | `build` | `read` | `Project.inspect('localization')` | `localization` | `path`, `profile`, `language`, `key`, `key_prefix`, `module_id`, `collection_id` | List loaded localization rows. |
| `build.assets` | `build` | `read` | `Project.inspect('assets')` | `assets` | `path`, `profile`, `module_id`, `collection_id`, `family`, `slot`, `file_format` | List loaded static copy assets. |
| `build.sprites` | `build` | `read` | `Project.inspect('sprites')` | `sprites` | `path`, `profile`, `module_id`, `collection_id`, `family`, `slot`, `name` | List planned interface sprite declarations. |
| `build.diagnostics` | `build` | `read` | `Project.inspect('diagnostics')` | `diagnostics` | `path`, `profile`, `severity`, `code`, `family`, `owner`, `target_root`, `module_id`, `collection_id`, `source_path`, `slot`, `strict_metadata`, `published` | List build diagnostics. |
| `build.source_map` | `build` | `read` | `Project.inspect('source-map')` | `source-map` | `path`, `profile`, `module_id`, `collection_id`, `family`, `slot`, `artifact_type`, `target_root` | Trace artifacts back to source rows. |
| `build.dependencies` | `build` | `read` | `Project.inspect('dependencies')` | `dependencies` | `path`, `profile`, `source`, `target`, `kind`, `module_id` | List build dependency edges. |
| `build.graph` | `build` | `read` | `Project.inspect('build-graph')` | `build-graph` | `path`, `profile`, `module_id`, `collection_id`, `family`, `slot`, `artifact_type`, `target_root`, `edge_kind` | Return grouped source, artifact, and dependency graph nodes and edges. |
| `build.explain` | `build` | `read` | `Project.inspect('build-explain')` | `build-explain` | `path`, `module_id`, `collection_id`, `source_path`, `artifact_path`, `diagnostic_code`, `target_root`, `profile` | Explain one module, collection, source, artifact, or diagnostic. |
| `build.families` | `build` | `read` | `Project.inspect('families')` | `families` | `path`, `profile`, `family`, `kind`, `source_slot`, `collection_source_slot`, `sprite_slot`, `route`, `artifact_type` | List compiler family and authoring contracts. |

### PDX (`pdx`, 4 operations)

| Operation | Group | Mode | Python SDK | CLI | Inputs | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `pdx.parse` | `pdx` | `read` | `parse_pdx_file` | `parse` | `path`, `include_dump`, `include_tokens` | Parse one PDX file. |
| `pdx.tokens` | `pdx` | `read` | `parse_pdx_file(..., include_tokens=True)` | `parse --tokens` | `path`, `include_tokens` | Parse one PDX file and include lexer token rows. |
| `pdx.dump` | `pdx` | `read` | `parse_pdx_file(..., include_dump=True)` | `parse --dump` | `path`, `include_dump` | Parse one PDX file and include the lossless AST dump. |
| `pdx.format` | `pdx` | `write` | `format_pdx_file` | `format` | `path`, `indent`, `comments`, `write` | Format PDX text through the SDK formatter. |

### LSP (`lsp`, 7 operations)

| Operation | Group | Mode | Python SDK | CLI | Inputs | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `lsp.diagnostics` | `lsp` | `read` | `diagnose_pdx_lsp_text` |  | `text`, `uri`, `path` | Publish document diagnostics. |
| `lsp.symbols` | `lsp` | `read` | `document_symbols_pdx_lsp_text` |  | `text`, `uri`, `path` | Return document symbols. |
| `lsp.hover` | `lsp` | `read` | `hover_pdx_lsp_text` |  | `text`, `line`, `character`, `uri`, `path` | Return hover details for a document position. |
| `lsp.formatting` | `lsp` | `write` | `format_pdx_lsp_text` |  | `text`, `uri`, `path`, `indent`, `comments` | Return text edits for PDX formatting. |
| `lsp.completion` | `lsp` | `read` | `complete_pdx_lsp_text` |  | `text`, `line`, `character`, `offset`, `uri`, `path`, `project_path`, `database`, `game_root`, `limit` | Return catalog-backed completion items for a document position. |
| `lsp.semantic_tokens` | `lsp` | `read` | `semantic_tokens_pdx_lsp_text` |  | `text`, `uri`, `path` | Return semantic tokens for PDX highlighting. |
| `lsp.keywords` | `lsp` | `read` | `hoi4_keyword_dataset` | `lsp keywords` | `game_root` | Return the HOI4 keyword dataset used by editor completion. |

### Catalog (`catalog`, 4 operations)

| Operation | Group | Mode | Python SDK | CLI | Inputs | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `catalog.preview` | `catalog` | `read` | `Project.inspect('catalog-preview')` | `hb catalog-preview` | `path`, `profile` | Return deterministic HeavenBase-ready catalog rows. |
| `catalog.write` | `catalog` | `write` | `paradev.hb.catalog_write` | `hb catalog-write` | `path`, `profile`, `database` | Write preview rows to a local HeavenBase catalog database. |
| `catalog.refresh` | `catalog` | `write` | `paradev.hb.catalog_refresh` | `hb catalog-refresh` | `path`, `profile`, `database` | Replace the local HeavenBase catalog database. |
| `catalog.query` | `catalog` | `read` | `Project.inspect('catalog-query')` | `hb catalog-query` | `path`, `database`, `entity`, `target_id`, `name`, `tag`, `limit`, `offset`, `include_data` | Query written HeavenBase catalog rows. |

### AI (`ai`, 4 operations)

| Operation | Group | Mode | Python SDK | CLI | Inputs | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `ai.profiles` | `ai` | `read` | `desktop_chat_profiles` |  | `project_root` | Return SDK-owned desktop AI chat role profiles. |
| `ai.profile.write` | `ai` | `write` | `desktop_write_chat_profile` |  | `profile_id`, `profile`, `project_root` | Write one SDK-owned desktop AI chat role profile override. |
| `ai.profile.reset` | `ai` | `write` | `desktop_reset_chat_profile` |  | `profile_id`, `project_root` | Reset one SDK-owned desktop AI chat role profile override to built-in defaults. |
| `ai.chat` | `ai` | `read` | `desktop_chat` |  | `provider`, `model`, `gateway`, `preset`, `key_env`, `base_url`, `prompt`, `role`, `project_root`, `sources` | Send one desktop AI chat prompt through the Python SDK and HeavenBase. |

### Surfaces (`surfaces`, 12 operations)

| Operation | Group | Mode | Python SDK | CLI | Inputs | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `surface.frontend_api` | `surfaces` | `read` | `get_frontend_api_selection` | `frontend-api` | `operation_id`, `group_id`, `form` | Return this frontend API contract. |
| `surface.frontend_api.workspace` | `surfaces` | `read` | `get_frontend_api_workspace` | `frontend-api --workspace` |  | Return the SDK-owned frontend workspace action projection. |
| `surface.frontend_api.action` | `surfaces` | `read` | `get_frontend_api_action` | `frontend-api --operation --action` | `operation_id` | Return one frontend operation's workspace action, form, bindings, and option-source summary. |
| `surface.frontend_api.normalize` | `surfaces` | `read` | `normalize_frontend_api_inputs` | `frontend-api --operation --values-json` | `operation_id`, `values` | Normalize submitted frontend API form values into adapter buckets. |
| `surface.frontend_api.rest_request` | `surfaces` | `read` | `plan_frontend_api_rest_request` | `frontend-api --operation --values-json --rest-request` | `operation_id`, `values` | Plan the REST request for submitted frontend API form values. |
| `surface.frontend_api.options` | `surfaces` | `read` | `resolve_frontend_api_options` | `frontend-api --operation --option-field --values-json` | `operation_id`, `field_name`, `values` | Resolve dynamic form field options from SDK-owned option-source providers. |
| `surface.frontend_api.binding_lookup` | `surfaces` | `read` | `get_frontend_api_binding_lookup` | `frontend-api --binding-surface --binding-key` | `binding_surface`, `binding_key` | Map one SDK, CLI, REST, MCP, or LSP surface call key back to frontend operation ids. |
| `surface.architecture` | `surfaces` | `read` | `get_architecture_spec` | `architecture` |  | Return the SDK-owned architecture graph. |
| `surface.openapi` | `surfaces` | `read` | `get_openapi_seed` |  |  | Return the local REST/OpenAPI seed. |
| `surface.cli_contract` | `surfaces` | `read` | `get_cli_contract` |  |  | Return the CLI adapter contract. |
| `surface.mcp_contract` | `surfaces` | `read` | `get_mcp_contract` |  |  | Return the MCP toolkit contract. |
| `surface.lsp_contract` | `surfaces` | `read` | `get_lsp_contract` |  |  | Return the LSP capability contract. |
