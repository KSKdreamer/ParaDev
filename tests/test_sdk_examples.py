from __future__ import annotations

import json
from pathlib import Path

from heavenbase.utils import copy_dir

from paradev.sdk import (
    Project,
    diagnose_pdx_lsp_text,
    document_symbols_pdx_lsp_text,
    format_pdx_file,
    format_pdx_lsp_text,
    format_pdx_text,
    hover_pdx_lsp_text,
    parse_pdx_file,
)

PROJECT_ROOT = Path("demos/assets/projects/minimal").resolve()


def test_project_load_build_and_emit_manifests_sdk_example(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)

    project = Project.load(project_root)
    result = project.build(emit_manifests=True)

    assert result.project_id == "minimal_hoi4"
    assert result.dry_run is True
    assert result.collections[0].collection_id == "GER_main"
    assert [artifact.path for artifact in result.artifacts if artifact.artifact_type != "mod_descriptor"] == [
        "common/national_focus/GER_main.txt",
        "views/focus-tree/GER_main.json",
        "localisation/english/GER_sample_l_english.yml",
    ]
    assert [artifact.path for artifact in result.artifacts if artifact.artifact_type == "mod_descriptor"] == [
        "descriptor.mod",
        "launcher/minimal_hoi4.mod",
    ]
    assert [dependency.to_dict() for dependency in result.dependencies] == [
        {
            "source": "module:focus/GER_sample",
            "target": "idea:GER_industrial_spirit",
            "kind": "requires",
        },
        {
            "source": "module:focus/GER_sample",
            "target": "focus:GER_rhineland",
            "kind": "after",
        },
    ]
    source_map = json.loads((project.build_root / "source-map.json").read_text(encoding="utf-8"))
    assert [row["type"] for row in source_map["source_map"] if row["type"] != "mod_descriptor"] == ["pdx", "view", "loc"]
    assert [row["artifact_path"] for row in source_map["source_map"] if row["type"] == "mod_descriptor"] == [
        "descriptor.mod",
        "launcher/minimal_hoi4.mod",
    ]


def test_project_load_build_and_emit_artifacts_sdk_example(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)

    project = Project.load(project_root)
    result = project.build(emit_artifacts=True)

    assert result.dry_run is False
    assert (project.output_root / "common/national_focus/GER_main.txt").is_file()
    assert (project.build_root / "views/focus-tree/GER_main.json").is_file()
    assert not (project.output_root / "views/focus-tree/GER_main.json").exists()
    assert (project.output_root / "localisation/english/GER_sample_l_english.yml").is_file()


def test_project_create_build_and_emit_sdk_example(tmp_path: Path) -> None:
    project = Project.create(tmp_path / "starter-mod", title="Starter Mod")

    result = project.build(emit_artifacts=True, emit_manifests=True)

    assert project.project_id == "starter_mod"
    assert result.blocked is False
    assert [artifact.path for artifact in result.artifacts if artifact.artifact_type != "mod_descriptor"] == [
        "common/modifiers/starter_mod_starter_modifier.txt",
        "localisation/english/starter_mod_starter_modifier_l_english.yml",
    ]
    assert [artifact.path for artifact in result.artifacts if artifact.artifact_type == "mod_descriptor"] == [
        "descriptor.mod",
        "launcher/starter_mod.mod",
    ]
    assert (project.output_root / "descriptor.mod").is_file()
    assert (project.build_root / "launcher/starter_mod.mod").is_file()
    assert (project.output_root / "common/modifiers/starter_mod_starter_modifier.txt").is_file()
    assert (project.build_root / "summary.json").is_file()


def test_project_add_two_ideas_with_sdk_templates_example(tmp_path: Path) -> None:
    project = Project.create(tmp_path / "starter-mod", title="Starter Mod")

    for object_id, title, description in (
        ("GER_industry_spirit", "German Industry Spirit", "Industrial production spirit."),
        ("GER_army_spirit", "German Army Spirit", "Army modernization spirit."),
    ):
        plan = project.scaffold_module(
            "hoi4:idea/basic",
            object_id,
            values={"title": title, "description": description},
            write=True,
        )
        assert plan["blocked"] is False

    result = project.build()

    assert result.blocked is False
    assert (project.source_roots[0] / "modules/idea/GER_industry_spirit/def.txt").is_file()
    assert (project.source_roots[0] / "modules/idea/GER_army_spirit/main.loc").is_file()


