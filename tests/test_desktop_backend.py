from __future__ import annotations

import base64
import platform
import subprocess
import sys
from io import StringIO
from pathlib import Path

import heavenbase
import pytest
from heavenbase.utils import dumps_json, loads_json, loads_yaml

import paradev
from paradev.desktop import backend
from paradev.sdk import get_project_inspection_contract
from paradev.sdk._module_diagram_api import (
    MAX_MODULE_DIAGRAM_NODE_INTENTS,
    MAX_MODULE_DIAGRAM_POSITION_INTENTS,
)

EXPECTED_DESKTOP_OPERATIONS = {
    "apply_project_draft",
    "collection_remove",
    "collection_rename",
    "collection_scaffold",
    "create_module_batch",
    "create_module_draft",
    "desktop_chat",
    "desktop_chat_profiles",
    "desktop_dependency_status",
    "desktop_hoi4_launch_readiness",
    "desktop_install_dependency",
    "desktop_install_project_package",
    "desktop_open_path",
    "desktop_path_status",
    "desktop_project_build_command",
    "desktop_project_package_catalog",
    "desktop_read_app_config",
    "desktop_read_binary_source",
    "desktop_read_config_value",
    "desktop_read_text_source",
    "desktop_read_thumbnail_cache",
    "desktop_reset_chat_profile",
    "desktop_run_hoi4",
    "desktop_state",
    "desktop_test_llm_route",
    "desktop_write_app_config",
    "desktop_write_browser_cache",
    "desktop_write_chat_profile",
    "desktop_write_config_value",
    "desktop_write_thumbnail_cache",
    "duplicate_module",
    "module_batch_request",
    "module_diagram",
    "module_diagram_edit",
    "module_collection_set",
    "module_activity_set",
    "project_browser",
    "project_catalog_query",
    "project_catalog_status",
    "project_catalog_refresh",
    "project_inspect",
    "project_localization_update",
    "project_localization_workspace",
    "project_preferred_language",
    "project_source_form",
    "project_source_form_update_batch",
    "read_project_browser_cache",
    "remove_module",
    "rename_module",
}


