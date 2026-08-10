"""Transport-neutral API services and lazy REST facade compatibility."""

from .api import (
    REST_FACADE_API_TABLE_SCHEMA,
    RestFacadeApiRow,
    RestFacadeApiTable,
    get_rest_facade_api_selection,
    get_rest_facade_api_table,
    render_rest_facade_api_reference_markdown,
)
from .projects import (
    apply_project_draft,
    create_module_batch,
    create_module_draft,
    read_project_source_form,
    read_project_source_text,
)

read_project_source = read_project_source_text

_LAZY_REST_EXPORTS = frozenset({"build_app", "get_openapi_seed"})

__all__ = [
    "apply_project_draft",
    "build_app",
    "create_module_batch",
    "create_module_draft",
    "get_openapi_seed",
    "read_project_source",
    "read_project_source_form",
    "REST_FACADE_API_TABLE_SCHEMA",
    "RestFacadeApiRow",
    "RestFacadeApiTable",
    "get_rest_facade_api_selection",
    "get_rest_facade_api_table",
    "render_rest_facade_api_reference_markdown",
]


def __getattr__(name: str) -> object:
    """Resolve compatibility-only REST exports without eager surface imports."""

    if name not in _LAZY_REST_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from paradev.surfaces import rest

    value = getattr(rest, name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    """Return eager and lazy public API names for interactive discovery."""

    return sorted(set(globals()) | _LAZY_REST_EXPORTS)
