# API Catalog Reference

Generated from `paradev.surfaces.get_api_catalog_table()`.

Regenerate this file whenever an API reference table or generated contract is added, removed, or renamed:

```bash
rtk uv run paradev api-catalog --markdown > docs/user-manual/api-catalog-reference.md
```

## Summary / 汇总

- References / Reference 数: 29
- Layers / Layer 数: 16
- Features / Feature 数: 27
- Kinds / 类型数: 12
- Reference groups / Reference 分组数: 6
- Index dimensions / Index 维度数: 11
- Owner modules / Owner Module 数: 19
- Surfaces / Surface 数: 11
- CLI commands / CLI 命令数: 28
- Selector helpers / Selector helper 数: 28
- Doc pages / Doc page 数: 29

## Reference Groups / Reference 分组

Reader-oriented group map derived from the generated kind index.

| Group | Title | References | Kinds | IDs | Use |
| --- | --- | --- | --- | --- | --- |
| `overall` | Overall Catalog | 1 | `api-catalog` | `api-catalog` | Start here for the complete generated reference inventory and selector map. |
| `facades` | Facade API Tables | 14 | `facade-table` | `sdk-api`, `package-api`, `config-api`, `gui-api`, `desktop-api`, `games-api`, `surfaces-api`, `project-facade-api`, `localization-api`, `build-api`, `pdx-core-api`, `lsp-server-api`, `hb-api`, `rest-facade-api` | Stable package and layer import surfaces exposed to SDK users and developers. |
| `modules` | Object and Module Tables | 3 | `object-table`, `module-table` | `project-api`, `templates-api`, `copy-roots-api` | Concrete SDK object and module contracts for project, template, and copy-root work. |
| `workflows` | Workflow Contracts | 3 | `operation-contract`, `operation-matrix`, `inspection-contract` | `frontend-api`, `sdk-cli-reference`, `project-inspection-reference` | Generated operation, CLI workflow, and inspection contracts shared by GUIs and agents. |
| `surfaces` | Surface API Tables | 7 | `api-table`, `route-table`, `tool-table`, `command-table` | `architecture-api`, `pdx-api`, `lsp-api`, `catalog-api`, `rest-api`, `mcp-api`, `cli-api` | Callable SDK, REST, MCP, and CLI surface tables with selector helpers. |
| `adapters` | Adapter Contracts | 1 | `surface-contract` | `surface-contract-reference` | Cross-surface adapter status and ownership contracts. |

## Index Catalog / Index 目录

| Index | Table Path | Python Helper | Use |
| --- | --- | --- | --- |
| `id` | `table["rows"][*]["id"]` | `get_api_catalog_reference(reference_id)` | Reference id to one aggregate API catalog row. |
| `layer` | `table["layer_index"][layer]` | `get_api_catalog_reference_ids('layer', layer)` | Architecture layer to generated reference ids. |
| `feature` | `table["feature_index"][feature]` | `get_api_catalog_reference_ids('feature', feature)` | Feature area to generated reference ids. |
| `kind` | `table["kind_index"][kind]` | `get_api_catalog_reference_ids('kind', kind)` | Reference kind to generated reference ids. |
| `group` | `table["group_index"][group]` | `get_api_catalog_group_reference_ids(group)` | Reader-oriented reference group to generated reference ids. |
| `reference_group` | `table["reference_groups"][*]["id"]` | `get_api_catalog_reference_group(group)` | Reference group id to one reader-oriented reference group row. |
| `owner_module` | `table["owner_module_index"][owner_module]` | `get_api_catalog_reference_ids('owner_module', owner_module)` | Owner module import path to generated reference ids. |
| `surface` | `table["surface_index"][surface]` | `get_api_catalog_reference_ids('surface', surface)` | Surface id to generated reference ids. |
| `cli_command` | `table["cli_command_index"][cli_command]` | `get_api_catalog_reference_ids('cli_command', cli_command)` | CLI command stem to generated reference ids. |
| `selector_helper` | `table["selector_helper_index"][selector_helper]` | `get_api_catalog_reference_ids('selector_helper', selector_helper)` | Shared selector helper to generated reference ids. |
| `doc_page` | `table["doc_page_index"][doc_page]` | `get_api_catalog_reference_ids('doc_page', doc_page)` | Manual page path to generated reference ids. |