def test_parse_pdx_file_sdk_example(tmp_path: Path) -> None:
    source = tmp_path / "focus.pdx"
    source.write_text("focus = { id = GER_test }", encoding="utf-8")

    payload = parse_pdx_file(source, include_tokens=True)

    assert payload["schema"] == "paradev.pdx.parse.v1"
    assert payload["path"] == str(source.resolve())
    assert payload["file_ext"] == ".pdx"
    assert payload["ok"] is True
    assert payload["data"] == {"focus": {"id": "GER_test"}}
    assert payload["diagnostics"] == []
    assert payload["tokens"][0] == {"type": "identifier", "value": "focus", "line": 1, "column": 1}


def test_parse_pdx_file_sdk_reports_diagnostics_without_raising(tmp_path: Path) -> None:
    source = tmp_path / "broken.pdx"
    source.write_text("value = 0x", encoding="utf-8")

    payload = parse_pdx_file(source, include_tokens=True)

    assert payload == {
        "schema": "paradev.pdx.parse.v1",
        "path": str(source.resolve()),
        "file_ext": ".pdx",
        "ok": False,
        "data": None,
        "diagnostics": [
            {
                "code": "pdx.invalid_hex_number",
                "message": "PDX hexadecimal number requires at least one digit.",
                "line": 1,
                "column": 9,
                "severity": "error",
            }
        ],
    }


def test_format_pdx_text_sdk_example() -> None:
    payload = format_pdx_text("# focus comment\nfocus={id=GER_test cost=10}", path="focus.pdx")

    assert payload == {
        "schema": "paradev.pdx.format.v1",
        "path": "focus.pdx",
        "file_ext": ".pdx",
        "ok": True,
        "formatted_text": "# focus comment\nfocus = {\n\tid = GER_test\n\tcost = 10\n}\n",
        "changed": True,
        "written": False,
        "indent": "\t",
        "comments": True,
        "diagnostics": [],
    }


def test_format_pdx_file_sdk_can_preview_and_write(tmp_path: Path) -> None:
    source = tmp_path / "focus.pdx"
    source.write_text("focus={id=GER_test cost=10}", encoding="utf-8")

    dry = format_pdx_file(source)

    assert dry["schema"] == "paradev.pdx.format.v1"
    assert dry["path"] == str(source.resolve())
    assert dry["formatted_text"] == "focus = {\n\tid = GER_test\n\tcost = 10\n}\n"
    assert dry["changed"] is True
    assert dry["written"] is False
    assert source.read_text(encoding="utf-8") == "focus={id=GER_test cost=10}"

    written = format_pdx_file(source, write=True)

    assert written["changed"] is True
    assert written["written"] is True
    assert source.read_text(encoding="utf-8") == "focus = {\n\tid = GER_test\n\tcost = 10\n}\n"


def test_format_pdx_file_sdk_reports_diagnostics_without_writing(tmp_path: Path) -> None:
    source = tmp_path / "broken.pdx"
    source.write_text("value = 0x", encoding="utf-8")

    payload = format_pdx_file(source, write=True)

    assert payload == {
        "schema": "paradev.pdx.format.v1",
        "path": str(source.resolve()),
        "file_ext": ".pdx",
        "ok": False,
        "formatted_text": None,
        "changed": False,
        "written": False,
        "indent": "\t",
        "comments": True,
        "diagnostics": [
            {
                "code": "pdx.invalid_hex_number",
                "message": "PDX hexadecimal number requires at least one digit.",
                "line": 1,
                "column": 9,
                "severity": "error",
            }
        ],
    }
    assert source.read_text(encoding="utf-8") == "value = 0x"