def test_project_preferred_language_delegates_guarded_plan_apply(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = {"schema": "paradev.project.preferred-language.v1"}
    calls: list[object] = []

    class StubProject:
        def set_preferred_language(
            self,
            preferred_language: str,
            *,
            write: bool = False,
            plan_hash: str | None = None,
        ) -> dict[str, object]:
            calls.append((preferred_language, write, plan_hash))
            return expected

    monkeypatch.setattr(
        backend,
        "open_project",
        lambda path: calls.append(("open", path)) or StubProject(),
    )
    request = dumps_json(
        {
            "projectRoot": " /workspace/PIHC3 ",
            "preferredLanguage": " zh ",
            "write": True,
            "planHash": f" {'a' * 64} ",
        },
        compact=True,
    )

    assert backend._desktop_call(_call_request("project_preferred_language", [request])) is expected
    assert calls == [
        ("open", "/workspace/PIHC3"),
        ("zh", True, "a" * 64),
    ]


@pytest.mark.parametrize(
    ("request_payload", "message"),
    [
        ({}, "project preferred-language projectRoot cannot be empty."),
        (
            {"projectRoot": "/tmp/PIHC3", "preferredLanguage": "zh", "write": "yes"},
            "project preferred-language write must be a JSON boolean or null.",
        ),
        (
            {"projectRoot": "/tmp/PIHC3", "preferredLanguage": "zh", "force": True},
            "project preferred-language request contains unsupported fields: force.",
        ),
    ],
)
def test_project_preferred_language_rejects_noncanonical_bridge_requests(
    request_payload: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(ValueError) as error:
        backend._set_project_preferred_language(dumps_json(request_payload, compact=True))
    assert str(error.value) == message


def test_module_rename_forwards_optional_readable_title(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[object] = []
    expected = {"schema": "paradev.module.rename.v1"}

    class StubProject:
        def rename_module(
            self,
            module_id: str,
            object_id: str,
            **kwargs: object,
        ) -> dict[str, object]:
            calls.append((module_id, object_id, kwargs))
            return expected

    monkeypatch.setattr(
        backend,
        "open_project",
        lambda path: calls.append(("open", path)) or StubProject(),
    )

    payload = backend._rename_module(
        dumps_json(
            {
                "projectRoot": "/workspace/PIHC3",
                "moduleId": "idea/IDEA_OLD",
                "objectId": "IDEA_NEW",
                "sourceRoot": "src",
                "title": "New Idea",
            }
        )
    )

    assert payload == expected
    assert calls == [
        ("open", "/workspace/PIHC3"),
        (
            "idea/IDEA_OLD",
            "IDEA_NEW",
            {"source_root": "src", "title": "New Idea"},
        ),
    ]


def test_collection_scaffold_maps_reviewed_request_to_sdk(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[object, ...]] = []
    expected = {"schema": "paradev.sdk.collection_scaffold.v1"}

    class StubProject:
        def scaffold_collection(
            self,
            template_id: str,
            collection_id: str,
            **kwargs: object,
        ) -> dict[str, object]:
            calls.append((template_id, collection_id, kwargs))
            return expected

    monkeypatch.setattr(
        backend,
        "open_project",
        lambda path: calls.append(("open", path)) or StubProject(),
    )
    request = dumps_json(
        {
            "projectRoot": "/workspace/PIHC3",
            "templateId": "pihc3:focus-tree/basic",
            "collectionId": "C01_NEW",
            "values": {"title": "新国策树", "country_tag": "C01"},
            "sourceRoot": "/workspace/PIHC3/src",
            "write": True,
            "force": False,
            "planHash": "a" * 64,
        },
        compact=True,
    )

    assert backend._desktop_call(_call_request("collection_scaffold", [request])) is expected
    assert calls == [
        ("open", "/workspace/PIHC3"),
        (
            "pihc3:focus-tree/basic",
            "C01_NEW",
            {
                "source_root": "/workspace/PIHC3/src",
                "values": {
                    "title": "新国策树",
                    "country_tag": "C01",
                },
                "write": True,
                "force": False,
                "plan_hash": "a" * 64,
            },
        ),
    ]


def test_collection_scaffold_rejects_non_object_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    opened = False

    def fail_open(_path: str) -> object:
        nonlocal opened
        opened = True
        raise AssertionError("invalid request must not open a project")

    monkeypatch.setattr(backend, "open_project", fail_open)
    request = dumps_json(
        {
            "projectRoot": "/workspace/PIHC3",
            "templateId": "pihc3:focus-tree/basic",
            "collectionId": "C01_NEW",
            "values": [],
        },
        compact=True,
    )

    with pytest.raises(ValueError, match="values must be a JSON object"):
        backend._collection_scaffold(request)
    assert opened is False


def test_collection_rename_maps_exact_identity_to_sdk(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[object] = []
    expected = {"schema": "paradev.collection.rename.v1"}

    class StubProject:
        def rename_collection(
            self,
            collection_id: str,
            target_id: str,
            **kwargs: object,
        ) -> dict[str, object]:
            calls.append((collection_id, target_id, kwargs))
            return expected

    monkeypatch.setattr(
        backend,
        "open_project",
        lambda path: calls.append(("open", path)) or StubProject(),
    )

    payload = backend._rename_collection(
        dumps_json(
            {
                "projectRoot": "/workspace/PIHC3",
                "collectionId": "C01_OLD",
                "targetId": "C01_NEW",
                "family": "focus",
                "sourceRoot": "src",
            },
            compact=True,
        )
    )

    assert payload is expected
    assert calls == [
        ("open", "/workspace/PIHC3"),
        (
            "C01_OLD",
            "C01_NEW",
            {"family": "focus", "source_root": "src"},
        ),
    ]


def test_collection_remove_maps_guarded_plan_apply_to_sdk(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[object] = []
    expected = {"schema": "paradev.collection.remove.v1"}

    class StubProject:
        def remove_collection(
            self,
            collection_id: str,
            **kwargs: object,
        ) -> dict[str, object]:
            calls.append((collection_id, kwargs))
            return expected

    monkeypatch.setattr(
        backend,
        "open_project",
        lambda path: calls.append(("open", path)) or StubProject(),
    )

    payload = backend._remove_collection(
        dumps_json(
            {
                "projectRoot": "/workspace/PIHC3",
                "collectionId": "C01_OLD",
                "family": "focus",
                "sourceRoot": "src",
                "write": True,
                "planHash": "a" * 64,
            },
            compact=True,
        )
    )

    assert payload is expected
    assert calls == [
        ("open", "/workspace/PIHC3"),
        (
            "C01_OLD",
            {
                "family": "focus",
                "source_root": "src",
                "write": True,
                "plan_hash": "a" * 64,
            },
        ),
    ]


def test_desktop_project_package_install_rejects_desktop_version_drift(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        backend,
        "desktop_project_package_catalog",
        lambda: {"desktop_version": "1.2.3"},
    )
    install_called = False

    def fake_install(_archive: str, _destination: str) -> dict[str, object]:
        nonlocal install_called
        install_called = True
        return {}

    monkeypatch.setattr(backend, "desktop_install_project_package", fake_install)

    with pytest.raises(ValueError, match="targets ParaDev Desktop 1.2.3"):
        backend._desktop_install_project_package("/tmp/package.zip", "/tmp/projects", "9.9.9")

    assert install_called is False


def test_desktop_backend_create_module_batch_alias_uses_rest_sdk_contract(
    tmp_path: Path,
) -> None:
    project = paradev.Project.create(tmp_path / "starter")
    request = dumps_json(
        {
            "projectId": project.project_id,
            "projectRoot": str(project.root),
            "modules": [
                {
                    "family": "idea",
                    "object_id": "DESKTOP_IDEA",
                    "values": {"title": "Desktop Idea"},
                }
            ],
        },
        compact=True,
    )

    payload = backend._HELPERS["create_module_batch"](request)

    assert payload["schema"] == "paradev.sdk.module_batch.v1"
    assert payload["blocked"] is False
    assert payload["written"] is False
    assert payload["modules"][0]["module_id"] == "idea/DESKTOP_IDEA"


def test_backend_entry_file_runs_without_package_context(tmp_path) -> None:
    entrypoint = Path(__file__).resolve().parents[1] / "src" / "paradev" / "desktop" / "backend.py"

    result = subprocess.run(
        [sys.executable, str(entrypoint), "backend-info"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = loads_json(result.stdout)
    assert payload["schema"] == "paradev.desktop.backend-info.v1"
    assert payload["protocol"] == "paradev.desktop.backend.v1"


def test_backend_entry_file_round_trips_unicode_protocol_text(tmp_path) -> None:
    entrypoint = Path(__file__).resolve().parents[1] / "src" / "paradev" / "desktop" / "backend.py"
    unicode_path = tmp_path / "角色-测试"
    unicode_path.mkdir()
    request = dumps_json(
        {
            "protocol": backend.DESKTOP_BACKEND_PROTOCOL,
            "operation": "desktop_path_status",
            "args": [str(unicode_path)],
        },
        compact=True,
    ).encode("utf-8")

    result = subprocess.run(
        [sys.executable, str(entrypoint), "desktop-call"],
        cwd=tmp_path,
        input=request,
        check=False,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    payload = loads_json(result.stdout.decode("utf-8", errors="strict"))
    assert payload["path"] == str(unicode_path)
    assert payload["openable"] is True


def test_backend_protocol_redirects_noisy_helper_output_to_stderr(tmp_path) -> None:
    large_value = f"角色-{'x' * 200_000}"
    request = dumps_json(
        {
            "protocol": backend.DESKTOP_BACKEND_PROTOCOL,
            "operation": "noisy",
            "args": [large_value],
        },
        compact=True,
    ).encode("utf-8")
    script = (
        "from paradev.desktop import backend\n"
        "backend._HELPERS = {'noisy': lambda value: print('诊断噪声') or {'value': value}}\n"
        "raise SystemExit(backend.main(['desktop-call']))\n"
    )

    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=tmp_path,
        input=request,
        check=False,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    assert loads_json(result.stdout.decode("utf-8", errors="strict")) == {"value": large_value}
    assert result.stderr.decode("utf-8", errors="strict") == "诊断噪声\n"


def _call_request(operation: str, args: list[str]) -> StringIO:
    return StringIO(
        dumps_json(
            {
                "protocol": backend.DESKTOP_BACKEND_PROTOCOL,
                "operation": operation,
                "args": args,
            },
            compact=True,
        )
    )


def test_backend_info_reports_embedded_runtime(capsys) -> None:
    assert backend.main(["backend-info"]) == 0

    captured = capsys.readouterr()
    payload = loads_json(captured.out)
    assert captured.err == ""
    assert payload == {
        "schema": "paradev.desktop.backend-info.v1",
        "protocol": "paradev.desktop.backend.v1",
        "paradevVersion": paradev.__version__,
        "heavenbaseVersion": heavenbase.__version__,
        "pythonVersion": platform.python_version(),
        "platform": sys.platform,
        "platformVersion": platform.version(),
        "machine": platform.machine(),
    }


def test_desktop_call_accepts_current_string_arguments(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "stdin", _call_request("desktop_path_status", [str(tmp_path)]))

    assert backend.main(["desktop-call"]) == 0

    captured = capsys.readouterr()
    payload = loads_json(captured.out)
    assert captured.err == ""
    assert payload["schema"] == "paradev.desktop.path-status.v1"
    assert payload["path"] == str(tmp_path)
    assert payload["openable"] is True


def test_desktop_call_encodes_thumbnail_cache_miss_as_null(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    monkeypatch.setattr(
        sys,
        "stdin",
        _call_request(
            "desktop_read_thumbnail_cache",
            [str(project_root), "v1|ideas:IDEA_ALPHA|icon.png"],
        ),
    )

    assert backend.main(["desktop-call"]) == 0

    captured = capsys.readouterr()
    assert captured.err == ""
    assert loads_json(captured.out) is None


def test_desktop_call_carries_stdin_sized_payloads(monkeypatch, capsys, cm_paradev_lock) -> None:
    settings = {"schema": "paradev.desktop.app-settings.v1", "draft": "x" * 200_000}
    monkeypatch.setattr(
        sys,
        "stdin",
        _call_request("desktop_write_app_config", [dumps_json(settings, compact=True)]),
    )

    assert backend.main(["desktop-call"]) == 0
    assert loads_json(capsys.readouterr().out) is None

    monkeypatch.setattr(sys, "stdin", _call_request("desktop_read_app_config", []))
    assert backend.main(["desktop-call"]) == 0
    assert loads_json(capsys.readouterr().out) == settings


def test_desktop_build_plan_contains_only_forwarded_cli_arguments(monkeypatch, capsys, cm_paradev_lock) -> None:
    request = {
        "projectRoot": "/tmp/PIHC3",
        "mode": "full",
        "strictMetadata": False,
        "parallelism": 2,
    }
    monkeypatch.setattr(
        sys,
        "stdin",
        _call_request("desktop_project_build_command", [dumps_json(request, compact=True), ""]),
    )

    assert backend.main(["desktop-call"]) == 0

    captured = capsys.readouterr()
    args = loads_json(captured.out)
    assert captured.err == ""
    assert args[:2] == ["build", "/tmp/PIHC3"]
    assert args[-1] == "--json"
    assert "--full-rebuild" in args
    assert "--no-sync-launcher-descriptor" in args
    assert "uv" not in args
    assert "paradev" not in args


def test_desktop_state_delegates_raw_requests_to_the_sdk(monkeypatch) -> None:
    calls: list[tuple[str | None, bool]] = []
    expected = {"schema": "raw.desktop-state.v1", "projects": ["角色项目"]}

    def fake_desktop_state(project_root: str | None = None, *, include_browser: bool = True) -> dict[str, object]:
        calls.append((project_root, include_browser))
        return expected

    monkeypatch.setattr(backend, "desktop_state", fake_desktop_state)

    assert backend._desktop_state("{}") is expected
    assert backend._desktop_state('{"projectRoot":null,"includeBrowser":null}') is expected
    request = dumps_json({"projectRoot": "  /tmp/角色项目  ", "includeBrowser": False}, compact=True)
    assert backend._desktop_call(_call_request("desktop_state", [request])) is expected
    assert calls == [(None, True), (None, True), ("/tmp/角色项目", False)]


def test_project_draft_bridge_maps_source_revision_and_format_fields(
    monkeypatch,
) -> None:
    calls: list[tuple[str, dict[str, object]]] = []
    expected = {"schema": "raw.draft-apply.v1", "written": True}

    def fake_apply_project_draft(*, project_id: str, request: dict[str, object]) -> dict[str, object]:
        calls.append((project_id, request))
        return expected

    monkeypatch.setattr(backend, "apply_project_draft", fake_apply_project_draft)
    request = dumps_json(
        {
            "projectId": "PIHC3",
            "projectRoot": "/tmp/PIHC3",
            "sourceEdits": [
                {
                    "path": "/tmp/PIHC3/src/modules/idea/test/def.txt",
                    "text": "ideas = {}\n",
                    "expectedSize": 12,
                    "expectedMtimeNs": "1700000000000000000",
                }
            ],
            "sourceRemovals": [
                {
                    "path": "/tmp/PIHC3/src/modules/idea/test/old.loc",
                    "expectedSize": 64,
                    "expectedMtimeNs": "1700000000000000002",
                }
            ],
            "sourceReplacements": [
                {
                    "path": "/tmp/PIHC3/src/modules/idea/test/icon.dds",
                    "contentBase64": "cG5n",
                    "contentFormat": "png",
                    "targetFormat": "dds",
                    "expectedSize": 128,
                    "expectedMtimeNs": "1700000000000000001",
                }
            ],
            "moduleRename": {
                "moduleId": "idea/IDEA_ALPHA",
                "objectId": "IDEA_ALPHA",
                "sourceRoot": "/tmp/PIHC3/src",
                "title": "Readable Alpha",
            },
        },
        compact=True,
    )

    assert backend._apply_project_draft(request) is expected
    assert calls == [
        (
            "PIHC3",
            {
                "project_root": "/tmp/PIHC3",
                "source_edits": [
                    {
                        "path": "/tmp/PIHC3/src/modules/idea/test/def.txt",
                        "text": "ideas = {}\n",
                        "expected_size": 12,
                        "expected_mtime_ns": "1700000000000000000",
                    }
                ],
                "source_removals": [
                    {
                        "path": "/tmp/PIHC3/src/modules/idea/test/old.loc",
                        "expected_size": 64,
                        "expected_mtime_ns": "1700000000000000002",
                    }
                ],
                "source_replacements": [
                    {
                        "path": "/tmp/PIHC3/src/modules/idea/test/icon.dds",
                        "content_base64": "cG5n",
                        "content_format": "png",
                        "target_format": "dds",
                        "expected_size": 128,
                        "expected_mtime_ns": "1700000000000000001",
                    }
                ],
                "module_rename": {
                    "module_id": "idea/IDEA_ALPHA",
                    "object_id": "IDEA_ALPHA",
                    "source_root": "/tmp/PIHC3/src",
                    "title": "Readable Alpha",
                },
            },
        )
    ]


def test_project_draft_bridge_maps_expected_absence_and_rejects_unknown_fields(
    monkeypatch,
) -> None:
    calls: list[dict[str, object]] = []

    def fake_apply_project_draft(
        *,
        project_id: str,
        request: dict[str, object],
    ) -> dict[str, object]:
        assert project_id == "PIHC3"
        calls.append(request)
        return {"schema": "raw.draft-apply.v1", "written": True}

    monkeypatch.setattr(
        backend,
        "apply_project_draft",
        fake_apply_project_draft,
    )
    request = dumps_json(
        {
            "projectId": "PIHC3",
            "projectRoot": "/tmp/PIHC3",
            "sourceReplacements": [
                {
                    "path": "/tmp/PIHC3/src/modules/idea/test/new.png",
                    "contentBase64": "cG5n",
                    "expectedAbsent": True,
                }
            ],
        },
        compact=True,
    )

    backend._apply_project_draft(request)

    assert calls[0]["source_replacements"] == [
        {
            "path": "/tmp/PIHC3/src/modules/idea/test/new.png",
            "content_base64": "cG5n",
            "expected_absent": True,
        }
    ]

    with pytest.raises(ValueError, match="unsupported fields"):
        backend._apply_project_draft(
            dumps_json(
                {
                    "projectId": "PIHC3",
                    "projectRoot": "/tmp/PIHC3",
                    "sourceEdits": [
                        {
                            "path": "/tmp/PIHC3/src/modules/idea/test/def.txt",
                            "text": "ideas = {}",
                            "expected_size": 12,
                            "expected_mtime_ns": "1700000000000000000",
                        }
                    ],
                },
                compact=True,
            )
        )

    with pytest.raises(
        ValueError,
        match="sourceReplacements must be a JSON array",
    ):
        backend._apply_project_draft(
            dumps_json(
                {
                    "projectId": "PIHC3",
                    "projectRoot": "/tmp/PIHC3",
                    "sourceEdits": [
                        {
                            "path": "/tmp/PIHC3/src/modules/idea/test/def.txt",
                            "text": "ideas = {}",
                        }
                    ],
                    "sourceReplacements": {},
                },
                compact=True,
            )
        )


def test_project_draft_bridge_creates_title_only_metadata_with_absence_guard(
    tmp_path: Path,
) -> None:
    project = paradev.Project.create(tmp_path / "metadata-free")
    module_root = project.root / "src" / "modules" / "idea" / "IDEA_METADATA_FREE"
    module_root.mkdir(parents=True)
    (module_root / "def.pdx").write_text(
        "ideas = {}\n",
        encoding="utf-8",
    )
    metadata_path = module_root / "meta.yaml"
    title = 'Friendship: "魔法"'
    metadata_text = f"title: {dumps_json(title, ensure_ascii=False, compact=True)}\n"
    request = dumps_json(
        {
            "projectId": project.project_id,
            "projectRoot": str(project.root),
            "sourceReplacements": [
                {
                    "path": str(metadata_path),
                    "contentBase64": base64.b64encode(metadata_text.encode("utf-8")).decode("ascii"),
                    "expectedAbsent": True,
                }
            ],
        },
        compact=True,
    )

    payload = backend._apply_project_draft(request)

    assert payload["written"] is True
    assert payload["files"] == [
        {
            "path": str(metadata_path),
            "relative_path": ("src/modules/idea/IDEA_METADATA_FREE/meta.yaml"),
            "operation": "replace_bytes",
        }
    ]
    assert metadata_path.read_text(encoding="utf-8") == metadata_text
    assert loads_yaml(metadata_text) == {"title": title}

    conflicting_text = 'title: "Newer title"\n'
    conflicting_request = dumps_json(
        {
            "projectId": project.project_id,
            "projectRoot": str(project.root),
            "sourceReplacements": [
                {
                    "path": str(metadata_path),
                    "contentBase64": base64.b64encode(conflicting_text.encode("utf-8")).decode("ascii"),
                    "expectedAbsent": True,
                }
            ],
        },
        compact=True,
    )
    with pytest.raises(
        ValueError,
        match="appeared after the draft was opened",
    ):
        backend._apply_project_draft(conflicting_request)

    assert metadata_path.read_text(encoding="utf-8") == metadata_text


def test_project_source_form_bridge_preserves_the_current_editor_buffer(
    monkeypatch,
) -> None:
    calls: list[tuple[str, dict[str, object]]] = []
    expected = {
        "schema": "paradev.source-form.v1",
        "project_id": "PIHC3",
        "path": "/tmp/PIHC3/src/modules/Entity/VIENTO_MIRROR/record.json",
        "relative_path": "src/modules/Entity/VIENTO_MIRROR/record.json",
        "sections": [],
    }

    def fake_read_project_source_form(*, project_id: str, request: dict[str, object]) -> dict[str, object]:
        calls.append((project_id, request))
        return expected

    monkeypatch.setattr(backend, "read_project_source_form", fake_read_project_source_form)
    text = '  {"mesh":{"scale":4.25}}\n'
    request = dumps_json(
        {
            "projectId": " PIHC3 ",
            "projectRoot": " /tmp/PIHC3 ",
            "sourcePath": " src/modules/Entity/VIENTO_MIRROR/record.json ",
            "text": text,
            "query": "C01_C02_GREENLIGHT.40",
        },
        compact=True,
    )

    assert backend._project_source_form(request) is expected
    assert calls == [
        (
            "PIHC3",
            {
                "project_root": "/tmp/PIHC3",
                "path": "src/modules/Entity/VIENTO_MIRROR/record.json",
                "text": text,
                "query": "C01_C02_GREENLIGHT.40",
            },
        )
    ]


def test_project_source_form_bridge_preserves_an_unsupported_null_response(
    monkeypatch,
) -> None:
    monkeypatch.setattr(backend, "read_project_source_form", lambda **_kwargs: None)

    assert (
        backend._project_source_form(
            dumps_json(
                {
                    "projectId": "PIHC3",
                    "projectRoot": "/tmp/PIHC3",
                    "sourcePath": "src/modules/idea/DEMO/def.txt",
                    "text": "ideas = {}\n",
                },
                compact=True,
            )
        )
        is None
    )


def test_project_source_form_update_batch_bridge_preserves_unsaved_bases(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, dict[str, object]]] = []
    expected = {"schema": "paradev.source-form-update-batch.v1"}

    def fake_plan(*, project_id: str, request: dict[str, object]) -> dict[str, object]:
        calls.append((project_id, request))
        return expected

    monkeypatch.setattr(backend, "plan_project_source_form_updates", fake_plan)
    text = '{"mesh":{"scale":4.25}}\n'
    request = dumps_json(
        {
            "projectId": " PIHC3 ",
            "projectRoot": " /tmp/PIHC3 ",
            "updates": [
                {
                    "sourcePath": (" src/modules/entity/VIENTO_MIRROR/record.json "),
                    "values": {"mesh.scale": 4.5},
                    "text": text,
                    "query": "mesh scale",
                }
            ],
        },
        compact=True,
    )

    assert backend._project_source_form_update_batch(request) is expected
    assert calls == [
        (
            "PIHC3",
            {
                "project_root": "/tmp/PIHC3",
                "updates": [
                    {
                        "source_path": ("src/modules/entity/VIENTO_MIRROR/record.json"),
                        "values": {"mesh.scale": 4.5},
                        "text": text,
                        "query": "mesh scale",
                    }
                ],
            },
        )
    ]

    with pytest.raises(ValueError, match="unsupported fields: write"):
        backend._project_source_form_update_batch(
            dumps_json(
                {
                    "projectId": "PIHC3",
                    "projectRoot": "/tmp/PIHC3",
                    "updates": [
                        {
                            "sourcePath": "record.json",
                            "values": {"scale": 2},
                            "write": True,
                        }
                    ],
                },
                compact=True,
            )
        )


def test_project_localization_workspace_bridge_preserves_unsaved_sources(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, dict[str, object]]] = []
    expected = {"schema": "paradev.localization-workspace.v2"}

    def fake_read(*, project_id: str, request: dict[str, object]) -> dict[str, object]:
        calls.append((project_id, request))
        return expected

    monkeypatch.setattr(backend, "read_project_localization_workspace", fake_read)
    payload = dumps_json(
        {
            "projectId": " PIHC3 ",
            "projectRoot": " /tmp/PIHC3 ",
            "targetKind": " module ",
            "targetId": " idea/IDEA_TEST ",
            "sourceRoot": " /tmp/PIHC3/src ",
            "limit": 128,
            "drafts": [
                {
                    "sourcePath": " src/modules/idea/IDEA_TEST/main.loc ",
                    "text": "[en.IDEA_TEST]\nDraft\n",
                }
            ],
        },
        compact=True,
    )

    assert backend._project_localization_workspace(payload) is expected
    assert calls == [
        (
            "PIHC3",
            {
                "project_root": "/tmp/PIHC3",
                "target_kind": "module",
                "target_id": "idea/IDEA_TEST",
                "source_root": "/tmp/PIHC3/src",
                "limit": 128,
                "drafts": [
                    {
                        "source_path": "src/modules/idea/IDEA_TEST/main.loc",
                        "text": "[en.IDEA_TEST]\nDraft\n",
                    }
                ],
            },
        )
    ]


def test_project_localization_update_bridge_preserves_closed_operation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, dict[str, object]]] = []
    expected = {"schema": "paradev.localization-update-plan.v2"}

    def fake_plan(*, project_id: str, request: dict[str, object]) -> dict[str, object]:
        calls.append((project_id, request))
        return expected

    monkeypatch.setattr(backend, "plan_project_localization_update", fake_plan)
    payload = dumps_json(
        {
            "projectId": "PIHC3",
            "projectRoot": "/tmp/PIHC3",
            "targetKind": "module",
            "targetId": "idea/IDEA_TEST",
            "operation": {
                "op": "set",
                "language": "l_english",
                "key": "@",
                "value": "New title",
            },
        },
        compact=True,
    )

    assert backend._project_localization_update(payload) is expected
    assert calls == [
        (
            "PIHC3",
            {
                "project_root": "/tmp/PIHC3",
                "target_kind": "module",
                "target_id": "idea/IDEA_TEST",
                "drafts": [],
                "operation": {
                    "op": "set",
                    "language": "l_english",
                    "key": "@",
                    "value": "New title",
                },
            },
        )
    ]

    with pytest.raises(ValueError, match="operation must be an object"):
        backend._project_localization_update(
            dumps_json(
                {
                    "projectId": "PIHC3",
                    "projectRoot": "/tmp/PIHC3",
                    "targetKind": "module",
                    "targetId": "idea/IDEA_TEST",
                    "operation": None,
                },
                compact=True,
            )
        )


def test_project_browser_delegates_full_and_summary_requests_to_the_sdk(
    monkeypatch,
) -> None:
    calls: list[tuple[str, dict[str, object]]] = []
    full_payload = {"schema": "raw.project-browser.v1", "items": ["角色"]}
    summary_payload = {"schema": "raw.project-browser.v1", "items": []}

    class FakeProject:
        def browser(self, **filters: object) -> dict[str, object]:
            calls.append(("browser", filters))
            return full_payload

        def browser_summary(self, **filters: object) -> dict[str, object]:
            calls.append(("browser_summary", filters))
            return summary_payload

    roots: list[str] = []

    def fake_open_project(project_root: str) -> FakeProject:
        roots.append(project_root)
        return FakeProject()

    monkeypatch.setattr(backend, "open_project", fake_open_project)
    full_request = dumps_json(
        {
            "projectRoot": "  /tmp/角色项目  ",
            "profile": "  hoi4  ",
            "kind": " module ",
            "family": " ideas ",
            "moduleId": " ideas/example ",
            "collectionId": " example_collection ",
            "summary": False,
        },
        compact=True,
    )
    summary_request = dumps_json(
        {
            "projectRoot": "/tmp/角色项目",
            "profile": "hoi4",
            "kind": "collection",
            "family": "focus_trees",
            "summary": True,
        },
        compact=True,
    )

    assert backend._desktop_call(_call_request("project_browser", [full_request])) is full_payload
    assert backend._project_browser(summary_request) is summary_payload
    assert roots == ["/tmp/角色项目", "/tmp/角色项目"]
    assert calls == [
        (
            "browser",
            {
                "profile": "hoi4",
                "kind": "module",
                "family": "ideas",
                "module_id": "ideas/example",
                "collection_id": "example_collection",
            },
        ),
        (
            "browser_summary",
            {"profile": "hoi4", "kind": "collection", "family": "focus_trees"},
        ),
    ]


@pytest.mark.parametrize(
    ("request_payload", "message"),
    [
        ([], "desktop state request must be a JSON object."),
        (
            {"unexpected": True},
            "desktop state request contains unsupported fields: unexpected.",
        ),
        (
            {"projectRoot": 42},
            "desktop state projectRoot must be a JSON string or null.",
        ),
        (
            {"includeBrowser": "false"},
            "desktop state includeBrowser must be a JSON boolean or null.",
        ),
    ],
)
def test_desktop_state_rejects_invalid_request_shapes(request_payload: object, message: str) -> None:
    with pytest.raises(ValueError) as error:
        backend._desktop_state(dumps_json(request_payload, compact=True))
    assert str(error.value) == message


@pytest.mark.parametrize(
    ("request_payload", "message"),
    [
        ([], "project browser request must be a JSON object."),
        ({}, "project browser projectRoot cannot be empty."),
        ({"projectRoot": "  "}, "project browser projectRoot cannot be empty."),
        (
            {"projectRoot": 42},
            "project browser projectRoot must be a JSON string or null.",
        ),
        (
            {"projectRoot": "/tmp/PIHC3", "unknown": "value"},
            "project browser request contains unsupported fields: unknown.",
        ),
        (
            {"projectRoot": "/tmp/PIHC3", "profile": []},
            "project browser profile must be a JSON string or null.",
        ),
        (
            {"projectRoot": "/tmp/PIHC3", "summary": 1},
            "project browser summary must be a JSON boolean or null.",
        ),
        (
            {"projectRoot": "/tmp/PIHC3", "summary": True, "moduleId": "ideas/example"},
            "project browser summary cannot be combined with moduleId or collectionId.",
        ),
        (
            {"projectRoot": "/tmp/PIHC3", "summary": True, "collectionId": "example"},
            "project browser summary cannot be combined with moduleId or collectionId.",
        ),
    ],
)
def test_project_browser_rejects_invalid_request_shapes(request_payload: object, message: str) -> None:
    with pytest.raises(ValueError) as error:
        backend._project_browser(dumps_json(request_payload, compact=True))
    assert str(error.value) == message


def test_module_diagram_delegates_a_canonical_projection_request_to_the_sdk(
    monkeypatch,
) -> None:
    expected = {
        "schema": "raw.module-diagram.v1",
        "family": "technology",
        "nodes": [{"id": "TECHNOLOGY_FIREARM_I"}],
    }
    calls: list[tuple[str, str, str | None]] = []

    class FakeProject:
        def module_diagram(
            self,
            family: str,
            *,
            profile: str | None = None,
        ) -> dict[str, object]:
            calls.append(("/tmp/角色项目", family, profile))
            return expected

    roots: list[str] = []

    def fake_open_project(project_root: str) -> FakeProject:
        roots.append(project_root)
        return FakeProject()

    monkeypatch.setattr(backend, "open_project", fake_open_project)
    request = dumps_json(
        {
            "projectRoot": "  /tmp/角色项目  ",
            "family": "  technologies  ",
            "profile": "  hoi4  ",
        },
        compact=True,
    )

    assert backend._desktop_call(_call_request("module_diagram", [request])) is expected
    assert roots == ["/tmp/角色项目"]
    assert calls == [("/tmp/角色项目", "technologies", "hoi4")]


def test_module_diagram_edit_maps_dry_plan_and_hash_guarded_write_to_the_sdk(
    monkeypatch,
) -> None:
    dry_payload = {
        "schema": "raw.module-diagram-edit.v1",
        "plan_hash": "sha256:reviewed",
        "written": False,
    }
    write_payload = {
        "schema": "raw.module-diagram-edit.v1",
        "plan_hash": "sha256:reviewed",
        "written": True,
    }
    calls: list[tuple[str, dict[str, object]]] = []
    positions = [
        {
            "organization_id": "C01_ORG",
            "trait_id": "standardized_alloys_trait",
            "x": 12.5,
            "y": 7,
            "source_revision": f"sha256:{'a' * 64}",
        }
    ]
    edges = [
        {
            "kind": kind,
            "organization_id": "C01_ORG",
            "source_id": "shared_root_trait",
            "target_id": "standardized_alloys_trait",
            "present": True,
            "source_revision": f"sha256:{'a' * 64}",
        }
        for kind in (
            "relative_position",
            "any_parent",
            "all_parent",
            "mutually_exclusive",
        )
    ]

    class FakeProject:
        def edit_module_diagram(
            self,
            family: str,
            **options: object,
        ) -> dict[str, object]:
            calls.append((family, options))
            return write_payload if options["write"] else dry_payload

    roots: list[str] = []

    def fake_open_project(project_root: str) -> FakeProject:
        roots.append(project_root)
        return FakeProject()

    monkeypatch.setattr(backend, "open_project", fake_open_project)
    base_request = {
        "projectRoot": "  /tmp/角色项目  ",
        "family": " military_industrial_organization ",
        "profile": " hoi4 ",
        "positionIntents": positions,
        "edgeIntents": edges,
    }

    assert backend._module_diagram_edit(dumps_json(base_request, compact=True)) is dry_payload
    assert (
        backend._desktop_call(
            _call_request(
                "module_diagram_edit",
                [
                    dumps_json(
                        {
                            **base_request,
                            "write": True,
                            "planHash": "  sha256:reviewed  ",
                        },
                        compact=True,
                    )
                ],
            )
        )
        is write_payload
    )
    assert roots == ["/tmp/角色项目", "/tmp/角色项目"]
    assert calls == [
        (
            "military_industrial_organization",
            {
                "profile": "hoi4",
                "position_intents": positions,
                "edge_intents": edges,
                "node_intents": [],
                "write": False,
                "plan_hash": None,
            },
        ),
        (
            "military_industrial_organization",
            {
                "profile": "hoi4",
                "position_intents": positions,
                "edge_intents": edges,
                "node_intents": [],
                "write": True,
                "plan_hash": "sha256:reviewed",
            },
        ),
    ]


@pytest.mark.parametrize(
    ("request_payload", "message"),
    [
        ([], "module diagram request must be a JSON object."),
        ({}, "module diagram projectRoot cannot be empty."),
        (
            {"projectRoot": 42, "family": "technology"},
            "module diagram projectRoot must be a JSON string or null.",
        ),
        (
            {"projectRoot": "/tmp/PIHC3"},
            "module diagram family cannot be empty.",
        ),
        (
            {"projectRoot": "/tmp/PIHC3", "family": "  "},
            "module diagram family cannot be empty.",
        ),
        (
            {"projectRoot": "/tmp/PIHC3", "family": []},
            "module diagram family must be a JSON string or null.",
        ),
        (
            {
                "projectRoot": "/tmp/PIHC3",
                "family": "technology",
                "profile": False,
            },
            "module diagram profile must be a JSON string or null.",
        ),
        (
            {
                "projectRoot": "/tmp/PIHC3",
                "family": "technology",
                "fallbackMetadata": True,
            },
            "module diagram request contains unsupported fields: fallbackMetadata.",
        ),
    ],
)
def test_module_diagram_rejects_noncanonical_requests_before_opening_a_project(
    request_payload: object,
    message: str,
    monkeypatch,
) -> None:
    def fail_open_project(_project_root: str) -> None:
        raise AssertionError("invalid requests must not open a project")

    monkeypatch.setattr(backend, "open_project", fail_open_project)

    with pytest.raises(ValueError) as error:
        backend._module_diagram(dumps_json(request_payload, compact=True))
    assert str(error.value) == message


@pytest.mark.parametrize(
    ("request_payload", "message"),
    [
        ([], "module diagram edit request must be a JSON object."),
        ({}, "module diagram edit projectRoot cannot be empty."),
        (
            {"projectRoot": "/tmp/PIHC3"},
            "module diagram edit family cannot be empty.",
        ),
        (
            {
                "projectRoot": "/tmp/PIHC3",
                "family": "technology",
                "positionIntents": {},
            },
            "Module diagram position_intents must be a JSON array.",
        ),
        (
            {
                "projectRoot": "/tmp/PIHC3",
                "family": "technology",
                "positionIntents": [None],
            },
            "Module diagram position_intents[0] must be a JSON object.",
        ),
        (
            {
                "projectRoot": "/tmp/PIHC3",
                "family": "technology",
                "edgeIntents": "dependency",
            },
            "Module diagram edge_intents must be a JSON array.",
        ),
        (
            {
                "projectRoot": "/tmp/PIHC3",
                "family": "technology",
                "edgeIntents": [[]],
            },
            "Module diagram edge_intents[0] must be a JSON object.",
        ),
        (
            {
                "projectRoot": "/tmp/PIHC3",
                "family": "technology",
                "nodeIntents": {},
            },
            "Module diagram node_intents must be a JSON array.",
        ),
        (
            {
                "projectRoot": "/tmp/PIHC3",
                "family": "technology",
                "nodeIntents": [None],
            },
            "Module diagram node_intents[0] must be a JSON object.",
        ),
        (
            {
                "projectRoot": "/tmp/PIHC3",
                "family": "technology",
                "write": "true",
            },
            "module diagram edit write must be a JSON boolean or null.",
        ),
        (
            {
                "projectRoot": "/tmp/PIHC3",
                "family": "technology",
                "planHash": False,
            },
            "module diagram edit planHash must be a JSON string or null.",
        ),
        (
            {
                "projectRoot": "/tmp/PIHC3",
                "family": "technology",
                "write": True,
                "force": True,
            },
            "module diagram edit request contains unsupported fields: force.",
        ),
    ],
)
def test_module_diagram_edit_rejects_noncanonical_requests_before_opening_a_project(
    request_payload: object,
    message: str,
    monkeypatch,
) -> None:
    def fail_open_project(_project_root: str) -> None:
        raise AssertionError("invalid requests must not open a project")

    monkeypatch.setattr(backend, "open_project", fail_open_project)

    with pytest.raises(ValueError) as error:
        backend._module_diagram_edit(dumps_json(request_payload, compact=True))
    assert str(error.value) == message


def test_module_diagram_edit_bounds_intents_before_opening_a_project(
    monkeypatch,
) -> None:
    def fail_open_project(_project_root: str) -> None:
        raise AssertionError("oversized requests must not open a project")

    monkeypatch.setattr(backend, "open_project", fail_open_project)
    request = {
        "projectRoot": "/tmp/PIHC3",
        "family": "technology",
        "positionIntents": [{} for _ in range(MAX_MODULE_DIAGRAM_POSITION_INTENTS + 1)],
    }

    with pytest.raises(
        ValueError,
        match=("Module diagram position_intents cannot contain more than " f"{MAX_MODULE_DIAGRAM_POSITION_INTENTS} intents"),
    ):
        backend._module_diagram_edit(dumps_json(request, compact=True))

    request["positionIntents"] = []
    request["nodeIntents"] = [{} for _ in range(MAX_MODULE_DIAGRAM_NODE_INTENTS + 1)]
    with pytest.raises(
        ValueError,
        match=("Module diagram node_intents cannot contain more than " f"{MAX_MODULE_DIAGRAM_NODE_INTENTS} intents"),
    ):
        backend._module_diagram_edit(dumps_json(request, compact=True))


def test_module_diagram_does_not_hide_an_unsupported_provider_error(
    monkeypatch,
) -> None:
    class FakeProject:
        def module_diagram(
            self,
            family: str,
            *,
            profile: str | None = None,
        ) -> dict[str, object]:
            raise ValueError(f"Module diagram family {family!r} has no authoritative edit provider.")

    monkeypatch.setattr(backend, "open_project", lambda _project_root: FakeProject())
    request = dumps_json(
        {"projectRoot": "/tmp/PIHC3", "family": "focus"},
        compact=True,
    )

    with pytest.raises(
        ValueError,
        match="has no authoritative edit provider",
    ):
        backend._module_diagram(request)


def test_project_catalog_query_delegates_a_finite_canonical_page(monkeypatch) -> None:
    expected = {"schema": "raw.catalog-query.v1", "rows": [{"name": "角色"}]}
    calls: list[tuple[str, dict[str, object]]] = []

    class FakeProject:
        def catalog_query(self, **filters: object) -> dict[str, object]:
            calls.append(("catalog_query", filters))
            return expected

    roots: list[str] = []

    def fake_open_project(project_root: str) -> FakeProject:
        roots.append(project_root)
        return FakeProject()

    monkeypatch.setattr(backend, "open_project", fake_open_project)
    request = dumps_json(
        {
            "projectRoot": "  /tmp/角色项目  ",
            "entity": " module ",
            "targetId": " module:abc ",
            "name": " 角色 ",
            "tag": " family:ideas ",
            "limit": 1,
            "offset": 100,
            "includeData": True,
        },
        compact=True,
    )

    assert backend._desktop_call(_call_request("project_catalog_query", [request])) is expected
    assert roots == ["/tmp/角色项目"]
    assert calls == [
        (
            "catalog_query",
            {
                "entity": "module",
                "target_id": "module:abc",
                "name": "角色",
                "tag": "family:ideas",
                "limit": 1,
                "offset": 100,
                "include_data": True,
            },
        )
    ]


def test_project_catalog_query_defaults_to_unhydrated_first_page(monkeypatch) -> None:
    filters_seen: list[dict[str, object]] = []

    class FakeProject:
        def catalog_query(self, **filters: object) -> dict[str, object]:
            filters_seen.append(filters)
            return {"schema": "raw.catalog-query.v1", "rows": []}

    monkeypatch.setattr(backend, "open_project", lambda project_root: FakeProject())
    request = dumps_json({"projectRoot": "/tmp/PIHC3", "limit": 50}, compact=True)

    backend._project_catalog_query(request)

    assert filters_seen == [
        {
            "entity": None,
            "target_id": None,
            "name": None,
            "tag": None,
            "limit": 50,
            "offset": 0,
            "include_data": False,
        }
    ]


@pytest.mark.parametrize(
    ("request_payload", "message"),
    [
        ([], "project catalog query request must be a JSON object."),
        ({}, "project catalog query projectRoot cannot be empty."),
        ({"projectRoot": "/tmp/PIHC3"}, "project catalog query limit is required."),
        (
            {"projectRoot": "/tmp/PIHC3", "limit": 0},
            "project catalog query limit must be an integer from 1 to 200.",
        ),
        (
            {"projectRoot": "/tmp/PIHC3", "limit": 201},
            "project catalog query limit must be an integer from 1 to 200.",
        ),
        (
            {"projectRoot": "/tmp/PIHC3", "limit": True},
            "project catalog query limit must be an integer from 1 to 200.",
        ),
        (
            {"projectRoot": "/tmp/PIHC3", "limit": "50"},
            "project catalog query limit must be an integer from 1 to 200.",
        ),
        (
            {"projectRoot": "/tmp/PIHC3", "limit": 50, "offset": -1},
            "project catalog query offset must be a non-negative integer.",
        ),
        (
            {"projectRoot": "/tmp/PIHC3", "limit": 50, "offset": True},
            "project catalog query offset must be a non-negative integer.",
        ),
        (
            {"projectRoot": "/tmp/PIHC3", "limit": 50, "includeData": 1},
            "project catalog query includeData must be a JSON boolean or null.",
        ),
        (
            {"projectRoot": "/tmp/PIHC3", "limit": 2, "includeData": True},
            "project catalog query hydrated requests must have limit 1.",
        ),
        (
            {"projectRoot": "/tmp/PIHC3", "limit": 50, "database": "/tmp/other.sqlite"},
            "project catalog query request contains unsupported fields: database.",
        ),
    ],
)
def test_project_catalog_query_rejects_invalid_request_shapes(request_payload: object, message: str) -> None:
    with pytest.raises(ValueError) as error:
        backend._project_catalog_query(dumps_json(request_payload, compact=True))
    assert str(error.value) == message


def test_project_catalog_status_delegates_to_the_canonical_project_resource(
    monkeypatch,
) -> None:
    expected = {
        "schema": "paradev.hb.catalog-status.v1",
        "project_id": "PIHC3",
        "database": "/tmp/PIHC3/.paradev/.cache/hb/catalog.sqlite",
        "status": "present",
        "code": "catalog.present",
    }
    roots: list[str] = []
    calls: list[str] = []

    class FakeProject:
        def catalog_status(self) -> dict[str, object]:
            calls.append("catalog_status")
            return expected

    def fake_open_project(project_root: str) -> FakeProject:
        roots.append(project_root)
        return FakeProject()

    monkeypatch.setattr(backend, "open_project", fake_open_project)
    request = dumps_json({"projectRoot": "  /tmp/PIHC3  "}, compact=True)

    assert backend._desktop_call(_call_request("project_catalog_status", [request])) is expected
    assert roots == ["/tmp/PIHC3"]
    assert calls == ["catalog_status"]


@pytest.mark.parametrize(
    ("request_payload", "message"),
    [
        ([], "project catalog status request must be a JSON object."),
        ({}, "project catalog status projectRoot cannot be empty."),
        ({"projectRoot": "  "}, "project catalog status projectRoot cannot be empty."),
        (
            {"projectRoot": 42},
            "project catalog status projectRoot must be a JSON string or null.",
        ),
        (
            {"projectRoot": "/tmp/PIHC3", "database": "/tmp/other.sqlite"},
            "project catalog status request contains unsupported fields: database.",
        ),
    ],
)
def test_project_catalog_status_rejects_invalid_request_shapes(request_payload: object, message: str) -> None:
    with pytest.raises(ValueError) as error:
        backend._project_catalog_status(dumps_json(request_payload, compact=True))
    assert str(error.value) == message


def test_project_catalog_refresh_delegates_to_the_canonical_catalog(
    monkeypatch,
) -> None:
    expected = {
        "schema": "raw.catalog-refresh.v1",
        "database": "/tmp/PIHC3/.paradev/.cache/hb/catalog.sqlite",
    }
    project = object()
    calls: list[tuple[object, str | None]] = []
    monkeypatch.setattr(backend, "open_project", lambda project_root: project)

    def fake_catalog_refresh(source_project: object, *, profile: str | None = None) -> dict[str, object]:
        calls.append((source_project, profile))
        return expected

    monkeypatch.setattr(backend, "catalog_refresh", fake_catalog_refresh)
    request = dumps_json({"projectRoot": " /tmp/PIHC3 ", "profile": " hoi4 "}, compact=True)

    assert backend._desktop_call(_call_request("project_catalog_refresh", [request])) is expected
    assert calls == [(project, "hoi4")]


@pytest.mark.parametrize(
    ("request_payload", "message"),
    [
        ({}, "project catalog refresh projectRoot cannot be empty."),
        (
            {"projectRoot": "/tmp/PIHC3", "profile": []},
            "project catalog refresh profile must be a JSON string or null.",
        ),
        (
            {"projectRoot": "/tmp/PIHC3", "database": "/tmp/other.sqlite"},
            "project catalog refresh request contains unsupported fields: database.",
        ),
    ],
)
def test_project_catalog_refresh_rejects_invalid_request_shapes(request_payload: object, message: str) -> None:
    with pytest.raises(ValueError) as error:
        backend._project_catalog_refresh(dumps_json(request_payload, compact=True))
    assert str(error.value) == message


def _camel_alias(value: str) -> str:
    head, *tail = value.split("_")
    return head + "".join(part.title() for part in tail)


def test_project_inspect_dispatches_every_sdk_contract_kind_and_filter(
    monkeypatch,
) -> None:
    calls: list[tuple[str, dict[str, object]]] = []

    class FakeProject:
        def inspect(self, kind: str, /, **filters: object) -> dict[str, object]:
            calls.append((kind, filters))
            return {"kind": kind, "filters": filters}

    roots: list[str] = []

    def fake_open_project(project_root: str) -> FakeProject:
        roots.append(project_root)
        return FakeProject()

    monkeypatch.setattr(backend, "open_project", fake_open_project)
    contract = get_project_inspection_contract()
    for row in contract["inspections"]:
        expected_filters = {name: f"值:{name}" for name in row["filters"]}
        request = dumps_json(
            {
                "projectRoot": "  /tmp/角色项目  ",
                "kind": f"  {row['kind']}  ",
                "filters": {_camel_alias(name): value for name, value in expected_filters.items()},
            },
            compact=True,
        )

        payload = backend._desktop_call(_call_request("project_inspect", [request]))

        assert payload == {"kind": row["kind"], "filters": expected_filters}

    assert roots == ["/tmp/角色项目"] * len(contract["inspections"])
    assert calls == [(row["kind"], {name: f"值:{name}" for name in row["filters"]}) for row in contract["inspections"]]


def test_project_inspect_preserves_json_scalar_values_until_sdk_dispatch(monkeypatch, capsys) -> None:
    seen: list[tuple[str, dict[str, object]]] = []

    class FakeProject:
        def inspect(self, kind: str, /, **filters: object) -> dict[str, object]:
            seen.append((kind, filters))
            return {"schema": "raw.sdk.payload.v1", "filters": filters}

    monkeypatch.setattr(backend, "open_project", lambda project_root: FakeProject())
    request = dumps_json(
        {
            "projectRoot": "/tmp/角色项目",
            "kind": "diagnostics",
            "filters": {
                "strictMetadata": False,
                "code": None,
                "moduleId": 0,
                "owner": "角色-测试",
            },
        },
        compact=True,
    )
    monkeypatch.setattr(sys, "stdin", _call_request("project_inspect", [request]))

    assert backend.main(["desktop-call"]) == 0

    captured = capsys.readouterr()
    expected = {
        "strict_metadata": False,
        "code": None,
        "module_id": 0,
        "owner": "角色-测试",
    }
    assert captured.err == ""
    assert loads_json(captured.out) == {
        "schema": "raw.sdk.payload.v1",
        "filters": expected,
    }
    assert seen == [("diagnostics", expected)]


def test_project_inspect_keeps_large_noisy_sdk_output_off_protocol_stdout(monkeypatch, capsys) -> None:
    large_value = f"角色-{'x' * 200_000}"

    class FakeProject:
        def inspect(self, kind: str, /, **filters: object) -> dict[str, object]:
            print("SDK 诊断噪声")
            return {"kind": kind, "value": filters["name"]}

    monkeypatch.setattr(backend, "open_project", lambda project_root: FakeProject())
    request = dumps_json(
        {
            "projectRoot": "/tmp/PIHC3",
            "kind": "catalog-query",
            "filters": {"name": large_value},
        },
        compact=True,
    )
    monkeypatch.setattr(sys, "stdin", _call_request("project_inspect", [request]))

    assert backend.main(["desktop-call"]) == 0

    captured = capsys.readouterr()
    assert loads_json(captured.out) == {"kind": "catalog-query", "value": large_value}
    assert captured.err == "SDK 诊断噪声\n"


@pytest.mark.parametrize(
    ("request_payload", "message"),
    [
        ([], "project inspection request must be a JSON object."),
        ({}, "project root cannot be empty."),
        ({"projectRoot": 42, "kind": "summary"}, "project root cannot be empty."),
        ({"projectRoot": "/tmp/PIHC3"}, "project inspection kind cannot be empty."),
        (
            {"projectRoot": "/tmp/PIHC3", "kind": []},
            "project inspection kind cannot be empty.",
        ),
        (
            {"projectRoot": "/tmp/PIHC3", "kind": "summary", "filters": []},
            "project inspection filters must be a JSON object.",
        ),
        (
            {
                "projectRoot": "/tmp/PIHC3",
                "kind": "summary",
                "filters": {"💥": "value"},
            },
            "project inspection filter name '💥' must normalize to non-empty snake_case.",
        ),
    ],
)
def test_project_inspect_rejects_invalid_request_shapes(request_payload: object, message: str) -> None:
    with pytest.raises(ValueError) as error:
        backend._project_inspect(dumps_json(request_payload, compact=True))
    assert str(error.value) == message


def test_project_inspect_rejects_normalized_filter_alias_collisions() -> None:
    request = dumps_json(
        {
            "projectRoot": "/tmp/PIHC3",
            "kind": "diagnostics",
            "filters": {"strictMetadata": False, "strict_metadata": True},
        },
        compact=True,
    )

    with pytest.raises(ValueError) as error:
        backend._project_inspect(request)
    message = "project inspection filter aliases collide: 'strictMetadata' and 'strict_metadata' both normalize to 'strict_metadata'."
    assert str(error.value) == message


def test_remove_module_delegates_to_the_sdk_with_write_enabled(monkeypatch) -> None:
    expected = {"schema": "paradev.module.remove.v1", "removed": True}
    roots: list[str] = []
    calls: list[tuple[str, str | None, bool]] = []

    class FakeProject:
        def remove_module(self, module_id: str, *, source_root: str | None = None, write: bool = False) -> dict[str, object]:
            calls.append((module_id, source_root, write))
            return expected

    def fake_open_project(project_root: str) -> FakeProject:
        roots.append(project_root)
        return FakeProject()

    monkeypatch.setattr(backend, "open_project", fake_open_project)
    request = dumps_json(
        {
            "projectRoot": "  /tmp/PIHC3  ",
            "moduleId": " modifier/demo ",
            "sourceRoot": " src ",
        },
        compact=True,
    )

    assert backend._desktop_call(_call_request("remove_module", [request])) is expected
    assert roots == ["/tmp/PIHC3"]
    assert calls == [("modifier/demo", "src", True)]


def test_duplicate_module_delegates_plan_and_exact_hash_apply_to_the_sdk(
    monkeypatch,
) -> None:
    expected = {"schema": "paradev.sdk.module_duplicate.v1", "status": "duplicated"}
    roots: list[str] = []
    calls: list[tuple[str, str, str | None, str | None, str, bool, str | None]] = []

    class FakeProject:
        def duplicate_module(
            self,
            module_id: str,
            object_id: str,
            *,
            source_root: str | None = None,
            destination_source_root: str | None = None,
            identity: str = "rewrite",
            write: bool = False,
            plan_hash: str | None = None,
        ) -> dict[str, object]:
            calls.append(
                (
                    module_id,
                    object_id,
                    source_root,
                    destination_source_root,
                    identity,
                    write,
                    plan_hash,
                )
            )
            return expected

    def fake_open_project(project_root: str) -> FakeProject:
        roots.append(project_root)
        return FakeProject()

    monkeypatch.setattr(backend, "open_project", fake_open_project)
    request = dumps_json(
        {
            "projectRoot": " /tmp/PIHC3 ",
            "moduleId": " modifier/demo ",
            "objectId": " copied_demo ",
            "sourceRoot": " src ",
            "destinationSourceRoot": " imports ",
            "write": True,
            "planHash": f" {'a' * 64} ",
        },
        compact=True,
    )

    assert backend._desktop_call(_call_request("duplicate_module", [request])) is expected
    assert roots == ["/tmp/PIHC3"]
    assert calls == [
        (
            "modifier/demo",
            "copied_demo",
            "src",
            "imports",
            "rewrite",
            True,
            "a" * 64,
        )
    ]


def test_set_module_collection_delegates_plan_and_exact_hash_apply_to_the_sdk(
    monkeypatch,
) -> None:
    expected = {
        "schema": "paradev.sdk.module_collection_update.v1",
        "status": "updated",
    }
    roots: list[str] = []
    calls: list[tuple[str, str | None, str | None, bool, str | None]] = []

    class FakeProject:
        def set_module_collection(
            self,
            module_id: str,
            collection_id: str | None,
            *,
            source_root: str | None = None,
            write: bool = False,
            plan_hash: str | None = None,
        ) -> dict[str, object]:
            calls.append((module_id, collection_id, source_root, write, plan_hash))
            return expected

    def fake_open_project(project_root: str) -> FakeProject:
        roots.append(project_root)
        return FakeProject()

    monkeypatch.setattr(backend, "open_project", fake_open_project)
    request = dumps_json(
        {
            "projectRoot": " /tmp/PIHC3 ",
            "moduleId": " focus/FOCUS_DEMO ",
            "collectionId": " C01_focus_tree ",
            "sourceRoot": " src ",
            "write": True,
            "planHash": f" {'a' * 64} ",
        },
        compact=True,
    )

    assert backend._desktop_call(_call_request("module_collection_set", [request])) is expected
    assert roots == ["/tmp/PIHC3"]
    assert calls == [
        (
            "focus/FOCUS_DEMO",
            "C01_focus_tree",
            "src",
            True,
            "a" * 64,
        )
    ]


def test_set_module_activity_delegates_plan_and_exact_hash_apply_to_the_sdk(
    monkeypatch,
) -> None:
    expected = {
        "schema": "paradev.sdk.module_activity_update.v1",
        "status": "updated",
    }
    roots: list[str] = []
    calls: list[tuple[str, bool, str | None, bool, str | None]] = []

    class FakeProject:
        def set_module_active(
            self,
            module_id: str,
            active: bool,
            *,
            source_root: str | None = None,
            write: bool = False,
            plan_hash: str | None = None,
        ) -> dict[str, object]:
            calls.append((module_id, active, source_root, write, plan_hash))
            return expected

    def fake_open_project(project_root: str) -> FakeProject:
        roots.append(project_root)
        return FakeProject()

    monkeypatch.setattr(backend, "open_project", fake_open_project)
    request = dumps_json(
        {
            "projectRoot": " /tmp/PIHC3 ",
            "moduleId": " focus/FOCUS_DEMO ",
            "active": False,
            "sourceRoot": " src ",
            "write": True,
            "planHash": f" {'a' * 64} ",
        },
        compact=True,
    )

    assert backend._desktop_call(_call_request("module_activity_set", [request])) is expected
    assert roots == ["/tmp/PIHC3"]
    assert calls == [
        (
            "focus/FOCUS_DEMO",
            False,
            "src",
            True,
            "a" * 64,
        )
    ]


@pytest.mark.parametrize(
    ("request_payload", "message"),
    [
        ({}, "module collection projectRoot cannot be empty."),
        (
            {"projectRoot": "/tmp/PIHC3"},
            "module collection moduleId cannot be empty.",
        ),
        (
            {
                "projectRoot": "/tmp/PIHC3",
                "moduleId": "focus/FOCUS_DEMO",
                "collectionId": [],
            },
            "module collection collectionId must be a JSON string or null.",
        ),
        (
            {
                "projectRoot": "/tmp/PIHC3",
                "moduleId": "focus/FOCUS_DEMO",
                "write": "yes",
            },
            "module collection write must be a JSON boolean or null.",
        ),
        (
            {
                "projectRoot": "/tmp/PIHC3",
                "moduleId": "focus/FOCUS_DEMO",
                "force": True,
            },
            "module collection request contains unsupported fields: force.",
        ),
    ],
)
def test_set_module_collection_rejects_noncanonical_requests(
    request_payload: object,
    message: str,
) -> None:
    with pytest.raises(ValueError) as error:
        backend._set_module_collection(dumps_json(request_payload, compact=True))
    assert str(error.value) == message


@pytest.mark.parametrize(
    ("request_payload", "message"),
    [
        ({}, "module duplicate projectRoot cannot be empty."),
        (
            {"projectRoot": "/tmp/PIHC3", "moduleId": "modifier/demo"},
            "module duplicate objectId cannot be empty.",
        ),
        (
            {
                "projectRoot": "/tmp/PIHC3",
                "moduleId": "modifier/demo",
                "objectId": "copy",
                "write": "yes",
            },
            "module duplicate write must be a JSON boolean or null.",
        ),
        (
            {
                "projectRoot": "/tmp/PIHC3",
                "moduleId": "modifier/demo",
                "objectId": "copy",
                "force": True,
            },
            "module duplicate request contains unsupported fields: force.",
        ),
    ],
)
def test_duplicate_module_rejects_noncanonical_requests(
    request_payload: object,
    message: str,
) -> None:
    with pytest.raises(ValueError) as error:
        backend._duplicate_module(dumps_json(request_payload, compact=True))
    assert str(error.value) == message


@pytest.mark.parametrize(
    ("request_payload", "message"),
    [
        ({}, "module remove projectRoot cannot be empty."),
        (
            {"projectRoot": 42, "moduleId": "modifier/demo"},
            "module remove projectRoot must be a JSON string or null.",
        ),
        ({"projectRoot": "/tmp/PIHC3"}, "module remove moduleId cannot be empty."),
        (
            {"projectRoot": "/tmp/PIHC3", "moduleId": []},
            "module remove moduleId must be a JSON string or null.",
        ),
        (
            {
                "projectRoot": "/tmp/PIHC3",
                "moduleId": "modifier/demo",
                "sourceRoot": False,
            },
            "module remove sourceRoot must be a JSON string or null.",
        ),
        (
            {"projectRoot": "/tmp/PIHC3", "moduleId": "modifier/demo", "write": False},
            "module remove request contains unsupported fields: write.",
        ),
    ],
)
def test_remove_module_rejects_noncanonical_requests(request_payload: object, message: str) -> None:
    with pytest.raises(ValueError) as error:
        backend._remove_module(dumps_json(request_payload, compact=True))
    assert str(error.value) == message


def test_desktop_call_rejects_unknown_protocol_and_operation(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        sys,
        "stdin",
        StringIO(
            dumps_json(
                {
                    "protocol": "paradev.desktop.backend.v0",
                    "operation": "desktop_path_status",
                    "args": ["."],
                },
                compact=True,
            )
        ),
    )
    assert backend.main(["desktop-call"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "unsupported desktop backend protocol: 'paradev.desktop.backend.v0'.\n"

    monkeypatch.setattr(sys, "stdin", _call_request("dynamic_python_eval", []))
    assert backend.main(["desktop-call"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "unsupported desktop operation: 'dynamic_python_eval'.\n"


def test_desktop_helper_allowlist_matches_the_embedded_bridge() -> None:
    assert set(backend._HELPERS) == EXPECTED_DESKTOP_OPERATIONS


def test_backend_forwards_other_arguments_to_the_cli(monkeypatch) -> None:
    seen: list[list[str]] = []

    def fake_main(argv) -> int:
        seen.append(list(argv))
        return 23

    monkeypatch.setattr("paradev.cli.main", fake_main)

    assert backend.main(["summary", "/tmp/PIHC3", "--json"]) == 23
    assert seen == [["summary", "/tmp/PIHC3", "--json"]]
