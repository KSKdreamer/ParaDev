from __future__ import annotations

from pathlib import Path

import pytest
from heavenbase.utils import dumps_json, loads_json

import paradev.api as public_api
import paradev.api.projects as project_api
import paradev.sdk.project as project_sdk
import paradev.surfaces.rest as rest_surface
from paradev.build import Slot
from paradev.sdk import Project, ProjectManifestError, plan_frontend_api_rest_request
from paradev.sdk.source_forms import (
    MAX_LOC_SOURCE_FORM_CONTROLS,
    MAX_PDX_SOURCE_FORM_CONTROLS,
    apply_source_form_values,
    normalize_source_form_patch,
)


class _SourceFormFamily:
    def __init__(self, payload: object) -> None:
        self.payload = payload
        self.calls: list[dict[str, str]] = []

    def source_form(self, *, module_id: str, relative_path: str, text: str) -> object:
        self.calls.append(
            {
                "module_id": module_id,
                "relative_path": relative_path,
                "text": text,
            }
        )
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


class _SourceFormRegistry:
    def __init__(self, family: object, *, error: ValueError | None = None) -> None:
        self._family = family
        self._error = error
        self.calls: list[str] = []

    def family(self, family_id: str) -> object:
        self.calls.append(family_id)
        if self._error is not None:
            raise self._error
        return self._family


class _PdxSourceFormFamily:
    source_slots = (Slot(name="def", match="def.txt", kind="pdx", required=True),)


class _LocSourceFormFamily:
    source_slots = (Slot(name="loc", match="main.loc", kind="loc", required=True),)


class _YmlLocSourceFormFamily:
    source_slots = (Slot(name="loc", match="main.yml", kind="loc", required=True),)


class _HintedPdxSourceFormFamily(_PdxSourceFormFamily):
    source_form_field_hints = {
        "year": {
            "label": {"default": "Production year", "zh": "投产年份"},
            "description": {
                "default": "Technology year used for equipment availability.",
                "zh": "用于装备可用性的科技年份。",
            },
        }
    }


class _IntegerListPdxSourceFormFamily(_PdxSourceFormFamily):
    source_form_field_hints = {
        "provinces": {
            "label": {"default": "Provinces", "zh": "省份"},
            "control": "integer-list",
            "columns": 1,
            "minimum": 1,
        },
        "victory_points": {
            "label": {"default": "Victory points", "zh": "胜利点"},
            "control": "integer-list",
            "columns": 2,
            "minimum": 0,
        },
    }


class _BlockBodyPdxSourceFormFamily(_PdxSourceFormFamily):
    source_form_field_hints = {
        "$module": {
            "label": {"default": "Effect body", "zh": "效果脚本"},
            "description": {
                "default": "Statements executed by this scripted effect.",
                "zh": "此脚本效果执行的语句。",
            },
            "placeholder": {
                "default": "add_political_power = 10",
                "zh": "add_political_power = 10",
            },
            "control": "block-text",
        }
    }


class _MultiPdxSourceFormFamily:
    source_slots = (
        Slot(
            name="definitions",
            match=r"^common/example/.*\.txt$",
            kind="pdx",
            regex=True,
            many=True,
        ),
        Slot(name="fragment", match="fragment.pdx", kind="pdx"),
        Slot(name="interface", match="interface/example.gui", kind="pdx"),
    )


def _source_form_project(tmp_path: Path) -> tuple[Project, Path, str]:
    project = Project.create(tmp_path / "guided-mod", project_id="guided_mod", title="Guided Mod")
    source_path = project.root / "src/modules/idea/GER_guided/record.json"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    disk_text = dumps_json(
        {
            "enabled": True,
            "kind": "infantry",
            "mesh": {"scale": 1},
            "title": "Disk title",
        }
    )
    source_path.write_text(disk_text, encoding="utf-8")
    return project, source_path, disk_text


def _install_source_form_family(
    monkeypatch: pytest.MonkeyPatch,
    family: object,
    *,
    error: ValueError | None = None,
) -> _SourceFormRegistry:
    registry = _SourceFormRegistry(family, error=error)
    monkeypatch.setattr(Project, "_build_registry", lambda self, *, profile=None: registry)
    return registry


def _rich_source_form() -> dict[str, object]:
    return {
        "contract": "pihc2.idea.record.v1",
        "label": {"default": "Idea", "zh": "理念"},
        "description": "Edit the common fields without touching raw JSON.",
        "sections": [
            {
                "id": "identity",
                "label": "Identity",
                "controls": [
                    {
                        "id": "module-id",
                        "label": "Module ID",
                        "control": "readonly",
                        "value": "idea/GER_guided",
                    }
                ],
                "sections": [
                    {
                        "id": "details",
                        "label": {"default": "Details", "zh": "详情"},
                        "description": "Frequently edited values.",
                        "controls": [
                            {
                                "id": "title",
                                "label": "Title",
                                "control": "text",
                                "value": "Unsaved title",
                                "placeholder": {"default": "Display title", "zh": "显示名称"},
                                "patch": {"op": "replace-json-scalar", "path": ["title"]},
                            },
                            {
                                "id": "scale",
                                "label": "Scale",
                                "control": "number",
                                "value": 1.5,
                                "min": 0,
                                "max": 4,
                                "step": 0.25,
                                "placeholder": {"default": "Scale", "zh": "缩放"},
                                "patch": {"op": "replace-json-scalar", "path": ["mesh", "scale"]},
                            },
                            {
                                "id": "enabled",
                                "label": "Enabled",
                                "control": "boolean",
                                "value": False,
                                "patch": {"op": "replace-json-scalar", "path": ["enabled"]},
                            },
                            {
                                "id": "kind",
                                "label": "Unit kind",
                                "control": "choice",
                                "value": "armor",
                                "choices": [
                                    {"label": "Infantry", "value": "infantry"},
                                    {"label": {"default": "Armor", "zh": "装甲"}, "value": "armor"},
                                ],
                                "placeholder": "Choose a kind",
                                "patch": {"op": "replace-json-scalar", "path": ["kind"]},
                            },
                        ],
                    }
                ],
            }
        ],
    }


def _single_control_form(control: dict[str, object], *, section_label: object = "Main") -> dict[str, object]:
    return {
        "contract": "pihc2.test.record.v1",
        "sections": [
            {
                "id": "main",
                "label": section_label,
                "controls": [control],
            }
        ],
    }


