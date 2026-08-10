# Surface Contract Reference

Generated from `paradev.surfaces.get_surface_contract_summary()`.

Regenerate this file whenever the static surface contract catalog changes:

```bash
rtk uv run paradev architecture --surface-contracts-markdown > docs/user-manual/surface-contract-reference.md
```

## Summary / 汇总

- Surfaces / Surface 数: 6
- SDK-owned / SDK 拥有: 6

## Index Catalog / Index 目录

| Index | Contract Path | Python Helper | Use |
| --- | --- | --- | --- |
| `identifier` | `summary["index"][identifier]` | `get_surface_contract_summary_row(identifier)` | Surface identifier to compact summary row. |
| `status` | `summary["status_index"][status]` | `get_surface_contract_status_ids(status)` | Contract status to ordered surface ids. |

## Status Index / Status 索引

| Status | Surfaces | Surface IDs |
| --- | --- | --- |
| `implemented` | 3 | `bundle`, `lsp`, `openapi` |
| `scaffold` | 3 | `cli`, `mcp`, `vscode` |

## Surface Contracts / Surface Contract 表

| Surface | Status | Runtime | SDK-owned | Top-Level Keys |
| --- | --- | --- | --- | --- |
| `bundle` | `implemented` | `python-wheel-loopback` | yes | `identifier`, `inputs`, `outputs`, `platform_priority`, `runtime`, `sdk_owned`, `security`, `status`, `tools` |
| `cli` | `scaffold` | `python-typer-rich` | yes | `adapters`, `commands`, `filters`, `frontend_operation_ids`, `identifier`, `inspection_contract`, `projections`, `runtime`, `sdk_owned`, `status` |
| `lsp` | `implemented` |  | yes | `backend_components`, `capabilities`, `frontend_clients`, `frontend_operation_ids`, `identifier`, `method_contracts`, `sdk_owned`, `server_command`, `server_framework_target`, `side_channel`, `status`, `transport` |
| `mcp` | `scaffold` | `heavenbase-mcp` | yes | `frontend_operation_ids`, `identifier`, `runtime`, `runtime_scope`, `runtime_status`, `runtime_tools`, `sdk_owned`, `server_command`, `status`, `stdio_server`, `tool_contracts`, `toolkit_factory`, `tools`, `transport` |
| `openapi` | `implemented` | `openapi-3.1.0` | yes | `info`, `openapi`, `paths` |
| `vscode` | `scaffold` | `typescript-vscode` | yes | `activation_events`, `client_role`, `extension_entrypoint`, `identifier`, `language_ids`, `lsp_server_command`, `lsp_transport`, `path`, `runtime`, `sdk_owned`, `status`, `uses` |
