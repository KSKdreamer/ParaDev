# Config API Reference

Generated from `paradev.config.get_config_api_table()`.

Regenerate this file whenever the public `paradev.config` facade changes:

```bash
rtk uv run paradev config-api --markdown > docs/user-manual/config-api-reference.md
```

## Summary / 汇总

- API rows / API 行数: 15
- Config modules / Config 模块数: 2
- Features / Feature 数: 4
- Row kinds / 行类型数: 5

## Module Index / 模块索引

| Module | Symbols | Public Exports |
| --- | --- | --- |
| `config` | 9 | `DEFAULT_CONFIG`, `BOOTSTRAP_CONFIG`, `CM_PARADEV`, `config_get`, `config_list`, `config_set`, `config_unset`, `config_scopes`, `config_history` |
| `config_api` | 6 | `CONFIG_API_TABLE_SCHEMA`, `ConfigApiRow`, `ConfigApiTable`, `get_config_api_selection`, `get_config_api_table`, `render_config_api_reference_markdown` |

## Feature Index / Feature 索引

| Feature | Symbols | Public Exports |
| --- | --- | --- |
| `defaults` | 2 | `DEFAULT_CONFIG`, `BOOTSTRAP_CONFIG` |
| `config-manager` | 1 | `CM_PARADEV` |
| `config` | 6 | `config_get`, `config_list`, `config_set`, `config_unset`, `config_scopes`, `config_history` |
| `config-api` | 6 | `CONFIG_API_TABLE_SCHEMA`, `ConfigApiRow`, `ConfigApiTable`, `get_config_api_selection`, `get_config_api_table`, `render_config_api_reference_markdown` |

## Kind Index / 行类型索引

| Kind | Symbols | Public Exports |
| --- | --- | --- |
| `dict constant` | 2 | `DEFAULT_CONFIG`, `BOOTSTRAP_CONFIG` |
| `ConfigManager` | 1 | `CM_PARADEV` |
| `function` | 9 | `config_get`, `config_list`, `config_set`, `config_unset`, `config_scopes`, `config_history`, `get_config_api_selection`, `get_config_api_table`, `render_config_api_reference_markdown` |
| `schema constant` | 1 | `CONFIG_API_TABLE_SCHEMA` |
| `TypedDict` | 2 | `ConfigApiRow`, `ConfigApiTable` |

## API Standard Table / API 标准表

| Symbol | Kind | Layer | Module | Feature | Import Path | Returns | Value | Registry Seam | Surface | Doc Page | Test Anchor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `DEFAULT_CONFIG` | `dict constant` | `config` | `config` | `defaults` | `paradev.config.DEFAULT_CONFIG` | `dict[1]` |  | `HeavenBase ConfigManager defaults` | `sdk` | `docs/user-manual/config-api-reference.md` | `tests/test_architecture.py::test_config_api_table_lists_public_config_facade` |
| `BOOTSTRAP_CONFIG` | `dict constant` | `config` | `config` | `defaults` | `paradev.config.BOOTSTRAP_CONFIG` | `dict[5]` |  | `HeavenBase ConfigManager defaults` | `sdk` | `docs/user-manual/config-api-reference.md` | `tests/test_architecture.py::test_config_api_table_lists_public_config_facade` |
| `CM_PARADEV` | `ConfigManager` | `config` | `config` | `config-manager` | `paradev.config.CM_PARADEV` | `ConfigManager` |  | `HeavenBase ConfigManager` | `sdk` | `docs/user-manual/config-api-reference.md` | `tests/test_architecture.py::test_config_api_table_lists_public_config_facade` |
| `config_get` | `function` | `config` | `config` | `config` | `paradev.config.config_get` | `object` |  | `HeavenBase ConfigManager` | `sdk` | `docs/user-manual/config-api-reference.md` | `tests/test_architecture.py::test_config_api_table_lists_public_config_facade` |
| `config_list` | `function` | `config` | `config` | `config` | `paradev.config.config_list` | `list[dict[str, object]]` |  | `HeavenBase ConfigManager` | `sdk` | `docs/user-manual/config-api-reference.md` | `tests/test_architecture.py::test_config_api_table_lists_public_config_facade` |
| `config_set` | `function` | `config` | `config` | `config` | `paradev.config.config_set` | `bool` |  | `HeavenBase ConfigManager` | `sdk` | `docs/user-manual/config-api-reference.md` | `tests/test_architecture.py::test_config_api_table_lists_public_config_facade` |
| `config_unset` | `function` | `config` | `config` | `config` | `paradev.config.config_unset` | `bool` |  | `HeavenBase ConfigManager` | `sdk` | `docs/user-manual/config-api-reference.md` | `tests/test_architecture.py::test_config_api_table_lists_public_config_facade` |
| `config_scopes` | `function` | `config` | `config` | `config` | `paradev.config.config_scopes` | `object` |  | `HeavenBase ConfigManager` | `sdk` | `docs/user-manual/config-api-reference.md` | `tests/test_architecture.py::test_config_api_table_lists_public_config_facade` |
| `config_history` | `function` | `config` | `config` | `config` | `paradev.config.config_history` | `object` |  | `HeavenBase ConfigManager` | `sdk` | `docs/user-manual/config-api-reference.md` | `tests/test_architecture.py::test_config_api_table_lists_public_config_facade` |
| `CONFIG_API_TABLE_SCHEMA` | `schema constant` | `config` | `config_api` | `config-api` | `paradev.config.CONFIG_API_TABLE_SCHEMA` | `paradev.config.api-table.v1` | `paradev.config.api-table.v1` | `config facade API table` | `sdk` | `docs/user-manual/config-api-reference.md` | `tests/test_architecture.py::test_config_api_table_lists_public_config_facade` |
| `ConfigApiRow` | `TypedDict` | `config` | `config_api` | `config-api` | `paradev.config.ConfigApiRow` | `TypedDict schema` |  | `config facade API table` | `sdk` | `docs/user-manual/config-api-reference.md` | `tests/test_architecture.py::test_config_api_table_lists_public_config_facade` |
| `ConfigApiTable` | `TypedDict` | `config` | `config_api` | `config-api` | `paradev.config.ConfigApiTable` | `TypedDict schema` |  | `config facade API table` | `sdk` | `docs/user-manual/config-api-reference.md` | `tests/test_architecture.py::test_config_api_table_lists_public_config_facade` |
| `get_config_api_selection` | `function` | `config` | `config_api` | `config-api` | `paradev.config.get_config_api_selection` | `ConfigApiTable \| ConfigApiRow \| list[str]` |  | `config facade API table` | `sdk` | `docs/user-manual/config-api-reference.md` | `tests/test_architecture.py::test_config_api_table_lists_public_config_facade` |
| `get_config_api_table` | `function` | `config` | `config_api` | `config-api` | `paradev.config.get_config_api_table` | `ConfigApiTable` |  | `config facade API table` | `sdk` | `docs/user-manual/config-api-reference.md` | `tests/test_architecture.py::test_config_api_table_lists_public_config_facade` |
| `render_config_api_reference_markdown` | `function` | `config` | `config_api` | `config-api` | `paradev.config.render_config_api_reference_markdown` | `str` |  | `config facade API table` | `sdk` | `docs/user-manual/config-api-reference.md` | `tests/test_architecture.py::test_config_api_table_lists_public_config_facade` |
