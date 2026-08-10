"""REST and frontend contracts for guarded module transactions."""

from __future__ import annotations

import os

import pytest

from paradev.sdk import Project, plan_frontend_api_rest_request
from paradev.surfaces.rest import (
    MODULE_ACTIVITY_SET_PATH,
    MODULE_COLLECTION_SET_PATH,
    MODULE_METADATA_CLEAN_PATH,
    clean_module_metadata,
    duplicate_module,
    set_module_active,
    set_module_collection,
)

SOURCE_MODULE_ID = "modifier/starter_mod_starter_modifier"


def _duplicate_request(project: Project, *, write: bool = False) -> dict[str, object]:
    return {
        "project_root": str(project.root),
        "module_id": SOURCE_MODULE_ID,
        "object_id": "starter_mod_copied_modifier",
        "write": write,
    }


@pytest.mark.skipif(os.name != "posix", reason="Descriptor-anchored duplicate publication is POSIX-only.")
def test_duplicate_module_rest_helper_plans_and_applies_exact_hash(tmp_path) -> None:
    project = Project.create(tmp_path / "starter-mod", title="Starter Mod")
    source = project.source_roots[0] / "modules/modifier/starter_mod_starter_modifier"
    (source / "asset.bin").write_bytes(b"\x00ParaDev\xff")
    (source / ".paradev").mkdir()
    (source / ".paradev/state.yaml").write_text("owner: system\n", encoding="utf-8")
    request = _duplicate_request(project)

    plan = duplicate_module(request=request)
    applied = duplicate_module(
        request={
            **request,
            "write": True,
            "plan_hash": plan["plan_hash"],
        }
    )

    destination = project.source_roots[0] / "modules/modifier/starter_mod_copied_modifier"
    assert plan["schema"] == "paradev.sdk.module_duplicate.v1"
    assert plan["status"] == "planned"
    assert plan["blocked"] is False
    assert plan["identity_mode"] == "rewrite"
    assert plan["content_rewritten"] is True
    assert plan["totals"]["excluded_count"] == 1
    assert applied["status"] == "duplicated"
    assert applied["applied"] is True
    assert applied["plan_hash"] == plan["plan_hash"]
    assert (destination / "asset.bin").read_bytes() == b"\x00ParaDev\xff"
    assert not (destination / ".paradev").exists()


def test_duplicate_module_rest_helper_rejects_unrecognized_fields(tmp_path) -> None:
    project = Project.create(tmp_path / "starter-mod", title="Starter Mod")

    with pytest.raises(ValueError, match="unsupported fields: force"):
        duplicate_module(request={**_duplicate_request(project), "force": True})


def test_module_duplicate_frontend_plan_executes_through_rest_route(tmp_path) -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces.rest import build_app

    project = Project.create(tmp_path / "starter-mod", title="Starter Mod")
    plan = plan_frontend_api_rest_request(
        "module.duplicate",
        {
            "path": str(project.root),
            "module_id": SOURCE_MODULE_ID,
            "object_id": "starter_mod_copied_modifier",
        },
    )

    assert plan["method"] == "POST"
    assert plan["path"] == "/projects/modules/duplicate"
    assert plan["query"] == {"identity": "rewrite"}
    assert plan["body"] == {
        "project_root": str(project.root),
        "module_id": SOURCE_MODULE_ID,
        "object_id": "starter_mod_copied_modifier",
        "write": False,
    }

    client = testclient.TestClient(build_app())
    response = client.post(plan["path"], json=plan["body"])

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["schema"] == "paradev.sdk.module_duplicate.v1"
    assert payload["blocked"] is False
    assert payload["module_id"] == "modifier/starter_mod_copied_modifier"

    invalid = client.post(plan["path"], json={**plan["body"], "force": True})

    assert invalid.status_code == 400
    assert "unsupported fields: force" in invalid.json()["detail"]


