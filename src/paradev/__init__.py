"""ParaDev package."""

from .config import CM_PARADEV
from .package_api import (
    PACKAGE_API_TABLE_SCHEMA,
    PackageApiRow,
    PackageApiTable,
    get_package_api_selection,
    get_package_api_table,
    render_package_api_reference_markdown,
)
from .sdk import ArchitectureSpec, ParaDevProject, Project, ProjectManifestError, SurfaceSpec, get_architecture_spec, open_project
from .version import __version__

__all__ = [
    "ArchitectureSpec",
    "CM_PARADEV",
    "PACKAGE_API_TABLE_SCHEMA",
    "ParaDevProject",
    "PackageApiRow",
    "PackageApiTable",
    "Project",
    "ProjectManifestError",
    "SurfaceSpec",
    "__version__",
    "get_architecture_spec",
    "get_package_api_selection",
    "get_package_api_table",
    "open_project",
    "render_package_api_reference_markdown",
]
