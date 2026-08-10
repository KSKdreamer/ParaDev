# Authoring Templates API Reference

Generated from `paradev.sdk.templates.get_templates_api_table()`.

Regenerate this file whenever SDK authoring-template helpers change:

```bash
rtk uv run paradev templates-api --markdown > docs/user-manual/templates-api-reference.md
```

## Summary / 汇总

- API rows / API 行数: 18
- Template modules / Template 模块数: 1
- Features / Feature 数: 6
- Row kinds / 行类型数: 5

## Module Index / 模块索引

| Module | Symbols | Public Exports |
| --- | --- | --- |
| `sdk.templates` | 18 | `TEMPLATES_SCHEMA`, `MODULE_SCAFFOLD_SCHEMA`, `COLLECTION_SCAFFOLD_SCHEMA`, `ProjectTemplateSpecError`, `TemplateArg`, `TemplateFile`, `ModuleTemplate`, `builtin_module_templates`, `project_module_templates`, `template_index`, `module_scaffold_plan`, `collection_scaffold_plan`, `TEMPLATES_API_TABLE_SCHEMA`, `TemplatesApiRow`, `TemplatesApiTable`, `get_templates_api_selection`, `get_templates_api_table`, `render_templates_api_reference_markdown` |

## Feature Index / Feature 索引

| Feature | Symbols | Public Exports |
| --- | --- | --- |
| `schemas` | 3 | `TEMPLATES_SCHEMA`, `MODULE_SCAFFOLD_SCHEMA`, `COLLECTION_SCAFFOLD_SCHEMA` |
| `errors` | 1 | `ProjectTemplateSpecError` |
| `models` | 3 | `TemplateArg`, `TemplateFile`, `ModuleTemplate` |
| `registry` | 3 | `builtin_module_templates`, `project_module_templates`, `template_index` |
| `scaffold` | 2 | `module_scaffold_plan`, `collection_scaffold_plan` |
| `templates-api` | 6 | `TEMPLATES_API_TABLE_SCHEMA`, `TemplatesApiRow`, `TemplatesApiTable`, `get_templates_api_selection`, `get_templates_api_table`, `render_templates_api_reference_markdown` |

## Kind Index / 行类型索引

| Kind | Symbols | Public Exports |
| --- | --- | --- |
| `schema constant` | 4 | `TEMPLATES_SCHEMA`, `MODULE_SCAFFOLD_SCHEMA`, `COLLECTION_SCAFFOLD_SCHEMA`, `TEMPLATES_API_TABLE_SCHEMA` |
| `exception` | 1 | `ProjectTemplateSpecError` |
| `dataclass` | 3 | `TemplateArg`, `TemplateFile`, `ModuleTemplate` |
| `function` | 8 | `builtin_module_templates`, `project_module_templates`, `template_index`, `module_scaffold_plan`, `collection_scaffold_plan`, `get_templates_api_selection`, `get_templates_api_table`, `render_templates_api_reference_markdown` |
| `TypedDict` | 2 | `TemplatesApiRow`, `TemplatesApiTable` |

## API Standard Table / API 标准表