def test_module_metadata_clean_rest_helper_and_route_forward_guarded_plan(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces.rest import build_app

    project = Project.create(tmp_path / "starter-mod", title="Starter Mod")
    calls: list[dict[str, object]] = []

    def cleanup(
        self: Project,
        *,
        family: str | None = None,
        module_id: str | None = None,
        source_root: str | None = None,
        write: bool = False,
        plan_hash: str | None = None,
    ) -> dict[str, object]:
        calls.append(
            {
                "family": family,
                "module_id": module_id,
                "source_root": source_root,
                "write": write,
                "plan_hash": plan_hash,
            }
        )
        return {
            "schema": "paradev.sdk.module_metadata_cleanup.v1",
            "applied": write,
            "blocked": False,
            "plan_hash": "reviewed-plan",
        }

    monkeypatch.setattr(Project, "clean_module_metadata", cleanup)
    rest_plan = plan_frontend_api_rest_request(
        "module.metadata.clean",
        {
            "path": str(project.root),
            "family": "idea",
            "source_root": "src",
        },
    )
    plan = clean_module_metadata(
        request={
            "project_root": str(project.root),
            "family": "idea",
            "source_root": "src",
        }
    )
    client = testclient.TestClient(build_app())
    response = client.post(
        MODULE_METADATA_CLEAN_PATH,
        json={
            "project_root": str(project.root),
            "module_id": "idea/sample",
            "write": True,
            "plan_hash": plan["plan_hash"],
        },
    )

    assert rest_plan["method"] == "POST"
    assert rest_plan["path"] == MODULE_METADATA_CLEAN_PATH
    assert rest_plan["query"] == {}
    assert rest_plan["body"] == {
        "project_root": str(project.root),
        "family": "idea",
        "source_root": "src",
        "write": False,
    }
    assert plan["applied"] is False
    assert response.status_code == 200, response.text
    assert response.json()["applied"] is True
    assert calls == [
        {
            "family": "idea",
            "module_id": None,
            "source_root": "src",
            "write": False,
            "plan_hash": None,
        },
        {
            "family": None,
            "module_id": "idea/sample",
            "source_root": None,
            "write": True,
            "plan_hash": "reviewed-plan",
        },
    ]
    with pytest.raises(ValueError, match="unsupported fields: force"):
        clean_module_metadata(
            request={
                "project_root": str(project.root),
                "force": True,
            }
        )


def test_module_collection_rest_helper_route_and_frontend_plan_forward_exact_guard(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces.rest import build_app

    project = Project.create(tmp_path / "starter-mod", title="Starter Mod")
    calls: list[dict[str, object]] = []

    def update_collection(
        self: Project,
        module_id: str,
        collection_id: str | None,
        *,
        source_root: str | None = None,
        write: bool = False,
        plan_hash: str | None = None,
    ) -> dict[str, object]:
        calls.append(
            {
                "module_id": module_id,
                "collection_id": collection_id,
                "source_root": source_root,
                "write": write,
                "plan_hash": plan_hash,
            }
        )
        return {
            "schema": "paradev.sdk.module_collection_update.v1",
            "blocked": False,
            "applied": write,
            "plan_hash": "reviewed-plan",
        }

    monkeypatch.setattr(Project, "set_module_collection", update_collection)
    rest_plan = plan_frontend_api_rest_request(
        "module.collection.set",
        {
            "path": str(project.root),
            "module_id": SOURCE_MODULE_ID,
            "collection_id": "starter_modifiers",
            "source_root": "src",
        },
    )
    plan = set_module_collection(request=rest_plan["body"])
    client = testclient.TestClient(build_app())
    response = client.post(
        MODULE_COLLECTION_SET_PATH,
        json={
            "project_root": str(project.root),
            "module_id": SOURCE_MODULE_ID,
            "collection_id": None,
            "write": True,
            "plan_hash": plan["plan_hash"],
        },
    )

    assert rest_plan["schema"] == "paradev.sdk.frontend-api.rest-request.v1"
    assert rest_plan["operation_id"] == "module.collection.set"
    assert rest_plan["method"] == "POST"
    assert rest_plan["path"] == MODULE_COLLECTION_SET_PATH
    assert rest_plan["query"] == {}
    assert rest_plan["body"] == {
        "project_root": str(project.root),
        "module_id": SOURCE_MODULE_ID,
        "collection_id": "starter_modifiers",
        "source_root": "src",
        "write": False,
    }
    assert response.status_code == 200, response.text
    assert response.json()["applied"] is True
    assert calls == [
        {
            "module_id": SOURCE_MODULE_ID,
            "collection_id": "starter_modifiers",
            "source_root": "src",
            "write": False,
            "plan_hash": None,
        },
        {
            "module_id": SOURCE_MODULE_ID,
            "collection_id": None,
            "source_root": None,
            "write": True,
            "plan_hash": "reviewed-plan",
        },
    ]
    with pytest.raises(ValueError, match="unsupported fields: force"):
        set_module_collection(
            request={
                "project_root": str(project.root),
                "module_id": SOURCE_MODULE_ID,
                "force": True,
            }
        )


def test_module_activity_rest_and_frontend_contract_share_guarded_request(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces.rest import build_app

    project = Project.create(tmp_path / "starter-mod", title="Starter Mod")
    calls: list[dict[str, object]] = []

    def update_activity(
        self: Project,
        module_id: str,
        active: bool,
        *,
        source_root: str | None = None,
        write: bool = False,
        plan_hash: str | None = None,
    ) -> dict[str, object]:
        calls.append(
            {
                "module_id": module_id,
                "active": active,
                "source_root": source_root,
                "write": write,
                "plan_hash": plan_hash,
            }
        )
        return {
            "schema": "paradev.sdk.module_activity_update.v1",
            "blocked": False,
            "applied": write,
            "plan_hash": "reviewed-plan",
        }

    monkeypatch.setattr(Project, "set_module_active", update_activity)
    rest_plan = plan_frontend_api_rest_request(
        "module.activity.set",
        {
            "path": str(project.root),
            "module_id": SOURCE_MODULE_ID,
            "active": False,
            "source_root": "src",
        },
    )
    plan = set_module_active(request=rest_plan["body"])
    client = testclient.TestClient(build_app())
    response = client.post(
        MODULE_ACTIVITY_SET_PATH,
        json={
            "project_root": str(project.root),
            "module_id": SOURCE_MODULE_ID,
            "active": True,
            "write": True,
            "plan_hash": plan["plan_hash"],
        },
    )

    assert rest_plan["operation_id"] == "module.activity.set"
    assert rest_plan["method"] == "POST"
    assert rest_plan["path"] == MODULE_ACTIVITY_SET_PATH
    assert rest_plan["query"] == {}
    assert rest_plan["body"] == {
        "project_root": str(project.root),
        "module_id": SOURCE_MODULE_ID,
        "active": False,
        "source_root": "src",
        "write": False,
    }
    assert response.status_code == 200, response.text
    assert response.json()["applied"] is True
    assert calls == [
        {
            "module_id": SOURCE_MODULE_ID,
            "active": False,
            "source_root": "src",
            "write": False,
            "plan_hash": None,
        },
        {
            "module_id": SOURCE_MODULE_ID,
            "active": True,
            "source_root": None,
            "write": True,
            "plan_hash": "reviewed-plan",
        },
    ]
    with pytest.raises(ValueError, match="unsupported fields: force"):
        set_module_active(
            request={
                "project_root": str(project.root),
                "module_id": SOURCE_MODULE_ID,
                "active": False,
                "force": True,
            }
        )