def test_format_pdx_file_sdk_reports_write_diagnostics(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "focus.pdx"
    source.write_text("focus={id=GER_test}", encoding="utf-8")

    def fail_write(self: Path, *args, **kwargs) -> int:
        raise OSError("permission denied")

    monkeypatch.setattr(type(source), "write_text", fail_write)

    payload = format_pdx_file(source, write=True)

    assert payload == {
        "schema": "paradev.pdx.format.v1",
        "path": str(source.resolve()),
        "file_ext": ".pdx",
        "ok": False,
        "formatted_text": None,
        "changed": False,
        "written": False,
        "indent": "\t",
        "comments": True,
        "diagnostics": [
            {
                "code": "pdx.source_unwritable",
                "message": f"PDX source file cannot be written: {source.resolve()}. permission denied.",
                "severity": "error",
            }
        ],
    }


def test_format_pdx_lsp_text_sdk_returns_full_document_edit() -> None:
    payload = format_pdx_lsp_text("focus={id=GER_test cost=10}", uri="file:///workspace/focus.pdx")

    assert payload == {
        "schema": "paradev.lsp.formatting.v1",
        "method": "textDocument/formatting",
        "language": "pdx",
        "uri": "file:///workspace/focus.pdx",
        "path": None,
        "file_ext": "",
        "ok": True,
        "changed": True,
        "edits": [
            {
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 0, "character": 27},
                },
                "newText": "focus = {\n\tid = GER_test\n\tcost = 10\n}\n",
            }
        ],
        "diagnostics": [],
    }


def test_format_pdx_lsp_text_sdk_returns_no_edits_when_unchanged() -> None:
    text = "focus = {\n\tid = GER_test\n}\n"

    payload = format_pdx_lsp_text(text, path="focus.pdx")

    assert payload["schema"] == "paradev.lsp.formatting.v1"
    assert payload["path"] == "focus.pdx"
    assert payload["file_ext"] == ".pdx"
    assert payload["ok"] is True
    assert payload["changed"] is False
    assert payload["edits"] == []
    assert payload["diagnostics"] == []


def test_format_pdx_lsp_text_sdk_maps_parse_errors_to_lsp_diagnostics() -> None:
    payload = format_pdx_lsp_text("value = 0x", uri="file:///workspace/broken.pdx")

    assert payload == {
        "schema": "paradev.lsp.formatting.v1",
        "method": "textDocument/formatting",
        "language": "pdx",
        "uri": "file:///workspace/broken.pdx",
        "path": None,
        "file_ext": "",
        "ok": False,
        "changed": False,
        "edits": [],
        "diagnostics": [
            {
                "range": {
                    "start": {"line": 0, "character": 8},
                    "end": {"line": 0, "character": 9},
                },
                "severity": 1,
                "code": "pdx.invalid_hex_number",
                "source": "paradev.pdx",
                "message": "PDX hexadecimal number requires at least one digit.",
            }
        ],
    }


def test_diagnose_pdx_lsp_text_sdk_reports_clean_document() -> None:
    payload = diagnose_pdx_lsp_text("focus = {\n\tid = GER_test\n}\n", uri="file:///workspace/focus.pdx")

    assert payload == {
        "schema": "paradev.lsp.diagnostics.v1",
        "method": "textDocument/publishDiagnostics",
        "language": "pdx",
        "uri": "file:///workspace/focus.pdx",
        "path": None,
        "file_ext": "",
        "ok": True,
        "diagnostics": [],
    }


def test_diagnose_pdx_lsp_text_sdk_maps_parse_errors_to_lsp_diagnostics() -> None:
    payload = diagnose_pdx_lsp_text("value = 0x", path="broken.pdx")

    assert payload == {
        "schema": "paradev.lsp.diagnostics.v1",
        "method": "textDocument/publishDiagnostics",
        "language": "pdx",
        "uri": None,
        "path": "broken.pdx",
        "file_ext": ".pdx",
        "ok": False,
        "diagnostics": [
            {
                "range": {
                    "start": {"line": 0, "character": 8},
                    "end": {"line": 0, "character": 9},
                },
                "severity": 1,
                "code": "pdx.invalid_hex_number",
                "source": "paradev.pdx",
                "message": "PDX hexadecimal number requires at least one digit.",
            }
        ],
    }