## Layer Index / Layer 索引

| Layer | References | IDs |
| --- | --- | --- |
| `surface` | 3 | `api-catalog`, `surfaces-api`, `surface-contract-reference` |
| `sdk` | 10 | `sdk-api`, `project-api`, `templates-api`, `copy-roots-api`, `frontend-api`, `sdk-cli-reference`, `project-inspection-reference`, `architecture-api`, `pdx-api`, `lsp-api` |
| `package` | 1 | `package-api` |
| `config` | 1 | `config-api` |
| `gui` | 1 | `gui-api` |
| `desktop` | 1 | `desktop-api` |
| `games` | 1 | `games-api` |
| `project` | 1 | `project-facade-api` |
| `localization` | 1 | `localization-api` |
| `build` | 1 | `build-api` |
| `pdx` | 1 | `pdx-core-api` |
| `lsp` | 1 | `lsp-server-api` |
| `hb` | 2 | `catalog-api`, `hb-api` |
| `rest` | 2 | `rest-api`, `rest-facade-api` |
| `mcp` | 1 | `mcp-api` |
| `cli` | 1 | `cli-api` |

## Feature Index / Feature 索引

| Feature | References | IDs |
| --- | --- | --- |
| `overall` | 1 | `api-catalog` |
| `facade` | 3 | `sdk-api`, `package-api`, `hb-api` |
| `config` | 1 | `config-api` |
| `launcher` | 1 | `gui-api` |
| `state` | 1 | `desktop-api` |
| `profiles` | 1 | `games-api` |
| `surfaces` | 1 | `surfaces-api` |
| `projects` | 1 | `project-api` |
| `authoring` | 1 | `templates-api` |
| `copy-roots` | 1 | `copy-roots-api` |
| `project-facade` | 1 | `project-facade-api` |
| `localization` | 1 | `localization-api` |
| `compiler` | 1 | `build-api` |
| `frontend` | 1 | `frontend-api` |
| `sdk-cli` | 1 | `sdk-cli-reference` |
| `inspections` | 1 | `project-inspection-reference` |
| `architecture` | 1 | `architecture-api` |
| `pdx` | 1 | `pdx-api` |
| `pdx-core` | 1 | `pdx-core-api` |
| `lsp` | 1 | `lsp-api` |
| `lsp-server` | 1 | `lsp-server-api` |
| `catalog` | 1 | `catalog-api` |
| `rest` | 1 | `rest-api` |
| `rest-facade` | 1 | `rest-facade-api` |
| `mcp` | 1 | `mcp-api` |
| `cli` | 1 | `cli-api` |
| `adapters` | 1 | `surface-contract-reference` |

## Kind Index / 类型索引

| Kind | References | IDs |
| --- | --- | --- |
| `api-catalog` | 1 | `api-catalog` |
| `facade-table` | 14 | `sdk-api`, `package-api`, `config-api`, `gui-api`, `desktop-api`, `games-api`, `surfaces-api`, `project-facade-api`, `localization-api`, `build-api`, `pdx-core-api`, `lsp-server-api`, `hb-api`, `rest-facade-api` |
| `object-table` | 1 | `project-api` |
| `module-table` | 2 | `templates-api`, `copy-roots-api` |
| `operation-contract` | 1 | `frontend-api` |
| `operation-matrix` | 1 | `sdk-cli-reference` |
| `inspection-contract` | 1 | `project-inspection-reference` |
| `api-table` | 4 | `architecture-api`, `pdx-api`, `lsp-api`, `catalog-api` |
| `route-table` | 1 | `rest-api` |
| `tool-table` | 1 | `mcp-api` |
| `command-table` | 1 | `cli-api` |
| `surface-contract` | 1 | `surface-contract-reference` |

## Reference Group Index / Reference 分组索引

