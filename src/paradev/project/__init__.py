"""Project discovery and manifest package."""

from __future__ import annotations

from .api import (
    PROJECT_FACADE_API_TABLE_SCHEMA,
    ProjectFacadeApiRow,
    ProjectFacadeApiTable,
    get_project_facade_api_selection,
    get_project_facade_api_table,
    render_project_facade_api_reference_markdown,
)
from paradev.sdk.project import Project, ProjectManifestError

__all__ = [
    "Project",
    "ProjectManifestError",
    "PROJECT_FACADE_API_TABLE_SCHEMA",
    "ProjectFacadeApiRow",
    "ProjectFacadeApiTable",
    "get_project_facade_api_selection",
    "get_project_facade_api_table",
    "render_project_facade_api_reference_markdown",
]
