"""Typed public facade for transport-neutral and lazy REST API exports."""

from .api import (
    REST_FACADE_API_TABLE_SCHEMA as REST_FACADE_API_TABLE_SCHEMA,
    RestFacadeApiRow as RestFacadeApiRow,
    RestFacadeApiTable as RestFacadeApiTable,
    get_rest_facade_api_selection as get_rest_facade_api_selection,
    get_rest_facade_api_table as get_rest_facade_api_table,
    render_rest_facade_api_reference_markdown as render_rest_facade_api_reference_markdown,
)
from .projects import (
    apply_project_draft as apply_project_draft,
    create_module_batch as create_module_batch,
    create_module_draft as create_module_draft,
    read_project_source_form as read_project_source_form,
    read_project_source_text as read_project_source,
)

def build_app() -> object: ...
def get_openapi_seed() -> dict[str, object]: ...
