"""REST and frontend contracts for transactional module batch creation."""

from __future__ import annotations

import pytest

from paradev.sdk import Project, plan_frontend_api_rest_request
from paradev.surfaces.rest import create_module_batch


def _batch_request(project: Project) -> dict[str, object]:
    return {
        "project_id": project.project_id,
        "project_root": str(project.root),
        "modules": [
            {
                "family": "idea",
                "object_id": object_id,
                "values": {"title": f"Idea {object_id}"},
            }
            for object_id in ("A", "B")
        ],
        "write": False,
    }


def test_create_module_batch_rest_helper_plans_and_applies_with_hash(tmp_path) -> None:
    project = Project.create(tmp_path / "starter")
    request = _batch_request(project)

    plan = create_module_batch(request=request)
    applied = create_module_batch(request={**request, "write": True, "plan_hash": plan["plan_hash"]})

    assert plan["schema"] == "paradev.sdk.module_batch.v1"
    assert plan["blocked"] is False
    assert plan["applied"] is False
    assert plan["counts"] == {"create": 2, "created": 0, "unchanged": 0, "blocked": 0}
    assert applied["blocked"] is False
    assert applied["applied"] is True
    assert applied["counts"] == {"create": 0, "created": 2, "unchanged": 0, "blocked": 0}
    assert (project.source_roots[0] / "modules/idea/A/meta.yaml").is_file()
    assert (project.source_roots[0] / "modules/idea/B/meta.yaml").is_file()


@pytest.mark.parametrize(
    ("update", "message"),
    [
        ({"force": True}, "unsupported fields: force"),
        ({"modules": {"family": "idea"}}, "must be a JSON array"),
        ({"modules": []}, "must contain at least one module request"),
    ],
)
def test_create_module_batch_rest_helper_rejects_invalid_request_envelope(
    tmp_path,
    update: dict[str, object],
    message: str,
) -> None:
    project = Project.create(tmp_path / "starter")

    with pytest.raises(ValueError, match=message):
        create_module_batch(request={**_batch_request(project), **update})


def test_module_create_batch_frontend_plan_executes_through_rest_route(tmp_path) -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces.rest import build_app

    project = Project.create(tmp_path / "starter")
    modules = [
        {
            "family": "idea",
            "object_id": "REST_IDEA",
            "values": {"title": "REST Idea"},
        }
    ]
    plan = plan_frontend_api_rest_request(
        "module.create_batch",
        {
            "project_id": project.project_id,
            "path": str(project.root),
            "modules": modules,
        },
    )

    assert plan["method"] == "POST"
    assert plan["path"] == "/projects/modules/create-batch"
    assert plan["query"] == {}
    assert plan["body"] == {
        "project_id": project.project_id,
        "project_root": str(project.root),
        "modules": modules,
        "write": False,
    }

    client = testclient.TestClient(build_app())
    response = client.post(plan["path"], json=plan["body"])

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["schema"] == "paradev.sdk.module_batch.v1"
    assert payload["blocked"] is False
    assert payload["modules"][0]["module_id"] == "idea/REST_IDEA"

    invalid = client.post(plan["path"], json={**plan["body"], "force": True})

    assert invalid.status_code == 400
    assert "unsupported fields: force" in invalid.json()["detail"]
