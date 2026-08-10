"""VS Code extension contract."""

from __future__ import annotations

_VSCODE_LSP_SERVER_COMMAND = "paradev lsp serve --project <workspace-folder> --game-root <hoi4-root>"
_VSCODE_SURFACE_USES = ("lsp", "cli", "rest", "openapi")


def get_vscode_contract() -> dict[str, object]:
    """Return the VS Code extension contract."""

    return {
        "identifier": "vscode",
        "runtime": "typescript-vscode",
        "status": "scaffold",
        "path": "packages/vscode-paradev",
        "extension_entrypoint": "packages/vscode-paradev/src/extension.ts",
        "lsp_server_command": _VSCODE_LSP_SERVER_COMMAND,
        "activation_events": ["onLanguage:paradox-pdx"],
        "language_ids": ["paradox-pdx"],
        "lsp_transport": "stdio",
        "client_role": "thin LSP client over SDK-owned PDX semantics",
        "uses": list(_VSCODE_SURFACE_USES),
        "sdk_owned": True,
    }
