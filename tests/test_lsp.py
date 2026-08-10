from __future__ import annotations

import json
import sqlite3
import time
from io import BytesIO
from pathlib import Path

import pytest
from heavenbase.utils import copy_dir

from paradev.config import CM_PARADEV
from paradev.hb import catalog_write
from paradev.lsp import PdxLanguageServer, read_lsp_message, serve_pdx_lsp_stdio, write_lsp_message
from paradev.sdk import (
    Project,
    complete_pdx_lsp_text,
    diagnose_pdx_lsp_text,
    document_symbols_pdx_lsp_text,
    format_pdx_lsp_text,
    hover_pdx_lsp_text,
    semantic_tokens_pdx_lsp_text,
)

PROJECT_ROOT = Path("demos/assets/projects/minimal").resolve()


def _write_lsp_keyword_documentation(game_root: Path, *, kind: str, keyword: str, scope: str = "country") -> None:
    documentation = game_root / "documentation"
    documentation.mkdir(parents=True, exist_ok=True)
    filenames = {
        "modifier": "modifiers_documentation.md",
        "effect": "effects_documentation.md",
        "trigger": "triggers_documentation.md",
    }
    headings = {
        "modifier": "Modifiers",
        "effect": "Effects",
        "trigger": "Triggers",
    }
    (documentation / filenames[kind]).write_text(
        f"# {headings[kind]}\n\n" f"## {headings[kind]} for scope {scope}\n\n" f"* [{keyword}](#{keyword})\n",
        encoding="utf-8",
    )


def test_lsp_diagnostics_convert_pdx_errors_to_zero_based_ranges() -> None:
    payload = diagnose_pdx_lsp_text("value = 0x", uri="file:///broken.pdx", path="broken.pdx")

    assert payload["schema"] == "paradev.lsp.diagnostics.v1"
    assert payload["method"] == "textDocument/publishDiagnostics"
    assert payload["ok"] is False
    assert payload["uri"] == "file:///broken.pdx"
    assert payload["file_ext"] == ".pdx"
    assert payload["diagnostics"] == [
        {
            "range": {"start": {"line": 0, "character": 8}, "end": {"line": 0, "character": 9}},
            "severity": 1,
            "code": "pdx.invalid_hex_number",
            "source": "paradev.pdx",
            "message": "PDX hexadecimal number requires at least one digit.",
        }
    ]


def test_lsp_formatting_returns_full_document_text_edit() -> None:
    payload = format_pdx_lsp_text("focus = { id = GER_test }", path="focus.pdx")

    assert payload["schema"] == "paradev.lsp.formatting.v1"
    assert payload["method"] == "textDocument/formatting"
    assert payload["ok"] is True
    assert payload["changed"] is True
    assert payload["diagnostics"] == []
    assert payload["edits"][0]["range"] == {"start": {"line": 0, "character": 0}, "end": {"line": 0, "character": 25}}
    assert payload["edits"][0]["newText"] == "focus = {\n\tid = GER_test\n}\n"


def test_lsp_symbols_and_hover_use_pdx_key_spans() -> None:
    text = "focus = {\n\tid = GER_test\n}\n"
    symbols = document_symbols_pdx_lsp_text(text, uri="file:///focus.pdx")
    hover = hover_pdx_lsp_text(text, 0, 2, uri="file:///focus.pdx")

    assert symbols["schema"] == "paradev.lsp.symbols.v1"
    assert symbols["symbols"][0]["name"] == "focus"
    assert symbols["symbols"][0]["children"][0]["name"] == "id"
    assert hover["schema"] == "paradev.lsp.hover.v1"
    assert hover["hover"]["range"] == {"start": {"line": 0, "character": 0}, "end": {"line": 0, "character": 5}}
    assert "`focus` = `{ ... }`" in hover["hover"]["contents"]["value"]
    json.dumps(symbols)
    json.dumps(hover)


