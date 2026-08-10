"""Dependency and compatibility gates for project API services."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_project_api_import_is_transport_neutral_in_fresh_process() -> None:
    result = _run_import_probe("""
import sys
import paradev.api.projects
assert "paradev.surfaces.rest" not in sys.modules
assert "paradev.desktop.backend" not in sys.modules
""")

    assert result.returncode == 0, result.stderr


def test_desktop_backend_import_does_not_load_rest_in_fresh_process() -> None:
    result = _run_import_probe("""
import sys
import paradev.desktop.backend
assert "paradev.surfaces.rest" not in sys.modules
assert not any(name.startswith("paradev.surfaces") for name in sys.modules)
""")

    assert result.returncode == 0, result.stderr


def test_desktop_and_rest_import_in_either_order() -> None:
    for first, second in (
        ("paradev.desktop.backend", "paradev.surfaces.rest"),
        ("paradev.surfaces.rest", "paradev.desktop.backend"),
    ):
        result = _run_import_probe(f"import {first}\nimport {second}\n")
        assert result.returncode == 0, result.stderr


def test_rest_and_public_api_keep_project_service_aliases() -> None:
    import paradev.api as public_api
    from paradev.api import projects
    from paradev.surfaces import rest

    assert public_api.apply_project_draft is projects.apply_project_draft
    assert public_api.create_module_batch is projects.create_module_batch
    assert public_api.create_module_draft is projects.create_module_draft
    assert public_api.read_project_source is projects.read_project_source_text
    assert public_api.read_project_source_form is projects.read_project_source_form
    assert rest.apply_project_draft is projects.apply_project_draft
    assert rest.create_module_batch is projects.create_module_batch
    assert rest.create_module_draft is projects.create_module_draft
    assert rest.normalize_project_draft_mutations is projects.normalize_project_draft_mutations
    assert rest.plan_project_localization_update is projects.plan_project_localization_update
    assert rest.plan_project_source_form_updates is projects.plan_project_source_form_updates
    assert rest.read_project_localization_workspace is projects.read_project_localization_workspace
    assert rest.read_project_source is projects.read_project_source_text
    assert rest.read_project_source_form is projects.read_project_source_form


def test_desktop_backend_source_has_no_surface_dependency() -> None:
    backend_source = Path("src/paradev/desktop/backend.py").read_text(encoding="utf-8")

    assert "paradev.surfaces" not in backend_source


def _run_import_probe(source: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", source],
        check=False,
        capture_output=True,
        text=True,
    )