def test_project_source_form_wraps_family_contract_and_uses_unsaved_text_without_writing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project, source_path, disk_text = _source_form_project(tmp_path)
    raw_form = _rich_source_form()
    family = _SourceFormFamily(raw_form)
    registry = _install_source_form_family(monkeypatch, family)
    editor_text = dumps_json(
        {
            "enabled": False,
            "kind": "armor",
            "mesh": {"scale": 1.5},
            "title": "Unsaved title",
        }
    )

    payload = project.source_form(source_path, text=editor_text)

    assert payload == {
        "schema": "paradev.source-form.v1",
        "project_id": "guided_mod",
        "family": "idea",
        "module_id": "idea/GER_guided",
        "path": str(source_path),
        "relative_path": "src/modules/idea/GER_guided/record.json",
        "module_relative_path": "record.json",
        "source_root": str(project.root / "src"),
        "source_format": "json",
        **raw_form,
    }
    assert registry.calls == ["idea"]
    assert family.calls == [
        {
            "module_id": "idea/GER_guided",
            "relative_path": "record.json",
            "text": editor_text,
        }
    ]
    assert source_path.read_text(encoding="utf-8") == disk_text


def test_project_plans_and_applies_revision_guarded_json_source_form_values(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project, source_path, disk_text = _source_form_project(tmp_path)
    _install_source_form_family(monkeypatch, _SourceFormFamily(_rich_source_form()))

    plan = project.plan_source_form_update(
        source_path,
        {
            "enabled": False,
            "kind": "armor",
            "scale": 2.5,
            "title": "Guided title",
        },
    )

    assert plan["schema"] == "paradev.source-form-update.v1"
    assert plan["module_id"] == "idea/GER_guided"
    assert plan["source_format"] == "json"
    assert plan["form_contract"] == "pihc2.idea.record.v1"
    assert plan["changed"] is True
    assert [change["control_id"] for change in plan["changes"]] == [
        "enabled",
        "kind",
        "scale",
        "title",
    ]
    edit = plan["source_edit"]
    assert edit["path"] == str(source_path)
    assert edit["expected_size"] == len(disk_text.encode("utf-8"))
    assert str(edit["expected_mtime_ns"]).isdigit()
    assert source_path.read_text(encoding="utf-8") == disk_text
    assert loads_json(edit["text"], restore=False) == {
        "enabled": False,
        "kind": "armor",
        "mesh": {"scale": 2.5},
        "title": "Guided title",
    }

    applied = project.apply_source_draft(source_edits=[edit])

    assert applied["written"] is True
    assert source_path.read_text(encoding="utf-8") == edit["text"]


def test_project_plans_and_atomically_applies_guided_source_update_batch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project, first_path, disk_text = _source_form_project(tmp_path)
    second_path = project.root / "src/modules/idea/GER_second/record.json"
    second_path.parent.mkdir(parents=True)
    second_path.write_text(disk_text, encoding="utf-8")
    _install_source_form_family(monkeypatch, _SourceFormFamily(_rich_source_form()))

    plan = project.plan_source_form_updates(
        [
            {
                "source_path": first_path,
                "values": {"title": "First guided title"},
            },
            {
                "source_path": second_path,
                "values": {"enabled": False},
            },
        ]
    )

    assert plan["schema"] == "paradev.source-form-update-batch.v1"
    assert plan["changed"] is True
    assert plan["counts"] == {
        "requested": 2,
        "changed": 2,
        "unchanged": 0,
    }
    assert [row["module_id"] for row in plan["updates"]] == [
        "idea/GER_guided",
        "idea/GER_second",
    ]
    assert [edit["path"] for edit in plan["source_edits"]] == [
        str(first_path),
        str(second_path),
    ]
    assert first_path.read_text(encoding="utf-8") == disk_text
    assert second_path.read_text(encoding="utf-8") == disk_text

    applied = project.apply_source_draft(source_edits=plan["source_edits"])

    assert applied["written"] is True
    assert loads_json(first_path.read_text(encoding="utf-8"), restore=False)["title"] == "First guided title"
    assert loads_json(second_path.read_text(encoding="utf-8"), restore=False)["enabled"] is False


def test_project_guided_source_update_batch_preserves_unsaved_code_base(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project, source_path, disk_text = _source_form_project(tmp_path)
    _install_source_form_family(monkeypatch, _SourceFormFamily(_rich_source_form()))
    unsaved_text = dumps_json(
        {
            "enabled": True,
            "kind": "armor",
            "mesh": {"scale": 1},
            "title": "Unsaved code title",
        }
    )

    plan = project.plan_source_form_updates(
        [
            {
                "source_path": source_path,
                "text": unsaved_text,
                "values": {"title": "Guided title"},
            }
        ]
    )

    assert plan["changed"] is True
    edit = plan["source_edits"][0]
    assert edit["expected_size"] == len(disk_text.encode("utf-8"))
    assert loads_json(edit["text"], restore=False) == {
        "enabled": True,
        "kind": "armor",
        "mesh": {"scale": 1},
        "title": "Guided title",
    }
    assert source_path.read_text(encoding="utf-8") == disk_text

    applied = project.apply_source_draft(source_edits=plan["source_edits"])

    assert applied["written"] is True
    assert source_path.read_text(encoding="utf-8") == edit["text"]


def test_project_guided_source_update_batch_omits_unchanged_edits_and_rejects_duplicates(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project, source_path, disk_text = _source_form_project(tmp_path)
    _install_source_form_family(monkeypatch, _SourceFormFamily(_rich_source_form()))

    unchanged = project.plan_source_form_updates([{"source_path": source_path, "values": {"title": "Disk title"}}])

    assert unchanged["changed"] is False
    assert unchanged["counts"] == {
        "requested": 1,
        "changed": 0,
        "unchanged": 1,
    }
    assert unchanged["source_edits"] == []
    assert unchanged["updates"][0]["source_edit"]["text"] == disk_text

    with pytest.raises(ValueError, match="same filesystem path more than once"):
        project.plan_source_form_updates(
            [
                {"source_path": source_path, "values": {"title": "First"}},
                {"source_path": source_path, "values": {"title": "Second"}},
            ]
        )

    assert source_path.read_text(encoding="utf-8") == disk_text


@pytest.mark.parametrize(
    ("updates", "message"),
    [
        ([], "must not be empty"),
        ([{"source_path": "record.json"}], "values must be an object"),
        (
            [
                {
                    "source_path": "record.json",
                    "values": {"title": "Title"},
                    "text": 42,
                }
            ],
            "text must be a string",
        ),
        (
            [
                {
                    "source_path": "record.json",
                    "values": {"title": "Title"},
                    "write": True,
                }
            ],
            "contains unsupported fields: write",
        ),
    ],
)
def test_project_guided_source_update_batch_rejects_invalid_rows(
    tmp_path: Path,
    updates: list[dict[str, object]],
    message: str,
) -> None:
    project = Project.create(tmp_path / "guided-batch", title="Guided batch")

    with pytest.raises(ValueError, match=message):
        project.plan_source_form_updates(updates)


def test_project_source_form_update_preserves_exact_pdx_surroundings(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project = Project.create(
        tmp_path / "pdx-guided-update",
        project_id="pdx_guided_update",
        title="PDX Guided Update",
    )
    source_path = project.root / "src/modules/example/EXAMPLE/fragment.pdx"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_text = "# 😀 keep this comment\r\n" "year = 1936\r\n" "active = yes\r\n" 'title = "Old title"\r\n'
    source_path.write_text(source_text, encoding="utf-8")
    _install_source_form_family(monkeypatch, _MultiPdxSourceFormFamily())

    plan = project.plan_source_form_update(
        source_path,
        {
            "pdx-control-000": 1937,
            "pdx-control-001": False,
            "pdx-control-002": "New title",
        },
    )

    assert plan["source_format"] == "pdx"
    assert plan["changed"] is True
    assert plan["source_edit"]["text"] == ("# 😀 keep this comment\r\n" "year = 1937\r\n" "active = no\r\n" 'title = "New title"\r\n')
    assert source_path.read_bytes().decode("utf-8") == source_text


def test_project_source_form_projects_and_updates_registry_integer_lists(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project = Project.create(
        tmp_path / "pdx-list-guided-update",
        project_id="pdx_list_guided_update",
        title="PDX List Guided Update",
    )
    source_path = project.root / "src/modules/state/199/def.txt"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_text = (
        "# 😀 keep this comment\r\n"
        "state = {\r\n"
        "    id = 199\r\n"
        "    provinces = {\r\n"
        "        345\r\n"
        "        1637\r\n"
        "    }\r\n"
        "    history = {\r\n"
        "        victory_points = {\r\n"
        "            345\r\n"
        "            5\r\n"
        "            1637\r\n"
        "            3\r\n"
        "        }\r\n"
        "    }\r\n"
        "}\r\n"
    )
    source_path.write_bytes(source_text.encode("utf-8"))
    _install_source_form_family(monkeypatch, _IntegerListPdxSourceFormFamily())

    payload = project.source_form(source_path)

    assert payload is not None
    controls = _source_form_controls(payload)
    list_controls = [control for control in controls if control.get("patch", {}).get("op") == "replace-pdx-integer-list"]
    assert [control["value"] for control in list_controls] == [
        "345\n1637",
        "345 5\n1637 3",
    ]
    assert [control["multiline"] for control in list_controls] == [True, True]
    province_patch = list_controls[0]["patch"]
    assert province_patch["path"] == [
        {"key": "state", "occurrence": 0},
        {"key": "provinces", "occurrence": 0},
    ]
    assert province_patch["layout"] == {
        "prefix": "\r\n        ",
        "column_separator": " ",
        "row_separator": "\r\n        ",
        "suffix": "\r\n    ",
    }
    assert province_patch["source_length"] == _utf16_length(source_text)

    plan = project.plan_source_form_update(
        source_path,
        {
            list_controls[0]["id"]: "345\n2000\n3000",
            list_controls[1]["id"]: "345 7\n3000 2",
        },
    )

    assert plan["changed"] is True
    assert plan["changes"] == [
        {
            "control_id": list_controls[0]["id"],
            "previous": "345\n1637",
            "value": "345\n2000\n3000",
        },
        {
            "control_id": list_controls[1]["id"],
            "previous": "345 5\n1637 3",
            "value": "345 7\n3000 2",
        },
    ]
    assert plan["source_edit"]["text"] == source_text.replace(
        "        345\r\n        1637",
        "        345\r\n        2000\r\n        3000",
        1,
    ).replace(
        "            345\r\n            5\r\n            1637\r\n            3",
        "            345 7\r\n            3000 2",
        1,
    )
    assert source_path.read_bytes() == source_text.encode("utf-8")

    applied = project.apply_source_draft(source_edits=[plan["source_edit"]])

    assert applied["written"] is True
    assert source_path.read_bytes().decode("utf-8") == plan["source_edit"]["text"]


@pytest.mark.parametrize(
    ("replacement", "message"),
    [
        ("345 5 1637", "exactly 2 integers per row"),
        ("345 five", "not a decimal integer"),
        ("345 -1", "below the minimum 0"),
        ("", "at least one integer"),
    ],
)
def test_project_source_form_rejects_invalid_registry_integer_list_updates(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    replacement: str,
    message: str,
) -> None:
    project = Project.create(tmp_path / "pdx-list-invalid", title="PDX list invalid")
    source_path = project.root / "src/modules/state/199/def.txt"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_text = "state = { history = { victory_points = { 345 5 } } }"
    source_path.write_text(source_text, encoding="utf-8")
    _install_source_form_family(monkeypatch, _IntegerListPdxSourceFormFamily())
    payload = project.source_form(source_path)
    assert payload is not None
    control = next(control for control in _source_form_controls(payload) if control.get("patch", {}).get("op") == "replace-pdx-integer-list")

    with pytest.raises(ValueError, match=message):
        project.plan_source_form_update(source_path, {control["id"]: replacement})

    assert source_path.read_text(encoding="utf-8") == source_text


def test_project_source_form_rejects_commented_registry_integer_lists(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project = Project.create(tmp_path / "pdx-list-comment", title="PDX list comment")
    source_path = project.root / "src/modules/state/199/def.txt"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text(
        "state = { provinces = { 345 # keep province\n 1637 } }",
        encoding="utf-8",
    )
    _install_source_form_family(monkeypatch, _IntegerListPdxSourceFormFamily())

    with pytest.raises(ValueError, match="contains comments; edit it in Code"):
        project.source_form(source_path)


def test_project_source_form_projects_and_updates_registry_block_bodies(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project = Project.create(tmp_path / "pdx-block-guided-update", title="PDX block guided update")
    source_path = project.root / "src/modules/scripted_effect/MY_EFFECT/def.txt"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_text = (
        "# 😀 keep this comment\r\n"
        "MY_EFFECT = {\r\n"
        "\tadd_political_power = 5\r\n"
        "\tif = {\r\n"
        "\t\tlimit = { always = yes }\r\n"
        "\t\tadd_stability = 0.01\r\n"
        "\t}\r\n"
        "}\r\n"
    )
    source_path.write_bytes(source_text.encode("utf-8"))
    _install_source_form_family(monkeypatch, _BlockBodyPdxSourceFormFamily())

    payload = project.source_form(source_path)

    assert payload is not None
    control = next(control for control in _source_form_controls(payload) if control.get("patch", {}).get("op") == "replace-pdx-block-body")
    assert control["label"] == {"default": "Effect body", "zh": "效果脚本"}
    assert control["value"] == ("add_political_power = 5\n" "if = {\n" "\tlimit = { always = yes }\n" "\tadd_stability = 0.01\n" "}")
    assert control["multiline"] is True
    patch = control["patch"]
    assert patch["path"] == [{"key": "MY_EFFECT", "occurrence": 0}]
    assert patch["layout"] == {
        "prefix": "\r\n\t",
        "line_prefix": "\r\n\t",
        "suffix": "\r\n",
    }
    assert patch["source_length"] == _utf16_length(source_text)

    replacement = "add_political_power = 10\nadd_stability = 0.05"
    plan = project.plan_source_form_update(source_path, {control["id"]: replacement})

    assert plan["changed"] is True
    assert plan["changes"] == [
        {
            "control_id": control["id"],
            "previous": control["value"],
            "value": replacement,
        }
    ]
    assert plan["source_edit"]["text"] == (
        "# 😀 keep this comment\r\n" "MY_EFFECT = {\r\n" "\tadd_political_power = 10\r\n" "\tadd_stability = 0.05\r\n" "}\r\n"
    )
    assert source_path.read_bytes() == source_text.encode("utf-8")


def test_project_source_form_block_body_supports_empty_blocks_and_rejects_escape(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project = Project.create(tmp_path / "pdx-empty-block", title="PDX empty block")
    source_path = project.root / "src/modules/scripted_effect/EMPTY_EFFECT/def.txt"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_text = "EMPTY_EFFECT = {}\n"
    source_path.write_text(source_text, encoding="utf-8")
    _install_source_form_family(monkeypatch, _BlockBodyPdxSourceFormFamily())
    payload = project.source_form(source_path)
    assert payload is not None
    control = _source_form_controls(payload)[0]

    assert control["value"] == ""
    assert control["patch"]["span"] == {"start": 16, "end": 16}
    plan = project.plan_source_form_update(
        source_path,
        {control["id"]: "add_political_power = 5"},
    )
    assert plan["source_edit"]["text"] == "EMPTY_EFFECT = {\n    add_political_power = 5\n}\n"

    with pytest.raises(ValueError, match="must remain inside one PDX block"):
        project.plan_source_form_update(
            source_path,
            {control["id"]: "}\nOTHER_EFFECT = { always = yes"},
        )


def test_pdx_block_body_apply_revalidates_registry_path() -> None:
    text = "EXPECTED = { always = yes }\n"
    sections = [
        {
            "id": "body",
            "label": "Body",
            "controls": [
                {
                    "id": "body-control",
                    "label": "Body",
                    "control": "text",
                    "value": "always = yes",
                    "patch": {
                        "op": "replace-pdx-block-body",
                        "path": [{"key": "OTHER", "occurrence": 0}],
                        "span": {"start": 12, "end": 26},
                        "expected": " always = yes ",
                        "layout": {
                            "prefix": " ",
                            "line_prefix": " ",
                            "suffix": " ",
                        },
                        "source_length": len(text),
                    },
                }
            ],
        }
    ]

    with pytest.raises(ValueError, match="path does not contain 'OTHER'"):
        apply_source_form_values(
            text=text,
            source_format="pdx",
            sections=sections,
            values={"body-control": "always = no"},
        )


@pytest.mark.parametrize(
    ("values", "message"),
    [
        ({"missing": "value"}, "unknown or readonly control 'missing'"),
        ({"module-id": "idea/OTHER"}, "unknown or readonly control 'module-id'"),
        ({"scale": "large"}, "requires a number"),
        ({"scale": 5}, "exceeds its maximum"),
        ({"kind": "cavalry"}, "requires one declared choice"),
    ],
)
def test_project_source_form_update_rejects_unowned_readonly_and_mismatched_values(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    values: dict[str, object],
    message: str,
) -> None:
    project, source_path, disk_text = _source_form_project(tmp_path)
    _install_source_form_family(monkeypatch, _SourceFormFamily(_rich_source_form()))

    with pytest.raises(ValueError, match=message):
        project.plan_source_form_update(source_path, values)

    assert source_path.read_text(encoding="utf-8") == disk_text


def test_project_source_form_returns_none_for_unsupported_sources_and_missing_hooks(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project, source_path, _disk_text = _source_form_project(tmp_path)
    text_path = source_path.with_suffix(".md")
    text_path.write_text("plain text", encoding="utf-8")
    root_json_path = project.root / "settings.json"
    root_json_path.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        Project,
        "_build_registry",
        lambda self, *, profile=None: (_ for _ in ()).throw(AssertionError("registry must not be built")),
    )

    assert project.source_form(root_json_path) is None

    _install_source_form_family(monkeypatch, object())
    assert project.source_form(text_path) is None
    assert project.source_form(source_path) is None

    family = _SourceFormFamily(None)
    _install_source_form_family(monkeypatch, family)
    assert project.source_form(source_path) is None
    assert family.calls[0]["text"] == source_path.read_text(encoding="utf-8")

    registry = _install_source_form_family(monkeypatch, object(), error=ValueError("unknown family"))
    assert project.source_form(source_path) is None
    assert registry.calls == ["idea"]


@pytest.mark.parametrize(
    "relative_path",
    [
        "common/example/first.txt",
        "fragment.pdx",
        "interface/example.gui",
    ],
)
def test_project_source_form_projects_any_registry_owned_pdx_source(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    relative_path: str,
) -> None:
    project = Project.create(
        tmp_path / "multi-pdx-mod",
        project_id="multi_pdx_mod",
        title="Multi PDX Mod",
    )
    source_path = project.root / "src/modules/example/EXAMPLE_MULTI" / Path(relative_path)
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_text = "enabled = yes\nvalue = 3\n"
    source_path.write_text(source_text, encoding="utf-8")
    _install_source_form_family(monkeypatch, _MultiPdxSourceFormFamily())

    payload = project.source_form(source_path)

    assert payload is not None
    assert payload["source_format"] == "pdx"
    assert payload["module_id"] == "example/EXAMPLE_MULTI"
    assert payload["module_relative_path"] == relative_path
    assert [(control["label"], control["value"]) for control in _source_form_controls(payload)] == [("Enabled", True), ("Value", 3)]


def test_project_source_form_does_not_hide_registry_construction_failures(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project, source_path, _disk_text = _source_form_project(tmp_path)

    def fail_registry(self: Project, *, profile: str | None = None) -> object:
        raise ProjectManifestError("project family registry is invalid")

    monkeypatch.setattr(Project, "_build_registry", fail_registry)

    with pytest.raises(ProjectManifestError, match="project family registry is invalid"):
        project.source_form(source_path)


@pytest.mark.parametrize(
    ("raw_form", "message"),
    [
        (
            _single_control_form(
                {
                    "id": "missing",
                    "label": "Missing",
                    "control": "readonly",
                    "value": None,
                }
            ),
            "must be a finite JSON string, number, or boolean scalar",
        ),
        (
            _single_control_form(
                {
                    "id": "kind",
                    "label": "Kind",
                    "control": "choice",
                    "value": "armor",
                    "choices": ["infantry", "armor"],
                    "patch": {"op": "replace-json-scalar", "path": ["kind"]},
                }
            ),
            "choices[0] must be an object",
        ),
        (
            _single_control_form(
                {
                    "id": "title",
                    "label": "Title",
                    "control": "text",
                    "value": "Example",
                    "patch": {"op": "replace-json-scalar", "path": [" "]},
                }
            ),
            "path[0] must be a non-empty string or non-negative integer",
        ),
        (
            _single_control_form(
                {
                    "id": "title",
                    "label": "Title",
                    "control": "readonly",
                    "value": "Example",
                },
                section_label={"zh": "主要"},
            ),
            "localized text must define a non-empty default value",
        ),
        (
            _single_control_form(
                {
                    "id": "enabled",
                    "label": "Enabled",
                    "control": "boolean",
                    "value": True,
                    "placeholder": "Not allowed",
                    "patch": {"op": "replace-json-scalar", "path": ["enabled"]},
                }
            ),
            "placeholder is only valid for text, number, or choice controls",
        ),
        (
            _single_control_form(
                {
                    "id": "kind",
                    "label": "Kind",
                    "control": "choice",
                    "value": "armor",
                    "choices": [
                        {"label": "Armor", "value": "armor"},
                        {"label": "Disabled", "value": False},
                    ],
                    "patch": {"op": "replace-json-scalar", "path": ["kind"]},
                }
            ),
            "choices must use the same JSON scalar kind",
        ),
    ],
)
def test_project_source_form_rejects_invalid_provider_contracts_with_source_context(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    raw_form: dict[str, object],
    message: str,
) -> None:
    project, source_path, disk_text = _source_form_project(tmp_path)
    _install_source_form_family(monkeypatch, _SourceFormFamily(raw_form))

    with pytest.raises(ValueError) as captured:
        project.source_form(source_path)

    assert "Invalid source form 'src/modules/idea/GER_guided/record.json'" in str(captured.value)
    assert message in str(captured.value)
    assert source_path.read_text(encoding="utf-8") == disk_text


def test_project_source_form_preflights_editor_text_before_calling_provider(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project, source_path, disk_text = _source_form_project(tmp_path)
    family = _SourceFormFamily(_rich_source_form())
    _install_source_form_family(monkeypatch, family)

    with pytest.raises(ValueError, match="Invalid JSON source draft"):
        project.source_form(source_path, text='{"title":')
    assert family.calls == []

    monkeypatch.setattr(project_sdk, "MAX_PROJECT_SOURCE_TEXT_BYTES", 3)
    with pytest.raises(ValueError, match="larger than the 3-byte editor limit"):
        project.source_form(source_path, text="éé")
    assert family.calls == []
    assert source_path.read_text(encoding="utf-8") == disk_text


@pytest.mark.parametrize(
    ("editor_text", "message"),
    [
        ('{"title":"first","title":"second"}', "duplicate JSON object key 'title' is not allowed"),
        ('{"mesh":{"scale":1e400}}', "non-finite JSON number '1e400' is not allowed"),
        ('{"mesh":{"scale":' + "1" + ("0" * 400) + "}}", "non-finite JSON number"),
    ],
)
def test_project_source_form_rejects_json_the_exact_token_editor_cannot_patch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    editor_text: str,
    message: str,
) -> None:
    project, source_path, disk_text = _source_form_project(tmp_path)
    family = _SourceFormFamily(_rich_source_form())
    _install_source_form_family(monkeypatch, family)

    with pytest.raises(ValueError, match=message):
        project.source_form(source_path, text=editor_text)

    assert family.calls == []
    assert source_path.read_text(encoding="utf-8") == disk_text


def test_project_source_form_contextualizes_family_provider_failures(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project, source_path, _disk_text = _source_form_project(tmp_path)
    _install_source_form_family(monkeypatch, _SourceFormFamily(RuntimeError("idea provider crashed")))

    with pytest.raises(ValueError) as captured:
        project.source_form(source_path)

    assert str(captured.value) == "Invalid source form 'src/modules/idea/GER_guided/record.json': idea provider crashed"
    assert isinstance(captured.value.__cause__, RuntimeError)


@pytest.mark.parametrize(
    ("family_id", "source_text", "expected_values"),
    [
        (
            "idea",
            ("ideas = { country = { IDEA_TEST = { picture = IDEA_TEST " "removal_cost = -1 allowed_civil_war = { always = yes } } } }"),
            [("Picture", "IDEA_TEST"), ("Removal cost", -1), ("Always", True)],
        ),
        (
            "character",
            (
                "characters = { CHARACTER_TEST = { name = CHARACTER_TEST_NAME "
                'portraits = { civilian = { large = "gfx/leaders/test.dds" } } '
                "gender = male } }"
            ),
            [
                ("Name", "CHARACTER_TEST_NAME"),
                ("Gender", "male"),
                ("Large", "gfx/leaders/test.dds"),
            ],
        ),
        (
            "event",
            (
                "add_namespace = TEST country_event = { id = TEST.1 "
                "is_triggered_only = yes option = { ai_chance = { factor = 10 } } "
                "option = { ai_chance = { factor = 20 } } }"
            ),
            [
                ("Add namespace", "TEST"),
                ("Id", "TEST.1"),
                ("Is triggered only", True),
                ("Factor", 10),
                ("Factor", 20),
            ],
        ),
        (
            "equipment",
            ("equipments = { EQUIPMENT_TEST = { year = 1936 " "is_archetype = no active = yes group_by = archetype } }"),
            [
                ("Year", 1936),
                ("Is archetype", False),
                ("Active", True),
                ("Group by", "archetype"),
            ],
        ),
    ],
)
def test_project_source_form_projects_representative_pdx_def_scalars_without_writing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    family_id: str,
    source_text: str,
    expected_values: list[tuple[str, object]],
) -> None:
    project = Project.create(
        tmp_path / f"{family_id}-guided-mod",
        project_id=f"{family_id}_guided_mod",
        title=f"{family_id.title()} Guided Mod",
    )
    source_path = project.root / "src" / "modules" / family_id / f"{family_id.upper()}_TEST" / "def.txt"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text(source_text, encoding="utf-8")
    _install_source_form_family(monkeypatch, _PdxSourceFormFamily())

    payload = project.source_form(source_path, text=source_text)

    assert payload is not None
    assert payload["source_format"] == "pdx"
    assert payload["contract"] == "paradev.pdx.guided-form.v1"
    controls = _source_form_controls(payload)
    assert [(str(control["label"]), control["value"]) for control in controls] == expected_values
    assert all(control["description_source"] == "generated" for control in controls)
    assert all(control.get("description") for control in controls)
    assert all(isinstance(control.get("patch"), dict) and control["patch"]["op"] == "replace-pdx-scalar" for control in controls)
    assert source_path.read_text(encoding="utf-8") == source_text


def test_project_source_form_projects_and_updates_lossless_localization_text(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project = Project.create(tmp_path / "loc-guided-mod", project_id="loc_guided_mod", title="Localization Guided Mod")
    source_path = project.root / "src/modules/idea/IDEA_TEST/main.loc"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_text = (
        "[en.IDEA_TEST]\r\n"
        "Old 😀 title\r\n"
        "\r\n"
        "[en.IDEA_TEST_desc]\r\n"
        "[GetCountryName]\r\n"
        "Second line.\r\n"
        "\r\n"
        "[zh.IDEA_TEST]\r\n"
        "旧标题\r\n"
    )
    source_path.write_bytes(source_text.encode("utf-8"))
    _install_source_form_family(monkeypatch, _LocSourceFormFamily())

    payload = project.source_form(source_path)

    assert payload is not None
    assert payload["source_format"] == "loc"
    assert payload["contract"] == "paradev.localization.text-form.v1"
    assert payload["coverage"] == {
        "truncated": False,
        "shown_controls": 3,
        "total_controls": 3,
    }
    controls = _source_form_controls(payload)
    assert [control["value"] for control in controls] == [
        "Old 😀 title",
        "[GetCountryName]\nSecond line.",
        "旧标题",
    ]
    assert all(control["multiline"] is True for control in controls)
    first_patch = controls[0]["patch"]
    assert first_patch["path"] == {
        "language": "l_english",
        "key": "IDEA_TEST",
        "occurrence": 0,
    }
    assert first_patch["newline"] == "\r\n"
    assert first_patch["span"]["start"] == _utf16_length(source_text[: source_text.index("Old")])
    assert first_patch["source_length"] == _utf16_length(source_text)

    plan = project.plan_source_form_update(
        source_path,
        {
            "loc-control-000": "New title",
            "loc-control-001": "[GetCountryName]\nAnother line.",
        },
    )

    assert plan["changed"] is True
    assert plan["source_format"] == "loc"
    assert plan["source_edit"]["text"] == source_text.replace(
        "Old 😀 title",
        "New title",
    ).replace(
        "[GetCountryName]\r\nSecond line.",
        "[GetCountryName]\r\nAnother line.",
    )
    assert source_path.read_bytes() == source_text.encode("utf-8")


def test_project_source_form_localization_inline_empty_and_syntax_guards(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project = Project.create(tmp_path / "loc-inline-mod", project_id="loc_inline_mod", title="Localization Inline Mod")
    source_path = project.root / "src/modules/idea/IDEA_TEST/main.loc"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text("[en]\nIDEA_TEST=Old title\nIDEA_TEST_desc=\n", encoding="utf-8")
    _install_source_form_family(monkeypatch, _LocSourceFormFamily())

    payload = project.source_form(source_path)

    assert payload is not None
    controls = _source_form_controls(payload)
    assert [control["value"] for control in controls] == ["Old title", ""]
    assert all(control["multiline"] is False for control in controls)
    assert controls[1]["patch"]["span"]["start"] == controls[1]["patch"]["span"]["end"]
    plan = project.plan_source_form_update(source_path, {"loc-control-001": "New description"})
    assert plan["source_edit"]["text"] == "[en]\nIDEA_TEST=Old title\nIDEA_TEST_desc=New description\n"

    with pytest.raises(ValueError, match="must stay on one line"):
        project.plan_source_form_update(source_path, {"loc-control-000": "Line one\nLine two"})
    section_text = "[en.IDEA_TEST]\nOld title\n"
    source_path.write_text(section_text, encoding="utf-8")
    with pytest.raises(ValueError, match="contains a source section header"):
        project.plan_source_form_update(source_path, {"loc-control-000": "Safe\n[en.INJECTED]\nUnsafe"})


def test_project_source_form_updates_registry_owned_hoi4_yml_localization(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project = Project.create(tmp_path / "loc-yml-mod", project_id="loc_yml_mod", title="Localization YML Mod")
    source_path = project.root / "src/modules/idea/IDEA_TEST/main.yml"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_text = 'l_english:\r\n IDEA_TEST:0 "Old \\"title\\""\r\n'
    source_path.write_bytes(source_text.encode("utf-8"))
    _install_source_form_family(monkeypatch, _YmlLocSourceFormFamily())

    payload = project.source_form(source_path)

    assert payload is not None
    assert payload["source_format"] == "loc"
    controls = _source_form_controls(payload)
    assert controls[0]["value"] == 'Old "title"'
    assert controls[0]["patch"]["style"] == "yaml"

    plan = project.plan_source_form_update(
        source_path,
        {"loc-control-000": 'New "title" at C:\\path'},
    )

    assert plan["source_edit"]["text"] == ('l_english:\r\n IDEA_TEST:0 "New \\"title\\" at C:\\\\path"\r\n')
    assert source_path.read_bytes() == source_text.encode("utf-8")


def test_project_source_form_localization_is_bounded_and_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project = Project.create(tmp_path / "loc-bounded-mod", project_id="loc_bounded_mod", title="Localization Bounded Mod")
    source_path = project.root / "src/modules/idea/IDEA_TEST/main.loc"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_text = "\n".join(f"[en.KEY_{index}]\nValue {index}\n" for index in range(MAX_LOC_SOURCE_FORM_CONTROLS + 1))
    source_path.write_text(source_text, encoding="utf-8")
    _install_source_form_family(monkeypatch, _LocSourceFormFamily())

    payload = project.source_form(source_path)

    assert payload is not None
    assert payload["coverage"] == {
        "truncated": True,
        "shown_controls": MAX_LOC_SOURCE_FORM_CONTROLS,
        "total_controls": MAX_LOC_SOURCE_FORM_CONTROLS + 1,
    }
    assert len(_source_form_controls(payload)) == MAX_LOC_SOURCE_FORM_CONTROLS

    queried = project.source_form(source_path, query=f"KEY_{MAX_LOC_SOURCE_FORM_CONTROLS}")
    assert queried is not None
    assert queried["query"] == f"KEY_{MAX_LOC_SOURCE_FORM_CONTROLS}"
    assert queried["coverage"] == {
        "truncated": False,
        "shown_controls": 1,
        "total_controls": 1,
    }
    queried_controls = _source_form_controls(queried)
    assert queried_controls[0]["id"] == f"loc-control-{MAX_LOC_SOURCE_FORM_CONTROLS:03d}"
    assert queried_controls[0]["value"] == f"Value {MAX_LOC_SOURCE_FORM_CONTROLS}"
    plan = project.plan_source_form_update(
        source_path,
        {queried_controls[0]["id"]: "Late value"},
        query=f"KEY_{MAX_LOC_SOURCE_FORM_CONTROLS}",
    )
    assert f"[en.KEY_{MAX_LOC_SOURCE_FORM_CONTROLS}]\nLate value\n" in plan["source_edit"]["text"]

    no_matches = project.source_form(source_path, query="NO_SUCH_LOCALIZATION_KEY")
    assert no_matches is not None
    assert no_matches["coverage"] == {
        "truncated": False,
        "shown_controls": 0,
        "total_controls": 0,
    }
    assert no_matches["sections"] == []

    source_path.write_text("[en\nKEY=broken\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Localization source line 1 is invalid: invalid line"):
        project.source_form(source_path)


def test_project_source_form_uses_registry_family_owned_pdx_field_help(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project = Project.create(tmp_path / "equipment-help", project_id="equipment_help", title="Equipment Help")
    source_path = project.root / "src/modules/equipment/EQUIPMENT_TEST/def.txt"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_text = "equipments = { EQUIPMENT_TEST = { year = 1936 active = yes } }"
    source_path.write_text(source_text, encoding="utf-8")
    _install_source_form_family(monkeypatch, _HintedPdxSourceFormFamily())

    payload = project.source_form(source_path)

    assert payload is not None
    controls = _source_form_controls(payload)
    assert controls[0]["label"] == {"default": "Production year", "zh": "投产年份"}
    assert controls[0]["description_source"] == "declared"
    assert controls[0]["description"] == {
        "default": "Technology year used for equipment availability.",
        "zh": "用于装备可用性的科技年份。",
    }
    assert controls[1]["description_source"] == "generated"
    assert controls[1]["description"]["default"].endswith("equipments › EQUIPMENT_TEST › active.")


def test_project_source_form_rejects_malformed_registry_pdx_field_help(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    class MalformedHintFamily(_PdxSourceFormFamily):
        source_form_field_hints = {"year": {"choices": [1936]}}

    project = Project.create(tmp_path / "bad-help", project_id="bad_help", title="Bad Help")
    source_path = project.root / "src/modules/equipment/EQUIPMENT_TEST/def.txt"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text("year = 1936", encoding="utf-8")
    _install_source_form_family(monkeypatch, MalformedHintFamily())

    with pytest.raises(ValueError, match="contains unsupported fields: choices"):
        project.source_form(source_path)


def test_project_source_form_pdx_paths_keep_duplicate_occurrences_and_utf16_exact_spans(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project = Project.create(tmp_path / "pdx-span-mod", project_id="pdx_span_mod", title="PDX Span Mod")
    source_path = project.root / "src/modules/event/TEST/def.txt"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_text = "# 😀 retained comment\r\n" "country_event = {\r\n" "  option = { factor = 10 }\r\n" "  option = { factor = 20 }\r\n" "}\r\n"
    source_path.write_text(source_text, encoding="utf-8")
    _install_source_form_family(monkeypatch, _PdxSourceFormFamily())

    payload = project.source_form(source_path, text=source_text)

    assert payload is not None
    factors = [control for control in _source_form_controls(payload) if str(control["label"]).startswith("Factor")]
    assert len(factors) == 2
    first_patch = factors[0]["patch"]
    second_patch = factors[1]["patch"]
    assert isinstance(first_patch, dict)
    assert isinstance(second_patch, dict)
    assert first_patch["path"] == [
        {"key": "country_event", "occurrence": 0},
        {"key": "option", "occurrence": 0},
        {"key": "factor", "occurrence": 0},
    ]
    assert second_patch["path"] == [
        {"key": "country_event", "occurrence": 0},
        {"key": "option", "occurrence": 1},
        {"key": "factor", "occurrence": 0},
    ]
    span = first_patch["span"]
    assert isinstance(span, dict)
    assert span["start"] == _utf16_length(source_text[: source_text.index("10")])
    assert span["end"] - span["start"] == 2
    assert first_patch["source_length"] == _utf16_length(source_text)
    assert first_patch["expected"] == "10"


def test_project_source_form_pdx_fails_closed_for_malformed_text_and_complexity(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project = Project.create(tmp_path / "pdx-guard-mod", project_id="pdx_guard_mod", title="PDX Guard Mod")
    source_path = project.root / "src/modules/idea/TEST/def.txt"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text("value =", encoding="utf-8")
    _install_source_form_family(monkeypatch, _PdxSourceFormFamily())

    with pytest.raises(
        ValueError,
        match=r"Invalid source form 'src/modules/idea/TEST/def.txt'.*requires a value",
    ):
        project.source_form(source_path)

    complex_text = "\n".join(f"value = {index}" for index in range(MAX_PDX_SOURCE_FORM_CONTROLS + 1))
    source_path.write_text(complex_text, encoding="utf-8")
    payload = project.source_form(source_path)
    assert payload is not None
    assert payload["coverage"] == {
        "truncated": True,
        "shown_controls": MAX_PDX_SOURCE_FORM_CONTROLS,
        "total_controls": MAX_PDX_SOURCE_FORM_CONTROLS + 1,
    }
    assert len(_source_form_controls(payload)) == MAX_PDX_SOURCE_FORM_CONTROLS


def test_source_form_patch_contract_discriminates_pdx_spans_from_json_paths() -> None:
    pdx_patch = {
        "op": "replace-pdx-scalar",
        "path": [{"key": "option", "occurrence": 1}],
        "span": {"start": 4, "end": 7},
        "expected": "yes",
        "scalar_kind": "boolean",
        "source_length": 10,
    }

    assert normalize_source_form_patch(pdx_patch, "patch") == pdx_patch
    with pytest.raises(ValueError, match="span length must match expected"):
        normalize_source_form_patch(
            {**pdx_patch, "span": {"start": 4, "end": 8}},
            "patch",
        )
    with pytest.raises(ValueError, match="contains unsupported fields"):
        normalize_source_form_patch(
            {**pdx_patch, "path": [{"key": "option", "occurrence": 1, "index": 2}]},
            "patch",
        )

    list_patch = {
        "op": "replace-pdx-integer-list",
        "path": [{"key": "provinces", "occurrence": 0}],
        "span": {"start": 2, "end": 7},
        "expected": " 1 2 ",
        "item_kind": "integer",
        "columns": 1,
        "minimum": 1,
        "layout": {
            "prefix": " ",
            "column_separator": " ",
            "row_separator": " ",
            "suffix": " ",
        },
        "source_length": 9,
    }
    assert normalize_source_form_patch(list_patch, "patch") == list_patch
    with pytest.raises(ValueError, match="exactly 2 integers per row"):
        normalize_source_form_patch(
            {**list_patch, "columns": 2, "expected": " 1 2 3 ", "span": {"start": 0, "end": 7}},
            "patch",
        )

    block_patch = {
        "op": "replace-pdx-block-body",
        "path": [{"key": "MY_EFFECT", "occurrence": 0}],
        "span": {"start": 2, "end": 2},
        "expected": "",
        "layout": {
            "prefix": "\n    ",
            "line_prefix": "\n    ",
            "suffix": "\n",
        },
        "source_length": 4,
    }
    assert normalize_source_form_patch(block_patch, "patch") == block_patch
    escaping_body = "}\nOTHER = { always = yes "
    with pytest.raises(ValueError, match="must remain inside one PDX block"):
        normalize_source_form_patch(
            {
                **block_patch,
                "span": {"start": 0, "end": len(escaping_body)},
                "expected": escaping_body,
                "source_length": len(escaping_body),
            },
            "patch",
        )


def test_source_form_rest_facade_openapi_and_frontend_planner(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = {"schema": "paradev.source-form.v1", "contract": "pihc2.idea.record.v1", "sections": []}
    calls: list[dict[str, object]] = []

    class FakeProject:
        def source_form(
            self,
            source_path: str,
            *,
            text: str | None = None,
            query: str | None = None,
        ) -> dict[str, object]:
            calls.append({"source_path": source_path, "text": text, "query": query})
            return expected

    monkeypatch.setattr(
        project_api,
        "_project",
        lambda project_id, project_root: calls.append({"project_id": project_id, "project_root": project_root}) or FakeProject(),
    )
    result = rest_surface.read_project_source_form(
        project_id="guided_mod",
        request={
            "project_root": "/workspace/guided-mod",
            "path": "src/modules/idea/GER_guided/record.json",
            "text": "{}",
            "query": "C01_C02_GREENLIGHT.40",
        },
    )

    assert result == expected
    assert calls == [
        {"project_id": "guided_mod", "project_root": "/workspace/guided-mod"},
        {
            "source_path": "src/modules/idea/GER_guided/record.json",
            "text": "{}",
            "query": "C01_C02_GREENLIGHT.40",
        },
    ]
    with pytest.raises(ValueError, match="Request field 'text' must be a string"):
        rest_surface.read_project_source_form(
            project_id="guided_mod",
            request={"path": "src/modules/idea/GER_guided/record.json", "text": False},
        )
    with pytest.raises(ValueError, match="contains unsupported fields: projectRoot"):
        rest_surface.read_project_source_form(
            project_id="guided_mod",
            request={
                "path": "src/modules/idea/GER_guided/record.json",
                "projectRoot": "/workspace/guided-mod",
            },
        )

    with pytest.raises(ValueError, match="Request field 'text' must be a string"):
        rest_surface.read_project_source_form(
            project_id="guided_mod",
            request={"path": "src/modules/idea/GER_guided/record.json", "text": None},
        )
    with pytest.raises(ValueError, match="Request field 'text' must be a string"):
        rest_surface.read_project_source_form(
            project_id="guided_mod",
            request={"path": "src/modules/idea/GER_guided/record.json"},
        )

    operation = rest_surface.get_openapi_seed()["paths"][rest_surface.SOURCE_FORM_PATH]["post"]
    assert operation["parameters"] == [{"name": "project_id", "in": "path", "required": True, "schema": {"type": "string"}}]
    body_schema = operation["requestBody"]["content"]["application/json"]["schema"]
    assert body_schema["required"] == ["path", "text"]
    assert body_schema["additionalProperties"] is False
    assert body_schema["properties"] == {
        "project_root": {"type": ["string", "null"]},
        "path": {"type": "string"},
        "text": {"type": "string"},
        "query": {"type": "string", "maxLength": 200},
    }

    plan = plan_frontend_api_rest_request(
        "project.source_form",
        {
            "project_id": "guided_mod",
            "path": "/workspace/guided-mod",
            "source_path": "src/modules/idea/GER_guided/record.json",
            "text": "{}",
            "query": "C01_C02_GREENLIGHT.40",
        },
    )
    assert plan["method"] == "POST"
    assert plan["path"] == "/projects/guided_mod/sources/form"
    assert plan["query"] == {}
    assert plan["body"] == {
        "project_root": "/workspace/guided-mod",
        "path": "src/modules/idea/GER_guided/record.json",
        "text": "{}",
        "query": "C01_C02_GREENLIGHT.40",
    }
    with pytest.raises(ValueError, match="Missing required frontend API inputs for project.source_form: text"):
        plan_frontend_api_rest_request(
            "project.source_form",
            {
                "project_id": "guided_mod",
                "path": "/workspace/guided-mod",
                "source_path": "src/modules/idea/GER_guided/record.json",
            },
        )

    assert public_api.read_project_source_form is rest_surface.read_project_source_form
    row = next(row for row in public_api.get_rest_facade_api_table()["rows"] if row["symbol"] == "read_project_source_form")
    assert row["feature"] == "project-sources"
    assert row["registry_seam"] == "REST project source bridge"


def test_source_form_fastapi_route_returns_payload_null_and_contextual_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    from fastapi.testclient import TestClient

    expected = {"schema": "paradev.source-form.v1", "contract": "pihc2.idea.record.v1", "sections": []}
    calls: list[dict[str, object]] = []

    def source_form(*, project_id: str, request: dict[str, object]) -> dict[str, object] | None:
        calls.append({"project_id": project_id, "request": request})
        return expected

    monkeypatch.setattr(rest_surface, "read_project_source_form", source_form)
    client = TestClient(rest_surface.build_app())
    request = {"path": "src/modules/idea/GER_guided/record.json", "text": "{}"}

    response = client.post("/projects/guided_mod/sources/form", json=request)

    assert response.status_code == 200
    assert response.json() == expected
    assert calls == [{"project_id": "guided_mod", "request": request}]

    monkeypatch.setattr(rest_surface, "read_project_source_form", lambda **_kwargs: None)
    unsupported = client.post("/projects/guided_mod/sources/form", json=request)
    assert unsupported.status_code == 200
    assert unsupported.json() is None

    def invalid_form(**_kwargs: object) -> None:
        raise ValueError("Invalid source form 'record.json': bad patch")

    monkeypatch.setattr(rest_surface, "read_project_source_form", invalid_form)
    invalid = client.post("/projects/guided_mod/sources/form", json=request)
    assert invalid.status_code == 400
    assert invalid.json()["detail"] == "Invalid source form 'record.json': bad patch"


def _source_form_controls(payload: dict[str, object]) -> list[dict[str, object]]:
    sections = payload.get("sections")
    assert isinstance(sections, list)
    controls: list[dict[str, object]] = []
    stack = list(sections)
    while stack:
        section = stack.pop(0)
        assert isinstance(section, dict)
        rows = section.get("controls", [])
        assert isinstance(rows, list)
        controls.extend(row for row in rows if isinstance(row, dict))
        children = section.get("sections", [])
        assert isinstance(children, list)
        stack.extend(children)
    return controls


def _utf16_length(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2