def test_lsp_completion_reads_written_heavenbase_catalog(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    project = Project.load(project_root)
    catalog_write(project)
    database = project_root / ".paradev/.cache/hb/catalog.sqlite"
    with sqlite3.connect(database) as connection:
        connection.execute("drop index paradev_sys_catalog_browse")

    payload = complete_pdx_lsp_text("focus = {\n\tid = GER\n}\n", 1, 9, project=project, path="def.txt")

    assert payload["schema"] == "paradev.lsp.completion.v1"
    assert payload["method"] == "textDocument/completion"
    assert payload["ok"] is True
    assert payload["prefix"] == "GER"
    labels = [item["label"] for item in payload["items"]]
    assert "GER_sample" in labels
    assert "GER_sample_desc" in labels
    entity_item = next(item for item in payload["items"] if item["label"] == "GER_sample")
    assert entity_item["detail"] == "focus/GER_sample"
    assert entity_item["data"]["source"] == "hoi4-entity"
    json.dumps(payload)


def test_catalog_completion_reads_typed_pdx_symbol_fields(tmp_path: Path) -> None:
    from paradev import hb as hb_module

    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    project = Project.load(project_root)
    catalog_write(project)

    items = hb_module.catalog_completion_items(project, prefix="cost", limit=20)

    assert [item["label"] for item in items] == ["cost"]
    assert items[0]["detail"] == "focus/cost"
    assert items[0]["data"]["source"] == "pdx-symbol"


def test_catalog_completion_reuses_cached_database_rows(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from paradev import hb as hb_module

    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    project = Project.load(project_root)
    catalog_write(project)
    calls = 0
    original = hb_module._query_catalog_completion_items

    def counting_query_catalog_completion_items(database: Path, *, prefix: str, limit: int | None):
        nonlocal calls
        calls += 1
        return original(database, prefix=prefix, limit=limit)

    monkeypatch.setattr(hb_module, "_query_catalog_completion_items", counting_query_catalog_completion_items)

    first = hb_module.catalog_completion_items(project, prefix="GER", limit=20)
    first_data = first[0]["data"]
    assert isinstance(first_data, dict)
    first_data["source"] = "mutated"
    second = hb_module.catalog_completion_items(project, prefix="GER", limit=20)

    assert calls == 1
    assert "GER_sample" in [item["label"] for item in first]
    second_data = second[0]["data"]
    assert isinstance(second_data, dict)
    assert second_data["source"] != "mutated"


def test_catalog_completion_bounds_candidate_hydration(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from paradev import hb as hb_module

    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    project = Project.load(project_root)
    preview = hb_module.catalog_preview(project)
    preview["entities"]["loc-entry"].extend(
        {
            "key": f"GER_BULK_{index:04d}",
            "language": "l_english",
            "text": f"Bulk completion {index}",
            "module_id": "focus/GER_sample",
        }
        for index in range(120)
    )
    catalog_write(project, preview=preview)
    hydrated = 0
    original = hb_module._catalog_query_row

    def counting_catalog_query_row(*args: object, **kwargs: object) -> dict[str, object]:
        nonlocal hydrated
        hydrated += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(hb_module, "_catalog_query_row", counting_catalog_query_row)

    default_items = hb_module.catalog_completion_items(project, prefix="GER_BULK")

    assert len(default_items) == 100
    assert hydrated == 100

    hydrated = 0
    limited_items = hb_module.catalog_completion_items(project, prefix="GER_BULK", limit=20)

    assert len(limited_items) == 20
    assert hydrated == 20


def test_lsp_completion_uses_cursor_offset_for_large_documents() -> None:
    rows = [f"focus_{index} = {{\n\tid = GER_focus_{index}\n\tavailable = {{ always = yes }}\n}}\n" for index in range(10_000)]
    rows.append("focus_tail = {\n\tid = GER")
    text = "".join(rows)
    line = text.count("\n")
    character = len(text.rsplit("\n", 1)[-1])

    start = time.perf_counter()
    payload = complete_pdx_lsp_text(text, line, character, offset=len(text), path="def.txt", limit=20)
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert payload["prefix"] == "GER"
    assert elapsed_ms < 50


def test_lsp_completion_suggests_hoi4_modifiers_in_modifier_context(tmp_path: Path) -> None:
    documentation = tmp_path / "documentation"
    documentation.mkdir()
    (documentation / "modifiers_documentation.md").write_text(
        "# Modifiers\n\n" "## Modifiers for scope country\n\n" "* [stability_factor](#stability_factor)\n" "* [war_support_factor](#war_support_factor)\n",
        encoding="utf-8",
    )

    payload = complete_pdx_lsp_text("idea = {\n\tmodifier = {\n\t\tsta", 2, 5, game_root=tmp_path, path="common/ideas/sample.txt")

    labels = [item["label"] for item in payload["items"]]
    assert labels == ["stability_factor"]
    assert payload["items"][0]["data"]["source"] == "hoi4-keyword"
    assert payload["items"][0]["data"]["kind"] == "modifier"


def test_lsp_completion_uses_configured_game_root_when_omitted(tmp_path: Path, cm_paradev_lock) -> None:
    previous = CM_PARADEV.get("paradev.hoi4.game_root", default=None)
    game_root = tmp_path / "configured-game"
    _write_lsp_keyword_documentation(game_root, kind="modifier", keyword="cfg_modifier_factor")

    try:
        CM_PARADEV.set("paradev.hoi4.game_root", f"  {game_root}  ")

        payload = complete_pdx_lsp_text("idea = {\n\tmodifier = {\n\t\tcfg", 2, 5, path="common/ideas/sample.txt")

        assert "cfg_modifier_factor" in [item["label"] for item in payload["items"]]
    finally:
        if previous is None:
            CM_PARADEV.unset("paradev.hoi4.game_root")
        else:
            CM_PARADEV.set("paradev.hoi4.game_root", previous)


def test_lsp_completion_does_not_suggest_hoi4_modifiers_at_top_level(tmp_path: Path) -> None:
    documentation = tmp_path / "documentation"
    documentation.mkdir()
    (documentation / "modifiers_documentation.md").write_text(
        "# Modifiers\n\n" "## Modifiers for scope country\n\n" "* [stability_factor](#stability_factor)\n",
        encoding="utf-8",
    )

    payload = complete_pdx_lsp_text("sta", 0, 3, game_root=tmp_path)

    assert payload["items"] == []


def test_lsp_completion_suggests_hoi4_effects_in_effect_context(tmp_path: Path) -> None:
    documentation = tmp_path / "documentation"
    documentation.mkdir()
    (documentation / "effects_documentation.md").write_text(
        "# Effects\n\n" "## Effects for scope COUNTRY\n\n" "* [add_stability](#add_stability)\n" "* [add_war_support](#add_war_support)\n",
        encoding="utf-8",
    )

    payload = complete_pdx_lsp_text("country_event = {\n\toption = {\n\t\tadd_sta", 2, 9, game_root=tmp_path, path="events/sample.txt")

    labels = [item["label"] for item in payload["items"]]
    assert labels == ["add_stability"]
    assert payload["items"][0]["data"]["kind"] == "effect"


def test_lsp_completion_suggests_hoi4_triggers_in_trigger_context(tmp_path: Path) -> None:
    documentation = tmp_path / "documentation"
    documentation.mkdir()
    (documentation / "triggers_documentation.md").write_text(
        "# Triggers\n\n" "## Triggers for scope COUNTRY\n\n" "* [has_stability](#has_stability)\n" "* [has_war_support](#has_war_support)\n",
        encoding="utf-8",
    )

    payload = complete_pdx_lsp_text("focus = {\n\tavailable = {\n\t\thas_sta", 2, 9, game_root=tmp_path, path="common/national_focus/sample.txt")

    labels = [item["label"] for item in payload["items"]]
    assert labels == ["has_stability"]
    assert payload["items"][0]["data"]["kind"] == "trigger"


def test_lsp_completion_returns_modifier_dropdown_for_empty_prefix_in_modifier_context(tmp_path: Path) -> None:
    documentation = tmp_path / "documentation"
    documentation.mkdir()
    (documentation / "modifiers_documentation.md").write_text(
        "# Modifiers\n\n" "## Modifiers for scope country\n\n" "* [stability_factor](#stability_factor)\n" "* [war_support_factor](#war_support_factor)\n",
        encoding="utf-8",
    )

    payload = complete_pdx_lsp_text("idea = {\n\tmodifier = {\n\t\t", 2, 2, game_root=tmp_path, path="common/ideas/sample.txt")

    labels = [item["label"] for item in payload["items"]]
    assert "stability_factor" in labels
    assert "war_support_factor" in labels
    assert all(item["data"]["kind"] == "modifier" for item in payload["items"])


def test_lsp_semantic_tokens_mark_pdx_ranges_for_highlighting() -> None:
    payload = semantic_tokens_pdx_lsp_text("focus = {\n\tid = GER_test\n\tcost = 10\n}\n", path="focus.txt")

    assert payload["schema"] == "paradev.lsp.semantic-tokens.v1"
    assert payload["method"] == "textDocument/semanticTokens/full"
    assert payload["ok"] is True
    assert payload["legend"]["tokenTypes"] == ["property", "class", "enum", "string", "number", "variable"]
    assert payload["tokens"] == [
        {"line": 0, "character": 0, "length": 5, "token_type": "class", "token_modifiers": []},
        {"line": 1, "character": 1, "length": 2, "token_type": "property", "token_modifiers": []},
        {"line": 1, "character": 6, "length": 8, "token_type": "enum", "token_modifiers": []},
        {"line": 2, "character": 1, "length": 4, "token_type": "property", "token_modifiers": []},
        {"line": 2, "character": 8, "length": 2, "token_type": "number", "token_modifiers": []},
    ]
    assert payload["data"] == [0, 0, 5, 1, 0, 1, 1, 2, 0, 0, 0, 5, 8, 2, 0, 1, 1, 4, 0, 0, 0, 7, 2, 4, 0]
    json.dumps(payload)


def test_lsp_rest_routes_expose_completion_and_semantic_tokens(tmp_path: Path) -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces.rest import build_app

    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    catalog_write(Project.load(project_root))
    game_root = tmp_path / "game"
    documentation = game_root / "documentation"
    documentation.mkdir(parents=True)
    (documentation / "modifiers_documentation.md").write_text(
        "# Modifiers\n\n" "## Modifiers for scope country\n\n" "* [stability_factor](#stability_factor)\n",
        encoding="utf-8",
    )
    client = testclient.TestClient(build_app())

    completion = client.post(
        "/lsp/completion",
        json={
            "text": "focus = {\n\tid = GER\n}\n",
            "line": 1,
            "character": 9,
            "project_path": str(project_root),
        },
    )
    keyword_completion = client.post(
        "/lsp/completion",
        json={
            "text": "idea = {\n\tmodifier = {\n\t\tsta",
            "line": 2,
            "character": 5,
            "game_root": str(game_root),
            "path": "common/ideas/sample.txt",
        },
    )
    semantic = client.post("/lsp/semantic-tokens", json={"text": "focus = {\n\tid = GER_test\n}\n"})
    keywords = client.get("/lsp/keywords", params={"game_root": str(game_root)})

    assert completion.status_code == 200, completion.text
    completion_payload = completion.json()
    assert completion_payload["schema"] == "paradev.lsp.completion.v1"
    assert "GER_sample" in [item["label"] for item in completion_payload["items"]]
    assert keyword_completion.status_code == 200, keyword_completion.text
    keyword_completion_payload = keyword_completion.json()
    assert keyword_completion_payload["schema"] == "paradev.lsp.completion.v1"
    assert "stability_factor" in [item["label"] for item in keyword_completion_payload["items"]]
    assert semantic.status_code == 200, semantic.text
    assert semantic.json()["schema"] == "paradev.lsp.semantic-tokens.v1"
    assert keywords.status_code == 200, keywords.text
    keyword_payload = keywords.json()
    assert keyword_payload["schema"] == "paradev.hoi4.keyword-dataset.v1"
    modifier_rows = [row for row in keyword_payload["rows"] if row["kind"] == "modifier"]
    assert "stability_factor" in [row["name"] for row in modifier_rows]


def test_lsp_rest_keywords_use_configured_game_root_when_query_omitted(tmp_path: Path, cm_paradev_lock) -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces.rest import build_app

    previous = CM_PARADEV.get("paradev.hoi4.game_root", default=None)
    game_root = tmp_path / "configured-game"
    _write_lsp_keyword_documentation(game_root, kind="modifier", keyword="cfg_rest_factor")

    try:
        CM_PARADEV.set("paradev.hoi4.game_root", f"  {game_root}  ")
        client = testclient.TestClient(build_app())

        keywords = client.get("/lsp/keywords")

        assert keywords.status_code == 200, keywords.text
        keyword_payload = keywords.json()
        modifier_rows = [row for row in keyword_payload["rows"] if row["kind"] == "modifier"]
        assert keyword_payload["game_root"] == str(game_root)
        assert "cfg_rest_factor" in [row["name"] for row in modifier_rows]
    finally:
        if previous is None:
            CM_PARADEV.unset("paradev.hoi4.game_root")
        else:
            CM_PARADEV.set("paradev.hoi4.game_root", previous)


def test_lsp_rest_completion_uses_configured_game_root_when_body_omits_it(tmp_path: Path, cm_paradev_lock) -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces.rest import build_app

    previous = CM_PARADEV.get("paradev.hoi4.game_root", default=None)
    game_root = tmp_path / "configured-game"
    _write_lsp_keyword_documentation(game_root, kind="modifier", keyword="cfg_rest_completion_factor")

    try:
        CM_PARADEV.set("paradev.hoi4.game_root", f"  {game_root}  ")
        client = testclient.TestClient(build_app())

        completion = client.post(
            "/lsp/completion",
            json={
                "text": "idea = {\n\tmodifier = {\n\t\tcfg",
                "line": 2,
                "character": 5,
                "path": "common/ideas/sample.txt",
            },
        )

        assert completion.status_code == 200, completion.text
        completion_payload = completion.json()
        assert "cfg_rest_completion_factor" in [item["label"] for item in completion_payload["items"]]
    finally:
        if previous is None:
            CM_PARADEV.unset("paradev.hoi4.game_root")
        else:
            CM_PARADEV.set("paradev.hoi4.game_root", previous)


def test_pdx_lsp_server_initializes_and_publishes_diagnostics() -> None:
    server = PdxLanguageServer()
    uri = "file:///broken.pdx"

    initialize = server.handle_message({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    diagnostics = server.handle_message(
        {
            "jsonrpc": "2.0",
            "method": "textDocument/didOpen",
            "params": {"textDocument": {"uri": uri, "languageId": "pdx", "version": 1, "text": "value = 0x"}},
        }
    )

    assert initialize[0]["result"]["capabilities"]["completionProvider"]["resolveProvider"] is True
    assert initialize[0]["result"]["capabilities"]["semanticTokensProvider"]["legend"]["tokenTypes"] == [
        "property",
        "class",
        "enum",
        "string",
        "number",
        "variable",
    ]
    assert diagnostics == [
        {
            "jsonrpc": "2.0",
            "method": "textDocument/publishDiagnostics",
            "params": {
                "uri": uri,
                "diagnostics": [
                    {
                        "range": {"start": {"line": 0, "character": 8}, "end": {"line": 0, "character": 9}},
                        "severity": 1,
                        "code": "pdx.invalid_hex_number",
                        "source": "paradev.pdx",
                        "message": "PDX hexadecimal number requires at least one digit.",
                    }
                ],
            },
        }
    ]


def test_pdx_lsp_server_skips_large_change_diagnostics_until_save() -> None:
    server = PdxLanguageServer(change_diagnostics_max_bytes=8)
    uri = "file:///large-change.pdx"
    server.handle_message({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    server.handle_message(
        {
            "jsonrpc": "2.0",
            "method": "textDocument/didOpen",
            "params": {"textDocument": {"uri": uri, "languageId": "pdx", "version": 1, "text": "value = 1"}},
        }
    )

    diagnostics = server.handle_message(
        {
            "jsonrpc": "2.0",
            "method": "textDocument/didChange",
            "params": {"textDocument": {"uri": uri}, "contentChanges": [{"text": "value = 0x"}]},
        }
    )
    saved = server.handle_message({"jsonrpc": "2.0", "method": "textDocument/didSave", "params": {"textDocument": {"uri": uri}}})

    assert diagnostics == []
    assert saved[0]["params"]["diagnostics"][0]["code"] == "pdx.invalid_hex_number"


def test_lsp_reuses_parsed_document_for_repeated_text(monkeypatch: pytest.MonkeyPatch) -> None:
    from paradev import sdk as sdk_module

    text = "cache_probe = {\n\tid = GER_cache_probe\n}\n"
    calls = 0
    original = sdk_module.lsp.PDXBlock.from_str

    def counting_from_str(cls: type[object], value: str):
        nonlocal calls
        calls += 1
        return original(value)

    monkeypatch.setattr(sdk_module.lsp.PDXBlock, "from_str", classmethod(counting_from_str))

    semantic_tokens_pdx_lsp_text(text, path="focus.txt")
    document_symbols_pdx_lsp_text(text, path="focus.txt")

    assert calls == 1


def test_pdx_lsp_server_reads_catalog_for_completion_and_semantic_tokens(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    catalog_write(Project.load(project_root))
    uri = (project_root / "src/modules/focus/GER_sample/def.txt").as_uri()
    server = PdxLanguageServer(project_path=project_root)
    server.handle_message({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"rootUri": project_root.as_uri()}})
    server.handle_message(
        {
            "jsonrpc": "2.0",
            "method": "textDocument/didOpen",
            "params": {"textDocument": {"uri": uri, "languageId": "pdx", "version": 1, "text": "focus = {\n\tid = GER\n}\n"}},
        }
    )

    completion = server.handle_message(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "textDocument/completion",
            "params": {"textDocument": {"uri": uri}, "position": {"line": 1, "character": 9}},
        }
    )
    semantic = server.handle_message(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "textDocument/semanticTokens/full",
            "params": {"textDocument": {"uri": uri}},
        }
    )

    assert "GER_sample" in [item["label"] for item in completion[0]["result"]["items"]]
    assert semantic[0]["result"]["data"] == [0, 0, 5, 1, 0, 1, 1, 2, 0, 0, 0, 5, 3, 2, 0]


def test_pdx_lsp_server_payload_methods_do_not_require_open_documents(tmp_path: Path) -> None:
    documentation = tmp_path / "documentation"
    documentation.mkdir()
    (documentation / "modifiers_documentation.md").write_text(
        "# Modifiers\n\n" "## Modifiers for scope country\n\n" "* [stability_factor](#stability_factor)\n",
        encoding="utf-8",
    )
    server = PdxLanguageServer(game_root=tmp_path)
    server.handle_message({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})

    completion = server.handle_message(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "paradev/completionPayload",
            "params": {
                "text": "idea = {\n\tmodifier = {\n\t\tsta",
                "line": 2,
                "character": 5,
                "path": "common/ideas/sample.txt",
            },
        }
    )
    semantic = server.handle_message(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "paradev/semanticTokensPayload",
            "params": {"text": "focus = {\n\tid = GER_test\n}\n", "path": "focus.txt"},
        }
    )

    assert completion[0]["result"]["schema"] == "paradev.lsp.completion.v1"
    assert [item["label"] for item in completion[0]["result"]["items"]] == ["stability_factor"]
    assert semantic[0]["result"]["schema"] == "paradev.lsp.semantic-tokens.v1"
    assert semantic[0]["result"]["tokens"][0]["token_type"] == "class"


def test_pdx_lsp_server_blank_game_root_option_keeps_configured_fallback(tmp_path: Path, cm_paradev_lock) -> None:
    previous = CM_PARADEV.get("paradev.hoi4.game_root", default=None)
    game_root = tmp_path / "configured-game"
    _write_lsp_keyword_documentation(game_root, kind="modifier", keyword="cfg_server_factor")
    server = PdxLanguageServer()

    try:
        CM_PARADEV.set("paradev.hoi4.game_root", f"  {game_root}  ")
        server.handle_message(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {"initializationOptions": {"gameRoot": ""}},
            }
        )

        completion = server.handle_message(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "paradev/completionPayload",
                "params": {
                    "text": "idea = {\n\tmodifier = {\n\t\tcfg",
                    "line": 2,
                    "character": 5,
                    "path": "common/ideas/sample.txt",
                },
            }
        )

        assert "cfg_server_factor" in [item["label"] for item in completion[0]["result"]["items"]]
    finally:
        if previous is None:
            CM_PARADEV.unset("paradev.hoi4.game_root")
        else:
            CM_PARADEV.set("paradev.hoi4.game_root", previous)


def test_pdx_lsp_stdio_framing_round_trips_initialize_and_shutdown() -> None:
    source = BytesIO()
    sink = BytesIO()
    write_lsp_message(source, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    write_lsp_message(source, {"jsonrpc": "2.0", "id": 2, "method": "shutdown", "params": {}})
    write_lsp_message(source, {"jsonrpc": "2.0", "method": "exit", "params": {}})
    source.seek(0)

    serve_pdx_lsp_stdio(input_stream=source, output_stream=sink)

    sink.seek(0)
    first = read_lsp_message(sink)
    second = read_lsp_message(sink)
    assert first is not None
    assert first["id"] == 1
    assert first["result"]["serverInfo"]["name"] == "ParaDev PDX LSP"
    assert second == {"jsonrpc": "2.0", "id": 2, "result": None}
