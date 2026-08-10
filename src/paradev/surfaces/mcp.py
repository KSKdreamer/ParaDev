"""HeavenBase MCP surface contract and callable authoring tools."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, Any, Literal, cast

from typing_extensions import TypedDict

from paradev._api_table import api_indexed_table, api_table_selection
from paradev._api_table_markdown import (
    api_indexed_reference_sections,
    api_reference_markdown,
)
from paradev.localization._authoring import MAX_LOCALIZATION_WORKSPACE_ROWS
from paradev.sdk import (
    FRONTEND_API_SELECTORS,
    get_frontend_api_binding_index,
    get_frontend_api_contract,
    get_project_inspection_contract,
    open_project,
)
from paradev.sdk._module_diagram_api import (
    module_diagram_edit_input_schema,
    module_diagram_family_schema,
    module_diagram_intents,
    module_diagram_node_intents,
)
from paradev.sdk._localization_api import (
    localization_request_input_properties,
    localization_request_required_fields,
)
from paradev.sdk.project import (
    MAX_MODULE_CREATE_BATCH_SIZE,
    MAX_PROJECT_SOURCE_DRAFT_FILES,
)
from paradev.sdk.source_forms import MAX_SOURCE_FORM_QUERY_CHARS

if TYPE_CHECKING:
    from heavenbase import Toolkit

MCP_API_TABLE_SCHEMA = "paradev.mcp.api-table.v1"
TEMPLATE_FILTERS = [
    "template_id",
    "family",
    "kind",
    "source",
    "authoring_ready",
    "diagnostic_code",
]
_MCP_API_REFERENCE_PAGE = "docs/user-manual/mcp-api-reference.md"
_MCP_API_TEST_ANCHOR = "tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts"
_MCP_API_STANDARD_FIELDS = (
    "symbol",
    "kind",
    "layer",
    "feature",
    "mode",
    "sdk_method",
    "inputs",
    "returns",
    "raises",
    "frontend_operation_ids",
    "registry_seam",
    "doc_page",
    "test_anchor",
)
_MCP_API_INDEX_NAMES = ("mode_index", "feature_index", "frontend_operation_index")
_MCP_API_ROW_LIST_FIELDS = ("frontend_operation_ids",)
_MCP_TOOL_FEATURES = {
    "project_inspections": "inspections",
    "project_inspect": "inspections",
    "project_templates": "authoring",
    "project_authoring_path": "authoring",
    "project_authoring_plan": "authoring",
    "project_scaffold": "authoring",
    "project_create_modules": "authoring",
    "project_draft_apply": "authoring",
    "collection_scaffold": "authoring",
    "project_create": "projects",
    "project_open": "projects",
    "project_view": "projects",
    "project_browser": "projects",
    "project_find": "projects",
    "project_rename": "projects",
    "project_preferred_language": "projects",
    "module_rename": "modules",
    "module_duplicate": "modules",
    "module_collection_set": "modules",
    "module_activity_set": "modules",
    "module_metadata_clean": "modules",
    "module_diagram": "modules",
    "module_diagram_edit": "modules",
    "module_remove": "modules",
    "module_file": "modules",
    "module_asset": "modules",
    "module_source_form": "modules",
    "module_source_form_update": "modules",
    "module_source_form_update_batch": "modules",
    "localization_workspace": "authoring",
    "localization_plan": "authoring",
    "module_edit": "modules",
    "collection_file": "collections",
    "collection_edit": "collections",
    "collection_create": "collections",
    "collection_rename": "collections",
    "collection_remove": "collections",
    "frontend_api": "frontend-api",
    "api_catalog": "api-catalog",
    "surface_contracts": "surface-contracts",
    "pdx_parse": "pdx",
    "pdx_format": "pdx",
    "pdx_api": "pdx",
    "lsp_api": "lsp",
    "catalog_api": "catalog",
    "mcp_api": "mcp",
    "cli_api": "cli",
    "inspect_project": "projects",
    "list_surfaces": "architecture",
    "describe_architecture": "architecture",
    "architecture_api": "architecture",
}
_MCP_TOOL_INPUTS = {
    "project_inspections": "path",
    "project_inspect": "path, kind, filters",
    "project_templates": "path, template_id, family, kind, source, authoring_ready, diagnostic_code",
    "project_preferred_language": "path, preferred_language, write, plan_hash",
    "project_create_modules": "path, modules, source_root, write, plan_hash",
    "project_draft_apply": "path, source_edits, source_removals, source_replacements, module_rename",
    "collection_scaffold": "path, template_id, collection_id, values, source_root, write, force, plan_hash",
    "module_duplicate": "path, module_id, object_id, source_root, destination_source_root, write, plan_hash",
    "module_collection_set": "path, module_id, collection_id, source_root, write, plan_hash",
    "module_activity_set": "path, module_id, active, source_root, write, plan_hash",
    "module_metadata_clean": "path, family, module_id, source_root, write, plan_hash",
    "module_diagram": "path, family, profile",
    "module_diagram_edit": "path, family, profile, position_intents, edge_intents, node_intents, write, plan_hash",
    "module_asset": "path, module_id, relative_path, source_root, include_content",
    "module_source_form": "path, module_id, relative_path, source_root, encoding",
    "module_source_form_update": "path, module_id, relative_path, values, source_root, encoding",
    "module_source_form_update_batch": "path, updates, source_root, encoding",
    "localization_workspace": "path, target_kind, target_id, family, source_root, drafts, limit",
    "localization_plan": "path, target_kind, target_id, operation, family, source_root, drafts, limit",
    "frontend_api": ", ".join((*FRONTEND_API_SELECTORS, "index_name", "key")),
    "api_catalog": "reference_id, index_name, key",
    "surface_contracts": "identifier, status",
    "pdx_api": "symbol, index_name, key",
    "lsp_api": "symbol, index_name, key",
    "catalog_api": "symbol, index_name, key",
    "mcp_api": "symbol, index_name, key",
    "cli_api": "symbol, index_name, key",
    "inspect_project": "path",
    "list_surfaces": "none",
    "describe_architecture": "none",
    "architecture_api": "symbol, index_name, key",
}
_MCP_TOOL_RETURNS = {
    "project_inspections": "Project inspection contract",
    "project_inspect": "Project inspection payload",
    "project_templates": "Project authoring template payload",
    "project_authoring_path": "Project authoring path payload",
    "project_authoring_plan": "Project authoring plan payload",
    "project_scaffold": "SDK scaffold draft plan",
    "project_create_modules": "SDK atomic module batch plan or apply payload",
    "project_draft_apply": "SDK source-draft apply payload",
    "collection_scaffold": "SDK guarded collection scaffold plan or apply payload",
    "project_create": "Project create payload",
    "project_open": "Project manifest payload",
    "project_view": "Project view payload",
    "project_browser": "Project browser payload",
    "project_find": "Project find payload",
    "project_rename": "Project rename payload",
    "project_preferred_language": "Guarded project authoring-language plan or apply payload",
    "module_rename": "Module rename payload",
    "module_duplicate": "SDK guarded module duplicate plan or apply payload",
    "module_collection_set": "SDK guarded module collection plan or apply payload",
    "module_activity_set": "SDK guarded module activity plan or apply payload",
    "module_metadata_clean": "SDK guarded module metadata cleanup plan or apply payload",
    "module_diagram": "SDK source-backed module diagram payload",
    "module_diagram_edit": "SDK guarded module diagram edit plan or apply payload",
    "module_remove": "Module remove payload",
    "module_file": "Module file payload",
    "module_asset": "Registry-owned module asset payload",
    "module_source_form": "Stable module file snapshot plus optional Registry-owned source form",
    "module_source_form_update": "Revision-guarded full-text source edit plan from guided control values",
    "module_source_form_update_batch": "Atomic draft plan for several guided module source updates",
    "localization_workspace": "Registry-owned cross-language source-unit localization workspace",
    "localization_plan": "Revision-guarded source-unit localization update plan",
    "module_edit": "Module file payload",
    "collection_file": "Collection file payload",
    "collection_edit": "Collection file payload",
    "collection_create": "Collection create payload",
    "collection_rename": "Collection rename payload",
    "collection_remove": "Collection remove payload",
    "frontend_api": "Frontend API contract or selected projection",
    "api_catalog": "API catalog table, row, or index lookup payload",
    "surface_contracts": "Surface contract summary, contract payload, or status id list",
    "pdx_parse": "PDX parse payload",
    "pdx_format": "PDX format payload",
    "pdx_api": "PDX API table, row, or index lookup payload",
    "lsp_api": "LSP API table, row, or index lookup payload",
    "catalog_api": "Catalog API table, row, or index lookup payload",
    "mcp_api": "MCP API table, row, or index lookup payload",
    "cli_api": "CLI API table, row, or index lookup payload",
    "inspect_project": "Project view payload",
    "list_surfaces": "Architecture graph payload",
    "describe_architecture": "Architecture graph payload",
    "architecture_api": "Architecture API table, row, or index lookup payload",
}
_MCP_TOOL_RAISES = {
    "project_create": "ProjectCreateError on invalid or existing project",
    "project_open": "ProjectManifestError on invalid project",
    "project_rename": "ProjectManifestError or ValueError on invalid project rename",
    "project_preferred_language": "ProjectManifestError or ValueError on invalid project language",
    "project_create_modules": "ProjectManifestError, OSError, or ValueError on invalid module batch",
    "project_draft_apply": "ProjectManifestError, OSError, or ValueError on invalid source draft",
    "collection_scaffold": "ProjectManifestError, OSError, or ValueError on invalid collection scaffold",
    "module_rename": "ProjectManifestError or ValueError on invalid module rename",
    "module_duplicate": "ProjectManifestError, OSError, or ValueError on invalid module duplicate",
    "module_collection_set": "ProjectManifestError, OSError, or ValueError on invalid module collection",
    "module_activity_set": "ProjectManifestError, OSError, or ValueError on invalid module activity",
    "module_metadata_clean": "ProjectManifestError, OSError, or ValueError on invalid metadata cleanup",
    "module_diagram": "ProjectManifestError, OSError, or ValueError on invalid module diagram",
    "module_diagram_edit": "ProjectManifestError, OSError, or ValueError on invalid module diagram edit",
    "module_remove": "ProjectManifestError or ValueError on invalid module removal",
    "module_file": "ProjectManifestError or FileNotFoundError on missing module file",
    "module_asset": "ProjectManifestError, OSError, or ValueError on invalid module asset",
    "module_source_form": "ProjectManifestError, OSError, or ValueError on invalid module source form",
    "module_source_form_update": "ProjectManifestError, OSError, or ValueError on invalid guided source update",
    "module_source_form_update_batch": "ProjectManifestError, OSError, or ValueError on invalid guided source update batch",
    "localization_workspace": "ProjectManifestError, OSError, or ValueError on invalid localization workspace",
    "localization_plan": "ProjectManifestError, OSError, or ValueError on invalid localization operation",
    "module_edit": "ProjectManifestError or ValueError on invalid module file edit",
    "collection_file": "ProjectManifestError or FileNotFoundError on missing collection file",
    "collection_edit": "ProjectManifestError or ValueError on invalid collection file edit",
    "collection_create": "ProjectManifestError or ValueError on invalid collection create",
    "collection_rename": "ProjectManifestError or ValueError on invalid collection rename",
    "collection_remove": "ProjectManifestError or ValueError on invalid collection removal",
    "frontend_api": "ValueError on invalid frontend API selector",
    "api_catalog": "ValueError or KeyError on invalid API catalog selector",
    "surface_contracts": "ValueError or KeyError on invalid surface contract selector",
    "architecture_api": "ValueError or KeyError on invalid architecture API selector",
    "pdx_api": "ValueError or KeyError on invalid PDX API selector",
    "lsp_api": "ValueError or KeyError on invalid LSP API selector",
    "catalog_api": "ValueError or KeyError on invalid catalog API selector",
    "mcp_api": "ValueError or KeyError on invalid MCP API selector",
    "cli_api": "ValueError or KeyError on invalid CLI API selector",
    "pdx_parse": "ValueError on invalid PDX parse request",
    "pdx_format": "ValueError on invalid PDX format request",
}
_PROJECT_PREFERRED_LANGUAGE_INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "path": {"type": "string", "minLength": 1},
        "preferred_language": {
            "type": "string",
            "enum": ["en", "fr", "de", "ru", "es", "pl", "pt_br", "zh", "ja", "ko"],
        },
        "write": {"type": "boolean", "default": False},
        "plan_hash": {"type": ["string", "null"]},
    },
    "required": ["path", "preferred_language"],
    "allOf": [
        {
            "if": {
                "properties": {"write": {"const": True}},
                "required": ["write"],
            },
            "then": {
                "required": ["plan_hash"],
                "properties": {"plan_hash": {"type": "string", "minLength": 1}},
            },
        }
    ],
}
_PROJECT_CREATE_MODULES_INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "path": {
            "type": "string",
            "minLength": 1,
            "description": "Project root or nested project path.",
        },
        "modules": {
            "type": "array",
            "description": "Ordered module requests to plan or create atomically.",
            "maxItems": MAX_MODULE_CREATE_BATCH_SIZE,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "family": {"type": "string", "minLength": 1},
                    "template_id": {"type": "string", "minLength": 1},
                    "family_or_template": {"type": "string", "minLength": 1},
                    "object_id": {"type": "string", "minLength": 1},
                    "values": {"type": "object", "additionalProperties": True},
                },
                "required": ["object_id"],
                "oneOf": [
                    {"required": ["family"]},
                    {"required": ["template_id"]},
                    {"required": ["family_or_template"]},
                ],
            },
            "minItems": 1,
        },
        "source_root": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
        },
        "write": {"type": "boolean", "default": False},
        "plan_hash": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
    },
    "required": ["path", "modules"],
}
_PROJECT_DRAFT_APPLY_INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "path": {
            "type": "string",
            "minLength": 1,
            "description": "Project root or nested project path.",
        },
        "source_edits": {
            "type": "array",
            "maxItems": MAX_PROJECT_SOURCE_DRAFT_FILES,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["path", "text"],
                "dependentRequired": {
                    "expected_size": ["expected_mtime_ns"],
                    "expected_mtime_ns": ["expected_size"],
                },
                "properties": {
                    "path": {"type": "string", "minLength": 1},
                    "text": {"type": "string"},
                    "expected_size": {"type": "integer", "minimum": 0},
                    "expected_mtime_ns": {
                        "type": "string",
                        "pattern": "^[0-9]+$",
                    },
                },
            },
        },
        "source_removals": {
            "type": "array",
            "maxItems": MAX_PROJECT_SOURCE_DRAFT_FILES,
            "items": {
                "oneOf": [
                    {"type": "string", "minLength": 1},
                    {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["path"],
                        "dependentRequired": {
                            "expected_size": ["expected_mtime_ns"],
                            "expected_mtime_ns": ["expected_size"],
                        },
                        "properties": {
                            "path": {"type": "string", "minLength": 1},
                            "expected_size": {
                                "type": "integer",
                                "minimum": 0,
                            },
                            "expected_mtime_ns": {
                                "type": "string",
                                "pattern": "^[0-9]+$",
                            },
                        },
                    },
                ]
            },
        },
        "source_replacements": {
            "type": "array",
            "maxItems": MAX_PROJECT_SOURCE_DRAFT_FILES,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["path", "content_base64"],
                "dependentRequired": {
                    "expected_size": ["expected_mtime_ns"],
                    "expected_mtime_ns": ["expected_size"],
                    "content_format": ["target_format"],
                    "target_format": ["content_format"],
                },
                "allOf": [
                    {
                        "if": {
                            "required": ["expected_absent"],
                            "properties": {
                                "expected_absent": {
                                    "const": True,
                                }
                            },
                        },
                        "then": {
                            "not": {
                                "anyOf": [
                                    {"required": ["expected_size"]},
                                    {"required": ["expected_mtime_ns"]},
                                ]
                            }
                        },
                    }
                ],
                "properties": {
                    "path": {"type": "string", "minLength": 1},
                    "content_base64": {"type": "string"},
                    "expected_size": {"type": "integer", "minimum": 0},
                    "expected_mtime_ns": {
                        "type": "string",
                        "pattern": "^[0-9]+$",
                    },
                    "expected_absent": {"type": "boolean"},
                    "content_format": {
                        "type": "string",
                        "enum": ["png"],
                    },
                    "target_format": {
                        "type": "string",
                        "enum": [
                            "bmp",
                            "dds",
                            "jpeg",
                            "jpg",
                            "tga",
                            "webp",
                        ],
                    },
                },
            },
        },
        "module_rename": {
            "type": "object",
            "additionalProperties": False,
            "required": ["module_id", "object_id"],
            "properties": {
                "module_id": {"type": "string", "minLength": 1},
                "object_id": {"type": "string", "minLength": 1},
                "source_root": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                },
                "title": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                },
            },
        },
    },
    "required": ["path"],
    "anyOf": [
        {
            "required": ["source_edits"],
            "properties": {"source_edits": {"minItems": 1}},
        },
        {
            "required": ["source_removals"],
            "properties": {"source_removals": {"minItems": 1}},
        },
        {
            "required": ["source_replacements"],
            "properties": {"source_replacements": {"minItems": 1}},
        },
        {"required": ["module_rename"]},
    ],
}
_COLLECTION_SCAFFOLD_INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "path": {
            "type": "string",
            "minLength": 1,
            "description": "Project root or nested project path.",
        },
        "template_id": {
            "type": "string",
            "minLength": 1,
            "description": "Collection template id or unambiguous family.",
        },
        "collection_id": {
            "type": "string",
            "minLength": 1,
            "description": "New logical collection id.",
        },
        "values": {
            "type": "object",
            "additionalProperties": True,
            "default": {},
        },
        "source_root": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
        },
        "write": {"type": "boolean", "default": False},
        "force": {"type": "boolean", "default": False},
        "plan_hash": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
        },
    },
    "required": ["path", "template_id", "collection_id"],
    "allOf": [
        {
            "if": {
                "properties": {"write": {"const": True}},
                "required": ["write"],
            },
            "then": {
                "required": ["plan_hash"],
                "properties": {"plan_hash": {"type": "string", "minLength": 1}},
            },
        }
    ],
}
_COLLECTION_REMOVE_INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "path": {
            "type": "string",
            "minLength": 1,
            "description": "Project root or nested project path.",
        },
        "collection_id": {
            "type": "string",
            "minLength": 1,
            "description": "Existing collection id to remove.",
        },
        "family": {
            "anyOf": [{"type": "string", "minLength": 1}, {"type": "null"}],
            "default": None,
        },
        "source_root": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
        },
        "write": {"type": "boolean", "default": False},
        "plan_hash": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
        },
    },
    "required": ["path", "collection_id"],
    "allOf": [
        {
            "if": {
                "properties": {"write": {"const": True}},
                "required": ["write"],
            },
            "then": {
                "required": ["plan_hash"],
                "properties": {"plan_hash": {"type": "string", "minLength": 1}},
            },
        }
    ],
}
_MODULE_DUPLICATE_INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "path": {
            "type": "string",
            "minLength": 1,
            "description": "Project root or nested project path.",
        },
        "module_id": {
            "type": "string",
            "minLength": 1,
            "description": "Existing source module id in family/object_id form.",
        },
        "object_id": {
            "type": "string",
            "minLength": 1,
            "description": "Object id for the duplicated module folder.",
        },
        "source_root": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
        },
        "destination_source_root": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
        },
        "write": {"type": "boolean", "default": False},
        "plan_hash": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
        },
    },
    "required": ["path", "module_id", "object_id"],
}
_MODULE_COLLECTION_SET_INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "path": {
            "type": "string",
            "minLength": 1,
            "description": "Project root or nested project path.",
        },
        "module_id": {
            "type": "string",
            "minLength": 1,
            "description": "Existing source module id in family/object_id form.",
        },
        "collection_id": {
            "anyOf": [{"type": "string", "minLength": 1}, {"type": "null"}],
            "default": None,
            "description": "Target same-family collection id, or null to clear membership.",
        },
        "source_root": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
        },
        "write": {"type": "boolean", "default": False},
        "plan_hash": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
        },
    },
    "required": ["path", "module_id"],
    "allOf": [
        {
            "if": {
                "properties": {"write": {"const": True}},
                "required": ["write"],
            },
            "then": {
                "required": ["plan_hash"],
                "properties": {"plan_hash": {"type": "string", "minLength": 1}},
            },
        }
    ],
}
_MODULE_ACTIVITY_SET_INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "path": {
            "type": "string",
            "minLength": 1,
            "description": "Project root or nested project path.",
        },
        "module_id": {
            "type": "string",
            "minLength": 1,
            "description": "Existing source module id in family/object_id form.",
        },
        "active": {
            "type": "boolean",
            "description": "Whether every compilation mode should include the module.",
        },
        "source_root": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
        },
        "write": {"type": "boolean", "default": False},
        "plan_hash": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
        },
    },
    "required": ["path", "module_id", "active"],
    "allOf": [
        {
            "if": {
                "properties": {"write": {"const": True}},
                "required": ["write"],
            },
            "then": {
                "required": ["plan_hash"],
                "properties": {"plan_hash": {"type": "string", "minLength": 1}},
            },
        }
    ],
}
_MODULE_METADATA_CLEAN_INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "path": {
            "type": "string",
            "minLength": 1,
            "description": "Project root or nested project path.",
        },
        "family": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Optional compiler family scope.",
        },
        "module_id": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Optional module id scope in family/object_id form.",
        },
        "source_root": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Optional configured source-root scope.",
        },
        "write": {"type": "boolean", "default": False},
        "plan_hash": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
        },
    },
    "required": ["path"],
    "allOf": [
        {
            "if": {
                "properties": {
                    "write": {"const": True},
                },
                "required": ["write"],
            },
            "then": {
                "required": ["plan_hash"],
                "properties": {
                    "plan_hash": {
                        "type": "string",
                        "minLength": 1,
                    }
                },
            },
        }
    ],
}
_MODULE_DIAGRAM_INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "path": {
            "type": "string",
            "minLength": 1,
            "description": "Project root or nested project path.",
        },
        "family": module_diagram_family_schema(editable=False),
        "profile": {
            "anyOf": [{"type": "string", "minLength": 1}, {"type": "null"}],
            "default": None,
        },
    },
    "required": ["path", "family"],
}
_MODULE_DIAGRAM_EDIT_INPUT_SCHEMA = module_diagram_edit_input_schema(project_field="path")
_PROJECT_TEMPLATES_INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "path": {
            "type": "string",
            "description": "Project root or nested project path.",
        },
        "template_id": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
        },
        "family": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
        },
        "kind": {
            "anyOf": [
                {"type": "string", "enum": ["module", "collection"]},
                {"type": "null"},
            ],
            "default": None,
        },
        "source": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
        },
        "authoring_ready": {
            "anyOf": [{"type": "boolean"}, {"type": "null"}],
            "default": None,
        },
        "diagnostic_code": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
        },
    },
    "required": ["path"],
}
_PROJECT_AUTHORING_PATH_INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "path": {
            "type": "string",
            "description": "Project root or nested project path.",
        },
        "kind": {
            "type": "string",
            "enum": ["module", "collection"],
        },
        "family": {"type": "string"},
        "target_id": {"type": "string"},
        "source_root": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
        },
    },
    "required": ["path", "kind", "family", "target_id"],
}
_PROJECT_AUTHORING_PLAN_INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        **_PROJECT_AUTHORING_PATH_INPUT_SCHEMA["properties"],
        "profile": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
        },
    },
    "required": ["path", "kind", "family", "target_id"],
}
_PROJECT_BROWSER_INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "path": {
            "type": "string",
            "minLength": 1,
            "description": "Project root or nested project path.",
        },
        "profile": {
            "anyOf": [{"type": "string", "minLength": 1}, {"type": "null"}],
            "default": None,
        },
        "kind": {
            "anyOf": [
                {"type": "string", "enum": ["module", "collection"]},
                {"type": "null"},
            ],
            "default": None,
        },
        "family": {
            "anyOf": [{"type": "string", "minLength": 1}, {"type": "null"}],
            "default": None,
        },
        "module_id": {
            "anyOf": [{"type": "string", "minLength": 1}, {"type": "null"}],
            "default": None,
        },
        "collection_id": {
            "anyOf": [{"type": "string", "minLength": 1}, {"type": "null"}],
            "default": None,
        },
    },
    "required": ["path"],
}
_MODULE_FILE_INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "path": {
            "type": "string",
            "minLength": 1,
            "description": "Project root or nested project path.",
        },
        "module_id": {
            "type": "string",
            "minLength": 1,
            "description": "Existing source module id in family/object_id form.",
        },
        "relative_path": {
            "type": "string",
            "minLength": 1,
            "description": "Text source path relative to the module folder.",
        },
        "source_root": {
            "anyOf": [{"type": "string", "minLength": 1}, {"type": "null"}],
            "default": None,
        },
        "encoding": {
            "type": "string",
            "enum": ["utf-8"],
            "default": "utf-8",
        },
    },
    "required": ["path", "module_id", "relative_path"],
}
_COLLECTION_FILE_INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "path": _MODULE_FILE_INPUT_SCHEMA["properties"]["path"],
        "collection_id": {
            "type": "string",
            "minLength": 1,
            "description": "Existing collection id.",
        },
        "relative_path": {
            "type": "string",
            "minLength": 1,
            "description": "Text source path relative to the collection folder.",
        },
        "family": {
            "anyOf": [{"type": "string", "minLength": 1}, {"type": "null"}],
            "default": None,
            "description": "Optional collection family used to disambiguate the id.",
        },
        "source_root": _MODULE_FILE_INPUT_SCHEMA["properties"]["source_root"],
        "encoding": _MODULE_FILE_INPUT_SCHEMA["properties"]["encoding"],
    },
    "required": ["path", "collection_id", "relative_path"],
}
_MODULE_ASSET_INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "path": _MODULE_FILE_INPUT_SCHEMA["properties"]["path"],
        "module_id": _MODULE_FILE_INPUT_SCHEMA["properties"]["module_id"],
        "relative_path": {
            "type": "string",
            "minLength": 1,
            "description": ("Registry-owned copy or image source path relative to the " "module folder."),
        },
        "source_root": _MODULE_FILE_INPUT_SCHEMA["properties"]["source_root"],
        "include_content": {
            "type": "boolean",
            "default": False,
            "description": ("Include bounded base64 content. Keep false when only the " "digest and draft guard are needed."),
        },
    },
    "required": ["path", "module_id", "relative_path"],
}
_MODULE_SOURCE_FORM_INPUT_SCHEMA = {
    **_MODULE_FILE_INPUT_SCHEMA,
    "properties": {
        **_MODULE_FILE_INPUT_SCHEMA["properties"],
        "relative_path": {
            "type": "string",
            "minLength": 1,
            "description": ("Canonical Registry-owned JSON or PDX source path relative " "to the module folder."),
        },
        "query": {
            "type": "string",
            "maxLength": MAX_SOURCE_FORM_QUERY_CHARS,
            "description": ("Optional case-insensitive field search. Use the same query " "when submitting an update for a returned control id."),
        },
    },
}
_SOURCE_FORM_VALUES_INPUT_SCHEMA = {
    "type": "object",
    "minProperties": 1,
    "additionalProperties": {
        "anyOf": [
            {"type": "string"},
            {"type": "number"},
            {"type": "boolean"},
        ]
    },
    "description": "Editable guided control ids mapped to replacement scalar values.",
}
_MODULE_SOURCE_FORM_UPDATE_INPUT_SCHEMA = {
    **_MODULE_SOURCE_FORM_INPUT_SCHEMA,
    "properties": {
        **_MODULE_SOURCE_FORM_INPUT_SCHEMA["properties"],
        "values": _SOURCE_FORM_VALUES_INPUT_SCHEMA,
    },
    "required": ["path", "module_id", "relative_path", "values"],
}
_MODULE_SOURCE_FORM_UPDATE_BATCH_INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "path": _MODULE_FILE_INPUT_SCHEMA["properties"]["path"],
        "updates": {
            "type": "array",
            "minItems": 1,
            "maxItems": MAX_PROJECT_SOURCE_DRAFT_FILES,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["module_id", "relative_path", "values"],
                "properties": {
                    "module_id": _MODULE_FILE_INPUT_SCHEMA["properties"]["module_id"],
                    "relative_path": _MODULE_SOURCE_FORM_INPUT_SCHEMA["properties"]["relative_path"],
                    "values": _SOURCE_FORM_VALUES_INPUT_SCHEMA,
                    "query": _MODULE_SOURCE_FORM_INPUT_SCHEMA["properties"]["query"],
                },
            },
        },
        "source_root": _MODULE_FILE_INPUT_SCHEMA["properties"]["source_root"],
        "encoding": _MODULE_FILE_INPUT_SCHEMA["properties"]["encoding"],
    },
    "required": ["path", "updates"],
}


def _localization_mcp_input_schema(*, include_operation: bool) -> dict[str, object]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "path": _MODULE_FILE_INPUT_SCHEMA["properties"]["path"],
            **localization_request_input_properties(include_operation=include_operation),
        },
        "required": [
            "path",
            *localization_request_required_fields(include_operation=include_operation),
        ],
    }


_LOCALIZATION_WORKSPACE_INPUT_SCHEMA = _localization_mcp_input_schema(include_operation=False)
_LOCALIZATION_PLAN_INPUT_SCHEMA = _localization_mcp_input_schema(include_operation=True)


class McpApiRow(TypedDict):
    """One MCP tool contract table row."""

    symbol: str
    kind: str
    layer: str
    feature: str
    mode: str
    sdk_method: str
    inputs: str
    returns: str
    raises: str
    registry_seam: str
    surface: str
    frontend_operation_ids: list[str]
    doc_page: str
    test_anchor: str


class McpApiTable(TypedDict):
    """Generated API-standard table for MCP tools."""

    schema: str
    row_count: int
    mode_index: dict[str, list[str]]
    feature_index: dict[str, list[str]]
    frontend_operation_index: dict[str, list[str]]
    rows: list[McpApiRow]


class _ProjectCreateModuleRequired(TypedDict):
    object_id: str


class ProjectCreateModuleRequest(_ProjectCreateModuleRequired, total=False):
    """One JSON-safe request row for `project_create_modules`."""

    family: str
    template_id: str
    family_or_template: str
    values: dict[str, object]


class _ModuleSourceFormUpdateRequired(TypedDict):
    """One JSON-safe guided source row for a batch update plan."""

    module_id: str
    relative_path: str
    values: dict[str, str | int | float | bool]


class ModuleSourceFormUpdateRequest(_ModuleSourceFormUpdateRequired, total=False):
    """One guided update row with optional bounded form search."""

    query: str


def project_templates(
    path: str,
    template_id: str | None = None,
    family: str | None = None,
    kind: Literal["module", "collection"] | None = None,
    source: str | None = None,
    authoring_ready: bool | None = None,
    diagnostic_code: str | None = None,
) -> dict[str, object]:
    """List the authoring templates available to one project.

    Args:
        path (str): Project root or nested project path.
        template_id (str | None): Optional exact template id.
        family (str | None): Optional exact module family.
        kind (Literal["module", "collection"] | None): Optional target kind.
        source (str | None): Optional template source such as `builtin` or `project`.
        authoring_ready (bool | None): Optional authoring-readiness filter.
        diagnostic_code (str | None): Optional template diagnostic code.

    Returns:
        dict[str, object]: JSON-safe SDK template payload including source
            roots, form fields, and template indexes.

    Raises:
        ProjectManifestError: If the selected project cannot be loaded.
        ValueError: If a template filter is invalid.
    """

    return open_project(path).templates(
        template_id=template_id,
        family=family,
        kind=kind,
        source=source,
        authoring_ready=authoring_ready,
        diagnostic_code=diagnostic_code,
    )


def project_authoring_path(
    path: str,
    kind: Literal["module", "collection"],
    family: str,
    target_id: str,
    source_root: str | None = None,
) -> dict[str, object]:
    """Resolve the canonical source destination for one project object.

    Args:
        path (str): Project root or nested project path.
        kind (Literal["module", "collection"]): Use `module` for a module destination or `collection` for a collection destination.
        family (str): Compiler family id.
        target_id (str): Module object id or collection id.
        source_root (str | None): Optional configured source root.

    Returns:
        dict[str, object]: JSON-safe SDK authoring-path payload.

    Raises:
        ProjectManifestError: If the selected project cannot be loaded.
        ValueError: If the authoring destination is invalid.
    """

    return open_project(path).authoring_path(
        kind,
        family,
        target_id,
        source_root=source_root,
    )


def project_authoring_plan(
    path: str,
    kind: Literal["module", "collection"],
    family: str,
    target_id: str,
    source_root: str | None = None,
    profile: str | None = None,
) -> dict[str, object]:
    """Inspect the source slots expected at one authoring destination.

    Args:
        path (str): Project root or nested project path.
        kind (Literal["module", "collection"]): Use `module` to inspect a module destination or `collection` to inspect a collection destination.
        family (str): Compiler family id.
        target_id (str): Module object id or collection id.
        source_root (str | None): Optional configured source root.
        profile (str | None): Optional build profile override.

    Returns:
        dict[str, object]: JSON-safe SDK authoring plan with destination and
            source-slot status.

    Raises:
        ProjectManifestError: If the selected project cannot be loaded.
        ValueError: If the authoring plan request is invalid.
    """

    return open_project(path).authoring_plan(
        kind,
        family,
        target_id,
        source_root=source_root,
        profile=profile,
    )


def project_browser(
    path: str,
    profile: str | None = None,
    kind: Literal["module", "collection"] | None = None,
    family: str | None = None,
    module_id: str | None = None,
    collection_id: str | None = None,
) -> dict[str, object]:
    """Discover registered families and source-backed project objects.

    Args:
        path: Project root or nested project path.
        profile: Optional build profile override.
        kind: Optional item kind filter.
        family: Optional Registry family id or presentation alias.
        module_id: Optional exact module id in ``family/object_id`` form.
        collection_id: Optional exact collection id.

    Returns:
        JSON-safe SDK project browser payload with source slots and paths.

    Raises:
        ProjectManifestError: If the selected project cannot be loaded.
        OSError: If project discovery cannot read a source.
        ValueError: If a browser filter is invalid.
    """

    return open_project(path).browser(
        profile=profile,
        kind=kind,
        family=family,
        module_id=module_id,
        collection_id=collection_id,
    )


def module_file(
    path: str,
    module_id: str,
    relative_path: str,
    source_root: str | None = None,
    encoding: Literal["utf-8"] = "utf-8",
) -> dict[str, object]:
    """Read one stable text snapshot from an existing source module.

    The returned ``size`` and ``mtime_ns`` values come from the same stable
    file snapshot as ``text``. Pass them as ``expected_size`` and
    ``expected_mtime_ns`` to :func:`project_draft_apply` so a later external
    edit cannot be overwritten.

    Args:
        path: Project root or nested project path.
        module_id: Existing module id in ``family/object_id`` form.
        relative_path: Text source path relative to the module folder.
        source_root: Optional configured source-root selector.
        encoding: Text encoding. The MCP authoring surface supports UTF-8.

    Returns:
        JSON-safe module file payload with text and a stable source revision.

    Raises:
        ProjectManifestError: If the selected project cannot be loaded.
        OSError: If the source cannot be read.
        ValueError: If the module, source path, or text encoding is invalid.
    """

    return open_project(path).read_module_file(
        module_id,
        relative_path,
        source_root=source_root,
        encoding=encoding,
    )


def collection_file(
    path: str,
    collection_id: str,
    relative_path: str,
    family: str | None = None,
    source_root: str | None = None,
    encoding: Literal["utf-8"] = "utf-8",
) -> dict[str, object]:
    """Read one stable text snapshot from an existing collection.

    The returned ``size`` and ``mtime_ns`` values come from the same stable
    file snapshot as ``text``. Pass them as ``expected_size`` and
    ``expected_mtime_ns`` to :func:`project_draft_apply` so a later external
    edit cannot be overwritten.

    Args:
        path: Project root or nested project path.
        collection_id: Existing collection id.
        relative_path: Text source path relative to the collection folder.
        family: Optional collection family used to disambiguate the id.
        source_root: Optional configured source-root selector.
        encoding: Text encoding. The MCP authoring surface supports UTF-8.

    Returns:
        JSON-safe collection file payload with text and a stable source
        revision.

    Raises:
        ProjectManifestError: If the selected project cannot be loaded.
        OSError: If the source cannot be read.
        ValueError: If the collection, source path, or encoding is invalid.
    """

    return open_project(path).read_collection_file(
        collection_id,
        relative_path,
        family=family,
        source_root=source_root,
        encoding=encoding,
    )


def module_asset(
    path: str,
    module_id: str,
    relative_path: str,
    source_root: str | None = None,
    include_content: bool = False,
) -> dict[str, object]:
    """Read one stable Registry-owned module asset through MCP.

    Use the returned ``draft_guard`` unchanged in a
    :func:`project_draft_apply` binary replacement. Base64 content is omitted
    by default so asset discovery does not flood the model context.

    Args:
        path (str): Project root or nested project path.
        module_id (str): Existing module id in `family/object_id` form.
        relative_path (str): Registry-owned copy or image source path relative to the module folder.
        source_root (str | None): Optional configured source-root selector.
        include_content (bool): Whether to include bounded base64 content.

    Returns:
        dict[str, object]: JSON-safe asset payload with Registry source slots,
            SHA-256 digest, stable revision, draft guard, and optional content.

    Raises:
        ProjectManifestError: If the selected project cannot be loaded.
        OSError: If a stable source snapshot cannot be read.
        ValueError: If the module, asset path, Registry ownership, or size is
            invalid.
    """

    return open_project(path).read_module_asset(
        module_id,
        relative_path,
        source_root=source_root,
        include_content=include_content,
    )


def module_source_form(
    path: str,
    module_id: str,
    relative_path: str,
    source_root: str | None = None,
    encoding: Literal["utf-8"] = "utf-8",
    query: str | None = None,
) -> dict[str, object]:
    """Read one stable module source snapshot and its optional guided form.

    The source form is resolved by the owning Registry family. Any source
    declared by a PDX resource slot can use ParaDev's generic lossless scalar
    projection, while project extensions may provide their own JSON form
    contract. The returned source snapshot includes the paired ``size`` and
    ``mtime_ns`` revision required by :func:`project_draft_apply`.

    Args:
        path: Project root or nested project path.
        module_id: Existing module id in ``family/object_id`` form.
        relative_path: Canonical Registry-owned JSON or PDX source path
            relative to the module folder.
        source_root: Optional configured source-root selector.
        encoding: Text encoding. The MCP authoring surface supports UTF-8.
        query: Optional bounded search across safe PDX or localization fields.

    Returns:
        JSON-safe payload containing the stable source snapshot, whether a
        guided form is supported, and the optional Registry-owned form.

    Raises:
        ProjectManifestError: If the selected project cannot be loaded.
        OSError: If the source cannot be read.
        ValueError: If the module, source path, text encoding, or source-form
            provider contract is invalid.
    """

    project = open_project(path)
    source = project.read_module_file(
        module_id,
        relative_path,
        source_root=source_root,
        encoding=encoding,
    )
    form = project.source_form(
        str(source["path"]),
        text=str(source["text"]),
        **({"query": query} if query is not None else {}),
    )
    return {
        "schema": "paradev.mcp.module-source-form.v1",
        "project_id": project.project_id,
        "module_id": source["module_id"],
        "family": source["family"],
        "source": source,
        "supported": form is not None,
        "form": form,
    }


def module_source_form_update(
    path: str,
    module_id: str,
    relative_path: str,
    values: dict[str, str | int | float | bool],
    source_root: str | None = None,
    encoding: Literal["utf-8"] = "utf-8",
    query: str | None = None,
) -> dict[str, object]:
    """Plan a guarded full-text source edit from guided control values.

    This tool never writes. Resolve controls with :func:`module_source_form`,
    submit selected control ids here, review the returned changes and full-text
    ``source_edit``, then pass that edit to :func:`project_draft_apply`.

    Args:
        path: Project root or nested project path.
        module_id: Existing module id in ``family/object_id`` form.
        relative_path: Registry-owned JSON or PDX source path relative to the
            module folder.
        values: Non-empty editable control-id to scalar-value mapping.
        source_root: Optional configured source-root selector.
        encoding: Text encoding. The MCP authoring surface supports UTF-8.
        query: Optional bounded search used to resolve stable control ids
            outside the default projection window.

    Returns:
        JSON-safe ``paradev.source-form-update.v1`` plan with exact changes and
        a paired revision-guarded ``source_edit`` accepted by
        :func:`project_draft_apply`.

    Raises:
        ProjectManifestError: If the selected project cannot be loaded.
        OSError: If the source cannot be read.
        ValueError: If the module, source, control mapping, or source token is
            invalid or stale.
    """

    if encoding != "utf-8":
        raise ValueError("Guided source updates support only UTF-8 text.")
    project = open_project(path)
    source = project.read_module_file(
        module_id,
        relative_path,
        source_root=source_root,
        encoding=encoding,
    )
    return project.plan_source_form_update(
        str(source["path"]),
        values,
        **({"query": query} if query is not None else {}),
    )


def module_source_form_update_batch(
    path: str,
    updates: list[ModuleSourceFormUpdateRequest],
    source_root: str | None = None,
    encoding: Literal["utf-8"] = "utf-8",
) -> dict[str, object]:
    """Plan several guided module source updates as one atomic draft.

    This tool never writes. Review the per-source changes and combined
    ``source_edits``, then pass those edits to :func:`project_draft_apply`.
    Revision checks for every changed source occur before that transaction
    writes any file.

    Args:
        path: Project root or nested project path.
        updates: Ordered non-empty rows
            containing an existing ``module_id``, Registry-owned
            ``relative_path``, and guided control ``values``. At most 256
            distinct source files may be planned together.
        source_root: Optional configured source-root selector
            shared by every row.
        encoding: Text encoding. Only ``utf-8`` is supported.

    Returns:
        dict[str, object]: JSON-safe
            ``paradev.source-form-update-batch.v1`` plan containing per-source
            updates and the changed revision-guarded ``source_edits`` accepted
            by :func:`project_draft_apply`.

    Raises:
        ProjectManifestError: If the selected project cannot be loaded.
        OSError: If a source cannot be read.
        ValueError: If the batch, module, source, control mapping, or source
            token is invalid or stale.
    """

    if encoding != "utf-8":
        raise ValueError("Guided source updates support only UTF-8 text.")
    if not isinstance(updates, list) or not updates:
        raise ValueError("Guided module source update batch must be a non-empty array.")
    if len(updates) > MAX_PROJECT_SOURCE_DRAFT_FILES:
        raise ValueError("Guided module source update batch must contain at most " f"{MAX_PROJECT_SOURCE_DRAFT_FILES} rows.")

    project = open_project(path)
    planned_updates: list[dict[str, object]] = []
    for index, update in enumerate(updates):
        if not isinstance(update, Mapping):
            raise ValueError(f"Guided module source update row {index} must be an object.")
        unknown = sorted(str(key) for key in set(update) - {"module_id", "relative_path", "values", "query"})
        if unknown:
            raise ValueError(f"Guided module source update row {index} contains unsupported " f"fields: {', '.join(unknown)}.")
        module_id = update.get("module_id")
        relative_path = update.get("relative_path")
        values = update.get("values")
        query = update.get("query")
        if not isinstance(module_id, str) or not module_id:
            raise ValueError(f"Guided module source update row {index}.module_id must be non-empty text.")
        if not isinstance(relative_path, str) or not relative_path:
            raise ValueError(f"Guided module source update row {index}.relative_path must be non-empty text.")
        if not isinstance(values, Mapping):
            raise ValueError(f"Guided module source update row {index}.values must be an object.")
        if query is not None and not isinstance(query, str):
            raise ValueError(f"Guided module source update row {index}.query must be text.")
        source = project.read_module_file(
            module_id,
            relative_path,
            source_root=source_root,
            encoding=encoding,
        )
        planned_updates.append(
            {
                "source_path": str(source["path"]),
                "values": values,
                **({"query": query} if query is not None else {}),
            }
        )
    return project.plan_source_form_updates(planned_updates)


def localization_workspace(
    path: str,
    target_kind: Literal["module", "collection"],
    target_id: str,
    family: str | None = None,
    source_root: str | None = None,
    drafts: list[dict[str, str]] | None = None,
    limit: int = MAX_LOCALIZATION_WORKSPACE_ROWS,
) -> dict[str, object]:
    """Return one Registry-owned cross-language localization workspace.

    This tool never writes. Pass current unsaved localization sources through
    ``drafts`` so the returned table matches the user's editor state.

    Args:
        path: Project root or nested project path.
        target_kind: Whether the source unit is a module or collection.
        target_id: Existing module id or collection id.
        family: Optional collection-family disambiguator.
        source_root: Optional configured source-root selector.
        drafts: Optional source-path and text rows for current unsaved files.
        limit: Maximum localization-key rows returned.

    Returns:
        JSON-safe workspace with source revisions, languages, keys, values,
        and explicit truncation coverage.

    Raises:
        ProjectManifestError: If the selected project cannot be loaded.
        OSError: If a stable localization source snapshot cannot be read.
        ValueError: If the target, source ownership, drafts, source syntax, or
            row limit is invalid.
    """

    return open_project(path).localization_workspace(
        target_id,
        target_kind=target_kind,
        family=family,
        source_root=source_root,
        drafts=_localization_draft_mapping(drafts),
        limit=limit,
    )


def localization_plan(
    path: str,
    target_kind: Literal["module", "collection"],
    target_id: str,
    operation: dict[str, object],
    family: str | None = None,
    source_root: str | None = None,
    drafts: list[dict[str, str]] | None = None,
    limit: int = MAX_LOCALIZATION_WORKSPACE_ROWS,
) -> dict[str, object]:
    """Plan one lossless Registry-owned localization edit without writing.

    Review the returned changes and revision-guarded ``source_edits``, then
    pass those edits to :func:`project_draft_apply` for atomic application.

    Args:
        path: Project root or nested project path.
        target_kind: Whether the source unit is a module or collection.
        target_id: Existing module id or collection id.
        operation: Closed ``set``, ``add``, ``rename``, or ``remove`` mapping.
        family: Optional collection-family disambiguator.
        source_root: Optional configured source-root selector.
        drafts: Optional source-path and text rows for current unsaved files.
        limit: Maximum localization-key rows returned in the updated workspace.

    Returns:
        JSON-safe update plan with exact changes and guarded source edits.

    Raises:
        ProjectManifestError: If the selected project cannot be loaded.
        OSError: If a stable localization source snapshot cannot be read.
        ValueError: If ownership, drafts, source syntax, the operation,
            collision rules, or the row limit is invalid.
    """

    return open_project(path).plan_localization_update(
        target_id,
        operation,
        target_kind=target_kind,
        family=family,
        source_root=source_root,
        drafts=_localization_draft_mapping(drafts),
        limit=limit,
    )


def _localization_draft_mapping(
    drafts: list[dict[str, str]] | None,
) -> dict[str, str] | None:
    if drafts is None:
        return None
    if not isinstance(drafts, list):
        raise ValueError("Localization drafts must be an array.")
    normalized: dict[str, str] = {}
    for index, draft in enumerate(drafts):
        if not isinstance(draft, Mapping):
            raise ValueError(f"Localization draft {index} must be an object.")
        unknown = sorted(str(key) for key in set(draft) - {"source_path", "text"})
        if unknown:
            raise ValueError(f"Localization draft {index} contains unsupported fields: {', '.join(unknown)}.")
        source_path = draft.get("source_path")
        text = draft.get("text")
        if not isinstance(source_path, str) or not source_path:
            raise ValueError(f"Localization draft {index}.source_path must be non-empty text.")
        if not isinstance(text, str):
            raise ValueError(f"Localization draft {index}.text must be text.")
        if source_path in normalized:
            raise ValueError(f"Localization drafts repeat source path {source_path!r}.")
        normalized[source_path] = text
    return normalized


def project_create_modules(
    path: str,
    modules: list[ProjectCreateModuleRequest],
    source_root: str | None = None,
    write: bool = False,
    plan_hash: str | None = None,
) -> dict[str, object]:
    """Plan or atomically create project modules through MCP.

    Args:
        path (str): Project root or nested project path.
        modules (list[ProjectCreateModuleRequest]): Ordered module requests accepted by `Project.create_modules(...)`.
        source_root (str | None): Optional configured source root that receives every module.
        write (bool): Whether to apply the reviewed plan.
        plan_hash (str | None): Exact hash returned by a prior dry plan; required when `write` is true.

    Returns:
        dict[str, object]: JSON-safe atomic module batch plan or apply payload.

    Raises:
        ProjectManifestError: If the selected project cannot be loaded.
        OSError: If safe filesystem staging or publication fails.
        ValueError: If the module batch or plan hash is invalid.
    """

    return open_project(path).create_modules(
        modules,
        source_root=source_root,
        write=write,
        plan_hash=plan_hash,
    )


def project_preferred_language(
    path: str,
    preferred_language: str,
    write: bool = False,
    plan_hash: str | None = None,
) -> dict[str, object]:
    """Plan or apply the project-wide module-authoring language through MCP.

    Args:
        path: Project root or nested project path.
        preferred_language: Supported HoI4 language alias such as `en`
            or `zh`.
        write: Whether to atomically apply the reviewed plan.
        plan_hash: Exact hash returned by the current dry plan;
            required when `write` is true.

    Returns:
        dict[str, object]: Guarded project language plan or apply payload.

    Raises:
        ProjectManifestError: If the selected project cannot be loaded.
        ValueError: If the language, manifest, or plan hash is invalid.
    """

    return open_project(path).set_preferred_language(
        preferred_language,
        write=write,
        plan_hash=plan_hash,
    )


def project_draft_apply(
    path: str,
    source_edits: list[dict[str, object]] | None = None,
    source_removals: list[str | dict[str, object]] | None = None,
    source_replacements: list[dict[str, object]] | None = None,
    module_rename: dict[str, object] | None = None,
) -> dict[str, object]:
    """Apply source drafts and an optional module rename through MCP.

    Args:
        path: Project root or nested project path.
        source_edits: Optional text replacements with guarded source
            revisions.
        source_removals: Optional file removals with guarded source revisions.
        source_replacements: Optional binary replacements, including
            supported image conversion requests.
        module_rename: Optional module id, target object id, source-root
            selector, and readable folder title.

    Returns:
        dict[str, object]: JSON-safe source-draft payload. Source mutations
            and the optional module-folder rename share one rollback boundary.

    Raises:
        ProjectManifestError: If the selected project cannot be loaded.
        OSError: If guarded source mutation or rollback fails.
        ValueError: If the draft or module rename is invalid or stale.
    """

    return open_project(path).apply_source_draft(
        source_edits=source_edits,
        source_removals=source_removals,
        source_replacements=source_replacements,
        module_rename=module_rename,
    )


def collection_scaffold(
    path: str,
    template_id: str,
    collection_id: str,
    values: dict[str, object] | None = None,
    source_root: str | None = None,
    write: bool = False,
    force: bool = False,
    plan_hash: str | None = None,
) -> dict[str, object]:
    """Plan or transactionally create one collection through MCP.

    Args:
        path: Project root or nested project path.
        template_id: Collection template id or unambiguous family.
        collection_id: New logical collection id.
        values: Template-specific scalar values.
        source_root: Optional configured source root.
        write: Whether to apply the reviewed plan.
        force: Whether existing scaffold files may be overwritten.
        plan_hash: Exact dry-plan hash; required when ``write`` is true.

    Returns:
        JSON-safe guarded collection scaffold plan or apply payload.
    """

    return open_project(path).scaffold_collection(
        template_id,
        collection_id,
        values=values,
        source_root=source_root,
        write=write,
        force=force,
        plan_hash=plan_hash,
    )


def collection_remove(
    path: str,
    collection_id: str,
    family: str | None = None,
    source_root: str | None = None,
    write: bool = False,
    plan_hash: str | None = None,
) -> dict[str, object]:
    """Plan or transactionally remove one collection through MCP.

    The operation preserves every member module and clears its explicit
    collection pointer before removing the descriptor. Applying the plan
    requires the exact dry-run hash.

    Args:
        path: Project root or nested project path.
        collection_id: Existing logical collection id.
        family: Optional family used to disambiguate the collection.
        source_root: Optional configured source root.
        write: Whether to apply the reviewed plan.
        plan_hash: Exact dry-plan hash; required when ``write`` is true.

    Returns:
        JSON-safe guarded collection removal plan or apply payload.
    """

    return open_project(path).remove_collection(
        collection_id,
        family=family,
        source_root=source_root,
        write=write,
        plan_hash=plan_hash,
    )


def module_duplicate(
    path: str,
    module_id: str,
    object_id: str,
    source_root: str | None = None,
    destination_source_root: str | None = None,
    identity: Literal["rewrite", "preserve"] = "rewrite",
    write: bool = False,
    plan_hash: str | None = None,
) -> dict[str, object]:
    """Plan or atomically create an independent module copy through MCP.

    Call with `write=False` first, review renamed paths and rewritten file
    fingerprints, then pass the exact returned `plan_hash` with `write=True`.

    Args:
        path (str): Project root or nested project path.
        module_id (str): Existing module in `family/object_id` form.
        object_id (str): New module object identifier.
        source_root (str | None): Optional source-root selector.
        destination_source_root (str | None): Optional destination source root.
        identity (Literal["rewrite", "preserve"]): Identity policy for the copy.
        write (bool): Whether to apply the reviewed plan.
        plan_hash (str | None): Exact dry-plan hash required for apply.

    Returns:
        dict[str, object]: JSON-safe guarded duplicate plan or apply payload.
    """

    return open_project(path).duplicate_module(
        module_id,
        object_id,
        source_root=source_root,
        destination_source_root=destination_source_root,
        identity=identity,
        write=write,
        plan_hash=plan_hash,
    )


def module_metadata_clean(
    path: str,
    family: str | None = None,
    module_id: str | None = None,
    source_root: str | None = None,
    write: bool = False,
    plan_hash: str | None = None,
) -> dict[str, object]:
    """Plan or atomically clean redundant module metadata through MCP.

    Call with ``write=False`` first. Applying a reviewed plan requires its
    exact ``plan_hash`` so source changes cannot be cleaned from a stale
    preview.

    Args:
        path: Project root or nested project path.
        family: Optional compiler family scope.
        module_id: Optional module id scope in family/object_id form.
        source_root: Optional configured source-root scope.
        write: Whether to apply the reviewed plan.
        plan_hash: Exact dry-plan hash; required when ``write`` is true.

    Returns:
        JSON-safe SDK metadata cleanup plan or apply payload.

    Raises:
        ProjectManifestError: If the selected project cannot be loaded.
        OSError: If safe source mutation fails.
        ValueError: If the scope or plan hash is invalid.
    """

    return open_project(path).clean_module_metadata(
        family=family,
        module_id=module_id,
        source_root=source_root,
        write=write,
        plan_hash=plan_hash,
    )


def module_collection_set(
    path: str,
    module_id: str,
    collection_id: str | None = None,
    source_root: str | None = None,
    write: bool = False,
    plan_hash: str | None = None,
) -> dict[str, object]:
    """Plan or atomically change a module's collection through MCP.

    Pass ``collection_id=None`` to clear membership. Apply only the exact
    ``plan_hash`` returned by a dry plan.
    """

    return open_project(path).set_module_collection(
        module_id,
        collection_id,
        source_root=source_root,
        write=write,
        plan_hash=plan_hash,
    )


def module_activity_set(
    path: str,
    module_id: str,
    active: bool,
    source_root: str | None = None,
    write: bool = False,
    plan_hash: str | None = None,
) -> dict[str, object]:
    """Plan or atomically activate or deactivate a module through MCP."""

    return open_project(path).set_module_active(
        module_id,
        active,
        source_root=source_root,
        write=write,
        plan_hash=plan_hash,
    )


def module_diagram(
    path: str,
    family: str,
    profile: str | None = None,
) -> dict[str, object]:
    """Project one authoritative module family into a diagram through MCP.

    Args:
        path: Project root or nested project path.
        family: Editable source-backed diagram family. Use `technology` for a
            technology tree, `focus_tree` for a national focus tree, or `mio`
            for a Military Industrial Organization trait tree.
        profile: Optional build profile used for source discovery.

    Returns:
        JSON-safe SDK module diagram payload.

    Raises:
        ProjectManifestError: If the selected project cannot be loaded.
        OSError: If an authoritative source cannot be read.
        ValueError: If the family, profile, or source contract is invalid.
    """

    return open_project(path).module_diagram(family, profile=profile)


def module_diagram_edit(
    path: str,
    family: str,
    profile: str | None = None,
    position_intents: list[dict[str, object]] | None = None,
    edge_intents: list[dict[str, object]] | None = None,
    node_intents: list[dict[str, object]] | None = None,
    write: bool = False,
    plan_hash: str | None = None,
) -> dict[str, object]:
    """Plan or apply bounded source-backed module diagram edits through MCP.

    Args:
        path: Project root or nested project path.
        family: Editable source-backed diagram family. Use `technology`,
            `focus_tree`, or `mio`.
        profile: Optional build profile used for source discovery.
        position_intents: Reviewed family-specific node-position intents.
        edge_intents: Reviewed family-specific relationship-presence intents.
        node_intents: Reviewed provider-owned graph-item creation intents.
        write: Whether to apply the exact reviewed plan.
        plan_hash: Exact dry-plan hash; required when `write` is true.

    Returns:
        JSON-safe SDK module diagram edit plan or apply payload.

    Raises:
        ProjectManifestError: If the selected project cannot be loaded.
        OSError: If safe source mutation fails.
        ValueError: If the intents, provider, source contract, or plan hash is
            invalid.
    """

    positions, edges = module_diagram_intents(
        position_intents,
        edge_intents,
    )
    nodes = module_diagram_node_intents(node_intents)
    return open_project(path).edit_module_diagram(
        family,
        position_intents=positions,
        edge_intents=edges,
        node_intents=nodes,
        profile=profile,
        write=write,
        plan_hash=plan_hash,
    )


def _authoring_mcp_tool_definitions() -> tuple[tuple[Callable[..., dict[str, object]], str, dict[str, object]], ...]:
    return (
        (
            project_templates,
            "Start here: list project templates, source roots, form fields, and authoring diagnostics.",
            _PROJECT_TEMPLATES_INPUT_SCHEMA,
        ),
        (
            project_authoring_path,
            "Resolve the canonical project source destination for a proposed module or collection.",
            _PROJECT_AUTHORING_PATH_INPUT_SCHEMA,
        ),
        (
            project_authoring_plan,
            "Inspect the compiler source slots expected at a proposed authoring destination.",
            _PROJECT_AUTHORING_PLAN_INPUT_SCHEMA,
        ),
        (
            project_browser,
            "Discover Registry families, modules, collections, source slots, and source paths with bounded project filters.",
            _PROJECT_BROWSER_INPUT_SCHEMA,
        ),
        (
            module_file,
            "Read one stable UTF-8 module source snapshot and its revision before proposing an edit.",
            _MODULE_FILE_INPUT_SCHEMA,
        ),
        (
            collection_file,
            "Read one stable UTF-8 collection source snapshot and its revision before proposing an edit.",
            _COLLECTION_FILE_INPUT_SCHEMA,
        ),
        (
            module_asset,
            "Inspect one Registry-owned module asset and optionally read bounded base64 content before a guarded replacement.",
            _MODULE_ASSET_INPUT_SCHEMA,
        ),
        (
            module_source_form,
            "Read one stable module source snapshot and its Registry-owned guided controls before proposing an edit.",
            _MODULE_SOURCE_FORM_INPUT_SCHEMA,
        ),
        (
            module_source_form_update,
            "Turn selected guided control values into a reviewed revision-guarded full-text source edit without writing.",
            _MODULE_SOURCE_FORM_UPDATE_INPUT_SCHEMA,
        ),
        (
            module_source_form_update_batch,
            "Combine several guided module source changes into one reviewed atomic draft without writing.",
            _MODULE_SOURCE_FORM_UPDATE_BATCH_INPUT_SCHEMA,
        ),
        (
            localization_workspace,
            "Read one Registry-owned cross-language source-unit localization workspace, including current unsaved drafts.",
            _LOCALIZATION_WORKSPACE_INPUT_SCHEMA,
        ),
        (
            localization_plan,
            "Plan one lossless localization operation and return guarded source edits without writing.",
            _LOCALIZATION_PLAN_INPUT_SCHEMA,
        ),
        (
            project_create_modules,
            "Plan a module batch first, then atomically apply it with the exact current plan hash.",
            _PROJECT_CREATE_MODULES_INPUT_SCHEMA,
        ),
        (
            project_preferred_language,
            "Plan a project-wide authoring language first, then atomically apply the exact reviewed manifest update.",
            _PROJECT_PREFERRED_LANGUAGE_INPUT_SCHEMA,
        ),
        (
            project_draft_apply,
            "Apply guarded source edits and an optional canonical module-folder rename inside one SDK transaction.",
            _PROJECT_DRAFT_APPLY_INPUT_SCHEMA,
        ),
        (
            collection_scaffold,
            "Plan a Registry-backed collection first, then atomically apply it with the exact current plan hash.",
            _COLLECTION_SCAFFOLD_INPUT_SCHEMA,
        ),
        (
            collection_remove,
            "Plan a collection removal first, then preserve and ungroup its modules while atomically applying the exact plan.",
            _COLLECTION_REMOVE_INPUT_SCHEMA,
        ),
        (
            module_duplicate,
            "Plan a literal module-folder copy first, then atomically apply the exact reviewed plan without hidden content rewrites.",
            _MODULE_DUPLICATE_INPUT_SCHEMA,
        ),
        (
            module_collection_set,
            "Plan a same-family module collection change first, then atomically apply the exact reviewed plan.",
            _MODULE_COLLECTION_SET_INPUT_SCHEMA,
        ),
        (
            module_activity_set,
            "Plan a module activity change first, then atomically apply the exact reviewed plan.",
            _MODULE_ACTIVITY_SET_INPUT_SCHEMA,
        ),
        (
            module_metadata_clean,
            "Plan redundant module metadata cleanup first, then atomically apply the exact reviewed plan.",
            _MODULE_METADATA_CLEAN_INPUT_SCHEMA,
        ),
        (
            module_diagram,
            "Read the authoritative source-backed module diagram before proposing edits.",
            _MODULE_DIAGRAM_INPUT_SCHEMA,
        ),
        (
            module_diagram_edit,
            "Plan bounded diagram intents first, then apply the exact reviewed source-backed plan.",
            _MODULE_DIAGRAM_EDIT_INPUT_SCHEMA,
        ),
    )


def create_authoring_mcp_toolkit() -> "Toolkit":
    """Create the callable ParaDev authoring toolkit.

    Args:
        None.

    Returns:
        Toolkit: HeavenBase toolkit containing read-only authoring discovery
            tools plus guarded module creation, copy, cleanup, and diagram-edit
            mutations.
    """

    from heavenbase.entity.registry import (
        load_entity_artifact_export,
        load_entity_type,
    )

    from paradev.hb import _paradev_context

    context = _paradev_context()
    resolver = context.modules()
    resolver.setup()
    Tool = load_entity_artifact_export(
        "sys-toolkit",
        "tool",
        "Tool",
        resolver=resolver,
    )
    Toolkit = load_entity_type("sys-toolkit", resolver=resolver)
    tools = [
        Tool(
            function,
            name=function.__name__,
            description=description,
            input_schema=input_schema,
            output_schema={"type": "object"},
            namespace="paradev",
            version="1",
            resolver=resolver,
            config=context.config,
        )
        for function, description, input_schema in _authoring_mcp_tool_definitions()
    ]
    return Toolkit(
        "paradev-authoring",
        tools,
        namespace="paradev",
        version="1",
        description=(
            "Discover ParaDev authoring contracts and source-backed diagrams, " "then plan or apply guarded module changes through SDK-owned transactions."
        ),
        resolver=resolver,
        config=context.config,
    )


def create_authoring_mcp_server() -> Any:
    """Create the ParaDev authoring FastMCP server.

    Args:
        None.

    Returns:
        Any: HeavenBase-owned FastMCP export whose tool schemas and native
            structured results preserve the Toolkit contract.
    """

    return create_authoring_mcp_toolkit().to_fastmcp()


def serve_authoring_mcp_stdio() -> None:
    """Run the ParaDev authoring MCP server over clean stdio.

    FastMCP's banner is disabled and its startup log level is raised so stdout
    remains reserved for MCP protocol frames. Warnings and errors continue to
    use stderr.

    Args:
        None.

    Returns:
        None: This function does not return a value.
    """

    server = create_authoring_mcp_server()
    server.run(
        transport="stdio",
        show_banner=False,
        log_level="WARNING",
    )


def get_mcp_contract() -> dict[str, object]:
    """Return the MCP toolkit contract.

    Args:
        None.

    Returns:
        dict[str, object]: JSON-safe MCP surface contract with ordered tool
            metadata, read/write flags, SDK method targets, runtime tools, and
            frontend operation bindings.
    """

    inspection_contract = get_project_inspection_contract()
    tool_contracts = [
        {
            "name": "project_inspections",
            "sdk_method": "Project.inspect('inspections')",
            "read_only": True,
        },
        {
            "name": "project_inspect",
            "sdk_method": "Project.inspect",
            "read_only": True,
            "inspection_contract": inspection_contract,
        },
        {
            "name": "project_templates",
            "sdk_method": "Project.templates",
            "read_only": True,
            "filters": TEMPLATE_FILTERS,
        },
        {
            "name": "project_authoring_path",
            "sdk_method": "Project.authoring_path",
            "read_only": True,
        },
        {
            "name": "project_authoring_plan",
            "sdk_method": "Project.authoring_plan",
            "read_only": True,
        },
        {
            "name": "project_scaffold",
            "sdk_method": "Project.scaffold_module",
            "read_only": False,
        },
        {
            "name": "project_create_modules",
            "sdk_method": "Project.create_modules",
            "read_only": False,
        },
        {
            "name": "project_draft_apply",
            "sdk_method": "Project.apply_source_draft",
            "read_only": False,
        },
        {
            "name": "collection_scaffold",
            "sdk_method": "Project.scaffold_collection",
            "read_only": False,
        },
        {"name": "project_create", "sdk_method": "Project.create", "read_only": False},
        {"name": "project_open", "sdk_method": "Project.load", "read_only": True},
        {"name": "project_view", "sdk_method": "Project.to_view", "read_only": True},
        {"name": "project_browser", "sdk_method": "Project.browser", "read_only": True},
        {"name": "project_find", "sdk_method": "Project.find", "read_only": True},
        {"name": "project_rename", "sdk_method": "Project.rename", "read_only": False},
        {
            "name": "project_preferred_language",
            "sdk_method": "Project.set_preferred_language",
            "read_only": False,
        },
        {
            "name": "module_rename",
            "sdk_method": "Project.rename_module",
            "read_only": False,
        },
        {
            "name": "module_duplicate",
            "sdk_method": "Project.duplicate_module",
            "read_only": False,
        },
        {
            "name": "module_collection_set",
            "sdk_method": "Project.set_module_collection",
            "read_only": False,
        },
        {
            "name": "module_activity_set",
            "sdk_method": "Project.set_module_active",
            "read_only": False,
        },
        {
            "name": "module_metadata_clean",
            "sdk_method": "Project.clean_module_metadata",
            "read_only": False,
        },
        {
            "name": "module_diagram",
            "sdk_method": "Project.module_diagram",
            "read_only": True,
        },
        {
            "name": "module_diagram_edit",
            "sdk_method": "Project.edit_module_diagram",
            "read_only": False,
        },
        {
            "name": "module_remove",
            "sdk_method": "Project.remove_module",
            "read_only": False,
        },
        {
            "name": "module_file",
            "sdk_method": "Project.read_module_file",
            "read_only": True,
        },
        {
            "name": "module_asset",
            "sdk_method": "Project.read_module_asset",
            "read_only": True,
        },
        {
            "name": "module_source_form",
            "sdk_method": "Project.read_module_file + Project.source_form",
            "read_only": True,
        },
        {
            "name": "module_source_form_update",
            "sdk_method": "Project.read_module_file + Project.plan_source_form_update",
            "read_only": True,
        },
        {
            "name": "module_source_form_update_batch",
            "sdk_method": "Project.read_module_file + Project.plan_source_form_updates",
            "read_only": True,
        },
        {
            "name": "localization_workspace",
            "sdk_method": "Project.localization_workspace",
            "read_only": True,
        },
        {
            "name": "localization_plan",
            "sdk_method": "Project.plan_localization_update",
            "read_only": True,
        },
        {
            "name": "module_edit",
            "sdk_method": "Project.write_module_file",
            "read_only": False,
        },
        {
            "name": "collection_file",
            "sdk_method": "Project.read_collection_file",
            "read_only": True,
        },
        {
            "name": "collection_edit",
            "sdk_method": "Project.write_collection_file",
            "read_only": False,
        },
        {
            "name": "collection_create",
            "sdk_method": "Project.create_collection",
            "read_only": False,
        },
        {
            "name": "collection_rename",
            "sdk_method": "Project.rename_collection",
            "read_only": False,
        },
        {
            "name": "collection_remove",
            "sdk_method": "Project.remove_collection",
            "read_only": False,
        },
        {
            "name": "frontend_api",
            "sdk_method": "get_frontend_api_selection",
            "read_only": True,
            "selectors": [*FRONTEND_API_SELECTORS, "index_name", "key"],
        },
        {
            "name": "api_catalog",
            "sdk_method": "get_api_catalog_selection",
            "read_only": True,
            "selectors": ["reference_id", "index_name", "key"],
        },
        {
            "name": "surface_contracts",
            "sdk_method": "get_surface_contract_selection",
            "read_only": True,
            "selectors": ["identifier", "status"],
        },
        {"name": "pdx_parse", "sdk_method": "parse_pdx_file", "read_only": True},
        {"name": "pdx_format", "sdk_method": "format_pdx_file", "read_only": False},
        {
            "name": "pdx_api",
            "sdk_method": "get_pdx_api_selection",
            "read_only": True,
            "selectors": ["symbol", "index_name", "key"],
        },
        {
            "name": "lsp_api",
            "sdk_method": "get_lsp_api_selection",
            "read_only": True,
            "selectors": ["symbol", "index_name", "key"],
        },
        {
            "name": "catalog_api",
            "sdk_method": "get_catalog_api_selection",
            "read_only": True,
            "selectors": ["symbol", "index_name", "key"],
        },
        {
            "name": "mcp_api",
            "sdk_method": "get_mcp_api_selection",
            "read_only": True,
            "selectors": ["symbol", "index_name", "key"],
        },
        {
            "name": "cli_api",
            "sdk_method": "get_cli_api_selection",
            "read_only": True,
            "selectors": ["symbol", "index_name", "key"],
        },
        {"name": "inspect_project", "sdk_method": "Project.to_view", "read_only": True},
        {
            "name": "list_surfaces",
            "sdk_method": "get_architecture_spec",
            "read_only": True,
        },
        {
            "name": "describe_architecture",
            "sdk_method": "get_architecture_spec",
            "read_only": True,
        },
        {
            "name": "architecture_api",
            "sdk_method": "get_architecture_api_selection",
            "read_only": True,
            "selectors": ["symbol", "index_name", "key"],
        },
    ]
    return {
        "identifier": "mcp",
        "runtime": "heavenbase-mcp",
        "status": "scaffold",
        "runtime_status": "implemented",
        "transport": "stdio",
        "server_command": "paradev mcp serve",
        "runtime_scope": "authoring",
        "tools": [tool["name"] for tool in tool_contracts],
        "tool_contracts": tool_contracts,
        "runtime_tools": [function.__name__ for function, _description, _input_schema in _authoring_mcp_tool_definitions()],
        "toolkit_factory": "create_authoring_mcp_toolkit",
        "stdio_server": "serve_authoring_mcp_stdio",
        "frontend_operation_ids": get_frontend_api_binding_index("mcp"),
        "sdk_owned": True,
    }


def get_mcp_api_table() -> McpApiTable:
    """Return the API-standard table for MCP tools.

    Returns:
        JSON-safe table derived from `get_mcp_contract()`, with copied rows
        and indexes for mode, feature, and frontend operation audits.
    """

    return cast(
        McpApiTable,
        api_indexed_table(
            MCP_API_TABLE_SCHEMA,
            _mcp_api_rows(get_mcp_contract()),
            (
                ("mode_index", "mode"),
                ("feature_index", "feature"),
                ("frontend_operation_index", "frontend_operation_ids"),
            ),
            index_list_fields=("frontend_operation_ids",),
            row_list_fields=("frontend_operation_ids",),
        ),
    )


def get_mcp_api_selection(
    symbol: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
) -> McpApiTable | McpApiRow | list[str]:
    """Return the MCP tool table, one tool row, or one index projection.

    Args:
        symbol: Optional MCP tool symbol such as `frontend_api`.
        index_name: Optional index payload name such as `mode_index`,
            `feature_index`, or `frontend_operation_index`.
        key: Optional concrete index key used with `index_name`.

    Returns:
        Full MCP tool table, one MCP tool row, or one ordered tool-symbol list.

    Raises:
        ValueError: If selector arguments are ambiguous, incomplete, or use an
            unsupported index.
        KeyError: If `symbol` does not match an MCP tool row.
    """

    return cast(
        McpApiTable | McpApiRow | list[str],
        api_table_selection(
            get_mcp_api_table(),
            row_key_field="symbol",
            row_key=symbol,
            index_name=index_name,
            key=key,
            row_list_fields=_MCP_API_ROW_LIST_FIELDS,
            index_names=_MCP_API_INDEX_NAMES,
        ),
    )


def render_mcp_api_reference_markdown() -> str:
    """Render the MCP tool table as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/mcp-api-reference.md`. The content is generated
        from `get_mcp_api_table()` so the MCP contract, frontend binding
        reverse index, and manual page stay aligned.
    """

    table = get_mcp_api_table()
    return api_reference_markdown(
        title="MCP API Reference",
        source="paradev.surfaces.mcp.get_mcp_api_table()",
        regenerate_when="Regenerate this file whenever the MCP tool contract changes:",
        command="rtk uv run paradev mcp-api --markdown > docs/user-manual/mcp-api-reference.md",
        sections=api_indexed_reference_sections(
            summary_lines=[
                f"- API rows / API 行数: {table['row_count']}",
                f"- Read tools / 读取工具数: {len(table['mode_index'].get('read', []))}",
                f"- Write tools / 写入工具数: {len(table['mode_index'].get('write', []))}",
                f"- Features / Feature 数: {len(table['feature_index'])}",
                f"- Frontend-bound operations / 前端绑定操作数: {len(table['frontend_operation_index'])}",
                "- Runtime server / Runtime server: `paradev mcp serve` (`stdio`)",
                "- Runtime status / Runtime status: `implemented` (`authoring` scope)",
                "- Selector helper / Selector helper: Use "
                "`get_mcp_api_selection(symbol=..., index_name=..., key=...)` "
                "returns the table, one MCP tool row, or one tool-symbol index projection.",
            ],
            table=table,
            index_specs=(
                ("Mode Index / 模式索引", "mode_index", "Mode", "Tools", "Symbols"),
                (
                    "Feature Index / Feature 索引",
                    "feature_index",
                    "Feature",
                    "Tools",
                    "Symbols",
                ),
                (
                    "Frontend Operation Index / 前端操作索引",
                    "frontend_operation_index",
                    "Operation",
                    "Tools",
                    "Symbols",
                ),
            ),
            fields=_MCP_API_STANDARD_FIELDS,
            list_fields=("frontend_operation_ids",),
        ),
    )


def _mcp_api_rows(contract: Mapping[str, object]) -> list[McpApiRow]:
    tool_contracts = contract.get("tool_contracts", [])
    if not isinstance(tool_contracts, list):
        return []
    operation_index = contract.get("frontend_operation_ids", {})
    if not isinstance(operation_index, Mapping):
        operation_index = {}
    frontend_rows = _frontend_api_operation_rows()
    rows: list[McpApiRow] = []
    for tool in tool_contracts:
        if not isinstance(tool, Mapping):
            continue
        name = str(tool.get("name", ""))
        if not name:
            continue
        operation_ids = _mcp_api_operation_ids(operation_index, name)
        rows.append(
            {
                "symbol": name,
                "kind": "MCP tool",
                "layer": "mcp",
                "feature": _mcp_api_feature(name),
                "mode": "read" if tool.get("read_only") else "write",
                "sdk_method": str(tool.get("sdk_method", "")),
                "inputs": _mcp_api_inputs(name, operation_ids, frontend_rows),
                "returns": _mcp_api_returns(name, operation_ids, frontend_rows),
                "raises": _MCP_TOOL_RAISES.get(name, ""),
                "registry_seam": f"MCP tool registry: {name}",
                "surface": "mcp",
                "frontend_operation_ids": operation_ids,
                "doc_page": _MCP_API_REFERENCE_PAGE,
                "test_anchor": _MCP_API_TEST_ANCHOR,
            }
        )
    return rows


def _frontend_api_operation_rows() -> dict[str, Mapping[str, object]]:
    contract = get_frontend_api_contract()
    operations = contract.get("operations", [])
    if not isinstance(operations, list):
        return {}
    rows: dict[str, Mapping[str, object]] = {}
    for row in operations:
        if not isinstance(row, Mapping):
            continue
        operation_id = row.get("id")
        if isinstance(operation_id, str):
            rows[operation_id] = row
    return rows


def _mcp_api_operation_ids(operation_index: Mapping[str, object], name: str) -> list[str]:
    operation_ids = operation_index.get(name, [])
    if not isinstance(operation_ids, list):
        return []
    return [str(operation_id) for operation_id in operation_ids]


def _mcp_api_feature(name: str) -> str:
    return _MCP_TOOL_FEATURES.get(name, "mcp")


def _mcp_api_inputs(
    name: str,
    operation_ids: list[str],
    frontend_rows: Mapping[str, Mapping[str, object]],
) -> str:
    if name in _MCP_TOOL_INPUTS:
        return _MCP_TOOL_INPUTS[name]
    inputs: list[str] = []
    seen: set[str] = set()
    for operation_id in operation_ids:
        operation = frontend_rows.get(operation_id)
        if not isinstance(operation, Mapping):
            continue
        rows = operation.get("inputs", [])
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, Mapping):
                continue
            input_name = row.get("name")
            if not isinstance(input_name, str) or input_name in seen:
                continue
            seen.add(input_name)
            inputs.append(input_name)
    return ", ".join(inputs) if inputs else "none"


def _mcp_api_returns(
    name: str,
    operation_ids: list[str],
    frontend_rows: Mapping[str, Mapping[str, object]],
) -> str:
    if name in _MCP_TOOL_RETURNS:
        return _MCP_TOOL_RETURNS[name]
    payloads: list[str] = []
    seen: set[str] = set()
    for operation_id in operation_ids:
        operation = frontend_rows.get(operation_id)
        if not isinstance(operation, Mapping):
            continue
        payload = operation.get("payload") or "untyped payload"
        payload_name = str(payload)
        if payload_name in seen:
            continue
        seen.add(payload_name)
        payloads.append(payload_name)
    return "; ".join(payloads) if payloads else "MCP tool payload"
