"""Synchronous REST build-selection contracts."""

from __future__ import annotations

from collections.abc import Mapping

import pytest

from paradev.surfaces import rest


class _BuildResult:
    def __init__(self, payload: Mapping[str, object]) -> None:
        self.payload = dict(payload)

    def to_dict(self) -> dict[str, object]:
        return dict(self.payload)


class _Project:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def build(self, **options: object) -> _BuildResult:
        self.calls.append(dict(options))
        return _BuildResult({"schema": "test.build-result", "options": dict(options)})


def test_project_build_route_forwards_sdk_selection_and_execution_options(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    project = _Project()
    opened_paths: list[str] = []

    def open_project(path: str) -> _Project:
        opened_paths.append(path)
        return project

    monkeypatch.setattr(rest, "open_project", open_project)
    client = testclient.TestClient(rest.build_app())

    response = client.post(
        "/projects/build",
        params={
            "path": "/workspace/PIHC3",
            "profile": "hoi4",
            "emit_artifacts": True,
            "emit_manifests": True,
            "strict_metadata": True,
            "family": "technology",
            "module_id": "technology/TECHNOLOGY_FIREARM_I",
            "full_rebuild": False,
            "sync_launcher_descriptor": False,
            "parallelism": 4,
        },
    )

    assert response.status_code == 200, response.text
    assert opened_paths == ["/workspace/PIHC3"]
    assert project.calls == [
        {
            "profile": "hoi4",
            "emit_artifacts": True,
            "emit_manifests": True,
            "strict_metadata": True,
            "family": "technology",
            "module_id": "technology/TECHNOLOGY_FIREARM_I",
            "collection_id": None,
            "full_rebuild": False,
            "sync_launcher_descriptor": False,
            "parallelism": 4,
        }
    ]
    assert response.json()["schema"] == "test.build-result"


@pytest.mark.parametrize(
    ("params", "selection"),
    (
        (
            {"family": "idea"},
            {"family": "idea", "module_id": None, "collection_id": None},
        ),
        (
            {"family": "focus", "collection_id": "GER_main"},
            {"family": "focus", "module_id": None, "collection_id": "GER_main"},
        ),
        ({}, {"family": None, "module_id": None, "collection_id": None}),
    ),
)
def test_project_build_route_preserves_selection_defaults(
    monkeypatch: pytest.MonkeyPatch,
    params: dict[str, object],
    selection: dict[str, object],
) -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    project = _Project()
    monkeypatch.setattr(rest, "open_project", lambda _path: project)
    client = testclient.TestClient(rest.build_app())

    response = client.post("/projects/build", params=params)

    assert response.status_code == 200, response.text
    assert {key: project.calls[0][key] for key in selection} == selection
    assert project.calls[0]["full_rebuild"] is False
    assert project.calls[0]["sync_launcher_descriptor"] is True
    assert project.calls[0]["parallelism"] is None


def test_project_build_route_validates_parallelism_before_sdk_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    project = _Project()
    monkeypatch.setattr(rest, "open_project", lambda _path: project)
    client = testclient.TestClient(rest.build_app())

    response = client.post("/projects/build", params={"parallelism": 0})

    assert response.status_code == 422
    assert project.calls == []


def test_project_build_route_returns_sdk_validation_as_bad_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    testclient = pytest.importorskip("fastapi.testclient")

    class RejectingProject:
        def build(self, **_options: object) -> _BuildResult:
            raise ValueError("Pass only one targeted build selector: module_id or collection_id.")

    monkeypatch.setattr(rest, "open_project", lambda _path: RejectingProject())
    client = testclient.TestClient(rest.build_app())

    response = client.post(
        "/projects/build",
        params={
            "module_id": "idea/EXAMPLE",
            "collection_id": "EXAMPLE_COLLECTION",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Pass only one targeted build selector: module_id or collection_id."


def test_project_build_route_executes_targeted_sdk_plan() -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    client = testclient.TestClient(rest.build_app())

    response = client.post(
        "/projects/build",
        params={
            "path": "demos/assets/projects/minimal",
            "family": "focus",
            "module_id": "focus/GER_sample",
            "parallelism": 2,
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["project_id"] == "minimal_hoi4"
    assert payload["summary"]["blocked"] is False
    assert [module["module_id"] for module in payload["modules"]] == ["focus/GER_sample"]


def test_project_build_static_openapi_exposes_sdk_selection_options() -> None:
    operation = rest.get_openapi_seed()["paths"]["/projects/build"]["post"]
    parameters = {parameter["name"]: parameter for parameter in operation["parameters"]}

    assert list(parameters) == [
        "path",
        "profile",
        "emit_artifacts",
        "emit_manifests",
        "strict_metadata",
        "family",
        "module_id",
        "collection_id",
        "full_rebuild",
        "sync_launcher_descriptor",
        "parallelism",
    ]
    assert parameters["family"]["schema"] == {"type": "string"}
    assert parameters["module_id"]["schema"] == {"type": "string"}
    assert parameters["collection_id"]["schema"] == {"type": "string"}
    assert parameters["full_rebuild"]["schema"] == {
        "type": "boolean",
        "default": False,
    }
    assert parameters["sync_launcher_descriptor"]["schema"] == {
        "type": "boolean",
        "default": True,
    }
    assert parameters["parallelism"]["schema"] == {
        "type": "integer",
        "minimum": 1,
    }
    assert operation["responses"]["400"]["description"] == "Invalid project path or build options."

    row = rest.get_rest_api_selection(symbol="POST /projects/build")
    assert row["inputs"] == (
        "query:path, query:profile, query:emit_artifacts, query:emit_manifests, "
        "query:strict_metadata, query:family, query:module_id, query:collection_id, "
        "query:full_rebuild, query:sync_launcher_descriptor, query:parallelism"
    )
    assert row["raises"] == "400 Invalid project path or build options."
