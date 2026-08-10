import subprocess
import sys
from pathlib import Path
from types import MappingProxyType, SimpleNamespace


class FakeProcess:
    def __init__(self) -> None:
        self.returncode: int | None = None
        self.killed = False
        self.terminated = False

    def poll(self) -> int | None:
        return self.returncode

    def terminate(self) -> None:
        self.terminated = True
        self.returncode = -15

    def kill(self) -> None:
        self.killed = True
        self.returncode = -9

    def wait(self, timeout: float | None = None) -> int:
        if self.returncode is None:
            self.returncode = 0
        return self.returncode


def test_native_project_picker_returns_path_and_cancel(monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from paradev.surfaces import rest as rest_surface

    selections = iter(["/tmp/PIHC3", None])
    monkeypatch.setattr(
        rest_surface,
        "desktop_select_project_path",
        lambda: next(selections),
    )
    client = TestClient(rest_surface.build_app())

    selected = client.post("/desktop/select-project")
    cancelled = client.post("/desktop/select-project")

    assert selected.status_code == 200
    assert selected.json() == {
        "schema": "paradev.desktop.project-selection.v1",
        "path": "/tmp/PIHC3",
    }
    assert cancelled.status_code == 200
    assert cancelled.json() == {
        "schema": "paradev.desktop.project-selection.v1",
        "path": None,
    }


def test_native_project_package_import_returns_install_and_cancel(monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from paradev.surfaces import rest as rest_surface

    package_path = "/tmp/PIHC3-0.2.3-project.zip"
    selections = iter([package_path, None])
    expected = {
        "schema": "paradev.desktop.project-package-install.v1",
        "status": "installed",
        "installed": True,
        "project_root": "/tmp/Projects/PIHC3-0.2.3",
    }
    observed: list[str] = []
    monkeypatch.setattr(
        rest_surface,
        "desktop_select_project_package_path",
        lambda: next(selections),
    )

    def fake_install(selected: str) -> dict[str, object]:
        observed.append(selected)
        return expected

    monkeypatch.setattr(rest_surface, "desktop_install_project_package", fake_install)
    client = TestClient(rest_surface.build_app())

    installed = client.post("/desktop/import-project-package", json={})
    cancelled = client.post("/desktop/import-project-package", json={})

    assert installed.status_code == 200
    assert installed.json() == expected
    assert observed == [package_path]
    assert cancelled.status_code == 200
    assert cancelled.json() is None


def test_native_project_package_import_surfaces_actionable_failure(monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from paradev.surfaces import rest as rest_surface

    monkeypatch.setattr(
        rest_surface,
        "desktop_select_project_package_path",
        lambda: "/tmp/PIHC3-broken.zip",
    )
    monkeypatch.setattr(
        rest_surface,
        "desktop_install_project_package",
        lambda _path: (_ for _ in ()).throw(ValueError("Re-download the PIHC3 package.")),
    )
    client = TestClient(rest_surface.build_app())

    response = client.post("/desktop/import-project-package", json={})

    assert response.status_code == 400
    assert response.json()["detail"] == "Re-download the PIHC3 package."


def test_native_guided_source_update_batch_uses_registry_planner(
    monkeypatch,
) -> None:
    from fastapi.testclient import TestClient

    from paradev.surfaces import rest as rest_surface

    calls: list[tuple[str, dict[str, object]]] = []
    expected = {"schema": "paradev.source-form-update-batch.v1"}

    def fake_plan(*, project_id: str, request: dict[str, object]) -> dict[str, object]:
        calls.append((project_id, request))
        return expected

    monkeypatch.setattr(
        rest_surface,
        "plan_project_source_form_updates",
        fake_plan,
    )
    client = TestClient(rest_surface.build_app())
    text = '{"mesh":{"scale":4.25}}\n'

    response = client.post(
        "/desktop/sources/form-updates/plan",
        json={
            "projectId": "PIHC3",
            "projectRoot": "/tmp/PIHC3",
            "updates": [
                {
                    "sourcePath": ("src/modules/entity/VIENTO_MIRROR/record.json"),
                    "values": {"mesh.scale": 4.5},
                    "text": text,
                }
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == expected
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
                    }
                ],
            },
        )
    ]

    invalid = client.post(
        "/desktop/sources/form-updates/plan",
        json={
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
    )
    assert invalid.status_code == 400
    assert "unsupported fields: write" in invalid.json()["detail"]


def test_native_draft_apply_rejects_unknown_fields_and_alias_collisions() -> None:
    from fastapi.testclient import TestClient

    from paradev.surfaces.rest import build_app

    client = TestClient(build_app())

    unknown = client.post(
        "/desktop/drafts/apply",
        json={
            "projectRoot": "/missing",
            "sourceEdits": [],
            "unexpected": True,
        },
    )
    collision = client.post(
        "/desktop/drafts/apply",
        json={
            "projectRoot": "/missing",
            "project_root": "/also-missing",
            "sourceEdits": [],
        },
    )

    assert unknown.status_code == 400
    assert "unsupported fields: unexpected" in unknown.json()["detail"]
    assert collision.status_code == 400
    assert "cannot provide both 'projectRoot' and 'project_root'" in collision.json()["detail"]


def test_native_thumbnail_cache_recovers_stale_content_without_hiding_boundary_errors(tmp_path: Path) -> None:
    from fastapi.testclient import TestClient

    from paradev.desktop import desktop_thumbnail_cache_path
    from paradev.surfaces.rest import build_app

    project_root = tmp_path / "project"
    project_root.mkdir()
    client = TestClient(build_app())

    missing = client.get(
        "/desktop/thumbnail-cache",
        params={"project_root": str(project_root), "cache_key": "v1|ideas:IDEA_ALPHA|icon.png"},
    )

    assert missing.status_code == 200
    assert missing.json() is None

    invalid_key = client.get(
        "/desktop/thumbnail-cache",
        params={"project_root": str(project_root), "cache_key": " "},
    )
    invalid_root = client.get(
        "/desktop/thumbnail-cache",
        params={"project_root": str(tmp_path / "missing"), "cache_key": "icon.png"},
    )
    corrupt_path = desktop_thumbnail_cache_path(project_root, "corrupt")
    corrupt_path.parent.mkdir(parents=True)
    corrupt_path.write_bytes(b"not a png")
    corrupt = client.get(
        "/desktop/thumbnail-cache",
        params={"project_root": str(project_root), "cache_key": "corrupt"},
    )
    directory_path = desktop_thumbnail_cache_path(project_root, "directory")
    directory_path.mkdir()
    directory = client.get(
        "/desktop/thumbnail-cache",
        params={"project_root": str(project_root), "cache_key": "directory"},
    )
    rejected_write_path = desktop_thumbnail_cache_path(project_root, "invalid-write")
    invalid_write = client.put(
        "/desktop/thumbnail-cache",
        json={
            "projectRoot": str(project_root),
            "cacheKey": "invalid-write",
            "bytes": [106, 112, 101, 103],
        },
    )

    assert invalid_key.status_code == 400
    assert "thumbnail cache key cannot be empty" in invalid_key.json()["detail"]
    assert invalid_root.status_code == 400
    assert "Cannot resolve project root" in invalid_root.json()["detail"]
    assert corrupt.status_code == 200
    assert corrupt.json() is None
    assert not corrupt_path.exists()
    assert directory.status_code == 400
    assert "Thumbnail cache path is not a file" in directory.json()["detail"]
    assert invalid_write.status_code == 400
    assert "not a valid PNG" in invalid_write.json()["detail"]
    assert not rejected_write_path.exists()


def test_native_draft_apply_normalizes_nested_aliases_strictly(monkeypatch, tmp_path: Path) -> None:
    from fastapi.testclient import TestClient

    import paradev.surfaces.rest as rest

    calls: list[tuple[str, dict[str, object]]] = []

    def fake_apply_project_draft(*, project_id: str, request: dict[str, object]) -> dict[str, object]:
        calls.append((project_id, request))
        return {"schema": "paradev.rest.draft_apply.v1", "written": []}

    monkeypatch.setattr(
        rest,
        "open_project",
        lambda root: SimpleNamespace(project_id="PIHC3", root=Path(root)),
    )
    monkeypatch.setattr(rest, "apply_project_draft", fake_apply_project_draft)
    client = TestClient(rest.build_app())

    response = client.post(
        "/desktop/drafts/apply",
        json={
            "projectRoot": str(tmp_path),
            "sourceEdits": [
                {
                    "path": "src/modules/idea/test/def.txt",
                    "text": "ideas = {}\n",
                    "expectedSize": 12,
                    "expectedMtimeNs": "1700000000000000000",
                }
            ],
            "sourceRemovals": [
                {
                    "path": "src/modules/idea/test/old.loc",
                    "expected_size": 64,
                    "expected_mtime_ns": "1700000000000000001",
                }
            ],
            "sourceReplacements": [
                {
                    "path": "src/modules/idea/test/icon.dds",
                    "contentBase64": "cG5n",
                    "contentFormat": "png",
                    "targetFormat": "dds",
                    "expectedAbsent": True,
                }
            ],
        },
    )

    assert response.status_code == 200
    assert calls == [
        (
            "PIHC3",
            {
                "project_root": str(tmp_path),
                "source_edits": [
                    {
                        "path": "src/modules/idea/test/def.txt",
                        "text": "ideas = {}\n",
                        "expected_size": 12,
                        "expected_mtime_ns": "1700000000000000000",
                    }
                ],
                "source_removals": [
                    {
                        "path": "src/modules/idea/test/old.loc",
                        "expected_size": 64,
                        "expected_mtime_ns": "1700000000000000001",
                    }
                ],
                "source_replacements": [
                    {
                        "path": "src/modules/idea/test/icon.dds",
                        "content_base64": "cG5n",
                        "content_format": "png",
                        "target_format": "dds",
                        "expected_absent": True,
                    }
                ],
            },
        )
    ]

    unknown = client.post(
        "/desktop/drafts/apply",
        json={
            "projectRoot": str(tmp_path),
            "sourceEdits": [{"path": "def.txt", "text": "ideas = {}", "surprise": True}],
        },
    )
    collision = client.post(
        "/desktop/drafts/apply",
        json={
            "projectRoot": str(tmp_path),
            "sourceReplacements": [
                {
                    "path": "icon.dds",
                    "contentBase64": "cG5n",
                    "content_base64": "cG5n",
                }
            ],
        },
    )

    assert unknown.status_code == 400
    assert "unsupported fields: 'surprise'" in unknown.json()["detail"]
    assert collision.status_code == 400
    assert "cannot provide both 'contentBase64' and 'content_base64'" in collision.json()["detail"]


def test_live_openapi_uses_the_canonical_draft_apply_request_schema() -> None:
    from fastapi.testclient import TestClient

    from paradev.surfaces.rest import (
        DRAFT_APPLY_PATH,
        build_app,
        get_openapi_seed,
    )

    live_operation = TestClient(build_app()).get("/openapi.json").json()["paths"][DRAFT_APPLY_PATH]["post"]
    static_operation = get_openapi_seed()["paths"][DRAFT_APPLY_PATH]["post"]

    assert live_operation["requestBody"] == static_operation["requestBody"]


def test_native_web_bridge_runs_build_lifecycle(monkeypatch, tmp_path: Path) -> None:
    from fastapi.testclient import TestClient

    import paradev.desktop.builds as desktop_builds
    from paradev.surfaces.rest import build_app, get_openapi_seed

    processes: list[FakeProcess] = []
    popen_calls: list[dict[str, object]] = []

    def fake_popen(command, cwd=None, stdout=None, stderr=None, start_new_session=False):
        process = FakeProcess()
        processes.append(process)
        popen_calls.append(
            {
                "command": list(command),
                "cwd": str(cwd),
                "start_new_session": start_new_session,
            }
        )
        return process

    monkeypatch.setattr(desktop_builds.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(desktop_builds, "_desktop_build_output_path", lambda name: tmp_path / name)
    client = TestClient(build_app())

    started = client.post(
        "/desktop/builds",
        json={
            "projectRoot": "/tmp/PIHC3",
            "mode": "cached",
            "profile": "hoi4",
            "strictMetadata": True,
            "target": {"kind": "module", "id": "focus_tree/GER_main"},
        },
    )

    assert started.status_code == 200
    started_payload = started.json()
    assert started_payload["schema"] == "paradev.desktop.build-run.v1"
    assert started_payload["status"] == "running"
    assert started_payload["mode"] == "cached"
    assert started_payload["target"] == {"kind": "module", "id": "focus_tree/GER_main"}
    assert "--progress-jsonl" in popen_calls[0]["command"]
    assert popen_calls[0]["command"][:4] == [sys.executable, "-m", "paradev", "build"]
    assert popen_calls[0]["cwd"] == "/tmp/PIHC3"
    listed = client.get("/desktop/builds", params={"project_root": "/tmp/PIHC3"})
    assert listed.status_code == 200
    assert listed.json()["schema"] == "paradev.desktop.build-runs.v1"
    assert [run["runId"] for run in listed.json()["runs"]] == [started_payload["runId"]]

    isolated_client = TestClient(build_app())
    assert isolated_client.get("/desktop/builds/status").status_code == 422
    assert isolated_client.post("/desktop/builds/interrupt").status_code == 422
    assert isolated_client.get("/desktop/builds/status", params={"run_id": ""}).status_code == 422
    assert isolated_client.get("/desktop/builds/status", params={"run_id": "   "}).status_code == 422
    assert isolated_client.post("/desktop/builds/interrupt", json={}).status_code == 422
    assert isolated_client.post("/desktop/builds/interrupt", json={"runId": ""}).status_code == 422
    assert isolated_client.post("/desktop/builds/interrupt", json={"run_id": "   "}).status_code == 422
    assert isolated_client.post("/desktop/builds/interrupt", json={"runId": None}).status_code == 422
    assert (
        isolated_client.post(
            "/desktop/builds/interrupt",
            json={"runId": None, "run_id": "missing-run"},
        ).status_code
        == 200
    )
    assert (
        isolated_client.post(
            "/desktop/builds/interrupt",
            json={"runId": "missing-run", "extra": True},
        ).status_code
        == 422
    )
    assert (
        isolated_client.post(
            "/desktop/builds/interrupt",
            json={"runId": "build-one", "run_id": "build-two"},
        ).status_code
        == 422
    )
    assert isolated_client.post("/desktop/builds/interrupt", json={"run_id": "missing-run"}).status_code == 200
    live_openapi = isolated_client.get("/openapi.json").json()
    live_status_parameter = live_openapi["paths"]["/desktop/builds/status"]["get"]["parameters"][0]
    assert live_status_parameter["required"] is True
    assert live_status_parameter["schema"]["minLength"] == 1
    assert live_status_parameter["schema"]["pattern"] == r".*\S.*"
    live_interrupt_ref = live_openapi["paths"]["/desktop/builds/interrupt"]["post"]["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    live_interrupt_schema = live_openapi["components"]["schemas"][live_interrupt_ref.rsplit("/", 1)[-1]]
    static_interrupt_schema = get_openapi_seed()["paths"]["/desktop/builds/interrupt"]["post"]["requestBody"]["content"]["application/json"]["schema"]
    assert live_interrupt_schema["anyOf"] == static_interrupt_schema["anyOf"]
    assert live_interrupt_schema["properties"] == static_interrupt_schema["properties"]
    assert live_interrupt_schema["additionalProperties"] is static_interrupt_schema["additionalProperties"] is False
    for field_name in ("runId", "run_id"):
        string_schema = live_interrupt_schema["properties"][field_name]["anyOf"][0]
        assert string_schema["minLength"] == 1
        assert string_schema["pattern"] == r".*\S.*"

    processes[0].returncode = 0
    completed = client.get("/desktop/builds/status", params={"run_id": started_payload["runId"]})

    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"
    assert completed.json()["exitCode"] == 0
    assert client.get("/desktop/builds/status", params={"run_id": started_payload["runId"]}).json() == completed.json()

    second = client.post("/desktop/builds", json={"projectRoot": "/tmp/PIHC3", "mode": "cached"}).json()
    interrupted = client.post("/desktop/builds/interrupt", json={"runId": second["runId"]})

    assert interrupted.status_code == 200
    assert interrupted.json()["status"] == "interrupted"
    assert processes[1].terminated is True


def test_native_web_bridge_shutdown_reaps_every_active_build(monkeypatch) -> None:
    from fastapi.testclient import TestClient

    import paradev.desktop.builds as desktop_builds
    from paradev.surfaces.rest import build_app

    processes: list[FakeProcess] = []

    def fake_popen(command, cwd=None, stdout=None, stderr=None, start_new_session=False):
        process = FakeProcess()
        processes.append(process)
        return process

    monkeypatch.setattr(desktop_builds.subprocess, "Popen", fake_popen)

    with TestClient(build_app()) as client:
        first = client.post(
            "/desktop/builds",
            json={
                "projectRoot": "/tmp/PIHC3",
                "target": {"kind": "module", "id": "focus_tree/GER_main"},
            },
        )
        second = client.post(
            "/desktop/builds",
            json={
                "projectRoot": "/tmp/PIHC3-other",
                "target": {"kind": "module", "id": "focus_tree/ITA_main"},
            },
        )
        assert first.status_code == 200
        assert second.status_code == 200
        assert len(client.get("/desktop/builds").json()["runs"]) == 2

    assert len(processes) == 2
    assert all(process.terminated for process in processes)


def test_native_web_bridge_scopes_build_conflicts_by_project_root(monkeypatch) -> None:
    from fastapi.testclient import TestClient

    import paradev.desktop.builds as desktop_builds
    from paradev.surfaces.rest import build_app

    processes: list[FakeProcess] = []

    def fake_popen(command, cwd=None, stdout=None, stderr=None, start_new_session=False):
        process = FakeProcess()
        processes.append(process)
        return process

    monkeypatch.setattr(desktop_builds.subprocess, "Popen", fake_popen)
    shared_target = {"kind": "module", "id": "focus_tree/GER_main"}
    sibling_target = {"kind": "module", "id": "focus_tree/ITA_main"}

    with TestClient(build_app()) as client:
        alpha_partial = client.post(
            "/desktop/builds",
            json={"projectRoot": "/tmp/Alpha", "target": shared_target},
        )
        alpha_sibling = client.post(
            "/desktop/builds",
            json={"projectRoot": "/tmp/Alpha", "target": sibling_target},
        )
        beta_partial = client.post(
            "/desktop/builds",
            json={"projectRoot": "/tmp/Beta", "target": shared_target},
        )

        assert alpha_partial.status_code == 200
        assert alpha_sibling.status_code == 200
        assert beta_partial.status_code == 200
        assert {run["runId"] for run in client.get("/desktop/builds", params={"project_root": "/tmp/Alpha"}).json()["runs"]} == {
            alpha_partial.json()["runId"],
            alpha_sibling.json()["runId"],
        }
        assert (
            client.post(
                "/desktop/builds",
                json={"projectRoot": "/tmp/Alpha", "target": shared_target},
            ).status_code
            == 400
        )
        assert client.post("/desktop/builds", json={"projectRoot": "/tmp/Alpha"}).status_code == 400

        beta_interrupt = client.post(
            "/desktop/builds/interrupt",
            json={"runId": beta_partial.json()["runId"]},
        )
        assert beta_interrupt.status_code == 200

        beta_full = client.post("/desktop/builds", json={"projectRoot": "/tmp/Beta"})
        assert beta_full.status_code == 200
        assert (
            client.post(
                "/desktop/builds",
                json={
                    "projectRoot": "/tmp/Beta",
                    "target": {"kind": "module", "id": "focus_tree/ITA_main"},
                },
            ).status_code
            == 400
        )

        for run in (alpha_partial, alpha_sibling, beta_full):
            interrupted = client.post("/desktop/builds/interrupt", json={"runId": run.json()["runId"]})
            assert interrupted.status_code == 200

        alpha_full = client.post("/desktop/builds", json={"projectRoot": "/tmp/Alpha"})
        second_beta_full = client.post("/desktop/builds", json={"projectRoot": "/tmp/Beta"})
        assert alpha_full.status_code == 200
        assert second_beta_full.status_code == 200
        assert (
            client.post(
                "/desktop/builds",
                json={"projectRoot": "/tmp/Alpha", "target": sibling_target},
            ).status_code
            == 400
        )

    assert len(processes) == 6
    assert all(process.terminated for process in processes)


def test_native_web_bridge_opens_paths_and_runs_hoi4(monkeypatch, tmp_path: Path) -> None:
    from fastapi.testclient import TestClient

    import paradev.desktop.shell as shell
    from paradev.surfaces.rest import build_app

    commands: list[tuple[list[str], bool, dict[str, object]]] = []

    def fake_cmd(command, wait=True, **kwargs):
        commands.append((list(command), wait, kwargs))
        return None

    monkeypatch.setattr(shell, "cmd", fake_cmd)
    monkeypatch.setattr(shell, "_steam_launch_problem", lambda platform: None)
    client = TestClient(build_app())

    opened = client.post("/desktop/open-path", json={"path": str(tmp_path), "target": "vscode"})
    path_status = client.get("/desktop/path-status", params={"path": str(tmp_path)})
    launched = client.post("/desktop/run-hoi4", json={"mode": "steam"})

    assert opened.status_code == 200
    assert opened.json()["schema"] == "paradev.desktop.open-path.v1"
    assert opened.json()["command"] == ["code", "-r", str(tmp_path)]
    assert path_status.status_code == 200
    assert path_status.json() == {
        "schema": "paradev.desktop.path-status.v1",
        "inputPath": str(tmp_path),
        "path": str(tmp_path.resolve()),
        "exists": True,
        "kind": "directory",
        "readable": True,
        "openable": True,
    }
    assert launched.status_code == 200
    assert launched.json()["schema"] == "paradev.desktop.game-launch.v1"
    assert launched.json()["gameRoot"] == "steam://run/394360"
    expected_streams = {
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    assert commands[0] == (["code", "-r", str(tmp_path)], False, expected_streams)
    assert commands[1][0][-1] == "steam://run/394360"
    assert commands[1][1] is False
    assert commands[1][2] == expected_streams


def test_native_web_bridge_reads_authoritative_hoi4_launch_readiness(monkeypatch) -> None:
    from fastapi.testclient import TestClient

    import paradev.surfaces.rest as rest_surface

    def fake_readiness(project_root: str) -> dict[str, object]:
        return {
            "schema": "paradev.desktop.hoi4-launch-readiness.v1",
            "code": "whole_project_baseline_missing",
            "game": "hoi4",
            "outputRoot": "/mods/PIHC3",
            "projectId": "PIHC3",
            "projectRoot": project_root,
            "ready": False,
            "reason": "Build the whole project once.",
        }

    monkeypatch.setattr(rest_surface, "desktop_hoi4_launch_readiness", fake_readiness)
    client = TestClient(rest_surface.build_app())

    response = client.get(
        "/desktop/hoi4-launch-readiness",
        params={"project_root": "/tmp/PIHC3"},
    )

    assert response.status_code == 200
    assert response.json() == fake_readiness("/tmp/PIHC3")


def test_native_web_bridge_project_inspect_reports_invalid_project_as_bad_request(
    tmp_path: Path,
) -> None:
    from fastapi.testclient import TestClient

    from paradev.surfaces.rest import build_app

    client = TestClient(build_app(), raise_server_exceptions=False)
    missing_project = tmp_path / "missing-project"

    response = client.get(
        "/projects/inspect",
        params={"path": str(missing_project), "kind": "diagnostics"},
    )

    assert response.status_code == 400
    assert "paradev.yaml" in response.json()["detail"]


def test_native_web_bridge_catalog_query_uses_bounded_edge_defaults(
    monkeypatch,
) -> None:
    from fastapi.testclient import TestClient

    from paradev.surfaces.rest import build_app

    calls: list[tuple[str, dict[str, object]]] = []

    class FakeProject:
        def inspect(self, kind: str, **filters: object) -> dict[str, object]:
            calls.append((kind, filters))
            return {"schema": "fake.catalog-query", "rows": []}

    monkeypatch.setattr("paradev.surfaces.rest.open_project", lambda _path: FakeProject())
    client = TestClient(build_app())

    default_response = client.get(
        "/projects/inspect",
        params={"path": "/tmp/PIHC3", "kind": "CATALOG_QUERY", "entity": "module"},
    )
    hydrated_response = client.get(
        "/projects/inspect",
        params={
            "path": "/tmp/PIHC3",
            "kind": "catalog-query",
            "limit": 1,
            "offset": 2,
            "include_data": True,
        },
    )

    assert default_response.status_code == 200, default_response.text
    assert hydrated_response.status_code == 200, hydrated_response.text
    assert calls == [
        (
            "catalog-query",
            {"entity": "module", "limit": 100, "offset": 0, "include_data": False},
        ),
        (
            "catalog-query",
            {"limit": 1, "offset": 2, "include_data": True},
        ),
    ]


def test_native_web_bridge_module_remove_uses_the_existing_destructive_route(
    monkeypatch,
) -> None:
    from fastapi.testclient import TestClient

    from paradev.surfaces.rest import build_app

    expected = {
        "schema": "paradev.module.remove.v1",
        "module_id": "modifier/demo",
        "removed": True,
    }
    calls: list[tuple[str, str | None, bool]] = []

    class FakeProject:
        def remove_module(self, module_id: str, *, source_root: str | None = None, write: bool = False) -> dict[str, object]:
            calls.append((module_id, source_root, write))
            return expected

    monkeypatch.setattr("paradev.surfaces.rest.open_project", lambda _path: FakeProject())
    client = TestClient(build_app())

    response = client.delete(
        "/projects/modules/remove",
        params={
            "path": "/tmp/PIHC3",
            "module_id": "modifier/demo",
            "source_root": "src",
            "write": True,
        },
    )

    assert response.status_code == 200, response.text
    assert response.json() == expected
    assert calls == [("modifier/demo", "src", True)]


def test_native_web_bridge_catalog_query_rejects_unsafe_pages(monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from paradev.surfaces.rest import build_app

    monkeypatch.setattr("paradev.surfaces.rest.open_project", lambda _path: None)
    client = TestClient(build_app())

    oversized = client.get("/projects/inspect", params={"kind": "catalog-query", "limit": 201})
    hydrated = client.get(
        "/projects/inspect",
        params={"kind": "catalog-query", "limit": 2, "include_data": True},
    )

    assert oversized.status_code == 400
    assert "integer from 1 to 200" in oversized.json()["detail"]
    assert hydrated.status_code == 400
    assert "hydrated requests must use limit 1" in hydrated.json()["detail"]


def test_native_web_bridge_catalog_status_uses_the_read_only_project_resource(
    monkeypatch,
) -> None:
    from fastapi.testclient import TestClient

    from paradev.surfaces.rest import build_app

    expected = {
        "schema": "paradev.hb.catalog-status.v1",
        "project_id": "PIHC3",
        "database": "/tmp/PIHC3/.paradev/.cache/hb/catalog.sqlite",
        "status": "missing",
        "code": "catalog.missing",
    }
    roots: list[str] = []
    calls: list[str] = []

    class FakeProject:
        def catalog_status(self) -> dict[str, object]:
            calls.append("catalog_status")
            return expected

    def fake_open_project(path: str) -> FakeProject:
        roots.append(path)
        return FakeProject()

    monkeypatch.setattr("paradev.surfaces.rest.open_project", fake_open_project)
    client = TestClient(build_app())

    response = client.get("/projects/catalog", params={"path": "/tmp/PIHC3"})

    assert response.status_code == 200, response.text
    assert response.json() == expected
    assert roots == ["/tmp/PIHC3"]
    assert calls == ["catalog_status"]


def test_native_web_bridge_openapi_documents_catalog_query_edge() -> None:
    from paradev.surfaces.rest import get_openapi_seed

    edge = get_openapi_seed()["paths"]["/projects/inspect"]["get"]["x-paradev-catalog-query-edge"]

    assert edge == {
        "kind": "catalog-query",
        "default_limit": 100,
        "max_limit": 200,
        "default_offset": 0,
        "default_include_data": False,
        "max_hydrated_limit": 1,
    }


def test_native_web_bridge_config_endpoints_are_browser_safe(cm_paradev_lock) -> None:
    from fastapi.testclient import TestClient

    from paradev.config import CM_PARADEV
    from paradev.desktop import desktop_read_app_config, desktop_write_app_config
    from paradev.surfaces.rest import build_app

    previous_app_config = desktop_read_app_config()
    previous_project_name = CM_PARADEV.get("paradev.project.name", default=None)
    previous_parallelism = CM_PARADEV.get("paradev.build.parallelism", default=None)
    previous_strict_metadata = CM_PARADEV.get("paradev.build.strict_metadata", default=None)
    previous_launch_mode = CM_PARADEV.get("paradev.hoi4.launch_mode", default=None)
    previous_game_root = CM_PARADEV.get("paradev.hoi4.game_root", default=None)
    previous_cli_output = CM_PARADEV.get("paradev.cli.output", default=None)
    previous_ai_key_env = CM_PARADEV.get("paradev.ai.key_env", default=None)
    previous_ai_model = CM_PARADEV.get("paradev.ai.model", default=None)
    previous_ai_preset = CM_PARADEV.get("paradev.ai.preset", default=None)
    previous_ai_provider = CM_PARADEV.get("paradev.ai.provider", default=None)
    previous_ai_gateway = CM_PARADEV.get("paradev.ai.gateway", default=None)
    previous_ai_base_url = CM_PARADEV.get("paradev.ai.base_url", default=None)
    previous_ai_chat_default_role = CM_PARADEV.get("paradev.ai.chat.default_role", default=None)
    previous_thumbnail_cache = CM_PARADEV.get("paradev.desktop.thumbnail_cache.max_kb", default=None)
    origin = "http://127.0.0.1:5181"
    app_config = {
        "schema": "paradev.desktop.app-settings.v1",
        "configPage": {"build": {"parallelism": 5}},
    }

    try:
        desktop_write_app_config(app_config)
        client = TestClient(build_app())

        read_response = client.get("/desktop/app-config", headers={"origin": origin})
        preflight_response = client.options(
            "/desktop/config-value",
            headers={
                "origin": origin,
                "access-control-request-method": "PUT",
                "access-control-request-headers": "content-type",
            },
        )
        write_response = client.put(
            "/desktop/config-value",
            json={"key": "paradev.build.parallelism", "value": 3},
            headers={"origin": origin},
        )
        strict_metadata_response = client.put(
            "/desktop/config-value",
            json={"key": "paradev.build.strict_metadata", "value": True},
            headers={"origin": origin},
        )
        strict_metadata_read_response = client.get(
            "/desktop/config-value",
            params={"key": "paradev.build.strict_metadata"},
            headers={"origin": origin},
        )
        project_name_response = client.put(
            "/desktop/config-value",
            json={"key": "paradev.project.name", "value": " PIHC3 Workbench "},
            headers={"origin": origin},
        )
        launch_response = client.put(
            "/desktop/config-value",
            json={"key": "paradev.hoi4.launch_mode", "value": "local"},
            headers={"origin": origin},
        )
        game_root_response = client.put(
            "/desktop/config-value",
            json={
                "key": "paradev.hoi4.game_root",
                "value": " /Games/Hearts of Iron IV ",
            },
            headers={"origin": origin},
        )
        cli_output_response = client.put(
            "/desktop/config-value",
            json={"key": "paradev.cli.output", "value": "json"},
            headers={"origin": origin},
        )
        cli_output_read_response = client.get(
            "/desktop/config-value",
            params={"key": "paradev.cli.output"},
            headers={"origin": origin},
        )
        ai_key_env_response = client.put(
            "/desktop/config-value",
            json={"key": "paradev.ai.key_env", "value": " VISIBLE_DEEPSEEK_KEY "},
            headers={"origin": origin},
        )
        ai_model_response = client.put(
            "/desktop/config-value",
            json={"key": "paradev.ai.model", "value": " deepseek-reasoner "},
            headers={"origin": origin},
        )
        ai_preset_response = client.put(
            "/desktop/config-value",
            json={"key": "paradev.ai.preset", "value": "reason"},
            headers={"origin": origin},
        )
        ai_provider_response = client.put(
            "/desktop/config-value",
            json={"key": "paradev.ai.provider", "value": " deepseek "},
            headers={"origin": origin},
        )
        ai_gateway_response = client.put(
            "/desktop/config-value",
            json={"key": "paradev.ai.gateway", "value": " openrouter "},
            headers={"origin": origin},
        )
        ai_base_url_response = client.put(
            "/desktop/config-value",
            json={"key": "paradev.ai.base_url", "value": " https://proxy.example/v1 "},
            headers={"origin": origin},
        )
        ai_chat_default_role_response = client.put(
            "/desktop/config-value",
            json={"key": "paradev.ai.chat.default_role", "value": "build"},
            headers={"origin": origin},
        )
        thumbnail_cache_response = client.put(
            "/desktop/config-value",
            json={"key": "paradev.desktop.thumbnail_cache.max_kb", "value": 384},
            headers={"origin": origin},
        )
        thumbnail_cache_read_response = client.get(
            "/desktop/config-value",
            params={"key": "paradev.desktop.thumbnail_cache.max_kb"},
            headers={"origin": origin},
        )

        assert read_response.status_code == 200, read_response.text
        assert read_response.json() == app_config
        assert preflight_response.status_code == 200, preflight_response.text
        assert preflight_response.headers["access-control-allow-origin"] == origin
        assert "PUT" in preflight_response.headers["access-control-allow-methods"]
        assert write_response.status_code == 200, write_response.text
        assert write_response.headers["access-control-allow-origin"] == origin
        assert write_response.json()["value"] == 3
        assert strict_metadata_response.status_code == 200, strict_metadata_response.text
        assert strict_metadata_response.headers["access-control-allow-origin"] == origin
        assert strict_metadata_response.json()["value"] is True
        assert strict_metadata_read_response.status_code == 200, strict_metadata_read_response.text
        assert strict_metadata_read_response.headers["access-control-allow-origin"] == origin
        assert strict_metadata_read_response.json()["value"] is True
        assert project_name_response.status_code == 200, project_name_response.text
        assert project_name_response.headers["access-control-allow-origin"] == origin
        assert project_name_response.json()["value"] == "PIHC3 Workbench"
        assert launch_response.status_code == 200, launch_response.text
        assert launch_response.headers["access-control-allow-origin"] == origin
        assert launch_response.json()["value"] == "local"
        assert game_root_response.status_code == 200, game_root_response.text
        assert game_root_response.headers["access-control-allow-origin"] == origin
        assert game_root_response.json()["value"] == "/Games/Hearts of Iron IV"
        assert cli_output_response.status_code == 200, cli_output_response.text
        assert cli_output_response.headers["access-control-allow-origin"] == origin
        assert cli_output_response.json()["value"] == "json"
        assert cli_output_read_response.status_code == 200, cli_output_read_response.text
        assert cli_output_read_response.headers["access-control-allow-origin"] == origin
        assert cli_output_read_response.json()["value"] == "json"
        assert ai_key_env_response.status_code == 200, ai_key_env_response.text
        assert ai_key_env_response.headers["access-control-allow-origin"] == origin
        assert ai_key_env_response.json()["value"] == "VISIBLE_DEEPSEEK_KEY"
        assert ai_model_response.status_code == 200, ai_model_response.text
        assert ai_model_response.headers["access-control-allow-origin"] == origin
        assert ai_model_response.json()["value"] == "deepseek-reasoner"
        assert ai_preset_response.status_code == 200, ai_preset_response.text
        assert ai_preset_response.headers["access-control-allow-origin"] == origin
        assert ai_preset_response.json()["value"] == "reason"
        assert ai_provider_response.status_code == 200, ai_provider_response.text
        assert ai_provider_response.headers["access-control-allow-origin"] == origin
        assert ai_provider_response.json()["value"] == "deepseek"
        assert ai_gateway_response.status_code == 200, ai_gateway_response.text
        assert ai_gateway_response.headers["access-control-allow-origin"] == origin
        assert ai_gateway_response.json()["value"] == "openrouter"
        assert ai_base_url_response.status_code == 200, ai_base_url_response.text
        assert ai_base_url_response.headers["access-control-allow-origin"] == origin
        assert ai_base_url_response.json()["value"] == "https://proxy.example/v1"
        assert ai_chat_default_role_response.status_code == 200, ai_chat_default_role_response.text
        assert ai_chat_default_role_response.headers["access-control-allow-origin"] == origin
        assert ai_chat_default_role_response.json()["value"] == "build"
        assert thumbnail_cache_response.status_code == 200, thumbnail_cache_response.text
        assert thumbnail_cache_response.headers["access-control-allow-origin"] == origin
        assert thumbnail_cache_response.json()["value"] == 384
        assert thumbnail_cache_read_response.status_code == 200, thumbnail_cache_read_response.text
        assert thumbnail_cache_read_response.headers["access-control-allow-origin"] == origin
        assert thumbnail_cache_read_response.json()["value"] == 384
    finally:
        if previous_app_config is None:
            CM_PARADEV.unset("paradev.desktop.gui")
        else:
            desktop_write_app_config(previous_app_config)
        if previous_project_name is None:
            CM_PARADEV.unset("paradev.project.name")
        else:
            CM_PARADEV.set("paradev.project.name", previous_project_name)
        if previous_parallelism is None:
            CM_PARADEV.unset("paradev.build.parallelism")
        else:
            CM_PARADEV.set("paradev.build.parallelism", previous_parallelism)
        if previous_strict_metadata is None or isinstance(previous_strict_metadata, MappingProxyType):
            CM_PARADEV.unset("paradev.build.strict_metadata")
        else:
            CM_PARADEV.set("paradev.build.strict_metadata", previous_strict_metadata)
        if previous_launch_mode is None or isinstance(previous_launch_mode, MappingProxyType):
            CM_PARADEV.unset("paradev.hoi4.launch_mode")
        else:
            CM_PARADEV.set("paradev.hoi4.launch_mode", previous_launch_mode)
        if previous_game_root is None or isinstance(previous_game_root, MappingProxyType):
            CM_PARADEV.unset("paradev.hoi4.game_root")
        else:
            CM_PARADEV.set("paradev.hoi4.game_root", previous_game_root)
        if previous_cli_output is None or isinstance(previous_cli_output, MappingProxyType):
            CM_PARADEV.unset("paradev.cli.output")
        else:
            CM_PARADEV.set("paradev.cli.output", previous_cli_output)
        if previous_ai_key_env is None or isinstance(previous_ai_key_env, MappingProxyType):
            CM_PARADEV.unset("paradev.ai.key_env")
        else:
            CM_PARADEV.set("paradev.ai.key_env", previous_ai_key_env)
        if previous_ai_model is None or isinstance(previous_ai_model, MappingProxyType):
            CM_PARADEV.unset("paradev.ai.model")
        else:
            CM_PARADEV.set("paradev.ai.model", previous_ai_model)
        if previous_ai_preset is None or isinstance(previous_ai_preset, MappingProxyType):
            CM_PARADEV.unset("paradev.ai.preset")
        else:
            CM_PARADEV.set("paradev.ai.preset", previous_ai_preset)
        if previous_ai_provider is None or isinstance(previous_ai_provider, MappingProxyType):
            CM_PARADEV.unset("paradev.ai.provider")
        else:
            CM_PARADEV.set("paradev.ai.provider", previous_ai_provider)
        if previous_ai_gateway is None or isinstance(previous_ai_gateway, MappingProxyType):
            CM_PARADEV.unset("paradev.ai.gateway")
        else:
            CM_PARADEV.set("paradev.ai.gateway", previous_ai_gateway)
        if previous_ai_base_url is None or isinstance(previous_ai_base_url, MappingProxyType):
            CM_PARADEV.unset("paradev.ai.base_url")
        else:
            CM_PARADEV.set("paradev.ai.base_url", previous_ai_base_url)
        if previous_ai_chat_default_role is None or isinstance(previous_ai_chat_default_role, MappingProxyType):
            CM_PARADEV.unset("paradev.ai.chat.default_role")
        else:
            CM_PARADEV.set("paradev.ai.chat.default_role", previous_ai_chat_default_role)
        if previous_thumbnail_cache is None or isinstance(previous_thumbnail_cache, MappingProxyType):
            CM_PARADEV.unset("paradev.desktop.thumbnail_cache.max_kb")
        else:
            CM_PARADEV.set("paradev.desktop.thumbnail_cache.max_kb", previous_thumbnail_cache)