def test_document_symbols_pdx_lsp_text_sdk_returns_nested_symbols() -> None:
    payload = document_symbols_pdx_lsp_text("focus={id=GER_test cost=10}", uri="file:///workspace/focus.pdx")

    assert payload == {
        "schema": "paradev.lsp.symbols.v1",
        "method": "textDocument/documentSymbol",
        "language": "pdx",
        "uri": "file:///workspace/focus.pdx",
        "path": None,
        "file_ext": "",
        "ok": True,
        "symbols": [
            {
                "name": "focus",
                "kind": 19,
                "detail": "=",
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 0, "character": 5},
                },
                "selectionRange": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 0, "character": 5},
                },
                "children": [
                    {
                        "name": "id",
                        "kind": 7,
                        "detail": "=",
                        "range": {
                            "start": {"line": 0, "character": 7},
                            "end": {"line": 0, "character": 9},
                        },
                        "selectionRange": {
                            "start": {"line": 0, "character": 7},
                            "end": {"line": 0, "character": 9},
                        },
                    },
                    {
                        "name": "cost",
                        "kind": 7,
                        "detail": "=",
                        "range": {
                            "start": {"line": 0, "character": 19},
                            "end": {"line": 0, "character": 23},
                        },
                        "selectionRange": {
                            "start": {"line": 0, "character": 19},
                            "end": {"line": 0, "character": 23},
                        },
                    },
                ],
            }
        ],
        "diagnostics": [],
    }


def test_document_symbols_pdx_lsp_text_sdk_maps_parse_errors_to_lsp_diagnostics() -> None:
    payload = document_symbols_pdx_lsp_text("value = 0x", path="broken.pdx")

    assert payload == {
        "schema": "paradev.lsp.symbols.v1",
        "method": "textDocument/documentSymbol",
        "language": "pdx",
        "uri": None,
        "path": "broken.pdx",
        "file_ext": ".pdx",
        "ok": False,
        "symbols": [],
        "diagnostics": [
            {
                "range": {
                    "start": {"line": 0, "character": 8},
                    "end": {"line": 0, "character": 9},
                },
                "severity": 1,
                "code": "pdx.invalid_hex_number",
                "source": "paradev.pdx",
                "message": "PDX hexadecimal number requires at least one digit.",
            }
        ],
    }


def test_hover_pdx_lsp_text_sdk_returns_scalar_hover() -> None:
    payload = hover_pdx_lsp_text("focus={id=GER_test cost=10}", 0, 8, uri="file:///workspace/focus.pdx")

    assert payload == {
        "schema": "paradev.lsp.hover.v1",
        "method": "textDocument/hover",
        "language": "pdx",
        "uri": "file:///workspace/focus.pdx",
        "path": None,
        "file_ext": "",
        "ok": True,
        "position": {"line": 0, "character": 8},
        "hover": {
            "contents": {"kind": "markdown", "value": "`id` = `GER_test`\n\nPDX scalar entry."},
            "range": {
                "start": {"line": 0, "character": 7},
                "end": {"line": 0, "character": 9},
            },
        },
        "diagnostics": [],
    }


def test_hover_pdx_lsp_text_sdk_returns_no_hover_for_empty_position() -> None:
    payload = hover_pdx_lsp_text("focus={id=GER_test cost=10}", 0, 6, path="focus.pdx")

    assert payload == {
        "schema": "paradev.lsp.hover.v1",
        "method": "textDocument/hover",
        "language": "pdx",
        "uri": None,
        "path": "focus.pdx",
        "file_ext": ".pdx",
        "ok": True,
        "position": {"line": 0, "character": 6},
        "hover": None,
        "diagnostics": [],
    }


def test_hover_pdx_lsp_text_sdk_maps_parse_errors_to_lsp_diagnostics() -> None:
    payload = hover_pdx_lsp_text("value = 0x", 0, 8, path="broken.pdx")

    assert payload == {
        "schema": "paradev.lsp.hover.v1",
        "method": "textDocument/hover",
        "language": "pdx",
        "uri": None,
        "path": "broken.pdx",
        "file_ext": ".pdx",
        "ok": False,
        "position": {"line": 0, "character": 8},
        "hover": None,
        "diagnostics": [
            {
                "range": {
                    "start": {"line": 0, "character": 8},
                    "end": {"line": 0, "character": 9},
                },
                "severity": 1,
                "code": "pdx.invalid_hex_number",
                "source": "paradev.pdx",
                "message": "PDX hexadecimal number requires at least one digit.",
            }
        ],
    }