| Group | References | IDs |
| --- | --- | --- |
| `overall` | 1 | `api-catalog` |
| `facades` | 14 | `sdk-api`, `package-api`, `config-api`, `gui-api`, `desktop-api`, `games-api`, `surfaces-api`, `project-facade-api`, `localization-api`, `build-api`, `pdx-core-api`, `lsp-server-api`, `hb-api`, `rest-facade-api` |
| `modules` | 3 | `project-api`, `templates-api`, `copy-roots-api` |
| `workflows` | 3 | `frontend-api`, `sdk-cli-reference`, `project-inspection-reference` |
| `surfaces` | 7 | `architecture-api`, `pdx-api`, `lsp-api`, `catalog-api`, `rest-api`, `mcp-api`, `cli-api` |
| `adapters` | 1 | `surface-contract-reference` |

## Owner Module Index / Owner Module 索引

| Owner Module | References | IDs |
| --- | --- | --- |
| `paradev.surfaces` | 3 | `api-catalog`, `surfaces-api`, `surface-contract-reference` |
| `paradev.sdk` | 8 | `sdk-api`, `project-api`, `frontend-api`, `sdk-cli-reference`, `project-inspection-reference`, `architecture-api`, `pdx-api`, `lsp-api` |
| `paradev` | 1 | `package-api` |
| `paradev.config` | 1 | `config-api` |
| `paradev.gui` | 1 | `gui-api` |
| `paradev.desktop` | 1 | `desktop-api` |
| `paradev.games` | 1 | `games-api` |
| `paradev.sdk.templates` | 1 | `templates-api` |
| `paradev.sdk.copy_roots` | 1 | `copy-roots-api` |
| `paradev.project` | 1 | `project-facade-api` |
| `paradev.localization` | 1 | `localization-api` |
| `paradev.build` | 1 | `build-api` |
| `paradev.pdx` | 1 | `pdx-core-api` |
| `paradev.lsp` | 1 | `lsp-server-api` |
| `paradev.hb` | 2 | `catalog-api`, `hb-api` |
| `paradev.surfaces.rest` | 1 | `rest-api` |
| `paradev.api` | 1 | `rest-facade-api` |
| `paradev.surfaces.mcp` | 1 | `mcp-api` |
| `paradev.surfaces.cli` | 1 | `cli-api` |

## Surface Index / Surface 索引

| Surface | References | IDs |
| --- | --- | --- |
| `sdk` | 25 | `api-catalog`, `sdk-api`, `package-api`, `config-api`, `gui-api`, `desktop-api`, `games-api`, `surfaces-api`, `project-api`, `templates-api`, `copy-roots-api`, `project-facade-api`, `localization-api`, `build-api`, `frontend-api`, `sdk-cli-reference`, `project-inspection-reference`, `architecture-api`, `pdx-api`, `pdx-core-api`, `lsp-api`, `lsp-server-api`, `catalog-api`, `hb-api`, `rest-facade-api` |
| `cli` | 29 | `api-catalog`, `sdk-api`, `package-api`, `config-api`, `gui-api`, `desktop-api`, `games-api`, `surfaces-api`, `project-api`, `templates-api`, `copy-roots-api`, `project-facade-api`, `localization-api`, `build-api`, `frontend-api`, `sdk-cli-reference`, `project-inspection-reference`, `architecture-api`, `pdx-api`, `pdx-core-api`, `lsp-api`, `lsp-server-api`, `catalog-api`, `hb-api`, `rest-api`, `rest-facade-api`, `mcp-api`, `cli-api`, `surface-contract-reference` |
| `rest` | 12 | `api-catalog`, `surfaces-api`, `frontend-api`, `project-inspection-reference`, `architecture-api`, `pdx-api`, `lsp-api`, `catalog-api`, `rest-api`, `rest-facade-api`, `cli-api`, `surface-contract-reference` |
| `mcp` | 11 | `api-catalog`, `surfaces-api`, `frontend-api`, `project-inspection-reference`, `architecture-api`, `pdx-api`, `lsp-api`, `catalog-api`, `mcp-api`, `cli-api`, `surface-contract-reference` |
| `docs` | 29 | `api-catalog`, `sdk-api`, `package-api`, `config-api`, `gui-api`, `desktop-api`, `games-api`, `surfaces-api`, `project-api`, `templates-api`, `copy-roots-api`, `project-facade-api`, `localization-api`, `build-api`, `frontend-api`, `sdk-cli-reference`, `project-inspection-reference`, `architecture-api`, `pdx-api`, `pdx-core-api`, `lsp-api`, `lsp-server-api`, `catalog-api`, `hb-api`, `rest-api`, `rest-facade-api`, `mcp-api`, `cli-api`, `surface-contract-reference` |
| `desktop` | 2 | `gui-api`, `desktop-api` |
| `lsp` | 6 | `surfaces-api`, `frontend-api`, `lsp-api`, `lsp-server-api`, `catalog-api`, `surface-contract-reference` |
| `frontend` | 7 | `project-api`, `templates-api`, `frontend-api`, `project-inspection-reference`, `rest-api`, `mcp-api`, `cli-api` |
| `typescript` | 1 | `frontend-api` |
| `vscode` | 1 | `surface-contract-reference` |
| `bundle` | 1 | `surface-contract-reference` |

