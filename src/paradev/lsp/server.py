"""Stdio JSON-RPC server for the ParaDev PDX language service."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO
from urllib.parse import unquote, urlparse

from heavenbase.utils import dumps_json, loads_json

from paradev.sdk import (
    Project,
    complete_pdx_lsp_text,
    diagnose_pdx_lsp_text,
    document_symbols_pdx_lsp_text,
    format_pdx_lsp_text,
    hover_pdx_lsp_text,
    semantic_tokens_pdx_lsp_text,
)
from paradev.version import __version__

_JSONRPC_VERSION = "2.0"
_TEXT_DOCUMENT_SYNC_FULL = 1
_ERROR_METHOD_NOT_FOUND = -32601
_ERROR_INVALID_PARAMS = -32602
_ERROR_INTERNAL = -32603
_DEFAULT_CHANGE_DIAGNOSTICS_MAX_BYTES = 50_000


@dataclass(slots=True)
class PdxDocument:
    """One open editor document."""

    uri: str
    text: str
    path: str | None = None


class PdxLanguageServer:
    """Small JSON-RPC dispatcher for PDX LSP requests."""

    def __init__(
        self,
        *,
        project_path: str | Path | None = None,
        database: str | Path | None = None,
        game_root: str | Path | None = None,
        completion_limit: int | None = 100,
        change_diagnostics_max_bytes: int | None = _DEFAULT_CHANGE_DIAGNOSTICS_MAX_BYTES,
    ) -> None:
        self._project_path = _optional_path(project_path)
        self._database = _optional_path(database)
        self._game_root = _optional_path(game_root)
        self._completion_limit = completion_limit
        self._change_diagnostics_max_bytes = change_diagnostics_max_bytes
        self._documents: dict[str, PdxDocument] = {}
        self._project: Project | None = None
        self.shutdown_requested = False
        self.exited = False

    def handle_message(self, message: Mapping[str, object]) -> list[dict[str, object]]:
        """Handle one JSON-RPC message and return outbound messages."""

        method = message.get("method")
        request_id = message.get("id")
        has_request_id = "id" in message
        if not isinstance(method, str):
            return [_error_response(request_id, _ERROR_INVALID_PARAMS, "JSON-RPC message must include a string method.")] if has_request_id else []
        params = _params(message.get("params"))
        try:
            if has_request_id:
                result = self._handle_request(method, params)
                return [_response(request_id, result)]
            return self._handle_notification(method, params)
        except ValueError as error:
            return [_error_response(request_id, _ERROR_INVALID_PARAMS, str(error))] if has_request_id else []
        except Exception as error:  # pragma: no cover - defensive LSP boundary
            return [_error_response(request_id, _ERROR_INTERNAL, str(error))] if has_request_id else []

    def _handle_request(self, method: str, params: Mapping[str, object]) -> object:
        if method == "initialize":
            self._configure_workspace(params)
            return _initialize_result()
        if method == "shutdown":
            self.shutdown_requested = True
            return None
        if method == "textDocument/documentSymbol":
            text, uri, path = self._document_args(params)
            payload = document_symbols_pdx_lsp_text(text, uri=uri, path=path)
            return payload["symbols"]
        if method == "textDocument/hover":
            text, uri, path = self._document_args(params)
            line, character = _position(params)
            payload = hover_pdx_lsp_text(text, line, character, uri=uri, path=path)
            return payload["hover"]
        if method == "textDocument/formatting":
            text, uri, path = self._document_args(params)
            payload = format_pdx_lsp_text(text, uri=uri, path=path)
            return payload["edits"]
        if method == "textDocument/completion":
            return self._completion_result(params)
        if method == "textDocument/semanticTokens/full":
            text, uri, path = self._document_args(params)
            payload = semantic_tokens_pdx_lsp_text(text, uri=uri, path=path)
            return {"data": payload["data"]}
        if method == "paradev/completionPayload":
            return self._completion_payload(params)
        if method == "paradev/semanticTokensPayload":
            text, uri, path = _text_payload_args(params)
            return semantic_tokens_pdx_lsp_text(text, uri=uri, path=path)
        if method == "completionItem/resolve":
            return dict(params)
        raise ValueError(f"Unsupported PDX LSP method: {method}")

    def _handle_notification(self, method: str, params: Mapping[str, object]) -> list[dict[str, object]]:
        if method == "initialized":
            return []
        if method == "exit":
            self.exited = True
            return []
        if method == "textDocument/didOpen":
            document = _opened_document(params)
            self._documents[document.uri] = document
            return [self._diagnostics_notification(document)]
        if method == "textDocument/didChange":
            document = self._changed_document(params)
            return [self._diagnostics_notification(document)] if document is not None and self._should_diagnose_change(document) else []
        if method == "textDocument/didSave":
            document = self._params_document(params)
            return [self._diagnostics_notification(document)] if document is not None else []
        if method == "textDocument/didClose":
            uri = _text_document_uri(params)
            if uri:
                self._documents.pop(uri, None)
                return [_publish_diagnostics(uri, [])]
            return []
        if method.startswith("$/") or method.startswith("workspace/"):
            return []
        return []

    def _completion_result(self, params: Mapping[str, object]) -> dict[str, object]:
        text, uri, path = self._document_args(params)
        line, character = _position(params)
        try:
            payload = self._completion_payload_for(text=text, line=line, character=character, uri=uri, path=path)
        except FileNotFoundError:
            payload = complete_pdx_lsp_text(text, line, character, uri=uri, path=path, game_root=self._game_root, limit=self._completion_limit)
        return {"isIncomplete": payload["isIncomplete"], "items": payload["items"]}

    def _completion_payload(self, params: Mapping[str, object]) -> dict[str, object]:
        text, uri, path = _text_payload_args(params)
        line, character = _payload_position(params)
        offset = _payload_offset(params)
        try:
            return self._completion_payload_for(text=text, line=line, character=character, offset=offset, uri=uri, path=path)
        except FileNotFoundError:
            return complete_pdx_lsp_text(text, line, character, uri=uri, path=path, game_root=self._game_root, limit=self._completion_limit, offset=offset)

    def _completion_payload_for(
        self, *, text: str, line: int, character: int, offset: int | None = None, uri: str | None, path: str | None
    ) -> dict[str, object]:
        return complete_pdx_lsp_text(
            text,
            line,
            character,
            uri=uri,
            path=path,
            project=self._project_for_completion(),
            database=self._database,
            game_root=self._game_root,
            limit=self._completion_limit,
            offset=offset,
        )

    def _document_args(self, params: Mapping[str, object]) -> tuple[str, str | None, str | None]:
        document = self._params_document(params)
        if document is None:
            raise ValueError("LSP request references an unopened text document.")
        return document.text, document.uri, document.path

    def _params_document(self, params: Mapping[str, object]) -> PdxDocument | None:
        uri = _text_document_uri(params)
        if not uri:
            return None
        document = self._documents.get(uri)
        if document is not None:
            return document
        return PdxDocument(uri=uri, text="", path=_path_from_uri(uri))

    def _changed_document(self, params: Mapping[str, object]) -> PdxDocument | None:
        uri = _text_document_uri(params)
        if not uri:
            return None
        previous = self._documents.get(uri)
        text = previous.text if previous is not None else ""
        content_changes = params.get("contentChanges")
        if isinstance(content_changes, list):
            for change in content_changes:
                if isinstance(change, Mapping) and isinstance(change.get("text"), str):
                    text = str(change["text"])
        document = PdxDocument(uri=uri, text=text, path=previous.path if previous is not None else _path_from_uri(uri))
        self._documents[uri] = document
        return document

    def _diagnostics_notification(self, document: PdxDocument) -> dict[str, object]:
        payload = diagnose_pdx_lsp_text(document.text, uri=document.uri, path=document.path)
        return _publish_diagnostics(document.uri, payload["diagnostics"])

    def _should_diagnose_change(self, document: PdxDocument) -> bool:
        limit = self._change_diagnostics_max_bytes
        return limit is None or len(document.text) <= limit

    def _configure_workspace(self, params: Mapping[str, object]) -> None:
        options = params.get("initializationOptions")
        if isinstance(options, Mapping):
            if self._project_path is None and isinstance(options.get("projectPath"), str):
                self._project_path = _optional_path(str(options["projectPath"]))
            if self._database is None and isinstance(options.get("database"), str):
                self._database = _optional_path(str(options["database"]))
            if self._game_root is None and isinstance(options.get("gameRoot"), str):
                self._game_root = _optional_path(str(options["gameRoot"]))
            limit = options.get("completionLimit")
            if type(limit) is int and limit > 0:
                self._completion_limit = limit
            max_bytes = options.get("changeDiagnosticsMaxBytes")
            if type(max_bytes) is int and max_bytes >= 0:
                self._change_diagnostics_max_bytes = max_bytes
        if self._project_path is None:
            workspace_path = _workspace_project_path(params)
            if workspace_path is not None:
                self._project_path = workspace_path

    def _project_for_completion(self) -> Project | None:
        if self._project is not None:
            return self._project
        if self._project_path is None:
            return None
        try:
            self._project = Project.load(self._project_path)
        except Exception:
            return None
        return self._project


def serve_pdx_lsp_stdio(
    *,
    project_path: str | Path | None = None,
    database: str | Path | None = None,
    game_root: str | Path | None = None,
    completion_limit: int | None = 100,
    change_diagnostics_max_bytes: int | None = _DEFAULT_CHANGE_DIAGNOSTICS_MAX_BYTES,
    input_stream: BinaryIO | None = None,
    output_stream: BinaryIO | None = None,
) -> None:
    """Run the PDX language server over LSP stdio framing."""

    import sys

    server = PdxLanguageServer(
        project_path=project_path,
        database=database,
        game_root=game_root,
        completion_limit=completion_limit,
        change_diagnostics_max_bytes=change_diagnostics_max_bytes,
    )
    source = input_stream or sys.stdin.buffer
    sink = output_stream or sys.stdout.buffer
    while not server.exited:
        message = read_lsp_message(source)
        if message is None:
            break
        for outgoing in server.handle_message(message):
            write_lsp_message(sink, outgoing)


def read_lsp_message(source: BinaryIO) -> dict[str, object] | None:
    """Read one LSP framed JSON-RPC message."""

    content_length: int | None = None
    while True:
        line = source.readline()
        if line == b"":
            return None
        if line in {b"\r\n", b"\n"}:
            break
        name, _separator, value = line.decode("ascii").partition(":")
        if name.lower() == "content-length":
            content_length = int(value.strip())
    if content_length is None:
        raise ValueError("LSP message is missing Content-Length.")
    body = source.read(content_length)
    payload = loads_json(body.decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("LSP message body must be a JSON object.")
    return {str(key): value for key, value in payload.items()}


def write_lsp_message(sink: BinaryIO, message: Mapping[str, object]) -> None:
    """Write one LSP framed JSON-RPC message."""

    body = dumps_json(dict(message), compact=True).encode("utf-8")
    sink.write(f"Content-Length: {len(body)}\r\n\r\n".encode("ascii"))
    sink.write(body)
    sink.flush()


def _optional_path(value: str | Path | None) -> Path | None:
    if value is None:
        return None
    text = str(value).strip()
    return Path(text).expanduser() if text else None


def _initialize_result() -> dict[str, object]:
    legend = semantic_tokens_pdx_lsp_text("")["legend"]
    return {
        "serverInfo": {"name": "ParaDev PDX LSP", "version": __version__},
        "capabilities": {
            "textDocumentSync": {"openClose": True, "change": _TEXT_DOCUMENT_SYNC_FULL},
            "completionProvider": {"resolveProvider": True, "triggerCharacters": ["_", ":", "@"]},
            "documentSymbolProvider": True,
            "hoverProvider": True,
            "documentFormattingProvider": True,
            "semanticTokensProvider": {"legend": legend, "full": True, "range": False},
        },
    }


def _opened_document(params: Mapping[str, object]) -> PdxDocument:
    text_document = params.get("textDocument")
    if not isinstance(text_document, Mapping):
        raise ValueError("textDocument/didOpen requires textDocument.")
    uri = text_document.get("uri")
    text = text_document.get("text")
    if not isinstance(uri, str) or not isinstance(text, str):
        raise ValueError("textDocument/didOpen requires string uri and text.")
    return PdxDocument(uri=uri, text=text, path=_path_from_uri(uri))


def _position(params: Mapping[str, object]) -> tuple[int, int]:
    position = params.get("position")
    if not isinstance(position, Mapping):
        raise ValueError("LSP request requires position.")
    line = position.get("line")
    character = position.get("character")
    if type(line) is not int or type(character) is not int:
        raise ValueError("LSP position line and character must be integers.")
    return line, character


def _payload_position(params: Mapping[str, object]) -> tuple[int, int]:
    line = params.get("line")
    character = params.get("character")
    if type(line) is not int or type(character) is not int:
        raise ValueError("ParaDev LSP payload request line and character must be integers.")
    return line, character


def _payload_offset(params: Mapping[str, object]) -> int | None:
    offset = params.get("offset")
    if offset is None:
        return None
    if type(offset) is not int:
        raise ValueError("ParaDev LSP payload request offset must be an integer when provided.")
    return offset


def _params(value: object) -> Mapping[str, object]:
    return value if isinstance(value, Mapping) else {}


def _text_payload_args(params: Mapping[str, object]) -> tuple[str, str | None, str | None]:
    text = params.get("text")
    if not isinstance(text, str):
        raise ValueError("ParaDev LSP payload request requires string text.")
    uri = params.get("uri")
    path = params.get("path")
    if uri is not None and not isinstance(uri, str):
        raise ValueError("ParaDev LSP payload request uri must be a string.")
    if path is not None and not isinstance(path, str):
        raise ValueError("ParaDev LSP payload request path must be a string.")
    return text, uri, path


def _text_document_uri(params: Mapping[str, object]) -> str | None:
    text_document = params.get("textDocument")
    if not isinstance(text_document, Mapping):
        return None
    uri = text_document.get("uri")
    return uri if isinstance(uri, str) and uri else None


def _path_from_uri(uri: str) -> str | None:
    parsed = urlparse(uri)
    if parsed.scheme != "file":
        return None
    return unquote(parsed.path)


def _workspace_project_path(params: Mapping[str, object]) -> Path | None:
    root_uri = params.get("rootUri")
    if isinstance(root_uri, str):
        path = _path_from_uri(root_uri)
        if path:
            return Path(path)
    root_path = params.get("rootPath")
    if isinstance(root_path, str) and root_path:
        return Path(root_path).expanduser()
    workspace_folders = params.get("workspaceFolders")
    if isinstance(workspace_folders, list):
        for folder in workspace_folders:
            if isinstance(folder, Mapping) and isinstance(folder.get("uri"), str):
                path = _path_from_uri(str(folder["uri"]))
                if path:
                    return Path(path)
    return None


def _publish_diagnostics(uri: str, diagnostics: object) -> dict[str, object]:
    rows = diagnostics if isinstance(diagnostics, list) else []
    return {"jsonrpc": _JSONRPC_VERSION, "method": "textDocument/publishDiagnostics", "params": {"uri": uri, "diagnostics": rows}}


def _response(request_id: object, result: object) -> dict[str, object]:
    return {"jsonrpc": _JSONRPC_VERSION, "id": request_id, "result": result}


def _error_response(request_id: object, code: int, message: str) -> dict[str, object]:
    return {"jsonrpc": _JSONRPC_VERSION, "id": request_id, "error": {"code": code, "message": message}}


__all__ = [
    "PdxDocument",
    "PdxLanguageServer",
    "read_lsp_message",
    "serve_pdx_lsp_stdio",
    "write_lsp_message",
]
