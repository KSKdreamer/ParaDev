"""REST coverage for guarded project-language configuration."""

from pathlib import Path

import pytest

from paradev.sdk import Project


def test_project_language_rest_plans_then_applies_exact_revision(
    tmp_path: Path,
) -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces.rest import build_app

    project = Project.create(tmp_path / "starter", title="Starter")
    client = testclient.TestClient(build_app())
    query = {"path": str(project.root), "preferred_language": "zh"}

    planned_response = client.patch("/projects/language", params=query)
    assert planned_response.status_code == 200
    plan = planned_response.json()
    assert plan["blocked"] is False
    assert plan["written"] is False

    applied_response = client.patch(
        "/projects/language",
        params={
            **query,
            "write": True,
            "plan_hash": plan["plan_hash"],
        },
    )
    assert applied_response.status_code == 200
    payload = applied_response.json()
    assert payload["blocked"] is False
    assert payload["written"] is True
    assert Project.load(project.root).preferred_language == "zh"
