"""PDX LSP contract."""

from __future__ import annotations

from paradev.sdk import get_frontend_api_binding_index


def get_lsp_contract() -> dict[str, object]:
    """Return the LSP capability contract."""

    method_contracts = [
        {
            "method": "textDocument/publishDiagnostics",
            "capability": "diagnostics",
            "sdk_method": "diagnose_pdx_lsp_text",
            "payload": "paradev.lsp.diagnostics.v1",
            "status": "implemented",
        },
        {
            "method": "textDocument/documentSymbol",
            "capability": "document_symbols",
            "sdk_method": "document_symbols_pdx_lsp_text",
            "payload": "paradev.lsp.symbols.v1",
            "status": "implemented",
        },
        {
            "method": "textDocument/hover",
            "capability": "hover",
            "sdk_method": "hover_pdx_lsp_text",
            "payload": "paradev.lsp.hover.v1",
            "status": "implemented",
        },
        {
            "method": "textDocument/formatting",
            "capability": "formatting",
            "sdk_method": "format_pdx_lsp_text",
            "payload": "paradev.lsp.formatting.v1",
            "status": "implemented",
        },
        {
            "method": "textDocument/completion",
            "capability": "completion",
            "sdk_method": "complete_pdx_lsp_text",
            "payload": "paradev.lsp.completion.v1",
            "status": "implemented",
        },
        {
            "method": "textDocument/semanticTokens/full",
            "capability": "semantic_tokens",
            "sdk_method": "semantic_tokens_pdx_lsp_text",
            "payload": "paradev.lsp.semantic-tokens.v1",
            "status": "implemented",
        },
    ]
    return {
        "identifier": "lsp",
        "status": "implemented",
        "transport": "json-rpc",
        "server_command": "paradev lsp serve --project <project-root> --game-root <hoi4-root> --change-diagnostics-max-bytes 50000",
        "server_framework_target": "pygls-compatible",
        "frontend_clients": ["codemirror-adapter", "vscode-extension", "monaco-languageclient-target"],
        "backend_components": [
            "pdx parser",
            "AST traversal",
            "HeavenBase symbol catalog",
            "HOI4 keyword dataset",
            "diagnostics",
            "completion",
            "hover",
            "document symbols",
            "formatting",
            "semantic tokens",
        ],
        "side_channel": "FastAPI REST for non-LSP product actions",
        "capabilities": ["diagnostics", "document_symbols", "hover", "formatting", "completion", "semantic_tokens"],
        "method_contracts": method_contracts,
        "frontend_operation_ids": get_frontend_api_binding_index("lsp"),
        "sdk_owned": True,
    }