## Regeneration Index / 重新生成索引

| CLI Command | References | IDs |
| --- | --- | --- |
| `api-catalog` | 1 | `api-catalog` |
| `sdk-api` | 1 | `sdk-api` |
| `package-api` | 1 | `package-api` |
| `config-api` | 1 | `config-api` |
| `gui-api` | 1 | `gui-api` |
| `desktop-api` | 1 | `desktop-api` |
| `games-api` | 1 | `games-api` |
| `surfaces-api` | 1 | `surfaces-api` |
| `project-api` | 1 | `project-api` |
| `templates-api` | 1 | `templates-api` |
| `copy-roots-api` | 1 | `copy-roots-api` |
| `project-facade-api` | 1 | `project-facade-api` |
| `localization-api` | 1 | `localization-api` |
| `build-api` | 1 | `build-api` |
| `frontend-api` | 2 | `frontend-api`, `sdk-cli-reference` |
| `inspections` | 1 | `project-inspection-reference` |
| `architecture --api-table` | 1 | `architecture-api` |
| `pdx-api` | 1 | `pdx-api` |
| `pdx-core-api` | 1 | `pdx-core-api` |
| `lsp-api` | 1 | `lsp-api` |
| `lsp-server-api` | 1 | `lsp-server-api` |
| `catalog-api` | 1 | `catalog-api` |
| `hb-api` | 1 | `hb-api` |
| `rest-api` | 1 | `rest-api` |
| `rest-facade-api` | 1 | `rest-facade-api` |
| `mcp-api` | 1 | `mcp-api` |
| `cli-api` | 1 | `cli-api` |
| `architecture --surface-contracts` | 1 | `surface-contract-reference` |

## Selector Helper Index / Selector Helper 索引

| Selector Helper | References | IDs |
| --- | --- | --- |
| `get_api_catalog_selection` | 1 | `api-catalog` |
| `get_sdk_api_selection` | 1 | `sdk-api` |
| `get_package_api_selection` | 1 | `package-api` |
| `get_config_api_selection` | 1 | `config-api` |
| `get_gui_api_selection` | 1 | `gui-api` |
| `get_desktop_api_selection` | 1 | `desktop-api` |
| `get_games_api_selection` | 1 | `games-api` |
| `get_surfaces_api_selection` | 1 | `surfaces-api` |
| `get_project_api_selection` | 1 | `project-api` |
| `get_templates_api_selection` | 1 | `templates-api` |
| `get_copy_roots_api_selection` | 1 | `copy-roots-api` |
| `get_project_facade_api_selection` | 1 | `project-facade-api` |
| `get_localization_api_selection` | 1 | `localization-api` |
| `get_build_api_selection` | 1 | `build-api` |
| `get_frontend_api_selection` | 2 | `frontend-api`, `sdk-cli-reference` |
| `get_project_inspection_selection` | 1 | `project-inspection-reference` |
| `get_architecture_api_selection` | 1 | `architecture-api` |
| `get_pdx_api_selection` | 1 | `pdx-api` |
| `get_pdx_core_api_selection` | 1 | `pdx-core-api` |
| `get_lsp_api_selection` | 1 | `lsp-api` |
| `get_lsp_server_api_selection` | 1 | `lsp-server-api` |
| `get_catalog_api_selection` | 1 | `catalog-api` |
| `get_hb_api_selection` | 1 | `hb-api` |
| `get_rest_api_selection` | 1 | `rest-api` |
| `get_rest_facade_api_selection` | 1 | `rest-facade-api` |
| `get_mcp_api_selection` | 1 | `mcp-api` |
| `get_cli_api_selection` | 1 | `cli-api` |
| `get_surface_contract_selection` | 1 | `surface-contract-reference` |