| Symbol | Kind | Layer | Module | Feature | Import Path | Returns | Value | Registry Seam | Surface | Doc Page | Test Anchor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `TEMPLATES_SCHEMA` | `schema constant` | `sdk` | `sdk.templates` | `schemas` | `paradev.sdk.templates.TEMPLATES_SCHEMA` | `paradev.sdk.templates.v1` | paradev.sdk.templates.v1 | `authoring template payload schemas` | `sdk` | `docs/user-manual/templates-api-reference.md` | `tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract` |
| `MODULE_SCAFFOLD_SCHEMA` | `schema constant` | `sdk` | `sdk.templates` | `schemas` | `paradev.sdk.templates.MODULE_SCAFFOLD_SCHEMA` | `paradev.sdk.module_scaffold.v1` | paradev.sdk.module_scaffold.v1 | `authoring template payload schemas` | `sdk` | `docs/user-manual/templates-api-reference.md` | `tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract` |
| `COLLECTION_SCAFFOLD_SCHEMA` | `schema constant` | `sdk` | `sdk.templates` | `schemas` | `paradev.sdk.templates.COLLECTION_SCAFFOLD_SCHEMA` | `paradev.sdk.collection_scaffold.v1` | paradev.sdk.collection_scaffold.v1 | `authoring template payload schemas` | `sdk` | `docs/user-manual/templates-api-reference.md` | `tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract` |
| `ProjectTemplateSpecError` | `exception` | `sdk` | `sdk.templates` | `errors` | `paradev.sdk.templates.ProjectTemplateSpecError` | `ProjectTemplateSpecError exception` |  | `authoring template validation` | `sdk` | `docs/user-manual/templates-api-reference.md` | `tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract` |
| `TemplateArg` | `dataclass` | `sdk` | `sdk.templates` | `models` | `paradev.sdk.templates.TemplateArg` | `TemplateArg dataclass` |  | `authoring template model registry` | `sdk` | `docs/user-manual/templates-api-reference.md` | `tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract` |
| `TemplateFile` | `dataclass` | `sdk` | `sdk.templates` | `models` | `paradev.sdk.templates.TemplateFile` | `TemplateFile dataclass` |  | `authoring template model registry` | `sdk` | `docs/user-manual/templates-api-reference.md` | `tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract` |
| `ModuleTemplate` | `dataclass` | `sdk` | `sdk.templates` | `models` | `paradev.sdk.templates.ModuleTemplate` | `ModuleTemplate dataclass` |  | `authoring template model registry` | `sdk` | `docs/user-manual/templates-api-reference.md` | `tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract` |
| `builtin_module_templates` | `function` | `sdk` | `sdk.templates` | `registry` | `paradev.sdk.templates.builtin_module_templates` | `tuple[ModuleTemplate, ...]` |  | `authoring template registry` | `sdk` | `docs/user-manual/templates-api-reference.md` | `tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract` |
| `project_module_templates` | `function` | `sdk` | `sdk.templates` | `registry` | `paradev.sdk.templates.project_module_templates` | `tuple[ModuleTemplate, ...]` |  | `authoring template registry` | `sdk` | `docs/user-manual/templates-api-reference.md` | `tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract` |
| `template_index` | `function` | `sdk` | `sdk.templates` | `registry` | `paradev.sdk.templates.template_index` | `dict[str, ModuleTemplate]` |  | `authoring template registry` | `sdk` | `docs/user-manual/templates-api-reference.md` | `tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract` |
| `module_scaffold_plan` | `function` | `sdk` | `sdk.templates` | `scaffold` | `paradev.sdk.templates.module_scaffold_plan` | `dict[str, object]` |  | `resource scaffold planner` | `sdk` | `docs/user-manual/templates-api-reference.md` | `tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract` |
| `collection_scaffold_plan` | `function` | `sdk` | `sdk.templates` | `scaffold` | `paradev.sdk.templates.collection_scaffold_plan` | `dict[str, object]` |  | `resource scaffold planner` | `sdk` | `docs/user-manual/templates-api-reference.md` | `tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract` |
| `TEMPLATES_API_TABLE_SCHEMA` | `schema constant` | `sdk` | `sdk.templates` | `templates-api` | `paradev.sdk.templates.TEMPLATES_API_TABLE_SCHEMA` | `paradev.sdk.templates.api-table.v1` | paradev.sdk.templates.api-table.v1 | `authoring templates API table` | `sdk` | `docs/user-manual/templates-api-reference.md` | `tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract` |
| `TemplatesApiRow` | `TypedDict` | `sdk` | `sdk.templates` | `templates-api` | `paradev.sdk.templates.TemplatesApiRow` | `TypedDict schema` |  | `authoring templates API table` | `sdk` | `docs/user-manual/templates-api-reference.md` | `tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract` |
| `TemplatesApiTable` | `TypedDict` | `sdk` | `sdk.templates` | `templates-api` | `paradev.sdk.templates.TemplatesApiTable` | `TypedDict schema` |  | `authoring templates API table` | `sdk` | `docs/user-manual/templates-api-reference.md` | `tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract` |
| `get_templates_api_selection` | `function` | `sdk` | `sdk.templates` | `templates-api` | `paradev.sdk.templates.get_templates_api_selection` | `TemplatesApiTable \| TemplatesApiRow \| list[str]` |  | `authoring templates API table` | `sdk` | `docs/user-manual/templates-api-reference.md` | `tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract` |
| `get_templates_api_table` | `function` | `sdk` | `sdk.templates` | `templates-api` | `paradev.sdk.templates.get_templates_api_table` | `TemplatesApiTable` |  | `authoring templates API table` | `sdk` | `docs/user-manual/templates-api-reference.md` | `tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract` |
| `render_templates_api_reference_markdown` | `function` | `sdk` | `sdk.templates` | `templates-api` | `paradev.sdk.templates.render_templates_api_reference_markdown` | `str` |  | `authoring templates API table` | `sdk` | `docs/user-manual/templates-api-reference.md` | `tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract` |