## Doc Page Index / Doc Page 索引

| Doc Page | References | IDs |
| --- | --- | --- |
| `docs/user-manual/api-catalog-reference.md` | 1 | `api-catalog` |
| `docs/user-manual/sdk-api-reference.md` | 1 | `sdk-api` |
| `docs/user-manual/package-api-reference.md` | 1 | `package-api` |
| `docs/user-manual/config-api-reference.md` | 1 | `config-api` |
| `docs/user-manual/gui-api-reference.md` | 1 | `gui-api` |
| `docs/user-manual/desktop-api-reference.md` | 1 | `desktop-api` |
| `docs/user-manual/games-api-reference.md` | 1 | `games-api` |
| `docs/user-manual/surfaces-api-reference.md` | 1 | `surfaces-api` |
| `docs/user-manual/project-api-reference.md` | 1 | `project-api` |
| `docs/user-manual/templates-api-reference.md` | 1 | `templates-api` |
| `docs/user-manual/copy-roots-api-reference.md` | 1 | `copy-roots-api` |
| `docs/user-manual/project-facade-api-reference.md` | 1 | `project-facade-api` |
| `docs/user-manual/localization-api-reference.md` | 1 | `localization-api` |
| `docs/user-manual/build-api-reference.md` | 1 | `build-api` |
| `docs/user-manual/frontend-api-reference.md` | 1 | `frontend-api` |
| `docs/user-manual/sdk-cli-reference.md` | 1 | `sdk-cli-reference` |
| `docs/user-manual/project-inspection-reference.md` | 1 | `project-inspection-reference` |
| `docs/user-manual/architecture-api-reference.md` | 1 | `architecture-api` |
| `docs/user-manual/pdx-api-reference.md` | 1 | `pdx-api` |
| `docs/user-manual/pdx-core-api-reference.md` | 1 | `pdx-core-api` |
| `docs/user-manual/lsp-api-reference.md` | 1 | `lsp-api` |
| `docs/user-manual/lsp-server-api-reference.md` | 1 | `lsp-server-api` |
| `docs/user-manual/catalog-api-reference.md` | 1 | `catalog-api` |
| `docs/user-manual/hb-api-reference.md` | 1 | `hb-api` |
| `docs/user-manual/rest-api-reference.md` | 1 | `rest-api` |
| `docs/user-manual/rest-facade-api-reference.md` | 1 | `rest-facade-api` |
| `docs/user-manual/mcp-api-reference.md` | 1 | `mcp-api` |
| `docs/user-manual/cli-api-reference.md` | 1 | `cli-api` |
| `docs/user-manual/surface-contract-reference.md` | 1 | `surface-contract-reference` |

## API Catalog Table / API Catalog 表

| ID | Title | Kind | Layer | Feature | Schema | Rows | Table Helper | Selector Helper | Markdown Helper | CLI Command | Markdown CLI Command | Indexes | Surfaces | Doc Page | Test Anchor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `api-catalog` | API Catalog Reference | `api-catalog` | `surface` | `overall` | `paradev.api-catalog.v1` | 29 | `get_api_catalog_table` | `get_api_catalog_selection` | `render_api_catalog_reference_markdown` | `api-catalog` | `api-catalog --markdown` | `cli_command_index`, `doc_page_index`, `feature_index`, `group_index`, `kind_index`, `layer_index`, `owner_module_index`, `selector_helper_index`, `surface_index` | `sdk`, `cli`, `rest`, `mcp`, `docs` | `docs/user-manual/api-catalog-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `sdk-api` | SDK API Reference | `facade-table` | `sdk` | `facade` | `paradev.sdk.api-table.v1` | 138 | `get_sdk_api_table` | `get_sdk_api_selection` | `render_sdk_api_reference_markdown` | `sdk-api` | `sdk-api --markdown` | `feature_index`, `kind_index`, `module_index` | `sdk`, `cli`, `docs` | `docs/user-manual/sdk-api-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `package-api` | Package API Reference | `facade-table` | `package` | `facade` | `paradev.package.api-table.v1` | 15 | `get_package_api_table` | `get_package_api_selection` | `render_package_api_reference_markdown` | `package-api` | `package-api --markdown` | `feature_index`, `kind_index`, `module_index` | `sdk`, `cli`, `docs` | `docs/user-manual/package-api-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `config-api` | Config API Reference | `facade-table` | `config` | `config` | `paradev.config.api-table.v1` | 15 | `get_config_api_table` | `get_config_api_selection` | `render_config_api_reference_markdown` | `config-api` | `config-api --markdown` | `feature_index`, `kind_index`, `module_index` | `sdk`, `cli`, `docs` | `docs/user-manual/config-api-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `gui-api` | GUI API Reference | `facade-table` | `gui` | `launcher` | `paradev.gui.api-table.v1` | 8 | `get_gui_api_table` | `get_gui_api_selection` | `render_gui_api_reference_markdown` | `gui-api` | `gui-api --markdown` | `feature_index`, `kind_index`, `module_index` | `sdk`, `cli`, `desktop`, `docs` | `docs/user-manual/gui-api-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `desktop-api` | Desktop API Reference | `facade-table` | `desktop` | `state` | `paradev.desktop.api-table.v1` | 57 | `get_desktop_api_table` | `get_desktop_api_selection` | `render_desktop_api_reference_markdown` | `desktop-api` | `desktop-api --markdown` | `feature_index`, `kind_index`, `module_index` | `sdk`, `cli`, `desktop`, `docs` | `docs/user-manual/desktop-api-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `games-api` | Games API Reference | `facade-table` | `games` | `profiles` | `paradev.games.api-table.v1` | 8 | `get_games_api_table` | `get_games_api_selection` | `render_games_api_reference_markdown` | `games-api` | `games-api --markdown` | `feature_index`, `kind_index`, `module_index` | `sdk`, `cli`, `docs` | `docs/user-manual/games-api-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `surfaces-api` | Surfaces API Reference | `facade-table` | `surface` | `surfaces` | `paradev.surfaces.api-table.v1` | 56 | `get_surfaces_api_table` | `get_surfaces_api_selection` | `render_surfaces_api_reference_markdown` | `surfaces-api` | `surfaces-api --markdown` | `feature_index`, `kind_index`, `module_index` | `sdk`, `cli`, `rest`, `mcp`, `lsp`, `docs` | `docs/user-manual/surfaces-api-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `project-api` | Project API Reference | `object-table` | `sdk` | `projects` | `paradev.sdk.project-api-table.v1` | 81 | `get_project_api_table` | `get_project_api_selection` | `render_project_api_reference_markdown` | `project-api` | `project-api --markdown` | `cli_command_index`, `feature_index`, `frontend_operation_index`, `inspection_kind_index`, `kind_index` | `sdk`, `cli`, `frontend`, `docs` | `docs/user-manual/project-api-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `templates-api` | Authoring Templates API Reference | `module-table` | `sdk` | `authoring` | `paradev.sdk.templates.api-table.v1` | 18 | `get_templates_api_table` | `get_templates_api_selection` | `render_templates_api_reference_markdown` | `templates-api` | `templates-api --markdown` | `feature_index`, `kind_index`, `module_index` | `sdk`, `cli`, `frontend`, `docs` | `docs/user-manual/templates-api-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `copy-roots-api` | Copy Roots API Reference | `module-table` | `sdk` | `copy-roots` | `paradev.sdk.copy_roots.api-table.v1` | 12 | `get_copy_roots_api_table` | `get_copy_roots_api_selection` | `render_copy_roots_api_reference_markdown` | `copy-roots-api` | `copy-roots-api --markdown` | `feature_index`, `kind_index`, `module_index` | `sdk`, `cli`, `docs` | `docs/user-manual/copy-roots-api-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `project-facade-api` | Project Facade API Reference | `facade-table` | `project` | `project-facade` | `paradev.project.facade-api-table.v1` | 8 | `get_project_facade_api_table` | `get_project_facade_api_selection` | `render_project_facade_api_reference_markdown` | `project-facade-api` | `project-facade-api --markdown` | `feature_index`, `kind_index`, `module_index` | `sdk`, `cli`, `docs` | `docs/user-manual/project-facade-api-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `localization-api` | Localization API Reference | `facade-table` | `localization` | `localization` | `paradev.localization.api-table.v1` | 8 | `get_localization_api_table` | `get_localization_api_selection` | `render_localization_api_reference_markdown` | `localization-api` | `localization-api --markdown` | `feature_index`, `kind_index`, `module_index` | `sdk`, `cli`, `docs` | `docs/user-manual/localization-api-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `build-api` | Build API Reference | `facade-table` | `build` | `compiler` | `paradev.build.api-table.v1` | 133 | `get_build_api_table` | `get_build_api_selection` | `render_build_api_reference_markdown` | `build-api` | `build-api --markdown` | `feature_index`, `kind_index`, `module_index` | `sdk`, `cli`, `docs` | `docs/user-manual/build-api-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `frontend-api` | Frontend API Reference | `operation-contract` | `sdk` | `frontend` | `paradev.sdk.frontend-api.v1` | 98 | `get_frontend_api_contract` | `get_frontend_api_selection` | `render_frontend_api_reference_markdown` | `frontend-api` | `frontend-api --markdown` | `index.action`, `index.binding`, `index.group`, `index.id`, `index.mode`, `index.payload`, `index.status`, `index.surface`, `index.workspace_section` | `sdk`, `cli`, `rest`, `mcp`, `lsp`, `frontend`, `typescript`, `docs` | `docs/user-manual/frontend-api-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `sdk-cli-reference` | SDK And CLI API Reference | `operation-matrix` | `sdk` | `sdk-cli` | `paradev.sdk.frontend-api.v1` | 98 | `get_frontend_api_contract` | `get_frontend_api_selection` | `render_frontend_api_sdk_cli_markdown` | `frontend-api` | `frontend-api --sdk-cli-markdown` | `index.action`, `index.binding`, `index.group`, `index.id`, `index.mode`, `index.payload`, `index.status`, `index.surface`, `index.workspace_section` | `sdk`, `cli`, `docs` | `docs/user-manual/sdk-cli-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `project-inspection-reference` | Project Inspection Reference | `inspection-contract` | `sdk` | `inspections` | `paradev.sdk.inspections.v1` | 19 | `get_project_inspection_contract` | `get_project_inspection_selection` | `render_project_inspection_reference_markdown` | `inspections` | `inspections --markdown` | `index.filter`, `index.kind` | `sdk`, `cli`, `rest`, `mcp`, `frontend`, `docs` | `docs/user-manual/project-inspection-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `architecture-api` | Architecture API Reference | `api-table` | `sdk` | `architecture` | `paradev.sdk.architecture-api-table.v1` | 17 | `get_architecture_api_table` | `get_architecture_api_selection` | `render_architecture_api_reference_markdown` | `architecture --api-table` | `architecture --api-table-markdown` | `surface_index` | `sdk`, `cli`, `rest`, `mcp`, `docs` | `docs/user-manual/architecture-api-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `pdx-api` | PDX API Reference | `api-table` | `sdk` | `pdx` | `paradev.sdk.pdx-api-table.v1` | 22 | `get_pdx_api_table` | `get_pdx_api_selection` | `render_pdx_api_reference_markdown` | `pdx-api` | `pdx-api --markdown` | `feature_index`, `surface_index` | `sdk`, `cli`, `rest`, `mcp`, `docs` | `docs/user-manual/pdx-api-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `pdx-core-api` | PDX Core API Reference | `facade-table` | `pdx` | `pdx-core` | `paradev.pdx.core-api-table.v1` | 23 | `get_pdx_core_api_table` | `get_pdx_core_api_selection` | `render_pdx_core_api_reference_markdown` | `pdx-core-api` | `pdx-core-api --markdown` | `feature_index`, `kind_index`, `module_index` | `sdk`, `cli`, `docs` | `docs/user-manual/pdx-core-api-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `lsp-api` | LSP API Reference | `api-table` | `sdk` | `lsp` | `paradev.sdk.lsp-api-table.v1` | 42 | `get_lsp_api_table` | `get_lsp_api_selection` | `render_lsp_api_reference_markdown` | `lsp-api` | `lsp-api --markdown` | `feature_index`, `surface_index` | `sdk`, `cli`, `rest`, `mcp`, `lsp`, `docs` | `docs/user-manual/lsp-api-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `lsp-server-api` | LSP Server API Reference | `facade-table` | `lsp` | `lsp-server` | `paradev.lsp.server-api-table.v1` | 11 | `get_lsp_server_api_table` | `get_lsp_server_api_selection` | `render_lsp_server_api_reference_markdown` | `lsp-server-api` | `lsp-server-api --markdown` | `feature_index`, `kind_index`, `module_index` | `sdk`, `cli`, `lsp`, `docs` | `docs/user-manual/lsp-server-api-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `catalog-api` | Catalog API Reference | `api-table` | `hb` | `catalog` | `paradev.hb.catalog-api-table.v1` | 37 | `get_catalog_api_table` | `get_catalog_api_selection` | `render_catalog_api_reference_markdown` | `catalog-api` | `catalog-api --markdown` | `feature_index`, `surface_index` | `sdk`, `cli`, `rest`, `mcp`, `lsp`, `docs` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `hb-api` | HeavenBase Facade API Reference | `facade-table` | `hb` | `facade` | `paradev.hb.api-table.v1` | 27 | `get_hb_api_table` | `get_hb_api_selection` | `render_hb_api_reference_markdown` | `hb-api` | `hb-api --markdown` | `feature_index`, `kind_index`, `module_index` | `sdk`, `cli`, `docs` | `docs/user-manual/hb-api-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `rest-api` | REST API Reference | `route-table` | `rest` | `rest` | `paradev.rest.api-table.v1` | 84 | `get_rest_api_table` | `get_rest_api_selection` | `render_rest_api_reference_markdown` | `rest-api` | `rest-api --markdown` | `feature_index`, `frontend_operation_index`, `method_index` | `rest`, `cli`, `frontend`, `docs` | `docs/user-manual/rest-api-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `rest-facade-api` | REST Facade API Reference | `facade-table` | `rest` | `rest-facade` | `paradev.rest.facade-api-table.v1` | 13 | `get_rest_facade_api_table` | `get_rest_facade_api_selection` | `render_rest_facade_api_reference_markdown` | `rest-facade-api` | `rest-facade-api --markdown` | `feature_index`, `kind_index`, `module_index` | `sdk`, `cli`, `rest`, `docs` | `docs/user-manual/rest-facade-api-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `mcp-api` | MCP API Reference | `tool-table` | `mcp` | `mcp` | `paradev.mcp.api-table.v1` | 51 | `get_mcp_api_table` | `get_mcp_api_selection` | `render_mcp_api_reference_markdown` | `mcp-api` | `mcp-api --markdown` | `feature_index`, `frontend_operation_index`, `mode_index` | `mcp`, `cli`, `frontend`, `docs` | `docs/user-manual/mcp-api-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `cli-api` | CLI API Reference | `command-table` | `cli` | `cli` | `paradev.cli.api-table.v1` | 208 | `get_cli_api_table` | `get_cli_api_selection` | `render_cli_api_reference_markdown` | `cli-api` | `cli-api --markdown` | `adapter_index`, `feature_index`, `frontend_operation_index`, `kind_index` | `cli`, `rest`, `mcp`, `frontend`, `docs` | `docs/user-manual/cli-api-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
| `surface-contract-reference` | Surface Contract Reference | `surface-contract` | `surface` | `adapters` | `paradev.surface-contract-summary.v1` | 6 | `get_surface_contract_summary` | `get_surface_contract_selection` | `render_surface_contract_reference_markdown` | `architecture --surface-contracts` | `architecture --surface-contracts-markdown` | `status_index`, `index` | `cli`, `rest`, `mcp`, `lsp`, `vscode`, `bundle`, `docs` | `docs/user-manual/surface-contract-reference.md` | `tests/test_architecture.py::test_api_catalog_lists_generated_references` |
